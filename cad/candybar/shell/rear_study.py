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
class Band:
    """R3: the step as one band of one section from the floor to the rear. In side view its outer edge (on the
    full-width side) is one stroke of lines and arcs: an upright stub at the floor, an S (two arcs of foot_r) that
    leaves the floor `flare` behind the straight leaning line and joins it, the lean, a top arc of top_r, and a run
    back to the roll that falls toward the front at `fall`. The inner edge (on the recessed side) is that stroke offset
    by the step (12) toward the recess; the band between them is ruled square to the stroke: planes on the lines,
    cones on the arcs, so its section (45 degrees, 12 deep) is the same everywhere. The run's inner edge reaches the
    rear wall of the lower body (y body_d) run_dz above the roll's sharp lower crease there."""
    stub: float = 15.0
    flare: float = 80.0
    foot_r: float = 80.0
    top_r: float = 80.0
    poly: bool = False           # R7: the stroke as straight lines (stub, kick, lean, run) meeting on mitres, no arcs
    kick: float = 28.0           # poly: the kick's lean to the rear of upright, degrees
    fall: float = 0.36
    run_dz: float = -28.0
    inner_r: float = 7.0
    outer_r: float = 26.0


@dataclass(frozen=True)
class Shelf:
    """R4: the band's run and the roll's underside are one shelf under the head, at one height at the rear corner.
    The smile keeps R's curve up to `ease` before the point `flat` before the start of the corner round on the rear,
    then a tangent arc takes it to level there; the band's run arrives level at the same height. Under the head the body is the lower body's
    plan outline (corner R corner_r) tapered out at 45 degrees from that height: planes on the side and the rear, a
    right cone on the corner. Rounds: the lower crease is one chain round the corner, R inner_side on the band to
    R crease_lo on the roll; the upper edge is one chain, R outer_side on the band, R outer_corner where it passes the
    head's corner (a convex round there must stay under the corner's R 25), R crease_hi on the middle of the roll. The
    radius changes linearly along the corner and along the eased part of the smile."""
    ease: float = 40.0
    flat: float = 10.0
    inner_side: float = 7.0
    outer_side: float = 12.0
    outer_corner: float = 24.0
    constant: tuple[float, float] | None = (12.0, 20.0)   # (lower, upper): one radius per chain all round, in place of the laws
    joined: bool = True          # the shelf's corner as one B-spline from the band's level run to the swept roll (see shelf_cutter)


@dataclass(frozen=True)
class Planar:
    """R6, the mini's way: flat facets that meet on mitres, and one small round on every edge of the back (R `fillet`,
    against thin paint on a sharp edge). The shelf is the band's 45 degree facet on the side (12 deep) and the roll's
    45 degree facet on the rear (40 deep, the rear straight across), meeting on a hip line at the corner; above the
    band the rear facet runs on to the full-width side, where its end shows as a slanted edge. The cut-ins wrap the
    sharp corner on a mitre: `cut_side` along the side and `cut_rear` along the rear."""
    fillet: float = 3.0
    hip: float = 4.0             # the hip line's round: at R 3 its top corner (with the slanted edge and the band's edge) leaves a strip 1.0 wide
    cut_side: float = 30.0
    cut_rear: float = 20.0
    by_rule: bool = False        # R7: round only the edges that turn min_turn degrees or more (convex ones only, unless `concave`)
    min_turn: float = 40.0
    concave: bool = False
    cut_in_r: float = 0.0        # R7: the cut-ins' floor turns round the corner on this inner radius; 0: mitred legs (R6)
    low_corner: float = 0.0      # R7: the lower body's vertical rear corner on this radius (0: the small round); the cut-ins' path runs on it
    top_mitre: bool = False      # R7: also round the band's top mitre (concave, 43 degrees): left sharp, the band's outer round ends there in a strip 1.1 wide
    exact_corner: bool = False   # R8: the lower rear corner, the hip and the chamfer's mitre there made by hand (see exact_corner_cutter)
    ball_cut_ins: bool = False   # R8: cut-ins milled by a ball (ball_cut_ins)
    ball_path_r: float = 13.0    # the ball centre's turn round the corner
    grip_r: float = 0.0          # R8: the hand-holds' inside edges rounded on the cutter (the rim stays sharp)
    hood_whole: bool = False     # R8: the hood's corners rounded on both sides as one piece (no mirror line)
    round_ends: bool = False


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
    band: Band | None = None
    shelf: Shelf | None = None
    planar: Planar | None = None
    note: str = ""

    @property
    def hood_r(self) -> float:
        """The hood keeps the full width. Without a shoulder its round in plan is the body's round plus the step, so
        that both rounds leave the rear wall on the same line and the soffit grows from nothing at the rear to the step
        at the side. With a shoulder the head has the full width, and the head and the hood share one corner round."""
        if self.planar:
            return self.planar.fillet
        return self.corner_r if self.shoulder or self.band else self.corner_r + Blueprint().step_in


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
VARIANTS["R3"] = replace(VARIANTS["R2"], name="R3", title="R3: the step as one band from the floor to the roll", shoulder=None, band=Band(),
                         note="one band of the step's section: stub 15 at the floor, S of R 80, lean, top arc R 80, run back to the roll; "
                              "its lower crease reaches the rear wall 28 below the roll's (as high, the three rounds meet in faces of 1 to 2)")
VARIANTS["R4"] = replace(VARIANTS["R3"], name="R4", title="R4: one shelf under the head", band=replace(Band(), top_r=60.0, fall=0.0),
                         shelf=Shelf(), note="the band's run and the roll's underside are one 45 degree shelf, level at the rear corner")
VARIANTS["R5a"] = replace(VARIANTS["R4"], name="R5a", title="R5a: R4 with the rear straight across", smile=0.0,
                          band=replace(VARIANTS["R4"].band, top_r=65.0), shelf=replace(VARIANTS["R4"].shelf, constant=(3.0, 3.0), flat=0.0, joined=False),
                          note="no smile: the lower crease level at z 298 across the rear, round the corners and along the band's run; "
                               "band top arc R 65 (R 80 reaches level only after the corner round starts); the creases R 3 "
                               "(flat facets, round corners); the shelf is planes and a cone (no smile, so the rear planes merge)")
VARIANTS["R6"] = replace(VARIANTS["R3"], name="R6", title="R6: planar, the mini's way", smile=0.0, corner_r=3.0,
                         crease_lo=(540.0, 298.0, 0.0), crease_hi=(580.0, 338.0, 0.0), band=replace(Band(), top_r=65.0, fall=0.0, run_dz=0.0),
                         planar=Planar(), note="flat 45 degree facets meeting on a hip line at the rear corner, the rear straight "
                                               "across, sharp corners with R 3 on every edge of the back")
VARIANTS["R7"] = replace(VARIANTS["R6"], name="R7", title="R7: planar, the stroke in straight lines",
                         band=replace(VARIANTS["R6"].band, poly=True, stub=20.0, kick=28.0, flare=80.0),
                         planar=replace(Planar(), hip=4.0, by_rule=True, min_turn=40.0, cut_in_r=5.0, low_corner=8.0),
                         grips=replace(Grips(), z0=349.05),
                         note="the band's stroke as straight lines (stub 20, kick 28 to the rear, the lean, one mitre into the level run); "
                              "R 3 only on the convex edges that turn 40 degrees or more; hand-holds centred on the head's rear wall; "
                              "cut-ins with a round floor turning on R 10 round the corner")
