"""Detail sheet for one region of a reference photo: crop, local contrast, edges, and brightness profiles.

The region and its probes come from the annotation file (cad/reference/<photo-stem>.json). A probe is a scan
line from "from" to "to", averaged over "width" pixels across; it should cross the edges it reads at right
angles. Each profile is smoothed and split into plateaus (flat brightness: a flat face under even light),
ramps (brightness that changes steadily: a curved face such as a radius) and steps (a sharp change: a crease,
a border or a shadow line). When the probe has a "span" of two named points, every position is also given as
a fraction of the distance between the projections of those two points onto the probe.

Writes cad/out/photo-evidence/<photo-stem>/detail-<region>.png (the sheet) and detail-<region>.json (the
segments of every probe, in photo pixels along the probe and as span fractions).

Example:
    cad/.venv-tools/bin/python cad/tools/photo_detail.py cad/reference/photo-e-three-quarter.json deck-front
"""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

import photo_annot as pa


@dataclass
class Segment:
    kind: str
    start: float
    end: float
    mean: float
    slope: float
    start_frac: float | None = None
    end_frac: float | None = None


@dataclass
class Profile:
    name: str
    length: float
    values: list[float]
    steps: list[float]
    segments: list[Segment]
    span: tuple[float, float] | None
    steps_frac: list[float] | None = None


def luminance(img: np.ndarray) -> np.ndarray:
    b, g, r = (img[..., i].astype(np.float32) for i in range(3))
    return 0.299 * r + 0.587 * g + 0.114 * b


