"""The monitor cradle and the printed bezel plate (roadmap step 13; docs/design/monitor-cradle-and-bezel.md).

    CANDYBAR_OUT=cad/out/cradle cad/candybar/freecad-run.sh candybar.shell.cradle
    CANDYBAR_OUT=cad/out/cradle cad/candybar/freecad-run.sh --gui candybar.shell.cradle_view    # shell.FCStd
    cad/.venv-tools/bin/python cad/tools/draw_cradle.py                                        # the sheets

Frame of this module: (x, v, t). x is across the cabinet, v is up the flat screen face from the centre of the image,
t is the depth behind the screen face (solids.screen_frame). The back of the bezel plate is the plane t = mon_setback.

The parts:
  bezel_plate      the plate of solids.bezel, plate_fit smaller all round, with the edge break on its edges that show,
                   four radial slots for the locating pins and four magnet pockets in its back. It prints as two
                   halves (bezel_half_right, bezel_half_left) that stand on their outer side face.
  lugs             four added solids on the body: each widens a ledge of the opening by 11 and makes it 6 thick. A lug
                   holds one screw of an upright, one locating pin and one magnet.
  upright          two bars behind the monitor, from the bottom lugs to the top lugs. Each has a slot at each end.
  jaw              four sliders on the uprights: a wall with a pad on the edge of the monitor, a rest behind it, and a
                   land for the lock screw outside the monitor. The depth of the rest is for one monitor (Unit).
  shoe             the nut carrier behind the slot of an upright, one for each jaw.
  channel          a cable channel on the inner face of each side, on two bosses (added solids on the body).
The hardware (monitor, plugs, pads, pins, magnets, screws) is built for the checks and the pictures only.

The shell comes from a built folder (CANDYBAR_SHELL, default cad/out/shell-rev7: the BREP of each part and
fit/report.json with the anchors of the hardware) and the skin from the cache of the split. This module does not
change the outer form: the lugs and the bosses are added solids, and it needs no opening in the shell.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import FreeCAD as App
import MeshPart
import Part

from . import split
from .dims import MON_ACTIVE_H, MON_ACTIVE_W, Blueprint

V = App.Vector
CAD = Path(__file__).resolve().parents[2]
G = 9.81
ABS_DENSITY = 1.05e-6       # kg/mm3 (decision record 0008)
OVERHANG_LIMIT = 45.0
MESH_LINEAR, MESH_ANGULAR = 0.05, 0.05
TOL_VOLUME = 0.01           # mm3: two solids clash when they share more


@dataclass(frozen=True)
class Unit:
    """A monitor: its body, where the image lies in it, and its mass."""
    name: str
    w: float
    h: float
    t: float
    bezel_bottom: float     # the bottom edge of the body up to the first lit row
    mass: float             # kg


# the present unit (hardware-envelopes.md 1) and the body that the cabinet must take (the survey: the widest, the
# tallest and the thickest of five units, centred on the image; its mass is an assumption)
# the present unit's housing: width and height are the maker's 354 x 230 until the owner measures them; its
# thickness is MEASURED by the owner with a caliper, 10.45 to 10.6 all round (2026-11-14; the maker gives 10): the
# model uses 10.6, so that each part clears the thickest; its bottom bezel, 8.9 from the bottom edge of the housing
# to the lit picture, is MEASURED by the owner (2026-11-14; the estimate was 9.6)
PRESENT = Unit("UPERFECT BE16CU", 354.0, 230.0, 10.6, 8.9, 0.82)
PRESENT_T_MIN = 10.45
GENERIC = Unit("any 16 inch 16:10 unit", 360.0, 247.1, 20.6, (247.1 - MON_ACTIVE_H) / 2, 1.5)


@dataclass(frozen=True)
class Cradle:
    """The values of the cradle, the lugs, the channel and the mount of the bezel plate."""
    # the glass of the monitor stands this far behind the back of the bezel plate, so that the plate does not press
    # on the glass and a fingernail or a card goes behind the rim of the window
    glass_gap: float = 1.0
    adjust: float = 8.0             # movement of the monitor each way, across and along the face
    side_clear: float = 22.0        # a right-angle plug and its cable bend beside each side edge
    # pads: cellular rubber on the wall of each jaw, felt on the rest behind the monitor
    pad_edge: float = 2.0
    pad_back: float = 1.0
    pad_squeeze: float = 0.5        # how far the top jaws press the edge pads together
    pad_stiffness: float = 0.04     # MPa at that squeeze (cellular EPDM, an estimate)
    # uprights: centre from the centre line, width, depth, and the smallest rest behind the thickest monitor
    bar_x: float = 84.0
    bar_w: float = 24.0
    bar_t: float = 12.0
    rest_min: float = 4.0
    bar_half: float = 150.6         # half its length; its ends lie behind the ledges
    slot_w: float = 4.5
    slot_v0: float = 117.5          # the slot of each end, from the centre of the image
    slot_v1: float = 146.5
    ear_w: float = 12.0             # the post at each end that reaches forward to the lug, inboard of the bar
    ear_len: float = 14.5
    ear_gap: float = 0.2            # between the ear and the back of the lug
    insert_d: float = 5.6           # heat-set insert M4
    insert_depth: float = 8.0
    # jaws
    jaw_w: float = 23.0
    jaw_wall: float = 4.0
    jaw_land: float = 10.0
    jaw_land_t: float = 6.0
    jaw_rest: float = 16.0          # how far the rest reaches under the monitor
    jaw_front_gap: float = 0.5      # the wall ends this far behind the glass
    screw_hole: float = 4.5            # clearance hole M4
    shoe: tuple[float, float, float] = (22.0, 14.0, 6.0)    # across (from its inner side to the bar's outer face), along, deep
    shoe_lip: tuple[float, float] = (3.0, 4.0)              # the lip beside the bar that stops it turning: thick, high
    nut_af: float = 7.0
    nut_h: float = 3.2
    # lugs: from x0 to x1 each side, reach into the opening, thickness; screw, pin and magnet across
    lug_x0: float = 30.0
    lug_x1: float = 72.0
    lug_reach: float = 11.1
    lug_t: float = 6.0
    lug_v: float = 143.0            # the row of the screw, the pin and the magnet, from the centre of the image
    lug_slot: float = 1.25          # the screw hole is a slot, this far each way along the face
    head_d: float = 8.2             # counterbore for an M4 button head (ISO 7380)
    head_h: float = 2.4
    pin_x: float = 50.0
    dowel_d: float = 4.0
    pin_len: float = 12.0
    pin_hole: float = 3.9           # press fit in the lug
    pin_slot_w: float = 4.3         # the slot in the plate
    pin_slot_play: float = 2.0      # each way along the radius
    pin_slot_depth: float = 6.5
    magnet_x: float = 38.0
    magnet_d: float = 8.0
    magnet_h: float = 3.0
    magnet_pocket_d: float = 8.2
    magnet_pocket_h: float = 3.1
    magnet_pull: float = 5.0        # N for each pair at the working gap (an estimate for 8 x 3 N35 discs)
    # the printed plate: smaller than the recess by this much on each side and at each end; edge break
    plate_fit: float = 0.5
    seam_dowel_d: float = 4.1
    seam_dowel_depth: float = 8.0
    # cable channel: on the inner face of the side (side_wall_x; the check measures it), from v0 to v1
    side_wall_x: float = 243.0
    channel_v0: float = -112.0
    channel_v1: float = -12.0
    channel_t0: float = 22.0
    channel_in: tuple[float, float] = (21.0, 22.0)      # clear width across, clear depth
    channel_wall: float = 3.0
    channel_slot: float = 9.0
    boss_h: float = 5.0
    boss_d: float = 10.0
    boss_in: float = 1.0            # into the skin, so that the boss and the stepped skin are one solid
    boss_insert_d: float = 4.0      # heat-set insert M3
    boss_v: tuple[float, float] = (-95.0, -29.0)
    # lead clamp: pairs of slots for a cable tie through the front arm of each channel, at these places along the face.
    # A tie holds the leads on the channel, so that a plug does not carry the weight of its lead
    tie_v: tuple[float, ...] = (-88.0, -70.0, -50.0, -30.0)
    tie_slot: tuple[float, float] = (4.0, 2.5)          # across, along the face
    tie_x: tuple[float, float] = (3.5, 10.5)            # the two slots, from the inner face of the lip
    clamp_reach: float = 50.0                           # a clamp must be this near to the mini-HDMI plug
    # the sockets and the button of the present unit, above its bottom edge (hardware-envelopes.md 1; estimates)
    hdmi_up: float = 49.0                               # mini-HDMI, left edge
    usb_power_up: float = 86.0                          # the upper USB-C socket, left edge: power
    audio_up: float = 30.0                              # 3.5 mm output, right edge
    button_up: float = 63.5                             # power button, right edge: MEASURED by the owner (2026-11-14)
    button_proud: float = 1.5
    # the option for the power button: a square push rod through the inner frame of the plate, and a striker that
    # the rod's slope of 45 degrees moves across onto the button. The monitor starts by itself when its USB-C socket
    # gets power (the owner's test, 2026-11-14); the rod stays as a fallback. push_rod puts it in the document in
    # place of the plain plate; it is off until the owner has seen its mark on the face of the plate
    push_rod: bool = False
    rod: float = 4.0                                    # the rod is square
    rod_fit: float = 0.2                                # clearance on each side of the rod and of the striker
    rod_x: float = 192.5
    rod_proud: float = 1.5
    striker: float = 6.0
    striker_gap: float = 1.0                            # from its nose to the button
    guide_wall: float = 2.5
    # the stop of the option, so that the rod and the striker stay in their places when the plate is off: a collar on
    # the rod behind the plate (it rests on the back of the plate and travels in a pocket of the guide), and a lip
    # across the upper half of the open end of the guide, on which a step of the striker stops
    rod_collar: float = 1.5                             # each side of the rod
    collar_t: float = 1.0
    stop_lip: float = 1.0                               # along x
    # loads
    lock_torque: float = 0.4        # N m on an M4 lock screw
    lock_keep: float = 0.4          # share of the preload that is left after the plastic relaxes (an estimate for PETG; kept for ABS)
    friction: float = 0.25          # plastic on plastic (an estimate for PETG; kept for ABS)
    pad_friction: float = 0.6       # cellular rubber on the monitor's edge
    shock: float = 3.0              # g, when the owner puts the cabinet down
    shrink: tuple[float, float] = (0.0059, 0.0069)      # printed ABS, measured short in X and Y (abs-on-the-q2.md, one study)


class Frame:
    """The screen frame with its origin at the centre of the image."""

    def __init__(self, d: Blueprint):
        from . import solids as so  # noqa: PLC0415
        o, self.up, self.into = so.screen_frame(d)
        self.c = o + self.up * d.image_s
        self.t0 = d.mon_setback
        self.half_w = d.bezel_w / 2
        self.half_len = d.bezel_len / 2

    def pt(self, x: float, v: float, t: float) -> App.Vector:
        return self.c + V(x, 0, 0) + self.up * v + self.into * t

    def local(self, p: App.Vector) -> tuple[float, float, float]:
        q = p - self.c
        return q.x, q.dot(self.up), q.dot(self.into)

    def box(self, x: tuple[float, float], v: tuple[float, float], t: tuple[float, float]) -> Part.Shape:
        from . import solids as so  # noqa: PLC0415
        return so.slab(self.c, self.up, self.into, x, v, t)

    def prism_vt(self, pts: list[tuple[float, float]], x: tuple[float, float]) -> Part.Shape:
        """A polygon in (v, t) carried from x[0] to x[1]."""
        at = [self.pt(x[0], v, t) for v, t in pts]
        return Part.Face(Part.makePolygon(at + at[:1])).extrude(V(x[1] - x[0], 0, 0))

    def prism_xt(self, pts: list[tuple[float, float]], v: tuple[float, float]) -> Part.Shape:
        """A polygon in (x, t) carried from v[0] to v[1]."""
        at = [self.pt(x, v[0], t) for x, t in pts]
        return Part.Face(Part.makePolygon(at + at[:1])).extrude(self.up * (v[1] - v[0]))

    def cyl(self, x: float, v: float, t: tuple[float, float], dia: float) -> Part.Shape:
        return Part.makeCylinder(dia / 2, t[1] - t[0], self.pt(x, v, t[0]), self.into)

    def cyl_x(self, x: tuple[float, float], v: float, t: float, dia: float) -> Part.Shape:
        return Part.makeCylinder(dia / 2, x[1] - x[0], self.pt(x[0], v, t), V(1, 0, 0))

    def obround(self, x: float, v: tuple[float, float], t: tuple[float, float], dia: float) -> Part.Shape:
        """A slot along v with round ends."""
        r = dia / 2
        return self.box((x - r, x + r), v, t).fuse([self.cyl(x, v[0], t, dia), self.cyl(x, v[1], t, dia)]).removeSplitter()


def mirror_x(s: Part.Shape) -> Part.Shape:
    return s.mirror(V(0, 0, 0), V(1, 0, 0))


def one(shape: Part.Shape) -> Part.Shape:
    return shape.Solids[0] if len(shape.Solids) == 1 else shape


# ---------- where the monitor lies ----------

def edges_v(u: Unit, shift: float = 0.0) -> tuple[float, float]:
    """The bottom and the top edge of a unit along the face, from the centre of the image."""
    lo = -MON_ACTIVE_H / 2 - u.bezel_bottom + shift
    return lo, lo + u.h


def glass_t(d: Blueprint, c: Cradle) -> float:
    return d.mon_setback + c.glass_gap


def bed_t(d: Blueprint, c: Cradle) -> float:
    """The front face of the uprights: behind the thickest monitor, its felt and the smallest rest."""
    return glass_t(d, c) + GENERIC.t + c.pad_back + c.rest_min


def monitor(d: Blueprint, c: Cradle, u: Unit, out: float = 0.0, dx: float = 0.0, dv: float = 0.0) -> Part.Shape:
    f = Frame(d)
    lo, hi = edges_v(u, dv)
    g = glass_t(d, c) - out
    return f.box((dx - u.w / 2, dx + u.w / 2), (lo, hi), (g, g + u.t))


def plugs(d: Blueprint, c: Cradle, u: Unit, out: float = 0.0) -> Part.Shape:
    """The room of a right-angle plug and its cable bend on each side edge, over the height of the unit."""
    f = Frame(d)
    lo, hi = edges_v(u)
    g = glass_t(d, c) - out
    return Part.makeCompound([f.box((sx * u.w / 2, sx * (u.w / 2 + c.side_clear)), (lo, hi), (g, g + u.t)) for sx in (1, -1)])


def swept(d: Blueprint, c: Cradle, out: float = 0.0) -> Part.Shape:
    """Any 16:10 body with its adjustment each way, and its plug room on both sides: what must pass the opening."""
    f = Frame(d)
    a, u = c.adjust, GENERIC
    g = glass_t(d, c) - out
    return f.box((-u.w / 2 - a - c.side_clear, u.w / 2 + a + c.side_clear), (-u.h / 2 - a, u.h / 2 + a), (g, g + u.t))


# ---------- the bezel plate ----------

def fit_box(d: Blueprint, fit: float) -> Part.Shape:
    """The recess of the plate (solids.bezel_box), fit smaller on each side and at each end."""
    from . import profiles as pr  # noqa: PLC0415
    from . import solids as so  # noqa: PLC0415
    fr = pr.front(d)
    up, into = so.chord_frame(fr)
    ends = [V(0, *d.face(s)).dot(up) for s in (d.bezel_s0, d.bezel_s1)]
    bw = d.bezel_w / 2 - fit
    return so.slab(V(0, 0, 0), up, into, (-bw, bw), (ends[0] + fit, ends[1] - fit), (-so.BIG / 4, so.BIG / 4))


def plate_break_edges(shape: Part.Shape, d: Blueprint) -> list[Part.Edge]:
    """The convex edges of the plate that show and turn more than edge_break_turn: the four edges between the inner
    frame and the rim wall, the four edges round the land, and the four corners of the outline. The edges of the
    flat back do not show: the back lies on the ledges and in front of the monitor."""
    from . import solids as so  # noqa: PLC0415
    f = Frame(d)
    out = []
    for e in shape.Edges:
        if e.Degenerated or len(shape.ancestorsOfType(e, Part.Face)) != 2:
            continue
        if all(abs(f.local(e.valueAt(e.FirstParameter + (e.LastParameter - e.FirstParameter) * k / 4))[2] - f.t0) < 1e-4 for k in range(5)):
            continue
        convex, turn = so.edge_turn(shape, e)
        if convex and turn > d.edge_break_turn:
            out.append(e)
    return out


def pin_places(c: Cradle) -> list[tuple[float, float]]:
    return [(sx * c.pin_x, sv * c.lug_v) for sv in (-1, 1) for sx in (1, -1)]


def magnet_places(c: Cradle) -> list[tuple[float, float]]:
    return [(sx * c.magnet_x, sv * c.lug_v) for sv in (-1, 1) for sx in (1, -1)]


def pin_slot(d: Blueprint, c: Cradle, x: float, v: float) -> Part.Shape:
    """The slot of one pin in the back of the plate: its long axis points at the centre of the image, so that the
    plate keeps its centre when the plate and the body shrink by different amounts."""
    f = Frame(d)
    r = math.hypot(x, v)
    ux, uv = x / r, v / r
    half, w = c.dowel_d / 2 + c.pin_slot_play, c.pin_slot_w / 2
    corner = lambda a, b: f.pt(x + a * ux - b * uv, v + a * uv + b * ux, f.t0 + 1.0)
    face = Part.Face(Part.makePolygon([corner(-half, -w), corner(half, -w), corner(half, w), corner(-half, w), corner(-half, -w)]))
    return face.extrude(f.into * -(c.pin_slot_depth + 1.0))


def bezel_plate(d: Blueprint, c: Cradle, log: list[str] | None = None, back: bool = True) -> Part.Shape:
    """The printed plate in place: the form of solids.bezel inside fit_box, the edge break, and the features of its
    back (without them when back is False)."""
    from . import profiles as pr  # noqa: PLC0415
    from . import solids as so  # noqa: PLC0415
    log = log if log is not None else []
    f = Frame(d)
    plate = one(so.bezel(d, pr.front(d)).common(fit_box(d, c.plate_fit)).removeSplitter())
    # three steps. OpenCascade does not make the round on the four edges of the window in one call (they meet at the
    # corners of the window, where the rim walls meet in a concave corner): the top and the bottom edge first, then
    # the two side edges, which then end on the rounds of the first two
    rim = lambda s: [e for e in plate_break_edges(s, d) if abs(f.local(so.middle(e))[2] - (f.t0 - d.bezel_rim)) < 0.9 and e.Length > 50.0]
    steps = (("round the land and at the corners of the outline", lambda s: [e for e in plate_break_edges(s, d) if not any(e.isSame(r) for r in rim(s))]),
             ("the top and the bottom edge of the window", lambda s: [e for e in rim(s) if abs(f.local(so.middle(e))[0]) < 1.0]),
             ("the side edges of the window", rim))
    for what, pick in steps:
        es = pick(plate)
        log.append(f"bezel plate, edge break R {d.edge_break:g}, {what}: {len(es)} edges, {sum(e.Length for e in es):.0f} mm")
        plate = so.break_edges(plate, es, d.edge_break, log, "bezel plate")
    left = plate_break_edges(plate, d)
    log += [f"bezel plate: the edge at {tuple(round(v, 1) for v in so.middle(e))}, {e.Length:.1f} long, is still sharp" for e in left]
    if not back:
        return one(plate)
    cut = [pin_slot(d, c, x, v) for x, v in pin_places(c)]
    cut += [f.cyl(x, v, (f.t0 - c.magnet_pocket_h, f.t0 + 1.0), c.magnet_pocket_d) for x, v in magnet_places(c)]
    return one(plate.cut(cut))


def seam_dowels(d: Blueprint, c: Cradle) -> list[tuple[float, float]]:
    """(v, t) of the dowels in each cut face of the halves: two in the bottom bar and two in the top bar."""
    f = Frame(d)
    end = f.half_len - c.plate_fit
    return [(s * v, t) for s in (-1, 1) for v, t in ((end - 9.0, f.t0 - 5.0), (end - 32.0, f.t0 - 3.5))]


def bezel_halves(d: Blueprint, c: Cradle, plate: Part.Shape) -> dict[str, Part.Shape]:
    """The plate cut on the centre line, with the dowel holes of the seam in each cut face."""
    from . import solids as so  # noqa: PLC0415
    f = Frame(d)
    holes = [f.cyl_x((-c.seam_dowel_depth, c.seam_dowel_depth), v, t, c.seam_dowel_d) for v, t in seam_dowels(d, c)]
    cut = plate.cut(holes)
    return {"bezel_half_right": one(cut.common(so.halfspace(V(0, 0, 0), V(1, 0, 0)))),
            "bezel_half_left": one(cut.common(so.halfspace(V(0, 0, 0), V(-1, 0, 0))))}


def bezel_bars(d: Blueprint, plate: Part.Shape) -> dict[str, Part.Shape]:
    """The other printed way, for the comparison: four bars with mitres at the corners of the window, and the top
    and the bottom bar cut on the centre line because they are longer than the bed: six pieces."""
    from . import solids as so  # noqa: PLC0415
    f = Frame(d)
    wx, wv = MON_ACTIVE_W / 2, MON_ACTIVE_H / 2
    out = {}
    for name, sx, sv in (("right", 1, 0), ("left", -1, 0), ("top", 0, 1), ("bottom", 0, -1)):
        piece = plate
        for cx, cv in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            if sx and cx != sx or sv and cv != sv:
                continue
            # the mitre plane through the corner of the window, at 45 degrees
            n = V(cx, 0, 0) - f.up * cv if sx else f.up * cv - V(cx, 0, 0)
            piece = piece.common(so.halfspace(f.pt(cx * wx, cv * wv, 0), n))
        piece = piece.common(so.halfspace(f.pt(0, 0, 0), V(sx, 0, 0) if sx else f.up * sv))
        if sx:
            out[f"bar_{name}"] = one(piece)
        else:
            for side, n in (("right", V(1, 0, 0)), ("left", V(-1, 0, 0))):
                out[f"bar_{name}_{side}"] = one(piece.common(so.halfspace(V(0, 0, 0), n)))
    return out


# ---------- the lugs on the body ----------

def lug(d: Blueprint, c: Cradle, sx: int, sv: int) -> Part.Shape:
    """One lug: a ledge of the opening made lug_reach wider and lug_t thick, from lug_x0 to lug_x1. Its back ends in
    a slope of 45 degrees behind the ledge, so that it prints with the piece that carries it. It has the slot and
    the counterbore of the upright's screw, the hole of the locating pin and the pocket of the magnet."""
    f = Frame(d)
    t0, t1 = f.t0, f.t0 + c.lug_t
    edge = f.half_len - 6.0 - c.lug_reach           # the free edge, in the opening
    wall = f.half_len + d.wall_t                    # the far side of the wall at the end of the recess
    step = t1 - (f.t0 + d.wall_t)
    profile = [(edge, t0), (edge, t1), (wall - step, t1), (wall, t1 - step), (wall, t0)]
    solid = f.prism_vt([(sv * v, t) for v, t in profile], (sx * c.lug_x0, sx * c.lug_x1))
    x = sx * (c.bar_x - c.bar_w / 2 - c.ear_w / 2)
    v = sv * c.lug_v
    cut = [f.obround(x, (v - c.lug_slot, v + c.lug_slot), (t0 - 1.0, t1 + 1.0), c.screw_hole),
           f.obround(x, (v - c.lug_slot, v + c.lug_slot), (t0 - 1.0, t0 + c.head_h), c.head_d),
           f.cyl(sx * c.pin_x, v, (t0 - 1.0, t1 + 1.0), c.pin_hole),
           f.cyl(sx * c.magnet_x, v, (t0 - 1.0, t0 + c.magnet_pocket_h), c.magnet_pocket_d)]
    return one(solid.cut(cut))


