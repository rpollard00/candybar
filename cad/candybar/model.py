"""FreeCAD mechanics: expression-bound assemblies, primitives, sketches and features, and role tags.

Every dimension is written as an expression of parameter names, for example
`"stick_x - stick_plate_w / 2"`. `Model.expr` qualifies the names against the
`Params` sheet, and the result is bound with `setExpression`, so the saved
document follows later edits of the sheet.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Sequence

import FreeCAD as App
import Part
import Sketcher

from . import params

ROLES = ("hardware", "protrusion", "keepout", "massing", "trim", "printable")
ZERO = "0"

Triple = tuple[str, str, str]
Axis = tuple[float, float, float]
ORIGIN: Triple = (ZERO, ZERO, ZERO)
X_AXIS: Axis = (1.0, 0.0, 0.0)
Y_AXIS: Axis = (0.0, 1.0, 0.0)
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
class Corner:
    """One corner of a sketched outline. A `radius` rounds it, and must then stay above zero."""

    name: str
    x: str
    y: str
    radius: str = ZERO


class Side(Enum):
    """Which way a pad or a pocket goes from its sketch plane."""

    ALONG_NORMAL = "along the sketch normal"
    AGAINST_NORMAL = "against the sketch normal"


@dataclass(frozen=True)
class Placed:
    name: str
    role: str
    owner: str
    tag: str
    alternate: bool
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

    def common(self, parent: App.DocumentObject, name: str, shapes: Sequence[App.DocumentObject]) -> App.DocumentObject:
        obj = _new(parent, "Part::MultiCommon", name)
        obj.Shapes = list(shapes)
        return obj

    def fuse(self, parent: App.DocumentObject, name: str, shapes: Sequence[App.DocumentObject]) -> App.DocumentObject:
        obj = _new(parent, "Part::MultiFuse", name)
        obj.Shapes = list(shapes)
        return obj

    def sketch(self, parent: App.DocumentObject, name: str, plane: str, offset: str = ZERO) -> Sketch:
        """A sketch on an origin plane of a Body or Part, `offset` along the plane normal."""
        obj = _new(parent, "Sketcher::SketchObject", name)
        support = next(feature for feature in parent.Origin.OriginFeatures if feature.Role == plane)
        obj.AttachmentSupport = [(support, "")]
        obj.MapMode = "FlatFace"
        self.bind(obj, "AttachmentOffset.Base.z", offset)
        return Sketch(self, obj)

    def posed_sketch(self, parent: App.DocumentObject, name: str, base: Triple, pose: Pose) -> Sketch:
        """A sketch on a plane of its own: the parent's XY plane turned by `pose`, then moved to `base`."""
        obj = _new(parent, "Sketcher::SketchObject", name)
        self.pose(obj, base, pose)
        return Sketch(self, obj)

    def offset(
        self, parent: App.DocumentObject, name: str, outline: App.DocumentObject, distance: str
    ) -> App.DocumentObject:
        """A flat closed outline moved sideways by `distance`: outward when positive, inward when negative."""
        obj = _new(parent, "Part::Offset2D", name)
        obj.Source = outline
        obj.Join = "Intersection"
        self.bind(obj, "Value", distance)
        return obj

    def extrusion(
        self, parent: App.DocumentObject, name: str, outline: App.DocumentObject, axis: Axis, length: str, at: Triple = ORIGIN
    ) -> App.DocumentObject:
        """A flat outline made solid: `length` along `axis` of the parent frame, then moved by `at`."""
        obj = _new(parent, "Part::Extrusion", name)
        obj.Base = outline
        obj.DirMode = "Custom"
        obj.Dir = App.Vector(*axis)
        obj.Solid = True
        self.bind(obj, "LengthFwd", length)
        self.place(obj, at)
        return obj

    def slab(self, parent: App.DocumentObject, name: str, outline: App.DocumentObject, thickness: str) -> App.DocumentObject:
        """A flat outline made solid: `thickness` in total, half on each side of its plane."""
        obj = _new(parent, "Part::Extrusion", name)
        obj.Base = outline
        obj.DirMode = "Normal"
        obj.Symmetric = True
        obj.Solid = True
        self.bind(obj, "LengthFwd", thickness)
        return obj

    def pad(self, body: App.DocumentObject, name: str, profile: Sketch, length: str, side: Side) -> App.DocumentObject:
        obj = _new(body, "PartDesign::Pad", name)
        obj.Profile = profile.obj
        # FreeCAD pads along the sketch normal unless reversed.
        obj.Reversed = side is Side.AGAINST_NORMAL
        self.bind(obj, "Length", length)
        return obj

    def pocket(
        self, body: App.DocumentObject, name: str, profile: Sketch, depth: str | None, side: Side
    ) -> App.DocumentObject:
        """A pocket `depth` deep, or through everything when `depth` is None."""
        obj = _new(body, "PartDesign::Pocket", name)
        obj.Profile = profile.obj
        # FreeCAD pockets against the sketch normal unless reversed: the opposite of a pad.
        obj.Reversed = side is Side.ALONG_NORMAL
        if depth is None:
            obj.Type = "ThroughAll"
        else:
            self.bind(obj, "Length", depth)
        return obj


