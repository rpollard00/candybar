"""The coupon set (candybar.shell.coupons): every part is one valid solid that fits the bed in its print orientation
with no downward face that the set does not state, the pairs go together with the clearance of the joint, the cuts
from the real skin hold the feature they are for, every plate holds its parts, and the sheet for the printer names
every part. The checks also notice a pair that interferes, a hole of the wrong size and an overhang without a reason."""
from __future__ import annotations

import unittest
from dataclasses import replace
from unittest import mock

from candybar.shell import coupon, coupons, joints, split
from candybar.shell.dims import Blueprint

from . import support

SHEET = support.PARAMS.parents[1] / "docs" / "design" / "coupons.md"
SKIN = split.skin_cached(Blueprint())


class CouponSetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lim = coupons.bed()
        cls.items = [it for it in coupons.items() if SKIN or not it.real]
        cls.shapes = {it.name: coupons.to_bed(it.make()) for it in cls.items}
        cls.rows = [coupons.check_item(it, cls.shapes[it.name], cls.lim) for it in cls.items]

    def test_every_stl_is_a_closed_mesh(self) -> None:
        for name, shape in self.shapes.items():
            with self.subTest(part=name):
                m = coupons.closed_mesh(shape)
                self.assertTrue(m.isSolid())
                self.assertFalse(m.hasNonManifolds())
                self.assertAlmostEqual(m.Volume, shape.Volume, delta=0.005 * shape.Volume)  # the chords of the mesh on curved faces

    def test_the_names_are_unique_and_every_coupon_has_a_plate_and_a_purpose(self) -> None:
        names = [it.name for it in coupons.items()]
        self.assertEqual(len(names), len(set(names)))
        plates = {k for k, _ in coupons.PLATES}
        for it in coupons.items():
            with self.subTest(part=it.name):
                self.assertIn(it.plate, plates)
                self.assertIn(it.coupon, coupons.PROVES)
                self.assertIn(it.coupon, coupons.TINT)

    def test_every_part_is_one_valid_solid_that_fits_the_bed(self) -> None:
        for r in self.rows:
            with self.subTest(part=r["part"]):
                self.assertTrue(r["valid"])
                self.assertEqual(r["solids"], 1)
                self.assertTrue(r["fits_bed"], r["box_mm"])
                self.assertGreater(r["mass_g"], 0.5)

    def test_no_part_has_a_downward_face_without_a_reason(self) -> None:
        for r in self.rows:
            with self.subTest(part=r["part"]):
                self.assertEqual(r["unstated_overhang_mm2"], 0.0, r["overhangs"])
                self.assertTrue(r["pass"])

    def test_only_the_wall_of_joint_3_needs_support(self) -> None:
        self.assertEqual([r["part"] for r in self.rows if r["needs_support_mm2"]], ["joint3-wall"])

    def test_every_plate_holds_its_parts(self) -> None:
        layout = coupons.plate_layout(self.rows, self.lim)
        for key, places in layout.items():
            with self.subTest(plate=key):
                self.assertIsNotNone(places)
                for name, (x, y) in places.items():
                    w, h = next(r["box_mm"][:2] for r in self.rows if r["part"] == name.split("#")[0])
                    self.assertLessEqual(x + w, self.lim.xy + 1e-6)
                    self.assertLessEqual(y + h, self.lim.xy + 1e-6)
        self.assertEqual(sum(len(p) for p in layout.values()), sum(r["count"] for r in self.rows))

    def test_the_plates_keep_a_margin_on_the_bed_of_the_printer(self) -> None:
        self.assertEqual(coupons.BED, (270.0, 270.0, 256.0))
        self.assertEqual((self.lim.xy, self.lim.z), (248.0, 250.0))
        self.assertEqual((coupons.BED_MARGIN, coupons.TOP_MARGIN), (11.0, 6.0))
        strip = next(r for r in self.rows if r["part"] == "flat-strip")
        self.assertEqual(strip["box_mm"][0], self.lim.xy)
        self.assertLessEqual(coupons.SHRINK_L + coupons.GAP + coupons.SHRINK_W, self.lim.xy)

    def test_the_facet_and_the_hand_hold_print_two_times_for_the_two_fan_values(self) -> None:
        self.assertEqual({r["part"]: r["count"] for r in self.rows if r["part"] in ("facet45", "hand-hold", "warp-wall")},
                         {"facet45": 2, "hand-hold": 2, "warp-wall": 2})

    def test_the_parts_on_a_plate_do_not_touch(self) -> None:
        sizes = {"a": (100.0, 50.0), "b": (100.0, 50.0), "c": (30.0, 200.0), "d": (220.0, 12.0)}
        at = coupons.pack(sizes, 240.0)
        boxes = [(x, y, x + sizes[k][0], y + sizes[k][1]) for k, (x, y) in at.items()]
        for i, a in enumerate(boxes):
            for b in boxes[i + 1:]:
                self.assertTrue(a[2] + coupons.GAP <= b[0] + 1e-6 or b[2] + coupons.GAP <= a[0] + 1e-6
                                or a[3] + coupons.GAP <= b[1] + 1e-6 or b[3] + coupons.GAP <= a[1] + 1e-6, (a, b))
        self.assertIsNone(coupons.pack({"a": (241.0, 10.0)}, 240.0))
        self.assertIsNone(coupons.pack({"a": (200.0, 130.0), "b": (200.0, 130.0)}, 240.0))

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

    def test_the_sheet_for_the_printer_names_every_part(self) -> None:
        text = SHEET.read_text(encoding="utf-8")
        for it in coupons.items():
            with self.subTest(part=it.name):
                self.assertIn(f"`{it.name}`", text)

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


@unittest.skipUnless(SKIN, "the skin is not in the cache of the split (cad/out/shell-rev7/split/cache)")
class CouponRealTest(unittest.TestCase):
    def test_the_cuts_from_the_real_skin_hold_their_features(self) -> None:
        for name, r in coupons.check_real().items():
            with self.subTest(coupon=name):
                self.assertTrue(r["pass"], r)

    def test_the_rear_facet_is_the_skin_of_the_form(self) -> None:
        d = Blueprint()
        shape = coupons.to_bed(coupons.facet45())
        b = coupons.tight_box(shape)
        self.assertAlmostEqual(b.YLength, d.rear_proud + d.wall_t + joints.JOINT.foot_h, delta=0.01)
        self.assertAlmostEqual(coupons.check_real()["facet45"]["crease_z_above_bed"], d.door_frame, delta=1e-6)

    def test_the_floor_tile_has_the_size_of_the_smallest_tile(self) -> None:
        w, h = coupons.tile_size()
        self.assertAlmostEqual(w, 137.0, delta=1.0)
        self.assertAlmostEqual(h, 163.0, delta=1.0)
