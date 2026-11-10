"""Control panel: lever, buttons, encoder, and the two printable deck tiles.

Local frame: x from the panel centre line, y from the panel front edge toward
the rear, z up from the panel top face. The deck occupies z from -deck_t to 0.
"""
from __future__ import annotations

from dataclasses import dataclass

import FreeCAD as App

from .model import ZERO, Assembly, Model, Prim, Side, ball, box, cyl

OWNER = "ControlPanel"
ACTION_NUT = "action_nut"
SERVICE_NUT = "service_nut"
BUTTON_COUNTS = (6, 8)
SERVICE_COUNT = 3

LEVER_X = "stick_x"
LEVER_Y = "stick_y"
PLATE_Z = "-stick_plate_drop"
BODY_BOTTOM_Z = "-stick_plate_drop - stick_body_depth"

Hole = tuple[str, str, str, str]


@dataclass(frozen=True)
class Button:
    name: str
    x: str
    y: str
    hole_d: str
    rim_d: str
    body_d: str
    nut_d: str
    nut_h: str
    depth: str
    nut_tag: str

    def prims(self) -> tuple[Prim, ...]:
        centre = (self.x, self.y)
        return (
            cyl(f"{self.name}_Cap", "protrusion", self.rim_d, "btn_rim_h", (*centre, ZERO)),
            cyl(f"{self.name}_Body", "hardware", self.body_d, self.depth, (*centre, f"-{self.depth}")),
            cyl(f"{self.name}_Nut", "hardware", self.nut_d, self.nut_h, (*centre, f"-deck_t - {self.nut_h}"), self.nut_tag),
            cyl(f"{self.name}_Wiring", "keepout", self.hole_d, "btn_wire_clear", (*centre, f"-{self.depth} - btn_wire_clear")),
        )

    def hole(self) -> Hole:
        return (self.name.lower(), self.x, self.y, self.hole_d)


def buttons(action_count: int) -> tuple[Button, ...]:
    action = tuple(
        Button(
            f"Btn{i}",
            f"stick_x + btn{i}_dx",
            f"stick_y + btn{i}_dy",
            "btn_hole_d",
            "btn_rim_d",
            "btn_body_d",
            "btn_nut_d",
            "btn_nut_h",
            "btn_depth",
            ACTION_NUT,
        )
        for i in range(1, action_count + 1)
    )
    service = tuple(
        Button(
            f"Svc{j}",
            f"svc{j}_x",
            "svc_y",
            "svc_hole_d",
            "svc_rim_d",
            "svc_body_d",
            "svc_nut_d",
            "svc_nut_h",
            "svc_depth",
            SERVICE_NUT,
        )
        for j in range(1, SERVICE_COUNT + 1)
    )
    return action + service


LEVER = (
    box(
        "Lever_Plate",
        "hardware",
        ("stick_plate_w", "stick_plate_l", "stick_plate_t"),
        ("stick_x - stick_plate_w / 2", "stick_y - stick_plate_l / 2", "-stick_plate_drop - stick_plate_t"),
    ),
    box(
        "Lever_Body",
        "hardware",
        ("stick_body_w", "stick_body_l", "stick_body_depth - stick_plate_t"),
        ("stick_x - stick_body_w / 2", "stick_y - stick_body_l / 2", BODY_BOTTOM_Z),
    ),
    cyl(
        "Lever_Tip",
        "hardware",
        "stick_tip_d",
        "stick_tip_depth - stick_body_depth",
        (LEVER_X, LEVER_Y, "-stick_plate_drop - stick_tip_depth"),
    ),
    cyl("Lever_Shaft", "protrusion", "stick_shaft_d", "stick_ball_cz + stick_plate_drop", (LEVER_X, LEVER_Y, PLATE_Z)),
    ball("Lever_Ball", "protrusion", "stick_ball_d", (LEVER_X, LEVER_Y, "stick_ball_cz")),
    box(
        "Lever_Harness",
        "keepout",
        ("stick_conn_clear", "40 mm", "stick_body_depth"),
        ("stick_x - stick_body_w / 2 - stick_conn_clear", "stick_y - 20 mm", BODY_BOTTOM_Z),
    ),
)

