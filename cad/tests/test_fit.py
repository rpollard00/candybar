"""The checks of the fit study: they notice an item that leaves the cavity, and the speaker search finds the circle."""
from __future__ import annotations

import math
import unittest

import FreeCAD as App
import Part

from candybar import check, model, panel, params
from candybar.shell import cavity, fit
from candybar.shell import solids as so
from candybar.shell import profiles as pr
from candybar.shell.dims import Blueprint

from . import support

# a stand-in for the room behind the speaker face and the marquee, which the study measures on the cavity
ROOM = {"fit_spk_x": 140.0, "fit_spk_y": 470.0, "fit_spk_z": 475.0, "fit_spk_d": 50.0, "fit_spk_depth": 50.0,
        "fit_mq_w": 352.0, "fit_mq_h": 34.0, "fit_mq_y": 470.0, "fit_mq_z0": 517.0}


class FitChecksTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        d, lay = Blueprint(), fit.Layout()
        base = fit.sheet(params.load(support.PARAMS), "FitTestBase")
        v = lambda name: params.value(base, name)
        values = fit.anchors(d, lay, v, d.width / 2 - d.wall_t) | ROOM
        cls.doc = fit.build_items(fit.sheet_rows(support.PARAMS, values))
        cls.found = fit.items(cls.doc)
        cls.everything = Part.makeBox(2000, 2000, 2000, App.Vector(-1000, -1000, -1000))
        cls.plate = Part.makeBox(1, 1, 1)

    @classmethod
    def tearDownClass(cls) -> None:
        for name in ("FitTestBase", cls.doc.Name):
            App.closeDocument(name)

    def containment(self, walls: list[Part.Shape]) -> list[tuple[str, str, str]]:
        cav = cavity.Cavity([self.everything], walls, [])
        return fit.run_checks(self.doc, self.found, cav, self.plate, self.plate)["containment in the cavity"]

    def test_every_item_is_in_a_cavity_that_holds_everything(self) -> None:
        self.assertEqual([lv for lv, _, _ in self.containment([])], [check.PASS])

    def test_containment_notices_the_power_supply_in_the_skin(self) -> None:
        psu = next(it for it in self.found if it.name == "PSU").shape(fit.ENVELOPE).BoundBox
        wall = Part.makeBox(psu.XLength, psu.YLength, psu.ZLength / 2, App.Vector(psu.XMin, psu.YMin, psu.ZMin))
        failed = {subject for lv, subject, _ in self.containment([wall]) if lv == check.FAIL}
        self.assertIn("PSU_Body", failed)
        self.assertFalse({name for name in failed if not name.startswith("PSU")})

    def test_every_control_stays_inside_the_panel_outline(self) -> None:
        """Below the plate a control must pass through the opening (the outline less the ledge); above it, a cap or
        the ball must stand on the plate."""
        d = Blueprint()
        prism = lambda grow: so.prism(so.poly(pr.panel_outline(d, grow)), so.xy(-100.0), App.Vector(0, 0, 400))
        under, over = prism(-cavity.Openings().panel_ledge), prism(0.0)
        panel = [s for it in self.found if it.group == "Panel" for s in it.solids]
        self.assertGreater(len(panel), 40)
        for s in panel:
            with self.subTest(solid=s.name):
                bb = s.world.BoundBox
                room = over if bb.ZMin >= d.panel_top - 1e-6 else under
                self.assertLess(s.world.cut(room).Volume, 1e-3)

    def test_no_air_zone_shares_room_with_another_item(self) -> None:
        self.assertEqual([lv for lv, _, _ in fit.air_zones(self.found)], [check.PASS])

    def test_air_zones_notice_the_duct_in_the_power_supply_fan_space(self) -> None:
        """The BC-250 5 lower: its exhaust duct enters the 25 mm space over the power supply's fan."""
        d, lay = Blueprint(), fit.Layout()
        base = fit.sheet(params.load(support.PARAMS), "FitTestLow")
        v = lambda name: params.value(base, name)
        values = fit.anchors(d, lay, v, d.width / 2 - d.wall_t) | ROOM
        values["bc_top_z"] -= 5.0
        doc = fit.build_items(fit.sheet_rows(support.PARAMS, values))
        try:
            failed = {subject for lv, subject, _ in fit.air_zones(fit.items(doc)) if lv == check.FAIL}
        finally:
            App.closeDocument("FitTestLow")
            App.closeDocument(doc.Name)
        self.assertIn("Compute_ExhaustDuct / PSU_FanAir", failed)

    def test_every_item_is_built(self) -> None:
        names = {it.name for it in self.found}
        for name in ("Monitor", "Compute", "PSU", "CableBundle", "Lever", "Encoder", "Hub", "SpeakerR", "SpeakerL", "Marquee"):
            self.assertIn(name, names)
        self.assertEqual(len([n for n in names if n.startswith("USB_")]), len(fit.USB_ORDER))


