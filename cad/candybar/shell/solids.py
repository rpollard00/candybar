"""The outer form of the blueprint (docs/blueprint) as solids, built with FreeCAD's Part module from profiles.py.

Every part is made from the profile paths of profiles.py and the values of dims.Blueprint, with true curves:
  deck         an evolved solid: the edge section carried round the deck outline in plan (offset curves, so the
               rounds stay exact round the corners), cut at the foot of the sweep; a pocket for the control panel.
  body         the side profile extruded across the width, in common with the front outline (with the tuck)
               extruded along the depth. The edge section is cut along the rail: revolutions round the arcs of
               the sweep and of the rail below the tuck; above it, where the section is measured in from the side
               at each height, a loft between sections, on along the tangent over the top. Then the bevel of the
               seam groove (a plane along the whole depth), the step to the rear body, and the recess and reveal
               of the bezel plate. The plane through the outer edge of the step splits front and rear body.
  hood         an evolved solid: the quarter ellipse of the soft edge carried round the front outline, in common
               with the side profile extruded across the width; the bevel of the seam groove (a plane along the
               whole depth), the recess of the opening; the marquee lip and the forms on the hood band as parts
               of their own.
  bezel        the land on a cylinder bezel_drop below the rail arc, a flat back on the screen, the window as a
               ruled loft from the inner edge of the land to the rim and straight on to the screen.

The functions take the profiles as data, so that the same construction can run on offset profiles later.
Run headless, it writes the parts to CANDYBAR_OUT (default cad/out/shell-bp); tools/check_solids.py compares
them with profiles.faces():

    CANDYBAR_OUT=cad/out/shell-bp cad/candybar/freecad-run.sh candybar.shell.solids
"""
from __future__ import annotations

import json
import math
import os
from collections.abc import Callable

import FreeCAD
import MeshPart
import Part

from . import profiles as pr
from .dims import MON_ACTIVE_H, MON_ACTIVE_W, Blueprint

V = FreeCAD.Vector
P2 = pr.P2
Place = Callable[[P2], FreeCAD.Vector]
BIG = 2000.0
OVER = 10.0
TUCK_STATIONS = 24
EDGE_POINTS = 16
OFF_LAND = 0.01
FINISH = {"deck": "white", "control_panel": "black", "front_body": "white", "rear_body": "white", "bezel": "black",
          "screen": "#3a4250", "hood": "white", "marquee_lip": "white", "speaker_left": "black", "speaker_right": "black",
          "logo_form": "#2f4f3a"}


# ---------- paths to edges ----------

def edge(seg: pr.Line | pr.Arc | pr.Conic, place: Place, spline: bool = False) -> Part.Edge:
    """One segment of a profile as an edge. Conics are exact rational B-splines (the boolean check rejects Bezier
    surfaces); spline gives arcs the same form (for evolved solids)."""
    if isinstance(seg, pr.Line):
        return Part.LineSegment(place(seg.p), place(seg.q)).toShape()
    if isinstance(seg, pr.Arc):
        arc = Part.Arc(place(seg.at(seg.a0)), place(seg.at((seg.a0 + seg.a1) / 2)), place(seg.at(seg.a1)))
        return (arc.toBSpline() if spline else arc).toShape()
    curve = Part.BezierCurve()
    curve.setPoles([place(seg.p), place(seg.corner), place(seg.q)])
    curve.setWeight(2, seg.w)
    return curve.toBSpline().toShape()


def wire(path: pr.Path, place: Place, spline: bool = False) -> Part.Wire:
    return Part.Wire([edge(s, place, spline) for s in path])


def ends(seg: pr.Line | pr.Arc | pr.Conic) -> tuple[P2, P2]:
    if isinstance(seg, pr.Arc):
        return seg.at(seg.a0), seg.at(seg.a1)
    return seg.p, seg.q


def reverse(path: pr.Path) -> pr.Path:
    out: pr.Path = []
    for s in reversed(path):
        if isinstance(s, pr.Line):
            out.append(pr.Line(s.q, s.p))
        elif isinstance(s, pr.Arc):
            out.append(pr.Arc(s.c, s.r, s.a1, s.a0))
        else:
            out.append(pr.Conic(s.q, s.corner, s.p, s.w))
    return out


