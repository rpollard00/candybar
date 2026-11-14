"""The split: where the printed shell divides into pieces for the bed of the printer.

There is one layout: the owner's choice of 2026-11-11 (decision record 0006), the seams of the study's option B with
the hood of its option A, on the form of revision 7. The options that the owner did not choose are not in the code.
The layout holds its seams once, as data. A seam is a set of flat polygons in the cabinet frame with a name, a
class (hidden in a line that the design already has, or on an open face), the joint it gets, and whether it
opens again. A piece is a name, a seed point in it, and the direction that points up on the printer. The same data
drive the cut (main, under FreeCAD), the drawing (tools/draw_split.py) and the test (tests/test_split.py).

The seams follow the form. No seam goes through a hand-hold or a cut-in. The seams of the sides lie in the inner
crease of the band and in the crease of the rear shelf; the seams of the back lie on the centre line and on the
lines of the door's sides.

The cut divides the 4 mm skin of the outer form: the solids of solids.py less the cavity of cavity.py
(cavity.hollow). The skin takes about 20 minutes to make, so it is kept in cad/out/shell-rev7/split/cache (binary
BREP) under a fingerprint of
everything that makes it (the values of dims.Blueprint, the openings and the source of dims, profiles, solids and
cavity). The cut itself runs every time: it splits the skin with the seam polygons, names each piece by its seed,
and measures it in its print orientation (the box after a turn on the bed that makes it smallest) against the
usable volume of params/printer.csv.

    CANDYBAR_OUT=cad/out/shell-rev7 cad/candybar/freecad-run.sh candybar.shell.split

writes split/shell/ and split/bezel/ (one STL for each piece, manifest.json, seams.json) and
split/measurements.json. This module has no FreeCAD at import: the drawing tool imports it for the data and the words.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from dataclasses import dataclass, replace
from pathlib import Path

from . import profiles as pr
from .dims import Blueprint

P2 = tuple[float, float]
P3 = tuple[float, float, float]
Poly = tuple[P3, ...]

HIDDEN, FACE = "hidden", "face"
PETG_G_PER_CM3 = 1.27
CAD = Path(__file__).resolve().parents[2]
# the two things that are cut: the shell (the layout), and the bezel plate
SHELL, PLATE = "shell", "bezel"
# a seen face overhangs when it faces down more than OVERHANG from upright on the printer. A face within
# OVERHANG_BAND of that angle is at the limit: the facets of the rear shelf, the roofs of the hand-holds and the base
# facet are 45 degrees by design, and they print without support. The band is for the rounding of the mesh only
# (the facets come out within 0.001 of 45): a face at 45.1 counts as an overhang
OVERHANG = 45.0
OVERHANG_BAND = 0.05
# what each class means in the tables and on the drawings
CLASS_WORDS = {HIDDEN: "in a design line", FACE: "on an open face"}


# the seams that the outer form already has: no cut is needed for them
EXISTING = (
    ("G", "hood on the body: the level groove FB5 / HC15", "service",
     "The hood lifts off. Two pins at the front of the body top, two M4 screws through the foot of the hood's rear "
     "wall into inserts in the upper rear of the body (on the back)."),
    ("BZ4", "bezel plate in its reveal", "service",
     "The plate lifts out to the front. It rests on the ledge below it and is held by magnets and two pins (trim: no "
     "load). With the plate out, the opening behind it (422.7 x 293.4) is the service path of the monitor."),
    ("DK8", "control panel in its pocket", "service", "The panel latch is not designed yet (roadmap step 11)."),
    ("USB", "USB socket plate in the right side of the deck", "service",
     "A removable printed plate (fit study). Its outline is a seam of its own and ends 5 mm in front of D2."),
)


# ---------- the data ----------

@dataclass(frozen=True)
class Seam:
    """A cut surface: flat polygons in the cabinet frame (the right side, or both sides when mirror is False)."""
    label: str
    module: str
    polys: tuple[Poly, ...]
    cls: str
    joint: str
    reads: str
    mirror: bool = False
    side: str = ""

    @property
    def name(self) -> str:
        return f"{self.label} {self.side}".strip()


@dataclass(frozen=True)
class Piece:
    """A piece: a seed point near it, and the direction in the cabinet frame that points up on the printer."""
    name: str
    module: str
    seed: P3
    up: P3
    why: str
    mirror: bool = False
    side: str = ""
    bed: str = "upright"

    @property
    def full(self) -> str:
        return f"{self.name} {self.side}".strip()


@dataclass(frozen=True)
class Layout:
    """A set of seams and the pieces that they make."""
    key: str
    title: str
    idea: str
    seams: tuple[Seam, ...]
    pieces: tuple[Piece, ...]
    door: str = ""
    service: str = ""
    assembly: tuple[str, ...] = ()


@dataclass(frozen=True)
class Printer:
    """The usable volume of the bed, mm."""
    xy: float
    z: float
    bed: float
    source: str


def printer(params_dir: Path = CAD / "params") -> Printer:
    rows = {r["name"]: r for r in csv.DictReader(open(params_dir / "printer.csv", encoding="utf-8"))}
    if "a1_part_max_xy" in rows and "a1_part_max_z" in rows:
        return Printer(float(rows["a1_part_max_xy"]["value"]), float(rows["a1_part_max_z"]["value"]), float(rows["a1_bed"]["value"]),
                       "params/printer.csv: a1_part_max_xy, a1_part_max_z (bed less brim)")
    return Printer(250.0, 250.0, 256.0, "no limits in params/printer.csv: 250 x 250 x 250 assumed")


# ---------- polygons from lines in a view ----------

def side(points: list[P2], x0: float, x1: float) -> tuple[Poly, ...]:
    """A line in side view (y, z) carried across x0..x1: one quad for each segment."""
    return tuple(((x0, p[0], p[1]), (x1, p[0], p[1]), (x1, q[0], q[1]), (x0, q[0], q[1])) for p, q in zip(points, points[1:]))


def front(points: list[P2], y0: float, y1: float) -> tuple[Poly, ...]:
    """A line in front view (x, z) carried along y0..y1."""
    return tuple(((p[0], y0, p[1]), (p[0], y1, p[1]), (q[0], y1, q[1]), (q[0], y0, q[1])) for p, q in zip(points, points[1:]))


def top(points: list[P2], z0: float, z1: float) -> tuple[Poly, ...]:
    """A line in plan (x, y) carried up z0..z1."""
    return tuple(((p[0], p[1], z0), (q[0], q[1], z0), (q[0], q[1], z1), (p[0], p[1], z1)) for p, q in zip(points, points[1:]))


def level(points: list[P2], z: float) -> tuple[Poly, ...]:
    """A flat polygon at height z, its outline in plan."""
    return (tuple((x, y, z) for x, y in points),)


def mirror_point(p: P3) -> P3:
    return (-p[0], p[1], p[2])


def expanded(opt: Layout) -> tuple[list[Seam], list[Piece]]:
    """The seams and pieces of both sides: a mirrored item becomes a right one and a left one."""
    seams: list[Seam] = []
    for s in opt.seams:
        if s.mirror:
            seams.append(replace(s, side="R"))
            seams.append(replace(s, side="L", polys=tuple(tuple(mirror_point(p) for p in reversed(poly)) for poly in s.polys)))
        else:
            seams.append(s)
    pieces: list[Piece] = []
    for p in opt.pieces:
        if p.mirror:
            pieces.append(replace(p, side="R"))
            pieces.append(replace(p, side="L", seed=mirror_point(p.seed), up=mirror_point(p.up)))
        else:
            pieces.append(p)
    return seams, pieces


# ---------- the lines of the form that the seams use ----------

@dataclass(frozen=True)
class Lines:
    """Named positions on the outer form, from dims.Blueprint."""
    hw: float           # half the width
    y_foot: float       # the foot of the sweep: the deck ends here
    y_open: float       # just inside the back edge of the opening under the control panel
    x_jog: float        # in the 1 mm gap between the panel's side edge and the pocket wall
    x_kink: float       # the front corner of the pocket, where the panel's front turns to the flank
    flank: tuple[P2, P2]  # the bisector of the deck front's flank break: crease point, pocket corner
    z_crease: float     # the crease of the deck's edge section
    z_low: float        # level of the bezel's bottom corner on the rail land
    z_sill: float       # the sill of the rear door
    z_belt: float       # the crease of the rear shelf: on the lower rear wall and on the side of the lower body
    z_top: float        # the body top
    y_rear: float       # the lower rear wall
    y_back: float       # the upper rear wall (the back of the cabinet)
    crease: tuple[P2, ...]  # the inner crease of the band in side view (y, z), from below the desk up to z_low
    y_crease_sill: float    # the band's inner crease at the height of the door sill
    x_bay: float        # the gap between the logo form and the speaker forms on the hood band
    rear_half: float    # half the width of the lower body
    door: tuple[float, float, float]  # half width, z of its lower and upper edge
    grip: tuple[float, float, float, float]  # the hand-holds: x from, x to (right side), z from, z to
    cut_in: tuple[float, float, float, float]  # the cut-ins: x from (rear wall), y from (side), z from, z to
    chord_up: P3        # up the chord of the apron's centre piece (shelf to the bezel's bottom edge)


def lines(d: Blueprint) -> Lines:
    fr = pr.front(d)
    hw = d.width / 2
    y_foot = d.foot_y - d.bend_t
    opening = pr.panel_outline(d, -8.0)  # the ledge under the plate is cavity.Openings().panel_ledge wide
    y_open = opening[4][1] - 1.0
    pocket = pr.panel_outline(d, d.panel_gap)
    x_jog = d.panel_w / 2 + d.panel_gap / 2
    # the flank break of the deck front: the middle of its crease round, and the pocket's front corner
    plan = pr.deck_plan(d)
    crease = plan[3]
    mid = crease.at((crease.a0 + crease.a1) / 2)
    flank = (mid, pocket[2])
    z_low = fr.on_rail(d, d.bezel_s0)[1] + 0.3
    # the apron's centre piece: from the back of the ledge under the panel to the bezel's bottom edge on the rail
    a = (y_open, d.panel_top - d.panel_t - d.wall_t)
    b = fr.on_rail(d, d.bezel_s0)
    n = math.dist(a, b)
    chord_up = (0.0, (b[0] - a[0]) / n, (b[1] - a[1]) / n)
    # the band's inner crease from the desk up to z_low: the stub, the kick, and the lean as far as L1
    band = pr.band_crease(d)
    low = [p for p in band if p[1] < z_low] + [(pr.crease_y(d, z_low), z_low)]
    low[0] = (low[0][0], -1.0)
    return Lines(hw, y_foot, y_open, x_jog, pocket[2][0], flank, d.deck_top - d.deck_lean_h, z_low, d.door_z0, d.rear_shelf_z0, d.body_top,
                 d.body_d, d.depth, tuple(low), pr.crease_y(d, d.door_z0), d.logo_w / 2 + d.logo_gap, d.rear_w / 2,
                 (d.door_w / 2, d.door_z0, d.door_z1), (d.grip_x0, d.grip_x1, d.grip_z0, d.grip_z1),
                 (d.cut_in_x, d.cut_in_y, d.cut_in_z0, d.cut_in_z1), chord_up)


def along(a: P2, b: P2, t0: float, t1: float) -> list[P2]:
    """The line through a and b, from parameter t0 to t1 (0 at a, 1 at b)."""
    return [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for t in (t0, t1)]


# ---------- the seams ----------

def deck_seams(L: Lines) -> list[Seam]:
    (cx, cy), (kx, ky) = L.flank
    t_end = (L.y_open - cy) / (ky - cy)
    t_front = (-12.0 - cy) / (ky - cy)
    flank = along((cx, cy), (kx, ky), t_front, t_end)
    out = 2 * L.hw
    return [
        Seam("D1", "body", top([(-L.x_jog, L.y_foot), (-L.x_jog, L.y_open), (L.x_jog, L.y_open), (L.x_jog, L.y_foot)], -1.0, 95.0),
             HIDDEN, "bond-line",
             "Deck to body. Under the control panel, along the back of its opening; at each end 15 mm on the line of "
             "the pocket's side edge, in the 1 mm gap and then across the shelf. Not seen with the panel in."),
        Seam("D2", "body", top([(L.x_jog, L.y_foot), (out, L.y_foot)], -1.0, 95.0), FACE, "bond-fill",
             "Deck to body beside the panel: across the deck border at the foot of the sweep (where the sweep starts "
             "to rise), round the deck's edge and down the side, 72 mm upright. From the seat it is a short line at "
             "the start of the sweep; from the side an upright line under the cheek's foot.", mirror=True),
        Seam("F1", "body", top(flank, -1.0, L.z_crease), HIDDEN, "bond-line",
             "Deck front at the flank break: in the crease where the centre face turns 8 degrees to the flank.", mirror=True),
        Seam("F2", "body", top(flank, L.z_crease, 95.0), FACE, "bond-fill",
             "Over the deck's front edge and across the 25 mm border to the front corner of the panel, on the "
             "bisector of the flank break. It reads as the panel's corner carried to the front. It is 62 mm outside "
             "the lever axis and 14 mm outside the lever's mounting plate.", mirror=True),
        Seam("P1", "body", top([(L.x_kink, L.y_open - 1.0), (L.x_kink, 300.0)], 60.0, 200.0), FACE, "bond-fill",
             "Up the shelf, the sweep and the apron to the bezel's bottom edge, in line with the panel's front "
             "corner and F1. Two upright lines below the screen, 273 mm apart: they frame the centre of the panel.", mirror=True),
    ]


def side_seams(L: Lines) -> list[Seam]:
    """The seams of the sides and of the lower rear corners. They follow the band and the rear shelf."""
    x = L.door[0]
    y_low = L.crease[-1][0]
    return [
        Seam("L1", "body", level([(L.x_kink, 250.0), (300.0, 250.0), (300.0, y_low), (L.x_kink, y_low)], L.z_low)
             + level([(x, L.y_crease_sill), (300.0, L.y_crease_sill), (300.0, 600.0), (x, 600.0)], L.z_sill),
             FACE, "bond-fill",
             "Level line in two parts, with its step hidden in the crease of the band (S1). In front of the band it "
             "lies at the bezel's bottom corner: across the rail land and its edge and along the side band to the "
             "band. From the seat it continues the bezel's bottom edge to the outer edge. Behind the band it lies at "
             f"the height of the door sill (z {L.z_sill:.0f}): along the side of the lower body, round the rear corner and "
             f"on the lower rear wall to the door's side. It continues the line of the sill, {L.cut_in[2] - L.z_sill:.0f} mm below the "
             "lowest cut-in.", mirror=True),
        Seam("B1", "body", level([(200.0, 250.0), (300.0, 250.0), (300.0, 600.0), (x, 600.0), (x, 530.0), (200.0, 530.0)], L.z_belt),
             FACE, "bond-fill",
             f"Belt line in the crease of the rear shelf (z {L.z_belt:.0f}). On the back it lies in the crease under the "
             "head, from the rear corner to the line of the door's side. On each side it lies in the crease of the "
             "band's level run; in front of that it crosses the band and the side band to the rail. From the seat a "
             "short level line on the rail land; from the side one level line under the head.", mirror=True),
        Seam("S1", "body", side(list(L.crease), -300.0, 300.0), HIDDEN, "bond-line",
             "Front to rear body below L1: in the inner crease of the band (its stub, its kick and its lean)."),
    ]


def rear_seams(L: Lines) -> list[Seam]:
    """The seams of the back: the door, the centre line, and the lines of the door's sides. The hand-holds lie
    between the centre line and the door's sides; the cut-ins lie outside the door's sides, above L1."""
    x, z0, z1 = L.door
    return [
        door_outline(L),
        Seam("R1", "body", front([(x, z1), (x, L.z_belt)], 520.0, 560.0), FACE, "bond-fill",
             f"{L.z_belt - z1:.0f} mm on the back, from the door's top corner up to the crease of the rear shelf, on the line of the door's side.",
             mirror=True),
        Seam("R2", "body", front([(0.0, -1.0), (0.0, z0)], 520.0, 560.0), FACE, "bond-fill", "On the centre line of the back, below the door."),
        Seam("R3", "body", front([(x, L.z_belt), (x, 440.0)], 520.0, 600.0), FACE, "bond-fill",
             "On the back above the crease of the rear shelf, on the line of the door's side: up the rear facet and "
             f"the upper rear wall to the groove. It continues R1. It is {x - L.grip[1]:.0f} mm outside the hand-hold.", mirror=True),
        Seam("R4", "body", front([(0.0, z0), (0.0, z1)], 520.0, 560.0), FACE, "bond-fill", "On the centre line of the door: two halves bonded into one."),
        Seam("R5", "body", front([(0.0, z1), (0.0, 440.0)], 520.0, 600.0), FACE, "bond-fill",
             "On the centre line of the back above the door: up the frame above the door, the rear facet and the "
             f"upper rear wall to the groove. It continues R4 and R2. It is {L.grip[0]:.0f} mm from each hand-hold."),
    ]


def hood_bays(L: Lines, x: float) -> list[Seam]:
    return [Seam("H1", "hood", top([(x, 420.0), (x, 600.0)], 420.0, 600.0), FACE, "bond-fill",
                 "Hood at the gap between the logo form and the speaker form: up the sill and the ledge, along the "
                 "inner end of the speaker form, over the lip, the top bar (21 mm) and the soft edge, across the roof "
                 "and down the rear arc and the rear wall. From the seat two short upright lines on the top bar, in "
                 "line with the inner ends of the speaker forms.", mirror=True)]


def brow(L: Lines, x: float) -> Seam:
    return Seam("W1", "body", top([(x, 380.0), (x, 470.0)], 300.0, 440.0), FACE, "bond-fill",
                "Brow above the bezel: 32 mm upright from the bezel's top edge to the groove, in line with H1 on "
                "the hood above it. It reads as the hood's bay line carried down to the bezel.", mirror=True)


def base_seams(L: Lines) -> list[Seam]:
    long = top([(L.x_bay, -10.0), (L.x_bay, 600.0)], -2.0, 10.0)
    return [Seam("BA1", "base", long, HIDDEN, "base", "Under the cabinet, below the bay lines.", mirror=True),
            Seam("BA2", "base", top([(-300.0, 194.0), (300.0, 194.0)], -2.0, 10.0), HIDDEN, "base", "Under the cabinet."),
            Seam("BA3", "base", top([(-300.0, 357.0), (300.0, 357.0)], -2.0, 10.0), HIDDEN, "base", "Under the cabinet.")]


def base_pieces() -> list[Piece]:
    up, why = (0.0, 0.0, 1.0), ("Flat, on the bed: a sandwich of 10 mm, two skins of 1.2 mm and a gyroid core of 40 %. "
                                "It is not seen.")
    return [Piece(f"floor {row} {col}", "base", (x, y, 2.0), up, why, mirror=x > 0, bed="flat")
            for row, y in (("front", 100.0), ("middle", 275.0), ("rear", 450.0)) for col, x in (("side", 175.0), ("centre", 0.0))]


def door_outline(L: Lines) -> Seam:
    x, z0, z1 = L.door
    return Seam("DR", "body", front([(-x, z0), (x, z0), (x, z1), (-x, z1), (-x, z0)], 520.0, 560.0), HIDDEN, "service",
                f"The rear door: its own gap (the opening of dims.Blueprint, {2 * x:.1f} x {z1 - z0:.0f}).")


def trim_pieces() -> list[Piece]:
    why = "Front face on the bed: the face that is seen is the smoothest one."
    bed = "front face on the bed"
    return [Piece("speaker form", "speaker_right", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), why, side="R", bed=bed),
            Piece("speaker form", "speaker_left", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), why, side="L", bed=bed),
            Piece("logo form", "logo_form", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), why, bed=bed)]


# ---------- the print orientations, in words ----------

UP = (0.0, 0.0, 1.0)
WHY = {
    "deck nose": ("upright, on the bed diagonal", "Upright, along the bed diagonal (it is 277 long). The deck front is a wall, so its layer lines run "
                 "level across it; the 25 mm border prints as the top. The ledge for the panel inside needs a 45 degree "
                 "gusset."),
    "deck side": ("upright", "Upright. Front, corner and side are walls; the border and the edge radius are the top."),
    "apron": ("on its rear edge, on the bed diagonal", "On its rear edge with the chord from the shelf to the bezel's bottom edge upright, along the bed "
             "diagonal (it is 273 long). The concave sweep then faces sideways; only its lower end overhangs more "
             "than 45 degrees (about 3 cm2: a support there, sanded before primer). The rear wall of the panel pocket "
             "overhangs 45.5 degrees; the control panel hides it. Layer lines run across the width."),
    "lower": ("upright", "Upright. The side, the rail's foot, the sweep and the foot of the band are walls or face up; the base facet is 45 degrees."),
    "middle": ("upright, on the bed diagonal", "Upright, along the bed diagonal: it is a thin wall with a short return on the back. The side and the "
              "band are walls with level layer lines. The rail land is reclined 25 to 33 degrees and shows fine "
              "layer steps; they sand out under primer. The four cut-ins are in this piece: the upper half of each "
              "groove faces down 33 degrees at its lip, less than the limit."),
    "upper": ("upright", "Upright: the tuck leans in (no overhang), the seam bevel and the brow are on top. The side facet of the "
             "rear shelf is under the head: it is 45 degrees, at the limit, and prints without support."),
    "brow": ("upright", "Upright: the brow faces up and forward."),
    "upper rear": ("upright", "Upright: the rear facet of the rear shelf and the roof of the hand-hold are 45 degrees, at the limit; "
                  "the upper rear wall is a wall. The hand-hold is whole in this piece."),
    "rear lower": ("upright", "Upright: rear wall and side are walls; the base facet is 45 degrees."),
    "door": ("outer face on the bed", "Outer face on the bed: the door is a flat cover, so this gives the smoothest face and the best strength in its plane."),
    "hood centre": ("on a cut face", "On its cut face: inside the top flat the hood is a straight extrusion, so every face prints as a wall "
                   "and the rear arc and the front lean are smooth. No support, no layer steps."),
    "hood side": ("upright", "Upright: the side and the leg are near-upright walls; the top corner steps near the roof and the "
                 "end of the soffit needs a small support inside the marquee opening."),
}


def piece(name: str, module: str, seed: P3, up: P3, key: str, mirror: bool = False) -> Piece:
    bed, why = WHY[key]
    return Piece(name, module, seed, up, why, mirror, bed=bed)


# ---------- the layout ----------

def layout(d: Blueprint) -> Layout:
    """The split that the owner chose on 2026-11-11 (decision record 0006), on the form of revision 7."""
    L = lines(d)
    bay = L.x_bay
    seams = deck_seams(L) + side_seams(L) + rear_seams(L) + [brow(L, bay)] + hood_bays(L, bay) + base_seams(L)
    x_wall = L.rear_half - 2.0
    pieces = [
        piece("deck nose", "body", (0.0, 2.0, 30.0), UP, "deck nose"),
        piece("deck side", "body", (L.hw - 2.0, 120.0, 20.0), UP, "deck side", mirror=True),
        piece("apron", "body", (0.0, 243.8, 85.2), L.chord_up, "apron"),
        piece("lower", "body", (L.hw - 2.0, 300.0, 60.0), UP, "lower", mirror=True),
        piece("middle", "body", (L.hw - 2.0, 380.0, 220.0), UP, "middle", mirror=True),
        piece("upper", "body", (d.side_x(380.0) - 2.0, 500.0, 380.0), UP, "upper", mirror=True),
        piece("brow", "body", (0.0, 432.0, 408.7), UP, "brow"),
        piece("upper rear", "body", ((L.grip[1] + L.door[0]) / 2, L.y_back - 2.0, 380.0), UP, "upper rear", mirror=True),
        piece("rear lower", "body", (x_wall, 450.0, 60.0), UP, "rear lower", mirror=True),
        piece("door half", "body", (110.0, L.y_rear - 2.0, 200.0), (0.0, -1.0, 0.0), "door", mirror=True),
        piece("hood centre", "hood", (0.0, 520.0, 571.0), (1.0, 0.0, 0.0), "hood centre"),
        piece("hood side", "hood", (219.0, 520.0, 500.0), UP, "hood side", mirror=True),
    ] + trim_pieces() + base_pieces()
    return Layout(
        SHELL, "The split of the shell (the owner's choice of 2026-11-11, on revision 7)",
        "Every seam lies in a line that the form has, or carries such a line on: the deck's flank break and the "
        "panel's front corner (x = +-137), the bezel's bottom corner and the door sill (L1), the crease of the rear "
        "shelf (B1), the inner crease of the band (S1), the bays of the hood band (x = +-106) on the brow and the "
        "hood, the door's edges, and on the back the centre line and the lines of the door's sides. The hand-holds "
        "and the cut-ins are whole in one piece each.",
        tuple(seams), tuple(pieces),
        "Two halves on the centre line, bonded into one cover with the fan vent and the slot vents in it and nothing "
        "wired to it. It lifts off; its own gap (DR) is the service joint. The seam runs into the left end of the "
        "fan vent, between two of its bars.",
        "The hood (groove G), the rear door (DR), the control panel (pocket), the bezel plate (reveal; the monitor "
        "comes out behind it) and the USB plate. Every other seam is bonded for good, the floor tiles too.",
        ("Bond and screw the nine floor tiles; stick the non-slip pads under them.",
         "Bond the rear: the two rear lower pieces, on the floor (R2).",
         "Bond the deck: deck nose and deck sides; then the apron and the two lower pieces (D1, D2, P1, S1).",
         "Bond the two middle pieces (L1), then the brow, the two upper pieces and the two upper rear pieces (B1, W1, R1, R3, R5).",
         "Bond the two door halves into one cover; bond the three hood pieces and the lip.",
         "Dry assembly with all hardware: power supply and hub on the floor, compute module on its "
         "carrier through the door opening, monitor on its carrier from the front through the bezel opening.",
         "Take the hardware out, fill and paint the permanent seams, and assemble again."))


BEZEL_OPTIONS = (
    ("1", "Two halves on the centre line, bonded into one plate",
     "Each half stands on its cut face (217 tall); its side profile lies along the bed diagonal. The land's arc and "
     "the inner frame are in the layer plane, so they print smooth, with no support. The seam crosses the top and "
     "bottom of the frame on the centre line (45 mm each: 20 of land, 25 of inner frame). The plate is a cosmetic "
     "subassembly, so the seam is filled and painted black. Two pieces for each plate: eight for the four plates."),
    ("2", "Four bars, mitred at the corners",
     "Mitres hide in the corner creases of the inner frame (BZ2) but cross the land at 45 degrees (28 mm on face at "
     "each corner). The top and bottom bars are 435 long, so each needs a centre seam as well: six pieces for each "
     "plate. More seams than option 1 for the same result."),
    ("3", "A cut plate with a printed inner frame",
     "One cut sheet (black anodised aluminium or acrylic) for the land, rolled to the rail arc (radius 1.33 m), and "
     "the sloped inner frame printed behind it. The sheet needs no seam. But the inner frame is 395 long at the top "
     "and the bottom, so it still has seams; and a rolled sheet with a window changes the land from a 20 mm band of "
     "the frame to a flat sheet edge. It changes the accepted form of BZ1 and BZ2."),
)
BEZEL_RECOMMENDED = "1"
# option 1, measured: the plate cut on the centre line, each half on its cut face
BEZEL = Layout(PLATE, "bezel plate in two halves", "",
               (Seam("Z1", "bezel", front([(0.0, 0.0), (0.0, 600.0)], 0.0, 700.0), FACE, "bond-fill",
                     "On the centre line of the plate: over the land and the inner frame at the top and the bottom."),),
               (Piece("bezel half", "bezel", (100.0, 276.0, 141.0), (1.0, 0.0, 0.0),
                      "On its cut face: the land's arc and the inner frame lie in the layer plane and print smooth.",
                      mirror=True, bed="on its cut face, the profile on the bed diagonal"),))


# ---------- the inputs of the skin, for the cache ----------

def fingerprint(d: Blueprint) -> str:
    """A hash of everything that makes the skin: the dimensions, the openings and the source that builds it."""
    from . import cavity  # noqa: PLC0415 - needs FreeCAD

    h = hashlib.sha256(repr(d).encode())
    h.update(repr(cavity.Openings()).encode())
    for name in ("dims.py", "profiles.py", "solids.py", "cavity.py"):
        h.update((Path(__file__).parent / name).read_bytes())
    return h.hexdigest()[:16]


def cache_dir() -> Path:
    """Where the skin is kept: beside the default build, for every run and for the tests."""
    return Path(os.environ.get("CANDYBAR_SPLIT_CACHE") or CAD / "out" / "shell-rev7" / "split" / "cache")


# ---------- the print box: pure numpy, so that the test can use it on its own ----------

def frame_of(up: P3):
    import numpy as np  # noqa: PLC0415

    u = np.array(up, float)
    u /= np.linalg.norm(u)
    a = np.array((1.0, 0.0, 0.0)) if abs(u[0]) < 0.9 else np.array((0.0, 1.0, 0.0))
    e1 = np.cross(u, a)
    e1 /= np.linalg.norm(e1)
    return e1, np.cross(u, e1), u


def print_box(points, up: P3, lim: Printer, step: float = 0.5) -> dict:
    """The box of the points with `up` pointing up on the printer, turned on the bed (yaw) so that its larger side
    is as small as it can be."""
    import numpy as np  # noqa: PLC0415

    p = np.asarray(points, float)
    e1, e2, u = frame_of(up)
    a, b, h = p @ e1, p @ e2, p @ u
    best = None
    for deg in np.arange(0.0, 90.0, step):
        t = math.radians(deg)
        x = a * math.cos(t) + b * math.sin(t)
        y = -a * math.sin(t) + b * math.cos(t)
        ext = (float(x.max() - x.min()), float(y.max() - y.min()))
        key = max(ext)
        if best is None or key < best[0] - 1e-9:
            best = (key, deg, ext)
    key, deg, (ex, ey) = best
    ez = float(h.max() - h.min())
    lo, hi = sorted((ex, ey))
    return {"yaw": float(deg), "x": round(hi, 1), "y": round(lo, 1), "z": round(ez, 1),
            "fits": hi <= lim.xy + 1e-6 and ez <= lim.z + 1e-6}


# ---------- the cut, under FreeCAD ----------

def door_of(d: Blueprint) -> dict:
    """The opening of the rear door, as the form sets it (dims.Blueprint): inside the cut-ins and below the rear shelf."""
    x = d.door_w / 2
    return {"x0": -x, "x1": x, "z0": d.door_z0, "z1": d.door_z1, "w": 2 * x, "h": d.door_z1 - d.door_z0}


@dataclass
class Modules:
    """What the seams cut: the skin of the walls, the base and the hood, the trims and the bezel; and the outer
    solids, which say where the outside of each module is."""
    skin: dict
    outer: dict
    parts: dict
    key: str


SKIN_MODULES = ("body", "base", "hood")


def skin_files(d: Blueprint) -> dict[str, Path]:
    """The cache file of each module of the skin, for the fingerprint of d and the source."""
    key = fingerprint(d)
    return {k: cache_dir() / f"{k}-{key}.bin" for k in SKIN_MODULES}


def skin_cached(d: Blueprint) -> bool:
    return all(f.exists() for f in skin_files(d).values())


def build_modules(d: Blueprint, log=print, parts: dict | None = None, cav=None) -> Modules:
    """The modules of the built parts (built here when not given). The skin comes from the cache when its
    fingerprint is there; else it is made (with the cavity `cav` when given) and written to the cache. In both cases
    the skin that the seams cut is the one read from the cache files, so that every run cuts the same shapes.

    The cache files are binary BREP, which keeps every number as it is. The text BREP keeps 15 digits, and the
    narrow step faces of the skin are not valid when they come back from it."""
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415

    from . import cavity  # noqa: PLC0415
    from . import solids as so  # noqa: PLC0415

    key = fingerprint(d)
    cache = cache_dir()
    parts = parts or so.build(d)
    outer_body = so.unsplit(parts["deck"].fuse(parts["body"]))
    outer_hood = so.unsplit(parts["hood"].fuse(parts["marquee_lip"]))
    files = skin_files(d)
    if skin_cached(d):
        log(f"split: skin from the cache {key}")
    else:
        log("split: making the skin (about 20 minutes)")
        cav = cav or cavity.build(parts, d)
        slabs = [p for p in cav.pieces if p.BoundBox.ZMin < d.wall_t + 1.0]
        z = d.wall_t + 0.5
        floor = [Part.Face(w) for p in slabs for w in p.slice(App.Vector(0, 0, 1), z)]
        region = floor[0].fuse(floor[1:]).removeSplitter() if len(floor) > 1 else floor[0]
        region = region.translated(App.Vector(0, 0, -z - 1.0)).extrude(App.Vector(0, 0, z + 1.0))
        body = cavity.hollow(outer_body, cav)
        made = {"base": body.common(region), "body": body.cut(region), "hood": cavity.hollow(outer_hood, cav)}
        cache.mkdir(parents=True, exist_ok=True)
        for k, f in files.items():
            made[k].exportBinary(str(f))
    skin = {}
    for k, f in files.items():
        skin[k] = Part.Shape()
        skin[k].importBinary(str(f))
        if not skin[k].isValid():
            bad = [face for face in skin[k].Faces if not face.isValid()]
            raise RuntimeError(f"split: the skin of {k} ({f.name}) is not a valid shape: {len(bad)} of its {len(skin[k].Faces)} faces are not valid")
    outer = {"body": outer_body, "base": outer_body, "hood": outer_hood}
    for k in TRIMS:
        skin[k] = outer[k] = parts[k]
    return Modules(skin, outer, parts, key)


TRIMS = ("speaker_right", "speaker_left", "logo_form", "bezel")
DEBRIS_MM3 = 50.0


def grown(bb, by: float):
    import FreeCAD as App  # noqa: PLC0415

    return App.BoundBox(bb.XMin - by, bb.YMin - by, bb.ZMin - by, bb.XMax + by, bb.YMax + by, bb.ZMax + by)


KERF = 0.1


def kerf(face):
    """The seam as a slab KERF thick. A split by the bare face leaves the stepped skin in one piece where it should
    not (the generalFuse of OCCT keeps it connected); a thin cut away separates it, and changes no box by more than
    KERF / 2."""
    n = face.normalAt(0, 0)
    return face.translated(n * (-KERF / 2)).extrude(n * KERF)


def poly_face(poly: Poly):
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415

    pts = [App.Vector(*p) for p in poly]
    return Part.Face(Part.makePolygon(pts + [pts[0]]))


def cut(opt_seams: list[Seam], opt_pieces: list[Piece], mods: Modules) -> tuple[dict, list[dict]]:
    """Split each module with its seams and name the pieces by their seeds. Returns {piece: shape} and a list of
    problems (an unnamed piece, a seed that two pieces share, debris)."""
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415

    out, problems = {}, []
    for module in sorted({p.module for p in opt_pieces}):
        shape = mods.skin[module]
        faces = [poly_face(poly) for s in opt_seams if s.module == module for poly in s.polys]
        solids = list(shape.cut([kerf(f) for f in faces]).Solids) if faces else list(shape.Solids)
        debris = [s for s in solids if s.Volume < DEBRIS_MM3]
        solids = [s for s in solids if s.Volume >= DEBRIS_MM3]
        if debris:
            problems.append({"module": module, "problem": "debris", "count": len(debris), "volume_mm3": round(sum(s.Volume for s in debris), 1)})
        wanted = [p for p in opt_pieces if p.module == module]
        if len(solids) == 1 and len(wanted) == 1 and not faces:
            out[wanted[0].full] = solids[0]
            continue
        taken: dict[int, str] = {}
        for p in wanted:
            seed = App.Vector(*p.seed)
            dist = [s.distToShape(Part.Vertex(seed))[0] if grown(s.BoundBox, 25.0).isInside(seed) else math.inf for s in solids]
            k = min(range(len(solids)), key=lambda i: dist[i])
            if dist[k] > 25.0:
                problems.append({"module": module, "problem": "seed far from every piece", "piece": p.full, "distance": round(dist[k], 1)})
            if k in taken:
                problems.append({"module": module, "problem": "two seeds in one piece", "piece": p.full, "other": taken[k]})
            taken[k] = p.full
            out[p.full] = solids[k]
        for i, s in enumerate(solids):
            if i not in taken:
                c = s.BoundBox.Center
                problems.append({"module": module, "problem": "piece without a name", "volume_cm3": round(s.Volume / 1000, 1),
                                 "centre": [round(c.x), round(c.y), round(c.z)]})
    return out, problems


def cover_shapes(d: Blueprint):
    """Where a face of the shell is under a plate (the bezel plate, the control panel) or under the hood: not seen."""
    import FreeCAD as App  # noqa: PLC0415

    from . import solids as so  # noqa: PLC0415

    bw = d.bezel_w / 2 + d.panel_gap + 0.5
    origin, up, into = so.screen_frame(d)
    plate = so.slab(origin, up, into, (-bw, bw), (d.bezel_s0 - 0.5, d.bezel_s1 + 0.5), (-30.0, d.mon_setback + d.wall_t + 2.0))
    # the control panel in its pocket: from below the ledge up to where the edge break of the pocket's rim starts, so
    # that the whole upright wall of the pocket is under the plate (a box that ended lower counted that wall as
    # seen on one side of the cabinet and as hidden on the other)
    z0 = d.panel_top - d.panel_t - 9.0
    pocket = so.prism(so.poly(pr.panel_outline(d, d.panel_gap + 0.5)), so.xy(z0), App.Vector(0, 0, d.panel_top - d.edge_break - z0))
    return [plate, pocket]


def seam_planes(seams: list[Seam], module: str) -> list[tuple]:
    """The plane of each seam polygon of a module: a point on it and its unit normal."""
    import numpy as np  # noqa: PLC0415

    out = []
    for s in seams:
        if s.module != module:
            continue
        for poly in s.polys:
            p = np.array(poly, float)
            n = np.cross(p[1] - p[0], p[2] - p[0])
            out.append((p[0], n / np.linalg.norm(n)))
    return out


def faces_of(piece, outer, covers, d: Blueprint, planes=()):
    """Each face of a piece with its triangles (outward normals) and its kind: 'seen' (outer face that a person sees),
    'hidden' (outer face under a plate, under the hood or on the desk) or 'inside' (cavity or cut face).

    A cut face is a flat face that lies KERF / 2 from the plane of a seam (planes: seam_planes of the piece's
    module). It is known by that, not by a point beside it: a cut face that ends in the gap round the control panel
    has such points outside the form, and it then counted as seen on one side of the cabinet and not on the other."""
    import FreeCAD as App  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415
    import Part  # noqa: PLC0415

    out = []
    for f in piece.Faces:
        pts, tris = f.tessellate(1.0)
        if not tris:
            continue
        p = np.array([(v.x, v.y, v.z) for v in pts])
        t = np.array(tris)
        n = np.cross(p[t[:, 1]] - p[t[:, 0]], p[t[:, 2]] - p[t[:, 0]])
        area = np.linalg.norm(n, axis=1) / 2
        k = int(np.argmax(area))
        c = p[t[k]].mean(axis=0)
        try:
            uv = f.Surface.parameter(App.Vector(*c))
            ref = f.normalAt(*uv)
        except Exception:  # noqa: BLE001 - a degenerate face: keep the winding
            ref = App.Vector(*n[k])
        if np.dot(n[k], (ref.x, ref.y, ref.z)) < 0:
            n = -n
        unit = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)
        q = App.Vector(*(c + unit[k] * 0.3))
        flat = isinstance(f.Surface, Part.Plane)
        if flat and any(abs(abs(float(unit[k] @ pn)) - 1.0) < 1e-6 and abs(abs(float((c - pp) @ pn)) - KERF / 2) < 1e-3 for pp, pn in planes):
            kind = "inside"
        elif outer.isInside(q, 1e-3, True):
            kind = "inside"
        else:
            centre = App.Vector(*c)
            under = unit[k][2] < -0.99 and c[2] < 0.5
            top = unit[k][2] > 0.99 and abs(c[2] - d.body_top) < 0.5
            foot = unit[k][2] < -0.99 and abs(c[2] - d.body_top - d.seam_gap) < 0.5
            covered = any(s.isInside(centre, 1e-3, True) for s in covers)
            kind = "hidden" if under or top or foot or covered else "seen"
        out.append((kind, p[t].reshape(-1, 3, 3), unit, area))
    return out


def measure(piece, up: P3, lim: Printer, outer, covers, d: Blueprint, detail: bool = True, planes=()) -> dict:
    """The box in the print orientation, the mass of the skin, and what the orientation does to the faces that are
    seen: area that overhangs more than OVERHANG (by more than OVERHANG_BAND), area at that limit (within the band:
    the 45 degree facets of the design), area of shallow tops that show layer terraces, area on the bed. Without
    detail, only the box and the mass."""
    import numpy as np  # noqa: PLC0415

    if not detail:
        pts, _ = piece.tessellate(0.5)
        box = print_box([(v.x, v.y, v.z) for v in pts], up, lim)
        return {**box, "up": [round(v, 3) for v in up], "volume_cm3": round(piece.Volume / 1000, 1),
                "mass_g": round(piece.Volume / 1000 * PETG_G_PER_CM3)}
    faces = faces_of(piece, outer, covers, d, planes)
    pts = np.concatenate([tri.reshape(-1, 3) for _, tri, _, _ in faces])
    box = print_box(pts, up, lim)
    u = np.array(up, float)
    u /= np.linalg.norm(u)
    h = pts @ u
    z0 = h.min()
    acc = {"seen": 0.0, "overhang_seen": 0.0, "limit_seen": 0.0, "terrace_seen": 0.0, "overhang_inside": 0.0, "bed": 0.0}
    over, limit = -math.sin(math.radians(OVERHANG + OVERHANG_BAND)), -math.sin(math.radians(OVERHANG - OVERHANG_BAND))
    for kind, tri, unit, area in faces:
        nz = unit @ u
        zc = tri.mean(axis=1) @ u
        at_bed = zc < z0 + 0.5
        if kind == "seen":
            acc["seen"] += area.sum()
            acc["overhang_seen"] += area[(nz < over) & ~at_bed].sum()
            acc["limit_seen"] += area[(nz >= over) & (nz <= limit) & ~at_bed].sum()
            acc["terrace_seen"] += area[(nz > math.cos(math.radians(25))) & (nz < 0.9998)].sum()
        elif kind == "inside":
            acc["overhang_inside"] += area[(nz < over) & ~at_bed].sum()
        acc["bed"] += area[(nz < -0.9998) & at_bed].sum()
    bb = piece.BoundBox
    return {**box, "up": [round(v, 3) for v in up], "volume_cm3": round(piece.Volume / 1000, 1),
            "mass_g": round(piece.Volume / 1000 * PETG_G_PER_CM3), "cabinet": [round(bb.XMin, 1), round(bb.XMax, 1), round(bb.YMin, 1),
                                                                              round(bb.YMax, 1), round(bb.ZMin, 1), round(bb.ZMax, 1)],
            **{k: round(v / 100, 1) for k, v in acc.items()}}


def seam_lines(seams: list[Seam], mods: Modules, covers) -> dict:
    """Where each seam meets the outside of its module: polylines in 3D, and the length that a person sees."""
    import FreeCAD as App  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415

    out = {}
    for s in seams:
        outer = mods.outer[s.module]
        lines_, seen = [], 0.0
        for poly in s.polys:
            sec = outer.section(poly_face(poly))
            for e in sec.Edges:
                pts = np.array([(v.x, v.y, v.z) for v in e.discretize(Distance=1.5)])
                if len(pts) < 2:
                    continue
                lines_.append(np.round(pts, 2).tolist())
                mid = (pts[1:] + pts[:-1]) / 2
                seg = np.linalg.norm(pts[1:] - pts[:-1], axis=1)
                ok = np.array([m[2] > 0.5 and not any(c.isInside(App.Vector(*m), 1e-3, True) for c in covers) for m in mid])
                seen += float(seg[ok].sum())
        out[s.name] = {"label": s.label, "side": s.side, "module": s.module, "cls": s.cls, "joint": s.joint, "reads": s.reads,
                       "lines": lines_, "seen_mm": round(seen, 1)}
    return out


TINTS = ("#e8c39e", "#9ec5e8", "#b9dea0", "#e3a8c8", "#f0e09a", "#a8d8d0", "#c9b8e8", "#f2b8a0")


def tints(shapes: dict) -> dict:
    """A soft colour for each piece, different from its neighbours (boxes that touch), the same for a mirrored pair."""
    names = list(shapes)
    pair = lambda n: n[:-2] if n.endswith((" R", " L")) else n
    groups = {}
    for n in names:
        groups.setdefault(pair(n), []).append(n)
    boxes = {n: shapes[n].BoundBox for n in names}
    near = lambda a, b: all(boxes[a].__getattribute__(f"{c}Min") - 1.0 <= boxes[b].__getattribute__(f"{c}Max") and
                            boxes[b].__getattribute__(f"{c}Min") - 1.0 <= boxes[a].__getattribute__(f"{c}Max") for c in "XYZ")
    colour = {}
    order = sorted(groups, key=lambda g: -sum(shapes[n].Volume for n in groups[g]))
    for g in order:
        used = {colour[h] for h in colour for n in groups[g] for m in groups[h] if near(n, m)}
        colour[g] = next((c for c in TINTS if c not in used), TINTS[len(colour) % len(TINTS)])
    return {n: colour[pair(n)] for n in names}


def mirror_gaps(rows: dict) -> list[dict]:
    """Where a right piece and its left twin are not alike: the print box and the mass, and with detail the areas."""
    out = []
    for name, r in rows.items():
        if not name.endswith(" R") or name[:-1] + "L" not in rows:
            continue
        left = rows[name[:-1] + "L"]
        for k, tol in (("x", 1.0), ("y", 1.0), ("z", 1.0), ("mass_g", 2.0), ("seen", 1.0), ("overhang_seen", 1.0), ("limit_seen", 1.0), ("terrace_seen", 1.0)):
            if k in r and abs(r[k] - left[k]) > tol:
                out.append({"problem": "mirrored pieces differ", "piece": name[:-2], "value": k, "right": r[k], "left": left[k]})
    return out


def run(out: Path | None = None, mods: Modules | None = None, lim: Printer | None = None,
        log=print, write: bool = True, detail: bool = True, bezel: bool = True) -> dict:
    """Cut and measure the shell and the bezel plate. Writes split/shell/, split/bezel/ and split/measurements.json
    when write is True; without detail it measures only the print boxes and the masses (for the test)."""
    import MeshPart  # noqa: PLC0415

    d = Blueprint()
    lim = lim or printer()
    mods = mods or build_modules(d, log)
    covers = cover_shapes(d)
    result = {"printer": vars(lim), "skin_key": mods.key, "door": door_of(d)}
    root = (out or Path(os.environ.get("CANDYBAR_OUT", "cad/out/shell-rev7"))) / "split"
    for opt in (layout(d),) + ((BEZEL,) if bezel else ()):
        seams, pieces = expanded(opt)
        shapes, problems = cut(seams, pieces, mods)
        rows = {}
        for p in pieces:
            if p.full not in shapes:
                continue
            rows[p.full] = {"module": p.module, **measure(shapes[p.full], p.up, lim, mods.outer[p.module], covers, d, detail, seam_planes(seams, p.module))}
        problems += mirror_gaps(rows)
        res = {"pieces": rows, "problems": problems, "count": len(rows), "fits": all(r["fits"] for r in rows.values()) and not
               [q for q in problems if q["problem"] != "debris"]}
        result[opt.key] = res
        log(f"split: {opt.key}: {len(rows)} pieces, fits {res['fits']}, problems {problems}")
        if write:
            here = root / opt.key
            here.mkdir(parents=True, exist_ok=True)
            colour = tints(shapes)
            manifest = {}
            for name, shape in shapes.items():
                f = name.replace(" ", "_") + ".stl"
                MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.3, AngularDeflection=0.15).write(str(here / f))
                manifest[name] = {"file": f, "finish": colour[name]}
            (here / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
            lines_ = seam_lines(seams, mods, covers)
            (here / "seams.json").write_text(json.dumps(lines_), encoding="utf-8")
            res["seams"] = {k: {kk: vv for kk, vv in v.items() if kk != "lines"} for k, v in lines_.items()}
    if write:
        (root / "measurements.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    return result


def main() -> int:
    res = run()
    for k in (SHELL, PLATE):
        v = res[k]
        big = max(v["pieces"].items(), key=lambda kv: max(kv[1]["x"], kv[1]["y"], kv[1]["z"]))
        print(f"{k}: {v['count']} pieces, fits {v['fits']}, largest {big[0]} {big[1]['x']} x {big[1]['y']} x {big[1]['z']}")
    return 0 if all(res[k]["fits"] for k in (SHELL, PLATE)) else 1
