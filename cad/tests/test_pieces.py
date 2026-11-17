"""The print pieces of candybar.shell.pieces: the joint generator, and the whole set.

The generator is tested on three small shells, which take seconds: a box cut by a level seam (a straight seam with
four corners), a shell whose upper part leaves the seam at 45 degrees (a seam in a crease), and a box with a second,
upright seam in its lower half (three pieces meet). The pieces of each are made with the real cut of
candybar.shell.split and the real generator.

The whole set (WholeSetTest, the slow group) is made once, from the skin in the cache; it takes about 25 minutes, and
CANDYBAR_PIECES_SKIP_SET=1 leaves it out. It needs the outer solids of the default build on disk (cad/out/shell-rev7)
and the skin in the cache. Its tests are rules of the joints that pieces.check_set does not check yet: when the build
checks them, they go."""
from __future__ import annotations

import math
import os
import unittest

import FreeCAD as App
import Part

from candybar.shell import pieces, split
from candybar.shell.dims import Blueprint
from candybar.shell.joints import JOINT

from . import support

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


@support.slow
class WholeSetTest(unittest.TestCase):
    """Every seam of the layout, the floor and the ribs: about 25 minutes."""

    @classmethod
    def setUpClass(cls) -> None:
        from pathlib import Path

        cls.d = Blueprint()
        out = Path(os.environ.get("CANDYBAR_PIECES_CACHE") or pieces.CAD / "out" / "pieces")
        quiet = lambda *_: None
        cls.pl = pieces.plain(cls.d, out, quiet)
        cls.items = pieces.hardware()
        cls.res = pieces.generate(cls.d, cls.pl, None, None, cls.items, quiet)
        cls.rep = pieces.seam_report(cls.res)
        # as the build does it: the pieces go through their BREP files, and the checks are on what the files hold
        folder = support.temp_dir()
        pieces.write_parts(folder, cls.res.pieces)
        cls.made = pieces.read_parts(folder)[0]
        cls.chk = pieces.check_set(cls.d, cls.pl, cls.made, cls.rep, cls.items, quiet)

    def test_there_are_30_pieces(self) -> None:
        # 2026-11-16: the three stand-ins of the hood band left the split (band A has its own printed parts), and the
        # marquee window of band A makes the strip under it a piece of its own (hood sill)
        self.assertEqual(len(self.res.pieces), 30)

    def test_the_joints_add_no_clash_with_the_hardware(self) -> None:
        # a plain piece may already be in a keep-out zone (the fit study reports those); the joints must not add to it
        more = [h for h in self.chk["hardware"] if h["mm3"] - h["of_the_plain_piece_mm3"] > pieces.BUILD.clash_mm3]
        self.assertEqual(more, [])

    def test_a_right_piece_and_its_left_twin_differ_only_where_the_hardware_differs(self) -> None:
        twin = lambda n: n[:-2] if n.endswith((" R", " L")) else n
        cut = {twin(h["piece"]) for h in self.rep["hits"]}
        # the two pieces of a seam on the centre line: one has the key and the pilot holes, its twin the groove and the pockets
        centre = {twin(p["head"]) for p in self.rep["pairs"] if twin(p["head"]) == twin(p["pilot"])}
        # the hood centre prints on one of its two cut faces: the key is on the hood side there, and on the hood centre at the other end
        moved = {twin(n) for p in self.rep["pairs"] if p["key"] and p["key"] != p["pilot"] for n in (p["head"], p["pilot"])}
        # the door halves are the designed halves of candybar.shell.rear: the fan vent is in R and the hot-air vent in L,
        # and this generator adds nothing to them (seams DR and R4 are skipped)
        designed = {"door half"}
        self.assertFalse(any(n.startswith("door half") for n in self.res.added))
        odd = [t for t in self.chk["twins_that_differ"] if t["piece"] not in cut | centre | moved | designed and not t["piece"].startswith("floor")]
        self.assertEqual(odd, [])

    def test_every_bonded_seam_has_a_flange_on_both_pieces_or_is_a_known_exception(self) -> None:
        none = sorted({(s["seam"].split()[0], s["piece"].rsplit(" ", 1)[0] if s["piece"][-1] in "RL" else s["piece"])
                       for s in self.rep["sides"] if s["flange_cm3"] == 0.0})
        self.assertEqual(none, sorted(pieces.NO_FLANGE))

    def test_every_seam_longer_than_a_screw_run_has_screws(self) -> None:
        bare = sorted({p["seam"].split()[0] for p in self.rep["pairs"] if p["run_mm"] >= 2 * pieces.BUILD.run_screw and not p["screws"]})
        # a seam of this list has a flange and a key on both pieces; clamps hold it while the bond sets
        self.assertEqual(bare, sorted(pieces.NO_SCREW))

    def test_no_key_stands_on_a_face_that_lies_on_the_printer_bed(self) -> None:
        where = {(sd["seam"], sd["k"], sd["piece"]): sd["in_print"] for sd in self.rep["sides"]}
        bad = [(p["seam"], p["key"]) for p in self.rep["pairs"] if p["key"] and where[(p["seam"], p["k"], p["key"])] == "on the bed"]
        self.assertEqual(bad, [])
        self.assertGreater(len([p for p in self.rep["pairs"] if p["key"]]), 20)

    def test_the_floor_has_nine_tiles_and_every_tile_is_screwed(self) -> None:
        fl = self.rep["floor"]
        tiles = [n for n in self.res.pieces if n.startswith("floor")]
        self.assertEqual(len(tiles), 9)
        used = {s["upper"] for s in fl["lap_screws"]} | {s["lower"] for s in fl["lap_screws"]} | {s["tile"] for s in fl["foot_screws"]}
        self.assertEqual(sorted(used), sorted(tiles))
        self.assertEqual(fl["hardware_in_floor"], [])

    def test_each_closing_piece_has_the_closing_gap_at_its_upright_closing_seams(self) -> None:
        """The brow and the upper rear R go in last, each into two upright seams at once (docs/blueprint/index.md,
        "Where each ring closes"): their seam faces stand the closing gap back from the seam plane, flange faces
        included. No material of the piece is nearer to the plane than that."""
        from candybar.shell.joints import OTHER_JOINTS

        gap = OTHER_JOINTS.closing_gap
        done = {c["piece"]: c for c in self.rep["closing"]}
        self.assertEqual(set(done), {"brow", "upper rear R"})
        self.assertEqual(done["brow"]["seams"], ["W1"])
        self.assertEqual(done["upper rear R"]["seams"], ["R3", "R5"])
        for side in self.res.sides:
            label = side.cf.seam.split()[0]
            if not pieces.closing(side.cf.piece, label)[1]:
                continue
            with self.subTest(piece=side.cf.piece, seam=side.cf.seam):
                self.assertGreater(done[side.cf.piece]["removed_mm3"], 0.0)
                near = pieces.closing_slab(side.cf, gap - 0.02)
                self.assertLess(self.res.pieces[side.cf.piece].common(near).Volume, 0.05)

    def test_joint_7_rings_the_body_top_and_the_hood_lies_on_it(self) -> None:
        """The top ring on every piece of the body top and the foot on every hood piece (docs/blueprint/index.md,
        joint 7); four cones on the ring, each in a socket of the foot; the seam gap of the form stays open outside
        the wall: nothing of the ring or the foot is in the outer part of the gap."""
        made = {r["piece"] for r in self.rep["ring"] if r["cm3"] > 10.0}
        self.assertEqual(made, set(pieces.RING_PIECES) | set(pieces.FOOT_PIECES))
        cones = self.rep["ring_cones"]
        self.assertEqual(len(cones), 4)
        self.assertTrue(all(c["foot"] in pieces.FOOT_PIECES for c in cones), cones)
        # the gap between the body top and the foot of the hood: at points 1 and 3 inside the outer line of the body
        # top, in the middle of the gap, no piece has material
        body = self.pl.outer["body"]
        wire = max(body.slice(V(0, 0, 1), self.d.body_top - 0.01), key=lambda w: w.Length)
        z = self.d.body_top + self.d.seam_gap / 2
        points = []
        for e in wire.Edges:
            for t in (0.25, 0.5, 0.75):
                u = e.FirstParameter + (e.LastParameter - e.FirstParameter) * t
                p, tan = e.valueAt(u), e.tangentAt(u)
                n = V(-tan.y, tan.x, 0.0)
                if not body.isInside(V(p.x, p.y, self.d.body_top - 1.0) + n * 1.0, 1e-4, True):
                    n = n * -1.0
                points += [V(p.x, p.y, z) + n * k for k in (1.0, 3.0)]
        self.assertGreater(len(points), 40)
        for name in pieces.RING_PIECES + pieces.FOOT_PIECES:
            with self.subTest(piece=name):
                shape = self.made[name]
                inside = [q for q in points if shape.BoundBox.isInside(q) and shape.isInside(q, 1e-4, True)]
                self.assertEqual(inside, [])

    def test_the_hood_is_bolted_with_four_screws_that_a_key_reaches_from_below(self) -> None:
        """The bolted hood (2026-11-16): four screws, each with a boss in a piece of the ring and a boss with the hole
        of the insert in a piece of the foot, a mirror pair on each side; a hex key goes straight up to each head
        through HOOD_KEY of free room."""
        from candybar.shell.joints import OTHER_JOINTS as oj

        rows = self.rep["hood_screws"]
        self.assertEqual(len(rows), 4)
        for r in rows:
            with self.subTest(at=r["at"]):
                self.assertIn(r["ring"], pieces.RING_PIECES)
                self.assertIn(r["foot"], pieces.FOOT_PIECES)
                self.assertGreater(r["ring_boss_cm3"], 1.0)
                self.assertGreater(r["foot_boss_cm3"], 1.0)
                x, y, _ = r["at"]
                holes = support.hole_centres(self.made[r["foot"]], oj.insert_hole_d)
                self.assertTrue(any(math.dist(h, (x, y)) < 0.05 for h in holes), holes)
        xs = sorted(round(r["at"][0], 3) for r in rows)
        self.assertEqual(xs[:2], [-xs[3], -xs[2]])
        self.assertEqual(len(self.chk["hood_reach"]), 4)
        self.assertTrue(all(r["free"] >= pieces.HOOD_KEY for r in self.chk["hood_reach"]), self.chk["hood_reach"])

    def test_seam_l1_has_no_screw_in_the_span_of_the_cut_ins(self) -> None:
        # a head pocket there would cut into the step of the skin behind the lowest cut-in
        l1 = [sc["at"] for p in self.rep["pairs"] if p["seam"].split()[0] == "L1" for sc in p["screws"]]
        self.assertGreater(len(l1), 0)
        inside = [at for at in l1 if pieces.in_cut_in_span(V(*at), self.d)]
        self.assertEqual(inside, [])

    def test_no_flange_is_in_a_part_of_the_rear(self) -> None:
        rear = {n for n, role, _ in self.items if role == "rear"}
        self.assertIn("head_rail_r", rear)
        more = [h for h in self.chk["hardware"] if h["item"] in rear and h["mm3"] - h["of_the_plain_piece_mm3"] > pieces.BUILD.clash_mm3]
        self.assertEqual(more, [])

    def test_the_flanges_stop_short_of_the_door_opening(self) -> None:
        d, b = self.d, pieces.BUILD
        x = d.door_w / 2 + b.door_stop - 0.5
        zone = Part.makeBox(2 * x, 30.0, d.door_z1 - d.door_z0 + 2 * b.door_stop - 1.0, V(-x, d.body_d - d.wall_t - 28.0, d.door_z0 - b.door_stop + 0.5))
        for sd in self.res.sides + self.res.ribs:
            if sd.solid is not None and sd.solid.BoundBox.intersect(zone.BoundBox):
                self.assertLess(sd.solid.common(zone).Volume, 1.0, f"{sd.cf.seam} {sd.cf.piece}")


