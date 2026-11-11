"""Fit study: the hardware inside the outer form of the blueprint, with a skin of wall_t (docs/blueprint sheet 09).

Run headless. It exits 1 when an item fails a check:

    CANDYBAR_OUT=cad/out/shell-bp cad/candybar/freecad-run.sh candybar.shell.fit

It builds the outer form (solids.build), the cavity inside its skin (cavity.build) and the hardware. Every hardware
size comes from cad/params/*.csv through params.load, and the envelopes and keep-out zones are those of
candybar/hardware.py and candybar/panel.py; only their anchors change. The anchors come from Blueprint; the layout
choices that nothing fixes yet are the named values of Layout. The checks are rules R1 (interference), R2 (keep-out)
and R5 (button spacing) of candybar/check.py, run on these solids, and containment: the test of R3 with the cavity in
place of the outline shell. It writes into <out>/fit:
  report.md, report.json   the clearance table, the findings, the wall, the air path, the room for the speakers and
                           the marquee, and the print table
  sections.json            the sections and the rear view for sheet 09 (tools/draw_blueprint.py fit)
  cutaway/                 meshes of the near half removed, for tools/render_views.py
"""
from __future__ import annotations

import json
import math
import os
from collections import defaultdict
from dataclasses import asdict, dataclass, replace
from itertools import combinations
from pathlib import Path

import FreeCAD as App
import MeshPart
import Part

from .. import check, hardware, model, panel, params
from ..model import ORIGIN, X_AXIS, ZERO, Assembly, Pose, box, cyl
from . import cavity
from . import profiles as pr
from . import solids as so
from .dims import CHAIR_H, DESK_H, PEOPLE, SLUMP, Blueprint, eye_of

V = App.Vector
FIT = "fit"
SHEET_ROWS = "shell/fit.py"
TOL = check.VOLUME_TOLERANCE
ENVELOPE = ("hardware", "keepout")
# the depth probes for the speaker and the marquee: step of the search and the longest depth tried
PROBE_STEP = 0.5
PROBE_MAX = 200.0
# the wall is measured at points this far apart on the cavity's side faces, on every slab of this many SLAB or more
WALL_STEP = 25.0
WALL_EVERY = 8
# a ray that measures the wall starts this far outside the form
RAY = 300.0
# gaps are first looked for among the pieces this near
GAP_NEAR = 30.0
# an item that is fixed to the skin stands this far off it, so that a face on a face of the cavity does not count
# as a clash
SEAT = 0.1
# a point on the face of a cavity piece counts as inside it
SAME_POINT = 1e-6
# a sight line ends this far in front of the image, so that it does not touch the glass; hidden bands to this step
SIGHT_OFF = 0.5
SIGHT_STEP = 0.5
# the meshes of the cut-away
MESH_LINEAR, MESH_ANGULAR = 0.3, 0.1
FINISH = {"skin": "white", "plate": "black", "Monitor": "#3a4250", "Compute": "#4f7a3a", "PSU": "#8a8f99", "CableBundle": "#b08a3a",
          "Hub": "#6a4fa0", "Speaker": "#c04040", "Marquee": "#e0b040", "USB": "#3070c0", "Panel": "#303030", "Cables": "#d07020"}


@dataclass(frozen=True)
class Layout:
    """Positions and gaps that nothing fixes yet."""
    # power supply: its left face this far from the inner side wall of the rear body (as in the earlier layout)
    psu_side_gap: float = 8.0
    # stowed cables: this far right of the power supply, against the rear wall (as in the earlier layout)
    bundle_gap: float = 6.0
    # BC-250: the DisplayPort plug space ends this far from the inner side wall (3 in the earlier layout; 4 here,
    # because behind the step the cavity of this study is up to 3.4 narrower than a true offset)
    bc_side_gap: float = 4.0
    # BC-250: its lower edge this far above the clear space over the supply's fan (as in the earlier layout)
    bc_above_psu: float = 2.0
    # lever: centre from the panel centre line (as in the earlier layout), and at this share of the panel depth
    stick_x: float = -75.0
    stick_y_share: float = 0.5
    # start, coin and menu: a column at the right end of the panel, centres this far from its right edge, the
    # column centred on the panel depth at this pitch
    svc_end_gap: float = 38.0
    svc_pitch: float = 45.0
    # encoder: under the left end of the panel, this far inside the edge of the deck opening, centred on the depth
    enc_edge_gap: float = 2.0
    # USB row in the right side of the deck: the first pocket this far behind the end of the deck's front corner, so
    # that the row (147.6 long) ends before the joint of the deck and the body, 153 behind the corner
    usb_front_gap: float = 0.0
    # hub: on the floor behind the USB row, this far from the side wall of the narrower rear body (its rear plugs
    # reach behind the step) and this far behind the last socket
    hub_side_gap: float = 10.0
    hub_back_gap: float = 10.0
    # speaker: the frame of the driver stays this far inside the outline of the speaker form
    speaker_frame_margin: float = 2.0
    # rear door: the rear wall keeps a frame this wide round it; its lower edge this far below the board
    door_frame: float = 12.0
    door_overlap: float = 8.0
    # monitor cables: the channels run back from the plug space at the height of the middle of the BC-250, to the
    # air space in front of its backplate
    cable_at_board_share: float = 0.5


# ---------- the parameter sheet, with the anchors of this form ----------

def sheet_rows(params_dir: Path, values: dict[str, float]) -> list[params.Param]:
    """The rows of the parameter sheets, with the values of `values` in place of the rows of the same name, and new
    rows for the names that the sheets do not have."""
    rows = params.load(params_dir)
    known = {r.name for r in rows}
    out = [replace(r, value=repr(float(values[r.name])), status="derived", source=SHEET_ROWS) if r.name in values else r for r in rows]
    unit = {r.name: r.unit for r in rows}
    extra = [params.Param(k, repr(float(v)), "mm", "derived", "", SHEET_ROWS, "fit study", SHEET_ROWS, i + 1)
             for i, (k, v) in enumerate(values.items()) if k not in known]
    for k in values:
        if k in known and not unit[k]:
            raise params.ParamError(f"{k}: the fit study only sets values with a unit")
    return out + extra


def sheet(rows: list[params.Param], name: str) -> App.Document:
    doc = App.newDocument(name)
    params.write_sheet(doc, rows)
    return doc


def deck_side_start(d: Blueprint) -> float:
    """Where the straight right side of the deck begins behind its front corner."""
    return pr.deck_plan(d)[0].q[1]


