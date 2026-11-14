"""The mounts of the hardware inside the shell (docs/design/hardware-mounts.md).

Run headless. It exits 1 when a check fails:

    CANDYBAR_OUT=cad/out/mounts cad/candybar/freecad-run.sh candybar.shell.mounts

The fit study (fit.py) places the hardware as boxes. This module makes what holds each item, at the anchors of
fit.Layout, and checks it:
  the compute module   a tray in two parts on the four backplate standoffs of the board, a dock on each side wall of
                       the lower body, and a boss for each dock on that wall
  the power supply     a fence on the floor (two rails and a front stop) and the four screws of its rear face
  the hub              two rails on the floor and a saddle that snaps on them
  the cables           tie staples on the floor and on the lower rear wall, and tie slots in the docks
A printed part is loose and is fastened with screws. A boss is a solid that the owner adds to a piece of the shell or
to a floor tile: it is made here as a net solid that stands fit.SEAT off the skin, and a root that goes Mounts.sink
into the skin, so that the two fuse with the piece.

The skin is the one of the split (the cache of split.build_modules). A boolean with the whole skin takes 20 s, so
the skin is cut once into the zones of the mounts (ZONES), which are kept beside the skin in the cache.

It writes into <out>:
  parts/                BREP and STL of each part and boss, manifest.json, edges.json (for tools/face_check.py and
                        tools/render_views.py)
  report.md, report.json   the values, the checks, the loads, the screws and the interfaces
  scenes/               the model directories of the sheets (tools/draw_mounts.py renders them)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

import FreeCAD as App
import MeshPart
import Part

from .. import check, model, params
from . import cavity, fit, split
from . import profiles as pr
from . import solids as so
from . import structure as st
from .dims import Blueprint

V = App.Vector
P3 = tuple[float, float, float]
TOL = check.VOLUME_TOLERANCE
SEAT = fit.SEAT
MESH_LINEAR, MESH_ANGULAR = 0.1, 0.1
# the boxes (x0, x1, y0, y1, z0, z1) of the skin round the mounts
ZONES = {"dock_r": (185.0, 255.0, 405.0, 470.0, 105.0, 195.0), "dock_l": (-255.0, -185.0, 405.0, 470.0, 105.0, 195.0),
         "floor_rear": (-250.0, 250.0, 370.0, 545.0, -5.0, 45.0), "rear_wall": (-75.0, 75.0, 520.0, 545.0, 45.0, 105.0),
         "floor_mid": (-250.0, 250.0, 195.0, 370.0, -5.0, 45.0)}
# a boss keeps this far from a bonded seam and from the flange of a seam
SEAM_CLEAR = 6.0
FINISH = {"compute": "#d98030", "psu": "#3c8f8f", "hub": "#9a6fd0", "ties": "#c8b030", "boss": "#e8e6e0"}
OWNER = "Mount_"
# the pairs that the fit rules report and that the design accepts: a tray has two posts through the air zone behind
# the backplate, because the standoffs of the board are there
DECLARED = (("Compute_UndersideAir", "Mount_TrayL"), ("Compute_UndersideAir", "Mount_TrayR"))


@dataclass(frozen=True)
class Mounts:
    """The values of the mounts. Lengths in mm."""
    # ---- screws: M3 socket head screws and M3 heat-set inserts everywhere; one 2.5 mm hex driver
    m3_clear: float = 3.4
    insert_d: float = 4.0
    insert_l: float = 6.5
    cbore_d: float = 8.0
    cbore_l: float = 8.0
    driver_d: float = 6.0      # the room that the driver needs round the axis of a screw
    sink: float = 1.0          # a boss goes this far into the skin or the floor
    # ---- the compute module
    # the four backplate standoffs of the BC-250, from the I/O edge and from the straight long edge
    # (docs/research/hardware-envelopes.md, section 2)
    standoffs: tuple[tuple[float, float], ...] = ((51.85, 17.68), (82.25, 114.50), (277.45, 37.75), (292.25, 114.25))
    post_d: float = 9.0        # a post through the air zone, from an arm to the backplate
    arm_t: float = 6.0         # an arm, in front of the air zone
    arm_h: float = 14.0
    upright_w: float = 12.0    # an upright, beside the end of the board
    upright_gap: float = 1.5
    channel_clear: float = 1.15  # behind the cable channel, where an upright passes it
    tray_top: float = 9.0      # the top of a tray below the top of the door opening
    board_gap: float = 0.5     # the foot of an upright above the lower edge of the board
    shroud_inset: float = 4.0  # a shroud point inside the end of the fin block, along the upright
    dock_t: float = 6.5
    dock_z0: float = 10.0      # the lower edge of a dock above the door sill
    dock_z1: float = 2.0       # its upper edge below the cable channel
    dock_wall_gap: float = 3.5
    boss_t: float = 14.0
    boss_pad: float = 24.0     # a pad on the wall behind the boss, beside the dock: it spreads the moment in the wall
    boss_pad_t: float = 3.0
    boss_tip_h: float = 21.0
    boss_screw_in: float = 5.35   # the screws of a dock inside the side of the door opening
    boss_edge: float = 7.0        # from those screws to the tip of the boss
    boss_screw_z: tuple[float, float] = (5.5, 15.5)  # below the top of the boss
    hang_z: float = 6.0        # the hanging screw below the top of the dock
    drop: float = 5.0          # the tray goes down this far onto the hanging screws
    web: float = 3.0           # the web of the keyhole
    key_entry: float = 6.5
    key_slot: float = 3.5
    pocket_half: float = 4.0   # the pocket behind the web, above and below the travel of the screw head
    pocket_back: float = 6.0   # what stays behind the pocket
    secure_z: tuple[float, float] = (15.0, 36.0)  # the two screws of the right tray above the lower edge of the dock
    slot_w: float = 3.0        # a pair of tie slots
    slot_h: float = 7.0
    slot_x: tuple[float, float] = (10.0, 22.0)  # outside the upright
    # ---- the power supply
    fence_gap: float = 0.5
    fence_w: float = 5.0
    rail_h: float = 12.0
    rail_ends: tuple[float, float] = (10.0, 10.0)
    stop_t: float = 8.0
    stop_under_plugs: float = 0.5
    stop_ends: tuple[float, float] = (8.0, 4.0)
    # the screw pattern of an ATX rear face, seen from behind with the fan face up: from its lower left corner
    # (docs/research/hardware-envelopes.md, section 6)
    atx_holes: tuple[tuple[float, float], ...] = ((6.0, 80.0), (144.0, 80.0), (6.0, 16.0), (120.0, 6.0))
    atx_hole_d: float = 4.0
    # ---- the hub
    hub_rail_ends: float = 10.0
    hub_rail_h: float = 8.0
    bead: float = 1.5
    bead_h: float = 2.4
    saddle_w: float = 30.0
    leg_t: float = 2.4
    strap_t: float = 2.5
    hub_top_gap: float = 0.5
    snap_play: float = 0.3
    hook_face: float = 2.2
    # ---- the tie staples: a bar on two legs
    tie_span: float = 12.0
    tie_leg: float = 4.0
    tie_depth: float = 6.0
    tie_gap: float = 4.0
    tie_bar: float = 3.0
    bundle_tie_x: float = 45.0      # the straps of the stowed cables, each side of the centre line
    bundle_tie_front: float = 8.0   # in front of the bundle
    bundle_tie_up: float = 14.0     # on the rear wall, above the bundle
    lead_tie_y: float = 36.0        # the leads to the control panel: behind the seam BA2
    lead_tie_x: tuple[float, ...] = (-150.0, -50.0, 50.0, 150.0)
    power_tie: tuple[float, float] = (75.0, 397.0)


@dataclass
class Solid:
    name: str
    group: str            # compute, psu, hub, ties
    kind: str             # printed, boss
    shape: Part.Shape
    on: str               # the piece of the split that carries a boss; what a printed part is fastened to
    up: P3 = (0.0, 0.0, 1.0)   # the direction in the cabinet that points up on the printer
    bed: str = ""         # the face on the bed
    root: Part.Shape | None = None
    note: str = ""

    @property
    def whole(self) -> Part.Shape:
        """A boss with its root."""
        return self.shape if self.root is None else unite([self.shape, self.root])


@dataclass(frozen=True)
class Screw:
    name: str
    size: str
    head: P3              # the seat of the head
    through: str
    into: str
    state: str            # "bench", "module out" or "all in place"
    count: int = 1
    axis: P3 = (0.0, -1.0, 0.0)   # the way the screw goes in


@dataclass
class Site:
    """The anchors of the fit study, and the faces of the skin, that the mounts are built on."""
    a: dict[str, float]
    bx0: float
    bx1: float
    bz0: float
    bz1: float
    y_pcb: float
    y_back: float
    y_air: float
    band: tuple[float, float]
    psu: tuple[float, ...]
    bundle: tuple[float, ...]
    hub: tuple[float, ...]
    plug_z0: float
    floor: float
    door: dict
    wall_x: float         # the inner face of the side of the lower body, behind the band
    rear_y: float         # the inner face of the lower rear wall
    fin: tuple[float, float]


@dataclass
class Design:
    site: Site
    solids: list[Solid]
    screws: list[Screw]
    shroud_points: list[P3]
    psu_holes: list[P3]
    ties: list[dict] = field(default_factory=list)

    def get(self, name: str) -> Solid:
        return next(s for s in self.solids if s.name == name)


# ---------- small solids ----------

def bx(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part.Shape:
    x0, x1, y0, y1, z0, z1 = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl_y(dia: float, x: float, z: float, y0: float, y1: float) -> Part.Shape:
    return Part.makeCylinder(dia / 2, y1 - y0, V(x, y0, z), V(0, 1, 0))


def prism_y(points: list[tuple[float, float]], y0: float, y1: float) -> Part.Shape:
    """A prism along y with the outline `points` in (x, z)."""
    wire = Part.makePolygon([V(x, y0, z) for x, z in points + points[:1]])
    return solid(Part.Face(wire).extrude(V(0, y1 - y0, 0)))


def solid(shape: Part.Shape) -> Part.Shape:
    """One valid solid with its faces merged and its outside out."""
    out = shape.removeSplitter()
    if len(out.Solids) != 1 or not out.isValid():
        raise RuntimeError(f"a mount is not one valid solid: {len(out.Solids)} solids, valid {out.isValid()}")
    out = out.Solids[0]
    if out.Volume < 0:
        out.reverse()
    return out


def unite(shapes: list[Part.Shape]) -> Part.Shape:
    return solid(shapes[0].fuse(shapes[1:])) if len(shapes) > 1 else solid(shapes[0])


def less(shape: Part.Shape, tools: list[Part.Shape]) -> Part.Shape:
    return solid(shape.cut(tools)) if tools else solid(shape)


def framed(shape: Part.Shape, at: P3, b: P3, n: P3) -> Part.Shape:
    """A shape made in (u, v, w) put at `at` with u along b, w along n and v along n x b."""
    bv, nv = V(*b), V(*n)
    cv = nv.cross(bv)
    out = shape.copy()
    out.Placement = App.Placement(App.Matrix(bv.x, cv.x, nv.x, at[0], bv.y, cv.y, nv.y, at[1], bv.z, cv.z, nv.z, at[2], 0, 0, 0, 1))
    return out


# ---------- the skin round the mounts ----------

def zones(d: Blueprint, log=print) -> dict[str, Part.Shape]:
    """The skin of the body inside each box of ZONES, and the floor of the skin ("base"), from the cache of the split."""
    files = split.skin_files(d)
    if not split.skin_cached(d):
        raise RuntimeError(f"mounts: the skin {split.fingerprint(d)} is not in {split.cache_dir()}; run candybar.shell.split first (18 minutes)")
    key, body, out = split.fingerprint(d), None, {}
    for name, (x0, x1, y0, y1, z0, z1) in ZONES.items():
        f = split.cache_dir() / f"mounts-{name}-{key}-{hashlib.sha256(repr(ZONES[name]).encode()).hexdigest()[:8]}.bin"
        out[name] = Part.Shape()
        if f.exists():
            out[name].importBinary(str(f))
            continue
        if body is None:
            log("mounts: cutting the zones of the skin (2 minutes, once)")
            body = Part.Shape()
            body.importBinary(str(files["body"]))
        out[name] = body.common(bx(x0, x1, y0, y1, z0, z1))
        out[name].exportBinary(str(f))
    out["base"] = Part.Shape()
    out["base"].importBinary(str(files["base"]))
    return out


def face_at(skin: Part.Shape, start: P3, direction: P3, reach: float = 120.0) -> float:
    """How far a ray from start goes before it enters the skin."""
    n = V(*direction)
    seg = Part.makeLine(V(*start), V(*start) + n * reach)
    hits = [(v.Point - V(*start)).dot(n) for e in seg.common(skin).Edges for v in e.Vertexes]
    if not hits:
        raise RuntimeError(f"mounts: no skin within {reach:g} of {start} along {direction}")
    return min(hits)


def plane_at(skin: Part.Shape, points: list[P3], direction: P3, what: str) -> float:
    """The distance to a flat face of the skin, measured at each point: the nearest, and an error when the face is
    not flat within the ridge of the cavity."""
    found = [face_at(skin, p, direction) for p in points]
    if max(found) - min(found) > cavity.RIDGE + 1e-6:
        raise RuntimeError(f"mounts: {what} is not flat where a boss goes: {min(found):.3f} to {max(found):.3f}")
    return min(found)


def site(d: Blueprint, lay: fit.Layout, v, skin: dict[str, Part.Shape], m: Mounts) -> Site:
    a = fit.anchors(d, lay, v, d.width / 2 - d.wall_t)
    bx0, bz1 = a["bc_x0"], a["bc_top_z"]
    y_pcb = a["bc_pcb_y"]
    y_back = y_pcb - v("bc_backplate_drop")
    psu_y1 = a["psu_y0"] + v("psu_d_max")
    psu = (a["psu_x0"], a["psu_x0"] + v("psu_w"), psu_y1 - v("psu_d"), psu_y1, a["psu_z0"], a["psu_z0"] + v("psu_h"))
    bundle = (a["bundle_x0"], a["bundle_x0"] + v("psu_bundle_w"), a["bundle_y0"], a["bundle_y0"] + v("psu_bundle_d"), a["psu_z0"], a["psu_z0"] + v("psu_bundle_h"))
    hub = (a["fit_hub_x0"], a["fit_hub_x0"] + v("usb_hub_w"), a["fit_hub_y0"], a["fit_hub_y0"] + v("usb_hub_l"), a["fit_hub_z0"], a["fit_hub_z0"] + v("usb_hub_h"))
    bz0 = bz1 - v("bc_pcb_w_pwr")
    door = fit.door_outline(d)
    zb = (door["z0"] + m.dock_z0 - 4.0, door["z0"] + m.dock_z0 + 50.0)
    wall = min(150.0 + plane_at(skin[z], [(s * 150.0, y, zz) for y in (424.0, 436.0) for zz in zb], (s, 0, 0), "the side of the lower body")
               for z, s in (("dock_r", 1.0), ("dock_l", -1.0)))
    z_tie = bundle[5] + m.bundle_tie_up
    rear = 500.0 + plane_at(skin["rear_wall"], [(x, 500.0, z_tie + dz) for x in (-m.bundle_tie_x, m.bundle_tie_x) for dz in (-8.0, 3.0)],
                            (0, 1, 0), "the lower rear wall")
    half = v("mon_cable_w") / 2
    return Site(a, bx0, bx0 + v("bc_pcb_l"), bz0, bz1, y_pcb, y_back, y_back - v("bc_underside_gap"), (a["fit_ch_z"] - half, a["fit_ch_z"] + half),
                psu, bundle, hub, psu[4] + v("psu_plug_z0"), lay.floor_t, door, wall, rear,
                (bz0 + v("bc_fin_y0"), bz0 + v("bc_fin_y0") + v("bc_fin_w")))


# ---------- the compute module ----------

def tray_frame(s: Site, m: Mounts, side: float) -> dict[str, float]:
    """The lines of a tray and of its dock: side is 1 for the right (the far end of the board), -1 for the left."""
    x0 = s.bx1 + m.upright_gap if side > 0 else s.bx0 - m.upright_gap - m.upright_w
    y0 = s.y_air - m.arm_t
    zd0, zd1 = s.door["z0"] + m.dock_z0, s.band[0] - m.dock_z1
    half = s.door["w"] / 2
    return {"x0": x0, "x1": x0 + m.upright_w, "xc": x0 + m.upright_w / 2, "y0": y0, "yc": s.y_air + m.channel_clear, "y1": s.y_pcb,
            "z0": s.bz0 + m.board_gap, "z1": s.door["z1"] - m.tray_top, "zd0": zd0, "zd1": zd1, "zh": zd1 - m.hang_z,
            "xs": side * (half - m.boss_screw_in), "xtip": side * (half - m.boss_screw_in - m.boss_edge),
            "yd0": y0 - m.dock_t, "yb0": y0 - m.dock_t - m.boss_t}


def tray(s: Site, m: Mounts, side: float) -> Solid:
    """One half of the tray: an upright beside the end of the board, an arm in front of the air zone to each of the
    two standoffs at that end, and a post from the arm to the backplate. The upright has the keyhole for the hanging
    screw, two inserts for the shroud, and on the right the two screws that fasten the module."""
    f = tray_frame(s, m, side)
    x0, x1, xc, y0, y1 = f["x0"], f["x1"], f["xc"], f["y0"], f["y1"]
    body = bx(x0, x1, y0, y1, f["z0"], f["z1"]).cut(bx(x0 - 1, x1 + 1, y0 - 1, f["yc"], s.band[0] - 1, s.band[1] + 1))
    mid = (s.bx0 + s.bx1) / 2
    mine = [(s.bx0 + px, s.bz0 + pz) for px, pz in m.standoffs if (s.bx0 + px > mid) == (side > 0)]
    adds, cuts = [], []
    for px, pz in mine:
        xa = (px - m.arm_h / 2, x0) if side > 0 else (x1, px + m.arm_h / 2)
        adds += [bx(xa[0], xa[1], y0, s.y_air, pz - m.arm_h / 2, pz + m.arm_h / 2), cyl_y(m.post_d, px, pz, s.y_air, s.y_back)]
        cuts.append(cyl_y(m.m3_clear, px, pz, y0 - 1, s.y_back + 1))
    cuts += [cyl_y(m.insert_d, xc, z, y1 - m.insert_l, y1 + 1) for z in shroud_z(s, m)]
    zh = f["zh"]
    cuts += [cyl_y(m.key_entry, xc, zh - m.drop, y0 - 1, y0 + m.web + 0.5), bx(xc - m.key_slot / 2, xc + m.key_slot / 2, y0 - 1, y0 + m.web + 0.5, zh - m.drop, zh),
             cyl_y(m.key_slot, xc, zh, y0 - 1, y0 + m.web + 0.5),
             bx(x0 - 1, x1 + 1, y0 + m.web, y1 - m.pocket_back, zh - m.drop - m.pocket_half, zh + m.pocket_half)]
    if side > 0:
        for dz in m.secure_z:
            cuts += [cyl_y(m.m3_clear, xc, f["zd0"] + dz, y0 - 1, y1 + 1), cyl_y(m.cbore_d, xc, f["zd0"] + dz, y1 - m.cbore_l, y1 + 1)]
    name = "TrayR" if side > 0 else "TrayL"
    return Solid(name, "compute", "printed", less(unite([body] + adds), cuts), "the board (two M3 screws) and the dock " + name[-1],
                 (0.0, 1.0, 0.0), "its front face (the face of the arms, toward the front of the cabinet)",
                 note="the notch for the cable channel is a bridge of 22 mm; the pocket of the keyhole is a bridge of 12 mm")


def shroud_z(s: Site, m: Mounts) -> tuple[float, float]:
    return s.fin[0] + m.shroud_inset, s.fin[1] - m.shroud_inset


def dock(s: Site, m: Mounts, side: float) -> Solid:
    """The plate on a boss of the side wall that a tray seats on: the hanging screw, and on the right the inserts of
    the two screws that fasten the module. It has a pair of tie slots."""
    f = tray_frame(s, m, side)
    inner = f["x0"] if side > 0 else f["x1"]
    plate = bx(inner, side * (s.wall_x - m.dock_wall_gap), f["yd0"], f["y0"], f["zd0"], f["zd1"])
    top = f["zd1"]
    cuts = [cyl_y(m.m3_clear, f["xs"], top - dz, f["yd0"] - 1, f["y0"] + 1) for dz in m.boss_screw_z]
    cuts.append(cyl_y(m.insert_d, f["xc"], f["zh"], f["yd0"] - 1, f["y0"] + 1))
    if side > 0:
        cuts += [cyl_y(m.insert_d, f["xc"], f["zd0"] + dz, f["yd0"] - 1, f["y0"] + 1) for dz in m.secure_z]
    outer = f["x1"] if side > 0 else f["x0"]
    for dx in m.slot_x:
        xs = outer + side * dx
        cuts.append(bx(xs, xs + side * m.slot_w, f["yd0"] - 1, f["y0"] + 1, top - 5.0 - m.slot_h, top - 5.0))
    name = "DockR" if side > 0 else "DockL"
    return Solid(name, "compute", "printed", less(plate, cuts), "the boss " + name[-1] + " (two M3 screws)", (0.0, 1.0, 0.0),
                 "its front face (toward the boss)")


def boss(s: Site, m: Mounts, side: float) -> Solid:
    """The boss of a dock on the side wall of the lower body: a bracket with a 45 degree underside, so that the piece
    prints upright with no support. Two inserts in its rear face."""
    f = tray_frame(s, m, side)
    net = side * (s.wall_x - SEAT)
    zt = f["zd1"]
    zb = zt - m.boss_tip_h
    run = abs(net - f["xtip"])
    low, pad = zb - run, net - side * m.boss_pad_t
    y2 = f["yd0"] + m.boss_pad
    wedge = prism_y([(net, zt), (f["xtip"], zt), (f["xtip"], zb), (net, low)], f["yb0"], f["yd0"])
    shape = less(unite([wedge, prism_y([(net, zt), (pad, zt), (pad, low + m.boss_pad_t), (net, low)], f["yd0"], y2)]),
                 [cyl_y(m.insert_d, f["xs"], zt - dz, f["yd0"] - m.insert_l, f["yd0"] + 1) for dz in m.boss_screw_z])
    root = bx(net, side * (s.wall_x + m.sink), f["yb0"], y2, low, zt)
    name = "BossR" if side > 0 else "BossL"
    return Solid(name, "compute", "boss", shape, "middle R" if side > 0 else "middle L", root=root,
                 bed="it prints with its piece, which stands upright", note="the underside is 45 degrees")


def compute(s: Site, m: Mounts) -> tuple[list[Solid], list[Screw], list[P3]]:
    out = [fn(s, m, side) for side in (-1.0, 1.0) for fn in (tray, dock, boss)]
    screws = []
    y0 = s.y_air - m.arm_t
    for side, tag in ((-1.0, "L"), (1.0, "R")):
        f = tray_frame(s, m, side)
        for px, pz in m.standoffs:
            if (s.bx0 + px > (s.bx0 + s.bx1) / 2) == (side > 0):
                screws.append(Screw(f"board to tray {tag}, standoff at ({px:g}, {pz:g})", "M3 x 20", (s.bx0 + px, y0, s.bz0 + pz), "Tray" + tag,
                                    "the standoff of the board", "bench", axis=(0.0, 1.0, 0.0)))
        for dz in m.boss_screw_z:
            screws.append(Screw(f"dock {tag} to its boss, z {f['zd1'] - dz:g}", "M3 x 12", (f["xs"], f["y0"], f["zd1"] - dz), "Dock" + tag, "Boss" + tag, "module out"))
        screws.append(Screw(f"hanging screw {tag}", "M3 x 10, head 3.3 proud", (f["xc"], f["y0"] + m.web + 0.3, f["zh"]), "Tray" + tag, "Dock" + tag, "bench"))
        if side > 0:
            for dz in m.secure_z:
                screws.append(Screw(f"module to dock R, z {f['zd0'] + dz:g}", "M3 x 18", (f["xc"], s.y_pcb - m.cbore_l, f["zd0"] + dz), "TrayR", "DockR", "all in place"))
    points = [(tray_frame(s, m, side)["xc"], s.y_pcb, z) for side in (-1.0, 1.0) for z in shroud_z(s, m)]
    return out, screws, points


# ---------- the power supply ----------

def psu(s: Site, m: Mounts, x_bay: float) -> tuple[list[Solid], list[P3]]:
    """The fence on the floor: a rail along each side and a stop in front, below the plug zone. The stop has a gap
    at the seam of the floor tiles. Each is a boss of a floor tile."""
    x0, x1, y0, y1, z0, _ = s.psu
    g, w = m.fence_gap, m.fence_w
    ry = (y0 + m.rail_ends[0], y1 - m.rail_ends[1])
    sy = (y0 - g - m.stop_t, y0 - g)
    sz = s.plug_z0 - m.stop_under_plugs
    boxes = {"PsuRailL": ((x0 - g - w, x0 - g, *ry, z0, z0 + m.rail_h), "floor rear side L"),
             "PsuRailR": ((x1 + g, x1 + g + w, *ry, z0, z0 + m.rail_h), "floor rear centre"),
             "PsuStopL": ((x0 + m.stop_ends[0], -x_bay - SEAM_CLEAR - 2.0, *sy, z0, sz), "floor rear side L"),
             "PsuStopR": ((-x_bay + SEAM_CLEAR + 2.0, x1 - m.stop_ends[1], *sy, z0, sz), "floor rear centre")}
    out = [Solid(k, "psu", "boss", bx(*b), on, root=bx(b[0], b[1], b[2], b[3], z0 - m.sink, z0), bed="it prints with its floor tile, which lies flat")
           for k, (b, on) in boxes.items()]
    holes = [(x1 - hx, y1, z0 + hz) for hx, hz in m.atx_holes]
    return out, holes


# ---------- the hub ----------

def hub(s: Site, m: Mounts) -> list[Solid]:
    """Two rails on the floor beside the hub, each with a bead on its outer face, and a saddle over the hub whose
    legs snap under the beads."""
    x0, x1, y0, y1, _, z1 = s.hub
    z0 = s.floor
    xi, xo = x0 - m.fence_gap - m.fence_w, x1 + m.fence_gap + m.fence_w   # the outer faces of the two rails
    top = z0 + m.hub_rail_h
    ry = (y0 + m.hub_rail_ends, y1 - m.hub_rail_ends)
    out = []
    for name, face, sgn in (("HubRailIn", xi, -1.0), ("HubRailOut", xo, 1.0)):
        back = face - sgn * m.fence_w
        pts = [(back, z0), (back, top), (face, top), (face + sgn * m.bead, top - m.bead_h), (face, top - 2 * m.bead_h), (face, z0)]
        out.append(Solid(name, "hub", "boss", prism_y(pts, *ry), "floor middle side R", root=bx(back, face, *ry, z0 - m.sink, z0),
                         bed="it prints with its floor tile, which lies flat", note="the bead overhangs 37 degrees"))
    # the saddle: one outline in (x, z)
    li, lo = xi - m.bead - m.snap_play, xo + m.bead + m.snap_play     # the inner faces of the legs
    tip = m.bead - m.snap_play                                        # how far a hook goes in from its leg
    hz1 = top - m.bead_h                                              # the top of a hook, under the tip of the bead
    hz0 = hz1 - 2 * m.bead_h * tip / m.bead / 2
    zs0, zs1 = z1 + m.hub_top_gap, z1 + m.hub_top_gap + m.strap_t
    zl = hz0 - m.hook_face                                            # the foot of a leg: the hook is its foot

    def leg(inner: float, sgn: float) -> list[tuple[float, float]]:
        """The inner side of a leg from its foot up to the strap; sgn is the way out from the hub."""
        t = inner - sgn * tip
        return [(t, zl), (t, hz0), (inner, hz1), (inner, zs0)]

    left, right = leg(li, -1.0), leg(lo, 1.0)
    pts = [(lo + m.leg_t, zl), (lo + m.leg_t, zs1), (li - m.leg_t, zs1), (li - m.leg_t, zl)] + left + right[::-1]
    ym = (y0 + y1) / 2
    out.append(Solid("HubSaddle", "hub", "printed", prism_y(pts, ym - m.saddle_w / 2, ym + m.saddle_w / 2), "the two rails of the hub (snap fit, no screw)",
                     (0.0, 1.0, 0.0), "one of its two flat sides, so that the legs bend in the plane of the layers"))
    return out


# ---------- the tie staples ----------

def staple(m: Mounts, at: P3, n: P3, b: P3, wall: bool) -> tuple[Part.Shape, Part.Shape]:
    """A bar on two legs, for a cable tie or a strap: at is the middle of its foot on the surface, n the normal of
    the surface, b the direction of the bar. On a wall, n x b points up and each leg has a 45 degree gusset below it,
    so that it prints with the wall. It returns the staple and its root in the surface."""
    h, r = m.tie_span / 2, m.tie_span / 2 + m.tie_leg
    top = m.tie_gap + m.tie_bar
    d0 = m.tie_depth / 2
    outline = [V(-r, -d0, 0), V(-h, -d0, 0), V(-h, -d0, m.tie_gap), V(h, -d0, m.tie_gap), V(h, -d0, 0), V(r, -d0, 0), V(r, -d0, top), V(-r, -d0, top)]
    parts = [Part.Face(Part.makePolygon(outline + outline[:1])).extrude(V(0, m.tie_depth, 0))]
    low = -d0 - top if wall else -d0
    if wall:
        for u in (-r, h):
            tri = [V(u, -d0, 0), V(u, -d0, top), V(u, low, 0)]
            parts.append(Part.Face(Part.makePolygon(tri + tri[:1])).extrude(V(m.tie_leg, 0, 0)))
    roots = [Part.makeBox(m.tie_leg, d0 - low, m.sink + SEAT, V(u, low, -m.sink - SEAT)) for u in (-r, h)]
    return framed(unite(parts), at, b, n), framed(Part.makeCompound(roots), at, b, n)


def ties(s: Site, m: Mounts, x_bay: float) -> tuple[list[Solid], list[dict]]:
    spots = []
    yb = s.bundle[2] - m.bundle_tie_front
    zb = s.bundle[5] + m.bundle_tie_up
    for x, tag in ((-m.bundle_tie_x, "L"), (m.bundle_tie_x, "R")):
        spots.append((f"TieBundleFront{tag}", (x, yb, s.floor), (0, 0, 1), (1, 0, 0), False, "floor rear centre", "the strap of the stowed cables"))
        spots.append((f"TieBundleRear{tag}", (x, s.rear_y - SEAT, zb), (0, -1, 0), (1, 0, 0), True, "rear lower " + tag, "the strap of the stowed cables"))
    for i, x in enumerate(m.lead_tie_x):
        on = "floor middle centre" if abs(x) < x_bay else "floor middle side " + ("R" if x > 0 else "L")
        spots.append((f"TieLead{i + 1}", (x, 194.0 + m.lead_tie_y, s.floor), (0, 0, 1), (1, 0, 0), False, on, "the leads from the control panel to the hub"))
    spots.append(("TiePower", (*m.power_tie, s.floor), (0, 0, 1), (1, 0, 0), False, "floor rear centre", "the 12 V lead to the BC-250 and the 5 V lead to the hub"))
    out, rows = [], []
    for name, at, n, b, wall, on, use in spots:
        shape, root = staple(m, at, n, b, wall)
        out.append(Solid(name, "ties", "boss", shape, on, root=root, bed="it prints with its piece" + (", which stands upright" if wall else ", which lies flat"),
                         note="the bar is a bridge of 12 mm"))
        rows.append({"name": name, "at": [round(c, 2) for c in at], "on": on, "for": use})
    for side, tag, use in ((-1.0, "L", "the video lead from the I/O end to the monitor (left channel)"),
                           (1.0, "R", "the power lead of the monitor (right channel), the 12 V lead, the leads from the hood")):
        f = tray_frame(s, m, side)
        outer = f["x1"] if side > 0 else f["x0"]
        rows.append({"name": f"tie slots of the dock {tag}", "at": [round(outer + side * (sum(m.slot_x) + m.slot_w) / 2, 2), f["y0"], round(f["zd1"] - 5.0 - m.slot_h / 2, 2)],
                     "on": "Dock" + tag, "for": use})
    return out, rows


def build(d: Blueprint, lay: fit.Layout, m: Mounts, v, skin: dict[str, Part.Shape]) -> Design:
    s = site(d, lay, v, skin, m)
    x_bay = split.lines(d).x_bay
    solids, screws, points = compute(s, m)
    fence, holes = psu(s, m, x_bay)
    staples, rows = ties(s, m, x_bay)
    return Design(s, solids + fence + hub(s, m) + staples, screws, points, holes, rows)


# ---------- the checks ----------

def in_skin(design: Design, skin: dict[str, Part.Shape]) -> list[dict]:
    """Each solid against the skin: a printed part and the net solid of a boss have no volume in the skin; the root
    of a boss lies in the skin or in the floor."""
    rows = []
    floor = bx(-300.0, 300.0, 0.0, 600.0, design.site.floor - 50.0, design.site.floor)
    for s in design.solids:
        near = [z for z in skin.values() if z.BoundBox.intersect(s.shape.BoundBox)]
        vol = sum(s.shape.common(z).Volume for z in near)
        row = {"solid": s.name, "kind": s.kind, "in_skin_mm3": round(vol, 3), "ok": vol <= TOL}
        if s.root is not None:
            held = sum(s.root.common(z).Volume for z in skin.values() if z.BoundBox.intersect(s.root.BoundBox)) + (
                s.root.common(floor).Volume if s.on.startswith("floor") else 0.0)
            row["root_held_mm3"] = round(held, 1)
            row["ok"] = row["ok"] and held > 0.5 * s.root.Volume
        rows.append(row)
    return rows


def own_pairs(design: Design) -> list[tuple[str, str, float]]:
    """The pairs of the mounts' own solids that have a common volume."""
    out = []
    for i, a in enumerate(design.solids):
        for b in design.solids[i + 1:]:
            if a.shape.BoundBox.intersect(b.shape.BoundBox) and (vol := a.shape.common(b.shape).Volume) > TOL:
                out.append((a.name, b.name, vol))
    return out


