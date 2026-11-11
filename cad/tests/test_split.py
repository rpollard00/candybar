"""The seam options of candybar.shell.split: every piece of every option fits the printer's usable volume, and the
check notices a piece that does not.

The cut is real on every run: the skin is split with the seam data of each option and each piece is measured in
its print orientation. Only the skin (the outer form less the 4 mm cavity) comes from a cache, because it takes
about 12 minutes to make. The cache file carries a fingerprint of everything that makes the skin (the values of
dims.Blueprint, the openings, and the source of dims, profiles, solids and cavity); when any of them changes, the
fingerprint changes and build_modules makes the skin again before the test cuts it. The limits come from
params/printer.csv on every run.
"""
from __future__ import annotations

import unittest
from dataclasses import replace

from candybar.shell import split
from candybar.shell.dims import Blueprint

from . import support


class PrintBoxTest(unittest.TestCase):
    """The box after a turn on the bed: a thin rod longer than the bed's side fits on its diagonal, up to a point."""

    def setUp(self) -> None:
        self.lim = split.Printer(240.0, 245.0, 256.0, "test")

    def rod(self, length: float) -> list[tuple[float, float, float]]:
        return [(x, y, z) for x in (0.0, length) for y in (0.0, 10.0) for z in (0.0, 10.0)]

    def test_a_rod_of_300_fits_on_the_diagonal(self) -> None:
        box = split.print_box(self.rod(300.0), (0.0, 0.0, 1.0), self.lim)
        self.assertTrue(box["fits"])
        self.assertAlmostEqual(box["yaw"], 45.0, delta=1.0)

    def test_a_rod_of_350_does_not_fit(self) -> None:
        self.assertFalse(split.print_box(self.rod(350.0), (0.0, 0.0, 1.0), self.lim)["fits"])

    def test_standing_up_it_must_be_lower_than_the_height_limit(self) -> None:
        self.assertFalse(split.print_box(self.rod(250.0), (1.0, 0.0, 0.0), self.lim)["fits"])
        self.assertTrue(split.print_box(self.rod(240.0), (1.0, 0.0, 0.0), self.lim)["fits"])


class SeamOptionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d = Blueprint()
        cls.lim = split.printer(support.PARAMS)
        cls.mods = split.build_modules(cls.d, log=lambda *_: None)
        cls.result = split.run(mods=cls.mods, lim=cls.lim, write=False, detail=False, log=lambda *_: None)

    def test_every_piece_of_every_option_fits_the_printer(self) -> None:
        for key, res in self.result["options"].items():
            with self.subTest(option=key):
                big = {n: (r["x"], r["y"], r["z"]) for n, r in res["pieces"].items() if not r["fits"]}
                self.assertEqual(big, {})

    def test_every_piece_has_its_own_seed(self) -> None:
        for key, res in self.result["options"].items():
            with self.subTest(option=key):
                self.assertEqual([q for q in res["problems"] if q["problem"] != "debris"], [])

    def test_the_cut_leaves_no_debris_worth_a_piece(self) -> None:
        for key, res in self.result["options"].items():
            with self.subTest(option=key):
                debris = sum(q["volume_mm3"] for q in res["problems"] if q["problem"] == "debris")
                self.assertLess(debris, 500.0)

    def test_mirrored_pieces_have_the_same_print_box(self) -> None:
        for key, res in self.result["options"].items():
            for name, r in res["pieces"].items():
                if not name.endswith(" R"):
                    continue
                left = res["pieces"][name[:-1] + "L"]
                with self.subTest(option=key, piece=name):
                    self.assertAlmostEqual(max(r["x"], r["y"]), max(left["x"], left["y"]), delta=1.0)
                    self.assertAlmostEqual(r["z"], left["z"], delta=1.0)

    def test_the_check_notices_an_option_without_its_belt_line(self) -> None:
        """Without the belt seam B1 the middle and the upper piece of each side are one piece: too large, and two
        seeds in it."""
        opt = next(o for o in split.options(self.d, self.result["door"]) if o.key == "A")
        opt = replace(opt, seams=tuple(s for s in opt.seams if s.label != "B1"), pieces=tuple(p for p in opt.pieces if p.module == "body"))
        seams, pieces = split.expanded(opt)
        shapes, problems = split.cut(seams, pieces, self.mods)
        self.assertIn("two seeds in one piece", {q["problem"] for q in problems})
        merged = split.measure(shapes["upper R"], (0.0, 0.0, 1.0), self.lim, None, None, self.d, detail=False)
        self.assertFalse(merged["fits"])


if __name__ == "__main__":
    unittest.main()
