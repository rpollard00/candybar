"""Face check: find the faces that make a form look wrong when the face edges are drawn (as the FreeCAD GUI draws them).

It reads solids and reports, for each part:
  sliver     a face narrower than MIN_WIDTH: the width of the rectangle with the face's area and perimeter (seam edges
             of closed surfaces do not count in the perimeter)
  needle     a corner of a face where its two edges meet at less than NEEDLE_DEG: the face tapers to a point there
  crowded    a vertex where more than MAX_EDGES edges meet
  kink       two faces that meet at a small angle (KINK_DEG): a round that is not tangent to its faces, flat facets in
             place of a round, or pieces of a round that do not join smoothly. A crease of CREASE_DEG is listed as a
             shallow crease for information (a deliberate turn of the form, as the 10 degree band of the deck) and does
             not fail
  split      two faces that meet with the same normal and the same curvature on their common edge: one surface cut
             into strips, which the GUI draws as a stack of lines (unmerged faces, rounds made of stacked lofts)
A finding is listed as allowed, and does not fail, in three cases only:
  reveal       it lies inside a named reveal (a seam groove, the bezel reveal, the panel pocket): these are as narrow
               as the reveal is by design
  edge break   it is a narrow face that is a round of the edge break's radius along an edge (the last modelling step
               of the shell puts one on every sharp convex edge). The ball at a corner where three broken edges meet
               is not a round along an edge, and is not allowed by this: it must lie in a named reveal or be a
               known item
  known item   it is one of KNOWN: the findings of the shell that stay, each with its part, its rule, its place, its
               size and the reason. A known item holds for the right side and for its mirror image on the left.
               It is one list, and no entry allows a whole part or a whole rule.

Run headless on a directory of BREP files with manifest.json (as candybar.shell.solids writes it); it writes
face-check.json and face-check.md there and exits 1 when a finding is not allowed, or when a known item has no
finding any more:

    CANDYBAR_OUT=cad/out/shell-rev7 cad/candybar/freecad-run.sh tools.face_check
    CANDYBAR_FACE_PARTS=body,hood ...   (only these parts)
"""
from __future__ import annotations

import json
import math
import os
from collections.abc import Callable
from dataclasses import asdict, dataclass, field

import FreeCAD
import Part

V = FreeCAD.Vector
MIN_WIDTH = 2.0
SMALL_BREAKS = (0.5, 0.3)   # the breaks on a small feature or a tight place, where the edge break does not fit (docs/adr/0007)
NEEDLE_DEG = 12.0
MAX_EDGES = 4
KINK_DEG = (1.0, 4.5)
CREASE_DEG = (4.5, 20.0)
SPLIT_DEG = 0.5
SPLIT_CURVATURE = 0.03
SAMPLES = (0.2, 0.5, 0.8)
RULES = ("sliver", "needle", "crowded", "kink", "split")
INFO = ("crease",)


@dataclass(frozen=True)
class Reveal:
    """A named reveal: findings of these rules on these parts inside the box are allowed."""
    name: str
    parts: tuple[str, ...]
    rules: tuple[str, ...]
    box: tuple[float, float, float, float, float, float]

    def holds(self, part: str, rule: str, at: tuple[float, float, float]) -> bool:
        x0, y0, z0, x1, y1, z1 = self.box
        return part in self.parts and rule in self.rules and x0 <= at[0] <= x1 and y0 <= at[1] <= y1 and z0 <= at[2] <= z1


@dataclass
class Finding:
    part: str
    rule: str
    at: tuple[float, float, float]
    detail: str
    faces: list[int] = field(default_factory=list)
    allowed: str = ""


@dataclass(frozen=True)
class Known:
    """A finding of the shell that stays: the part and the rule, its place on the right side (x >= 0; the same item
    on the left is its mirror image), its size, and the reason. A finding of that part and rule within `within` of
    the place is this item."""
    part: str
    rule: str
    at: tuple[float, float, float]
    size: str
    reason: str
    within: float = 1.5

    def holds(self, f: Finding) -> bool:
        return f.part == self.part and f.rule == self.rule and math.dist((abs(f.at[0]), f.at[1], f.at[2]), self.at) <= self.within


