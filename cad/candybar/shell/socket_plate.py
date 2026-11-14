"""The front socket plate: a removable printed plate in the right side face of the deck, with the four USB sockets,
the everyday power button and, as an option, the volume control (docs/design/front-socket-plate.md).

The plate lies where fit.Layout has the four USB sockets: in the upright part of the right side of the deck, between
the front corner of the deck and the seam D2 of the split. It is in the print piece "deck side R". The values are
those of SocketPlate; the arrangements are the entries of VARIANTS, and all of them go into one opening.

    CANDYBAR_OUT=cad/out/socket-plate cad/candybar/freecad-run.sh candybar.shell.socket_plate

writes one folder for each variant into cad/out/socket-plate (BREP, meshes, manifest.json, edges.json, focus.json,
report.json), and report.md with the checks. tools/draw_socket_plate.py makes shell.FCStd, the renders and the
sheets from these folders.

Frame of the plate: s along +y (toward the rear) and t along +z (up) from the centre of the plate on the outer face
of the deck side; depth is the distance inward from that face (-x). Seen from outside, the front of the cabinet is on
the left.

This module changes no shared file. seat() is the cut that solids.deck must make, and fitted() runs the rules of
fit.py on the hardware of the plate in place of fit.usb_row().
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from . import profiles as pr
from .dims import Blueprint

P2 = tuple[float, float]


@dataclass(frozen=True)
class Variant:
    """An arrangement on the plate: the centre of each item along s. The two USB-A sockets are one above the other
    in one column, and the two USB-C sockets in a second column."""
    key: str
    title: str
    button_s: float
    a_s: float
    c_s: float
    knob_s: float | None = None

    @property
    def knob(self) -> bool:
        return self.knob_s is not None


# Layout A: the controls at the two ends. Layout B: the controls together at the front end. Each has a form with
# the knob and a form without it; all four have the same outline, the same opening and the same two plate screws
VARIANTS = (
    Variant("a-knob", "A, with the knob: button at the front end, sockets, knob at the rear end", -48.0, -15.5, 21.1, 48.0),
    Variant("a-plain", "A, no knob: button at the front end, sockets in the middle of the rest", -48.0, -3.6, 33.0),
    Variant("b-knob", "B, with the knob: button and knob together at the front, sockets behind them", -48.5, 6.5, 43.1, -25.0),
    Variant("b-plain", "B, no knob: button apart at the front end, sockets at the rear end", -48.5, 6.5, 43.1),
)
# the audio research (2026-11-14) recommends the volume control beside the power button: layout B with the knob
DEFAULT = "b-knob"


def variant(key: str) -> Variant:
    return next(v for v in VARIANTS if v.key == key)


@dataclass(frozen=True)
class SocketPlate:
    """The values of the plate, its seat in the shell and the hardware on it, mm. Status: SOURCED from
    docs/research/pc-panel-and-front-usb.md (A4, A5) where it says so; every other value is PROVISIONAL (a design
    choice) or ESTIMATED (hardware that is not measured)."""
    # the outline: a level slot with round ends, as the cut-ins and the hand-holds of the rear have. The round ends
    # have the radius of half the height
    length: float = 142.0
    height: float = 33.0
    # None: round ends. A number: a rectangle with corners of this radius, as the service doors below the control
    # panel of the full-size cabinet have (the option "square" on the sheet of the outlines)
    corner_r: float | None = None
    # the plate is as thick as the skin and lies flush in its recess (seat "flush"); the reveal round it is as wide
    # as the reveal of the control panel and of the bezel plate (Blueprint.panel_gap)
    t: float = 4.0
    reveal: float = 1.0
    # its rear end stays this far in front of the seam D2 (split.EXISTING: "ends 5 mm in front of D2")
    d2_gap: float = 5.0
    # behind the sockets and the knob the plate is thinned from the back to a web: the sockets mate fully through
    # 2.5 at most (SOURCED)
    web: float = 2.4
    web_max: float = 2.5
    # the seat. A frame behind the skin, round the opening: frame_t thick, frame_grow wider than the recess, with a
    # facet of 45 degrees on its inner edge so that it prints on the upright piece. The plate rests on a ledge of the
    # frame; the window inside the ledge is window_half long each side of the centre, with corners of window_r
    ledge: float = 2.5
    frame_t: float = 4.0
    frame_grow: float = 3.0
    frame_facet: float = 3.4
    window_half: float = 60.5
    window_r: float = 6.0
    # two screws M3 from the front, on the centre line, screw_end from each end; a heat-set insert in the frame
    screw_end: float = 6.0
    screw_hole_d: float = 3.4
    m3_insert_hole_d: float = 4.0
    plate_screw_d: float = 3.0
    plate_screw_l: float = 8.0
    head_d: float = 5.7      # button head (ISO 7380), for the plate screws and the flange screws: ESTIMATED
    head_h: float = 1.65
    # USB-A socket (DataPro 1698) and USB-C socket (DataPro 1678): cut-out as sourced, with 0.2 added on each side
    # for the print; the two flange holes; the space that the flange needs behind the panel (SOURCED). The body
    # depth and the clear depth are those of params/hardware.csv (ESTIMATED)
    a_cut: tuple[float, float, float] = (15.1, 7.7, 1.8)
    c_cut: tuple[float, float, float] = (10.9, 5.0, 2.5)   # round ends: the sourced radius of 2.0 leaves a flat of 0.6
    a_holes: float = 15.0
    c_holes: float = 10.0
    flange_hole_d: float = 3.4
    a_back: P2 = (39.0, 13.0)
    c_back: P2 = (28.2, 8.7)
    back_margin: float = 1.0
    usb_body_depth: float = 32.0
    usb_clear_depth: float = 60.0
    # the two rows of sockets: their centre lines are row_pitch apart (the flange of 13, and 1 between two flanges)
    row_pitch: float = 14.0
    # the power button: a 16 mm panel button with a lit ring. Hole as printed 16.3; a flat face of 22 round the hole
    # for its rim; 45 clear behind the plate for its body and wires (ESTIMATED until the part is measured)
    button_hole_d: float = 16.3
    button_flat_d: float = 22.0
    button_thread_d: float = 16.0
    button_rim_d: float = 19.0
    button_rim_h: float = 2.0
    button_ring_d: P2 = (10.0, 13.0)   # the lit ring on its face, for the views
    button_body_l: float = 28.0
    button_clear: float = 45.0
    button_nut_d: float = 22.0
    button_nut_h: float = 3.0
    # the volume control: the potentiometer of the amplifier (1 kOhm, three wires that carry no sound; the audio
    # research of 2026-11-14). Hole 9.4, a wall of 2 to 3 at the hole (the web), 20 clear behind the plate, and a
    # flat circle of 22 outside for the knob. Its nut is on the front, under the knob. The knob and the body are ESTIMATED
    knob_hole_d: float = 9.4
    knob_flat_d: float = 22.0
    knob_wall: P2 = (2.0, 3.0)
    knob_bush_d: float = 9.0
    knob_d: float = 18.0
    knob_h: float = 15.0
    knob_body_d: float = 17.0
    knob_body_l: float = 12.0
    knob_clear: float = 20.0
    knob_pocket_d: float = 19.0
    knob_nut_d: float = 12.0
    knob_nut_h: float = 2.0
    # the centre of the plate along y, when it is not at the rear end of the flat (the small plate for the knob)
    y_centre: float | None = None
    # the floor of the cabinet (fit.Layout.floor_t): nothing of the plate's hardware goes below its top
    floor_t: float = 10.0

    # ---------- derived ----------
    def half(self, grow: float = 0.0) -> P2:
        return self.length / 2 + grow, self.height / 2 + grow

    def radius(self, grow: float = 0.0) -> float:
        """The radius of the corners of the outline, grown by grow: half the height for round ends."""
        return (self.height / 2 if self.corner_r is None else self.corner_r) + grow

    def centre(self, d: Blueprint) -> tuple[float, float, float]:
        """The centre of the plate on the outer face of the deck's right side: mid-height of the upright face (from
        the base facet to the crease of the edge section), its rear end d2_gap + reveal in front of D2."""
        y_d2 = d.foot_y - d.bend_t
        y = y_d2 - self.d2_gap - self.reveal - self.length / 2 if self.y_centre is None else self.y_centre
        return d.width / 2, y, (d.base_facet + d.deck_top - d.deck_lean_h) / 2

    def rows(self) -> P2:
        return self.row_pitch / 2, -self.row_pitch / 2

    def screws(self) -> P2:
        return -(self.length / 2 - self.screw_end), self.length / 2 - self.screw_end

    def sockets(self, v: Variant) -> list[tuple[str, str, float, float]]:
        """The four sockets by the names of fit.Layout: (name, kind, s, t). The sockets with the lower number are in
        the upper row."""
        up, low = self.rows()
        return [("USB_A1", "a", v.a_s, up), ("USB_C2", "c", v.c_s, up), ("USB_A3", "a", v.a_s, low), ("USB_C4", "c", v.c_s, low)]

    def back(self, kind: str) -> P2:
        return self.a_back if kind == "a" else self.c_back

    def cut(self, kind: str) -> tuple[float, float, float]:
        return self.a_cut if kind == "a" else self.c_cut

    def holes(self, kind: str) -> float:
        return self.a_holes if kind == "a" else self.c_holes

    def pocket(self, kind: str) -> P2:
        """Half the size of the pocket in the back of the plate for the two flanges of one column."""
        w, h = self.back(kind)
        return w / 2 + self.back_margin, (self.row_pitch + h) / 2 + self.back_margin


def layout_rows(sp: SocketPlate, v: Variant) -> list[dict]:
    """What lies along the centre line of a variant, from the front end to the rear end: each item with the span
    that it needs behind or on the plate, and the gap to the item before it. A negative gap is a clash."""
    a, c = sp.back("a")[0] / 2, sp.back("c")[0] / 2
    items = [("window, front end", -sp.window_half, -sp.window_half),
             ("power button (nut)", v.button_s - sp.button_nut_d / 2, v.button_s + sp.button_nut_d / 2),
             ("USB-A column (flanges)", v.a_s - a, v.a_s + a), ("USB-C column (flanges)", v.c_s - c, v.c_s + c)]
    if v.knob:
        items.append(("knob", v.knob_s - max(sp.knob_d, sp.knob_body_d) / 2, v.knob_s + max(sp.knob_d, sp.knob_body_d) / 2))
    items.append(("window, rear end", sp.window_half, sp.window_half))
    items.sort(key=lambda r: (r[1] + r[2]) / 2)
    return [{"item": n, "from": round(s0, 2), "to": round(s1, 2), "gap": None if i == 0 else round(s0 - items[i - 1][2], 2)}
            for i, (n, s0, s1) in enumerate(items)]


def outside_rows(sp: SocketPlate, v: Variant) -> list[dict]:
    """What lies on the front of the plate along the centre line: the head of each plate screw, the flat face of
    the button and the flat circle of the knob, with the gap to the item before it."""
    items = [("plate screw, front", sp.screws()[0] - sp.head_d / 2, sp.screws()[0] + sp.head_d / 2),
             ("flat face of the button", v.button_s - sp.button_flat_d / 2, v.button_s + sp.button_flat_d / 2),
             ("plate screw, rear", sp.screws()[1] - sp.head_d / 2, sp.screws()[1] + sp.head_d / 2)]
    if v.knob:
        items.append(("flat circle of the knob", v.knob_s - sp.knob_flat_d / 2, v.knob_s + sp.knob_flat_d / 2))
    items.sort(key=lambda r: r[1])
    return [{"item": n, "from": round(s0, 2), "to": round(s1, 2), "gap": None if i == 0 else round(s0 - items[i - 1][2], 2)}
            for i, (n, s0, s1) in enumerate(items)]


def flat_face(sp: SocketPlate, d: Blueprint) -> dict:
    """The flat part of the deck's side face, as the form has it, and what one row of all the hardware needs."""
    y0, y1 = pr.deck_plan(d)[0].q[1], d.foot_y - d.bend_t
    z0, z1 = d.base_facet, d.deck_top - d.deck_lean_h
    land = 2.0 + d.edge_break  # a strip of face narrower than 2 beside the edge break is a sliver
    row = 2 * sp.a_back[0] + 2 * sp.c_back[0]
    return {"y": [round(y0, 1), round(y1, 1)], "length": round(y1 - y0, 1), "z": [z0, z1], "height": z1 - z0,
            "longest_recess": round(y1 - sp.d2_gap - y0 - land, 1), "longest_plate": round(y1 - sp.d2_gap - y0 - land - 2 * sp.reveal, 1),
            "one_row_flanges": round(row, 1), "one_row_all": round(row + sp.button_flat_d + sp.knob_flat_d + 2 * 2 * sp.screw_end + 5 * 2.0, 1),
            "one_row_sockets_only": round(row + 2 * 2 * sp.screw_end + 3 * 2.0, 1), "plate": sp.length}


