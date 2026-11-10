from __future__ import annotations

from pathlib import Path
from typing import Sequence

import FreeCAD as App
import Import
import MeshPart

from . import model

LAYOUT_STEP = "candybar.step"
OUTPUTS = ("step", "stl", LAYOUT_STEP)
STL_LINEAR_DEFLECTION = 0.05
STL_ANGULAR_DEFLECTION = 0.26


def write(doc: App.Document, out_dir: Path) -> None:
    solids = model.placed(doc)
    step_dir, stl_dir = out_dir / "step", out_dir / "stl"
    step_dir.mkdir()
    stl_dir.mkdir()
    for part in solids:
        if part.role == "printable":
            part.own.exportStep(str(step_dir / f"{part.name}.step"))
            mesh = MeshPart.meshFromShape(
                Shape=part.own, LinearDeflection=STL_LINEAR_DEFLECTION, AngularDeflection=STL_ANGULAR_DEFLECTION, Relative=False
            )
            mesh.write(str(stl_dir / f"{part.name}.stl"))
    _write_layout([solid for solid in solids if solid.role != "keepout"], out_dir / LAYOUT_STEP)


def _write_layout(solids: Sequence[model.Placed], path: Path) -> None:
    scratch = App.newDocument("candybar_layout", hidden=True)
    try:
        features = []
        for solid in solids:
            feature = scratch.addObject("Part::Feature", solid.name)
            feature.Shape = solid.world
            features.append(feature)
        Import.export(features, str(path))
    finally:
        App.closeDocument(scratch.Name)
