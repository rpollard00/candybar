"""The hood band (candybar.shell.band holds band A of the default build; candybar.shell.hood_band keeps B, C and the
taller hoods as variants): the places, the parts of the band on small solids (quick); and in the slow group, the one
check of the variants: each builds and keeps the outside of the hood.

The parts of the shell that the variants share (the cap of the hood among them) are kept under cad/out/hood-band/base,
as the skin of the split is kept under cad/out/shell-rev7. The first run makes them."""
from __future__ import annotations

import functools
import unittest
from pathlib import Path

import FreeCAD as App
import Part

from candybar.shell import fit, hood_band as hb, profiles as pr
from candybar.shell.dims import Blueprint

from . import support

OUT = Path(__file__).resolve().parents[1] / "out" / "hood-band"
V = App.Vector


@functools.cache
def base() -> dict[str, Part.Shape]:
    return hb.base(OUT, Blueprint(), [])


@functools.cache
def built(key: str) -> dict[str, Part.Shape]:
    parts = base()
    return hb.build(Blueprint(), hb.Band(), hb.Driver(), hb.VARIANTS[key], parts["cap"], parts["opening"])


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
                self.assertGreater(2 * self.b.spk_half_h, self.drv.frame + 2 * self.b.seat_gap + 1.0)
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

    def test_the_light_box_stands_clear_of_the_baffle(self) -> None:
        for key in hb.VARIANTS:
            pl = self.places(key)
            x0, x1, z0, z1 = hb.baffle(self.d, self.h, self.b, pl)
            self.assertGreaterEqual(hb.box_low(self.d, self.h, self.b) - z1, 1.0, key)
            for x, z in pl.opening:
                self.assertTrue(x0 + 3.0 < x < x1 - 3.0 and z0 + 3.0 < z < z1 - 3.0, f"{key}: the baffle goes round the opening")

    def test_the_clamp_bars_lie_on_the_frame_and_inside_the_tunnel(self) -> None:
        b = self.b
        self.assertLess(b.bar_x - b.bar_w / 2, self.drv.frame / 2 - 1.5)
        self.assertLess(b.bar_x + b.bar_w / 2, b.spk_w / 2 - b.grille_gap)
        self.assertGreater(b.screw_x - b.screw_hole / 2, self.drv.frame / 2 + b.seat_gap)
        self.assertLess(b.screw_x + b.screw_hole / 2, b.bar_x + b.bar_w / 2 - 0.5)

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
        self.assertLess(hb.seat(self.d, self.h, self.b, self.drv, pl).common(drv).Volume, 1e-6)

    def test_the_enclosure_holds_its_volume_of_air_and_closes_on_the_baffle(self) -> None:
        for key, v in hb.VARIANTS.items():
            pl = hb.places(self.d, self.h, self.b, v)
            solid, _ = hb.enclosure(self.d, self.h, self.b, self.drv, pl)
            seat, drv = hb.seat(self.d, self.h, self.b, self.drv, pl), hb.driver(self.b, self.drv, pl)
            bb = solid.BoundBox
            w = self.b.encl_wall
            inside = Part.makeBox(bb.XLength - 2 * self.b.baffle_half_w + 2 * self.b.encl_half_w - 2 * w, bb.YLength - w, bb.ZLength - 2 * w,
                                  V(pl.cx - self.b.encl_half_w + w, bb.YMin, bb.ZMin + w))
            air = inside.Volume - inside.common(drv).Volume
            self.assertAlmostEqual(air / 1e6, self.b.encl_litres, places=3, msg=key)
            self.assertLess(inside.common(solid).Volume, 1e-3, key)
            self.assertAlmostEqual(bb.YMin, seat.BoundBox.YMax, places=6, msg=key)
            self.assertLess(solid.common(seat).Volume, 1e-6, key)
            self.assertLess(solid.common(drv).Volume, 1e-6, key)

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


@support.slow
class VariantsTest(unittest.TestCase):

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