def usb_row_start(d: Blueprint, lay: Layout, v) -> float:
    """The centre of the first socket: its pocket starts usb_front_gap behind the deck's front corner."""
    return deck_side_start(d) + lay.usb_front_gap + v(f"usb_{USB_ORDER[0].lower()}_back_w") / 2


def usb_row_z(d: Blueprint) -> float:
    """The centre line of the sockets: mid-height of the upright part of the deck's side (pc-panel-and-front-usb.md A5)."""
    return (d.deck_top - d.deck_lean_h) / 2


def anchors(d: Blueprint, lay: Layout, v, side_in: float) -> dict[str, float]:
    """The anchors and layout values of the hardware in this form, by the names of the parameter sheets. side_in is
    the inner face of the deck's right side at the USB row, as the cavity has it."""
    w = d.wall_t
    o = cavity.Openings()
    rear_y = d.body_d - w
    rear_x = d.rear_w / 2 - w
    bottom = so.on_screen(d, 0.0, d.image_s - v("mon_active_h") / 2 - v("mon_bezel_bottom"), d.mon_setback)
    psu_z0 = w + v("psu_raise")
    psu_x0 = -rear_x + lay.psu_side_gap
    bc_bottom = psu_z0 + v("psu_h") + v("psu_fan_clear") + lay.bc_above_psu
    open_x = d.panel_w / 2 - o.panel_ledge
    out = {"recline": d.recline, "mon_bottom_y": bottom.y, "mon_bottom_z": bottom.z,
           "psu_x0": psu_x0, "psu_y0": rear_y - v("psu_d_max"), "psu_z0": psu_z0,
           "bundle_x0": psu_x0 + v("psu_w") + lay.bundle_gap, "bundle_y0": rear_y - v("psu_bundle_d"),
           "bc_x0": -rear_x + v("bc_dp_clear") + v("bc_io_overhang") + lay.bc_side_gap,
           "bc_top_z": bc_bottom + v("bc_pcb_w_pwr"), "bc_pcb_y": rear_y - SEAT - v("bc_gap_door") - v("bc_shroud_h"),
           "panel_y0": d.deck_nose + d.panel_gap, "cp_top_z": d.panel_top, "deck_t": d.panel_t, "panel_d": d.panel_d, "panel_w": d.panel_w,
           "stick_x": lay.stick_x, "stick_y": lay.stick_y_share * d.panel_d,
           "enc_x": -open_x + lay.enc_edge_gap + v("enc_w") / 2, "enc_y": d.panel_d / 2}
    for j in range(panel.SERVICE_COUNT):
        out[f"svc{j + 1}_x"] = d.panel_w / 2 - lay.svc_end_gap
        out[f"fit_svc{j + 1}_y"] = d.panel_d / 2 + (j - (panel.SERVICE_COUNT - 1) / 2) * lay.svc_pitch
    out["fit_usb_x"] = side_in - SEAT
    out["fit_usb_y0"] = usb_row_start(d, lay, v)
    out["fit_usb_z"] = usb_row_z(d)
    row_end = out["fit_usb_y0"] + (len(USB_ORDER) - 1) * v("usb_pitch") + v(f"usb_{USB_ORDER[-1].lower()}_back_w") / 2
    out["fit_hub_x0"] = rear_x - lay.hub_side_gap - v("usb_hub_w")
    out["fit_hub_y0"] = row_end + lay.hub_back_gap + v("usb_hub_plug_clear")
    out["fit_hub_z0"] = w + SEAT
    centre = so.on_screen(d, 0.0, d.image_s, d.mon_setback)
    out["fit_img_y"], out["fit_img_z"] = centre.y, centre.z
    z = bc_bottom + lay.cable_at_board_share * v("bc_pcb_w_pwr")
    su, cu = d.u
    behind = d.mon_setback + v("mon_gen_t")  # the channel leaves the plug space at its back
    s = (z - d.deck_top + behind * su) / cu
    out["fit_ch_x"] = v("mon_gen_w") / 2 + v("mon_adjust") + v("mon_side_clear")
    out["fit_ch_y0"] = d.foot_y + s * su + behind * cu
    out["fit_ch_y1"] = out["bc_pcb_y"] - v("bc_backplate_drop") - v("bc_underside_gap")
    out["fit_ch_z"] = z
    return out


# ---------- the items: the earlier envelopes, and the new ones ----------

def owned(name: str, prims) -> tuple:
    return tuple(replace(p, owner=name) for p in prims)


def control_panel(count: int) -> Assembly:
    """The lever, the action buttons, the service buttons in their column and the encoder, on the panel top."""
    action = [b for b in panel.buttons(count) if b.nut_tag == panel.ACTION_NUT]
    service = [panel.Button(f"Svc{j}", f"svc{j}_x", f"fit_svc{j}_y", "svc_hole_d", "svc_rim_d", "svc_body_d", "svc_nut_d", "svc_nut_h",
                            "svc_depth", panel.SERVICE_NUT) for j in range(1, panel.SERVICE_COUNT + 1)]
    prims = (*owned("Lever", panel.LEVER), *(p for b in action + service for p in owned(b.name, b.prims())), *owned("Encoder", (panel.ENCODER,)))
    return Assembly(panel.OWNER, base=(ZERO, "panel_y0", "cp_top_z"), prims=prims)


USB_ORDER = "ACAC"


def usb_row() -> Assembly:
    """Four sockets in the right side of the deck: each body behind the inner wall face, then its cable bend."""
    prims = []
    for k, kind in enumerate(USB_ORDER):
        w, h = f"usb_{kind.lower()}_back_w", f"usb_{kind.lower()}_back_h"
        y = f"{k} * usb_pitch - {w} / 2"
        name = f"USB_{kind}{k + 1}"
        prims += owned(name, (box(f"{name}_Body", "hardware", ("usb_body_depth", w, h), ("-usb_body_depth", y, f"-{h} / 2")),
                              box(f"{name}_Bend", "keepout", ("usb_clear_depth - usb_body_depth", w, h), ("-usb_clear_depth", y, f"-{h} / 2"))))
    return Assembly("USB", base=("fit_usb_x", "fit_usb_y0", "fit_usb_z"), prims=tuple(prims))


