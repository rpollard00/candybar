"""A study of a latch for the control panel that needs no tool (docs/design/control-panel-latch.md).

Run headless. It exits 1 when a check of a built candidate fails:

    CANDYBAR_OUT=cad/out/panel-latch cad/candybar/freecad-run.sh candybar.shell.panel_latch
    cad/.venv-tools/bin/python cad/tools/draw_panel_latch.py                       # renders and sheets

The study does not change the default. panel_frame.Interface.latch stays SCREW (option A), and MAGNET (option B)
stays as it is. Each candidate starts from option B (a magnet pair at each of the four latch points) and adds to it:

  M  magnets and shear keys only: the largest frame magnet that the pad takes (12 x 10). The cones stay. Straight lift.
  H  hook and drop: two hooks under the rear edge of the panel go into notches in the rear bar of the frame. The
     panel swings down about its rear top edge. The magnets (12 x 5 in the frame) hold the front edge.
  B  hooks and a push bolt (the owner's choice, 2026-11-15; this is its final form): the hooks of H, and one bolt
     at the front centre. The bolt is a printed bar in a tunnel that is one print with the left half of the frame.
     Its front end is a flush button in the front face of the deck, on the centre line. Hold the button in and lift
     the panel out by hand. A steel spring pushes the bolt forward again; a gate dropped into the rear of the tunnel
     holds the spring. A wedge of 8 degrees under the bolt pulls the panel down (the preload). Magnets in all four
     pads. A panel with nothing to hold has a finger hole.
  Q  hooks and two quarter-turn cams: the hooks of H, and two printed cams in the panel near its front edge. A cam
     has a flush head with a finger bar on the top face; its tongue turns under the front bar of the frame.

The rear hooks replace nothing: the two cones at the rear edge stay and locate the panel in every candidate.

Frames: the cabinet frame of dims.py (y from the front face of the deck to the rear, z up from the desk).
"""
from __future__ import annotations

import json
import math
import os
import time
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

import FreeCAD as App
import Part

from . import fit, split
from . import panel_frame as pf
from . import profiles as pr
from . import solids as so
from .dims import Blueprint

V = App.Vector
OUT = "cad/out/panel-latch"
CANDIDATES = ("M", "H", "B", "Q")
NAMES = {"M": "Magnets only", "H": "Hooks and magnets", "B": "Hooks and a push bolt", "Q": "Hooks and two quarter-turn cams"}
FINISH = {**pf.FINISH, "slider": "#d0762b", "housing": "#5a7fa8", "cover": "#7d9cc0", "cam": "#d0762b", "tongue": "#c06020",
          "spring": "#8c8f96", "hook": "#2b2b2e"}


@dataclass(frozen=True)
class Latch:
    """The values of the study. Lengths in mm, forces in N."""
    # ---- the magnets (all candidates): a disc in each pad of the frame, a disc of 12 x 2 in the plate (the pocket
    # of option B, 12.2 x 2.2, does not change). The frame magnet of each candidate:
    frame_magnet_h: dict = field(default_factory=lambda: {"M": 10.0, "H": 5.0, "B": 2.0, "Q": 2.0})
    # B has them at all four: the front two keep the front corners down (see corner_rock)
    magnet_points: dict = field(default_factory=lambda: {"M": (0, 1, 2, 3), "H": (0, 1, 2, 3), "B": (0, 1, 2, 3), "Q": (0, 1, 2, 3)})
    plate_magnet_h: float = 2.0
    # ESTIMATED pull of an N52 disc of 12 diameter on thick steel at contact (maker's data, case 1): 46 N for 12 x 5
    # (one maker), 50 N for 12.7 x 4.76 (another). Other thicknesses: F = f_inf (1 - exp(-h / h0)), fitted to these
    magnet_f_inf: float = 75.6
    magnet_h0: float = 5.25
    # a pair of magnets at contact pulls about as one magnet of the two thicknesses together, less pair_factor
    pair_factor: float = 0.75
    # the gap: pad_drop 0.1 and 0.2 of adhesive and print error. A gap of 1 mm loses more than half (maker's chart):
    # exp(-gap / gap_scale)
    magnet_gap: float = 0.3
    gap_scale: float = 1.0
    # tilt, coating, 40 degrees C in the cabinet, a pocket that is not square
    use_factor: float = 0.7
    # ---- the rear hooks (H, B, Q): a stem under the plate and a toe whose top and bottom are arcs about the pivot
    # (the rear top edge of the plate, y_pivot z panel_top). The toe goes into a notch in the rear bar of the frame
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
    # ---- the push bolt (B)
    bolt_w: float = 12.0
    bolt_z: tuple = (52.0, 58.0)
    # the button fits in the leaning band of the front face (z 48 to 62.6), so that its face is one plane
    button_d: float = 14.0
    button_z: float = 55.3
    button_hole_d: float = 14.6
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
    frame_split_x: float = 20.0    # the halves of the frame meet here, not on the centre line: the tunnel is whole in the left half
    # a panel with nothing to hold (the blank panel) has a finger hole near its front edge
    finger_hole: tuple = (50.0, 37.0, 22.0)   # x, yl, diameter
    bolt_spring_free: float = 22.0
    bolt_spring_rate: float = 1.2  # N/mm: 7.8 N at the lock, 13.8 N at the full stroke
    bolt_spring_bore: float = 4.4
    bolt_spring_d: float = 4.0
    mu: float = 0.3                # ABS on ABS, dry (ESTIMATED; 0.25 to 0.45)
    # ---- the quarter-turn cams (Q)
    cam_x: float = 128.5          # on the middle line of the rib beside the service buttons: the rib crosses the boss cleanly
    cam_y: float = 43.2
    cam_head_d: float = 16.0
    cam_head_h: float = 3.2
    cam_bar: tuple = (3.0, 11.0, 1.5)   # the finger bar on the head: a half capsule, wide, long, high
    cam_shank_d: float = 8.0
    cam_hole_d: float = 8.4
    cam_hub_d: float = 13.0          # the boss of the tongue round the end of the shank
    cam_tongue: tuple = (8.0, 14.0, 3.8)   # wide, from the axis, thick
    cam_boss_h: float = 8.0
    cam_pin_d: float = 3.0           # a steel dowel pin 3 x 14 joins the tongue to the shank
    cam_plate_boss: tuple = (15.0, 5.0)   # a boss under the plate round each cam hole: diameter, height
    cam_tongue_clear: float = 0.4
    # ---- the loads (docs/research/controls-ergonomics.md 6.3, control-panel.md)
    pull_up: float = 80.0          # on the lever, upward
    side: float = 50.0             # at the ball, in any horizontal direction
    play: float = 15.0             # normal play, at the ball
    panel_weight: float = 5.0
    # ---- printed ABS, ESTIMATED: along the layers and across them
    abs_along: float = 35.0
    abs_across: float = 15.0
    abs_e: float = 2200.0
    abs_yield_strain: float = 0.02


L0 = Latch()


# ---------- small helpers ----------

def side_prism(pts: list[tuple[float, float]], x0: float, x1: float) -> Part.Shape:
    """A profile in (y, z) at x0, extruded to x1."""
    w = Part.makePolygon([V(x0, y, z) for y, z in pts] + [V(x0, *pts[0])])
    return Part.Face(w).extrude(V(x1 - x0, 0, 0))


def xcyl(r: float, x0: float, x1: float, y: float, z: float) -> Part.Shape:
    return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def ycyl(d: float, y0: float, y1: float, x: float, z: float) -> Part.Shape:
    return Part.makeCylinder(d / 2, y1 - y0, V(x, y0, z), V(0, 1, 0))


def pivot(d: Blueprint, i: pf.Interface) -> tuple[float, float]:
    """The axis of the swing (along x): the rear top edge of the plate."""
    return pr.panel_outline(d, -i.seat_gap)[4][1], d.panel_top


def rear_bar_face(d: Blueprint, i: pf.Interface) -> float:
    """y of the inner face of the rear bar of the frame (the opening less the bond gap)."""
    return pf.opening(d, i, i.bond_gap)[4][1]


def front_bar_face(d: Blueprint, i: pf.Interface) -> float:
    return pf.opening(d, i, i.bond_gap)[1][1]


def bar_z(d: Blueprint, i: pf.Interface) -> tuple[float, float]:
    z1 = pf.z_rest(d) - d.wall_t - i.bond_gap
    return z1 - i.bar_h, z1


def magnet_pull(h_frame: float, h_plate: float, L: Latch = L0) -> dict:
    """ESTIMATED hold of one magnet pair, N, with each step of the estimate."""
    case1 = lambda h: L.magnet_f_inf * (1 - math.exp(-h / L.magnet_h0))
    contact = case1(h_frame + h_plate) * L.pair_factor
    gap = math.exp(-L.magnet_gap / L.gap_scale)
    return {"frame": [12.0, h_frame], "plate": [12.0, h_plate], "case1_frame_N": round(case1(h_frame), 1),
            "pair_contact_N": round(contact, 1), "gap_mm": L.magnet_gap, "gap_factor": round(gap, 3), "use_factor": L.use_factor,
            "pull_N": round(contact * gap * L.use_factor, 1)}


def interface(c: str, L: Latch = L0) -> pf.Interface:
    """Option B, with the frame magnet of the candidate."""
    return replace(pf.Interface(), latch=pf.MAGNET, magnet_h=L.frame_magnet_h[c], keeper_h=L.plate_magnet_h)


# ---------- the rear hooks ----------

def hook(d: Blueprint, i: pf.Interface, x: float, L: Latch = L0) -> Part.Shape:
    """A hook under the rear edge of the plate: a stem and a toe. The top and the bottom of the toe are arcs about the
    pivot, so that the toe slides out of the notch when the front of the panel goes up."""
    yp, zp = pivot(d, i)
    face = rear_bar_face(d, i)
    zr = pf.z_rest(d)
    r_in = math.hypot(yp - (face - i.bond_gap), zp - L.notch_top) + L.toe_clear
    tip = face + L.notch_back - L.toe_tip_gap
    stem_y1 = face - L.stem_gap
    x0, x1 = x - L.hook_w / 2, x + L.hook_w / 2
    ring = xcyl(L.toe_r_out, x0, x1, yp, zp).cut(xcyl(r_in, x0 - 1, x1 + 1, yp, zp))
    toe = ring.common(pf.box(x0, x1, stem_y1 - L.stem_t, tip, zp - L.toe_r_out - 1, zr))
    # the stem goes down to the bottom arc of the toe at the stem's rear face, so that no narrow strip of its lower
    # face is left beside the toe
    z_low = zp - math.sqrt(L.toe_r_out ** 2 - (yp - stem_y1) ** 2)
    stem = pf.box(x0, x1, stem_y1 - L.stem_t, stem_y1, z_low, zr)
    return pf.one_solid(so.unsplit(stem.fuse(toe)), "rear hook")


def notches(d: Blueprint, i: pf.Interface, L: Latch = L0) -> list[Part.Shape]:
    """The notches in the rear bar of the frame that take the toes: open at the bottom and at the front."""
    face = rear_bar_face(d, i)
    z0, _ = bar_z(d, i)
    w = L.hook_w / 2 + L.notch_side
    return [pf.box(x - w, x + w, face - 1, face + L.notch_back, z0 - 1, L.notch_top) for x in (-L.hook_x, L.hook_x)]


