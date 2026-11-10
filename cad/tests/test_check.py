from __future__ import annotations

import unittest
from unittest import mock

import FreeCAD as App
import Part

from candybar import check, massing, model, params

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
        rules = {rule for rule, _ in self.new_fails(cab_d=440)}
        self.assertTrue(rules & {"R1", "R2", "R3"}, rules)

    def test_power_supply_pushed_into_the_side_wall_fails_interference_with_the_skin(self) -> None:
        moved_left = params.value(self.doc, "psu_x0") - 10
        self.assertIn(("R1", "PSU_Body / Shell_Skin"), self.new_fails(psu_x0=moved_left))

    def test_hardware_through_a_trim_plate_fails_interference(self) -> None:
        through_the_bezel = params.value(self.doc, "bundle_y0") - 25
        self.assertIn(("R1", "CableBundle_Body / Bezel_16x9"), self.new_fails(bundle_y0=through_the_bezel))

    def test_keepout_through_a_trim_plate_fails_the_keepout_rule(self) -> None:
        longer_trunk = params.value(self.doc, "psu_trunk_clear") + 15
        self.assertIn(("R2", "PSU_Trunk / Bezel_16x9"), self.new_fails(psu_trunk_clear=longer_trunk))

    def test_hardware_in_the_recess_between_the_cheeks_fails_containment(self) -> None:
        proud_of_the_bezel = params.value(self.doc, "mon_bottom_y") - 8
        self.assertIn(("R3", "Monitor_Body"), self.new_fails(mon_bottom_y=proud_of_the_bezel))

    def test_tagged_object_that_is_not_one_solid_fails_the_state_rule(self) -> None:
        lumps = self.doc.addObject("Part::Feature", "TwoLumps")
        lumps.Shape = Part.makeCompound([Part.makeBox(5, 5, 5), Part.makeBox(5, 5, 5, App.Vector(20, 0, 0))])
        model.tag(lumps, "massing", massing.OWNER)
        self.assertIn(("R0", "TwoLumps"), support.fail_rows(check.run(self.doc)))

    def test_rule_that_raises_becomes_a_fail_row(self) -> None:
        def broken(scene: check.Scene) -> list[check.Finding]:
            raise RuntimeError("no such shape")

        with mock.patch.object(check, "RULES", (("R9", "broken rule", broken),)):
            rows = check.run(self.doc).rows
        self.assertEqual(rows, (check.Row("R9", "broken rule", check.FAIL, "rule could not run", "RuntimeError: no such shape"),))

    def test_wider_nut_fails_button_spacing(self) -> None:
        rules = {rule for rule, _ in self.new_fails(btn_nut_d=38)}
        self.assertIn("R5", rules)

    def test_lever_far_left_makes_the_button_tile_too_big_to_print(self) -> None:
        self.assertIn(("R4", "Deck_Buttons"), self.new_fails(stick_x=-110))

    def test_steep_recline_fails_interference_or_keepout(self) -> None:
        rules = {rule for rule, _ in self.new_fails(recline=40)}
        self.assertTrue(rules & {"R1", "R2"}, rules)
