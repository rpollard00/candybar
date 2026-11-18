"""The cavity inside the outer form: where the skin of wall_t leaves room for the hardware.

The cavity is an inward offset of the outer form by wall_t, made from offset side sections. The outer parts are
cut by planes square to X (a side section each SLAB apart). Each section is offset inward by wall_t in its own plane,
which is exact in Y and Z. For a slab between two planes, the cavity is the common of the offset sections over the
slab and wall_t on each side of it, so a point of the slab is at least wall_t from the outer surface
in X too (between two planes a face that turns across X can come nearer by a small part of a SLAB; measure_wall
measures the wall that results). On faces that turn across X (the sides of the tuck, the rail edge, the soft edges
and bevels of the hood, the corners of the deck) the wall comes out thicker than wall_t.

The cavity reads the hood before its edge break (form_parts). The break of the hood is cut by lofts, and a section
through a loft is a spline: the offset of a section with these splines fails at some planes, and then a slab has no
cavity. The wall is not thinner for it: the break is on convex edges, where the wall is thicker than wall_t.

Two openings go through the skin, because a plate closes them: under the control panel, inside a ledge of
panel_ledge on which the plate rests (the outline of the plate, profiles.panel_outline, moved in), and behind the bezel plate, inside a ledge of bezel_ledge. The body top is
open into the hood: the seam gap is filled before the offset.

The skin is the outer form less the cavity (hollow). Two things make that cut work:
  RIDGE     Where the form does not turn across X, two neighbour slabs have the same section, and where it starts to
            turn, their outlines part on a tangent. The face of the step between them then ends in a point of zero
            angle, or its outline goes through one point twice, and OpenCascade cannot orient such a face: the skin
            is not a valid shape. Thus every second slab stands RIDGE farther in. Two neighbour outlines then cross
            at an angle or do not meet, and the step between them is a ring. The wall of every second slab is RIDGE
            thicker than wall_t.
  CUT_STEP  One boolean with all the prisms of the cavity (255 on the body) took 12.8 GB of memory and did not end.
            The prisms are cut away CUT_STEP at a time; the result is the same solid.

Two things keep the skin sound:
  sound     The 2D offset of OpenCascade makes the offset of a spline or an ellipse as an offset curve that is only
            C0 at the knots of its basis, and whose curve on the plane does not follow it; at a corner where two edges
            meet nearly tangent it adds a join arc of about 1e-6 mm. The mesh of a piece of the split then put a node
            of a step face hundreds of mm off it, at a place that changed from run to run. Each offset curve becomes
            arcs through points of the exact offset (within ARC_TOL), with their corners where the section of the face
            crosses a fixed family of lines (Grid): a neighbour section cuts the same face and has its corners on the
            same lines, so two neighbour outlines run side by side piece by piece, and their common has no tiny edges.
  absorb    Where the form turns across X and takes RIDGE back, two neighbour outlines can run a few 0.0001 mm apart;
            the step between them is then a strip that the mesh of a part leaves open. A thin part (under THIN) of the
            difference between two neighbour regions is absorbed into the later one, which takes the outline of the
            earlier one there.
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
# distance between two section planes; the first slab spans the centre line
SLAB = 1.0
# the outer parts that make the skin; the bezel and the control panel are plates that close openings in it
SKIN = ("deck", "body", "hood", "marquee_lip")
# the same section when its area and its bounding box agree to this, in mm2 and mm
SAME = 1e-3
# the fuzzy tolerance of a boolean that failed without it, mm
FUZZY = 1e-3
# a section whose offset fails is offset again as a polygon that stands at most this far off its edges; and the
# shortest radius of a face sets the longest piece between two corners of its offset by this deflection, mm
POLY_DEFLECTION = 0.02
# the offset of a section is made sound (sound): its offset curves become arcs with their corners on the grid of
# their faces, at most ARC_STEP longest pieces apart; an arc stands at most ARC_TOL off the curve; an arc shorter than
# JOIN_ARC is the join at a corner where two edges meet nearly tangent; an offset curve shorter than SHORT_CURVE is a
# line; DENSE points of a curve find where it crosses the grid, mm
ARC_STEP = 4.0
ARC_TOL = 0.005
JOIN_ARC = 1e-3
SHORT_CURVE = 1e-2
DENSE = 400
# two neighbour slabs whose outlines run closer than this take one outline (absorb), mm
THIN = 0.01
# every second slab of the cavity stands this far inside the offset by wall_t, so that no two neighbour slabs share
# a part of their outline (see the module text), mm
RIDGE = 0.05
# the prisms of the cavity are cut from a solid this many at a time
CUT_STEP = 12


@dataclass(frozen=True)
class Openings:
    """Where the skin is open under a plate: the plate rests on a ledge of this width round the opening."""
    panel_ledge: float = 8.0
    # behind the bezel the opening must take any 16:10 monitor with its adjustment and its plug space on both sides
    # (2 x 210 wide); the bezel plate is 434.7 wide. The plate rests on a ledge at its top and bottom only (the owner,
    # 2026-11-11): at its sides the flanges of the monitor carrier hold it, so that the monitor comes out to the front
    # with 7.3 to spare on each side
    bezel_ledge: float = 6.0
    bezel_side_ledge: float = 0.0


@dataclass
class Cavity:
    """The cavity as solids, the skin left round it as prisms of the same slabs, and the slabs themselves: x0, x1,
    the cavity's section and the outer section, both in the plane x = 0. The outer face of the skin prisms steps by
    SLAB where the form turns across X; their inner face is the cavity's."""
    pieces: list[Part.Shape]
    walls: list[Part.Shape]
    slabs: list[tuple[float, float, Part.Shape | None, Part.Shape]]

    @property
    def shape(self) -> Part.Shape:
        return Part.makeCompound(self.pieces)