# Any 16 inch 16:10 body, centred on the image and free to move by mon_adjust in the plane of the face: the generic
# envelope with its thickness, the clamp jaws on its top and bottom edges, the cradle behind it, and plug space on
# both side edges over the whole height. Local frame of the monitor, from the centre of the image on its front glass.
SWEPT_W = "mon_gen_w + 2 * mon_adjust"
SWEPT_H = "mon_gen_h + 2 * mon_adjust"
MONITOR_ANY = Assembly("MonitorAny", base=(ZERO, "fit_img_y", "fit_img_z"), pose=hardware.MONITOR.pose, prims=owned("Monitor", (
    box("MonitorAny_Body", "keepout", (SWEPT_W, "mon_gen_t", SWEPT_H), (f"-({SWEPT_W}) / 2", ZERO, f"-({SWEPT_H}) / 2")),
    box("MonitorAny_ClampTop", "keepout", (SWEPT_W, "mon_gen_t", "mon_clamp_edge"), (f"-({SWEPT_W}) / 2", ZERO, f"({SWEPT_H}) / 2")),
    box("MonitorAny_ClampBottom", "keepout", (SWEPT_W, "mon_gen_t", "mon_clamp_edge"), (f"-({SWEPT_W}) / 2", ZERO, f"-({SWEPT_H}) / 2 - mon_clamp_edge")),
    box("MonitorAny_Cradle", "keepout", (SWEPT_W, "cradle_t", f"{SWEPT_H} + 2 * mon_clamp_edge"), (f"-({SWEPT_W}) / 2", "mon_gen_t", f"-({SWEPT_H}) / 2 - mon_clamp_edge")),
    box("MonitorAny_PlugsLeft", "keepout", ("mon_side_clear", "mon_gen_t", SWEPT_H), (f"-({SWEPT_W}) / 2 - mon_side_clear", ZERO, f"-({SWEPT_H}) / 2")),
    box("MonitorAny_PlugsRight", "keepout", ("mon_side_clear", "mon_gen_t", SWEPT_H), (f"({SWEPT_W}) / 2", ZERO, f"-({SWEPT_H}) / 2")))))

# A cable channel from the plug space on each side back to the air space in front of the BC-250, and one across
# the cabinet there, so that a cable from the right side reaches the I/O end on the left.
MONITOR_CABLES = Assembly("MonitorCables", base=ORIGIN, prims=owned("Monitor", (
    box("MonitorCables_Left", "keepout", ("mon_cable_w", "fit_ch_y1 - fit_ch_y0", "mon_cable_w"), ("-fit_ch_x", "fit_ch_y0", "fit_ch_z - mon_cable_w / 2")),
    box("MonitorCables_Right", "keepout", ("mon_cable_w", "fit_ch_y1 - fit_ch_y0", "mon_cable_w"), ("fit_ch_x - mon_cable_w", "fit_ch_y0", "fit_ch_z - mon_cable_w / 2")),
    box("MonitorCables_Across", "keepout", ("2 * fit_ch_x", "mon_cable_w", "mon_cable_w"), ("-fit_ch_x", "fit_ch_y1 - mon_cable_w", "fit_ch_z - mon_cable_w / 2")))))

HUB = Assembly("Hub", base=("fit_hub_x0", "fit_hub_y0", "fit_hub_z0"), prims=(
    box("Hub_Body", "hardware", ("usb_hub_w", "usb_hub_l", "usb_hub_h"), ORIGIN),
    box("Hub_PlugsFront", "keepout", ("usb_hub_w", "usb_hub_plug_clear", "usb_hub_h"), (ZERO, "-usb_hub_plug_clear", ZERO)),
    box("Hub_PlugsRear", "keepout", ("usb_hub_w", "usb_hub_plug_clear", "usb_hub_h"), (ZERO, "usb_hub_l", ZERO))))

# a cylinder along +y: the local z of the assembly turned onto the depth
FIRING_FORWARD = Pose(X_AXIS, -90.0)


def speakers() -> tuple[Assembly, Assembly]:
    """The room reserved for each driver behind the speaker face: the largest that fits (see speaker_room)."""
    return tuple(Assembly(f"Speaker{side}", base=(f"{sign}fit_spk_x", "fit_spk_y", "fit_spk_z"), pose=FIRING_FORWARD,
                          prims=(cyl(f"Speaker{side}_Driver", "keepout", "fit_spk_d", "fit_spk_depth", ORIGIN),))
                 for side, sign in (("R", ""), ("L", "-")))


MARQUEE = Assembly("Marquee", base=("-fit_mq_w / 2", "fit_mq_y", "fit_mq_z0"), prims=(
    box("Marquee_Modules", "keepout", ("fit_mq_w", "mq_led_depth", "fit_mq_h"), ORIGIN),))


# ---------- the room behind the speaker face and the marquee ----------

def world(h: pr.Hood, y: float, z: float) -> tuple[float, float]:
    return h.origin[1] + y, h.origin[2] + z


def speaker_face(d: Blueprint, h: pr.Hood) -> tuple[list[tuple[float, float]], float]:
    """The right speaker form seen from the front, in (x, z) of the cabinet, and the face of the band behind it."""
    length = h.z_band_top - h.z_sill
    v0, v1 = d.speaker_foot_gap, length - d.speaker_head_gap
    leg = lambda v: h.half_width(max(h.z_sill + v, h.z_sill + d.hood_sill_corner_r), h.opening) - d.speaker_side_gap
    xi = d.logo_w / 2 + d.logo_gap
    z = lambda v: h.origin[2] + h.z_sill + v
    return [(xi, z(v0)), (leg(v0), z(v0)), (leg(v1), z(v1)), (xi, z(v1))], h.origin[1] + h.y_band_top


def largest_circle(quad: list[tuple[float, float]], steps: int = 60) -> tuple[float, float, float]:
    """The centre and radius of the largest circle inside a convex quad (a search on a grid, then round the best)."""
    edges = list(zip(quad, quad[1:] + quad[:1]))

    def inside(p):
        out = math.inf
        for (ax, az), (bx, bz) in edges:
            nx, nz = -(bz - az), bx - ax
            k = math.hypot(nx, nz)
            out = min(out, ((p[0] - ax) * nx + (p[1] - az) * nz) / k)
        return out

    xs, zs = [p[0] for p in quad], [p[1] for p in quad]
    best = (0.0, 0.0, -math.inf)
    lo, hi = (min(xs), min(zs)), (max(xs), max(zs))
    for _ in range(3):
        for i in range(steps + 1):
            for j in range(steps + 1):
                p = (lo[0] + (hi[0] - lo[0]) * i / steps, lo[1] + (hi[1] - lo[1]) * j / steps)
                r = inside(p)
                if r > best[2]:
                    best = (p[0], p[1], r)
        span = ((hi[0] - lo[0]) / steps * 2, (hi[1] - lo[1]) / steps * 2)
        lo, hi = (best[0] - span[0], best[1] - span[1]), (best[0] + span[0], best[1] + span[1])
    if best[2] <= 0:  # the quad runs the other way round
        return largest_circle(quad[::-1], steps)
    return best


