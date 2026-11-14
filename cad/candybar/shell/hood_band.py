"""The hood band as a design study: the speaker grilles, the marquee and the logo field, in variants for the owner.

The default build (solids.py) has four stand-ins in the opening of the hood: marquee_lip, speaker_left, speaker_right
and logo_form. This module builds the hood with a designed band in their place. It does not change the outer form:
the cap of the hood is solids.cap, and every opening of the band is a cutter that this module makes.

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
  driver_seat_*         the seat of the driver behind the wall, with the holes for the heat-set inserts (inside)
  logo_backer           the floor of the logo recess behind the wall (inside; variant B)
  driver_*, led_strip   envelopes of the hardware (assumptions, see Band)

Run headless. It writes one folder for each variant into CANDYBAR_OUT (default cad/out/hood-band): the BREP and STL of
each part, manifest.json, edges.json, focus.json, sections.json, report.json and check.md. The parts of the shell that
do not change are written once into <out>/base. HOOD_BAND_VARIANTS=A,B builds only these variants.

    CANDYBAR_OUT=cad/out/hood-band cad/candybar/freecad-run.sh candybar.shell.hood_band
    CANDYBAR_OUT=cad/out/hood-band/A cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc     # shell.FCStd
    cad/.venv-tools/bin/python cad/tools/draw_hood_band.py                                        # the sheets
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass
from pathlib import Path

import FreeCAD
import MeshPart
import Part

from . import profiles as pr
from . import solids as so
from .dims import Blueprint

V = FreeCAD.Vector
P2 = tuple[float, float]
MIRROR = (V(0, 0, 0), V(1, 0, 0))
# a part that does not show is tested with rays this long, which start this far off the surface
RAY = 600.0
RAY_OFF = 0.4
RAYS = ((0.0, -1.0, 0.0), (0.6, -0.8, 0.0), (-0.6, -0.8, 0.0), (0.0, -0.8, 0.6), (0.0, -0.8, -0.6))
# two inside parts, or an inside part and the skin, interfere when they share more than this, mm3
SHARED = 1.0
# an edge lies in a joint when a point of one of its faces, this far from the edge and this far off the face, is in another part
JOINT_IN = 0.5
JOINT_OUT = 0.05
PRINTER = (240.0, 240.0, 245.0)


@dataclass(frozen=True)
class Driver:
    """The speaker driver: an assumption. A full-range driver of the 50 mm (2 inch) class with a square frame. The
    values are the envelope that the seat and the grille are made for; no model is chosen."""
    frame: float = 50.0
    frame_t: float = 2.0
    frame_r: float = 3.0
    basket_d: float = 47.0
    basket_depth: float = 12.0
    magnet_d: float = 36.0
    magnet_depth: float = 14.0
    cone_d: float = 44.0


@dataclass(frozen=True)
class Band:
    """The values of the hood band that all variants share. Lengths in mm. z is measured from the foot of the hood
    (the hood's own frame), x from the centre line."""
    wall_t: float = 4.0
    seat_off: float = 0.1           # inside parts stand this far behind the wall, as in the fit study (every second slab of the skin is 0.05 thicker)
    edge_break: float = 1.0
    # --- speakers ---
    spk_half_h: float = 26.0        # half the height of the speaker opening (52: the frame of 50 passes it)
    spk_w: float = 64.0             # width of the straight opening (variants A and C)
    spk_r: float = 4.0              # corner radius of the opening
    spk_contour_inner: float = 112.0    # variant B: the inner end of the opening (6 from the seam H1 at x 106)
    spk_contour_gap: float = 10.0       # variant B: the outer end stands this far inside the leg of the opening
    pod_inner: float = 106.0        # the inner end of a pod (on the line of the seam H1)
    pod_leg_gap: float = 8.0        # the outer end of a pod stands this far inside the leg
    pod_end_gap: float = 2.0        # a pod stands this far above the ledge and below the lip
    pod_r: float = 8.0              # corner radius of a pod, seen from the front
    pod_edge_r: float = 2.5         # round of the front edge of a pod
    grille_t: float = 2.4
    grille_gap: float = 0.15        # between the grille and its opening, each side
    hole_d: float = 3.8
    hole_pitch: float = 5.2
    slot_w: float = 3.4
    slot_pitch: float = 7.0
    slot_centre_bar: float = 5.6    # the bar on the centre line of a slot grille, which takes the two screws
    slot_edge: float = 5.0          # a slot ends this far inside the edge of the grille
    field_half_w: float = 21.0      # the holes and the upright slots lie within this of the driver's centre
    screw_x: float = 29.0           # the two screws of a grille, left and right of the driver's centre
    screw_hole: float = 3.4
    insert_hole: float = 4.0        # for an M3 heat-set insert
    insert_depth: float = 5.65
    bar_w: float = 8.0              # the clamp bar behind a grille that stands in a pod
    bar_half_h: float = 20.0
    seat_face: float = 3.5          # the front of the seat stands this far behind the front of the wall: a flush grille (set back 1.0, 2.4 thick) then lies on the driver's frame
    seat_flange: float = 6.0
    seat_flange_t: float = 5.0
    seat_gap: float = 0.3
    frame_proud: float = 0.1        # the driver's frame stands this far proud of the seat, so that the grille clamps it
    # --- marquee ---
    mq_w: float = 352.0             # the opening in the wall: the lit window (eleven modules of 32)
    mq_h: float = 32.0              # the marquee window of the blueprint (34) less box_margin_z at its top and bottom
    mq_r: float = 3.0
    mq_front_t: float = 2.2
    mq_front_gap: float = 2.0       # between the front and the legs and the top bar: the front lifts by this to come out
    mq_lap: float = 4.0             # half the length of the lap between the two halves of the front
    lip_round: float = 1.0          # the round top of the lip's fence (the fence is 2 thick); also the depth of the groove
    lip_groove: float = 2.5         # the groove behind the fence: the front and 0.3
    hook_w: float = 6.0
    hook_h: float = 8.0
    hook_nose: float = 2.0
    hook_hold: float = 1.3          # how far the nose of a hook stands below its slot when the front is down
    hook_in: float = 6.5            # the middle of a hook stands this far outside the end of the lit window
    box_depth: float = 25.0         # the light box behind the wall: the diffuser distance is this plus the wall
    box_wall: float = 2.0
    box_margin_x: float = 2.0
    box_margin_z: float = 1.0
    box_flange: float = 3.0
    led_w: float = 10.0
    led_t: float = 2.5
    led_len: float = 350.0
    # --- logo ---
    logo_w: float = 176.0
    logo_z0: float = 25.0
    logo_z1: float = 74.9
    logo_proud: float = 5.0
    logo_r: float = 6.0
    logo_inset: float = 5.0
    logo_recess: float = 3.2
    badge_t: float = 2.2
    badge_gap: float = 0.3


    @property
    def lip_proud(self) -> float:
        """How far the lip stands in front of the band: its fence and its groove."""
        return 2 * self.lip_round + self.lip_groove


@dataclass(frozen=True)
class Variant:
    key: str
    name: str
    pod_proud: float        # 0: no pod
    opening: str            # "straight" or "contour"
    grille: str             # "holes", "level slots" or "upright slots"
    grille_setback: float   # the grille stands this far behind the front of the pod, or of the band
    logo: str               # "raised", "recess" or "none"
    text: str


VARIANTS = {
    "A": Variant("A", "pods", 13.0, "straight", "holes", 1.5, "raised",
                 "A pod round each speaker with a hole grille, and a raised logo field with a badge recess."),
    "B": Variant("B", "flush", 0.0, "contour", "level slots", 1.0, "recess",
                 "No pod: a grille with level slots in an opening that follows the leg, and a badge recess in the band."),
    "C": Variant("C", "frames", 5.0, "straight", "upright slots", 1.5, "none",
                 "A low frame round each speaker with an upright slot grille, and a plain band with no logo field."),
}
# the finish of each part for the renders and the FreeCAD document, and its class for the checks:
#   painted      a printed part of the exterior that is filled and painted: the edge rule holds
#   black        a printed part that shows and is not painted (black PETG as printed)
#   translucent  the printed front of the marquee
#   plate        the badge: a printed or cut plate with the owner's mark
#   inside       a printed part behind the wall
#   hardware     an envelope of a purchased part
PARTS = {
    "hood": ("white", "painted"), "marquee_lip": ("white", "painted"), "speaker_pod": ("white", "painted"),
    "logo_field": ("white", "painted"), "grille": ("black", "black"), "logo_badge": ("#2f4f3a", "plate"),
    "marquee_front": ("#e9dca6", "translucent"), "light_box": ("dark", "inside"), "driver_seat": ("dark", "inside"),
    "logo_backer": ("dark", "inside"), "driver": ("grey", "hardware"), "led_strip": ("#d8c060", "hardware"),
}
BASE = {"deck": "white", "control_panel": "black", "body": "white", "bezel": "black", "screen": "#3a4250"}
PRINT = {
    "hood": "As in the split (pieces 18 to 20): the centre on a cut face, each side upright on its foot.",
    "marquee_lip": "On its rear face (the face that lies on the band). The front and the round top are walls.",
    "speaker_pod": "Front face on the bed. The tunnel is a hole through the part. No support.",
    "logo_field": "Rear face on the bed. The recess is open to the top. No support.",
    "grille": "Front face on the bed. The holes or slots go straight up; the clamp bars stand on the plate. No support.",
    "logo_badge": "Flat, front face on the bed.",
    "marquee_front": "Flat, front face on the bed. The hooks stand up; the nose of a hook is a bridge of 2.",
    "light_box": "Mouth on the bed. The rear wall is a bridge of 36 across the box.",
    "driver_seat": "Flange on the bed, the island up. No support.",
    "logo_backer": "Flange on the bed, the island up. No support.",
}


def kind(name: str) -> str:
    """The kind of a part: its name without the side."""
    for end in ("_right", "_left"):
        if name.endswith(end):
            return name[:-len(end)]
    return name


# ---------- small solids from outlines in (x, z) ----------

def loop(points: list[P2], r: float) -> Part.Wire:
    """A closed polygon in (x, z) on the plane y = 0, each corner rounded with the radius r (arcs of circles)."""
    n = len(points)
    at = lambda q: V(q[0], 0.0, q[1])
    if r < 1e-9:
        return Part.makePolygon([at(p) for p in points + points[:1]])
    cuts = []
    for i, p in enumerate(points):
        a, b = points[i - 1], points[(i + 1) % n]
        u1 = ((a[0] - p[0]) / math.dist(a, p), (a[1] - p[1]) / math.dist(a, p))
        u2 = ((b[0] - p[0]) / math.dist(b, p), (b[1] - p[1]) / math.dist(b, p))
        half = math.acos(max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1]))) / 2
        t = r / math.tan(half)
        k = math.hypot(u1[0] + u2[0], u1[1] + u2[1])
        c = (p[0] + (u1[0] + u2[0]) / k * r / math.sin(half), p[1] + (u1[1] + u2[1]) / k * r / math.sin(half))
        m = (c[0] + (p[0] - c[0]) / math.dist(p, c) * r, c[1] + (p[1] - c[1]) / math.dist(p, c) * r)
        cuts.append(((p[0] + u1[0] * t, p[1] + u1[1] * t), m, (p[0] + u2[0] * t, p[1] + u2[1] * t)))
    edges = []
    for i, (a, m, b) in enumerate(cuts):
        edges.append(Part.Arc(at(a), at(m), at(b)).toShape())
        nxt = cuts[(i + 1) % n][0]
        if math.dist(b, nxt) > 1e-9:
            edges.append(Part.LineSegment(at(b), at(nxt)).toShape())
    return Part.Wire(edges)