def seam_filler(parts: dict[str, Part.Shape], d: Blueprint) -> Part.Shape:
    """The seam gap between the body top and the foot of the hood, filled, so that the cavity runs on into the hood."""
    e = SAME * 10
    z = d.body_top - e
    faces = [Part.Face(w) for w in parts["body"].slice(V(0, 0, 1), z)]
    top = faces[0].fuse(faces[1:]).removeSplitter() if len(faces) > 1 else faces[0]
    return top.extrude(V(0, 0, d.seam_gap + 2 * e))


def form_parts(parts: dict[str, Part.Shape], d: Blueprint) -> list[Part.Shape]:
    """The skin parts as the cavity reads them: the built parts, with the hood as it is before its edge break (the
    cap of solids.cap_unbroken, which the build breaks as its last step)."""
    h = pr.hood(d)
    hood = so.hood_frame(h)(so.cap_unbroken(d, h)[0])
    skin = so.skin_parts(d, parts)
    return [hood if k == "hood" else skin[k] for k in SKIN]


def section(skin: list[Part.Shape], x: float) -> Part.Shape | None:
    """The side section of the skin parts at x, as faces in the plane x."""
    faces = []
    for shape in skin:
        wires = shape.slice(V(1, 0, 0), x)
        if wires:
            faces.append(Part.makeFace(wires, "Part::FaceMakerBullseye"))
    if not faces:
        return None
    return faces[0].fuse(faces[1:]).removeSplitter() if len(faces) > 1 else faces[0]


def closed_points(wire: Part.Wire) -> list[FreeCAD.Vector]:
    pts = wire.discretize(Deflection=POLY_DEFLECTION)
    return pts if (pts[0] - pts[-1]).Length < 1e-6 else pts + [pts[0]]


