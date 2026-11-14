"""The print pieces with their joints: joint 1 of joints.py made on every bonded seam of the split.

split.py cuts the hollow skin into plain pieces. This module reads that cut and gives each piece what decision
record 0006 asks for: a flange on the inside of each seam (with its 45 degree gusset), the key and the groove that
locate the two pieces, the screws that clamp them, and the V on the outside for the filler. It also makes the printed
floor (ten millimetres, with half-laps and a rebate for the foot flange of the walls) and the ribs of the large walls.

The generator works in the plane of a seam. A plain piece has one flat cut face on each seam polygon (the section of
its wall). The edges of that face which lie on the outside of the form are the outer line of the seam. The outer
line is made simple (straight segments and arcs of a large radius: an edge break or a small step becomes a sharp
corner, a tight curve becomes chords). A section of joints.Joint in (u, z), u inward from the outer face and z into
the piece, is then carried along each segment, and turned about each corner where the segments open; all of these
are fused, and the form and the other seams trim the result:

    flange    u 0.5 .. wall_t + flange_h, flange_t deep into the piece
    gusset    from the flange tip (at flange_t) to the wall (at flange_t + gusset_leg): 45 degrees
    key       u key_u, key_proj high, on the piece with the pilot holes
    groove    the key with the clearance, in the piece with the screw heads
    screws    on the line u = screw_u, square to the seam plane
    rebate    on the outer line, for the seams that are filled (it replaces the V of the joint sheet)

The same code makes a straight seam, a seam in a crease (the wall of one piece leaves the seam plane at 45 degrees:
that side gets a band outside the outer line too, and the form trims it) and the place where three pieces meet (the
flange of each piece ends at the cut face of the next seam, and the flanges of two seams on one piece fuse into a
corner).

    CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh candybar.shell.pieces

CANDYBAR_PIECES names what to build: "pilot" (the two pilot pairs), "all" (default), or piece names separated by
commas. No FreeCAD at import.
"""
from __future__ import annotations

import json
import math
import os
import time
from dataclasses import dataclass, field, replace
from pathlib import Path

from . import split
from .dims import Blueprint
from .joints import JOINT, OTHER_JOINTS, Joint

CAD = Path(__file__).resolve().parents[2]
SHARED = Path(os.environ.get("CANDYBAR_SHARED") or Path.home() / ".local/share/candybar/out/shell-rev7")


@dataclass(frozen=True)
class Build:
    """The values of this module, mm. The joint values are in joints.py; these say how the joint goes on a seam."""
    crease_band: float = 8.0       # a side whose wall leaves the seam plane outward: the flange starts this far outside the outer line
    skin_lap: float = 0.5          # the flange starts this far inside the outer face, so that the fuse has no sliver
    small_edge: float = 4.5        # an edge of the outer line shorter than this is an edge break or a step: it becomes a corner
    arc_r: float = 25.0            # an arc of at least this radius stays an arc; a tighter curve becomes chords
    chord: float = 6.0             # of at most this length
    end_drop: float = 12.0         # a tail of the outer line shorter than this, behind an edge break, is a corner of the form: it is left out
    end_reach: float = 20.0        # and the line goes on straight by this much; the form trims it
    seam_reach: float = 20.0       # the cut faces of the other seams reach this far past their polygons when they trim a flange
    run_screw: float = 22.0        # a run of flange shorter than this has no screw
    run_key: float = 20.0          # and shorter than this, no key
    run_flange: float = 8.0        # and shorter than this, no flange
    screw_end: float = 12.0        # a screw axis stays this far from the end of its run
    wall_left: float = 1.2         # a hole or a pocket leaves this much of the skin to the outside
    driver_d: float = 8.0          # the shaft of the screwdriver (a 1/4 inch bit holder)
    driver_len: float = 80.0       # the clear length that it needs behind the screw head
    hardware_gap: float = 2.0      # a flange stays this far from the hardware and the keep-out zones of fit.Layout
    door_stop: float = 10.0        # the flanges stop this far from the opening of the rear door (another package)
    floor_gap: float = 0.3         # the wall flanges stop this far above the printed floor
    clash_mm3: float = 1.0         # a common volume larger than this is a clash
    debris_mm3: float = 2.0        # a solid smaller than this, left by a cut, is debris


BUILD = Build()
PILOT = (("D2 R", ("deck side R", "lower R")), ("B1 R", ("middle R", "upper R")))


def joint() -> Joint:
    """The joint of the cabinet. The pilot hole is open until the coupon decides; the pieces are modelled with the
    table value for PET (ASSUMPTION: PETG behaves as PET)."""
    return replace(JOINT, pilot_d=JOINT.pilot_d_pet)


# ---------- the plain pieces, from the cache ----------

def cache_dir(out: Path) -> Path:
    return out / "cache"


def load_binary(path: Path):
    import Part  # noqa: PLC0415

    s = Part.Shape()
    s.importBinary(str(path))
    return s


def outer_parts() -> dict:
    """The outer solids of the default build. They are read from the shared build (text BREP), because the default
    build does not end on every machine (the edge break of the hood)."""
    import Part  # noqa: PLC0415

    from . import solids as so  # noqa: PLC0415

    names = ("deck", "body", "hood", "marquee_lip", "speaker_right", "speaker_left", "logo_form", "bezel")
    here = Path(os.environ.get("CANDYBAR_SHELL", CAD / "out" / "shell-rev7"))
    folder = next((f for f in (here, SHARED) if all((f / f"{k}.brep").exists() for k in names)), None)
    if folder is None:
        return so.build(Blueprint()), so
    parts = {}
    for k in names:
        parts[k] = Part.Shape()
        parts[k].read(str(folder / f"{k}.brep"))
    return parts, so


def modules(d: Blueprint, log=print) -> split.Modules:
    """As split.build_modules, from the outer solids on disk and the skin in the cache. A skin that OpenCascade reads
    as not valid (faces that it cannot orient) is repaired with ShapeFix; the repair does not change its volume."""
    import Part  # noqa: PLC0415

    parts, so = outer_parts()
    skin = {}
    for k, f in split.skin_files(d).items():
        if not f.exists():
            raise FileNotFoundError(f"pieces: the skin {f} is not in the cache; run candybar.shell.split first")
        skin[k] = Part.Shape()
        skin[k].importBinary(str(f))
        if not skin[k].isValid():
            v = skin[k].Volume
            skin[k].fix(1e-7, 1e-7, 1e-2)
            log(f"pieces: the skin of {k} was not valid as read; repaired, volume change {skin[k].Volume - v:.3f} mm3, valid {skin[k].isValid()}")
    body = so.unsplit(parts["deck"].fuse(parts["body"]))
    hood = so.unsplit(parts["hood"].fuse(parts["marquee_lip"]))
    outer = {"body": body, "base": body, "hood": hood}
    for k in split.TRIMS:
        skin[k] = outer[k] = parts[k]
    return split.Modules(skin, outer, parts, split.fingerprint(d))


@dataclass
class Plain:
    """The plain cut: each piece, the outer solid of each module, and the data of the split."""
    shapes: dict
    outer: dict
    seams: list
    pieces: list
    key: str


def plain(d: Blueprint, out: Path, log=print) -> Plain:
    """The plain pieces of split.cut. They are kept in out/cache under the fingerprint of the skin and of the seam
    data, because the cut takes three minutes."""
    import hashlib  # noqa: PLC0415

    seams, pieces = split.expanded(split.layout(d))
    key = hashlib.sha256((split.fingerprint(d) + repr(seams) + repr(pieces) + str(split.KERF)).encode()).hexdigest()[:16]
    here = cache_dir(out) / key
    names = [p.full for p in pieces]
    files = {n: here / (n.replace(" ", "_") + ".bin") for n in names}
    outer_files = {k: here / f"outer_{k}.bin" for k in ("body", "hood")}
    if not all(f.exists() for f in list(files.values()) + list(outer_files.values())):
        log("pieces: cutting the skin (about 3 minutes)")
        mods = modules(d, log)
        shapes, problems = split.cut(seams, pieces, mods)
        if problems:
            raise RuntimeError(f"pieces: the cut has problems: {problems}")
        here.mkdir(parents=True, exist_ok=True)
        for n, s in shapes.items():
            s.exportBinary(str(files[n]))
        for k, f in outer_files.items():
            mods.outer[k].exportBinary(str(f))
    shapes = {n: load_binary(f) for n, f in files.items()}
    outer = {k: load_binary(f) for k, f in outer_files.items()}
    outer["base"] = outer["body"]
    return Plain(shapes, outer, seams, pieces, key)


# ---------- the cut faces ----------

@dataclass
class CutFace:
    """The flat face that a seam polygon leaves on a piece."""
    seam: str          # the name of the seam, with its side
    k: int             # the polygon of the seam
    piece: str
    face: object       # the face, moved to the plane of the polygon
    n: object          # the unit normal of the polygon
    side: int          # +1: the piece lies on the side of n
    origin: object     # a point of the polygon
    gap: float = split.KERF   # the slab that the cut took away: the face of the piece is half of it from the plane

    @property
    def into(self):
        return self.n * self.side

    @property
    def key(self) -> tuple[str, int]:
        return (self.seam, self.k)


