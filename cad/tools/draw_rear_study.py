"""Sheets of the rear form study (revision 7 candidates): cad/out/shell-bp/compare/rear-rev7-*.png.

The models come from candybar.shell.rear_study (cad/out/shell-bp-rev7/<name>/, and rev6/ for revision 6). Every render
draws all BREP face boundaries (edges.json of each model, see render_views.py). Steps:

    cad/.venv-tools/bin/python cad/tools/draw_rear_study.py render     # Blender, one model at a time
    cad/.venv-tools/bin/python cad/tools/draw_rear_study.py sheets     # the five sheets
    cad/.venv-tools/bin/python cad/tools/draw_rear_study.py costs      # the numbers of the cost list (Markdown)
    cad/.venv-tools/bin/python cad/tools/draw_rear_study.py render-r2  # R2 and its flares, and R with R2's cameras
    cad/.venv-tools/bin/python cad/tools/draw_rear_study.py sheets-r2  # rear-rev7-r2-corner.png, rear-rev7-r2-flare.png
    cad/.venv-tools/bin/python cad/tools/draw_rear_study.py render-r3  # R3 with R2's cameras
    cad/.venv-tools/bin/python cad/tools/draw_rear_study.py sheet-r3   # rear-rev7-r3.png
    cad/.venv-tools/bin/python cad/tools/draw_rear_study.py render-r4  # R4 with R3's cameras
    cad/.venv-tools/bin/python cad/tools/draw_rear_study.py sheet-r4   # rear-rev7-r4.png
    cad/.venv-tools/bin/python cad/tools/draw_rear_study.py render-r5  # R5a and R6 with R4's cameras (and R6's hood corner)
    cad/.venv-tools/bin/python cad/tools/draw_rear_study.py sheet-r5   # rear-rev7-r5.png

Needs numpy, Pillow and matplotlib (cad/.venv-tools); no FreeCAD.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from compose_sheet import font, project  # noqa: E402
from candybar.shell.dims import Blueprint  # noqa: E402

ROOT = os.path.dirname(HERE)
STUDY = os.path.join(ROOT, "out", "shell-bp-rev7")
RENDERS = os.path.join(STUDY, "renders")
COMPARE = os.path.join(ROOT, "out", "shell-bp", "compare")
FIT = os.path.join(ROOT, "out", "shell-bp", "fit", "sections.json")
FRAME = "-252,-6,-2,252,586,578"
MAIN = ("rear", "three-quarter-rear-right", "side-right")
CLOSE = ("closeup-seam-corner", "closeup-step-top", "closeup-roll-corner", "closeup-base-corner", "closeup-deck-front-low", "closeup-cut-ins")
MODELS = {"rev6": "Revision 6", "A": "A: present rear, repaired", "R": "R: roll, smile, grips, cut-ins", "A25": "A, corner R 25",
          "A-cut": "A with cut-ins (R 18)", "A-e3": "A, creases R 3 / R 20", "A-e8": "A, creases R 8 / R 20", "A-e15": "A, creases R 15 / R 20",
          "A-ch3": "A, base chamfer 3",
          "A-ch8": "A, base chamfer 8"}
R2_MODELS = {"R2": "R2: head at full width", "R2Fb": "R2Fb: inner crease flares", "R2Fa": "R2Fa: whole band flares",
             "R2Fm": "R2Fm: mix (outer 30, inner 80)"}
R2_VIEWS = ("three-quarter-rear-right", "side-right", "rear", "closeup-r2-corner", "closeup-turn", "three-quarter-rear-above", "flare-foot",
            "closeup-roll-corner", "closeup-step-top", "closeup-seam-corner", "closeup-base-corner", "closeup-cut-ins")
R_CAMS = "R-r2cams"
RECOMMEND = "R"
INK, MUTED, ACCENT, HW = (30, 30, 34), (110, 110, 118), (200, 40, 40), (40, 90, 200)
D = Blueprint()
TAN = math.tan(math.radians(22.5))
DOOR_LAND, DOOR_FRAME, CORNER_CLEAR = 4.0, 12.0, 5.0
PSU = dict(x0=-212.35, w=150.0, z0=10.0, h=86.0, y1=536.0, d=150.0)
INLET = dict(x0=95.0, x1=205.0, z0=15.0, z1=108.0)
BOARD_TOP = 268.0


# ---------- the numbers of a candidate ----------

def variant(name: str) -> dict:
    if name == "rev6":
        return {"name": "rev6", "corner_r": 18.0, "crease_lo": [540.0, 310.0, 0.0], "crease_hi": [580.0, 350.0, 0.0], "smile": 0.0,
                "cut_ins": None, "grips": None, "chamfer": 0.0}
    return json.load(open(os.path.join(STUDY, name, "report.json")))["variant"]


def rear_x(z: float = 0.0) -> float:
    return D.side_x(z) - D.step_in


def layout(name: str) -> dict:
    """Door, power supply face, inlet, cut-ins and grips in the rear elevation (x to the player's right, z up)."""
    v = variant(name)
    r = v["corner_r"]
    lo = v["crease_lo"]
    shelf, planar = v.get("shelf") or {}, v.get("planar") or {}
    lo_r = shelf["constant"][0] if shelf.get("constant") else planar.get("fillet", lo[2])  # R4/R5a/R6: the crease's own round
    roll_foot = lo[1] - lo_r * TAN
    door_half = rear_x() - r - DOOR_LAND
    if planar:                                       # R6: the cut-ins' rear legs bound the door, not the corner
        door_half = rear_x() - planar["cut_rear"] - DOOR_LAND
    door = (-door_half, 116.0, door_half, roll_foot - DOOR_FRAME)
    round_start = rear_x() - r
    psu_x0 = max(PSU["x0"], -round_start + CORNER_CLEAR)
    out = {"v": v, "door": door, "roll_foot": roll_foot, "round_start": round_start, "psu": (psu_x0, PSU["z0"], psu_x0 + PSU["w"], PSU["z0"] + PSU["h"]),
           "psu_move": psu_x0 - PSU["x0"], "inlet": (INLET["x0"], INLET["z0"], INLET["x1"], INLET["z1"])}
    c = v.get("cut_ins")
    if c:
        out["cut_ins"] = [(c["z0"] + k * c["pitch"], c["z0"] + k * c["pitch"] + c["height"]) for k in range(c["count"])]
    g = v.get("grips")
    if g:
        out["grips"] = (g["x0"], g["z0"], g["x1"], g["z0"] + g["height"])
    return out


def costs(name: str) -> list[tuple[str, str]]:
    """The cost list of a candidate against revision 6, from its numbers (estimates: no fit run)."""
    L, base = layout(name), layout("rev6")
    v = L["v"]
    r = v["corner_r"]
    door = L["door"]
    rows = []
    rows.append(("Rear door opening", f"{door[2] - door[0]:.1f} x {door[3] - door[1]:.1f} (x {door[0]:.1f} to {door[2]:.1f}, z {door[1]:.0f} to {door[3]:.1f}); "
                 f"revision 6 {base['door'][2] - base['door'][0]:.1f} x {298 - 116:.0f}"))
    rows.append(("BC-250 behind the door", f"board top z {BOARD_TOP:.0f}: {door[3] - BOARD_TOP:+.1f} below the door top; the duct must move "
                 f"{max(0.0, (-door[2] + 1) - (-212.3)):.1f} to the right to stay 1 inside the door and {CORNER_CLEAR:.0f} inside the round"))
    psu = L["psu"]
    rows.append(("Power supply face 150 x 86", f"x {psu[0]:.1f} to {psu[2]:.1f}, z 10 to 96: on the flat of the wall "
                 f"({psu[0] + L['round_start']:.1f} from the start of the round); moves {L['psu_move']:.1f} toward the centre"))
    bundle_x1 = psu[2] + 6 + 140
    rows.append(("Stowed cables right of the supply", f"x {psu[2] + 6:.1f} to {bundle_x1:.1f}: {INLET['x0'] - bundle_x1:.1f} left of the inlet grille"))
    if "cut_ins" in L:
        c = v["cut_ins"]
        rows.append(("Cut-ins", f"{c['count']} grooves {c['height']:.0f} high, pitch {c['pitch']:.0f}, {c['depth']:.0f} deep, z {L['cut_ins'][0][0]:.0f} to "
                     f"{L['cut_ins'][-1][1]:.0f}; {L['cut_ins'][0][0] - 96:.0f} above the supply's top; on the round and the side, not on the door land"))
    if "grips" in L:
        g = L["grips"]
        rows.append(("Hand-holds", f"x {g[0]:.0f} to {g[2]:.0f} each side, z {g[1]:.0f} to {g[3]:.0f}, {v['grips']['depth']:.0f} deep; level with the monitor's top clamp "
                     "(z 364 to 379) but 114 behind it (y 440 against 554); below the seam, so the hood interior is not touched"))
    return rows


# ---------- renders ----------

def render() -> None:
    script = os.path.join(HERE, "render_views.py")
    for name in MODELS:
        model = os.path.join(STUDY, name)
        if not os.path.isdir(model):
            print("missing", model)
            continue
        views = ",".join(MAIN + CLOSE)
        focus = json.load(open(os.path.join(model, "focus.json")))
        views = ",".join(v for v in views.split(",") if v in MAIN or v in focus)
        out = os.path.join(RENDERS, name)
        subprocess.run([sys.executable, script, out, model, "--views", views, f"--frame={FRAME}", "--size", "1100", "--samples", "16"], check=True)


# ---------- sheets ----------

def tile(name: str, view: str, w: int) -> Image.Image:
    path = os.path.join(RENDERS, name, f"{view}.png")
    if not os.path.exists(path):
        im = Image.new("RGB", (w, 40), (245, 245, 245))
        ImageDraw.Draw(im).text((10, 10), "no such element on this model", fill=MUTED, font=font(16))
        return im
    im = Image.open(path).convert("RGB")
    if view == "rear":
        im = rear_marks(im, name, view)
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def rear_marks(im: Image.Image, name: str, view: str) -> Image.Image:
    """The power supply's rear face (not cut in the solids), the door and the inlet grille, drawn on the rear view."""
    cams = json.load(open(os.path.join(RENDERS, name, "views.json")))["views"]
    cam = cams[view]
    L = layout(name)
    dr = ImageDraw.Draw(im)
    y = D.body_d + 0.5

    def box(b, colour, width=2, dash=False):
        pts = project(cam, np.array([[b[0], y, b[1]], [b[2], y, b[1]], [b[2], y, b[3]], [b[0], y, b[3]], [b[0], y, b[1]]]))
        if dash:
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 8))
                for k in range(0, n, 2):
                    dr.line([(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n), (x0 + (x1 - x0) * (k + 1) / n, y0 + (y1 - y0) * (k + 1) / n)], fill=colour, width=width)
        else:
            dr.line([tuple(p) for p in pts], fill=colour, width=width)
        return pts

    box(L["door"], (60, 60, 60), 2, dash=True)
    p = L["psu"]
    box(p, HW, 2)
    # generic ATX rear face, fan up: mains socket and switch at the outer (left) end, grille over the rest
    sock = (p[0] + 8, p[1] + 20, p[0] + 38, p[1] + 44)
    sw = (p[0] + 10, p[1] + 52, p[0] + 30, p[1] + 66)
    box(sock, HW, 2)
    box(sw, HW, 2)
    for k in range(6):
        x = p[0] + 50 + k * 16
        box((x, p[1] + 10, x + 10, p[3] - 10), HW, 1)
    box(L["inlet"], (0, 140, 90), 2, dash=True)
    f = font(26, bold=True)
    q = project(cam, np.array([[p[0], y, p[3] + 4]]))[0]
    dr.text((q[0] - 330, q[1] - 62), "supply face (generic ATX,\nlayout not measured)", fill=HW, font=f)
    q = project(cam, np.array([[L["inlet"][0], y, L["inlet"][3] + 4]]))[0]
    dr.text((q[0] - 120, q[1] - 32), "inlet grille", fill=(0, 140, 90), font=f)
    q = project(cam, np.array([[L["door"][2] - 10, y, L["door"][3] - 8]]))[0]
    dr.text((q[0], q[1]), "door opening", fill=(60, 60, 60), font=f)
    return im


