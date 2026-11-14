"""Compare the solids of the blueprint with the blueprint's own faces, and fail when they differ by more than 0.5 mm.

The solids are the parts that candybar.shell.solids writes (one BREP file per part, listed in manifest.json).
The reference is profiles.faces(Blueprint()): the labelled faces as flat polygons. The check has three parts:
  solid state  each part is one valid closed solid with a positive volume and a clean check(); no two parts
               share more than 1 mm3.
  silhouettes  the outlines of all parts together and of all faces, seen from the front, the right and above,
               rasterised at 1/6 mm; the largest distance from a point of one outline to the other outline.
  sections     the cut of the parts and the cut of the faces with named planes; the largest distance in each
               direction. The parts of each of GROUPS are fused first, as the faces draw them as one skin; the
               forms on the hood band are cut on their own, as the faces draw the band under them.

The faces draw the form. The edge break (a round of 1 mm, the last modelling step) is not in them: at an edge of 90
degrees it stands 0.4 off the sharp edge, inside the tolerance, and no plane is put where it would cut a break at a
small angle.

Where the faces leave out a short wall, a point of a solid's cut does not count when it lies in a gap between two
loose ends of the faces' cut: inside a disc over a gap of at most BRIDGE, or on the straight line over a gap of at
most CHORD. The report counts these points. The faces MARKS are drawn 0.5 proud as markings and are not compared.

Run headless (exit status 1 when a tolerance is exceeded):

    CANDYBAR_OUT=cad/out/shell-rev7 cad/candybar/freecad-run.sh tools.check_solids
"""
from __future__ import annotations

import json
import math
import os

import FreeCAD
import MeshPart
import numpy as np
import Part
from PIL import Image, ImageDraw

from candybar.shell import profiles as pr
from candybar.shell.dims import Blueprint

V = FreeCAD.Vector
TOL = 0.5
OVERLAP = 1.0
BRIDGE = 7.0
CHORD = 25.0
PX_PER_MM = 6.0
STEP = 0.2
MARKS = {"RB6", "MQ2", "SP2", "LG2"}
VIEWS = {"front": (0, 2), "right side": (1, 2), "top": (0, 1)}
GROUPS = (("deck", "control_panel", "body", "bezel", "screen"), ("hood", "marquee_lip"))


def planes(d: Blueprint) -> dict[str, tuple[int, float]]:
    """The section planes: (axis, position)."""
    h = pr.hood(d)
    hw = d.width / 2
    return {"X 0": (0, 0.0),
            "X rail land": (0, (d.bezel_w / 2 + d.panel_gap + hw - d.edge_in) / 2),
            "X band": (0, hw - d.step_in / 2),
            "Z deck": (2, d.deck_top - d.deck_lean_h / 2),
            "Z panel pocket": (2, (d.panel_top + d.deck_top) / 2),
            "Z cut-in": (2, d.cut_in_z0 + d.cut_in_h / 2),
            "Z mid body": (2, (d.deck_top + d.body_top) / 2),
            "Z tuck": (2, (d.tuck_z0 + d.body_top) / 2),
            "Z seam, body": (2, d.body_top - d.seam_groove / 2),
            "Z seam, hood": (2, d.body_top + d.seam_gap + d.seam_groove / 2),
            "Z hood": (2, h.origin[2] + 0.4 * h.height),
            "Y hood front": (1, h.origin[1] + d.hood_edge_back / 4),
            "X hood, off centre": (0, h.half_top / 2),
            "X seam corner": (0, d.side_x(d.body_top) - d.edge_in / 2),
            "X speaker": (0, d.logo_w / 2 + d.logo_gap + 40.0),
            # through the seam at the front corners, where it cuts the leaning front of the hood half way up the sill: a
            # plane that cuts the front where it meets the opening goes through the edge break of the rim at a small
            # angle, which the faces do not draw
            "Y seam corner": (1, h.origin[1] + 0.5 * d.hood_sill_h * math.tan(math.radians(d.hood_front_lean_low))),
            "Y rear corner": (1, d.depth - 4.0 / 3.0 * d.seam_groove),
            "Y rear shelf": (1, d.body_d + d.rear_proud / 2),
            "Y body top": (1, (d.seam_y + d.depth) / 2)}


# ---------- the faces ----------

