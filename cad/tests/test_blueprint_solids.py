"""The solids of the blueprint: valid parts that do not overlap, and a check that notices a solid off the blueprint."""
from __future__ import annotations

import math
import unittest
from dataclasses import replace
from unittest import mock

import FreeCAD as App

from candybar.shell import cavity, solids
from candybar.shell import profiles as pr
from candybar.shell.dims import Blueprint
from tools import check_solids


def over(row: dict) -> bool:
    return max(row["solid_to_blueprint"], row["blueprint_to_solid"]) > check_solids.TOL


def failing(report: dict) -> set[str]:
    return {name for name, row in [*report["sections"].items(), *report["silhouettes"].items()] if over(row)}


class BlueprintSolidsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d = Blueprint()
        cls.parts = solids.build(cls.d)
        cls.baseline = check_solids.run(cls.parts, cls.d)

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
