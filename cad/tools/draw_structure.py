"""The structure sheets, the sheet of cable routes and air path, the joint sheet, and the width study of the seam
proposal. draw_split.py calls these; they read what candybar.shell.split and candybar.shell.structure wrote.

    cad/.venv-tools/bin/python cad/tools/draw_split.py   (draws these too)

structure-<option>.png  a side view and a plan of the cavity with the hardware boxes of the fit study, and the
                        floor, ring frames, cross-members, ribs, frame members and mounts in colour
services.png            the cable routes and the air path, with the plugs at the parts that open
joints.png              dimensioned sections of the joints, and the coupon pair
"""
from __future__ import annotations

import json

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(HERE)
sys.path.insert(0, CAD)
sys.path.insert(0, HERE)
import draw_blueprint as db  # noqa: E402
from candybar.shell import split as sp  # noqa: E402
from candybar.shell import structure as st  # noqa: E402
from candybar.shell.dims import Blueprint  # noqa: E402

SHELL = os.path.join(CAD, "out", "shell-bp")
OUT = os.path.join(SHELL, "split")
KIND_COLOUR = {"floor": "#1f77b4", "ring": "#ff7f0e", "cross": "#2ca02c", "rib": "#9467bd", "mount": "#8c564b", "frame": "#d62728"}
LABELLED = {"Monitor_Body": "monitor", "MonitorAny_Cradle": "monitor room", "Compute_Heatsink": "BC-250", "Compute_FanShroud": "fan, shroud",
            "Compute_ExhaustDuct": "exhaust duct", "PSU_Body": "power supply", "Hub_Body": "hub", "SpeakerR_Driver": "speaker",
            "Marquee_Modules": "marquee", "Lever_Body": "lever", "CableBundle_Body": "cables", "USB_C4_Body": "USB"}


def sections() -> dict:
    return json.load(open(os.path.join(SHELL, "fit", "sections.json")))


def outline(ax, sec: dict, axes: tuple[int, int] | None = None) -> None:
    for line in sec["outer"]:
        p = np.array(line)
        ax.plot(p[:, 0], p[:, 1], color="#555", lw=0.8, zorder=2)
    for line in sec["cavity"]:
        p = np.array(line)
        ax.fill(p[:, 0], p[:, 1], color="#f4f4f4", zorder=1)
        ax.plot(p[:, 0], p[:, 1], color="#bbb", lw=0.5, zorder=2)


def items(ax, view: str, labels: bool = True) -> None:
    for it in sections()["rear"]["items"]:
        x0, z0, x1, z1 = it["box"]
        y0, y1 = it["y"]
        a, b = ((y0, z0), (y1, z1)) if view == "side" else ((x0, y0), (x1, y1))
        hard = it["role"] == "hardware"
        ax.add_patch(Rectangle(a, b[0] - a[0], b[1] - a[1], fc="#d9d9d9" if hard else "none", ec="#999", lw=0.4,
                               ls="-" if hard else (0, (2, 2)), zorder=3))
        if labels and it["solid"] in LABELLED and (view == "side" or it["solid"] not in ("SpeakerR_Driver", "Marquee_Modules")):
            ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, LABELLED[it["solid"]], fontsize=6, ha="center", va="center", color="#444", zorder=8)


def member_shapes(m: st.Member, view: str) -> list[np.ndarray]:
    sides = [False, True] if m.mirror else [False]
    out = []
    for left in sides:
        k = -1.0 if left else 1.0
        if m.box:
            x0, x1, y0, y1, z0, z1 = m.box
            if left:
                x0, x1 = -x1, -x0
            pts = [(y0, z0), (y1, z0), (y1, z1), (y0, z1)] if view == "side" else [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        else:
            (y0, z0), (y1, z1) = m.p, m.q
            n = np.array((-(z1 - z0), y1 - y0))
            n = n / np.linalg.norm(n) * m.sn / 2
            if view == "side":
                pts = [(y0 + n[0], z0 + n[1]), (y1 + n[0], z1 + n[1]), (y1 - n[0], z1 - n[1]), (y0 - n[0], z0 - n[1])]
            else:
                xa, xb = sorted((k * m.x0, k * (m.x0 + m.sx)))
                pts = [(xa, min(y0, y1)), (xb, min(y0, y1)), (xb, max(y0, y1)), (xa, max(y0, y1))]
        out.append(np.array(pts))
        if view == "side":
            break
    return out


def frame_ax(ax, title: str, xlim, ylim) -> None:
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=10)
    ax.tick_params(labelsize=6)
    ax.grid(True, color="#eee", lw=0.4, zorder=0)


