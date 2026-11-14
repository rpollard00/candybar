"""The layout rules of the hardware items: interference (R1), keep-out (R2) and button spacing (R5), and what the
fit study gives as warnings: two ergonomic targets (R6) and the parameters that are still to measure (R7).

Every rule reads evaluated parameters and shapes from the document, nothing else. The fit study (fit.py) runs them
and has the rules that need the cavity."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import hypot
from typing import Callable

import FreeCAD as App

from . import controls, model, params

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
SOLID_ROLES = ("hardware", "protrusion")
VOLUME_TOLERANCE = 1.0
LENGTH_TOLERANCE = 1e-6
NUT_OVERLAP_WARN = 1.0
NUT_TAGS = (controls.ACTION_NUT, controls.SERVICE_NUT)
Finding = tuple[str, str, str]


@dataclass(frozen=True)
class Scene:
    doc: App.Document
    solids: tuple[model.Placed, ...]
    table: tuple[dict[str, str], ...]

    def value(self, name: str) -> float:
        return params.value(self.doc, name)

    def with_role(self, *roles: str) -> list[model.Placed]:
        return [solid for solid in self.solids if solid.role in roles]

    def with_tag(self, *tags: str) -> list[model.Placed]:
        return [solid for solid in self.solids if solid.tag in tags]


def _common_volume(a: model.Placed, b: model.Placed) -> float:
    if not a.world.BoundBox.intersect(b.world.BoundBox):
        return 0.0
    return a.world.common(b.world).Volume


def _clashes(pairs: list[tuple[model.Placed, model.Placed]]) -> list[Finding]:
    found = [
        (FAIL, f"{a.name} / {b.name}", f"common volume {volume:.0f} mm3")
        for a, b in pairs
        if (volume := _common_volume(a, b)) > VOLUME_TOLERANCE
    ]
    return found or [(PASS, f"{len(pairs)} pairs", f"no common volume above {VOLUME_TOLERANCE:g} mm3")]


def interference(scene: Scene) -> list[Finding]:
    """R1: two solids of different owners share more than VOLUME_TOLERANCE."""
    pairs = [
        (a, b)
        for a, b in combinations(scene.with_role(*SOLID_ROLES), 2)
        if a.owner != b.owner and not _both_nuts(a, b)
    ]
    return _clashes(pairs)


def _both_nuts(a: model.Placed, b: model.Placed) -> bool:
    """Two button nuts are judged by the spacing rule, which grades a small overlap as a warning."""
    return a.tag in NUT_TAGS and b.tag in NUT_TAGS


def keepout(scene: Scene) -> list[Finding]:
    """R2: a solid of one owner is in a keep-out zone of a different owner."""
    pairs = [
        (zone, solid)
        for zone in scene.with_role("keepout")
        for solid in scene.with_role(*SOLID_ROLES)
        if zone.owner != solid.owner
    ]
    return _clashes(pairs)


def button_spacing(scene: Scene) -> list[Finding]:
    """R5: two button nuts overlap. More than NUT_OVERLAP_WARN fails; less gives a warning."""
    nuts = scene.with_tag(*NUT_TAGS)
    found: list[Finding] = []
    for a, b in combinations(nuts, 2):
        box_a, box_b = a.world.BoundBox, b.world.BoundBox
        distance = hypot(box_a.Center.x - box_b.Center.x, box_a.Center.y - box_b.Center.y)
        needed = (box_a.XLength + box_b.XLength) / 2
        overlap = needed - distance
        if overlap > LENGTH_TOLERANCE:
            level = FAIL if overlap > NUT_OVERLAP_WARN else WARN
            detail = f"centres {distance:.2f} mm apart, the nuts need {needed:.2f} mm: overlap {overlap:.2f} mm"
            found.append((level, f"{a.name} / {b.name}", detail))
    return found or [(PASS, f"{len(nuts)} buttons", "no two nuts overlap")]


def _palm_rest(scene: Scene) -> float:
    return min(nut.world.BoundBox.Center.y for nut in scene.with_tag(controls.ACTION_NUT))


# The sight line and the eye distance of the older rule are in fit.sight_lines, for three players.
ERGONOMICS: tuple[tuple[str, Callable[[Scene], float], str, str], ...] = (
    ("panel top above the desk", lambda scene: scene.value("cp_top_z"), "tgt_panel_top", "mm"),
    ("palm rest: cabinet front edge to the nearest button centre", _palm_rest, "tgt_palm", "mm"),
)


def ergonomics(scene: Scene) -> list[Finding]:
    """R6: each value against its target range. Outside the range gives a warning."""
    found: list[Finding] = []
    for label, measure, target, unit in ERGONOMICS:
        actual, low, high = measure(scene), scene.value(f"{target}_min"), scene.value(f"{target}_max")
        level = PASS if low <= actual <= high else WARN
        found.append((level, label, f"{actual:.1f} {unit}; target {low:g} to {high:g} {unit}"))
    return found


def to_measure(scene: Scene) -> tuple[dict[str, str], ...]:
    """R7: the rows that name a measurement and are not measured. A row that the fit study sets is derived."""
    return tuple(row for row in scene.table if row["measure"] and row["status"] not in ("measured", "derived"))


def status_counts(scene: Scene) -> dict[str, int]:
    return {status: sum(row["status"] == status for row in scene.table) for status in params.STATUSES}


def md_table(headings: tuple[str, ...], rows: list[tuple[str, ...]]) -> str:
    lines = [headings, tuple("---" for _ in headings), *rows]
    return "\n".join("| " + " | ".join(cell.replace("|", "\\|") for cell in line) + " |" for line in lines)
