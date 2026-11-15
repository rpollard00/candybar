"""The monitor cradle and the printed bezel plate (candybar.shell.cradle): the parts are valid solids, the plate keeps
the form of the shell's plate and has no sharp edge that shows, the fastening goes together, the monitor fits its
jaws and comes out to the front, the parts fit the printer, and the checks notice a part that is in the way.

The tests of CradleInTheBodyTest read the built shell (cradle.shell_dir: the BREP of each part and fit/report.json)
and the skin in the cache of the split. They do not build the shell."""
from __future__ import annotations

import functools
import math
import unittest
from dataclasses import replace

import FreeCAD as App
import Part

from candybar.shell import cradle as cr
from candybar.shell import profiles as pr
from candybar.shell import solids as so
from candybar.shell import split
from candybar.shell.dims import MON_ACTIVE_H, MON_ACTIVE_W, Blueprint

from . import support

V = App.Vector
D = Blueprint()
C = cr.Cradle()


@functools.cache
def parts() -> dict[str, Part.Shape]:
    return cr.build(D, C, cr.PRESENT)


@functools.cache
def nominal() -> Part.Shape:
    return so.bezel(D, pr.front(D))


class ValuesTest(unittest.TestCase):
    def test_the_lock_screw_of_a_jaw_stays_in_its_slot_for_every_unit(self) -> None:
        thin = replace(cr.PRESENT, h=MON_ACTIVE_H + 6.0, bezel_bottom=3.0)        # 3 of bezel at the top and the bottom
        for unit, shift in ((cr.PRESENT, 0.0), (thin, 0.0), (cr.GENERIC, C.adjust), (cr.GENERIC, -C.adjust)):
            for sv in (-1, 1):
                with self.subTest(unit=unit.name, shift=shift, end=sv):
                    v = abs(cr.screw_v(C, unit, sv, shift))
                    self.assertGreaterEqual(v - C.screw_hole / 2, C.slot_v0)
                    self.assertLessEqual(v + C.screw_hole / 2, C.slot_v1)

    def test_the_lock_screw_is_inside_the_opening_for_any_unit(self) -> None:
        f = cr.Frame(D)
        for sv in (-1, 1):
            v = abs(cr.screw_v(C, cr.GENERIC, sv, sv * C.adjust))
            self.assertLess(v + 1.5, f.half_len - 6.0)       # the key of 2.5 goes in beside the ledge

    def test_the_uprights_stand_behind_the_thickest_monitor(self) -> None:
        back = cr.glass_t(D, C) + cr.GENERIC.t
        self.assertGreaterEqual(cr.bed_t(D, C) - back, C.pad_back + C.rest_min - 1e-9)

    def test_the_lugs_are_inside_the_centre_pieces_of_the_split(self) -> None:
        """The apron ends at the panel's front corner (x 137) and the brow at the hood's bay line (x 106)."""
        self.assertLess(C.lug_x1, 106.0 - 4.0)
        self.assertGreater(C.lug_x0, 0.0)

    def test_the_room_that_is_left_at_the_largest_shrink(self) -> None:
        room = cr.room_rows(D, C, cr.PRESENT)
        worst = room[f"shrink {max(C.shrink) * 100:.2f} %"]
        # at the larger shrink of printed ABS, 0.69 % (it was 0.76 % for PETG: 5.69 and 16.69)
        self.assertAlmostEqual(worst["any unit with plugs at full adjustment, each side"], 5.84, delta=0.02)
        self.assertAlmostEqual(worst["present unit with plugs, each side"], 16.84, delta=0.02)
        self.assertGreater(worst["any unit at full adjustment, bottom and top"], 10.0)
        self.assertGreater(worst["lock screw of a jaw inside the opening, any unit at full adjustment"], 2.5)
        self.assertLess(worst["pin moves along its slot when the plate and the body differ by the spread of the shrink"], C.pin_slot_play)
        self.assertGreaterEqual(min(worst["gap round the plate when they differ by that spread: side, end"]), 0.0)

    def test_the_loads_have_a_margin(self) -> None:
        rows = cr.loads(D, C, cr.PRESENT, parts()["bezel_plate"])
        for unit in rows["units"].values():
            self.assertGreater(unit[f"bottom jaws: friction over the load at {C.shock:g} g"], 2.0)
            self.assertGreater(unit["tilted"]["90 deg forward"]["grip of the pads over it"], 1.5)
        self.assertGreater(rows["plate"]["magnets_N"], 2 * rows["plate"]["solid_kg"] * cr.G * math.sin(math.radians(60.0)))
        self.assertLess(rows["lug"]["bending_MPa"], 1.0)


