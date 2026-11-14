"""The rear as parts: the door in its opening, its vents, the shroud and the exhaust duct of the compute module, the
opening for the power supply and the inlet for make-up air (roadmap step 11).

Run headless. It exits 1 when a check fails:

    CANDYBAR_OUT=cad/out/shell-rev7 cad/candybar/freecad-run.sh candybar.shell.rear

The outer form does not change. The opening of the door is the one of dims.Blueprint, the positions of the hardware
are the anchors of the fit study (fit.anchors), and the joint values are those of joints.py. Rear holds every other
value. The frame is that of the cabinet: x across, y to the rear, z up; the lower rear wall stands between
y = body_d - wall_t and y = body_d.

The door is a rebated cover in two halves, bonded on the centre line. Its joint with the shell lies inside the
thickness of the wall, not in the 4 mm strip beside the cut-ins: the inner half of the wall goes on round the opening
as a land (the lip on the sill, a tongue on each side, the tongue of the head rail), and the door's margin is the
outer half. The lip on the sill is a hook: the door's foot stands behind it. Two quarter-turn fasteners at the head
pull the door onto the land, and two cones locate it. The head rail is a part of its own, bonded behind the strip
above the opening, because the upper rear piece stands on that edge on the printer.

The vents have one form: upright slots with round ends. The lower rear wall prints upright, and an upright slot
prints there with no support (its round head is 8 across). The door prints flat and has the same slots.

The parts:
  door half R, L     printed, painted: the fan vent in R, the vent for the hot air in L
  head rail R, L     printed, bonded behind the strip above the opening: the land of the head, the seats of the
                     quarter-turn fasteners and the sockets of the cones
  shroud base, top   printed: the walls round the fins and the seat of the fan; the four fan screws hold them together
  duct body, back    printed: the box that turns the hot air to the door
  fan, seals         bought: the fan, and the foam between the compute module and the door
and what it does to the pieces of the split (finish_pieces): the lip and the rib under the sill on the two rear lower
pieces, the tongue and the post on the two middle pieces, the openings in the lower rear wall, and the edge break
round every opening.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass
from pathlib import Path

import FreeCAD as App
import MeshPart
import Part

from . import check, params
from . import joints
from . import solids as so
from . import split
from .dims import Blueprint

V = App.Vector
P2 = tuple[float, float]
REAR = "rear"
CAD = Path(__file__).resolve().parents[2]
SIDES = {1: "R", -1: "L"}
# a tool reaches this far past the faces that it cuts through
PAST = 1.0
# two faces that only touch do not always fuse: a part that is added reaches this far into the piece
INTO = 0.6
# the hardware values that the rear parts read from the parameter sheets
SHEET_VALUES = ("bc_pcb_l", "bc_pcb_w_io", "bc_pcb_w_pwr", "bc_pcb_step_x", "bc_pcb_t", "bc_fin_x0", "bc_fin_y0", "bc_fin_l", "bc_fin_w",
                "bc_fin_h", "bc_shroud_x0", "bc_shroud_y0", "bc_shroud_l", "bc_shroud_w", "bc_shroud_h", "bc_fan_cx", "bc_fan_cy",
                "bc_hood_x1", "bc_dp_clear", "bc_io_overhang", "bc_gap_door", "fan_frame", "fan_t", "fan_hole_pitch", "fan_hole_d",
                "psu_w", "psu_h")


@dataclass(frozen=True)
class Rear:
    """The design values of the rear parts, mm."""
    # ---- the door in its opening: a rebated cover ----
    door_gap: float = 1.0        # between the door's edge and the opening, all round (as panel_gap)
    margin_t: float = 2.0        # the door's margin is the outer part of the wall, this thick; the land is the rest
    land: float = 6.0            # the land stands this far inside the opening, all round
    step_gap: float = 0.5        # the door's inner step to the ring of the land, at the sides and the head
    lip_h: float = 5.0           # the lip on the sill, at the plane of the lap; its top falls 45 degrees to the inside
    nose_gap: float = 0.3        # the door's foot to the lip, square to the 45 degree faces
    sill_rib_gap: float = 3.0    # the rib under the sill ends this far from the clear space over the supply's fan
    post_w: float = 8.0          # the post behind each side tongue: across
    post_d: float = 6.0          # and inward from the inner face of the wall
    # ---- the two halves: bonded on the centre line ----
    seam_rib_w: float = 6.0      # each half has a rib at the centre line, this wide
    seam_rib_d: float = 8.0      # and this deep behind the inner face
    seam_rib_z0: float = 8.0     # it starts this far above the sill
    dowel_len: float = 10.0      # two dowel pins of joints.pin_d line the halves up
    dowel_z: tuple[float, float] = (34.0, 124.0)  # above the sill
    # ---- the head rib: it makes the door a beam between the two fasteners ----
    head_rib_w: float = 6.0
    head_rib_d: float = 20.0
    head_rib_gap: float = 6.0    # below the head rail. The door comes off with its head tilted out 6 degrees (more,
                                 # and its foot runs into the lip), and then it lifts 2 over the lip. At 6 degrees
                                 # the rib has risen 1.5 and a part of it is still under the rail
    head_rib_end: float = 2.6    # it ends this far before the block of the fastener
    # ---- the head rail ----
    rail_d: float = 12.0         # inward from the inner face of the wall
    rail_drop: float = 12.0      # its lower face below the top edge of the opening: 1 above the top of the board
    rail_rise: float = 9.0       # its upper face above the top edge of the opening: the bond to the strip
    rail_end_gap: float = 0.5    # to the post at its outer end
    rail_mid_gap: float = 0.25   # to the centre line
    block_drop: float = 10.0     # the block of the fastener hangs this far below the rail
    block_in: float = 27.4       # and starts this far from the fastener, toward the centre line
    # ---- the quarter-turn fastener: ASSUMED, a common panel quarter-turn of the small series (DZUS type) ----
    qt_x: float = 180.0          # from the centre line: outside the board, so that the board passes under the rail
    qt_below: float = 10.0       # below the door's top edge: the hole in the web then ends 0.5 below the tongue
    qt_hole: float = 6.5         # through the door, for a shank of 6.0 to 6.4
    qt_head: float = 15.0        # the largest head that the flat round it takes
    qt_flat: float = 18.0        # the flat of the door round the hole: no vent, no edge break
    qt_web: float = 3.0          # the web of the rail that the receptacle sits behind: grip = wall_t + qt_web
    qt_web_hole: float = 9.0
    qt_pocket_w: float = 32.0    # the room of the receptacle behind the web: across
    qt_pocket_h: float = 13.0    # and up; its depth is rail_d - qt_web
    cone_dx: float = -21.7       # the locating cone, from the fastener
    cone_dz: float = -6.0
    cone_tip: float = 4.0        # the cone of joints.cone_d x cone_h ends at this diameter
    # ---- the vents: upright slots with round ends ----
    slot: float = 8.0
    bar: float = 2.5
    corner: float = 3.0          # the radius of each corner of the two large openings in plan: as the design round of
                                 # the rear (Blueprint.rear_round_r)
    fan_vent_d: float = 116.0    # the slots of the fan vent end on this circle
    hot_slots: int = 9
    fan_open_min: float = 0.70   # bc250-cooling-and-psu.md A6: the door grille is at least 70 % open
    hot_free_min: float = 3000.0  # the same: at least 30 cm2 behind the hood
    # ---- the lower rear wall: the supply's openings, and the inlet as their mirror. u, v on the supply's rear face,
    # seen from behind: u to the right from its lower left corner, v up ----
    low_v0: float = 10.5         # every opening of the lower wall stands between these two lines; the supply's screws
    low_v1: float = 75.5         # are 4.5 below and 4.5 above them
    grille_u0: float = 7.0
    grille_slots: int = 7
    socket_u: P2 = (84.0, 122.0)
    socket_cut: P2 = (0.0, 10.0)  # the corner cuts at the sill and at the head (the head bridges 20 on the printer)
    switch_u: P2 = (125.0, 145.0)
    switch_cut: P2 = (0.0, 0.0)  # none: its head bridges 14
    psu_screws: tuple[P2, ...] = ((6.0, 6.0), (144.0, 6.0), (6.0, 80.0), (144.0, 80.0))
    psu_screw_hole: float = 4.0
    inlet_slots: int = 13
    # ---- the shroud and the duct ----
    shell_t: float = 2.4         # their walls
    seat_t: float = 2.0          # the plate under the fan
    air_gap: float = 10.0        # between the fin tops and the plate
    fin_clear: float = 0.25      # the walls to the sides of the fin block
    fan_clear: float = 0.3       # the collar to the fan
    fin_foam: float = 3.0        # foam between a wall and the fin tops
    pcb_clear: float = 0.5       # the walls end this far above the board
    notch: tuple[float, float, float, float] = (242.25, 286.68, 1.8, 30.8)  # the corner of the fin block with no fins: x', y'
    fence_t: float = 2.0
    fan_post: float = 9.6        # the post of a fan screw: an insert of joints.insert_hole_d and 2 of wall
    fan_post_web: float = 16.0   # the corner plate that ties a post to the walls
    ear: tuple[float, float, float] = (10.0, 8.0, 6.0)  # the ears to the carrier: along, out, thick
    ear_x: P2 = (180.0, 270.0)
    ear_hole: float = 3.4
    duct_floor_gap: float = 0.3  # the duct's floor to the edge of the board
    cable_notch: tuple[float, float, float] = (-45.0, -5.0, 16.0)  # in the lower wall of the duct: x' from, to, and its height
    cable_notch_cut: float = 10.0  # its two upper corners are cut 45 degrees: the head bridges 20 on the printer

    @property
    def pitch(self) -> float:
        return self.slot + self.bar


@dataclass(frozen=True)
class Place:
    """Where the hardware stands (the anchors of the fit study), and the values of the parameter sheets."""
    psu_x1: float   # the edge of the supply's rear face that is nearest to the centre line (u = 0)
    psu_z0: float
    bc_x0: float    # the I/O edge of the board
    bc_y: float     # the top face of the PCB
    bc_z0: float    # the straight long edge of the board
    v: dict

    def x(self, xp: float) -> float:
        return self.bc_x0 + xp

    def y(self, zp: float) -> float:
        return self.bc_y + zp

    def z(self, yp: float) -> float:
        return self.bc_z0 + yp

    def box(self, x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part.Shape:
        """A box in the datum of the board: x' from the I/O edge, y' from the straight long edge, z' above the PCB."""
        return box(self.x(x0), self.x(x1), self.y(z0), self.y(z1), self.z(y0), self.z(y1))

    def rod(self, xp: float, yp: float, z0: float, z1: float, dia: float) -> Part.Shape:
        """A cylinder along z' of the board."""
        return Part.makeCylinder(dia / 2, z1 - z0, V(self.x(xp), self.y(z0), self.z(yp)), V(0, 1, 0))


