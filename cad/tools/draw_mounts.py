"""Render the sheets of the hardware mounts, with every BREP edge drawn.

candybar.shell.mounts writes one model directory for each sheet into <out>/scenes (meshes, manifest.json, edges.json
and focus.json with the cameras). This tool renders each camera with tools/render_views.py into <out>/sheets:

    cad/.venv-tools/bin/python cad/tools/draw_mounts.py cad/out/mounts

It needs Blender (the `blender` command). It exits 1 when a view is missing.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE = 2000


def main(argv: list[str]) -> int:
    out = os.path.abspath(argv[1] if len(argv) > 1 else "cad/out/mounts")
    scenes, sheets = os.path.join(out, "scenes"), os.path.join(out, "sheets")
    os.makedirs(sheets, exist_ok=True)
    missing = []
    for name in sorted(os.listdir(scenes)):
        folder = os.path.join(scenes, name)
        views = list(json.load(open(os.path.join(folder, "focus.json"))))
        work = os.path.join(out, "renders", name)
        done = subprocess.run([sys.executable, os.path.join(HERE, "render_views.py"), work, folder, "--views", ",".join(views), "--size", str(SIZE)])
        for view in views:
            png = os.path.join(work, view + ".png")
            if done.returncode or not os.path.exists(png):
                missing.append(view)
            else:
                shutil.copy(png, os.path.join(sheets, view + ".png"))
    print(f"draw_mounts: {len(os.listdir(sheets))} sheets in {sheets}" + (f"; missing: {', '.join(missing)}" if missing else ""))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
