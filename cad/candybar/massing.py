"""The cabinet shell: one styled massing solid, and the trim plates in its bezel and hood.

The outer form is the common of three extruded silhouettes, seen from the
side, the front and above. Every corner and radius of those silhouettes is a
sketch dimension bound to the parameter sheet, so no fillet refers to an edge
of a boolean result. It is massing, not a set of printable parts.
"""
from __future__ import annotations

import FreeCAD as App

from .model import ORIGIN, X_AXIS, Y_AXIS, Z_AXIS, ZERO, Assembly, Corner, Model, Pose, box, leaning_back, tag

OWNER = "Shell"
ENVELOPE = "Shell_Envelope"
SKIN = "Shell_Skin"

DECK_LEFT = "-deck_w / 2"

# Sketch x is global Y, sketch y is global Z.
SIDE_PROFILE = (
    Corner("deck_foot", "deck_facet_in", "foot_h"),
    Corner("deck_facet", ZERO, "foot_h + deck_facet_h"),
    Corner("deck_front", ZERO, "cp_top_z", "deck_edge_r"),
    Corner("cheek_foot", "cheek_foot_y", "cp_top_z", "sweep_r"),
    Corner("cheek_top", "cheek_top_y", "bezel_top_z"),
    Corner("hood_lip", "hood_lip_y", "bezel_top_z"),
    Corner("hood_top", "hood_top_y", "cab_h", "hood_r"),
    Corner("roof_rear", "cab_d", "cab_h"),
    Corner("rear_foot", "cab_d", "foot_h"),
)

# Sketch x is global X, sketch y is global Z. The right half, going up; the left half mirrors it.
FRONT_RIGHT = (
    Corner("deck_foot", "deck_w / 2 - deck_facet_in", "foot_h"),
    Corner("deck_facet", "deck_w / 2", "foot_h + deck_facet_h"),
    Corner("deck_edge", "deck_w / 2", "cp_top_z", "deck_edge_r"),
    Corner("flare", "outer_w / 2", "cp_top_z", "flare_r"),
    Corner("hood_corner", "outer_w / 2 - body_taper", "cab_h", "hood_corner_r"),
)
# The inside stays straight while the outside tapers, so the side wall thins toward the roof
# and the monitor's plug zones keep their room.
FRONT_INNER_RIGHT = (
    Corner("floor", "inner_w / 2", "foot_h"),
    Corner("roof", "inner_w / 2", "cab_h - skin_t", "hood_corner_r - side_t + body_taper"),
)

# Sketch x is global X, sketch y is global Y. The right half, front to rear; the left half mirrors it.
# The wide deck is a tray at the front; behind it the body goes down to the table at its own width.
PLAN_RIGHT = (
    Corner("deck_front", "deck_w / 2", ZERO, "deck_corner_r"),
    Corner("deck_rear", "deck_w / 2", "deck_end_y", "deck_rear_r"),
    Corner("deck_return", "outer_w / 2", "deck_end_y", "deck_return_r"),
    Corner("body_rear", "outer_w / 2", "cab_d"),
)

FACE_REACH = "150 mm"


def _in_front_of_bezel_plane(foot_y: str, foot_z: str) -> tuple[Corner, ...]:
    """The slab of space in front of the bezel plane, from a line across the screen face up to the hood.

    Sketch x is global Y, sketch y is global Z.
    """
    return (
        Corner("foot", foot_y, foot_z),
        Corner("top", "bezel_top_y", "bezel_top_z"),
        Corner("top_front", f"bezel_top_y - {FACE_REACH}", "bezel_top_z"),
        Corner("foot_front", f"{foot_y} - {FACE_REACH}", foot_z),
    )


# The screen face has two bands. The apron, from the shelf up, is body at the level of the cheeks.
# Above it the bezel plate sits in a recess between the cheeks.
RECESS_PROFILE = _in_front_of_bezel_plane("bezel_y0", "bezel_z0")
# Nothing in front of the bezel plane is hollow, from the deck top up: that is the apron and the cheeks.
FACE_PROFILE = _in_front_of_bezel_plane("bezel_foot_y", "cp_top_z")

