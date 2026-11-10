"""The target form of the cabinet (the blueprint) as 2D profiles and labelled faces, from dims.Blueprint.

This module has no FreeCAD in it. cad/tools/draw_blueprint.py draws the sheets of docs/blueprint from it, and
the solids are to be built from the same profiles, so that the drawing and the model cannot drift apart.

Frame: x to the player's right, y from the deck front toward the rear, z up from the desk. A profile is a list
of Line, Arc and Conic segments in a named plane; sample() turns it into points. faces() returns every face of
the outer form with a stable ID (two letters for the component, a number), its plain name, which way it faces,
what it joins, the dimension that sets it, and its surface as flat polygons for drawing.

The forms, in the order they are built here:
  edge section   a soft radius, then a band that leans, then a crease: the section the deck has round its top.
                 The same section runs up the rail, so the edge follows through from the hood seam, down the
                 screen face, round the sweep, along the deck's side and round its front.
  front profile  deck top, sweep (bend_r in dims), screen face (apron, bezel, brow band), body top.
  rear           side band flush with the deck's side, a leaning step to the narrower rear body, a lower rear
                 wall, and an upper rear that stands proud of it.
  hood           a cap on the body top: near-straight sides that turn into the top through a tight corner, an
                 upright front with a soft edge, a long arc from the roof down the rear; in its opening the marquee,
                 a lip, the hood band with the speaker forms and the logo plate, and the ledge on the sill.
"""
from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field

from .dims import MON_ACTIVE_H, MON_ACTIVE_W, Blueprint

P2 = tuple[float, float]
P3 = tuple[float, float, float]


@dataclass(frozen=True)
class Line:
    p: P2
    q: P2


@dataclass(frozen=True)
class Arc:
    """An arc round c from angle a0 to a1 (radians from the first axis toward the second)."""
    c: P2
    r: float
    a0: float
    a1: float

    def at(self, a: float) -> P2:
        return self.c[0] + self.r * math.cos(a), self.c[1] + self.r * math.sin(a)


@dataclass(frozen=True)
class Conic:
    """A conic from p to q, tangent at both ends to the lines that meet at corner; w 0.707 is an ellipse quarter."""
    p: P2
    corner: P2
    q: P2
    w: float = math.sqrt(0.5)

    def at(self, t: float) -> P2:
        b0, b1, b2 = (1 - t) ** 2, 2 * t * (1 - t) * self.w, t ** 2
        k = b0 + b1 + b2
        return ((b0 * self.p[0] + b1 * self.corner[0] + b2 * self.q[0]) / k, (b0 * self.p[1] + b1 * self.corner[1] + b2 * self.q[1]) / k)


Path = list[Line | Arc | Conic]


def sample(path: Path, step: float = 4.0) -> list[P2]:
    """Points along a path, about step apart, without repeating the joints."""
    out: list[P2] = []
    for seg in path:
        if isinstance(seg, Line):
            pts = [seg.p, seg.q]
        elif isinstance(seg, Arc):
            n = max(2, math.ceil(abs(seg.a1 - seg.a0) * seg.r / step))
            pts = [seg.at(seg.a0 + (seg.a1 - seg.a0) * i / n) for i in range(n + 1)]
        else:
            n = max(6, math.ceil((math.dist(seg.p, seg.corner) + math.dist(seg.corner, seg.q)) / step))
            pts = [seg.at(i / n) for i in range(n + 1)]
        out += pts if not out or math.dist(out[-1], pts[0]) > 1e-9 else pts[1:]
    return out


def offset(points: list[P2], by: float) -> list[P2]:
    """A polyline moved by a distance to the left of its direction of travel."""
    out = []
    for i, p in enumerate(points):
        a, b = points[max(i - 1, 0)], points[min(i + 1, len(points) - 1)]
        length = math.dist(a, b)
        out.append((p[0] - by * (b[1] - a[1]) / length, p[1] + by * (b[0] - a[0]) / length))
    return out


# ---------- the edge section, the front profile, the deck plan ----------

def edge_section(d: Blueprint) -> Path:
    """The edge in (inward from the side plane, down from the top surface): radius, leaning band, crease at the side."""
    t = math.radians(90.0 - d.deck_lean)
    r, i = d.deck_top_r, d.edge_in
    arc = Arc((i, r), r, -math.pi / 2, -math.pi / 2 - t)
    return [arc, Line(arc.at(arc.a1), (0.0, d.deck_lean_h))]


@dataclass(frozen=True)
class Front:
    """The front of the body in side view, in (y, z): the sweep up from the deck top, then the rail arc to the body top.

    The rail arc is convex toward the player. Its chord runs from the end of the sweep to the front edge of the
    body top; the recline of the cabinet is the angle of this chord, which is also the tangent of the arc at
    mid chord and the recline of the flat screen behind it.
    """
    sweep: Arc
    rail: Arc
    chord: float
    recline: float
    sagitta: float
    foot_lean: float
    top_lean: float

    def on_rail(self, d: Blueprint, s: float, below: float = 0.0) -> P2:
        """The point of the rail arc in front of the point at s on the flat screen face, moved into the body by below."""
        fy, fz = d.face(s)
        mid = self.rail.at((self.rail.a0 + self.rail.a1) / 2)
        rho = math.radians(self.recline)
        t = (fy - mid[0]) * math.sin(rho) + (fz - mid[1]) * math.cos(rho)
        a = (self.rail.a0 + self.rail.a1) / 2 - math.asin(max(-1.0, min(1.0, t / self.rail.r)))
        a = min(max(a, self.rail.a1), self.rail.a0)
        r = self.rail.r - below
        return self.rail.c[0] + r * math.cos(a), self.rail.c[1] + r * math.sin(a)

    def rise(self, d: Blueprint, s: float) -> float:
        """How far the rail arc stands in front of the flat screen face at s, square to that face."""
        y, z = self.on_rail(d, s)
        fy, fz = d.face(s)
        su, cu = d.u
        return -(y - fy) * cu + (z - fz) * su

    def chain(self, n_rail: int = 48, n_sweep: int = 14) -> list[tuple[float, float, P2]]:
        """Points from the body top down the rail and round the sweep to the deck, each with the direction into the body."""
        out = []
        for i in range(n_rail + 1):
            a = self.rail.a1 + (self.rail.a0 - self.rail.a1) * i / n_rail
            out.append((*self.rail.at(a), (-math.cos(a), -math.sin(a))))
        for i in range(1, n_sweep + 1):
            a = self.sweep.a1 + (self.sweep.a0 - self.sweep.a1) * i / n_sweep
            out.append((*self.sweep.at(a), (math.cos(a), math.sin(a))))
        return out


