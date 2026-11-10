"""Draw the deck's front edge in true side section, large and dimensioned, from deck-section.json of a build.

The points are the slice of the deck solid at the centre line (written by build.py), so the drawing shows the
built geometry, not the intended one. With "plan" first it draws the deck from above instead, from a top render
of the deck, beside a rectified reference photo. Needs matplotlib, numpy and Pillow (cad/.venv-tools). Examples:
    cad/.venv-tools/bin/python cad/candybar/shell/section_sheet.py cad/out/shell-d/3-short-band/deck-section.json \
        cad/out/shell-d/sheet-deck-section.png
    cad/.venv-tools/bin/python cad/candybar/shell/section_sheet.py plan DECK_SECTION_JSON DECK_RENDER_DIR \
        REFERENCE_PNG OUT_PNG
"""
from __future__ import annotations

import json
import math
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def main(src: str, out: str) -> None:
    data = json.load(open(src))
    d = data["dims"]
    pts = sorted(data["points"], key=lambda p: p[1])
    top, r, lean, lean_h, rb = d["deck_top"], d["deck_top_r"], d["deck_lean"], d["deck_lean_h"], d["bottom_r"]
    crease = top - lean_h
    turn = 90.0 - lean
    r_bottom = top - r * (1 - math.cos(math.radians(turn)))
    band = r_bottom - crease
    fig, ax = plt.subplots(figsize=(9, 11), dpi=150)
    ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=2, color="#222")
    ax.set_aspect("equal")
    ax.set_xlim(-25, 45)
    ax.set_ylim(-8, top + 12)
    ax.grid(True, color="#ddd", lw=0.5)
    ax.set_xlabel("Y, behind the deck front edge (mm)")
    ax.set_ylabel("Z, above the desk (mm)")
    note = dict(fontsize=10, color="#b0302a", ha="left", va="center")
    ax.axhline(top, color="#888", lw=0.6, ls=":")
    ax.axhline(crease, color="#b0302a", lw=0.8, ls="--")
    ax.axhline(r_bottom, color="#b0302a", lw=0.6, ls=":")
    ax.text(-24, top + 3, f"deck top border, Z {top:.0f}", **{**note, "color": "#555"})
    ax.text(10, (top + r_bottom) / 2 + 2, f"top radius R {r:.0f}, turning {turn:.0f} deg\n(from the top surface down to the leaning band)", **note)
    ax.text(10, (r_bottom + crease) / 2, f"leaning band: {lean:.0f} deg from vertical,\n{band:.1f} high (Z {crease:.0f} to {r_bottom:.1f}); top of the\ntaper inset {lean_h * math.tan(math.radians(lean)):.1f} behind the face", **note)
    ax.text(10, crease - 3, f"crease at Z {crease:.0f} ({lean_h / top * 100:.0f} % of the front height from the top)", **note)
    ax.text(10, (crease + rb) / 2, f"front face vertical, Z {rb:.0f} to {crease:.0f}", **note)
    ax.text(10, 2, f"bottom radius R {rb:.0f}", **note)
    ax.set_title("Deck front edge, true side section at the centre line (built solid, sliced)", fontsize=11)
    fig.tight_layout()
    fig.savefig(out)




def plan_sheet(src: str, render_dir: str, reference: str, out: str) -> None:
    """The deck from directly above (an orthographic render) with its faces and angles dimensioned, beside the
    rectified reference photo."""
    import numpy as np
    from PIL import Image

    data = json.load(open(src))
    d, w = data["dims"], data["width"]
    cam = json.load(open(f"{render_dir}/views.json"))["views"]["top"]
    img = np.asarray(Image.open(f"{render_dir}/top.png"))
    rx, ry = cam["res"]
    k = cam["mm_per_px"]
    cx, cy = cam["center_ru"]
    extent = (cx - rx / 2 * k, cx + rx / 2 * k, cy - ry / 2 * k, cy + ry / 2 * k)
    fig, (a, b) = plt.subplots(1, 2, figsize=(18, 8.5), dpi=130, gridspec_kw={"width_ratios": [1.15, 1]})
    a.imshow(img, extent=extent)
    a.set_xlim(-w / 2 - 40, w / 2 + 40)
    a.set_ylim(d_top_y(data) + 10, -60)
    a.set_aspect("equal")
    red = "#b0302a"
    xc = d["deck_centre_frac"] * w / 2
    a.annotate("", xy=(-xc, -30), xytext=(xc, -30), arrowprops=dict(arrowstyle="<->", color=red))
    a.text(0, -36, f"centre face {2 * xc:.0f} mm = {d['deck_centre_frac']:.2f} of the deck width {w:.0f}", color=red, ha="center")
    yf = (w / 2 - xc) * math.tan(math.radians(d["deck_flank"]))
    for sx in (1, -1):
        a.plot([sx * xc, sx * w / 2], [-8, yf - 8], color=red, lw=1.2)
        a.plot([sx * xc, sx * w / 2], [-8, -8], color=red, lw=0.6, ls=":")
        a.text(sx * (xc + w / 2) / 2, -14, f"flank {d['deck_flank']:.0f} deg", color=red, ha="center")
    r = d["deck_corner_frac"] * w
    a.text(w / 2 - 10, yf + r + 20, f"corner R {r:.0f}\n({d['deck_corner_frac']:.2f} W)", color=red, ha="right")
    bd = data["border"]
    fig.text(0.02, 0.06, "Border from the panel pocket, front corner: "
           f"{bd['front corner, to the outline']} mm to the outline, {bd['front corner, to the flat border edge']} mm flat; "
           f"front middle {bd['front middle, to the outline']} / {bd['front middle, to the flat border edge']}; "
           f"side {bd['side, to the outline']} / {bd['side, to the flat border edge']}", fontsize=11, color="#333")
    a.set_title("Variant D deck from directly above (orthographic render, mm)")
    a.set_xlabel("X (mm)")
    a.set_ylabel("Y behind the deck front (mm)")
    b.imshow(np.asarray(Image.open(reference)))
    b.set_axis_off()
    b.set_title("Reference: photo-d, rectified to the deck top plane")
    fig.tight_layout()
    fig.savefig(out)


def d_top_y(data: dict) -> float:
    return max(p[1] for p in data["plan"]) - 30.0


if __name__ == "__main__":
    if sys.argv[1] == "plan":
        plan_sheet(*sys.argv[2:6])
    else:
        main(sys.argv[1], sys.argv[2])
