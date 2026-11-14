"""The views and the sheets of the front socket plate, with every BREP edge drawn.

The model is the output of candybar.shell.socket_plate (cad/out/socket-plate: one build folder for each variant, and
the folders proud, behind and out). Steps:

    cad/.venv-tools/bin/python cad/tools/draw_socket_plate.py fcstd    -> <folder>/shell.FCStd, for a person to open
    cad/.venv-tools/bin/python cad/tools/draw_socket_plate.py render   -> <folder>/renders/<view>.png
    cad/.venv-tools/bin/python cad/tools/draw_socket_plate.py sheets   -> sheets/*.png
    cad/.venv-tools/bin/python cad/tools/draw_socket_plate.py all

Blender runs in background mode, one folder at a time (render_views.py). FreeCAD runs its GUI binary offscreen for
the documents (candybar.shell.viewdoc). Needs numpy, Pillow and matplotlib (cad/.venv-tools).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from compose_sheet import font  # noqa: E402

ROOT = os.path.dirname(HERE)
MODEL = os.environ.get("CANDYBAR_OUT") or os.path.join(ROOT, "out", "socket-plate")
SHEETS = os.path.join(MODEL, "sheets")
# the frame of draw_shell.py, so that the whole cabinet has the scale of the other renders
FRAME = "-252,-6,-2,252,586,578"
VARIANTS = ("a-knob", "a-plain", "b-knob", "b-plain")
DEFAULT = "b-knob"
SEATS = ("seat-small-adult", "seat-tall-adult")
VIEWS = {**{v: ("front", "three-quarter-front-right", "deck-right", *SEATS, "plate-side", "plate-quarter", "plate-button", "plate-usb") for v in VARIANTS},
         "proud": ("plate-side", "plate-quarter"), "square": ("plate-side", "plate-quarter"), "knob-left": ("three-quarter-front-left", "deck-left", "left-quarter", "left-side", "deck-right"), "behind": ("plate-inside",), "out": ("plate-out", "plate-out-rear")}
INK, MUTED = (30, 30, 34), (110, 110, 118)


def titles() -> dict[str, str]:
    report = json.load(open(os.path.join(MODEL, "report.json")))
    return {k: r["title"] for k, r in report["variants"].items()}


def fcstd() -> None:
    run = os.path.join(ROOT, "candybar", "freecad-run.sh")
    for folder in VIEWS:
        out = os.path.join(MODEL, folder)
        subprocess.run([run, "--gui", "candybar.shell.viewdoc"], env=os.environ | {"CANDYBAR_OUT": out}, check=True)


def render(only: tuple[str, ...] = ()) -> None:
    script = os.path.join(HERE, "render_views.py")
    for folder, views in VIEWS.items():
        if only and folder not in only:
            continue
        model = os.path.join(MODEL, folder)
        subprocess.run([sys.executable, script, os.path.join(model, "renders"), model, "--views", ",".join(views), f"--frame={FRAME}",
                        "--size", "1500", "--samples", "16"], check=True)


def tile(folder: str, view: str, w: int) -> Image.Image:
    im = Image.open(os.path.join(MODEL, folder, "renders", f"{view}.png")).convert("RGB")
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def grid(rows: list[tuple[str, str]], views: tuple[str, ...], heads: tuple[str, ...], title: str, notes: list[str], out: str, w: int = 520) -> None:
    """One line of pictures for each folder of rows (label, folder), one column for each view."""
    gap, left, top = 12, 230, 96
    pictures = [[tile(folder, v, w) for v in views] for _, folder in rows]
    wrapped = [line for note in notes for line in textwrap.wrap(note, int((left + len(views) * (w + gap)) / 10.2)) + [""]]
    height = top + 30 + sum(max(im.height for im in line) + gap for line in pictures) + 26 * len(wrapped) + 30
    page = Image.new("RGB", (left + len(views) * (w + gap) + gap, height), (255, 255, 255))
    dr = ImageDraw.Draw(page)
    dr.text((20, 22), title, fill=INK, font=font(32, bold=True))
    for c, head in enumerate(heads):
        dr.text((left + gap + c * (w + gap), top), head, fill=MUTED, font=font(18))
    y = top + 30
    for (label, _), line in zip(rows, pictures):
        dr.multiline_text((20, y + 10), "\n".join(textwrap.wrap(label, 19)), fill=INK, font=font(19, bold=True), spacing=6)
        for c, im in enumerate(line):
            page.paste(im, (left + gap + c * (w + gap), y))
        y += max(im.height for im in line) + gap
    y += 10
    for text in wrapped:
        dr.text((20, y), text, fill=INK, font=font(19))
        y += 26
    os.makedirs(SHEETS, exist_ok=True)
    page.save(out)
    print("draw_socket_plate:", out)


def section_sheet(out: str) -> None:
    """The sections across the deck side of the default variant, drawn from sections.json: every line of the cut."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    data = json.load(open(os.path.join(MODEL, DEFAULT, "sections.json")))
    rep = json.load(open(os.path.join(MODEL, "report.json")))
    sp = rep["values"]
    x0, _, zc = rep["centre"]
    names = {"button": "Through the power button", "usb-a": "Through the two USB-A sockets", "usb-c": "Through the two USB-C sockets",
             "knob": "Through the volume control"}
    fig, axes = plt.subplots(2, 2, figsize=(19, 12.5), dpi=110)
    for ax, (key, sec) in zip(axes.flat, data.items()):
        for line in sec["skin"]:
            ax.fill([p[0] for p in line], [p[1] for p in line], facecolor="#e9e6df", edgecolor="#22232a", linewidth=1.1)
        for line in sec["panel"]:
            ax.fill([p[0] for p in line], [p[1] for p in line], facecolor="#3a3c40", edgecolor="#22232a", linewidth=1.0)
        for line in sec["plate"]:
            ax.fill([p[0] for p in line], [p[1] for p in line], facecolor="#f2c14e", edgecolor="#22232a", linewidth=1.1)
        for name, lines in sec["hardware"].items():
            colour = "#9aa3b2" if "screw" not in name else "#55585e"
            for line in lines:
                ax.fill([p[0] for p in line], [p[1] for p in line], facecolor=colour, edgecolor="#22232a", linewidth=1.0)
        for lines in sec["rooms"].values():
            for line in lines:
                ax.plot([p[0] for p in line], [p[1] for p in line], color="#c0392b", linewidth=1.2, linestyle=(0, (6, 4)))
        ax.fill([150, x0 - 4.34, x0 - 4.34, 150], [0, 0, sp["floor_t"], sp["floor_t"]], facecolor="none", edgecolor="#3a6ea5", hatch="//", linewidth=1.0)
        ax.text(153, sp["floor_t"] / 2 - 1.2, f"floor, {sp['floor_t']:g} (fit.Layout.floor_t)", color="#3a6ea5", fontsize=10)
        ax.annotate("", (x0, 77), (x0 - sp["t"], 77), arrowprops={"arrowstyle": "<->", "color": "#22232a"})
        ax.text(x0 - 2, 78.5, f"plate {sp['t']:g}", ha="center", fontsize=10)
        deep = {"button": sp["t"] + sp["button_clear"], "knob": sp["t"] + sp["knob_clear"]}.get(key, sp["web"] + sp["usb_clear_depth"])
        ax.annotate("", (x0, 52.5), (x0 - deep, 52.5), arrowprops={"arrowstyle": "<->", "color": "#c0392b"})
        ax.text(x0 - deep / 2, 54, f"{deep:g} from the outer face", ha="center", color="#c0392b", fontsize=10)
        ax.axhline(zc, color="#888", linewidth=0.6, linestyle=":")
        ax.text(151, zc + 0.8, f"centre line of the plate, z {zc:g}", color="#666", fontsize=9)
        ax.set_title(f"{names[key]} (plane y = {sec['y']:g})", fontsize=14, loc="left")
        ax.set_aspect("equal")
        ax.set_xlim(150, x0 + 24)
        ax.set_ylim(-3, 82)
        ax.set_xlabel("x, mm (outside of the cabinet on the right)")
        ax.set_ylabel("z, mm above the desk")
        ax.grid(True, color="#ddd", linewidth=0.5)
    for ax in list(axes.flat)[len(data):]:
        ax.axis("off")
    fig.suptitle(f"Front socket plate, variant {DEFAULT}: sections across the right side of the deck. Yellow: the plate. Grey: hardware (estimated sizes). "
                 "Red dashed: room for cables and wires. Dark: the control panel.", fontsize=13, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    os.makedirs(SHEETS, exist_ok=True)
    fig.savefig(out)
    print("draw_socket_plate:", out)


def sheets() -> None:
    t = titles()
    rows = [(f"{k}: {t[k].split(': ', 1)[1]}", k) for k in VARIANTS]
    grid(rows, ("front", "three-quarter-front-right", "deck-right", *SEATS),
         ("the front", "the cabinet from the front right", "the right side of the deck", "from the seat, small adult", "from the seat, tall adult"),
         "Front socket plate: the four variants on the cabinet", [
             "The plate is in the right side face of the deck, where fit.Layout has the four USB sockets. The front face of the deck has no hole (settled by "
             "the owner). All BREP face edges are drawn.",
             "From the seat the eye is above the deck and left of the plate: the side face of the deck does not show. Only the knob and the rims of the "
             "button and of the screw heads stand out of the side."],
         os.path.join(SHEETS, "1-cabinet-with-each-variant.png"), w=430)
    grid(rows, ("plate-side", "plate-quarter"), ("square to the side of the deck (the front of the cabinet is on the left)", "from the front right"),
         "Front socket plate: the four variants close up", [
             "All four have one outline (142 x 33, round ends), one opening in the shell and the same two plate screws. Layout A has the controls at "
             "the two ends. Layout B has them together at the front end. The plate lies flush in a recess with a reveal of 1.",
             "Screw heads that show: eight flange screws of the sockets and two plate screws."],
         os.path.join(SHEETS, "2-plate-close-up.png"), w=760)
    grid([("Round ends, flush in a recess with a reveal of 1 (the proposal)", DEFAULT), ("Square ends with corners of R 6, flush in the same recess depth", "square"),
          ("Proud: the plate lies on the face of the deck, 4 high", "proud")],
         ("plate-side", "plate-quarter"), ("square to the side of the deck", "from the front right"),
         "Front socket plate: the outline and the seat, on variant " + DEFAULT, [
             "Round ends: a level slot, as the cut-ins and the hand-holds of the rear. Square ends: as the service doors below the control panel of the "
             "full-size cabinet. Both have the same length, height, window and screws.",
             "Flush: the plate reads as a part of the form, as the control panel and the bezel plate do. The roof of the recess faces down on the "
             "upright print piece and needs a support (5.5 cm2, in the reveal).",
             "Proud: no recess, so the print piece needs no support at a face that shows. The plate stands 4 out of the side and its rim catches the light."],
         os.path.join(SHEETS, "3-outline-and-seat.png"), w=760)
    grid([("The print piece deck side R with the seat; the plate is out with its hardware", "out")], ("plate-out", "plate-out-rear"),
         ("from the front right", "from the rear right"), "Front socket plate: the plate out, and what is behind it", [
             "The window is 121 x 28. The frame behind the skin carries the ledge of 2.5 and the two M3 inserts. The plugs of the socket leads and the "
             "inline plugs of the button and the knob pass through the window, so the plate comes out with its leads.",
             "Grey: the floor of 10. Violet: the hub, as fit.Layout places it."],
         os.path.join(SHEETS, "4-plate-out.png"), w=760)
    grid([("The plate in place, seen from inside the deck. Orange: the room for the cable bends and the wires", "behind")], ("plate-inside",),
         ("from inside, toward the right side",), "Front socket plate: behind the plate", [
             "The hardware sizes are estimates until the parts are measured (docs/design/front-socket-plate.md)."],
         os.path.join(SHEETS, "5-behind-the-plate.png"), w=1100)
    section_sheet(os.path.join(SHEETS, "6-sections.png"))
    grid([("The knob alone in a small plate (50 x 33) in the left side of the deck; the right plate has the button and the sockets", "knob-left")],
         ("deck-left", "left-quarter", "left-side", "deck-right"), ("the left side of the deck", "the small plate", "square to the left side", "the right side of the deck"),
         "Front socket plate: the alternative with the knob on the left side", [
             "This is the alternative that the audio research asks for if one plate is too short. One plate is not too short: with the sockets in two rows, "
             "the button, the knob and the four sockets fit in the plate of 142 (sheets 1 and 2). One row does not fit: the flat of the side is 153 long.",
             "The small plate has the height, the round ends, the reveal and the two screws of the socket plate. It adds a second opening, in the print piece deck side L."],
         os.path.join(SHEETS, "7-knob-on-the-left.png"), w=560)


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else ""
    if step in ("fcstd", "all"):
        fcstd()
    if step in ("render", "all"):
        render(tuple(sys.argv[2:]))
    if step in ("sheets", "all"):
        sheets()
    if step not in ("fcstd", "render", "sheets", "all"):
        raise SystemExit(__doc__)
