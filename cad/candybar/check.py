"""Layout checks. Every rule reads evaluated parameters and shapes from the document, nothing else."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from itertools import combinations
from math import hypot
from pathlib import Path
from typing import Callable

import FreeCAD as App

from . import massing, model, panel, params

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
LEVELS = (FAIL, WARN, PASS)
SOLID_ROLES = ("hardware", "protrusion", "printable", "massing", "trim")
VOLUME_TOLERANCE = 1.0
LENGTH_TOLERANCE = 1e-6
NUT_OVERLAP_WARN = 1.0
REPORT_MD = "report.md"
REPORT_JSON = "report.json"
OUTPUTS = (REPORT_MD, REPORT_JSON)
OVERALL = ("deck_w", "outer_w", "cab_d", "cab_h", "cp_top_z", "mon_center_y", "mon_center_z", "sight_angle", "eye_dist")

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


@dataclass(frozen=True)
class Row:
    rule: str
    title: str
    level: str
    subject: str
    detail: str


@dataclass(frozen=True)
class Measure:
    name: str
    value: float
    unit: str
    note: str

    def __str__(self) -> str:
        return f"{self.value:.1f} {self.unit}"


@dataclass(frozen=True)
class PartSize:
    """A printable part's bounding box and volume in its own frame, in mm and mm3."""

    name: str
    x: float
    y: float
    z: float
    volume: float


@dataclass(frozen=True)
class Report:
    rows: tuple[Row, ...]
    overall: tuple[Measure, ...]
    printables: tuple[PartSize, ...]
    status_counts: dict[str, int]
    to_measure: tuple[dict[str, str], ...]

    def count(self, level: str) -> int:
        return sum(row.level == level for row in self.rows)

    @property
    def result(self) -> str:
        return next(level for level in LEVELS if self.count(level))


def _state(scene: Scene) -> list[Finding]:
    found = [(FAIL, name, reason) for name, reason in model.errors(scene.doc)]
    return found or [(PASS, f"{len(scene.doc.Objects)} objects", "all recomputed without error")]


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


def _interference(scene: Scene) -> list[Finding]:
    pairs = [
        (a, b)
        for a, b in combinations(scene.with_role(*SOLID_ROLES), 2)
        if a.owner != b.owner or "printable" in (a.role, b.role)
    ]
    return _clashes(pairs)


def _keepout(scene: Scene) -> list[Finding]:
    pairs = [
        (zone, solid)
        for zone in scene.with_role("keepout")
        for solid in scene.with_role(*SOLID_ROLES)
        if zone.owner != solid.owner
    ]
    return _clashes(pairs)


def _containment(scene: Scene) -> list[Finding]:
    envelope = model.world_shape(scene.doc.getObject(massing.ENVELOPE))
    hardware = scene.with_role("hardware")
    found = [
        (FAIL, solid.name, f"{volume:.0f} mm3 lies outside the shell envelope")
        for solid in hardware
        if (volume := solid.world.cut(envelope).Volume) > VOLUME_TOLERANCE
    ]
    return found or [(PASS, f"{len(hardware)} hardware objects", "all inside the shell envelope")]


def _print_size(part: model.Placed) -> tuple[float, float, float]:
    bounds = part.own.BoundBox
    lengths = {"x": bounds.XLength, "y": bounds.YLength, "z": bounds.ZLength}
    height = lengths.pop(part.print_axis)
    return (*lengths.values(), height)


def _print_fit(scene: Scene) -> list[Finding]:
    bed, max_xy, max_z = (scene.value(name) for name in ("a1_bed", "a1_part_max_xy", "a1_part_max_z"))
    found: list[Finding] = []
    for part in scene.with_role("printable"):
        side_a, side_b, height = _print_size(part)
        footprint = max(side_a, side_b)
        if footprint > bed + LENGTH_TOLERANCE or height > bed + LENGTH_TOLERANCE:
            level = FAIL
        elif footprint > max_xy + LENGTH_TOLERANCE or height > max_z + LENGTH_TOLERANCE:
            level = WARN
        else:
            level = PASS
        detail = (
            f"{side_a:.1f} x {side_b:.1f} mm on the bed, {height:.1f} mm tall; "
            f"bed {bed:g} mm, recommended {max_xy:g} x {max_xy:g} x {max_z:g} mm"
        )
        found.append((level, part.name, detail))
    return found


def _button_spacing(scene: Scene) -> list[Finding]:
    nuts = scene.with_tag(panel.ACTION_NUT, panel.SERVICE_NUT)
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
    return min(nut.assembly.BoundBox.Center.y for nut in scene.with_tag(panel.ACTION_NUT))


ERGONOMICS: tuple[tuple[str, Callable[[Scene], float], str, str], ...] = (
    ("panel top above the desk", lambda scene: scene.value("cp_top_z"), "tgt_panel_top", "mm"),
    ("palm rest: panel front edge to the nearest button centre", _palm_rest, "tgt_palm", "mm"),
    ("sight line to the screen centre, below horizontal", lambda scene: scene.value("sight_angle"), "tgt_sight", "deg"),
    ("eye to screen centre", lambda scene: scene.value("eye_dist"), "tgt_eye_dist", "mm"),
)


