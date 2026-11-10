"""Profile photos: a side view of a cabinet, traced, levelled and scaled; measured; and laid over the blueprint.

The annotation file (cad/reference/<photo-stem>.json, see photo_annot.py) holds the picks:
  traces   {name: [[x, y], ...]}   edges traced in photo pixels (photo_annot.py snap)
  points   {name: [x, y, sigma]}   single picks
  profile  {"floor": trace,                          a line on the floor: it sets the level
            "height": [trace, trace | point, mm],    from the floor to the highest point of a trace or a point
            "depth": [point, point, mm]}             along the floor, between two points

The picture is levelled on the floor line and scaled with a separate millimetres per pixel along the height
and along the depth. Where the photo is not a true side view, the two scales disagree; every measure is also
computed with the height scale on both axes and with the depth scale on both axes, and the spread of the three
is its uncertainty from perspective.

Subcommands:
  measure   the profile of the photo and of the blueprint (dims.Blueprint, profiles.py) side by side, as ratios
            to the body width; writes <out>/<stem>-profile.json and prints the table
  overlay   the blueprint side profile, scaled so that its rail chord (deck top to seam) matches the photo's,
            drawn on the photo, and both profiles drawn over each other without the photo

Example:
    cad/.venv-tools/bin/python cad/tools/photo_profile.py measure cad/reference/owner-ref-4-profile.json
    cad/.venv-tools/bin/python cad/tools/photo_profile.py overlay cad/reference/owner-ref-4-profile.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections.abc import Callable

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import photo_annot as pa  # noqa: E402

sys.path.insert(0, os.path.join(pa.REPO, "cad"))
from candybar.shell import profiles as pr  # noqa: E402
from candybar.shell.dims import Blueprint  # noqa: E402

RECON = os.path.join(pa.REPO, "cad", "out", "shell-d", "reconstruction")
REAL_W = 750.0
Map = Callable[[np.ndarray], np.ndarray]


# ---------- the photo in millimetres ----------

class Frame:
    """Photo pixels to (depth, height) in millimetres: depth toward the front, height up from the floor."""

    def __init__(self, ann: pa.Annotation, scales: str = "axes"):
        prof, tr = ann.data["profile"], ann.data["traces"]
        floor = np.array(tr[prof["floor"]], float)
        a, b = np.polyfit(floor[:, 0], floor[:, 1], 1)
        self.angle = math.atan(a)
        self.floor = (floor[:, 0].mean(), floor[:, 0].mean() * a + b)
        top = self.level(self.ref(ann, prof["height"][1], highest=True))
        h_px = self.level(np.array([self.floor]))[0, 1] - top[0, 1]
        d0, d1 = (self.level(self.ref(ann, k))[0, 0] for k in prof["depth"][:2])
        self.sz, self.sx = prof["height"][2] / h_px, prof["depth"][2] / abs(d1 - d0)
        self.x0 = min(d0, d1)
        if scales == "height":
            self.sx = self.sz
        elif scales == "depth":
            self.sz = self.sx

    @staticmethod
    def ref(ann: pa.Annotation, key: str, highest: bool = False) -> np.ndarray:
        if key in ann.data.get("traces", {}):
            t = np.array(ann.data["traces"][key], float)
            return t[[int(np.argmin(t[:, 1]))]] if highest else t
        return np.array([ann.data["points"][key][:2]], float)

    def level(self, px: np.ndarray) -> np.ndarray:
        c, s = math.cos(-self.angle), math.sin(-self.angle)
        q = np.asarray(px, float) - self.floor
        return np.stack([q[:, 0] * c - q[:, 1] * s, q[:, 0] * s + q[:, 1] * c], axis=1) + self.floor

    def mm(self, px: np.ndarray) -> np.ndarray:
        q = self.level(np.atleast_2d(px))
        return np.stack([(q[:, 0] - self.x0) * self.sx, (self.floor[1] - q[:, 1]) * self.sz], axis=1)

    def px(self, mm: np.ndarray) -> np.ndarray:
        mm = np.atleast_2d(mm)
        q = np.stack([mm[:, 0] / self.sx + self.x0, self.floor[1] - mm[:, 1] / self.sz], axis=1) - self.floor
        c, s = math.cos(self.angle), math.sin(self.angle)
        return np.stack([q[:, 0] * c - q[:, 1] * s, q[:, 0] * s + q[:, 1] * c], axis=1) + self.floor


# ---------- measures on a profile in millimetres ----------

def circle(p: np.ndarray) -> tuple[np.ndarray, float]:
    """Least-squares circle through points."""
    A = np.c_[2 * p, np.ones(len(p))]
    sol = np.linalg.lstsq(A, (p ** 2).sum(1), rcond=None)[0]
    c = sol[:2]
    return c, float(math.sqrt(sol[2] + c @ c))


def arc(p: np.ndarray) -> dict:
    """A convex curve between its two ends: chord, lean of the chord from upright, sagitta, fitted radius."""
    a, b = p[0], p[-1]
    u = (b - a) / np.linalg.norm(b - a)
    off = (p - a) @ np.array([-u[1], u[0]])
    chord = float(np.linalg.norm(b - a))
    _, r = circle(p)
    return {"chord": chord, "lean_deg": math.degrees(math.atan2(abs(b[0] - a[0]), abs(b[1] - a[1]))),
            "sagitta": float(np.max(np.abs(off))), "sagitta_over_chord": float(np.max(np.abs(off))) / chord, "radius": r}


def lean(p: np.ndarray) -> float:
    """Lean of a straight run from upright, degrees; positive when it leans toward the front as it rises."""
    return math.degrees(math.atan(np.polyfit(p[:, 1], p[:, 0], 1)[0]))


def x_at(p: np.ndarray, z: float) -> float:
    o = np.argsort(p[:, 1])
    return float(np.interp(z, p[o, 1], p[o, 0]))


# ---------- the two profiles ----------

def photo_profile(ann: pa.Annotation, f: Frame) -> dict:
    """The named traces and points of the photo in millimetres."""
    tr = {k: f.mm(np.array(v, float)) for k, v in ann.data["traces"].items()}
    pts = {k: f.mm(np.array(v[:2], float))[0] for k, v in ann.data["points"].items()}
    return {"traces": tr, "points": pts}


def blueprint_profile(d: Blueprint) -> dict:
    """The blueprint's side view in (depth, height), millimetres, with the same names as the photo's traces. Depth
    runs toward the front, as in the photo: it is the blueprint's y negated."""
    fr = pr.front(d)
    h = pr.hood(d)
    oy, oz = h.origin[1], h.origin[2]
    rail = np.array([fr.rail.at(fr.rail.a0 + (fr.rail.a1 - fr.rail.a0) * k / 60) for k in range(61)])
    sweep = np.array([fr.sweep.at(fr.sweep.a0 + (fr.sweep.a1 - fr.sweep.a0) * k / 20) for k in range(21)])
    side = np.array([(oy + y, oz + z) for y, z in h.side])
    t = math.tan(math.radians(d.step_lean))
    step = np.array([(d.step_y0 + d.width / 2 - d.rear_w / 2 + z * t, z) for z in np.linspace(0.0, d.body_top, 30)])
    crease = np.array([(y + ny * d.deck_lean_h, z + nz * d.deck_lean_h) for y, z, (ny, nz) in fr.chain()[:49]])
    rear = np.array(pr.rear_profile(d)[1:5])
    outline = np.vstack([[(0.0, 0.0), (0.0, d.deck_top)], sweep, rail, [(d.seam_y + d.hood_shoulder_front, d.body_top)], side, rear, [(0.0, 0.0)]])
    flip = lambda q: np.asarray(q, float) * np.array([-1.0, 1.0])
    return {"traces": {k: flip(v) for k, v in {"rail": rail, "sweep": sweep, "hood": side, "step_inner": step, "rail_crease": crease, "rear": rear}.items()},
            "points": {k: flip(v) for k, v in {"rail_foot_deck": sweep[0], "rail_top": rail[-1], "hood_front_foot": (oy, oz)}.items()},
            "outline": flip(outline)}


