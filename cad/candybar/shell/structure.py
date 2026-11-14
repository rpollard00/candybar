"""Structure, mounts, cable routes and the air path of the split, at concept level.

The seams of split.py are joints, and joints are structure. The shell is a stressed skin (decision record 0006):
the flanges of the bonded seams are ring frames, the printed floor is the datum, and the hardware carriers are
cross-members: the fixed part of the monitor cradle between the two rails, the carrier of the BC-250 (the rear door
is a cover), the control panel frame, the hood as a cap. Ribs stiffen the large near-flat walls. The frame of
aluminium extrusion that the study of 2026-11-11 examined (its option C) is not in the code: the owner did not
choose it.

This module holds the data (members, mounts, routes, air path) and the hand estimates. It has no FreeCAD at
import; main() (under FreeCAD) moves the hardware of the fit study in the skin, measures the walls of the hand-holds
and writes split/structure.json. tools/draw_split.py draws the sheets and writes split/report.md from both. The
joint values are in joints.py (Joint, OtherJoints); this module has none of its own.

    CANDYBAR_OUT=cad/out/shell-rev7 cad/candybar/freecad-run.sh candybar.shell.structure
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from pathlib import Path

from .dims import Blueprint

P3 = tuple[float, float, float]
E_PETG = 2000.0        # MPa, printed PETG in the layer plane (ESTIMATED from data sheets: 1.9 to 2.1 GPa)
NU = 0.38
E_AL = 70000.0         # MPa
G = 9.81
CREEP_MPA = 5.0        # sustained stress limit for PETG at room temperature (ESTIMATED: a tenth of the 50 MPa yield)
YIELD_MPA = 50.0       # short-term strength of printed PETG in the layer plane (ESTIMATED from data sheets: 45 to 55 MPa)


# ---------- masses ----------

# (item, kg, status, source)
HARDWARE = (
    ("power supply EVGA SuperNOVA 1000 P5", 3.27, "sourced", "maker's net weight (bc250-cooling-and-psu.md S1); may include cables"),
    ("monitor, 16 inch UPERFECT", 0.82, "sourced", "hardware-envelopes.md section 1"),
    ("BC-250 board with stock heatsink", 1.00, "estimated", "no published weight"),
    ("ARCTIC P12 Pro fan", 0.183, "sourced", "ARCTIC spec sheet"),
    ("fan shroud, exhaust duct and BC-250 carrier, printed", 0.40, "estimated", ""),
    ("control panel: 2.0 mm aluminium and 1.5 mm polycarbonate", 0.49, "estimated", "396 x 175 plate area, 2.70 and 1.20 g/cm3"),
    ("lever, 8 buttons, 3 service buttons, encoder", 0.70, "estimated", ""),
    ("monitor cradle with clamps", 0.35, "estimated", ""),
    ("speakers (2), amplifier", 0.45, "estimated", "no hardware chosen"),
    ("marquee modules (11) and controller", 0.25, "estimated", "no hardware chosen"),
    ("USB hub, sockets and socket plate", 0.20, "estimated", ""),
    ("cables and connectors", 0.60, "estimated", ""),
    ("bezel plate, printed", 0.76, "measured from the solid", "split/measurements.json: two halves, solid"),
    ("ribs, flanges, splice plates, inserts, screws", 0.0, "estimated", "25 % of the skin; set in total_mass"),
)
# the printed floor (the owner, 2026-11-11: "we just print a rigid piece of petg with more infill"): a sandwich 10 mm
# thick, two skins of 1.2 mm on a gyroid core of 40 %. The cabinet stands on it on the table, on thin non-slip pads
# (the owner: "I think floor on table, I can add non slip adhesive feet"); no feet and no ribs under it. The power
# supply, the BC-250 and the hub stand 3 mm higher than on the 7 mm floor of the study (fit.Layout.floor_t)
FLOOR_T = 10.0
PAD_T = (2.0, 3.0)  # the non-slip pads under the floor (ESTIMATED: thin adhesive pads)
FLOOR_SKIN = 1.2
FLOOR_INFILL = 0.40
FLOOR_KG_DM2 = 1.27 * (2 * FLOOR_SKIN + FLOOR_INFILL * (FLOOR_T - 2 * FLOOR_SKIN)) / 100  # g/cm3 x mm -> kg/dm2


def total_mass(skin_kg: float, floor_area_dm2: float) -> dict:
    """skin_kg: the shell pieces without the floor tiles; the floor is the FLOOR_T sandwich."""
    hw = sum(m for _, m, _, _ in HARDWARE)
    extras = 0.25 * skin_kg
    floor = FLOOR_KG_DM2 * floor_area_dm2
    return {"skin": skin_kg, "joints_and_ribs": extras, "floor": floor, "hardware": hw, "total": skin_kg + extras + floor + hw}


def skin_kg(rows: dict) -> float:
    """The mass of the printed pieces of a cut without the floor tiles (split.measure rows)."""
    return sum(r["mass_g"] for r in rows.values() if r["module"] != "base") / 1000


def centre_of_mass(rows: dict, mass: dict, d: Blueprint) -> tuple[float, float]:
    """(y, z) of the centre of mass of the cabinet: each printed piece at the middle of its box in the cabinet, the
    extras with the skin, the floor at the middle of its plan, and the hardware at the places of the fit study
    (ESTIMATED: each item at the middle of its envelope)."""
    my = mz = m = 0.0
    for r in rows.values():
        if r["module"] == "base" or "cabinet" not in r:
            continue
        k = r["mass_g"] / 1000 * (1 + mass["joints_and_ribs"] / mass["skin"])
        my, mz, m = my + k * (r["cabinet"][2] + r["cabinet"][3]) / 2, mz + k * (r["cabinet"][4] + r["cabinet"][5]) / 2, m + k
    my, mz, m = my + mass["floor"] * d.body_d / 2, mz + mass["floor"] * FLOOR_T / 2, m + mass["floor"]
    for name, kg, _, _ in HARDWARE:
        y, z = next((yz for key, yz in HARDWARE_AT.items() if name.startswith(key)), (d.body_d / 2, d.body_top / 2))
        my, mz, m = my + kg * y, mz + kg * z, m + kg
    return my / m, mz / m


# where the centre of each item of HARDWARE is, (y, z), from the fit study's layout (ESTIMATED to the nearest 10 mm)
HARDWARE_AT = {"power supply": (460.0, 55.0), "monitor": (350.0, 250.0), "BC-250": (480.0, 195.0), "ARCTIC": (510.0, 185.0),
               "fan shroud": (500.0, 185.0), "control panel": (115.0, 68.0), "lever": (115.0, 50.0), "monitor cradle": (365.0, 250.0),
               "speakers": (480.0, 475.0), "marquee": (480.0, 535.0), "USB hub": (295.0, 20.0), "cables": (400.0, 100.0),
               "bezel plate": (345.0, 265.0)}


def floor_stiffness() -> dict:
    """Bending stiffness D per mm of width: the sandwich (skins only, core ignored for E) against a solid plate."""
    h = FLOOR_T - FLOOR_SKIN
    sandwich = E_PETG * FLOOR_SKIN * h ** 2 / 2
    solid4 = E_PETG * 4.0 ** 3 / 12
    solid7 = E_PETG * FLOOR_T ** 3 / 12
    # the power supply (3.27 kg) on a tile span of 190: a strip 150 wide, simply supported, load at mid span
    p, span, width = 3.27 * G * 2, 190.0, 150.0
    w = p * span ** 3 / (48 * sandwich * width)
    return {"sandwich_Nmm": sandwich, "solid4_Nmm": solid4, "solid7_Nmm": solid7, "psu_sag_mm": w}


# ---------- hand estimates ----------

def plate_deflection(p: float, b: float, a: float, t: float, e: float, nu: float = NU) -> float:
    """Centre deflection of a simply supported rectangular plate (short side b, long side a) under a point load p at
    its centre: w = alpha p b^2 / D (Timoshenko, Theory of Plates and Shells, table 26; alpha from 0.0116 at a/b = 1
    to 0.0165 at a/b = 2 and more)."""
    r = min(a / b, 2.0)
    alpha = 0.0116 + (0.0165 - 0.0116) * (r - 1.0)
    d = e * t ** 3 / (12 * (1 - nu ** 2))
    return alpha * p * b ** 2 / d


def rib_spacing(p: float, w_max: float, t: float, e: float = E_PETG) -> float:
    """The largest short side of a skin panel that keeps the deflection under a point load p below w_max (a/b = 2)."""
    d = e * t ** 3 / (12 * (1 - NU ** 2))
    return math.sqrt(w_max * d / (0.0165 * p))


def estimates(mass: dict, d: Blueprint) -> dict:
    """The load cases of the brief to the coordinator, each as numbers with its formula."""
    w = mass["total"] * G
    out = {}
    # a straight lift by the two hand-holds, with a factor of 2 for a jerk: the whole weight on the two roofs
    per = w * 2 / 2
    rim = d.grip_x1 - d.grip_x0
    out["lift"] = {"weight_N": w, "per_hold_N": per,
                   "rim_shear_MPa": per / (rim * d.wall_t),
                   "note": f"two holds, dynamic factor 2: {per:.0f} N each into the {rim:.0f} mm rim of the roof, {d.wall_t:g} mm wall"}
    # lean on the deck front: 200 N on the 4 mm front wall of the nose, 274 mm long
    out["lean"] = {"stress_MPa": 200.0 / (274.0 * d.wall_t), "note": "200 N in compression in the deck's front wall (274 x 4)"}
    # hit on the control panel: 200 N at the centre of the 2.0 mm aluminium plate on its ledge
    out["panel"] = {"deflection_mm": plate_deflection(200.0, d.panel_d, d.panel_w, 2.0, E_AL),
                    "note": "200 N at the centre, 2.0 mm aluminium, simply supported on the 8 mm ledge (the cover adds stiffness)"}
    # racking: 50 N sideways at the top of the hood
    h_top = d.body_top + d.hood_h
    out["racking"] = {"moment_body_top_Nm": 50.0 * (h_top - d.body_top) / 1000, "moment_floor_Nm": 50.0 * h_top / 1000,
                      "portal_mm": portal(25.0, 300.0, 4.0e4), "note": "half of 50 N on each of the front and rear portals"}
    # finger push on the largest near-flat span, 4 mm skin
    spans = {"side band between L1 and B1": (d.rear_shelf_z0 - 134.3, 240.0),
             "side of the lower body below L1": (d.door_z0, d.body_d - (d.band_foot_y + d.band_depth)),
             "lower rear wall below the door, one half": (d.door_z0, d.door_w / 2),
             "upper rear wall between the hand-holds": (d.body_top - d.rear_shelf_z1, 2 * d.grip_x0)}
    out["finger"] = {k: plate_deflection(20.0, min(v), max(v), d.wall_t, E_PETG) for k, v in spans.items()}
    out["rib_spacing_mm"] = rib_spacing(20.0, 0.3, d.wall_t)
    out["rib_spacing_3mm"] = rib_spacing(20.0, 0.3, 3.0)
    out["floor"] = floor_stiffness()
    # the monitor on its cradle, 30 degrees of recline
    m = 0.82
    along = m * G * math.cos(math.radians(d.recline))
    normal = m * G * math.sin(math.radians(d.recline))
    lever, bw, bt = 10.0, 20.0, 4.0
    out["monitor"] = {"along_face_N": along, "into_cradle_N": normal,
                      "clamp_stress_MPa": 6 * along * lever / (bw * bt ** 2), "creep_limit_MPa": CREEP_MPA,
                      "note": "bottom clamp tab 20 wide, 4 thick, load 10 from its root"}
    # hot air: dT = P / (rho cp Q); no limit on PETG near it (the owner's PETG case for a BC-250 does not soften)
    q = 40.0 / 3600
    out["heat"] = {"exhaust_dT_K": 200.0 / (1.2 * 1005 * q),
                   "note": "200 W of the BC-250 at 40 m3/h through the fins (bc250-cooling-and-psu.md: about 15 K)"}
    return out


def portal(p: float, h: float, i: float) -> float:
    """Sway of a portal with fixed feet and a stiff top beam: p h^3 / (24 E I) for the two posts."""
    return p * h ** 3 / (24 * E_PETG * i)


# ---------- the parts of each architecture, as drawing data ----------

@dataclass(frozen=True)
class Member:
    """A structural part in the cabinet frame: a box (x0, x1, y0, y1, z0, z1), or a bar along a line in the yz plane
    (p, q) with a section of sx (across x, from x0) and sn (square to the line)."""
    name: str
    kind: str          # floor, ring, cross, rib, mount
    box: tuple[float, ...] = ()
    p: tuple[float, float] = ()
    q: tuple[float, float] = ()
    x0: float = 0.0
    sx: float = 20.0
    sn: float = 20.0
    mirror: bool = False
    note: str = ""


KIND_WORDS = {"floor": "structural floor", "ring": "ring frame (seam flange)", "cross": "cross-member (hardware carrier)",
              "rib": "ribs", "mount": "mount"}


def grip_box(d: Blueprint) -> tuple[float, ...]:
    """The right hand-hold as a box (x0, x1, y0, y1, z0, z1): the recess of dims.Blueprint in the rear wall of the head."""
    return (d.grip_x0, d.grip_x1, d.depth - d.grip_depth, d.depth, d.grip_z0, d.grip_z1)


# the make-up air inlet: a slot grille in the lower rear wall, right of the centre line, below the door sill (z 116)
# and the cut-ins (from z 126, x 215), and right of the stowed cables (x up to 73); far from the power supply's grille
# at the left
INLET = (95.0, 205.0, 536.0, 540.0, 15.0, 108.0)
INLET_OPEN = 0.55  # ESTIMATED: the open share of a printed slot grille (slots 3 wide, bars 2.5)


def makeup_air() -> dict:
    """The air that the power supply's fan draws from the cabinet, and the inlet area it needs. The BC-250 draws its
    own air through the door straight into its shroud, so only the supply needs make-up air."""
    heat_w, dt = 25.0, 10.0          # ESTIMATED: 20 to 25 W of supply loss at 200 W (bc250-cooling-and-psu.md), 10 K rise
    q = heat_w / (1.2 * 1005 * dt)   # m3/s
    design = 3.0 * q                 # a margin of 3 for the fan, which moves more than the heat needs when it turns
    need = {v: design / v * 1e4 for v in (1.0, 1.5)}  # cm2 of free area at a face speed of 1.0 and 1.5 m/s
    perimeter = 2 * (494.7 + 540.0)  # mm, the edge of the floor
    gap = {}
    for h in PAD_T:
        area = perimeter * h / 100   # cm2 at the edge
        v = design / (area * 1e-4)
        dp = 12 * 1.8e-5 * 0.25 * v / (h / 1000) ** 2   # Pa, laminar flow 250 mm under the floor (plates h apart)
        gap[h] = {"area_cm2": area, "speed_m_s": v, "dp_Pa": dp}
    x0, x1, _, _, z0, z1 = INLET
    gross = (x1 - x0) * (z1 - z0) / 100
    return {"heat_W": heat_w, "dT_K": dt, "flow_m3h": q * 3600, "design_m3h": design * 3600, "need_cm2": need, "gap": gap,
            "inlet_gross_cm2": gross, "inlet_free_cm2": gross * INLET_OPEN, "inlet": INLET}


def members(d: Blueprint, board: tuple[float, float] | None = None) -> list[Member]:
    """The stressed skin: the printed floor, the ring frames that the seam flanges make, the cross-members, the
    hand-holds and the inlet. board is the x range of the BC-250's board in the fit study (its carrier goes round
    it); without it the carrier is not in the list."""
    x = d.width / 2
    door_x = d.door_w / 2
    y_band = d.band_foot_y + d.band_depth
    out = [
        Member("floor", "floor", box=(-243.3, 243.3, 4.0, 536.0, 0.0, FLOOR_T),
               note=f"printed PETG sandwich {FLOOR_T:g} mm, nine tiles with half-lap joints: the datum that the lower pieces bolt "
                    "to; it stands on the table on thin non-slip pads"),
        Member("ring L1, front", "ring", box=(-x, x, 194.0, y_band, 130.0, 138.0), note="flanges of L1 in front of the band, at the bezel's bottom corner"),
        Member("ring L1, rear", "ring", box=(-x, x, y_band - 16.0, d.body_d, d.door_z0 - 4.0, d.door_z0 + 4.0),
               note="flanges of L1 behind the band, round the sides and the rear at the height of the door sill"),
        Member("ring B1", "ring", box=(-x, x, 250.0, d.body_d, d.rear_shelf_z0 - 8.0, d.rear_shelf_z0),
               note="flanges of B1, in the crease of the rear shelf on the rear and on the sides"),
        Member("top ring", "ring", box=(-x, x, 420.0, d.depth, d.body_top - 8.0, d.body_top),
               note="the service flange under the groove: closes the open body top, carries the hood"),
        Member("deck frame D1/D2", "ring", box=(-x, x, 188.0, 211.0, d.wall_t, 72.0), note="flanges of D1 and D2, across the deck's back"),
        Member("monitor cradle", "cross", p=(300.0, 125.0), q=(450.0, 380.0), x0=-211.0, sx=422.0, sn=20.0,
               note="the fixed frame between the two middle pieces, screwed to their inner flanges at the rails; it "
                    "holds the magnets for the bezel plate; the monitor's carrier slides out of it to the front"),
        Member("door opening frame", "ring", box=(-door_x - 8.0, door_x + 8.0, d.body_d - 16.0, d.body_d - d.wall_t, d.door_z0 - 8.0, d.door_z1 + 8.0),
               note="flanges round the door opening (rear lower, middle and upper rear pieces); the door screws to it and closes the ring"),
        Member("panel frame", "cross", box=(-199.0, 199.0, 26.0, 202.0, 58.0, 65.0), note="the ledge under the control panel and its latch"),
        Member("side ribs", "rib", box=(x - 12.0, x - 4.0, 210.0, 520.0, 20.0, 400.0), mirror=True,
               note="ribs 8 high, 3 thick, at most 110 apart on the side band and the side of the lower body"),
        Member("hand-hold", "mount", box=grip_box(d), mirror=True,
               note="a recess in the rear wall of the head, part of the shell (decision record 0007): a level floor, and a "
                    "roof that falls 45 degrees toward the inside as the hook for the fingers. It is whole in one upper rear piece"),
        Member("make-up air inlet", "mount", box=INLET, note="a slot grille in the lower rear wall, right of the "
               "centre line and below the door: the air that the power supply's fan draws in"),
    ]
    if board:
        out.insert(8, Member("BC-250 carrier", "cross", box=(board[0] - 11.0, board[1] + 21.5, 455.0, 470.0, d.door_z0 - 1.0, d.door_z1 - 10.0),
                             note="two uprights and two edge rails round the board; right foot on the floor, left on the door sill"))
    return out


@dataclass(frozen=True)
class Mount:
    item: str
    how: str
    on: str


def mounts() -> list[Mount]:
    return [
        Mount("power supply", "Stands on rubber pads in a printed saddle screwed to the floor; two straps over it. Its four "
              "rear screws only locate it on the rear wall; no weight hangs on the wall.", "floor"),
        Mount("BC-250", "On its long edge in a printed carrier: two uprights and two rails that hold the board's edges. "
              "Right upright on the floor, left upright on the door sill and the flanges round the door opening.",
              "floor and door sill"),
        Mount("fan shroud and exhaust duct", "Printed, screwed to the BC-250's carrier; they end 5 mm short of the door, "
              "and a foam seal closes the gap, so that the door lifts off free.", "BC-250 carrier"),
        Mount("optional duct fan, 92 mm", "Four screws into bosses on the duct, in front of the slot vents.", "exhaust duct"),
        Mount("monitor", "A removable carrier with clamps on the top and bottom edges of the monitor and slots for 8 mm of "
              "adjustment each way, set from the front with the bezel plate off; it slides out forward through the opening. "
              "The fixed part of the cradle is screwed at four corners to the inner flanges of the two middle pieces at the rails.",
              "middle R and L"),
        Mount("speakers", "Each driver screws to a printed baffle bonded behind the speaker opening of the hood band.", "hood"),
        Mount("marquee modules", "On a printed rail across the hood behind the marquee cover, screwed to the hood's inner "
              "flanges at the legs; the controller beside it.", "hood"),
        Mount("encoder", "On the control panel frame under the panel, so that it leaves with the panel (one encoder for each "
              "panel).", "control panel"),
        Mount("USB hub", f"On the {FLOOR_T:g} mm floor behind the USB row (fit study), in a printed clip.", "floor"),
        Mount("USB socket plate", "Screwed from inside into a frame of inserts round its opening in the deck side.", "deck side R"),
        Mount("control panel frame and latch", "The ledge under the plate takes the load; two pins at the front, a latch at "
              "the back into the deck frame D1/D2.", "deck"),
        Mount("hood", "Two pins at the front, two M4 screws through the foot of the rear wall into the top ring.", "body top"),
        Mount("non-slip pads", f"Thin adhesive non-slip pads ({PAD_T[0]:g} to {PAD_T[1]:g} mm) under the floor tiles; the floor "
              "stands on the table. No feet.", "the floor"),
    ]


@dataclass(frozen=True)
class Route:
    name: str
    colour: str
    points: tuple[P3, ...]
    crossings: str


ROUTES = (
    Route("mains", "#000000", ((-150.0, 600.0, 50.0), (-150.0, 541.0, 50.0)),
          "Wall to the power supply's own inlet (IEC C14), through its grille in the rear lower wall. No seam."),
    Route("12 V to the BC-250", "#d62728", ((-120.0, 380.0, 40.0), (150.0, 380.0, 60.0), (150.0, 440.0, 80.0), (150.0, 440.0, 300.0),
                                           (58.0, 470.0, 320.0)),
          "PCIe 6+2 lead from the power supply's front, along the floor, up right of the compute module to its plug. "
          "The door opens: unplug at the board, and a 150 mm loop lets the door swing down first."),
    Route("5 V to the hub", "#ff7f0e", ((-120.0, 380.0, 30.0), (190.0, 370.0, 14.0)),
          "SATA lead along the floor to the hub. No service joint."),
    Route("video and power to the monitor", "#9467bd", ((-158.0, 470.0, 200.0), (-200.0, 450.0, 192.0), (-200.0, 337.0, 192.0),
                                                       (-188.0, 330.0, 215.0)),
          "DisplayPort to HDMI at the BC-250's I/O end, then the left channel (x -210 to -190) to the monitor's plugs; "
          "the monitor's USB-C power by the right channel. The monitor leaves through the bezel opening: unplug at the "
          "monitor (right-angle plugs), with 100 mm of slack in the channel."),
    Route("hub to the USB sockets", "#2ca02c", ((199.0, 241.0, 14.0), (199.0, 200.0, 20.0), (205.0, 120.0, 24.0)),
          "Short leads forward along the floor; they cross seam D2 inside (no joint needed). The socket plate comes "
          "out with its leads."),
    Route("encoder to the hub", "#17becf", ((-165.0, 87.0, 40.0), (-165.0, 180.0, 20.0), (190.0, 230.0, 14.0)),
          "USB from the encoder on the panel. The panel opens: one USB plug at the panel's back edge, 200 mm loop."),
    Route("speakers and marquee", "#8c564b", ((136.0, 480.0, 475.0), (120.0, 470.0, 430.0), (120.0, 470.0, 300.0), (60.0, 470.0, 300.0)),
          "From the hood down through the open body top to the amplifier and the controller. The hood lifts off: one "
          "multi-pin plug at the hood's foot."),
)

AIR = (
    ("fan vent (intake)", "rear door: door half R, and its left end in door half L; a foam seal to the shroud", "Outside air in through the vent over the fan."),
    ("fan, ARCTIC P12 Pro", "on the fins, under the shroud", "Blows down into the opened fin tops."),
    ("shroud", "door's inner frame", "Seals the fan to the fins."),
    ("fins of the heatsink", "BC-250", "Air leaves the fins at the I/O end."),
    ("exhaust duct", "door's inner frame", "Turns the hot air along the door to the slot vents."),
    ("slot vents (exhaust)", "rear door, left: door half L", "Hot air out, about 15 K above the intake."),
    ("power supply fan", "power supply (its top face)", "Draws cabinet air; off below about 200 W (sister unit data)."),
    ("power supply grille", "lower rear wall, left, below the cut-ins: rear lower L", "The power supply's own exhaust out of its rear face."),
    ("make-up air inlet", "lower rear wall, right of the centre line below the door: rear lower R",
     "Replaces the air that the power supply's fan takes out. The owner wants all vents in the rear; the 2 to 3 mm "
     "under the floor is too thin (see the air path). It is 150 mm right of the supply's grille, so warm air is not "
     "drawn back in."),
)


# ---------- the hardware in the skin, under FreeCAD ----------

def fit_items(root: Path):
    """The hardware and keep-out solids of the fit study, placed with the anchors that the study wrote."""
    from candybar import params  # noqa: PLC0415

    from . import fit  # noqa: PLC0415

    anchors = json.load(open(root / "fit" / "report.json"))["anchors"]
    doc = fit.build_items(fit.sheet_rows(Path(__file__).resolve().parents[2] / "params", anchors))
    return doc, fit.items(doc)


def compute_move(found, steps=(0.0, 2.0, 3.5, 5.0, 8.0)) -> list[dict]:
    """The compute module moved toward the front by dy: the common volume of its solids with every other item's
    solids (hardware and keep-out zones). The rear door is at y 536; the module's duct reaches 535.9."""
    import FreeCAD as App  # noqa: PLC0415

    comp = [sl for it in found if it.group == "Compute" for sl in it.solids]
    others = [(it.name, sl) for it in found if it.group not in ("Compute",) for sl in it.solids]
    out = []
    for dy in steps:
        hits = {}
        for c in comp:
            moved = c.world.translated(App.Vector(0, -dy, 0))
            for name, o in others:
                if not moved.BoundBox.intersect(o.world.BoundBox):
                    continue
                v = moved.common(o.world).Volume
                if v > 1.0:
                    key = f"{c.name} / {o.name} ({o.role})"
                    hits[key] = round(hits.get(key, 0.0) + v)
        out.append({"dy": dy, "hits": hits})
    return out