def place(d: Blueprint, lay=None, params_dir: Path | None = None) -> Place:
    from . import fit  # noqa: PLC0415

    lay = lay or fit.Layout()
    base = fit.sheet(params.load(params_dir or CAD / "params"), "RearBase")
    try:
        v = lambda name: params.value(base, name)
        a = fit.anchors(d, lay, v, 0.0)
        vals = {name: v(name) for name in SHEET_VALUES}
    finally:
        App.closeDocument(base.Name)
    return Place(a["psu_x0"] + vals["psu_w"], a["psu_z0"], a["bc_x0"], a["bc_pcb_y"], a["bc_top_z"] - vals["bc_pcb_w_pwr"], vals)


@dataclass(frozen=True)
class Frame:
    """The lines of the door and its opening that the values of Rear give on the form."""
    x_open: float
    z0: float
    z1: float
    y_in: float
    y_lap: float
    y_out: float
    x_door: float
    zd0: float
    zd1: float
    x_ring: float
    z_lip: float
    z_lip_in: float
    z_head: float
    x_step: float
    z_step1: float
    z_nose: float
    z_nose_in: float
    z_rail0: float
    z_rail1: float
    x_rail0: float
    x_rail1: float
    x_block0: float
    z_block0: float
    zq: float
    x_cone: float
    z_cone: float
    z_rib0: float
    z_rib1: float
    x_rib1: float


def frame(d: Blueprint, r: Rear) -> Frame:
    x_open, z0, z1 = d.door_w / 2, d.door_z0, d.door_z1
    y_out = d.body_d
    y_in, y_lap = y_out - d.wall_t, y_out - r.margin_t
    x_ring, z_lip, z_head = x_open - r.land, z0 + r.lip_h, z1 - r.land
    z_lip_in = z_lip - (y_lap - y_in)
    rise = r.nose_gap * math.sqrt(2)
    z_rail0 = z1 - r.rail_drop
    zd1 = z1 - r.door_gap
    zq = zd1 - r.qt_below
    return Frame(x_open, z0, z1, y_in, y_lap, y_out, x_open - r.door_gap, z0 + r.door_gap, zd1, x_ring, z_lip, z_lip_in, z_head,
                 x_ring - r.step_gap, z_head - r.step_gap, z_lip + rise, z_lip_in + rise, z_rail0, z1 + r.rail_rise,
                 r.rail_mid_gap, x_ring - r.rail_end_gap, r.qt_x - r.block_in, z_rail0 - r.block_drop, zq,
                 r.qt_x + r.cone_dx, zq + r.cone_dz, z_rail0 - r.head_rib_gap - r.head_rib_w, z_rail0 - r.head_rib_gap,
                 r.qt_x - r.block_in - r.head_rib_end)


# ---------- small builders ----------

def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part.Shape:
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def plate(points: list[P2]) -> Part.Face:
    """A face in the plane y = 0 from points (x, z)."""
    return Part.Face(Part.makePolygon([V(x, 0.0, z) for x, z in [*points, points[0]]]))


def through(face: Part.Shape, y0: float, y1: float) -> Part.Shape:
    """A face of the plane y = 0 as a prism from y0 to y1."""
    return face.translated(V(0, y0, 0)).extrude(V(0, y1 - y0, 0))


def prism_x(points: list[P2], x0: float, x1: float) -> Part.Shape:
    """A section (y, z) as a prism from x0 to x1."""
    face = Part.Face(Part.makePolygon([V(x0, y, z) for y, z in [*points, points[0]]]))
    return face.extrude(V(x1 - x0, 0, 0))


def mirrored(shape: Part.Shape) -> Part.Shape:
    return shape.mirror(V(0, 0, 0), V(1, 0, 0))


def soft(face: Part.Face, radius: float) -> Part.Face | None:
    """The face with a radius on each convex corner of its outline: in by the radius, and out again with arcs. None
    when the face is too small for it."""
    if radius <= 0:
        return face
    try:
        inner = face.makeOffset2D(-radius, 0, False, False, False)
        out = inner.makeOffset2D(radius, 0, False, False, False)
    except (Part.OCCError, ValueError, RuntimeError):
        return None
    faces = [f for f in out.Faces if f.Area > radius * radius]
    return faces[0] if len(faces) == 1 else None


def stadium(xc: float, z0: float, z1: float, w: float) -> Part.Face:
    """An upright slot w wide from z0 to z1 with round ends, in the plane y = 0."""
    h = w / 2
    pt = lambda x, z: V(x, 0.0, z)
    a, b, c, e = pt(xc - h, z0 + h), pt(xc + h, z0 + h), pt(xc + h, z1 - h), pt(xc - h, z1 - h)
    return Part.Face(Part.Wire([Part.Arc(a, pt(xc, z0), b).toShape(), Part.LineSegment(b, c).toShape(),
                                Part.Arc(c, pt(xc, z1), e).toShape(), Part.LineSegment(e, a).toShape()]))


def octagon(x0: float, x1: float, z0: float, z1: float, low: float, top: float) -> list[P2]:
    """A rectangle with 45 degree corner cuts: low at the sill, top at the head. A cut of 0 leaves the corner."""
    points = [(x0 + low, z0), (x1 - low, z0), (x1, z0 + low), (x1, z1 - top), (x1 - top, z1), (x0 + top, z1), (x0, z1 - top), (x0, z0 + low)]
    return [q for i, q in enumerate(points) if q != points[i - 1]]


def area(faces: list[Part.Face]) -> float:
    return sum(f.Area for f in faces)


# ---------- the openings: faces in the plane y = 0, in the x and z of the cabinet ----------

def slots(centres: list[float], z0: float, z1: float, r: Rear) -> list[Part.Face]:
    """Upright slots at the centres, from z0 to z1."""
    return [stadium(x, z0, z1, r.slot) for x in centres]


def fan_vent(r: Rear, p: Place) -> list[Part.Face]:
    """The vent over the fan: the slots of one field, each as long as the circle of the fan lets it be (its round
    ends touch the circle from inside)."""
    cx, cz, reach = p.x(p.v["bc_fan_cx"]), p.z(p.v["bc_fan_cy"]), r.fan_vent_d / 2 - r.slot / 2
    n = int(reach // r.pitch)
    out = []
    for k in range(-n, n + 1):
        half = math.sqrt(max(0.0, reach ** 2 - (k * r.pitch) ** 2))
        if half > r.slot / 2:  # shorter, and the slot is nearly a round hole
            out.append(stadium(cx + k * r.pitch, cz - half - r.slot / 2, cz + half + r.slot / 2, r.slot))
    return out


def duct_inside(r: Rear, p: Place) -> tuple[float, float, float, float]:
    """The inside of the duct at the door: x from, x to, z from, z to."""
    v = p.v
    return (p.x(-v["bc_dp_clear"] - v["bc_io_overhang"] + r.shell_t), p.x(v["bc_hood_x1"] - r.shell_t),
            p.z(v["bc_shroud_y0"] + r.shell_t), p.z(v["bc_shroud_y0"] + v["bc_shroud_w"] - r.shell_t))


def hot_vent(r: Rear, p: Place) -> list[Part.Face]:
    """The vent for the hot air: slots as high as the fan vent, in the middle of the duct's inside."""
    x0, x1, _, _ = duct_inside(r, p)
    cz, rad = p.z(p.v["bc_fan_cy"]), r.fan_vent_d / 2
    first = (x0 + x1) / 2 - (r.hot_slots - 1) / 2 * r.pitch
    return slots([first + k * r.pitch for k in range(r.hot_slots)], cz - rad, cz + rad, r)


def low_z(r: Rear, p: Place) -> P2:
    return p.psu_z0 + r.low_v0, p.psu_z0 + r.low_v1


def supply_openings(r: Rear, p: Place) -> dict[str, list[Part.Face]]:
    """The openings for the supply's rear face in the lower rear wall: the grille over its vent, the opening for
    the mains socket, and the opening for the rocker and the ECO switch."""
    z0, z1 = low_z(r, p)
    x = lambda u: p.psu_x1 - u
    grille = slots([x(r.grille_u0 + r.slot / 2 + k * r.pitch) for k in range(r.grille_slots)], z0, z1, r)
    socket = soft(plate(octagon(x(r.socket_u[1]), x(r.socket_u[0]), z0, z1, *r.socket_cut)), r.corner)
    switch = soft(plate(octagon(x(r.switch_u[1]), x(r.switch_u[0]), z0, z1, *r.switch_cut)), r.corner)
    return {"grille": grille, "socket": [socket], "switch": [switch]}


def supply_screws(r: Rear, p: Place) -> list[P2]:
    return [(p.psu_x1 - u, p.psu_z0 + v) for u, v in r.psu_screws]


def inlet(r: Rear, p: Place) -> list[Part.Face]:
    """The inlet for make-up air: the mirror of the supply's field, all slots."""
    z0, z1 = low_z(r, p)
    return slots([-p.psu_x1 + r.grille_u0 + r.slot / 2 + k * r.pitch for k in range(r.inlet_slots)], z0, z1, r)


def field(faces: list[Part.Face]) -> tuple[float, float, float, float]:
    """The box of some openings: x from, x to, z from, z to."""
    return (min(f.BoundBox.XMin for f in faces), max(f.BoundBox.XMax for f in faces),
            min(f.BoundBox.ZMin for f in faces), max(f.BoundBox.ZMax for f in faces))


# ---------- the door ----------

def chamfered_hole(x: float, z: float, dia: float, y0: float, y1: float) -> list[Part.Shape]:
    """A hole along y from y0 to the outer face y1, with the chamfer of joints at its mouth."""
    c = joints.OTHER_JOINTS.service_chamfer
    return [Part.makeCylinder(dia / 2, y1 - y0 + 2 * PAST, V(x, y0 - PAST, z), V(0, 1, 0)),
            Part.makeCone(dia / 2 + 2 * c, dia / 2, 2 * c, V(x, y1 + c, z), V(0, -1, 0))]


def on_outer(e: Part.Edge, y: float) -> bool:
    return all(abs(v.Point.y - y) < 1e-6 for v in e.Vertexes)


def door_half(d: Blueprint, r: Rear, p: Place, side: int) -> Part.Shape:
    """One half of the door, with its vent, its ribs, its cone, the hole of its fastener and the edge break. It is
    made on the right and turned over for the left."""
    f, oj = frame(d, r), joints.OTHER_JOINTS
    skin = box(0, f.x_door, f.y_lap, f.y_out, f.zd0, f.zd1)
    step = prism_x([(f.y_in, f.z_nose_in), (f.y_lap, f.z_nose), (f.y_lap, f.z_step1), (f.y_in, f.z_step1)], 0, f.x_step)
    seam = box(0, r.seam_rib_w, f.y_in - r.seam_rib_d, f.y_in, f.z0 + r.seam_rib_z0, f.z_rib1)
    head = box(0, f.x_rib1, f.y_in - r.head_rib_d, f.y_in, f.z_rib0, f.z_rib1)
    cone = Part.makeCone(oj.cone_d / 2, r.cone_tip / 2, oj.cone_h, V(f.x_cone, f.y_in, f.z_cone), V(0, -1, 0))
    body = skin.fuse([step, seam, head, cone]).removeSplitter()
    vent = fan_vent(r, p) if side > 0 else [mirrored(v) for v in hot_vent(r, p)]
    tools = [through(v, f.y_in - PAST, f.y_out + PAST) for v in vent]
    tools += chamfered_hole(r.qt_x, f.zq, r.qt_hole, f.y_in, f.y_out)
    hole = oj.pin_d + oj.pin_clearance
    tools += [Part.makeCylinder(hole / 2, r.dowel_len / 2 + 0.5 + PAST, V(-PAST, f.y_in - r.seam_rib_d / 2, f.z0 + z), V(1, 0, 0)) for z in r.dowel_z]
    body = body.cut(tools)
    at_hole = lambda e: e.BoundBox.Center.distanceToPoint(V(r.qt_x, f.y_out, f.zq)) < 1.0 and e.BoundBox.DiagonalLength < 2 * r.qt_hole
    rim = [e for e in body.Edges if on_outer(e, f.y_out) and not all(abs(v.Point.x) < 1e-6 for v in e.Vertexes) and not at_hole(e)]
    corners = [e for e in body.Edges if len(e.Vertexes) == 2 and all(abs(v.Point.x - f.x_door) < 1e-6 for v in e.Vertexes)
               and abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) < 1e-6 and min(abs(e.Vertexes[0].Point.z - z) for z in (f.zd0, f.zd1)) < 1e-6]
    out = body.makeFillet(d.edge_break, rim + corners)
    if out.isNull() or not out.isValid() or len(out.Solids) != 1:
        raise Part.OCCError(f"door half {SIDES[side]}: the edge break did not make one valid solid")
    return out if side > 0 else mirrored(out)


