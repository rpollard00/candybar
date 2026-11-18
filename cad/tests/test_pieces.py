"""The print pieces of candybar.shell.pieces: the joint generator, and the whole set.

The generator is tested on three small shells, which take seconds: a box cut by a level seam (a straight seam with
four corners), a shell whose upper part leaves the seam at 45 degrees (a seam in a crease), and a box with a second,
upright seam in its lower half (three pieces meet). The pieces of each are made with the real cut of
candybar.shell.split and the real generator.

The rules of the joints on the whole set are checked by the build itself (pieces.set_rules, check.json "rules"),
since 2026-11-17; they have no test here."""
from __future__ import annotations

import unittest

import FreeCAD as App
import Part

from candybar.shell import pieces, split
from candybar.shell.dims import Blueprint
from candybar.shell.joints import JOINT


V = App.Vector
WALL = JOINT.wall_t


def shell_of(outer: Part.Shape) -> Part.Shape:
    """A skin of wall_t inside an outer solid."""
    inner = outer.makeOffsetShape(-WALL, 1e-3, join=2)
    return outer.cut(inner)


SEAM_Z = 120.0   # the level seam of the test shells: a screwdriver has room on both sides of it


def box_outer() -> Part.Shape:
    return Part.makeBox(160.0, 120.0, 2 * SEAM_Z)


def crease_outer() -> Part.Shape:
    """A box of 100 x 100 x SEAM_Z, and above it a head that leaves the box at 45 degrees and goes on upright."""
    square = lambda s, z: Part.makePolygon([V(-s, -s, z), V(s, -s, z), V(s, s, z), V(-s, s, z), V(-s, -s, z)])
    low = Part.makeBox(100.0, 100.0, SEAM_Z, V(-50.0, -50.0, 0.0))
    flare = Part.makeLoft([square(50.0, SEAM_Z), square(75.0, SEAM_Z + 25.0)], True, True)
    head = Part.makeBox(150.0, 150.0, 115.0, V(-75.0, -75.0, SEAM_Z + 25.0))
    return low.fuse(flare).fuse(head).removeSplitter()


def level(z: float) -> tuple:
    return split.level([(-300.0, -300.0), (300.0, -300.0), (300.0, 300.0), (-300.0, 300.0)], z)


def plain_of(outer: Part.Shape, seams: list[split.Seam], named: list[split.Piece]) -> pieces.Plain:
    mods = split.Modules({"test": shell_of(outer)}, {"test": outer}, {}, "test")
    shapes, problems = split.cut(seams, named, mods)
    assert not problems, problems
    return pieces.Plain(shapes, {"test": outer}, seams, named, "test")


def made(pl: pieces.Plain) -> pieces.Result:
    return pieces.generate(Blueprint(), pl, None, None, None, log=lambda *_: None, with_feet=False, with_ribs=False, with_floor=False)


def piece(name: str, seed: tuple) -> split.Piece:
    return split.Piece(name, "test", seed, (0.0, 0.0, 1.0), "")


def seam(label: str, polys: tuple) -> split.Seam:
    return split.Seam(label, "test", polys, split.FACE, "bond-fill", "")


def overlap(res: pieces.Result) -> float:
    names = list(res.pieces)
    return max(res.pieces[a].common(res.pieces[b]).Volume for i, a in enumerate(names) for b in names[i + 1:])


