"""The solids of the blueprint: valid parts that do not overlap, and a check that notices a solid off the blueprint."""
from __future__ import annotations

import unittest
from dataclasses import replace

from candybar.shell import solids
from candybar.shell.dims import Blueprint
from tools import check_solids


def over(row: dict) -> bool:
    return max(row["solid_to_blueprint"], row["blueprint_to_solid"]) > check_solids.TOL


def failing(report: dict) -> set[str]:
    return {name for name, row in [*report["sections"].items(), *report["silhouettes"].items()] if over(row)}


class BlueprintSolidsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d = Blueprint()
        cls.baseline = check_solids.run(solids.build(cls.d), cls.d)

    def test_every_part_is_one_valid_closed_solid(self) -> None:
        for name, state in self.baseline["parts"].items():
            with self.subTest(part=name):
                self.assertTrue(state["valid"] and state["closed"] and state["check"])
                self.assertEqual(state["solids"], 1)
                self.assertGreater(state["volume_mm3"], 0)

    def test_no_two_parts_overlap(self) -> None:
        self.assertEqual(self.baseline["overlaps"], [])

    def test_sections_clear_of_the_blueprint_defects_match_it(self) -> None:
        for name in ("X side band", "Z deck", "Z mid body", "Z tuck", "Z hood"):
            with self.subTest(plane=name):
                self.assertFalse(over(self.baseline["sections"][name]))

    def assert_check_notices(self, **change: float) -> None:
        changed = check_solids.run(solids.build(replace(self.d, **change)), self.d)
        new = failing(changed) - failing(self.baseline)
        self.assertFalse(changed["ok"])
        self.assertTrue(new, f"no view or section fails that passed before: {change}")

    def test_check_notices_a_stronger_rail_arc(self) -> None:
        self.assert_check_notices(rail_sagitta_ratio=self.d.rail_sagitta_ratio + 0.01)

    def test_check_notices_a_smaller_tuck(self) -> None:
        self.assert_check_notices(body_tuck_ratio=self.d.body_tuck_ratio - 0.008)
