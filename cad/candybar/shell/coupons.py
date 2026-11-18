"""The coupon set: every small test print that the design rests on, as printable parts on plates.

    CANDYBAR_OUT=cad/out/coupons cad/candybar/freecad-run.sh candybar.shell.coupons
    CANDYBAR_OUT=cad/out/coupons cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc     # shell.FCStd
    cad/.venv-tools/bin/python cad/tools/draw_coupon.py cad/out/coupons --set                  # coupons.png, plates.png

docs/design/coupons.md is the sheet for the printer: what each coupon proves, what to measure, the value that passes
and what changes in the design when it fails. This module makes the parts and the numbers of that sheet.

The parts, each in its print orientation (z up, on the bed):
  shrink-x, shrink-y    two bars with three stops (0, half, full length), along X and along Y of the bed
  warp-wall, flat-strip a tall wall of the skin on its foot flange, and a long flat strip of the floor
  weld-lower, weld-upper   the section of joint 1 on a short straight seam, to weld with solvent and then break
  insert                M4 heat-set insert holes of three diameters, upright from the bed in the foot of the hood and
                        level in a flange on a wall
  holes-*               the button holes, the lever's mount, the hole of a 16 mm power button, the USB cut-outs
  cone-gauge, cone-plug the cone that locates a seam, in sockets of three clearances
  joint1-*              the pairs of joint 1 (candybar.shell.coupon): three clearances, and the plaques
  joint2-*, joint3-*, joint5-*   a pair for the floor lap, the wall foot on the floor and the service seam
  facet45, cut-in, hand-hold     cut from the real skin of the body (the cache of candybar.shell.split)
  edges-level, edges-upright     one bar with the edges of decision record 0007, in two print orientations
  floor-tile            a plate of the size of the smallest floor tile of the split, as the 10 mm sandwich
  latch-*               the first test piece of the control panel's latch (docs/design/control-panel-latch.md): a
                        strip of the deck nose with the button's hole (cut from the real skin), the middle of the
                        frame's front bar with the tunnel, the bolt, the gate and a strip of a tile with the strike;
                        and a strip of the rear bar with one notch and a strip of a tile's rear edge with one hook

Values. The joints come from candybar.shell.joints (JOINT, OTHER_JOINTS) and the form from dims.Blueprint. A value
that the concept does not have yet is derived from those or named here as PROPOSED, with its reason; the hand-over
lists them for the owner of joints.py. No joint value is set here a second time (tests/test_joints.py).

Outputs in CANDYBAR_OUT (default cad/out/coupons):
  brep/, stl/      one BREP and one STL of each part, in its print orientation with its box at the origin
  layout/          the same parts moved to their place on their plate (BREP), and manifest.json, edges.json for
                   candybar.shell.viewdoc (shell.FCStd) and tools/render_views.py
  sheet/           the parts spread on a grid with one camera each (focus.json), for the drawn sheet
  coupons.json     every part: size, plate, place, mass, time, checks; main() returns 1 when a check fails
  table.md         the generated columns of docs/design/coupons.md
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from dataclasses import dataclass, field
from pathlib import Path

from . import coupon as c1
from .dims import Blueprint
from .joints import JOINT, OTHER_JOINTS, Line, foot_profile, key_runs, screw_stations, seam_edge, skin_profile

CAD = Path(__file__).resolve().parents[2]
P3 = tuple[float, float, float]

# ---------- values that the concept does not have yet (PROPOSED: the hand-over lists them) ----------

# heat-set inserts (research of 2026-11-14): a printed hole comes out about 0.25 small, so the coupon has the hole
# of joints.OTHER_JOINTS and two larger ones; the insert is 8.1 long, so the hole is 9.5 deep and the boss 13
INSERT_PLUS = (0.0, 0.1, 0.2)
INSERT_DEPTH = 9.5
INSERT_BOSS = 13.0
INSERT_PITCH = 16.0
# the screws of joints 2 and 3 (3.5): the same shares of the screw diameter as joint 1 has for its 3.0 screw
SCREW_HEAD = 2.0            # a countersunk head: its diameter over the screw diameter
CONE_CLEARANCES = (0.05, 0.15, 0.25)
CONE_EXTRA = 0.3            # a socket is this much deeper than its cone
LAP_END_GAP = "groove_clearance"   # the end of a lap and the edge of the floor stand this far from the next part
BOSS_OVER_SCREW = 6.0       # joint 3: a block on the foot flange over each screw, so that the screw does not come out
M4_CLEAR = 4.4              # cad/params/controls.csv, panel_fix_d
PIN_IN_FRAME, PIN_IN_COVER = 5.5, 3.0
# the 16 mm power button: the thread is M16; three holes
POWER_HOLES = (16.0, 16.2, 16.4)
HOLE_PLUS = 0.3             # the second button hole of each size
# USB sockets (docs/research/pc-panel-and-front-usb.md, A5): cut-out as printed (w, h, corner radius), pocket behind
# the wall (w, h), flange holes each side of the socket centre
USB = {"A": ((15.1, 7.7, 1.8), (41.0, 15.0), 15.0), "C": ((10.9, 5.0, 2.2), (30.2, 10.7), 10.0)}
USB_WEB, USB_POCKET, USB_HOLE, USB_PITCH = 2.0, 3.0, 3.4, 38.0

# ---------- sizes of the coupons ----------

SHRINK_L, SHRINK_W, SHRINK_T, STOP_L, STOP_H = 230.0, 12.0, 3.0, 6.0, 8.0   # the two bars and the gap fill one plate
WARP = (180.0, 100.0)       # long, high
PAIR_L = 100.0              # joints 2, 3 and 5: along the seam
TILE_W = 25.0               # joints 2 and 3: the floor behind the joint
WALL_H = 40.0               # joint 3: the wall above the table
SERVICE = (110.0, 20.0)     # joint 5: long, high
EDGE_L = 60.0
# the boxes that cut the real skin (cabinet frame: x right, y to the rear, z up)
FACET_BOX = (5.0, 65.0, 500.0, 600.0, 281.0, 345.0)
CUT_IN_BOX = (200.0, 250.0, 496.0, 600.0, 138.0, 168.0)
HAND_HOLD_BOX = (135.0, 185.0, 500.0, 600.0, 372.0, 430.0)
TILE = "floor middle side R"

DENSITY = 1.05              # g/cm3, ABS (the owner chose ABS on 2026-11-14)
# the printer: a Qidi Q2. Its print size is 270 x 270 x 256 as width, depth, height (the maker's specification, read by
# the research of 2026-11-14). The limit of a piece is 250 x 250 on the bed and 250 high. The footprint in the model is
# PIECE_GROWTH less, because the slicer makes a piece larger to compensate the shrink. The plates use that footprint,
# which leaves BED_MARGIN at each side of the bed and TOP_MARGIN below the top (the margins are estimates)
BED = (270.0, 270.0, 256.0)
PIECE_XY, PIECE_Z, PIECE_GROWTH = 250.0, 250.0, 2.0
BED_MARGIN = (BED[0] - (PIECE_XY - PIECE_GROWTH)) / 2
TOP_MARGIN = BED[2] - PIECE_Z
FLAT = (PIECE_XY - PIECE_GROWTH, 40.0)   # the long flat strip of the floor: as long as the plate allows
WELD_L, WELD_HALF = 40.0, 30.0   # the weld pair: along the seam, from the seam to the free edge
RATE_CM3_H = 21.6           # 6 mm3/s on average, travel and small features included
PLATE_SETUP_H = 0.1
GAP = 5.0                   # between parts on a plate
MESH = (0.02, 0.1)


def bed() -> c1.Printer:
    """The part of the build volume that the plates use: the bed less its margins."""
    return c1.Printer(PIECE_XY - PIECE_GROWTH, PIECE_Z)


def floor_fill() -> float:
    """The printed share of the floor sandwich (structure.py: two skins on a gyroid core)."""
    from . import structure as st
    return (2 * st.FLOOR_SKIN + st.FLOOR_INFILL * (st.FLOOR_T - 2 * st.FLOOR_SKIN)) / st.FLOOR_T


def controls(params_dir: Path = CAD / "params") -> dict[str, float]:
    out = {}
    for r in csv.DictReader(open(params_dir / "controls.csv", encoding="utf-8")):
        try:
            out[r["name"]] = float(r["value"])
        except ValueError:
            pass
    return out


def base_screw() -> dict:
    """The holes for the 3.5 screw of joints 2 and 3, by the shares of joint 1 (rounded to 0.05)."""
    d = OTHER_JOINTS.base_screw_d
    r = lambda v: round(v * 20) / 20
    return {"d": d, "pilots": [r(d * JOINT.pilot_d_pet / JOINT.screw_d), r(d * JOINT.pilot_d_abs / JOINT.screw_d)],
            "clearance": r(d * JOINT.clearance_d / JOINT.screw_d), "head": d * SCREW_HEAD}


# ---------- small solids ----------

def V(*a):
    import FreeCAD as App
    return App.Vector(*a)


def box(x0, x1, y0, y1, z0, z1):
    import Part
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(d, at: P3, axis: P3, length):
    import Part
    return Part.makeCylinder(d / 2, length, V(*at), V(*axis))


def prism(poly_yz, x0, x1):
    """A section in (y, z), extruded along x."""
    import Part
    pts = [V(x0, y, z) for y, z in poly_yz]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(x1 - x0, 0, 0))


def fuse(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.removeSplitter()


def cut(body, tools):
    for t in tools:
        body = body.cut(t)
    return body.removeSplitter()


def dots(n: int, at: P3, into: P3, along: P3, pitch: float = 3.6):
    """n sunk marks (90 degree cones of DOT_D) in a face: `at` is on the face, `into` points into the part."""
    import Part
    lift, r = 0.2, c1.DOT_D / 2 + 0.2
    out = []
    for k in range(n):
        s = (k - (n - 1) / 2) * pitch
        base = V(*at) + V(*along) * s - V(*into) * lift
        out.append(Part.makeCone(r, 0.0, r, base, V(*into)))
    return out


def countersink(d_head, d_hole, at: P3, axis: P3):
    """A 90 degree countersink that opens at `at` and narrows along `axis`."""
    import Part
    e = 0.01
    return Part.makeCone(d_head / 2 + e, d_hole / 2, (d_head - d_hole) / 2 + e, V(*at) - V(*axis) * e, V(*axis))


def cone(clearance: float = 0.0, extra: float = 0.0, at: P3 = (0, 0, 0), axis: P3 = (0, 0, 1)):
    """The cone of OTHER_JOINTS (flanks of 45 degrees). With a clearance it is the socket: the gap is measured square
    to the flank, and the socket is `extra` deeper."""
    import Part
    o = OTHER_JOINTS
    r0 = o.cone_d / 2 + clearance * math.sqrt(2)
    h = o.cone_h + extra
    e = 0.01 if clearance else 0.0
    return Part.makeCone(r0 + e, r0 - h, h + e, V(*at) - V(*axis) * e, V(*axis))


def edges_on(shape, pred):
    return [e for e in shape.Edges if pred(e)]


def turned(shape, axis: P3, deg: float):
    s = shape.copy()
    s.rotate(V(0, 0, 0), V(*axis), deg)
    return s


def tight_box(shape):
    """The box of the solid itself. Shape.BoundBox reaches to the poles of a B-spline face, which stand outside a cut
    from the real skin."""
    return shape.optimalBoundingBox(False, False)


WELD = 0.001   # mm: the points of an STL that are nearer than this are one point


def closed_mesh(shape):
    """The STL mesh of a part, closed. The mesh of the cut-in (a cut of the real skin) has 24 open edges, each 0.004
    long, where two slabs of the cavity meet; its points within WELD are made one point, and the mesh is closed."""
    import Mesh
    import MeshPart
    m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=MESH[0], AngularDeflection=MESH[1], Relative=False)
    if m.isSolid():
        return m
    pts, fac = m.Topology
    key, at, idx = {}, [], []
    for p in pts:
        k = (round(p.x / WELD), round(p.y / WELD), round(p.z / WELD))
        if k not in key:
            key[k] = len(at)
            at.append(p)
        idx.append(key[k])
    welded = Mesh.Mesh([[at[idx[a]], at[idx[b]], at[idx[c]]] for a, b, c in fac if len({idx[a], idx[b], idx[c]}) == 3])
    welded.removeDuplicatedPoints()
    welded.removeDuplicatedFacets()
    return welded


def to_bed(shape):
    """Move a part that is already in its print orientation so that its box starts at the origin. With OpenCascade
    7.9.3 a plain translation of the cuts of the real skin (cut-in, hand-hold) is not a valid shape, although the cut
    is, and ShapeFix does not mend it; transformGeometry moves them as valid shapes (the volume changes by less than
    0.05 mm3). It is used only when the translation is not valid."""
    b = tight_box(shape)
    return moved(shape, V(-b.XMin, -b.YMin, -b.ZMin))


def moved(shape, by):
    """The shape moved by the vector `by`: a translation, or transformGeometry when the translation is not valid
    (see to_bed), or the translation mended (Shape.fix) when neither is valid. The cut of hand-hold from the skin of
    2026-11-15 needs the third way: both moves leave a face that is not orientable, and the fix mends it."""
    out = shape.translated(by)
    if out.isValid() or not shape.isValid():
        return out
    import FreeCAD as App
    m = App.Matrix()
    m.move(by)
    moved_ = shape.transformGeometry(m)
    if moved_.isValid():
        return moved_
    out = out.copy()          # a mend in place on the translated shape does nothing; on a copy it works
    out.fix(1e-7, 1e-7, 1e-7)
    return out


# ---------- shrink and warp ----------

def shrink_bar(marks: int):
    """A bar along X with three stops. Measure over the outer faces of the stops: half and full length."""
    half = SHRINK_L / 2
    stops = [(0.0, STOP_L), (half - STOP_L, half), (SHRINK_L - STOP_L, SHRINK_L)]
    body = fuse([box(0, SHRINK_L, 0, SHRINK_W, 0, SHRINK_T)] + [box(a, b, 0, SHRINK_W, SHRINK_T - 0.5, STOP_H) for a, b in stops])
    return cut(body, dots(marks, (STOP_L / 2, SHRINK_W / 2, STOP_H), (0, 0, -1), (0, 1, 0)))


def wall_on_foot(length: float, height: float):
    """A wall of the skin, outer face at y = 0, on the foot flange of joint 3."""
    j = JOINT
    return fuse([box(0, length, 0, j.wall_t, 0, height), box(0, length, j.wall_t - 0.5, j.wall_t + j.foot_h, 0, j.foot_t)])


def warp_wall():
    return wall_on_foot(*WARP)


def flat_strip():
    """A strip of the floor (the sandwich of structure.FLOOR_T), flat on the bed, with sharp corners as the floor
    tiles have: the corners show the lift."""
    from . import structure as st
    return box(0, FLAT[0], 0, FLAT[1], 0, st.FLOOR_T)


# ---------- the weld pair: the section of joint 1 on a short straight seam ----------

def weld_path() -> Line:
    return Line(-WELD_L / 2, WELD_L / 2)


def weld_lower():
    """The piece below the seam: flange, gusset, key, one pilot hole of the ABS value, on the foot flange."""
    j, p = JOINT, weld_path()
    add, tool = seam_edge(j, p, "below", [0.0], pilots=[j.pilot_d_abs])
    return cut(fuse([p.sweep(skin_profile(j, "below", WELD_HALF)), add, p.sweep(foot_profile(j, WELD_HALF))]), [tool])


def weld_upper():
    """The piece above the seam: flange, gusset, groove (the clearance of the joint), one clearance hole."""
    j, p = JOINT, weld_path()
    add, tool = seam_edge(j, p, "above", [0.0])
    return cut(fuse([p.sweep(skin_profile(j, "above", WELD_HALF)), add]), [tool])


# ---------- inserts and holes ----------

def insert_holes() -> list[float]:
    return [round(OTHER_JOINTS.insert_hole_d + p, 2) for p in INSERT_PLUS]


def insert_coupon():
    """A wall of the skin, standing, with the foot of the hood at the bed (joint 7, the bolted hood of 2026-11-16: the
    foot flange on the bed with three bosses of 13 x hood_boss_h, the holes from the bed upward, as the hood side
    prints) and at its top a thick flange on a 45 degree gusset (holes with a level axis, as in the frame of the rear
    door)."""
    o, w = OTHER_JOINTS, JOINT.wall_t
    n = len(INSERT_PLUS)
    length = (n - 1) * INSERT_PITCH + 18.0
    xs = [9.0 + k * INSERT_PITCH for k in range(n)]
    foot_h = INSERT_BOSS + 3.0
    top = foot_h + 3.5 + o.ring_w + INSERT_BOSS
    t, rw = o.hood_foot_t, o.ring_w
    foot = prism([(w - 0.5, 0.0), (w + rw, 0.0), (w + rw, t), (w, t + rw), (w - 0.5, t + rw)], 0, length)
    bosses = [cyl(o.service_boss, (x, w + rw / 2, 0.0), (0, 0, 1), o.hood_boss_h) for x in xs]
    block = prism([(w - 0.5, top), (INSERT_BOSS, top), (INSERT_BOSS, top - foot_h), (w, top - foot_h - (INSERT_BOSS - w)),
                   (w - 0.5, top - foot_h - (INSERT_BOSS - w))], 0, length)
    body = fuse([box(0, length, 0, w, 0, top), foot, block, *bosses])
    tools = []
    for k, (x, d) in enumerate(zip(xs, insert_holes())):
        tools.append(cyl(d, (x, w + rw / 2, -0.01), (0, 0, 1), INSERT_DEPTH + 0.01))
        tools.append(cyl(d, (x, INSERT_BOSS + 0.01, top - foot_h / 2), (0, -1, 0), INSERT_DEPTH + 0.01))
        tools += dots(k + 1, (x, w / 2, top), (0, 0, -1), (1, 0, 0))
    return cut(body, tools)


def button_plate(v: dict | None = None):
    """The printed panel plate (dims.panel_t) with two holes for the 30 mm button and two for the 24 mm button: the
    drawn size and HOLE_PLUS more (one dot)."""
    v = v or controls()
    t = Blueprint().panel_t
    holes, x = [], 6.0
    for d in (v["btn_hole_d"], v["svc_hole_d"]):
        for plus in (0.0, HOLE_PLUS):
            x += d / 2
            holes.append((x, d + plus, plus))
            x += d / 2 + 9.0
        x -= 2.0
    width = v["btn_hole_d"] + 12.0
    body = box(0, x - 1.0, 0, width, 0, t)
    tools = [cyl(d, (cx, width / 2, -0.01), (0, 0, 1), t + 0.02) for cx, d, _ in holes]
    tools += [m for cx, d, plus in holes if plus for m in dots(1, (cx, width / 2 - d / 2 - 3.0, t), (0, 0, -1), (1, 0, 0))]
    return cut(body, tools)


def lever_plate(v: dict | None = None):
    """The lever's mount: the shaft hole and the four bosses with insert holes, on the printed panel plate. The panel
    top is on the bed."""
    v = v or controls()
    t = Blueprint().panel_t
    hw, hl = v["stick_plate_w"] / 2 + 5.0, v["stick_plate_l"] / 2 + 5.0
    drop = v["stick_plate_drop"]
    spots = [(sx * v["stick_mount_w"] / 2, sy * v["stick_mount_l"] / 2) for sx in (-1, 1) for sy in (-1, 1)]
    body = fuse([box(-hw, hw, -hl, hl, 0, t)] + [cyl(v["stick_boss_d"], (x, y, t - 0.5), (0, 0, 1), drop - t + 0.5) for x, y in spots])
    tools = [cyl(v["stick_shaft_hole_d"], (0, 0, -0.01), (0, 0, 1), t + 0.02)]
    tools += [cyl(v["stick_insert_d"], (x, y, drop + 0.01), (0, 0, -1), v["stick_insert_depth"] + 0.01) for x, y in spots]
    return cut(body, tools)


def power_wall():
    """Three holes for a 16 mm button in a wall of the skin, printed upright (the hole axis is level)."""
    pitch, height, zc = 28.0, 32.0, 19.0
    length = pitch * len(POWER_HOLES)
    body = wall_on_foot(length, height)
    tools = []
    for k, d in enumerate(POWER_HOLES):
        x = pitch / 2 + k * pitch
        tools.append(cyl(d, (x, -0.01, zc), (0, 1, 0), JOINT.wall_t + 0.02))
        tools += dots(k + 1, (x, JOINT.wall_t / 2, height), (0, 0, -1), (1, 0, 0))
    return cut(body, tools)


def rounded_slot(w, h, r, at: P3, depth):
    """A cut-out w x h with corner radius r, centred on `at`, cut along +z."""
    b = box(at[0] - w / 2, at[0] + w / 2, at[1] - h / 2, at[1] + h / 2, at[2], at[2] + depth)
    return b.makeFillet(r, edges_on(b, lambda e: abs(e.tangentAt(e.FirstParameter).z) > 0.99))


def usb_plate():
    """The socket plate: one USB-A and one USB-C cut-out in the web, with the pockets behind it and the flange holes.
    The outer face is on the bed."""
    t = USB_WEB + USB_POCKET
    length, width = 86.0, 25.0
    xs = {"A": 26.0, "C": 26.0 + USB_PITCH}
    tools = []
    for kind, ((w, h, r), (pw, ph), hole) in USB.items():
        x = xs[kind]
        tools.append(rounded_slot(w, h, r, (x, width / 2, -0.01), USB_WEB + 0.02))
        tools.append(box(x - pw / 2, x + pw / 2, width / 2 - ph / 2, width / 2 + ph / 2, USB_WEB, t + 0.01))
        tools += [cyl(USB_HOLE, (x + s * hole, width / 2, -0.01), (0, 0, 1), USB_WEB + 0.02) for s in (-1, 1)]
    return cut(box(0, length, 0, width, 0, t), tools)


# ---------- the cone ----------

def cone_gauge():
    """A plate with three sockets, clearance CONE_CLEARANCES; one, two and three dots."""
    t, w, pitch = 6.0, 14.0, 15.0
    tools = []
    for k, c in enumerate(CONE_CLEARANCES):
        x = 7.0 + k * pitch
        tools.append(cone(c, CONE_EXTRA, (x, w / 2, t), (0, 0, -1)))
        tools += dots(k + 1, (x + pitch / 2, w / 2, t), (0, 0, -1), (0, 1, 0))
    return cut(box(0, 7.0 + len(CONE_CLEARANCES) * pitch, 0, w, 0, t), tools)


def cone_plug():
    t, w = 6.0, 14.0
    return fuse([box(0, w, 0, w, 0, t), cone(at=(w / 2, w / 2, t - 0.001))])


# ---------- the push rod of the monitor's button (cradle.button_option) ----------

ROD_HOLES = (-0.1, 0.0, 0.1)   # the holes of the block: the hole of the plate (rod + 2 x rod_fit) and 0.1 less and more


def rod_block():
    """A block of the inner frame of the bezel plate, as thick as the frame at the rod's hole (the length of the rod's
    run through the plate), with three square holes for the rod: the hole of the plate and 0.1 smaller and larger. It
    prints as the plate does: its face on the bed."""
    from . import cradle as cr
    c = cr.Cradle()
    t, w, pitch = 16.0, 12.0, 12.0
    holes = [c.rod + 2 * c.rod_fit + k for k in ROD_HOLES]
    block = box(0, pitch * len(holes), 0, w, 0, t)
    return block.cut([box(pitch * (i + 0.5) - a / 2, pitch * (i + 0.5) + a / 2, w / 2 - a / 2, w / 2 + a / 2, -1, t + 1) for i, a in enumerate(holes)])


def rod_piece():
    """The rod of 4 x 4 with its small break at the tip, 40 long: it prints standing on its tip, as the real rod."""
    import Part
    from . import cradle as cr
    c = cr.Cradle()
    rod = box(0, c.rod, 0, c.rod, 0, 40.0)
    tip = [e for e in rod.Edges if all(v.Point.z < 1e-6 for v in e.Vertexes)]
    try:
        return rod.makeFillet(c.small_break, tip)
    except Part.OCCError:
        return rod.makeChamfer(c.small_break, tip)


# ---------- the latch of the control panel: the first test piece (panel_frame, PUSH_BOLT) ----------

LATCH_W = 60.0      # the strips are this wide, on the centre line (the latch document's test piece)


def latch_build():
    """The control panel as built (panel_frame.build), once for the four parts of the latch."""
    from . import panel_frame as pf
    global _LATCH
    try:
        return _LATCH
    except NameError:
        _LATCH = pf.build()
        return _LATCH


def latch_nose_box() -> tuple:
    """The strip of the deck nose: LATCH_W wide on the centre line, from the front face to the front of the ledge's
    room, and from below the button's hole to above the deck top."""
    from . import panel_frame as pf
    d = Blueprint()
    return (-LATCH_W / 2, LATCH_W / 2, -3.0, pf.y0(d) + 18.0, d.latch_button_z - d.latch_button_d / 2 - 6.0, d.deck_top + 1.0)


