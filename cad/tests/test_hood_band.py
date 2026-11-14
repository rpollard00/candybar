"""The hood band study (candybar.shell.hood_band): the places of each variant, its parts, the edge rule and the face
check on what shows, the room behind the wall, and the way the marquee front comes out.

The parts of the shell that the variants share (the cap of the hood among them) are kept under cad/out/hood-band/base,
as the skin of the split is kept under cad/out/shell-rev7. The first run makes them."""
from __future__ import annotations

import functools
import unittest
from dataclasses import replace
from pathlib import Path

import FreeCAD as App
import Part

from candybar.shell import fit, hood_band as hb, profiles as pr, split
from candybar.shell.dims import Blueprint

OUT = Path(__file__).resolve().parents[1] / "out" / "hood-band"
V = App.Vector


@functools.cache
def base() -> dict[str, Part.Shape]:
    return hb.base(OUT, Blueprint(), [])


@functools.cache
def built(key: str) -> dict[str, Part.Shape]:
    parts = base()
    return hb.build(Blueprint(), hb.Band(), hb.Driver(), hb.VARIANTS[key], parts["cap"], parts["opening"])


@functools.cache
def checked(key: str) -> dict:
    d, b, v = Blueprint(), hb.Band(), hb.VARIANTS[key]
    h = pr.hood(d)
    skin = hb.hood_skin(d, h, b, v, hb.places(d, h, b, v))
    return hb.check(built(key), base(), d, b, hb.Driver(), v, skin)


class PlacesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.d, self.b, self.drv = Blueprint(), hb.Band(), hb.Driver()
        self.h = pr.hood(self.d)

    def places(self, key: str) -> hb.Places:
        return hb.places(self.d, self.h, self.b, hb.VARIANTS[key])

    def test_each_speaker_opening_lies_in_the_band_and_clear_of_the_seam(self) -> None:
        for key in hb.VARIANTS:
            pl = self.places(key)
            xs, zs = [p[0] for p in pl.opening], [p[1] for p in pl.opening]
            with self.subTest(variant=key):
                self.assertGreaterEqual(min(zs) - self.h.z_sill, 5.0)
                self.assertGreaterEqual(self.h.z_band_top - max(zs), 5.0)
                self.assertGreaterEqual(min(xs), 106.0 + 5.0, "the seam H1 of the hood is at x 106")
                for x, z in pl.opening:
                    self.assertGreaterEqual(hb.leg(self.h, self.d, z) - x, 8.0)

    def test_the_frame_of_the_driver_passes_the_opening(self) -> None:
        for key in hb.VARIANTS:
            pl = self.places(key)
            with self.subTest(variant=key):
                self.assertGreater(2 * self.b.spk_half_h, self.drv.frame + 1.0)
                self.assertGreater(max(p[0] for p in pl.opening) - pl.cx, self.b.screw_x + self.b.screw_hole / 2 + 1.0)

    def test_the_driver_is_inside_the_largest_frame_of_the_fit_study(self) -> None:
        """fit.speaker_room gives 53.9: the height of the stand-in form (57.9) less a margin of 2 on each side."""
        quad, _ = fit.speaker_face(self.d, self.h)
        largest = 2 * (fit.largest_circle(quad)[2] - fit.Layout().speaker_frame_margin)
        self.assertAlmostEqual(largest, 53.9, places=1)
        self.assertLessEqual(self.drv.frame, largest)

    def test_the_mouth_of_the_light_box_is_the_marquee_room_of_the_fit_study(self) -> None:
        _, room = fit.marquee_box(self.d, self.h, 25.0)
        win = hb.window(self.d, self.h, self.b)
        z0 = self.h.origin[2] + win[0][1] - self.b.box_margin_z
        self.assertAlmostEqual(z0, room["fit_mq_z0"], places=6)
        self.assertAlmostEqual(self.b.mq_h + 2 * self.b.box_margin_z, room["fit_mq_h"], places=6)
        self.assertEqual(self.b.mq_w, room["fit_mq_w"])
        self.assertAlmostEqual(self.h.origin[1] + self.h.y_band_top + self.b.wall_t + self.b.seat_off, room["fit_mq_y"], places=6)

    def test_the_window_lies_between_the_lip_and_the_top_bar(self) -> None:
        win = hb.window(self.d, self.h, self.b)
        self.assertGreaterEqual(win[0][1] - self.h.z_rail_top, 2.0)
        self.assertGreaterEqual(self.h.z_open_top - win[2][1], 2.0)

    def test_the_light_box_stands_clear_of_the_driver_seat(self) -> None:
        flange_low = hb.window(self.d, self.h, self.b)[0][1] - self.b.box_margin_z - self.b.box_wall - self.b.box_flange
        for key in hb.VARIANTS:
            seat_top = max(p[1] for p in self.places(key).opening) + self.b.seat_flange
            self.assertGreaterEqual(flange_low - seat_top, 2.0, key)

    def test_the_front_lifts_far_enough_to_come_out(self) -> None:
        """The front lifts by the gap under the top bar. That frees the hooks, and the foot leaves the groove."""
        b = self.b
        self.assertGreater(b.mq_front_gap, b.hook_hold + 0.3)
        self.assertGreater(b.mq_front_gap, b.lip_round)
        self.assertGreaterEqual(b.lip_groove, b.mq_front_t + 0.3)

    def test_a_pod_leaves_a_land_on_its_front(self) -> None:
        for key, v in hb.VARIANTS.items():
            if not v.pod_proud:
                continue
            pl = self.places(key)
            land = (pl.pod[2][1] - pl.pod[0][1]) / 2 - self.b.spk_half_h - self.b.pod_edge_r - self.b.edge_break
            self.assertGreaterEqual(land, 2.0, key)


class PartsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.d, self.b, self.drv = Blueprint(), hb.Band(), hb.Driver()
        self.h = pr.hood(self.d)

    def test_a_loop_with_round_corners_has_the_area_of_its_polygon_less_the_corners(self) -> None:
        face = Part.Face(hb.loop(hb.rect(0.0, 0.0, 40.0, 20.0), 4.0))
        self.assertAlmostEqual(face.Area, 800.0 - (4 - 3.141592653589793) * 16.0, places=6)

    def test_grow_moves_each_side_out(self) -> None:
        quad = [(0.0, 0.0), (10.0, 0.0), (8.0, 6.0), (0.0, 6.0)]
        grown = Part.Face(hb.loop(hb.grow(quad, 1.0), 0.0))
        self.assertAlmostEqual(grown.distToShape(Part.Vertex(V(5.0, 0.0, 0.0)))[0], 0.0)
        for p, q in zip(quad, quad[1:] + quad[:1]):
            mid = V((p[0] + q[0]) / 2, 0.0, (p[1] + q[1]) / 2)
            self.assertAlmostEqual(Part.Wire(grown.OuterWire).distToShape(Part.Vertex(mid))[0], 1.0, places=6)

    def test_each_grille_leaves_two_fifths_of_the_cone_open(self) -> None:
        for key, v in hb.VARIANTS.items():
            area = hb.open_area(self.b, v, self.drv, hb.places(self.d, self.h, self.b, v))
            self.assertGreaterEqual(area["share"], 0.4, key)

    def test_a_grille_in_a_pod_has_clamp_bars_and_a_flush_grille_has_none(self) -> None:
        box = lambda key: hb.grille(self.b, hb.VARIANTS[key], hb.places(self.d, self.h, self.b, hb.VARIANTS[key])).BoundBox.YLength
        self.assertAlmostEqual(box("B"), self.b.grille_t, places=6)
        self.assertGreater(box("A"), hb.VARIANTS["A"].pod_proud)

    def test_the_seat_holds_the_frame_proud_so_that_the_grille_clamps_it(self) -> None:
        v = hb.VARIANTS["B"]
        pl = hb.places(self.d, self.h, self.b, v)
        grille, drv = hb.grille(self.b, v, pl), hb.driver(self.b, self.drv, pl)
        self.assertAlmostEqual(grille.BoundBox.YMax - drv.BoundBox.YMin, 0.0, places=6)
        self.assertLess(hb.seat(self.b, self.drv, pl).common(drv).Volume, 1e-6)

    def test_the_driver_has_the_depth_of_its_values(self) -> None:
        drv = hb.driver(self.b, self.drv, hb.places(self.d, self.h, self.b, hb.VARIANTS["A"]))
        self.assertAlmostEqual(drv.BoundBox.YLength, self.drv.frame_t + self.drv.basket_depth + self.drv.magnet_depth, places=6)

    def test_a_block_with_sharp_edges_fails_the_edge_rule(self) -> None:
        block = Part.makeBox(40.0, 10.0, 30.0, V(100.0, 440.0, 460.0))
        sharp = hb.sharp_edges_that_show({"speaker_pod_right": block}, {k: Part.makeBox(1, 1, 1, V(0, 900, 0)) for k in hb.BASE},
                                         self.d, hb.Scene({"speaker_pod_right": block}))
        self.assertTrue(sharp)
        self.assertTrue(all(e["turn"] > self.d.edge_break_turn for e in sharp))

    def test_an_edge_against_another_part_is_in_a_joint(self) -> None:
        block = Part.makeBox(40.0, 10.0, 30.0, V(100.0, 440.0, 460.0))
        wall = Part.makeBox(200.0, 10.0, 200.0, V(0.0, 450.0, 400.0))
        rear = [e for e in block.Edges if all(abs(v.Y - 450.0) < 1e-9 for v in e.Vertexes)]
        front = [e for e in block.Edges if all(abs(v.Y - 440.0) < 1e-9 for v in e.Vertexes)]
        self.assertTrue(all(hb.in_joint(block, e, [wall]) for e in rear))
        self.assertFalse(any(hb.in_joint(block, e, [wall]) for e in front))