def mirror(path: pr.Path) -> pr.Path:
    """The path seen in a mirror at x = 0 (first coordinate negated)."""
    m = lambda p: (-p[0], p[1])
    out: pr.Path = []
    for s in path:
        if isinstance(s, pr.Line):
            out.append(pr.Line(m(s.p), m(s.q)))
        elif isinstance(s, pr.Arc):
            out.append(pr.Arc(m(s.c), s.r, math.pi - s.a0, math.pi - s.a1))
        else:
            out.append(pr.Conic(m(s.p), m(s.corner), m(s.q), s.w))
    return out


def both_sides(right: pr.Path) -> pr.Path:
    """A path that ends on the centre line, followed by its mirror image back out."""
    return right + reverse(mirror(right))


def closed(path: pr.Path) -> pr.Path:
    a, b = ends(path[-1])[1], ends(path[0])[0]
    return path + ([pr.Line(a, b)] if math.dist(a, b) > 1e-9 else [])


def poly(points: list[P2]) -> pr.Path:
    return [pr.Line(p, q) for p, q in zip(points, points[1:] + points[:1])]


def offset_seg(seg: pr.Line | pr.Arc, by: float) -> pr.Line | pr.Arc:
    """A line or arc moved by a distance to the left of its direction of travel."""
    if isinstance(seg, pr.Arc):
        return pr.Arc(seg.c, seg.r - by if seg.a1 > seg.a0 else seg.r + by, seg.a0, seg.a1)
    (x0, z0), (x1, z1) = seg.p, seg.q
    n = (-(z1 - z0) / math.dist(seg.p, seg.q), (x1 - x0) / math.dist(seg.p, seg.q))
    return pr.Line((x0 + by * n[0], z0 + by * n[1]), (x1 + by * n[0], z1 + by * n[1]))


def from_height(seg: pr.Line | pr.Arc, z: float) -> pr.Line | pr.Arc:
    """The part of a rising line or arc above height z."""
    if isinstance(seg, pr.Arc):
        return pr.Arc(seg.c, seg.r, math.asin((z - seg.c[1]) / seg.r), seg.a1)
    (x0, z0), (x1, z1) = seg.p, seg.q
    return pr.Line((x0 + (x1 - x0) * (z - z0) / (z1 - z0), z), seg.q)


# ---------- solids from planar paths ----------

def xz(y: float) -> Place:
    return lambda p: V(p[0], y, p[1])


def yz(x: float) -> Place:
    return lambda p: V(x, p[0], p[1])


def xy(z: float) -> Place:
    return lambda p: V(p[0], p[1], z)


def prism(path: pr.Path, place: Place, along: FreeCAD.Vector) -> Part.Shape:
    return Part.Face(wire(closed(path), place)).extrude(along)


def across(path: pr.Path) -> Part.Shape:
    """A profile in (y, z) extruded across the whole width."""
    return prism(path, yz(-BIG / 2), V(BIG, 0, 0))


def along(path: pr.Path, y0: float = -OVER, y1: float = BIG) -> Part.Shape:
    """An outline in (x, z) extruded along the depth."""
    return prism(path, xz(y0), V(0, y1 - y0, 0))


def slab(origin: FreeCAD.Vector, u: FreeCAD.Vector, w: FreeCAD.Vector, ur: tuple[float, float], vr: tuple[float, float],
         wr: tuple[float, float]) -> Part.Shape:
    """A box in the frame (x, u, w) at origin: x across, u and w square to x and to each other."""
    at = lambda x, a: origin + V(x, 0, 0) + u * a + w * wr[0]
    face = Part.Face(Part.makePolygon([at(ur[0], vr[0]), at(ur[1], vr[0]), at(ur[1], vr[1]), at(ur[0], vr[1]), at(ur[0], vr[0])]))
    return face.extrude(w * (wr[1] - wr[0]))


def halfspace(point: FreeCAD.Vector, normal: FreeCAD.Vector) -> Part.Shape:
    """The solid region on the side of the plane that the normal points to, as a large box."""
    n = V(normal).normalize()
    box = Part.makeBox(BIG * 2, BIG * 2, BIG, V(-BIG, -BIG, 0))
    box.Placement = FreeCAD.Placement(point, FreeCAD.Rotation(V(0, 0, 1), n))
    return box