def latch_nose():
    """The deck nose round the button's hole, cut from the real skin: its front wall with the hole and its rim break,
    the deck top and the ledge of the pocket, under which the frame strip bonds. As the cabinet stands, on its lower
    cut."""
    return skin_piece("latch-nose", latch_nose_box())


def latch_frame():
    """The middle of the left half of the frame (it ends at the frame's seam at x 20): the front bar with the notch
    of the bolt and the tunnel with its floor, walls, roof and the slot of the gate. As the frame prints."""
    from . import panel_frame as pf
    b = latch_build()
    p = b.i.push
    keep = box(-LATCH_W / 2, p.frame_split_x, -50.0, p.housing_y[1] + 2.0, 0.0, 200.0)
    return pf.one_solid(b.frame["frame_left"].common(keep).removeSplitter(), "latch frame strip")


def latch_bolt():
    """The bolt, on its side (the flat side x -6 on the bed)."""
    return turned(latch_build().latch["latch_bolt"], (0, 1, 0), -90)


def latch_gate():
    """The gate, flat: its rear face on the bed, the peg up."""
    return turned(latch_build().latch["latch_gate"], (1, 0, 0), -90)


def latch_strike():
    """A strip of the button tile with the strike: LATCH_W wide on the centre line, the front of the plate with the
    stub of the front rib each side of the bolt's room. Top face down, as the tiles print."""
    from . import panel_frame as pf
    b = latch_build()
    d = b.d
    keep = box(-LATCH_W / 2, LATCH_W / 2, pf.y0(d) - 1.0, pf.y0(d) + 32.0, 0.0, 200.0)
    tile = next(t for t in b.arcade.values() if t.BoundBox.XMin < 0 < t.BoundBox.XMax)
    return turned(pf.one_solid(tile.common(keep).removeSplitter(), "latch strike strip"), (1, 0, 0), 180)