def structure_sheet(key: str, opt: sp.Option, d: Blueprint) -> str:
    sec = sections()["sections"]
    members = st.frame_c(d) if key == "C" else st.skin_members(d, key)
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(24, 9), gridspec_kw={"width_ratios": [1.15, 1.0, 0.75]})
    outline(a1, sec["side, centre line"])
    items(a1, "side")
    outline(a2, sec["plan, compute module"])
    items(a2, "plan")
    seams = json.load(open(os.path.join(OUT, key, "seams.json")))
    for s in seams.values():
        if s["side"] == "L" or s["module"] != "body":
            continue
        for line in s["lines"]:
            p = np.array(line)
            a1.plot(p[:, 1], p[:, 2], color=KIND_COLOUR["ring"], lw=0.7, alpha=0.55, zorder=4)
    for m in members:
        c = KIND_COLOUR[m.kind]
        for view, ax in (("side", a1), ("plan", a2)):
            for pts in member_shapes(m, view):
                fade = 0.07 if m.kind == "floor" and view == "plan" else 0.30 if m.kind in ("ring", "floor", "rib") else 0.55
                hollow = m.kind == "rib" or (m.kind == "ring" and view == "plan")
                ax.add_patch(Polygon(pts, closed=True, fc="none" if hollow else c, ec=c, alpha=0.9 if hollow else fade,
                                     lw=1.2, ls=(0, (3, 2)) if m.kind == "rib" else "-", zorder=5))
        pts = member_shapes(m, "side")[0]
        a1.annotate(m.name, xy=pts.mean(axis=0), xytext=pts.mean(axis=0) + (0, 0), fontsize=6.3, color=c, ha="center",
                    va="center", zorder=9, bbox=dict(fc="white", ec=c, lw=0.5, pad=0.6, alpha=0.85))
    frame_ax(a1, "side (y, z): centre-line section, members projected", (-20, 620), (-20, 600))
    frame_ax(a2, f"plan (x, y): section at z {sec['plan, compute module']['at']:.0f}, members projected", (-270, 270), (-20, 600))
    a3.axis("off")
    rows = [f"{opt.title}: structure", ""]
    for kind in ("floor", "ring", "cross", "rib", "mount", "frame"):
        names = [m.name for m in members if m.kind == kind]
        if names:
            rows.append(f"{st.KIND_WORDS[kind]}: {', '.join(names)}")
    rows += ["", "mounts:"]
    for i, mt in enumerate(st.mounts(key), 1):
        rows.append(f"{i:>2}. {mt.item}: on {mt.on}")
    a3.text(0, 1, "\n".join(rows), fontsize=7.5, va="top", family="DejaVu Sans Mono", transform=a3.transAxes, wrap=True)
    for i, (kind, c) in enumerate(KIND_COLOUR.items()):
        a3.add_patch(Rectangle((0.0, 0.02 + i * 0.035), 0.05, 0.022, fc=c, alpha=0.5, transform=a3.transAxes))
        a3.text(0.07, 0.031 + i * 0.035, st.KIND_WORDS[kind], fontsize=7.5, va="center", transform=a3.transAxes)
    fig.suptitle(f"Structure of option {opt.title} (mm). Grey: hardware of the fit study; dashed: keep-out zones; light "
                 "orange lines: the bonded seams, each with an inside flange", fontsize=11)
    path = os.path.join(OUT, f"structure-{key}.png")
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return path


