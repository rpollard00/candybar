"""FreeCAD mechanics of the hardware items: assemblies of primitive solids that are bound to the parameter sheet, and
role tags.

Every dimension is written as an expression of parameter names, for example
`"stick_x - stick_plate_w / 2"`. `Model.expr` qualifies the names against the
`Params` sheet, and the result is bound with `setExpression`, so FreeCAD
calculates each size and position from the sheet.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Iterable

import FreeCAD as App
import Part

from . import params

ROLES = ("hardware", "protrusion", "keepout")
ZERO = "0"

Triple = tuple[str, str, str]
Axis = tuple[float, float, float]
ORIGIN: Triple = (ZERO, ZERO, ZERO)
X_AXIS: Axis = (1.0, 0.0, 0.0)
Z_AXIS: Axis = (0.0, 0.0, 1.0)

_UNITS = frozenset({"mm", "deg"})
_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_GROUP = "Candybar"


@dataclass(frozen=True)
class Prim:
    """One primitive solid in its assembly's frame. `role` is empty for a tool shape.

    `owner` names the part the solid belongs to, when that is not the whole assembly.
    """

    name: str
    role: str
    kind: str
    size: tuple[str, ...]
    at: Triple
    tag: str = ""
    owner: str = ""


def box(name: str, role: str, size: Triple, at: Triple) -> Prim:
    """Size along x, y, z; `at` is the corner with the lowest coordinates."""
    return Prim(name, role, "box", size, at)


def cyl(name: str, role: str, diameter: str, height: str, at: Triple, tag: str = "") -> Prim:
    """Axis along z; `at` is the centre of the bottom face."""
    return Prim(name, role, "cyl", (diameter, height), at, tag)


def ball(name: str, role: str, diameter: str, at: Triple) -> Prim:
    """`at` is the centre."""
    return Prim(name, role, "ball", (diameter,), at)


_KINDS: dict[str, tuple[str, tuple[str, ...]]] = {
    "box": ("Part::Box", ("Length", "Width", "Height")),
    "cyl": ("Part::Cylinder", ("Radius", "Height")),
    "ball": ("Part::Sphere", ("Radius",)),
}


def owned(part_name: str, prims: tuple[Prim, ...]) -> tuple[Prim, ...]:
    """The primitives as the solids of one purchased part, so that the checks compare one part with the next."""
    return tuple(replace(prim, owner=part_name) for prim in prims)


@dataclass(frozen=True)
class Pose:
    """A rotation about an axis of the parent frame. A text `angle` is bound; a number is fixed degrees."""

    axis: Axis = Z_AXIS
    angle: str | float = 0.0


def leaning_back(angle: str) -> Pose:
    """Upright, then tipped by `angle` so that the top moves toward the rear."""
    return Pose((-1.0, 0.0, 0.0), angle)


@dataclass(frozen=True)
class Assembly:
    """An `App::Part` with a bound placement."""

    name: str
    base: Triple
    pose: Pose = Pose()
    prims: tuple[Prim, ...] = ()


@dataclass(frozen=True)
class Placed:
    name: str
    role: str
    owner: str
    tag: str
    world: Part.Shape
    assembly: Part.Shape
    own: Part.Shape


class Model:
    def __init__(self, doc: App.Document, names: Iterable[str]) -> None:
        self.doc = doc
        self._names = frozenset(names)
        self._sheet = doc.getObject(params.SHEET)

    def expr(self, text: str) -> str:
        def qualify(match: re.Match[str]) -> str:
            word = match.group()
            if word in self._names:
                return f"{params.SHEET}.{word}"
            if word in _UNITS:
                return word
            raise KeyError(f"unknown parameter {word!r} in expression {text!r}")

        return _WORD.sub(qualify, text)

    def number(self, text: str) -> float:
        """Evaluate an expression through FreeCAD, in mm or degrees."""
        if text == ZERO:
            return 0.0
        result = self._sheet.evalExpression(self.expr(text))
        return float(getattr(result, "Value", result))

    def bind(self, obj: App.DocumentObject, prop: str, text: str) -> None:
        if text != ZERO:
            obj.setExpression(prop, self.expr(text))

    def place(self, obj: App.DocumentObject, at: Triple) -> None:
        for axis, text in zip("xyz", at, strict=True):
            self.bind(obj, f"Placement.Base.{axis}", text)

    def pose(self, obj: App.DocumentObject, base: Triple, pose: Pose) -> None:
        bound = isinstance(pose.angle, str)
        degrees = self.number(pose.angle) if bound else pose.angle
        obj.Placement = App.Placement(App.Vector(), App.Rotation(App.Vector(*pose.axis), degrees))
        if bound:
            self.bind(obj, "Placement.Rotation.Angle", pose.angle)
        self.place(obj, base)

    def assembly(self, spec: Assembly, parent: App.DocumentObject | None = None, owner: str = "") -> App.DocumentObject:
        """An `App::Part` with its solids. The solids of a sub-assembly belong to `owner`."""
        part = _new(parent or self.doc, "App::Part", spec.name)
        self.pose(part, spec.base, spec.pose)
        for prim in spec.prims:
            self.solid(part, prim, owner or spec.name)
        return part

    def solid(self, parent: App.DocumentObject, prim: Prim, owner: str) -> App.DocumentObject:
        type_id, props = _KINDS[prim.kind]
        obj = _new(parent, type_id, prim.name)
        for prop, text in zip(props, prim.size, strict=True):
            self.bind(obj, prop, f"({text}) / 2" if prop == "Radius" else text)
        self.place(obj, prim.at)
        if prim.role:
            tag(obj, prim.role, prim.owner or owner, prim.tag)
        return obj

def _new(parent: App.Document | App.DocumentObject, type_id: str, name: str) -> App.DocumentObject:
    obj = parent.addObject(type_id, name) if isinstance(parent, App.Document) else parent.newObject(type_id, name)
    if obj.Name != name:
        raise ValueError(f"object name {name!r} is already taken")
    return obj


def tag(obj: App.DocumentObject, role: str, owner: str, kind: str = "") -> None:
    """Mark a solid with its role and owner."""
    if role not in ROLES:
        raise ValueError(f"{obj.Name}: unknown role {role!r}")
    for prop, text in (("CB_Role", role), ("CB_Owner", owner), ("CB_Tag", kind)):
        if text:
            obj.addProperty("App::PropertyString", prop, _GROUP)
            setattr(obj, prop, text)


def placed(doc: App.Document) -> list[Placed]:
    """Every role-tagged object that has a shape, in document order."""
    found: list[Placed] = []
    for obj in doc.Objects:
        if "CB_Role" not in obj.PropertiesList or obj.Shape.isNull():
            continue
        own = obj.Shape.copy()
        own.Placement = App.Placement()
        found.append(
            Placed(
                name=obj.Name,
                role=obj.CB_Role,
                owner=obj.CB_Owner,
                tag=getattr(obj, "CB_Tag", ""),
                world=world_shape(obj),
                assembly=obj.Shape,
                own=own,
            )
        )
    return found


def world_shape(obj: App.DocumentObject) -> Part.Shape:
    shape = obj.Shape.copy()
    shape.Placement = obj.getGlobalPlacement()
    return shape


def errors(doc: App.Document) -> list[tuple[str, str]]:
    """Objects that failed to recompute, and tagged objects that are not one valid solid."""
    found: list[tuple[str, str]] = []
    for obj in doc.Objects:
        if not obj.isValid():
            found.append((obj.Name, obj.getStatusString()))
        elif "CB_Role" in obj.PropertiesList and not _is_one_solid(obj.Shape):
            found.append((obj.Name, "not one valid solid"))
    return found


def _is_one_solid(shape: Part.Shape) -> bool:
    return not shape.isNull() and shape.isValid() and len(shape.Solids) == 1 and shape.Volume > 0