# ---------- the land: what the shell gets round the opening ----------

def sill_rib_span(d: Blueprint, r: Rear, p: Place, side: int) -> P2:
    """Where the rib under the sill runs on one side, as distances from the centre line: all the way on the right,
    and on the left as far as the clear space over the fan of the power supply lets it."""
    f = frame(d, r)
    return (0.0, f.x_ring) if side > 0 else (0.0, min(f.x_ring, -p.psu_x1 - r.sill_rib_gap))


def sill_lip(d: Blueprint, r: Rear, p: Place, side: int) -> Part.Shape:
    """The lip on the sill and the rib under it, for one rear lower piece. The inner part of the wall goes on above
    the sill, and its top falls 45 degrees to the inside, so that the door's foot hooks behind it. The rib is the
    flange of joint 1 with its gusset (joints.JOINT), without a key or a screw: it stiffens the sill, which is a
    free edge when the door is off."""
    f, j = frame(d, r), joints.JOINT
    top = f.z0 - split.KERF / 2
    lip = prism_x([(f.y_in, top - INTO), (f.y_lap, top - INTO), (f.y_lap, f.z_lip), (f.y_in, f.z_lip_in)], 0, f.x_ring)
    x0, x1 = sill_rib_span(d, r, p, side)
    rib = prism_x([(f.y_in + INTO, top), (f.y_in - j.flange_h, top), (f.y_in - j.flange_h, top - j.flange_t),
                   (f.y_in + INTO, top - j.flange_t - j.gusset_leg - INTO)], x0, x1)
    both = lip.fuse(rib).removeSplitter()
    return both if side > 0 else mirrored(both)


def side_tongue(d: Blueprint, r: Rear, side: int) -> Part.Shape:
    """The tongue on one side of the opening and the post behind it, for one middle piece."""
    f = frame(d, r)
    z0 = f.z0 + split.KERF / 2
    tongue = box(f.x_ring, f.x_open + INTO, f.y_in, f.y_lap, z0, f.z1)
    # the post starts at the height of the lip's top, with a foot of 45 degrees: below that height the clear space
    # over the fan of the power supply reaches the rear wall at the left
    post = prism_x([(f.y_in + INTO, f.z_lip - INTO), (f.y_in, f.z_lip), (f.y_in - r.post_d, f.z_lip + r.post_d), (f.y_in - r.post_d, f.z1),
                    (f.y_in + INTO, f.z1)], f.x_ring, f.x_ring + r.post_w)
    both = tongue.fuse(post).removeSplitter()
    return both if side > 0 else mirrored(both)


def head_rail(d: Blueprint, r: Rear, side: int) -> Part.Shape:
    """The head rail of one half: the land of the head, the seat of the quarter-turn fastener (a web with the room
    of the receptacle behind it) and the socket of the cone."""
    f, oj = frame(d, r), joints.OTHER_JOINTS
    y0 = f.y_in - r.rail_d
    body = box(f.x_rail0, f.x_rail1, y0, f.y_in, f.z_rail0, f.z_rail1)
    tongue = box(f.x_rail0, f.x_rail1, f.y_in, f.y_lap, f.z_head, f.z1)
    block = box(f.x_block0, f.x_rail1, y0, f.y_in, f.z_block0, f.z_rail0)
    rail = body.fuse([tongue, block]).removeSplitter()
    pocket = box(r.qt_x - r.qt_pocket_w / 2, r.qt_x + r.qt_pocket_w / 2, y0 - PAST, f.y_in - r.qt_web, f.zq - r.qt_pocket_h / 2, f.zq + r.qt_pocket_h / 2)
    hole = Part.makeCylinder(r.qt_web_hole / 2, r.qt_web + PAST, V(r.qt_x, f.y_in - r.qt_web - PAST, f.zq), V(0, 1, 0))
    # the socket: the cone with the clearance of joints all round, 0.5 deeper, and widened a little at its mouth
    deep, lead = oj.cone_h + 0.5, 0.2
    slope = (oj.cone_d - r.cone_tip) / 2 / oj.cone_h
    r0 = oj.cone_d / 2 + oj.cone_clearance
    socket = Part.makeCone(r0 + lead * slope, r0 - deep * slope, deep + lead, V(f.x_cone, f.y_in + lead, f.z_cone), V(0, -1, 0))
    rail = rail.cut([pocket, hole, socket])
    return rail if side > 0 else mirrored(rail)


# ---------- the shroud, the fan and the duct, in the datum of the board ----------

def shroud_lines(r: Rear, p: Place) -> dict[str, float]:
    """The planes of the shroud in the datum of the board."""
    v = p.v
    fan0 = v["bc_fin_h"] + r.air_gap + r.seat_t  # the seat of the fan
    half = v["fan_frame"] / 2
    return {"x0": v["bc_shroud_x0"], "x1": v["bc_shroud_x0"] + v["bc_shroud_l"],
            "fy0": v["bc_fin_y0"] - r.fin_clear, "fy1": v["bc_fin_y0"] + v["bc_fin_w"] + r.fin_clear,
            "cy0": v["bc_fan_cy"] - half - r.fan_clear, "cy1": v["bc_fan_cy"] + half + r.fan_clear,
            "cx0": v["bc_fan_cx"] - half - r.fan_clear, "cx1": v["bc_fan_cx"] + half + r.fan_clear,
            "fin": v["bc_fin_h"], "seat0": fan0 - r.seat_t, "fan0": fan0, "fan1": fan0 + v["fan_t"],
            "fin_end": v["bc_fin_x0"] + v["bc_fin_l"]}


def fan_holes(p: Place) -> list[P2]:
    h = p.v["fan_hole_pitch"] / 2
    return [(p.v["bc_fan_cx"] + a * h, p.v["bc_fan_cy"] + b * h) for a in (-1, 1) for b in (-1, 1)]


def shroud_base(r: Rear, p: Place) -> Part.Shape:
    """The lower part of the shroud: the walls beside and behind the fin block, the wall over the fins on the side
    of the exhaust, the fence round the corner with no fins, the posts of the fan screws and the ears to the carrier."""
    s, oj = shroud_lines(r, p), joints.OTHER_JOINTS
    t = r.shell_t
    y0, y1 = s["cy0"] - t, s["cy1"] + t
    low, top = r.pcb_clear, s["seat0"]
    parts = [p.box(s["x0"], s["x1"], y0, s["fy0"], low, top), p.box(s["x0"], s["x1"], s["fy1"], y1, low, top),
             p.box(s["x1"] - t, s["x1"], y0, y1, low, top),
             p.box(s["x0"], s["x0"] + t, y0, y1, s["fin"] + r.fin_foam, top)]
    nx0, nx1, ny0, ny1 = r.notch
    parts += [p.box(nx0 - r.fence_t, nx0, s["fy0"], ny1 + r.fence_t, s["fin"], top),
              p.box(nx0 - r.fence_t, s["x1"] - t, ny1, ny1 + r.fence_t, s["fin"], top)]
    post0 = top - oj.insert_l - 1.5
    web = r.fan_post_web
    for hx, hy in fan_holes(p):
        parts.append(p.rod(hx, hy, post0, top, r.fan_post))
        cx = s["cx0"] if hx < p.v["bc_fan_cx"] else s["cx1"] - web
        cy = s["cy0"] if hy < p.v["bc_fan_cy"] else s["cy1"] - web
        parts.append(p.box(cx, cx + web, cy, cy + web, top - r.seat_t, top))
    along, out, thick = r.ear
    for ex in r.ear_x:
        parts += [p.box(ex - along / 2, ex + along / 2, y0 - out, y0 + INTO, top - thick, top),
                  p.box(ex - along / 2, ex + along / 2, y1 - INTO, y1 + out, top - thick, top)]
    base = parts[0].fuse(parts[1:]).removeSplitter()
    holes = [p.rod(hx, hy, post0 - PAST, top + PAST, oj.insert_hole_d) for hx, hy in fan_holes(p)]
    for ex in r.ear_x:
        holes += [p.rod(ex, y0 - out / 2, top - thick - PAST, top + PAST, r.ear_hole), p.rod(ex, y1 + out / 2, top - thick - PAST, top + PAST, r.ear_hole)]
    return base.cut(holes)


