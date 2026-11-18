"""The hood band as a design study: the speaker grilles, the marquee and the logo field, in variants for the owner.

The owner chose band A (2026-11-14). Since 2026-11-16 band A is in the default build of the shell: its values and
its geometry are in candybar.shell.band, which solids.build uses. This module keeps the variants B and C and the
studies of a taller hood, and builds each variant, A among them, with its checks and sheets. The cap of the hood is
solids.cap, and every opening of the band is a cutter of candybar.shell.band.

Each variant is one consistent band (VARIANTS):
  A  pods     a raised pod round each speaker, a grille with a field of holes set into the pod, a raised logo field
              with a recess for a badge. This is the band of the reference cabinet.
  B  flush    no pod: the grille lies in an opening of the band whose outer end is parallel to the leg of the hood,
              with level slots; the logo is a recess in the band for a badge.
  C  frames   a low frame round each speaker, a grille with upright slots, and no logo field.
All three have the same marquee: a lit window behind a printed front, a lip with a groove, and a closed light box.

The parts of one band, by name (left parts are mirror images):
  hood                  the cap with the openings of the band (painted)
  marquee_lip_*         the lower frame of the marquee: a bar with a groove that holds the foot of the front (painted)
  speaker_pod_*         the pod or the frame round a speaker (painted; variants A and C)
  logo_field            the raised field for the owner's mark (painted; variant A)
  grille_*              the speaker grille: a black printed insert that also clamps the driver
  logo_badge            the plate with the owner's mark (variants A and B)
  marquee_front_*       the printed translucent front of the marquee, in two halves with a lap
  light_box_*           the closed box behind the marquee window that holds the light (black, inside)
  driver_seat_*         the seat of the driver: a baffle behind the wall with the holes for the heat-set inserts (inside)
  speaker_enclosure_*   the sealed enclosure behind the driver, screwed to the baffle (inside)
  logo_backer           the floor of the logo recess behind the wall (inside; variant B)
  driver_*, led_strip   envelopes of the hardware (assumptions, see Band)

Run headless. It writes one folder for each variant into CANDYBAR_OUT (default cad/out/hood-band): the BREP and STL of
each part, manifest.json, edges.json, focus.json, sections.json, report.json and check.md. The parts of the shell that
do not change are written once into <out>/base. HOOD_BAND_VARIANTS=A,B builds only these variants.

The owner chose band A on the hood as it is (2026-11-14, CHOICE): it is the default build's band. Bands B and C and the
taller hoods stay as variants and studies here.

It also builds two studies of the whole cabinet with a taller hood, for a display in the marquee (TALL): H20 and H46,
each with band A, into <out>/H20 and <out>/H46. Their checks are written and do not fail the run. HOOD_BAND_TALL=
builds none of them.

    CANDYBAR_OUT=cad/out/hood-band cad/candybar/freecad-run.sh candybar.shell.hood_band
    CANDYBAR_OUT=cad/out/hood-band/A cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc     # shell.FCStd
    cad/.venv-tools/bin/python cad/tools/draw_hood_band.py                                        # the sheets
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import FreeCAD
import MeshPart
import Part

from . import profiles as pr
from . import solids as so
from .dims import Blueprint
from .band import (  # noqa: F401 - the band of the default build; this study builds its variants with it
    DEFAULT, MIRROR, Driver, Band, Variant, PARTS, PRINT, kind, loop, plate, rect, grow, stadium, hole, box, one, rounded, right_and_left, Places, leg, places, pod, screws, grille_cutters, grille, small_round, SMALL_LEFT, grille_screws, box_low, baffle, bosses, seat, enclosure, driver, open_area, lip, window, hook_place, marquee_front, hook_slot, light_box, logo_recess, logo_field, logo_badge, logo_backer, hood_cutters, hood_form, build, skin_cutters)

V = FreeCAD.Vector
P2 = tuple[float, float]
# a part that does not show is tested with rays this long, which start this far off the surface
RAY = 600.0
RAY_OFF = 0.4
RAYS = ((0.0, -1.0, 0.0), (0.6, -0.8, 0.0), (-0.6, -0.8, 0.0), (0.0, -0.8, 0.6), (0.0, -0.8, -0.6))
# two inside parts, or an inside part and the skin, interfere when they share more than this, mm3
SHARED = 1.0
# an edge lies in a joint when a point of one of its faces, this far from the edge and this far off the face, is in another part
JOINT_IN = 0.5
JOINT_OUT = 0.05








VARIANTS = {
    "A": DEFAULT,
    "B": Variant("B", "flush", 0.0, "contour", "level slots", 1.0, "recess",
                 "No pod: a grille with level slots in an opening that follows the leg, and a badge recess in the band."),
    "C": Variant("C", "frames", 5.0, "straight", "upright slots", 1.5, "none",
                 "A low frame round each speaker with an upright slot grille, and a plain band with no logo field."),
}
# the owner's choice of 2026-11-14: band A, on the hood as it is (no taller hood)
CHOICE = "A"


@dataclass(frozen=True)
class Tall:
    """A study of the whole cabinet with a taller hood, for a display in the marquee. The hood grows by `extra`, and
    all of it goes into the marquee opening: the band, the lip, the top bar and the lower front of the hood stay."""
    key: str
    name: str
    extra: float
    win_w: float
    win_h: float
    depth: float
    text: str


TALL = {
    "H20": Tall("H20", "hood +20, bar LCD of 8.8 inch", 20.0, 217.0, 54.0, 15.0,
                "The hood is 20 higher, for a bar LCD of 8.8 inch behind a window of 217 x 54. Band A."),
    "H46": Tall("H46", "hood +46, LED matrix 320 x 80", 46.0, 321.0, 81.0, 40.0,
                "The hood is 46 higher, for an LED matrix of 128 x 32 points (320 x 80) behind a window of 321 x 81. Band A."),
}
TALL_FRONT = "#20242c"


def tall_blueprint(t: Tall, d: Blueprint | None = None) -> Blueprint:
    """The blueprint with the taller hood: the flat top and the top of the rear arc are `extra` higher, and the
    marquee opening is `extra` higher. The bend of the hood front stays at its height."""
    d = d or Blueprint()
    open_h = d.hood_marquee_open_h + t.extra
    return replace(d, hood_flat_h=d.hood_flat_h + t.extra, hood_h_ratio=(d.hood_h + t.extra) / d.width, hood_marquee_open_h=open_h,
                   marquee_h=t.win_h, marquee_margin=(open_h - t.win_h) / 2,
                   hood_front_low_share=d.hood_front_low_share * d.hood_flat_h / (d.hood_flat_h + t.extra))


def tall_band(t: Tall, b: Band | None = None) -> Band:
    """The band for a display: the window in the wall is the window of the display, and the box behind it has the
    depth of the display. The envelope "led_strip" is then the display panel."""
    return replace(b or Band(), mq_w=t.win_w, mq_h=t.win_h, box_margin_z=0.0, box_depth=t.depth, led_len=t.win_w - 2.0, led_w=t.win_h - 2.0,
                   led_t=min(10.0, t.depth - 2.0))


BASE = {"deck": "white", "control_panel": "black", "body": "white", "bezel": "black", "screen": "#3a4250"}




# ---------- small solids from outlines in (x, z) ----------





















# ---------- the cap ----------

def cap(d: Blueprint, h: pr.Hood, log: list[str]) -> tuple[Part.Shape, Part.Shape]:
    """The cap of the hood with its edge break, in the hood's frame, and its opening as a prism: solids.cap. (The
    server, OpenCascade 7.8.1, needed a fall-back here that cut the tools of the edge break one at a time;
    with OpenCascade 7.9.3 solids.cap makes the cap of the present hood and of the two taller hoods.)"""
    return so.cap(d, h, log)


def base_dir(out: Path, d: Blueprint) -> Path:
    from . import split  # noqa: PLC0415 - the fingerprint of the form

    return out / "base" / split.fingerprint(d)


def base(out: Path, d: Blueprint, log: list[str], shell: dict[str, Part.Shape] | None = None) -> dict[str, Part.Shape]:
    """The parts that every variant shares, in the cabinet frame, except the cap and its opening, which stay in the
    hood's frame: built once and kept as binary BREP under the fingerprint of the form. `shell` gives the parts below
    the hood for a blueprint that differs in its hood only: then only the cap is made, and its edge break can fail."""
    folder = base_dir(out, d)
    if shell is not None:
        files = {k: folder / f"{k}.bin" for k in ("cap", "opening")}
        if not all(f.exists() for f in files.values()):
            made = dict(zip(files, cap(d, pr.hood(d), log)))
            folder.mkdir(parents=True, exist_ok=True)
            for k, f in files.items():
                made[k].exportBinary(str(f))
        parts = {k: shell[k] for k in BASE}
        for k, f in files.items():
            parts[k] = Part.Shape()
            parts[k].importBinary(str(f))
        return parts
    names = (*BASE, "cap", "opening")
    if all((folder / f"{k}.bin").exists() for k in names):
        parts = {}
        for k in names:
            parts[k] = Part.Shape()
            parts[k].importBinary(str(folder / f"{k}.bin"))
        log.append(f"base parts from {folder}")
        return parts
    fr, h = pr.front(d), pr.hood(d)
    parts = {}
    parts["deck"], parts["control_panel"] = so.deck(d, log)
    parts["body"] = so.body(d, fr, log)
    parts["bezel"] = so.bezel(d, fr)
    parts["screen"] = so.screen(d)
    parts["cap"], parts["opening"] = cap(d, h, log)
    parts = {k: s.Solids[0] if len(s.Solids) == 1 else s for k, s in parts.items()}
    folder.mkdir(parents=True, exist_ok=True)
    for k, s in parts.items():
        s.exportBinary(str(folder / f"{k}.bin"))
    for k in BASE:
        MeshPart.meshFromShape(Shape=parts[k], LinearDeflection=0.05, AngularDeflection=0.05).write(str(folder / f"{k}.stl"))
        parts[k].exportBrep(str(folder / f"{k}.brep"))
    json.dump({k: so.edge_polylines(parts[k]) for k in BASE}, open(folder / "edges.json", "w"))
    return parts


# ---------- where things are ----------







# ---------- the speaker: pod, grille, seat, driver ----------



























# ---------- the marquee: lip, front, light box ----------













# ---------- the logo ----------









# ---------- the hood with the openings of a band ----------





def hood_skin(d: Blueprint, h: pr.Hood, b: Band, v: Variant, pl: Places) -> Part.Shape | None:
    """The skin of the hood (from the cache of the split) with the stand-in lip cut off and the openings of a band cut
    through (band.skin_cutters), in the cabinet frame; None when the skin is not in the cache. It is for the sections and the room check."""
    from . import split  # noqa: PLC0415

    if not split.skin_cached(d):
        return None
    skin = Part.Shape()
    skin.importBinary(str(split.skin_files(d)["hood"]))
    # the skin of the cache has the openings of band A already (cavity.openings); a variant's are cut here as well
    return skin.cut(skin_cutters(d, b, v))


# ---------- one variant ----------



# ---------- the checks ----------

class Scene:
    """All the solids of a build, for the question whether a point shows: a point shows when one of RAYS from it,
    toward the player, meets no solid."""

    def __init__(self, parts: dict[str, Part.Shape]):
        self.solids = [(s.BoundBox, s) for s in parts.values()]

    def free(self, q: FreeCAD.Vector, way: tuple[float, float, float]) -> bool:
        line = Part.makeLine(q, q + V(*way) * RAY)
        box_ = line.BoundBox
        return not any(bb.intersect(box_) and s.distToShape(line)[0] < 1e-7 for bb, s in self.solids)

    def shows(self, p: FreeCAD.Vector, out: FreeCAD.Vector | None = None) -> bool:
        """Whether the point p of a surface shows; `out` points away from the solid there (default: toward the player)."""
        return any(self.free(p + (out or V(*way)) * RAY_OFF, way) for way in RAYS)


def edge_out(shape: Part.Shape, e: Part.Edge) -> FreeCAD.Vector:
    """The direction away from the solid at the middle of an edge: the sum of the outward normals of its two faces."""
    m = so.middle(e)
    n = V(0, 0, 0)
    for f in shape.ancestorsOfType(e, Part.Face):
        n = n + f.normalAt(*f.Surface.parameter(m))
    return n.normalize() if n.Length > 1e-9 else V(0, -1, 0)


def in_joint(shape: Part.Shape, e: Part.Edge, others: list[Part.Shape]) -> bool:
    """Whether an edge lies in a joint: one of its two faces lies against another part beside the edge (a point of
    that face JOINT_IN from the edge, moved JOINT_OUT off the face, is inside the other part)."""
    m = so.middle(e)
    t = e.tangentAt((e.FirstParameter + e.LastParameter) / 2)
    for f in shape.ancestorsOfType(e, Part.Face):
        n = f.normalAt(*f.Surface.parameter(m))
        away = n.cross(t)
        if away.Length < 1e-9:
            continue
        away.normalize()
        if f.distToShape(Part.Vertex(m + away * JOINT_IN))[0] > f.distToShape(Part.Vertex(m - away * JOINT_IN))[0]:
            away = -away
        q = m + away * JOINT_IN + n * JOINT_OUT
        if any(o.BoundBox.isInside(q) and o.isInside(q, 1e-6, True) for o in others):
            return True
    return False


SHOWN = ("painted", "black", "translucent", "plate")   # the classes of the parts that show: the edge rule holds on them




def open_edges(v: Variant) -> dict[str, str]:
    """The parts of a variant whose sharp edges that show are not finished, with the reason: a small break that did
    not build (SMALL_LEFT). The edge finish is a guideline (docs/adr/0007): such a place is listed, not failed."""
    left = [w for w in SMALL_LEFT if "grille" in w]
    if not left or v.grille not in ("holes", "upright slots"):
        return {}
    why = f"not finished: {'; '.join(sorted(set(left)))} did not build, and the rims stay as they are"
    return {f"grille_{s}": why for s in ("right", "left")}


def sharp_edges_that_show(parts: dict[str, Part.Shape], base_parts: dict[str, Part.Shape], d: Blueprint, scene: Scene) -> list[dict]:
    """The edge rule on the parts that show (SHOWN): each convex edge that turns more than edge_break_turn, has no
    round and shows. An edge in a joint does not show, and an edge behind another part does not show."""
    out = []
    for name, shape in parts.items():
        if PARTS[kind(name)][1] not in SHOWN:
            continue
        others = [s for k, s in parts.items() if k != name] + [base_parts[k] for k in BASE]
        where = (lambda m: m.z > d.body_top + d.seam_gap + 0.05) if name == "hood" else (lambda m: True)
        for e, _ in so.sharp_edges(shape, d, where):
            m = so.middle(e)
            if not in_joint(shape, e, others) and scene.shows(m, edge_out(shape, e)):
                out.append({"part": name, "at": [round(m.x, 1), round(m.y, 1), round(m.z, 1)], "length": round(e.Length, 1),
                            "turn": round(so.edge_turn(shape, e)[1], 1)})
    return out


def face_findings(parts: dict[str, Part.Shape], d: Blueprint, scene: Scene) -> tuple[list, list, list]:
    """The face check (tools/face_check.py) on the parts of the band that show: the findings that fail and show, the
    findings that fail and do not show, and the known items of the hood that have no finding."""
    from tools import face_check  # noqa: PLC0415

    allow = face_check.default_reveals() + face_check.band_reveals(parts)
    found = []
    for name, shape in parts.items():
        if PARTS[kind(name)][1] in ("inside", "hardware"):
            continue
        found += face_check.check(shape, name, allow, break_radius=d.edge_break)
    stale = [k for k in face_check.mark_known(found) if k.part == "hood"]
    bad = face_check.failures(found)
    shown = [f for f in bad if scene.shows(V(*f.at))]
    return shown, [f for f in bad if f not in shown], stale


def room(parts: dict[str, Part.Shape], skin: Part.Shape | None) -> dict:
    """The inside parts and the hardware against each other and against the skin of the hood: the volume that two of
    them share (it must be nothing), and the smallest distance of each driver and of the light box to the skin."""
    inside = {k: s for k, s in parts.items() if PARTS[kind(k)][1] in ("inside", "hardware")}
    shared = []
    names = sorted(inside)
    for i, a in enumerate(names):
        for c in names[i + 1:]:
            if inside[a].BoundBox.intersect(inside[c].BoundBox):
                vol = inside[a].common(inside[c]).Volume
                if vol > SHARED:
                    shared.append({"a": a, "b": c, "mm3": round(vol, 1)})
    out: dict = {"shared": shared, "skin": None}
    if skin is not None:
        rows = {}
        for k, s in inside.items():
            near = skin.common(Part.makeBox(*(s.BoundBox.XLength + 20, s.BoundBox.YLength + 20, s.BoundBox.ZLength + 20),
                                            V(s.BoundBox.XMin - 10, s.BoundBox.YMin - 10, s.BoundBox.ZMin - 10)))
            vol = near.common(s).Volume
            rows[k] = {"in_skin_mm3": round(vol, 2)}
            if vol > SHARED:
                shared.append({"a": k, "b": "the skin of the hood", "mm3": round(vol, 1)})
        bb = skin.BoundBox
        rows["hood, outside"] = {"y_rear": round(bb.YMax, 1), "z_top": round(bb.ZMax, 1)}
        out["skin"] = rows
    return out


def print_boxes(parts: dict[str, Part.Shape]) -> dict[str, dict]:
    """The box of each printed part of the band and whether it fits the printer (the hood is in the split)."""
    from . import split  # noqa: PLC0415

    lim = split.printer()
    out = {}
    for name, s in parts.items():
        if name == "hood" or PARTS[kind(name)][1] == "hardware":
            continue
        bb = s.BoundBox
        size = sorted((bb.XLength, bb.YLength, bb.ZLength), reverse=True)
        out[name] = {"box": [round(x, 1) for x in size], "fits": size[0] <= lim.z + 1e-6 and size[1] <= lim.xy + 1e-6}
    return out


def check(parts: dict[str, Part.Shape], base_parts: dict[str, Part.Shape], d: Blueprint, b: Band, drv: Driver, v: Variant,
          skin: Part.Shape | None) -> dict:
    """All the checks of one variant. "failures" lists what does not pass."""
    h = pr.hood(d)
    pl = places(d, h, b, v)
    scene = Scene({**parts, **{k: base_parts[k] for k in BASE}})
    sharp = sharp_edges_that_show(parts, base_parts, d, scene)
    held = open_edges(v)
    sharp, open_ = [e for e in sharp if e["part"] not in held], [e for e in sharp if e["part"] in held]
    shown, hidden, stale = face_findings(parts, d, scene)
    rm = room(parts, skin)
    boxes = print_boxes(parts)
    area = open_area(b, v, drv, pl)
    encl = enclosure(d, h, b, drv, pl)[1]
    invalid = [k for k, s in parts.items() if not s.isValid() or len(s.Solids) != 1]
    failures = [f"{k}: not one valid solid" for k in invalid]
    failures += [f"edge rule: {e['part']} has a sharp edge that shows at {tuple(e['at'])}, {e['length']} long, {e['turn']} degrees" for e in sharp]
    failures += [f"face check: {f.part} {f.rule} at {f.at}: {f.detail}" for f in shown]
    failures += [f"face check: the known item of the hood at {k.at} ({k.rule}) has no finding" for k in stale]
    failures += [f"room: {r['a']} and {r['b']} share {r['mm3']} mm3" for r in rm["shared"]]
    failures += [f"print: {k} does not fit the printer ({x['box']})" for k, x in boxes.items() if not x["fits"]]
    if area["share"] < 0.4:
        failures.append(f"grille: the open area is {area['share']:.0%} of the cone, less than 40%")
    return {"variant": asdict(v), "sharp_edges_that_show": sharp, "sharp_edges_open": open_,
            "open": sorted(set(held[e["part"]] for e in open_)),
            "face_findings_that_show": [asdict(f) for f in shown], "face_findings_hidden": [asdict(f) for f in hidden],
            "room": rm, "print": boxes, "open_area": area, "enclosure": encl, "skin_checked": skin is not None, "failures": failures}


def check_md(rep: dict) -> str:
    v = rep["variant"]
    lines = [f"# Hood band {v['key']} ({v['name']}): checks", "", v["text"], "",
             f"- Sharp convex edges that show, on the parts that show: {len(rep['sharp_edges_that_show'])}",
             f"- Sharp convex edges that show and are an open item for the owner: {len(rep.get('sharp_edges_open', []))}",
             f"- Face-check findings that show: {len(rep['face_findings_that_show'])}",
             f"- Face-check findings on faces that do not show (in a joint or behind a part): {len(rep['face_findings_hidden'])}",
             f"- Open area of the grille in front of the cone: {rep['open_area']['open_mm2']} mm2 of {rep['open_area']['cone_mm2']} ({rep['open_area']['share']:.0%})",
             f"- Sealed enclosure: {rep['enclosure']['litres']} l of air, {rep['enclosure']['inside'][0]} x {rep['enclosure']['inside'][1]} x {rep['enclosure']['depth_inside']} inside, its rear at y {rep['enclosure']['rear_y']}",
             f"- Inside parts and hardware that share volume: {len(rep['room']['shared'])}"
             + ("" if rep["skin_checked"] else " (the skin of the hood is not in the cache: not compared with the skin)"), "",
             "| Part | Box, mm | Fits the printer |", "| --- | --- | --- |"]
    lines += [f"| {k} | {' x '.join(str(x) for x in r['box'])} | {'yes' if r['fits'] else 'NO'} |" for k, r in rep["print"].items()]
    lines += ["", "Result: PASS" if not rep["failures"] else "Result: FAIL", ""]
    lines += [f"- {f}" for f in rep["failures"]]
    if rep.get("open"):
        lines += ["", "Open items:", ""] + [f"- {o}" for o in rep["open"]]
    if rep["face_findings_hidden"]:
        lines += ["", "Findings on faces that do not show:", ""]
        lines += [f"- {f['part']} {f['rule']} at {tuple(f['at'])}: {f['detail']}" for f in rep["face_findings_hidden"]]
    return "\n".join(lines).rstrip() + "\n"


# ---------- output ----------

def section_x(d: Blueprint, b: Band, v: Variant) -> dict[str, float]:
    """Where the two sections are cut: through the centre of the right speaker, and through the marquee and the logo."""
    return {"speaker": round(places(d, pr.hood(d), b, v).cx, 2), "marquee": 30.0}


def sections(parts: dict[str, Part.Shape], skin: Part.Shape | None, xs: dict[str, float]) -> dict:
    """The outline of each part in the planes x = const, in (y, z) of the cabinet frame, as closed polylines."""
    out = {}
    shapes = dict(parts)
    if skin is not None:
        shapes["hood"] = skin
    for label, x in xs.items():
        cut = {}
        for name, s in shapes.items():
            if not s.BoundBox.XMin - 1e-6 < x < s.BoundBox.XMax + 1e-6:
                continue
            loops = [[[round(p.y, 3), round(p.z, 3)] for p in w.discretize(Deflection=0.02)] for w in s.slice(V(1, 0, 0), x)]
            if loops:
                cut[name] = loops
        out[label] = {"x": x, "parts": cut}
    return out


def focus(d: Blueprint, b: Band, v: Variant) -> dict[str, dict]:
    """Close-up cameras on the band for tools/render_views.py."""
    h = pr.hood(d)
    pl = places(d, h, b, v)
    oy, oz = h.origin[1], h.origin[2]
    cam = lambda target, radius, az, el, aspect=0.8: {"target": [round(t, 1) for t in target], "radius": radius, "az": az, "el": el, "aspect": aspect}
    zm = oz + (h.z_rail_top + h.z_open_top) / 2
    return {"band-front": cam((0.0, oy + pl.yb, oz + (h.z_sill + h.z_open_top) / 2), 235.0, 0.0, 2.0, 0.42),
            "band-right": cam((120.0, oy + pl.yb, oz + 70.0), 135.0, 32.0, 8.0, 0.62),
            "band-speaker": cam((pl.cx, oy + pl.yb - 6.0, oz + pl.zc), 62.0, 30.0, 10.0),
            "band-marquee": cam((130.0, oy + pl.yb, zm), 80.0, 24.0, -6.0, 0.6),
            "band-logo": cam((0.0, oy + pl.yb, oz + pl.zc), 110.0, -20.0, 8.0, 0.6)}


def export(folder: Path, parts: dict[str, Part.Shape], base_folder: Path, d: Blueprint, b: Band, v: Variant, rep: dict,
           cuts: dict, log: list[str], finish: dict[str, str] | None = None) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    manifest = {k: {"file": str(base_folder / f"{k}.stl"), "finish": BASE[k], "brep": str(base_folder / f"{k}.brep")} for k in BASE}
    for k, s in parts.items():
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.03, AngularDeflection=0.05).write(str(folder / f"{k}.stl"))
        s.exportBrep(str(folder / f"{k}.brep"))
        manifest[k] = {"file": f"{k}.stl", "finish": (finish or {}).get(kind(k), PARTS[kind(k)][0]), "brep": f"{k}.brep", "class": PARTS[kind(k)][1]}
        if k in open_edges(v):   # for tools/edge_finish.py: the sharp edges of this part that show are an open item
            manifest[k]["open"] = open_edges(v)[k]
    json.dump(manifest, open(folder / "manifest.json", "w"), indent=1)
    edges = json.load(open(base_folder / "edges.json"))
    edges.update({k: so.edge_polylines(s) for k, s in parts.items()})
    json.dump(edges, open(folder / "edges.json", "w"))
    json.dump(focus(d, b, v), open(folder / "focus.json", "w"), indent=1)
    json.dump(cuts, open(folder / "sections.json", "w"))
    rep = dict(rep, log=log, band=asdict(b), parts={k: {"faces": len(s.Faces), "volume_mm3": round(s.Volume, 1)} for k, s in parts.items()})
    json.dump(rep, open(folder / "report.json", "w"), indent=1)
    (folder / "check.md").write_text(check_md(rep), encoding="utf-8")


def main() -> int:
    out = Path(os.environ.get("CANDYBAR_OUT", "cad/out/hood-band")).resolve()
    keys = [k for k in os.environ.get("HOOD_BAND_VARIANTS", "").split(",") if k] or list(VARIANTS)
    d, b, drv = Blueprint(), Band(), Driver()
    h = pr.hood(d)
    log: list[str] = []
    base_parts = base(out, d, log)
    for line in log:
        print(line)
    failed = False
    for key in keys:
        v = VARIANTS[key]
        parts = build(d, b, drv, v, base_parts["cap"], base_parts["opening"])
        skin = hood_skin(d, h, b, v, places(d, h, b, v))
        rep = check(parts, base_parts, d, b, drv, v, skin)
        export(out / key, parts, base_dir(out, d), d, b, v, rep, sections(parts, skin, section_x(d, b, v)), log)
        print(f"variant {key} ({v.name}): {len(parts)} parts, open area {rep['open_area']['share']:.0%}, "
              f"{'PASS' if not rep['failures'] else 'FAIL'}")
        for f in rep["failures"]:
            print("  FAIL", f)
        failed = failed or bool(rep["failures"])
    tall = os.environ.get("HOOD_BAND_TALL")
    for key in ([k for k in tall.split(",") if k] if tall is not None else list(TALL)):
        t = TALL[key]
        d2, b2 = tall_blueprint(t, d), tall_band(t, b)
        v = replace(VARIANTS["A"], key=t.key, name=t.name, text=t.text)
        tlog: list[str] = []
        tall_parts = base(out, d2, tlog, shell=base_parts)
        parts = build(d2, b2, drv, v, tall_parts["cap"], tall_parts["opening"])
        rep = check(parts, tall_parts, d2, b2, drv, v, None)
        bb = parts["hood"].BoundBox
        rep["tall"] = {"extra": t.extra, "cabinet_height": round(bb.ZMax, 1), "hood_box": [round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)],
                       "hood_flat_h": d2.hood_flat_h, "hood_flat_h_over_width": round(d2.hood_flat_h / d2.width, 3),
                       "window": [t.win_w, t.win_h], "marquee_opening_h": d2.hood_marquee_open_h}
        export(out / key, parts, base_dir(out, d), d2, b2, v, rep, sections(parts, None, section_x(d2, b2, v)), tlog, {"marquee_front": TALL_FRONT})
        print(f"study {key} ({t.name}): cabinet {rep['tall']['cabinet_height']} high, {len(rep['failures'])} check failures (a study: they do not fail the run)")
        for line in tlog:
            print("  ", line)
        for f in rep["failures"]:
            print("   finding:", f)
    return 1 if failed else 0