class Grid:
    """The corners of the offset of a section: for each face of the skin parts, a family of lines in the plane of a
    section (y = k * step, or z = k * step: the one across which the section of the face runs, from its normal at its
    centre), and the longest piece between two corners (from its smallest radius). A neighbour section cuts the same
    face, so it has its corners on the same lines: two neighbour outlines run side by side piece by piece."""

    def __init__(self, shapes: list[Part.Shape]) -> None:
        self.faces = [(f, f.BoundBox) for s in shapes for f in s.Faces if not isinstance(f.Surface, Part.Plane)]
        self.rules: dict[int, tuple[int, float, float]] = {}

    def face_of(self, edge: Part.Edge) -> Part.Face | None:
        mid = edge.valueAt(edge.getParameterByLength(edge.Length / 2))
        best, dist = None, math.inf
        for f, b in self.faces:
            if b.XMin - 0.01 <= mid.x <= b.XMax + 0.01 and b.YMin - 0.01 <= mid.y <= b.YMax + 0.01 and b.ZMin - 0.01 <= mid.z <= b.ZMax + 0.01:
                dd = f.distToShape(Part.Vertex(mid))[0]
                if dd < dist:
                    best, dist = f, dd
        return best if dist < 1e-3 else None

    def rule(self, f: Part.Face) -> tuple[int, float, float]:
        """(1 for lines y = k * step, 2 for z = k * step; step; the longest piece), fixed for the face."""
        key = f.hashCode()
        if key not in self.rules:
            s = f.Surface
            u0, u1, v0, v1 = f.ParameterRange
            n = f.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
            axis = 1 if abs(n.z) > abs(n.y) else 2
            rmin = 1e6
            for i in range(7):
                for j in range(7):
                    u, v = u0 + (u1 - u0) * (i + 0.5) / 7, v0 + (v1 - v0) * (j + 0.5) / 7
                    try:
                        c = max(abs(s.curvature(u, v, "Max")), abs(s.curvature(u, v, "Min")))
                    except (Part.OCCError, RuntimeError):
                        continue
                    if c > 1e-9:
                        rmin = min(rmin, 1 / c)
            piece = ARC_STEP * max(0.1, min(20.0, math.sqrt(8 * POLY_DEFLECTION * rmin)))
            self.rules[key] = (axis, piece * 0.7, piece)
        return self.rules[key]

    def params(self, curve, t0: float, t1: float) -> list[float]:
        """The parameters in (t0, t1) of the corners of a section curve: where it crosses the lines of its face, and
        more where two of them stand farther apart than the longest piece, evenly by length."""
        import bisect

        edge = Part.Edge(curve, t0, t1)
        if edge.Length < SHORT_CURVE:
            return []
        f = self.face_of(edge)
        axis, step, piece = self.rule(f) if f is not None else (2, 1.0, ARC_STEP)
        ts = [t0 + (t1 - t0) * i / DENSE for i in range(DENSE + 1)]
        ps = [curve.value(t) for t in ts]
        vals = [(q.y if axis == 1 else q.z) / step for q in ps]
        cut = {t0, t1}
        for i in range(DENSE):
            g0, g1 = vals[i], vals[i + 1]
            lo, hi = sorted((g0, g1))
            if hi - lo > 1e-15:
                for n in range(math.floor(lo) + 1, math.floor(hi) + 1):
                    cut.add(ts[i] + (n - g0) / (g1 - g0) * (ts[i + 1] - ts[i]))
        acc = [0.0]
        for i in range(DENSE):
            acc.append(acc[-1] + (ps[i + 1] - ps[i]).Length)

        def length_at(t: float) -> float:
            x = (t - t0) / (t1 - t0) * DENSE
            i = min(int(x), DENSE - 1)
            return acc[i] + (x - i) * (acc[i + 1] - acc[i])

        def param_at(length: float) -> float:
            i = min(max(bisect.bisect_left(acc, length) - 1, 0), DENSE - 1)
            span = acc[i + 1] - acc[i]
            return ts[i] + (0.0 if span <= 0 else (length - acc[i]) / span) * (ts[i + 1] - ts[i])

        out = []
        cut = sorted(cut)
        for a, b in zip(cut, cut[1:]):
            la, lb = length_at(a), length_at(b)
            m = max(1, math.ceil((lb - la) / piece))
            out += [param_at(la + (lb - la) * k / m) for k in range(1, m)] + [b]
        return [t for t in out if t0 < t < t1]


