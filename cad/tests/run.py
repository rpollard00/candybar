from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent


def main() -> int:
    loader = unittest.TestLoader()
    if only := os.environ.get("CANDYBAR_TESTS"):
        loader.testNamePatterns = [f"*{only}*"]
    suite = loader.discover(str(TESTS), top_level_dir=str(TESTS.parent))
    from . import support

    try:
        result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    finally:
        support.remove_temp_dirs()
    return 0 if result.wasSuccessful() and result.testsRun else 1
