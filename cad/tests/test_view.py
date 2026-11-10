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
        shown = ("Monitor", "Monitor_Body", "Shell_Skin", "Hood_Marquee", "Deck_Lever", look()["tips"]["Deck_Lever"])
        for name in shown:
            self.assertTrue(self.visible(name), name)

    def test_every_tagged_solid_is_shown_unless_it_is_a_keepout_or_an_alternate(self) -> None:
        tagged = {name: seen for name, seen in look()["objects"].items() if seen["role"]}
        self.assertGreater(len(tagged), 50)
        wrong = [
            name
            for name, seen in tagged.items()
            if seen["visible"] != (seen["role"] != "keepout" and not seen["alternate"])
        ]
        self.assertEqual(wrong, [])

    def test_one_bezel_plate_is_shown_and_its_alternates_are_hidden(self) -> None:
        self.assertTrue(self.visible("Bezel_16x9"))
        for name in ("Bezel_16x10", "Bezel_4x3", "Bezel_Tate"):
            self.assertFalse(self.visible(name), name)

    def test_keepouts_sketches_earlier_features_origins_and_tools_are_hidden(self) -> None:
        hidden = ("PSU_FanAir", "Shell_SideProfile", "Shell_Envelope", "Deck_Lever_Plate", "Deck_Lever_HoleSketch", "XY_Plane")
        for name in (*hidden, "Bezel_16x9_Window"):
            self.assertFalse(self.visible(name), name)

    def test_solids_carry_the_colour_of_their_role(self) -> None:
        samples = (
            ("Monitor_Body", "hardware"),
            ("Shell_Skin", "massing"),
            ("Bezel_16x9", "trim"),
            ("Hood_SpeakerL", "trim"),
            (look()["tips"]["Deck_Lever"], "printable"),
        )
        for name, role in samples:
            seen, style = look()["objects"][name], ROLE_STYLES[role]
            for channel, expected in zip(seen["colour"], style.shape_colour, strict=True):
                self.assertAlmostEqual(channel, expected, places=3, msg=name)
            self.assertEqual(seen["transparency"], style.transparency, name)

    def test_shell_is_opaque_until_asked_to_be_seen_through(self) -> None:
        self.assertEqual(look()["objects"]["Shell_Skin"]["transparency"], 0)
        through, again = look()["seen_through"], look()["opaque_again"]
        for name in ("Shell_Skin", "Bezel_16x9", "Hood_Marquee"):
            self.assertGreater(through[name], 50, name)
            self.assertEqual(again[name], 0, name)
        self.assertEqual(through["Monitor_Body"], 0)

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