def stand_in(parts: dict[str, Part.Shape], skin: dict[str, Part.Shape], d: Blueprint) -> cavity.Cavity:
    """A cavity for the rules of the fit study, without the 6 minutes of cavity.build: its walls are the zones of
    the real skin round the mounts and the floor of the skin, and a point is in the cavity when it is in the outer
    form. So an item is tested against the skin near the mounts only; the fit study tests it against all the skin."""
    return cavity.Cavity([parts[k] for k in cavity.SKIN] + [cavity.seam_filler(parts, d)], list(skin.values()), [])


def room_values(d: Blueprint, lay: fit.Layout, v, shell_out: Path) -> dict[str, float]:
    """The values that the fit study measures on the whole cavity (the room of the speakers and the marquee, and the
    inner face of the deck side at the USB row), from the report of the fit study of the default build."""
    report = shell_out / fit.FIT / "report.json"
    if not report.exists():
        raise RuntimeError(f"mounts: {report} is not there; run candybar.shell.fit first")
    anchors = json.loads(report.read_text(encoding="utf-8"))["anchors"]
    return {k: x for k, x in anchors.items() if k.startswith(("fit_spk_", "fit_mq_")) or k == "fit_usb_x"}


def fit_rules(d: Blueprint, lay: fit.Layout, params_dir: Path, parts: dict[str, Part.Shape], cav: cavity.Cavity, room: dict[str, float],
              design: Design | None) -> dict[str, list[tuple[str, str, str]]]:
    """The rules of the fit study (R1, R2, R5, containment, the air zones, the door service) on the hardware, with
    the solids of the mounts added as hardware when a design is given. Each solid of a mount is its own owner, so
    that R1 compares it with every other solid."""
    base = fit.sheet(params.load(params_dir), "MountsFitBase")
    try:
        values = fit.anchors(d, lay, lambda name: params.value(base, name), room["fit_usb_x"] + SEAT) | room
        doc = fit.build_items(fit.sheet_rows(params_dir, values))
    finally:
        App.closeDocument(base.Name)
    try:
        for s in design.solids if design else ():
            obj = doc.addObject("Part::Feature", OWNER + s.name)
            obj.Shape = s.shape
            model.tag(obj, "hardware", OWNER + s.name)
        doc.recompute()
        found = fit.items(doc)
        rules = fit.run_checks(doc, found, cav, parts["bezel"], parts["control_panel"])
        rules["door service"] = fit.door_service(found, fit.door_outline(d), d, lay)
        return rules
    finally:
        App.closeDocument(doc.Name)