# the strips of the rear hook: from x 82 to x 113, round the hook at x +100 (PushBolt.hook_x). The pad of the cone at
# x 120 starts at x 108; the strips stop before the cone and its slot
HOOK_STRIP = (82.0, 113.0)


def latch_notch():
    """A strip of the rear bar of the right half of the frame with the notch of the hook at x +100: the bar, its
    notch and a part of the pad of the cone at x 120. As the frame prints: the lower face of the bar on the bed."""
    from . import panel_frame as pf
    b = latch_build()
    rear = pf.rear_bar_face(b.d, b.i)
    keep = box(*HOOK_STRIP, rear - 6.0, rear + 30.0, 0.0, 200.0)
    return pf.one_solid(b.frame["frame_right"].common(keep).removeSplitter(), "latch notch strip")


def latch_hook():
    """A strip of the rear edge of the button tile with the hook at x +100: the plate, the rear rib and the hook.
    Top face down, as the tiles print."""
    from . import panel_frame as pf
    b = latch_build()
    d = b.d
    keep = box(*HOOK_STRIP, pf.y0(d) + b.i.rib_rear_yl - 4.0, pf.y0(d) + d.panel_d + 5.0, 0.0, 200.0)
    tile = next(t for t in b.arcade.values() if t.BoundBox.XMin < 100.0 < t.BoundBox.XMax)
    return turned(pf.one_solid(tile.common(keep).removeSplitter(), "latch hook strip"), (1, 0, 0), 180)


# ---------- joint 2: floor tile to floor tile (assembled: seam along x, z up from the table) ----------

def lap_stations() -> list[float]:
    return screw_stations(Line(-PAIR_L / 2, PAIR_L / 2), OTHER_JOINTS.lap_screw_pitch)


def lap_cones() -> list[float]:
    return [-PAIR_L / 2 + 10.0, PAIR_L / 2 - 10.0]


def joint2_lower():
    from . import structure as st
    o, t, h, s = OTHER_JOINTS, st.FLOOR_T, PAIR_L / 2, base_screw()
    half, gap = o.lap_w / 2, getattr(JOINT, LAP_END_GAP)
    body = fuse([box(-h, h, -half - TILE_W, -half, 0, t), box(-h, h, -half - 0.5, half - gap, 0, t / 2)]
                + [cone(at=(x, 0, t / 2 - 0.001)) for x in lap_cones()])
    tools = []
    for x in lap_stations():
        tools.append(cyl(s["clearance"], (x, 0, -0.01), (0, 0, 1), t / 2 + 0.02))
        tools.append(countersink(s["head"], s["clearance"], (x, 0, 0), (0, 0, 1)))
    return cut(body, tools)


