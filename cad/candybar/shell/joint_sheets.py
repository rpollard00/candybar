"""The scenes of the sheet of the second pass on the joints of the print pieces (docs/design/print-pieces.md): the
closing gap of the brow at W1 and of upper rear R at R5 and R3, and the top ring of the body with the foot of the hood
(joint 7) in a section through a cone. Every face edge is drawn on the renders.

    CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh candybar.shell.joint_sheets
    cad/.venv-tools/bin/python cad/tools/draw_joint_sheets.py cad/out/pieces

It reads the pieces from the build folder (candybar.shell.pieces) and writes <out>/joints-2/scenes.
"""
from __future__ import annotations

import json
import os

import FreeCAD
import MeshPart
import Part

from . import solids as so

V = FreeCAD.Vector


def main() -> int:
    root = os.path.abspath(os.environ.get("CANDYBAR_OUT", "cad/out/pieces"))
    OUT = os.path.join(root, "joints-2", "scenes")

    def load(n):
        s = Part.Shape()
        s.read(os.path.join(root, f"{n.replace(' ', '_')}.brep"))
        return s
    def scene(name, items, cams, keep=None):
        folder = os.path.join(OUT, name); os.makedirs(folder, exist_ok=True)
        man, edges = {}, {}
        for k, s, fin in items:
            if keep is not None:
                s = s.common(keep)
            if not s.Faces: continue
            MeshPart.meshFromShape(Shape=s, LinearDeflection=0.08, AngularDeflection=0.12, Relative=False).write(f"{folder}/{k}.stl")
            man[k] = {"file": f"{k}.stl", "finish": fin}; edges[k] = so.edge_polylines(s)
        json.dump(man, open(f"{folder}/manifest.json", "w")); json.dump(edges, open(f"{folder}/edges.json", "w"))
        json.dump(cams, open(f"{folder}/focus.json", "w"))
    cam = lambda t, r, az, el: {"target": list(t), "radius": r, "az": az, "el": el, "aspect": 0.8}
    box = lambda x0, x1, y0, y1, z0, z1: Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
    W, B, G, P = "white", "#e8c39e", "#9ec3e8", "#c8e89e"
    # 1: the brow between the two upper pieces at W1 R (x 106), from above and from inside
    scene("w1", [("brow", load("brow"), W), ("upper_R", load("upper R"), B)], {"w1-inside": cam((106.0, 430.0, 400.0), 30.0, 200.0, 35.0)},
          keep=box(60, 160, 380, 480, 330, 430))
    # 2: upper rear R between upper rear L (R5, x 0) and upper R (R3, x 211.4)
    scene("r5r3", [("upper_rear_R", load("upper rear R"), W), ("upper_rear_L", load("upper rear L"), G), ("upper_R", load("upper R"), B)],
          {"r5-inside": cam((0.0, 560.0, 423.0), 10.0, 180.0, 75.0), "r3-inside": cam((211.4, 560.0, 423.0), 10.0, 180.0, 75.0)},
          keep=box(-60, 260, 500, 600, 280, 430))
    # 3: the ring and the foot in a section at x 150 (through a cone), the left part of the cabinet off
    cut = box(150.0, 300.0, 300.0, 650.0, 380.0, 470.0)
    scene("ring", [("upper_R", load("upper R"), B), ("upper_rear_R", load("upper rear R"), W), ("hood_side_R", load("hood side R"), P), ("brow", load("brow"), W)],
          {"ring-front-cone": cam((150.0, 451.0, 425.0), 22.0, 270.0, 10.0), "ring-rear-cone": cam((150.0, 566.0, 425.0), 22.0, 270.0, 10.0),
           "ring-along": cam((150.0, 510.0, 425.0), 90.0, 240.0, 25.0)}, keep=cut)
    return 0
