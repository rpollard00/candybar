"""The outer-form solids of shell variant D, built with FreeCAD's Part module from the dimensions in dims.py.

The front of the cabinet is one side profile (deck front, deck top, one concave bend, the straight screen
face) extruded across the width. One band runs round its outer edge without a break: a soft radius at the
land, a bevel leaning 30 degrees from the side face, then the side face. Along the side chain the band is a
ruled loft between the profile at the inner edge of the bevel and the profile offset inward at the side
plane, so its width is the same everywhere by construction; across the deck front and the flat corner faces
the band is a plane with the same section. The hood is built the same way, so its sides continue the rails.
"""
from __future__ import annotations

import math

import FreeCAD
import Part

from .dims import MON_ACTIVE_H, MON_ACTIVE_W, Dims

V = FreeCAD.Vector
BIG = 4000.0


def halfspace(point: tuple[float, float, float], normal: tuple[float, float, float]) -> Part.Shape:
    """The solid region n . (p - point) >= 0, as a large box."""
    n = V(*normal)
    n.normalize()
    b = Part.makeBox(BIG, BIG, BIG, V(-BIG / 2, -BIG / 2, 0))
    b.Placement = FreeCAD.Placement(V(*point), FreeCAD.Rotation(V(0, 0, 1), n))
    return b


def common(*shapes: Part.Shape) -> Part.Shape:
    out = shapes[0]
    for s in shapes[1:]:
        out = out.common(s)
    return out


def box(lo: tuple[float, float, float], hi: tuple[float, float, float]) -> Part.Shape:
    return Part.makeBox(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2], V(*lo))


def face_from(points: list[tuple[float, float, float]]) -> Part.Face:
    return Part.Face(Part.makePolygon([V(*p) for p in points] + [V(*points[0])]))


def prism_y(xz: list[tuple[float, float]], y0: float, y1: float) -> Part.Shape:
    return face_from([(x, y0, z) for x, z in xz]).extrude(V(0, y1 - y0, 0))


# ---------- profiles in the YZ plane: a list of segments ("L", p, q) or ("A", p, mid, q) ----------

Seg = tuple


def wire_at(segs: list[Seg], x: float) -> Part.Wire:
    edges = []
    for s in segs:
        pts = [V(x, p[0], p[1]) for p in s[1:]]
        edges.append(Part.makeLine(*pts) if s[0] == "L" else Part.Arc(*pts).toShape())
    return Part.Wire(edges)


def arc_seg(centre: tuple[float, float], r: float, a0: float, a1: float) -> Seg:
    pt = lambda a: (centre[0] + r * math.cos(a), centre[1] + r * math.sin(a))
    return ("A", pt(a0), pt((a0 + a1) / 2), pt(a1))


def band_solid(inner: list[Seg], outer: list[Seg], half: float, d: Dims) -> Part.Shape:
    """Profile extruded over |x| <= half - band_in, plus on each side the ruled loft to the offset profile at |x| = half."""
    xi = half - d.band_in
    core = Part.Face(wire_at(inner, -xi)).extrude(V(2 * xi, 0, 0))
    out = core
    for sx in (1, -1):
        loft = Part.makeLoft([wire_at(inner, sx * xi), wire_at(outer, sx * half)], True, True)
        out = out.fuse(loft)
    return out.removeSplitter()


def band_plane_cut(solid: Part.Shape, q: tuple[float, float], m: tuple[float, float], z_top: float, d: Dims) -> Part.Shape:
    """Cut the band along a straight top edge: q a point of the edge in plan, m its outward normal in plan."""
    ml = math.hypot(*m)
    mx, my = m[0] / ml, m[1] / ml
    a, b = d.band_in, d.band_drop
    return solid.cut(halfspace((q[0], q[1], z_top - b), (mx * b, my * b, a)))


def land_edges(solid: Part.Shape, test) -> list[Part.Edge]:
    return [e for e in solid.Edges if test(e)]


