"""Draw the seam proposal from what candybar.shell.split wrote, and write proposal.md.

    cad/.venv-tools/bin/python cad/tools/draw_split.py            -> cad/out/shell-bp/split/options.png, option-*.png, proposal.md
    cad/.venv-tools/bin/python cad/tools/draw_split.py render     -> cad/out/shell-bp/split/renders/<option>/*.png (Blender)

Run the cut first (CANDYBAR_OUT=cad/out/shell-bp cad/candybar/freecad-run.sh candybar.shell.split). The elevations
are z-buffer pictures of the pieces (the STL files of the cut), each piece in its soft tint, with the bezel plate,
the control panel and the screen as dark context. The seams are the 3D lines of seams.json, drawn where the
picture shows the surface they lie on: blue in a design line, red on an open face. The faces that a seam crosses
are found from the blueprint's labelled faces (profiles.faces), the hardware near a seam from the fit study's
boxes (fit/sections.json). Needs numpy, scipy and matplotlib (cad/.venv-tools).
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(HERE)
REPO = os.path.dirname(CAD)
sys.path.insert(0, CAD)
sys.path.insert(0, HERE)
import draw_blueprint as db  # noqa: E402
from candybar.shell import profiles as pr  # noqa: E402
from candybar.shell import split as sp  # noqa: E402
from candybar.shell.dims import Blueprint  # noqa: E402

SHELL = os.path.join(CAD, "out", "shell-bp")
OUT = os.path.join(SHELL, "split")
CLASS_COLOUR = {sp.HIDDEN: "#1565c0", sp.FACE: "#d62718"}
CONTEXT = {"~bezel": ("bezel.stl", (0.12, 0.12, 0.13)), "~panel": ("control_panel.stl", (0.22, 0.22, 0.24)),
           "~screen": ("screen.stl", (0.25, 0.29, 0.36))}
EXTENT = {"front": (-300, 300, -25, 600), "side": (-25, 610, -25, 600), "top": (-300, 300, -25, 605), "rear": (-300, 300, -25, 600)}
VIEW_NAMES = {"front": "front", "side": "right side", "top": "top", "rear": "rear"}
NEAR_HARDWARE = 18.0  # a flange 12 deep behind the 4 mm skin, and 2 mm
PX = 1.7


def load(opt: str) -> tuple[dict, dict, np.ndarray, np.ndarray]:
    here = os.path.join(OUT, opt)
    manifest = json.load(open(os.path.join(here, "manifest.json")))
    seams = json.load(open(os.path.join(here, "seams.json")))
    tris, ids = [], []
    for name, m in manifest.items():
        t = db.load_stl(os.path.join(here, m["file"]))
        tris.append(t)
        ids += [name] * len(t)
    for key, (f, _) in CONTEXT.items():
        path = os.path.join(SHELL, f)
        if os.path.exists(path):
            t = db.load_stl(path)
            tris.append(t)
            ids += [key] * len(t)
    return manifest, seams, np.concatenate(tris), np.array(ids, dtype=object)


def picture(ras: db.Raster, manifest: dict) -> np.ndarray:
    table = []
    for n in ras.names:
        if n in manifest:
            h = manifest[n]["finish"].lstrip("#")
            table.append(tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))
        else:
            table.append(CONTEXT.get(n, ("", (0.8, 0.8, 0.8)))[1])
    table.append((1.0, 1.0, 1.0))
    rgb = np.array(table)[ras.ids]
    shade = np.clip(0.78 + 0.22 * np.abs(ras.normal[..., 2:3]) + 0.0 * ras.normal[..., :1], 0, 1)
    rgb = rgb * np.where(ras.ids[..., None] < len(ras.names), 0.86 + 0.14 * shade, 1.0)
    from scipy import ndimage
    rgb[ndimage.binary_dilation(ras.edges(), iterations=1)] = (0.25, 0.25, 0.27)
    return np.clip(rgb, 0, 1)


def seam_runs(lines: list, view: db.View, ras: db.Raster) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """The parts of a seam's lines that the picture shows, in view coordinates; and the hidden parts."""
    x0, x1, y0, y1 = ras.extent
    h, w = ras.ids.shape
    seen, hidden = [], []
    for line in lines:
        p = np.array(line, float)
        xy, depth = db.project(p, view)
        c = np.clip(((xy[:, 0] - x0) * PX).astype(int), 0, w - 1)
        r = np.clip(((y1 - xy[:, 1]) * PX).astype(int), 0, h - 1)
        best = np.full(len(p), -np.inf)
        for dr in (-2, -1, 0, 1, 2):
            for dc in (-2, -1, 0, 1, 2):
                rr, cc = np.clip(r + dr, 0, h - 1), np.clip(c + dc, 0, w - 1)
                cover = ras.ids[rr, cc] < len(ras.names)
                best = np.maximum(best, np.where(cover, ras.depth[rr, cc], -np.inf))
        ok = depth >= best - 1.2
        k = 0
        while k < len(p):
            j = k
            while j + 1 < len(p) and ok[j + 1] == ok[k]:
                j += 1
            run = xy[max(k - 1, 0) if ok[k] else k: j + 1]
            if len(run) >= 2:
                (seen if ok[k] else hidden).append(run)
            k = j + 1
    return seen, hidden


