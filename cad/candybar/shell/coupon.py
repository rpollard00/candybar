"""The joint coupon: two halves of a curved wall joined by joint 1 (candybar.shell.joints), in three groove
clearances, and the flat plaque for the primer tests of docs/research/petg-finishing.md, section 4.

    CANDYBAR_OUT=cad/out/coupon cad/candybar/freecad-run.sh candybar.shell.coupon

Shape. The wall is curved in plan on a radius of 300 (convex outside, like a rounded corner of the body) and the
seam is a level line along it, as L1 runs round the body. Each half is 130 along the arc and 60 from the seam to its
free edge, so the pair is 130 x 120 across the seam: the 120 long coupon of the research note, with two screws at the
real pitch of 60. Print orientation: the orientation of the wall pieces of the proposal (all upright). The lower half
is the piece below L1 (lower R or L, piece 5 or 6), printed upright with the seam at its top: its level flange stands
on the 45 degree gusset. The upper half is the piece above L1 (middle R or L, piece 7 or 8), printed upright with the
seam on the bed. The lower half stands on a joint 3 foot flange (12 x 4) at its free edge, as a lower piece stands
on its foot flange. The outer face is a wall in both halves and needs no support.

Outputs in CANDYBAR_OUT (default cad/out/coupon):
  step/, stl/       every part in its print orientation, and step/coupon-pair-c02-assembled.step
  assembled/        STL of the pair at 0.2 in the assembled position (for the drawing and the renders)
  checks.json       the checks with numbers; main() returns 1 when one fails
  drawing.json      the sections across the joint, for tools/draw_coupon.py
  README.md         what to print and how to test it
Then draw (coupon.png) and render (renders/), after this run has ended:
    cad/.venv-tools/bin/python cad/tools/draw_coupon.py cad/out/coupon
"""
from __future__ import annotations

import csv
import json
import math
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from .joints import JOINT, Arc, Joint, flange_profile, foot_profile, screw_stations, seam_edge, skin_profile

CAD = Path(__file__).resolve().parents[2]
CLEARANCES = (0.1, 0.2, 0.3)
RADIUS = 300.0
LENGTH = 130.0          # along the arc, on the outer face
HALF = 60.0             # from the seam plane to the free edge of each half
DOT_D = 3.0             # clearance marks: sunk 90 degree cones on the inner face, one dot for each 0.1
DOT_PITCH = 5.0
DOT_Z = 36.0
PLAQUE = (120.0, 60.0, 4.0)   # long, high, thick; printed upright on a long edge
PLAQUE_FOOT = (8.0, 4.0)      # on the back at the bed: depth, height
OVERHANG_LIMIT = 45.0         # degrees from vertical; the proposal prints 45 degree gussets and slopes with no support
ASSEMBLED_C = 0.2
MESH_LINEAR, MESH_ANGULAR = 0.02, 0.1


@dataclass(frozen=True)
class Printer:
    xy: float
    z: float


def printer(params_dir: Path = CAD / "params") -> Printer:
    rows = {r["name"]: r for r in csv.DictReader(open(params_dir / "printer.csv", encoding="utf-8"))}
    return Printer(float(rows["a1_part_max_xy"]["value"]), float(rows["a1_part_max_z"]["value"]))


def tag(c: float) -> str:
    return f"c{round(c * 10):02d}"


def path() -> Arc:
    return Arc(RADIUS, -LENGTH / 2, LENGTH / 2)


def stations(j: Joint = JOINT) -> list[float]:
    return screw_stations(path(), j.screw_pitch)


def pilots(j: Joint = JOINT) -> list[float]:
    """One pilot of each candidate in every lower half: the smaller (PET value) at -30, the larger (ABS value) at +30."""
    return [j.pilot_d_pet, j.pilot_d_abs]


PILOT_MARK = (8.0, 2.0, 1.0, -24.0)   # the sunk bar beside the smaller pilot: length, width, depth, height (z)


# ---------- parts, in the assembled position (seam plane z = 0, outer face toward -y) ----------

def _dots(j: Joint, n: int, z: float):
    import FreeCAD as App
    import Part
    p = path()
    out = []
    for k in range(n):
        s = (k - (n - 1) / 2) * DOT_PITCH
        lift = 0.2
        base = App.Vector(*p.point(s, j.wall_t + lift, z))
        out.append(Part.makeCone(DOT_D / 2 + lift, 0.0, DOT_D / 2 + lift, base, App.Vector(*[-v for v in p.inward(s)])))
    return out


def _cut(body, tools):
    for t in tools:
        body = body.cut(t)
    return body.removeSplitter()


