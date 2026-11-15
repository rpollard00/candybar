"""Sheets of the control panel, with every BREP edge drawn.

The models are the scene directories that candybar.shell.panel_frame writes into cad/out/control-panel/scenes (meshes,
manifest.json, edges.json and focus.json with the cameras, see render_views.py). Steps:

    cad/.venv-tools/bin/python cad/tools/draw_panel.py [OUT]            render every scene, then make the sheets
    cad/.venv-tools/bin/python cad/tools/draw_panel.py [OUT] sheets     make the sheets again from the renders

OUT is cad/out/control-panel. The renders go to OUT/renders/<scene>/<view>.png, the sheets to OUT/sheets.
Blender runs in background mode, one scene at a time. Needs Pillow (cad/.venv-tools); no FreeCAD.
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
INK, MUTED = (30, 30, 34), (110, 110, 118)
# scene: its views
SCENES = {"in-place": ("above", "above-left"), "lifted": ("lifted",), "frame": ("frame", "frame-corner"),
          "section-lever": ("section", "section-oblique"), "latch-screw": ("latch", "latch-oblique"),
          "latch-magnet": ("latch", "latch-oblique"), "underside": ("underside", "underside-lever"),
          "blank": ("above-left",), "blank-underside": ("underside",)}


def render(out: str) -> None:
    script = os.path.join(HERE, "render_views.py")
    for scene, views in SCENES.items():
        subprocess.run([sys.executable, script, os.path.join(out, "renders", scene), os.path.join(out, "scenes", scene),
                        "--views", ",".join(views), "--size", "1500", "--samples", "16"], check=True)


def picture(out: str, scene: str, view: str, w: int) -> Image.Image:
    im = Image.open(os.path.join(out, "renders", scene, f"{view}.png")).convert("RGB")
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def sheet(out: str, name: str, title: str, cells: list[tuple[str, str, str]], notes: list[str], w: int = 900, per_row: int = 2) -> None:
    """A sheet: the pictures of `cells` (scene, view, label) in rows of per_row, and the notes below them."""
    gap, top = 14, 84
    pictures = [(picture(out, scene, view, w), label) for scene, view, label in cells]
    rows = [pictures[k:k + per_row] for k in range(0, len(pictures), per_row)]
    width = gap + per_row * (w + gap)
    lines = [line for note in notes for line in (textwrap.wrap(note, int(width / 11.5)) or [""])]
    height = top + sum(34 + max(im.height for im, _ in row) + gap for row in rows) + 28 * len(lines) + 30
    page = Image.new("RGB", (width, height), (255, 255, 255))
    dr = ImageDraw.Draw(page)
    dr.text((gap, 22), title, fill=INK, font=font(34, bold=True))
    y = top
    for row in rows:
        for c, (im, label) in enumerate(row):
            dr.text((gap + c * (w + gap), y), label, fill=MUTED, font=font(20))
            page.paste(im, (gap + c * (w + gap), y + 34))
        y += 34 + max(im.height for im, _ in row) + gap
    for line in lines:
        dr.text((gap, y), line, fill=INK, font=font(20))
        y += 28
    os.makedirs(os.path.join(out, "sheets"), exist_ok=True)
    path = os.path.join(out, "sheets", name)
    page.save(path)
    print("draw_panel:", path)


def sheets(out: str) -> None:
    rep = json.load(open(os.path.join(out, "report.json")))
    i, a, st = rep["interface"], rep["arcade"], rep["stiffness"]
    ribs, flat = st["cases"]["with the ribs"], st["cases"]["flat plate of 5, no ribs"]
    lt = st["latch"]
    edges = "All BREP edges are drawn."
    sheet(out, "01-panel-above.png", "Arcade panel in the pocket of the deck",
          [("in-place", "above", "from above"), ("in-place", "above-left", "from the front left")],
          [edges, f"The plate is two printed tiles of ABS, 5 thick, with a seam at x {rep['seam_x']:g} between the lever and the buttons. "
           f"Its top lies 2 below the deck top, as the form has it, and stands {i['seat_gap']:g} inside the wall of its seat. "
           f"The top edge of its outline has the edge break of R 1.",
           f"Buttons: {a['buttons']} (Sanwa OBSF). The plate is {a['seat_t']:g} thick round each button hole. "
           "Four flush M4 screws show on the top face, one in each corner."])
    sheet(out, "02-panel-lifted.png", "Panel lifted out; the frame stays in the deck",
          [("lifted", "lifted", "the panel 95 above its seat"), ("frame", "frame", "the frame and the opening, from above")],
          [edges, "The frame (blue) is two halves, bonded under the ledge of the opening, on four posts that stand on the floor. "
           f"A pad in each corner of the opening has the M4 insert of a latch point. Two pads at the rear edge have the locating cones "
           f"(x -{i['cone_x']:g}: round socket in the panel; x +{i['cone_x']:g}: slot). The clip at the rear edge holds the USB cable.",
           f"The cable has {i['cable_slack']:g} of slack between the clip of the frame and the clip under the panel."])
    sheet(out, "03-section-lever.png", "Section through the lever (x -75), seen from the right",
          [("section-lever", "section", "section"), ("section-lever", "section-oblique", "the same cut, turned")],
          [edges, "The line in the cut plane is the true section of the skin of the deck.",
           "The plate of the lever bolts under a pad, 9.25 below the top of the panel. The pad lies between the rib beside the encoder and the "
           "flanges of the seam. The load goes from the ribs to the front and rear ledges, into the bar of the frame and its posts, and to the floor.",
           f"Hand estimate, {st['load_N']:g} N on the ball: the ball moves {ribs['forward_ball_mm']} forward and {ribs['side_ball_mm']} sideways "
           f"(a flat plate of 5 with no ribs: {flat['forward_ball_mm']} and {flat['side_ball_mm']})."])
    sheet(out, "04-latch.png", "The latch, close up: a flush M4 screw into an insert in the frame",
          [("latch-screw", "latch", "cut through the front right latch point"), ("latch-screw", "latch-oblique", "the same cut, turned"),
           ("frame", "frame-corner", "the pad of the frame with its insert, panel removed")],
          [edges, f"The pad stands inside the corner of the opening. Its top is {i['pad_drop']:g} below the rest face, so the plate rests on the ledge. "
           f"Screw: M4 x {i['latch_screw_l']:g} countersunk, 3 mm hex key. The countersink is {i['screw_head_d']:g} across."], per_row=3, w=640)
    sheet(out, "05-latch-options.png", "Two latch options on the same four latch points",
          [("latch-screw", "latch-oblique", "A. Screws (built as the default)"), ("latch-magnet", "latch-oblique", "B. Magnets")],
          [edges, "A. Four flush M4 screws into heat-set inserts. One common tool. The screws pull the panel down on the ledge. Four heads show.",
           f"B. A magnet of {i['magnet_d']:g} x {i['magnet_h']:g} in each pad and one of {i['magnet_d']:g} x {i['keeper_h']:g} in the plate. No tool, and "
           f"nothing shows. ESTIMATED hold: {lt['magnet_edge_N']:g} N on one edge, against {lt['lift_per_edge_N']} N from the lever "
           f"(factor {lt['magnet_factor']}). A pull of {lt['magnet_lift_out_N']:g} N on the lever lifts the panel out.",
           "The research note does not recommend magnets as the only latch: a lever moment peels the panel. Option A is the proposal."])
    sheet(out, "06-underside.png", "Arcade panel from below",
          [("underside", "underside", "the two tiles with the hardware"), ("underside", "underside-lever", "the lever, the encoder and the cable clip")],
          [edges, f"Ribs {i['rib_h']:g} deep: one along the front, one along the rear, one beside the encoder, the flanges of the seam, and one between "
           "the buttons and the service buttons. Four bosses hold the encoder. The clip holds the cable, which passes the rib through a gate."])
    sheet(out, "07-blank-panel.png", "The blank panel: made from the interface only",
          [("blank", "above-left", "in the pocket"), ("blank-underside", "underside", "from below")],
          [edges, "It has the outline, the rest face, the two sockets, the four latch points and the cable clip of the interface, and it goes on the same frame."])


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    only_sheets = "sheets" in args
    out = next((a for a in args if a != "sheets"), os.path.join(ROOT, "out", "control-panel"))
    if not only_sheets:
        render(out)
    sheets(out)