def cut_faces(pl: Plain, names: list[str] | None = None) -> list[CutFace]:
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415

    out = []
    module = {p.full: p.module for p in pl.pieces}
    for name, shape in pl.shapes.items():
        if names is not None and name not in names:
            continue
        planes = []
        for s in pl.seams:
            if s.module != module[name]:
                continue
            for k, poly in enumerate(s.polys):
                p = [App.Vector(*q) for q in poly]
                n = (p[1] - p[0]).cross(p[2] - p[0])
                n.normalize()
                box = App.BoundBox()
                for q in p:
                    box.add(q)
                box.enlarge(1.0)
                planes.append((s.name, k, p[0], n, box))
        for f in shape.Faces:
            if not isinstance(f.Surface, Part.Plane):
                continue
            c = f.CenterOfMass
            fn = f.Surface.Axis
            for sname, k, p0, n, box in planes:
                dist = (c - p0).dot(n)
                if abs(abs(dist) - split.KERF / 2) < 1e-3 and abs(abs(fn.dot(n)) - 1.0) < 1e-6 and box.isInside(c):
                    side = 1 if dist > 0 else -1
                    out.append(CutFace(sname, k, name, f.translated(n * (-dist)), n, side, p0))
    return out


# ---------- the outer line of a cut face, made simple ----------

@dataclass
class Seg:
    """One element of the simple outer line: a straight segment from p to q, or an arc (centre c, with the turn in
    degrees about the seam normal)."""
    p: object
    q: object
    c: object = None
    turn: float = 0.0
    lean_out: bool = False   # the wall leaves the seam plane outward here: the flange starts outside the outer line
    gusset: bool = True      # False in a crease of about 45 degrees: the wall itself carries the flange

    @property
    def length(self) -> float:
        if self.c is None:
            return self.p.distanceToPoint(self.q)
        return abs(math.radians(self.turn)) * self.c.distanceToPoint(self.p)

    def tangent(self, at_end: bool, n):
        """The unit direction of travel at the start or at the end."""
        if self.c is None:
            t = self.q - self.p
        else:
            r = (self.q if at_end else self.p) - self.c
            t = n.cross(r) * (1.0 if self.turn > 0 else -1.0)
        t.normalize()
        return t

    def point(self, s: float, n):
        """The point at length s from p, and the tangent there."""
        if self.c is None:
            t = self.tangent(False, n)
            return self.p + t * s, t
        import FreeCAD as App  # noqa: PLC0415

        r = self.c.distanceToPoint(self.p)
        a = math.degrees(s / r) * (1.0 if self.turn > 0 else -1.0)
        rot = App.Rotation(n, a)
        v = rot.multVec(self.p - self.c)
        t = n.cross(v) * (1.0 if self.turn > 0 else -1.0)
        t.normalize()
        return self.c + v, t


@dataclass
class Skeleton:
    """The simple outer line of one cut face: its segments in order, the seam normal, and the sign that makes
    sign * (n x tangent) point into the form."""
    segs: list
    n: object
    sign: float
    true_wire: object      # the outer line as it is on the form
    closed: bool = False

    def inward(self, t):
        b = self.n.cross(t) * self.sign
        b.normalize()
        return b

    @property
    def length(self) -> float:
        return sum(s.length for s in self.segs)

    def samples(self, step: float = 1.0):
        """Points along the line with the tangent at each: (length from the start, point, tangent)."""
        out, base = [], 0.0
        for seg in self.segs:
            k = max(1, int(math.ceil(seg.length / step)))
            for i in range(k + 1):
                s = seg.length * i / k
                p, t = seg.point(s, self.n)
                out.append((base + s, p, t))
            base += seg.length
        return out


def polyline(wire, step: float = 1.0):
    """Points along a wire and the length to each."""
    pts = wire.discretize(Distance=step) if wire.Length > 2 * step else [v.Point for v in wire.OrderedVertexes]
    s = [0.0]
    for p, q in zip(pts, pts[1:]):
        s.append(s[-1] + p.distanceToPoint(q))
    return pts, s


def point_at(pts, s, at: float):
    """The point at length `at` along a polyline, and the unit tangent there."""
    for i in range(1, len(pts)):
        if s[i] >= at or i == len(pts) - 1:
            t = pts[i] - pts[i - 1]
            seg = s[i] - s[i - 1]
            p = pts[i - 1] + t * ((at - s[i - 1]) / seg if seg > 0 else 0.0)
            t.normalize()
            return p, t
    raise ValueError("empty polyline")


def _intersect(p, dp, q, dq, n):
    """Where the line through p along dp meets the line through q along dq, in the plane with normal n."""
    den = dp.cross(dq).dot(n)
    if abs(den) < 0.17:  # less than 10 degrees between them
        return None
    return p + dp * ((q - p).cross(dq).dot(n) / den)


def simple_line(edges: list, n, b: Build = BUILD) -> tuple[list[Seg], list[bool]]:
    """The ordered edges of an outer line as segments. Returns the segments and, for each end, whether a tail was
    left out there."""
    import Part  # noqa: PLC0415

    wire = Part.Wire(edges)
    verts = [v.Point for v in wire.OrderedVertexes]
    items = []   # (kind, edge, start, end): kind "small", "line", "arc", "curve"
    for i, e in enumerate(wire.OrderedEdges):
        p, q = verts[i], verts[(i + 1) % len(verts)] if wire.isClosed() else verts[i + 1]
        c = e.Curve
        if e.Length < b.small_edge:
            kind = "small"
        elif isinstance(c, Part.Line):
            kind = "line"
        elif isinstance(c, Part.Circle) and c.Radius >= b.arc_r:
            kind = "arc"
        else:
            kind = "curve"
        items.append((kind, e, p, q))
    dropped = [False, False]
    if not wire.isClosed():
        for end in (0, 1):
            seq = items if end == 0 else items[::-1]
            while seq and seq[0][0] == "small":
                seq.pop(0)
                dropped[end] = True
            tail = 0.0
            for i, it in enumerate(seq):
                if it[0] == "small":
                    if tail < b.end_drop:
                        k = i
                        while k < len(seq) and seq[k][0] == "small":
                            k += 1
                        del seq[:k]
                        dropped[end] = True
                    break
                tail += it[1].Length
                if tail >= b.end_drop:
                    break
            items = seq if end == 0 else seq[::-1]
    segs: list[Seg] = []
    pending = None  # the start of a group of small edges
    for kind, e, p, q in items:
        if kind == "small":
            pending = p if pending is None else pending
            continue
        new: list[Seg] = []
        if kind == "line":
            new = [Seg(p, q)]
        elif kind == "arc":
            c = e.Curve
            a = math.degrees(e.Length / c.Radius)
            turn = a if n.cross(p - c.Center).dot(q - p) > 0 else -a
            new = [Seg(p, q, c.Center, turn)]
        else:
            k = max(2, int(math.ceil(e.Length / b.chord)))
            pts = e.discretize(Number=k + 1)
            if pts[0].distanceToPoint(p) > pts[-1].distanceToPoint(p):
                pts = pts[::-1]
            pts[0], pts[-1] = p, q
            new = [Seg(a, c) for a, c in zip(pts, pts[1:])]
        if pending is not None and segs:
            # a group of small edges between two elements: a sharp corner where their lines meet near it, else a chord
            a, z = segs[-1], new[0]
            gap = pending.distanceToPoint(p)
            x = None
            if a.c is None and z.c is None:
                x = _intersect(a.q, a.tangent(True, n), z.p, z.tangent(False, n), n)
                if x is not None and (x.distanceToPoint(a.q) > 3 * gap + 1.0 or x.distanceToPoint(z.p) > 3 * gap + 1.0
                                      or (x - a.p).dot(a.q - a.p) <= 0 or (z.q - x).dot(z.q - z.p) <= 0):
                    x = None
            if x is not None:
                a.q, z.p = x, x
            elif gap > 0.05:
                segs.append(Seg(a.q, z.p))
            else:
                z.p = a.q
        pending = None
        segs += new
    return segs, dropped


def outer_lines(cf: CutFace, outer, section, b: Build = BUILD) -> list[Skeleton]:
    """The outer lines of a cut face: its edges on the section of the outer solid, each run made simple."""
    import Part  # noqa: PLC0415

    on = []
    for e in cf.face.Edges:
        if e.Length < 1e-4:
            continue
        a, z = e.FirstParameter, e.LastParameter
        if all(section.distToShape(Part.Vertex(e.valueAt(a + (z - a) * t)))[0] < 0.08 for t in (0.2, 0.5, 0.8)):
            on.append(e)
    out = []
    for group in Part.sortEdges(on):
        try:
            true_wire = Part.Wire(group)
        except Part.OCCError:
            continue
        segs, dropped = simple_line(group, cf.n, b)
        if not segs or sum(s.length for s in segs) < b.run_flange:
            continue
        if dropped[0]:
            t = segs[0].tangent(False, cf.n)
            segs.insert(0, Seg(segs[0].p - t * b.end_reach, segs[0].p))
        if dropped[1]:
            t = segs[-1].tangent(True, cf.n)
            segs.append(Seg(segs[-1].q, segs[-1].q + t * b.end_reach))
        long = max(segs, key=lambda s: s.length)
        p, t = long.point(long.length / 2, cf.n)
        sign = 1.0 if outer.isInside(p + cf.n.cross(t) * 1.0, 1e-4, False) else -1.0
        out.append(Skeleton(segs, cf.n, sign, true_wire, true_wire.isClosed()))
    return out


# ---------- a section carried along the outer line ----------

P2 = tuple[float, float]