def try_fillet(solid: Part.Shape, r: float, edges: list[Part.Edge], log: list[str], what: str) -> Part.Shape:
    if not edges or r <= 0:
        return solid
    try:
        out = solid.makeFillet(r, edges)
        if out.isValid() and out.Volume > 0.9 * solid.Volume:
            log.append(f"{what}: fillet r {r} on {len(edges)} edges held")
            return out
        log.append(f"{what}: fillet gave an invalid solid, skipped")
    except Part.OCCError as exc:
        log.append(f"{what}: fillet failed ({exc}), skipped")
    return solid


# ---------- the front: deck, bend, screen face, body ----------

def front_profiles(d: Dims) -> tuple[list[Seg], list[Seg]]:
    """Side profile of deck and body (inner edge of the bevel) and its offset (the side plane edge of the band)."""
    su, cu = d.u
    top, h, D = d.deck_top, d.body_top, d.body_d
    b, a = d.band_drop, d.band_in
    t, r = d.bend_t, d.bend_r
    ya = d.foot_y - t
    centre = (ya, top + r)
    a0, a1 = -math.pi / 2, -math.pi / 2 + math.radians(90 - d.recline)
    s_seam = (h - top) / cu
    fy, fz = d.face(s_seam)
    nin = (cu, -su)

    def face_top(off: float) -> tuple[float, float]:
        y0, z0 = fy + off * nin[0], fz + off * nin[1]
        return y0 + (h - z0) * su / cu, h

    inner = [("L", (0.0, 0.0), (0.0, top - b)), ("L", (0.0, top - b), (a, top)), ("L", (a, top), (ya, top)),
             arc_seg(centre, r, a0, a1), ("L", None, face_top(0.0)), ("L", face_top(0.0), (D, h)), ("L", (D, h), (D, 0.0)),
             ("L", (D, 0.0), (0.0, 0.0))]
    inner[4] = ("L", inner[3][3], face_top(0.0))
    rb = r + b
    outer = [("L", (0.0, 0.0), (0.0, top - b - 20.0)), ("L", (0.0, top - b - 20.0), (a, top - b)), ("L", (a, top - b), (ya, top - b)),
             arc_seg(centre, rb, a0, a1), ("L", None, face_top(b)), ("L", face_top(b), (D, h)), ("L", (D, h), (D, 0.0)),
             ("L", (D, 0.0), (0.0, 0.0))]
    outer[4] = ("L", outer[3][3], face_top(b))
    return inner, outer


def front_solid(d: Dims, log: list[str]) -> Part.Shape:
    w, top = d.width, d.deck_top
    inner, outer = front_profiles(d)
    solid = band_solid(inner, outer, w / 2, d)
    c = d.deck_corner
    for sx in (1, -1):
        m = (sx, -1.0)
        q = (sx * (w / 2 - c), 0.0)
        solid = solid.cut(halfspace((q[0], q[1], 0), (m[0], m[1], 0)))
        solid = band_plane_cut(solid, (sx * (w / 2 - c / 2), c / 2), m, top, d)
    solid = solid.removeSplitter()
    xi = w / 2 - d.band_in
    s_seam_z = d.body_top

    def land(e: Part.Edge) -> bool:
        zs = [v.Point.z for v in e.Vertexes]
        mid = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
        if all(abs(z - top) < 1e-3 for z in zs) and mid.y < d.foot_y - d.bend_t - 1 and abs(mid.z - top) < 1e-3:
            return mid.y > 1.0 and not (abs(abs(mid.x) - w / 2) < 1e-3)
        on_side = abs(abs(mid.x) - xi) < 1e-3 and top - 1e-3 <= mid.z < s_seam_z - 1e-3
        return on_side and all(abs(abs(v.Point.x) - xi) < 1e-3 for v in e.Vertexes)

    solid = try_fillet(solid, d.band_r, land_edges(solid, land), log, "front land radius")
    bottom = lambda e: all(v.Point.z < 1e-3 for v in e.Vertexes) and e.valueAt(e.FirstParameter).y < c + 1e-3 \
        and e.valueAt(e.LastParameter).y < c + 1e-3
    solid = try_fillet(solid, d.bottom_r, land_edges(solid, bottom), log, "deck bottom radius")
    return solid