def hits(shape: Part.Shape, obstacles: list[Part.Shape]) -> bool:
    bb = shape.BoundBox
    return any(o.BoundBox.intersect(bb) and shape.common(o).Volume > TOL for o in obstacles)


def deepest(make, obstacles: list[Part.Shape]) -> float:
    """The largest depth for which make(depth) meets no obstacle (bisection to PROBE_STEP)."""
    if hits(make(PROBE_STEP), obstacles):
        return 0.0
    lo, hi = PROBE_STEP, PROBE_MAX
    if not hits(make(hi), obstacles):
        return hi
    while hi - lo > PROBE_STEP:
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if hits(make(mid), obstacles) else (mid, hi)
    return lo


def marquee_box(d: Blueprint, h: pr.Hood, depth: float) -> tuple[Part.Shape, dict[str, float]]:
    w, mh = pr.marquee_window(d, h)
    y, z0 = world(h, h.y_marquee_bottom + d.wall_t + SEAT, h.z_rail_top + d.marquee_margin)
    return Part.makeBox(w, depth, mh, V(-w / 2, y, z0)), {"fit_mq_w": w, "fit_mq_h": mh, "fit_mq_y": y, "fit_mq_z0": z0}


def speaker_room(d: Blueprint, lay: Layout, h: pr.Hood, walls: list[Part.Shape], led_depth: float) -> dict[str, float]:
    """The largest round driver inside the speaker form (less the frame margin) and the depth behind the band that
    it has before it meets the skin or the marquee's light modules."""
    quad, y_face = speaker_face(d, h)
    cx, cz, r = largest_circle(quad)
    dia = 2 * (r - lay.speaker_frame_margin)
    y0 = y_face + d.wall_t + SEAT
    cylinder = lambda depth: Part.makeCylinder(dia / 2, depth, V(cx, y0, cz), V(0, 1, 0))
    mq, _ = marquee_box(d, h, led_depth)
    depth = deepest(cylinder, walls + [mq])
    # the reserved room stops one search step short of what it met
    return {"fit_spk_x": cx, "fit_spk_y": y0, "fit_spk_z": cz, "fit_spk_d": dia, "fit_spk_depth": depth - PROBE_STEP}


# ---------- the document of the items ----------

def build_items(rows: list[params.Param]) -> App.Document:
    doc = sheet(rows, "Fit")
    m = model.Model(doc, [r.name for r in rows])
    count = int(params.value(doc, "btn_count"))
    for spec in (hardware.MONITOR, MONITOR_ANY, MONITOR_CABLES, hardware.COMPUTE, hardware.PSU, hardware.CABLE_BUNDLE, control_panel(count), usb_row(), HUB, *speakers(), MARQUEE):
        m.assembly(spec)
    doc.recompute()
    return doc


# ---------- the checks ----------

def near(shape: Part.Shape, pieces: list[Part.Shape], reach: float = 0.0) -> list[Part.Shape]:
    bb = App.BoundBox(shape.BoundBox)
    bb.enlarge(reach)
    return [p for p in pieces if p.BoundBox.intersect(bb)]


def in_skin(shape: Part.Shape, obstacles: list[Part.Shape]) -> float:
    """The volume of shape inside the skin or a plate: the skin's prisms do not overlap, so the volumes add."""
    return sum(shape.common(o).Volume for o in near(shape, obstacles))


def in_cavity(point: App.Vector, cav: cavity.Cavity) -> bool:
    return any(p.isInside(point, SAME_POINT, True) for p in near(Part.Vertex(point), cav.pieces))


def gap(a: Part.Shape, pieces: list[Part.Shape], reach: float) -> tuple[float, App.Vector, App.Vector]:
    """The smallest distance from a to the pieces, with the two nearest points: first among the pieces near a, then
    farther out, up to reach."""
    best = (math.inf, None, None)
    for r in (GAP_NEAR, reach):
        for p in near(a, pieces, r):
            dist, pairs, _ = a.distToShape(p)
            if dist < best[0]:
                best = (dist, pairs[0][0], pairs[0][1])
        if best[0] <= r:
            return best
    return best


@dataclass
class Item:
    name: str
    group: str
    owner: str
    solids: list[model.Placed]

    def shape(self, roles: tuple[str, ...]) -> Part.Shape | None:
        found = [s.world for s in self.solids if s.role in roles]
        return Part.makeCompound(found) if found else None

    @property
    def body(self) -> Part.Shape:
        """What another item must keep clear of: the hardware, or the keep-out zone of an item that is only room."""
        return self.shape(("hardware",)) or self.shape(("keepout",))


GROUPS = {"Lever": "Panel", "Encoder": "Panel", "Btn": "Panel", "Svc": "Panel", "USB": "USB", "Speaker": "Speaker"}
# the monitor's owner holds the present unit, the room for any 16:10 unit and the cable channels: one item each
MONITOR_ITEMS = {"MonitorAny": "Monitor, any 16:10", "MonitorCables": "Monitor cables"}


def group_of(owner: str) -> str:
    return next((g for k, g in GROUPS.items() if owner.startswith(k)), owner)


def items(doc: App.Document) -> list[Item]:
    by_name: dict[tuple[str, str], list[model.Placed]] = defaultdict(list)
    for s in model.placed(doc):
        name = next((v for k, v in MONITOR_ITEMS.items() if s.name.startswith(k)), s.owner)
        by_name[(name, s.owner)].append(s)
    special = {MONITOR_ITEMS["MonitorAny"]: "MonitorRoom", MONITOR_ITEMS["MonitorCables"]: "Cables"}
    return [Item(name, special.get(name, group_of(owner)), owner, v) for (name, owner), v in by_name.items()]


def run_checks(doc: App.Document, found: list[Item], cav: cavity.Cavity, bezel: Part.Shape, plate: Part.Shape) -> dict:
    """R1, R2 and R5 of check.py, and containment: no solid of the hardware and no keep-out zone in the skin or in
    the bezel plate, and each one's middle inside the cavity (the test of R3). The buttons and the lever pass through
    the control panel plate; every other item must keep out of it too."""
    scene = check.Scene(doc, tuple(model.placed(doc)), ())
    rules = {"R1 interference": check._interference(scene), "R2 keep-out": check._keepout(scene), "R5 button spacing": check._button_spacing(scene)}
    contained = []
    for it in found:
        obstacles = cav.walls + [bezel] + ([] if it.group == "Panel" else [plate])
        for s in it.solids:
            if s.role not in ENVELOPE:
                continue
            if (vol := in_skin(s.world, obstacles)) > TOL:
                contained.append((check.FAIL, s.name, f"{vol:.0f} mm3 lies in the skin or a plate"))
            elif not in_cavity(s.world.BoundBox.Center, cav):
                contained.append((check.FAIL, s.name, "lies outside the form"))
    rules["containment in the cavity"] = contained or [(check.PASS, f"{sum(len(i.solids) for i in found)} solids", "the hardware and the keep-out zones lie inside the cavity")]
    return rules