VARIANTS["R8"] = replace(VARIANTS["R7"], name="R8", title="R8: R7 with exact corners, ball-milled cut-ins, rounded hand-holds",
                         planar=replace(VARIANTS["R7"].planar, hip=3.0, low_corner=0.0, exact_corner=True, ball_cut_ins=True, grip_r=8.0,
                                        hood_whole=True),
                         note="the lower rear corner, the hip and the chamfer mitre made by hand to meet exactly; cut-ins milled by a ball "
                              "round the sharp corner; hand-holds round inside, sharp at the rim; the hood's corners rounded in one piece")
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
    if v.shelf:
        return eased_smile(v, x, half)
    return v.smile * (abs(x) / half) ** v.smile_power


def shelf_x(v: Variant, half: float) -> tuple[float, float]:
    """Where the smile's ease starts and where it is level: `flat` before the start of the lower corner round on the
    rear, so that the swept roll ends on a plane of the taper and not on its cone."""
    xe = half - v.corner_r - v.shelf.flat
    return xe - v.shelf.ease, xe


def ease_arc(v: Variant, half: float) -> tuple[float, float, float]:
    """The tangent arc of the eased smile: centre x, centre z, radius (level at xe, tangent to R's smile at xt)."""
    xt, xe = shelf_x(v, half)
    zt = v.smile * (xt / half) ** v.smile_power
    m = v.smile * v.smile_power * xt ** (v.smile_power - 1) / half ** v.smile_power
    a = math.atan(m)
    rho = (xe - xt) / math.sin(a)
    ze = zt + rho * (1 - math.cos(a))
    return xe, ze - rho, rho


def eased_smile(v: Variant, x: float, half: float) -> float:
    if not v.smile:
        return 0.0
    x = abs(x)
    xt, xe = shelf_x(v, half)
    if x <= xt:
        return v.smile * (x / half) ** v.smile_power
    cx, cz, rho = ease_arc(v, half)
    if x >= xe:
        return cz + rho
    return cz + math.sqrt(rho * rho - (x - cx) ** 2)


def rear_cutter(d: Blueprint, v: Variant) -> Part.Shape:
    """What the rear profile takes off the plain rear: the region behind the profile, across the width (A) or swept
    along the smile with every section parallel (R). With a shelf (R4): the sharp profile (its creases are rounded
    later, as chains round the corner), swept only between the starts of the two lower corner rounds, along a spine
    of three edges (the eased ends and R's smile between), level at both ends; the shelf's taper takes the corners."""
    if v.shelf:
        return shelf_rear_cutter(d, v)
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


def shelf_rear_cutter(d: Blueprint, v: Variant) -> Part.Shape:
    lo, hi = v.crease_lo, v.crease_hi
    path = rounded([(d.depth, d.body_top + 3 * OVER, 0.0), (hi[0], hi[1], 0.0), (lo[0], lo[1], 0.0), (d.body_d, -3 * OVER, 0.0)])
    far = d.depth + 3 * OVER
    region = path + so.poly([so.ends(path[-1])[1], (far, -3 * OVER), (far, d.body_top + 3 * OVER)])[:-1]
    half = d.rear_w / 2
    xt, xe = shelf_x(v, half)
    if not v.smile:
        # the rear straight across (R5a): the sharp profile extruded between the starts of the corner rounds
        return so.prism(so.closed(region), so.yz(-xe), V(2 * xe, 0, 0))
    cx, cz, rho = ease_arc(v, half)
    at = lambda x: V(x, d.depth, eased_smile(v, x, half))
    left = Part.Arc(at(-xe), at(-(xt + xe) / 2), at(-xt)).toShape()
    right = Part.Arc(at(xt), at((xt + xe) / 2), at(xe)).toShape()
    mid = Part.BSplineCurve()
    t = right.tangentAt(right.FirstParameter)
    mid.interpolate(Points=[at(x) for x in (-xt + 2 * xt * k / 40 for k in range(41))], InitialTangent=V(t.x, 0, -t.z), FinalTangent=t)
    spine = Part.Wire([left, mid.toShape(), right])
    prof = so.wire(so.closed(region), lambda p: V(-xe, p[0], p[1] + eased_smile(v, xe, half)))
    ps = Part.BRepOffsetAPI.MakePipeShell(spine)
    ps.setTrihedronMode(V(0, 0, 0), V(1, 0, 0))
    ps.add(prof, False, False)
    ps.build()
    ps.makeSolid()
    return ps.shape()


def shelf_zc(d: Blueprint, v: Variant) -> float:
    """Height of the shelf's lower crease (sharp) at the rear corner: the roll's, with the eased smile."""
    return v.crease_lo[1] + eased_smile(v, d.rear_w / 2, d.rear_w / 2)


def shelf_cutter(d: Blueprint, v: Variant) -> Part.Shape:
    """What the shelf takes off the right rear corner, behind the start of the corner round on the rear (x > xe) and
    behind the level part of the band (y > y_level): all that is outside the taper of the lower body's plan outline.
    The taper is the outline (side x = rear_w/2, corner arc R corner_r, rear y = body_d) up to the crease height, and
    above it the ruled loft to that outline moved out by its rise: planes and a right cone on the arc."""
    a, r = d.rear_w / 2, v.corner_r
    xt, xe = shelf_x(v, a)
    zc = shelf_zc(d, v)
    y_level = band_level_y(d, v)
    c = (a - r, d.body_d - r)
    x0, y0, rise = xe - OVER, y_level - OVER, d.body_top + 2 * OVER - zc

    def outline(by: float, z: float, joined: bool) -> Part.Wire:
        """The outline moved out by `by` at height z. joined: the side line from where the band's run is level, the
        corner arc and the rear line to where the swept roll starts, as one exact rational B-spline: the seams of the
        shelf then do not fall on the seams of the walls (where both meet the crease at one point, the round leaves a
        filler face 0.1 wide), and each seam of the shelf is where its curvature changes (a plane cut in two would be a
        split)."""
        pts = lambda p: V(p[0], p[1], z)
        m = math.sqrt(0.5)
        p1, p2 = (a + by, y_level), (xe, d.body_d + by)
        circle = Part.Arc(pts((a + by, c[1])), pts((c[0] + (r + by) * m, c[1] + (r + by) * m)), pts((c[0], d.body_d + by)))
        if joined:
            # side line, the quarter arc as one rational segment, rear line: the same knots at every offset, so that
            # the ruled loft pairs points square to the outline (planes and an exact cone)
            q0, q1, q2, q3 = p1, (a + by, c[1]), (c[0], d.body_d + by), p2
            mid = lambda u, w: ((u[0] + w[0]) / 2, (u[1] + w[1]) / 2)
            poles = [pts(q) for q in (q0, mid(q0, q1), q1, (a + by, d.body_d + by), q2, mid(q2, q3), q3)]
            corner = Part.BSplineCurve()
            corner.buildFromPolesMultsKnots(poles, [3, 2, 2, 3], [0.0, 1.0, 2.0, 3.0], False, 2, [1.0, 1.0, 1.0, m, 1.0, 1.0, 1.0])
        else:
            corner = circle
            p1, p2 = (a + by, c[1]), (c[0], d.body_d + by)
        ring = [(x0 - by, y0 - by), (a + by, y0 - by), p1, p2, (x0 - by, d.body_d + by)]
        edges = [Part.LineSegment(pts(ring[0]), pts(ring[1])).toShape(), Part.LineSegment(pts(ring[1]), pts(ring[2])).toShape(), corner.toShape(),
                 Part.LineSegment(pts(ring[3]), pts(ring[4])).toShape(), Part.LineSegment(pts(ring[4]), pts(ring[0])).toShape()]
        return Part.Wire(edges)

    below = Part.Face(outline(0.0, -3 * OVER, False)).extrude(V(0, 0, zc + 3 * OVER))
    taper = Part.makeLoft([outline(0.0, zc, v.shelf.joined), outline(rise, zc + rise, v.shelf.joined)], True, True)
    keep = below.fuse(taper).removeSplitter()
    box = Part.makeBox(d.width / 2 + 2 * OVER - xe, d.depth + 3 * OVER - y_level, rise + zc + 3 * OVER, V(xe, y_level, -3 * OVER))
    return box.cut(keep)


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
    if v.shelf:
        # the head's rear corners first, as plan rounds from the floor to the body top; the cuts below take the lower part
        solid = solid.makeFillet(v.corner_r, edges_where(solid, lambda p: abs(abs(p.x) - d.side_x(p.z)) < ON and abs(p.y - d.depth) < ON))
    xb = d.bezel_w / 2 + d.panel_gap
    bw = d.bezel_w / 2
    plate = so.bezel_box(d, fr, -bw, bw).cut(so.behind_screen(d, d.mon_setback))
    reveal = so.bezel_box(d, fr, bw, xb).cut(so.land_cylinder(d, fr))
    step = band_cutter(d, v) if v.band else recess_cutter(d, v) if v.shoulder else step_cutter(d)
    if v.shelf:
        step = step.fuse(shelf_cutter(d, v)).removeSplitter()
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


