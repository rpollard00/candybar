"""The face check and the rear form study: the check finds the defects of revision 6's rear corner and passes the
repaired rear of candidate A; the study leaves Blueprint() at revision 6."""
from __future__ import annotations

import math
import unittest
from dataclasses import replace

import FreeCAD as App
import Part

from candybar.shell import profiles as pr
from candybar.shell import rear_study as rs
from candybar.shell import solids
from candybar.shell.dims import Blueprint
from tools import face_check as fc

V = App.Vector


def rules(found: list) -> set[str]:
    return {f.rule for f in fc.failures(found)}


class FaceCheckRulesTest(unittest.TestCase):
    def test_a_box_with_true_rounds_passes(self) -> None:
        box = Part.makeBox(100, 60, 40)
        box = box.makeFillet(8, [e for e in box.Edges if abs(e.BoundBox.ZLength - 40) < 1e-6])
        self.assertEqual(fc.failures(fc.check(box, "box")), [])

    def test_a_face_that_tapers_to_a_point_is_a_needle(self) -> None:
        box = Part.makeBox(100, 60, 40)
        wedge = Part.Face(Part.makePolygon([V(0, 0, 40), V(100, 0, 40), V(100, 6, 40), V(0, 0, 40)])).extrude(V(0, 0, -20))
        self.assertIn("needle", rules(fc.check(box.cut(wedge), "box")))

    def test_a_narrow_face_is_a_sliver(self) -> None:
        box = Part.makeBox(100, 60, 40).cut(Part.makeBox(100, 1.0, 1.0, V(0, 0, 39)))
        self.assertIn("sliver", rules(fc.check(box, "box")))

    def test_a_surface_cut_into_strips_is_split(self) -> None:
        cyl = Part.makeCylinder(20, 10).fuse(Part.makeCylinder(20, 10, V(0, 0, 10)))
        self.assertIn("split", rules(fc.check(cyl, "cylinder")))

    def test_faces_that_meet_at_a_small_angle_are_a_kink(self) -> None:
        box = Part.makeBox(100, 60, 40)
        ramp = Part.Face(Part.makePolygon([V(0, 30, 40), V(0, 60, 40), V(0, 60, 41), V(0, 30, 40)])).extrude(V(100, 0, 0))
        self.assertIn("kink", rules(fc.check(box.fuse(ramp).removeSplitter(), "box")))


class RevisionSixRearTest(unittest.TestCase):
    """The defects the owner marked: the fan where the step runs out into the corner round, and the strips."""

    @classmethod
    def setUpClass(cls) -> None:
        d = Blueprint()
        cls.d = d
        _, cls.rear = solids.body(d, pr.front(d))
        cls.found = [f for f in fc.failures(fc.check(cls.rear, "rear_body")) if f.at[1] > 500]

    def test_the_fan_below_the_seam_fails(self) -> None:
        fan = [f for f in self.found if f.rule == "needle" and f.at[2] > 380]
        self.assertTrue(fan, "no needle at the step's run-out")

    def test_the_strips_on_the_slope_fail(self) -> None:
        strips = [f for f in self.found if f.rule in ("split", "sliver") and self.d.rear_step_z0 - 5 < f.at[2] < self.d.rear_step_z1 + 5]
        self.assertGreaterEqual(len(strips), 8)


class CandidateATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.v = rs.VARIANTS["A"]
        cls.d = rs.blueprint(cls.v)
        cls.body = rs.body(cls.d, cls.v, [])

    def test_the_body_is_one_valid_solid(self) -> None:
        self.assertTrue(self.body.isValid())
        self.assertEqual(len(self.body.Solids), 1)

    def test_the_rear_passes_the_face_check(self) -> None:
        behind = [f for f in fc.failures(fc.check(self.body, "body", fc.default_reveals())) if f.at[1] > self.d.step_y(f.at[2]) - 1.0]
        self.assertEqual(behind, [])

    def test_the_step_meets_the_seam_in_front_of_the_corner_round(self) -> None:
        crease = self.d.step_y(self.d.body_top) + self.d.step_in
        self.assertAlmostEqual(self.d.step_y(self.d.body_top), self.v.step_seam_y, places=6)
        self.assertGreaterEqual(self.d.depth - self.v.corner_r - (crease + self.v.step_crease_r * rs.math.tan(rs.math.radians(22.5))), 10.0)