# ---------- the push bolt (B) ----------

def band_y(z: float, d: Blueprint) -> float:
    """y of the front face of the deck at height z, at the centre line (upright to the crease, then the band leans)."""
    crease = d.deck_top - d.deck_lean_h
    return max(0.0, (z - crease) * math.tan(math.radians(d.deck_lean)))


def bolt(d: Blueprint, L: Latch = L0, s: float = 0.0) -> Part.Shape:
    """The push bolt, moved back by s: a bar along y with a flush button at its front, a neck (where the lips of the
    strike pass when it is released), the lock section with the wedge under it, a stop block and a bore for its
    spring at the rear. The underside of the lock section falls wedge_deg toward the rear over the lips: the spring
    pushes the bolt forward, and the wedge pulls the strike (and the panel) down."""
    z0, z1 = L.bolt_z
    hw = L.bolt_w / 2
    neck0, neck1 = neck(L)
    yw1 = wedge_end(L)
    head_y1 = 10.0
    # the button: a cylinder cut by the plane of the leaning band of the front face
    t = math.tan(math.radians(d.deck_lean))
    crease = d.deck_top - d.deck_lean_h
    # it is no wider than the bolt, so that the bolt lies flat on its side on the printer
    head = ycyl(L.button_d, -5.0, head_y1, 0.0, L.button_z).common(pf.box(-hw, hw, -10.0, head_y1 + 1, 0.0, 100.0))
    outside = side_prism([(-20.0, crease - 40.0), (-20.0, crease + 60.0), (60.0 * t, crease + 60.0), (-40.0 * t, crease - 40.0)],
                         -L.button_d, L.button_d)
    head = head.cut(outside)
    front = pf.box(-hw, hw, head_y1 - 1, neck0 + 0.5, z0, z1)
    narrow = pf.box(-L.neck_w / 2, L.neck_w / 2, neck0, neck1, under(L, neck1), z1)
    lock = side_prism([(neck1, under(L, neck1)), (yw1, z0), (L.bolt_end_y, z0), (L.bolt_end_y, z1), (neck1, z1)], -hw, hw)
    # the stop block stands out on the +x side only: the -x side of the bolt is one plane, which lies on the bed
    stop = pf.box(-hw, L.stop_w / 2, L.stop_y, L.stop_y + 3.0, z0, z1)
    solid = so.unsplit(head.fuse([front, narrow, lock, stop]))
    bore = ycyl(L.bolt_spring_bore, L.bolt_end_y - 10.0, L.bolt_end_y + 1, 0.0, (z0 + z1) / 2)
    solid = pf.one_solid(solid.cut(bore), "push bolt")
    return break_front(solid, d).translated(V(0, s, 0))


def neck(L: Latch = L0) -> tuple[float, float]:
    """The neck of the bolt at the lock: it holds the lug with neck_margin at each end when the bolt is back by the
    stroke."""
    y0, y1 = L.lug_y
    return y0 - L.neck_front - L.stroke, y1 + L.neck_margin - L.stroke


def wedge_end(L: Latch = L0) -> float:
    return L.lug_y[1] + L.neck_margin + 0.5


def under(L: Latch, y: float) -> float:
    """z of the underside of the bolt's lock section at y (the bolt at the lock)."""
    w = math.tan(math.radians(L.wedge_deg))
    return L.bolt_z[0] + w * max(0.0, wedge_end(L) - y)


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


def strike(d: Blueprint, i: pf.Interface, L: Latch = L0) -> Part.Shape:
    """The strike under the front edge of the panel, at the centre: two legs that stand each side of the bolt, a bridge
    above it, and a lip on each leg that reaches in under the bolt. The top of each lip is parallel to the wedge
    under the bolt, bolt_clear below it."""
    z0, z1 = L.bolt_z
    hw = L.bolt_w / 2 + L.bolt_clear
    y0, y1 = L.lug_y
    zr = pf.z_rest(d)
    outer = pf.box(-hw - L.lug_leg_t, hw + L.lug_leg_t, y0, y1, L.lug_z0, zr)
    window = side_prism([(y0 - 1, under(L, y0 - 1) - L.bolt_clear), (y1 + 1, under(L, y1 + 1) - L.bolt_clear), (y1 + 1, z1 + L.bolt_clear), (y0 - 1, z1 + L.bolt_clear)], -hw, hw)
    slot = pf.box(-(L.bolt_w / 2 - L.lug_lip), L.bolt_w / 2 - L.lug_lip, y0 - 1, y1 + 1, L.lug_z0 - 1, z1)
    return pf.one_solid(so.unsplit(outer.cut([window, slot])), "strike")


def tunnel(d: Blueprint, i: pf.Interface, L: Latch = L0) -> Part.Shape:
    """The tunnel of the bolt, a part of the left half of the frame: a floor under the bolt from the front bar to the
    rear of the tunnel (in the plane of the lower face of the bar), with a window round the strike; two walls and a
    roof round the bolt behind the strike; a shoulder in the right wall that stops the stop block of the bolt; a slot
    for the gate at the rear. The walls stand back on the right from the shoulder to the rear, so that the bolt goes
    in from the rear."""
    fz0, _ = bar_z(d, i)
    fz1 = L.bolt_z[0] - L.bolt_clear
    ya, yb = L.housing_y
    hw, tw = L.housing_w / 2, L.tunnel_w / 2
    bw = L.bolt_w / 2 + L.bolt_clear
    sw = L.stop_w / 2 + L.bolt_clear
    rz0, rz1 = L.roof_z
    y_walls = L.lug_y[1] + 1.5
    ch0 = L.stop_y - 0.3
    floor = pf.box(-hw, hw, ya, yb, fz0, fz1)
    walls = [pf.box(-tw, -bw, y_walls, yb, fz1, rz0), pf.box(bw, tw, y_walls, ch0, fz1, rz0), pf.box(sw, tw, ch0, yb, fz1, rz0)]
    roof = pf.box(-tw, tw, y_walls, yb, rz0, rz1)
    solid = pf.joined([floor, *walls, roof])
    g = L.strike_window
    sb = strike(d, i, L).BoundBox
    window = pf.box(sb.XMin - g, sb.XMax + g, sb.YMin - g - 0.5, sb.YMax + g + 0.5, fz0 - 1, fz1 + 1)
    c = L.gate_slot_clear
    slot = pf.box(L.gate_x[0] - c, L.gate_x[1] + c, L.gate_y[0] - c, L.gate_y[1] + c, fz1, rz1 + 1)
    return so.unsplit(solid.cut([window, slot]))


def gate(L: Latch = L0) -> Part.Shape:
    """The gate: a plate dropped into the slot at the rear of the tunnel. The spring of the bolt pushes it back
    against the rear face of the slot. Its top stands gate_tab above the roof for the fingers; the plate of a seated
    panel stands above it, so it cannot leave its slot while a panel is in."""
    z0, z1 = L.bolt_z
    g = pf.box(L.gate_x[0], L.gate_x[1], L.gate_y[0], L.gate_y[1], z0, L.roof_z[1] + L.gate_tab)
    # a peg on its front face that the end of the spring goes over
    peg = ycyl(3.0, L.gate_y[0] - 4.0, L.gate_y[0] + 0.5, 0.0, (z0 + z1) / 2)
    return pf.one_solid(so.unsplit(g.fuse(peg)), "gate")


def joined(shapes: list[Part.Shape]) -> Part.Shape:
    return pf.joined(shapes)


def springs(L: Latch = L0, s: float = 0.0) -> dict[str, Part.Shape]:
    """The bought spring of the bolt as a plain cylinder, for the pictures: between the bore of the bolt and the seat
    in the gate."""
    z0, z1 = L.bolt_z
    return {"bolt_spring": ycyl(L.bolt_spring_d, L.bolt_end_y - 10.0 + s, L.gate_y[0], 0.0, (z0 + z1) / 2)}


def spring_length(L: Latch = L0, s: float = 0.0) -> float:
    return L.gate_y[0] - (L.bolt_end_y - 10.0 + s)


def button_hole(L: Latch = L0) -> Part.Shape:
    """The hole for the button in the front wall of the deck (a change of the deck nose): a circle with two flats,
    the shape of the button with a gap of (button_hole_d - button_d) / 2 round it."""
    g = (L.button_hole_d - L.button_d) / 2
    hw = L.bolt_w / 2 + g
    return ycyl(L.button_hole_d, -2.0, 12.0, 0.0, L.button_z).common(pf.box(-hw, hw, -3.0, 13.0, 0.0, 100.0))


def front_notch(d: Blueprint, i: pf.Interface, L: Latch = L0) -> Part.Shape:
    """The bolt passes the front bar of the frame through a notch above the floor of the tunnel."""
    _, z1 = bar_z(d, i)
    hw = L.bolt_w / 2 + 1.0
    return pf.box(-hw, hw, front_bar_face(d, i) - 12, front_bar_face(d, i) + 1, L.bolt_z[0] - L.bolt_clear, z1 + 1)


def bolt_room(L: Latch = L0) -> Part.Shape:
    """What B takes from the room below the plate: the box of the tunnel, the gate and the travel of the bolt, with
    room_gap round it. A panel keeps clear of it, but for its strike."""
    g = 0.5
    hw = L.housing_w / 2 + g
    return pf.box(-hw, hw, L.housing_y[0], L.housing_y[1] + g, 48.8 - g, 65.0)


def resplit(frame: dict[str, Part.Shape], at: float, gap: float) -> dict[str, Part.Shape]:
    """The two halves of the frame joined again and cut at x = at. Near the centre line the frame is two straight
    bars along x, so the gap of the first cut is filled with a slice of the right half moved to it."""
    left, right = frame["frame_left"], frame["frame_right"]
    x0 = right.BoundBox.XMin
    fill = right.common(pf.box(x0, x0 + 2.0, -so.BIG, so.BIG, -so.BIG, so.BIG)).translated(V(-2.0 * x0 - 0.5, 0, 0))
    whole = so.unsplit(left.fuse([right, fill]))
    g = gap / 2
    out = dict(frame)
    out["frame_left"] = pf.one_solid(so.unsplit(whole.common(pf.box(-so.BIG, at - g, -so.BIG, so.BIG, 0, 200))), "frame, left half")
    out["frame_right"] = pf.one_solid(so.unsplit(whole.common(pf.box(at + g, so.BIG, -so.BIG, so.BIG, 0, 200))), "frame, right half")
    return out