def label(im: Image.Image, text: str, size: int = 22, colour=INK, at=(12, 8)) -> None:
    ImageDraw.Draw(im).text(at, text, fill=colour, font=font(size, bold=True))


def grid(rows: list[list[Image.Image]], row_labels: list[str], col_labels: list[str], title: str, notes: list[str], highlight: int | None = None,
         gap: int = 10) -> Image.Image:
    import textwrap
    cw = [max(r[c].width for r in rows) for c in range(len(rows[0]))]
    width_chars = max(60, int((300 + sum(cw) + gap * (len(cw) + 1) - 40) / 10.5))
    notes = textwrap.wrap(" ".join(notes), width_chars)
    rh = [max(im.height for im in r) for r in rows]
    left, top = 300, 110
    W = left + sum(cw) + gap * (len(cw) + 1)
    H = top + sum(rh) + gap * (len(rh) + 1) + 40 + 26 * len(notes)
    sheet = Image.new("RGB", (W, H), (255, 255, 255))
    dr = ImageDraw.Draw(sheet)
    dr.text((20, 20), title, fill=INK, font=font(34, bold=True))
    y = top
    for i, (r, h) in enumerate(zip(rows, rh)):
        x = left + gap
        if highlight == i:
            dr.rectangle([6, y - 6, W - 6, y + h + 6], outline=ACCENT, width=5)
            dr.text((20, y + 100), "RECOMMENDED", fill=ACCENT, font=font(22, bold=True))
        dr.multiline_text((20, y + 10), row_labels[i], fill=INK, font=font(22, bold=True), spacing=6)
        for c, im in enumerate(r):
            sheet.paste(im, (x, y))
            if i == 0:
                dr.text((x, top - 34), col_labels[c], fill=MUTED, font=font(20))
            x += cw[c] + gap
        y += h + gap
    y += 20
    for n in notes:
        dr.text((20, y), n, fill=INK, font=font(19))
        y += 26
    return sheet


