"""The face check: its five rules and its list of known items, on small solids. cad/check.sh (tools.face_check) runs
it on the parts of every build."""
from __future__ import annotations

import unittest

import FreeCAD as App
import Part

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

    def test_an_edge_break_is_allowed_and_a_wider_strip_of_the_same_width_is_not(self) -> None:
        box = Part.makeBox(100, 60, 40)
        top = [e for e in box.Edges if abs(e.BoundBox.ZMin - 40) < 1e-6]
        broken = box.makeFillet(1.0, top)
        self.assertTrue(rules(fc.check(broken, "box")))                       # R 1 rounds are narrow faces
        self.assertEqual(rules(fc.check(broken, "box", break_radius=1.0)), set())
        self.assertTrue(rules(fc.check(box.makeFillet(0.6, top), "box", break_radius=1.0)))


class KnownItemsTest(unittest.TestCase):
    def test_a_known_item_holds_for_its_place_on_both_sides_and_nowhere_else(self) -> None:
        item = fc.Known("body", "sliver", (246.5, 550.0, 305.0), "0.4 wide", "a reason")
        hit = lambda part, rule, at: item.holds(fc.Finding(part, rule, at, ""))
        self.assertTrue(hit("body", "sliver", (246.3, 550.7, 304.9)))
        self.assertTrue(hit("body", "sliver", (-246.3, 550.7, 304.9)))
        self.assertFalse(hit("body", "needle", (246.3, 550.7, 304.9)))
        self.assertFalse(hit("hood", "sliver", (246.3, 550.7, 304.9)))
        self.assertFalse(hit("body", "sliver", (246.3, 554.0, 304.9)))

    def test_a_known_item_with_no_finding_is_reported(self) -> None:
        item = fc.Known("body", "sliver", (10.0, 10.0, 10.0), "", "")
        self.assertEqual(fc.mark_known([fc.Finding("body", "sliver", (100.0, 10.0, 10.0), "")], (item,)), [item])

    def test_every_known_item_has_a_place_a_size_and_a_reason(self) -> None:
        for item in fc.KNOWN:
            with self.subTest(item=item):
                self.assertIn(item.rule, fc.RULES)
                self.assertGreaterEqual(item.at[0], 0.0)
                self.assertTrue(item.size and item.reason)
                self.assertLessEqual(item.within, 3.0)


