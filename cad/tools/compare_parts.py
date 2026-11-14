"""Compare the parts of two builds of the shell: volume, bounding box, and the distance between the two surfaces.

Each build is a directory with manifest.json and one BREP file for each part (as candybar.shell.solids writes it).
For each part that both builds have, the tool gives:
  volume       of each build, and the difference
  box          the largest difference between the six limits of the two bounding boxes
  distance     the largest distance from a point on the surface of one build to the surface of the other, in both
               directions. The points are the corners of a mesh of each face (not coarser than MESH) and points along
               each edge, STEP apart. The distance is to the exact surface of the other build, not to a mesh.
A part in one build can stand for several parts in the other: PAIR=body:front_body+rear_body compares the part body of
the first build with the fuse of the two parts of the second.

The edge break is counted on its own. One build can have the edge break (a round of 1 mm, the last modelling step)
on an edge that is sharp in the other. There the two surfaces are (sqrt(2) - 1) x 1 = 0.41 mm apart at an edge of 90
degrees: the size of the break, not a difference of the form. A point that lies on a face of the edge break, or
whose nearest face in the other build is one, goes into the columns "at the edge break"; the tolerance is for all
other points.

Run headless. It writes compare.json and compare.md into CANDYBAR_OUT and exits 1 when a distance is more than
CANDYBAR_TOL (default 0.3) or a part of the first build has no partner:

    CANDYBAR_A=cad/out/shell-rev7 CANDYBAR_B=cad/out/shell-bp-rev7/R10 CANDYBAR_OUT=cad/out/shell-rev7/compare \\
        cad/candybar/freecad-run.sh tools.compare_parts
    CANDYBAR_PARTS=hood,deck ...   (only these parts of the first build)
"""
from __future__ import annotations

import json
import math
import os

import FreeCAD
import Part

from tools import face_check

V = FreeCAD.Vector
MESH = 1.0
STEP = 0.5
NEAR = 1.0
TIE = 1e-6
SURE = 1e-4


def load(folder: str) -> dict[str, Part.Shape]:
    manifest = json.load(open(os.path.join(folder, "manifest.json")))
    out = {}
    for name, entry in manifest.items():
        s = Part.Shape()
        s.read(entry["brep"] if os.path.isabs(entry["brep"]) else os.path.join(folder, entry["brep"]))
        out[name] = s
    return out


def surface_points(shape: Part.Shape, radius: float, mesh: float = MESH, step: float = STEP) -> list[tuple[FreeCAD.Vector, bool]]:
    """Points on the surface of a shape: the corners of a mesh of each face, and points along each edge; each with
    whether it lies on a face of the edge break (or on an edge of one)."""
    broken = {f.hashCode() for f in shape.Faces if face_check.is_break(f, radius)}
    out = []
    for f in shape.Faces:
        out += [(p, f.hashCode() in broken) for p in f.tessellate(mesh)[0]]
    for e in shape.Edges:
        if e.Degenerated or e.Length < 1e-6:
            continue
        on_break = any(f.hashCode() in broken for f in shape.ancestorsOfType(e, Part.Face))
        out += [(p, on_break) for p in e.discretize(Number=max(3, math.ceil(e.Length / step) + 1))]
    return out


def face_distance(f: Part.Face, p: FreeCAD.Vector, v: Part.Vertex) -> float:
    """The distance from a point to a face. OpenCascade's distance can miss the nearest point of a spline face (it
    gives 2 to 3 mm for points that lie on the leaning soft edge of the hood); when it gives more than SURE, the
    point is also projected on the face's surface, and that distance counts when the foot lies inside the face."""
    dist = f.distToShape(v)[0]
    if dist > SURE and not isinstance(f.Surface, Part.Plane):
        try:
            u, w = f.Surface.parameter(p)
            if f.isPartOfDomain(u, w):
                dist = min(dist, (f.Surface.value(u, w) - p).Length)
        except (Part.OCCError, RuntimeError):
            pass
    return dist


class Surface:
    """The faces of a shape, with their boxes, for the distance from a point to the nearest face."""

    def __init__(self, shape: Part.Shape, radius: float) -> None:
        self.faces = [(f, f.BoundBox, face_check.is_break(f, radius)) for f in shape.Faces]

    def distance(self, p: FreeCAD.Vector, near: float = NEAR) -> tuple[float, bool]:
        """The distance from p to the nearest face, and whether that face is one of the edge break. The faces whose
        box is within `near` of p are measured first; when none is nearer than `near`, all faces are measured. When
        the nearest point lies on an edge between a face of the edge break and another face, the two faces are at
        the same distance (within TIE): the point then counts as nearest to the edge break."""
        v = Part.Vertex(p)
        found, rest = [], []
        for f, b, broken in self.faces:
            if b.XMin - near <= p.x <= b.XMax + near and b.YMin - near <= p.y <= b.YMax + near and b.ZMin - near <= p.z <= b.ZMax + near:
                found.append((face_distance(f, p, v), broken))
                if found[-1][0] < 1e-7:
                    return found[-1]
            else:
                rest.append((f, broken))
        best = min((dist for dist, _ in found), default=math.inf)
        if best > near:
            found += [(face_distance(f, p, v), broken) for f, broken in rest]
            best = min(dist for dist, _ in found)
        return best, any(broken for dist, broken in found if dist <= best + TIE)