# the known items of the default build (candybar.shell.solids, revision 7). Places in the cabinet frame, mm
HIP_TOP = ("top of the hip: OpenCascade's patch where the round of the hip (made by hand) meets the rounds of the band's level run and "
           "of the head's lower edge. Three rounds of R 3 meet at this corner; the exact corner is a part of a sphere about 1.0 wide")
HEAD_FOOT = ("foot of the head's rear corner: OpenCascade's patch where the rounds of the head's corner, of the head's lower edge and of "
             "the lower edge of the upper rear wall meet (three rounds of R 3 at one corner)")
RAIL = ("rail: the cut of the edge section stands 0.01 proud of the rail land (solids.OFF_LAND), so that it does not lie on the "
        "land's tangent, and its radius meets the land at 2.5 degrees. Older than revision 7; a smaller value makes the cut fail")
RUN_OUT = ("hood: the round of the rear corner runs out on the roof, where the side and the rear turn tangent to each other")
KINK = ("hood: the wall of the front opening has a concave kink of 11.5 degrees at each lower corner, where the round of the sill "
        "corner ends upright and the leg starts with its lean (the form of R10). The ball of the edge break turns about that "
        "kink between the break along the corner and the break along the leg")
LATCH = ("deck: the edge break by hand on the rim of the latch button's hole (solids.deck): at each corner, where a flat of the "
         "hole meets its round (round in plan, solids.LATCH_CORNER), the lofts of the break meet in a narrow patch, and the face of "
         "the break is split at the top and the bottom of the hole")

KNOWN: tuple[Known, ...] = (
    Known("body", "sliver", (246.8, 549.8, 305.0), "1.20 wide, 4.2 mm2", HIP_TOP, within=0.5),
    Known("body", "sliver", (246.3, 550.7, 304.9), "0.43 wide, 2.0 mm2", HIP_TOP, within=0.5),
    Known("body", "split", (246.8, 550.4, 305.0), "the two patches continue each other along 3.7", HIP_TOP, within=0.5),
    Known("body", "sliver", (245.2, 579.1, 333.4), "1.69 wide, 7.2 mm2", HEAD_FOOT, within=0.8),
    Known("body", "kink", (234.8, 234.9, 80.5), "2.5 degrees along 59.3, round the sweep", RAIL),
    Known("body", "kink", (234.8, 297.6, 200.9), "2.5 degrees along 214.5, below the tuck", RAIL),
    Known("body", "kink", (232.6, 390.2, 357.5), "2.5 degrees along 153.9, in the tuck", RAIL),
    Known("body", "kink", (223.9, 438.2, 422.4), "2.2 degrees along 4.2, in the seam bevel", RAIL),
    Known("deck", "sliver", (6.7, 0.9, 51.6), "0.46 wide, 0.7 mm2: the patch at the lower corner of the hole", LATCH, within=1.0),
    Known("deck", "sliver", (6.7, 2.3, 59.2), "0.45 wide, 0.8 mm2: the patch at the upper corner of the hole", LATCH, within=1.0),
    Known("deck", "split", (0.0, 3.0, 62.9), "the face of the break at the top of the hole, split on the centre line, 1.6 long", LATCH, within=1.0),
    Known("deck", "split", (0.0, 0.4, 47.9), "the face of the break at the bottom of the hole, split on the centre line, 1.0 long", LATCH, within=1.0),
    Known("hood", "sliver", (181.3, 522.6, 572.9), "0.77 wide, 6.4 mm2: the last face of the round, 1.6 wide where it starts, 10 long", RUN_OUT, within=1.0),
    Known("hood", "needle", (176.5, 520.0, 573.4), "the tip of that face: its two edges meet at 10.7 degrees", RUN_OUT, within=1.0),
    Known("hood", "sliver", (210.5, 447.0, 448.6), "0.08 wide, 0.13 mm2: the face of the break in that turn, 0.21 wide on the front "
          "and 0.06 on the wall, 1.6 long", KINK, within=0.5),
    Known("hood", "needle", (209.9, 447.8, 448.4), "the wall of the leg beside that face: the kink and the edge of the face meet at "
          "3.8 degrees, along 0.05", KINK, within=0.5),
)
# the parts of the build that are not printed parts: the lit image is a plate of 1 mm for the renders
NOT_PARTS = ("screen",)


