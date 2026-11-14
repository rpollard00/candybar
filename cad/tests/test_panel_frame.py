"""The control panel of candybar.shell.panel_frame: the interface, the arcade panel on the hardware of fit.Layout,
the blank panel, the frame, and the checks of the package on the real skin of the deck."""
from __future__ import annotations

import functools
import math
import unittest
from dataclasses import replace

import Part

from candybar.shell import fit, panel_frame as pf, split
from candybar.shell import profiles as pr
from candybar.shell.dims import Blueprint

from . import support


@functools.cache
def values():
    return pf.values()


@functools.cache
def built() -> pf.Built:
    return pf.build(v=values())


@functools.cache
def scene() -> tuple[Part.Shape, pf.Hardware]:
    """The skin of the deck round the pocket, from the cached skin of the shell (made here when the cache is empty),
    and the hardware of the fit study."""
    d = built().d
    if not split.skin_cached(d):
        split.build_modules(d, log=lambda text: None)
    deck = pf.deck_skin(d, log=lambda text: None)
    return pf.pocket_skin(d, deck), pf.hardware(d, deck)


@functools.cache
def report() -> dict:
    return pf.check(built(), *scene(), values())


def cylinders(shape: Part.Shape, diameter: float) -> int:
    return len(support.hole_centres(shape, diameter))


def near(a: list[tuple[float, float]], b: list[tuple[float, float]]) -> bool:
    return len(a) == len(b) and all(math.dist(p, q) < 1e-6 for p, q in zip(sorted(a), sorted(b)))


class InterfaceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.d, self.i = Blueprint(), pf.Interface()

    def test_the_plate_stands_the_seat_gap_inside_the_outline_of_the_form(self) -> None:
        plate = pf.plate(self.d, self.i)
        outline = pr.panel_outline(self.d)
        self.assertAlmostEqual(plate.BoundBox.XMax, outline[3][0] - self.i.seat_gap)
        self.assertAlmostEqual(plate.BoundBox.YMax, outline[4][1] - self.i.seat_gap)
        self.assertAlmostEqual(plate.BoundBox.ZMax, self.d.panel_top)
        self.assertAlmostEqual(plate.BoundBox.ZMin, self.d.panel_top - self.d.panel_t)

    def test_the_latch_points_lie_inside_the_opening_and_mirror_each_other(self) -> None:
        points = pf.latch_points(self.d, self.i)
        hole = pf.plan(pf.opening(self.d, self.i), 0.0, 1.0)
        for x, y in points:
            self.assertTrue(hole.isInside(pf.V(x, y, 0.5), 1e-6, False))
        self.assertAlmostEqual(points[0][0], -points[1][0])
        self.assertAlmostEqual(points[3][0], -points[2][0])
        self.assertAlmostEqual(points[0][1], points[1][1])

    def test_the_cones_stand_at_the_rear_edge_one_each_side(self) -> None:
        (xa, ya), (xb, yb) = pf.cone_points(self.d, self.i)
        self.assertEqual((xa, xb), (-self.i.cone_x, self.i.cone_x))
        self.assertAlmostEqual(ya, pf.opening(self.d, self.i)[4][1] - self.i.cone_in)
        self.assertEqual(ya, yb)

    def test_the_panel_goes_in_one_way(self) -> None:
        """The outline is not the same when it is turned half a turn, and the two sockets are not alike."""
        outline = pr.panel_outline(self.d)
        mid = (outline[1][1] + outline[4][1]) / 2
        turned = sorted((round(-x, 6), round(2 * mid - y, 6)) for x, y in outline)
        self.assertNotEqual(turned, sorted((round(x, 6), round(y, 6)) for x, y in outline))
        self.assertGreater(self.i.cone_slot, 0.0)


class ArcadeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.b = built()
        self.h = pf.holes(self.b.d, self.b.a, values())
        self.whole = Part.makeCompound(list(self.b.arcade.values()))

    def test_each_tile_is_one_valid_solid(self) -> None:
        for name, tile in self.b.arcade.items():
            self.assertTrue(tile.isValid(), name)
            self.assertEqual(len(tile.Solids), 1, name)

    def test_the_holes_are_where_the_fit_study_puts_the_hardware(self) -> None:
        v, a = values(), self.b.a
        _, hw = scene()
        caps = {s.name: s.world.BoundBox.Center for s in hw.solids(("Panel",), ("protrusion",))}
        action = [(caps[f"Btn{k}_Cap"].x, caps[f"Btn{k}_Cap"].y) for k in range(1, 9)]
        service = [(caps[f"Svc{k}_Cap"].x, caps[f"Svc{k}_Cap"].y) for k in range(1, 4)]
        self.assertTrue(near(support.hole_centres(self.whole, v("btn_hole_d") + a.hole_allow), action))
        self.assertTrue(near(support.hole_centres(self.whole, v("svc_hole_d") + a.hole_allow), service))
        self.assertTrue(near(support.hole_centres(self.b.arcade["panel_lever_tile"], v("stick_shaft_hole_d")), [(caps["Lever_Ball"].x, caps["Lever_Ball"].y)]))

    def test_the_seat_of_the_lever_is_the_plate_drop_below_the_top(self) -> None:
        v, d = values(), self.b.d
        _, hw = scene()
        plate = next(s.world for s in hw.solids(("Panel",)) if s.name == "Lever_Plate")
        self.assertAlmostEqual(self.h.lever_seat_z, plate.BoundBox.ZMax)
        self.assertAlmostEqual(d.panel_top - self.h.lever_seat_z, v("stick_plate_drop"))
        self.assertTrue(near(support.hole_centres(self.b.arcade["panel_lever_tile"], v("stick_insert_d")), list(self.h.lever_mount)))

    def test_the_seam_lies_between_the_lever_body_and_the_first_button(self) -> None:
        x = pf.seam_x(self.b.a)
        first = min(p[0] for p in self.h.action) - values()("btn_nut_d") / 2
        self.assertGreaterEqual(x - self.b.i.flange_t, self.h.body_x1)
        self.assertLessEqual(x + self.b.i.flange_t, first)
        self.assertAlmostEqual(self.b.arcade["panel_lever_tile"].BoundBox.XMax, x)
        self.assertAlmostEqual(self.b.arcade["panel_button_tile"].BoundBox.XMin, x)

    def test_the_buttons_are_one_value(self) -> None:
        """Snap-in: a counterbore under each hole, to a seat of seat_t. Spread: no counterbore, and no pair of
        buttons nearer than the nut."""
        v, a = values(), self.b.a
        bore = v("btn_hole_d") + a.hole_allow + 2 * a.seat_ring
        self.assertEqual(a.buttons, pf.SNAP_IN)
        self.assertEqual(cylinders(self.whole, bore), 8)
        spread = replace(a, buttons=pf.SPREAD)
        tiles = Part.makeCompound(list(pf.arcade(self.b.d, self.b.i, spread, v).values()))
        self.assertEqual(cylinders(tiles, bore), 0)
        centres = pf.holes(self.b.d, spread, v).action
        closest = min(math.dist(p, q) for k, p in enumerate(centres) for q in centres[k + 1:])
        self.assertGreaterEqual(closest, v("btn_nut_d"))
        self.assertLess(min(math.dist(p, q) for k, p in enumerate(self.h.action) for q in self.h.action[k + 1:]), v("btn_nut_d"))

    def test_the_latch_is_one_value(self) -> None:
        i = self.b.i
        self.assertEqual(i.latch, pf.SCREW)
        self.assertEqual(cylinders(self.whole, i.screw_hole_d), 4)
        magnet = replace(i, latch=pf.MAGNET)
        tiles = Part.makeCompound(list(pf.arcade(self.b.d, magnet, self.b.a, values()).values()))
        self.assertEqual(cylinders(tiles, i.screw_hole_d), 0)
        self.assertTrue(near(support.hole_centres(tiles, i.magnet_d + i.magnet_clear), pf.latch_points(self.b.d, i)))
        frame = Part.makeCompound(list(pf.frame(self.b.d, magnet).values()))
        self.assertTrue(near(support.hole_centres(frame, i.magnet_d + i.magnet_clear), pf.latch_points(self.b.d, i)))


