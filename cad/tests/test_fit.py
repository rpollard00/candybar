"""The checks of the fit study: they notice an item that leaves the cavity, and the speaker search finds the circle."""
from __future__ import annotations

import unittest

import FreeCAD as App
import Part

from candybar import check, params
from candybar.shell import cavity, fit
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

    def test_every_item_is_built(self) -> None:
        names = {it.name for it in self.found}
        for name in ("Monitor", "Compute", "PSU", "CableBundle", "Lever", "Encoder", "Hub", "SpeakerR", "SpeakerL", "Marquee"):
            self.assertIn(name, names)
        self.assertEqual(len([n for n in names if n.startswith("USB_")]), len(fit.USB_ORDER))


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