def face_cut(faces: dict[str, pr.Face], axis: int, at: float) -> np.ndarray:
    """The cut of every polygon with the plane, as segments (n, 2, 2) in the two other coordinates."""
    keep = [i for i in range(3) if i != axis]
    out = []
    for face in faces.values():
        if face.id in MARKS:
            continue
        for p in face.polys:
            pts = np.array(p, float)
            side = pts[:, axis] - at
            hits = []
            for i in range(len(pts)):
                a, b = pts[i], pts[(i + 1) % len(pts)]
                sa, sb = side[i], side[(i + 1) % len(pts)]
                if (sa > 0) != (sb > 0):
                    hits.append((a + sa / (sa - sb) * (b - a))[keep])
            if len(hits) >= 2:
                hits = np.array(hits)
                spread = hits.max(axis=0) - hits.min(axis=0)
                hits = hits[np.argsort(hits[:, int(np.argmax(spread))])]
                out += [hits[k:k + 2] for k in range(0, len(hits) - 1, 2)]
    return np.array(out).reshape(-1, 2, 2)


def sample(segs: np.ndarray, step: float = STEP) -> np.ndarray:
    pts = []
    for a, b in segs:
        n = max(1, math.ceil(np.linalg.norm(b - a) / step))
        pts.append(a + (b - a) * np.linspace(0.0, 1.0, n + 1)[:, None])
    return np.concatenate(pts) if pts else np.zeros((0, 2))


def nearest_segment(points: np.ndarray, segs: np.ndarray, chunk: int = 512) -> np.ndarray:
    a, ab = segs[:, 0], segs[:, 1] - segs[:, 0]
    ll = np.maximum((ab ** 2).sum(-1), 1e-18)
    out = np.empty(len(points))
    for k in range(0, len(points), chunk):
        p = points[k:k + chunk, None, :]
        t = np.clip(((p - a) * ab).sum(-1) / ll, 0.0, 1.0)
        out[k:k + chunk] = np.sqrt((((a + t[..., None] * ab) - p) ** 2).sum(-1)).min(axis=1)
    return out


def distance(points: np.ndarray, segs: np.ndarray, tile: float = 20.0, reach: float = 10.0) -> np.ndarray:
    """Distance from each point to the nearest segment: exact, with the segments sorted into tiles first."""
    if not len(segs):
        return np.full(len(points), np.inf)
    lo, hi = segs.min(axis=1), segs.max(axis=1)
    keys = np.floor(points / tile).astype(int)
    out = np.full(len(points), np.inf)
    for key in np.unique(keys, axis=0):
        at = np.nonzero((keys == key).all(axis=1))[0]
        near = ((lo <= (key + 1) * tile + reach) & (hi >= key * tile - reach)).all(axis=1)
        if near.any():
            out[at] = nearest_segment(points[at], segs[near])
    far = out > reach
    if far.any():
        out[far] = nearest_segment(points[far], segs)
    return out