def monitor_path(d: Blueprint, found, skin) -> list[dict]:
    """The room for any 16:10 monitor (body, clamps, plug space) pulled forward, square to the screen face, out
    through the opening behind the bezel: its common volume with the skin at each step."""
    from . import solids as so  # noqa: PLC0415

    room = [sl.world for it in found if it.group == "MonitorRoom" for sl in it.solids if "Cradle" not in sl.name]
    _, _, into = so.screen_frame(d)
    out = []
    for t in (0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0):
        v = sum(r.translated(into * -t).common(skin).Volume for r in room)
        out.append({"out_mm": t, "in_skin_mm3": round(v)})
    return out


FLOOR_DM2 = 4.866 * 5.32  # the plan of the floor inside the walls


def wall_rays(d: Blueprint) -> list[tuple[str, P3, P3]]:
    """Rays through the walls of the right hand-hold, each from a point in the recess: (name, start, direction)."""
    x0, x1, y0, y1, z0, z1 = grip_box(d)
    xm, ym, zm = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
    return [("back", (xm, y1 - 1.0, zm), (0.0, -1.0, 0.0)), ("floor", (xm, ym, zm), (0.0, 0.0, -1.0)),
            ("roof, straight up", (xm, ym, zm - 8.0), (0.0, 0.0, 1.0)), ("outer end", (xm, ym, zm - 8.0), (1.0, 0.0, 0.0)),
            ("inner end", (xm, ym, zm - 8.0), (-1.0, 0.0, 0.0)),
            ("wall above the recess", (xm, d.depth + 1.0, (z1 + d.body_top - d.seam_groove) / 2), (0.0, -1.0, 0.0))]