def shroud_top(r: Rear, p: Place) -> Part.Shape:
    """The upper part of the shroud: the plate under the fan with its opening, closed over the corner with no fins,
    and the collar round the fan. The rim of the collar and the face of the fan are the land of the door seal."""
    s = shroud_lines(r, p)
    t = r.shell_t
    y0, y1 = s["cy0"] - t, s["cy1"] + t
    seat = p.box(s["x0"], s["x1"], y0, y1, s["seat0"], s["fan0"])
    collar = p.box(s["x0"], s["x1"], y0, y1, s["fan0"], s["fan1"]).cut(p.box(s["cx0"], s["cx1"], s["cy0"], s["cy1"], s["fan0"] - PAST, s["fan1"] + PAST))
    top = seat.fuse(collar).removeSplitter()
    nx0, _, _, ny1 = r.notch
    bore = p.rod(p.v["bc_fan_cx"], p.v["bc_fan_cy"], s["seat0"] - PAST, s["fan0"] + PAST, r.fan_vent_d)
    bore = bore.cut(p.box(nx0 - r.fence_t, s["x1"], s["fy0"] - PAST, ny1 + r.fence_t, s["seat0"] - 2 * PAST, s["fan0"] + 2 * PAST))
    holes = [p.rod(hx, hy, s["seat0"] - PAST, s["fan0"] + PAST, p.v["fan_hole_d"]) for hx, hy in fan_holes(p)]
    return top.cut([bore, *holes])


def fan(r: Rear, p: Place) -> Part.Shape:
    """The fan as a frame with its bore and its hub (bought)."""
    s, v = shroud_lines(r, p), p.v
    half = v["fan_frame"] / 2
    body = p.box(v["bc_fan_cx"] - half, v["bc_fan_cx"] + half, v["bc_fan_cy"] - half, v["bc_fan_cy"] + half, s["fan0"], s["fan1"])
    bore = p.rod(v["bc_fan_cx"], v["bc_fan_cy"], s["fan0"] - PAST, s["fan1"] + PAST, r.fan_vent_d)
    holes = [p.rod(hx, hy, s["fan0"] - PAST, s["fan1"] + PAST, v["fan_hole_d"]) for hx, hy in fan_holes(p)]
    hub = p.rod(v["bc_fan_cx"], v["bc_fan_cy"], s["fan0"] + 2.0, s["fan1"] - 2.0, 40.0)
    return Part.makeCompound([body.cut([bore, *holes]), hub])


def duct_lines(r: Rear, p: Place) -> dict[str, float]:
    v = p.v
    return {"x0": -v["bc_dp_clear"] - v["bc_io_overhang"], "x1": v["bc_hood_x1"], "y0": v["bc_shroud_y0"], "y1": v["bc_shroud_y0"] + v["bc_shroud_w"],
            "top": v["bc_shroud_h"], "fin": v["bc_fin_h"],
            "fy0": v["bc_fin_y0"] - r.fin_clear, "fy1": v["bc_fin_y0"] + v["bc_fin_w"] + r.fin_clear}


def duct_body(r: Rear, p: Place) -> Part.Shape:
    """The duct without its back wall: the floor in front of the board's edge, the end wall and the two side walls,
    open to the door. The lower side wall has the notch for the cables of the I/O end."""
    k, t = duct_lines(r, p), r.shell_t
    floor = p.box(k["x0"], -r.duct_floor_gap, k["y0"], k["y1"], -t, 0.0)
    end = p.box(k["x0"], k["x0"] + t, k["y0"], k["y1"], -t, k["top"])
    sides = [p.box(k["x0"], k["x1"], k["y0"], k["y0"] + t, -t, k["top"]), p.box(k["x0"], k["x1"], k["y1"] - t, k["y1"], -t, k["top"])]
    body = floor.fuse([end, *sides]).removeSplitter()
    nx0, nx1, nh = r.cable_notch
    c = r.cable_notch_cut
    notch = [(nx0, 0.0), (nx1, 0.0), (nx1, nh - c), (nx1 - c, nh), (nx0 + c, nh), (nx0, nh - c)]
    face = Part.Face(Part.makePolygon([V(p.x(x), p.y(z), p.z(k["y0"] - PAST)) for x, z in [*notch, notch[0]]]))
    return body.cut(face.extrude(V(0, 0, t + 2 * PAST)))


def duct_back(r: Rear, p: Place) -> Part.Shape:
    """The back wall of the duct: a flat plate between the side walls, with the cut-out for the fin block. It
    stands on the fin tops with foam under it."""
    k, t = duct_lines(r, p), r.shell_t
    wall = p.box(k["x1"] - t, k["x1"], k["y0"] + t, k["y1"] - t, r.pcb_clear, k["top"])
    return wall.cut(p.box(k["x1"] - t - PAST, k["x1"] + PAST, k["fy0"], k["fy1"], r.pcb_clear - PAST, k["fin"] + r.fin_foam))


def seals(d: Blueprint, r: Rear, p: Place) -> dict[str, Part.Shape]:
    """The foam between the compute module and the door: a ring on the collar and the fan, a strip on the rim of the
    duct. Each fills the gap to the inner face of the door."""
    s, k, t = shroud_lines(r, p), duct_lines(r, p), r.shell_t
    door = d.body_d - d.wall_t - p.bc_y  # the inner face of the door above the PCB
    ring = p.box(s["x0"], s["x1"], s["cy0"] - t, s["cy1"] + t, s["fan1"], door).cut(
        p.rod(p.v["bc_fan_cx"], p.v["bc_fan_cy"], s["fan1"] - PAST, door + PAST, r.fan_vent_d))
    strip = p.box(k["x0"], k["x1"], k["y0"], k["y1"], k["top"], door).cut(
        p.box(k["x0"] + t, k["x1"] - t, k["y0"] + t, k["y1"] - t, k["top"] - PAST, door + PAST))
    return {"seal_fan": ring, "seal_duct": strip}


def build(d: Blueprint, r: Rear, p: Place) -> dict[str, Part.Shape]:
    """Every part of the rear that is a part of its own, by name."""
    out = {}
    for side, s in SIDES.items():
        out[f"door_half_{s.lower()}"] = door_half(d, r, p, side)
        out[f"head_rail_{s.lower()}"] = head_rail(d, r, side)
    out.update({"shroud_base": shroud_base(r, p), "shroud_top": shroud_top(r, p), "fan": fan(r, p),
                "duct_body": duct_body(r, p), "duct_back": duct_back(r, p)}, **seals(d, r, p))
    return out


# ---------- the pieces of the split, finished ----------

def one_solid(shape: Part.Shape, what: str) -> Part.Shape:
    if shape.isNull() or not shape.isValid() or len(shape.Solids) != 1:
        raise Part.OCCError(f"{what}: the result is not one valid solid ({0 if shape.isNull() else len(shape.Solids)} solids)")
    return shape.Solids[0]


def broken(piece: Part.Shape, a: tuple[float, float, float], b: tuple[float, float, float], n2: tuple[float, float, float],
           radius: float, what: str) -> Part.Shape:
    """The piece with the edge break on the straight edge a-b of its outer face (the face that looks to the rear);
    n2 is the outward normal of the other face of the edge."""
    tool = so.edge_round_cutter(V(*a), V(*b), V(0, 1, 0), V(*n2), radius)
    full = (1 - math.pi / 4) * radius ** 2 * V(*a).distanceToPoint(V(*b))
    out = piece.cut(tool)
    # one cut is enough when it takes what the round takes off the edge (the tool is a little longer than the edge);
    # if OpenCascade skips it, the cut is made near the tool
    if out.isNull() or not out.isValid() or len(out.Solids) != 1 or not 0.5 * full < piece.Volume - out.Volume <= full + 1e-3:
        out = so.cut_near(piece, [tool], what)
    return one_solid(out, what)


def with_openings(piece: Part.Shape, faces: list[Part.Face], screws: list[P2], d: Blueprint, r: Rear, what: str) -> Part.Shape:
    """A piece of the lower rear wall with the openings cut through it, the edge break on the rim of each one on the
    outer face, and the chamfered holes of the screws."""
    y_out, y_in = d.body_d, d.body_d - d.wall_t
    cut = one_solid(piece.cut([through(f, y_in - 2 * PAST, y_out + PAST) for f in faces]), what)
    x0, x1, z0, z1 = field(faces)
    inside = lambda e: x0 - 0.1 < e.BoundBox.Center.x < x1 + 0.1 and z0 - 0.1 < e.BoundBox.Center.z < z1 + 0.1
    rim = [e for e in cut.Edges if on_outer(e, y_out) and inside(e) and e.BoundBox.XMin > x0 - 0.1 and e.BoundBox.XMax < x1 + 0.1]
    out = one_solid(cut.makeFillet(d.edge_break, rim), f"{what}, the edge break of the openings")
    if screws:
        out = one_solid(out.cut([t for x, z in screws for t in chamfered_hole(x, z, r.psu_screw_hole, y_in - PAST, y_out)]), f"{what}, the screw holes")
    return out


# the pieces of the split that the rear changes, and those already finished in this process
CHANGED = ("rear lower", "middle", "upper rear", "door half")
_FINISHED: dict[tuple, Part.Shape] = {}