class BlankTest(unittest.TestCase):
    """The second panel has the interface and nothing else."""

    def setUp(self) -> None:
        self.b = built()
        self.blank = Part.makeCompound(list(self.b.blank.values()))
        self.arcade = Part.makeCompound(list(self.b.arcade.values()))

    def test_it_has_the_latch_points_and_the_clip_of_the_arcade_panel(self) -> None:
        i = self.b.i
        points = pf.latch_points(self.b.d, i)
        for panel in (self.blank, self.arcade):
            self.assertTrue(near(support.hole_centres(panel, i.screw_hole_d), points))
            self.assertEqual(cylinders(panel, i.cable_bore), 1)

    def test_its_sockets_take_the_cones_of_the_frame(self) -> None:
        frame = Part.makeCompound([self.b.frame["frame_left"], self.b.frame["frame_right"]])
        for panel in (self.blank, self.arcade):
            self.assertLess(panel.common(frame).Volume, 1e-6)
            self.assertAlmostEqual(panel.distToShape(frame)[0], min(self.b.i.pad_drop, self.b.i.cone_clear), places=6)

    def test_it_has_no_hole_for_hardware(self) -> None:
        v = values()
        for name in ("btn_hole_d", "svc_hole_d"):
            self.assertEqual(cylinders(self.blank, v(name) + self.b.a.hole_allow), 0)

    def test_it_has_the_outline_of_the_arcade_panel(self) -> None:
        a, b = self.blank.BoundBox, self.arcade.BoundBox
        for p, q in ((a.XMin, b.XMin), (a.XMax, b.XMax), (a.YMin, b.YMin), (a.YMax, b.YMax), (a.ZMin, b.ZMin), (a.ZMax, b.ZMax)):
            self.assertAlmostEqual(p, q)


class FrameTest(unittest.TestCase):
    def setUp(self) -> None:
        self.b = built()

    def test_the_bar_lies_under_the_ledge_and_the_pads_stand_in_the_opening(self) -> None:
        d, i = self.b.d, self.b.i
        zr = d.panel_top - d.panel_t
        for name in ("frame_left", "frame_right"):
            half = self.b.frame[name]
            self.assertTrue(half.isValid() and len(half.Solids) == 1, name)
            # above the lower face of the ledge the half stands inside the opening, the bond gap from its edge
            above = half.common(pf.box(-1e3, 1e3, -1e3, 1e3, zr - d.wall_t, 1e3))
            ledge = pf.plan(pr.panel_outline(d), zr - d.wall_t, zr + 10).cut(pf.plan(pf.opening(d, i), zr - d.wall_t - 1, zr + 11))
            self.assertLess(above.common(ledge).Volume, 1e-6)
            self.assertAlmostEqual(above.distToShape(ledge)[0], i.bond_gap, places=6)

    def test_the_posts_stand_on_the_floor_under_the_bar(self) -> None:
        d, i = self.b.d, self.b.i
        for name, post in self.b.frame.items():
            if not name.startswith("post"):
                continue
            self.assertAlmostEqual(post.BoundBox.ZMin, fit.Layout().floor_t)
            self.assertAlmostEqual(post.BoundBox.ZMax, d.panel_top - d.panel_t - d.wall_t - i.bond_gap - i.bar_h - i.bond_gap)

    def test_the_insert_is_under_each_screw(self) -> None:
        i = self.b.i
        frame = Part.makeCompound(list(self.b.frame.values()))
        self.assertTrue(near(support.hole_centres(frame, i.insert_hole_d), pf.latch_points(self.b.d, i)))
        self.assertGreaterEqual(i.insert_hole_depth, i.screw_l - self.b.d.panel_t + 1.0)