def sample(lum: np.ndarray, a: pa.Point, b: pa.Point, width: float, step: float = 0.5) -> tuple[np.ndarray, float]:
    a_, b_ = np.array(a), np.array(b)
    length = float(np.linalg.norm(b_ - a_))
    t = np.arange(0, length + 1e-9, step)
    d = (b_ - a_) / length
    n = np.array([-d[1], d[0]])
    offs = np.arange(-(width - 1) / 2, (width - 1) / 2 + 1e-9, 1.0) if width > 1 else np.array([0.0])
    xs = (a_[0] + np.outer(offs, np.full_like(t, n[0])) + np.outer(np.ones_like(offs), t * d[0]) - 0.5)
    ys = (a_[1] + np.outer(offs, np.full_like(t, n[1])) + np.outer(np.ones_like(offs), t * d[1]) - 0.5)
    v = cv2.remap(lum, xs.astype(np.float32), ys.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return v.mean(axis=0), length


def project(p: pa.Point, a: pa.Point, b: pa.Point) -> float:
    a_, b_, p_ = np.array(a), np.array(b), np.array(p)
    d = (b_ - a_) / np.linalg.norm(b_ - a_)
    return float((p_ - a_) @ d)


def segment(values: np.ndarray, step: float, smooth_px: float, k_step: float, min_px: float
            ) -> tuple[list[float], list[Segment]]:
    s = gaussian_filter1d(values, smooth_px / step)
    g = np.gradient(s, step)
    noise = 1.4826 * np.median(np.abs(g - np.median(g))) + 1e-6
    flat = max(2.5 * noise, 0.08 * np.abs(g).max())
    peaks, props = find_peaks(np.abs(g), prominence=k_step * noise, height=max(flat * 2.0, 1.5), width=0)
    kind = np.where(np.abs(g) < flat, 0, 1)
    in_step = np.zeros(len(g), bool)
    steps = []
    for p, lo, hi in zip(peaks, props["left_ips"], props["right_ips"]):
        if (hi - lo) * step <= 3.0 * smooth_px + 2.0:
            in_step[int(np.floor(lo)):int(np.ceil(hi)) + 1] = True
            steps.append(float(p * step))
    kind[in_step] = 2
    names = {0: "plateau", 1: "ramp", 2: "step"}
    segs: list[list[int]] = []
    for i, c in enumerate(kind):
        if segs and segs[-1][0] == c:
            segs[-1][2] = i
        else:
            segs.append([int(c), i, i])
    merged: list[list[int]] = []
    for c, i0, i1 in segs:
        if merged and (i1 - i0 + 1) * step < min_px and c != 2:
            merged[-1][2] = i1
        else:
            merged.append([c, i0, i1])
    out = []
    for c, i0, i1 in merged:
        if out and out[-1].kind == names[c]:
            out[-1].end = i1 * step
            continue
        seg = s[i0:i1 + 1]
        slope = float(np.polyfit(np.arange(len(seg)) * step, seg, 1)[0]) if len(seg) > 1 else 0.0
        out.append(Segment(names[c], i0 * step, i1 * step, float(seg.mean()), slope))
    return steps, out


def run(ann: pa.Annotation, region: str, smooth_px: float, k_step: float, min_px: float) -> str:
    x0, y0, x1, y1 = ann.data["regions"][region]
    pts = ann.resolve()
    probes = {k: v for k, v in ann.data.get("probes", {}).items() if v.get("region") == region}
    lum = luminance(ann.image)
    profiles: list[Profile] = []
    for name, pr in probes.items():
        a, b = ann.point(pr["from"], pts), ann.point(pr["to"], pts)
        vals, length = sample(lum, a, b, pr.get("width", 5))
        steps, segs = segment(vals, 0.5, pr.get("smooth_px", smooth_px), k_step, pr.get("min_px", min_px))
        span = None
        if "span" in pr:
            span = (project(pts[pr["span"][0]], a, b), project(pts[pr["span"][1]], a, b))
            for sg in segs:
                sg.start_frac = (sg.start - span[0]) / (span[1] - span[0])
                sg.end_frac = (sg.end - span[0]) / (span[1] - span[0])
        frac = [(s - span[0]) / (span[1] - span[0]) for s in steps] if span else None
        profiles.append(Profile(name, length, vals.tolist(), steps, segs, span, frac))

    crop = ann.image[y0:y1, x0:x1]
    k = min(900 / (x1 - x0), 700 / (y1 - y0))
    big = cv2.resize(crop, (round((x1 - x0) * k), round((y1 - y0) * k)), interpolation=cv2.INTER_CUBIC)
    lab = cv2.cvtColor(big, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    lab[..., 0] = clahe.apply(lab[..., 0])
    enh = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    gray = cv2.GaussianBlur(cv2.cvtColor(enh, cv2.COLOR_BGR2GRAY), (0, 0), 1.2 * k)
    med = float(np.median(gray))
    edges = cv2.Canny(gray, 0.33 * med * 0.5, 0.66 * med * 0.5 + 10)
    sob = cv2.magnitude(cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 1, 0), cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 0, 1))
    sob = (255 * np.clip(sob / (np.percentile(sob, 99.5) + 1e-6), 0, 1)).astype(np.uint8)
    edge_img = cv2.cvtColor(255 - sob, cv2.COLOR_GRAY2BGR)
    edge_img[edges > 0] = (0, 0, 200)

    def mark(img: np.ndarray) -> np.ndarray:
        img = img.copy()
        for i, p in enumerate(profiles):
            pr = probes[p.name]
            a, b = np.array(ann.point(pr["from"], pts)), np.array(ann.point(pr["to"], pts))
            col = pa.COLORS[i % len(pa.COLORS)]
            A = tuple(int(v) for v in ((a - (x0, y0)) * k))
            B = tuple(int(v) for v in ((b - (x0, y0)) * k))
            cv2.arrowedLine(img, A, B, col, 1, cv2.LINE_AA, tipLength=0.03)
            d = (b - a) / np.linalg.norm(b - a)
            for s in p.steps:
                q = ((a + d * s) - (x0, y0)) * k
                cv2.circle(img, (int(q[0]), int(q[1])), 4, col, 1, cv2.LINE_AA)
            pa.text(img, p.name, (A[0] + 4, A[1] - 4), col, 0.4)
        return img

    n = max(1, len(profiles))
    fig = plt.figure(figsize=(16, 7 + 2.6 * n), dpi=110)
    gs = fig.add_gridspec(1 + n, 3, height_ratios=[7] + [2.6] * n)
    for j, (img, title) in enumerate([(mark(big), f"crop x{k:.1f}"), (mark(enh), "local contrast (CLAHE)"),
                                      (mark(edge_img), "edges (gradient, Canny in red)")]):
        ax = fig.add_subplot(gs[0, j])
        ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), extent=(x0, x1, y1, y0))
        ax.set_title(title, fontsize=9)
        ax.tick_params(labelsize=7)
    shade = {"plateau": "#cfe8cf", "ramp": "#f3e3c0", "step": "#f2b8b8"}
    for i, p in enumerate(profiles):
        ax = fig.add_subplot(gs[1 + i, :])
        t = np.arange(len(p.values)) * 0.5
        ax.plot(t, p.values, color="0.3", lw=0.8, label="luminance")
        ax.plot(t, gaussian_filter1d(np.array(p.values), smooth_px / 0.5), color=np.array(pa.COLORS[i % 7][::-1]) / 255, lw=1.4)
        for sg in p.segments:
            ax.axvspan(sg.start, sg.end, color=shade[sg.kind], alpha=0.6, lw=0)
            label = f"{sg.kind[0].upper()} {sg.end - sg.start:.1f}"
            if sg.start_frac is not None:
                label += f"\n{sg.start_frac:.2f}-{sg.end_frac:.2f}"
            ax.text((sg.start + sg.end) / 2, ax.get_ylim()[0], label, fontsize=6, ha="center", va="bottom")
        for s in p.steps:
            ax.axvline(s, color="r", lw=0.8)
        if p.span:
            for s in p.span:
                ax.axvline(s, color="b", lw=1.0, ls="--")
        ax.set_xlim(0, p.length)
        ax.set_title(f"{p.name}: luminance along the probe (photo px); P plateau, R ramp, S step; "
                     f"red = step centre, blue dashed = span ends; numbers = length px and span fractions",
                     fontsize=8)
        ax.tick_params(labelsize=7)
    fig.suptitle(f"{ann.data['photo']}  region {region} [{x0},{y0},{x1},{y1}]", fontsize=10)
    fig.tight_layout()
    d = pa.out_dir(ann)
    png = os.path.join(d, f"detail-{region}.png")
    fig.savefig(png)
    plt.close(fig)
    cv2.imwrite(os.path.join(d, f"detail-{region}-clahe.png"), enh)
    with open(os.path.join(d, f"detail-{region}.json"), "w") as fh:
        json.dump({"photo": ann.data["photo"], "region": region, "profiles": [
            {**{k: v for k, v in asdict(p).items() if k != "values"}} for p in profiles]}, fh, indent=1)
    return png


