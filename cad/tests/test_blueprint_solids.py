"""The solids of the blueprint: the profile of the band and of the panel outline, the guard on a cut (quick); and in the
slow group, the planar rear of revision 7 (decision record 0007) on the built shell, and one proof that the check of
the solids against the blueprint can still fail. cad/check.sh (tools.check_solids) checks the solids on every build."""
from __future__ import annotations

import math
import unittest
from dataclasses import replace

import FreeCAD as App
import Part

from candybar.shell import solids
from candybar.shell import profiles as pr
from candybar.shell.dims import Blueprint
from tools import check_solids

from . import support

V = App.Vector


def over(row: dict) -> bool:
    return max(row["solid_to_blueprint"], row["blueprint_to_solid"]) > check_solids.TOL


def failing(report: dict) -> set[str]:
    return {name for name, row in [*report["sections"].items(), *report["silhouettes"].items()] if over(row)}


@support.slow
class BlueprintSolidsTest(unittest.TestCase):
    """The check of the solids against the blueprint (tools.check_solids) can still fail: it notices a stronger arc of
    the rail. The check itself runs in cad/check.sh on every build."""

    def test_check_notices_a_stronger_rail_arc(self) -> None:
        d = Blueprint()
        changed = check_solids.run(solids.build(replace(d, rail_sagitta_ratio=d.rail_sagitta_ratio + 0.01)), d)
        self.assertFalse(changed["ok"])
        self.assertTrue(failing(changed), "no view or section fails")


def plan_points(shape: Part.Shape, z: float, keep, step: float = 0.05) -> list[App.Vector]:
    """The points of the level section of a solid at z that pass keep()."""
    return [p for w in shape.slice(V(0, 0, 1), z) for e in w.Edges for p in e.discretize(Distance=step) if keep(p)]


def face_at(shape: Part.Shape, point: App.Vector) -> Part.Face:
    """The face of a solid on which a point lies."""
    face = min(shape.Faces, key=lambda f: f.distToShape(Part.Vertex(point))[0])
    if face.distToShape(Part.Vertex(point))[0] > 0.01:
        raise AssertionError(f"no face at {point}")
    return face


class BandStrokeTest(unittest.TestCase):
    """Revision 7: the band's stroke is straight lines (the profile alone, no build)."""

    def setUp(self) -> None:
        self.d = Blueprint()

    def test_the_stroke_is_four_straight_lines(self) -> None:
        d = self.d
        foot, stub, knee, top, end = pr.band_stroke(d)
        self.assertEqual(foot[0], stub[0])                                   # the stub stands upright
        self.assertAlmostEqual(stub[1], d.band_stub)
        self.assertAlmostEqual(math.degrees(math.atan2(stub[0] - knee[0], knee[1] - stub[1])), d.band_kick)
        self.assertAlmostEqual(knee[1], 85.2, delta=0.1)
        self.assertAlmostEqual(math.degrees(math.atan2(top[0] - knee[0], top[1] - knee[1])), d.band_lean)
        self.assertAlmostEqual(top[1], end[1])                               # the run is level
        self.assertAlmostEqual(top[1], d.rear_shelf_z0 + d.band_depth)