def carry(sk: Skeleton, profile, into, z0: float, corners: bool = True):
    """The solid of a section (u inward from the outer line, z along `into` from z0 past the seam plane) carried
    along every segment of the line, with a turned solid at each corner where the segments open. One fused solid.
    profile is a list of (u, z), or a function that gives the list for a segment."""
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415

    of = profile if callable(profile) else (lambda seg: profile)

    def face_at(p, t, prof):
        bvec = sk.inward(t)
        pts = [p + bvec * u + into * (z0 + z) for u, z in prof]
        return Part.Face(Part.makePolygon(pts + [pts[0]]))

    solids = []
    for seg in sk.segs:
        if seg.length < 1e-6:
            continue
        f = face_at(seg.p, seg.tangent(False, sk.n), of(seg))
        if seg.c is None:
            solids.append(f.extrude(seg.q - seg.p))
        else:
            solids.append(f.revolve(seg.c, sk.n, seg.turn))
    if corners:
        pairs = list(zip(sk.segs, sk.segs[1:])) + ([(sk.segs[-1], sk.segs[0])] if sk.closed else [])
        for a, z in pairs:
            umax = max(u for u, _ in of(a))
            umin = min(u for u, _ in of(a))
            pos = [(0.0 if u <= umin else u, zz) for u, zz in of(a)]
            ta, tz = a.tangent(True, sk.n), z.tangent(False, sk.n)
            turn = ta.cross(tz).dot(sk.n) * sk.sign
            # the inward sides open when the line turns away from the inside
            if turn < -0.02 and umax > 0:
                bvec = sk.inward(ta)
                pts = [a.q + bvec * u + into * (z0 + zz) for u, zz in pos]
                solids.append(Part.Face(Part.makePolygon(pts + [pts[0]])).revolve(a.q, into, 360.0))
    for k, sd in enumerate(solids):
        # a prism or a turned solid whose face looked the other way comes out inside out: the fuse then loses it
        if sd.Volume < 0:
            solids[k] = sd.reversed()
    # one at a time: OpenCascade's fuse of many solids at once loses solids when a turned solid is among them
    out = solids[0]
    for sd in solids[1:]:
        out = out.fuse(sd)
    return out.removeSplitter()


def flange_section(j: Joint, lo: float, gusset: bool) -> list[P2]:
    """Flange and gusset as one outline, from u = lo: the section of joints.flange_profile, which starts in the skin."""
    w, h, t, g = j.wall_t, j.flange_h, j.flange_t, j.gusset_leg
    if gusset:
        return [(lo, 0.0), (w + h, 0.0), (w + h, t), (w, t + g), (lo, t + g)]
    return [(lo, 0.0), (w + h, 0.0), (w + h, t), (lo, t)]


# ---------- one side of a seam ----------

@dataclass
class Side:
    """What the generator knows about one piece at one seam polygon."""
    cf: CutFace
    lines: list[Skeleton]
    solid: object = None           # flange and gusset, trimmed
    mate: object = None            # the face of the flange on the seam plane (moved to the plane of the polygon)
    lean_out: bool = False         # the wall leaves the seam plane outward: the flange starts outside the outer line
    gusset: bool = True
    notes: list[str] = field(default_factory=list)


def lean(side: Side, outer, j: Joint, b: Build = BUILD) -> None:
    """Whether the wall of this side leaves the seam plane outward, for each segment of its outer lines, from points
    beside the segment at the depth of the flange: 1 mm outside the line (the wall leans out, so the flange must
    start outside the line) and 5 mm outside (a crease of about 45 degrees: the wall itself carries the flange, and
    there is no gusset)."""
    into = side.cf.into
    for sk in side.lines:
        for seg in sk.segs:
            near = far = 0
            spots = [seg.point(seg.length * f, sk.n) for f in (0.25, 0.5, 0.75)]
            for p, t in spots:
                q = p + into * j.flange_t
                out = sk.inward(t) * -1.0
                near += outer.isInside(q + out * 1.0, 1e-4, False)
                far += outer.isInside(q + out * 5.0, 1e-4, False)
            seg.lean_out = near >= 2
            seg.gusset = far < 2
    side.lean_out = any(seg.lean_out for sk in side.lines for seg in sk.segs)
    side.gusset = all(seg.gusset for sk in side.lines for seg in sk.segs)


def grown_kerf(poly, reach: float):
    """The slab of another seam, its polygon made larger by reach in its own plane."""
    face = split.poly_face(poly)
    try:
        big = face.makeOffset2D(reach, join=2)
        face = big.Faces[0] if big.Faces else face
    except Exception:  # noqa: BLE001
        pass
    return split.kerf(face)


def flange(side: Side, piece, outer, trims: list, j: Joint, b: Build = BUILD, section=None):
    """Flange and gusset of one side: the section carried along each outer line, inside the form, less the cut faces
    of the other seams and the zones that stay free. Only the solids that reach into the piece stay."""
    import Part  # noqa: PLC0415

    into, half = side.cf.into, side.cf.gap / 2
    section = section or (lambda seg: flange_section(j, -b.crease_band if seg.lean_out else b.skin_lap, seg.gusset))
    kept = []
    for sk in side.lines:
        try:
            raw = carry(sk, section, into, half)
        except Exception as e:  # noqa: BLE001
            side.notes.append(f"no flange on a line of {sk.length:.0f} mm: {e}")
            continue
        got = raw.common(outer)
        if not got.Solids:
            side.notes.append(f"no flange on a line of {sk.length:.0f} mm: it is outside the form")
            continue
        near = [t for t in trims if t.BoundBox.intersect(got.BoundBox)]
        if near:
            got = got.cut(near)
        for s in got.Solids:
            if s.Volume > b.debris_mm3 and s.common(piece).Volume > 0.5:
                kept.append(s)
    if not kept:
        side.solid = None
        return None
    side.solid = _fuse_all(kept).removeSplitter()
    set_mate(side)
    return side.solid


def set_mate(side: Side) -> None:
    """The face of the flange on the seam plane, moved to the plane of the polygon."""
    import Part  # noqa: PLC0415

    side.mate = None
    if side.solid is None:
        return
    into, half = side.cf.into, side.cf.gap / 2
    faces = [f.translated(into * -half) for f in side.solid.Faces
             if isinstance(f.Surface, Part.Plane) and abs(abs(f.Surface.Axis.dot(side.cf.n)) - 1.0) < 1e-6
             and abs((f.CenterOfMass - side.cf.origin).dot(into) - half) < 1e-3]
    side.mate = Part.makeCompound(faces) if faces else None


def cut_back(side: Side, piece, items: list, hits: list, b: Build = BUILD) -> None:
    """Cut the flange of a side back where it is in the hardware or in a keep-out zone of the fit study, with
    hardware_gap round the item."""
    cf = side.cf
    for name, role, solid in items or []:
        if side.solid is None:
            break
        if not solid.BoundBox.intersect(side.solid.BoundBox):
            continue
        v = side.solid.common(solid).Volume
        if v > b.clash_mm3:
            left = [s for s in side.solid.cut(grown(solid, b.hardware_gap)).Solids if s.Volume > b.debris_mm3 and s.common(piece).Volume > 0.5]
            hits.append({"seam": cf.seam, "k": cf.k, "piece": cf.piece, "item": name, "role": role, "mm3": round(v)})
            side.notes.append(f"cut back for {name} ({role}): {v:.0f} mm3")
            side.solid = _fuse_all(left) if left else None
    set_mate(side)


# ---------- a pair of sides: the screws, the key and the groove ----------

@dataclass
class Screw:
    at: object            # the axis on the plane of the seam polygon
    tangent: object       # along the seam
    free: float = 0.0     # the clear length for the screwdriver behind the head


@dataclass
class Pair:
    """Two pieces that meet at one seam polygon."""
    a: Side
    b: Side
    mate: object                  # where the two flange faces lie on each other
    head: Side = None             # the side with the clearance holes, the head pockets and the groove
    pilot: Side = None            # the side with the pilot holes and the key
    screws: list[Screw] = field(default_factory=list)
    runs: list[tuple] = field(default_factory=list)   # (length, first point, tangent out of the run, last point, tangent out)
    notes: list[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        return f"{self.a.cf.seam} #{self.a.cf.k}: {self.a.cf.piece} / {self.b.cf.piece}"


def mate_runs(sk: Skeleton, mate, u: float, b: Build = BUILD) -> list[list[tuple]]:
    """The stretches of the line u inward of the outer line that lie on the mating face: lists of (length, point,
    tangent). A stretch ends where the line leaves the face, and at a corner of the outer line."""
    runs, cur, last = [], [], None
    for s, p, t in sk.samples(1.0):
        q = p + sk.inward(t) * u
        ok = any(f.isInside(q, 0.01, True) for f in mate.Faces)
        jump = last is not None and (q.distanceToPoint(last) > 2.5 or q.distanceToPoint(last) < 1e-6)
        if cur and (not ok or jump):
            runs.append(cur)
            cur = []
        if ok:
            cur.append((s, q, t))
        last = q
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 2]


def stations(run: list[tuple], j: Joint, b: Build = BUILD) -> list[Screw]:
    length = sum(p[1].distanceToPoint(q[1]) for p, q in zip(run, run[1:]))
    if length < b.run_screw:
        return []
    count = max(1, round(length / j.screw_pitch))
    out, acc, k = [], 0.0, 0
    want = [length / 2 + (i - (count - 1) / 2) * j.screw_pitch for i in range(count)]
    for p, q in zip(run, run[1:]):
        step = p[1].distanceToPoint(q[1])
        while k < len(want) and acc + step >= want[k]:
            f = (want[k] - acc) / step if step > 0 else 0.0
            out.append(Screw(p[1] + (q[1] - p[1]) * f, p[2]))
            k += 1
        acc += step
    return out