def hand_hold_walls(d: Blueprint, skin) -> dict:
    """The wall round the right hand-hold, measured on the skin: along each ray of wall_rays, the first length that
    lies in the skin."""
    import FreeCAD as App  # noqa: PLC0415
    import Part  # noqa: PLC0415

    x0, x1, y0, y1, z0, z1 = grip_box(d)
    m = 45.0
    near = skin.common(Part.makeBox(x1 - x0 + 2 * m, y1 - y0 + m + 2.0, z1 - z0 + 2 * m, App.Vector(x0 - m, y0 - m, z0 - m)))
    out = {}
    for name, start, direction in wall_rays(d):
        p, n = App.Vector(*start), App.Vector(*direction)
        spans = sorted((min((v.Point - p).dot(n) for v in e.Vertexes), e.Length) for e in Part.makeLine(p, p + n * 80.0).common(near).Edges)
        out[name] = {"from": round(spans[0][0], 2), "wall": round(spans[0][1], 2)} if spans else None
    return out


def main() -> int:
    import FreeCAD as App  # noqa: PLC0415

    from . import split  # noqa: PLC0415

    d = Blueprint()
    root = Path(os.environ.get("CANDYBAR_OUT", "cad/out/shell-rev7"))
    mods = split.build_modules(d)
    doc, found = fit_items(root)
    move = compute_move(found)
    path = monitor_path(d, found, mods.skin["body"])
    App.closeDocument(doc.Name)
    walls = hand_hold_walls(d, mods.skin["body"])
    out = {"compute_move": move, "monitor_path": path, "hand_hold_walls": walls}
    meas = root / "split" / "measurements.json"
    if meas.exists():
        rows = json.load(open(meas))[split.SHELL]["pieces"]
        mass = total_mass(skin_kg(rows), FLOOR_DM2)
        com = centre_of_mass(rows, mass, d)
        out.update(mass=mass, centre_of_mass=com, hand_holds=hand_holds(mass["total"], com[0], d))
    for m in move:
        print("compute forward", m["dy"], m["hits"])
    for m in path:
        print("monitor out", m)
    print("hand-hold walls", walls)
    if "hand_holds" in out:
        print("hand-holds", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out["hand_holds"].items()})
    (root / "split").mkdir(parents=True, exist_ok=True)
    (root / "split" / "structure.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


# ---------- the owner's choices of 2026-11-11 ----------

def floor_options(mass_kg: float) -> dict:
    """The floor under the power supply when the cabinet is lifted by its hand-holds (the supply's weight x 2 for a
    jerk), as a strip as wide as the supply spanning from the deck's back frame (y 207) to the rear wall (y 536):
    a 7 mm sandwich alone, the same with ribs under it, and a 10 mm sandwich with the supply raised 3 mm. The core
    is left out of the stiffness (ESTIMATED: a gyroid core of 40 % adds little in bending)."""
    p = 3.27 * G * 2
    span, a = 536.0 - 207.0, 461.0 - 207.0
    b = span - a
    width = 150.0

    def ei(parts: list[tuple[float, float, float]]) -> float:
        """Rectangles (width, height, z of the centre): E I about the common neutral axis."""
        area = sum(w * h for w, h, _ in parts)
        zc = sum(w * h * z for w, h, z in parts) / area
        return E_PETG * sum(w * h ** 3 / 12 + w * h * (z - zc) ** 2 for w, h, z in parts)

    s = FLOOR_SKIN
    sandwich = lambda t: [(width, s, s / 2), (width, s, t - s / 2)]
    rib_h, rib_t, rib_pitch = 12.0, 2.4, 50.0
    ribs = [(rib_t, rib_h, -rib_h / 2)] * int(width / rib_pitch)
    lap = [(width, FLOOR_T, FLOOR_T / 2)]  # the bonded half-lap of a tile joint: solid over 20 mm
    rows = {"sandwich 7 mm": ei(sandwich(7.0)), "sandwich 7 mm with ribs 12 x 2.4 every 50 under it": ei(sandwich(7.0) + ribs),
            "sandwich 10 mm (the supply 3 mm higher)": ei(sandwich(10.0))}
    out = {k: {"EI": v, "sag_mm": p * a ** 2 * b ** 2 / (3 * v * span)} for k, v in rows.items()}
    out[f"joint, solid {FLOOR_T:g} mm lap"] = {"EI": ei(lap), "sag_mm": p * a ** 2 * b ** 2 / (3 * ei(lap) * span)}
    out["joint, lap with a rib splice"] = {"EI": ei(lap + ribs), "sag_mm": p * a ** 2 * b ** 2 / (3 * ei(lap + ribs) * span)}
    out["load_N"] = p
    out["rib_h"], out["foot_h"] = rib_h, rib_h + 6.0
    return out


HAND_W = 80.0  # ESTIMATED: the width of four fingers in a hand-hold


def hand_holds(total_kg: float, com_y: float, d: Blueprint) -> dict:
    """The lift that the owner chose (2026-11-11): one person lifts the back by the two hand-holds, and the cabinet
    pivots on the front bottom edge of the deck (y 0, on the table). Moments about that edge: the hand-holds carry
    W com_y / y_grip, the edge the rest. A factor of 2 for a jerk gives the design load in each recess.

    The fingers pull up on the roof of the recess (the hook). The roof is a plate of wall_t that falls 45 degrees
    from its rim on the rear wall to the back wall of the recess, between the two ends. Hand estimates for the
    design load f in one recess:
      roof plate      the roof on its four edges, f at its middle (plate_deflection)
      roof strip      a strip of the roof as wide as the hand, from the rim to the back wall, f at mid span:
                      M = f s / 4, stress = M / (HAND_W t^2 / 6)
      roof edges      shear where the roof joins the rear wall and the back wall: f / (2 span t)
      wall above      the wall between the rim and the body top (less the seam groove) as a beam with fixed ends that
                      takes half of f along the rim: M = (f / 2) span / 12, stress = M / (t h^2 / 6)
      straight lift   the same four numbers for the whole weight on the two recesses with the factor of 2 (a lift
                      with no pivot): the load in each recess is then the weight
    """
    w = total_kg * G
    x0, x1, y0, y1, z0, z1 = grip_box(d)
    grip_y = (y0 + y1) / 2
    lift = w * com_y / grip_y
    t, span = d.wall_t, x1 - x0
    slope = d.grip_depth * math.sqrt(2)
    above = d.body_top - d.seam_groove - z1

    def loads(f: float) -> dict:
        return {"load_N": f, "roof_plate_mm": plate_deflection(f, slope, span, t, E_PETG),
                "roof_strip_MPa": (f * slope / 4) / (HAND_W * t ** 2 / 6), "roof_edge_shear_MPa": f / (2 * span * t),
                "wall_above_MPa": (f / 2 * span / 12) / (t * above ** 2 / 6)}

    return {"weight_N": w, "com_y": com_y, "grip_y": grip_y, "pivot": "the front bottom edge of the deck, y 0, on the table",
            "lift_N": lift, "each_N": lift / 2, "each_design_N": lift, "edge_N": w - lift,
            "roof_span": span, "roof_slope": slope, "wall_above": above, "hand_w": HAND_W, "yield_MPa": YIELD_MPA,
            "pivot_lift": loads(lift), "straight_lift": loads(w), "grip": (x0, x1, y0, y1, z0, z1)}


# seam, the joint, what locates it, the directions it fixes (n: square to the seam; t: across the wall, so that the
# faces lie flush; s: along the seam)
ALIGNMENT = (
    ("floor tiles (BA1 to BA3)", "2", "cones in the half-laps", "n, t, s"),
    ("wall feet to the floor", "3", "a key under each foot flange in a slot of the floor; the floor is the datum", "n, t, s"),
    ("D1 (deck to body, under the panel)", "1", "flange key; one cone at each end of the seam", "n, t, s"),
    ("D2 (deck to body, at the sweep foot)", "1", "flange key; a cone at the deck's top corner", "n, t, s"),
    ("F1, F2 (deck nose at the flank break)", "1", "flange key down the front and across the border; a cone at the top", "n, t, s"),
    ("P1 (apron at the panel corners)", "1", "flange key; one cone near the bezel edge", "n, t, s"),
    ("S1 (front to rear body, in the band's crease)", "1", "flange key; node 4 with L1", "n, t, s"),
    ("L1 (level at the bezel's bottom corner, and at the door sill behind the band)", "1 and 4", "flange key round the ring; nodes with S1, P1 and the door sill", "n, t, s"),
    ("B1 (belt in the crease of the rear shelf)", "1 and 4", "flange key round the ring; nodes with R1 and W1", "n, t, s"),
    ("R1 (rear, door corner to the crease)", "1", "flange key; node with B1", "n, t; s from the node"),
    ("R2 (rear wall below the door, centre)", "1", "flange key; one cone", "n, t, s"),
    ("R3 (upper rear, on the line of the door's side)", "1", "flange key; node with B1", "n, t, s"),
    ("R4 (the door's centre)", "1", "flange key; one cone; the door is bonded apart from the cabinet, on a flat table", "n, t, s"),
    ("R5 (upper rear, centre)", "1", "flange key; a cone at the top ring", "n, t, s"),
    ("W1 (brow beside the hood bay)", "1", "flange key; a cone at the top ring", "n, t, s"),
    ("H1 (hood bays)", "1", "flange key; a cone at the roof and one at the sill", "n, t, s"),
    ("hood on the body top (groove)", "7", "two cones at the front and two at the rear corners of the top ring", "n, t, s"),
    ("rear door (DR)", "5", "two pins and a lip on the sill", "n, t, s"),
    ("bezel plate (reveal)", "5", "two pins in the bottom ledge; magnets on the fixed cradle; the lip on the bottom ledge", "n, t, s"),
    ("control panel (pocket)", "5", "the pocket's six edges and two pins at the front", "n, t, s"),
)

ABS_CHANGES = (
    ("bond", "slow methacrylate (MMA) on the flange", "acetone or ABS slurry welds the flange; joints near the strength of one part in two studies"),
    ("groove", "polyester glazing putty that lists plastics; optional PETG weld", "ABS slurry or a polyester putty that names ABS on its data sheet"),
    ("sanding", "wet only (PETG gums dry)", "wet or dry"),
    ("primer and lacquer", "scuff and prime every face; hobby lacquer only over primer", "1K plastic primers name ABS; hobby lacquers grip it, but thinners crack stressed ABS"),
    ("shrink", "0.76 % and 0.54 % in X and Y (one study)", "0.59 % and 0.69 % in X and Y, 0.92 % growth in Z (same study): the clearances stay; warp, not shrink, decides"),
    ("printer", "the A1", "an enclosed printer with a chamber, a vent to outdoors; flat floor tiles may warp"),
)
