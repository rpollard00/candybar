from __future__ import annotations

import unittest

import Part

from candybar import model

from . import support

RELATIVE_TOLERANCE = 1e-4


class LayoutStepTest(unittest.TestCase):
    def test_layout_step_holds_every_solid_on_show_and_no_alternate_or_keepout(self) -> None:
        out, _ = support.baseline()
        with support.saved_document() as doc:
            on_show = [solid for solid in model.placed(doc) if solid.role != "keepout" and not solid.alternate]
            hidden = [solid for solid in model.placed(doc) if solid.role == "keepout" or solid.alternate]
        self.assertGreaterEqual(len(hidden), 4)
        self.assertEqual(len(Part.read(str(out / "candybar.step")).Solids), len(on_show))


class StepRoundTripTest(unittest.TestCase):
    def test_each_printable_step_reimports_with_the_same_box_and_volume(self) -> None:
        out, _ = support.baseline()
        with support.saved_document() as doc:
            printables = [solid for solid in model.placed(doc) if solid.role == "printable"]
        self.assertGreaterEqual(len(printables), 2)
        for part in printables:
            with self.subTest(part=part.name):
                original = part.own
                reimported = Part.read(str(out / "step" / f"{part.name}.step"))
                size = original.BoundBox.DiagonalLength
                for corner in ("XMin", "YMin", "ZMin", "XMax", "YMax", "ZMax"):
                    difference = getattr(reimported.BoundBox, corner) - getattr(original.BoundBox, corner)
                    self.assertLessEqual(abs(difference), RELATIVE_TOLERANCE * size, corner)
                self.assertLessEqual(abs(reimported.Volume - original.Volume), RELATIVE_TOLERANCE * original.Volume)
