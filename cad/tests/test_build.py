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
