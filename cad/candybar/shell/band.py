"""The hood band of the cabinet: the speaker pods with their grilles, the logo field with its badge, and the marquee
with its lip, its printed front and its light box (docs/design/hood-band.md). The owner chose band A, on the hood as
it is (2026-11-14), and since 2026-11-16 it is in the default build of the shell (solids.build): DEFAULT.

The cap of the hood is solids.cap; every opening of the band is a cutter that this module makes (hood_cutters). The
study candybar.shell.hood_band keeps the other bands (B, C) and the taller hoods, with the checks and the sheets of
the variants; it builds them with the functions of this module.

The parts of the band, by name (left parts are mirror images):
  hood                  the cap with the openings of the band (painted)
  marquee_lip_*         the lower frame of the marquee: a bar with a groove that holds the foot of the front (painted)
  speaker_pod_*         the pod round a speaker (painted)
  logo_field            the raised field for the owner's mark (painted)
  grille_*              the speaker grille: a black printed insert that also clamps the driver
  grille_screw_*        the two M3 screws of a grille (bought)
  logo_badge            the plate with the owner's mark
  marquee_front_*       the printed translucent front of the marquee, in two halves with a lap
  light_box_*           the closed box behind the marquee window that holds the light (black, inside)
  driver_seat_*         the seat of the driver: a baffle behind the wall with the holes for the heat-set inserts (inside)
  speaker_enclosure_*   the sealed enclosure behind the driver, screwed to the baffle (inside)
  driver_*, led_strip   envelopes of the hardware
Frames: z from the foot of the hood (the hood's own frame) in the functions of the band; build() returns every part
in the cabinet frame.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import FreeCAD
import Part

from . import profiles as pr
from . import solids as so
from .dims import Blueprint

V = FreeCAD.Vector
P2 = tuple[float, float]


MIRROR = (V(0, 0, 0), V(1, 0, 0))


@dataclass(frozen=True)
class Driver:
    """The speaker driver. The research of 2026-11-14 recommends the Tectonic TEBM35C10-4, with a square frame of
    51.8, in a sealed enclosure of 0.45 l. The frame is that value. The other values are an envelope of the 50 mm
    class that this study did not compare with a data sheet. The fallback, the Visaton FRS 5 X, has a smaller frame
    (50): it needs its own seat pocket."""
    frame: float = 51.8
    frame_t: float = 2.0
    frame_r: float = 3.0
    basket_d: float = 47.0
    basket_depth: float = 12.0
    magnet_d: float = 36.0
    magnet_depth: float = 14.0
    cone_dia: float = 44.0


@dataclass(frozen=True)
class Band:
    """The values of the hood band that all variants share. Lengths in mm. z is measured from the foot of the hood
    (the hood's own frame), x from the centre line."""
    wall_t: float = 4.0
    seat_off: float = 0.1           # inside parts stand this far behind the wall, as in the fit study (every second slab of the skin is 0.05 thicker)
    edge_break: float = 1.0
    small_break: float = 0.3        # on the rims of the holes of grille A and on the rear rims of the slots of grille C
    # --- speakers ---
    spk_half_h: float = 27.0        # half the height of the speaker opening (54: the frame of 51.8 and its pocket pass it)
    spk_w: float = 64.0             # width of the straight opening (variants A and C)
    spk_r: float = 4.0              # corner radius of the opening
    spk_contour_inner: float = 112.0    # variant B: the inner end of the opening (6 from the seam H1 at x 106)
    spk_contour_gap: float = 10.0       # variant B: the outer end stands this far inside the leg of the opening
    pod_inner: float = 106.0        # the inner end of a pod (on the line of the seam H1)
    pod_leg_gap: float = 8.0        # the outer end of a pod stands this far inside the leg
    pod_end_gap: float = 1.5        # a pod stands this far above the ledge and below the lip
    pod_r: float = 8.0              # corner radius of a pod, seen from the front
    pod_edge_r: float = 2.0         # round of the front edge of a pod
    grille_t: float = 2.4
    grille_gap: float = 0.15        # between the grille and its opening, each side
    hole_d: float = 3.8
    hole_pitch: float = 5.2
    slot_w: float = 3.4
    slot_pitch: float = 7.0
    slot_centre_bar: float = 5.6    # the bar on the centre line of a slot grille, which takes the two screws
    slot_edge: float = 5.0          # a slot ends this far inside the edge of the grille
    field_half_w: float = 21.0      # the holes and the upright slots lie within this of the driver's centre
    screw_x: float = 29.0           # the two screws of a grille, left and right of the driver's centre
    screw_hole: float = 3.4
    head_d: float = 5.7             # the head of an M3 button-head screw (ISO 7380, ESTIMATED: the screw is not bought)
    head_h: float = 1.65
    insert_hole: float = 4.0        # for an M3 heat-set insert
    insert_depth: float = 5.65
    bar_w: float = 8.0              # the clamp bar behind a grille that stands in a pod
    bar_half_h: float = 20.0
    bar_x: float = 27.5             # the middle of a clamp bar from the driver's centre: it lies on the edge of the frame, inside the tunnel
    seat_face: float = 3.5          # the front of the seat stands this far behind the front of the wall: a flush grille (set back 1.0, 2.4 thick) then lies on the driver's frame
    seat_flange_t: float = 5.0
    # the baffle: the flange of the seat is a plate behind the wall, and the sealed enclosure closes on its rear
    baffle_half_w: float = 55.0
    baffle_z0: float = 16.5         # from the foot of the hood
    baffle_top_gap: float = 1.5     # below the flange of the light box
    encl_half_w: float = 46.0
    encl_edge: float = 1.0          # the enclosure stands this far inside the top and bottom of the baffle
    encl_wall: float = 2.4
    encl_litres: float = 0.45       # the air in the enclosure, with the volume of the driver taken off
    ear_t: float = 3.0
    ear_half_h: float = 28.0
    boss_z: float = 20.0            # the four screws of the enclosure: above and below the driver's centre, in the ears
    seat_gap: float = 0.3
    frame_proud: float = 0.1        # the driver's frame stands this far proud of the seat, so that the grille clamps it
    # --- marquee ---
    mq_w: float = 352.0             # the opening in the wall: the lit window (eleven modules of 32)
    mq_h: float = 32.0              # the marquee window of the blueprint (34) less box_margin_z at its top and bottom
    mq_r: float = 3.0
    mq_front_t: float = 2.2
    mq_front_gap: float = 2.0       # between the front and the legs and the top bar: the front lifts by this to come out
    mq_lap: float = 4.0             # half the length of the lap between the two halves of the front
    lip_round: float = 1.0          # the round top of the lip's fence (the fence is 2 thick); also the depth of the groove
    lip_groove: float = 2.5         # the groove behind the fence: the front and 0.3
    hook_w: float = 6.0
    hook_h: float = 8.0
    hook_nose: float = 2.0
    hook_hold: float = 1.3          # how far the nose of a hook stands below its slot when the front is down
    hook_in: float = 6.5            # the middle of a hook stands this far outside the end of the lit window
    box_depth: float = 25.0         # the light box behind the wall: the diffuser distance is this plus the wall
    box_wall: float = 2.0
    box_margin_x: float = 2.0
    box_margin_z: float = 1.0
    box_flange: float = 3.0
    led_w: float = 10.0
    led_t: float = 2.5
    led_len: float = 350.0
    # --- logo ---
    logo_w: float = 176.0
    logo_z0: float = 25.0
    logo_z1: float = 74.9
    logo_proud: float = 5.0
    logo_r: float = 6.0
    logo_inset: float = 5.0
    logo_recess: float = 3.2
    badge_t: float = 2.2
    badge_gap: float = 0.3
    backer_flange: float = 6.0


    @property
    def lip_proud(self) -> float:
        """How far the lip stands in front of the band: its fence and its groove."""
        return 2 * self.lip_round + self.lip_groove


@dataclass(frozen=True)
class Variant:
    key: str
    name: str
    pod_proud: float        # 0: no pod
    opening: str            # "straight" or "contour"
    grille: str             # "holes", "level slots" or "upright slots"
    grille_setback: float   # the grille stands this far behind the front of the pod, or of the band
    logo: str               # "raised", "recess" or "none"
    text: str


# the finish of each part for the renders and the FreeCAD document, and its class for the checks:
#   painted      a printed part of the exterior that is filled and painted: the edge rule holds
#   black        a printed part that shows and is not painted (black ABS as printed)
#   translucent  the printed front of the marquee
#   plate        the badge: a printed or cut plate with the owner's mark
#   inside       a printed part behind the wall
#   hardware     an envelope of a purchased part
PARTS = {
    "hood": ("white", "painted"), "marquee_lip": ("white", "painted"), "speaker_pod": ("white", "painted"),
    "logo_field": ("white", "painted"), "grille": ("black", "black"), "logo_badge": ("#2f4f3a", "plate"),
    "marquee_front": ("#e9dca6", "translucent"), "light_box": ("#2a2a30", "inside"), "driver_seat": ("#2a2a30", "inside"),
    "speaker_enclosure": ("#3a3a44", "inside"), "logo_backer": ("#2a2a30", "inside"), "driver": ("#5a5a5c", "hardware"), "led_strip": ("#d8c060", "hardware"),
    "grille_screw_inner": ("#1a1a1a", "hardware"), "grille_screw_outer": ("#1a1a1a", "hardware"),
}


PRINT = {
    "hood": "As in the split (pieces 18 to 20): the centre on a cut face, each side upright on its foot.",
    "marquee_lip": "On its rear face (the face that lies on the band). The front and the round top are walls.",
    "speaker_pod": "Front face on the bed. The tunnel is a hole through the part. No support.",
    "logo_field": "Rear face on the bed. The recess is open to the top. No support.",
    "grille": "Front face on the bed. The holes or slots go straight up; the clamp bars stand on the plate. No support.",
    "logo_badge": "Flat, front face on the bed.",
    "marquee_front": "Flat, front face on the bed. The hooks stand up; the nose of a hook is a bridge of 2.",
    "light_box": "Mouth on the bed. The rear wall is a bridge of 36 across the box.",
    "driver_seat": "Baffle on the bed, the island up. No support.",
    "speaker_enclosure": "Rear wall on the bed, the mouth up. No support.",
    "logo_backer": "Flange on the bed, the island up. No support.",
}


def kind(name: str) -> str:
    """The kind of a part: its name without the side."""
    for end in ("_right", "_left"):
        if name.endswith(end):
            return name[:-len(end)]
    return name


def loop(points: list[P2], r: float) -> Part.Wire:
    """A closed polygon in (x, z) on the plane y = 0, each corner rounded with the radius r (arcs of circles)."""
    n = len(points)
    at = lambda q: V(q[0], 0.0, q[1])
    if r < 1e-9:
        return Part.makePolygon([at(p) for p in points + points[:1]])
    cuts = []
    for i, p in enumerate(points):
        a, b = points[i - 1], points[(i + 1) % n]
        u1 = ((a[0] - p[0]) / math.dist(a, p), (a[1] - p[1]) / math.dist(a, p))
        u2 = ((b[0] - p[0]) / math.dist(b, p), (b[1] - p[1]) / math.dist(b, p))
        half = math.acos(max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1]))) / 2
        t = r / math.tan(half)
        k = math.hypot(u1[0] + u2[0], u1[1] + u2[1])
        c = (p[0] + (u1[0] + u2[0]) / k * r / math.sin(half), p[1] + (u1[1] + u2[1]) / k * r / math.sin(half))
        m = (c[0] + (p[0] - c[0]) / math.dist(p, c) * r, c[1] + (p[1] - c[1]) / math.dist(p, c) * r)
        cuts.append(((p[0] + u1[0] * t, p[1] + u1[1] * t), m, (p[0] + u2[0] * t, p[1] + u2[1] * t)))
    edges = []
    for i, (a, m, b) in enumerate(cuts):
        edges.append(Part.Arc(at(a), at(m), at(b)).toShape())
        nxt = cuts[(i + 1) % n][0]
        if math.dist(b, nxt) > 1e-9:
            edges.append(Part.LineSegment(at(b), at(nxt)).toShape())
    return Part.Wire(edges)