class PartsTest(unittest.TestCase):
    def test_each_part_is_made_of_valid_closed_solids(self) -> None:
        count = {"bezel_plate": 1, "lugs": 4, "bosses": 4, "upright_right": 1, "upright_left": 1, "jaws": 4, "shoes": 4, "channel_right": 1, "channel_left": 1}
        for name, n in count.items():
            with self.subTest(part=name):
                s = parts()[name]
                self.assertTrue(s.isValid())
                self.assertEqual(len(s.Solids), n)
                self.assertTrue(all(x.isClosed() for x in s.Solids))

    def test_the_left_parts_are_the_mirror_images_of_the_right_parts(self) -> None:
        for name in ("upright", "channel"):
            right, left = parts()[f"{name}_right"], parts()[f"{name}_left"]
            self.assertAlmostEqual(right.Volume, left.Volume, places=3)
            self.assertLess(cr.mirror_x(right).cut(left).Volume, 1e-3)

    def test_the_printed_parts_do_not_meet_each_other_or_the_monitor(self) -> None:
        p = parts()
        names = list(cr.PRINTED + cr.ADDED + ("monitor",))
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                with self.subTest(a=a, b=b):
                    self.assertLess(cr.volume_in(p[a], p[b]), cr.TOL_VOLUME)

    def test_the_monitor_lies_in_its_jaws(self) -> None:
        p = parts()
        self.assertAlmostEqual(cr.gap(p["monitor"], p["bezel_plate"]), C.glass_gap, places=3)
        self.assertAlmostEqual(cr.gap(p["monitor"], p["jaws"]), C.pad_back, places=3)       # the felt on the rest
        self.assertLess(cr.volume_in(p["pads"], p["monitor"]), cr.TOL_VOLUME)
        self.assertLess(cr.volume_in(p["pads"], p["jaws"]), cr.TOL_VOLUME)
        self.assertLess(cr.gap(p["pads"], p["monitor"]), 1e-6)
        self.assertGreaterEqual(cr.gap(p["jaws"], p["bezel_plate"]), C.jaw_front_gap + C.glass_gap - 1e-6)

    def test_a_jaw_for_a_thick_monitor_keeps_its_rest(self) -> None:
        jaw = cr.jaw(D, C, cr.GENERIC, 1, -1, -C.adjust)
        self.assertTrue(jaw.isValid())
        self.assertLess(cr.volume_in(jaw, cr.monitor(D, C, cr.GENERIC, dv=-C.adjust)), cr.TOL_VOLUME)
        self.assertLess(cr.volume_in(jaw, parts()["upright_right"]), cr.TOL_VOLUME)
        self.assertLess(cr.volume_in(jaw, parts()["lugs"]), cr.TOL_VOLUME)


    def test_a_housing_from_10_45_to_10_6_lies_on_the_rests_of_its_jaws(self) -> None:
        """The owner measured 10.45 to 10.6 (2026-11-14). The jaws are made for 10.6. The screen leans back, so the
        housing lies on the felt of the rests: a thinner one has its glass farther from the plate by the difference."""
        f, p = cr.Frame(D), parts()
        pads = cr.pads(D, C, cr.PRESENT)
        for t in (cr.PRESENT_T_MIN, cr.PRESENT.t):
            back = cr.PRESENT.t - t
            unit = cr.monitor(D, C, replace(cr.PRESENT, t=t)).translated(f.into * back)
            with self.subTest(t=t):
                self.assertLess(cr.volume_in(unit, p["jaws"]), cr.TOL_VOLUME)
                self.assertLess(cr.volume_in(unit, pads), cr.TOL_VOLUME)
                self.assertLess(cr.volume_in(unit, p["bezel_plate"]), cr.TOL_VOLUME)
                self.assertLess(cr.gap(unit, pads), 1e-3)                                   # it lies on the felt
                self.assertAlmostEqual(cr.gap(unit, p["bezel_plate"]), C.glass_gap + back, delta=1e-3)