def pilot_mark(j: Joint = JOINT):
    """A sunk bar on the inner face under the smaller pilot: a V of 45 degree faces, so it prints with no support."""
    length, width, depth, z = PILOT_MARK
    s = stations(j)[pilots(j).index(min(pilots(j)))]
    w = j.wall_t + 0.01
    return path().sweep([(w, z - width / 2), (w, z + width / 2), (w - depth, z)], s - length / 2, s + length / 2)


def lower_half(c: float, j: Joint = JOINT, holes: bool = True):
    p = path()
    add, cut = seam_edge(j, p, "below", stations(j), pilots=pilots(j))
    body = p.sweep(skin_profile(j, "below", HALF)).fuse([add, p.sweep(foot_profile(j, HALF))]).removeSplitter()
    return _cut(body, ([cut] if holes else []) + _dots(j, round(c * 10), -DOT_Z) + [pilot_mark(j)])


def upper_half(c: float, j: Joint = JOINT):
    p = path()
    add, cut = seam_edge(j, p, "above", stations(j), c)
    body = p.sweep(skin_profile(j, "above", HALF)).fuse(add).removeSplitter()
    return _cut(body, [cut] + _dots(j, round(c * 10), DOT_Z))


def plaque(code: int):
    """Flat plaque, show face at y = 0 toward -y, standing on a long edge. The halves: x < 60 is scuffed (it carries
    the code dots on the back), x > 60 is wiped only. The line between them: a V notch in the top edge and a V line
    on the back, both at x = 60."""
    import FreeCAD as App
    import Part
    L, H, T = PLAQUE
    fd, fh = PLAQUE_FOOT
    body = Part.makeBox(L, T, H).fuse(Part.makeBox(L, fd, fh, App.Vector(0, T - 0.5, 0))).removeSplitter()
    m = L / 2
    notch = Part.Face(Part.makePolygon([App.Vector(m - 1, -1, H + 0.01), App.Vector(m + 1, -1, H + 0.01),
                                        App.Vector(m, -1, H - 1), App.Vector(m - 1, -1, H + 0.01)])).extrude(App.Vector(0, T + 2, 0))
    line = Part.Face(Part.makePolygon([App.Vector(m - 0.5, T + 0.01, fh), App.Vector(m + 0.5, T + 0.01, fh),
                                       App.Vector(m, T - 0.5, fh), App.Vector(m - 0.5, T + 0.01, fh)])).extrude(App.Vector(0, 0, H - fh + 1))
    dots = []
    for k in range(code):
        x = m / 2 + (k - (code - 1) / 2) * DOT_PITCH
        dots.append(Part.makeCone(DOT_D / 2 + 0.2, 0.0, DOT_D / 2 + 0.2, App.Vector(x, T + 0.2, H * 0.6), App.Vector(0, -1, 0)))
    return _cut(body, [notch, line, *dots])


def to_bed(shape):
    """Move a part that is already upright so that its box starts at the origin (the print orientation)."""
    import FreeCAD as App
    b = shape.BoundBox
    s = shape.copy()
    s.translate(App.Vector(-b.XMin, -b.YMin, -b.ZMin))
    return s


# ---------- checks ----------

def overhangs(shape, limit_deg: float = OVERHANG_LIMIT, tol: float = 0.01) -> list[dict]:
    """Downward faces steeper than the limit (measured from vertical), not on the bed, grouped by height."""
    import MeshPart
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=MESH_LINEAR, AngularDeflection=MESH_ANGULAR, Relative=False)
    zmin = shape.BoundBox.ZMin
    bound = -math.cos(math.radians(90 - limit_deg)) - tol
    groups: dict[float, dict] = {}
    for f in mesh.Facets:
        n = f.Normal
        pts = f.Points
        if n.z >= bound or max(p[2] for p in pts) < zmin + 0.05:
            continue
        zc = round(sum(p[2] for p in pts) / 3 - zmin, 1)
        g = groups.setdefault(zc, {"z": zc, "area_mm2": 0.0, "steepest_deg": 0.0, "x": [1e9, -1e9], "y": [1e9, -1e9]})
        g["area_mm2"] += f.Area
        g["steepest_deg"] = max(g["steepest_deg"], math.degrees(math.asin(min(1.0, -n.z))))
        for p in pts:
            g["x"] = [min(g["x"][0], p[0]), max(g["x"][1], p[0])]
            g["y"] = [min(g["y"][0], p[1]), max(g["y"][1], p[1])]
    out = []
    for g in groups.values():
        g["area_mm2"] = round(g["area_mm2"], 1)
        g["steepest_deg"] = round(g["steepest_deg"], 1)
        g["x"] = [round(v, 1) for v in g["x"]]
        g["y"] = [round(v, 1) for v in g["y"]]
        out.append(g)
    return sorted(out, key=lambda g: g["z"])


