"""The edge finish of the shell: which convex edges are still sharp, by part and by place, and whether the edge rule
holds.

The edge rule (the owner, 2026-11-12; decision record 0007): no outside edge of the exterior stays fully sharp,
because paint does not hold on a sharp edge. A convex edge that turns more than edge_break_turn has a round of the
design or the edge break. The rule is for the parts that are printed, filled and painted. Each part of the build is
in one class, by name:
  PRINTED       a printed and painted part of the exterior: the rule holds
  CUT_PLATES    a cut plate: not a printed part
  PROVISIONAL   a stand-in for a part that is not designed yet: "provisional, not finished"
  NOT_DECIDED   the record does not say how the part is made: the rule waits for the owner's choice
  INSIDE        a printed part inside the shell that is not painted: the rule does not apply
  BOUGHT        a bought part in the build folder of a work package: not a printed part
A part of the build that is in no class is a failure: no part passes because nobody named it.

This tool reads the parts of a build and lists, for each part, the convex edges that turn more than
edge_break_turn and have no round, in groups by place and by whether they show:
  outside                 the edge shows on the finished cabinet
  in a joint: against X   one of its two faces lies against the part X, or in the seam between the body and the
                          hood. A person does not see the edge, and paint does not go there
A sharp edge of a printed part passes only in a joint of JOINTS, which names each joint. It also counts the faces
that are rounds: those of the edge break (with the balls at the corners where three broken edges meet), and those
of the design (any other radius under ROUND_MAX).

Run headless. It writes edge-finish.json and edge-finish.md into the build's directory, and exits 1 when the rule
does not hold:

    CANDYBAR_OUT=cad/out/shell-rev7 cad/candybar/freecad-run.sh tools.edge_finish
"""
from __future__ import annotations

import json
import math
import os
from collections import defaultdict

import FreeCAD
import Part

from candybar.shell import coupons as cp
from candybar.shell import cradle as cr
from candybar.shell import hood_band as hb
from candybar.shell import joints as jt
from candybar.shell import mounts as mt
from candybar.shell import panel_frame as pf
from candybar.shell import profiles as pr
from candybar.shell import socket_plate as spm
from candybar.shell import solids as so
from candybar.shell import split
from candybar.shell.dims import Blueprint
from tools import face_check

V = FreeCAD.Vector
ROUND_MAX = 12.0
NEAR = 0.05
SEAM = 0.2
SEAM_NAME = "the seam between the body and the hood"

# the printed parts of the shell, and of the work packages by the module that makes them
PRINTED = ("deck", "body", "hood") + pf.PARTS + cr.HALVES + ("socket_plate",)
# printed parts inside the shell that are not painted: the edge rule is for the painted outside (decision record 0007)
INSIDE = {name: "A printed part of the monitor cradle, inside the shell behind the bezel plate. It is not painted." for name in cr.INSIDE}
# a sharp edge of these parts is hidden when its middle lies under one of the named parts (socket_plate.covered)
UNDER = {"socket_plate": spm.BOUGHT,
         # the mouth of a screw hole of a grille of the hood band, under the head of its screw
         **{f"grille_{s}": (f"grille_screw_inner_{s}", f"grille_screw_outer_{s}") for s in ("right", "left")}}