def lugs(d: Blueprint, c: Cradle) -> Part.Shape:
    return Part.makeCompound([lug(d, c, sx, sv) for sv in (-1, 1) for sx in (1, -1)])


# ---------- the uprights, the jaws and the shoes ----------

def upright(d: Blueprint, c: Cradle, sx: int) -> Part.Shape:
    """One upright: a bar behind the monitor with a slot through each end for the lock screws of the jaws, and at
    each end an ear that reaches forward to the back of the lug and holds a heat-set insert."""
    f = Frame(d)
    b0 = bed_t(d, c)
    b1 = b0 + c.bar_t
    x0, x1 = c.bar_x - c.bar_w / 2, c.bar_x + c.bar_w / 2
    bar = f.box((x0, x1), (-c.bar_half, c.bar_half), (b0, b1))
    e0 = f.t0 + c.lug_t + c.ear_gap
    ears = [f.box((x0 - c.ear_w, x0), (min(sv * c.bar_half, sv * (c.bar_half - c.ear_len)), max(sv * c.bar_half, sv * (c.bar_half - c.ear_len))), (e0, b1))
            for sv in (-1, 1)]
    solid = bar.fuse(ears).removeSplitter()
    xe = x0 - c.ear_w / 2
    cut = [f.box((c.bar_x - c.slot_w / 2, c.bar_x + c.slot_w / 2), (min(sv * c.slot_v0, sv * c.slot_v1), max(sv * c.slot_v0, sv * c.slot_v1)), (b0 - 1.0, b1 + 1.0))
           for sv in (-1, 1)]
    cut += [f.cyl(xe, sv * c.lug_v, (e0 - 1.0, e0 + c.insert_depth), c.insert_d) for sv in (-1, 1)]
    solid = one(solid.cut(cut))
    return solid if sx > 0 else one(mirror_x(solid))