def arcs(e: Part.Edge, a: FreeCAD.Vector, b: FreeCAD.Vector, grid: Grid) -> list[Part.Edge]:
    """An offset curve from a to b as arcs (a line where the curve is that straight) through its corners on the grid
    and the point of the exact offset halfway between two corners; a piece whose arc stands more than ARC_TOL off
    the curve at a quarter is cut in two."""
    base = getattr(e.Curve, "BasisCurve", None) or e.Curve
    t0, t1 = e.FirstParameter, e.LastParameter
    params = [t0] + grid.params(base, t0, t1) + [t1]
    if (e.valueAt(t0) - a).Length > (e.valueAt(t1) - a).Length:
        params.reverse()
    out: list[Part.Edge] = []

    def piece(tp: float, tq: float, p: FreeCAD.Vector, q: FreeCAD.Vector, depth: int = 0) -> None:
        if (q - p).Length < 1e-9:
            return
        tm = (tp + tq) / 2
        m = e.valueAt(tm)
        quarters = [e.valueAt(tp + (tq - tp) * k) for k in (0.25, 0.75)]
        if (m - (p + q) * 0.5).Length <= ARC_TOL:
            line = Part.makeLine(p, q)
            if depth >= 6 or max(line.distToShape(Part.Vertex(c))[0] for c in quarters) <= ARC_TOL:
                out.append(line)
                return
        else:
            try:
                arc = Part.Arc(p, m, q).toShape()
            except Part.OCCError:
                arc = None
            if arc is not None and (depth >= 6 or max(arc.distToShape(Part.Vertex(c))[0] for c in quarters) <= ARC_TOL):
                out.append(arc)
                return
        piece(tp, tm, p, m, depth + 1)
        piece(tm, tq, m, q, depth + 1)

    pts = [e.valueAt(t) for t in params]
    pts[0], pts[-1] = a, b
    for (tp, tq), (p, q) in zip(zip(params, params[1:]), zip(pts, pts[1:])):
        piece(tp, tq, p, q)
    return out


def sound(face: Part.Face, grid: Grid) -> Part.Face:
    """An offset face (makeOffset2D) with each offset curve made arcs on the grid (arcs); the lines and the arcs of
    the offset stay, but a join arc shorter than JOIN_ARC goes and its two neighbours meet at one point.

    The 2D offset of OpenCascade makes the offset of a spline or an ellipse as an offset curve that is only C0 at the
    knots of its basis, and its curve on the plane does not follow it (BOPAlgo_InvalidCurveOnSurface); at a corner
    where two edges meet nearly tangent it adds a join arc of about 1e-6 mm (BOPAlgo TooSmallEdge). The skin had step
    faces with such edges, and the mesh of a piece of the split put a node of such a face hundreds of mm off it, at a
    place that changed from run to run."""
    wires = []
    for wire in face.Wires:
        edges, vs = wire.OrderedEdges, [v.Point for v in wire.OrderedVertexes]
        items = []      # [kind, edge, start, end]
        for i, e in enumerate(edges):
            a, b = vs[i], vs[(i + 1) % len(vs)]
            if isinstance(e.Curve, Part.Circle):
                if e.Length >= JOIN_ARC:
                    items.append(["arc", e, a, b])
            elif isinstance(e.Curve, Part.Line) or e.Length < SHORT_CURVE:
                items.append(["line", e, a, b])
            else:
                items.append(["curve", e, a, b])
        # neighbours meet at one point: the end of an arc, else the end of the edge before
        for k, cur in enumerate(items):
            nxt = items[(k + 1) % len(items)]
            joint = nxt[2] if nxt[0] == "arc" and cur[0] != "arc" else cur[3]
            cur[3] = joint
            if nxt[0] != "arc":
                nxt[2] = joint
        out = []
        for kind, e, a, b in items:
            if kind == "arc":
                out.append(e)
            elif kind == "line":
                if (b - a).Length > 1e-9:
                    out.append(Part.makeLine(a, b))
            else:
                out += arcs(e, a, b, grid)
        wires.append(Part.Wire(out))
    return Part.makeFace(wires, "Part::FaceMakerBullseye")