class Sketch:
    """A sketch whose dimensions are named constraints bound to the parameter sheet.

    Geometry is seeded at the evaluated values, so the solver starts from a
    solved state and a later parameter edit only has to move it.
    """

    _H_AXIS = -1
    _V_AXIS = -2
    _ORIGIN = (-1, 1)
    _START = 1
    _END = 2
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

    def rectangle(self, x0: str, x1: str, y0: str, y1: str, name: str = "") -> None:
        """An upright rectangle. `name` tells the constraints of several rectangles in one sketch apart."""
        number = self._model.number
        left, right, low, high = number(x0), number(x1), number(y0), number(y1)
        corners = [App.Vector(x, y, 0) for x, y in ((left, low), (right, low), (right, high), (left, high))]
        first = self.obj.GeometryCount
        for index in range(4):
            self.obj.addGeometry(Part.LineSegment(corners[index], corners[(index + 1) % 4]), False)
        for index, kind in enumerate(("Horizontal", "Vertical", "Horizontal", "Vertical")):
            edge, following = first + index, first + (index + 1) % 4
            self.obj.addConstraint(Sketcher.Constraint("Coincident", edge, self._END, following, self._START))
            self.obj.addConstraint(Sketcher.Constraint(kind, edge))
        self._pin(f"{name}min", first, self._START, x0, y0)
        self._pin(f"{name}max", first + 2, self._START, x1, y1)

    def polygon(self, corners: Sequence[Corner]) -> None:
        """A closed outline through the corners in order, every corner pinned, rounded where it has a radius.

        A rounded corner keeps its sharp position as a construction point, so
        the same two parameters place it whatever its radius is. The arcs at
        the two ends of an edge must fit on it: when they do not, the sketch
        cannot be solved and `errors` reports it.
        """
        number = self._model.number
        points = [App.Vector(number(corner.x), number(corner.y), 0) for corner in corners]
        count = len(corners)
        trims = [
            _trim(points[index - 1], points[index], points[(index + 1) % count], number(corner.radius))
            for index, corner in enumerate(corners)
        ]
        first = self.obj.GeometryCount
        for index in range(count):
            self.obj.addGeometry(Part.LineSegment(trims[index].leave, trims[(index + 1) % count].enter), False)
        for index, (corner, trim) in enumerate(zip(corners, trims, strict=True)):
            before, after = first + (index - 1) % count, first + index
            if trim.centre is None:
                self.obj.addConstraint(Sketcher.Constraint("Coincident", before, self._END, after, self._START))
                self._pin(corner.name, after, self._START, corner.x, corner.y)
            else:
                self._round(corner, trim, before, after)

    def _round(self, corner: Corner, trim: _Trim, before: int, after: int) -> None:
        """The arc of a rounded corner, tangent to the edges `before` and `after` it."""
        enter_angle, leave_angle = (_angle(trim.centre, point) for point in (trim.enter, trim.leave))
        circle = Part.Circle(trim.centre, App.Vector(0, 0, 1), trim.radius)
        # A sketch arc always runs counter-clockwise from its start to its end.
        if trim.turns_left:
            arc = self.obj.addGeometry(Part.ArcOfCircle(circle, enter_angle, leave_angle), False)
            at_enter, at_leave = self._START, self._END
        else:
            arc = self.obj.addGeometry(Part.ArcOfCircle(circle, leave_angle, enter_angle), False)
            at_enter, at_leave = self._END, self._START
        self.obj.addConstraint(Sketcher.Constraint("Tangent", before, self._END, arc, at_enter))
        self.obj.addConstraint(Sketcher.Constraint("Tangent", arc, at_leave, after, self._START))
        self._dimension(f"{corner.name}_r", Sketcher.Constraint("Radius", arc, trim.radius), corner.radius)
        sharp = self.obj.addGeometry(Part.Point(trim.sharp), True)
        self._pin(corner.name, sharp, self._START, corner.x, corner.y)
        for edge in (before, after):
            self.obj.addConstraint(Sketcher.Constraint("PointOnObject", sharp, self._START, edge))

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


