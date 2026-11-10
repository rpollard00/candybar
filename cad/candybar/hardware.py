from __future__ import annotations

from .model import ORIGIN, X_AXIS, ZERO, Assembly, Model, Pose, box, leaning_back

# Local frame: x across the screen from its left edge, y from the front glass
# toward the back, z up the screen from its bottom edge.
MONITOR = Assembly(
    "Monitor",
    base=("-mon_w / 2", "mon_bottom_y", "mon_bottom_z"),
    pose=leaning_back("recline"),
    prims=(
        box("Monitor_Body", "hardware", ("mon_w", "mon_t", "mon_h"), ORIGIN),
        box("Monitor_Cradle", "keepout", ("mon_w", "cradle_t", "mon_h"), (ZERO, "mon_t", ZERO)),
        box(
            "Monitor_Plugs",
            "keepout",
            ("mon_side_clear", "mon_t", "mon_port_z_hi - mon_port_z_lo"),
            ("-mon_side_clear", ZERO, "mon_port_z_lo"),
        ),
        box(
            "Monitor_Controls",
            "keepout",
            ("mon_side_clear", "mon_t", "mon_ctrl_z_hi - mon_ctrl_z_lo"),
            ("mon_w", ZERO, "mon_ctrl_z_lo"),
        ),
    ),
)

# The board stands on its stepped long edge with its straight long edge on top:
# local y points down, and local z, the heatsink side, points at the rear door.
ON_LONG_EDGE_HEATSINK_TO_REAR = Pose(X_AXIS, -90.0)

# Local frame is the board datum: x from the I/O edge toward the power end, y
# from the straight long edge toward the stepped edge, z up from the PCB top
# face toward the heatsink.
COMPUTE = Assembly(
    "Compute",
    base=("bc_x0", "bc_pcb_y", "bc_top_z"),
    pose=ON_LONG_EDGE_HEATSINK_TO_REAR,
    prims=(
        box("Compute_PCB_IO", "hardware", ("bc_pcb_step_x", "bc_pcb_w_io", "bc_pcb_t"), (ZERO, ZERO, "-bc_pcb_t")),
        box(
            "Compute_PCB_Pwr",
            "hardware",
            ("bc_pcb_l - bc_pcb_step_x", "bc_pcb_w_pwr", "bc_pcb_t"),
            ("bc_pcb_step_x", ZERO, "-bc_pcb_t"),
        ),
        box(
            "Compute_Backplate",
            "hardware",
            ("bc_pcb_l", "bc_pcb_w_io", "bc_backplate_drop - bc_pcb_t"),
            (ZERO, ZERO, "-bc_backplate_drop"),
        ),
        box("Compute_Heatsink", "hardware", ("bc_fin_l", "bc_fin_w", "bc_fin_h"), ("bc_fin_x0", "bc_fin_y0", ZERO)),
        box(
            "Compute_IO",
            "hardware",
            ("bc_fin_x0 + bc_io_overhang", "bc_pcb_w_io", "bc_io_h"),
            ("-bc_io_overhang", ZERO, ZERO),
        ),
        box(
            "Compute_FanShroud",
            "hardware",
            ("bc_shroud_l", "bc_shroud_w", "bc_shroud_h - bc_fin_h"),
            ("bc_shroud_x0", "bc_shroud_y0", "bc_fin_h"),
        ),
        box(
            "Compute_DPPlug",
            "keepout",
            ("bc_dp_clear", "bc_pcb_w_io", "bc_io_h"),
            ("-bc_io_overhang - bc_dp_clear", ZERO, ZERO),
        ),
        box(
            "Compute_PowerPlug",
            "keepout",
            ("bc_pwr_x1 - bc_pwr_x0", "bc_pwr_clear", "bc_pwr_h"),
            ("bc_pwr_x0", "bc_pcb_w_pwr", ZERO),
        ),
        box(
            "Compute_UndersideAir",
            "keepout",
            ("bc_pcb_l", "bc_pcb_w_pwr", "bc_underside_gap"),
            (ZERO, ZERO, "-bc_backplate_drop - bc_underside_gap"),
        ),
    ),
)

# Local frame: x width, y depth front to rear with the bay's rear face at
# y = psu_d_max, z height.
PSU = Assembly(
    "PSU",
    base=("psu_x0", "psu_y0", "psu_z0"),
    prims=(
        box("PSU_Body", "hardware", ("psu_w", "psu_d", "psu_h"), (ZERO, "psu_d_max - psu_d", ZERO)),
        box("PSU_Bay", "keepout", ("psu_w", "psu_d_max", "psu_h"), ORIGIN),
        box("PSU_FanAir", "keepout", ("psu_w", "psu_d_max", "psu_fan_clear"), (ZERO, ZERO, "psu_h")),
        box(
            "PSU_Plugs",
            "keepout",
            ("psu_w", "psu_plug_clear", "psu_plug_h"),
            (ZERO, "-psu_plug_clear", "psu_plug_z0"),
        ),
    ),
)

CABLE_BUNDLE = Assembly(
    "CableBundle",
    base=("bundle_x0", "bundle_y0", "psu_z0"),
    prims=(box("CableBundle_Body", "hardware", ("psu_bundle_w", "psu_bundle_d", "psu_bundle_h"), ORIGIN),),
)

ASSEMBLIES = (MONITOR, COMPUTE, PSU, CABLE_BUNDLE)


def build(model: Model) -> None:
    for spec in ASSEMBLIES:
        model.assembly(spec)
