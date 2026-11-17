"""The control panel as printed parts, and the interface that every control panel shares (roadmap step 12).

Run headless. It exits 1 when a check fails:

    CANDYBAR_OUT=cad/out/control-panel cad/candybar/freecad-run.sh candybar.shell.panel_frame
    CANDYBAR_OUT=cad/out/control-panel cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc    # shell.FCStd
    cad/.venv-tools/bin/python cad/tools/draw_panel.py                                             # the sheets

A control panel is a service part: it lifts out of the pocket of the deck and another panel goes in. The parts:

  the frame        a ring of two halves, bonded under the ledge of the deck's opening. It has the four latch points
                   (a pad in each corner of the opening), the two locating cones (on two pads at the rear edge) and
                   the anchor of the cable. Four posts carry it on the floor. It stays in the cabinet.
  the arcade panel two tiles (the plate is wider than the printer), bonded and screwed at a seam between the lever
                   and the buttons. It has the holes of the lever and the buttons that fit.Layout places, the seat
                   of the lever, the bosses of the encoder, ribs where they clear the hardware, and the cable clip.
  the blank panel  a second panel made from the interface only. It proves that the interface is sufficient.

Interface holds every value that a panel and the frame share. Arcade holds the values of the arcade panel. The
outer form does not change, and the shell gets no new opening: all the parts stand inside the opening that
cavity.Openings makes under the panel.

Frames: the cabinet frame of dims.py. "yl" in this module is a depth from the front edge of the panel at the centre
line (y - panel_y0), as the parameter sheets give the positions of the lever and the buttons.
"""
from __future__ import annotations

import json
import math
import os
import time
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

import FreeCAD as App
import MeshPart
import Part

from . import cavity, controls, fit, model, params, split, structure
from . import profiles as pr
from . import solids as so
from .dims import Blueprint
from .joints import OTHER_JOINTS

V = App.Vector
P2 = tuple[float, float]
CAD = Path(__file__).resolve().parents[2]
PARAMS = CAD / "params"
OUT = "cad/out/control-panel"
TOL = 1.0              # mm3: the common volume that the fit rules allow (check.VOLUME_TOLERANCE)
ABS = split.ABS_G_PER_CM3 / 1000  # g/mm3
SNAP_IN, SPREAD = "snap-in", "spread"
SCREW, MAGNET, PUSH_BOLT = "screw", "magnet", "push-bolt"
STEEL = "steel"
FINISH = {"deck": "white", "frame": "#8fa6c2", "post": "#6f86a2", "tile": "#2b2b2e", "blank": "#3d4a40", "latch": "#d0762b",
          "spring": "#8c8f96",
          "Lever": "#b03030", "Buttons": "#c8a020", "Encoder": "#2f7a3a", "USB": "#3070c0", "Hub": "#6a4fa0",
          "screw": "#b8bcc4", "insert": "#c9a23a", "magnet": "#9aa0aa", "floor": "#c9ccd2", "underside": "#9a9da6"}


@dataclass(frozen=True)
class PushBolt:
    """The latch PUSH_BOLT (docs/design/control-panel-latch.md, the owner's choice of 2026-11-15): two hooks under the
    rear edge of the panel in notches of the rear bar of the frame, and one printed bolt at the front centre in a tunnel
    that is one print with the left half of the frame. The front end of the bolt is a flush button in the front face of
    the deck (the hole: Blueprint.latch_button_d). A steel spring pushes the bolt forward; a gate dropped into the rear
    of the tunnel holds the spring; a wedge under the bolt pulls the panel down. A magnet in each of the four pads of
    the frame, a steel disc above each in the plate. A panel with nothing to hold has a finger hole.
    Frames: the cabinet frame (y from the front face of the deck, z up from the desk). Lengths in mm."""
    # the magnets: a disc of Interface.magnet_d x pad_magnet_h in each pad; in the plate a disc of magnet_d x
    # Interface.keeper_h of plate_disc: STEEL (the user, 2026-11-16: no pole to mind, about 10 % less pull, ESTIMATED)
    # or a magnet
    pad_magnet_h: float = 2.0
    plate_disc: str = STEEL
    # the rear hooks: a stem under the plate and a toe whose top and bottom are arcs about the pivot (the rear top edge
    # of the plate). The toe goes into a notch in the rear bar of the frame
    hook_x: float = 100.0
    hook_w: float = 14.0
    stem_t: float = 6.0
    stem_gap: float = 1.0          # the stem's rear face to the inner face of the frame bar
    notch_top: float = 56.0        # the roof of the notch (z of its lower face)
    notch_back: float = 4.4        # the notch goes this far into the bar
    notch_side: float = 1.0        # clearance each side of the hook
    toe_clear: float = 0.3         # radial clearance of the toe under the front edge of the roof
    toe_r_out: float = 20.0
    toe_tip_gap: float = 0.6       # the tip of the toe to the back of the notch
    # the bolt
    bolt_w: float = 12.0
    bolt_z: tuple = (52.0, 58.0)
    # the button fits in the leaning band of the front face (z 48 to 62.6), so that its face is one plane. Its outline
    # is the outline of the hole (Blueprint.latch_button_d, latch_button_flats, latch_button_z, solids.LATCH_CORNER)
    # moved in by button_gap (button_outline): a round of 14, two flats bolt_w apart, the four corners rounded
    button_gap: float = 0.3
    lug_y: tuple = (46.5, 50.5)    # the strike on the panel (its legs and lips), yl 20.5 to 24.5
    lug_leg_t: float = 7.0
    lug_lip: float = 3.4           # the lips reach in under the bolt
    lug_z0: float = 49.5
    bolt_clear: float = 0.2
    wedge_deg: float = 8.0         # the lips and the underside of the bolt meet at this angle
    neck_w: float = 4.0
    neck_margin: float = 0.75      # the neck is this much longer than the lug at its rear end
    neck_front: float = 2.0        # and this much at its front end: the lips move forward a little as the front swings up
    stroke: float = 5.0
    bolt_end_y: float = 66.0
    stop_y: float = 61.0           # the stop block on the bolt (it limits the forward travel with the panel out)
    stop_w: float = 18.0
    stop_l: float = 2.5            # along y: the side of the bolt behind it is then 2.5 long (3 left a face of 2, the limit of the face check)
    # the tunnel of the bolt: one print with the left half of the frame. Its floor lies in the plane of the lower
    # face of the bar (the frame prints on that plane), under the bolt; its walls and roof close round the bolt
    # behind the strike. A gate dropped into a slot at its rear holds the spring; the panel keeps the gate in.
    housing_y: tuple = (26.5, 78.0)
    housing_w: float = 32.0        # the floor
    tunnel_w: float = 26.0         # outside the walls
    roof_z: tuple = (58.3, 62.3)
    strike_window: float = 0.5     # round the strike, in the floor
    gate_y: tuple = (72.2, 75.8)
    gate_x: tuple = (-8.4, 10.6)
    gate_tab: float = 2.0          # the gate stands this much above the roof: a grip for the fingers
    gate_slot_clear: float = 0.2
    # behind the tunnel the room of a panel stops room_rear back: a rib on the centre line (the seam of the blank
    # panel) sweeps 1.1 forward into the end of the roof as the front swings up 3 to 4 degrees
    room_rear: float = 3.0
    frame_split_x: float = 20.0    # the halves of the frame meet here, not on the centre line: the tunnel is whole in the left half
    # a panel with nothing to hold (the blank panel) has a finger hole near its front edge (the user, 2026-11-16)
    finger_hole: tuple = (50.0, 37.0, 22.0)   # x, yl, diameter
    # the bought spring of the bolt: steel, 4 outside, 22 free, about 1.2 N/mm (7.8 N at the lock, 13.8 N at the stroke)
    bolt_spring_free: float = 22.0
    bolt_spring_rate: float = 1.2
    bolt_spring_bore: float = 4.4
    bolt_spring_d: float = 4.0


PB0 = PushBolt()


@dataclass(frozen=True)
class Interface:
    """What a control panel and the frame share. A panel that matches these values goes into the cabinet."""
    # the plate stands seat_gap inside the wall of its seat (profiles.panel_outline moved in). Its top is
    # Blueprint.panel_top, its rest face panel_t below. The coupon sets the gap
    seat_gap: float = 0.3
    # the opening under the plate: the outline moved in by the ledge of cavity.Openings (the rest face is that wide)
    ledge: float = cavity.Openings().panel_ledge
    # a bonded face of the frame stands this far from the skin: the room of the adhesive
    bond_gap: float = 0.2
    # the latch: PUSH_BOLT (the default since 2026-11-16: the rear hooks, the push bolt and a magnet with a steel disc
    # at each latch point, PushBolt), SCREW (the fall-back: four flush M4 screws into inserts in the pads) or MAGNET
    # (a magnet in each pad, a thin magnet in the plate above it, nothing else). One value: all use the same four
    # latch points
    latch: str = PUSH_BOLT
    push: PushBolt = PB0
    # a latch point is latch_at from a corner of the opening, on the line that halves the corner. The frame has a
    # pad of pad_r there, inside the opening. Its top stands pad_drop below the rest face, so that the plate
    # rests on the ledge and does not rock on a pad
    latch_at: float = 12.5
    pad_r: float = 21.0
    pad_drop: float = 0.1
    # the screw: M4 x 16 countersunk (ISO 10642), flush in a countersink of screw_head_d; its insert in the pad
    latch_screw_d: float = 4.0
    latch_screw_l: float = 16.0
    screw_hole_d: float = 4.5
    screw_head_d: float = 9.0
    insert_hole_d: float = OTHER_JOINTS.insert_hole_d
    insert_l: float = OTHER_JOINTS.insert_l
    # the hole under each latch insert: deeper than the insert hole of the joints (joints.OTHER_JOINTS), because the
    # M4 x 16 latch screw goes through the plate of panel_t and 11 into the pad, past the end of the insert
    latch_hole_depth: float = 12.5
    # the magnets: a disc of magnet_d x magnet_h in the pad, a disc of magnet_d x keeper_h in the plate
    magnet_d: float = 12.0
    magnet_h: float = 5.0
    keeper_h: float = 2.0
    magnet_clear: float = 0.2
    # the locating cones: two cones on pads at the rear edge of the opening, cone_x each side of the centre line
    # and cone_in from the edge. The panel has a round socket at -cone_x and a slot along X at +cone_x, so that a
    # change of size between two prints does not bind them
    cone_x: float = 120.0
    cone_in: float = 6.5
    cone_d: float = OTHER_JOINTS.cone_d
    cone_top_d: float = 5.0
    cone_h: float = OTHER_JOINTS.cone_h
    cone_clear: float = OTHER_JOINTS.cone_clearance
    cone_slot: float = 1.5
    cone_pad_r: float = 12.0
    # the frame: a bar of bar_h under the ledge; a post under the bar at post_x each side of the centre line, at
    # the front and at the rear, post_w wide
    bar_in: float = 0.5
    bar_h: float = 12.0
    post_x: float = 66.0
    post_w: float = 20.0
    half_gap: float = OTHER_JOINTS.closing_gap
    # the cable: one USB cable. A clip holds it under the panel (clip_x, clip_yl: its middle), another on the
    # frame at the rear edge (anchor_x). Between the two clips the cable has cable_slack, which lies on the floor
    cable_bore: float = 4.2
    cable_mouth: float = 3.4
    clip_l: float = 14.0
    clip_w: float = 9.0
    clip_h: float = 10.0
    clip_x: float = -93.0
    clip_yl: float = 145.5
    anchor_x: float = -80.0
    cable_slack: float = 300.0
    # the room below the plate that a panel can use: the opening less room_gap, down to room_floor_gap above the
    # floor, without the pads and the anchor (less room_gap), and without the space of the USB sockets
    room_gap: float = 0.5
    room_floor_gap: float = 2.0
    usb_gap: float = 2.0
    # ribs of a panel: this deep below the plate, this far from the front and the rear edge of the panel
    rib_h: float = 15.0
    rib_front_yl: float = 20.0
    rib_rear_yl: float = 150.0
    rib_t: float = 3.0
    rib_end_x: float = 164.0
    seam_flange_t: float = 4.0
    seam_screw_d: float = 3.4
    seam_screw_z: float = 10.0

    def pad_magnet_h(self) -> float:
        """The height of the magnet in a pad of the frame."""
        return self.push.pad_magnet_h if self.latch == PUSH_BOLT else self.magnet_h

    def magnet_pull(self) -> float:
        """ESTIMATED hold of one latch point with magnets, N: an N52 disc of 12 x 5 pulls about 35 N on thick steel
        (data sheets of the suppliers). Against a disc of 12 x 2, with a gap of 2 x magnet_clear, about 20 N."""
        return 20.0