def moves(sp: SocketPlate, d: Blueprint, v: Variant, was: dict[str, P2]) -> list[dict]:
    """How far each socket stands from its place in fit.Layout: was = {name: (y, z)}."""
    _, yc, zc = sp.centre(d)
    out = []
    for name, _, s, t in sp.sockets(v):
        y, z = yc + s, zc + t
        out.append({"socket": name, "was": [round(c, 1) for c in was[name]], "is": [round(y, 1), round(z, 1)],
                    "dy": round(y - was[name][0], 1), "dz": round(z - was[name][1], 1)})
    return out


def seam_distances(sp: SocketPlate, d: Blueprint) -> dict[str, float]:
    """The distances from the rim of the recess to the lines of the form and to the seams of the split round the
    piece "deck side R", mm. The front corner of the deck starts where the side is no longer flat."""
    from . import split  # noqa: PLC0415

    hw, yc, zc = sp.centre(d)
    a, b = sp.half(sp.reveal)
    L = split.lines(d)
    (cx, cy), (kx, ky) = L.flank
    # the seam F1/F2 on the deck front: the nearest point of the recess is its front end
    flank_x = cx + (kx - cx) * ((yc - a) - cy) / (ky - cy)
    return {"seam D2 (deck to body), behind the recess": round(L.y_foot - (yc + a), 2),
            "start of the deck's front corner, in front of the recess": round((yc - a) - pr.deck_plan(d)[0].q[1], 2),
            "crease of the edge section, above the recess": round(L.z_crease - (zc + b), 2),
            "edge of the base facet, below the recess": round((zc - b) - d.base_facet, 2),
            "seam F1 / F2 (flank break of the deck front), across the deck": round(hw - flank_x, 1),
            "seam D1 (under the control panel), across the deck": round(hw - L.x_jog, 1),
            "floor seam BA2 (y 194), which crosses under the plate": round(194.0 - (yc - a), 1)}


# ---------- the solids, under FreeCAD ----------

def _v(*c: float):
    import FreeCAD  # noqa: PLC0415

    return FreeCAD.Vector(*c)