def clearances(found: list[Item], cav: cavity.Cavity, rules: dict, reach: float) -> list[dict]:
    owner = {s.name: it.name for it in found for s in it.solids}
    failed = defaultdict(list)
    for title, rows in rules.items():
        for level, subject, detail in rows:
            if level == check.FAIL:
                for name in (n.strip() for n in subject.split("/")):
                    if name in owner:
                        failed[owner[name]].append(f"{title}: {subject}: {detail}")
    bodies = {it.name: it.body for it in found}
    pair = {}
    for a, b in combinations(found, 2):
        if a.owner == b.owner:
            continue
        dist, pa, pb = gap(bodies[a.name], [bodies[b.name]], reach)
        pair[(a.name, b.name)] = (dist, pa, pb)
        pair[(b.name, a.name)] = (dist, pb, pa)
    table = []
    for it in found:
        env = it.shape(ENVELOPE)
        skin = gap(env, cav.walls, reach)
        others = [(k[1], v) for k, v in pair.items() if k[0] == it.name]
        nb, (nd, pa, pb) = min(others, key=lambda kv: kv[1][0])
        point = lambda p: [round(c, 2) for c in p] if p is not None else None
        table.append({"item": it.name, "group": it.group, "skin_gap": skin[0], "skin_points": [point(skin[1]), point(skin[2])],
                      "neighbour": nb, "neighbour_gap": nd, "neighbour_points": [point(pa), point(pb)],
                      "result": check.FAIL if failed[it.name] else check.PASS, "why": failed[it.name]})
    return table


# ---------- the wall ----------

def first_hit(shapes: list[Part.Shape], start: App.Vector, direction: App.Vector) -> float:
    """How far a ray from start goes before it enters one of the shapes (inf when it meets none)."""
    n = V(direction).normalize()
    seg = Part.makeLine(start, start + n * RAY * 2)
    best = math.inf
    for s in near(seg, shapes):
        for e in seg.common(s).Edges:
            best = min(best, *((v.Point - start).dot(n) for v in e.Vertexes))
    return best


def ray_wall(parts: dict[str, Part.Shape], cav: cavity.Cavity, start: App.Vector, direction: App.Vector) -> float:
    """The wall along a ray that comes from outside the form: from where it enters the skin to where it enters the cavity."""
    return first_hit(cav.pieces, start, direction) - first_hit([parts[k] for k in cavity.SKIN], start, direction)


# ---------- the monitor: margins at the tuck and at the sweep, straight plugs ----------

# a margin at the top or the bottom of the monitor is measured from this much of its height at that end
BAND = 10.0


def ends(shape: Part.Shape, up: App.Vector) -> tuple[Part.Shape, Part.Shape, float, float]:
    """The top and the bottom BAND of a shape along up, and how far up its two ends are."""
    hi = max(v.Point.dot(up) for v in shape.Vertexes)
    lo = min(v.Point.dot(up) for v in shape.Vertexes)
    return shape.common(so.halfspace(up * (hi - BAND), up)), shape.common(so.halfspace(up * (lo + BAND), -up)), lo, hi


def monitor_margins(doc: App.Document, found: list[Item], cav: cavity.Cavity, d: Blueprint, v) -> dict:
    """The gap from the top of the monitor (at the tuck) and from its bottom (at the sweep) to the skin, for the
    present unit and for any 16:10 unit with its adjustment, clamps and plug space; and the room for straight plugs."""
    up = doc.getObject(hardware.MONITOR.name).getGlobalPlacement().Rotation.multVec(V(0, 0, 1))
    present = next(it for it in found if it.name == hardware.MONITOR.name)
    body = Part.makeCompound([s.world for s in present.solids if s.name == "Monitor_Body"])
    room = next(it for it in found if it.name == MONITOR_ITEMS["MonitorAny"]).shape(ENVELOPE)
    out = {}
    for name, shape in (("present unit", body), ("any 16:10 unit, with adjustment, clamps and plug space", room)):
        top, bottom, _, _ = ends(shape, up)
        out[name] = {"top": gap(top, cav.walls, d.width)[0], "bottom": gap(bottom, cav.walls, d.width)[0]}
    hw = d.width / 2
    swept = v("mon_gen_w") / 2 + v("mon_adjust")
    rows = []
    for where, s in (("top corners", d.image_s + v("mon_gen_h") / 2 + v("mon_adjust")), ("middle of the image", d.image_s)):
        p = so.on_screen(d, 0.0, s, d.mon_setback + v("mon_gen_t") / 2)
        inner = hw + RAY - first_hit(cav.pieces, V(hw + RAY, p.y, p.z), V(-1, 0, 0))
        rows.append({"where": where, "z": p.z, "cavity_half_width": inner,
                     "right_angle_needs": swept + v("mon_side_clear"), "straight_needs": swept + v("mon_side_clear_straight")})
    out["plugs"] = rows
    return out


# ---------- the sight line for a range of players ----------

def sight_lines(d: Blueprint, parts: dict[str, Part.Shape], v) -> list[dict]:
    """For each seated player: the angle between the sight line to the centre of the image and the screen's normal,
    and how much of the image the bezel's inner frame or the hood hides at its top and bottom edges (at the middle
    and at the corners). The lit image lies on the monitor's front glass."""
    obstacles = [s for k, s in parts.items() if k != "screen"]
    _, _, into = so.screen_frame(d)
    half_w, half_h = v("mon_active_w") / 2, v("mon_active_h") / 2
    out = []
    for person in PEOPLE:
        ey, ez = eye_of(person)
        eye = V(0, ey, ez)
        at = lambda x, s: so.on_screen(d, x, s, d.mon_setback)
        seen = lambda p: not hits_line(Part.makeLine(eye, p + (eye - p).normalize() * SIGHT_OFF), obstacles)
        centre = at(0.0, d.image_s)
        to_eye = (eye - centre).normalize()
        angle = math.degrees(math.acos(max(-1.0, min(1.0, to_eye.dot(-into)))))
        below = math.degrees(math.atan2(eye.z - centre.z, centre.y - eye.y))
        hidden = {}
        for edge, sign in (("top", 1.0), ("bottom", -1.0)):
            worst = 0.0
            for x in (0.0, -half_w, half_w):
                lo, hi = 0.0, half_h  # distance in from the edge, along the face
                if seen(at(x, d.image_s + sign * half_h)):
                    continue
                while hi - lo > SIGHT_STEP:
                    mid = (lo + hi) / 2
                    lo, hi = (lo, mid) if seen(at(x, d.image_s + sign * (half_h - mid))) else (mid, hi)
                worst = max(worst, hi)
            hidden[edge] = worst
        out.append({"person": person.name, "source": person.source, "eye_y": ey, "eye_z": ez, "to_normal_deg": angle,
                    "below_horizontal_deg": below, "distance": (eye - centre).Length, "hidden_top": hidden["top"], "hidden_bottom": hidden["bottom"],
                    "top": [at(0.0, d.image_s + half_h).y, at(0.0, d.image_s + half_h).z], "bottom": [at(0.0, d.image_s - half_h).y, at(0.0, d.image_s - half_h).z]})
    return out