def body_and_deck(d: Dims, log: list[str]) -> tuple[Part.Shape, Part.Shape, Part.Shape]:
    """(body, deck, control panel). The deck is split off at the start of the bend."""
    w = d.width
    solid = front_solid(d, log)
    t = math.tan(math.radians(d.step_lean))
    for sx in (1, -1):
        step = common(halfspace((sx * d.rear_w / 2, 0, 0), (sx, 0, 0)), halfspace((sx * w / 2, d.step_y0, 0), (sx, 1, -t)))
        solid = solid.cut(step)
        below = halfspace((0, d.step_y0, 0), (0, 1, -t))
        c = d.rear_facet
        solid = solid.cut(common(halfspace((sx * (d.rear_w / 2 - c), d.body_d, 0), (sx, 1, 0)), below))
        solid = solid.cut(halfspace((sx * (w / 2 - c), d.body_d, 0), (sx, 1, 0)))
    # bezel recess between the lands, 2 mm behind the land surface plus the plate thickness
    half = d.bezel_w / 2 + d.panel_gap
    solid = solid.cut(in_face(box((-half, -60.0, d.bezel_s0), (half, d.bezel_t + 2.0, d.bezel_s1)), d))
    # control panel pocket
    py0 = d.deck_nose
    hw = d.panel_w / 2 + d.panel_gap
    solid = solid.cut(box((-hw, py0, d.panel_top - d.panel_t), (hw, py0 + d.panel_d + 2 * d.panel_gap, d.deck_top + 30)))
    split_y = d.foot_y - d.bend_t
    deck = common(solid, halfspace((0, split_y, 0), (0, -1, 0))).removeSplitter()
    body = common(solid, halfspace((0, split_y, 0), (0, 1, 0))).removeSplitter()
    panel = box((-d.panel_w / 2, py0 + d.panel_gap, d.panel_top - d.panel_t), (d.panel_w / 2, py0 + d.panel_gap + d.panel_d, d.panel_top))
    return body, deck, panel


def rear_features(d: Dims, solid: Part.Shape, fan_xz: tuple[float, float], duct_xz: tuple[float, float],
                  psu_box: tuple[tuple[float, float], tuple[float, float]]) -> tuple[Part.Shape, Part.Shape]:
    """Cut the door opening, vents, pockets and slots into the rear wall; return (body, rear door)."""
    D = d.body_d
    hw = d.door_w / 2
    solid = solid.cut(box((-hw, D - 3, d.door_z0), (hw, D + 1, d.door_z1)))
    door = box((-hw + 1.5, D - 3, d.door_z0 + 1.5), (hw - 1.5, D - 0.6, d.door_z1 - 1.5))
    fan = Part.makeCylinder(d.fan_d / 2, 20, V(fan_xz[0], D - 12, fan_xz[1]), V(0, 1, 0))
    door = door.cut(fan)
    solid = solid.cut(fan)
    for i in range(7):
        z = duct_xz[1] - 48 + i * 16
        slot = box((duct_xz[0] - 42, D - 9, z), (duct_xz[0] + 42, D + 1, z + 7))
        door = door.cut(slot)
        solid = solid.cut(slot)
    pz = d.pocket_z0 or d.door_z1 + 48
    for cx in (-d.rear_w / 4, d.rear_w / 4):
        pocket = common(box((cx - d.pocket_w / 2, D - 40, pz), (cx + d.pocket_w / 2, D + 1, pz + d.pocket_h)),
                        halfspace((0, D, pz), (0, 1, 28 / d.pocket_h)))
        solid = solid.cut(pocket)
    for sx in (1, -1):
        for i in range(4):
            z = 150 + i * 22
            x0, x1 = sorted((sx * (hw + 7), sx * (hw + 21)))
            solid = solid.cut(box((x0, D - 4, z), (x1, D + 1, z + 6)))
    (x0, x1), (z0, z1) = psu_box
    solid = solid.cut(box((x0, D - 4, z0), (x1, D + 1, z1)))
    return solid.removeSplitter(), door


# ---------- the face frame: x across, y into the cabinet (normal to the screen face), z up the slope ----------

