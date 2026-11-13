"""Rear form study (revision 7 candidates): the shell with a new rear, built with true rounds, for comparison only.

Blueprint() and profiles.faces() do not change: the default build stays revision 6. This module builds candidates
with the true dimensions of the shell (the tuck, the hood's rear outline, the seam groove) and its own rear:

  A   the present rear, repaired: the step ends on the hood seam in front of the corner round (the hood keeps its
      full width and overhangs the narrower rear body behind the step), the two creases of the rear slope are rounded,
      the step's edges get a small radius.
  R   the rear of the maker's mini inside the same envelope: the 40 mm overhang as a soft roll whose foot line is a
      smile, a larger corner round, two hand-hold recesses in the head, the cut-ins at the lower rear corners.
  R2  R with the head at full width back to the rear corner (as the mini): the set-back behind the step is closed at
      the top by a shoulder plane that falls toward the front and turns into the step through a round; the lower body,
      the head and the hood share one corner R 25. R2Fb, R2Fa, R2Fm: R2 with the foot of the step flaring back toward
      the rear near the floor (inner crease only, the whole band, or a mix).

R2's method differs (shoulder_body): the step facet, the recessed side and the shoulder are three half-spaces, so the
recess has only concave edges; its rounds are made on the right side of the body before the rear cut (the turn, then
the recessed edge as one chain, then the full-width edge as one chain), that half is mirrored, the rear is cut, and
the corner is rounded from the floor to the seam in one call on both sides.

Method. The body is first built with sharp edges: the side profile with a plain rear wall, the front outline with the
tuck, the rail, the step and the bezel cuts of solids.py, and a cut by the rear profile. The rear profile is a path
of lines and exact arcs in side view; it is extruded across the width (A) or swept along the smile with a fixed
trihedron (R: every section is the same profile, moved up by the smile). Then true fillets (BRepFilletAPI, makeFillet)
in this order: the step's outer edge and inner crease, the vertical corner chain (rear body side to the rear surfaces,
one radius from the floor to the body top, tangent all the way because the rear profile has no crease left), then the
base chamfer, then the seam bevel of solids.py, then the recesses. The hood is built as in solids.py without its
corner cutter, and its rear corner chain gets a true fillet. No loft of sampled sections makes a round here.

Run headless (one variant or a list; the default is all):

    CANDYBAR_OUT=cad/out/shell-bp-rev7 CANDYBAR_REAR=A,R cad/candybar/freecad-run.sh candybar.shell.rear_study

Each variant writes <out>/<name>/: the BREP and STL of each part, manifest.json, focus.json (close-up cameras),
edges.json (every BREP edge as a polyline, for the edge-drawn renders), face-check.json/.md and numbers.json (the
values that the cost sheet uses). candybar.shell.viewdoc writes shell.FCStd beside them (run with --gui).
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass, field, replace

import FreeCAD
import MeshPart
import Part

from . import profiles as pr
from . import solids as so
from .dims import Blueprint

V = FreeCAD.Vector
OVER = so.OVER
BIG = so.BIG
EDGE_STEP = 0.6
ON = 0.05


@dataclass(frozen=True)
class CutIns:
    """The decorative cut-ins at each lower rear corner: a row of short level grooves with round ends and a round
    floor, that wrap round the corner round. Lengths in mm; z of the lowest and the pitch."""
    count: int = 4
    z0: float = 126.0
    pitch: float = 22.0
    height: float = 10.0
    depth: float = 3.0
    start_on_round: float = 6.0   # where each groove starts: this far round the corner from the rear wall (the door
                                  # land beside the door is only 4 wide, so the grooves start on the round)
    on_side: float = 40.0         # how far each groove runs onto the side from the end of the round


@dataclass(frozen=True)
class Grips:
    """Two hand-hold recesses in the head: an opening in the upper rear wall, a roof that slopes down inward at 45
    degrees (a hook for the fingers, printable upright), a level floor."""
    x0: float = 70.0
    x1: float = 170.0
    z0: float = 345.0
    height: float = 62.0
    depth: float = 26.0
    end_r: float = 10.0


@dataclass(frozen=True)
class Shoulder:
    """The head at full width (R2): the set-back behind the step is closed at the top by a shoulder, a plane that
    rises `rise` while it runs out by the step (the side of the band under the roll), and falls toward the front at
    `fall` (tangent) from the rear corner, where its lower crease meets the roll's lower crease, to the turn, where the
    step's inner crease runs into it. The rounds, in this order: the turn (the concave mitre of the step facet and the
    shoulder), the recessed edge (the step's inner crease, round the turn, the shoulder's lower crease: one chain), the
    full-width edge (the step's outer edge, round the turn, the shoulder's upper crease: one chain), then the corner
    from the floor to the seam. The full-width edge must be about R 22 or more where the corner passes it, or the R 25
    corner fails or leaves a needle there; at the floor that round leaves only 3 of flat on the step facet, and the
    base chamfer makes a sliver of it. So the full-width round grows along its edge, linearly, from outer_r_floor at
    the floor to outer_r at the rear corner. The recessed round must be R 7 or more: the shoulder turns only 16.7
    degrees from the recessed side, and a smaller round is narrower than 2."""
    rise: float = 40.0
    fall: float = 0.36
    turn_r: float = 30.0
    inner_r: float = 7.0
    outer_r: float = 22.0
    outer_r_floor: float = 16.0
    inner_r_floor: float = 7.0


@dataclass(frozen=True)
class Flare:
    """The foot of the step curves back toward the rear near the floor. In side view each edge of the step band leaves
    its leaning line at z0 on a tangent arc and reaches the floor `inner_back` (the inner crease, on the recessed side)
    or `outer_back` (the outer edge, on the full-width side) behind the straight line. The band between them is ruled
    with level rulings; every level section of it is an affine image of the inner arc, so it is exact."""
    z0: float = 130.0
    inner_back: float = 80.0
    outer_back: float = 0.0


@dataclass(frozen=True)
class Variant:
    name: str
    title: str
    step_seam_y: float = 537.0
    step_lean: float = 28.0
    corner_r: float = 18.0
    # rear profile in side view, from the top down: (y, z, radius of the round at that vertex)
    crease_lo: tuple[float, float, float] = (540.0, 310.0, 8.0)
    crease_hi: tuple[float, float, float] = (580.0, 350.0, 8.0)
    smile: float = 0.0
    smile_power: float = 4.0
    step_r: float = 10.0         # the step's outer edge (convex in plan): at least the base chamfer + 3, or the chamfer collapses or tapers there
    step_crease_r: float = 6.0   # the step's inner crease (concave): below 5 the round leaves a piece under 2 mm where the tuck starts
    chamfer: float = 5.0
    grips: Grips | None = None
    cut_ins: CutIns | None = None
    shoulder: Shoulder | None = None
    flare: Flare | None = None
    note: str = ""

    @property
    def hood_r(self) -> float:
        """The hood keeps the full width. Without a shoulder its round in plan is the body's round plus the step, so
        that both rounds leave the rear wall on the same line and the soffit grows from nothing at the rear to the step
        at the side. With a shoulder the head has the full width, and the head and the hood share one corner round."""
        return self.corner_r if self.shoulder else self.corner_r + Blueprint().step_in


VARIANTS: dict[str, Variant] = {
    "A": Variant("A", "A: present rear, repaired", crease_lo=(540.0, 310.0, 20.0), crease_hi=(580.0, 350.0, 20.0),
                 note="step ends on the seam at y 537; creases R 20; corner R 18"),
    "A25": Variant("A25", "A, corner R 25", step_seam_y=530.0, corner_r=25.0, crease_lo=(540.0, 310.0, 30.0), crease_hi=(580.0, 350.0, 30.0),
                   note="step on the seam at y 530; the convex crease must exceed the corner round (R 30); the concave one is free"),
    "A-e3": Variant("A-e3", "A, creases R 3 / R 20", crease_lo=(540.0, 310.0, 3.0), crease_hi=(580.0, 350.0, 20.0)),
    "A-e8": Variant("A-e8", "A, creases R 8 / R 20", crease_lo=(540.0, 310.0, 8.0), crease_hi=(580.0, 350.0, 20.0)),
    "A-e15": Variant("A-e15", "A, creases R 15 / R 20", crease_lo=(540.0, 310.0, 15.0), crease_hi=(580.0, 350.0, 20.0)),
    "A-ch3": Variant("A-ch3", "A, base chamfer 3", crease_lo=(540.0, 310.0, 20.0), crease_hi=(580.0, 350.0, 20.0), chamfer=3.0),
    "A-ch8": Variant("A-ch8", "A, base chamfer 8", crease_lo=(540.0, 310.0, 20.0), crease_hi=(580.0, 350.0, 20.0), chamfer=8.0, step_r=11.0),
    "A-cut": Variant("A-cut", "A with cut-ins", crease_lo=(540.0, 310.0, 20.0), crease_hi=(580.0, 350.0, 20.0), cut_ins=CutIns()),
    "R": Variant("R", "R: roll, smile, grips, cut-ins", step_seam_y=530.0, corner_r=25.0, crease_lo=(540.0, 298.0, 25.0),
                 crease_hi=(580.0, 338.0, 60.0), smile=24.0, grips=Grips(), cut_ins=CutIns(),
                 note="roll crease z 298 at the centre (the lowest that keeps the BC-250 board inside the door), smile 24; corner R 25"),
}
VARIANTS["R2"] = replace(VARIANTS["R"], name="R2", title="R2: R with the head at full width", shoulder=Shoulder(),
                         note="head at full width to the rear corner; set-back closed by a shoulder that falls toward the front; "
                              "head, band and hood share one corner R 25")
VARIANTS["R2Fb"] = replace(VARIANTS["R2"], name="R2Fb", title="R2Fb: R2, the step's inner crease flares back at the floor", flare=Flare(),
                           shoulder=replace(VARIANTS["R2"].shoulder, inner_r_floor=18.0, outer_r_floor=22.0),
                           note="inner crease curves back from z 130 to 80 behind at the floor; the outer edge keeps its lean and one R 22 "
                                "round to the floor; the recessed round grows from R 7 at z 130 to R 18 at the floor, where the ramp "
                                "turns only 7 degrees from the recessed side (R 7 there is 0.9 wide)")
VARIANTS["R2Fm"] = replace(VARIANTS["R2Fb"], name="R2Fm", title="R2Fm: R2Fb with the outer edge flaring a little", flare=Flare(outer_back=30.0),
                           note="inner crease 80 behind at the floor, outer edge 30 behind; outer round R 22, recessed round R 7 to R 18")
VARIANTS["R2Fa"] = replace(VARIANTS["R2"], name="R2Fa", title="R2Fa: R2, the whole step band flares back at the floor",
                           flare=Flare(outer_back=80.0), note="both edges of the step curve back from z 130 to 80 behind at the floor")


def blueprint(v: Variant) -> Blueprint:
    """The Blueprint of a candidate: the step moved so that its outer edge meets the body top at step_seam_y."""
    b = Blueprint()
    t = math.tan(math.radians(v.step_lean))
    return replace(b, step_lean=v.step_lean, step_y0=v.step_seam_y - b.body_top * t, rear_corner_r=v.hood_r)


# ---------- the rear profile ----------

def rounded(points: list[tuple[float, float, float]]) -> pr.Path:
    """A polyline in (y, z) with a round of the given radius at each inner vertex: lines and exact arcs."""
    out: pr.Path = []
    cur = points[0][:2]
    for i in range(1, len(points) - 1):
        p, r = points[i][:2], points[i][2]
        a, b = points[i - 1][:2], points[i + 1][:2]
        u = ((p[0] - a[0]) / math.dist(a, p), (p[1] - a[1]) / math.dist(a, p))
        w = ((b[0] - p[0]) / math.dist(p, b), (b[1] - p[1]) / math.dist(p, b))
        turn = math.atan2(u[0] * w[1] - u[1] * w[0], u[0] * w[0] + u[1] * w[1])
        if r <= 0 or abs(turn) < 1e-9:
            out.append(pr.Line(cur, p))
            cur = p
            continue
        t = r * math.tan(abs(turn) / 2)
        t0 = (p[0] - u[0] * t, p[1] - u[1] * t)
        t1 = (p[0] + w[0] * t, p[1] + w[1] * t)
        side = 1.0 if turn > 0 else -1.0
        c = (t0[0] - side * u[1] * r, t0[1] + side * u[0] * r)
        a0 = math.atan2(t0[1] - c[1], t0[0] - c[0])
        out += [pr.Line(cur, t0), pr.Arc(c, r, a0, a0 + turn)]
        cur = t1
    out.append(pr.Line(cur, points[-1][:2]))
    return out


def rear_path(d: Blueprint, v: Variant) -> pr.Path:
    lo, hi = v.crease_lo, v.crease_hi
    return rounded([(d.depth, d.body_top + 3 * OVER, 0.0), hi, lo, (d.body_d, -3 * OVER, 0.0)])


def smile_z(v: Variant, x: float, half: float) -> float:
    return v.smile * (abs(x) / half) ** v.smile_power


def rear_cutter(d: Blueprint, v: Variant) -> Part.Shape:
    """What the rear profile takes off the plain rear: the region behind the profile, across the width (A) or swept
    along the smile with every section parallel (R)."""
    path = rear_path(d, v)
    far = d.depth + 3 * OVER
    region = path + so.poly([so.ends(path[-1])[1], (far, -3 * OVER), (far, d.body_top + 3 * OVER)])[:-1]
    if not v.smile:
        return so.prism(region, so.yz(-BIG / 2), V(BIG, 0, 0))
    half = d.rear_w / 2
    x0 = -(d.width / 2 + 2 * OVER)
    z0 = smile_z(v, x0, half)
    prof = so.wire(so.closed(region), lambda p: V(x0, p[0], p[1] + z0))
    pts = [V(x, d.depth, smile_z(v, x, half)) for x in (x0 + (-2 * x0) * k / 40 for k in range(41))]
    spine = Part.BSplineCurve()
    spine.interpolate(pts)
    ps = Part.BRepOffsetAPI.MakePipeShell(Part.Wire([spine.toShape()]))
    ps.setTrihedronMode(V(0, 0, 0), V(1, 0, 0))
    ps.add(prof, False, False)
    ps.build()
    ps.makeSolid()
    return ps.shape()


# ---------- edge finding ----------

def _samples(e: Part.Edge, n: int = 5) -> list:
    return [e.valueAt(e.FirstParameter + (e.LastParameter - e.FirstParameter) * k / (n - 1)) for k in range(n)]


def edges_where(shape: Part.Shape, test, n: int = 5) -> list[Part.Edge]:
    return [e for e in shape.Edges if not e.Degenerated and all(test(p) for p in _samples(e, n))]


def rear_side_x(d: Blueprint, z: float) -> float:
    return d.side_x(z) - d.step_in


# ---------- the body ----------

def step_cutter(d: Blueprint) -> Part.Shape:
    """What the step takes off the right side: the 45 degree notch of solids.step_cutter, and behind it the region
    outside the rear body side as exact surfaces (a plane, and the cylinder of the tuck), extruded along the depth and
    cut by the leaning plane of the step's inner crease. solids.step_cutter makes the rear body side from a sheared
    face, a surface that the fillet of the rear corner cannot use."""
    top = d.body_top + OVER
    s = d.step_in
    far = d.width / 2 + s + OVER
    sides = so.side_path(d, top)
    outline = sides + so.poly([so.ends(sides[-1])[1], (far, top), (far, -OVER), (d.width / 2, -OVER)])[:-1]
    m = FreeCAD.Matrix()
    m.A23 = math.tan(math.radians(d.step_lean))
    m.A24 = d.step_y0
    notch = Part.Face(so.wire(outline, so.xz(0.0))).transformGeometry(m).extrude(V(-s, s, 0))
    slab = Part.Face(so.wire(outline, so.xz(-BIG / 2))).translated(V(-s, 0, 0)).extrude(V(0, BIG, 0))
    t = math.tan(math.radians(d.step_lean))
    behind = so.halfspace(V(0, d.step_y0 + s, 0), V(0, 1, -t))
    return notch.fuse(slab.common(behind)).removeSplitter()


def sharp_body(d: Blueprint, v: Variant, rear: bool = True, right_only: bool = False) -> Part.Shape:
    """The body as one solid with the sharp rear: as solids.body, without the corner cutter, with the rear profile
    (rear=False: without it; right_only: the step or the recess on the right side only)."""
    fr = pr.front(d)
    top = d.body_top + OVER
    sides = so.side_path(d, top)
    end = so.ends(sides[-1])[1]
    ya = d.foot_y - d.bend_t
    rail_top = fr.rail.at(fr.rail.a1)
    profile = [pr.Line((ya, 0.0), (ya, d.deck_top)), fr.sweep, fr.rail] + so.poly([rail_top, (d.depth, d.body_top), (d.depth, 0.0), (ya, 0.0)])[:-1]
    solid = so.across(profile).common(so.along(so.both_sides(sides + [pr.Line(end, (0.0, end[1]))])))
    xb = d.bezel_w / 2 + d.panel_gap
    bw = d.bezel_w / 2
    plate = so.bezel_box(d, fr, -bw, bw).cut(so.behind_screen(d, d.mon_setback))
    reveal = so.bezel_box(d, fr, bw, xb).cut(so.land_cylinder(d, fr))
    step = recess_cutter(d, v) if v.shoulder else step_cutter(d)
    cutters = [so.both(so.rail_cutter(d, fr)), step if right_only else so.both(step), plate, so.both(reveal), so.screen(d)]
    return solid.cut(cutters + ([rear_cutter(d, v)] if rear else [])).removeSplitter()


# ---------- the shoulder (R2) ----------

def shoulder_z0(d: Blueprint, v: Variant) -> float:
    """Height of the shoulder's lower crease (sharp) at the rear wall: the roll's lower crease at the recessed side."""
    return v.crease_lo[1] + smile_z(v, d.rear_w / 2, d.rear_w / 2)


def shoulder_normal(d: Blueprint, v: Variant) -> FreeCAD.Vector:
    """The outward normal of the shoulder plane (down, out, and back: it falls toward the front)."""
    n = V(v.shoulder.rise / d.step_in, v.shoulder.fall, -1.0)
    n.normalize()
    return n


def step_normal(d: Blueprint) -> FreeCAD.Vector:
    n = V(1.0, 1.0, -math.tan(math.radians(d.step_lean)))
    n.normalize()
    return n


def turn_point(d: Blueprint, v: Variant) -> tuple[float, float]:
    """(y, z) where the step's inner crease meets the shoulder's lower crease on the recessed side (sharp lines)."""
    t = math.tan(math.radians(d.step_lean))
    z0, f = shoulder_z0(d, v), v.shoulder.fall
    # y = step_y0 + step_in + z t ; z = z0 + (y - body_d) f
    z = (z0 + (d.step_y0 + d.step_in - d.body_d) * f) / (1 - t * f)
    return d.step_y0 + d.step_in + z * t, z


def flare_arc(d: Blueprint, f: Flare) -> tuple[tuple[float, float], float, tuple[float, float]]:
    """The arc of the inner crease in side view (y, z): centre, radius and its point on the floor. It is tangent to the
    leaning line at z0 and reaches the floor inner_back behind it."""
    t = math.tan(math.radians(d.step_lean))
    k = math.hypot(1.0, t)
    yi = lambda z: d.step_y0 + d.step_in + z * t
    pf = (yi(f.z0), f.z0)

    def floor_y(r: float) -> float:
        c = (pf[0] + r / k, pf[1] - r * t / k)
        return c[0] - math.sqrt(max(r * r - c[1] ** 2, 0.0))

    lo, hi = 1.0, 1e5
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        lo, hi = (mid, hi) if floor_y(mid) - yi(0.0) > f.inner_back else (lo, mid)
    r = math.sqrt(lo * hi)
    c = (pf[0] + r / k, pf[1] - r * t / k)
    return c, r, (floor_y(r), 0.0)


def behind_step(d: Blueprint, v: Variant) -> Part.Shape:
    """The region behind the step band: the half-space behind the step facet, and with a flare, below z0, the ruled
    solid behind the flared band instead. That solid is a ruled loft between two level-ruled sections at
    x = W + OVER/10 and x = rear_w/2 - OVER/10; each section is the flare arc of the inner crease (and its tangent
    below the floor) moved by an affine map that keeps z, closed far behind. Above z0 the facet stays a plane, and the
    band is tangent to it along the ruling at z0."""
    facet = so.halfspace(V(d.width / 2, d.step_y0, 0), step_normal(d))
    f = v.flare
    if not f:
        return facet
    t = math.tan(math.radians(d.step_lean))
    W, s_in = d.width / 2, d.step_in
    yi = lambda z: d.step_y0 + s_in + z * t
    c, r, pb = flare_arc(d, f)
    pf = (yi(f.z0), f.z0)
    a0 = math.atan2(pf[1] - c[1], pf[0] - c[0])
    a1 = math.atan2(pb[1] - c[1], pb[0] - c[0])
    if a1 < a0:
        a1 += 2 * math.pi                          # the arc runs counter-clockwise (in y, z) from the line to the floor
    tan_b = (-math.sin(a1), math.cos(a1))          # its direction at the floor: down and back
    below = (pb[0] + tan_b[0] * OVER / -tan_b[1], -OVER)
    yz = lambda p: V(0.0, p[0], p[1])
    am = (a0 + a1) / 2
    path = [Part.Arc(yz(pf), yz((c[0] + r * math.cos(am), c[1] + r * math.sin(am))), yz(pb)).toShape(), Part.LineSegment(yz(pb), yz(below)).toShape()]
    far = d.depth + 2 * OVER

    def section(x: float) -> Part.Wire:
        u = W - x
        k = (f.outer_back + (f.inner_back - f.outer_back) * u / s_in) / f.inner_back
        m = FreeCAD.Matrix()
        m.A22, m.A23, m.A24 = k, (1 - k) * t, (1 - k) * d.step_y0 + u - k * s_in
        m.A14 = x
        edges = [e.transformGeometry(m) for e in path]
        top, bottom = edges[0].Vertexes[0].Point, edges[-1].Vertexes[-1].Point
        close = Part.makePolygon([bottom, V(x, far, -OVER), V(x, far, f.z0), top])
        return Part.Wire(edges + close.Edges)

    flared = Part.makeLoft([section(W + OVER / 10), section(d.rear_w / 2 - OVER / 10)], True, True)
    above = facet.common(so.halfspace(V(0, 0, f.z0), V(0, 0, 1)))
    return above.fuse(flared).removeSplitter()


def recess_cutter(d: Blueprint, v: Variant) -> Part.Shape:
    """What the step and the shoulder take off the right side: the region outside the recessed side (a plane at
    rear_w / 2: below the shoulder the tuck would move it by 0.2 at most), behind the step facet (45 degrees in plan,
    leaning back), and below the shoulder plane. Three half-spaces: all its edges are concave on the body."""
    a = d.rear_w / 2
    outside = so.halfspace(V(a, 0, 0), V(1, 0, 0))
    behind = behind_step(d, v) if v.flare else so.halfspace(V(d.width / 2, d.step_y0, 0), step_normal(d))
    below = so.halfspace(V(a, d.body_d, shoulder_z0(d, v)), shoulder_normal(d, v))
    return outside.common(behind).common(below)


def face_kind(f: Part.Face, d: Blueprint, v: Variant) -> str:
    """Name of a face of the right side behind the front body: W (full-width side), X (recessed side), F (step facet),
    S (shoulder), T (the round of the turn), or "" for any other face."""
    u0, u1, v0, v1 = f.ParameterRange
    c = f.valueAt((u0 + u1) / 2, (v0 + v1) / 2)
    if abs(c.x) < 150 or c.y < d.step_y0 - 1:
        return ""
    n = f.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
    if c.x < 0:
        c, n = V(-c.x, c.y, c.z), V(-n.x, n.y, n.z)
    if abs(abs(n.dot(step_normal(d))) - 1) < 1e-6 and abs(c.x - d.width / 2 + d.step_in / 2) < d.step_in / 2:
        return "F"
    if v.flare and c.z < v.flare.z0 + 1 and d.rear_w / 2 + 0.05 < c.x < d.width / 2 - 0.05 and not isinstance(f.Surface, (Part.Plane, Part.Cylinder)):
        return "R"
    if isinstance(f.Surface, Part.Plane):
        if abs(abs(n.dot(shoulder_normal(d, v))) - 1) < 1e-6:
            return "S"
        if abs(abs(n.x) - 1) < 1e-6 and abs(c.x - d.rear_w / 2) < 0.5:
            return "X"
    if isinstance(f.Surface, Part.Cylinder) and abs(f.Surface.Radius - v.shoulder.turn_r) < 1e-6 and c.y < d.body_d - 20:
        return "T"
    if abs(n.x) > 0.95 and c.x > d.width / 2 - 6:
        return "W"
    return ""


def kind_edges(s: Part.Shape, d: Blueprint, v: Variant, side: str, others: tuple[str, ...]) -> list[Part.Edge]:
    out = []
    for e in s.Edges:
        fs = s.ancestorsOfType(e, Part.Face)
        if len(fs) != 2 or e.Degenerated:
            continue
        ks = [face_kind(f, d, v) for f in fs]
        if side in ks and any(k in others for k in ks if k != side) and ks[0] != ks[1]:
            out.append(e)
    return out


def rear_corner_chain(s: Part.Shape, d: Blueprint) -> list[Part.Edge]:
    """The edges between the side surfaces and the rear surfaces at the right rear corner, from the floor to the body
    top: each joins a face that faces mostly sideways to one that faces mostly back."""
    out = []
    for e in s.Edges:
        b = e.BoundBox
        if e.Degenerated or min(abs(b.XMin), abs(b.XMax)) < d.rear_w / 2 - 10 or b.XMin * b.XMax < 0 or b.YMin < d.body_d - 10:
            continue
        fs = s.ancestorsOfType(e, Part.Face)
        if len(fs) != 2:
            continue
        ns = []
        for f in fs:
            u0, u1, v0, v1 = f.ParameterRange
            ns.append(f.normalAt((u0 + u1) / 2, (v0 + v1) / 2))
        if sorted(abs(n.y) > abs(n.x) for n in ns) == [False, True]:
            out.append(e)
    return out


def shoulder_body(d: Blueprint, v: Variant, log: list[str]) -> Part.Shape:
    """The body of a shoulder variant with its rounds, up to the base chamfer. The rounds of the step and the shoulder
    are made on the right side of a body without the rear cut, and that half is mirrored: OpenCascade lays the growing
    round along each edge in the edge's own direction, which the mirror reverses, so the same call on the left side
    gives another law. Only planes and cylinders cross the centre plane before the rear cut, so the two halves join
    into whole faces again. Then the rear cut and the corner, from the floor to the seam, on both sides."""
    sh = v.shoulder
    s = sharp_body(d, v, rear=False, right_only=True)
    es = kind_edges(s, d, v, "F", ("S",))
    log.append(f"turn: {len(es)} edges, R {sh.turn_r:g}")
    s = s.makeFillet(sh.turn_r, es)
    es = [e for e in kind_edges(s, d, v, "X", ("F", "T", "S", "R")) if e.BoundBox.Center.x > 0]
    s = growing_round(s, es, sh.inner_r_floor, sh.inner_r, V(d.rear_w / 2, band_y(d, v, d.step_in, 3.0), 3.0))
    log.append(f"recessed edge: {len(es)} edges, R {sh.inner_r_floor:g} at the floor, R {sh.inner_r:g} above")
    es = [e for e in kind_edges(s, d, v, "W", ("F", "T", "S", "R")) if e.BoundBox.Center.x > 0]
    s = growing_round(s, es, sh.outer_r_floor, sh.outer_r, V(d.width / 2, band_y(d, v, 0.0, 3.0), 3.0))
    log.append(f"full-width edge: {len(es)} edges, R {sh.outer_r_floor:g} at the floor growing to R {sh.outer_r:g}")
    half = s.common(so.halfspace(V(0, 0, 0), V(1, 0, 0)))
    s = half.fuse(half.mirror(V(0, 0, 0), V(1, 0, 0))).removeSplitter()
    s = s.cut(rear_cutter(d, v)).removeSplitter()
    es = rear_corner_chain(s, d)
    log.append(f"corner: {len(es)} edges, R {v.corner_r:g}")
    return s.makeFillet(v.corner_r, es)


def band_y(d: Blueprint, v: Variant, u: float, z: float) -> float:
    """Y of the sharp step band at height z, u in from the full-width side (0 the outer edge, step_in the inner crease)."""
    t = math.tan(math.radians(d.step_lean))
    y = d.step_y0 + z * t + u
    f = v.flare
    if not f or z >= f.z0:
        return y
    c, r, _ = flare_arc(d, f)
    delta = c[0] - math.sqrt(r * r - (z - c[1]) ** 2) - (d.step_y0 + d.step_in + z * t)
    return y + (f.outer_back + (f.inner_back - f.outer_back) * u / d.step_in) / f.inner_back * delta


def radius_at(s: Part.Shape, p: FreeCAD.Vector) -> float:
    """Radius (the smaller principal one) of the curved face of s nearest to p."""
    best = (math.inf, math.inf)
    for f in s.Faces:
        if isinstance(f.Surface, Part.Plane):
            continue
        dist, pts, _ = f.distToShape(Part.Vertex(p))
        if dist < best[0]:
            u, w = f.Surface.parameter(pts[0][0])
            k = max(abs(c) for c in f.curvatureAt(u, w))
            best = (dist, 1 / k if k > 1e-12 else math.inf)
    return best[1]


def growing_round(s: Part.Shape, edges: list[Part.Edge], r_floor: float, r_top: float, near_floor: FreeCAD.Vector) -> Part.Shape:
    """A round on one tangent chain whose radius runs linearly from r_floor at its floor end along the chain's lowest
    edge, and is r_top beyond. OpenCascade takes the two radii in the direction of that edge, which this code does not
    know, so both orders are made and the one with r_floor at near_floor (a point on the sharp edge near the floor)
    is kept."""
    if abs(r_floor - r_top) < 1e-9:
        return s.makeFillet(r_top, edges)
    made = []
    for r1, r2 in ((r_top, r_floor), (r_floor, r_top)):
        try:
            m = s.makeFillet(r1, r2, edges)
        except Part.OCCError:
            continue
        made.append((abs(radius_at(m, near_floor) - r_floor), m))
    if not made:
        raise Part.OCCError(f"no growing round R {r_floor:g} to R {r_top:g}")
    return min(made, key=lambda x: x[0])[1]


def step_edges(d: Blueprint, s: Part.Shape) -> tuple[list[Part.Edge], list[Part.Edge]]:
    t = math.tan(math.radians(d.step_lean))
    outer = lambda p: abs(abs(p.x) - d.side_x(p.z)) < ON and abs(p.y - (d.step_y0 + p.z * t)) < ON
    inner = lambda p: abs(abs(p.x) - rear_side_x(d, p.z)) < ON and abs(p.y - (d.step_y0 + p.z * t + d.step_in)) < ON
    keep = lambda f: [e for e in edges_where(s, lambda p: f(p) and -0.01 < p.z < d.body_top + 0.01) if e.BoundBox.ZLength > 0.5]
    return keep(outer), keep(inner)


def corner_edges(d: Blueprint, s: Part.Shape) -> list[Part.Edge]:
    t = math.tan(math.radians(d.step_lean))
    es = edges_where(s, lambda p: abs(abs(p.x) - rear_side_x(d, p.z)) < ON and p.y > d.step_y0 + p.z * t + d.step_in + 2.0
                     and -0.01 < p.z < d.body_top + 0.01 and p.y > d.body_d - 1.0)
    return [e for e in es if e.BoundBox.ZLength > 0.5]


def floor_edges(s: Part.Shape, y_front: float) -> list[Part.Edge]:
    return edges_where(s, lambda p: abs(p.z) < 1e-4 and p.y > y_front + 0.01, 3)


def body(d: Blueprint, v: Variant, log: list[str]) -> Part.Shape:
    s = shoulder_body(d, v, log) if v.shoulder else sharp_body(d, v)
    if v.step_r and not v.shoulder:
        outer, inner = step_edges(d, s)
        log.append(f"step edges: {len(outer)} outer, {len(inner)} inner")
        s = s.makeFillet(v.step_r, outer).makeFillet(v.step_crease_r, step_edges(d, s.makeFillet(v.step_r, outer))[1]) if inner else s
    if not v.shoulder:
        es = corner_edges(d, s)
        log.append(f"corner edges: {len(es)}")
        s = s.makeFillet(v.corner_r, es)
    if v.chamfer:
        es = floor_edges(s, d.foot_y - d.bend_t)
        log.append(f"floor edges: {len(es)}")
        s = s.makeChamfer(v.chamfer, es)
    g = d.seam_groove
    s = s.cut(so.ring_bevel(so.outline_at(s, d.body_top - g), d.body_top - g, d.body_top, g))
    if not s.isValid():
        # R2: the cut of the seam bevel past the full-width corner comes out with a face of the wrong orientation
        # ("unorientable shape"); ShapeFix turns it round and changes no face and no volume
        faces, volume = len(s.Faces), s.Volume
        s.fix(1e-7, 1e-7, 1e-7)
        log.append(f"seam bevel: shape fixed (valid {s.isValid()}, faces {faces} -> {len(s.Faces)}, volume change {abs(s.Volume - volume):.2g} mm3)")
    if v.cut_ins:
        s = s.cut(so.both(cut_in_cutter(d, v)))
    if v.grips:
        s = s.cut(so.both(grip_cutter(d, v)))
    return s.removeSplitter()


# ---------- the recesses ----------

def stadium(length: float, height: float, at: FreeCAD.Placement) -> Part.Face:
    """A slot outline with round ends, centred on the origin of `at`, long along its x, high along its y."""
    r = height / 2
    h = length / 2 - r
    pts = lambda a, cx: V(cx + r * math.cos(a), r * math.sin(a), 0)
    w = Part.Wire([Part.LineSegment(V(-h, -r, 0), V(h, -r, 0)).toShape(), Part.Arc(pts(-math.pi / 2, h), pts(0, h), pts(math.pi / 2, h)).toShape(),
                   Part.LineSegment(V(h, r, 0), V(-h, r, 0)).toShape(), Part.Arc(pts(math.pi / 2, -h), pts(math.pi, -h), pts(1.5 * math.pi, -h)).toShape()])
    f = Part.Face(w)
    f.Placement = at
    return f


def cut_in_cutter(d: Blueprint, v: Variant) -> Part.Shape:
    """The right row of cut-ins. Each groove runs level round the lower rear corner: from start_on_round along the
    corner round, then onto the side for on_side. Its section, square to the surface, from the lower lip: a round
    floor of radius depth, a back wall, a roof that rises outward at 45 degrees to the upper lip (it prints upright
    without support). The ends are planes square to the groove (90 degree inside corners)."""
    c = v.cut_ins
    r = v.corner_r
    xs = rear_side_x(d, 0.0)
    cx, cy = xs - r, d.body_d - r
    a0 = math.pi / 2 - c.start_on_round / r
    dp, h = c.depth, c.height
    out = []
    for k in range(c.count):
        z = c.z0 + k * c.pitch
        on_round = lambda a: V(cx + r * math.cos(a), cy + r * math.sin(a), z)
        p2, p3 = V(xs, cy, z), V(xs, cy - c.on_side, z)
        path = Part.Wire([Part.Arc(on_round(a0), on_round(a0 / 2), p2).toShape(), Part.LineSegment(p2, p3).toShape()])
        rad = V(math.cos(a0), math.sin(a0), 0)
        at = lambda q: on_round(a0) - rad * q[0] + V(0, 0, q[1])
        mid = (dp * math.sin(math.pi / 4), dp * (1 - math.cos(math.pi / 4)))
        sec = Part.Wire([Part.Arc(at((0.0, 0.0)), at(mid), at((dp, dp))).toShape(), Part.LineSegment(at((dp, dp)), at((dp, h - dp))).toShape(),
                         Part.LineSegment(at((dp, h - dp)), at((0.0, h))).toShape(), Part.LineSegment(at((0.0, h)), at((-OVER, h))).toShape(),
                         Part.LineSegment(at((-OVER, h)), at((-OVER, 0.0))).toShape(), Part.LineSegment(at((-OVER, 0.0)), at((0.0, 0.0))).toShape()])
        out.append(path.makePipeShell([sec], True, True))
    return out[0].fuse(out[1:]).removeSplitter() if len(out) > 1 else out[0]


def grip_cutter(d: Blueprint, v: Variant) -> Part.Shape:
    """The right hand-hold: in side view an opening of `height` in the upper rear wall, a roof that runs down inward
    at 45 degrees, a back wall `depth` in, a level floor; across, from x0 to x1 with round ends of end_r in plan."""
    g = v.grips
    y_out, y_in = d.depth + OVER, d.depth - g.depth
    zt = g.z0 + g.height
    prof = so.poly([(y_out, g.z0), (y_in, g.z0), (y_in, zt - g.depth), (d.depth, zt), (y_out, zt)])
    slab = so.prism(prof, so.yz(g.x0), V(g.x1 - g.x0, 0, 0))
    r = g.end_r
    plan = Part.makeBox(g.x1 - g.x0 - 2 * r, OVER * 4, 400, V(g.x0 + r, y_in - 1, 0)).fuse(
        [Part.makeCylinder(r, 400, V(g.x0 + r, y_in + r, 0)), Part.makeCylinder(r, 400, V(g.x1 - r, y_in + r, 0)),
         Part.makeBox(g.x1 - g.x0, OVER * 4, 400, V(g.x0, y_in + r, 0))])
    return slab.common(plan).removeSplitter()


# ---------- deck and hood ----------

def deck(d: Blueprint, v: Variant) -> tuple[Part.Shape, Part.Shape]:
    solid, panel = so.deck(d)
    if v.chamfer:
        solid = solid.makeChamfer(v.chamfer, edges_where(solid, lambda p: abs(p.z) < 1e-4 and p.y < d.foot_y - d.bend_t - 0.01, 3))
    return solid, panel


def hood(d: Blueprint, v: Variant, log: list[str]) -> dict[str, Part.Shape]:
    """The hood of solids.hood with the rear corner round of hood_r (d.rear_corner_r is set to it by blueprint()).

    The corner is still the cut by a loft of its sections (revision 6). A true fillet of the cap's sharp corner fails:
    the corner chain runs up the rear arc and over the top corner to the roof, where the side and the rear arc turn
    tangent, so that a round of one radius must vanish there. A clean hood corner needs a new construction of the
    hood's rear (stage 2); the face check lists what this one leaves."""
    log.append(f"hood corner R {d.rear_corner_r:g} (revision 6 construction)")
    return so.hood(d)


