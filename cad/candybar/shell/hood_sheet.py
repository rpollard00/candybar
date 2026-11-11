"""Draw the hood: front elevation, two true side sections and the plan of a foot, from hood-section.json of a build.

The outlines are slices and edges of the built solids (written by build.py), so the drawing shows the built
geometry. The dimension figures come from the named dimensions and the stations stored with them. All
positions are in the hood frame: x across, y back from the cap's front plane, z up from the cap's base.
Needs matplotlib (cad/.venv-tools). Example:
    cad/.venv-tools/bin/python cad/candybar/shell/hood_sheet.py cad/out/shell-d/3-short-band/hood-section.json \
        cad/out/shell-d/sheet-hood-section.png
"""
from __future__ import annotations

import json
import math
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402

FILL = {"body": "#cdd2da", "bezel": "#2a2b30", "hood": "#e3e1dc", "hood_band": "#f3ead0", "speaker_right": "#3a3a3e",
        "logo_plate": "#2f4f3a", "marquee_cover": "#5a5d66", "marquee": "#8fd16a"}
LABEL = {"body": "body", "bezel": "bezel", "hood": "cap (top bar, legs, sill, rail)", "hood_band": "hood band with raised forms",
         "speaker_right": "speaker grille", "logo_plate": "logo plate", "marquee_cover": "marquee cover", "marquee": "marquee window"}
ORDER = ["body", "bezel", "hood", "hood_band", "marquee_cover", "marquee", "speaker_right", "logo_plate"]
RED = "#b0302a"
BLUE = "#1f4e8c"


def dim(ax: Axes, p: tuple[float, float], q: tuple[float, float], text: str, shift: tuple[float, float] = (0.0, 0.0),
        colour: str = RED, size: float = 8.5, ha: str = "center", va: str = "center", turn: float = 0.0) -> None:
    """A dimension line from p to q with its figure at the middle, moved by shift."""
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="<->", color=colour, lw=0.9, shrinkA=0, shrinkB=0))
    mid = ((p[0] + q[0]) / 2 + shift[0], (p[1] + q[1]) / 2 + shift[1])
    ax.text(*mid, text, color=colour, fontsize=size, ha=ha, va=va, rotation=turn, bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))


def note(ax: Axes, at: tuple[float, float], text: str, to: tuple[float, float] | None = None, colour: str = BLUE,
         size: float = 8.5, ha: str = "left") -> None:
    if to is None:
        ax.text(*at, text, color=colour, fontsize=size, ha=ha, va="center", zorder=6)
    else:
        ax.annotate(text, xy=to, xytext=at, color=colour, fontsize=size, ha=ha, va="center", zorder=6,
                    arrowprops=dict(arrowstyle="-", color=colour, lw=0.7))


def draw_section(ax: Axes, cut: dict[str, list], title: str) -> None:
    for name in ORDER:
        for loop in cut.get(name, []):
            ax.fill([p[0] for p in loop], [p[1] for p in loop], fc=FILL[name], ec="#1c1c1f", lw=0.8, zorder=2 if name == "body" else 3)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=10.5)
    ax.grid(True, color="#e6e6e6", lw=0.5, zorder=0)
    ax.set_xlabel("y, behind the front plane of the cap (mm)")
    ax.set_ylabel("z, above the base of the cap (mm)")