def arrow(ax, a, b, colour, dashed=False) -> None:
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=11, color=colour, lw=1.6, ls="--" if dashed else "-", zorder=9))


AIR_SIDE = (  # (y, z) arrows in side view
    ((610, 185), (540, 185), "#1f77b4", False, "outside air in through the fan vent"),
    ((535, 185), (500, 185), "#1f77b4", False, ""),
    ((480, 200), (480, 245), "#d62728", False, "out of the fins at the I/O end"),
    ((500, 240), (545, 225), "#d62728", False, "duct to the slot vents"),
    ((150, -12), (150, 12), "#1f77b4", False, "make-up air through the floor"),
    ((300, 40), (420, 110), "#1f77b4", False, ""),
    ((460, 60), (560, 60), "#d62728", False, "power supply out of its grille"),
)
AIR_PLAN = (  # (x, y)
    ((48, 610), (48, 540), "#1f77b4", False), ((48, 530), (48, 495), "#1f77b4", False), ((40, 480), (-150, 480), "#d62728", False),
    ((-175, 490), (-175, 560), "#d62728", False), ((-150, 380), (-150, 560), "#d62728", False), ((0, 150), (-120, 360), "#1f77b4", False),
)
PLUGS = ((56.0, 470.0, 320.0, "PCIe plug at the board + 150 loop"), (-188.0, 330.0, 215.0, "monitor plugs (right angle) + slack"),
         (-165.0, 180.0, 22.0, "panel USB plug + 200 loop"), (120.0, 470.0, 432.0, "hood plug + loop"))
DUCT_FAN = (-174.0, 130.0, 182.0, 92.0)  # x centre, z centre... (x, z, y face, size)


def services_sheet() -> str:
    sec = sections()["sections"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(22, 10))
    outline(a1, sec["side, centre line"])
    items(a1, "side")
    outline(a2, sec["plan, compute module"])
    items(a2, "plan")
    for r in st.ROUTES:
        p = np.array(r.points)
        a1.plot(p[:, 1], p[:, 2], color=r.colour, lw=2.0, zorder=7, label=r.name)
        a2.plot(p[:, 0], p[:, 1], color=r.colour, lw=2.0, zorder=7)
    for x, y, z, words in PLUGS:
        for ax, a in ((a1, (y, z)), (a2, (x, y))):
            ax.plot(*a, marker="X", ms=9, color="black", zorder=10)
        a1.annotate(words, xy=(y, z), xytext=(y - 160, z + 40), fontsize=6.5, arrowprops=dict(arrowstyle="-", lw=0.5), zorder=10,
                    bbox=dict(fc="white", ec="#333", lw=0.4, pad=0.5))
    for a, b, c, dashed, words in AIR_SIDE:
        arrow(a1, a, b, c, dashed)
        if words:
            a1.text(*a, words, fontsize=6.5, color=c, ha="left", va="bottom", zorder=10)
    for a, b, c, dashed in AIR_PLAN:
        arrow(a2, a, b, c, dashed)
    # the optional fan in the duct: 92 mm, its face in front of the slot vents
    x, z, _, size = DUCT_FAN
    a1.add_patch(Rectangle((506, z + 52 - size / 2), 25, size, fc="none", ec="#d62728", ls="--", lw=1.4, zorder=9))
    a1.text(500, z + 52 + size / 2 + 4, "option: 92 mm fan in the duct", fontsize=6.5, color="#d62728", ha="right")
    a2.add_patch(Rectangle((x - size / 2, 506), size, 25, fc="none", ec="#d62728", ls="--", lw=1.4, zorder=9))
    a2.text(x, 470, "option: 92 mm\nduct fan", fontsize=6.5, color="#d62728", ha="center")
    a1.legend(loc="upper left", fontsize=7)
    frame_ax(a1, "side (y, z): cable routes and the air path", (-20, 630), (-25, 600))
    frame_ax(a2, "plan (x, y)", (-270, 270), (-20, 630))
    fig.suptitle("Cable routes and the air path. X: a plug where a part opens for service (door, hood, control panel, "
                 "monitor carrier). Blue: cool air; red: warm air.", fontsize=11)
    path = os.path.join(OUT, "services.png")
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------- the joint sheet ----------