# bought parts in a build folder of a work package: not printed
BOUGHT = {name: "A bought part of the front socket plate (docs/design/front-socket-plate.md)." for name in spm.BOUGHT}
CUT_PLATES = {"control_panel": "The top of a control panel is a cut plate (roadmap, settled by the owner)."}
PROVISIONAL = {
    "marquee_lip": "A stand-in for the lower frame of the marquee window. The marquee is not designed yet.",
    "speaker_right": "A stand-in for the speaker grille on the hood band. The grille is not designed yet.",
    "speaker_left": "A stand-in for the speaker grille on the hood band. The grille is not designed yet.",
    "logo_form": "A stand-in for the logo on the hood band. The logo is not designed yet.",
    "bezel": "A stand-in for the printed bezel plate. The owner chose a printed plate (2026-11-14). candybar.shell.cradle "
             "makes it, in two halves with the edge break (docs/design/monitor-cradle-and-bezel.md). The default build keeps "
             "the plain plate of the form.",
}
NOT_DECIDED: dict[str, str] = {}
# the print pieces of the split, as their build folder names them (cad/out/pieces): the walls are printed and
# painted; the floor tiles are inside (their top is inside, their underside lies on the table)
PIECE_MODULE = {p.full.replace(" ", "_"): p.module for p in split.expanded(split.layout(Blueprint()))[1]}
PIECES = tuple(PIECE_MODULE)
FLOOR_TILES = tuple(n for n in PIECES if n.startswith("floor"))
INSIDE.update({n: "A floor tile: its top is inside the shell and its underside lies on the table. It is not painted." for n in FLOOR_TILES})
# what a face of a print piece or of a coupon cut from the real skin lies against, besides another part
INSIDE_SHELL = "the inside of the shell or a seam"
SEAM_PIECE = "the next piece, at a seam"
SEAM_V = "the V of a filled seam"
# a face of a piece nearer than this to the next piece lies in the V on the outer edge of their seam, which is filled:
# the width of the V over the two pieces and the bond line that the split removes
V_REACH = jt.Joint().vgroove_w + split.KERF + 0.1
PIECE_OF = "piece "   # the name of another print piece among the covers of a piece
REST_OF_SHELL = "the rest of the shell (inside it, or where the coupon is cut off)"
CONTROL_EDGE = "the control edge of the paint test, sharp by design"
UNTESTED = "a face of the edge bar that its test does not look at: its two ends and its bed face"
HOOD_BAND = "a joint of the hood band, or behind one of its parts (hood_band.in_joint and Scene.shows)"
# the painted parts of a build folder of the hood band (hood_band.PARTS)
# the parts of the hood band that show (hood_band.SHOWN): painted, black as printed, the translucent front, the badge
BAND_SHOWN = ("hood", "marquee_lip_right", "marquee_lip_left", "speaker_pod_right", "speaker_pod_left", "logo_field", "logo_badge",
              "grille_right", "grille_left", "marquee_front_right", "marquee_front_left")
HELD = ("printed", "printed, not painted")   # the classes on which the edge rule holds
SHELL_FORM = ("deck", "body", "hood", "marquee_lip")
# the parts of the default build that lie on the outside of the shell's form: on a print piece they cover the faces of
# the pocket of the panel, the recess of the bezel and the pockets of the stand-ins of the hood band
SHELL_COVERS = ("control_panel", "bezel", "screen", "marquee_lip", "speaker_right", "speaker_left", "logo_form")
# the print pieces of the walls, by their rules; the piece "logo form" has the name of the stand-in of the default build
WALLS = tuple(p for p in PIECES if p not in FLOOR_TILES and p not in SHELL_FORM + SHELL_COVERS)
_FORM: dict[str, Part.Shape] = {}


def shell_parts() -> dict[str, Part.Shape]:
    """The parts of the default build (CANDYBAR_SHELL, default cad/out/shell-rev7) that the tools read for the print
    pieces and the coupons: the outer form and its covers."""
    if not _FORM:
        folder = os.environ.get("CANDYBAR_SHELL") or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "shell-rev7")
        manifest = json.load(open(os.path.join(folder, "manifest.json")))
        for k in SHELL_FORM + SHELL_COVERS:
            if k not in _FORM:
                _FORM[k] = Part.Shape()
                _FORM[k].read(os.path.join(folder, manifest[k]["brep"]))
    return _FORM


_PLATE: list[Part.Shape] = []


def real_bezel() -> Part.Shape:
    """The printed bezel plate of the cradle (cradle.bezel_plate), which the owner chose: the cover of the recess. The
    plate of the default build is a stand-in, and a stand-in must not hide an edge (2026-11-15: it hid the rims of
    the recess, which the printed plate leaves open by panel_gap)."""
    if not _PLATE:
        _PLATE.append(cr.bezel_plate(Blueprint(), cr.Cradle()))
    return _PLATE[0]


def outer_form() -> dict[str, Part.Shape]:
    """The outer solids of the default build: the outside of the shell."""
    return {k: shell_parts()[k] for k in SHELL_FORM}


def stand_in(k: str) -> str:
    return f"the stand-in {k}, which is a part of the skin here"