def joint2_upper():
    from . import structure as st
    o, t, h, s = OTHER_JOINTS, st.FLOOR_T, PAIR_L / 2, base_screw()
    half, gap = o.lap_w / 2, getattr(JOINT, LAP_END_GAP)
    body = fuse([box(-h, h, half, half + TILE_W, 0, t), box(-h, h, -half + gap, half + 0.5, t / 2, t)])
    tools = [cone(o.cone_clearance, CONE_EXTRA, (x, 0, t / 2), (0, 0, 1)) for x in lap_cones()]
    tools += [cyl(d, (x, 0, t / 2 - 0.01), (0, 0, 1), t / 2 + 0.02) for x, d in zip(lap_stations(), s["pilots"], strict=True)]
    tools += dots(1, (lap_stations()[0], half + TILE_W / 2, t), (0, 0, -1), (1, 0, 0))
    return cut(body, tools)


# ---------- joint 3: wall foot on the floor (assembled: wall outer face y = 0, inward +y, z up from the table) ----------

def foot_stations() -> list[float]:
    return [-PAIR_L / 2 + 10.0, PAIR_L / 2 - 10.0]


def foot_key_runs() -> list[tuple[float, float]]:
    return key_runs(JOINT, Line(-PAIR_L / 2, PAIR_L / 2), foot_stations())


def foot_key_y() -> tuple[float, float]:
    mid = JOINT.wall_t + JOINT.foot_h / 2
    return mid - OTHER_JOINTS.foot_key_w / 2, mid + OTHER_JOINTS.foot_key_w / 2


def joint3_wall():
    """The lower edge of a wall piece: the skin down to the table, the foot flange on the floor with the key under
    it, and a block over each screw. Upright, as the lower pieces print: the foot flange is a level overhang."""
    from . import structure as st
    j, o, t, h, s = JOINT, OTHER_JOINTS, st.FLOOR_T, PAIR_L / 2, base_screw()
    y0, y1 = foot_key_y()
    mid = j.wall_t + j.foot_h / 2
    parts = [box(-h, h, 0, j.wall_t, 0, WALL_H), box(-h, h, j.wall_t - 0.5, j.wall_t + j.foot_h, t, t + j.foot_t)]
    parts += [box(a, b, y0, y1, t - o.foot_key_h, t + 0.2) for a, b in foot_key_runs()]
    parts += [box(x - 5, x + 5, j.wall_t - 0.5, j.wall_t + j.foot_h, t + j.foot_t - 0.2, t + j.foot_t + BOSS_OVER_SCREW) for x in foot_stations()]
    tools = [cyl(d, (x, mid, t - 0.01), (0, 0, 1), foot_pilot_depth() + 0.01) for x, d in zip(foot_stations(), s["pilots"], strict=True)]
    tools += dots(1, (foot_stations()[0], mid, t + j.foot_t + BOSS_OVER_SCREW), (0, 0, -1), (1, 0, 0))
    return cut(fuse(parts), tools)


def foot_pilot_depth() -> float:
    """From the floor top into the foot flange: the screw of OTHER_JOINTS, flush under the floor, plus 1."""
    from . import structure as st
    return OTHER_JOINTS.foot_screw_l - st.FLOOR_T + 1.0


def joint3_floor():
    from . import structure as st
    j, o, t, h, s = JOINT, OTHER_JOINTS, st.FLOOR_T, PAIR_L / 2, base_screw()
    c = j.groove_clearance
    y0, y1 = foot_key_y()
    mid = j.wall_t + j.foot_h / 2
    tools = [box(a - c, b + c, y0 - c, y1 + c, t - o.foot_key_h - j.groove_extra_depth, t + 0.01) for a, b in foot_key_runs()]
    for x in foot_stations():
        tools.append(cyl(s["clearance"], (x, mid, -0.01), (0, 0, 1), t + 0.02))
        tools.append(countersink(s["head"], s["clearance"], (x, mid, 0), (0, 0, 1)))
    return cut(box(-h, h, j.wall_t + c, j.wall_t + c + j.foot_h + TILE_W, 0, t), tools)


# ---------- joint 5: service seam (assembled: seat plane y = 0, the fixed frame toward +y, the cover toward -y) ----------

def service_stations() -> list[float]:
    return [-OTHER_JOINTS.service_pitch_min / 2, OTHER_JOINTS.service_pitch_min / 2]


def service_pins() -> list[float]:
    return [-22.0, 22.0]


def _chamfered(body, y: float):
    """The chamfer of the service seam on the four edges of the face at y."""
    es = edges_on(body, lambda e: all(abs(v.Point.y - y) < 1e-6 for v in e.Vertexes))
    return body.makeChamfer(OTHER_JOINTS.service_chamfer, es)


def joint5_frame():
    """The fixed part: a flange INSERT_BOSS thick with two insert holes and two pin holes in its seat face. Upright,
    as the frame of the rear door prints: the holes are level."""
    o, (length, height) = OTHER_JOINTS, SERVICE
    body = _chamfered(box(-length / 2, length / 2, 0, INSERT_BOSS, 0, height), 0.0)
    tools = [cyl(o.insert_hole_d, (x, -0.01, height / 2), (0, 1, 0), INSERT_DEPTH + 0.01) for x in service_stations()]
    tools += [cyl(o.pin_d, (x, -0.01, height / 2), (0, 1, 0), PIN_IN_FRAME + 0.01) for x in service_pins()]
    return cut(body, tools)


def joint5_cover():
    """The cover (a strip of the rear door): clearance holes for the M4 screws, one round and one long pin hole."""
    o, (length, height), w = OTHER_JOINTS, SERVICE, JOINT.wall_t
    body = _chamfered(box(-length / 2, length / 2, -w, 0, 0, height), -w)
    d = o.pin_d + 2 * o.pin_clearance
    pin = lambda x: cyl(d, (x, 0.01, height / 2), (0, -1, 0), PIN_IN_COVER + 0.01)
    a, b = service_pins()
    slot = fuse([pin(b - 0.5), pin(b + 0.5), box(b - 0.5, b + 0.5, -PIN_IN_COVER, 0.01, height / 2 - d / 2, height / 2 + d / 2)])
    tools = [cyl(M4_CLEAR, (x, 0.01, height / 2), (0, -1, 0), w + 0.02) for x in service_stations()] + [pin(a), slot]
    return cut(body, tools)


# ---------- the edges of decision record 0007 ----------

EDGE_SECTION = [(6.0, 0.0), (30.0, 0.0), (30.0, 10.0), (22.0, 18.0), (22.0, 24.0), (0.0, 24.0), (0.0, 16.0), (6.0, 10.0)]
# (y, z) of an edge of the section -> what it is
EDGE_NAMES = {(0.0, 24.0): "sharp edge of 90 degrees (the control: paint goes thin here)",
              (22.0, 24.0): "edge of 90 degrees with the edge break",
              (30.0, 10.0): "45 degree lip with the edge break (as the band's edge and the base facet)",
              (0.0, 16.0): "round of the rear design on a 45 degree turn, over a facet that faces down 45 degrees (as the top of the rear shelf)",
              (22.0, 18.0): "inside crease, open to the top",
              (6.0, 10.0): "inside crease under a 45 degree facet (as the crease of the rear shelf)"}


def edge_bar():
    """One bar with the edges of the form, lying as the rear shelf prints (the edges are level)."""
    d = Blueprint()
    body = prism(EDGE_SECTION, 0, EDGE_L)
    at = lambda y, z: edges_on(body, lambda e: all(abs(v.Point.y - y) < 1e-6 and abs(v.Point.z - z) < 1e-6 for v in e.Vertexes))
    body = body.makeFillet(d.rear_round_r, at(0.0, 16.0))
    at = lambda y, z: edges_on(body, lambda e: all(abs(v.Point.y - y) < 1e-6 and abs(v.Point.z - z) < 1e-6 for v in e.Vertexes))
    return body.makeFillet(d.edge_break, at(22.0, 24.0) + at(30.0, 10.0))


# the coupons that test the edge finish and the 45 degree faces of the cabinet (plate 6): the edge rule holds on them.
# The others are test prints: of a fit, a hole, a weld, the shrink, or of the weld, the filler and the paint on a face
# (the finish pairs and the plaques), whose own edges are those of a test piece
PAINTED = ("facet45", "cut-in", "hand-hold", "edges")
# the boxes that cut the real skin, by coupon
CUT_BOXES = {"facet45": FACET_BOX, "cut-in": CUT_IN_BOX, "hand-hold": HAND_HOLD_BOX}
# the coupons whose sharp edge is the control of the paint test (EDGE_NAMES)
CONTROL = ("edges-level", "edges-upright")


def bar_frame(name: str, shape):
    """A shape in the frame of the edge bar (the section in y, z, along x 0 to EDGE_L) moved into the frame of the
    coupon `name` (stl/, brep/), as the bar is."""
    bar = edge_bar()
    if name == "edges-upright":
        shape, bar = turned(shape, (0, 1, 0), -90), turned(bar, (0, 1, 0), -90)
    b = tight_box(bar)
    return shape.translated(V(-b.XMin, -b.YMin, -b.ZMin))


def untested(name: str):
    """What lies outside the faces that the paint test of an edge bar looks at: beyond its two ends and below its bed
    face. A sharp edge there is an edge of the test piece, not one of the six edges of EDGE_NAMES."""
    import Part
    big = box(-100.0, EDGE_L + 100.0, -100.0, 130.0, -100.0, 124.0)
    return bar_frame(name, big.cut(box(0.01, EDGE_L - 0.01, -1.0, 31.0, 0.01, 25.0)))


def control_edge(name: str):
    """The sharp edge of 90 degrees that the paint test keeps as its control, in the frame of the coupon (stl/, brep/)."""
    import Part
    return bar_frame(name, Part.makeLine(V(0, 0, 24.0), V(EDGE_L, 0, 24.0)))


# ---------- cut from the real skin ----------

def skin_cache() -> Path:
    return CAD / "out" / "coupons" / "cache"


def skin(module: str):
    """The hollow skin of a module from the cache of the split (it is made by candybar.shell.split, 18 minutes)."""
    import Part
    from . import split
    f = split.skin_files(Blueprint())[module]
    if not f.exists():
        raise FileNotFoundError(f"the skin of the {module} is not in the cache ({f}): run candybar.shell.split, or copy the cache")
    s = Part.Shape()
    s.importBinary(str(f))
    return s