class BezelPlateTest(unittest.TestCase):
    def test_the_plate_has_the_form_of_the_shells_plate(self) -> None:
        plate = cr.bezel_plate(D, C, back=False)
        self.assertLess(plate.cut(nominal()).Volume, 1e-3)                       # nothing stands outside the nominal plate
        lost = nominal().Volume - plate.Volume
        rim = 2 * C.plate_fit * (D.bezel_w + D.bezel_len) * 20.0                # the strip of the fit, at most 20 thick
        self.assertGreater(lost, 0.0)
        self.assertLess(lost, rim)
        land = max(plate.Faces, key=lambda f: f.Area if isinstance(f.Surface, Part.Cylinder) else 0.0)
        self.assertAlmostEqual(land.Surface.Radius, pr.front(D).rail.r - D.bezel_drop, places=6)

    def test_the_plate_is_smaller_than_its_recess_by_the_fit(self) -> None:
        f = cr.Frame(D)
        plate = parts()["bezel_plate"]
        xs = [v.Point.x for v in plate.Vertexes]
        self.assertAlmostEqual(max(xs), f.half_w - C.plate_fit, delta=1e-3)
        self.assertAlmostEqual(min(xs), -(f.half_w - C.plate_fit), delta=1e-3)
        self.assertAlmostEqual(cr.gap(plate, cr.fit_box(D, 0.0).cut(cr.fit_box(D, C.plate_fit / 2))), C.plate_fit / 2, delta=1e-3)

    def test_no_convex_edge_of_the_plate_that_shows_is_sharp(self) -> None:
        plate = parts()["bezel_plate"]
        self.assertEqual(cr.plate_break_edges(plate, D), [])
        from tools import face_check
        breaks = [f for f in plate.Faces if face_check.is_break(f, D.edge_break)]
        self.assertEqual(len(breaks), 12)

    def test_the_nominal_plate_has_sharp_edges_and_the_check_finds_them(self) -> None:
        self.assertEqual(len(cr.plate_break_edges(nominal(), D)), 12)

    def test_the_window_is_the_lit_image(self) -> None:
        f = cr.Frame(D)
        rim = [f.local(v.Point) for v in parts()["bezel_plate"].Vertexes if abs(f.local(v.Point)[2] - f.t0) < 1e-6
               and abs(f.local(v.Point)[0]) < MON_ACTIVE_W / 2 + 1 and abs(f.local(v.Point)[1]) < MON_ACTIVE_H / 2 + 1]
        self.assertAlmostEqual(max(p[0] for p in rim), MON_ACTIVE_W / 2, delta=1e-3)
        self.assertAlmostEqual(max(p[1] for p in rim), MON_ACTIVE_H / 2, delta=1e-3)

    def test_the_pins_and_the_magnets_go_into_the_plate_and_the_lugs(self) -> None:
        p = parts()
        self.assertLess(cr.volume_in(p["pins"], p["bezel_plate"]), cr.TOL_VOLUME)
        self.assertLess(cr.volume_in(p["magnets"], p["bezel_plate"]), cr.TOL_VOLUME)
        self.assertLess(cr.volume_in(p["magnets"], p["lugs"]), cr.TOL_VOLUME)
        press = cr.volume_in(p["pins"], p["lugs"])                              # the pins are a press fit: 0.05 on the radius
        self.assertGreater(press, 0.0)
        self.assertLess(press, 4 * math.pi * C.dowel_d * 0.06 * C.lug_t)

    def test_each_slot_lets_its_pin_move_along_the_radius_only(self) -> None:
        f = cr.Frame(D)
        plate = parts()["bezel_plate"]
        for x, v in cr.pin_places(C):
            r = math.hypot(x, v)
            ux, uv = x / r, v / r
            pin = lambda a, b: f.cyl(x + a * ux - b * uv, v + a * uv + b * ux, (f.t0 - 6.0, f.t0), C.dowel_d)
            with self.subTest(pin=(x, v)):
                for move in (-C.pin_slot_play, C.pin_slot_play):
                    self.assertLess(cr.volume_in(pin(move, 0.0), plate), cr.TOL_VOLUME)
                self.assertGreater(cr.volume_in(pin(C.pin_slot_play + 1.0, 0.0), plate), 1.0)      # the end of the slot
                self.assertGreater(cr.volume_in(pin(0.0, 0.5), plate), 1.0)                         # across the slot

    def test_the_halves_make_the_plate_and_fit_the_printer(self) -> None:
        plate = parts()["bezel_plate"]
        halves = cr.bezel_halves(D, C, plate)
        self.assertEqual(len(halves), 2)
        holes = 8 * math.pi * (C.seam_dowel_d / 2) ** 2 * C.seam_dowel_depth
        self.assertAlmostEqual(sum(h.Volume for h in halves.values()), plate.Volume - holes, delta=5.0)
        self.assertAlmostEqual(halves["bezel_half_right"].Volume, halves["bezel_half_left"].Volume, delta=5.0)
        for h in halves.values():
            self.assertTrue(h.isValid())
            self.assertEqual(len(h.Solids), 1)

    def test_the_bars_are_six_pieces_of_the_same_plate(self) -> None:
        plate = cr.bezel_plate(D, C, back=False)
        bars = cr.bezel_bars(D, plate)
        self.assertEqual(len(bars), 6)
        self.assertAlmostEqual(sum(b.Volume for b in bars.values()), plate.Volume, delta=5.0)


class PrintTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        p = parts()
        halves = cr.bezel_halves(D, C, p["bezel_plate"])
        cls.shapes = {"bezel_half_right": halves["bezel_half_right"], "upright_right": p["upright_right"], "jaw": cr.jaw(D, C, cr.PRESENT, 1, -1),
                      "shoe": cr.shoe(D, C, cr.PRESENT, 1, -1), "channel_right": p["channel_right"]}
        cls.rows = {r["part"]: r for r in cr.print_rows(D, cls.shapes)}

    def test_each_printed_part_fits_the_printer(self) -> None:
        for name, r in self.rows.items():
            with self.subTest(part=name):
                self.assertTrue(r["fits"], r["box"])
        self.assertAlmostEqual(self.rows["bezel_half_right"]["box"][2], D.bezel_w / 2 - C.plate_fit, delta=0.2)

    def test_the_upright_prints_without_an_overhang(self) -> None:
        self.assertEqual(self.rows["upright_right"]["overhang_mm2"], 0)

    def test_the_overhangs_of_the_half_are_the_pockets_and_the_break_at_the_bed(self) -> None:
        """What faces down on the half: the roofs of the two magnet pockets, of the two pin slots and of the dowel
        holes, and the first layers of the edge break beside the bed. No face of the land, of the inner frame or of
        the rim wall is among them."""
        r = self.rows["bezel_half_right"]
        self.assertLess(r["overhang_mm2"], 800.0)
        half = cr.oriented(self.shapes["bezel_half_right"], D, (-1, 0, 0), (0, 1, 0))
        for f in half.Faces:
            if f.Area > 2000.0 and not isinstance(f.Surface, Part.Plane):        # the land and the inner frame
                u0, u1, v0, v1 = f.ParameterRange
                self.assertGreater(f.normalAt((u0 + u1) / 2, (v0 + v1) / 2).z, -0.05)

    def test_a_part_that_is_too_long_does_not_fit(self) -> None:
        long = replace(C, bar_half=C.bar_half + 10.0)
        row = cr.print_rows(D, {"upright_right": cr.upright(D, long, 1)})
        self.assertEqual([r["fits"] for r in row if r["part"] == "upright_right"], [False])