# ---------- all parts, export ----------

FINISH = dict(so.FINISH, body="white")


def build(v: Variant, log: list[str] | None = None) -> dict[str, Part.Shape]:
    log = log if log is not None else []
    d = blueprint(v)
    fr = pr.front(d)
    out: dict[str, Part.Shape] = {}
    out["deck"], out["control_panel"] = deck(d, v)
    out["body"] = body(d, v, log)
    out.update(hood(d, v, log))
    out["bezel"] = so.bezel(d, fr)
    out["screen"] = so.screen(d)
    return {k: s.Solids[0] if len(s.Solids) == 1 else s for k, s in out.items()}


def edge_polylines(shape: Part.Shape, step: float = EDGE_STEP) -> list[list[list[float]]]:
    """Every edge of a shape as a polyline (the face boundaries that the FreeCAD GUI draws)."""
    out = []
    for e in shape.Edges:
        if e.Degenerated or e.Length < 1e-6:
            continue
        n = max(2, math.ceil(e.Length / step) + 1)
        out.append([[round(p.x, 3), round(p.y, 3), round(p.z, 3)] for p in e.discretize(Number=n)])
    return out


def focus(d: Blueprint, v: Variant) -> dict[str, dict]:
    """Close-up cameras on the rear junctions."""
    cam = lambda target, radius, az, el: {"target": [round(c, 1) for c in target], "radius": radius, "az": az, "el": el}
    xs = rear_side_x(d, d.body_top)
    zs = (v.crease_lo[1] + v.crease_hi[1]) / 2 + v.smile
    out = {"closeup-seam-corner": cam((xs - 4, d.depth - v.corner_r - 6, d.body_top - 6), 45, 125, 10),
           "closeup-step-top": cam((d.side_x(d.body_top) - 6, v.step_seam_y + 6, d.body_top - 12), 40, 70, 4),
           "closeup-roll-corner": cam((rear_side_x(d, zs) - 6, d.body_d + 10, zs), 60, 140, 12),
           "closeup-base-corner": cam((rear_side_x(d, 0) - 10, d.body_d - 10, 10.0), 45, 135, 20),
           "closeup-deck-front-low": cam((d.width / 2 - 60, 0.0, 6.0), 70, -20, 4)}
    if v.shoulder:
        turn = turn_point(d, v)
        out["closeup-r2-corner"] = cam((d.width / 2 - 20, d.body_d + 5, 375.0), 95, 128, 14)
        out["closeup-turn"] = cam((d.width / 2 - 4, turn[0] + 6, turn[1] + 14), 48, 105, 8)
        out["three-quarter-rear-above"] = cam((110.0, 450.0, 450.0), 330, 140, 34)
        out["flare-foot"] = cam((d.width / 2 - 30, 420.0, 140.0), 210, 140, 14)
    if v.cut_ins:
        c = v.cut_ins
        out["closeup-cut-ins"] = cam((rear_side_x(d, 0) - v.corner_r / 2, d.body_d - v.corner_r / 2, c.z0 + c.pitch * (c.count - 1) / 2), 60, 145, 10)
    return out


