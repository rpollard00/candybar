"""Compose the review sheets of the hood: the renders of a build beside the reference photos.

The crops of the photos go to <out>/critique/hood (the photos are other people's work and stay under
cad/vendor and cad/out). The sheets go to <out>. Run after build.py and render_views.py:
    cad/.venv-tools/bin/python cad/candybar/shell/hood_review.py cad/out/shell-d 3-short-band "round 3"
Needs Pillow and matplotlib (cad/.venv-tools).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(os.path.dirname(HERE))
VENDOR = os.path.join(CAD, "vendor")
REAL = os.path.join(VENDOR, "sega-new-astro-city", "photo-real-three-quarter.png")
MINI = os.path.join(VENDOR, "reddit-mgs-mini-astro")
CROPS = {
    "real-hood": (REAL, (140, 160, 580, 450)),
    "e-hood": (os.path.join(MINI, "photo-e-three-quarter.png"), (500, 210, 1220, 656)),
    "b-cabinet": (os.path.join(MINI, "photo-b.png"), (20, 800, 395, 1345)),
    "b-hood": (os.path.join(MINI, "photo-b.png"), (55, 805, 375, 965)),
    "a-hood": (os.path.join(MINI, "photo-a.png"), (170, 750, 450, 930)),
}


def crop(name: str, out_dir: str) -> str:
    src, box = CROPS[name]
    path = os.path.join(out_dir, f"{name}.png")
    Image.open(src).convert("RGB").crop(box).save(path)
    return path


def sheet(out: str, columns: list[str], views: str, title: str, subtitles: list[str], cell: int = 620) -> None:
    cmd = [sys.executable, os.path.join(CAD, "tools", "compose_sheet.py"), out, *columns, "--views", views, "--title", title,
           "--cell", str(cell), "--no-overlay"]
    for s in subtitles:
        cmd += ["--subtitle", s]
    subprocess.run(cmd, check=True)


def main(root: str, option: str, stamp: str) -> None:
    model = os.path.join(root, option)
    renders = os.path.join(model, "renders")
    crops = os.path.join(root, "critique", "hood")
    os.makedirs(crops, exist_ok=True)
    pic = {name: crop(name, crops) for name in CROPS}
    report = json.load(open(os.path.join(model, "report.json")))
    w, dep, h = report["outside"]
    hood = report["hood"]
    size = f"D={w:.0f} x {dep:.0f} x {h:.0f} mm, hood {hood['hood_height_over_body_top']:.0f} high ({hood['hood_height_ratio']:.2f} of the width), {stamp}"
    ours = f"D={renders}"
    view = lambda name: os.path.join(renders, f"{name}.png")
    sheet(os.path.join(root, "sheet-hood-vs-real.png"), [ours, f"Real New Astro City={pic['real-hood']}"], "hood-as-real",
          "The hood against the real New Astro City", [size, "Real New Astro City=seen from the player's left, camera at about the height of the seam"])
    sheet(os.path.join(root, "sheet-hood-vs-photo-e.png"), [ours, f"photo-e={pic['e-hood']}"], "hood-as-photo-e",
          "The hood against the maker's mini (photo-e)", [size, "photo-e=seen from the right and from above"])
    sheet(os.path.join(root, "sheet-hood-front.png"), [ours, f"photo-b={pic['b-cabinet']}", f"D, hood from straight in front={view('hood-front')}",
                                                         f"photo-b, hood={pic['b-hood']}"],
          "cabinet-as-photo-b", "The hood from the front, against the maker's mini (photo-b)",
          [size.replace(", hood", " | hood").replace(", round", " | round"), "photo-b=4:3 and 230 wide; | ours is 16:10 and 495 wide",
           "D, hood from straight in front=camera level with the hood", "photo-b, hood=camera a little above the hood"], cell=560)
    sheet(os.path.join(root, "sheet-hood-under-brow.png"), [ours, f"D, across the band={view('hood-speakers')}", f"photo-a (level view)={pic['a-hood']}"],
          "hood-under-brow", "Under the top bar: the marquee, the rail, the hood band and the ledge",
          [size, "D, across the band=the speaker faces lean back with the band; the marquee faces down", "photo-a (level view)=the marquee under the bar, the pods upright"])
    sheet(os.path.join(root, "sheet-vs-photo-e.png"), [ours, f"photo-e={os.path.join(MINI, 'photo-e-three-quarter.png')}"],
          "three-quarter-front-right", "Variant D against photo-e", [size], cell=900)
    sheet(os.path.join(root, "sheet-vs-real.png"), [ours, f"D, from the left={view('three-quarter-front-left')}", f"Real New Astro City={REAL}"],
          "three-quarter-front-right", "Variant D against the real New Astro City", [size, "Real New Astro City=a floor cabinet 750 wide, seen from the player's left"], cell=900)
    subprocess.run([sys.executable, os.path.join(HERE, "hood_sheet.py"), os.path.join(model, "hood-section.json"),
                    os.path.join(root, "sheet-hood-section.png")], check=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