# ---------- the band (R3) ----------

def band_path(d: Blueprint, v: Variant) -> pr.Path:
    """The outer edge of the band in side view, (y, z) on the full-width side, from below the floor to past the rear:
    stub, S (CCW arc then CW arc, both foot_r), lean (the step's outer edge line), top arc (CW, top_r), run."""
    b = v.band
    t = math.tan(math.radians(d.step_lean))
    lean = math.pi / 2 - math.radians(d.step_lean)            # direction of the lean, from +y toward +z
    line_y = lambda z: d.step_y0 + z * t
    if b.poly:
        return poly_stroke(d, v)
    yf, r, ls = line_y(0.0) + b.flare, b.foot_r, b.stub

    def s_curve(th: float) -> tuple[P2, P2, P2, P2]:
        c1 = (yf - r, ls)
        p1 = (c1[0] + r * math.cos(th), c1[1] + r * math.sin(th))
        c2 = (p1[0] + r * math.cos(th), p1[1] + r * math.sin(th))
        p2 = (c2[0] + r * math.cos(lean + math.pi / 2), c2[1] + r * math.sin(lean + math.pi / 2))
        return c1, p1, c2, p2

    off = lambda th: s_curve(th)[3][0] - line_y(s_curve(th)[3][1])
    lo, hi = 1e-6, math.radians(89.0)
    if off(lo) * off(hi) > 0:
        raise ValueError("no S curve joins the lean with these values")
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if off(lo) * off(mid) > 0 else (lo, mid)
    th = lo
    c1, p1, c2, p2 = s_curve(th)
    # top arc: tangent to the lean and to the run; the run's inner edge passes the rear wall at shoulder_z0
    phi = math.atan(b.fall)
    r3 = b.top_r
    nl = (math.sin(lean), -math.cos(lean))
    nr = (math.sin(phi), -math.cos(phi))
    z_inner = shelf_zc(d, v) if v.shelf else shoulder_z0(d, v) + b.run_dz
    q0 = (d.body_d - d.step_in * nr[0], z_inner - d.step_in * nr[1])
    a1, a2 = (line_y(0.0) + r3 * nl[0], r3 * nl[1]), (q0[0] + r3 * nr[0], q0[1] + r3 * nr[1])
    u1, u2 = (math.cos(lean), math.sin(lean)), (math.cos(phi), math.sin(phi))
    det = -u1[0] * u2[1] + u1[1] * u2[0]
    k = (-(a2[0] - a1[0]) * u2[1] + (a2[1] - a1[1]) * u2[0]) / det
    c3 = (a1[0] + k * u1[0], a1[1] + k * u1[1])
    p3 = (c3[0] - r3 * nl[0], c3[1] - r3 * nl[1])
    p4 = (c3[0] - r3 * nr[0], c3[1] - r3 * nr[1])
    far = d.depth + 3 * OVER
    p5 = (far, p4[1] + (far - p4[0]) * b.fall)
    return [pr.Line((yf, -OVER), (yf, ls)), pr.Arc(c1, r, 0.0, th), pr.Arc(c2, r, math.pi + th, lean + math.pi / 2),
            pr.Line(p2, p3), pr.Arc(c3, r3, lean + math.pi / 2, phi + math.pi / 2), pr.Line(p4, p5)]


def poly_stroke(d: Blueprint, v: Variant) -> pr.Path:
    """R7: the outer edge of the band in side view as straight lines: an upright stub `flare` behind the leaning line
    at the floor, a kick that leans `kick` degrees to the rear of upright, the lean, and a level run at the height of
    the shelf, each meeting the next on a mitre."""
    b = v.band
    t, k = math.tan(math.radians(d.step_lean)), math.tan(math.radians(b.kick))
    y0, yf, zs = d.step_y0, d.step_y0 + b.flare, b.stub
    zk = (yf + zs * k - y0) / (t + k)                          # knee: the kick (y = yf - (z - zs) k) meets the lean
    knee = (y0 + zk * t, zk)
    zo = v.crease_lo[1] + d.step_in                            # the run's outer edge: the inner crease is level at the shelf
    top = (y0 + zo * t, zo)
    far = d.depth + 3 * OVER
    return [pr.Line((yf, -OVER), (yf, zs)), pr.Line((yf, zs), knee), pr.Line(knee, top), pr.Line(top, (far, zo))]


def band_level_y(d: Blueprint, v: Variant) -> float:
    """Y where the band's run is level (the end of its top arc)."""
    return band_path(d, v)[-1].p[0]


def small_rounds(v: Variant) -> bool:
    """Whether the back's rounds are small (R6, R5a): smaller than the base chamfer + 3, so the chamfer is made first
    and the rounds end on it, and the S of the band is one face (a face boundary at its inflection with small rounds
    reads to the face check as one torus cut in two)."""
    return bool(v.planar or (v.shelf and v.shelf.constant and max(v.shelf.constant) < v.chamfer + 3))