def plate(points: list[P2], r: float, y0: float, y1: float) -> Part.Shape:
    """A rounded polygon in (x, z) as a solid from y0 to y1."""
    return Part.Face(loop(points, r)).translated(V(0, y0, 0)).extrude(V(0, y1 - y0, 0))


def rect(cx: float, cz: float, w: float, h: float) -> list[P2]:
    return [(cx - w / 2, cz - h / 2), (cx + w / 2, cz - h / 2), (cx + w / 2, cz + h / 2), (cx - w / 2, cz + h / 2)]


def grow(points: list[P2], by: float) -> list[P2]:
    """A convex polygon (counter-clockwise) with each side moved out by a distance."""
    n = len(points)
    lines = []
    for i, p in enumerate(points):
        q = points[(i + 1) % n]
        k = math.dist(p, q)
        nx, nz = (q[1] - p[1]) / k, -(q[0] - p[0]) / k
        lines.append((nx, nz, nx * p[0] + nz * p[1] + by))
    out = []
    for i in range(n):
        (a1, b1, c1), (a2, b2, c2) = lines[i - 1], lines[i]
        det = a1 * b2 - a2 * b1
        out.append(((c1 * b2 - c2 * b1) / det, (a1 * c2 - a2 * c1) / det))
    return out


def stadium(p: P2, q: P2, w: float, y0: float, y1: float) -> Part.Shape:
    """A slot with round ends between the centres p and q in (x, z), w wide, as a solid from y0 to y1."""
    k = math.dist(p, q)
    ux, uz = (q[0] - p[0]) / k, (q[1] - p[1]) / k
    nx, nz = -uz, ux
    r = w / 2
    at = lambda c, a, b: V(c[0] + ux * a + nx * b, 0.0, c[1] + uz * a + nz * b)
    edges = [Part.LineSegment(at(p, 0, -r), at(q, 0, -r)).toShape(), Part.Arc(at(q, 0, -r), at(q, r, 0), at(q, 0, r)).toShape(),
             Part.LineSegment(at(q, 0, r), at(p, 0, r)).toShape(), Part.Arc(at(p, 0, r), at(p, -r, 0), at(p, 0, -r)).toShape()]
    return Part.Face(Part.Wire(edges)).translated(V(0, y0, 0)).extrude(V(0, y1 - y0, 0))