def hardware_shapes(d: Blueprint, lay: fit.Layout, params_dir: Path, room: dict[str, float]) -> dict[str, tuple[str, str, Part.Shape]]:
    """Each solid of the hardware of the fit study: its owner, its role and its shape in the cabinet."""
    base = fit.sheet(params.load(params_dir), "MountsHwBase")
    try:
        values = fit.anchors(d, lay, lambda name: params.value(base, name), room["fit_usb_x"] + SEAT) | room
        doc = fit.build_items(fit.sheet_rows(params_dir, values))
    finally:
        App.closeDocument(base.Name)
    try:
        return {p.name: (p.owner, p.role, p.world.copy()) for p in model.placed(doc) if p.role in fit.ENVELOPE}
    finally:
        App.closeDocument(doc.Name)


def split_findings(rules: dict[str, list[tuple[str, str, str]]]) -> tuple[list[str], list[str]]:
    """The failures of the rules: those that the design declares (DECLARED), and the others."""
    declared, other = [], []
    for title, rows in rules.items():
        for level, subject, detail in rows:
            if level != check.FAIL:
                continue
            names = {n.strip() for n in subject.split("/")}
            text = f"{title}: {subject}: {detail}"
            (declared if any(names == set(pair) for pair in DECLARED) else other).append(text)
    return declared, other


