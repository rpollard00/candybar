"""The joint coupon (candybar.shell.coupon): the halves do not interfere, the key and groove have the clearance that
the part name says, the flange faces meet, the screw axes line up, and every part fits the printer's usable volume.
The checks also notice a pair that interferes and a part that does not fit."""
from __future__ import annotations

import unittest
from dataclasses import replace

from candybar.shell import coupon
from candybar.shell.joints import JOINT

from . import support


class CouponPairTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.body = coupon.lower_half(0.1, holes=False)
        cls.pairs = {c: (coupon.lower_half(c), coupon.upper_half(c)) for c in coupon.CLEARANCES}
        cls.checks = {c: coupon.check_pair(JOINT, c, lo, up, cls.body) for c, (lo, up) in cls.pairs.items()}

    def test_the_halves_do_not_interfere(self) -> None:
        for c, r in self.checks.items():
            with self.subTest(clearance=c):
                self.assertTrue(r["valid"])
                self.assertLess(r["common_volume_mm3"], 1e-6)

    def test_the_key_gap_is_the_clearance_in_the_name(self) -> None:
        for c, r in self.checks.items():
            with self.subTest(clearance=c, part=f"coupon-upper-{coupon.tag(c)}"):
                self.assertEqual(coupon.tag(c), f"c{round(c * 10):02d}")
                self.assertAlmostEqual(r["key_gap_side_mm"][0], c, delta=1e-3)
                self.assertAlmostEqual(r["key_gap_side_mm"][1], c, delta=1e-3)
                self.assertAlmostEqual(r["key_gap_end_mm"][0], c, delta=1e-3)
                self.assertGreaterEqual(r["key_gap_top_mm"], JOINT.groove_extra_depth - 1e-3)

    def test_the_flange_faces_meet_and_the_screw_axes_line_up(self) -> None:
        for c, r in self.checks.items():
            with self.subTest(clearance=c):
                self.assertGreater(r["flange_contact_mm2"], 0.6 * JOINT.flange_h * coupon.LENGTH)
                self.assertEqual(r["pilot_holes"], r["screws"])
                self.assertEqual(r["clearance_holes"], r["screws"])
                self.assertLess(r["screw_axis_offset_mm"], 1e-4)
                self.assertLess(r["pilot_breaks_out_mm3"], 1e-6)
                self.assertTrue(r["pass"])

    def test_each_lower_half_has_the_two_pilots_in_their_places(self) -> None:
        self.assertEqual(coupon.stations(), [-30.0, 30.0])
        for c, r in self.checks.items():
            with self.subTest(clearance=c):
                self.assertEqual([(p["s"], p["pilot_d"]) for p in r["pilots"]],
                                 [(-30.0, JOINT.pilot_d_pet), (30.0, JOINT.pilot_d_abs)])
                self.assertTrue(all(p["right_diameter"] for p in r["pilots"]), r["pilots"])

    def test_the_mark_is_beside_the_smaller_pilot(self) -> None:
        mark = coupon.pilot_mark().BoundBox
        x_small = coupon.path().point(-30.0, JOINT.screw_u, 0.0)[0]
        self.assertAlmostEqual((mark.XMin + mark.XMax) / 2, x_small, delta=1.0)
        lo = self.pairs[0.1][0]
        self.assertLess(lo.common(coupon.pilot_mark()).Volume, 1e-6)   # the bar is cut out of the lower half

    def test_the_cabinet_pilot_stays_open_until_the_coupon_decides(self) -> None:
        self.assertIsNone(JOINT.pilot_d)
        with self.assertRaises(ValueError):
            JOINT.pilot()
        self.assertEqual(replace(JOINT, pilot_d=JOINT.pilot_d_pet).pilot(), 2.25)

    def test_the_check_notices_swapped_pilots(self) -> None:
        swapped = replace(JOINT, pilot_d_pet=JOINT.pilot_d_abs, pilot_d_abs=JOINT.pilot_d_pet)
        lo = coupon.lower_half(0.1, swapped)
        r = coupon.check_pair(JOINT, 0.1, lo, self.pairs[0.1][1], self.body)
        self.assertFalse(all(p["right_diameter"] for p in r["pilots"]))
        self.assertFalse(r["pass"])

    def test_the_check_notices_a_key_too_wide_for_its_groove(self) -> None:
        wide = replace(JOINT, key_w=JOINT.key_w + 0.5)
        lo = coupon.lower_half(0.1, wide)
        up = coupon.upper_half(0.1)
        r = coupon.check_pair(wide, 0.1, lo, up, self.body)
        self.assertGreater(r["common_volume_mm3"], 1.0)
        self.assertFalse(r["pass"])


class CouponPrintTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lim = coupon.printer(support.PARAMS)
        cls.parts = {f"lower-{coupon.tag(c)}": coupon.to_bed(coupon.lower_half(c)) for c in coupon.CLEARANCES}
        cls.parts |= {f"upper-{coupon.tag(c)}": coupon.to_bed(coupon.upper_half(c)) for c in coupon.CLEARANCES}
        cls.parts |= {f"plaque-P{k}": coupon.to_bed(coupon.plaque(k)) for k in range(1, 5)}

    def test_every_part_fits_the_bed_in_its_print_orientation(self) -> None:
        for name, shape in self.parts.items():
            with self.subTest(part=name):
                r = coupon.check_part(JOINT, name, shape, self.lim)
                self.assertTrue(r["valid"])
                self.assertTrue(r["fits_bed"], r["box_mm"])
                self.assertEqual(r["unstated_overhang_mm2"], 0.0, r["overhangs"])
                self.assertTrue(r["pass"])

    def test_the_check_notices_a_part_that_does_not_fit(self) -> None:
        small = coupon.Printer(100.0, 245.0)
        r = coupon.check_part(JOINT, "lower-c01", self.parts["lower-c01"], small)
        self.assertFalse(r["fits_bed"])
        self.assertFalse(r["pass"])