class ChecksTest(unittest.TestCase):
    """The checks of the package pass on the real skin of the deck, and each one finds a fault that is put in."""

    def test_no_check_fails(self) -> None:
        self.assertEqual(report()["failures"], [])

    def test_no_part_meets_the_skin_the_hardware_or_another_part(self) -> None:
        rows = report()["clashes"] + report()["clashes_blank"]
        self.assertGreater(len(rows), 30)
        self.assertEqual([r for r in rows if r["result"] != "PASS"], [])

    def test_a_rib_through_a_button_is_found(self) -> None:
        b = built()
        skin, hw = scene()
        bad = pf.arcade(b.d, b.i, replace(b.a, rib_right_x=90.0), values())
        rows = pf.clash_rows(bad, skin, hw)
        self.assertIn(("panel_button_tile", "hardware: Panel", "FAIL"), {(r["part"], r["against"], r["result"]) for r in rows})

    def test_a_plate_with_no_seat_gap_is_found_in_the_skin_when_it_is_too_large(self) -> None:
        b = built()
        skin, hw = scene()
        large = pf.arcade(b.d, replace(b.i, seat_gap=-1.0), b.a, values())
        rows = pf.clash_rows(large, skin, hw)
        self.assertTrue(any(r["against"] == "skin of the deck" and r["result"] == "FAIL" for r in rows))

    def test_the_hardware_of_the_panel_lies_in_the_room_below_the_plate(self) -> None:
        rows = report()["room"]
        self.assertEqual([r for r in rows if r["result"] != "PASS"], [])
        self.assertTrue(any(r["what"].startswith("Lever_Tip") for r in rows))

    def test_the_panel_lifts_straight_out(self) -> None:
        self.assertEqual([r for r in report()["lift"] if r["result"] != "PASS"], [])

    def test_a_panel_that_hooks_under_the_ledge_does_not_lift_out(self) -> None:
        b = built()
        skin, hw = scene()
        d = b.d
        hook = pf.box(-20, 20, pf.y0(d) + d.panel_d - 12, pf.y0(d) + d.panel_d - 2, pf.z_rest(d) - 9, pf.z_rest(d) - 5)
        rows = pf.lift_rows({**b.arcade, "hook": hook}, hw, b.frame, skin, steps=(3.0,))
        self.assertEqual(rows[0]["result"], "FAIL")

    def test_each_part_fits_the_printer_and_needs_no_support(self) -> None:
        rows = report()["print"]
        self.assertEqual(len(rows), 10)
        for r in rows:
            self.assertTrue(r["fits"], r["part"])
            # a tile lies on its top face: the round of the edge break and the countersinks are all that looks down
            self.assertLess(r["overhang_cm2"], 6.0, r["part"])
            if not r["part"].startswith(("panel", "blank")):
                self.assertEqual(r["overhang_cm2"], 0.0, r["part"])

    def test_no_sharp_edge_shows_and_no_face_fails(self) -> None:
        rep = report()
        for name, r in rep["edge_finish"].items():
            self.assertEqual([g for g in r["sharp"] if not g["against"]], [], name)
            self.assertEqual(sum(rep["face_check"].get(name, {}).get(k, 0) for k in ("sliver", "needle", "crowded", "kink", "split")), 0, name)
        for name in (*built().arcade, *built().blank):
            self.assertGreater(rep["edge_finish"][name]["break_faces"], 0, name)

    def test_a_plate_with_no_edge_break_fails_the_edge_rule(self) -> None:
        b = built()
        _, bad, _ = pf.finish_rows({"plate": pf.plate(b.d, b.i)}, b.d, b.i)
        self.assertTrue(any(line.startswith("edge rule: plate") for line in bad), bad)


class StiffnessTest(unittest.TestCase):
    def setUp(self) -> None:
        b = built()
        self.st = pf.stiffness(b.d, b.i, b.a, values())

    def test_the_load_is_the_couple_of_the_research_note(self) -> None:
        self.assertEqual(self.st["couple_Nmm"], 40.0 * 60.0)

    def test_the_ribs_make_the_seat_of_the_lever_stiffer(self) -> None:
        ribs, flat = self.st["cases"]["with the ribs"], self.st["cases"]["flat plate of 5, no ribs"]
        self.assertLess(ribs["forward_ball_mm"] * 10, flat["forward_ball_mm"])
        self.assertLess(ribs["side_ball_mm"] * 10, flat["side_ball_mm"])
        self.assertLess(max(ribs["forward_ball_mm"], ribs["side_ball_mm"]), 0.2)

    def test_a_tee_is_stiffer_than_its_flange(self) -> None:
        self.assertAlmostEqual(pf.tee(50.0, 5.0, 0.0, 0.0001), 50.0 * 125.0 / 12, places=3)
        self.assertGreater(pf.tee(50.0, 5.0, 3.0, 15.0), 5 * 50.0 * 125.0 / 12)


if __name__ == "__main__":
    unittest.main()