# the solids of the compute module that are there when a person drives a screw or takes the module out
MODULE = ("Compute_PCB_IO", "Compute_PCB_Pwr", "Compute_Backplate", "Compute_Heatsink", "Compute_IO", "Compute_FanShroud", "Compute_ExhaustDuct")
FLOOR_ITEMS = ("PSU_Body", "CableBundle_Body", "Hub_Body")


def access(design: Design, m: Mounts, hw: dict[str, tuple[str, str, Part.Shape]], d: Blueprint) -> list[dict]:
    """Each screw that is driven in the cabinet: the driver, a cylinder of driver_d on the axis of the screw from its
    head to behind the cabinet, must pass through the door opening and meet no solid. The module's own solids are in
    the way only for a screw that is driven with all in place."""
    door = design.site.door
    rows = []
    for sc in design.screws:
        row = {"screw": sc.name, "size": sc.size, "count": sc.count, "state": sc.state, "head": [round(c, 2) for c in sc.head]}
        if sc.state == "bench":
            rows.append(row | {"ok": True, "how": "on the bench, before the part goes into the cabinet"})
            continue
        x, y, z = sc.head
        r = m.driver_d / 2
        tool = cyl_y(m.driver_d, x, z, y, d.body_d + 60.0)
        margin = min(x - r - door["x0"], door["x1"] - x - r, z - r - door["z0"], door["z1"] - z - r)
        there = [s for s in design.solids if s.name not in (sc.through, sc.into) and (sc.state == "all in place" or not s.name.startswith("Tray"))]
        names = FLOOR_ITEMS + (MODULE if sc.state == "all in place" else ())
        hit = [s.name for s in there if s.shape.BoundBox.intersect(tool.BoundBox) and s.shape.common(tool).Volume > TOL]
        hit += [k for k in names if hw[k][2].BoundBox.intersect(tool.BoundBox) and hw[k][2].common(tool).Volume > TOL]
        rows.append(row | {"door_margin": round(margin, 2), "in_the_way": hit, "ok": margin >= 0 and not hit,
                           "how": f"through the rear door opening, {d.body_d - y:.0f} mm inside it"})
    return rows