def loose_ends(segs: np.ndarray, eps: float = 0.05) -> np.ndarray:
    """The ends of the cut that touch no other segment."""
    lo, hi = segs.min(axis=1) - eps, segs.max(axis=1) + eps
    out = []
    for k, e in enumerate(segs.reshape(-1, 2)):
        near = np.nonzero(((lo <= e) & (hi >= e)).all(axis=1))[0]
        near = near[near != k // 2]
        if not len(near) or nearest_segment(e[None], segs[near])[0] > eps:
            out.append(e)
    return np.array(out).reshape(-1, 2)


def bridged(points: np.ndarray, ends: np.ndarray) -> np.ndarray:
    """The points that lie in a gap between two loose ends: the walls that the faces leave out."""
    out = np.zeros(len(points), bool)
    gaps = np.linalg.norm(ends[:, None] - ends[None], axis=-1)
    for i, j in zip(*np.nonzero(np.triu((gaps > 1e-6) & (gaps <= CHORD)))):
        if gaps[i, j] <= BRIDGE:
            out |= np.linalg.norm(points - (ends[i] + ends[j]) / 2, axis=1) <= gaps[i, j] / 2 + TOL
        else:
            out |= nearest_segment(points, np.array([[ends[i], ends[j]]])) <= TOL
    return out


# ---------- the solids ----------

def skins(parts: dict[str, Part.Shape]) -> list[Part.Shape]:
    """The parts as the faces draw them: each of GROUPS fused, the others alone. The faces of the fuse are not merged
    (removeSplitter): merging the halves of a face that two parts share can leave an edge with a tolerance of
    millimetres, and the cuts are the same without it."""
    out = []
    for group in GROUPS:
        shapes = [parts[k] for k in group if k in parts]
        out.append(shapes[0].multiFuse(shapes[1:]) if len(shapes) > 1 else shapes[0])
    return out + [s for k, s in parts.items() if not any(k in g for g in GROUPS)]


def solid_cut(shapes: list[Part.Shape], axis: int, at: float) -> np.ndarray:
    """The cut of the skins with the plane, as segments (n, 2, 2) in the two other coordinates. The cut is a slice of
    each whole shape: a section face by face can miss part of a curve where a plane meets a spline face at a small
    angle."""
    keep = [i for i in range(3) if i != axis]
    normal = V(*[1.0 if i == axis else 0.0 for i in range(3)])
    segs = []
    for shape in shapes:
        for w in shape.slice(normal, at):
            for e in w.Edges:
                pts = np.array([[p[i] for i in keep] for p in e.discretize(Distance=STEP)])
                if len(pts) > 1:
                    segs.append(np.stack([pts[:-1], pts[1:]], axis=1))
    return np.concatenate(segs) if segs else np.zeros((0, 2, 2))


def compare(solid: np.ndarray, ref: np.ndarray) -> dict:
    """Largest distance from the solid's cut to the faces' cut and back, with the points that fall in a bridge."""
    pts = sample(solid)
    dist = distance(pts, ref)
    covered = bridged(pts, loose_ends(ref))
    ref_pts = sample(ref)
    back = distance(ref_pts, solid)
    far = dist[~covered]
    at = lambda p, k: [round(float(v), 1) for v in p[int(np.argmax(k))]] if len(k) else []
    return {"solid_to_blueprint": round(float(far.max()) if len(far) else 0.0, 3),
            "blueprint_to_solid": round(float(back.max()) if len(back) else 0.0, 3),
            "solid_worst_at": at(pts[~covered], far), "blueprint_worst_at": at(ref_pts, back),
            "bridged_points": int((covered & (dist > TOL)).sum())}


# ---------- silhouettes ----------

def mask(polys: list[np.ndarray], axes: tuple[int, int], box: tuple[float, float, float, float]) -> np.ndarray:
    x0, y0, x1, y1 = box
    w, h = int(math.ceil((x1 - x0) * PX_PER_MM)), int(math.ceil((y1 - y0) * PX_PER_MM))
    img = Image.new("1", (w, h), 0)
    draw = ImageDraw.Draw(img)
    for p in polys:
        q = [((x - x0) * PX_PER_MM, (y1 - y) * PX_PER_MM) for x, y in p[:, axes]]
        draw.polygon(q, fill=1, outline=1)
    return np.array(img, bool)


def outline(m: np.ndarray, box: tuple[float, float, float, float]) -> np.ndarray:
    """The centres of the pixels of a mask that touch the outside, in mm."""
    inner = m.copy()
    inner[1:, :] &= m[:-1, :]
    inner[:-1, :] &= m[1:, :]
    inner[:, 1:] &= m[:, :-1]
    inner[:, :-1] &= m[:, 1:]
    r, c = np.nonzero(m & ~inner)
    return np.stack([box[0] + (c + 0.5) / PX_PER_MM, box[3] - (r + 0.5) / PX_PER_MM], axis=1)


def nearest(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return distance(a, np.stack([b, b], axis=1))


def silhouettes(parts: dict[str, Part.Shape], faces: dict[str, pr.Face]) -> dict[str, dict]:
    tris = []
    for s in parts.values():
        mesh = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.1)
        pts, idx = mesh.Topology
        pts = np.array([[p.x, p.y, p.z] for p in pts])
        tris += list(pts[np.array(idx)])
    ref = [np.array(p, float) for f in faces.values() if f.id not in MARKS for p in f.polys]
    out = {}
    for view, axes in VIEWS.items():
        lo = np.min([t[:, axes].min(axis=0) for t in tris + ref], axis=0) - 2.0
        hi = np.max([t[:, axes].max(axis=0) for t in tris + ref], axis=0) + 2.0
        box = (lo[0], lo[1], hi[0], hi[1])
        a, b = outline(mask(tris, axes, box), box), outline(mask(ref, axes, box), box)
        out[view] = {"solid_to_blueprint": round(float(nearest(a, b).max()), 3), "blueprint_to_solid": round(float(nearest(b, a).max()), 3)}
    return out


# ---------- the whole check ----------

def solid_state(parts: dict[str, Part.Shape]) -> tuple[dict[str, dict], list[dict]]:
    state = {}
    for k, s in parts.items():
        try:
            s.check(True)
            clean = True
        except (ValueError, Part.OCCError):
            clean = False
        closed = all(sh.isClosed() for sh in s.Shells)
        state[k] = {"valid": s.isValid(), "solids": len(s.Solids), "closed": closed, "check": clean, "volume_mm3": round(s.Volume, 1)}
    overlaps = []
    names = list(parts)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if parts[a].BoundBox.intersect(parts[b].BoundBox):
                v = parts[a].common(parts[b]).Volume
                if v > OVERLAP:
                    overlaps.append({"parts": [a, b], "volume_mm3": round(v, 1)})
    return state, overlaps


def run(parts: dict[str, Part.Shape], d: Blueprint) -> dict:
    """Every number of the check, and whether all of them are inside the tolerances."""
    faces = pr.faces(d)
    state, overlaps = solid_state(parts)
    shapes = skins(parts)
    sections = {}
    for name, (axis, at) in planes(d).items():
        sections[name] = {"at": round(at, 2), **compare(solid_cut(shapes, axis, at), face_cut(faces, axis, at))}
    sil = silhouettes(parts, faces)
    over = lambda r: max(r["solid_to_blueprint"], r["blueprint_to_solid"]) > TOL
    ok = (all(s["valid"] and s["solids"] == 1 and s["closed"] and s["check"] and s["volume_mm3"] > 0 for s in state.values())
          and not overlaps and not any(over(r) for r in [*sections.values(), *sil.values()]))
    return {"ok": ok, "tolerance_mm": TOL, "parts": state, "overlaps": overlaps, "silhouettes": sil, "sections": sections}


def table(r: dict) -> str:
    lines = ["| Part | Valid | Closed | check() | Volume, mm3 |", "| --- | --- | --- | --- | --- |"]
    lines += [f"| {k} | {s['valid'] and s['solids'] == 1} | {s['closed']} | {s['check']} | {s['volume_mm3']:.0f} |" for k, s in r["parts"].items()]
    lines += ["", f"Overlaps over {OVERLAP} mm3: " + (", ".join(f"{'/'.join(o['parts'])} {o['volume_mm3']}" for o in r["overlaps"]) or "none"), "",
              "| View or plane | At, mm | Solid to blueprint, mm | Blueprint to solid, mm | Bridged points | Worst solid point | Worst blueprint point | Within 0.5 |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k, s in r["silhouettes"].items():
        lines.append(f"| {k} | | {s['solid_to_blueprint']:.2f} | {s['blueprint_to_solid']:.2f} | | | | {max(s['solid_to_blueprint'], s['blueprint_to_solid']) <= TOL} |")
    for k, s in r["sections"].items():
        lines.append(f"| {k} | {s['at']} | {s['solid_to_blueprint']:.2f} | {s['blueprint_to_solid']:.2f} | {s['bridged_points']} | {s['solid_worst_at']} | {s['blueprint_worst_at']} |"
                     f" {max(s['solid_to_blueprint'], s['blueprint_to_solid']) <= TOL} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    out = os.environ.get("CANDYBAR_OUT", "cad/out/shell-rev7")
    manifest = json.load(open(os.path.join(out, "manifest.json")))
    parts = {k: Part.read(os.path.join(out, v["brep"])) for k, v in manifest.items()}
    r = run(parts, Blueprint())
    json.dump(r, open(os.path.join(out, "check.json"), "w"), indent=1)
    text = table(r)
    open(os.path.join(out, "check.md"), "w").write(text)
    print(text, end="")
    print("check:", "pass" if r["ok"] else "FAIL")
    return 0 if r["ok"] else 1