def hole(cx: float, cz: float, dia: float, y0: float, y1: float) -> Part.Shape:
    return Part.makeCylinder(dia / 2, y1 - y0, V(cx, y0, cz), V(0, 1, 0))


def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part.Shape:
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def one(shape: Part.Shape, what: str) -> Part.Shape:
    """The shape as one valid solid, or an error that names the step."""
    if shape.isNull() or not shape.isValid() or len(shape.Solids) != 1:
        raise Part.OCCError(f"hood band: {what} is not one valid solid")
    return shape.Solids[0]


def rounded(solid: Part.Shape, r: float, test, what: str) -> Part.Shape:
    """A round of radius r on the edges of a solid whose middle and ends pass the test."""
    edges = [e for e in solid.Edges if not e.Degenerated and all(test(p) for p in (so.middle(e), *[v.Point for v in e.Vertexes]))]
    if not edges:
        raise Part.OCCError(f"hood band: {what} found no edge to round")
    return one(solid.makeFillet(r, edges), what)


def right_and_left(name: str, right: Part.Shape) -> dict[str, Part.Shape]:
    return {f"{name}_right": right, f"{name}_left": right.mirror(*MIRROR)}


# ---------- the cap ----------

def cap(d: Blueprint, h: pr.Hood, log: list[str]) -> tuple[Part.Shape, Part.Shape]:
    """The cap of the hood with its edge break, in the hood's frame, and its opening as a prism: solids.cap. On some
    machines the one boolean that solids.cut_near does with all the tools of the break leaves most of them uncut, and
    its second try fails on a tool of 0.013 mm3. Then the tools are cut one at a time here, which gives the same cap."""
    try:
        return so.cap(d, h, log)
    except Part.OCCError as err:
        log.append(f"hood: solids.cap failed ({err}). The tools of the edge break are cut one at a time.")
    solid, opening = so.cap_unbroken(d, h, log)
    g = d.seam_groove
    solid = so.settled(solid)
    listed = [e for e, _ in so.sharp_edges(solid, d, lambda m: m.z > 0.05)]
    foot = so.edges_where(solid, lambda p: abs(p.z - g) < 1e-3)
    blunt = [e for e in foot if not any(e.isSame(x) for x in listed)]
    tools, corners = so.round_cutters(solid, listed + blunt, d.edge_break, [])
    good = lambda s: not s.isNull() and s.isValid() and len(s.Solids) == 1
    out = solid
    for k, tool in enumerate(tools):
        due, near = so.held(out, tool)
        for cutter in (tool, near.common(tool)):
            step = out.cut(cutter)
            if good(step) and so.held(step, tool)[0] <= max(so.CUT_LEFT * due, so.CUT_LEFT_MM3):
                out = step
                break
        else:
            raise Part.OCCError(f"hood: tool {k} of the edge break does not cut, one at a time ({due:.3f} mm3)")
    out = so.fit_tolerances(so.cut_round_corners(out, corners, d.edge_break))
    left = so.sharp_edges(out, d, lambda m: m.z > 0.05)
    if left:
        raise Part.OCCError(f"hood: {len(left)} edges are still sharp after the edge break")
    log.append(f"hood, edge break R {d.edge_break:g}, one tool at a time: {len(tools)} tools, {len(out.Faces)} faces")
    return out, opening


