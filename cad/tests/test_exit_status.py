from __future__ import annotations

import json
import os
import unittest
import zipfile
from pathlib import Path

from candybar import build

from . import support


def read_report(out: Path) -> dict:
    return json.loads((out / "report.json").read_text(encoding="utf-8"))


class ExitStatusTest(unittest.TestCase):
    def test_status_of_the_real_design_mirrors_its_report(self) -> None:
        done, out = support.shell_baseline()
        self.assertEqual(done.returncode == 0, read_report(out)["counts"]["FAIL"] == 0, done.stderr)

    def test_forced_check_failure_returns_non_zero(self) -> None:
        done, out = support.shell_build(support.params_copy({"btn_nut_d": "45"}))
        self.assertNotEqual(done.returncode, 0)
        forced = [row for row in read_report(out)["rows"] if row["rule"] == "R5" and row["level"] == "FAIL"]
        self.assertTrue(forced, done.stdout)
        self.assertIn("GuiDocument.xml", zipfile.ZipFile(out / build.SAVED).namelist())

    def test_view_step_that_cannot_start_returns_non_zero_and_says_so(self) -> None:
        stand_in = support.temp_dir() / "freecad"
        stand_in.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        stand_in.chmod(0o755)
        path = f"{stand_in.parent}{os.pathsep}{os.environ['PATH']}"
        done, out = support.shell_build(support.PARAMS, {"PATH": path})
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("View step failed", done.stderr)
        self.assertNotIn("GuiDocument.xml", zipfile.ZipFile(out / build.SAVED).namelist())

    def test_parameter_error_returns_non_zero_and_names_the_row(self) -> None:
        done, out = support.shell_build(support.params_copy({"deck_t": "five"}))
        self.assertNotEqual(done.returncode, 0)
        self.assertRegex(done.stderr, r"cabinet\.csv row \d+ \('deck_t'\): value 'five'")
        self.assertNotIn("View step failed", done.stderr)
        self.assertFalse((out / "report.json").exists())

    def test_broken_build_removes_the_outputs_of_an_earlier_good_one(self) -> None:
        _, out = support.shell_build(support.PARAMS)
        produced = sorted(path.name for path in out.iterdir() if not path.name.startswith("."))
        self.assertEqual(produced, ["candybar.FCStd", "candybar.step", "report.json", "report.md", "step", "stl"])
        done, _ = support.shell_build(support.params_copy({"deck_t": "five"}), out=out)
        self.assertNotEqual(done.returncode, 0)
        self.assertEqual([path.name for path in out.iterdir() if not path.name.startswith(".")], [])
