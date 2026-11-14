"""The sheets of the monitor cradle and the bezel plate, with every BREP edge drawn.

The model is the output of candybar.shell.cradle (cad/out/cradle: the meshes, manifest.json, edges.json,
sections.json, and the folders print/, options/ and path/) and the built shell (cad/out/shell-rev7). Steps:

    cad/.venv-tools/bin/python cad/tools/draw_cradle.py            # render, then all sheets
    cad/.venv-tools/bin/python cad/tools/draw_cradle.py sheets     # the sheets again from the renders

It writes cad/out/cradle/sheets/*.png. Each scene is a folder under cad/out/cradle/scenes with the meshes by
absolute path, the edges of its parts and its cameras, as tools/render_views.py reads them. Blender runs in
background mode, one scene at a time. Needs numpy, matplotlib and Pillow (cad/.venv-tools); no FreeCAD.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
from compose_sheet import font  # noqa: E402

from candybar.shell.dims import MON_ACTIVE_H, MON_ACTIVE_W, Blueprint  # noqa: E402

MODEL = os.environ.get("CANDYBAR_OUT") or os.path.join(ROOT, "out", "cradle")
SHELL = os.environ.get("CANDYBAR_SHELL") or os.path.join(ROOT, "out", "shell-rev7")
SCENES, RENDERS, SHEETS = (os.path.join(MODEL, k) for k in ("scenes", "renders", "sheets"))
INK, MUTED = (30, 30, 34), (110, 110, 118)
SHELL_PARTS = ("deck", "control_panel", "body", "hood", "marquee_lip", "speaker_right", "speaker_left", "logo_form")
CRADLE = ("lugs", "bosses", "upright_right", "upright_left", "jaws", "shoes", "channel_right", "channel_left", "pins", "magnets", "screws")
COLOUR = {"skin": "#c8c8c8", "bezel_plate": "#303030", "lugs": "#d8b060", "bosses": "#d8b060", "upright_right": "#5a7fb5", "upright_left": "#5a7fb5",
          "jaws": "#d0703a", "shoes": "#8a5a30", "channel_right": "#6aa06a", "channel_left": "#6aa06a", "monitor": "#3a4250", "plugs": "#e0c890",
          "pads": "#202020", "pins": "#8080ff", "magnets": "#b040b0", "screws": "#707078"}
LABEL = {"skin": "skin of the body (4)", "bezel_plate": "bezel plate", "lugs": "lug (added solid)", "bosses": "boss (added solid)", "upright_right": "upright",
         "jaws": "jaw", "shoes": "shoe with nut", "channel_right": "cable channel", "monitor": "monitor", "plugs": "plug room", "pads": "pad",
         "pins": "locating pin", "magnets": "magnet", "screws": "screw M4"}


class Frame:
    """The frame of candybar.shell.cradle: x across, v up the screen face from the centre of the image, t behind it."""

    def __init__(self, d: Blueprint):
        a = math.radians(d.recline)
        self.up = (0.0, math.sin(a), math.cos(a))
        self.into = (0.0, math.cos(a), -math.sin(a))
        self.c = (0.0, d.foot_y + self.up[1] * d.image_s, d.deck_top + self.up[2] * d.image_s)

    def pt(self, x: float, v: float, t: float) -> list[float]:
        return [round(self.c[i] + (x if i == 0 else 0.0) + self.up[i] * v + self.into[i] * t, 2) for i in range(3)]


def scene(name: str, parts: list[tuple[str, str, str | None]], cameras: dict) -> str:
    """A model folder for render_views.py: (folder of the part, its name, a finish or None for its own)."""
    dst = os.path.join(SCENES, name)
    os.makedirs(dst, exist_ok=True)
    manifest, edges = {}, {}
    cache: dict[str, tuple[dict, dict]] = {}
    for k, (folder, part, finish) in enumerate(parts):
        if folder not in cache:
            cache[folder] = (json.load(open(os.path.join(folder, "manifest.json"))), json.load(open(os.path.join(folder, "edges.json"))))
        m, e = cache[folder]
        key = f"{k:02d}-{part}"
        manifest[key] = {"file": os.path.join(folder, m[part]["file"]), "finish": finish or m[part]["finish"]}
        edges[key] = e[part]
    json.dump(manifest, open(os.path.join(dst, "manifest.json"), "w"), indent=1)
    json.dump(edges, open(os.path.join(dst, "edges.json"), "w"))
    json.dump(cameras, open(os.path.join(dst, "focus.json"), "w"), indent=1)
    return dst


def render(name: str, folder: str, views: list[str], size: int = 1500) -> None:
    out = os.path.join(RENDERS, name)
    subprocess.run([sys.executable, os.path.join(HERE, "render_views.py"), out, folder, "--views", ",".join(views), "--size", str(size), "--samples", "16"], check=True)


def cameras(d: Blueprint, c: dict) -> dict:
    f = Frame(d)
    cam = lambda target, radius, az, el, aspect=0.75: {"target": target, "radius": radius, "az": az, "el": el, "aspect": aspect}
    hw, hl = d.bezel_w / 2, d.bezel_len / 2
    lug = ((c["lug_x0"] + c["lug_x1"]) / 2, -c["lug_v"])
    return {"closeup-face": cam(f.pt(0, 0, 0), 262, 0, d.recline, 0.78),
            "closeup-window-corner": cam(f.pt(MON_ACTIVE_W / 2 - 6, MON_ACTIVE_H / 2 - 4, 4), 20, -18, d.recline + 8),
            "closeup-outline-corner": cam(f.pt(hw - 5, hl - 5, -3), 20, 22, d.recline + 10),
            "closeup-seam": cam(f.pt(0, hl - 22, 0), 46, 0, d.recline + 6),
            "closeup-lug": cam(f.pt(lug[0], lug[1] + 4, 10), 52, -14, d.recline + 14),
            "closeup-bottom-jaw": cam(f.pt(c["bar_x"], -128, 20), 62, 26, d.recline + 20),
            "closeup-top-jaw": cam(f.pt(c["bar_x"], 124, 20), 62, 26, d.recline - 22),
            "closeup-channel": cam(f.pt(200, (c["channel_v0"] + c["channel_v1"]) / 2, 30), 95, -34, d.recline + 4),
            "closeup-way-out": cam(f.pt(40, 0, -60), 330, 58, 24, 0.8),
            "closeup-back": cam(f.pt(0, 0, 8), 262, 180, -d.recline, 0.78),
            "closeup-back-slot": cam(f.pt(-lug[0], lug[1] + 2, 8), 46, 168, -d.recline - 12)}


def render_all() -> None:
    d = Blueprint()
    c = json.load(open(os.path.join(MODEL, "sections.json")))["cradle"]
    cams = cameras(d, c)
    shell = [(SHELL, p, None) for p in SHELL_PARTS]
    inside = [(MODEL, p, None) for p in CRADLE]
    hardware = [(MODEL, "monitor", None), (MODEL, "plugs", "#e0c890"), (MODEL, "pads", None)]
    skin = [(MODEL, "skin", "white")]
    jobs = [("plate-on", shell + [(MODEL, "bezel_plate", None), (MODEL, "monitor", "#22262e")], ["closeup-face", "closeup-window-corner", "closeup-outline-corner", "closeup-seam"]),
            ("plate-off", skin + inside + hardware, ["closeup-face", "closeup-lug", "closeup-bottom-jaw", "closeup-top-jaw", "closeup-channel"]),
            ("empty", skin + inside, ["closeup-face", "closeup-lug", "closeup-channel"]),
            ("way-out", skin + inside + [(os.path.join(MODEL, "path", k), "monitor", colour) for k, colour in (("in", "#3a4250"), ("half", "#7f8aa0"), ("out", "#c0c8d8"))]
             + [(os.path.join(MODEL, "path", k), "plugs", "#e0c890") for k in ("in", "half", "out")], ["closeup-way-out"]),
            ("plate-back", [(MODEL, "bezel_plate", "#404040"), (MODEL, "pins", None), (MODEL, "magnets", None)], ["closeup-back", "closeup-back-slot"]),
            ("option-halves", [(os.path.join(MODEL, "options", "halves"), p, None) for p in ("bezel_half_right", "bezel_half_left")], ["closeup-face", "closeup-seam"]),
            ("option-bars", [(os.path.join(MODEL, "options", "bars"), p, None)
                             for p in json.load(open(os.path.join(MODEL, "options", "bars", "manifest.json")))], ["closeup-face", "closeup-seam"])]
    for name, parts, views in jobs:
        render(name, scene(name, parts, cams), views)


# ---------- the drawings of the sections ----------

def draw_cut(ax, cut: dict, xlim, ylim, title: str, flip: bool = False, skip: tuple[str, ...] = ()) -> None:
    order = ["skin", "bezel_plate", "lugs", "bosses", "upright_right", "upright_left", "channel_right", "channel_left", "shoes", "jaws", "monitor", "plugs",
             "pads", "screws", "pins", "magnets"]
    seen = set()
    for k in order:
        if k in skip or k not in cut:
            continue
        for line in cut[k]:
            xs, ys = [p[0] for p in line], [p[1] for p in line]
            name = LABEL.get(k)
            ax.fill(xs, ys, facecolor=COLOUR[k], alpha=0.25 if k == "plugs" else 0.55, edgecolor="#101010", linewidth=0.7, label=name if name and name not in seen else None)
            seen.add(name)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=11, loc="left")
    ax.grid(True, linewidth=0.3, color="#c0c0c0")
    ax.tick_params(labelsize=8)
    if flip:
        ax.invert_xaxis()


def note(ax, text: str, xy, xytext) -> None:
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=8.5, arrowprops={"arrowstyle": "-", "linewidth": 0.6, "color": "#404040"}, color="#101010")


def sections_sheet(data: dict, rep: dict) -> None:
    cuts, c, f = data["cuts"], data["cradle"], data["frame"]
    lo, hi = data["edges_v"]
    t0 = f["t0"]
    fig, axs = plt.subplots(2, 2, figsize=(17, 13))
    # the front of the cabinet is at the top of each drawing (t grows downward)
    draw_cut(axs[0][0], cuts["bottom clamp"], (lo - 52, lo + 30), (60, -16), f"Bottom clamp: section through the upright (x {c['bar_x']:g}); v along the face, t behind it")
    draw_cut(axs[0][1], cuts["bottom clamp"], (hi - 30, hi + 48), (60, -16), "Top clamp: the same section at the top edge")
    draw_cut(axs[1][0], cuts["lug and ear"], (lo - 52, lo + 30), (60, -16), f"Bottom lug and the ear of the upright (x {c['bar_x'] - c['bar_w'] / 2 - c['ear_w'] / 2:g})")
    draw_cut(axs[1][1], cuts["lug and ear"], (hi - 30, hi + 48), (60, -16), "Top lug and ear")
    a = axs[0][0]
    note(a, "monitor, glass 1.0 behind the plate", (lo + 14, t0 + c["glass_gap"] + 3), (lo + 2, -9))
    note(a, "pad 2 on the wall of the jaw", (lo - 1, t0 + 6), (lo - 50, -4))
    note(a, "lock screw M4, from the front", (lo - 11, 24), (lo - 50, 2))
    note(a, "slot of the upright: the jaw moves along the face", (lo - 20, 40), (lo - 50, 56))
    note(a, "ledge of the opening (skin)", (-f["half_len"] + 3, t0 + 2), (lo - 50, 9))
    note(a, "rest behind the monitor, felt 1", (lo + 8, t0 + c["glass_gap"] + data["unit"]["t"] + 3), (lo + 2, 50))
    a = axs[1][0]
    note(a, "lug: the ledge made 11.1 wider and 6 thick", (-f["half_len"] + 12, t0 + 4), (lo - 20, -8))
    note(a, "screw M4 button head, under the plate", (-c["lug_v"], t0 + 1.2), (lo - 20, 2))
    note(a, "heat-set insert M4 in the ear", (-c["lug_v"], t0 + c["lug_t"] + 4), (lo - 20, 30))
    note(a, "upright", (-c["lug_v"] + 20, 40), (lo - 20, 54))
    handles, labels = axs[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=7, fontsize=9, frameon=False)
    fig.suptitle("Sections through the clamps and the lugs (plate on, present monitor). All face boundaries are drawn. Millimetres.", fontsize=13, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.035, 1, 0.97))
    fig.savefig(os.path.join(SHEETS, "03-sections-clamps.png"), dpi=110)
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(17, 7.5), gridspec_kw={"width_ratios": [1.0, 1.9]})
    xw = c["side_wall_x"]
    draw_cut(axs[0], cuts["channel"], (165, 252), (62, -16), f"Cable channel, right side: section across the face at v {c['boss_v'][1]:g}; x across, t behind the face")
    note(axs[0], "side of the body, inner face x 243", (xw + 1, 40), (168, 58))
    note(axs[0], "boss with insert M3 (added solid)", (xw - 2.5, 36), (168, 52))
    note(axs[0], f"clear {c['channel_in'][0]:g} x {c['channel_in'][1]:g}: video lead, power lead, slack", (xw - 18, 36), (168, 46))
    note(axs[0], "entry slot 9, toward the plugs", (xw - 29.5, 36), (168, 40))
    note(axs[0], "plug room 22 (right-angle plugs)", (188, 13), (168, -10))
    note(axs[0], "jamb of the opening", (219, 0), (222, -10))
    draw_cut(axs[1], cuts["across the image"], (-252, 252), (62, -16), "Across the centre of the image: both channels, both uprights, the monitor with its plug room")
    handles, labels = axs[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=7, fontsize=9, frameon=False)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(os.path.join(SHEETS, "04a-cable-channel-sections.png"), dpi=110)
    plt.close(fig)

    fig, axs = plt.subplots(1, 3, figsize=(17, 6.8))
    v = c["lug_v"]
    draw_cut(axs[0], cuts["pin"], (-v - 16, -v + 12), (20, -8), f"Locating pin (x {c['pin_x']:g}), bottom: dowel 4 x 12 pressed in the lug; slot in the plate")
    draw_cut(axs[1], cuts["magnet"], (-v - 16, -v + 12), (20, -8), f"Magnets (x {c['magnet_x']:g}), bottom: 8 x 3 in the lug and 8 x 3 in the plate")
    draw_cut(axs[2], cuts["lug and ear"], (-v - 16, -v + 12), (26, -8), "Screw of the upright: under the plate, in a slot of 2.5 along the face")
    note(axs[0], f"plate {c['plate_fit']:g} smaller than its recess", (-f["half_len"] + 0.25, 0), (-v - 15, -6))
    note(axs[0], "slot 4.3 wide, +-2 along the radius, 6.5 deep", (-v, t0 - 3), (-v - 15, 17))
    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=7, fontsize=9, frameon=False)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(os.path.join(SHEETS, "06a-fastening-sections.png"), dpi=110)
    plt.close(fig)

    # the way out: the section on the centre line with the monitor in three positions
    fig, ax = plt.subplots(figsize=(15, 8.5))
    draw_cut(ax, cuts["centre line"], (-175, 175), (64, -175), "Way out, section on the centre line (plate off, top jaws pushed up). v along the face, t behind it; the front is at the top", skip=("monitor", "plugs", "pads", "bezel_plate"))
    u, g = data["unit"], t0 + c["glass_gap"]
    for out, shade, name in ((0.0, "#3a4250", "in"), (60.0, "#7f8aa0", "60 out"), (150.0, "#c0c8d8", "150 out")):
        ax.fill([lo, hi, hi, lo], [g - out, g - out, g - out + u["t"], g - out + u["t"]], facecolor=shade, edgecolor="#101010", linewidth=0.8, alpha=0.9)
        ax.text(lo + 6, g - out + u["t"] / 2, f"present monitor, {name}", va="center", fontsize=9, color="white" if out == 0 else "black")
    half = rep["generic"]["h"] / 2 + c["adjust"]
    ax.plot([-half, -half, half, half], [g + rep["generic"]["t"], -170, -170, g + rep["generic"]["t"]], color="#c03030", linewidth=1.0, linestyle="--")
    ax.text(-half + 4, -165, "the prism that any 16:10 unit passes through, with its adjustment of 8 each way", color="#c03030", fontsize=9)
    ax.text(-f["half_len"] + 8, 4, "opening 293.4", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(SHEETS, "05a-way-out-section.png"), dpi=110)
    plt.close(fig)


# ---------- the sheets ----------

def tile(scene_name: str, view: str, w: int) -> Image.Image:
    im = Image.open(os.path.join(RENDERS, scene_name, f"{view}.png")).convert("RGB")
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def page(title: str, rows: list[list[tuple[str, Image.Image]]], notes: list[str], out: str) -> None:
    gap, top, width = 14, 74, max(sum(im.width for _, im in row) + gap * (len(row) + 1) for row in rows)
    lines = [ln for n in notes for ln in textwrap.wrap(n, int(width / 10.2)) + [""]]
    height = top + sum(max(im.height for _, im in row) + 30 + gap for row in rows) + 25 * len(lines) + 20
    sheet = Image.new("RGB", (width, height), (255, 255, 255))
    dr = ImageDraw.Draw(sheet)
    dr.text((gap, 18), title, fill=INK, font=font(30, bold=True))
    y = top
    for row in rows:
        x = gap
        for label, im in row:
            dr.text((x, y), label, fill=MUTED, font=font(18))
            sheet.paste(im, (x, y + 28))
            x += im.width + gap
        y += max(im.height for _, im in row) + 30 + gap
    for ln in lines:
        dr.text((gap, y), ln, fill=INK, font=font(18))
        y += 25
    sheet.save(os.path.join(SHEETS, out))
    print("draw_cradle:", os.path.join(SHEETS, out))


def drawing(name: str, w: int) -> Image.Image:
    im = Image.open(os.path.join(SHEETS, name)).convert("RGB")
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def sheets() -> None:
    os.makedirs(SHEETS, exist_ok=True)
    data = json.load(open(os.path.join(MODEL, "sections.json")))
    rep = json.load(open(os.path.join(MODEL, "report.json")))
    c = rep["cradle"]
    sections_sheet(data, rep)
    edge = rep["edge"]["rows"]
    page("The bezel plate (16:10), printed, from the front", [
        [("In the body, seen square to the screen face", tile("plate-on", "closeup-face", 1150)),
         ("Top seam on the centre line (bonded, filled, painted)", tile("plate-on", "closeup-seam", 600))],
        [("Corner of the window: the edge break R 1 on the rim", tile("plate-on", "closeup-window-corner", 870)),
         ("Corner of the outline: the edge break R 1, the gap of 0.5 and the reveal", tile("plate-on", "closeup-outline-corner", 870))]],
         [f"Every BREP edge is drawn. The plate has the form of solids.bezel. It is {c['plate_fit']:g} smaller than its recess on each side and at each end. "
          f"The edge break R 1 is on 12 edges: 4 between the inner frame and the rim wall of the window, 4 round the land, 4 at the corners of the outline "
          f"({edge['break_faces']} faces of the break, {edge['break_corner_faces']} corner balls). No convex edge that shows is sharp.",
          "At each corner of the window, the rounds of two edges meet in a patch of 0.2 mm2 that OpenCascade makes. It is a known item of the face check."],
         "01-bezel-plate-front.png")
    page("Two printed ways for the bezel plate", [
        [("Two halves, seam on the centre line (chosen): 2 pieces, 2 seams of 45", tile("option-halves", "closeup-face", 880)),
         ("Four bars with mitres: 6 pieces, 4 mitres of 51 and 2 seams of 45", tile("option-bars", "closeup-face", 880))],
        [("Halves: the seam at the top", tile("option-halves", "closeup-seam", 880)), ("Bars: the seam at the top; the mitres are in the corners", tile("option-bars", "closeup-seam", 880))]],
         ["Halves: each half prints on its outer side face, 217 high. The land, the inner frame and the rim wall are walls or face up: no support on a face that shows. "
          "The layers are square to the plate, so the plate does not curl out of its plane. Two dowels of 4 in each seam put the halves in line.",
          "Bars: the top and the bottom bar are 435 long, more than the bed diagonal, so each is two pieces. The mitres cross the land at 45 degrees. More seams on the face for the same result."],
         "01b-bezel-plate-options.png")
    page("The plate off: the monitor in the cradle", [
        [("Present monitor in the cradle, with its plug room on both sides", tile("plate-off", "closeup-face", 1050)),
         ("The cradle without the monitor", tile("empty", "closeup-face", 1050))],
        [("Bottom jaw on the right upright", tile("plate-off", "closeup-bottom-jaw", 690)), ("Top jaw", tile("plate-off", "closeup-top-jaw", 690)),
         ("Bottom right lug: screw of the upright, pin, magnet", tile("empty", "closeup-lug", 690))]],
         ["White: the skin of the body round the screen face (its inner faces are the slabs of the cavity). Yellow: the four lugs and the four bosses, added solids on the body. "
          "Blue: the two uprights. Orange: the four jaws. Green: the cable channels. Pale: the room of the right-angle plugs.",
          "To take the monitor out: pull the plate off, loosen the two top lock screws with a 2.5 mm hexagon key, push the top jaws up, tip the top of the monitor forward, pull the plugs, lift the monitor out."],
         "02-plate-off-monitor-in-cradle.png")
    page("Cable channel", [[("Sections", drawing("04a-cable-channel-sections.png", 1500))],
                           [("Right channel, with the monitor", tile("plate-off", "closeup-channel", 740)), ("Right channel, without the monitor", tile("empty", "closeup-channel", 740))]],
         [f"One channel on the inner face of each side, on two bosses with M3 inserts. Clear section {c['channel_in'][0]:g} x {c['channel_in'][1]:g}, 100 long, with an entry slot of {c['channel_slot']:g} toward the plugs. "
          "It holds a video lead and a power lead with right-angle plugs, and the slack of 100 that the monitor needs to come forward before the plugs are pulled."],
         "04-cable-channel.png")
    page("The monitor on its way out", [[("Three positions: in, 60 out, 150 out", tile("way-out", "closeup-way-out", 900)), ("Section on the centre line", drawing("05a-way-out-section.png", 1000))]],
         ["The way out is square to the screen face. " + " ".join(f"At {r['out_mm']:g} out, {r['what']}: {r['common_mm3']:g} mm3 in common, gap {r['gap']:.1f}." for r in rep["path"])],
         "05-way-out.png")
    page("The fastening of the bezel plate", [[("Sections", drawing("06a-fastening-sections.png", 1500))],
                                             [("The back of the plate: four slots that point at the centre, four magnets", tile("plate-back", "closeup-back", 900)),
                                              ("Slot, pin and magnet", tile("plate-back", "closeup-back-slot", 600))]],
         ["Four dowel pins of 4 x 12 in the lugs go into four slots in the back of the plate. Each slot points at the centre of the image. "
          "Thus the plate keeps its centre when the plate and the body shrink by different amounts, and it goes back in the same place.",
          f"Four pairs of magnets 8 x 3 hold it: about {4 * c['magnet_pull']:g} N in total (an estimate). No part of the fastening is on the face of the plate."],
         "06-fastening.png")


if __name__ == "__main__":
    os.makedirs(SHEETS, exist_ok=True)
    if len(sys.argv) < 2 or sys.argv[1] == "render":
        render_all()
    if len(sys.argv) < 2 or sys.argv[1] == "sheets":
        sheets()