def reveals(body_top: float, seam_gap: float, groove: float, bezel: tuple[float, float, float, float, float, float] | None = None,
            panel: tuple[float, float, float, float, float, float] | None = None) -> list[Reveal]:
    """The named reveals of the shell: the seam groove (its bevel faces on the body and the hood, which are as narrow as
    the groove where the outline turns), the reveal round the bezel plate (panel_gap wide) and the pocket of the
    control panel (its walls are deck_top - panel_top high)."""
    out = [Reveal("seam groove", ("body", "hood"), ("sliver", "needle", "crowded"),
                  (-1e4, -1e4, body_top - groove - 0.5, 1e4, 1e4, body_top + seam_gap + groove + 0.5))]
    if bezel:
        out.append(Reveal("bezel reveal", ("body", "bezel"), ("sliver", "needle", "crowded"), bezel))
    if panel:
        out.append(Reveal("panel pocket", ("deck",), ("sliver",), panel))
    return out


def _r(v) -> tuple[float, float, float]:
    return (round(v.x, 1), round(v.y, 1), round(v.z, 1))


def width(face: Part.Face) -> float:
    """The width of the rectangle with the face's area and perimeter; a seam edge is not a boundary."""
    perimeter = 0.0
    for w in face.Wires:
        edges = w.Edges
        for e in edges:
            if e.Degenerated:
                continue
            if sum(1 for o in edges if o.isSame(e)) > 1:
                continue
            perimeter += e.Length
    a = face.Area
    return (perimeter - math.sqrt(max(perimeter * perimeter - 16 * a, 0.0))) / 4


def away(e: Part.Edge, v) -> list:
    """The unit tangents of an edge that point away from a vertex, one for each end of the edge on that vertex."""
    out = []
    p0, p1 = e.valueAt(e.FirstParameter), e.valueAt(e.LastParameter)
    tol = max(1e-4, 2 * v.Tolerance)
    if (p0 - v.Point).Length < tol:
        t = e.tangentAt(e.FirstParameter)
        out.append(t.normalize() if t.Length else t)
    if (p1 - v.Point).Length < tol:
        t = e.tangentAt(e.LastParameter)
        out.append((-t).normalize() if t.Length else t)
    return out


def angle(a, b) -> float:
    c = max(-1.0, min(1.0, a.dot(b) / (a.Length * b.Length))) if a.Length and b.Length else 1.0
    return math.degrees(math.acos(c))


def corners(face: Part.Face) -> list[tuple[float, object]]:
    """Each vertex of the face with the smallest angle between two different edges of the face that meet there."""
    out = []
    edges = [e for e in face.Edges if not e.Degenerated]
    for v in face.Vertexes:
        dirs = []
        for k, e in enumerate(edges):
            for t in away(e, v):
                dirs.append((k, t))
        best = 180.0
        for i in range(len(dirs)):
            for j in range(i + 1, len(dirs)):
                if dirs[i][0] == dirs[j][0] or edges[dirs[i][0]].isSame(edges[dirs[j][0]]):
                    continue
                best = min(best, angle(dirs[i][1], dirs[j][1]))
        if dirs:
            out.append((best, v))
    return out


def normal_and_curvature(face: Part.Face, p):
    u, v = face.Surface.parameter(p)
    n = face.normalAt(u, v)
    try:
        k = sorted(abs(c) for c in face.curvatureAt(u, v))
    except Part.OCCError:
        k = None
    return n, k


