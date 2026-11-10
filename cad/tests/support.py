from __future__ import annotations

import atexit
import contextlib
import csv
import functools
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterator

import FreeCAD as App
import Part

from candybar import build, check, model, params

CAD = Path(__file__).resolve().parents[1]
PARAMS = CAD / "params"
BUILD = CAD / "build.sh"
FREECAD_RUN = CAD / "candybar" / "freecad-run.sh"


def temp_dir() -> Path:
    path = Path(tempfile.mkdtemp(prefix="candybar-test-"))
    atexit.register(shutil.rmtree, path, ignore_errors=True)
    return path


@functools.cache
def baseline() -> tuple[Path, check.Report]:
    out = temp_dir()
    return out, build.run(PARAMS, out, renders=False)


def shell_build(params_dir: Path, extra_env: dict[str, str] | None = None) -> tuple[subprocess.CompletedProcess[str], Path]:
    out = temp_dir()
    env = os.environ | {"CANDYBAR_PARAMS": str(params_dir), "CANDYBAR_OUT": str(out)} | (extra_env or {})
    return subprocess.run([str(BUILD), "--no-render"], env=env, capture_output=True, text=True), out


@functools.cache
def shell_baseline() -> tuple[subprocess.CompletedProcess[str], Path]:
    return shell_build(PARAMS)


@contextlib.contextmanager
def saved_document() -> Iterator[App.Document]:
    out, _ = baseline()
    doc = App.openDocument(str(out / f"{build.DOCUMENT}.FCStd"))
    try:
        yield doc
    finally:
        App.closeDocument(doc.Name)


def params_copy(overrides: dict[str, str]) -> Path:
    folder = temp_dir()
    pending = dict(overrides)
    for filename in params.FILES:
        with (PARAMS / filename).open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            row["value"] = pending.pop(row["name"], row["value"])
        with (folder / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, params.COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
    if pending:
        raise KeyError(f"no parameter rows named {sorted(pending)}")
    return folder


def edit(doc: App.Document, **values: float) -> None:
    for name, number in values.items():
        params.edit(doc, name, number)
    doc.recompute()


def solids(doc: App.Document) -> dict[str, model.Placed]:
    return {solid.name: solid for solid in model.placed(doc)}


def hole_centres(shape: Part.Shape, diameter: float) -> list[tuple[float, float]]:
    return sorted(
        {
            (round(face.Surface.Center.x, 6), round(face.Surface.Center.y, 6))
            for face in shape.Faces
            if isinstance(face.Surface, Part.Cylinder) and abs(2 * face.Surface.Radius - diameter) < 1e-6
        }
    )


def underside_z(shape: Part.Shape) -> float:
    looking_down = [face for face in shape.Faces if isinstance(face.Surface, Part.Plane) and face.normalAt(0, 0).z < -0.99]
    return max(looking_down, key=lambda face: face.Area).CenterOfMass.z


def fail_rows(report: check.Report, *rules: str) -> set[tuple[str, str]]:
    return {(row.rule, row.subject) for row in report.rows if row.level == check.FAIL and (not rules or row.rule in rules)}