def skin_piece(name: str, bounds: tuple):
    """The skin of the body inside a box, kept beside the build under the fingerprint of the skin and the box."""
    import Part
    from . import split
    key = hashlib.sha256(repr((split.fingerprint(Blueprint()), bounds)).encode()).hexdigest()[:12]
    f = skin_cache() / f"{name}-{key}.bin"
    if f.exists():
        s = Part.Shape()
        s.importBinary(str(f))
        return s
    s = skin("body").common(box(*bounds))
    if len(s.Solids) != 1 or not s.isValid():
        raise RuntimeError(f"{name}: the cut of the skin is not one valid solid ({len(s.Solids)} solids, valid {s.isValid()})")
    f.parent.mkdir(parents=True, exist_ok=True)
    s.exportBinary(str(f))
    return s


def facet45():
    """A length of the upper rear piece: the frame above the door, the crease of the rear shelf, the rear facet (45
    degrees), its round and the foot of the upper rear wall. A foot flange inside at the bed stands for the flange
    of the door frame."""
    d, j = Blueprint(), JOINT
    x0, x1, _, _, z0, _ = FACET_BOX
    inner = d.body_d - d.wall_t
    return fuse([skin_piece("facet45", FACET_BOX), box(x0, x1, inner - j.foot_h, inner + 0.5, z0, z0 + j.foot_t)])


def cut_in():
    """The right lower rear corner of the body with the second cut-in, whole, and 10 mm of wall under and over it."""
    return skin_piece("cut-in", CUT_IN_BOX)


def hand_hold():
    """The outer end of the right hand-hold: its rim, its roof (45 degrees), the wall over the rim and the body top."""
    return skin_piece("hand-hold", HAND_HOLD_BOX)


def tile_size() -> tuple[float, float]:
    """The plan box of the smallest floor tile of the split (TILE), cut from the floor of the cached skin."""
    import Part
    from . import split
    f = skin_cache() / f"floor-tile-{split.fingerprint(Blueprint())}.json"
    if f.exists():
        return tuple(json.loads(f.read_text()))
    seams, pieces = split.expanded(split.layout(Blueprint()))
    base = [p for p in pieces if p.module == "base"]
    shapes, problems = split.cut([s for s in seams if s.module == "base"], base, split.Modules({"base": skin("base")}, {}, {}, ""))
    if [p for p in problems if p["problem"] != "debris"]:
        raise RuntimeError(f"floor tile: the cut of the floor has problems: {problems}")
    b = tight_box(shapes[TILE])
    size = (round(b.XLength, 1), round(b.YLength, 1))
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(size))
    return size


def floor_tile():
    """A plate of the size of the smallest floor tile of the split, as the sandwich of structure.FLOOR_T. The laps of
    joint 2 are not on the tiles of the split yet and the outline of the tile in the skin is stepped, so the coupon
    is the plain rectangle."""
    from . import structure as st
    w, h = tile_size()
    return box(0, w, 0, h, 0, st.FLOOR_T)


# ---------- the set ----------

@dataclass(frozen=True)
class Stated:
    """A downward face past the limit that a part is allowed to have: between z0 and z1 above the bed."""
    z0: float
    z1: float
    why: str
    support: bool = False     # True: it does not print without support; the sheet says so


@dataclass(frozen=True)
class Item:
    name: str                 # the file name of the part
    coupon: str               # the coupon it belongs to (a row of the sheet)
    plate: str
    make: object              # () -> the solid in its print orientation
    how: str                  # the print orientation, in words
    fill: float = 1.0         # the printed share of the volume
    count: int = 1            # how many to print
    stated: tuple = ()
    view: tuple = (-35.0, 30.0)   # the camera of the sheet: az, el
    real: bool = False        # cut from the real skin: its inner faces are those of the cavity


PLATES = (("1", "shrink"), ("2", "warp: two walls and the flat strip"), ("3", "holes, inserts and the cone"),
          ("4", "joint 1: the fit"), ("5", "the weld pairs and joints 2, 3 and 5"),
          ("6", "the form: facets, edges, cut-in, hand-hold"), ("7", "the floor tile"),
          ("8", "the finish: four pairs"), ("9", "the finish: four plaques"), ("10", "the latch of the control panel"))


def _joint1_stated(part: str) -> tuple:
    j = JOINT
    if part == "upper":
        return (Stated(0.0, j.vgroove_w / 2 + 0.1, "the half V-groove at the bed edge of the outer face"),
                Stated(j.groove_depth - 0.2, j.groove_depth + 0.2, "the ceiling of the groove: a bridge of 4.2 to 4.6, inside"),
                Stated(c1.DOT_Z - c1.DOT_D, c1.DOT_Z + c1.DOT_D, "clearance dots: cones of 90 degrees, at the limit"))
    return (Stated(c1.HALF + c1.PILOT_MARK[3] - c1.PILOT_MARK[1], c1.HALF + c1.PILOT_MARK[3] + c1.PILOT_MARK[1], "the pilot mark: a V bar, at the limit"),
            Stated(c1.HALF - c1.DOT_Z - c1.DOT_D, c1.HALF - c1.DOT_Z + c1.DOT_D, "clearance dots: cones of 90 degrees, at the limit"))


