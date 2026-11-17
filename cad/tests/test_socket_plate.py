"""The front socket plate (candybar.shell.socket_plate, in the default build as b-knob): its values, its place on the
deck side, the knob as the one difference between two forms, the plate in its recess (quick); and in the slow group,
the cut of the seat changes the deck at the seat only. The build of the plate checks its solids, the seat and the fit."""
from __future__ import annotations

import unittest

from candybar.shell import profiles as pr
from candybar.shell import socket_plate as spm
from candybar.shell import solids as so
from candybar.shell.dims import Blueprint

from . import support

# the smallest gap between two items along the centre line of a variant, mm
MIN_GAP = 1.0
# the rim of the recess keeps this far from a line of the form (a narrower strip of face is a sliver), mm
MIN_LAND = 2.0 + Blueprint.edge_break


class ValuesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.d, self.sp = Blueprint(), spm.SocketPlate()

    def test_the_web_lets_the_sockets_mate(self) -> None:
        self.assertLessEqual(self.sp.web, self.sp.web_max)
        self.assertLess(self.sp.web, self.sp.t)

    def test_the_plate_is_as_thick_as_the_skin_and_its_reveal_is_that_of_the_other_plates(self) -> None:
        self.assertEqual(self.sp.t, self.d.wall_t)
        self.assertEqual(self.sp.reveal, self.d.panel_gap)

    def test_each_variant_has_room_along_the_centre_line(self) -> None:
        for v in spm.VARIANTS:
            for row in spm.layout_rows(self.sp, v):
                if row["gap"] is not None:
                    self.assertGreaterEqual(row["gap"], MIN_GAP, f"{v.key}: {row['item']}")

    def test_the_four_variants_are_two_layouts_with_and_without_the_knob(self) -> None:
        self.assertEqual([v.key for v in spm.VARIANTS], ["a-knob", "a-plain", "b-knob", "b-plain"])
        self.assertEqual([v.knob for v in spm.VARIANTS], [True, False, True, False])

    def test_the_flanges_pass_inside_the_ledge(self) -> None:
        open_half = self.sp.height / 2 - self.sp.ledge
        for kind in "ac":
            self.assertLess(self.sp.row_pitch / 2 + self.sp.back(kind)[1] / 2, open_half)
        self.assertGreaterEqual(self.sp.row_pitch, self.sp.back("a")[1] + 1.0)

    def test_the_pockets_stay_inside_the_plate(self) -> None:
        for kind in "ac":
            self.assertLessEqual(self.sp.pocket(kind)[1] + 1.5, self.sp.height / 2)

    def test_the_button_has_its_flat_face_clear_of_the_screw_heads_and_the_rim(self) -> None:
        for v in spm.VARIANTS:
            flat = self.sp.button_flat_d / 2
            self.assertLessEqual(abs(v.button_s) + flat, self.sp.length / 2)
            self.assertGreaterEqual(abs(self.sp.screws()[0] - v.button_s), flat + self.sp.head_d / 2)

    def test_the_knob_has_what_the_audio_research_asks_for(self) -> None:
        self.assertEqual(self.sp.knob_hole_d, 9.4)
        self.assertEqual(self.sp.knob_flat_d, 22.0)
        self.assertEqual(self.sp.knob_clear, 20.0)
        self.assertTrue(self.sp.knob_wall[0] <= self.sp.web <= self.sp.knob_wall[1])
        self.assertTrue(spm.variant(spm.DEFAULT).knob)

    def test_the_flat_faces_and_the_screw_heads_on_the_front_do_not_overlap(self) -> None:
        for v in spm.VARIANTS:
            for row in spm.outside_rows(self.sp, v):
                if row["gap"] is not None:
                    self.assertGreaterEqual(row["gap"], MIN_GAP, f"{v.key}: {row['item']}")

    def test_one_row_does_not_fit_the_flat_and_the_plate_does(self) -> None:
        flat = spm.flat_face(self.sp, self.d)
        self.assertAlmostEqual(flat["length"], 153.0, delta=0.05)
        self.assertGreater(flat["one_row_sockets_only"], flat["longest_plate"])
        self.assertLessEqual(self.sp.length, flat["longest_plate"])

    def test_nothing_of_the_hardware_is_below_the_floor(self) -> None:
        _, _, zc = self.sp.centre(self.d)
        low = zc - self.sp.row_pitch / 2 - self.sp.back("a")[1] / 2
        self.assertGreater(low, self.sp.floor_t)
        self.assertGreater(zc - self.sp.button_nut_d / 2, self.sp.floor_t)


class PlaceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.d, self.sp = Blueprint(), spm.SocketPlate()

    def test_the_recess_lies_on_the_flat_of_the_deck_side(self) -> None:
        x, y, z = self.sp.centre(self.d)
        a, b = self.sp.half(self.sp.reveal)
        self.assertAlmostEqual(x, self.d.width / 2)
        self.assertGreaterEqual(y - a - pr.deck_plan(self.d)[0].q[1], MIN_LAND)
        self.assertGreaterEqual(self.d.deck_top - self.d.deck_lean_h - (z + b), MIN_LAND)
        self.assertGreaterEqual(z - b - self.d.base_facet, MIN_LAND)

    def test_it_ends_in_front_of_seam_d2_and_clear_of_the_other_seams(self) -> None:
        rows = spm.seam_distances(self.sp, self.d)
        self.assertAlmostEqual(rows["seam D2 (deck to body), behind the recess"], self.sp.d2_gap)
        self.assertGreater(rows["seam F1 / F2 (flank break of the deck front), across the deck"], 100.0)
        self.assertGreater(rows["seam D1 (under the control panel), across the deck"], 40.0)

    def test_the_plate_is_in_the_middle_of_the_upright_face(self) -> None:
        _, _, z = self.sp.centre(self.d)
        self.assertAlmostEqual(z - self.d.base_facet, self.d.deck_top - self.d.deck_lean_h - z)


class SolidsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d, cls.sp = Blueprint(), spm.SocketPlate()
        cls.plates = {v.key: spm.plate(cls.sp, cls.d, v) for v in spm.VARIANTS}

    def test_the_knob_is_the_only_difference_between_the_two_forms_of_a_layout(self) -> None:
        knob = 3.14159265 / 4 * (self.sp.knob_hole_d ** 2 * self.sp.web + self.sp.knob_pocket_d ** 2 * (self.sp.t - self.sp.web))
        for layout in "ab":
            self.assertAlmostEqual(self.plates[f"{layout}-plain"].Volume - self.plates[f"{layout}-knob"].Volume, knob, delta=0.5)

class SeatTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d, cls.sp = Blueprint(), spm.SocketPlate()
        cls.deck, _ = so.deck(cls.d)
        cls.seated = spm.seat(cls.deck, cls.sp, cls.d, hollow=False)

    @support.slow
    def test_the_cut_changes_the_deck_at_the_seat_only(self) -> None:
        x, y, z = self.sp.centre(self.d)
        a, b = self.sp.half(self.sp.reveal + self.d.edge_break)  # the recess, and the edge break round its rim
        gone = self.deck.cut(self.seated)
        bb = gone.optimalBoundingBox(False, False)
        self.assertGreaterEqual(bb.YMin, y - a - 1e-6)
        self.assertLessEqual(bb.YMax, y + a + 1e-6)
        self.assertGreaterEqual(bb.ZMin, z - b - 1e-6)
        self.assertLessEqual(bb.ZMax, z + b + 1e-6)
        self.assertGreaterEqual(bb.XMin, x - self.d.wall_t - self.sp.frame_t - spm.OVER - 1e-6)

    def test_the_plate_lies_in_the_recess_with_the_reveal_all_round(self) -> None:
        p = spm.plate(self.sp, self.d, spm.variant(spm.DEFAULT))
        self.assertLess(self.seated.common(p).Volume, 1e-3)
        # a section of both in the plane of the outer face less the edge break: the gap is the reveal
        gap, _, _ = self.seated.distToShape(p)
        self.assertLess(gap, 1e-6)  # the plate rests on the ledge
        side = spm.Frame(self.sp, self.d).prism(self.sp.length / 2 + self.sp.reveal - 0.01, self.sp.height / 2 + self.sp.reveal - 0.01,
                                               self.sp.radius(self.sp.reveal - 0.01), self.d.edge_break, self.sp.t - 0.01)
        self.assertLess(self.seated.common(side).Volume, 1e-3)

if __name__ == "__main__":
    unittest.main()