def finger_hole(d: Blueprint, tiles: dict[str, Part.Shape], L: Latch = L0) -> dict[str, Part.Shape]:
    """A finger hole through the plate of a panel with nothing to hold, with the edge break round both of its rims."""
    x, yl, dia = L.finger_hole
    y = pf.y0(d) + yl
    zr, zt = pf.z_rest(d), d.panel_top
    out = {}
    for name, tile in tiles.items():
        b = tile.BoundBox
        if not (b.XMin < x < b.XMax):
            out[name] = tile
            continue
        cut = pf.one_solid(so.unsplit(tile.cut(pf.cyl(dia, x, y, zr - 1, zt + 1))), name)
        rims = [e for e in cut.Edges if not e.Degenerated and abs(e.BoundBox.Center.x - x) < 1e-3 and abs(e.BoundBox.Center.y - y) < 1e-3
                and (abs(e.BoundBox.ZMin - zt) < 1e-6 or abs(e.BoundBox.ZMin - zr) < 1e-6) and abs(e.BoundBox.ZMax - e.BoundBox.ZMin) < 1e-6]
        out[name] = pf.one_solid(cut.makeFillet(d.edge_break, rims), f"{name}, with the finger hole")
    return out


# ---------- the quarter-turn cams (Q) ----------

def cam(d: Blueprint, L: Latch = L0, x: float = 125.0, turn: float = 0.0) -> dict[str, Part.Shape]:
    """One cam: the stud (a flush head with a finger bar, and the shank) and the tongue (an arm on a boss that takes the
    end of the shank). A steel cross pin through the boss and the shank joins them. Locked (turn 0) the tongue points
    to the front, under the front bar of the frame; turn 90 points it toward the centre line. An O-ring on the shank
    under the plate (bought) holds the stud up against its head and gives the turn some friction."""
    zt = d.panel_top
    y = L.cam_y
    tw, tl, tt = L.cam_tongue
    b0, _ = bar_z(d, pf.Interface())
    tz1 = b0 - L.cam_tongue_clear
    tz0 = tz1 - tt
    head = pf.cyl(L.cam_head_d, x, y, zt - L.cam_head_h, zt)
    # under the head, a cone of 45 degrees down to the shank: the stud prints upright with no support
    rh, rs = L.cam_head_d / 2, L.cam_shank_d / 2
    head = head.fuse(Part.makeCone(rs, rh, rh - rs, V(x, y, zt - L.cam_head_h - (rh - rs)), V(0, 0, 1)))
    bw, bl, bh = L.cam_bar
    r = bw / 2
    capsule = ycyl(bw, y - bl / 2 + r, y + bl / 2 - r, x, zt).fuse([Part.makeSphere(r, V(x, y - bl / 2 + r, zt)), Part.makeSphere(r, V(x, y + bl / 2 - r, zt))])
    bar = capsule.common(pf.box(x - 10, x + 10, y - bl, y + bl, zt, zt + bh))
    end = tz0 + 1.2
    shank = pf.cyl(L.cam_shank_d, x, y, end, zt - L.cam_head_h + 0.1)
    stud = finish_head(so.unsplit(head.fuse(shank)), d, zt)
    stud = so.unsplit(stud.fuse(bar))
    pin = cam_pin(L, x, tz0)
    stud = stud.cut(pin)
    boss = pf.cyl(L.cam_hub_d, x, y, tz0, tz0 + L.cam_boss_h)
    arm = pf.box(x - tw / 2, x + tw / 2, y - tl, y, tz0, tz1)
    socket = pf.cyl(L.cam_shank_d + 0.3, x, y, end, tz0 + L.cam_boss_h + 1)
    tongue = so.unsplit(boss.fuse(arm).cut([socket, pin]))
    sign = 1.0 if x < 0 else -1.0
    rot = lambda s: s.rotated(V(x, y, 0), V(0, 0, 1), sign * turn) if turn else s
    return {"cam_stud": rot(pf.one_solid(stud, "cam stud")), "cam_tongue": rot(pf.one_solid(tongue, "cam tongue"))}


def cam_pin(L: Latch, x: float, tz0: float) -> Part.Shape:
    """The steel cross pin of a cam (bought): along x through the boss of the tongue and the shank."""
    return xcyl(L.cam_pin_d / 2, x - L.cam_hub_d / 2 - 1, x + L.cam_hub_d / 2 + 1, L.cam_y, tz0 + L.cam_boss_h / 2 + 1.0)


def finish_head(stud: Part.Shape, d: Blueprint, zt: float) -> Part.Shape:
    """The edge break on the edges of the head and the finger bar that stand above the plate."""
    edges = [e for e in stud.Edges if not e.Degenerated and e.BoundBox.ZMin > zt - 1e-6 and e.BoundBox.ZMax < zt + 1e-6
             and len(stud.ancestorsOfType(e, Part.Face)) == 2 and so.edge_turn(stud, e)[0]]
    for r in (d.edge_break, 0.7):
        try:
            out = stud.makeFillet(r, edges)
            if out.isValid():
                return out
        except Part.OCCError:
            continue
    return stud


def cam_holes(d: Blueprint, L: Latch = L0) -> tuple[list[Part.Shape], list[Part.Shape], list[Part.Shape]]:
    """What a panel needs for the cams: first what is cut from its ribs (the boss of the tongue turns there), then the
    boss under the plate round each hole (so that the hole is long enough for the shank), then the hole and the
    counterbore of the head."""
    zt, zr = d.panel_top, pf.z_rest(d)
    clear, bosses, holes = [], [], []
    for x in (-L.cam_x, L.cam_x):
        clear.append(pf.cyl(L.cam_hub_d + 1.0, x, L.cam_y, zr - 30.0, zr))
        bosses.append(pf.cyl(L.cam_plate_boss[0], x, L.cam_y, zr - L.cam_plate_boss[1], zr + 0.5))
        rh, rs = L.cam_head_d / 2 + 0.3, L.cam_hole_d / 2
        z_cb = zt - L.cam_head_h - 0.2
        holes += [pf.cyl(L.cam_hole_d, x, L.cam_y, zr - 10.0, zt + 1), pf.cyl(2 * rh, x, L.cam_y, z_cb, zt + 1),
                  Part.makeCone(rs, rh, rh - rs, V(x, L.cam_y, z_cb - (rh - rs)), V(0, 0, 1))]
    return clear, bosses, holes


# ---------- a candidate ----------

@dataclass
class Candidate:
    c: str
    d: Blueprint
    i: pf.Interface
    L: Latch
    frame: dict[str, Part.Shape]          # stays in the cabinet: the frame halves and posts
    fixed: dict[str, Part.Shape]          # other latch parts that stay in the cabinet (the gate of B)
    arcade: dict[str, Part.Shape]
    blank: dict[str, Part.Shape]
    on_panel: dict[str, Part.Shape]       # latch parts that go with the panel (the cams)
    moving: dict[str, Part.Shape]         # latch parts in the cabinet that move (the bolt), at the lock

    @property
    def printed(self) -> dict[str, Part.Shape]:
        out = {**self.frame, **self.fixed, **self.arcade, **self.blank, **self.moving}
        for k, s in self.on_panel.items():
            out[k] = s
        return out


def add_to_tiles(tiles: dict[str, Part.Shape], add: list[Part.Shape], cut: list[Part.Shape]) -> dict[str, Part.Shape]:
    """Fuse each added solid to the tile that holds its middle (a solid across the seam is split at it), and cut."""
    names = list(tiles)
    seam = tiles[names[0]].BoundBox.XMax
    out = {}
    for k, name in enumerate(names):
        tile = tiles[name]
        half = pf.box(-so.BIG, seam, -so.BIG, so.BIG, -so.BIG, so.BIG) if k == 0 else pf.box(seam, so.BIG, -so.BIG, so.BIG, -so.BIG, so.BIG)
        parts = [s.common(half) for s in add]
        parts = [s for s in parts if s.Volume > 1e-6]
        if cut:
            tile = tile.cut(cut)
        if parts:
            tile = so.unsplit(tile.fuse(parts))
        out[name] = pf.one_solid(tile, name)
    return out


def build(c: str, d: Blueprint | None = None, a: pf.Arcade | None = None, v=None, L: Latch = L0) -> Candidate:
    d, a = d or Blueprint(), a or pf.Arcade()
    v = v or pf.values()
    i = interface(c, L)
    frame = pf.frame(d, i)
    arcade = pf.arcade(d, i, a, v)
    blank = pf.blank(d, i)
    fixed, on_panel, moving = {}, {}, {}
    if c in ("H", "B", "Q"):
        hk = [hook(d, i, x, L) for x in (-L.hook_x, L.hook_x)]
        cuts = notches(d, i, L)
        frame = {k: (pf.one_solid(so.unsplit(s.cut(cuts)), k) if k.startswith("frame") else s) for k, s in frame.items()}
        panel_add, panel_cut = list(hk), []
        if c == "B":
            frame = resplit(frame, L.frame_split_x, i.half_gap)
            left = so.unsplit(frame["frame_left"].cut(front_notch(d, i, L)).fuse(tunnel(d, i, L)))
            frame["frame_left"] = pf.one_solid(left, "frame, left half, with the tunnel of the bolt")
            panel_cut.append(bolt_room(L))
            panel_add.append(strike(d, i, L))
            fixed = {"latch_gate": gate(L)}
            moving = {"latch_bolt": bolt(d, L)}
        if c == "Q":
            clear, bosses, holes = cam_holes(d, L)
            arcade = add_to_tiles(arcade, [], clear)
            blank = add_to_tiles(blank, [], clear)
            panel_add += bosses
            for x, side in ((-L.cam_x, "left"), (L.cam_x, "right")):
                for k, s in cam(d, L, x).items():
                    on_panel[f"{k}_{side}"] = s
        arcade = add_to_tiles(arcade, panel_add, panel_cut)
        blank = add_to_tiles(blank, panel_add, panel_cut)
        if c == "Q":
            arcade = add_to_tiles(arcade, [], holes)
            blank = add_to_tiles(blank, [], holes)
        if c == "B":
            blank = finger_hole(d, blank, L)
    return Candidate(c, d, i, L, frame, fixed, arcade, blank, on_panel, moving)


# ---------- the motion ----------

@dataclass(frozen=True)
class Step:
    """One position of the way out: the latch moved (the bolt back by `bolt`, the cams turned by `cam`), the panel
    turned by `swing` degrees about the pivot (its front up), then moved by `lift` (y, z)."""
    name: str
    bolt: float = 0.0
    cam: float = 0.0
    swing: float = 0.0
    lift: tuple = (0.0, 0.0)


def way_out(c: str, L: Latch = L0) -> list[Step]:
    if c == "M":
        return [Step("seated")] + [Step(f"lifted {z:g}", lift=(0.0, z)) for z in (2.0, 5.0, 10.0, 20.0, 40.0, 80.0)]
    pre: list[Step] = []
    if c == "B":
        pre = [Step(f"bolt back {s:g}", bolt=s) for s in (1.0, 2.5, L.stroke)]
    if c == "Q":
        pre = [Step(f"cams turned {t:g}", cam=t) for t in (15.0, 30.0, 45.0, 60.0, 75.0, 90.0)]
    b, t = (L.stroke if c == "B" else 0.0), (90.0 if c == "Q" else 0.0)
    swing = [Step(f"front up {a:g} degrees", bolt=b, cam=t, swing=a) for a in (1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 13.0, 16.0, 20.0)]
    out = [Step(f"up and forward {k}", bolt=b, cam=t, swing=20.0, lift=(-2.0 * k, 6.0 * k)) for k in (1, 2, 4, 8, 16)]
    return [Step("seated")] + pre + swing + out


