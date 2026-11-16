"""The pictures of the larger-monitor study (docs/research/larger-monitor.md).

It reads the files of candybar.shell.monitor_study (front.json, cuts.json) from cad/out/larger-monitor and writes
there: front.png (the front of the cabinet, square to the screen face, with the present screen and three candidates
at one scale, each with its 16:9, 4:3 and tate window), section-side.png and section-above.png (the screen zone cut
on the centre line and across the face, with the limits and the outlines of the candidates), and pictures.md (the
table of the pictures).

    cad/.venv-tools/bin/python cad/tools/draw_larger_monitor.py
"""
from __future__ import annotations

import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from candybar.shell import monitor_pictures as mp  # noqa: E402

OUT = os.environ.get("CANDYBAR_OUT") or os.path.join(ROOT, "out", "larger-monitor")
SHOWN = ("present", "p18", "b19w", "b19")
TINT = {"present": "#3a4250", "p18": "#1f77b4", "b19w": "#d62728", "b19": "#2ca02c", "o19": "#9467bd"}
WINDOW = {"16:9": "#0b5fd0", "4:3": "#e07000", "tate 3:4": "#0a8a3a"}
UNIT = {u.key: u for u in mp.UNITS}


def rect(ax, w, h, cx=0.0, cy=0.0, **kw):
    ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, **kw))


def front() -> None:
    edges = json.load(open(os.path.join(OUT, "front.json"), encoding="utf-8"))
    base = {k: mp.diagonal_in(*p) for k, p in mp.pictures(UNIT["present"]).items()}
    fig, axs = plt.subplots(2, 2, figsize=(22, 25))
    for ax, key in zip(axs.flat, SHOWN):
        u = UNIT[key]
        for group, lw, colour in (("outline", 0.9, "#000000"), ("sharp", 0.6, "#202020"), ("smooth", 0.3, "#707070"), ("sewn", 0.3, "#707070")):
            for line in edges.get(group, []):
                ax.plot([p[0] for p in line], [p[1] for p in line], color=colour, linewidth=lw, solid_capstyle="round")
        rect(ax, *mp.OPENING, facecolor="#101010", edgecolor="none", zorder=3)
        rect(ax, u.w, min(u.h, mp.OPENING[1]), cy=-u.up if u.h < mp.OPENING[1] else 0.0, facecolor="#5a5f6a", edgecolor="none", zorder=4)
        lit = (min(u.lit_w, mp.OPENING[0]), min(u.lit_h, mp.OPENING[1]))
        rect(ax, *lit, facecolor="#cfe3f7", edgecolor="none", zorder=5)
        rect(ax, *mp.OPENING, fill=False, edgecolor="#c00000", linewidth=1.6, linestyle=(0, (6, 3)), zorder=9)
        pics = mp.pictures(u)
        notes = []
        for name, colour in WINDOW.items():
            w, h = pics[name]
            rect(ax, w, h, fill=False, edgecolor=colour, linewidth=2.6, zorder=8)
            d = mp.diagonal_in(w, h)
            notes.append((colour, f"{name}:  {d:.1f} in   {w:.0f} x {h:.0f} mm   ({(d / base[name] - 1) * 100:+.0f} %)"))
        ax.plot([-100, 0], [-330, -330], color="#000000", linewidth=3)
        ax.text(-50, -322, "100 mm", ha="center", fontsize=11)
        ax.set_title(u.name + f"\nbody {u.w:g} x {u.h:g} x {u.t:g}, lit {u.lit_w:.1f} x {u.lit_h:.1f}", fontsize=15, loc="left")
        for i, (colour, text) in enumerate(notes):
            ax.text(-250, 437 - 22 * i, text, color=colour, fontsize=14, weight="bold")
        ax.set_xlim(-265, 265)
        ax.set_ylim(-345, 450)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.suptitle("The front of the cabinet, square to the screen face, at one scale. Red dashes: the opening behind the bezel plate, 434.7 x 293.4 (the shell).\n"
                 "Grey: the body of the unit. Pale blue: its lit picture. Frames: the largest window of each shape. In brackets: the diagonal against the present unit.",
                 fontsize=15, x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.955))
    fig.savefig(os.path.join(OUT, "front.png"), dpi=110)
    plt.close(fig)


