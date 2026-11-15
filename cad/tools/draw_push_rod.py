"""The sheet for the owner of the push rod's mark: the front of the cabinet with the printed bezel plate, without the
rod and with it, from one camera about 1 m in front of the screen; the same place of the two views at full size; and a
close view of the right bar with the mark of 4.4 x 4.4 beside a ruler of 1 mm ticks. Every face edge is drawn.

    CANDYBAR_OUT=cad/out/push-rod-mark cad/candybar/freecad-run.sh candybar.shell.rod_mark
    cad/.venv-tools/bin/python cad/tools/draw_push_rod.py cad/out/push-rod-mark    # --no-render: compose from the renders that are there

It renders the scenes of candybar.shell.rod_mark with tools/render_views.py (Blender, one at a time under the lock of
tools/cad-lock.sh) and writes <out>/push-rod-mark.png.
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
VIEWS = {"without-rod": "front-1m", "with-rod": "front-1m", "closeup": "mark"}


def render(out: str) -> dict[str, str]:
    pngs = {}
    for scene, view in VIEWS.items():
        work = os.path.join(out, "renders", scene)
        size = "1600" if scene == "closeup" else "2400"
        subprocess.run([os.path.join(HERE, "cad-lock.sh"), sys.executable, os.path.join(HERE, "render_views.py"), work,
                        os.path.join(out, "scenes", scene), "--views", view, "--size", size], check=True)
        pngs[scene] = os.path.join(work, f"{view}.png")
    return pngs


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    out = os.path.abspath(args[0] if args else "cad/out/push-rod-mark")
    info = json.load(open(os.path.join(out, "scene.json")))
    pngs = {k: os.path.join(out, "renders", k, f"{v}.png") for k, v in VIEWS.items()} if "--no-render" in argv else render(out)
    a, b, c = (Image.open(pngs[k]).convert("RGB") for k in ("without-rod", "with-rod", "closeup"))
    # the place of the mark at full size: the same box of pixels of the two front views
    w, h = a.size
    px_per_mm = w / info["front_view_width_mm"]
    box = (int(w * 0.72), int(h * 0.50), int(w * 0.98), int(h * 0.72))   # round the mark on the right bar
    crops = [img.crop(box) for img in (a, b)]
    scale = 0.42
    fw, fh = int(w * scale), int(h * scale)
    margin, gap, head = 40, 30, 175
    cw, ch = crops[0].size
    width = 2 * fw + gap + 2 * margin
    height = head + fh + 60 + ch + 60 + c.size[1] // 2 + 140
    sheet = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(sheet)
    d.text((margin, 30), "The push rod of the monitor's power button: its mark on the bezel plate", font=font(40, True), fill="black")
    d.text((margin, 85), f"The rod is {info['rod_mm']:g} x {info['rod_mm']:g} in a hole of {info['mark_mm']:g} x {info['mark_mm']:g}, "
           f"{info['rod_proud']:g} out of the face, on the inner frame of the right bar. Face edges drawn.\nThe two views have one camera, "
           f"{info['front_camera_distance_mm'] / 1000:.1f} m in front of the screen.", font=font(22), fill="black")
    y = head
    for k, (img, title) in enumerate(((a, "Without the rod (the default)"), (b, "With the rod"))):
        x = margin + k * (fw + gap)
        sheet.paste(img.resize((fw, fh)), (x, y + 40))
        d.text((x, y), title, font=font(24, True), fill="black")
    y += fh + 60
    d.text((margin, y), f"The same place of the two views, at the size of the render ({px_per_mm:.1f} pixels for each mm at that distance)",
           font=font(24, True), fill="black")
    for k, img in enumerate(crops):
        sheet.paste(img, (margin + k * (cw + gap), y + 40))
    y += ch + 60
    cs = c.resize((c.size[0] // 2, c.size[1] // 2))
    d.text((margin, y), "Close view of the right bar: the mark and a ruler with a tick each mm (long each 5 mm)", font=font(24, True), fill="black")
    sheet.paste(cs, (margin, y + 40))
    d.text((margin + cs.size[0] + 30, y + 60), "The other way to the button: pull the plate off\n(magnets) and press it with a finger.\n"
           "The monitor starts by itself when its USB-C\nsocket gets power (the owner's test).", font=font(24), fill="black")
    path = os.path.join(out, "push-rod-mark.png")
    sheet.save(path)
    print(f"draw_push_rod: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
