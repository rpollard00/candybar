"""FreeCAD mechanics: expression-bound assemblies, primitives, sketches and features, and role tags.

Every dimension is written as an expression of parameter names, for example
`"stick_x - stick_plate_w / 2"`. `Model.expr` qualifies the names against the
`Params` sheet, and the result is bound with `setExpression`, so the saved
document follows later edits of the sheet.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Sequence

import FreeCAD as App
import Part
import Sketcher

from . import params

ROLES = ("hardware", "protrusion", "keepout", "massing", "printable")
ZERO = "0"

Triple = tuple[str, str, str]

_UNITS = frozenset({"mm", "deg"})
_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_GROUP = "Candybar"


@dataclass(frozen=True)
class Prim:
    """One primitive solid in its assembly's frame. `role` is empty for a tool shape."""

    name: str
    role: str
    kind: str
    size: tuple[str, ...]
    at: Triple
    tag: str = ""


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


@dataclass(frozen=True)
class Assembly:
    """An `App::Part` with a bound placement. A text `angle` is bound; a number is fixed degrees."""

    name: str
    base: Triple
    axis: tuple[float, float, float] = (0.0, 0.0, 1.0)
    angle: str | float = 0.0
    prims: tuple[Prim, ...] = ()


@dataclass(frozen=True)
class Placed:
    name: str
    role: str
    owner: str
    tag: str
    print_axis: str
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

    def assembly(self, spec: Assembly, parent: App.DocumentObject | None = None) -> App.DocumentObject:
        part = _new(parent or self.doc, "App::Part", spec.name)
        bound = isinstance(spec.angle, str)
        degrees = self.number(spec.angle) if bound else spec.angle
        part.Placement = App.Placement(App.Vector(), App.Rotation(App.Vector(*spec.axis), degrees))
        if bound:
            self.bind(part, "Placement.Rotation.Angle", spec.angle)
        self.place(part, spec.base)
        for prim in spec.prims:
            self.solid(part, prim, spec.name)
        return part

    def solid(self, parent: App.DocumentObject, prim: Prim, owner: str) -> App.DocumentObject:
        type_id, props = _KINDS[prim.kind]
        obj = _new(parent, type_id, prim.name)
        for prop, text in zip(props, prim.size, strict=True):
            self.bind(obj, prop, f"({text}) / 2" if prop == "Radius" else text)
        self.place(obj, prim.at)
        if prim.role:
            tag(obj, prim.role, owner, prim.tag)
        return obj

    def body(self, parent: App.DocumentObject, name: str, owner: str) -> App.DocumentObject:
        """An empty PartDesign body, tagged as a printable part."""
        obj = _new(parent, "PartDesign::Body", name)
        tag(obj, "printable", owner)
        return obj

    def cut(
        self, parent: App.DocumentObject, name: str, base: App.DocumentObject, tool: App.DocumentObject
    ) -> App.DocumentObject:
        obj = _new(parent, "Part::Cut", name)
        obj.Base = base
        obj.Tool = tool
        return obj

    def sketch(self, parent: App.DocumentObject, name: str, plane: str, offset: str = ZERO) -> Sketch:
        """A sketch on an origin plane of a Body or Part, `offset` along the plane normal."""
        obj = _new(parent, "Sketcher::SketchObject", name)
        support = next(feature for feature in parent.Origin.OriginFeatures if feature.Role == plane)
        obj.AttachmentSupport = [(support, "")]
        obj.MapMode = "FlatFace"
        self.bind(obj, "AttachmentOffset.Base.z", offset)
        return Sketch(self, obj)

    def extrusion(
        self, parent: App.DocumentObject, name: str, profile: Sketch, length: str, at: Triple
    ) -> App.DocumentObject:
        """The sketch extruded along its normal, then moved by `at`."""
        obj = _new(parent, "Part::Extrusion", name)
        obj.Base = profile.obj
        obj.DirMode = "Normal"
        obj.Solid = True
        self.bind(obj, "LengthFwd", length)
        self.place(obj, at)
        return obj

    def pad(
        self, body: App.DocumentObject, name: str, profile: Sketch, length: str, reversed_: bool
    ) -> App.DocumentObject:
        obj = _new(body, "PartDesign::Pad", name)
        obj.Profile = profile.obj
        obj.Reversed = reversed_
        self.bind(obj, "Length", length)
        return obj

    def pocket(
        self, body: App.DocumentObject, name: str, profile: Sketch, depth: str | None, reversed_: bool
    ) -> App.DocumentObject:
        """A pocket `depth` deep, or through everything when `depth` is None."""
        obj = _new(body, "PartDesign::Pocket", name)
        obj.Profile = profile.obj
        obj.Reversed = reversed_
        if depth is None:
            obj.Type = "ThroughAll"
        else:
            self.bind(obj, "Length", depth)
        return obj


