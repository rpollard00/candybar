"""The outer form of the blueprint (docs/blueprint) as solids, built with FreeCAD's Part module from profiles.py.

Every part is made from the profile paths of profiles.py and the values of dims.Blueprint, with true curves:
  deck         an evolved solid: the edge section carried round the deck outline in plan (offset curves, so the
               rounds stay exact round the corners), cut at the foot of the sweep; a pocket for the control panel;
               the base facet round its foot.
  body         the side profile extruded across the width, in common with the front outline (with the tuck)
               extruded along the depth. The edge section is cut along the rail: revolutions round the arcs of
               the sweep and of the rail below the tuck; above it, where the section is measured in from the side
               at each height, a loft between sections, on along the tangent over the top. Then the recess and
               reveal of the bezel plate, and the planar rear (decision record 0007): the band on the rear edge of
               the side (a cut between two offsets of its stroke: flat facets, true planes), the rear shelf and the upper
               rear (a cut by the rear profile across the width), the base facet. The lower rear corner, the hip
               and the mitre of the base facet are rounded by hand (lower_corner_cutter); the other edges of the
               rear get their round from the edge rule (rear_design_edges). Then the bevel of the seam groove, the
               cut-ins, the hand-holds, and the edge break as the last step.
  hood         the front as an evolved solid: the quarter ellipse of the soft edge carried round the front outline,
               made to lean as the side view draws it; behind the soft edge the cap is the front outline extruded
               along the depth, in common with the side profile extruded across the width (exact surfaces). Its
               rear corners have the round of the head's corners. The bevel of the seam groove, the recess of the
               opening; the marquee lip and the forms on the hood band as parts of their own.
  bezel        the land on a cylinder bezel_drop below the rail arc, a flat back on the screen, the window as a
               ruled loft from the inner edge of the land to the rim and straight on to the screen.

The functions take the profiles as data, so that the same construction can run on offset profiles later.
Run headless, it writes the parts to CANDYBAR_OUT (default cad/out/shell-rev7): the BREP and STL of each part,
manifest.json, focus.json (close-up cameras), edges.json (every BREP edge as a polyline, for the edge-drawn renders
of tools/render_views.py) and report.json. tools/check_solids.py compares the parts with profiles.faces(), and
tools/face_check.py checks their faces:

    CANDYBAR_OUT=cad/out/shell-rev7 cad/candybar/freecad-run.sh candybar.shell.solids
"""
from __future__ import annotations

import bisect
import json
import math
import os
from collections.abc import Callable
from dataclasses import dataclass

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
BLEND_SECTIONS = 6
SHEAR_TOL = 1e-3
BEVEL_STEP = 0.5
# a round that is cut by hand along a curved edge (the hood's rear corners): its sections are ROUND_STEP apart or
# less along the edge, found on ROUND_SAMPLES heights, from ROUND_BELOW under the foot to where the edge turns
# ROUND_END (radians). Its arc stands ROUND_OFF out from the true round: it then crosses the two faces at 0.5
# degrees, and it is clear of the edge where the edge turns less than 0.9 degrees
ROUND_STEP = 0.5
ROUND_SAMPLES = 4000
ROUND_BELOW = 5.0
ROUND_OFF = 1e-4
ROUND_END = math.radians(0.7)
# after a cut by several tools, a tool may still hold this share of what it held of the solid, or this volume in mm3
CUT_LEFT = 0.02
CUT_LEFT_MM3 = 0.01
# the edges of the BREP are written to edges.json as polylines with points this far apart
EDGE_STEP = 0.6
FINISH = {"deck": "white", "control_panel": "black", "body": "white", "bezel": "black",
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
    """A path as a wire. An arc of no radius is a sharp corner and makes no edge."""
    return Part.Wire([edge(s, place, spline) for s in path if not (isinstance(s, pr.Arc) and s.r < 1e-9)])


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


def unsplit(shape: Part.Shape) -> Part.Shape:
    """The shape with the faces that a fuse split merged again; the shape as it is when that fails (it can on the
    round of the step's run-out, which the front and the rear body share)."""
    try:
        return shape.removeSplitter()
    except Part.OCCError:
        return shape


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

def deck(d: Blueprint, log: list[str] | None = None) -> tuple[Part.Shape, Part.Shape]:
    """The deck to the foot of the sweep, with the pocket of the control panel, the base facet round its foot and the
    edge break on the rim of the pocket; and the control panel plate."""
    log = log if log is not None else []
    plan = pr.deck_plan(d)
    first = plan[0]
    plan = [pr.Line((first.p[0], first.p[1] + OVER * 4), first.q)] + plan[1:]
    solid = evolved(symmetric(plan), edge_profile(d, d.deck_top))
    ya = d.foot_y - d.bend_t
    solid = solid.common(Part.makeBox(BIG, ya + OVER, d.deck_top + OVER, V(-BIG / 2, -OVER, -OVER)))
    pocket = prism(poly(pr.panel_outline(d, d.panel_gap)), xy(d.panel_top), V(0, 0, OVER))
    panel = prism(poly(pr.panel_outline(d)), xy(d.panel_top - d.panel_t), V(0, 0, d.panel_t))
    solid = solid.cut([pocket, panel]).removeSplitter()
    # the facet takes the front edges of the foot; it runs on along the sides, which are tangent to the front corners
    solid = solid.makeChamfer(d.base_facet, floor_edges(solid, lambda p: p.y < ya - 0.01))
    # the rim of the pocket: the other sharp edges of the deck lie in its joint with the body or under the panel
    rim = sharp_edges(solid, d, lambda m: abs(m.z - d.deck_top) < 1e-3 and m.y < ya - 1.0)
    log.append(f"deck, edge break R {d.edge_break:g}: {len(rim)} edges (the rim of the panel pocket)")
    return break_edges(solid, [e for e, _ in rim], d.edge_break, log, "deck"), panel


# ---------- edges and rounds ----------

def middle(e: Part.Edge) -> FreeCAD.Vector:
    return e.valueAt((e.FirstParameter + e.LastParameter) / 2)


def edges_where(shape: Part.Shape, test: Callable[[FreeCAD.Vector], bool], n: int = 5) -> list[Part.Edge]:
    """The edges of a shape on which n points, evenly spread from end to end, all pass the test."""
    at = lambda e, k: e.valueAt(e.FirstParameter + (e.LastParameter - e.FirstParameter) * k / (n - 1))
    return [e for e in shape.Edges if not e.Degenerated and all(test(at(e, k)) for k in range(n))]


def crease_angle(faces: list[Part.Face], p: FreeCAD.Vector) -> float:
    """Angle in degrees between the normals of two faces at a point of their common edge (0: tangent)."""
    ns = [f.normalAt(*f.Surface.parameter(p)) for f in faces]
    return math.degrees(math.acos(max(-1.0, min(1.0, abs(ns[0].dot(ns[1]))))))


def edge_turn(shape: Part.Shape, e: Part.Edge) -> tuple[bool, float]:
    """(convex, turn in degrees) of an edge between two faces of a solid, at its middle: convex when the first face,
    followed away from the edge, falls behind the second face's outward normal."""
    fs = shape.ancestorsOfType(e, Part.Face)
    m = middle(e)
    t = e.tangentAt((e.FirstParameter + e.LastParameter) / 2)
    n = [f.normalAt(*f.Surface.parameter(m)) for f in fs]
    away = n[0].cross(t)
    away.normalize()
    if fs[0].distToShape(Part.Vertex(m + away * 0.3))[0] > fs[0].distToShape(Part.Vertex(m - away * 0.3))[0]:
        away = -away
    return away.dot(n[1]) < 0, crease_angle(fs, m)


def tight(face: Part.Face, limit: float) -> bool:
    """Whether a face is curved more tightly than the radius `limit` in its middle (a round, not a wall)."""
    u0, u1, v0, v1 = face.ParameterRange
    try:
        k = max(abs(c) for c in face.curvatureAt((u0 + u1) / 2, (v0 + v1) / 2))
    except Exception:
        return False
    return k > 1.0 / limit


def fillet(shape: Part.Shape, edges: list[Part.Edge], radius: Callable[[Part.Edge], float]) -> Part.Shape:
    """A round of radius(edge) on each edge, all in one builder, so that the rounds that meet at a corner are made
    together (a Part::Fillet feature, which takes a radius for each edge)."""
    index: dict[int, int] = {}
    for i, e in enumerate(shape.Edges):
        index.setdefault(e.hashCode(), i + 1)
    doc = FreeCAD.newDocument("fillet")
    try:
        base = doc.addObject("Part::Feature", "base")
        base.Shape = shape
        fl = doc.addObject("Part::Fillet", "fillet")
        fl.Base = base
        fl.Edges = [(index[e.hashCode()], radius(e), radius(e)) for e in edges]
        doc.recompute()
        out = fl.Shape.copy()
    finally:
        FreeCAD.closeDocument(doc.Name)
    if out.isNull() or not out.isValid():
        raise Part.OCCError("the rounds failed")
    return out


def edge_round_cutter(p0: FreeCAD.Vector, p1: FreeCAD.Vector, n1: FreeCAD.Vector, n2: FreeCAD.Vector, r: float, ext0: float = 0.0,
                      ext1: float = 0.0, e: float = 1.0) -> Part.Shape:
    """What a round of radius r takes off a straight convex edge p0-p1 between two planes with outward normals n1, n2:
    the region between the edge and the round's cylinder (reaching e out past both faces), a prism along the edge
    from ext0 before p0 to ext1 past p1. Its walls stand square to the two faces on the lines where the round is
    tangent to them, so the cut gives an exact cylinder that meets both faces with no step."""
    t = p1 - p0
    length = t.Length
    t.normalize()
    n1, n2 = V(n1), V(n2)
    n1.normalize()
    n2.normalize()
    b = -(n1 + n2)
    b.normalize()
    alpha = math.acos(max(-1.0, min(1.0, -n1.dot(n2))))         # the material's angle at the edge
    a0 = p0 - t * ext0 + b * (r / math.sin(alpha / 2))
    t1, t2 = a0 + n1 * r, a0 + n2 * r
    tip, mid = p0 - t * ext0 - b * e, a0 - b * r
    w = Part.Wire([Part.LineSegment(t1 + n1 * e, tip).toShape(), Part.LineSegment(tip, t2 + n2 * e).toShape(),
                   Part.LineSegment(t2 + n2 * e, t2).toShape(), Part.Arc(t2, mid, t1).toShape(), Part.LineSegment(t1, t1 + n1 * e).toShape()])
    return Part.Face(w).extrude(t * (length + ext0 + ext1))


# ---------- body ----------

def side_path(d: Blueprint, z_top: float) -> pr.Path:
    """The right side of the body seen from the front, in (x, z): upright, then the tuck arc, up to z_top."""
    hw = d.width / 2
    if d.tuck <= 0 or z_top <= d.tuck_z0:
        return [pr.Line((hw, -OVER), (hw, z_top))]
    r = d.tuck_r
    return [pr.Line((hw, -OVER), (hw, d.tuck_z0)), pr.Arc((hw - r, d.tuck_z0), r, 0.0, math.asin((z_top - d.tuck_z0) / r))]


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


def outline_at(shape: Part.Shape, z: float) -> Part.Wire:
    """The outer outline where a level plane at height z cuts a solid."""
    return max(shape.slice(V(0, 0, 1), z), key=lambda w: w.BoundBox.DiagonalLength)


def edge_points(loop: Part.Wire) -> list[list[tuple[float, float]]]:
    """The edges of a closed outline as lists of points about BEVEL_STEP apart, in order and counter-clockwise; each
    list starts on the last point of the one before."""
    chain = []
    for e in loop.OrderedEdges:
        chain.append([(p.x, p.y) for p in e.discretize(Number=max(5, math.ceil(e.Length / BEVEL_STEP) + 1))])
    for k, q in enumerate(chain):
        nxt = chain[(k + 1) % len(chain)]
        if min(math.dist(q[-1], nxt[0]), math.dist(q[-1], nxt[-1])) > min(math.dist(q[0], nxt[0]), math.dist(q[0], nxt[-1])):
            chain[k] = q[::-1]
    for k, q in enumerate(chain[1:], 1):
        if math.dist(chain[k - 1][-1], q[0]) > math.dist(chain[k - 1][-1], q[-1]):
            chain[k] = q[::-1]
    pts = [p for q in chain for p in q[:-1]]
    if sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1])) < 0:
        chain = [q[::-1] for q in reversed(chain)]
    for k, q in enumerate(chain):
        q[-1] = chain[(k + 1) % len(chain)][0]
    return chain