@dataclass(frozen=True)
class Arcade:
    """The arcade panel. The positions of the lever, the buttons and the encoder are those of fit.Layout."""
    # the buttons: SPREAD (screw-in buttons, Sanwa OBSN-30 with their nuts of 36 across: the layout larger by spread
    # about button 1 (next to the seam of the tiles), so that no two nuts overlap, and the plate at its full thickness of panel_t,
    # 5, the largest panel that Sanwa gives for them) or SNAP_IN (Sanwa OBSF: the plate is seat_t thick round each
    # hole, by a counterbore from below). One value. The owner uses screw-in buttons (2026-11-14)
    buttons: str = SPREAD
    seat_t: float = 3.0
    seat_ring: float = 2.0
    spread: float = 1.02
    # a printed hole is drawn hole_allow larger than the data sheet's hole (controls-ergonomics.md 2.4)
    hole_allow: float = 0.3
    # the seam between the lever tile and the button tile: seam_dx to the right of the lever
    # (controls-ergonomics.md 3.6: between the lever body and the first button)
    seam_dx: float = 36.0
    seam_screws_yl: tuple[float, ...] = (30.0, 44.0, 131.0, 145.0)
    # the seat of the lever: a pad to the depth of stick_plate_drop, lever_margin round the lever's plate
    lever_margin: float = 3.0
    # the rib between the encoder and the harness of the lever, and the rib between the buttons and the service
    # buttons (its middle, from the centre line)
    rib_right_x: float = 128.5
    rib_right_t: float = 4.0
    # the gate for the cable in the rib beside the encoder
    gate_yl: tuple[float, float] = (140.0, 148.0)
    gate_h: float = 7.0
    # the encoder: bosses of boss_d on its four holes (the pattern of the RP2040 Advanced Breakout Board)
    enc_hole_x: float = 36.95
    enc_hole_y: float = 87.96
    boss_d: float = 8.0
    boss_pilot_d: float = 2.6
    boss_pilot_depth: float = 6.0
    # the load of the lever: a hard input, sideways on the ball (controls-ergonomics.md 6.3: 20 to 40 N, about 60
    # above the panel)
    lever_load: float = 40.0
    lever_arm: float = 60.0
    hand_load: float = 100.0


# ---------- geometry helpers ----------

def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part.Shape:
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(d: float, x: float, y: float, z0: float, z1: float) -> Part.Shape:
    return Part.makeCylinder(d / 2, z1 - z0, V(x, y, z0), V(0, 0, 1))


def plan(points: list[P2], z0: float, z1: float) -> Part.Shape:
    return so.prism(so.poly(points), so.xy(z0), V(0, 0, z1 - z0))


def joined(shapes: list[Part.Shape]) -> Part.Shape:
    out = shapes[0].fuse(shapes[1:]) if len(shapes) > 1 else shapes[0]
    return so.unsplit(out)


def one_solid(shape: Part.Shape, what: str) -> Part.Shape:
    if shape.isNull() or not shape.isValid() or len(shape.Solids) != 1:
        raise RuntimeError(f"{what}: not one valid solid ({0 if shape.isNull() else len(shape.Solids)} solids)")
    return shape.Solids[0]


def y0(d: Blueprint) -> float:
    """Y of the front edge of the panel at the centre line: yl is measured from it."""
    return d.deck_nose + d.panel_gap


def z_rest(d: Blueprint) -> float:
    return d.panel_top - d.panel_t


def opening(d: Blueprint, i: Interface, less: float = 0.0) -> list[P2]:
    """The opening under the panel, moved in by `less`."""
    return pr.panel_outline(d, -(i.ledge + less))


def corners(d: Blueprint, i: Interface, less: float = 0.0) -> list[tuple[P2, P2]]:
    """The four corners of the opening (front left, front right, rear right, rear left), each with the unit vector
    that halves the corner and points into the opening."""
    pts = opening(d, i, less)
    out = []
    for k in (0, 3, 4, 5):
        p, a, b = pts[k], pts[k - 1], pts[(k + 1) % len(pts)]
        u = [(q[0] - p[0]) / math.dist(p, q) for q in (a, b)], [(q[1] - p[1]) / math.dist(p, q) for q in (a, b)]
        n = math.hypot(sum(u[0]), sum(u[1]))
        out.append((p, (sum(u[0]) / n, sum(u[1]) / n)))
    return out


def latch_points(d: Blueprint, i: Interface) -> list[P2]:
    """The four latch points in plan."""
    return [(p[0] + i.latch_at * b[0], p[1] + i.latch_at * b[1]) for p, b in corners(d, i)]


def cone_points(d: Blueprint, i: Interface) -> list[P2]:
    """The two locating cones in plan: the round one at the left, the one in the slot at the right."""
    y = y0(d) + d.panel_d - i.ledge - i.cone_in
    return [(-i.cone_x, y), (i.cone_x, y)]


def clip(x: float, y: float, z_base: float, i: Interface, up: bool) -> Part.Shape:
    """A cable clip: a block with a bore along X and a mouth in the face that is far from its base (up: the base is
    its lower face). The cable goes in through the mouth, which is narrower than the bore."""
    s = 1.0 if up else -1.0
    z_tip = z_base + s * i.clip_h
    zc = z_tip - s * (i.cable_bore / 2 + 1.6)
    block = box(x - i.clip_l / 2, x + i.clip_l / 2, y - i.clip_w / 2, y + i.clip_w / 2, min(z_base, z_tip), max(z_base, z_tip))
    bore = Part.makeCylinder(i.cable_bore / 2, i.clip_l + 2, V(x - i.clip_l / 2 - 1, y, zc), V(1, 0, 0))
    mouth = box(x - i.clip_l / 2 - 1, x + i.clip_l / 2 + 1, y - i.cable_mouth / 2, y + i.cable_mouth / 2, min(zc, z_tip + s), max(zc, z_tip + s))
    return block.cut([bore, mouth])


def stadium(x: float, y: float, z: float, r: float, half: float) -> Part.Wire:
    """A slot outline in the plane z: two half circles of r, their centres `half` each side of x."""
    a, b = V(x - half, y - r, z), V(x + half, y - r, z)
    c, e = V(x + half, y + r, z), V(x - half, y + r, z)
    return Part.Wire([Part.LineSegment(a, b).toShape(), Part.Arc(b, V(x + half + r, y, z), c).toShape(),
                      Part.LineSegment(c, e).toShape(), Part.Arc(e, V(x - half - r, y, z), a).toShape()])


# ---------- the push bolt (PushBolt; moved from panel_latch, where the study keeps its other candidates) ----------

def side_prism(pts: list[tuple[float, float]], x0: float, x1: float) -> Part.Shape:
    """A profile in (y, z) at x0, extruded to x1."""
    w = Part.makePolygon([V(x0, y, z) for y, z in pts] + [V(x0, *pts[0])])
    return Part.Face(w).extrude(V(x1 - x0, 0, 0))


def xcyl(r: float, x0: float, x1: float, y: float, z: float) -> Part.Shape:
    return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def ycyl(d: float, y0: float, y1: float, x: float, z: float) -> Part.Shape:
    return Part.makeCylinder(d / 2, y1 - y0, V(x, y0, z), V(0, 1, 0))


def pivot(d: Blueprint, i: Interface) -> tuple[float, float]:
    """The axis of the swing (along x): the rear top edge of the plate."""
    return pr.panel_outline(d, -i.seat_gap)[4][1], d.panel_top


def rear_bar_face(d: Blueprint, i: Interface) -> float:
    """y of the inner face of the rear bar of the frame (the opening less the bond gap)."""
    return opening(d, i, i.bond_gap)[4][1]


def front_bar_face(d: Blueprint, i: Interface) -> float:
    return opening(d, i, i.bond_gap)[1][1]


def bar_z(d: Blueprint, i: Interface) -> tuple[float, float]:
    z1 = z_rest(d) - d.wall_t - i.bond_gap
    return z1 - i.bar_h, z1


def hook(d: Blueprint, i: Interface, x: float, p: PushBolt = PB0) -> Part.Shape:
    """A hook under the rear edge of the plate: a stem and a toe. The top and the bottom of the toe are arcs about the
    pivot, so that the toe slides out of the notch when the front of the panel goes up."""
    yp, zp = pivot(d, i)
    face = rear_bar_face(d, i)
    zr = z_rest(d)
    r_in = math.hypot(yp - (face - i.bond_gap), zp - p.notch_top) + p.toe_clear
    tip = face + p.notch_back - p.toe_tip_gap
    stem_y1 = face - p.stem_gap
    x0, x1 = x - p.hook_w / 2, x + p.hook_w / 2
    ring = xcyl(p.toe_r_out, x0, x1, yp, zp).cut(xcyl(r_in, x0 - 1, x1 + 1, yp, zp))
    toe = ring.common(box(x0, x1, stem_y1 - p.stem_t, tip, zp - p.toe_r_out - 1, zr))
    # the stem goes down to the bottom arc of the toe at the stem's rear face, so that no narrow strip of its lower
    # face is left beside the toe
    z_low = zp - math.sqrt(p.toe_r_out ** 2 - (yp - stem_y1) ** 2)
    stem = box(x0, x1, stem_y1 - p.stem_t, stem_y1, z_low, zr)
    return one_solid(so.unsplit(stem.fuse(toe)), "rear hook")


def notches(d: Blueprint, i: Interface, p: PushBolt = PB0) -> list[Part.Shape]:
    """The notches in the rear bar of the frame that take the toes: open at the bottom and at the front."""
    face = rear_bar_face(d, i)
    z0, _ = bar_z(d, i)
    w = p.hook_w / 2 + p.notch_side
    return [box(x - w, x + w, face - 1, face + p.notch_back, z0 - 1, p.notch_top) for x in (-p.hook_x, p.hook_x)]


def band_y(z: float, d: Blueprint) -> float:
    """y of the front face of the deck at height z, at the centre line (upright to the crease, then the band leans)."""
    crease = d.deck_top - d.deck_lean_h
    return max(0.0, (z - crease) * math.tan(math.radians(d.deck_lean)))


def bolt(d: Blueprint, p: PushBolt = PB0, s: float = 0.0) -> Part.Shape:
    """The push bolt, moved back by s: a bar along y with a flush button at its front, a neck (where the lips of the
    strike pass when it is released), the lock section with the wedge under it, a stop block and a bore for its
    spring at the rear. The underside of the lock section falls wedge_deg toward the rear over the lips: the spring
    pushes the bolt forward, and the wedge pulls the strike (and the panel) down."""
    z0, z1 = p.bolt_z
    hw = p.bolt_w / 2
    neck0, neck1 = neck(p)
    yw1 = wedge_end(p)
    head_y1 = 10.0
    # the button: the outline of the hole moved in by button_gap (button_outline), cut by the plane of the leaning
    # band of the front face. Its flats are bolt_w apart, so that the bolt lies flat on its side on the printer
    t = math.tan(math.radians(d.deck_lean))
    crease = d.deck_top - d.deck_lean_h
    head = button_outline(d, p).translated(V(0, -5.0, 0)).extrude(V(0, head_y1 + 5.0, 0))
    outside = side_prism([(-20.0, crease - 40.0), (-20.0, crease + 60.0), (60.0 * t, crease + 60.0), (-40.0 * t, crease - 40.0)],
                         -20.0, 20.0)
    head = so.unsplit(head.cut(outside))
    # the lower face of the front of the bar starts where the flats of the button end (above z0 by 0.04), so that the
    # side of the bar and the flat of the button are one face with a straight lower edge
    r, fx, c = d.latch_button_d / 2, d.latch_button_flats / 2, so.LATCH_CORNER
    flat_low = d.latch_button_z - math.sqrt((r - c) ** 2 - (fx - c) ** 2)
    front = box(-hw, hw, head_y1 - 1, neck0 + 0.5, max(z0, flat_low), z1)
    narrow = box(-p.neck_w / 2, p.neck_w / 2, neck0, neck1, under(p, neck1), z1)
    lock = side_prism([(neck1, under(p, neck1)), (yw1, z0), (p.bolt_end_y, z0), (p.bolt_end_y, z1), (neck1, z1)], -hw, hw)
    # the stop block stands out on the +x side only: the -x side of the bolt is one plane, which lies on the bed
    stop = box(-hw, p.stop_w / 2, p.stop_y, p.stop_y + p.stop_l, z0, z1)
    solid = so.unsplit(head.fuse([front, narrow, lock, stop]))
    bore = ycyl(p.bolt_spring_bore, p.bolt_end_y - 10.0, p.bolt_end_y + 1, 0.0, (z0 + z1) / 2)
    solid = one_solid(solid.cut(bore), "push bolt")
    return break_front(solid, d).translated(V(0, s, 0))