def base_dir(out: Path, d: Blueprint) -> Path:
    from . import split  # noqa: PLC0415 - the fingerprint of the form

    return out / "base" / split.fingerprint(d)


def base(out: Path, d: Blueprint, log: list[str]) -> dict[str, Part.Shape]:
    """The parts that every variant shares, in the cabinet frame, except the cap and its opening, which stay in the
    hood's frame: built once and kept as binary BREP under the fingerprint of the form."""
    folder = base_dir(out, d)
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

@dataclass(frozen=True)
class Places:
    """The places of one variant, in the hood's frame."""
    yb: float                   # the front of the band wall (the wall is upright)
    zc: float                   # the height of the speaker's centre
    opening: list[P2]           # the right speaker opening in (x, z), counter-clockwise
    cx: float                   # the driver's centre
    pod: list[P2] | None        # the outline of the right pod
    y_grille: float             # the front of the grille
    y_seat: float               # the front of the seat (the driver's frame lies on it)


def leg(h: pr.Hood, d: Blueprint, z: float) -> float:
    """Half the width of the opening of the hood at height z, on its legs (above the round of the sill's corner)."""
    return h.half_width(max(z, h.z_sill + d.hood_sill_corner_r), h.opening)


def places(d: Blueprint, h: pr.Hood, b: Band, v: Variant) -> Places:
    yb = h.y_band_top
    zc = (h.z_sill + h.z_band_top) / 2
    z0, z1 = zc - b.spk_half_h, zc + b.spk_half_h
    pz0, pz1 = h.z_sill + b.pod_end_gap, h.z_band_top - b.pod_end_gap
    pod = [(b.pod_inner, pz0), (leg(h, d, pz0) - b.pod_leg_gap, pz0), (leg(h, d, pz1) - b.pod_leg_gap, pz1), (b.pod_inner, pz1)]
    if v.opening == "contour":
        out = lambda z: leg(h, d, z) - b.spk_contour_gap
        opening = [(b.spk_contour_inner, z0), (out(z0), z0), (out(z1), z1), (b.spk_contour_inner, z1)]
        cx = (b.spk_contour_inner + out(zc)) / 2
    else:
        cx = (b.pod_inner + leg(h, d, zc) - b.pod_leg_gap) / 2
        opening = rect(cx, zc, b.spk_w, 2 * b.spk_half_h)
    return Places(yb, zc, opening, cx, pod if v.pod_proud else None, yb - v.pod_proud + v.grille_setback, yb + b.seat_face)


# ---------- the speaker: pod, grille, seat, driver ----------

def pod(b: Band, v: Variant, pl: Places) -> Part.Shape:
    """The right pod: its outline raised square to the band, with the tunnel of the speaker opening through it. The
    corners have a radius seen from the front, the front edge has a round, and the rim of the tunnel has the edge
    break."""
    y0 = pl.yb - v.pod_proud
    solid = plate(pl.pod, b.pod_r, y0, pl.yb).cut(plate(pl.opening, b.spk_r, y0 - 1, pl.yb + 1))
    xs, zs = [p[0] for p in pl.opening], [p[1] for p in pl.opening]
    in_tunnel = lambda p: min(xs) - 0.01 < p.x < max(xs) + 0.01 and min(zs) - 0.01 < p.z < max(zs) + 0.01
    front = lambda p: abs(p.y - y0) < 1e-6
    solid = rounded(one(solid, "the pod"), b.pod_edge_r, lambda p: front(p) and not in_tunnel(p), "the round of the pod's front edge")
    return rounded(solid, b.edge_break, lambda p: front(p) and in_tunnel(p), "the edge break of the pod's tunnel")


def screws(pl: Places, b: Band) -> list[P2]:
    return [(pl.cx - b.screw_x, pl.zc), (pl.cx + b.screw_x, pl.zc)]


def grille_cutters(b: Band, v: Variant, pl: Places, y0: float, y1: float) -> list[Part.Shape]:
    """The holes or slots of the right grille, as solids from y0 to y1."""
    cx, zc = pl.cx, pl.zc
    if v.grille == "holes":
        rows = int((b.spk_half_h - 3.5 - b.hole_d / 2) / (b.hole_pitch * math.sqrt(3) / 2))
        out = []
        for j in range(-rows, rows + 1):
            shift = b.hole_pitch / 2 if j % 2 else 0.0
            n = int((b.field_half_w - b.hole_d / 2 + shift) / b.hole_pitch) + 1
            for i in range(-n, n + 1):
                x = i * b.hole_pitch + shift
                if abs(x) <= b.field_half_w - b.hole_d / 2 + 1e-9:
                    out.append(hole(cx + x, zc + j * b.hole_pitch * math.sqrt(3) / 2, b.hole_d, y0, y1))
        return out
    first = b.slot_centre_bar / 2 + b.slot_w / 2
    if v.grille == "upright slots":
        n = int((b.field_half_w - b.slot_w / 2 - first) / b.slot_pitch) + 1
        offs = [s * (first + k * b.slot_pitch) for k in range(n) for s in (1, -1)]
        reach = b.spk_half_h - b.slot_edge - b.slot_w / 2
        return [stadium((cx + o, zc - reach), (cx + o, zc + reach), b.slot_w, y0, y1) for o in offs]
    n = int((b.spk_half_h - b.slot_edge - b.slot_w / 2 - first) / b.slot_pitch) + 1
    offs = [s * (first + k * b.slot_pitch) for k in range(n) for s in (1, -1)]
    (xa, za), (xb, zb) = pl.opening[1], pl.opening[2]
    inner = pl.opening[0][0] + b.slot_edge + b.slot_w / 2
    outer = lambda z: xa + (xb - xa) * (z - za) / (zb - za) - b.slot_edge - b.slot_w / 2
    return [stadium((inner, zc + o), (outer(zc + o), zc + o), b.slot_w, y0, y1) for o in offs]