REV6_CHECK = "cad/out/shell-bp-rev6/face-check.json"


def mark_inherited(found: list, path: str = REV6_CHECK, tol: float = 1.0) -> None:
    """Mark the findings that revision 6 has at the same place in plan (within tol; the base chamfer moves a face's
    centre up) under the same rule (from its face check): the parts in front of the step and the hood's corner
    method, which this study does not change."""
    if not os.path.exists(path):
        return
    old = [(f["rule"], f["at"]) for f in json.load(open(path))["findings"]]
    for f in found:
        if f.allowed:
            continue
        if any(r == f.rule and math.dist(a[:2], f.at[:2]) <= tol and abs(a[2] - f.at[2]) <= 2 * OVER for r, a in old):
            f.allowed = "inherited from revision 6 (stage 2)"
        elif f.part == "hood":
            f.allowed = "hood rear corner: revision 6 method with the new radius (stage 2)"


def export(out: str, parts: dict[str, Part.Shape], d: Blueprint, v: Variant, log: list[str]) -> dict:
    from tools import face_check
    os.makedirs(out, exist_ok=True)
    manifest, edges = {}, {}
    for k, s in parts.items():
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.05).write(os.path.join(out, f"{k}.stl"))
        s.exportBrep(os.path.join(out, f"{k}.brep"))
        manifest[k] = {"file": f"{k}.stl", "finish": FINISH[k], "brep": f"{k}.brep"}
        edges[k] = edge_polylines(s)
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    json.dump(edges, open(os.path.join(out, "edges.json"), "w"))
    json.dump(focus(d, v), open(os.path.join(out, "focus.json"), "w"), indent=1)
    found = []
    allow = face_check.default_reveals()
    for k, s in parts.items():
        found += face_check.check(s, k, allow)
    mark_inherited(found)
    json.dump({"summary": face_check.summary(found), "findings": [asdict(f) for f in found]}, open(os.path.join(out, "face-check.json"), "w"), indent=1)
    open(os.path.join(out, "face-check.md"), "w").write(face_check.report_md(found, f"candidate {v.name}"))
    report = {"variant": asdict(v), "hood_r": v.hood_r, "step_y0": d.step_y0, "log": log,
              "parts": {k: {"valid": s.isValid(), "solids": len(s.Solids), "faces": len(s.Faces), "volume_mm3": round(s.Volume, 1)} for k, s in parts.items()},
              "face_check_failures": len(face_check.failures(found))}
    json.dump(report, open(os.path.join(out, "report.json"), "w"), indent=1)
    return report


