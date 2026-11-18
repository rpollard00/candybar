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
    hood_screw_scenes(root, load, scene, cam, box)
    return 0


def hood_screw_scenes(root, load, scene, cam, box) -> None:
    """The bolted hood (2026-11-16): the right side of the cabinet cut open just inside its wall, the rear door off,
    with the two screws of that side and a hex key of 3 in each; and a section through the front screw."""
    from . import pieces as pc
    from .joints import OTHER_JOINTS as oj

    seams = json.load(open(os.path.join(root, "seams.json")))
    right = [r for r in seams.get("hood_screws", []) if r["at"][0] > 0]
    if not right:
        return
    x = right[0]["at"][0]
    wall = x + oj.ring_w / 2 - 0.1     # just inside the inner face of the side wall
    names = ("upper R", "middle R", "lower R", "upper rear R", "rear lower R", "brow", "hood side R", "hood centre", "apron", "deck side R")
    shown = [(n.replace(" ", "_"), load(n), "#e8c39e" if n.startswith("hood") else "white") for n in names
             if os.path.exists(os.path.join(root, f"{n.replace(' ', '_')}.brep"))]
    hw, hd = oj.hood_screw_head
    tools = []
    for k, r in enumerate(right):
        sx, sy, seat = r["at"]
        screw = Part.makeCylinder(hw / 2, hd, V(sx, sy, seat - hd), V(0, 0, 1)).fuse(Part.makeCylinder(2.0, oj.hood_screw_l, V(sx, sy, seat), V(0, 0, 1)))
        key = Part.makeCylinder(1.5, pc.HOOD_KEY, V(sx, sy, seat - hd - pc.HOOD_KEY), V(0, 0, 1))
        tools += [(f"screw_{k}", screw, "#b8bcc4"), (f"key_{k}", key, "#d02020")]
    items = [(n, s_) for n, role, s_ in pc.hardware() if role == "hardware" and n.startswith(("Monitor_", "Compute", "PSU"))]
    hard = [(f"hw_{k}", Part.makeCompound([s_ for n, s_ in items if n.startswith(pre)]), "#6a8fd0")
            for k, pre in enumerate(("Monitor_", "Compute", "PSU")) if any(n.startswith(pre) for n, _ in items)]
    keep = box(-400.0, wall, -100.0, 700.0, 0.0, 700.0)
    mid = (wall, 500.0, 330.0)
    scene("hood-reach", shown + hard + tools, {"reach": cam(mid, 330.0, 90.0, 8.0), "reach-close": cam((wall, 505.0, 380.0), 120.0, 90.0, 12.0)}, keep=keep)
    sx, sy, seat = right[0]["at"]
    cut = box(sx, sx + 40.0, sy - 40.0, sy + 40.0, seat - 60.0, seat + 40.0)
    scene("hood-screw", [(n, sh, f) for n, sh, f in shown if n in ("upper_R", "hood_side_R")] + tools[:2], {"screw": cam((sx, sy, seat + 8.0), 46.0, 270.0, 5.0)}, keep=cut)
