"""Annotation files for reference photos: load, check, resolve points, and draw picks for review.

An annotation file lives in cad/reference/<photo-stem>.json. It names the photo by its repository-relative
path and SHA-256 (the photo is never copied) and holds every picked point, line, plane, probe and measure, so
that a measurement can be re-run and a wrong pick corrected by editing one number. Pixel coordinates are in
the full photo, x to the right and y down, with (0, 0) at the corner of the top-left pixel.

Keys (all optional except photo and sha256):
  points    {name: [x, y] | [x, y, sigma] | {"intersect": [[a, b], [c, d]]} | {"along": [a, b, t]}}
  lines     {name: [point, point, ...]}       points on one straight 3D edge
  vanishing {name: [line, line, ...]}         lines that are parallel in 3D
  camera    {"f_px": f} | {"f_from": "vanishing:x,z"} | {"f_from": "plane:screen"}
  planes    {name: {"rect": [tl, tr, br, bl], "size_mm": [w, h] | "aspect": w/h, "scale": [a, b, mm]}
             | {"vanishing": [u, v], "scale": [a, b, mm]}}
  measures  [{"name", "kind", ...}]           see photo_rectify.py
  regions   {name: [x0, y0, x1, y1]}
  probes    {name: {"from": point | [x, y], "to": ..., "width": px, "region": name, "span": [a, b]}}

Subcommands:
  show   draw every point, line, plane and probe with its label on the photo (and per-region crops)
  crop   write an enlarged crop with a labelled pixel grid and optional markers, for picking points by eye
  check  verify the SHA-256 of the photo
  snap   move a rough pick to the strongest brightness edge along a direction (prints the result)

Example:
    cad/.venv-tools/bin/python cad/tools/photo_annot.py show cad/reference/photo-e-three-quarter.json
    cad/.venv-tools/bin/python cad/tools/photo_annot.py crop cad/vendor/reddit-mgs-mini-astro/photo-b.png \\
        60 820 340 960 --scale 4 --grid 10 --mark 100,850 --out /tmp/crop.png
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from dataclasses import dataclass, field

import cv2
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EVIDENCE = os.path.join(REPO, "cad", "out", "photo-evidence")
DEFAULT_SIGMA = 1.0

Point = tuple[float, float]


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def repo_path(rel: str) -> str:
    return os.path.join(REPO, rel)


@dataclass
class Annotation:
    path: str
    data: dict
    image: np.ndarray = field(repr=False)

    @property
    def stem(self) -> str:
        return os.path.splitext(os.path.basename(self.path))[0]

    @property
    def size(self) -> tuple[int, int]:
        return self.image.shape[1], self.image.shape[0]

    def base_points(self) -> dict[str, tuple[float, float, float]]:
        out = {}
        sigma = float(self.data.get("sigma_px", DEFAULT_SIGMA))
        for name, v in self.data.get("points", {}).items():
            if isinstance(v, list):
                out[name] = (float(v[0]), float(v[1]), float(v[2]) if len(v) > 2 else sigma)
        return out

    def resolve(self, base: dict[str, Point] | None = None) -> dict[str, Point]:
        """All points, derived ones included, from the base picks (or from perturbed copies of them)."""
        pts: dict[str, Point] = dict(base) if base is not None else {
            k: (v[0], v[1]) for k, v in self.base_points().items()}
        pending = {k: v for k, v in self.data.get("points", {}).items() if isinstance(v, dict)}
        while pending:
            done = []
            for name, spec in pending.items():
                if "intersect" in spec:
                    groups = [self.data["lines"][g] if isinstance(g, str) else g for g in spec["intersect"]]
                    if all(p in pts for g in groups for p in g):
                        l1, l2 = (line_through([pts[p] for p in g]) for g in groups)
                        q = np.cross(l1, l2)
                        pts[name] = (float(q[0] / q[2]), float(q[1] / q[2]))
                        done.append(name)
                elif "along" in spec:
                    a, b, t = spec["along"]
                    if a in pts and b in pts:
                        pts[name] = (pts[a][0] + t * (pts[b][0] - pts[a][0]), pts[a][1] + t * (pts[b][1] - pts[a][1]))
                        done.append(name)
                else:
                    raise SystemExit(f"point {name}: unknown derived form {spec}")
            if not done:
                raise SystemExit(f"cannot resolve points {sorted(pending)}")
            for n in done:
                pending.pop(n)
        return pts

    def point(self, ref, pts: dict[str, Point]) -> Point:
        return pts[ref] if isinstance(ref, str) else (float(ref[0]), float(ref[1]))


def line_through(points: list[Point]) -> np.ndarray:
    """Homogeneous image line through two points, or the least-squares line through more."""
    q = np.array(points, float)
    c = q.mean(0)
    d = np.linalg.svd(q - c)[2][0]
    n = np.array([-d[1], d[0]])
    return np.array([n[0], n[1], -n @ c])


def load(path: str, verify: bool = True) -> Annotation:
    with open(path) as fh:
        data = json.load(fh)
    photo = repo_path(data["photo"])
    if not os.path.exists(photo):
        raise SystemExit(f"{data['photo']}: photo not found (fetch the vendor photos first)")
    if verify and sha256(photo) != data["sha256"]:
        raise SystemExit(f"{data['photo']}: SHA-256 differs from the annotation; the picks may not fit this file")
    image = cv2.imread(photo, cv2.IMREAD_COLOR)
    return Annotation(os.path.abspath(path), data, image)


def out_dir(ann: Annotation, *sub: str) -> str:
    d = os.path.join(EVIDENCE, ann.stem, *sub)
    os.makedirs(d, exist_ok=True)
    return d


COLORS = [(0, 0, 255), (0, 160, 0), (255, 0, 0), (0, 140, 255), (200, 0, 200), (0, 200, 200), (40, 40, 40)]


def text(img: np.ndarray, s: str, xy: tuple[int, int], color, scale: float = 0.45) -> None:
    cv2.putText(img, s, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), 3, cv2.LINE_AA)
    cv2.putText(img, s, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)


def draw(ann: Annotation, img: np.ndarray, k: float = 1.0, ox: float = 0.0, oy: float = 0.0,
         labels: bool = True) -> np.ndarray:
    """Draw the annotation onto img, an image of the photo scaled by k and offset by (ox, oy) photo px."""
    pts = ann.resolve()
    base = ann.base_points()
    sub = 16

    def P(p: Point) -> tuple[int, int]:
        return int(round(((p[0] - ox) * k) * sub)), int(round(((p[1] - oy) * k) * sub))

    def Pi(p: Point) -> tuple[int, int]:
        return int(round((p[0] - ox) * k)), int(round((p[1] - oy) * k))

    for i, (name, plane) in enumerate(ann.data.get("planes", {}).items()):
        if "rect" in plane:
            poly = np.array([P(pts[c]) for c in plane["rect"]], dtype=np.int32)
            cv2.polylines(img, [poly], True, (255, 160, 0), 1, cv2.LINE_AA, shift=4)
            if labels:
                text(img, f"plane {name}", Pi(pts[plane["rect"][0]]), (255, 120, 0))
    for i, (name, members) in enumerate(ann.data.get("lines", {}).items()):
        q = np.array([pts[m] for m in members])
        d = q[-1] - q[0]
        a, b = q[0] - 0.08 * d, q[-1] + 0.08 * d
        cv2.line(img, P(a), P(b), (0, 200, 255), 1, cv2.LINE_AA, shift=4)
    for name, probe in ann.data.get("probes", {}).items():
        a, b = ann.point(probe["from"], pts), ann.point(probe["to"], pts)
        cv2.arrowedLine(img, Pi(a), Pi(b), (200, 0, 200), 1, cv2.LINE_AA, tipLength=0.04)
        if labels:
            text(img, name, Pi(a), (200, 0, 200), 0.4)
    for j, (name, p) in enumerate(sorted(pts.items())):
        derived = name not in base
        c = (0, 140, 255) if derived else (0, 0, 255)
        x, y = P(p)
        r = 5 * sub
        cv2.line(img, (x - r, y), (x + r, y), c, 1, cv2.LINE_AA, shift=4)
        cv2.line(img, (x, y - r), (x, y + r), c, 1, cv2.LINE_AA, shift=4)
        if labels:
            text(img, name, (int(x / sub) + 4, int(y / sub) - 4), c, 0.38)
    return img


def show(path: str) -> None:
    ann = load(path)
    d = out_dir(ann)
    w, h = ann.size
    k = max(1.0, 1800 / max(w, h))
    big = cv2.resize(ann.image, (round(w * k), round(h * k)), interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(os.path.join(d, "picks.png"), draw(ann, big, k))
    for name, (x0, y0, x1, y1) in ann.data.get("regions", {}).items():
        kk = min(1400 / (x1 - x0), 1100 / (y1 - y0))
        crop = ann.image[y0:y1, x0:x1]
        crop = cv2.resize(crop, (round((x1 - x0) * kk), round((y1 - y0) * kk)), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(os.path.join(d, f"picks-{name}.png"), draw(ann, crop, kk, x0, y0))
    print(f"photo_annot: picks drawn -> {os.path.relpath(d, REPO)}")


def crop(photo: str, box: list[int], scale: float, grid: int, marks: list[str], out: str) -> None:
    img = cv2.imread(photo, cv2.IMREAD_COLOR)
    x0, y0, x1, y1 = box
    c = cv2.resize(img[y0:y1, x0:x1], (round((x1 - x0) * scale), round((y1 - y0) * scale)),
                   interpolation=cv2.INTER_CUBIC)
    pad = 34
    canvas = np.full((c.shape[0] + pad, c.shape[1] + pad, 3), 255, np.uint8)
    canvas[pad:, pad:] = c
    for gx in range((x0 // grid + 1) * grid, x1, grid):
        X = pad + round((gx - x0) * scale)
        major = gx % (grid * 5) == 0
        cv2.line(canvas, (X, pad - 8), (X, pad + (canvas.shape[0] if major else 0)), (0, 200, 255), 1)
        cv2.line(canvas, (X, canvas.shape[0] - 8), (X, canvas.shape[0]), (0, 200, 255), 1)
        if major:
            cv2.putText(canvas, str(gx), (X - 12, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    for gy in range((y0 // grid + 1) * grid, y1, grid):
        Y = pad + round((gy - y0) * scale)
        major = gy % (grid * 5) == 0
        cv2.line(canvas, (pad - 8, Y), (pad + (canvas.shape[1] if major else 0), Y), (0, 200, 255), 1)
        cv2.line(canvas, (canvas.shape[1] - 8, Y), (canvas.shape[1], Y), (0, 200, 255), 1)
        if major:
            cv2.putText(canvas, str(gy), (0, Y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0), 1)
    for i, m in enumerate(marks):
        parts = m.split(",")
        x, y = float(parts[0]), float(parts[1])
        label = parts[2] if len(parts) > 2 else str(i)
        X, Y = pad + round((x - x0) * scale), pad + round((y - y0) * scale)
        col = COLORS[i % len(COLORS)]
        cv2.circle(canvas, (X, Y), 6, col, 1, cv2.LINE_AA)
        cv2.line(canvas, (X - 10, Y), (X + 10, Y), col, 1)
        cv2.line(canvas, (X, Y - 10), (X, Y + 10), col, 1)
        text(canvas, label, (X + 7, Y - 7), col, 0.4)
    cv2.imwrite(out, canvas)


def snap(photo: str, xy: list[float], direction: str, reach: float, width: int) -> tuple[float, float, float]:
    """The strongest brightness edge within reach of xy along direction h, v or an angle in degrees."""
    img = cv2.imread(photo, cv2.IMREAD_COLOR).astype(np.float32)
    lum = 0.299 * img[..., 2] + 0.587 * img[..., 1] + 0.114 * img[..., 0]
    ang = {"h": 0.0, "v": 90.0}.get(direction)
    ang = math.radians(float(direction) if ang is None else ang)
    d = np.array([math.cos(ang), math.sin(ang)])
    n = np.array([-d[1], d[0]])
    t = np.arange(-reach, reach + 1e-9, 0.25)
    offs = np.arange(-(width - 1) / 2, (width - 1) / 2 + 1e-9)
    xs = xy[0] + np.outer(offs, np.full_like(t, n[0])) + t * d[0] - 0.5
    ys = xy[1] + np.outer(offs, np.full_like(t, n[1])) + t * d[1] - 0.5
    v = cv2.remap(lum, xs.astype(np.float32), ys.astype(np.float32), cv2.INTER_LINEAR).mean(0)
    v = np.convolve(v, np.ones(5) / 5, mode="same")
    g = np.abs(np.gradient(v))
    g[:4] = g[-4:] = 0
    i = int(np.argmax(g))
    return xy[0] + t[i] * d[0], xy[1] + t[i] * d[1], float(g[i] * 4)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("show")
    s.add_argument("annotation")
    c = sp.add_parser("crop")
    c.add_argument("photo")
    c.add_argument("box", nargs=4, type=int)
    c.add_argument("--scale", type=float, default=3.0)
    c.add_argument("--grid", type=int, default=10)
    c.add_argument("--mark", action="append", default=[], help="x,y[,label] in photo pixels")
    c.add_argument("--out", required=True)
    k = sp.add_parser("check")
    k.add_argument("annotation")
    n = sp.add_parser("snap")
    n.add_argument("photo")
    n.add_argument("points", nargs="+", help="x,y,direction (h, v or degrees)[,reach]")
    n.add_argument("--width", type=int, default=3)
    a = ap.parse_args()
    if a.cmd == "show":
        show(a.annotation)
    elif a.cmd == "crop":
        crop(a.photo, a.box, a.scale, a.grid, a.mark, a.out)
    elif a.cmd == "snap":
        for spec in a.points:
            p = spec.split(",")
            x, y, s = snap(a.photo, [float(p[0]), float(p[1])], p[2], float(p[3]) if len(p) > 3 else 6.0, a.width)
            print(f"{spec:28s} -> [{x:.1f}, {y:.1f}]  edge {s:.1f}")
    else:
        load(a.annotation)
        print("photo_annot: SHA-256 matches")


if __name__ == "__main__":
    main()