def cylinder(at, axis, z0: float, z1: float, dia: float):
    import Part  # noqa: PLC0415

    return Part.makeCylinder(dia / 2, z1 - z0, at + axis * z0, axis)


def screw_tools(sc: Screw, head_into, j: Joint) -> dict:
    """The holes of one screw, with the head on the side that head_into points into."""
    h = split.KERF / 2
    down = head_into * -1.0
    return {"pilot": cylinder(sc.at, down, h - 0.01, h + j.pilot_depth, j.pilot()),
            "counterbore": cylinder(sc.at, down, h - 0.01, h + j.pilot_counterbore_depth, j.pilot_counterbore_d),
            "clearance": cylinder(sc.at, head_into, h - 0.01, h + j.flange_t + 0.01, j.clearance_d),
            "pocket": cylinder(sc.at, head_into, h + j.flange_t, h + j.flange_t + j.gusset_leg + 1.0, j.head_pocket_d)}


def free_length(sc: Screw, head_into, obstacles: list, j: Joint, b: Build = BUILD, reach: float = 200.0) -> float:
    """The clear length for the screwdriver behind the head of a screw: a shaft of driver_d along the screw axis,
    from the top of the flange, against the given solids. reach when nothing is in the way."""
    import Part  # noqa: PLC0415

    h = split.KERF / 2 + j.flange_t + 0.5
    shaft = cylinder(sc.at, head_into, h, h + reach, b.driver_d)
    best = reach
    for o in obstacles:
        if not o.BoundBox.intersect(shaft.BoundBox):
            continue
        hit = shaft.common(o)
        if hit.Volume < b.clash_mm3:
            continue
        for v in hit.Vertexes:
            best = min(best, (v.Point - sc.at).dot(head_into) - h)
    return max(best, 0.0)


def screw_fits(sc: Screw, head: Side, pilot: Side, pieces: dict, outer, j: Joint, b: Build = BUILD) -> str:
    """Why a screw does not fit with its head in `head` and its thread in `pilot`; empty when it fits."""
    tools = screw_tools(sc, head.cf.into, j)
    shell = outer.Shells[0]
    for name in ("pilot", "pocket"):
        t = tools[name]
        if t.common(outer).Volume < t.Volume - 0.01 or t.distToShape(shell)[0] < b.wall_left:
            return f"the {name} comes within {b.wall_left:g} of the outside"
    body = pilot.solid.fuse(pieces[pilot.cf.piece].common(tools["pilot"]))
    if tools["pilot"].common(body).Volume < 0.97 * tools["pilot"].Volume:
        return "the pilot hole is not in the flange"
    return ""


def pair_up(sides: list[Side], b: Build = BUILD) -> list[Pair]:
    """The pairs of sides that share a seam polygon and whose flange faces lie on each other."""
    out = []
    by = {}
    for sd in sides:
        if sd.mate is not None:
            by.setdefault(sd.cf.key, []).append(sd)
    for group in by.values():
        for i, x in enumerate(group):
            for y in group[i + 1:]:
                if x.cf.side == y.cf.side:
                    continue
                m = x.mate.common(y.mate)
                if m.Area > 20.0:
                    out.append(Pair(x, y, m))
    return out


def plan_screws(pair: Pair, pieces: dict, outer, obstacles: list, j: Joint, b: Build = BUILD, head: str = "") -> None:
    """Choose the side of the screw heads and place the screws. The head goes on the side where more screws fit
    and the screwdriver has more room; on a level seam it is the upper piece when both are equal."""
    sk = max(pair.a.lines, key=lambda s: s.length)
    runs = mate_runs(sk, pair.mate, j.screw_u, b)
    pair.runs = runs
    cand = [sc for r in runs for sc in stations(r, j, b)]
    options = []
    for h, p in ((pair.a, pair.b), (pair.b, pair.a)):
        good, why = [], []
        for sc in cand:
            fail = screw_fits(sc, h, p, pieces, outer, j, b)
            if not fail:
                free = free_length(sc, h.cf.into, obstacles, j, b)
                if free < b.driver_len:
                    fail = f"the screwdriver has {free:.0f} mm"
                else:
                    good.append(Screw(sc.at, sc.tangent, free))
            if fail:
                why.append(fail)
        upper = h.cf.into.z > 0.5
        options.append((len(good), h.cf.piece == head, upper, h, p, good, why))
    options.sort(key=lambda o: (o[1], o[0], o[2]), reverse=True)
    _, _, _, pair.head, pair.pilot, pair.screws, why = options[0]
    other = options[1]
    pair.notes.append(f"with the head in {other[3].cf.piece}: {other[0]} of {len(cand)}" + (" (" + "; ".join(sorted(set(other[6]))) + ")" if other[6] else ""))
    if len(pair.screws) < len(cand):
        pair.notes.append(f"{len(cand) - len(pair.screws)} of {len(cand)} screws left out: " + "; ".join(sorted(set(why))))
    if not cand:
        pair.notes.append("no screw: the flange faces share no run of %g mm" % b.run_screw)


