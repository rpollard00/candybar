"""The hood of shell variant D: a cap that stands on the body top, built with FreeCAD's Part module.

The cap is an arch seen from the front: a top bar, two legs that lean in, and a sill, round an opening whose
top corners are concentric with the cap's corners. Its outer form is the front outline extruded to the depth
of the body top. Every rounded edge is a profile carried along an outline of lines and arcs: an extrusion
along each line and a revolution round each arc centre, so the rounds are exact and meet without a crease.
The soft edge round the front of the cap is a quarter ellipse (a rational Bezier edge); the rear edge and the
rim of the opening are quarter circles. In the opening stand, from the top down: the marquee, tilted down
toward the player under the top bar; a small rail; the hood band, leaning back, with two raised speaker forms
and the logo plate between them, their faces parallel to the band; and the ledge on the sill.

All shapes are built in the hood frame (x across, y back from the cap's front plane, z up from its base) and
moved to the cabinet frame at the end. Dimensions come from dims.py.
"""
from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass

import FreeCAD
import Part

from .dims import Dims, HoodStations, hood_stations
from .parts import common, try_fillet

V = FreeCAD.Vector
Pt = tuple[float, float]
OVER = 2.0


@dataclass(frozen=True)
class Line:
    p: Pt
    q: Pt


@dataclass(frozen=True)
class Arc:
    """An arc round c from angle a0 to a1 (radians, counter-clockwise positive, measured from the first axis)."""
    c: Pt
    r: float
    a0: float
    a1: float

    def at(self, a: float) -> Pt:
        return self.c[0] + self.r * math.cos(a), self.c[1] + self.r * math.sin(a)


@dataclass(frozen=True)
class Conic:
    """A quarter of an ellipse from p to q, tangent at both ends to the lines that meet at corner."""
    p: Pt
    corner: Pt
    q: Pt


Outline = list[Line | Arc]
Path = list[Line | Arc | Conic]
Place = Callable[[Pt], FreeCAD.Vector]


def ends(seg: Line | Arc | Conic) -> tuple[Pt, Pt]:
    return (seg.at(seg.a0), seg.at(seg.a1)) if isinstance(seg, Arc) else (seg.p, seg.q)


def reverse(outline: Outline) -> Outline:
    return [Line(s.q, s.p) if isinstance(s, Line) else Arc(s.c, s.r, s.a1, s.a0) for s in reversed(outline)]


def edges_of(path: Path, place: Place) -> list[Part.Edge]:
    """Edges of a path; place maps a 2D point of the path to a 3D vector."""
    out = []
    for s in path:
        if isinstance(s, Line):
            out.append(Part.makeLine(place(s.p), place(s.q)))
        elif isinstance(s, Arc):
            out.append(Part.Arc(place(s.at(s.a0)), place(s.at((s.a0 + s.a1) / 2)), place(s.at(s.a1))).toShape())
        else:
            curve = Part.BezierCurve()
            curve.setPoles([place(s.p), place(s.corner), place(s.q)])
            curve.setWeight(2, math.sqrt(0.5))
            out.append(curve.toShape())
    return out


def face_of(path: Path, place: Place) -> Part.Face:
    return Part.Face(Part.Wire(edges_of(path, place)))


def polygon(points: list[Pt]) -> Outline:
    return [Line(p, q) for p, q in zip(points, points[1:] + points[:1])]


# ---------- a profile carried along an outline ----------

def carry(profile: Path, outline: Outline, y_plane: float, into: float) -> list[Part.Shape]:
    """Solids swept by a profile along an outline that lies in the plane y = y_plane.

    The profile is in (o, v): o to the right of the direction of travel, in the plane, and v into the solid
    (into is +1 when the solid lies toward +y, -1 when toward -y). Each line of the outline gives an extrusion
    and each arc a revolution round its centre, so neighbouring pieces share their end sections exactly.
    """
    out = []
    for s in outline:
        if isinstance(s, Line):
            length = math.dist(s.p, s.q)
            t = ((s.q[0] - s.p[0]) / length, (s.q[1] - s.p[1]) / length)
            n = (t[1], -t[0])
            face = face_of(profile, lambda ov: V(s.p[0] + ov[0] * n[0], y_plane + into * ov[1], s.p[1] + ov[0] * n[1]))
            out.append(face.extrude(V(s.q[0] - s.p[0], 0, s.q[1] - s.p[1])))
        else:
            turn = 1.0 if s.a1 > s.a0 else -1.0
            e = (math.cos(s.a0), math.sin(s.a0))
            face = face_of(profile, lambda ov: V(s.c[0] + (s.r + turn * ov[0]) * e[0], y_plane + into * ov[1],
                                                 s.c[1] + (s.r + turn * ov[0]) * e[1]))
            out.append(face.revolve(V(s.c[0], 0, s.c[1]), V(0, -turn, 0), math.degrees(abs(s.a1 - s.a0))))
    return out