def points_wire(chain: list[list[tuple[float, float]]], z: float) -> Part.Wire:
    """Edges through lists of points at height z: a line where the points lie on one, a spline through them elsewhere."""
    edges = []
    for q in chain:
        p = [V(x, y, z) for x, y in q]
        a, b = p[0], p[-1]
        if all(((r - a).cross(b - a)).Length / (b - a).Length < 1e-6 for r in p):
            edges.append(Part.makeLine(a, b))
        else:
            curve = Part.BSplineCurve()
            curve.interpolate(p)
            edges.append(curve.toShape())
    return Part.Wire(edges)


def ring_bevel(loop: Part.Wire, z_edge: float, z_face: float, by: float) -> Part.Shape:
    """What a bevel of one height takes off a part whose outline at z_edge is loop: a slab from a little before z_edge
    to a little past z_face, less the ruled solid that runs in as far as it rises, edge beside edge. It starts a
    little outside the outline, so that it crosses the part's side and does not lie on it. Both of its outlines are
    made from the same points along the edges of the section, moved with pr.inset (the corners meet where the moved
    edges cross), so that the ruled surface pairs them edge for edge."""
    e = OVER / 20
    k = 1.0 if z_face > z_edge else -1.0
    chain = edge_points(loop)
    flat = [p for q in chain for p in q[:-1]]

    def moved(by_: float) -> list[list[tuple[float, float]]]:
        pts, out, i = pr.inset(flat, by_), [], 0
        for q in chain:
            out.append([pts[(i + j) % len(pts)] for j in range(len(q))])
            i += len(q) - 1
        return out

    keep = Part.makeLoft([points_wire(moved(-e), z_edge - k * e), points_wire(moved(by + e), z_face + k * e)], True, True)
    z0, z1 = sorted((z_edge - k * e, z_face + k * e))
    return Part.makeBox(BIG, BIG, z1 - z0, V(-BIG / 2, -BIG / 2, z0)).cut(keep)


def stroke(d: Blueprint) -> pr.Path:
    """The outer edge of the band in side view (profiles.band_stroke) as lines, from below the desk to past the rear."""
    foot, stub, knee, top, end = pr.band_stroke(d)
    return [pr.Line((foot[0], -OVER), stub), pr.Line(stub, knee), pr.Line(knee, top), pr.Line(top, (d.depth + 3 * OVER, end[1]))]


