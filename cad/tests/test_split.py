"""The split of candybar.shell.split: every piece fits the printer's usable volume, each piece has its own seed, a
right piece and its left twin are alike, no seam goes through a hand-hold or a cut-in, and the check notices a
layout that has lost a seam.

The cut is real on every run: the skin is split with the seam data and each piece is measured in its print
orientation. Only the skin (the outer form less the cavity) comes from a cache, because it takes about 20 minutes
to make. The cache file carries a fingerprint of everything that makes the skin (the values of dims.Blueprint, the
openings, and the source of dims, profiles, solids and cavity); when any of them changes, the fingerprint changes
and build_modules makes the skin again before the test cuts it. The limits come from params/printer.csv on every run.
"""
from __future__ import annotations

import unittest
from dataclasses import replace

import FreeCAD as App
import Part

from candybar.shell import split
from candybar.shell import structure

from . import support


class PrintBoxTest(unittest.TestCase):
    """print_box: the box of a piece after the turn on the bed that makes its larger side smallest."""

    def setUp(self) -> None:
        self.lim = split.Printer(240.0, 245.0, 256.0, "test")

    def rod(self, length: float) -> list[tuple[float, float, float]]:
        return [(0.0, 0.0, 0.0), (length, 0.0, 0.0), (length, 10.0, 0.0), (0.0, 10.0, 0.0), (0.0, 0.0, 10.0), (length, 10.0, 10.0)]

    def test_a_rod_of_300_fits_on_the_diagonal(self) -> None:
        box = split.print_box(self.rod(300.0), (0.0, 0.0, 1.0), self.lim)
        self.assertTrue(box["fits"])
        self.assertGreater(box["yaw"], 30.0)

    def test_a_rod_of_350_does_not_fit(self) -> None:
        self.assertFalse(split.print_box(self.rod(350.0), (0.0, 0.0, 1.0), self.lim)["fits"])

    def test_standing_up_it_must_be_lower_than_the_height_limit(self) -> None:
        self.assertFalse(split.print_box(self.rod(250.0), (1.0, 0.0, 0.0), self.lim)["fits"])
        self.assertTrue(split.print_box(self.rod(240.0), (1.0, 0.0, 0.0), self.lim)["fits"])


def zones(d) -> dict[str, Part.Shape]:
    """The right hand-hold with its walls, and the two legs of the right row of cut-ins with the wall behind them."""
    w = d.wall_t
    x0, x1, y0, y1, z0, z1 = structure.grip_box(d)
    box = lambda a, b: Part.makeBox(b[0] - a[0], b[1] - a[1], b[2] - a[2], App.Vector(*a))
    rw, deep = d.rear_w / 2, w + d.cut_in_depth
    return {"hand-hold": box((x0 - w, y0 - w, z0 - w), (x1 + w, y1, z1 + w)),
            "cut-ins on the rear": box((d.cut_in_x, d.body_d - deep, d.cut_in_z0), (rw, d.body_d, d.cut_in_z1)),
            "cut-ins on the side": box((rw - deep, d.cut_in_y, d.cut_in_z0), (rw, d.body_d, d.cut_in_z1))}


