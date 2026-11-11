"""Draw the seam proposal from what candybar.shell.split wrote, and write proposal.md.

    cad/.venv-tools/bin/python cad/tools/draw_split.py            -> cad/out/shell-bp/split/options.png, option-*.png, proposal.md
    cad/.venv-tools/bin/python cad/tools/draw_split.py proposal   -> the same without the elevations (they take minutes)
    cad/.venv-tools/bin/python cad/tools/draw_split.py render     -> cad/out/shell-bp/split/renders/<option>/*.png (Blender)
    cad/.venv-tools/bin/python cad/tools/draw_split.py blueprint  -> docs/blueprint/10-split.svg, .png (the chosen layout)
                                                                     and 11-joints.svg, .png (the joint sheet)

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
    names = [n for n in rows if not n.startswith(("base", "floor"))]
    return {n: i + 1 for i, n in enumerate(names)}


def option_sheet(key: str, meas: dict, opt: sp.Option, path: str | None = None, svg: bool = False,
                 title: str | None = None) -> str:
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
    printed = {n: r for n, r in rows.items() if r["module"] != "base"}  # the floor tiles are module base
    big = max(printed.items(), key=lambda kv: max(kv[1]["x"], kv[1]["z"]))
    face = sorted({s["label"] for s in seams.values() if s["cls"] == sp.FACE and s["module"] != "base" and s["joint"] != "service"})
    service = sorted({s["label"] for s in seams.values() if s["joint"] == "service"} | {e[0] for e in sp.EXISTING})
    text = [f"{opt.title}", "", f"pieces printed: {len(printed)} (+ {len(rows) - len(printed)} printed floor tiles)",
            f"all pieces fit {meas['printer']['xy']:.0f} x {meas['printer']['xy']:.0f} x {meas['printer']['z']:.0f}: "
            f"{'yes' if res['fits'] else 'NO'}",
            f"largest: {big[0]}, {big[1]['x']:.0f} x {big[1]['y']:.0f} x {big[1]['z']:.0f}", "",
            f"bonded seams on open faces (filled): {', '.join(face)}", f"service seams: {', '.join(service)}", ""]
    for n, i in numbers.items():
        r = rows[n]
        text.append(f"{i:>2} {n:<22.22s} {r['x']:>4.0f} x {r['y']:>4.0f} x {r['z']:>4.0f} {'' if r['fits'] else ' NO'}")
    ax.text(0.0, 1.0, "\n".join(text), fontsize=7.0, family="DejaVu Sans Mono", va="top", ha="left", transform=ax.transAxes)
    ax.plot([0.02, 0.1], [0.04, 0.04], color=CLASS_COLOUR[sp.HIDDEN], lw=2, transform=ax.transAxes)
    ax.text(0.12, 0.04, "seam in a design line", fontsize=7.5, va="center", transform=ax.transAxes)
    ax.plot([0.02, 0.1], [0.015, 0.015], color=CLASS_COLOUR[sp.FACE], lw=2, transform=ax.transAxes)
    ax.text(0.12, 0.015, "seam on an open face (dashed: behind)", fontsize=7.5, va="center", transform=ax.transAxes)
    fig.suptitle(title or f"Seam proposal {opt.title}  (mm; the numbers are the pieces in the list)", fontsize=13, y=0.99)
    path = path or os.path.join(OUT, f"option-{key}.png")
    fig.savefig(path, dpi=115, bbox_inches="tight")
    if svg:
        fig.savefig(os.path.splitext(path)[0] + ".svg", dpi=115, bbox_inches="tight")
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

def face_cloud(d: Blueprint, step: float = 4.0, cap: int = 60):
    """Points on every labelled face of the blueprint, about step apart (at most cap x cap on one triangle), with the
    face ID of each, in a k-d tree."""
    from scipy.spatial import cKDTree

    tri, ids = db.triangles_of(pr.faces(d))
    pts, out_ids = [], []
    for t, fid in zip(tri, ids):
        edge = max(np.linalg.norm(t[1] - t[0]), np.linalg.norm(t[2] - t[1]), np.linalg.norm(t[0] - t[2]))
        n = int(min(cap, max(1, np.ceil(edge / step))))
        i, j = np.meshgrid(np.arange(n + 1), np.arange(n + 1))
        keep = i + j <= n
        u, v = i[keep] / n, j[keep] / n
        pts.append(t[0] + np.outer(u, t[1] - t[0]) + np.outer(v, t[2] - t[0]))
        out_ids += [fid] * len(u)
    return cKDTree(np.concatenate(pts)), np.array(out_ids, dtype=object)


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

def measurements() -> dict:
    """The per-option files of the cut, merged."""
    out = None
    for key in (*sp.ALL, "bezel"):
        one = json.load(open(os.path.join(OUT, f"measurements-{key}.json")))
        if out is None:
            out = one
        else:
            out["options"].update(one["options"])
    return out


def main(elevations: bool = True) -> None:
    import draw_structure as ds
    import split_proposal

    meas = measurements()
    d = Blueprint()
    opts = {o.key: o for o in sp.options(d, meas["door"])}
    if elevations:
        paths = [option_sheet(k, meas, opts[k]) for k in sp.OPTIONS_ORDER]
        stack(paths, os.path.join(OUT, "options.png"))
    if elevations or not os.path.exists(os.path.join(OUT, "chosen.png")):
        os.replace(option_sheet(sp.CHOSEN, meas, opts[sp.CHOSEN]), os.path.join(OUT, "chosen.png"))
        print("draw_split:", os.path.relpath(os.path.join(OUT, "chosen.png"), REPO))
    for k in sp.ALL:
        print("draw_split:", os.path.relpath(ds.structure_sheet(k, opts[k], d), REPO))
    print("draw_split:", os.path.relpath(ds.services_sheet(), REPO))
    print("draw_split:", os.path.relpath(ds.joints_sheet(), REPO))
    text = split_proposal.write(meas, opts, d, face_cloud, crossed, near_hardware, hardware_boxes())
    with open(os.path.join(OUT, "proposal.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    print("draw_split:", os.path.relpath(os.path.join(OUT, "proposal.md"), REPO))


def blueprint() -> None:
    """The tracked sheets of the split: the chosen layout (10) and the joints (11), from the cut and joints.py."""
    import draw_structure as ds

    meas = measurements()
    opt = next(o for o in sp.options(Blueprint(), meas["door"]) if o.key == sp.CHOSEN)
    option_sheet(sp.CHOSEN, meas, opt, os.path.join(db.OUT, "10-split.png"), svg=True,
                 title=f"Blueprint 10: the split that the owner chose on 2026-11-11, {opt.title} (mm; the numbers are the "
                       "pieces in the list; the nine floor tiles have no number). Flanges, keys, ribs, carriers and grips are not "
                       "modelled yet.")
    print("draw_split:", os.path.relpath(ds.joints_sheet(db.OUT, "11-joints", svg=True), REPO))


def render(keys=(sp.CHOSEN,)) -> None:
    for key in keys:
        out = os.path.join(OUT, "renders", key)
        cmd = [sys.executable, os.path.join(HERE, "render_views.py"), out, os.path.join(OUT, key),
               os.path.join(SHELL, "bezel.stl") + "=black", os.path.join(SHELL, "control_panel.stl") + "=black",
               os.path.join(SHELL, "screen.stl") + "=#3a4250", "--views", "three-quarter-front-left,three-quarter-rear-left",
               "--size", "1300"]
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "render":
        render()
    elif len(sys.argv) > 1 and sys.argv[1] == "blueprint":
        blueprint()
    else:
        main(elevations=not (len(sys.argv) > 1 and sys.argv[1] == "proposal"))