# the joints in which a sharp edge of a printed part can lie: (part, what the face of the edge lies against)
JOINTS = {
    ("deck", "body"): "The deck and the body meet on the plane at the foot of the sweep. They are one bonded shell.",
    ("deck", "control_panel"): "The pocket of the control panel, under the panel.",
    ("body", "deck"): "The deck and the body meet on the plane at the foot of the sweep. They are one bonded shell.",
    ("body", "screen"): "The window of the form behind the bezel plate, where the monitor lies. The screen of the build is a "
                        "plate of 1 mm for the renders.",
    # the control panel (docs/design/control-panel.md): its covers (panel_frame.covers) and the bonded seam of its tiles
    **{(part, cover): pf.JOINTS[cover] for part in pf.PARTS for cover in pf.joints_of(part)},
    # the bezel plate of the cradle (docs/design/monitor-cradle-and-bezel.md), in its two printed halves
    **{(part, cover): cr.EDGE_JOINTS[cover] for part in cr.HALVES for cover in ("screen", "the other half")},
    ("bezel_half_right", cr.ROD_HOLE): cr.EDGE_JOINTS[cr.ROD_HOLE],
    # the print pieces (docs/design/print-pieces.md): the bonded seams, and the inside, which is not painted
    **{(p, INSIDE_SHELL): "A face of the piece that is not on the outer form of the shell: the cavity, a flange, a key, a rib "
                          "(not painted), or the face of a bonded seam (filled)." for p in WALLS},
    **{(p, c): f"A part of the default build lies on this face of the piece: {why}" for p in WALLS
       for c, why in (("control_panel", "the pocket of the control panel, under the panel."),
                      ("bezel", "the recess and the reveal of the bezel plate, under and beside the plate."),
                      ("screen", "the window of the form behind the bezel plate, where the monitor lies."),
                      *((k, "a pocket of a stand-in of the hood band, which hood_band.py replaces.")
                        for k in ("marquee_lip", "speaker_right", "speaker_left", "logo_form")),
                      (SEAM_NAME, "the top of the body and the foot of the hood lie on each other in the seam groove."),
                      (SEAM_PIECE, "the face of a bonded seam between two pieces, thin where it meets the outside; the seam is filled."),
                      (SEAM_V, "a face in the V on the outer edge of a seam (joints.vgroove_profile): the owner fills the V."),
                      *((stand_in(k), f"the face is a face of the stand-in {k}: provisional, not finished ({PROVISIONAL[k]})")
                        for k in PROVISIONAL if k in SHELL_COVERS))},
    # the hood band (docs/design/hood-band.md): its parts lie on the hood and on each other, and an edge in a
    # joint or behind a part of the band does not show, by the band's own rule
    **{(p, HOOD_BAND): "The hood band's rule: the edge lies in a joint with another part, or every ray from it toward the player meets a part."
       for p in BAND_SHOWN if p not in ("marquee_lip_right", "marquee_lip_left", "logo_field")},   # their joints are named
    ("hood", "logo_field"): "The logo field is bonded on the band of the hood.",
    ("logo_field", "hood"): "The logo field is bonded on the band of the hood.",
    **{(f"marquee_lip_{s}", "hood"): "The lip of the marquee is bonded on the hood." for s in ("right", "left")},
    ("marquee_lip_right", "marquee_lip_left"): "The two halves of the lip of the marquee are bonded on the centre line.",
    ("marquee_lip_left", "marquee_lip_right"): "The two halves of the lip of the marquee are bonded on the centre line.",
    # the coupons cut from the real skin, and the control edge of the paint test (docs/design/coupons.md)
    **{(c, REST_OF_SHELL): "The coupon is a part of the shell: its inside and its cut faces are not faces of the cabinet."
       for c in ("facet45", "cut-in", "hand-hold")},
    **{(c, CONTROL_EDGE): "The sharp edge of 90 degrees is the control of the paint test (coupons.EDGE_NAMES)." for c in cp.CONTROL},
    **{(c, UNTESTED): "The test looks at the six edges of the section (coupons.EDGE_NAMES), not at the ends of the bar." for c in cp.CONTROL},
    **{(f"grille_{s}", f"grille_screw_{w}_{s}"): "The mouth of a screw hole of the grille, under the head of its screw."
       for s in ("right", "left") for w in ("inner", "outer")},
    # the front socket plate (docs/design/front-socket-plate.md) in its seat in the deck, and the bought parts on it
    ("socket_plate", "the inside of the shell, behind the web"): "The back of the socket plate, inside the shell: not painted.",
    ("deck", "the inside of the shell, behind the plate"): "The ledge and the window of the seat behind the socket plate, inside the shell.",
    **{("socket_plate", part): "The rim of a round hole of the plate, under the rim of the button, the nut of the knob or the head of a screw."
       for part in ("screws", "knob", "power_button")},
}