def plate(points: list[P2], r: float, y0: float, y1: float) -> Part.Shape:
    """A rounded polygon in (x, z) as a solid from y0 to y1."""
    return Part.Face(loop(points, r)).translated(V(0, y0, 0)).extrude(V(0, y1 - y0, 0))


def rect(cx: float, cz: float, w: float, h: float) -> list[P2]:
    return [(cx - w / 2, cz - h / 2), (cx + w / 2, cz - h / 2), (cx + w / 2, cz + h / 2), (cx - w / 2, cz + h / 2)]


def grow(points: list[P2], by: float) -> list[P2]:
    """A convex polygon (counter-clockwise) with each side moved out by a distance."""
    n = len(points)
    lines = []
    for i, p in enumerate(points):
        q = points[(i + 1) % n]
        k = math.dist(p, q)
        nx, nz = (q[1] - p[1]) / k, -(q[0] - p[0]) / k
        lines.append((nx, nz, nx * p[0] + nz * p[1] + by))
    out = []
    for i in range(n):
        (a1, b1, c1), (a2, b2, c2) = lines[i - 1], lines[i]
        det = a1 * b2 - a2 * b1
        out.append(((c1 * b2 - c2 * b1) / det, (a1 * c2 - a2 * c1) / det))
    return out


def stadium(p: P2, q: P2, w: float, y0: float, y1: float) -> Part.Shape:
    """A slot with round ends between the centres p and q in (x, z), w wide, as a solid from y0 to y1."""
    k = math.dist(p, q)
    ux, uz = (q[0] - p[0]) / k, (q[1] - p[1]) / k
    nx, nz = -uz, ux
    r = w / 2
    at = lambda c, a, b: V(c[0] + ux * a + nx * b, 0.0, c[1] + uz * a + nz * b)
    edges = [Part.LineSegment(at(p, 0, -r), at(q, 0, -r)).toShape(), Part.Arc(at(q, 0, -r), at(q, r, 0), at(q, 0, r)).toShape(),
             Part.LineSegment(at(q, 0, r), at(p, 0, r)).toShape(), Part.Arc(at(p, 0, r), at(p, -r, 0), at(p, 0, -r)).toShape()]
    return Part.Face(Part.Wire(edges)).translated(V(0, y0, 0)).extrude(V(0, y1 - y0, 0))