def measures(prof: dict, real: bool) -> dict[str, float]:
    """The lines of the comparison, in millimetres and degrees."""
    tr, pt = prof["traces"], prof["points"]
    out: dict[str, float] = {}
    if real:
        rail = tr["rail"][tr["rail"][:, 1] <= pt["rail_top"][1] + 1e-9]
        _, r_rail = circle(rail)
        a = arc(np.vstack([[pt["rail_top"]], rail]))
        sweep = np.vstack([rail[-3:], tr["sweep"]])
        _, r_sweep = circle(sweep)
        seam = np.mean(tr["seam_top"][:, 1])
        deck = np.mean(tr["deck_top"][:, 1])
        hood_front = pt["box_top_front"][0]
        out.update({
            "rail_chord": a["chord"], "rail_lean": a["lean_deg"], "rail_sagitta": a["sagitta"], "rail_s_over_c": a["sagitta_over_chord"],
            "rail_radius": r_rail, "sweep_radius": r_sweep, "seam_above_deck": seam - deck,
            "hood_height": tr["hood_top"][:, 1].max() - seam, "hood_depth_at_seam": hood_front - pt["hood_rear_foot"][0],
            "hood_overhang": hood_front - pt["rail_top"][0], "hood_front_box_height": pt["box_top_front"][1] - seam,
            "hood_front_box_depth": hood_front - pt["box_top_rear"][0], "hood_upper_depth": pt["hood_top_front"][0] - pt["hood_top_rear"][0],
            "hood_step": tr["hood_top"][:, 1].max() - pt["box_top_front"][1], "hood_rear_lean": lean(tr["hood_rear"]),
            "rear_upper_lean": lean(tr["rear"][tr["rear"][:, 1] > seam - 0.35 * (seam - deck)])})
    else:
        out.update(blueprint_measures(prof))
    z_mid = lambda frac: deck_z(prof, real) + frac * (seam_z(prof, real) - deck_z(prof, real))
    for frac in (0.25, 0.5, 0.75):
        z = z_mid(frac)
        out[f"crease_gap_{frac}"] = x_at(tr["rail"], z) - x_at(tr["rail_crease"], z)
        out[f"step_gap_{frac}"] = x_at(tr["rail"], z) - x_at(tr["step_inner"], z)
    return out


