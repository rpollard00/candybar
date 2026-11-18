"""A study, not a part of the design: the units of the larger-monitor study and the pictures that each can show
(docs/research/larger-monitor.md). No FreeCAD: monitor_study.py and tools/draw_larger_monitor.py read this module.

A picture is the largest rectangle of one shape that lies in the lit area of a unit and in the window that a bezel
plate can have. The window cannot be larger than the opening behind the bezel plate.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .dims import MON_ACTIVE_H, MON_ACTIVE_W

# the opening behind the bezel plate, MEASURED on the skin (cuts.json of monitor_study): between the jambs, and
# between the bottom ledge and the top ledge
OPENING = (434.7, 293.4)
# the narrowest bar that a printed bezel plate can have between its outline and its window: an ESTIMATE (the rim wall
# of 2, the inner frame and a land; the present plate has 45). The plate is 433.7 x 304.4
PLATE = (433.7, 304.4)
BAR_MIN = 12.0
WINDOW_MAX = (PLATE[0] - 2 * BAR_MIN, PLATE[1] - 2 * BAR_MIN)
# the window that keeps the four lugs of the cradle out of sight: they stand 11.1 into the opening at x 30 to 72
LUG_CLEAR_H = 271.2

# a body that is larger than the opening lies behind the ledges and the jambs, which end 11.2 behind the screen face
# (MEASURED); its glass is then on GLASS_BEHIND. A body that goes into the opening has its glass on GLASS (8.2)
GLASS = 8.2
GLASS_BEHIND = 12.4
FIT = 1.0       # the smallest room between a body and the edge of the opening, on each side, for a body in the opening

SHAPES = (("16:10", 16 / 10), ("16:9", 16 / 9), ("4:3", 4 / 3), ("5:4", 5 / 4), ("tate 3:4", 3 / 4), ("tate 9:16", 9 / 16))


@dataclass(frozen=True)
class Screen:
    """A unit: the body and the lit picture as its maker gives them. up: how far the centre of the picture stands
    above the centre of the body. fits: the result of the study, for the table."""
    key: str
    kind: str
    name: str
    w: float
    h: float
    t: float
    lit_w: float
    lit_h: float
    up: float = 0.0
    mass: float = 0.0       # kg; 0 when the maker does not give it


UNITS = (
    Screen("present", "portable", "Present unit: 16.0 in 16:10 (UPERFECT BE16CU)", 354.0, 230.0, 10.6, MON_ACTIVE_W, MON_ACTIVE_H, up=8.9 + MON_ACTIVE_H / 2 - 115.0, mass=0.82),
    Screen("p173", "portable", "17.3 in 16:9 portable (UPERFECT BE173BF)", 398.0, 247.0, 12.0, 381.888, 214.812, mass=0.91),
    Screen("p18", "portable", "18 in 16:10 portable (UPERFECT GR18BQ)", 400.0, 260.0, 10.0, 387.76, 242.35, mass=0.87),
    Screen("p185", "portable", "18.5 in 16:9 portable (UPERFECT GR185BF)", 425.0, 250.0, 18.0, 408.96, 230.04, mass=1.12),
    Screen("b185", "bare panel", "18.5 in 16:9 panel (AUO M185XTN01.2)", 430.4, 254.6, 10.4, 409.8, 230.4),
    Screen("b19w", "bare panel", "19 in 16:10 panel (AUO M190PW01 V8)", 428.0, 278.0, 10.8, 408.24, 255.15),
    Screen("b19", "bare panel", "19 in 5:4 panel (AUO M190EG02 V9)", 396.0, 324.0, 11.4, 376.32, 301.056, mass=1.8),
    Screen("o19", "open frame", "19 in 5:4 open frame (Elo 1990L)", 414.7, 342.7, 50.0, 376.32, 301.06, mass=4.6),
    Screen("d19", "desktop", "19 in 5:4 desktop, no stand (Dell P1917S)", 405.6, 334.3, 50.3, 376.32, 301.056),
    Screen("b17", "bare panel", "17 in 5:4 panel (AUO M170EG01 V7)", 358.5, 296.5, 17.5, 337.92, 270.336),
    Screen("b15", "bare panel", "15 in 4:3 panel (AUO G150XTN06)", 326.5, 253.5, 12.0, 304.128, 228.096),
)


def glass_t(w: float, h: float) -> float:
    """The depth of the glass of a body w x h behind the screen face."""
    return GLASS if w + 2 * FIT <= OPENING[0] and h + 2 * FIT <= OPENING[1] else GLASS_BEHIND


def diagonal_in(w: float, h: float) -> float:
    return math.hypot(w, h) / 25.4


def picture(lit: tuple[float, float], ratio: float, window: tuple[float, float] = WINDOW_MAX) -> tuple[float, float]:
    """The largest rectangle of width / height = ratio in a lit area that is seen through a window of at most
    `window`. The lit area and the window have the same centre."""
    w, h = min(lit[0], window[0]), min(lit[1], window[1])
    return (h * ratio, h) if w / h > ratio else (w, w / ratio)


def pictures(u: Screen, turned: bool = False, window: tuple[float, float] = WINDOW_MAX) -> dict[str, tuple[float, float]]:
    """Each shape of SHAPES on a unit. turned: the unit lies with its long side up the face."""
    lit = (u.lit_h, u.lit_w) if turned else (u.lit_w, u.lit_h)
    return {name: picture(lit, r, window) for name, r in SHAPES}


def table(window: tuple[float, float] = WINDOW_MAX) -> list[dict]:
    """A row for each unit: each picture as width, height, diagonal in inches, and its diagonal over that of the
    present unit (the first of UNITS) for the same shape."""
    base = {k: diagonal_in(*p) for k, p in pictures(UNITS[0], window=window).items()}
    rows = []
    for u in UNITS:
        for turned in (False, True):
            cells = {}
            for k, (w, h) in pictures(u, turned, window).items():
                d = diagonal_in(w, h)
                cells[k] = {"w": round(w, 1), "h": round(h, 1), "in": round(d, 1), "gain": round(d / base[k] - 1, 3)}
            rows.append({"key": u.key, "name": u.name, "turned": turned, "cells": cells})
    return rows