def soft_edge_profile(c_in: float, c_back: float) -> Path:
    """What a soft edge removes: all outside a quarter ellipse that runs c_in on the face and c_back on the side."""
    a, e = (-c_in, 0.0), (0.0, c_back)
    return [Conic(a, (0.0, 0.0), e), *polygon([e, (OVER, c_back), (OVER, -OVER), (-c_in, -OVER), a])[:-1]]


def round_profile(r: float) -> Path:
    """What a plain rounded edge of radius r removes."""
    arc = Arc((-r, r), r, -math.pi / 2, 0.0)
    return [arc, *polygon([(0.0, r), (OVER, r), (OVER, -OVER), (-r, -OVER), (-r, 0.0)])[:-1]]


# ---------- the outlines of the arch, seen from the front, in (x, z) ----------

def cap_outline(d: Dims, st: HoodStations, below: float = 0.0) -> Outline:
    """The cap's sides and top, counter-clockwise from the foot of the right side to the foot of the left."""
    a = math.radians(d.hood_side_lean)
    xc, zc = st.corner_centre
    r = d.hood_corner_r
    right = Arc((xc, zc), r, a, math.pi / 2)
    left = Arc((-xc, zc), r, math.pi / 2, math.pi - a)
    foot = (st.half_base + below * math.tan(a), -below)
    return [Line(foot, right.at(a)), right, Line((xc, st.height), (-xc, st.height)), left,
            Line(left.at(left.a1), (-foot[0], foot[1]))]


def opening_outline(d: Dims, st: HoodStations, gap: float = 0.0) -> Outline:
    """The opening of the arch, counter-clockwise, drawn in by gap: the cap's outline offset by the bar, on a sill."""
    a = math.radians(d.hood_side_lean)
    xc, zc = st.corner_centre
    r_top = d.hood_corner_r - d.hood_bar - gap
    r_foot = d.hood_sill_corner_r - gap
    z0 = st.z_sill + gap
    side_x = lambda z: st.half_base - z * math.tan(a) - (d.hood_bar + gap) / math.cos(a)
    xf = side_x(z0 + r_foot) - r_foot / math.cos(a)
    foot_r = Arc((xf, z0 + r_foot), r_foot, -math.pi / 2, a)
    top_r = Arc((xc, zc), r_top, a, math.pi / 2)
    top_l = Arc((-xc, zc), r_top, math.pi / 2, math.pi - a)
    foot_l = Arc((-xf, z0 + r_foot), r_foot, math.pi - a, 1.5 * math.pi)
    return [Line((-xf, z0), (xf, z0)), foot_r, Line(foot_r.at(a), top_r.at(a)), top_r,
            Line((xc, zc + r_top), (-xc, zc + r_top)), top_l, Line(top_l.at(top_l.a1), foot_l.at(foot_l.a0)), foot_l]


def opening_half_width(d: Dims, st: HoodStations, z: float, gap: float = 0.0) -> float:
    """Half the clear width of the opening at height z."""
    a = math.radians(d.hood_side_lean)
    xc, zc = st.corner_centre
    r_top = d.hood_corner_r - d.hood_bar - gap
    if z > zc + r_top * math.sin(a):
        return xc + math.sqrt(max(r_top ** 2 - (z - zc) ** 2, 0.0))
    return st.half_base - z * math.tan(a) - (d.hood_bar + gap) / math.cos(a)


def front(y: float) -> Place:
    return lambda p: V(p[0], y, p[1])


def side(x: float) -> Place:
    return lambda p: V(x, p[0], p[1])


def prism_y(path: Path, y0: float, y1: float) -> Part.Shape:
    return face_of(path, front(y0)).extrude(V(0, y1 - y0, 0))