def section_centre(ax: Axes, data: dict) -> None:
    st, d, dv, sv = data["stations"], data["dims"], data["derived"], data["survey"]
    draw_section(ax, data["sections"]["centre"], "True side section at the centre line (through the logo plate)")
    h, dep = st["height"], st["depth"]
    zs, zb, zr, zo = st["z_sill"], st["z_band_top"], st["z_rail_top"], st["z_open_top"]
    ax.set_xlim(-104, dep + 104)
    ax.set_ylim(-46, h + 44)
    x = -14.0
    for z0, z1, text in ((0, zs, f"sill {zs:.0f}"), (zs, zb, f"hood band {zb - zs:.1f}"), (zb, zr, f"rail {zr - zb:.0f}"),
                         (zr, zo, f"marquee {zo - zr:.1f}"), (zo, h, f"top bar {h - zo:.0f}")):
        dim(ax, (x, z0), (x, z1), text, shift=(-3, 0), ha="right")
        ax.plot([x - 2, 0], [z1, z1], color=RED, lw=0.4)
    ax.plot([x - 2, 0], [0, 0], color=RED, lw=0.4)
    dim(ax, (-88, -d["seam_gap"]), (-88, h), f"hood {dv['hood_h']:.1f} above the body top = {dv['hood_h'] / dv['width']:.2f} of the width {dv['width']:.1f}",
        shift=(-6, 0), turn=90.0)
    dim(ax, (0, h + 9), (dep, h + 9), f"cap depth {dep:.1f}", shift=(0, 4))
    c_in, c_back = d["hood_edge_in"], d["hood_edge_back"]
    dim(ax, (0, h + 22), (c_back, h + 22), f"soft edge {c_back:.0f} back", shift=(-34, 0))
    note(ax, (c_back + 4, h + 26), f"and {c_in:.0f} down the front:\na quarter ellipse, all round the front")
    note(ax, (dep + 6, h + 4), f"rear edge R {d['hood_rear_r']:.0f}", to=(dep - 5, h - 5))
    dim(ax, (0, zs + 2.5), (st["y_band_foot"], zs + 2.5), f"ledge {st['y_band_foot']:.0f}", shift=(-14, 6), size=8)
    dim(ax, (0, zb - 7), (st["y_band_top"], zb - 7), f"band top {st['y_band_top']:.1f} back", shift=(-44, -5), size=8)
    dim(ax, (0, zo - 3), (st["y_marquee_top"], zo - 3), f"marquee {st['y_marquee_top']:.1f} under the bar", shift=(-48, 0), size=8)
    behind = sv.get("depth_behind_band_min", -1.0)
    y_rear = st["y_band_top"] + d["hood_band_t"] / math.cos(math.radians(d["hood_band_tilt"]))
    dim(ax, (y_rear, zb - 7), (st["y_wall"], zb - 7), f"{st['y_wall'] - y_rear:.1f}", shift=(0, -5), size=8)
    note(ax, (dep + 6, zs + 22), f"clear depth behind\nthe band: {behind:.1f} at\nthe least (probed),\nrear wall {d['hood_wall']:.0f}", to=(st["y_wall"], zs + 22))
    note(ax, (dep + 6, (zs + zb) / 2 + 22), f"hood band leans\nback {d['hood_band_tilt']:.0f} deg", to=(st["y_band_foot"] + (zb - zs) * 0.75 * math.tan(math.radians(d["hood_band_tilt"])), zs + (zb - zs) * 0.75))
    note(ax, (dep + 6, (zr + zo) / 2 + 4), f"marquee faces down\n{d['marquee_tilt']:.0f} deg: straight\nwindow {sv['marquee_window'][0]:.0f} x {sv['marquee_window'][1]:.0f},\n{sv['marquee_modules']} modules of {d['marquee_module']:.0f}",
         to=(st["y_marquee_bottom"] - (zo - zr) * 0.5 * math.tan(math.radians(d["marquee_tilt"])), (zr + zo) / 2))
    note(ax, (-100, -32), f"shoulder {d['hood_shoulder_front']:.0f} at front and rear,\nseam gap {d['seam_gap']:.1f}; the screen face\nbelow reclines {dv['recline']:.0f} deg", to=(-d["hood_shoulder_front"], -d["seam_gap"]))
    note(ax, (dep + 6, zo + 9), f"rim R {d['hood_rim_r']:.0f}", to=(1.5, zo + 1.5))