def _merge_heights(groups: list[dict], step: float = 0.15) -> list[dict]:
    """Join groups whose heights are within a mesh step: one face is one entry."""
    out: list[dict] = []
    for g in groups:
        if out and g["z"] - out[-1]["z_max"] <= step:
            o = out[-1]
            o["z_max"] = g["z"]
            o["area_mm2"] = round(o["area_mm2"] + g["area_mm2"], 1)
            o["steepest_deg"] = max(o["steepest_deg"], g["steepest_deg"])
        else:
            out.append({"z": g["z"], "z_max": g["z"], "area_mm2": g["area_mm2"], "steepest_deg": g["steepest_deg"]})
    return out


def bridge_exception(j: Joint, part: str, z: float) -> str | None:
    """The stated exceptions: the only downward faces past the limit that the coupon is allowed to have."""
    if part.startswith("upper") and z < j.vgroove_w / 2 + 0.05:
        return (f"the half V-groove on the outer edge at the bed: {j.vgroove_d:g} deep over {j.vgroove_w / 2:g} high "
                f"({math.degrees(math.atan2(j.vgroove_d, j.vgroove_w / 2)):.0f} degrees from vertical), two to three layers; "
                "it needs no support and the filler fills it")
    if part.startswith("lower") and abs(z - (HALF + PILOT_MARK[3])) < PILOT_MARK[1]:
        return "pilot mark: a V bar with 45 degree faces, at the limit; only mesh facets pass it"
    if part.startswith(("upper", "lower")) and abs(abs(z - (HALF if part.startswith("upper") else 0.0)) - (HALF - DOT_Z)) < DOT_D:
        return "clearance dot: a 90 degree cone, 45 degrees at its top; only mesh facets pass the limit"
    if part.startswith("upper") and abs(z - j.groove_depth) < 0.2:
        return "groove ceiling: a bridge over the groove on the flange face, inside, never seen"
    return None


def faces_at(shape, z: float, nz: float):
    return [f for f in shape.Faces if abs(f.BoundBox.ZMin - z) < 1e-6 and abs(f.BoundBox.ZMax - z) < 1e-6
            and f.normalAt(*_mid(f)).z * nz > 0.99]


def _mid(face):
    u0, u1, v0, v1 = face.ParameterRange
    return (u0 + u1) / 2, (v0 + v1) / 2


def hole_axes(shape, radius: float) -> list[tuple[float, float]]:
    """(x, y) of the axes of the vertical cylindrical faces of this radius."""
    out = []
    for f in shape.Faces:
        s = f.Surface
        if type(s).__name__ == "Cylinder" and abs(s.Radius - radius) < 1e-6 and abs(abs(s.Axis.z) - 1) < 1e-9:
            xy = (round(s.Center.x, 4), round(s.Center.y, 4))
            if xy not in out:
                out.append(xy)
    return sorted(out)


def key_gaps(j: Joint, lower, upper) -> dict:
    """Gaps from each key run to the upper half: at the two sides, the two ends and the top."""
    import Part
    from .joints import key_solids
    p = path()
    sides, ends, tops = [], [], []
    for k in key_solids(j, p, stations(j)):
        for f in k.Faces:
            n = f.normalAt(*_mid(f))
            c = f.valueAt(*_mid(f))
            if c.z < 0.1 and n.z < 0.5:
                continue                                         # the part inside the lower flange
            if n.z > 0.99:
                tops.append(Part.Vertex(c).distToShape(upper)[0])      # at the middle of the face
            elif abs(n.z) < 1e-6:
                radial = abs(n.x * c.x + n.y * c.y) / math.hypot(c.x, c.y)
                if radial > 0.99:
                    sides.append(Part.Vertex(c).distToShape(upper)[0])
                else:
                    ends.append(f.distToShape(upper)[0])                 # the nearest point of the end face
    return {"side_min": round(min(sides), 4), "side_max": round(max(sides), 4), "end_min": round(min(ends), 4),
            "end_max": round(max(ends), 4), "top": round(min(tops), 4), "runs": len(key_solids(j, p, stations(j)))}