def prism_x(path: Path, half: float) -> Part.Shape:
    return face_of(path, side(-half)).extrude(V(2 * half, 0, 0))


# ---------- the cap ----------

def cap(d: Dims, st: HoodStations) -> Part.Shape:
    """The arch with its soft front edge, rounded rear edge, opening, rounded rim, rail and open floor."""
    closed = cap_outline(d, st)
    closed.append(Line(ends(closed[-1])[1], ends(closed[0])[0]))
    solid = prism_y(closed, 0.0, st.depth)
    run = cap_outline(d, st, below=6.0)
    tools = carry(soft_edge_profile(d.hood_edge_in, d.hood_edge_back), run, 0.0, 1.0)
    tools += carry(round_profile(d.hood_rear_r), run, st.depth, -1.0)
    tools.append(prism_y(opening_outline(d, st), -OVER, st.y_wall))
    tools += carry(round_profile(d.hood_rim_r), reverse(opening_outline(d, st)), 0.0, 1.0)
    xf = ends(opening_outline(d, st)[0])[1][0]
    y_sill = d.hood_ledge + d.hood_band_t / math.cos(math.radians(d.hood_band_tilt)) + 1.0
    tools.append(Part.makeBox(2 * xf, st.y_wall - y_sill, st.z_sill + 2 * OVER, V(-xf, y_sill, -OVER)))
    solid = solid.cut(tools)
    return solid.fuse(rail(d, st)).removeSplitter()


def rail(d: Dims, st: HoodStations) -> Part.Shape:
    """The small bar between the marquee and the hood band: a rounded nose, proud of both."""
    r = d.hood_rail_h / 2
    y_nose = st.y_band_top - d.hood_rail_proud
    y_back = st.y_band_top + d.hood_band_t / math.cos(math.radians(d.hood_band_tilt)) + 6.0
    zm = (st.z_band_top + st.z_rail_top) / 2
    nose = Arc((y_nose + r, zm), r, 1.5 * math.pi, 0.5 * math.pi)
    bar = [nose, *polygon([(y_nose + r, st.z_rail_top), (y_back, st.z_rail_top), (y_back, st.z_band_top),
                           (y_nose + r, st.z_band_top)])[:-1]]
    return common(prism_x(bar, st.half_base), prism_y(opening_outline(d, st, gap=-0.5), -OVER, st.depth))


# ---------- what stands in the arch ----------

def plane_frame(origin: Pt, tilt: float, faces_down: bool) -> FreeCAD.Matrix:
    """Frame of a tilted plane through origin (y, z): x across, y up the plane, z out toward the player.

    The hood band leans back (its top is behind its foot); the marquee faces down (its top is in front).
    """
    a = math.radians(tilt)
    up = (0.0, -math.sin(a), math.cos(a)) if faces_down else (0.0, math.sin(a), math.cos(a))
    out = (0.0, -math.cos(a), -math.sin(a)) if faces_down else (0.0, -math.cos(a), math.sin(a))
    m = FreeCAD.Matrix()
    m.A11, m.A12, m.A13, m.A14 = 1.0, up[0], out[0], 0.0
    m.A21, m.A22, m.A23, m.A24 = 0.0, up[1], out[1], origin[0]
    m.A31, m.A32, m.A33, m.A34 = 0.0, up[2], out[2], origin[1]
    return m


def placed(shape: Part.Shape, m: FreeCAD.Matrix) -> Part.Shape:
    s = shape.copy()
    s.transformShape(m)
    return s


def inset(points: list[Pt], by: float) -> list[Pt]:
    """A convex polygon (counter-clockwise) drawn in by a distance on every side."""
    lines = []
    for p, q in zip(points, points[1:] + points[:1]):
        length = math.dist(p, q)
        n = (-(q[1] - p[1]) / length, (q[0] - p[0]) / length)
        lines.append(((p[0] + by * n[0], p[1] + by * n[1]), (q[0] - p[0], q[1] - p[1])))
    out = []
    for (p, u), (q, w) in zip(lines[-1:] + lines[:-1], lines):
        k = ((q[0] - p[0]) * w[1] - (q[1] - p[1]) * w[0]) / (u[0] * w[1] - u[1] * w[0])
        out.append((p[0] + k * u[0], p[1] + k * u[1]))
    return out


