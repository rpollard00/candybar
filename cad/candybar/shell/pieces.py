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
    V         on the outer line, for the seams that are filled

The same code makes a straight seam, a seam in a crease (the wall of one piece leaves the seam plane at 45 degrees:
that side gets a band outside the outer line too, and the form trims it) and the place where three pieces meet (the
flange of each piece ends at the cut face of the next seam, and the flanges of two seams on one piece fuse into a
corner).

    CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh candybar.shell.pieces

The front socket plate is in the default build (the owner's plate b-knob, 2026-11-16): deck side R has its seat and
frame (plain, with_socket_plate), the floor tile under the frame its notch, and the foot flange stops along the plate
(the items of hardware(), socket_plate_items).
CANDYBAR_PIECES names what to do: "all" (default: every piece, the files and the checks), "pilot" (the two pilot
pairs only), "check" (the checks again, on the files of a build), "rules" (the rules of the set again, on the
files of a build: seconds) or "views" (the folders that tools/draw_pieces.py
renders). No FreeCAD at import.
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
    driver_len: float = 40.0       # the clear length that it needs behind the screw head: a 25 mm bit in a flat ratchet
    hardware_gap: float = 2.0      # a flange stays this far from the hardware and the keep-out zones of fit.Layout
    door_stop: float = 10.0        # the flanges stop this far from the opening of the rear door (another package)
    floor_gap: float = 0.3         # the wall flanges stop this far above the printed floor
    clash_mm3: float = 1.0         # a common volume larger than this is a clash
    debris_mm3: float = 2.0        # a solid smaller than this, left by a cut, is debris
    cut_in_clear: float = 10.0     # seam L1 has no screw this near the span of the cut-ins (the round end of a slot
                                   # and the head pocket): the skin steps in behind the lowest cut-in, and a head
                                   # pocket of 9 would cut 1.0 into that step of 1.5 (the rear door's study, 2026-11-14)


BUILD = Build()
PILOT = (("D2 R", ("deck side R", "lower R")), ("B1 R", ("middle R", "upper R")))


def joint() -> Joint:
    """The joint of the cabinet. The pilot hole is open until the coupon decides; the pieces are modelled with the
    table value for ABS, the first candidate for the shell in ABS (decision record 0008)."""
    return replace(JOINT, pilot_d=JOINT.pilot_d_abs)


# ---------- the plain pieces, from the cache ----------

def cache_dir(out: Path) -> Path:
    return out / "cache"


def load_binary(path: Path):
    import Part  # noqa: PLC0415

    s = Part.Shape()
    s.importBinary(str(path))
    return s


def outer_parts() -> dict:
    """The outer solids of the default build, read from its BREP files (CANDYBAR_SHELL, default cad/out/shell-rev7);
    made here when the folder does not hold them."""
    import Part  # noqa: PLC0415

    from . import solids as so  # noqa: PLC0415

    names = ("deck", "body", "hood", "bezel")
    here = Path(os.environ.get("CANDYBAR_SHELL", CAD / "out" / "shell-rev7"))
    folder = here if all((here / f"{k}.brep").exists() for k in names) else None
    if folder is None:
        return so.build(Blueprint()), so
    parts = {}
    for k in names:
        parts[k] = Part.Shape()
        parts[k].read(str(folder / f"{k}.brep"))
    return parts, so


def modules(d: Blueprint, log=print) -> split.Modules:
    """As split.build_modules, from the outer solids on disk and the skin in the cache."""
    import Part  # noqa: PLC0415

    parts, so = outer_parts()
    skin = {}
    for k, f in split.skin_files(d).items():
        if not f.exists():
            raise FileNotFoundError(f"pieces: the skin {f} is not in the cache; run candybar.shell.split first")
        skin[k] = Part.Shape()
        skin[k].importBinary(str(f))
        if not skin[k].isValid():
            raise RuntimeError(f"pieces: the skin {f} is not a valid shape as read")
    # as split.build_modules: the form of the skin (solids.skin_parts)
    form = so.skin_parts(d, parts)
    body = so.unsplit(form["deck"].fuse(form["body"]))
    hood = so.unsplit(form["hood"].fuse(form["marquee_lip"]))
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

    from . import rear  # noqa: PLC0415

    seams, pieces = split.expanded(split.layout(d))
    # the rear finishes the pieces of the door and of its opening (rear.finish_pieces): its source is in the key
    rear_src = hashlib.sha256(Path(rear.__file__).read_bytes()).hexdigest()
    key = hashlib.sha256((split.fingerprint(d) + repr(seams) + repr(pieces) + str(split.KERF) + rear_src).encode()).hexdigest()[:16]
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
        # as split.run does it: the door halves are the designed halves, and the pieces round the opening have the
        # lip, the tongues, the posts and the openings of the lower wall
        shapes = rear.finish_pieces(shapes, d, log=log)
        here.mkdir(parents=True, exist_ok=True)
        for n, s in shapes.items():
            s.exportBinary(str(files[n]))
        for k, f in outer_files.items():
            mods.outer[k].exportBinary(str(f))
    shapes = {n: load_binary(f) for n, f in files.items()}
    outer = {k: load_binary(f) for k, f in outer_files.items()}
    outer["base"] = outer["body"]
    # the seat of the front socket plate in deck side R (it is cut on the piece, not in the skin of the cache)
    return with_socket_plate(Plain(shapes, outer, seams, pieces, key), d)


# ---------- the front socket plate (in the default build since 2026-11-16) ----------

SOCKET_PLATE = "socket plate"   # the role of its parts among the items; the stop of the foot flange is a "zone"


def with_socket_plate(pl: Plain, d: Blueprint) -> Plain:
    """The plain cut with the seat of the front socket plate in "deck side R": the opening, the frame behind the skin
    and the edge break of the rim (socket_plate.seat). The floor then gets its notch round the frame, as round any
    part of a wall that stands in its plan."""
    from . import socket_plate as spm  # noqa: PLC0415

    shapes = dict(pl.shapes)
    shapes["deck side R"] = spm.seat(shapes["deck side R"], spm.SocketPlate(), d, hollow=True)
    return replace(pl, shapes=shapes)


def socket_plate_items(d: Blueprint, fl: "Floor" = None) -> list[tuple[str, str, object]]:
    """The plate and the bought parts of every variant of the front socket plate (with the room of their leads), and
    the stretch of the foot flange along the plate: the floor tile has its notch round the frame there, so a foot
    flange under it holds no tile and has no screw."""
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415

    from . import socket_plate as spm  # noqa: PLC0415

    fl = fl or FLOOR
    sp = spm.SocketPlate()
    out = []
    for v in spm.VARIANTS:
        out.append((f"socket plate {v.key}", SOCKET_PLATE, spm.plate(sp, d, v)))
        out += [(f"{k} ({v.key})", SOCKET_PLATE, shape) for k, shape in spm.hardware(sp, d, v).items()]
    x, y, z = sp.centre(d)
    a, _ = sp.half(sp.reveal + sp.frame_grow)
    stop = Part.makeBox(fl.foot_w + 10.0, 2 * a, fl.foot_thick + 1.0, App.Vector(x - fl.foot_w - 5.0, y - a, -0.5))
    out.append(("the foot flange along the socket plate", "zone", stop))
    return out


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


JOIN = 0.05   # two edges of an outer line join when their ends are this near


def chains(edges: list, tol: float = JOIN) -> list[tuple[list, bool]]:
    """Edges put end to end: a list of (chain, closed), a chain being (edge, start, end) in order. An edge shorter
    than the tolerance is left out. Part.Wire does this too, but it fails on some of the outer lines (an edge of no
    length at a corner of the form), and then a seam had a flange on one side of the cabinet only."""
    items = [(e, e.valueAt(e.FirstParameter), e.valueAt(e.LastParameter)) for e in edges if e.Length > tol / 2]
    out = []
    while items:
        chain = [items.pop(0)]
        grown = True
        while grown:
            grown = False
            start, end = chain[0][1], chain[-1][2]
            for k, (e, p, q) in enumerate(items):
                if p.distanceToPoint(end) < tol:
                    chain.append((e, p, q))
                elif q.distanceToPoint(end) < tol:
                    chain.append((e, q, p))
                elif q.distanceToPoint(start) < tol:
                    chain.insert(0, (e, p, q))
                elif p.distanceToPoint(start) < tol:
                    chain.insert(0, (e, q, p))
                else:
                    continue
                items.pop(k)
                grown = True
                break
        out.append((chain, len(chain) > 1 and chain[0][1].distanceToPoint(chain[-1][2]) < tol))
    return out


def simple_line(edges: list, n, b: Build = BUILD, chain: list | None = None, closed: bool = False) -> tuple[list[Seg], list[bool]]:
    """The edges of one outer line as segments (or a chain of chains()). Returns the segments and, for each end,
    whether a tail was left out there."""
    import Part  # noqa: PLC0415

    if chain is None:
        chain, closed = chains(edges)[0]
    items = []   # (kind, edge, start, end): kind "small", "line", "arc", "curve"
    for e, p, q in chain:
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
    if not closed:
        for end in (0, 1):
            seq = items if end == 0 else items[::-1]
            while seq and seq[0][0] == "small":
                seq.pop(0)
                dropped[end] = True
            tail = 0.0
            for i, it in enumerate(seq):
                if it[0] == "small":
                    rest = sum(x[1].Length for x in seq[i:] if x[0] != "small")
                    if tail < b.end_drop and tail < rest:
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
    for chain, closed in chains(on):
        segs, dropped = simple_line([], cf.n, b, chain, closed)
        if not segs or sum(s.length for s in segs) < b.run_flange:
            continue
        if dropped[0]:
            t = segs[0].tangent(False, cf.n)
            segs.insert(0, Seg(segs[0].p - t * b.end_reach, segs[0].p))
        if dropped[1]:
            t = segs[-1].tangent(True, cf.n)
            segs.append(Seg(segs[-1].q, segs[-1].q + t * b.end_reach))
        # which side of the line is inside the form: points 1 mm beside it, 1 mm into the piece (a point in the seam
        # plane itself can lie on a face of the form, as on the table)
        votes = 0
        for seg in segs:
            for f in (0.25, 0.5, 0.75):
                p, t = seg.point(seg.length * f, cf.n)
                side_ = cf.n.cross(t)
                base = p + cf.into * 1.0
                votes += int(outer.isInside(base + side_, 1e-4, False)) - int(outer.isInside(base - side_, 1e-4, False))
        sign = 1.0 if votes >= 0 else -1.0
        out.append(Skeleton(segs, cf.n, sign, closed))
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


def near_part(outer, shape, by: float = 1.0):
    """The part of the outer solid in the box of a shape. A common with the whole outer solid comes back empty for
    some solids that lie inside it (OpenCascade, on the brow at W1); the common with the part near them is right."""
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415

    bb = shape.BoundBox
    box = Part.makeBox(bb.XLength + 2 * by, bb.YLength + 2 * by, bb.ZLength + 2 * by, App.Vector(bb.XMin - by, bb.YMin - by, bb.ZMin - by))
    return outer.common(box)


def inside_form(shape, outer):
    """The part of a shape inside the outer solid. OpenCascade loses volume in this common in two different ways (with
    the whole outer solid on the brow at W1, with the part near the shape on the feet of the deck); what is lost is
    never added, so the larger of the two results is the right one."""
    a = shape.common(outer)
    b = shape.common(near_part(outer, shape))
    return a if a.Volume >= b.Volume else b


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
        got = inside_form(raw, outer)
        if not got.Solids:
            side.notes.append(f"no flange on a line of {sk.length:.0f} mm: it is outside the form")
            continue
        # one tool at a time: a cut by many tools at once is another place where OpenCascade loses solids
        for t in trims:
            if t.BoundBox.intersect(got.BoundBox):
                got = got.cut(t)
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
    head: Side = None             # the side with the clearance holes and the head pockets
    pilot: Side = None            # the side with the pilot holes
    key: Side = None              # the side with the key: the pilot side, unless its seam face lies on the printer bed
    groove: Side = None
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
    # the volumes add: a shaft that grazes a wall and its flange is stopped, also when each graze alone is small
    hits = []
    for o in obstacles:
        if not o.BoundBox.intersect(shaft.BoundBox):
            continue
        hit = shaft.common(o)
        if hit.Volume > 1e-3:
            hits.append(hit)
    if sum(x.Volume for x in hits) < b.clash_mm3:
        return reach
    # from the mesh of what is in the way: where a round shaft meets a flat wall, the nearest point is on a curve
    # and no vertex is there
    best = min((v - sc.at).dot(head_into) - h for x in hits for v in x.tessellate(0.3)[0])
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


def in_cut_in_span(at, d: Blueprint, b: Build = BUILD) -> bool:
    """A point at a lower rear corner, in the span of the cut-ins: behind their ends on the side and outside their
    ends on the rear, with cut_in_clear more."""
    return at.y > d.cut_in_y - b.cut_in_clear and abs(at.x) > d.cut_in_x - b.cut_in_clear


def plan_screws(pair: Pair, pieces: dict, outer, obstacles: list, j: Joint, b: Build = BUILD, head: str = "",
                keep=None) -> None:
    """Choose the side of the screw heads and place the screws. The head goes on the side where more screws fit
    and the screwdriver has more room; on a level seam it is the upper piece when both are equal. A station that
    `keep` refuses gets no screw."""
    sk = max(pair.a.lines, key=lambda s: s.length)
    runs = mate_runs(sk, pair.mate, j.screw_u, b)
    pair.runs = runs
    cand = [sc for r in runs for sc in stations(r, j, b)]
    if keep is not None:
        left = [sc for sc in cand if keep(sc)]
        if len(left) < len(cand):
            pair.notes.append(f"{len(cand) - len(left)} stations in the span of the cut-ins get no screw")
        cand = left
    options = []
    for h, p in ((pair.a, pair.b), (pair.b, pair.a)):
        good, why = [], []
        for sc in cand:
            fail = screw_fits(sc, h, p, pieces, outer, j, b)
            if not fail:
                # the flange of the head side is in the way too, where the outer line turns: all of it but the head pocket
                own = h.solid.cut(screw_tools(sc, h.cf.into, j)["pocket"])
                free = free_length(sc, h.cf.into, obstacles + [own], j, b)
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


def on_bed(side: Side, up) -> bool:
    """Whether the seam face of this side lies on the printer bed: the piece prints with `up` pointing up."""
    n = math.sqrt(sum(v * v for v in up))
    return (side.cf.into.x * up[0] + side.cf.into.y * up[1] + side.cf.into.z * up[2]) / n > 0.7


def key_and_groove(pair: Pair, j: Joint, b: Build = BUILD, ups: dict | None = None, clearance: float | None = None):
    """The key and the groove: the sections of joints.py carried along the outer line. The key is on the pilot
    side, as joints.py has it. But a key must not stand on the face that lies on the printer bed (ups: piece ->
    its up direction): then the key goes on the other piece. The key lies on the mating face only; it stops key_gap
    each side of a screw and key_end_margin from the ends of each run. The groove is the key with the clearance on
    every side (`clearance`, default the groove clearance of the joint)."""
    from . import joints  # noqa: PLC0415

    pair.key, pair.groove = pair.pilot, pair.head
    if ups and on_bed(pair.pilot, ups[pair.pilot.cf.piece]) and not on_bed(pair.head, ups[pair.head.cf.piece]):
        pair.key, pair.groove = pair.head, pair.pilot
        pair.notes.append(f"the key is on {pair.head.cf.piece}: the seam face of {pair.pilot.cf.piece} lies on the printer bed")
    if not pair.runs or sum(r[-1][0] - r[0][0] for r in pair.runs) < b.run_key:
        pair.notes.append("no key: the run is shorter than %g mm" % b.run_key)
        return None, None
    h = split.KERF / 2
    up = pair.groove.cf.into
    sk = max(pair.key.lines, key=lambda s: s.length)
    c = j.groove_clearance if clearance is None else clearance
    key = carry(sk, joints.key_profile(j), up, -h, corners=False)
    groove = carry(sk, joints.groove_profile(j, c), up, h, corners=False)
    key = key.common([f.translated(up * -1.0).extrude(up * 4.0) for f in pair.mate.Faces][0] if len(pair.mate.Faces) == 1
                     else _fuse_all([f.translated(up * -1.0).extrude(up * 4.0) for f in pair.mate.Faces]))
    gaps_key, gaps_groove = [], []
    for sc in pair.screws:
        gaps_key.append(box_along(sc.at, sc.tangent, up, j.key_gap, j.flange_h, -2.0, 4.0))
        gaps_groove.append(box_along(sc.at, sc.tangent, up, j.key_gap - c, j.flange_h, -2.0, 4.0))
    for run in pair.runs:
        for s, q, t in (run[0], run[-1]):
            gaps_key.append(box_along(q, t, up, j.key_end_margin, j.flange_h, -2.0, 4.0))
            gaps_groove.append(box_along(q, t, up, j.key_end_margin - c, j.flange_h, -2.0, 4.0))
    key = key.cut(gaps_key)
    groove = groove.cut(gaps_groove)
    least = j.key_w * j.key_proj * 5.0   # a key shorter than 5 mm is left out
    keys = [s for s in key.Solids if s.Volume > least]
    grooves = [s for s in groove.Solids if s.Volume > least]
    if not keys:
        pair.notes.append("no key: nothing left between the screws and the ends")
        return None, None
    return _fuse_all(keys), _fuse_all(grooves)


def key_side_groove_in(pair: Pair, ups: dict | None, closing_pieces: list[str]) -> bool:
    """Whether the groove of a pair lies in one of the closing pieces (as key_and_groove places the key)."""
    groove = pair.head
    if ups and on_bed(pair.pilot, ups[pair.pilot.cf.piece]) and not on_bed(pair.head, ups[pair.head.cf.piece]):
        groove = pair.pilot
    return groove.cf.piece in closing_pieces


def _fuse_all(shapes: list):
    out = shapes[0]
    for sd in shapes[1:]:
        out = out.fuse(sd)
    return out


def vee(side: Side, j: Joint):
    """The half of the V on the outer edge of one piece, for the filler: the section of joints.vgroove_profile,
    which starts outside the outer line so that it cuts the edge of a wall that leans."""
    h = side.cf.gap / 2
    section = [(-1.5, -0.01), (j.vgroove_d, -0.01), (j.vgroove_d, 0.0), (0.0, j.vgroove_w / 2), (-1.5, j.vgroove_w / 2)]
    out = []
    for sk in side.lines:
        try:
            out.append(carry(sk, section, side.cf.into, h, corners=False))
        except Exception as e:  # noqa: BLE001
            side.notes.append(f"no V: {e}")
    return _fuse_all(out) if out else None


# ---------- the seams of the layout ----------

# what the whole set is known to leave out (tests/test_pieces.py holds the generator to these lists):
# (seam, piece) with no flange, and seams with a run for screws but no screw
NO_FLANGE: tuple = ()
NO_SCREW: tuple = ("F2",)   # the deck is 72 high: no screwdriver gets behind a screw in the flank break
# a pair of one seam that has the weld and the key alone, by (seam, piece): the other pairs of the seam have screws
NO_SCREW_PAIRS = {("H1", "hood sill"): "the owner, 2026-11-17: the seam is 96 long, the sill is a strip of the band wall under the marquee "
                  "window with no load of its own, the lip and the pods are bonded over that zone, and a screw pocket would come "
                  "within 1.2 of the outside. The weld holds 7.7 kN (docs/design/print-pieces.md)"}
# the pieces that close a ring (docs/blueprint/index.md, "Where each ring closes"): each goes in last, into two
# seams at once. On the seams named here its grooves get the closing gap at each side in place of the groove
# clearance; and where `face` is true (an upright seam that the piece drops into) its seam face, with the flange
# face, stands the closing gap back from the seam plane, for a bond that fills a gap (joints.OtherJoints.closing_gap).
# The second middle piece sits on the level seam L1: its grooves get the gap, its faces do not move.
CLOSING: dict = {"brow": (("W1",), True), "upper rear R": (("R5", "R3"), True), "middle R": (("L1",), False)}


def closing(piece: str, label: str) -> tuple[bool, bool]:
    """(grooves get the closing gap, the face stands back) for a side of `piece` on the seam `label`."""
    seams, face = CLOSING.get(piece, ((), False))
    return (label in seams, label in seams and face)


def closing_slab(cf: CutFace, gap: float, reach: float = 20.0):
    """The layer of a piece that a closing gap takes away at one seam face: the cut face, grown by `reach` in its plane
    so that it holds the face of the flange too, from the seam plane to `gap` past the face of the piece."""
    face = cf.face
    try:
        big = face.makeOffset2D(reach, join=2)
        face = big.Faces[0] if big.Faces else face
    except Exception:  # noqa: BLE001
        pass
    return face.translated(cf.into * -0.01).extrude(cf.into * (cf.gap / 2 + gap + 0.01))


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
    added: dict = field(default_factory=dict)            # name -> what the generator added to the plain piece, with its holes
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
    study wrote (fit/report.json of the default build, or of the shared build); and the parts of the rear that are
    not pieces (candybar.shell.rear: the head rails, the shroud, the fan, the duct and the seals), with the role
    "rear"."""
    import FreeCAD as App  # noqa: PLC0415

    from . import rear, structure  # noqa: PLC0415

    root = root or Path(os.environ.get("CANDYBAR_SHELL", CAD / "out" / "shell-rev7"))
    doc, found = structure.fit_items(root)
    out = [(sl.name, sl.role, sl.world.copy()) for it in found for sl in it.solids if sl.role in ("hardware", "keepout")]
    App.closeDocument(doc.Name)
    d = Blueprint()
    parts = rear.build(d, rear.Rear(), rear.place(d))
    out += [(name, "rear", shape) for name, shape in parts.items() if not name.startswith("door_half")]
    # the front socket plate of every variant, with its bought parts and the stretch where the foot flange stops
    return out + socket_plate_items(d)


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
             with_feet: bool = True, with_ribs: bool = True, with_floor: bool = True, with_ring: bool = True) -> Result:
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
    rings, foot_sides, cones, sockets, screw_add, screw_cut = [], [], {}, {}, {}, {}
    if with_ring and all(n in pl.shapes for n in RING_PIECES + FOOT_PIECES) and (names is None or set(names) & set(RING_PIECES + FOOT_PIECES)):
        level = top_ring(d, pl, items, res.hits, kerfs, log, j, b)
        rings = [sd for sd in level if sd.cf.piece in RING_PIECES]
        foot_sides = [sd for sd in level if sd.cf.piece in FOOT_PIECES]
        cones, sockets, res.extra["ring_cones"] = ring_cones(d, rings, foot_sides)
        screw_add, screw_cut, res.extra["hood_screws"] = hood_screws(d, rings, foot_sides, cabinet_form(pl, d))
        res.extra["ring"] = [{"piece": sd.cf.piece, "cm3": round(sd.solid.Volume / 1000, 1) if sd.solid is not None else 0.0, "notes": sd.notes}
                             for sd in level]
    # what a screwdriver must pass: the plain pieces and every flange, foot and rib but the two of its own seam
    made = [sd for sd in res.sides + res.feet + res.ribs if sd.solid is not None]
    for pair in res.pairs:
        outer = pl.outer[module[pair.a.cf.piece]]
        obstacles = list(pl.shapes.values()) + [sd.solid for sd in made if sd is not pair.a and sd is not pair.b]
        label = seam_of[pair.a.cf.seam].label
        keep = (lambda sc: not in_cut_in_span(sc.at, d, b)) if label == "L1" else None
        plan_screws(pair, pl.shapes, outer, obstacles, j, b, heads.get(label, ""), keep)
        log(f"pieces: {pair.name}: head in {pair.head.cf.piece}, {len(pair.screws)} screws {pair.notes} [{time.time() - t0:.0f} s]")
    add: dict[str, list] = {}
    cut: dict[str, list] = {}
    for side in res.feet + res.ribs + rings + foot_sides:
        if side.solid is not None:
            add.setdefault(side.cf.piece, []).append(side.solid)
    for name, shapes in cones.items():
        add.setdefault(name, []).extend(shapes)
    for name, shapes in sockets.items():
        cut.setdefault(name, []).extend(shapes)
    for name, shapes in screw_add.items():
        add.setdefault(name, []).extend(shapes)
    for name, shapes in screw_cut.items():
        cut.setdefault(name, []).extend(shapes)
    for side in res.sides:
        if side.solid is not None:
            add.setdefault(side.cf.piece, []).append(side.solid)
            if seam_of[side.cf.seam].joint == "bond-fill":
                r = vee(side, j)
                if r is not None:
                    cut.setdefault(side.cf.piece, []).append(r)
    ups = {p.full: p.up for p in pl.pieces}
    from .joints import OTHER_JOINTS  # noqa: PLC0415
    gap = OTHER_JOINTS.closing_gap
    res.extra["closing"] = []
    for pair in res.pairs:
        label = seam_of[pair.a.cf.seam].label
        wide = [sd.cf.piece for sd in (pair.a, pair.b) if closing(sd.cf.piece, label)[0]]
        # the groove of a closing piece gets the closing gap; the key stays on the side that joints.py gives it
        key, groove = key_and_groove(pair, j, b, ups, gap if key_side_groove_in(pair, ups, wide) else None)
        hp, pp = pair.head.cf.piece, pair.pilot.cf.piece
        if key is not None:
            add.setdefault(pair.key.cf.piece, []).append(key)
            cut.setdefault(pair.groove.cf.piece, []).append(groove)
        for sc in pair.screws:
            tools = screw_tools(sc, pair.head.cf.into, j)
            cut.setdefault(pp, []).extend([tools["pilot"], tools["counterbore"]])
            cut.setdefault(hp, []).extend([tools["clearance"], tools["pocket"]])
    for name, shape in pl.shapes.items():
        if names is not None and name not in names:
            continue
        out = shape
        if add.get(name):
            extra = _fuse_all(add[name])
            res.added[name] = extra.cut(cut[name]) if cut.get(name) else extra
            out = shape.fuse(extra)
            if out.Volume < shape.Volume + 0.2 * extra.Volume:
                # the fuse lost solids: one at a time
                out = shape
                for sd in add[name]:
                    out = out.fuse(sd)
                log(f"pieces: {name}: the fuse of all flanges at once lost volume; fused one at a time")
        slabs = [closing_slab(sd.cf, gap) for sd in res.sides if sd.cf.piece == name and closing(name, seam_of[sd.cf.seam].label)[1]]
        if slabs:
            before = out.Volume
            out = out.cut(_fuse_all(slabs))
            res.extra["closing"].append({"piece": name, "seams": sorted({seam_of[sd.cf.seam].label for sd in res.sides if sd.cf.piece == name
                                                                          and closing(name, seam_of[sd.cf.seam].label)[1]}),
                                         "gap": gap, "removed_mm3": round(before - out.Volume, 1)})
        if cut.get(name):
            out = out.cut(cut[name])
        if add.get(name) or cut.get(name) or slabs:
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


# ---------- joint 7: the top ring of the body and the foot of the hood ----------

RING_PIECES = ("brow", "upper R", "upper L", "upper rear R", "upper rear L")   # the pieces that carry the body top
FOOT_PIECES = ("hood centre", "hood side R", "hood side L", "hood sill")   # the hood sill: since band A (2026-11-16)
RING_CONE_X = 150.0      # the four cones of the ring: at x +-RING_CONE_X, at the front and at the rear
# the screws of the bolted hood (the owner, 2026-11-16: "for the hood - we can bolt it on"): (side, y), on the middle
# line of the side ring at that y. Each is an M4 screw from below, up through a boss of the ring into a heat-set insert
# in a boss of the foot, turned with a 3 mm hex key from inside the body with the rear door off
# (docs/design/print-pieces.md, "The bolted hood"). On the sides, behind the monitor: under the front cones the
# cradle of the monitor stands 48 below the ring, and the rear ring lies over the rear shelf, which a key from the
# door cannot pass upright
HOOD_SCREWS: tuple = ((1, 475.0), (-1, 475.0), (1, 540.0), (-1, 540.0))
HOOD_KEY = 100.0   # mm: a hex key from below needs this much straight and free under the head of a screw of the hood


def ring_top(d: Blueprint) -> float:
    """The top of the ring inside the wall: the foot of the hood lies on it, so the seam gap of the form stays
    d.seam_gap outside (a bolted hood has no bond line)."""
    return d.body_top + d.seam_gap


def ring_joints(j: Joint):
    """The joint values of the top ring (OtherJoints ring_w x ring_t, between the inserts) and of the foot of the
    hood (ring_w x hood_foot_t), as Joint values that the flange code carries along the outer line."""
    from dataclasses import replace  # noqa: PLC0415
    from .joints import OTHER_JOINTS as oj  # noqa: PLC0415

    return replace(j, flange_h=oj.ring_w, flange_t=oj.ring_t), replace(j, flange_h=oj.ring_w, flange_t=oj.hood_foot_t)


def ring_section(j: Joint, rise: float, b: Build = BUILD):
    """The section of the top ring, (u inward, z down from the body top): the flange of 14 x ring_t with its gusset,
    and inside the wall a rise of `rise` up to the foot of the hood, so that the seam gap of the form stays open
    outside. At each screw of the hood the ring has a boss (hood_screws)."""
    w, h, t, g = j.wall_t, j.flange_h, j.flange_t, j.gusset_leg
    return lambda seg: [(b.skin_lap, 0.0), (w + 0.2, 0.0), (w + 0.2, -rise), (w + h, -rise), (w + h, t), (w, t + g), (b.skin_lap, t + g)]


def level_faces(pl: Plain, names: tuple, z: float, up: bool) -> list:
    """The planar faces of the named pieces that lie in the level plane z and face up (or down), as CutFace objects
    of the seam "G": the body top of the ring pieces, the foot of the hood pieces."""
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415

    n = App.Vector(0, 0, 1)
    out = []
    for name in names:
        for f in pl.shapes[name].Faces:
            if isinstance(f.Surface, Part.Plane) and abs(f.CenterOfMass.z - z) < 1e-3 and abs(f.Surface.Axis.z) > 1 - 1e-9 \
                    and (f.normalAt(0, 0).z > 0) == up:
                out.append(CutFace("G", len(out), name, f, n, -1 if up else 1, f.CenterOfMass, 0.0))
    return out


def cabinet_form(pl: Plain, d: Blueprint):
    """The outer form of the body and the hood with the seam gap between them filled: the form that the ring and the
    foot must stay inside."""
    import FreeCAD as App  # noqa: PLC0415

    body, hood = pl.outer["body"], pl.outer["hood"]
    sec = body.slice(App.Vector(0, 0, 1), d.body_top - 0.01)
    import Part  # noqa: PLC0415

    face = Part.Face(Part.Wire(max(sec, key=lambda w: w.Length).Edges)).translated(App.Vector(0, 0, 0.01))
    gap = face.extrude(App.Vector(0, 0, d.seam_gap))
    return body.fuse([hood, gap]).removeSplitter()


def top_ring(d: Blueprint, pl: Plain, items: list, hits: list, kerfs: dict, log=print, j: Joint | None = None, b: Build = BUILD) -> list[Side]:
    """Joint 7 (docs/blueprint/index.md): the top ring on the body pieces under the body top, and the foot of the hood
    on the hood pieces. The ring rises inside the wall to the foot, which lies on it with a bond line of 0.1. The
    flanges end at the cut faces of the other seams of their module, as the flanges of joint 1 do."""
    from . import split as sp  # noqa: PLC0415

    j = j or joint()
    jr, jf = ring_joints(j)
    form = cabinet_form(pl, d)
    module = {p.full: p.module for p in pl.pieces}
    out = []
    for cf, jj, section in ([(cf, jr, ring_section(jr, ring_top(d) - d.body_top, b)) for cf in level_faces(pl, RING_PIECES, d.body_top, True)]
                            + [(cf, jf, None) for cf in level_faces(pl, FOOT_PIECES, d.body_top + d.seam_gap, False)]):
        mod = module[cf.piece]
        sec = form.slice(cf.n, cf.origin.z)
        import Part  # noqa: PLC0415

        side = Side(cf, outer_lines(cf, form, Part.makeCompound(sec), b))
        if not side.lines:
            side.notes.append("no outer line on the level plane")
            out.append(side)
            continue
        for sk in side.lines:
            for seg in sk.segs:
                seg.lean_out, seg.gusset = False, True
        trims = [k for (m, k) in kerfs.values() if m == mod]
        flange(side, pl.shapes[cf.piece], form, trims, jj, b, section)
        cut_back(side, pl.shapes[cf.piece], items, hits, b)
        out.append(side)
        log(f"pieces: joint 7 on {cf.piece}: {0 if side.solid is None else side.solid.Volume / 1000:.1f} cm3 {side.notes}")
    return out


def ring_cones(d: Blueprint, rings: list[Side], feet: list[Side]) -> tuple[dict, dict, list]:
    """The four cones of joint 7 on the top of the ring (two at the front, two at the rear, at x +-RING_CONE_X), and
    their sockets in the foot of the hood. Returns (cones by piece, sockets by piece, the places)."""
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415
    from .joints import OTHER_JOINTS as oj  # noqa: PLC0415

    top = ring_top(d)   # the top of the ring inside the wall
    cones, sockets, places = {}, {}, []
    up = App.Vector(0, 0, 1)
    for x in (RING_CONE_X, -RING_CONE_X):
        line = Part.makeLine(App.Vector(x, -100.0, top - 0.05), App.Vector(x, 800.0, top - 0.05))
        hits = []
        for r in rings:
            if r.solid is None:
                continue
            for e in r.solid.common(line).Edges:
                ys = sorted(v.Point.y for v in e.Vertexes)
                if ys[1] - ys[0] > oj.cone_d + 2.0:
                    hits.append(((ys[0] + ys[1]) / 2, r.cf.piece))
        if not hits:
            continue
        for y, piece in (min(hits), max(hits)):
            p = App.Vector(x, y, top)
            c = oj.cone_clearance
            cones.setdefault(piece, []).append(Part.makeCone(oj.cone_d / 2, 1.0, oj.cone_h, p - up * 0.01, up))
            foot = next((f for f in feet if f.solid is not None and f.solid.distToShape(Part.Vertex(p + up * 0.2))[0] < 0.3), None)
            if foot is not None:
                sockets.setdefault(foot.cf.piece, []).append(Part.makeCone(oj.cone_d / 2 + c, 1.0 + c, oj.cone_h + c, p - up * 0.01, up))
            places.append({"at": [round(p.x, 1), round(p.y, 1), round(p.z, 2)], "ring": piece, "foot": foot.cf.piece if foot else None})
    return cones, sockets, places


def hood_screws(d: Blueprint, rings: list[Side], feet: list[Side], form, places: tuple = HOOD_SCREWS) -> tuple[dict, dict, list]:
    """The screws of the bolted hood at `places`: under the ring a boss of service_boss down to ring_h below its top
    (the seat of the head), with a clearance hole; in the foot a boss of service_boss up to hood_boss_h above its
    lower face, with the hole of the M4 insert from below. Each boss stays inside the outer form. Returns (added
    solids by piece, cut solids by piece, the rows of the report)."""
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415
    from .joints import OTHER_JOINTS as oj  # noqa: PLC0415

    V = App.Vector
    top = ring_top(d)
    cyl = lambda dia, x, y, z0, z1: Part.makeCylinder(dia / 2, z1 - z0, V(x, y, z0), V(0, 0, 1))
    add, cut, rows = {}, {}, []
    nearest = lambda sides, q: min((s for s in sides if s.solid is not None), key=lambda s: s.solid.distToShape(Part.Vertex(q))[0])
    for side, y in places:
        # the middle line of the ring at y: the rise of the ring inside the wall, just under its top
        line = Part.makeLine(V(0.0, y, top - 0.05), V(side * 400.0, y, top - 0.05))
        spans = [sorted(v.Point.x for v in e.Vertexes) for r in rings if r.solid is not None for e in r.solid.common(line).Edges]
        a, b_ = max(spans, key=lambda sp: abs(sp[0] + sp[1]))
        x = (a + b_) / 2
        ring = nearest(rings, V(x, y, top - 0.5))
        foot = nearest(feet, V(x, y, top + 0.5))
        seat = top - oj.ring_h
        rb = cyl(oj.service_boss, x, y, seat, top).common(form)
        fb = cyl(oj.service_boss, x, y, top, top + oj.hood_boss_h).common(form)
        add.setdefault(ring.cf.piece, []).append(rb)
        add.setdefault(foot.cf.piece, []).append(fb)
        cut.setdefault(ring.cf.piece, []).append(cyl(oj.hood_screw_hole_d, x, y, seat - 1.0, top + 0.5))
        cut.setdefault(foot.cf.piece, []).append(cyl(oj.insert_hole_d, x, y, top - 0.5, top + oj.insert_hole_depth))
        rows.append({"at": [round(x, 1), round(y, 1), round(seat, 2)], "ring": ring.cf.piece, "foot": foot.cf.piece,
                     "screw": oj.hood_screw, "ring_boss_cm3": round(rb.Volume / 1000, 2), "foot_boss_cm3": round(fb.Volume / 1000, 2)})
    return add, cut, rows


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
    foot_thick: float = 5.0          # and is this thick: half the floor
    rebate_gap: float = 0.3       # the rebate is this much wider than the foot flange
    rebate_lift: float = 0.2      # and this much higher: the bond line
    lap_gap: float = 0.2          # between two tiles, in plan
    lap_lift: float = 0.1         # between the two halves of a lap: the bond line
    screw_len: float = 9.5         # 3.5 x 9.5, countersunk: it does not reach the table through 10 mm
    pilot_hole: float = 2.6         # ASSUMPTION: 0.75 d, the table value for PET, as joints.Joint.pilot_d_pet
    clear_hole: float = 3.9
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
    rebate = outline.cut(Part.makeFace(inner.Wires, "Part::FaceMakerBullseye")).translated(up * -1.0).extrude(up * (1.0 + fl.foot_thick + fl.rebate_lift))
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
        hole = Part.makeCylinder(fl.clear_hole / 2, half + 1.0, App.Vector(p.x, p.y, top - half - 0.5), up)
        sink = Part.makeCone(fl.clear_hole / 2, fl.head_d / 2 + 0.01, (fl.head_d - fl.clear_hole) / 2, App.Vector(p.x, p.y, top - (fl.head_d - fl.clear_hole) / 2 + 0.01), up)
        pilot = Part.makeCylinder(fl.pilot_hole / 2, fl.screw_len - half + 1.5, App.Vector(p.x, p.y, top - fl.screw_len - 1.0), up)
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
            q = App.Vector(p.x, p.y, fl.foot_thick / 2)
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
    profile = [(b.skin_lap, 0.0), (fl.foot_w, 0.0), (fl.foot_w, fl.foot_thick), (b.skin_lap, fl.foot_thick)]
    outline, _ = floor_plan(outer, fl)
    inner = Part.makeFace(outline.makeOffset2D(-fl.foot_w, join=2).Wires, "Part::FaceMakerBullseye")
    band = outline.cut(inner).translated(App.Vector(0, 0, -1.0)).extrude(App.Vector(0, 0, fl.foot_thick + 2.0))
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
        if side.solid is not None:
            # only the band along the outline: where the outline turns at the end of a piece (the foot of the band),
            # the line goes on straight and would reach into the plan of the floor
            kept = [sd for sd in side.solid.common(band).Solids if sd.Volume > b.debris_mm3 and sd.common(shape).Volume > 0.5]
            side.solid = _fuse_all(kept) if kept else None
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
            Rib("rear lower", "x", on_a_bar(third, d), "lower rear wall below the door, one half", (116.0, 211.0)),
            Rib("rear lower", "x", on_a_bar(2 * third, d), "lower rear wall below the door, one half", (116.0, 211.0))]


def on_a_bar(x: float, d: Blueprint) -> float:
    """x, or the middle of the nearest bar of the inlet (candybar.shell.rear) when x is inside its field of slots:
    a rib across a slot would close a part of it. The openings of the supply on the left are the mirror of the inlet."""
    from . import rear  # noqa: PLC0415

    slots = sorted((f.BoundBox.XMin, f.BoundBox.XMax) for f in rear.inlet(rear.Rear(), rear.place(d)))
    if not slots[0][0] - RIB_T / 2 < x < slots[-1][1] + RIB_T / 2:
        return x
    bars = [(a[1] + b[0]) / 2 for a, b in zip(slots, slots[1:])]
    return min(bars, key=lambda c: abs(c - x))


def rib_sides(d: Blueprint, pl: Plain, names: list[str] | None, items: list, hits: list, extra_trims: dict, log=print, b: Build = BUILD) -> list[Side]:
    """Each rib as a side: the section of the piece in the plane of the rib is its cut face, and a rectangle of
    RIB_T by wall_t + RIB_H is carried along the outer line of that section."""
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415

    outer = pl.outer["body"]
    kerfs = [grown_kerf(poly, b.seam_reach) for s in pl.seams if s.module == "body" for poly in s.polys] + zones(d, b)["body"]
    w = d.wall_t
    # the section of a rib is centred on its plane: the plane of a rib on a bar of the inlet lies on the bar
    profile = [(b.skin_lap, -RIB_T / 2), (w + RIB_H, -RIB_T / 2), (w + RIB_H, RIB_T / 2), (b.skin_lap, RIB_T / 2)]
    out = []
    for rib in ribs(d):
        for sx, tag in ((1.0, "R"), (-1.0, "L")):
            name = f"{rib.piece} {tag}"
            if name not in pl.shapes or (names is not None and name not in names):
                continue
            n = App.Vector(1, 0, 0) if rib.axis == "x" else App.Vector(0, 1, 0)
            at = rib.at * sx if rib.axis == "x" else rib.at
            origin = n * at
            wires = pl.shapes[name].slice(n, at)
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
            section = Part.makeCompound(outer.slice(n, at))
            side = Side(cf, outer_lines(cf, outer, section, b))
            if not side.lines:
                log(f"pieces: rib {rib.axis} {at:g} of {name}: no outer line")
                continue
            trims = kerfs + extra_trims.get(name, [])
            flange(side, pl.shapes[name], outer, trims, JOINT, b, section=lambda seg: profile)
            whole = side.solid.Volume if side.solid is not None else 0.0
            cut_back(side, pl.shapes[name], items, hits, b)
            if side.solid is not None and side.solid.Volume < 0.5 * whole:
                # hardware stands against the wall here: a stub of a rib does nothing
                side.solid = None
                side.notes.append("left out: less than half of the rib is clear of the hardware")
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


def write_brep(shape, path: Path):
    """A BREP file that reads as a valid shape; returns the shape as the file holds it. The text file keeps 15 digits, and some narrow step faces of the
    skin are not valid when they come back from it (also with OpenCascade 7.9.3: deck side R); ShapeFix repairs them
    with no change of volume, and the repaired shape stays valid in the file."""
    import Part  # noqa: PLC0415

    shape.exportBrep(str(path))
    back = Part.Shape()
    back.read(str(path))
    if back.isValid():
        return back
    volume = back.Volume
    back.fix(1e-7, 1e-7, 1e-2)
    if not back.isValid() or abs(back.Volume - volume) > 0.5 or len(back.Solids) != len(shape.Solids):
        raise RuntimeError(f"pieces: {path.name} does not read as a valid shape, and the repair did not help")
    back.exportBrep(str(path))
    again = Part.Shape()
    again.read(str(path))
    if not again.isValid():
        raise RuntimeError(f"pieces: {path.name} is not valid after the repair was written")
    return again


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
        # the mesh and the edges come from the shape as the file holds it: the mesh of a shape in memory had a
        # triangle at the origin (hood side), and the file did not
        shape = write_brep(shape, folder / f"{stem}.brep")
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
    up = {p.full: p.up for p in res.plain.pieces}

    def on_bed(sd: Side) -> str:
        """Where the flange lies in the print orientation of its piece."""
        u = up.get(sd.cf.piece, (0.0, 0.0, 1.0))
        n = math.sqrt(sum(v * v for v in u))
        dot = (sd.cf.into.x * u[0] + sd.cf.into.y * u[1] + sd.cf.into.z * u[2]) / n
        return "on the bed" if dot > 0.7 else "at the top" if dot < -0.7 else "upright"

    side_row = lambda sd: {"seam": sd.cf.seam, "k": sd.cf.k, "piece": sd.cf.piece, "in_print": on_bed(sd),
                           "longest_straight_mm": round(max((seg.length for sk in sd.lines for seg in sk.segs if seg.c is None), default=0.0), 1),
                           "flange_cm3": round(sd.solid.Volume / 1000, 1) if sd.solid is not None else 0.0,
                           "line_mm": round(sum(sk.length for sk in sd.lines), 1), "lean_out": sd.lean_out, "gusset": sd.gusset, "notes": sd.notes}
    pairs = [{"seam": p.a.cf.seam, "k": p.a.cf.k, "head": p.head.cf.piece, "pilot": p.pilot.cf.piece,
              "key": p.key.cf.piece if p.key is not None and not any(n.startswith("no key") for n in p.notes) else None, "mate_cm2": round(p.mate.Area / 100, 1),
              "run_mm": round(sum(r[-1][0] - r[0][0] for r in p.runs), 1), "normal": vec(p.head.cf.into),
              "screws": [{"at": vec(sc.at), "along": [round(v, 4) for v in sc.tangent], "free": round(sc.free)} for sc in p.screws], "notes": p.notes} for p in res.pairs]
    return {"sides": [side_row(sd) for sd in res.sides], "feet": [side_row(sd) for sd in res.feet], "ribs": [side_row(sd) for sd in res.ribs],
            "pairs": pairs, "hits": res.hits, "floor": res.extra.get("floor", {}), "closing": res.extra.get("closing", []),
            "ring": res.extra.get("ring", []), "ring_cones": res.extra.get("ring_cones", []), "merged": res.extra.get("merged", []),
            "hood_screws": res.extra.get("hood_screws", [])}


# ---------- the checks of the whole set ----------

def tight_box(shape):
    """The box of a shape from its mesh: the BoundBox of a shape read from a file is not tight."""
    import numpy as np  # noqa: PLC0415

    pts, _ = shape.tessellate(0.5)
    p = np.array([(v.x, v.y, v.z) for v in pts])
    return p, p.min(axis=0), p.max(axis=0)


def overhang(shape, up, deflection: float = 0.3) -> dict:
    """What a print orientation does to a piece, from its mesh, cm2: the area on the bed, the area that faces down
    more than split.OVERHANG from upright (it needs support) and the area at that limit."""
    import numpy as np  # noqa: PLC0415

    pts, tris = shape.tessellate(deflection)
    p = np.array([(v.x, v.y, v.z) for v in pts])
    t = np.array(tris)
    u = np.array(up, float)
    u /= np.linalg.norm(u)
    a, b_, c = p[t[:, 0]], p[t[:, 1]], p[t[:, 2]]
    n = np.cross(b_ - a, c - a)
    area = np.linalg.norm(n, axis=1) / 2
    nz = (n @ u) / (2 * area + 1e-12)
    h = ((a + b_ + c) / 3) @ u
    z0 = (p @ u).min()
    at_bed = h < z0 + 0.5
    over = -math.sin(math.radians(split.OVERHANG + split.OVERHANG_BAND))
    limit = -math.sin(math.radians(split.OVERHANG - split.OVERHANG_BAND))
    return {"bed_cm2": round(float(area[(nz < -0.9998) & at_bed].sum()) / 100, 1),
            "overhang_cm2": round(float(area[(nz < over) & ~at_bed].sum()) / 100, 1),
            "limit_cm2": round(float(area[(nz >= over) & (nz <= limit) & ~at_bed].sum()) / 100, 1)}


def split_rows() -> dict:
    """The rows of the split's own measurement of the plain pieces (seen faces that overhang), when it is on disk."""
    f = Path(os.environ.get("CANDYBAR_SHELL", CAD / "out" / "shell-rev7")) / "split" / "measurements.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))[split.SHELL]["pieces"]
    return {}


def check_set(d: Blueprint, pl: Plain, made: dict, rep: dict, items: list, log=print, b: Build = BUILD) -> dict:
    """The checks of the whole set: every piece is one valid solid inside the printer's limit; no two pieces share
    volume; no piece is in the hardware; a screwdriver reaches each screw past the finished pieces; the mass; the
    screws; what each print orientation overhangs. made: the finished pieces; rep: seam_report of the build."""
    import FreeCAD as App  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415

    lim = split.printer()
    up = {p.full: p.up for p in pl.pieces}
    bed = {p.full: p.bed for p in pl.pieces}
    before = split_rows()
    rows, boxes = {}, {}
    t0 = time.time()
    for name, shape in made.items():
        pts, lo, hi = tight_box(shape)
        boxes[name] = (lo, hi)
        row = {"valid": bool(shape.isValid()), "solids": len(shape.Solids), "faces": len(shape.Faces),
               "volume_cm3": round(shape.Volume / 1000, 1), "plain_cm3": round(pl.shapes[name].Volume / 1000, 1) if name in pl.shapes else None,
               "mass_g": round(shape.Volume / 1000 * split.ABS_G_PER_CM3), "bed": bed[name], "up": [round(v, 3) for v in up[name]],
               **split.print_box(pts, up[name], lim), **overhang(shape, up[name])}
        if name.startswith("floor"):
            # a tile prints flat either way up: the way with less overhang
            flipped = overhang(shape, tuple(-v for v in up[name]))
            row["flipped"] = flipped
            if flipped["overhang_cm2"] < row["overhang_cm2"]:
                row.update(flipped)
                row["bed"] = "flat, top face on the bed"
                row["up"] = [-v for v in row["up"]]
        elif name in before:
            row["seen_overhang_plain_cm2"] = before[name].get("overhang_seen")
            row["overhang_plain_cm2"] = round(before[name].get("overhang_seen", 0.0) + before[name].get("overhang_inside", 0.0), 1)
        rows[name] = row
    log(f"pieces: boxes and overhangs [{time.time() - t0:.0f} s]")
    names = list(made)
    clashes = []
    for i, a in enumerate(names):
        for c in names[i + 1:]:
            (alo, ahi), (clo, chi) = boxes[a], boxes[c]
            if np.any(alo > chi + 0.1) or np.any(clo > ahi + 0.1):
                continue
            v = made[a].common(made[c]).Volume
            if v > b.clash_mm3:
                clashes.append({"a": a, "b": c, "mm3": round(v, 1)})
    log(f"pieces: clashes between pieces: {clashes} [{time.time() - t0:.0f} s]")
    hard = []
    for iname, role, solid in items or []:
        sb = solid.BoundBox
        for name, shape in made.items():
            lo, hi = boxes[name]
            if sb.XMin > hi[0] or sb.XMax < lo[0] or sb.YMin > hi[1] or sb.YMax < lo[1] or sb.ZMin > hi[2] or sb.ZMax < lo[2]:
                continue
            v = shape.common(solid).Volume
            if v > b.clash_mm3:
                plain_v = pl.shapes[name].common(solid).Volume if name in pl.shapes and not name.startswith("floor") else 0.0
                hard.append({"piece": name, "item": iname, "role": role, "mm3": round(v, 1), "of_the_plain_piece_mm3": round(plain_v, 1)})
    log(f"pieces: clashes with hardware: {hard} [{time.time() - t0:.0f} s]")
    # the screwdriver again, past the finished pieces
    j = joint()
    reach = []
    solids = list(made.values())
    for p in rep["pairs"]:
        into = App.Vector(*p["normal"])
        for sc in p["screws"]:
            free = free_length(Screw(App.Vector(*sc["at"]), None), into, solids, j, b)
            reach.append({"seam": p["seam"], "head": p["head"], "at": sc["at"], "free": round(free)})
    short = [r for r in reach if r["free"] < b.driver_len]
    log(f"pieces: screws that a screwdriver does not reach: {short} [{time.time() - t0:.0f} s]")
    hood = hood_reach(rep.get("hood_screws", []), made, items)
    log(f"pieces: the screws of the hood, free under the head: {[r['free'] for r in hood]} [{time.time() - t0:.0f} s]")
    fl = rep.get("floor", {})
    wall_g = sum(r["mass_g"] for n, r in rows.items() if not n.startswith("floor"))
    plain_g = sum(pl.shapes[n].Volume / 1000 * split.ABS_G_PER_CM3 for n in rows if not n.startswith("floor"))
    part = lambda rows_: round(sum(r["flange_cm3"] for r in rows_) * split.ABS_G_PER_CM3)
    twins = [{"piece": n[:-2], "right_cm3": r["volume_cm3"], "left_cm3": rows[n[:-1] + "L"]["volume_cm3"]} for n, r in rows.items()
             if n.endswith(" R") and n[:-1] + "L" in rows and abs(r["volume_cm3"] - rows[n[:-1] + "L"]["volume_cm3"]) > 0.05]
    return {"pieces": rows, "twins_that_differ": twins, "clashes": clashes, "hardware": hard, "reach": reach, "reach_short": short,
            "hood_reach": hood,
            "screws": {"joint 1, 3.0 x 16": sum(len(p["screws"]) for p in rep["pairs"]),
                       "floor, 3.5 x 9.5 countersunk": len(fl.get("lap_screws", [])) + len(fl.get("foot_screws", []))},
            "cones": len(fl.get("cones", [])),
            "mass": {"pieces_without_floor_g": wall_g, "plain_skin_without_floor_g": round(plain_g),
                     "joints_ribs_feet_g": round(wall_g - plain_g), "flanges_and_gussets_g": part(rep["sides"]), "feet_g": part(rep["feet"]),
                     "ribs_g": part(rep["ribs"]), "floor_solid_g": sum(r["mass_g"] for n, r in rows.items() if n.startswith("floor"))},
            "printer": vars(lim),
            "ok": all(r["valid"] and r["solids"] == 1 and r["fits"] for r in rows.values()) and not clashes and not short
                  and all(r["free"] >= HOOD_KEY for r in hood)}


def hood_reach(screws: list[dict], made: dict, items: list) -> list[dict]:
    """For each screw of the hood: how far a hex key goes straight down from the head (ring_h below the ring's top,
    less the head) before it meets a piece or a part of the hardware, up to 300; and the nearest of them sideways at
    20, 50 and 80 under the head."""
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415
    from .joints import OTHER_JOINTS as oj  # noqa: PLC0415

    out = []
    others = list(made.items()) + [(n, s) for n, _, s in items or []]
    for sc in screws:
        x, y, seat = sc["at"]
        z0 = seat - oj.hood_screw_head[1]
        seg = Part.makeLine(App.Vector(x, y, z0 - 0.1), App.Vector(x, y, z0 - 300.0))
        free, what = 300.0, ""
        for n, s in others:
            if not s.BoundBox.intersect(seg.BoundBox):
                continue
            for e in s.common(seg).Edges:
                top = max(v.Point.z for v in e.Vertexes)
                if z0 - top < free:
                    free, what = z0 - top, n
        side = {}
        for dz in (20.0, 50.0, 80.0):
            q = Part.Vertex(App.Vector(x, y, z0 - dz))
            near = [(round(s.distToShape(q)[0], 1), n) for n, s in others if s.BoundBox.isInside(App.Vector(x, y, z0 - dz)) or
                    abs(s.BoundBox.XMin - x) < 100 or abs(s.BoundBox.XMax - x) < 100]
            side[str(dz)] = min(near) if near else None
        out.append({"at": sc["at"], "head_z": round(z0, 2), "free": round(free, 1), "first": what, "room": side})
    return out


PIECE_COUNT = 30   # the pieces of the split since 2026-11-16 (band A: no stand-ins, the hood sill)


def set_rules(d: Blueprint, pl: Plain, made: dict, rep: dict, chk: dict, items: list, res: "Result | None" = None, log=print) -> dict:
    """The joint rules of the whole set, each with its result: {rule: {"ok": bool, "detail": ..., "seconds": t}}. The
    rules that need the sides, ribs and added solids of the generation (res) are skipped when it is not given (a check
    of the files alone, check_files): their "ok" is None. made: the pieces as the files hold them."""
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415
    from .joints import OTHER_JOINTS as oj  # noqa: PLC0415

    V = App.Vector
    out: dict[str, dict] = {}

    def rule(name, fn, needs_res=False):
        t0 = time.time()
        if needs_res and res is None:
            out[name] = {"ok": None, "detail": "needs the generation (the build), not checked on the files alone", "seconds": 0.0}
            return
        ok, detail = fn()
        out[name] = {"ok": bool(ok), "detail": detail, "seconds": round(time.time() - t0, 1)}
        log(f"pieces: rule {name}: {'pass' if ok else 'FAIL'}{'' if ok else ': ' + str(detail)} [{out[name]['seconds']} s]")

    def piece_count():
        return len(made) == PIECE_COUNT, {"pieces": len(made), "expected": PIECE_COUNT}

    def closing_gap():
        gap = oj.closing_gap
        done = {c["piece"]: c for c in rep.get("closing", [])}
        want = {"brow": ["W1"], "upper rear R": ["R3", "R5"]}
        bad = [] if {k: done[k]["seams"] for k in done} == want else [f"closing pieces {sorted(done)} with their seams: expected {want}"]
        for side in res.sides:
            label = side.cf.seam.split()[0]
            if not closing(side.cf.piece, label)[1]:
                continue
            if done.get(side.cf.piece, {}).get("removed_mm3", 0.0) <= 0.0:
                bad.append(f"{side.cf.piece}: nothing removed at {side.cf.seam}")
            v = made[side.cf.piece].common(closing_slab(side.cf, gap - 0.02)).Volume
            if v >= 0.05:
                bad.append(f"{side.cf.piece} at {side.cf.seam}: {v:.2f} mm3 nearer to the seam plane than the closing gap {gap:g}")
        return not bad, bad

    def flange_both():
        none = sorted({(sd["seam"].split()[0], sd["piece"].rsplit(" ", 1)[0] if sd["piece"][-1] in "RL" else sd["piece"])
                       for sd in rep["sides"] if sd["flange_cm3"] == 0.0})
        return none == sorted(NO_FLANGE), {"without a flange": none, "known exceptions": list(NO_FLANGE)}

    def screws_on_long_seams():
        excepted = lambda p: any(p["seam"].split()[0] == label and piece in (p["head"], p["pilot"]) for label, piece in NO_SCREW_PAIRS)
        bare = sorted({p["seam"].split()[0] for p in rep["pairs"] if p["run_mm"] >= 2 * BUILD.run_screw and not p["screws"] and not excepted(p)})
        return bare == sorted(NO_SCREW), {"long seams with no screw": bare, "known exceptions": list(NO_SCREW),
                                          "known pairs": [f"{k[0]} at {k[1]}" for k in NO_SCREW_PAIRS]}

    def joint_7():
        bad = []
        ringed = {r["piece"] for r in rep.get("ring", []) if r["cm3"] > 10.0}
        if ringed != set(RING_PIECES) | set(FOOT_PIECES):
            bad.append(f"ring or foot on {sorted(ringed)}, expected {sorted(set(RING_PIECES) | set(FOOT_PIECES))}")
        cones = rep.get("ring_cones", [])
        if len(cones) != 4 or not all(c["foot"] in FOOT_PIECES for c in cones):
            bad.append(f"cones: {cones}")
        if res is not None:
            # the gap between the body top and the foot of the hood stays open outside the wall: 1 and 3 inside the
            # outer line of the body top, in the middle of the gap, no piece of the ring or the foot has material
            body = pl.outer["body"]
            wire = max(body.slice(V(0, 0, 1), d.body_top - 0.01), key=lambda w: w.Length)
            z = d.body_top + d.seam_gap / 2
            points = []
            for e in wire.Edges:
                for t in (0.25, 0.5, 0.75):
                    u = e.FirstParameter + (e.LastParameter - e.FirstParameter) * t
                    q, tan = e.valueAt(u), e.tangentAt(u)
                    n = V(-tan.y, tan.x, 0.0)
                    if not body.isInside(V(q.x, q.y, d.body_top - 1.0) + n * 1.0, 1e-4, True):
                        n = n * -1.0
                    points += [V(q.x, q.y, z) + n * k for k in (1.0, 3.0)]
            for name in RING_PIECES + FOOT_PIECES:
                shape = made[name]
                inside = [q for q in points if shape.BoundBox.isInside(q) and shape.isInside(q, 1e-4, True)]
                if inside:
                    bad.append(f"{name} has material in the seam gap at {len(inside)} of {len(points)} points")
        return not bad, bad

    def no_flange_in_rear():
        rear = {n for n, role, _ in items if role == "rear"}
        more = [h for h in chk["hardware"] if h["item"] in rear and h["mm3"] - h["of_the_plain_piece_mm3"] > BUILD.clash_mm3]
        return not more, more

    def no_key_on_bed():
        where = {(sd["seam"], sd["k"], sd["piece"]): sd["in_print"] for sd in rep["sides"]}
        bad = [(p["seam"], p["key"]) for p in rep["pairs"] if p["key"] and where[(p["seam"], p["k"], p["key"])] == "on the bed"]
        keys = len([p for p in rep["pairs"] if p["key"]])
        return not bad and keys > 20, {"keys on the bed": bad, "keys": keys}

    def l1_screws():
        l1 = [sc["at"] for p in rep["pairs"] if p["seam"].split()[0] == "L1" for sc in p["screws"]]
        inside = [at for at in l1 if in_cut_in_span(V(*at), d)]
        return bool(l1) and not inside, {"L1 screws": len(l1), "in the span of the cut-ins": inside}

    def door_zone():
        x = d.door_w / 2 + BUILD.door_stop - 0.5
        zone = Part.makeBox(2 * x, 30.0, d.door_z1 - d.door_z0 + 2 * BUILD.door_stop - 1.0, V(-x, d.body_d - d.wall_t - 28.0, d.door_z0 - BUILD.door_stop + 0.5))
        bad = []
        for sd in res.sides + res.ribs:
            if sd.solid is not None and sd.solid.BoundBox.intersect(zone.BoundBox):
                v = sd.solid.common(zone).Volume
                if v >= 1.0:
                    bad.append(f"{sd.cf.seam} {sd.cf.piece}: {v:.1f} mm3 in the zone of the door opening")
        return not bad, bad

    def floor_tiles():
        fl = rep.get("floor", {})
        tiles = sorted(n for n in made if n.startswith("floor"))
        used = sorted({sc["upper"] for sc in fl.get("lap_screws", [])} | {sc["lower"] for sc in fl.get("lap_screws", [])}
                      | {sc["tile"] for sc in fl.get("foot_screws", [])})
        # a "zone" is not hardware: it marks where a foot flange stops (the stretch along the socket plate, at the floor)
        inside = [h for h in fl.get("hardware_in_floor", []) if h.get("role") != "zone"]
        ok = len(tiles) == 9 and used == tiles and not inside
        return ok, {"tiles": len(tiles), "tiles with no screw": sorted(set(tiles) - set(used)), "hardware in the floor": inside}

    def hood_bolted():
        rows = rep.get("hood_screws", [])
        bad = [] if len(rows) == 4 else [f"{len(rows)} screws, expected 4"]
        for r in rows:
            x, y, _ = r["at"]
            if r["ring"] not in RING_PIECES or r["foot"] not in FOOT_PIECES or r["ring_boss_cm3"] <= 1.0 or r["foot_boss_cm3"] <= 1.0:
                bad.append(f"the screw at {r['at']}: ring {r['ring']}, foot {r['foot']}, bosses {r['ring_boss_cm3']} and {r['foot_boss_cm3']} cm3")
            holes = [f for f in made[r["foot"]].Faces if isinstance(f.Surface, Part.Cylinder) and abs(f.Surface.Radius - oj.insert_hole_d / 2) < 1e-3
                     and abs(abs(f.Surface.Axis.z) - 1.0) < 1e-6 and math.hypot(f.Surface.Center.x - x, f.Surface.Center.y - y) < 0.05]
            if not holes:
                bad.append(f"no hole of the insert in {r['foot']} at ({x:g}, {y:g})")
        xs = sorted(round(r["at"][0], 3) for r in rows)
        if len(xs) == 4 and xs[:2] != [-xs[3], -xs[2]]:
            bad.append(f"the screws are not a mirror pair on each side: {xs}")
        short = [r for r in chk.get("hood_reach", []) if r["free"] < HOOD_KEY]
        if len(chk.get("hood_reach", [])) != 4 or short:
            bad.append(f"a key does not reach: {short}")
        return not bad, bad

    def joints_no_clash():
        more = [h for h in chk["hardware"] if h["role"] != "zone" and h["mm3"] - h["of_the_plain_piece_mm3"] > BUILD.clash_mm3]
        return not more, more

    def twins():
        twin = lambda n: n[:-2] if n.endswith((" R", " L")) else n
        cut = {twin(h["piece"]) for h in rep["hits"]}
        # the two pieces of a seam on the centre line: one has the key and the pilot holes, its twin the groove
        centre = {twin(p["head"]) for p in rep["pairs"] if twin(p["head"]) == twin(p["pilot"])}
        # a piece whose key moved off the bed (the hood centre prints on a cut face)
        moved = {twin(n) for p in rep["pairs"] if p["key"] and p["key"] != p["pilot"] for n in (p["head"], p["pilot"])}
        # the door halves are the designed halves of candybar.shell.rear, and this generator adds nothing to them
        bad = [n for n in res.added if n.startswith("door half")]
        bad += [t for t in chk["twins_that_differ"] if t["piece"] not in cut | centre | moved | {"door half"} and not t["piece"].startswith("floor")]
        return not bad, bad

    rule("piece_count", piece_count)
    rule("closing_gap", closing_gap, needs_res=True)
    rule("flange_on_both_pieces", flange_both)
    rule("screws_on_long_seams", screws_on_long_seams)
    rule("joint_7_ring_and_foot", joint_7, needs_res=True)
    rule("no_flange_in_the_rear", no_flange_in_rear)
    rule("no_key_on_the_bed", no_key_on_bed)
    rule("l1_screws_clear_of_the_cut_ins", l1_screws)
    rule("flanges_clear_of_the_door", door_zone, needs_res=True)
    rule("floor_nine_tiles_screwed", floor_tiles)
    rule("hood_bolted_four_screws", hood_bolted)
    rule("joints_add_no_clash_with_hardware", joints_no_clash)
    rule("twins_differ_only_by_hardware", twins, needs_res=True)
    return out


def summary(chk: dict, log=print) -> int:
    bad = [n for n, r in chk["pieces"].items() if not r["valid"] or r["solids"] != 1 or not r["fits"]]
    log(f"pieces: {len(chk['pieces'])} pieces, screws {chk['screws']}, not one valid solid in the limit: {bad}, clashes {len(chk['clashes'])}, "
        f"in hardware {len(chk['hardware'])}, screws out of reach {len(chk['reach_short'])}, twins that differ {chk['twins_that_differ']}, mass {chk['mass']}")
    failed = [k for k, r in chk.get("rules", {}).items() if r["ok"] is False]
    if failed:
        log(f"pieces: rules of the set that fail: {failed}")
    return 0 if chk["ok"] else 1


MERGE_DV = 0.5   # mm3: the volume of a piece may change by this much (or 1e-6 of it) when its faces are merged
# the folder of the merged copies, and the end of their file names: a copy to look at in FreeCAD, never a print file
MERGED_VIEW = "merged-view"
MERGED_SUFFIX = "-merged-view-not-for-print"


def merge_faces(shapes: dict, log=print) -> tuple[dict, list[dict]]:
    """Each piece with the faces that continue each other merged into one (removeSplitter), as a copy to look at. The
    merge of OpenCascade is not the same in each run, and a boolean on a merged piece can fail, so the merged shape is
    in no print file and no check. Returns the merged copies (none for a piece whose merge is not one valid closed
    solid of the same volume, within MERGE_DV) and a row for each piece."""
    out, rows = {}, []
    for name, shape in shapes.items():
        t0 = time.time()
        row = {"piece": name, "faces_before": len(shape.Faces)}
        try:
            # on a deep copy: the merge can change the tolerances of the sub-shapes that it shares with the piece, and a
            # piece that keeps its faces must stay as the joints left it
            m = shape.copy().removeSplitter()
            if len(m.Solids) == 1:
                m = m.Solids[0]
            dv = m.Volume - shape.Volume
            ok = m.isValid() and len(m.Solids) == 1 and m.isClosed() and abs(dv) <= max(MERGE_DV, 1e-6 * shape.Volume)
            row.update({"faces_after": len(m.Faces), "valid": bool(m.isValid()), "solids": len(m.Solids), "closed": bool(m.isClosed()),
                        "dv_mm3": round(dv, 3), "merged": bool(ok)})
            if not ok:
                row["why"] = "not one valid closed solid" if not (m.isValid() and len(m.Solids) == 1 and m.isClosed()) else f"the volume changes by {dv:.3f} mm3"
        except Exception as e:  # noqa: BLE001
            ok, m = False, shape
            row.update({"merged": False, "why": f"removeSplitter failed: {e}"})
        if ok:
            out[name] = m
        row["seconds"] = round(time.time() - t0, 1)
        rows.append(row)
        log(f"pieces: {name}: faces merged {row.get('faces_before')} -> {row.get('faces_after')}, merged {row['merged']} {row.get('why', '')}")
    return out, rows


def write_merged_view(folder: Path, shapes: dict) -> None:
    """The merged copies as BREP files only (no STL, no manifest: no tool and no slicer takes them), each named
    <piece>-merged-view-not-for-print.brep, and a README that says what they are."""
    import shutil  # noqa: PLC0415

    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    for name, shape in shapes.items():
        shape.exportBrep(str(folder / f"{name.replace(' ', '_')}{MERGED_SUFFIX}.brep"))
    (folder / "README.txt").write_text(
        "The print pieces with their merged faces, to look at in FreeCAD (File > Open, or Part > Import).\n"
        "They are not print files: print the STL files of the folder above. The merge of OpenCascade is not the same in\n"
        "each run, so no check reads these copies. A piece whose merge failed has no copy here.\n", encoding="utf-8")


def build_all(out: Path, log=print) -> int:
    d = Blueprint()
    pl = plain(d, out, log)
    items = hardware()
    res = generate(d, pl, None, None, items, log)
    write_parts(out, res.pieces)
    # the merged copies, to look at in FreeCAD only (merge_faces)
    view, res.extra["merged"] = merge_faces(res.pieces, log)
    write_merged_view(out / MERGED_VIEW, view)
    # the joints alone, for tools/face_check.py: the skin has narrow step faces of its own, which hide the joints' faces
    write_parts(out / "joints", res.added, {n: "#9ec5e8" for n in res.added})
    rep = seam_report(res)
    (out / "seams.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    # the checks are on the pieces as the files hold them
    made = read_parts(out)[0]
    chk = check_set(d, pl, made, rep, items, log)
    chk["rules"] = set_rules(d, pl, made, rep, chk, items, res, log)
    chk["ok"] = chk["ok"] and all(r["ok"] is not False for r in chk["rules"].values())
    (out / "check.json").write_text(json.dumps(chk, indent=1), encoding="utf-8")
    return summary(chk, log)


def check_rules(out: Path, log=print) -> int:
    """The rules of the set again on the files of a build (set_rules), with the rest of its check.json as it is: a
    few seconds, where check_files runs every check of the set again. The rules that need the generation stay as the
    build wrote them."""
    d = Blueprint()
    pl = plain(d, out, log)
    made, _ = read_parts(out)
    rep = json.loads((out / "seams.json").read_text(encoding="utf-8"))
    chk = json.loads((out / "check.json").read_text(encoding="utf-8"))
    built = chk.get("rules", {})
    rules = set_rules(d, pl, made, rep, chk, hardware(), None, log)
    for k, r in rules.items():
        if r["ok"] is None and k in built:
            rules[k] = {**built[k], "detail": f"as the build wrote it: {built[k]['detail']}"}
    chk["rules"] = rules
    chk["ok"] = all(r["valid"] and r["solids"] == 1 and r["fits"] for r in chk["pieces"].values()) and not chk["clashes"] \
        and not chk["reach_short"] and all(r["free"] >= HOOD_KEY for r in chk["hood_reach"]) and all(r["ok"] is not False for r in rules.values())
    (out / "check.json").write_text(json.dumps(chk, indent=1), encoding="utf-8")
    return summary(chk, log)


def check_files(out: Path, log=print) -> int:
    """The checks of the whole set again, on the BREP files and seams.json of a build folder."""
    d = Blueprint()
    pl = plain(d, out, log)
    shapes, _ = read_parts(out)
    rep = json.loads((out / "seams.json").read_text(encoding="utf-8"))
    items = hardware()
    chk = check_set(d, pl, shapes, rep, items, log)
    chk["rules"] = set_rules(d, pl, shapes, rep, chk, items, None, log)
    chk["ok"] = chk["ok"] and all(r["ok"] is not False for r in chk["rules"].values())
    (out / "check.json").write_text(json.dumps(chk, indent=1), encoding="utf-8")
    return summary(chk, log)


# ---------- the folders that the sheets are rendered from ----------

@dataclass(frozen=True)
class View:
    """A picture of some pieces: which ones, how far each is moved, and the camera (tools/render_views.py)."""
    name: str
    title: str
    pieces: tuple[str, ...]            # empty: all
    target: tuple[float, float, float]
    radius: float
    az: float
    el: float
    moved: tuple[tuple[str, tuple[float, float, float]], ...] = ()
    explode: float = 0.0               # every piece moved away from the middle of the cabinet by this share
    aspect: float = 0.75


CENTRE = (0.0, 290.0, 250.0)
VIEWS = (
    View("exploded-front", "The 30 pieces, moved apart, from the front right", (), (0.0, 290.0, 235.0), 640.0, 38.0, 22.0, explode=0.45, aspect=0.85),
    View("exploded-rear", "The 30 pieces, moved apart, from the rear left", (), (0.0, 290.0, 235.0), 640.0, -142.0, 22.0, explode=0.45, aspect=0.85),
    View("pilot-front-closed", "Pilot, front: deck side R on lower R at seam D2, closed, seen from inside", ("deck side R", "lower R"),
         (195.0, 207.0, 38.0), 85.0, -128.0, 28.0),
    View("pilot-front-open", "Pilot, front: seam D2 open by 40 mm", ("deck side R", "lower R"),
         (195.0, 187.0, 38.0), 100.0, -128.0, 28.0, moved=(("deck side R", (0.0, -40.0, 0.0)),)),
    View("pilot-rear-closed", "Pilot, rear: upper R on middle R at seam B1 in the crease of the rear shelf, closed, seen from inside",
         ("middle R", "upper R"), (225.0, 440.0, 293.0), 150.0, -75.0, 12.0),
    View("pilot-rear-open", "Pilot, rear: seam B1 open by 40 mm", ("middle R", "upper R"),
         (225.0, 440.0, 313.0), 160.0, -75.0, 12.0, moved=(("upper R", (0.0, 0.0, 40.0)),)),
    View("pilot-rear-under", "Pilot, rear: the flange of upper R at B1 from below (no gusset where the wall leaves at 45 degrees)", ("upper R",),
         (225.0, 440.0, 300.0), 150.0, -70.0, -35.0),
    View("close-l1-cut-in", "Seam L1 behind the band, under the lowest cut-in: middle R on rear lower R, open by 30 mm",
         ("middle R", "rear lower R"), (232.0, 505.0, 131.0), 75.0, -55.0, 18.0, moved=(("middle R", (0.0, 0.0, 30.0)),)),
    View("close-door-land", "The land between the door's side and the cut-ins: the flanges stop 10 mm from the door opening",
         ("middle R", "rear lower R", "upper rear R"), (222.0, 538.0, 200.0), 120.0, -22.0, 8.0),
    View("close-hand-hold", "The hand-hold in upper rear R, from inside: seams R3, R5 and B1 round it",
         ("upper rear R", "upper R"), (130.0, 560.0, 360.0), 130.0, -12.0, -8.0),
    View("close-s1-node", "Seam S1 in the crease of the band, where lower R, rear lower R and middle R meet",
         ("lower R", "rear lower R", "middle R"), (238.0, 385.0, 105.0), 95.0, -100.0, 14.0),
    View("close-floor", "The floor: the foot flange of rear lower R; the side tile lifted 35 mm and the centre tile 70 mm (rebate, half-lap, cones)",
         ("rear lower R", "floor rear side R", "floor rear centre"), (140.0, 470.0, 30.0), 175.0, -40.0, 30.0,
         moved=(("floor rear side R", (0.0, 0.0, 35.0)), ("floor rear centre", (0.0, 0.0, 70.0)))),
    View("close-floor-under", "The same two tiles from below: the rebate for the foot flange, the upper half of the lap, the sockets of the cones",
         ("floor rear side R", "floor rear centre"), (110.0, 450.0, 20.0), 170.0, -35.0, -40.0,
         moved=(("floor rear centre", (0.0, 0.0, 40.0)),)),
    View("close-apron", "The apron between the two lower pieces (P1) and the deck (D1), from behind",
         ("apron", "lower R", "deck side R"), (150.0, 215.0, 85.0), 120.0, 150.0, 22.0),
    View("close-hood", "The hood: the flange of hood side R at seam H1 (hood centre left out)", ("hood side R",), (106.0, 510.0, 500.0), 110.0, -100.0, 8.0),
    View("close-hood-centre", "The hood: the flange of hood centre at seam H1, cut back for the marquee modules", ("hood centre",),
         (106.0, 510.0, 500.0), 110.0, 80.0, 8.0),
)


def read_parts(out: Path) -> tuple[dict, dict]:
    """The finished pieces and their tints, from the BREP files of a build folder."""
    import Part  # noqa: PLC0415

    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    shapes, tint = {}, {}
    for stem, m in manifest.items():
        s = Part.Shape()
        s.read(str(out / m["brep"]))
        shapes[stem.replace("_", " ")] = s
        tint[stem.replace("_", " ")] = m["finish"]
    return shapes, tint


def section_of_a_joint(out: Path, shapes: dict) -> None:
    """The section through the first screw of each pilot seam, square to the seam: polygons in (u, z), u inward
    along the flange and z across the seam, for tools/draw_pieces.py."""
    import FreeCAD as App  # noqa: PLC0415

    rep = json.loads((out / "seams.json").read_text(encoding="utf-8"))
    done = {}
    for seam, _ in PILOT:
        pair = next((p for p in rep["pairs"] if p["seam"] == seam and p["screws"]), None)
        if pair is None:
            continue
        sc = pair["screws"][len(pair["screws"]) // 2]
        at, t, n = App.Vector(*sc["at"]), App.Vector(*sc["along"]), App.Vector(*pair["normal"])
        polys = {}
        for name in (pair["head"], pair["pilot"]):
            rows = []
            for w in shapes[name].slice(t, at.dot(t)):
                pts = [p - at for p in w.discretize(Distance=0.25)]
                if min(p.Length for p in pts) > 45.0:
                    continue
                rows.append([[round(p.dot(n.cross(t)), 3), round(p.dot(n), 3)] for p in pts])
            polys[name] = rows
        done[seam] = {"head": pair["head"], "pilot": pair["pilot"], "polys": polys}
    (out / "views").mkdir(exist_ok=True)
    (out / "views" / "section.json").write_text(json.dumps(done), encoding="utf-8")


def views(out: Path, log=print) -> int:
    """Write a folder for each picture under out/views: the meshes and the edges of its pieces, moved as the view
    asks, and the camera. tools/draw_pieces.py renders them."""
    import numpy as np  # noqa: PLC0415

    shapes, tint = read_parts(out)
    for v in VIEWS:
        names = [n for n in (v.pieces or tuple(shapes)) if n in shapes]
        moved = dict(v.moved)
        if v.explode:
            for n in names:
                _, lo, hi = tight_box(shapes[n])
                c = (lo + hi) / 2 - np.array(CENTRE)
                shift = c * v.explode
                if n.startswith("floor"):
                    shift[2] -= 60.0
                moved[n] = tuple(float(x) for x in shift)
        folder = out / "views" / v.name
        write_parts(folder, {n: shapes[n] for n in names}, tint, moved)
        (folder / "focus.json").write_text(json.dumps({v.name: {"target": list(v.target), "radius": v.radius, "az": v.az, "el": v.el,
                                                                 "aspect": v.aspect}}), encoding="utf-8")
        (folder / "title.txt").write_text(v.title, encoding="utf-8")
        log(f"pieces: view {v.name}: {len(names)} pieces")
    section_of_a_joint(out, shapes)
    return 0


def main() -> int:
    out = Path(os.environ.get("CANDYBAR_OUT", "cad/out/pieces"))
    what = os.environ.get("CANDYBAR_PIECES", "all")
    if what == "pilot":
        return pilot(out)
    if what == "views":
        return views(out)
    if what == "check":
        return check_files(out)
    if what == "rules":
        return check_rules(out)
    return build_all(out)