# Tools cut 1 mm past both faces of a wall, so that no cut ends on a face of the solid it cuts.
OPENINGS = (
    box(
        "Shell_PanelOpening",
        "",
        ("panel_w + 2 * panel_gap", "panel_d + 2 * panel_gap", "skin_t + 2 mm"),
        ("-panel_w / 2 - panel_gap", "panel_y0 - panel_gap", "cp_top_z - skin_t - 1 mm"),
    ),
    box("Shell_PsuCutout", "", ("psu_w", "rear_t + 2 mm", "psu_h"), ("psu_x0", "rear_inner_y - 1 mm", "psu_z0")),
    box(
        "Shell_FanIntake",
        "",
        ("fan_frame", "rear_t + 2 mm", "fan_frame"),
        ("vent_fan_x - fan_frame / 2", "rear_inner_y - 1 mm", "vent_fan_z - fan_frame / 2"),
    ),
    box(
        "Shell_ExhaustVent",
        "",
        ("vent_out_w", "rear_t + 2 mm", "vent_out_h"),
        ("vent_out_x0", "rear_inner_y - 1 mm", "vent_out_z0"),
    ),
)

# The hood face frame: x across from the centre line, y into the hood, z up the face from the hood lip.
HOOD_BASE = (ZERO, "hood_lip_y", "bezel_top_z")
HOOD_TILT = "hood_tilt"
# name, left edge, width, lower edge, height: on the hood face, x across and z up it.
HOOD_PLATES = (
    ("Hood_Marquee", "-marquee_w / 2", "marquee_w", "hood_band_z0", "marquee_h"),
    ("Hood_SpeakerL", "-marquee_w / 2 - spk_gap - spk_w", "spk_w", "hood_band_z0", "spk_h"),
    ("Hood_SpeakerR", "marquee_w / 2 + spk_gap", "spk_w", "hood_band_z0", "spk_h"),
    ("Hood_Strip", "-strip_w / 2", "strip_w", "strip_z0", "strip_h"),
)
HOOD_FACE = Assembly(
    "HoodFace",
    base=HOOD_BASE,
    pose=leaning_back(HOOD_TILT),
    prims=tuple(box(name, "trim", (width, "skin_t", height), (x0, ZERO, z0)) for name, x0, width, z0, height in HOOD_PLATES),
)
# The same face as a sketch plane: sketch x across, sketch y up the face.
HOOD_FACE_AS_SKETCH = Pose(X_AXIS, f"90 deg - {HOOD_TILT}")
# The cutting slab is centred on the face: half of this is in front of it, half goes through the wall.
HOOD_CUT_THROUGH = "2 * skin_t + 4 mm"

# The bezel frame: x from the plate's left edge, y back from the bezel front plane, z up the slope
# from the plate's bottom edge at the top of the apron.
BEZEL = Assembly("Bezel", base=("-bezel_w / 2", "bezel_y0", "bezel_z0"), pose=leaning_back("recline"))
# name, window width, window height, is an alternate to the first.
BEZEL_PLATES = (
    ("Bezel_16x9", "mon_active_w", "win169_h", False),
    ("Bezel_16x10", "mon_active_w", "mon_active_h", True),
    ("Bezel_4x3", "win43_w", "mon_active_h", True),
    ("Bezel_Tate", "wintate_w", "mon_active_h", True),
)


def build(model: Model) -> None:
    shell = model.assembly(Assembly(OWNER, base=ORIGIN))
    side = _outline(model, shell, "Shell_SideProfile", "YZ_Plane", SIDE_PROFILE)
    plan = _outline(model, shell, "Shell_PlanProfile", "XY_Plane", _mirrored(PLAN_RIGHT))
    envelope = _envelope(model, shell, side, plan)
    cavity = _cavity(model, shell, side, plan)
    openings = [model.solid(shell, opening, OWNER) for opening in OPENINGS]
    voids = model.fuse(shell, "Shell_Voids", [cavity, *openings, _hood_openings(model, shell)])
    tag(model.cut(shell, SKIN, envelope, voids), "massing", OWNER)
    model.assembly(HOOD_FACE, parent=shell)
    _bezel_plates(model, shell)


def _outline(model: Model, shell: App.DocumentObject, name: str, plane: str, corners: tuple[Corner, ...]) -> App.DocumentObject:
    sketch = model.sketch(shell, name, plane)
    sketch.polygon(corners)
    return sketch.obj