def finish_pieces(shapes: dict[str, Part.Shape], d: Blueprint, r: Rear | None = None, p: Place | None = None,
                  log=lambda line: None) -> dict[str, Part.Shape]:
    """The pieces of the split with the rear on them. The two door halves are the designed halves. The rear lower
    pieces get the openings of the lower wall, the edge break on the sill and the lip. The middle pieces get the
    edge break on the side of the opening, the tongue and the post. The upper rear pieces get the edge break on the
    head of the opening. A piece that the dictionary does not hold is left out."""
    r, p = r or Rear(), p or place(d)
    f, k = frame(d, r), split.KERF / 2
    # the finished pieces are kept for the process: the split and the checks of the rear ask for the same ones
    key = lambda name: (name, split.fingerprint(d), r, p.psu_x1, p.psu_z0, p.bc_x0, p.bc_y, p.bc_z0, tuple(sorted(p.v.items())),
                        round(shapes[name].Volume, 3), len(shapes[name].Faces))
    keys = {name: key(name) for name in shapes if name.startswith(CHANGED)}
    if keys and all(q in _FINISHED for q in keys.values()):
        return {**shapes, **{name: _FINISHED[q] for name, q in keys.items()}}
    out = dict(shapes)
    low = supply_openings(r, p)
    holes = {-1: ([o for v in low.values() for o in v], supply_screws(r, p)), 1: (inlet(r, p), [])}
    for side, s in SIDES.items():
        end = side * (f.x_open + d.edge_break)
        name = f"rear lower {s}"
        if name in out:
            piece = with_openings(out[name], *holes[side], d, r, name)
            piece = broken(piece, (0.0, f.y_out, f.z0 - k), (end, f.y_out, f.z0 - k), (0, 0, 1), d.edge_break, f"{name}, the edge break of the sill")
            out[name] = one_solid(piece.fuse(sill_lip(d, r, p, side)), f"{name}, the lip and the rib under the sill")
            log(f"rear: {name}: {len(holes[side][0])} openings, the edge break of the sill, the lip and the rib under the sill")
        name = f"middle {s}"
        if name in out:
            x = side * (f.x_open + k)
            piece = broken(out[name], (x, f.y_out, f.z0 + k), (x, f.y_out, f.z1 + d.edge_break), (-side, 0, 0), d.edge_break, f"{name}, the edge break of the opening's side")
            # the cut left the face of the opening's side and the face of seam R1 above it as two faces of one plane;
            # they are made one, so that no line crosses the side of the opening at its top corner
            out[name] = one_solid(piece.fuse(side_tongue(d, r, side)).removeSplitter(), f"{name}, the tongue and the post")
            log(f"rear: {name}: the edge break of the opening's side, the tongue and the post")
        name = f"upper rear {s}"
        if name in out:
            out[name] = broken(out[name], (0.0, f.y_out, f.z1 + k), (end, f.y_out, f.z1 + k), (0, 0, -1), d.edge_break, f"{name}, the edge break of the opening's head")
            log(f"rear: {name}: the edge break of the opening's head")
        name = f"door half {s}"
        if name in out:
            out[name] = door_half(d, r, p, side)
    _FINISHED.update({q: out[name] for name, q in keys.items()})
    return out


# ---------- the checks ----------

# the boxes of the fit study that the real parts stand in for
REPLACED = {"Compute_FanShroud": ("shroud_base", "shroud_top", "fan"), "Compute_ExhaustDuct": ("duct_body", "duct_back")}
# make-up air for the power supply (structure.makeup_air): 25 W of loss, 10 K of rise, and three times that flow
SUPPLY_LOSS_W, AIR_RISE_K, FLOW_FACTOR = 25.0, 10.0, 3.0
INLET_SPEEDS = (1.0, 1.5)
ABS_E = 2200.0  # MPa, printed ABS in the layer plane (abs-on-the-q2.md 6), for the beam estimate of the head rib


def inlet_need() -> dict[float, float]:
    """The free area of the inlet in mm2 for each air speed of INLET_SPEEDS, at the design flow."""
    flow = FLOW_FACTOR * SUPPLY_LOSS_W / (1.2 * 1005.0 * AIR_RISE_K)  # m3/s
    return {v: flow / v * 1e6 for v in INLET_SPEEDS}


def areas(r: Rear, p: Place) -> dict:
    """The open area of each vent against what it needs."""
    disc = math.pi * (r.fan_vent_d / 2) ** 2
    fan_a, hot_a, in_a = area(fan_vent(r, p)), area(hot_vent(r, p)), area(inlet(r, p))
    low = {k: area(v) for k, v in supply_openings(r, p).items()}
    need = inlet_need()
    return {"fan": {"free_mm2": fan_a, "field_mm2": disc, "share": fan_a / disc, "need_share": r.fan_open_min, "ok": fan_a / disc >= r.fan_open_min},
            "hot": {"free_mm2": hot_a, "need_mm2": r.hot_free_min, "ok": hot_a >= r.hot_free_min},
            "inlet": {"free_mm2": in_a, "need_mm2": {f"{v:g} m/s": a for v, a in need.items()}, "speed_m_s": max(need.values()) * min(need) / in_a,
                      "ok": in_a >= need[min(need)]},
            "supply": {**{f"{k}_mm2": a for k, a in low.items()},
                       "grille_share_of_vent": low["grille"] / ((r.grille_slots * r.pitch - r.bar) * (r.low_v1 - r.low_v0))}}


def fit_rows(d: Blueprint, lay, found: list, walls: list[Part.Shape]) -> list[tuple[str, str, str]]:
    """The rule "rear parts" of the fit study: the real parts in place of the boxes. No rear part has a common volume
    with a solid or a keep-out zone of the hardware (the two boxes that they stand in for left out); the shroud, the
    fan and the duct do not lie in the skin and keep to the columns of their boxes; they and the board pass the clear
    opening of the door; the blocks of the fasteners stand clear of the board's way out; the vents lie on the fan and
    inside the duct; and the floor stays free for the lead of the power button."""
    from . import fit  # noqa: PLC0415

    r = Rear()
    try:
        p = place(d, lay)
        parts = build(d, r, p)
        land = {f"sill_lip_{s.lower()}": sill_lip(d, r, p, side) for side, s in SIDES.items()}
        land.update({f"side_tongue_{s.lower()}": side_tongue(d, r, side) for side, s in SIDES.items()})
    except (Part.OCCError, ValueError) as ex:
        return [(check.FAIL, "rear parts", f"they cannot be made at this layout: {str(ex).splitlines()[0][:160]}")]
    f = frame(d, r)
    everything = {**parts, **land}
    solids = [s for it in found for s in it.solids if s.role in fit.ENVELOPE and s.name not in REPLACED]
    rows = []
    for name, shape in everything.items():
        for s in solids:
            if shape.BoundBox.intersect(s.world.BoundBox) and (vol := shape.common(s.world).Volume) > fit.TOL:
                rows.append((check.FAIL, f"{name} / {s.name}", f"{vol:.0f} mm3 in common"))
    names = list(everything)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if everything[a].BoundBox.intersect(everything[b].BoundBox) and (vol := everything[a].common(everything[b]).Volume) > fit.TOL:
                rows.append((check.FAIL, f"{a} / {b}", f"{vol:.0f} mm3 in common"))
    if not rows:
        rows.append((check.PASS, f"{len(everything)} rear parts", f"no common volume with {len(solids)} solids and keep-out zones of the hardware, "
                     "and none with each other"))
    hard = [n for names in REPLACED.values() for n in names]
    buried = [(n, v) for n in hard if (v := fit.in_skin(parts[n], walls)) > fit.TOL]
    rows += [(check.FAIL, n, f"{v:.0f} mm3 lies in the skin") for n, v in buried] or [(check.PASS, "shroud, fan and duct", "no volume in the skin")]
    boxes = {s.name: s.world.BoundBox for it in found for s in it.solids if s.name in REPLACED}
    ears = 4 * r.ear[0] * r.ear[1] * r.ear[2]
    clear = (-f.x_ring, f.x_ring, f.z_lip, f.z_rail0)
    for box_name, names in REPLACED.items():
        if box_name not in boxes:
            continue
        b = boxes[box_name]
        column = box(b.XMin - 1e-6, b.XMax + 1e-6, p.bc_y - r.shell_t - 1e-6, b.YMax + 1e-6, b.ZMin - 1e-6, b.ZMax + 1e-6)
        outside = sum(parts[n].cut(column).Volume for n in names)
        allow = ears if "shroud_base" in names else 0.0
        rows.append((check.PASS if outside <= allow + fit.TOL else check.FAIL, f"{box_name}: the real parts",
                     f"{outside:.0f} mm3 stands outside the column of the box (its sides and its face to the door); allowed {allow:.0f} (the ears to the carrier)"))
        bb = Part.makeCompound([parts[n] for n in names]).BoundBox
        ok = clear[0] <= bb.XMin and bb.XMax <= clear[1] and bb.ZMax <= clear[3]
        rows.append((check.PASS if ok else check.FAIL, f"{box_name}: the real parts in the clear opening",
                     f"x {bb.XMin:.1f} to {bb.XMax:.1f}, z {bb.ZMin:.1f} to {bb.ZMax:.1f}; clear opening x {clear[0]:.1f} to {clear[1]:.1f}, under the head rail "
                     f"at z {clear[3]:.1f}; the lip stands to z {clear[2]:.1f}, so the part lifts {max(0.0, clear[2] - bb.ZMin):.1f} over it"))
    v = p.v
    board = (p.x(0.0), p.x(v["bc_pcb_l"]), p.z(0.0), p.z(v["bc_pcb_w_pwr"]))
    ok = clear[0] <= board[0] and board[1] <= clear[1] and clear[2] <= board[2] and board[3] <= clear[3]
    rows.append((check.PASS if ok else check.FAIL, "board in the clear opening", f"x {board[0]:.1f} to {board[1]:.1f}, z {board[2]:.1f} to {board[3]:.1f}; "
                 f"clear opening x {clear[0]:.1f} to {clear[1]:.1f}, z {clear[2]:.1f} to {clear[3]:.1f}"))
    step = p.x(v["bc_pcb_step_x"])
    for side, s in SIDES.items():
        a, b_ = sorted((side * f.x_block0, side * f.x_rail1))
        tops = [top for x0, x1, top in ((board[0], step, p.z(v["bc_pcb_w_io"])), (step, board[1], board[3])) if x0 < b_ and a < x1]
        ok = max(tops, default=-math.inf) <= f.z_block0
        rows.append((check.PASS if ok else check.FAIL, f"block of the fastener {s}", f"x {a:.1f} to {b_:.1f}, down to z {f.z_block0:.1f}; "
                     + (f"the board under it reaches z {max(tops):.1f}" if tops else "no part of the board is under it")))
    fx0, fx1, fz0, fz1 = field(fan_vent(r, p))
    cx, cz, rad = p.x(v["bc_fan_cx"]), p.z(v["bc_fan_cy"]), r.fan_vent_d / 2
    ok = cx - rad - 1e-6 <= fx0 and fx1 <= cx + rad + 1e-6 and fx1 < f.x_step and fx0 > r.seam_rib_w
    rows.append((check.PASS if ok else check.FAIL, "fan vent", f"x {fx0:.1f} to {fx1:.1f}, z {fz0:.1f} to {fz1:.1f}: on the circle of the fan "
                 f"(centre x {cx:.2f}, z {cz:.2f}, diameter {2 * rad:g}), whole in the right half"))
    hx0, hx1, hz0, hz1 = field(hot_vent(r, p))
    dx0, dx1, dz0, dz1 = duct_inside(r, p)
    margin = min(hx0 - dx0, dx1 - hx1, hz0 - dz0, dz1 - hz1)
    ok = margin >= 0 and hx0 > -f.x_step and hx1 < -r.seam_rib_w
    rows.append((check.PASS if ok else check.FAIL, "hot-air vent", f"x {hx0:.1f} to {hx1:.1f}, z {hz0:.1f} to {hz1:.1f}: {margin:.1f} or more inside "
                 f"the duct (x {dx0:.1f} to {dx1:.1f}, z {dz0:.1f} to {dz1:.1f}), whole in the left half"))
    lowest = min(parts[n].BoundBox.ZMin for n in hard)
    top = p.psu_z0 + v["psu_h"]
    rows.append((check.PASS if lowest >= top else check.FAIL, "lead of the power button", f"no rear part stands below z {lowest:.1f} in front of the "
                 f"rear wall; the power supply ends at z {top:.1f}, so the floor from its front to the deck is free"))
    return rows