class StraightSeamTest(unittest.TestCase):
    """A box cut level: each half gets a flange round the seam, and the two lock and screw together."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.pl = plain_of(box_outer(), [seam("T1", level(SEAM_Z))], [piece("low", (2.0, 60.0, 20.0)), piece("high", (2.0, 60.0, SEAM_Z + 60.0))])
        cls.res = made(cls.pl)

    def test_each_piece_is_one_valid_solid(self) -> None:
        for name, s in self.res.pieces.items():
            self.assertTrue(s.isValid(), name)
            self.assertEqual(len(s.Solids), 1, name)

    def test_each_side_has_a_flange_with_a_gusset(self) -> None:
        self.assertEqual(len(self.res.sides), 2)
        j = JOINT
        ring = 2 * (160.0 + 120.0)
        for sd in self.res.sides:
            self.assertIsNotNone(sd.solid, sd.cf.piece)
            self.assertTrue(sd.gusset)
            self.assertFalse(sd.lean_out)
            # the flange alone is flange_h x flange_t along the ring, less the corners; the gusset adds half as much again
            self.assertGreater(sd.solid.Volume, 0.8 * ring * j.flange_h * j.flange_t)

    def test_the_flange_reaches_flange_h_inward_of_the_skin(self) -> None:
        j = JOINT
        low = self.res.pieces["low"]
        inside = lambda x, y, z: low.isInside(V(x, y, z), 1e-6, False)
        z = SEAM_Z - split.KERF / 2 - 1.0
        self.assertTrue(inside(80.0, WALL + j.flange_h - 0.5, z))
        self.assertFalse(inside(80.0, WALL + j.flange_h + 0.5, z))
        # the gusset: 45 degrees from the flange tip to the wall
        self.assertTrue(inside(80.0, WALL + 2.0, z - j.flange_t - j.gusset_leg + 5.0))
        self.assertFalse(inside(80.0, WALL + 2.0, z - j.flange_t - j.gusset_leg - 1.0))

    def test_the_pieces_do_not_share_volume(self) -> None:
        self.assertLess(overlap(self.res), 1.0)

    def test_the_key_moves_to_the_other_piece_when_its_face_lies_on_the_bed(self) -> None:
        j = pieces.joint()
        # the same pair, but the lower piece prints upside down: its seam face is on the bed
        pair = self.res.pairs[0]
        fresh = pieces.Pair(pair.a, pair.b, pair.mate, head=pair.head, pilot=pair.pilot, screws=pair.screws, runs=pair.runs)
        key, groove = pieces.key_and_groove(fresh, j, ups={"low": (0.0, 0.0, -1.0), "high": (0.0, 0.0, -1.0)})
        self.assertEqual(fresh.key.cf.piece, "high")
        self.assertIsNotNone(key)
        # the key now stands down from the upper piece: below the seam plane
        self.assertLess(key.BoundBox.ZMin, SEAM_Z - 1.0)
        self.assertGreater(key.BoundBox.ZMax, SEAM_Z)
        fresh = pieces.Pair(pair.a, pair.b, pair.mate, head=pair.head, pilot=pair.pilot, screws=pair.screws, runs=pair.runs)
        pieces.key_and_groove(fresh, j, ups={"low": (0.0, 0.0, 1.0), "high": (0.0, 0.0, 1.0)})
        self.assertEqual(fresh.key.cf.piece, "low")

    def test_there_is_one_pair_with_screws_on_every_wall(self) -> None:
        self.assertEqual(len(self.res.pairs), 1)
        pair = self.res.pairs[0]
        # runs of 159 and 119 at the pitch of 60: three and two on each wall
        self.assertEqual(len(pair.screws), 10, pair.notes)
        # level seam: the heads go in the upper piece
        self.assertEqual(pair.head.cf.piece, "high")
        for sc in pair.screws:
            self.assertGreaterEqual(sc.free, pieces.BUILD.driver_len)

    def test_the_key_stands_in_the_groove_with_the_clearance(self) -> None:
        j = JOINT
        low, high = self.res.pieces["low"], self.res.pieces["high"]
        # a point in the key, 10 mm beside a screw: in the lower piece, above the seam plane
        sc = self.res.pairs[0].screws[0]
        at = sc.at + sc.tangent * 20.0 + (V(0, 0, 1).cross(sc.tangent)) * 0.0
        u_mid = sum(j.key_u) / 2 - j.screw_u
        inward = V(80.0, 60.0, sc.at.z) - sc.at
        inward = inward - sc.tangent * inward.dot(sc.tangent)
        inward.normalize()
        p = at + inward * u_mid + V(0, 0, 1) * (j.key_proj / 2)
        self.assertTrue(low.isInside(p, 1e-6, False), "no key")
        self.assertFalse(high.isInside(p, 1e-6, False), "no groove")
        # beside the key, inside the clearance, there is neither
        q = p + inward * (j.key_w / 2 + j.groove_clearance / 2)
        self.assertFalse(low.isInside(q, 1e-6, False))
        self.assertFalse(high.isInside(q, 1e-6, False))

    def test_the_holes_are_in_both_pieces(self) -> None:
        j = pieces.joint()
        sc = self.res.pairs[0].screws[0]
        low, high = self.res.pieces["low"], self.res.pieces["high"]
        self.assertFalse(low.isInside(sc.at + V(0, 0, -5.0), 1e-6, False), "no pilot hole")
        self.assertTrue(low.isInside(sc.at + V(0, 0, -j.pilot_depth - 1.0), 1e-6, False), "the pilot hole is too deep")
        self.assertFalse(high.isInside(sc.at + V(0, 0, 3.0), 1e-6, False), "no clearance hole")
        self.assertFalse(high.isInside(sc.at + V(j.head_pocket_d / 2 - 0.5, 0, j.flange_t + 3.0), 1e-6, False), "no head pocket")

    def test_the_outer_edge_has_the_v_for_the_filler(self) -> None:
        j = JOINT
        low = self.res.pieces["low"]
        z = SEAM_Z - split.KERF / 2
        # inside the V: a quarter of its depth from the outside, a quarter of its half width from the seam
        self.assertFalse(low.isInside(V(80.0, j.vgroove_d / 4, z - j.vgroove_w / 8), 1e-6, False))
        # outside it: under its tip, and inward of its depth
        self.assertTrue(low.isInside(V(80.0, j.vgroove_d / 4, z - j.vgroove_w / 2 - 0.2), 1e-6, False))
        self.assertTrue(low.isInside(V(80.0, j.vgroove_d + 0.2, z - 0.1), 1e-6, False))


class CreaseSeamTest(unittest.TestCase):
    """A seam in a crease: the wall of the upper piece leaves the seam plane at 45 degrees."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.pl = plain_of(crease_outer(), [seam("T1", level(SEAM_Z))], [piece("low", (48.0, 0.0, 20.0)), piece("high", (73.0, 0.0, SEAM_Z + 60.0))])
        cls.res = made(cls.pl)
        cls.side = {sd.cf.piece: sd for sd in cls.res.sides}

    def test_the_upper_side_is_found_as_a_crease(self) -> None:
        self.assertTrue(self.side["high"].lean_out)
        self.assertFalse(self.side["high"].gusset)
        self.assertFalse(self.side["low"].lean_out)
        self.assertTrue(self.side["low"].gusset)

    def test_each_piece_is_one_valid_solid(self) -> None:
        for name, s in self.res.pieces.items():
            self.assertTrue(s.isValid(), name)
            self.assertEqual(len(s.Solids), 1, name)

    def test_the_flange_of_the_crease_side_stays_inside_the_form(self) -> None:
        outer = self.pl.outer["test"]
        for name, s in self.res.pieces.items():
            self.assertLess(s.cut(outer).Volume, 0.01, name)

    def test_the_flange_of_the_crease_side_joins_the_wall_with_no_slot(self) -> None:
        # straight above the outer line, just over the flange, the wall has already left: the flange must fill up to it
        high = self.res.pieces["high"]
        z = SEAM_Z + split.KERF / 2 + JOINT.flange_t - 0.5
        for u in (0.5, 2.0, 6.0, 12.0):
            self.assertTrue(high.isInside(V(50.0 - u, 0.0, z), 1e-6, False), u)

    def test_the_pieces_do_not_share_volume(self) -> None:
        self.assertLess(overlap(self.res), 1.0)

    def test_the_screws_have_their_heads_in_the_lower_piece_or_the_upper(self) -> None:
        pair = self.res.pairs[0]
        self.assertGreater(len(pair.screws), 0, pair.notes)