def hole(cx: float, cz: float, dia: float, y0: float, y1: float) -> Part.Shape:
    return Part.makeCylinder(dia / 2, y1 - y0, V(cx, y0, cz), V(0, 1, 0))


def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part.Shape:
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def one(shape: Part.Shape, what: str) -> Part.Shape:
    """The shape as one valid solid, or an error that names the step."""
    if shape.isNull() or not shape.isValid() or len(shape.Solids) != 1:
        raise Part.OCCError(f"hood band: {what} is not one valid solid")
    return shape.Solids[0]


def rounded(solid: Part.Shape, r: float, test, what: str) -> Part.Shape:
    """A round of radius r on the edges of a solid whose middle and ends pass the test."""
    edges = [e for e in solid.Edges if not e.Degenerated and all(test(p) for p in (so.middle(e), *[v.Point for v in e.Vertexes]))]
    if not edges:
        raise Part.OCCError(f"hood band: {what} found no edge to round")
    return one(solid.makeFillet(r, edges), what)


def right_and_left(name: str, right: Part.Shape) -> dict[str, Part.Shape]:
    return {f"{name}_right": right, f"{name}_left": right.mirror(*MIRROR)}


@dataclass(frozen=True)
class Places:
    """The places of one variant, in the hood's frame."""
    yb: float                   # the front of the band wall (the wall is upright)
    zc: float                   # the height of the speaker's centre
    opening: list[P2]           # the right speaker opening in (x, z), counter-clockwise
    cx: float                   # the driver's centre
    pod: list[P2] | None        # the outline of the right pod
    y_grille: float             # the front of the grille
    y_seat: float               # the front of the seat (the driver's frame lies on it)


def leg(h: pr.Hood, d: Blueprint, z: float) -> float:
    """Half the width of the opening of the hood at height z, on its legs (above the round of the sill's corner)."""
    return h.half_width(max(z, h.z_sill + d.hood_sill_corner_r), h.opening)