def box_along(at, tangent, n, half_len: float, half_w: float, z0: float, z1: float):
    """A box centred on `at`: half_len each way along the tangent, half_w each way across it in the seam plane,
    from z0 to z1 along n."""
    import Part  # noqa: PLC0415

    across = n.cross(tangent)
    pts = [at + tangent * a * half_len + across * c * half_w + n * z0 for a, c in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(n * (z1 - z0))


def key_and_groove(pair: Pair, j: Joint, b: Build = BUILD):
    """The key on the pilot side and the groove in the head side: the sections of joints.py carried along the outer
    line. The key lies on the mating face only; it stops key_gap each side of a screw and key_end_margin from the
    ends of each run. The groove is the key with the clearance on every side."""
    from . import joints  # noqa: PLC0415

    if not pair.runs or sum(r[-1][0] - r[0][0] for r in pair.runs) < b.run_key:
        pair.notes.append("no key: the run is shorter than %g mm" % b.run_key)
        return None, None
    h = split.KERF / 2
    up = pair.head.cf.into
    sk = max(pair.pilot.lines, key=lambda s: s.length)
    c = j.groove_clearance
    key = carry(sk, joints.key_profile(j), up, -h, corners=False)
    groove = carry(sk, joints.groove_profile(j, c), up, h, corners=False)
    key = key.common([f.translated(up * -1.0).extrude(up * 4.0) for f in pair.mate.Faces][0] if len(pair.mate.Faces) == 1
                     else _fuse_all([f.translated(up * -1.0).extrude(up * 4.0) for f in pair.mate.Faces]))
    gaps_key, gaps_groove = [], []
    wide = j.key_w + 3.0
    mid = sum(j.key_u) / 2 - j.screw_u
    for sc in pair.screws:
        across = up.cross(sc.tangent)
        gaps_key.append(box_along(sc.at, sc.tangent, up, j.key_gap, j.flange_h, -2.0, 4.0))
        gaps_groove.append(box_along(sc.at, sc.tangent, up, j.key_gap - c, j.flange_h, -2.0, 4.0))
    for run in pair.runs:
        for s, q, t in (run[0], run[-1]):
            gaps_key.append(box_along(q, t, up, j.key_end_margin, j.flange_h, -2.0, 4.0))
            gaps_groove.append(box_along(q, t, up, j.key_end_margin - c, j.flange_h, -2.0, 4.0))
    key = key.cut(gaps_key)
    groove = groove.cut(gaps_groove)
    least = j.key_w * j.key_proj * 8.0
    keys = [s for s in key.Solids if s.Volume > least]
    grooves = [s for s in groove.Solids if s.Volume > least]
    if not keys:
        pair.notes.append("no key: nothing left between the screws and the ends")
        return None, None
    return _fuse_all(keys), _fuse_all(grooves)


def _fuse_all(shapes: list):
    out = shapes[0]
    for sd in shapes[1:]:
        out = out.fuse(sd)
    return out


def rebate(side: Side, j: Joint):
    """The half of the filler groove on the outer edge of one piece: vgroove_d deep from the outside, half of
    vgroove_w wide. It is a square rebate where the joint sheet has a V, so that it is an exact offset of the line."""
    h = split.KERF / 2
    section = [(-1.5, -0.01), (j.vgroove_d, -0.01), (j.vgroove_d, j.vgroove_w / 2), (-1.5, j.vgroove_w / 2)]
    out = []
    for sk in side.lines:
        try:
            out.append(carry(sk, section, side.cf.into, h, corners=False))
        except Exception as e:  # noqa: BLE001
            side.notes.append(f"no rebate: {e}")
    return _fuse_all(out) if out else None


# ---------- the seams of the layout ----------

# what the whole set is known to leave out (tests/test_pieces.py holds the generator to these lists):
# (seam, piece) with no flange, and seams with a run for screws but no screw
NO_FLANGE: tuple = ()
NO_SCREW: tuple = ()
SKIP = {"DR": "the outline of the rear door: the door and the frame of its opening are another package",
        "R4": "the centre seam of the rear door: the door is another package"}


@dataclass
class Result:
    """What the generator made: the pieces, and what it knows about each seam."""
    pieces: dict                  # name -> the finished solid
    plain: Plain
    sides: list[Side]
    pairs: list[Pair]
    feet: list[Side] = field(default_factory=list)
    ribs: list[Side] = field(default_factory=list)
    hits: list[dict] = field(default_factory=list)       # hardware that a flange was cut back for
    log: list[str] = field(default_factory=list)
    extra: dict = field(default_factory=dict)            # what the floor and the ribs report


def zones(d: Blueprint, b: Build = BUILD, floor_top: float = 10.0) -> dict[str, list]:
    """The zones that the flanges of the walls stay out of, for each module: the printed floor, and the frame of
    the rear door's opening."""
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415

    floor = Part.makeBox(700.0, 700.0, 30.0 + floor_top + b.floor_gap, App.Vector(-350.0, -50.0, -30.0))
    x = d.door_w / 2 + b.door_stop
    door = Part.makeBox(2 * x, 60.0, d.door_z1 - d.door_z0 + 2 * b.door_stop, App.Vector(-x, d.body_d - 50.0, d.door_z0 - b.door_stop))
    return {"body": [floor, door], "hood": []}


def hardware(root: Path | None = None) -> list[tuple[str, str, object]]:
    """The hardware and the keep-out zones of the fit study: (name, role, solid), placed by the anchors that the
    study wrote (fit/report.json of the default build, or of the shared build)."""
    import FreeCAD as App  # noqa: PLC0415

    from . import structure  # noqa: PLC0415

    root = root or Path(os.environ.get("CANDYBAR_SHELL", CAD / "out" / "shell-rev7"))
    if not (root / "fit" / "report.json").exists():
        root = SHARED
    doc, found = structure.fit_items(root)
    out = [(sl.name, sl.role, sl.world.copy()) for it in found for sl in it.solids if sl.role in ("hardware", "keepout")]
    App.closeDocument(doc.Name)
    return out


def grown(shape, by: float):
    """A solid made larger by `by` on every side (sharp corners); the solid itself when OpenCascade cannot."""
    try:
        big = shape.makeOffsetShape(by, 1e-3, join=2)
        if big.isValid() and big.Volume > shape.Volume:
            return big
    except Exception:  # noqa: BLE001
        pass
    return shape


def generate(d: Blueprint, pl: Plain, names: list[str] | None = None, seams: list[str] | None = None,
             items: list | None = None, log=print, j: Joint | None = None, b: Build = BUILD, heads: dict | None = None,
             with_feet: bool = True, with_ribs: bool = True, with_floor: bool = True) -> Result:
    """Make the joints of the given pieces (all when None) on the given seams (all bonded seams when None), the
    foot flanges, the ribs and the floor."""
    import Part  # noqa: PLC0415

    j = j or joint()
    heads = heads or {}
    module = {p.full: p.module for p in pl.pieces}
    seam_of = {s.name: s for s in pl.seams}
    zone = zones(d, b) if any(m == "body" for m in module.values()) else {}
    kerfs = {(s.name, k): (s.module, grown_kerf(poly, b.seam_reach)) for s in pl.seams for k, poly in enumerate(s.polys)}
    res = Result({}, pl, [], [])
    sections: dict = {}
    t0 = time.time()
    for cf in cut_faces(pl, names):
        label = seam_of[cf.seam].label
        mod = module[cf.piece]
        if label in SKIP or mod == "base" or (seams is not None and cf.seam not in seams):
            continue
        outer = pl.outer[mod]
        key = (mod,) + cf.key
        if key not in sections:
            sections[key] = Part.makeCompound(outer.slice(cf.n, cf.origin.dot(cf.n)))
        side = Side(cf, outer_lines(cf, outer, sections[key], b))
        if not side.lines:
            side.notes.append("no outer line of %g mm: no flange" % b.run_flange)
            res.sides.append(side)
            continue
        lean(side, outer, j, b)
        trims = [k for key2, (m, k) in kerfs.items() if m == mod and key2 != cf.key] + zone.get(mod, [])
        flange(side, pl.shapes[cf.piece], outer, trims, j, b)
        cut_back(side, pl.shapes[cf.piece], items, res.hits, b)
        res.sides.append(side)
        log(f"pieces: {cf.seam} #{cf.k} {cf.piece}: flange {0 if side.solid is None else side.solid.Volume / 1000:.1f} cm3, "
            f"lean out {side.lean_out}, gusset {side.gusset} {side.notes} [{time.time() - t0:.0f} s]")
    if with_feet:
        res.feet = feet(pl, names, items, res.hits, log, FLOOR, b)
    if with_ribs:
        res.ribs = rib_sides(d, pl, names, items, res.hits, {}, log, b)
    res.pairs = pair_up(res.sides, b)
    obstacles = list(pl.shapes.values())
    for pair in res.pairs:
        outer = pl.outer[module[pair.a.cf.piece]]
        plan_screws(pair, pl.shapes, outer, obstacles, j, b, heads.get(seam_of[pair.a.cf.seam].label, ""))
        log(f"pieces: {pair.name}: head in {pair.head.cf.piece}, {len(pair.screws)} screws {pair.notes} [{time.time() - t0:.0f} s]")
    add: dict[str, list] = {}
    cut: dict[str, list] = {}
    for side in res.feet + res.ribs:
        if side.solid is not None:
            add.setdefault(side.cf.piece, []).append(side.solid)
    for side in res.sides:
        if side.solid is not None:
            add.setdefault(side.cf.piece, []).append(side.solid)
            if seam_of[side.cf.seam].joint == "bond-fill":
                r = rebate(side, j)
                if r is not None:
                    cut.setdefault(side.cf.piece, []).append(r)
    for pair in res.pairs:
        key, groove = key_and_groove(pair, j, b)
        hp, pp = pair.head.cf.piece, pair.pilot.cf.piece
        if key is not None:
            add.setdefault(pp, []).append(key)
            cut.setdefault(hp, []).append(groove)
        for sc in pair.screws:
            tools = screw_tools(sc, pair.head.cf.into, j)
            cut.setdefault(pp, []).extend([tools["pilot"], tools["counterbore"]])
            cut.setdefault(hp, []).extend([tools["clearance"], tools["pocket"]])
    for name, shape in pl.shapes.items():
        if names is not None and name not in names:
            continue
        out = shape
        if add.get(name):
            out = out.fuse(_fuse_all(add[name]))
        if cut.get(name):
            out = out.cut(cut[name])
        if add.get(name) or cut.get(name):
            solids = [s for s in out.Solids if s.Volume > b.debris_mm3]
            if len(solids) == 1:
                out = solids[0]
        res.pieces[name] = out
        log(f"pieces: {name}: {len(add.get(name, []))} added, {len(cut.get(name, []))} cut, valid {out.isValid()}, "
            f"solids {len(out.Solids)}, {out.Volume / 1000:.1f} cm3 (plain {shape.Volume / 1000:.1f}) [{time.time() - t0:.0f} s]")
    if with_floor and names is None:
        walls = {n: sh for n, sh in res.pieces.items() if module[n] == "body"}
        tiles, wall_cuts, rep = floor(pl, walls, items, log, FLOOR, b)
        for n, tools in wall_cuts.items():
            res.pieces[n] = res.pieces[n].cut(tools)
        res.pieces.update(tiles)
        res.extra["floor"] = rep
        log(f"pieces: floor: {len(tiles)} tiles, {len(rep['lap_screws'])} lap screws, {len(rep['cones'])} cones, "
            f"{len(rep['foot_screws'])} foot screws, {len(rep['left_out'])} left out, hardware in the floor {rep['hardware_in_floor']} [{time.time() - t0:.0f} s]")
    return res


# ---------- the foot of the walls and the printed floor ----------

@dataclass(frozen=True)
class Floor:
    """The printed floor and the foot flange of the walls (joints 2 and 3 as built), mm.

    The skin of the walls reaches the table round the floor. Each wall piece gets a foot flange on the table, which
    is also its foot on the printer bed. The floor is nine tiles of floor_t; its edge has a rebate that lies on the
    foot flange, so that the walls carry the floor from below when the cabinet is lifted. The tiles join with
    half-laps. All floor screws are the same: thread-forming, countersunk, driven from above."""
    t: float = 10.0               # structure.FLOOR_T: the owner's floor (2026-11-11)
    inset: float = 5.0            # the edge of the floor, inward from the outline of the cabinet on the table: the wall is 4.4 there
    notch_gap: float = 0.5        # round a part of a wall that stands in the plan of the floor (the web between the deck and the body)
    foot_w: float = 16.0          # the foot flange reaches this far inward from that outline
    foot_t: float = 5.0           # and is this thick: half the floor
    rebate_gap: float = 0.3       # the rebate is this much wider than the foot flange
    rebate_lift: float = 0.2      # and this much higher: the bond line
    lap_gap: float = 0.2          # between two tiles, in plan
    lap_lift: float = 0.1         # between the two halves of a lap: the bond line
    screw_l: float = 9.5          # 3.5 x 9.5, countersunk: it does not reach the table through 10 mm
    pilot_d: float = 2.6          # ASSUMPTION: 0.75 d, the table value for PET, as joints.Joint.pilot_d_pet
    clearance_d: float = 3.9
    head_d: float = 7.0           # the countersink at the top face, 90 degrees
    foot_screw_u: float = 10.5    # the screws into the foot flange, from the outline of the cabinet
    foot_pitch: float = 80.0      # joints.OtherJoints.foot_screw_pitch
    tile_edge: float = 12.0       # a foot screw stays this far from the edge of its tile
    lap_end: float = 30.0         # a lap screw or cone stays this far from the ends of its seam


FLOOR = Floor()
TABLE = 0.002   # the outline of the cabinet on the table is the section of the form this far above it
FLOOR_SEAMS = ("BA1", "BA2", "BA3")


def bottom_face(piece):
    """The faces of a piece on the table (z = 0)."""
    import Part  # noqa: PLC0415

    faces = [f for f in piece.Faces if isinstance(f.Surface, Part.Plane) and abs(f.Surface.Axis.z) > 0.999999
             and abs(f.CenterOfMass.z) < 1e-3 and f.Area > 1.0]
    return Part.makeCompound(faces) if faces else None


def foot_side(name: str, piece, fl: Floor = FLOOR) -> CutFace | None:
    import FreeCAD as App  # noqa: PLC0415

    face = bottom_face(piece)
    if face is None:
        return None
    return CutFace("FL", 0, name, face, App.Vector(0, 0, 1), 1, App.Vector(0, 0, 0), gap=0.0)


def floor_plan(outer, fl: Floor = FLOOR):
    """The outline of the cabinet on the table, and the plan of the floor inside it."""
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415

    wires = outer.slice(App.Vector(0, 0, 1), TABLE)
    outline = Part.makeFace(wires, "Part::FaceMakerBullseye").translated(App.Vector(0, 0, -TABLE))
    plan = outline.makeOffset2D(-fl.inset, join=2)
    return outline, Part.makeFace(plan.Wires, "Part::FaceMakerBullseye")


def rect(x0: float, x1: float, y0: float, y1: float):
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415

    return Part.Face(Part.makePolygon([App.Vector(x0, y0, 0), App.Vector(x1, y0, 0), App.Vector(x1, y1, 0), App.Vector(x0, y1, 0), App.Vector(x0, y0, 0)]))


def tile_cells(pl: Plain) -> dict[str, tuple]:
    """The cell of each floor tile in plan (x0, x1, y0, y1), from the seams BA1 to BA3 of the layout."""
    xs = sorted({round(p[0], 3) for s in pl.seams if s.label == "BA1" for poly in s.polys for p in poly})
    ys = sorted({round(p[1], 3) for s in pl.seams if s.label in ("BA2", "BA3") for poly in s.polys for p in poly})
    big = 400.0
    cols = {"side L": (-big, xs[0]), "centre": (xs[0], xs[-1]), "side R": (xs[-1], big)}
    rows = {"front": (-big, ys[0]), "middle": (ys[0], ys[-1]), "rear": (ys[-1], 2 * big)}
    out = {}
    for row, (y0, y1) in rows.items():
        for col, (x0, x1) in cols.items():
            name = f"floor {row} {col.split()[0]}" + (f" {col.split()[1]}" if " " in col else "")
            out[name] = (x0, x1, y0, y1)
    return out


def lower_first(name: str) -> int:
    """The order in which the tiles take the lower half of a lap: a side tile lies under the centre tile beside it
    (the side tiles rest on the foot flange of the walls and carry the centre column), and a middle tile lies under
    the front and the rear tile (so that no tile is longer than the bed). Lower number: lower in the lap."""
    row, col = name.split()[1], name.split()[2]
    return (0 if col == "side" else 2) + (0 if row == "middle" else 1)


def floor(pl: Plain, walls: dict, items: list, log=print, fl: Floor = FLOOR, b: Build = BUILD) -> tuple[dict, dict, dict]:
    """The nine floor tiles, and the holes that they give the wall pieces. Returns (tiles, cuts for the wall pieces,
    report). walls are the finished wall pieces with their foot flanges."""
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415

    up = App.Vector(0, 0, 1)
    outline, plan = floor_plan(pl.outer["body"], fl)
    cells = tile_cells(pl)
    lap = OTHER_JOINTS.lap_w
    g = fl.lap_gap / 2
    upper = {n: plan.common(rect(x0 + g, x1 - g, y0 + g, y1 - g)) for n, (x0, x1, y0, y1) in cells.items()}
    order = sorted(cells, key=lambda n: (lower_first(n), n))
    lower: dict = {}
    for n in order:
        x0, x1, y0, y1 = cells[n]
        rank = lower_first(n)
        grow = [0.0, 0.0, 0.0, 0.0]
        for m, (a0, a1, c0, c1) in cells.items():
            if m == n or lower_first(m) <= rank:
                continue
            if abs(a1 - x0) < 1e-6 and c0 == y0:
                grow[0] = lap
            if abs(a0 - x1) < 1e-6 and c0 == y0:
                grow[1] = lap
            if abs(c1 - y0) < 1e-6 and a0 == x0:
                grow[2] = lap
            if abs(c0 - y1) < 1e-6 and a0 == x0:
                grow[3] = lap
        face = plan.common(rect(x0 - grow[0] + g, x1 + grow[1] - g, y0 - grow[2] + g, y1 + grow[3] - g))
        taken = [lower[m].makeOffset2D(fl.lap_gap, join=2) for m in lower if lower[m].BoundBox.intersect(face.BoundBox)]
        if taken:
            face = face.cut(taken)
        lower[n] = max(face.Faces, key=lambda f: f.Area)
    # the rebate over the foot flange: everything within foot_w + rebate_gap of the outline of the cabinet
    inner = outline.makeOffset2D(-(fl.foot_w + fl.rebate_gap), join=2)
    rebate = outline.cut(Part.makeFace(inner.Wires, "Part::FaceMakerBullseye")).translated(up * -1.0).extrude(up * (1.0 + fl.foot_t + fl.rebate_lift))
    tiles = {}
    report_notches: list[dict] = []
    half = fl.t / 2
    for n in order:
        body = upper[n].extrude(up * fl.t)
        others = [lower[m].makeOffset2D(fl.lap_gap, join=2).translated(up * -1.0).extrude(up * (1.0 + half + fl.lap_lift / 2))
                  for m in order if m != n and lower[m].BoundBox.intersect(upper[n].BoundBox)]
        body = body.cut(others)
        low = lower[n].extrude(up * (half - fl.lap_lift / 2))
        solid = body.fuse(low).cut(rebate)
        # a part of a wall that stands in the plan of the floor: a notch round its box
        notches = []
        for w, sh in pl.shapes.items():
            if w.startswith("floor") or not sh.BoundBox.intersect(solid.BoundBox):
                continue
            for part in sh.common(solid).Solids:
                if part.Volume > b.clash_mm3:
                    bb = part.BoundBox
                    k = fl.notch_gap
                    notches.append(Part.makeBox(bb.XLength + 2 * k, bb.YLength + 2 * k, bb.ZLength + 2 * k, App.Vector(bb.XMin - k, bb.YMin - k, bb.ZMin - k)))
                    report_notches.append({"tile": n, "wall": w, "box": [round(v, 1) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)]})
        if notches:
            solid = solid.cut(notches)
        solid = solid.removeSplitter()
        big = [sd for sd in solid.Solids if sd.Volume > 100.0]
        tiles[n] = big[0] if len(big) == 1 else solid
    # screws and cones
    wall_cuts: dict[str, list] = {}
    tile_cuts: dict[str, list] = {n: [] for n in tiles}
    tile_adds: dict[str, list] = {n: [] for n in tiles}
    report = {"lap_screws": [], "foot_screws": [], "cones": [], "left_out": [], "notches": report_notches}
    oj = OTHER_JOINTS

    def screw_at(p, top: float):
        """The holes of one floor screw at p, its head at the height top: (through the upper part, into the lower)."""
        hole = Part.makeCylinder(fl.clearance_d / 2, half + 1.0, App.Vector(p.x, p.y, top - half - 0.5), up)
        sink = Part.makeCone(fl.clearance_d / 2, fl.head_d / 2 + 0.01, (fl.head_d - fl.clearance_d) / 2, App.Vector(p.x, p.y, top - (fl.head_d - fl.clearance_d) / 2 + 0.01), up)
        pilot = Part.makeCylinder(fl.pilot_d / 2, fl.screw_l - half + 1.5, App.Vector(p.x, p.y, top - fl.screw_l - 1.0), up)
        return hole.fuse(sink), pilot

    inside = lambda face, p: any(f.isInside(p, 0.01, True) for f in face.Faces)
    rim = Part.makeCompound(outline.Wires)
    names = list(tiles)
    for i, n in enumerate(names):
        for m in names[i + 1:]:
            lo, hi = (n, m) if lower_first(n) < lower_first(m) else (m, n)
            if lower_first(n) == lower_first(m):
                continue
            zone = lower[lo].common(upper[hi])
            if zone.Area < 100.0:
                continue
            bb = zone.BoundBox
            along_x = bb.XLength > bb.YLength
            length = bb.XLength if along_x else bb.YLength
            count = int((length - 2 * fl.lap_end) // (oj.lap_screw_pitch / 2)) + 1
            for k in range(max(count, 0)):
                s = fl.lap_end + k * oj.lap_screw_pitch / 2
                p = App.Vector(bb.XMin + s, bb.Center.y, 0) if along_x else App.Vector(bb.Center.x, bb.YMin + s, 0)
                if not inside(zone, p) or Part.Vertex(p).distToShape(Part.makeCompound(zone.Wires))[0] < oj.cone_d / 2 + 2.0:
                    continue
                if Part.Vertex(p).distToShape(rim)[0] < fl.foot_w + fl.rebate_gap + oj.cone_d / 2 + 2.0:
                    continue
                if k % 2 == 0:
                    hole, pilot = screw_at(p, fl.t)
                    tile_cuts[hi].append(hole)
                    tile_cuts[lo].append(pilot)
                    report["lap_screws"].append({"at": [round(p.x, 1), round(p.y, 1)], "upper": hi, "lower": lo})
                else:
                    z = half - fl.lap_lift / 2
                    c = oj.cone_clearance
                    tile_adds[lo].append(Part.makeCone(oj.cone_d / 2, 1.0, oj.cone_h, App.Vector(p.x, p.y, z - 0.01), up))
                    tile_cuts[hi].append(Part.makeCone(oj.cone_d / 2 + c, 1.0 + c, oj.cone_h + c, App.Vector(p.x, p.y, z - 0.01), up))
                    report["cones"].append({"at": [round(p.x, 1), round(p.y, 1)], "upper": hi, "lower": lo})
    line = outline.makeOffset2D(-fl.foot_screw_u, join=2).Wires[0]
    pts, acc = polyline(line, 1.0)
    count = max(1, round(acc[-1] / fl.foot_pitch))
    for k in range(count):
        p, _ = point_at(pts, acc, (k + 0.5) * acc[-1] / count)
        p = App.Vector(p.x, p.y, 0.0)
        tile = next((n for n in names if inside(upper[n], p)), None)
        why = ""
        if tile is None:
            why = "on a tile seam"
        else:
            x0, x1, y0, y1 = cells[tile]
            if min(abs(p.x - x0), abs(p.x - x1), abs(p.y - y0), abs(p.y - y1)) < fl.tile_edge:
                why = "nearer than %g to the edge of its tile" % fl.tile_edge
            elif any(inside(lower[m], p) for m in names if m != tile):
                why = "in a lap"
        wall = None
        if not why:
            q = App.Vector(p.x, p.y, fl.foot_t / 2)
            wall = next((w for w, sh in walls.items() if sh.isInside(q, 0.01, True)), None)
            if wall is None:
                why = "no foot flange under it"
        if why:
            report["left_out"].append({"at": [round(p.x, 1), round(p.y, 1)], "why": why})
            continue
        hole, pilot = screw_at(p, fl.t)
        tile_cuts[tile].append(hole)
        wall_cuts.setdefault(wall, []).append(pilot)
        report["foot_screws"].append({"at": [round(p.x, 1), round(p.y, 1)], "tile": tile, "wall": wall})
    for n in names:
        out = tiles[n]
        if tile_adds[n]:
            out = out.fuse(_fuse_all(tile_adds[n]))
        if tile_cuts[n]:
            out = out.cut(tile_cuts[n])
        tiles[n] = out.removeSplitter()
    hits = []
    for name, role, solid in items or []:
        for n, t in tiles.items():
            if solid.BoundBox.intersect(t.BoundBox):
                v = t.common(solid).Volume
                if v > b.clash_mm3:
                    hits.append({"tile": n, "item": name, "role": role, "mm3": round(v)})
    report["hardware_in_floor"] = hits
    return tiles, wall_cuts, report


def feet(pl: Plain, names: list[str] | None, items: list, hits: list, log=print, fl: Floor = FLOOR, b: Build = BUILD) -> list[Side]:
    """The foot flange of each wall piece that stands on the table: the band of foot_w along the outline of the
    cabinet, foot_t thick, between the cut faces of the upright seams."""
    import Part  # noqa: PLC0415

    import FreeCAD as App  # noqa: PLC0415

    module = {p.full: p.module for p in pl.pieces}
    outer = pl.outer["body"]
    section = Part.makeCompound(outer.slice(App.Vector(0, 0, 1), TABLE)).translated(App.Vector(0, 0, -TABLE))
    kerfs = [grown_kerf(poly, b.seam_reach) for s in pl.seams if s.module == "body" for poly in s.polys]
    profile = [(b.skin_lap, 0.0), (fl.foot_w, 0.0), (fl.foot_w, fl.foot_t), (b.skin_lap, fl.foot_t)]
    out = []
    for name, shape in pl.shapes.items():
        if module[name] != "body" or (names is not None and name not in names):
            continue
        cf = foot_side(name, shape, fl)
        if cf is None:
            continue
        side = Side(cf, outer_lines(cf, outer, section, b))
        if not side.lines:
            continue
        flange(side, shape, outer, kerfs, JOINT, b, section=lambda seg: profile)
        cut_back(side, shape, items, hits, b)
        out.append(side)
        log(f"pieces: foot of {name}: {0 if side.solid is None else side.solid.Volume / 1000:.1f} cm3, lines {[round(sk.length) for sk in side.lines]} {side.notes}")
    return out


# ---------- ribs ----------

@dataclass(frozen=True)
class Rib:
    """A rib on the inside of a wall: in the plane axis = at, on the named piece."""
    piece: str
    axis: str      # "x" or "y": the normal of the plane of the rib
    at: float
    panel: str
    span: tuple[float, float]   # the panel that it divides, short side and long side, mm


RIB_T = 3.0     # structure.members: "ribs 8 high, 3 thick, at most 110 apart"
RIB_H = 8.0
RIB_LIMIT = 0.3  # mm under a finger push of 20 N (structure.estimates: rib_spacing)


def ribs(d: Blueprint) -> list[Rib]:
    """The ribs of the right side; the left side mirrors them. A rib stands upright in the print orientation of its
    piece, so it needs no support. Where: the three panels whose hand estimate (structure.plate_deflection, 20 N)
    is more than RIB_LIMIT."""
    third = d.rear_w / 6
    return [Rib("middle", "y", 330.0, "side band between L1 and B1", (127.0, 159.0)),
            Rib("middle", "y", 460.0, "side of the lower body between L1 and B1", (136.0, 177.0)),
            Rib("rear lower", "x", third, "lower rear wall below the door, one half", (116.0, 211.0)),
            Rib("rear lower", "x", 2 * third, "lower rear wall below the door, one half", (116.0, 211.0))]


def rib_sides(d: Blueprint, pl: Plain, names: list[str] | None, items: list, hits: list, extra_trims: dict, log=print, b: Build = BUILD) -> list[Side]:
    """Each rib as a side: the section of the piece in the plane of the rib is its cut face, and a rectangle of
    RIB_T by wall_t + RIB_H is carried along the outer line of that section."""
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415

    outer = pl.outer["body"]
    kerfs = [grown_kerf(poly, b.seam_reach) for s in pl.seams if s.module == "body" for poly in s.polys] + zones(d, b)["body"]
    w = d.wall_t
    profile = [(b.skin_lap, 0.0), (w + RIB_H, 0.0), (w + RIB_H, RIB_T), (b.skin_lap, RIB_T)]
    out = []
    for rib in ribs(d):
        for sx, tag in ((1.0, "R"), (-1.0, "L")):
            name = f"{rib.piece} {tag}"
            if name not in pl.shapes or (names is not None and name not in names):
                continue
            n = App.Vector(1, 0, 0) if rib.axis == "x" else App.Vector(0, 1, 0)
            at = rib.at * sx if rib.axis == "x" else rib.at
            origin = n * (at - RIB_T / 2)
            wires = pl.shapes[name].slice(n, at - RIB_T / 2)
            if not wires:
                log(f"pieces: rib {rib.axis} {at:g} of {name}: the plane does not cut the piece")
                continue
            faces = []
            for wv in wires:
                try:
                    faces.append(Part.Face(wv))
                except Part.OCCError:
                    pass
            cf = CutFace(f"rib {rib.axis} {at:g}", 0, name, Part.makeCompound(faces), n, 1, origin, gap=0.0)
            section = Part.makeCompound(outer.slice(n, at - RIB_T / 2))
            side = Side(cf, outer_lines(cf, outer, section, b))
            if not side.lines:
                log(f"pieces: rib {rib.axis} {at:g} of {name}: no outer line")
                continue
            trims = kerfs + extra_trims.get(name, [])
            flange(side, pl.shapes[name], outer, trims, JOINT, b, section=lambda seg: profile)
            cut_back(side, pl.shapes[name], items, hits, b)
            out.append(side)
            log(f"pieces: rib {rib.axis} {at:g} of {name}: {0 if side.solid is None else side.solid.Volume / 1000:.1f} cm3 {side.notes}")
    return out


# ---------- files ----------

EDGE_STEP = 2.0


def edge_polylines(shape, step: float = EDGE_STEP) -> list:
    out = []
    for e in shape.Edges:
        if e.Degenerated or e.Length < 1e-6:
            continue
        n = max(2, math.ceil(e.Length / step) + 1)
        out.append([[round(p.x, 3), round(p.y, 3), round(p.z, 3)] for p in e.discretize(Number=n)])
    return out


def write_parts(folder: Path, shapes: dict, tint: dict | None = None, moved: dict | None = None) -> None:
    """One BREP and one STL for each piece, manifest.json and edges.json (every BREP edge, for the renders). moved
    gives a shift for each piece in the meshes and the edges only (an exploded view); the BREP stays in place."""
    import FreeCAD as App  # noqa: PLC0415
    import MeshPart  # noqa: PLC0415

    folder.mkdir(parents=True, exist_ok=True)
    tint = tint or split.tints(shapes)
    manifest, edges = {}, {}
    for name, shape in shapes.items():
        stem = name.replace(" ", "_")
        shape.exportBrep(str(folder / f"{stem}.brep"))
        shown = shape.translated(App.Vector(*moved[name])) if moved and name in moved else shape
        MeshPart.meshFromShape(Shape=shown, LinearDeflection=0.2, AngularDeflection=0.15).write(str(folder / f"{stem}.stl"))
        manifest[stem] = {"file": f"{stem}.stl", "brep": f"{stem}.brep", "finish": tint[name]}
        edges[stem] = edge_polylines(shown)
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    (folder / "edges.json").write_text(json.dumps(edges), encoding="utf-8")


def pilot(out: Path, log=print) -> int:
    d = Blueprint()
    pl = plain(d, out, log)
    items = hardware()
    code = 0
    for seam, names in PILOT:
        res = generate(d, pl, list(names), [seam], items, log)
        folder = out / "pilot" / seam.replace(" ", "_")
        write_parts(folder, res.pieces)
        n = res.pairs[0].head.cf.n if res.pairs else None
        if n is not None:
            # the pair open: the head side lifted 40 mm off the seam
            up = res.pairs[0].head.cf.into * 40.0
            write_parts(folder / "open", res.pieces, moved={res.pairs[0].head.cf.piece: (up.x, up.y, up.z)})
        for name, s in res.pieces.items():
            if not s.isValid() or len(s.Solids) != 1:
                code = 1
    return code


def vec(v) -> list[float]:
    return [round(v.x, 2), round(v.y, 2), round(v.z, 2)]


def seam_report(res: Result) -> dict:
    """What was made on each seam, as plain data."""
    side_row = lambda sd: {"seam": sd.cf.seam, "k": sd.cf.k, "piece": sd.cf.piece,
                           "flange_cm3": round(sd.solid.Volume / 1000, 1) if sd.solid is not None else 0.0,
                           "line_mm": round(sum(sk.length for sk in sd.lines), 1), "lean_out": sd.lean_out, "gusset": sd.gusset, "notes": sd.notes}
    pairs = [{"seam": p.a.cf.seam, "k": p.a.cf.k, "head": p.head.cf.piece, "pilot": p.pilot.cf.piece, "mate_cm2": round(p.mate.Area / 100, 1),
              "run_mm": round(sum(r[-1][0] - r[0][0] for r in p.runs), 1), "normal": vec(p.head.cf.into),
              "screws": [{"at": vec(sc.at), "free": round(sc.free)} for sc in p.screws], "notes": p.notes} for p in res.pairs]
    return {"sides": [side_row(sd) for sd in res.sides], "feet": [side_row(sd) for sd in res.feet], "ribs": [side_row(sd) for sd in res.ribs],
            "pairs": pairs, "hits": res.hits, "floor": res.extra.get("floor", {})}


# ---------- the checks of the whole set ----------

def tight_box(shape):
    """The box of a shape from its mesh: the BoundBox of a shape read from a file is not tight."""
    import numpy as np  # noqa: PLC0415

    pts, _ = shape.tessellate(0.5)
    p = np.array([(v.x, v.y, v.z) for v in pts])
    return p, p.min(axis=0), p.max(axis=0)


def check_set(d: Blueprint, res: Result, items: list, log=print, b: Build = BUILD, detail: bool = True) -> dict:
    """The checks of the whole set: every piece is one valid solid inside the printer's limit; no two pieces share
    volume; no piece is in the hardware; the mass; the screws; what each print orientation overhangs."""
    import numpy as np  # noqa: PLC0415

    lim = split.printer()
    pl = res.plain
    up = {p.full: p.up for p in pl.pieces}
    bed = {p.full: p.bed for p in pl.pieces}
    module = {p.full: p.module for p in pl.pieces}
    covers = split.cover_shapes(d) if detail else []
    rows, boxes = {}, {}
    t0 = time.time()
    for name, shape in res.pieces.items():
        pts, lo, hi = tight_box(shape)
        boxes[name] = (lo, hi)
        row = {"valid": bool(shape.isValid()), "solids": len(shape.Solids), "faces": len(shape.Faces),
               "volume_cm3": round(shape.Volume / 1000, 1), "plain_cm3": round(pl.shapes[name].Volume / 1000, 1) if name in pl.shapes else None,
               "mass_g": round(shape.Volume / 1000 * split.PETG_G_PER_CM3), "bed": bed[name], **split.print_box(pts, up[name], lim)}
        if detail and module[name] in ("body", "hood", "base"):
            m = split.measure(shape, up[name], lim, pl.outer[module[name]], covers, d, True, split.seam_planes(pl.seams, module[name]))
            row.update({k: m[k] for k in ("seen", "overhang_seen", "limit_seen", "overhang_inside", "bed")} | {"bed_cm2": m["bed"]})
            row["bed"] = bed[name]
        rows[name] = row
        log(f"pieces: check {name}: valid {row['valid']}, solids {row['solids']}, box {row['x']} x {row['y']} x {row['z']}, fits {row['fits']} [{time.time() - t0:.0f} s]")
    names = list(res.pieces)
    clashes = []
    for i, a in enumerate(names):
        for c in names[i + 1:]:
            (alo, ahi), (clo, chi) = boxes[a], boxes[c]
            if np.any(alo > chi + 0.1) or np.any(clo > ahi + 0.1):
                continue
            v = res.pieces[a].common(res.pieces[c]).Volume
            if v > b.clash_mm3:
                clashes.append({"a": a, "b": c, "mm3": round(v, 1)})
    log(f"pieces: clashes between pieces: {clashes} [{time.time() - t0:.0f} s]")
    hard = []
    for iname, role, solid in items or []:
        sb = solid.BoundBox
        for name, shape in res.pieces.items():
            lo, hi = boxes[name]
            if sb.XMin > hi[0] or sb.XMax < lo[0] or sb.YMin > hi[1] or sb.YMax < lo[1] or sb.ZMin > hi[2] or sb.ZMax < lo[2]:
                continue
            v = shape.common(solid).Volume
            plain_v = pl.shapes[name].common(solid).Volume if name in pl.shapes and not name.startswith("floor") else 0.0
            if v > b.clash_mm3:
                hard.append({"piece": name, "item": iname, "role": role, "mm3": round(v, 1), "of_the_plain_piece_mm3": round(plain_v, 1)})
    log(f"pieces: clashes with hardware: {hard} [{time.time() - t0:.0f} s]")
    # the screwdriver again, against the finished pieces
    j = joint()
    reach = []
    solids = list(res.pieces.values())
    for p in res.pairs:
        for sc in p.screws:
            free = free_length(sc, p.head.cf.into, solids, j, b)
            reach.append({"seam": p.a.cf.seam, "head": p.head.cf.piece, "at": vec(sc.at), "free": round(free)})
    short = [r for r in reach if r["free"] < b.driver_len]
    fl = res.extra.get("floor", {})
    wall_g = sum(r["mass_g"] for n, r in rows.items() if not n.startswith("floor"))
    plain_g = sum(pl.shapes[n].Volume / 1000 * split.PETG_G_PER_CM3 for n in rows if not n.startswith("floor"))
    twins = [{"piece": n[:-2], "right_cm3": r["volume_cm3"], "left_cm3": rows[n[:-1] + "L"]["volume_cm3"]} for n, r in rows.items()
             if n.endswith(" R") and n[:-1] + "L" in rows and abs(r["volume_cm3"] - rows[n[:-1] + "L"]["volume_cm3"]) > 0.05]
    out = {"pieces": rows, "twins_that_differ": twins, "clashes": clashes, "hardware": hard, "reach": reach, "reach_short": short,
           "screws": {"joint 1, 3.0 x 16": sum(len(p.screws) for p in res.pairs),
                      "floor, 3.5 x 9.5 countersunk": len(fl.get("lap_screws", [])) + len(fl.get("foot_screws", []))},
           "cones": len(fl.get("cones", [])),
           "mass": {"pieces_without_floor_g": wall_g, "plain_skin_without_floor_g": round(plain_g),
                    "joints_ribs_feet_g": round(wall_g - plain_g), "floor_solid_g": sum(r["mass_g"] for n, r in rows.items() if n.startswith("floor"))},
           "printer": vars(lim),
           "ok": all(r["valid"] and r["solids"] == 1 and r["fits"] for r in rows.values()) and not clashes}
    return out


def build_all(out: Path, log=print) -> int:
    d = Blueprint()
    pl = plain(d, out, log)
    items = hardware()
    res = generate(d, pl, None, None, items, log)
    write_parts(out, res.pieces)
    (out / "seams.json").write_text(json.dumps(seam_report(res), indent=1), encoding="utf-8")
    chk = check_set(d, res, items, log)
    (out / "check.json").write_text(json.dumps(chk, indent=1), encoding="utf-8")
    bad = [n for n, r in chk["pieces"].items() if not r["valid"] or r["solids"] != 1 or not r["fits"]]
    log(f"pieces: {len(res.pieces)} pieces, screws {chk['screws']}, not one valid solid in the limit: {bad}, clashes {len(chk['clashes'])}, "
        f"in hardware {len(chk['hardware'])}, mass {chk['mass']}")
    return 0 if chk["ok"] else 1


def main() -> int:
    out = Path(os.environ.get("CANDYBAR_OUT", "cad/out/pieces"))
    what = os.environ.get("CANDYBAR_PIECES", "all")
    if what == "pilot":
        return pilot(out)
    return build_all(out)