class WayOutTest(unittest.TestCase):
    def test_the_way_out_is_free_of_the_parts_that_stay(self) -> None:
        p = parts()
        fixed = [p[k] for k in ("lugs", "bosses", "upright_right", "upright_left", "channel_right", "channel_left")]
        jaws = Part.makeCompound([cr.jaw(D, C, cr.PRESENT, sx, -1) for sx in (1, -1)])
        for r in cr.path_out(D, C, cr.PRESENT, fixed, jaws, (0.0, 20.0, 60.0, 150.0)):
            with self.subTest(out=r["out_mm"], what=r["what"]):
                self.assertLess(r["common_mm3"], cr.TOL_VOLUME)
        self.assertLess(cr.sweep_out(D, C, 200.0, fixed)["common_mm3"], cr.TOL_VOLUME)

    def test_the_check_finds_a_part_in_the_way(self) -> None:
        f = cr.Frame(D)
        block = f.box((-10.0, 10.0), (-10.0, 10.0), (-40.0, -30.0))               # in front of the monitor
        rows = cr.path_out(D, C, cr.PRESENT, [block], block, (0.0, 45.0))
        self.assertLess(rows[0]["common_mm3"], cr.TOL_VOLUME)
        self.assertGreater(rows[2]["common_mm3"], 1000.0)
        self.assertGreater(cr.sweep_out(D, C, 200.0, [block])["common_mm3"], 1000.0)

    def test_a_lug_that_is_too_long_is_in_the_way_of_a_tall_unit(self) -> None:
        deep = replace(C, lug_reach=C.lug_reach + 8.0)
        self.assertGreater(cr.sweep_out(D, C, 200.0, [cr.lugs(D, deep)])["common_mm3"], 100.0)


