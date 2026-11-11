"""The drawing of the joint coupon: coupon.png in the coupon's output directory.

    cad/.venv-tools/bin/python cad/tools/draw_coupon.py cad/out/coupon [--no-render]

Run it after candybar.shell.coupon has finished (one FreeCAD or Blender process at a time). It reads what candybar.shell.coupon wrote there: drawing.json (the sections across the joint, cut from the solids)
and assembled/*.stl (the pair at 0.2 in the assembled position). Panels: the section through a screw and the section
through the key, dimensioned; the two halves seen from the inside; the assembled pair. Unless --no-render, it first
renders the pair and the halves apart with render_views.py into renders/pair and renders/apart, and the drawing
uses the render of the pair.
"""
from __future__ import annotations

import json
import os
import struct
import subprocess
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

COL = {"lower": "#e8c39e", "upper": "#9ec5e8"}
INK, RED, BLUE = "#333333", "#c0281b", "#1f4e8c"


def load_stl(path: str) -> np.ndarray:
    data = open(path, "rb").read()
    n = struct.unpack("<I", data[80:84])[0]
    rec = np.frombuffer(data[84:84 + n * 50], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    return rec["v"].astype(float)


def save_stl(path: str, tris: np.ndarray) -> None:
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1), 1e-12)[:, None]
    rec = np.zeros(len(tris), dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    rec["n"], rec["v"] = n, tris
    with open(path, "wb") as fh:
        fh.write(b"candybar coupon".ljust(80, b" ") + struct.pack("<I", len(tris)) + rec.tobytes())


def render(out: str, tag: str, lower: np.ndarray, upper: np.ndarray) -> dict:
    """Renders of the pair and of the halves apart with tools/render_views.py (Blender, one process at a time)."""
    here = os.path.dirname(os.path.abspath(__file__))
    scratch = os.path.join(os.path.dirname(here), "out", "_scratch")
    mesh = os.path.join(out, "renders", "mesh")
    os.makedirs(mesh, exist_ok=True)
    save_stl(os.path.join(mesh, "lower.stl"), lower)
    save_stl(os.path.join(mesh, "upper.stl"), upper)
    save_stl(os.path.join(mesh, "upper-apart.stl"), upper + np.array([0, 0, 45.0]))
    env = os.environ | {"TMPDIR": scratch}
    done = {}
    for name, files in (("pair", ("lower.stl", "upper.stl")), ("apart", ("lower.stl", "upper-apart.stl"))):
        dest = os.path.join(out, "renders", name)
        specs = [f"{os.path.join(mesh, f)}={'#d9a877' if f.startswith('lower') else '#86b3dc'}" for f in files]
        cmd = [sys.executable, os.path.join(here, "render_views.py"), dest, *specs, "--views",
               "three-quarter-rear-left,three-quarter-front-left", "--size", "1100"]
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
        print(proc.stdout.strip() or proc.stderr.strip()[-1500:])
        if proc.returncode == 0:
            done[name] = dest
    return done


def dim(ax, p, q, text, off=(0.0, 0.0), size=7.0, color=RED) -> None:
    ax.annotate("", p, q, arrowprops=dict(arrowstyle="<->", color=color, lw=0.7, shrinkA=0, shrinkB=0))
    ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, color=color, fontsize=size, ha="center", va="center",
            bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.85))


def note(ax, at, text, to=None, size=6.8) -> None:
    if to is None:
        ax.text(*at, text, fontsize=size, color=BLUE, va="center")
    else:
        ax.annotate(text, to, at, fontsize=size, color=BLUE, va="center",
                    arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.5, shrinkA=1, shrinkB=1))


