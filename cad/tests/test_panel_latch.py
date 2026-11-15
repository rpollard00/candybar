"""The latch study of the control panel (candybar.shell.panel_latch): the four candidates, their way out, their hold
with its factor, the strain of what flexes, and what each one asks of the interface. Options A and B of
panel_frame stay as they are (test_panel_frame tests them)."""
from __future__ import annotations

import functools
import math
import unittest
from dataclasses import replace

import Part

from candybar.shell import panel_frame as pf, panel_latch as pl, split
from candybar.shell.dims import Blueprint


@functools.cache
def values():
    return pf.values()


@functools.cache
def built(c: str) -> pl.Candidate:
    return pl.build(c, v=values())


@functools.cache
def scene() -> tuple[Part.Shape, pf.Hardware]:
    d = Blueprint()
    if not split.skin_cached(d):
        split.build_modules(d, log=lambda text: None)
    deck = pf.deck_skin(d, log=lambda text: None)
    return deck, pf.hardware(d, deck)


@functools.cache
def report(c: str) -> dict:
    return pl.check(built(c), *scene(), values())


class DefaultTest(unittest.TestCase):
    def test_the_default_stays_the_screws_and_option_b_stays_as_it_is(self) -> None:
        self.assertEqual(pf.Interface().latch, pf.SCREW)
        b = pf.Interface(latch=pf.MAGNET)
        self.assertEqual((b.magnet_d, b.magnet_h, b.keeper_h), (12.0, 5.0, 2.0))

    def test_every_candidate_keeps_the_four_latch_points_and_the_pocket_of_option_b(self) -> None:
        d = Blueprint()
        for c in pl.CANDIDATES:
            i = pl.interface(c)
            self.assertEqual(i.latch, pf.MAGNET, c)
            self.assertEqual((i.magnet_d, i.keeper_h), (12.0, 2.0), c)
            self.assertEqual(pf.latch_points(d, i), pf.latch_points(d, pf.Interface()), c)


class PartsTest(unittest.TestCase):
    def test_each_part_is_one_valid_solid(self) -> None:
        for c in pl.CANDIDATES:
            for name, s in built(c).printed.items():
                self.assertTrue(s.isValid() and len(s.Solids) == 1, f"{c} {name}")

    def test_the_toe_of_a_hook_lies_between_its_two_arcs_about_the_pivot(self) -> None:
        """So that it slides out of the notch when the front goes up: no point of the toe behind the stem is nearer to
        the pivot than the arc under the roof of the notch."""
        d, L = Blueprint(), pl.L0
        i = pl.interface("H")
        yp, zp = pl.pivot(d, i)
        h = pl.hook(d, i, L.hook_x)
        face = pl.rear_bar_face(d, i)
        r_in = math.hypot(yp - (face - i.bond_gap), zp - L.notch_top) + L.toe_clear
        behind = [v.Point for v in h.Vertexes if v.Point.y > face - L.stem_gap + 1e-6]
        self.assertTrue(behind)
        for p in behind:
            r = math.hypot(p.y - yp, p.z - zp)
            self.assertGreaterEqual(r, r_in - 1e-6)
            self.assertLessEqual(r, L.toe_r_out + 1e-6)

    def test_the_neck_of_the_bolt_holds_the_strike_when_the_bolt_is_back(self) -> None:
        L = pl.L0
        n0, n1 = pl.neck(L)
        self.assertLessEqual(n0 + L.stroke, L.lug_y[0] - L.neck_front + 1e-9)
        self.assertGreaterEqual(n1 + L.stroke, L.lug_y[1] + L.neck_margin - 1e-9)
        # locked, the full section of the bolt lies over the whole lug but its first 0.25
        self.assertLess(n1, L.lug_y[0] + 0.5)

    def test_the_button_is_flush_with_the_leaning_band_and_inside_it(self) -> None:
        d, L = Blueprint(), pl.L0
        b = pl.bolt(d, L)
        crease = d.deck_top - d.deck_lean_h
        self.assertGreater(L.button_z - L.button_d / 2, crease)
        self.assertLess(L.button_z + L.button_d / 2, 62.6)
        for v in b.Vertexes:
            self.assertGreaterEqual(v.Point.y, pl.band_y(v.Point.z, d) - 1e-6)

    def test_the_cams_stand_on_the_straight_part_of_the_front_edge(self) -> None:
        """At the flank break (x 137) the front edge of the opening turns back 8 degrees; a cam outside it met the bar."""
        d = Blueprint()
        xc = d.deck_centre_frac * d.width / 2
        # locked, the tongue points to the front; free, it points to the centre: the boss sets the outer edge
        L = pl.L0
        self.assertLess(L.cam_x + max(L.cam_hub_d / 2, L.cam_tongue[0] / 2) + 1.0, xc)


