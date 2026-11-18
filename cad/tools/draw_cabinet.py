"""The sheet of the whole cabinet as it is designed now: the front, a three-quarter view from the front right, the
right side and a three-quarter view from the rear left, with every face edge drawn.

    CANDYBAR_OUT=cad/out/cabinet cad/candybar/freecad-run.sh candybar.shell.cabinet
    cad/.venv-tools/bin/python cad/tools/draw_cabinet.py cad/out/cabinet     # --no-render: render only what is missing

It renders the views of <out>/focus.json with tools/render_views.py (Blender, under the lock of tools/cad-lock.sh)
into <out>/renders and writes <out>/cabinet.png.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compose_sheet import font  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
VIEWS = [("front", "From the front"), ("front-right", "From the front right"), ("side", "The right side"), ("rear-left", "From the rear left")]
NOTES = [
    "The shell (white): the deck, the body and the hood, with the hood band A: two pods with black hole grilles, the logo field with its badge,",
    "the marquee with its lip and its translucent front. The front socket plate b-knob in the right side of the deck: four USB sockets, the power",
    "button and the volume knob. The printed bezel plate with the push rod of the monitor's button, and the monitor behind it. The control panel:",
    "the arcade panel with the lever and the eight buttons on the push bolt, whose button is in the front of the deck. The rear with the door on.",
    "Face edges drawn. The parts as built: cad/out/shell-rev7, cad/out/cradle, cad/out/control-panel. The FreeCAD document: shell.FCStd in this folder.",
]


def render(out: str, missing_only: bool) -> None:
    views = [v for v, _ in VIEWS if not (missing_only and os.path.exists(os.path.join(out, "renders", f"{v}.png")))]
    if views:
        subprocess.run([os.path.join(HERE, "cad-lock.sh"), sys.executable, os.path.join(HERE, "render_views.py"), os.path.join(out, "renders"), out,
                        "--views", ",".join(views), "--size", "1600"], check=True)


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    out = os.path.abspath(args[0] if args else "cad/out/cabinet")
    render(out, "--no-render" in argv)
    json.load(open(os.path.join(out, "manifest.json")))
    cw = 1000
    imgs = []
    for v, cap in VIEWS:
        im = Image.open(os.path.join(out, "renders", f"{v}.png")).convert("RGB")
        imgs.append((im.resize((cw, int(im.size[1] * cw / im.size[0]))), cap))
    ch = max(i.size[1] for i, _ in imgs)
    margin, gap, head, cap_h = 40, 30, 130, 44
    width = 2 * margin + 2 * cw + gap
    height = head + 2 * (cap_h + ch + gap) + 34 * len(NOTES) + 40
    sheet = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(sheet)
    d.text((margin, 30), "The cabinet as it is designed now", font=font(42, True), fill="black")
    d.text((margin, 84), "All sizes in mm. Every face edge is drawn.", font=font(22), fill="black")
    for k, (img, cap) in enumerate(imgs):
        x = margin + (k % 2) * (cw + gap)
        y = head + (k // 2) * (cap_h + ch + gap)
        d.text((x, y), cap, font=font(24, True), fill="black")
        sheet.paste(img, (x, y + cap_h))
    y = head + 2 * (cap_h + ch + gap)
    for line in NOTES:
        d.text((margin, y), line, font=font(21), fill="black")
        y += 34
    path = os.path.join(out, "cabinet.png")
    sheet.save(path)
    print(f"draw_cabinet: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
