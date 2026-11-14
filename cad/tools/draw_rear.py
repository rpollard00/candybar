"""The drawings of the rear: the elevation, the sections through the door, and the close-ups of its joint, its
fastening and the openings of the lower rear wall.

It reads cad/out/shell-rev7/rear/sections.json and report.json (candybar.shell.rear writes them) and writes PNG
sheets into cad/out/shell-rev7/rear/sheets. A section shows every outline that the cut plane makes in each part.

    cad/.venv-tools/bin/python cad/tools/draw_rear.py [out directory of the rear]

Needs matplotlib and numpy (cad/.venv-tools); no FreeCAD.
"""
from __future__ import annotations

import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, PathPatch, Rectangle  # noqa: E402
from matplotlib.path import Path  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REAR = os.path.join(os.path.dirname(HERE), "out", "shell-rev7", "rear")
INK, MUTED, DASH = "#1c1c20", "#6a6a72", (0, (4, 3))
FILL = {"door": "#f0dfae", "rail": "#d8a94e", "shroud": "#c9853a", "duct": "#b0603a", "fan": "#5a606c", "seal": "#86abd0", "board": "#4f8a3a",
        "heatsink": "#aab1bb", "io": "#8a8f99", "psu": "#70757f", "shell": "#d4d6da"}
WORDS = {"door": "door", "rail": "head rail", "shroud": "shroud", "duct": "duct", "fan": "fan", "seal": "foam seal", "board": "board",
         "heatsink": "heatsink", "io": "I/O connectors", "psu": "power supply", "shell": "shell"}


def kind(name: str) -> str:
    return next((k for k in ("seal", "door", "rail", "shroud", "duct", "fan", "board", "heatsink", "io", "psu") if k in name), "shell")


def inside(pt, loop) -> bool:
    x, y = pt
    hit = False
    for (x0, y0), (x1, y1) in zip(loop, np.roll(loop, -1, axis=0)):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            hit = not hit
    return hit


def patch(loops: list, colour: str, flip: bool = False) -> PathPatch | None:
    """The loops of one part in a section as one patch; a loop inside another one is a hole."""
    loops = [np.array(q, float) for q in loops if len(q) >= 3]
    if not loops:
        return None
    if flip:
        loops = [q * (-1.0, 1.0) for q in loops]
    verts, codes = [], []
    for i, q in enumerate(loops):
        depth = sum(1 for j, other in enumerate(loops) if j != i and inside(q[0], other))
        area = 0.5 * float(np.sum(q[:-1, 0] * q[1:, 1] - q[1:, 0] * q[:-1, 1]))
        if (area > 0) != (depth % 2 == 0):
            q = q[::-1]
        verts += [*q, q[0]]
        codes += [Path.MOVETO, *[Path.LINETO] * (len(q) - 1), Path.CLOSEPOLY]
    return PathPatch(Path(verts, codes), facecolor=colour, edgecolor=INK, linewidth=0.5)


def draw_section(ax, sec: dict, xlim, ylim, title: str, flip: bool = False, legend: bool = True, beside: bool = False) -> None:
    seen = []
    for name, loops in sec["parts"].items():
        k = kind(name)
        if (p := patch(loops, FILL[k], flip)) is not None:
            ax.add_patch(p)
            if k not in seen:
                seen.append(k)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.set_title(f"{title} ({sec['axis']} = {sec['at']:g})", fontsize=9, loc="left")
    ax.tick_params(labelsize=7)
    ax.grid(True, color="#e6e6ea", linewidth=0.4)
    ax.set_axisbelow(True)
    if legend:
        handles = [Rectangle((0, 0), 1, 1, facecolor=FILL[k], edgecolor=INK, linewidth=0.5) for k in seen]
        where = {"loc": "center left", "bbox_to_anchor": (1.02, 0.5), "ncol": 1} if beside else {"loc": "lower left", "ncol": 2}
        ax.legend(handles, [WORDS[k] for k in seen], fontsize=6.5, framealpha=0.9, **where)


def note(ax, at, text: str, to=None, size: float = 7.0) -> None:
    if to is None:
        ax.text(*at, text, fontsize=size, color=INK, va="center")
    else:
        ax.annotate(text, xy=to, xytext=at, fontsize=size, color=INK, va="center", arrowprops={"arrowstyle": "-", "color": MUTED, "linewidth": 0.6})


def dim(ax, a, b, text: str, off=(0.0, 0.0), size: float = 6.5) -> None:
    ax.annotate("", xy=a, xytext=b, arrowprops={"arrowstyle": "<->", "color": MUTED, "linewidth": 0.6, "shrinkA": 0, "shrinkB": 0})
    ax.text((a[0] + b[0]) / 2 + off[0], (a[1] + b[1]) / 2 + off[1], text, fontsize=size, color=MUTED, ha="center", va="center",
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.4})