def draw_section(ax, sec: dict, j: dict, c: float, through: str, pilots: list[float] | None = None,
                 stations: list[float] | None = None) -> None:
    for name in ("lower", "upper"):
        for line in sec[name]:
            ax.add_patch(Polygon(np.array(line), closed=True, fc=COL[name], ec=INK, lw=0.7))
    w, fh, ft = j["wall_t"], j["flange_h"], j["flange_t"]
    ax.axhline(0, color="#888", lw=0.4, ls="--", zorder=0)
    ax.text(-7.2, 0.4, "seam plane", fontsize=6, color="#666")
    dim(ax, (0, -15), (w, -15), f"{w:g}", (0, -1.2))
    dim(ax, (w, -24.5), (w + fh, -24.5), f"flange {fh:g}", (0, -1.2))
    dim(ax, (w + fh + 2.5, -ft), (w + fh + 2.5, 0), f"{ft:g}", (1.6, 0))
    dim(ax, (w + fh + 2.5, 0), (w + fh + 2.5, ft), f"{ft:g}", (1.6, 0))
    ax.text(w + 3.8, -ft - 6.5, f"gusset {j['gusset_angle']:g}°", fontsize=7, color=RED)
    ax.text(-7.2, -20, "outer face", fontsize=6.5, color="#666", rotation=90)
    ax.text(-7.2, 9, "each half runs on\nto 60 from the seam", fontsize=6, color="#666")
    if through == "key":
        a, b = j["wall_t"] + j["key_u0"], j["wall_t"] + j["key_u0"] + j["key_w"]
        dim(ax, (a, 4.6), (b, 4.6), f"key {j['key_w']:g}", (0, 0.9))
        dim(ax, (b + 2.0, 0), (b + 2.0, j["key_proj"]), f"{j['key_proj']:g}", (1.4, 0))
        dim(ax, (a - c, -3.6), (b + c, -3.6), f"groove {j['key_w'] + 2 * c:.1f} (+{c:g} each side)", (0, -1.2))
        dim(ax, (a - 2.6, 0), (a - 2.6, j["key_proj"] + j["groove_extra_depth"]),
            f"{j['key_proj'] + j['groove_extra_depth']:g}", (-1.6, 0.9))
        note(ax, (-7, 15.5), f"V-groove {j['vgroove_w']:g} wide, {j['vgroove_d']:g} deep (outside)", (0.3, 0.2))
        note(ax, (8, 17), f"chamfer {j['groove_chamfer']:g} at the groove mouth\n(the upper half prints with this face on the bed)",
             (a - c - 0.15, 0.1))
        ax.set_title(f"Section through the key (middle of the arc), groove +{c:g}", fontsize=9)
    else:
        u = j["screw_u"]
        ax.plot([u, u], [-j["screw_l"] + ft, ft], color="#111", lw=2.2, zorder=5)
        ax.plot([u - 2.8, u + 2.8], [ft + 0.6, ft + 0.6], color="#111", lw=2.6, zorder=5)
        dim(ax, (0, ft + 14), (u, ft + 14), f"axis {u:g} from outside", (0, 1.1))
        dim(ax, (u - j["head_pocket_d"] / 2, ft + 9.5), (u + j["head_pocket_d"] / 2, ft + 9.5), f"pocket {j['head_pocket_d']:g}", (0, 1.1))
        dim(ax, (u + 5.8, -j["pilot_depth"]), (u + 5.8, 0), f"pilot {pilots[0]:g}\n{j['pilot_depth']:g} deep", (3.4, 0))
        note(ax, (-7, 19), f"screw {j['screw_d']:g} x {j['screw_l']:g} for plastics; every {j['screw_pitch']:g}", (u, 2))
        note(ax, (8, -29), f"clearance hole {j['clearance_d']:g}; counterbore {j['pilot_counterbore_d']:g} x {j['pilot_counterbore_depth']:g} on the pilot",
             (u + 1.7, 3))
        ax.set_title(f"Section through the screw at {stations[0]:+.0f}: pilot {pilots[0]:g} (at {stations[1]:+.0f}: {pilots[1]:g})", fontsize=9)
    ax.set_xlim(-9, 26)
    ax.set_ylim(-31, 24)
    ax.set_aspect("equal")
    ax.set_xlabel("inward from the outer face (mm)", fontsize=7)
    ax.set_ylabel("from the seam plane (mm)", fontsize=7)
    ax.tick_params(labelsize=6)
    ax.grid(color="#eee", lw=0.4)


def shade(ax, tris: np.ndarray, colour: str, rot: np.ndarray, light=(0.3, -0.5, 0.8)) -> None:
    """Draw triangles projected by rot (rows: screen right, screen up, toward the viewer), far ones first."""
    p = tris @ rot.T
    n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
    ln = np.linalg.norm(n, axis=1)
    keep = ln > 1e-12
    p, n = p[keep], n[keep] / ln[keep, None]
    facing = n[:, 2] > 0                     # STL triangles turn counter-clockwise seen from outside: cull the back faces
    p, n = p[facing], n[facing]
    l = np.array(light) / np.linalg.norm(light)
    k = np.clip(np.abs(n @ l), 0, 1)
    base = np.array(matplotlib.colors.to_rgb(colour))
    cols = np.clip(base[None, :] * (0.45 + 0.6 * k[:, None]), 0, 1)
    order = np.argsort(p[:, :, 2].mean(axis=1))
    ax.add_collection(PolyCollection(p[order][:, :, :2], facecolors=cols[order], edgecolors=cols[order], linewidths=0.2))


def view(az: float, el: float) -> np.ndarray:
    """Camera rows for a viewer at azimuth az (degrees from -y toward +x) and elevation el, looking at the origin."""
    a, e = np.radians(az), np.radians(el)
    toward = np.array([np.sin(a) * np.cos(e), -np.cos(a) * np.cos(e), np.sin(e)])
    right = np.cross(np.array([0, 0, 1.0]), toward)
    right /= np.linalg.norm(right)
    up = np.cross(toward, right)
    return np.array([right, up, toward])