def both(shape: Part.Shape) -> Part.Shape:
    """A cutter on the right side, and its mirror image on the left."""
    return shape.fuse(shape.mirror(V(0, 0, 0), V(1, 0, 0)))


def evolved(spine: pr.Path, profile: pr.Path) -> Part.Shape:
    """A profile in (inward, up) carried round a closed outline in (x, y): offset curves, exact round the corners.
    The outline runs counter-clockwise, so that up is +z."""
    loop = closed(spine)
    pts = pr.sample(loop)
    if sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1])) < 0:
        loop = reverse(loop)
    return Part.Face(wire(loop, xy(0.0))).makeEvolved(Profile=wire(profile, lambda p: V(0, p[0], p[1]), spline=True), Join=0,
                                                       AxeProf=True, Solid=True)


def extended(p: P2, q: P2, by: float = OVER) -> tuple[P2, P2]:
    """The ends of a line moved apart along it by a distance each."""
    k = by / math.dist(p, q)
    return (p[0] - (q[0] - p[0]) * k, p[1] - (q[1] - p[1]) * k), (q[0] + (q[0] - p[0]) * k, q[1] + (q[1] - p[1]) * k)


# ---------- the edge section ----------

def edge_profile(d: Blueprint, top: float) -> pr.Path:
    """The side of the deck in (inward, up): upright to the crease, then the edge section to the top flat."""
    lift = lambda path: [pr.Line((s.p[0], top - s.p[1]), (s.q[0], top - s.q[1])) if isinstance(s, pr.Line)
                         else pr.Arc((s.c[0], top - s.c[1]), s.r, -s.a0, -s.a1) for s in path]
    return [pr.Line((0.0, 0.0), (0.0, top - d.deck_lean_h))] + lift(reverse(pr.edge_section(d)))


def edge_cutter_section(d: Blueprint) -> pr.Path:
    """What the edge section takes off a square corner, in (inward, down), with room outside the corner. The band
    runs on past the crease, so that the crease is where the band crosses the side, not an edge laid on it. The
    section stands OFF_LAND out from the land, so that it crosses the land at a small angle and does not lie on
    its tangent."""
    arc, band = pr.edge_section(d)
    out = lambda p: (p[0], p[1] - OFF_LAND)
    arc = pr.Arc(out(arc.c), arc.r, arc.a0, arc.a1)
    (i0, d0), (i1, d1) = out(band.p), out(band.q)
    past = (i1 - OVER / 5, d1 + (d1 - d0) / (i0 - i1) * OVER / 5)
    return [pr.Line((-OVER, -OVER), (d.edge_in, -OVER)), pr.Line((d.edge_in, -OVER), out((d.edge_in, 0.0))), arc, pr.Line((i0, d0), past),
            pr.Line(past, (-OVER, past[1])), pr.Line((-OVER, past[1]), (-OVER, -OVER))]


def station(x_off: float, p: P2, n: P2) -> Place:
    """The section plane at a point of the side profile: inward is -x from x_off, down is n in (y, z)."""
    return lambda q: V(x_off - q[0], p[0] + n[0] * q[1], p[1] + n[1] * q[1])


def tucked(d: Blueprint, p: P2, n: P2) -> Place:
    """The section at a point of the side profile, with inward measured from the side at the height of each point."""
    return lambda q: V(d.side_x(p[1] + n[1] * q[1]) - q[0], p[0] + n[0] * q[1], p[1] + n[1] * q[1])


def warped_wire(path: pr.Path, place: Place, flat: Place) -> Part.Wire:
    """A section through a place that bends it: where it does not bend a segment (the same points as flat), and
    for lines at one depth, the edge stays exact; the rest are splines through points, with the true tangent at
    both ends."""
    edges = []
    for seg in path:
        probe = [seg.p, seg.q] if isinstance(seg, pr.Line) else [seg.at(seg.a0 + (seg.a1 - seg.a0) * k / 4) for k in range(5)]
        if (isinstance(seg, pr.Line) and abs(seg.p[1] - seg.q[1]) < 1e-12) or all((place(q) - flat(q)).Length < 1e-12 for q in probe):
            edges.append(edge(seg, place))
            continue
        if isinstance(seg, pr.Line):
            at = lambda t: (seg.p[0] + (seg.q[0] - seg.p[0]) * t, seg.p[1] + (seg.q[1] - seg.p[1]) * t)
        else:
            at = lambda t: seg.at(seg.a0 + (seg.a1 - seg.a0) * t)
        tangent = lambda t: (place(at(t + 1e-6)) - place(at(t - 1e-6))).normalize()
        curve = Part.BSplineCurve()
        curve.interpolate(Points=[place(at(k / EDGE_POINTS)) for k in range(EDGE_POINTS + 1)], InitialTangent=tangent(0.0), FinalTangent=tangent(1.0))
        edges.append(curve.toShape())
    return Part.Wire(edges)