def reference_sketch(w: int, h: int) -> Image.Image:
    """A line sketch of the maker's mini rear in proportion to its width (own drawing from the estimates of Part 1)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(w / 100, h / 100), dpi=100)
    W = 1.0
    body_h = 1.0
    head_foot = 0.55        # the smile's lowest point, of the body height (estimated)
    corner_up = 0.17        # how far the smile rises at its ends (estimated)
    xs = np.linspace(-0.5, 0.5, 200)
    smile = head_foot + corner_up * (np.abs(xs) / 0.5) ** 4
    ax.plot([-0.5, -0.5, 0.5, 0.5], [0.70, body_h, body_h, 0.70], "k-", lw=1.4)
    ax.plot(xs, smile, "k-", lw=1.4)
    ax.plot([-0.44, -0.44], [0.03, head_foot + 0.02], "k-", lw=1.0)
    ax.plot([0.44, 0.44], [0.03, head_foot + 0.02], "k-", lw=1.0)
    ax.plot([-0.5, -0.5], [0.70, 0.04], "k:", lw=0.8)
    ax.plot([0.5, 0.5], [0.70, 0.04], "k:", lw=0.8)
    ax.plot([-0.44, 0.44], [0.03, 0.03], "k-", lw=1.0)
    ax.add_patch(plt.Rectangle((-0.30, 0.13), 0.60, 0.38, fill=False, lw=1.2))
    for x0 in (-0.36, 0.14):
        ax.add_patch(plt.Rectangle((x0, 0.68), 0.22, 0.20, fill=False, lw=1.2))
    for sgn in (-1, 1):
        for k in range(4):
            z = 0.14 + k * 0.075
            ax.plot([sgn * 0.33, sgn * 0.44], [z, z], "k-", lw=2.2, solid_capstyle="round")
    ax.text(0, -0.08, "maker's mini, rear (own line sketch; proportions estimated\nfrom photo-f: head, smile, 2 recesses, door, 4 cut-ins a side)",
            ha="center", va="top", fontsize=8)
    ax.set_xlim(-0.6, 0.6)
    ax.set_ylim(-0.2, 1.05)
    ax.set_aspect("equal")
    ax.axis("off")
    path = os.path.join(RENDERS, "reference-sketch.png")
    fig.savefig(path, dpi=100)
    plt.close(fig)
    return Image.open(path).convert("RGB").resize((w, h), Image.LANCZOS)


def sheet_overview() -> None:
    names = ["rev6", "A", "R"]
    w = 520
    rows = [[tile(n, v, w) for v in MAIN] for n in names]
    sk = reference_sketch(w, rows[0][0].height)
    rows[0].append(sk)
    for r in rows[1:]:
        r.append(Image.new("RGB", (w, 10), (255, 255, 255)))
    notes = ["All face boundaries of the BREP are drawn (exact edges, hidden ones removed). Rear view: blue = the power supply's rear face (not cut in the solids;",
             "generic ATX face, layout not measured), dashed grey = door opening, dashed green = inlet grille. Same frame and scale in every view of a column.",
             "A: step ends on the seam at y 537 in front of the corner round; hood full width overhangs the rear body by 12; creases R 20; corner R 18; step edges R 10 / R 6.",
             "R: roll (R 25 concave, R 60 convex) whose foot is a smile (24 higher at the corners), corner R 25, two hand-holds in the head, 4 cut-ins a corner.",
             "Base chamfer 5 all round on A and R. Recommended: R (see the cost sheet); A is the fallback with the least change."]
    sheet = grid(rows, [MODELS[n].replace(": ", ":\n") for n in names], [*MAIN, "reference (line sketch)"], "Rear form, revision 7 candidates (rear view seen from behind: the player's left is on the right)", notes,
                 highlight=names.index(RECOMMEND))
    sheet.save(os.path.join(COMPARE, "rear-rev7-overview.png"))


def sheet_junction() -> None:
    names = ["rev6", "A", "A25", "R", "A-cut"]
    views = ["closeup-seam-corner", "closeup-step-top", "closeup-roll-corner", "closeup-cut-ins"]
    w = 430
    rows = [[tile(n, v, w) for v in views] for n in names]
    notes = ["Close-ups with all face edges drawn. Revision 6: the fan of narrow faces where the step runs out into the corner round, and the stack of strips on the slope.",
             "A / A25 / R: the step ends on the seam with its full section; 10 of flat rear body side to the seam in front of the corner round; the hood (full width) overhangs by 12.",
             "Hood corner = body corner + 12, so both rounds leave the rear wall on the same line. Cut-ins: on R 18 (A with cut-ins) the grooves are mostly on the side;",
             "on R 25 (R) they wrap the round. Grooves start 6 round the corner because the door land is only 4 wide."]
    sheet = grid(rows, [MODELS[n].replace(": ", ":\n") for n in names], views, "Rear junctions, close-ups", notes, highlight=names.index(RECOMMEND))
    sheet.save(os.path.join(COMPARE, "rear-rev7-junction.png"))


def sheet_edges() -> None:
    names = ["A-e3", "A-e8", "A-e15", "A", "R"]
    views = ["three-quarter-rear-right", "side-right", "closeup-roll-corner"]
    w = 480
    rows = [[tile(n, v, w) for v in views] for n in names]
    notes = ["Lower crease (concave, under the overhang) R 3 / R 8 / R 15 / R 20; upper crease (convex) R 20 in all. The corner round is one rolling ball from the floor",
             "to the body top, inside the material: its path is the rear profile moved in by the corner radius, so the upper (convex) crease must be larger than the corner",
             "round (R 18 on A, R 25 on R), or the round cannot be made (tested: R 8 and R 17 fail under R 18). The lower crease is free of that limit, but its tangent line",
             "must stay clear of the start of the tuck (z 306.7): R 8 ends exactly there (a face of zero width: fails), R 15 leaves a piece 1.9 wide (fails); R 3 and R 20 pass.",
             "Recommended for A: R 20 / R 20 (one even S; reads as a soft step; passes).",
             "R takes the idea further: R 25 / R 60, a roll. Step: outer edge R 10 (the base chamfer collapses or tapers on a smaller convex round), inner crease R 6."]
    sheet = grid(rows, [MODELS[n].replace(": ", ":\n").replace(", ", ",\n") for n in names], views, "Creases of the rear: sizes", notes, highlight=3)
    sheet.save(os.path.join(COMPARE, "rear-rev7-edges.png"))


def chamfer_section(w: int, h: int) -> Image.Image:
    """The foot of the wall in section for chamfers 3, 5, 8, and the paint radius R 1 and R 2 at 1:1."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 4, figsize=(w / 100, h / 100), dpi=100, gridspec_kw={"width_ratios": [1, 1, 1, 1.25]})
    for ax, c in zip(axs[:3], (3, 5, 8)):
        pad = 2.5
        ax.add_patch(plt.Polygon([(0, pad), (-40, pad), (-40, pad + 10), (-4, pad + 10), (-4, pad + 40), (0, pad + 40), (0, pad + c), (-c, pad)], closed=True,
                                 fc="#dfe3ea", ec="k", lw=1.2))
        ax.plot([-40, 0], [pad + 10, pad + 10], "k-", lw=0.8)
        ax.add_patch(plt.Rectangle((-30, 0), 10, pad, fc="#888", ec="k", lw=0.6))
        ax.plot([-45, 8], [0, 0], color="#555", lw=1.0)
        ax.annotate("", xy=(-c, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="<->", lw=0.6))
        ax.text(2, pad + 10, "wall 4 on\nfloor 10", fontsize=7, va="center")
        ax.text(-38, pad + 4, "floor tile (10)", fontsize=7)
        ax.text(-30, -3.5, "pad 2-3", fontsize=7)
        ax.set_title(f"chamfer {c}: {10 - c} of floor edge left\nunder the joint; gap at the edge {c + pad:.1f}", fontsize=8)
        ax.set_xlim(-45, 14)
        ax.set_ylim(-6, 46)
        ax.set_aspect("equal")
        ax.axis("off")
    ax = axs[3]
    ax.set_title("paint radius at the edges, 5:1 (true size: print\nthe 1:1 strip at 300 dpi)", fontsize=8)
    for k, r in enumerate((1.0, 2.0)):
        ox = k * 14
        t = np.linspace(0, math.pi / 2, 30)
        xs = np.concatenate([[ox - 8, ox - r], ox - r + r * np.sin(t), [ox, ox]])
        ys = np.concatenate([[0, 0], r - r * np.cos(t), [r, 8]])
        ax.fill(np.concatenate([xs, [ox - 8]]), np.concatenate([ys, [8]]), fc="#dfe3ea", ec="k", lw=1.0)
        ax.text(ox - 4, -2.5, f"R {r:g}", ha="center", fontsize=8)
    ax.set_xlim(-10, 18)
    ax.set_ylim(-4, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    path = os.path.join(RENDERS, "chamfer-section.png")
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)
    return Image.open(path).convert("RGB")


