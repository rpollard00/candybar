"""Write a FreeCAD document of the built solids, with their colours, for a person to open.

    CANDYBAR_OUT=cad/out/shell-rev7 cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc

Reads manifest.json and the BREP files that candybar.shell.solids wrote into the output directory, and writes
shell.FCStd beside them. It needs the GUI binary: a document saved headless opens with every solid hidden.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import FreeCAD as App
import Part

NAMED = {"white": (0.93, 0.93, 0.91), "black": (0.12, 0.12, 0.12)}
DOCUMENT = "shell.FCStd"


def colour(finish: str) -> tuple[float, float, float]:
    if finish in NAMED:
        return NAMED[finish]
    value = finish.lstrip("#")
    return tuple(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))


def main() -> int:
    # This switches off backup files and thumbnails in FreeCAD's user settings, so it refuses to run outside the
    # throwaway user directory that freecad-run.sh provides.
    throwaway = os.environ.get("CANDYBAR_THROWAWAY_HOME")
    if not throwaway or Path(App.getUserAppDataDir()).resolve() != Path(throwaway).resolve():
        raise RuntimeError("viewdoc changes FreeCAD's user settings: run it with freecad-run.sh, in a throwaway user directory")
    if not App.GuiUp:
        raise RuntimeError("view settings need FreeCAD's GUI binary: run this step with freecad-run.sh --gui")
    out = Path(os.environ["CANDYBAR_OUT"])
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    settings = App.ParamGet("User parameter:BaseApp/Preferences/Document")
    settings.SetBool("CreateBackupFiles", False)
    settings.SetBool("SaveThumbnail", False)
    doc = App.newDocument("Shell")
    for name, part in manifest.items():
        shape = Part.Shape()
        shape.read(str(out / part["brep"]))
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        obj.ViewObject.ShapeColor = colour(part["finish"])
        obj.ViewObject.Visibility = True
    doc.recompute()
    doc.saveAs(str(out / DOCUMENT))
    print(f"wrote {out / DOCUMENT}: {len(manifest)} solids")
    return 0