def section_speaker(ax: Axes, data: dict) -> None:
    st, d, dv = data["stations"], data["dims"], data["derived"]
    draw_section(ax, data["sections"]["speaker"], f"True side section through a speaker (x = {dv['speaker_x']:.0f})")
    h, dep = st["height"], st["depth"]
    zs, zb = st["z_sill"], st["z_band_top"]
    ax.set_xlim(-60, dep + 104)
    ax.set_ylim(-46, h + 44)
    b = math.radians(d["hood_band_tilt"])
    zm = (zs + zb) / 2
    ym = st["y_band_foot"] + (zm - zs) * math.tan(b)
    face = (ym - d["speaker_proud"] * math.cos(b), zm + d["speaker_proud"] * math.sin(b))
    dim(ax, (ym, zm), face, f"{d['speaker_proud']:.0f}", shift=(-9, 4), size=8)
    note(ax, (dep + 6, zm + 22), f"speaker form {d['speaker_proud']:.0f} proud\nof the band; its face\nand the grille are\nparallel to the band\n({d['hood_band_tilt']:.0f} deg), not upright", to=face)
    note(ax, (dep + 6, zm - 20), f"grille {d['grille_recess']:.1f} below\nthe face, face\nedge R {d['speaker_edge_r']:.0f}", to=(face[0] + 1.5, face[1] - 12))
    note(ax, (-56, h + 30), "the front plane of\nthe cap (y = 0)", to=(0, h + 8))
    ax.axvline(0.0, color=BLUE, lw=0.5, ls=":")


def elevation(ax: Axes, data: dict) -> None:
    st, d, dv, sv = data["stations"], data["dims"], data["derived"], data["survey"]
    for name in ORDER:
        for line in data["elevation"].get(name, []):
            ax.plot([p[0] for p in line], [p[1] for p in line], color=FILL[name] if name in ("marquee", "logo_plate") else "#1c1c1f",
                    lw=1.3 if name in ("marquee", "logo_plate") else 0.7)
    for name in ORDER[2:]:
        ax.plot([], [], color=FILL[name], lw=6, label=LABEL[name])
    ax.legend(loc="upper left", fontsize=7.5, ncol=1, frameon=False)
    ax.set_aspect("equal")
    ax.set_title("Front elevation of the hood (edges of the built solids in front of the band)", fontsize=10.5)
    hb, h = st["half_base"], st["height"]
    xc, zc = st["corner_centre"]
    w = dv["width"]
    ax.set_xlim(-w / 2 - 110, w / 2 + 110)
    ax.set_ylim(-42, h + 34)
    ax.plot([-w / 2, w / 2], [-d["seam_gap"], -d["seam_gap"]], color="#666", lw=1.0)
    ax.plot([-w / 2, -w / 2], [-d["seam_gap"], -30], color="#666", lw=1.0)
    ax.plot([w / 2, w / 2], [-d["seam_gap"], -30], color="#666", lw=1.0)
    dim(ax, (-w / 2, -24), (w / 2, -24), f"body {w:.1f}", shift=(0, -6))
    dim(ax, (-hb, -10), (hb, -10), f"cap at its base {2 * hb:.1f} (shoulder {d['hood_shoulder']:.0f} each side, {sv.get('shoulder_min', 0):.1f} at the least round the corner)", shift=(0, -5))
    dim(ax, (-xc, h + 8), (xc, h + 8), f"top flat {2 * xc:.1f} = {2 * xc / w:.2f} of the width", shift=(0, 5))
    dim(ax, (w / 2 + 14, -d["seam_gap"]), (w / 2 + 14, h), f"{dv['hood_h']:.1f}", shift=(5, 0), ha="left")
    a = math.radians(d["hood_side_lean"])
    note(ax, (xc + 70, h + 18), f"corner R {d['hood_corner_r']:.0f}, inside R {d['hood_corner_r'] - d['hood_bar']:.0f} (same centre)",
         to=(xc + d["hood_corner_r"] * math.cos(math.radians(50)), zc + d["hood_corner_r"] * math.sin(math.radians(50))), ha="left")
    note(ax, (-w / 2 - 104, h * 0.36), f"sides lean in {d['hood_side_lean']:.0f} deg", to=(-hb + 0.3 * h * math.tan(a), 0.3 * h))
    z_leg = st["z_sill"] + 20
    x_out = hb - z_leg * math.tan(a)
    dim(ax, (x_out - d["hood_bar"] / math.cos(a), z_leg), (x_out, z_leg), f"leg {d['hood_bar']:.0f}", shift=(52, 0), size=8)
    dim(ax, (-60, st["z_open_top"]), (-60, h), f"{d['hood_bar']:.0f}", shift=(-9, 0), size=8)
    mw, mh = sv["marquee_window"]
    zm = (st["z_rail_top"] + st["z_open_top"]) / 2
    dim(ax, (-mw / 2, zm), (mw / 2, zm), f"marquee window {mw:.0f} x {mh:.0f} straight ({sv['marquee_modules']} modules of {d['marquee_module']:.0f})", size=8.5)
    gw, gh = sv["speaker_grille"]
    lw_, lh = sv["logo_plate"]
    zmid = (st["z_sill"] + st["z_band_top"]) / 2
    note(ax, (dv["speaker_x"], zmid), f"grille {gw:.0f} x {gh:.0f}", colour="white", ha="center", size=8)
    note(ax, (0, zmid), f"logo plate {lw_:.0f} x {lh:.0f}", colour="white", ha="center", size=8)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("z, above the base of the cap (mm)")
    ax.grid(True, color="#ececec", lw=0.5)