def front(d: Blueprint) -> Front:
    """Solve the sweep and the rail arc: the sweep keeps its start and radius, and ends where the rail arc is tangent to it."""
    centre = (d.foot_y - d.bend_t, d.deck_top + d.bend_r)
    top = d.face(d.top_s)
    turn = math.radians(d.rail_turn)
    lean = math.radians(d.recline) - turn / 2
    for _ in range(30):
        foot = (centre[0] + d.bend_r * math.cos(lean), centre[1] - d.bend_r * math.sin(lean))
        rho = math.atan2(top[0] - foot[0], top[1] - foot[1])
        lean = rho - turn / 2
    chord = math.dist(foot, top)
    sweep = Arc(centre, d.bend_r, -math.pi / 2, -lean)
    if turn < 1e-9:
        r = 1e7
        turn = 2 * math.asin(chord / (2 * r))
    else:
        r = chord / (2 * math.sin(turn / 2))
    sagitta = r * (1 - math.cos(turn / 2))
    mid = ((foot[0] + top[0]) / 2, (foot[1] + top[1]) / 2)
    c = (mid[0] + (r - sagitta) * math.cos(rho), mid[1] - (r - sagitta) * math.sin(rho))
    rail = Arc(c, r, math.pi - rho + turn / 2, math.pi - rho - turn / 2)
    return Front(sweep, rail, chord, math.degrees(rho), sagitta, math.degrees(lean), math.degrees(rho + turn / 2))


def body_half(d: Blueprint, z: float) -> float:
    """Half the width of the body side at height z, with the bevel of the seam groove at its top."""
    return d.side_x(z) - max(0.0, z - (d.body_top - d.seam_groove))


def rear_profile(d: Blueprint) -> list[P2]:
    """Centre-line profile of the body behind the screen face in (y, z): body top, upper rear, slope, lower rear, floor."""
    return [d.face(d.top_s), (d.depth, d.body_top), (d.depth, d.rear_step_z1), (d.body_d, d.rear_step_z0), (d.body_d, 0.0), (0.0, 0.0)]


def deck_front_section(d: Blueprint) -> list[P2]:
    """The deck's front edge at the centre line in (y, z), from the top flat down to the desk."""
    r = d.bottom_r
    edge = [(i, d.deck_top - down) for i, down in sample(edge_section(d), 1.0)]
    foot = sample([Arc((r, r), r, math.pi, 1.5 * math.pi)], 1.0)
    return [(d.edge_in + 12.0, d.deck_top)] + edge + foot + [(r + 12.0, 0.0)]


def deck_plan(d: Blueprint) -> Path:
    """The right half of the deck's outline at its sides and front, in (x, y), from the rear of the side to the centre."""
    hw = d.width / 2
    xc = d.deck_centre_frac * hw
    a = math.radians(d.deck_flank)
    yk = (hw - xc) * math.tan(a)
    big, small = d.deck_corner_frac * d.width, d.deck_crease_r
    tb, ts = big * math.tan((math.pi / 2 - a) / 2), small * math.tan(a / 2)
    corner = Arc((hw - big, yk + tb), big, 0.0, -(math.pi / 2 - a))
    crease = Arc((xc - ts, small), small, -(math.pi / 2 - a), -math.pi / 2)
    return [Line((hw, d.foot_y - d.bend_t), (hw, yk + tb)), corner, Line(corner.at(corner.a1), crease.at(crease.a0)), crease,
            Line((xc - ts, 0.0), (0.0, 0.0))]


# ---------- the hood, in its own frame: x across, y back from its front plane, z up from its base ----------

@dataclass(frozen=True)
class Hood:
    origin: P3
    height: float
    depth: float
    half_base: float
    half_top: float
    z_corner: float
    side_arc: Line | Arc
    corner: Arc
    z_sill: float
    z_band_top: float
    z_rail_top: float
    z_open_top: float
    y_band_foot: float
    y_band_top: float
    y_marquee_bottom: float
    y_marquee_top: float
    outline: list[P2]
    opening: list[P2]
    edge_line: list[P2]
    side: list[P2]

    def half_width(self, z: float, points: list[P2] | None = None) -> float:
        """Half the width of the outline (or of another curve of the same kind) at height z."""
        pts = points or self.outline
        for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
            if z0 <= z <= z1 and z1 > z0:
                return x0 + (x1 - x0) * (z - z0) / (z1 - z0)
        return pts[-1][0] if z >= pts[-1][1] else pts[0][0]

    def y_rear(self, z: float) -> float:
        """Where the rear of the cap is at height z, from the side profile."""
        top = max(y for y, zz in self.side if zz >= self.height - 1e-6)
        rear = [p for p in self.side if p[0] >= top - 1e-6]
        for (y0, z0), (y1, z1) in zip(rear, rear[1:]):
            lo, hi = min(z0, z1), max(z0, z1)
            if lo <= z <= hi and hi > lo:
                return y0 + (y1 - y0) * (z - z0) / (z1 - z0)
        return top if z >= self.height else self.depth

    def half_open(self, z: float, d: Blueprint) -> float:
        """Half the clear width of the opening at height z, with the round of its bottom corners."""
        r = d.hood_sill_corner_r
        zc = self.z_sill + r
        if z >= zc:
            return self.half_width(z, self.opening)
        return self.half_width(zc, self.opening) - r + math.sqrt(max(r * r - (zc - z) ** 2, 0.0))

    def y_recess(self, z: float, d: Blueprint) -> float:
        """Depth of the recess behind the front plane at height z: band, rail or marquee."""
        if z <= self.z_band_top:
            return self.y_band_foot + (z - self.z_sill) * math.tan(math.radians(d.hood_band_tilt))
        if z < self.z_rail_top:
            return self.y_band_top
        return self.y_marquee_bottom - (z - self.z_rail_top) * math.tan(math.radians(d.marquee_tilt))


