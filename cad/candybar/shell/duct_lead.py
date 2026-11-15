"""The scenes of the sheets of the DisplayPort to HDMI adapter and the exhaust duct (docs/design/duct-lead-exit.md):
  way-1     the adapter straight in the board's socket: its body in the duct, the HDMI plug through the end wall
  way-2     a short DisplayPort extension lead, and the adapter in its place on the left dock
  places    the places where a lead can leave the duct's zone: A, B, C (recommended) and the present notch
Each scene has a view from above (cut level above the adapter) and a view in perspective with the duct cut open.
Every face edge is drawn on the renders. Nothing here is a part of the build: the owner chooses from the sheets.

    CANDYBAR_OUT=cad/out/duct-lead cad/candybar/freecad-run.sh candybar.shell.duct_lead
    cad/.venv-tools/bin/python cad/tools/draw_duct_lead.py cad/out/duct-lead

It reads the parts and the hardware of the mounts (cad/out/mounts, built by candybar.shell.mounts) and the skin of the
split from its cache.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import FreeCAD as App
import Part

from . import mounts_scenes as ms, rear
from .dims import Blueprint

V = App.Vector
CAD = Path(__file__).resolve().parents[2]

# the DisplayPort socket of the BC-250 in the datum of the board (docs/research/hardware-envelopes.md, Connectors):
# y' 48.61 to 66.40, top 10.96; its face stands 1.5 beyond the I/O edge; 15.5 deep (ESTIMATED)
DP_SOCKET = (-1.5, 14.0, 48.61, 66.40, 0.0, 10.96)
DP_IN = 9.0                         # how far a DisplayPort plug goes into its socket (ESTIMATED: 8 to 10)
ADAPTER = (52.43, 19.88, 9.84)      # the owner's adapter, measured: length with its plug, width, thickness
HDMI_HEAD = (14.0, 21.0, 12.0)      # a right-angle HDMI plug beyond the adapter's face: length, width, thickness (ESTIMATED)
EXT_HEAD = (25.0, 20.0, 10.0)       # the plug of a DisplayPort extension lead beyond the socket's face (ESTIMATED)
EXT_SOCKET = (30.0, 20.0, 10.0)     # its in-line socket: length, width, thickness (ESTIMATED)
LEAD_D = 6.0                        # a lead (ESTIMATED: 5 to 6)

FIN = {"skin": "#e9e7e1", "board": "#2f6b3a", "io": "#9aa0a6", "duct": "#b9783a", "shroud": "#c9a15a", "dock": "#7d8fa8",
       "adapter": "#1f4e9c", "plug": "#202020", "lead": "#303030", "fan": "#d04040", "place": "#e8c87a",
       "A": "#e08a2a", "B": "#3a78c8", "C": "#2aa84a", "notch": "#909090", "clash": "#d02020"}


def bx(x0, x1, y0, y1, z0, z1) -> Part.Shape:
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def lead(points: list[tuple[float, float, float]], dia: float = LEAD_D) -> Part.Shape:
    """A lead along a polyline: a cylinder on each segment and a ball at each bend."""
    r = dia / 2
    out = []
    for a, b in zip(points, points[1:]):
        va, vb = V(*a), V(*b)
        out.append(Part.makeCylinder(r, (vb - va).Length, va, vb - va))
    out += [Part.makeSphere(r, V(*p)) for p in points[1:-1]]
    return out[0].fuse(out[1:]).removeSplitter() if len(out) > 1 else out[0]


def read(folder: Path) -> dict[str, Part.Shape]:
    out = {}
    for name, e in json.load(open(folder / "manifest.json")).items():
        s = Part.Shape()
        s.read(str(folder / e["brep"]))
        out[name] = s
    return out


def main() -> int:
    root = Path(os.environ.get("CANDYBAR_OUT", "cad/out/duct-lead")).resolve()
    d = Blueprint()
    r, p = rear.Rear(), rear.place(d)
    real = rear.build(d, r, p)
    hw = read(CAD / "out" / "mounts" / "hardware")
    parts = read(CAD / "out" / "mounts" / "parts")
    skin = ms.view_skin(d)
    k = rear.duct_lines(r, p)

    # the numbers of the duct and of the board
    x_io = p.bc_x0
    end_in, end_out = p.x(k["x0"] + r.shell_t), p.x(k["x0"])
    sx0, sx1, sy0, sy1, sz0, sz1 = DP_SOCKET
    zc = p.z((sy0 + sy1) / 2)               # the middle of the socket, in the cabinet
    yc = p.y((sz0 + sz1) / 2)
    face = p.x(sx0)                         # the socket's face
    socket = p.box(*DP_SOCKET)
    board = [hw[n] for n in ("Compute_PCB_IO", "Compute_PCB_Pwr") if n in hw]
    fan_air = hw["PSU_FanAir"]
    fa = fan_air.BoundBox
    # the outline of the top of the clear space over the fan: a frame of bars 2 wide
    z0, z1, b = fa.ZMax - 1.0, fa.ZMax, 2.0
    fan_top = bx(fa.XMin, fa.XMax, fa.YMin, fa.YMin + b, z0, z1).fuse([bx(fa.XMin, fa.XMax, fa.YMax - b, fa.YMax, z0, z1),
                                                                     bx(fa.XMin, fa.XMin + b, fa.YMin, fa.YMax, z0, z1),
                                                                     bx(fa.XMax - b, fa.XMax, fa.YMin, fa.YMax, z0, z1)])
    probe = skin.common(Part.makeLine(V(-260.0, yc, zc), V(-205.0, yc, zc)))
    x_side = max(v.Point.x for v in probe.Vertexes)                             # the inner face of the side wall
    duct = [("duct_body", real["duct_body"], FIN["duct"])]
    common = [("skin", skin.common(bx(-260.0, -60.0, 420.0, 560.0, 85.0, 275.0)), FIN["skin"]),
              *((f"board_{i}", s, FIN["board"] if i == 0 else FIN["io"]) for i, s in enumerate(board)),
              ("dp_socket", socket, FIN["io"]), ("dock_left", parts["DockL"], FIN["dock"]), ("tray_left", parts["TrayL"], FIN["dock"]),
              ("fan_space_top", fan_top, FIN["fan"]), ("shroud_base", real["shroud_base"], FIN["shroud"])]

    # way 1: the adapter straight in the socket, and a right-angle HDMI plug through the end wall
    L, W, T = ADAPTER
    a_in = face + DP_IN
    a_out = a_in - L
    adapter1 = bx(a_out, a_in, yc - T / 2, yc + T / 2, zc - W / 2, zc + W / 2)
    hl, hw_, ht = HDMI_HEAD
    head1 = bx(a_out - hl, a_out, yc - ht / 2, yc + ht / 2, zc - hw_ / 2, zc + hw_ / 2)
    x_lead = a_out - hl + LEAD_D / 2 + 1.0
    lead1 = lead([(x_lead, yc, zc - hw_ / 2), (x_lead, yc, 132.0), (x_lead, 440.0, 132.0)])
    hole1 = bx(end_out - 0.4, end_in + 0.4, yc - ht / 2 - 1.0, yc + ht / 2 + 1.0, zc - hw_ / 2 - 1.0, zc + hw_ / 2 + 1.0)
    way1 = [("adapter", adapter1, FIN["adapter"]), ("hdmi_plug", head1, FIN["plug"]), ("hdmi_lead", lead1, FIN["lead"]),
            ("end_wall_opening", hole1, FIN["B"])]

    # way 2: an extension lead out through place C, and the adapter in its place on the left dock (plug down)
    el, ew, et = EXT_HEAD
    head2 = bx(face - el, face + DP_IN, yc - et / 2, yc + et / 2, zc - ew / 2, zc + ew / 2)
    pd = parts["PlaceDpAdapter"].BoundBox
    adapter2 = bx(pd.XMin + (pd.XLength - W) / 2, pd.XMin + (pd.XLength + W) / 2, pd.YMin + (pd.YLength - T) / 2, pd.YMin + (pd.YLength + T) / 2,
                  pd.ZMin, pd.ZMin + L)
    sl, sw, st = EXT_SOCKET
    ax, ay = (pd.XMin + pd.XMax) / 2, (pd.YMin + pd.YMax) / 2
    socket2 = bx(ax - sw / 2, ax + sw / 2, ay - st / 2, ay + st / 2, pd.ZMin + DP_IN - sl, pd.ZMin + DP_IN)
    z_low = pd.ZMin + DP_IN - sl
    c_x = -187.5
    lead2 = lead([(face - el, yc, zc), (c_x, yc, zc), (c_x, yc, 127.0), (c_x, 458.0, 127.0), (c_x, 458.0, z_low - 8.0),
                  (ax, ay, z_low - 8.0), (ax, ay, z_low)])
    clash = socket2.common(fan_air)
    way2 = [("ext_plug", head2, FIN["plug"]), ("ext_lead", lead2, FIN["lead"]), ("adapter", adapter2, FIN["adapter"]),
            ("ext_socket", socket2, FIN["plug"])]
    if clash.Volume > 1e-6:   # the part of the socket in the clear space over the fan, drawn 0.4 larger so that it shows
        cb = clash.BoundBox
        way2.append(("clash", bx(cb.XMin - 0.4, cb.XMax + 0.4, cb.YMin - 0.4, cb.YMax + 0.4, cb.ZMin, cb.ZMax), FIN["clash"]))

    # the places: the present notch is in duct_body; A, B, C as thin marks on the faces of the duct
    y_floor0, y_floor1 = p.y(-r.shell_t), p.y(0.0)
    z_low0, z_low1 = p.z(k["y0"]), p.z(k["y0"] + r.shell_t)
    marks = {"A": bx(-199.0, -175.0, y_floor0 - 0.6, y_floor1 + 0.6, 125.0, 137.0),
             "B": bx(end_out - 0.6, end_in + 0.6, 470.0, 494.0, 128.0, 140.0),
             "C": bx(-200.0, -175.0, y_floor0 - 0.6, y_floor0 + 12.0, z_low0 - 0.6, z_low0 + 12.0)}
    places = [(f"place_{n}", s, FIN[n]) for n, s in marks.items()]

    # the cameras: from above, cut above the adapter; in perspective, the duct cut open (its back wall off, the
    # upper side wall and the shroud cut away)
    cut_z = zc + W / 2 + 4.0
    keep_plan = (-1000.0, 1000.0, -1000.0, 1000.0, -1000.0, cut_z)
    keep_open = (-1000.0, 1000.0, -1000.0, 1000.0, -1000.0, cut_z + 30.0)
    plan = ms.cam((-190.0, 470.0, cut_z), 70.0, 0.0, 90.0, 0.8)
    persp = ms.cam((-192.0, 470.0, 158.0), 70.0, 150.0, 30.0, 0.8)
    # way 2 is seen from the left: the adapter and its socket stand in front of the duct, beside the dock
    # (from the left, with the side wall left out of that view)
    left = ms.cam((-188.0, 458.0, 140.0), 65.0, -80.0, 12.0, 0.8)
    no_skin = [i for i in common if i[0] != "skin"]
    for name, items, cam, near in (("way-1", common + duct + way1, persp, None), ("way-2", common + duct + way2, left, no_skin + duct + way2),
                                   ("places", common + duct + places, persp, None)):
        ms.scene(root / "scenes" / name / "plan", items, {"plan": plan}, keep=keep_plan)
        ms.scene(root / "scenes" / name / "open", near or items, {"open": cam}, keep=keep_open)

    numbers = {
        "io_edge_x": round(x_io, 2), "socket_face_x": round(face, 2), "socket_middle_z": round(zc, 2), "socket_middle_y": round(yc, 2),
        "end_wall_in_x": round(end_in, 2), "end_wall_out_x": round(end_out, 2), "side_wall_x": round(x_side, 2),
        "room_beside_duct": round(end_out - x_side, 2), "io_to_side_wall": round(x_io - x_side, 2), "io_to_end_wall": round(x_io - end_out, 2),
        "adapter": ADAPTER, "dp_in": DP_IN, "adapter_out_x": round(a_out, 2), "adapter_to_end_wall": round(a_out - end_in, 2),
        "hdmi_head": HDMI_HEAD, "hdmi_head_end_x": round(a_out - hl, 2), "hdmi_room_left": round(a_out - hl - x_side, 2),
        "ext_head": EXT_HEAD, "ext_socket": EXT_SOCKET, "place_dp": [round(v, 2) for v in (pd.XMin, pd.XMax, pd.YMin, pd.YMax, pd.ZMin, pd.ZMax)],
        "ext_socket_low_z": round(z_low, 2), "fan_space_top_z": round(fa.ZMax, 2), "fan_space": [round(v, 2) for v in (fa.XMin, fa.XMax, fa.YMin, fa.YMax, fa.ZMin, fa.ZMax)],
        "socket_in_fan_space_mm3": round(clash.Volume, 1), "places": {n: [round(v, 2) for v in (s.BoundBox.XMin, s.BoundBox.XMax, s.BoundBox.YMin, s.BoundBox.YMax, s.BoundBox.ZMin, s.BoundBox.ZMax)] for n, s in marks.items()},
        "present_notch": list(r.cable_notch), "cut_z": round(cut_z, 2),
    }
    (root / "scene.json").write_text(json.dumps(numbers, indent=1), encoding="utf-8")
    print(json.dumps(numbers, indent=1))
    return 0