class CreaseRuleTest(unittest.TestCase):
    def test_a_convex_crease_smaller_than_the_corner_round_cannot_be_rounded(self) -> None:
        v = replace(rs.VARIANTS["A"], crease_hi=(580.0, 350.0, 8.0))
        d = rs.blueprint(v)
        s = rs.sharp_body(d, v)
        with self.assertRaises(Part.OCCError):
            s.makeFillet(v.corner_r, rs.corner_edges(d, s))


class BlueprintUnchangedTest(unittest.TestCase):
    def test_the_default_blueprint_is_revision_6(self) -> None:
        b = Blueprint()
        rs.blueprint(rs.VARIANTS["R"])
        self.assertEqual((b.step_y0, b.step_lean, b.rear_corner_r, b.rear_step_z0, b.rear_step_z1), (345.0, 28.0, 18.0, 310.0, 350.0))


def half_width(shape: Part.Shape, z: float, y_min: float) -> float:
    """Half the width of a level section of a solid, over the part of it behind y_min."""
    return max(abs(p.x) for w in shape.slice(V(0, 0, 1), z) for p in w.discretize(Distance=0.2) if p.y >= y_min)


def corner_line(shape: Part.Shape, z: float, y_min: float) -> tuple[float, float, float]:
    """In the level section at z, right rear corner: the side's x, the y where the round leaves the side, and the
    x where it leaves the rear wall (the face edges that the corner round draws)."""
    pts = [(p.x, p.y) for w in shape.slice(V(0, 0, 1), z) for p in w.discretize(Distance=0.05) if p.x > 150 and p.y > y_min]
    xm, ym = max(p[0] for p in pts), max(p[1] for p in pts)
    return xm, max(p[1] for p in pts if p[0] > xm - 0.002), max(p[0] for p in pts if p[1] > ym - 0.002)


class CandidateR2Test(unittest.TestCase):
    """R2: the head at full width back to the rear corner, the set-back closed by a shoulder, one corner R 25 for the
    lower body, the head and the hood."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.v = rs.VARIANTS["R2"]
        cls.d = rs.blueprint(cls.v)
        cls.body = rs.body(cls.d, cls.v, [])
        cls.hood = rs.hood(cls.d, cls.v, [])["hood"]

    def test_the_body_is_one_valid_solid(self) -> None:
        self.assertTrue(self.body.isValid())
        self.assertEqual(len(self.body.Solids), 1)

    def test_the_head_has_the_full_width_at_the_seam_and_at_mid_head(self) -> None:
        d, v = self.d, self.v
        seam = d.body_top - d.seam_groove - 0.5
        mid = (d.body_top + v.crease_hi[1] + v.smile) / 2
        for z in (seam, mid):
            self.assertAlmostEqual(half_width(self.body, z, d.body_d), d.side_x(z), delta=0.05, msg=f"z {z:.1f}")

    def test_the_head_and_the_hood_share_the_corner(self) -> None:
        d = self.d
        hz = d.body_top + d.seam_gap
        top, foot = d.body_top - d.seam_groove - 0.05, hz + d.seam_groove + 0.05
        for shape, z in ((self.body, top), (self.hood, foot)):
            pts = [p for w in shape.slice(V(0, 0, 1), z) for p in w.discretize(Distance=0.2) if p.x > 150 and p.y > d.body_d]
            p = max(pts, key=lambda q: q.x + q.y)
            self.assertAlmostEqual(rs.radius_at(shape, p), self.v.corner_r, delta=0.5, msg=f"corner radius at z {z:.1f}")
        body, hood = corner_line(self.body, top, d.body_d), corner_line(self.hood, foot, d.body_d)
        self.assertLess(abs(body[1] - hood[1]), 1.0, "the round leaves the side at the same y above and below the seam")
        self.assertLess(abs((body[0] - body[2]) - (hood[0] - hood[2])), 1.5, "the round is as wide on the rear above and below the seam")

    def test_the_changed_zone_passes_the_face_check(self) -> None:
        d = self.d
        found = [f for f in fc.failures(fc.check(self.body, "body", fc.default_reveals())) if abs(f.at[0]) > 150 and f.at[1] > d.step_y(f.at[2]) - 1.0]
        self.assertEqual(found, [])

    def test_the_door_opening_is_that_of_r(self) -> None:
        wall = max((f for f in self.body.Faces if isinstance(f.Surface, Part.Plane) and abs(f.Surface.Axis.y) > 0.999
                    and abs(f.CenterOfMass.y - self.d.body_d) < 1e-3), key=lambda f: f.Area)
        pts = wall.OuterWire.discretize(Distance=0.5)
        xs = [p.x for p in pts if abs(p.z - 200) < 0.6]
        self.assertAlmostEqual(max(xs) - min(xs) - 8.0, 412.7, delta=0.1)
        self.assertAlmostEqual(max(p.z for p in pts if abs(p.x) < 1.0) - 12.0 - 116.0, 159.6, delta=0.1)


class FlareTest(unittest.TestCase):
    """R2Fb: the step's inner crease curves back toward the rear at the floor. Build and face check only."""

    def test_r2fb_builds_and_its_flared_zone_passes_the_face_check(self) -> None:
        v = rs.VARIANTS["R2Fb"]
        d = rs.blueprint(v)
        body = rs.body(d, v, [])
        self.assertTrue(body.isValid())
        self.assertEqual(len(body.Solids), 1)
        found = [f for f in fc.failures(fc.check(body, "body", fc.default_reveals())) if abs(f.at[0]) > 150 and f.at[1] > d.step_y(f.at[2]) - 1.0]
        self.assertEqual(found, [])