def loops_of(ax, loops, colour=INK, lw=0.6, fill=None, sign=-1.0) -> None:
    for q in loops:
        a = np.array(q, float) * (sign, 1.0)
        if fill:
            ax.fill(a[:, 0], a[:, 1], color=fill, zorder=3)
        ax.plot(a[:, 0], a[:, 1], color=colour, linewidth=lw, zorder=4)


def rect(ax, box, sign=-1.0, **kw) -> None:
    x0, x1, z0, z1 = box
    xs = sorted((sign * x0, sign * x1))
    ax.add_patch(Rectangle((xs[0], z0), xs[1] - xs[0], z1 - z0, fill=kw.pop("fill", False), **kw))


def elevation(ax, data: dict, rep: dict, xlim, ylim, title: str, words: bool = True) -> None:
    """The rear seen from behind: the cabinet's right side is at the left of the picture."""
    r, fr, v = data["rear"], data["frame"], data["values"]
    half, shelf = r["rear_half"], r["shelf"]
    ax.plot([-half, -half, half, half], [shelf, 0, 0, shelf], color=INK, linewidth=0.9)
    ax.plot([-half, half], [shelf, shelf], color=MUTED, linewidth=0.6)
    cx, z0, pitch, h, count = r["cut_ins"]
    for k in range(int(count)):
        for s in (1, -1):
            rect(ax, (s * cx, s * half, z0 + k * pitch, z0 + k * pitch + h), edgecolor=MUTED, linewidth=0.6)
    rect(ax, r["opening"], edgecolor=INK, linewidth=0.9)
    rect(ax, r["door"], edgecolor=INK, linewidth=0.6, fill=True, facecolor="#f6efd9", zorder=1)
    rect(ax, r["ring"][:2] + [r["ring"][2], fr["z_head"]], edgecolor=MUTED, linewidth=0.5, linestyle=DASH)
    ax.plot([0, 0], [fr["zd0"], fr["zd1"]], color=INK, linewidth=0.5)
    for key in ("fan_vent", "hot_vent"):
        loops_of(ax, r[key], fill="#30333a")
    loops_of(ax, r["inlet"], fill="#30333a")
    rect(ax, r["psu_face"], edgecolor=MUTED, linewidth=0.5, linestyle=DASH)
    for loops in r["supply"].values():
        loops_of(ax, loops, fill="#30333a")
    for name, box in r["psu_features"].items():
        if "vent" not in name:
            rect(ax, box, edgecolor="#e0a030", linewidth=0.7, zorder=5)
    ax.add_patch(Circle((-r["psu_led"][0], r["psu_led"][1]), 1.2, color="#e0a030", zorder=5))
    for x, z in r["screws"]:
        ax.add_patch(Circle((-x, z), r["screw_hole"] / 2, fill=False, edgecolor=INK, linewidth=0.6, zorder=5))
    for x, z in r["fasteners"]:
        ax.add_patch(Circle((-x, z), v["qt_head"] / 2, facecolor="#9aa0a8", edgecolor=INK, linewidth=0.6, zorder=5))
        ax.plot([-x - 4, -x + 4], [z, z], color=INK, linewidth=1.0, zorder=6)
    for x, z in r["cones"]:
        ax.add_patch(Circle((-x, z), 4.0, fill=False, edgecolor=MUTED, linewidth=0.5, linestyle=DASH, zorder=5))
    fx, fz, fd = r["fan"]
    ax.add_patch(Circle((-fx, fz), fd / 2, fill=False, edgecolor=MUTED, linewidth=0.5, linestyle=DASH))
    dx0, dx1, dz0, dz1 = r["duct_inside"]
    rect(ax, (dx0, dx1, dz0, dz1), edgecolor=MUTED, linewidth=0.5, linestyle=DASH)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=9, loc="left")
    ax.tick_params(labelsize=7)
    ax.set_xticks([t for t in ax.get_xticks() if xlim[0] <= t <= xlim[1]])
    ax.set_xticklabels(["0" if abs(t) < 1e-9 else f"{-t:g}" for t in ax.get_xticks()])
    if words:
        a = rep["areas"]
        note(ax, (-fx - 40, fr["z1"] + 22), f"fan vent: {a['fan']['free_mm2'] / 100:.1f} cm2, {a['fan']['share'] * 100:.1f} % of the fan's circle", (-fx, fz + fd / 2 - 6))
        hx = -(dx0 + dx1) / 2
        note(ax, (hx - 70, fr["z1"] + 36), f"hot-air vent: {a['hot']['free_mm2'] / 100:.1f} cm2", (hx, dz1 - 12))
        qx, qz = r["fasteners"][0]
        note(ax, (-qx - 52, fr["z1"] + 50), "quarter-turn fastener", (-qx, qz + 4))
        ax.text(-r["psu_face"][0], 104, f"supply: grille {a['supply']['grille_mm2'] / 100:.1f} cm2, socket, switches, four screws", fontsize=7, color=INK,
                va="center", ha="right")
        note(ax, (-half + 6, 104), f"inlet: {a['inlet']['free_mm2'] / 100:.1f} cm2")
        dim(ax, (-r["opening"][0], fr["z0"] - 7), (-r["opening"][1], fr["z0"] - 7), f"opening {2 * fr['x_open']:.1f} x {fr['z1'] - fr['z0']:g}; door {2 * fr['x_door']:.1f} x {fr['zd1'] - fr['zd0']:g}")


