from __future__ import annotations

import unittest
from unittest import mock

import FreeCAD as App

from candybar import build, check, params

from . import support

NAME = "candybar_build_test"


class BuildDocumentTest(unittest.TestCase):
    def test_six_buttons_build_six_buttons_and_six_holes(self) -> None:
        doc = build.build_document(support.params_copy({"btn_count": "6"}), name=NAME)
        self.addCleanup(App.closeDocument, doc.Name)
        bodies = sorted(obj.Name for obj in doc.Objects if obj.Name.startswith("Btn") and obj.Name.endswith("_Body"))
        self.assertEqual(bodies, [f"Btn{i}_Body" for i in range(1, 7)])
        self.assertEqual([obj.Name for obj in doc.Objects if obj.Name.startswith(("Btn7", "Btn8"))], [])
        tile = doc.getObject("Deck_Buttons").Shape
        self.assertEqual(len(support.hole_centres(tile, params.value(doc, "btn_hole_d"))), 6)
        self.assertEqual(support.fail_rows(check.run(doc)), set())

    def test_lever_tile_has_an_insert_hole_in_each_boss(self) -> None:
        with support.saved_document() as doc:
            tile = doc.getObject("Deck_Lever").Shape
            self.assertEqual(len(support.hole_centres(tile, params.value(doc, "stick_insert_d"))), 4)

    def test_open_document_with_unsaved_changes_is_not_replaced(self) -> None:
        App.newDocument(NAME)
        self.addCleanup(App.closeDocument, NAME)
        gui = mock.Mock()
        gui.getDocument.return_value.Modified = True
        with mock.patch.object(App, "GuiUp", 1), mock.patch.object(App, "Gui", gui, create=True):
            with self.assertRaisesRegex(RuntimeError, "unsaved changes"):
                build.build_document(name=NAME)
        self.assertEqual(App.getDocument(NAME).Objects, [])

    def test_failed_build_closes_the_document_it_started(self) -> None:
        with self.assertRaisesRegex(params.ParamError, "btn_count must be one of"):
            build.build_document(support.params_copy({"btn_count": "7"}), name=NAME)
        self.assertNotIn(NAME, App.listDocuments())


class ComputeModuleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.doc: App.Document = self.enterContext(support.saved_document())
        self.solids = support.solids(self.doc)

    def value(self, name: str) -> float:
        return params.value(self.doc, name)

    def test_board_stands_on_its_straight_edge_with_the_power_connector_on_top(self) -> None:
        bottom, top = self.value("bc_bottom_z"), self.value("bc_top_z")
        narrow_part = self.solids["Compute_PCB_IO"].world.BoundBox
        self.assertAlmostEqual(narrow_part.ZMin, bottom, places=6)
        self.assertAlmostEqual(narrow_part.ZMax, bottom + self.value("bc_pcb_w_io"), places=6)
        self.assertAlmostEqual(self.solids["Compute_Heatsink"].world.BoundBox.ZMin, bottom + self.value("bc_fin_y0"), places=6)
        self.assertAlmostEqual(self.solids["Compute_PowerPlug"].world.BoundBox.ZMin, top, places=6)

    def test_rear_door_vents_open_onto_the_fan_and_the_exhaust_duct(self) -> None:
        skin = self.solids["Shell_Skin"].world
        in_the_rear_wall = self.value("rear_inner_y") + self.value("rear_t") / 2
        half_fan = self.value("fan_frame") / 2
        shroud = self.solids["Compute_FanShroud"].world.BoundBox
        self.assertGreaterEqual(self.value("vent_fan_x") - half_fan, shroud.XMin)
        self.assertLessEqual(self.value("vent_fan_x") + half_fan, shroud.XMax)
        self.assertGreaterEqual(self.value("vent_fan_z") - half_fan, shroud.ZMin)
        self.assertLessEqual(self.value("vent_fan_z") + half_fan, shroud.ZMax)
        fan_vent = App.Vector(self.value("vent_fan_x"), in_the_rear_wall, self.value("vent_fan_z"))
        self.assertFalse(skin.isInside(fan_vent, 0.01, True))

        duct = self.solids["Compute_ExhaustDuct"].world.BoundBox
        left, bottom = self.value("vent_out_x0"), self.value("vent_out_z0")
        right, top = left + self.value("vent_out_w"), bottom + self.value("vent_out_h")
        self.assertGreaterEqual(left, duct.XMin)
        self.assertLessEqual(right, duct.XMax)
        self.assertGreaterEqual(bottom, duct.ZMin)
        self.assertLessEqual(top, duct.ZMax)
        hot_air_vent = App.Vector((left + right) / 2, in_the_rear_wall, (bottom + top) / 2)
        self.assertFalse(skin.isInside(hot_air_vent, 0.01, True))

    def test_left_side_wall_has_no_vent(self) -> None:
        skin = self.solids["Shell_Skin"].world
        in_the_side_wall = App.Vector(-self.value("inner_w") / 2 - 2, self.value("bc_pcb_y"), self.value("bc_bottom_z") + 60)
        self.assertTrue(skin.isInside(in_the_side_wall, 0.01, True))