def edge_rows(d: Blueprint, r: Rear, shapes: dict[str, Part.Shape]) -> list[tuple[str, str, str]]:
    """The edge rule on the door and the openings: no convex edge on the outside turns more than edge_break_turn
    without a round. On a door half every edge that reaches the outer face counts, the centre joint left out. On a
    piece of the shell the edges on the outer face count that lie on the rim of the door's opening or in the field
    of an opening of the lower wall. The mouth of a screw hole or of the fastener's hole has the chamfer of joints,
    which turns 45 degrees twice."""
    f = frame(d, r)
    y = f.y_out
    rows = []
    for name, shape in shapes.items():
        door = name.startswith("door half")
        sharp, seen = [], 0
        for e in shape.Edges:
            if e.Degenerated or len(shape.ancestorsOfType(e, Part.Face)) != 2:
                continue
            pts = [v.Point for v in e.Vertexes] + [so.middle(e)]
            if door:
                if not any(q.y > y - 1e-3 for q in pts) or all(abs(q.x) < 1e-3 for q in pts):
                    continue
            else:
                m = so.middle(e)
                at_door = abs(m.x) < f.x_open + 0.2 and f.z0 - 0.2 < m.z < f.z1 + 0.2
                low = m.z < f.z0 - d.edge_break - 0.5 and m.z > d.base_facet + d.edge_break + 0.5 and abs(m.x) > 1.0 and abs(m.x) < d.rear_flat_x - 1.0
                if not all(q.y > y - d.edge_break - 1e-3 for q in pts) or not (at_door or low):
                    continue
            seen += 1
            convex, turn = so.edge_turn(shape, e)
            if convex and turn > d.edge_break_turn:
                m = so.middle(e)
                sharp.append((round(e.Length, 2), round(turn, 1), (round(m.x, 1), round(m.y, 1), round(m.z, 1))))
        if sharp:
            worst = sorted(sharp, reverse=True)[:3]
            rows.append((check.FAIL, name, f"{len(sharp)} sharp convex edges of {seen} on the outside, the longest {worst}"))
        else:
            rows.append((check.PASS, name, f"{seen} edges on the outside in the zone of the door and the openings: none sharp"))
    return rows


def flat_on_bed(shape: Part.Shape, up: tuple[float, float, float]) -> tuple[float, float]:
    """The flat area of a part that lies on the bed with `up` pointing up, and the area of its footprint box."""
    u = V(*up)
    u.normalize()
    pts, _ = shape.tessellate(0.5)
    low = min(q.dot(u) for q in pts)
    flat = sum(fc.Area for fc in shape.Faces if isinstance(fc.Surface, Part.Plane) and fc.normalAt(0, 0).dot(u) < -0.9999
               and abs(fc.CenterOfMass.dot(u) - low) < 0.01)
    return flat, low


PRINTS = {  # each printed part of its own: what points up on the printer, and how it lies
    "door_half_r": ((0.0, -1.0, 0.0), "outer face on the bed"), "door_half_l": ((0.0, -1.0, 0.0), "outer face on the bed"),
    "head_rail_r": ((0.0, 1.0, 0.0), "front face on the bed, the tongue on top"), "head_rail_l": ((0.0, 1.0, 0.0), "front face on the bed, the tongue on top"),
    "shroud_base": ((0.0, -1.0, 0.0), "the edge under the fan plate on the bed, the walls up"),
    "shroud_top": ((0.0, 1.0, 0.0), "the fan plate on the bed, the collar up"),
    "duct_body": ((0.0, 1.0, 0.0), "the floor and the lower edges of the side walls on the bed, open to the top"),
    "duct_back": ((1.0, 0.0, 0.0), "flat on the bed"),
}


def print_rows(parts: dict[str, Part.Shape], lim: split.Printer) -> list[dict]:
    rows = []
    over = -math.sin(math.radians(split.OVERHANG + split.OVERHANG_BAND))
    for name, (up, how) in PRINTS.items():
        shape = parts[name]
        pts, _ = shape.tessellate(0.5)
        size = split.print_box([(q.x, q.y, q.z) for q in pts], up, lim)
        flat, low = flat_on_bed(shape, up)
        u = V(*up)
        hang = 0.0
        for fc in shape.Faces:
            vs, tris = fc.tessellate(0.5)
            for a, b, c in tris:
                n = (vs[b] - vs[a]).cross(vs[c] - vs[a])
                if n.Length < 1e-9:
                    continue
                mid = (vs[a] + vs[b] + vs[c]) * (1 / 3)
                uv = fc.Surface.parameter(mid)
                out = fc.normalAt(*uv)
                if out.dot(u) < over and mid.dot(u) > low + 0.3:
                    hang += n.Length / 2
        rows.append({"part": name, "how": how, "up": list(up), "x": size["x"], "y": size["y"], "z": size["z"], "fits": size["fits"],
                     "flat_on_bed_cm2": round(flat / 100, 1), "overhang_cm2": round(hang / 100, 2),
                     "volume_cm3": round(shape.Volume / 1000, 1), "mass_g": round(shape.Volume / 1000 * split.ABS_G_PER_CM3)})
    return rows


def head_beam(d: Blueprint, r: Rear, p: Place, push: float) -> dict:
    """The head of the door as a beam between the two fasteners, with `push` N at the middle of the fan vent: the
    section is the head rib and a strip of the plate, and the load is the half of the seal's push that goes to the head."""
    strip = 40.0
    a1, c1 = strip * d.wall_t, d.wall_t / 2
    a2, c2 = r.head_rib_w * r.head_rib_d, d.wall_t + r.head_rib_d / 2
    c = (a1 * c1 + a2 * c2) / (a1 + a2)
    inertia = strip * d.wall_t ** 3 / 12 + a1 * (c - c1) ** 2 + r.head_rib_w * r.head_rib_d ** 3 / 12 + a2 * (c2 - c) ** 2
    span = 2 * r.qt_x
    a = r.qt_x - p.x(p.v["bc_fan_cx"])
    b = span - a
    return {"push_N": push, "span": span, "inertia_mm4": round(inertia), "deflection_mm": round(push * a ** 2 * b ** 2 / (3 * ABS_E * inertia * span), 2)}


def seal_push(r: Rear, p: Place, d: Blueprint) -> dict:
    """The area of the two seals on the door and their push at 5 and at 20 kPa (soft and firm foam)."""
    s = seals(d, r, p)
    gap = lambda shape: shape.BoundBox.YLength
    a = {k: shape.Volume / gap(shape) for k, shape in s.items()}
    return {"area_mm2": {k: round(v) for k, v in a.items()}, "thickness": {k: round(gap(shape), 2) for k, shape in s.items()},
            "push_N": {f"{kpa:g} kPa": round(sum(a.values()) * kpa / 1000, 1) for kpa in (5.0, 20.0)}}


# ---------- the files ----------

def hardware_boxes(d: Blueprint, p: Place) -> dict[str, Part.Shape]:
    """The compute module and the power supply as the boxes of the fit study, for the drawings."""
    v = p.v
    step, t = v["bc_pcb_step_x"], v["bc_pcb_t"]
    board = p.box(0, step, 0, v["bc_pcb_w_io"], -t, 0).fuse(p.box(step, v["bc_pcb_l"], 0, v["bc_pcb_w_pwr"], -t, 0))
    sink = p.box(v["bc_fin_x0"], v["bc_fin_x0"] + v["bc_fin_l"], v["bc_fin_y0"], v["bc_fin_y0"] + v["bc_fin_w"], 0, v["bc_fin_h"])
    io = p.box(-v["bc_io_overhang"], v["bc_fin_x0"], 0, v["bc_pcb_w_io"], 0, 23.0)
    y1 = d.body_d - d.wall_t - 0.1
    psu = box(p.psu_x1 - v["psu_w"], p.psu_x1, y1 - 150.0, y1, p.psu_z0, p.psu_z0 + v["psu_h"])
    return {"board": board, "heatsink": sink, "io": io, "psu": psu}


def body_pieces(d: Blueprint, log=print) -> dict[str, Part.Shape]:
    """The pieces of the body's skin, cut as the split cuts them. The skin comes from the cache of the split."""
    f = split.skin_files(d)["body"]
    if f.exists():
        skin = Part.Shape()
        skin.importBinary(str(f))
    else:
        skin = split.build_modules(d, log).skin["body"]
    seams, pieces = split.expanded(split.layout(d))
    shapes, problems = split.cut([s for s in seams if s.module == "body"], [q for q in pieces if q.module == "body"],
                                 split.Modules({"body": skin}, {}, {}, split.fingerprint(d)))
    if [q for q in problems if q["problem"] != "debris"]:
        raise RuntimeError(f"rear: the cut of the body has problems: {problems}")
    return shapes


def polylines(shape: Part.Shape, normal: App.Vector, at: float, axes: tuple[int, int]) -> list[list[list[float]]]:
    out = []
    for w in shape.slice(normal, at):
        out.append([[round(q[axes[0]], 3), round(q[axes[1]], 3)] for q in w.discretize(Deflection=0.03)])
    return out