def tablet(points: list[Pt], z0: float, z1: float, corner_r: float, edge_r: float, log: list[str], what: str) -> Part.Shape:
    """A raised form on a plane: a polygon with rounded corners, from z0 to z1, its top edge rounded."""
    solid = Part.Face(Part.makePolygon([V(x, y, z0) for x, y in points + points[:1]])).extrude(V(0, 0, z1 - z0))
    upright = [e for e in solid.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[-1].Point.z) > 1e-6]
    solid = try_fillet(solid, corner_r, upright, log, f"{what} corners")
    top = [e for e in solid.Edges if all(abs(v.Point.z - z1) < 1e-6 for v in e.Vertexes)]
    return try_fillet(solid, edge_r, top, log, f"{what} face edge") if edge_r > 0 else solid


def speaker_outline(d: Dims, st: HoodStations) -> list[Pt]:
    """The right-hand speaker form on the band plane: its outer end runs parallel to the leg of the arch."""
    b, a = math.radians(d.hood_band_tilt), math.radians(d.hood_side_lean)
    length = (st.z_band_top - st.z_sill) / math.cos(b)
    v0, v1 = d.speaker_foot_gap, length - d.speaker_head_gap
    wall = lambda v: opening_half_width(d, st, st.z_sill + v * math.cos(b)) - d.speaker_side_gap
    xi = d.logo_w / 2 + d.logo_gap
    return [(xi, v0), (wall(v0), v0), (wall(v1), v1), (xi, v1)]


def logo_outline(d: Dims, st: HoodStations) -> list[Pt]:
    length = (st.z_band_top - st.z_sill) / math.cos(math.radians(d.hood_band_tilt))
    v0, v1 = d.speaker_foot_gap + d.logo_end_gap, length - d.speaker_head_gap - d.logo_end_gap
    return [(-d.logo_w / 2, v0), (d.logo_w / 2, v0), (d.logo_w / 2, v1), (-d.logo_w / 2, v1)]


def marquee_window(d: Dims, st: HoodStations) -> tuple[float, float]:
    """Width and height of the straight window of the marquee, the widest that clears the corners of the arch."""
    z_top = st.z_rail_top + (d.marquee_margin + d.marquee_h) * math.cos(math.radians(d.marquee_tilt))
    half = opening_half_width(d, st, z_top, gap=d.hood_trim_gap + 0.5)
    return 2 * math.floor(half), d.marquee_h


def band_parts(d: Dims, st: HoodStations, log: list[str]) -> dict[str, Part.Shape]:
    """The hood band with its raised forms, the two speaker grilles and the logo plate."""
    b = math.radians(d.hood_band_tilt)
    tb = d.hood_band_t / math.cos(b)
    z0, z1 = st.z_sill, st.z_band_top - 0.5
    y = lambda z: st.y_band(z, d.hood_band_tilt)
    slab = prism_x(polygon([(y(z0), z0), (y(z1), z1), (y(z1) + tb, z1), (y(z0) + tb, z0)]), st.half_base)
    band = common(slab, prism_y(opening_outline(d, st, gap=d.hood_trim_gap), -OVER, st.depth))
    frame = plane_frame((st.y_band_foot, st.z_sill), d.hood_band_tilt, faces_down=False)
    out: dict[str, Part.Shape] = {}
    right = speaker_outline(d, st)
    forms = [("speaker_right", right, d.speaker_proud, d.grille_inset, d.grille_recess),
             ("speaker_left", [(-x, v) for x, v in reversed(right)], d.speaker_proud, d.grille_inset, d.grille_recess),
             ("logo_plate", logo_outline(d, st), d.logo_proud, d.logo_inset, 1.0)]
    for name, outline, h, margin, recess in forms:
        form = tablet(outline, -0.5, h, d.speaker_corner_r, d.speaker_edge_r, log, name)
        plate_outline = inset(outline, margin)
        pocket = tablet(plate_outline, h - recess - 2.0, h + OVER, d.speaker_corner_r - margin + 2.0, 0.0, log, f"{name} pocket")
        plate = tablet(plate_outline, h - recess - 2.0, h - recess, d.speaker_corner_r - margin + 2.0, 0.0, log, f"{name} plate")
        band = band.fuse(placed(form.cut(pocket), frame))
        out[name] = placed(plate, frame)
    return {"hood_band": band.removeSplitter(), **out}


