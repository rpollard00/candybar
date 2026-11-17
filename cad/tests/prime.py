"""Make one of the caches that the tests read, before the tests run (cad/tests/parallel.py, the step "prime").

The tests make these caches themselves when they are missing, but two test processes that make the same cache at
the same time write the same file, and a third can read it half written. The parallel run makes each cache here,
once, after the skin is in the cache of the split; then the tests only read it. Each cache is in its own files, so
the steps after "skin" can run at the same time.

    CANDYBAR_PRIME=<step> cad/candybar/freecad-run.sh tests.prime

Steps:
  skin     the skin of the shell (split.build_modules, in cad/out/shell-rev7/split/cache or CANDYBAR_SPLIT_CACHE)
  pieces   the plain pieces of the split (pieces.plain, in cad/out/pieces/cache or CANDYBAR_PIECES_CACHE)
  deck     the skin of the deck (panel_frame.deck_skin, beside the skin in the cache of the split)
  zones    the skin round the mounts (mounts.zones, beside the skin)
  coupons  every coupon of the set, for the cuts of the real skin and the floor tile (in cad/out/coupons/cache)
  hood     the base parts of the hood band (hood_band.base, in cad/out/hood-band/base)
"""
from __future__ import annotations

import os
from pathlib import Path

CAD = Path(__file__).resolve().parents[1]


def skin() -> None:
    from candybar.shell import split
    from candybar.shell.dims import Blueprint

    split.build_modules(Blueprint(), print)


def pieces() -> None:
    from candybar.shell import pieces as pc
    from candybar.shell.dims import Blueprint

    pc.plain(Blueprint(), Path(os.environ.get("CANDYBAR_PIECES_CACHE") or pc.CAD / "out" / "pieces"), print)


def deck() -> None:
    from candybar.shell import panel_frame
    from candybar.shell.dims import Blueprint

    panel_frame.deck_skin(Blueprint(), print)


def zones() -> None:
    from candybar.shell import mounts
    from candybar.shell.dims import Blueprint

    mounts.zones(Blueprint(), print)


def coupons() -> None:
    from candybar.shell import coupons as co

    for item in co.items():
        item.make()


def hood() -> None:
    from candybar.shell import hood_band
    from candybar.shell.dims import Blueprint

    hood_band.base(CAD / "out" / "hood-band", Blueprint(), [])


STEPS = {"skin": skin, "pieces": pieces, "deck": deck, "zones": zones, "coupons": coupons, "hood": hood}


def main() -> int:
    step = os.environ.get("CANDYBAR_PRIME", "")
    if step not in STEPS:
        print(f"CANDYBAR_PRIME must be one of {', '.join(STEPS)}, not {step!r}")
        return 2
    STEPS[step]()
    return 0
