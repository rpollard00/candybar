"""The styled shell: one solid of the right size, and live on the saved document like the rest."""
from __future__ import annotations

import math
import unittest

import FreeCAD as App
import Part

from candybar import check, massing, model, params

from . import support

HOOD_PLATES = tuple(name for name, *_ in massing.HOOD_PLATES)


def front_face(plate: Part.Shape) -> Part.Face:
    """The broad face of a hood plate that looks out of the cabinet."""
    return max((face for face in plate.Faces if face.normalAt(0, 0).y < 0), key=lambda face: face.Area)


def lies_in_a_face_of(solid: Part.Shape, flat: Part.Face) -> bool:
    """True when some flat face of `solid` is in the same plane as `flat` and looks the same way."""
    point, normal = flat.CenterOfMass, flat.normalAt(0, 0)
    for face in solid.Faces:
        if isinstance(face.Surface, Part.Plane):
            same_way = face.normalAt(0, 0).dot(normal) > 1 - 1e-9
            if same_way and abs((face.CenterOfMass - point).dot(normal)) < 1e-6:
                return True
    return False


class ShellTest(unittest.TestCase):
    def setUp(self) -> None:
        self.doc: App.Document = self.enterContext(support.saved_document())

    def value(self, name: str) -> float:
        return params.value(self.doc, name)

    def edit(self, **values: float) -> None:
        support.edit(self.doc, **values)
        self.assertEqual(model.errors(self.doc), [])

    def shape(self, name: str) -> Part.Shape:
        return support.solids(self.doc)[name].world

    def test_skin_is_one_solid_as_big_as_the_cabinet(self) -> None:
        skin = self.shape(massing.SKIN)
        self.assertEqual(len(skin.Solids), 1)
        self.assertTrue(skin.isValid())
        size = (skin.BoundBox.XLength, skin.BoundBox.YLength, skin.BoundBox.ZLength)
        expected = (self.value("deck_w"), self.value("cab_d"), self.value("cab_h") - self.value("foot_h"))
        for measured, wanted in zip(size, expected, strict=True):
            self.assertAlmostEqual(measured, wanted, places=4)

    def test_skin_is_hollow_and_open_where_the_panel_and_the_bezel_go(self) -> None:
        skin = self.shape(massing.SKIN)
        box = skin.BoundBox
        self.assertLess(skin.Volume, 0.2 * box.XLength * box.YLength * box.ZLength)
        for name in ("Deck_Lever", "Deck_Buttons", "Bezel_16x9", "Monitor_Body", *HOOD_PLATES):
            self.assertLess(skin.common(self.shape(name)).Volume, 1e-3, name)

    def test_recline_moves_the_bezel_plates_with_the_monitor_and_the_shell(self) -> None:
        top_before = self.shape(massing.SKIN).BoundBox.ZMax
        self.edit(recline=self.value("recline") + 5)
        monitor, skin = self.shape("Monitor_Body"), self.shape(massing.SKIN)
        for name, *_ in massing.BEZEL_PLATES:
            plate = self.shape(name)
            self.assertAlmostEqual(plate.distToShape(monitor)[0], 0, places=6, msg=name)
            self.assertLess(plate.common(monitor).Volume, 1e-3, name)
            self.assertLess(plate.common(skin).Volume, 1e-3, name)
        self.assertAlmostEqual(skin.BoundBox.ZMax, self.value("cab_h"), places=4)
        self.assertLess(skin.BoundBox.ZMax, top_before - 5)

    def test_hood_height_raises_the_cabinet_and_the_skin_top(self) -> None:
        height_before, top_before = self.value("cab_h"), self.shape(massing.SKIN).BoundBox.ZMax
        self.edit(hood_h=self.value("hood_h") + 25)
        self.assertAlmostEqual(self.value("cab_h"), height_before + 25, places=4)
        self.assertAlmostEqual(self.shape(massing.SKIN).BoundBox.ZMax, top_before + 25, places=4)

    def test_deck_flare_widens_the_deck_and_not_the_hood(self) -> None:
        deck_z, hood_z = self.value("cp_top_z") - 20, self.value("cab_h") - 80
        deck_before, hood_before = (support.width_at(self.shape(massing.SKIN), z) for z in (deck_z, hood_z))
        self.assertAlmostEqual(deck_before, self.value("deck_w"), places=4)
        self.assertAlmostEqual(hood_before, self.value("outer_w"), places=4)
        self.edit(deck_flare=self.value("deck_flare") + 10)
        deck_after, hood_after = (support.width_at(self.shape(massing.SKIN), z) for z in (deck_z, hood_z))
        self.assertAlmostEqual(deck_after, deck_before + 20, places=4)
        self.assertAlmostEqual(hood_after, hood_before, places=4)

    def test_monitor_width_widens_the_body(self) -> None:
        hood_z = self.value("cab_h") - 80
        before = support.width_at(self.shape(massing.SKIN), hood_z)
        self.edit(mon_w=self.value("mon_w") + 6)
        self.assertAlmostEqual(support.width_at(self.shape(massing.SKIN), hood_z), before + 6, places=4)
        self.assertAlmostEqual(self.value("outer_w"), before + 6, places=4)

    def test_sweep_radius_reshapes_the_cheek_foot(self) -> None:
        before = self.shape(massing.SKIN).Volume
        self.edit(sweep_r=self.value("sweep_r") - 6)
        self.assertGreater(abs(self.shape(massing.SKIN).Volume - before), 1000)

    def test_hood_trim_plates_sit_flush_in_the_hood_face(self) -> None:
        skin = self.shape(massing.SKIN)
        for name in HOOD_PLATES:
            self.assertTrue(lies_in_a_face_of(skin, front_face(self.shape(name))), name)

    def test_upright_hood_face_keeps_its_trim_plates_flush(self) -> None:
        _, baseline = support.baseline()
        self.edit(hood_tilt=0)
        skin = self.shape(massing.SKIN)
        for name in HOOD_PLATES:
            plate = self.shape(name)
            self.assertAlmostEqual(abs(front_face(plate).normalAt(0, 0).y), 1, places=9, msg=name)
            self.assertTrue(lies_in_a_face_of(skin, front_face(plate)), name)
            self.assertLess(plate.common(skin).Volume, 1e-3, name)
        self.assertEqual(support.fail_rows(check.run(self.doc)) - support.fail_rows(baseline), set())

    def test_bezel_windows_have_their_aspect_ratios(self) -> None:
        wanted = {"Bezel_16x9": 16 / 9, "Bezel_16x10": 16 / 10, "Bezel_4x3": 4 / 3, "Bezel_Tate": 3 / 4}
        plate_area = self.value("bezel_w") * self.value("bezel_len")
        for name, ratio in wanted.items():
            front = max(self.doc.getObject(name).Shape.Faces, key=lambda face: face.Area)
            (window,) = [wire for wire in front.Wires if not wire.isSame(front.OuterWire)]
            box = window.BoundBox
            self.assertAlmostEqual(box.XLength / box.ZLength, ratio, places=2, msg=name)
            self.assertAlmostEqual(front.Area, plate_area - box.XLength * box.ZLength, places=3, msg=name)
            self.assertTrue(math.isclose(box.Center.z, self.value("win_cz"), abs_tol=1e-6), name)
