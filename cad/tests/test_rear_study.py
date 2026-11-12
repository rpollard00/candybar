"""The face check and the rear form study: the check finds the defects of revision 6's rear corner and passes the
repaired rear of candidate A; the study leaves Blueprint() at revision 6."""
from __future__ import annotations

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
