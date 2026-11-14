"""Run by test_build_entry through freecad-run.sh: returns the number in CANDYBAR_PROBE, or raises when it is 'raise'."""
from __future__ import annotations

import os


def main() -> int:
    wanted = os.environ["CANDYBAR_PROBE"]
    if wanted == "raise":
        raise RuntimeError("the probe was told to raise")
    print("the probe ran")
    return int(wanted)