def places(d: Blueprint, h: pr.Hood, b: Band, v: Variant) -> Places:
    yb = h.y_band_top
    zc = (h.z_sill + h.z_band_top) / 2
    z0, z1 = zc - b.spk_half_h, zc + b.spk_half_h
    pz0, pz1 = h.z_sill + b.pod_end_gap, h.z_band_top - b.pod_end_gap
    pod = [(b.pod_inner, pz0), (leg(h, d, pz0) - b.pod_leg_gap, pz0), (leg(h, d, pz1) - b.pod_leg_gap, pz1), (b.pod_inner, pz1)]
    if v.opening == "contour":
        out = lambda z: leg(h, d, z) - b.spk_contour_gap
        opening = [(b.spk_contour_inner, z0), (out(z0), z0), (out(z1), z1), (b.spk_contour_inner, z1)]
        cx = (b.spk_contour_inner + out(zc)) / 2
    else:
        cx = (b.pod_inner + leg(h, d, zc) - b.pod_leg_gap) / 2
        opening = rect(cx, zc, b.spk_w, 2 * b.spk_half_h)
    return Places(yb, zc, opening, cx, pod if v.pod_proud else None, yb - v.pod_proud + v.grille_setback, yb + b.seat_face)


def pod(b: Band, v: Variant, pl: Places) -> Part.Shape:
    """The right pod: its outline raised square to the band, with the tunnel of the speaker opening through it. The
    corners have a radius seen from the front, the front edge has a round, and the rim of the tunnel has the edge
    break."""
    y0 = pl.yb - v.pod_proud
    solid = plate(pl.pod, b.pod_r, y0, pl.yb).cut(plate(pl.opening, b.spk_r, y0 - 1, pl.yb + 1))
    xs, zs = [p[0] for p in pl.opening], [p[1] for p in pl.opening]
    in_tunnel = lambda p: min(xs) - 0.01 < p.x < max(xs) + 0.01 and min(zs) - 0.01 < p.z < max(zs) + 0.01
    front = lambda p: abs(p.y - y0) < 1e-6
    solid = rounded(one(solid, "the pod"), b.pod_edge_r, lambda p: front(p) and not in_tunnel(p), "the round of the pod's front edge")
    return rounded(solid, b.edge_break, lambda p: front(p) and in_tunnel(p), "the edge break of the pod's tunnel")


def screws(pl: Places, b: Band) -> list[P2]:
    return [(pl.cx - b.screw_x, pl.zc), (pl.cx + b.screw_x, pl.zc)]


def grille_cutters(b: Band, v: Variant, pl: Places, y0: float, y1: float) -> list[Part.Shape]:
    """The holes or slots of the right grille, as solids from y0 to y1."""
    cx, zc = pl.cx, pl.zc
    if v.grille == "holes":
        rows = int((b.spk_half_h - 3.5 - b.hole_d / 2) / (b.hole_pitch * math.sqrt(3) / 2))
        out = []
        for j in range(-rows, rows + 1):
            shift = b.hole_pitch / 2 if j % 2 else 0.0
            n = int((b.field_half_w - b.hole_d / 2 + shift) / b.hole_pitch) + 1
            for i in range(-n, n + 1):
                x = i * b.hole_pitch + shift
                if abs(x) <= b.field_half_w - b.hole_d / 2 + 1e-9:
                    out.append(hole(cx + x, zc + j * b.hole_pitch * math.sqrt(3) / 2, b.hole_d, y0, y1))
        return out
    first = b.slot_centre_bar / 2 + b.slot_w / 2
    if v.grille == "upright slots":
        n = int((b.field_half_w - b.slot_w / 2 - first) / b.slot_pitch) + 1
        offs = [s * (first + k * b.slot_pitch) for k in range(n) for s in (1, -1)]
        reach = b.spk_half_h - b.slot_edge - b.slot_w / 2
        return [stadium((cx + o, zc - reach), (cx + o, zc + reach), b.slot_w, y0, y1) for o in offs]
    n = int((b.spk_half_h - b.slot_edge - b.slot_w / 2 - first) / b.slot_pitch) + 1
    offs = [s * (first + k * b.slot_pitch) for k in range(n) for s in (1, -1)]
    (xa, za), (xb, zb) = pl.opening[1], pl.opening[2]
    inner = pl.opening[0][0] + b.slot_edge + b.slot_w / 2
    outer = lambda z: xa + (xb - xa) * (z - za) / (zb - za) - b.slot_edge - b.slot_w / 2
    return [stadium((inner, zc + o), (outer(zc + o), zc + o), b.slot_w, y0, y1) for o in offs]


def grille(b: Band, v: Variant, pl: Places) -> Part.Shape:
    """The right grille: a plate in the speaker opening with its holes or slots and two screw holes. In a pod, two
    clamp bars stand behind the plate and reach back to the driver's frame. With no pod, the plate lies on the frame."""
    y0, y1 = pl.y_grille, pl.y_grille + b.grille_t
    solid = plate(grow(pl.opening, -b.grille_gap), b.spk_r - b.grille_gap, y0, y1)
    y_frame = pl.y_seat - b.frame_proud
    if y_frame - y1 > 0.5:
        for sx in (-1, 1):
            x0 = pl.cx + sx * b.bar_x - b.bar_w / 2
            solid = solid.fuse(box(x0, x0 + b.bar_w, y1, y_frame, pl.zc - b.bar_half_h, pl.zc + b.bar_half_h))
        solid = solid.removeSplitter()
    cutters = grille_cutters(b, v, pl, y0 - 1, y1 + 0.001) + [hole(x, z, b.screw_hole, y0 - 1, y_frame + 1) for x, z in screws(pl, b)]
    solid = one(solid.cut(cutters), "the grille")
    # the front face shows: the rim of the plate and the mouth of each slot have the edge break of edge_break. The
    # holes of grille A leave webs of 1.4, so their rims have the small break (small_break). The mouth of a screw hole
    # lies under the head of its screw (grille_screws), and the bar between two slots leaves no room for a break there
    off_screws = lambda p: all(math.hypot(p.x - x, p.z - z) > b.screw_hole / 2 + 0.01 for x, z in screws(pl, b))
    front = lambda p: abs(p.y - y0) < 1e-6 and off_screws(p)
    in_field = lambda p: abs(p.x - pl.cx) < b.field_half_w + 0.5 and abs(p.z - pl.zc) < b.spk_half_h - 1.0
    # the rear rims of the holes and of the upright slots show through them (the room behind the grille is open)
    rear = lambda p: abs(p.y - y1) < 1e-6 and off_screws(p) and in_field(p)
    if v.grille == "holes":
        solid = rounded(solid, b.edge_break, lambda p: front(p) and not in_field(p), "the edge break of the grille's rim")
        solid = small_round(solid, b.small_break, lambda p: front(p) and in_field(p), "the small break of the holes of the grille")
        return small_round(solid, b.small_break, rear, "the small break of the rear rims of the holes")
    solid = rounded(solid, b.edge_break, front, "the edge break of the grille's front")
    if v.grille == "upright slots":
        solid = small_round(solid, b.small_break, rear, "the small break of the rear rims of the slots")
    return solid


