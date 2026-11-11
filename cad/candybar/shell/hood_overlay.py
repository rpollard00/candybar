"""Draw the outline of variant D over photo-e with cad/tools/photo_overlay.py, to see where its hood lands.

Our cabinet is wider and lower than the maker's mini, so the model cannot be laid on the photo as it is. The
four bezel corners picked in the photo are tied to a rectangle in our screen face that has our bezel's top
edge and width and the photo bezel's aspect. The fit then puts our bezel top on the photo's at the same
width, and the hood falls where it falls.

The photo tool and its annotation are another author's files and are only read: a copy of the annotation with
our overlay section goes to <out>/critique/hood/overlay, and the tool's evidence directory is pointed there
for this run. Needs the packages of the photo tools (cad/.venv-tools) and Blender. Example:
    cad/.venv-tools/bin/python cad/candybar/shell/hood_overlay.py cad/out/shell-d 3-short-band
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(os.path.dirname(HERE))
REPO = os.path.dirname(CAD)
PHOTO = "photo-e-three-quarter"
HOOD_BOX = (380, 150, 1320, 760)


def main(root: str, option: str) -> None:
    sys.path.insert(0, os.path.join(CAD, "tools"))
    import photo_annot
    import photo_overlay

    report = json.load(open(os.path.join(root, option, "report.json")))
    bezel_w = report["bezel"][0]
    top, low = report["bezel_top"], report["bezel_foot_line"]
    out = os.path.join(root, "critique", "hood", "overlay")
    os.makedirs(out, exist_ok=True)
    ann = json.load(open(os.path.join(CAD, "reference", f"{PHOTO}.json")))
    aspect = ann["planes"]["bezel"]["aspect"]
    k = bezel_w / aspect / report["bezel"][1]
    foot = [top[i] + k * (low[i] - top[i]) for i in range(2)]
    half = bezel_w / 2
    ann["overlay"] = {"model": os.path.relpath(os.path.join(root, option), REPO),
                      "anchors": {"bz_tl": [-half, *top], "bz_tr": [half, *top], "bz_br": [half, *foot], "bz_bl": [-half, *foot]},
                      "plane": ["bz_tl", "bz_tr", "bz_br", "bz_bl"], "f_px": ann["overlay"]["f_px"]}
    copy = os.path.join(out, f"{PHOTO}.json")
    json.dump(ann, open(copy, "w"), indent=1)
    photo_annot.EVIDENCE = os.path.abspath(out)
    sys.argv = ["photo_overlay.py", copy, "--fits", "plane"]
    photo_overlay.main()
    fit = os.path.join(out, PHOTO, "overlay-plane")
    crops = []
    for name in ("outline", "blend"):
        path = os.path.join(fit, f"{name}-hood.png")
        Image.open(os.path.join(fit, f"{name}.png")).convert("RGB").crop(HOOD_BOX).save(path)
        crops.append(path)
    subprocess.run([sys.executable, os.path.join(CAD, "tools", "compose_sheet.py"), os.path.join(root, "sheet-hood-overlay-photo-e.png"),
                    f"Outline of D on photo-e={crops[0]}", f"D and photo-e, half and half={crops[1]}", "--views", "photo",
                    "--title", "Variant D laid on photo-e: bezel top edges and bezel widths made equal", "--cell", "640",
                    "--subtitle", "Outline of D on photo-e=cyan: outline and creases of D",
                    "--subtitle", "D and photo-e, half and half=ours is 16:10, so only the hood and the bezel top compare"], check=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
