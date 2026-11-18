"""Width study: the accepted Blueprint made wider by a number of mm, for comparison only.

Blueprint() does not change. widened(extra) returns a copy in which the growth goes into the rails: the land
(Dims.land, so rail_t and the derived width) grows by extra / 2 on each side; the bezel, the window, the screen and
the monitor keep their size and stay centred. Depth and height stay: the lower body grows with the width so that the
band stays 12 deep, and hood_h_ratio is set so that the top of the hood's rear arc (hood_h) stays in mm. The deck's
front corner keeps its radius in mm (44.5), because the USB row in the deck's side starts where that corner ends and
must end before the joint of the deck and the body (fit.Layout.usb_front_gap). All other values keep their meaning:
the ratios of W (tuck, hood corner, deck centre face) scale with W, and the
values in mm (control panel, logo, speaker gaps, the band's stroke) stay; the door follows the lower rear wall. The speaker forms follow from the hood's
opening, so they grow. The marquee window is a whole number of light modules (module_window): 11 x 32 = 352 up to
about +43, where 12 (384) fit.

No FreeCAD here: cad/tools/draw_widths.py draws from it, and candybar/shell/width_run.py builds from it.
"""
from __future__ import annotations

import math
from dataclasses import replace

from . import profiles as pr
from .dims import Blueprint

# the ledge on which the bezel plate rests round the opening behind it (cavity.Openings.bezel_ledge)
BEZEL_LEDGE = 6.0
# the half width of the generic 16:10 monitor swept by its adjustment (mon_gen_w / 2 + mon_adjust), and what its
# plugs add beside each edge (mon_side_clear, mon_side_clear_straight): cad/params/hardware.csv
MON_SWEPT, MON_ADJUST, PLUG_RIGHT_ANGLE, PLUG_STRAIGHT = 188.0, 8.0, 22.0, 70.0

# name: (extra width in mm, extra width of each side bar of the bezel frame in mm, why it is studied)
OPTIONS: dict[str, tuple[float, float, str]] = {
    "+0": (0.0, 0.0, "the accepted model"),
    "+10": (10.0, 0.0, "about the widest at which half the width still fits the bed (256)"),
    "+20": (20.0, 0.0, "the rail land comes to about 0.05 W, as on the maker's mini"),
    "+20 split": (20.0, 5.0, "+5 to each rail land and +5 to each side bar: the opening behind the bezel grows"),
    # +38.5, not +38: at exactly +38 the boolean that cuts the front body (solids.body) fails in OCC; +37.5 and +38.5 build
    "+38.5": (38.5, 0.0, "the cavity takes straight monitor plugs (258 from the centre line)"),
    "+38.5 split": (38.5, 8.5, "each rail land 26.75 (0.05 W), the rest (8.5) into each side bar"),
}


def widened(extra: float, bar: float = 0.0, base: Blueprint | None = None) -> Blueprint:
    """The base made extra mm wider, with its depth and height kept. Each side bar of the bezel frame grows by bar
    (frame_side; the window, the screen and the frame at the top and the bottom stay); the rest goes into the rail
    lands."""
    b = base or Blueprint()
    if not extra and not bar:
        return b
    w = b.width + extra
    return replace(b, land=b.land + extra / 2 - bar, frame_side=b.frame_side + bar, rear_w=b.rear_w + extra, hood_h_ratio=b.hood_h / w,
                   deck_corner_frac=b.deck_corner_frac * b.width / w)


def option(name: str) -> Blueprint:
    extra, bar, _ = OPTIONS[name]
    return widened(extra, bar)


_widest_window = pr.marquee_window


