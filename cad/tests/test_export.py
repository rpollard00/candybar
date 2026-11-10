from __future__ import annotations

import unittest

import Mesh
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


class BuildOutputsTest(unittest.TestCase):
    def test_full_build_draws_four_views_and_writes_a_true_stl_for_each_printable(self) -> None:
        done, out = support.shell_build(support.PARAMS, renders=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        for view in ("front", "right", "top", "iso"):
            self.assertGreater((out / "views" / f"{view}.png").stat().st_size, 10_000, view)
        with support.saved_document() as doc:
            printables = [solid for solid in model.placed(doc) if solid.role == "printable"]
        self.assertGreaterEqual(len(printables), 2)
        for part in printables:
            mesh = Mesh.Mesh(str(out / "stl" / f"{part.name}.stl"))
            self.assertLessEqual(abs(mesh.Volume - part.own.Volume), 0.01 * part.own.Volume, part.name)

    def test_layout_step_names_no_alternate_bezel(self) -> None:
        out, _ = support.baseline()
        text = (out / "candybar.step").read_text(encoding="utf-8", errors="replace")
        self.assertIn("Bezel_16x9", text)
        for alternate in ("Bezel_16x10", "Bezel_4x3", "Bezel_Tate"):
            self.assertNotIn(alternate, text)


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
