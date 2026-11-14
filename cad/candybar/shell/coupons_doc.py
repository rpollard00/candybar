"""Write shell.FCStd of the coupon set: every part in its place on its plate, a group for each plate, and the outline
of the usable bed.

    CANDYBAR_OUT=cad/out/coupons cad/candybar/freecad-run.sh --gui candybar.shell.coupons_doc

Reads coupons.json, manifest.json and layout/ that candybar.shell.coupons wrote. It needs the GUI binary: a document
saved headless opens with every solid hidden.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import FreeCAD as App
import Part

from .viewdoc import DOCUMENT, colour


def main() -> int:
    if not App.GuiUp:
        print("view settings need FreeCAD's GUI binary: run this with freecad-run.sh --gui")
        return 1
    out = Path(os.environ["CANDYBAR_OUT"])
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    plates = json.loads((out / "coupons.json").read_text(encoding="utf-8"))["plates"]
    settings = App.ParamGet("User parameter:BaseApp/Preferences/Document")
    settings.SetBool("CreateBackupFiles", False)
    settings.SetBool("SaveThumbnail", False)
    doc = App.newDocument("Coupons")
    count = 0
    for p in plates:
        group = doc.addObject("App::DocumentObjectGroup", f"Plate_{p['plate']}")
        group.Label = f"Plate {p['plate']}: {p['title']}"
        bed = Part.Shape()
        bed.read(str(out / "layout" / f"plate-{p['plate']}.brep"))
        obj = doc.addObject("Part::Feature", f"Bed_{p['plate']}")
        obj.Shape = bed
        obj.ViewObject.LineColor = (0.5, 0.5, 0.5)
        group.addObject(obj)
        for name, part in manifest.items():
            if not name.startswith(f"p{p['plate']}_"):
                continue
            shape = Part.Shape()
            shape.read(str(out / part["brep"]))
            obj = doc.addObject("Part::Feature", name)
            obj.Label = name.split("_", 1)[1].replace("_", "-")
            obj.Shape = shape
            obj.ViewObject.ShapeColor = colour(part["finish"])
            obj.ViewObject.Visibility = True
            group.addObject(obj)
            count += 1
    doc.recompute()
    doc.saveAs(str(out / DOCUMENT))
    print(f"wrote {out / DOCUMENT}: {count} solids on {len(plates)} plates")
    return 0
