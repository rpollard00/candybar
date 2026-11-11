from __future__ import annotations

import math
import unittest

import FreeCAD as App
import Part

from candybar import check, model, params

from . import support


class LiveParametricsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.doc: App.Document = self.enterContext(support.saved_document())

    def value(self, name: str) -> float:
        return params.value(self.doc, name)

    def edit(self, **values: float) -> None:
        support.edit(self.doc, **values)
        self.assertEqual(model.errors(self.doc), [])

    def shape(self, name: str, frame: str = "world") -> Part.Shape:
        return getattr(support.solids(self.doc)[name], frame)

    def test_recline_tilts_the_monitor_lowers_its_top_and_moves_it_rearward(self) -> None:
        before = self.shape("Monitor_Body").BoundBox
        recline = self.value("recline") + 5
        self.edit(recline=recline)
        after = self.shape("Monitor_Body").BoundBox
        self.assertLess(after.ZMax, before.ZMax - 1)
        self.assertGreater(after.YMax, before.YMax + 1)
        tilt = math.radians(recline)
        depth_when_tilted = self.value("mon_h") * math.sin(tilt) + self.value("mon_t") * math.cos(tilt)
        self.assertAlmostEqual(after.YLength, depth_when_tilted, places=4)

    def test_stick_x_moves_the_shaft_hole_and_the_seam(self) -> None:
        hole_d = self.value("stick_shaft_hole_d")
        (hole_before,) = support.hole_centres(self.shape("Deck_Lever", "assembly"), hole_d)
        lever_before = self.shape("Deck_Lever", "own").BoundBox.XLength
        buttons_before = self.shape("Deck_Buttons", "own").BoundBox.XLength
        self.edit(stick_x=self.value("stick_x") + 15)
        (hole_after,) = support.hole_centres(self.shape("Deck_Lever", "assembly"), hole_d)
        self.assertAlmostEqual(hole_after[0], hole_before[0] + 15, places=4)
        self.assertAlmostEqual(hole_after[1], hole_before[1], places=4)
        self.assertAlmostEqual(self.shape("Deck_Lever", "own").BoundBox.XLength, lever_before + 15, places=4)
        self.assertAlmostEqual(self.shape("Deck_Buttons", "own").BoundBox.XLength, buttons_before - 15, places=4)

    def test_psu_depth_is_measured_forward_from_the_rear_wall(self) -> None:
        depth = self.value("psu_d") - 15
        self.edit(psu_d=depth)
        body = self.shape("PSU_Body").BoundBox
        self.assertAlmostEqual(body.YLength, depth, places=4)
        self.assertAlmostEqual(body.YMax, self.value("rear_inner_y"), places=4)

    def test_psu_as_deep_as_its_bay_is_a_valid_design(self) -> None:
        _, baseline = support.baseline()
        bay_depth = self.value("psu_d_max")
        self.edit(psu_d=bay_depth)
        self.assertAlmostEqual(self.shape("PSU_Body").BoundBox.YLength, bay_depth, places=4)
        self.assertEqual(support.fail_rows(check.run(self.doc)) - support.fail_rows(baseline), set())

    def test_deck_thickness_changes_both_tiles_but_not_the_boss_faces(self) -> None:
        thickness = self.value("deck_t") - 1
        self.edit(deck_t=thickness)
        for name in ("Deck_Lever", "Deck_Buttons"):
            tile = self.shape(name, "assembly")
            self.assertAlmostEqual(tile.BoundBox.ZMax, 0, places=4, msg=name)
            self.assertAlmostEqual(support.underside_z(tile), -thickness, places=4, msg=name)
        self.assertAlmostEqual(self.shape("Deck_Buttons", "assembly").BoundBox.ZMin, -thickness, places=4)
        self.assertAlmostEqual(self.shape("Deck_Lever", "assembly").BoundBox.ZMin, -self.value("stick_plate_drop"), places=4)

    def test_button_offset_moves_its_hole(self) -> None:
        hole_d = self.value("btn_hole_d")
        before = support.hole_centres(self.shape("Deck_Buttons", "assembly"), hole_d)
        self.edit(btn1_dx=self.value("btn1_dx") + 2)
        after = support.hole_centres(self.shape("Deck_Buttons", "assembly"), hole_d)
        ((old_x, old_y),) = set(before) - set(after)
        ((new_x, new_y),) = set(after) - set(before)
        self.assertAlmostEqual(new_x, old_x + 2, places=4)
        self.assertAlmostEqual(new_y, old_y, places=4)
        self.assertAlmostEqual(new_x, self.value("stick_x") + self.value("btn1_dx"), places=4)