def jaw_edge(u: Unit, sv: int) -> float:
    lo, hi = edges_v(u)
    return lo if sv < 0 else hi


def jaw(d: Blueprint, c: Cradle, u: Unit, sx: int, sv: int, dv: float = 0.0) -> Part.Shape:
    """One jaw for the unit u, on the upright of side sx, at the bottom (sv -1) or the top (sv +1) edge. Its profile
    in (distance outside the edge, depth): the rest behind the monitor, the wall beside its edge, and the land of
    the lock screw. One extrusion across its width, with one hole."""
    f = Frame(d)
    g, b = glass_t(d, c), bed_t(d, c)
    rest = g + u.t + c.pad_back
    w0, w1 = c.pad_edge, c.pad_edge + c.jaw_wall
    end = w1 + c.jaw_land
    profile = [(-c.jaw_rest, rest), (w0, rest), (w0, g + c.jaw_front_gap), (w1, g + c.jaw_front_gap), (w1, b - c.jaw_land_t),
               (end, b - c.jaw_land_t), (end, b), (-c.jaw_rest, b)]
    edge = jaw_edge(u, sv) + dv
    solid = f.prism_vt([(edge + sv * o, t) for o, t in profile], (sx * c.bar_x - c.jaw_w / 2, sx * c.bar_x + c.jaw_w / 2))
    hole = f.cyl(sx * c.bar_x, screw_v(c, u, sv, dv), (b - c.jaw_land_t - 1.0, b + 1.0), c.screw_hole)
    return one(solid.cut(hole))


def screw_v(c: Cradle, u: Unit, sv: int, dv: float = 0.0) -> float:
    """Where the lock screw of a jaw is along the face: in the middle of its land."""
    return jaw_edge(u, sv) + dv + sv * (c.pad_edge + c.jaw_wall + c.jaw_land / 2)


def shoe(d: Blueprint, c: Cradle, u: Unit, sx: int, sv: int) -> Part.Shape:
    """The nut carrier behind the upright: a block with a pocket for an M4 hexagon nut, and a lip along the outer
    face of the bar that stops it turning with the screw."""
    f = Frame(d)
    b1 = bed_t(d, c) + c.bar_t
    w, ln, h = c.shoe
    lip_w, lip_h = c.shoe_lip
    v = screw_v(c, u, sv)
    x0, xo = c.bar_x + c.bar_w / 2 - w, c.bar_x + c.bar_w / 2 + 0.2
    solid = f.prism_xt([(x0, b1), (xo, b1), (xo, b1 - lip_h), (xo + lip_w, b1 - lip_h), (xo + lip_w, b1 + h), (x0, b1 + h)], (v - ln / 2, v + ln / 2))
    r = c.nut_af / math.sqrt(3)
    hexagon = Part.Face(Part.makePolygon([f.pt(c.bar_x + r * math.cos(math.radians(60 * k)), v + r * math.sin(math.radians(60 * k)), b1 + h - c.nut_h) for k in range(7)]))
    solid = one(solid.cut([f.cyl(c.bar_x, v, (b1 - 1.0, b1 + h + 1.0), c.screw_hole), hexagon.extrude(f.into * (c.nut_h + 1.0))]))
    return solid if sx > 0 else one(mirror_x(solid))


