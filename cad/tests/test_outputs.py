"""The files of the build: the part files that solids.export writes, and the document that viewdoc saves."""
from __future__ import annotations

import json
import os
import subprocess
import unittest
from unittest import mock

import FreeCAD as App
import Part

from candybar.shell import solids, viewdoc
from candybar.shell.dims import Blueprint

from . import support


def small_parts() -> dict[str, Part.Shape]:
    """Two small solids under the names of two parts of the build (export takes the finish of a part from its name)."""
    return {"deck": Part.makeBox(40, 30, 20), "bezel": Part.makeCylinder(8, 25, App.Vector(60, 0, 0))}


class ExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.out = support.temp_dir()
        cls.parts = small_parts()
        cls.report = solids.export(str(cls.out), cls.parts, Blueprint(), ["a line of the log"])
        cls.manifest = json.loads((cls.out / "manifest.json").read_text(encoding="utf-8"))

    def test_each_part_has_a_brep_file_that_reads_back_with_the_same_volume(self) -> None:
        self.assertEqual(set(self.manifest), set(self.parts))
        for name, part in self.parts.items():
            back = Part.Shape()
            back.read(str(self.out / self.manifest[name]["brep"]))
            self.assertTrue(back.isValid(), name)
            self.assertAlmostEqual(back.Volume, part.Volume, places=6, msg=name)

    def test_each_part_has_an_stl_file_of_its_volume(self) -> None:
        import Mesh  # noqa: PLC0415

        for name, part in self.parts.items():
            mesh = Mesh.Mesh(str(self.out / self.manifest[name]["file"]))
            self.assertTrue(mesh.isSolid(), name)
            self.assertAlmostEqual(mesh.Volume / part.Volume, 1.0, places=2, msg=name)

    def test_the_step_file_holds_every_part(self) -> None:
        back = Part.Shape()
        back.read(str(self.out / "shell.step"))
        self.assertEqual(len(back.Solids), len(self.parts))
        self.assertAlmostEqual(back.Volume, sum(p.Volume for p in self.parts.values()), places=4)

    def test_the_report_has_each_part_and_the_log(self) -> None:
        self.assertEqual(self.report["log"], ["a line of the log"])
        for name, part in self.parts.items():
            row = self.report["parts"][name]
            self.assertEqual((row["valid"], row["solids"], row["faces"]), (True, 1, len(part.Faces)))


class ViewDocumentTest(unittest.TestCase):
    """viewdoc under the GUI binary: the saved document opens with each solid on show, in the colour of its finish."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.out = support.temp_dir()
        cls.parts = small_parts()
        solids.export(str(cls.out), cls.parts, Blueprint())
        cls.steps = [subprocess.run([str(support.FREECAD_RUN), "--gui", module], env=os.environ | {"CANDYBAR_OUT": str(cls.out)},
                                    capture_output=True, text=True) for module in ("candybar.shell.viewdoc", "tests.viewdoc_probe")]
        look = cls.out / "look.json"
        cls.look = json.loads(look.read_text(encoding="utf-8")) if look.exists() else {}

    def test_both_steps_end_with_status_zero(self) -> None:
        for step in self.steps:
            self.assertEqual(step.returncode, 0, step.stdout + step.stderr)

    def test_probe_runs_with_view_providers(self) -> None:
        self.assertTrue(self.look["gui"])

    def test_each_solid_is_on_show_in_the_colour_of_its_finish(self) -> None:
        self.assertEqual(set(self.look["objects"]), set(self.parts))
        for name, seen in self.look["objects"].items():
            self.assertTrue(seen["shown"], name)
            want = viewdoc.colour(solids.FINISH[name])
            for got, channel in zip(seen["colour"], want, strict=True):
                self.assertAlmostEqual(got, channel, places=2, msg=name)

    def test_the_saved_solids_have_the_volume_of_the_parts(self) -> None:
        for name, seen in self.look["objects"].items():
            self.assertAlmostEqual(seen["volume"], self.parts[name].Volume, places=4, msg=name)


class SettingsGuardTest(unittest.TestCase):
    """viewdoc changes FreeCAD's user settings, so it runs only in the throwaway user directory of freecad-run.sh."""

    def test_refuses_without_a_throwaway_user_directory(self) -> None:
        environment = {key: text for key, text in os.environ.items() if key != "CANDYBAR_THROWAWAY_HOME"}
        with mock.patch.dict(os.environ, environment, clear=True):
            with self.assertRaisesRegex(RuntimeError, "throwaway user directory"):
                viewdoc.main()

    def test_refuses_when_freecad_uses_another_user_directory(self) -> None:
        with mock.patch.dict(os.environ, {"CANDYBAR_THROWAWAY_HOME": str(support.temp_dir())}):
            with self.assertRaisesRegex(RuntimeError, "throwaway user directory"):
                viewdoc.main()

    def test_inside_the_throwaway_directory_it_goes_on_to_ask_for_the_gui(self) -> None:
        with mock.patch.dict(os.environ, {"CANDYBAR_THROWAWAY_HOME": App.getUserAppDataDir()}):
            with self.assertRaisesRegex(RuntimeError, "GUI binary"):
                viewdoc.main()
