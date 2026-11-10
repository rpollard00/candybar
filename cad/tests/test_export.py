from __future__ import annotations

import unittest

import Part

from candybar import model

from . import support

RELATIVE_TOLERANCE = 1e-4


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