def placed(shape: Part.Shape, st: Step, d: Blueprint, i: pf.Interface) -> Part.Shape:
    """A part of the panel at a step: turned about the pivot, then moved."""
    out = shape
    if st.swing:
        yp, zp = pivot(d, i)
        # the front (smaller y) goes up: a turn about +x by -swing
        out = out.rotated(V(0, yp, zp), V(1, 0, 0), -st.swing)
    if st.lift != (0.0, 0.0):
        out = out.translated(V(0, *st.lift))
    return out


def motion_rows(cd: Candidate, hw: pf.Hardware, skin: Part.Shape) -> list[dict]:
    """The real way out in steps: at each step the common volume of the moving group (the arcade panel with its
    hardware and its latch parts) with what stays (the skin of the deck, the frame, the housing, the bolt where it is).
    A row also checks the latch parts in the cabinet that move (the bolt) against what stays and the seated panel."""
    d, i = cd.d, cd.i
    panel = [*cd.arcade.values(), *[s.world for s in hw.solids(("Panel",), ("hardware", "protrusion"))]]
    still_base = [skin, *cd.frame.values(), *cd.fixed.values()]
    rows = []
    for st in way_out(cd.c, cd.L):
        moving = list(panel)
        if cd.c == "Q":
            for x, side in ((-cd.L.cam_x, "left"), (cd.L.cam_x, "right")):
                moving += list(cam(d, cd.L, x, st.cam).values())
        else:
            moving += list(cd.on_panel.values())
        group = Part.makeCompound([placed(s, st, d, i) for s in moving])
        still = list(still_base)
        if cd.c == "B":
            still.append(bolt(d, cd.L, st.bolt))
        vol = sum(pf.common_volume(group, s) for s in still)
        rows.append({"step": st.name, "swing": st.swing, "lift": list(st.lift), "bolt": st.bolt, "cam": st.cam,
                     "common_mm3": round(vol, 3), "result": "FAIL" if vol > pf.TOL else "PASS"})
    if cd.c == "B":
        seated = Part.makeCompound(list(cd.arcade.values()))
        for s in (0.0, 1.0, 2.5, cd.L.stroke):
            b = bolt(d, cd.L, s)
            vol = sum(pf.common_volume(b, x) for x in [skin.cut(button_hole(cd.L)), *cd.frame.values(), *cd.fixed.values()])
            rows.append({"step": f"the bolt alone, back {s:g}, against the deck, the frame and the housing", "bolt": s, "common_mm3": round(vol, 3),
                         "result": "FAIL" if vol > pf.TOL else "PASS"})
        b = bolt(d, cd.L, cd.L.stroke)
        vol = pf.common_volume(b, seated)
        rows.append({"step": "the bolt back by the stroke, against the seated panel", "bolt": cd.L.stroke, "common_mm3": round(vol, 3),
                     "result": "FAIL" if vol > pf.TOL else "PASS"})
    return rows


def locked_rows(cd: Candidate) -> list[dict]:
    """The lock really holds: with the latch locked, a small lift (1 mm) or a small swing (1 degree) of the panel
    makes the latch parts meet. A row FAILS when the panel could leave without the release."""
    d, i = cd.d, cd.i
    if cd.c == "M":
        return []
    rows = []
    hooks = [hook(d, i, x, cd.L) for x in (-cd.L.hook_x, cd.L.hook_x)]
    frame = Part.makeCompound([cd.frame["frame_left"], cd.frame["frame_right"]])
    up = Step("lift 1", lift=(0.0, 1.0))
    vol = sum(pf.common_volume(placed(h, up, d, i), frame) for h in hooks)
    rows.append({"what": "rear hooks: a straight lift of 1 meets the roofs of the notches", "common_mm3": round(vol, 3), "result": "PASS" if vol > pf.TOL else "FAIL"})
    if cd.c in ("B", "Q"):
        tilt = Step("swing 2", swing=2.0)
        if cd.c == "B":
            part, other = strike(d, i, cd.L), bolt(d, cd.L)
            vol = pf.common_volume(placed(part, tilt, d, i), other)
            rows.append({"what": "bolt locked: a swing of 2 degrees makes the lips meet the bolt", "common_mm3": round(vol, 3), "result": "PASS" if vol > pf.TOL else "FAIL"})
        else:
            tongues = [cam(d, cd.L, x)["cam_tongue"] for x in (-cd.L.cam_x, cd.L.cam_x)]
            vol = sum(pf.common_volume(placed(t, tilt, d, i), frame) for t in tongues)
            rows.append({"what": "cams locked: a swing of 2 degrees makes the tongues meet the front bar", "common_mm3": round(vol, 3), "result": "PASS" if vol > pf.TOL else "FAIL"})
    return rows


# ---------- the hold ----------

def restraints(cd: Candidate) -> list[dict]:
    """Every point that holds the panel down: (x, y), what it is, its capacity in N, and whether it acts in the
    swing about the pivot (a hook does not: the swing is how it lets go)."""
    d, i, L = cd.d, cd.i, cd.L
    pull = magnet_pull(L.frame_magnet_h[cd.c], L.plate_magnet_h, L)["pull_N"]
    pts = pf.latch_points(d, i)
    out = [{"what": f"magnet pair {k}", "at": pts[k], "cap": pull, "kind": "magnet", "swing": True} for k in L.magnet_points[cd.c]]
    yp, _ = pivot(d, i)
    st = strength(cd)
    if cd.c in ("H", "B", "Q"):
        y = rear_bar_face(d, i) - L.stem_gap - L.stem_t / 2
        out += [{"what": f"rear hook x {x:g}", "at": (x, y), "cap": st["hook_N"], "kind": "hook", "swing": False} for x in (-L.hook_x, L.hook_x)]
    if cd.c == "B":
        out.append({"what": "push bolt", "at": (0.0, sum(L.lug_y) / 2), "cap": st["strike_N"], "kind": "lock", "swing": True})
    if cd.c == "Q":
        out += [{"what": f"cam x {x:g}", "at": (x, front_bar_face(d, i) - 3.0), "cap": st["cam_N"], "kind": "lock", "swing": True} for x in (-L.cam_x, L.cam_x)]
    return out


def strength(cd: Candidate) -> dict:
    """Hand estimates of what each rigid latch part carries before printed ABS yields (ESTIMATED: beam theory, a
    strength along the layers and a lower one across them). The weakest section of each part sets its value."""
    L = cd.L
    out = {}
    # the hook: the stem is in tension and bending across the layers (the tile prints top face down, so the stem
    # stands upright on the printer); the toe's load is toe_arm in front of the middle of the stem
    w, t = L.hook_w, L.stem_t
    arm = L.stem_t / 2 + L.stem_gap + L.notch_back / 2
    out["hook_N"] = round(L.abs_across / (1 / (w * t) + arm / (w * t ** 2 / 6)), 0)
    # the strike: two legs in tension and bending across the layers; a lip in bending along the layers
    leg = L.lug_leg_t
    ly = L.lug_y[1] - L.lug_y[0]
    lip_arm = L.lug_lip / 2 + leg / 2
    leg_N = 2 * L.abs_across / (1 / (leg * ly) + lip_arm / (ly * leg ** 2 / 6))
    lip_t = L.bolt_z[0] - L.bolt_clear - L.lug_z0
    lip_N = 2 * L.abs_along * (ly * lip_t ** 2 / 6) / (L.lug_lip / 2)
    # the roof of the tunnel: the bolt pushes up on its front edge, between the two walls (a beam of the span between
    # them, as wide as the contact, about 8); it prints with the frame, so the stress lies along the layers
    ct = L.roof_z[1] - L.roof_z[0]
    span = L.bolt_w + 2 * L.bolt_clear
    cover_N = L.abs_along * (8.0 * ct ** 2 / 6) / (span / 4)
    out["strike_N"] = round(min(leg_N, lip_N, cover_N), 0)
    out["strike_parts_N"] = {"legs": round(leg_N), "lips": round(lip_N), "roof": round(cover_N)}
    # the cam: the tongue bends along the layers (it prints flat); the shank is in tension across the layers
    tw, tl, tt = L.cam_tongue
    tongue_N = L.abs_along * (tw * tt ** 2 / 6) / (tl - L.cam_hub_d / 2 - 2.5)
    shank_N = L.abs_across * math.pi * (L.cam_shank_d / 2) ** 2
    out["cam_N"] = round(min(tongue_N, shank_N), 0)
    out["cam_parts_N"] = {"tongue": round(tongue_N), "shank": round(shank_N)}
    return out


def lever_point(d: Blueprint) -> tuple[float, float]:
    lay = fit.Layout()
    return lay.stick_x, pf.y0(d) + lay.stick_y_share * d.panel_d


def ball_z(d: Blueprint, v) -> float:
    return d.panel_top + v("stick_ball_cz")


def load_cases(cd: Candidate, v) -> list[dict]:
    """The load cases at the ball of the lever: a force (fx, fy, fz)."""
    L = cd.L
    out = [{"name": f"pull up {L.pull_up:g}", "f": (0.0, 0.0, L.pull_up)}]
    for name, (ux, uy) in (("to the front", (0, -1)), ("to the rear", (0, 1)), ("to the left", (-1, 0)), ("to the right", (1, 0))):
        out.append({"name": f"side {L.side:g} {name}", "f": (L.side * ux, L.side * uy, 0.0)})
        out.append({"name": f"pull up {L.pull_up:g} and side {L.side:g} {name}", "f": (L.side * ux, L.side * uy, L.pull_up)})
    return out


def mechanisms(d: Blueprint, i: pf.Interface):
    """The ways a rigid plate on its ledge can leave it: a straight lift, or a turn about a line in the rest plane that
    touches the outline of the plate or lies outside it (a point of the plate cannot go down into the ledge). Yields
    (name, up(x, y) -> upward movement for a unit turn, turn vector, a point of the line, is_swing)."""
    zr = pf.z_rest(d)
    yield ("straight lift", lambda x, y: 1.0, None, None, False)
    yp, _ = pivot(d, i)
    outline = pr.panel_outline(d, -i.seat_gap)
    for deg in range(0, 360, 2):
        a = math.radians(deg)
        t = (math.cos(a), math.sin(a))
        nrm = (-t[1], t[0])
        tangent = min(x * nrm[0] + y * nrm[1] for x, y in outline)
        for extra in (0.0, 10.0, 30.0, 80.0, 200.0, 500.0):
            c = tangent - extra
            p0 = (nrm[0] * c, nrm[1] * c)
            up = (lambda nrm, c: (lambda x, y: x * nrm[0] + y * nrm[1] - c))(nrm, c)
            swing = extra == 0.0 and abs(t[1]) < math.sin(math.radians(3)) and nrm[1] < 0 and abs(-c - yp) < 1.0
            yield (f"turn about a line at {deg} degrees, {extra:g} outside the plate", up, (t[0], t[1], 0.0), (p0[0], p0[1], zr), swing)


