"""The coupon set (candybar.shell.coupons), on the coupons that do not come from the skin: their values, the latch pair
against the hook of the panel, the pairs with the clearance of the joint, and the checks that notice a pair that
interferes, a part that does not fit and an overhang without a reason. The build of the set (candybar.shell.coupons)
checks every part, plate, overhang and the cuts from the real skin, and fails on them."""
from __future__ import annotations

import unittest
from dataclasses import replace
from unittest import mock

from candybar.shell import coupon, coupons, joints
from candybar.shell.dims import Blueprint

from . import support



class CouponSetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lim = coupons.bed()
        # only the coupons that these tests read: none of them is cut from the skin (the real cuts and the floor tile are)
        names = ("shrink-x", "shrink-y", "holes-buttons", "holes-lever", "holes-power", "holes-usb", "joint3-wall")
        cls.items = [it for it in coupons.items() if it.name in names]
        cls.shapes = {it.name: coupons.to_bed(it.make()) for it in cls.items}
        cls.rows = [coupons.check_item(it, cls.shapes[it.name], cls.lim) for it in cls.items]

    def test_the_hook_strip_holds_the_whole_hook_and_seats_in_the_notch_strip(self) -> None:
        """The pair of the rear corner: in the cabinet the hook strip holds the whole hook at x +100, it seats in the
        notch strip with no common volume, and a lift of 1 makes the toe meet the roof of the notch (the lock)."""
        from candybar.shell import panel_frame as pf

        b = coupons.latch_build()
        hook_strip = coupons.turned(coupons.latch_hook(), (1, 0, 0), 180)
        notch_strip = coupons.latch_notch()
        hook = pf.hook(b.d, b.i, b.i.push.hook_x, b.i.push)
        self.assertAlmostEqual(hook_strip.common(hook).Volume, hook.Volume, delta=0.01 * hook.Volume)
        self.assertLess(hook_strip.common(notch_strip).Volume, 1e-3)
        lifted = hook_strip.translated(pf.V(0, 0, 1.0))
        self.assertGreater(lifted.common(notch_strip).Volume, pf.TOL)

    def test_the_names_are_unique_and_every_coupon_has_a_plate_and_a_purpose(self) -> None:
        names = [it.name for it in coupons.items()]
        self.assertEqual(len(names), len(set(names)))
        plates = {k for k, _ in coupons.PLATES}
        for it in coupons.items():
            with self.subTest(part=it.name):
                self.assertIn(it.plate, plates)
                self.assertIn(it.coupon, coupons.PROVES)
                self.assertIn(it.coupon, coupons.TINT)

    def test_the_shrink_bars_have_their_stops_at_half_and_full_length(self) -> None:
        for name, axis in (("shrink-x", 0), ("shrink-y", 1)):
            with self.subTest(part=name):
                r = next(r for r in self.rows if r["part"] == name)
                self.assertEqual(r["box_mm"][axis], coupons.SHRINK_L)
                top = [f for f in self.shapes[name].Faces if abs(f.BoundBox.ZMin - coupons.STOP_H) < 1e-6]
                ends = sorted({round((f.BoundBox.XMax, f.BoundBox.YMax)[axis], 3) for f in top})
                self.assertEqual(ends, [coupons.STOP_L, coupons.SHRINK_L / 2, coupons.SHRINK_L])

    def test_the_hole_coupons_have_the_holes_of_the_parameter_sheets(self) -> None:
        v = coupons.controls(support.PARAMS)
        up = (0, 0, 1)
        self.assertEqual(coupons.holes_of(self.shapes["holes-buttons"], up),
                         {v["svc_hole_d"]: 1, v["svc_hole_d"] + coupons.HOLE_PLUS: 1, v["btn_hole_d"]: 1, v["btn_hole_d"] + coupons.HOLE_PLUS: 1})
        lever = coupons.holes_of(self.shapes["holes-lever"], up)
        self.assertEqual(lever[v["stick_insert_d"]], 4)
        self.assertEqual(lever[v["stick_shaft_hole_d"]], 1)
        self.assertEqual(coupons.holes_of(self.shapes["holes-power"], (0, 1, 0)), {d: 1 for d in coupons.POWER_HOLES})
        self.assertEqual(coupons.holes_of(self.shapes["holes-usb"], up)[coupons.USB_HOLE], 4)

    def test_the_edge_bar_has_the_round_and_the_break_of_the_form(self) -> None:
        d = Blueprint()
        radii = sorted(round(f.Surface.Radius, 3) for f in coupons.edge_bar().Faces if type(f.Surface).__name__ == "Cylinder")
        self.assertEqual(radii, [d.edge_break, d.edge_break, d.rear_round_r])
        self.assertEqual(len(coupons.EDGE_NAMES), 6)
        self.assertTrue(set(coupons.EDGE_NAMES) <= set(coupons.EDGE_SECTION))

    def test_the_check_notices_an_overhang_without_a_reason(self) -> None:
        it = next(i for i in self.items if i.name == "joint3-wall")
        r = coupons.check_item(replace(it, stated=()), self.shapes[it.name], self.lim)
        self.assertGreater(r["unstated_overhang_mm2"], 900.0)
        self.assertFalse(r["pass"])

    def test_the_check_notices_a_part_that_does_not_fit(self) -> None:
        it = next(i for i in self.items if i.name == "shrink-x")
        r = coupons.check_item(it, self.shapes[it.name], coupon.Printer(200.0, 245.0))
        self.assertFalse(r["fits_bed"])
        self.assertFalse(r["pass"])


class CouponPairsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checks = coupons.check_pairs()

    def test_the_pairs_go_together(self) -> None:
        for name, r in self.checks.items():
            with self.subTest(pair=name):
                self.assertTrue(r["pass"], r)
                self.assertLess(r.get("common_volume_mm3", 0.0), 1e-6)

    def test_the_clearances_are_those_of_the_joints(self) -> None:
        o, j = joints.OTHER_JOINTS, joints.JOINT
        self.assertEqual(self.checks["joint2"]["cone_gap_mm"], [o.cone_clearance] * 2)
        self.assertEqual(self.checks["joint3"]["key_gap_side_mm"], [j.groove_clearance] * 2)
        self.assertEqual(self.checks["joint3"]["key_gap_end_mm"], [j.groove_clearance] * 2)
        self.assertEqual([s["gap_mm"] for s in self.checks["cone"]["sockets"]], list(coupons.CONE_CLEARANCES))

    def test_the_insert_holes_are_the_hole_of_the_joint_and_two_larger(self) -> None:
        self.assertEqual(coupons.insert_holes(), [5.6, 5.7, 5.8])
        self.assertEqual(coupons.insert_holes()[0], joints.OTHER_JOINTS.insert_hole_d)
        self.assertEqual(self.checks["joint5"]["behind_insert_mm"], coupons.INSERT_BOSS - coupons.INSERT_DEPTH)

    def test_the_screws_of_the_concept_are_longer_than_the_parts_they_join(self) -> None:
        """A finding for the owner of joints.py, held here so that it does not go away unseen."""
        self.assertEqual(self.checks["joint2"]["screw_longer_than_floor_mm"], 2.0)
        self.assertEqual(self.checks["joint3"]["screw_through_flange_mm"], 2.0)

    def test_the_holes_of_the_floor_screw_follow_joint_1(self) -> None:
        s = coupons.base_screw()
        self.assertEqual(s, {"d": 3.5, "pilots": [2.6, 2.8], "clearance": 3.95, "head": 7.0})

    def test_the_weld_pair_has_the_section_of_joint_1_and_the_abs_pilot(self) -> None:
        j = joints.JOINT
        r = self.checks["weld"]
        self.assertGreater(r["seam_contact_mm2"], 0.6 * (j.flange_h + j.wall_t) * coupons.WELD_L)
        self.assertEqual(r["holes_lower"][j.pilot_d_abs], 1)
        b = coupons.tight_box(coupons.weld_upper())
        self.assertAlmostEqual(b.YLength, j.wall_t + j.flange_h, delta=1e-6)

    def test_the_check_notices_a_cone_that_does_not_go_into_its_socket(self) -> None:
        tight = replace(joints.OTHER_JOINTS, cone_clearance=-0.2)
        with mock.patch.object(coupons, "OTHER_JOINTS", tight):
            upper = coupons.joint2_upper()
        self.assertGreater(coupons.joint2_lower().common(upper).Volume, 1.0)

    def test_the_check_notices_a_key_too_wide_for_its_slot(self) -> None:
        wide = replace(joints.OTHER_JOINTS, foot_key_w=joints.OTHER_JOINTS.foot_key_w + 1.0)
        with mock.patch.object(coupons, "OTHER_JOINTS", wide):
            wall = coupons.joint3_wall()
        self.assertGreater(wall.common(coupons.joint3_floor()).Volume, 1.0)