def sheet_rear(data: dict, rep: dict, out: str) -> str:
    fig, ax = plt.subplots(figsize=(13.5, 8.6))
    elevation(ax, data, rep, (-250, 250), (-6, 350), "The rear, seen from behind, with the door on (x of the cabinet on the scale; its right side is at the left)")
    fig.text(0.01, 0.01, "Dashed: the clear opening inside the land, the circle of the fan, the inside of the duct, the rear face of the supply, the "
             "cones behind the door. Orange: the socket, the rocker, the ECO switch and the LED of the supply (ESTIMATED positions).", fontsize=7, color=MUTED)
    path = os.path.join(out, "rear-elevation.png")
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return path


def sheet_sections(data: dict, rep: dict, out: str) -> str:
    s, fr, v = data["sections"], data["frame"], data["values"]
    fig = plt.figure(figsize=(14, 12.5))
    ax = fig.add_axes([0.05, 0.56, 0.92, 0.40])
    draw_section(ax, s["plan through the fan vent and the duct"], (-245, 245), (452, 546), "Plan section through the fan vent, the hot-air vent and the duct")
    note(ax, (-60, 520), "bars of the hot-air vent", (data["rear"]["duct_inside"][0] + 30, fr["y_out"] - 2))
    note(ax, (150, 470), "post and tongue of the land", (fr["x_ring"] + 3, fr["y_in"] - 2))
    note(ax, (-40, 500), "ribs at the centre line, bonded", (0, fr["y_in"] - 4))
    ax.set_xlabel("x, mm", fontsize=7)
    ax.set_ylabel("y, mm (the rear is at the top)", fontsize=7)
    ax2 = fig.add_axes([0.05, 0.05, 0.42, 0.45])
    draw_section(ax2, s["side through the fan vent"], (452, 548), (96, 300), "Side section through the middle slot of the fan vent", beside=True)
    note(ax2, (456, 285), "head rail, bonded behind the strip", (fr["y_in"] - 6, fr["z_rail0"] + 8))
    note(ax2, (456, 112), "lip on the sill, rib under it", (fr["y_lap"] - 1, fr["z_lip"] - 2))
    note(ax2, (500, 262), "head rib of the door", (fr["y_in"] - 10, fr["z_rib0"] + 3))
    ax2.set_xlabel("y, mm (the rear is at the right)", fontsize=7)
    ax2.set_ylabel("z, mm", fontsize=7)
    ax3 = fig.add_axes([0.55, 0.05, 0.42, 0.45])
    draw_section(ax3, s["side through the duct"], (452, 548), (96, 300), "Side section through the middle slot of the hot-air vent", beside=True)
    note(ax3, (456, 285), "duct: open to the door, foam on its rim", (fr["y_in"] - 12, 252))
    ax3.set_xlabel("y, mm (the rear is at the right)", fontsize=7)
    path = os.path.join(out, "rear-sections.png")
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return path


