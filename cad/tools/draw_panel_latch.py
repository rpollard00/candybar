"""Sheets of the latch study of the control panel, with every BREP edge drawn.

The models are the scene directories that candybar.shell.panel_latch writes into cad/out/panel-latch/<candidate>/scenes
(meshes, manifest.json, edges.json and focus.json with the cameras, see render_views.py). Steps:

    cad/.venv-tools/bin/python cad/tools/draw_panel_latch.py [OUT]            render every scene, then make the sheets
    cad/.venv-tools/bin/python cad/tools/draw_panel_latch.py [OUT] sheets     make the sheets again from the renders
    cad/.venv-tools/bin/python cad/tools/draw_panel_latch.py [OUT] B          only B: sheet 03 and sheet 06 (the grip)

OUT is cad/out/panel-latch. The renders go to OUT/<candidate>/renders/<scene>/<view>.png, the sheets to OUT/sheets.
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
INK, MUTED, BAD, GOOD = (30, 30, 34), (110, 110, 118), (170, 40, 40), (30, 110, 50)
CANDIDATES = ("M", "H", "B", "Q")
SCENES = {"top": ("player", "front"), "section-locked": ("section",), "section-released": ("section",),
          "way-1": ("way",), "way-2": ("way",), "way-3": ("way",), "way-4": ("way",), "parts": ("parts",), "blank": ("player", "hole")}


def run(script: str, out: str, scene: str, views: tuple[str, ...], size: int) -> None:
    subprocess.run([sys.executable, script, out, scene, "--views", ",".join(views), "--size", str(size), "--samples", "16"], check=True)


def render(out: str, which: tuple[str, ...] = CANDIDATES) -> None:
    script = os.path.join(HERE, "render_views.py")
    for c in which:
        for scene, views in SCENES.items():
            src = os.path.join(out, c, "scenes", scene)
            if os.path.isdir(src):
                run(script, os.path.join(out, c, "renders", scene), src, views, 1400)
        src = os.path.join(out, "scenes", f"compare-{c}")
        if os.path.isdir(src) and tuple(which) == CANDIDATES:
            run(script, os.path.join(out, "renders", f"compare-{c}"), src, ("player",), 1400)


def picture(path: str, w: int) -> Image.Image:
    im = Image.open(path).convert("RGB")
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def page(out: str, name: str, title: str, cells: list[tuple[str, str]], notes: list[str], w: int = 760, per_row: int = 2, subtitle: str = "") -> None:
    """A sheet: the pictures of `cells` (path, label) in rows of per_row, and the notes below them."""
    gap, top = 16, 96 if subtitle else 70
    pictures = [(picture(p, w), label) for p, label in cells]
    rows = [pictures[k:k + per_row] for k in range(0, len(pictures), per_row)]
    width = gap + per_row * (w + gap)
    wrap = int(width / 11.2)
    lines = []
    for note in notes:
        lines += textwrap.wrap(note, wrap) or [""]
    height = top + sum(34 + max(im.height for im, _ in row) + gap for row in rows) + 27 * len(lines) + 30
    sheet = Image.new("RGB", (width, height), (255, 255, 255))
    dr = ImageDraw.Draw(sheet)
    dr.text((gap, 18), title, fill=INK, font=font(32, bold=True))
    if subtitle:
        dr.text((gap, 58), subtitle, fill=MUTED, font=font(21))
    y = top
    for row in rows:
        for c, (im, label) in enumerate(row):
            dr.text((gap + c * (w + gap), y), label, fill=MUTED, font=font(20))
            sheet.paste(im, (gap + c * (w + gap), y + 32))
        y += 34 + max(im.height for im, _ in row) + gap
    for line in lines:
        dr.text((gap, y), line, fill=INK, font=font(19))
        y += 27
    os.makedirs(os.path.join(out, "sheets"), exist_ok=True)
    path = os.path.join(out, "sheets", name)
    sheet.save(path)
    print("draw_panel_latch:", path)


def r(out: str, c: str, scene: str, view: str) -> str:
    return os.path.join(out, c, "renders", scene, f"{view}.png")


TEXT = {
    "M": ("M. Magnets only",
          ["How it works: a magnet pair at each corner holds the panel down on its ledge. The two cones at the rear edge stop it sliding. To take it out, pull it straight up.",
           "To put it in: set it on the ledge; the cones find the sockets and the magnets pull it down."]),
    "H": ("H. Rear hooks and magnets",
          ["How it works: two hooks under the rear edge of the panel go under the rear bar of the frame. The front edge is held only by the two front magnets.",
           "To take it out: lift the front edge (by the lever). The panel turns about its rear top edge and the hooks slide out of their notches; then lift it up and forward.",
           "To put it in: hold the panel with its front up, put its rear edge down against the rear of the pocket, and lower the front."]),
    "B": ("B. Rear hooks and a push bolt: the final form",
          ["How it works: two hooks under the rear edge of the panel go under the rear bar of the frame. At the front centre a printed bolt goes over two lips of a strike under the panel. "
           "A steel spring pushes the bolt forward, and an 8 degree wedge under it pulls the panel down, so the panel sits without play. Four magnet pairs keep the corners down. "
           "The front end of the bolt is a flush button in the front face of the deck, on the centre line. The bolt slides in a tunnel that is one print with the frame; a gate at the rear of the tunnel holds its spring.",
           "To take it out: hold the button in (5). Lift the panel by the lever, or a blank panel by its finger hole. It turns about its rear edge; pull it up and forward.",
           "To put it in: put the rear edge down against the rear of the pocket, hold the button in, lower the front, let the button go. If the button is not held, the panel stands 8 high at the front and does not seat."]),
    "Q": ("Q. Rear hooks and two quarter-turn cams",
          ["How it works: the rear hooks of H hold the rear edge. Near the front edge, two printed cams go through the panel. Under the panel the tongue of each cam turns under the front bar of the frame.",
           "To take it out: turn the two heads a quarter turn with a finger (the finger bar shows the way of the tongue), lift the front edge by the lever or by the finger bars, and pull the panel up and forward.",
           "To put it in: as H, then turn the two heads back."]),
}


def factor_line(s: dict) -> str:
    return f"Hold (ESTIMATED): factor {s['factor']:g} against the worst of a pull of 80 N on the lever and a push of 50 N at the ball. Normal play (15 N at the ball) without a click: factor {s['play']:g} on the preload alone."


def b_notes(s: dict) -> list[str]:
    p, rock, rr = s["preload"], s["corner_rock"], s["removal"]
    hard = rock["rows"][1]
    return [f"The button: it starts to move at {p['button_start_N']:g} N and needs {p['button_force_N']:g} N at the end of its {p['stroke_mm']:g}. The lips are free after {p['unlocks_at_mm']:g}. "
            "It is flush: a flat thing on the front face (a knee, a hand, the edge of a desk) cannot push it in, only a fingertip.",
            f"Preload at the front: {p['wedge_down_N']:g} N from the wedge. The front corners (beam estimate, hard input of 50 N): with no magnet the front left corner lifts "
            f"{hard['no_front_magnets']['corner_lift_mm']:g}; with the magnet it lifts {hard['front_magnets']['largest_lift_mm']:g} at most and the magnet holds its share with a factor of {hard['front_magnets']['factor']:g}.",
            f"To lift out with the button in: {rr['lever_N']:g} N up on the lever, {rr['finger_hole_N']:g} N at the finger hole of a blank panel."]


def ramp_drawing(out: str, s: dict) -> str:
    """A side view of the grip that B does not take: a rigid ramp on the bolt under the legs of the strike."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Rectangle

    ro = s["ramp_option"]
    path = os.path.join(out, "B", "renders", "ramp", "ramp.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig, axes = plt.subplots(2, 1, figsize=(7.6, 6.4), dpi=130)
    for ax, (title, shift, lift) in zip(axes, (("locked: the ramp stands in front of the legs", 0.0, 0.0),
                                              (f"button in by {ro['travel_mm']:g}: the ramp lifts the strike {ro['rise_at_strike_mm']:g}", ro["travel_mm"], ro["rise_at_strike_mm"]))):
        ax.add_patch(Rectangle((10 + shift, 52), 56, 6, fc="#d0762b", ec="k", lw=0.8))
        ax.add_patch(Polygon([(30 + shift, 52), (39 + shift, 52), (41.5 + shift, 49.5), (41.5 + shift, 47), (30 + shift, 47)], fc="#e8a060", ec="k", lw=0.8, hatch="//"))
        ax.add_patch(Rectangle((46.5, 49.5 + lift), 4, 15.5, fc="#2b2b2e", ec="k", lw=0.8))
        ax.add_patch(Rectangle((20, 65 + lift), 60, 5, fc="#2b2b2e", ec="k", lw=0.8))
        ax.add_patch(Rectangle((20, 42.5), 60, 4.5, fc="#5a7fa8", ec="k", lw=0.8))
        ax.text(12 + shift, 54.2, "bolt", fontsize=9)
        ax.text(31 + shift, 47.6, "ramp", fontsize=9)
        ax.text(51.5, 56, "leg of the strike", fontsize=9)
        ax.text(22, 66.6 + lift, "plate of the panel", fontsize=9, color="white")
        ax.text(22, 43.6, "floor of the tunnel (lower)", fontsize=9, color="white")
        ax.set_xlim(5, 85)
        ax.set_ylim(40, 74)
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("y, from the front face of the deck")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path


def sheet_b(out: str, s: dict) -> None:
    """Sheet 03 (the final form of B) and the sheet of the two ways to grip a blank panel."""
    edges = ("All BREP edges are drawn. Blue: the frame (stays in the cabinet). Dark: the panel. Orange: the bolt. Light blue: the gate. Grey: magnets and the spring. "
             "The colours are for the pictures only: the button prints in the colour of the deck.")
    title, how = TEXT["B"]
    sh = s["shows"]
    page(out, "03-B-hooks-and-a-push-bolt.png", title,
         [(r(out, "B", "top", "player"), "1. what the player sees, panel in"), (r(out, "B", "top", "front"), "2. the front face of the deck"),
          (r(out, "B", "section-locked", "section"), "3. section through the bolt, locked"), (r(out, "B", "section-released", "section"), "4. the same section, the button held in"),
          (r(out, "B", "way-1", "way"), "5. way out: button in, front lifted"), (r(out, "B", "way-2", "way"), "6. step 2"),
          (r(out, "B", "way-3", "way"), "7. step 3"), (r(out, "B", "way-4", "way"), "8. step 4: out"),
          (r(out, "B", "parts", "parts"), "9. the latch parts apart: the tunnel (a part of the frame), the bolt, the spring, the gate, the strike")],
         how + [f"On the top face: {sh['top_in']} On the front face: {sh['front_in']}", f"Panel out: {sh['out']}", f"The gap round the panel: {sh['gap']}",
                factor_line(s)] + b_notes(s) + ["Buy: " + "; ".join(s["buy"]) + ".", edges])
    ro, rr = s["ramp_option"], s["removal"]
    page(out, "06-B-grip-for-a-blank-panel.png", "B: two ways to grip a panel with nothing to hold",
         [(r(out, "B", "blank", "player"), "A. a finger hole in the panel (taken)"), (r(out, "B", "blank", "hole"), "A. the finger hole, close"),
          (ramp_drawing(out, s), "B. a ramp on the bolt (not taken)")],
         [f"A. A finger hole of 22 through the plate of the blank panel, near its front edge, with the edge break on both rims. A finger goes in and lifts the panel ({rr['finger_hole_N']:g} N with the button in). "
          "It shows on the top face of the blank panel only. No part, no spring, and nothing changes in the cabinet or in the hold.",
          f"B. A rigid ramp on the bolt lifts the strike {ro['rise_at_strike_mm']:g} after the lips are free: the front edge rises {ro['front_edge_rise_mm']:g} and stands {ro['above_deck_top_mm']:g} above the deck top while the button is held. "
          f"Nothing shows. But the button must travel {ro['travel_mm']:g} in place of 5 (a fingertip does not go that far into a flush hole of 14.6), the button force becomes about {ro['button_N']:g} N "
          "because the ramp lifts the front against the magnets, the bolt gets longer, and the floor of the tunnel must go down. The edge that it raises is too low to hold well.",
          "Recommendation: A. It is simpler, it adds no way to fail, and only a panel with nothing to hold carries it. A panel with a lever or keys lifts by them.", edges],
         w=760, per_row=2)


def sheets(out: str, which: tuple[str, ...] = CANDIDATES) -> None:
    summ = json.load(open(os.path.join(out, "summary.json")))
    if "B" in which:
        sheet_b(out, summ["B"])
    if tuple(which) != CANDIDATES:
        return
    edges = ("All BREP edges are drawn. Blue: the frame (stays in the cabinet). Dark: the panel. Orange: the parts of the latch that move. Grey: magnets and springs. "
             "The colours are for the pictures only: the button of B prints in the colour of the deck, the heads of Q in the colour of the panel.")
    for k, c in enumerate(CANDIDATES):
        if c == "B":
            continue
        s = summ[c]
        title, how = TEXT[c]
        sh = s["shows"]
        first = "the panel is lifted 5" if c == "M" else "the front edge is up 4 degrees" if c == "H" else "released"
        page(out, f"{k + 1:02d}-{c}-{s['name'].lower().replace(' ', '-')}.png", title,
             [(r(out, c, "top", "player"), "1. what the player sees, panel in"), (r(out, c, "top", "front"), "2. the front face of the deck"),
              (r(out, c, "section-locked", "section"), "3. section through the latch, locked"), (r(out, c, "section-released", "section"), f"4. the same section, {first}"),
              (r(out, c, "way-1", "way"), "5. way out, step 1"), (r(out, c, "way-2", "way"), "6. step 2"),
              (r(out, c, "way-3", "way"), "7. step 3"), (r(out, c, "way-4", "way"), "8. step 4: out"),
              (r(out, c, "parts", "parts"), "9. the latch parts apart")],
             how + [f"On the top face: {sh['top_in']} On the front face: {sh['front_in']}", f"Panel out: {sh['out']}", f"The gap round the panel: {sh['gap']}",
                    factor_line(s), f"Removal: {s['removal']['how']}", "Buy: " + "; ".join(s["buy"]) + ".", edges])
    # the side-by-side sheet, from the same camera
    cells = [(os.path.join(out, "renders", f"compare-{c}", "player.png"), f"{c}. {summ[c]['name']}: factor {summ[c]['factor']:g}") for c in CANDIDATES]
    notes = [f"{c}. {summ[c]['name']}. Top face: {summ[c]['shows']['top_in']} Front face: {summ[c]['shows']['front_in']}" for c in CANDIDATES]
    notes += ["The factor is the smallest of all load cases: a pull of 80 N up on the lever, a push of 50 N at the ball in each of four directions, and the two together. "
              "It is ESTIMATED from maker's data for the magnets and from beam theory for the printed parts. Below 1 the panel comes out under the load.",
              "Recommendation: B. Nothing shows on the top face, no tool, a rigid lock against the pull, and a spring and wedge for the preload. "
              "The cost is a button on the front face of the deck.", edges]
    page(out, "05-side-by-side.png", "Four latches, the same camera", cells, notes, w=760)


if __name__ == "__main__":
    args = list(sys.argv[1:])
    only = "sheets" in args
    which = tuple(a for a in args if a in CANDIDATES) or CANDIDATES
    out = next((a for a in args if a != "sheets" and a not in CANDIDATES), os.path.join(ROOT, "out", "panel-latch"))
    if not only:
        render(out, which)
    sheets(out, which)
