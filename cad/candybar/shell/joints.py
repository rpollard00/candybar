"""Joint 1 of the seam proposal (skin to skin on a wall or a curved face): the one definition of its dimensions and
the functions that make it on the edge of a wall.

The numbers come from the joint sheet of the proposal (tools/draw_structure.py, joint_skin, and
cad/out/shell-bp/split/proposal.md, "Joints"); the coupon (candybar.shell.coupon) proves them before the cabinet
is printed. Later part modelling imports Joint and the builders from here, so that every seam and the coupon have
one set of values.

Frame of a seam (the section across it):
  u  the distance inward from the outer face of the skin (u = 0 outside, u = wall_t on the inner face, the flange
     reaches u = wall_t + flange_h);
  z  the distance from the seam plane, positive into the piece ABOVE the seam.
The piece BELOW the seam has its flange at its top edge, with a 45 degree gusset under it, the key on its flange
face and the pilot holes. The piece ABOVE has its flange at its bottom edge (a gusset over it), the groove and the
clearance holes with a pocket for the screw head. In the upright print of the wall pieces the piece below prints
with the seam at its top (the gusset carries the level flange) and the piece above prints with the seam on the bed.

A seam follows a path along the edge: an Arc (a wall curved in plan, the convex side outside) or a Line. Each
builder returns a solid in the frame of the cabinet; the caller fuses or cuts it. No FreeCAD at import.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

P2 = tuple[float, float]
P3 = tuple[float, float, float]


@dataclass(frozen=True)
class Joint:
    """Joint 1, mm and degrees."""
    wall_t: float = 4.0              # skin
    flange_t: float = 6.0            # flange thickness, across the seam (along z)
    flange_h: float = 12.0           # flange height, inward from the inner face of the skin (along u)
    gusset_angle: float = 45.0       # from the wall; at 45 the gusset prints with no support (the printer's limit)
    key_proj: float = 1.5            # the key stands this far out of the flange face (into the groove)
    key_w: float = 4.0               # key width, along the flange height
    key_u0: float = 4.0              # the key starts this far inward of the inner face (proposal: 8 to 12 from outside)
    key_gap: float = 7.0             # the key stops this far each side of a screw axis, so that the holes miss it
    key_end_margin: float = 5.0      # the key stops this far from a free end of the seam
    groove_clearance: float = 0.2    # per side, at the sides and the ends of the key; the coupon sets it (0.1 to 0.3)
    groove_extra_depth: float = 0.5  # the groove is this much deeper than the key: the bridge over it may sag and the
                                     # key must never hold the flange faces apart; the depth does not locate
    groove_chamfer: float = 0.3      # 45 degree chamfer at the groove mouth, against the first-layer squish on the bed
    screw_d: float = 3.0             # thread-forming screw for plastics (30 degree thread, EJOT PT type), 3.0 x 16
    screw_l: float = 16.0
    # Pilot hole: two candidates, and the coupon decides. Source: "Hole Size Recommendations for EJOT Type-PT
    # Alternatives" (EJOT distributor table, https://cdn.shopify.com/s/files/1/0056/7856/3437/files/MetPTholesize.pdf):
    # a 3.0 screw into PET 2.25 (0.75 d), into ABS 2.4 (0.8 d); the EJOT DELTA PT flyer gives 0.8 d1 as the most
    # favourable hole in most cases. PETG is not in the table. Both are ASSUMPTIONS that the coupon tests: each lower
    # half has one of each (the smaller at -30, the larger at +30) and the repeated-drive test compares them.
    pilot_d_pet: float = 2.25        # the table value for PET; nearest to the planned PETG
    pilot_d_abs: float = 2.4         # the table value for ABS
    # The pilot of the cabinet: open until the coupon decides. Part modelling must set it, e.g.
    # replace(JOINT, pilot_d=JOINT.pilot_d_pet); the builders refuse a joint without it (Joint.pilot()).
    pilot_d: float | None = None
    pilot_depth: float = 11.0        # from the seam plane into the piece below: the screw reaches 10, 1 spare
    pilot_counterbore_d: float = 3.2 # EJOT: counterbore 1.05 d1 at the hole mouth, so that no bulge lifts the faces
    pilot_counterbore_depth: float = 0.5
    clearance_d: float = 3.4         # through the flange of the piece above: the screw clamps it, it does not thread
    head_pocket_d: float = 9.0       # through the gusset of the piece above, for the head and a 1/4 inch hex bit
    screw_u: float = 9.0             # screw axis from the outer face (5 inward of the inner face)
    screw_pitch: float = 60.0
    vgroove_w: float = 1.0           # outside, across the seam: half on each piece
    vgroove_d: float = 0.8
    foot_h: float = 12.0             # joint 3 foot flange (wall foot on the floor), used as the print foot
    foot_t: float = 4.0

    def pilot(self) -> float:
        """The pilot hole that the cabinet uses. It is open until the coupon decides between pilot_d_pet and pilot_d_abs."""
        if self.pilot_d is None:
            raise ValueError("Joint.pilot_d is open: the coupon decides between pilot_d_pet and pilot_d_abs; set it with "
                             "dataclasses.replace(JOINT, pilot_d=...)")
        return self.pilot_d

    @property
    def gusset_leg(self) -> float:
        """The gusset meets the flange tip and the wall at gusset_leg from the flange."""
        return self.flange_h / math.tan(math.radians(self.gusset_angle))

    @property
    def key_u(self) -> P2:
        a = self.wall_t + self.key_u0
        return a, a + self.key_w

    def groove_u(self, clearance: float | None = None) -> P2:
        c = self.groove_clearance if clearance is None else clearance
        a, b = self.key_u
        return a - c, b + c

    @property
    def groove_depth(self) -> float:
        return self.key_proj + self.groove_extra_depth


JOINT = Joint()


# ---------- the section across the seam (u, z); "below" and "above" name the piece ----------

def _flip(poly: list[P2], side: str) -> list[P2]:
    return poly if side == "above" else [(u, -z) for u, z in poly]


def skin_profile(j: Joint, side: str, length: float) -> list[P2]:
    """The skin of one piece from the seam plane to its free edge `length` away."""
    return _flip([(0.0, 0.0), (j.wall_t, 0.0), (j.wall_t, length), (0.0, length)], side)


def flange_profile(j: Joint, side: str) -> list[P2]:
    """Flange and gusset as one outline. The gusset reaches 0.5 into the skin so that the fuse has no sliver."""
    w, h, t, g = j.wall_t, j.flange_h, j.flange_t, j.gusset_leg
    return _flip([(w - 0.5, 0.0), (w + h, 0.0), (w + h, t), (w, t + g), (w - 0.5, t + g + 0.5)], side)


def vgroove_profile(j: Joint, side: str) -> list[P2]:
    """The half V on the outer edge of one piece (cut)."""
    e = 0.01
    return _flip([(-e, -e), (j.vgroove_d, -e), (j.vgroove_d, 0.0), (0.0, j.vgroove_w / 2), (-e, j.vgroove_w / 2)], side)


def key_profile(j: Joint) -> list[P2]:
    """The key on the flange face of the piece below; it stands into the piece above (z > 0)."""
    a, b = j.key_u
    return [(a, -0.2), (b, -0.2), (b, j.key_proj), (a, j.key_proj)]


def groove_profile(j: Joint, clearance: float) -> list[P2]:
    """The groove in the flange face of the piece above, with the chamfer at its mouth (cut)."""
    a, b = j.groove_u(clearance)
    k = j.groove_chamfer
    return [(a - k, -0.01), (b + k, -0.01), (b + k, 0.0), (b, k), (b, j.groove_depth), (a, j.groove_depth), (a, k), (a - k, 0.0)]


def foot_profile(j: Joint, length: float) -> list[P2]:
    """Joint 3 foot flange at the free edge of a piece below the seam, `length` under the seam: the print foot."""
    w = j.wall_t
    return [(w - 0.5, -length), (w + j.foot_h, -length), (w + j.foot_h, -length + j.foot_t), (w - 0.5, -length + j.foot_t)]


# ---------- paths along the edge ----------

@dataclass(frozen=True)
class Arc:
    """A seam along a wall curved in plan: the outer face is a cylinder of radius r about the z axis, convex outside.
    s is the arc length on the outer face, from the -y axis toward +x."""
    r: float
    s0: float
    s1: float

    def point(self, s: float, u: float, z: float) -> P3:
        a = s / self.r
        return ((self.r - u) * math.sin(a), -(self.r - u) * math.cos(a), z)

    def inward(self, s: float) -> P3:
        a = s / self.r
        return (-math.sin(a), math.cos(a), 0.0)

    def along(self, ds: float, u: float) -> float:
        """The outer arc length that matches a length ds at depth u."""
        return ds * self.r / (self.r - u)

    def sweep(self, poly: list[P2], s0: float | None = None, s1: float | None = None):
        import FreeCAD as App
        import Part
        s0 = self.s0 if s0 is None else s0
        s1 = self.s1 if s1 is None else s1
        pts = [App.Vector(*self.point(s0, u, z)) for u, z in poly]
        face = Part.Face(Part.makePolygon(pts + [pts[0]]))
        return face.revolve(App.Vector(0, 0, 0), App.Vector(0, 0, 1), math.degrees((s1 - s0) / self.r))


@dataclass(frozen=True)
class Line:
    """A straight seam along +x; the outer face is the plane y = 0 and inward is +y."""
    s0: float
    s1: float

    def point(self, s: float, u: float, z: float) -> P3:
        return (s, u, z)

    def inward(self, s: float) -> P3:
        return (0.0, 1.0, 0.0)

    def along(self, ds: float, u: float) -> float:
        return ds

    def sweep(self, poly: list[P2], s0: float | None = None, s1: float | None = None):
        import FreeCAD as App
        import Part
        s0 = self.s0 if s0 is None else s0
        s1 = self.s1 if s1 is None else s1
        pts = [App.Vector(*self.point(s0, u, z)) for u, z in poly]
        return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(App.Vector(s1 - s0, 0, 0))


Path = Arc | Line


def screw_stations(path: Path, pitch: float) -> list[float]:
    """Screw positions along the path: the nearest whole number of pitches, centred, at least one."""
    n = max(1, round((path.s1 - path.s0) / pitch))
    mid = (path.s0 + path.s1) / 2
    return [mid + (k - (n - 1) / 2) * pitch for k in range(n)]


def key_runs(j: Joint, path: Path, stations: list[float]) -> list[P2]:
    """The runs of the key along the path: from end margin to end margin, stopped each side of every screw.
    The gap is measured at the middle of the key, as a length there."""
    um = sum(j.key_u) / 2
    gap, margin = path.along(j.key_gap, um), path.along(j.key_end_margin, um)
    runs, start = [], path.s0 + margin
    for s in sorted(stations):
        if s - gap > start:
            runs.append((start, s - gap))
        start = s + gap
    if path.s1 - margin > start:
        runs.append((start, path.s1 - margin))
    return runs


# ---------- solids ----------

def _fuse(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.removeSplitter()


def _cylinder(path: Path, s: float, u: float, z0: float, z1: float, d: float):
    import FreeCAD as App
    import Part
    x, y, _ = path.point(s, u, 0.0)
    return Part.makeCylinder(d / 2, z1 - z0, App.Vector(x, y, z0), App.Vector(0, 0, 1))


def key_solids(j: Joint, path: Path, stations: list[float]) -> list:
    return [path.sweep(key_profile(j), a, b) for a, b in key_runs(j, path, stations)]


def groove_cut(j: Joint, path: Path, stations: list[float], clearance: float):
    """The groove: each key run with the clearance added at both ends. On an arc the end faces are radial, so the
    clearance is set where they are nearest, at the inner edge of the key (it grows by 1.4 % to the outer edge)."""
    c = path.along(clearance, j.key_u[1])
    return _fuse([path.sweep(groove_profile(j, clearance), a - c, b + c) for a, b in key_runs(j, path, stations)])


def pilot_cut(j: Joint, path: Path, stations: list[float], pilots: list[float] | None = None):
    """Pilot holes into the piece below, with the counterbore at the mouth. `pilots` gives a diameter for each station
    (the coupon tests two); without it every hole is Joint.pilot()."""
    pilots = pilots or [j.pilot()] * len(stations)
    out = []
    for s, d in zip(stations, pilots, strict=True):
        out.append(_cylinder(path, s, j.screw_u, -j.pilot_depth, 0.01, d))
        out.append(_cylinder(path, s, j.screw_u, -j.pilot_counterbore_depth, 0.01, j.pilot_counterbore_d))
    return _fuse(out)


def clearance_cut(j: Joint, path: Path, stations: list[float], top: float):
    """Clearance holes through the flange of the piece above and the head pockets through its gusset, to `top`."""
    out = []
    for s in stations:
        out.append(_cylinder(path, s, j.screw_u, -0.01, j.flange_t + 0.01, j.clearance_d))
        out.append(_cylinder(path, s, j.screw_u, j.flange_t, top, j.head_pocket_d))
    return _fuse(out)


def seam_edge(j: Joint, path: Path, side: str, stations: list[float], clearance: float | None = None,
              pilots: list[float] | None = None):
    """What one piece needs at the seam: (solid to fuse, solid to cut). Below: flange, gusset and key; pilot holes and
    half the V. Above: flange and gusset; groove, clearance holes, head pockets and half the V."""
    add = [path.sweep(flange_profile(j, side))]
    if side == "below":
        add += key_solids(j, path, stations)
        cut = [pilot_cut(j, path, stations, pilots)]
    else:
        c = j.groove_clearance if clearance is None else clearance
        cut = [groove_cut(j, path, stations, c), clearance_cut(j, path, stations, j.flange_t + j.gusset_leg + 1.0)]
    cut.append(path.sweep(vgroove_profile(j, side), path.s0 - 1.0, path.s1 + 1.0))
    return _fuse(add), _fuse(cut)