def _ergonomics(scene: Scene) -> list[Finding]:
    found: list[Finding] = []
    for label, measure, target, unit in ERGONOMICS:
        actual, low, high = measure(scene), scene.value(f"{target}_min"), scene.value(f"{target}_max")
        level = PASS if low <= actual <= high else WARN
        found.append((level, label, f"{actual:.1f} {unit}; target {low:g} to {high:g} {unit}"))
    return found


def _to_measure(scene: Scene) -> tuple[dict[str, str], ...]:
    return tuple(row for row in scene.table if row["measure"] and row["status"] != "measured")


def _status_counts(scene: Scene) -> dict[str, int]:
    return {status: sum(row["status"] == status for row in scene.table) for status in params.STATUSES}


def _parameter_status(scene: Scene) -> list[Finding]:
    counts = ", ".join(f"{count} {status}" for status, count in _status_counts(scene).items())
    pending = len(_to_measure(scene))
    detail = f"{counts}; {pending} have a measurement still to take"
    return [(WARN if pending else PASS, f"{len(scene.table)} parameters", detail)]


RULES: tuple[tuple[str, str, Callable[[Scene], list[Finding]]], ...] = (
    ("R0", "object state", _state),
    ("R1", "interference", _interference),
    ("R2", "keep-out", _keepout),
    ("R3", "containment", _containment),
    ("R4", "print fit", _print_fit),
    ("R5", "button spacing", _button_spacing),
    ("R6", "ergonomics", _ergonomics),
    ("R7", "parameter status", _parameter_status),
)


def _apply(check: Callable[[Scene], list[Finding]], scene: Scene) -> list[Finding]:
    try:
        return check(scene)
    except Exception as error:  # a rule that cannot run on broken geometry must fail, not vanish
        return [(FAIL, "rule could not run", f"{type(error).__name__}: {error}")]


def run(doc: App.Document) -> Report:
    """Apply every rule to a recomputed document."""
    scene = Scene(doc, tuple(model.placed(doc)), tuple(params.table(doc)))
    rows = tuple(Row(rule, title, *finding) for rule, title, check in RULES for finding in _apply(check, scene))
    by_name = {row["name"]: row for row in scene.table}
    return Report(
        rows=rows,
        overall=tuple(_measure(scene, by_name[name]) for name in OVERALL),
        printables=tuple(_part_size(part) for part in scene.with_role("printable")),
        status_counts=_status_counts(scene),
        to_measure=_to_measure(scene),
    )


def _measure(scene: Scene, row: dict[str, str]) -> Measure:
    return Measure(row["name"], scene.value(row["name"]), row["unit"], row["note"])


def _part_size(part: model.Placed) -> PartSize:
    bounds = part.own.BoundBox
    return PartSize(part.name, bounds.XLength, bounds.YLength, bounds.ZLength, part.own.Volume)


def summary(report: Report) -> str:
    lines = [f"candybar check: {report.result} ({_counts(report)})"]
    lines += [
        f"  {row.level} {row.rule} {row.title}: {row.subject}: {row.detail}"
        for level in (FAIL, WARN)
        for row in report.rows
        if row.level == level
    ]
    lines.append("  " + ", ".join(f"{measure.name} {measure}" for measure in report.overall))
    return "\n".join(lines)


def _counts(report: Report) -> str:
    return ", ".join(f"{report.count(level)} {level}" for level in LEVELS)


def write(report: Report, out_dir: Path) -> None:
    (out_dir / REPORT_JSON).write_text(json.dumps(_as_json(report), indent=2) + "\n", encoding="utf-8")
    (out_dir / REPORT_MD).write_text(_as_markdown(report), encoding="utf-8")


def _as_json(report: Report) -> dict[str, object]:
    return {"result": report.result, "counts": {level: report.count(level) for level in LEVELS}} | asdict(report)


def _as_markdown(report: Report) -> str:
    ordered = [row for level in LEVELS for row in report.rows if row.level == level]
    findings = [(f"{row.rule} {row.title}", row.level, row.subject, row.detail) for row in ordered]
    overall = [(measure.name, str(measure), measure.note) for measure in report.overall]
    parts = [
        (part.name, f"{part.x:.2f}", f"{part.y:.2f}", f"{part.z:.2f}", f"{part.volume / 1000:.1f}")
        for part in report.printables
    ]
    statuses = [(status, str(count)) for status, count in report.status_counts.items()]
    to_measure = [(row["name"], row["value"], row["status"], row["file"], row["measure"]) for row in report.to_measure]
    sections = [
        "# Candybar layout check",
        f"Result: **{report.result}** ({_counts(report)})",
        "## Findings",
        _md_table(("Rule", "Level", "Subject", "Detail"), findings),
        "## Overall dimensions",
        _md_table(("Parameter", "Value", "Meaning"), overall),
        "## Printable parts",
        "Sizes are in each part's own frame.",
        _md_table(("Part", "X mm", "Y mm", "Z mm", "Volume cm3"), parts),
        "## Parameters by status",
        _md_table(("Status", "Count"), statuses),
        "## Still to measure",
        "Rows that name a measurement and are not yet marked `measured`.",
        _md_table(("Parameter", "Value now", "Status", "File", "What to measure"), to_measure),
    ]
    return "\n\n".join(sections) + "\n"


def _md_table(headings: tuple[str, ...], rows: list[tuple[str, ...]]) -> str:
    lines = [headings, tuple("---" for _ in headings), *rows]
    return "\n".join("| " + " | ".join(cell.replace("|", "\\|") for cell in line) + " |" for line in lines)