class Sketch:
    """A sketch whose dimensions are named constraints bound to the parameter sheet."""

    _H_AXIS = -1
    _V_AXIS = -2
    _ORIGIN = (-1, 1)
    _CENTRE = 3

    def __init__(self, model: Model, obj: App.DocumentObject) -> None:
        self._model = model
        self.obj = obj

    def circle(self, name: str, x: str, y: str, diameter: str) -> None:
        number = self._model.number
        centre = App.Vector(number(x), number(y), 0)
        geo = self.obj.addGeometry(Part.Circle(centre, App.Vector(0, 0, 1), number(diameter) / 2), False)
        self._dimension(f"{name}_d", Sketcher.Constraint("Diameter", geo, number(diameter)), diameter)
        self._pin(name, geo, self._CENTRE, x, y)

    def rectangle(self, x0: str, x1: str, y0: str, y1: str) -> None:
        number = self._model.number
        left, right, low, high = number(x0), number(x1), number(y0), number(y1)
        first = self._closed_polyline([(left, low), (right, low), (right, high), (left, high)])
        for offset, kind in enumerate(("Horizontal", "Vertical", "Horizontal", "Vertical")):
            self.obj.addConstraint(Sketcher.Constraint(kind, first + offset))
        self._pin("min", first, 1, x0, y0)
        self._pin("max", first + 2, 1, x1, y1)

    def polygon(self, corners: Sequence[tuple[str, str, str]]) -> None:
        """A closed outline through named corners `(name, x, y)`, every corner pinned."""
        number = self._model.number
        first = self._closed_polyline([(number(x), number(y)) for _, x, y in corners])
        for offset, (name, x, y) in enumerate(corners):
            self._pin(name, first + offset, 1, x, y)

    def _closed_polyline(self, points: Sequence[tuple[float, float]]) -> int:
        first = self.obj.GeometryCount
        count = len(points)
        vectors = [App.Vector(x, y, 0) for x, y in points]
        for start, end in zip(vectors, vectors[1:] + vectors[:1]):
            self.obj.addGeometry(Part.LineSegment(start, end), False)
        for offset in range(count):
            self.obj.addConstraint(Sketcher.Constraint("Coincident", first + offset, 2, first + (offset + 1) % count, 1))
        return first

    def _pin(self, name: str, geo: int, point: int, x: str, y: str) -> None:
        for suffix, kind, text, axis in (("x", "DistanceX", x, self._V_AXIS), ("y", "DistanceY", y, self._H_AXIS)):
            if text == ZERO:
                self.obj.addConstraint(Sketcher.Constraint("PointOnObject", geo, point, axis))
            else:
                constraint = Sketcher.Constraint(kind, *self._ORIGIN, geo, point, self._model.number(text))
                self._dimension(f"{name}_{suffix}", constraint, text)

    def _dimension(self, name: str, constraint: Sketcher.Constraint, text: str) -> None:
        index = self.obj.addConstraint(constraint)
        self.obj.renameConstraint(index, name)
        self.obj.setExpression(f"Constraints.{name}", self._model.expr(text))


def _new(parent: App.Document | App.DocumentObject, type_id: str, name: str) -> App.DocumentObject:
    obj = parent.addObject(type_id, name) if isinstance(parent, App.Document) else parent.newObject(type_id, name)
    if obj.Name != name:
        raise ValueError(f"object name {name!r} is already taken")
    return obj


def tag(obj: App.DocumentObject, role: str, owner: str, kind: str = "") -> None:
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
                print_axis=getattr(obj, "CB_PrintAxis", "z"),
                world=world_shape(obj),
                assembly=obj.Shape,
                own=own,
            )
        )
    return found


def fingerprint(doc: App.Document) -> tuple[tuple[str | float, ...], ...]:
    """Name, volume and global bounding box of every tagged solid: equal while the geometry is unchanged."""

    def row(solid: Placed) -> tuple[str | float, ...]:
        box = solid.world.BoundBox
        numbers = (solid.world.Volume, box.XMin, box.YMin, box.ZMin, box.XMax, box.YMax, box.ZMax)
        return (solid.name, *(round(number, 6) for number in numbers))

    return tuple(row(solid) for solid in placed(doc))


def world_shape(obj: App.DocumentObject) -> Part.Shape:
    shape = obj.Shape.copy()
    shape.Placement = obj.getGlobalPlacement()
    return shape


def errors(doc: App.Document) -> list[tuple[str, str]]:
    """Objects that failed to recompute, tagged solids without a valid shape, loose sketches."""
    found: list[tuple[str, str]] = []
    for obj in doc.Objects:
        if not obj.isValid():
            found.append((obj.Name, obj.getStatusString()))
        elif "CB_Role" in obj.PropertiesList and not _is_solid(obj.Shape):
            found.append((obj.Name, "no valid solid shape"))
        elif obj.isDerivedFrom("Sketcher::SketchObject") and (freedom := obj.solve()) != 0:
            found.append((obj.Name, f"not fully constrained (solver result {freedom})"))
    return found


def _is_solid(shape: Part.Shape) -> bool:
    return not shape.isNull() and shape.isValid() and shape.Volume > 0

