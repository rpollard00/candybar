from __future__ import annotations

import unittest

from candybar.shell import monitor_pictures as mp


class PictureTest(unittest.TestCase):
    def test_a_wide_picture_takes_the_width_of_the_lit_area(self) -> None:
        w, h = mp.picture((344.678, 215.424), 16 / 9, (1000.0, 1000.0))
        self.assertAlmostEqual(w, 344.678)
        self.assertAlmostEqual(h, 344.678 * 9 / 16)

    def test_a_narrow_picture_takes_the_height_of_the_lit_area(self) -> None:
        w, h = mp.picture((344.678, 215.424), 3 / 4, (1000.0, 1000.0))
        self.assertAlmostEqual(h, 215.424)
        self.assertAlmostEqual(w, 215.424 * 3 / 4)

    def test_the_window_cuts_a_lit_area_that_is_higher(self) -> None:
        w, h = mp.picture((376.32, 301.056), 4 / 3, (409.7, 280.4))
        self.assertAlmostEqual(h, 280.4)
        self.assertAlmostEqual(w, 280.4 * 4 / 3)

    def test_a_turned_unit_has_its_lit_area_turned(self) -> None:
        u = mp.UNITS[0]
        w, h = mp.pictures(u, turned=True, window=(1000.0, 1000.0))["tate 3:4"]
        self.assertAlmostEqual(w, u.lit_h)
        self.assertAlmostEqual(h, u.lit_h * 4 / 3)

    def test_the_present_unit_is_the_base_of_the_gain(self) -> None:
        row = mp.table()[0]
        self.assertEqual(row["key"], "present")
        self.assertTrue(all(c["gain"] == 0 for c in row["cells"].values()))
        self.assertEqual(row["cells"]["16:10"]["in"], 16.0)

    def test_a_body_larger_than_the_opening_lies_behind_the_ledges(self) -> None:
        self.assertEqual(mp.glass_t(354.0, 230.0), mp.GLASS)
        self.assertEqual(mp.glass_t(396.0, 324.0), mp.GLASS_BEHIND)
        self.assertEqual(mp.glass_t(452.0, 263.0), mp.GLASS_BEHIND)