def small_round(solid: Part.Shape, r: float, test, what: str) -> Part.Shape:
    """The small break on the edges whose middle and ends pass the test: a round of r, or a chamfer of r when the round
    does not build. It is left out (the edges stay as they are) when neither builds as one valid solid."""
    edges = [e for e in solid.Edges if not e.Degenerated and all(test(p) for p in (so.middle(e), *[v.Point for v in e.Vertexes]))]
    if not edges:
        return solid
    for make in (lambda: solid.makeFillet(r, edges), lambda: solid.makeChamfer(r, edges)):
        try:
            out = make()
            if out.isValid() and len(out.Solids) == 1:
                return out.Solids[0]
        except Part.OCCError:
            pass
    SMALL_LEFT.append(what)
    return solid


def grille_screws(b: Band, pl: Places) -> dict[str, Part.Shape]:
    """The heads of the two screws of the right grille, on its front face: the inner one is nearer the centre line."""
    y0 = pl.y_grille
    (xi, zi), (xo, zo) = sorted(screws(pl, b), key=lambda q: abs(q[0]))
    head = lambda x, z: Part.makeCylinder(b.head_d / 2, b.head_h, V(x, y0 - b.head_h, z), V(0, 1, 0))
    return {"grille_screw_inner": head(xi, zi), "grille_screw_outer": head(xo, zo)}


def box_low(d: Blueprint, h: pr.Hood, b: Band) -> float:
    """The lower edge of the light box's flange, from the foot of the hood."""
    return window(d, h, b)[0][1] - b.box_margin_z - b.box_wall - b.box_flange


def baffle(d: Blueprint, h: pr.Hood, b: Band, pl: Places) -> tuple[float, float, float, float]:
    """The baffle behind the wall, in (x0, x1, z0, z1): from baffle_z0 up to baffle_top_gap below the light box."""
    return pl.cx - b.baffle_half_w, pl.cx + b.baffle_half_w, b.baffle_z0, box_low(d, h, b) - b.baffle_top_gap


def bosses(d: Blueprint, h: pr.Hood, b: Band, pl: Places) -> list[P2]:
    """The four screws that hold the enclosure on the baffle."""
    x = (b.encl_half_w + b.baffle_half_w) / 2
    return [(pl.cx + sx * x, pl.zc + sz * b.boss_z) for sx in (-1, 1) for sz in (-1, 1)]


def seat(d: Blueprint, h: pr.Hood, b: Band, drv: Driver, pl: Places) -> Part.Shape:
    """The right driver seat: the baffle, a plate behind the wall round the speaker opening, and an island that fills
    the opening up to the seat face. It has a pocket for the driver's frame, a hole for its basket, two holes for the
    heat-set inserts of the grille screws, and four for the screws of the enclosure."""
    y_wall = pl.yb + b.wall_t + b.seat_off
    x0, x1, z0, z1 = baffle(d, h, b, pl)
    island = plate(grow(pl.opening, -b.seat_gap), b.spk_r - b.seat_gap, pl.y_seat, y_wall + 0.001)
    solid = island.fuse(box(x0, x1, y_wall, y_wall + b.seat_flange_t, z0, z1)).removeSplitter()
    f = drv.frame + 2 * b.seat_gap
    cutters = [plate(rect(pl.cx, pl.zc, f, f), drv.frame_r + b.seat_gap, pl.y_seat - 1, pl.y_seat + drv.frame_t - b.frame_proud),
               hole(pl.cx, pl.zc, drv.basket_d + 1.0, pl.y_seat - 1, y_wall + b.seat_flange_t + 1)]
    cutters += [hole(x, z, b.insert_hole, pl.y_seat - 1, pl.y_seat + b.insert_depth) for x, z in screws(pl, b)]
    cutters += [hole(x, z, b.insert_hole, y_wall + b.seat_flange_t - b.insert_depth + 1.0, y_wall + b.seat_flange_t + 1) for x, z in bosses(d, h, b, pl)]
    return one(solid.cut(cutters), "the driver seat")