def deck_z(prof: dict, real: bool) -> float:
    return float(np.mean(prof["traces"]["deck_top"][:, 1])) if real else float(prof["points"]["rail_foot_deck"][1])


def seam_z(prof: dict, real: bool) -> float:
    return float(np.mean(prof["traces"]["seam_top"][:, 1])) if real else float(prof["points"]["hood_front_foot"][1])


def blueprint_measures(prof: dict) -> dict[str, float]:
    d = Blueprint()
    fr, h = pr.front(d), pr.hood(d)
    a = arc(prof["traces"]["rail"])
    return {"rail_chord": a["chord"], "rail_lean": a["lean_deg"], "rail_sagitta": a["sagitta"], "rail_s_over_c": a["sagitta_over_chord"],
            "rail_radius": fr.rail.r, "sweep_radius": d.bend_r, "seam_above_deck": h.origin[2] - d.deck_top,
            "hood_height": h.height, "hood_depth_at_seam": h.depth, "hood_overhang": -d.hood_shoulder_front,
            "hood_front_box_height": float("nan"), "hood_front_box_depth": float("nan"), "hood_upper_depth": h.depth - d.hood_rear_arc_d - d.hood_edge_back,
            "hood_step": 0.0, "hood_rear_lean": 0.0, "rear_upper_lean": 0.0}