def hold(cd: Candidate, v, preload_only: bool = False, loads: list[dict] | None = None, point: tuple | None = None, released: bool = False) -> dict:
    """The factor of the latch for each load case: for every way the plate can leave its ledge, the work that the
    restraints and the weight can do against the work of the load; the smallest ratio. A plate point that goes down
    rests on the ledge, which takes any load. With preload_only the rigid parts with play (the hooks; the cams; the
    bolt beyond its wedge) do not count: what is left must hold the normal play without a click."""
    d, i, L = cd.d, cd.i, cd.L
    lx, ly = lever_point(d)
    bz = ball_z(d, v)
    if point is not None:
        lx, ly, bz = point
    res = restraints(cd)
    if released:
        res = [r for r in res if r["kind"] != "lock"]
    if preload_only:
        res = [r for r in res if r["kind"] == "magnet"]
        if cd.c == "B":
            res.append({"what": "wedge of the bolt (preload)", "at": (0.0, sum(L.lug_y) / 2), "cap": bolt_preload(L)["net_N"], "kind": "wedge", "swing": True})
    cy = pf.y0(d) + d.panel_d / 2
    out = []
    for case in (loads or load_cases(cd, v)):
        fx, fy, fz = case["f"]
        best = (math.inf, "", "")
        for name, up, t, p0, swing in mechanisms(d, i):
            if t is None:
                work = fz
                resist = sum(r["cap"] for r in res) + L.panel_weight
                gov = "all"
            else:
                rx, ry, rz = lx - p0[0], ly - p0[1], bz - p0[2]
                # displacement of the ball for a unit turn t x r
                dx, dy, dz = t[1] * rz - 0 * ry, 0 * rx - t[0] * rz, t[0] * ry - t[1] * rx
                work = fx * dx + fy * dy + fz * up(lx, ly)
                resist = -L.panel_weight * up(0.0, cy)
                terms = [(r["cap"] * max(0.0, up(*r["at"])), r["what"]) for r in res if not (swing and not r["swing"])]
                resist += sum(x for x, _ in terms)
                gov = max(terms, default=(0, ""))[1]
            if work <= 1e-9:
                continue
            f = resist / work
            if f < best[0]:
                best = (f, name, gov)
        out.append({"case": case["name"], "factor": round(best[0], 2), "mechanism": best[1], "governs": best[2]})
    return {"rows": out, "factor": min(r["factor"] for r in out)}


def bolt_preload(L: Latch = L0) -> dict:
    """B: the spring pushes the bolt forward; the wedge of wedge_deg turns that into a pull down on the strike. The
    wedge holds by friction when tan(wedge) < mu. The push on the button: the spring, and the friction of the wedge
    less its slope while the bolt starts back; at the end of the stroke the spring and some friction in the tunnel."""
    comp = L.bolt_spring_free - spring_length(L, 0.0)
    p_lock = L.bolt_spring_rate * comp
    p_full = L.bolt_spring_rate * (comp + L.stroke)
    a, phi = math.radians(L.wedge_deg), math.atan(L.mu)
    down = p_lock / math.tan(a + phi)
    start = p_lock + down * (L.mu * math.cos(a) - math.sin(a))
    free_at = L.lug_y[1] - neck(L)[1]
    return {"spring_lock_N": round(p_lock, 1), "spring_full_N": round(p_full, 1), "spring_compressed_mm": [round(comp, 1), round(comp + L.stroke, 1)],
            "wedge_down_N": round(down, 1), "net_N": round(down, 1), "self_locking": math.tan(a) < L.mu, "mu_needed": round(math.tan(a), 3),
            "button_start_N": round(start, 1), "button_force_N": round(p_full + 2.0, 1), "unlocks_at_mm": round(free_at, 2), "stroke_mm": L.stroke}


def ramp_option(cd: Candidate, v) -> dict:
    """The grip that B does not take (ESTIMATED): a rigid ramp of 45 degrees on the bolt that lifts the strike by
    `rise` after the lips are free. The bolt must then travel further, and the button must lift the front against
    the magnets through the ramp."""
    d, L, i = cd.d, cd.L, cd.i
    rise = 2.5
    p = bolt_preload(L)
    travel = p["unlocks_at_mm"] + 0.5 + rise + 0.5
    ys = sum(L.lug_y) / 2
    lift = hold(cd, v, loads=[{"name": "up 1", "f": (0.0, 0.0, 1.0)}], point=(0.0, ys, d.panel_top), released=True)["rows"][0]["factor"]
    phi = math.atan(L.mu)
    spring = L.bolt_spring_rate * (p["spring_compressed_mm"][0] + travel)
    yp, _ = pivot(d, i)
    front = rise * (yp - pf.y0(d)) / (yp - ys)
    return {"rise_at_strike_mm": rise, "travel_mm": round(travel, 1), "lift_at_strike_N": round(lift, 1),
            "button_N": round(spring + lift * math.tan(math.radians(45.0) + phi), 0), "front_edge_rise_mm": round(front, 1),
            "above_deck_top_mm": round(front - (d.deck_top - d.panel_top), 1)}


def corner_rock(cd: Candidate, v) -> dict:
    """The front corners under the lever's couple, with the plate not rigid (a beam estimate, ESTIMATED).

    A push at the ball to the rear lifts the front edge. The couple goes into the two ribs of the lever's bay (the
    rib beside the encoder and the flanges of the seam) and each puts half of M / span up at the front edge. The
    front strip of the plate (the plate from the front edge to yl 40, with the front rib) is a beam along x. It is
    held down by the bolt at x 0. Without front magnets the left end of the strip is free (a cantilever from the
    bolt): the front left corner lifts. With a magnet pair at the front left pad the strip is a beam held at the bolt
    and at the magnet; the magnet keeps the corner down while its share stays below its pull."""
    d, i, L, a = cd.d, cd.i, cd.L, pf.Arcade()
    e = pf.structure.E_ABS
    h = pf.holes(d, a, v)
    rl0, rl1 = pf.rib_left(i, h)
    xs = [-(rl0 + rl1) / 2, -pf.seam_x(a)]           # distances of the two ribs from the bolt
    span = d.panel_d - 2 * i.ledge
    arm = ball_z(d, v) - pf.z_rest(d)
    ii = pf.tee(40.0, d.panel_t, i.rib_t, i.rib_h)
    corner = -pr.panel_outline(d, -i.seat_gap)[0][0]
    xm = -pf.latch_points(d, i)[0][0]
    pull = magnet_pull(L.frame_magnet_h[cd.c], L.plate_magnet_h, L)["pull_N"]

    def cant(x: float, at: float, p: float) -> float:
        return p * x ** 2 * (3 * at - x) / (6 * e * ii) if x <= at else p * at ** 2 * (3 * x - at) / (6 * e * ii)

    def ss(x: float, at: float, p: float, ln: float) -> float:
        b = ln - at
        if x <= at:
            return p * b * x * (ln ** 2 - b ** 2 - x ** 2) / (6 * ln * e * ii)
        return ss(ln - x, b, p, ln)

    rows = []
    for name, f in (("normal play", L.play), ("hard input", L.side)):
        p = f * arm / span / 2
        free_corner = sum(cant(corner, x, p) for x in xs)
        free_rib = sum(cant(xs[0], x, p) for x in xs)
        held_rib = max(sum(ss(t, x, p, xm) for x in xs) for t in [k * xm / 40 for k in range(1, 40)])
        share = sum(p * x / xm for x in xs)
        rows.append({"case": f"{name}: {f:g} N at the ball, to the rear", "front_lift_N": round(2 * p, 2),
                     "no_front_magnets": {"corner_lift_mm": round(free_corner, 3), "lift_at_encoder_rib_mm": round(free_rib, 3)},
                     "front_magnets": {"largest_lift_mm": round(held_rib, 3), "corner_share_N": round(share, 2), "magnet_N": pull, "factor": round(pull / share, 1)}})
    return {"E_MPa": e, "I_strip_mm4": round(ii), "strip": "plate 5 x 40 with the front rib 3 x 15", "ribs_x": [round(-x, 1) for x in xs],
            "corner_x": round(-corner, 1), "magnet_x": round(-xm, 1), "rows": rows}


# ---------- the flexing features and the wear ----------

def strain_rows(cd: Candidate) -> list[dict]:
    """The strain of each feature that bends when the latch moves. A rigid part that only slides or turns has none."""
    L = cd.L
    rows = []
    if cd.c == "B":
        rows.append({"feature": "push bolt, strike, housing", "moves": "slides 5 along y", "strain_pct": 0.0, "note": "rigid: nothing bends; the steel spring takes the travel"})
        rows.append({"feature": "spring of the bolt (steel, bought)", "moves": f"{L.bolt_spring_free - 18.0:g} to {L.bolt_spring_free - 13.0:g} shorter", "strain_pct": None, "note": "a steel spring does not creep"})
    if cd.c == "Q":
        rows.append({"feature": "cam", "moves": "turns 90", "strain_pct": 0.0, "note": f"rigid; the tongue stands {L.cam_tongue_clear:g} below the bar"})
    if cd.c in ("H", "B", "Q"):
        rows.append({"feature": "rear hooks", "moves": "swing in and out of the notches", "strain_pct": 0.0, "note": f"rigid; the toe stands {L.toe_clear:g} below the roof"})
    rows.append({"feature": "magnets", "moves": "lift off", "strain_pct": 0.0, "note": "no printed part bends"})
    # the detent, which this study does not build: a printed cantilever that must hold the panel's edge
    return rows


def detent(L: Latch = L0, hold_N: float = 40.0) -> dict:
    """The detent that the study does not build (candidate D): a printed arm with a bump on its end that drops into a
    groove. It lets go above its hold. To hold hold_N with a ramp of 45 degrees and mu, the arm must push the bump
    with P = hold / tan(45 + phi); the arm of length l, width w, thickness t then bends by P l^3 / (3 E I)."""
    a, phi = math.radians(45.0), math.atan(L.mu)
    p = hold_N / math.tan(a + phi)
    bump = 1.0
    for t in (2.0, 2.5, 3.0, 4.0):
        w, l = 10.0, 20.0
        i = w * t ** 3 / 12
        k = 3 * L.abs_e * i / l ** 3
        defl = p / k
        if defl >= bump:
            strain = 3 * t * bump / (2 * l ** 2)
            return {"hold_N": hold_N, "push_N": round(p, 1), "arm": [l, w, t], "bump_mm": bump, "strain_pct": round(strain * 100, 2),
                    "release_on_lever_N": round(hold_N / 0.51, 0), "note": "the bend is only while the panel goes in or out"}
    return {"hold_N": hold_N, "push_N": round(p, 1), "note": "no arm found"}


def wear(c: str) -> list[str]:
    common = ["The magnets do not wear. Their adhesive can let go after many swaps: use epoxy, and a pocket that holds the magnet by its rim."]
    if c in ("H", "B", "Q"):
        common.append("The front edge of the roof of each notch and the top of each toe rub when the hooks go in. ABS on ABS: a polished mark after some hundreds of swaps, no loss of fit.")
    if c == "B":
        common += ["The lips of the strike and the wedge under the bolt rub each time it locks. If the wedge wears smooth, the friction falls: the wedge of 8 degrees still holds while mu is above 0.14. The bolt is a part of its own: print a new one.",
                   "The button rubs in the hole of the deck wall. The hole has a chamfer; a dry PTFE spray is enough."]
    if c == "Q":
        common += ["The tongue rubs under the front bar at each turn. The head of each cam is turned by a finger; its finger bar wears smooth first."]
    if c == "M":
        common += ["The cones and their sockets locate the panel each time it goes in. They wear little: they do not carry the lift."]
    return common


