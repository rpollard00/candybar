from __future__ import annotations

import functools
import json
import os
import subprocess
import unittest
import zipfile

import FreeCAD as App

from candybar import build, model
from candybar.style import ROLE_STYLES

from . import support


@functools.cache
def look() -> dict:
    _, out = support.shell_baseline()
    report = out / "view-probe.json"
    env = os.environ | {
        "CANDYBAR_OUT": str(out),
        "CANDYBAR_PROBE_FILE": str(out / build.SAVED),
        "CANDYBAR_PROBE_JSON": str(report),
    }
    done = subprocess.run([str(support.FREECAD_RUN), "--gui", "tests.view_probe"], env=env, capture_output=True, text=True)
    if done.returncode != 0:
        raise AssertionError(f"the offscreen GUI process could not open the document:\n{done.stderr}")
    return json.loads(report.read_text(encoding="utf-8"))


class SavedViewTest(unittest.TestCase):
    def visible(self, name: str) -> bool:
        return look()["objects"][name]["visible"]

    def test_saved_file_carries_view_settings(self) -> None:
        _, out = support.shell_baseline()
        self.assertIn("GuiDocument.xml", zipfile.ZipFile(out / build.SAVED).namelist())

    def test_probe_runs_with_view_providers(self) -> None:
        self.assertTrue(look()["gui_up"])

    def test_assemblies_solids_and_body_tips_are_shown(self) -> None:
        for name in ("Monitor", "Monitor_Body", "Shell_Floor", "Deck_Lever", look()["tips"]["Deck_Lever"]):
            self.assertTrue(self.visible(name), name)

    def test_every_tagged_solid_is_shown_unless_it_is_a_keepout(self) -> None:
        tagged = {name: seen for name, seen in look()["objects"].items() if seen["role"]}
        self.assertGreater(len(tagged), 50)
        wrong = [name for name, seen in tagged.items() if seen["visible"] != (seen["role"] != "keepout")]
        self.assertEqual(wrong, [])

    def test_keepouts_sketches_earlier_features_origins_and_tools_are_hidden(self) -> None:
        hidden = ("PSU_FanAir", "Shell_Profile", "Deck_Lever_Plate", "Deck_Lever_HoleSketch", "XY_Plane", "Shell_Bezel_Window")
        for name in hidden:
            self.assertFalse(self.visible(name), name)

    def test_solids_carry_the_colour_of_their_role(self) -> None:
        for name, role in (("Monitor_Body", "hardware"), ("Shell_Floor", "massing"), (look()["tips"]["Deck_Lever"], "printable")):
            seen, style = look()["objects"][name], ROLE_STYLES[role]
            for channel, expected in zip(seen["colour"], style.shape_colour, strict=True):
                self.assertAlmostEqual(channel, expected, places=3, msg=name)
            self.assertEqual(seen["transparency"], style.transparency, name)

    def test_document_opens_on_the_isometric_view(self) -> None:
        for component, expected in zip(look()["view_direction"], (-0.57735, 0.57735, -0.57735), strict=True):
            self.assertAlmostEqual(component, expected, places=3)

    def test_nothing_is_left_to_recompute(self) -> None:
        self.assertEqual(look()["touched"], [])

    def test_view_step_leaves_the_geometry_the_checker_saw(self) -> None:
        _, out = support.shell_baseline()
        with support.saved_document() as headless:
            checked = model.fingerprint(headless)
        decorated = App.openDocument(str(out / build.SAVED))
        self.addCleanup(App.closeDocument, decorated.Name)
        self.assertEqual(model.fingerprint(decorated), checked)