UPRIGHT_X = 60.0


class ThreePiecesTest(unittest.TestCase):
    """A level seam, and under it an upright seam: three pieces meet on the level seam."""

    @classmethod
    def setUpClass(cls) -> None:
        # the upright seam is off the middle, so that a screwdriver has its length on one side of it
        upright = split.front([(UPRIGHT_X, -10.0), (UPRIGHT_X, SEAM_Z)], -10.0, 130.0)
        cls.pl = plain_of(box_outer(), [seam("T1", level(SEAM_Z)), seam("T2", upright)],
                          [piece("low a", (2.0, 60.0, 20.0)), piece("low b", (158.0, 60.0, 20.0)), piece("high", (2.0, 60.0, SEAM_Z + 60.0))])
        cls.res = made(cls.pl)

    def test_each_piece_is_one_valid_solid(self) -> None:
        self.assertEqual(sorted(self.res.pieces), ["high", "low a", "low b"])
        for name, s in self.res.pieces.items():
            self.assertTrue(s.isValid(), name)
            self.assertEqual(len(s.Solids), 1, name)

    def test_the_pieces_do_not_share_volume(self) -> None:
        self.assertLess(overlap(self.res), 1.0)

    def test_there_are_three_pairs(self) -> None:
        names = sorted(tuple(sorted((p.a.cf.piece, p.b.cf.piece))) for p in self.res.pairs)
        self.assertEqual(names, [("high", "low a"), ("high", "low b"), ("low a", "low b")])

    def test_the_flange_of_a_lower_piece_ends_at_the_upright_seam(self) -> None:
        a = self.res.pieces["low a"]
        z = SEAM_Z - split.KERF / 2 - 2.0
        self.assertTrue(a.isInside(V(UPRIGHT_X - split.KERF / 2 - 0.5, WALL + 3.0, z), 1e-6, False))
        self.assertFalse(a.isInside(V(UPRIGHT_X + 0.5, WALL + 3.0, z), 1e-6, False))

    def test_the_two_flanges_of_a_lower_piece_make_a_corner(self) -> None:
        # in the corner of the level flange and the upright flange, inward of both gussets, the piece is solid
        a = self.res.pieces["low a"]
        j = JOINT
        self.assertTrue(a.isInside(V(UPRIGHT_X - 3.0, WALL + j.flange_h - 1.0, SEAM_Z - 3.0), 1e-6, False))

    def test_every_pair_has_screws(self) -> None:
        for p in self.res.pairs:
            self.assertGreater(len(p.screws), 0, p.name)