def grille(b: Band, v: Variant, pl: Places) -> Part.Shape:
    """The right grille: a plate in the speaker opening with its holes or slots and two screw holes. In a pod, two
    clamp bars stand behind the plate and reach back to the driver's frame. With no pod, the plate lies on the frame."""
    y0, y1 = pl.y_grille, pl.y_grille + b.grille_t
    solid = plate(grow(pl.opening, -b.grille_gap), b.spk_r - b.grille_gap, y0, y1)
    y_frame = pl.y_seat - b.frame_proud
    if y_frame - y1 > 0.5:
        for sx in (-1, 1):
            x0 = pl.cx + sx * (b.screw_x + b.bar_w / 2 - 2.0) - b.bar_w / 2
            solid = solid.fuse(box(x0, x0 + b.bar_w, y1, y_frame, pl.zc - b.bar_half_h, pl.zc + b.bar_half_h))
        solid = solid.removeSplitter()
    cutters = grille_cutters(b, v, pl, y0 - 1, y1 + 0.001) + [hole(x, z, b.screw_hole, y0 - 1, y_frame + 1) for x, z in screws(pl, b)]
    return one(solid.cut(cutters), "the grille")


def seat(b: Band, drv: Driver, pl: Places) -> Part.Shape:
    """The right driver seat: a flange behind the wall round the speaker opening, and an island that fills the
    opening up to the seat face. It has a pocket for the driver's frame, a hole for its basket, and two holes for
    heat-set inserts."""
    y_wall = pl.yb + b.wall_t + b.seat_off
    island = plate(grow(pl.opening, -b.seat_gap), b.spk_r - b.seat_gap, pl.y_seat, y_wall + 0.001)
    flange = plate(grow(pl.opening, b.seat_flange), b.spk_r + b.seat_flange, y_wall, y_wall + b.seat_flange_t)
    solid = island.fuse(flange).removeSplitter()
    f = drv.frame + 2 * b.seat_gap
    cutters = [plate(rect(pl.cx, pl.zc, f, f), drv.frame_r + b.seat_gap, pl.y_seat - 1, pl.y_seat + drv.frame_t - b.frame_proud),
               hole(pl.cx, pl.zc, drv.basket_d + 1.0, pl.y_seat - 1, y_wall + b.seat_flange_t + 1)]
    cutters += [hole(x, z, b.insert_hole, pl.y_seat - 1, pl.y_seat + b.insert_depth) for x, z in screws(pl, b)]
    return one(solid.cut(cutters), "the driver seat")


def driver(b: Band, drv: Driver, pl: Places) -> Part.Shape:
    """The envelope of the right driver: the frame, the basket as a cone, the magnet."""
    y0 = pl.y_seat - b.frame_proud
    y1 = y0 + drv.frame_t
    frame = plate(rect(pl.cx, pl.zc, drv.frame, drv.frame), drv.frame_r, y0, y1)
    basket = Part.makeCone(drv.basket_d / 2, drv.magnet_d / 2 + 1.0, drv.basket_depth, V(pl.cx, y1, pl.zc), V(0, 1, 0))
    magnet = Part.makeCylinder(drv.magnet_d / 2, drv.magnet_depth, V(pl.cx, y1 + drv.basket_depth, pl.zc), V(0, 1, 0))
    return one(frame.fuse([basket, magnet]).removeSplitter(), "the driver")


def open_area(b: Band, v: Variant, drv: Driver, pl: Places) -> dict[str, float]:
    """How much of the driver's cone the grille leaves open: the area of its holes or slots inside the cone's circle."""
    disc = Part.Face(Part.Wire(Part.Circle(V(pl.cx, 0, pl.zc), V(0, 1, 0), drv.cone_d / 2).toShape()))
    cuts = Part.makeCompound(grille_cutters(b, v, pl, -1.0, 1.0))
    area = disc.common(cuts).Area
    return {"open_mm2": round(area, 1), "cone_mm2": round(disc.Area, 1), "share": round(area / disc.Area, 3)}


# ---------- the marquee: lip, front, light box ----------