ENCODER = box(
    "Encoder_Board",
    "hardware",
    ("enc_w", "enc_l", "enc_h"),
    ("enc_x - enc_w / 2", "enc_y - enc_l / 2", "-deck_t - enc_standoff - enc_h"),
)

BOSSES = tuple(
    (f"boss_{row}{side}", f"stick_x {x_sign} stick_mount_w / 2", f"stick_y {y_sign} stick_mount_l / 2")
    for row, y_sign in (("front", "-"), ("rear", "+"))
    for side, x_sign in (("_left", "-"), ("_right", "+"))
)


def _fix_holes(x: str) -> tuple[Hole, ...]:
    return (
        ("fix_front", x, "panel_fix_inset", "panel_fix_d"),
        ("fix_rear", x, "panel_d - panel_fix_inset", "panel_fix_d"),
    )


def build(model: Model, action_count: int) -> None:
    fitted = buttons(action_count)
    prims = (*LEVER, *(prim for button in fitted for prim in button.prims()), ENCODER)
    part = model.assembly(Assembly(OWNER, base=(ZERO, "panel_y0", "cp_top_z"), prims=prims))
    _deck_lever(model, part)
    _deck_buttons(model, part, tuple(button.hole() for button in fitted))


def _deck_lever(model: Model, part: App.DocumentObject) -> None:
    name = "Deck_Lever"
    body = _plate(model, part, name, "-panel_w / 2", "seam_x - seam_gap / 2")
    bosses = model.sketch(body, f"{name}_BossSketch", "XY_Plane")
    for label, x, y in BOSSES:
        bosses.circle(label, x, y, "stick_boss_d")
    model.pad(body, f"{name}_Bosses", bosses, "stick_plate_drop", Side.AGAINST_NORMAL)
    shaft: Hole = ("shaft", LEVER_X, LEVER_Y, "stick_shaft_hole_d")
    _through_holes(model, body, name, (shaft, *_fix_holes("-panel_w / 2 + panel_fix_inset")))
    inserts = model.sketch(body, f"{name}_InsertSketch", "XY_Plane", offset=PLATE_Z)
    for label, x, y in BOSSES:
        inserts.circle(label, x, y, "stick_insert_d")
    # The sketch lies on the boss faces and its normal points up, into the bosses.
    model.pocket(body, f"{name}_Inserts", inserts, "stick_insert_depth", Side.ALONG_NORMAL)


def _deck_buttons(model: Model, part: App.DocumentObject, button_holes: tuple[Hole, ...]) -> None:
    name = "Deck_Buttons"
    body = _plate(model, part, name, "seam_x + seam_gap / 2", "panel_w / 2")
    _through_holes(model, body, name, (*button_holes, *_fix_holes("panel_w / 2 - panel_fix_inset")))


def _plate(model: Model, part: App.DocumentObject, name: str, x0: str, x1: str) -> App.DocumentObject:
    body = model.body(part, name, OWNER)
    outline = model.sketch(body, f"{name}_OutlineSketch", "XY_Plane")
    outline.rectangle(x0, x1, ZERO, "panel_d")
    model.pad(body, f"{name}_Plate", outline, "deck_t", Side.AGAINST_NORMAL)
    return body


def _through_holes(model: Model, body: App.DocumentObject, name: str, holes: tuple[Hole, ...]) -> None:
    sketch = model.sketch(body, f"{name}_HoleSketch", "XY_Plane")
    for label, x, y, diameter in holes:
        sketch.circle(label, x, y, diameter)
    model.pocket(body, f"{name}_Holes", sketch, None, Side.AGAINST_NORMAL)