def items() -> list[Item]:
    from . import structure as st
    j, o, t = JOINT, OTHER_JOINTS, st.FLOOR_T
    ff = floor_fill()
    upright = "upright, as the wall pieces print"
    cs = "the countersinks at the bed: cones of 90 degrees, at the limit"
    out = [
        Item("shrink-x", "shrink", "1", lambda: shrink_bar(1), "flat, along X of the bed"),
        Item("shrink-y", "shrink", "1", lambda: turned(shrink_bar(2), (0, 0, 1), 90), "flat, along Y of the bed"),
        Item("warp-wall", "warp", "2", warp_wall, upright + ", on its foot flange", count=2, view=(145.0, 25.0)),
        Item("flat-strip", "warp", "2", flat_strip, "flat, the table face on the bed", ff),
        Item("insert", "insert", "3", insert_coupon, upright + ": the foot of the hood on the bed, the holes from the bed up", view=(140.0, 35.0),
             stated=(Stated(INSERT_DEPTH - 0.2, INSERT_DEPTH + 0.2, "the ends of the three upright holes from the bed: bridges of 5.6 to 5.8, as in the foot of the hood"),
                     Stated(INSERT_BOSS + 3.0 + 3.5 + OTHER_JOINTS.ring_w + INSERT_BOSS - (INSERT_BOSS + 3.0), INSERT_BOSS + 3.0 + 3.5 + OTHER_JOINTS.ring_w + INSERT_BOSS,
                            "the tops of the three level insert holes (5.6 to 5.8 wide)"))),
        Item("holes-buttons", "holes", "3", button_plate, "flat, the panel top on the bed"),
        Item("holes-lever", "holes", "3", lever_plate, "flat, the panel top on the bed"),
        Item("holes-power", "holes", "3", power_wall, upright + ", on its foot flange", view=(-35.0, 20.0),
             stated=(Stated(19.0, 19.0 + max(POWER_HOLES) / 2 + 0.2, "the tops of the three level holes (16 wide): this is the test"),)),
        Item("holes-usb", "holes", "3", usb_plate, "flat, the outer face on the bed"),
        Item("cone-gauge", "cone", "3", cone_gauge, "flat, the sockets open to the top (as the upper floor tile prints)"),
        Item("cone-plug", "cone", "3", cone_plug, "flat, the cone on top (as the lower floor tile prints)"),
        Item("rod-block", "rod-fit", "3", rod_block, "flat, the face of the plate on the bed (as the bezel plate prints)"),
        Item("rod", "rod-fit", "3", rod_piece, "standing on its tip, as the real rod",
             stated=(Stated(0.0, 0.31, "the small break of 0.3 round the tip, at the bed"),)),
    ]
    for c in c1.CLEARANCES:
        out.append(Item(f"joint1-lower-{c1.tag(c)}", "joint1", "4", lambda c=c: c1.lower_half(c), upright + ", the seam at the top",
                        stated=_joint1_stated("lower"), view=(145.0, 25.0)))
        out.append(Item(f"joint1-upper-{c1.tag(c)}", "joint1", "4", lambda c=c: c1.upper_half(c), upright + ", the seam on the bed",
                        stated=_joint1_stated("upper"), view=(145.0, 25.0)))
    out += [
        Item("weld-lower", "weld", "5", weld_lower, upright + ", the seam at the top", count=3, view=(145.0, 25.0)),
        Item("weld-upper", "weld", "5", weld_upper, upright + ", the seam on the bed", count=3, view=(145.0, 25.0),
             stated=(Stated(0.0, j.vgroove_w / 2 + 0.1, "the half V-groove at the bed edge of the outer face"),
                     Stated(j.groove_depth - 0.2, j.groove_depth + 0.2, "the ceiling of the groove: a bridge of 4.4, inside"))),
        Item("joint2-lower", "joint2", "5", joint2_lower, "flat, the table face on the bed", ff, stated=(Stated(0.0, 2.0, cs),)),
        Item("joint2-upper", "joint2", "5", lambda: turned(joint2_upper(), (1, 0, 0), 180), "flat, the top face on the bed (turned over)", ff,
             stated=(Stated(0.0, 2.0, "the mark of the smaller pilot at the bed: a cone of 90 degrees"),)),
        Item("joint3-floor", "joint3", "5", joint3_floor, "flat, the table face on the bed", ff, stated=(Stated(0.0, 2.0, cs),)),
        Item("joint3-wall", "joint3", "5", joint3_wall, upright + ": the foot flange is 10 above the bed", view=(145.0, 20.0),
             stated=(Stated(t - o.foot_key_h - 0.1, t + 0.1, "the foot flange and its key: a level overhang 12 wide, 10 above the bed", support=True),
                     Stated(t + foot_pilot_depth() - 0.3, t + foot_pilot_depth() + 0.3, "the blind ends of the two pilot holes"))),
        Item("joint5-frame", "joint5", "5", joint5_frame, upright + ": the seat face is upright, the holes are level", view=(-35.0, 25.0),
             stated=(Stated(0.0, 0.6, "the chamfer of the seat face at the bed"),
                     Stated(SERVICE[1] / 2, SERVICE[1] / 2 + 3.2, "the tops of the level insert and pin holes"))),
        Item("joint5-cover", "joint5", "5", lambda: turned(joint5_cover(), (1, 0, 0), 90), "flat, the outer face on the bed",
             stated=(Stated(0.0, 0.6, "the chamfer of the outer face at the bed"),)),
        Item("facet45", "facet45", "6", facet45, upright + " (the upper rear piece): on the door's top edge", count=2, view=(150.0, 20.0), real=True,
             stated=(Stated(0.0, 64.0, "the rear facet of the rear shelf: 45 degrees, at the limit; only mesh facets pass it"),)),
        Item("cut-in", "cut-in", "6", cut_in, upright + " (the middle piece): on its lower cut", view=(140.0, 20.0), real=True,
             stated=(Stated(0.0, 30.0, "the upper half of the cut-in (33 degrees at its lip) and the steps of the cavity inside"),)),
        Item("hand-hold", "hand-hold", "6", hand_hold, upright + " (the upper rear piece): on its lower cut", count=2, view=(150.0, 5.0), real=True,
             stated=(Stated(0.0, 52.0, "the roof of the hand-hold: 45 degrees, at the limit; and the steps of the cavity inside"),)),
        Item("edges-level", "edges", "6", edge_bar, "lying: the edges are level, as on the rear shelf", 0.55, view=(-150.0, 30.0),
             stated=(Stated(9.0, 17.5, "the facet that faces down 45 degrees and its round: at the limit"),)),
        Item("edges-upright", "edges", "6", lambda: turned(edge_bar(), (0, 1, 0), -90), "on its end: the edges are upright, as on the band's stub", 0.55,
             view=(-150.0, 30.0)),
        Item("floor-tile", "floor", "7", floor_tile, "flat, the table face on the bed", ff),
        Item("latch-nose", "latch", "10", latch_nose, "as the deck stands, as the deck nose prints: on its lower cut, the front face upright", view=(-40.0, 15.0), real=True,
             stated=(Stated(0.0, 30.0, "the ceilings of the skin inside: the steps of the cavity, the underside of the ledge and of the deck top, as in the deck nose piece"),)),
        Item("latch-frame", "latch", "10", latch_frame, "as the frame prints: the lower face of the bar on the bed", view=(-35.0, 35.0),
             stated=(Stated(9.3, 9.7, "the roof of the tunnel: a bridge between its walls, as in the frame"),)),
        Item("latch-bolt", "latch", "10", latch_bolt, "on its side: the flat side on the bed", view=(-35.0, 35.0),
             stated=(Stated(0.0, 1.0, "the edge break of the button's rim at the bed"),
                     Stated(3.8, 8.4, "the side of the neck (a step of 4) and the top of the spring's bore: short bridges"))),
        Item("latch-gate", "latch", "10", latch_gate, "flat: its rear face on the bed, the peg up"),
        Item("latch-notch", "latch", "10", latch_notch, "as the frame prints: the lower face of the bar on the bed", view=(150.0, 30.0),
             stated=(Stated(7.0, 7.4, "the roof of the notch: a bridge of 16, as in the frame"),)),
        Item("latch-hook", "latch", "10", latch_hook, "top face down, as the tiles print", view=(150.0, 30.0),
             stated=(Stated(0.0, 0.4, "the edge break of the plate's rear edge at the bed"),
                     Stated(13.8, 16.0, "the top arc of the toe of the hook: it looks down, as on each tile (about 0.7 cm2)"))),
        Item("latch-strike", "latch", "10", latch_strike, "top face down, as the tiles print", view=(-35.0, 35.0),
             stated=(Stated(0.0, 0.4, "the edge break of the plate's front edge at the bed"),
                     Stated(17.4, 18.0, "the lips of the strike: an overhang of 3.4, as on each panel"))),
    ]
    best = c1.ASSEMBLED_C
    out += [
        Item(f"finish-lower-{c1.tag(best)}", "finish", "8", lambda: c1.lower_half(best), upright + ", the seam at the top", count=4,
             stated=_joint1_stated("lower"), view=(145.0, 25.0)),
        Item(f"finish-upper-{c1.tag(best)}", "finish", "8", lambda: c1.upper_half(best), upright + ", the seam on the bed", count=4,
             stated=_joint1_stated("upper"), view=(145.0, 25.0)),
    ]
    for k in range(1, 5):
        out.append(Item(f"plaque-P{k}", "finish", "9", lambda k=k: c1.plaque(k), "upright on its long edge, as a wall piece",
                        stated=(Stated(c1.PLAQUE[1] * 0.6 - c1.DOT_D, c1.PLAQUE[1] * 0.6 + c1.DOT_D, "code dots: cones of 90 degrees, at the limit"),
                                Stated(c1.PLAQUE[1] - 1.5, c1.PLAQUE[1], "the V notch in the top edge"))))
    return out


# ---------- checks ----------

def overhangs(shape, zmin: float) -> list[dict]:
    """coupon.overhangs, with the heights from the bed of the tight box."""
    out = c1.overhangs(shape)
    shift = shape.BoundBox.ZMin - zmin
    for g in out:
        g["z"] = round(g["z"] + shift, 1)
    return out


def check_item(it: Item, shape, lim: c1.Printer) -> dict:
    b = tight_box(shape)
    groups = c1._merge_heights(overhangs(shape, b.ZMin))
    for g in groups:
        hit = next((s for s in it.stated if s.z0 - 0.2 <= g["z"] and g["z_max"] <= s.z1 + 0.2), None)
        g["exception"] = hit.why if hit else None
        g["support"] = bool(hit and hit.support)
    fits = b.XLength <= lim.xy + 1e-6 and b.YLength <= lim.xy + 1e-6 and b.ZLength <= lim.z and abs(b.ZMin) < 1e-6
    printed = shape.Volume / 1000 * it.fill
    res = {"part": it.name, "coupon": it.coupon, "plate": it.plate, "how": it.how, "count": it.count, "real": it.real,
           "valid": shape.isValid(), "solids": len(shape.Solids), "faces": len(shape.Faces),
           "box_mm": [round(b.XLength, 1), round(b.YLength, 1), round(b.ZLength, 1)], "fits_bed": bool(fits),
           "volume_cm3": round(shape.Volume / 1000, 2), "fill": round(it.fill, 3), "mass_g": round(printed * DENSITY, 1),
           "time_h": round(printed / RATE_CM3_H, 2), "overhangs": groups,
           "needs_support_mm2": round(sum(g["area_mm2"] for g in groups if g["support"]), 1),
           "unstated_overhang_mm2": round(sum(g["area_mm2"] for g in groups if not g["exception"]), 2)}
    res["pass"] = bool(res["valid"] and res["solids"] == 1 and fits and res["unstated_overhang_mm2"] < 0.5)
    return res


def face_findings(shape, name: str) -> dict[str, int]:
    """The findings of tools/face_check.py on a part, by rule (the edge break is allowed). They are for information:
    a coupon has narrow faces by design (a chamfer, a V-groove, a key, a mark), and a cut from the real skin has the
    steps of the cavity inside."""
    from tools import face_check
    out: dict[str, int] = {}
    for f in face_check.failures(face_check.check(shape, name, break_radius=Blueprint().edge_break)):
        out[f.rule] = out.get(f.rule, 0) + 1
    return out


def holes_of(shape, axis: P3) -> dict[float, int]:
    """{diameter: number of axes} of the cylindrical holes along an axis."""
    seen: dict[float, set] = {}
    for f in shape.Faces:
        s = f.Surface
        if type(s).__name__ == "Cylinder" and abs(abs(s.Axis.dot(V(*axis))) - 1) < 1e-9:
            c = s.Center - V(*axis) * s.Center.dot(V(*axis))
            seen.setdefault(round(2 * s.Radius, 3), set()).add((round(c.x, 3), round(c.y, 3), round(c.z, 3)))
    return {d: len(v) for d, v in sorted(seen.items())}