class LeadsAndButtonTest(unittest.TestCase):
    def test_each_lead_has_a_clamp_near_its_plug(self) -> None:
        rows = {r["lead"]: r for r in cr.clamp_rows(D, C, cr.PRESENT)}
        self.assertEqual(set(rows), {"mini-HDMI", "USB-C power", "3.5 mm audio"})
        self.assertEqual({k: r["side"] for k, r in rows.items()}, {"mini-HDMI": "left", "USB-C power": "left", "3.5 mm audio": "right"})
        for r in rows.values():
            self.assertLessEqual(r["distance"], C.clamp_reach)

    def test_the_channel_has_two_slots_for_each_tie(self) -> None:
        f = cr.Frame(D)
        plain = cr.channel(D, replace(C, tie_v=()), 1)
        slots = plain.Volume - parts()["channel_right"].Volume
        self.assertAlmostEqual(slots, len(C.tie_v) * 2 * C.tie_slot[0] * C.tie_slot[1] * C.channel_wall, delta=0.01)
        section = C.channel_in[0] * C.channel_in[1]
        leads = sum(math.pi * (dia / 2) ** 2 for dia in (7.0, 4.5, 4.0))         # HDMI, USB-C, audio: the largest of each
        self.assertGreater(section, 4 * leads)
        del f

    def test_the_rod_and_the_striker_stay_in_their_places_when_the_plate_is_off(self) -> None:
        """The collar of the rod rests on the back of the plate and stops the rod both ways; the lip of the guide stops
        the striker just past its travel. The full travel is free."""
        f = cr.Frame(D)
        p = parts()
        option = cr.button_option(D, C, cr.PRESENT, p["bezel_plate"])
        rod, striker, guide, plate = (option[k] for k in ("button_rod", "button_striker", "button_guide", "bezel_plate_button"))
        travel = C.striker_gap + 1.0
        self.assertLess(cr.gap(rod, plate), C.rod_fit + 1e-3)                    # the collar lies on the back of the plate
        self.assertGreater(cr.volume_in(rod.translated(f.into * -0.5), plate), 1.0)      # it cannot go out to the front
        self.assertLess(cr.volume_in(rod.translated(f.into * travel), guide), cr.TOL_VOLUME)   # the travel is free
        self.assertGreater(cr.volume_in(rod.translated(f.into * (travel + C.rod_fit + 0.5)), guide), 1.0)
        self.assertLess(cr.volume_in(striker.translated(V(-travel, 0, 0)), guide), cr.TOL_VOLUME)
        self.assertGreater(cr.volume_in(striker.translated(V(-(travel + C.rod_fit + 0.5), 0, 0)), guide), 1.0)

    def test_the_tools_of_the_shell_pass_on_the_print_parts(self) -> None:
        """tools/edge_finish.py and tools/face_check.py as they run on cad/out/cradle/print: the halves of the plate are
        printed parts with no sharp edge that shows, each named joint of the halves holds a sharp edge, the inside
        parts are in their class, and each finding of the face check is a known item of this module."""
        from tools import edge_finish as ef, face_check as fc

        p = parts()
        halves = cr.bezel_halves(D, C, p["bezel_plate"])
        prints = {**halves, "upright": p["upright_right"], "jaw": cr.jaw(D, C, cr.PRESENT, 1, -1), "shoe": cr.shoe(D, C, cr.PRESENT, 1, -1),
                  "channel": p["channel_right"]}
        rows = ef.survey(prints, D)
        self.assertEqual(ef.failures(rows), [])
        self.assertEqual({k for k, r in rows.items() if r["class"] == "inside, not painted"}, set(cr.INSIDE))
        used = {(part, g["against"]) for part, r in rows.items() if r["class"] == "printed" for g in r["sharp"] if g["against"]}
        self.assertEqual(used, {j for j in ef.JOINTS if j[0] in prints})
        found, stale = fc.check_shell(prints)
        self.assertEqual(fc.failures(found), [])
        self.assertEqual(stale, [])

    def test_the_push_rod_moves_the_striker_onto_the_button(self) -> None:
        # the option is complete and off: the monitor starts by itself, and the owner has not seen the rod's mark
        self.assertFalse(C.push_rod)
        f = cr.Frame(D)
        p = parts()
        option = cr.button_option(D, C, cr.PRESENT, p["bezel_plate"])
        for name, shape in option.items():
            with self.subTest(part=name):
                self.assertTrue(shape.isValid())
                self.assertEqual(len(shape.Solids), 1)
        rod, striker, guide, plate = (option[k] for k in ("button_rod", "button_striker", "button_guide", "bezel_plate_button"))
        for a, b in ((rod, striker), (rod, guide), (striker, guide), (rod, plate), (striker, plate), (guide, p["monitor"]), (striker, p["monitor"]), (guide, p["jaws"]),
                     *((q, p[k]) for q in (rod, striker, guide) for k in ("pins", "magnets"))):
            self.assertLess(cr.volume_in(a, b), cr.TOL_VOLUME)
        self.assertLess(cr.gap(guide, plate), 1e-6)                              # the guide lies on the back of the plate
        x, v = cr.sockets(D, C, cr.PRESENT)["power button"]
        tb = cr.glass_t(D, C) + cr.PRESENT.t / 2
        button = f.box((x, x + C.button_proud), (v - 2.0, v + 2.0), (tb - 2.0, tb + 2.0))
        self.assertAlmostEqual(cr.gap(striker, button), C.striker_gap, delta=1e-3)
        # the rod pushed in by the gap: the striker must move the same distance across, and then it is on the button
        pushed = rod.translated(f.into * C.striker_gap)
        self.assertGreater(cr.volume_in(pushed, striker), 1.0)
        moved = striker.translated(V(-C.striker_gap, 0, 0))
        self.assertLess(cr.volume_in(pushed, moved), cr.TOL_VOLUME)
        self.assertLess(cr.gap(moved, button), 1e-3)
        self.assertLess(cr.volume_in(moved, guide), cr.TOL_VOLUME)
        # the rod shows on the face of the plate
        shank = rod.common(f.box((C.rod_x - 10.0, C.rod_x + 10.0), (v - 10.0, v + 10.0), (-40.0, f.t0 - 0.01)))  # in front of the collar
        self.assertAlmostEqual(cr.gap(shank, plate), C.rod_fit, delta=1e-3)


