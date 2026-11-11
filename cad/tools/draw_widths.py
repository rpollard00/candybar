"""Width study sheets: the options of candybar.shell.widths side by side to one scale, and their numbers.

    cad/.venv-tools/bin/python cad/tools/draw_widths.py options          -> cad/out/shell-bp/compare/width-options.png
    cad/.venv-tools/bin/python cad/tools/draw_widths.py table [probes]   -> the numbers as Markdown on stdout; probes is a
                                                                            directory with probe-<tag>/probe.json (width_run probe)
    cad/.venv-tools/bin/python cad/tools/draw_widths.py renders <out> <label=renders-dir>...
                                                                         -> <out>: the front and three-quarter renders side by side

Draws from profiles.faces() of each option (2D, no FreeCAD). Blueprint() is not changed.
"""
from __future__ import annotations

import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(HERE)
sys.path.insert(0, CAD)
sys.path.insert(0, HERE)
import draw_blueprint as bp  # noqa: E402
from candybar.shell import profiles as pr  # noqa: E402
from candybar.shell import widths  # noqa: E402

COMPARE = os.path.join(CAD, "out", "shell-bp", "compare")
STRIP = ("+0", "+10", "+20", "+20 split", "+38.5", "+38.5 split")
TAGS = {"+0": "w0", "+10": "w10", "+20": "w20", "+20 split": "w20s", "+38.5": "w38", "+38.5 split": "w38s"}
BED, USABLE = 256.0, 240.0


def options() -> None:
    widths.use_module_window()
    n = len(STRIP)
    fig, axes = plt.subplots(2, n, figsize=(4.1 * n, 8.4), gridspec_kw={"height_ratios": [1.0, 0.5]})
    front_ext, top_ext = (-290.0, 290.0, -40.0, 600.0), (-290.0, 290.0, -45.0, 265.0)
    for col, name in enumerate(STRIP):
        d = widths.option(name)
        v = widths.numbers(d)
        tri, ids = bp.triangles_of(pr.faces(d))
        hw, bw = d.width / 2, d.bezel_w / 2
        a = axes[0, col]
        extra, bar, _ = widths.OPTIONS[name]
        bp.show(a, bp.raster(tri, ids, bp.VIEWS["front"], front_ext, px_per_mm=2.0, closed=False), "white",
                f"{name}: W {v['W']:.1f}  ({v['W'] / 2:.1f} a half)")
        a.set_xlim(front_ext[0], front_ext[1])
        a.set_ylim(front_ext[2], front_ext[3])
        bp.dim(a, (-hw, -22), (hw, -22), f"W {v['W']:.1f}", (0, -11), size=7)
        z = v["z_bezel_top"]
        bp.dim(a, (bw, z + 6), (d.side_x(z), z + 6), f"gap {v['gap_top']:.1f}", (-6, 11), size=6.5)
        zm = d.face(d.image_s)[1]
        bp.dim(a, (bw + d.panel_gap, zm), (d.side_x(zm) - d.edge_in, zm), f"land {v['land_mid']:.1f}", (-2, 11), size=6.5)
        bp.dim(a, (bw + d.panel_gap, z - 7), (d.side_x(z) - d.edge_in, z - 7), f"{v['land_top']:.1f}", (0, -9), size=6.5)
        bp.dim(a, (-bw, zm - 30), (-bw + d.frame_side, zm - 30), f"bar {d.frame_side:.1f}", (0, -10), size=6.5, colour_=bp.BLUE)
        clear = v["pass_right_angle"]
        a.text(0, 112, f"land {v['land_mid']:.1f} = {v['land_mid'] / v['W']:.3f} W, at the top corner {v['land_top']:.1f}\n"
                       f"side bar {d.frame_side:.1f} (top and bottom 45)\n"
                       f"opening behind the bezel {2 * v['opening_half']:.1f}\n"
                       f"pass-through, right-angle plugs: {clear:.1f} each side\n"
                       f"({v['pass_right_angle_no_side_ledge']:.1f} with no side ledge; straight plugs {v['pass_straight']:.0f})",
               ha="center", va="center", fontsize=7, color=bp.INK, zorder=9001, bbox=dict(fc="white", ec="#888", pad=3, lw=0.5))
        a = axes[1, col]
        bp.show(a, bp.raster(tri, ids, bp.VIEWS["top"], top_ext, px_per_mm=2.0, closed=False), "white", "")
        a.set_xlim(top_ext[0], top_ext[1])
        a.set_ylim(top_ext[2], top_ext[3])
        bp.dim(a, (-hw, -30), (hw, -30), f"{v['W']:.1f}", (0, -10), size=7)
        bp.dim(a, (d.panel_w / 2, 120), (hw, 120), f"{v['deck_border_side']:.1f}", (0, 9), size=6.5)
        bp.dim(a, (-v["deck_centre"] / 2, -12), (v["deck_centre"] / 2, -12), f"centre face {v['deck_centre']:.0f}", (0, 8), size=6.5, colour_=bp.BLUE)
        a.text(0, 120, f"panel {d.panel_w:.0f}", ha="center", fontsize=7, color=bp.INK, zorder=9001)
    fig.suptitle("Width options, one scale: front elevation (top) and the deck from above (bottom). The window, the screen and the "
                 "monitor do not change; the growth goes into the rail lands, and in the split options also into the side bars of the "
                 "bezel frame.\nland: rail land at mid image and (below) at the bezel's top corner; gap: bezel top corner to the side "
                 "outline; pass-through: opening behind the bezel (bezel less a ledge of 6) less the monitor with its adjustment and "
                 "right-angle plugs (210 from the centre line).", fontsize=9.5)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    os.makedirs(COMPARE, exist_ok=True)
    fig.savefig(os.path.join(COMPARE, "width-options.png"), dpi=110)
    print(os.path.join(COMPARE, "width-options.png"))