def button_outline(d: Blueprint, p: PushBolt = PB0) -> Part.Face:
    """The outline of the button in the plane y = 0: the outline of its hole in the deck (solids.latch_button_hole: a
    round of latch_button_d, two flats latch_button_flats apart, the four corners rounded by solids.LATCH_CORNER) moved
    in by button_gap. Thus the gap round the button is button_gap all round, also at the corners (their rounds are
    concentric), and the button's corners (LATCH_CORNER less button_gap) are larger than the edge break of its rim."""
    r, fx, z = d.latch_button_d / 2, d.latch_button_flats / 2, d.latch_button_z
    prism = Part.makeCylinder(r, 1.0, V(0, 0, z), V(0, 1, 0)).common(box(-fx, fx, 0.0, 1.0, z - r - 1.0, z + r + 1.0))
    corners = [e for e in prism.Edges if abs(e.BoundBox.YLength - 1.0) < 1e-6 and e.BoundBox.XLength < 1e-6 and e.BoundBox.ZLength < 1e-6
               and abs(abs(e.BoundBox.XMin) - fx) < 1e-6]
    prism = prism.makeFillet(so.LATCH_CORNER, corners)
    face = next(f for f in prism.Faces if isinstance(f.Surface, Part.Plane) and abs(f.CenterOfMass.y) < 1e-6)
    out = face.makeOffset2D(-p.button_gap)
    return out if out.ShapeType == "Face" else out.Faces[0]


def neck(p: PushBolt = PB0) -> tuple[float, float]:
    """The neck of the bolt at the lock: it holds the lug with neck_margin at each end when the bolt is back by the
    stroke."""
    y0, y1 = p.lug_y
    return y0 - p.neck_front - p.stroke, y1 + p.neck_margin - p.stroke


def wedge_end(p: PushBolt = PB0) -> float:
    return p.lug_y[1] + p.neck_margin + 0.5


def under(p: PushBolt, y: float) -> float:
    """z of the underside of the bolt's lock section at y (the bolt at the lock)."""
    w = math.tan(math.radians(p.wedge_deg))
    return p.bolt_z[0] + w * max(0.0, wedge_end(p) - y)


def break_front(solid: Part.Shape, d: Blueprint) -> Part.Shape:
    """The edge break on the rim of the button: the only edge of the bolt that shows."""
    rim = [e for e in solid.Edges if not e.Degenerated and e.BoundBox.YMax < 4.0 and len(solid.ancestorsOfType(e, Part.Face)) == 2]
    for r in (d.edge_break, 0.8, 0.6):
        try:
            out = solid.makeFillet(r, rim)
            if out.isValid():
                return out
        except Part.OCCError:
            continue
    return solid


def strike(d: Blueprint, i: Interface, p: PushBolt = PB0) -> Part.Shape:
    """The strike under the front edge of the panel, at the centre: two legs that stand each side of the bolt, a bridge
    above it, and a lip on each leg that reaches in under the bolt. The top of each lip is parallel to the wedge
    under the bolt, bolt_clear below it."""
    z0, z1 = p.bolt_z
    hw = p.bolt_w / 2 + p.bolt_clear
    y0, y1 = p.lug_y
    zr = z_rest(d)
    outer = box(-hw - p.lug_leg_t, hw + p.lug_leg_t, y0, y1, p.lug_z0, zr)
    window = side_prism([(y0 - 1, under(p, y0 - 1) - p.bolt_clear), (y1 + 1, under(p, y1 + 1) - p.bolt_clear), (y1 + 1, z1 + p.bolt_clear), (y0 - 1, z1 + p.bolt_clear)], -hw, hw)
    slot = box(-(p.bolt_w / 2 - p.lug_lip), p.bolt_w / 2 - p.lug_lip, y0 - 1, y1 + 1, p.lug_z0 - 1, z1)
    return one_solid(so.unsplit(outer.cut([window, slot])), "strike")


def tunnel(d: Blueprint, i: Interface, p: PushBolt = PB0) -> Part.Shape:
    """The tunnel of the bolt, a part of the left half of the frame: a floor under the bolt from the front bar to the
    rear of the tunnel (in the plane of the lower face of the bar), with a window round the strike; two walls and a
    roof round the bolt behind the strike; a shoulder in the right wall that stops the stop block of the bolt; a slot
    for the gate at the rear. The walls stand back on the right from the shoulder to the rear, so that the bolt goes
    in from the rear."""
    fz0, _ = bar_z(d, i)
    fz1 = p.bolt_z[0] - p.bolt_clear
    ya, yb = p.housing_y
    hw, tw = p.housing_w / 2, p.tunnel_w / 2
    bw = p.bolt_w / 2 + p.bolt_clear
    sw = p.stop_w / 2 + p.bolt_clear
    rz0, rz1 = p.roof_z
    y_walls = p.lug_y[1] + 1.5
    ch0 = p.stop_y - 0.3
    floor = box(-hw, hw, ya, yb, fz0, fz1)
    walls = [box(-tw, -bw, y_walls, yb, fz1, rz0), box(bw, tw, y_walls, ch0, fz1, rz0), box(sw, tw, ch0, yb, fz1, rz0)]
    roof = box(-tw, tw, y_walls, yb, rz0, rz1)
    solid = joined([floor, *walls, roof])
    g = p.strike_window
    sb = strike(d, i, p).BoundBox
    window = box(sb.XMin - g, sb.XMax + g, sb.YMin - g - 0.5, sb.YMax + g + 0.5, fz0 - 1, fz1 + 1)
    c = p.gate_slot_clear
    slot = box(p.gate_x[0] - c, p.gate_x[1] + c, p.gate_y[0] - c, p.gate_y[1] + c, fz1, rz1 + 1)
    return so.unsplit(solid.cut([window, slot]))


def gate(p: PushBolt = PB0) -> Part.Shape:
    """The gate: a plate dropped into the slot at the rear of the tunnel. The spring of the bolt pushes it back
    against the rear face of the slot. Its top stands gate_tab above the roof for the fingers; the plate of a seated
    panel stands above it, so it cannot leave its slot while a panel is in."""
    z0, z1 = p.bolt_z
    g = box(p.gate_x[0], p.gate_x[1], p.gate_y[0], p.gate_y[1], z0, p.roof_z[1] + p.gate_tab)
    # a peg on its front face that the end of the spring goes over
    peg = ycyl(3.0, p.gate_y[0] - 4.0, p.gate_y[0] + 0.5, 0.0, (z0 + z1) / 2)
    return one_solid(so.unsplit(g.fuse(peg)), "gate")


def springs(p: PushBolt = PB0, s: float = 0.0) -> dict[str, Part.Shape]:
    """The bought spring of the bolt as a plain cylinder, for the pictures: between the bore of the bolt and the seat
    in the gate."""
    z0, z1 = p.bolt_z
    return {"bolt_spring": ycyl(p.bolt_spring_d, p.bolt_end_y - 10.0 + s, p.gate_y[0], 0.0, (z0 + z1) / 2)}


def spring_length(p: PushBolt = PB0, s: float = 0.0) -> float:
    return p.gate_y[0] - (p.bolt_end_y - 10.0 + s)


def front_notch(d: Blueprint, i: Interface, p: PushBolt = PB0) -> Part.Shape:
    """The bolt passes the front bar of the frame through a notch above the floor of the tunnel."""
    _, z1 = bar_z(d, i)
    hw = p.bolt_w / 2 + 1.0
    return box(-hw, hw, front_bar_face(d, i) - 12, front_bar_face(d, i) + 1, p.bolt_z[0] - p.bolt_clear, z1 + 1)


def bolt_room(p: PushBolt = PB0) -> Part.Shape:
    """What the push bolt takes from the room below the plate: the box of the tunnel, the gate and the travel of the
    bolt, with 0.5 round it and room_rear behind it. A panel keeps clear of it, but for its strike."""
    g = 0.5
    hw = p.housing_w / 2 + g
    return box(-hw, hw, p.housing_y[0], p.housing_y[1] + p.room_rear, 48.8 - g, 65.0)


def finger_hole(d: Blueprint, tiles: dict[str, Part.Shape], p: PushBolt = PB0) -> dict[str, Part.Shape]:
    """A finger hole through the plate of a panel with nothing to hold, with the edge break round both of its rims."""
    x, yl, dia = p.finger_hole
    y = y0(d) + yl
    zr, zt = z_rest(d), d.panel_top
    out = {}
    for name, tile in tiles.items():
        b = tile.BoundBox
        if not (b.XMin < x < b.XMax):
            out[name] = tile
            continue
        cut = one_solid(so.unsplit(tile.cut(cyl(dia, x, y, zr - 1, zt + 1))), name)
        rims = [e for e in cut.Edges if not e.Degenerated and abs(e.BoundBox.Center.x - x) < 1e-3 and abs(e.BoundBox.Center.y - y) < 1e-3
                and (abs(e.BoundBox.ZMin - zt) < 1e-6 or abs(e.BoundBox.ZMin - zr) < 1e-6) and abs(e.BoundBox.ZMax - e.BoundBox.ZMin) < 1e-6]
        out[name] = one_solid(cut.makeFillet(d.edge_break, rims), f"{name}, with the finger hole")
    return out


def add_to_tiles(tiles: dict[str, Part.Shape], add: list[Part.Shape], cut: list[Part.Shape]) -> dict[str, Part.Shape]:
    """Fuse each added solid to the tile that holds its middle (a solid across the seam is split at it), and cut."""
    names = list(tiles)
    seam = tiles[names[0]].BoundBox.XMax
    out = {}
    for k, name in enumerate(names):
        tile = tiles[name]
        half = box(-so.BIG, seam, -so.BIG, so.BIG, -so.BIG, so.BIG) if k == 0 else box(seam, so.BIG, -so.BIG, so.BIG, -so.BIG, so.BIG)
        parts = [s.common(half) for s in add]
        parts = [s for s in parts if s.Volume > 1e-6]
        if cut:
            tile = tile.cut(cut)
        if parts:
            tile = so.unsplit(tile.fuse(parts))
        out[name] = one_solid(tile, name)
    return out


# ---------- the way out of a panel with the push bolt ----------

@dataclass(frozen=True)
class Step:
    """One position of the way out: the latch moved (the bolt back by `bolt`; panel_latch also turns its cams by
    `cam`), the panel turned by `swing` degrees about the pivot (its front up), then moved by `lift` (y, z)."""
    name: str
    bolt: float = 0.0
    cam: float = 0.0
    swing: float = 0.0
    lift: tuple = (0.0, 0.0)


def way_out(p: PushBolt = PB0) -> list[Step]:
    """The way out with the push bolt: the button in, the front of the panel up about its rear top edge, then up and
    forward."""
    pre = [Step(f"bolt back {s:g}", bolt=s) for s in (1.0, 2.5, p.stroke)]
    swing = [Step(f"front up {a:g} degrees", bolt=p.stroke, swing=a) for a in (1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 13.0, 16.0, 20.0)]
    out = [Step(f"up and forward {k}", bolt=p.stroke, swing=20.0, lift=(-2.0 * k, 6.0 * k)) for k in (1, 2, 4, 8, 16)]
    return [Step("seated")] + pre + swing + out


def placed(shape: Part.Shape, st: Step, d: Blueprint, i: Interface) -> Part.Shape:
    """A part of the panel at a step: turned about the pivot, then moved."""
    out = shape
    if st.swing:
        yp, zp = pivot(d, i)
        # the front (smaller y) goes up: a turn about +x by -swing
        out = out.rotated(V(0, yp, zp), V(1, 0, 0), -st.swing)
    if st.lift != (0.0, 0.0):
        out = out.translated(V(0, *st.lift))
    return out


def way_out_rows(d: Blueprint, i: Interface, panel: dict[str, Part.Shape], hw: Hardware | None, frame: dict[str, Part.Shape],
                 fixed: dict[str, Part.Shape], skin: Part.Shape, p: PushBolt | None = None) -> list[dict]:
    """The real way out in steps (way_out): at each step the common volume of the moving group (the panel with its
    hardware) with what stays (the skin of the deck, the frame, the gate, the bolt where it is). Then the bolt alone
    at four places of its travel against the deck, the frame and the gate, and the bolt back by the stroke against the
    seated panel. FAIL above TOL."""
    p = p or i.push
    moving = [*panel.values(), *([s.world for s in hw.solids(("Panel",), ("hardware", "protrusion"))] if hw else [])]
    still = [skin, *frame.values(), *fixed.values()]
    rows = []
    for st in way_out(p):
        group = Part.makeCompound([placed(s, st, d, i) for s in moving])
        vol = sum(common_volume(group, s) for s in [*still, bolt(d, p, st.bolt)])
        rows.append({"step": st.name, "swing": st.swing, "lift": list(st.lift), "bolt": st.bolt, "cam": st.cam,
                     "common_mm3": round(vol, 3), "result": "FAIL" if vol > TOL else "PASS"})
    for s in (0.0, 1.0, 2.5, p.stroke):
        vol = sum(common_volume(bolt(d, p, s), x) for x in still)
        rows.append({"step": f"the bolt alone, back {s:g}, against the deck, the frame and the gate", "bolt": s, "common_mm3": round(vol, 3),
                     "result": "FAIL" if vol > TOL else "PASS"})
    vol = common_volume(bolt(d, p, p.stroke), Part.makeCompound(list(panel.values())))
    rows.append({"step": "the bolt back by the stroke, against the seated panel", "bolt": p.stroke, "common_mm3": round(vol, 3),
                 "result": "FAIL" if vol > TOL else "PASS"})
    return rows