@dataclass(frozen=True)
class _Trim:
    """Where an outline enters and leaves one corner. A sharp corner has no centre."""

    sharp: App.Vector
    enter: App.Vector
    leave: App.Vector
    centre: App.Vector | None = None
    radius: float = 0.0
    turns_left: bool = False


def _trim(before: App.Vector, at: App.Vector, after: App.Vector, radius: float) -> _Trim:
    """The arc of `radius` tangent to both edges that meet at the corner `at`, or the sharp corner itself."""
    if radius == 0:
        return _Trim(at, at, at)
    back = (before - at).normalize()
    ahead = (after - at).normalize()
    half_angle = back.getAngle(ahead) / 2
    setback = radius / math.tan(half_angle)
    centre = at + (back + ahead).normalize() * (radius / math.sin(half_angle))
    return _Trim(at, at + back * setback, at + ahead * setback, centre, radius, turns_left=back.cross(ahead).z < 0)


def _angle(centre: App.Vector, point: App.Vector) -> float:
    return math.atan2(point.y - centre.y, point.x - centre.x)


def _new(parent: App.Document | App.DocumentObject, type_id: str, name: str) -> App.DocumentObject:
    obj = parent.addObject(type_id, name) if isinstance(parent, App.Document) else parent.newObject(type_id, name)
    if obj.Name != name:
        raise ValueError(f"object name {name!r} is already taken")
    return obj


def tag(obj: App.DocumentObject, role: str, owner: str, kind: str = "", alternate: bool = False) -> None:
    """Mark a solid with its role and owner. An `alternate` stands in for another solid and is hidden by default."""
    if role not in ROLES:
        raise ValueError(f"{obj.Name}: unknown role {role!r}")
    for prop, text in (("CB_Role", role), ("CB_Owner", owner), ("CB_Tag", kind)):
        if text:
            obj.addProperty("App::PropertyString", prop, _GROUP)
            setattr(obj, prop, text)
    if alternate:
        obj.addProperty("App::PropertyBool", "CB_Alternate", _GROUP)
        obj.CB_Alternate = True


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
                alternate=getattr(obj, "CB_Alternate", False),
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
    """Objects that failed to recompute, tagged objects that are not one valid solid, loose sketches."""
    found: list[tuple[str, str]] = []
    for obj in doc.Objects:
        if not obj.isValid():
            found.append((obj.Name, obj.getStatusString()))
        elif "CB_Role" in obj.PropertiesList and not _is_one_solid(obj.Shape):
            found.append((obj.Name, "not one valid solid"))
        elif obj.isDerivedFrom("Sketcher::SketchObject") and (freedom := obj.solve()) != 0:
            found.append((obj.Name, f"not fully constrained (solver result {freedom})"))
    return found


def _is_one_solid(shape: Part.Shape) -> bool:
    return not shape.isNull() and shape.isValid() and len(shape.Solids) == 1 and shape.Volume > 0
