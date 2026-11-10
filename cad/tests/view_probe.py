from __future__ import annotations

import json
import os
from pathlib import Path

import FreeCAD as App

from candybar import style


def main() -> int:
    doc = App.openDocument(os.environ["CANDYBAR_PROBE_FILE"])
    view = App.Gui.getDocument(doc.Name).ActiveView
    look = {
        "gui_up": bool(App.GuiUp),
        "objects": {obj.Name: _look(obj) for obj in doc.Objects},
        "tips": {obj.Name: obj.Tip.Name for obj in doc.Objects if obj.isDerivedFrom("PartDesign::Body")},
        "view_direction": list(view.getViewDirection()),
        "touched": [obj.Name for obj in doc.Objects if "Touched" in obj.State],
    }
    style.see_through(doc)
    look["seen_through"] = {obj.Name: _look(obj)["transparency"] for obj in doc.Objects if getattr(obj, "CB_Role", "")}
    style.see_through(doc, False)
    look["opaque_again"] = {obj.Name: _look(obj)["transparency"] for obj in doc.Objects if getattr(obj, "CB_Role", "")}
    Path(os.environ["CANDYBAR_PROBE_JSON"]).write_text(json.dumps(look), encoding="utf-8")
    return 0


def _look(obj: App.DocumentObject) -> dict[str, object]:
    view = obj.ViewObject
    colour = list(view.ShapeColor[:3]) if hasattr(view, "ShapeColor") else None
    return {
        "visible": bool(view.Visibility),
        "role": getattr(obj, "CB_Role", ""),
        "alternate": getattr(obj, "CB_Alternate", False),
        "colour": colour,
        "transparency": getattr(view, "Transparency", None),
    }
