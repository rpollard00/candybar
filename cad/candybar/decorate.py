"""The view step of the build: store view settings in the saved document.

A document saved headless has none, and FreeCAD's GUI then opens it with every
solid hidden.
"""
from __future__ import annotations

import os
from pathlib import Path

import FreeCAD as App

from . import model, style
from .build import SAVED


def decorate(path: Path) -> None:
    """Apply the role styles and the opening view to a saved document, and save it in place.

    The geometry must come out as it went in, or the check report would no
    longer describe the saved file. If it does not, the file is left unsaved.

    This switches off backup files and thumbnails in FreeCAD's user settings,
    so it belongs in the throwaway user directory that freecad-run.sh provides.
    """
    if not App.GuiUp:
        raise RuntimeError("view settings need FreeCAD's GUI binary: run this step with freecad-run.sh --gui")
    settings = App.ParamGet("User parameter:BaseApp/Preferences/Document")
    settings.SetBool("CreateBackupFiles", False)
    # The offscreen platform cannot draw, so the thumbnail would be FreeCAD's icon instead of the layout.
    settings.SetBool("SaveThumbnail", False)
    doc = App.openDocument(str(path))
    try:
        before = model.fingerprint(doc)
        style.apply(doc)
        style.frame(doc)
        touched = [obj.Name for obj in doc.Objects if "Touched" in obj.State]
        if touched or model.fingerprint(doc) != before:
            raise RuntimeError(f"the view step changed the model (touched: {touched}); {path} keeps no view settings")
        doc.save()
    finally:
        App.closeDocument(doc.Name)


def main() -> int:
    decorate(Path(os.environ["CANDYBAR_OUT"]) / SAVED)
    return 0