def hits_line(seg: Part.Shape, obstacles: list[Part.Shape]) -> bool:
    return any(seg.common(o).Length > SAME_POINT for o in near(seg, obstacles))


def wall_probes(d: Blueprint, h: pr.Hood) -> list[tuple[str, App.Vector, App.Vector]]:
    """Named rays through the skin, each about square to the outer face it enters."""
    hw = d.width / 2
    origin, up, into = so.screen_frame(d)
    on = lambda s, x=0.0: origin + V(x, 0, 0) + up * s - into * RAY
    oy, oz = h.origin[1], h.origin[2]
    rear_arc = math.sqrt(0.5)
    return [("floor under the panel", V(0, d.deck_nose + d.panel_d / 2, -RAY), V(0, 0, 1)),
            ("deck front, centre", V(0, -RAY, (d.deck_top - d.deck_lean_h) / 2), V(0, 1, 0)),
            ("deck side at the USB row", V(hw + RAY, deck_side_start(d) + d.panel_d / 2, (d.deck_top - d.deck_lean_h) / 2), V(-1, 0, 0)),
            ("deck top, beside the panel", V(hw - d.rail_t, d.deck_nose + d.panel_d / 2, d.deck_top + RAY), V(0, 0, -1)),
            ("side, below the tuck", V(hw + RAY, (d.foot_y + d.step_y0) / 2, d.tuck_z0 / 2), V(-1, 0, 0)),
            ("side, in the tuck", V(hw + RAY, (d.seam_y + d.body_d) / 2, (d.tuck_z0 + d.body_top) / 2), V(-1, 0, 0)),
            ("rail edge at the middle of the bezel, square to the screen", on(d.image_s, hw - d.edge_in / 2), into),
            ("apron, below the bezel", on(d.bend_t + d.band_len / 2), into),
            ("brow, above the bezel", on(d.bezel_s1 + d.brow_ledge / 2), into),
            ("lower rear wall", V(0, d.body_d + RAY, d.rear_step_z0 / 2), V(0, -1, 0)),
            ("upper rear wall", V(0, d.depth + RAY, (d.rear_step_z1 + d.body_top) / 2), V(0, -1, 0)),
            ("hood top", V(0, oy + h.depth / 2, oz + h.height + RAY), V(0, 0, -1)),
            ("hood rear arc", V(0, oy + h.depth - d.hood_rear_arc_d / 3 + RAY * rear_arc, oz + h.height - d.hood_rear_arc_h / 3 + RAY * rear_arc),
             V(0, -rear_arc, -rear_arc)),
            ("hood side", V(h.half_width(h.height / 2) + RAY, oy + h.depth / 2, oz + h.height / 2), V(-1, 0, 0)),
            ("hood top bar, front", V(0, oy - RAY, oz + (h.z_open_top + h.height - d.hood_edge_in) / 2), V(0, 1, 0)),
            ("hood band (speaker face)", V(0, oy - RAY, oz + (h.z_sill + h.z_band_top) / 2), V(0, 1, 0))]


# ---------- the air path, the print table ----------

def air_path(v) -> dict:
    """The sections of the path from the fan vent in the rear door to the slot vents, from the parameter sheets."""
    fan = v("fan_frame")
    plenum = v("bc_shroud_h") - v("fan_t") - v("bc_fin_h")
    hood_len = v("bc_dp_clear") + v("bc_io_overhang") + v("bc_hood_x1")
    rows = [("fan vent in the door, fan face", fan * fan, f"{fan:.0f} x {fan:.0f}; the fan stands {v('bc_gap_door'):.0f} from the door, sealed by the shroud"),
            ("into the opened fin tops under the fan", fan * v("bc_fin_w"), f"{fan:.0f} x {v('bc_fin_w'):.1f}, gross, after an air space of {plenum:.1f} under the fan"),
            ("fin passage toward the I/O end", v("bc_fin_w") * v("bc_fin_h"), f"{v('bc_fin_w'):.1f} wide x {v('bc_fin_h'):.1f} high, gross: the fins take part of it"),
            ("exhaust duct at the I/O end, along the door", hood_len * v("bc_shroud_w"), f"{hood_len:.1f} x {v('bc_shroud_w'):.0f}, {v('bc_shroud_h') + v('bc_gap_door'):.0f} deep to the door"),
            ("slot vents in the door", v("vent_out_w") * v("vent_out_h"), f"{v('vent_out_w'):.1f} x {v('vent_out_h'):.1f}, gross")]
    out = [{"section": s, "area_mm2": round(a), "note": n} for s, a, n in rows]
    tight = min(out, key=lambda r: r["area_mm2"])
    return {"path": out, "tightest": tight["section"], "tightest_mm2": tight["area_mm2"], "plenum": plenum}


def print_table(parts: dict[str, Part.Shape], v) -> list[dict]:
    """The bounding size of each part of the shell against the bed: the fewest pieces if it is cut on the grid of the
    largest recommended footprint and height."""
    bed, xy, zmax = v("a1_bed"), v("a1_part_max_xy"), v("a1_part_max_z")
    out = []
    for k, s in parts.items():
        if k == "screen":  # the lit image, not a part
            continue
        bb = s.BoundBox
        a, b, c = sorted((bb.XLength, bb.YLength, bb.ZLength))
        fits = c <= bed and b <= bed and a <= bed
        pieces = math.ceil(c / xy) * math.ceil(b / xy) * math.ceil(a / zmax)
        out.append({"part": k, "x": round(bb.XLength, 1), "y": round(bb.YLength, 1), "z": round(bb.ZLength, 1), "fits_bed": fits, "pieces_at_least": pieces})
    return out


