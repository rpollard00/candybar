"""A sheet of the detail pass on the outer form, for the owner.

    cad/.venv-tools/bin/python cad/tools/draw_detail.py detail-options -> cad/out/shell-bp/compare/detail-options.png

detail-options draws the small questions of the form, each at one scale: the present state, the alternatives and
the recommendation. The sheets of revision 6's rear corner round (rear-options, before-after) went with that
construction: revision 7 has the planar rear (decision record 0007).

Needs numpy and matplotlib (cad/.venv-tools).
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import replace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Polygon  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(HERE)
sys.path.insert(0, CAD)
from candybar.shell import profiles as pr  # noqa: E402
from candybar.shell.dims import Blueprint  # noqa: E402

COMPARE = os.path.join(CAD, "out", "shell-bp", "compare")
INK, RED, BLUE, GREY, GREEN = "#1c1c1f", "#b0302a", "#1f4e8c", "#9a9aa0", "#2f7a3a"


def edge_section_points(d: Blueprint) -> list[tuple[float, float]]:
    """The deck's edge section in (in from the side, down from the top), with the side below the crease."""
    pts = [(-30.0, 0.0)] + [(i, -dn) for i, dn in reversed(pr.sample(pr.edge_section(d), 0.5))]
    pts = [(-30.0, 0.0)] + [(x, y) for x, y in sorted(pts[1:], key=lambda p: -p[1])]
    return pts


def round_only(r: float, depth: float = 40.0) -> list[tuple[float, float]]:
    return [(-30.0, 0.0), (-r, 0.0)] + [(-r + r * math.sin(a), -r + r * math.cos(a)) for a in [math.pi / 2 * k / 16 for k in range(17)]] + [(0.0, -depth)]


def panel(ax, title: str, rec: bool = False) -> None:
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=8.5, color=GREEN if rec else INK, fontweight="bold" if rec else "normal")
    ax.tick_params(labelsize=6)


