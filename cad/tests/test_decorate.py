"""The view step refuses to change FreeCAD user settings that are not its own, or the model."""
from __future__ import annotations

import os
import shutil
import unittest
from pathlib import Path
from unittest import mock

import FreeCAD as App

from candybar import decorate, params, style

from . import support


class SettingsGuardTest(unittest.TestCase):
    def saved(self) -> Path:
        out, _ = support.baseline()
        return out / "candybar.FCStd"

    def test_refuses_without_a_throwaway_user_directory(self) -> None:
        environment = {key: text for key, text in os.environ.items() if key != "CANDYBAR_THROWAWAY_HOME"}
        with mock.patch.dict(os.environ, environment, clear=True):
            with self.assertRaisesRegex(RuntimeError, "throwaway user directory"):
                decorate.decorate(self.saved())

    def test_refuses_when_freecad_uses_another_user_directory(self) -> None:
        with mock.patch.dict(os.environ, {"CANDYBAR_THROWAWAY_HOME": str(support.temp_dir())}):
            with self.assertRaisesRegex(RuntimeError, "throwaway user directory"):
                decorate.decorate(self.saved())

    def test_inside_the_throwaway_directory_it_goes_on_to_ask_for_the_gui(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "GUI binary"):
            decorate.decorate(self.saved())


class GeometryGuardTest(unittest.TestCase):
    def test_refuses_to_save_when_styling_changes_the_model(self) -> None:
        out, _ = support.baseline()
        saved = support.temp_dir() / "candybar.FCStd"
        shutil.copy(out / "candybar.FCStd", saved)
        before = saved.read_bytes()

        def spoil(doc: App.Document) -> None:
            support.edit(doc, mon_h=params.value(doc, "mon_h") - 30)

        with mock.patch.object(App, "GuiUp", 1), mock.patch.object(style, "apply", spoil), mock.patch.object(style, "frame"):
            with self.assertRaisesRegex(RuntimeError, "changed the model"):
                decorate.decorate(saved)
        self.assertEqual(saved.read_bytes(), before)