def face_matrix(d: Dims) -> FreeCAD.Matrix:
    su, cu = d.u
    fy, fz = d.face(0.0)
    m = FreeCAD.Matrix()
    m.A11, m.A12, m.A13, m.A14 = 1, 0, 0, 0
    m.A21, m.A22, m.A23, m.A24 = 0, cu, su, fy
    m.A31, m.A32, m.A33, m.A34 = 0, -su, cu, fz
    return m


def in_face(shape: Part.Shape, d: Dims) -> Part.Shape:
    s = shape.copy()
    s.transformShape(face_matrix(d))
    return s


def rounded_box(w: float, depth: float, h: float, r: float, x0: float, y0: float, z0: float) -> Part.Shape:
    b = box((x0, y0, z0), (x0 + w, y0 + depth, z0 + h))
    edges = [e for e in b.Edges if abs(e.Vertexes[0].Point.y - e.Vertexes[1].Point.y) > 1e-6]
    return b.makeFillet(r, edges) if r > 0 else b


def bezel(d: Dims) -> Part.Shape:
    """A thick dark frame, its front 2 mm behind the land, stepping down to the screen."""
    w = d.bezel_w
    plate = box((-w / 2, 2.0, d.bezel_s0), (w / 2, 2.0 + d.bezel_t, d.bezel_s1))
    cs = d.image_s
    win = rounded_box(MON_ACTIVE_W, d.bezel_t + 4, MON_ACTIVE_H, d.bezel_corner_r, -MON_ACTIVE_W / 2, 0.0, cs - MON_ACTIVE_H / 2)
    sw = d.bezel_step_w
    step = rounded_box(MON_ACTIVE_W + 2 * sw, d.bezel_step + 2, MON_ACTIVE_H + 2 * sw, d.bezel_corner_r + sw,
                       -MON_ACTIVE_W / 2 - sw, 0.0, cs - MON_ACTIVE_H / 2 - sw)
    return in_face(plate.cut(win).cut(step).removeSplitter(), d)


def screen(d: Dims) -> Part.Shape:
    cs = d.image_s
    return in_face(box((-MON_ACTIVE_W / 2, d.mon_setback, cs - MON_ACTIVE_H / 2),
                       (MON_ACTIVE_W / 2, d.mon_setback + 1, cs + MON_ACTIVE_H / 2)), d)


# ---------- hood: its sides continue the rails ----------

def hood_profiles(d: Dims, front_y: float) -> tuple[list[Seg], list[Seg], dict[str, float]]:
    z0 = d.body_top + d.seam_gap
    h = d.hood_h - d.seam_gap
    top, D = z0 + h, d.body_d
    lf, lr = math.radians(d.hood_lean_front), math.radians(d.hood_lean_rear)
    rn = d.hood_nose_r

    def prof(off: float) -> list[Seg]:
        # front line y = front_y + off*cos(lf) + (z - z0) tan(lf), offset inward by off; roof lowered by off
        roof = top - off
        r = max(rn - off, 5.0)
        cz = roof - r
        cy = front_y + off / math.cos(lf) + (cz - z0) * math.tan(lf) + r / math.cos(lf)
        tan_pt = (cy - r * math.cos(lf), cz + r * math.sin(lf))
        start = (front_y + off / math.cos(lf), z0)
        rear_top = (D - (roof - z0) * math.tan(lr), roof)
        a0, a1 = math.pi - lf, math.pi / 2
        arc = arc_seg((cy, cz), r, a0, a1)
        return [("L", start, tan_pt), ("A", tan_pt, arc[2], (cy, roof)), ("L", (cy, roof), rear_top), ("L", rear_top, (D, z0)),
                ("L", (D, z0), start)]

    return prof(0.0), prof(d.band_drop), {"z0": z0, "top": top, "front_y": front_y}


