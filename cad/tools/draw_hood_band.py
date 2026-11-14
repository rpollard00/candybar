"""The sheets of the hood band study: renders of each variant with every BREP edge drawn, sections, and the references.

The model is the output of candybar.shell.hood_band (cad/out/hood-band/<variant>: the meshes, manifest.json,
edges.json, focus.json with the cameras of the band, sections.json and report.json). Steps:

    cad/.venv-tools/bin/python cad/tools/draw_hood_band.py            # render, then all sheets
    cad/.venv-tools/bin/python cad/tools/draw_hood_band.py render     # cad/out/hood-band/<variant>/renders/<view>.png
    cad/.venv-tools/bin/python cad/tools/draw_hood_band.py sheets     # cad/out/hood-band/sheets/*.png

The sheets:
  01-cabinet.png     the whole cabinet from the front and three-quarter front, the variants side by side
  02-band.png        the band of each variant close up
  03-sections.png    a section through a speaker and one through the marquee, for each variant
  04-reference.png   crops of the reference photos (cad/vendor, not in git) beside the variants

Blender runs in background mode, one model at a time. Needs numpy, Pillow and matplotlib (cad/.venv-tools); no FreeCAD.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from compose_sheet import font  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "out", "hood-band")
SHEETS = os.path.join(OUT, "sheets")
VENDOR = os.path.join(ROOT, "vendor")
# one frame for every model, so that all renders have one scale (as tools/draw_shell.py)
FRAME = "-252,-6,-2,252,586,578"
WHOLE = ("front", "three-quarter-front-left")
CLOSE = ("band-front", "band-right", "band-speaker", "band-marquee", "band-logo")
INK, MUTED = (30, 30, 34), (110, 110, 118)
# the colour of each kind of part in a section
FILL = {"hood": "#d9d9d4", "marquee_lip": "#bfc7d6", "speaker_pod": "#bfc7d6", "logo_field": "#bfc7d6", "grille": "#30303a",
        "logo_badge": "#2f6f4a", "marquee_front": "#e3b93c", "light_box": "#6b6b78", "driver_seat": "#8d7fb5", "logo_backer": "#8d7fb5",
        "driver": "#c05a4a", "led_strip": "#f08020"}
NAMES = {"hood": "hood (skin 4)", "marquee_lip": "lip", "speaker_pod": "pod or frame", "logo_field": "logo field", "grille": "grille",
         "logo_badge": "badge", "marquee_front": "marquee front", "light_box": "light box", "driver_seat": "driver seat",
         "logo_backer": "logo backer", "driver": "driver (envelope)", "led_strip": "LED strip (envelope)"}
# crops of the reference photos: file under cad/vendor, box (left, top, right, bottom), label
REFERENCES = (("sega-new-astro-city/photo-real-three-quarter.png", (140, 160, 560, 340), "The real cabinet"),
              ("reddit-mgs-mini-astro/photo-e-three-quarter.png", (530, 230, 1010, 500), "The maker's mini (the reference cabinet)"),
              ("reddit-mgs-mini-astro/photo-b.png", (60, 815, 360, 935), "The maker's mini, from the front"))


def variants() -> list[str]:
    return sorted(k for k in os.listdir(OUT) if os.path.exists(os.path.join(OUT, k, "report.json")))


def report(key: str) -> dict:
    return json.load(open(os.path.join(OUT, key, "report.json")))


def kind(name: str) -> str:
    for end in ("_right", "_left"):
        if name.endswith(end):
            return name[:-len(end)]
    return name


def render() -> None:
    script = os.path.join(HERE, "render_views.py")
    for key in variants():
        model = os.path.join(OUT, key)
        subprocess.run([sys.executable, script, os.path.join(model, "renders"), model, "--views", ",".join(WHOLE + CLOSE),
                        f"--frame={FRAME}", "--size", "1500", "--samples", "16"], check=True)


def picture(key: str, view: str, w: int, crop: tuple[float, float, float, float] | None = None) -> Image.Image:
    im = Image.open(os.path.join(OUT, key, "renders", f"{view}.png")).convert("RGB")
    if crop:
        im = im.crop((int(crop[0] * im.width), int(crop[1] * im.height), int(crop[2] * im.width), int(crop[3] * im.height)))
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def title_of(key: str) -> str:
    v = report(key)["variant"]
    return f"{key}: {v['name']}"


def grid(rows: list[list[Image.Image]], heads: list[str], labels: list[str], title: str, notes: list[str], out: str) -> None:
    """A sheet: one column for each head, one line of pictures for each label."""
    gap, left, top = 12, 150, 96
    w = rows[0][0].width
    heights = [max(im.height for im in row) for row in rows]
    page = Image.new("RGB", (left + len(heads) * (w + gap) + gap, top + sum(h + gap for h in heights) + 28 * len(notes) + 30), (255, 255, 255))
    dr = ImageDraw.Draw(page)
    dr.text((20, 18), title, fill=INK, font=font(30, bold=True))
    for c, head in enumerate(heads):
        dr.text((left + gap + c * (w + gap), 62), head, fill=INK, font=font(22, bold=True))
    y = top
    for row, label, h in zip(rows, labels, heights):
        dr.multiline_text((20, y + 8), label, fill=MUTED, font=font(17), spacing=5)
        for c, im in enumerate(row):
            page.paste(im, (left + gap + c * (w + gap), y))
        y += h + gap
    for line in notes:
        dr.text((20, y + 6), line, fill=INK, font=font(18))
        y += 28
    os.makedirs(os.path.dirname(out), exist_ok=True)
    page.save(out)
    print("draw_hood_band:", out)


def text_of(key: str) -> str:
    return report(key)["variant"]["text"]


def cabinet_sheet() -> None:
    keys = variants()
    crops = {"front": None, "three-quarter-front-left": (0.08, 0.16, 0.92, 0.96)}
    rows = [[picture(k, v, 620, crops[v]) for k in keys] for v in WHOLE]
    grid(rows, [title_of(k) for k in keys], ["front", "three-quarter\nfront"], "Hood band: the whole cabinet with each variant",
         ["Every BREP face edge is drawn. One camera and one scale for all variants."] + [f"{k}: {text_of(k)}" for k in keys],
         os.path.join(SHEETS, "01-cabinet.png"))


def band_sheet() -> None:
    keys = variants()
    views = ("band-front", "band-right", "band-speaker", "band-marquee", "band-logo")
    rows = [[picture(k, v, 620) for k in keys] for v in views]
    grid(rows, [title_of(k) for k in keys], ["the band,\nfrom the front", "right half", "speaker", "marquee and lip,\nfrom below", "logo field"],
         "Hood band: close up", ["Every BREP face edge is drawn."] + [f"{k}: {text_of(k)}" for k in keys],
         os.path.join(SHEETS, "02-band.png"))


def draw_section(ax, cut: dict, title: str, span: tuple[float, float, float, float]) -> None:
    order = ["hood", "light_box", "driver_seat", "logo_backer", "speaker_pod", "logo_field", "marquee_lip", "driver", "led_strip",
             "marquee_front", "logo_badge", "grille"]
    parts = sorted(cut["parts"].items(), key=lambda kv: order.index(kind(kv[0])) if kind(kv[0]) in order else 99)
    for name, loops in parts:
        verts, codes = [], []
        for lp in loops:
            if len(lp) < 3:
                continue
            verts += lp + [lp[0]]
            codes += [MPath.MOVETO] + [MPath.LINETO] * (len(lp) - 1) + [MPath.CLOSEPOLY]
        if verts:
            ax.add_patch(PathPatch(MPath(verts, codes), facecolor=FILL.get(kind(name), "#cccccc"), edgecolor="#202024", linewidth=0.5))
    ax.set_xlim(span[0], span[1])
    ax.set_ylim(span[2], span[3])
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=11, loc="left")
    ax.set_xlabel("y, mm (front to rear)", fontsize=8)
    ax.set_ylabel("z, mm", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.grid(True, linewidth=0.3, color="#bbbbbb")


def sections_sheet() -> None:
    keys = variants()
    fig, axes = plt.subplots(len(keys), 4, figsize=(26, 6.2 * len(keys)), gridspec_kw={"width_ratios": [1.5, 1, 1.5, 1]})
    for row, key in zip(axes, keys):
        rep = report(key)
        cuts = json.load(open(os.path.join(OUT, key, "sections.json")))
        b = rep["band"]
        whole, near = (432.0, 584.0, 420.0, 578.0), (438.0, 500.0, 436.0, 562.0)
        s, m = cuts["speaker"], cuts["marquee"]
        area = rep["open_area"]
        draw_section(row[0], s, f"{title_of(key)}. Section through the right speaker, x = {s['x']:.1f}", whole)
        draw_section(row[1], s, f"The same, close up. Grille: {area['share']:.0%} open in front of the cone", near)
        draw_section(row[2], m, f"{title_of(key)}. Section through the marquee and the logo, x = {m['x']:.1f}", whole)
        draw_section(row[3], m, f"The same, close up. LED to front: {b['box_depth'] - b['led_t'] + b['wall_t'] + b['seat_off']:.1f}", near)
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=FILL[k], edgecolor="#202024", linewidth=0.5) for k in NAMES]
    fig.legend(handles, list(NAMES.values()), loc="lower center", ncol=6, fontsize=10, frameon=False)
    fig.suptitle("Hood band: sections in the planes x = const, seen from the right. The player is on the left of each picture. "
                 "The hood is its printed skin (4 mm).", fontsize=14, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.035, 1, 0.975))
    os.makedirs(SHEETS, exist_ok=True)
    out = os.path.join(SHEETS, "03-sections.png")
    fig.savefig(out, dpi=110)
    plt.close(fig)
    print("draw_hood_band:", out)


def reference_sheet() -> None:
    keys = variants()
    w, gap, left, top = 760, 14, 24, 96
    refs = []
    for rel, box, label in REFERENCES:
        path = os.path.join(VENDOR, rel)
        if os.path.exists(path):
            im = Image.open(path).convert("RGB").crop(box)
            refs.append((im.resize((w, round(im.height * w / im.width)), Image.LANCZOS), label))
    ours = [(picture(k, "three-quarter-front-left", w, (0.10, 0.20, 0.62, 0.48)), f"Variant {title_of(k)}, three-quarter front") for k in keys]
    fronts = [(picture(k, "band-front", w), f"Variant {title_of(k)}, from the front") for k in keys]
    cols = [refs, ours, fronts]
    height = top + max(sum(im.height + 34 + gap for im, _ in col) for col in cols) + 150
    page = Image.new("RGB", (left + 3 * (w + gap) + gap, height), (255, 255, 255))
    dr = ImageDraw.Draw(page)
    dr.text((20, 18), "Hood band: the references beside the variants", fill=INK, font=font(30, bold=True))
    for c, (col, head) in enumerate(zip(cols, ("References (photos, not in git)", "Variants, three-quarter front", "Variants, from the front"))):
        x = left + c * (w + gap)
        dr.text((x, 60), head, fill=INK, font=font(22, bold=True))
        y = top
        for im, label in col:
            dr.text((x, y), label, fill=MUTED, font=font(17))
            page.paste(im, (x, y + 28))
            y += im.height + 34 + gap
    notes = ["The references have a lit strip under the top bar, two speaker pods with square black fronts, and a logo plate between the pods.",
             "The parts of the variants carry no name and no logo of a maker: the logo field and the marquee front are plain, for the owner's own mark.",
             "A: pods and a raised logo field (the band of the references). B: no pod, the grille follows the leg. C: low frames, no logo field."]
    y = height - 140
    for line in notes:
        dr.text((20, y), line, fill=INK, font=font(18))
        y += 28
    os.makedirs(SHEETS, exist_ok=True)
    out = os.path.join(SHEETS, "04-reference.png")
    page.save(out)
    print("draw_hood_band:", out)


def sheets() -> None:
    cabinet_sheet()
    band_sheet()
    sections_sheet()
    reference_sheet()


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    if step in ("render", "all"):
        render()
    if step in ("sheets", "all"):
        sheets()
    if step not in ("render", "sheets", "all"):
        raise SystemExit(__doc__)