def built() -> bool:
    return (cr.shell_dir() / "manifest.json").exists() and (cr.shell_dir() / "fit" / "report.json").exists() and split.skin_cached(D)


@functools.cache
def study() -> dict:
    return cr.study(D, C, cr.PRESENT, support.temp_dir(), log=lambda *_: None)


@unittest.skipUnless(built(), "the built shell is not there: run candybar.shell.solids, candybar.shell.fit and candybar.shell.split into cad/out/shell-rev7")
class CradleInTheBodyTest(unittest.TestCase):
    def test_the_study_passes(self) -> None:
        self.assertEqual(study()["failures"], [])
        self.assertEqual(study()["result"], "PASS")

    def test_no_part_meets_the_skin_or_the_hardware_of_the_fit_study(self) -> None:
        rows = study()["clashes"]
        self.assertGreater(len(rows), 150)
        self.assertEqual([r for r in rows if r["common_mm3"] > cr.TOL_VOLUME], [])
        others = {r["b"] for r in rows}
        for name in ("skin", "Compute_PCB_IO", "MonitorCables_Left", "MonitorCables_Right", "SpeakerR_Driver", "SpeakerL_Driver", "Marquee_Modules"):
            self.assertIn(name, others)

    def test_the_lugs_and_the_bosses_are_on_the_skin(self) -> None:
        for name, volumes in study()["attached"].items():
            with self.subTest(part=name):
                self.assertEqual(len(volumes), 4)
                self.assertGreater(min(volumes), 10.0)

    def test_the_side_is_where_the_bosses_stand(self) -> None:
        for r in study()["side_wall"]:
            self.assertAlmostEqual(r["inner_x"], C.side_wall_x, delta=C.boss_in)

    def test_the_way_out_is_free_of_the_skin(self) -> None:
        for r in study()["path"]:
            self.assertLess(r["common_mm3"], cr.TOL_VOLUME)
        self.assertLess(study()["sweep"]["common_mm3"], cr.TOL_VOLUME)
        self.assertGreater(study()["sweep"]["gap"], 0.5)

    def test_the_sight_lines_of_the_fit_study_hold(self) -> None:
        for now, before in zip(study()["sight"], study()["sight_before"]):
            with self.subTest(person=now["person"]):
                self.assertLessEqual(now["hidden_top"], before["hidden_top"] + 0.5)
                self.assertLessEqual(now["hidden_bottom"], before["hidden_bottom"] + 0.5)

    def test_the_edge_rule_holds_on_the_plate(self) -> None:
        edge = study()["edge"]
        self.assertEqual(edge["failures"], [])
        self.assertEqual([g for g in edge["rows"]["sharp"] if not g["against"]], [])
        self.assertEqual(edge["rows"]["break_faces"], 12)

    def test_each_finding_of_the_face_check_has_a_reason(self) -> None:
        for name, r in study()["faces"].items():
            with self.subTest(part=name):
                self.assertEqual(r["not_allowed"], [])
        self.assertEqual(study()["faces"]["upright_right"]["findings"], 0)
        self.assertEqual(study()["faces"]["lugs"]["findings"], 0)

    def test_the_monitor_is_where_the_fit_study_has_it(self) -> None:
        """The present unit of this module is the body of the fit study, glass_gap farther back."""
        doc, found = cr.fit_items(D)
        try:
            body = next(s.world for it in found if it.name == "Monitor" for s in it.solids if s.name == "Monitor_Body")
            mine = cr.monitor(D, C, cr.PRESENT)
            f = cr.Frame(D)
            self.assertAlmostEqual(mine.Volume, body.Volume, delta=1.0)
            self.assertAlmostEqual((mine.CenterOfMass - body.CenterOfMass).dot(f.into), C.glass_gap, delta=1e-3)
            self.assertLess(abs((mine.CenterOfMass - body.CenterOfMass).dot(f.up)), 1e-3)
        finally:
            App.closeDocument(doc.Name)
