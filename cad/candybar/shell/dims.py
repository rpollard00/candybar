"""The named dimensions of the outer form: Dims, and Blueprint, the target of the blueprint; and the seated players.

Lengths are millimetres, angles degrees. Frame: X to the player's right, Y from the deck front edge toward
the rear, Z up from the desk. The names follow CONTEXT.md; they will move into the parameter sheets later.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

MON_ACTIVE_W = 344.678
MON_ACTIVE_H = 215.424


@dataclass(frozen=True)
class Dims:
    # control panel and deck
    panel_w: float = 396.0
    panel_d: float = 175.0
    panel_gap: float = 1.0
    panel_top: float = 70.0
    panel_t: float = 5.0
    deck_nose: float = 25.0
    deck_tail: float = 5.0
    deck_top: float = 72.0
    deck_under_body: float = 50.0
    deck_centre_frac: float = 0.56
    deck_flank: float = 8.0
    deck_corner_frac: float = 0.09
    deck_crease_r: float = 6.0
    deck_top_r: float = 10.5
    deck_lean: float = 10.0
    deck_lean_h: float = 24.0
    # screen face
    recline: float = 30.0
    band_len: float = 60.0
    frame_side: float = 45.0
    frame_v: float = 45.0
    bezel_t: float = 20.0
    bezel_step: float = 8.0
    bezel_step_w: float = 10.0
    bezel_corner_r: float = 10.0
    reveal: float = 3.0
    brow_ledge: float = 12.0
    mon_setback: float = 18.0
    # the rail: one band (radius, bevel, land) round the deck and up the cabinet
    land: float = 12.0
    band_in: float = 17.0
    band_drop: float = 29.5
    band_r: float = 12.0
    bottom_r: float = 4.0
    bend_r: float = 50.0
    body_d: float = 540.0
    rear_w: float = 430.0
    band_lean: float = 28.0
    # hood: the cap (an arch of a top bar, two legs and a sill, standing on the body top)
    hood_h_ratio: float = 0.32
    seam_gap: float = 1.5
    hood_shoulder: float = 8.0
    hood_shoulder_front: float = 4.0
    hood_side_lean: float = 10.0
    hood_corner_r: float = 70.0
    hood_bar: float = 21.0
    hood_edge_in: float = 16.0
    hood_edge_back: float = 32.0
    hood_rim_r: float = 4.0
    hood_wall: float = 4.0
    hood_sill_h: float = 17.0
    hood_sill_corner_r: float = 8.0
    hood_ledge: float = 12.0
    hood_rail_h: float = 6.0
    hood_rail_proud: float = 5.0
    # hood: what stands in the arch (the marquee under the top bar, the hood band below it)
    marquee_h: float = 34.0
    marquee_margin: float = 1.0
    marquee_head: float = 3.0
    marquee_tilt: float = 18.0
    marquee_cover_t: float = 3.0
    marquee_module: float = 32.0
    hood_band_tilt: float = 16.0
    hood_band_t: float = 4.0
    hood_trim_gap: float = 1.0
    speaker_proud: float = 13.0
    speaker_side_gap: float = 8.0
    speaker_foot_gap: float = 4.0
    speaker_head_gap: float = 6.0
    speaker_corner_r: float = 8.0
    speaker_edge_r: float = 4.0
    grille_inset: float = 6.0
    grille_recess: float = 1.5
    logo_w: float = 176.0
    logo_gap: float = 18.0
    logo_proud: float = 5.0
    logo_end_gap: float = 4.0
    logo_inset: float = 5.0

    # derived
    @property
    def bezel_w(self) -> float:
        return MON_ACTIVE_W + 2 * self.frame_side

    @property
    def bezel_len(self) -> float:
        return MON_ACTIVE_H + 2 * self.frame_v

    @property
    def width(self) -> float:
        return self.bezel_w + 2 * (self.rail_t + self.panel_gap)

    @property
    def rail_t(self) -> float:
        """Horizontal thickness of the rail seen from the front: bevel plus land."""
        return self.band_in + self.land

    @property
    def bend_t(self) -> float:
        """Tangent length of the concave bend between the deck top and the screen face."""
        return self.bend_r * math.tan(math.radians(90.0 - self.recline) / 2)

    @property
    def foot_y(self) -> float:
        return self.deck_nose + self.panel_gap * 2 + self.panel_d + self.deck_tail + self.bend_t

    @property
    def deck_end(self) -> float:
        return self.foot_y + self.deck_under_body

    @property
    def u(self) -> tuple[float, float]:
        a = math.radians(self.recline)
        return math.sin(a), math.cos(a)

    def face(self, s: float) -> tuple[float, float]:
        """Point (y, z) on the screen face (the bezel front plane), s along the slope from its foot."""
        su, cu = self.u
        return self.foot_y + s * su, self.deck_top + s * cu

    @property
    def bezel_s0(self) -> float:
        return self.bend_t + self.band_len

    @property
    def bezel_s1(self) -> float:
        return self.bezel_s0 + self.bezel_len

    @property
    def image_s(self) -> float:
        return (self.bezel_s0 + self.bezel_s1) / 2

    @property
    def top_s(self) -> float:
        return self.bezel_s1 + self.brow_ledge

    @property
    def body_top(self) -> float:
        return self.face(self.top_s)[1]

    @property
    def hood_h(self) -> float:
        """Height of the hood top above the body top (the seam gap included)."""
        return self.hood_h_ratio * self.width

    @property
    def seam_y(self) -> float:
        """Y of the front edge of the body top, where the rail lands end."""
        return self.face(self.top_s)[0]


@dataclass(frozen=True)
class Blueprint(Dims):
    """The target of the blueprint (docs/blueprint): the dimensions that differ from the built model, and new ones.

    The deck and the bezel window keep the values of Dims; the flat screen stands nearer the bezel, and the control
    panel's front follows the deck's front contour (profiles.panel_outline). The blueprint
    changes the rail (one edge section from the hood seam to the front of the deck), the rear (planar, revision 7:
    decision record 0007) and the hood (deeper, near-straight sides with tight top corners). It also holds the curves
    of the form as named values: the arc of the rail in side view, the tuck of the body sides toward the hood in
    front view, the side and top corner of the hood, and the lines that the references draw straight (crown, bow),
    which are zero. profiles.py turns these into profiles and faces.
    """
    # the rear, revision 7: planar. The lower body is rear_w wide behind the band; the head (the body above the rear
    # shelf) and the hood have the full width back to the rear, and stand rear_proud behind the lower rear wall
    rear_w: float = 470.7
    rear_proud: float = 40.0
    # the rear shelf under the head: two flat facets of 45 degrees that meet on the hip. Its inner crease is level at
    # rear_shelf_z0, on the lower rear wall and on the side of the lower body; the rear facet ends on the upper rear
    # wall at rear_shelf_z1 (rear_proud higher), the side facet on the side band band_depth higher (band_top_z)
    rear_shelf_z0: float = 293.0
    rear_shelf_z1: float = 333.0
    # the band: the facet of 45 degrees, band_depth deep, on the rear edge of the side band. Its outer edge in side view
    # (the stroke) is four straight lines: an upright stub of band_stub at the desk (at band_foot_y), a kick that
    # leans band_kick to the rear of upright on its way down, the lean (band_lean, as on the reference), and the level
    # run that is the side facet of the rear shelf. The line of the lean passes the desk band_flare in front of the
    # stub (at band_lean_y0, where the form has no edge), and it would reach the body top at band_seam_y
    band_seam_y: float = 530.0
    band_stub: float = 20.0
    band_flare: float = 80.0
    band_kick: float = 28.0
    # the edge finish. No outside edge stays fully sharp, and the form is not rounded off: a convex edge of the rear
    # design that turns edge_min_turn or more has a round of rear_round_r (the band's outer edge, the hip, the
    # edges of the head, the rear corners of the head and of the hood; the lower rear corner is the ellipse that this
    # round makes in plan); every other convex edge that turns more than edge_break_turn gets a break of edge_break
    # as the last modelling step. Concave creases and blunt mitres stay sharp
    rear_round_r: float = 3.0
    edge_min_turn: float = 40.0
    edge_break: float = 1.0
    edge_break_turn: float = 45.5
    # the facet round the foot of the cabinet (deck front and sides, the band's foot, the lower body)
    base_facet: float = 5.0
    # the crease between the centre face and each flank of the deck front (it turns deck_flank, 8 degrees) is sharp: a
    # blunt mitre. The round of 6 that Dims has there is an arc 0.84 long, which stands 0.015 off the sharp crease and
    # makes faces under 1 mm wide down the front of the deck
    deck_crease_r: float = 0.0
    # the opening of the rear door in the lower rear wall. The form sets its sides and its top: a land of door_land
    # between each side and the ends of the cut-ins, a frame of door_frame between its top and the crease of the rear
    # shelf (door_w, door_z1). Its sill is door_z0; the fit study checks that the compute module, which stands on
    # the power supply's fan space, lies inside the opening with its lower edge above the sill
    door_land: float = 4.0
    door_frame: float = 12.0
    door_z0: float = 116.0
    # the cut-ins at each lower rear corner: cut_in_count level grooves that turn the corner, the lowest lip at
    # cut_in_z0, cut_in_pitch apart. A ball mills each groove along the true offset of the plan outline, so that the
    # slot is cut_in_h high and cut_in_depth deep all the way; it runs cut_in_side along the side and cut_in_rear
    # along the rear, to round ends
    cut_in_count: int = 4
    cut_in_z0: float = 126.0
    cut_in_pitch: float = 22.0
    cut_in_h: float = 10.0
    cut_in_depth: float = 1.5
    cut_in_side: float = 30.0
    cut_in_rear: float = 20.0
    # the hand-holds: two recesses in the rear wall of the head, from grip_x0 to grip_x1 each side of the centre
    # line, grip_h high from grip_z0, grip_depth deep, with ends of grip_end_r in plan. The roof falls 45 degrees
    # toward the inside (a hook for the fingers that prints without support). The edges inside are rounds of grip_r,
    # those of the roof grip_roof_r; the rim has the edge break
    grip_x0: float = 70.0
    grip_x1: float = 170.0
    grip_z0: float = 349.05
    grip_h: float = 62.0
    grip_depth: float = 26.0
    grip_end_r: float = 10.0
    grip_r: float = 8.0
    grip_roof_r: float = 3.0
    # curves of the body
    rail_sagitta_ratio: float = 0.035
    body_tuck_ratio: float = 0.023
    body_tuck_from: float = 0.667
    body_bow_ratio: float = 0.0
    bezel_land: float = 20.0
    bezel_rim: float = 2.0
    # the bezel land lies this far below the rail land; the reveal round the plate (panel_gap wide) has the same depth
    bezel_drop: float = 2.0
    # the bezel, the window and the screen stand lower on the face than in Dims, so that the strip of face above the
    # bezel (brow_ledge) holds the seam bevel with plain face below it, and the top corners of the bezel stand clear
    # of the tuck; the band below the bezel gives the length up. Their sum keeps the body top where it was.
    band_len: float = 40.0
    brow_ledge: float = 32.0
    # the flat screen stands mon_setback behind the chord of the rail arc
    mon_setback: float = 7.2
    # the lit image as a thin plate on the screen face, for the renders of the solids
    screen_t: float = 1.0
    # hood cap: its foot has the outline of the body top, with a groove at the seam: no shoulder at the sides or the
    # rear (its rear wall is flush with the upper rear); at the front its foot lies on the line of the rail
    hood_shoulder: float = 0.0
    hood_shoulder_front: float = 0.0
    hood_shoulder_rear: float = 0.0
    seam_groove: float = 3.0
    hood_crown_ratio: float = 0.0
    # hood in side view: the front leans back, more over its lower part, with a blend between; a flat top below the
    # top of the rear arc, which it cuts, with a radius in the crease; a soft edge of one radius round the front
    hood_flat_h: float = 148.0
    hood_front_lean_low: float = 16.0
    hood_front_low_share: float = 0.29
    hood_front_lean_up: float = 2.0
    hood_front_blend_r: float = 40.0
    hood_top_rear_r: float = 10.0
    hood_edge_in: float = 14.0
    hood_edge_back: float = 14.0
    # hood side: tangent to the tuck at the seam, it turns hood_side_turn degrees on its way up to a top corner of one radius
    hood_side_turn: float = 2.0
    hood_corner_ratio: float = 0.07
    hood_rear_arc_d: float = 95.0
    hood_rear_arc_h: float = 110.0
    hood_sill_corner_r: float = 6.0
    # hood band: upright, so that the speakers fire straight forward; its face stands hood_band_recess behind the
    # hood front at the top of the band, and the ledge on the sill is what is left between them
    hood_band_tilt: float = 0.0
    hood_band_recess: float = 5.0
    # marquee: upright, so that it faces directly forward; it stands hood_marquee_edge behind the front of the lip,
    # which leaves a small edge on top of the lip; between the lip and the top bar the opening is hood_marquee_open_h
    marquee_tilt: float = 0.0
    hood_marquee_edge: float = 5.0
    hood_marquee_open_h: float = 36.1
    # the printed skin: the inner surface of the deck, the body and the hood stands at least wall_t inside the outer one
    wall_t: float = 4.0

    @property
    def edge_in(self) -> float:
        """How far the edge section runs in from the side plane: the radius, then the leaning band."""
        t = math.radians(90.0 - self.deck_lean)
        return self.deck_top_r * math.sin(t) + (self.deck_lean_h - self.deck_top_r * (1 - math.cos(t))) * math.tan(math.radians(self.deck_lean))

    @property
    def rail_land(self) -> float:
        """Width of the land beside the bezel below the tuck: what the edge section leaves of the rail."""
        return self.rail_t - self.edge_in

    @property
    def depth(self) -> float:
        return self.body_d + self.rear_proud

    @property
    def band_depth(self) -> float:
        """How far the side of the lower body stands in from the side band: the depth of the band."""
        return self.width / 2 - self.rear_w / 2

    @property
    def band_lean_y0(self) -> float:
        """Y of the line of the band's lean at the desk. The lean ends at the knee, so the form has no edge here: the
        band's outer edge at the desk is band_foot_y."""
        return self.band_seam_y - self.body_top * math.tan(math.radians(self.band_lean))

    @property
    def band_foot_y(self) -> float:
        """Y of the band's outer edge at the desk: the upright stub. Behind it (and band_depth farther in) the lower
        body is rear_w wide."""
        return self.band_lean_y0 + self.band_flare

    @property
    def cut_in_z1(self) -> float:
        """Height of the upper lip of the highest cut-in."""
        return self.cut_in_z0 + (self.cut_in_count - 1) * self.cut_in_pitch + self.cut_in_h

    @property
    def cut_in_x(self) -> float:
        """Half the width of the lower rear wall that the cut-ins leave plain: their slots end here."""
        return self.rear_w / 2 - self.cut_in_rear

    @property
    def rear_flat_x(self) -> float:
        """Half the width of the lower rear wall that is flat: the upright corner (the ellipse that the round of the
        hip makes in plan) starts here."""
        return self.rear_w / 2 - self.rear_round_r / math.sqrt(2)

    @property
    def cut_in_y(self) -> float:
        """Y where the slots of the cut-ins end on the side of the lower body."""
        return self.body_d - self.cut_in_side

    @property
    def door_w(self) -> float:
        """Width of the rear door opening: door_land inside the ends of the cut-ins on each side."""
        return 2 * (self.cut_in_x - self.door_land)

    @property
    def door_z1(self) -> float:
        """Top of the rear door opening: door_frame below the crease of the rear shelf."""
        return self.rear_shelf_z0 - self.door_frame

    @property
    def grip_z1(self) -> float:
        """Top of the opening of each hand-hold in the rear wall of the head."""
        return self.grip_z0 + self.grip_h

    def band_lean_y(self, z: float) -> float:
        """Y of the line of the band's lean at height z (it leans back)."""
        return self.band_lean_y0 + z * math.tan(math.radians(self.band_lean))

    def rear_y(self, z: float) -> float:
        """Y of the rear at height z on the centre line: the lower rear wall, the rear facet of the shelf, the upper
        rear wall."""
        if z <= self.rear_shelf_z0:
            return self.body_d
        return min(self.depth, self.body_d + (z - self.rear_shelf_z0) * (self.depth - self.body_d) / (self.rear_shelf_z1 - self.rear_shelf_z0))

    @property
    def band_top_z(self) -> float:
        """Height of the outer edge of the band's level run: the side facet of the rear shelf ends there on the side band."""
        return self.rear_shelf_z0 + self.band_depth

    @property
    def tuck(self) -> float:
        """How far each body side stands in from the side plane at the seam."""
        return self.body_tuck_ratio * self.width

    @property
    def tuck_z0(self) -> float:
        """Height at which the body side leaves the side plane."""
        return self.deck_top + self.body_tuck_from * (self.body_top - self.deck_top)

    @property
    def tuck_lean(self) -> float:
        """Lean of the body side at the seam, degrees from vertical: the tuck is one arc that starts vertical."""
        return math.degrees(2 * math.atan2(self.tuck, self.body_top - self.tuck_z0))

    @property
    def tuck_r(self) -> float:
        """Radius of the tuck arc. The hood side leaves the seam on its tangent, so the outline has no corner there."""
        lean = math.radians(self.tuck_lean)
        return (self.body_top - self.tuck_z0) / math.sin(lean) if lean > 1e-9 else math.inf

    def side_x(self, z: float) -> float:
        """Half the width of the body at height z: the side plane, a bow below the tuck when one is set, and the tuck.
        Above the body top the tuck arc runs on, for the solids that are cut there."""
        half = self.width / 2
        if self.body_bow_ratio:
            t = min(max((z - self.deck_top) / (self.tuck_z0 - self.deck_top), 0.0), 1.0)
            half += self.body_bow_ratio * self.width * 4 * t * (1 - t)
        if z <= self.tuck_z0 or self.tuck <= 0:
            return half
        dz = z - self.tuck_z0
        return half - (self.tuck_r - math.sqrt(self.tuck_r ** 2 - dz ** 2))

    @property
    def rail_turn(self) -> float:
        """Angle through which the rail arc turns, degrees, from its sagitta."""
        return math.degrees(4 * math.atan(2 * self.rail_sagitta_ratio))


@dataclass(frozen=True)
class Seated:
    """A player at the desk: the eye height above the seat, sitting upright, from published data."""
    name: str
    eye_above_seat: float
    source: str


# the desk and the chair: a desk of normal height (the middle of 730 to 760) and an office chair at the low end of
# 480 to 530 (controls-ergonomics.md 5.4 and 5.5); relaxed sitting lowers the eye by SLUMP (same section); the eyes
# are EYE_Y in front of the deck's front edge (as in the earlier form)
DESK_H = 745.0
CHAIR_H = 500.0
SLUMP = 30.0
EYE_Y = -60.0
PEOPLE = (Seated("child of 8", 578.0, "DINBelg 2005, boys of 8 years, mean sitting eye height (dinbelg.be)"),
          Seated("small adult", 698.0, "ANSUR II women, 5th percentile eye height above the seat (controls-ergonomics.md 5.2)"),
          Seated("tall adult", 860.0, "ANSUR II men, 95th percentile eye height above the seat (controls-ergonomics.md 5.2)"))


def eye_of(p: Seated) -> tuple[float, float]:
    """The eye of a seated player in (y, z) of the cabinet: z above the desk top."""
    return EYE_Y, CHAIR_H + p.eye_above_seat - SLUMP - DESK_H