def swept(shape: Part.Shape, y1: float) -> Part.Shape:
    """The box that a solid sweeps when it goes straight back to y1."""
    b = shape.BoundBox
    return bx(b.XMin, b.XMax, b.YMin, max(b.YMax, y1), b.ZMin, b.ZMax)


def module_path(design: Design, m: Mounts, hw: dict[str, tuple[str, str, Part.Shape]], d: Blueprint) -> dict:
    """The compute module on its way out: up by the drop of the keyholes, then straight back through the door
    opening. Each of its solids, as the box it sweeps, must pass the opening and meet nothing that stays."""
    door = design.site.door
    moving = [design.get("TrayL").shape, design.get("TrayR").shape] + [hw[k][2] for k in MODULE]
    stays = [s for s in design.solids if not s.name.startswith("Tray")]
    fixed = [(s.name, s.shape) for s in stays] + [(k, hw[k][2]) for k in FLOOR_ITEMS]
    hits, lo, hi = [], [math.inf] * 2, [-math.inf] * 2
    for shape in moving:
        b = shape.BoundBox
        lifted = bx(b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax + m.drop)
        path = swept(lifted.translated(V(0, 0, 0)), d.body_d + 20.0)
        path = bx(path.BoundBox.XMin, path.BoundBox.XMax, path.BoundBox.YMin, path.BoundBox.YMax, b.ZMin + m.drop, b.ZMax + m.drop)
        for vol in (lifted, path):
            hits += [name for name, f in fixed if f.BoundBox.intersect(vol.BoundBox) and f.common(vol).Volume > TOL]
        lo = [min(lo[0], b.XMin), min(lo[1], b.ZMin + m.drop)]
        hi = [max(hi[0], b.XMax), max(hi[1], b.ZMax + m.drop)]
    margins = {"left": lo[0] - door["x0"], "right": door["x1"] - hi[0], "sill": lo[1] - door["z0"], "top": door["z1"] - hi[1]}
    return {"steps": ["Unplug the leads of the board (power, video, USB, fan).", "Remove the 2 screws of the right tray (M3, 2.5 mm hex driver).",
                      f"Lift the module {m.drop:g} mm, off the two hanging screws.", "Pull it straight back through the door opening."],
            "box_x": [round(lo[0], 2), round(hi[0], 2)], "box_z": [round(lo[1], 2), round(hi[1], 2)],
            "margins": {k: round(x, 2) for k, x in margins.items()}, "in_the_way": sorted(set(hits)),
            "ok": min(margins.values()) >= 0 and not hits}


