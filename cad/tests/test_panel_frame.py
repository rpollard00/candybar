"""The control panel of candybar.shell.panel_frame: the interface, the arcade panel, the blank panel, the frame, the
stiffness, the push bolt (quick); and in the slow group, on the real skin of the deck: the checks can still fail, the
panel comes out with the button held and not with a hook under the ledge, and the options (screws, magnets) still
build and pass. The build of the package checks its parts and fails."""
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


@functools.cache
def option(latch: str) -> pf.Built:
    return pf.build(i=pf.Interface(latch=latch), v=values())


def pocket(i: pf.Interface) -> float:
    return i.magnet_d + i.magnet_clear


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

    def test_the_seam_lies_between_the_lever_body_and_the_first_button(self) -> None:
        x = pf.seam_x(self.b.a)
        first = min(p[0] for p in self.h.action) - values()("btn_nut_d") / 2
        self.assertGreaterEqual(x - self.b.i.seam_flange_t, self.h.body_x1)
        self.assertLessEqual(x + self.b.i.seam_flange_t, first)
        self.assertAlmostEqual(self.b.arcade["panel_lever_tile"].BoundBox.XMax, x)
        self.assertAlmostEqual(self.b.arcade["panel_button_tile"].BoundBox.XMin, x)

    def test_the_buttons_are_one_value(self) -> None:
        """Spread (the default: the owner's screw-in buttons): no counterbore, the plate at its full thickness of 5,
        and no pair of buttons nearer than the nut. Snap-in: a counterbore under each hole, to a seat of seat_t."""
        v, a = values(), self.b.a
        bore = v("btn_hole_d") + a.hole_allow + 2 * a.seat_ring
        self.assertEqual(a.buttons, pf.SPREAD)
        self.assertEqual(cylinders(self.whole, bore), 0)
        self.assertLessEqual(self.b.d.panel_t, 5.0)
        closest = min(math.dist(p, q) for k, p in enumerate(self.h.action) for q in self.h.action[k + 1:])
        self.assertGreaterEqual(closest, v("btn_nut_d"))
        snap = replace(a, buttons=pf.SNAP_IN)
        tiles = Part.makeCompound(list(pf.arcade(self.b.d, self.b.i, snap, v).values()))
        self.assertEqual(cylinders(tiles, bore), 8)
        centres = pf.holes(self.b.d, snap, v).action
        self.assertLess(min(math.dist(p, q) for k, p in enumerate(centres) for q in centres[k + 1:]), v("btn_nut_d"))

    def test_the_latch_is_one_value(self) -> None:
        """The push bolt is the default (the owner, 2026-11-15): a pocket for a disc at each latch point and no screw
        hole. The screws (the fall-back) and the magnets alone stay options on the same four points."""
        i, d = self.b.i, self.b.d
        self.assertEqual(i.latch, pf.PUSH_BOLT)
        self.assertEqual(cylinders(self.whole, i.screw_hole_d), 0)
        self.assertTrue(near(support.hole_centres(self.whole, pocket(i)), pf.latch_points(d, i)))
        screw = Part.makeCompound(list(option(pf.SCREW).arcade.values()))
        self.assertTrue(near(support.hole_centres(screw, i.screw_hole_d), pf.latch_points(d, i)))
        magnet = option(pf.MAGNET)
        for part in (magnet.arcade, magnet.frame):
            self.assertTrue(near(support.hole_centres(Part.makeCompound(list(part.values())), pocket(i)), pf.latch_points(d, i)))
        self.assertEqual(magnet.latch, {})


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
            self.assertTrue(near(support.hole_centres(panel, pocket(i)), points))
            self.assertEqual(cylinders(panel, i.cable_bore), 1)

    def test_it_has_the_finger_hole_and_the_arcade_panel_has_none(self) -> None:
        x, yl, dia = self.b.i.push.finger_hole
        self.assertTrue(near(support.hole_centres(self.blank, dia), [(x, pf.y0(self.b.d) + yl)]))
        self.assertEqual(cylinders(self.arcade, dia), 0)

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
        i = option(pf.SCREW).i
        frame = Part.makeCompound(list(option(pf.SCREW).frame.values()))
        self.assertTrue(near(support.hole_centres(frame, i.insert_hole_d), pf.latch_points(self.b.d, i)))
        self.assertGreaterEqual(i.latch_hole_depth, i.latch_screw_l - self.b.d.panel_t + 1.0)