def marquee_parts(d: Dims, st: HoodStations) -> dict[str, Part.Shape]:
    """The marquee: a cover whose ends follow the corners of the arch, and the straight window in it."""
    t = math.radians(d.marquee_tilt)
    tc = d.marquee_cover_t / math.cos(t)
    z0, z1 = st.z_rail_top + 0.5, st.z_open_top + OVER
    y = lambda z: st.y_marquee(z, d.marquee_tilt)
    slab = prism_x(polygon([(y(z0), z0), (y(z0) + tc, z0), (y(z1) + tc, z1), (y(z1), z1)]), st.half_base)
    cover = common(slab, prism_y(opening_outline(d, st, gap=d.hood_trim_gap), -OVER, st.depth))
    frame = plane_frame((st.y_marquee_bottom, st.z_rail_top), d.marquee_tilt, faces_down=True)
    w, h = marquee_window(d, st)
    window = placed(Part.makeBox(w, h, 1.0, V(-w / 2, d.marquee_margin, -1.0)), frame)
    return {"marquee_cover": cover.cut(window), "marquee": window}


def hood_parts(d: Dims, log: list[str]) -> dict[str, Part.Shape]:
    """Every part of the hood, in the cabinet frame."""
    st = hood_stations(d)
    parts = {"hood": cap(d, st), **band_parts(d, st, log), **marquee_parts(d, st)}
    move = FreeCAD.Matrix()
    move.move(V(*st.origin))
    for name, shape in parts.items():
        if not shape.isValid() or shape.Volume <= 0:
            log.append(f"{name}: the solid is not valid")
        parts[name] = placed(shape, move)
    return parts


# ---------- measurements of the built hood, cameras, and the data of the section sheet ----------

def span_y(shape: Part.Shape, x: float, z: float) -> list[tuple[float, float]]:
    """Where a line along y at (x, z) is inside the shape: sorted (y0, y1) spans."""
    probe = Part.makeLine(V(x, -1000.0, z), V(x, 2000.0, z))
    spans = [(e.BoundBox.YMin, e.BoundBox.YMax) for e in probe.common(shape).Edges]
    return sorted(spans)


def plan_outline(shape: Part.Shape, z: float) -> Part.Wire:
    """The largest loop of a horizontal slice, moved to z = 0."""
    wire = max(shape.slice(V(0, 0, 1), z), key=lambda w: w.BoundBox.DiagonalLength)
    wire.translate(V(0, 0, -z))
    return wire