# ---------- the checks ----------

def print_rows(parts: dict[str, Part.Shape]) -> list[dict]:
    """Each printed part on the printer, in its orientation (the tiles, the frame and the posts as panel_frame has
    them; the bolt on its side, the housing on its floor, the cover on its top, the cam stud on its head, the
    tongue flat)."""
    lim = split.printer()
    up_of = {"latch_bolt": (V(1, 0, 0), "on its side: the profile in y and z on the bed"),
             "latch_gate": (V(0, -1, 0), "flat, its rear face on the bed"),
             "cam_stud": (V(0, 0, 1), "upright, the end of the shank on the bed"),
             "cam_tongue": (V(0, 0, 1), "flat, the arm on the bed")}
    rows = []
    for name, shape in parts.items():
        key = next((k for k in up_of if name.startswith(k)), None)
        up, how = up_of[key] if key else pf.PRINT[pf.kind(name)]
        # the points of a mesh, not the vertices: a round part has few vertices on its outline
        pts = [(p.x, p.y, p.z) for p in shape.tessellate(0.5)[0]]
        b = split.print_box(pts, (up.x, up.y, up.z), lim)
        rows.append({"part": name, "how": how, "x": b["x"], "y": b["y"], "z": b["z"], "fits": b["fits"],
                     "overhang_cm2": round(pf.overhang(shape, up) / 100, 2), "mass_g": round(shape.Volume * pf.ABS, 1)})
    return rows


def shown_edges(shape: Part.Shape, d: Blueprint, where) -> list[list[float]]:
    """The convex edges of a part that turn more than edge_break_turn, have no round, and lie where `where` says the
    part shows."""
    out = []
    for e in shape.Edges:
        fs = shape.ancestorsOfType(e, Part.Face)
        if e.Degenerated or len(fs) != 2:
            continue
        convex, turn = so.edge_turn(shape, e)
        m = so.middle(e)
        if convex and turn > d.edge_break_turn and where(m):
            out.append([round(m.x, 1), round(m.y, 1), round(m.z, 1)])
    return out


def finish(cd: Candidate) -> tuple[dict, list[str], dict]:
    """The edge rule and the face check (panel_frame.finish_rows, with the tools of the shell) on each group of parts,
    and the rule for the faces that show outside the pocket: the button on the front face of the deck, the head of a
    cam above the plate."""
    d, i = cd.d, cd.i
    rows, bad, faces = {}, [], {}
    groups = [{**cd.arcade}, {**cd.blank}, {**cd.frame}] + [{k: s} for k, s in {**cd.fixed, **cd.moving, **cd.on_panel}.items()]
    for g in groups:
        r, b, f = pf.finish_rows(g, d, i)
        rows.update(r)
        bad += b
        faces.update(f)
    for name, shape in cd.moving.items():
        sharp = shown_edges(shape, d, lambda m: m.y < 4.0)
        rows[name]["shows"] = sharp
        if sharp:
            bad.append(f"edge rule: {name}: {len(sharp)} sharp edges show on the front face of the deck, at {sharp[0]}")
    for name, shape in cd.on_panel.items():
        sharp = shown_edges(shape, d, lambda m: m.z > d.panel_top - 1e-6)
        rows[name]["shows"] = sharp
        if sharp:
            bad.append(f"edge rule: {name}: {len(sharp)} sharp edges show above the plate, at {sharp[0]}")
    return rows, bad, faces