def is_break(face: Part.Face, radius: float, tol: float = 0.02) -> bool:
    """Whether a face is an edge break: a round of `radius` along an edge (its tighter principal radius is `radius`
    all over and the other one is more than 1.5 times larger, which leaves out a ball-like patch at a vertex; a break
    along an edge that bends round a small corner keeps a short other radius, down to about 1.8 for R 1)."""
    if isinstance(face.Surface, Part.Plane):
        return False
    u0, u1, v0, v1 = face.ParameterRange
    for su, sv in ((0.5, 0.5), (0.2, 0.5), (0.8, 0.5), (0.5, 0.2), (0.5, 0.8)):
        try:
            k = sorted(abs(c) for c in face.curvatureAt(u0 + (u1 - u0) * su, v0 + (v1 - v0) * sv))
        except Exception:
            return False
        if abs(k[1] - 1.0 / radius) > tol / radius ** 2 or k[0] > 1.0 / (1.5 * radius):
            return False
    return True


def is_break_surface(face: Part.Face, radius: float, tol: float = 0.02) -> bool:
    """Whether a face is a part of the edge break: one of its two principal radii is `radius` all over. That is a
    round along an edge (is_break), the ball at a corner where three broken edges meet, and the face on which the
    ball turns about a kink in a wall. compare_parts counts a distance at such a face as a distance at the edge
    break. The face check does not allow a narrow face by this: only a round along an edge is allowed there."""
    if isinstance(face.Surface, Part.Plane):
        return False
    u0, u1, v0, v1 = face.ParameterRange
    for su, sv in ((0.5, 0.5), (0.2, 0.5), (0.8, 0.5), (0.5, 0.2), (0.5, 0.8)):
        try:
            k = [abs(c) for c in face.curvatureAt(u0 + (u1 - u0) * su, v0 + (v1 - v0) * sv)]
        except Exception:
            return False
        if min(abs(c - 1.0 / radius) for c in k) > tol / radius ** 2:
            return False
    return True


def behind_break(shape: Part.Shape, f: Part.Face, radius: float) -> bool:
    """Whether a narrow face is the wall of a thin plate behind an edge break: it runs on, tangent, from a face of the
    break (is_break, of the edge break or of a small break, SMALL_BREAKS) along one of its long edges. A plate of 2.4 with a break of R 1 on its front keeps a wall of 1.4
    round each opening and at its rim."""
    if width(f) < 0.5:
        return False
    half = sum(e.Length for e in f.Edges) / 2
    for e in f.Edges:
        if e.Degenerated or e.Length < 0.4 * half:
            continue
        m = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
        for g in shape.ancestorsOfType(e, Part.Face):
            if g.isSame(f) or not (is_break(g, radius) or any(is_break(g, b) for b in SMALL_BREAKS)):
                continue
            na, nb = (x.normalAt(*x.Surface.parameter(m)) for x in (f, g))
            if math.degrees(math.acos(max(-1.0, min(1.0, abs(na.dot(nb)))))) < 1.0:   # tangent
                return True
    return False