def strip_1to1() -> Image.Image:
    """R 1 and R 2 on a 90 degree edge at true size for 300 dpi (11.81 px per mm), with a 10 mm bar."""
    k = 300 / 25.4
    im = Image.new("RGB", (round(60 * k), round(16 * k)), (255, 255, 255))
    dr = ImageDraw.Draw(im)
    for i, r in enumerate((1.0, 2.0)):
        ox = (8 + i * 26) * k
        pts = [(ox - 8 * k, 12 * k), (ox - 8 * k, 4 * k)]
        for a in np.linspace(0, math.pi / 2, 20):
            pts.append((ox - r * k + r * k * math.sin(a), 4 * k + r * k - r * k * math.cos(a)))
        pts += [(ox, 12 * k)]
        dr.polygon(pts, fill=(223, 227, 234), outline=INK)
        dr.text((ox - 6 * k, 13 * k), f"R {r:g}", fill=INK, font=font(14))
    dr.line([(48 * k, 13 * k), (58 * k, 13 * k)], fill=INK, width=2)
    dr.text((48 * k, 10 * k), "10 mm", fill=INK, font=font(12))
    return im


def sheet_base() -> None:
    names = ["A-ch3", "A", "A-ch8"]
    views = ["closeup-base-corner", "closeup-deck-front-low"]
    w = 520
    rows = [[tile(n, v, w) for v in views] for n in names]
    sec = chamfer_section(1100, 360)
    sheet = grid(rows, ["base chamfer 3", "base chamfer 5\n(A, R)", "base chamfer 8"], views, "Base chamfer: 3, 5, 8", [
        "The chamfer lies in the floor tile's edge (z 0 to 10): the 4 mm wall stands on the floor, so no size cuts the wall foot. It leaves 10 - c of upright floor",
        "edge under the joint line of floor and wall (8: a 2 mm land, a seam close above the chamfer). With the pads (2 to 3) the gap at the front edge is c + pad:",
        "5.5 / 7.5 / 10.5 for 3 / 5 / 8: room for fingertips at 5 and 8. Recommended 5. A convex round in plan must be at least c + 3 (the step's outer edge: R 10),",
        "or the chamfer collapses or tapers there. Paint radius: R 1 or R 2 on every other outside edge (stage 2); R 2 holds paint and primer better on a sanded edge."],
        highlight=1)
    out = Image.new("RGB", (sheet.width, sheet.height + sec.height + 300), (255, 255, 255))
    out.paste(sheet, (0, 0))
    out.paste(sec, (20, sheet.height))
    st = strip_1to1()
    out.paste(st, (20, sheet.height + sec.height + 10))
    ImageDraw.Draw(out).text((40 + st.width, sheet.height + sec.height + 40), "1:1 at 300 dpi: R 1 and R 2 on an outside edge", fill=INK, font=font(18))
    out.save(os.path.join(COMPARE, "rear-rev7-base.png"))