def lip(d: Blueprint, h: pr.Hood, b: Band, opening: Part.Shape) -> dict[str, Part.Shape]:
    """The lip under the marquee, in two halves: a bar across the opening, as high as the stand-in. Its top has a
    fence with a round top, and behind the fence a groove that holds the foot of the marquee front. The lower front
    edge has the edge break. The ends follow the legs of the opening. The lip is lip_proud in front of the band (the
    stand-in is 5): its front stands behind the front of the hood, so that its ends lie on the wall of the leg and not
    in the edge break of the leg's rim."""
    yb, yf = h.y_band_top, h.y_band_top - b.lip_proud
    z0, zt = h.z_band_top, h.z_rail_top
    r, e = b.lip_round, b.edge_break
    zg = zt - r
    at = lambda y, z: V(-300.0, y, z)
    k = math.sqrt(0.5)
    edges = [Part.LineSegment(at(yb, z0), at(yf + e, z0)).toShape(),
             Part.Arc(at(yf + e, z0), at(yf + e - e * k, z0 + e - e * k), at(yf, z0 + e)).toShape(),
             Part.LineSegment(at(yf, z0 + e), at(yf, zg)).toShape(),
             Part.Arc(at(yf, zg), at(yf + r, zt), at(yf + 2 * r, zg)).toShape(),
             Part.LineSegment(at(yf + 2 * r, zg), at(yb, zg)).toShape(),
             Part.LineSegment(at(yb, zg), at(yb, z0)).toShape()]
    bar = Part.Face(Part.Wire(edges)).extrude(V(600.0, 0, 0)).common(opening)
    right = one(bar.common(box(0.0, 300.0, -50.0, 50.0, 0.0, 200.0)), "the lip")
    return right_and_left("marquee_lip", right)


def window(d: Blueprint, h: pr.Hood, b: Band) -> list[P2]:
    """The opening of the lit window in the wall, in (x, z): at the height of the marquee window of the blueprint
    (marquee_margin above the lip, marquee_h high), less box_margin_z at its top and bottom."""
    return rect(0.0, h.z_rail_top + d.marquee_margin + d.marquee_h / 2, b.mq_w, b.mq_h)


def hook_place(d: Blueprint, h: pr.Hood, b: Band) -> tuple[float, float]:
    """The middle of the right hook, in (x, z)."""
    return b.mq_w / 2 + b.hook_in, h.z_rail_top + d.marquee_margin + d.marquee_h / 2


def marquee_front(d: Blueprint, h: pr.Hood, b: Band) -> dict[str, Part.Shape]:
    """The printed front of the marquee, in two halves that lap on the centre line. Its foot stands in the groove of
    the lip. Its ends and its top stand mq_front_gap inside the legs and the top bar. A hook at each end goes through
    a slot in the wall and holds behind it when the front is down."""
    side, corner, top = pr.hood_outline(d, h.height, h.half_base)
    by = d.hood_bar + b.mq_front_gap
    zb = h.z_rail_top - b.lip_round + 0.1
    side_in = so.from_height(so.offset_seg(side, by), zb)
    path = [pr.Line((0.0, zb), (so.ends(side_in)[0][0], zb)), side_in, so.offset_seg(corner, by), so.offset_seg(top, by)]
    yb = h.y_band_top
    solid = so.prism(so.both_sides(path), so.xz(yb - b.mq_front_t), V(0, b.mq_front_t, 0))
    hx, hz = hook_place(d, h, b)
    y_back = yb + b.wall_t + 0.4
    stem = box(hx - b.hook_w / 2, hx + b.hook_w / 2, yb, y_back + b.hook_nose, hz - b.hook_h / 2, hz + b.hook_h / 2)
    nose = box(hx - b.hook_w / 2, hx + b.hook_w / 2, y_back, y_back + b.hook_nose, hz - b.hook_h / 2 - b.hook_nose - b.hook_hold, hz - b.hook_h / 2)
    hook = stem.fuse(nose)
    solid = solid.fuse([hook, hook.mirror(*MIRROR)]).removeSplitter()
    ym = yb - b.mq_front_t / 2
    right_half = box(b.mq_lap, 400.0, -50.0, 50.0, 0.0, 200.0).fuse(box(-b.mq_lap, b.mq_lap + 1.0, ym, 50.0, 0.0, 200.0))
    right = one(solid.common(right_half).removeSplitter(), "the right half of the marquee front")
    left = one(solid.cut(right_half).removeSplitter(), "the left half of the marquee front")
    return {"marquee_front_right": right, "marquee_front_left": left}


def hook_slot(d: Blueprint, h: pr.Hood, b: Band, depth: float) -> Part.Shape:
    """The slot in the wall for the right hook: the hook goes in with the front lifted, and its nose stands hook_hold
    below the slot when the front is down."""
    hx, hz = hook_place(d, h, b)
    z0 = hz - b.hook_h / 2 - b.hook_nose
    z1 = hz + b.hook_h / 2 + b.mq_front_gap
    yb = h.y_band_top
    return box(hx - b.hook_w / 2 - 0.3, hx + b.hook_w / 2 + 0.3, yb - 1, yb + depth, z0, z1)


def light_box(d: Blueprint, h: pr.Hood, b: Band) -> tuple[dict[str, Part.Shape], Part.Shape]:
    """The light box behind the lit window, in two halves, and the envelope of the LED strip on its rear wall. The
    box is closed: five walls and a flange that lies on the rear of the wall round the window. Its mouth is the
    window with a margin."""
    y0 = h.y_band_top + b.wall_t + b.seat_off
    win = window(d, h, b)
    x1, z0, z1 = win[1][0] + b.box_margin_x, win[0][1] - b.box_margin_z, win[2][1] + b.box_margin_z
    w = b.box_wall
    outer = box(-x1 - w, x1 + w, y0, y0 + b.box_depth + w, z0 - w, z1 + w)
    flange = box(-x1 - w - b.box_flange, x1 + w + b.box_flange, y0, y0 + w, z0 - w - b.box_flange, z1 + w + b.box_flange)
    solid = outer.fuse(flange).removeSplitter().cut(box(-x1, x1, y0 - 1, y0 + b.box_depth, z0, z1))
    right = one(solid.common(box(0.0, 400.0, -50.0, 200.0, 0.0, 200.0)), "the light box")
    zm = (z0 + z1) / 2
    led = box(-b.led_len / 2, b.led_len / 2, y0 + b.box_depth - b.led_t, y0 + b.box_depth, zm - b.led_w / 2, zm + b.led_w / 2)
    return right_and_left("light_box", right), led