def fill_cut(ax, cut: dict, hardware: dict, ix: int, iy: int, skip: tuple[str, ...] = ()) -> None:
    seen = set()
    for name, loops in cut.items():
        if name.startswith(skip):
            continue
        if name.startswith("skin_"):
            style = {"facecolor": "#b9b9b9", "edgecolor": "#000000", "label": "skin of the shell (cannot move)"}
        elif name in ("cradle_skin", "cradle_monitor", "cradle_plugs", "cradle_pads", "cradle_pins", "cradle_magnets", "cradle_screws"):
            continue
        elif name == "cradle_bezel_plate":
            style = {"facecolor": "#303030", "edgecolor": "#000000", "label": "bezel plate (a new plate for each window)"}
        elif name.startswith("cradle_"):
            style = {"facecolor": "#f0c060", "edgecolor": "#6a4a00", "label": "cradle: lugs, uprights, jaws, channels (inside parts)"}
        else:
            role = hardware.get(name[3:], {}).get("role")
            if name.startswith("hw_Monitor"):
                continue
            style = ({"facecolor": "#8fc98f", "edgecolor": "#1d5e1d", "label": "hardware"} if role == "hardware"
                     else {"facecolor": "none", "edgecolor": "#c08000", "linestyle": (0, (4, 2)), "label": "keep-out zone of the hardware"})
        label = style.pop("label")
        for loop in loops:
            if name.startswith("skin_"):
                ax.fill([p[ix] for p in loop], [p[iy] for p in loop], linewidth=0.8, zorder=2, fill=False, edgecolor="#000000")
            else:
                ax.fill([p[ix] for p in loop], [p[iy] for p in loop], linewidth=0.8, zorder=3, label=None if label in seen else label, **style)
                seen.add(label)
    # the skin: one compound path, so that the hollow of each wall section is not filled
    from matplotlib.patches import PathPatch  # noqa: PLC0415
    from matplotlib.path import Path  # noqa: PLC0415
    verts, codes = [], []
    for name, loops in cut.items():
        if name.startswith("skin_"):
            for loop in loops:
                verts += [(p[ix], p[iy]) for p in loop]
                codes += [Path.MOVETO] + [Path.LINETO] * (len(loop) - 2) + [Path.CLOSEPOLY]
    patch = PathPatch(Path(verts, codes), facecolor="#b9b9b9", edgecolor="#000000", linewidth=0.8, zorder=1, label="skin of the shell (cannot move)")
    patch.get_path().should_simplify = False
    ax.add_patch(patch)


def dim(ax, a, b, text, off=(0, 0), colour="#c00000", ha="center") -> None:
    ax.annotate("", xy=a, xytext=b, arrowprops={"arrowstyle": "<->", "color": colour, "linewidth": 1.3}, zorder=20)
    ax.text((a[0] + b[0]) / 2 + off[0], (a[1] + b[1]) / 2 + off[1], text, color=colour, fontsize=11, ha=ha, va="center", zorder=21,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 1.5})


