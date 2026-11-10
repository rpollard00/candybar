"""Draw the deck's front edge in true side section, large and dimensioned, from deck-section.json of a build.

The points are the slice of the deck solid at the centre line (written by build.py), so the drawing shows the
built geometry, not the intended one. Needs matplotlib (cad/.venv-tools). Example:
    cad/.venv-tools/bin/python cad/candybar/shell/section_sheet.py cad/out/shell-d/3-short-band/deck-section.json \
        cad/out/shell-d/sheet-deck-section.png
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


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