def check_pair(j: Joint, c: float, lower, upper, lower_body) -> dict:
    import FreeCAD as App
    import Part
    common = lower.common(upper).Volume
    gaps = key_gaps(j, lower, upper)
    lower_top, upper_bottom = faces_at(lower, 0.0, 1.0), faces_at(upper, 0.0, -1.0)
    touch = Part.makeCompound(lower_top).common(Part.makeCompound(upper_bottom))
    contact = touch.Area
    slab = path().sweep([(j.wall_t, -1.0), (j.wall_t + j.flange_h, -1.0), (j.wall_t + j.flange_h, 1.0), (j.wall_t, 1.0)])
    flange_contact = touch.common(slab).Area
    near = lambda a, b: math.hypot(a[0] - b[0], a[1] - b[1])
    clears = hole_axes(upper, j.clearance_d / 2)
    found = {d: hole_axes(lower, d / 2) for d in sorted(set(pilots(j)))}
    pilot_axes = [a for axes in found.values() for a in axes]
    offsets = [min(near(a, b) for b in clears) for a in pilot_axes] if clears and pilot_axes else [math.inf]
    per_station, pilot_out = [], 0.0
    for s, d in zip(stations(j), pilots(j), strict=True):
        x, y, _ = path().point(s, j.screw_u, 0.0)
        own = min((near(a, (x, y)) for a in found[d]), default=math.inf)
        other = min((near(a, (x, y)) for e, axes in found.items() if e != d for a in axes), default=math.inf)
        per_station.append({"s": s, "pilot_d": d, "axis_vs_layout_mm": round(own, 6), "right_diameter": own < 1e-4 and other > 1.0})
        cyl = Part.makeCylinder(d / 2, j.pilot_depth, App.Vector(x, y, -j.pilot_depth), App.Vector(0, 0, 1))
        pilot_out += cyl.cut(lower_body).Volume
    off_expected = max(p["axis_vs_layout_mm"] for p in per_station)
    reach = j.screw_l - j.flange_t
    res = {
        "clearance": c,
        "valid": lower.isValid() and upper.isValid(),
        "common_volume_mm3": round(common, 6),
        "key_gap_side_mm": [gaps["side_min"], gaps["side_max"]],
        "key_gap_end_mm": [gaps["end_min"], gaps["end_max"]],
        "key_gap_top_mm": gaps["top"],
        "key_runs": gaps["runs"],
        "seam_contact_mm2": round(contact, 1),
        "flange_contact_mm2": round(flange_contact, 1),
        "screws": len(stations(j)),
        "screw_axis_offset_mm": round(max(offsets), 6),
        "screw_axis_vs_layout_mm": round(off_expected, 6),
        "pilot_holes": len(pilot_axes), "clearance_holes": len(clears), "pilots": per_station,
        "screw_reach_into_lower_mm": reach, "pilot_depth_mm": j.pilot_depth,
        "pilot_breaks_out_mm3": round(pilot_out, 6),
    }
    res["pass"] = bool(res["valid"] and common < 1e-6 and abs(gaps["side_min"] - c) < 2e-3 and abs(gaps["side_max"] - c) < 2e-3
                       and gaps["end_min"] >= c - 0.02 and gaps["top"] >= j.groove_extra_depth - 1e-3
                       and flange_contact > 0.6 * j.flange_h * LENGTH and len(pilot_axes) == len(clears) == res["screws"]
                       and all(p["right_diameter"] for p in per_station)
                       and res["screw_axis_offset_mm"] < 1e-4 and off_expected < 1e-4 and pilot_out < 1e-6
                       and reach < j.pilot_depth)
    return res


def check_part(j: Joint, name: str, shape, lim: Printer) -> dict:
    b = shape.BoundBox
    groups = _merge_heights(overhangs(shape))
    for g in groups:
        g["exception"] = bridge_exception(j, name, g["z"])
    fits = b.XLength <= lim.xy and b.YLength <= lim.xy and b.ZLength <= lim.z and abs(b.ZMin) < 1e-6
    res = {"part": name, "valid": shape.isValid(), "solids": len(shape.Solids),
           "box_mm": [round(b.XLength, 1), round(b.YLength, 1), round(b.ZLength, 1)], "fits_bed": fits,
           "volume_cm3": round(shape.Volume / 1000, 2), "overhangs": groups,
           "unstated_overhang_mm2": round(sum(g["area_mm2"] for g in groups if not g["exception"]), 2)}
    res["pass"] = bool(res["valid"] and res["solids"] == 1 and fits and res["unstated_overhang_mm2"] < 0.5)
    return res


# ---------- drawing data ----------

def section(shapes: dict, s: float) -> dict:
    """The cut of the parts by the vertical plane through the z axis at arc length s, as polylines in (u, z)."""
    import FreeCAD as App
    a = s / RADIUS
    n = App.Vector(math.cos(a), math.sin(a), 0)
    out = {}
    for name, shp in shapes.items():
        lines = []
        for w in shp.slice(n, 0.0):
            pts = w.discretize(Deflection=0.005)
            lines.append([[round(RADIUS - math.hypot(p.x, p.y), 4), round(p.z, 4)] for p in pts])
        out[name] = lines
    return out


# ---------- README ----------