# the grid of the parts that build() reads, for inner (a module variable: width_run replaces inner(face, x, w))
_GRID: Grid | None = None


def inner(face: Part.Shape | None, x: float, w: float) -> Part.Shape | None:
    """The section offset inward by w, moved into the plane x = 0, with its edges made sound (sound): the inner face
    of the wall stands at most ARC_TOL off the exact offset."""
    if face is None:
        return None
    out = []
    for f in face.Faces:
        try:
            off = f.makeOffset2D(-w, 0, False, False, False)
            out.append(Part.makeCompound([sound(g, _GRID) for g in off.Faces]) if _GRID is not None else off)
            continue
        except (FreeCAD.Base.CADKernelError, Part.OCCError, ValueError, RuntimeError):
            pass
        # the offset of a section through a lofted surface (the rear corner rounds) can fail on its spline edges:
        # try again on the same outline as a polygon within POLY_DEFLECTION of it; when that fails too, the face is
        # thinner than 2 w and nothing is left of it
        try:
            wires = [Part.makePolygon(closed_points(wi)) for wi in f.Wires]
            out.append(Part.makeFace(wires, "Part::FaceMakerBullseye").makeOffset2D(-w, 0, False, False, False))
        except (FreeCAD.Base.CADKernelError, Part.OCCError, ValueError, RuntimeError):
            continue
    out = [s for s in out if s.Faces and s.Area > SAME]
    if not out:
        return None
    shape = out[0].fuse(out[1:]) if len(out) > 1 else out[0]
    return shape.translated(V(-x, 0, 0))


def common(faces: list[Part.Shape | None]) -> Part.Shape | None:
    """The common of the sections. Two sections that share edges can make the boolean fail and return nothing;
    then it runs again with a fuzzy tolerance of FUZZY. (The fuzzy common is not the first try: on the body at x 233 it
    returned 12059 mm2 where the plain common gives the 108981 of the offset.)"""
    if any(f is None for f in faces):
        return None
    out = faces[0]
    for f in faces[1:]:
        both = out.common(f)
        if both.isNull() or both.Area < SAME:
            both = out.common([f], FUZZY)
        if both.isNull() or both.Area < SAME:
            return None
        out = both
    return out


def thin(face: Part.Face) -> bool:
    return face.Area / max(face.Length / 2, 1e-12) < THIN


def absorb(regions: list[Part.Shape | None]) -> list[Part.Shape | None]:
    """Each region with the thin parts of its difference from the region before it absorbed: where two neighbour
    outlines run closer than THIN (the form turns across X and takes RIDGE back), the step between them would be a
    strip of a few 0.0001 mm, which the mesh of a part leaves open; the later region takes the outline of the earlier
    one there."""
    out = list(regions)
    for k in range(1, len(out)):
        a, b = out[k - 1], out[k]
        if a is None or b is None:
            continue
        add = [f for f in a.cut(b).Faces if thin(f)]
        take = [f for f in b.cut(a).Faces if thin(f)]
        if add:
            b = b.fuse(add).removeSplitter()
        if take:
            b = b.cut(take).removeSplitter()
        out[k] = b
    return out


def same(a: Part.Shape | None, b: Part.Shape | None) -> bool:
    if a is None or b is None:
        return a is b
    ba, bb = a.BoundBox, b.BoundBox
    return abs(a.Area - b.Area) < SAME and all(abs(p - q) < SAME for p, q in zip((ba.YMin, ba.YMax, ba.ZMin, ba.ZMax), (bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)))