def enclosure(d: Blueprint, h: pr.Hood, b: Band, drv: Driver, pl: Places) -> tuple[Part.Shape, dict[str, float]]:
    """The sealed enclosure behind the right driver: a box that is open to the front and closes on the rear of the
    baffle, with an ear on each side for its four screws. Its depth gives encl_litres of air after the driver's
    volume behind the baffle is taken off. Returns the solid and its numbers."""
    y0 = pl.yb + b.wall_t + b.seat_off + b.seat_flange_t
    _, _, bz0, bz1 = baffle(d, h, b, pl)
    z0, z1 = bz0 + b.encl_edge, bz1 - b.encl_edge
    w = b.encl_wall
    inner = (2 * (b.encl_half_w - w)) * (z1 - z0 - 2 * w)
    drv_vol = driver(b, drv, pl).common(box(-500.0, 500.0, y0, 500.0, -500.0, 500.0)).Volume
    depth = (b.encl_litres * 1e6 + drv_vol) / inner
    outer = box(pl.cx - b.encl_half_w, pl.cx + b.encl_half_w, y0, y0 + depth + w, z0, z1)
    ears = box(pl.cx - b.baffle_half_w, pl.cx + b.baffle_half_w, y0, y0 + b.ear_t, pl.zc - b.ear_half_h, pl.zc + b.ear_half_h)
    room_ = box(pl.cx - b.encl_half_w + w, pl.cx + b.encl_half_w - w, y0 - 1, y0 + depth, z0 + w, z1 - w)
    cutters = [room_] + [hole(x, z, b.screw_hole, y0 - 1, y0 + b.ear_t + 1) for x, z in bosses(d, h, b, pl)]
    solid = one(outer.fuse(ears).removeSplitter().cut(cutters), "the enclosure")
    return solid, {"litres": b.encl_litres, "depth_inside": round(depth, 1), "inside": [round(2 * (b.encl_half_w - w), 1), round(z1 - z0 - 2 * w, 1)],
                   "driver_cm3": round(drv_vol / 1000, 1), "rear_y": round(y0 + depth + w + h.origin[1], 1)}


def driver(b: Band, drv: Driver, pl: Places) -> Part.Shape:
    """The envelope of the right driver: the frame, the basket as a cone, the magnet."""
    y0 = pl.y_seat - b.frame_proud
    y1 = y0 + drv.frame_t
    frame = plate(rect(pl.cx, pl.zc, drv.frame, drv.frame), drv.frame_r, y0, y1)
    basket = Part.makeCone(drv.basket_d / 2, drv.magnet_d / 2 + 1.0, drv.basket_depth, V(pl.cx, y1, pl.zc), V(0, 1, 0))
    magnet = Part.makeCylinder(drv.magnet_d / 2, drv.magnet_depth, V(pl.cx, y1 + drv.basket_depth, pl.zc), V(0, 1, 0))
    return one(frame.fuse([basket, magnet]).removeSplitter(), "the driver")


def open_area(b: Band, v: Variant, drv: Driver, pl: Places) -> dict[str, float]:
    """How much of the driver's cone the grille leaves open: the area of its holes or slots inside the cone's circle."""
    disc = Part.Face(Part.Wire(Part.Circle(V(pl.cx, 0, pl.zc), V(0, 1, 0), drv.cone_dia / 2).toShape()))
    cuts = Part.makeCompound(grille_cutters(b, v, pl, -1.0, 1.0))
    area = disc.common(cuts).Area
    return {"open_mm2": round(area, 1), "cone_mm2": round(disc.Area, 1), "share": round(area / disc.Area, 3)}


def lip(d: Blueprint, h: pr.Hood, b: Band, opening: Part.Shape) -> dict[str, Part.Shape]:
    """The lip under the marquee, in two halves: a bar across the opening, as high as the stand-in. Its top has a
    fence with a round top, and behind the fence a groove that holds the foot of the marquee front. The lower front
    edge has the edge break. The ends follow the legs of the opening. The lip is lip_proud in front of the band (the
    stand-in is 5): its front stands behind the front of the hood, so that its ends lie on the wall of the leg and not
    in the edge break of the leg's rim."""
    yb, yf = h.y_band_top, h.y_band_top - b.lip_proud
    z0, zt = h.z_band_top, h.z_rail_top
    r, e = b.lip_round, b.edge_break
    zg = zt - r
    at = lambda y, z: V(-300.0, y, z)
    k = math.sqrt(0.5)
    edges = [Part.LineSegment(at(yb, z0), at(yf + e, z0)).toShape(),
             Part.Arc(at(yf + e, z0), at(yf + e - e * k, z0 + e - e * k), at(yf, z0 + e)).toShape(),
             Part.LineSegment(at(yf, z0 + e), at(yf, zg)).toShape(),
             Part.Arc(at(yf, zg), at(yf + r, zt), at(yf + 2 * r, zg)).toShape(),
             Part.LineSegment(at(yf + 2 * r, zg), at(yb, zg)).toShape(),
             Part.LineSegment(at(yb, zg), at(yb, z0)).toShape()]
    bar = Part.Face(Part.Wire(edges)).extrude(V(600.0, 0, 0)).common(opening)
    right = one(bar.common(box(0.0, 300.0, -50.0, 50.0, 0.0, 200.0)), "the lip")
    return right_and_left("marquee_lip", right)


def window(d: Blueprint, h: pr.Hood, b: Band) -> list[P2]:
    """The opening of the lit window in the wall, in (x, z): at the height of the marquee window of the blueprint
    (marquee_margin above the lip, marquee_h high), less box_margin_z at its top and bottom."""
    return rect(0.0, h.z_rail_top + d.marquee_margin + d.marquee_h / 2, b.mq_w, b.mq_h)


def hook_place(d: Blueprint, h: pr.Hood, b: Band) -> tuple[float, float]:
    """The middle of the right hook, in (x, z)."""
    return b.mq_w / 2 + b.hook_in, h.z_rail_top + d.marquee_margin + d.marquee_h / 2