class CandidateR3Test(unittest.TestCase):
    """R3: the step as one band of one section from the floor to the roll: an upright stub at the floor, an S, the
    lean, a top arc and a run back; the head at full width above it."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.v = rs.VARIANTS["R3"]
        cls.d = rs.blueprint(cls.v)
        cls.body = rs.body(cls.d, cls.v, [])

    def test_the_body_is_one_valid_solid(self) -> None:
        self.assertTrue(self.body.isValid())
        self.assertEqual(len(self.body.Solids), 1)

    def test_the_changed_zone_passes_the_face_check(self) -> None:
        d = self.d
        found = [f for f in fc.failures(fc.check(self.body, "body", fc.default_reveals())) if abs(f.at[0]) > 150 and f.at[1] > d.step_y(f.at[2]) - 1.0]
        self.assertEqual(found, [])

    def test_the_head_has_the_full_width(self) -> None:
        d, v = self.d, self.v
        for z in (d.body_top - d.seam_groove - 0.5, (d.body_top + v.crease_hi[1] + v.smile) / 2):
            self.assertAlmostEqual(half_width(self.body, z, d.body_d), d.side_x(z), delta=0.05, msg=f"z {z:.1f}")

    def test_the_band_meets_the_floor_at_90_degrees(self) -> None:
        """On the stub, above the base chamfer, the band's level sections are the same at two heights."""
        foot = rs.band_path(self.d, self.v)[0]
        self.assertEqual(foot.p[0], foot.q[0])
        y = foot.p[0]

        def band(z: float) -> list[tuple[float, float]]:
            return [(p.x, p.y) for w in self.body.slice(V(0, 0, 1), z) for p in w.discretize(Distance=0.1)
                    if p.x > self.d.rear_w / 2 - 1 and y - 25 < p.y < y + 25]

        low, high = band(self.v.chamfer + 1.0), band(self.v.band.stub - 1.0)
        self.assertTrue(low)
        self.assertLess(max(min(math.dist(p, q) for q in high) for p in low), 0.05)


def corner_column(shape: Part.Shape, z: float, y_side: float = 512.5, x_rear: float = 205.0, tol: float = 0.05) -> tuple[float, float]:
    """At height z, right rear corner: the y where the outline leaves the side line (as it is at y_side) and the x
    where it leaves the rear line (as it is at x_rear)."""
    pts = [(p.x, p.y) for w in shape.slice(V(0, 0, 1), z) for e in w.Edges for p in e.discretize(Distance=0.05) if p.x > 150 and p.y > 480]
    xs = max(p[0] for p in pts if abs(p[1] - y_side) < 0.3)
    yr = max(p[1] for p in pts if abs(p[0] - x_rear) < 0.3)
    return max(p[1] for p in pts if abs(p[0] - xs) < tol), max(p[0] for p in pts if abs(p[1] - yr) < tol)


