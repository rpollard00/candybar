"""A study, not a part of the design: how large a screen the shell can take (docs/research/larger-monitor.md).

It measures on built parts and changes none of them. It reads the skin from the cache of the split, the parts of the
cradle and the hardware of the fit study as the laptop built them, and the parts of the outer form.

    CANDYBAR_OUT=cad/out/larger-monitor cad/candybar/freecad-run.sh candybar.shell.monitor_study
    MONITOR_STUDY=cut,room,units ...      # only these steps (default: cut, room, units, front)
    cad/.venv-tools/bin/python cad/tools/draw_larger_monitor.py

Inputs (each can be set): CANDYBAR_SHELL (default cad/out/shell-rev7: the outer form and the cache of the skin),
MONITOR_STUDY_BUILT (default cad/out/laptop-2026-11-15: cradle/ and fit/ of the present monitor).

Frame: (x, v, t) of cradle.Frame. x is across the cabinet, v is up the screen face from the centre of the image, t is
the depth behind the screen face. The glass of a unit is on the plane t = mon_setback + glass_gap (8.2).

Steps and files:
  cut      cuts.json: the skin, the cradle and the hardware cut by planes x = const and v = const, as polylines
  room     room.json: the free room behind the opening. From a grid of points on the glass plane, a ray along x, v
           and t to the first face of the skin, of the fixed cradle parts and of the hardware
  units    units.json: each unit of UNITS as a box at its place: the volume that it shares with the skin, the lugs,
           the cradle and the hardware, and its gap to each
  front    front.json: the outer form seen square to the screen face, its visible edges only (hidden lines removed)
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import FreeCAD as App
import Part

from . import cradle as cr
from . import split
from .dims import Blueprint
from .monitor_pictures import UNITS, Screen, glass_t

V = App.Vector
CAD = Path(__file__).resolve().parents[2]
SIDE_CUTS = (0.0, 50.0, 84.0, 120.0, 160.0, 190.0, 205.0, 215.0, 225.0, 235.0)
FACE_CUTS = (-190.0, -170.0, -150.0, -140.0, -120.0, -80.0, -40.0, 0.0, 40.0, 80.0, 120.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0, 200.0)
# the box of the screen zone in which the skin is kept for the rays and the units
ZONE = ((-270.0, 270.0), (-215.0, 250.0), (-40.0, 230.0))
RAY = 600.0


def built() -> Path:
    return Path(os.environ.get("MONITOR_STUDY_BUILT") or CAD / "out" / "laptop-2026-11-15")


def read(path: Path) -> Part.Shape:
    s = Part.Shape()
    s.read(str(path))
    return s


def skin(d: Blueprint) -> dict[str, Part.Shape]:
    out = {}
    for k, path in split.skin_files(d).items():
        out[k] = Part.Shape()
        out[k].importBinary(str(path))
    return out


def cradle_parts() -> dict[str, Part.Shape]:
    folder = built() / "cradle"
    names = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    return {k: read(folder / e["brep"]) for k, e in names.items()}


def hardware(d: Blueprint) -> dict[str, tuple[Part.Shape, str, str]]:
    """Each solid of the fit study at its place: the shape, its item and its role."""
    _, found = cr.fit_items(d, built())
    return {s.name: (s.world, it.name, s.role) for it in found for s in it.solids}


def lines(shape: Part.Shape, normal: App.Vector, at: float, f: cr.Frame) -> list:
    out = []
    for w in shape.slice(normal, at):
        out.append([[round(c, 2) for c in f.local(p)] + [round(p.y, 2), round(p.z, 2)] for p in w.discretize(Deflection=0.05)])
    return out


def cuts(d: Blueprint, shapes: dict[str, Part.Shape]) -> dict:
    """Every shape cut by the planes x = const and v = const. A point is (x, v, t, y, z)."""
    f = cr.Frame(d)
    out = {"side": {}, "face": {}}
    for x in SIDE_CUTS:
        out["side"][f"{x:g}"] = {k: ln for k, s in shapes.items() if (ln := lines(s, V(1, 0, 0), x, f))}
    for v in FACE_CUTS:
        at = f.pt(0, v, 0).dot(f.up)
        out["face"][f"{v:g}"] = {k: ln for k, s in shapes.items() if (ln := lines(s, f.up, at, f))}
    return out


def reach(start: App.Vector, way: App.Vector, shape: Part.Shape) -> float:
    """The distance from start along way to the first point of shape, or RAY when the ray is free."""
    hit = Part.makeLine(start, start + way * RAY).common(shape)
    pts = [p.Point for e in hit.Edges for p in e.Vertexes]
    return min(((p - start).dot(way) for p in pts), default=RAY)


def room(d: Blueprint, c: cr.Cradle, groups: dict[str, Part.Shape]) -> dict:
    """From points on the glass plane (and on planes behind it), the free length along +x, -v, +v and +t to each
    group of solids."""
    f = cr.Frame(d)
    g = cr.glass_t(d, c)
    rows = []
    for t in (g + 1.0, 14.0, 20.0, 30.0, 45.0, 60.0):
        for x in (0.0, 60.0, 120.0, 180.0, 210.0):
            p = f.pt(x, 0.0, t)
            rows.append({"from": [x, 0.0, t], "way": "+v", **{k: round(reach(p, f.up, s), 2) for k, s in groups.items()}})
            rows.append({"from": [x, 0.0, t], "way": "-v", **{k: round(reach(p, f.up * -1, s), 2) for k, s in groups.items()}})
        for v in (-150.0, -120.0, -60.0, 0.0, 60.0, 120.0, 150.0, 165.0, 180.0):
            p = f.pt(0.0, v, t)
            rows.append({"from": [0.0, v, t], "way": "+x", **{k: round(reach(p, V(1, 0, 0), s), 2) for k, s in groups.items()}})
    for x in (0.0, 60.0, 120.0, 150.0, 180.0, 200.0):
        for v in (-150.0, -120.0, -80.0, -40.0, 0.0, 40.0, 80.0, 120.0, 150.0):
            p = f.pt(x, v, g)
            rows.append({"from": [x, v, g], "way": "+t", **{k: round(reach(p, f.into, s), 2) for k, s in groups.items()}})
    return {"glass_t": g, "rows": rows}


def body_box(d: Blueprint, c: cr.Cradle, u: Screen, turned: bool = False) -> tuple[Part.Shape, tuple[float, ...]]:
    """The body of a unit with its glass on its glass plane (monitor_pictures.glass_t). The centre of its picture is on the centre of the image.
    turned: the body lies with its long side up the face."""
    f = cr.Frame(d)
    w, h, up = (u.h, u.w, 0.0) if turned else (u.w, u.h, u.up)
    g = glass_t(w, h)
    v0 = -up - h / 2
    return f.box((-w / 2, w / 2), (v0, v0 + h), (g, g + u.t)), (-w / 2, w / 2, v0, v0 + h, g, g + u.t)


TURNED = ("p18",)     # the units that the study also tries with the long side up the face


def units(d: Blueprint, c: cr.Cradle, groups: dict[str, Part.Shape]) -> list[dict]:
    """Each unit at its place: the volume that it shares with each group, and its gap to each group but the skin.
    The gap to the skin takes an hour for each unit on this machine; the sections give it (tools/larger_monitor_room.py).
    MONITOR_UNITS names the units to try (default: all)."""
    only = [k for k in (os.environ.get("MONITOR_UNITS") or "").split(",") if k]
    rows = []
    for u in UNITS:
        if only and u.key not in only:
            continue
        for turned in (False, True) if u.key in TURNED else (False,):
            box, edge = body_box(d, c, u, turned)
            row = {"key": u.key, "name": u.name, "turned": turned, "x": edge[:2], "v": edge[2:4], "t": edge[4:], "with": {}}
            for k, s in groups.items():
                row["with"][k] = {"common_mm3": round(cr.volume_in(box, s), 1)}
                if k != "skin":
                    row["with"][k]["gap"] = round(cr.gap(box, s), 2)
                print(u.key, "turned" if turned else "", k, row["with"][k], flush=True)
            rows.append(row)
    return rows


def front(d: Blueprint, parts: dict[str, Part.Shape]) -> dict:
    """The visible edges of each part of the outer form, seen square to the screen face, as polylines in (x, v)."""
    import TechDraw  # noqa: PLC0415
    f = cr.Frame(d)
    # the frame (x, v, t) becomes (X, Y, -Z): the viewer looks along -Z
    m = App.Matrix(1, 0, 0, -f.c.x,
                   f.up.x, f.up.y, f.up.z, -f.c.dot(f.up),
                   -f.into.x, -f.into.y, -f.into.z, f.c.dot(f.into),
                   0, 0, 0, 1)
    whole = Part.makeCompound(list(parts.values())).transformGeometry(m)
    seen = TechDraw.projectEx(whole, V(0, 0, 1))
    out = {}
    for name, group in zip(("sharp", "smooth", "sewn", "outline", "iso"), seen[:5]):
        out[name] = [[[round(p.x, 2), round(p.y, 2)] for p in e.discretize(Deflection=0.1)] for e in group.Edges]
    return out


def main() -> int:
    out = Path(os.environ.get("CANDYBAR_OUT") or CAD / "out" / "larger-monitor")
    out.mkdir(parents=True, exist_ok=True)
    steps = (os.environ.get("MONITOR_STUDY") or "cut,room,units,front").split(",")
    d, c = Blueprint(), cr.Cradle()
    f = cr.Frame(d)
    if "front" in steps:
        folder = cr.shell_dir()
        names = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        parts = {k: read(folder / e["brep"]) for k, e in names.items() if k != "screen"}
        (out / "front.json").write_text(json.dumps(front(d, parts)), encoding="utf-8")
        print("front.json", flush=True)
    if not {"cut", "room", "units"} & set(steps):
        return 0
    sk = skin(d)
    cp = cradle_parts()
    hw = hardware(d)
    print("read: the skin", list(sk), "the cradle", list(cp), "the hardware", len(hw), "solids", flush=True)
    if "cut" in steps:
        shapes = {f"skin_{k}": s for k, s in sk.items()}
        shapes.update({f"cradle_{k}": s for k, s in cp.items()})
        shapes.update({f"hw_{k}": s for k, (s, _, _) in hw.items()})
        data = cuts(d, shapes)
        data["hardware"] = {k: {"item": item, "role": role} for k, (_, item, role) in hw.items()}
        data["frame"] = {"c": list(f.c), "up": list(f.up), "into": list(f.into), "glass_t": cr.glass_t(d, c)}
        (out / "cuts.json").write_text(json.dumps(data), encoding="utf-8")
        print("cuts.json", flush=True)
    if not {"room", "units"} & set(steps):
        return 0
    zone = f.box(*ZONE)
    near = {}
    for k, s in sk.items():                      # the cut of the skin takes minutes: keep it beside the results
        kept = out / f"zone-{k}.brep"
        if not kept.exists():
            s.common(zone).exportBrep(str(kept))
        near[k] = read(kept)
    print("the skin in the screen zone:", {k: round(s.Volume) for k, s in near.items()}, flush=True)
    own = ("Monitor", "Monitor, any 16:10", "Monitor cables")
    groups = {"skin": Part.makeCompound([s for s in near.values() if s.Volume > 0]),
              "lugs": cp["lugs"], "bosses": cp["bosses"],
              "uprights": Part.makeCompound([cp["upright_right"], cp["upright_left"]]),
              "channels": Part.makeCompound([cp["channel_right"], cp["channel_left"]])}
    panel = ("Lever", "Encoder", "Btn", "Svc")
    names = {i: ("Controls" if i.startswith(panel) else "USB sockets" if i.startswith("USB") else "Speakers" if i.startswith("Speaker") else i)
             for _, i, _ in hw.values() if i not in own}
    for name in sorted(set(names.values())):
        for role in ("hardware", "keepout"):
            found = [s for s, i, r in hw.values() if names.get(i) == name and r == role]
            if found:
                groups[f"{name}: {role}"] = Part.makeCompound(found)
    if "room" in steps:
        (out / "room.json").write_text(json.dumps(room(d, c, groups), indent=1), encoding="utf-8")
        print("room.json", flush=True)
    if "units" in steps:
        (out / "units.json").write_text(json.dumps(units(d, c, groups), indent=1), encoding="utf-8")
        print("units.json", flush=True)
    return 0