def _mirrored(right: tuple[Corner, ...]) -> tuple[Corner, ...]:
    """A closed outline symmetric about x = 0: the right half as given, then its mirror image in reverse."""
    left = tuple(Corner(f"left_{corner.name}", f"-({corner.x})", corner.y, corner.radius) for corner in reversed(right))
    return right + left


def _across_deck(model: Model, shell: App.DocumentObject, name: str, outline: App.DocumentObject) -> App.DocumentObject:
    return model.extrusion(shell, name, outline, X_AXIS, "deck_w", (DECK_LEFT, ZERO, ZERO))


def _envelope(model: Model, shell: App.DocumentObject, side: App.DocumentObject, plan: App.DocumentObject) -> App.DocumentObject:
    """The outer form, less the recess for the bezel plate. Hardware and trim must stay inside it."""
    front = _outline(model, shell, "Shell_FrontProfile", "XZ_Plane", _mirrored(FRONT_RIGHT))
    silhouettes = (
        _across_deck(model, shell, "Shell_SideSolid", side),
        model.extrusion(shell, "Shell_FrontSolid", front, Y_AXIS, "cab_d"),
        model.extrusion(shell, "Shell_PlanSolid", plan, Z_AXIS, "cab_h"),
    )
    outer = model.common(shell, "Shell_Outer", silhouettes)
    recess = _outline(model, shell, "Shell_RecessProfile", "YZ_Plane", RECESS_PROFILE)
    between_cheeks = model.extrusion(shell, "Shell_Recess", recess, X_AXIS, "bezel_w", ("-bezel_w / 2", ZERO, ZERO))
    return model.cut(shell, ENVELOPE, outer, between_cheeks)


def _cavity(model: Model, shell: App.DocumentObject, side: App.DocumentObject, plan: App.DocumentObject) -> App.DocumentObject:
    """The hollow inside: the silhouettes moved inward by the wall thickness, and nothing in front of the bezel plane."""
    front = _outline(model, shell, "Shell_FrontInner", "XZ_Plane", _mirrored(FRONT_INNER_RIGHT))
    side_inner = model.offset(shell, "Shell_SideInner", side, "-skin_t")
    plan_inner = model.offset(shell, "Shell_PlanInner", plan, "-skin_t")
    silhouettes = (
        _across_deck(model, shell, "Shell_SideInnerSolid", side_inner),
        model.extrusion(shell, "Shell_FrontInnerSolid", front, Y_AXIS, "cab_d"),
        model.extrusion(shell, "Shell_PlanInnerSolid", plan_inner, Z_AXIS, "cab_h"),
    )
    block = model.common(shell, "Shell_CavityBlock", silhouettes)
    face = _outline(model, shell, "Shell_FaceProfile", "YZ_Plane", FACE_PROFILE)
    return model.cut(shell, "Shell_Cavity", block, _across_deck(model, shell, "Shell_FaceSolid", face))


def _hood_openings(model: Model, shell: App.DocumentObject) -> App.DocumentObject:
    """One tool through the hood face for all the plates set into it."""
    sketch = model.posed_sketch(shell, "Shell_HoodOpeningSketch", HOOD_BASE, HOOD_FACE_AS_SKETCH)
    for name, x0, width, z0, height in HOOD_PLATES:
        sketch.rectangle(x0, f"{x0} + {width}", z0, f"{z0} + {height}", name=f"{name}_")
    return model.slab(shell, "Shell_HoodOpenings", sketch.obj, HOOD_CUT_THROUGH)


def _bezel_plates(model: Model, shell: App.DocumentObject) -> None:
    bezel = model.assembly(BEZEL, parent=shell)
    for name, window_w, window_h, alternate in BEZEL_PLATES:
        plate = model.solid(bezel, box(f"{name}_Plate", "", ("bezel_w", "mon_setback", "bezel_len"), ORIGIN), OWNER)
        window = model.solid(
            bezel,
            box(
                f"{name}_Window",
                "",
                (window_w, "mon_setback + 2 mm", window_h),
                (f"(bezel_w - {window_w}) / 2", "-1 mm", f"win_cz - {window_h} / 2"),
            ),
            OWNER,
        )
        tag(model.cut(bezel, name, plate, window), "trim", BEZEL.name, alternate=alternate)
