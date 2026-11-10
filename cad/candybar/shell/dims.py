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
    deck_nose: float = 20.0
    deck_tail: float = 10.0
    deck_top: float = 72.0
    deck_under_body: float = 50.0
    deck_corner: float = 58.0
    deck_facet_in: float = 13.0
    deck_facet_drop: float = 11.0
    deck_crease_z: float = 30.0
    deck_crease_in: float = 15.0
    # screen face
    recline: float = 24.0
    band_len: float = 0.0
    frame_side: float = 42.0
    frame_v: float = 195.0
    bezel_t: float = 14.0
    bezel_step: float = 5.0
    bezel_step_w: float = 12.0
    bezel_corner_r: float = 10.0
    reveal: float = 3.0
    brow_ledge: float = 16.0
    mon_setback: float = 4.0
    # cheeks and body
    cheek_t: float = 40.0
    cheek_proj: float = 34.0
    cheek_bulge: float = 12.0
    cheek_reach: float = 72.0
    cheek_sweep_s: float = 70.0
    cheek_facet: float = 22.0
    body_d: float = 540.0
    rear_w: float = 430.0
    step_y0: float = 330.0
    step_lean: float = 28.0
    rear_facet: float = 14.0
    # hood
    hood_h_ratio: float = 0.28
    hood_lean_front: float = 6.0
    hood_lean_rear: float = 16.0
    hood_side_in: float = 52.0
    hood_corner_r: float = 46.0
    hood_nose_r: float = 40.0
    hood_bar_side: float = 34.0
    hood_bar_top: float = 46.0
    hood_overhang: float = 24.0
    band_setback: float = 44.0
    band_tilt: float = 26.0
    band_t: float = 8.0
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
    controls_forward: float = 10.0

    # derived
    @property
    def bezel_w(self) -> float:
        return MON_ACTIVE_W + 2 * self.frame_side

    @property
    def bezel_len(self) -> float:
        return MON_ACTIVE_H + 2 * self.frame_v

    @property
    def width(self) -> float:
        return self.bezel_w + 2 * (self.cheek_t + self.panel_gap)

    @property
    def foot_y(self) -> float:
        return self.deck_nose + self.panel_gap * 2 + self.panel_d + self.deck_tail

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
        return self.band_len + (self.reveal if self.band_len else 0.0)

    @property
    def bezel_s1(self) -> float:
        return self.bezel_s0 + self.bezel_len

    @property
    def image_s(self) -> float:
        return (self.bezel_s0 + self.bezel_s1) / 2

    @property
    def top_s(self) -> float:
        return self.bezel_s1 + self.reveal

    @property
    def body_top(self) -> float:
        return self.face(self.top_s)[1] + self.brow_ledge

    @property
    def hood_h(self) -> float:
        return self.hood_h_ratio * self.width


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