# ---------- deck ----------

def deck(d: Blueprint) -> tuple[Part.Shape, Part.Shape]:
    """The deck to the foot of the sweep, with the pocket of the control panel; and the control panel plate."""
    plan = pr.deck_plan(d)
    first = plan[0]
    plan = [pr.Line((first.p[0], first.p[1] + OVER * 4), first.q)] + plan[1:]
    solid = evolved(both_sides(plan), edge_profile(d, d.deck_top))
    ya = d.foot_y - d.bend_t
    solid = solid.common(Part.makeBox(BIG, ya + OVER, d.deck_top + OVER, V(-BIG / 2, -OVER, -OVER)))
    px, py0 = d.panel_w / 2 + d.panel_gap, d.deck_nose
    py1 = py0 + d.panel_d + 2 * d.panel_gap
    pocket = Part.makeBox(2 * px, py1 - py0, OVER, V(-px, py0, d.panel_top))
    pw = d.panel_w / 2
    panel = Part.makeBox(2 * pw, d.panel_d, d.panel_t, V(-pw, py0 + d.panel_gap, d.panel_top - d.panel_t))
    return solid.cut([pocket, panel]).removeSplitter(), panel


# ---------- body ----------

def side_path(d: Blueprint, z_top: float) -> pr.Path:
    """The right side of the body seen from the front, in (x, z): upright, then the tuck arc, up to z_top."""
    hw = d.width / 2
    if d.tuck <= 0 or z_top <= d.tuck_z0:
        return [pr.Line((hw, -OVER), (hw, z_top))]
    r = d.tuck_r
    return [pr.Line((hw, -OVER), (hw, d.tuck_z0)), pr.Arc((hw - r, d.tuck_z0), r, 0.0, math.asin((z_top - d.tuck_z0) / r))]


def side_profile(d: Blueprint, fr: pr.Front) -> pr.Path:
    """The body in side view, in (y, z): the sweep, the rail arc, the body top and the rear."""
    ya = d.foot_y - d.bend_t
    rear = pr.rear_profile(d)[1:-1] + [(ya, 0.0)]
    top = fr.rail.at(fr.rail.a1)
    return [pr.Line((ya, 0.0), (ya, d.deck_top)), fr.sweep, fr.rail] + poly([top] + rear)[:-1]


def rail_cutter(d: Blueprint, fr: pr.Front) -> Part.Shape:
    """The edge section along the right rail: revolutions round the sweep and the rail arc below the tuck; where
    the side tucks in, a loft between sections measured in from the side at each height, on along the tangent over
    the body top."""
    sec = edge_cutter_section(d)
    hw = d.width / 2
    sw, rl = fr.sweep, fr.rail
    face_at = lambda x_off, p, n: Part.Face(wire(sec, station(x_off, p, n)))
    rail_n = lambda a: (-math.cos(a), -math.sin(a))
    axis = lambda c: (V(0, c[0], c[1]), V(1, 0, 0))
    start = sw.at(sw.a0)
    pieces = [face_at(hw, start, (0.0, -1.0)).extrude(V(0, -OVER, 0)),
              face_at(hw, start, (0.0, -1.0)).revolve(*axis(sw.c), math.degrees(sw.a1 - sw.a0))]
    top, n_top = rl.at(rl.a1), rail_n(rl.a1)
    up = (math.sin(rl.a1), -math.cos(rl.a1))
    reach = 2 * d.deck_lean_h
    z_s = d.tuck_z0 - d.deck_lean_h / 2
    if d.tuck <= 0 or top[1] <= z_s:
        pieces.append(face_at(hw, rl.at(rl.a0), rail_n(rl.a0)).revolve(*axis(rl.c), math.degrees(rl.a1 - rl.a0)))
        pieces.append(face_at(hw, top, n_top).extrude(V(0, *up) * reach))
        return pieces[0].multiFuse(pieces[1:])
    a_s = math.pi - math.asin((z_s - rl.c[1]) / rl.r)
    arc = [(rl.at(a), rail_n(a)) for a in (a_s + (rl.a1 - a_s) * k / TUCK_STATIONS for k in range(TUCK_STATIONS + 1))]
    tangent = [((top[0] + up[0] * reach * k / 8, top[1] + up[1] * reach * k / 8), n_top) for k in range(1, 9)]
    pieces.append(face_at(hw, rl.at(rl.a0), rail_n(rl.a0)).revolve(*axis(rl.c), math.degrees(a_s - rl.a0)))
    pieces.append(Part.makeLoft([warped_wire(sec, tucked(d, p, n), station(hw, p, n)) for p, n in arc + tangent], True, False))
    return pieces[0].multiFuse(pieces[1:])