def check_pairs() -> dict:
    """The pairs in their assembled position: no common volume, the faces meet, the holes are on one axis."""
    import Part
    from . import structure as st
    s, o, t = base_screw(), OTHER_JOINTS, st.FLOOR_T
    out = {}
    lo, up = joint2_lower(), joint2_upper()
    lap = Part.makeCompound([f for f in lo.Faces if abs(f.BoundBox.ZMin - t / 2) < 1e-6 and abs(f.BoundBox.ZMax - t / 2) < 1e-6]).common(
        Part.makeCompound([f for f in up.Faces if abs(f.BoundBox.ZMin - t / 2) < 1e-6 and abs(f.BoundBox.ZMax - t / 2) < 1e-6])).Area
    gaps = [Part.Vertex(V(x + o.cone_d / 2 - o.cone_h / 2, 0, t / 2 + o.cone_h / 2)).distToShape(up)[0] for x in lap_cones()]
    out["joint2"] = {"common_volume_mm3": round(lo.common(up).Volume, 6), "lap_contact_mm2": round(lap, 1),
                     "cone_gap_mm": [round(g, 4) for g in gaps], "cone_clearance": o.cone_clearance,
                     "holes_lower": holes_of(lo, (0, 0, 1)), "holes_upper": holes_of(up, (0, 0, 1)),
                     "screw_l": o.lap_screw_l, "floor_t": t,
                     "screw_longer_than_floor_mm": round(o.lap_screw_l - t, 2)}
    out["joint2"]["pass"] = bool(out["joint2"]["common_volume_mm3"] < 1e-6 and lap > 0.6 * (o.lap_w - 1) * PAIR_L
                                 and all(abs(g - o.cone_clearance) < 2e-3 for g in gaps)
                                 and out["joint2"]["holes_lower"] == {s["clearance"]: 2}
                                 and out["joint2"]["holes_upper"] == {d: 1 for d in s["pilots"]})
    wa, fl = joint3_wall(), joint3_floor()
    y0, y1 = foot_key_y()
    (a, b), = foot_key_runs()
    mid_z = t - o.foot_key_h / 2
    side = [Part.Vertex(V((a + b) / 2, y, mid_z)).distToShape(fl)[0] for y in (y0, y1)]
    end = [Part.Vertex(V(x, (y0 + y1) / 2, mid_z)).distToShape(fl)[0] for x in (a, b)]
    seat = Part.makeCompound([f for f in wa.Faces if abs(f.BoundBox.ZMin - t) < 1e-6 and abs(f.BoundBox.ZMax - t) < 1e-6]).common(
        Part.makeCompound([f for f in fl.Faces if abs(f.BoundBox.ZMin - t) < 1e-6 and abs(f.BoundBox.ZMax - t) < 1e-6])).Area
    tip = t + foot_pilot_depth() - 1.0
    out["joint3"] = {"common_volume_mm3": round(wa.common(fl).Volume, 6), "key_gap_side_mm": [round(v, 4) for v in side],
                     "key_gap_end_mm": [round(v, 4) for v in end], "seat_contact_mm2": round(seat, 1),
                     "holes_wall": holes_of(wa, (0, 0, 1)), "holes_floor": holes_of(fl, (0, 0, 1)),
                     "screw_tip_z": tip, "flange_top_z": t + JOINT.foot_t, "block_top_z": t + JOINT.foot_t + BOSS_OVER_SCREW,
                     "screw_through_flange_mm": round(tip - (t + JOINT.foot_t), 2)}
    c = JOINT.groove_clearance
    out["joint3"]["pass"] = bool(out["joint3"]["common_volume_mm3"] < 1e-6 and all(abs(v - c) < 2e-3 for v in side + end)
                                 and seat > 0.5 * JOINT.foot_h * PAIR_L and out["joint3"]["holes_wall"] == {d: 1 for d in s["pilots"]}
                                 and out["joint3"]["holes_floor"] == {s["clearance"]: 2} and tip < out["joint3"]["block_top_z"] - 1.0)
    fr, co = joint5_frame(), joint5_cover()
    out["joint5"] = {"common_volume_mm3": round(fr.common(co).Volume, 6), "holes_frame": holes_of(fr, (0, 1, 0)),
                     "holes_cover": holes_of(co, (0, 1, 0)), "insert_hole_d": o.insert_hole_d, "insert_depth": INSERT_DEPTH,
                     "behind_insert_mm": round(INSERT_BOSS - INSERT_DEPTH, 2), "pin_gap_mm": o.pin_clearance}
    d_pin = round(o.pin_d + 2 * o.pin_clearance, 3)
    out["joint5"]["pass"] = bool(out["joint5"]["common_volume_mm3"] < 1e-6 and out["joint5"]["holes_frame"] == {o.pin_d: 2, o.insert_hole_d: 2}
                                 and out["joint5"]["holes_cover"] == {d_pin: 3, M4_CLEAR: 2})
    wl, wu = weld_lower(), weld_upper()
    touch = Part.makeCompound(c1.faces_at(wl, 0.0, 1.0)).common(Part.makeCompound(c1.faces_at(wu, 0.0, -1.0))).Area
    out["weld"] = {"common_volume_mm3": round(wl.common(wu).Volume, 6), "seam_contact_mm2": round(touch, 1),
                   "holes_lower": holes_of(wl, (0, 0, 1)), "weld_face_mm2_wanted": round(0.6 * (JOINT.flange_h + JOINT.wall_t) * WELD_L, 1)}
    out["weld"]["pass"] = bool(out["weld"]["common_volume_mm3"] < 1e-6 and touch > out["weld"]["weld_face_mm2_wanted"]
                               and JOINT.pilot_d_abs in out["weld"]["holes_lower"])
    plug, gauge = cone_plug(), cone_gauge()
    gaps = []
    for k, cl in enumerate(CONE_CLEARANCES):
        p = turned(plug, (1, 0, 0), 180)
        b0 = p.BoundBox
        p.translate(V(7.0 + k * 15.0 - (b0.XMin + b0.XMax) / 2, 7.0 - (b0.YMin + b0.YMax) / 2, 6.0 - b0.ZMin - o.cone_h + 0.001))
        probe = V(7.0 + k * 15.0 + o.cone_d / 2 - o.cone_h / 2, 7.0, 6.0 - o.cone_h / 2)
        gaps.append({"clearance": cl, "gap_mm": round(Part.Vertex(probe).distToShape(gauge)[0], 4), "common_mm3": round(p.common(gauge).Volume, 6)})
    out["cone"] = {"sockets": gaps, "pass": all(abs(g["gap_mm"] - g["clearance"]) < 2e-3 and g["common_mm3"] < 1e-6 for g in gaps)}
    ins = insert_coupon()
    upright = holes_of(ins, (0, 0, 1))
    # the bosses of the foot of the hood (service_boss across) are cylinders with an upright axis too
    bosses = sum(n for k, n in upright.items() if abs(float(k) - OTHER_JOINTS.service_boss) < 1e-6)
    upright = {k: n for k, n in upright.items() if abs(float(k) - OTHER_JOINTS.service_boss) >= 1e-6}
    out["insert"] = {"holes_upright": upright, "bosses_of_the_foot": bosses, "holes_level": holes_of(ins, (0, 1, 0)), "depth": INSERT_DEPTH, "boss": INSERT_BOSS}
    want = {d: 1 for d in insert_holes()}
    out["insert"]["pass"] = upright == want and out["insert"]["holes_level"] == want and bosses == len(want)
    return out


def check_real() -> dict:
    """What the cuts from the real skin must have: the 45 degree facet, the round, the cut-in, the roof."""
    d = Blueprint()
    out = {}

    def facets(shape, tol=0.02):
        return round(sum(f.Area for f in shape.Faces if type(f.Surface).__name__ == "Plane"
                         and abs(f.normalAt(0, 0).z + math.sqrt(0.5)) < tol), 1)

    def rounds(shape, r):
        return sum(1 for f in shape.Faces if type(f.Surface).__name__ == "Cylinder" and abs(f.Surface.Radius - r) < 1e-3)

    f = facet45()
    out["facet45"] = {"facet_45_mm2": facets(f), "rounds_r3": rounds(f, d.rear_round_r), "wall_mm3_per_mm2": None,
                      "crease_z_above_bed": d.rear_shelf_z0 - FACET_BOX[4]}
    out["facet45"]["pass"] = out["facet45"]["facet_45_mm2"] > 0.9 * (FACET_BOX[1] - FACET_BOX[0]) * d.rear_proud * math.sqrt(2) * 0.9 and out["facet45"]["rounds_r3"] >= 1
    del out["facet45"]["wall_mm3_per_mm2"]
    h = hand_hold()
    out["hand-hold"] = {"roof_45_mm2": facets(h), "rim_z_above_bed": round(d.grip_z1 - HAND_HOLD_BOX[4], 2)}
    out["hand-hold"]["pass"] = out["hand-hold"]["roof_45_mm2"] > 300.0
    ci = cut_in()
    solid = tight_box(ci)
    lip0, lip1 = d.cut_in_z0 + d.cut_in_pitch, d.cut_in_z0 + d.cut_in_pitch + d.cut_in_h
    out["cut-in"] = {"lips_z": [lip0, lip1], "box_z": [CUT_IN_BOX[4], CUT_IN_BOX[5]], "box_mm": [round(solid.XLength, 1), round(solid.YLength, 1), round(solid.ZLength, 1)],
                     "depth": d.cut_in_depth}
    out["cut-in"]["pass"] = CUT_IN_BOX[4] < lip0 - 5 and CUT_IN_BOX[5] > lip1 + 5 and CUT_IN_BOX[0] < d.cut_in_x - d.cut_in_h and CUT_IN_BOX[2] < d.cut_in_y - d.cut_in_h
    return out


# ---------- plates ----------

def pack(sizes: dict[str, tuple[float, float]], bed: float, gap: float = GAP) -> dict[str, tuple[float, float]] | None:
    """Places for rectangles on a square bed: each at the first free corner of those already placed. None when one
    does not fit."""
    placed: dict[str, tuple[float, float, float, float]] = {}
    for name, (w, h) in sorted(sizes.items(), key=lambda kv: (-max(kv[1]), -kv[1][0] * kv[1][1], kv[0])):
        spots = [(0.0, 0.0)] + [p for x0, y0, x1, y1 in placed.values() for p in ((x1 + gap, y0), (x0, y1 + gap), (x1 + gap, 0.0), (0.0, y1 + gap))]
        for x, y in sorted(spots, key=lambda p: (p[1], p[0])):
            if x + w > bed + 1e-6 or y + h > bed + 1e-6:
                continue
            if all(x + w + gap <= a + 1e-6 or c + gap <= x + 1e-6 or y + h + gap <= b + 1e-6 or e + gap <= y + 1e-6 for a, b, c, e in placed.values()):
                placed[name] = (x, y, x + w, y + h)
                break
        else:
            return None
    return {k: (v[0], v[1]) for k, v in placed.items()}


def plate_layout(rows: list[dict], lim: c1.Printer) -> dict:
    """{plate: {copy name: (x, y)}} with every copy of every part; a plate that does not hold its parts is None."""
    out = {}
    for key, _ in PLATES:
        sizes = {}
        for r in rows:
            if r["plate"] == key:
                for k in range(r["count"]):
                    sizes[r["part"] if r["count"] == 1 else f"{r['part']}#{k + 1}"] = (r["box_mm"][0], r["box_mm"][1])
        out[key] = pack(sizes, lim.xy)
    return out


# ---------- outputs ----------

