from __future__ import annotations

import csv
import functools
import os
import shutil
import tempfile
from pathlib import Path

import Part

from candybar.shell import cavity as shell_cavity
from candybar.shell import params
from candybar.shell import solids as shell_solids
from candybar.shell.dims import Blueprint

CAD = Path(__file__).resolve().parents[1]
PARAMS = CAD / "params"
FREECAD_RUN = CAD / "candybar" / "freecad-run.sh"


_temp_dirs: list[Path] = []


def temp_dir() -> Path:
    path = Path(tempfile.mkdtemp(prefix="candybar-test-"))
    _temp_dirs.append(path)
    return path


def remove_temp_dirs() -> None:
    """Called by the runner: the launcher ends the process with os._exit, which skips atexit hooks."""
    while _temp_dirs:
        shutil.rmtree(_temp_dirs.pop(), ignore_errors=True)


@functools.cache
def shell() -> tuple[Blueprint, dict[str, Part.Shape], tuple[str, ...]]:
    """The default build of the shell (candybar.shell.solids), made once for all the tests that read it: the
    dimensions, the parts by name, and the lines of the build's log."""
    d = Blueprint()
    log: list[str] = []
    return d, shell_solids.build(d, log), tuple(log)


@functools.cache
def cavity() -> shell_cavity.Cavity:
    """The cavity of the default build (candybar.shell.cavity), made once for all the tests that read it. It takes
    some minutes to make."""
    d, parts, _ = shell()
    return shell_cavity.build(parts, d)


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


def hole_centres(shape: Part.Shape, diameter: float) -> list[tuple[float, float]]:
    """The (x, y) centres of the cylinder faces of the given diameter in a shape: its upright round holes."""
    return sorted(
        {
            (round(face.Surface.Center.x, 6), round(face.Surface.Center.y, 6))
            for face in shape.Faces
            if isinstance(face.Surface, Part.Cylinder) and abs(2 * face.Surface.Radius - diameter) < 1e-6
        }
    )