def report(path: str) -> None:
    with open(path) as fh:
        data = json.load(fh)
    for p in data["profiles"]:
        print(f"{p['name']}: length {p['length']:.1f} px, span {p['span']}")
        fr = p["steps_frac"] or [None] * len(p["steps"])
        print("  step centres: " + ", ".join(f"{s:.1f}" + (f" ({f:.3f})" if f is not None else "")
                                           for s, f in zip(p["steps"], fr)))
        for s in p["segments"]:
            fr = f"  {s['start_frac']:+.3f} .. {s['end_frac']:+.3f}" if s["start_frac"] is not None else ""
            print(f"  {s['kind']:8s} {s['start']:6.1f} .. {s['end']:6.1f}  mean {s['mean']:6.1f}  "
                  f"slope {s['slope']:+6.2f}{fr}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("annotation")
    ap.add_argument("regions", nargs="*", help="region names (default: every region that has probes)")
    ap.add_argument("--smooth", type=float, default=1.5, help="profile smoothing, photo px")
    ap.add_argument("--k-step", type=float, default=8.0, help="step prominence in noise units")
    ap.add_argument("--min-px", type=float, default=3.0, help="shortest plateau or ramp, photo px")
    a = ap.parse_args()
    ann = pa.load(a.annotation)
    regions = a.regions or sorted({p["region"] for p in ann.data.get("probes", {}).values()})
    for r in regions:
        png = run(ann, r, a.smooth, a.k_step, a.min_px)
        print(f"photo_detail: {os.path.relpath(png, pa.REPO)}")
        report(png[:-4] + ".json")


if __name__ == "__main__":
    main()