def table(rows: list[dict], layout: dict) -> str:
    lines = ["| Plate | Part (`stl/`, `brep/`) | Count | Print box (mm) | Orientation | ABS (g) | Time (h) |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        lines.append(f"| {r['plate']} | `{r['part']}` | {r['count']} | {' x '.join(f'{v:g}' for v in r['box_mm'])} | {r['how']} | "
                     f"{r['mass_g'] * r['count']:.0f} | {r['time_h'] * r['count']:.1f} |")
    lines += ["", "| Plate | Content | Parts | ABS (g) | Time (h) | Fits the bed |", "| --- | --- | --- | --- | --- | --- |"]
    for key, title in PLATES:
        mine = [r for r in rows if r["plate"] == key]
        lines.append(f"| {key} | {title} | {sum(r['count'] for r in mine)} | {sum(r['mass_g'] * r['count'] for r in mine):.0f} | "
                     f"{sum(r['time_h'] * r['count'] for r in mine) + PLATE_SETUP_H:.1f} | {'yes' if layout[key] else 'NO'} |")
    lines.append(f"| | **all** | {sum(r['count'] for r in rows)} | {sum(r['mass_g'] * r['count'] for r in rows):.0f} | "
                 f"{sum(r['time_h'] * r['count'] for r in rows) + PLATE_SETUP_H * len(PLATES):.1f} | |")
    return "\n".join(lines) + "\n"


PROVES = {"rod-fit": "the fit of the push rod of 4 x 4 in its hole of 4.4 in the bezel plate, in ABS",
          "latch": "the latch of the control panel: the button flush in its hole with 0.3 all round, the stroke, the wedge and the spring",
          "shrink": "the shrink of ABS along X and Y of the bed",
          "warp": "warp in ABS: a tall wall and a long flat strip stay flat",
          "weld": "the solvent weld of ABS on the real joint section",
          "insert": "the hole for the M4 heat-set insert, upright from the bed (the foot of the bolted hood) and level",
          "holes": "holes: buttons, lever, power button, USB sockets",
          "cone": "the clearance of the cone that locates a seam",
          "joint1": "joint 1: the groove clearance and the pilot hole",
          "joint2": "joint 2: the floor lap with its cones and screws",
          "joint3": "joint 3: the wall foot on the floor",
          "joint5": "joint 5: the service seam with inserts and pins",
          "facet45": "the 45 degree rear facet prints clean with no support",
          "cut-in": "a cut-in prints clean and takes paint",
          "hand-hold": "the rim and the roof of a hand-hold print clean",
          "edges": "where paint goes thin: sharp edge, break, round, lip, crease",
          "floor": "the floor sandwich: flat, stiff, its mass and time",
          "finish": "bond, fill, prime and paint: the seam does not show"}

TINT = {"rod-fit": "#c0c0c0", "latch": "#d0762b", "shrink": "#9ec5e8", "warp": "#9ec5e8", "weld": "#f0a0a0", "insert": "#e8c39e", "holes": "#f0e09a", "cone": "#e3a8c8", "joint1": "#b9dea0",
        "joint2": "#a8d8d0", "joint3": "#c9b8e8", "joint5": "#f2b8a0", "facet45": "white", "cut-in": "white", "hand-hold": "white",
        "edges": "white", "floor": "#d0d0d0", "finish": "#b9dea0"}
PLATE_PITCH = 280.0
SHEET_PITCH = 1000.0


def main() -> int:
    import MeshPart
    import Part

    from .solids import edge_polylines

    out = Path(os.environ.get("CANDYBAR_OUT", CAD / "out" / "coupons")).resolve()
    if out == (CAD / "out").resolve():
        out = out / "coupons"
    for sub in ("brep", "stl", "layout", "sheet"):
        (out / sub).mkdir(parents=True, exist_ok=True)
        for old in (out / sub).glob("*.*"):
            old.unlink()
    lim = bed()
    its = items()
    shapes, rows, cabinet = {}, [], {}
    for it in its:
        made = it.make()
        if it.real:  # where the cut was in the cabinet: the corner of its box
            b = tight_box(made)
            cabinet[it.name] = (b.XMin, b.YMin, b.ZMin)
        shapes[it.name] = to_bed(made)
        rows.append(check_item(it, shapes[it.name], lim))
        r = rows[-1]
        r["face_check"] = face_findings(shapes[it.name], it.name)
        print(f"{it.name}: valid {r['valid']}, {r['faces']} faces, box {r['box_mm']}, {r['mass_g']} g, {r['time_h']} h, overhangs "
              f"{[(g['z'], g['z_max'], g['area_mm2'], g['steepest_deg'], bool(g['exception'])) for g in r['overhangs']]} -> {'pass' if r['pass'] else 'FAIL'}; face check {r['face_check']}")
        shapes[it.name].exportBrep(str(out / "brep" / f"{it.name}.brep"))
        stl = closed_mesh(shapes[it.name])
        r["stl_closed"] = stl.isSolid()
        r["pass"] = r["pass"] and r["stl_closed"]
        stl.write(str(out / "stl" / f"{it.name}.stl"))
    pairs = check_pairs()
    real = check_real()
    for k, v in {**pairs, **real}.items():
        print(f"{k}: {json.dumps({a: b for a, b in v.items() if a != 'pass'})} -> {'pass' if v['pass'] else 'FAIL'}")
    layout = plate_layout(rows, lim)
    by = {r["part"]: r for r in rows}
    manifest, edges, places = {}, {}, {}
    for n, (key, title) in enumerate(PLATES):
        ox, oy = (n % 4) * PLATE_PITCH, -(n // 4) * PLATE_PITCH
        full = Part.makePolygon([V(ox - BED_MARGIN, oy - BED_MARGIN, 0), V(ox + lim.xy + BED_MARGIN, oy - BED_MARGIN, 0),
                                 V(ox + lim.xy + BED_MARGIN, oy + lim.xy + BED_MARGIN, 0), V(ox - BED_MARGIN, oy + lim.xy + BED_MARGIN, 0),
                                 V(ox - BED_MARGIN, oy - BED_MARGIN, 0)])
        full.exportBrep(str(out / "layout" / f"bed-{key}.brep"))
        used = Part.makePolygon([V(ox, oy, 0), V(ox + lim.xy, oy, 0), V(ox + lim.xy, oy + lim.xy, 0), V(ox, oy + lim.xy, 0), V(ox, oy, 0)])
        used.exportBrep(str(out / "layout" / f"plate-{key}.brep"))
        print(f"plate {key} ({title}): {'fits' if layout[key] else 'DOES NOT FIT'}, {len(layout[key] or {})} parts")
        for copy, (x, y) in (layout[key] or {}).items():
            part = copy.split("#")[0]
            s = moved(shapes[part], V(ox + x, oy + y, 0))
            stem = f"p{key}-{copy.replace('#', '-')}"
            s.exportBrep(str(out / "layout" / f"{stem}.brep"))
            MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.2, Relative=False).write(str(out / "layout" / f"{stem}.stl"))
            name = stem.replace("-", "_")
            manifest[name] = {"file": f"layout/{stem}.stl", "finish": TINT[by[part]["coupon"]], "brep": f"layout/{stem}.brep",
                              # for the tools: the coupon, the move from its own frame (stl/, brep/) to the plate, and for a
                              # cut from the real skin the move from the plate back into the cabinet
                              "coupon": part, "group": by[part]["coupon"], "offset": [round(ox + x, 6), round(oy + y, 6), 0.0]}
            if part in cabinet:
                manifest[name]["to_cabinet"] = [round(c - o, 6) for c, o in zip(cabinet[part], (ox + x, oy + y, 0.0))]
            edges[name] = edge_polylines(s)
            places[copy] = {"plate": key, "x": round(x, 1), "y": round(y, 1)}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
    (out / "edges.json").write_text(json.dumps(edges))
    sheet_manifest, sheet_edges, focus = {}, {}, {}
    for n, it in enumerate(its):
        s = shapes[it.name]
        b = tight_box(s)
        cx, cy = (n % 6) * SHEET_PITCH, -(n // 6) * SHEET_PITCH
        s = s.translated(V(cx - b.XLength / 2, cy - b.YLength / 2, 0))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.03, AngularDeflection=0.1, Relative=False).write(str(out / "sheet" / f"{it.name}.stl"))
        key = it.name.replace("-", "_")
        sheet_manifest[key] = {"file": f"{it.name}.stl", "finish": TINT[it.coupon]}
        sheet_edges[key] = edge_polylines(s, 0.4)
        focus[it.name] = {"target": [cx, cy, b.ZLength / 2], "radius": round(0.62 * b.DiagonalLength + 4, 1), "az": it.view[0], "el": it.view[1], "aspect": 0.75}
    (out / "sheet" / "manifest.json").write_text(json.dumps(sheet_manifest, indent=1))
    (out / "sheet" / "edges.json").write_text(json.dumps(sheet_edges))
    (out / "sheet" / "focus.json").write_text(json.dumps(focus, indent=1))
    ok = all(r["pass"] for r in rows) and all(v["pass"] for v in pairs.values()) and all(v["pass"] for v in real.values()) and all(layout.values())
    result = {"printer": {"xy": lim.xy, "z": lim.z, "bed": list(BED), "bed_margin": BED_MARGIN, "top_margin": TOP_MARGIN}, "material": "ABS", "rule": {"density_g_cm3": DENSITY, "rate_cm3_h": RATE_CM3_H, "plate_setup_h": PLATE_SETUP_H},
              "plates": [{"plate": k, "title": t, "fits": bool(layout[k]), "origin": [(n % 4) * PLATE_PITCH, -(n // 4) * PLATE_PITCH]}
                         for n, (k, t) in enumerate(PLATES)], "proves": PROVES, "parts": rows, "places": places,
              "pairs": pairs, "real": real, "base_screw": base_screw(), "insert_holes": insert_holes(),
              "edges": [{"y": y, "z": z, "what": w} for (y, z), w in EDGE_NAMES.items()], "pass": bool(ok)}
    (out / "coupons.json").write_text(json.dumps(result, indent=1))
    (out / "table.md").write_text(table(rows, layout))
    total = sum(r["mass_g"] * r["count"] for r in rows)
    print(f"coupons: {len(rows)} parts, {sum(r['count'] for r in rows)} prints, {total:.0f} g: {'all checks pass' if ok else 'A CHECK FAILS'} -> {out}")
    return 0 if ok else 1