def covers_of(name: str, parts: dict[str, Part.Shape], d: Blueprint, entry: dict | None = None
              ) -> tuple[dict[str, Part.Shape], tuple[str, ...], dict[str, str]]:
    """What the faces of a part lie against, the covers that can hide an edge of the top face of a control panel (all
    when the tuple is empty), and the name of the joint for each cover that is not its own name. A part of the shell
    lies against the other parts of the build. A part of the control panel lies against the covers of panel_frame
    (its seat, its holes, the room below it) and the other tile of its panel; on its top face only a hole or that tile
    hides an edge (panel_frame.ON_TOP). A print piece lies against the next piece at a seam, and its inside faces lie
    in the outer form of the shell. A coupon cut from the real skin lies in the rest of the shell, moved onto its
    plate (the manifest's to_cabinet)."""
    if name in pf.PARTS:
        return {**{"the other tile": parts[k] for k in pf.twins(name, parts)}, **pf.covers(d, pf.Interface())}, pf.ON_TOP, {}
    if name in cr.HALVES:
        return {**{"the other half": parts[k] for k in cr.HALVES if k != name and k in parts}, **cr.edge_covers(d)}, (), {}
    if name in WALLS:
        # survey uses on_skin first: a face of a piece shows only on the outer form, and there only where no part of
        # the default build lies on it
        return ({**{k: (real_bezel() if k == "bezel" else shell_parts()[k]) for k in SHELL_COVERS},
                 **{f"{PIECE_OF}{k}": s for k, s in parts.items() if k in PIECES and k != name}}, (), {})
    if entry and "to_cabinet" in entry:
        back = V(*entry["to_cabinet"])
        others = {f"form {k}": s.translated(-back) for k, s in outer_form().items()}
        x0, x1, y0, y1, z0, z1 = cp.CUT_BOXES[entry["coupon"]]
        cut = Part.makeBox(2000.0, 2000.0, 2000.0, V(-1000.0, -1000.0, -1000.0)).cut(Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0)))
        others["beyond the cut"] = cut.translated(-back)
        return others, (), {k: REST_OF_SHELL for k in others}
    if entry and entry.get("coupon") in cp.CONTROL:
        return {"untested": cp.untested(entry["coupon"]).translated(V(*entry["offset"]))}, (), {"untested": UNTESTED}
    # the plate of the default build is a stand-in: the printed plate of the cradle covers in its place
    others = {k: (real_bezel() if k == "bezel" and name != "bezel" else s) for k, s in parts.items() if k != name}
    if "socket_plate" in parts and name in ("socket_plate", "deck"):
        # the inside of the shell behind the socket plate (socket_plate.inside_covers)
        others.update(spm.inside_covers(spm.SocketPlate(), d)[name])
    return others, (), {}


def finish_class(part: str, entry: dict | None = None) -> str:
    """The class of a part of the build, or "" when it is in none. `entry` is the part's entry of the manifest of its
    folder: a coupon of the layout names its group there."""
    if part in PRINTED:
        return "printed"
    if part in CUT_PLATES:
        return "cut plate"
    if part in PROVISIONAL:
        return "provisional, not finished"
    if part in NOT_DECIDED:
        return "not decided"
    if part in INSIDE:
        return "inside, not painted"
    if part in BOUGHT:
        return "bought"
    if part in PIECES:
        return "provisional, not finished" if PIECE_MODULE[part] in PROVISIONAL else "printed"
    if part.startswith(mt.PLACE_PREFIX):
        return "a place"
    if part.startswith(mt.INSIDE_PREFIXES):
        return "inside, not painted"
    k = hb.kind(part)
    if k in hb.PARTS and (k != part or k in ("logo_field", "logo_badge", "led_strip", "logo_backer")):
        return {"painted": "printed", "inside": "inside, not painted", "hardware": "bought"}.get(hb.PARTS[k][1], "printed, not painted")
    if entry and "group" in entry:
        return "printed" if entry["group"] in cp.PAINTED else "a test print"
    return ""


def manifest_of(folder: str) -> dict:
    return json.load(open(os.path.join(folder, "manifest.json")))


