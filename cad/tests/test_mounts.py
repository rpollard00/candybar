"""The mounts of the hardware: a finding of the fit study that the mounts do not declare stays a failure. The checks of
the mounts on the design run in their build (candybar.shell.mounts), which fails on them."""
from __future__ import annotations

import unittest

from candybar.shell import check, mounts


class FindingsTest(unittest.TestCase):
    def test_a_failure_that_is_not_declared_is_another_failure(self) -> None:
        rules = {"R2 keep-out": [(check.FAIL, "Compute_UndersideAir / Mount_TrayL", "common volume 1091 mm3"), (check.FAIL, "PSU_FanAir / Mount_TrayL", "common volume 5 mm3")],
                 "R1 interference": [(check.PASS, "10 pairs", "")]}
        declared, other = mounts.split_findings(rules)
        self.assertEqual(len(declared), 1)
        self.assertEqual(other, ["R2 keep-out: PSU_FanAir / Mount_TrayL: common volume 5 mm3"])