def sheet_costs() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    sec = json.load(open(os.path.join(STUDY, "R", "sections.json")))
    fit = json.load(open(FIT))["rear"]["items"]
    L = layout("R")
    move = L["psu_move"]
    fig, axs = plt.subplots(2, 3, figsize=(24, 15), dpi=90)

    def draw(ax, name, title, hw_axes, lim):
        s = sec[name]
        for q in s["outer"]:
            q = np.array(q)
            ax.plot(q[:, 0], q[:, 1], "k-", lw=1.2)
        for q in s["inner"]:
            q = np.array(q)
            ax.plot(q[:, 0], q[:, 1], color="#888", lw=0.8)
        for it in fit:
            if it["role"] not in ("hardware", "keepout") or it["item"] not in ("Compute", "PSU", "CableBundle", "Hub", "Monitor", "Monitor, any 16:10"):
                continue
            box = {"x": (it["box"][0], it["box"][2]), "z": (it["box"][1], it["box"][3]), "y": tuple(it["y"])}
            axis = s["axis"]
            at = s["at"]
            dx = move if it["item"] in ("Compute", "PSU", "CableBundle") else 0.0
            key = "xyz"[axis]
            rng = (box[key][0] + (dx if key == "x" else 0), box[key][1] + (dx if key == "x" else 0))
            if not (rng[0] <= at <= rng[1]):
                continue
            a, b = hw_axes
            ra = (box[a][0] + (dx if a == "x" else 0), box[a][1] + (dx if a == "x" else 0))
            rb = (box[b][0] + (dx if b == "x" else 0), box[b][1] + (dx if b == "x" else 0))
            col = "#2860c8" if it["role"] == "hardware" else "#e09030"
            ax.add_patch(Rectangle((ra[0], rb[0]), ra[1] - ra[0], rb[1] - rb[0], fill=False, ec=col, lw=1.0, ls="-" if it["role"] == "hardware" else "--"))
            ax.text(ra[0] + 1, rb[1] - 6, it["solid"], fontsize=6, color=col, clip_on=True)
        ax.set_title(title, fontsize=12)
        ax.set_xlim(*lim[0])
        ax.set_ylim(*lim[1])
        ax.set_aspect("equal")
        ax.grid(True, lw=0.3)

    draw(axs[0, 0], "side x 0", "R, side section x 0: roll, door, BC-250", ("y", "z"), ((380, 600), (0, 440)))
    draw(axs[0, 1], "side x -205", "R, side section x -205: supply, cut-in zone", ("y", "z"), ((380, 600), (0, 440)))
    draw(axs[0, 2], "side x 120", "R, side section x 120: hand-hold", ("y", "z"), ((380, 600), (200, 440)))
    draw(axs[1, 0], "plan z 50", "R, plan z 50: supply, base, corner R 25", ("x", "y"), ((-250, 250), (380, 600)))
    draw(axs[1, 1], "plan z 160", "R, plan z 160: cut-ins, duct", ("x", "y"), ((-250, 250), (380, 600)))
    draw(axs[1, 2], "plan z 380", "R, plan z 380: hand-holds", ("x", "y"), ((-250, 250), (380, 600)))
    ax = axs[0, 0]
    d = L["door"]
    ax.plot([D.body_d, D.body_d], [d[1], d[3]], color="#c82828", lw=4, alpha=0.6)
    ax.text(D.body_d + 4, d[3] + 2, f"door top {d[3]:.1f}", color="#c82828", fontsize=9)
    ax.axhline(BOARD_TOP, color="#2860c8", lw=0.6, ls=":")
    ax.text(385, BOARD_TOP + 2, "board top 268", color="#2860c8", fontsize=8)
    ax = axs[1, 0]
    p = L["psu"]
    ax.add_patch(Rectangle((p[0], PSU["y1"] - PSU["d"]), PSU["w"], PSU["d"], fill=False, ec="#c82828", lw=1.5))
    ax.text(p[0] + 2, PSU["y1"] - 12, f"supply moved +{move:.0f}", color="#c82828", fontsize=9)
    fig.suptitle("Candidate R: sections with a 4 mm skin (grey: 2D inward offset, an estimate) and the hardware of the revision 6 fit, moved where R needs it",
                 fontsize=14)
    fig.tight_layout(rect=(0, 0.13, 1, 0.97))
    rows = costs("R")
    txt = "\n".join(f"{k}: {v}" for k, v in rows)
    fig.text(0.01, 0.01, "Cost list of R (estimates from sections, not a fit run; stage 2 proves them):\n" + txt, fontsize=10, va="bottom", family="DejaVu Sans")
    path = os.path.join(COMPARE, "rear-rev7-costs.png")
    fig.savefig(path, dpi=90)
    plt.close(fig)
    # the rear elevation of R with the door, supply face and inlet beside the sections
    im = Image.open(path).convert("RGB")
    rear = tile("R", "rear", 640)
    out = Image.new("RGB", (im.width + rear.width + 20, max(im.height, rear.height)), (255, 255, 255))
    out.paste(im, (0, 0))
    out.paste(rear, (im.width + 10, 60))
    ImageDraw.Draw(out).text((im.width + 10, 20), "R, rear: door, supply face, inlet", fill=INK, font=font(20, bold=True))
    out.save(path)