REV6 = "cad/out/shell-bp-rev6"
SECTION_PLANES = {"side x 0": (0, 0.0), "side x 120": (0, 120.0), "side x -205": (0, -205.0), "side x 228": (0, 228.0),
                  "plan z 50": (2, 50.0), "plan z 160": (2, 160.0), "plan z 300": (2, 300.0), "plan z 380": (2, 380.0)}


def prepare_rev6(out: str) -> None:
    """A model directory for revision 6 beside the candidates: its meshes (by absolute path), edges.json and the same
    close-up cameras as the candidates, so that the sheets show the three in the same views."""
    src = os.path.abspath(REV6)
    manifest = json.load(open(os.path.join(src, "manifest.json")))
    os.makedirs(out, exist_ok=True)
    edges = {}
    for k, e in manifest.items():
        sh = Part.Shape()
        sh.read(os.path.join(src, e["brep"]))
        edges[k] = edge_polylines(sh)
        e["file"] = os.path.join(src, e["file"])
        e["brep"] = os.path.join(src, e["brep"])
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    json.dump(edges, open(os.path.join(out, "edges.json"), "w"))
    v = replace(VARIANTS["A"], step_seam_y=Blueprint().step_y(Blueprint().body_top), crease_lo=(540.0, 310.0, 0.0), crease_hi=(580.0, 350.0, 0.0))
    json.dump(focus(Blueprint(), v), open(os.path.join(out, "focus.json"), "w"), indent=1)