class SimpleLineTest(unittest.TestCase):
    """The outer line of a cut face made simple."""

    def line(self, pts: list[tuple]) -> list[Part.Edge]:
        return [Part.makeLine(V(*a), V(*b)) for a, b in zip(pts, pts[1:])]

    def test_an_edge_break_between_two_lines_becomes_their_corner(self) -> None:
        edges = self.line([(0, 0, 0), (50, 0, 0), (51, 1, 0), (51, 60, 0)])
        segs, dropped = pieces.simple_line(edges, V(0, 0, 1))
        self.assertEqual(len(segs), 2)
        self.assertEqual(dropped, [False, False])
        self.assertAlmostEqual(segs[0].q.x, 51.0)
        self.assertAlmostEqual(segs[0].q.y, 0.0)

    def test_a_short_tail_behind_an_edge_break_is_left_out(self) -> None:
        edges = self.line([(0, 0, 0), (80, 0, 0), (81, 1, 0), (81, 5, 0)])
        segs, dropped = pieces.simple_line(edges, V(0, 0, 1))
        self.assertEqual(len(segs), 1)
        self.assertEqual(dropped, [False, True])

    def test_a_step_between_two_parallel_lines_stays_as_a_chord(self) -> None:
        edges = self.line([(0, 0, 0), (40, 0, 0), (41, 1, 0), (90, 1, 0)])
        segs, _ = pieces.simple_line(edges, V(0, 0, 1))
        self.assertEqual(len(segs), 3)
        self.assertAlmostEqual(segs[1].length, 2 ** 0.5, places=6)

    def test_a_tight_curve_becomes_chords_and_a_wide_arc_stays(self) -> None:
        tight = Part.makeCircle(10.0, V(0, 0, 0), V(0, 0, 1), 0.0, 90.0)
        wide = Part.makeCircle(60.0, V(0, 0, 0), V(0, 0, 1), 0.0, 30.0)
        segs, _ = pieces.simple_line([tight], V(0, 0, 1))
        self.assertGreater(len(segs), 2)
        self.assertTrue(all(s.c is None for s in segs))
        segs, _ = pieces.simple_line([wide], V(0, 0, 1))
        self.assertEqual(len(segs), 1)
        self.assertIsNotNone(segs[0].c)
        self.assertAlmostEqual(abs(segs[0].turn), 30.0, places=6)


class ClosingTest(unittest.TestCase):
    def test_the_closing_pieces_and_their_seams(self) -> None:
        self.assertEqual(pieces.closing("brow", "W1"), (True, True))
        self.assertEqual(pieces.closing("upper rear R", "R5"), (True, True))
        self.assertEqual(pieces.closing("upper rear L", "R5"), (False, False))
        self.assertEqual(pieces.closing("middle R", "L1"), (True, False))
        self.assertEqual(pieces.closing("middle L", "L1"), (False, False))


class FloorDataTest(unittest.TestCase):
    """The floor, as data."""

    def test_a_side_tile_lies_under_the_centre_tile_and_a_middle_tile_under_the_front_and_rear(self) -> None:
        f = pieces.lower_first
        self.assertLess(f("floor front side R"), f("floor front centre"))
        self.assertLess(f("floor middle side L"), f("floor rear side L"))
        self.assertLess(f("floor middle centre"), f("floor rear centre"))

    def test_the_floor_screw_does_not_reach_the_table(self) -> None:
        self.assertLess(pieces.FLOOR.screw_len, pieces.FLOOR.t)

    def test_the_foot_flange_and_the_lip_over_it_make_the_floor(self) -> None:
        fl = pieces.FLOOR
        self.assertAlmostEqual(fl.foot_thick, fl.t / 2)
        self.assertGreater(fl.foot_w - fl.inset, 8.0)

    def test_no_tile_with_its_laps_is_longer_than_the_bed(self) -> None:
        d = Blueprint()
        seams, named = split.expanded(split.layout(d))
        cells = pieces.tile_cells(pieces.Plain({}, {}, seams, named, ""))
        lim = split.printer()
        lap = pieces.OTHER_JOINTS.lap_w
        half = d.width / 2
        for name, (x0, x1, y0, y1) in cells.items():
            w = min(x1, half) - max(x0, -half) + (lap if "side" in name else 0.0)
            deep = min(y1, d.body_d) - max(y0, 0.0) + (2 * lap if "middle" in name else 0.0)
            self.assertLessEqual(max(w, deep), lim.xy, name)