def psu_path(design: Design, m: Mounts, hw: dict[str, tuple[str, str, Part.Shape]], d: Blueprint) -> dict:
    """The power supply on its way out, with the compute module and the stowed cables out: up over the fence, forward
    off the rear wall, to the right past the left dock, up to the door opening, and back through it."""
    s = design.site
    door = s.door
    x0, x1, y0, y1, z0, z1 = s.psu
    lift = m.rail_h + 1.0
    f = tray_frame(s, m, -1.0)
    right = f["x1"] + 1.0 - x0                       # its left face past the inner edge of the left dock
    up = door["z0"] + 2.0 - z0
    moves = [("up", (0.0, 0.0, lift)), ("forward", (0.0, -20.0, 0.0)), ("right", (right, 0.0, 0.0)), ("up", (0.0, 0.0, up - lift)),
             ("back", (0.0, d.body_d + 20.0 - y1 + 20.0, 0.0))]
    fixed = [(q.name, q.shape) for q in design.solids if not q.name.startswith("Tray")] + [("Hub_Body", hw["Hub_Body"][2])]
    at, hits, steps = [x0, y0, z0], [], []
    for word, (dx, dy, dz) in moves:
        to = [at[0] + dx, at[1] + dy, at[2] + dz]
        vol = bx(min(at[0], to[0]), max(at[0], to[0]) + x1 - x0, min(at[1], to[1]), max(at[1], to[1]) + y1 - y0, min(at[2], to[2]), max(at[2], to[2]) + z1 - z0)
        hits += [name for name, shape in fixed if shape.BoundBox.intersect(vol.BoundBox) and shape.common(vol).Volume > TOL]
        steps.append(f"{word} {abs(dx + dy + dz):.1f}")
        at = to
    margins = {"left": at[0] - door["x0"], "right": door["x1"] - (at[0] + x1 - x0), "sill": at[2] - door["z0"], "top": door["z1"] - (at[2] + z1 - z0),
               "under the upper edge of nothing": 0.0}
    margins.pop("under the upper edge of nothing")
    return {"steps": steps, "margins": {k: round(x, 2) for k, x in margins.items()}, "in_the_way": sorted(set(hits)),
            "ok": min(margins.values()) >= 0 and not hits}


def seams(design: Design, d: Blueprint) -> list[dict]:
    """Each boss against the seams and the seam flanges of the piece that carries it: its distance to the nearest,
    which must be SEAM_CLEAR or more."""
    L = split.lines(d)
    rows = []
    for s in design.solids:
        if s.kind != "boss":
            continue
        b = s.whole.BoundBox
        if s.on.startswith("floor"):
            near = {"BA1 (x = -106)": abs(b.XMin + L.x_bay) if b.XMax < -L.x_bay else abs(b.XMax + L.x_bay) if b.XMin > -L.x_bay else 0.0,
                    "BA1 (x = 106)": abs(b.XMin - L.x_bay) if b.XMin > L.x_bay else abs(L.x_bay - b.XMax) if b.XMax < L.x_bay else 0.0,
                    "BA2 (y = 194)": b.YMin - 194.0 if b.YMin > 194.0 else 194.0 - b.YMax if b.YMax < 194.0 else 0.0,
                    "BA3 (y = 357)": b.YMin - 357.0 if b.YMin > 357.0 else 357.0 - b.YMax if b.YMax < 357.0 else 0.0}
        elif s.on.startswith("middle"):
            crease = max(pr.crease_y(d, z) for z in (b.ZMin, b.ZMax))
            near = {"L1 with its flange (z = 120)": b.ZMin - (L.z_sill + 4.0), "B1 with its flange (z = 285)": L.z_belt - 8.0 - b.ZMax,
                    "S1, the crease of the band": b.YMin - crease, "the cut-in (y = 510)": d.cut_in_y - b.YMax}
        else:  # rear lower
            near = {"R2 (x = 0)": min(abs(b.XMin), abs(b.XMax)), "L1 and DR with their flange (z = 108)": L.z_sill - 8.0 - b.ZMax,
                    "the base seam at the floor": b.ZMin - design.site.floor}
        name, dist = min(near.items(), key=lambda kv: kv[1])
        rows.append({"boss": s.name, "on": s.on, "nearest": name, "distance": round(dist, 2), "ok": dist >= SEAM_CLEAR})
    return rows


def print_rows(design: Design, lim: split.Printer) -> list[dict]:
    """The print box of each printed part in its print direction."""
    rows = []
    for s in design.solids:
        if s.kind != "printed":
            continue
        pts = [(p.x, p.y, p.z) for e in s.shape.Edges for p in e.discretize(Number=6)]
        box = split.print_box(pts, s.up, lim)
        rows.append({"part": s.name, "x": box["x"], "y": box["y"], "z": box["z"], "fits": box["fits"], "bed": s.bed, "note": s.note,
                     "grams": round(s.shape.Volume * 1.27e-3, 1)})
    return rows


