"""The named dimensions of shell variant D, and the screen-face options.

Lengths are millimetres, angles degrees. Frame: X to the player's right, Y from the deck front edge toward
the rear, Z up from the desk. The names follow CONTEXT.md; they will move into the parameter sheets later.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

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
    deck_corner: float = 32.0
    deck_corner_r: float = 10.0
    deck_top_r: float = 12.0
    deck_lean: float = 10.0
    deck_lean_h: float = 27.0
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
    step_y0: float = 380.0
    step_lean: float = 28.0
    rear_facet: float = 14.0
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
    hood_rear_r: float = 20.0
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
    # rear
    door_w: float = 368.0
    door_z0: float = 112.0
    door_z1: float = 300.0
    fan_d: float = 118.0
    pocket_w: float = 100.0
    pocket_h: float = 42.0
    pocket_z0: float = 0.0
    wall_spare: float = 12.0
    psu_side: float = 14.0
    controls_forward: float = 15.0

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
class HoodStations:
    """Derived stations of the hood in its own frame: x across, y back from the cap's front plane, z up from its base."""
    origin: tuple[float, float, float]
    height: float
    depth: float
    half_base: float
    z_sill: float
    z_band_top: float
    z_rail_top: float
    z_open_top: float
    y_band_foot: float
    y_band_top: float
    y_marquee_bottom: float
    y_marquee_top: float
    y_wall: float
    corner_centre: tuple[float, float]

    def y_band(self, z: float, tilt: float) -> float:
        return self.y_band_foot + (z - self.z_sill) * math.tan(math.radians(tilt))

    def y_marquee(self, z: float, tilt: float) -> float:
        return self.y_marquee_bottom - (z - self.z_rail_top) * math.tan(math.radians(tilt))


def hood_stations(d: Dims) -> HoodStations:
    """Where the parts of the hood stand: levels up the arch, depths behind its front plane, the corner centre."""
    height = d.hood_h - d.seam_gap
    origin = (0.0, d.seam_y + d.hood_shoulder_front, d.body_top + d.seam_gap)
    depth = d.body_d - d.hood_shoulder_front - origin[1]
    half_base = d.width / 2 - d.hood_shoulder
    z_open_top = height - d.hood_bar
    tm, tb = math.radians(d.marquee_tilt), math.radians(d.hood_band_tilt)
    z_rail_top = z_open_top - (d.marquee_margin + d.marquee_h + d.marquee_head) * math.cos(tm)
    z_band_top = z_rail_top - d.hood_rail_h
    y_band_top = d.hood_ledge + (z_band_top - d.hood_sill_h) * math.tan(tb)
    y_marquee_bottom = y_band_top + d.hood_band_t / math.cos(tb) - d.marquee_cover_t / math.cos(tm)
    y_marquee_top = y_marquee_bottom - (z_open_top - z_rail_top) * math.tan(tm)
    a = math.radians(d.hood_side_lean)
    zc = height - d.hood_corner_r
    xc = half_base - zc * math.tan(a) - d.hood_corner_r / math.cos(a)
    return HoodStations(origin, height, depth, half_base, d.hood_sill_h, z_band_top, z_rail_top, z_open_top, d.hood_ledge,
                        y_band_top, y_marquee_bottom, y_marquee_top, depth - d.hood_wall, (xc, zc))


OPTIONS: dict[str, dict[str, float]] = {
    "1-tall-bezel": {"recline": 24.0, "band_len": 0.0, "frame_side": 42.0, "frame_v": -1.0},
    "2-tall-band": {"recline": 26.0, "band_len": 100.0, "frame_side": 45.0, "frame_v": 45.0},
    "3-short-band": {"recline": 30.0, "band_len": 60.0, "frame_side": 45.0, "frame_v": 45.0},
    "4-on-deck": {"recline": 36.0, "band_len": 0.0, "frame_side": 40.0, "frame_v": 40.0},
}
EYE = (-60.0, 530.0)
EYE_LOW = (-60.0, 450.0)


def sight(d: Dims, eye: tuple[float, float] = EYE) -> tuple[float, float]:
    """Sight angle below horizontal and eye distance to the centre of the lit image."""
    y, z = d.face(d.image_s)
    su, cu = d.u
    y, z = y + d.mon_setback * cu, z - d.mon_setback * su
    dy, dz = y - eye[0], eye[1] - z
    return math.degrees(math.atan2(dz, dy)), math.hypot(dy, dz)


def frame_for_sight(d: Dims, target: float = 25.0) -> float:
    """The frame height above and below the image that puts the sight angle on target (bisection)."""
    lo, hi = 0.0, 400.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if sight(replace(d, frame_v=mid))[0] > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def option(name: str, base: Dims | None = None) -> Dims:
    d = replace(base or Dims(), **{k: v for k, v in OPTIONS[name].items() if v >= 0})
    if OPTIONS[name]["frame_v"] < 0:
        d = replace(d, frame_v=round(frame_for_sight(d), 1))
    return d