def load(folder: str) -> dict[str, Part.Shape]:
    manifest = manifest_of(folder)
    out = {}
    for name, entry in manifest.items():
        s = Part.Shape()
        s.read(os.path.join(folder, entry["brep"]))
        out[name] = s
    return out


SKIN = 0.1   # a point nearer than this to the outer form of the default build is on the outside of the shell
_SKIN: list[tuple[FreeCAD.BoundBox, Part.Face]] = []


def on_skin(p: FreeCAD.Vector, tol: float = SKIN) -> bool:
    """Whether a point of the cabinet lies on the outer form of the default build: only the faces whose box holds the
    point are measured (a print piece has 3000 faces, and isInside on the next piece takes a second)."""
    if not _SKIN:
        for s in outer_form().values():
            for f in s.Faces:
                bb = FreeCAD.BoundBox(f.BoundBox)
                bb.enlarge(tol)
                _SKIN.append((bb, f))
    v = Part.Vertex(p)
    return any(bb.isInside(p) and f.distToShape(v)[0] < tol for bb, f in _SKIN)


OFF = 0.5   # a face of the skin is on the outside when a point this far off its middle, along its normal, is outside the form


def face_on_skin(face: Part.Face, back: FreeCAD.Vector | None = None) -> bool:
    """Whether a face of a print piece or of a coupon (moved by `back` into the cabinet) is a face of the outside of
    the shell: its middle lies on the outer form, and the side it faces is outside the form. The second test leaves
    out a face of the cavity that ends at the outer form (a step of 0.01 at the top of a wall)."""
    u0, u1, v0, v1 = face.ParameterRange
    p = face.valueAt((u0 + u1) / 2, (v0 + v1) / 2) + (back or V(0, 0, 0))
    if not on_skin(p):
        return False
    q = p + face.normalAt((u0 + u1) / 2, (v0 + v1) / 2) * OFF
    return not any(s.BoundBox.isInside(q) and s.isInside(q, 1e-6, True) for s in outer_form().values())


def face_middle(face: Part.Face) -> FreeCAD.Vector:
    u0, u1, v0, v1 = face.ParameterRange
    return face.valueAt((u0 + u1) / 2, (v0 + v1) / 2)


FIT = 0.3   # a print piece is cut from the skin, whose pockets are larger than the parts in them by a fit of this or less


def against(face: Part.Face, others: dict[str, Part.Shape], d: Blueprint, near: float = NEAR) -> str:
    """What a face lies against: the name of another part (a point just outside the middle of the face is inside
    that part), the seam between the body top and the foot of the hood, or "" when the face shows."""
    u0, u1, v0, v1 = face.ParameterRange
    p = face.valueAt((u0 + u1) / 2, (v0 + v1) / 2)
    n = face.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
    if abs(abs(n.z) - 1) < 1e-6 and d.body_top - SEAM < p.z < d.body_top + d.seam_gap + SEAM:
        return SEAM_NAME
    q = p + n * near
    return next((name for name, o in others.items() if o.BoundBox.isInside(q) and o.isInside(q, 1e-3, True)), "")


def zone(part: str, m: FreeCAD.Vector, d: Blueprint) -> str:
    """A plain name for the place of an edge on its part."""
    g = d.seam_groove
    if part == "body":
        if m.z < 1e-3:
            return "floor edge"
        if m.z > d.body_top - g - 0.5:
            return "seam groove (bevel and body top)"
        if so.behind_band(d, m):
            return "rear (band, shelf, head, lower body)"
        if abs(m.x) < d.bezel_w / 2 + d.panel_gap + 0.5:
            return "bezel opening (reveal and recess)"
        return "rail and side band"
    if part == "hood":
        if m.z < d.body_top + d.seam_gap + g + 0.5:
            return "seam groove (bevel and foot)"
        if m.y > d.depth - 60:
            return "rear"
        return "front opening (legs, top bar, sill, recess)"
    if part == "deck":
        if m.z < 1e-3:
            return "floor edge"
        if m.z > d.panel_top - d.panel_t - 0.5 and abs(m.x) < d.panel_w / 2 + d.panel_gap + 0.5 and m.y > d.deck_nose - 1:
            return "panel pocket"
        return "front, sides and joint with the body"
    return "all"


def edge_faces(shape: Part.Shape) -> dict[int, list[Part.Face]]:
    """The faces of each edge of a part, in one pass (ancestorsOfType for each edge of a print piece of 10 000 edges
    takes hours)."""
    out: dict[int, list[Part.Face]] = defaultdict(list)
    for f in shape.Faces:
        for h in {e.hashCode() for e in f.Edges}:
            out[h].append(f)
    return out