def survey(d: Dims, shell: dict[str, Part.Shape]) -> dict:
    """Measured on the built solids: outside sizes, the shoulder, the clear depth behind the hood band, the trims."""
    st = hood_stations(d)
    bb = shell["hood"].BoundBox
    z0 = st.origin[2]
    xs = shell["speaker_right"].BoundBox.Center.x
    depths = []
    for x in (0.0, xs):
        for i in range(9):
            z = z0 + st.z_sill + 4.0 + (st.z_band_top - st.z_sill - 8.0) * i / 8
            band, cap_spans = span_y(shell["hood_band"], x, z), span_y(shell["hood"], x, z)
            behind = [s for s in cap_spans if band and s[0] > band[-1][1]]
            if band and behind:
                depths.append(behind[0][0] - band[-1][1])
    top = [e for e in shell["hood"].Edges if all(abs(v.Point.z - bb.ZMax) < 1e-4 for v in e.Vertexes)]
    shoulder = plan_outline(shell["body"], d.body_top - 0.05).distToShape(plan_outline(shell["hood"], z0 + 0.05))[0]
    w, h = marquee_window(d, st)
    size = lambda name: [round(shell[name].BoundBox.XLength, 1), round(shell[name].BoundBox.ZLength, 1)]
    return {"hood_height_over_body_top": round(bb.ZMax - d.body_top, 2), "hood_height_ratio": round((bb.ZMax - d.body_top) / d.width, 4),
            "hood_top_over_bezel_top_ratio": round((bb.ZMax - d.face(d.bezel_s1)[1]) / d.width, 4),
            "base_width": round(bb.XLength, 2), "depth": round(bb.YLength, 2),
            "top_flat_width": round(max((e.BoundBox.XLength for e in top), default=0.0), 2),
            "shoulder_min": round(shoulder, 2), "depth_behind_band_min": round(min(depths), 2) if depths else -1.0,
            "marquee_window": [round(w, 1), round(h, 1)], "marquee_modules": int(w // d.marquee_module),
            "speaker_grille": size("speaker_right"), "logo_plate": size("logo_plate")}


def focus_points(d: Dims) -> dict[str, dict]:
    """The hood cameras of the render harness: target, half width of the view, azimuth, elevation, picture shape."""
    st = hood_stations(d)
    _, y, z = st.origin
    yc = y + st.depth / 2 - 10.0
    w = d.width
    return {"hood-as-real": {"target": [0.0, yc, z + 22.0], "radius": 0.60 * w, "az": -32.0, "el": -3.0, "aspect": 0.66},
            "hood-speakers": {"target": [d.logo_w / 2, y + 20.0, z + 0.45 * st.height], "radius": 0.33 * w, "az": 66.0, "el": 6.0, "aspect": 0.7},
            "hood-as-photo-e": {"target": [10.0, yc, z + 24.0], "radius": 0.53 * w, "az": 41.0, "el": 15.0, "aspect": 0.62},
            "hood-front": {"target": [0.0, yc, z + 0.4 * st.height], "radius": 0.56 * w, "az": 0.0, "el": 0.0, "aspect": 0.5},
            "hood-side": {"target": [0.0, yc, z + 0.4 * st.height], "radius": 0.30 * w, "az": 90.0, "el": 0.0, "aspect": 1.0},
            "hood-under-brow": {"target": [0.0, yc, z + 0.45 * st.height], "radius": 0.56 * w, "az": 14.0, "el": -30.0, "aspect": 0.6},
            "cabinet-as-photo-b": {"target": [0.0, d.foot_y, (z + st.height) / 2 - 20.0], "radius": 0.60 * w, "az": 2.0, "el": 11.0, "aspect": 1.2}}


def section_data(d: Dims, shell: dict[str, Part.Shape]) -> dict:
    """True side sections (centre line, speaker), the front elevation and the plan at the seam, in the hood frame."""
    st = hood_stations(d)
    ox, oy, oz = st.origin
    names = ["hood", "hood_band", "speaker_right", "logo_plate", "marquee_cover", "marquee"]
    xs = shell["speaker_right"].BoundBox.Center.x
    data: dict = {"stations": st.__dict__, "dims": {k: getattr(d, k) for k in d.__dataclass_fields__},
                  "derived": {"width": d.width, "body_top": d.body_top, "hood_h": d.hood_h,
                              "recline": d.recline, "body_d": d.body_d, "seam_y": d.seam_y, "speaker_x": xs,
                              "bezel_w": d.bezel_w, "rail_t": d.rail_t},
                  "survey": survey(d, shell), "sections": {}, "elevation": {}, "plan": {}}
    for label, x in (("centre", 0.01), ("speaker", xs)):
        cut: dict[str, list] = {}
        for name in names + ["body", "bezel"]:
            loops = []
            for wire in shell[name].slice(V(1, 0, 0), x):
                pts = [[round(p.y - oy, 3), round(p.z - oz, 3)] for p in wire.discretize(Deflection=0.05)]
                if max(p[1] for p in pts) > -60.0:
                    loops.append(pts)
            cut[name] = loops
        data["sections"][label] = cut
    for name in names:
        lines = []
        for e in shell[name].Edges:
            pts = e.discretize(Deflection=0.1) if e.Length > 0.2 else []
            if pts and max(p.y for p in pts) - oy < st.y_band_top + 12.0:
                lines.append([[round(p.x, 2), round(p.z - oz, 2)] for p in pts])
        data["elevation"][name] = lines
    for name, z in (("body", d.body_top - 0.05), ("hood", oz + 0.05)):
        data["plan"][name] = [[round(p.x, 3), round(p.y - oy, 3)] for p in plan_outline(shell[name], z).discretize(Deflection=0.02)]
    loops = sorted(shell["hood"].slice(V(0, 0, 1), oz + 0.05), key=lambda w: w.BoundBox.DiagonalLength)[:-1]
    data["plan"]["hood_open"] = [[[round(p.x, 3), round(p.y - oy, 3)] for p in w.discretize(Deflection=0.05)] for w in loops]
    return data
