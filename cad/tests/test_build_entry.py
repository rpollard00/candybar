"""The build entry: the exit status of freecad-run.sh, what cad/build.sh does when a step cannot run, and what
cad/check.sh does when a check fails."""
from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path

from . import support

BUILD = support.CAD / "build.sh"
CHECK = support.CAD / "check.sh"
CHECKS = ("tools.check_solids", "tools.face_check", "tools.edge_finish", "candybar.shell.fit", "candybar.shell.split", "candybar.shell.structure")
# what an earlier build left: part files, which a new build must not leave when it breaks, and the results of the
# studies, which it must keep
PART_FILES = ("body.brep", "body.stl", "shell.step", "shell.FCStd", "manifest.json", "report.json", "focus.json", "edges.json")
KEPT = ("fit/report.md", "split/cache/body-0123456789abcdef.bin", "check.md")


def stand_in(name: str, script: str) -> Path:
    """A directory with a program `name` that runs `script` in place of FreeCAD."""
    folder = support.temp_dir()
    program = folder / name
    program.write_text(f"#!/bin/sh\n{script}\n", encoding="utf-8")
    program.chmod(0o755)
    return folder


def path_with(*folders: Path) -> dict[str, str]:
    return {"PATH": os.pathsep.join([*(str(f) for f in folders), os.environ["PATH"]])}


REPORTS_SUCCESS = 'echo 0 > "$CANDYBAR_STATUS"'
CANNOT_START = "exit 1"


class LauncherTest(unittest.TestCase):
    def run_probe(self, wanted: str, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        env = os.environ | {"CANDYBAR_OUT": str(support.temp_dir()), "CANDYBAR_PROBE": wanted} | (extra_env or {})
        return subprocess.run([str(support.FREECAD_RUN), "tests.launch_probe"], env=env, capture_output=True, text=True)

    def test_the_result_of_the_module_is_the_exit_status(self) -> None:
        for wanted in (0, 1, 3):
            done = self.run_probe(str(wanted))
            self.assertEqual(done.returncode, wanted, done.stderr)
            self.assertIn("the probe ran", done.stdout)

    def test_an_error_in_the_module_gives_status_one_and_its_traceback(self) -> None:
        done = self.run_probe("raise")
        self.assertEqual(done.returncode, 1)
        self.assertIn("RuntimeError: the probe was told to raise", done.stderr)

    def test_freecad_that_cannot_start_gives_status_one_and_says_so(self) -> None:
        done = self.run_probe("0", path_with(stand_in("freecadcmd", CANNOT_START)))
        self.assertEqual(done.returncode, 1)
        self.assertIn("FreeCAD ended without reporting a result for tests.launch_probe", done.stderr)


class BuildScriptTest(unittest.TestCase):
    """cad/build.sh with stand-ins for the two FreeCAD programs: the script's own rules, without a build."""

    def earlier_build(self) -> Path:
        out = support.temp_dir()
        for name in (*PART_FILES, *KEPT):
            (out / name).parent.mkdir(parents=True, exist_ok=True)
            (out / name).write_text("from an earlier build", encoding="utf-8")
        return out

    def build(self, out: Path, *folders: Path, args: tuple[str, ...] = ()) -> subprocess.CompletedProcess[str]:
        env = os.environ | {"CANDYBAR_OUT": str(out)} | path_with(*folders)
        return subprocess.run([str(BUILD), *args], env=env, capture_output=True, text=True)

    def left(self, out: Path) -> set[str]:
        return {str(path.relative_to(out)) for path in out.rglob("*") if path.is_file() and ".freecad" not in path.parts}

    def test_a_build_that_cannot_start_leaves_no_part_file_of_an_earlier_build(self) -> None:
        out = self.earlier_build()
        done = self.build(out, stand_in("freecadcmd", CANNOT_START))
        self.assertNotEqual(done.returncode, 0)
        self.assertEqual(self.left(out), set(KEPT))

    def test_a_view_step_that_cannot_start_returns_non_zero_and_says_so(self) -> None:
        done = self.build(support.temp_dir(), stand_in("freecadcmd", REPORTS_SUCCESS), stand_in("freecad", CANNOT_START))
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("View step failed", done.stderr)

    def test_a_failed_first_step_does_not_run_the_view_step(self) -> None:
        marker = support.temp_dir() / "view-step-ran"
        done = self.build(support.temp_dir(), stand_in("freecadcmd", 'echo 1 > "$CANDYBAR_STATUS"'), stand_in("freecad", f'touch "{marker}"'))
        self.assertEqual(done.returncode, 1)
        self.assertFalse(marker.exists())
        self.assertNotIn("View step failed", done.stderr)

    def test_two_good_steps_return_zero(self) -> None:
        done = self.build(support.temp_dir(), stand_in("freecadcmd", REPORTS_SUCCESS), stand_in("freecad", REPORTS_SUCCESS))
        self.assertEqual(done.returncode, 0, done.stderr)

    def test_an_argument_is_rejected(self) -> None:
        done = self.build(support.temp_dir(), args=("--no-render",))
        self.assertEqual(done.returncode, 2)
        self.assertIn("usage", done.stderr)


class CheckScriptTest(unittest.TestCase):
    """cad/check.sh with a stand-in for FreeCAD that notes each module it is asked to run."""

    def check(self, failing: str = "", built: bool = True) -> tuple[subprocess.CompletedProcess[str], list[str]]:
        out = support.temp_dir()
        if built:
            (out / "manifest.json").write_text("{}", encoding="utf-8")
        ran = out / "ran.txt"
        script = f'echo "$CANDYBAR_MODULE" >> "{ran}"; [ "$CANDYBAR_MODULE" = "{failing}" ] && echo 1 > "$CANDYBAR_STATUS" || echo 0 > "$CANDYBAR_STATUS"'
        env = os.environ | {"CANDYBAR_OUT": str(out)} | path_with(stand_in("freecadcmd", script))
        done = subprocess.run([str(CHECK)], env=env, capture_output=True, text=True)
        return done, ran.read_text(encoding="utf-8").split() if ran.exists() else []

    def test_every_check_runs_and_all_good_checks_return_zero(self) -> None:
        done, ran = self.check()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(ran, list(CHECKS))
        self.assertEqual([line.split()[0] for line in done.stdout.splitlines()], ["PASS"] * len(CHECKS))

    def test_one_failed_check_returns_one_names_it_and_the_later_checks_still_run(self) -> None:
        done, ran = self.check(failing="tools.face_check")
        self.assertEqual(done.returncode, 1)
        self.assertEqual(ran, list(CHECKS))
        self.assertEqual([line.split()[1] for line in done.stdout.splitlines() if line.startswith("FAIL")], ["tools.face_check"])

    def test_without_a_build_it_returns_two_and_runs_nothing(self) -> None:
        done, ran = self.check(built=False)
        self.assertEqual(done.returncode, 2)
        self.assertEqual(ran, [])
        self.assertIn("cad/build.sh", done.stderr)