def detail_options() -> None:
    d = Blueprint()
    h = pr.hood(d)
    fig = plt.figure(figsize=(22, 27))
    gs = fig.add_gridspec(6, 4, hspace=0.55, wspace=0.3)

    # 1. edge of the rail: whole section or radius only, in the plane square to the rail
    sec = sorted([(-i, -dn) for i, dn in pr.sample(pr.edge_section(d), 0.5)], key=lambda p: p[0])
    for k, (title, pts, rec) in enumerate((
            ("Q1 now: the deck's whole edge section up the rail\n(R 10.5, band 10 deg, crease 24 behind the land)", None, True),
            ("Q1 alternative: a radius only, R 10\n(the maker's mini reads about 8 at this size)", round_only(10.0), False),
            ("Q1 alternative: a radius only, R 16\n(as wide as the section; softer)", round_only(16.0), False))):
        ax = fig.add_subplot(gs[0, k])
        panel(ax, title, rec)
        if pts is None:
            outline = [(-30.0, 0.0)] + [(x, y) for x, y in sec] + [(0.0, -40.0)]
        else:
            outline = pts
        ax.add_patch(Polygon([(x, y) for x, y in outline] + [(-30.0, -40.0)], closed=True, fc="#eeeeea", ec=INK, lw=1.2))
        ax.set_xlim(-32, 8)
        ax.set_ylim(-42, 6)
        ax.text(-30, 2.5, "land (front)", fontsize=6.5)
        ax.text(1, -38, "side band", fontsize=6.5, rotation=90)
    ax = fig.add_subplot(gs[0, 3])
    ax.axis("off")
    ax.text(0, 0.95, "Q1 recommendation: keep the whole section.", fontsize=10, color=GREEN, fontweight="bold", va="top")
    ax.text(0, 0.82, "It is one line from the hood seam round the sweep\nand along the deck: the rail and the deck read as one\n"
            "member. Radius only would split the rail from the deck\n(two edge languages at the sweep foot), and the band's\n"
            "10 deg crease is what catches light down the rail.\nCost: none; it is built and checked.", fontsize=8.5, va="top")

    # 2. the crease behind the stripe: plan section of the side band and the band
    def step_plan(depth: float, lean_back: float = 1.0) -> list[tuple[float, float]]:
        return [(0.0, -60.0), (0.0, 0.0), (-depth, depth * lean_back), (-depth, 60.0)]
    for k, (title, pts, rec) in enumerate((
            ("Q3 now: the band, 12 deep, 45 deg in plan", step_plan(12.0), True),
            ("Q3 alternative: deeper, 20 (as the 3D model)", step_plan(20.0), False),
            ("Q3 alternative: a shallow line, a V 2 deep", [(0.0, -60.0), (0.0, -1.5), (-2.0, 0.0), (0.0, 1.5), (0.0, 60.0)], False))):
        ax = fig.add_subplot(gs[1, k])
        panel(ax, title, rec)
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=INK, lw=1.6)
        ax.fill_betweenx([p[1] for p in pts], [p[0] for p in pts], -40, color="#eeeeea")
        ax.set_xlim(-40, 12)
        ax.set_ylim(-62, 62)
        ax.text(1, -55, "side band (stripe)", fontsize=6.5, rotation=90)
        ax.text(-38, 45, "rear body", fontsize=6.5)
    ax = fig.add_subplot(gs[1, 3])
    ax.axis("off")
    ax.text(0, 0.95, "Q3: decided. The band is 12 deep.", fontsize=10, color=GREEN, fontweight="bold", va="top")
    ax.text(0, 0.82, "Revision 7 (decision record 0007) keeps 12: the band's\nlevel run is the side facet of the rear shelf, and the\n"
            "two facets of the shelf meet on the hip. A deeper band\n(20) narrows the lower body by 16; a shallow line\n"
            "loses the break that ends the stripe.", fontsize=8.5, va="top")

    # 3. legs and top bar of the hood, front elevation of the right half
    for k, (bar, rec) in enumerate(((21.0, True), (18.0, False), (25.0, False))):
        dd = replace(d, hood_bar=bar)
        hh = pr.hood(dd)
        ax = fig.add_subplot(gs[2, k])
        panel(ax, f"Q5 {'now' if rec else 'alternative'}: legs and top bar {bar:g}", rec)
        ax.plot(*zip(*hh.outline), color=INK, lw=1.4)
        ax.plot(*zip(*hh.opening), color=INK, lw=1.0)
        w, _ = pr.marquee_window(dd, hh)
        ax.text(5, hh.height - bar - 14, f"marquee window {w:.0f}", fontsize=7)
        ax.set_xlim(0, hh.half_base + 6)
        ax.set_ylim(0, hh.height + 6)
    ax = fig.add_subplot(gs[2, 3])
    ax.axis("off")
    ax.text(0, 0.95, "Q5 recommendation: keep 21.", fontsize=10, color=GREEN, fontweight="bold", va="top")
    ax.text(0, 0.82, "21 is 0.042 W: between the maker's 0.037 and the 3D\nmodel's 0.056, and it keeps the window at 352 (11\n"
            "modules). 18 and 25 keep the window at 352 too. 18\nreads thin: the soft edge (14) then takes most of the\n"
            "bar's face. 25 reads heavy against the tight top\ncorner (R 34.6).", fontsize=8.5, va="top")

    # 4. bottom corners of the hood opening
    for k, (r, rec) in enumerate(((6.0, False), (10.0, True))):
        dd = replace(d, hood_sill_corner_r=r)
        hh = pr.hood(dd)
        ax = fig.add_subplot(gs[3, k])
        panel(ax, f"Hood opening, bottom corner R {r:g}{' (now)' if r == 6.0 else ' (proposed by the finishing audit)'}", rec)
        zs = [hh.z_sill + i * 0.5 for i in range(0, 60)]
        ax.plot([hh.half_open(z, dd) for z in zs], zs, color=INK, lw=1.4)
        ax.plot([0, hh.half_open(hh.z_sill, dd)], [hh.z_sill, hh.z_sill], color=INK, lw=1.4)
        ax.set_xlim(hh.half_open(hh.z_sill + 30, dd) - 40, hh.half_open(hh.z_sill + 30, dd) + 6)
        ax.set_ylim(hh.z_sill - 4, hh.z_sill + 30)
        ax.text(hh.half_open(hh.z_sill + 30, dd) - 38, hh.z_sill - 3, "ledge (13.9 deep)", fontsize=6.5)
    ax = fig.add_subplot(gs[3, 2:])
    ax.axis("off")
    ax.text(0, 0.95, "Opening corner recommendation: R 10.", fontsize=10, color=GREEN, fontweight="bold", va="top")
    ax.text(0, 0.82, "A sanding sponge and a filler knife reach an inside corner of R 10; R 6 needs a dowel. The corner sits\n"
            "behind the speaker forms (their outer ends stand 8 from the legs), so the change is not seen from the\n"
            "seat. The speaker forms lose nothing: they start 4 above the ledge, and the round ends 10 above it\n"
            "at the leg. It does not change the marquee, the lip or the legs.", fontsize=8.5, va="top")

    # 5. a smallest outside edge radius
    ax = fig.add_subplot(gs[4, 0])
    panel(ax, "Edge, paint film: sharp, R 0.5, R 2 (to one scale)")
    for k, r in enumerate((0.0, 0.5, 2.0)):
        ox = k * 9.0
        if r == 0:
            body = [(ox, 0), (ox + 6, 0), (ox + 6, 6)]
            ax.plot([ox, ox + 6, ox + 6], [6, 6, 0], color=INK, lw=1.2)
            ax.plot([ox, ox + 6.1, ox + 6.1], [6.12, 6.03, 0], color=RED, lw=0.9)
        else:
            arc = [(ox + 6 - r + r * math.sin(a), 6 - r + r * math.cos(a)) for a in [math.pi / 2 * i / 16 for i in range(17)]]
            ax.plot([ox] + [p[0] for p in arc] + [ox + 6], [6] + [p[1] for p in arc] + [0], color=INK, lw=1.2)
            ax.plot([ox] + [p[0] + 0.12 * math.sin(math.pi / 2 * i / 16) for i, p in enumerate(arc)] + [ox + 6.12],
                    [6.12] + [p[1] + 0.12 * math.cos(math.pi / 2 * i / 16) for i, p in enumerate(arc)] + [0], color=RED, lw=0.9)
        ax.text(ox, -1.5, "sharp" if r == 0 else f"R {r:g}", fontsize=7)
    ax.set_xlim(-1, 26)
    ax.set_ylim(-2.5, 8)
    ax.text(-0.5, 7.4, "red: the paint film (0.12 drawn); it pulls back from a sharp edge", fontsize=6.5, color=RED)
    ax = fig.add_subplot(gs[4, 1:])
    ax.axis("off")
    ax.text(0, 0.98, "Smallest outside edge radius: R 2 on every convex outside edge that is not a design line.", fontsize=10,
            color=GREEN, fontweight="bold", va="top")
    ax.text(0, 0.86,
            "Reason: a liquid coat pulls back from a sharp edge and is thin there; ISO 12944-3 (paint systems, design) asks for edges\n"
            "rounded to at least R 2 so that the coat keeps its thickness. R 2 also survives filling and sanding by hand: a sharp\n"
            "printed edge chips and sands round unevenly. Sharp convex outside edges now: the hood opening (leg fronts HC1/HC11, top\n"
            "bar HC2/HC10, sill HC3/HC12), the marquee lip HC13, the logo form walls LG3, the upper crease of the rear slope RB4/RB5,\n"
            "the step's outer edge RL4/RB2 (above its run-out it is round), the edges of the seam bevels FB5/HC15, the bezel reveal\n"
            "BZ4/RL1, the panel pocket DK8/DK1, the floor edge FL1.\n"
            "Keep crisp (R 0.5, a chamfer of 0.5 as joint 5 has): the service seams, where the gap is the line: the groove FB5/HC15,\n"
            "the bezel reveal, the panel pocket, the rear door. Keep the step's outer edge and the slope crease at R 1: they are the\n"
            "lines that the eye follows; R 2 would soften them. Inside (concave) corners need no radius for the paint.",
            fontsize=8.5, va="top")

    # 6. the speaker grille
    tb = 0.0
    length = h.z_band_top - h.z_sill
    v0, v1 = d.speaker_foot_gap, length - d.speaker_head_gap
    leg = lambda v: h.half_width(max(h.z_sill + v, h.z_sill + d.hood_sill_corner_r), h.opening) - d.speaker_side_gap
    xi = d.logo_w / 2 + d.logo_gap
    form = [(xi, v0), (leg(v0), v0), (leg(v1), v1), (xi, v1)]
    g = d.grille_inset
    for k, (title, kind, rec) in enumerate((
            ("Speaker form now: a plain grille plate set 1.5 in", "plate", False),
            ("Alternative: horizontal slots 3 x full width, bars 2.5", "slots", True),
            ("Alternative: round holes 3.5 on a 5.0 hex pitch", "holes", False))):
        ax = fig.add_subplot(gs[5, k])
        panel(ax, title, rec)
        ax.add_patch(Polygon(form, closed=True, fc="#2a2a2c", ec=INK, lw=1.0))
        inner = [(xi + g, v0 + g), (leg(v0 + g) - g, v0 + g), (leg(v1 - g) - g, v1 - g), (xi + g, v1 - g)]
        x_in = lambda v: leg(v) - g
        if kind == "plate":
            ax.add_patch(Polygon(inner, closed=True, fc="#444448", ec="#888", lw=0.6))
        elif kind == "slots":
            v = v0 + g
            while v + 3.0 <= v1 - g:
                ax.add_patch(Polygon([(xi + g, v), (x_in(v), v), (x_in(v + 3.0), v + 3.0), (xi + g, v + 3.0)], closed=True, fc="#d8d8d4", lw=0))
                v += 5.5
        else:
            row = 0
            v = v0 + g + 1.75
            while v + 1.75 <= v1 - g:
                x = xi + g + 1.75 + (2.5 if row % 2 else 0.0)
                while x + 1.75 <= x_in(v) - 0.5:
                    ax.add_patch(Circle((x, v), 1.75, fc="#d8d8d4", lw=0))
                    x += 5.0
                v += 4.33
                row += 1
        ax.set_xlim(xi - 4, leg(v0) + 4)
        ax.set_ylim(v0 - 4, v1 + 4)
    ax = fig.add_subplot(gs[5, 3])
    ax.axis("off")
    ax.text(0, 0.95, "Speaker grille recommendation:\nhorizontal slots 3 wide, bars 2.5.", fontsize=10, color=GREEN, fontweight="bold", va="top")
    ax.text(0, 0.72, "Printed front face down, the slots are straight holes:\nno support. Open area about 55 % (ESTIMATED: a grille of\n"
            "30 % or more open, with holes far smaller than the\nwavelength, is about transparent to sound). A sanding\n"
            "block runs along the bars; slots of 3 stay open after\nprimer and paint (0.1 to 0.2 a side). Chamfer the slot\n"
            "edges 0.4 on the front. Round holes of 3.5 give 44 %\nand are harder to sand and to paint clean inside.", fontsize=8.5, va="top")

    fig.suptitle("Detail pass, part 2: the remaining small questions of the form. Each row: the present state, alternatives "
                 "at one scale, and the recommendation (green).", fontsize=13)
    os.makedirs(COMPARE, exist_ok=True)
    fig.savefig(os.path.join(COMPARE, "detail-options.png"), dpi=90)
    plt.close(fig)


if __name__ == "__main__":
    {"detail-options": detail_options}[sys.argv[1]]()