def sheets() -> None:
    os.makedirs(COMPARE, exist_ok=True)
    sheet_overview()
    sheet_junction()
    sheet_edges()
    sheet_base()
    sheet_costs()


def render_r2() -> None:
    """R2 and the flare variants with their cameras, and R with R2's cameras (from a model folder that points at R's
    files: R's own folders are not written)."""
    script = os.path.join(HERE, "render_views.py")
    for name in R2_MODELS:
        model = os.path.join(STUDY, name)
        if not os.path.isdir(model):
            print("missing", model)
            continue
        focus = json.load(open(os.path.join(model, "focus.json")))
        views = ",".join(v for v in R2_VIEWS if v in MAIN or v in focus)
        subprocess.run([sys.executable, script, os.path.join(RENDERS, name), model, "--views", views, f"--frame={FRAME}", "--size", "1100", "--samples", "16"], check=True)
    src, dst = os.path.join(STUDY, "R"), os.path.join(STUDY, R_CAMS)
    os.makedirs(dst, exist_ok=True)
    manifest = json.load(open(os.path.join(src, "manifest.json")))
    for e in manifest.values():
        e["file"], e["brep"] = os.path.join(src, e["file"]), os.path.join(src, e["brep"])
    json.dump(manifest, open(os.path.join(dst, "manifest.json"), "w"), indent=1)
    if not os.path.exists(os.path.join(dst, "edges.json")):
        os.symlink(os.path.join(src, "edges.json"), os.path.join(dst, "edges.json"))
    cams = json.load(open(os.path.join(STUDY, "R2", "focus.json")))
    json.dump({k: cams[k] for k in ("closeup-r2-corner", "closeup-turn", "three-quarter-rear-above", "flare-foot")}, open(os.path.join(dst, "focus.json"), "w"), indent=1)
    subprocess.run([sys.executable, script, os.path.join(RENDERS, R_CAMS), dst, "--views", "three-quarter-rear-right,side-right,closeup-r2-corner,closeup-turn,three-quarter-rear-above",
                    f"--frame={FRAME}", "--size", "1100", "--samples", "16"], check=True)