def loads(design: Design, m: Mounts, v) -> list[dict]:
    """Hand estimates. The design load of a mount is its weight times LIFT_FACTOR in the worst direction: the cabinet
    is tilted on its front edge and put down again. A stress is compared with the limit for a short load on PETG
    (structure.YIELD_MPA); the stress under the weight alone is compared with the creep limit."""
    s = design.site
    g = st.G
    mass = {k: kg for k, kg, *_ in ((h[0], h[1]) for h in st.HARDWARE)}
    kg = lambda word: next(x for k, x in mass.items() if word in k)
    rows = []

    def row(mount: str, what: str, force: float, path: str, how: str, stress: float, sustained: float) -> None:
        rows.append({"mount": mount, "what": what, "force_N": round(force, 1), "path": path, "estimate": how, "stress_MPa": round(stress, 2),
                     "sustained_MPa": round(sustained, 2), "ok": stress <= st.YIELD_MPA and sustained <= st.CREEP_MPA})

    trays = sum(design.get(k).shape.Volume for k in ("TrayL", "TrayR")) * 1.27e-6
    module = kg("BC-250") + kg("ARCTIC") + kg("shroud") + trays
    w = module * g
    f = LIFT_FACTOR * w
    fr = tray_frame(s, m, 1.0)
    fl = tray_frame(s, m, -1.0)
    com_x = s.bx0 + v("bc_fin_x0") + v("bc_fin_l") / 2
    share = (com_x - fl["xc"]) / (fr["xc"] - fl["xc"])
    arm = s.wall_x - abs(fr["xs"])
    moment = share * f * arm
    tall = m.boss_tip_h + s.wall_x - SEAT - abs(fr["xtip"])
    wide = m.boss_t + m.boss_pad
    row("compute module", "the wall at the right boss, load along the cabinet (tilted)", share * f, "boss R, then the side of the lower body in the piece middle R",
        f"moment {moment:.0f} N mm about an upright line; it enters the wall along the root height {tall:.0f}: 6 M / (height x t2), wall t = 4",
        6 * moment / (tall * 4.0 ** 2), 0.0)
    row("compute module", "the wall at the right boss, load down (upright)", share * f, "boss R, then the side of the lower body in the piece middle R",
        f"the same moment about a level line; it enters the wall along the root with its pad, {wide:g} wide: 6 M / (width x t2)", 6 * moment / (wide * 4.0 ** 2),
        6 * moment / LIFT_FACTOR / (wide * 4.0 ** 2))
    far = max(abs(s.bx0 + px - (fl["x1"] if s.bx0 + px < (s.bx0 + s.bx1) / 2 else fr["x0"])) for px, _ in m.standoffs)
    per = f / len(m.standoffs)
    z_weak = m.arm_h * m.arm_t ** 2 / 6
    row("compute module", f"the longest arm of a tray ({far:.0f} mm), load along the cabinet", per, "arm, upright, hanging screw, dock, boss",
        f"{per:.1f} N at {far:.0f}: M / Z, Z = {m.arm_h:g} x {m.arm_t:g}2 / 6", per * far / z_weak, per * far / LIFT_FACTOR / z_weak)
    bear = m.web * 3.0
    row("compute module", "the web of a keyhole on the shank of the hanging screw", f / 2, "tray, hanging screw (M3 steel), insert in the dock",
        f"bearing on {m.web:g} x 3", f / 2 / bear, w / 2 / bear)
    pull = INSERT_PULL
    row("compute module", "the inserts of a dock in its boss (2 x M3)", share * f, "dock, two inserts, boss",
        f"against {pull:g} N for one M3 heat-set insert in PETG (ESTIMATED); shown as a share of 50", share * f / (2 * pull) * st.YIELD_MPA, share * w / (2 * pull) * st.CREEP_MPA)
    wp = kg("power supply") * g
    x0, x1, y0, y1, z0, _ = s.psu
    row("power supply", "the floor under it (upright)", wp, "floor tiles rear side L and rear centre, then the table", f"{wp:.0f} N on {x1 - x0:g} x {y1 - y0:g}",
        wp / ((x1 - x0) * (y1 - y0)), wp / ((x1 - x0) * (y1 - y0)))
    stop = sum(design.get(k).shape.BoundBox.XLength for k in ("PsuStopL", "PsuStopR"))
    sh = s.plug_z0 - m.stop_under_plugs - z0
    fs = LIFT_FACTOR * wp * math.sin(math.radians(TILT_DEG))
    row("power supply", f"the front stop, cabinet tilted {TILT_DEG:g} degrees on its front edge", fs, "stop, then the floor tiles (the stop is part of them)",
        f"{fs:.0f} N at half the height {sh:g}: bending of a root {stop:.0f} x {m.stop_t:g}", 6 * fs * sh / 2 / (stop * m.stop_t ** 2), 0.0)
    rim = 4 * m.atx_hole_d * 4.0
    row("power supply", f"a pull of {LEAD_PULL:g} N on the mains lead", LEAD_PULL, "the 4 screws of the rear face (6-32), then the lower rear wall in the piece rear lower L",
        f"bearing of 4 screws in a wall of 4: {LEAD_PULL:g} / (4 x {m.atx_hole_d:g} x 4)", LEAD_PULL / rim, 0.0)
    strain = 1.5 * m.leg_t * (m.bead - m.snap_play) / (s.hub[5] + m.hub_top_gap - (s.floor + m.hub_rail_h - m.bead_h)) ** 2
    row("hub", "a leg of the saddle when it snaps over the bead", kg("USB hub") * g, "saddle, rails, floor tile middle side R",
        f"strain 1.5 t y / L2 = {100 * strain:.1f} %, times E", strain * st.E_PETG, 0.0)
    ws = LIFT_FACTOR * kg("cables") * g
    span = m.tie_span
    row("ties", "the bar of a staple, the strap of the stowed cables", ws / 2, "staple, then the floor tile rear centre or the lower rear wall",
        f"{ws / 2:.1f} N at the middle of a span of {span:g}: (F L / 4) / (b h2 / 6)", (ws / 2 * span / 4) / (m.tie_depth * m.tie_bar ** 2 / 6), 0.0)
    return rows


LIFT_FACTOR = 2.0     # as structure.hand_holds: a lift is a short load with a jolt
TILT_DEG = 45.0       # ESTIMATED: how far the cabinet is tilted on its front edge when a person lifts its back
LEAD_PULL = 50.0      # ESTIMATED: a person who trips on the mains lead
INSERT_PULL = 300.0   # ESTIMATED: pull-out of one M3 heat-set insert in PETG


def face_findings(design: Design) -> list[str]:
    """The findings of tools/face_check.py on each part and boss."""
    from tools import face_check  # noqa: PLC0415 - a tool, not a part of the generator

    out = []
    for s in design.solids:
        out += [f"{s.name}: {f.rule} at {f.at}: {f.detail}" for f in face_check.failures(face_check.check(s.shape, s.name))]
    return out


# ---------- the run ----------

def shell_parts(d: Blueprint, shell_out: Path, log=print) -> dict[str, Part.Shape]:
    """The parts of the default build: its BREP files when they are there (solids.main writes them), else a build."""
    manifest = shell_out / "manifest.json"
    if not manifest.exists():
        return so.build(d)
    log(f"mounts: the shell from {shell_out}")
    out = {}
    for name, entry in json.loads(manifest.read_text(encoding="utf-8")).items():
        out[name] = Part.Shape()
        out[name].read(str(shell_out / entry["brep"]))
    return out


@dataclass
class Run:
    design: Design
    report: dict
    hw: dict[str, tuple[str, str, Part.Shape]]
    skin: dict[str, Part.Shape]

    @property
    def failures(self) -> list[str]:
        return self.report["failures"]