def plan_corner(ax: Axes, data: dict) -> None:
    """The right front corner at the seam, seen from above: the foot of the leg on the land and the facet of the rail."""
    st, d, dv, sv = data["stations"], data["dims"], data["derived"], data["survey"]
    body, hood = data["plan"]["body"], data["plan"]["hood"]
    ax.fill([p[0] for p in body], [p[1] for p in body], fc=FILL["body"], ec="#1c1c1f", lw=0.8, zorder=2)
    ax.fill([p[0] for p in hood], [p[1] for p in hood], fc=FILL["hood"], ec="#1c1c1f", lw=1.0, zorder=3)
    ax.set_aspect("equal")
    w, hb, sf = dv["width"], st["half_base"], d["hood_shoulder_front"]
    ax.set_xlim(w / 2 - 62, w / 2 + 64)
    ax.set_ylim(70, -24)
    ax.set_title("Plan at the seam, right front corner: the foot of the leg on the rail", fontsize=10.5)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y, behind the front plane of the cap (mm)")
    ax.grid(True, color="#e6e6e6", lw=0.5, zorder=0)
    xi = w / 2 - d["band_in"]
    dim(ax, (xi - 22, -sf), (xi - 22, 0), f"{sf:.0f}", shift=(-4, 0), size=8)
    dim(ax, (hb, 58), (w / 2, 58), f"{d['hood_shoulder']:.0f}", shift=(0, 5), size=8)
    note(ax, (w / 2 - 60, -17), f"front edge of the body top: the land ends here\n(land {d['land']:.0f} wide, its outer edge rounded R {d['band_r']:.0f})", to=(xi - 8, -sf))
    note(ax, (w / 2 + 6, 4), "top end of the rail's facet", to=(w / 2 - 7, 14))
    note(ax, (w / 2 + 6, 26), f"foot of the leg: its front\nface stands over the land,\nits soft edge ({d['hood_edge_in']:.0f} by {d['hood_edge_back']:.0f},\na quarter ellipse) over the\nfacet; the shoulder is\n{sv.get('shoulder_min', 0):.1f} at the least", to=(hb - 6, 9))
    for loop in data["plan"].get("hood_open", []):
        ax.fill([p[0] for p in loop], [p[1] for p in loop], fc="white", ec="#1c1c1f", lw=0.6, zorder=4)
    note(ax, (w / 2 - 60, 44), "open floor of\nthe cap, behind\nthe sill", size=8)


def draw(data: dict, out: str, heading: str) -> None:
    fig = plt.figure(figsize=(21, 14.5), dpi=110)
    grid = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.9], width_ratios=[1.0, 1.0, 0.8], hspace=0.12, wspace=0.16)
    elevation(fig.add_subplot(grid[0, :]), data)
    section_centre(fig.add_subplot(grid[1, 0]), data)
    section_speaker(fig.add_subplot(grid[1, 1]), data)
    if data.get("plan"):
        plan_corner(fig.add_subplot(grid[1, 2]), data)
    fig.suptitle(heading, fontsize=13, y=0.985)
    fig.savefig(out, bbox_inches="tight")


def main(src: str, out: str) -> None:
    draw(json.load(open(src)), out, "Hood of variant D: built solids, sliced")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