def mitre_offset(path: pr.Path, by: float) -> pr.Path:
    """A path of lines moved by a distance to the left of its direction of travel (negative: to the right). Each
    line is moved, and neighbours are cut where they cross (mitre joins)."""
    moved = [offset_seg(sg, by) for sg in path]

    def cross(l1: pr.Line, l2: pr.Line) -> P2:
        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = l1.p, l1.q, l2.p, l2.q
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(den) < 1e-12:
            return l1.q
        a, c = x1 * y2 - y1 * x2, x3 * y4 - y3 * x4
        return ((a * (x3 - x4) - (x1 - x2) * c) / den, (a * (y3 - y4) - (y1 - y2) * c) / den)

    pts = [moved[0].p] + [cross(moved[i], moved[i + 1]) for i in range(len(moved) - 1)] + [moved[-1].q]
    return [pr.Line(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]


def plane_solid(a: list[FreeCAD.Vector], b: list[FreeCAD.Vector]) -> Part.Shape:
    """The solid between two closed polygons with the same number of corners, whose matching edges are parallel: its
    ends are the polygons, and each side face is a plane through two matching edges. (A ruled loft between the two
    gives the same faces as splines of degree 1, on which OpenCascade's rounds become splines with loose curves.)"""
    ring = lambda pts: Part.Face(Part.makePolygon(pts + pts[:1]))
    faces = [ring(a), ring(b)] + [ring([a[i], a[(i + 1) % len(a)], b[(i + 1) % len(a)], b[i]]) for i in range(len(a))]
    shell = Part.makeShell(faces)
    shell.sewShape()
    solid = Part.makeSolid(shell)
    if solid.Volume < 0:
        solid.reverse()
    return solid


def band_cutter(d: Blueprint) -> Part.Shape:
    """What the band takes off the right side: the region outside the side of the lower body (x > rear_w / 2) and
    behind or below the band. That region lies between its sections at x = W + e and x = rear_w / 2 - e: the region
    behind the stroke, moved by the stroke's offset at that x (the band runs in by one for each one it runs back or
    down, square to the stroke). Matching edges of the two sections are parallel, so each piece of the band is a
    plane."""
    path = stroke(d)
    hw, a, e = d.width / 2, d.rear_w / 2, OVER / 10

    def section(x: float) -> list[FreeCAD.Vector]:
        moved = mitre_offset(path, -(hw - x))
        start, end = ends(moved[0])[0], ends(moved[-1])[1]
        return [V(x, *p) for p in [start] + [ends(sg)[1] for sg in moved] + [(end[0], -OVER)]]

    behind = plane_solid(section(hw + e), section(a - e))
    return halfspace(V(a, 0, 0), V(1, 0, 0)).common(behind)


def rear_cutter(d: Blueprint) -> Part.Shape:
    """What the rear profile takes off a plain rear wall at the full depth: the region behind the upper rear wall,
    the rear facet of the shelf and the lower rear wall, across the whole width."""
    far, lo, hi = d.depth + 3 * OVER, -3 * OVER, d.body_top + 3 * OVER
    region = poly([(d.depth, hi), (d.depth, d.rear_step_z1), (d.body_d, d.rear_step_z0), (d.body_d, lo), (far, lo), (far, hi)])
    return prism(region, yz(-BIG / 2), V(BIG, 0, 0))


def sharp_body(d: Blueprint, fr: pr.Front) -> Part.Shape:
    """The body as one solid with every edge of the rear sharp: the side profile with a plain rear wall, in common
    with the front outline (with the tuck); less the edge section along the rail, the band, the recess and reveal of
    the bezel plate, and the rear profile."""
    top = d.body_top + OVER
    sides = side_path(d, top)
    end = ends(sides[-1])[1]
    ya = d.foot_y - d.bend_t
    rail_top = fr.rail.at(fr.rail.a1)
    profile = [pr.Line((ya, 0.0), (ya, d.deck_top)), fr.sweep, fr.rail] + poly([rail_top, (d.depth, d.body_top), (d.depth, 0.0), (ya, 0.0)])[:-1]
    solid = across(profile).common(along(both_sides(sides + [pr.Line(end, (0.0, end[1]))])))
    xb = d.bezel_w / 2 + d.panel_gap
    bw = d.bezel_w / 2
    plate = bezel_box(d, fr, -bw, bw).cut(behind_screen(d, d.mon_setback))
    reveal = bezel_box(d, fr, bw, xb).cut(land_cylinder(d, fr))
    cutters = [both(rail_cutter(d, fr)), both(band_cutter(d)), plate, both(reveal), screen(d), rear_cutter(d)]
    return solid.cut(cutters).removeSplitter()


def floor_edges(shape: Part.Shape, test: Callable[[FreeCAD.Vector], bool]) -> list[Part.Edge]:
    """The edges of a shape that lie on the desk, where their two ends and their middle pass the test."""
    return edges_where(shape, lambda p: abs(p.z) < 1e-4 and test(p), 3)


def lower_corner_cutter(d: Blueprint) -> Part.Shape:
    """What the rounds of the two lower rear corners take off, made by hand so that they meet exactly. The hip
    (between the two 45 degree facets of the shelf) and the mitre of the base facet (between two faces of the base
    facet, parallel to those of the shelf) get a round of rear_corner_r (R). Each of these rounds, cut by a level
    plane, is an ellipse: centre (a - 2 r, y0 - 2 r) with r = R / sqrt(2), semi-axes sqrt(3) R along the diagonal and
    R across, tangent to both walls at r from the corner. The upright corner between them is that ellipse carried
    straight up, so it meets the round of the hip and the round of the mitre on the same curve: no ledge and no
    needle. (A circular round of r there meets the creases at the same points, but it stands up to 0.035 r proud of
    the hip's round between them.)"""
    a, y0, zc, ch = d.rear_w / 2, d.body_d, d.rear_step_z0, d.base_facet
    big, k = 4000.0, math.sqrt(0.5)
    big_r = d.rear_corner_r
    rr = big_r / math.sqrt(2)
    level = lambda z0, z1: Part.makeBox(big, big, z1 - z0, V(-big / 2, -big / 2, z0))
    out = []
    for sx in (1, -1):
        X = lambda p: V(sx * p.x, p.y, p.z)
        hip_top = V(d.width / 2, y0 + d.width / 2 - a, zc + d.width / 2 - a)
        hip = edge_round_cutter(X(V(a, y0, zc)), X(hip_top), V(sx * k, 0, -k), V(0, k, -k), big_r, 3.0, 5.0)
        mitre = edge_round_cutter(X(V(a, y0, ch)), X(V(a - ch, y0 - ch, 0)), V(sx * k, 0, -k), V(0, k, -k), big_r, 3.0, 2.0)
        o = V(sx * (a - 2 * rr), y0 - 2 * rr, ch)
        ell = Part.Ellipse(o + V(sx * k, k, 0) * (math.sqrt(3) * big_r), o + V(-sx * k, k, 0) * big_r, o)
        ps, pr_ = V(sx * a, y0 - rr, ch), V(sx * (a - rr), y0, ch)
        u0, u1 = sorted((ell.parameter(ps), ell.parameter(pr_)))
        arc = ell.toShape(u0, u1) if u1 - u0 < math.pi else ell.toShape(u1, u0 + 2 * math.pi)   # the short arc, toward the corner
        q0, q1 = arc.Vertexes[0].Point, arc.Vertexes[-1].Point
        out0 = lambda q: q + (V(sx, 0, 0) if abs(abs(q.x) - a) < 1e-6 else V(0, 1, 0))
        corner = V(sx * (a + 1), y0 + 1, ch)
        w = Part.Wire([arc, Part.LineSegment(q1, out0(q1)).toShape(), Part.LineSegment(out0(q1), corner).toShape(),
                       Part.LineSegment(corner, out0(q0)).toShape(), Part.LineSegment(out0(q0), q0).toShape()])
        column = Part.Face(w).extrude(V(0, 0, zc - ch))
        out += [column, hip.common(level(zc, big)), mitre.common(level(-OVER, ch))]
    return out[0].fuse(out[1:]).removeSplitter()


def behind_band(d: Blueprint, p: FreeCAD.Vector) -> bool:
    """Whether a point belongs to the rear of the body: behind the line of the band's lean, or on the rear."""
    return p.y > d.step_y(p.z) - 1 or p.y > d.body_d - 1


def rear_design_edges(shape: Part.Shape, d: Blueprint) -> list[Part.Edge]:
    """The edges of the rear that the edge rule gives the design round: convex, a turn of edge_min_turn or more,
    behind the band or on the rear, above the base facet and below the body top. They are the outer edge of the
    band, the edge where the rear facet of the shelf ends on the side band, the lower edge of the upper rear wall
    and the upright rear corners of the head. The lower rear corner is not taken: lower_corner_cutter has made it."""
    rw, y0, zc = d.rear_w / 2, d.body_d, d.rear_step_z0
    out = []
    for e in shape.Edges:
        if e.Degenerated:
            continue
        m, b = middle(e), e.BoundBox
        if b.ZMax < d.base_facet + 0.01 + 1e-3 or b.ZMin > d.body_top - 0.5 or not behind_band(d, m):
            continue
        if abs(abs(m.x) - rw) < 4 and abs(m.y - y0) < 4 and m.z < zc + 0.5:      # the corner column, made by hand
            continue
        fs = shape.ancestorsOfType(e, Part.Face)
        if len(fs) != 2 or crease_angle(fs, m) <= 5.0:
            continue
        convex, turn = edge_turn(shape, e)
        if convex and turn >= d.edge_min_turn:
            out.append(e)
    return out


def cut_in_cutter(d: Blueprint) -> Part.Shape:
    """The right row of cut-ins, milled by a ball whose centre keeps one distance dc outside the surface all the way:
    its path is the offset of the body's plan outline at the groove's height (the rear line, the ellipse of the lower
    corner's column, the side line). Thus the lips are level lines at sqrt(R^2 - dc^2) = h / 2 above and below the
    path, on the legs and round the corner alike, and the floor is the outline moved in by the depth.

    Built as a sweep of the groove's own section (the ball's arc inside the wall, closed by a chord 1 outside) along
    the outline, the section kept upright (binormal z) and square to the outline: the outline sampled every 0.1 and
    approximated by one B-spline (deviation under 0.002), so each groove is one face from end to end. A sweep of the
    whole ball along a path twisted on the near-straight parts and crossed itself. The depth must stay under the
    smallest radius of the outline (the ellipse's R / sqrt(3), 1.73 for R 3), else the floor would cross itself at
    the corner; the floor turns on that radius minus the depth. A sphere at each end (round ends)."""
    a, y0, h = d.rear_w / 2, d.body_d, d.cut_in_h
    dep = d.cut_in_depth
    dc = (h * h / 4 / dep - dep) / 2                    # the centre's distance outside the surface
    rho = dc + dep                                      # the ball
    big_r = d.rear_corner_r
    rr, k = big_r / math.sqrt(2), math.sqrt(0.5)
    end = h / 2                                         # the slot reaches this far past the ball's last centre
    out = []
    for i in range(d.cut_in_count):
        z = d.cut_in_z0 + i * d.cut_in_pitch + h / 2
        o = V(a - 2 * rr, y0 - 2 * rr, z)
        ell = Part.Ellipse(o + V(k, k, 0) * (math.sqrt(3) * big_r), o + V(-k, k, 0) * big_r, o)
        u0, u1 = sorted((ell.parameter(V(a, y0 - rr, z)), ell.parameter(V(a - rr, y0, z))))
        if u1 - u0 > math.pi:
            u0, u1 = u1, u0 + 2 * math.pi
        arc = ell.toShape(u0, u1).discretize(Distance=0.05)
        pr0, pr1 = V(a - d.cut_in_rear + end, y0, z), V(a - rr, y0, z)
        ps0, ps1 = V(a, y0 - rr, z), V(a, y0 - d.cut_in_side + end, z)
        if (arc[0] - pr1).Length > 1e-3:
            arc = arc[::-1]
        n0, n1 = int((pr1 - pr0).Length / 0.1), int((ps1 - ps0).Length / 0.1)
        pts = [pr0 + (pr1 - pr0) * (j / n0) for j in range(n0)] + arc[:-1] + [ps0 + (ps1 - ps0) * (j / n1) for j in range(n1 + 1)]
        sp = Part.BSplineCurve()
        sp.approximate(Points=pts, DegMin=3, DegMax=5, Tolerance=0.002, Continuity="C2")
        q0, q1 = sp.value(sp.FirstParameter), sp.value(sp.LastParameter)
        t0 = sp.tangent(sp.FirstParameter)[0]
        nrm = V(-t0.y, t0.x, 0)
        if nrm.y < 0:
            nrm = -nrm
        at = lambda n_, dz: q0 + nrm * n_ + V(0, 0, dz)  # noqa: E731
        cz = math.sqrt(rho * rho - (1 - dc) ** 2)
        section = Part.Wire([Part.Arc(at(1, cz), at(-dep, 0), at(1, -cz)).toShape(), Part.LineSegment(at(1, -cz), at(1, cz)).toShape()])
        mk = Part.BRepOffsetAPI.MakePipeShell(Part.Wire([sp.toShape()]))
        mk.setBiNormalMode(V(0, 0, 1))
        mk.add(section, False, False)
        mk.build()
        mk.makeSolid()
        groove = mk.shape()
        groove = groove if groove.ShapeType == "Solid" else groove.Solids[0]
        out.append(groove.fuse([Part.makeSphere(rho, q0 + nrm * dc), Part.makeSphere(rho, q1 + V(dc, 0, 0))]).removeSplitter())
    return out[0].fuse(out[1:]).removeSplitter()


def hand_hold_cutter(d: Blueprint) -> Part.Shape:
    """The right hand-hold: in side view an opening of grip_h in the upper rear wall, a roof that runs down inward at
    45 degrees, a back wall grip_depth in, a level floor; across, from grip_x0 to grip_x1 with round ends of
    grip_end_r in plan. Every edge of it that lies inside the wall is rounded on the cutter: grip_r, and
    grip_roof_r on the roof's edges (with R 8 there, the blend of the 45 degree roof and the round end dips to 43.8
    degrees; with R 3 it holds 45.0). The edges where the cutter passes through the rear wall are not touched: the rim
    gets the edge break with the rest of the body."""
    x0, x1, z0 = d.grip_x0, d.grip_x1, d.grip_z0
    y_out, y_in = d.depth + OVER, d.depth - d.grip_depth
    zt = z0 + d.grip_h
    prof = poly([(y_out, z0), (y_in, z0), (y_in, zt - d.grip_depth), (d.depth, zt), (y_out, zt)])
    block = prism(prof, yz(x0), V(x1 - x0, 0, 0))
    r, top = d.grip_end_r, d.body_top + OVER
    plan = Part.makeBox(x1 - x0 - 2 * r, OVER * 4, top, V(x0 + r, y_in - 1, 0)).fuse(
        [Part.makeCylinder(r, top, V(x0 + r, y_in + r, 0)), Part.makeCylinder(r, top, V(x1 - r, y_in + r, 0)),
         Part.makeBox(x1 - x0, OVER * 4, top, V(x0, y_in + r, 0))])
    cutter = block.common(plan).removeSplitter()
    faces_of = lambda e: cutter.ancestorsOfType(e, Part.Face)
    inside = [e for e in cutter.Edges if not e.Degenerated and e.BoundBox.YMax < d.depth - 0.5 and len(faces_of(e)) == 2
              and crease_angle(faces_of(e), middle(e)) > 5.0]
    on_roof = lambda e: any(isinstance(f.Surface, Part.Plane) and abs(f.normalAt(0, 0).z - math.sqrt(0.5)) < 1e-3 for f in faces_of(e))
    return fillet(cutter, inside, lambda e: d.grip_roof_r if on_roof(e) else d.grip_r)


def hand_hold_rim(shape: Part.Shape, d: Blueprint) -> list[Part.Edge]:
    """Every edge of the two hand-hold openings on the rear wall of the head."""
    out = []
    for e in shape.Edges:
        b = e.BoundBox
        if abs(b.YMin - d.depth) < 1e-3 and abs(b.YMax - d.depth) < 1e-3 and d.grip_x0 - 1 < abs(b.Center.x) < d.grip_x1 + 1 \
                and d.grip_z0 - 1 < b.Center.z < d.grip_z0 + d.grip_h + 1:
            out.append(e)
    return out


def sharp_edges(shape: Part.Shape, d: Blueprint, where: Callable[[FreeCAD.Vector], bool]) -> list[tuple[Part.Edge, str]]:
    """Every convex edge of a solid, with its middle where `where` holds, that turns more than edge_break_turn, with
    its class: "beside a round" when one of its faces is a round (the edge itself is still sharp: where the lip of a
    cut-in crosses the corner round, where the base facet meets the corner column), else "sharp". The edges that
    the design rounds are faces now, not in the list. An edge that turns less is blunt and gets no finish."""
    out = []
    for e in shape.Edges:
        if e.Degenerated or not where(middle(e)):
            continue
        fs = shape.ancestorsOfType(e, Part.Face)
        if len(fs) != 2:
            continue
        convex, turn = edge_turn(shape, e)
        if convex and turn > d.edge_break_turn:
            out.append((e, "beside a round" if any(not isinstance(f.Surface, Part.Plane) and tight(f, 30.0) for f in fs) else "sharp"))
    return out


def rear_break_edges(shape: Part.Shape, d: Blueprint) -> list[tuple[Part.Edge, str]]:
    """The edges of the rear of the body that get the edge break: every sharp convex edge behind the band or on the
    rear (sharp_edges), and the rims of the hand-holds all the way round ("rim": the top edge of a rim turns only 45
    degrees, at the roof, and the edges along the rounds inside border a round but are sharp themselves)."""
    out = sharp_edges(shape, d, lambda m: behind_band(d, m))
    seen = {e.hashCode() for e, kind in out if kind == "sharp"}
    for e in hand_hold_rim(shape, d):
        if e.hashCode() not in seen:
            out = [(x, kind) for x, kind in out if not x.isSame(e)] + [(e, "rim")]
    return out


def bevel_crossings(listed: list[tuple[Part.Edge, str]], in_groove: Callable[[FreeCAD.Vector], bool]) -> tuple[list[tuple[Part.Edge, str]], list[Part.Edge]]:
    """The listed edges without those where the seam bevel crosses a corner round (an edge beside a round, in the seam
    groove); and those edges, in one order. Such an edge is a few mm long. It continues the upper or lower edge of the
    bevel, which is blunt on the walls, and turns a little more on the round. The edge break on it is a valid solid in
    some runs and not in others, so it gets none: the build must be the same in every run."""
    crossing = [e for e, kind in listed if kind == "beside a round" and in_groove(middle(e))]
    kept = [(e, kind) for e, kind in listed if not any(e.isSame(x) for x in crossing)]
    return kept, sorted(crossing, key=lambda e: (round(abs(middle(e).x), 1), middle(e).x < 0))


def where(e: Part.Edge) -> str:
    m = middle(e)
    return f"({m.x:.1f}, {m.y:.1f}, {m.z:.1f}), {e.Length:.1f} long"


def break_edges(shape: Part.Shape, edges: list[Part.Edge], radius: float, log: list[str], what: str) -> Part.Shape:
    """A round of `radius` on the edges of a symmetric solid: the edge break. All edges in one call, when that gives
    one valid solid. If not, the edges are taken in groups of edges that touch each other (a chain cannot be made
    edge by edge). A group that does not build loses the one pair of edges (an edge and the edge that mirrors it, so
    that both sides stay the same) without which it builds; if no one pair does that, the whole group stays sharp.
    log names the edges that stay sharp. The rest is made in one call. The number of tries is at most one for each
    pair of edges and two for each group."""
    good = lambda s: not s.isNull() and s.isValid() and len(s.Solids) == 1

    def made(units: list[list[Part.Edge]]) -> Part.Shape | None:
        if not units:
            return shape
        try:
            out = shape.makeFillet(radius, [e for u in units for e in u])
        except Part.OCCError:
            return None
        return out if good(out) else None

    if not edges:
        return shape
    # one order of the edges in every run (OpenCascade lists the edges of a shape in an order that changes from run
    # to run, and the round it makes depends on the order in which it gets them): by place, right side first
    place = lambda e: (round(middle(e).z, 2), round(middle(e).y, 2), round(abs(middle(e).x), 2), middle(e).x < 0, round(e.Length, 2))
    edges = sorted(edges, key=place)
    # an edge and the edge that mirrors it are one unit
    units: list[list[Part.Edge]] = []
    for e in edges:
        m = middle(e)
        twin = next((u for u in units if abs(m.x) > 0.05 and (middle(u[0]) - V(-m.x, m.y, m.z)).Length < 0.05), None)
        if twin is not None:
            twin.append(e)
        else:
            units.append([e])
    out = made(units)
    if out is not None:
        return out
    # the groups: units whose edges share a corner
    corners = lambda u: {(round(v.Point.x, 3), round(v.Point.y, 3), round(v.Point.z, 3)) for e in u for v in e.Vertexes}
    groups: list[tuple[set, list[list[Part.Edge]]]] = []
    for u in units:
        pts, members = corners(u), [u]
        for g in [g for g in groups if g[0] & pts]:
            groups.remove(g)
            pts |= g[0]
            members = g[1] + members
        groups.append((pts, members))
    kept, sharp = [], []
    for _, members in groups:
        if made(members) is not None:
            kept += members
            continue
        one = next((u for u in sorted(members, key=lambda u: u[0].Length) if made([x for x in members if x is not u]) is not None), None)
        gone = [one] if one is not None else members
        kept += [u for u in members if not any(u is x for x in gone)]
        sharp += gone
    out = made(kept)
    if out is None:
        raise Part.OCCError(f"{what}: the edge break of R {radius:g} does not build, also without the {len(sharp)} pairs of edges that fail in their groups")
    for u in sharp:
        places = " and ".join(where(e) for e in u)
        log.append(f"{what}: no edge break at {places}: with it, the round of R {radius:g} on the edges that touch it is not a valid solid; "
                   f"{'they stay' if len(u) > 1 else 'it stays'} sharp")
    return out


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


def body(d: Blueprint, fr: pr.Front, log: list[str] | None = None) -> Part.Shape:
    """The body: the sharp form, the base facet on its sharp corners (it mitres), the lower rear corners by hand, the
    design round on the edges of the rear (all in one builder, so that the rounds that meet at a corner are made
    together), the bevel of the seam groove, the cut-ins, the hand-holds, and the edge break last.

    The bevel of the seam groove is the one of the sharp form: it is lofted through points of the outline 3 below
    the body top, and it cannot follow a small round there. Cut after the rounds, it takes the top of the head's
    corner rounds, which run out in it."""
    log = log if log is not None else []
    ya = d.foot_y - d.bend_t
    sharp = sharp_body(d, fr)
    g = d.seam_groove
    bevel = ring_bevel(outline_at(sharp, d.body_top - g), d.body_top - g, d.body_top, g)
    es = floor_edges(sharp, lambda p: p.y > ya + 0.01)
    log.append(f"body, base facet {d.base_facet:g}: {len(es)} edges")
    s = sharp.makeChamfer(d.base_facet, es)
    s = s.cut(lower_corner_cutter(d))
    r = d.rear_corner_r
    log.append(f"body, lower rear corners by hand: hip and mitre of the base facet R {r:g}, the column on their ellipse "
               f"({math.sqrt(3) * r:.2f} x {r:g}, tangent at {r / math.sqrt(2):.2f} from the corner)")
    es = rear_design_edges(s, d)
    log.append(f"body, design rounds R {r:g}: {len(es)} edges")
    s = s.makeFillet(r, es).removeSplitter()
    s = s.cut(bevel)
    if not s.isValid():
        s.fix(1e-7, 1e-7, 1e-7)
        log.append(f"body, seam bevel: shape fixed (valid {s.isValid()})")
    s = s.cut(both(cut_in_cutter(d)))
    s = s.cut(both(hand_hold_cutter(d)))
    s = s.removeSplitter()
    listed = rear_break_edges(s, d)
    count = lambda kind: sum(1 for _, k in listed if k == kind)
    log.append(f"body, edge break R {d.edge_break:g} at the rear: {len(listed)} edges ({count('rim')} on the rims of the hand-holds, "
               f"{count('beside a round')} beside a round, {count('sharp')} others)")
    # in front of the band the sharp edges that show are the two edges of the rail land along the reveal of the bezel
    # plate, and the floor edge of each side (the base facet does not run there). The others lie in a joint: against
    # the deck, under the bezel plate, in the seam under the hood
    xb = d.bezel_w / 2 + d.panel_gap
    reveal = lambda m: abs(abs(m.x) - xb) < 1e-3 and abs(math.dist((m.y, m.z), fr.rail.c) - fr.rail.r) < 1e-3
    front = sharp_edges(s, d, lambda m: not behind_band(d, m) and (reveal(m) or (m.z < 1e-3 and m.y > ya + 0.01)))
    log.append(f"body, edge break R {d.edge_break:g} at the front: {len(front)} edges ({sum(1 for e, _ in front if reveal(middle(e)))} of the rail land "
               f"along the bezel reveal, {sum(1 for e, _ in front if not reveal(middle(e)))} floor edges of the sides)")
    listed, crossing = bevel_crossings(listed, lambda m: m.z > d.body_top - g - 0.5)
    log += [f"body: no edge break at {where(e)}, where the seam bevel crosses the round of the head's corner; it stays sharp" for e in crossing]
    return break_edges(s, [e for e, _ in listed + front], d.edge_break, log, "body")


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
    pts = [(-OVER, h.z_sill - OVER), (h.y_band_foot - OVER * tb, h.z_sill - OVER), (h.y_band_top, h.z_band_top),
           (h.y_band_top, h.z_rail_top), (h.y_marquee_bottom, h.z_rail_top), (h.y_marquee_top, h.z_open_top),
           (h.y_marquee_top - OVER * tm, h.z_open_top + OVER), (-OVER, h.z_open_top + OVER)]
    return [p for p, q in zip(pts, pts[-1:] + pts[:-1]) if math.dist(p, q) > 1e-9]


def leaning(shell: Part.Shape, h: pr.Hood, d: Blueprint) -> Part.Shape:
    """The cap with its front leaning back as the side view draws it: each height of the shell moved back by the
    front's lean there. Below and above the blend this is a shear of the shell; through the blend, a loft between
    its level sections, each moved back as far as the front. The edges of a sheared shape get a tolerance of
    SHEAR_TOL, as their curves no longer lie exactly on the converted faces."""
    za, zb = h.front[0].q[1], h.front[2].p[1]
    t0, t1 = (math.tan(math.radians(a)) for a in (d.hood_front_lean_low, d.hood_front_lean_up))
    low, up = FreeCAD.Matrix(), FreeCAD.Matrix()
    low.A23, up.A23, up.A24 = t0, t1, h.front_y(zb) - zb * t1
    level = lambda z0, z1: Part.makeBox(BIG, BIG, z1 - z0, V(-BIG / 2, -BIG / 2, z0))
    lower = shell.common(level(-OVER / 20, za)).transformGeometry(low)
    upper = shell.common(level(zb, BIG / 4)).transformGeometry(up)
    for part in (lower, upper):
        part.fixTolerance(SHEAR_TOL)
    zs = [za + (zb - za) * k / BLEND_SECTIONS for k in range(BLEND_SECTIONS + 1)]
    blend = Part.makeLoft([outline_at(shell, z).translated(V(0, h.front_y(z), 0)) for z in zs], True, False)
    return lower.fuse([blend, upper]).removeSplitter()


def symmetric(right: pr.Path) -> pr.Path:
    """A path whose last segment is a line to the centre line, square to it, followed by its mirror image back out.
    The two halves of that line are one line, so that the surface made from it is one face across the centre line."""
    last = right[-1]
    return right[:-1] + [pr.Line(last.p, (-last.p[0], last.p[1]))] + reverse(mirror(right[:-1]))


def cap_outline(d: Blueprint, h: pr.Hood) -> pr.Path:
    """The cap seen from the front, in (x, z), from below its foot: both sides, the top corners and the top."""
    side, corner, top = pr.hood_outline(d, h.height, h.half_base)
    lean = side.a0 if isinstance(side, pr.Arc) else math.atan2(side.p[0] - side.q[0], side.q[1] - side.p[1])
    drop = OVER * 2
    foot = (h.half_base + drop * math.tan(lean), -drop)
    return symmetric([pr.Line(foot, (h.half_base, 0.0)), side, corner, top])


def lean_line(h: pr.Hood, back: float, z0: float, z1: float) -> pr.Path:
    """The front of the cap in side view, in (y, z), moved back by `back`: its lower line from z0, the blend, its
    upper line to z1."""
    def moved(seg: pr.Line | pr.Arc) -> pr.Line | pr.Arc:
        if isinstance(seg, pr.Line):
            return pr.Line((seg.p[0] + back, seg.p[1]), (seg.q[0] + back, seg.q[1]))
        return pr.Arc((seg.c[0] + back, seg.c[1]), seg.r, seg.a0, seg.a1)

    low, blend, up = (moved(s) for s in h.front)
    at = lambda s, z: (s.p[0] + (s.q[0] - s.p[0]) * (z - s.p[1]) / (s.q[1] - s.p[1]), z)
    return [pr.Line(at(low, z0), low.q), blend, pr.Line(up.p, at(up, z1))]


def cap_front(d: Blueprint, h: pr.Hood) -> Part.Shape:
    """The front of the cap, to the line where its soft edge ends on the sides and the roof (hood_edge_back behind
    the leaning front): the quarter ellipse of the soft edge carried round the front outline as an evolved solid,
    made to lean, and cut on that line."""
    eb = d.hood_edge_back
    profile = [pr.Conic((d.hood_edge_in, 0.0), (0.0, 0.0), (0.0, eb)), pr.Line((0.0, eb), (0.0, eb + OVER / 2))]
    turn = FreeCAD.Matrix(-1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0)
    shell = leaning(evolved(cap_outline(d, h), profile).transformed(turn), h, d)
    z0, z1 = -3 * OVER, h.height + OVER
    line = lean_line(h, eb, z0, z1)
    return shell.common(across(line + poly([ends(line[-1])[1], (-3 * OVER, z1), (-3 * OVER, z0), ends(line[0])[0]])[:-1]))


def cap_rear(d: Blueprint, h: pr.Hood) -> Part.Shape:
    """The cap behind its soft edge, with exact surfaces: the front outline extruded along the depth, in common with
    the side profile (the roof, the round in the crease, the rear arc, the rear wall) extruded across the width.
    It starts on the line where the soft edge ends, and it runs on below the foot."""
    view = pr.hood_side_profile(d, h.height, h.depth, d.hood_h - d.seam_gap)
    z0, z1 = -2 * OVER, h.height + OVER
    line = lean_line(h, d.hood_edge_back, z0, z1)
    far = h.depth + 3 * OVER
    behind = across(line + poly([ends(line[-1])[1], (far, z1), (far, z0), ends(line[0])[0]])[:-1])
    rear = view[5:-1] + [pr.Line(view[-1].p, (h.depth, z0))]
    profile = across(poly([(h.depth, z0), (-3 * OVER, z0), (-3 * OVER, h.height), view[4].q])[:-1] + rear)
    block = prism(cap_outline(d, h), xz(-3 * OVER), V(0, h.depth + 6 * OVER, 0))
    return block.common(profile).common(behind)


@dataclass(frozen=True)
class Station:
    """One section of a round along an edge between two surfaces: the centre of the rolling ball, and the outward
    unit normals of the two surfaces at the points where the ball touches them."""
    c: FreeCAD.Vector
    n1: FreeCAD.Vector
    n2: FreeCAD.Vector

    @property
    def turn(self) -> float:
        """The angle through which the edge turns here, radians."""
        return math.acos(max(-1.0, min(1.0, self.n1.dot(self.n2))))


def hood_corner_stations(d: Blueprint, h: pr.Hood, r: float) -> list[list[Station]]:
    """The round of the cap's right rear corner (profiles.hood_corner) as stations along its edge, in the hood's
    frame, from ROUND_BELOW under the foot to the roof.

    The stations come in four pieces, one for each part of the edge on which both outlines keep their kind of curve.
    A piece ends where an outline changes its curvature, so that each piece is a smooth surface. In a piece the
    stations are ROUND_STEP apart or less along the centre line, at one spacing (a loft through sections that are
    not equally spaced swings far off). The last station is where the edge turns ROUND_END: near the roof the side
    and the rear turn tangent to each other, and the round runs out."""
    rd = pr.hood_corner(d, h, r)
    station = lambda zc: Station(*(V(*v) for v in rd.station(zc)))
    z_lo, z_end = -ROUND_BELOW, rd.end(ROUND_END)
    at = lambda u: z_lo + (z_end - z_lo) * (1.0 - (1.0 - u) ** 2)        # the heights closer together toward the roof
    heights = [at(k / ROUND_SAMPLES) for k in range(ROUND_SAMPLES + 1)]
    along = [0.0]
    for p, q in zip(heights, heights[1:]):
        along.append(along[-1] + (station(q).c - station(p).c).Length)

    def length_at(z: float) -> float:
        k = min(max(bisect.bisect_right(heights, z) - 1, 0), ROUND_SAMPLES - 1)
        return along[k] + (along[k + 1] - along[k]) * (z - heights[k]) / (heights[k + 1] - heights[k])

    def height_at(length: float) -> float:
        k = min(max(bisect.bisect_right(along, length) - 1, 0), ROUND_SAMPLES - 1)
        return heights[k] + (heights[k + 1] - heights[k]) * (length - along[k]) / (along[k + 1] - along[k])

    pieces = []
    marks = [z_lo, *rd.marks, z_end]
    for za, zb in zip(marks, marks[1:]):
        la, lb = length_at(za), length_at(zb)
        n = max(2, math.ceil((lb - la) / ROUND_STEP))
        pieces.append([station(za)] + [station(height_at(la + (lb - la) * k / n)) for k in range(1, n)] + [station(zb)])
    return pieces


def round_section(st: Station, r: float, off: float, e: float = 1.0) -> Part.Wire:
    """What a round takes off at one station, as a wire in the plane of the two normals: the region between the
    edge and the round's arc, reaching e out past both surfaces. The walls stand square to the two surfaces where
    the arc meets them. The arc stands `off` out from the true round, so that it crosses the two surfaces at a small
    angle and does not lie on their tangent (a boolean with a tangent face fails, or leaves faces of no width).
    Where the edge turns so little that the round is less than `off` deep, the arc is clear of the edge: the round
    ends there in a point on the edge."""
    b = st.n1 + st.n2
    b.normalize()
    p1, p2, mid = st.c + st.n1 * (r + off), st.c + st.n2 * (r + off), st.c + b * (r + off)
    apex = st.c + (st.n1 + st.n2) * (r / (1.0 + st.n1.dot(st.n2)))      # where the two tangents meet: the edge, or outside it
    tip, q1, q2 = apex + b * e, p1 + st.n1 * e, p2 + st.n2 * e
    return Part.Wire([Part.LineSegment(q1, tip).toShape(), Part.LineSegment(tip, q2).toShape(), Part.LineSegment(q2, p2).toShape(),
                      Part.Arc(p2, mid, p1).toShape(), Part.LineSegment(p1, q1).toShape()])


def hood_corner_cutter(d: Blueprint, h: pr.Hood) -> list[Part.Shape]:
    """What the round of the right rear corner takes off the cap, in the hood's frame: for each piece of the edge
    (hood_corner_stations) a loft of degree 3 through the sections of the round at its stations. It is the round that
    a ball of rear_corner_r makes when it rolls along the edge in touch with the side and the rear. OpenCascade's own
    round of this edge builds on the right side only, and on the cap of revision 6 not in every run."""
    r = d.rear_corner_r
    return [Part.makeLoft([round_section(st, r, ROUND_OFF) for st in piece], True, False, False, 3) for piece in hood_corner_stations(d, h, r)]


def cut_checked(solid: Part.Shape, tools: list[Part.Shape], what: str) -> Part.Shape:
    """A solid less some tools that do not overlap. A cut by lofts can come back with the work of one tool missing,
    or with material added, and no error. So the result is checked: it is one valid solid, it is not larger than the
    solid was, and no tool still holds more of it than CUT_LEFT of what that tool held of the solid (or CUT_LEFT_MM3).
    When the cut by all tools at once does not pass, the tools are cut one after the other; when that does not pass,
    it is an error."""
    due = [solid.common(t).Volume for t in tools]

    def left(s: Part.Shape) -> str:
        if not s.isValid() or len(s.Solids) != 1:
            return f"not one valid solid (valid {s.isValid()}, {len(s.Solids)} solids)"
        if s.Volume > solid.Volume + CUT_LEFT_MM3:
            return f"{s.Volume - solid.Volume:.2f} mm3 larger than before the cut"
        for k, (t, v) in enumerate(zip(tools, due)):
            rest = s.common(t).Volume
            if rest > max(CUT_LEFT * v, CUT_LEFT_MM3):
                return f"tool {k} still holds {rest:.3f} mm3 of {v:.3f}"
        return ""

    out = solid.cut(tools)
    if not left(out):
        return out
    out = solid
    for t in tools:
        out = out.cut(t)
    why = left(out)
    if why:
        raise Part.OCCError(f"{what}: {why}")
    return out


def cap(d: Blueprint, h: pr.Hood, log: list[str]) -> tuple[Part.Shape, Part.Shape]:
    """The cap in the hood's own frame, and its opening as a prism (for the marquee lip): the front and the rear
    joined on the line where the soft edge ends, cut level at the foot, the bevel of the seam groove, the recess of
    the opening, and the round of the two rear corners."""
    view = pr.hood_side_profile(d, h.height, h.depth, d.hood_h - d.seam_gap)
    solid = cap_front(d, h).fuse(cap_rear(d, h)).removeSplitter()
    solid = solid.common(across(poly([(h.depth, 0.0), (-OVER, 0.0), (-OVER, h.height), view[4].q])[:-1] + view[5:]))
    g = d.seam_groove
    solid = solid.cut(ring_bevel(outline_at(solid, g), g, 0.0, g))
    opening = prism(both_sides(opening_path(d, h)), xz(-OVER), V(0, BIG / 4, 0))
    solid = solid.cut(opening.common(across(poly(recess_profile(d, h))))).removeSplitter()
    right = hood_corner_cutter(d, h)
    solid = cut_checked(solid, right + [c.mirror(V(0, 0, 0), V(1, 0, 0)) for c in right], "the round of the hood's rear corners")
    pieces = hood_corner_stations(d, h, d.rear_corner_r)
    log.append(f"hood, rear corners R {d.rear_corner_r:g} by hand: {len(pieces)} lofts through {sum(len(p) for p in pieces)} sections on each side, "
               f"from below the foot to where the edge turns {math.degrees(pieces[-1][-1].turn):.1f} degrees")
    # The cap gets no edge break. Its sharp edges are the rim of the opening and the upper edge of the seam bevel (which
    # turns more than 45 degrees, because the sides and the front of the cap lean). The leaning front is a sheared
    # spline surface with a tolerance of 0.001, and OpenCascade's round on an edge of it is a valid solid that is not
    # the same in every run: the rim alone has two outcomes, the bevel alone two, both together three, and the strict
    # check of one of those does not end. The build must be the same in every run, so these edges stay sharp until the
    # front of the cap is made of exact surfaces
    listed = sharp_edges(solid, d, lambda m: m.z > 0.05)
    bevel = [e for e, _ in listed if middle(e).z < g + 0.5]
    log.append(f"hood: no edge break ({len(listed) - len(bevel)} edges on the rim of the opening, {len(bevel)} on the seam bevel, "
               f"{sum(e.Length for e, _ in listed):.0f} mm): the round on the leaning front is not the same in every run; they stay sharp")
    return solid, opening


def hood(d: Blueprint, log: list[str] | None = None) -> dict[str, Part.Shape]:
    """The cap and what stands in its opening, in the cabinet frame."""
    log = log if log is not None else []
    h = pr.hood(d)
    solid, opening = cap(d, h, log)
    xr = h.half_open(h.z_band_top, d) + OVER
    lip = Part.makeBox(2 * xr, d.hood_rail_proud, h.z_rail_top - h.z_band_top, V(-xr, h.y_band_top - d.hood_rail_proud, h.z_band_top)).common(opening)
    out = {"hood": solid, "marquee_lip": lip.removeSplitter()}
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

def build(d: Blueprint, log: list[str] | None = None) -> dict[str, Part.Shape]:
    """Every part of the outer form, by name, in the cabinet frame. log takes one line for each step that finds its
    edges on the solid (how many it found)."""
    log = log if log is not None else []
    fr = pr.front(d)
    out: dict[str, Part.Shape] = {}
    out["deck"], out["control_panel"] = deck(d, log)
    out["body"] = body(d, fr, log)
    out.update(hood(d, log))
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
    hw, rw, zc = d.width / 2, d.rear_w / 2, d.rear_step_z0
    mitre = pr.band_stroke(d)[3]
    cam = lambda target, radius, az, el: {"target": [round(v, 1) for v in target], "radius": radius, "az": az, "el": el}
    return {"closeup-cheek-foot": cam((hw - 6, *foot), 70, 45, 12),
            "closeup-rail-tuck": cam(crease, 40, 70, 10),
            "closeup-rail-top": cam((d.side_x(d.body_top) - 6, d.seam_y + 15, d.body_top - 10), 45, 55, 12),
            "closeup-hood-foot": cam((h.half_base - 5, h.origin[1] + 25, h.origin[2]), 40, 60, 8),
            "closeup-deck-front": cam((hw - 30, 10.0, d.deck_top - 10), 60, -40, 24),
            "closeup-deck-front-low": cam((hw - 60, 0.0, 6.0), 70, -20, 4),
            "closeup-seam-corner-left": cam((-(d.side_x(d.body_top) - 8), d.seam_y + 6, d.body_top), 35, -42, 6),
            "closeup-front-seam": cam((d.width / 4, d.seam_y, d.body_top - 4), 45, -15, 12),
            "closeup-seam-rear-corner": cam((d.side_x(d.body_top) - 8, d.depth - 8, d.body_top), 45, 140, 14),
            "closeup-rear-corner": cam((hw - 20, d.body_d + 5, 375.0), 95, 128, 14),
            "closeup-base-corner": cam((rw - 10, d.body_d - 10, 10.0), 45, 135, 20),
            "closeup-hip-foot": cam((rw - 1, d.body_d - 1, zc + 1), 18, 135, 8),
            "closeup-hip-top": cam((hw - 2, d.body_d + 10, zc + 12), 18, 125, 15),
            "closeup-head-foot": cam((hw - 2, d.depth - 2, d.rear_step_z1 + 1), 18, 125, 15),
            "closeup-top-mitre": cam((hw - 2, mitre[0] + 2, mitre[1] - 2), 20, 100, 10),
            "closeup-band-foot": cam((hw - 30, 420.0, 140.0), 210, 140, 14),
            "closeup-cut-ins": cam((rw - d.rear_corner_r / 2, d.body_d - d.rear_corner_r / 2, d.cut_in_z0 + d.cut_in_pitch * (d.cut_in_count - 1) / 2), 60, 145, 10),
            "closeup-cut-in-corner": cam((rw - 2, d.body_d - 2, d.cut_in_z0 + 5), 22, 135, 6),
            "closeup-cut-in-straight": cam((rw - 1, d.body_d - 1, d.cut_in_z0 + d.cut_in_pitch + d.cut_in_h / 2), 30, 135, 0),
            "closeup-hand-hold": cam(((d.grip_x0 + d.grip_x1) / 2, d.depth, d.grip_z0 + d.grip_h / 2), 65, 165, 12),
            "closeup-hood-corner-above": cam((hw - 18, d.depth - 18, d.body_top + 8), 75, 135, 38),
            "closeup-hood-corner-side": cam((hw - 12, d.depth - 12, d.body_top + 25), 90, 90, 5),
            "closeup-hood-corner-rear": cam((hw - 12, d.depth - 12, d.body_top + 25), 90, 180, 5),
            "closeup-hood-roof-end": cam((h.half_top + 6, h.origin[1] + h.depth - 58, h.origin[2] + h.height - 1), 40, 135, 45),
            "closeup-hood-rear-top": cam((h.half_top - 4, d.depth - 30, h.origin[2] + h.height - 12), 60, 135, 28),
            "closeup-hood-band": cam((d.logo_w / 2 + d.logo_gap + 40, h.origin[1] + 20, h.origin[2] + (h.z_sill + h.z_rail_top) / 2), 100, 40, 10)}


def edge_polylines(shape: Part.Shape, step: float = EDGE_STEP) -> list[list[list[float]]]:
    """Every edge of a shape as a polyline (the face boundaries that the FreeCAD GUI draws)."""
    out = []
    for e in shape.Edges:
        if e.Degenerated or e.Length < 1e-6:
            continue
        n = max(2, math.ceil(e.Length / step) + 1)
        out.append([[round(p.x, 3), round(p.y, 3), round(p.z, 3)] for p in e.discretize(Number=n)])
    return out


def export(out: str, parts: dict[str, Part.Shape], d: Blueprint, log: list[str] | None = None) -> dict:
    os.makedirs(out, exist_ok=True)
    manifest = {}
    for k, s in parts.items():
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.05).write(os.path.join(out, f"{k}.stl"))
        s.exportBrep(os.path.join(out, f"{k}.brep"))
        manifest[k] = {"file": f"{k}.stl", "finish": FINISH[k], "brep": f"{k}.brep"}
    Part.makeCompound(list(parts.values())).exportStep(os.path.join(out, "shell.step"))
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    json.dump(focus(d), open(os.path.join(out, "focus.json"), "w"), indent=1)
    json.dump({k: edge_polylines(s) for k, s in parts.items()}, open(os.path.join(out, "edges.json"), "w"))
    bb = Part.makeCompound(list(parts.values())).BoundBox
    report = {"outside": [round(bb.XLength, 2), round(bb.YLength, 2), round(bb.ZLength, 2)],
              "parts": {k: {"valid": s.isValid(), "solids": len(s.Solids), "volume_mm3": round(s.Volume, 1), "faces": len(s.Faces),
                            "surfaces": sorted({type(f.Surface).__name__ for f in s.Faces})} for k, s in parts.items()},
              "log": log or [], "dims": {k: getattr(d, k) for k in d.__dataclass_fields__}}
    json.dump(report, open(os.path.join(out, "report.json"), "w"), indent=1)
    return report


def main() -> int:
    out = os.environ.get("CANDYBAR_OUT", "cad/out/shell-rev7")
    d = Blueprint()
    log: list[str] = []
    report = export(out, build(d, log), d, log)
    for line in log:
        print(line)
    for k, r in report["parts"].items():
        print(f"{k:14s} valid {r['valid']}  solids {r['solids']}  faces {r['faces']:4d}  volume {r['volume_mm3']:>12.1f}  {', '.join(r['surfaces'])}")
    print("outside", " x ".join(f"{v:.1f}" for v in report["outside"]))
    return 0 if all(r["valid"] and r["solids"] == 1 for r in report["parts"].values()) else 1