def marquee_front(d: Blueprint, h: pr.Hood, b: Band) -> dict[str, Part.Shape]:
    """The printed front of the marquee, in two halves that lap on the centre line. Its foot stands in the groove of
    the lip. Its ends and its top stand mq_front_gap inside the legs and the top bar. A hook at each end goes through
    a slot in the wall and holds behind it when the front is down."""
    side, corner, top = pr.hood_outline(d, h.height, h.half_base)
    by = d.hood_bar + b.mq_front_gap
    zb = h.z_rail_top - b.lip_round + 0.1
    side_in = so.from_height(so.offset_seg(side, by), zb)
    path = [pr.Line((0.0, zb), (so.ends(side_in)[0][0], zb)), side_in, so.offset_seg(corner, by), so.offset_seg(top, by)]
    yb = h.y_band_top
    solid = so.prism(so.both_sides(path), so.xz(yb - b.mq_front_t), V(0, b.mq_front_t, 0))
    hx, hz = hook_place(d, h, b)
    y_back = yb + b.wall_t + 0.4
    stem = box(hx - b.hook_w / 2, hx + b.hook_w / 2, yb, y_back + b.hook_nose, hz - b.hook_h / 2, hz + b.hook_h / 2)
    nose = box(hx - b.hook_w / 2, hx + b.hook_w / 2, y_back, y_back + b.hook_nose, hz - b.hook_h / 2 - b.hook_nose - b.hook_hold, hz - b.hook_h / 2)
    hook = stem.fuse(nose)
    solid = solid.fuse([hook, hook.mirror(*MIRROR)]).removeSplitter()
    # the front face shows in the window: its edges have the break, before the split, so that the two halves agree
    solid = rounded(solid, b.edge_break, lambda p: abs(p.y - (yb - b.mq_front_t)) < 1e-6, "the edge break of the marquee front")
    ym = yb - b.mq_front_t / 2
    right_half = box(b.mq_lap, 400.0, -50.0, 50.0, 0.0, 200.0).fuse(box(-b.mq_lap, b.mq_lap + 1.0, ym, 50.0, 0.0, 200.0))
    right = one(solid.common(right_half).removeSplitter(), "the right half of the marquee front")
    left = one(solid.cut(right_half).removeSplitter(), "the left half of the marquee front")
    return {"marquee_front_right": right, "marquee_front_left": left}


def hook_slot(d: Blueprint, h: pr.Hood, b: Band, depth: float) -> Part.Shape:
    """The slot in the wall for the right hook: the hook goes in with the front lifted, and its nose stands hook_hold
    below the slot when the front is down."""
    hx, hz = hook_place(d, h, b)
    z0 = hz - b.hook_h / 2 - b.hook_nose
    z1 = hz + b.hook_h / 2 + b.mq_front_gap
    yb = h.y_band_top
    return box(hx - b.hook_w / 2 - 0.3, hx + b.hook_w / 2 + 0.3, yb - 1, yb + depth, z0, z1)


def light_box(d: Blueprint, h: pr.Hood, b: Band) -> tuple[dict[str, Part.Shape], Part.Shape]:
    """The light box behind the lit window, in two halves, and the envelope of the LED strip on its rear wall. The
    box is closed: five walls and a flange that lies on the rear of the wall round the window. Its mouth is the
    window with a margin."""
    y0 = h.y_band_top + b.wall_t + b.seat_off
    win = window(d, h, b)
    x1, z0, z1 = win[1][0] + b.box_margin_x, win[0][1] - b.box_margin_z, win[2][1] + b.box_margin_z
    w = b.box_wall
    outer = box(-x1 - w, x1 + w, y0, y0 + b.box_depth + w, z0 - w, z1 + w)
    flange = box(-x1 - w - b.box_flange, x1 + w + b.box_flange, y0, y0 + w, z0 - w - b.box_flange, z1 + w + b.box_flange)
    solid = outer.fuse(flange).removeSplitter().cut(box(-x1, x1, y0 - 1, y0 + b.box_depth, z0, z1))
    right = one(solid.common(box(0.0, 400.0, -50.0, 200.0, 0.0, 200.0)), "the light box")
    zm = (z0 + z1) / 2
    led = box(-b.led_len / 2, b.led_len / 2, y0 + b.box_depth - b.led_t, y0 + b.box_depth, zm - b.led_w / 2, zm + b.led_w / 2)
    return right_and_left("light_box", right), led


def logo_recess(b: Band) -> list[P2]:
    w = b.logo_w - 2 * b.logo_inset
    return rect(0.0, (b.logo_z0 + b.logo_z1) / 2, w, b.logo_z1 - b.logo_z0 - 2 * b.logo_inset)


def logo_field(b: Band, yb: float) -> Part.Shape:
    """The raised logo field: a block on the band with round corners, the edge break on its front edge, and a recess
    for the badge whose rim has the edge break too."""
    y0 = yb - b.logo_proud
    outline = rect(0.0, (b.logo_z0 + b.logo_z1) / 2, b.logo_w, b.logo_z1 - b.logo_z0)
    solid = plate(outline, b.logo_r, y0, yb).cut(plate(logo_recess(b), b.logo_r - b.logo_inset + 2.0, y0 - 1, y0 + b.logo_recess))
    return rounded(one(solid, "the logo field"), b.edge_break, lambda p: abs(p.y - y0) < 1e-6, "the edge break of the logo field")


def logo_badge(b: Band, y_floor: float) -> Part.Shape:
    """The badge: a plate that lies on the floor of the recess, 1 below its rim. Its front edges have the break."""
    y0 = y_floor - b.badge_t
    solid = plate(grow(logo_recess(b), -b.badge_gap), b.logo_r - b.logo_inset + 2.0 - b.badge_gap, y0, y_floor)
    return rounded(solid, b.edge_break, lambda p: abs(p.y - y0) < 1e-6, "the edge break of the badge")