def piece_face(f: Part.Face, covers: dict[str, Part.Shape], d: Blueprint) -> str:
    """What a face of a print piece lies against: the inside of the shell (not on the outside of the form), a part of
    the default build on it (within the fit of the skin's pockets), a face of a stand-in that the skin carries (the bar
    of the marquee lip), the next piece at a seam or the V of the seam, or "" when it shows."""
    if not face_on_skin(f):
        return INSIDE_SHELL
    parts = {k: s for k, s in covers.items() if not k.startswith(PIECE_OF)}
    k = against(f, parts, d) or against(f, parts, d, FIT)
    if k:
        return k
    v = Part.Vertex(face_middle(f))
    k = next((stand_in(c) for c in PROVISIONAL if c in parts and parts[c].distToShape(v)[0] < 0.05), "")
    if k:
        return k
    # a face of a seam that the cut leaves thin at the outside: the next piece lies on it
    pieces = {k: s for k, s in covers.items() if k.startswith(PIECE_OF)}
    if against(f, pieces, d) or against(f, pieces, d, FIT):
        return SEAM_PIECE
    m = face_middle(f)
    for s in pieces.values():
        bb = FreeCAD.BoundBox(s.BoundBox)
        bb.enlarge(V_REACH)
        if bb.isInside(m) and s.distToShape(Part.Vertex(m))[0] < V_REACH:
            return SEAM_V
    return ""


NOT_FINISHED = "not finished: "   # a named place that the edge finish leaves as it is, with its reason (docs/adr/0007)


def not_finished(m: FreeCAD.Vector, d: Blueprint) -> str:
    """The reason when a sharp edge of the body (or of a print piece of the body) at m is a place that the edge finish
    names and leaves as it is (the edge finish is a guideline, docs/adr/0007), or ""."""
    fr = pr.front(d)
    xb = d.bezel_w / 2 + d.panel_gap
    y0, z0 = fr.on_rail(d, d.bezel_s0, 0.0)
    y1, z1 = fr.on_rail(d, d.bezel_s1, 0.0)
    if abs(abs(m.x) - d.bezel_w / 2) < 0.05 and z0 < m.z < z1:
        return (NOT_FINISHED + "the corner of the plate's seat at the side of the bezel recess, 1 from the break of the rail "
                "land: R 1 does not build there, and a break of 0.5 by hand left the body failing its strict check")
    if abs(m.x) < xb + 1.5 and math.dist((m.y, m.z), (y1, z1)) < 0.6:
        return (NOT_FINISHED + "the top rim of the bezel recess: R 1 meets the round of the rail land in faces that fail the strict "
                "check, and a break by hand leaves narrow faces and short sharp ends there")
    return ""


def edge_turn(e: Part.Edge, fs: list[Part.Face], m: FreeCAD.Vector) -> tuple[bool, float]:
    """solids.edge_turn with the two faces of the edge given. It is here and not in solids.py because the source of
    solids.py is a part of the fingerprint of the skin cache (split.fingerprint)."""
    t = e.tangentAt((e.FirstParameter + e.LastParameter) / 2)
    n = [f.normalAt(*f.Surface.parameter(m)) for f in fs]
    away = n[0].cross(t)
    away.normalize()
    if fs[0].distToShape(Part.Vertex(m + away * 0.3))[0] > fs[0].distToShape(Part.Vertex(m - away * 0.3))[0]:
        away = -away
    return away.dot(n[1]) < 0, so.crease_angle(fs, m)