def placed_with(name: str, **changes: float) -> App.Document:
    """The document of the items at the anchors of the default layout, with some values of the sheet changed."""
    d, lay = Blueprint(), fit.Layout()
    base = fit.sheet(params.load(support.PARAMS), f"{name}Base")
    try:
        v = lambda key: params.value(base, key)
        values = fit.anchors(d, lay, v, d.width / 2 - d.wall_t) | ROOM
        for key, change in changes.items():
            values[key] = change(values[key] if key in values else v(key)) if callable(change) else change
    finally:
        App.closeDocument(base.Name)
    return fit.build_items(fit.sheet_rows(support.PARAMS, values))


class ItemRulesTest(unittest.TestCase):
    """Rules R1, R2 and R5 and the state rule on the items of the fit study. The older generator had these tests on
    its own document."""

    def failed(self, **changes: float) -> set[tuple[str, str]]:
        doc = placed_with("FitRules", **changes)
        try:
            scene = check.Scene(doc, tuple(model.placed(doc)), ())
            rules = {"R1": check._interference(scene), "R2": check._keepout(scene), "R5": check._button_spacing(scene)}
        finally:
            App.closeDocument(doc.Name)
        return {(rule, subject) for rule, rows in rules.items() for level, subject, _ in rows if level == check.FAIL}

    def test_the_default_layout_has_no_fail(self) -> None:
        self.assertEqual(self.failed(), set())

    def test_encoder_under_a_button_fails_interference_between_two_purchased_parts(self) -> None:
        doc = placed_with("FitRulesAt")
        try:
            at = next(s.world.BoundBox.Center for s in model.placed(doc) if s.name == "Btn2_Body")
            origin = doc.getObject("ControlPanel").Placement.Base
        finally:
            App.closeDocument(doc.Name)
        under_button_2 = {"enc_x": at.x - origin.x, "enc_y": at.y - origin.y}
        self.assertIn(("R1", "Btn2_Body / Encoder_Board"), self.failed(**under_button_2))

    def test_cable_bundle_in_the_plug_zone_fails_the_keepout_rule(self) -> None:
        doc = placed_with("FitRulesAt")
        try:
            plugs = next(s.world.BoundBox for s in model.placed(doc) if s.name == "PSU_Plugs")
        finally:
            App.closeDocument(doc.Name)
        self.assertIn(("R2", "PSU_Plugs / CableBundle_Body"), self.failed(bundle_x0=plugs.XMin, bundle_y0=plugs.YMin))

    def test_wider_nut_fails_button_spacing(self) -> None:
        self.assertIn("R5", {rule for rule, _ in self.failed(btn_nut_d=38.0)})

    def test_item_with_no_height_stops_the_study(self) -> None:
        try:
            with self.assertRaisesRegex(ValueError, "Encoder_Board"):
                placed_with("FitRulesFlat", enc_h=0.0)
        finally:
            App.closeDocument("Fit")


