"""The edge finish of the shell: which convex edges are still sharp, by part and by place, and whether the edge rule
holds.

The edge rule (the owner, 2026-11-12; decision record 0007): no outside edge of the exterior stays fully sharp,
because paint does not hold on a sharp edge. A convex edge that turns more than edge_break_turn has a round of the
design or the edge break. The rule is for the parts that are printed, filled and painted. Each part of the build is
in one class, by name:
  PRINTED       a printed and painted part of the exterior: the rule holds
  CUT_PLATES    a cut plate: not a printed part
  PROVISIONAL   a stand-in for a part that is not designed yet: "provisional, not finished"
  NOT_DECIDED   the record does not say how the part is made: the rule waits for the owner's choice
A part of the build that is in no class is a failure: no part passes because nobody named it.

This tool reads the parts of a build and lists, for each part, the convex edges that turn more than
edge_break_turn and have no round, in groups by place and by whether they show:
  outside                 the edge shows on the finished cabinet
  in a joint: against X   one of its two faces lies against the part X, or in the seam between the body and the
                          hood. A person does not see the edge, and paint does not go there
A sharp edge of a printed part passes only in a joint of JOINTS, which names each joint. It also counts the faces
that are rounds: those of the edge break (with the balls at the corners where three broken edges meet), and those
of the design (any other radius under ROUND_MAX).

Run headless. It writes edge-finish.json and edge-finish.md into the build's directory, and exits 1 when the rule
does not hold:

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
SEAM_NAME = "the seam between the body and the hood"

PRINTED = ("deck", "body", "hood")
CUT_PLATES = {"control_panel": "The top of a control panel is a cut plate (roadmap, settled by the owner)."}
PROVISIONAL = {
    "marquee_lip": "A stand-in for the lower frame of the marquee window. The marquee is not designed yet.",
    "speaker_right": "A stand-in for the speaker grille on the hood band. The grille is not designed yet.",
    "speaker_left": "A stand-in for the speaker grille on the hood band. The grille is not designed yet.",
    "logo_form": "A stand-in for the logo on the hood band. The logo is not designed yet.",
}
NOT_DECIDED = {
    "bezel": "The record does not say how the bezel plate is made. Decision record 0006 does not name the way to cut it, "
             "and split.BEZEL_OPTIONS keeps three ways: two printed halves, four printed bars, or a cut plate with a printed "
             "inner frame. The owner did not choose.",
}
# the joints in which a sharp edge of a printed part can lie: (part, what the face of the edge lies against)
JOINTS = {
    ("deck", "body"): "The deck and the body meet on the plane at the foot of the sweep. They are one bonded shell.",
    ("deck", "control_panel"): "The pocket of the control panel, under the panel.",
    ("body", "deck"): "The deck and the body meet on the plane at the foot of the sweep. They are one bonded shell.",
    ("body", "bezel"): "The recess and the reveal of the bezel plate, under and beside the plate.",
    ("body", "screen"): "The window of the form behind the bezel plate, where the monitor lies. The screen of the build is a "
                        "plate of 1 mm for the renders.",
}


def finish_class(part: str) -> str:
    """The class of a part of the build, or "" when it is in none."""
    if part in PRINTED:
        return "printed"
    if part in CUT_PLATES:
        return "cut plate"
    if part in PROVISIONAL:
        return "provisional, not finished"
    if part in NOT_DECIDED:
        return "not decided"
    return ""


def load(folder: str) -> dict[str, Part.Shape]:
    manifest = json.load(open(os.path.join(folder, "manifest.json")))
    out = {}
    for name, entry in manifest.items():
        s = Part.Shape()
        s.read(os.path.join(folder, entry["brep"]))
        out[name] = s
    return out


def against(face: Part.Face, others: dict[str, Part.Shape], d: Blueprint) -> str:
    """What a face lies against: the name of another part (a point just outside the middle of the face is inside
    that part), the seam between the body top and the foot of the hood, or "" when the face shows."""
    u0, u1, v0, v1 = face.ParameterRange
    p = face.valueAt((u0 + u1) / 2, (v0 + v1) / 2)
    n = face.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
    if abs(abs(n.z) - 1) < 1e-6 and d.body_top - SEAM < p.z < d.body_top + d.seam_gap + SEAM:
        return SEAM_NAME
    q = p + n * NEAR
    return next((name for name, o in others.items() if o.BoundBox.isInside(q) and o.isInside(q, 1e-3, True)), "")


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
    """For each part: its class, the sharp convex edges that turn more than edge_break_turn, grouped by place and by
    what they lie against; and how many of its faces are rounds."""
    out = {}
    for name, shape in parts.items():
        if name in face_check.NOT_PARTS:
            continue
        others = {k: s for k, s in parts.items() if k != name}
        lies = {f.hashCode(): against(f, others, d) for f in shape.Faces}
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
            joint = next((lies[f.hashCode()] for f in fs if lies[f.hashCode()]), "")
            groups[(zone(name, m, d), joint)].append((round(e.Length, 1), round(turn, 1), [round(m.x, 1), round(m.y, 1), round(m.z, 1)]))
        breaks = [f for f in shape.Faces if face_check.is_break(f, d.edge_break)]
        balls = [f for f in shape.Faces if isinstance(f.Surface, Part.Sphere) and abs(f.Surface.Radius - d.edge_break) < 0.02]
        rounds = [f for f in shape.Faces if not isinstance(f.Surface, Part.Plane) and so.tight(f, ROUND_MAX)
                  and not face_check.is_break_surface(f, d.edge_break)]
        out[name] = {"class": finish_class(name),
                     "sharp": [{"zone": z, "against": j, "edges": len(es), "length": round(sum(e[0] for e in es), 1),
                                "turn": [min(e[1] for e in es), max(e[1] for e in es)], "at": [e[2] for e in sorted(es, reverse=True)[:6]]}
                               for (z, j), es in sorted(groups.items())],
                     "break_faces": len(breaks), "break_corner_faces": len(balls), "design_round_faces": len(rounds)}
    return out


def failures(rows: dict) -> list[str]:
    """Where the edge rule does not hold: a part in no class, a printed part with a sharp edge that shows, and a
    printed part with a sharp edge in a joint that JOINTS does not name."""
    out = []
    for part, r in rows.items():
        if not r["class"]:
            out.append(f"{part}: the part is in no class (printed, cut plate, provisional, not decided)")
        if r["class"] != "printed":
            continue
        for g in r["sharp"]:
            if not g["against"]:
                out.append(f"{part}, {g['zone']}: {g['edges']} sharp edges show ({g['length']} mm, {g['turn'][0]:g} to {g['turn'][1]:g} degrees), "
                           f"the longest at {tuple(g['at'][0])}")
            elif (part, g["against"]) not in JOINTS:
                out.append(f"{part}, {g['zone']}: {g['edges']} sharp edges lie against {g['against']}, which is not a named joint")
    return out


def shows(part_class: str, joint: str) -> str:
    """How a group of sharp edges reads in the list."""
    if joint:
        return f"in a joint: against {joint}"
    return {"printed": "outside", "cut plate": "outside (a cut plate)", "provisional, not finished": "provisional, not finished",
            "not decided": "outside (not decided)"}.get(part_class, "outside")


def table(rows: dict, d: Blueprint) -> str:
    count = lambda r, joint: sum(g["edges"] for g in r["sharp"] if bool(g["against"]) == joint)

    def verdict(part: str, r: dict) -> str:
        if r["class"] == "printed":
            return "finished" if not count(r, False) else "NOT FINISHED"
        return r["class"] or "IN NO CLASS"

    lines = ["# Edge finish of the shell", "",
             f"Convex edges that turn more than {d.edge_break_turn:g} degrees and have no round. "
             f"The edge break is R {d.edge_break:g}. The design round of the rear is R {d.rear_round_r:g}.", "",
             "| Part | Class | Faces of the edge break | Faces of design rounds | Sharp edges that show | Sharp edges in a joint | Edge finish |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for part, r in rows.items():
        corners = f" and {r['break_corner_faces']} corner balls" if r["break_corner_faces"] else ""
        lines.append(f"| {part} | {r['class'] or 'none'} | {r['break_faces']}{corners} | {r['design_round_faces']} | {count(r, False)} | {count(r, True)} | {verdict(part, r)} |")
    lines += ["", "| Part | Place | Shows | Edges | Total length, mm | Turn, degrees | Longest at (x, y, z) |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for part, r in rows.items():
        for g in r["sharp"]:
            lines.append(f"| {part} | {g['zone']} | {shows(r['class'], g['against'])} | {g['edges']} | {g['length']} | {g['turn'][0]:g} to {g['turn'][1]:g} | "
                         f"{'; '.join(str(tuple(a)) for a in g['at'][:3])} |")
    lines += ["", "The parts that are not printed and painted parts of the exterior:", ""]
    lines += [f"- `{part}`: {why}" for group in (CUT_PLATES, PROVISIONAL, NOT_DECIDED) for part, why in group.items() if part in rows]
    lines += ["", "The joints in which a sharp edge of a printed part lies:", ""]
    used = sorted({(part, g["against"]) for part, r in rows.items() if r["class"] == "printed" for g in r["sharp"] if g["against"]})
    lines += [f"- `{part}` against {joint}: {JOINTS.get((part, joint), 'NOT A NAMED JOINT')}" for part, joint in used]
    bad = failures(rows)
    lines += ["", "The edge rule holds: no printed part has a sharp edge that shows." if not bad else "The edge rule does NOT hold:", ""]
    lines += [f"- {b}" for b in bad]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    out = os.environ.get("CANDYBAR_OUT", "cad/out/shell-rev7")
    d = Blueprint()
    rows = survey(load(out), d)
    json.dump({"parts": rows, "failures": failures(rows)}, open(os.path.join(out, "edge-finish.json"), "w"), indent=1)
    text = table(rows, d)
    open(os.path.join(out, "edge-finish.md"), "w").write(text)
    print(text, end="")
    return 1 if failures(rows) else 0