def hood_parts(d: Dims, log: list[str]) -> dict[str, Part.Shape]:
    su, cu = d.u
    front_y = d.face((d.body_top - d.deck_top) / cu)[0]
    inner, outer, g = hood_profiles(d, front_y)
    w = d.width
    hood = band_solid(inner, outer, w / 2, d)
    xi = w / 2 - d.band_in

    def land(e: Part.Edge) -> bool:
        mid = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
        return all(abs(abs(v.Point.x) - xi) < 1e-3 for v in e.Vertexes) and abs(abs(mid.x) - xi) < 1e-3 \
            and mid.z > g["z0"] + 1e-3 and mid.y < d.body_d - 30
    hood = try_fillet(hood, d.band_r, land_edges(hood, land), log, "hood land radius")

    def outer_edge(e: Part.Edge) -> bool:
        mid = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
        return all(abs(abs(v.Point.x) - w / 2) < 1e-3 for v in e.Vertexes) and abs(abs(mid.x) - w / 2) < 1e-3 \
            and mid.z > g["z0"] + 1e-3 and mid.y < d.body_d - 30
    hood = try_fillet(hood, d.hood_outer_r, land_edges(hood, outer_edge), log, "hood outer radius")
    for sx in (1, -1):
        hood = hood.cut(halfspace((sx * (w / 2 - d.rear_facet), d.body_d, 0), (sx, 1, 0)))
    z0, top, yf = g["z0"], g["top"], front_y
    bar = d.rail_t
    r_in = max(d.hood_corner_r - bar, 8.0)
    k0, k1 = (-(w / 2 - bar), top - d.hood_bar_top), (w / 2 - bar, top - d.hood_bar_top)
    inset = [(-(w / 2 - bar), z0 - 5), (k0[0], k0[1] - r_in), *[(k0[0] + r_in - r_in * math.cos(a), k0[1] - r_in + r_in * math.sin(a))
             for a in [i * math.pi / 20 for i in range(1, 10)]], (k0[0] + r_in, k0[1]), (k1[0] - r_in, k1[1]),
             *[(k1[0] - r_in + r_in * math.cos(a), k1[1] - r_in + r_in * math.sin(a)) for a in [math.pi / 2 - i * math.pi / 20 for i in range(1, 10)]],
             (k1[0], k1[1] - r_in), (w / 2 - bar, z0 - 5)]
    bt = math.radians(d.band_tilt)
    p0 = (0, yf + d.band_setback, z0)
    n = (0, math.cos(bt), -math.sin(bt))
    neg = tuple(-x for x in n)
    opening = prism_y(inset, yf - 200, d.body_d)
    hood = hood.cut(common(opening, halfspace(p0, neg))).removeSplitter()
    back = (0, p0[1] + n[1] * d.band_t, p0[2] + n[2] * d.band_t)
    parts = {"hood": hood, "hood_band": common(opening, halfspace(p0, n), halfspace(back, neg), halfspace((0, 0, z0), (0, 0, 1)))}
    proud = (0, p0[1] - n[1] * 3, p0[2] - n[2] * 3)
    face_slab = common(halfspace(p0, neg), halfspace(proud, n))
    shrink = [(x * (1 - 9 / (w / 2)), z if z > z0 else z0 + 9) for x, z in inset]
    shrink = [(x, min(z, top - d.hood_bar_top - 9)) for x, z in shrink]
    inner_open = prism_y(shrink, yf - 200, d.body_d)
    strip_top = top - d.hood_bar_top - 4
    strip_bottom = strip_top - 12
    for name, sx in (("speaker_left", -1), ("speaker_right", 1)):
        x0, x1 = sorted((sx * 98, sx * w))
        parts[name] = common(inner_open, face_slab, box((x0, -BIG, z0), (x1, BIG, strip_bottom - 5)))
    parts["marquee"] = common(face_slab, box((-80, -BIG, z0 + 14), (80, BIG, strip_bottom - 7)))
    parts["light_strip"] = common(inner_open, face_slab, box((-w, -BIG, strip_bottom), (w, BIG, strip_top)))
    return parts


def focus_points(d: Dims) -> dict[str, list[float]]:
    """Targets and radii of the close-up cameras: the cheek foot, the hood corner and the deck front corner."""
    w = d.width
    su, cu = d.u
    seam_y = d.face((d.body_top - d.deck_top) / cu)[0]
    return {"closeup-cheek-foot": [w / 2 - 20, d.foot_y, d.deck_top + 70, 190.0],
            "closeup-hood-corner": [w / 2 - 70, seam_y + 30, d.body_top + 40, 200.0],
            "closeup-deck-front": [-w / 2 + 120, 70.0, d.deck_top - 15, 210.0]}