def openings(d: Blueprint, o: Openings, parts: dict[str, Part.Shape] | None = None) -> list[Part.Shape]:
    """The skin removed under the control panel and behind the bezel plate, inside their ledges (the bezel's at its
    top and bottom only), through the wall at the hole of the latch's button (solids.latch_button_hole), and through
    the band wall of the hood at the openings of the hood band, with the stand-in of the lip in front of it
    (band.skin_cutters)."""
    w = d.wall_t
    z1 = d.panel_top - d.panel_t
    panel = so.prism(so.poly(pr.panel_outline(d, -o.panel_ledge)), so.xy(z1 - w - SLAB), V(0, 0, w + SLAB))
    bx = d.bezel_w / 2 - o.bezel_side_ledge
    s0, s1 = d.bezel_s0 + o.bezel_ledge, d.bezel_s1 - o.bezel_ledge
    origin, up, into = so.screen_frame(d)
    # the face of the body behind the plate lies screen_t behind the screen face; the opening goes SLAB into the cavity
    bezel = so.slab(origin, up, into, (-bx, bx), (s0, s1), (d.mon_setback, d.mon_setback + d.screen_t + w + SLAB))
    from . import band  # noqa: PLC0415

    out = [panel, bezel, *band.skin_cutters(d)]
    if parts is not None and "deck" in parts:
        hole = so.latch_button_hole(d, parts["deck"], w + SLAB + 5.0)
        if hole is not None:
            out.append(hole[0])
    return out


def prisms(region: Part.Shape, x0: float, x1: float) -> list[Part.Shape]:
    """A section in the plane x = 0 made solid from x0 to x1 and from -x1 to -x0; one prism across the centre line."""
    if x0 == 0:
        return [region.translated(V(-x1, 0, 0)).extrude(V(2 * x1, 0, 0))]
    return [region.translated(V(x, 0, 0)).extrude(V(x1 - x0, 0, 0)) for x in (x0, -x1)]


def build(parts: dict[str, Part.Shape], d: Blueprint, o: Openings = Openings()) -> Cavity:
    """The cavity of the skin parts, as slabs symmetric about the centre line plus the two openings."""
    global _GRID
    w = d.wall_t
    skin = form_parts(parts, d) + [seam_filler(parts, d)]
    _GRID = Grid(skin)
    half = max(s.BoundBox.XMax for s in skin)
    n = math.ceil(half / SLAB) + 1
    reach = math.ceil(w / SLAB)
    outer = {i: section(skin, i * SLAB) for i in range(n + reach + 1)}
    offs = {i: inner(f, i * SLAB, w) for i, f in outer.items()}
    rows = []
    for i in range(n):
        window = [offs[abs(j)] for j in range(i - reach, i + reach + 2)]
        face = outer[i].translated(V(-i * SLAB, 0, 0)) if outer[i] is not None else None
        rows.append((common(window), face))
    holes = [i for i in range(1, n - 1) if rows[i][0] is None and rows[i - 1][0] is not None and rows[i + 1][0] is not None]
    if holes:
        raise RuntimeError(f"the cavity has no section at x = {', '.join(str(i * SLAB) for i in holes)}, between two that have one")
    slabs = []
    i = 0
    while i < n:
        j = i
        while j + 1 < n and same(rows[i][0], rows[j + 1][0]) and same(rows[i][1], rows[j + 1][1]):
            j += 1
        if rows[i][1] is not None:
            slabs.append((i * SLAB, (j + 1) * SLAB, *rows[i]))
        i = j + 1
    # every second slab stands RIDGE farther in (see the module text): its region comes from the same sections,
    # offset by w + RIDGE
    far: dict[int, Part.Shape | None] = {}

    def ridge(i: int) -> Part.Shape | None:
        window = [abs(j) for j in range(i - reach, i + reach + 2)]
        for j in window:
            if j not in far:
                far[j] = inner(outer[j], j * SLAB, w + RIDGE)
        return common([far[j] for j in window])

    stepped = [(x0, x1, ridge(round(x0 / SLAB)) if k % 2 and region is not None else region, face) for k, (x0, x1, region, face) in enumerate(slabs)]
    lost = [x0 for (x0, _, region, _), (_, _, before, _) in zip(stepped, slabs) if region is None and before is not None]
    if lost:
        raise RuntimeError(f"the cavity has no section for the slabs at x = {', '.join(f'{x:g}' for x in lost)}: the offset by wall_t + RIDGE failed there")
    slabs = [(x0, x1, region, face) for (x0, x1, _, face), region in zip(stepped, absorb([r for _, _, r, _ in stepped]))]
    cut = openings(d, o, parts)
    pieces = [p for x0, x1, region, _ in slabs if region is not None for p in prisms(region, x0, x1)] + cut
    walls = []
    for x0, x1, region, face in slabs:
        for p in prisms(face.cut(region) if region is not None else face, x0, x1):
            tools = [c for c in cut if c.BoundBox.intersect(p.BoundBox)]
            walls.append(p.cut(tools) if tools else p)
    return Cavity(pieces, walls, slabs)