def hood_outline(d: Blueprint, height: float, half_base: float) -> Path:
    """Right half of the cap seen from the front, in (x, z): a side that leaves the seam on the tangent of the body's
    tuck and turns only hood_side_turn on its way up, a top corner of one radius, half the top flat. The bevel of the
    seam groove at the foot is not in this outline."""
    a0, a1 = math.radians(d.tuck_lean), math.radians(d.tuck_lean + d.hood_side_turn)
    rc = d.hood_corner_ratio * d.width
    zc = height - rc * (1 - math.sin(a1))
    if a1 - a0 > 1e-9:
        rs = zc / (math.sin(a1) - math.sin(a0))
        side: Line | Arc = Arc((half_base - rs * math.cos(a0), -rs * math.sin(a0)), rs, a0, a1)
        pc = side.at(a1)
    else:
        pc = (half_base - zc * math.tan(a0), zc)
        side = Line((half_base, 0.0), pc)
    corner = Arc((pc[0] - rc * math.cos(a1), height - rc), rc, a1, math.pi / 2)
    top = corner.at(math.pi / 2)
    return [side, corner, Line(top, (0.0, height))]


def hood_side_profile(d: Blueprint, height: float, depth: float) -> Path:
    """The cap seen from the side, in (y, z): upright front, soft edge, short roof, a long arc down to the rear wall."""
    return [Line((0.0, 0.0), (0.0, height - d.hood_edge_in)),
            Conic((0.0, height - d.hood_edge_in), (0.0, height), (d.hood_edge_back, height)),
            Line((d.hood_edge_back, height), (depth - d.hood_rear_arc_d, height)),
            Conic((depth - d.hood_rear_arc_d, height), (depth, height), (depth, height - d.hood_rear_arc_h)),
            Line((depth, height - d.hood_rear_arc_h), (depth, 0.0))]


def hood(d: Blueprint) -> Hood:
    height = d.hood_h - d.seam_gap
    origin = (0.0, d.seam_y + d.hood_shoulder_front, d.body_top + d.seam_gap)
    depth = d.depth - d.hood_shoulder_front - origin[1]
    half_base = d.side_x(d.body_top) - d.hood_shoulder
    path = hood_outline(d, height, half_base)
    outline = sample(path, 3.0)
    z_open_top = height - d.hood_bar
    tm, tb = math.radians(d.marquee_tilt), math.radians(d.hood_band_tilt)
    z_rail_top = z_open_top - (d.marquee_margin + d.marquee_h + d.marquee_head) * math.cos(tm)
    z_band_top = z_rail_top - d.hood_rail_h
    y_band_top = d.hood_ledge + (z_band_top - d.hood_sill_h) * math.tan(tb)
    y_mb = y_band_top + d.hood_band_t / math.cos(tb) - d.marquee_cover_t / math.cos(tm)
    return Hood(origin, height, depth, half_base, path[-1].p[0], path[1].at(path[1].a0)[1], path[0], path[1], d.hood_sill_h,
                z_band_top, z_rail_top, z_open_top, d.hood_ledge, y_band_top, y_mb, y_mb - (z_open_top - z_rail_top) * math.tan(tm),
                outline, offset(outline, d.hood_bar), offset(outline, d.hood_edge_in), sample(hood_side_profile(d, height, depth), 3.0))


def marquee_window(d: Blueprint, h: Hood) -> tuple[float, float]:
    """Width and height of the straight marquee window: the widest that clears the corner of the opening."""
    z_top = h.z_rail_top + (d.marquee_margin + d.marquee_h) * math.cos(math.radians(d.marquee_tilt))
    return 2 * math.floor(h.half_width(z_top, offset(h.outline, d.hood_bar + d.hood_trim_gap + 0.5))), d.marquee_h


# ---------- faces ----------

@dataclass
class Face:
    id: str
    name: str
    component: str
    facing: str
    joins: str
    sets: str
    curve: str
    build: str
    polys: list[list[P3]] = field(default_factory=list)
    edges: list[list[P3]] = field(default_factory=list)


def strip(a: list[P3], b: list[P3]) -> list[list[P3]]:
    return [[a[i], a[i + 1], b[i + 1], b[i]] for i in range(len(a) - 1)]


def mirror(polys: list[list[P3]]) -> list[list[P3]]:
    return [[(-x, y, z) for x, y, z in reversed(p)] for p in polys]


