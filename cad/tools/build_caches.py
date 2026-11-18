"""Make one of the caches of the skin, as a step of its own (cad/tools/chain.py).

Several packages make these caches when they are missing, and two processes that make the same cache at the same
time write the same file. The chain makes each one here, once, before the packages that read it start.

    CANDYBAR_CACHE=<name> cad/candybar/freecad-run.sh tools.build_caches

Names:
  skin   the skin of the shell (split.build_modules, in cad/out/shell-rev7/split/cache or CANDYBAR_SPLIT_CACHE)
  deck   the skin of the deck (panel_frame.deck_skin, beside the skin)
  zones  the skin round the mounts (mounts.zones, beside the skin)
"""
from __future__ import annotations

import os
import time


def main() -> int:
    from candybar.shell.dims import Blueprint

    name = os.environ.get("CANDYBAR_CACHE", "")
    d, start = Blueprint(), time.monotonic()
    if name == "skin":
        from candybar.shell import split
        split.build_modules(d, print)
    elif name == "deck":
        from candybar.shell import panel_frame
        panel_frame.deck_skin(d, print)
    elif name == "zones":
        from candybar.shell import mounts
        mounts.zones(d, print)
    else:
        print(f"CANDYBAR_CACHE must be skin, deck or zones, not {name!r}")
        return 2
    print(f"cache {name}: {time.monotonic() - start:.0f} s")
    return 0
