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
A finding that lies inside a named reveal of ALLOW (a seam groove, the bezel reveal) is listed as allowed.

Run headless on a directory of BREP files with manifest.json (as candybar.shell.solids writes it); it writes
face-check.json and face-check.md there and exits 1 when a finding is not allowed:

    CANDYBAR_OUT=cad/out/shell-bp-rev6 cad/candybar/freecad-run.sh tools.face_check
    CANDYBAR_FACE_PARTS=rear_body,hood ...   (only these parts)
"""
from __future__ import annotations

import json
import math
import os
from collections.abc import Callable
from dataclasses import asdict, dataclass, field

import Part

MIN_WIDTH = 2.0
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


def reveals(body_top: float, seam_gap: float, groove: float, bezel: tuple[float, float, float, float, float, float] | None = None,
            panel: tuple[float, float, float, float, float, float] | None = None) -> list[Reveal]:
    """The named reveals of the shell: the seam groove (its bevel faces on the body and the hood, which are as narrow as
    the groove where the outline turns), the reveal round the bezel plate (panel_gap wide) and the pocket of the
    control panel (its walls are deck_top - panel_top high)."""
    out = [Reveal("seam groove", ("front_body", "rear_body", "body", "hood"), ("sliver", "needle", "crowded"),
                  (-1e4, -1e4, body_top - groove - 0.5, 1e4, 1e4, body_top + seam_gap + groove + 0.5))]
    if bezel:
        out.append(Reveal("bezel reveal", ("front_body", "body", "bezel"), ("sliver", "needle", "crowded"), bezel))
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


def run_dir(out: str, parts: list[str] | None = None, allow: list[Reveal] | None = None) -> list[Finding]:
    manifest = json.load(open(os.path.join(out, "manifest.json")))
    if allow is None:
        allow = default_reveals()
    found: list[Finding] = []
    for name, entry in manifest.items():
        if parts and name not in parts:
            continue
        s = Part.Shape()
        s.read(os.path.join(out, entry["brep"]))
        found += check(s, name, allow)
    return found


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
    return reveals(d.body_top, d.seam_gap, d.seam_groove, bezel, panel)


def main() -> int:
    out = os.environ.get("CANDYBAR_OUT", "cad/out/shell-bp")
    parts = [p for p in os.environ.get("CANDYBAR_FACE_PARTS", "").split(",") if p] or None
    found = run_dir(out, parts)
    json.dump({"summary": summary(found), "findings": [asdict(f) for f in found]}, open(os.path.join(out, "face-check.json"), "w"), indent=1)
    open(os.path.join(out, "face-check.md"), "w").write(report_md(found, out))
    for part, row in summary(found).items():
        print(f"{part:14s} " + "  ".join(f"{r} {row[r]}" for r in (*RULES, "allowed", *INFO)))
    return 1 if failures(found) else 0


def failures(found: list[Finding]) -> list[Finding]:
    """The findings that fail: not allowed, and not for information."""
    return [f for f in found if not f.allowed and f.rule not in INFO]