class ChecksTest(unittest.TestCase):
    """The checks of the package pass on the real skin of the deck, and each one finds a fault that is put in."""

    @support.slow
    def test_a_rib_through_a_button_is_found(self) -> None:
        b = built()
        skin, hw = scene()
        bad = pf.arcade(b.d, b.i, replace(b.a, rib_right_x=90.0), values())
        rows = pf.clash_rows(bad, skin, hw)
        self.assertIn(("panel_button_tile", "hardware: Panel", "FAIL"), {(r["part"], r["against"], r["result"]) for r in rows})

    @support.slow
    def test_a_plate_with_no_seat_gap_is_found_in_the_skin_when_it_is_too_large(self) -> None:
        b = built()
        skin, hw = scene()
        large = pf.arcade(b.d, replace(b.i, seat_gap=-1.0), b.a, values())
        rows = pf.clash_rows(large, skin, hw)
        self.assertTrue(any(r["against"] == "skin of the deck" and r["result"] == "FAIL" for r in rows))

    @support.slow
    def test_the_panel_comes_out_with_the_button_held_and_not_without_it(self) -> None:
        rep = report()
        self.assertGreater(len(rep["lift"]), 20)
        self.assertEqual([r for r in rep["lift"] if r["result"] != "PASS"], [])
        self.assertTrue(any(r["step"].startswith("blank panel") for r in rep["lift"]))
        self.assertEqual(len(rep["locks"]), 2)
        self.assertEqual([r for r in rep["locks"] if r["result"] != "PASS"], [])

    @support.slow
    def test_the_options_still_build_and_pass(self) -> None:
        """The screws (the fall-back) and the magnets alone: each passes every check of the package."""
        skin, hw = scene()
        for latch in (pf.SCREW, pf.MAGNET):
            rep = pf.check(option(latch), skin, hw, values())
            self.assertEqual(rep["failures"], [], latch)
            self.assertEqual([r for r in rep["lift"] if r["result"] != "PASS"], [], latch)

    @support.slow
    def test_a_panel_that_hooks_under_the_ledge_does_not_lift_out(self) -> None:
        b = built()
        skin, hw = scene()
        d = b.d
        hook = pf.box(-20, 20, pf.y0(d) + d.panel_d - 12, pf.y0(d) + d.panel_d - 2, pf.z_rest(d) - 9, pf.z_rest(d) - 5)
        rows = pf.lift_rows({**b.arcade, "hook": hook}, hw, b.frame, skin, steps=(3.0,))
        self.assertEqual(rows[0]["result"], "FAIL")

    def test_a_plate_with_no_edge_break_fails_the_edge_rule(self) -> None:
        b = built()
        _, bad, _ = pf.finish_rows({"plate": pf.plate(b.d, b.i)}, b.d, b.i)
        self.assertTrue(any(line.startswith("edge rule: plate") for line in bad), bad)


class StiffnessTest(unittest.TestCase):
    def setUp(self) -> None:
        b = built()
        self.st = pf.stiffness(b.d, b.i, b.a, values())

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


class PushBoltTest(unittest.TestCase):
    """The latch of the default build: the rear hooks, the push bolt in its tunnel, the gate, the magnets in the frame
    and the steel discs in the plate (docs/design/control-panel-latch.md)."""

    def setUp(self) -> None:
        self.b = built()
        self.d, self.i, self.p = self.b.d, self.b.i, self.b.i.push

    def test_the_halves_of_the_frame_meet_at_x_20_and_the_left_half_has_the_tunnel(self) -> None:
        left, right = self.b.frame["frame_left"], self.b.frame["frame_right"]
        g = self.i.half_gap / 2
        self.assertAlmostEqual(left.BoundBox.XMax, self.p.frame_split_x - g, places=4)
        self.assertAlmostEqual(right.BoundBox.XMin, self.p.frame_split_x + g, places=4)
        tunnel = pf.tunnel(self.d, self.i, self.p)
        self.assertLess(tunnel.cut(left).Volume, 1.0)

    def test_the_frame_has_a_magnet_in_each_pad_and_the_plate_a_steel_disc(self) -> None:
        frame = Part.makeCompound([self.b.frame["frame_left"], self.b.frame["frame_right"]])
        self.assertTrue(near(support.hole_centres(frame, pocket(self.i)), pf.latch_points(self.d, self.i)))
        self.assertEqual((self.i.pad_magnet_h(), self.i.keeper_h, self.p.plate_disc), (2.0, 2.0, pf.STEEL))
        hw = pf.latch_hardware(self.d, self.i)
        self.assertEqual(set(hw), {"magnets", "discs", "spring"})
        self.assertEqual(set(pf.latch_split(hw)[0]), {"discs"})

    def test_the_gap_round_the_button_is_the_same_all_round(self) -> None:
        """The button is the outline of its hole in the deck moved in by button_gap: the distance from each point of
        its outline to the hole's outline is button_gap, at the round, the flats and the corners."""
        from candybar.shell import solids as so

        d = self.d
        button = pf.button_outline(d, self.p)
        r, fx, z = d.latch_button_d / 2, d.latch_button_flats / 2, d.latch_button_z
        hole = Part.makeCylinder(r, 1.0, pf.V(0, -0.5, z), pf.V(0, 1, 0)).common(pf.box(-fx, fx, -0.5, 0.5, z - r - 1, z + r + 1))
        corners = [e for e in hole.Edges if abs(e.BoundBox.YLength - 1.0) < 1e-6 and e.BoundBox.XLength < 1e-6 and e.BoundBox.ZLength < 1e-6]
        hole = hole.makeFillet(so.LATCH_CORNER, corners)
        rim = hole.slice(pf.V(0, 1, 0), 0.0)[0]
        gaps = [rim.distToShape(Part.Vertex(q))[0] for w in button.Wires for q in w.discretize(Distance=0.1)]
        self.assertAlmostEqual(min(gaps), self.p.button_gap, places=4)
        self.assertAlmostEqual(max(gaps), self.p.button_gap, places=4)
        self.assertGreater(so.LATCH_CORNER - self.p.button_gap, d.edge_break)

    def test_a_button_with_no_edge_break_fails_the_edge_rule(self) -> None:
        bare = pf.bolt(self.d, self.p).cut(pf.box(-50, 50, -50, 1.5, 0, 100))
        bare = bare.fuse(pf.box(-5, 5, 1.0, 2.0, 53, 57)).removeSplitter()
        _, bad, _ = pf.finish_rows({"latch_bolt": bare}, self.d, self.i)
        self.assertTrue(any(line.startswith("edge rule: latch_bolt") for line in bad), bad)