def bevel_cutter(d: Blueprint) -> Part.Shape:
    """The bevel of the seam groove on the right side of the body: a plane along the whole depth."""
    a, b = extended(*pr.body_bevel(d))
    far = d.width / 2 + OVER
    return along(poly([a, b, (far, b[1]), (far, a[1])]))


def step_cutter(d: Blueprint) -> Part.Shape:
    """What the step takes off the right side behind the side band: a 45 degree notch in plan, leaning back."""
    top = d.body_top + OVER
    s = d.width / 2 - d.rear_w / 2
    far = d.width / 2 + s + OVER
    sides = side_path(d, top)
    outline = sides + poly([ends(sides[-1])[1], (far, top), (far, -OVER), (d.width / 2, -OVER)])[:-1]
    m = FreeCAD.Matrix()
    m.A23 = math.tan(math.radians(d.step_lean))
    m.A24 = d.step_y0
    leaning = Part.Face(wire(outline, xz(0.0))).transformGeometry(m)
    return leaning.extrude(V(-s, s, 0)).fuse(leaning.translated(V(-s, s, 0)).extrude(V(0, BIG, 0)))


def chord_frame(fr: pr.Front) -> tuple[FreeCAD.Vector, FreeCAD.Vector]:
    """Up the chord of the rail arc, and square to it into the body."""
    r = math.radians(fr.recline)
    return V(0, math.sin(r), math.cos(r)), V(0, math.cos(r), -math.sin(r))


def screen_frame(d: Blueprint) -> tuple[FreeCAD.Vector, FreeCAD.Vector, FreeCAD.Vector]:
    """The flat screen face: origin at s = 0, up the face, and square to it into the body."""
    su, cu = d.u
    return V(0, d.foot_y, d.deck_top), V(0, su, cu), V(0, cu, -su)


def on_screen(d: Blueprint, x: float, s: float, behind: float) -> FreeCAD.Vector:
    o, up, into = screen_frame(d)
    return o + V(x, 0, 0) + up * s + into * behind


def bezel_box(d: Blueprint, fr: pr.Front, x0: float, x1: float) -> Part.Shape:
    """A box across x0..x1 between the planes square to the chord at the foot and at the top of the bezel."""
    up, into = chord_frame(fr)
    t = [V(0, *d.face(s)).dot(up) for s in (d.bezel_s0, d.bezel_s1)]
    return slab(V(0, 0, 0), up, into, (x0, x1), (t[0], t[1]), (-BIG / 4, BIG / 4))


def land_cylinder(d: Blueprint, fr: pr.Front) -> Part.Shape:
    """The solid cylinder of the bezel land: the rail arc, 2 below."""
    return Part.makeCylinder(fr.rail.r - d.bezel_drop, BIG, V(-BIG / 2, *fr.rail.c), V(1, 0, 0))


def behind_screen(d: Blueprint, depth: float) -> Part.Shape:
    """The region more than depth behind the flat screen face."""
    o, up, into = screen_frame(d)
    return halfspace(o + into * depth, into)


def screen(d: Blueprint) -> Part.Shape:
    """The lit image as a thin plate on the screen face (SC1), for the renders."""
    o, up, into = screen_frame(d)
    cs = d.image_s
    return slab(o, up, into, (-MON_ACTIVE_W / 2, MON_ACTIVE_W / 2), (cs - MON_ACTIVE_H / 2, cs + MON_ACTIVE_H / 2), (d.mon_setback, d.mon_setback + d.screen_t))