def survey(parts: dict[str, Part.Shape], d: Blueprint, meta: dict | None = None) -> dict:
    """For each part: its class, the sharp convex edges that turn more than edge_break_turn, grouped by place and by
    what they lie against; and how many of its faces are rounds. `meta` is the manifest of the folder."""
    out = {}
    for name, shape in parts.items():
        if name in face_check.NOT_PARTS:
            continue
        entry = (meta or {}).get(name, {})
        cls = finish_class(name, entry)
        if cls in ("a place", "bought"):
            out[name] = {"class": cls, "sharp": [], "break_faces": 0, "break_corner_faces": 0, "design_round_faces": 0}
            continue
        others, on_top, labels = covers_of(name, parts, d, entry)
        cache: dict[int, str] = {}

        def lies(f: Part.Face) -> str:
            # what the face lies against, found only for the faces of a sharp edge (a print piece has 3000 faces)
            if f.hashCode() not in cache:
                if name in WALLS:
                    cache[f.hashCode()] = piece_face(f, others, d)
                else:
                    k = against(f, others, d)
                    cache[f.hashCode()] = labels.get(k, k)
            return cache[f.hashCode()]
        control = cp.control_edge(entry["coupon"]).translated(V(*entry["offset"])) if entry.get("coupon") in cp.CONTROL else None
        band = None
        if name in BAND_SHOWN and any(hb.kind(k) in ("speaker_pod", "marquee_front", "grille", "light_box") for k in parts):
            band = ([s for k, s in parts.items() if k != name], hb.Scene(parts))
        groups: dict[tuple[str, str], list] = defaultdict(list)
        faces_of = edge_faces(shape)
        for e in shape.Edges:
            if e.Degenerated:
                continue
            fs = faces_of.get(e.hashCode(), [])
            if len(fs) != 2:
                continue
            m = so.middle(e)
            if so.crease_angle(fs, m) <= d.edge_break_turn:   # the cheap half of edge_turn first
                continue
            convex, turn = edge_turn(e, fs, m)
            if not convex or turn <= d.edge_break_turn:
                continue
            hidden = [lies(f) for f in fs if lies(f)]
            if not hidden and name in UNDER:
                # the rim of a round hole of the socket plate under a bought part (socket_plate.covered)
                hidden = [k for k in UNDER[name] if k in parts and parts[k].distToShape(Part.Vertex(m))[0] < spm.COVER][:1]
            if not hidden and control is not None and control.distToShape(Part.Vertex(m))[0] < 0.05:
                hidden = [CONTROL_EDGE]
            if not hidden and (name == "body" or name in WALLS):
                hidden = [r] if (r := not_finished(m, d)) else []
            if band is not None and not any((entry.get("coupon", name), h) in JOINTS for h in hidden) \
                    and (hb.in_joint(shape, e, band[0]) or not band[1].shows(m, hb.edge_out(shape, e))):
                hidden = [HOOD_BAND]   # the band's own rule, where no named joint holds the edge
            if on_top and abs(m.z - d.panel_top) < 1e-6:
                hidden = [j for j in hidden if j in on_top]
            joint = hidden[0] if hidden else ""
            groups[(zone(name, m, d), joint)].append((round(e.Length, 1), round(turn, 1), [round(m.x, 1), round(m.y, 1), round(m.z, 1)]))
        breaks = [f for f in shape.Faces if face_check.is_break(f, d.edge_break)]
        balls = [f for f in shape.Faces if isinstance(f.Surface, Part.Sphere) and abs(f.Surface.Radius - d.edge_break) < 0.02]
        rounds = [f for f in shape.Faces if not isinstance(f.Surface, Part.Plane) and so.tight(f, ROUND_MAX)
                  and not face_check.is_break_surface(f, d.edge_break)]
        out[name] = {"class": cls, "joint_name": entry.get("coupon", name), "open": entry.get("open", ""),
                     "sharp": [{"zone": z, "against": j, "edges": len(es), "length": round(sum(e[0] for e in es), 1),
                                "turn": [min(e[1] for e in es), max(e[1] for e in es)], "at": [e[2] for e in sorted(es, reverse=True)[:6]]}
                               for (z, j), es in sorted(groups.items())],
                     "break_faces": len(breaks), "break_corner_faces": len(balls), "design_round_faces": len(rounds)}
    return out


def failures(rows: dict) -> list[str]:
    """Where the edge rule does not hold: a part in no class, a printed part with a sharp edge that shows, and a
    printed part with a sharp edge in a joint that JOINTS does not name."""
    out = []
    for part, r in rows.items():
        if not r["class"]:
            out.append(f"{part}: the part is in no class (printed, cut plate, provisional, not decided, inside, bought)")
        if r["class"] not in HELD:
            continue
        for g in r["sharp"]:
            if not g["against"] and r.get("open"):
                continue   # not finished, named with its reason in the manifest ("open"): the table lists it
            if not g["against"]:
                out.append(f"{part}, {g['zone']}: {g['edges']} sharp edges show ({g['length']} mm, {g['turn'][0]:g} to {g['turn'][1]:g} degrees), "
                           f"the longest at {tuple(g['at'][0])}")
            elif g["against"].startswith(NOT_FINISHED):
                continue   # a named place that the edge finish leaves as it is: the table lists it
            elif (r.get("joint_name", part), g["against"]) not in JOINTS:
                out.append(f"{part}, {g['zone']}: {g['edges']} sharp edges lie against {g['against']}, which is not a named joint")
    return out


