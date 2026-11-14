"""The mounts of the hardware: the design passes its checks, and each check notices the fault it is there for."""
from __future__ import annotations

import re
import unittest
from dataclasses import replace

import FreeCAD as App
import Part

from candybar import check, params
from candybar.shell import fit, mounts, split
from candybar.shell.dims import Blueprint

from . import support

SHELL_OUT = support.CAD / "out" / "shell-rev7"
# stand-ins for the values that the fit study measures on the whole cavity, when its report is not there
ROOM = {"fit_spk_x": 136.4, "fit_spk_y": 463.1, "fit_spk_z": 475.3, "fit_spk_d": 53.9, "fit_spk_depth": 109.0,
        "fit_mq_w": 352.0, "fit_mq_h": 34.0, "fit_mq_y": 463.1, "fit_mq_z0": 517.3, "fit_usb_x": 242.9}


def shell_parts(d: Blueprint) -> dict[str, Part.Shape]:
    """The default build, made here; its files in cad/out/shell-rev7 when the build does not end on this machine."""
    try:
        return support.shell()[1]
    except Part.OCCError:
        if not (SHELL_OUT / "manifest.json").exists():
            raise
        return mounts.shell_parts(d, SHELL_OUT, log=lambda *_: None)


class MountsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d, cls.lay, cls.m = Blueprint(), fit.Layout(), mounts.Mounts()
        parts = shell_parts(cls.d)
        if not split.skin_cached(cls.d):
            split.build_modules(cls.d, log=lambda *_: None, parts=parts)
        room = mounts.room_values(SHELL_OUT) if (SHELL_OUT / fit.FIT / "report.json").exists() else ROOM
        cls.result = mounts.run(cls.d, cls.lay, cls.m, support.PARAMS, SHELL_OUT, log=lambda *_: None, parts=parts, room=room)
        cls.rep, cls.design = cls.result.report, cls.result.design
        cls.base = fit.sheet(params.load(support.PARAMS), "MountsTestBase")
        cls.v = staticmethod(lambda name: params.value(cls.base, name))

    @classmethod
    def tearDownClass(cls) -> None:
        App.closeDocument(cls.base.Name)

    def test_no_check_fails(self) -> None:
        self.assertEqual(self.rep["failures"], [])

    def test_each_solid_is_one_valid_solid(self) -> None:
        self.assertEqual(len(self.design.solids), 38)
        for s in self.design.solids:
            for shape in (s.shape, s.whole):
                self.assertTrue(shape.isValid(), s.name)
                self.assertEqual(len(shape.Solids), 1, s.name)
                self.assertGreater(shape.Volume, 0.0, s.name)

    def test_the_fit_rules_fail_only_where_the_trays_cross_the_air_zone(self) -> None:
        self.assertEqual(self.rep["fit_before"], [])
        self.assertEqual(self.rep["fit_other"], [])
        self.assertEqual(len(self.rep["fit_declared"]), 4)
        for title in ("R1 interference", "R2 keep-out", "containment in the cavity", "R2b air zones", "door service"):
            self.assertTrue(self.rep["fit_rules"][title], title)
        post = 3.14159 * ((self.m.post_d / 2) ** 2 - (self.m.m3_clear / 2) ** 2) * self.v("bc_underside_gap")
        for text in self.rep["fit_declared"]:
            self.assertIn("Compute_UndersideAir", text)
            self.assertAlmostEqual(float(re.search(r"(\d+) mm3", text).group(1)), 2 * post, delta=3.0)

    def test_no_solid_is_in_the_skin_and_each_root_is(self) -> None:
        self.assertEqual([r["solid"] for r in self.rep["skin"] if not r["ok"]], [])
        self.assertEqual(self.rep["own_pairs"], [])
        moved = replace(self.design, solids=[replace(s, shape=s.shape.translated(App.Vector(3.0, 0, 0))) if s.name == "BossR" else s for s in self.design.solids])
        self.assertEqual([r["solid"] for r in mounts.in_skin(moved, self.result.skin) if not r["ok"]], ["BossR"])
        pushed = replace(self.design, solids=[replace(s, shape=s.shape.translated(App.Vector(0, -2.0, 0))) if s.name == "DockR" else s for s in self.design.solids])
        self.assertEqual([(a, b) for a, b, _ in mounts.own_pairs(pushed)], [("DockR", "BossR")])

    def test_a_driver_reaches_each_screw_through_the_door(self) -> None:
        rows = self.rep["access"]
        self.assertEqual([r["screw"] for r in rows if not r["ok"]], [])
        self.assertEqual(sorted(r["state"] for r in rows if r["state"] != "bench"), ["all in place"] * 2 + ["module out"] * 4)
        self.assertGreaterEqual(min(r["door_margin"] for r in rows if "door_margin" in r), 2.0)
        jamb = self.design.site.door["x1"] + 2.0
        hidden = [replace(sc, head=(jamb, sc.head[1], sc.head[2])) if sc.state == "module out" and sc.head[0] > 0 else sc for sc in self.design.screws]
        bad = mounts.access(replace(self.design, screws=hidden), self.m, self.result.hw, self.d)
        self.assertEqual(len([r for r in bad if not r["ok"]]), 2)
        # with the module in place the exhaust duct hides a screw at the left end of the board
        f = mounts.tray_frame(self.design.site, self.m, -1.0)
        under = mounts.Screw("a screw under the duct", "M3", (f["xc"], self.design.site.y_pcb, f["zd0"] + 15.0), "TrayL", "DockL", "all in place")
        row = mounts.access(replace(self.design, screws=[under]), self.m, self.result.hw, self.d)[0]
        self.assertIn("Compute_ExhaustDuct", row["in_the_way"])

    def test_the_module_and_the_supply_come_out_through_the_door(self) -> None:
        for key in ("module_path", "psu_path"):
            self.assertTrue(self.rep[key]["ok"], key)
            self.assertGreaterEqual(min(self.rep[key]["margins"].values()), 2.0, key)
        s = self.design.site
        bar = mounts.Solid("Bar", "compute", "printed", mounts.bx(-50.0, 50.0, s.y_pcb + 5.0, s.y_pcb + 15.0, s.bz0, s.bz0 + 10.0), "nothing")
        blocked = mounts.module_path(replace(self.design, solids=self.design.solids + [bar]), self.m, self.result.hw, self.d)
        self.assertFalse(blocked["ok"])
        self.assertEqual(blocked["in_the_way"], ["Bar"])

    def test_no_boss_is_near_a_seam(self) -> None:
        rows = self.rep["seams"]
        self.assertEqual(len(rows), 26)
        self.assertGreaterEqual(min(r["distance"] for r in rows), mounts.SEAM_CLEAR)
        x_bay = split.lines(self.d).x_bay
        on_seam = mounts.build(self.d, self.lay, replace(self.m, power_tie=(x_bay, 397.0)), self.v, self.result.skin)
        self.assertEqual([r["boss"] for r in mounts.seams(on_seam, self.d) if not r["ok"]], ["TiePower"])

    def test_each_printed_part_fits_the_printer(self) -> None:
        rows = self.rep["print"]
        self.assertEqual(sorted(r["part"] for r in rows), ["DockL", "DockR", "HubSaddle", "TrayL", "TrayR"])
        self.assertTrue(all(r["fits"] for r in rows))

    def test_the_loads_are_below_the_limits(self) -> None:
        self.assertEqual([r["what"] for r in self.rep["loads"] if not r["ok"]], [])
        self.assertEqual({r["mount"] for r in self.rep["loads"]}, {"compute module", "power supply", "hub", "ties"})
        thin = mounts.loads(self.design, replace(self.m, arm_t=1.5), self.v)
        self.assertEqual([r["what"].split(" (")[0] for r in thin if not r["ok"]], ["the longest arm of a tray"])

    def test_the_interfaces(self) -> None:
        s, door = self.design.site, self.design.site.door
        self.assertEqual(len(self.design.shroud_points), 4)
        for x, y, z in self.design.shroud_points:
            self.assertAlmostEqual(y, s.y_pcb)
            self.assertTrue(door["x0"] < x < door["x1"] and door["z0"] < z < door["z1"])
            self.assertTrue(s.fin[0] < z < s.fin[1])
        self.assertEqual(len(self.design.psu_holes), 4)
        for x, y, z in self.design.psu_holes:
            self.assertAlmostEqual(y, s.psu[3])
            self.assertTrue(s.psu[0] + 5.0 < x < s.psu[1] - 5.0 and s.psu[4] + 5.0 < z < s.psu[5] - 5.0)

    def test_each_small_item_has_a_place_that_is_clear_and_a_tie_point(self) -> None:
        places = {r["name"]: r for r in self.rep["places"]}
        self.assertEqual(sorted(places), ["PlaceAmplifier", "PlaceButtonAdapter", "PlaceCharger", "PlaceChargerBarrel", "PlaceChargerUsbC", "PlaceDpAdapter", "PlaceSoundAdapter"])
        s, ties = self.design.site, {r["name"]: r for r in self.rep["ties"]}
        for name in ("TieButton", "TieDeck", "TieAmpFront", "TieAmpRear", "TieChargerFront", "TieChargerRear", "TieBarrel", "tie slots of the dock L, at the place"):
            self.assertIn(name, ties)
        dp, ch, amp = places["PlaceDpAdapter"]["box"], places["PlaceCharger"]["box"], places["PlaceAmplifier"]["box"]
        # the adapter is in front of the plane of the board and outside its end: clear of the shroud and of the air zones
        self.assertLess(dp[3], s.y_pcb)
        self.assertLess(dp[1], s.bx0)
        # the charging hub has the size that the owner gave, air under it, and its USB end below the door opening
        self.assertEqual([round(ch[1] - ch[0], 1), round(ch[3] - ch[2], 1), round(ch[5] - ch[4], 1)], [74.7, 51.3, 22.6])
        self.assertGreaterEqual(ch[4] - s.floor, 5.0)
        usb, barrel = places["PlaceChargerBarrel"]["box"], places["PlaceChargerBarrel"]["box"]
        left = places["PlaceChargerUsbC"]["box"]
        # with its plugs it has 156.7 x 60 x 30: all the length between the stowed cables and the side wall
        self.assertAlmostEqual(barrel[1] - left[0], 156.7)
        self.assertEqual([round(barrel[3] - barrel[2]), round(barrel[5] - barrel[4])], [60, 30])
        self.assertLess(s.wall_x - barrel[1], 1.0)
        self.assertLess(left[0] - s.bundle[1], 2.0)
        # the barrel plug with its fuse is at the right, below the part of the door opening that the module leaves free
        self.assertTrue(s.bx1 + self.m.upright_gap + self.m.upright_w < ties["TieBarrel"]["at"][0] < s.door["x1"])
        self.assertEqual([round(x) for x in (places["PlaceAmplifier"]["box"][1] - amp[0], amp[3] - amp[2])], [54, 41])
        self.assertTrue(s.bx1 < usb[0] and usb[0] < s.door["x1"])
        self.assertLess(usb[2] - s.hub[3], 60.0)
        # the amplifier is far from the fan of the power supply
        self.assertGreater(amp[0] - s.psu[1], 150.0)
        # a place that moves into the exhaust duct fails the rules: the rules see the places
        self.assertTrue(any(k.startswith("containment") or k.startswith("R1") for k in self.rep["fit_rules"]))
        moved = replace(self.design, solids=[replace(q, shape=q.shape.translated(App.Vector(0, 15.0, 0))) if q.name == "PlaceDpAdapter" else q for q in self.design.solids])
        self.assertIn(("TrayL", "PlaceDpAdapter"), [(a, b) for a, b, _ in mounts.own_pairs(replace(moved, solids=[
            replace(q, shape=q.shape.translated(App.Vector(-15.0, 0, 0))) if q.name == "TrayL" else q for q in moved.solids]))])

    def test_the_faces_are_clean(self) -> None:
        self.assertEqual(self.rep["faces"], [])


class FindingsTest(unittest.TestCase):
    def test_a_failure_that_is_not_declared_is_another_failure(self) -> None:
        rules = {"R2 keep-out": [(check.FAIL, "Compute_UndersideAir / Mount_TrayL", "common volume 1091 mm3"), (check.FAIL, "PSU_FanAir / Mount_TrayL", "common volume 5 mm3")],
                 "R1 interference": [(check.PASS, "10 pairs", "")]}
        declared, other = mounts.split_findings(rules)
        self.assertEqual(len(declared), 1)
        self.assertEqual(other, ["R2 keep-out: PSU_FanAir / Mount_TrayL: common volume 5 mm3"])