def pads(d: Blueprint, c: Cradle, u: Unit) -> Part.Shape:
    f = Frame(d)
    g = glass_t(d, c)
    out = []
    for sv in (-1, 1):
        e = jaw_edge(u, sv)
        for sx in (1, -1):
            x = (sx * c.bar_x - c.jaw_w / 2, sx * c.bar_x + c.jaw_w / 2)
            out.append(f.box(x, tuple(sorted((e, e + sv * c.pad_edge))), (g + c.jaw_front_gap, g + u.t)))
            out.append(f.box(x, tuple(sorted((e - sv * c.jaw_rest, e))), (g + u.t, g + u.t + c.pad_back)))
    return Part.makeCompound(out)


# ---------- the cable channel and its bosses ----------

def channel(d: Blueprint, c: Cradle, sx: int) -> Part.Shape:
    """One cable channel: a C section along the face on the inner face of the side, open toward the monitor's edge
    through a slot. It holds a video lead and a power lead and the slack that the monitor needs to come out."""
    f = Frame(d)
    w = c.channel_wall
    cx, ct = c.channel_in
    xb = c.side_wall_x - c.boss_h          # the back of the channel, on the bosses
    t0 = c.channel_t0
    lip = (ct - c.channel_slot) / 2
    xi = xb - w - cx
    pts = [(xb, t0), (xb, t0 + ct + 2 * w), (xi - w, t0 + ct + 2 * w), (xi - w, t0 + w + ct - lip), (xi, t0 + w + ct - lip), (xi, t0 + w + ct),
           (xb - w, t0 + w + ct), (xb - w, t0 + w), (xi, t0 + w), (xi, t0 + w + lip), (xi - w, t0 + w + lip), (xi - w, t0)]
    solid = f.prism_xt(pts, (c.channel_v0, c.channel_v1))
    tm = t0 + w + ct / 2
    holes = [f.cyl_x((xb - w - 1.0, xb + 1.0), v, tm, 3.4) for v in c.boss_v]
    sx_, sv_ = c.tie_slot
    holes += [f.box((xi + a - sx_ / 2, xi + a + sx_ / 2), (v - sv_ / 2, v + sv_ / 2), (t0 - 1.0, t0 + w + 1.0)) for v in c.tie_v for a in c.tie_x]
    solid = one(solid.cut(holes))
    return solid if sx > 0 else one(mirror_x(solid))


def bosses(d: Blueprint, c: Cradle) -> Part.Shape:
    """The bosses of the cable channels on the inner face of each side: added solids on the body."""
    f = Frame(d)
    tm = c.channel_t0 + c.channel_wall + c.channel_in[1] / 2
    out = []
    for v in c.boss_v:
        b = f.cyl_x((c.side_wall_x - c.boss_h, c.side_wall_x + c.boss_in), v, tm, c.boss_d).cut(
            f.cyl_x((c.side_wall_x - c.boss_h - 1.0, c.side_wall_x - 0.5), v, tm, c.boss_insert_d))
        out += [one(b), one(mirror_x(b))]
    return Part.makeCompound(out)


# ---------- the leads and the power button of the present unit ----------

def sockets(d: Blueprint, c: Cradle, u: Unit) -> dict[str, tuple[float, float]]:
    """(x, v) of each socket and of the power button of the present unit, on its side edges."""
    lo, _ = edges_v(u)
    return {"mini-HDMI": (-u.w / 2, lo + c.hdmi_up), "USB-C power": (-u.w / 2, lo + c.usb_power_up),
            "3.5 mm audio": (u.w / 2, lo + c.audio_up), "power button": (u.w / 2, lo + c.button_up)}


def clamp_rows(d: Blueprint, c: Cradle, u: Unit) -> list[dict]:
    """How far each socket is from the nearest lead clamp of the channel on its side (the middle of a tie)."""
    xi = c.side_wall_x - c.boss_h - c.channel_wall - c.channel_in[0]
    tie_x = xi + sum(c.tie_x) / 2
    rows = []
    for name, (x, v) in sockets(d, c, u).items():
        if name == "power button":
            continue
        near = min(c.tie_v, key=lambda t: abs(t - v))
        rows.append({"lead": name, "side": "left" if x < 0 else "right", "socket_v": round(v, 1), "clamp_v": near,
                     "distance": round(math.hypot(tie_x - abs(x), near - v), 1), "limit": c.clamp_reach})
    return rows


def button_option(d: Blueprint, c: Cradle, u: Unit, plate: Part.Shape) -> dict[str, Part.Shape]:
    """The option for the power button on the right edge: the plate with a square hole in its inner frame, a push
    rod in the hole, a striker that the rod moves across onto the button, and the guide of the striker on the back
    of the plate. The three parts leave with the plate. A collar on the rod and a lip of the guide keep the rod and
    the striker in their places when the plate is off."""
    f = Frame(d)
    x_btn, v = sockets(d, c, u)["power button"]
    tb = glass_t(d, c) + u.t / 2                       # the button is in the middle of the edge
    r, s, fit = c.rod / 2, c.striker / 2, c.rod_fit
    # where the rod leaves the face of the plate
    line = Part.makeLine(f.pt(c.rod_x, v, -40.0), f.pt(c.rod_x, v, f.t0)).common(plate)
    front = min(f.local(p.Point)[2] for e in line.Edges for p in e.Vertexes)
    nose = x_btn + c.button_proud + c.striker_gap
    # the slope: the line t = x - k in (x, t), through the lower inner corner of the rod at the top of the striker
    k = (c.rod_x - r) - (tb - s + 1.0)
    rod = f.prism_xt([(c.rod_x - r, front - c.rod_proud), (c.rod_x + r, front - c.rod_proud), (c.rod_x + r, c.rod_x + r - k), (c.rod_x - r, c.rod_x - r - k)], (v - r, v + r))
    top = tb - s
    striker = f.prism_xt([(nose, top), (top + k - fit, top), (tb + s + k - fit, tb + s), (nose, tb + s)], (v - s, v + s))
    g0, g1 = nose + 1.0, c.rod_x + r + c.guide_wall + 2.0
    travel = c.striker_gap + 1.0
    # the stop: the collar of the rod rests on the back of the plate; the step of the striker is travel (and the fit)
    # from the lip at the open end of the guide
    cw = r + c.rod_collar
    rod = rod.fuse(f.box((c.rod_x - cw, c.rod_x + cw), (v - cw, v + cw), (f.t0, f.t0 + c.collar_t))).removeSplitter()
    step = g0 + c.stop_lip + travel + fit
    striker = striker.cut(f.box((nose - 1.0, step), (v - s - 1.0, v + s + 1.0), (tb - fit, tb + s + 1.0)))
    guide = f.box((g0, g1), (v - s - fit - c.guide_wall, v + s + fit + c.guide_wall), (f.t0, tb + s + fit + c.guide_wall))
    guide = guide.cut([f.box((g0 - 1.0, g1 - c.guide_wall), (v - s - fit, v + s + fit), (top - fit, tb + s + fit)),
                       f.box((c.rod_x - r - fit, c.rod_x + r + fit), (v - r - fit, v + r + fit), (f.t0 - 1.0, top)),
                       f.box((c.rod_x - cw - fit, c.rod_x + cw + fit), (v - cw - fit, v + cw + fit), (f.t0 - 1.0, f.t0 + c.collar_t + travel + fit)),
                       # the tip of the rod goes on past the striker by the travel: a pocket in the back wall of the guide
                       f.box((c.rod_x - r - fit, c.rod_x + r + fit), (v - r - fit, v + r + fit), (top, c.rod_x + r - k + travel + fit))])
    guide = guide.fuse(f.box((g0, g0 + c.stop_lip), (v - s - fit, v + s + fit), (tb, tb + s + fit))).removeSplitter()
    hole = f.box((c.rod_x - r - fit, c.rod_x + r + fit), (v - r - fit, v + r + fit), (-40.0, f.t0 + 1.0))
    return {"bezel_plate_button": one(plate.cut(hole)), "button_rod": one(rod), "button_striker": one(striker), "button_guide": one(guide)}


def button_rows(d: Blueprint, c: Cradle, u: Unit, option: dict[str, Part.Shape], parts: dict[str, Part.Shape], skin: Part.Shape) -> dict:
    """The option against what is near it, and the gap from the striker to the button."""
    f = Frame(d)
    x_btn, v = sockets(d, c, u)["power button"]
    tb = glass_t(d, c) + u.t / 2
    button = f.box((x_btn, x_btn + c.button_proud), (v - 2.0, v + 2.0), (tb - 2.0, tb + 2.0))
    others = {"monitor": parts["monitor"], "jaws": parts["jaws"], "skin": skin, "channel_right": parts["channel_right"], "lugs": parts["lugs"],
              "pins": parts["pins"], "magnets": parts["magnets"]}
    rows = {"valid": all(s.isValid() and len(s.Solids) == 1 for s in option.values()),
            "striker to the button": round(gap(option["button_striker"], button), 2),
            "rod stands out of the face": c.rod_proud, "travel of the rod and of the striker": c.striker_gap + 1.0, "clashes": {}}
    names = list(option)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if {a, b} == {"bezel_plate_button", "button_guide"}:
                continue                                # the guide is bonded to the back of the plate
            rows["clashes"][f"{a} / {b}"] = round(volume_in(option[a], option[b]), 3)
        for b, shape in others.items():
            rows["clashes"][f"{a} / {b}"] = round(volume_in(option[a], shape), 3)
    rows["guide on the plate, gap"] = round(gap(option["button_guide"], option["bezel_plate_button"]), 3)
    rows["guide to the monitor"] = round(gap(option["button_guide"], parts["monitor"]), 2)
    return rows