# ---------- the logo ----------

def logo_recess(b: Band) -> list[P2]:
    w = b.logo_w - 2 * b.logo_inset
    return rect(0.0, (b.logo_z0 + b.logo_z1) / 2, w, b.logo_z1 - b.logo_z0 - 2 * b.logo_inset)


def logo_field(b: Band, yb: float) -> Part.Shape:
    """The raised logo field: a block on the band with round corners, the edge break on its front edge, and a recess
    for the badge whose rim has the edge break too."""
    y0 = yb - b.logo_proud
    outline = rect(0.0, (b.logo_z0 + b.logo_z1) / 2, b.logo_w, b.logo_z1 - b.logo_z0)
    solid = plate(outline, b.logo_r, y0, yb).cut(plate(logo_recess(b), b.logo_r - b.logo_inset + 2.0, y0 - 1, y0 + b.logo_recess))
    return rounded(one(solid, "the logo field"), b.edge_break, lambda p: abs(p.y - y0) < 1e-6, "the edge break of the logo field")


def logo_badge(b: Band, y_floor: float) -> Part.Shape:
    """The badge: a plate that lies on the floor of the recess, 1 below its rim."""
    return plate(grow(logo_recess(b), -b.badge_gap), b.logo_r - b.logo_inset + 2.0 - b.badge_gap, y_floor - b.badge_t, y_floor)


def logo_backer(b: Band, yb: float) -> Part.Shape:
    """The floor of a logo recess that is an opening in the wall: a flange behind the wall and an island in the opening."""
    y_wall = yb + b.wall_t + b.seat_off
    r = b.logo_r - b.logo_inset + 2.0
    island = plate(grow(logo_recess(b), -b.seat_gap), r - b.seat_gap, yb + b.logo_recess, y_wall + 0.001)
    flange = plate(grow(logo_recess(b), b.seat_flange), r + b.seat_flange, y_wall, y_wall + 3.0)
    return one(island.fuse(flange).removeSplitter(), "the logo backer")


# ---------- the hood with the openings of a band ----------

def hood_cutters(d: Blueprint, h: pr.Hood, b: Band, v: Variant, pl: Places, depth: float) -> tuple[list[Part.Shape], list[list[P2]]]:
    """What a band cuts out of the wall: the cutters (as deep as `depth` behind the front of the wall), and the
    outlines of the openings whose rim shows and gets the edge break."""
    yb = pl.yb
    cut = lambda pts, r: plate(pts, r, yb - 1, yb + depth)
    spk = cut(pl.opening, b.spk_r)
    slot = hook_slot(d, h, b, depth)
    cutters = [cut(window(d, h, b), b.mq_r), spk, spk.mirror(*MIRROR), slot, slot.mirror(*MIRROR)]
    rims: list[list[P2]] = []
    if not v.pod_proud:
        rims += [pl.opening, [(-x, z) for x, z in pl.opening]]
    if v.logo == "recess":
        cutters.append(cut(logo_recess(b), b.logo_r - b.logo_inset + 2.0))
        rims.append(logo_recess(b))
    return cutters, rims


def hood_form(d: Blueprint, h: pr.Hood, b: Band, v: Variant, pl: Places, solid: Part.Shape) -> Part.Shape:
    """The cap as an outer form with the openings of a band: each opening is a pocket through the wall and wall_t
    deeper. The rim of an opening that shows gets the edge break."""
    cutters, rims = hood_cutters(d, h, b, v, pl, 2 * b.wall_t)
    out = one(solid.cut(cutters), "the hood with the openings of the band")
    for pts in rims:
        xs, zs = [p[0] for p in pts], [p[1] for p in pts]
        on_rim = lambda p, xs=xs, zs=zs: abs(p.y - pl.yb) < 1e-6 and min(xs) - 0.01 < p.x < max(xs) + 0.01 and min(zs) - 0.01 < p.z < max(zs) + 0.01
        out = rounded(out, b.edge_break, on_rim, "the edge break of an opening of the band")
    return out


def hood_skin(d: Blueprint, h: pr.Hood, b: Band, v: Variant, pl: Places) -> Part.Shape | None:
    """The skin of the hood (from the cache of the split) with the stand-in lip cut off and the openings of a band cut
    through, in the cabinet frame; None when the skin is not in the cache. It is for the sections and the room check."""
    from . import split  # noqa: PLC0415

    if not split.skin_cached(d):
        return None
    skin = Part.Shape()
    skin.importBinary(str(split.skin_files(d)["hood"]))
    cutters, _ = hood_cutters(d, h, b, v, pl, 3 * b.wall_t)
    yb = pl.yb
    cutters.append(box(-300.0, 300.0, yb - d.hood_rail_proud - 1.0, yb, h.z_band_top - 0.01, h.z_rail_top + 0.01))
    return skin.cut([so.hood_frame(h)(c) for c in cutters])


# ---------- one variant ----------