def shows(part_class: str, joint: str) -> str:
    """How a group of sharp edges reads in the list."""
    if joint.startswith(NOT_FINISHED):
        return joint
    if joint:
        return f"in a joint: against {joint}"
    return {"printed": "outside", "cut plate": "outside (a cut plate)", "provisional, not finished": "provisional, not finished",
            "not decided": "outside (not decided)"}.get(part_class, "outside")


def table(rows: dict, d: Blueprint) -> str:
    count = lambda r, joint: sum(g["edges"] for g in r["sharp"] if bool(g["against"]) == joint)

    def verdict(part: str, r: dict) -> str:
        if r["class"] in HELD:
            named = any(g["against"].startswith(NOT_FINISHED) for g in r["sharp"])
            if count(r, False):
                return "not finished, named (see below)" if r.get("open") else "NOT FINISHED"
            return "finished but for named places (see the list)" if named else "finished"
        return r["class"] or "IN NO CLASS"

    lines = ["# Edge finish of the shell", "",
             f"Convex edges that turn more than {d.edge_break_turn:g} degrees and have no round. "
             f"The edge break is R {d.edge_break:g}. The design round of the rear is R {d.rear_round_r:g}.", "",
             "| Part | Class | Faces of the edge break | Faces of design rounds | Sharp edges that show | Sharp edges in a joint | Edge finish |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for part, r in rows.items():
        corners = f" and {r['break_corner_faces']} corner balls" if r["break_corner_faces"] else ""
        lines.append(f"| {part} | {r['class'] or 'none'} | {r['break_faces']}{corners} | {r['design_round_faces']} | {count(r, False)} | {count(r, True)} | {verdict(part, r)} |")
    lines += ["", "| Part | Place | Shows | Edges | Total length, mm | Turn, degrees | Longest at (x, y, z) |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for part, r in rows.items():
        for g in r["sharp"]:
            lines.append(f"| {part} | {g['zone']} | {shows(r['class'], g['against'])} | {g['edges']} | {g['length']} | {g['turn'][0]:g} to {g['turn'][1]:g} | "
                         f"{'; '.join(str(tuple(a)) for a in g['at'][:3])} |")
    lines += ["", "The parts that are not printed and painted parts of the exterior:", ""]
    lines += [f"- `{part}`: {why}" for group in (CUT_PLATES, PROVISIONAL, NOT_DECIDED, INSIDE, BOUGHT) for part, why in group.items() if part in rows]
    lines += ["", "The joints in which a sharp edge of a printed part lies:", ""]
    used = sorted({(r.get("joint_name", part), g["against"]) for part, r in rows.items() if r["class"] in HELD for g in r["sharp"]
                   if g["against"] and not g["against"].startswith(NOT_FINISHED)})
    lines += [f"- `{part}` against {joint}: {JOINTS.get((part, joint), 'NOT A NAMED JOINT')}" for part, joint in used]
    held = sorted({r["open"] for r in rows.values() if r.get("open")})
    if held:
        lines += ["", "Not finished, named with the reason (sharp edges that show, listed and not failed; the edge finish is a guideline):", ""]
        lines += [f"- {', '.join(f'`{p}`' for p, r in rows.items() if r.get('open') == o)}: {o}" for o in held]
    bad = failures(rows)
    lines += ["", "The edge rule holds: no printed part has a sharp edge that shows." if not bad else "The edge rule does NOT hold:", ""]
    lines += [f"- {b}" for b in bad]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    out = os.environ.get("CANDYBAR_OUT", "cad/out/shell-rev7")
    d = Blueprint()
    rows = survey(load(out), d, manifest_of(out))
    json.dump({"parts": rows, "failures": failures(rows)}, open(os.path.join(out, "edge-finish.json"), "w"), indent=1)
    text = table(rows, d)
    open(os.path.join(out, "edge-finish.md"), "w").write(text)
    print(text, end="")
    return 1 if failures(rows) else 0