# ---------- the hardware, for the pictures and the checks ----------

def fasteners(d: Blueprint, c: Cradle, u: Unit) -> dict[str, Part.Shape]:
    f = Frame(d)
    b = bed_t(d, c)
    pins = [f.cyl(x, v, (f.t0 - (c.pin_len - c.lug_t), f.t0 + c.lug_t), c.dowel_d) for x, v in pin_places(c)]
    magnets = [f.cyl(x, v, (f.t0 + dt, f.t0 + dt + c.magnet_h), c.magnet_d) for x, v in magnet_places(c) for dt in (-c.magnet_h, 0.0)]
    screws = []
    for sv in (-1, 1):
        for sx in (1, -1):
            x, v = sx * c.bar_x, screw_v(c, u, sv)
            top = b - c.jaw_land_t
            screws.append(f.cyl(x, v, (top - 2.2, top), 7.6).fuse(f.cyl(x, v, (top, top + 25.0), 4.0)))
            xe = sx * (c.bar_x - c.bar_w / 2 - c.ear_w / 2)
            screws.append(f.cyl(xe, sv * c.lug_v, (f.t0 + 0.2, f.t0 + c.head_h), 7.6).fuse(f.cyl(xe, sv * c.lug_v, (f.t0 + c.head_h, f.t0 + c.head_h + 12.0), 4.0)))
    return {"pins": Part.makeCompound(pins), "magnets": Part.makeCompound(magnets), "screws": Part.makeCompound(screws)}


# ---------- all parts ----------

FINISH = {"bezel_plate": "black", "lugs": "#d8b060", "bosses": "#d8b060", "upright_right": "#5a7fb5", "upright_left": "#5a7fb5",
          "jaws": "#d0703a", "shoes": "#8a5a30", "channel_right": "#6aa06a", "channel_left": "#6aa06a", "monitor": "#3a4250",
          "plugs": "#b08a3a", "pads": "#202020", "pins": "#c0c0c8", "magnets": "#909098", "screws": "#707078", "skin": "white",
          "bezel_half_right": "black", "bezel_half_left": "#303030"}
# the parts that are printed, and the added solids on the body
PRINTED = ("bezel_plate", "upright_right", "upright_left", "jaws", "shoes", "channel_right", "channel_left")
ADDED = ("lugs", "bosses")
HARDWARE = ("monitor", "plugs", "pads", "pins", "magnets", "screws")


def build(d: Blueprint, c: Cradle = Cradle(), u: Unit = PRESENT, log: list[str] | None = None) -> dict[str, Part.Shape]:
    """Every part of this package in place in the cabinet frame, and the hardware."""
    out = {"bezel_plate": bezel_plate(d, c, log), "lugs": lugs(d, c), "bosses": bosses(d, c),
           "upright_right": upright(d, c, 1), "upright_left": upright(d, c, -1),
           "jaws": Part.makeCompound([jaw(d, c, u, sx, sv) for sv in (-1, 1) for sx in (1, -1)]),
           "shoes": Part.makeCompound([shoe(d, c, u, sx, sv) for sv in (-1, 1) for sx in (1, -1)]),
           "channel_right": channel(d, c, 1), "channel_left": channel(d, c, -1),
           "monitor": monitor(d, c, u), "plugs": plugs(d, c, u), "pads": pads(d, c, u)}
    out.update(fasteners(d, c, u))
    return out


# ---------- the shell and the hardware of the fit study ----------

def shell_dir() -> Path:
    return Path(os.environ.get("CANDYBAR_SHELL") or CAD / "out" / "shell-rev7")


def shell_parts(folder: Path | None = None) -> dict[str, Part.Shape]:
    """The parts of a built shell, from the BREP files of its folder."""
    folder = folder or shell_dir()
    out = {}
    for name, entry in json.loads((folder / "manifest.json").read_text(encoding="utf-8")).items():
        out[name] = Part.Shape()
        out[name].read(str(folder / entry["brep"]))
    return out


def skin_near(d: Blueprint) -> Part.Shape:
    """The skin of the body round the screen face, from the cache of the split: all of it between the shelf and the
    hood seam, in front of the compute module."""
    from . import split  # noqa: PLC0415
    f = Frame(d)
    body = Part.Shape()
    body.importBinary(str(split.skin_files(d)["body"]))
    return body.common(f.box((-270.0, 270.0), (-195.0, 195.0), (-40.0, 110.0)))


def fit_items(d: Blueprint, folder: Path | None = None):
    """The hardware of the fit study at its anchors (fit/report.json of the built shell): the document and the items."""
    from . import fit  # noqa: PLC0415
    rep = json.loads(((folder or shell_dir()) / "fit" / "report.json").read_text(encoding="utf-8"))
    doc = fit.build_items(fit.sheet_rows(CAD / "params", {k: float(v) for k, v in rep["anchors"].items()}))
    return doc, fit.items(doc)


# ---------- the checks ----------

def volume_in(a: Part.Shape, b: Part.Shape) -> float:
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    return sum(s.common(b).Volume for s in (a.Solids or [a]))


def gap(a: Part.Shape, b: Part.Shape) -> float:
    return a.distToShape(b)[0]


def solid_rows(parts: dict[str, Part.Shape]) -> dict[str, dict]:
    out = {}
    for k, s in parts.items():
        solids = s.Solids
        out[k] = {"valid": s.isValid(), "solids": len(solids), "closed": all(x.isClosed() for x in solids), "volume_mm3": round(s.Volume, 1),
                  "faces": len(s.Faces), "box": [round(v, 1) for v in (s.BoundBox.XLength, s.BoundBox.YLength, s.BoundBox.ZLength)]}
    return out


def clashes(parts: dict[str, Part.Shape], skin: Part.Shape, found, c: Cradle) -> list[dict]:
    """Every part of this package against the skin, against each other, and against each solid of the fit study
    that is not the monitor's own room: the common volume, and the gap where the rule asks for one."""
    rows = []
    mine = {k: parts[k] for k in PRINTED + ADDED + ("monitor", "plugs")}
    for k, s in mine.items():
        if k in ADDED:
            continue                                   # they are part of the body
        rows.append({"a": k, "b": "skin", "common_mm3": round(volume_in(s, skin), 3), "gap": round(gap(s, skin), 2)})
    names = list(mine)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if {a, b} == {"monitor", "plugs"}:
                continue
            rows.append({"a": a, "b": b, "common_mm3": round(volume_in(mine[a], mine[b]), 3), "gap": round(gap(mine[a], mine[b]), 2)})
    for it in found:
        if it.group in ("MonitorRoom", "Panel", "USB", "Hub", "PSU", "CableBundle") or it.name == "Monitor":
            continue
        for s in it.solids:
            for k in PRINTED + ADDED:
                if k == "bezel_plate":
                    continue
                rows.append({"a": k, "b": s.name, "role": s.role, "common_mm3": round(volume_in(mine[k], s.world), 3), "gap": round(gap(mine[k], s.world), 2)})
    return rows


def attached(parts: dict[str, Part.Shape], skin: Part.Shape) -> dict[str, list[float]]:
    """The volume that each added solid shares with the skin: more than zero means that they are one solid."""
    return {k: [round(volume_in(s, skin), 1) for s in parts[k].Solids] for k in ADDED}


def side_wall(d: Blueprint, c: Cradle, skin: Part.Shape) -> list[dict]:
    """The inner face of the right side where the bosses stand: a ray across from the centre of each boss."""
    f = Frame(d)
    tm = c.channel_t0 + c.channel_wall + c.channel_in[1] / 2
    out = []
    for v in c.boss_v:
        for dt in (-c.boss_d / 2, 0.0, c.boss_d / 2):
            p = f.pt(200.0, v, tm + dt)
            hit = Part.makeLine(p, p + V(80, 0, 0)).common(skin)
            x = min(vv.Point.x for e in hit.Edges for vv in e.Vertexes) if hit.Edges else math.inf
            out.append({"v": v, "t": round(tm + dt, 1), "inner_x": round(x, 2)})
    return out