FINISH = {"shell": "white", "door": "#e9e4d8", "rail": "#d8c9a8", "shroud": "#c9a15a", "duct": "#b9783a", "fan": "#30343a", "seal": "#5a7a9a",
          "board": "#4f7a3a", "heatsink": "#9aa0a8", "io": "#7a7f88", "psu": "#3a3d44", "fastener": "#8a8f99"}


def finish_of(name: str) -> str:
    for key in ("fastener", "seal", "door", "rail", "shroud", "duct", "fan"):
        if key in name:
            return FINISH[key]
    return FINISH.get(name, FINISH["shell"])


def fastener_heads(d: Blueprint, r: Rear) -> dict[str, Part.Shape]:
    """The heads of the two quarter-turn fasteners, for the renders: a disc of the largest head with a slot. The
    bought part sets the true head."""
    f = frame(d, r)
    out = {}
    for side, s in SIDES.items():
        head = Part.makeCylinder(r.qt_head / 2, 2.5, V(side * r.qt_x, f.y_out, f.zq), V(0, 1, 0))
        slot = box(side * r.qt_x - r.qt_head / 2 + 2.0, side * r.qt_x + r.qt_head / 2 - 2.0, f.y_out + 1.5, f.y_out + 3.0, f.zq - 0.8, f.zq + 0.8)
        out[f"fastener_{s.lower()}"] = head.cut(slot)
    return out


def write_model(folder: Path, shapes: dict[str, Part.Shape], focus: dict) -> None:
    """A model directory for tools/render_views.py: a mesh of each shape, the manifest, every BREP edge, the cameras."""
    folder.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, shape in shapes.items():
        f = name.replace(" ", "_")
        MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.08, AngularDeflection=0.12).write(str(folder / f"{f}.stl"))
        manifest[name] = {"file": f"{f}.stl", "finish": finish_of(name)}
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    (folder / "focus.json").write_text(json.dumps(focus, indent=1), encoding="utf-8")
    (folder / "edges.json").write_text(json.dumps({k: so.edge_polylines(s) for k, s in shapes.items()}), encoding="utf-8")


def focus(d: Blueprint, r: Rear, p: Place) -> dict:
    """The close-up cameras of the rear."""
    f = frame(d, r)
    z0, z1 = low_z(r, p)
    mid = (z0 + z1) / 2
    cam = lambda x, y, z, rad, az, el, aspect=0.7: {"target": [x, y, z], "radius": rad, "az": az, "el": el, "aspect": aspect}
    return {"closeup-rear-door": cam(0.0, f.y_out, f.z1 / 2 + 15, 250.0, 180.0, 4.0, 0.74),
            "closeup-door-right": cam(120.0, f.y_out, (f.z0 + f.z1) / 2, 125.0, 152.0, 12.0, 0.8),
            "closeup-door-left": cam(-120.0, f.y_out, (f.z0 + f.z1) / 2, 125.0, -152.0, 12.0, 0.8),
            "closeup-fastener": cam(r.qt_x, f.y_out, f.zq - 8, 42.0, 150.0, 14.0, 0.8),
            "closeup-sill": cam(150.0, f.y_out, f.z0, 45.0, 150.0, 24.0, 0.8),
            "closeup-supply": cam(p.psu_x1 - p.v["psu_w"] / 2, f.y_out, mid, 95.0, -160.0, 6.0, 0.7),
            "closeup-inlet": cam(-p.psu_x1 + p.v["psu_w"] / 2, f.y_out, mid, 95.0, 160.0, 6.0, 0.7),
            "closeup-door-inside": cam(60.0, f.y_in - 20, (f.z0 + f.z1) / 2 + 30, 150.0, 28.0, 14.0, 0.8),
            "closeup-rail-inside": cam(r.qt_x - 20, f.y_in - 10, f.zq, 60.0, 28.0, -12.0, 0.8)}


def reveals(d: Blueprint, r: Rear, p: Place, parts: tuple[str, ...]) -> list:
    """The named reveals of the rear for the face check: the gap round the door, which is door_gap wide and
    margin_t deep, and the mouths of the holes under a fastener's head or a screw's head."""
    from tools import face_check  # noqa: PLC0415

    f = frame(d, r)
    # the gap, and the edge break on each side of it: the ball at an outer corner of the door, where the breaks of
    # two rims and of the corner edge meet, lies in it
    y0, y1, e = f.y_lap - 0.1, f.y_out + 0.1, d.edge_break + 0.2
    gap = ("sliver", "needle", "crowded")
    out = [face_check.Reveal("gap round the rear door, sill", parts, gap, (-f.x_open - e, y0, f.z0 - e, f.x_open + e, y1, f.zd0 + e)),
           face_check.Reveal("gap round the rear door, head", parts, gap, (-f.x_open - e, y0, f.zd1 - e, f.x_open + e, y1, f.z1 + e))]
    for s in SIDES:
        x0, x1 = sorted((s * (f.x_door - e), s * (f.x_open + e)))
        out.append(face_check.Reveal("gap round the rear door, side", parts, gap, (x0, y0, f.z0 - e, x1, y1, f.z1 + e)))
        out.append(face_check.Reveal("mouth of the fastener's hole, under its head", parts, ("sliver",),
                                     (s * r.qt_x - r.qt_flat / 2, y0, f.zq - r.qt_flat / 2, s * r.qt_x + r.qt_flat / 2, y1, f.zq + r.qt_flat / 2)))
    for x, z in supply_screws(r, p):
        out.append(face_check.Reveal("mouth of a screw hole of the supply, under the screw's head", parts, ("sliver",),
                                     (x - r.psu_screw_hole, y0, z - r.psu_screw_hole, x + r.psu_screw_hole, y1, z + r.psu_screw_hole)))
    return out


def face_rows(d: Blueprint, r: Rear, p: Place, shapes: dict[str, Part.Shape]) -> list[tuple[str, str, str]]:
    """The face check (tools/face_check.py) on the rear. A head rail is checked whole. A door half and a piece of the
    shell are checked where they show from behind: from the plane of the lap outward, and for a piece of the shell
    only at the door's opening and in the fields of the openings of the lower wall (the rest of a piece is the skin
    of the form, with the steps of the cavity inside, and a cut face is not seen). A finding passes when it is a
    round of the edge break or lies in a named reveal of the rear."""
    from tools import face_check  # noqa: PLC0415

    f = frame(d, r)
    allow = reveals(d, r, p, tuple(shapes))
    low = supply_openings(r, p)
    fields = [field([o for v in low.values() for o in v]), field(inlet(r, p))]
    rows = []
    for name, shape in shapes.items():
        found = face_check.check(shape, name, allow, break_radius=d.edge_break)
        if "rail" in name:
            mine = found
        elif "door" in name:
            mine = [x for x in found if x.at[1] > f.y_lap - 0.1]
        else:
            at_door = lambda a: abs(a[0]) < f.x_open + 0.2 and f.z0 - d.edge_break - 0.2 < a[2] < f.z1 + d.edge_break + 0.2
            in_field = lambda a: any(x0 - 1.5 < a[0] < x1 + 1.5 and z0 - 1.5 < a[2] < z1 + 1.5 for x0, x1, z0, z1 in fields)
            mine = [x for x in found if x.at[1] > f.y_lap - 0.1 and (at_door(x.at) or in_field(x.at))]
        bad = face_check.failures(mine)
        if bad:
            kinds = sorted({x.rule for x in bad})
            rows.append((check.FAIL, name, f"{len(bad)} findings ({', '.join(kinds)}), the first at {bad[0].at}: {bad[0].detail}"))
        else:
            by = {}
            for x in mine:
                if x.allowed:
                    by[x.allowed] = by.get(x.allowed, 0) + 1
            rows.append((check.PASS, name, "no finding that fails" + ("; allowed: " + ", ".join(f"{n} ({k})" for k, n in sorted(by.items())) if by else "")))
    return rows


def sections(d: Blueprint, r: Rear, p: Place, parts: dict[str, Part.Shape], pieces: dict[str, Part.Shape]) -> dict:
    """The sections and the outlines for the drawings of tools/draw_rear.py."""
    f = frame(d, r)
    hw = hardware_boxes(d, p)
    everything = {**pieces, **parts, **hw}
    cx, cz = p.x(p.v["bc_fan_cx"]), p.z(p.v["bc_fan_cy"])
    hot = field(hot_vent(r, p))
    z0, z1 = low_z(r, p)
    planes = {"plan through the fan vent and the duct": (2, cz + 12.0), "plan through the lower wall": (2, (z0 + z1) / 2),
              "side through the fan vent": (0, cx), "side through the fastener": (0, r.qt_x), "side through the cone": (0, f.x_cone),
              "side through the duct": (0, (hot[0] + hot[1]) / 2)}
    out = {"sections": {}, "frame": asdict(f), "values": asdict(r)}
    for title, (axis, at) in planes.items():
        normal = V(*(1.0 if k == axis else 0.0 for k in range(3)))
        axes = (0, 1) if axis == 2 else (1, 2)
        cut = {}
        for name, shape in everything.items():
            bb = shape.BoundBox
            lo, hi = (bb.XMin, bb.XMax) if axis == 0 else (bb.ZMin, bb.ZMax)
            if lo - 1 <= at <= hi + 1 and (lines := polylines(shape, normal, at, axes)):
                cut[name] = lines
        out["sections"][title] = {"axis": "xyz"[axis], "at": round(at, 3), "parts": cut}
    outline = lambda faces: [[[round(q.x, 3), round(q.z, 3)] for q in w.discretize(Deflection=0.03)] for fc in faces for w in fc.Wires]
    low = supply_openings(r, p)
    u = lambda a: p.psu_x1 - a
    out["rear"] = {"door": [-f.x_door, f.x_door, f.zd0, f.zd1], "opening": [-f.x_open, f.x_open, f.z0, f.z1], "ring": [-f.x_ring, f.x_ring, f.z_lip, f.z_head],
                   "fan_vent": outline(fan_vent(r, p)), "hot_vent": outline(hot_vent(r, p)), "inlet": outline(inlet(r, p)),
                   "supply": {k: outline(v) for k, v in low.items()}, "screws": supply_screws(r, p), "screw_hole": r.psu_screw_hole,
                   "fasteners": [[s * r.qt_x, f.zq] for s in SIDES], "cones": [[s * f.x_cone, f.z_cone] for s in SIDES],
                   "psu_face": [u(p.v["psu_w"]), u(0.0), p.psu_z0, p.psu_z0 + p.v["psu_h"]],
                   "psu_features": {"IEC C14 inlet": [u(119.0), u(88.0), p.psu_z0 + 34.0, p.psu_z0 + 57.0], "rocker": [u(142.0), u(128.0), p.psu_z0 + 35.0, p.psu_z0 + 55.0],
                                    "ECO switch": [u(142.0), u(128.0), p.psu_z0 + 21.0, p.psu_z0 + 31.0], "vent (mainly)": [u(88.0), u(0.0), p.psu_z0, p.psu_z0 + p.v["psu_h"]]},
                   "psu_led": [u(102.5), p.psu_z0 + 66.0],
                   "fan": [cx, cz, r.fan_vent_d], "duct_inside": list(duct_inside(r, p)), "cut_ins": [d.cut_in_x, d.cut_in_z0, d.cut_in_pitch, d.cut_in_h, d.cut_in_count],
                   "rear_half": d.rear_w / 2, "shelf": d.rear_shelf_z0}
    return out


