"""Renders of the default build of the shell with every BREP edge drawn, and a sheet that puts it beside another build.

The model is the output of candybar.shell.solids (cad/out/shell-rev7: the meshes, manifest.json, focus.json with the
close-up cameras, and edges.json, see render_views.py). Steps:

    cad/.venv-tools/bin/python cad/tools/draw_shell.py render
        -> cad/out/shell-rev7/renders/<view>.png: the views of VIEWS and the close-ups of CLOSE
    cad/.venv-tools/bin/python cad/tools/draw_shell.py compare OTHER LABEL OUT.png
        -> OUT.png: OTHER (a directory with meshes, manifest.json and edges.json, for example the approved candidate
           cad/out/shell-bp-rev7/R10) and the default build, one row each, from the same cameras. OTHER is rendered
           into cad/out/_scratch/rev7/compare-renders with the cameras of the default build; its files are not changed.

Blender runs in background mode, one model at a time. Needs numpy and Pillow (cad/.venv-tools); no FreeCAD.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from compose_sheet import font  # noqa: E402

ROOT = os.path.dirname(HERE)
MODEL = os.path.join(ROOT, "out", "shell-rev7")
RENDERS = os.path.join(MODEL, "renders")
SCRATCH = os.path.join(ROOT, "out", "_scratch", "rev7", "compare-renders")
# one frame for every model, so that all renders have one scale: xmin, ymin, zmin, xmax, ymax, zmax
FRAME = "-252,-6,-2,252,586,578"
VIEWS = ("three-quarter-front-left", "three-quarter-rear-right", "rear", "side-right")
CLOSE = ("closeup-rear-corner", "closeup-cut-in-corner", "closeup-hand-hold", "closeup-hood-corner-above", "closeup-hip-top", "closeup-head-foot",
         "closeup-hood-roof-end", "closeup-base-corner")
SHEET = ("three-quarter-front-left", "three-quarter-rear-right", "rear", "side-right", "closeup-rear-corner", "closeup-cut-in-corner",
         "closeup-hand-hold", "closeup-hood-corner-above")
INK, MUTED = (30, 30, 34), (110, 110, 118)


def render(model: str, out: str, views: tuple[str, ...]) -> None:
    script = os.path.join(HERE, "render_views.py")
    subprocess.run([sys.executable, script, out, model, "--views", ",".join(views), f"--frame={FRAME}", "--size", "1100", "--samples", "16"], check=True)


def with_cameras(other: str, name: str) -> str:
    """A model directory for another build with the close-up cameras of the default build: its meshes by absolute
    path, its edges, and the default build's focus.json. The other build's own directory is not written to."""
    src, dst = os.path.abspath(other), os.path.join(SCRATCH, name + "-model")
    os.makedirs(dst, exist_ok=True)
    manifest = json.load(open(os.path.join(src, "manifest.json")))
    for entry in manifest.values():
        entry["file"] = os.path.join(src, entry["file"])
        if "brep" in entry:
            entry["brep"] = os.path.join(src, entry["brep"])
    json.dump(manifest, open(os.path.join(dst, "manifest.json"), "w"), indent=1)
    link = os.path.join(dst, "edges.json")
    if os.path.lexists(link):
        os.remove(link)
    os.symlink(os.path.join(src, "edges.json"), link)
    json.dump(json.load(open(os.path.join(MODEL, "focus.json"))), open(os.path.join(dst, "focus.json"), "w"), indent=1)
    return dst


def tile(folder: str, view: str, w: int) -> Image.Image:
    im = Image.open(os.path.join(folder, f"{view}.png")).convert("RGB")
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def sheet(rows: list[tuple[str, str]], views: tuple[str, ...], title: str, notes: str, out: str, w: int = 380, per_row: int = 4) -> None:
    """A sheet of the views in blocks of per_row columns; in each block one line of pictures for each model."""
    gap, left, top = 10, 190, 90
    blocks = [views[i:i + per_row] for i in range(0, len(views), per_row)]
    lines = textwrap.wrap(notes, int((left + per_row * (w + gap)) / 10.5))
    pictures = [[[tile(folder, v, w) for v in block] for _, folder in rows] for block in blocks]
    height = top + sum(34 + sum(max(im.height for im in line) + gap for line in block) + 14 for block in pictures) + 26 * len(lines) + 30
    page = Image.new("RGB", (left + per_row * (w + gap) + gap, height), (255, 255, 255))
    dr = ImageDraw.Draw(page)
    dr.text((20, 20), title, fill=INK, font=font(32, bold=True))
    y = top
    for block, lines_of_block in zip(blocks, pictures):
        for c, v in enumerate(block):
            dr.text((left + gap + c * (w + gap), y), v, fill=MUTED, font=font(18))
        y += 34
        for (label, _), line in zip(rows, lines_of_block):
            dr.multiline_text((20, y + 10), "\n".join(textwrap.wrap(label, 14)), fill=INK, font=font(20, bold=True), spacing=6)
            for c, im in enumerate(line):
                page.paste(im, (left + gap + c * (w + gap), y))
            y += max(im.height for im in line) + gap
        y += 14
    for text in lines:
        dr.text((20, y), text, fill=INK, font=font(19))
        y += 26
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    page.save(out)
    print("draw_shell:", out)


def compare(other: str, label: str, out: str) -> None:
    name = os.path.basename(os.path.normpath(other))
    there = os.path.join(SCRATCH, name)
    render(with_cameras(other, name), there, SHEET)
    if not all(os.path.exists(os.path.join(RENDERS, f"{v}.png")) for v in SHEET):
        render(MODEL, RENDERS, VIEWS + CLOSE)
    report = json.load(open(os.path.join(MODEL, "report.json")))
    sheet([(label, there), ("Default build (revision 7)", RENDERS)], SHEET, f"{label} and the default build, from the same cameras",
          "All BREP face edges are drawn. Top line of each block: " + label + ". Bottom line: the default build of candybar.shell.solids. "
          + " ".join(line + "." for line in report.get("log", []) if "no edge break" in line), out)


if __name__ == "__main__":
    if sys.argv[1] == "render":
        render(MODEL, RENDERS, VIEWS + CLOSE)
    elif sys.argv[1] == "compare":
        compare(*sys.argv[2:5])
    else:
        raise SystemExit(__doc__)