FLAT, SINGLE, DOUBLE = "flat", "single-curved", "double-curved"
FACES: dict[str, tuple[str, str, str, str, str, str, str]] = {
    # id: (name, component, facing, joins, the dimension that sets it, curvature, how to build it and what it means for the print)
    "DK1": ("deck top border", "deck", "faces up", "CP1, DK2, FB1, RL1", "deck_top 72; flat border 12 or more in front of the panel", FLAT, "extrusion"),
    "DK2": ("deck edge radius", "deck", "turns from up to 10 deg off vertical", "DK1, DK3", "deck_top_r 10.5, turning 80 deg",
            "single-curved; double-curved round the corners", "sweep of the edge section along the deck outline"),
    "DK3": ("deck edge band", "deck", "leans 10 deg from vertical, faces out", "DK2, DK4 to DK7 at the crease", "deck_lean 10, crease deck_lean_h 24 below the top",
            "flat; single-curved round the corners", "the same sweep"),
    "DK4": ("deck front, centre face", "deck", "faces the player, vertical", "DK3, DK5", "deck_centre_frac 0.56 of the width", FLAT, "extrusion of the deck outline"),
    "DK5": ("deck front, flank", "deck", "vertical, turned back 8 deg", "DK4, DK6", "deck_flank 8", FLAT, "extrusion of the deck outline"),
    "DK6": ("deck front corner", "deck", "vertical, round in plan", "DK5, DK7", "deck_corner_frac 0.09 of the width (R 44.5)", SINGLE, "extrusion of the deck outline"),
    "DK7": ("deck side", "deck", "faces sideways, vertical", "DK6, RL4 (same plane)", "at the full width; flush with RL4", FLAT, "extrusion of the deck outline"),
    "CP1": ("control panel", "control panel", "faces up", "DK1", "396 x 175, 2 below the deck top", FLAT, "cut plate"),
    "FB1": ("sweep", "front body", "concave, from up to the foot of the rail arc", "DK1, FB2, RL1", "bend_r 50, turning 68 deg", SINGLE,
            "extrusion of the side profile across the width"),
    "FB2": ("apron", "front body", "faces the player; follows the rail arc", "FB1, BZ1, RL1", "band_len 60", SINGLE, "extrusion of the side profile across the width"),
    "FB3": ("brow band", "front body", "faces the player; follows the rail arc", "BZ1, FB4, RL1", "brow_ledge 12", SINGLE, "extrusion of the side profile across the width"),
    "FB4": ("body top", "front body", "faces up", "FB3, RL1 to RL4, RB5, hood foot", "body_top 423.9; under the hood, bare for 4 at the front and rear", FLAT, "plane cut"),
    "RL1": ("rail land", "rail", "faces the player; one convex arc in side view, chord reclined 30 deg", "BZ1, FB1 to FB3, RL2, DK1",
            "rail_sagitta_ratio 0.035 of the chord (13.0); 16.0 wide, 6.4 at the top of the bezel", SINGLE,
            "extrusion of the side profile; on a print that stands upright the arc is in the layer plane and prints smooth"),
    "RL2": ("rail edge radius", "rail", "turns from the land to 10 deg off the side", "RL1, RL3, DK2", "same section as DK2", DOUBLE,
            "sweep of the edge section along the rail arc; above the start of the tuck the path leaves the side plane, so loft between sections there"),
    "RL3": ("rail edge band", "rail", "leans 10 deg from the side", "RL2, RL4 at the crease, DK3", "same section as DK3: 13.0 in, crease 24 behind the land", DOUBLE,
            "the same sweep and loft"),
    "RL4": ("side band", "rail", "faces sideways; vertical up to 0.667 of the body height, then leans in on one arc", "RL3, DK7 (same plane), RB2, hood side HC5",
            "body_tuck_ratio 0.023 (11.4 in at the seam, 11.1 deg there), from body_tuck_from 0.667; carries the stripe", "flat; single-curved above the start of the tuck",
            "extrusion of the front outline of the side along the depth; a stripe decal lies flat on it"),
    "BZ1": ("bezel land", "bezel", "faces the player; follows the rail arc, 2 below the rail land", "RL1, FB2, FB3, BZ2", "434.7 x 305.4 outside, bezel_land 20 wide", SINGLE,
            "extrusion; print the plate on its long edge, or the back down with layer steps on the land"),
    "BZ2": ("bezel inner frame", "bezel", "slopes in toward the screen, 16 to 33 deg from the land", "BZ1, BZ3", "from the land down to a flat rim 2 above the screen",
            "flat at the top and bottom; ruled and twisted at the sides", "loft between the inner edge of the land (an arc) and the rim (a line)"),
    "BZ3": ("bezel rim wall", "bezel", "faces the centre of the screen", "BZ2, SC1", "bezel_rim 2 deep", FLAT, "extrusion"),
    "SC1": ("screen", "bezel", "faces the player, flat, reclined 30 deg", "BZ3", "344.7 x 215.4; mon_setback 7.2 behind the chord of the rail, 14.0 to 20.2 behind the rail land", FLAT, "the monitor"),
    "RB1": ("rear body side", "rear body", "faces sideways; vertical, then leans in with the side band", "RB2, RB3 to RB5", "12 in from the side band", "flat; single-curved above the start of the tuck",
            "extrusion of the front outline of the side"),
    "RB2": ("step", "rear body", "faces out and back, 45 deg in plan, leans 28 deg", "RL4, RB1", "foot 138 behind the deck (0.28 W); 12 deep", "flat; twisted above the start of the tuck",
            "loft between the two edges of the step"),
    "RB3": ("lower rear wall", "rear body", "faces the rear, vertical", "RB1, RB2, RB4, RB6", "body_d 540", FLAT, "extrusion"),
    "RB4": ("rear slope", "rear body", "faces the rear and down, 45 deg", "RB3, RB5", "z 310 to 350", FLAT, "extrusion"),
    "RB5": ("upper rear wall", "rear body", "faces the rear, vertical", "RB4, FB4", "rear_proud 40 behind the lower wall", FLAT, "extrusion"),
    "RB6": ("rear door", "rear body", "faces the rear, vertical", "RB3", "368 x 188", FLAT, "plate"),
    "FL1": ("underside", "floor", "faces down", "DK4 to DK7, RL4, RB1 to RB3", "on the desk (feet not designed)", FLAT, "extrusion"),
    "HC1": ("hood leg, front face", "hood cap", "faces the player, upright", "HC4, HC11, HC3", "hood_bar 21 less the soft edge; its outline follows the side", FLAT, "extrusion of the front outline"),
    "HC2": ("hood top bar, front face", "hood cap", "faces the player, upright", "HC4, HC10", "hood_bar 21 less the soft edge", FLAT, "extrusion of the front outline"),
    "HC3": ("hood sill, front face", "hood cap", "faces the player, upright", "HC1, HC12", "hood_sill_h 17", FLAT, "extrusion of the front outline"),
    "HC4": ("hood soft edge", "hood cap", "turns from the front to the side and the roof", "HC1, HC2, HC5 to HC7", "quarter ellipse 16 in, 32 back",
            "single-curved along the top flat; double-curved along the side and the corner", "sweep of the quarter ellipse along the front outline: an extrusion along the top flat, revolutions round the arcs of the side and the corner"),
    "HC5": ("hood side", "hood cap", "faces sideways; leans in 11.1 deg at the seam and 13.1 deg at the top corner", "HC4, HC6, HC9, RL4",
            "tangent to the tuck at the seam; hood_side_turn 2 deg on one arc of 7.7 W; no shoulder: a groove of 3 at the seam", SINGLE,
            "extrusion of the front outline along the depth; print the cap on its rear face so that this outline is in the layer plane"),
    "HC6": ("hood side blend", "hood cap", "turns from the side to the roof", "HC5, HC7", "hood_corner_ratio 0.07: one radius of 34.6, from 130 above the seam to the top flat", SINGLE,
            "the same extrusion"),
    "HC7": ("hood roof", "hood cap", "faces up", "HC4, HC6, HC8", "top flat 0.705 W wide (348.8): follows from the side and the corner; hood_crown_ratio 0: no crown", FLAT, "the same extrusion"),
    "HC8": ("hood rear arc", "hood cap", "turns from the roof to the rear", "HC7, HC9", "conic 95 deep, 110 high", SINGLE,
            "extrusion of the side profile across the width, cut by the extrusion of the front outline (the common of two extrusions)"),
    "HC9": ("hood rear wall", "hood cap", "faces the rear, upright", "HC8, HC5, FB4", "4 in from the upper rear wall", FLAT, "extrusion"),
    "HC10": ("hood soffit", "hood cap", "faces down", "HC2, MQ1", "under the top bar, back to the marquee", FLAT, "extrusion"),
    "HC11": ("hood leg, inner wall", "hood cap", "faces the centre line", "HC1, HB1, MQ1", "from the front plane back to the band", SINGLE, "extrusion of the opening outline"),
    "HC12": ("hood ledge", "hood cap", "faces up", "HC3, HB1", "hood_ledge 14", FLAT, "extrusion"),
    "HC13": ("marquee lip", "hood cap", "faces the player", "MQ1, HB1", "6 high, 5 proud", SINGLE, "extrusion across the width"),
    "MQ1": ("marquee cover", "marquee", "faces down 18 deg toward the player", "HC10, HC11, HC13, MQ2", "ends follow the corner of the opening", FLAT, "plate"),
    "MQ2": ("marquee window", "marquee", "faces down 18 deg toward the player", "MQ1", "straight, 358 x 34, eleven modules of 32", FLAT, "plate"),
    "HB1": ("hood band", "hood band", "leans back 24 deg", "HC12, HC11, HC13, SP1, LG1", "foot on the ledge", FLAT, "plate"),
    "SP1": ("speaker form", "hood band", "parallel to the band", "HB1, SP2", "13 proud; outer end parallel to the leg", FLAT, "extrusion square to the band"),
    "SP2": ("speaker grille", "hood band", "parallel to the band", "SP1", "set 1.5 into the form", FLAT, "plate"),
    "SP3": ("speaker form walls", "hood band", "square to the band", "SP1, HB1", "13 high, top edge R 4", FLAT, "extrusion with a fillet"),
    "LG1": ("logo form", "hood band", "parallel to the band", "HB1, LG2", "5 proud", FLAT, "extrusion square to the band"),
    "LG2": ("logo plate", "hood band", "parallel to the band", "LG1", "166 wide", FLAT, "plate"),
    "LG3": ("logo form walls", "hood band", "square to the band", "LG1, HB1", "5 high", FLAT, "extrusion"),
}


