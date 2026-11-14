"""The solids of the blueprint: valid parts that do not overlap, a check that notices a solid off the blueprint, and
the planar rear of revision 7 (decision record 0007)."""
from __future__ import annotations

import math
import re
import unittest
from dataclasses import replace
from unittest import mock

import FreeCAD as App
import Part

from candybar.shell import cavity, solids
from candybar.shell import profiles as pr
from candybar.shell.dims import Blueprint
from tools import check_solids
from tools import face_check as fc

from . import support

V = App.Vector


def over(row: dict) -> bool:
    return max(row["solid_to_blueprint"], row["blueprint_to_solid"]) > check_solids.TOL


def failing(report: dict) -> set[str]:
    return {name for name, row in [*report["sections"].items(), *report["silhouettes"].items()] if over(row)}


class BlueprintSolidsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d, cls.parts, _ = support.shell()
        cls.baseline = check_solids.run(cls.parts, cls.d)

    def test_the_parts_are_those_of_revision_7(self) -> None:
        self.assertEqual(list(self.parts), ["deck", "control_panel", "body", "hood", "marquee_lip", "speaker_right", "speaker_left",
                                            "logo_form", "bezel", "screen"])

    def test_every_part_is_one_valid_closed_solid(self) -> None:
        for name, state in self.baseline["parts"].items():
            with self.subTest(part=name):
                self.assertTrue(state["valid"] and state["closed"] and state["check"])
                self.assertEqual(state["solids"], 1)
                self.assertGreater(state["volume_mm3"], 0)

    def test_no_two_parts_overlap(self) -> None:
        self.assertEqual(self.baseline["overlaps"], [])

    def test_every_view_and_section_matches_the_blueprint(self) -> None:
        self.assertEqual(failing(self.baseline), set())
        self.assertTrue(self.baseline["ok"])

    def test_no_point_of_a_section_is_skipped(self) -> None:
        self.assertEqual(sum(row["bridged_points"] for row in self.baseline["sections"].values()), 0)

    def assert_check_notices(self, **change: float) -> None:
        changed = check_solids.run(solids.build(replace(self.d, **change)), self.d)
        self.assertFalse(changed["ok"])
        self.assertTrue(failing(changed), f"no view or section fails: {change}")

    def test_check_notices_a_stronger_rail_arc(self) -> None:
        self.assert_check_notices(rail_sagitta_ratio=self.d.rail_sagitta_ratio + 0.01)

    def test_check_notices_a_smaller_tuck(self) -> None:
        self.assert_check_notices(body_tuck_ratio=self.d.body_tuck_ratio - 0.008)

    def test_check_notices_a_rectangular_panel(self) -> None:
        d = self.d
        x, y0, y1 = d.panel_w / 2, d.deck_nose + d.panel_gap, d.deck_nose + d.panel_gap + d.panel_d
        rectangle = lambda d_, grow=0.0: [(-x - grow, y0 - grow), (x + grow, y0 - grow), (x + grow, y1 + grow), (-x - grow, y1 + grow)]
        with mock.patch.object(pr, "panel_outline", rectangle):
            parts = solids.build(d)
        changed = check_solids.run(parts, d)
        self.assertFalse(changed["ok"])
        self.assertIn("Z panel pocket", failing(changed))

    def test_check_notices_a_higher_rear_shelf(self) -> None:
        self.assert_check_notices(rear_shelf_z0=self.d.rear_shelf_z0 + 6.0, rear_shelf_z1=self.d.rear_shelf_z1 + 6.0)

    def test_check_notices_a_steeper_kick(self) -> None:
        self.assert_check_notices(band_kick=self.d.band_kick - 18.0)

    def assert_same_points(self, found: list[tuple[float, float]], expected: list[tuple[float, float]]) -> None:
        self.assertEqual(len(found), len(expected), found)
        for p in expected:
            self.assertLess(min(math.dist(p, q) for q in found), 1e-4, f"{p} not in {found}")

    def test_panel_plate_and_pocket_have_the_outline(self) -> None:
        d = self.d
        corners = lambda shape, z: [(v.X, v.Y) for v in shape.Vertexes if abs(v.Z - z) < 1e-6]
        self.assert_same_points(corners(self.parts["control_panel"], d.panel_top), pr.panel_outline(d))
        z = (d.panel_top + d.deck_top) / 2
        pocket = min(self.parts["deck"].slice(App.Vector(0, 0, 1), z), key=lambda w: w.BoundBox.DiagonalLength)
        self.assert_same_points([(v.X, v.Y) for v in pocket.Vertexes], pr.panel_outline(d, d.panel_gap))
        opening = cavity.openings(d, cavity.Openings())[0]
        self.assert_same_points(corners(opening, opening.BoundBox.ZMax), pr.panel_outline(d, -cavity.Openings().panel_ledge))


