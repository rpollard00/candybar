"""The view step refuses to change FreeCAD user settings that are not its own to change."""
from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock

from candybar import decorate

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