def sections() -> None:
    cuts = json.load(open(os.path.join(OUT, "cuts.json"), encoding="utf-8"))
    fr = cuts["frame"]
    c, up, into = fr["c"], fr["up"], fr["into"]

    def yz(v, t):
        return c[1] + up[1] * v + into[1] * t, c[2] + up[2] * v + into[2] * t

    # from the side, on the centre line, as the cabinet stands
    fig, ax = plt.subplots(figsize=(20, 20))
    fill_cut(ax, cuts["side"]["50"], cuts["hardware"], 3, 4)
    for key in SHOWN + ("o19",):
        u = UNIT[key]
        g = mp.glass_t(u.w, u.h)
        v0 = -u.up - u.h / 2
        pts = [yz(v0, g), yz(v0 + u.h, g), yz(v0 + u.h, g + u.t), yz(v0, g + u.t)]
        ax.fill([p[0] for p in pts], [p[1] for p in pts], facecolor=TINT[key], alpha=0.25 if key != "present" else 0.6, edgecolor=TINT[key], linewidth=2.0, zorder=10,
                label=f"{u.name}: {u.h:g} high, {u.t:g} thick")
    def label(v, t, text, colour, ha="center"):
        ax.text(*yz(v, t), text, color=colour, fontsize=12, ha=ha, va="center", zorder=21, bbox={"facecolor": "white", "edgecolor": colour, "pad": 3})

    def span(v0, t0, v1, t1, colour):
        a, b = yz(v0, t0), yz(v1, t1)
        ax.plot([a[0], b[0]], [a[1], b[1]], color=colour, linewidth=1.6, marker="o", markersize=5, zorder=20)

    span(-146.7, -30.0, 146.7, -30.0, "#c00000")
    label(0.0, -30.0, "1  opening, ledge to ledge: 293.4 (the shell)", "#c00000", ha="right")
    span(-135.6, -52.0, 135.6, -52.0, "#6a4a00")
    label(-40.0, -52.0, "2  between the lugs: 271.2 (inside parts)", "#6a4a00", ha="right")
    span(-287.0, 72.0, 209.5, 72.0, "#005a9c")
    label(120.0, 72.0, "3  behind the ledges the cavity is free\nfrom 287 below to 209 above the centre\nof the image (the shell: sweep and hood)", "#005a9c", ha="left")
    span(40.0, 8.2, 40.0, 96.6, "#1d5e1d")
    label(40.0, 100.0, "4  from the glass to the keep-out zone\nof the compute module: 88.4 on this line,\n65.5 at its nearest point", "#1d5e1d", ha="left")
    label(165.0, -8.0, "5  the ledges are 4.0 thick and end\n11.2 behind the screen face", "#c00000", ha="right")
    ax.set_xlim(150, 640)
    ax.set_ylim(0, 560)
    ax.set_aspect("equal")
    ax.grid(True, linewidth=0.3, color="#c0c0c0")
    ax.set_xlabel("y, from the front edge of the deck to the rear (mm)")
    ax.set_ylabel("z, above the desk (mm)")
    ax.set_title("Section from the side, 50 right of the centre line (through two lugs of the cradle). The opening limits what shows; behind the ledges the cavity is free far past the opening.\n"
                 "A body higher than 291 lies behind the ledges, with its glass 12.4 behind the face (4.2 farther back than the present glass).", fontsize=14, loc="left")
    ax.legend(loc="lower right", fontsize=11, framealpha=0.95)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "section-side.png"), dpi=100)
    plt.close(fig)

    # across the face, through the centre of the image: x across, t behind the face (down the page is the front)
    fig, ax = plt.subplots(figsize=(22, 13))
    fill_cut(ax, cuts["face"]["0"], cuts["hardware"], 0, 2)
    for i, key in enumerate(SHOWN + ("o19",)):
        u = UNIT[key]
        g = mp.glass_t(u.w, u.h)
        ax.add_patch(Rectangle((-u.w / 2, g), u.w, u.t, facecolor=TINT[key], alpha=0.25 if key != "present" else 0.6, edgecolor=TINT[key], linewidth=2.0, zorder=10,
                               label=f"{u.name}: {u.w:g} wide, {u.t:g} thick"))
    p = UNIT["present"]
    for s in (1, -1):
        ax.add_patch(Rectangle((s * p.w / 2, 8.2), s * 22.0, p.t, facecolor="none", edgecolor="#3a4250", linestyle=(0, (3, 2)), linewidth=1.4, zorder=11,
                               label="plug room of the present unit, 22 each side" if s == 1 else None))
    dim(ax, (-217.34, -24), (217.34, -24), "1  opening between the jambs: 434.7 (the shell)", off=(0, -7))
    dim(ax, (-242.0, 84), (242.0, 84), "2  between the inner faces of the sides, behind the jambs: 484 (the shell); 464 at the top corners of a body 343 high", off=(0, 7), colour="#005a9c")
    dim(ax, (-120.0, 8.2), (-120.0, 119.7), "3  from the glass to the keep-out zone\nof the compute module: 111.5 on this line", off=(-78, 30), colour="#1d5e1d")
    ax.text(262, 5.6, "4  the jambs end\n11.2 behind\nthe face", color="#c00000", fontsize=11, ha="center", va="center")
    ax.set_xlim(-290, 290)
    ax.set_ylim(-40, 300)
    ax.set_aspect("equal")
    ax.grid(True, linewidth=0.3, color="#c0c0c0")
    ax.set_xlabel("x, across the cabinet (mm)")
    ax.set_ylabel("t, behind the screen face (mm)")
    ax.set_title("Section across the face through the centre of the image, seen from above (the front is at the bottom).\n"
                 "A body up to 432.7 wide goes into the opening. A wider body must lie behind the jambs, and the opening still shows 434.7 at most.", fontsize=14, loc="left")
    ax.legend(loc="upper center", fontsize=10.5, framealpha=0.95, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "section-above.png"), dpi=100)
    plt.close(fig)


ROWS = (("present", False, "Present unit, 16.0 in 16:10"), ("present", True, "Present unit, turned 90 degrees"), ("p173", False, "17.3 in 16:9 portable"),
        ("p18", False, "A. 18 in 16:10 portable"), ("p18", True, "A, turned 90 degrees"), ("b185", False, "18.5 in 16:9, portable or panel"),
        ("b19w", False, "B. 19 in 16:10 panel"), ("b19", False, "C. 19 in 5:4: panel, open frame or desktop"), ("b17", False, "17 in 5:4 panel"),
        ("b15", False, "15 in 4:3 panel"))
COLUMNS = ("16:10", "16:9", "4:3", "tate 3:4", "tate 9:16")


def table() -> str:
    """The table of the document: a row for each unit of ROWS, a column for each shape of COLUMNS."""
    rows = {(r["key"], r["turned"]): r for r in mp.table()}
    lines = ["| Unit | " + " | ".join(COLUMNS) + " |", "| --- |" + " --- |" * len(COLUMNS)]
    for key, turned, name in ROWS:
        cells = []
        for n in COLUMNS:
            x = rows[(key, turned)]["cells"][n]
            cells.append(f"**{x['in']:.1f}** ({x['w']:.0f} x {x['h']:.0f}) {x['gain'] * 100:+.0f} %")
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    what = sys.argv[1:] or ["table", "sections", "front"]
    if "table" in what:
        open(os.path.join(OUT, "pictures.md"), "w", encoding="utf-8").write(table())
    if "sections" in what:
        sections()
    if "front" in what:
        front()


if __name__ == "__main__":
    main()