def box(ax, x, y, w, h, c="#e8c39e", hatch=None, lw=0.8) -> None:
    ax.add_patch(Rectangle((x, y), w, h, fc=c, ec="#333", lw=lw, hatch=hatch, zorder=3))


def dim(ax, p, q, text, shift=(0, 0)) -> None:
    db.dim(ax, p, q, text, shift, size=6.5)


def note(ax, at, text, to=None) -> None:
    db.note(ax, at, text, to, size=6.5)


def joint_skin(ax) -> None:
    """Skin to skin on a wall: inside flanges on both pieces, a key on one face, thread-forming screws, a V-groove."""
    a, b = "#e8c39e", "#9ec5e8"
    box(ax, -40, 0, 39.5, 4, a)                 # wall of piece 1 (outside at y = 0)
    box(ax, 0.5, 0, 39.5, 4, b)                 # wall of piece 2
    box(ax, -6.5, 4, 6, 12, a)                  # flange 1
    box(ax, 0.5, 4, 6, 12, b)                   # flange 2
    ax.add_patch(Polygon([(-6.5, 16), (-6.5, 4), (-18.5, 4)], fc=a, ec="#333", lw=0.8, zorder=3))  # 45 deg gusset
    ax.add_patch(Polygon([(6.5, 16), (6.5, 4), (18.5, 4)], fc=b, ec="#333", lw=0.8, zorder=3))
    box(ax, -0.5, 8, 1.5, 4, a)                 # key on flange 1 into a groove of flange 2
    ax.add_patch(Polygon([(-0.5, 0), (0.5, 0), (0, 0.8)], fc="white", ec="#d62718", lw=0.8, zorder=4))  # V-groove
    ax.plot([-12, 12], [12, 12], color="#333", lw=1.4, zorder=5)  # screw
    ax.plot([-0.25, -0.25], [4, 16], color="#2ca02c", lw=1.2, zorder=4)
    dim(ax, (-34, 0), (-34, 4), "4", (-4, 0))
    dim(ax, (-6.5, 19), (6.5, 19), "2 x 6 flange", (0, 3))
    dim(ax, (22, 4), (22, 16), "12", (4, 0))
    note(ax, (-40, 26), "key 1.5 x 4, groove +0.2 (coupon sets it): locates", (-0.5, 10))
    note(ax, (-40, 32), "thread-forming screw 3.0 x 16 for plastics, every 60: clamps while it cures, stays in", (-12, 12))
    note(ax, (2, -9), "V-groove 1.0 wide, 0.8 deep on the outside: takes the filler", (0, 0.4))
    note(ax, (8, 26), "green: adhesive on the flange faces, 10 x seam length", (0, 10))
    note(ax, (-42, -16), "45 deg gusset under a level flange: prints with no support", (-12, 5))
    ax.set_title("1  skin to skin on a wall or a curved face (section across the seam)", fontsize=9)


def joint_floor(ax) -> None:
    box(ax, -40, 0, 50, 3.5, "#e8c39e")
    box(ax, -40, 3.5, 30, 3.5, "#e8c39e")
    box(ax, -10, 3.5, 50, 3.5, "#9ec5e8")
    box(ax, 10, 0, 30, 3.5, "#9ec5e8")
    ax.add_patch(Polygon([(-4, 3.5), (4, 3.5), (0, 6.5)], fc="#e8c39e", ec="#333", lw=0.8, zorder=4))  # cone
    ax.plot([-5, -5], [-6, 6], color="#333", lw=1.4, zorder=5)
    ax.plot([5, 5], [-6, 6], color="#333", lw=1.4, zorder=5)
    dim(ax, (-10, 10), (10, 10), "half-lap 20", (0, 3))
    dim(ax, (44, 0), (44, 7), "7", (4, 0))
    note(ax, (-40, 18), "cone 8 dia x 3 in the lower lap, socket in the upper: locates", (0, 5))
    note(ax, (-40, 23), "thread-forming 3.5 x 12 from below, every 50; adhesive on the 20 lap", (-5, -4))
    note(ax, (12, -12), "sandwich: skins 1.2, gyroid core 40 %", (25, 2))
    ax.set_title("2  floor tile to floor tile (printed floor, 7 thick)", fontsize=9)