def locked_rows(d: Blueprint, i: Interface, frame: dict[str, Part.Shape], p: PushBolt | None = None) -> list[dict]:
    """The lock really holds: with the bolt forward, a lift of 1 makes the toes of the hooks meet the roofs of their
    notches, and a swing of 2 degrees makes the lips of the strike meet the bolt. A row FAILS when the panel could
    leave without the button."""
    p = p or i.push
    halves = Part.makeCompound([frame["frame_left"], frame["frame_right"]])
    up = Step("lift 1", lift=(0.0, 1.0))
    vol = sum(common_volume(placed(hook(d, i, x, p), up, d, i), halves) for x in (-p.hook_x, p.hook_x))
    rows = [{"what": "rear hooks: a straight lift of 1 meets the roofs of the notches", "common_mm3": round(vol, 3), "result": "PASS" if vol > TOL else "FAIL"}]
    vol = common_volume(placed(strike(d, i, p), Step("swing 2", swing=2.0), d, i), bolt(d, p))
    rows.append({"what": "bolt locked: a swing of 2 degrees makes the lips meet the bolt", "common_mm3": round(vol, 3), "result": "PASS" if vol > TOL else "FAIL"})
    return rows


# ---------- the frame ----------

def frame(d: Blueprint, i: Interface) -> dict[str, Part.Shape]:
    """The frame: its left half and its right half, and the four posts. The bar lies under the ledge, bond_gap
    below it; the pads rise inside the opening to pad_drop below the rest face."""
    zr = z_rest(d)
    z1 = zr - d.wall_t - i.bond_gap
    z0 = z1 - i.bar_h
    top = zr - i.pad_drop
    inside = opening(d, i, i.bond_gap)
    hole = plan(inside, z0 - 1, top + 1)
    ring = plan(pr.panel_outline(d, -i.bar_in), z0, z1).cut(hole)
    lands = plan(inside, z0, top)
    pads = [lands.common(cyl(2 * i.pad_r, *p, z0, top)) for p, _ in corners(d, i, i.bond_gap)]
    y_edge = inside[4][1]
    pads += [lands.common(cyl(2 * i.cone_pad_r, x, y_edge, z0, top)) for x, _ in cone_points(d, i)]
    cones = [Part.makeCone(i.cone_d / 2, i.cone_top_d / 2, i.cone_h, V(x, y, top), V(0, 0, 1)) for x, y in cone_points(d, i)]
    anchor = clip(i.anchor_x, y_edge - i.clip_w / 2, z0, i, up=True)
    solid = joined([ring, *pads, *cones, anchor])
    cuts = []
    for x, y in latch_points(d, i):
        if i.latch == SCREW:
            cuts.append(cyl(i.insert_hole_d, x, y, top - i.latch_hole_depth, top + 1))
        else:
            cuts.append(cyl(i.magnet_d + i.magnet_clear, x, y, top - i.pad_magnet_h() - i.magnet_clear, top + 1))
    g = i.half_gap / 2
    if i.latch == PUSH_BOLT:
        # the notches of the rear hooks; the halves meet at frame_split_x, so that the tunnel of the bolt is whole in
        # the left half, with the notch of the bolt in the front bar
        p = i.push
        solid = so.unsplit(solid.cut(cuts + notches(d, i, p)))
        left = so.unsplit(solid.common(box(-so.BIG, p.frame_split_x - g, -so.BIG, so.BIG, 0, 200)))
        left = so.unsplit(left.cut(front_notch(d, i, p)).fuse(tunnel(d, i, p)))
        out = {"frame_left": one_solid(left, "frame, left half, with the tunnel of the bolt"),
               "frame_right": one_solid(so.unsplit(solid.common(box(p.frame_split_x + g, so.BIG, -so.BIG, so.BIG, 0, 200))), "frame, right half")}
    else:
        solid = solid.cut(cuts)
        out = {"frame_left": one_solid(solid.common(box(-so.BIG, -g, -so.BIG, so.BIG, 0, 200)), "frame, left half"),
               "frame_right": one_solid(solid.common(box(g, so.BIG, -so.BIG, so.BIG, 0, 200)), "frame, right half")}
    floor = fit.Layout().floor_t
    front, rear = pr.panel_outline(d, -i.bar_in)[1][1], pr.panel_outline(d, -i.bar_in)[4][1]
    w = i.ledge + i.bond_gap - i.bar_in
    for name, x, ya in (("post_front_left", -i.post_x, front), ("post_front_right", i.post_x, front),
                        ("post_rear_left", -i.post_x, rear - w), ("post_rear_right", i.post_x, rear - w)):
        out[name] = box(x - i.post_w / 2, x + i.post_w / 2, ya + 0.1, ya + w - 0.1, floor, z0 - i.bond_gap)
    return out


# ---------- a panel on the interface ----------

def plate(d: Blueprint, i: Interface) -> Part.Shape:
    return plan(pr.panel_outline(d, -i.seat_gap), z_rest(d), d.panel_top)


def interface_cuts(d: Blueprint, i: Interface) -> list[Part.Shape]:
    """What the interface takes out of every panel: the latch (the screw holes with their countersinks, or the
    pockets of the thin magnets) and the two sockets of the locating cones."""
    zr, zt = z_rest(d), d.panel_top
    cuts = []
    for x, y in latch_points(d, i):
        if i.latch == SCREW:
            depth = (i.screw_head_d - i.screw_hole_d) / 2
            cuts += [cyl(i.screw_hole_d, x, y, zr - 1, zt + 1),
                     Part.makeCone(i.screw_hole_d / 2, i.screw_head_d / 2, depth, V(x, y, zt - depth), V(0, 0, 1))]
        else:
            cuts.append(cyl(i.magnet_d + i.magnet_clear, x, y, zr - 1, zr + i.keeper_h + i.magnet_clear))
    (xa, ya), (xb, yb) = cone_points(d, i)
    c, h = i.cone_clear, i.cone_h + 2 * i.cone_clear
    r0, r1 = i.cone_d / 2 + c, i.cone_top_d / 2 + c
    cuts.append(Part.makeCone(r0, r1, h, V(xa, ya, zr), V(0, 0, 1)))
    cuts.append(Part.makeLoft([stadium(xb, yb, zr, r0, i.cone_slot), stadium(xb, yb, zr + h, r1, i.cone_slot)], True, True))
    return cuts


def long_ribs(d: Blueprint, i: Interface, x0: float, x1: float, rear_x0: float | None = None) -> list[Part.Shape]:
    """The rib along the front edge and the rib along the rear edge, between x0 and x1 (the rear one from rear_x0)."""
    zr = z_rest(d)
    return [box(x0, x1, y0(d) + i.rib_front_yl, y0(d) + i.rib_front_yl + i.rib_t, zr - i.rib_h, zr),
            box(x0 if rear_x0 is None else rear_x0, x1, y0(d) + i.rib_rear_yl, y0(d) + i.rib_rear_yl + i.rib_t, zr - i.rib_h, zr)]


def seam_ribs(d: Blueprint, i: Interface, x: float) -> Part.Shape:
    """The two flanges of a seam at x, as one rib from the front rib to the rear rib."""
    zr = z_rest(d)
    return box(x - i.seam_flange_t, x + i.seam_flange_t, y0(d) + i.rib_front_yl, y0(d) + i.rib_rear_yl + i.rib_t, zr - i.rib_h, zr)


def seam_holes(d: Blueprint, i: Interface, x: float, at_yl: tuple[float, ...]) -> list[Part.Shape]:
    z = z_rest(d) - i.seam_screw_z
    return [Part.makeCylinder(i.seam_screw_d / 2, 2 * i.seam_flange_t + 2, V(x - i.seam_flange_t - 1, y0(d) + yl, z), V(1, 0, 0)) for yl in at_yl]


def panel_clip(d: Blueprint, i: Interface) -> Part.Shape:
    return clip(i.clip_x, y0(d) + i.clip_yl, z_rest(d), i, up=False)


def on_outline(points: list[P2], p: App.Vector, tol: float = 1e-4) -> bool:
    for a, b in zip(points, points[1:] + points[:1]):
        t = max(0.0, min(1.0, ((p.x - a[0]) * (b[0] - a[0]) + (p.y - a[1]) * (b[1] - a[1])) / math.dist(a, b) ** 2))
        if math.hypot(p.x - a[0] - t * (b[0] - a[0]), p.y - a[1] - t * (b[1] - a[1])) < tol:
            return True
    return False


def tiles(solid: Part.Shape, d: Blueprint, i: Interface, seam_x: float, names: tuple[str, str]) -> dict[str, Part.Shape]:
    """A panel cut at its seam into its two tiles, each with the edge break on the top edge of its outline (the
    edge that shows in the reveal). The four upright corners of the plate get the break first, so that the round
    of the top edge runs round each corner with no mitre. The two blunt corners of the front edge (deck_flank)
    stay as they are. The top edges at the seam stay sharp: the seam is bonded."""
    edge = pr.panel_outline(d, -i.seat_gap)
    upright = [edge[k] for k in (0, 3, 4, 5)]
    out = {}
    for name, part in zip(names, (box(-so.BIG, seam_x, -so.BIG, so.BIG, 0, 200), box(seam_x, so.BIG, -so.BIG, so.BIG, 0, 200))):
        tile = one_solid(so.unsplit(solid.common(part)), name)
        posts = so.edges_where(tile, lambda p: any(math.hypot(p.x - x, p.y - y) < 1e-4 for x, y in upright))
        tile = one_solid(tile.makeFillet(d.edge_break, posts), f"{name}, with its corners broken")
        rim = so.edges_where(tile, lambda p: abs(p.z - d.panel_top) < 1e-6 and on_outline(edge, p, d.edge_break / 2))
        out[name] = one_solid(tile.makeFillet(d.edge_break, rim), f"{name}, with the edge break")
    return out


# ---------- the arcade panel ----------

@dataclass(frozen=True)
class Holes:
    """Where the hardware of fit.Layout stands on the panel, in the cabinet frame."""
    lever: P2
    lever_mount: tuple[P2, ...]
    lever_plate: tuple[float, float, float, float]   # x0, x1, y0, y1
    lever_seat_z: float
    action: tuple[P2, ...]
    service: tuple[P2, ...]
    encoder: tuple[float, float, float, float]
    encoder_holes: tuple[P2, ...]
    encoder_z: float
    harness_x0: float
    body_x1: float


def holes(d: Blueprint, a: Arcade, v) -> Holes:
    """The positions from the parameter sheets and fit.Layout (fit.anchors sets the same values for the envelopes)."""
    lay = fit.Layout()
    ya = y0(d)
    sx, sy = lay.stick_x, ya + lay.stick_y_share * d.panel_d
    count = int(v("btn_count"))
    action = [(sx + v(f"btn{k}_dx"), sy + v(f"btn{k}_dy")) for k in range(1, count + 1)]
    if a.buttons == SPREAD:
        # about button 1, the button next to the seam of the tiles: its nut keeps its room to the seam's flange
        cx, cy = action[0]
        action = [(cx + a.spread * (x - cx), cy + a.spread * (y - cy)) for x, y in action]
    svc_x = d.panel_w / 2 - lay.svc_end_gap
    service = [(svc_x, ya + d.panel_d / 2 + (j - 1) * lay.svc_pitch) for j in range(3)]
    open_x = d.panel_w / 2 - cavity.Openings().panel_ledge
    ex, ey = -open_x + lay.enc_edge_gap + v("enc_w") / 2, ya + d.panel_d / 2
    return Holes(lever=(sx, sy),
                 lever_mount=tuple((sx + u * v("stick_mount_w") / 2, sy + w * v("stick_mount_l") / 2) for u in (-1, 1) for w in (-1, 1)),
                 lever_plate=(sx - v("stick_plate_w") / 2, sx + v("stick_plate_w") / 2, sy - v("stick_plate_l") / 2, sy + v("stick_plate_l") / 2),
                 lever_seat_z=d.panel_top - v("stick_plate_drop"), action=tuple(action), service=tuple(service),
                 encoder=(ex - v("enc_w") / 2, ex + v("enc_w") / 2, ey - v("enc_l") / 2, ey + v("enc_l") / 2),
                 encoder_holes=tuple((ex + u * a.enc_hole_x / 2, ey + w * a.enc_hole_y / 2) for u in (-1, 1) for w in (-1, 1)),
                 encoder_z=z_rest(d) - v("enc_standoff"), harness_x0=sx - v("stick_conn_clear"), body_x1=sx + v("stick_body_w") / 2)


def seam_x(a: Arcade) -> float:
    return fit.Layout().stick_x + a.seam_dx


def rib_left(i: Interface, h: Holes) -> tuple[float, float]:
    """The rib between the encoder and the harness of the lever: in the middle of the room between them."""
    m = (h.encoder[1] + h.harness_x0) / 2
    return m - i.rib_t / 2, m + i.rib_t / 2


