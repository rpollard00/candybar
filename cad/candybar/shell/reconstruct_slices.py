"""Slice the meshes of a model directory (manifest.json of render_views.py) with named planes, for the reconstruction.

Runs under freecadcmd through cad/candybar/freecad-run.sh. Each plane is "name:axis:offset" (axis x, y or z;
offset in mm in the project frame). Writes one JSON: {"planes": {name: [axis, offset]}, "parts": {part: {name:
[polyline, ...]}}}, every polyline a list of [x, y, z]. The slices are exact for the mesh. Example:
    RECON_MODEL=cad/vendor/mini-new-astro-city/assembled RECON_OUT=cad/out/shell-d/reconstruction/slices-k.json \
    RECON_PLANES="centre:x:0.3,cheek:x:122,screen:z:155.5" CANDYBAR_OUT=cad/out/shell-d \
    cad/candybar/freecad-run.sh candybar.shell.reconstruct_slices
"""
from __future__ import annotations

import json
import os

import FreeCAD
import Mesh

AXES = {"x": (1.0, 0.0, 0.0), "y": (0.0, 1.0, 0.0), "z": (0.0, 0.0, 1.0)}


def main() -> int:
    model = os.environ["RECON_MODEL"]
    planes = {}
    for spec in os.environ["RECON_PLANES"].split(","):
        name, axis, offset = spec.split(":")
        planes[name] = (axis, float(offset))
    manifest = json.load(open(os.path.join(model, "manifest.json")))
    parts: dict[str, dict[str, list]] = {}
    for part, entry in manifest.items():
        mesh = Mesh.Mesh(os.path.join(model, entry["file"]))
        cuts = {}
        for name, (axis, offset) in planes.items():
            n = FreeCAD.Vector(*AXES[axis])
            loops = mesh.crossSections([(n * offset, n)], 0.01)[0]
            cuts[name] = [[[round(p.x, 3), round(p.y, 3), round(p.z, 3)] for p in loop] for loop in loops if len(loop) > 1]
        parts[part] = cuts
    out = os.environ["RECON_OUT"]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"model": model, "planes": planes, "parts": parts}, open(out, "w"))
    print("reconstruct_slices:", out, {k: sum(len(v) for v in c.values()) for k, c in parts.items()})
    return 0