class EnvelopeTest(unittest.TestCase):
    """The envelopes of the purchased parts follow the parameter sheets. The older generator had these tests on its
    own document."""

    def boxes(self, **changes: float) -> tuple[dict[str, App.BoundBox], dict[str, float]]:
        doc = placed_with("FitEnvelope", **changes)
        try:
            names = ("bc_top_z", "bc_pcb_w_pwr", "bc_pcb_w_io", "bc_fin_y0", "mon_h", "mon_t", "recline", "psu_d", "psu_d_max",
                     "psu_y0", "stick_x", "btn1_dx")
            return {s.name: s.world.BoundBox for s in model.placed(doc)}, {n: params.value(doc, n) for n in names}
        finally:
            App.closeDocument(doc.Name)

    def test_board_stands_on_its_straight_edge_with_the_power_connector_on_top(self) -> None:
        box, v = self.boxes()
        bottom, top = v["bc_top_z"] - v["bc_pcb_w_pwr"], v["bc_top_z"]
        self.assertAlmostEqual(box["Compute_PCB_IO"].ZMin, bottom, places=6)
        self.assertAlmostEqual(box["Compute_PCB_IO"].ZMax, bottom + v["bc_pcb_w_io"], places=6)
        self.assertAlmostEqual(box["Compute_Heatsink"].ZMin, bottom + v["bc_fin_y0"], places=6)
        self.assertAlmostEqual(box["Compute_PowerPlug"].ZMin, top, places=6)

    def test_monitor_leans_back_by_the_recline(self) -> None:
        box, v = self.boxes()
        tilt = math.radians(v["recline"])
        self.assertAlmostEqual(v["recline"], Blueprint().recline)
        self.assertAlmostEqual(box["Monitor_Body"].YLength, v["mon_h"] * math.sin(tilt) + v["mon_t"] * math.cos(tilt), places=4)
        self.assertAlmostEqual(box["Monitor_Body"].ZLength, v["mon_h"] * math.cos(tilt) + v["mon_t"] * math.sin(tilt), places=4)

    def test_psu_depth_is_measured_forward_from_the_rear_of_its_bay(self) -> None:
        box, v = self.boxes(psu_d=lambda depth: depth - 15.0)
        self.assertAlmostEqual(box["PSU_Body"].YLength, v["psu_d"], places=4)
        self.assertAlmostEqual(box["PSU_Body"].YMax, v["psu_y0"] + v["psu_d_max"], places=4)
        self.assertAlmostEqual(box["PSU_Body"].YMax, box["PSU_Bay"].YMax, places=4)

    def test_psu_as_deep_as_its_bay_fills_it(self) -> None:
        _, v = self.boxes()
        box, _ = self.boxes(psu_d=v["psu_d_max"])
        self.assertAlmostEqual(box["PSU_Body"].YLength, v["psu_d_max"], places=4)
        self.assertAlmostEqual(box["PSU_Body"].YMin, box["PSU_Bay"].YMin, places=4)

    def test_button_follows_its_offset_from_the_lever(self) -> None:
        before, _ = self.boxes()
        after, _ = self.boxes(btn1_dx=lambda dx: dx + 2.0)
        self.assertAlmostEqual(after["Btn1_Body"].Center.x, before["Btn1_Body"].Center.x + 2.0, places=4)
        self.assertAlmostEqual(after["Btn1_Body"].Center.y, before["Btn1_Body"].Center.y, places=4)
        self.assertAlmostEqual(after["Btn2_Body"].Center.x, before["Btn2_Body"].Center.x, places=4)

    def test_six_buttons_build_six_action_buttons(self) -> None:
        for count in panel.BUTTON_COUNTS:
            bodies = [p.name for p in fit.control_panel(count).prims if p.name.startswith("Btn") and p.name.endswith("_Body")]
            self.assertEqual(len(bodies), count)

    def test_button_count_that_has_no_layout_is_rejected(self) -> None:
        try:
            with self.assertRaisesRegex(params.ParamError, "btn_count must be one of"):
                fit.build_items(params.load(support.params_copy({"btn_count": "7"})))
        finally:
            App.closeDocument("Fit")


class WarningsTest(unittest.TestCase):
    """The file of warnings has what the older report gave and the study's report does not: rules R6 and R7."""

    @classmethod
    def setUpClass(cls) -> None:
        doc = placed_with("FitWarnings")
        try:
            cls.text = fit.warnings(doc)
        finally:
            App.closeDocument(doc.Name)

    def row(self, start: str) -> str:
        return next(line for line in self.text.splitlines() if line.startswith(f"| {start}"))

    def test_panel_top_and_palm_rest_have_their_targets(self) -> None:
        self.assertIn(f"{Blueprint().panel_top:.1f} mm; target", self.row("panel top above the desk"))
        self.assertRegex(self.row("palm rest"), r"\| (PASS|WARN) \| \d+\.\d mm; target \d+ to \d+ mm")

    def test_a_row_to_measure_is_listed_with_its_file_and_instruction(self) -> None:
        row = next(r for r in params.load(support.PARAMS) if r.measure and r.file == "hardware.csv")
        line = self.row(row.name)
        self.assertIn("hardware.csv", line)
        self.assertIn(row.measure.replace("|", "\\|"), line)

    def test_a_value_that_the_study_sets_is_not_listed_to_measure(self) -> None:
        listed = self.text.split("## Still to measure")[1]
        self.assertNotIn("| recline |", listed)
        self.assertNotIn("shell/fit.py", listed)