def joint_foot(ax) -> None:
    box(ax, -30, 0, 60, 7, "#9ec5e8")           # floor tile
    box(ax, 30, 0, 4, 60, "#e8c39e")            # wall, outside at x = 34
    box(ax, 18, 7, 12, 4, "#e8c39e")            # foot flange on the floor
    box(ax, 22, 7, 3, 2.5, "#e8c39e")           # key into a slot in the floor? drawn as a rib
    ax.plot([24, 24], [-6, 11], color="#333", lw=1.4, zorder=5)
    dim(ax, (18, 14), (30, 14), "12", (0, 3))
    dim(ax, (-34, 0), (-34, 7), "7", (-4, 0))
    note(ax, (-30, 30), "the wall stands on the desk outside the floor; its foot flange lies on the floor", (25, 10))
    note(ax, (-30, 36), "key 3 x 2.5 under the flange into a slot in the floor: locates", (23.5, 8))
    note(ax, (-30, 42), "thread-forming 3.5 x 16 up from below every 80; adhesive on the flange", (24, 2))
    ax.set_title("3  wall foot to floor", fontsize=9)


def joint_node(ax) -> None:
    box(ax, -30, -2, 60, 4, "#e8c39e")          # level seam flanges seen from inside
    box(ax, -2, 2, 4, 28, "#9ec5e8")
    box(ax, -2, -30, 4, 28, "#b9dea0")
    box(ax, -12, -12, 24, 24, "#f2e3a0", lw=1.2)
    for p in ((-7, -7), (7, -7), (-7, 7), (7, 7)):
        ax.add_patch(plt.Circle(p, 2.0, fc="white", ec="#333", lw=0.8, zorder=6))
    note(ax, (-30, 38), "node plate 24 x 24 x 4, bonded inside over the three flanges", (0, 12))
    note(ax, (-30, 44), "cone in each flange, socket in the plate: the plate sets all three", (7, 7))
    note(ax, (-30, -40), "one thread-forming screw into each piece", (-7, -7))
    ax.set_title("4  node: three pieces meet (seen from inside)", fontsize=9)


def joint_service(ax) -> None:
    box(ax, -40, 0, 39.5, 4, "#e8c39e")
    box(ax, 0.5, 0, 39.5, 4, "#9ec5e8")
    box(ax, -12.5, 4, 12, 4, "#e8c39e")
    box(ax, 0.5, 4, 12, 9, "#9ec5e8")           # boss with insert
    box(ax, 4.5, 6, 4, 7, "#c0c0c0")
    ax.plot([6.5, 6.5], [-4, 13], color="#333", lw=1.6, zorder=6)
    ax.add_patch(Polygon([(-0.5, 0), (0.5, 0), (0, 0.5)], fc="white", ec="#333", lw=0.6, zorder=4))
    dim(ax, (0.5, 16), (12.5, 16), "boss 12", (0, 3))
    note(ax, (-40, 26), "M4 heat-set insert (5.6 hole, 8 deep) in the fixed part; M4 screw every 80 to 100", (6.5, 10))
    note(ax, (-40, 32), "two pins 4 dia, +0.1, for the place; chamfer 0.5 on both edges; never glued or filled", (0, 2))
    note(ax, (-40, -10), "door: 4 thumb screws into inserts", None)
    note(ax, (-40, -14), "hood: 2 pins at the front, 2 M4 at the rear", None)
    note(ax, (-40, -18), "bezel plate: magnets on the fixed cradle, 2 pins, a finger notch: no tool", None)
    ax.set_title("5  service seam (opens again)", fontsize=9)