def faces(d: Blueprint) -> dict[str, Face]:
    """Every face of the target with its surface as polygons (both sides of the cabinet)."""
    out = {k: Face(k, *v) for k, v in FACES.items()}
    hw, top = d.width / 2, d.deck_top
    su, cu = d.u
    inset = d.edge_in
    xb = d.bezel_w / 2 + d.panel_gap
    sec = sample(edge_section(d), 2.5)
    n_radius = len(sample(edge_section(d)[:1], 2.5))

    def add(key: str, polys: list[list[P3]], both: bool = True, edges: list[list[P3]] | None = None) -> None:
        out[key].polys += polys + (mirror(polys) if both else [])
        for e in edges or []:
            out[key].edges += [e] + ([[(-x, y, z) for x, y, z in e]] if both else [])

    # chain A: from the body top down the rail arc and round the sweep; frame: in = toward the centre line, down = into the body
    fr = front(d)
    chain_a = fr.chain()
    n_rail = 49
    lean_top = math.radians(fr.top_lean)
    seam_x = d.side_x(d.body_top)
    rows_a = [[(seam_x - i, d.seam_y + dn / math.cos(lean_top), d.body_top) for i, dn in sec]]
    rows_a += [[(d.side_x(z) - i, y + ny * dn, z + nz * dn) for i, dn in sec] for y, z, (ny, nz) in chain_a]
    land_out = [(d.side_x(z) - inset, y, z) for y, z, _ in chain_a]
    land_in = [(xb, y, z) for y, z, _ in chain_a]
    add("RL1", strip(land_out, land_in), edges=[land_out, land_in])
    for j in range(len(sec) - 1):
        add("RL2" if j < n_radius - 1 else "RL3", strip([r[j] for r in rows_a], [r[j + 1] for r in rows_a]))
    crease_a = [r[-1] for r in rows_a]
    add("RL3", [], edges=[crease_a, [r[n_radius - 1] for r in rows_a]])
    centre = [(y, z) for y, z, _ in chain_a]

    def along(s0: float, s1: float, below: float = 0.0, n: int = 8) -> list[P2]:
        """Points of the rail arc between two stations of the screen face, moved into the body by below."""
        return [fr.on_rail(d, s0 + (s1 - s0) * k / n, below) for k in range(n + 1)]

    def across(pts: list[P2], x0: float, x1: float) -> list[list[P3]]:
        return strip([(x0, y, z) for y, z in pts], [(x1, y, z) for y, z in pts])

    add("FB3", across(along(d.top_s, d.bezel_s1, n=3), -xb, xb), both=False)
    add("FB2", across(along(d.bezel_s0, d.bezel_s0 - d.band_len, n=6) + centre[n_rail - 1:n_rail], -xb, xb), both=False)
    add("FB1", across(centre[n_rail - 1:], -xb, xb), both=False,
        edges=[[(-xb, *centre[-1]), (xb, *centre[-1])], [(-xb, *centre[n_rail - 1]), (xb, *centre[n_rail - 1])]])

    # bezel: a land that follows the rail arc, an inner frame that slopes down to a flat rim, and the flat screen
    def on_face(x: float, s: float, behind: float) -> P3:
        y, z = d.face(s)
        return x, y + behind * cu, z - behind * su

    cs, bw, bl = d.image_s, d.bezel_w / 2, d.bezel_land
    win = (-MON_ACTIVE_W / 2, cs - MON_ACTIVE_H / 2, MON_ACTIVE_W / 2, cs + MON_ACTIVE_H / 2)
    rim_depth = d.mon_setback - d.bezel_rim
    s_in0, s_in1 = d.bezel_s0 + bl, d.bezel_s1 - bl
    face = lambda s0, s1: along(s0, s1, 2.0, 14)
    add("BZ1", across(face(d.bezel_s0, s_in0)[::7], -bw, bw) + across(face(s_in1, d.bezel_s1)[::7], -bw, bw), both=False)
    add("BZ1", across(face(s_in0, s_in1), bw - bl, bw))
    outer = [(bw, y, z) for y, z in face(d.bezel_s0, d.bezel_s1)]
    inner = [(bw - bl, y, z) for y, z in face(s_in0, s_in1)]
    add("BZ1", [], edges=[outer, inner])
    add("BZ1", [], both=False, edges=[[(-bw, *p), (bw, *p)] for p in (outer[0][1:], outer[-1][1:])] + [[(-bw + bl, *p), (bw - bl, *p)] for p in (inner[0][1:], inner[-1][1:])])
    rim_side = [on_face(win[2], win[1] + (win[3] - win[1]) * k / 14, rim_depth) for k in range(15)]
    add("BZ2", strip(inner, rim_side), edges=[rim_side])
    add("BZ2", [[(-bw + bl, *inner[0][1:]), (bw - bl, *inner[0][1:]), rim_side[0], (-rim_side[0][0], *rim_side[0][1:])],
                [(-bw + bl, *inner[-1][1:]), (bw - bl, *inner[-1][1:]), rim_side[-1], (-rim_side[-1][0], *rim_side[-1][1:])]], both=False,
        edges=[[(-p[0], *p[1:]), p] for p in (rim_side[0], rim_side[-1])])
    rect = lambda r, behind: [on_face(r[0], r[1], behind), on_face(r[2], r[1], behind), on_face(r[2], r[3], behind), on_face(r[0], r[3], behind)]
    near, far = rect(win, rim_depth), rect(win, d.mon_setback)
    add("BZ3", [[near[k], near[(k + 1) % 4], far[(k + 1) % 4], far[k]] for k in range(4)], both=False)
    add("SC1", [far], both=False, edges=[far + far[:1]])

    # chain B: round the deck at the height of its top; frame: in = inward in plan, down = -z
    plan = deck_plan(d)
    chain_b: list[tuple[float, float, float, float, str]] = []
    for seg, key in zip(plan, ("DK7", "DK6", "DK5", "DK4", "DK4")):
        pts = sample([seg], 5.0)
        for i, p in enumerate(pts):
            a, c = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
            length = math.dist(a, c)
            chain_b.append((p[0], p[1], (c[1] - a[1]) / length, -(c[0] - a[0]) / length, key))
    rows_b = [[(x + nx * i, y + ny * i, top - dn) for i, dn in sec] for x, y, nx, ny, _ in chain_b]
    for j in range(len(sec) - 1):
        add("DK2" if j < n_radius - 1 else "DK3", strip([r[j] for r in rows_b], [r[j + 1] for r in rows_b]))
    crease_b = [r[-1] for r in rows_b]
    add("DK3", [], edges=[crease_b, [r[n_radius - 1] for r in rows_b]])
    for i in range(len(chain_b) - 1):
        key = chain_b[i][4]
        (x0, y0), (x1, y1) = chain_b[i][:2], chain_b[i + 1][:2]
        if math.dist((x0, y0), (x1, y1)) > 1e-9:
            add(key, [[(x0, y0, top - d.deck_lean_h), (x1, y1, top - d.deck_lean_h), (x1, y1, 0.0), (x0, y0, 0.0)]])
    for key in ("DK4", "DK5", "DK6", "DK7"):
        ends = [i for i, c in enumerate(chain_b) if c[4] == key]
        for i in (ends[0], ends[-1]):
            add(key, [], edges=[[(chain_b[i][0], chain_b[i][1], top - d.deck_lean_h), (chain_b[i][0], chain_b[i][1], 0.0)]])
        add(key, [], edges=[[(chain_b[i][0], chain_b[i][1], 0.0) for i in ends]])
    ya = d.foot_y - d.bend_t
    flat = [r[0] for r in rows_b]
    ring_out = [(x, y) for x, y, _ in flat[::-1]] + [(-x, y) for x, y, _ in flat]
    px, py0, py1 = d.panel_w / 2 + d.panel_gap, d.deck_nose, d.deck_nose + d.panel_d + 2 * d.panel_gap
    cy = (py0 + py1) / 2

    def on_pocket(p: P2) -> P2:
        dx, dy = p[0], p[1] - cy
        k = min(px / abs(dx) if abs(dx) > 1e-9 else math.inf, ((py1 - py0) / 2) / abs(dy) if abs(dy) > 1e-9 else math.inf)
        return dx * k, cy + dy * k

    closed = ring_out + ring_out[:1]
    add("DK1", [[(*closed[i], top), (*closed[i + 1], top), (*on_pocket(closed[i + 1]), top), (*on_pocket(closed[i]), top)]
                for i in range(len(closed) - 1)], both=False,
        edges=[[(x, y, top) for x, y in closed], [(px, py0, top), (px, py1, top), (-px, py1, top), (-px, py0, top), (px, py0, top)]])
    pw = d.panel_w / 2
    panel = [(pw, py0 + d.panel_gap, d.panel_top), (pw, py1 - d.panel_gap, d.panel_top), (-pw, py1 - d.panel_gap, d.panel_top), (-pw, py0 + d.panel_gap, d.panel_top)]
    add("CP1", [panel], both=False, edges=[panel + panel[:1]])

    # body top, side band, step, rear body: every side face follows the tuck of the body toward the hood
    ys = d.seam_y
    t = math.tan(math.radians(d.step_lean))
    in_step = hw - d.rear_w / 2
    crease = sorted({(round(z, 6), y) for _, y, z in crease_a})

    def y_front(z: float) -> float:
        """Front boundary of the side band at height z: the crease of the rail edge, or the seam to the deck below it."""
        if z <= crease[0][0]:
            return ya
        for (z0, y0), (z1, y1) in zip(crease, crease[1:]):
            if z0 <= z <= z1:
                return y0 + (y1 - y0) * (z - z0) / (z1 - z0) if z1 > z0 else y0
        return crease[-1][1]

    def y_rear(z: float) -> float:
        if z <= d.rear_step_z0:
            return d.body_d
        return min(d.depth, d.body_d + (z - d.rear_step_z0) * (d.depth - d.body_d) / (d.rear_step_z1 - d.rear_step_z0))

    tuck_levels = [d.tuck_z0 + (d.body_top - d.tuck_z0) * k / 16 for k in range(17)]
    levels = sorted({0.0, d.rear_step_z0, d.rear_step_z1, d.body_top - d.seam_groove, *tuck_levels, *[d.tuck_z0 * k / 20 for k in range(21)], *[z for z, _ in crease]})
    band_front = [(body_half(d, z), y_front(z), z) for z in levels]
    step_out = [(body_half(d, z), min(d.step_y0 + z * t, y_rear(z)), z) for z in levels]
    step_in = [(body_half(d, z) - in_step, min(d.step_y0 + in_step + z * t, y_rear(z)), z) for z in levels]
    rear_in = [(body_half(d, z) - in_step, y_rear(z), z) for z in levels]
    add("RL4", strip(band_front, step_out), edges=[band_front, step_out, [band_front[0], step_out[0]]])
    add("RB2", strip(step_out, step_in), edges=[step_out, step_in])
    add("RB1", strip(step_in, rear_in), edges=[rear_in, [step_in[0], rear_in[0]]])
    top_half = body_half(d, d.body_top)
    y_top = min(d.step_y0 + d.body_top * t, d.depth)
    top_edge = [(seam_x - i, ys + dn / math.cos(lean_top), d.body_top) for i, dn in sec]
    right = [(0.0, ys, d.body_top), (seam_x - inset, ys, d.body_top)] + top_edge + [(top_half, y_top, d.body_top), (top_half - in_step, min(y_top + in_step, d.depth), d.body_top),
                                                                                    (top_half - in_step, d.depth, d.body_top), (0.0, d.depth, d.body_top)]
    add("FB4", [right], edges=[right[1:-1]])
    rw = hw - in_step
    under = [(x, y, 0.0) for x, y, *_ in chain_b] + [(0.0, d.body_d, 0.0), (rw, d.body_d, 0.0), (rw, d.step_y0 + in_step, 0.0), (hw, d.step_y0, 0.0)]
    add("FL1", [under])
    for key, z0, z1 in (("RB3", 0.0, d.rear_step_z0), ("RB4", d.rear_step_z0, d.rear_step_z1), ("RB5", d.rear_step_z1, d.body_top)):
        rows = [p for p in rear_in if z0 - 1e-9 <= p[2] <= z1 + 1e-9]
        add(key, strip([(-x, y, z) for x, y, z in rows], rows), both=False, edges=[rows, [(-x, y, z) for x, y, z in rows], [(-rows[0][0], *rows[0][1:]), rows[0]],
                                                                                [(-rows[-1][0], *rows[-1][1:]), rows[-1]]])
    dw = d.door_w / 2
    door = [(-dw, d.body_d + 0.5, d.door_z0), (dw, d.body_d + 0.5, d.door_z0), (dw, d.body_d + 0.5, d.door_z1), (-dw, d.body_d + 0.5, d.door_z1)]
    add("RB6", [door], both=False, edges=[door + door[:1]])

    # hood
    h = hood(d)
    ox, oy, oz = h.origin
    at = lambda x, y, z: (x, oy + y, oz + z)
    nb = sum(1 for p in h.outline if p[1] <= h.z_corner + 1e-6)
    normals = offset(h.outline, 1.0)
    normals[0] = (h.outline[0][0] - 1.0, 0.0)
    quarter = [(d.hood_edge_in * (1 - math.sin(p)), d.hood_edge_back * (1 - math.cos(p))) for p in [math.pi / 2 * i / 8 for i in range(9)]]
    rows_h = [[at(x + (nx - x) * i, back, z + (nz - z) * i) for i, back in quarter] for (x, z), (nx, nz) in zip(h.outline, normals)]
    for j in range(8):
        add("HC4", strip([r[j] for r in rows_h], [r[j + 1] for r in rows_h]))
    add("HC4", [], edges=[[r[8] for r in rows_h], [r[0] for r in rows_h]])
    front_out = [at(x, 0.0, z) for x, z in h.edge_line]
    front_in = [at(x, 0.0, z) for x, z in h.opening]
    add("HC1", strip(front_out[:nb], front_in[:nb]), edges=[front_out[:nb], front_in[:nb]])
    add("HC2", strip(front_out[nb - 1:], front_in[nb - 1:]), edges=[front_out[nb - 1:], front_in[nb - 1:]])
    xs = h.half_open(h.z_sill, d)
    corner = [(h.half_open(h.z_sill + d.hood_sill_corner_r * (1 - i / 8), d), h.z_sill + d.hood_sill_corner_r * (1 - i / 8)) for i in range(9)]
    x0 = h.half_width(0.0, h.opening)
    right_sill = [at(x0, 0.0, 0.0)] + [at(x, 0.0, z) for x, z in corner]
    sill = right_sill + [(-x, y, z) for x, y, z in reversed(right_sill)]
    add("HC3", [sill], both=False, edges=[[at(x, 0.0, z) for x, z in corner] + [at(-x, 0.0, z) for x, z in reversed(corner)]])
    g = d.seam_groove
    side_line = ([(h.outline[0][0] - g, 0.0), (h.half_width(g), g)] if g > 0 else [h.outline[0]]) + [p for p in h.outline if p[1] > g + 1e-6]
    nb = sum(1 for p in side_line if p[1] <= h.z_corner + 1e-6)
    side_front = [at(x, d.hood_edge_back, z) for x, z in side_line]
    side_rear = [at(x, h.y_rear(z), z) for x, z in side_line]
    add("HC5", strip(side_front[:nb], side_rear[:nb]), edges=[side_front[:nb], side_rear[:nb]])
    add("HC6", strip(side_front[nb - 1:-1], side_rear[nb - 1:-1]), edges=[[side_front[nb - 1], side_rear[nb - 1]], [side_front[-2], side_rear[-2]]])
    roof = [at(-h.half_top, d.hood_edge_back, h.height), at(h.half_top, d.hood_edge_back, h.height),
            at(h.half_top, h.depth - d.hood_rear_arc_d, h.height), at(-h.half_top, h.depth - d.hood_rear_arc_d, h.height)]
    add("HC7", [roof], both=False)
    rear = [p for p in h.side if p[0] >= h.depth - d.hood_rear_arc_d - 1e-6]
    rear_l = [at(-h.half_width(z), y, z) for y, z in rear]
    rear_r = [at(h.half_width(z), y, z) for y, z in rear]
    na = sum(1 for y, z in rear if z >= h.height - d.hood_rear_arc_h - 1e-6)
    add("HC8", strip(rear_l[:na], rear_r[:na]), both=False, edges=[rear_r[:na], rear_l[:na]])
    add("HC9", strip(rear_l[na - 1:], rear_r[na - 1:]), both=False, edges=[rear_r[na - 1:], rear_l[na - 1:], [rear_l[na - 1], rear_r[na - 1]]])
    xo = h.half_width(h.z_open_top - 1.0, h.opening)
    add("HC10", [[at(-xo, 0.0, h.z_open_top), at(xo, 0.0, h.z_open_top), at(xo, h.y_marquee_top, h.z_open_top), at(-xo, h.y_marquee_top, h.z_open_top)]], both=False)
    inner = [(h.half_open(z, d), z) for x, z in h.opening if h.z_sill <= z <= h.z_open_top]
    add("HC11", strip([at(x, 0.0, z) for x, z in inner], [at(x, h.y_recess(z, d), z) for x, z in inner]))
    add("HC12", [[at(-xs, 0.0, h.z_sill), at(xs, 0.0, h.z_sill), at(xs, h.y_band_foot, h.z_sill), at(-xs, h.y_band_foot, h.z_sill)]], both=False)
    xr = h.half_open(h.z_band_top, d)
    yr = h.y_band_top - d.hood_rail_proud
    rail = [at(-xr, yr, h.z_band_top), at(xr, yr, h.z_band_top), at(xr, yr, h.z_rail_top), at(-xr, yr, h.z_rail_top)]
    add("HC13", [rail], both=False, edges=[rail + rail[:1]])

    def recess(z0: float, z1: float, n: int = 10) -> list[list[P3]]:
        zs = [z0 + (z1 - z0) * i / n for i in range(n + 1)]
        left = [at(-h.half_open(z, d), h.y_recess(z, d), z) for z in zs]
        return strip(left, [(-x, y, z) for x, y, z in left])

    add("HB1", recess(h.z_sill, h.z_band_top, 16), both=False)
    add("MQ1", recess(h.z_rail_top, h.z_open_top, 14), both=False)
    tm, tb = math.radians(d.marquee_tilt), math.radians(d.hood_band_tilt)

    def on_plane(origin: P2, tilt: float, down: bool) -> Callable[[float, float, float], P3]:
        up = (-math.sin(tilt), math.cos(tilt)) if down else (math.sin(tilt), math.cos(tilt))
        nrm = (-math.cos(tilt), -math.sin(tilt)) if down else (-math.cos(tilt), math.sin(tilt))
        return lambda x, v, n: at(x, origin[0] + up[0] * v + nrm[0] * n, origin[1] + up[1] * v + nrm[1] * n)

    def tilted(place: Callable[[float, float, float], P3], quad: list[P2], n: float, bands: int = 8) -> list[list[P3]]:
        """A quad (x, v) on a tilted plane, n proud of it, cut into bands along v so that it sorts by depth."""
        (a0, v0_), (b0, _), (b1, v1_), (a1, _) = quad
        rows = [(a0 + (a1 - a0) * i / bands, b0 + (b1 - b0) * i / bands, v0_ + (v1_ - v0_) * i / bands) for i in range(bands + 1)]
        return [[place(l0, u0, n), place(r0, u0, n), place(r1, u1, n), place(l1, u1, n)] for (l0, r0, u0), (l1, r1, u1) in zip(rows, rows[1:])]

    def raised(place: Callable[[float, float, float], P3], quad: list[P2], n: float) -> list[list[P3]]:
        """The four walls of a form that stands n proud on a tilted plane."""
        ring = quad + quad[:1]
        return [[place(*p, 0.0), place(*q, 0.0), place(*q, n), place(*p, n)] for p, q in zip(ring, ring[1:])]

    mq = on_plane((h.y_marquee_bottom, h.z_rail_top), tm, True)
    w, mh = marquee_window(d, h)
    window = [(-w / 2, d.marquee_margin), (w / 2, d.marquee_margin), (w / 2, d.marquee_margin + mh), (-w / 2, d.marquee_margin + mh)]
    add("MQ2", tilted(mq, window, 0.5, 4), both=False, edges=[[mq(x, v, 0.5) for x, v in window + window[:1]]])
    bd = on_plane((h.y_band_foot, h.z_sill), tb, False)
    length = (h.z_band_top - h.z_sill) / math.cos(tb)
    v0, v1 = d.speaker_foot_gap, length - d.speaker_head_gap
    leg = lambda v: h.half_width(max(h.z_sill + v * math.cos(tb), h.z_sill + d.hood_sill_corner_r), h.opening) - d.speaker_side_gap
    xi = d.logo_w / 2 + d.logo_gap
    form = [(xi, v0), (leg(v0), v0), (leg(v1), v1), (xi, v1)]
    g = d.grille_inset
    grille = [(xi + g, v0 + g), (leg(v0 + g) - g, v0 + g), (leg(v1 - g) - g, v1 - g), (xi + g, v1 - g)]
    add("SP1", tilted(bd, form, d.speaker_proud), edges=[[bd(x, v, d.speaker_proud) for x, v in form + form[:1]]])
    add("SP2", tilted(bd, grille, d.speaker_proud + 0.5), edges=[[bd(x, v, d.speaker_proud + 0.5) for x, v in grille + grille[:1]]])
    add("SP3", raised(bd, form, d.speaker_proud))
    lw, le = d.logo_w / 2, d.logo_end_gap
    logo = [(-lw, v0 + le), (lw, v0 + le), (lw, v1 - le), (-lw, v1 - le)]
    li = d.logo_inset
    plate = [(-lw + li, v0 + le + li), (lw - li, v0 + le + li), (lw - li, v1 - le - li), (-lw + li, v1 - le - li)]
    add("LG1", tilted(bd, logo, d.logo_proud), both=False, edges=[[bd(x, v, d.logo_proud) for x, v in logo + logo[:1]]])
    add("LG2", tilted(bd, plate, d.logo_proud + 0.5), both=False, edges=[[bd(x, v, d.logo_proud + 0.5) for x, v in plate + plate[:1]]])
    add("LG3", raised(bd, logo, d.logo_proud), both=False)
    return out