def check(cd: Candidate, deck: Part.Shape, hw: pf.Hardware, v, log=lambda text: None) -> dict:
    """Every check of a candidate. "failures" is empty when all pass."""
    d, i = cd.d, cd.i
    reach = 32.0 if cd.c == "B" else 16.0
    skin = pf.pocket_skin(d, deck, reach)
    if cd.c == "B":
        skin = skin.cut(button_hole(cd.L))
    log(f"{cd.c}: clashes")
    fixed = {**cd.frame, **cd.fixed, **cd.moving}
    clashes = pf.clash_rows({**fixed, **cd.arcade, **cd.on_panel}, skin, hw)
    clashes_blank = [r for r in pf.clash_rows({**fixed, **cd.blank}, skin, hw, ("USB", "Hub")) if r["part"].startswith("blank") or r["against"].startswith("blank")]
    log(f"{cd.c}: room")
    space = pf.room(d, i, cd.frame, hw)
    if cd.c == "B":
        space = pf.one_solid(space.cut(bolt_room(cd.L)), "the room less the housing of the bolt")
    # the room of a panel with hooks takes in the two notches; B's also the place of the strike (inside the box of
    # the bolt)
    extra = []
    if cd.c in ("H", "B", "Q"):
        extra += [n.common(pf.box(-so.BIG, so.BIG, -so.BIG, so.BIG, -so.BIG, pf.z_rest(d))) for n in notches(d, i, cd.L)]
    if cd.c == "Q":
        extra += [cam(d, cd.L, x)["cam_tongue"] for x in (-cd.L.cam_x, cd.L.cam_x)]
    if cd.c == "B":
        b = strike(d, i, cd.L).BoundBox
        extra.append(pf.box(b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
    if extra:
        space = so.unsplit(space.fuse(extra))
    keep = {**cd.frame, **cd.fixed}
    rooms = pf.room_rows(space, d, keep, skin, hw, {**cd.arcade, **cd.on_panel})
    log(f"{cd.c}: way out")
    motion = motion_rows(cd, hw, skin)
    locks = locked_rows(cd)
    log(f"{cd.c}: print, edges")
    prints = print_rows(cd.printed)
    edges, bad, faces = finish(cd)
    log(f"{cd.c}: hold")
    held = hold(cd, v)
    play = hold(cd, v, preload_only=True, loads=[{"name": f"play {cd.L.play:g} {k}", "f": f} for k, f in
                                                   (("to the front", (0, -cd.L.play, 0)), ("to the rear", (0, cd.L.play, 0)),
                                                    ("to the left", (-cd.L.play, 0, 0)), ("to the right", (cd.L.play, 0, 0)))])
    release = removal(cd, v)
    failures = [f"clash: {r['part']} / {r['against']}: {r['common_mm3']} mm3" for r in clashes + clashes_blank if r["result"] == "FAIL"]
    failures += [f"room: {r['what']}: {r['common_mm3']} mm3" for r in rooms if r["result"] == "FAIL"]
    failures += [f"way out: {r['step']}: {r['common_mm3']} mm3" for r in motion if r["result"] == "FAIL"]
    failures += [f"lock: {r['what']}" for r in locks if r["result"] == "FAIL"]
    failures += [f"print: {r['part']} does not fit the printer" for r in prints if not r["fits"]]
    failures += bad
    return {"candidate": cd.c, "name": NAMES[cd.c], "interface": asdict(i), "latch": {k: getattr(cd.L, k) for k in ()},
            "magnet": magnet_pull(cd.L.frame_magnet_h[cd.c], cd.L.plate_magnet_h, cd.L), "restraints": restraints(cd), "strength": strength(cd),
            "hold": held, "play": play, "removal": release, "preload": bolt_preload(cd.L) if cd.c == "B" else None,
            "corner_rock": corner_rock(cd, v) if cd.c == "B" else None, "ramp_option": ramp_option(cd, v) if cd.c == "B" else None,
            "clashes": clashes, "clashes_blank": clashes_blank, "room_volume_cm3": round(space.Volume / 1000, 1), "room": rooms,
            "motion": motion, "locks": locks, "print": prints, "strain": strain_rows(cd), "wear": wear(cd.c), "edge_finish": edges,
            "face_check": faces, "shows": shows(cd), "buy": buy(cd), "interface_rows": interface_rows(cd), "failures": failures}


def removal(cd: Candidate, v) -> dict:
    """What it takes to free the panel after the release (the latch open): the smallest upward pull that lifts it out,
    found as the hold is (every way the plate can leave its ledge, the hooks free in the swing), at the ball of the
    lever, at the middle of the front edge, and (B) at the finger hole of a panel with nothing to hold."""
    d, L = cd.d, cd.L
    up = [{"name": "up 1", "f": (0.0, 0.0, 1.0)}]
    zt = d.panel_top
    at = {"lever": None, "front edge": (0.0, pf.y0(d) + 3.0, zt)}
    if cd.c == "B":
        at["finger hole"] = (L.finger_hole[0], pf.y0(d) + L.finger_hole[1], zt)
    f = {k: round(hold(cd, v, loads=up, point=p, released=True)["rows"][0]["factor"], 1) for k, p in at.items()}
    pull = magnet_pull(L.frame_magnet_h[cd.c], L.plate_magnet_h, L)["pull_N"]
    n = len(L.magnet_points[cd.c])
    if cd.c == "M":
        how = f"pull the lever up with {f['lever']:g} N; the magnets on the lever's side let go first. A panel with no lever has no grip."
    elif cd.c == "H":
        how = f"pull the lever up with {f['lever']:g} N: the front magnets let go and the panel swings about its rear edge. A panel with no lever has no grip."
    elif cd.c == "Q":
        how = f"turn the two heads a quarter turn; lift the front by the lever ({f['lever']:g} N) or by the two finger bars."
    else:
        p = bolt_preload(L)
        how = (f"hold the button in (it starts at {p['button_start_N']:g} N, {p['button_force_N']:g} N at the end of its {L.stroke:g}) and lift the panel by the lever "
               f"({f['lever']:g} N) or, a panel with nothing to hold, by its finger hole ({f['finger hole']:g} N). The {n} magnets ({pull:g} N each) are all that hold it then.")
    return {"lever_N": f["lever"], "front_edge_N": f["front edge"], "finger_hole_N": f.get("finger hole"), "how": how}


def shows(cd: Candidate) -> dict:
    """What shows of the latch, with the panel in and with the panel out."""
    L = cd.L
    gap = cd.i.seat_gap
    base_out = "The frame in the opening: the four pads with their magnets, the two cones at the rear edge, the cable clip."
    if cd.c == "M":
        return {"top_in": "Nothing. The gap round the panel stays 0.3 all round.", "front_in": "Nothing.", "out": base_out, "gap": f"{gap:g} all round, no change"}
    hooks_out = f" Two notches {L.hook_w + 2 * L.notch_side:g} wide in the rear bar under the ledge, at x -{L.hook_x:g} and +{L.hook_x:g}."
    if cd.c == "H":
        return {"top_in": "Nothing. The gap stays 0.3 all round.", "front_in": "Nothing.", "out": base_out + hooks_out, "gap": f"{gap:g} all round, no change"}
    if cd.c == "B":
        return {"top_in": "Nothing. The gap stays 0.3 all round.",
                "front_in": f"A button of {L.button_d:g} with two flats ({L.bolt_w:g} wide) in the front face of the deck at the centre line, {L.button_z:g} above the desk, on the leaning band above the crease. It is flush, with a gap of {(L.button_hole_d - L.button_d) / 2:g} round it and an edge break on its rim.",
                "out": base_out + hooks_out + " At the front centre: the bolt across the front bar, and its tunnel (a part of the frame) with the tab of the gate at its rear.",
                "gap": f"{gap:g} all round, no change. A panel with nothing to hold has a finger hole of {L.finger_hole[2]:g} near its front edge; the arcade panel has none."}
    return {"top_in": f"Two round heads of {L.cam_head_d:g} at x -{L.cam_x:g} and +{L.cam_x:g}, {L.cam_y - pf.y0(cd.d):.0f} behind the front edge of the panel. Each is flush with the plate and has a finger bar {L.cam_bar[2]:g} high (it stays {cd.d.deck_top - cd.d.panel_top - L.cam_bar[2]:g} below the deck top).",
            "front_in": "Nothing.", "out": base_out + hooks_out, "gap": f"{gap:g} all round, no change"}


def buy(cd: Candidate) -> list[str]:
    L = cd.L
    n = len(L.magnet_points[cd.c])
    h = L.frame_magnet_h[cd.c]
    frame = f"{n} disc magnets N52 12 x {h:g}, axial" if h <= 5 else f"{2 * n} disc magnets N52 12 x 5, axial (two stacked in each pad)"
    out = [frame + " (frame, once for the cabinet)", f"{n} disc magnets N52 12 x {L.plate_magnet_h:g}, axial, for each panel (or {n} steel discs 12 x 2: no polarity to mind, ESTIMATED 10 % less pull)",
           "Epoxy for the magnets"]
    if cd.c == "B":
        out += [f"1 compression spring, steel, {L.bolt_spring_d:g} outside, {L.bolt_spring_free:g} free, about {L.bolt_spring_rate:g} N/mm (the bolt)"]
    if cd.c == "Q":
        out += [f"2 steel dowel pins {L.cam_pin_d:g} x 14 for each panel (tongue to stud)", "2 O-rings 8 x 2 (inside 8, section 2) for each panel, on the shank under the plate"]
    return out


def interface_rows(cd: Candidate) -> list[list[str]]:
    """The rows of the interface table that the candidate adds or changes."""
    L, d = cd.L, cd.d
    yl = lambda y: f"yl {y - pf.y0(d):.1f}"
    rows = [["Latch points (4)", f"Magnet: a pocket of 12.2 x 2.2 in the lower face, a disc of 12 x {L.plate_magnet_h:g} in it (option B, no change). Each panel has the 4 pockets."]]
    if cd.c in ("H", "B", "Q"):
        yp, zp = pivot(d, cd.i)
        rows.append(["Rear hooks (2)", f"At x -{L.hook_x:g} and +{L.hook_x:g}, {L.hook_w:g} wide. A stem {L.stem_t:g} thick under the plate, its rear face at {yl(rear_bar_face(d, cd.i) - L.stem_gap)}; "
                     f"a toe whose top and bottom are arcs of R {math.hypot(yp - rear_bar_face(d, cd.i) + cd.i.bond_gap, zp - L.notch_top) + L.toe_clear:.1f} and R {L.toe_r_out:g} about the rear top edge of the plate (yl {yp - pf.y0(d):.1f}, z {zp:g}). "
                     f"Its tip at {yl(rear_bar_face(d, cd.i) + L.notch_back - L.toe_tip_gap)}. A blank panel prints them with its tiles."])
    if cd.c == "B":
        rows.append(["Strike (1)", f"At the front centre, {yl(L.lug_y[0])} to {yl(L.lug_y[1])}: two legs each side of x 0 ({L.bolt_w / 2 + L.bolt_clear:g} to {L.bolt_w / 2 + L.bolt_clear + L.lug_leg_t:g}), down to z {L.lug_z0:g}, each with a lip {L.lug_lip:g} in under the bolt; the top of each lip falls {L.wedge_deg:g} degrees to the rear."])
        rows.append(["Room below the plate", f"Less the box of the bolt: x -{L.housing_w / 2 + 0.5:g} to +{L.housing_w / 2 + 0.5:g}, {yl(L.housing_y[0])} to {yl(L.housing_y[1] + 0.5)}, z 48.3 to the rest face. "
                     "A rib that crosses it (the front rib of the arcade panel, the seam of the blank panel) stops at it."])
        x, ylh, dia = L.finger_hole
        rows.append(["Grip", f"A panel with nothing to hold has a finger hole of {dia:g} through the plate at x {x:g}, yl {ylh:g}, with the edge break on both rims. It is not a part of the interface: a panel with a lever or keys lifts by them."])
    if cd.c == "Q":
        rows.append(["Cam holes (2)", f"At x -{L.cam_x:g} and +{L.cam_x:g}, {yl(L.cam_y)}: a hole of {L.cam_hole_d:g} through the plate and a boss of {L.cam_plate_boss[0]:g} x {L.cam_plate_boss[1]:g} under it, "
                     f"with a counterbore of {L.cam_head_d + 0.6:g} x {L.cam_head_h + 0.2:g} and a cone of 45 degrees under it for the head. Each panel carries 2 printed cams (stud and tongue), 2 steel pins {L.cam_pin_d:g} x 14 and 2 O-rings."])
        rows.append(["Room below the plate", f"A circle of {2 * (L.cam_tongue[1] + 1):g} round each cam hole, from z {bar_z(d, cd.i)[0] - L.cam_tongue_clear - L.cam_tongue[2] - 0.5:.1f} up, is the sweep of its tongue."])
    return rows


# ---------- the pictures ----------

def scenes(out: Path, cd: Candidate, deck: Part.Shape, hw: pf.Hardware) -> None:
    """The model directories of the sheets of one candidate (tools/draw_panel_latch.py renders them)."""
    d, i, L = cd.d, cd.i, cd.L
    zt = d.panel_top
    mid = (0.0, pf.y0(d) + d.panel_d / 2, zt)
    hard = pf.groups(hw)
    deck_outer = so.deck(d)[0]
    if cd.c == "B":
        deck_outer = deck_outer.cut(button_hole(L))
        deck = deck.cut(button_hole(L))
    floor = deck_outer.common(pf.box(-so.BIG, so.BIG, -so.BIG, so.BIG, 0.0, fit.Layout().floor_t))
    base = {"deck": (deck, FINISH["deck"]), "floor": (floor, FINISH["floor"])}
    outer = {"deck": deck_outer}
    fin = lambda k: FINISH["hook"] if k.startswith("panel") else FINISH["cover"] if k == "latch_gate" \
        else FINISH["slider"] if k == "latch_bolt" else FINISH["cam"] if k.startswith("cam_stud") else FINISH["tongue"] if k.startswith("cam_tongue") else pf.finish_of(k)
    frame = {k: (s, fin(k)) for k, s in {**cd.frame, **cd.fixed}.items()}
    on_panel_hw = {k: hard[k] for k in ("Lever", "Buttons", "Encoder")}
    mags = magnets(cd)

    def panel_at(st: Step) -> dict:
        shapes = {**{k: (s, pf.FINISH["tile"]) for k, s in cd.arcade.items()}, **on_panel_hw, "plate_magnets": mags["plate"]}
        if cd.c == "Q":
            for x, side in ((-L.cam_x, "left"), (L.cam_x, "right")):
                for k, s in cam(d, L, x, st.cam).items():
                    shapes[f"{k}_{side}"] = (s, fin(k))
        return {k: (placed(s, st, d, i), f) for k, (s, f) in shapes.items()}

    def cabinet_at(st: Step) -> dict:
        shapes = {**base, **frame, "frame_magnets": mags["frame"]}
        if cd.c == "B":
            shapes["latch_bolt"] = (bolt(d, L, st.bolt), FINISH["slider"])
            for k, s in springs(L, st.bolt).items():
                shapes[k] = (s, FINISH["spring"])
        return shapes

    # 1. the top face as the player sees it, and the front face of the deck
    seated = way_out(cd.c, L)[0]
    eye = {"player": view(mid, 240, 0, 52), "front": view((0.0, 20.0, 50.0), 110, 0, 8, 0.55)}
    write(out / "top", {**cabinet_at(seated), **panel_at(seated)}, outer, eye)
    # 2. a section through the latch, locked and released
    sec_x, look = section_place(cd)
    for state, st in (("locked", seated), ("released", release_step(cd))):
        keep = pf.box(-so.BIG, sec_x, -so.BIG, so.BIG, -so.BIG, so.BIG)
        every = {**cabinet_at(st), **panel_at(st)}
        cut, lines = pf.cut_scene(every, keep, deck, V(1, 0, 0), sec_x)
        write(out / f"section-{state}", cut, None, {"section": look}, lines)
    # 3. the way out in four steps
    for k, st in enumerate(steps_for_sheet(cd)):
        write(out / f"way-{k + 1}", {**cabinet_at(st), **panel_at(st)}, outer, {"way": view((0.0, mid[1] - 10, zt + 25), 300, -40, 26, 0.7)})
    # 5. B: the blank panel with its finger hole
    if cd.c == "B":
        blank = {k: (s, pf.FINISH["blank"]) for k, s in cd.blank.items()}
        x, ylh, _ = L.finger_hole
        write(out / "blank", {**base, **blank}, outer, {"player": view(mid, 240, 0, 52), "hole": view((x, pf.y0(d) + ylh, zt), 45, -25, 40, 0.7)})
    # 4. the latch parts apart
    write(out / "parts", exploded(cd), None, {"parts": view(exploded_target(cd), exploded_radius(cd), -35, 30, 0.7)})


def write(folder: Path, shapes: dict, edges: dict | None, focus: dict, lines: dict | None = None) -> None:
    pf.write_model(folder, shapes, edges, focus, lines)


def view(target, radius: float, az: float, el: float, aspect: float = 0.62) -> dict:
    return pf.cam(target, radius, az, el, aspect)


def magnets(cd: Candidate) -> dict:
    d, i, L = cd.d, cd.i, cd.L
    zr = pf.z_rest(d)
    top = zr - i.pad_drop
    pts = [p for k, p in enumerate(pf.latch_points(d, i)) if k in L.magnet_points[cd.c]]
    plate = [pf.cyl(i.magnet_d, x, y, zr, zr + i.keeper_h) for x, y in pts]
    fr = [pf.cyl(i.magnet_d, x, y, top - i.magnet_clear - i.magnet_h, top - i.magnet_clear) for x, y in pts]
    return {"plate": (Part.makeCompound(plate), FINISH["magnet"]), "frame": (Part.makeCompound(fr), FINISH["magnet"])}


def section_place(cd: Candidate) -> tuple[float, dict]:
    """Where each sheet cuts through its latch, and the camera (from the right, the cut face toward it)."""
    d, L = cd.d, cd.L
    zr = pf.z_rest(d)
    if cd.c == "M":
        x, y = pf.latch_points(d, cd.i)[1]
        return x, view((x, y + 4, zr - 2), 34, 90, 0, 0.7)
    if cd.c == "H":
        return L.hook_x, view((L.hook_x, rear_bar_face(d, cd.i) - 4, zr - 4), 36, 90, 0, 0.7)
    if cd.c == "B":
        return 0.0, view((0.0, 42.0, 55.0), 52, 90, 0, 0.6)
    return L.cam_x, view((L.cam_x, L.cam_y - 6, zr - 4), 34, 90, 0, 0.7)


def release_step(cd: Candidate) -> Step:
    if cd.c == "M":
        return Step("lifted 5", lift=(0.0, 5.0))
    if cd.c == "H":
        return Step("front up 4", swing=4.0)
    if cd.c == "B":
        return Step("released", bolt=cd.L.stroke)
    return Step("released", cam=90.0)


def steps_for_sheet(cd: Candidate) -> list[Step]:
    L = cd.L
    if cd.c == "M":
        return [Step("seated"), Step("lifted 10", lift=(0, 10)), Step("lifted 40", lift=(0, 40)), Step("lifted 120", lift=(0, 120))]
    first = {"H": Step("seated"), "B": Step("button in", bolt=L.stroke, swing=4.0), "Q": Step("released", cam=90.0)}[cd.c]
    b, t = (L.stroke if cd.c == "B" else 0.0), (90.0 if cd.c == "Q" else 0.0)
    return [first, Step("front up 10", bolt=b, cam=t, swing=10.0), Step("front up 20", bolt=b, cam=t, swing=20.0),
            Step("out", bolt=b, cam=t, swing=20.0, lift=(-40.0, 110.0))]


def exploded(cd: Candidate) -> dict:
    """The latch parts apart, round the corner or the place where they work."""
    d, i, L = cd.d, cd.i, cd.L
    mags = magnets(cd)
    fr = {k: (s, pf.FINISH["frame"]) for k, s in cd.frame.items() if k.startswith("frame")}
    if cd.c == "M":
        x, y = pf.latch_points(d, i)[1]
        keep = pf.box(x - 40, x + 40, y - 40, y + 40, -so.BIG, so.BIG)
        tile = cd.arcade["panel_button_tile"].common(keep).translated(V(0, 0, 40))
        return {"frame_corner": (fr["frame_right"][0].common(keep), pf.FINISH["frame"]),
                "magnets_frame": (mags["frame"][0].common(keep).translated(V(0, 0, 12)), FINISH["magnet"]),
                "magnets_plate": (mags["plate"][0].common(keep).translated(V(0, 0, 28)), FINISH["magnet"]),
                "tile_corner": (tile, FINISH["hook"])}
    yr = rear_bar_face(d, i)
    out = {}
    if cd.c == "Q":
        # one cam with the piece of the front bar that its tongue turns under
        x = L.cam_x
        parts = cam(d, L, x)
        keep = pf.box(x - 22, x + 22, 20, 60, -so.BIG, so.BIG)
        return {"frame_front": (fr["frame_right"][0].common(keep), pf.FINISH["frame"]),
                "cam_tongue": (parts["cam_tongue"].translated(V(0, 0, -14)), FINISH["tongue"]),
                "cam_pin": (cam_pin(L, x, bar_z(d, i)[0] - L.cam_tongue_clear - L.cam_tongue[2]).translated(V(14, 0, -14)), FINISH["spring"]),
                "cam_stud": (parts["cam_stud"].translated(V(0, 0, 24)), FINISH["cam"])}
    if cd.c == "H":
        x = L.hook_x
        keep = pf.box(x - 30, x + 30, yr - 30, yr + 20, -so.BIG, so.BIG)
        out["frame_rear"] = (fr["frame_right"][0].common(keep), pf.FINISH["frame"])
        out["hook"] = (hook(d, i, x, L).translated(V(0, -14, 26)), FINISH["hook"])
        return out
    # B: the tunnel (a piece of the left half of the frame), the bolt, the gate, the spring, the strike
    keep = pf.box(-L.housing_w / 2 - 6, L.housing_w / 2 + 6, L.housing_y[0] - 2, L.housing_y[1] + 2, -so.BIG, so.BIG)
    out["frame_tunnel"] = (cd.frame["frame_left"].common(keep), pf.FINISH["frame"])
    out["latch_bolt"] = (bolt(d, L).translated(V(0, 0, 16)), FINISH["slider"])
    out["latch_gate"] = (gate(L).translated(V(0, 18, 30)), FINISH["cover"])
    out["bolt_spring"] = (springs(L)["bolt_spring"].translated(V(0, 8, 22)), FINISH["spring"])
    out["strike"] = (strike(d, i, L).translated(V(0, 0, 40)), FINISH["hook"])
    return out


def exploded_target(cd: Candidate) -> tuple:
    d, L = cd.d, cd.L
    if cd.c == "M":
        x, y = pf.latch_points(d, cd.i)[1]
        return (x, y, 70.0)
    if cd.c == "B":
        return (0.0, 45.0, 70.0)
    if cd.c == "Q":
        return (L.cam_x, L.cam_y - 6, 62.0)
    return (L.hook_x, rear_bar_face(d, cd.i) - 8, 70.0)


def exploded_radius(cd: Candidate) -> float:
    return {"M": 50.0, "H": 45.0, "B": 75.0, "Q": 48.0}[cd.c]


def compare_scene(out: Path, cands: dict[str, Candidate], deck: Part.Shape, hw: pf.Hardware) -> None:
    """One model of each candidate with the panel in, from the same camera, for the side-by-side sheet."""
    for c, cd in cands.items():
        d = cd.d
        zt = d.panel_top
        hard = pf.groups(hw)
        deck_c = deck.cut(button_hole(cd.L)) if c == "B" else deck
        deck_outer = so.deck(d)[0]
        if c == "B":
            deck_outer = deck_outer.cut(button_hole(cd.L))
        shapes = {"deck": (deck_c, FINISH["deck"]), **{k: (s, pf.FINISH["tile"]) for k, s in cd.arcade.items()},
                  **{k: hard[k] for k in ("Lever", "Buttons")}}
        for k, s in cd.on_panel.items():
            shapes[k] = (s, FINISH["cam"] if "stud" in k else FINISH["tongue"])
        if c == "B":
            shapes["latch_bolt"] = (bolt(d, cd.L), FINISH["slider"])
        write(out / f"compare-{c}", shapes, {"deck": deck_outer},
              {"player": view((0.0, pf.y0(d) + d.panel_d / 2 - 20, zt), 250, -24, 40, 0.62)})


# ---------- the files ----------

def markdown(reps: dict[str, dict]) -> str:
    lines = ["# Control panel latch study: checks", ""]
    for c, r in reps.items():
        lines += [f"## {c}. {r['name']}", "", f"Result: **{'FAIL' if r['failures'] else 'PASS'}**.", ""]
        lines += [f"- {f}" for f in r["failures"]]
        m = r["magnet"]
        lines += ["", f"Magnet pair (ESTIMATED): frame 12 x {m['frame'][1]:g}, plate 12 x {m['plate'][1]:g}: case 1 of the frame magnet {m['case1_frame_N']} N; "
                  f"the pair at contact {m['pair_contact_N']} N; gap {m['gap_mm']} (x {m['gap_factor']}); use x {m['use_factor']}: **{m['pull_N']} N**.", "",
                  "| Load case | Factor | Way out that governs | Restraint that governs |", "| --- | --- | --- | --- |"]
        lines += [f"| {h['case']} | {h['factor']} | {h['mechanism']} | {h['governs']} |" for h in r["hold"]["rows"]]
        lines += ["", f"Normal play, preload only (no click): factor {r['play']['factor']}.", "", f"Removal: {r['removal']['how']}", ""]
        if r["preload"]:
            lines += [f"Bolt: {json.dumps(r['preload'])}", ""]
        lines += ["| Step of the way out | Common volume, mm3 | Result |", "| --- | --- | --- |"]
        lines += [f"| {x['step']} | {x['common_mm3']} | {x['result']} |" for x in r["motion"]]
        lines += ["", "| Lock | Common volume, mm3 | Result |", "| --- | --- | --- |"] + [f"| {x['what']} | {x['common_mm3']} | {x['result']} |" for x in r["locks"]]
        bad = [x for x in r["clashes"] + r["clashes_blank"] + r["room"] if x["result"] != "PASS"]
        lines += ["", f"Clashes and room: {len(r['clashes']) + len(r['clashes_blank'])} pairs and {len(r['room'])} rows, {len(bad)} fail. Room {r['room_volume_cm3']} cm3.", "",
                  "| Part | On the printer | Box | Fits | Overhang, cm2 | Mass, g |", "| --- | --- | --- | --- | --- | --- |"]
        lines += [f"| {p['part']} | {p['how']} | {p['x']} x {p['y']} x {p['z']} | {'yes' if p['fits'] else 'NO'} | {p['overhang_cm2']} | {p['mass_g']} |" for p in r["print"]]
        lines += [""]
    return "\n".join(lines) + "\n"


def main() -> int:
    out = Path(os.environ.get("CANDYBAR_OUT", OUT))
    out.mkdir(parents=True, exist_ok=True)
    which = tuple(c for c in os.environ.get("CANDYBAR_LATCH", ",".join(CANDIDATES)).split(",") if c)
    pictures = os.environ.get("CANDYBAR_LATCH_SCENES", "1") != "0"
    start = time.time()
    log = lambda text: print(f"[{time.time() - start:6.1f} s] {text}", flush=True)
    v = pf.values()
    d = Blueprint()
    deck = pf.deck_skin(d, log)
    hw = pf.hardware(d, deck)
    reps, cands = {}, {}
    for c in which:
        cd = build(c, d, v=v)
        cands[c] = cd
        log(f"{c}: built")
        rep = check(cd, deck, hw, v, log)
        reps[c] = rep
        (out / c).mkdir(parents=True, exist_ok=True)
        (out / c / "report.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
        pf.write_model(out / c / "parts", {k: (s, pf.finish_of(k)) for k, s in cd.printed.items()})
        if pictures:
            scenes(out / c / "scenes", cd, deck, hw)
            log(f"{c}: scenes written")
    if pictures and len(cands) == len(CANDIDATES):
        compare_scene(out / "scenes", cands, deck, hw)
    summary = {c: {"name": r["name"], "failures": r["failures"], "factor": r["hold"]["factor"], "play": r["play"]["factor"],
                   "removal": r["removal"], "shows": r["shows"], "buy": r["buy"], "interface_rows": r["interface_rows"],
                   "strain": r["strain"], "wear": r["wear"], "magnet": r["magnet"], "strength": r["strength"], "preload": r["preload"],
                   "hold": r["hold"]["rows"], "print": r["print"], "corner_rock": r["corner_rock"], "ramp_option": r["ramp_option"],
                   "interface_rows_all": r["interface_rows"]} for c, r in reps.items()}
    summary["detent"] = detent()
    # a run of some candidates keeps the others of an earlier run (the record of the study)
    old = out / "summary.json"
    if old.exists():
        summary = {**json.loads(old.read_text(encoding="utf-8")), **summary}
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=str), encoding="utf-8")
    for c, r in reps.items():
        (out / c / "report.md").write_text(markdown({c: r}), encoding="utf-8")
    if len(reps) == len(CANDIDATES):
        (out / "report.md").write_text(markdown(reps), encoding="utf-8")
    print(markdown(reps))
    log("done")
    return 1 if any(r["failures"] for r in reps.values()) else 0