def room_rows(d: Blueprint, c: Cradle, u: Unit) -> dict:
    """The room of the monitor in the opening, as designed and when the body is printed short by each value of
    shrink. The monitor does not shrink."""
    f = Frame(d)
    half_w, half_len = f.half_w, f.half_len - 6.0
    lo, hi = edges_v(u)
    out = {}
    for name, k in (("as designed", 0.0),) + tuple((f"shrink {s * 100:.2f} %", s) for s in c.shrink):
        w, ln = half_w * (1 - k), half_len * (1 - k)
        out[name] = {
            "opening": [round(2 * w, 2), round(2 * ln, 2)],
            "present unit with plugs, each side": round(w - (u.w / 2 + c.side_clear), 2),
            "any unit with plugs at full adjustment, each side": round(w - (GENERIC.w / 2 + c.adjust + c.side_clear), 2),
            "present unit, bottom and top": [round(lo + ln, 2), round(ln - hi, 2)],
            "any unit at full adjustment, bottom and top": round(ln - (GENERIC.h / 2 + c.adjust), 2),
            "lock screw of a jaw inside the opening, any unit at full adjustment": round(ln - (GENERIC.h / 2 + c.adjust + c.pad_edge + c.jaw_wall + c.jaw_land / 2), 2),
            "radial slot of a pin takes": round(c.pin_slot_play, 2),
            "pin moves along its slot when the plate and the body differ by the spread of the shrink": round(math.hypot(c.pin_x, c.lug_v) * (c.shrink[1] - c.shrink[0]), 2),
            "gap round the plate when they differ by that spread: side, end": [round(c.plate_fit - half_w * (c.shrink[1] - c.shrink[0]), 2),
                                                                             round(c.plate_fit - f.half_len * (c.shrink[1] - c.shrink[0]), 2)],
        }
    return out


def path_out(d: Blueprint, c: Cradle, u: Unit, fixed: list[Part.Shape], jaws: Part.Shape, steps: tuple[float, ...]) -> list[dict]:
    """The monitor on its way out, square to the screen face, with the bezel plate off and the top jaws pushed up:
    the present unit with its plugs against everything that stays in the body and its own bottom jaws, and any unit
    with its plug room against everything that stays (its jaws stand where its edges are)."""
    rows = []
    for out in steps:
        for name, shape, stays in (("present unit with plugs", Part.makeCompound([monitor(d, c, u, out), plugs(d, c, u, out)]), fixed + [jaws]),
                                   ("any unit with plugs, at full adjustment", swept(d, c, out), fixed)):
            rows.append({"out_mm": out, "what": name, "common_mm3": round(sum(volume_in(shape, s) for s in stays), 3),
                         "gap": round(min(gap(shape, s) for s in stays), 2)})
    return rows


def sweep_out(d: Blueprint, c: Cradle, reach: float, fixed: list[Part.Shape]) -> dict:
    """Everything any unit passes through on its way out by `reach`: one prism. Its common volume with what stays."""
    f = Frame(d)
    a, u = c.adjust, GENERIC
    g = glass_t(d, c)
    prism = f.box((-u.w / 2 - a - c.side_clear, u.w / 2 + a + c.side_clear), (-u.h / 2 - a, u.h / 2 + a), (g - reach, g + u.t))
    return {"reach": reach, "common_mm3": round(sum(volume_in(prism, s) for s in fixed), 3), "gap": round(min(gap(prism, s) for s in fixed), 2)}


def loads(d: Blueprint, c: Cradle, u: Unit, plate: Part.Shape) -> dict:
    """The load of the monitor on the cradle with the cabinet upright and tilted. Estimates: the values of Cradle
    say which numbers are assumptions."""
    a = math.radians(d.recline)
    preload = c.lock_torque / (0.2 * 0.004)
    hold = preload * c.lock_keep * c.friction
    pad_area = 2 * c.jaw_w * (u.t - c.jaw_front_gap)
    clamp = c.pad_stiffness * pad_area
    grip = 2 * c.pad_friction * clamp
    plate_kg = plate.Volume * ABS_DENSITY
    out = {"lock screw": {"torque_Nm": c.lock_torque, "preload_N": round(preload), "kept_N": round(preload * c.lock_keep), "holds_each_jaw_N": round(hold, 1)},
           "edge pads": {"area_each_edge_mm2": round(pad_area), "clamp_N": round(clamp, 1), "grip_N": round(grip, 1)},
           "plate": {"solid_kg": round(plate_kg, 2), "printed_kg": round(plate_kg * 0.45, 2), "magnets_N": 4 * c.magnet_pull}, "units": {}}
    for unit in (u, GENERIC):
        w = unit.mass * G
        along, normal = w * math.cos(a), w * math.sin(a)
        rows = {"weight_N": round(w, 1), "upright: along the face, on the two bottom jaws": round(along, 1), "upright: into the rests": round(normal, 1),
                "bottom jaws: friction over the load": round(2 * hold / along, 1),
                f"bottom jaws: friction over the load at {c.shock:g} g": round(2 * hold / (along * c.shock), 1), "tilted": {}}
        for tilt in (30.0, 45.0, 60.0, 90.0):
            t = math.radians(tilt)
            forward = w * math.sin(t - a)             # out of the cradle, toward the bezel plate
            on_top = w * -math.cos(t - a)             # along the face toward the top jaws when it is more than zero
            rows["tilted"][f"{tilt:g} deg forward"] = {"out of the cradle_N": round(max(forward, 0.0), 1),
                                                       "grip of the pads over it": round(grip / forward, 1) if forward > 1e-6 else None,
                                                       "on the bottom jaws_N": round(max(-on_top, 0.0), 1)}
        out["units"][unit.name] = rows
    # the lug as a cantilever of lug_reach from the ledge, loaded at its free edge by the share of one lug
    worst = GENERIC.mass * G
    f_lug = worst * math.sin(a) / 4 + worst * math.cos(a) / 2 * 0.0
    m = f_lug * c.lug_reach
    out["lug"] = {"normal_load_N": round(f_lug, 2), "bending_MPa": round(6 * m / ((c.lug_x1 - c.lug_x0) * c.lug_t ** 2), 3),
                  "along the face, in the plane of the ledge_N": round(worst * math.cos(a) / 2, 1),
                  "bearing of an M4 in the ear_MPa": round(worst * math.cos(a) / 2 / (4.0 * c.insert_depth), 2)}
    # the upright as a beam between its ears: the player pushes on the screen with 50 N at its middle
    span = 2 * (c.bar_half - c.ear_len / 2)
    push = 50.0 / 2
    i = c.bar_w * c.bar_t ** 3 / 12
    arm = c.bar_half - c.ear_len / 2 - (c.slot_v0 + c.slot_v1) / 2 + 10.0
    out["upright"] = {"span": round(span, 1), "push_on_the_screen_N": 50.0, "load_at_each_jaw_N": push / 2,
                      "bending_MPa": round((push / 2) * arm * (c.bar_t / 2) / i, 2), "note": "the jaws stand near the ears, so the bar bends little"}
    return out


def sight(d: Blueprint, c: Cradle, shell: dict[str, Part.Shape], plate: Part.Shape, doc) -> list[dict]:
    """The sight lines of the fit study with the printed plate in the shell and the glass glass_gap farther back."""
    from . import params  # noqa: PLC0415
    from . import fit  # noqa: PLC0415
    parts = dict(shell)
    parts["bezel"] = plate
    return fit.sight_lines(replace(d, mon_setback=d.mon_setback + c.glass_gap), parts, lambda name: params.value(doc, name))


# ---------- the print ----------

@dataclass(frozen=True)
class Print:
    part: str
    count: int
    up: tuple[float, float, float]      # the direction of the part in this module's frame (x, v, t) that points up on the bed
    along: tuple[float, float, float]   # its long direction on the bed
    how: str
    underside: str


PRINTS = (
    Print("bezel_half_right", 2, (-1, 0, 0), (0, 1, 0), "On its outer side face, the side bar along the bed diagonal. The two half bars stand up, the cut faces are on top.",
          "The outer side face: flat, 304 x 10 to 18. The land, the inner frame and the rim wall are walls or face up."),
    Print("upright_right", 2, (0, 0, -1), (0, 1, 0), "On its back, along the bed diagonal. The ears stand up.", "The back of the bar: flat, 301 x 24, with the back of the ears."),
    Print("jaw", 4, (1, 0, 0), (0, 1, 0), "On one side face: the profile lies on the bed.", "A side face: flat, the whole profile."),
    Print("shoe", 4, (0, 0, -1), (0, 1, 0), "On its back: the lip stands up.", "The back: flat, 25 x 14, with the nut pocket open to the bed."),
    Print("channel_right", 2, (0, 1, 0), (1, 0, 0), "On one end: the C section lies on the bed.", "An end face: flat, the whole section."),
)


def oriented(shape: Part.Shape, d: Blueprint, up: tuple[float, float, float], along: tuple[float, float, float]) -> Part.Shape:
    """A part turned into its print orientation, its box at the origin."""
    f = Frame(d)
    world = lambda a: V(a[0], 0, 0) + f.up * a[1] + f.into * a[2]
    z, x = world(up), world(along)
    y = z.cross(x)
    m = App.Matrix(x.x, x.y, x.z, 0, y.x, y.y, y.z, 0, z.x, z.y, z.z, 0, 0, 0, 0, 1)
    s = shape.copy()
    s.transformShape(m)
    b = s.optimalBoundingBox(False, False)      # the box of a B-spline face is its poles' box otherwise
    s.translate(V(-b.XMin, -b.YMin, -b.ZMin))
    return s


def print_rows(d: Blueprint, shapes: dict[str, Part.Shape]) -> list[dict]:
    from . import coupon  # noqa: PLC0415
    rows = []
    for p in PRINTS:
        if p.part not in shapes:
            continue
        s = oriented(shapes[p.part], d, p.up, p.along)
        b = s.optimalBoundingBox(False, False)
        a, w = max(b.XLength, b.YLength), min(b.XLength, b.YLength)
        lim = split.printer()
        fits = b.ZLength <= lim.z and (a <= lim.xy or (a + w) / math.sqrt(2) <= lim.xy)
        over = coupon.overhangs(s, OVERHANG_LIMIT)
        rows.append({"part": p.part, "count": p.count, "how": p.how, "underside": p.underside, "box": [round(a, 1), round(w, 1), round(b.ZLength, 1)],
                     "on_the_diagonal": a > lim.xy, "diagonal_needs": round((a + w) / math.sqrt(2), 1), "fits": fits,
                     "overhang_mm2": round(sum(g["area_mm2"] for g in over), 1), "overhangs": over[:6], "mass_g_solid": round(s.Volume * ABS_DENSITY * 1000)})
    return rows


