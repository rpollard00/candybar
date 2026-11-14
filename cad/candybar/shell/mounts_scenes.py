"""The model directories of the mount sheets, and the document of the mounts in the shell.

mounts.main calls write(): it makes one directory for each sheet in <out>/scenes, with the meshes of what the sheet
shows, manifest.json, edges.json (every BREP edge) and focus.json (the cameras). tools/draw_mounts.py renders them.
It also writes the hardware boxes to <out>/hardware, for the document.

The document, with the GUI binary (a document saved headless opens with every solid hidden):

    CANDYBAR_OUT=cad/out/mounts cad/candybar/freecad-run.sh --gui candybar.shell.mounts_scenes

It reads <out>/parts, <out>/hardware and the skin of the split, and writes <out>/shell.FCStd.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import FreeCAD as App
import MeshPart
import Part

from . import fit, mounts, split, viewdoc
from . import solids as so
from .dims import Blueprint

V = App.Vector
MESH_LINEAR, MESH_ANGULAR = 0.15, 0.1
SKIN, FLOOR = "#e9e7e1", "#cfcabd"
# the skin that the sheets show: behind the deck and below the rear shelf
VIEW_BOX = (-260.0, 260.0, 195.0, 560.0, -5.0, 300.0)
BIG = 2000.0
# what a sheet shows of the hardware: the solids, and the two zones that are parts of the compute module
SHOWN = ("hardware",)
ZONES_SHOWN = ("Compute_ExhaustDuct",)


def view_skin(d: Blueprint, log=print) -> Part.Shape:
    """The skin of the body inside VIEW_BOX, with the door opening cut out; kept in the cache of the split."""
    key = hashlib.sha256(repr(VIEW_BOX).encode()).hexdigest()[:8]
    f = split.cache_dir() / f"mounts-view-{split.fingerprint(d)}-{key}.bin"
    out = Part.Shape()
    if f.exists():
        out.importBinary(str(f))
        return out
    log("mounts: cutting the skin for the sheets (1 minute, once)")
    body = Part.Shape()
    body.importBinary(str(split.skin_files(d)["body"]))
    door = fit.door_outline(d)
    out = body.common(mounts.bx(*VIEW_BOX)).cut(mounts.bx(door["x0"], door["x1"], d.body_d - 30.0, d.body_d + 30.0, door["z0"], door["z1"]))
    out.exportBinary(str(f))
    return out


def scene(folder: Path, items: list[tuple[str, Part.Shape, str]], cameras: dict, keep: tuple[float, ...] | None = None) -> None:
    """A model directory: each item inside the box `keep` as a mesh, with every edge of what is left."""
    folder.mkdir(parents=True, exist_ok=True)
    manifest, edges = {}, {}
    box = mounts.bx(*keep) if keep else None
    for name, shape, finish in items:
        if box is not None:
            if not shape.BoundBox.intersect(box.BoundBox):
                continue
            shape = shape.common(box)
        if not shape.Faces:
            continue
        MeshPart.meshFromShape(Shape=shape, LinearDeflection=MESH_LINEAR, AngularDeflection=MESH_ANGULAR).write(str(folder / f"{name}.stl"))
        manifest[name] = {"file": f"{name}.stl", "finish": finish}
        edges[name] = so.edge_polylines(shape)
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    (folder / "edges.json").write_text(json.dumps(edges), encoding="utf-8")
    (folder / "focus.json").write_text(json.dumps(cameras, indent=1), encoding="utf-8")


def cam(target: tuple[float, float, float], radius: float, az: float, el: float, aspect: float) -> dict:
    return {"target": list(target), "radius": radius, "az": az, "el": el, "aspect": aspect}


def write(out: Path, d: Blueprint, result: mounts.Run, log=print) -> None:
    design, hw, s, m = result.design, result.hw, result.design.site, mounts.Mounts()
    skin = view_skin(d, log)
    floor = mounts.bx(-(s.wall_x - 0.2), s.wall_x - 0.2, 400.0, s.rear_y - 0.2, d.wall_t, s.floor)
    shell = [("skin", skin, SKIN), ("skin_floor", result.skin["base"].common(mounts.bx(*VIEW_BOX)), SKIN), ("floor", floor, FLOOR)]
    own = [(q.name, q.whole, mounts.FINISH["boss" if q.kind == "boss" else q.group]) for q in design.solids]
    boxes = [(k, shape, fit.FINISH.get(fit.group_of(owner), "#808080")) for k, (owner, role, shape) in hw.items()
             if (role in SHOWN or k in ZONES_SHOWN) and owner in ("Compute", "PSU", "CableBundle", "Hub")]
    module = [i for i in boxes if i[0].startswith("Compute")]
    rest = [i for i in boxes if not i[0].startswith("Compute")]
    trays = [i for i in own if i[0].startswith("Tray")]
    fixed = [i for i in own if not i[0].startswith("Tray")]
    folder = out / "scenes"
    fr, fl = mounts.tray_frame(s, m, 1.0), mounts.tray_frame(s, m, -1.0)
    mid_z = (s.bz0 + s.bz1) / 2
    # 1: the inside through the rear door opening, with all in place and with the compute module out
    rear = cam((0.0, 500.0, 180.0), 250.0, 180.0, 6.0, 0.62)
    scene(folder / "door", shell + own + boxes, {"through-the-door": rear})
    scene(folder / "door-module-out", shell + fixed + rest, {"through-the-door-module-out": rear, "through-the-door-from-above": cam((0.0, 470.0, 100.0), 255.0, 180.0, 38.0, 0.7)})
    # 2: the plan section at the floor
    scene(folder / "plan-floor", shell + own + boxes, {"plan-floor": cam((0.0, 370.0, 20.0), 262.0, 0.0, 90.0, 0.72)}, keep=(-BIG, BIG, -BIG, BIG, -BIG, 45.0))
    # 3: the sections through the compute module: a plan through the lower screw of the right tray, a side section
    # through the right upright, and a side section through a standoff
    z_cut = fr["zd0"] + m.secure_z[0]
    scene(folder / "plan-compute", shell + own + boxes, {"plan-compute": cam((0.0, 475.0, z_cut), 250.0, 0.0, 90.0, 0.32),
                                                       "plan-compute-right": cam((190.0, 452.0, z_cut), 62.0, 0.0, 90.0, 0.8),
                                                       "plan-compute-left": cam((-190.0, 452.0, z_cut), 62.0, 0.0, 90.0, 0.8)}, keep=(-BIG, BIG, -BIG, BIG, -BIG, z_cut))
    scene(folder / "side-upright", shell + own + boxes, {"section-right-upright": cam((fr["xc"], 475.0, 190.0), 95.0, 90.0, 0.0, 1.1)}, keep=(-BIG, fr["xc"], -BIG, BIG, -BIG, BIG))
    xs = s.bx0 + m.standoffs[1][0]
    scene(folder / "side-standoff", shell + own + boxes, {"section-standoff": cam((xs, 475.0, 190.0), 95.0, 90.0, 0.0, 1.1)}, keep=(-BIG, xs, -BIG, BIG, -BIG, BIG))
    # 4: each mount close up, with the rear wall cut away
    open_rear = (-BIG, BIG, -BIG, s.rear_y - 30.0, -BIG, BIG)
    scene(folder / "close-fixed", shell + fixed, {"dock-right": cam((195.0, 440.0, 158.0), 60.0, 222.0, 18.0, 0.9), "dock-left": cam((-195.0, 440.0, 158.0), 60.0, 138.0, 18.0, 0.9),
                                               "psu-fence": cam((-148.0, 450.0, 14.0), 120.0, 205.0, 42.0, 0.75), "bundle-ties": cam((0.0, 470.0, 40.0), 95.0, 195.0, 35.0, 0.8),
                                               "lead-ties": cam((0.0, 232.0, 12.0), 190.0, 180.0, 50.0, 0.4)}, keep=open_rear)
    scene(folder / "close-places", shell + fixed + rest, {"places-on-the-docks": cam((0.0, 450.0, 155.0), 245.0, 180.0, 4.0, 0.3),
                                                        "places-on-the-floor": cam((40.0, 340.0, 15.0), 215.0, 180.0, 55.0, 0.6)}, keep=open_rear)
    scene(folder / "close-hub", shell + fixed + rest, {"hub": cam((199.0, 297.0, 20.0), 75.0, 250.0, 32.0, 0.75)}, keep=open_rear)
    scene(folder / "close-all", shell + own + module, {"docks-with-trays-right": cam((180.0, 450.0, 170.0), 85.0, 215.0, 20.0, 1.0),
                                                     "docks-with-trays-left": cam((-185.0, 450.0, 170.0), 85.0, 145.0, 20.0, 1.0)}, keep=open_rear)
    board = [i for i in module if i[0] in ("Compute_PCB_IO", "Compute_PCB_Pwr", "Compute_Backplate", "Compute_Heatsink", "Compute_IO")]
    scene(folder / "trays", trays + board, {"trays-from-the-front": cam((0.0, 455.0, mid_z), 185.0, 20.0, 18.0, 0.6), "trays-from-the-rear": cam((0.0, 455.0, mid_z), 185.0, 200.0, 18.0, 0.6)})
    scene(folder / "saddle", [i for i in own if i[0].startswith("Hub")] + [i for i in rest if i[0] == "Hub_Body"], {"hub-saddle": cam((199.0, 297.0, 22.0), 55.0, 200.0, 25.0, 0.8)})
    # 5: the board on its way out: up off the hanging screws, then half through the door opening
    move = App.Placement(V(0, d.body_d - s.y_pcb + 20.0, m.drop), App.Rotation())
    moved = [(k, shape.transformed(move.toMatrix()), finish) for k, shape, finish in trays + module]
    scene(folder / "board-out", shell + fixed + rest + moved, {"board-out": cam((0.0, 540.0, 190.0), 290.0, 212.0, 18.0, 0.7), "board-out-side": cam((0.0, 520.0, 190.0), 150.0, 90.0, 0.0, 1.0)})
    # the hardware boxes, for the document
    hardware = out / "hardware"
    hardware.mkdir(parents=True, exist_ok=True)
    listing = {}
    for k, (owner, role, shape) in hw.items():
        shape.exportBrep(str(hardware / f"{k}.brep"))
        listing[k] = {"brep": f"{k}.brep", "finish": fit.FINISH.get(fit.group_of(owner), "#808080"), "role": role, "owner": owner}
    floor.exportBrep(str(hardware / "FloorTop.brep"))
    listing["FloorTop"] = {"brep": "FloorTop.brep", "finish": FLOOR, "role": "floor", "owner": "shell"}
    (hardware / "manifest.json").write_text(json.dumps(listing, indent=1), encoding="utf-8")


def main() -> int:
    """The document: the skin, the hardware boxes and the mounts."""
    if not App.GuiUp:
        print("view settings need FreeCAD's GUI binary: run this with freecad-run.sh --gui")
        return 1
    out = Path(os.environ["CANDYBAR_OUT"])
    d = Blueprint()
    settings = App.ParamGet("User parameter:BaseApp/Preferences/Document")
    settings.SetBool("CreateBackupFiles", False)
    settings.SetBool("SaveThumbnail", False)
    doc = App.newDocument("Mounts")
    count = 0

    def add(name: str, shape: Part.Shape, finish: str, group, transparency: int = 0, visible: bool = True) -> None:
        nonlocal count
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        obj.ViewObject.ShapeColor = viewdoc.colour(finish)
        obj.ViewObject.Transparency = transparency
        obj.ViewObject.Visibility = visible
        group.addObject(obj)
        count += 1

    groups = {k: doc.addObject("App::DocumentObjectGroup", k) for k in ("Shell", "Hardware", "KeepOutZones", "Mounts", "Bosses", "Places")}
    for k, f in split.skin_files(d).items():
        shape = Part.Shape()
        shape.importBinary(str(f))
        add("Skin_" + k, shape, SKIN, groups["Shell"], transparency=70)
    for folder, pick in ((out / "hardware", lambda e: "KeepOutZones" if e["role"] == "keepout" else "Shell" if e["role"] == "floor" else "Hardware"),
                         (out / "parts", lambda e: {"boss": "Bosses", "place": "Places"}.get(e["kind"], "Mounts"))):
        for name, entry in json.loads((folder / "manifest.json").read_text(encoding="utf-8")).items():
            shape = Part.Shape()
            shape.read(str(folder / entry["brep"]))
            g = pick(entry)
            add(name, shape, entry["finish"], groups[g], transparency={"KeepOutZones": 80, "Places": 50}.get(g, 0), visible=g != "KeepOutZones")
    doc.recompute()
    doc.saveAs(str(out / viewdoc.DOCUMENT))
    print(f"wrote {out / viewdoc.DOCUMENT}: {count} solids")
    return 0