def arcade(d: Blueprint, i: Interface, a: Arcade, v) -> dict[str, Part.Shape]:
    """The arcade panel as its two tiles: the lever tile and the button tile."""
    zr, zt, ya = z_rest(d), d.panel_top, y0(d)
    h = holes(d, a, v)
    xs = seam_x(a)
    rl0, rl1 = rib_left(i, h)
    z_rib = zr - i.rib_h
    y_f, y_r = ya + i.rib_front_yl, ya + i.rib_rear_yl + i.rib_t
    add = [plate(d, i), *long_ribs(d, i, -i.rib_end_x, i.rib_end_x, rear_x0=rl0), seam_ribs(d, i, xs),
           box(rl0, rl1, y_f, y_r, z_rib, zr),
           box(a.rib_right_x - a.rib_right_t / 2, a.rib_right_x + a.rib_right_t / 2, y_f, y_r, z_rib, zr),
           # the seat of the lever, from the rib at the left to the flange of the seam
           box(rl1, xs - i.seam_flange_t, h.lever_plate[2] - a.lever_margin, h.lever_plate[3] + a.lever_margin, h.lever_seat_z, zr),
           panel_clip(d, i)]
    add += [cyl(a.boss_d, x, y, h.encoder_z, zr) for x, y in h.encoder_holes]
    solid = joined(add)
    cuts = interface_cuts(d, i) + seam_holes(d, i, xs, a.seam_screws_yl)
    cuts.append(box(rl0 - 1, rl1 + 1, ya + a.gate_yl[0], ya + a.gate_yl[1], z_rib - 1, z_rib + a.gate_h))
    cuts.append(cyl(v("stick_shaft_hole_d"), *h.lever, h.lever_seat_z - 1, zt + 1))
    cuts += [cyl(v("stick_insert_d"), x, y, h.lever_seat_z - 1, h.lever_seat_z + v("stick_insert_depth")) for x, y in h.lever_mount]
    cuts += [cyl(a.boss_pilot_d, x, y, h.encoder_z - 1, h.encoder_z + a.boss_pilot_depth) for x, y in h.encoder_holes]
    for group, name in ((h.action, "btn_hole_d"), (h.service, "svc_hole_d")):
        for x, y in group:
            cuts.append(cyl(v(name) + a.hole_allow, x, y, zr - 1, zt + 1))
            if a.buttons == SNAP_IN:
                cuts.append(cyl(v(name) + a.hole_allow + 2 * a.seat_ring, x, y, zr - 1, zt - a.seat_t))
    return latch_on_panel(d, i, tiles(solid.cut(cuts), d, i, xs, ("panel_lever_tile", "panel_button_tile")))


def blank(d: Blueprint, i: Interface) -> dict[str, Part.Shape]:
    """A panel with no hardware, made from the interface only: the plate, the latch, the sockets, the cable clip,
    two long ribs, a seam on the centre line and a rib at a quarter of the width on each side."""
    zr, ya = z_rest(d), y0(d)
    y_f, y_r = ya + i.rib_front_yl, ya + i.rib_rear_yl + i.rib_t
    q = d.panel_w / 4
    add = [plate(d, i), *long_ribs(d, i, -i.rib_end_x, i.rib_end_x), seam_ribs(d, i, 0.0), panel_clip(d, i)]
    add += [box(x - i.seam_flange_t / 2, x + i.seam_flange_t / 2, y_f, y_r, zr - i.rib_h, zr) for x in (-q, q)]
    cuts = interface_cuts(d, i) + seam_holes(d, i, 0.0, (40.0, 70.0, 105.0, 135.0))
    out = latch_on_panel(d, i, tiles(joined(add).cut(cuts), d, i, 0.0, ("blank_left_tile", "blank_right_tile")))
    # a panel with nothing to hold lifts by a finger hole (PUSH_BOLT: the front edge must come up first)
    return finger_hole(d, out, i.push) if i.latch == PUSH_BOLT else out


def latch_on_panel(d: Blueprint, i: Interface, tiles: dict[str, Part.Shape]) -> dict[str, Part.Shape]:
    """PUSH_BOLT: the two rear hooks and the strike on the tiles of a panel, and the room of the bolt (bolt_room) cut
    from its ribs. A rib that crosses that room stops at it."""
    if i.latch != PUSH_BOLT:
        return tiles
    p = i.push
    return add_to_tiles(tiles, [*(hook(d, i, x, p) for x in (-p.hook_x, p.hook_x)), strike(d, i, p)], [bolt_room(p)])


# ---------- the deck and the hardware round the panel ----------

def deck_skin(d: Blueprint, log=print) -> Part.Shape:
    """The skin of the deck: the cached skin of the shell (split.build_modules makes it), cut to the deck. It is
    kept beside the skin, under the same fingerprint."""
    file = split.cache_dir() / f"deck-{split.fingerprint(d)}.bin"
    skin = Part.Shape()
    if file.exists():
        skin.importBinary(str(file))
        return skin
    source = split.skin_files(d)["body"]
    if not source.exists():
        raise RuntimeError(f"the skin of the shell is not in the cache ({source}): run candybar.shell.split first, or copy the cache")
    log("panel: cutting the deck from the cached skin")
    skin.importBinary(str(source))
    out = skin.common(box(-so.BIG, so.BIG, -so.OVER, d.foot_y + d.deck_under_body, -so.OVER, d.deck_top + so.OVER))
    out.exportBinary(str(file))
    return out


def pocket_skin(d: Blueprint, skin: Part.Shape, reach: float = 32.0) -> Part.Shape:
    """The skin of the deck round the pocket of the panel: what a part of the panel or of the frame can meet. The
    checks run on it, because a boolean with the whole deck takes much longer. It reaches to the front face of the
    deck, where the button of the push bolt stands in its hole."""
    pts = pr.panel_outline(d, reach)
    return skin.common(plan(pts, fit.Layout().floor_t - 1.0, d.deck_top + so.OVER))


def side_in(d: Blueprint, skin: Part.Shape, v) -> float:
    """X of the inner face of the deck's right side at the first USB socket (fit.place measures the same ray)."""
    lay = fit.Layout()
    y, z = fit.usb_row_start(d, lay, v), fit.usb_row_z(d)
    seg = Part.makeLine(V(d.width / 2 + 50, y, z), V(d.width / 2 - 50, y, z))
    xs = sorted((vx.Point.x for e in seg.common(skin).Edges for vx in e.Vertexes), reverse=True)
    return xs[1]


@dataclass
class Hardware:
    doc: App.Document
    base: App.Document
    items: list[fit.Item]

    def solids(self, groups: tuple[str, ...] = (), roles: tuple[str, ...] = ("hardware", "keepout", "protrusion")) -> list[model.Placed]:
        return [s for it in self.items if not groups or it.group in groups for s in it.solids if s.role in roles]

    def close(self) -> None:
        for doc in (self.doc, self.base):
            App.closeDocument(doc.Name)


def hardware(d: Blueprint, skin: Part.Shape, a: Arcade | None = None) -> Hardware:
    """The lever, the buttons, the encoder, the USB sockets and the hub, as fit.Layout places them: the envelopes
    and the keep-out zones of the fit study, with its anchors. With the spread layout of the buttons (Arcade) the
    envelopes of the action buttons stand at the spread places, where the holes are."""
    a = a or Arcade()
    base = fit.sheet(params.load(PARAMS), "PanelBase")
    v = lambda name: params.value(base, name)
    values = fit.anchors(d, fit.Layout(), v, side_in(d, skin, v))
    if a.buttons == SPREAD:
        lay = fit.Layout()
        sx, sy = lay.stick_x, y0(d) + lay.stick_y_share * d.panel_d
        for k, (x, y) in enumerate(holes(d, a, v).action, start=1):
            values[f"btn{k}_dx"], values[f"btn{k}_dy"] = x - sx, y - sy
    rows = fit.sheet_rows(PARAMS, values)
    doc = fit.sheet(rows, "PanelFit")
    m = model.Model(doc, [r.name for r in rows])
    for spec in (controls.control_panel(int(params.value(doc, "btn_count"))), fit.usb_row(), fit.HUB):
        m.assembly(spec)
    doc.recompute()
    return Hardware(doc, base, fit.items(doc))


def room(d: Blueprint, i: Interface, fr: dict[str, Part.Shape], hw: Hardware) -> Part.Shape:
    """The room below the plate that a panel can use (see Interface)."""
    zr = z_rest(d)
    z0 = fit.Layout().floor_t + i.room_floor_gap
    out = plan(opening(d, i, i.bond_gap + i.room_gap), z0, zr)
    grow = i.room_gap
    cuts = [cyl(2 * (i.pad_r + grow), *p, z0 - 1, zr + 1) for p, _ in corners(d, i, i.bond_gap)]
    y_edge = opening(d, i, i.bond_gap)[4][1]
    cuts += [cyl(2 * (i.cone_pad_r + grow), x, y_edge, z0 - 1, zr + 1) for x, _ in cone_points(d, i)]
    cuts.append(box(i.anchor_x - i.clip_l / 2 - grow, i.anchor_x + i.clip_l / 2 + grow, y_edge - i.clip_w - grow, y_edge + 1, z0 - 1, zr + 1))
    usb = Part.makeCompound([s.world for s in hw.solids(("USB",))]).BoundBox
    cuts.append(box(usb.XMin - i.usb_gap, so.BIG, -so.BIG, so.BIG, z0 - 1, usb.ZMax + i.usb_gap))
    if i.latch != PUSH_BOLT:
        return one_solid(out.cut(cuts), "the room below the plate")
    # PUSH_BOLT: less the box of the bolt, its tunnel and the gate (bolt_room); a panel takes in the two notches of the
    # hooks and the place of its strike
    p = i.push
    out = out.cut(cuts + [bolt_room(p)])
    below = box(-so.BIG, so.BIG, -so.BIG, so.BIG, -so.BIG, zr)
    sb = strike(d, i, p).BoundBox
    extra = [n.common(below) for n in notches(d, i, p)] + [box(sb.XMin, sb.XMax, sb.YMin, sb.YMax, sb.ZMin, sb.ZMax)]
    # the place of the strike is an island inside the room of the bolt: the room is two solids
    out = so.unsplit(out.fuse(extra))
    if not out.isValid():
        raise RuntimeError("the room below the plate: not a valid shape")
    return out


# ---------- the checks ----------

def common_volume(a: Part.Shape, b: Part.Shape) -> float:
    return a.common(b).Volume if a.BoundBox.intersect(b.BoundBox) else 0.0


def gap(a: Part.Shape, b: Part.Shape) -> float:
    return a.distToShape(b)[0]


def clash_rows(parts: dict[str, Part.Shape], skin: Part.Shape, hw: Hardware, which: tuple[str, ...] = ("Panel", "USB", "Hub")) -> list[dict]:
    """Each printed part against the skin of the deck, against every other printed part and against every solid of
    the hardware (envelopes, keep-out zones and what stands out of the panel): the common volume, and FAIL above
    TOL. For the hardware the row gives the largest common volume and the smallest gap of the group."""
    rows = []
    names = list(parts)
    for k, name in enumerate(names):
        vol = common_volume(parts[name], skin)
        rows.append({"part": name, "against": "skin of the deck", "common_mm3": round(vol, 3), "gap": None, "result": "FAIL" if vol > TOL else "PASS"})
        for other in names[k + 1:]:
            vol = common_volume(parts[name], parts[other])
            if parts[name].BoundBox.intersect(parts[other].BoundBox):
                rows.append({"part": name, "against": other, "common_mm3": round(vol, 3), "gap": None, "result": "FAIL" if vol > TOL else "PASS"})
        for group in which:
            solids = hw.solids((group,))
            worst = max(((common_volume(parts[name], s.world), s.name) for s in solids), default=(0.0, ""))
            near = [s for s in solids if gap_box(parts[name], s.world) < 30.0]
            nearest = min(((gap(parts[name], s.world), s.name) for s in near), default=(None, ""))
            rows.append({"part": name, "against": f"hardware: {group}", "common_mm3": round(worst[0], 3), "worst": worst[1],
                         "gap": None if nearest[0] is None else round(nearest[0], 2), "nearest": nearest[1],
                         "result": "FAIL" if worst[0] > TOL else "PASS"})
    return rows


def gap_box(a: Part.Shape, b: Part.Shape) -> float:
    """A lower bound of the distance between two shapes, from their boxes."""
    p, q = a.BoundBox, b.BoundBox
    return max(p.XMin - q.XMax, q.XMin - p.XMax, p.YMin - q.YMax, q.YMin - p.YMax, p.ZMin - q.ZMax, q.ZMin - p.ZMax, 0.0)


def room_rows(space: Part.Shape, d: Blueprint, fixed: dict[str, Part.Shape], skin: Part.Shape, hw: Hardware, panel: dict[str, Part.Shape]) -> list[dict]:
    """The room below the plate is free of the skin, the frame, the USB sockets and the hub; and the arcade panel
    with its hardware lies in the room (below the rest face) or above it."""
    rows = []
    for name, shape in [("skin of the deck", skin), *fixed.items(), *[(s.name, s.world) for s in hw.solids(("USB", "Hub"))]]:
        vol = common_volume(space, shape)
        if vol > 0 or name in fixed or name == "skin of the deck":
            rows.append({"what": f"room / {name}", "common_mm3": round(vol, 3), "result": "FAIL" if vol > TOL else "PASS"})
    below = box(-so.BIG, so.BIG, -so.BIG, so.BIG, -so.BIG, z_rest(d))
    for name, shape in [*panel.items(), *[(s.name, s.world) for s in hw.solids(("Panel",))]]:
        low = shape.common(below)
        out = low.Volume - low.common(space).Volume if low.Volume > 0 else 0.0
        rows.append({"what": f"{name} outside the room", "common_mm3": round(out, 3), "result": "FAIL" if out > TOL else "PASS"})
    return rows