LINES = [
    # key, label, how to compare (W: ratio to the body width; C: ratio to the rail chord; deg: degrees)
    ("rail_s_over_c", "Rail arc, sagitta / chord (chord from the top of the sweep to the seam)", "1"),
    ("rail_lean", "Recline of the rail chord, deg from upright", "deg"),
    ("rail_radius", "Rail arc radius / W (circle fit)", "W"),
    ("sweep_radius", "Sweep radius / W (circle fit)", "W"),
    ("rail_chord", "Rail chord / W", "W"),
    ("seam_above_deck", "Seam (hood foot) above the deck top / W", "W"),
    ("hood_height", "Hood height over the seam / W", "W"),
    ("hood_depth_at_seam", "Hood depth at the seam / W", "W"),
    ("hood_overhang", "Hood front beyond the rail top at the seam / W (negative: behind it)", "W"),
    ("hood_front_box_height", "Front box of the hood (speaker and marquee), top above the seam / W", "W"),
    ("hood_front_box_depth", "Front box of the hood, depth in front of the upper part / W", "W"),
    ("hood_step", "Step from the front box up to the hood top / W", "W"),
    ("hood_upper_depth", "Flat hood top, depth / W", "W"),
    ("hood_rear_lean", "Hood rear, lean forward from upright, deg", "deg"),
    ("rear_upper_lean", "Body rear wall above the deck, lean forward from upright, deg", "deg"),
    ("step_gap_0.5", "Side band: rail edge to the step, at mid rail / W", "W"),
    ("crease_gap_0.5", "Rail edge to the line behind it (crease), at mid rail / W", "W"),
    ("crease_gap_0.25", "The same at a quarter of the rail height / W", "W"),
    ("crease_gap_0.75", "The same at three quarters of the rail height / W", "W"),
]


def ratio(v: float, kind: str, w: float, chord: float) -> float:
    return v / w if kind == "W" else v / chord if kind == "C" else v


def table(ann: pa.Annotation) -> tuple[list[dict], dict]:
    d = Blueprint()
    real = {k: measures(photo_profile(ann, Frame(ann, k)), True) for k in ("axes", "height", "depth")}
    ours = measures(blueprint_profile(d), False)
    f = Frame(ann)
    rows = []
    for key, label, kind in LINES:
        vals = [ratio(real[s][key], kind, REAL_W, real[s]["rail_chord"]) for s in ("axes", "height", "depth")]
        mine = ratio(ours[key], kind, d.width, ours["rail_chord"])
        rows.append({"line": label, "real": vals[0], "real_min": min(vals), "real_max": max(vals), "ours": mine,
                     "difference": mine - vals[0] if not math.isnan(mine) else float("nan")})
    return rows, {"mm_per_px_height": f.sz, "mm_per_px_depth": f.sx, "level_deg": math.degrees(f.angle)}


def fmt(v: float, kind: str) -> str:
    if math.isnan(v):
        return "none"
    return f"{v:.1f}" if kind == "deg" else f"{v:.3f}"


def measure(path: str) -> None:
    ann = pa.load(path)
    rows, scale = table(ann)
    out = pa.out_dir(ann)
    json.dump({"scale": scale, "rows": rows}, open(os.path.join(out, f"{ann.stem}-profile.json"), "w"), indent=1)
    print(f"mm per px: height {scale['mm_per_px_height']:.3f}, depth {scale['mm_per_px_depth']:.3f}; floor tilt {scale['level_deg']:.2f} deg")
    print("| Line | Real cabinet | Range | Ours | Difference |\n| --- | --- | --- | --- | --- |")
    for (key, label, kind), r in zip(LINES, rows):
        print(f"| {label} | {fmt(r['real'], kind)} | {fmt(r['real_min'], kind)} to {fmt(r['real_max'], kind)} | {fmt(r['ours'], kind)} | {fmt(r['difference'], kind)} |")