def one_way(points: list[tuple[FreeCAD.Vector, bool]], to: Surface) -> dict:
    """The largest distance from the points to a surface: for the points of the form, and for those at the edge break."""
    worst = {False: (0.0, [0.0, 0.0, 0.0]), True: (0.0, [0.0, 0.0, 0.0])}
    for p, on_break in points:
        dist, to_break = to.distance(p)
        key = on_break or to_break
        if dist > worst[key][0]:
            worst[key] = (dist, [round(p.x, 2), round(p.y, 2), round(p.z, 2)])
    return {"form": round(worst[False][0], 4), "form_at": worst[False][1], "break": round(worst[True][0], 4), "break_at": worst[True][1]}


def compare(a: Part.Shape, b: Part.Shape, radius: float = 1.0) -> dict:
    """The numbers of the comparison of two shapes; radius is that of the edge break."""
    ba, bb = a.optimalBoundingBox(False, False), b.optimalBoundingBox(False, False)   # the true boxes, not those of the spline poles
    box = max(abs(p - q) for p, q in zip((ba.XMin, ba.YMin, ba.ZMin, ba.XMax, ba.YMax, ba.ZMax), (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax)))
    pa, pb = surface_points(a, radius), surface_points(b, radius)
    ab, ba_ = one_way(pa, Surface(b, radius)), one_way(pb, Surface(a, radius))
    return {"volume_a": round(a.Volume, 1), "volume_b": round(b.Volume, 1), "volume_diff": round(a.Volume - b.Volume, 1),
            "area_a": round(a.Area, 1), "area_b": round(b.Area, 1), "faces_a": len(a.Faces), "faces_b": len(b.Faces),
            "box_a": [round(v, 3) for v in (ba.XMin, ba.YMin, ba.ZMin, ba.XMax, ba.YMax, ba.ZMax)],
            "box_b": [round(v, 3) for v in (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax)], "box_diff": round(box, 4),
            "a_to_b": ab["form"], "a_to_b_at": ab["form_at"], "b_to_a": ba_["form"], "b_to_a_at": ba_["form_at"],
            "break_a_to_b": ab["break"], "break_a_to_b_at": ab["break_at"], "break_b_to_a": ba_["break"], "break_b_to_a_at": ba_["break_at"],
            "points_a": len(pa), "points_b": len(pb)}


def pairs(a: dict[str, Part.Shape], b: dict[str, Part.Shape], spec: str) -> dict[str, list[str] | None]:
    """For each part of the first build, the parts of the second that it is compared with (None: no partner)."""
    named = dict(item.split(":") for item in spec.split(",") if item)
    out: dict[str, list[str] | None] = {}
    for k in a:
        names = named[k].split("+") if k in named else [k]
        out[k] = names if all(n in b for n in names) else None
    return out


def table(rows: dict[str, dict | None], title: str, tol: float) -> str:
    lines = [f"# {title}", "", f"Tolerance for the distance: {tol:g} mm. A is the first build, B the second. The columns \"at the edge break\" are for the "
             "points on a face of the edge break, or nearest to one; the tolerance is for all other points.", "",
             "| Part | Volume A, mm3 | Volume B, mm3 | A - B, mm3 | Faces A / B | Box, largest difference, mm | A to B, mm | at | B to A, mm | at | "
             "At the edge break, A to B / B to A, mm | at | Within the tolerance |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k, r in rows.items():
        if r is None:
            lines.append(f"| {k} | | | | | | | | | | | | no partner |")
            continue
        ok = max(r["a_to_b"], r["b_to_a"]) <= tol
        at = r["break_a_to_b_at"] if r["break_a_to_b"] >= r["break_b_to_a"] else r["break_b_to_a_at"]
        lines.append(f"| {k} | {r['volume_a']:.1f} | {r['volume_b']:.1f} | {r['volume_diff']:+.1f} | {r['faces_a']} / {r['faces_b']} | {r['box_diff']:.4f} | "
                     f"{r['a_to_b']:.4f} | {r['a_to_b_at']} | {r['b_to_a']:.4f} | {r['b_to_a_at']} | {r['break_a_to_b']:.4f} / {r['break_b_to_a']:.4f} | {at} | "
                     f"{'yes' if ok else 'NO'} |")
    return "\n".join(lines) + "\n"


def run(dir_a: str, dir_b: str, spec: str = "", only: list[str] | None = None) -> dict[str, dict | None]:
    from candybar.shell.dims import Blueprint
    radius = Blueprint().edge_break
    a, b = load(dir_a), load(dir_b)
    rows: dict[str, dict | None] = {}
    for k, names in pairs(a, b, spec).items():
        if only and k not in only:
            continue
        if names is None:
            rows[k] = None
            continue
        other = b[names[0]] if len(names) == 1 else b[names[0]].fuse([b[n] for n in names[1:]])
        rows[k] = compare(a[k], other, radius)
    return rows


def main() -> int:
    dir_a, dir_b = os.environ["CANDYBAR_A"], os.environ["CANDYBAR_B"]
    out = os.environ.get("CANDYBAR_OUT", os.path.join(dir_a, "compare"))
    tol = float(os.environ.get("CANDYBAR_TOL", "0.3"))
    only = [p for p in os.environ.get("CANDYBAR_PARTS", "").split(",") if p] or None
    rows = run(dir_a, dir_b, os.environ.get("PAIR", ""), only)
    os.makedirs(out, exist_ok=True)
    json.dump({"a": dir_a, "b": dir_b, "tolerance_mm": tol, "parts": rows}, open(os.path.join(out, "compare.json"), "w"), indent=1)
    text = table(rows, f"Parts of {dir_a} (A) against {dir_b} (B)", tol)
    open(os.path.join(out, "compare.md"), "w").write(text)
    print(text, end="")
    ok = all(r is not None and max(r["a_to_b"], r["b_to_a"]) <= tol for r in rows.values())
    print("compare:", "pass" if ok else "FAIL")
    return 0 if ok else 1
