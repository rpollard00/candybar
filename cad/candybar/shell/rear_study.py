"""Rear form study (revision 7 candidates): the shell with a new rear, built with true rounds, for comparison only.

Blueprint() and profiles.faces() do not change: the default build stays revision 6. This module builds candidates
with the true dimensions of the shell (the tuck, the hood's rear outline, the seam groove) and its own rear:

  A   the present rear, repaired: the step ends on the hood seam in front of the corner round (the hood keeps its
      full width and overhangs the narrower rear body behind the step), the two creases of the rear slope are rounded,
      the step's edges get a small radius.
  R   the rear of the maker's mini inside the same envelope: the 40 mm overhang as a soft roll whose foot line is a
      smile, a larger corner round, two hand-hold recesses in the head, the cut-ins at the lower rear corners.

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
    note: str = ""

    @property
    def hood_r(self) -> float:
        """The hood keeps the full width; its round in plan is the body's round plus the step, so that both rounds
        leave the rear wall on the same line and the soffit grows from nothing at the rear to the step at the side."""
        return self.corner_r + Blueprint().step_in


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


def sharp_body(d: Blueprint, v: Variant) -> Part.Shape:
    """The body as one solid with the sharp rear: as solids.body, without the corner cutter, with the rear profile."""
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
    cutters = [so.both(so.rail_cutter(d, fr)), so.both(step_cutter(d)), plate, so.both(reveal), so.screen(d), rear_cutter(d, v)]
    return solid.cut(cutters).removeSplitter()


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
    s = sharp_body(d, v)
    if v.step_r:
        outer, inner = step_edges(d, s)
        log.append(f"step edges: {len(outer)} outer, {len(inner)} inner")
        s = s.makeFillet(v.step_r, outer).makeFillet(v.step_crease_r, step_edges(d, s.makeFillet(v.step_r, outer))[1]) if inner else s
    es = corner_edges(d, s)
    log.append(f"corner edges: {len(es)}")
    s = s.makeFillet(v.corner_r, es)
    if v.chamfer:
        es = floor_edges(s, d.foot_y - d.bend_t)
        log.append(f"floor edges: {len(es)}")
        s = s.makeChamfer(v.chamfer, es)
    g = d.seam_groove
    s = s.cut(so.ring_bevel(so.outline_at(s, d.body_top - g), d.body_top - g, d.body_top, g))
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
