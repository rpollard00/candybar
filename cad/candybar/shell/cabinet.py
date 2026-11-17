"""The cabinet as it is designed now, with everything in, for the owner: one folder and one FreeCAD document.

    cad/build.sh                                                                   # the outer form (cad/out/shell-rev7)
    CANDYBAR_OUT=cad/out/cradle cad/candybar/freecad-run.sh candybar.shell.cradle            # the bezel plate, the monitor
    CANDYBAR_OUT=cad/out/control-panel cad/candybar/freecad-run.sh candybar.shell.panel_frame   # the control panel
    CANDYBAR_OUT=cad/out/cabinet cad/candybar/freecad-run.sh candybar.shell.cabinet         # this folder
    CANDYBAR_OUT=cad/out/cabinet cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc   # cad/out/cabinet/shell.FCStd
    cad/.venv-tools/bin/python cad/tools/draw_cabinet.py cad/out/cabinet                   # cabinet.png

It reads the BREP files of the three builds and writes each part again into CANDYBAR_OUT (default cad/out/cabinet):
BREP, STL, manifest.json, edges.json (every face edge) and focus.json (the four cameras of the sheet).

  the shell        the default build: the deck with the seat of the socket plate, the body, the hood with band A,
                   every part of the band, the socket plate b-knob with its sockets, button and knob (solids.build).
                   The plain plate of the bezel and the plain control panel of the form are left out: the printed
                   parts take their places
  the bezel        the printed bezel plate with the push rod of the monitor's button, the monitor and the cradle
                   (candybar.shell.cradle)
  the panel        the arcade panel with the lever, the buttons and the encoder, the frame, the push bolt with its
                   button in the deck's front (candybar.shell.panel_frame)
  the rear         the door is on: the body of the form is closed at the door, which is its marking; the heads of the
                   door's two fasteners (candybar.shell.rear)
Names from two builds that are the same get the name of their build in front (cradle_screws, panel_magnets).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import MeshPart
import Part

from . import rear
from . import solids as so
from .dims import Blueprint

CAD = Path(__file__).resolve().parents[2]
OUT = "cad/out/cabinet"
# the parts of each build that the cabinet takes, and the names of the parts of the shell that it leaves out
SHELL_LEFT_OUT = ("bezel", "control_panel")
CRADLE_LEFT_OUT = ("bezel_plate_no_button", "skin")
PANEL_TAKEN = ("frame_left", "frame_right", "post_front_left", "post_front_right", "post_rear_left", "post_rear_right", "latch_bolt",
               "latch_gate", "panel_lever_tile", "panel_button_tile", "Lever", "Buttons", "Encoder", "magnets", "discs", "spring")
FINISH = {"bezel_plate": "#1b1d22", "button_rod": "#2a2c31", "monitor": "#16181c"}
# a colour that a build writes as a name, as a hex value (viewdoc reads white, black and hex values)
NAMED = {"grey": "#8c8f96"}


def read_build(folder: Path, take=None, leave=()) -> dict[str, tuple[Part.Shape, str]]:
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    out = {}
    for name, entry in manifest.items():
        if (take is not None and name not in take) or name in leave:
            continue
        s = Part.Shape()
        s.read(str(folder / entry["brep"]))
        out[name] = (s, NAMED.get(entry["finish"], entry["finish"]))
    return out


def gather(shell: Path, cradle: Path, panel: Path) -> dict[str, tuple[Part.Shape, str]]:
    """Every part of the cabinet by name, with its colour."""
    parts = read_build(shell, leave=SHELL_LEFT_OUT)
    for prefix, more in (("cradle", read_build(cradle, leave=CRADLE_LEFT_OUT)), ("panel", read_build(panel, take=PANEL_TAKEN))):
        for name, (s, finish) in more.items():
            key = f"{prefix}_{name}" if name in parts else name
            parts[key] = (s, FINISH.get(name, finish))
    d = Blueprint()
    for name, s in rear.fastener_heads(d, rear.Rear()).items():
        parts[name] = (s, "#3a3c40")
    return parts


def cameras(d: Blueprint) -> dict[str, dict]:
    """The four views of the sheet: the front, a three-quarter view from the front right, the right side and a
    three-quarter view from the rear left."""
    mid = [0.0, d.depth / 2, 287.0]
    cam = lambda az, el, radius, aspect=1.15: {"target": mid, "radius": radius, "az": az, "el": el, "aspect": aspect}
    return {"front": cam(0.0, 8.0, 370.0), "front-right": cam(38.0, 18.0, 420.0), "side": cam(90.0, 4.0, 440.0), "rear-left": cam(-140.0, 18.0, 440.0)}


def main() -> int:
    out = Path(os.environ.get("CANDYBAR_OUT", OUT))
    out.mkdir(parents=True, exist_ok=True)
    built = CAD / "out"
    parts = gather(Path(os.environ.get("CANDYBAR_SHELL", built / "shell-rev7")), built / "cradle", built / "control-panel")
    manifest, edges = {}, {}
    for name, (s, finish) in parts.items():
        s.exportBrep(str(out / f"{name}.brep"))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.08, AngularDeflection=0.08).write(str(out / f"{name}.stl"))
        manifest[name] = {"file": f"{name}.stl", "brep": f"{name}.brep", "finish": finish}
        edges[name] = so.edge_polylines(s)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    (out / "edges.json").write_text(json.dumps(edges), encoding="utf-8")
    (out / "focus.json").write_text(json.dumps(cameras(Blueprint()), indent=1), encoding="utf-8")
    print(f"cabinet: {len(parts)} parts -> {out}")
    return 0