def sheet_joint(data: dict, rep: dict, out: str) -> str:
    s, fr, v = data["sections"], data["frame"], data["values"]
    q = rep["fastener"]
    fig, axes = plt.subplots(2, 3, figsize=(15, 10.5))
    ax = axes[0][0]
    draw_section(ax, s["side through the fan vent"], (519, 545), (94, 131), "Sill: the lip, the rib under it and the door's foot", legend=False)
    dim(ax, (fr["y_lap"], fr["z0"]), (fr["y_lap"], fr["z_lip"]), f"lip {v['lip_h']:g}", (-2.2, 0))
    dim(ax, (fr["y_out"] + 1.2, fr["z0"]), (fr["y_out"] + 1.2, fr["zd0"]), f"gap {v['door_gap']:g}", (0.2, 3.0))
    note(ax, (519.5, 129.5), f"hook: 45 degrees, {v['nose_gap']:g} clear")
    note(ax, (519.5, 96), "rear lower piece: rib with gusset, edge break R 1 on the sill")
    ax = axes[0][1]
    draw_section(ax, s["side through the fastener"], (519, 545), (254, 296), "Head: section through a quarter-turn fastener", legend=False)
    ax.plot([fr["y_in"] - v["rail_d"] - 4, fr["y_out"] + 4], [fr["zq"], fr["zq"]], color="#c03030", linewidth=0.7, linestyle=(0, (8, 3, 2, 3)))
    ax.add_patch(Rectangle((fr["y_out"], fr["zq"] - q["largest_head"] / 2), 2.5, q["largest_head"], facecolor="#9aa0a8", edgecolor=INK, linewidth=0.5, zorder=5))
    note(ax, (519.5, 294), f"hole in the door {q['door_hole']:g}, largest head {q['largest_head']:g}, grip {q['grip']:g}")
    note(ax, (519.5, 256), f"room of the receptacle {q['room'][0]:g} x {q['room'][1]:g} x {q['room'][2]:g}, hole in the web {q['web_hole']:g}")
    dim(ax, (fr["y_out"] + 3.6, fr["zq"]), (fr["y_out"] + 3.6, fr["zd1"]), f"{v['qt_below']:g}", (0.9, 0))
    ax = axes[0][2]
    draw_section(ax, s["side through the cone"], (519, 545), (254, 296), "Head: section through a locating cone", legend=False)
    note(ax, (519.5, 294), "cone of joints.py on the door, socket in the block of the rail")
    note(ax, (519.5, 256), f"tongue of the rail: the land of the head, {v['land']:g} wide")
    ax = axes[1][0]
    plan = s["plan through the fan vent and the duct"]
    draw_section(ax, plan, (194, 240), (518, 544), "Side of the opening: the tongue, the post and a cut-in", legend=False)
    dim(ax, (fr["x_ring"], 521), (fr["x_open"], 521), f"land {v['land']:g}", (0, 1.3))
    note(ax, (195, 542.6), f"gap {v['door_gap']:g}; edge break R 1 on the door and on the opening")
    note(ax, (216, 524), "cut-in (groove 1.5 deep)", (223, 539.2))
    ax = axes[1][1]
    draw_section(ax, plan, (-16, 16), (524, 544), "Centre line: the two halves, bonded, with their ribs", legend=False)
    note(ax, (-15.5, 525.5), f"rib {v['seam_rib_w']:g} x {v['seam_rib_d']:g} on each half; two dowel pins of 4 x {v['dowel_len']:g}")
    ax = axes[1][2]
    draw_section(ax, s["plan through the lower wall"], (-232, -60), (505, 545), "Lower wall, left: the supply behind its openings", legend=False)
    note(ax, (-228, 509), "grille, opening of the socket, opening of the switches (edge break R 1 on each rim)")
    for a in axes.flat:
        a.set_xlabel("mm", fontsize=7)
    fig.tight_layout()
    path = os.path.join(out, "rear-joint.png")
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return path


def sheet_low(data: dict, rep: dict, out: str) -> str:
    r = data["rear"]
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.2))
    half = r["rear_half"]
    elevation(axes[0], data, rep, (-r["psu_face"][1] - 8, half + 4), (0, 122), "The supply's openings, seen from behind", words=False)
    elevation(axes[1], data, rep, (-half - 4, r["psu_face"][1] + 8), (0, 122), "The inlet for make-up air, seen from behind", words=False)
    a = rep["areas"]
    v = data["values"]
    note(axes[0], (-r["psu_face"][1] - 4, 113), f"slots {v['slot']:g} wide with round ends, bars {v['bar']:g}; grille {a['supply']['grille_mm2'] / 100:.1f} cm2")
    note(axes[0], (-r["psu_face"][1] - 4, 106), "orange: socket, rocker, ECO switch, LED (ESTIMATED); dashed: the supply's rear face 150 x 86")
    need = ", ".join(f"{x / 100:.1f} cm2 at {k}" for k, x in a["inlet"]["need_mm2"].items())
    note(axes[1], (-half, 113), f"inlet: {a['inlet']['free_mm2'] / 100:.1f} cm2 free; need {need}")
    fig.tight_layout()
    path = os.path.join(out, "rear-lower-wall.png")
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return path


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else REAR
    data = json.load(open(os.path.join(root, "sections.json"), encoding="utf-8"))
    rep = json.load(open(os.path.join(root, "report.json"), encoding="utf-8"))
    out = os.path.join(root, "sheets")
    os.makedirs(out, exist_ok=True)
    for make in (sheet_rear, sheet_sections, sheet_joint, sheet_low):
        print(make(data, rep, out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