@support.slow
class PlanarRearTest(unittest.TestCase):
    """Revision 7 on the built shell: the band and the two facets under the head are planes, the rear goes straight
    across, the hand-holds print without support, and the corner lines of the head and the hood meet across the seam."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.d, parts, cls.log = support.shell()
        cls.body, cls.hood = parts["body"], parts["hood"]

    def test_each_piece_of_the_band_is_a_plane(self) -> None:
        d, hw = self.d, self.d.width / 2
        stroke = pr.band_stroke(d)
        for (y0, z0), (y1, z1) in zip(stroke[1:4], stroke[2:5]):
            length = math.hypot(y1 - y0, z1 - z0)
            ty, tz = (y1 - y0) / length, (z1 - z0) / length
            if z1 == z0:                                                     # the run: its facet ends on the hip
                y1 = d.body_d
            u = d.band_depth / 2                                                # half way in, square to the stroke
            point = V(hw - u, (y0 + y1) / 2 + u * tz, (z0 + z1) / 2 - u * ty)
            with self.subTest(at=(round(point.y), round(point.z))):
                self.assertIsInstance(face_at(self.body, point).Surface, Part.Plane)

    def test_the_two_facets_of_the_shelf_are_planes_at_45_degrees(self) -> None:
        d, rw, zc = self.d, self.d.rear_w / 2, self.d.rear_shelf_z0
        for point, normal in ((V(rw + 6, d.body_d - 20, zc + 6), V(1, 0, -1)), (V(0, d.body_d + 20, zc + 20), V(0, 1, -1))):
            normal.normalize()
            surface = face_at(self.body, point).Surface
            self.assertIsInstance(surface, Part.Plane)
            self.assertAlmostEqual(abs(surface.Axis.dot(normal)), 1.0, places=6)

    def test_the_rear_goes_straight_across(self) -> None:
        d = self.d
        for z, y in ((150.0, d.body_d), (d.rear_shelf_z1 + 10.0, d.depth)):
            pts = plan_points(self.body, z, lambda p: abs(p.x) < 60 and p.y > d.body_d - 5, 1.0)
            self.assertTrue(pts)
            self.assertLess(max(abs(p.y - y) for p in pts), 1e-6, msg=f"z {z}")

    def test_nothing_in_the_hand_holds_faces_down_flatter_than_45_degrees(self) -> None:
        d = self.d
        worst = 90.0
        for f in self.body.Faces:
            b = f.BoundBox
            if not (b.XMin > d.grip_x0 - 2 and b.XMax < d.grip_x1 + 2 and b.YMin > d.depth - d.grip_depth - 2 and b.ZMin > d.grip_z0 - 2
                    and b.ZMax < d.grip_z0 + d.grip_h + 2):
                continue
            u0, u1, v0, v1 = f.ParameterRange
            for i in range(21):
                for j in range(21):
                    uv = (u0 + (u1 - u0) * i / 20, v0 + (v1 - v0) * j / 20)
                    n = f.normalAt(*uv)
                    if n.z < -1e-6 and f.isInside(f.valueAt(*uv), 1e-3, True):
                        worst = min(worst, math.degrees(math.acos(min(1.0, -n.z))))
        self.assertGreaterEqual(worst, 45.0 - 0.01)

    def test_the_corner_lines_of_the_head_and_the_hood_meet_across_the_seam(self) -> None:
        """Each corner read 0.05 and 10 from its side of the seam groove and carried to the middle of the seam: the
        two corner points within 0.3."""
        d = self.d
        zm = d.body_top + d.seam_gap / 2

        def read(s: Part.Shape, z: float) -> tuple[float, float]:
            pts = plan_points(s, z, lambda q: q.x > 150 and q.y > 520, 0.01)
            xs = max(q.x for q in pts if abs(q.y - 560) < 0.05)
            yr = max(q.y for q in pts if abs(q.x - 215) < 0.05)
            dg = max((q.x - xs) + (q.y - yr) for q in pts)
            return xs + dg / 2, yr + dg / 2

        def at_middle(s: Part.Shape, z0: float, z1: float) -> tuple[float, float]:
            p0, p1 = read(s, z0), read(s, z1)
            return tuple(p0[i] + (p0[i] - p1[i]) / (z0 - z1) * (zm - z0) for i in range(2))

        g = d.seam_groove
        body = at_middle(self.body, d.body_top - g - 0.05, d.body_top - g - 10)
        hood = at_middle(self.hood, d.body_top + d.seam_gap + g + 0.05, d.body_top + d.seam_gap + g + 10)
        self.assertLess(math.dist(body, hood), 0.3)

class LazySolid:
    """A solid whose cut takes nothing off, as a cut by a loft can."""

    def __init__(self, shape: Part.Shape) -> None:
        self.shape, self.Volume, self.Solids = shape, shape.Volume, shape.Solids

    def isValid(self) -> bool:
        return True

    def cut(self, tools: object) -> "LazySolid":
        return self

    def common(self, tool: Part.Shape) -> Part.Shape:
        return self.shape.common(tool)


class CutCheckTest(unittest.TestCase):
    """The guard on a cut by several tools: it stops a result in which a tool did no work."""

    def setUp(self) -> None:
        self.box = Part.makeBox(40, 40, 40)
        self.tools = [Part.makeBox(10, 10, 10, V(-5, -5, -5)), Part.makeBox(10, 10, 10, V(35, 35, 35))]

    def test_a_cut_that_does_its_work_passes(self) -> None:
        self.assertAlmostEqual(solids.cut_checked(self.box, self.tools, "test").Volume, 40 ** 3 - 2 * 125)

    def test_a_result_with_a_tool_left_in_it_is_an_error(self) -> None:
        with self.assertRaises(Part.OCCError):
            solids.cut_checked(LazySolid(self.box), self.tools, "test")


class PanelOutlineTest(unittest.TestCase):
    """The front of the control panel follows the deck's front contour at one border; the faces use the outline."""

    def test_front_follows_the_deck_contour_at_one_border(self) -> None:
        d = Blueprint()
        out = pr.panel_outline(d)
        self.assertEqual(len(out), 6)
        a = math.radians(d.deck_flank)
        xc = d.deck_centre_frac * d.width / 2
        border = d.deck_nose + d.panel_gap
        # the centre segment on the line of the centre face, moved back by the border
        self.assertAlmostEqual(out[1][1], border)
        self.assertAlmostEqual(out[2][1], border)
        # each corner on the line of its flank, moved back by the border, square to the flank
        for px, py in (out[0], out[3]):
            self.assertAlmostEqual((py - (abs(px) - xc) * math.tan(a)) * math.cos(a), border)
            self.assertAlmostEqual(abs(px), d.panel_w / 2)
        self.assertGreater(out[3][1] - out[2][1], 8.0)
        self.assertAlmostEqual(out[4][1], border + d.panel_d)

    def test_pocket_stands_panel_gap_outside_the_plate_on_every_edge(self) -> None:
        d = Blueprint()
        plate, pocket = pr.panel_outline(d), pr.panel_outline(d, d.panel_gap)
        for (p, q), r in zip(zip(plate, plate[1:] + plate[:1]), pocket):
            nx, ny = q[1] - p[1], -(q[0] - p[0])
            k = math.hypot(nx, ny)
            # the pocket corner at the start of the edge lies panel_gap outside the line of the edge
            self.assertAlmostEqual(((r[0] - p[0]) * nx + (r[1] - p[1]) * ny) / k, d.panel_gap)

    def test_faces_of_the_panel_and_the_pocket_use_the_outline(self) -> None:
        d = Blueprint()
        f = pr.faces(d)
        (plate,) = f["CP1"].polys
        self.assertEqual([(x, y) for x, y, _ in plate], pr.panel_outline(d))
        rim = {(round(x, 6), round(y, 6)) for q in f["DK8"].polys for x, y, z in q if abs(z - d.deck_top) < 1e-9}
        self.assertEqual(rim, {(round(x, 6), round(y, 6)) for x, y in pr.panel_outline(d, d.panel_gap)})