# ---------- the edge rule and the face check ----------

# the class of each part for the edge rule: the plate is a printed and painted part of the exterior; the others are
# inside the body, where the rule does not hold
EDGE_CLASS = {"bezel_plate": "printed"}
EDGE_JOINTS = {"body": "The recess of the plate: the ledges and the lugs behind it.", "lugs": "The plate lies on the lugs.",
               "screen": "The back of the plate in front of the monitor.", "monitor": "The back of the plate in front of the monitor.",
               "the other half": "The seam of the two halves of the plate, on the centre line, on pins."}


# the printed parts of the print folder (print/), for tools/edge_finish.py: the halves of the plate are painted
# parts of the outside; the others are printed parts inside the shell
HALVES = ("bezel_half_right", "bezel_half_left")
INSIDE = ("upright", "jaw", "shoe", "channel")


def edge_covers(d: Blueprint, c: Cradle = Cradle(), u: Unit = PRESENT) -> dict[str, Part.Shape]:
    """What the faces of the plate lie against in place (EDGE_JOINTS): the body and the screen of the built shell,
    the lugs and the monitor."""
    shell = shell_parts()
    return {"body": shell["body"], "screen": shell["screen"], "lugs": lugs(d, c), "monitor": monitor(d, c, u)}


def edge_rows(d: Blueprint, plate: Part.Shape, shell: dict[str, Part.Shape], parts: dict[str, Part.Shape]) -> dict:
    """The edge rule on the plate with tools/edge_finish.py: its convex edges that turn more than edge_break_turn and
    have no round, by what they lie against. A sharp edge passes only against a part of EDGE_JOINTS."""
    from tools import edge_finish  # noqa: PLC0415
    scene = {"bezel_plate": plate, "body": shell["body"], "screen": shell["screen"], "lugs": parts["lugs"], "monitor": parts["monitor"]}
    rows = edge_finish.survey(scene, d)["bezel_plate"]
    rows["class"] = EDGE_CLASS["bezel_plate"]
    bad = [f"{g['edges']} sharp edges show ({g['length']} mm, {g['turn'][0]:g} to {g['turn'][1]:g} degrees), the longest at {tuple(g['at'][0])}"
           for g in rows["sharp"] if not g["against"]]
    bad += [f"{g['edges']} sharp edges lie against {g['against']}, which is not a named joint" for g in rows["sharp"] if g["against"] and g["against"] not in EDGE_JOINTS]
    return {"rows": rows, "failures": bad}


def face_known(d: Blueprint, part: str, rule: str, at: tuple[float, float, float], detail: str) -> str:
    """Why a finding of the face check stays, or "" when it must not. One entry for each kind of finding."""
    f = Frame(d)
    x, v, t = f.local(V(*at))
    if part in ("shoes", "shoe") and rule == "sliver" and "Plane" in detail:
        return "the seat of the M4 nut: a ring 1.25 wide between the hexagon pocket and the screw hole"
    if part not in ("bezel_plate", "bezel_half_right", "bezel_half_left"):
        return ""
    corner = abs(abs(x) - MON_ACTIVE_W / 2) < 1.5 and abs(abs(v) - MON_ACTIVE_H / 2) < 1.5
    if corner and rule in ("sliver", "needle", "crowded"):
        return ("corner of the window: the patch that OpenCascade makes where the rounds of two edges of the window meet "
                "in a concave corner (0.2 mm2)")
    if rule == "sliver" and "Plane" in detail and f.t0 - d.bezel_rim < t < f.t0 and (abs(abs(x) - MON_ACTIVE_W / 2) < 0.1 or abs(abs(v) - MON_ACTIVE_H / 2) < 0.1):
        return "rim wall of the window: bezel_rim 2 deep by design, less the edge break"
    if rule == "sliver" and "Sphere" in detail and abs(x) > f.half_w - 2.0 and abs(v) > f.half_len - 2.0:
        return "corner of the outline: the ball of the edge break where three broken edges meet"
    return ""


def face_rows(d: Blueprint, parts: dict[str, Part.Shape]) -> dict:
    """tools/face_check.py on each printed part and each added solid. No reveal of the shell is used: a finding
    passes as a face of the edge break, or as an item of face_known, which gives the reason."""
    from tools import face_check  # noqa: PLC0415
    out = {}
    for k in PRINTED + ADDED + tuple(x for x in parts if x.startswith("bezel_half")):
        found = []
        for s in parts[k].Solids:
            found += face_check.check(s, k, [], d.edge_break)
        for x in found:
            x.allowed = x.allowed or face_known(d, k, x.rule, x.at, x.detail)
        out[k] = {"findings": len(found), "not_allowed": [asdict(x) for x in found if not x.allowed],
                  "allowed": {why: sum(1 for x in found if x.allowed == why) for why in sorted({x.allowed for x in found if x.allowed})}}
    return out


# ---------- the build folder ----------

def export(out: Path, parts: dict[str, Part.Shape], finish: dict[str, str] = FINISH) -> None:
    from . import solids as so  # noqa: PLC0415
    out.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for k, s in parts.items():
        MeshPart.meshFromShape(Shape=s, LinearDeflection=MESH_LINEAR, AngularDeflection=MESH_ANGULAR).write(str(out / f"{k}.stl"))
        s.exportBrep(str(out / f"{k}.brep"))
        manifest[k] = {"file": f"{k}.stl", "finish": finish.get(k, "grey"), "brep": f"{k}.brep"}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    (out / "edges.json").write_text(json.dumps({k: so.edge_polylines(s) for k, s in parts.items()}), encoding="utf-8")


def section(shapes: dict[str, Part.Shape], f: Frame, normal: App.Vector, at: App.Vector, axes) -> dict[str, list]:
    """Each shape cut by a plane, as polylines in two coordinates of this module's frame."""
    out = {}
    for k, s in shapes.items():
        lines = []
        for w in s.slice(normal, at.dot(normal)):
            lines.append([[round(f.local(p)[axes[0]], 3), round(f.local(p)[axes[1]], 3)] for p in w.discretize(Deflection=0.05)])
        if lines:
            out[k] = lines
    return out


def markdown(rep: dict) -> str:
    c = rep["cradle"]
    lines = ["# The monitor cradle and the bezel plate: checks", "", f"Result: **{rep['result']}**.", "",
             "## Solids", "", "| Part | Valid | Solids | Closed | Faces | Volume, cm3 |", "| --- | --- | --- | --- | --- | --- |"]
    lines += [f"| {k} | {r['valid']} | {r['solids']} | {r['closed']} | {r['faces']} | {r['volume_mm3'] / 1000:.1f} |" for k, r in rep["solids"].items()]
    lines += ["", "## Clashes", "", f"{len(rep['clashes'])} pairs. The pairs with a common volume:", ""]
    bad = [r for r in rep["clashes"] if r["common_mm3"] > TOL_VOLUME]
    lines += [f"- {r['a']} / {r['b']}: {r['common_mm3']} mm3" for r in bad] or ["- none"]
    lines += ["", "The smallest gaps:", "", "| Part | Against | Gap |", "| --- | --- | --- |"]
    lines += [f"| {r['a']} | {r['b']} | {r['gap']:.2f} |" for r in sorted(rep["clashes"], key=lambda r: r["gap"])[:24]]
    lines += ["", "Added solids on the body, volume in common with the skin (mm3): " + json.dumps(rep["attached"]), "",
              "Inner face of the right side at the bosses: " + ", ".join(f"x {r['inner_x']} at v {r['v']}, t {r['t']}" for r in rep["side_wall"]), "",
              "## The way out", "", "| Out | What | Common volume, mm3 | Gap |", "| --- | --- | --- | --- |"]
    lines += [f"| {r['out_mm']:g} | {r['what']} | {r['common_mm3']} | {r['gap']:.2f} |" for r in rep["path"]]
    s = rep["sweep"]
    lines += ["", f"The prism that any unit passes through, {s['reach']:g} out: {s['common_mm3']} mm3 in common with what stays, gap {s['gap']:.2f}.", "",
              "## Room in the opening, and the shrink", ""]
    keys = list(next(iter(rep["room"].values())))
    lines += ["| Value | " + " | ".join(rep["room"]) + " |", "| --- |" + " --- |" * len(rep["room"])]
    lines += [f"| {k} | " + " | ".join(str(r[k]) for r in rep["room"].values()) + " |" for k in keys]
    lines += ["", "## Leads and the power button", "", "Sockets of the present unit (x, v): " + json.dumps(rep["sockets"]), "",
              "| Lead | Side | Socket at v | Clamp at v | Distance | Limit |", "| --- | --- | --- | --- | --- | --- |"]
    lines += [f"| {r['lead']} | {r['side']} | {r['socket_v']} | {r['clamp_v']} | {r['distance']} | {r['limit']} |" for r in rep["clamps"]]
    lines += ["", "Option for the power button: " + json.dumps(rep["button"]), ""]
    lines += ["", "## Sight lines", "", "| Player | To the screen normal, deg | Image hidden at the top | At the bottom | Fit study: top | Bottom |", "| --- | --- | --- | --- | --- | --- |"]
    lines += [f"| {r['person']} | {r['to_normal_deg']:.1f} | {r['hidden_top']:.1f} | {r['hidden_bottom']:.1f} | {b['hidden_top']:.1f} | {b['hidden_bottom']:.1f} |"
              for r, b in zip(rep["sight"], rep["sight_before"])]
    lines += ["", "## Loads (estimates)", "", "```json", json.dumps(rep["loads"], indent=1), "```", "",
              "## Print", "", "| Part | Count | Box on the bed | Fits | Overhang over 45 deg, mm2 | Mass solid, g | How | Underside |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    lines += [f"| {r['part']} | {r['count']} | {r['box'][0]} x {r['box'][1]} x {r['box'][2]}{' (diagonal: ' + str(r['diagonal_needs']) + ')' if r['on_the_diagonal'] else ''} | "
              f"{r['fits']} | {r['overhang_mm2']} | {r['mass_g_solid']} | {r['how']} | {r['underside']} |" for r in rep["print"]]
    e = rep["edge"]
    lines += ["", "## Edge rule on the bezel plate", "", f"Faces of the edge break: {e['rows']['break_faces']}. Sharp convex edges:", ""]
    lines += [f"- {g['edges']} edges, {g['length']} mm, {g['turn'][0]:g} to {g['turn'][1]:g} degrees: {'against ' + g['against'] if g['against'] else 'SHOWS'}" for g in e["rows"]["sharp"]] or ["- none"]
    lines += ["", "Failures: " + ("; ".join(e["failures"]) or "none"), "", "## Face check", "", "| Part | Findings | Not allowed | Allowed as |", "| --- | --- | --- | --- |"]
    lines += [f"| {k} | {r['findings']} | {len(r['not_allowed'])} | {'; '.join(f'{n} x {why}' for why, n in r['allowed'].items())} |" for k, r in rep["faces"].items()]
    for k, r in rep["faces"].items():
        lines += [f"- {k}: {x['rule']} at {x['at']}: {x['detail']}" for x in r["not_allowed"]]
    lines += ["", "## Failures", ""] + ([f"- {x}" for x in rep["failures"]] or ["- none"])
    lines += ["", "## Values", "", "```json", json.dumps(c, indent=1), "```"]
    return "\n".join(lines) + "\n"