def logo_backer(b: Band, yb: float) -> Part.Shape:
    """The floor of a logo recess that is an opening in the wall: a flange behind the wall and an island in the opening."""
    y_wall = yb + b.wall_t + b.seat_off
    r = b.logo_r - b.logo_inset + 2.0
    island = plate(grow(logo_recess(b), -b.seat_gap), r - b.seat_gap, yb + b.logo_recess, y_wall + 0.001)
    flange = plate(grow(logo_recess(b), b.backer_flange), r + b.backer_flange, y_wall, y_wall + 3.0)
    return one(island.fuse(flange).removeSplitter(), "the logo backer")


def hood_cutters(d: Blueprint, h: pr.Hood, b: Band, v: Variant, pl: Places, depth: float) -> tuple[list[Part.Shape], list[list[P2]]]:
    """What a band cuts out of the wall: the cutters (as deep as `depth` behind the front of the wall), and the
    outlines of the openings whose rim shows and gets the edge break."""
    yb = pl.yb
    cut = lambda pts, r: plate(pts, r, yb - 1, yb + depth)
    spk = cut(pl.opening, b.spk_r)
    slot = hook_slot(d, h, b, depth)
    cutters = [cut(window(d, h, b), b.mq_r), spk, spk.mirror(*MIRROR), slot, slot.mirror(*MIRROR)]
    rims: list[list[P2]] = []
    if not v.pod_proud:
        rims += [pl.opening, [(-x, z) for x, z in pl.opening]]
    if v.logo == "recess":
        cutters.append(cut(logo_recess(b), b.logo_r - b.logo_inset + 2.0))
        rims.append(logo_recess(b))
    return cutters, rims


def hood_form(d: Blueprint, h: pr.Hood, b: Band, v: Variant, pl: Places, solid: Part.Shape) -> Part.Shape:
    """The cap as an outer form with the openings of a band: each opening is a pocket through the wall and wall_t
    deeper. The rim of an opening that shows gets the edge break."""
    cutters, rims = hood_cutters(d, h, b, v, pl, 2 * b.wall_t)
    out = one(solid.cut(cutters), "the hood with the openings of the band")
    for pts in rims:
        xs, zs = [p[0] for p in pts], [p[1] for p in pts]
        on_rim = lambda p, xs=xs, zs=zs: abs(p.y - pl.yb) < 1e-6 and min(xs) - 0.01 < p.x < max(xs) + 0.01 and min(zs) - 0.01 < p.z < max(zs) + 0.01
        out = rounded(out, b.edge_break, on_rim, "the edge break of an opening of the band")
    return out


def build(d: Blueprint, b: Band, drv: Driver, v: Variant, cap_solid: Part.Shape, opening: Part.Shape) -> dict[str, Part.Shape]:
    """The parts of one hood band, by name, in the cabinet frame."""
    h = pr.hood(d)
    pl = places(d, h, b, v)
    out: dict[str, Part.Shape] = {"hood": hood_form(d, h, b, v, pl, cap_solid)}
    out.update(lip(d, h, b, opening))
    if v.pod_proud:
        out.update(right_and_left("speaker_pod", pod(b, v, pl)))
    out.update(right_and_left("grille", grille(b, v, pl)))
    for k, s in grille_screws(b, pl).items():
        out.update(right_and_left(k, s))
    if v.logo == "raised":
        out["logo_field"] = logo_field(b, pl.yb)
        out["logo_badge"] = logo_badge(b, pl.yb - b.logo_proud + b.logo_recess)
    elif v.logo == "recess":
        out["logo_badge"] = logo_badge(b, pl.yb + b.logo_recess)
        out["logo_backer"] = logo_backer(b, pl.yb)
    out.update(marquee_front(d, h, b))
    boxes, led = light_box(d, h, b)
    out.update(boxes)
    out["led_strip"] = led
    out.update(right_and_left("driver_seat", seat(d, h, b, drv, pl)))
    out.update(right_and_left("speaker_enclosure", enclosure(d, h, b, drv, pl)[0]))
    out.update(right_and_left("driver", driver(b, drv, pl)))
    return {k: so.hood_frame(h)(s) for k, s in out.items()}


SMALL_LEFT: list[str] = []   # the small breaks that did not build in this run (small_round)

# the owner's band (2026-11-14): band A, on the hood as it is. The study candybar.shell.hood_band has B and C
DEFAULT = Variant("A", "pods", 13.0, "straight", "holes", 1.5, "raised",
                  "A pod round each speaker with a hole grille, and a raised logo field with a badge recess.")


def skin_cutters(d: Blueprint, b: Band | None = None, v: Variant = DEFAULT) -> list[Part.Shape]:
    """What the band takes out of the skin of the hood, in the cabinet frame: its openings, through the wall and
    beyond, and the stand-in of the lip in front of the band wall (solids.lip_stand_in), which the skin is made with.
    cavity.openings cuts them; the study's hood_skin cuts the same from the skin of the cache."""
    b = b or Band()
    h = pr.hood(d)
    pl = places(d, h, b, v)
    cutters, _ = hood_cutters(d, h, b, v, pl, 3 * b.wall_t)
    cutters.append(box(-300.0, 300.0, pl.yb - d.hood_rail_proud - 1.0, pl.yb, h.z_band_top - 0.01, h.z_rail_top + 0.01))
    return [so.hood_frame(h)(c) for c in cutters]


def default_parts(d: Blueprint, cap_solid: Part.Shape, opening: Part.Shape) -> dict[str, Part.Shape]:
    """The hood with band A and every part of the band, in the cabinet frame (solids.build)."""
    return build(d, Band(), Driver(), DEFAULT, cap_solid, opening)

