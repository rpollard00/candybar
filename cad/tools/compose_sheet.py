"""Put named views of several models side by side, with labels, for review.

Each column is LABEL=DIR, where DIR holds the renders of render_views.py (and its views.json), or
LABEL=FILE.png for a single picture such as a photo. Each row is one named view. An optional overlay
JSON next to a model (DIR/overlay.json, or --overlay LABEL=FILE) draws hardware boxes as coloured
outlines, projected with the camera of the render. Models rendered with the same --frame share one scale;
a 100 mm scale bar is drawn on orthographic views.

Needs numpy and Pillow (cad/.venv-tools). Example:
    cad/.venv-tools/bin/python cad/tools/compose_sheet.py sheet.png "Reference=ref/" "Variant A=a/" \\
        --views three-quarter-front-right,side-right --title "Reference against variant A"
"""
from __future__ import annotations

import argparse
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

BG = (255, 255, 255)
INK = (30, 30, 34)
MUTED = (110, 110, 118)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]
    try:
        import matplotlib
        names.insert(0, os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf", names[0]))
    except ImportError:
        pass
    for n in names + ["/usr/share/fonts/TTF/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def project(cam: dict, pts: np.ndarray) -> np.ndarray:
    f, r, u = (np.array(cam[k]) for k in ("forward", "right", "up"))
    rx, ry = cam["res"]
    if cam["kind"] == "ortho":
        a = pts @ r - cam["center_ru"][0]
        b = pts @ u - cam["center_ru"][1]
        k = 1.0 / cam["mm_per_px"]
    else:
        d = pts - np.array(cam["location"])
        z = d @ f
        a, b = (d @ r) / z, (d @ u) / z
        k = max(rx, ry) / (cam["sensor_mm"] / cam["lens_mm"])
    return np.stack([rx / 2 + a * k, ry / 2 - b * k], axis=1)


def hull(p: np.ndarray) -> np.ndarray:
    pts = sorted(set(map(tuple, p.round(3))))
    if len(pts) < 3:
        return np.array(pts)

    def half(seq):
        out = []
        for q in seq:
            while len(out) >= 2 and (out[-1][0] - out[-2][0]) * (q[1] - out[-2][1]) - (out[-1][1] - out[-2][1]) * (q[0] - out[-2][0]) <= 0:
                out.pop()
            out.append(q)
        return out
    lower, upper = half(pts), half(reversed(pts))
    return np.array(lower[:-1] + upper[:-1])


def draw_overlay(img: Image.Image, cam: dict, overlay: list[dict], scale: float) -> None:
    d = ImageDraw.Draw(img, "RGBA")
    for item in overlay:
        p = project(cam, np.array(item["corners"])) * scale
        h = hull(p)
        col = tuple(int(item["colour"][i:i + 2], 16) for i in (1, 3, 5))
        d.polygon([tuple(q) for q in h], fill=col + (40,), outline=col + (255,), width=max(2, round(3 * scale)))


def load_cell(src: str, view: str) -> tuple[Image.Image, dict | None]:
    if os.path.isdir(src):
        meta = json.load(open(os.path.join(src, "views.json")))
        return Image.open(os.path.join(src, f"{view}.png")).convert("RGB"), meta["views"][view]
    return Image.open(src).convert("RGB"), None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("out")
    ap.add_argument("columns", nargs="+", help="LABEL=DIR or LABEL=FILE.png")
    ap.add_argument("--views", default="three-quarter-front-right")
    ap.add_argument("--title", default="")
    ap.add_argument("--subtitle", action="append", default=[], help="LABEL=text under the column label")
    ap.add_argument("--overlay", action="append", default=[], help="LABEL=overlay.json (default DIR/overlay.json)")
    ap.add_argument("--no-overlay", action="store_true")
    ap.add_argument("--cell", type=int, default=760, help="cell height in pixels")
    ap.add_argument("--footer", default="")
    a = ap.parse_args()
    cols = [c.split("=", 1) for c in a.columns]
    views = a.views.split(",")
    subs = dict(s.split("=", 1) for s in a.subtitle)
    overlays = dict(o.split("=", 1) for o in a.overlay)
    cells = [[load_cell(src, v) for _, src in cols] for v in views]
    scale = min(a.cell / img.height for row in cells for img, cam in row if cam is not None) if any(
        cam for row in cells for _, cam in row) else 1.0
    resized: list[list[tuple[Image.Image, dict | None]]] = []
    for row in cells:
        out_row = []
        for (label, src), (img, cam) in zip(cols, row):
            k = scale if cam is not None else a.cell / img.height
            im = img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)
            if cam is not None and not a.no_overlay:
                path = overlays.get(label, os.path.join(src, "overlay.json"))
                if os.path.exists(path):
                    draw_overlay(im, cam, json.load(open(path)), k)
            out_row.append((im, cam, k))
        resized.append(out_row)
    gap, top, label_h = 24, 70 if a.title else 16, 74
    col_w = [max(row[i][0].width for row in resized) for i in range(len(cols))]
    row_h = [max(c[0].height for c in row) for row in resized]
    footer_h = 40 if a.footer else 10
    W = sum(col_w) + gap * (len(cols) + 1)
    H = top + label_h + sum(row_h) + gap * len(views) + footer_h
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    if a.title:
        d.text((gap, 18), a.title, fill=INK, font=font(30, True))
    x = gap
    for i, (label, _) in enumerate(cols):
        d.text((x, top), label, fill=INK, font=font(26, True))
        if label in subs:
            d.text((x, top + 34), subs[label], fill=MUTED, font=font(20))
        x += col_w[i] + gap
    y = top + label_h
    for r, row in enumerate(resized):
        x = gap
        for i, (im, cam, k) in enumerate(row):
            sheet.paste(im, (x + (col_w[i] - im.width) // 2, y + row_h[r] - im.height))
            if cam is not None and cam["kind"] == "ortho":
                px = 100.0 / cam["mm_per_px"] * k
                bx, by = x + 12, y + row_h[r] - 18
                d.line([(bx, by), (bx + px, by)], fill=INK, width=4)
                d.text((bx, by - 26), "100 mm", fill=INK, font=font(17))
            x += col_w[i] + gap
        d.text((gap, y + 4), views[r], fill=MUTED, font=font(17))
        y += row_h[r] + gap
    if a.footer:
        d.text((gap, H - footer_h + 6), a.footer, fill=MUTED, font=font(18))
    sheet.save(a.out)
    print(f"compose_sheet: {W} x {H} -> {a.out}")


if __name__ == "__main__":
    main()