def r2_numbers(name: str) -> dict:
    return json.load(open(os.path.join(STUDY, name, "report.json")))


def sheet_r2_corner() -> None:
    views = ["three-quarter-rear-right", "closeup-r2-corner", "side-right"]
    w = 560
    rows = [[tile(R_CAMS, v, w) for v in views], [tile("R2", v, w) for v in views]]
    notes = ["All BREP face edges drawn. Same cameras in each column. R: the step runs up to the seam, so the rear body is 12 narrower than the hood on each side;",
             "the hood overhangs it with a soffit, the body corner is R 25 under a hood corner of R 37, and the roll wraps the narrow corner under the overhang.",
             "R2: the head is full width from the roll up to the seam; the set-back below is closed by a shoulder (12 out, 40 up, 73 degrees) that falls toward the",
             "front at 0.36 (20 degrees) from the rear corner (sharp lower crease z 322) to the turn (y 475.5, z 298.8), where the step's inner crease runs into it",
             "through a round of R 30. One corner round R 25 from the floor to the seam, and the hood's corner R 25 on the same line (the corner lines meet",
             "within 0.5 on the side and 1.0 on the rear across the seam; the hood corner is still the revision 6 loft, stage 2). Roll, smile, door, grips: as R.",
             "Rounds of the band: recessed edge R 7, full-width edge R 22 (R 16 at the floor, growing up the step), turn R 30, corner R 25."]
    sheet = grid(rows, ["R (revision 7\ncandidate)", "R2: head at\nfull width"], views, "Rear corner: R and R2 (owner markup 06)", notes)
    sheet.save(os.path.join(COMPARE, "rear-rev7-r2-corner.png"))


def sheet_r2_flare() -> None:
    names = [n for n in ("R2", "R2Fb", "R2Fa", "R2Fm") if os.path.isdir(os.path.join(RENDERS, n))]
    views = ["flare-foot", "side-right"]
    w = 470
    rows = [[tile(n, v, w) for n in names] for v in views]
    notes = ["All BREP face edges drawn; same camera in each row (top: the owner's sketch view, rear right, low; bottom: side). Flare from z 130, tangent to the",
             "leaning line (no kink), 80 behind the straight line at the floor. R2Fb (the owner's reading): only the inner crease curves back; the outer edge keeps its",
             "lean and one R 22 round to the floor; the facet widens into a ruled ramp (level rulings, exact), tangent to the plane facet at z 130. The recessed round",
             "grows from R 7 at z 130 to R 18 at the floor, as the ramp there turns only 7 degrees from the recessed side (R 7 would be 0.9 wide). R2Fa: the whole band",
             "curves back (same 45 degree section, R 7 / R 16-22). R2Fm: mix, outer edge 30 back, inner crease 80 back. Full-width floor edge gained per side",
             "(at the top of the base chamfer): R2Fb +6, R2Fa +73, R2Fm +34; footprint gained per side 450 / 880 / 610 mm2. All pass the face check; cut-ins untouched."]
    sheet = grid(rows, ["owner's view\n(rear right, low)", "side"], [R2_MODELS[n] for n in names], "Foot of the step: flare (owner markup 07)", notes)
    sheet.save(os.path.join(COMPARE, "rear-rev7-r2-flare.png"))


def sheets_r2() -> None:
    os.makedirs(COMPARE, exist_ok=True)
    sheet_r2_corner()
    sheet_r2_flare()


R3_VIEWS = ("three-quarter-rear-right", "closeup-r2-corner", "closeup-turn", "flare-foot", "side-right", "rear", "three-quarter-rear-above")


def render_r3(name: str = "R3") -> None:
    model = os.path.join(STUDY, name)
    subprocess.run([sys.executable, os.path.join(HERE, "render_views.py"), os.path.join(RENDERS, name), model, "--views", ",".join(R3_VIEWS),
                    f"--frame={FRAME}", "--size", "1100", "--samples", "16"], check=True)


