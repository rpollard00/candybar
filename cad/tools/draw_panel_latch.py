"""Sheets of the latch study of the control panel, with every BREP edge drawn.

The models are the scene directories that candybar.shell.panel_latch writes into cad/out/panel-latch/<candidate>/scenes
(meshes, manifest.json, edges.json and focus.json with the cameras, see render_views.py). Steps:

    cad/.venv-tools/bin/python cad/tools/draw_panel_latch.py [OUT]            render every scene, then make the sheets
    cad/.venv-tools/bin/python cad/tools/draw_panel_latch.py [OUT] sheets     make the sheets again from the renders

OUT is cad/out/panel-latch. The renders go to OUT/<candidate>/renders/<scene>/<view>.png, the sheets to OUT/sheets.
Blender runs in background mode, one scene at a time. Needs Pillow (cad/.venv-tools); no FreeCAD.
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
INK, MUTED, BAD, GOOD = (30, 30, 34), (110, 110, 118), (170, 40, 40), (30, 110, 50)
CANDIDATES = ("M", "H", "B", "Q")
SCENES = {"top": ("player", "front"), "section-locked": ("section",), "section-released": ("section",),
          "way-1": ("way",), "way-2": ("way",), "way-3": ("way",), "way-4": ("way",), "parts": ("parts",)}


def run(script: str, out: str, scene: str, views: tuple[str, ...], size: int) -> None:
    subprocess.run([sys.executable, script, out, scene, "--views", ",".join(views), "--size", str(size), "--samples", "16"], check=True)


def render(out: str) -> None:
    script = os.path.join(HERE, "render_views.py")
    for c in CANDIDATES:
        for scene, views in SCENES.items():
            src = os.path.join(out, c, "scenes", scene)
            if os.path.isdir(src):
                run(script, os.path.join(out, c, "renders", scene), src, views, 1400)
        src = os.path.join(out, "scenes", f"compare-{c}")
        if os.path.isdir(src):
            run(script, os.path.join(out, "renders", f"compare-{c}"), src, ("player",), 1400)


def picture(path: str, w: int) -> Image.Image:
    im = Image.open(path).convert("RGB")
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def page(out: str, name: str, title: str, cells: list[tuple[str, str]], notes: list[str], w: int = 760, per_row: int = 2, subtitle: str = "") -> None:
    """A sheet: the pictures of `cells` (path, label) in rows of per_row, and the notes below them."""
    gap, top = 16, 96 if subtitle else 70
    pictures = [(picture(p, w), label) for p, label in cells]
    rows = [pictures[k:k + per_row] for k in range(0, len(pictures), per_row)]
    width = gap + per_row * (w + gap)
    wrap = int(width / 11.2)
    lines = []
    for note in notes:
        lines += textwrap.wrap(note, wrap) or [""]
    height = top + sum(34 + max(im.height for im, _ in row) + gap for row in rows) + 27 * len(lines) + 30
    sheet = Image.new("RGB", (width, height), (255, 255, 255))
    dr = ImageDraw.Draw(sheet)
    dr.text((gap, 18), title, fill=INK, font=font(32, bold=True))
    if subtitle:
        dr.text((gap, 58), subtitle, fill=MUTED, font=font(21))
    y = top
    for row in rows:
        for c, (im, label) in enumerate(row):
            dr.text((gap + c * (w + gap), y), label, fill=MUTED, font=font(20))
            sheet.paste(im, (gap + c * (w + gap), y + 32))
        y += 34 + max(im.height for im, _ in row) + gap
    for line in lines:
        dr.text((gap, y), line, fill=INK, font=font(19))
        y += 27
    os.makedirs(os.path.join(out, "sheets"), exist_ok=True)
    path = os.path.join(out, "sheets", name)
    sheet.save(path)
    print("draw_panel_latch:", path)


def r(out: str, c: str, scene: str, view: str) -> str:
    return os.path.join(out, c, "renders", scene, f"{view}.png")


TEXT = {
    "M": ("M. Magnets only",
          ["How it works: a magnet pair at each corner holds the panel down on its ledge. The two cones at the rear edge stop it sliding. To take it out, pull it straight up.",
           "To put it in: set it on the ledge; the cones find the sockets and the magnets pull it down."]),
    "H": ("H. Rear hooks and magnets",
          ["How it works: two hooks under the rear edge of the panel go under the rear bar of the frame. The front edge is held only by the two front magnets.",
           "To take it out: lift the front edge (by the lever). The panel turns about its rear top edge and the hooks slide out of their notches; then lift it up and forward.",
           "To put it in: hold the panel with its front up, put its rear edge down against the rear of the pocket, and lower the front."]),
    "B": ("B. Rear hooks and a push bolt",
          ["How it works: the rear hooks of H hold the rear edge. At the front centre a printed bolt goes over two lips of a strike under the panel. A steel spring pushes the bolt forward; "
           "an 8 degree wedge under it pulls the panel down, so the panel sits without play. The front end of the bolt is a flush button in the front face of the deck.",
           "To take it out: push the button. The bolt slides back 5, the lips are free, and two springs lift the front edge. Lift the front edge and pull the panel up and forward.",
           "To put it in: put the rear edge down against the rear of the pocket, push the button, lower the front, let the button go."]),
    "Q": ("Q. Rear hooks and two quarter-turn cams",
          ["How it works: the rear hooks of H hold the rear edge. Near the front edge, two printed cams go through the panel. Under the panel the tongue of each cam turns under the front bar of the frame.",
           "To take it out: turn the two heads a quarter turn with a finger (the finger bar shows the way of the tongue), lift the front edge by the lever or by the finger bars, and pull the panel up and forward.",
           "To put it in: as H, then turn the two heads back."]),
}


def factor_line(s: dict) -> str:
    return f"Hold (ESTIMATED): factor {s['factor']:g} against the worst of a pull of 80 N on the lever and a push of 50 N at the ball. Normal play (15 N at the ball) without a click: factor {s['play']:g} on the preload alone."


def sheets(out: str) -> None:
    summ = json.load(open(os.path.join(out, "summary.json")))
    edges = ("All BREP edges are drawn. Blue: the frame (stays in the cabinet). Dark: the panel. Orange: the parts of the latch that move. Grey: magnets and springs. "
             "The colours are for the pictures only: the button of B prints in the colour of the deck, the heads of Q in the colour of the panel.")
    for k, c in enumerate(CANDIDATES):
        s = summ[c]
        title, how = TEXT[c]
        sh = s["shows"]
        first = "the panel is lifted 5" if c == "M" else "the front edge is up 4 degrees" if c == "H" else "released"
        page(out, f"{k + 1:02d}-{c}-{s['name'].lower().replace(' ', '-')}.png", title,
             [(r(out, c, "top", "player"), "1. what the player sees, panel in"), (r(out, c, "top", "front"), "2. the front face of the deck"),
              (r(out, c, "section-locked", "section"), "3. section through the latch, locked"), (r(out, c, "section-released", "section"), f"4. the same section, {first}"),
              (r(out, c, "way-1", "way"), "5. way out, step 1"), (r(out, c, "way-2", "way"), "6. step 2"),
              (r(out, c, "way-3", "way"), "7. step 3"), (r(out, c, "way-4", "way"), "8. step 4: out"),
              (r(out, c, "parts", "parts"), "9. the latch parts apart")],
             how + [f"On the top face: {sh['top_in']} On the front face: {sh['front_in']}", f"Panel out: {sh['out']}", f"The gap round the panel: {sh['gap']}",
                    factor_line(s), f"Removal: {s['removal']['how']}", "Buy: " + "; ".join(s["buy"]) + ".", edges])
    # the side-by-side sheet, from the same camera
    cells = [(os.path.join(out, "renders", f"compare-{c}", "player.png"), f"{c}. {summ[c]['name']}: factor {summ[c]['factor']:g}") for c in CANDIDATES]
    notes = [f"{c}. {summ[c]['name']}. Top face: {summ[c]['shows']['top_in']} Front face: {summ[c]['shows']['front_in']}" for c in CANDIDATES]
    notes += ["The factor is the smallest of all load cases: a pull of 80 N up on the lever, a push of 50 N at the ball in each of four directions, and the two together. "
              "It is ESTIMATED from maker's data for the magnets and from beam theory for the printed parts. Below 1 the panel comes out under the load.",
              "Recommendation: B. Nothing shows on the top face, no tool, a rigid lock against the pull, and a spring and wedge for the preload. "
              "The cost is a button on the front face of the deck.", edges]
    page(out, "05-side-by-side.png", "Four latches, the same camera", cells, notes, w=760)


if __name__ == "__main__":
    args = list(sys.argv[1:])
    only = "sheets" in args
    out = next((a for a in args if a != "sheets"), os.path.join(ROOT, "out", "panel-latch"))
    if not only:
        render(out)
    sheets(out)