class WayOutTest(unittest.TestCase):
    """The real motion in steps: the latch opens, the panel swings about its rear top edge, then it goes up and forward."""

    def test_every_candidate_leaves_its_pocket_without_a_clash(self) -> None:
        for c in pl.CANDIDATES:
            rows = report(c)["motion"]
            self.assertGreater(len(rows), 6, c)
            self.assertEqual([r for r in rows if r["result"] != "PASS"], [], c)

    def test_the_locks_hold_until_they_are_released(self) -> None:
        for c in ("H", "B", "Q"):
            rows = report(c)["locks"]
            self.assertTrue(rows, c)
            self.assertEqual([r for r in rows if r["result"] != "PASS"], [], c)

    def test_a_hook_with_a_flat_toe_does_not_swing_out(self) -> None:
        """The arcs matter: a toe with a flat top meets the roof of the notch in the swing."""
        cd = built("H")
        d, i = cd.d, cd.i
        h = pl.hook(d, i, pl.L0.hook_x)
        b = h.BoundBox
        flat = pf.box(b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, pl.L0.notch_top - 0.2)
        frame = cd.frame["frame_right"]
        hit = max(pf.common_volume(pl.placed(flat, pl.Step("s", swing=a), d, i), frame) for a in (4.0, 8.0, 12.0))
        self.assertGreater(hit, pf.TOL)

    def test_the_panel_does_not_swing_out_with_the_bolt_forward(self) -> None:
        cd = built("B")
        d, i = cd.d, cd.i
        strike = pl.strike(d, i)
        vol = pf.common_volume(pl.placed(strike, pl.Step("s", swing=3.0), d, i), pl.bolt(d))
        self.assertGreater(vol, pf.TOL)

    def test_the_springs_lift_the_front_edge_when_the_bolt_is_back(self) -> None:
        cd = built("B")
        self.assertGreater(pl.lifted_rise(cd), 5.0)
        self.assertGreater(pl.lifted_by_springs(cd), 2.0)


class HoldTest(unittest.TestCase):
    def test_the_magnet_estimate_follows_the_maker_data(self) -> None:
        """46 N for an N52 disc of 12 x 5 on thick steel (one maker); the fit gives the same within 1 N."""
        m = pl.magnet_pull(5.0, 0.0)
        self.assertAlmostEqual(m["case1_frame_N"], 46.0, delta=1.0)
        # the gap and the use take more than a third off
        self.assertLess(pl.magnet_pull(5.0, 2.0)["pull_N"], 0.66 * pl.magnet_pull(5.0, 2.0)["pair_contact_N"])

    def test_magnets_alone_and_hooks_with_magnets_do_not_hold_the_pull(self) -> None:
        for c in ("M", "H"):
            self.assertLess(report(c)["hold"]["factor"], 1.0, c)

    def test_the_bolt_and_the_cams_hold_with_a_factor_of_two(self) -> None:
        for c in ("B", "Q"):
            self.assertGreaterEqual(report(c)["hold"]["factor"], 2.0, c)

    def test_every_candidate_sits_without_a_click_in_normal_play(self) -> None:
        for c in pl.CANDIDATES:
            self.assertGreaterEqual(report(c)["play"]["factor"], 2.0, c)

    def test_the_hooks_do_not_count_in_the_swing(self) -> None:
        """The swing about the rear top edge is how the hooks let go: there only the front holds."""
        cd = built("H")
        v = values()
        rows = pl.hold(cd, v, loads=[{"name": "to the rear", "f": (0.0, cd.L.side, 0.0)}])["rows"]
        self.assertIn("magnet pair", rows[0]["governs"])

    def test_a_plate_with_nothing_but_its_weight_lifts_at_its_weight(self) -> None:
        cd = built("M")
        bare = replace(cd.L, magnet_points={**cd.L.magnet_points, "M": ()})
        cd = replace(cd, L=bare)
        rows = pl.hold(cd, values(), loads=[{"name": "up", "f": (0.0, 0.0, 10.0)}])["rows"]
        self.assertLessEqual(rows[0]["factor"], bare.panel_weight / 10.0 + 1e-6)

    def test_the_wedge_of_the_bolt_locks_by_friction_and_preloads_the_panel(self) -> None:
        p = pl.bolt_preload()
        self.assertTrue(p["self_locking"])
        self.assertGreater(p["net_N"], 2 * 4.3)  # the front lifts about 4.3 N in normal play
        self.assertLess(p["button_force_N"], 20.0)


class StrainTest(unittest.TestCase):
    def test_no_printed_part_of_the_built_candidates_bends_when_it_moves(self) -> None:
        for c in pl.CANDIDATES:
            for row in report(c)["strain"]:
                self.assertIn(row["strain_pct"], (0.0, None), f"{c} {row['feature']}")

    def test_the_detent_that_was_not_built_bends_below_yield(self) -> None:
        dt = pl.detent()
        self.assertLess(dt["strain_pct"] / 100, pl.L0.abs_yield_strain)
        # and it lets go only above its hold, through the lever: about twice the hold
        self.assertGreater(dt["release_on_lever_N"], 1.5 * dt["hold_N"])


class InterfaceTest(unittest.TestCase):
    def test_each_candidate_names_what_it_adds_to_the_interface(self) -> None:
        counts = {c: len(report(c)["interface_rows"]) for c in pl.CANDIDATES}
        self.assertEqual(counts["M"], 1)
        self.assertEqual(counts["H"], 2)
        self.assertGreater(counts["B"], counts["H"])
        self.assertGreater(counts["Q"], counts["H"])

    def test_a_blank_panel_is_made_from_the_interface_of_each_candidate(self) -> None:
        for c in pl.CANDIDATES:
            rows = report(c)["clashes_blank"]
            self.assertTrue(rows, c)
            self.assertEqual([r for r in rows if r["result"] != "PASS"], [], c)


class ChecksTest(unittest.TestCase):
    def test_no_check_fails(self) -> None:
        for c in pl.CANDIDATES:
            self.assertEqual(report(c)["failures"], [], c)

    def test_each_part_fits_the_printer(self) -> None:
        for c in pl.CANDIDATES:
            for r in report(c)["print"]:
                self.assertTrue(r["fits"], f"{c} {r['part']}")

    def test_nothing_shows_on_the_top_face_but_the_heads_of_q(self) -> None:
        for c in ("M", "H", "B"):
            self.assertTrue(report(c)["shows"]["top_in"].startswith("Nothing"), c)
        self.assertTrue(report("Q")["shows"]["top_in"].startswith("Two round heads"))


if __name__ == "__main__":
    unittest.main()