def lift_rows(panel: dict[str, Part.Shape], hw: Hardware, fixed: dict[str, Part.Shape], skin: Part.Shape,
              steps: tuple[float, ...] = (3.0, 8.0, 16.0, 32.0, 64.0)) -> list[dict]:
    """The panel with its hardware (not the keep-out zones) lifted straight up: its common volume with the skin of
    the deck and the frame at each height."""
    moving = Part.makeCompound([*panel.values(), *[s.world for s in hw.solids(("Panel",), ("hardware", "protrusion"))]])
    still = [skin, *fixed.values()]
    rows = []
    for dz in steps:
        up = moving.translated(V(0, 0, dz))
        vol = sum(common_volume(up, s) for s in still)
        rows.append({"lift": dz, "common_mm3": round(vol, 3), "result": "FAIL" if vol > TOL else "PASS"})
    return rows


def tee(flange_w: float, seam_flange_t: float, web_t: float, web_h: float) -> float:
    """Second moment of area of a T section (the plate as the flange, a rib as the web) about its own centre, mm4."""
    af, aw = flange_w * seam_flange_t, web_t * web_h
    yf, yw = seam_flange_t / 2, seam_flange_t + web_h / 2
    c = (af * yf + aw * yw) / (af + aw)
    return flange_w * seam_flange_t ** 3 / 12 + af * (c - yf) ** 2 + web_t * web_h ** 3 / 12 + aw * (yw - c) ** 2


def stiffness(d: Blueprint, i: Interface, a: Arcade, v) -> dict:
    """Hand estimate of how the panel moves under the lever (ESTIMATED: beam theory, E of printed ABS).

    The load: lever_load sideways on the ball, lever_arm above the panel: a couple at the seat of the lever. The
    bay of the lever is the plate between the rib beside the encoder and the flanges of the seam. It spans from
    the front ledge to the rear ledge and rests on them (simply supported; the pad of the seat is not counted).
      forward or back   the couple bends the bay about X. The slope at the seat is M L / (12 E I), the largest
                        deflection M L^2 / (72 sqrt(3) E I)
      left or right     the couple loads the two ribs with +F and -F, F = M / s (s: between the ribs). Each rib is
                        a beam with half the bay as its flange: F L^3 / (48 E I). The seat turns by the sum over s
    The same without ribs is the flat plate of the bay. The hand: hand_load on the middle of the button field,
    a plate that rests on four sides (structure.plate_deflection)."""
    e = structure.E_ABS
    h = holes(d, a, v)
    rl0, rl1 = rib_left(i, h)
    xs = seam_x(a)
    span = d.panel_d - 2 * i.ledge
    bay = xs + i.seam_flange_t - rl0
    m = a.lever_load * a.lever_arm
    ball = v("stick_ball_cz") + d.panel_t / 2
    t = d.panel_t
    webs = (i.rib_t, 2 * i.seam_flange_t)
    af = bay * t
    aw = sum(webs) * i.rib_h
    c = (af * t / 2 + aw * (t + i.rib_h / 2)) / (af + aw)
    i_bay = bay * t ** 3 / 12 + af * (c - t / 2) ** 2 + sum(webs) * i.rib_h ** 3 / 12 + aw * (t + i.rib_h / 2 - c) ** 2
    i_flat = bay * t ** 3 / 12
    s = xs - (rl0 + rl1) / 2
    f = m / s
    ribs = [tee(bay / 2, t, w, i.rib_h) for w in webs]
    side_turn = sum(f * span ** 3 / (48 * e * ix) for ix in ribs) / s
    side_flat = 2 * (f * span ** 3 / (48 * e * i_flat / 2)) / s
    rows = {}
    for name, ix, side in (("with the ribs", i_bay, side_turn), ("flat plate of 5, no ribs", i_flat, side_flat)):
        slope = m * span / (12 * e * ix)
        rows[name] = {"I_bay_mm4": round(ix), "forward_slope_mrad": round(slope * 1e3, 2), "forward_deflection_mm": round(m * span ** 2 / (72 * math.sqrt(3) * e * ix), 3),
                      "forward_ball_mm": round(slope * ball, 3), "side_slope_mrad": round(side * 1e3, 2), "side_ball_mm": round(side * ball, 3)}
    field_a = a.rib_right_x - a.rib_right_t / 2 - (xs + i.seam_flange_t)
    short, long = sorted((span, field_a))
    hand = structure.plate_deflection(a.hand_load, short, long, t, e)
    arm = span
    return {"E_MPa": e, "load_N": a.lever_load, "arm_mm": a.lever_arm, "couple_Nmm": m, "span_mm": span, "bay_mm": round(bay, 2),
            "rib_spacing_mm": round(s, 2), "ball_above_plate_mm": round(ball, 2), "cases": rows,
            "hand": {"load_N": a.hand_load, "field_mm": [round(short, 1), round(long, 1)], "deflection_mm": round(hand, 2),
                     "per_10N_mm": round(hand * 10 / a.hand_load, 3)},
            "latch": {"lift_per_edge_N": round(m / arm, 1), "magnet_edge_N": 2 * i.magnet_pull(), "magnet_factor": round(2 * i.magnet_pull() / (m / arm), 2),
                      "magnet_lift_out_N": 4 * i.magnet_pull()}}


def overhang(shape: Part.Shape, up: App.Vector, limit: float = 45.0) -> float:
    """The area, mm2, of the faces that look down more than `limit` degrees from upright when `up` points up on the
    printer, without the faces on the bed."""
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05, AngularDeflection=0.1)
    n = V(up).normalize()
    bed = min(p.Vector.dot(n) for p in mesh.Points)
    cos = math.cos(math.radians(limit))
    area = 0.0
    for f in mesh.Facets:
        if f.Normal.dot(n) < -cos - 1e-6 and min(V(*p).dot(n) for p in f.Points) > bed + 0.01:
            area += f.Area
    return area


# how each part stands on the printer: the direction that points up, and the face on the bed
PRINT = {"tile": (V(0, 0, -1), "top face down: the face that shows lies on the bed, the ribs stand up"),
         "frame": (V(0, 0, 1), "as in the cabinet: the lower face of the bar on the bed, the pads and the cones stand up"),
         "post": (V(0, 1, 0), "on its wide side"),
         "latch_bolt": (V(1, 0, 0), "on its side: the flat side (x -6) on the bed"),
         "latch_gate": (V(0, -1, 0), "flat: its rear face on the bed, the peg up")}


def kind(name: str) -> str:
    return "post" if name.startswith("post") else "frame" if name.startswith("frame") else "latch" if name.startswith("latch") else "tile"


def print_rows(parts: dict[str, Part.Shape]) -> list[dict]:
    lim = split.printer()
    rows = []
    for name, shape in parts.items():
        up, how = PRINT[name if kind(name) == "latch" else kind(name)]
        # the points of a mesh, not the vertices: a round part has few vertices on its outline
        pts = [(p.x, p.y, p.z) for p in shape.tessellate(0.5)[0]]
        b = split.print_box(pts, (up.x, up.y, up.z), lim)
        low = min(vx.Point.dot(up) for vx in shape.Vertexes)
        bed = sum(f.Area for f in shape.Faces if isinstance(f.Surface, Part.Plane) and abs(f.CenterOfMass.dot(up) - low) < 1e-6
                  and abs(f.normalAt(0, 0).dot(up) + 1) < 1e-6)
        rows.append({"part": name, "how": how, "x": b["x"], "y": b["y"], "z": b["z"], "fits": b["fits"], "bed_cm2": round(bed / 100, 1),
                     "overhang_cm2": round(overhang(shape, up) / 100, 2), "mass_g": round(shape.Volume * ABS)})
    return rows


# an edge on the top face is hidden only where its other face is the wall of a hole or the bonded seam
HOLE_EDGE = 2.0
# the front of the button of the push bolt shows: from the front face of the deck (y 0 below the crease) to this y
SHOWN = 4.0
ON_TOP = ("the other tile", "panel_holes")


def covers(d: Blueprint, i: Interface) -> dict[str, Part.Shape]:
    """What the faces of these parts lie against, for the edge rule (tools/edge_finish.py): the seat of the plate
    in the pocket, the holes through the plate (the plate less HOLE_EDGE round its outline, so that the side of the
    plate is not a hole), and the room below the plate, inside the shell."""
    zr, zt = z_rest(d), d.panel_top
    seat = plan(pr.panel_outline(d), zr, zt).cut(plan(pr.panel_outline(d, -i.seat_gap), zr - 1, zt + 1))
    # the room starts SHOWN behind the front face of the deck: the front of the push bolt's button shows in its hole
    room = plan(pr.panel_outline(d, 30.0), 0.0, zr).common(box(-so.BIG, so.BIG, SHOWN, so.BIG, -so.BIG, so.BIG))
    return {"panel_seat": seat, "panel_holes": plan(pr.panel_outline(d, -i.seat_gap - HOLE_EDGE), zr, zt), "panel_room": room}


JOINTS = {"panel_seat": "The seat of the panel in the pocket: the side of the plate stands seat_gap from the wall of the seat. "
                        "The top edge of the side shows in the reveal, so the seat does not hide an edge on the top face.",
          "panel_holes": "A hole through the plate. The rim of a button, the dust washer of the lever or the head of a screw covers its top edge.",
          "panel_room": "Below the plate, inside the shell: the ribs, the frame, the bolt behind its button and the gate. These faces are not painted.",
          "the other tile": "The bonded seam between the two tiles of a panel."}


# the printed parts of this module, by name (tools/edge_finish.py puts them in its class of printed parts)
PARTS = ("frame_left", "frame_right", "post_front_left", "post_front_right", "post_rear_left", "post_rear_right",
         "panel_lever_tile", "panel_button_tile", "blank_left_tile", "blank_right_tile", "latch_bolt", "latch_gate")


def joints_of(name: str) -> tuple[str, ...]:
    """The covers of JOINTS that a part's faces lie against: the frame lies under the plate and in the room below
    it, a post, the bolt and the gate of the push bolt in that room; a tile in its seat, on the room, at the other tile, and (but a blank tile) round its
    holes."""
    k = kind(name)
    if k in ("post", "latch"):
        return ("panel_room",)
    if k == "frame":
        return ("panel_holes", "panel_room")
    return ("panel_room", "panel_seat", "the other tile") + (() if name.startswith("blank") else ("panel_holes",))


def twins(name: str, names) -> list[str]:
    """The other tile of the panel of a tile: the two tiles of a panel are bonded at their seam."""
    return [k for k in names if k != name and kind(k) == "tile" == kind(name) and k.split("_")[0] == name.split("_")[0]]


def corner_balls(d: Blueprint, i: Interface, tiles: tuple[str, ...]) -> list:
    """At each upright corner of a plate three breaks meet: the corner is a ball of R edge_break, as on the hood.
    The face check allows a narrow face of the break along an edge by itself; the ball is allowed by its place."""
    from tools import face_check  # noqa: PLC0415

    r = d.edge_break
    out = [face_check.Reveal("corner ball of the plate", tiles, ("sliver",), (x - 1.5 * r, y - 1.5 * r, d.panel_top - 1.5 * r, x + 1.5 * r, y + 1.5 * r, d.panel_top))
           for x, y in (pr.panel_outline(d, -i.seat_gap)[k] for k in (0, 3, 4, 5))]
    # the four corners of the button in plan (button_outline): each turns 31 degrees, so its round of LATCH_CORNER
    # less button_gap is a face about 0.7 wide along the button, with its piece of the edge break at the front
    z, h = d.latch_button_z, d.latch_button_d / 2
    out += [face_check.Reveal("corner of the button in plan", ("latch_bolt",), ("sliver",), (-h, -6.0, z - h, h, 11.0, z + h))]
    return out