def module_window(d: Blueprint, h: pr.Hood) -> tuple[float, float]:
    """The marquee window as a whole number of light modules: the most that the widest straight window holds.
    For the accepted model this is the same window (352 = 11 x 32)."""
    w, mh = _widest_window(d, h)
    return d.marquee_module * (w // d.marquee_module), mh


def use_module_window() -> None:
    """Make profiles.faces and the fit study use module_window (for the width variants only)."""
    pr.marquee_window = module_window


def numbers(d: Blueprint) -> dict[str, float]:
    """The 2D numbers of one width that the table reports (no cavity: that needs the solids)."""
    fr = pr.front(d)
    h = pr.hood(d)
    w = d.width
    z_top = fr.on_rail(d, d.bezel_s1)[1]
    z_mid = fr.on_rail(d, d.image_s)[1]
    height = h.origin[2] + h.height
    mq_max, _ = _widest_window(d, h)
    mq_w, _ = module_window(d, h)
    tb = math.radians(d.hood_band_tilt)
    length = (h.z_band_top - h.z_sill) / math.cos(tb)
    leg = lambda v: h.half_width(max(h.z_sill + v * math.cos(tb), h.z_sill + d.hood_sill_corner_r), h.opening) - d.speaker_side_gap
    xi = d.logo_w / 2 + d.logo_gap
    v0, v1 = d.speaker_foot_gap, length - d.speaker_head_gap
    panel = pr.panel_outline(d)
    hw = w / 2
    return {
        "W": w, "H": height, "D": d.depth, "H/W": height / w, "D/W": d.depth / w,
        "hood_h": height - d.body_top, "hood_h/W": (height - d.body_top) / w, "hood_d": h.depth, "hood_d/W": h.depth / w,
        "hood_to_bezel_top/W": (height - d.face(d.bezel_s1)[1]) / w,
        "land_mid": d.side_x(z_mid) - d.edge_in - d.bezel_w / 2 - d.panel_gap,
        "land_top": d.side_x(z_top) - d.edge_in - d.bezel_w / 2 - d.panel_gap,
        "gap_top": d.side_x(z_top) - d.bezel_w / 2, "z_bezel_top": z_top,
        "rail_seen": hw - d.bezel_w / 2, "bezel/W": d.bezel_w / w,
        "half": hw, "tuck": d.tuck, "hood_corner_r": d.hood_corner_ratio * w,
        "hood_foot": 2 * h.half_base, "hood_top_flat": 2 * h.half_top,
        "deck_centre": d.deck_centre_frac * w, "deck_corner_r": d.deck_corner_frac * w,
        "deck_border_side": hw - d.panel_w / 2, "deck_border_flat": hw - d.edge_in - d.panel_w / 2 - d.panel_gap,
        "panel_depth_side": panel[-1][1] - panel[0][1], "panel_front_mid": 2 * panel[2][0],
        "mq_w": mq_w, "mq_modules": mq_w // d.marquee_module, "mq_widest": mq_max,
        "spk_w_foot": leg(v0) - xi, "spk_w_head": leg(v1) - xi, "spk_span": 2 * leg(v0), "spk_x_out": leg(v0),
        "logo_w": d.logo_w, "rear_w": d.rear_w, "step": hw - d.rear_w / 2,
        "frame_side": d.frame_side, "bezel_w": d.bezel_w, "opening_half": d.bezel_w / 2 - BEZEL_LEDGE,
        "pass_right_angle": d.bezel_w / 2 - BEZEL_LEDGE - MON_SWEPT - PLUG_RIGHT_ANGLE,
        "pass_right_angle_centred": d.bezel_w / 2 - BEZEL_LEDGE - MON_SWEPT + MON_ADJUST - PLUG_RIGHT_ANGLE,
        "pass_straight": d.bezel_w / 2 - BEZEL_LEDGE - MON_SWEPT - PLUG_STRAIGHT,
        "pass_right_angle_no_side_ledge": d.bezel_w / 2 - MON_SWEPT - PLUG_RIGHT_ANGLE,
        "pass_bare_monitor": d.bezel_w / 2 - BEZEL_LEDGE - MON_SWEPT,
    }
