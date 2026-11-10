from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import FreeCAD as App

from candybar import params

HEADER = ",".join(params.COLUMNS)
GOOD = "panel_w,380,mm,provisional,,design choice,Panel width"
STICK_X = "stick_x,-75,mm,provisional,,,Lever"
EDGE_X = "edge_x,=stick_x - panel_w / 2,mm,derived,,,Edge"


def write_sheets(folder: Path, controls_rows: list[str]) -> Path:
    for filename in params.FILES:
        rows = controls_rows if filename == "controls.csv" else []
        (folder / filename).write_text("\n".join([HEADER, *rows]) + "\n", encoding="utf-8")
    return folder


class LoadTest(unittest.TestCase):
    def setUp(self) -> None:
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def load(self, *rows: str) -> list[params.Param]:
        return params.load(write_sheets(self.folder, list(rows)))

    def test_valid_rows_load_in_order(self) -> None:
        loaded = self.load(GOOD, "half_w,=panel_w / 2,mm,derived,,,Half the panel")
        self.assertEqual([row.name for row in loaded], ["panel_w", "half_w"])
        self.assertEqual([row.cell_text for row in loaded], ["=380 mm", "=panel_w / 2"])

    def test_duplicate_name_is_rejected(self) -> None:
        with self.assertRaisesRegex(params.ParamError, r"controls\.csv row 3 \('panel_w'\): duplicate name.*controls\.csv row 2"):
            self.load(GOOD, "panel_w,390,mm,provisional,,,Again")

    def test_name_that_reads_as_a_cell_address_is_rejected(self) -> None:
        with self.assertRaisesRegex(params.ParamError, r"controls\.csv row 3 \('BC250'\): not a legal alias"):
            self.load(GOOD, "BC250,307.6,mm,sourced,,,Board length")

    def test_unknown_status_is_rejected(self) -> None:
        with self.assertRaisesRegex(params.ParamError, r"controls\.csv row 3 \('deck_t'\): unknown status 'guessed'"):
            self.load(GOOD, "deck_t,5,mm,guessed,,,Deck thickness")

    def test_non_numeric_literal_is_rejected(self) -> None:
        with self.assertRaisesRegex(params.ParamError, r"controls\.csv row 3 \('deck_t'\): value 'five'"):
            self.load(GOOD, "deck_t,five,mm,provisional,,,Deck thickness")


class SheetTest(unittest.TestCase):
    def setUp(self) -> None:
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.doc = App.newDocument("candybar_params_test")
        self.addCleanup(App.closeDocument, self.doc.Name)

    def write(self, *rows: str) -> None:
        params.write_sheet(self.doc, params.load(write_sheets(self.folder, list(rows))))

    def test_values_evaluate_with_units_and_signs(self) -> None:
        self.write(GOOD, STICK_X, EDGE_X, "btn_count,8,,provisional,,,Buttons")
        values = [params.value(self.doc, name) for name in ("panel_w", "stick_x", "edge_x", "btn_count")]
        self.assertEqual(values, [380, -75, -265, 8])

    def test_edit_keeps_the_unit_and_moves_dependent_cells(self) -> None:
        self.write(GOOD, STICK_X, EDGE_X)
        params.edit(self.doc, "stick_x", -60)
        self.doc.recompute()
        self.assertEqual(params.value(self.doc, "edge_x"), -250)

    def test_name_that_is_a_unit_is_rejected(self) -> None:
        with self.assertRaisesRegex(params.ParamError, r"controls\.csv row 3 \('deg'\): FreeCAD rejects this name"):
            self.write(GOOD, "deg,22,deg,provisional,,,Recline")

    def test_formula_that_does_not_evaluate_is_rejected(self) -> None:
        with self.assertRaisesRegex(params.ParamError, r"controls\.csv row 3 \('half_w'\): '=panel_width / 2' does not evaluate"):
            self.write(GOOD, "half_w,=panel_width / 2,mm,derived,,,Half the panel")

    def test_formula_with_the_wrong_unit_is_rejected(self) -> None:
        message = r"controls\.csv row 3 \('half_w'\): evaluates to .* does not match the unit column 'deg'"
        with self.assertRaisesRegex(params.ParamError, message):
            self.write(GOOD, "half_w,=panel_w / 2,deg,derived,,,Half the panel")