def study(d: Blueprint, c: Cradle, u: Unit, out: Path, log=print) -> dict:
    """Build the parts, check them and write the build folder."""
    from . import solids as so  # noqa: PLC0415
    lines: list[str] = []
    parts = build(d, c, u, lines)
    for line in lines:
        log(line)
    f = Frame(d)
    shell = shell_parts()
    skin = skin_near(d)
    log(f"cradle: skin round the screen face: {len(skin.Solids)} solids, valid {skin.isValid()}")
    doc, found = fit_items(d)
    halves = bezel_halves(d, c, parts["bezel_plate"])
    plain = bezel_plate(d, c, back=False)
    option = button_option(d, c, u, parts["bezel_plate"])
    rows = clashes(parts, skin, found, c)
    fixed = [skin, parts["lugs"], parts["bosses"], parts["upright_right"], parts["upright_left"], parts["channel_right"], parts["channel_left"]]
    bottom_jaws = Part.makeCompound([jaw(d, c, u, sx, -1) for sx in (1, -1)])
    rep = {"cradle": asdict(c), "unit": asdict(u), "generic": asdict(GENERIC), "log": lines,
           "solids": solid_rows({k: parts[k] for k in PRINTED + ADDED} | halves),
           "clashes": rows, "attached": attached(parts, skin), "side_wall": side_wall(d, c, skin),
           "path": path_out(d, c, u, fixed, bottom_jaws, (0.0, 30.0, 60.0, 150.0)), "sweep": sweep_out(d, c, 200.0, fixed),
           "sockets": {k: [round(x, 1), round(v, 1)] for k, (x, v) in sockets(d, c, u).items()}, "clamps": clamp_rows(d, c, u),
           "room": room_rows(d, c, u), "loads": loads(d, c, u, parts["bezel_plate"]),
           "sight": sight(d, c, shell, parts["bezel_plate"], doc),
           "sight_before": json.loads((shell_dir() / "fit" / "report.json").read_text(encoding="utf-8"))["sight"],
           "print": print_rows(d, {"bezel_half_right": halves["bezel_half_right"], "upright_right": parts["upright_right"], "jaw": jaw(d, c, u, 1, -1),
                                   "shoe": shoe(d, c, u, 1, -1), "channel_right": parts["channel_right"]}),
           "edge": edge_rows(d, parts["bezel_plate"], shell, parts), "faces": face_rows(d, parts | halves)}
    rep["button"] = button_rows(d, c, u, option, parts, skin)
    bad = [f"{k}: not one valid closed solid each" for k, r in rep["solids"].items() if not (r["valid"] and r["closed"])]
    bad += [f"clash: {r['a']} / {r['b']}: {r['common_mm3']} mm3" for r in rows if r["common_mm3"] > TOL_VOLUME]
    bad += [f"{k}: an added solid is not on the skin" for k, vs in rep["attached"].items() if min(vs) <= 0]
    bad += [f"way out at {r['out_mm']:g}: {r['what']}: {r['common_mm3']} mm3" for r in rep["path"] if r["common_mm3"] > TOL_VOLUME]
    bad += [f"way out: the prism shares {rep['sweep']['common_mm3']} mm3"] if rep["sweep"]["common_mm3"] > TOL_VOLUME else []
    bad += [f"lead clamp: {r['lead']} is {r['distance']} from its clamp" for r in rep["clamps"] if r["distance"] > r["limit"]]
    bad += [f"button option: {k}: {v} mm3" for k, v in rep["button"]["clashes"].items() if v > TOL_VOLUME]
    bad += ["button option: a part is not one valid solid"] if not rep["button"]["valid"] else []
    bad += [f"print: {r['part']} does not fit the printer" for r in rep["print"] if not r["fits"]]
    bad += [f"edge rule: {x}" for x in rep["edge"]["failures"]]
    bad += [f"face check: {k}: {x['rule']} at {x['at']}: {x['detail']}" for k, r in rep["faces"].items() for x in r["not_allowed"]]
    bad += [f"sight line: {r['person']} loses {r['hidden_top']:.1f} at the top and {r['hidden_bottom']:.1f} at the bottom"
            for r, b in zip(rep["sight"], rep["sight_before"]) if r["hidden_top"] > b["hidden_top"] + 1.0 or r["hidden_bottom"] > b["hidden_bottom"] + 1.0]
    rep["failures"], rep["result"] = bad, "FAIL" if bad else "PASS"
    # the build folder: the parts in place, with the skin round the screen face and the body for the document
    show = dict(parts)
    show["skin"] = skin
    export(out, show)
    export(out / "print", halves | {"upright": parts["upright_right"], "jaw": jaw(d, c, u, 1, -1), "shoe": shoe(d, c, u, 1, -1), "channel": parts["channel_right"]})
    export(out / "options" / "halves", {"bezel_half_right": halves["bezel_half_right"], "bezel_half_left": halves["bezel_half_left"]})
    export(out / "options" / "button", option, {"bezel_plate_button": "black", "button_rod": "#d03030", "button_striker": "#e0a030", "button_guide": "#6080c0"})
    bars = bezel_bars(d, plain)
    export(out / "options" / "bars", bars, {k: ("black" if i % 2 == 0 else "#303030") for i, k in enumerate(bars)})
    # the way out: three positions of the monitor with its plugs
    for name, o in (("in", 0.0), ("half", 60.0), ("out", 150.0)):
        export(out / "path" / name, {"monitor": monitor(d, c, u, o), "plugs": plugs(d, c, u, o)})
    scene = {k: parts[k] for k in PRINTED + ADDED + HARDWARE} | {"skin": skin}
    cuts = {"bottom clamp": section(scene, f, V(1, 0, 0), f.pt(c.bar_x, 0, 0), (1, 2)),
            "centre line": section(scene, f, V(1, 0, 0), f.pt(0.01, 0, 0), (1, 2)),
            "lug and ear": section(scene, f, V(1, 0, 0), f.pt(c.bar_x - c.bar_w / 2 - c.ear_w / 2, 0, 0), (1, 2)),
            "pin": section(scene, f, V(1, 0, 0), f.pt(c.pin_x, 0, 0), (1, 2)),
            "magnet": section(scene, f, V(1, 0, 0), f.pt(c.magnet_x, 0, 0), (1, 2)),
            "channel": section(scene, f, f.up, f.pt(0, c.boss_v[1], 0), (0, 2)),
            "across the image": section(scene, f, f.up, f.pt(0, 0, 0), (0, 2)),
            "button": section({k: v for k, v in scene.items() if k != "bezel_plate"} | option, f, f.up, f.pt(0, sockets(d, c, u)["power button"][1], 0), (0, 2))}
    (out / "sections.json").write_text(json.dumps({"cuts": cuts, "frame": {"half_w": f.half_w, "half_len": f.half_len, "t0": f.t0}, "edges_v": edges_v(u),
                                                   "unit": asdict(u), "cradle": asdict(c)}), encoding="utf-8")
    (out / "report.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
    (out / "report.md").write_text(markdown(rep), encoding="utf-8")
    App.closeDocument(doc.Name)
    return rep


def main() -> int:
    out = Path(os.environ.get("CANDYBAR_OUT") or CAD / "out" / "cradle")
    rep = study(Blueprint(), Cradle(), PRESENT, out)
    print(markdown(rep))
    return 1 if rep["failures"] else 0