def fit_report(out: Path) -> dict | None:
    """The rules "rear parts" and "door service" of the fit study, when its report is in the output directory."""
    f = out.parent / "fit" / "report.json"
    if not f.exists():
        return None
    rules = json.loads(f.read_text(encoding="utf-8")).get("rules", {})
    return {k: rules[k] for k in ("rear parts", "door service") if k in rules} or None


def run(d: Blueprint, r: Rear, p: Place, out: Path, log=print) -> dict:
    """Build the rear, check it and write its files into out: parts/ (BREP and STL of each part and of the finished
    pieces), model-on/ and model-off/ (for the renders), sections.json, report.json and report.md."""
    out.mkdir(parents=True, exist_ok=True)
    lim, f = split.printer(), frame(d, r)
    parts = build(d, r, p)
    done = finish_pieces(body_pieces(d, log), d, r, p, log)
    doors = {k: v for k, v in done.items() if k.startswith("door half")}
    near = {k: v for k, v in done.items() if k.startswith(("rear lower", "middle", "upper rear"))}
    up = {q.full: q.up for q in split.expanded(split.layout(d))[1]}
    pieces = {k: split.measure(v, up[k], lim, None, None, d, detail=False) for k, v in {**doors, **near}.items()}
    push = seal_push(r, p, d)
    rep = {"values": asdict(r), "frame": asdict(f), "place": {"psu_x1": p.psu_x1, "psu_z0": p.psu_z0, "bc_x0": p.bc_x0, "bc_y": p.bc_y, "bc_z0": p.bc_z0},
           "areas": areas(r, p), "print": print_rows(parts, lim), "pieces": pieces,
           "rules": {"edge rule": edge_rows(d, r, {**doors, **near}),
                     "face check": face_rows(d, r, p, {**doors, **{k: parts[k] for k in ("head_rail_r", "head_rail_l")}, **near})},
           "seal": push, "beam": [head_beam(d, r, p, v / 2) for v in push["push_N"].values()], "fit": fit_report(out),
           "fastener": {"x": r.qt_x, "z": f.zq, "door_hole": r.qt_hole, "largest_head": r.qt_head, "flat": r.qt_flat, "grip": d.wall_t + r.qt_web,
                        "web_hole": r.qt_web_hole, "room": [r.qt_pocket_w, r.qt_pocket_h, r.rail_d - r.qt_web]}}
    area_rows = [(check.PASS if a["ok"] else check.FAIL, k, f"{a['free_mm2'] / 100:.1f} cm2 free") for k, a in rep["areas"].items() if "ok" in a]
    size_rows = [(check.PASS if q["fits"] else check.FAIL, q["part"], f"{q['x']} x {q['y']} x {q['z']}") for q in rep["print"]]
    size_rows += [(check.PASS if q["fits"] else check.FAIL, k, f"{q['x']} x {q['y']} x {q['z']}") for k, q in pieces.items()]
    rep["rules"]["open area of the vents"] = area_rows
    rep["rules"]["size on the printer"] = size_rows
    rep["failures"] = [f"{title}: {subject}: {detail}" for title, rows in rep["rules"].items() for level, subject, detail in rows if level == check.FAIL]
    if rep["fit"]:
        rep["failures"] += [f"fit study, {title}: {subject}: {detail}" for title, rows in rep["fit"].items() for level, subject, detail in rows if level == check.FAIL]
    folder = out / "parts"
    folder.mkdir(exist_ok=True)
    for name, shape in {**parts, **doors, **near}.items():
        stem = name.replace(" ", "_")
        shape.exportBrep(str(folder / f"{stem}.brep"))
        MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.1, AngularDeflection=0.15).write(str(folder / f"{stem}.stl"))
    shell = {k: v for k, v in done.items() if not k.startswith("door half")}
    hw = hardware_boxes(d, p)
    cams = focus(d, r, p)
    rails = {k: parts[k] for k in ("head_rail_r", "head_rail_l")}
    write_model(out / "model-on", {**shell, **doors, **rails, **fastener_heads(d, r), "psu": hw["psu"]}, cams)
    inside = {k: parts[k] for k in ("shroud_base", "shroud_top", "fan", "duct_body", "duct_back", "seal_fan", "seal_duct")}
    write_model(out / "model-off", {**shell, **rails, **inside, **hw}, cams)
    write_model(out / "model-door", {**{k: parts[k] for k in ("door_half_r", "door_half_l", "head_rail_r", "head_rail_l")}}, cams)
    (out / "sections.json").write_text(json.dumps(sections(d, r, p, parts, {**doors, **near})), encoding="utf-8")
    (out / "report.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
    (out / "report.md").write_text(markdown(rep), encoding="utf-8")
    return rep


def markdown(rep: dict) -> str:
    a, fr, q = rep["areas"], rep["frame"], rep["fastener"]
    lines = ["# The rear: door, vents, shroud, supply opening and inlet", "", f"Result: **{'FAIL' if rep['failures'] else 'PASS'}**.", "",
             "## Open area of the vents", "", "| Vent | Free area, cm2 | Need | Result |", "| --- | --- | --- | --- |",
             f"| Fan vent (door half R) | {a['fan']['free_mm2'] / 100:.1f}, {a['fan']['share'] * 100:.1f} % of the fan's circle | {a['fan']['need_share'] * 100:.0f} % "
             f"({a['fan']['field_mm2'] * a['fan']['need_share'] / 100:.1f} cm2) | {'PASS' if a['fan']['ok'] else 'FAIL'} |",
             f"| Hot-air vent (door half L) | {a['hot']['free_mm2'] / 100:.1f} | {a['hot']['need_mm2'] / 100:.0f} cm2 | {'PASS' if a['hot']['ok'] else 'FAIL'} |",
             f"| Inlet for make-up air (rear lower R) | {a['inlet']['free_mm2'] / 100:.1f}: {a['inlet']['speed_m_s']:.2f} m/s at the design flow | "
             + ", ".join(f"{v / 100:.1f} cm2 at {k}" for k, v in a["inlet"]["need_mm2"].items()) + f" | {'PASS' if a['inlet']['ok'] else 'FAIL'} |",
             f"| Supply: grille over its vent (rear lower L) | {a['supply']['grille_mm2'] / 100:.1f}: {a['supply']['grille_share_of_vent'] * 100:.0f} % of the "
             "part of the vent behind it | no rule: the supply's fan pushes the air | - |",
             f"| Supply: opening of the socket | {a['supply']['socket_mm2'] / 100:.1f} | - | - |",
             f"| Supply: opening of the switches | {a['supply']['switch_mm2'] / 100:.1f} | - | - |", "",
             "## The door in its opening", "",
             f"Opening x +-{fr['x_open']:.2f}, z {fr['z0']:g} to {fr['z1']:g}. Door x +-{fr['x_door']:.2f}, z {fr['zd0']:g} to {fr['zd1']:g}. "
             f"Clear opening inside the land x +-{fr['x_ring']:.2f}, z {fr['z_lip']:g} (the lip) to {fr['z_rail0']:g} (the head rail).", "",
             f"Quarter-turn fasteners at x +-{q['x']:g}, z {q['z']:g}: hole in the door {q['door_hole']:g}, largest head {q['largest_head']:g} on a flat of "
             f"{q['flat']:g}, grip {q['grip']:g} (door and web), hole in the web {q['web_hole']:g}, room of the receptacle "
             f"{q['room'][0]:g} x {q['room'][1]:g} x {q['room'][2]:g}.", "",
             "Push of the two foam seals on the door, and how far the head of the door bows between the fasteners (half of the push on the head):", "",
             "| Foam | Push, N | Bow of the head, mm |", "| --- | --- | --- |"]
    lines += [f"| {k} | {v} | {b['deflection_mm']} |" for (k, v), b in zip(rep["seal"]["push_N"].items(), rep["beam"])]
    lines += ["", "## Print", "", "| Part | How it lies | X | Y | Z | Fits | Flat on the bed, cm2 | Overhang past 45 degrees, cm2 | Mass, g |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    lines += [f"| {p['part']} | {p['how']} | {p['x']} | {p['y']} | {p['z']} | {'yes' if p['fits'] else 'no'} | {p['flat_on_bed_cm2']} | {p['overhang_cm2']} | {p['mass_g']} |" for p in rep["print"]]
    lines += ["", "The pieces of the split that the rear changes, in their print orientation:", "", "| Piece | X | Y | Z | Fits | Mass, g |", "| --- | --- | --- | --- | --- | --- |"]
    lines += [f"| {k} | {p['x']} | {p['y']} | {p['z']} | {'yes' if p['fits'] else 'no'} | {p['mass_g']} |" for k, p in rep["pieces"].items()]
    lines += ["", "## Checks", "", "| Rule | Level | Subject | Detail |", "| --- | --- | --- | --- |"]
    lines += [f"| {k} | {lv} | {s} | {dt} |" for k, rows in rep["rules"].items() for lv, s, dt in rows]
    if rep["fit"]:
        lines += [f"| fit study: {k} | {lv} | {s} | {dt} |" for k, rows in rep["fit"].items() for lv, s, dt in rows]
    else:
        lines += ["", "The fit study has no report in this output directory: run candybar.shell.fit for the rule \"rear parts\"."]
    return "\n".join(lines) + "\n"


def main() -> int:
    out = Path(os.environ.get("CANDYBAR_OUT", "cad/out/shell-rev7")) / REAR
    d, r = Blueprint(), Rear()
    rep = run(d, r, place(d), out)
    print(markdown(rep))
    return 1 if rep["failures"] else 0