def body(d: Blueprint, fr: pr.Front) -> tuple[Part.Shape, Part.Shape]:
    """The front body and the rear body, split by the plane of the outer edge of the step."""
    top = d.body_top + OVER
    sides = side_path(d, top)
    end = ends(sides[-1])[1]
    solid = across(side_profile(d, fr)).common(along(both_sides(sides + [pr.Line(end, (0.0, end[1]))])))
    xb = d.bezel_w / 2 + d.panel_gap
    bw = d.bezel_w / 2
    plate = bezel_box(d, fr, -bw, bw).cut(behind_screen(d, d.mon_setback))
    reveal = bezel_box(d, fr, bw, xb).cut(land_cylinder(d, fr))
    cutters = [both(rail_cutter(d, fr)), both(bevel_cutter(d)), both(step_cutter(d)), plate, both(reveal), screen(d)]
    solid = solid.cut(cutters).removeSplitter()
    t = math.tan(math.radians(d.step_lean))
    split = V(0, -1, t).normalize()
    front = solid.common(halfspace(V(0, d.step_y0, 0), split)).removeSplitter()
    rear = solid.common(halfspace(V(0, d.step_y0, 0), -split)).removeSplitter()
    return front, rear


# ---------- bezel ----------

def land_edge(d: Blueprint, fr: pr.Front, x: float, s0: float, s1: float) -> Part.Edge:
    """An arc of the bezel land at x, between two stations of the screen face."""
    pts = [V(x, *fr.on_rail(d, s, d.bezel_drop)) for s in (s0, (s0 + s1) / 2, s1)]
    return Part.Arc(*pts).toShape()


def bezel(d: Blueprint, fr: pr.Front) -> Part.Shape:
    """The bezel plate: the land on the cylinder 2 below the rail arc, a flat back on the screen, and the window:
    the inner frame as a ruled loft from the inner edge of the land to the rim, then the rim wall to the screen."""
    bw, bl = d.bezel_w / 2, d.bezel_land
    plate = bezel_box(d, fr, -bw, bw).common(land_cylinder(d, fr)).cut(behind_screen(d, d.mon_setback))
    xi, s0, s1 = bw - bl, d.bezel_s0 + bl, d.bezel_s1 - bl
    p = lambda x, s: V(x, *fr.on_rail(d, s, d.bezel_drop))
    land = Part.Wire([Part.makeLine(p(-xi, s0), p(xi, s0)), land_edge(d, fr, xi, s0, s1), Part.makeLine(p(xi, s1), p(-xi, s1)),
                      land_edge(d, fr, -xi, s1, s0)])
    w, cs, h = MON_ACTIVE_W / 2, d.image_s, MON_ACTIVE_H / 2
    rect = lambda behind: Part.makePolygon([on_screen(d, x, s, behind) for x, s in ((-w, cs - h), (w, cs - h), (w, cs + h), (-w, cs + h), (-w, cs - h))])
    _, _, into = screen_frame(d)
    front = land.translated(into * -OVER * 2)
    cap = Part.makePolygon([v.Point - into * OVER for v in front.OrderedVertexes] + [front.OrderedVertexes[0].Point - into * OVER])
    window = Part.makeLoft([rect(d.mon_setback + OVER), rect(d.mon_setback - d.bezel_rim), land, front, cap], True, True)
    return plate.cut(window).removeSplitter()


# ---------- hood ----------

def hood_frame(h: pr.Hood) -> Callable[[Part.Shape], Part.Shape]:
    return lambda shape: shape.translated(V(*h.origin))


def opening_path(d: Blueprint, h: pr.Hood) -> pr.Path:
    """The right half of the opening of the cap in (x, z), from the centre of the sill to the centre of the top bar:
    the outline moved in by the top bar, with the round of the bottom corner."""
    side, corner, top = pr.hood_outline(d, h.height, h.half_base)
    r = d.hood_sill_corner_r
    zc = h.z_sill + r
    side_in = from_height(offset_seg(side, d.hood_bar), zc)
    xc = ends(side_in)[0][0]
    round_ = pr.Arc((xc - r, zc), r, -math.pi / 2, 0.0)
    return [pr.Line((0.0, h.z_sill), (xc - r, h.z_sill)), round_, side_in, offset_seg(corner, d.hood_bar), offset_seg(top, d.hood_bar)]


