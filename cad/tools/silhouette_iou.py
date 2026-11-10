"""Score two renders of the same named orthographic view: silhouette IoU and bounding-box edge differences.

Takes two PNG renders of render_views.py (for example a/front.png and b/front.png). The object mask is read
from the sibling <view>-mask.png, or else from the pixels that differ from the background colour. When both
render directories hold views.json, the masks are placed in millimetres, so renders of different framing
compare correctly; the bounding-box differences are then in millimetres, else in pixels.

Three scores are printed:
  iou        the masks as placed (same position and scale)
  iou_scaled B scaled uniformly to the height of A, bottoms and centres aligned (shape only)
  iou_fitted B scaled to the width and the height of A separately (outline only)

Needs numpy and Pillow (cad/.venv-tools). Example:
    cad/.venv-tools/bin/python cad/tools/silhouette_iou.py ref/side-right.png target-A/side-right.png
"""
from __future__ import annotations

import argparse
import json
import os

import numpy as np
from PIL import Image

BACKGROUND = np.array([0.86, 0.865, 0.87]) * 255


def load_mask(png: str) -> np.ndarray:
    stem, _ = os.path.splitext(png)
    mask_png = stem + "-mask.png"
    if os.path.exists(mask_png):
        return np.asarray(Image.open(mask_png).convert("L"), dtype=np.float64) > 127
    rgb = np.asarray(Image.open(png).convert("RGB"), dtype=np.float64)
    return np.abs(rgb - BACKGROUND).max(-1) > 6


def load_camera(png: str) -> dict | None:
    meta = os.path.join(os.path.dirname(os.path.abspath(png)), "views.json")
    view = os.path.splitext(os.path.basename(png))[0]
    if not os.path.exists(meta):
        return None
    cam = json.load(open(meta))["views"].get(view)
    return cam if cam and cam["kind"] == "ortho" else None


def points_mm(mask: np.ndarray, cam: dict | None) -> np.ndarray:
    """Pixel centres of the mask in (right, up) coordinates: millimetres with a camera, else pixels."""
    ys, xs = np.nonzero(mask)
    if cam is None:
        return np.stack([xs + 0.5, mask.shape[0] - ys - 0.5], axis=1)
    rx, ry = cam["res"]
    k = cam["mm_per_px"]
    return np.stack([cam["center_ru"][0] + (xs + 0.5 - rx / 2) * k, cam["center_ru"][1] - (ys + 0.5 - ry / 2) * k], axis=1)


def rasterise(pts: np.ndarray, lo: np.ndarray, step: float, shape: tuple[int, int]) -> np.ndarray:
    grid = np.zeros(shape, dtype=bool)
    ij = np.floor((pts - lo) / step).astype(int)
    ok = (ij[:, 0] >= 0) & (ij[:, 0] < shape[1]) & (ij[:, 1] >= 0) & (ij[:, 1] < shape[0])
    grid[ij[ok, 1], ij[ok, 0]] = True
    return grid


def iou(a: np.ndarray, b: np.ndarray, step: float) -> float:
    lo = np.minimum(a.min(0), b.min(0)) - step
    hi = np.maximum(a.max(0), b.max(0)) + step
    shape = (int(np.ceil((hi[1] - lo[1]) / step)) + 1, int(np.ceil((hi[0] - lo[0]) / step)) + 1)
    ma, mb = rasterise(a, lo, step, shape), rasterise(b, lo, step, shape)
    union = (ma | mb).sum()
    return float((ma & mb).sum() / union) if union else 0.0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("a")
    ap.add_argument("b")
    a = ap.parse_args()
    cams = [load_camera(p) for p in (a.a, a.b)]
    use_mm = all(cams)
    pa, pb = (points_mm(load_mask(p), c if use_mm else None) for p, c in zip((a.a, a.b), cams))
    step = max(c["mm_per_px"] for c in cams) if use_mm else 1.0
    unit = "mm" if use_mm else "px"
    la, ha = pa.min(0), pa.max(0)
    lb, hb = pb.min(0), pb.max(0)
    sa, sb = ha - la, hb - lb
    k = sa[1] / sb[1]
    scaled = (pb - np.array([(lb[0] + hb[0]) / 2, lb[1]])) * k + np.array([(la[0] + ha[0]) / 2, la[1]])
    fitted = (pb - lb) * (sa / sb) + la
    print(f"view            {os.path.splitext(os.path.basename(a.a))[0]}")
    print(f"iou             {iou(pa, pb, step):.4f}")
    print(f"iou_scaled      {iou(pa, scaled, step):.4f}   (B x {k:.3f})")
    print(f"iou_fitted      {iou(pa, fitted, step):.4f}   (B x {sa[0] / sb[0]:.3f} wide, x {k:.3f} high)")
    print(f"size A          {sa[0]:.1f} x {sa[1]:.1f} {unit}")
    print(f"size B          {sb[0]:.1f} x {sb[1]:.1f} {unit}")
    for name, da in (("left", lb[0] - la[0]), ("right", hb[0] - ha[0]), ("bottom", lb[1] - la[1]), ("top", hb[1] - ha[1])):
        print(f"edge {name:<10} B - A = {da:+.1f} {unit}")


if __name__ == "__main__":
    main()
