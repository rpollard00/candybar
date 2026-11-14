"""Run under the GUI binary by test_outputs: what a person sees when shell.FCStd opens, as JSON."""
from __future__ import annotations

import json
import os
from pathlib import Path

import FreeCAD as App

from candybar.shell import viewdoc


def main() -> int:
    out = Path(os.environ["CANDYBAR_OUT"])
    doc = App.openDocument(str(out / viewdoc.DOCUMENT))
    look = {obj.Name: {"shown": bool(obj.ViewObject.Visibility), "colour": [round(c, 3) for c in obj.ViewObject.ShapeColor[:3]],
                       "volume": obj.Shape.Volume} for obj in doc.Objects}
    (out / "look.json").write_text(json.dumps({"gui": bool(App.GuiUp), "objects": look}), encoding="utf-8")
    App.closeDocument(doc.Name)
    return 0