class FitOnTheRealCavityTest(unittest.TestCase):
    """The fit study on the default build and its real cavity: the hardware at its anchors, every rule of the study.
    A hardware item in the skin of the real form fails here (in unit 1 of revision 7 the exhaust duct lay in the skin
    behind the cut-ins, and no test saw it)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.d, cls.parts, _ = support.shell()
        cls.cav = support.cavity()
        cls.fitted = fit.place(cls.d, fit.Layout(), support.PARAMS, cls.parts, cls.cav)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fitted.close()

    def box(self, name: str) -> App.BoundBox:
        return next(s.world.BoundBox for it in self.fitted.found for s in it.solids if s.name == name)

    def test_no_rule_of_the_study_fails(self) -> None:
        self.assertEqual(self.fitted.failures, [])

    def test_every_rule_ran(self) -> None:
        for title in ("R1 interference", "R2 keep-out", "containment in the cavity", "R2b air zones", "door service"):
            self.assertTrue(self.fitted.rules[title], title)

    def test_the_door_is_inside_the_cut_ins_and_below_the_rear_shelf(self) -> None:
        d, door = self.d, self.fitted.door
        self.assertAlmostEqual(d.cut_in_x - door["x1"], d.door_land)
        self.assertAlmostEqual(d.rear_shelf_z0 - door["z1"], d.door_frame)

    def test_the_exhaust_duct_is_inside_the_door_and_clear_of_the_cut_ins(self) -> None:
        duct, door = self.box("Compute_ExhaustDuct"), self.fitted.door
        self.assertGreaterEqual(duct.XMin, door["x0"])
        self.assertGreaterEqual(self.d.cut_in_x - abs(duct.XMin), fit.Layout().cut_in_reach(self.d) - 1e-6)

    def test_the_power_supply_is_below_the_cut_ins(self) -> None:
        self.assertLessEqual(self.box("PSU_Body").ZMax, self.d.cut_in_z0 - fit.Layout().cut_in_reach(self.d))

    def test_the_study_notices_the_duct_behind_the_cut_ins(self) -> None:
        """The duct moved out to where it stood in unit 1 (its end 8 inside the corner, with each rule of the layout
        that holds it back set aside): it lies in the skin behind the cut-ins, and it is outside the door."""
        d = self.d
        end = d.rear_w / 2 - 8.0
        far = fit.Layout(duct_in_door=d.door_w / 2 - end, cut_in_clear=d.cut_in_x - end - d.wall_t - cavity.SLAB)
        moved = fit.place(d, far, support.PARAMS, self.parts, self.cav)
        try:
            at = next(s.world.BoundBox.XMin for it in moved.found for s in it.solids if s.name == "Compute_ExhaustDuct")
            failed = "\n".join(moved.failures)
        finally:
            moved.close()
        self.assertAlmostEqual(at, -end)
        self.assertIn("containment in the cavity: Compute_ExhaustDuct", failed)
        self.assertIn("door service: Compute_ExhaustDuct", failed)


class SpeakerSearchTest(unittest.TestCase):
    def test_largest_circle_in_a_square_touches_all_four_sides(self) -> None:
        x, z, r = fit.largest_circle([(0.0, 0.0), (40.0, 0.0), (40.0, 40.0), (0.0, 40.0)])
        self.assertAlmostEqual(r, 20.0, places=1)
        self.assertAlmostEqual(x, 20.0, places=0)
        self.assertAlmostEqual(z, 20.0, places=0)

    def test_the_speaker_form_holds_the_circle(self) -> None:
        d = Blueprint()
        quad, _ = fit.speaker_face(d, pr.hood(d))
        x, z, r = fit.largest_circle(quad)
        height = quad[2][1] - quad[1][1]
        self.assertLessEqual(2 * r, height + 1e-6)
        self.assertGreater(r, 0.0)
