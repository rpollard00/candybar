"""The outer-form solids of shell variant D, built with FreeCAD's Part module from the dimensions in dims.py.

The front of the cabinet is one side profile (deck front, deck top, one concave bend, the straight screen
face) extruded across the width. One band runs round its outer edge without a break: a soft radius at the
land, a bevel leaning 30 degrees from the side face, then the side face. Along the side chain the band is a
ruled loft between the profile at the inner edge of the bevel and the profile offset inward at the side
plane, so its width is the same everywhere by construction; across the deck front and the flat corner faces
the band is a plane with the same section. The hood is in hood.py.
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
    """Fillet, retrying slightly smaller radii when OCC refuses the nominal one; log what held."""
    if not edges or r <= 0:
        return solid
    for k in (1.0, 0.97, 0.92, 0.85):
        try:
            out = solid.makeFillet(r * k, edges)
        except Part.OCCError:
            continue
        if out.isValid() and out.Volume > 0.9 * solid.Volume:
            log.append(f"{what}: fillet r {r * k:.1f} on {len(edges)} edges held")
            return out
    log.append(f"{what}: fillet failed at r {r} to {r * 0.85:.1f}, skipped")
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


def rail_solid(d: Dims, log: list[str]) -> Part.Shape:
    """The body: its land bends into the deck top, and its wide facet is one plane from the hood to the table."""
    w, top = d.width, d.deck_top
    inner, _ = front_profiles(d)
    ya = d.foot_y - d.bend_t
    body_prof = [("L", (ya, 0.0), (ya, top))] + inner[3:7] + [("L", (d.body_d, 0.0), (ya, 0.0))]
    solid = Part.Face(wire_at(body_prof, -w / 2)).extrude(V(w, 0, 0))
    su, cu = d.u
    xi = w / 2 - d.band_in
    fy, fz = d.face(0.0)
    u3 = V(0, su, cu)
    for sx in (1, -1):
        p0 = V(sx * xi, fy, fz)
        w3 = V(sx * d.band_in, d.band_drop * cu, -d.band_drop * su)
        n = u3.cross(w3)
        if n.dot(V(sx * w / 2, fy, fz) - p0) < 0:
            n = n * -1
        cut = common(halfspace((p0.x, p0.y, p0.z), (n.x, n.y, n.z)), halfspace((sx * xi, 0, 0), (sx, 0, 0)))
        solid = solid.cut(cut)
    solid = solid.removeSplitter()
    front_n = V(0, -cu, su)

    def land(e: Part.Edge) -> bool:
        faces = solid.ancestorsOfType(e, Part.Face)
        if len(faces) != 2 or e.Length < 50:
            return False
        normals = [f.normalAt(*f.Surface.parameter(e.valueAt(e.FirstParameter + 0.5 * (e.LastParameter - e.FirstParameter)))) for f in faces]
        has_front = any(abs(nv.dot(front_n)) > 0.999 for nv in normals)
        has_facet = any(0.3 < abs(nv.x) < 0.95 for nv in normals)
        return has_front and has_facet
    return try_fillet(solid, d.band_r, land_edges(solid, land), log, "rail land radius")


def deck_solid(d: Dims, log: list[str]) -> Part.Shape:
    """The deck: soft vertical corners, then a soft radius over a short, slightly leaning band, then a crease
    and a vertical front face down to a small bottom radius. The same section runs round the corners and sides."""
    w, top, c = d.width, d.deck_top, d.deck_corner
    ya = d.foot_y - d.bend_t
    yr = ya + 30.0
    plan = [(-w / 2, yr), (-w / 2, c), (-w / 2 + c, 0), (w / 2 - c, 0), (w / 2, c), (w / 2, yr)]
    prism = face_from([(x, y, 0) for x, y in plan]).extrude(V(0, 0, top))
    corners = [e for e in prism.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > 1 and
               min(v.Point.y for v in e.Vertexes) < c + 1e-3]
    prism = try_fillet(prism, d.deck_corner_r, corners, log, "deck corner rounds")
    base = min(prism.Faces, key=lambda f: f.CenterOfMass.z)
    zc = top - d.deck_lean_h
    inset = d.deck_lean_h * math.tan(math.radians(d.deck_lean))
    w_low = base.OuterWire.copy()
    w_low.translate(V(0, 0, zc))
    w_top = base.OuterWire.makeOffset2D(-inset)
    w_top.translate(V(0, 0, top))
    lower = Part.Face(base.OuterWire).extrude(V(0, 0, zc))
    upper = Part.makeLoft([w_low, w_top], True, True)
    deck = lower.fuse(upper).removeSplitter()
    top_edges = [e for e in deck.Edges if all(abs(v.Point.z - top) < 1e-3 for v in e.Vertexes)]
    deck = try_fillet(deck, d.deck_top_r, top_edges, log, "deck top radius")
    bottom_edges = [e for e in deck.Edges if all(abs(v.Point.z) < 1e-3 for v in e.Vertexes)]
    deck = try_fillet(deck, d.bottom_r, bottom_edges, log, "deck bottom radius")
    return deck.common(halfspace((0, ya, 0), (0, -1, 0))).removeSplitter()


def body_and_deck(d: Dims, log: list[str]) -> tuple[Part.Shape, Part.Shape, Part.Shape]:
    """(body, deck, control panel)."""
    w = d.width
    solid = rail_solid(d, log)
    t = math.tan(math.radians(d.step_lean))
    for sx in (1, -1):
        step = common(halfspace((sx * d.rear_w / 2, 0, 0), (sx, 0, 0)), halfspace((sx * w / 2, d.step_y0, 0), (sx, 1, -t)))
        solid = solid.cut(step)
        below = halfspace((0, d.step_y0, 0), (0, 1, -t))
        c = d.rear_facet
        solid = solid.cut(common(halfspace((sx * (d.rear_w / 2 - c), d.body_d, 0), (sx, 1, 0)), below))
        solid = solid.cut(halfspace((sx * (w / 2 - c), d.body_d, 0), (sx, 1, 0)))
    half = d.bezel_w / 2 + d.panel_gap
    body = solid.cut(in_face(box((-half, -60.0, d.bezel_s0), (half, d.bezel_t + 2.0, d.bezel_s1)), d)).removeSplitter()
    py0 = d.deck_nose
    hw = d.panel_w / 2 + d.panel_gap
    deck = deck_solid(d, log).cut(box((-hw, py0, d.panel_top - d.panel_t), (hw, py0 + d.panel_d + 2 * d.panel_gap, d.deck_top + 30)))
    panel = box((-d.panel_w / 2, py0 + d.panel_gap, d.panel_top - d.panel_t), (d.panel_w / 2, py0 + d.panel_gap + d.panel_d, d.panel_top))
    return body, deck.removeSplitter(), panel


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


def focus_points(d: Dims) -> dict[str, list[float]]:
    """Targets and radii of the close-up cameras: the cheek foot, the hood corner and the deck front corner."""
    w = d.width
    su, cu = d.u
    seam_y = d.face((d.body_top - d.deck_top) / cu)[0]
    return {"closeup-cheek-foot": [w / 2 - 20, d.foot_y, d.deck_top + 70, 190.0],
            "closeup-hood-corner": [w / 2 - 70, seam_y + 30, d.body_top + 40, 200.0],
            "closeup-deck-front": [-w / 2 + 120, 70.0, d.deck_top - 15, 210.0]}
