"""Draw the print pieces from what candybar.shell.pieces wrote: the sheets, with every BREP edge drawn.

    CANDYBAR_PIECES=views CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh candybar.shell.pieces
    cad/.venv-tools/bin/python cad/tools/draw_pieces.py [name-fragment]

The first command writes a folder for each picture under cad/out/pieces/views (the meshes and the edges of its
pieces, moved as the view asks, with the camera). This tool renders each folder with tools/render_views.py
(Blender, no window) and puts the pictures on sheets in cad/out/pieces/sheets:

    exploded.png   the assembly moved apart, from the front and from the rear
    pilot.png      the two pilot pairs, closed and open
    section.png    the section through a screw of each pilot seam, with the values of joints.Joint
    closeups.png   the difficult seams

With a name fragment, only the views whose name holds it are rendered again. Needs matplotlib and Pillow
(cad/.venv-tools).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(HERE)
sys.path.insert(0, CAD)
from candybar.shell import pieces  # noqa: E402

OUT = os.environ.get("CANDYBAR_OUT", os.path.join(CAD, "out", "pieces"))
SHEETS = (
    ("exploded", "The print pieces with their joints: the assembly moved apart", ("exploded-front", "exploded-rear"), 1),
    ("pilot", "The pilot pairs: a straight seam at the front (D2) and a seam in a crease at the rear (B1)",
     ("pilot-front-closed", "pilot-front-open", "pilot-rear-closed", "pilot-rear-open", "pilot-rear-under"), 2),
    ("closeups", "The difficult seams", ("close-l1-cut-in", "close-door-land", "close-hand-hold", "close-s1-node", "close-floor",
                                         "close-floor-under", "close-apron", "close-hood", "close-hood-centre"), 2),
)


def render(name: str, size: int = 1800) -> str:
    folder = os.path.join(OUT, "views", name)
    shots = os.path.join(folder, "renders")
    cmd = [sys.executable, os.path.join(HERE, "render_views.py"), shots, folder, "--views", name, "--size", str(size)]
    done = subprocess.run(cmd, capture_output=True, text=True)
    png = os.path.join(shots, f"{name}.png")
    if done.returncode != 0 or not os.path.exists(png):
        raise RuntimeError(f"render of {name} failed:\n{done.stdout[-2000:]}\n{done.stderr[-2000:]}")
    return png


def sheet(stem: str, title: str, names: tuple[str, ...], cols: int) -> str:
    rows = -(-len(names) // cols)
    fig, axes = plt.subplots(rows, cols, figsize=(11.0 * cols, 8.6 * rows), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")
    for ax, name in zip(axes.flat, names):
        png = os.path.join(OUT, "views", name, "renders", f"{name}.png")
        if not os.path.exists(png):
            continue
        ax.imshow(plt.imread(png))
        caption = open(os.path.join(OUT, "views", name, "title.txt"), encoding="utf-8").read()
        ax.set_title(caption, fontsize=13, loc="left", wrap=True)
    fig.suptitle(title + ". Every BREP edge is drawn.", fontsize=17, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    os.makedirs(os.path.join(OUT, "sheets"), exist_ok=True)
    path = os.path.join(OUT, "sheets", f"{stem}.png")
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path


def section_sheet() -> str | None:
    src = os.path.join(OUT, "views", "section.json")
    if not os.path.exists(src):
        return None
    data = json.load(open(src, encoding="utf-8"))
    j = pieces.joint()
    fig, axes = plt.subplots(1, len(data), figsize=(11.0 * len(data), 9.0), squeeze=False)
    for ax, (seam, sec) in zip(axes.flat, data.items()):
        for name, colour in ((sec["pilot"], "#e8c39e"), (sec["head"], "#9ec5e8")):
            for poly in sec["polys"][name]:
                # u may point outward in the data: the skin is where |u| is small on the wall side
                ax.add_patch(Polygon(poly, closed=True, fc=colour, ec="#222", lw=0.8))
        ax.plot([0, 0], [-j.pilot_depth, j.flange_t + j.gusset_leg + 6], color="#b00", lw=0.8, ls="-.")
        ax.set_aspect("equal")
        ax.set_xlim(-26, 26)
        ax.set_ylim(-30, 30)
        ax.grid(True, lw=0.3, color="#bbb")
        ax.set_xlabel("mm across the flange, from the screw axis")
        ax.set_ylabel("mm across the seam, from the seam plane")
        ax.set_title(f"Seam {seam}: {sec['head']} (blue, screw head) and {sec['pilot']} (tan, pilot hole)", fontsize=12, loc="left")
    text = (f"joints.Joint: skin {j.wall_t:g}; flange {j.flange_h:g} x {j.flange_t:g}; gusset {j.gusset_angle:g} deg; "
            f"key {j.key_w:g} x {j.key_proj:g}, groove +{j.groove_clearance:g} each side and {j.groove_extra_depth:g} deeper;\n"
            f"screw {j.screw_d:g} x {j.screw_l:g} at {j.screw_u:g} from the outside, pitch {j.screw_pitch:g}; pilot {j.pilot():g} x {j.pilot_depth:g}; "
            f"clearance {j.clearance_d:g}; head pocket {j.head_pocket_d:g};\nV for the filler {j.vgroove_d:g} deep, "
            f"{j.vgroove_w:g} wide over the two pieces; bond line {pieces.split.KERF:g}")
    fig.suptitle("Section through a screw of each pilot seam, square to the seam\n" + text, fontsize=12, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    os.makedirs(os.path.join(OUT, "sheets"), exist_ok=True)
    path = os.path.join(OUT, "sheets", "section.png")
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def label_of(seam: str) -> str:
    return seam.split()[0]


def twin(name: str) -> str:
    return name[:-2] if name.endswith((" R", " L")) else name


def report() -> str | None:
    """report.md: the table of seams and the table of pieces, from seams.json and check.json."""
    try:
        seams = json.load(open(os.path.join(OUT, "seams.json"), encoding="utf-8"))
        chk = json.load(open(os.path.join(OUT, "check.json"), encoding="utf-8"))
    except FileNotFoundError:
        return None
    rows: dict[str, dict] = {}
    for sd in seams["sides"]:
        r = rows.setdefault(label_of(sd["seam"]), {"pieces": set(), "flange": 0.0, "crease": set(), "screws": 0, "heads": set(), "notes": set(),
                                                  "free": [], "run": 0.0})
        r["pieces"].add(twin(sd["piece"]))
        r["flange"] += sd["flange_cm3"]
        if sd["lean_out"] and not sd["gusset"]:
            r["crease"].add(twin(sd["piece"]))
        for n in sd["notes"]:
            r["notes"].add(f"{sd['piece']}: {n}")
        if sd["flange_cm3"] == 0.0:
            r["notes"].add(f"{sd['piece']}: no flange")
    for p in seams["pairs"]:
        r = rows[label_of(p["seam"])]
        r["screws"] += len(p["screws"])
        r["run"] += p["run_mm"]
        if p["screws"]:
            r["heads"].add(twin(p["head"]))
            r["free"] += [sc["free"] for sc in p["screws"]]
        for n in p["notes"]:
            if "left out" in n or "no screw" in n or "no key" in n:
                r["notes"].add(f"{p['head']} / {p['pilot']}: {n}")
    lines = ["## Seams", "",
             "| Seam | Pieces | Flange and gusset (cm3) | Crease side (no gusset) | Mating run (mm) | Screws | Head in | Least room for the screwdriver (mm) | What was done |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k in sorted(rows):
        r = rows[k]
        lines.append(f"| {k} | {', '.join(sorted(r['pieces']))} | {r['flange']:.0f} | {', '.join(sorted(r['crease'])) or '-'} | {r['run']:.0f} | {r['screws']} | "
                     f"{', '.join(sorted(r['heads'])) or '-'} | {min(r['free']) if r['free'] else '-'} | {'; '.join(sorted(r['notes'])) or 'as defined'} |")
    lines += ["", "## Pieces", "",
              "| Piece | Print box (mm) | Fits | On the bed | Face on the bed (cm2) | Volume (cm3) | Of that, joints (cm3) | Mass, solid (g) | Faces over 45 deg (cm2) | The same on the plain piece (cm2) | Seen faces over 45 deg, plain piece (cm2) |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for n, r in chk["pieces"].items():
        plain = r.get("plain_cm3")
        extra = f"{r['volume_cm3'] - plain:.1f}" if plain is not None and not n.startswith("floor") else "-"
        lines.append(f"| {n} | {r['x']:.0f} x {r['y']:.0f} x {r['z']:.0f} | {'yes' if r['fits'] else 'NO'} | {r['bed']} | {r['bed_cm2']} | {r['volume_cm3']} | "
                     f"{extra} | {r['mass_g']} | {r['overhang_cm2']} | {r.get('overhang_plain_cm2', '-')} | {r.get('seen_overhang_plain_cm2', '-')} |")
    lines += ["", "## Checks", "", f"- Pieces: {len(chk['pieces'])}. One valid solid each, inside the limit: {'yes' if chk['ok'] or not [1 for r in chk['pieces'].values() if not (r['valid'] and r['solids'] == 1 and r['fits'])] else 'NO'}.",
              f"- Clashes between pieces: {chk['clashes'] or 'none'}.",
              f"- Clashes with the hardware: {chk['hardware'] or 'none'}.",
              f"- Twins that differ: {chk['twins_that_differ'] or 'none'}.",
              f"- Screws: {chk['screws']}. Cones: {chk['cones']}.",
              f"- Screws that a screwdriver does not reach: {chk['reach_short'] or 'none'}.",
              f"- Mass: {chk['mass']}.", "",
              "## Hardware that a flange, a foot or a rib was cut back for", "",
              "| Where | Piece | Item | Role | Volume in it before the cut (mm3) |", "| --- | --- | --- | --- | --- |"]
    for h in seams["hits"]:
        lines.append(f"| {h['seam']} | {h['piece']} | {h['item']} | {h['role']} | {h['mm3']} |")
    fl = seams.get("floor", {})
    lines += ["", "## Floor", "", f"- Lap screws: {len(fl.get('lap_screws', []))}. Cones: {len(fl.get('cones', []))}. Foot screws: {len(fl.get('foot_screws', []))}.",
              f"- Foot screws left out: {fl.get('left_out', [])}.", f"- Notches: {fl.get('notches', [])}.", ""]
    path = os.path.join(OUT, "report.md")
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    return path


def main() -> None:
    want = sys.argv[1] if len(sys.argv) > 1 else ""
    if want == "report":
        print("wrote", report())
        return
    for v in pieces.VIEWS:
        if want in v.name and os.path.isdir(os.path.join(OUT, "views", v.name)):
            print("rendered", render(v.name))
    for stem, title, names, cols in SHEETS:
        print("wrote", sheet(stem, title, names, cols))
    print("wrote", section_sheet())
    print("wrote", report())


if __name__ == "__main__":
    main()
