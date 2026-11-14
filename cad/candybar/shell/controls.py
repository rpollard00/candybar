"""The controls of the arcade panel: the envelopes and the keep-out zones of the lever, the buttons and the encoder.

Local frame: x from the panel centre line, y from the panel front edge toward
the rear, z up from the panel top face. The plate occupies z from -deck_t to 0.
"""
from __future__ import annotations

from dataclasses import dataclass

from .model import ZERO, Assembly, Prim, ball, box, cyl, owned

OWNER = "ControlPanel"
ACTION_NUT = "action_nut"
SERVICE_NUT = "service_nut"
BUTTON_COUNTS = (6, 8)
SERVICE_COUNT = 3

LEVER_X = "stick_x"
LEVER_Y = "stick_y"
PLATE_Z = "-stick_plate_drop"
BODY_BOTTOM_Z = "-stick_plate_drop - stick_body_depth"

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


def action_buttons(count: int) -> tuple[Button, ...]:
    """The action buttons, each at its offset from the lever."""
    return tuple(
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
        for i in range(1, count + 1)
    )


def service_buttons() -> tuple[Button, ...]:
    """The start, coin and menu buttons: a column at the right end of the panel (svcN_x, fit_svcN_y)."""
    return tuple(
        Button(
            f"Svc{j}",
            f"svc{j}_x",
            f"fit_svc{j}_y",
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
        ("stick_conn_clear - stick_body_w / 2", "stick_conn_w", "stick_body_depth"),
        ("stick_x - stick_conn_clear", "stick_y - stick_conn_w / 2", BODY_BOTTOM_Z),
    ),
)

ENCODER = box(
    "Encoder_Board",
    "hardware",
    ("enc_w", "enc_l", "enc_h"),
    ("enc_x - enc_w / 2", "enc_y - enc_l / 2", "-deck_t - enc_standoff - enc_h"),
)


def control_panel(action_count: int) -> Assembly:
    """The lever, the action buttons, the service buttons and the encoder, in the frame of the panel."""
    fitted = action_buttons(action_count) + service_buttons()
    prims = (*owned("Lever", LEVER), *(p for b in fitted for p in owned(b.name, b.prims())), *owned("Encoder", (ENCODER,)))
    return Assembly(OWNER, base=(ZERO, "panel_y0", "cp_top_z"), prims=prims)