def sections(model: str) -> dict:
    """The outer sections of the shell parts (all but the trim) at SECTION_PLANES, and the inner surface of a skin of
    wall_t as the 2D inward offset of each section (an estimate of the skin: cavity.py makes it from slabs). Each part
    is cut on its own (the parts of revision 6 do not fuse), so the offset is also drawn along the joints of the parts."""
    manifest = json.load(open(os.path.join(model, "manifest.json")))
    shell = [k for k in manifest if k in ("deck", "body", "front_body", "rear_body", "hood")]
    shapes = []
    for k in shell:
        sh = Part.Shape()
        sh.read(manifest[k]["brep"] if os.path.isabs(manifest[k]["brep"]) else os.path.join(model, manifest[k]["brep"]))
        shapes.append(sh)
    out = {}
    wall = Blueprint().wall_t
    for name, (axis, at) in SECTION_PLANES.items():
        n = V(*[1.0 if i == axis else 0.0 for i in range(3)])
        wires = [w for sh in shapes for w in sh.slice(n, at)]
        keep = [i for i in (0, 1, 2) if i != axis]
        loops, inner = [], []
        for w in wires:
            loops.append([[round(p[i], 2) for i in keep] for p in w.discretize(Distance=1.0)])
            try:
                f = Part.Face(w).makeOffset2D(-wall, 0, False, False, False)
                for iw in f.Wires:
                    inner.append([[round(p[i], 2) for i in keep] for p in iw.discretize(Distance=1.0)])
            except Part.OCCError:
                pass
        out[name] = {"axis": axis, "at": at, "outer": loops, "inner": inner}
    return out


def main() -> int:
    out = os.environ.get("CANDYBAR_OUT", "cad/out/shell-bp-rev7")
    step = os.environ.get("CANDYBAR_REAR_STEP", "build")
    if step == "rev6":
        prepare_rev6(os.path.join(out, "rev6"))
        return 0
    if step == "sections":
        for name in [n for n in os.environ.get("CANDYBAR_REAR", "rev6,A,R").split(",") if n]:
            json.dump(sections(os.path.join(out, name)), open(os.path.join(out, name, "sections.json"), "w"))
            print("sections", name)
        return 0
    names = [n for n in os.environ.get("CANDYBAR_REAR", ",".join(VARIANTS)).split(",") if n]
    ok = True
    for name in names:
        v = VARIANTS[name]
        log: list[str] = []
        parts = build(v, log)
        r = export(os.path.join(out, name), parts, blueprint(v), v, log)
        print(name, "; ".join(log), "| face check failures:", r["face_check_failures"])
        for k, p in r["parts"].items():
            print(f"   {k:14s} valid {p['valid']} solids {p['solids']} faces {p['faces']}")
        ok = ok and all(p["valid"] and p["solids"] == 1 for p in r["parts"].values())
    return 0 if ok else 1