def hollow(outer: Part.Shape, cav: Cavity, step: int = CUT_STEP) -> Part.Shape:
    """A solid of the outer form less the cavity: its skin. The prisms of the cavity that reach the solid are cut
    away `step` at a time (see CUT_STEP). A skin that is not a valid shape is an error."""
    box = outer.BoundBox
    tools = [p for p in cav.pieces if p.BoundBox.intersect(box)]
    skin = outer
    for i in range(0, len(tools), step):
        skin = skin.cut(tools[i:i + step])
    if not skin.isValid():
        bad = [f for f in skin.Faces if not f.isValid()]
        where = "; ".join(f"({c.x:.1f}, {c.y:.1f}, {c.z:.1f})" for c in (f.BoundBox.Center for f in bad[:6]))
        raise RuntimeError(f"the skin is not a valid shape: {len(bad)} of its {len(skin.Faces)} faces are not valid, at {where}")
    return skin


def outer_faces(parts: dict[str, Part.Shape], filler: Part.Shape) -> Part.Shape:
    """The faces of the skin parts that lie on the outside of the form: not those where two parts meet, nor those in
    the filled seam."""
    skin = [parts[k] for k in SKIN] + [filler]
    out = []
    for k in SKIN:
        others = [s for s in skin if s is not parts[k]]
        for f in parts[k].Faces:
            u0, u1, v0, v1 = f.ParameterRange
            p = f.valueAt((u0 + u1) / 2, (v0 + v1) / 2)
            n = f.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
            probes = (p + n * (SAME * 10), p - n * (SAME * 10))
            if not any(o.isInside(q, SAME, True) for o in others for q in probes):
                out.append(f)
    return Part.makeCompound(out)


def measure_wall(parts: dict[str, Part.Shape], cav: Cavity, filler: Part.Shape, step: float, every: int) -> list[tuple[float, FreeCAD.Vector]]:
    """The distance from points on the cavity's side faces (at the middle of every slab wider than `every` SLAB and
    of every `every`-th narrow one, about step apart) to the outer faces of the skin. A face that another part covers
    in part (the band behind the marquee lip) is outer elsewhere; a nearest point on two parts at once is under such
    a cover, and the point is not counted."""
    surface = outer_faces(parts, filler)
    skin = [parts[k] for k in SKIN] + [filler]
    out = []
    for k, (x0, x1, region, _) in enumerate(cav.slabs):
        if region is None or (x1 - x0 <= every * SLAB and k % every):
            continue
        x = (x0 + x1) / 2
        for edge in region.Edges:
            for p in edge.discretize(Distance=step):
                q = V(x, p.y, p.z)
                dist, pairs, _ = surface.distToShape(Part.Vertex(q))
                if sum(sh.isInside(pairs[0][0], SAME, True) for sh in skin) < 2:
                    out.append((dist, q))
    return out