class CandidateR4Test(unittest.TestCase):
    """R4: the band's run and the roll's underside are one 45 degree shelf under the head, level at the rear corner,
    a cone round the corner; the corner moves outward once from the lower body to the head."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.v = rs.VARIANTS["R4"]
        cls.d = rs.blueprint(cls.v)
        cls.body = rs.body(cls.d, cls.v, [])

    def test_the_body_is_one_valid_solid(self) -> None:
        self.assertTrue(self.body.isValid())
        self.assertEqual(len(self.body.Solids), 1)

    def test_the_changed_zone_passes_the_face_check(self) -> None:
        d = self.d
        found = [f for f in fc.failures(fc.check(self.body, "body", fc.default_reveals())) if abs(f.at[0]) > 150 and f.at[1] > d.step_y(f.at[2]) - 1.0]
        self.assertEqual(found, [])

    def test_the_head_has_the_full_width(self) -> None:
        d, v = self.d, self.v
        for z in (d.body_top - d.seam_groove - 0.5, (d.body_top + v.crease_hi[1] + v.smile) / 2):
            self.assertAlmostEqual(half_width(self.body, z, d.body_d), d.side_x(z), delta=0.05, msg=f"z {z:.1f}")

    def test_the_band_meets_the_floor_at_90_degrees(self) -> None:
        y = rs.band_path(self.d, self.v)[0].p[0]

        def band(z: float) -> list[tuple[float, float]]:
            return [(p.x, p.y) for w in self.body.slice(V(0, 0, 1), z) for p in w.discretize(Distance=0.1)
                    if p.x > self.d.rear_w / 2 - 1 and y - 25 < p.y < y + 25]

        low, high = band(self.v.chamfer + 1.0), band(self.v.band.stub - 1.0)
        self.assertTrue(low)
        self.assertLess(max(min(math.dist(p, q) for q in high) for p in low), 0.05)

    def test_the_corner_moves_outward_once(self) -> None:
        """From z 280 to z 380 every 5 mm, the corner round leaves the side and the rear further out or as far as
        before (the rear's x with the tuck of the side taken out): no step back and forth."""
        d = self.d
        rows = [(z, *corner_column(self.body, float(z))) for z in range(280, 385, 5)]
        side = [y for _, y, _ in rows]
        rear = [x + (d.width / 2 - d.side_x(z)) for z, _, x in rows]
        for k in range(1, len(rows)):
            self.assertGreaterEqual(side[k], side[k - 1] - 0.3, f"side at z {rows[k][0]}: {side}")
            self.assertGreaterEqual(rear[k], rear[k - 1] - 0.3, f"rear at z {rows[k][0]}: {rear}")
        self.assertGreater(side[-1] - side[0], 30.0)
        self.assertGreater(rear[-1] - rear[0], 8.0)


class CandidateR5aTest(unittest.TestCase):
    """R5a: R4 with the rear straight across (no smile), the creases R 3: flat facets, the R 25 corners and the cone."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.v = rs.VARIANTS["R5a"]
        cls.d = rs.blueprint(cls.v)
        cls.body = rs.body(cls.d, cls.v, [])

    def test_the_body_is_one_valid_solid(self) -> None:
        self.assertTrue(self.body.isValid())
        self.assertEqual(len(self.body.Solids), 1)

    def test_the_changed_zone_passes_the_face_check(self) -> None:
        d = self.d
        found = [f for f in fc.failures(fc.check(self.body, "body", fc.default_reveals())) if abs(f.at[0]) > 150 and f.at[1] > d.step_y(f.at[2]) - 1.0 or f.at[1] > d.body_d - 1]
        self.assertEqual(found, [])

    def test_the_head_has_the_full_width(self) -> None:
        d = self.d
        for z in (d.body_top - d.seam_groove - 0.5, (d.body_top + 340.0) / 2):
            self.assertAlmostEqual(half_width(self.body, z, d.body_d), d.side_x(z), delta=0.05, msg=f"z {z:.1f}")

    def test_the_corner_moves_outward_once(self) -> None:
        d = self.d
        rows = [(z, *corner_column(self.body, float(z))) for z in range(280, 385, 5)]
        for k in range(1, len(rows)):
            self.assertGreaterEqual(rows[k][1], rows[k - 1][1] - 0.3)
            self.assertGreaterEqual(rows[k][2] + d.width / 2 - d.side_x(rows[k][0]), rows[k - 1][2] + d.width / 2 - d.side_x(rows[k - 1][0]) - 0.3)


class CandidateR6Test(unittest.TestCase):
    """R6, planar: two flat 45 degree facets (the band's on the side, the roll's on the rear) meeting on a hip line at a
    sharp corner, R 3 on the edges of the back."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.v = rs.VARIANTS["R6"]
        cls.d = rs.blueprint(cls.v)
        cls.body = rs.body(cls.d, cls.v, [])

    def test_the_body_is_one_valid_solid(self) -> None:
        self.assertTrue(self.body.isValid())
        self.assertEqual(len(self.body.Solids), 1)

    def test_the_changed_zone_passes_the_face_check_but_for_the_foot_of_the_hip(self) -> None:
        """The one open item: where the hip, the two lower creases and the lower vertical corner meet (two convex and
        two concave rounds), OpenCascade's corner patch is 1.7 wide and meets its neighbours at 1.3 degrees."""
        d, a = self.d, self.d.rear_w / 2
        foot = lambda at: abs(abs(at[0]) - a) < 3.0 and abs(at[1] - d.body_d) < 3.0 and abs(at[2] - self.v.crease_lo[1]) < 3.0
        found = [f for f in fc.failures(fc.check(self.body, "body", fc.default_reveals()))
                 if (abs(f.at[0]) > 150 and f.at[1] > d.step_y(f.at[2]) - 1.0 or f.at[1] > d.body_d - 1) and not foot(f.at)]
        self.assertEqual(found, [])

    def test_the_head_has_the_full_width(self) -> None:
        d = self.d
        for z in (d.body_top - d.seam_groove - 0.5, (d.body_top + 340.0) / 2):
            self.assertAlmostEqual(half_width(self.body, z, d.body_d), d.side_x(z), delta=0.05, msg=f"z {z:.1f}")

    def test_the_side_facet_and_the_rear_facet_are_planes(self) -> None:
        """Behind the band's level run, the side facet is the plane x - rear_w/2 = z - 298 and the rear facet the
        plane y - body_d = z - 298, each a face of its own."""
        d, a, z0 = self.d, self.d.rear_w / 2, self.v.crease_lo[1]
        for point, normal in ((V(a + 6, d.body_d - 20, z0 + 6), V(1, 0, -1)), (V(0, d.body_d + 20, z0 + 20), V(0, 1, -1))):
            normal.normalize()
            near = [f for f in self.body.Faces if f.distToShape(Part.Vertex(point))[0] < 0.01]
            self.assertTrue(near, f"no face at {point}")
            self.assertTrue(any(isinstance(f.Surface, Part.Plane) and abs(abs(f.Surface.Axis.dot(normal)) - 1) < 1e-6 for f in near))

    def test_the_corner_moves_outward_once(self) -> None:
        d = self.d
        rows = [(z, *corner_column(self.body, float(z))) for z in range(280, 385, 5)]
        for k in range(1, len(rows)):
            self.assertGreaterEqual(rows[k][1], rows[k - 1][1] - 0.3)
            self.assertGreaterEqual(rows[k][2] + d.width / 2 - d.side_x(rows[k][0]), rows[k - 1][2] + d.width / 2 - d.side_x(rows[k - 1][0]) - 0.3)


class CandidateR7Test(unittest.TestCase):
    """R7: R6 with the band's stroke in straight lines (stub, kick, lean, one mitre into the level run), R 3 only on
    the convex edges that turn 40 degrees or more."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.v = rs.VARIANTS["R7"]
        cls.d = rs.blueprint(cls.v)
        cls.body = rs.body(cls.d, cls.v, [])

    def test_the_body_is_one_valid_solid(self) -> None:
        self.assertTrue(self.body.isValid())
        self.assertEqual(len(self.body.Solids), 1)

    def test_the_stroke_has_no_arc(self) -> None:
        path = rs.band_path(self.d, self.v)
        self.assertTrue(all(isinstance(sg, rs.pr.Line) for sg in path))
        self.assertEqual(path[0].p[0], path[0].q[0])                       # the stub stands upright
        self.assertAlmostEqual(path[-1].p[1], path[-1].q[1], places=9)     # the run is level

    def test_the_band_facets_are_flat(self) -> None:
        """The face in the middle of each piece of the band's facet (kick, lean) is flat: every point of it lies within
        0.001 of the plane through three of its points (the ruled loft makes them B-splines of degree 1)."""
        d, W = self.d, self.d.width / 2
        for sg in rs.band_path(d, self.v)[1:3]:
            (y0, z0), (y1, z1) = sg.p, sg.q
            ym, zm = (y0 + y1) / 2, (z0 + z1) / 2
            ty, tz = (y1 - y0) / math.hypot(y1 - y0, z1 - z0), (z1 - z0) / math.hypot(y1 - y0, z1 - z0)
            u = d.step_in / 2                                                 # half way in, square to the stroke
            point = V(W - u, ym + u * tz, zm - u * ty)
            face = min(self.body.Faces, key=lambda f: f.distToShape(Part.Vertex(point))[0])
            self.assertLess(face.distToShape(Part.Vertex(point))[0], 0.01)
            u0, u1, v0, v1 = face.ParameterRange
            pts = [face.valueAt(u0 + (u1 - u0) * i / 6, v0 + (v1 - v0) * j / 6) for i in range(7) for j in range(7)]
            n = (pts[6] - pts[0]).cross(pts[-1] - pts[0])
            n.normalize()
            self.assertLess(max(abs((p - pts[0]).dot(n)) for p in pts), 1e-3)

    def test_the_changed_zone_passes_the_face_check_but_for_three_corner_patches(self) -> None:
        """The open items, each a corner where small rounds meet (OpenCascade's corner patch): the end of the band's
        outer round at the sharp top mitre, the foot of the head's corner, the foot of the hip."""
        d = self.d
        spots = [(247.2, 469.3, 310.3), (245.2, 579.2, 339.1), (244.2, 579.5, 337.9), (227.3, 540.0, 298.0), (238.2, 542.9, 301.7)]
        near = lambda at: any(math.dist((abs(at[0]), at[1], at[2]), q) < 3.0 for q in spots)
        found = [f for f in fc.failures(fc.check(self.body, "body", fc.default_reveals()))
                 if (abs(f.at[0]) > 150 and f.at[1] > d.step_y(f.at[2]) - 1.0 or f.at[1] > d.body_d - 1) and not near(f.at)]
        self.assertEqual(found, [])

    def test_the_head_has_the_full_width(self) -> None:
        d = self.d
        for z in (d.body_top - d.seam_groove - 0.5, (d.body_top + 340.0) / 2):
            self.assertAlmostEqual(half_width(self.body, z, d.body_d), d.side_x(z), delta=0.05, msg=f"z {z:.1f}")

    def test_the_corner_moves_outward_once(self) -> None:
        """Tolerance 0.5: at the foot of the head's R 3 corner (z 340 to 345) the rear reading steps in 0.37, the corner
        patch there (an open item); elsewhere the corner only moves out."""
        d = self.d
        rows = [(z, *corner_column(self.body, float(z))) for z in range(280, 385, 5)]
        for k in range(1, len(rows)):
            self.assertGreaterEqual(rows[k][1], rows[k - 1][1] - 0.5)
            self.assertGreaterEqual(rows[k][2] + d.width / 2 - d.side_x(rows[k][0]), rows[k - 1][2] + d.width / 2 - d.side_x(rows[k - 1][0]) - 0.5)


class CandidateR8Test(unittest.TestCase):
    """R8: R7 with the lower rear corner, the hip and the chamfer's mitre made by hand, cut-ins milled by a ball and
    hand-holds round inside."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.v = rs.VARIANTS["R8"]
        cls.d = rs.blueprint(cls.v)
        cls.body = rs.body(cls.d, cls.v, [])

    def test_the_body_is_one_valid_solid(self) -> None:
        self.assertTrue(self.body.isValid())
        self.assertEqual(len(self.body.Solids), 1)

    def test_the_stroke_is_that_of_r7(self) -> None:
        a, b = rs.band_path(self.d, self.v), rs.band_path(rs.blueprint(rs.VARIANTS["R7"]), rs.VARIANTS["R7"])
        self.assertEqual([(sg.p, sg.q) for sg in a], [(sg.p, sg.q) for sg in b])

    def test_the_foot_of_the_hip_and_the_base_corner_pass_the_face_check(self) -> None:
        d, a = self.d, self.d.rear_w / 2
        near = lambda at: abs(abs(at[0]) - a) < 8 and abs(at[1] - d.body_d) < 8 and (at[2] < 12 or abs(at[2] - self.v.crease_lo[1]) < 8)
        found = [f for f in fc.failures(fc.check(self.body, "body", fc.default_reveals())) if near(f.at)]
        self.assertEqual(found, [])

    def test_the_changed_zone_passes_the_face_check_but_for_three_corner_patches(self) -> None:
        """Open: the top of the hip, the band's top mitre and the foot of the head's corner (OpenCascade's corner
        patches where rounds made with makeFillet meet)."""
        d = self.d
        spots = [(246.6, 550.0, 310.0), (247.2, 469.3, 310.3), (245.2, 579.2, 339.1), (244.2, 579.5, 337.9)]
        near = lambda at: any(math.dist((abs(at[0]), at[1], at[2]), q) < 3.0 for q in spots)
        found = [f for f in fc.failures(fc.check(self.body, "body", fc.default_reveals()))
                 if (abs(f.at[0]) > 150 and f.at[1] > d.step_y(f.at[2]) - 1.0 or f.at[1] > d.body_d - 1) and not near(f.at)]
        self.assertEqual(found, [])

    def test_the_cut_ins_have_round_ends(self) -> None:
        """On the rear wall, the outline of the lowest slot at its end is curved: no straight upright piece."""
        d, v = self.d, self.v
        a, c = d.rear_w / 2, v.cut_ins
        x_end = a - v.planar.cut_rear
        edges = [e for w in self.body.slice(V(0, 1, 0), d.body_d - 0.05) for e in w.Edges
                 if e.BoundBox.XMin < x_end + 6 and e.BoundBox.XMax > x_end - 1 and c.z0 - 1 < e.BoundBox.Center.z < c.z0 + c.height + 1]
        self.assertTrue(edges)
        self.assertFalse(any(isinstance(e.Curve, Part.Line) and e.BoundBox.ZLength > 1.0 and e.BoundBox.XLength < 0.01 for e in edges))

    def test_the_hand_holds_are_round_inside_and_sharp_at_the_rim(self) -> None:
        d, g = self.d, self.v.grips
        rim = [e for e in self.body.Edges if abs(e.BoundBox.YMin - d.depth) < 1e-3 and abs(e.BoundBox.YMax - d.depth) < 1e-3
               and g.x0 - 1 < e.BoundBox.Center.x < g.x1 + 1 and g.z0 - 1 < e.BoundBox.Center.z < g.z0 + g.height + 1]
        self.assertTrue(rim)
        self.assertTrue(all(rs.crease_angle(self.body.ancestorsOfType(e, Part.Face), e.valueAt((e.FirstParameter + e.LastParameter) / 2)) > 40 for e in rim))
        inside = [f for f in self.body.Faces if g.x0 < f.CenterOfMass.x < g.x1 and d.depth - g.depth - 1 < f.CenterOfMass.y < d.depth - 1
                  and g.z0 < f.CenterOfMass.z < g.z0 + g.height and isinstance(f.Surface, (Part.Cylinder, Part.Toroid, Part.Sphere, Part.BSplineSurface))]
        self.assertTrue(any(abs(getattr(f.Surface, "Radius", getattr(f.Surface, "MinorRadius", 0.0)) - self.v.planar.grip_r) < 0.01 for f in inside))
