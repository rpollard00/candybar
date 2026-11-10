from __future__ import annotations

import unittest

import FreeCAD as App

from candybar import check

from . import support


class CheckerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.doc: App.Document = self.enterContext(support.saved_document())

    def new_fails(self, **values: float) -> set[tuple[str, str]]:
        _, baseline = support.baseline()
        support.edit(self.doc, **values)
        return support.fail_rows(check.run(self.doc)) - support.fail_rows(baseline)

    def test_baseline_has_no_fail(self) -> None:
        _, baseline = support.baseline()
        self.assertEqual(sorted(support.fail_rows(baseline)), [])

    def test_reopened_document_checks_the_same_as_the_fresh_build(self) -> None:
        _, baseline = support.baseline()
        self.assertEqual(check.run(self.doc).rows, baseline.rows)

    def test_shallow_cabinet_fails_interference_keepout_or_containment(self) -> None:
        rules = {rule for rule, _ in self.new_fails(cab_d=430)}
        self.assertTrue(rules & {"R1", "R2", "R3"}, rules)

    def test_wider_nut_fails_button_spacing(self) -> None:
        rules = {rule for rule, _ in self.new_fails(btn_nut_d=38)}
        self.assertIn("R5", rules)

    def test_lever_far_left_makes_the_button_tile_too_big_to_print(self) -> None:
        self.assertIn(("R4", "Deck_Buttons"), self.new_fails(stick_x=-110))

    def test_steep_recline_fails_interference_or_keepout(self) -> None:
        rules = {rule for rule, _ in self.new_fails(recline=40)}
        self.assertTrue(rules & {"R1", "R2"}, rules)
