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


# ---------- the cache of the shell and the cavity on disk ----------
# support.shell() and support.cavity() take minutes, and each test process made them again. They are kept on disk,
# as the skin of the split is: binary BREP (which keeps every number as it is), under a key of everything that makes
# them: the values of Blueprint(), the source of the modules that build them, and the versions of FreeCAD and
# OpenCascade. CANDYBAR_TEST_CACHE sets the folder (default cad/out/test-cache); CANDYBAR_TEST_CACHE=off makes them
# in the process, as before. A file is written to a temporary name and then renamed, so that processes that run at the
# same time never read half a file.
SHELL_SOURCES = ("dims.py", "profiles.py", "solids.py")
CAVITY_SOURCES = (*SHELL_SOURCES, "cavity.py")


def cache_key(sources: tuple[str, ...]) -> str:
    import hashlib

    import FreeCAD

    h = hashlib.sha256(repr(Blueprint()).encode())
    h.update(repr(FreeCAD.Version()).encode())
    h.update(Part.OCC_VERSION.encode() if hasattr(Part, "OCC_VERSION") else b"")
    for name in sources:
        h.update((CAD / "candybar" / "shell" / name).read_bytes())
    return h.hexdigest()[:16]


def cache_dir() -> Path | None:
    where = os.environ.get("CANDYBAR_TEST_CACHE", "")
    return None if where == "off" else Path(where or CAD / "out" / "test-cache")


def write_atomic(path: Path, write) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    write(temp)
    os.replace(temp, path)


def read_shapes(path: Path) -> list[Part.Shape]:
    compound = Part.Shape()
    compound.importBinary(str(path))
    return list(compound.childShapes())


def write_shapes(path: Path, shapes: list[Part.Shape]) -> None:
    write_atomic(path, lambda temp: Part.makeCompound(shapes).exportBinary(str(temp)))


@functools.cache
def shell() -> tuple[Blueprint, dict[str, Part.Shape], tuple[str, ...]]:
    """The default build of the shell (candybar.shell.solids), made once for all the tests that read it: the
    dimensions, the parts by name, and the lines of the build's log. Kept on disk (see cache_key)."""
    import json

    d = Blueprint()
    folder = cache_dir()
    if folder is not None:
        key = cache_key(SHELL_SOURCES)
        shapes, meta = folder / f"shell-{key}.bin", folder / f"shell-{key}.json"
        if shapes.exists() and meta.exists():
            data = json.loads(meta.read_text(encoding="utf-8"))
            return d, dict(zip(data["names"], read_shapes(shapes))), tuple(data["log"])
    log: list[str] = []
    parts = shell_solids.build(d, log)
    if folder is not None:
        write_shapes(shapes, list(parts.values()))
        write_atomic(meta, lambda temp: temp.write_text(json.dumps({"names": list(parts), "log": log}), encoding="utf-8"))
    return d, parts, tuple(log)


@functools.cache
def cavity() -> shell_cavity.Cavity:
    """The cavity of the default build (candybar.shell.cavity), made once for all the tests that read it. It takes
    some minutes to make. Kept on disk (see cache_key): its pieces, its walls, and its slabs as numbers and shapes."""
    import json

    folder = cache_dir()
    if folder is not None:
        key = cache_key(CAVITY_SOURCES)
        shapes, meta = folder / f"cavity-{key}.bin", folder / f"cavity-{key}.json"
        if shapes.exists() and meta.exists():
            data = json.loads(meta.read_text(encoding="utf-8"))
            found = read_shapes(shapes)
            take = lambda i: None if i is None else found[i]
            return shell_cavity.Cavity([found[i] for i in data["pieces"]], [found[i] for i in data["walls"]],
                                       [(x0, x1, take(a), take(b)) for x0, x1, a, b in data["slabs"]])
    d, parts, _ = shell()
    cav = shell_cavity.build(parts, d)
    if folder is not None:
        found: list[Part.Shape] = []

        def put(shape):
            if shape is None:
                return None
            found.append(shape)
            return len(found) - 1

        data = {"pieces": [put(s) for s in cav.pieces], "walls": [put(s) for s in cav.walls],
                "slabs": [(x0, x1, put(a), put(b)) for x0, x1, a, b in cav.slabs]}
        write_shapes(shapes, found)
        write_atomic(meta, lambda temp: temp.write_text(json.dumps(data), encoding="utf-8"))
    return cav


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