def coupon(ax) -> None:
    t = np.linspace(-0.45, 0.45, 40)
    r = 300.0
    for k, (c, lo, hi) in enumerate((("#e8c39e", -0.45, 0.0), ("#9ec5e8", 0.0, 0.45))):
        tt = np.linspace(lo, hi, 20)
        outer = np.stack([r * np.sin(tt), r * np.cos(tt) - r], 1)
        inner = np.stack([(r - 4) * np.sin(tt), (r - 4) * np.cos(tt) - r], 1)
        ax.add_patch(Polygon(np.concatenate([outer, inner[::-1]]), fc=c, ec="#333", lw=0.8))
    box(ax, -6.5, -16, 6, 12, "#e8c39e")
    box(ax, 0.5, -16, 6, 12, "#9ec5e8")
    dim(ax, (-130, 8), (130, 8), "2 x 130 along the arc, 60 wide, 4 skin, joint 1 between them", (0, 4))
    note(ax, (-130, -40), "radius 300 (a curved face like the rail's land); print each half in its real orientation", (-100, -18))
    note(ax, (-130, -48), "make three pairs: groove +0.1, +0.2, +0.3", (0, -10))
    ax.set_title("6  coupon pair for joint 1", fontsize=9)


def joint_hood(ax) -> None:
    """The hood on the body top: keyed, then bolted or bonded with the same parts."""
    box(ax, 0, 1.5, 4, 40, "#9ec5e8")            # hood wall, outside at x = 0
    box(ax, 0, -40, 4, 40, "#e8c39e")            # body wall
    ax.add_patch(Polygon([(0, 1.5), (0, 4.5), (-0.01, 4.5)], fc="white", ec="none"))
    ax.plot([0, 3], [-3, 0], color="#333", lw=0.8)   # body bevel 3 x 3
    ax.plot([0, 3], [4.5, 1.5], color="#333", lw=0.8)  # hood bevel
    box(ax, 4, -12, 14, 12, "#e8c39e")           # top ring flange of the body
    box(ax, 4, 1.5, 14, 6, "#9ec5e8")            # hood foot flange
    ax.add_patch(Polygon([(7, 0), (13, 0), (10, 3)], fc="#e8c39e", ec="#333", lw=0.8, zorder=4))  # cone into a socket
    box(ax, 14, -10, 3, 8, "#c0c0c0")             # insert in the ring
    ax.plot([15.5, 15.5], [-8, 11], color="#333", lw=1.6, zorder=6)
    dim(ax, (-6, 1.5), (-6, 0), "1.5", (-5, 0))
    dim(ax, (4, -16), (18, -16), "ring 14", (0, -3))
    note(ax, (-40, 30), "cone 8 x 3 on the ring, socket in the hood: two at the front, two at the rear corners", (10, 2))
    note(ax, (-40, 24), "bolt: M4 into a heat-set insert in the ring, from inside the hood (two at the rear)", (15.5, 5))
    note(ax, (-40, 18), "bond: the same faces take adhesive; the cones still set the place", (11, 4))
    note(ax, (-40, -28), "groove 1.5 + bevels 3 x 3 stays open: a design line", (1.5, -1.5))
    ax.set_title("7  hood on the body top: keyed, to bolt or to bond", fontsize=9)


def joint_values(ax) -> None:
    ax.axis("off")
    rows = ["Named values (structure.JOINT; joints.py of the coupon study", "becomes their one source):", ""]
    rows += [f"{k:<16} {v}" for k, v in st.JOINT.items()]
    rows += ["", "PETG and ABS use the same values; the coupon", "sets the clearances for the chosen material."]
    ax.text(0, 1, "\n".join(rows), fontsize=7.5, family="DejaVu Sans Mono", va="top", transform=ax.transAxes)