def run(d: Blueprint, lay: fit.Layout, m: Mounts, params_dir: Path, shell_out: Path, log=print, baseline: bool = True) -> Run:
    """The mounts and every check on them."""
    skin = zones(d, log)
    base = fit.sheet(params.load(params_dir), "MountsBase")
    try:
        v = lambda name: params.value(base, name)
        design = build(d, lay, m, v, skin)
        load_rows = loads(design, m, v)
    finally:
        App.closeDocument(base.Name)
    parts = shell_parts(d, shell_out, log)
    cav = stand_in(parts, skin, d)
    room = room_values(d, lay, None, shell_out)
    hw = hardware_shapes(d, lay, params_dir, room)
    before = fit_rules(d, lay, params_dir, parts, cav, room, None) if baseline else {}
    rules = fit_rules(d, lay, params_dir, parts, cav, room, design)
    declared, other = split_findings(rules)
    rep = {"values": asdict(m), "skin": in_skin(design, skin), "own_pairs": own_pairs(design),
           "fit_before": [f"{t}: {s}: {x}" for t, rows in before.items() for lv, s, x in rows if lv == check.FAIL],
           "fit_rules": {t: rows for t, rows in rules.items()}, "fit_declared": declared, "fit_other": other,
           "access": access(design, m, hw, d), "module_path": module_path(design, m, hw, d), "psu_path": psu_path(design, m, hw, d),
           "seams": seams(design, d), "print": print_rows(design, split.printer(params_dir)), "loads": load_rows, "faces": face_findings(design),
           "screws": [asdict(sc) for sc in design.screws], "shroud_points": [[round(c, 2) for c in p] for p in design.shroud_points],
           "psu_holes": [[round(c, 2) for c in p] for p in design.psu_holes], "ties": design.ties,
           "bosses": [{"name": s.name, "on": s.on, "box": box_of(s.whole), "cm3": round(s.whole.Volume / 1000, 2), "note": s.note} for s in design.solids if s.kind == "boss"],
           "site": {k: x for k, x in asdict(design.site).items() if k != "a"}}
    fails = [f"skin: {r['solid']} has {r['in_skin_mm3']} mm3 in the skin" for r in rep["skin"] if not r["ok"]]
    fails += [f"own solids: {a} / {b}: {vol:.1f} mm3 in common" for a, b, vol in rep["own_pairs"]]
    fails += ["fit rules, hardware alone: " + t for t in rep["fit_before"]] + ["fit rules: " + t for t in other]
    fails += [f"access: {r['screw']}: margin {r.get('door_margin')}, in the way {r.get('in_the_way')}" for r in rep["access"] if not r["ok"]]
    fails += [f"{k}: margins {rep[k]['margins']}, in the way {rep[k]['in_the_way']}" for k in ("module_path", "psu_path") if not rep[k]["ok"]]
    fails += [f"seam: {r['boss']} is {r['distance']} from {r['nearest']}" for r in rep["seams"] if not r["ok"]]
    fails += [f"print: {r['part']} does not fit the printer ({r['x']} x {r['y']} x {r['z']})" for r in rep["print"] if not r["fits"]]
    fails += [f"load: {r['mount']}, {r['what']}: {r['stress_MPa']} MPa (sustained {r['sustained_MPa']})" for r in rep["loads"] if not r["ok"]]
    fails += ["face check: " + t for t in rep["faces"]]
    rep["failures"] = fails
    rep["result"] = check.FAIL if fails else check.PASS
    return Run(design, rep, hw, skin)


def box_of(shape: Part.Shape) -> list[float]:
    b = shape.BoundBox
    return [round(x, 2) for x in (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax)]


def markdown(rep: dict) -> str:
    out = ["# The mounts of the hardware", "", f"Result: **{rep['result']}**.", ""]
    out += [f"- FAIL: {t}" for t in rep["failures"]] + ([""] if rep["failures"] else [])
    out += ["## Fit rules with the mounts added", "", "| Rule | Level | Subject | Detail |", "| --- | --- | --- | --- |"]
    out += [f"| {k} | {lv} | {s} | {x} |" for k, rows in rep["fit_rules"].items() for lv, s, x in rows]
    out += ["", f"Declared: {len(rep['fit_declared'])}. Other failures: {len(rep['fit_other'])}. Failures of the hardware alone: {len(rep['fit_before'])}.", "",
            "## Skin", "", "| Solid | Kind | In the skin (mm3) | Root held (mm3) | Result |", "| --- | --- | --- | --- | --- |"]
    out += [f"| {r['solid']} | {r['kind']} | {r['in_skin_mm3']} | {r.get('root_held_mm3', '')} | {'PASS' if r['ok'] else 'FAIL'} |" for r in rep["skin"]]
    out += ["", "## Screws", "", "| Screw | Size | State | Head (x, y, z) | Margin in the door | In the way | Result |", "| --- | --- | --- | --- | --- | --- | --- |"]
    out += [f"| {r['screw']} | {r['size']} | {r['state']} | {r['head']} | {r.get('door_margin', '')} | {', '.join(r.get('in_the_way', []))} | {'PASS' if r['ok'] else 'FAIL'} |"
            for r in rep["access"]]
    for key, title in (("module_path", "The compute module on its way out"), ("psu_path", "The power supply on its way out")):
        p = rep[key]
        out += ["", f"## {title}", "", f"Steps: {'; '.join(p['steps'])}.", f"Margins in the door opening: {p['margins']}. In the way: {p['in_the_way'] or 'nothing'}. "
                f"Result: {'PASS' if p['ok'] else 'FAIL'}."]
    out += ["", "## Seams", "", "| Boss | Piece | Nearest seam or flange | Distance | Result |", "| --- | --- | --- | --- | --- |"]
    out += [f"| {r['boss']} | {r['on']} | {r['nearest']} | {r['distance']} | {'PASS' if r['ok'] else 'FAIL'} |" for r in rep["seams"]]
    out += ["", "## Print", "", "| Part | Box (mm) | Fits | Grams | On the bed | Note |", "| --- | --- | --- | --- | --- | --- |"]
    out += [f"| {r['part']} | {r['x']} x {r['y']} x {r['z']} | {'yes' if r['fits'] else 'no'} | {r['grams']} | {r['bed']} | {r['note']} |" for r in rep["print"]]
    out += ["", "## Loads", "", "| Mount | What | Force (N) | Path | Estimate | Stress (MPa) | Sustained (MPa) | Result |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    out += [f"| {r['mount']} | {r['what']} | {r['force_N']} | {r['path']} | {r['estimate']} | {r['stress_MPa']} | {r['sustained_MPa']} | {'PASS' if r['ok'] else 'FAIL'} |"
            for r in rep["loads"]]
    out += ["", "## Interfaces", "", f"Shroud points (M3 inserts, axis along y, in the plane of the board's top face): {rep['shroud_points']}.",
            f"Screw holes of the power supply in the lower rear wall (diameter {rep['values']['atx_hole_d']:g}, at the inner face): {rep['psu_holes']}.", "",
            "## Bosses", "", "| Boss | Piece | Box (x0, x1, y0, y1, z0, z1) | cm3 | Note |", "| --- | --- | --- | --- | --- |"]
    out += [f"| {r['name']} | {r['on']} | {r['box']} | {r['cm3']} | {r['note']} |" for r in rep["bosses"]]
    out += ["", "## Tie points", "", "| Name | At (x, y, z) | On | For |", "| --- | --- | --- | --- |"]
    out += [f"| {r['name']} | {r['at']} | {r['on']} | {r['for']} |" for r in rep["ties"]]
    out += ["", f"Face check: {len(rep['faces'])} findings."] + [f"- {t}" for t in rep["faces"]]
    return "\n".join(out) + "\n"


def export(out: Path, design: Design) -> None:
    """The parts and bosses as BREP and STL, with manifest.json and edges.json."""
    folder = out / "parts"
    folder.mkdir(parents=True, exist_ok=True)
    manifest, edges = {}, {}
    for s in design.solids:
        shape = s.whole
        shape.exportBrep(str(folder / f"{s.name}.brep"))
        MeshPart.meshFromShape(Shape=shape, LinearDeflection=MESH_LINEAR, AngularDeflection=MESH_ANGULAR).write(str(folder / f"{s.name}.stl"))
        manifest[s.name] = {"file": f"{s.name}.stl", "brep": f"{s.name}.brep", "finish": FINISH["boss" if s.kind == "boss" else s.group], "group": s.group,
                            "kind": s.kind, "on": s.on}
        edges[s.name] = so.edge_polylines(shape)
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    (folder / "edges.json").write_text(json.dumps(edges), encoding="utf-8")


def main() -> int:
    root = Path(os.environ.get("CANDYBAR_ROOT", Path(__file__).resolve().parents[2]))
    params_dir = Path(os.environ.get("CANDYBAR_PARAMS") or root / "params")
    out = Path(os.environ.get("CANDYBAR_OUT", root / "out" / "mounts"))
    shell_out = Path(os.environ.get("CANDYBAR_SHELL", root / "out" / "shell-rev7"))
    out.mkdir(parents=True, exist_ok=True)
    d = Blueprint()
    result = run(d, fit.Layout(), Mounts(), params_dir, shell_out)
    (out / "report.json").write_text(json.dumps(result.report, indent=1, default=str), encoding="utf-8")
    (out / "report.md").write_text(markdown(result.report), encoding="utf-8")
    export(out, result.design)
    if os.environ.get("CANDYBAR_MOUNT_SCENES", "1") != "0":
        from . import mounts_scenes  # noqa: PLC0415 - the drawings need the whole skin

        mounts_scenes.write(out, d, result)
    print(markdown(result.report))
    return 1 if result.failures else 0