def recess_profile(d: Blueprint, h: pr.Hood) -> list[P2]:
    """How deep the opening goes at each height, in (y, z): ledge, hood band, lip, marquee, soffit."""
    tb, tm = math.tan(math.radians(d.hood_band_tilt)), math.tan(math.radians(d.marquee_tilt))
    return [(-OVER, h.z_sill - OVER), (h.y_band_foot - OVER * tb, h.z_sill - OVER), (h.y_band_top, h.z_band_top),
            (h.y_band_top, h.z_rail_top), (h.y_marquee_bottom, h.z_rail_top), (h.y_marquee_top, h.z_open_top),
            (h.y_marquee_top - OVER * tm, h.z_open_top + OVER), (-OVER, h.z_open_top + OVER)]


def hood_bevel(d: Blueprint, h: pr.Hood) -> Part.Shape:
    """The bevel of the seam groove at the foot of the right side of the cap: a plane along the whole depth."""
    p0, p1 = pr.hood_bevel(d, h)
    a = extended(p0, p1)[0]
    far = h.half_base + OVER
    return along(poly([a, p1, (far, p1[1]), (far, a[1])]), -OVER, h.depth + OVER)


def hood(d: Blueprint) -> dict[str, Part.Shape]:
    """The cap and what stands in its opening, in the cabinet frame."""
    h = pr.hood(d)
    side, corner, top = pr.hood_outline(d, h.height, h.half_base)
    lean = side.a0 if isinstance(side, pr.Arc) else math.atan2(side.p[0] - side.q[0], side.q[1] - side.p[1])
    drop = OVER * 2
    foot = (h.half_base + drop * math.tan(lean), -drop)
    outline = both_sides([pr.Line(foot, (h.half_base, 0.0)), side, corner, top])
    profile = [pr.Conic((d.hood_edge_in, 0.0), (0.0, 0.0), (0.0, d.hood_edge_back)), pr.Line((0.0, d.hood_edge_back), (0.0, h.depth + OVER))]
    shell = evolved(outline, profile)
    turn = FreeCAD.Matrix(-1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0)
    shell = shell.transformed(turn)
    side_view = pr.hood_side_profile(d, h.height, h.depth)
    side_view = [pr.Line((-OVER, 0.0), (-OVER, h.height)), pr.Line((-OVER, h.height), side_view[2].q)] + side_view[3:] + [pr.Line((h.depth, 0.0), (-OVER, 0.0))]
    cap = shell.common(across(side_view))
    opening = prism(both_sides(opening_path(d, h)), xz(-OVER), V(0, BIG / 4, 0))
    recess = opening.common(across(poly(recess_profile(d, h))))
    cap = cap.cut([both(hood_bevel(d, h)), recess]).removeSplitter()
    xr = h.half_open(h.z_band_top, d) + OVER
    lip = Part.makeBox(2 * xr, d.hood_rail_proud, h.z_rail_top - h.z_band_top, V(-xr, h.y_band_top - d.hood_rail_proud, h.z_band_top)).common(opening)
    out = {"hood": cap, "marquee_lip": lip.removeSplitter()}
    out.update(band_forms(d, h))
    return {k: hood_frame(h)(s) for k, s in out.items()}


def band_forms(d: Blueprint, h: pr.Hood) -> dict[str, Part.Shape]:
    """The speaker forms and the logo form: quads on the hood band, raised square to it."""
    tb = math.radians(d.hood_band_tilt)
    up, out = V(0, math.sin(tb), math.cos(tb)), V(0, -math.cos(tb), math.sin(tb))
    origin = V(0, h.y_band_foot, h.z_sill)
    raised = lambda quad, n: Part.Face(Part.makePolygon([origin + V(x, 0, 0) + up * v for x, v in quad + quad[:1]])).extrude(out * n)
    length = (h.z_band_top - h.z_sill) / math.cos(tb)
    v0, v1 = d.speaker_foot_gap, length - d.speaker_head_gap
    leg = lambda v: h.half_width(max(h.z_sill + v * math.cos(tb), h.z_sill + d.hood_sill_corner_r), h.opening) - d.speaker_side_gap
    xi = d.logo_w / 2 + d.logo_gap
    form = [(xi, v0), (leg(v0), v0), (leg(v1), v1), (xi, v1)]
    lw, le = d.logo_w / 2, d.logo_end_gap
    right = raised(form, d.speaker_proud)
    return {"speaker_right": right, "speaker_left": right.mirror(V(0, 0, 0), V(1, 0, 0)),
            "logo_form": raised([(-lw, v0 + le), (lw, v0 + le), (lw, v1 - le), (-lw, v1 - le)], d.logo_proud)}