def finish_rows(parts: dict[str, Part.Shape], d: Blueprint, i: Interface, log=lambda text: None) -> tuple[dict, list[str], dict]:
    """The edge rule and the face check on the printed parts, with the functions of the shell's tools
    (tools/edge_finish.py, tools/face_check.py). Every part here is a printed part. A convex edge that turns more
    than edge_break_turn and has no round passes only where one of its faces lies against a cover of JOINTS; on the
    top face of a panel, only in a hole or at the bonded seam (ON_TOP).
    Returns, for each part, its sharp edges by what they lie against and the number of faces of the edge break;
    the failures of both checks; and the summary of the face check."""
    from tools import edge_finish, face_check  # noqa: PLC0415 - the tools are not a package of the generator

    extra = covers(d, i)
    rows, bad = {}, []
    for name, shape in parts.items():
        # a tile lies against the other tile of its panel; the two panels stand in the same place, one at a time
        twin = {"the other tile": parts[k] for k in twins(name, parts)}
        others = {**twin, **extra}
        lies = {f.hashCode(): edge_finish.against(f, others, d) for f in shape.Faces}
        groups: dict[str, list] = {}
        for e in shape.Edges:
            fs = shape.ancestorsOfType(e, Part.Face)
            if e.Degenerated or len(fs) != 2:
                continue
            convex, turn = so.edge_turn(shape, e)
            if not convex or turn <= d.edge_break_turn:
                continue
            m = so.middle(e)
            hidden = [lies[f.hashCode()] for f in fs if lies[f.hashCode()]]
            if abs(m.z - d.panel_top) < 1e-6:
                hidden = [j for j in hidden if j in ON_TOP]
            joint = hidden[0] if hidden else ""
            groups.setdefault(joint, []).append((round(e.Length, 1), round(turn, 1), [round(m.x, 1), round(m.y, 1), round(m.z, 1)]))
        rows[name] = {"class": "printed", "break_faces": len([f for f in shape.Faces if face_check.is_break(f, d.edge_break)]),
                      "sharp": [{"against": j, "edges": len(es), "length": round(sum(e[0] for e in es), 1), "at": [e[2] for e in sorted(es, reverse=True)[:6]]}
                                for j, es in sorted(groups.items())]}
        for g in rows[name]["sharp"]:
            if not g["against"]:
                bad.append(f"edge rule: {name}: {g['edges']} sharp edges show ({g['length']} mm), the longest at {tuple(g['at'][0])}")
    log("face check")
    r = d.edge_break
    balls = corner_balls(d, i, tuple(k for k in parts if kind(k) == "tile"))
    found = []
    for name, shape in parts.items():
        found += face_check.check(shape, name, balls, break_radius=r)
    bad += [f"face check: {f.part}: {f.rule} at {f.at}: {f.detail}" for f in face_check.failures(found)]
    return rows, bad, face_check.summary(found)


# ---------- the build ----------

@dataclass
class Built:
    d: Blueprint
    i: Interface
    a: Arcade
    frame: dict[str, Part.Shape]
    arcade: dict[str, Part.Shape]
    blank: dict[str, Part.Shape]
    # PUSH_BOLT: the printed parts of the latch that stay in the cabinet and are not the frame: the bolt (at the lock)
    # and the gate
    latch: dict[str, Part.Shape] = field(default_factory=dict)

    @property
    def parts(self) -> dict[str, Part.Shape]:
        return {**self.frame, **self.arcade, **self.blank, **self.latch}

    @property
    def fixed(self) -> dict[str, Part.Shape]:
        """What stays in the cabinet when a panel comes out."""
        return {**self.frame, **self.latch}


def values(base: App.Document | None = None):
    base = base or fit.sheet(params.load(PARAMS), "PanelValues")
    return lambda name: params.value(base, name)


def build(d: Blueprint | None = None, i: Interface | None = None, a: Arcade | None = None, v=None) -> Built:
    d, i, a = d or Blueprint(), i or Interface(), a or Arcade()
    v = v or values()
    latch = {"latch_bolt": bolt(d, i.push), "latch_gate": gate(i.push)} if i.latch == PUSH_BOLT else {}
    return Built(d, i, a, frame(d, i), arcade(d, i, a, v), blank(d, i), latch)


def check(b: Built, skin: Part.Shape, hw: Hardware, v, log=lambda text: None) -> dict:
    """Every check of the package on the built parts. "failures" is empty when all pass. skin: pocket_skin."""
    d, i = b.d, b.i
    push = i.latch == PUSH_BOLT
    log("clashes")
    clashes = clash_rows({**b.fixed, **b.arcade}, skin, hw)
    # the blank panel has no hardware of its own: it is compared with the skin, the frame, the USB sockets and the hub
    clashes_blank = [r for r in clash_rows({**b.fixed, **b.blank}, skin, hw, ("USB", "Hub")) if r["part"].startswith("blank") or r["against"].startswith("blank")]
    log("room")
    space = room(d, i, b.frame, hw)
    # the bolt stands in the room of the bolt (bolt_room) behind the front bar and in the notch of that bar before it
    keep = {**b.frame, **{k: s for k, s in b.latch.items() if k != "latch_bolt"}}
    rooms = room_rows(space, d, keep, skin, hw, b.arcade) + [r for r in room_rows(space, d, {}, skin, hw, b.blank) if "blank" in r["what"]]
    log("way out" if push else "lift")
    # PUSH_BOLT: the way out with the button held (way_out_rows) for each panel, and the lock (locked_rows); the other
    # latches: a straight lift
    if push:
        lifts = way_out_rows(d, i, b.arcade, hw, b.frame, {"latch_gate": b.latch["latch_gate"]}, skin)
        lifts += [{**r, "step": f"blank panel: {r['step']}"} for r in way_out_rows(d, i, b.blank, None, b.frame, {"latch_gate": b.latch["latch_gate"]}, skin)]
        locks = locked_rows(d, i, b.frame)
    else:
        lifts, locks = lift_rows(b.arcade, hw, b.frame, skin), []
    held = None
    if push:
        log("hold (the estimates of panel_latch)")
        from . import panel_latch  # noqa: PLC0415 - the study imports this module
        held = panel_latch.default_hold(b, v)
    log("print")
    prints = print_rows(b.parts)
    log("edges and faces")
    edges, bad, faces = finish_rows(b.parts, d, i, log)
    failures = [f"clash: {r['part']} / {r['against']}: {r['common_mm3']} mm3" for r in clashes + clashes_blank if r["result"] == "FAIL"]
    failures += [f"room: {r['what']}: {r['common_mm3']} mm3" for r in rooms if r["result"] == "FAIL"]
    failures += [f"lift: at {r.get('step', r.get('lift'))} the panel meets the deck or the frame: {r['common_mm3']} mm3" for r in lifts if r["result"] == "FAIL"]
    failures += [f"lock: {r['what']}: {r['common_mm3']} mm3" for r in locks if r["result"] == "FAIL"]
    failures += [f"print: {r['part']} does not fit the printer ({r['x']} x {r['y']} x {r['z']})" for r in prints if not r["fits"]]
    failures += bad
    return {"interface": asdict(i), "arcade": asdict(b.a), "latch_points": latch_points(d, i), "cone_points": cone_points(d, i),
            "seam_x": seam_x(b.a), "room_volume_cm3": round(space.Volume / 1000, 1), "room_box": box_of(space),
            "clashes": clashes, "clashes_blank": clashes_blank, "room": rooms, "lift": lifts, "locks": locks, "hold": held, "print": prints,
            "stiffness": stiffness(d, i, b.a, v), "edge_finish": edges, "face_check": faces, "failures": failures}


def box_of(shape: Part.Shape) -> list[float]:
    bb = shape.BoundBox
    return [round(x, 2) for x in (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax)]


# ---------- the files ----------

def write_model(folder: Path, shapes: dict[str, tuple[Part.Shape, str]], edges: dict[str, Part.Shape] | None = None,
                focus: dict | None = None, extra_lines: dict[str, list] | None = None) -> None:
    """A model directory as candybar.shell.solids writes it: a mesh and a BREP file of each shape, manifest.json,
    edges.json (every BREP edge, for render_views.py) and focus.json (the cameras). `edges` gives another shape
    whose edges are drawn for a name (the outer form in place of the stepped skin)."""
    folder.mkdir(parents=True, exist_ok=True)
    manifest, lines = {}, {}
    for name, (shape, finish) in shapes.items():
        MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05, AngularDeflection=0.1).write(str(folder / f"{name}.stl"))
        shape.exportBrep(str(folder / f"{name}.brep"))
        manifest[name] = {"file": f"{name}.stl", "finish": finish, "brep": f"{name}.brep"}
        lines[name] = so.edge_polylines((edges or {}).get(name, shape)) + (extra_lines or {}).get(name, [])
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    (folder / "edges.json").write_text(json.dumps(lines), encoding="utf-8")
    (folder / "focus.json").write_text(json.dumps(focus or {}, indent=1), encoding="utf-8")


def finish_of(name: str) -> str:
    return FINISH["blank"] if name.startswith("blank") else FINISH[kind(name)]


def groups(hw: Hardware, which: tuple[str, ...] = ("Panel", "USB", "Hub")) -> dict[str, tuple[Part.Shape, str]]:
    """The hardware for a picture: what is solid (not the keep-out zones), by kind."""
    out: dict[str, list] = {}
    for it in hw.items:
        if it.group not in which:
            continue
        key = {"Panel": "Lever" if it.owner == "Lever" else "Encoder" if it.owner == "Encoder" else "Buttons"}.get(it.group, it.group)
        out.setdefault(key, []).extend(s.world for s in it.solids if s.role in ("hardware", "protrusion"))
    return {k: (Part.makeCompound(s), FINISH[k]) for k, s in out.items()}


def latch_hardware(d: Blueprint, i: Interface) -> dict[str, tuple[Part.Shape, str]]:
    """The bought parts of the latch, for the pictures: the screws and their inserts; or the magnets; or (PUSH_BOLT)
    the magnets in the frame, the steel discs in the plate and the spring of the bolt."""
    zr, zt = z_rest(d), d.panel_top
    top = zr - i.pad_drop
    if i.latch == PUSH_BOLT:
        pts = latch_points(d, i)
        p = i.push
        return {"magnets": (Part.makeCompound([cyl(i.magnet_d, x, y, top - i.magnet_clear - i.pad_magnet_h(), top - i.magnet_clear) for x, y in pts]), FINISH["magnet"]),
                "discs": (Part.makeCompound([cyl(i.magnet_d, x, y, zr, zr + i.keeper_h) for x, y in pts]), FINISH["magnet" if p.plate_disc != STEEL else "screw"]),
                "spring": (springs(p)["bolt_spring"], FINISH["spring"])}
    a, b = [], []
    for x, y in latch_points(d, i):
        if i.latch == SCREW:
            head = (i.screw_head_d - 0.4 - i.latch_screw_d) / 2
            a.append(Part.makeCone(i.latch_screw_d / 2, (i.screw_head_d - 0.4) / 2, head, V(x, y, zt - head), V(0, 0, 1))
                     .fuse(cyl(i.latch_screw_d, x, y, zt - i.latch_screw_l, zt - head)))
            b.append(cyl(i.insert_hole_d, x, y, top - i.insert_l, top).cut(cyl(i.latch_screw_d, x, y, top - i.insert_l - 1, top + 1)))
        else:
            a.append(cyl(i.magnet_d, x, y, zr, zr + i.keeper_h))
            b.append(cyl(i.magnet_d, x, y, top - i.magnet_clear - i.magnet_h, top - i.magnet_clear))
    if i.latch == SCREW:
        return {"screws": (Part.makeCompound(a), FINISH["screw"]), "inserts": (Part.makeCompound(b), FINISH["insert"])}
    return {"magnets": (Part.makeCompound(a + b), FINISH["magnet"])}


ON_PANEL = ("screws", "discs")    # the bought parts of a latch that go with the panel; the others stay in the frame


def latch_split(bought: dict[str, tuple[Part.Shape, str]]) -> tuple[dict, dict]:
    """The bought parts of a latch: those that go with the panel, and those that stay in the cabinet."""
    return {k: v for k, v in bought.items() if k in ON_PANEL}, {k: v for k, v in bought.items() if k not in ON_PANEL}


def cut_scene(shapes: dict[str, tuple[Part.Shape, str]], keep: Part.Shape, skin: Part.Shape | None, normal: App.Vector, at: float):
    """The shapes cut by a solid `keep`, and the outline of the skin in the cut plane as lines."""
    out = {k: (s.common(keep), f) for k, (s, f) in shapes.items()}
    out = {k: (s, f) for k, (s, f) in out.items() if s.Volume > 1e-3}
    lines = {}
    if skin is not None:
        lines["deck"] = [[[round(p.x, 3), round(p.y, 3), round(p.z, 3)] for p in w.discretize(Deflection=0.02)] for w in skin.slice(normal, at)]
    return out, lines


def cam(target, radius: float, az: float, el: float, aspect: float = 0.62) -> dict:
    return {"target": [round(c, 1) for c in target], "radius": radius, "az": az, "el": el, "aspect": aspect}