def plan_points(shape: Part.Shape, z: float, keep, step: float = 0.05) -> list[App.Vector]:
    """The points of the level section of a solid at z that pass keep()."""
    return [p for w in shape.slice(V(0, 0, 1), z) for e in w.Edges for p in e.discretize(Distance=step) if keep(p)]


def face_at(shape: Part.Shape, point: App.Vector) -> Part.Face:
    """The face of a solid on which a point lies."""
    face = min(shape.Faces, key=lambda f: f.distToShape(Part.Vertex(point))[0])
    if face.distToShape(Part.Vertex(point))[0] > 0.01:
        raise AssertionError(f"no face at {point}")
    return face


class PlanarRearTest(unittest.TestCase):
    """Revision 7: the rear goes straight across; the band's stroke is straight lines; under the head two flat facets
    meet on the hip; the head has the full width."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.d, parts, cls.log = support.shell()
        cls.body, cls.hood = parts["body"], parts["hood"]

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

    def test_the_head_has_the_full_width(self) -> None:
        d = self.d
        for z in (d.body_top - d.seam_groove - 0.5, (d.body_top + d.rear_shelf_z1) / 2):
            width = max(abs(p.x) for p in plan_points(self.body, z, lambda p: p.y >= d.body_d, 0.2))
            self.assertAlmostEqual(width, d.side_x(z), delta=0.05, msg=f"z {z:.1f}")

    def test_the_lower_rear_corner_is_the_ellipse_of_the_hip(self) -> None:
        """At a height below the cut-ins, the plan section leaves the side at r from the corner and the rear at r
        from it (r = R / sqrt(2)), and on the diagonal it stands (2 - sqrt(3)) R inside the sharp corner."""
        d, rw, big = self.d, self.d.rear_w / 2, self.d.rear_round_r
        r = big / math.sqrt(2)
        pts = plan_points(self.body, d.cut_in_z0 - 20.0, lambda p: p.x > rw - 8 and p.y > d.body_d - 8)
        self.assertAlmostEqual(max(p.y for p in pts if abs(p.x - rw) < 1e-4), d.body_d - r, delta=0.06)
        self.assertAlmostEqual(max(p.x for p in pts if abs(p.y - d.body_d) < 1e-4), rw - r, delta=0.06)
        reach = max((p.x - rw) + (p.y - d.body_d) for p in pts) / math.sqrt(2)
        self.assertAlmostEqual(-reach, (2 - math.sqrt(3)) * big, delta=0.02)

    def test_the_cut_ins_have_level_lips_and_a_slot_of_one_height_round_the_corner(self) -> None:
        """On a line 0.002 inside the surface, at two places on each leg and five round the corner's ellipse: one
        slot, its lips cut_in_h / 2 above and below the middle of the groove."""
        d = self.d
        rw, y0, big, h = d.rear_w / 2, d.body_d, d.rear_round_r, d.cut_in_h
        r, k = big / math.sqrt(2), math.sqrt(0.5)
        o = V(rw - 2 * r, y0 - 2 * r, 0)
        ell = Part.Ellipse(o + V(k, k, 0) * (math.sqrt(3) * big), o + V(-k, k, 0) * big, o)
        u0, u1 = sorted((ell.parameter(V(rw, y0 - r, 0)), ell.parameter(V(rw - r, y0, 0))))
        if u1 - u0 > math.pi:
            u0, u1 = u1, u0 + 2 * math.pi
        spots = [(V(rw - 12, y0, 0), V(0, 1, 0)), (V(rw - 6, y0, 0), V(0, 1, 0)), (V(rw, y0 - 6, 0), V(1, 0, 0)), (V(rw, y0 - 12, 0), V(1, 0, 0))]
        for t in (0.05, 0.25, 0.5, 0.75, 0.95):
            u = u0 + (u1 - u0) * t
            dv = ell.tangent(u)[0]
            n = V(dv.y, -dv.x, 0)
            spots.append((ell.value(u), n if n.x + n.y > 0 else -n))
        for i in range(d.cut_in_count):
            zm = d.cut_in_z0 + i * d.cut_in_pitch + h / 2
            for q, n in spots:
                pt = q - n * 0.002
                seg = Part.LineSegment(V(pt.x, pt.y, zm - 9), V(pt.x, pt.y, zm + 9)).toShape().common(self.body)
                zs = sorted(z for e in seg.Edges for z in (e.Vertexes[0].Point.z, e.Vertexes[-1].Point.z))
                gaps = [(zs[j], zs[j + 1]) for j in range(1, len(zs) - 1, 2) if zs[j + 1] - zs[j] > 1]
                self.assertEqual(len(gaps), 1, msg=f"slot {i} at ({q.x:.2f}, {q.y:.2f})")
                lo, hi = gaps[0]
                self.assertAlmostEqual(hi - zm, h / 2, delta=0.05)
                self.assertAlmostEqual(zm - lo, h / 2, delta=0.05)

    def test_the_cut_ins_are_as_deep_as_the_dimension(self) -> None:
        d, rw = self.d, self.d.rear_w / 2
        zm = d.cut_in_z0 + d.cut_in_h / 2
        pts = plan_points(self.body, zm, lambda p: rw - 12.5 < p.x < rw - 11.5 and p.y > d.body_d - 5)
        self.assertAlmostEqual(d.body_d - min(p.y for p in pts), d.cut_in_depth, delta=0.01)

    def rim(self) -> list[Part.Edge]:
        return solids.hand_hold_rim(self.body, self.d)

    def test_the_rims_of_the_hand_holds_have_the_edge_break_all_round(self) -> None:
        """No sharp edge is left on the rear wall round the openings: each edge there joins the wall to a round of
        the edge break."""
        rim = self.rim()
        self.assertTrue(rim)
        for e in rim:
            fs = self.body.ancestorsOfType(e, Part.Face)
            self.assertLess(solids.crease_angle(fs, solids.middle(e)), 1.0)
            self.assertTrue(any(fc.is_break(f, self.d.edge_break) for f in fs if not isinstance(f.Surface, Part.Plane)))

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

    def round_area(self, shape: Part.Shape, keep) -> tuple[float, float]:
        """The area of the faces of a solid that are rounds of rear_round_r and pass keep(): right side, left side."""
        def tight(f: Part.Face) -> bool:
            u0, u1, v0, v1 = f.ParameterRange
            try:
                return abs(max(abs(k) for k in f.curvatureAt((u0 + u1) / 2, (v0 + v1) / 2)) - 1 / self.d.rear_round_r) < 0.02
            except Exception:
                return False
        rounds = [f for f in shape.Faces if tight(f) and keep(f)]
        return sum(f.Area for f in rounds if f.CenterOfMass.x > 0), sum(f.Area for f in rounds if f.CenterOfMass.x < 0)

    def test_the_hood_has_the_round_on_both_rear_corners(self) -> None:
        right, left = self.round_area(self.hood, lambda f: f.BoundBox.YMax > self.d.depth - 80)
        self.assertGreater(right, 500.0)
        self.assertAlmostEqual(left, right, delta=0.001 * right)

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

    def test_no_convex_edge_of_the_rear_stays_sharp_but_those_that_the_build_names(self) -> None:
        """After the edge break, a convex edge behind the band that turns more than edge_break_turn is what is left
        of an edge that the build's log names as left sharp: it lies within 3 of the place in the log (the breaks of
        the edges beside it make it shorter)."""
        left = solids.sharp_edges(self.body, self.d, lambda m: solids.behind_band(self.d, m))
        named = [line for line in self.log if line.startswith("body: no edge break at")]
        places = [tuple(float(v) for v in m.groups()) for line in named for m in re.finditer(r"\((-?[\d.]+), (-?[\d.]+), (-?[\d.]+)\)", line)]
        self.assertEqual(len(places), 2, named)
        for e, _ in left:
            m = solids.middle(e)
            self.assertLess(min(math.dist((m.x, m.y, m.z), p) for p in places), 3.0, f"sharp edge at {solids.where(e)}")


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


class ScreenPositionTest(unittest.TestCase):
    """The bezel, the window and the screen stand 12 lower on the face than in revision 4; the body top stays."""

    def test_strips_above_and_below_the_bezel(self) -> None:
        d = Blueprint()
        self.assertAlmostEqual(d.top_s - d.bezel_s1, 32.0)
        self.assertAlmostEqual(d.bezel_s0 - d.bend_t, 40.0)

    def test_the_drop_keeps_the_body_top(self) -> None:
        d = Blueprint()
        rev4 = replace(d, band_len=52.0, brow_ledge=20.0)
        self.assertAlmostEqual(d.body_top, rev4.body_top)
        self.assertAlmostEqual(d.seam_y, rev4.seam_y)
        self.assertAlmostEqual(d.face(rev4.image_s)[1] - d.face(d.image_s)[1], 12.0 * d.u[1])
