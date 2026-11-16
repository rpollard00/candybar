"""Write a FreeCAD document of the monitor cradle and the bezel plate in place in the body, for a person to open.

    CANDYBAR_OUT=cad/out/cradle cad/candybar/freecad-run.sh --gui candybar.shell.cradle_view

Reads manifest.json and the BREP files that candybar.shell.cradle wrote into the output directory, and the parts of
the built shell (cradle.shell_dir). It writes shell.FCStd into the output directory. It needs the GUI binary: a
document saved headless opens with every solid hidden.

Groups of the document:
  Bezel plate    the printed plate in place, and its two halves (hidden)
  Cradle         the uprights, the jaws, the shoes and the cable channels
  On the body    the lugs and the bosses (added solids), and the skin round the screen face
  Hardware       the monitor, its plug room, the pads, the pins, the magnets and the screws
  Option         the power-button option: the plate with the hole, the push rod, the striker and the guide; on show
                 in place of the plain plate when Cradle.push_rod is set (the default since 2026-11-15)
  Shell          the outer parts of the built shell; the body and the nominal plate are hidden, because the body is a
                 solid form and hides what is inside
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import FreeCAD as App
import Part

from . import cradle
from .viewdoc import colour

DOCUMENT = "shell.FCStd"
GROUPS = {"Bezel plate": ("bezel_plate",), "Cradle": ("upright_right", "upright_left", "jaws", "shoes", "channel_right", "channel_left"),
          "On the body": ("lugs", "bosses", "skin"), "Hardware": cradle.HARDWARE}
HIDDEN = ("body", "bezel", "screen", "bezel_half_right", "bezel_half_left")
CLEAR = {"skin": 55, "plugs": 70}


def main() -> int:
    if not App.GuiUp:
        print("view settings need FreeCAD's GUI binary: run this with freecad-run.sh --gui")
        return 1
    out = Path(os.environ.get("CANDYBAR_OUT") or cradle.CAD / "out" / "cradle")
    settings = App.ParamGet("User parameter:BaseApp/Preferences/Document")
    settings.SetBool("CreateBackupFiles", False)
    settings.SetBool("SaveThumbnail", False)
    doc = App.newDocument("Cradle")

    def add(group, name: str, path: Path, finish: str) -> None:
        shape = Part.Shape()
        shape.read(str(path))
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        group.addObject(obj)
        obj.ViewObject.ShapeColor = colour(finish)
        obj.ViewObject.Visibility = name not in HIDDEN
        obj.ViewObject.Transparency = CLEAR.get(name, 0)

    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    count = 0
    for title, names in GROUPS.items():
        group = doc.addObject("App::DocumentObjectGroup", title.replace(" ", "_"))
        group.Label = title
        for name in names:
            add(group, name, out / manifest[name]["brep"], manifest[name]["finish"])
            count += 1
        if title == "Bezel plate":
            halves = json.loads((out / "print" / "manifest.json").read_text(encoding="utf-8"))
            for name in ("bezel_half_right", "bezel_half_left"):
                add(group, name, out / "print" / halves[name]["brep"], halves[name]["finish"])
                count += 1
    option = json.loads((out / "options" / "button" / "manifest.json").read_text(encoding="utf-8"))
    group = doc.addObject("App::DocumentObjectGroup", "Option_power_button")
    on = cradle.Cradle().push_rod
    group.Label = "Option: power button" + ("" if on else " (hidden)")
    for name, part in option.items():
        add(group, name, out / "options" / "button" / part["brep"], part["finish"])
        doc.getObject(name).ViewObject.Visibility = on
        count += 1
    if on:  # the plate with the hole for the rod in place of the plain plate
        doc.getObject("bezel_plate").ViewObject.Visibility = False
    shell = cradle.shell_dir()
    group = doc.addObject("App::DocumentObjectGroup", "Shell")
    for name, part in json.loads((shell / "manifest.json").read_text(encoding="utf-8")).items():
        add(group, name, shell / part["brep"], part["finish"])
        count += 1
    doc.recompute()
    doc.saveAs(str(out / DOCUMENT))
    print(f"wrote {out / DOCUMENT}: {count} solids")
    return 0
