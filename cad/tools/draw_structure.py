"""The structure sheets, the sheet of cable routes and air path, the joint sheet, and the width study of the seam
proposal. draw_split.py calls these; they read what candybar.shell.split and candybar.shell.structure wrote.

    cad/.venv-tools/bin/python cad/tools/draw_split.py   (draws these too)

structure-<option>.png  a side view and a plan of the cavity with the hardware boxes of the fit study, and the
                        floor, ring frames, cross-members, ribs, frame members and mounts in colour
services.png            the cable routes and the air path, with the plugs at the parts that open
joints.png              dimensioned sections of the joints, and the coupon pair; every value from
                        candybar.shell.joints (also docs/blueprint/11-joints: draw_split.py blueprint)
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import fields

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(HERE)
sys.path.insert(0, CAD)
sys.path.insert(0, HERE)
import draw_blueprint as db  # noqa: E402
from candybar.shell import coupon as cp  # noqa: E402
from candybar.shell import joints as jt  # noqa: E402
from candybar.shell import split as sp  # noqa: E402
from candybar.shell import structure as st  # noqa: E402
from candybar.shell.dims import Blueprint  # noqa: E402

SHELL = os.path.join(CAD, "out", "shell-bp")
OUT = os.path.join(SHELL, "split")
KIND_COLOUR = {"floor": "#1f77b4", "ring": "#ff7f0e", "cross": "#2ca02c", "rib": "#9467bd", "mount": "#8c564b", "frame": "#d62728"}
LABELLED = {"Monitor_Body": "monitor", "MonitorAny_Cradle": "monitor room", "Compute_Heatsink": "BC-250", "Compute_FanShroud": "fan, shroud",
            "Compute_ExhaustDuct": "exhaust duct", "PSU_Body": "power supply", "Hub_Body": "hub", "SpeakerR_Driver": "speaker",
            "Marquee_Modules": "marquee", "Lever_Body": "lever", "CableBundle_Body": "cables", "USB_C4_Body": "USB"}


def sections() -> dict:
    return json.load(open(os.path.join(SHELL, "fit", "sections.json")))


def outline(ax, sec: dict, axes: tuple[int, int] | None = None) -> None:
    for line in sec["outer"]:
        p = np.array(line)
        ax.plot(p[:, 0], p[:, 1], color="#555", lw=0.8, zorder=2)
    for line in sec["cavity"]:
        p = np.array(line)
        ax.fill(p[:, 0], p[:, 1], color="#f4f4f4", zorder=1)
        ax.plot(p[:, 0], p[:, 1], color="#bbb", lw=0.5, zorder=2)


def items(ax, view: str, labels: bool = True) -> None:
    for it in sections()["rear"]["items"]:
        x0, z0, x1, z1 = it["box"]
        y0, y1 = it["y"]
        a, b = ((y0, z0), (y1, z1)) if view == "side" else ((x0, y0), (x1, y1))
        hard = it["role"] == "hardware"
        ax.add_patch(Rectangle(a, b[0] - a[0], b[1] - a[1], fc="#d9d9d9" if hard else "none", ec="#999", lw=0.4,
                               ls="-" if hard else (0, (2, 2)), zorder=3))
        if labels and it["solid"] in LABELLED and (view == "side" or it["solid"] not in ("SpeakerR_Driver", "Marquee_Modules")):
            ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, LABELLED[it["solid"]], fontsize=6, ha="center", va="center", color="#444", zorder=8)


def member_shapes(m: st.Member, view: str) -> list[np.ndarray]:
    sides = [False, True] if m.mirror else [False]
    out = []
    for left in sides:
        k = -1.0 if left else 1.0
        if m.box:
            x0, x1, y0, y1, z0, z1 = m.box
            if left:
                x0, x1 = -x1, -x0
            pts = [(y0, z0), (y1, z0), (y1, z1), (y0, z1)] if view == "side" else [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        else:
            (y0, z0), (y1, z1) = m.p, m.q
            n = np.array((-(z1 - z0), y1 - y0))
            n = n / np.linalg.norm(n) * m.sn / 2
            if view == "side":
                pts = [(y0 + n[0], z0 + n[1]), (y1 + n[0], z1 + n[1]), (y1 - n[0], z1 - n[1]), (y0 - n[0], z0 - n[1])]
            else:
                xa, xb = sorted((k * m.x0, k * (m.x0 + m.sx)))
                pts = [(xa, min(y0, y1)), (xb, min(y0, y1)), (xb, max(y0, y1)), (xa, max(y0, y1))]
        out.append(np.array(pts))
        if view == "side":
            break
    return out


def frame_ax(ax, title: str, xlim, ylim) -> None:
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=10)
    ax.tick_params(labelsize=6)
    ax.grid(True, color="#eee", lw=0.4, zorder=0)


def structure_sheet(key: str, opt: sp.Option, d: Blueprint) -> str:
    sec = sections()["sections"]
    members = st.frame_c(d) if key == "C" else st.skin_members(d, key)
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(24, 9), gridspec_kw={"width_ratios": [1.15, 1.0, 0.75]})
    outline(a1, sec["side, centre line"])
    items(a1, "side")
    outline(a2, sec["plan, compute module"])
    items(a2, "plan")
    seams = json.load(open(os.path.join(OUT, key, "seams.json")))
    for s in seams.values():
        if s["side"] == "L" or s["module"] != "body":
            continue
        for line in s["lines"]:
            p = np.array(line)
            a1.plot(p[:, 1], p[:, 2], color=KIND_COLOUR["ring"], lw=0.7, alpha=0.55, zorder=4)
    for m in members:
        c = KIND_COLOUR[m.kind]
        for view, ax in (("side", a1), ("plan", a2)):
            for pts in member_shapes(m, view):
                fade = 0.07 if m.kind == "floor" and view == "plan" else 0.30 if m.kind in ("ring", "floor", "rib") else 0.55
                hollow = m.kind == "rib" or (m.kind == "ring" and view == "plan")
                ax.add_patch(Polygon(pts, closed=True, fc="none" if hollow else c, ec=c, alpha=0.9 if hollow else fade,
                                     lw=1.2, ls=(0, (3, 2)) if m.kind == "rib" else "-", zorder=5))
        pts = member_shapes(m, "side")[0]
        a1.annotate(m.name, xy=pts.mean(axis=0), xytext=pts.mean(axis=0) + (0, 0), fontsize=6.3, color=c, ha="center",
                    va="center", zorder=9, bbox=dict(fc="white", ec=c, lw=0.5, pad=0.6, alpha=0.85))
    frame_ax(a1, "side (y, z): centre-line section, members projected", (-20, 620), (-20, 600))
    frame_ax(a2, f"plan (x, y): section at z {sec['plan, compute module']['at']:.0f}, members projected", (-270, 270), (-20, 600))
    a3.axis("off")
    rows = [f"{opt.title}: structure", ""]
    for kind in ("floor", "ring", "cross", "rib", "mount", "frame"):
        names = [m.name for m in members if m.kind == kind]
        if names:
            rows.append(f"{st.KIND_WORDS[kind]}: {', '.join(names)}")
    rows += ["", "mounts:"]
    for i, mt in enumerate(st.mounts(key), 1):
        rows.append(f"{i:>2}. {mt.item}: on {mt.on}")
    a3.text(0, 1, "\n".join(rows), fontsize=7.5, va="top", family="DejaVu Sans Mono", transform=a3.transAxes, wrap=True)
    for i, (kind, c) in enumerate(KIND_COLOUR.items()):
        a3.add_patch(Rectangle((0.0, 0.02 + i * 0.035), 0.05, 0.022, fc=c, alpha=0.5, transform=a3.transAxes))
        a3.text(0.07, 0.031 + i * 0.035, st.KIND_WORDS[kind], fontsize=7.5, va="center", transform=a3.transAxes)
    fig.suptitle(f"Structure of option {opt.title} (mm). Grey: hardware of the fit study; dashed: keep-out zones; light "
                 "orange lines: the bonded seams, each with an inside flange", fontsize=11)
    path = os.path.join(OUT, f"structure-{key}.png")
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return path


def arrow(ax, a, b, colour, dashed=False) -> None:
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=11, color=colour, lw=1.6, ls="--" if dashed else "-", zorder=9))


AIR_SIDE = (  # (y, z) arrows in side view
    ((610, 185), (540, 185), "#1f77b4", False, "outside air in through the fan vent"),
    ((535, 185), (500, 185), "#1f77b4", False, ""),
    ((480, 200), (480, 245), "#d62728", False, "out of the fins at the I/O end"),
    ((500, 240), (545, 225), "#d62728", False, "duct to the slot vents"),
    ((150, -12), (150, 12), "#1f77b4", False, "make-up air through the floor"),
    ((300, 40), (420, 110), "#1f77b4", False, ""),
    ((460, 60), (560, 60), "#d62728", False, "power supply out of its grille"),
)
AIR_PLAN = (  # (x, y)
    ((48, 610), (48, 540), "#1f77b4", False), ((48, 530), (48, 495), "#1f77b4", False), ((40, 480), (-150, 480), "#d62728", False),
    ((-175, 490), (-175, 560), "#d62728", False), ((-150, 380), (-150, 560), "#d62728", False), ((0, 150), (-120, 360), "#1f77b4", False),
)
PLUGS = ((56.0, 470.0, 320.0, "PCIe plug at the board + 150 loop"), (-188.0, 330.0, 215.0, "monitor plugs (right angle) + slack"),
         (-165.0, 180.0, 22.0, "panel USB plug + 200 loop"), (120.0, 470.0, 432.0, "hood plug + loop"))
DUCT_FAN = (-174.0, 130.0, 182.0, 92.0)  # x centre, z centre... (x, z, y face, size)


def services_sheet() -> str:
    sec = sections()["sections"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(22, 10))
    outline(a1, sec["side, centre line"])
    items(a1, "side")
    outline(a2, sec["plan, compute module"])
    items(a2, "plan")
    for r in st.ROUTES:
        p = np.array(r.points)
        a1.plot(p[:, 1], p[:, 2], color=r.colour, lw=2.0, zorder=7, label=r.name)
        a2.plot(p[:, 0], p[:, 1], color=r.colour, lw=2.0, zorder=7)
    for x, y, z, words in PLUGS:
        for ax, a in ((a1, (y, z)), (a2, (x, y))):
            ax.plot(*a, marker="X", ms=9, color="black", zorder=10)
        a1.annotate(words, xy=(y, z), xytext=(y - 160, z + 40), fontsize=6.5, arrowprops=dict(arrowstyle="-", lw=0.5), zorder=10,
                    bbox=dict(fc="white", ec="#333", lw=0.4, pad=0.5))
    for a, b, c, dashed, words in AIR_SIDE:
        arrow(a1, a, b, c, dashed)
        if words:
            a1.text(*a, words, fontsize=6.5, color=c, ha="left", va="bottom", zorder=10)
    for a, b, c, dashed in AIR_PLAN:
        arrow(a2, a, b, c, dashed)
    # the optional fan in the duct: 92 mm, its face in front of the slot vents
    x, z, _, size = DUCT_FAN
    a1.add_patch(Rectangle((506, z + 52 - size / 2), 25, size, fc="none", ec="#d62728", ls="--", lw=1.4, zorder=9))
    a1.text(500, z + 52 + size / 2 + 4, "option: 92 mm fan in the duct", fontsize=6.5, color="#d62728", ha="right")
    a2.add_patch(Rectangle((x - size / 2, 506), size, 25, fc="none", ec="#d62728", ls="--", lw=1.4, zorder=9))
    a2.text(x, 470, "option: 92 mm\nduct fan", fontsize=6.5, color="#d62728", ha="center")
    a1.legend(loc="upper left", fontsize=7)
    frame_ax(a1, "side (y, z): cable routes and the air path", (-20, 630), (-25, 600))
    frame_ax(a2, "plan (x, y)", (-270, 270), (-20, 630))
    fig.suptitle("Cable routes and the air path. X: a plug where a part opens for service (door, hood, control panel, "
                 "monitor carrier). Blue: cool air; red: warm air.", fontsize=11)
    path = os.path.join(OUT, "services.png")
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------- the joint sheet ----------
# Every number on this sheet comes from candybar.shell.joints (Joint for joint 1, OtherJoints for joints 2 to 7),
# from the floor of candybar.shell.structure, the coupon of candybar.shell.coupon and the groove of dims.Blueprint.

J, O = jt.JOINT, jt.OTHER_JOINTS
LOWER, UPPER = "#e8c39e", "#9ec5e8"   # the piece below the seam (key, pilots) and the piece above (groove, clearance)


def g(v: float) -> str:
    return f"{v:g}"


def box(ax, x, y, w, h, c=LOWER, hatch=None, lw=0.8, ls="-"):
    return ax.add_patch(Rectangle((x, y), w, h, fc=c, ec="#333", lw=lw, hatch=hatch, ls=ls, zorder=3))


def section(ax, pts, x0: float, fc: str, ec: str = "#333", z: int = 3, ls="-", lw: float = 0.8):
    """A profile of joints.py, (u, z) across the seam, drawn with z to the right (from x0) and u up (inward)."""
    return ax.add_patch(Polygon([(x0 + zz, uu) for uu, zz in pts], closed=True, fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))


def dim(ax, p, q, text, shift=(0, 0)) -> None:
    db.dim(ax, p, q, text, shift, size=6.0)


def note(ax, at, text, to=None) -> None:
    db.note(ax, at, text, to, size=6.0)


def pilot_words() -> str:
    """The pilot of the cabinet is open in joints.py until the coupon decides: the sheet gives both candidates."""
    if J.pilot_d is not None:
        return f"pilot {g(J.pilot_d)}"
    return f"pilot {g(J.pilot_d_pet)} (PET) or {g(J.pilot_d_abs)} (ABS): open, the coupon decides"


def bond_width() -> float:
    """The flange face beside the groove mouth, per mm of seam: what takes the adhesive."""
    a, b = J.groove_u()
    return J.flange_h - (b - a + 2 * J.groove_chamfer)


def joint_skin(ax) -> None:
    """Joint 1, from the profiles of joints.py: section A between two screws (key in its groove), section B at a screw.
    Left of each seam the piece below, right of it the piece above; up is inward from the outer face (u)."""
    w, h, t, run = J.wall_t, J.flange_h, J.flange_t, 22.0
    for x0, title in ((-30.0, "A: between screws"), (30.0, "B: at a screw")):
        for side, c in (("below", LOWER), ("above", UPPER)):
            section(ax, jt.skin_profile(J, side, run), x0, c)
            section(ax, jt.flange_profile(J, side), x0, c)
            section(ax, jt.vgroove_profile(J, side), x0, "white", ec="#d62718", z=4)
        ax.text(x0, -5.5, title, fontsize=6.5, ha="center", va="center", color="#333")
    xa, xb = -30.0, 30.0
    upper_b = section(ax, jt.flange_profile(J, "above"), xb, UPPER)
    # A: key on the piece below, groove in the piece above, adhesive on the flange faces beside the groove
    section(ax, jt.groove_profile(J, J.groove_clearance), xa, "white", z=4)
    section(ax, jt.key_profile(J), xa, LOWER, z=5)
    ga, gb = J.groove_u()
    for u0, u1 in ((w, ga - J.groove_chamfer), (gb + J.groove_chamfer, w + h)):
        ax.plot([xa, xa], [u0, u1], color="#2ca02c", lw=1.6, zorder=6)
    dim(ax, (xa - run + 3, 0), (xa - run + 3, w), g(w), (-2.5, 0))
    dim(ax, (xa - t, w + h + 2), (xa, w + h + 2), g(t), (0, 1.6))
    dim(ax, (xa, w + h + 2), (xa + t, w + h + 2), g(t), (0, 1.6))
    dim(ax, (xa - t - 2, w), (xa - t - 2, w + h), g(h), (-2.0, 0))
    note(ax, (-58, 26), f"key {g(J.key_proj)} x {g(J.key_w)}, {g(J.key_u0)} inward of the skin; groove "
         f"+{g(J.groove_clearance)} each side (the coupon sets it: {', '.join('+' + g(c) for c in cp.CLEARANCES)}), "
         f"{g(J.groove_extra_depth)} deeper than the key", (xa + 0.8, (J.key_u[0] + J.key_u[1]) / 2))
    note(ax, (-58, 22), f"green: adhesive on the flange faces beside the groove, {bond_width():g} per mm of seam, "
         f"and the {g(w)} butt", (xa, w + 1))
    note(ax, (-58, 30), f"V-groove {g(J.vgroove_w)} wide, {g(J.vgroove_d)} deep, half on each piece: takes the filler",
         (xa, J.vgroove_d / 2))
    note(ax, (-58, -10), f"{g(J.gusset_angle)} deg gusset under the level flange: prints with no support",
         (xa - t - J.gusset_leg / 2, w + h / 2))
    # B: the screw through the clearance hole of the piece above into the pilot of the piece below
    u = J.screw_u
    holes = ((-J.pilot_depth, 0.0, J.pilot_d_pet), (-J.pilot_counterbore_depth, 0.0, J.pilot_counterbore_d),
             (0.0, t, J.clearance_d), (t, t + J.gusset_leg + 1.0, J.head_pocket_d))
    for z0, z1, d in holes:
        cut = box(ax, xb + z0, u - d / 2, z1 - z0, d, "white", lw=0.6)
        if z0 >= t:
            cut.set_clip_path(upper_b)   # the head pocket cuts the gusset only
    box(ax, xb - J.pilot_depth, u - J.pilot_d_abs / 2, J.pilot_depth, J.pilot_d_abs, "none", lw=0.6, ls=(0, (2, 1.5)))
    ax.plot([xb + t - J.screw_l, xb + t], [u, u], color="#333", lw=J.screw_d * 0.9, solid_capstyle="butt", zorder=7)
    ax.plot([xb + t, xb + t], [u - J.screw_d, u + J.screw_d], color="#333", lw=2.2, zorder=7)
    dim(ax, (xb + run - 3, 0), (xb + run - 3, u), g(u), (2.5, 0))
    dim(ax, (xb - J.pilot_depth, u - 4.5), (xb, u - 4.5), g(J.pilot_depth), (0, -1.6))
    note(ax, (-10, -14), f"thread-forming screw {g(J.screw_d)} x {g(J.screw_l)} for plastics, every "
         f"{g(J.screw_pitch)}: clamps while it cures, stays in", (xb, u))
    note(ax, (-10, -18), pilot_words(), (xb - J.pilot_depth / 2, u - J.pilot_d_abs / 2))
    note(ax, (-10, -22), f"counterbore {g(J.pilot_counterbore_d)} x {g(J.pilot_counterbore_depth)}; clearance "
         f"{g(J.clearance_d)}; head pocket {g(J.head_pocket_d)}", (xb + t / 2, u + J.clearance_d / 2))
    note(ax, (-58, 34), f"the key stops {g(J.key_gap)} each side of a screw and {g(J.key_end_margin)} from a "
         "free end of the seam: section B has no key")
    ax.set_title("1  skin to skin on a wall or a curved face (sections across the seam; up: inward)", fontsize=9)


def joint_floor(ax) -> None:
    f, lap = st.FLOOR_T, O.lap_w
    half = f / 2
    box(ax, -40, 0, 40 + lap / 2, half, LOWER)
    box(ax, -40, half, 40 - lap / 2, half, LOWER)
    box(ax, -lap / 2, half, 40 + lap / 2, half, UPPER)
    box(ax, lap / 2, 0, 40 - lap / 2, half, UPPER)
    ax.add_patch(Polygon([(-O.cone_d / 2, half), (O.cone_d / 2, half), (0, half + O.cone_h)], fc=LOWER, ec="#333", lw=0.8, zorder=4))
    for x in (-lap / 4, lap / 4):
        ax.plot([x, x], [f - 1 - O.lap_screw_l, f - 1], color="#333", lw=1.4, zorder=5)
    dim(ax, (-lap / 2, f + 3), (lap / 2, f + 3), f"half-lap {g(lap)}", (0, 3))
    dim(ax, (44, 0), (44, f), g(f), (4, 0))
    note(ax, (-40, 18), f"cone {g(O.cone_d)} dia x {g(O.cone_h)} in the lower lap, socket +{g(O.cone_clearance)} in the "
         "upper: locates", (0, half + 1))
    note(ax, (-40, 23), f"thread-forming {g(O.base_screw_d)} x {g(O.lap_screw_l)} from below, every "
         f"{g(O.lap_screw_pitch)}; adhesive on the {g(lap)} lap", (-lap / 4, -4))
    note(ax, (12, -12), f"sandwich: skins {g(st.FLOOR_SKIN)}, gyroid core {st.FLOOR_INFILL * 100:.0f} %", (25, 2))
    ax.set_title(f"2  floor tile to floor tile (printed floor, {g(f)} thick)", fontsize=9)


def joint_foot(ax) -> None:
    f, w = st.FLOOR_T, J.wall_t
    x_out = 34.0
    box(ax, -30, 0, 60, f, UPPER)                                   # floor tile
    box(ax, x_out - w, 0, w, 60, LOWER)                             # wall, outside at x_out
    box(ax, x_out - w - J.foot_h, f, J.foot_h, J.foot_t, LOWER)     # foot flange on the floor
    kx = x_out - w - J.foot_h / 2 - O.foot_key_w / 2
    box(ax, kx, f - O.foot_key_h, O.foot_key_w, O.foot_key_h, LOWER)  # key under the flange, in a slot of the floor
    sx = x_out - w - J.foot_h / 2 + O.foot_key_w
    ax.plot([sx, sx], [f + J.foot_t - O.foot_screw_l, f + J.foot_t], color="#333", lw=1.4, zorder=5)
    dim(ax, (x_out - w - J.foot_h, f + J.foot_t + 3), (x_out - w, f + J.foot_t + 3), f"{g(J.foot_h)} x {g(J.foot_t)}", (0, 3))
    dim(ax, (-34, 0), (-34, f), g(f), (-4, 0))
    note(ax, (-30, 30), "the wall stands on the desk outside the floor; its foot flange lies on the floor", (x_out - w - 6, f + J.foot_t))
    note(ax, (-30, 36), f"key {g(O.foot_key_w)} x {g(O.foot_key_h)} under the flange into a slot in the floor: locates",
         (kx + O.foot_key_w / 2, f - O.foot_key_h / 2))
    note(ax, (-30, 42), f"thread-forming {g(O.base_screw_d)} x {g(O.foot_screw_l)} up from below every "
         f"{g(O.foot_screw_pitch)}; adhesive on the flange", (sx, 2))
    ax.set_title("3  wall foot to floor", fontsize=9)


def joint_node(ax) -> None:
    p, fw = O.node_plate, 2 * J.flange_t
    box(ax, -30, -fw / 2, 60, fw, LOWER)          # the flanges of the level seam, seen from inside
    box(ax, -fw / 2, fw / 2, fw, 30 - fw / 2, UPPER)
    box(ax, -fw / 2, -30, fw, 30 - fw / 2, "#b9dea0")
    box(ax, -p / 2, -p / 2, p, p, "#f2e3a0", lw=1.2)
    for c in ((-p / 4, -p / 4), (p / 4, -p / 4), (-p / 4, p / 4), (p / 4, p / 4)):
        ax.add_patch(plt.Circle(c, O.cone_d / 2, fc="white", ec="#333", lw=0.8, zorder=6))
    note(ax, (-30, 38), f"node plate {g(p)} x {g(p)} x {g(O.node_plate_t)}, bonded inside over the three flanges", (0, p / 2))
    note(ax, (-30, 44), f"cone {g(O.cone_d)} x {g(O.cone_h)} in each flange, socket in the plate: the plate sets all three",
         (p / 4, p / 4))
    note(ax, (-30, -40), "one thread-forming screw into each piece", (-p / 4, -p / 4))
    ax.set_title("4  node: three pieces meet (seen from inside)", fontsize=9)


def joint_service(ax) -> None:
    w, b = J.wall_t, O.service_boss
    box(ax, -40, 0, 39.5, w, LOWER)
    box(ax, 0.5, 0, 39.5, w, UPPER)
    box(ax, -0.5 - b, w, b, w, LOWER)                                   # flange of the part that opens
    box(ax, 0.5, w, b, O.insert_l + 1, UPPER)                           # boss of the fixed part
    xc = 0.5 + b / 2
    box(ax, xc - O.insert_hole_d / 2, w + 1, O.insert_hole_d, O.insert_l, "#c0c0c0")
    ax.plot([xc, xc], [-4, w + O.insert_l + 1], color="#333", lw=1.6, zorder=6)
    ax.add_patch(Polygon([(-0.5, 0), (0.5, 0), (0, O.service_chamfer)], fc="white", ec="#333", lw=0.6, zorder=4))
    dim(ax, (0.5, w + O.insert_l + 4), (0.5 + b, w + O.insert_l + 4), f"boss {g(b)}", (0, 3))
    note(ax, (-40, 26), f"{O.insert} heat-set insert ({g(O.insert_hole_d)} hole, {g(O.insert_l)} deep) in the fixed part; "
         f"{O.insert} screw every {g(O.service_pitch_min)} to {g(O.service_pitch_max)}", (xc, w + O.insert_l))
    note(ax, (-40, 32), f"two pins {g(O.pin_d)} dia, +{g(O.pin_clearance)}, for the place; chamfer {g(O.service_chamfer)} "
         "on both edges; never glued or filled", (0, 2))
    note(ax, (-40, -10), "door: 4 thumb screws into inserts", None)
    note(ax, (-40, -14), f"hood: 2 pins at the front, 2 {O.insert} at the rear", None)
    note(ax, (-40, -18), "bezel plate: magnets on the fixed cradle, 2 pins, a finger notch: no tool", None)
    ax.set_title("5  service seam (opens again)", fontsize=9)


def coupon(ax) -> None:
    """The coupon pair as candybar.shell.coupon models it: plan of the arc, and the face seen from outside."""
    r, n, half, w = cp.RADIUS, cp.LENGTH, cp.HALF, J.wall_t
    top = 10.0
    t = np.linspace(-n / 2 / r, n / 2 / r, 40)
    outer = np.stack([r * np.sin(t), r * np.cos(t) - r + top], 1)
    inner = np.stack([(r - w) * np.sin(t), (r - w) * np.cos(t) - r + top - w * 0], 1)
    inner[:, 1] -= w
    ax.add_patch(Polygon(np.concatenate([outer, inner[::-1]]), fc=LOWER, ec="#333", lw=0.8))
    ax.text(0, top + 4, f"plan: {g(n)} along the arc, radius {g(r)}, skin {g(w)}", fontsize=6.5, ha="center")
    y0 = -12.0
    box(ax, -n / 2, y0 - half, n, half, UPPER)
    box(ax, -n / 2, y0 - 2 * half, n, half, LOWER)
    for s in jt.screw_stations(cp.path(), J.screw_pitch):
        ax.plot([s, s], [y0 - half - J.pilot_depth, y0 - half + J.flange_t], color="#333", lw=1.4, zorder=5)
    dim(ax, (-n / 2, y0 - 2 * half - 5), (n / 2, y0 - 2 * half - 5), f"{g(n)}", (0, -3))
    dim(ax, (n / 2 + 5, y0 - half), (n / 2 + 5, y0), g(half), (4, 0))
    dim(ax, (n / 2 + 5, y0 - 2 * half), (n / 2 + 5, y0 - half), g(half), (4, 0))
    note(ax, (-n / 2, y0 - half / 2), "upper half: the groove; prints with the seam on the bed")
    note(ax, (-n / 2, y0 - 1.5 * half), "lower half: the key and one pilot of each candidate; prints with the seam on top")
    note(ax, (-n / 2, y0 - 2 * half - 14), f"seam level along the arc, as L1; screws at the pitch of {g(J.screw_pitch)}; "
         f"three pairs: groove {', '.join('+' + g(c) for c in cp.CLEARANCES)}")
    ax.set_title("6  coupon pair for joint 1 (cad/out/coupon)", fontsize=9)


def joint_hood(ax, d: Blueprint) -> None:
    """The hood on the body top: keyed, then bolted or bonded with the same parts."""
    w, gap, bev = J.wall_t, d.seam_gap, d.seam_groove
    box(ax, 0, gap, w, 40, UPPER)                                   # hood wall, outside at x = 0
    box(ax, 0, -40, w, 40, LOWER)                                   # body wall
    ax.plot([0, bev], [-bev, 0], color="#333", lw=0.8)              # body bevel
    ax.plot([0, bev], [gap + bev, gap], color="#333", lw=0.8)       # hood bevel
    box(ax, w, -O.ring_h, O.ring_w, O.ring_h, LOWER)                # top ring of the body
    box(ax, w, gap, O.ring_w, O.hood_foot_t, UPPER)                 # foot flange of the hood
    cx = w + 0.4 * O.ring_w
    ax.add_patch(Polygon([(cx - O.cone_d / 2, 0), (cx + O.cone_d / 2, 0), (cx, O.cone_h)], fc=LOWER, ec="#333", lw=0.8, zorder=4))
    ix = w + O.ring_w - O.insert_hole_d / 2 - 0.5
    box(ax, ix - O.insert_hole_d / 2, -O.insert_l - 1, O.insert_hole_d, O.insert_l, "#c0c0c0")
    ax.plot([ix, ix], [-O.insert_l, gap + O.hood_foot_t + 4], color="#333", lw=1.6, zorder=6)
    dim(ax, (-6, gap), (-6, 0), g(gap), (-5, 0))
    dim(ax, (w, -O.ring_h - 4), (w + O.ring_w, -O.ring_h - 4), f"ring {g(O.ring_w)}", (0, -3))
    note(ax, (-40, 30), f"cone {g(O.cone_d)} x {g(O.cone_h)} on the ring, socket in the hood: two at the front, two at the "
         "rear corners", (cx, O.cone_h / 2))
    note(ax, (-40, 24), f"bolt: {O.insert} into a heat-set insert in the ring, from inside the hood (two at the rear)", (ix, 5))
    note(ax, (-40, 18), "bond: the same faces take adhesive; the cones still set the place", (cx + 1, gap + 1))
    note(ax, (-40, -28), f"groove {g(gap)} + bevels {g(bev)} x {g(bev)} stays open: a design line", (bev / 2, -bev / 2))
    ax.set_title("7  hood on the body top: keyed, to bolt or to bond", fontsize=9)


def value_rows(obj) -> list[str]:
    rows = []
    for f in fields(obj):
        v = getattr(obj, f.name)
        if f.name == "pilot_d" and v is None:
            v = f"open: {g(obj.pilot_d_pet)} or {g(obj.pilot_d_abs)}"
        rows.append(f"{f.name:<20} {v if isinstance(v, str) else g(v)}")
    return rows


def joint_values(ax) -> None:
    ax.axis("off")
    left = ["joints.Joint (joint 1, on the coupon):", ""] + value_rows(J)
    right = ["joints.OtherJoints (2 to 7, concept):", ""] + value_rows(O)
    right += ["", "PETG and ABS use the same values;", "the coupon of each material sets", "the clearances and the pilot."]
    for x, rows in ((0.0, left), (0.45, right)):
        ax.text(x, 1, "\n".join(rows), fontsize=7.5, family="DejaVu Sans Mono", va="top", transform=ax.transAxes)


def joints_sheet(out: str = OUT, name: str = "joints", svg: bool = False) -> str:
    d = Blueprint()
    fig = plt.figure(figsize=(32, 13))
    grid = fig.add_gridspec(2, 5, hspace=0.12, wspace=0.12)
    places = (grid[0, 0:2], grid[0, 2], grid[0, 3], grid[0, 4], grid[1, 0], grid[1, 1], grid[1, 2])
    drawers = (joint_skin, joint_floor, joint_foot, lambda ax: joint_hood(ax, d), joint_node, joint_service, coupon)
    limits = (((-60, 60), (-25, 38)), ((-45, 50), (-16, 28)), ((-35, 40), (-10, 64)), ((-45, 25), (-35, 40)),
              ((-35, 35), (-45, 50)), ((-45, 45), (-20, 36)), ((-75, 80), (-160, 22)))
    for place, f, lim in zip(places, drawers, limits):
        ax = fig.add_subplot(place)
        f(ax)
        ax.set_xlim(*lim[0])
        ax.set_ylim(*lim[1])
        ax.set_aspect("equal")
        ax.tick_params(labelsize=6)
        ax.grid(True, color="#f0f0f0", lw=0.4)
    joint_values(fig.add_subplot(grid[1, 3:5]))
    fig.suptitle("Joints of the bonded seams and the service seams (mm), from cad/candybar/shell/joints.py. Step 1: the key, "
                 "cone or pin sets the place in a dry assembly held by screws. Step 2: adhesive, the same screws, then "
                 "filler in the V-groove.\nJoint 1 is modelled on the coupon; joints 2 to 7 are not modelled yet.", fontsize=12)
    path = os.path.join(out, name + ".png")
    fig.savefig(path, dpi=110, bbox_inches="tight")
    if svg:
        fig.savefig(os.path.join(out, name + ".svg"), bbox_inches="tight")
    plt.close(fig)
    return path


# ---------- the width study ----------

def hull_points(p: np.ndarray) -> np.ndarray:
    from scipy.spatial import ConvexHull

    if len(p) < 8:
        return p
    try:
        return p[ConvexHull(p).vertices]
    except Exception:  # noqa: BLE001 - flat piece: keep the points
        return p


def width_study(meas: dict, step: float = 0.5) -> dict:
    """Each option's pieces with the cabinet wider by dW, the growth put into the rails (the agent that studies width
    adds it beside the bezel; candidates 514.7 and 533.2): every point outside x = +-218.3 of the body and the floor, and outside x = +-174 of the
    hood (the top flat), moves out by dW / 2. The centre seam of the hood halves then grows with them. Gives the
    largest dW at which every piece still fits, and the result at +20 and +38."""
    lim = sp.Printer(**{k: meas["printer"][k] for k in ("xy", "z", "bed", "source")})
    out = {}
    for key in sp.ALL:
        man = json.load(open(os.path.join(OUT, key, "manifest.json")))
        rows = meas["options"][key]["pieces"]
        parts = {}
        for name, m in man.items():
            module = rows[name]["module"]
            if module in ("bezel", "speaker_right", "speaker_left", "logo_form"):
                continue
            t = 174.0 if module == "hood" else 218.3
            p = db.load_stl(os.path.join(OUT, key, m["file"])).reshape(-1, 3)
            p = np.unique(np.round(p, 2), axis=0)
            groups = [hull_points(p[p[:, 0] > t]), hull_points(p[p[:, 0] < -t]), hull_points(p[np.abs(p[:, 0]) <= t])]
            parts[name] = (groups, rows[name]["up"])

        def fails(dw: float) -> list[str]:
            bad = []
            for name, (g, up) in parts.items():
                q = [g[0] + (dw / 2, 0, 0), g[1] - (dw / 2, 0, 0), g[2]]
                q = np.concatenate([x for x in q if len(x)])
                if not sp.print_box(q, tuple(up), lim, step=1.0)["fits"]:
                    bad.append(name)
            return bad

        lo, hi = 0.0, 80.0
        if fails(hi):
            while hi - lo > step:
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if not fails(mid) else (lo, mid)
        else:
            lo = hi
        out[key] = {"max_dw": lo, "at_20": fails(20.0), "at_38": fails(38.5), "first": fails(hi) if hi < 80 else []}
    return out


def panel_seam(x: float = -41.2) -> dict:
    """A seam across a printed control panel plate at x: its clearance to every control under the plate, and the width
    of the larger half."""
    d = Blueprint()
    from candybar.shell import profiles as pr

    out = pr.panel_outline(d)
    near = []
    for it in sections()["rear"]["items"]:
        if it["group"] != "Panel" or it["role"] != "hardware":
            continue
        x0, _, x1, _ = it["box"]
        gap = x0 - x if x0 > x else (x - x1 if x1 < x else -1.0)
        near.append((gap, it["solid"]))
    near.sort()
    xs = [p[0] for p in out]
    return {"x": x, "halves": (round(x - min(xs), 1), round(max(xs) - x, 1)), "nearest": near[:3]}