def sheet_r4() -> None:
    views = ["three-quarter-rear-right", "closeup-r2-corner", "rear", "side-right"]
    w = 470
    rows = [[tile("R3", v, w) for v in views], [tile("R4", v, w) for v in views]]
    notes = ["All BREP face edges drawn; same camera in each column. R4: the band's run and the roll's underside are one 45 degree shelf, level at the rear corner",
             "(lower crease z 305.7), 12 deep on the side and 40 deep on the rear; round the corner it is the lower body's R 25 outline tapered out at 45 degrees",
             "(planes, and a cone on the arc), cut by the head. R's smile is kept to x 160 and eased to level at x 200 (tangent arc R 313): 0.3 lower at x 170, 2.6 at 190,",
             "4.9 at 200. The band's top arc is R 60 (R 80 does not reach level before the corner round). Rounds: one constant pair all round, R 12 at the lower crease",
             "and R 20 at the upper edge, so the roll is crisper than R's R 25 / R 60. Radii that change along the corner built clean but OpenCascade did not follow",
             "the radii set at the edges, and left lumps (not used). The corner moves outward once: no twist, no knuckle."]
    sheet = grid(rows, ["R3", "R4: one shelf"], views, "Rear: R3 and R4 (one shelf under the head)", notes)
    sheet.save(os.path.join(COMPARE, "rear-rev7-r4.png"))


def sheet_r3() -> None:
    views = ["three-quarter-rear-right", "closeup-r2-corner", "flare-foot", "side-right"]
    w = 470
    rows = [[tile("R2Fa", v, w) for v in views], [tile("R3", v, w) for v in views]]
    notes = ["All BREP face edges drawn; same camera in each column. R3: the step is one band of one section from the floor to the roll: 12 deep, a 45 degree facet,",
             "outer round R 26, inner round R 7, the same on the stub, the S, the lean, the top arc and the run (planes and cones, ruled square to the stroke).",
             "Stroke of the outer edge: upright stub 15 (meets the floor at 90 degrees; the base chamfer crosses it square), S of two arcs R 80 (29 degrees forward, then 57 degrees back to the lean;",
             "the foot is 80 behind the straight lean), the 28 degree lean from z 130 to z 247, a top arc R 80 (42 degrees), a run back to the roll rising 0.36.",
             "The band's lower crease reaches the rear wall at z 294, 28 below the roll's (322): level with it, three rounds meet there in faces of 1 to 2 mm.",
             "No surface between band and roll morphs: they meet in the R 25 corner, which runs from the floor to the seam. Roll, smile, grips, cut-ins, door as R2."]
    sheet = grid(rows, ["R2Fa", "R3: one band,\nstub, S, run back"], views, "Rear: R2Fa and R3 (the step as one band)", notes)
    sheet.save(os.path.join(COMPARE, "rear-rev7-r3.png"))


def render_r5() -> None:
    render_r3("R5a")
    model = os.path.join(STUDY, "R6")
    subprocess.run([sys.executable, os.path.join(HERE, "render_views.py"), os.path.join(RENDERS, "R6"), model, "--views",
                    ",".join(R3_VIEWS + ("closeup-hood-corner-above", "closeup-cut-ins")), f"--frame={FRAME}", "--size", "1100", "--samples", "16"], check=True)


def sheet_r5() -> None:
    views = ["three-quarter-rear-right", "closeup-r2-corner", "rear", "side-right"]
    w = 470
    names = ["R4", "R5a", "R6"]
    rows = [[tile(n, v, w) for v in views] for n in names]
    hood = tile("R6", "closeup-hood-corner-above", w)
    blank = Image.new("RGB", (w, 10), (255, 255, 255))
    rows.append([hood, blank, blank, blank])
    notes = ["All BREP face edges drawn; same camera in each column. R4: one 45 degree shelf (12 deep on the side, 40 on the rear) with the smile eased level at",
             "the corner, a cone round the R 25 corner, rounds R 12 / R 20. R5a: R4 with the rear straight across (no smile, crease level at z 298), the band's top arc",
             "R 65, the creases R 3 (flat facets, round corners). R6: the mini's way: two flat 45 degree facets meeting on a hip line at a sharp corner, the rear facet's end",
             "showing on the side as a slanted edge, R 3 on every edge of the back (the hip R 4), the base chamfer mitred, the cut-ins round the sharp corner on a mitre",
             "(30 on the side, 20 on the rear). Last row: R6 from above the rear right corner: the hood's rear corners stay sharp (their R 3 does not build on both",
             "sides), the head's is R 3, so the corner lines across the seam differ by the round (3). R5b (one 12 deep section all round) was not built."]
    sheet = grid(rows, ["R4", "R5a: straight,\nR 3 creases", "R6: planar", "R6: hood corner\nand seam"], views, "Rear: R4, R5a, R6 (planar)", notes)
    sheet.save(os.path.join(COMPARE, "rear-rev7-r5.png"))


def costs_md() -> None:
    for name in ("A", "A25", "R"):
        print(f"\n## {MODELS[name]}\n\n| Item | Estimate |\n| --- | --- |")
        for k, v in costs(name):
            print(f"| {k} | {v} |")


if __name__ == "__main__":
    {"render": render, "sheets": sheets, "costs": costs_md, "render-r2": render_r2, "sheets-r2": sheets_r2, "render-r3": render_r3,
     "sheet-r3": sheet_r3, "render-r4": lambda: render_r3("R4"), "sheet-r4": sheet_r4,
     "render-r5": render_r5, "sheet-r5": sheet_r5}[sys.argv[1]]()