# ---------- the sections for sheet 09 ----------

def polylines(shape: Part.Shape, normal: App.Vector, at: float, axes: tuple[int, int]) -> list[list[list[float]]]:
    out = []
    for w in shape.slice(normal, at):
        pts = w.discretize(Deflection=0.2)
        out.append([[round(p[axes[0]], 2), round(p[axes[1]], 2)] for p in pts])
    return out


def fused_section(pieces: list[Part.Shape], normal: App.Vector, at: float) -> Part.Shape | None:
    faces = [Part.Face(w) for p in pieces for w in p.slice(normal, at) if w.isClosed()]
    if not faces:
        return None
    return faces[0].fuse(faces[1:]).removeSplitter() if len(faces) > 1 else faces[0]


def outline(face: Part.Shape | None, axes: tuple[int, int]) -> list[list[list[float]]]:
    if face is None:
        return []
    return [[[round(p[axes[0]], 2), round(p[axes[1]], 2)] for p in w.discretize(Deflection=0.2)] for f in face.Faces for w in f.Wires]


def sections(parts: dict[str, Part.Shape], cav: cavity.Cavity, found: list[Item], planes: dict[str, tuple[int, float]]) -> dict:
    out = {}
    for name, (axis, at) in planes.items():
        normal = V(*[1.0 if i == axis else 0.0 for i in range(3)])
        axes = tuple(i for i in range(3) if i != axis)
        out[name] = {"axis": axis, "at": at,
                     "outer": [pl for s in parts.values() for pl in polylines(s, normal, at, axes)],
                     "cavity": outline(fused_section(cav.pieces, normal, at), axes),
                     "items": [{"item": it.name, "group": it.group, "solid": s.name, "role": s.role, "lines": polylines(s.world, normal, at, axes)}
                               for it in found for s in it.solids if s.role in ENVELOPE]}
        out[name]["items"] = [r for r in out[name]["items"] if r["lines"]]
    return out


def rear_view(parts: dict[str, Part.Shape], found: list[Item], d: Blueprint, door: dict) -> dict:
    """The rear of the form seen from behind, the items as boxes in (x, z), and the proposed door."""
    w = d.wall_t
    walls = {"lower rear wall": d.body_d - w / 2, "upper rear wall": d.depth - w / 2}
    out = {"outer": {k: [pl for s in parts.values() for pl in polylines(s, V(0, 1, 0), y, (0, 2))] for k, y in walls.items()},
           "items": [], "door": door}
    for it in found:
        for s in it.solids:
            if s.role in ENVELOPE:
                bb = s.world.BoundBox
                out["items"].append({"item": it.name, "group": it.group, "solid": s.name, "role": s.role,
                                     "box": [round(bb.XMin, 2), round(bb.ZMin, 2), round(bb.XMax, 2), round(bb.ZMax, 2)], "y": [round(bb.YMin, 2), round(bb.YMax, 2)]})
    return out


def door_outline(d: Blueprint, lay: Layout, v) -> dict:
    """A proposed opening in the lower rear wall for the rear door, which carries the BC-250: as wide as the rear wall
    allows inside a frame of door_frame, from just below the board to door_frame below the slope of the upper rear."""
    x = d.rear_w / 2 - lay.door_frame
    z0 = v("bc_top_z") - v("bc_pcb_w_pwr") - lay.door_overlap
    z1 = d.rear_step_z0 - lay.door_frame
    return {"x0": -x, "x1": x, "z0": z0, "z1": z1, "w": 2 * x, "h": z1 - z0}


# ---------- the cut-away ----------

