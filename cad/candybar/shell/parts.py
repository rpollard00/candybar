"""The outer-form solids of shell variant D, built with FreeCAD's Part module from the dimensions in dims.py.

Every part is an outer form only: no hollowing, joints or print splits. Most forms are the common of two
extruded profiles (side view and front view), cut by planar half-spaces for facets; the cheek front edge is
one interpolated B-spline, and its outer facet is a chamfer on that edge.
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
    box = Part.makeBox(BIG, BIG, BIG, V(-BIG / 2, -BIG / 2, 0))
    box.Placement = FreeCAD.Placement(V(*point), FreeCAD.Rotation(V(0, 0, 1), n))
    return box


def common(*shapes: Part.Shape) -> Part.Shape:
    out = shapes[0]
    for s in shapes[1:]:
        out = out.common(s)
    return out


def face_from(points: list[tuple[float, float, float]]) -> Part.Face:
    return Part.Face(Part.makePolygon([V(*p) for p in points] + [V(*points[0])]))


def prism_x(yz: list[tuple[float, float]], x0: float, x1: float) -> Part.Shape:
    return face_from([(x0, y, z) for y, z in yz]).extrude(V(x1 - x0, 0, 0))


def prism_y(xz: list[tuple[float, float]], y0: float, y1: float) -> Part.Shape:
    return face_from([(x, y0, z) for x, z in xz]).extrude(V(0, y1 - y0, 0))


def box(lo: tuple[float, float, float], hi: tuple[float, float, float]) -> Part.Shape:
    return Part.makeBox(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2], V(*lo))


def bezier_corner(a: tuple[float, float], k: tuple[float, float], b: tuple[float, float], n: int = 10) -> list[tuple[float, float]]:
    """Quadratic Bezier from a to b with control point k (a tangent-continuous round of the corner k)."""
    out = []
    for i in range(1, n):
        t = i / n
        out.append(tuple((1 - t) ** 2 * a[j] + 2 * t * (1 - t) * k[j] + t ** 2 * b[j] for j in range(2)))
    return out


def toward(p: tuple[float, float], q: tuple[float, float], dist: float) -> tuple[float, float]:
    d = math.dist(p, q)
    return p[0] + (q[0] - p[0]) * dist / d, p[1] + (q[1] - p[1]) * dist / d


def rounded_outline(b0: tuple[float, float], k0: tuple[float, float], k1: tuple[float, float], b1: tuple[float, float],
                    r0: float, r1: float) -> list[tuple[float, float]]:
    """Open polygon b0 - k0 - k1 - b1 with the corners k0 and k1 rounded by Bezier arcs of leg r0 and r1."""
    a0, c0 = toward(k0, b0, r0), toward(k0, k1, r0)
    a1, c1 = toward(k1, k0, r1), toward(k1, b1, r1)
    return [b0, a0, *bezier_corner(a0, k0, c0), c0, a1, *bezier_corner(a1, k1, c1), c1, b1]


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


# ---------- cheek curve and body ----------

def cheek_points(d: Dims) -> tuple[list[FreeCAD.Vector], float]:
    """Points of the cheek front edge in the YZ plane from the deck up to the hood seam, and the top Y."""
    su, cu = d.u
    s_end = (d.body_top - d.deck_top) / cu
    pts = []
    n = 9
    for i in range(n + 1):
        s = d.cheek_sweep_s + (s_end - d.cheek_sweep_s) * i / n
        proj = d.cheek_proj + d.cheek_bulge * math.sin(math.pi * s / s_end)
        y, z = d.face(s)
        pts.append(V(0, y - proj * cu, z + proj * su))
    top = pts[-1]
    # put the last point exactly on the seam height, keeping its distance in front of the face
    top.z = d.body_top
    start = V(0, d.foot_y - d.cheek_reach, d.deck_top)
    return [start, *pts], top.y


def body(d: Dims) -> Part.Shape:
    w = d.width
    pts, top_y = cheek_points(d)
    curve = Part.BSplineCurve()
    curve.interpolate(Points=pts, InitialTangent=V(0, 1, 0), FinalTangent=pts[-1] - pts[-2])
    edges = [curve.toShape()]
    poly = [pts[-1], V(0, d.body_d, d.body_top), V(0, d.body_d, 0), V(0, d.deck_end, 0), V(0, d.deck_end, d.deck_top), pts[0]]
    edges += [Part.makeLine(poly[i], poly[i + 1]) for i in range(len(poly) - 1)]
    face = Part.Face(Part.Wire(edges))
    face.translate(V(-w / 2, 0, 0))
    solid = face.extrude(V(w, 0, 0))
    front = [e for e in solid.Edges if "BSpline" in type(e.Curve).__name__ and abs(abs(e.Vertexes[0].Point.x) - w / 2) < 1e-3]
    try:
        solid = solid.makeChamfer(d.cheek_facet, front)
    except Part.OCCError:
        pass
    # rear body stepped in behind the leaning step line, with a 45 degree facet in plan
    t = math.tan(math.radians(d.step_lean))
    for sx in (1, -1):
        step = common(halfspace((sx * d.rear_w / 2, 0, 0), (sx, 0, 0)), halfspace((sx * w / 2, d.step_y0, 0), (sx, 1, -t)))
        solid = solid.cut(step)
        below = halfspace((0, d.step_y0, 0), (0, 1, -t))
        c = d.rear_facet
        solid = solid.cut(common(halfspace((sx * (d.rear_w / 2 - c), d.body_d, 0), (sx, 1, 0)), below))
        solid = solid.cut(halfspace((sx * (w / 2 - c), d.body_d, 0), (sx, 1, 0)))
    # the screen face recess between the cheeks, down to the back of the bezel plate
    su, cu = d.u
    tan_r = su / cu
    yb = lambda z: d.foot_y + d.bezel_t / cu + (z - d.deck_top) * tan_r
    z_rt = d.face(d.top_s)[1]
    half = d.bezel_w / 2 + d.panel_gap
    solid = solid.cut(prism_x([(-200, d.deck_top), (yb(d.deck_top), d.deck_top), (yb(z_rt), z_rt), (-200, z_rt)], -half, half))
    return solid.removeSplitter()


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
    slots = []
    for i in range(7):
        z = duct_xz[1] - 48 + i * 16
        slots.append(box((duct_xz[0] - 42, D - 9, z), (duct_xz[0] + 42, D + 1, z + 7)))
    for s in slots:
        door = door.cut(s)
        solid = solid.cut(s)
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


# ---------- deck and control panel ----------

def deck(d: Dims) -> tuple[Part.Shape, Part.Shape]:
    w, c, top = d.width, d.deck_corner, d.deck_top
    plan = [(-w / 2, d.deck_end), (-w / 2, c), (-w / 2 + c, 0), (w / 2 - c, 0), (w / 2, c), (w / 2, d.deck_end)]
    solid = face_from([(x, y, 0) for x, y in plan]).extrude(V(0, 0, top))
    edges = [((-w / 2, 0), (-1, 0)), ((-w / 2 + c / 2, c / 2), (-1, -1)), ((0, 0), (0, -1)),
             ((w / 2 - c / 2, c / 2), (1, -1)), ((w / 2, 0), (1, 0))]
    a, b = d.deck_facet_in, d.deck_facet_drop
    for (qx, qy), (mx, my) in edges:
        ml = math.hypot(mx, my)
        mx, my = mx / ml, my / ml
        solid = solid.cut(halfspace((qx, qy, top - b), (mx * b, my * b, a)))
        solid = solid.cut(halfspace((qx, qy, d.deck_crease_z), (mx * d.deck_crease_z, my * d.deck_crease_z, -d.deck_crease_in)))
    py0 = d.deck_nose
    hw = d.panel_w / 2 + d.panel_gap
    pocket = box((-hw, py0, d.panel_top - d.panel_t), (hw, py0 + d.panel_d + 2 * d.panel_gap, top + 1))
    solid = solid.cut(pocket)
    panel = box((-d.panel_w / 2, py0 + d.panel_gap, d.panel_top - d.panel_t), (d.panel_w / 2, py0 + d.panel_gap + d.panel_d, d.panel_top))
    return solid.removeSplitter(), panel


# ---------- screen face: bezel plate, band, screen ----------

def bezel(d: Dims) -> Part.Shape:
    w = d.bezel_w
    plate = box((-w / 2, 0, d.bezel_s0), (w / 2, d.bezel_t, d.bezel_s1))
    cs = d.image_s
    win = rounded_box(MON_ACTIVE_W, d.bezel_t + 2, MON_ACTIVE_H, d.bezel_corner_r, -MON_ACTIVE_W / 2, -1, cs - MON_ACTIVE_H / 2)
    sw = d.bezel_step_w
    step = rounded_box(MON_ACTIVE_W + 2 * sw, d.bezel_step + 1, MON_ACTIVE_H + 2 * sw, d.bezel_corner_r + sw,
                       -MON_ACTIVE_W / 2 - sw, -1, cs - MON_ACTIVE_H / 2 - sw)
    return in_face(plate.cut(win).cut(step).removeSplitter(), d)


def band(d: Dims) -> Part.Shape | None:
    if d.band_len <= 0:
        return None
    w = d.bezel_w
    return in_face(box((-w / 2, 0, 0), (w / 2, d.bezel_t, d.band_len)), d)


def screen(d: Dims) -> Part.Shape:
    cs = d.image_s
    return in_face(box((-MON_ACTIVE_W / 2, d.mon_setback, cs - MON_ACTIVE_H / 2),
                       (MON_ACTIVE_W / 2, d.mon_setback + 1, cs + MON_ACTIVE_H / 2)), d)


# ---------- hood ----------

def hood_outline_front(d: Dims, inset_side: float = 0.0, inset_top: float = 0.0, z_drop: float = 0.0) -> list[tuple[float, float]]:
    hw, h, z0 = d.width / 2, d.hood_h, d.body_top
    lean = d.hood_side_in
    phi = math.atan2(lean, h)
    hw_i = hw - inset_side / math.cos(phi)
    top = z0 + h - inset_top
    lean_i = lean * (top - z0) / h
    r = max(d.hood_corner_r - inset_side * 0.6, 10.0)
    return rounded_outline((-hw_i, z0 - z_drop), (-(hw_i - lean_i), top), (hw_i - lean_i, top), (hw_i, z0 - z_drop), r, r)


def hood_parts(d: Dims, front_y: float) -> dict[str, Part.Shape]:
    z0, h, D = d.body_top, d.hood_h, d.body_d
    top = z0 + h
    yf = front_y - d.hood_overhang
    lf, lr = math.radians(d.hood_lean_front), math.radians(d.hood_lean_rear)
    side = rounded_outline((yf, z0), (yf + h * math.tan(lf), top), (D - h * math.tan(lr), top), (D, z0), d.hood_nose_r, 10.0)
    side = [(yf - 0.01, z0 - 0.01)] + side[1:-1] + [(D + 0.01, z0 - 0.01)]
    outline = hood_outline_front(d)
    hood = common(prism_x(side, -d.width, d.width), prism_y(outline, yf - 50, D + 50))
    inset = hood_outline_front(d, d.hood_bar_side, d.hood_bar_top, 5.0)
    bt = math.radians(d.band_tilt)
    p0 = (0, yf + d.band_setback, z0)
    n = (0, math.cos(bt), -math.sin(bt))
    neg = tuple(-x for x in n)
    opening = prism_y(inset, yf - 100, D)
    hood = hood.cut(common(opening, halfspace(p0, neg)))
    for sx in (1, -1):
        hood = hood.cut(halfspace((sx * (d.width / 2 - d.rear_facet), D, 0), (sx, 1, 0)))
    hood = hood.removeSplitter()
    back = (0, p0[1] + n[1] * d.band_t, p0[2] + n[2] * d.band_t)
    hood_band = common(opening, halfspace(p0, n), halfspace(back, neg), halfspace((0, 0, z0), (0, 0, 1)))
    proud = (0, p0[1] - n[1] * 3, p0[2] - n[2] * 3)
    face_slab = common(halfspace(p0, neg), halfspace(proud, n))
    inner = prism_y(hood_outline_front(d, d.hood_bar_side + 9, d.hood_bar_top + 9, -9.0), yf - 100, D)
    parts = {"hood": hood, "hood_band": hood_band}
    strip_top = top - d.hood_bar_top - 4
    strip_bottom = strip_top - 12
    for name, sx in (("speaker_left", -1), ("speaker_right", 1)):
        x0, x1 = sorted((sx * 98, sx * d.width))
        parts[name] = common(inner, face_slab, box((x0, -BIG, z0), (x1, BIG, strip_bottom - 5)))
    parts["marquee"] = common(face_slab, box((-80, -BIG, z0 + 14), (80, BIG, strip_bottom - 7)))
    # the lit strip runs across the top of the hood band, under the brow, inside the arch contour
    parts["light_strip"] = common(inner, face_slab, box((-d.width, -BIG, strip_bottom), (d.width, BIG, strip_top)))
    return parts
