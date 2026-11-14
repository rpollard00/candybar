"""The edge rule (the owner, 2026-11-12): no outside edge of the exterior stays fully sharp. A printed part of the
exterior has no convex outside edge that turns more than 45 degrees with neither a design round nor the edge break.
The rule on small solids; the tools that make the break by hand; and the rule on the default build of the shell."""
from __future__ import annotations

import math
import unittest

import FreeCAD as App
import Part

from candybar.shell import cavity, solids
from candybar.shell.dims import Blueprint
from tools import edge_finish as ef
from tools import face_check as fc

from . import support

V = App.Vector


def box(name_at: tuple[float, float, float] = (0.0, 0.0, 0.0), size: tuple[float, float, float] = (100.0, 60.0, 40.0)) -> Part.Shape:
    return Part.makeBox(*size, V(*name_at))


def broken(shape: Part.Shape, radius: float, keep_sharp=lambda e: False) -> Part.Shape:
    """A solid with a round on every edge but those that keep_sharp names."""
    return shape.makeFillet(radius, [e for e in shape.Edges if not keep_sharp(e)])


class EdgeRuleTest(unittest.TestCase):
    """The rule on small solids, by the names of the parts."""

    def setUp(self) -> None:
        self.d = Blueprint()

    def failures(self, parts: dict[str, Part.Shape]) -> list[str]:
        return ef.failures(ef.survey(parts, self.d))

    def test_a_printed_part_with_sharp_edges_fails(self) -> None:
        rows = ef.survey({"body": box()}, self.d)
        self.assertEqual(sum(g["edges"] for g in rows["body"]["sharp"] if not g["against"]), 12)
        found = ef.failures(rows)
        self.assertTrue(found)
        self.assertTrue(all("sharp edges show" in f for f in found))

    def test_the_edge_break_on_every_edge_passes(self) -> None:
        self.assertEqual(self.failures({"body": broken(box(), self.d.edge_break)}), [])

    def test_a_round_of_the_design_passes(self) -> None:
        self.assertEqual(self.failures({"hood": broken(box(), self.d.rear_round_r)}), [])

    def test_one_edge_without_the_break_fails(self) -> None:
        solid = box()
        one = solid.Edges[0]
        found = self.failures({"deck": broken(solid, self.d.edge_break, lambda e: e.isSame(one))})
        self.assertEqual(len(found), 1)                        # the edge, and what the rounds beside it leave at its two ends
        self.assertIn("sharp edges show", found[0])
        self.assertIn("the longest at (0.0, 0.0, 20.0)", found[0])

    def test_an_edge_that_turns_45_degrees_is_blunt(self) -> None:
        """A flat of 45 degrees on one edge of a box: its two long edges turn 45 degrees and are not sharp."""
        solid = Part.makeBox(100, 60, 40)
        solid = solid.makeChamfer(5.0, [solid.Edges[0]])
        turns = [round(solids.edge_turn(solid, e)[1]) for e in solid.Edges]
        self.assertEqual(turns.count(45), 2)
        sharp = solids.sharp_edges(solid, self.d, lambda m: True)
        self.assertEqual(len(sharp), len(solid.Edges) - 2)
        self.assertTrue(all(solids.edge_turn(solid, e)[1] > 46 for e, _ in sharp))

    def joint(self, other: str) -> dict[str, Part.Shape]:
        """Two boxes that meet on the plane y = 60, with the break on every edge that is not in that plane."""
        on_joint = lambda e: all(abs(v.Point.y - 60.0) < 1e-6 for v in e.Vertexes)
        return {"deck": broken(box(), self.d.edge_break, on_joint), other: broken(box((0.0, 60.0, 0.0)), self.d.edge_break, on_joint)}

    def test_a_sharp_edge_in_a_named_joint_passes(self) -> None:
        rows = ef.survey(self.joint("body"), self.d)
        self.assertEqual({g["against"] for g in rows["deck"]["sharp"]}, {"body"})
        self.assertEqual(ef.failures(rows), [])

    def test_a_sharp_edge_in_a_joint_that_has_no_name_fails(self) -> None:
        found = self.failures(self.joint("hood"))
        self.assertTrue(found)
        self.assertTrue(all("not a named joint" in f for f in found))

    def test_a_provisional_form_is_not_a_failure_and_reads_as_provisional(self) -> None:
        rows = ef.survey({"logo_form": box()}, self.d)
        self.assertEqual(ef.failures(rows), [])
        text = ef.table(rows, self.d)
        self.assertIn("| logo_form | all | provisional, not finished | 12 |", text)
        self.assertNotIn("| logo_form | all | outside |", text)

    def test_a_part_that_nobody_named_fails(self) -> None:
        found = self.failures({"new_part": broken(box(), self.d.edge_break)})
        self.assertEqual(len(found), 1)
        self.assertIn("in no class", found[0])

    def test_each_part_is_in_one_class_only(self) -> None:
        names = list(ef.PRINTED) + list(ef.CUT_PLATES) + list(ef.PROVISIONAL) + list(ef.NOT_DECIDED)
        self.assertEqual(len(names), len(set(names)))


