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

    def test_every_view_and_section_matches_the_blueprint(self) -> None:
        self.assertEqual(failing(self.baseline), set())
        self.assertTrue(self.baseline["ok"])

    def test_no_point_of_a_section_is_skipped(self) -> None:
        self.assertEqual(sum(row["bridged_points"] for row in self.baseline["sections"].values()), 0)

    def assert_check_notices(self, **change: float) -> None:
        changed = check_solids.run(solids.build(replace(self.d, **change)), self.d)
        self.assertFalse(changed["ok"])
        self.assertTrue(failing(changed), f"no view or section fails: {change}")

    def test_check_notices_a_stronger_rail_arc(self) -> None:
        self.assert_check_notices(rail_sagitta_ratio=self.d.rail_sagitta_ratio + 0.01)

    def test_check_notices_a_smaller_tuck(self) -> None:
        self.assert_check_notices(body_tuck_ratio=self.d.body_tuck_ratio - 0.008)