class Labels:
    """Places labels so that they do not lie on each other: tries rings of offsets round the anchor."""

    def __init__(self, ax, extent) -> None:
        self.ax, self.boxes = ax, []
        self.extent = extent

    def put(self, at: tuple[float, float], text: str, colour: str, size: float = 6.5) -> None:
        w, h = 4.6 * len(text) + 6, 11.0
        cx = (self.extent[0] + self.extent[1]) / 2
        out = 1.0 if at[0] >= cx else -1.0
        for radius in (16, 26, 38, 52, 68, 86):
            for ang in (0, 25, -25, 50, -50, 75, -75, 100, -100, 130, -130, 180):
                a = math.radians(ang)
                dx, dy = out * radius * math.cos(a), radius * math.sin(a)
                c = (at[0] + dx, at[1] + dy)
                box = (c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2)
                if box[0] < self.extent[0] or box[2] > self.extent[1] or box[1] < self.extent[2] or box[3] > self.extent[3]:
                    continue
                if any(not (box[2] < b[0] or b[2] < box[0] or box[3] < b[1] or b[3] < box[1]) for b in self.boxes):
                    continue
                self.boxes.append(box)
                self.ax.annotate(text, xy=at, xytext=c, fontsize=size, ha="center", va="center", color=colour, family="DejaVu Sans Mono",
                                 fontweight="bold", zorder=9600, bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=colour, lw=0.7),
                                 arrowprops=dict(arrowstyle="-", color=colour, lw=0.6, shrinkA=0, shrinkB=0))
                return
        self.ax.annotate(text, xy=at, fontsize=size, color=colour, zorder=9600)

    def block(self, box: tuple[float, float, float, float]) -> None:
        self.boxes.append(box)