# ---------- all parts ----------

def build(d: Blueprint) -> dict[str, Part.Shape]:
    """Every part of the outer form, by name, in the cabinet frame."""
    fr = pr.front(d)
    out: dict[str, Part.Shape] = {}
    out["deck"], out["control_panel"] = deck(d)
    out["front_body"], out["rear_body"] = body(d, fr)
    out.update(hood(d))
    out["bezel"] = bezel(d, fr)
    out["screen"] = screen(d)
    return {k: s.Solids[0] if len(s.Solids) == 1 else s for k, s in out.items()}


def focus(d: Blueprint) -> dict[str, dict]:
    """Close-up cameras for render_views.py on the junctions of the form."""
    fr, h = pr.front(d), pr.hood(d)
    a = math.pi - math.asin(((d.tuck_z0 + d.body_top) / 2 - fr.rail.c[1]) / fr.rail.r)
    p = fr.rail.at(a)
    crease = (d.side_x(p[1]), p[0] - math.cos(a) * d.deck_lean_h, p[1] - math.sin(a) * d.deck_lean_h)
    foot = fr.sweep.at(fr.sweep.a1)
    cam = lambda target, radius, az, el: {"target": [round(v, 1) for v in target], "radius": radius, "az": az, "el": el}
    return {"closeup-cheek-foot": cam((d.width / 2 - 6, *foot), 70, 45, 12),
            "closeup-rail-tuck": cam(crease, 40, 70, 10),
            "closeup-rail-top": cam((d.side_x(d.body_top) - 6, d.seam_y + 15, d.body_top - 10), 45, 55, 12),
            "closeup-hood-foot": cam((h.half_base - 5, h.origin[1] + 25, h.origin[2]), 40, 60, 8),
            "closeup-step-top": cam((d.side_x(d.body_top) - d.seam_groove - 6, d.depth - 8, d.body_top - 8), 40, 140, 20),
            "closeup-deck-front": cam((d.width / 2 - 30, 10.0, d.deck_top - 10), 60, -40, 24)}


def export(out: str, parts: dict[str, Part.Shape], d: Blueprint) -> dict:
    os.makedirs(out, exist_ok=True)
    manifest = {}
    for k, s in parts.items():
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.02).write(os.path.join(out, f"{k}.stl"))
        s.exportBrep(os.path.join(out, f"{k}.brep"))
        manifest[k] = {"file": f"{k}.stl", "finish": FINISH[k], "brep": f"{k}.brep"}
    Part.makeCompound(list(parts.values())).exportStep(os.path.join(out, "shell-bp.step"))
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    json.dump(focus(d), open(os.path.join(out, "focus.json"), "w"), indent=1)
    bb = Part.makeCompound(list(parts.values())).BoundBox
    report = {"outside": [round(bb.XLength, 2), round(bb.YLength, 2), round(bb.ZLength, 2)],
              "parts": {k: {"valid": s.isValid(), "solids": len(s.Solids), "volume_mm3": round(s.Volume, 1), "faces": len(s.Faces),
                            "surfaces": sorted({type(f.Surface).__name__ for f in s.Faces})} for k, s in parts.items()},
              "dims": {k: getattr(d, k) for k in d.__dataclass_fields__}}
    json.dump(report, open(os.path.join(out, "report.json"), "w"), indent=1)
    return report


def main() -> int:
    out = os.environ.get("CANDYBAR_OUT", "cad/out/shell-bp")
    d = Blueprint()
    report = export(out, build(d), d)
    for k, r in report["parts"].items():
        print(f"{k:14s} valid {r['valid']}  solids {r['solids']}  volume {r['volume_mm3']:>12.1f}  {', '.join(r['surfaces'])}")
    print("outside", " x ".join(f"{v:.1f}" for v in report["outside"]))
    return 0 if all(r["valid"] and r["solids"] == 1 for r in report["parts"].values()) else 1
