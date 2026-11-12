"""Sheets of the detail pass on the outer form (revision 6), for the owner.

    cad/.venv-tools/bin/python cad/tools/draw_detail.py rear-options   -> cad/out/shell-bp/compare/rear-fillet-options.png
    cad/.venv-tools/bin/python cad/tools/draw_detail.py before-after   -> cad/out/shell-bp/compare/rear-fillet-before-after.png
    cad/.venv-tools/bin/python cad/tools/draw_detail.py detail-options -> cad/out/shell-bp/compare/detail-options.png

rear-options draws the plan outline of the right rear corner at three heights (the lower rear, the upper rear where
the step runs into the corner, the hood) for three radii of the corner round, from profiles.body_rounds and
profiles.hood_round, with the outline of revision 5 dashed. before-after puts the renders of revision 5
(cad/out/shell-bp-rev5/renders) beside those of the build (cad/out/shell-bp/renders). detail-options draws the
remaining small questions of the form, each at one scale: the present state, the alternatives and the
recommendation.

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
from matplotlib.patches import Circle, Polygon, Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(HERE)
sys.path.insert(0, CAD)
from candybar.shell import profiles as pr  # noqa: E402
from candybar.shell.dims import Blueprint  # noqa: E402

COMPARE = os.path.join(CAD, "out", "shell-bp", "compare")
INK, RED, BLUE, GREY, GREEN = "#1c1c1f", "#b0302a", "#1f4e8c", "#9a9aa0", "#2f7a3a"
WALL = 4.0
DOOR_LAND = 4.0  # fit.Layout.door_land
CLEAR = 5.0      # fit.Layout.corner_clear


# ---------- the plan outline of the right rear corner ----------

def body_outline(d: Blueprint, z: float) -> list[tuple[float, float]]:
    """The plan outline of the body's right rear corner at height z: the side band, the step, the rear body side and
    the corner round, then the rear wall."""
    s, y0, yr = d.side_x(min(z, d.body_top)), d.step_y(z), d.rear_y(z)
    xb, yb = s - d.step_in, y0 + d.step_in
    if yb >= yr:
        xb, yb = s - (yr - y0), yr
    edge, corner = pr.body_rounds(d, z)
    pts = [(s, y0 - 45.0)]
    pts += edge.points(12) if edge else [(s, y0)]
    if corner.a0 < math.pi / 4 - 1e-6:
        pts.append((xb, yb))
    pts += corner.points(24)
    pts.append((corner.c[0] - 60.0, yr))
    return pts


def body_outline_rev5(d: Blueprint, z: float) -> list[tuple[float, float]]:
    s, y0, yr = d.side_x(z), d.step_y(z), d.rear_y(z)
    if y0 + d.step_in < yr:
        return [(s, y0 - 45.0), (s, y0), (s - d.step_in, y0 + d.step_in), (s - d.step_in, yr), (s - d.step_in - 60.0 - d.rear_corner_r, yr)]
    return [(s, y0 - 45.0), (s, y0), (s - (yr - y0), yr), (s - 80.0, yr)]


def hood_outline(d: Blueprint, z: float) -> tuple[list, list]:
    h = pr.hood(d)
    back = pr.hood_back(d, h)
    rd = pr.hood_round(d, h, back, z)
    x, y = back.x(z), h.origin[1] + back.y(z)
    new = [(x, y - 45.0)] + rd.points(24) + [(rd.c[0] - 60.0, y)]
    # revision 5: the plane at 45 degrees in plan through the corner of the step in the body top
    c = d.side_x(d.body_top) + d.step_y(d.body_top)
    old = [(x, y - 45.0)]
    if x + y > c:
        old += [(x, c - x), (c - y, y)]
    else:
        old.append((x, y))
    old.append((rd.c[0] - 60.0, y))
    return new, old


def draw_corner(ax, new, old, title: str, note_lines: list[str]) -> None:
    ax.plot(*zip(*old), color=GREY, lw=1.2, ls="--", label="revision 5")
    ax.plot(*zip(*new), color=INK, lw=1.8, label="this radius")
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=9)
    ax.tick_params(labelsize=7)
    for k, line in enumerate(note_lines):
        ax.text(0.02, 0.04 + 0.075 * k, line, transform=ax.transAxes, fontsize=7, color=BLUE)


def rear_options() -> None:
    """Plan outlines of the right rear corner for three radii: a small one, the one built, a large one."""
    d0 = Blueprint()
    radii = ((10.0, "small"), (d0.rear_corner_r, "built"), (25.0, "large"))
    z_lo, z_up = 150.0, 412.0
    fig, axes = plt.subplots(3, 3, figsize=(17, 16))
    for col, (r, word) in enumerate(radii):
        d = replace(d0, rear_corner_r=r)
        z1, zm = d.runout_z
        door = d.rear_w / 2 - r - DOOR_LAND
        psu = min(d.rear_w / 2 - WALL - 8.0, d.rear_w / 2 - r - CLEAR)
        rb1_foot = d.rear_y(d.rear_step_z0) - (d.step_y(d.rear_step_z0) + d.step_in)
        # lower rear: the door edge, the power supply's corner and the inner skin
        ax = axes[0, col]
        draw_corner(ax, body_outline(d, z_lo), body_outline_rev5(d, z_lo), f"R {r:g} ({word}), lower rear z {z_lo:.0f}", [])
        corner = pr.body_rounds(d, z_lo)[1]
        ax.add_patch(Circle(corner.c, r - WALL, fill=False, color=GREY, lw=0.8, ls=":"))
        ax.axvline(door, color=RED, lw=0.9)
        ax.text(door - 1, d.body_d + 6, f"door edge x {door:.1f}\n(opening {2 * door:.1f}, was 446.7)", color=RED, fontsize=7, ha="right")
        ax.add_patch(Rectangle((psu - 40, d.body_d - WALL - 40), 40, 40, fill=False, color=GREEN, lw=1.0))
        ax.text(psu - 38, d.body_d - WALL - 36, f"power supply, its left face\n at x {-psu:.1f} (was -223.4)", color=GREEN, fontsize=7)
        ax.set_xlim(d.width / 2 - 75, d.width / 2 + 8)
        ax.set_ylim(d.body_d - 62, d.body_d + 18)
        # upper rear: where the step runs into the corner
        ax = axes[1, col]
        draw_corner(ax, body_outline(d, z_up), body_outline_rev5(d, z_up), f"R {r:g}, upper rear z {z_up:.0f} (the step runs into the round)", [])
        gx1 = door
        ax.axvline(gx1, color=RED, lw=0.9)
        ax.text(gx1 - 1, d.depth + 4, f"grip pocket ends x {gx1:.1f}", color=RED, fontsize=7, ha="right")
        ax.set_xlim(d.width / 2 - 75, d.width / 2 + 8)
        ax.set_ylim(d.depth - 62, d.depth + 14)
        # hood
        ax = axes[2, col]
        new, old = hood_outline(d, 60.0)
        draw_corner(ax, new, old, f"R {r:g}, hood 60 above its foot", [])
        ax.set_xlim(new[0][0] - 75, new[0][0] + 8)
        ax.set_ylim(d.depth - 62, d.depth + 14)
        psu_move = max(0.0, (d.rear_w / 2 - WALL - 8.0) - (d.rear_w / 2 - r - CLEAR))
        duct_move = max(0.0, (d.rear_w / 2 - WALL - 4.0) - (d.rear_w / 2 - r - CLEAR))
        moves = f"power supply {psu_move:+.0f}, BC-250 and its duct {duct_move:+.0f} toward the centre line"
        limits = {
            "small": [f"Fits everything: door {2 * door:.1f} ({2 * door - 446.7:+.1f}); {moves}.",
                      f"But the step reaches the body top {d.depth - d.step_y(d.body_top):.1f} from the rear wall, so it cannot run",
                      "out into a round this small: the foot of the hood keeps a flat at 45 deg, or the groove jogs.",
                      "It reads hard next to the hood's top rear R 10 and the deck's front corner R 44.5."],
            "built": [f"Largest that passes. Limits: the rear body side is {rb1_foot:.1f} long at the foot of the slope (z 310),",
                      f"and the step must run out into the round inside the seam bevel (R 16.4 to 19.1); here at z {zm:.1f}.",
                      f"Door {2 * door:.1f} ({2 * door - 446.7:+.1f}); {moves}.",
                      "Beside the door: 4 flat, then the round. The supply stands 5 inside the start of the round (inner skin R 14)."],
            "large": [f"The round runs over the step's inner crease at the foot of the slope ({rb1_foot:.1f} long there),",
                      f"and the step runs out at z {zm:.1f}, {d.body_top - zm:.1f} below the body top: a second blend under the groove.",
                      f"Door {2 * door:.1f} ({2 * door - 446.7:+.1f}); {moves}: the slot vents lose width.",
                      "It reads soft, near bulbous where it meets the hood's top rear R 10."],
        }[word]
        for k, line in enumerate(limits):
            axes[0, col].text(0.0, -0.14 - 0.06 * k, line, transform=axes[0, col].transAxes, fontsize=7.5, color=INK)
    axes[0, 0].legend(fontsize=7, loc="upper left")
    fig.suptitle("Rear corner round: the plan outline of the right rear corner (x across, y toward the rear), one scale, for three radii.\n"
                 "Dashed: revision 5 (sharp corners, the step's 45 deg run-out, the flat corner face HC16 on the hood). Dotted: the inner skin (4 mm).",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.subplots_adjust(hspace=0.55)
    os.makedirs(COMPARE, exist_ok=True)
    fig.savefig(os.path.join(COMPARE, "rear-fillet-options.png"), dpi=110)
    plt.close(fig)


# ---------- before and after ----------

def before_after() -> None:
    before = os.path.join(CAD, "out", "shell-bp-rev5", "renders")
    after = os.path.join(CAD, "out", "shell-bp", "renders")
    views = ("three-quarter-rear-left", "rear", "side-right", "top", "closeup-seam-rear-corner")
    fig, axes = plt.subplots(2, len(views), figsize=(4.2 * len(views), 9))
    for k, v in enumerate(views):
        for row, (folder, word) in enumerate(((before, "revision 5"), (after, "revision 6"))):
            ax = axes[row, k]
            ax.axis("off")
            path = os.path.join(folder, f"{v}.png")
            if os.path.exists(path):
                ax.imshow(plt.imread(path))
            ax.set_title(f"{word}: {v}", fontsize=9)
    fig.suptitle("The vertical corners of the back: revision 5 (top) and revision 6 with the rear corner round R 18 (bottom)", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(os.path.join(COMPARE, "rear-fillet-before-after.png"), dpi=100)
    plt.close(fig)


# ---------- part 2: the rest of the detail pass ----------

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

    # 2. the crease behind the stripe: plan section of the side band and the step
    def step_plan(depth: float, lean_back: float = 1.0) -> list[tuple[float, float]]:
        return [(0.0, -60.0), (0.0, 0.0), (-depth, depth * lean_back), (-depth, 60.0)]
    for k, (title, pts, rec) in enumerate((
            ("Q3 now: a step 12 deep, 45 deg in plan", step_plan(12.0), True),
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
    ax.text(0, 0.95, "Q3 recommendation: keep the step of 12.", fontsize=10, color=GREEN, fontweight="bold", va="top")
    ax.text(0, 0.82, "The rear corner round of revision 6 is sized on it: the\nstep sets R 18 (the rear body side is 18.2 long at the\n"
            "slope foot). A deeper step (20) cuts the round to about\nR 10 and narrows the rear body by 16; a shallow line\n"
            "frees the round (R 25 possible) but loses the break\nthat ends the stripe and hides seam S1.", fontsize=8.5, va="top")

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
    {"rear-options": rear_options, "before-after": before_after, "detail-options": detail_options}[sys.argv[1]]()