def check(shape: Part.Shape, part: str = "", allow: list[Reveal] = (), break_radius: float = 0.0) -> list[Finding]:
    """The findings of the five rules on one solid. break_radius: a narrow face that is a round of that radius along an
    edge is listed as allowed ("edge break"); nothing else is."""
    found: list[Finding] = []
    faces = shape.Faces
    index = {f.hashCode(): i for i, f in enumerate(faces)}

    def add(rule: str, at, detail: str, fs: list[int]) -> None:
        a = _r(at)
        why = next((r.name for r in allow if r.holds(part, rule, a)), "")
        found.append(Finding(part, rule, a, detail, fs, why))

    for i, f in enumerate(faces):
        w = width(f)
        if w < MIN_WIDTH:
            add("sliver", f.CenterOfMass, f"{type(f.Surface).__name__} {w:.2f} wide, area {f.Area:.1f} mm2", [i + 1])
            if break_radius and is_break(f, break_radius):
                found[-1].allowed = "edge break"
            elif break_radius and any(is_break(f, b) for b in SMALL_BREAKS):
                found[-1].allowed = "small break"
            elif break_radius and behind_break(shape, f, break_radius):
                found[-1].allowed = "the wall of a thin plate behind its edge break"
        for a, v in corners(f):
            if a < NEEDLE_DEG:
                add("needle", v.Point, f"{type(f.Surface).__name__}: two edges meet at {a:.1f} deg", [i + 1])
    for v in shape.Vertexes:
        n = len([e for e in shape.ancestorsOfType(v, Part.Edge) if not e.Degenerated])
        if n > MAX_EDGES:
            add("crowded", v.Point, f"{n} edges meet", [])
    for e in shape.Edges:
        if e.Degenerated:
            continue
        adj = shape.ancestorsOfType(e, Part.Face)
        if len(adj) != 2 or adj[0].isSame(adj[1]):
            continue
        fa, fb = adj
        worst, same = 0.0, True
        for s in SAMPLES:
            p = e.valueAt(e.FirstParameter + s * (e.LastParameter - e.FirstParameter))
            na, ka = normal_and_curvature(fa, p)
            nb, kb = normal_and_curvature(fb, p)
            worst = max(worst, angle(na, nb))
            if ka is None or kb is None or any(abs(x - y) > SPLIT_CURVATURE * max(abs(x), abs(y), 1e-3) + 1e-4 for x, y in zip(ka, kb)):
                same = False
        ids = [index.get(fa.hashCode(), -2) + 1, index.get(fb.hashCode(), -2) + 1]
        mid = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
        if KINK_DEG[0] <= worst < KINK_DEG[1]:
            add("kink", mid, f"faces meet at {worst:.1f} deg along {e.Length:.1f}", ids)
        elif CREASE_DEG[0] <= worst < CREASE_DEG[1]:
            add("crease", mid, f"shallow crease of {worst:.1f} deg along {e.Length:.1f}", ids)
        elif worst < SPLIT_DEG and same:
            add("split", mid, f"{type(fa.Surface).__name__} / {type(fb.Surface).__name__} continue each other along {e.Length:.1f}", ids)
    return found


