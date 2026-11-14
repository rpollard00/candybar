"""The structure data of candybar.shell.structure reads the form from dims.Blueprint: the hand-holds, the door and
the rear shelf. The frame of the study's option C is not in the code."""
from __future__ import annotations

import unittest
from dataclasses import replace

from candybar.shell import split, structure
from candybar.shell.dims import Blueprint


class HandHoldsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.d = Blueprint()

    def test_the_grip_box_is_the_recess_of_the_blueprint(self) -> None:
        d = self.d
        self.assertEqual(structure.grip_box(d), (d.grip_x0, d.grip_x1, d.depth - d.grip_depth, d.depth, d.grip_z0, d.grip_z0 + d.grip_h))

    def test_the_lift_follows_the_place_of_the_recess(self) -> None:
        """A deeper recess has its middle farther forward, so the hand-holds carry more of the weight."""
        a = structure.hand_holds(20.0, 330.0, self.d)
        b = structure.hand_holds(20.0, 330.0, replace(self.d, grip_depth=self.d.grip_depth + 20.0))
        self.assertAlmostEqual(a["grip_y"], self.d.depth - self.d.grip_depth / 2)
        self.assertAlmostEqual(b["grip_y"], a["grip_y"] - 10.0)
        self.assertGreater(b["lift_N"], a["lift_N"])

    def test_the_design_load_in_each_recess_is_the_lift_with_a_factor_of_two(self) -> None:
        hh = structure.hand_holds(20.0, 330.0, self.d)
        self.assertAlmostEqual(hh["lift_N"], 20.0 * structure.G * 330.0 / hh["grip_y"])
        self.assertAlmostEqual(hh["each_design_N"], 2 * hh["each_N"])
        self.assertAlmostEqual(hh["pivot_lift"]["load_N"], hh["each_design_N"])
        self.assertAlmostEqual(hh["straight_lift"]["load_N"], hh["weight_N"])

    def test_a_wider_recess_bends_the_wall_above_it_more(self) -> None:
        a = structure.hand_holds(20.0, 330.0, self.d)
        b = structure.hand_holds(20.0, 330.0, replace(self.d, grip_x1=self.d.grip_x1 + 40.0))
        self.assertGreater(b["pivot_lift"]["wall_above_MPa"], a["pivot_lift"]["wall_above_MPa"])

    def test_the_hand_hold_member_is_the_recess(self) -> None:
        member = next(m for m in structure.members(self.d) if m.name == "hand-hold")
        self.assertEqual(member.box, structure.grip_box(self.d))
        self.assertTrue(member.mirror)


class MembersFollowTheFormTest(unittest.TestCase):
    def setUp(self) -> None:
        self.d = Blueprint()
        self.members = {m.name: m for m in structure.members(self.d, board=(-161.0, 146.0))}

    def test_the_door_frame_goes_round_the_door_of_the_blueprint(self) -> None:
        d, box = self.d, self.members["door opening frame"].box
        self.assertLess(box[0], -d.door_w / 2)
        self.assertGreater(box[1], d.door_w / 2)
        self.assertLess(box[4], d.door_z0)
        self.assertGreater(box[5], d.door_z1)

    def test_the_belt_ring_lies_at_the_crease_of_the_rear_shelf(self) -> None:
        self.assertEqual(self.members["ring B1"].box[5], self.d.rear_shelf_z0)

    def test_the_carrier_goes_round_the_board_of_the_fit_study(self) -> None:
        box = self.members["BC-250 carrier"].box
        self.assertLess(box[0], -161.0)
        self.assertGreater(box[1], 146.0)
        self.assertNotIn("BC-250 carrier", {m.name for m in structure.members(self.d)})

    def test_no_frame_of_the_study_is_left(self) -> None:
        self.assertEqual([n for n in vars(structure) if "frame_c" in n.lower() or "extrusion" in n.lower()], [])
        self.assertEqual({m.kind for m in self.members.values()} - set(structure.KIND_WORDS), set())
        self.assertNotIn("frame", structure.KIND_WORDS)

    def test_the_split_has_one_layout(self) -> None:
        self.assertEqual([n for n in vars(split) if n.startswith("option_") or n in ("OPTIONS_ORDER", "CHOSEN", "ALL", "options")], [])


if __name__ == "__main__":
    unittest.main()