def table(probes: str | None) -> None:
    widths.use_module_window()
    rows = [(name, widths.option(name)) for name in STRIP]
    nums = [widths.numbers(d) for _, d in rows]
    cav = []
    for name, _ in rows:
        path = os.path.join(probes, f"probe-{TAGS[name]}", "probe.json") if probes else ""
        cav.append({r["where"]: r["cavity_half_width"] for r in json.load(open(path))["plugs"]} if path and os.path.exists(path) else {})
    f = lambda k, fmt="{:.1f}": [fmt.format(v[k]) for v in nums]
    lines = [("W", f("W")), ("H/W, D/W", [f"{v['H/W']:.3f}, {v['D/W']:.3f}" for v in nums]),
             ("hood height / W, hood depth / W", [f"{v['hood_h/W']:.3f}, {v['hood_d/W']:.3f}" for v in nums]),
             ("side bar of the bezel frame", f("frame_side")), ("bezel width / W", f("bezel/W", "{:.3f}")),
             ("rail land at mid bezel, mm (/ W)", [f"{v['land_mid']:.1f} ({v['land_mid'] / v['W']:.3f})" for v in nums]),
             ("rail land at the bezel's top corner, mm (/ W)", [f"{v['land_top']:.1f} ({v['land_top'] / v['W']:.3f})" for v in nums]),
             ("front view: bezel top corner to the side outline", f("gap_top")),
             ("opening behind the bezel, width", [f"{2 * v['opening_half']:.1f}" for v in nums]),
             ("pass-through each side, right-angle plugs (monitor at the end of its adjustment / centred)",
              [f"{v['pass_right_angle']:.1f} / {v['pass_right_angle_centred']:.1f}" for v in nums]),
             ("the same with no side ledge (plate rests at the top and the bottom only)", [f"{v['pass_right_angle_no_side_ledge']:.1f}" for v in nums]),
             ("pass-through each side, straight plugs", f("pass_straight")),
             ("cavity half width, monitor top corners / mid image", [f"{c.get('top corners', float('nan')):.0f} / {c.get('middle of the image', float('nan')):.0f}" for c in cav]),
             ("straight plugs (258): spare at top corners / mid image", [f"{c.get('top corners', float('nan')) - 258:+.0f} / {c.get('middle of the image', float('nan')) - 258:+.0f}" for c in cav]),
             ("right-angle plugs (210): spare at top corners / mid image", [f"{c.get('top corners', float('nan')) - 210:+.0f} / {c.get('middle of the image', float('nan')) - 210:+.0f}" for c in cav]),
             ("half the width (W / 2) on the bed: bed 256, usable 240", [f"{v['half']:.1f}: {'fits' if v['half'] <= BED else 'no'}, {'fits' if v['half'] <= USABLE else 'no'}" for v in nums]),
             ("deck beside the control panel (side to the plate / flat inside the edge)", [f"{v['deck_border_side']:.1f} / {v['deck_border_flat']:.1f}" for v in nums]),
             ("control panel: width, depth at the sides", [f"396, {v['panel_depth_side']:.1f}" for v in nums]),
             ("deck centre face (0.56 W), deck corner R (kept in mm)", [f"{v['deck_centre']:.0f}, {v['deck_corner_r']:.1f}" for v in nums]),
             ("tuck each side at the seam (0.023 W)", f("tuck")), ("hood top corner R (0.07 W)", f("hood_corner_r")),
             ("hood foot / top flat", [f"{v['hood_foot']:.0f} / {v['hood_top_flat']:.0f}" for v in nums]),
             ("marquee: widest straight window, window used (modules of 32)", [f"{v['mq_widest']:.0f}, {v['mq_w']:.0f} ({v['mq_modules']:.0f})" for v in nums]),
             ("speaker form width at the foot / head; outer span / W", [f"{v['spk_w_foot']:.0f} / {v['spk_w_head']:.0f}; {v['spk_span'] / v['W']:.3f}" for v in nums]),
             ("logo form 176 / W", [f"{176 / v['W']:.3f}" for v in nums]), ("rear body (step 12)", f("rear_w"))]
    print("| | " + " | ".join(n for n, _ in rows) + " |")
    print("| --- |" + " --- |" * len(rows))
    for label, vals in lines:
        print(f"| {label} | " + " | ".join(vals) + " |")
    print()
    print("| Proportion | 3D model | Maker's mini | Real NAC | " + " | ".join(n for n, _ in rows) + " |")
    print("| --- | --- | --- | --- |" + " --- |" * len(rows))
    props = [bp.proportions(d) for _, d in rows]
    for i, row in enumerate(props[0]):
        print(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | " + " | ".join(p[i][4] for p in props) + " |")
    extra = [("Land / bezel width (mini 0.07 +-0.02 measured)", lambda v: v["land_mid"] / v["bezel_w"]),
             ("Land and edge seen from the front / bezel width (mini 0.11 +-0.01 measured)", lambda v: v["rail_seen"] / v["bezel_w"]),
             ("Speaker pod width / W (mini 0.176, real 0.19)", lambda v: v["spk_w_foot"] / v["W"]),
             ("Pods outer span / W (mini 0.753, real 0.89)", lambda v: v["spk_span"] / v["W"]),
             ("Lit marquee width / W (mini 0.82, real about 0.9)", lambda v: v["mq_w"] / v["W"]),
             ("Logo / W (mini 0.369, real 0.30)", lambda v: 176 / v["W"])]
    for label, fn in extra:
        print(f"| {label} | | | | " + " | ".join(f"{fn(v):.3f}" for v in nums) + " |")


def renders(out: str, specs: list[str]) -> None:
    from PIL import Image
    cols = [s.split("=", 1) for s in specs]
    views = ("front", "three-quarter-front-left")
    fig, axes = plt.subplots(len(views), len(cols), figsize=(5.2 * len(cols), 10.4))
    for c, (label, folder) in enumerate(cols):
        for r, view in enumerate(views):
            a = axes[r, c]
            a.imshow(Image.open(os.path.join(folder, f"{view}.png")))
            a.axis("off")
            if r == 0:
                a.set_title(label, fontsize=12)
    fig.suptitle("Width options, rendered to one scale (one camera frame for all): front and three-quarter front", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out, dpi=110)
    print(out)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "options":
        options()
    elif cmd == "table":
        table(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "renders":
        renders(sys.argv[2], sys.argv[3:])
