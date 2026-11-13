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