def build(d: Blueprint, b: Band, drv: Driver, v: Variant, cap_solid: Part.Shape, opening: Part.Shape) -> dict[str, Part.Shape]:
    """The parts of one hood band, by name, in the cabinet frame."""
    h = pr.hood(d)
    pl = places(d, h, b, v)
    out: dict[str, Part.Shape] = {"hood": hood_form(d, h, b, v, pl, cap_solid)}
    out.update(lip(d, h, b, opening))
    if v.pod_proud:
        out.update(right_and_left("speaker_pod", pod(b, v, pl)))
    out.update(right_and_left("grille", grille(b, v, pl)))
    if v.logo == "raised":
        out["logo_field"] = logo_field(b, pl.yb)
        out["logo_badge"] = logo_badge(b, pl.yb - b.logo_proud + b.logo_recess)
    elif v.logo == "recess":
        out["logo_badge"] = logo_badge(b, pl.yb + b.logo_recess)
        out["logo_backer"] = logo_backer(b, pl.yb)
    out.update(marquee_front(d, h, b))
    boxes, led = light_box(d, h, b)
    out.update(boxes)
    out["led_strip"] = led
    out.update(right_and_left("driver_seat", seat(b, drv, pl)))
    out.update(right_and_left("driver", driver(b, drv, pl)))
    return {k: so.hood_frame(h)(s) for k, s in out.items()}


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


def sharp_edges_that_show(parts: dict[str, Part.Shape], base_parts: dict[str, Part.Shape], d: Blueprint, scene: Scene) -> list[dict]:
    """The edge rule on the painted parts: each convex edge that turns more than edge_break_turn, has no round and
    shows. An edge in a joint does not show, and an edge behind another part does not show."""
    out = []
    for name, shape in parts.items():
        if PARTS[kind(name)][1] != "painted":
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

    allow = face_check.default_reveals()
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
    out = {}
    for name, s in parts.items():
        if name == "hood" or PARTS[kind(name)][1] == "hardware":
            continue
        bb = s.BoundBox
        size = sorted((bb.XLength, bb.YLength, bb.ZLength), reverse=True)
        out[name] = {"box": [round(x, 1) for x in size], "fits": size[0] <= PRINTER[2] + 1e-6 and size[1] <= PRINTER[0] + 1e-6}
    return out


def check(parts: dict[str, Part.Shape], base_parts: dict[str, Part.Shape], d: Blueprint, b: Band, drv: Driver, v: Variant,
          skin: Part.Shape | None) -> dict:
    """All the checks of one variant. "failures" lists what does not pass."""
    h = pr.hood(d)
    pl = places(d, h, b, v)
    scene = Scene({**parts, **{k: base_parts[k] for k in BASE}})
    sharp = sharp_edges_that_show(parts, base_parts, d, scene)
    shown, hidden, stale = face_findings(parts, d, scene)
    rm = room(parts, skin)
    boxes = print_boxes(parts)
    area = open_area(b, v, drv, pl)
    invalid = [k for k, s in parts.items() if not s.isValid() or len(s.Solids) != 1]
    failures = [f"{k}: not one valid solid" for k in invalid]
    failures += [f"edge rule: {e['part']} has a sharp edge that shows at {tuple(e['at'])}, {e['length']} long, {e['turn']} degrees" for e in sharp]
    failures += [f"face check: {f.part} {f.rule} at {f.at}: {f.detail}" for f in shown]
    failures += [f"face check: the known item of the hood at {k.at} ({k.rule}) has no finding" for k in stale]
    failures += [f"room: {r['a']} and {r['b']} share {r['mm3']} mm3" for r in rm["shared"]]
    failures += [f"print: {k} does not fit the printer ({x['box']})" for k, x in boxes.items() if not x["fits"]]
    if area["share"] < 0.4:
        failures.append(f"grille: the open area is {area['share']:.0%} of the cone, less than 40%")
    return {"variant": asdict(v), "sharp_edges_that_show": sharp,
            "face_findings_that_show": [asdict(f) for f in shown], "face_findings_hidden": [asdict(f) for f in hidden],
            "room": rm, "print": boxes, "open_area": area, "skin_checked": skin is not None, "failures": failures}


def check_md(rep: dict) -> str:
    v = rep["variant"]
    lines = [f"# Hood band {v['key']} ({v['name']}): checks", "", v["text"], "",
             f"- Sharp convex edges of painted parts that show: {len(rep['sharp_edges_that_show'])}",
             f"- Face-check findings that show: {len(rep['face_findings_that_show'])}",
             f"- Face-check findings on faces that do not show (in a joint or behind a part): {len(rep['face_findings_hidden'])}",
             f"- Open area of the grille in front of the cone: {rep['open_area']['open_mm2']} mm2 of {rep['open_area']['cone_mm2']} ({rep['open_area']['share']:.0%})",
             f"- Inside parts and hardware that share volume: {len(rep['room']['shared'])}"
             + ("" if rep["skin_checked"] else " (the skin of the hood is not in the cache: not compared with the skin)"), "",
             "| Part | Box, mm | Fits the printer |", "| --- | --- | --- |"]
    lines += [f"| {k} | {' x '.join(str(x) for x in r['box'])} | {'yes' if r['fits'] else 'NO'} |" for k, r in rep["print"].items()]
    lines += ["", "Result: PASS" if not rep["failures"] else "Result: FAIL", ""]
    lines += [f"- {f}" for f in rep["failures"]]
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
           cuts: dict, log: list[str]) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    manifest = {k: {"file": str(base_folder / f"{k}.stl"), "finish": BASE[k], "brep": str(base_folder / f"{k}.brep")} for k in BASE}
    for k, s in parts.items():
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.03, AngularDeflection=0.05).write(str(folder / f"{k}.stl"))
        s.exportBrep(str(folder / f"{k}.brep"))
        manifest[k] = {"file": f"{k}.stl", "finish": PARTS[kind(k)][0], "brep": f"{k}.brep", "class": PARTS[kind(k)][1]}
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
    return 1 if failed else 0