def draw_view(ax, key: str, manifest: dict, seams: dict, tri: np.ndarray, ids: np.ndarray, numbers: dict) -> None:
    view = db.VIEWS[key]
    ras = db.raster(tri, ids, view, EXTENT[key], px_per_mm=PX, closed=True)
    ax.imshow(picture(ras, manifest), extent=ras.extent, interpolation="antialiased", zorder=1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(VIEW_NAMES[key], fontsize=10)
    labels = Labels(ax, EXTENT[key])
    spots = ras.spots(min_px=4, right_only=False)
    for name, (at, room) in spots.items():
        if name in numbers and room > 5.0:
            ax.text(*at, str(numbers[name]), fontsize=5.6, ha="center", va="center", color="#333", zorder=9000,
                    bbox=dict(boxstyle="circle,pad=0.12", fc="white", ec="#666", lw=0.4, alpha=0.85))
            labels.block((at[0] - 5, at[1] - 5, at[0] + 5, at[1] + 5))
    done = set()
    order = sorted(seams.items(), key=lambda kv: (kv[1]["cls"] != sp.FACE, kv[0]))
    for name, s in order:
        seen, hidden = seam_runs(s["lines"], view, ras)
        colour = CLASS_COLOUR[s["cls"]]
        if hidden:
            ax.add_collection(LineCollection(hidden, colors=colour, linewidths=0.5, linestyles=(0, (2, 2)), alpha=0.35, zorder=9100))
        if seen:
            ax.add_collection(LineCollection(seen, colors=colour, linewidths=1.7, zorder=9200, capstyle="round"))
            tag = s["label"]
            if (tag, s["side"] == "L") in done:
                continue
            longest = max(seen, key=lambda r: np.linalg.norm(np.diff(r, axis=0), axis=1).sum())
            if np.linalg.norm(np.diff(longest, axis=0), axis=1).sum() < 6.0:
                continue
            if s["side"] == "L" and (tag, False) in done:
                continue
            done.add((tag, s["side"] == "L"))
            mid = longest[len(longest) // 2]
            labels.put((float(mid[0]), float(mid[1])), tag, colour)
    ax.set_xlim(EXTENT[key][:2])
    ax.set_ylim(EXTENT[key][2:])


def piece_numbers(rows: dict) -> dict:
    names = [n for n in rows if not n.startswith("base")]
    return {n: i + 1 for i, n in enumerate(names)}


def option_sheet(key: str, meas: dict, opt: sp.Option) -> str:
    manifest, seams, tri, ids = load(key)
    rows = meas["options"][key]["pieces"]
    numbers = piece_numbers(rows)
    fig = plt.figure(figsize=(25, 8.6))
    grid = fig.add_gridspec(1, 5, width_ratios=[1, 1.05, 1, 1, 1.05], wspace=0.03)
    for i, view in enumerate(("front", "side", "top", "rear")):
        draw_view(fig.add_subplot(grid[0, i]), view, manifest, seams, tri, ids, numbers)
    ax = fig.add_subplot(grid[0, 4])
    ax.axis("off")
    res = meas["options"][key]
    printed = {n: r for n, r in rows.items() if r["module"] != "base"}
    big = max(printed.items(), key=lambda kv: max(kv[1]["x"], kv[1]["z"]))
    face = sorted({s["label"] for s in seams.values() if s["cls"] == sp.FACE and s["module"] != "base"})
    text = [f"{opt.title}", "", f"pieces printed: {len(printed)} (+ {len(rows) - len(printed)} base tiles or one cut plate)",
            f"all pieces fit {meas['printer']['xy']:.0f} x {meas['printer']['xy']:.0f} x {meas['printer']['z']:.0f}: "
            f"{'yes' if res['fits'] else 'NO'}",
            f"largest: {big[0]}, {big[1]['x']:.0f} x {big[1]['y']:.0f} x {big[1]['z']:.0f}", "",
            f"seams on open faces: {', '.join(face)}", ""]
    for n, i in numbers.items():
        r = rows[n]
        text.append(f"{i:>2} {n:<22.22s} {r['x']:>4.0f} x {r['y']:>4.0f} x {r['z']:>4.0f} {'' if r['fits'] else ' NO'}")
    ax.text(0.0, 1.0, "\n".join(text), fontsize=7.0, family="DejaVu Sans Mono", va="top", ha="left", transform=ax.transAxes)
    ax.plot([0.02, 0.1], [0.04, 0.04], color=CLASS_COLOUR[sp.HIDDEN], lw=2, transform=ax.transAxes)
    ax.text(0.12, 0.04, "seam in a design line", fontsize=7.5, va="center", transform=ax.transAxes)
    ax.plot([0.02, 0.1], [0.015, 0.015], color=CLASS_COLOUR[sp.FACE], lw=2, transform=ax.transAxes)
    ax.text(0.12, 0.015, "seam on an open face (dashed: behind)", fontsize=7.5, va="center", transform=ax.transAxes)
    fig.suptitle(f"Seam proposal {opt.title}  (mm; the numbers are the pieces in the list)", fontsize=13, y=0.99)
    path = os.path.join(OUT, f"option-{key}.png")
    fig.savefig(path, dpi=115, bbox_inches="tight")
    plt.close(fig)
    print("draw_split:", os.path.relpath(path, REPO))
    return path


def stack(paths: list[str], out: str) -> None:
    from PIL import Image

    ims = [Image.open(p).convert("RGB") for p in paths]
    w = max(i.width for i in ims)
    canvas = Image.new("RGB", (w, sum(i.height for i in ims)), "white")
    y = 0
    for im in ims:
        canvas.paste(im, (0, y))
        y += im.height
    canvas.save(out)
    print("draw_split:", os.path.relpath(out, REPO))


# ---------- the faces a seam crosses, and the hardware near it ----------

def face_cloud(d: Blueprint, step: float = 3.0):
    """Points on every labelled face of the blueprint, about step apart, with the face ID of each."""
    from scipy.spatial import cKDTree

    tri, ids = db.triangles_of(pr.faces(d))
    pts, out_ids = [], []

    def split(t: np.ndarray, fid: str, depth: int = 0) -> None:
        if depth > 9 or max(np.linalg.norm(t[1] - t[0]), np.linalg.norm(t[2] - t[1]), np.linalg.norm(t[0] - t[2])) <= step:
            pts.append(t.mean(axis=0))
            out_ids.append(fid)
            return
        a, b, c = t
        ab, bc, ca = (a + b) / 2, (b + c) / 2, (c + a) / 2
        for q in ((a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca)):
            split(np.array(q), fid, depth + 1)

    for t, fid in zip(tri, ids):
        split(t, fid)
    return cKDTree(np.array(pts)), np.array(out_ids, dtype=object)


def crossed(lines: list, tree, fids: np.ndarray) -> list[str]:
    if not lines:
        return []
    p = np.concatenate([np.array(line, float) for line in lines])
    dist, idx = tree.query(p)
    hit = fids[idx[dist < 3.5]]
    names, counts = np.unique(hit, return_counts=True)
    order = {k: i for i, k in enumerate(["DK", "CP", "FB", "RL", "BZ", "SC", "RB", "FL", "HC", "MQ", "HB", "SP", "LG"])}
    keep = [str(n) for n, c in zip(names, counts) if c >= 3]
    return sorted(keep, key=lambda f: (order.get(f[:2], 99), int(f[2:])))


def hardware_boxes() -> list[dict]:
    path = os.path.join(SHELL, "fit", "sections.json")
    if not os.path.exists(path):
        return []
    return json.load(open(path))["rear"]["items"]


def near_hardware(lines: list, boxes: list[dict]) -> list[str]:
    if not lines or not boxes:
        return []
    p = np.concatenate([np.array(line, float) for line in lines])
    out = set()
    for b in boxes:
        lo = np.array([b["box"][0], b["y"][0], b["box"][1]]) - NEAR_HARDWARE
        hi = np.array([b["box"][2], b["y"][1], b["box"][3]]) + NEAR_HARDWARE
        if np.any(np.all((p >= lo) & (p <= hi), axis=1)):
            out.add(f"{b['solid']} ({b['role']})")
    return sorted(out)


# ---------- proposal.md ----------

def fmt(v: float) -> str:
    return f"{v:.0f}"


def proposal(meas: dict, opts: dict, d: Blueprint) -> str:
    tree, fids = face_cloud(d)
    boxes = hardware_boxes()
    lim = meas["printer"]
    L = []
    w = L.append
    w("# Seam proposal for the printed shell")
    w("")
    w(f"Date: {date.today().isoformat()}. Status: a proposal for the owner. Nothing is cut or joined in the model yet. "
      "This file is written by `cad/tools/draw_split.py` from the seam data in `cad/candybar/shell/split.py` and the "
      "cut that `candybar.shell.split` makes. Do not edit it by hand.")
    w("")
    w("Drawings: `options.png` (all three options) and `option-A.png`, `option-B.png`, `option-C.png` (larger). Renders: "
      "`renders/<option>/three-quarter-front-left.png` and `three-quarter-rear-left.png`, each piece in its own soft tint. "
      "On the drawings a blue seam lies in a design line and a red seam lies on an open face. A thin dashed line is a "
      "seam behind the surface that the view shows.")
    w("")
    w("## What decides the seams")
    w("")
    w("**Finish.** The brief makes the shell a painted shell, not raw PETG. Section 5 of its checklist: \"Remove "
      "electronics and glass before sanding or painting. Fill only permanent seams and apply the coupon-proven finish.\" "
      "The finishing steps: \"Dry-fit and stabilize the assembly; level only the necessary ridges; fill small defects "
      "with a tested compatible product; prime and guide-coat; sand according to the coating instructions; then apply "
      "color, graphics and optional clear.\" And: \"Keep permanent filled seams within cosmetic subassemblies; do not "
      "fill joints needed to remove the monitor, controls or computer.\"")
    w("")
    w("So a seam that is bonded for good is filled and painted, and in the finished cabinet it does not show. Two "
      "things still make its place matter. A filled seam on a thin PETG wall can show again as a fine line when the "
      "wall flexes or the temperature changes (the brief asks for a finished, two-piece coupon to test this), and the "
      "brief says: \"Put seams away from high-load palm-rest and joystick areas.\" A seam that opens again is never "
      "filled, so it must lie in a line of the design. Thus every option puts the service seams in design lines, and "
      "puts the bonded seams in design lines where it can, and where it cannot, at a place where a line would look "
      "deliberate if it shows.")
    w("")
    w(f"**Printer.** {lim['source']}: {lim['xy']:.0f} x {lim['xy']:.0f} mm on the bed, {lim['z']:.0f} mm high (the bed is "
      f"{lim['bed']:.0f}). A piece may turn on the bed (yaw) to fit; the box in the tables is the box after that turn. "
      f"The body is 494.7 wide. Half of it is 247.4, which is more than {lim['xy']:.0f}: a full-width part needs three "
      "pieces across, whatever the option. Only parts narrower than 480 (the hood, the rear wall, the door) can be two "
      "halves.")
    w("")
    w("**Lines that the form already has** (face IDs of `docs/blueprint/index.md`), where a seam can hide:")
    w("")
    for line in ("the level groove between hood and body: FB5 / HC15 (already a gap: the hood's service joint)",
                 "the reveal round the bezel plate: BZ4 (the plate's joint); its bottom and top corners on the rail land RL1",
                 "the pocket round the control panel: DK8; the opening under the panel; the panel's front corners where its "
                 "front turns to the flank (x = +-136.8)",
                 "the crease of the deck front where the centre face DK4 turns 8 degrees to the flank DK5 (x = +-138.5)",
                 "the crease of the edge section at the bottom of the band (DK3 / DK4..DK7, RL3 / RL4), 24 mm below the "
                 "top, round the deck and up the rail",
                 "the foot of the sweep FB1 (y 207), where the deck top starts to rise",
                 "the outer and inner crease of the step RB2 (leaning 28 degrees)",
                 "the creases of the rear slope RB4 (z 310 and 350) and the rear corners (RB1 / RB3)",
                 "the outline of the rear door in RB3 (fit study: 446.7 x 186)",
                 "the bays of the hood band: the gaps between the logo form LG1 and the speaker forms SP1 (x = +-88 to +-106)",
                 "the hood's own edges: the sill HC3 / ledge HC12, the soffit HC10, the leg's inner wall HC11",
                 "under-edges and the base FL1, and the back"):
        w(f"- {line}")
    w("")
    w("## The three options at a glance")
    w("")
    w("| Option | Printed pieces | Largest piece (print box, mm) | All fit | Seams on open faces |")
    w("| --- | --- | --- | --- | --- |")
    for key, opt in opts.items():
        res = meas["options"][key]
        printed = {n: r for n, r in res["pieces"].items() if r["module"] != "base"}
        big = max(printed.items(), key=lambda kv: max(kv[1]["x"], kv[1]["z"]))
        face = sorted({s["label"] for s in res["seams"].values() if s["cls"] == sp.FACE and s["module"] != "base"})
        w(f"| {opt.title} | {len(printed)} (+ base) | {big[0]}: {fmt(big[1]['x'])} x {fmt(big[1]['y'])} x {fmt(big[1]['z'])} | "
          f"{'yes' if res['fits'] else 'NO'} | {', '.join(face)} |")
    w("")
    w("The base under the cabinet is the same in all three: nine printed tiles (seams BA1 to BA3, hidden) or one cut "
      "plate. The bezel plate is a question of its own (below).")
    w("")
    for key, opt in opts.items():
        res = meas["options"][key]
        lines_ = json.load(open(os.path.join(OUT, key, "seams.json")))
        w(f"## {opt.title}")
        w("")
        w(opt.idea)
        w("")
        w("### Pieces")
        w("")
        w("| # | Piece | Print box (mm) | Fits | On the bed | Skin (g) | Seen (cm2) | Seen face over 45 deg (cm2) | Shallow tops (cm2) | Why this way |")
        w("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        nums = piece_numbers(res["pieces"])
        pieces = {p.full: p for p in sp.expanded(opt)[1]}
        for n, r in res["pieces"].items():
            p = pieces[n]
            why = "" if p.side == "L" and pieces.get(n[:-1] + "R") else p.why
            w(f"| {nums.get(n, '')} | {n} | {fmt(r['x'])} x {fmt(r['y'])} x {fmt(r['z'])} | {'yes' if r['fits'] else '**no**'} | "
              f"{p.bed} | {r['mass_g']} | {r['seen']} | {r['overhang_seen']} | {r['terrace_seen']} | {why or 'as R'} |")
        total = sum(r["mass_g"] for r in res["pieces"].values())
        w("")
        w(f"Skin mass of all pieces: {total / 1000:.2f} kg of PETG at {sp.PETG_G_PER_CM3} g/cm3, solid 4 mm skin; ribs, "
          "flanges and splice plates are not in it. \"Seen face over 45 deg\" is the area of faces that a person sees and "
          "that would need support in this orientation; \"shallow tops\" are faces seen at 1 to 25 degrees from level, "
          "which show layer terraces. Mirrored pieces (R, L) are measured each.")
        if res["problems"]:
            w("")
            w("Problems of the cut: " + "; ".join(json.dumps(q) for q in res["problems"]))
        w("")
        w("### Seams")
        w("")
        w("| Seam | Class | Joint | Faces crossed | Seen length (mm) | Hardware within 18 mm | How it reads |")
        w("| --- | --- | --- | --- | --- | --- | --- |")
        done = set()
        for name, s in res["seams"].items():
            if s["side"] == "L":
                continue
            ls = lines_[name]["lines"]
            other = lines_.get(f"{s['label']} L", {}).get("lines", [])
            both = " (each side)" if other else ""
            near = near_hardware(ls + other, boxes)
            w(f"| {s['label']} | {sp.CLASS_WORDS[s['cls']]} | {s['joint']} | {', '.join(crossed(ls, tree, fids))} | "
              f"{s['seen_mm']:.0f}{both} | {', '.join(near) if near else 'none'} | {s['reads']} |")
            done.add(s["label"])
        for label, what, joint, words in sp.EXISTING:
            w(f"| {label} | in a design line | {joint} | {what} | existing | | {words} |")
        w("")
        w("### Joints")
        w("")
        used = sorted({s["joint"] for s in res["seams"].values()} | {"service"})
        for j in used:
            w(f"- **{j}**: {sp.JOINTS[j]}")
        w("")
        w(f"**What opens for service.** {opt.service}")
        w("")
        w(f"**Rear door.** {opt.door}")
        w("")
        w("**Assembly order.**")
        w("")
        for i, step in enumerate(opt.assembly, 1):
            w(f"{i}. {step}")
        w("")
        w(f"**Against it.** {opt.against}")
        w("")
    bz = meas["options"].get("bezel", {})
    w("## The bezel plate")
    w("")
    w("The plate is 434.7 x 305.4 on a face reclined 30 degrees. It is wider than the bed in every orientation, so a "
      "printed plate needs a seam. The owner wants four plates (16:9, 16:10, 4:3, vertical); the land is the same on "
      "all of them and the window differs.")
    w("")
    for k, title, words in sp.BEZEL_OPTIONS:
        w(f"{k}. **{title}.** {words}")
    w("")
    if bz:
        w("Measured for option 1 (the 16:10 plate of the outer form):")
        w("")
        w("| Piece | Print box (mm) | Fits | On the bed | Mass (g, solid) | Seen face over 45 deg (cm2) |")
        w("| --- | --- | --- | --- | --- | --- |")
        beds = {p.full: p.bed for p in sp.expanded(sp.BEZEL)[1]}
        for n, r in bz["pieces"].items():
            w(f"| {n} | {fmt(r['x'])} x {fmt(r['y'])} x {fmt(r['z'])} | {'yes' if r['fits'] else '**no**'} | {beds[n]} | "
              f"{r['mass_g']} | {r['overhang_seen']} |")
        w("")
    w(f"Recommendation: option {sp.BEZEL_RECOMMENDED}. It keeps the accepted form of the land and the inner frame, prints "
      "without support with the arc smooth, and is the fewest pieces. The seam on the centre line is on the black "
      "plate, filled and painted with it; the plate is one part for the owner. A plate for another aspect ratio is "
      "the same two pieces with another window.")
    w("")
    w("## The rear door")
    w("")
    w(f"The fit study proposes an opening of {meas['door']['w']:.1f} x {meas['door']['h']:.0f} (z {meas['door']['z0']:.0f} "
      f"to {meas['door']['z1']:.0f}). It is wider than the bed, so the door is two or three pieces. The compute module "
      "(its backplate spans x -178 to 129) and the fan vent (x -14 to 111) bridge any split, so the door pieces are "
      "bonded on an inner frame into one rigid door, and only the door's outline opens.")
    w("")
    for key, opt in opts.items():
        w(f"- {opt.title}: {opt.door}")
    w("- In every option: a cut aluminium door (one piece, with the vents cut) is an alternative to a printed one. "
      "It is stiffer and carries the compute module with no splice.")
    w("")
    w("## Recommendation")
    w("")
    w("**Option A**, with the door of B if the owner wants fewer pieces on the door. Reasons:")
    w("")
    w("- Looks: every service seam and most bonded seams lie in a line that the form has. The seams that cross an "
      "open face are short, mirrored and in line with something the eye already reads: the panel's front corners on "
      "the apron, the hood's bays on the brow and the back, the bezel's bottom corner and the slope crease as two "
      "level lines round the body. None is on the centre line of the front.")
    w("- Print: the hood's centre piece is a straight extrusion and prints with no support and no layer steps; the "
      "side pieces print upright with level layer lines on the sides. The pieces that are seen most (deck front, "
      "apron, rails) have no seen face over 45 degrees (see the tables).")
    w("- Count: 24 printed pieces against 21 for B. The three that B saves cost a seam in the middle of the hood's "
      "top bar, right above the marquee, and a hood that prints with support across the marquee opening.")
    w("- C is the build to choose if the owner does not want filler at all, or wants every panel to come off. It "
      "costs six more pieces and an inner frame that is not designed.")
    w("")
    w("## Questions for the owner")
    w("")
    w("1. Finish: fill and paint the bonded seams (A, B), or keep every seam dry as a crisp shadow line (C)? This "
      "decides between A and C more than anything else.")
    w("2. Option A, B or C? And if A: the door in three pieces in line with the bays of the back, or two halves?")
    w("3. The two level lines L1 (at the bezel's bottom corner, z 134) and B1 (at the slope crease, z 310) cross the "
      "side band, where a stripe decal may go. Is a seam under the stripe acceptable, or should the stripe's edge "
      "follow L1?")
    w("4. The apron lines P1 at x = +-137 are below the screen, in line with the panel's front corners. Accept, or "
      "move them to the panel's side edges (x = +-199)? The second puts a 398 mm centre piece on the bed, which does "
      "not fit, so the apron would then need a seam on the centre line.")
    w("5. Base: nine printed tiles, or one cut plate (plywood or aluminium) that also stiffens the cabinet and "
      "carries the feet?")
    w("6. Bezel: option 1 (two halves, a filled seam on the centre line of the black plate), or option 3 (a cut "
      "sheet, which changes the land)?")
    w("7. The usable bed: printer.csv gives 240 (bed less brim, provisional, to be confirmed with a 240 x 240 test "
      "print). If the test shows that 248 prints well, halves of 247.4 fit, and the deck and the apron could be two "
      "pieces with a centre seam. Do you want that tested?")
    w("")
    w("## How the numbers were made, and what is not checked")
    w("")
    w("- The skin is the outer form less the cavity of `cavity.py` (4 mm, open under the panel and behind the bezel). "
      "The cavity is made of 1 mm slabs, so the inner face of the skin is stepped; the masses include this. The "
      "floor is the base, cut off along the cavity's outline.")
    w("- Each piece is the skin cut by the seam polygons of its option and named by a seed point. The print box is "
      f"the box of the piece's tessellation (0.5 mm) after the turn on the bed that makes its larger side smallest, in "
      f"steps of 0.5 degrees. The limits are those of params/printer.csv.")
    w("- \"Hardware within 18 mm\" uses the boxes of the fit study (`fit/sections.json`): a flange 12 mm deep behind "
      "the 4 mm skin, and 2 mm. It is a box test, so it can name an item that is near but not in the way.")
    w("- Not checked: the joints themselves (flanges, pins, splice plates and inserts are not modelled), the warp of "
      "the long thin pieces on the bed, the slicer's own estimate of time and supports, and the fillet of the rear "
      "corners that the detail pass will add (the corner seams of C lie in it).")
    w("")
    return "\n".join(L)


def main() -> None:
    meas = json.load(open(os.path.join(OUT, "measurements.json")))
    d = Blueprint()
    opts = {o.key: o for o in sp.options(d, meas["door"])}
    paths = [option_sheet(k, meas, opts[k]) for k in sp.OPTIONS_ORDER]
    stack(paths, os.path.join(OUT, "options.png"))
    text = proposal(meas, opts, d)
    with open(os.path.join(OUT, "proposal.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    print("draw_split:", os.path.relpath(os.path.join(OUT, "proposal.md"), REPO))


def render() -> None:
    for key in sp.OPTIONS_ORDER:
        out = os.path.join(OUT, "renders", key)
        cmd = [sys.executable, os.path.join(HERE, "render_views.py"), out, os.path.join(OUT, key),
               os.path.join(SHELL, "bezel.stl") + "=black", os.path.join(SHELL, "control_panel.stl") + "=black",
               os.path.join(SHELL, "screen.stl") + "=#3a4250", "--views", "three-quarter-front-left,three-quarter-rear-left",
               "--size", "1300"]
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "render":
        render()
    else:
        main()