def offset_path(path: pr.Path, by: float) -> pr.Path:
    """A path of lines and arcs moved by `by` to its left (negative: right). Tangent-continuous: lines keep their
    vector, so that a ruled loft between two offsets of one path gives planes on the lines and cones on the arcs. A
    polyline (R7): each line moved, and neighbours cut where they cross (mitre joins)."""
    moved = [so.offset_seg(sg, by) for sg in path]
    if not all(isinstance(sg, pr.Line) for sg in path):
        return moved

    def cross(l1: pr.Line, l2: pr.Line) -> P2:
        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = l1.p, l1.q, l2.p, l2.q
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(den) < 1e-12:
            return l1.q
        a, c = x1 * y2 - y1 * x2, x3 * y4 - y3 * x4
        return ((a * (x3 - x4) - (x1 - x2) * c) / den, (a * (y3 - y4) - (y1 - y2) * c) / den)

    pts = [moved[0].p] + [cross(moved[i], moved[i + 1]) for i in range(len(moved) - 1)] + [moved[-1].q]
    return [pr.Line(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]


def band_cutter(d: Blueprint, v: Variant) -> Part.Shape:
    """What the band takes off the right side: the region outside the recessed side (x > rear_w / 2) and on the recess
    side of the band. That region is ruled between its sections at x = W + e and x = rear_w/2 - e: the region to the
    right of the stroke, moved by the stroke's offset at that x (the band runs in by one for each one it runs back
    or down, square to the stroke), so the loft gives planes and cones."""
    path = band_path(d, v)
    W, a, e = d.width / 2, d.rear_w / 2, OVER / 10

    def section(x: float) -> Part.Wire:
        moved = offset_path(path, -(W - x))
        start, end = so.ends(moved[0])[0], so.ends(moved[-1])[1]
        region = moved + [pr.Line(end, (end[0], -OVER)), pr.Line((end[0], -OVER), start)]
        w = so.wire(region, so.yz(x))
        if not small_rounds(v) or not isinstance(path[1], pr.Arc):
            return w
        # the two arcs of the S as one rational B-spline (the same knots in every section): with small rounds, a
        # face boundary at the S's inflection reads to the face check as one torus cut in two
        es = w.Edges
        s_curve = es[1].Curve.toBSpline(es[1].FirstParameter, es[1].LastParameter)
        s_curve.join(es[2].Curve.toBSpline(es[2].FirstParameter, es[2].LastParameter))
        return Part.Wire([es[0], s_curve.toShape()] + es[3:])

    behind = Part.makeLoft([section(W + e), section(a - e)], True, True)
    return so.halfspace(V(a, 0, 0), V(1, 0, 0)).common(behind)


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
    if v.band:
        if d.rear_w / 2 + 0.05 < c.x < d.width / 2 - 0.05 and isinstance(f.Surface, (Part.Plane, Part.Cone)) and abs(n.x) < 0.99:
            return "B"
        if isinstance(f.Surface, Part.Plane) and abs(abs(n.x) - 1) < 1e-6 and abs(c.x - d.rear_w / 2) < 0.5:
            return "X"
        if abs(n.x) > 0.95 and c.x > d.width / 2 - 6:
            return "W"
        return ""
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


def shelf_face_kind(f: Part.Face, d: Blueprint, v: Variant) -> str:
    """L: a wall of the lower body (recessed side, its corner round, the lower rear wall); U: a wall of the head (the
    full-width side, its corner round, the upper rear wall); S: the band or the shelf (the faces between them); ""
    for any other face. Mirrored to the right side. shelf_edges keeps only edges behind the old leaning step line."""
    u0, u1, v0, v1 = f.ParameterRange
    c = f.valueAt((u0 + u1) / 2, (v0 + v1) / 2)
    n = f.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
    if c.x < 0:
        c, n = V(-c.x, c.y, c.z), V(-n.x, n.y, n.z)
    a, W, r = d.rear_w / 2, d.width / 2, v.corner_r
    plane = isinstance(f.Surface, Part.Plane)
    if (plane and abs(abs(n.x) - 1) < 1e-6 and abs(c.x - a) < 0.5) \
            or (isinstance(f.Surface, Part.Cylinder) and abs(f.Surface.Radius - r) < 1e-6 and abs(f.Surface.Center.y - (d.body_d - r)) < 1e-3) \
            or (plane and abs(abs(n.y) - 1) < 1e-6 and abs(c.y - d.body_d) < 1e-3):
        return "L"
    if (abs(n.x) > 0.95 and c.x > W - 6) or (plane and abs(abs(n.y) - 1) < 1e-6 and abs(c.y - d.depth) < 1e-3) \
            or (isinstance(f.Surface, (Part.Cylinder, Part.Toroid)) and c.x > W - r - 1 and c.y > d.depth - r - 1):
        return "U"
    if a + 0.05 < c.x < W - 0.05 or (d.body_d + 1 < c.y < d.depth - 1) or isinstance(f.Surface, Part.Cone):
        return "S"
    return ""


def shelf_radius(d: Blueprint, v: Variant, p: FreeCAD.Vector, upper: bool) -> float:
    """The radius of a crease round at a point of its edge (right side; x mirrored)."""
    sh, a, r = v.shelf, d.rear_w / 2, v.corner_r
    x, y = abs(p.x), p.y
    cx, cy = a - r, d.body_d - r
    xt, xe = shelf_x(v, a)
    if not upper:
        # from the side's R round the corner arc and the flat before it to the roll's R, linear in length along the crease
        arc, flat = r * math.pi / 2, cx - xe
        if y <= cy + 1e-6 and x > cx:
            along = 0.0
        elif x >= cx - 1e-6 and y > cy:
            along = r * math.atan2(y - cy, x - cx)
        elif x >= xe - 1e-6:
            along = arc + (cx - x)
        else:
            return v.crease_lo[2]
        return sh.inner_side + (v.crease_lo[2] - sh.inner_side) * along / (arc + flat)
    W, ch = d.width / 2, d.depth - r
    hx = W - r                                  # where the head's corner round starts on the rear
    if y <= cy + 1e-6 and x > a:
        return sh.outer_side
    if x > hx - 1e-6 and y < ch - 1e-6:
        return sh.outer_side + (sh.outer_corner - sh.outer_side) * (y - cy) / (ch - cy)
    if x >= hx - 1e-6:
        return sh.outer_corner
    if x >= xt:
        return sh.outer_corner + (v.crease_hi[2] - sh.outer_corner) * (hx - x) / (hx - xt)
    return v.crease_hi[2]


def chain_order(edges: list[Part.Edge]) -> list[tuple[Part.Edge, FreeCAD.Vector, FreeCAD.Vector]]:
    """The edges of one open chain in walking order from its end on the right side at the floor (largest x, then
    lowest z), each with the vertex it is entered at and the one it is left at."""
    key = lambda p: (round(p.x, 4), round(p.y, 4), round(p.z, 4))
    ends: dict = {}
    for e in edges:
        for vx in (e.Vertexes[0], e.Vertexes[-1]):
            ends.setdefault(key(vx.Point), []).append(e)
    free = [k for k, es in ends.items() if len(es) == 1]
    start = min(free, key=lambda k: (-(k[0] > 0), k[2], -k[0]))
    out, at, used = [], start, set()
    while True:
        nxt = [e for e in ends.get(at, []) if e.hashCode() not in used]
        if not nxt:
            break
        e = nxt[0]
        used.add(e.hashCode())
        p0, p1 = e.Vertexes[0].Point, e.Vertexes[-1].Point
        a, b = (p0, p1) if key(p0) == at else (p1, p0)
        out.append((e, a, b))
        at = key(b)
    return out


def law_fillet(s: Part.Shape, edges: list[Part.Edge], radius, probes: list[tuple[FreeCAD.Vector, float]] = ()) -> Part.Shape:
    """A round on one open chain whose radius runs linearly along each edge between radius() at its two ends (a
    Part::Fillet feature: OpenCascade's linear law per edge). OpenCascade lays the two radii of an edge along the
    chain's own direction, which is not known here, so the chain is walked from its end on the right floor and the
    round is made both ways; the one whose radius at the probe points is nearest to what is wanted is kept."""
    walk = chain_order(edges)
    if len(walk) != len(edges):
        raise ValueError(f"the edges are not one open chain ({len(walk)} of {len(edges)} walked)")
    index = {}
    for i, e in enumerate(s.Edges):
        index.setdefault(e.hashCode(), i + 1)
    made = []
    for forward in (True, False):
        doc = FreeCAD.newDocument("law_fillet")
        try:
            base = doc.addObject("Part::Feature", "base")
            base.Shape = s
            fl = doc.addObject("Part::Fillet", "fillet")
            fl.Base = base
            seq = walk if forward else [(e, b, a) for e, a, b in reversed(walk)]
            fl.Edges = [(index[e.hashCode()], radius(a), radius(b)) for e, a, b in seq]
            doc.recompute()
            out = fl.Shape.copy()
        finally:
            FreeCAD.closeDocument(doc.Name)
        if out.isNull() or not out.isValid():
            continue
        miss = sum(abs(radius_at(out, p) - r) for p, r in probes)
        made.append((miss, out))
    if not made:
        raise Part.OCCError("law fillet failed both ways")
    return min(made, key=lambda m: m[0])[1]


def crease_angle(faces: list[Part.Face], p: FreeCAD.Vector) -> float:
    """Angle in degrees between the normals of two faces at a point of their common edge (0: tangent)."""
    ns = [f.normalAt(*f.Surface.parameter(p)) for f in faces]
    return math.degrees(math.acos(max(-1.0, min(1.0, abs(ns[0].dot(ns[1]))))))


def shelf_edges(s: Part.Shape, d: Blueprint, v: Variant, wall: str) -> list[Part.Edge]:
    out = []
    for e in s.Edges:
        fs = s.ancestorsOfType(e, Part.Face)
        m = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
        if len(fs) == 2 and not e.Degenerated and e.BoundBox.ZMax > 1e-3 and m.y > d.step_y(m.z) - 1:
            ks = sorted(shelf_face_kind(f, d, v) for f in fs)
            if ks == sorted([wall, "S"]) and crease_angle(fs, m) > 5.0:
                out.append(e)
    return out


def shelf_body(d: Blueprint, v: Variant, log: list[str]) -> Part.Shape:
    """The body of a shelf variant with its rounds, up to the base chamfer: the sharp body (head corners and the lower
    corner round already in it), then the lower crease (one chain round each corner) and the upper edge (one chain),
    each with its radius law."""
    s = sharp_body(d, v)
    if small_rounds(v):
        es = floor_edges(s, d.foot_y - d.bend_t)
        log.append(f"floor edges: {len(es)} (before the small rounds)")
        s = s.makeChamfer(v.chamfer, es)
    for k, (name, wall, upper) in enumerate((("lower crease", "L", False), ("upper edge", "U", True))):
        es = shelf_edges(s, d, v, wall)
        if small_rounds(v):
            es = [e for e in es if e.BoundBox.ZMax > v.chamfer + 0.01]
        if v.shelf.constant:
            log.append(f"{name}: {len(es)} edges, R {v.shelf.constant[k]:g}")
            s = s.makeFillet(v.shelf.constant[k], es)
        else:
            log.append(f"{name}: {len(es)} edges, radius law")
            rad = lambda p, u=upper: shelf_radius(d, v, p, u)
            s = law_fillet(s, es, rad, shelf_probes(d, v, upper, rad))
    return s


def shelf_probes(d: Blueprint, v: Variant, upper: bool, rad) -> list[tuple[FreeCAD.Vector, float]]:
    """Points just off the sharp crease where the round's radius changes, with the radius wanted there."""
    a, r, W = d.rear_w / 2, v.corner_r, d.width / 2
    cx, cy = a - r, d.body_d - r
    xt, xe = shelf_x(v, a)
    zc = shelf_zc(d, v)
    if not upper:
        q = V(cx + r * math.cos(math.pi / 4), cy + r * math.sin(math.pi / 4), zc)
        x = (xt + xe) / 2
        return [(q, rad(q)), (V(x, d.body_d, v.crease_lo[1] + eased_smile(v, x, a)), rad(V(x, d.body_d, 0)))]
    x = (xt + W - r) / 2
    p = V(x, d.depth, v.crease_hi[1] + eased_smile(v, x, a))
    return [(p, rad(p))]


def band_body(d: Blueprint, v: Variant, log: list[str]) -> Part.Shape:
    """The body of a band variant with its rounds, up to the base chamfer: as shoulder_body, with two chains on the
    right side (the recessed edge and the full-width edge of the band, each from the floor to the rear), the mirror,
    the rear cut and the corner."""
    b = v.band
    s = sharp_body(d, v, rear=False, right_only=True)
    for name, side, r in (("recessed edge", "X", b.inner_r), ("full-width edge", "W", b.outer_r)):
        es = [e for e in kind_edges(s, d, v, side, ("B",)) if e.BoundBox.Center.x > 0]
        log.append(f"{name}: {len(es)} edges, R {r:g}")
        s = s.makeFillet(r, es)
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


def edge_turn(s: Part.Shape, e: Part.Edge) -> tuple[bool, float]:
    """(convex, turn in degrees) of an edge between two faces of a solid, at its middle: convex when the first face,
    followed away from the edge, falls behind the second face's outward normal."""
    fs = s.ancestorsOfType(e, Part.Face)
    m = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
    t = e.tangentAt((e.FirstParameter + e.LastParameter) / 2)
    n = []
    for f in fs:
        u, w = f.Surface.parameter(m)
        n.append(f.normalAt(u, w))          # normalAt already follows the face's orientation
    away = n[0].cross(t)
    away.normalize()
    if fs[0].distToShape(Part.Vertex(m + away * 0.3))[0] > fs[0].distToShape(Part.Vertex(m - away * 0.3))[0]:
        away = -away
    return away.dot(n[1]) < 0, crease_angle(fs, m)


def planar_edges(s: Part.Shape, d: Blueprint, top_edges: bool = False) -> list[Part.Edge]:
    """Every sharp edge of the back (R6): behind the old leaning step line or on the rear, below the seam bevel, above
    the base chamfer. The rounds of the vertical corners end on the chamfer and its mitre stays sharp: run on down
    the chamfer's hip edges, they meet the chamfer's sharp top edge in needles (0 degrees) and slivers of 0.3 and 1.7.
    top_edges (R7): also the edges that run up to the body top (the head's vertical corner; R6 left it sharp), but not
    those that lie at the top."""
    out = []
    for e in s.Edges:
        if e.Degenerated:
            continue
        m = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
        b = e.BoundBox
        if (b.ZMin if top_edges else b.ZMax) > d.body_top - d.seam_groove - 0.5 or b.ZMax < 5.01 + 1e-3:
            continue
        if not (m.y > d.step_y(m.z) - 1 or m.y > d.body_d - 1):
            continue
        fs = s.ancestorsOfType(e, Part.Face)
        if len(fs) == 2 and crease_angle(fs, m) > 5.0:
            out.append(e)
    return out


def body(d: Blueprint, v: Variant, log: list[str]) -> Part.Shape:
    if v.planar:
        return planar_body(d, v, log)
    s = shelf_body(d, v, log) if v.shelf else band_body(d, v, log) if v.band else shoulder_body(d, v, log) if v.shoulder else sharp_body(d, v)
    if v.step_r and not (v.shoulder or v.band):
        outer, inner = step_edges(d, s)
        log.append(f"step edges: {len(outer)} outer, {len(inner)} inner")
        s = s.makeFillet(v.step_r, outer).makeFillet(v.step_crease_r, step_edges(d, s.makeFillet(v.step_r, outer))[1]) if inner else s
    if not (v.shoulder or v.band):
        es = corner_edges(d, s)
        log.append(f"corner edges: {len(es)}")
        s = s.makeFillet(v.corner_r, es)
    if v.chamfer and not small_rounds(v):
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


def planar_body(d: Blueprint, v: Variant, log: list[str]) -> Part.Shape:
    """R6: the sharp body of planes (the band, the rear profile straight across, sharp vertical corners), the base
    chamfer on the sharp corners (it mitres), then one small round on every edge of the back, the chamfer's hip
    edges at the corners with it; then the seam bevel, the cut-ins and the grips as for the others."""
    s = sharp_body(d, v)
    es = floor_edges(s, d.foot_y - d.bend_t)
    log.append(f"floor edges: {len(es)}")
    s = s.makeChamfer(v.chamfer, es)
    a, p = d.rear_w / 2, v.planar
    if p.exact_corner:
        s = s.cut(exact_corner_cutter(d, v))
        log.append(f"lower rear corners by hand: hip and chamfer mitre R {p.fillet:g}, the column on their ellipse "
                   f"({math.sqrt(3) * p.fillet:.2f} x {p.fillet:g}, tangent at {p.fillet / math.sqrt(2):.2f} from the corner)")
    es = planar_edges(s, d)
    if p.exact_corner:
        zc, y0, W = v.crease_lo[1], d.body_d, d.width / 2
        hand = lambda m: (abs(abs(m.x) - a) < 4 and abs(m.y - y0) < 4 and m.z < zc + 4) or \
            (abs((abs(m.x) - a) - (m.y - y0)) < 2.5 and zc - 1 < m.z < zc + d.step_in + 1 and abs(m.x) < W - 2)
        es = [e for e in es if not hand(e.valueAt((e.FirstParameter + e.LastParameter) / 2))]
    if p.by_rule:
        top = band_path(d, v)[-1].p                       # the band's top mitre, in (y, z) on the full-width side
        at_top = lambda e: abs(e.BoundBox.ZMax - top[1]) < 0.5 and e.BoundBox.ZLength > 5 and abs(e.BoundBox.YMax - top[0] - d.step_in * 0.0) < 15
        es = [e for e in es if (lambda c: (c[0] or p.concave or (p.top_mitre and at_top(e))) and c[1] >= p.min_turn)(edge_turn(s, e))]

    def radius(e: Part.Edge) -> float:
        m = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
        hip = abs((abs(m.x) - a) - (m.y - d.body_d)) < 1.0 and v.crease_lo[1] - 1 < m.z < v.crease_lo[1] + d.step_in + 2
        low = p.low_corner and abs(abs(m.x) - a) < 0.3 and abs(m.y - d.body_d) < 0.3 and e.BoundBox.ZLength > 50
        return p.hip if hip else p.low_corner if low else p.fillet

    log.append(f"small rounds: {len(es)} edges, R {p.fillet:g}, the hip R {p.hip:g}")
    s = radius_fillet(s, es, radius)
    g = d.seam_groove
    s = s.cut(so.ring_bevel(so.outline_at(s, d.body_top - g), d.body_top - g, d.body_top, g))
    if not s.isValid():
        s.fix(1e-7, 1e-7, 1e-7)
        log.append(f"seam bevel: shape fixed (valid {s.isValid()})")
    if p.by_rule:
        # the head's vertical rear corners (R6 left them sharp): after the seam bevel, so that the bevel, lofted through
        # points of the outline, does not have to follow a small round (it meets one at 2 degrees)
        W, top = d.width / 2, d.body_top - g
        es = [e for e in s.Edges if not e.Degenerated and e.BoundBox.ZLength > 20 and e.BoundBox.ZMin > v.crease_hi[1] - 1
              and abs(e.BoundBox.Center.x) > W - 15 and e.BoundBox.YLength < 0.5 and abs(e.BoundBox.Center.y - d.depth) < 0.5]
        log.append(f"head corners: {len(es)} edges, R {p.fillet:g}")
        s = s.makeFillet(p.fillet, es)
    if v.cut_ins:
        s = s.cut(so.both(ball_cut_ins(d, v) if p.ball_cut_ins else planar_cut_ins(d, v)))
    if v.grips:
        s = s.cut(so.both(grip_cutter(d, v)))
    return s.removeSplitter()


def round_cutter(p0: FreeCAD.Vector, p1: FreeCAD.Vector, n1: FreeCAD.Vector, n2: FreeCAD.Vector, r: float, ext0: float = 0.0,
                 ext1: float = 0.0, e: float = 1.0) -> Part.Shape:
    """What a round of radius r takes off a straight convex edge p0-p1 between two planes with outward normals n1, n2:
    the region between the edge and the round's cylinder (reaching e out past both faces), a prism along the edge
    from ext0 before p0 to ext1 past p1."""
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


def exact_corner_cutter(d: Blueprint, v: Variant) -> Part.Shape:
    """R8: what the rounds of the lower rear corner take off, made by hand so that they meet exactly. The hip (between
    the two 45 degree facets) and the chamfer's mitre at the base (between two 45 degree chamfer faces, parallel to the
    facets) get a round of R; each cut by a level plane (the crease, the top of the chamfer) is an ellipse, centre
    (a - 2r, y0 - 2r) with r = R / sqrt(2), semi-axes sqrt(3) R along the diagonal and R across, tangent to both walls
    at r from the corner. The lower vertical corner between them is that ellipse carried straight up, so it meets the
    hip's round and the chamfer mitre's round on the same curve: no ledge and no needle. (A circular R r there meets
    the creases at the same points but stands up to 0.035 r proud of the hip's round between them.)"""
    a, y0, zc, ch = d.rear_w / 2, d.body_d, v.crease_lo[1], v.chamfer
    big, k = 4000.0, math.sqrt(0.5)
    big_r = v.planar.fillet
    rr = big_r / math.sqrt(2)
    level = lambda z0, z1: Part.makeBox(big, big, z1 - z0, V(-big / 2, -big / 2, z0))
    out = []
    for sx in (1, -1):
        X = lambda p: V(sx * p.x, p.y, p.z)
        hip_top = V(d.width / 2, y0 + d.width / 2 - a, zc + d.width / 2 - a)
        hip = round_cutter(X(V(a, y0, zc)), X(hip_top), V(sx * k, 0, -k), V(0, k, -k), big_r, 3.0, 5.0)
        mitre = round_cutter(X(V(a, y0, ch)), X(V(a - ch, y0 - ch, 0)), V(sx * k, 0, -k), V(0, k, -k), big_r, 3.0, 2.0)
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


def radius_fillet(s: Part.Shape, edges: list[Part.Edge], radius) -> Part.Shape:
    """Rounds of a constant radius on each edge, radius(edge), in one builder (a Part::Fillet feature)."""
    index = {}
    for i, e in enumerate(s.Edges):
        index.setdefault(e.hashCode(), i + 1)
    doc = FreeCAD.newDocument("radius_fillet")
    try:
        base = doc.addObject("Part::Feature", "base")
        base.Shape = s
        fl = doc.addObject("Part::Fillet", "fillet")
        fl.Base = base
        fl.Edges = [(index[e.hashCode()], radius(e), radius(e)) for e in edges]
        doc.recompute()
        out = fl.Shape.copy()
    finally:
        FreeCAD.closeDocument(doc.Name)
    if out.isNull() or not out.isValid():
        raise Part.OCCError("rounds failed")
    return out


def planar_hood(d: Blueprint, v: Variant, log: list[str]) -> dict[str, Part.Shape]:
    """The hood of solids.hood with sharp rear corners and the small round on them (R6), in place of the corner loft:
    the cap's rear corner edges, from the foot over the rear arc to the roof, rounded with makeFillet."""
    h = pr.hood(d)
    side, corner, top = pr.hood_outline(d, h.height, h.half_base)
    lean = side.a0 if isinstance(side, pr.Arc) else math.atan2(side.p[0] - side.q[0], side.q[1] - side.p[1])
    drop = OVER * 2
    foot = (h.half_base + drop * math.tan(lean), -drop)
    outline = so.both_sides([pr.Line(foot, (h.half_base, 0.0)), side, corner, top])
    profile = [pr.Conic((d.hood_edge_in, 0.0), (0.0, 0.0), (0.0, d.hood_edge_back)), pr.Line((0.0, d.hood_edge_back), (0.0, h.depth + OVER))]
    shell = so.evolved(outline, profile)
    turn = FreeCAD.Matrix(-1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0)
    shell = so.leaning(shell.transformed(turn), h, d)
    side_view = pr.hood_side_profile(d, h.height, h.depth, d.hood_h - d.seam_gap)
    side_view = [pr.Line((-OVER, 0.0), (-OVER, h.height)), pr.Line((-OVER, h.height), side_view[4].q)] + side_view[5:] + [pr.Line((h.depth, 0.0), (-OVER, 0.0))]
    cap = shell.common(so.across(side_view))
    def corner_chain(shape: Part.Shape, sign: int) -> list[Part.Edge]:
        out = []
        for e in shape.Edges:
            b = e.BoundBox
            if e.Degenerated or b.Center.x * sign < 100 or b.YMax < h.depth - 60:
                continue
            fs = shape.ancestorsOfType(e, Part.Face)
            if len(fs) != 2:
                continue
            m = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
            ns = [f.normalAt(*f.Surface.parameter(m)) for f in fs]
            if sorted(abs(n.y) > abs(n.x) for n in ns) == [False, True] and crease_angle(fs, m) > 5.0:
                out.append(e)
        return out

    g = d.seam_groove
    cap = cap.cut(so.ring_bevel(so.outline_at(cap, g), g, 0.0, g))
    opening = so.prism(so.both_sides(so.opening_path(d, h)), so.xz(-OVER), V(0, BIG / 4, 0))
    recess = opening.common(so.across(so.poly(so.recess_profile(d, h))))
    cap = cap.cut(recess).removeSplitter()
    # the small round on the rear corners last, one side at a time (both in one call fails), kept only when both
    # sides come out valid and pass the boolean check. Rounded on the sharp cap, the round makes it unorientable and
    # the cuts of the seam groove and the recess fail; rounded last, the right side builds but the left (the same
    # chain, mirrored) does not, so both stay sharp rather than a hood that is not symmetric.
    if v.planar.hood_whole:
        # R8: round the right corner, mirror that cap and keep what both have: both corners round, every face crossing
        # the centre plane is the cap's own (no mirror line)
        try:
            right = cap.makeFillet(v.planar.fillet, corner_chain(cap, 1))
            if not right.isValid():
                right.fix(1e-7, 1e-7, 1e-7)
            whole = right.common(right.mirror(V(0, 0, 0), V(1, 0, 0))).removeSplitter()
            if not whole.isValid():
                whole.fix(1e-7, 1e-7, 1e-7)
            try:
                whole.check(True)
            except (ValueError, RuntimeError, Part.OCCError):
                whole = Part.Shape()
            if not whole.isNull() and whole.isValid() and len(whole.Solids) == 1:
                cap = whole
                log.append(f"hood rear corners: R {v.planar.fillet:g}, the cap rounded on the right and kept in common with its mirror")
            else:
                log.append("hood rear corners: the common with the mirror does not pass the check, even after ShapeFix; left sharp")
        except Part.OCCError as ex:
            log.append(f"hood rear corners: the round failed ({str(ex).splitlines()[0][:50]}); left sharp")
        rounded_cap, notes = None, []
    elif v.planar.by_rule:
        # R7: round the right half and mirror it (the mirrored chain does not round)
        try:
            right = cap.makeFillet(v.planar.fillet, corner_chain(cap, 1))
            if not right.isValid():
                right.fix(1e-7, 1e-7, 1e-7)
            half = right.common(so.halfspace(V(0, 0, 0), V(1, 0, 0)))
            whole = half.fuse(half.mirror(V(0, 0, 0), V(1, 0, 0))).removeSplitter()
            if whole.isValid() and len(whole.Solids) == 1:
                cap = whole
                log.append(f"hood rear corners: R {v.planar.fillet:g}, the right half rounded and mirrored")
            else:
                log.append(f"hood rear corners: the mirrored half is not one valid solid ({len(whole.Solids)} solids); left sharp")
        except Part.OCCError as ex:
            log.append(f"hood rear corners: the round of the right half failed ({str(ex).splitlines()[0][:50]}); left sharp")
        rounded_cap, notes = None, []
    else:
        rounded_cap, notes = cap, []
    for sign in ((1, -1) if rounded_cap is not None else ()):
        es = corner_chain(rounded_cap, sign)
        name = "right" if sign > 0 else "left"
        try:
            trial = rounded_cap.makeFillet(v.planar.fillet, es)
            trial.check(True)
            rounded_cap = trial
            notes.append(f"{name} R {v.planar.fillet:g} ({len(es)} edges)")
        except (Part.OCCError, ValueError, RuntimeError) as ex:
            notes.append(f"{name} failed ({str(ex).splitlines()[0][:50]})")
            rounded_cap = None
            break
    if not (v.planar.by_rule or v.planar.hood_whole):
        if rounded_cap is not None:
            cap = rounded_cap
        log.append("hood rear corners: " + "; ".join(notes) + ("" if rounded_cap is not None else "; both left sharp"))
    xr = h.half_open(h.z_band_top, d) + OVER
    lip = Part.makeBox(2 * xr, d.hood_rail_proud, h.z_rail_top - h.z_band_top, V(-xr, h.y_band_top - d.hood_rail_proud, h.z_band_top)).common(opening)
    out = {"hood": cap, "marquee_lip": lip.removeSplitter()}
    out.update(so.band_forms(d, h))
    return {k: so.hood_frame(h)(sh) for k, sh in out.items()}


def planar_cut_ins(d: Blueprint, v: Variant) -> Part.Shape:
    """The right row of cut-ins round the sharp lower rear corner (R6): each groove is two straight legs, one along the
    rear and one along the side, with the section of cut_in_cutter (round floor, back wall, 45 degree roof), joined on
    the corner's mitre plane. The legs end on planes square to them."""
    c, p = v.cut_ins, v.planar
    a, y0 = d.rear_w / 2, d.body_d
    dp, h = c.depth, c.height
    mid = (dp * math.sin(math.pi / 4), dp * (1 - math.cos(math.pi / 4)))
    if p.cut_in_r:
        return round_cut_ins(d, v)
    out = []
    for k in range(c.count):
        z = c.z0 + k * c.pitch

        def leg(origin: FreeCAD.Vector, inward: FreeCAD.Vector, along: FreeCAD.Vector, length: float) -> Part.Shape:
            at = lambda q: origin + inward * q[0] + V(0, 0, z + q[1])
            sec = Part.Wire([Part.Arc(at((0.0, 0.0)), at(mid), at((dp, dp))).toShape(), Part.LineSegment(at((dp, dp)), at((dp, h - dp))).toShape(),
                             Part.LineSegment(at((dp, h - dp)), at((0.0, h))).toShape(), Part.LineSegment(at((0.0, h)), at((-OVER, h))).toShape(),
                             Part.LineSegment(at((-OVER, h)), at((-OVER, 0.0))).toShape(), Part.LineSegment(at((-OVER, 0.0)), at((0.0, 0.0))).toShape()])
            return Part.Face(sec).extrude(along * length)

        rear = leg(V(a - p.cut_rear, y0, 0), V(0, -1, 0), V(1, 0, 0), p.cut_rear + 2 * OVER)
        side = leg(V(a, y0 - p.cut_side, 0), V(-1, 0, 0), V(0, 1, 0), p.cut_side + 2 * OVER)
        mitre = so.halfspace(V(a, y0, 0), V(1, -1, 0))          # the side of the corner's bisector toward the side
        out.append(rear.cut(mitre).fuse(side.common(mitre)).removeSplitter())
    return out[0].fuse(out[1:]).removeSplitter()


def ball_cut_ins(d: Blueprint, v: Variant) -> Part.Shape:
    """R8: the right row of cut-ins, milled by a ball: a ball of radius sqrt(2) h / 2 whose centre runs h / 2 outside the
    wall, so the slot on the wall is h high and the groove's roof leaves the upper edge at 45 degrees. The centre runs
    along the rear, turns the corner on ball_path_r about a centre set inward (so the floor turns on ball_path_r minus
    the ball and the groove is deepest at the corner), and along the side; a sphere at each end (round ends). The legs
    are cut_rear and cut_side long to the ends of the slot on the wall."""
    c, p = v.cut_ins, v.planar
    a, y0, h = d.rear_w / 2, d.body_d, c.height
    rho, out = math.sqrt(2) * h / 2, h / 2
    rp = p.ball_path_r
    cx, cy = a + out - rp, y0 + out - rp                     # the centre of the path's turn
    end = math.sqrt(rho * rho - out * out)                   # how far the slot reaches past the ball's last centre
    tubes = []
    for k in range(c.count):
        z = c.z0 + k * c.pitch + h / 2
        p0, p1 = V(a - p.cut_rear + end, y0 + out, z), V(cx, y0 + out, z)
        p2, p3 = V(a + out, cy, z), V(a + out, y0 - p.cut_side + end, z)
        m = math.sqrt(0.5)
        path = Part.Wire([Part.LineSegment(p0, p1).toShape(), Part.Arc(p1, V(cx + rp * m, cy + rp * m, z), p2).toShape(),
                          Part.LineSegment(p2, p3).toShape()])
        ring = Part.Wire([Part.Circle(p0, V(1, 0, 0), rho).toShape()])
        tube = path.makePipeShell([ring], True, True)
        tubes.append(tube.fuse([Part.makeSphere(rho, p0), Part.makeSphere(rho, p3)]).removeSplitter())
    return tubes[0].fuse(tubes[1:]).removeSplitter()


def round_cut_ins(d: Blueprint, v: Variant) -> Part.Shape:
    """R7: the right row of cut-ins round the sharp lower rear corner, round inside as a contrast to the planar back.
    Each groove is R's section (round floor of radius depth, back wall, 45 degree roof) swept along a path on the wall
    that turns round the corner on the lower corner's round (low_corner), so that the lips meet the wall all the way
    and the floor turns on low_corner - depth. The ends are planes square to the groove: round ends (the section
    turned half round about the wall's normal) left strips 0.7 wide where they met the groove."""
    c, p = v.cut_ins, v.planar
    a, y0 = d.rear_w / 2, d.body_d
    dp, h = c.depth, c.height
    rp = p.cut_in_r + dp
    if p.low_corner:
        rp = p.low_corner                  # the path on the corner's round: the lips meet the wall all the way round
    cx, cy = a - rp, y0 - rp
    mid = (dp * math.sin(math.pi / 4), dp * (1 - math.cos(math.pi / 4)))
    out = []
    for k in range(c.count):
        z = c.z0 + k * c.pitch
        p0, p1 = V(a - p.cut_rear, y0, z), V(cx, y0, z)
        p2, p3 = V(a, cy, z), V(a, y0 - p.cut_side, z)
        m = math.sqrt(0.5)
        path = Part.Wire([Part.LineSegment(p0, p1).toShape(), Part.Arc(p1, V(cx + rp * m, cy + rp * m, z), p2).toShape(),
                          Part.LineSegment(p2, p3).toShape()])

        def section(origin: FreeCAD.Vector, inward: FreeCAD.Vector) -> Part.Wire:
            at = lambda q: origin + inward * q[0] + V(0, 0, q[1])
            return Part.Wire([Part.Arc(at((0.0, 0.0)), at(mid), at((dp, dp))).toShape(), Part.LineSegment(at((dp, dp)), at((dp, h - dp))).toShape(),
                              Part.LineSegment(at((dp, h - dp)), at((0.0, h))).toShape(), Part.LineSegment(at((0.0, h)), at((-OVER, h))).toShape(),
                              Part.LineSegment(at((-OVER, h)), at((-OVER, 0.0))).toShape(), Part.LineSegment(at((-OVER, 0.0)), at((0.0, 0.0))).toShape()])

        out.append(path.makePipeShell([section(p0, V(0, -1, 0))], True, True))
    return out[0].fuse(out[1:]).removeSplitter()


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
    # the plan's prism reached only z 400: a hand-hold with its top above that (R: 407; R7: 411) is cut off level at
    # z 400 there. Kept for the variants built so; R8 (grip_r) takes the prism to the body top
    top = d.body_top + OVER if (v.planar and v.planar.grip_r) else 400
    plan = Part.makeBox(g.x1 - g.x0 - 2 * r, OVER * 4, top, V(g.x0 + r, y_in - 1, 0)).fuse(
        [Part.makeCylinder(r, top, V(g.x0 + r, y_in + r, 0)), Part.makeCylinder(r, top, V(g.x1 - r, y_in + r, 0)),
         Part.makeBox(g.x1 - g.x0, OVER * 4, top, V(g.x0, y_in + r, 0))])
    cutter = slab.common(plan).removeSplitter()
    if v.planar and v.planar.grip_r:
        # R8: the inside rounded: every edge of the cutter that lies inside the wall (behind y = depth - 0.5); the edges
        # where the cutter passes through the rear wall are not touched, so the rim stays sharp
        es = [e for e in cutter.Edges if not e.Degenerated and e.BoundBox.YMax < d.depth - 0.5 and len(cutter.ancestorsOfType(e, Part.Face)) == 2
              and crease_angle(cutter.ancestorsOfType(e, Part.Face), e.valueAt((e.FirstParameter + e.LastParameter) / 2)) > 5.0]
        cutter = cutter.makeFillet(v.planar.grip_r, es)
    return cutter


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
    if v.planar:
        return planar_hood(d, v, log)
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
    if v.shoulder or v.band:
        turn = turn_point(d, v if v.shoulder else VARIANTS["R2"])   # R3 keeps R2's cameras, for the comparison
        out["closeup-r2-corner"] = cam((d.width / 2 - 20, d.body_d + 5, 375.0), 95, 128, 14)
        out["closeup-turn"] = cam((d.width / 2 - 4, turn[0] + 6, turn[1] + 14), 48, 105, 8)
        out["three-quarter-rear-above"] = cam((110.0, 450.0, 450.0), 330, 140, 34)
        out["flare-foot"] = cam((d.width / 2 - 30, 420.0, 140.0), 210, 140, 14)
    if v.planar:
        out["closeup-hood-corner-above"] = cam((d.width / 2 - 18, d.depth - 18, d.body_top + 8), 75, 135, 38)
    if v.planar and v.planar.exact_corner:
        a, W, zc = d.rear_w / 2, d.width / 2, v.crease_lo[1]
        out["closeup-hip-foot"] = cam((a - 1, d.body_d - 1, zc + 1), 18, 135, 8)
        out["closeup-head-foot"] = cam((W - 2, d.depth - 2, v.crease_hi[1] + 1), 18, 125, 15)
        out["closeup-top-mitre"] = cam((W - 2, band_path(d, v)[-1].p[0] + 2, band_path(d, v)[-1].p[1] - 2), 20, 100, 10)
        out["closeup-cut-in-corner"] = cam((a - 2, d.body_d - 2, v.cut_ins.z0 + 5), 22, 135, 6)
        out["closeup-hand-hold"] = cam((120.0, d.depth, (v.grips.z0 + v.grips.z0 + v.grips.height) / 2), 65, 165, 12)
        out["closeup-hood-roof-end"] = cam((182.0, 522.0, 572.0), 40, 135, 45)
    if v.cut_ins:
        c = v.cut_ins
        out["closeup-cut-ins"] = cam((rear_side_x(d, 0) - v.corner_r / 2, d.body_d - v.corner_r / 2, c.z0 + c.pitch * (c.count - 1) / 2), 60, 145, 10)
    return out


REV6_CHECK = "cad/out/shell-bp-rev6/face-check.json"


def mark_inherited(found: list, path: str = REV6_CHECK, tol: float = 1.0, hood_allowed: bool = True) -> None:
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
        elif f.part == "hood" and hood_allowed:
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
    mark_inherited(found, hood_allowed=not (v.planar and v.planar.hood_whole))
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
