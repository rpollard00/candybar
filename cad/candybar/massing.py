from __future__ import annotations

from .model import ZERO, Assembly, Model, box, tag

OWNER = "Shell"
PROFILE = "Shell_Profile"
ROLE = "massing"

# The side silhouette on the global YZ plane: sketch x is global Y, sketch y is global Z.
PROFILE_CORNERS = (
    ("front_foot", ZERO, "foot_h"),
    ("panel_front", ZERO, "cp_top_z"),
    ("bezel_foot", "bezel_foot_y", "cp_top_z"),
    ("bezel_top", "bezel_top_y", "bezel_top_z"),
    ("hood_lip", "hood_lip_y", "bezel_top_z"),
    ("roof_front", "top_front_y", "cab_h"),
    ("roof_rear", "cab_d", "cab_h"),
    ("rear_foot", "cab_d", "foot_h"),
)

SIDES = (("Shell_SideL", "-outer_w / 2"), ("Shell_SideR", "inner_w / 2"))

INNER_LEFT = "-inner_w / 2"
FLOOR_TOP = "foot_h + floor_t"

BOXES = (
    box("Shell_Floor", ROLE, ("outer_w", "cab_d", "floor_t"), ("-outer_w / 2", ZERO, "foot_h")),
    box("Shell_Rear", ROLE, ("inner_w", "rear_t", "cab_h - foot_h - floor_t"), (INNER_LEFT, "rear_inner_y", FLOOR_TOP)),
    box("Shell_Front", ROLE, ("inner_w", "front_t", "cp_inner_h"), (INNER_LEFT, ZERO, FLOOR_TOP)),
    box("Shell_Shelf", ROLE, ("inner_w", "shelf_depth", "deck_t"), (INNER_LEFT, "cp_depth", "cp_top_z - deck_t")),
    box("Shell_Roof", ROLE, ("inner_w", "cab_d - top_front_y", "rear_t"), (INNER_LEFT, "top_front_y", "cab_h - rear_t")),
)

# Local frame of the bezel: x from the left inner wall, y back from the bezel
# front plane, z up the slope from the shelf.
BEZEL = Assembly("Bezel", base=(INNER_LEFT, "bezel_foot_y", "cp_top_z"), axis=(-1.0, 0.0, 0.0), angle="recline")
BEZEL_PLATE = box("Shell_Bezel_Plate", "", ("inner_w", "mon_setback", "bezel_len"), (ZERO, ZERO, ZERO))
BEZEL_WINDOW = box(
    "Shell_Bezel_Window",
    "",
    ("mon_active_w", "mon_setback", "mon_active_h"),
    ("(inner_w - mon_active_w) / 2", ZERO, "mon_chin + mon_bezel_bottom"),
)


def build(model: Model) -> None:
    shell = model.assembly(Assembly(OWNER, base=(ZERO, ZERO, ZERO), prims=BOXES))
    profile = model.sketch(shell, PROFILE, "YZ_Plane")
    profile.polygon(PROFILE_CORNERS)
    for name, x in SIDES:
        tag(model.extrusion(shell, name, profile, "side_t", (x, ZERO, ZERO)), ROLE, OWNER)
    bezel = model.assembly(BEZEL, parent=shell)
    plate = model.solid(bezel, BEZEL_PLATE, OWNER)
    window = model.solid(bezel, BEZEL_WINDOW, OWNER)
    tag(model.cut(bezel, "Shell_Bezel", plate, window), ROLE, OWNER)