def summary(found: list[Finding]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for f in found:
        row = out.setdefault(f.part, {r: 0 for r in (*RULES, *INFO)} | {"allowed": 0})
        if f.allowed:
            row["allowed"] += 1
        else:
            row[f.rule] += 1
    return out


def report_md(found: list[Finding], title: str) -> str:
    lines = [f"# Face check: {title}", "",
             f"Rules: sliver (narrower than {MIN_WIDTH}), needle (edges meet at less than {NEEDLE_DEG} deg), crowded (more than "
             f"{MAX_EDGES} edges at a vertex), kink ({KINK_DEG[0]} to {KINK_DEG[1]} deg between faces), split (one surface cut into faces).", "",
             "| Part | sliver | needle | crowded | kink | split | allowed | shallow creases (information) |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for part, row in summary(found).items():
        lines.append(f"| {part} | " + " | ".join(str(row[r]) for r in (*RULES, "allowed", *INFO)) + " |")
    lines += ["", "| Part | Rule | At (x, y, z) | Faces | Detail | Allowed as |", "| --- | --- | --- | --- | --- | --- |"]
    for f in found:
        lines.append(f"| {f.part} | {f.rule} | {f.at[0]:.1f}, {f.at[1]:.1f}, {f.at[2]:.1f} | {', '.join(map(str, f.faces))} | {f.detail} | {f.allowed} |")
    return "\n".join(lines) + "\n"


def mark_known(found: list[Finding], known: tuple[Known, ...] = ()) -> list[Known]:
    """Mark the findings that are known items as allowed, and return the known items that have no finding (a list
    that names what is no longer there is not honest)."""
    known = known or KNOWN
    seen = set()
    for f in found:
        if f.allowed or f.rule in INFO:
            continue
        for k in known:
            if k.holds(f):
                f.allowed = f"known item: {k.reason}"
                seen.add(k)
                break
    return [k for k in known if k not in seen]




def check_shell(shapes: dict[str, Part.Shape], parts: list[str] | None = None, meta: dict | None = None) -> tuple[list[Finding], list[Known]]:
    """The face check of the parts of the shell: the findings, with the reveals, the edge breaks and the known items
    marked as allowed; and the known items that have no finding. `meta` is the manifest of the folder. Besides the
    reveals and the known items:
      - a finding on a print piece, or on a coupon cut from the real skin, that is not on the outside of the shell
        (none of its faces is on the outside of the default build's form: edge_finish.face_on_skin) does not show: the steps of the cavity, a flange, a key, a
        seam face, the cut face of a coupon
      - the findings on a printed part inside the shell and on a test print are listed and do not fail (the face check
        is for the look of the cabinet)
      - a bought part and a place are not checked"""
    from candybar.shell.dims import Blueprint
    from tools import edge_finish as ef
    meta = meta or {}
    allow = default_reveals() + band_reveals(shapes)
    found: list[Finding] = []
    for name, shape in shapes.items():
        cls = ef.finish_class(name, meta.get(name))
        if name in NOT_PARTS or cls in ("bought", "a place") or (parts and name not in parts):
            continue
        found += check(shape, name, allow, break_radius=Blueprint().edge_break)
    stale = mark_known(found)
    # the known items of the printed parts of the monitor cradle: candybar.shell.cradle.face_known gives the reason
    from candybar.shell import cradle as cr
    for f in found:
        if not f.allowed and f.rule not in INFO and f.part in cr.HALVES + cr.INSIDE + cr.PRINTED:
            f.allowed = cr.face_known(Blueprint(), f.part, f.rule, f.at, f.detail) and "known item: " + cr.face_known(Blueprint(), f.part, f.rule, f.at, f.detail)
    for f in found:
        if f.allowed or f.rule in INFO:
            continue
        entry = meta.get(f.part, {})
        cls = ef.finish_class(f.part, entry)
        if cls in ("inside, not painted", "a test print"):
            f.allowed = f"listed: a finding on {'an inside part' if cls.startswith('inside') else 'a test print'}; not a fault of the look"
            continue
        if f.part in ef.WALLS or "to_cabinet" in entry:
            back = V(*entry.get("to_cabinet", (0.0, 0.0, 0.0)))
            if not any(ef.face_on_skin(x, back) for x in faces_of(shapes[f.part], f)):
                f.allowed = "not on the outside of the shell: a face of the cavity, a flange, a seam or the cut face of a coupon"
            elif "coupon" in entry and on_cut(V(*f.at) + back, entry["coupon"]):
                f.allowed = "on the cut face of a coupon: a face of the test piece, not of the cabinet"
    # a known item of a part that is not in this set has nothing to be found in
    return found, [k for k in stale if k.part in shapes and (not parts or k.part in parts)]


def faces_of(shape: Part.Shape, f: Finding) -> list[Part.Face]:
    """The faces of a finding: those it names, or for a crowded vertex the faces that meet there."""
    if f.faces:
        return [shape.Faces[i - 1] for i in f.faces]
    p, out = V(*f.at), []
    for x in shape.Faces:   # the place of a finding is rounded to 0.1
        bb = FreeCAD.BoundBox(x.BoundBox)
        bb.enlarge(0.1)
        if bb.isInside(p) and x.distToShape(Part.Vertex(p))[0] < 0.1:
            out.append(x)
    return out


def on_cut(p, coupon: str, tol: float = 0.05) -> bool:
    """Whether a point of the cabinet lies on a face of the box that cut a coupon from the real skin."""
    from candybar.shell import coupons as cp
    x0, x1, y0, y1, z0, z1 = cp.CUT_BOXES[coupon]
    near = lambda v, a, b: a - tol <= v <= b + tol
    on = lambda v, a, b: abs(v - a) < tol or abs(v - b) < tol
    return near(p.x, x0, x1) and near(p.y, y0, y1) and near(p.z, z0, z1) and (on(p.x, x0, x1) or on(p.y, y0, y1) or on(p.z, z0, z1))


def band_reveals(shapes: dict[str, Part.Shape]) -> list[Reveal]:
    """The reveal of the marquee front of the hood band (hood_band.py): the lap of the two halves. The step of the
    lap lies in the joint, 1.1 wide, 6 each side of the centre line."""
    halves = {k: shapes[k] for k in ("marquee_front_right", "marquee_front_left") if k in shapes}
    if not halves:
        return []
    bb = FreeCAD.BoundBox()
    for s in halves.values():
        bb.add(s.BoundBox)
    out = []
    if len(halves) == 2:
        out.append(Reveal("lap of the two halves of the marquee front", tuple(halves), ("sliver",),
                          (-6.0, bb.YMin - 0.5, bb.ZMin - 0.5, 6.0, bb.YMax + 0.5, bb.ZMax + 0.5)))
    return out


def run_dir(out: str, parts: list[str] | None = None) -> tuple[list[Finding], list[Known]]:
    manifest = json.load(open(os.path.join(out, "manifest.json")))
    shapes = {}
    for name, entry in manifest.items():
        s = Part.Shape()
        s.read(os.path.join(out, entry["brep"]))
        shapes[name] = s
    return check_shell(shapes, parts, manifest)


def default_reveals() -> list[Reveal]:
    from candybar.shell.dims import Blueprint
    from candybar.shell import profiles as pr
    d = Blueprint()
    fr = pr.front(d)
    xb = d.bezel_w / 2 + d.panel_gap
    s0, s1 = d.face(d.bezel_s0), d.face(d.bezel_s1)
    bezel = (-xb - 1, s0[0] - 30, s0[1] - 30, xb + 1, s1[0] + 30, s1[1] + 30)
    del fr
    panel = (-d.width / 2, 0.0, d.panel_top - d.panel_t - 0.5, d.width / 2, d.foot_y, d.deck_top + 0.5)
    # the reveals of the printed parts of the work packages: the corner balls of the control panel's plates
    from candybar.shell import panel_frame as pf
    tiles = tuple(k for k in pf.PARTS if pf.kind(k) == "tile")
    # and the socket openings and the back pockets of the front socket plate
    from candybar.shell import socket_plate as spm
    return (reveals(d.body_top, d.seam_gap, d.seam_groove, bezel, panel) + pf.corner_balls(d, pf.Interface(), tiles)
            + [spm.face_reveal(spm.SocketPlate(), d)])


def known_md(stale: list[Known]) -> str:
    lines = ["", "## Known items", "", "Each holds for the right side and for its mirror image on the left.", "",
             "| Part | Rule | At (x, y, z) | Size | Reason | Found |", "| --- | --- | --- | --- | --- | --- |"]
    for k in KNOWN:
        lines.append(f"| {k.part} | {k.rule} | {k.at[0]:.1f}, {k.at[1]:.1f}, {k.at[2]:.1f} | {k.size} | {k.reason} | {'NO' if k in stale else 'yes'} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    out = os.environ.get("CANDYBAR_OUT", "cad/out/shell-rev7")
    parts = [p for p in os.environ.get("CANDYBAR_FACE_PARTS", "").split(",") if p] or None
    found, stale = run_dir(out, parts)
    json.dump({"summary": summary(found), "findings": [asdict(f) for f in found], "known": [asdict(k) for k in KNOWN],
               "known_without_finding": [asdict(k) for k in stale]}, open(os.path.join(out, "face-check.json"), "w"), indent=1)
    open(os.path.join(out, "face-check.md"), "w").write(report_md(found, out) + known_md(stale))
    for part, row in summary(found).items():
        print(f"{part:14s} " + "  ".join(f"{r} {row[r]}" for r in (*RULES, "allowed", *INFO)))
    for f in failures(found):
        print(f"FAIL {f.part} {f.rule} at {f.at}: {f.detail}")
    for k in stale:
        print(f"known item without a finding: {k.part} {k.rule} at {k.at}")
    return 1 if failures(found) or stale else 0


def failures(found: list[Finding]) -> list[Finding]:
    """The findings that fail: not allowed, and not for information."""
    return [f for f in found if not f.allowed and f.rule not in INFO]