def joints_sheet() -> str:
    fig, axes = plt.subplots(2, 4, figsize=(27, 12))
    joint_values(axes[1, 3])
    for ax, f, lim in zip(axes.ravel(), (joint_skin, joint_floor, joint_foot, joint_hood, joint_node, joint_service, coupon),
                          (((-45, 45), (-20, 36)), ((-45, 50), (-16, 28)), ((-35, 40), (-10, 64)), ((-45, 25), (-35, 40)),
                           ((-35, 35), (-45, 50)), ((-45, 45), (-20, 36)), ((-140, 140), (-55, 15)))):
        f(ax)
        ax.set_xlim(*lim[0])
        ax.set_ylim(*lim[1])
        ax.set_aspect("equal")
        ax.tick_params(labelsize=6)
        ax.grid(True, color="#f0f0f0", lw=0.4)
    fig.suptitle("Joints of the bonded seams and the service seams (mm). Step 1: the key, cone or pin sets the place in a dry "
                 "assembly held by screws. Step 2: adhesive, the same screws, then filler in the V-groove.", fontsize=11)
    path = os.path.join(OUT, "joints.png")
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------- the width study ----------

def hull_points(p: np.ndarray) -> np.ndarray:
    from scipy.spatial import ConvexHull

    if len(p) < 8:
        return p
    try:
        return p[ConvexHull(p).vertices]
    except Exception:  # noqa: BLE001 - flat piece: keep the points
        return p


def width_study(meas: dict, step: float = 0.5) -> dict:
    """Each option's pieces with the cabinet wider by dW, the growth put into the rails (the agent that studies width
    adds it beside the bezel; candidates 514.7 and 533.2): every point outside x = +-218.3 of the body and the floor, and outside x = +-174 of the
    hood (the top flat), moves out by dW / 2. The centre seam of the hood halves then grows with them. Gives the
    largest dW at which every piece still fits, and the result at +20 and +38."""
    lim = sp.Printer(**{k: meas["printer"][k] for k in ("xy", "z", "bed", "source")})
    out = {}
    for key in sp.ALL:
        man = json.load(open(os.path.join(OUT, key, "manifest.json")))
        rows = meas["options"][key]["pieces"]
        parts = {}
        for name, m in man.items():
            module = rows[name]["module"]
            if module in ("bezel", "speaker_right", "speaker_left", "logo_form"):
                continue
            t = 174.0 if module == "hood" else 218.3
            p = db.load_stl(os.path.join(OUT, key, m["file"])).reshape(-1, 3)
            p = np.unique(np.round(p, 2), axis=0)
            groups = [hull_points(p[p[:, 0] > t]), hull_points(p[p[:, 0] < -t]), hull_points(p[np.abs(p[:, 0]) <= t])]
            parts[name] = (groups, rows[name]["up"])

        def fails(dw: float) -> list[str]:
            bad = []
            for name, (g, up) in parts.items():
                q = [g[0] + (dw / 2, 0, 0), g[1] - (dw / 2, 0, 0), g[2]]
                q = np.concatenate([x for x in q if len(x)])
                if not sp.print_box(q, tuple(up), lim, step=1.0)["fits"]:
                    bad.append(name)
            return bad

        lo, hi = 0.0, 80.0
        if fails(hi):
            while hi - lo > step:
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if not fails(mid) else (lo, mid)
        else:
            lo = hi
        out[key] = {"max_dw": lo, "at_20": fails(20.0), "at_38": fails(38.5), "first": fails(hi) if hi < 80 else []}
    return out


def panel_seam(x: float = -41.2) -> dict:
    """A seam across a printed control panel plate at x: its clearance to every control under the plate, and the width
    of the larger half."""
    d = Blueprint()
    from candybar.shell import profiles as pr

    out = pr.panel_outline(d)
    near = []
    for it in sections()["rear"]["items"]:
        if it["group"] != "Panel" or it["role"] != "hardware":
            continue
        x0, _, x1, _ = it["box"]
        gap = x0 - x if x0 > x else (x - x1 if x1 < x else -1.0)
        near.append((gap, it["solid"]))
    near.sort()
    xs = [p[0] for p in out]
    return {"x": x, "halves": (round(x - min(xs), 1), round(max(xs) - x, 1)), "nearest": near[:3]}
