"""The scenes of the sheet for the push rod's mark (docs/design/monitor-cradle-and-bezel.md): the front of the cabinet
with the printed bezel plate, without the rod and with it, from one camera about 1 m in front of the screen, and a
close view of the right bar with a ruler of 1 mm ticks beside the mark. Every face edge is drawn on the renders.

    CANDYBAR_OUT=cad/out/push-rod-mark cad/candybar/freecad-run.sh candybar.shell.rod_mark
    cad/.venv-tools/bin/python cad/tools/draw_push_rod.py cad/out/push-rod-mark
"""
from __future__ import annotations

import json
import os

import MeshPart
import Part

from . import cradle as cr
from . import solids as so
from .dims import Blueprint

FOV_HALF_TAN = 0.30573   # tan(17 degrees): half the field of view of the close-up cameras of tools/render_views.py


def main() -> int:
    root = os.environ.get("CANDYBAR_OUT", "cad/out/push-rod-mark")
    d, c, u = Blueprint(), cr.Cradle(), cr.PRESENT
    f = cr.Frame(d)
    shell = cr.shell_parts()
    fin = json.load(open(os.path.join(str(cr.shell_dir()), "manifest.json")))
    plate = cr.bezel_plate(d, c)
    option = cr.button_option(d, c, u, plate)
    x_btn, v = cr.sockets(d, c, u)["power button"]
    line = Part.makeLine(f.pt(c.rod_x, v, -40.0), f.pt(c.rod_x, v, f.t0)).common(plate)
    front = min(f.local(p.Point)[2] for e in line.Edges for p in e.Vertexes)
    # the ruler: 20 mm with a tick each mm, longer each 5 mm, 8 below the mark, lying on the face of the bar
    vr = v - 8.0
    fronts = []
    for dx in range(-11, 12):
        lr = Part.makeLine(f.pt(c.rod_x + dx, vr, -40.0), f.pt(c.rod_x + dx, vr, f.t0)).common(plate)
        fronts.append(min(f.local(p.Point)[2] for e in lr.Edges for p in e.Vertexes))
    fr = min(fronts)   # the most forward point of the face along the ruler: the ruler lies on it and floats over the rest
    bits = [f.box((c.rod_x - 10.0, c.rod_x + 10.0), (vr - 0.2, vr + 0.2), (fr - 0.3, fr + 0.05))]
    for k in range(21):
        h = 3.0 if k % 5 == 0 else 1.6
        x = c.rod_x - 10.0 + k
        bits.append(f.box((x - 0.12, x + 0.12), (vr, vr + h), (fr - 0.3, fr + 0.05)))
    ruler = bits[0].fuse(bits[1:]).removeSplitter()
    base = {k: (s, fin[k]["finish"]) for k, s in shell.items() if k not in ("bezel",)}
    scenes = {"without-rod": {**base, "bezel_plate": (plate, "black")},
              "with-rod": {**base, "bezel_plate": (option["bezel_plate_button"], "black"), "button_rod": (option["button_rod"], "black")},
              "closeup": {"bezel_plate": (option["bezel_plate_button"], "black"), "button_rod": (option["button_rod"], "black"),
                          "ruler": (ruler, "white"), "body": (shell["body"], fin["body"]["finish"])}}
    tc = f.pt(0.0, 0.0, front)
    tm = f.pt(c.rod_x, v - 3.0, front)
    cams = {"without-rod": {"front-1m": {"target": [tc.x, tc.y, tc.z + 40.0], "radius": 300.0, "az": 0.0, "el": 20.0, "aspect": 1.15}},
            "with-rod": {"front-1m": {"target": [tc.x, tc.y, tc.z + 40.0], "radius": 300.0, "az": 0.0, "el": 20.0, "aspect": 1.15}},
            "closeup": {"mark": {"target": [tm.x, tm.y, tm.z], "radius": 16.0, "az": 0.0, "el": 30.0, "aspect": 0.8}}}
    for name, parts in scenes.items():
        folder = os.path.join(root, "scenes", name)
        os.makedirs(folder, exist_ok=True)
        manifest, edges = {}, {}
        for k, (s, finish) in parts.items():
            if name == "closeup" and k == "body":
                s = s.common(f.box((150.0, 240.0), (v - 40.0, v + 40.0), (-30.0, 20.0)))
            MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.1, Relative=False).write(os.path.join(folder, f"{k}.stl"))
            manifest[k] = {"file": f"{k}.stl", "finish": finish}
            edges[k] = so.edge_polylines(s)
        json.dump(manifest, open(os.path.join(folder, "manifest.json"), "w"), indent=1)
        json.dump(edges, open(os.path.join(folder, "edges.json"), "w"))
        json.dump(cams[name], open(os.path.join(folder, "focus.json"), "w"), indent=1)
    d_cam = 300.0 / FOV_HALF_TAN
    json.dump({"mark_mm": round(c.rod + 2 * c.rod_fit, 2), "rod_mm": c.rod, "rod_proud": c.rod_proud, "rod_x": c.rod_x, "v": round(v, 2),
               "front_camera_distance_mm": round(d_cam), "front_view_width_mm": 600.0}, open(os.path.join(root, "scene.json"), "w"), indent=1)
    return 0