def scenes(out: Path, b: Built, skin: Part.Shape, hw: Hardware, options: dict[str, Built]) -> None:
    """The model directories of the pictures (tools/draw_panel.py renders them with every edge drawn). `b` is the
    default build; `options` the other latches by name (screw, magnet), for their sections."""
    d, i = b.d, b.i
    deck_outer = so.deck(d)[0]
    zt = d.panel_top
    mid = (0.0, y0(d) + d.panel_d / 2, zt)
    hard = groups(hw)
    fixed = {k: (s, finish_of(k)) for k, s in b.fixed.items()}
    panel = {k: (s, finish_of(k)) for k, s in b.arcade.items()}
    with_panel, in_frame = latch_split(latch_hardware(d, i))
    on_panel = {k: hard[k] for k in ("Lever", "Buttons", "Encoder")}
    # the printed floor is not a part of the shell's model yet: a slab of its thickness under the deck, for the pictures
    floor = deck_outer.common(box(-so.BIG, so.BIG, -so.BIG, so.BIG, 0.0, fit.Layout().floor_t))
    deck = {"deck": (skin, FINISH["deck"]), "floor": (floor, FINISH["floor"])}
    outer = {"deck": deck_outer}
    light = lambda shapes: {k: (s, FINISH["underside"]) for k, s in shapes.items()}
    views = {"above": cam(mid, 265, 0, 62), "above-left": cam(mid, 265, -38, 34)}
    write_model(out / "in-place", {**deck, **fixed, **panel, **on_panel, **with_panel}, outer, views)
    lift = V(0, 0, 95)
    moved = {k: (s.translated(lift), f) for k, (s, f) in {**panel, **on_panel, **with_panel}.items()}
    views = {"lifted": cam((0, mid[1], zt + 30), 300, -34, 30, 0.8), "frame": cam(mid, 265, 0, 58)}
    write_model(out / "lifted", {**deck, **fixed, **in_frame, "USB": hard["USB"], **moved}, outer, views)
    write_model(out / "frame", {**deck, **fixed, **in_frame, "USB": hard["USB"]}, outer,
                {"frame": cam(mid, 265, 0, 58), "frame-corner": cam((latch_points(d, i)[1][0] - 12, latch_points(d, i)[1][1] + 6, zt - 4), 48, 35, 40)})
    low = cam((0, mid[1], z_rest(d) - 6), 255, 180, -52)
    write_model(out / "underside", {**light(b.arcade), **on_panel}, None, {"underside": low, "underside-lever": cam((-95, mid[1], z_rest(d) - 8), 120, 150, -38)})
    blank = {k: (s, finish_of(k)) for k, s in b.blank.items()}
    views = {"above-left": cam(mid, 265, -38, 34)}
    if i.latch == PUSH_BOLT:
        x, yl, _ = i.push.finger_hole
        views["finger-hole"] = cam((x, y0(d) + yl, zt), 45, -25, 40, 0.7)
    write_model(out / "blank", {**deck, **fixed, **blank, **with_panel}, outer, views)
    write_model(out / "blank-underside", light(b.blank), None, {"underside": low})
    # the section through the lever: everything to the left of the lever's centre, seen from the right
    sx = fit.Layout().stick_x
    keep = box(-so.BIG, sx, -so.BIG, so.BIG, -so.BIG, so.BIG)
    everything = {**deck, **fixed, **panel, **on_panel, **with_panel, **in_frame}
    cut, lines = cut_scene(everything, keep, skin, V(1, 0, 0), sx)
    write_model(out / "section-lever", cut, None, {"section": cam((sx, y0(d) + d.panel_d / 2 - 4, 44), 122, 90, 0, 0.5),
                                                  "section-oblique": cam((sx, y0(d) + d.panel_d / 2, 50), 135, 62, 16, 0.6)}, lines)
    # the latch of each option: a cut through the front right latch point
    for name, built in (("latch-" + k, o) for k, o in {"default": b, **options}.items()):
        lx, ly = latch_points(d, built.i)[1]
        keep = box(-so.BIG, lx, -so.BIG, so.BIG, -so.BIG, so.BIG)
        every = {**deck, **{k: (s, finish_of(k)) for k, s in {**built.fixed, **built.arcade}.items()}, **latch_hardware(d, built.i), "Buttons": hard["Buttons"]}
        cut, lines = cut_scene(every, keep, skin, V(1, 0, 0), lx)
        write_model(out / name, cut, None, {"latch": cam((lx, ly + 6, z_rest(d) - 3), 30, 90, 0, 0.7), "latch-oblique": cam((lx, ly + 4, z_rest(d)), 34, 55, 28, 0.7)}, lines)
    if i.latch == PUSH_BOLT:
        push_bolt_scenes(out, b, skin, hw)


def push_bolt_scenes(out: Path, b: Built, skin: Part.Shape, hw: Hardware) -> None:
    """The pictures of the push bolt: the front of the deck with the button in its hole (from the front and close),
    the rim of the hole alone (close), and the section through the bolt on the centre line, locked and with the
    button in (seen from the right, the cut face toward the camera)."""
    d, i = b.d, b.i
    p = i.push
    z = d.latch_button_z
    front = {"deck": (skin, FINISH["deck"]), "latch_bolt": (b.latch["latch_bolt"], FINISH["latch"])}
    write_model(out / "button-front", front, None, {"front": cam((0.0, 0.0, z), 70, 0, 4, 0.62), "close": cam((0.0, 0.0, z), 22, 0, 4, 0.8),
                                                    "close-oblique": cam((0.0, 0.0, z), 24, -35, 18, 0.8)})
    write_model(out / "button-rim", {"deck": (skin, FINISH["deck"])}, None, {"rim": cam((0.0, 0.0, z), 22, 0, 4, 0.8), "rim-oblique": cam((0.0, 2.0, z), 24, -35, 18, 0.8)})
    hard = groups(hw)
    panel = {**{k: (s, finish_of(k)) for k, s in b.arcade.items()}, "Buttons": hard["Buttons"], **latch_split(latch_hardware(d, i))[0]}
    cabinet = {"deck": (skin, FINISH["deck"]), **{k: (s, finish_of(k)) for k, s in b.frame.items()}, "latch_gate": (b.latch["latch_gate"], FINISH["latch"])}
    look = cam((0.0, 40.0, 56.0), 56, 90, 0, 0.6)
    for state, s_ in (("locked", 0.0), ("button-in", p.stroke)):
        every = {**cabinet, **panel, "latch_bolt": (bolt(d, p, s_), FINISH["latch"]), "spring": (springs(p, s_)["bolt_spring"], FINISH["spring"])}
        cut, lines = cut_scene(every, box(-so.BIG, 0.0, -so.BIG, so.BIG, -so.BIG, so.BIG), skin, V(1, 0, 0), 0.0)
        write_model(out / f"section-bolt-{state}", cut, None, {"section": look}, lines)


def markdown(rep: dict) -> str:
    st = rep["stiffness"]
    lines = ["# Control panel: checks", "", f"Result: **{'FAIL' if rep['failures'] else 'PASS'}**.", ""]
    lines += [f"- {f}" for f in rep["failures"]]
    lines += ["", "## Clashes", "", "Common volume in mm3 (the fit rules allow 1). Gap: the smallest distance to a solid of that hardware, in mm.", "",
              "| Part | Against | Common | Gap | Nearest | Result |", "| --- | --- | --- | --- | --- | --- |"]
    lines += [f"| {r['part']} | {r['against']} | {r['common_mm3']} | {'' if r.get('gap') is None else r['gap']} | {r.get('nearest', '')} | {r['result']} |"
              for r in rep["clashes"] + rep["clashes_blank"]]
    lines += ["", "## The room below the plate", "", f"Volume {rep['room_volume_cm3']} cm3, box {rep['room_box']}.", "", "| What | Volume, mm3 | Result |", "| --- | --- | --- |"]
    lines += [f"| {r['what']} | {r['common_mm3']} | {r['result']} |" for r in rep["room"]]
    lines += ["", "## The way out", "", "| Step | Common volume with what stays, mm3 | Result |", "| --- | --- | --- |"]
    lines += [f"| {r['step'] if 'step' in r else 'lift ' + format(r['lift'], 'g')} | {r['common_mm3']} | {r['result']} |" for r in rep["lift"]]
    if rep.get("locks"):
        lines += ["", "| The lock holds | Common volume, mm3 | Result |", "| --- | --- | --- |"]
        lines += [f"| {r['what']} | {r['common_mm3']} | {r['result']} |" for r in rep["locks"]]
    if rep.get("hold"):
        h = rep["hold"]
        lines += ["", "## The hold of the push bolt (ESTIMATED, candybar.shell.panel_latch)", "",
                  f"One latch point: a magnet {h['magnet']['frame'][0]:g} x {h['magnet']['frame'][1]:g} in the pad on a {h['magnet']['plate_disc']} disc "
                  f"{h['magnet']['plate'][0]:g} x {h['magnet']['plate'][1]:g} in the plate: {h['magnet']['pull_N']:g} N. The hold in the worst load case: factor "
                  f"{h['hold_factor']:.2f}; in normal play: factor {h['play_factor']:.2f}.", "",
                  f"To take the panel out: {h['removal']['how']}"]
    lines += ["", "## Stiffness (hand estimate)", "", f"Load {st['load_N']:g} N on the ball, {st['arm_mm']:g} above the panel: a couple of {st['couple_Nmm'] / 1000:g} N m. "
              f"E {st['E_MPa']:g} MPa. Span {st['span_mm']:g}, bay {st['bay_mm']:g}, ribs {st['rib_spacing_mm']:g} apart.", "",
              "| Case | I of the bay, mm4 | Forward: slope, mrad | Deflection, mm | Ball moves, mm | Sideways: slope, mrad | Ball moves, mm |", "| --- | --- | --- | --- | --- | --- | --- |"]
    lines += [f"| {k} | {c['I_bay_mm4']} | {c['forward_slope_mrad']} | {c['forward_deflection_mm']} | {c['forward_ball_mm']} | {c['side_slope_mrad']} | {c['side_ball_mm']} |"
              for k, c in st["cases"].items()]
    hd, lt = st["hand"], st["latch"]
    lines += ["", f"A hand of {hd['load_N']:g} N on the middle of the button field ({hd['field_mm'][0]} x {hd['field_mm'][1]}, plate of 5): {hd['deflection_mm']} mm "
              f"({hd['per_10N_mm']} mm for each 10 N).", "",
              f"The couple lifts one edge of the panel with {lt['lift_per_edge_N']} N. Two magnet points hold {lt['magnet_edge_N']:g} N (factor {lt['magnet_factor']}); "
              f"the four hold {lt['magnet_lift_out_N']:g} N against a pull on the lever.", "",
              "## Print", "", "| Part | On the printer | Box | Fits | On the bed, cm2 | Overhang over 45 degrees, cm2 | Mass, g |", "| --- | --- | --- | --- | --- | --- | --- |"]
    lines += [f"| {r['part']} | {r['how']} | {r['x']} x {r['y']} x {r['z']} | {'yes' if r['fits'] else 'NO'} | {r['bed_cm2']} | {r['overhang_cm2']} | {r['mass_g']} |" for r in rep["print"]]
    lines += ["", "## Edge finish and faces", "", "| Part | Faces of the edge break | Sharp edges that show | Sharp edges against a cover | Face check: findings that fail | allowed |", "| --- | --- | --- | --- | --- | --- |"]
    for name, r in rep["edge_finish"].items():
        fc = rep["face_check"].get(name, {})
        shown = sum(g["edges"] for g in r["sharp"] if not g["against"])
        hidden = sum(g["edges"] for g in r["sharp"] if g["against"])
        lines.append(f"| {name} | {r['break_faces']} | {shown} | {hidden} | {sum(fc.get(k, 0) for k in ('sliver', 'needle', 'crowded', 'kink', 'split'))} | {fc.get('allowed', 0)} |")
    lines += ["", "A sharp edge of these parts lies against:", ""] + [f"- `{k}`: {t}" for k, t in JOINTS.items()]
    return "\n".join(lines) + "\n"


def main() -> int:
    out = Path(os.environ.get("CANDYBAR_OUT", OUT))
    out.mkdir(parents=True, exist_ok=True)
    start = time.time()
    log = lambda text: print(f"[{time.time() - start:6.1f} s] {text}", flush=True)
    v = values()
    b = build(v=v)
    log("parts built")
    deck = deck_skin(b.d, log)
    hw = hardware(b.d, deck)
    skin = pocket_skin(b.d, deck)
    log(f"skin round the pocket: {len(skin.Faces)} faces of {len(deck.Faces)}")
    rep = check(b, skin, hw, v, log)
    log("checks done")
    (out / "report.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
    (out / "report.md").write_text(markdown(rep), encoding="utf-8")
    # the printed parts alone, for tools.edge_finish and tools.face_check
    write_model(out / "parts", {k: (s, finish_of(k)) for k, s in b.parts.items()})
    # the parts in place in the deck, for candybar.shell.viewdoc (shell.FCStd); the blank panel stands beside it
    aside = V(0, -260, 0)
    doc = {"deck": (deck, FINISH["deck"]), **{k: (s, finish_of(k)) for k, s in {**b.fixed, **b.arcade}.items()},
           **{k: (s.translated(aside), finish_of(k)) for k, s in b.blank.items()}, **groups(hw), **latch_hardware(b.d, b.i)}
    write_model(out, doc, {"deck": so.deck(b.d)[0]})
    options = {k: Built(b.d, oi, b.a, frame(b.d, oi), arcade(b.d, oi, b.a, v), {}) for k, oi in
               (("screw", replace(b.i, latch=SCREW)), ("magnet", replace(b.i, latch=MAGNET)))}
    scenes(out / "scenes", b, deck, hw, options)
    log("files written")
    print(markdown(rep))
    return 1 if rep["failures"] else 0