class BreakByHandTest(unittest.TestCase):
    """The edge break cut by hand on a block that is symmetric about x = 0: straight pieces, and a ball at each
    corner where three edges meet."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.size = (60.0, 40.0, 30.0)
        cls.block = Part.makeBox(*cls.size, V(-30.0, 0.0, 0.0))
        cls.log: list[str] = []
        cls.done = solids.break_by_hand(cls.block, cls.block.Edges, 1.0, cls.log, "block")

    def test_the_result_is_one_valid_solid_that_passes_the_strict_check(self) -> None:
        self.assertTrue(self.done.isValid())
        self.assertEqual(len(self.done.Solids), 1)
        solids.fit_tolerances(self.done).check(True)

    def test_no_edge_is_left_sharp(self) -> None:
        self.assertEqual(solids.sharp_edges(self.done, Blueprint(), lambda m: True), [])

    def test_it_has_the_volume_of_the_block_with_a_round_on_every_edge(self) -> None:
        a, b, c = (s - 2.0 for s in self.size)
        exact = a * b * c + 2.0 * (a * b + b * c + a * c) + math.pi * (a + b + c) + 4.0 / 3.0 * math.pi
        # the tools stand ROUND_OFF proud of the round: a quarter tube along each edge and a ball's shell at the corners
        proud = solids.ROUND_OFF * (math.pi / 2 * 4 * (a + b + c) + 4 * math.pi)
        self.assertAlmostEqual(self.done.Volume, exact + proud, delta=0.005)

    def test_each_corner_is_a_ball_and_each_edge_a_cylinder_of_the_radius(self) -> None:
        balls = [f for f in self.done.Faces if isinstance(f.Surface, Part.Sphere)]
        self.assertEqual(len(balls), 8)
        for f in balls:
            self.assertAlmostEqual(f.Surface.Radius, 1.0, delta=0.001)
        self.assertEqual(sum(1 for f in self.done.Faces if fc.is_break(f, 1.0)), 12)

    def test_a_corner_ball_is_a_face_of_the_break_but_not_a_round_along_an_edge(self) -> None:
        """The comparison of two builds counts the ball as edge break; the face check allows a narrow face only when
        it is a round along an edge."""
        for f in self.done.Faces:
            if isinstance(f.Surface, Part.Sphere):
                self.assertTrue(fc.is_break_surface(f, 1.0))
                self.assertFalse(fc.is_break(f, 1.0))
        self.assertEqual(sum(1 for f in self.done.Faces if fc.is_break_surface(f, 1.0)), 20)
        self.assertFalse(any(fc.is_break_surface(f, 1.0) for f in self.block.Faces))

    def test_the_left_side_is_the_mirror_image_of_the_right(self) -> None:
        mirror = self.done.mirror(V(0, 0, 0), V(1, 0, 0))
        self.assertLess(self.done.cut(mirror).Volume + mirror.cut(self.done).Volume, 1e-6)

    def test_the_log_counts_the_pieces(self) -> None:
        self.assertIn("block, edge break R 1 by hand: 12 edges", self.log[0])
        self.assertTrue(any("8 straight pieces" in line and "4 corners" in line for line in self.log), self.log)


class CutNearTest(unittest.TestCase):
    """The guard on the cut by the tools of the break: each tool must take something off."""

    def setUp(self) -> None:
        self.box = Part.makeBox(40, 40, 40)

    def test_a_cut_that_does_its_work_passes(self) -> None:
        tools = [Part.makeBox(10, 10, 10, V(-5, -5, -5)), Part.makeBox(10, 10, 10, V(35, 35, 35))]
        self.assertAlmostEqual(solids.cut_near(self.box, tools, "test").Volume, 40 ** 3 - 2 * 125)

    def test_what_a_tool_holds_is_found_near_the_tool(self) -> None:
        volume, near = solids.held(self.box, Part.makeBox(10, 10, 10, V(-5, -5, -5)))
        self.assertAlmostEqual(volume, 125.0)
        self.assertAlmostEqual(near.Volume, 7.0 ** 3)                    # the box within CUT_NEAR of the tool's box

    def test_a_tool_that_holds_nothing_is_an_error(self) -> None:
        with self.assertRaises(Part.OCCError):
            solids.cut_near(self.box, [Part.makeBox(10, 10, 10, V(-5, -5, -5)), Part.makeBox(5, 5, 5, V(60, 60, 60))], "test")


class TolerancesTest(unittest.TestCase):
    def test_a_large_tolerance_that_the_curves_do_not_need_is_set_to_what_they_need(self) -> None:
        loose = Part.makeBox(10, 10, 10)
        loose.fixTolerance(0.01)
        fitted = solids.fit_tolerances(loose)
        self.assertTrue(fitted.isValid())
        self.assertLess(max(e.Tolerance for e in fitted.Edges), 1e-6)
        self.assertLess(max(v.Tolerance for v in fitted.Vertexes), 1e-6)

    def test_a_tolerance_under_the_limit_stays(self) -> None:
        fine = Part.makeBox(10, 10, 10)
        fine.fixTolerance(1e-6)
        self.assertAlmostEqual(max(e.Tolerance for e in solids.fit_tolerances(fine).Edges), 1e-6)


class FlatBreakTest(unittest.TestCase):
    def test_a_flat_of_the_width_takes_the_edge_off(self) -> None:
        cube = Part.makeBox(2, 2, 2)
        edge = next(e for e in cube.Edges if all(abs(v.Point.x) < 1e-9 and abs(v.Point.y) < 1e-9 for v in e.Vertexes))
        log: list[str] = []
        done = solids.flat_break(cube, [edge], 1.0, log, "cube")
        self.assertAlmostEqual(cube.Volume - done.Volume, 0.5, delta=1e-6)           # a prism with legs of 1 / sqrt(2), 2 long
        out = V(-1, -1, 0).normalize()
        flats = [f for f in done.Faces if isinstance(f.Surface, Part.Plane) and (f.normalAt(0, 0) - out).Length < 1e-6]
        self.assertEqual(len(flats), 1)
        self.assertAlmostEqual(flats[0].Area, 2.0, delta=1e-6)                       # 1 wide, 2 long
        self.assertIn("the edge turns 90.0 degrees, the flat lies 0.50 under it", log[0])


class ShellEdgeFinishTest(unittest.TestCase):
    """The default build of the shell: the rule holds on the printed parts of the exterior (deck, body, hood). The
    edges in a joint, the provisional forms and the bezel plate are left out by name."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.d, cls.parts, cls.log = support.shell()
        cls.rows = ef.survey(cls.parts, cls.d)

    def test_no_printed_part_has_a_sharp_edge_that_shows_or_lies_in_a_joint_with_no_name(self) -> None:
        self.assertEqual(ef.failures(self.rows), [])

    def test_the_printed_parts_are_the_deck_the_body_and_the_hood(self) -> None:
        self.assertEqual({k for k, r in self.rows.items() if r["class"] == "printed"}, {"deck", "body", "hood"})

    def test_every_part_of_the_build_but_the_screen_is_in_a_class(self) -> None:
        self.assertEqual(set(self.rows), set(self.parts) - set(fc.NOT_PARTS))
        self.assertEqual([k for k, r in self.rows.items() if not r["class"]], [])

    def test_every_named_joint_holds_a_sharp_edge(self) -> None:
        """A list that names a joint with nothing in it is not honest."""
        used = {(part, g["against"]) for part, r in self.rows.items() if r["class"] == "printed" for g in r["sharp"] if g["against"]}
        self.assertEqual(used, set(ef.JOINTS))

    def test_the_hood_has_no_sharp_edge_at_all(self) -> None:
        """The rim of the opening and the seam bevel have the break; the foot of the hood is blunt."""
        self.assertEqual(self.rows["hood"]["sharp"], [])
        self.assertEqual(solids.sharp_edges(self.parts["hood"], self.d, lambda m: True), [])

    def test_the_hood_has_the_break_as_rounds_of_its_radius_and_a_ball_at_each_rear_corner(self) -> None:
        self.assertGreaterEqual(self.rows["hood"]["break_faces"], 28)
        self.assertEqual(self.rows["hood"]["break_corner_faces"], 2)

    def test_the_break_of_the_hood_is_the_same_on_both_sides(self) -> None:
        hood = self.parts["hood"]
        rounds = [f for f in hood.Faces if fc.is_break(f, self.d.edge_break)]
        right = sum(f.Area for f in rounds if f.CenterOfMass.x > 1.0)
        left = sum(f.Area for f in rounds if f.CenterOfMass.x < -1.0)
        self.assertGreater(right, 300.0)
        self.assertAlmostEqual(left, right, delta=1e-4 * right)

    def test_the_break_takes_at_most_its_own_depth_off_the_hood(self) -> None:
        """Each face of the break lies within the depth of a round of R 1 on an edge of 95 degrees of where the
        sharp edge was: the form does not change but by the break."""
        d, hood = self.d, self.parts["hood"]
        sharp = solids.hood_frame(solids.pr.hood(d))(solids.cap_unbroken(d, solids.pr.hood(d))[0])

        shell = sharp.Shells[0]

        def depth(p: App.Vector) -> float:
            """How far a point lies from the cap before the break: the least of the distance that OpenCascade finds
            (it misses the nearest point on the faces of the soft edge, and then gives too much) and the distance to
            the point's foot on each face's surface, when the foot lies on the face."""
            best = shell.distToShape(Part.Vertex(p))[0]
            for g in sharp.Faces:
                u, v = g.Surface.parameter(p)
                if g.isPartOfDomain(u, v):
                    best = min(best, (g.Surface.value(u, v) - p).Length)
            return best

        worst = 0.0
        for f in hood.Faces:
            if not (fc.is_break(f, d.edge_break) or isinstance(f.Surface, Part.Sphere)):
                continue
            u0, u1, v0, v1 = f.ParameterRange
            for a in (0.1, 0.3, 0.5, 0.7, 0.9):
                for b in (0.1, 0.3, 0.5, 0.7, 0.9):
                    if f.isPartOfDomain(u0 + (u1 - u0) * a, v0 + (v1 - v0) * b):
                        worst = max(worst, depth(f.valueAt(u0 + (u1 - u0) * a, v0 + (v1 - v0) * b)))
        self.assertGreater(worst, 0.25)
        self.assertLess(worst, d.edge_break * (1.0 - math.cos(math.radians(95.0 / 2))) + 0.01)

    def test_the_cavity_reads_the_hood_before_its_edge_break(self) -> None:
        """The offset of a section through the lofts of the break fails at some planes, and a slab then has no
        cavity. The other skin parts are the built ones."""
        skin = dict(zip(cavity.SKIN, cavity.form_parts(self.parts, self.d)))
        self.assertEqual(sum(1 for f in skin["hood"].Faces if fc.is_break_surface(f, self.d.edge_break)), 0)
        self.assertGreaterEqual(len(solids.sharp_edges(skin["hood"], self.d, lambda m: m.z > self.d.body_top + self.d.seam_gap + 0.05)), 24)
        self.assertGreater(skin["hood"].Volume, self.parts["hood"].Volume + 200.0)
        for k in ("deck", "body", "marquee_lip"):
            self.assertTrue(skin[k].isSame(self.parts[k]))

    def test_the_body_has_no_sharp_edge_at_the_rear_or_in_the_seam_groove(self) -> None:
        d = self.d
        left = solids.sharp_edges(self.parts["body"], d, lambda m: solids.behind_band(d, m) or m.z > d.body_top - d.seam_groove - 0.5)
        self.assertEqual([solids.where(e) for e, _ in left], [])

    def test_the_body_has_a_flat_break_where_the_break_of_the_bevel_ends_on_the_corner_round(self) -> None:
        flats = [line for line in self.log if line.startswith("body, flat break of 1 at")]
        self.assertEqual(len(flats), 2, self.log)

    def test_the_build_names_no_edge_that_is_still_sharp(self) -> None:
        self.assertEqual([line for line in self.log if "still sharp" in line or "stays sharp" in line or "stay sharp" in line], [])

    def test_the_provisional_forms_are_listed_as_provisional_and_are_still_sharp(self) -> None:
        """When a form on the hood band gets its design, it leaves this list."""
        text = ef.table(self.rows, self.d)
        for part in ef.PROVISIONAL:
            with self.subTest(part=part):
                self.assertEqual(self.rows[part]["class"], "provisional, not finished")
                self.assertTrue(any(not g["against"] for g in self.rows[part]["sharp"]))
                self.assertIn(f"| {part} | all | provisional, not finished |", text)

    def test_the_bezel_plate_waits_for_the_owners_choice(self) -> None:
        self.assertEqual(self.rows["bezel"]["class"], "not decided")
        self.assertEqual(sum(g["edges"] for g in self.rows["bezel"]["sharp"] if not g["against"]), 4)