class VariantsTest(unittest.TestCase):
    def test_each_variant_passes_its_checks(self) -> None:
        for key in hb.VARIANTS:
            with self.subTest(variant=key):
                self.assertEqual(checked(key)["failures"], [])

    def test_each_part_is_one_valid_solid_and_the_left_is_the_mirror_of_the_right(self) -> None:
        for key in hb.VARIANTS:
            parts = built(key)
            for name, s in parts.items():
                self.assertTrue(s.isValid() and len(s.Solids) == 1, f"{key} {name}")
            for name in parts:
                if name.endswith("_right") and not name.startswith("marquee_front"):
                    self.assertAlmostEqual(parts[name].Volume, parts[name.replace("_right", "_left")].Volume, places=3, msg=f"{key} {name}")

    def test_no_stand_in_is_left_and_each_part_has_a_class(self) -> None:
        for key in hb.VARIANTS:
            names = set(built(key))
            self.assertFalse(names & {"marquee_lip", "speaker_left", "speaker_right", "logo_form"}, key)
            self.assertTrue(all(hb.kind(n) in hb.PARTS for n in names), key)

    def test_the_bands_differ_as_the_variants_say(self) -> None:
        self.assertIn("speaker_pod_right", built("A"))
        self.assertNotIn("speaker_pod_right", built("B"))
        self.assertIn("logo_field", built("A"))
        self.assertIn("logo_backer", built("B"))
        self.assertNotIn("logo_badge", built("C"))

    def test_the_cap_keeps_its_outside(self) -> None:
        """The openings of a band are all behind the front of the band wall: the hood has the box of the cap."""
        d = Blueprint()
        h = pr.hood(d)
        cap = base()["cap"].translated(V(*h.origin)).BoundBox
        for key in hb.VARIANTS:
            bb = built(key)["hood"].BoundBox
            for a, c in zip((bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax), (cap.XMin, cap.YMin, cap.ZMin, cap.XMax, cap.YMax, cap.ZMax)):
                self.assertAlmostEqual(a, c, places=3, msg=key)
            lost = base()["cap"].Volume - built(key)["hood"].Volume
            self.assertGreater(lost, 0.0)
            self.assertLess(lost, 400.0 * 110.0 * 2 * hb.Band().wall_t)

    def test_no_part_of_a_band_stands_in_front_of_the_hood(self) -> None:
        d = Blueprint()
        y_front = base()["cap"].BoundBox.YMin + pr.hood(d).origin[1]
        for key in hb.VARIANTS:
            for name, s in built(key).items():
                self.assertGreaterEqual(s.BoundBox.YMin, y_front, f"{key} {name}")

    def test_the_marquee_front_comes_out_when_it_is_lifted(self) -> None:
        d, b, v = Blueprint(), hb.Band(), hb.VARIANTS["B"]
        if not split.skin_cached(d):
            self.skipTest("the skin of the hood is not in the cache of the split")
        h = pr.hood(d)
        parts = built("B")
        fixed = [hb.hood_skin(d, h, b, v, hb.places(d, h, b, v)), parts["marquee_lip_right"], parts["marquee_lip_left"]]
        front = parts["marquee_front_right"]
        down = sum(front.common(s).Volume for s in fixed)
        self.assertLess(down, 0.5)
        held = front.translated(V(0, -1.0, 0))
        self.assertGreater(sum(held.common(s).Volume for s in fixed), 1.0, "the lip and the hook hold the front when it is down")
        lifted = front.translated(V(0, 0, b.mq_front_gap - 0.1))
        for step in range(0, 13):
            out = lifted.translated(V(0, -step, 0))
            self.assertLess(sum(out.common(s).Volume for s in fixed), 0.5, f"the lifted front, {step} mm out")

    def test_the_inside_parts_are_in_the_cavity_of_the_hood(self) -> None:
        if not split.skin_cached(Blueprint()):
            self.skipTest("the skin of the hood is not in the cache of the split")
        for key in hb.VARIANTS:
            rep = checked(key)
            self.assertTrue(rep["skin_checked"])
            self.assertEqual(rep["room"]["shared"], [], key)

    def test_a_driver_that_is_too_deep_is_found(self) -> None:
        if not split.skin_cached(Blueprint()):
            self.skipTest("the skin of the hood is not in the cache of the split")
        d, b, v = Blueprint(), hb.Band(), hb.VARIANTS["B"]
        h = pr.hood(d)
        pl = hb.places(d, h, b, v)
        deep = hb.driver(b, replace(hb.Driver(), magnet_depth=140.0), pl).translated(V(*h.origin))
        rm = hb.room({"driver_right": deep}, hb.hood_skin(d, h, b, v, pl))
        self.assertTrue(rm["shared"])