class Frame:
    """The frame of the plate in the cabinet: at(s, t, depth)."""

    def __init__(self, sp: SocketPlate, d: Blueprint, out: float = 0.0) -> None:
        self.x, self.y, self.z = sp.centre(d)
        self.x += out

    def at(self, s: float, t: float, depth: float = 0.0):
        return _v(self.x - depth, self.y + s, self.z + t)

    def rounded(self, a: float, b: float, r: float, depth: float, s0: float = 0.0, t0: float = 0.0):
        """A rectangle of 2a x 2b with corners of r, about (s0, t0), as a wire in the plane at depth. Lines and arcs
        of circles only."""
        import Part  # noqa: PLC0415

        r = min(r, a, b)
        if r < 1e-9:
            pts = [self.at(s0 + qs * a, t0 + qt * b, depth) for qs, qt in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
            return Part.makePolygon(pts + [pts[0]])
        quads = ((1, 1), (-1, 1), (-1, -1), (1, -1))
        centre = lambda k: (s0 + quads[k % 4][0] * (a - r), t0 + quads[k % 4][1] * (b - r))
        on = lambda c, ang: self.at(c[0] + r * math.cos(ang), c[1] + r * math.sin(ang), depth)
        # the four corner arcs; two arcs with one centre (a round end) are one arc, so that the end is one face
        arcs = [[centre(k), k * math.pi / 2, (k + 1) * math.pi / 2] for k in range(4)]
        first = 1 if math.dist(arcs[3][0], arcs[0][0]) < 1e-9 else 0
        arcs = arcs[first:] + [[c, a0 + 2 * math.pi, a1 + 2 * math.pi] for c, a0, a1 in arcs[:first]]
        merged = [arcs[0]]
        for c, a0, a1 in arcs[1:]:
            if math.dist(c, merged[-1][0]) < 1e-9:
                merged[-1][2] = a1
            else:
                merged.append([c, a0, a1])
        edges = []
        for i, (c, a0, a1) in enumerate(merged):
            edges.append(Part.Arc(on(c, a0), on(c, (a0 + a1) / 2), on(c, a1)).toShape())
            nc, na0, _ = merged[(i + 1) % len(merged)]
            p0, p1 = on(c, a1), on(nc, na0)
            if (p1 - p0).Length > 1e-9:
                edges.append(Part.makeLine(p0, p1))
        return Part.Wire(edges)

    def prism(self, a: float, b: float, r: float, d0: float, d1: float, s0: float = 0.0, t0: float = 0.0):
        """The rounded rectangle made solid from depth d0 to depth d1 (d1 > d0)."""
        import Part  # noqa: PLC0415

        return Part.Face(self.rounded(a, b, r, d1, s0, t0)).extrude(_v(d1 - d0, 0, 0))

    def rod(self, dia: float, d0: float, d1: float, s: float, t: float = 0.0):
        """A cylinder along the depth, from depth d0 to depth d1."""
        import Part  # noqa: PLC0415

        return Part.makeCylinder(dia / 2, d1 - d0, self.at(s, t, d1), _v(1, 0, 0))


OVER = 1.0  # a cutter stands this far out of the face that it cuts through


def plate(sp: SocketPlate, d: Blueprint, v: Variant, out: float = 0.0):
    """The plate of a variant in place (or `out` farther out along +x), with its holes, the pockets in its back and
    the edge break on the rims that show: the outer rim of the front, and the rims of the socket openings. The rims
    of the round holes lie under the button, the nut of the knob and the screw heads."""
    fr = Frame(sp, d, out)
    a, b = sp.half()
    solid = fr.prism(a, b, sp.radius(), 0.0, sp.t)
    cuts = [fr.rod(sp.button_hole_d, -OVER, sp.t + OVER, v.button_s)]
    cuts += [fr.rod(sp.screw_hole_d, -OVER, sp.t + OVER, s) for s in sp.screws()]
    if v.knob:
        cuts += [fr.rod(sp.knob_hole_d, -OVER, sp.t + OVER, v.knob_s), fr.rod(sp.knob_pocket_d, sp.web, sp.t + OVER, v.knob_s)]
    for kind, s in (("a", v.a_s), ("c", v.c_s)):
        pa, pb = sp.pocket(kind)
        cuts.append(fr.prism(pa, pb, 1.0, sp.web, sp.t + OVER, s))
    for _, kind, s, t in sp.sockets(v):
        w, h, r = sp.cut(kind)
        cuts.append(fr.prism(w / 2, h / 2, r, -OVER, sp.t + OVER, s, t))
        cuts += [fr.rod(sp.flange_hole_d, -OVER, sp.t + OVER, s + k * sp.holes(kind), t) for k in (-1, 1)]
    solid = solid.cut(cuts).removeSplitter()
    return break_front(solid, fr.x, d.edge_break, lambda e: not is_hole(e))


def is_circle(e) -> bool:
    import Part  # noqa: PLC0415

    return isinstance(e.Curve, Part.Circle)


def is_hole(e) -> bool:
    """The rim of a round hole: a full circle."""
    return is_circle(e) and abs(abs(e.LastParameter - e.FirstParameter) - 2 * math.pi) < 1e-6


def break_front(solid, x_face: float, r: float, keep=lambda e: True):
    """The edge break on the edges of a solid that lie in the plane x = x_face and for which keep(edge) holds."""
    edges = [e for e in solid.Edges if all(abs(p.X - x_face) < 1e-6 for p in e.Vertexes) and abs(e.BoundBox.XLength) < 1e-6 and keep(e)]
    if not edges:
        raise RuntimeError("socket plate: no edge on the front face for the edge break")
    out = solid.makeFillet(r, edges)
    if not out.isValid() or len(out.Solids) != 1:
        raise RuntimeError("socket plate: the edge break did not make one valid solid")
    return out.Solids[0]


SEATS = ("flush", "proud")


def cutter(sp: SocketPlate, d: Blueprint, seat: str = "flush", deep: float | None = None):
    """What the opening takes out of the shell: the recess of the plate (the outline of the plate grown by the
    reveal, as deep as the plate), the window inside the ledge (through the skin and the frame) and the two holes
    for the inserts. With the seat "proud" the plate lies on the face of the deck: no recess. `deep` is how far in the
    window goes: through the skin and the frame, or farther for the solid outer form, which has no cavity."""
    fr = Frame(sp, d)
    a, b = sp.half(sp.reveal)
    wb = sp.height / 2 - sp.ledge
    deep = deep or d.wall_t + sp.frame_t + OVER
    tools = [fr.prism(sp.window_half, wb, sp.window_r, -OVER, deep)]
    tools += [fr.rod(sp.m3_insert_hole_d, -OVER if seat == "proud" else sp.t - OVER, deep, s) for s in sp.screws()]
    if seat == "flush":
        tools.append(fr.prism(a, b, sp.radius(sp.reveal), -OVER, sp.t))
    out = tools[0].fuse(tools[1:]).removeSplitter()
    return out


def frame(sp: SocketPlate, d: Blueprint, seat: str = "flush"):
    """The frame that the shell gets behind the skin, round the opening: the ledge of the plate and the bosses of
    the two inserts. It starts inside the skin (the inner face of the skin stands in steps of cavity.SLAB), and its
    inner edge has a facet of 45 degrees all round."""
    fr = Frame(sp, d)
    a, b = sp.half(sp.reveal + sp.frame_grow)
    d0 = sp.t if seat == "flush" else d.wall_t - OVER
    body = fr.prism(a, b, sp.radius(sp.reveal + sp.frame_grow), d0, d.wall_t + sp.frame_t)
    x_in = fr.x - d.wall_t - sp.frame_t
    rim = [e for e in body.Edges if all(abs(p.X - x_in) < 1e-6 for p in e.Vertexes) and abs(e.BoundBox.XLength) < 1e-6]
    body = body.makeChamfer(sp.frame_facet, rim)
    return body.cut(cutter(sp, d, seat))


def seat(shape, sp: SocketPlate, d: Blueprint, seat: str = "flush", hollow: bool = True, deep: float | None = None):
    """The shell part (the deck, the fused skin, or the print piece "deck side R") with the seat of the plate: the
    frame added behind the skin when the part is hollow, the opening cut, and the edge break on the rim of the
    opening on the outer face. This is the step that the build of the deck must get. A solid part (hollow False)
    gets no frame; `deep` then makes the window a pocket of that depth, so that the hardware behind the plate shows."""
    fr = Frame(sp, d)
    out = shape.fuse(frame(sp, d, seat)) if hollow else shape
    out = out.cut(cutter(sp, d, seat, deep))
    if seat != "flush":  # the plate covers the rim of the window
        return out
    a, b = sp.half(sp.reveal + OVER)
    rim = [e for e in out.Edges if all(abs(p.X - fr.x) < 1e-6 for p in e.Vertexes) and abs(e.BoundBox.XLength) < 1e-6
           and abs(e.BoundBox.Center.y - fr.y) < a and abs(e.BoundBox.Center.z - fr.z) < b and e.BoundBox.YLength < 2 * a]
    if not rim:
        raise RuntimeError("socket plate: the opening has no rim on the outer face")
    return out.makeFillet(d.edge_break, rim)


def hardware(sp: SocketPlate, d: Blueprint, v: Variant, out: float = 0.0) -> dict:
    """The hardware of a variant as solids, for the views and for the edge check: each socket (its flange in the
    pocket, its body, and the room of its cable bend), the button, the knob, and the screw heads."""
    fr = Frame(sp, d, out)
    box = lambda w, h, d0, d1, s, t: fr.prism(w / 2, h / 2, 0.0, d0, d1, s, t)
    parts: dict = {}
    for name, kind, s, t in sp.sockets(v):
        w, h = sp.back(kind)
        cw, ch, cr = sp.cut(kind)
        mouth = fr.prism(cw / 2 - 0.2, ch / 2 - 0.2, cr - 0.2, sp.web + 0.5, sp.web + 8.0, s, t)
        parts[name] = box(w, h, sp.web, sp.web + sp.usb_body_depth, s, t).cut(mouth)
        parts[f"{name}_bend"] = box(w, h, sp.web + sp.usb_body_depth, sp.web + sp.usb_clear_depth, s, t)
        for k in (-1, 1):
            parts[f"{name}_screw{'ab'[k > 0]}"] = fr.rod(sp.head_d, -sp.head_h, 0.0, s + k * sp.holes(kind), t).fuse(
                fr.rod(sp.plate_screw_d, 0.0, sp.web, s + k * sp.holes(kind), t))
    button = [fr.rod(sp.button_rim_d, -sp.button_rim_h, 0.0, v.button_s), fr.rod(sp.button_thread_d, 0.0, sp.t + sp.button_body_l, v.button_s),
              fr.rod(sp.button_nut_d, sp.t, sp.t + sp.button_nut_h, v.button_s)]
    parts["power_button"] = button[0].fuse(button[1:]).removeSplitter()
    ring = fr.rod(sp.button_ring_d[1], -sp.button_rim_h - 0.2, -sp.button_rim_h, v.button_s).cut(
        fr.rod(sp.button_ring_d[0], -sp.button_rim_h - 1.0, 0.0, v.button_s))
    parts["power_button_ring"] = ring
    parts["power_button_room"] = fr.rod(sp.button_nut_d, sp.t + sp.button_body_l, sp.t + sp.button_clear, v.button_s)
    if v.knob:
        parts["knob"] = knob_solid(fr, sp, v.knob_s)
        parts["knob_room"] = fr.rod(sp.knob_body_d, sp.web + sp.knob_body_l, sp.t + sp.knob_clear, v.knob_s)
    for k, s in enumerate(sp.screws()):
        parts[f"plate_screw{'ab'[k]}"] = fr.rod(sp.head_d, -sp.head_h, 0.0, s).fuse(fr.rod(sp.plate_screw_d, 0.0, sp.plate_screw_l, s))
    return parts


def knob_solid(fr: Frame, sp: SocketPlate, s: float):
    knob = [fr.rod(sp.knob_d, -sp.knob_h - sp.knob_nut_h, -sp.knob_nut_h, s), fr.rod(sp.knob_nut_d, -sp.knob_nut_h, 0.0, s),
            fr.rod(sp.knob_bush_d, 0.0, sp.web, s), fr.rod(sp.knob_body_d, sp.web, sp.web + sp.knob_body_l, s)]
    return knob[0].fuse(knob[1:]).removeSplitter()


# the alternative of the audio research: a second, small plate in the LEFT side of the deck for the knob alone. It has
# the height, the round ends, the seat and the two screws of the socket plate, and lies at the front end of the flat,
# opposite the front end of the socket plate. It is built on the right side and mirrored
KNOB_PLATE_LENGTH = 50.0
KNOB_PLATE_WINDOW = 14.0


def knob_plate_values(sp: SocketPlate, d: Blueprint) -> SocketPlate:
    _, yc, _ = sp.centre(d)
    return replace(sp, length=KNOB_PLATE_LENGTH, window_half=KNOB_PLATE_WINDOW, y_centre=yc - sp.length / 2 + KNOB_PLATE_LENGTH / 2)


def knob_plate(kp: SocketPlate, d: Blueprint):
    """The small plate for the knob alone, on the right side (mirror it for the left side)."""
    fr = Frame(kp, d)
    a, b = kp.half()
    cuts = [fr.rod(kp.knob_hole_d, -OVER, kp.t + OVER, 0.0), fr.rod(kp.knob_pocket_d, kp.web, kp.t + OVER, 0.0)]
    cuts += [fr.rod(kp.screw_hole_d, -OVER, kp.t + OVER, s) for s in kp.screws()]
    solid = fr.prism(a, b, kp.radius(), 0.0, kp.t).cut(cuts).removeSplitter()
    return break_front(solid, fr.x, d.edge_break, lambda e: not is_hole(e))


def knob_plate_hardware(kp: SocketPlate, d: Blueprint) -> dict:
    fr = Frame(kp, d)
    out = {"knob": knob_solid(fr, kp, 0.0)}
    for k, s in enumerate(kp.screws()):
        out[f"plate_screw{'ab'[k]}"] = fr.rod(kp.head_d, -kp.head_h, 0.0, s).fuse(fr.rod(kp.plate_screw_d, 0.0, kp.plate_screw_l, s))
    return out


def left(shape):
    """A shape of the right side as its mirror image on the left side."""
    return shape.mirror(_v(0, 0, 0), _v(1, 0, 0))


ROOM = ("_bend", "_room")


def is_room(name: str) -> bool:
    return name.endswith(ROOM)


SHELL_PARTS = ("deck", "control_panel", "body", "hood", "marquee_lip", "speaker_right", "speaker_left", "logo_form", "bezel", "screen")


def shell_parts(d: Blueprint, built: str | None = None) -> dict:
    """The parts of the outer form: a new build of solids.py, or the BREP files of a build in the folder `built`."""
    import Part  # noqa: PLC0415

    from . import solids as so  # noqa: PLC0415

    if not built:
        return so.build(d)
    out = {}
    for k in SHELL_PARTS:
        out[k] = Part.Shape()
        out[k].read(os.path.join(built, f"{k}.brep"))
        out[k] = out[k].Solids[0] if len(out[k].Solids) == 1 else out[k]
    return out


# ---------- the rules of the fit study, with the hardware of the plate ----------

def assemblies(sp: SocketPlate, d: Blueprint, v: Variant) -> list:
    """The hardware of the plate as the fit study reads it: each socket, the button and the knob as an item with a
    body (hardware), the room behind it (keep-out zone), and what stands outside the shell (protrusion). The frame
    of each assembly is the frame of the plate: local x is t, local y is s, local z is the depth."""
    from ..model import Assembly, Pose, Y_AXIS, box, cyl  # noqa: PLC0415

    x, y, z = sp.centre(d)
    mm = lambda value: f"{value:.4f} mm"
    at = lambda s, t, depth: (mm(t), mm(s), mm(depth))
    pose = Pose(Y_AXIS, -90.0)
    out = []
    for name, kind, s, t in sp.sockets(v):
        w, h = sp.back(kind)
        size = lambda depth: (mm(h), mm(w), mm(depth))
        out.append(Assembly(name, base=(mm(x), mm(y), mm(z)), pose=pose, prims=(
            box(f"{name}_Body", "hardware", size(sp.usb_body_depth), at(s - w / 2, t - h / 2, sp.web)),
            box(f"{name}_Bend", "keepout", size(sp.usb_clear_depth - sp.usb_body_depth), at(s - w / 2, t - h / 2, sp.web + sp.usb_body_depth)))))
    s = v.button_s
    out.append(Assembly("PowerButton", base=(mm(x), mm(y), mm(z)), pose=pose, prims=(
        cyl("PowerButton_Rim", "protrusion", mm(sp.button_rim_d), mm(sp.button_rim_h + sp.t), at(s, 0.0, -sp.button_rim_h)),
        cyl("PowerButton_Nut", "hardware", mm(sp.button_nut_d), mm(sp.button_nut_h), at(s, 0.0, sp.t)),
        cyl("PowerButton_Body", "hardware", mm(sp.button_thread_d), mm(sp.button_body_l), at(s, 0.0, sp.t)),
        cyl("PowerButton_Wires", "keepout", mm(sp.button_nut_d), mm(sp.button_clear - sp.button_body_l), at(s, 0.0, sp.t + sp.button_body_l)))))
    if v.knob:
        s = v.knob_s
        out.append(Assembly("VolumeKnob", base=(mm(x), mm(y), mm(z)), pose=pose, prims=(
            cyl("VolumeKnob_Knob", "protrusion", mm(sp.knob_d), mm(sp.knob_h + sp.knob_nut_h), at(s, 0.0, -sp.knob_h - sp.knob_nut_h)),
            cyl("VolumeKnob_Body", "hardware", mm(sp.knob_body_d), mm(sp.knob_body_l), at(s, 0.0, sp.web)),
            cyl("VolumeKnob_Wires", "keepout", mm(sp.knob_body_d), mm(sp.t + sp.knob_clear - sp.web - sp.knob_body_l), at(s, 0.0, sp.web + sp.knob_body_l)))))
    return out


OWNERS = ("USB_", "PowerButton", "VolumeKnob")


def opened(cav, sp: SocketPlate, d: Blueprint, v: Variant):
    """The cavity with the opening of the plate: the opening is room, the skin has the cut, and the frame and the
    plate are walls that the hardware must keep out of."""
    from . import cavity  # noqa: PLC0415

    cut = cutter(sp, d)
    walls = [w.cut(cut) if w.BoundBox.intersect(cut.BoundBox) else w for w in cav.walls]
    return cavity.Cavity(cav.pieces + [cut], walls + [frame(sp, d), plate(sp, d, v)], cav.slabs)


def fit_values(d: Blueprint, params_dir: Path, parts: dict, cav) -> dict:
    """The anchors of the hardware of fit.py in the cavity, as fit.place makes them: the same for every variant of
    the plate."""
    import FreeCAD as App  # noqa: PLC0415

    from .. import params  # noqa: PLC0415
    from . import fit  # noqa: PLC0415

    lay = fit.Layout()
    h = pr.hood(d)
    base = fit.sheet(params.load(params_dir), "SocketPlateBase")
    pv = lambda name: params.value(base, name)
    half = d.width / 2
    side_in = half - fit.ray_wall(parts, cav, _v(half + fit.RAY, fit.usb_row_start(d, lay, pv), fit.usb_row_z(d)), _v(-1, 0, 0))
    values = fit.anchors(d, lay, pv, side_in)
    _, marquee = fit.marquee_box(d, h, pv("mq_led_depth"))
    values.update({k: marquee[k] for k in ("fit_mq_w", "fit_mq_h", "fit_mq_y", "fit_mq_z0")}, **fit.speaker_room(d, lay, h, cav.walls, pv("mq_led_depth")))
    values["_side_in"] = side_in
    values["_usb_pitch"] = pv("usb_pitch")
    App.closeDocument(base.Name)
    return values


def fitted(sp: SocketPlate, d: Blueprint, v: Variant, params_dir: Path, parts: dict, cav, values: dict | None = None) -> dict:
    """The rules of the fit study (R1, R2, R5, containment in the cavity, the air zones, the door service) on the
    hardware of fit.py with the hardware of the plate in place of fit.usb_row(). fit.py is not changed: this builds
    the same items from its own functions. Returns the rules, and for each item of the plate its gap to the skin
    and the frame, and to its nearest neighbour. `values` is fit_values(), when the caller
    has it."""
    import FreeCAD as App  # noqa: PLC0415

    from .. import check, hardware as hw, model, params  # noqa: PLC0415
    from . import fit  # noqa: PLC0415

    lay = fit.Layout()
    values = dict(values or fit_values(d, params_dir, parts, cav))
    side_in, pitch = values.pop("_side_in"), values.pop("_usb_pitch")
    rows = fit.sheet_rows(params_dir, values)
    doc = fit.sheet(rows, "SocketPlateFit")
    m = model.Model(doc, [r.name for r in rows])
    count = int(params.value(doc, "btn_count"))
    for spec in (hw.MONITOR, fit.MONITOR_ANY, fit.MONITOR_CABLES, hw.COMPUTE, hw.PSU, hw.CABLE_BUNDLE, fit.control_panel(count),
                 *assemblies(sp, d, v), fit.HUB, *fit.speakers(), fit.MARQUEE):
        m.assembly(spec)
    doc.recompute()
    found = fit.items(doc)
    open_cav = opened(cav, sp, d, v)
    rules = fit.run_checks(doc, found, open_cav, parts["bezel"], parts["control_panel"])
    rules["door service"] = fit.door_service(found, fit.door_outline(d), d, lay)
    mine = [it for it in found if it.owner.startswith(OWNERS)]
    table = []
    shell_walls = open_cav.walls[:-1]  # the skin and the frame; the hardware lies against the plate
    for it in mine:
        skin = fit.gap(it.shape(fit.ENVELOPE), shell_walls, d.width)
        others = [(o.name, fit.gap(it.body, [o.body], d.width)) for o in found if o.owner != it.owner]
        name, near = min(others, key=lambda r: r[1][0])
        low = min(s.world.BoundBox.ZMin for s in it.solids if s.role in fit.ENVELOPE)
        table.append({"item": it.name, "skin_gap": round(skin[0], 2), "neighbour": name, "neighbour_gap": round(near[0], 2),
                      "above_floor": round(low - sp.floor_t, 2)})
    hub = next(it for it in found if it.name == "Hub").body.BoundBox
    fails = [f"{title}: {subject}: {detail}" for title, rs in rules.items() for level, subject, detail in rs if level == check.FAIL]
    out = {"rules": {k: [list(r) for r in rs] for k, rs in rules.items()}, "failures": fails, "items": table,
           "old_row": {f"USB_{kind}{k + 1}": (values["fit_usb_y0"] + k * pitch, values["fit_usb_z"]) for k, kind in enumerate(fit.USB_ORDER)},
           "side_in": round(side_in, 2), "hub": [round(c, 1) for c in (hub.XMin, hub.YMin, hub.ZMin, hub.XMax, hub.YMax, hub.ZMax)]}
    App.closeDocument(doc.Name)
    return out


# ---------- the edge finish and the faces ----------

COVER = 0.35  # an edge lies under a part when its middle is this near to the part


def sharp(shape, d: Blueprint):
    """The convex edges of a shape that turn more than edge_break_turn and have no round."""
    import Part  # noqa: PLC0415

    from . import solids as so  # noqa: PLC0415

    out = []
    for e in shape.Edges:
        if e.Degenerated or len(shape.ancestorsOfType(e, Part.Face)) != 2:
            continue
        convex, turn = so.edge_turn(shape, e)
        if convex and turn > d.edge_break_turn:
            out.append((e, turn))
    return out


def covered(e, covers: dict) -> str:
    import Part  # noqa: PLC0415

    from . import solids as so  # noqa: PLC0415

    m = Part.Vertex(so.middle(e))
    return next((k for k, s in covers.items() if s.distToShape(m)[0] < COVER), "")


def edge_finish(sp: SocketPlate, d: Blueprint, v: Variant, deck_seated, seat_kind: str = "flush") -> dict:
    """The edge rule (decision record 0007) on the plate and on the seat: every sharp convex edge, by where it is.
      shows      on the front of the plate (in front of the back of the web) or on the outer face of the deck, and
                 under no part: this is a failure
      under X    its middle lies under the part X (the rim of a round hole under the button, a nut or a screw head;
                 the edges of the seat under the plate)
      back       on the back of the plate, or on the seat behind the back of the plate: inside the shell, not painted
    """
    from . import solids as so  # noqa: PLC0415

    fr = Frame(sp, d)
    out_by = sp.t if seat_kind == "proud" else 0.0
    pl = plate(sp, d, v, out_by)
    hw = {k: s for k, s in hardware(sp, d, v, out_by).items() if not is_room(k)}
    rows = {"socket_plate": {"shows": [], "under": {}, "back": 0}, "deck": {"shows": [], "under": {}, "back": 0}}
    for e, turn in sharp(pl, d):
        m = so.middle(e)
        if m.x < fr.x + out_by - sp.web + 1e-3:
            rows["socket_plate"]["back"] += 1
        elif (c := covered(e, hw | {"deck": deck_seated})):
            rows["socket_plate"]["under"][c] = rows["socket_plate"]["under"].get(c, 0) + 1
        else:
            rows["socket_plate"]["shows"].append([round(e.Length, 1), round(turn, 1), [round(c, 1) for c in m]])
    a, b = sp.half(sp.reveal + sp.frame_grow)
    for e, turn in sharp(deck_seated, d):
        m = so.middle(e)
        if abs(m.y - fr.y) > a or abs(m.z - fr.z) > b or m.x < fr.x - d.wall_t - sp.frame_t - 2 * OVER:
            continue
        if m.x < fr.x - sp.t + 1e-3 and seat_kind == "flush":  # on the ledge or deeper: behind the back of the plate
            rows["deck"]["back"] += 1
        elif (c := covered(e, {"socket_plate": pl} | hw)):
            rows["deck"]["under"][c] = rows["deck"]["under"].get(c, 0) + 1
        else:
            rows["deck"]["shows"].append([round(e.Length, 1), round(turn, 1), [round(c, 1) for c in m]])
    return rows


def face_rows(sp: SocketPlate, d: Blueprint, v: Variant, deck_seated) -> dict:
    """The face check of tools/face_check.py on the plate and on the deck with the seat. Two named places are narrow
    by design and are listed as allowed: the walls of the socket openings (the web is 2.4, less its edge break) and
    the pockets in the back of the plate (1.6 deep); and the wall of the recess in the reveal."""
    from tools import face_check  # noqa: PLC0415

    x, y, z = sp.centre(d)
    a, b = sp.half(sp.reveal + 0.5)
    box = (x - sp.t - 0.5, y - a, z - b, x + 0.5, y + a, z + b)
    # behind the edge break of the front only: a narrow face on the front of the plate is not allowed by this
    inside = (box[0], box[1], box[2], x - d.edge_break + 0.05, box[4], box[5])
    allow = face_check.default_reveals() + [
        face_check.Reveal("socket openings and back pockets of the plate", ("socket_plate",), ("sliver",), inside)]
    out = {}
    for name, shape in (("socket_plate", plate(sp, d, v)), ("deck", deck_seated)):
        found = face_check.check(shape, name, allow, break_radius=d.edge_break)
        face_check.mark_known(found)
        near = [f for f in found if box[1] - 5 <= f.at[1] <= box[4] + 5 and f.at[2] <= box[5] + 5 and f.at[0] > 0] if name == "deck" else found
        out[name] = {"fail": [[f.rule, list(f.at), f.detail] for f in face_check.failures(near)],
                     "allowed": sorted({f"{f.rule}: {f.allowed}" for f in near if f.allowed and f.rule not in face_check.INFO}),
                     "allowed_count": sum(1 for f in near if f.allowed and f.rule not in face_check.INFO),
                     "faces": len(shape.Faces)}
    return out


# ---------- the print ----------

def print_rows(sp: SocketPlate, d: Blueprint, v: Variant, piece=None) -> dict:
    """The print orientation of the plate and of the piece "deck side R" with the seat, with the faces that face
    down more than 45 degrees."""
    from . import split  # noqa: PLC0415

    lim = split.printer()
    pl = plate(sp, d, v)
    pts = [(p.X, p.Y, p.Z) for p in pl.Vertexes]
    a, b = sp.half()
    rim = d.edge_break
    rows = {"socket_plate": {"up": [-1.0, 0.0, 0.0], "bed": "front face on the bed", "box": split.print_box(pts, (-1.0, 0.0, 0.0), lim),
                             "underside": f"the front face: flat over {2 * (a - rim):.0f} x {2 * (b - rim):.0f}, with the edge break of R {rim:g} round it",
                             "support": "none: the pockets are open to the top, the holes are upright"}}
    wb = sp.height / 2 - sp.ledge
    r = sp.radius(sp.reveal)
    level = sp.length + 2 * sp.reveal - 2 * r
    roof = level * sp.t  # the straight top of the recess; each round corner faces down more than 45 degrees over 45 degrees of arc
    arc = 2 * (math.pi / 4) * r * sp.t
    rows["deck side R"] = {"up": [0.0, 0.0, 1.0], "bed": "upright (split.py)",
                           "roof_of_recess_mm2": round(roof + arc), "roof_of_recess": f"{level:.0f} x {sp.t:g} level, and the top {math.pi / 4 * r:.1f} of the round at each end",
                           "window_bridge": round(2 * (sp.window_half - sp.window_r), 1), "window_h": 2 * wb,
                           "frame_facet_deg": 45.0}
    if piece is not None:
        seated = seat(piece, sp, d)
        rows["deck side R"]["box"] = split.print_box([(p.X, p.Y, p.Z) for p in seated.Vertexes], (0.0, 0.0, 1.0), lim)
        rows["deck side R"]["box_before"] = split.print_box([(p.X, p.Y, p.Z) for p in piece.Vertexes], (0.0, 0.0, 1.0), lim)
    return rows


# ---------- the build folders ----------

FINISH = {"deck": "white", "socket_plate": "white", "usb_sockets": "#26282c", "power_button": "#b9bcc2", "button_ring": "#5fb4ff", "knob": "#17181a", "screws": "#3a3c40",
          "deck_side_R": "white", "knob_plate": "white", "knob_left": "#17181a", "knob_screws": "#3a3c40", "floor": "#8a8f99", "hub": "#6a4fa0", "rooms": "#d07020"}
SQUARE_R = 6.0  # the corner radius of the outline option "square" (Blueprint.hood_sill_corner_r has the same value)
OUT_BY = 75.0  # the plate out of the shell, for the view of what is behind it


def deck_side_piece(d: Blueprint):
    """The print piece "deck side R" of the split, cut from the cached skin with the seams round it."""
    import Part  # noqa: PLC0415

    from . import split  # noqa: PLC0415

    skin = Part.Shape()
    skin.importBinary(str(split.skin_files(d)["body"]))
    seams, pieces = split.expanded(split.layout(d))
    keep = [s for s in seams if s.name in ("D1", "D2 R", "F1 R", "F2 R")]
    want = [p for p in pieces if p.full == "deck side R"]
    out, _ = split.cut(keep, want, split.Modules({"body": skin}, {}, {}, ""))
    return out["deck side R"]


def groups(sp: SocketPlate, d: Blueprint, v: Variant, out: float = 0.0, rooms: bool = False) -> dict:
    """The hardware of a variant in a few named compounds, for a build folder."""
    import Part  # noqa: PLC0415

    hw = hardware(sp, d, v, out)
    pick = lambda test: Part.makeCompound([s for k, s in hw.items() if test(k)])
    res = {"usb_sockets": pick(lambda k: k.startswith("USB_") and "screw" not in k and not is_room(k)), "power_button": hw["power_button"],
           "button_ring": hw["power_button_ring"], "screws": pick(lambda k: "screw" in k)}
    if v.knob:
        res["knob"] = hw["knob"]
    if rooms:
        res["rooms"] = pick(is_room)
    return res


def polylines(shape, y: float) -> list[list[list[float]]]:
    """The section of a shape in the plane y, as polylines in (x, z)."""
    out = []
    for w in shape.slice(_v(0, 1, 0), y):
        out.append([[round(p.x, 3), round(p.z, 3)] for p in w.discretize(Deflection=0.05)])
    return out


def sections(sp: SocketPlate, d: Blueprint, v: Variant, piece_seated, panel) -> dict:
    """Sections across the deck side (planes y) through the button, through the USB-A column, through the USB-C
    column and through the knob: the skin with the seat, the plate, the hardware and its rooms, the control panel."""
    _, yc, _ = sp.centre(d)
    hw = hardware(sp, d, v)
    pl = plate(sp, d, v)
    planes = {"button": yc + v.button_s, "usb-a": yc + v.a_s, "usb-c": yc + v.c_s}
    if v.knob:
        planes["knob"] = yc + v.knob_s
    out = {}
    for name, y in planes.items():
        out[name] = {"y": round(y, 2), "skin": polylines(piece_seated, y), "plate": polylines(pl, y), "panel": polylines(panel, y),
                     "hardware": {k: polylines(s, y) for k, s in hw.items() if not is_room(k) and s.BoundBox.YMin < y < s.BoundBox.YMax},
                     "rooms": {k: polylines(s, y) for k, s in hw.items() if is_room(k) and s.BoundBox.YMin < y < s.BoundBox.YMax}}
    return out


def cameras(sp: SocketPlate, d: Blueprint) -> dict:
    """The cameras of render_views.py on the plate: az turns from the front toward the player's right, el lifts."""
    from .dims import PEOPLE, eye_of  # noqa: PLC0415

    x, y, z = sp.centre(d)
    cam = lambda target, radius, az, el, aspect=0.6: {"target": [round(c, 1) for c in target], "radius": radius, "az": az, "el": el, "aspect": aspect}
    out = {"plate-side": cam((x, y, z), 86.0, 90.0, 0.0, 0.45), "plate-quarter": cam((x, y, z), 95.0, 58.0, 14.0), "plate-low": cam((x, y - 40, z), 60.0, 40.0, 4.0),
           "deck-right": cam((x - 40, y - 20, z + 20), 210.0, 52.0, 16.0, 0.6), "plate-button": cam((x, y - 48, z), 30.0, 68.0, 10.0, 0.75),
           "plate-usb": cam((x, y + 10, z), 36.0, 78.0, 8.0, 0.75), "plate-out": cam((x + OUT_BY / 2, y, z), 120.0, 52.0, 18.0, 0.7),
           "plate-inside": cam((x - 10, y, z + 4), 100.0, -104.0, 7.0, 0.6), "plate-out-rear": cam((x + OUT_BY / 2, y, z), 120.0, 128.0, 16.0, 0.7)}
    out["left-quarter"] = cam((-x, y - sp.length / 2 + KNOB_PLATE_LENGTH / 2, z), 70.0, -58.0, 14.0)
    out["left-side"] = cam((-x, y - sp.length / 2 + KNOB_PLATE_LENGTH / 2, z), 60.0, -90.0, 0.0, 0.6)
    out["deck-left"] = cam((-x + 40, y - 20, z + 20), 210.0, -52.0, 16.0, 0.6)
    # from the seat: the eye of the small adult and of the tall adult (dims.PEOPLE), toward the plate
    for person in PEOPLE[1:]:
        ey, ez = eye_of(person)
        dx, dy, dz = 0.0 - x, ey - y, ez - z
        out[f"seat-{person.name.replace(' ', '-')}"] = cam((x - 30, y - 10, z + 10), 240.0, round(math.degrees(math.atan2(dx, -dy)), 1),
                                                           round(math.degrees(math.atan2(dz, math.hypot(dx, dy))), 1), 0.7)
    return out


def write_folder(out: Path, shapes: dict, base: dict | None, base_edges: dict | None, focus: dict, deflection: float = 0.03) -> None:
    """A build folder as candybar.shell.solids writes it: BREP and mesh of each shape, manifest.json, edges.json and
    focus.json. `base` is the manifest of the shell parts that the folder shows as they are (their files by absolute
    path), `base_edges` their edges."""
    import MeshPart  # noqa: PLC0415

    from . import solids as so  # noqa: PLC0415

    out.mkdir(parents=True, exist_ok=True)
    manifest = dict(base or {})
    edges = dict(base_edges or {})
    for k, s in shapes.items():
        MeshPart.meshFromShape(Shape=s, LinearDeflection=deflection, AngularDeflection=0.05).write(str(out / f"{k}.stl"))
        s.exportBrep(str(out / f"{k}.brep"))
        manifest[k] = {"file": f"{k}.stl", "finish": FINISH[k], "brep": f"{k}.brep"}
        edges[k] = so.edge_polylines(s)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    (out / "edges.json").write_text(json.dumps(edges), encoding="utf-8")
    (out / "focus.json").write_text(json.dumps(focus, indent=1), encoding="utf-8")


def shell_base(folder: Path) -> tuple[dict, dict]:
    """The manifest and the edges of a build of the shell, without the deck, with its files by absolute path."""
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    edges = json.loads((folder / "edges.json").read_text(encoding="utf-8"))
    base = {k: {**e, "file": str(folder / e["file"]), "brep": str(folder / e["brep"])} for k, e in manifest.items() if k != "deck"}
    return base, {k: e for k, e in edges.items() if k != "deck"}


def markdown(rep: dict) -> str:
    sp = rep["values"]
    lines = ["# Front socket plate: values and checks", "", f"Result: **{rep['result']}**.", "",
             f"Plate {sp['length']:g} x {sp['height']:g} x {sp['t']:g}, round ends. Centre on the right side of the deck at "
             f"(x {rep['centre'][0]:.1f}, y {rep['centre'][1]:.1f}, z {rep['centre'][2]:.1f}). Print piece: deck side R.", "",
             "## The opening and the lines round it", "", "| From the rim of the recess to | mm |", "| --- | --- |"]
    lines += [f"| {k} | {val:g} |" for k, val in rep["seams"].items()]
    fl = rep["flat"]
    lines += ["", "## The flat part of the deck's side face", "",
              f"Flat from y {fl['y'][0]:g} to y {fl['y'][1]:g}: {fl['length']:g} long. Upright from z {fl['z'][0]:g} to z {fl['z'][1]:g}: {fl['height']:g} high. "
              f"The longest recess is {fl['longest_recess']:g} and the longest plate {fl['longest_plate']:g}; the plate is {fl['plate']:g}.",
              f"One row: the four flanges are {fl['one_row_flanges']:g}; the sockets alone with the two plate screws need {fl['one_row_sockets_only']:g}; "
              f"sockets, button and knob need {fl['one_row_all']:g}. One row does not fit. Two rows of sockets, the button and the knob fit in one plate."]
    lines += ["", f"The recess takes {rep['cut']['recess_mm3']:.0f} mm3 out of the outer form of the deck (the window: {rep['cut']['window']}).", ""]
    for key, r in rep["variants"].items():
        lines += [f"## Variant {key}: {r['title']}", "", "| Along the centre line | From s | To s | Gap to the item before |", "| --- | --- | --- | --- |"]
        lines += [f"| {x['item']} | {x['from']:g} | {x['to']:g} | {'' if x['gap'] is None else format(x['gap'], 'g')} |" for x in r["layout"]]
        lines += ["", "| On the front, along the centre line | From s | To s | Gap to the item before |", "| --- | --- | --- | --- |"]
        lines += [f"| {x['item']} | {x['from']:g} | {x['to']:g} | {'' if x['gap'] is None else format(x['gap'], 'g')} |" for x in r["outside"]]
        lines += ["", "| Socket | In fit.Layout (y, z) | On the plate (y, z) | Moved in y | Moved in z |", "| --- | --- | --- | --- | --- |"]
        lines += [f"| {m['socket']} | {m['was'][0]:g}, {m['was'][1]:g} | {m['is'][0]:g}, {m['is'][1]:g} | {m['dy']:+g} | {m['dz']:+g} |" for m in r["moves"]]
        lines += ["", f"Fit rules: {'PASS' if not r['fit']['failures'] else 'FAIL'}.", ""]
        lines += [f"- FAIL {f}" for f in r["fit"]["failures"]]
        lines += ["", "| Item | Gap to the skin and the frame | Nearest other item | Gap | Above the floor |", "| --- | --- | --- | --- | --- |"]
        lines += [f"| {i['item']} | {i['skin_gap']:g} | {i['neighbour']} | {i['neighbour_gap']:g} | {i['above_floor']:g} |" for i in r["fit"]["items"]]
        e, f = r["edges"], r["faces"]
        lines += ["", f"Edge finish: plate, {len(e['socket_plate']['shows'])} sharp edges that show, {sum(e['socket_plate']['under'].values())} under hardware, "
                  f"{e['socket_plate']['back']} on the back; seat in the deck, {len(e['deck']['shows'])} that show, {sum(e['deck']['under'].values())} under the plate, "
                  f"{e['deck']['back']} behind the plate.",
                  f"Face check: plate, {len(f['socket_plate']['fail'])} findings that fail of {f['socket_plate']['faces']} faces ({f['socket_plate']['allowed_count']} allowed: "
                  f"{'; '.join(f['socket_plate']['allowed'])}); deck, {len(f['deck']['fail'])} that fail at the seat ({f['deck']['allowed_count']} allowed: "
                  f"{'; '.join(f['deck']['allowed'])}).", ""]
    p = rep["print"]
    lines += ["## Print", "", f"- Plate: {p['socket_plate']['bed']}; box {p['socket_plate']['box']['x']:g} x {p['socket_plate']['box']['y']:g} x {p['socket_plate']['box']['z']:g}; "
              f"underside: {p['socket_plate']['underside']}; support: {p['socket_plate']['support']}.",
              f"- Deck side R: {p['deck side R']['bed']}; box {p['deck side R']['box']['x']:g} x {p['deck side R']['box']['y']:g} x {p['deck side R']['box']['z']:g} "
              f"(without the seat {p['deck side R']['box_before']['x']:g} x {p['deck side R']['box_before']['y']:g} x {p['deck side R']['box_before']['z']:g}). The roof of the recess "
              f"faces down: {p['deck side R']['roof_of_recess']} ({p['deck side R']['roof_of_recess_mm2']} mm2). The top of the window is a bridge of "
              f"{p['deck side R']['window_bridge']:g}. The frame has a facet of {p['deck side R']['frame_facet_deg']:g} degrees.", ""]
    return "\n".join(lines) + "\n"


def main() -> int:
    """Build every variant into CANDYBAR_OUT (default cad/out/socket-plate). CANDYBAR_SHELL names a folder with a
    build of the shell (candybar.shell.solids) to read the outer form from; without it the outer form is built
    here. CANDYBAR_PLATE_FIT=0 leaves the rules of the fit study out (they need the cavity, which takes some minutes)."""
    import Part  # noqa: PLC0415

    from .. import check  # noqa: PLC0415
    from . import cavity  # noqa: PLC0415
    from . import solids as so  # noqa: PLC0415

    root = Path(os.environ.get("CANDYBAR_ROOT", Path(__file__).resolve().parents[2]))
    out = Path(os.environ.get("CANDYBAR_OUT") or root / "out" / "socket-plate")
    built = os.environ.get("CANDYBAR_SHELL")
    d, sp = Blueprint(), SocketPlate()
    parts = shell_parts(d, built)
    if not built:
        built = str(out / "shell")
        so.export(built, parts, d)
    base, base_edges = shell_base(Path(built).resolve())
    focus = cameras(sp, d)
    deep = sp.web + sp.usb_clear_depth + 4.0
    deck = seat(parts["deck"], sp, d, hollow=False, deep=deep)
    deck_check = seat(parts["deck"], sp, d, hollow=False)
    piece = deck_side_piece(d)
    piece_seated = seat(piece, sp, d)
    cav = cavity.build(parts, d) if os.environ.get("CANDYBAR_PLATE_FIT", "1") != "0" else None
    x, yc, zc = sp.centre(d)
    rep = {"values": asdict(sp), "centre": [x, yc, zc], "seams": seam_distances(sp, d), "flat": flat_face(sp, d), "default": DEFAULT, "variants": {},
           "cut": {"recess_mm3": parts["deck"].Volume - deck_check.Volume,
                   "window": f"{2 * sp.window_half:g} x {sp.height - 2 * sp.ledge:g}, corners R {sp.window_r:g}; recess {sp.length + 2 * sp.reveal:g} x {sp.height + 2 * sp.reveal:g} x {sp.t:g} deep"},
           "piece": {"valid": piece_seated.isValid(), "solids": len(piece_seated.Solids), "volume_before_mm3": round(piece.Volume), "volume_mm3": round(piece_seated.Volume)}}
    values = fit_values(d, root / "params", parts, cav) if cav else None
    for v in VARIANTS:
        fit_rep = fitted(sp, d, v, root / "params", parts, cav, values) if cav else {"failures": ["not run"], "items": [], "rules": {}, "old_row": None}
        row = {"title": v.title, "layout": layout_rows(sp, v), "outside": outside_rows(sp, v), "fit": fit_rep, "edges": edge_finish(sp, d, v, deck_check), "faces": face_rows(sp, d, v, deck_check),
               "moves": moves(sp, d, v, fit_rep["old_row"]) if fit_rep["old_row"] else []}
        rep["variants"][v.key] = row
        write_folder(out / v.key, {"deck": deck, "socket_plate": plate(sp, d, v), **groups(sp, d, v)}, base, base_edges, focus)
        (out / v.key / "sections.json").write_text(json.dumps(sections(sp, d, v, piece_seated, parts["control_panel"])), encoding="utf-8")
        print(f"{v.key}: fit {'PASS' if not fit_rep['failures'] else fit_rep['failures']}, edges that show {len(row['edges']['socket_plate']['shows'])} + "
              f"{len(row['edges']['deck']['shows'])}, faces that fail {len(row['faces']['socket_plate']['fail'])} + {len(row['faces']['deck']['fail'])}")
    v = variant(DEFAULT)
    # the same variant with the plate proud on the face of the deck, for the sheet of the two seats
    proud = seat(parts["deck"], sp, d, "proud", hollow=False, deep=deep)
    write_folder(out / "proud", {"deck": proud, "socket_plate": plate(sp, d, v, sp.t), **groups(sp, d, v, sp.t)}, base, base_edges, focus)
    rep["proud"] = {"edges": edge_finish(sp, d, v, seat(parts["deck"], sp, d, "proud", hollow=False), "proud")}
    # the same variant with square ends (corners of SQUARE_R), for the sheet of the outlines
    sq = replace(sp, corner_r=SQUARE_R)
    write_folder(out / "square", {"deck": seat(parts["deck"], sq, d, hollow=False, deep=deep), "socket_plate": plate(sq, d, v), **groups(sq, d, v)}, base, base_edges, focus)
    sq_deck = seat(parts["deck"], sq, d, hollow=False)
    rep["square"] = {"corner_r": SQUARE_R, "edges": edge_finish(sq, d, v, sq_deck), "faces": face_rows(sq, d, v, sq_deck), "layout": layout_rows(sq, v)}
    # the alternative: the knob alone in a small plate in the left side of the deck, with the plain form of the default layout
    kp = knob_plate_values(sp, d)
    plain = variant(DEFAULT.replace("knob", "plain"))
    both = seat(left(seat(left(parts["deck"]), kp, d, hollow=False, deep=kp.t + kp.knob_clear + 4.0)), sp, d, hollow=False, deep=deep)
    khw = knob_plate_hardware(kp, d)
    kpl = knob_plate(kp, d)
    write_folder(out / "knob-left", {"deck": both, "socket_plate": plate(sp, d, plain), **groups(sp, d, plain), "knob_plate": left(kpl), "knob_left": left(khw["knob"]),
                                     "knob_screws": left(Part.makeCompound([khw["plate_screwa"], khw["plate_screwb"]]))}, base, base_edges, focus)
    kdeck = seat(parts["deck"], kp, d, hollow=False)
    kfr = Frame(kp, d)
    shows = [[round(e.Length, 1), round(turn, 1)] for e, turn in sharp(kpl, d) if so.middle(e).x >= kfr.x - kp.web + 1e-3 and not covered(e, khw | {"deck": kdeck})]
    kx, ky, kz = kp.centre(d)
    rep["knob_left"] = {"plate": [kp.length, kp.height, kp.t], "centre": [-kx, ky, kz], "window": [2 * kp.window_half, kp.height - 2 * kp.ledge],
                        "sharp_edges_that_show": shows, "valid": kpl.isValid() and both.isValid(), "with": plain.key,
                        "front_of_recess_behind_the_corner": round(ky - kp.length / 2 - kp.reveal - pr.deck_plan(d)[0].q[1], 2),
                        "deepest_x": round(-(kx - kp.t - kp.knob_clear), 1)}
    # the print piece with the seat: the plate in place, and the plate out with what is behind it
    hub = None
    if cav:
        b = rep["variants"][DEFAULT]["fit"]["hub"]
        hub = Part.makeBox(b[3] - b[0], b[4] - b[1], b[5] - b[2], _v(b[0], b[1], b[2]))
    bb = piece_seated.BoundBox
    floor = Part.makeBox(bb.XLength - d.wall_t - 1.0, bb.YLength + 60.0, sp.floor_t - 0.2, _v(bb.XMin, bb.YMin + d.wall_t + 1.0, 0.1))
    extra = {"floor": floor} | ({"hub": hub} if hub else {})
    write_folder(out / "behind", {"deck_side_R": piece_seated, "socket_plate": plate(sp, d, v), **groups(sp, d, v, rooms=True)}, None, None, focus)
    write_folder(out / "out", {"deck_side_R": piece_seated, "socket_plate": plate(sp, d, v, OUT_BY), **groups(sp, d, v, OUT_BY), **extra}, None, None, focus)
    rep["print"] = print_rows(sp, d, v, piece)
    bad = [k for k, r in rep["variants"].items() if r["fit"]["failures"] or r["edges"]["socket_plate"]["shows"] or r["edges"]["deck"]["shows"]
           or r["faces"]["socket_plate"]["fail"] or r["faces"]["deck"]["fail"]]
    other = rep["knob_left"]["sharp_edges_that_show"] or not rep["knob_left"]["valid"] or rep["proud"]["edges"]["socket_plate"]["shows"] or rep["square"]["edges"]["socket_plate"]["shows"] or rep["square"]["edges"]["deck"]["shows"] \
        or rep["square"]["faces"]["socket_plate"]["fail"] or rep["square"]["faces"]["deck"]["fail"]
    rep["result"] = check.FAIL if bad or other else check.PASS
    (out / "report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    (out / "report.md").write_text(markdown(rep), encoding="utf-8")
    print(f"socket plate: {rep['result']}; report in {out / 'report.md'}")
    return 1 if rep["result"] == check.FAIL else 0