def readme(j: Joint, checks: dict, parts: dict) -> str:
    box = {p["part"]: p["box_mm"] for p in checks["parts"]}
    fmt = lambda n: " x ".join(f"{v:g}" for v in box[n])
    st = ", ".join(f"{s:+.0f}" for s in stations(j))
    pair = {c["clearance"]: c for c in checks["pairs"]}
    dots = lambda n: f"{n} dot" + ("s" if n > 1 else "")
    pilot_text = lambda r: " / ".join(f"{p['pilot_d']:g}" for p in r["pilots"])
    lines = [
        "# Joint coupon",
        "",
        "`candybar.shell.coupon` writes this file. Do not edit it by hand. Rebuild:",
        "",
        "```sh",
        "CANDYBAR_OUT=cad/out/coupon cad/candybar/freecad-run.sh candybar.shell.coupon",
        "cad/.venv-tools/bin/python cad/tools/draw_coupon.py cad/out/coupon   # coupon.png and renders/",
        "```",
        "",
        "The coupon tests joint 1 of the seam proposal (`cad/out/shell-bp/split/proposal.md`, \"Joints\") before the cabinet is printed. "
        "The joint values are in `cad/candybar/shell/joints.py`. The tests and the pass rules are in "
        "`docs/research/petg-finishing.md`, section 4.",
        "",
        "## The parts",
        "",
        "| File (`stl/`, `step/`) | Part | Print box (mm) |",
        "| --- | --- | --- |",
    ]
    for c in CLEARANCES:
        lines.append(f"| `coupon-lower-{tag(c)}` | lower half, for the groove of +{c:.1f}. It has the key and the two pilot holes. {dots(round(c * 10))} inside. | {fmt(f'lower-{tag(c)}')} |")
        lines.append(f"| `coupon-upper-{tag(c)}` | upper half, groove clearance +{c:.1f} on each side. {dots(round(c * 10))} inside. | {fmt(f'upper-{tag(c)}')} |")
    for k in range(1, 5):
        lines.append(f"| `plaque-P{k}` | flat plaque for primer test P{k}. {dots(k)} on the back. | {fmt(f'plaque-P{k}')} |")
    lines += [
        "",
        f"`step/coupon-pair-{tag(ASSEMBLED_C)}-assembled.step` is one pair in the assembled position. `coupon.png` is the drawing. "
        "`renders/pair/` and `renders/apart/` hold renders of the pair and of the two halves apart. `checks.json` holds the checks.",
        "",
        f"The pair is a wall on a radius of {RADIUS:g} (convex outside). The seam is a level line along the arc. Each half is "
        f"{LENGTH:g} along the arc and {HALF:g} from the seam to its free edge, so the pair is {LENGTH:g} x {2 * HALF:g}. "
        f"Joint 1: skin {j.wall_t:g}; flange {j.flange_t:g} thick and {j.flange_h:g} high on each half, with a {j.gusset_angle:g} degree gusset; "
        f"key {j.key_proj:g} x {j.key_w:g} on the lower half, groove in the upper half; two screws {j.screw_d:g} x {j.screw_l:g} at a pitch of "
        f"{j.screw_pitch:g} (at {st} mm from the middle of the arc); V-groove {j.vgroove_w:g} wide and {j.vgroove_d:g} deep on the outside.",
        "",
        "The three pairs differ only in the groove of the upper half and in the dots. The key and the pilot holes are the same on all lower halves. "
        "The dots on the inside face give the clearance in tenths of a millimetre: one dot is +0.1, two dots +0.2, three dots +0.3. "
        "Keep the halves of one pair together.",
        "",
        "The plaque is 120 x 60 x 4, with a foot 8 x 4 on the back at the bed. A V notch in the top edge and a V line on the back, "
        "at 60 from each end, divide the two halves. The half with the code dots on the back (left when you look at the face) is the "
        "scuffed half (P320 wet and IPA). The other half gets the IPA wipe only.",
        "",
        "## Print orientation",
        "",
        "The STL files are in the print orientation. Do not turn them.",
        "",
        "- The halves print upright, as the wall pieces of the cabinet. The lower half stands for the piece below seam L1 "
        "(lower R or L, piece 5 or 6). It prints with the seam at its top, and the gusset carries its flange. It stands on a "
        "foot flange 12 x 4 at its free edge (joint 3). The upper half stands for the piece above L1 (middle R or L, piece 7 or 8). "
        "It prints with the seam on the bed.",
        "- The outer face is a wall in both halves. No support touches it. Do not add support.",
        "- The plaque prints upright on its long edge, so that its face has the layer lines of a wall piece.",
        "- Downward faces past 45 degrees from vertical, all in the upper half: (1) the ceiling of the groove, a bridge of 4.2 to 4.6 mm "
        "on the inside. The groove is 0.5 deeper than the key, so that a small sag of the bridge does not hold the flanges apart. "
        "(2) The half V-groove at the bed edge of the outer face: 0.8 deep over 0.5 high, two to three layers. It needs no support, "
        "and the filler fills it. The first-layer squish can close part of it: open it with a blade before the fit test. "
        "The dots are 90 degree cones: 45 degrees at the top, at the limit.",
        "- The note asks for one coupon with its outer face on the textured plate. A curved half does not lie flat on the bed. "
        "If you want that finish in the test, print one more plaque flat on the textured plate.",
        "",
        "## Slicer settings",
        "",
        "Use the profile of the real shell pieces. These settings must be the same as on the real pieces:",
        "",
        "| Setting | Value |",
        "| --- | --- |",
        "| Skin | Solid. Set enough wall loops to fill the 4 mm skin with walls (about 10 loops at a line width of 0.4 to 0.45), so that there is no infill in the skin, the flange or the gusset. |",
        "| Layer height | The value of the real pieces. The research note proposes 0.12 to 0.16 on curved show faces. Use one value for the coupon and the cabinet. |",
        "| Seam position | On the inside: paint the seam on the inner face or on the flange (seam painting), or use \"aligned\" and put it at an end of the arc on the inner side. Never on the outer face. |",
        "| Wall order | The order of the real pieces. |",
        "| Holes | No hole compensation for the pilot holes. The repeated-drive test checks the pilot holes as printed. |",
        "| Support | None. |",
        "| Brim | None on the outer edge. If a half lifts, add brim ears at the ends of the arc only. |",
        "",
        "Dry the filament before you print.",
        "",
        "## What to print",
        "",
        "### PETG (the plan)",
        "",
        "| Step | Print | Count | Use |",
        "| --- | --- | --- | --- |",
        "| 1 | `coupon-lower-c01` + `coupon-upper-c01`, `-c02` + `-c02`, `-c03` + `-c03` | 3 pairs | Fit test. Choose the clearance. Then the repeated-drive test on one pair. |",
        "| 2 | lower + upper halves of the chosen clearance | 4 pairs | Coupons A, B, C and D of the matrix (section 4.2): one bond each. Write the letter on the inside. |",
        "| 3 | `plaque-P1` to `plaque-P4` | 4 plaques | Primer tests P1 to P4 (section 4.2). |",
        "",
        "### ABS (an option)",
        "",
        "The ABS note (`docs/research/abs-switch.md`, summary and sections 7 and 10) allows these conditions only:",
        "",
        "- Print ABS on the A1 only as small parts, \"small-sized models with low infill densities\" (Bambu A1 FAQ). A 120 mm coupon is small.",
        "- Use the open frame, in a ventilated place, with no tent. Bambu does not recommend an enclosure for the A1.",
        "- Bambu says that ABS needs glue on the plate. The textured PEI plate needs no glue for ABS at a bed temperature of 90 to 100 C. Do not put acetone \"ABS juice\" on PEI.",
        "- The ABS set of the note: two coupons welded with acetone and two with slurry (one ABS and one ASA each), and two plaques. "
        "Put one coupon through the hobby-lacquer test over primer near a heat-set insert (stress cracking); the coupon has no boss for an insert, so put the insert into the flange. Use the tests and the pass rules of the PETG note.",
        "- Do not print ABS in a living area. Bambu says to avoid living areas and bedrooms.",
        "",
        "| Print | Count |",
        "| --- | --- |",
        "| Pairs at the chosen clearance (ABS, and ASA if you test it) | 2 ABS pairs, 2 ASA pairs |",
        "| `plaque-P1` and `plaque-P2` (or the two primers you test) | 2 |",
        "",
        "The PETG clearance can be different in ABS. If you continue with ABS, print the three fit pairs in ABS too.",
        "",
        "**Shrink of ABS.** Do not change the model. Set the shrink compensation in the filament profile of the slicer "
        "(OrcaSlicer: Filament, Shrinkage XY and Z). Measure the value on a calibration print in the same filament. "
        "As a guide, one study (ABS note, section 3.3) measured a shrink of 0.59 % in X and 0.69 % in Y, and a growth of 0.92 % in Z, for printed ABS. "
        "If your slicer has no shrink setting, scale the object in the slicer by the measured value.",
        "",
        "## Screws",
        "",
        f"Thread-forming screws for plastics, {j.screw_d:g} x {j.screw_l:g}, pan head, with the 30 degree thread of the PT type. Example: "
        "EJOT PT K 30x16 (WN 5411), or an equivalent \"screw for plastics\" of the same size. Do not use a sheet metal screw.",
        "",
        "- Two screws for each pair. The plan above needs 7 PETG pairs (14 screws), plus the screws of the repeated-drive test, "
        "plus 8 for the ABS option. Buy 50.",
        f"- Each lower half has two pilot holes. The hole at -30 is {j.pilot_d_pet:g} (the value for PET in the EJOT PT table, 0.75 d). "
        f"A sunk bar on the inside face, under the hole, marks it. The hole at +30 is {j.pilot_d_abs:g} (the value for ABS, 0.8 d). "
        "PETG is not in the table. The repeated-drive test chooses the value for the cabinet.",
        f"- A printed vertical hole comes out a little smaller than the model. Before the test, measure each pilot with the shank of a drill "
        f"(for example {j.pilot_d_pet - 0.15:.1f}, {j.pilot_d_pet - 0.05:.1f}, {j.pilot_d_abs - 0.1:.1f} and {j.pilot_d_abs:.1f}) and write down the largest shank that goes in.",
        f"- The driver: the screw head sits in a pocket {j.head_pocket_d:g} wide in the gusset of the upper half, "
        f"{j.screw_u - j.wall_t:g} from the inner face. Use a 1/4 inch hex bit at least 75 long, so that the handle clears the 60 mm wall.",
        "",
        "## Assembly",
        "",
        "1. Remove strings and the first-layer lip from the flange faces and the groove. Do not sand the key or the groove.",
        "2. Put the upper half on the lower half. The key goes into the groove. The outer faces must be flush.",
        "3. Put the two screws through the upper flange into the pilot holes. Tighten them by hand until the flange faces touch. Do not tighten more.",
        "4. For the bond tests, open the pair, put the adhesive on the flange faces, and put the same screws into the same holes again.",
        "",
        "## Tests",
        "",
        "**Fit test (step 1, dry, before any bond).** For each clearance:",
        "",
        "1. Put the halves together by hand without screws. Write down: does the key go in, how much force, is there play.",
        "2. Screw the pair. Write down the step at the V-groove between the two outer faces, with a feeler gauge or a straight edge.",
        "3. Choose the smallest clearance that goes together by hand with no force and has no play that you can feel.",
        "",
        "**Repeated-drive test (the cabinet needs this, the research note does not have it).** The cabinet is screwed together dry first, "
        "then opened and screwed again for the bond. Each pilot hole thus gets the same screw two or more times.",
        "",
        f"The test compares the two pilot holes: {j.pilot_d_pet:g} (under the bar, at -30) and {j.pilot_d_abs:g} (at +30). Do it in PETG. "
        "If the owner prints the ABS set, do it in ABS too.",
        "",
        "1. Use one pair of the fit set. Drive a screw into a pilot hole until the flanges touch, then 1/4 turn more.",
        "2. Remove the screw. Drive it into the same hole again.",
        "3. Do this 10 times in each of the two holes. Each time write down: does the screw tighten, does the head pull the flanges together, does the thread strip, does the flange crack.",
        "4. For each hole, write down the number of the first drive at which the thread does not hold. The cabinet needs 2 drives (dry assembly, then bond). A third good drive gives a margin for one correction.",
        f"5. Choose the pilot for the cabinet: the larger hole ({j.pilot_d_abs:g}) if it holds 3 drives, because it needs less torque and splits the flange less; "
        f"else the smaller hole ({j.pilot_d_pet:g}). Watch for a crack in the flange or the gusset with the smaller hole. Set `pilot_d` in `joints.py` to the value you choose. "
        "Until then `pilot_d` is open, and the part modelling cannot make a pilot hole.",
        "6. If neither hole holds 3 drives, make the pilots smaller in `joints.py`, print a new pair and do the test again.",
        "",
        "**Bond, fill, prime and paint tests.** Do the tests 1 to 6 of `docs/research/petg-finishing.md`, section 4.4, with the matrix of section 4.2 "
        "and the schedule of section 4.3. The pass rules and the decision rules are there. For the flex test (test 2), support the pair 100 apart "
        f"across the seam: the pair is {2 * HALF:g} across the seam.",
        "",
        "## Checks of the model",
        "",
        "| Clearance | Common volume (mm3) | Gap at the key sides (mm) | Gap at the key ends (mm) | Gap over the key (mm) | Flange contact (mm2) | Screw axes offset (mm) | Pilots at -30 / +30 (mm) | Pass |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for c in CLEARANCES:
        r = pair[c]
        lines.append(f"| +{c:.1f} | {r['common_volume_mm3']:g} | {r['key_gap_side_mm'][0]:.3f} to {r['key_gap_side_mm'][1]:.3f} | "
                     f"{r['key_gap_end_mm'][0]:.3f} to {r['key_gap_end_mm'][1]:.3f} | {r['key_gap_top_mm']:.3f} | {r['flange_contact_mm2']:.0f} | "
                     f"{r['screw_axis_offset_mm']:g} | {pilot_text(r)} | {'yes' if r['pass'] else 'NO'} |")
    lines += ["", "| Part | Valid | Print box (mm) | Fits the bed | Downward faces past 45 degrees | Pass |", "| --- | --- | --- | --- | --- | --- |"]
    for p in checks["parts"]:
        oh = "; ".join(f"{g['area_mm2']:g} mm2 at z {g['z']:g}: {g['exception'] or 'NOT STATED'}" for g in p["overhangs"]) or "none"
        lines.append(f"| {p['part']} | {'yes' if p['valid'] else 'NO'} | {' x '.join(f'{v:g}' for v in p['box_mm'])} | "
                     f"{'yes' if p['fits_bed'] else 'NO'} | {oh} | {'yes' if p['pass'] else 'NO'} |")
    lines += ["", f"Usable bed: {checks['printer']['xy']:g} x {checks['printer']['xy']:g}, {checks['printer']['z']:g} high (`cad/params/printer.csv`).",
              "", "Not proved by the model: that the gusset and the groove bridge print clean, the fit, the screw hold, the bond and the finish. Only the prints show these.", ""]
    return "\n".join(lines)


# ---------- main ----------

def main() -> int:
    import FreeCAD as App
    import MeshPart
    import Part

    out = Path(os.environ.get("CANDYBAR_OUT", CAD / "out" / "coupon")).resolve()
    if out == (CAD / "out").resolve():
        out = out / "coupon"
    for d in ("step", "stl", "assembled"):
        (out / d).mkdir(parents=True, exist_ok=True)
        for old in (out / d).glob("*.st[elp]*"):
            old.unlink()
    j, lim = JOINT, printer()
    print_parts: dict[str, object] = {}
    pairs, sections = [], {}
    lower_body = lower_half(0.1, j, holes=False)
    for c in CLEARANCES:
        lo, up = lower_half(c, j), upper_half(c, j)
        pairs.append(check_pair(j, c, lo, up, lower_body))
        r = pairs[-1]
        print(f"pair +{c:.1f}: common {r['common_volume_mm3']:g} mm3, key side gap {r['key_gap_side_mm']}, end gap {r['key_gap_end_mm']}, "
              f"over key {r['key_gap_top_mm']}, flange contact {r['flange_contact_mm2']} mm2, screw axes {r['screw_axis_offset_mm']} mm, "
              f"pilots {[(p['s'], p['pilot_d'], p['right_diameter']) for p in r['pilots']]}, "
              f"pilot break-out {r['pilot_breaks_out_mm3']} mm3 -> {'pass' if r['pass'] else 'FAIL'}")
        print_parts[f"lower-{tag(c)}"] = to_bed(lo)
        print_parts[f"upper-{tag(c)}"] = to_bed(up)
        if abs(c - ASSEMBLED_C) < 1e-9:
            Part.makeCompound([lo, up]).exportStep(str(out / "step" / f"coupon-pair-{tag(c)}-assembled.step"))
            for n, s in (("lower", lo), ("upper", up)):
                MeshPart.meshFromShape(Shape=s, LinearDeflection=MESH_LINEAR, AngularDeflection=MESH_ANGULAR, Relative=False).write(
                    str(out / "assembled" / f"{n}-{tag(c)}.stl"))
            sections = {"key": section({"lower": lo, "upper": up}, 0.0), "screw": section({"lower": lo, "upper": up}, stations(j)[0])}
    for k in range(1, 5):
        print_parts[f"plaque-P{k}"] = to_bed(plaque(k))
    parts = []
    for name, shp in print_parts.items():
        parts.append(check_part(j, name, shp, lim))
        r = parts[-1]
        print(f"{name}: valid {r['valid']}, box {r['box_mm']}, fits {r['fits_bed']}, overhangs "
              f"{[(g['z'], g['area_mm2'], g['exception'] is not None) for g in r['overhangs']]} -> {'pass' if r['pass'] else 'FAIL'}")
        stem = f"coupon-{name}" if not name.startswith("plaque") else name
        shp.exportStep(str(out / "step" / f"{stem}.step"))
        MeshPart.meshFromShape(Shape=shp, LinearDeflection=MESH_LINEAR, AngularDeflection=MESH_ANGULAR, Relative=False).write(
            str(out / "stl" / f"{stem}.stl"))
    checks = {"joint": asdict(j), "radius": RADIUS, "length": LENGTH, "half": HALF, "stations": stations(j), "pilots": pilots(j),
              "printer": asdict(lim), "overhang_limit_deg": OVERHANG_LIMIT, "pairs": pairs, "parts": parts}
    checks["pass"] = all(p["pass"] for p in pairs) and all(p["pass"] for p in parts)
    (out / "checks.json").write_text(json.dumps(checks, indent=1))
    (out / "drawing.json").write_text(json.dumps({"joint": asdict(j), "radius": RADIUS, "length": LENGTH, "half": HALF,
                                                  "stations": stations(j), "pilots": pilots(j), "clearance": ASSEMBLED_C, "sections": sections,
                                                  "flange_profile": flange_profile(j, "above")}))
    (out / "README.md").write_text(readme(j, checks, print_parts))
    print(f"coupon: {'all checks pass' if checks['pass'] else 'A CHECK FAILS'} -> {out}")
    return 0 if checks["pass"] else 1