# ---------- overlay ----------

def fitted(ann: pa.Annotation, f: Frame) -> tuple[dict, Map]:
    """The blueprint profile moved and scaled so that its rail chord (deck top to seam) lies on the photo's."""
    bp = blueprint_profile(Blueprint())
    ph = photo_profile(ann, f)
    a0, a1 = bp["points"]["rail_foot_deck"], bp["points"]["rail_top"]
    b0, b1 = ph["points"]["rail_foot_deck"], ph["points"]["rail_top"]
    k = np.linalg.norm(b1 - b0) / np.linalg.norm(a1 - a0)
    return bp, lambda q: (np.asarray(q, float) - a0) * k + b0


def overlay(path: str) -> None:
    ann = pa.load(path)
    f = Frame(ann)
    bp, move = fitted(ann, f)
    os.makedirs(RECON, exist_ok=True)
    img = cv2.cvtColor(ann.image, cv2.COLOR_BGR2RGB)
    fig, ax = plt.subplots(figsize=(img.shape[1] / 60, img.shape[0] / 60), dpi=60)
    ax.imshow(img)
    for name, q in [("outline", bp["outline"]), ("step", bp["traces"]["step_inner"]), ("crease", bp["traces"]["rail_crease"])]:
        p = f.px(move(q))
        ax.plot(p[:, 0], p[:, 1], color="#00e5ff" if name == "outline" else "#ff3df5", lw=1.6 if name == "outline" else 1.0)
    for k, t in ann.data["traces"].items():
        t = np.array(t)
        ax.plot(t[:, 0], t[:, 1], ".", color="#ffb000", ms=2.5)
    ax.set_axis_off()
    ax.set_title("blueprint (cyan) on the photo, rail chord matched; picks of the photo (orange)", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(RECON, f"overlay-{ann.stem}.png"))
    plt.close(fig)
    ph = photo_profile(ann, f)
    fig, ax = plt.subplots(figsize=(9, 11))
    c0, c1 = ph["points"]["rail_foot_deck"], ph["points"]["rail_top"]
    norm = lambda q: (np.asarray(q, float) - c0) / np.linalg.norm(c1 - c0)
    for k, t in ph["traces"].items():
        q = norm(t)
        ax.plot(q[:, 0], q[:, 1], "-", color="#b0302a", lw=1.3, label="real New Astro City (traces)" if k == "rail" else None)
    for name, q in [("outline", bp["outline"]), ("step", bp["traces"]["step_inner"]), ("crease", bp["traces"]["rail_crease"])]:
        q = norm(move(q))
        ax.plot(q[:, 0], q[:, 1], "-", color="#1f4e8c", lw=1.3 if name == "outline" else 0.8, label="blueprint" if name == "outline" else None)
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.legend(loc="lower left")
    ax.set_xlabel("depth / rail chord")
    ax.set_ylabel("height / rail chord, from the foot of the rail")
    ax.set_title(f"Side profiles over each other, scaled to the rail chord (deck top to seam)\n{ann.stem}: mm per px {f.sz:.2f} (height), {f.sx:.2f} (depth)")
    fig.tight_layout()
    fig.savefig(os.path.join(RECON, f"profiles-{ann.stem}.png"), dpi=110)
    plt.close(fig)
    print("photo_profile:", os.path.relpath(os.path.join(RECON, f"overlay-{ann.stem}.png"), pa.REPO), os.path.relpath(os.path.join(RECON, f"profiles-{ann.stem}.png"), pa.REPO))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("cmd", choices=["measure", "overlay"])
    ap.add_argument("annotation")
    a = ap.parse_args()
    measure(a.annotation) if a.cmd == "measure" else overlay(a.annotation)


if __name__ == "__main__":
    main()