class SeamsFollowTheFormTest(unittest.TestCase):
    """The seam data alone, with no cut."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.d, _, _ = support.shell()
        cls.seams, cls.pieces = split.expanded(split.layout(cls.d))

    def test_no_seam_goes_through_a_hand_hold_or_a_cut_in(self) -> None:
        """Each seam polygon of the body keeps door_land or more from the hand-holds (with their walls) and from the
        cut-ins (with the wall behind them), on both sides."""
        mirror = lambda s: s.mirror(App.Vector(0, 0, 0), App.Vector(1, 0, 0))
        for name, zone in zones(self.d).items():
            for side, shape in (("R", zone), ("L", mirror(zone))):
                for seam in self.seams:
                    if seam.module != "body":
                        continue
                    gap = min(split.poly_face(poly).distToShape(shape)[0] for poly in seam.polys)
                    with self.subTest(zone=f"{name} {side}", seam=seam.name):
                        self.assertGreaterEqual(gap, self.d.door_land - 1e-6)

    def test_the_seams_of_the_sides_lie_in_the_creases_of_the_band_and_the_rear_shelf(self) -> None:
        d = self.d
        by_label = {s.label: s for s in self.seams}
        belt = {p[2] for poly in by_label["B1"].polys for p in poly}
        self.assertEqual(belt, {d.rear_shelf_z0})
        crease = [(p[1], p[2]) for poly in by_label["S1"].polys for p in poly if p[2] >= 0.0]
        from candybar.shell import profiles as pr
        for y, z in crease:
            self.assertAlmostEqual(y, pr.crease_y(d, z), places=6)

    def test_the_door_is_the_one_of_the_form(self) -> None:
        d = self.d
        door = next(s for s in self.seams if s.label == "DR")
        xs = {round(abs(p[0]), 6) for poly in door.polys for p in poly}
        zs = {round(p[2], 6) for poly in door.polys for p in poly}
        self.assertEqual(xs, {round(d.door_w / 2, 6)})
        self.assertEqual(zs, {round(d.door_z0, 6), round(d.door_z1, 6)})


class SplitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d, parts, _ = support.shell()
        cls.lim = split.printer(support.PARAMS)
        cav = None if split.skin_cached(cls.d) else support.cavity()
        cls.mods = split.build_modules(cls.d, log=lambda *_: None, parts=parts, cav=cav)
        cls.result = split.run(mods=cls.mods, lim=cls.lim, write=False, detail=False, log=lambda *_: None)
        cls.cuts = {k: cls.result[k] for k in (split.SHELL, split.PLATE)}

    def test_the_skin_is_valid_and_closed(self) -> None:
        for name in split.SKIN_MODULES:
            with self.subTest(module=name):
                skin = self.mods.skin[name]
                self.assertTrue(skin.isValid())
                self.assertEqual(len(skin.Solids), 1)
                self.assertTrue(all(sh.isClosed() for sh in skin.Shells))

    def test_every_piece_fits_the_printer(self) -> None:
        for key, res in self.cuts.items():
            with self.subTest(cut=key):
                big = {n: (r["x"], r["y"], r["z"]) for n, r in res["pieces"].items() if not r["fits"]}
                self.assertEqual(big, {})

    def test_every_piece_has_its_own_seed(self) -> None:
        for key, res in self.cuts.items():
            with self.subTest(cut=key):
                self.assertEqual([q for q in res["problems"] if q["problem"] != "debris"], [])

    def test_the_shell_has_its_pieces(self) -> None:
        names = set(self.cuts[split.SHELL]["pieces"])
        self.assertEqual(len(names), 32)
        for name in ("upper rear R", "upper rear L", "rear lower R", "middle L", "door half R", "hood centre"):
            self.assertIn(name, names)

    def test_the_cut_leaves_no_debris_worth_a_piece(self) -> None:
        for key, res in self.cuts.items():
            with self.subTest(cut=key):
                debris = sum(q["volume_mm3"] for q in res["problems"] if q["problem"] == "debris")
                self.assertLess(debris, 500.0)

    def test_a_right_piece_and_its_left_twin_are_alike(self) -> None:
        """The print box and the mass of each pair (run puts a difference into the problems, which
        test_every_piece_has_its_own_seed reads); here the numbers themselves."""
        for key, res in self.cuts.items():
            for name, r in res["pieces"].items():
                if not name.endswith(" R"):
                    continue
                left = res["pieces"][name[:-1] + "L"]
                with self.subTest(cut=key, piece=name):
                    self.assertAlmostEqual(max(r["x"], r["y"]), max(left["x"], left["y"]), delta=1.0)
                    self.assertAlmostEqual(r["z"], left["z"], delta=1.0)
                    self.assertAlmostEqual(r["mass_g"], left["mass_g"], delta=2.0)

    def test_each_hand_hold_is_whole_in_one_piece(self) -> None:
        """Each upper rear piece holds the recess of its side with its walls: the box of its mesh (the box of the
        shape itself is wider than the piece, because it takes in the poles of spline faces)."""
        d = self.d
        x0, x1, y0, y1, z0, z1 = structure.grip_box(d)
        shapes, _ = split.cut(*split.expanded(split.layout(d)), self.mods)
        for side, sign in (("R", 1.0), ("L", -1.0)):
            points, _ = shapes[f"upper rear {side}"].tessellate(0.5)
            xs, zs = [sign * p.x for p in points], [p.z for p in points]
            with self.subTest(side=side):
                self.assertGreater(min(xs), -0.2)
                self.assertLess(min(xs), x0 - d.wall_t)
                self.assertGreater(max(xs), x1 + d.wall_t)
                self.assertLess(min(zs), z0 - d.wall_t)
                self.assertGreater(max(zs), z1 + d.wall_t)

    def test_the_check_notices_a_layout_without_its_belt_line(self) -> None:
        """Without the belt seam B1 the middle and the upper piece of each side are one piece: too large, and two
        seeds in it."""
        lay = split.layout(self.d)
        lay = replace(lay, seams=tuple(s for s in lay.seams if s.label != "B1"), pieces=tuple(p for p in lay.pieces if p.module == "body"))
        seams, pieces = split.expanded(lay)
        shapes, problems = split.cut(seams, pieces, self.mods)
        self.assertIn("two seeds in one piece", {q["problem"] for q in problems})
        merged = split.measure(shapes["upper R"], (0.0, 0.0, 1.0), self.lim, None, None, self.d, detail=False)
        self.assertFalse(merged["fits"])

    def test_the_check_notices_twins_that_differ(self) -> None:
        rows = {"wall R": {"x": 100.0, "y": 50.0, "z": 20.0, "mass_g": 100}, "wall L": {"x": 104.0, "y": 50.0, "z": 20.0, "mass_g": 100}}
        self.assertEqual([q["value"] for q in split.mirror_gaps(rows)], ["x"])


if __name__ == "__main__":
    unittest.main()
