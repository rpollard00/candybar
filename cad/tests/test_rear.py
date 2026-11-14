"""The rear (candybar.shell.rear): the door in its opening, its vents, the shroud and the duct, the openings of the
lower rear wall. The first classes make only the parts of the rear. RearInTheFitStudyTest needs the cavity of the
shell, and RearOnThePiecesTest cuts the skin of the cache into pieces and finishes them; both take some minutes."""
from __future__ import annotations

import math
import unittest
from dataclasses import replace

import FreeCAD as App
import Part

from candybar.shell import check
from candybar.shell import fit, joints, rear, split, structure
from candybar.shell.dims import Blueprint
from tests import support

V = App.Vector
# the longest level edge over an opening of the upright wall that prints as a bridge with no support
BRIDGE = 20.0


def level_roof(face: Part.Face) -> float:
    """How far across the outline of a face of the plane y = 0 runs over the opening at less than 45 degrees from
    level: what the printer must bridge when the wall stands upright."""
    run = 0.0
    for e in face.OuterWire.Edges:
        pts = e.discretize(Number=max(2, int(e.Length / 0.2) + 1))
        for a, b in zip(pts, pts[1:]):
            m = (a + b) * 0.5
            over = face.isInside(V(m.x, 0, m.z - 0.05), 1e-6, True) and not face.isInside(V(m.x, 0, m.z + 0.05), 1e-6, True)
            if over and abs(b.z - a.z) < abs(b.x - a.x) * math.tan(math.radians(44.9)):
                run += abs(b.x - a.x)
    return run


class RearValuesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d, cls.r = Blueprint(), rear.Rear()
        cls.p = rear.place(cls.d)
        cls.f = rear.frame(cls.d, cls.r)

    def test_the_door_is_the_opening_of_the_form_less_its_gap(self) -> None:
        d, r, f = self.d, self.r, self.f
        self.assertAlmostEqual(f.x_door, d.door_w / 2 - r.door_gap)
        self.assertAlmostEqual(f.zd0, d.door_z0 + r.door_gap)
        self.assertAlmostEqual(f.zd1, d.door_z1 - r.door_gap)
        self.assertAlmostEqual(f.y_out - f.y_in, d.wall_t)

    def test_the_joint_lies_in_the_wall_and_not_in_the_strip_beside_the_cut_ins(self) -> None:
        """The land stands inside the opening; nothing of it stands in the door_land of the form."""
        for side in (1, -1):
            lip, tongue = rear.sill_lip(self.d, self.r, self.p, side), rear.side_tongue(self.d, self.r, side)
            for part in (lip, tongue):
                self.assertLessEqual(max(abs(part.BoundBox.XMin), abs(part.BoundBox.XMax)), self.d.door_w / 2 + self.r.post_w)
            self.assertLessEqual(lip.BoundBox.YMax, self.f.y_lap + 1e-6)
            above = lip.common(rear.box(-300, 300, 0, 600, self.d.door_z0, 400))
            self.assertGreaterEqual(above.BoundBox.YMin, self.f.y_in - 1e-6)

    def test_the_rib_under_the_sill_keeps_out_of_the_space_over_the_supply_fan(self) -> None:
        x0, x1 = rear.sill_rib_span(self.d, self.r, self.p, -1)
        self.assertLessEqual(x1, -self.p.psu_x1 - self.r.sill_rib_gap + 1e-6)
        self.assertGreater(x1 - x0, 50.0)
        self.assertEqual(rear.sill_rib_span(self.d, self.r, self.p, 1), (0.0, self.f.x_ring))

    def test_the_duct_and_the_board_pass_the_clear_opening(self) -> None:
        lay = fit.Layout()
        self.assertGreaterEqual(lay.duct_in_door, self.r.land + 1.0)
        self.assertLessEqual(self.f.z_lip, self.p.z(self.p.v["bc_shroud_y0"]) + 1e-6)
        self.assertGreater(self.f.z_rail0, self.p.z(self.p.v["bc_pcb_w_pwr"]))

    def test_the_posts_start_above_the_space_over_the_supply_fan(self) -> None:
        """The clear space over the fan of the power supply reaches the rear wall up to the lip's top."""
        for side in (1, -1):
            post = rear.side_tongue(self.d, self.r, side).common(rear.box(-300, 300, 0, self.f.y_in - 0.01, 0, 400))
            self.assertGreaterEqual(post.BoundBox.ZMin, self.f.z_lip - 1e-6)

    def test_the_fastener_has_its_flat_and_its_room(self) -> None:
        r, f, d = self.r, self.f, self.d
        self.assertGreaterEqual(r.qt_flat, r.qt_head)
        self.assertLessEqual(f.zq + r.qt_head / 2, f.zd1 - d.edge_break)
        for vent in (rear.fan_vent(r, self.p), [rear.mirrored(v) for v in rear.hot_vent(r, self.p)]):
            near = min(v.distToShape(Part.Vertex(V(r.qt_x, 0, f.zq)))[0] for v in vent)
            self.assertGreaterEqual(near, r.qt_flat / 2)
        rail = rear.head_rail(d, r, 1)
        room = rear.box(r.qt_x - r.qt_pocket_w / 2 + 0.01, r.qt_x + r.qt_pocket_w / 2 - 0.01, f.y_in - r.rail_d, f.y_in - r.qt_web - 0.01,
                        f.zq - r.qt_pocket_h / 2 + 0.01, f.zq + r.qt_pocket_h / 2 - 0.01)
        self.assertLess(rail.common(room).Volume, 1e-6)
        self.assertGreater(r.rail_d - r.qt_web, 6.0)

    def test_no_value_of_the_joints_has_a_second_copy_here(self) -> None:
        mine = set(rear.Rear.__dataclass_fields__)
        theirs = set(joints.Joint.__dataclass_fields__) | set(joints.OtherJoints.__dataclass_fields__)
        self.assertEqual(mine & theirs, set())


class VentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d, cls.r = Blueprint(), rear.Rear()
        cls.p = rear.place(cls.d)
        cls.f = rear.frame(cls.d, cls.r)
        low = rear.supply_openings(cls.r, cls.p)
        cls.vents = {"fan vent": rear.fan_vent(cls.r, cls.p), "hot vent": rear.hot_vent(cls.r, cls.p), "inlet": rear.inlet(cls.r, cls.p),
                     "supply": [o for v in low.values() for o in v]}
        cls.areas = rear.areas(cls.r, cls.p)

    def test_no_opening_leaves_a_strip_under_2(self) -> None:
        self.assertGreaterEqual(self.r.bar, 2.0)
        for name, faces in self.vents.items():
            for i, a in enumerate(faces):
                for b in faces[i + 1:]:
                    with self.subTest(vent=name):
                        self.assertGreaterEqual(a.distToShape(b)[0], 2.0 - 1e-6)

    def test_the_openings_of_the_lower_wall_print_upright_with_no_support(self) -> None:
        """Over each opening the wall starts at 45 degrees or steeper, but for a bridge of BRIDGE at most. The round
        head of a slot is level over 0.71 of its width."""
        for name in ("inlet", "supply"):
            for face in self.vents[name]:
                level = level_roof(face)
                with self.subTest(vent=name, at=round(face.BoundBox.Center.x, 1)):
                    self.assertLessEqual(level, BRIDGE + 0.1)
                    if face.BoundBox.XLength < self.r.slot + 0.1:
                        self.assertLessEqual(level, 0.72 * self.r.slot)

    def test_the_fan_vent_is_open_enough(self) -> None:
        a = self.areas["fan"]
        self.assertGreaterEqual(a["share"], self.r.fan_open_min)
        self.assertTrue(a["ok"])

    def test_the_fan_vent_lies_on_the_fan(self) -> None:
        x0, x1, z0, z1 = rear.field(self.vents["fan vent"])
        cx, cz, rad = self.p.x(self.p.v["bc_fan_cx"]), self.p.z(self.p.v["bc_fan_cy"]), self.r.fan_vent_d / 2
        self.assertGreaterEqual(x0, cx - rad - 1e-6)
        self.assertLessEqual(x1, cx + rad + 1e-6)
        self.assertAlmostEqual((z0 + z1) / 2, cz, delta=0.01)
        self.assertGreater(x0, self.r.seam_rib_w)

    def test_the_hot_vent_is_inside_the_duct_and_open_enough(self) -> None:
        x0, x1, z0, z1 = rear.field(self.vents["hot vent"])
        dx0, dx1, dz0, dz1 = rear.duct_inside(self.r, self.p)
        self.assertGreaterEqual(min(x0 - dx0, dx1 - x1, z0 - dz0, dz1 - z1), 0.0)
        self.assertGreaterEqual(self.areas["hot"]["free_mm2"], self.r.hot_free_min)

    def test_the_inlet_is_the_mirror_of_the_supply_field_and_open_enough(self) -> None:
        ix0, ix1, iz0, iz1 = rear.field(self.vents["inlet"])
        sx0, sx1, sz0, sz1 = rear.field(self.vents["supply"])
        self.assertAlmostEqual(iz0, sz0, delta=0.5)
        self.assertAlmostEqual(iz1, sz1, delta=0.5)
        self.assertAlmostEqual(ix0, -sx1, delta=1e-6)
        self.assertAlmostEqual(ix1, -sx0, delta=self.r.pitch)
        self.assertEqual(self.r.corner, self.d.rear_round_r)
        need = rear.inlet_need()
        self.assertGreaterEqual(self.areas["inlet"]["free_mm2"], need[1.0])
        self.assertAlmostEqual(need[1.0], structure.makeup_air()["need_cm2"][1.0] * 100, delta=1.0)

    def test_the_structure_data_has_the_inlet_of_the_rear(self) -> None:
        x0, x1, z0, z1 = rear.field(self.vents["inlet"])
        sx0, sx1, _, _, sz0, sz1 = structure.INLET
        for mine, theirs in ((x0, sx0), (x1, sx1), (z0, sz0), (z1, sz1)):
            self.assertAlmostEqual(mine, theirs, delta=0.5)
        gross = (sx1 - sx0) * (sz1 - sz0)
        self.assertAlmostEqual(structure.INLET_OPEN * gross, self.areas["inlet"]["free_mm2"], delta=0.01 * gross)

    def test_the_supply_openings_show_the_socket_the_switches_and_the_screws(self) -> None:
        """The estimates of the research note (bc250-cooling-and-psu.md, Part B), on the supply's rear face."""
        low, p = rear.supply_openings(self.r, self.p), self.p
        at = lambda u, v: V(p.psu_x1 - u, 0, p.psu_z0 + v)
        for u, v in ((88.0, 34.0), (119.0, 57.0), (102.5, 66.0)):
            self.assertTrue(low["socket"][0].isInside(at(u, v), 1e-6, True))
        for u, v in ((128.0, 21.0), (142.0, 55.0)):
            self.assertTrue(low["switch"][0].isInside(at(u, v), 1e-6, True))
        everything = [o for faces in low.values() for o in faces]
        for x, z in rear.supply_screws(self.r, p):
            self.assertGreaterEqual(min(o.distToShape(Part.Vertex(V(x, 0, z)))[0] for o in everything), 4.0)

    def test_no_seam_goes_through_an_opening(self) -> None:
        """Each seam polygon of the body keeps 2 or more from every vent and every opening of the rear."""
        d, f = self.d, self.f
        seams, _ = split.expanded(split.layout(d))
        polys = [split.poly_face(poly) for s in seams if s.module == "body" for poly in s.polys]
        for name, faces in self.vents.items():
            for face in faces:
                solid = rear.through(face, f.y_in, f.y_out)
                with self.subTest(vent=name, at=round(face.BoundBox.Center.x, 1)):
                    self.assertGreaterEqual(min(q.distToShape(solid)[0] for q in polys), 2.0)


class RearPartsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d, cls.r = Blueprint(), rear.Rear()
        cls.p = rear.place(cls.d)
        cls.f = rear.frame(cls.d, cls.r)
        cls.parts = rear.build(cls.d, cls.r, cls.p)
        cls.lim = split.printer(support.PARAMS)

    def test_each_part_is_one_valid_solid(self) -> None:
        for name, shape in self.parts.items():
            with self.subTest(part=name):
                self.assertTrue(shape.isValid())
                self.assertEqual(len(shape.Solids), 2 if name == "fan" else 1)

    def test_the_parts_do_not_run_into_each_other(self) -> None:
        names = list(self.parts)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                with self.subTest(pair=(a, b)):
                    self.assertLess(self.parts[a].common(self.parts[b]).Volume, 1e-3)

    def test_the_two_halves_have_the_same_box(self) -> None:
        a, b = self.parts["door_half_r"].BoundBox, self.parts["door_half_l"].BoundBox
        self.assertAlmostEqual(a.XMax, -b.XMin, places=6)
        self.assertAlmostEqual(a.ZMin, b.ZMin, places=6)
        self.assertAlmostEqual(a.ZMax, b.ZMax, places=6)

    def test_the_door_sits_on_its_land_and_its_foot_hooks_behind_the_lip(self) -> None:
        d, r = self.d, self.r
        for side, s in rear.SIDES.items():
            door = self.parts[f"door_half_{s.lower()}"]
            lip, tongue, rail = rear.sill_lip(d, r, self.p, side), rear.side_tongue(d, r, side), self.parts[f"head_rail_{s.lower()}"]
            with self.subTest(side=s):
                for part in (lip, tongue, rail):
                    self.assertLess(door.common(part).Volume, 1e-3)
                # pulled straight out, the foot runs into the lip, and the cone into its socket
                out = door.translated(V(0, 1.0, 0))
                self.assertGreater(out.common(lip).Volume, 50.0)
                self.assertLess(out.common(tongue).Volume, 1e-3)
                # the cone locates: moved 0.5 in its plane, the door runs into the socket
                self.assertGreater(door.translated(V(0.5, 0, 0)).common(rail).Volume, 0.1)

    def test_the_door_tilts_out_and_lifts_off(self) -> None:
        """The way off: the head tilts out about the foot (the lower inner edge of the door's margin, on the lip),
        with nothing in its way at any angle; with the head out of the opening the door lifts over the lip."""
        d, r, f = self.d, self.r, self.f
        pivot = V(0, f.y_lap, f.zd0)
        for side, s in rear.SIDES.items():
            door = self.parts[f"door_half_{s.lower()}"]
            fixed = [rear.sill_lip(d, r, self.p, side), rear.side_tongue(d, r, side), self.parts[f"head_rail_{s.lower()}"]]
            for angle in (0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0):
                tilted = door.copy()
                tilted.rotate(pivot, V(1, 0, 0), -angle)
                with self.subTest(side=s, angle=angle):
                    self.assertGreater(tilted.BoundBox.YMax, door.BoundBox.YMax)
                    for part in fixed:
                        self.assertLess(tilted.common(part).Volume, 0.05)
            out = door.copy()
            out.rotate(pivot, V(1, 0, 0), -6.0)
            # at 6 degrees the head is 17 behind the wall: the door lifts, and then comes away
            self.assertGreater(out.BoundBox.YMax - f.y_out, 15.0)
            lifted = out.translated(V(0, 0, 3.0))
            for step in (0.0, 2.0, 6.0):
                away = lifted.translated(V(0, step, 0))
                for part in fixed:
                    self.assertLess(away.common(part).Volume, 0.05, (s, step))

    def test_the_door_has_no_sharp_edge_on_the_outside(self) -> None:
        doors = {f"door half {s}": self.parts[f"door_half_{s.lower()}"] for s in rear.SIDES.values()}
        for level, subject, detail in rear.edge_rows(self.d, self.r, doors):
            with self.subTest(part=subject):
                self.assertEqual(level, check.PASS, detail)

    def test_the_face_check_holds_on_the_door_and_the_rails(self) -> None:
        shapes = {k: self.parts[k] for k in ("door_half_r", "door_half_l", "head_rail_r", "head_rail_l")}
        for level, subject, detail in rear.face_rows(self.d, self.r, self.p, shapes):
            with self.subTest(part=subject):
                self.assertEqual(level, check.PASS, detail)

    def test_each_printed_part_fits_and_lies_flat_with_no_overhang(self) -> None:
        rows = {q["part"]: q for q in rear.print_rows(self.parts, self.lim)}
        self.assertEqual(set(rows), set(rear.PRINTS))
        for name, q in rows.items():
            with self.subTest(part=name):
                self.assertTrue(q["fits"])
                self.assertGreater(q["flat_on_bed_cm2"], 1.0)
        for name in ("door_half_r", "door_half_l", "shroud_base", "shroud_top", "duct_back"):
            self.assertLess(rows[name]["overhang_cm2"], 0.6, name)

    def test_the_seals_fill_the_gap_to_the_door(self) -> None:
        for name in ("seal_fan", "seal_duct"):
            self.assertAlmostEqual(self.parts[name].BoundBox.YMax, self.f.y_in, places=6)
        self.assertAlmostEqual(self.parts["seal_fan"].BoundBox.YMin, self.parts["fan"].BoundBox.YMax, places=6)

    def test_the_check_notices_a_sharp_edge(self) -> None:
        plain = rear.box(0, 100, self.f.y_lap, self.f.y_out, self.f.zd0, self.f.zd1)
        rows = rear.edge_rows(self.d, self.r, {"door half R": plain})
        self.assertEqual(rows[0][0], check.FAIL)


class RearInTheFitStudyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d, cls.shapes, _ = support.shell()
        cls.cav = support.cavity()
        cls.fitted = fit.place(cls.d, fit.Layout(), support.PARAMS, cls.shapes, cls.cav)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fitted.close()

    def test_the_fit_study_passes_with_the_real_parts(self) -> None:
        self.assertEqual(self.fitted.failures, [])
        subjects = [s for _, s, _ in self.fitted.rules["rear parts"]]
        for wanted in ("Compute_FanShroud: the real parts", "Compute_ExhaustDuct: the real parts", "board in the clear opening",
                       "fan vent", "hot-air vent", "lead of the power button"):
            self.assertIn(wanted, subjects)

    def test_the_rule_door_service_holds(self) -> None:
        self.assertEqual([r for r in self.fitted.rules["door service"] if r[0] == check.FAIL], [])

    def test_the_study_notices_a_duct_behind_the_land(self) -> None:
        """With the layout of before (the duct 1 inside the opening) the duct stands behind the left post, and the
        rib at the centre line of the door stands in the collar of the fan."""
        old = fit.place(self.d, replace(fit.Layout(), duct_in_door=1.0), support.PARAMS, self.shapes, self.cav)
        try:
            failed = "\n".join(old.failures)
        finally:
            old.close()
        self.assertIn("rear parts: duct_body / side_tongue_l", failed)
        self.assertIn("rear parts: door_half_r / shroud_top", failed)


class RearOnThePiecesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d, cls.r = Blueprint(), rear.Rear()
        cls.p = rear.place(cls.d)
        cls.lim = split.printer(support.PARAMS)
        cls.raw = rear.body_pieces(cls.d, log=lambda *_: None)
        cls.done = rear.finish_pieces(cls.raw, cls.d, cls.r, cls.p)
        cls.changed = {k: v for k, v in cls.done.items() if k.startswith(rear.CHANGED)}

    def test_each_changed_piece_is_one_valid_solid(self) -> None:
        self.assertEqual(len(self.changed), 8)
        for name, shape in self.changed.items():
            with self.subTest(piece=name):
                self.assertTrue(shape.isValid())
                self.assertEqual(len(shape.Solids), 1)

    def test_the_other_pieces_are_as_the_cut_made_them(self) -> None:
        for name, shape in self.done.items():
            if name not in self.changed:
                self.assertTrue(shape.isSame(self.raw[name]), name)

    def test_the_openings_are_cut_and_the_land_is_added(self) -> None:
        r, p, d = self.r, self.p, self.d
        low = rear.supply_openings(r, p)
        took = {"rear lower R": rear.area(rear.inlet(r, p)), "rear lower L": sum(rear.area(v) for v in low.values())}
        side = {"rear lower R": 1, "rear lower L": -1}
        for name, a in took.items():
            less = self.raw[name].Volume - self.done[name].Volume
            added = rear.sill_lip(d, r, p, side[name]).cut(self.raw[name]).Volume  # the lip and the rib under the sill
            with self.subTest(piece=name):
                self.assertGreater(added, 1500.0)
                self.assertAlmostEqual(less, a * d.wall_t - added, delta=0.08 * a * d.wall_t)
        for s in rear.SIDES.values():
            self.assertGreater(self.done[f"middle {s}"].Volume - self.raw[f"middle {s}"].Volume, 9000.0)
            self.assertAlmostEqual(self.raw[f"upper rear {s}"].Volume - self.done[f"upper rear {s}"].Volume,
                                   (1 - math.pi / 4) * d.edge_break ** 2 * d.door_w / 2, delta=1.0)

    def test_no_sharp_edge_on_the_rim_of_the_door_opening_or_of_an_opening(self) -> None:
        for level, subject, detail in rear.edge_rows(self.d, self.r, self.changed):
            with self.subTest(piece=subject):
                self.assertEqual(level, check.PASS, detail)

    def test_the_face_check_holds_on_the_outside_of_the_changed_pieces(self) -> None:
        for level, subject, detail in rear.face_rows(self.d, self.r, self.p, self.changed):
            with self.subTest(piece=subject):
                self.assertEqual(level, check.PASS, detail)

    def test_each_changed_piece_fits_the_printer_and_the_twins_have_one_box(self) -> None:
        up = {q.full: q.up for q in split.expanded(split.layout(self.d))[1]}
        rows = {k: split.measure(v, up[k], self.lim, None, None, self.d, detail=False) for k, v in self.changed.items()}
        for name, q in rows.items():
            with self.subTest(piece=name):
                self.assertTrue(q["fits"])
        self.assertEqual(split.mirror_gaps(rows), [])


if __name__ == "__main__":
    unittest.main()