def frame(ax, title: str) -> None:
    ax.autoscale_view()
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=9)
    ax.tick_params(labelsize=6)
    ax.grid(color="#eee", lw=0.4)


def main(out: str, renders: bool = True) -> int:
    d = json.load(open(os.path.join(out, "drawing.json")))
    j, c = d["joint"], d["clearance"]
    tag = f"c{round(c * 10):02d}"
    lower = load_stl(os.path.join(out, "assembled", f"lower-{tag}.stl"))
    upper = load_stl(os.path.join(out, "assembled", f"upper-{tag}.stl"))
    if renders:
        render(out, tag, lower, upper)
    fig = plt.figure(figsize=(18, 11.5))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1.0])
    draw_section(fig.add_subplot(gs[0, 0]), d["sections"]["screw"], j, c, "screw", d["pilots"], d["stations"])
    draw_section(fig.add_subplot(gs[0, 1]), d["sections"]["key"], j, c, "key")

    ax = fig.add_subplot(gs[0, 2])
    ax.axis("off")
    st = ", ".join(f"{s:+.0f}" for s in d["stations"])
    text = (f"Joint coupon: joint 1 on a wall of radius {d['radius']:g} (convex outside)\n\n"
            f"Each half: {d['length']:g} along the arc, {d['half']:g} from the seam to the free edge, skin {j['wall_t']:g}.\n"
            f"Pair: {d['length']:g} x {2 * d['half']:g}. The seam is a level line along the arc (as L1).\n\n"
            "Lower half (orange): the piece below the seam. Key, pilot holes,\n"
            "gusset under the flange, foot flange 12 x 4 at the free edge.\n"
            "Prints upright, seam at the top.\n\n"
            "Upper half (blue): the piece above the seam. Groove, clearance\n"
            "holes, head pockets. Prints upright, seam on the bed.\n\n"
            f"Groove clearance per side: 0.1, 0.2, 0.3 (drawn: {c:g}).\n"
            "Dots on the inside face: one for each 0.1.\n"
            f"Screws at {st} mm from the middle of the arc (pitch {j['screw_pitch']:g}).\n"
            f"Two pilot candidates: {d['pilots'][0]:g} at {d['stations'][0]:+.0f} (sunk bar under it, inside),\n"
            f"{d['pilots'][1]:g} at {d['stations'][1]:+.0f}. The repeated-drive test chooses one for the cabinet.\n"
            f"Key runs stop {j['key_gap']:g} each side of a screw and {j['key_end_margin']:g} from the ends.\n\n"
            "Sections and views are cut from the model (candybar.shell.coupon).")
    ax.text(0.0, 0.98, text, fontsize=8.5, va="top", family="DejaVu Sans")

    ax = fig.add_subplot(gs[1, 0:2])
    rot = view(180.0, 0.0)  # from the inside, looking out
    lift = np.array([0, 0, 18.0])
    shade(ax, lower, COL["lower"], rot)
    shade(ax, upper + lift, COL["upper"], rot)
    ax.text(0, 84, "upper half (lifted 18): groove, clearance holes, head pockets, two dots (+0.2)", ha="center", fontsize=7.5, color=BLUE)
    ax.text(0, -70, f"lower half: key runs, pilot holes ({d['pilots'][0]:g} with the bar, {d['pilots'][1]:g}), gusset, foot flange, two dots", ha="center", fontsize=7.5, color=BLUE)
    frame(ax, "The two halves of the +0.2 pair seen from the inside (mm)")
    ax.set_ylim(-75, 92)

    ax = fig.add_subplot(gs[1, 2])
    still = os.path.join(out, "renders", "pair", "three-quarter-rear-left.png")
    if os.path.exists(still):
        ax.imshow(plt.imread(still))
        ax.axis("off")
        ax.set_title("Assembled pair, from the inside (render)", fontsize=9)
    else:
        rot = view(205.0, 32.0)
        shade(ax, lower, COL["lower"], rot)
        shade(ax, upper, COL["upper"], rot)
        frame(ax, "Assembled pair, from the inside and above")

    fig.suptitle("Joint coupon for joint 1 (mm). Dimensions from cad/candybar/shell/joints.py", fontsize=12)
    fig.tight_layout()
    path = os.path.join(out, "coupon.png")
    fig.savefig(path, dpi=110)
    plt.close(fig)
    print(f"draw_coupon: {path}")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.exit(main(args[0] if args else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "coupon"),
                  renders="--no-render" not in sys.argv))
