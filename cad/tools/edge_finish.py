"""The edge finish of the shell: which convex edges are still sharp, by part and by place.

The edge rule (decision record 0007): no outside edge stays fully sharp. A convex edge that turns more than
edge_break_turn has a round of the design or the edge break. This tool reads the parts of a build and lists, for
each part, the convex edges that turn more than that and have no round, in groups:
  outside      the edge shows on the finished cabinet
  in a joint   one of its two faces lies against another part, or in the seam between the body and the hood
               (a person does not see it, and paint does not go there)
It also counts the faces that are rounds: those of the edge break, and those of the design (any other radius under
ROUND_MAX).

Run headless. It writes edge-finish.json and edge-finish.md into the build's directory:

    CANDYBAR_OUT=cad/out/shell-rev7 cad/candybar/freecad-run.sh tools.edge_finish
"""
from __future__ import annotations

import json
import os
from collections import defaultdict

import FreeCAD
import Part

from candybar.shell import solids as so
from candybar.shell.dims import Blueprint
from tools import face_check

V = FreeCAD.Vector
ROUND_MAX = 12.0
NEAR = 0.05
SEAM = 0.2


def load(folder: str) -> dict[str, Part.Shape]:
    manifest = json.load(open(os.path.join(folder, "manifest.json")))
    out = {}
    for name, entry in manifest.items():
        s = Part.Shape()
        s.read(os.path.join(folder, entry["brep"]))
        out[name] = s
    return out


def covered(face: Part.Face, others: list[Part.Shape], d: Blueprint) -> bool:
    """Whether a face lies against another part (a point just outside its middle is inside that part), or in the
    seam between the body top and the foot of the hood."""
    u0, u1, v0, v1 = face.ParameterRange
    p = face.valueAt((u0 + u1) / 2, (v0 + v1) / 2)
    n = face.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
    if abs(abs(n.z) - 1) < 1e-6 and d.body_top - SEAM < p.z < d.body_top + d.seam_gap + SEAM:
        return True
    q = p + n * NEAR
    return any(o.BoundBox.isInside(q) and o.isInside(q, 1e-3, True) for o in others)


def zone(part: str, m: FreeCAD.Vector, d: Blueprint) -> str:
    """A plain name for the place of an edge on its part."""
    g = d.seam_groove
    if part == "body":
        if m.z < 1e-3:
            return "floor edge"
        if m.z > d.body_top - g - 0.5:
            return "seam groove (bevel and body top)"
        if so.behind_band(d, m):
            return "rear (band, shelf, head, lower body)"
        if abs(m.x) < d.bezel_w / 2 + d.panel_gap + 0.5:
            return "bezel opening (reveal and recess)"
        return "rail and side band"
    if part == "hood":
        if m.z < d.body_top + d.seam_gap + g + 0.5:
            return "seam groove (bevel and foot)"
        if m.y > d.depth - 60:
            return "rear"
        return "front opening (legs, top bar, sill, recess)"
    if part == "deck":
        if m.z < 1e-3:
            return "floor edge"
        if m.z > d.panel_top - d.panel_t - 0.5 and abs(m.x) < d.panel_w / 2 + d.panel_gap + 0.5 and m.y > d.deck_nose - 1:
            return "panel pocket"
        return "front, sides and joint with the body"
    return "all"


def survey(parts: dict[str, Part.Shape], d: Blueprint) -> dict:
    """For each part: the sharp convex edges that turn more than edge_break_turn, grouped by place and by whether
    they show; and the areas of its rounds."""
    out = {}
    for name, shape in parts.items():
        if name in face_check.NOT_PARTS:
            continue
        others = [s for k, s in parts.items() if k != name]
        hidden = {f.hashCode(): covered(f, others, d) for f in shape.Faces}
        groups: dict[tuple[str, str], list] = defaultdict(list)
        for e in shape.Edges:
            if e.Degenerated:
                continue
            fs = shape.ancestorsOfType(e, Part.Face)
            if len(fs) != 2:
                continue
            convex, turn = so.edge_turn(shape, e)
            if not convex or turn <= d.edge_break_turn:
                continue
            m = so.middle(e)
            shows = "in a joint" if any(hidden[f.hashCode()] for f in fs) else "outside"
            groups[(zone(name, m, d), shows)].append((round(e.Length, 1), round(turn, 1), [round(m.x, 1), round(m.y, 1), round(m.z, 1)]))
        breaks = [f for f in shape.Faces if face_check.is_break(f, d.edge_break)]
        rounds = [f for f in shape.Faces if not isinstance(f.Surface, Part.Plane) and so.tight(f, ROUND_MAX) and not face_check.is_break(f, d.edge_break)]
        out[name] = {"sharp": [{"zone": z, "shows": s, "edges": len(es), "length": round(sum(e[0] for e in es), 1),
                                "turn": [min(e[1] for e in es), max(e[1] for e in es)], "at": [e[2] for e in sorted(es, reverse=True)[:6]]}
                               for (z, s), es in sorted(groups.items())],
                     "break_faces": len(breaks), "design_round_faces": len(rounds)}
    return out


def table(rows: dict, d: Blueprint) -> str:
    lines = ["# Edge finish of the shell", "",
             f"Convex edges that turn more than {d.edge_break_turn:g} degrees and have no round. "
             f"The edge break is R {d.edge_break:g}; the design round of the rear is R {d.rear_round_r:g}.", "",
             "| Part | Faces of the edge break | Faces of design rounds | Sharp edges, outside | Sharp edges, in a joint |", "| --- | --- | --- | --- | --- |"]
    for part, r in rows.items():
        count = lambda shows: sum(g["edges"] for g in r["sharp"] if g["shows"] == shows)
        lines.append(f"| {part} | {r['break_faces']} | {r['design_round_faces']} | {count('outside')} | {count('in a joint')} |")
    lines += ["", "| Part | Place | Shows | Edges | Total length, mm | Turn, degrees | Longest at (x, y, z) |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for part, r in rows.items():
        for g in r["sharp"]:
            lines.append(f"| {part} | {g['zone']} | {g['shows']} | {g['edges']} | {g['length']} | {g['turn'][0]:g} to {g['turn'][1]:g} | "
                         f"{'; '.join(str(tuple(a)) for a in g['at'][:3])} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    out = os.environ.get("CANDYBAR_OUT", "cad/out/shell-rev7")
    d = Blueprint()
    rows = survey(load(out), d)
    json.dump(rows, open(os.path.join(out, "edge-finish.json"), "w"), indent=1)
    text = table(rows, d)
    open(os.path.join(out, "edge-finish.md"), "w").write(text)
    print(text, end="")
    return 0