def cutaway(out: Path, parts: dict[str, Part.Shape], cav: cavity.Cavity, found: list[Item]) -> None:
    """Meshes of the far half of the skin and plates (x > 0) and of all the hardware, for render_views.py."""
    out.mkdir(parents=True, exist_ok=True)
    half = Part.makeBox(so.BIG, so.BIG, so.BIG, V(0, -so.BIG / 2, -so.BIG / 2))
    pieces = {"skin": Part.makeCompound([w.common(half) if w.BoundBox.XMin < 0 else w for w in cav.walls if w.BoundBox.XMax > 0]),
              "plates": Part.makeCompound([parts[k].common(half) for k in ("bezel", "control_panel")])}
    finish = {"skin": FINISH["skin"], "plates": FINISH["plate"]}
    by_group = defaultdict(list)
    for it in found:
        if it.group == "MonitorRoom":  # it would hide the present monitor
            continue
        roles = ("hardware", "protrusion") if it.shape(("hardware",)) else ("keepout",)
        by_group[it.group] += [s.world for s in it.solids if s.role in roles]
    for g, shapes in by_group.items():
        pieces[g] = Part.makeCompound(shapes)
        finish[g] = FINISH.get(g, FINISH["Panel"])
    manifest = {}
    for k, s in pieces.items():
        MeshPart.meshFromShape(Shape=s, LinearDeflection=MESH_LINEAR, AngularDeflection=MESH_ANGULAR).write(str(out / f"{k}.stl"))
        manifest[k] = {"file": f"{k}.stl", "finish": finish[k]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")


# ---------- the report ----------

def markdown(rep: dict) -> str:
    lines = ["# Fit study: the hardware in the shell", "", f"Result: **{rep['result']}**. Skin {rep['wall_t']:g} mm.", "",
             "## Clearance table", "", "Gaps in mm. Skin: from the item and its keep-out zones to the inner skin. Neighbour: from its hardware to the nearest other item's hardware (or room, for an item that is only room).", "",
             "| Item | Skin gap | Nearest neighbour | Gap | Result |", "| --- | --- | --- | --- | --- |"]
    lines += [f"| {r['item']} | {r['skin_gap']:.1f} | {r['neighbour']} | {r['neighbour_gap']:.1f} | {r['result']} |" for r in rep["clearances"]]
    lines += ["", "## Findings", "", "| Rule | Level | Subject | Detail |", "| --- | --- | --- | --- |"]
    lines += [f"| {k} | {lv} | {s} | {dt} |" for k, rows in rep["rules"].items() for lv, s, dt in rows]
    lines += ["", "## Wall", "", f"Measured on {rep['wall']['points']} points of the cavity's side faces: smallest {rep['wall']['min']:.2f}, "
              f"median {rep['wall']['median']:.2f}, largest {rep['wall']['max']:.2f}.", "", "| Where | Wall along the ray |", "| --- | --- |"]
    lines += [f"| {k} | {v:.1f} |" for k, v in rep["wall"]["probes"].items()]
    lines += ["", "## Air path", "", "| Section | Area mm2 | Note |", "| --- | --- | --- |"]
    lines += [f"| {r['section']} | {r['area_mm2']} | {r['note']} |" for r in rep["air"]["path"]]
    s = rep["speaker"]
    lines += ["", f"Tightest section: {rep['air']['tightest']} ({rep['air']['tightest_mm2']} mm2).", "",
              "## Speakers and marquee", "",
              f"Largest round driver behind each speaker form: {s['fit_spk_d']:.1f} across the frame, {s['fit_spk_depth']:.1f} deep behind the band.",
              f"Marquee: window {rep['marquee']['fit_mq_w']:.0f} x {rep['marquee']['fit_mq_h']:.0f}; room behind the cover {rep['marquee']['room']:.1f} deep.", "",
              "## Monitor", "", "Gap to the skin, mm, from the top 10 of the monitor (the tuck) and from its bottom 10 (the sweep).", "",
              "| Unit | Top | Bottom |", "| --- | --- | --- |"]
    lines += [f"| {k} | {m['top']:.1f} | {m['bottom']:.1f} |" for k, m in rep["monitor"].items() if k != "plugs"]
    lines += ["", "| Height | z | Cavity half width | Needed, right-angle plugs | Needed, straight plugs |", "| --- | --- | --- | --- | --- |"]
    lines += [f"| {r['where']} | {r['z']:.0f} | {r['cavity_half_width']:.1f} | {r['right_angle_needs']:.1f} | {r['straight_needs']:.1f} |" for r in rep["monitor"]["plugs"]]
    st = rep["seat"]
    lines += ["", "## Sight line", "", f"Desk {st['desk_h']:.0f}, chair seat {st['chair_h']:.0f}, relaxed sitting {st['slump']:.0f} below the upright eye height.", "",
              "| Player | Eye above the desk | To the screen normal, deg | Below horizontal, deg | Eye to centre | Image hidden at the top | At the bottom |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    lines += [f"| {r['person']} | {r['eye_z']:.0f} | {r['to_normal_deg']:.1f} | {r['below_horizontal_deg']:.1f} | {r['distance']:.0f} | {r['hidden_top']:.1f} | {r['hidden_bottom']:.1f} |" for r in rep["sight"]]
    lines += ["", "## Print table", "", "| Part | X | Y | Z | Fits the bed | Pieces at least |", "| --- | --- | --- | --- | --- | --- |"]
    lines += [f"| {r['part']} | {r['x']} | {r['y']} | {r['z']} | {'yes' if r['fits_bed'] else 'no'} | {r['pieces_at_least']} |" for r in rep["print"]]
    return "\n".join(lines) + "\n"


def main() -> int:
    root = Path(os.environ.get("CANDYBAR_ROOT", Path(__file__).resolve().parents[2]))
    params_dir = Path(os.environ.get("CANDYBAR_PARAMS") or root / "params")
    out = Path(os.environ.get("CANDYBAR_OUT", "cad/out/shell-bp")) / FIT
    d = Blueprint()
    parts = so.build(d)
    rep = study(d, Layout(), params_dir, out, parts, cavity.build(parts, d))
    print(markdown(rep))
    return 1 if rep["result"] == check.FAIL else 0


def study(d: Blueprint, lay: Layout, params_dir: Path, out: Path, parts: dict[str, Part.Shape], cav: cavity.Cavity) -> dict:
    """The whole study on built parts and their cavity; writes its files into out and returns the report."""
    out.mkdir(parents=True, exist_ok=True)
    h = pr.hood(d)
    base = sheet(params.load(params_dir), "FitBase")
    v = lambda name: params.value(base, name)
    hw = d.width / 2
    side_in = hw - ray_wall(parts, cav, V(hw + RAY, usb_row_start(d, lay, v), usb_row_z(d)), V(-1, 0, 0))
    values = anchors(d, lay, v, side_in)
    _, marquee = marquee_box(d, h, v("mq_led_depth"))
    marquee["room"] = deepest(lambda depth: marquee_box(d, h, depth)[0], cav.walls)
    speaker = speaker_room(d, lay, h, cav.walls, v("mq_led_depth"))
    values.update({k: marquee[k] for k in ("fit_mq_w", "fit_mq_h", "fit_mq_y", "fit_mq_z0")}, **speaker)
    doc = build_items(sheet_rows(params_dir, values))
    pv = lambda name: params.value(doc, name)
    found = items(doc)
    rules = run_checks(doc, found, cav, parts["bezel"], parts["control_panel"])
    reach = d.width
    table = clearances(found, cav, rules, reach)
    measured = sorted(t for t, _ in cavity.measure_wall(parts, cav, cavity.seam_filler(parts, d), WALL_STEP, WALL_EVERY))
    wall = {"points": len(measured), "min": measured[0], "median": measured[len(measured) // 2], "max": measured[-1],
            "probes": {name: ray_wall(parts, cav, p, n) for name, p, n in wall_probes(d, h)}}
    door = door_outline(d, lay, pv)
    margins = monitor_margins(doc, found, cav, d, pv)
    sight = sight_lines(d, parts, pv)
    failed = any(lv == check.FAIL for rows in rules.values() for lv, _, _ in rows)
    rep = {"result": check.FAIL if failed else check.PASS, "wall_t": d.wall_t, "layout": asdict(lay), "anchors": values,
           "openings": asdict(cavity.Openings()), "clearances": table, "rules": rules, "wall": wall, "air": air_path(pv),
           "psu_fan_clear": pv("psu_fan_clear"), "speaker": speaker, "marquee": marquee, "door": door, "print": print_table(parts, pv),
           "cavity_volume_l": sum(p.Volume for p in cav.pieces) / 1e6, "monitor": margins, "sight": sight,
           "seat": {"desk_h": DESK_H, "chair_h": CHAIR_H, "slump": SLUMP}}
    (out / "report.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
    (out / "report.md").write_text(markdown(rep), encoding="utf-8")
    z = lambda name: pv(name)
    planes = {"side, centre line": (0, 0.0), "side, through the lever": (0, lay.stick_x),
              "plan, power supply": (2, z("psu_z0") + z("psu_h") / 2), "plan, deck": (2, values["fit_usb_z"]),
              "plan, compute module": (2, z("bc_top_z") - z("bc_pcb_w_pwr") / 2)}
    data = {"sections": sections(parts, cav, found, planes), "rear": rear_view(parts, found, d, door), "clearances": table,
            "skin_parts": list(parts), "wall_t": d.wall_t, "sight": sight}
    (out / "sections.json").write_text(json.dumps(data), encoding="utf-8")
    cutaway(out / "cutaway", parts, cav, found)
    return rep
