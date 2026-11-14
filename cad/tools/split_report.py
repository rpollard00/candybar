"""Write <out>/split/report.md: the split of the shell and its structure, with the numbers of the cut.

draw_split.py calls write(). The numbers come from the cut (split/measurements.json), the structure run
(split/structure.json), the fit study (fit/sections.json) and the hand estimates of candybar.shell.structure. The
words are Simplified Technical English.

The study of 2026-11-11 compared three seam options and a frame of aluminium extrusion. The owner chose from it
(decision record 0006), and the options that were not chosen are not in the code. The text of that study is not
written again.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(HERE)
sys.path.insert(0, CAD)
sys.path.insert(0, HERE)
import draw_structure as ds  # noqa: E402
from candybar.shell import joints as jt  # noqa: E402
from candybar.shell import split as sp  # noqa: E402
from candybar.shell import structure as st  # noqa: E402
from candybar.shell.dims import Blueprint  # noqa: E402

OUT = ds.OUT


def fmt(v: float) -> str:
    return f"{v:.0f}"


def seam_kind(s: dict) -> str:
    return "service" if s["joint"] == "service" else "bonded"


def printed(rows: dict) -> dict:
    return {n: r for n, r in rows.items() if r["module"] != "base"}


def pieces_table(w, res: dict, lay: sp.Layout) -> None:
    w("| # | Piece | Print box (mm) | Fits | On the bed | Skin (g) | Seen (cm2) | Seen face over 45 deg (cm2) | Seen face at 45 deg (cm2) | Shallow tops (cm2) | Why this way |")
    w("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    nums = {n: i + 1 for i, n in enumerate(n for n in res["pieces"] if not n.startswith("floor"))}
    pieces = {p.full: p for p in sp.expanded(lay)[1]}
    for n, r in res["pieces"].items():
        p = pieces[n]
        why = "as R" if p.side == "L" and (n[:-1] + "R") in pieces else p.why
        w(f"| {nums.get(n, '')} | {n} | {fmt(r['x'])} x {fmt(r['y'])} x {fmt(r['z'])} | {'yes' if r['fits'] else '**no**'} | "
          f"{p.bed} | {r['mass_g']} | {r.get('seen', '')} | {r.get('overhang_seen', '')} | {r.get('limit_seen', '')} | {r.get('terrace_seen', '')} | {why} |")


def write(meas: dict, lay: sp.Layout, d: Blueprint, face_cloud, crossed, near_hardware, boxes) -> str:
    tree, fids = face_cloud(d)
    lim = meas["printer"]
    res = meas[sp.SHELL]
    rows = res["pieces"]
    lines_ = json.load(open(os.path.join(OUT, sp.SHELL, "seams.json")))
    path = os.path.join(OUT, "structure.json")
    struct = json.load(open(path)) if os.path.exists(path) else {}
    L: list[str] = []
    w = L.append
    big = max(printed(rows).items(), key=lambda kv: max(kv[1]["x"], kv[1]["y"]))
    over = sum(r.get("overhang_seen", 0.0) for r in rows.values())
    limit = sum(r.get("limit_seen", 0.0) for r in rows.values())

    w("# The split of the shell")
    w("")
    w(lay.idea)
    w("")
    w(f"- Pieces: {len(printed(rows))} printed pieces and {len(rows) - len(printed(rows))} floor tiles. The bezel plate is two pieces more.")
    w(f"- Printer limit: {lim['xy']:.0f} x {lim['xy']:.0f} on the bed, {lim['z']:.0f} high ({lim['source']}). "
      f"Each piece fits: {'yes' if res['fits'] else '**no**'}.")
    w(f"- Largest piece: {big[0]}, {big[1]['x']:.1f} x {big[1]['y']:.1f} x {big[1]['z']:.1f}; "
      f"{lim['xy'] - max(big[1]['x'], big[1]['y']):.1f} less than the limit.")
    w(f"- Seen faces that overhang more than {sp.OVERHANG:g} degrees: {over:.1f} cm2 in total. "
      f"Seen faces at {sp.OVERHANG:g} degrees (within {sp.OVERHANG_BAND:g}): {limit:.1f} cm2.")
    w(f"- Skin of the printed pieces without the floor: {st.skin_kg(rows):.2f} kg (a solid skin of {d.wall_t:g} mm; ribs and flanges are not in it).")
    w(f"- Problems of the cut: {'none' if not res['problems'] else '; '.join(json.dumps(q) for q in res['problems'])}.")
    w(f"- Skin: fingerprint {meas['skin_key']}.")
    w("")
    w("Drawings: `split.png` (four views with the seams), `split-front.png`, `split-rear.png`, `split-side.png`, `structure.png`, "
      "`services.png`, `joints.png`, `renders/`.")
    w("")
    w("## Pieces")
    w("")
    pieces_table(w, res, lay)
    w("")
    w(f"\"Seen face over 45 deg\": area that a person sees and that faces down more than {sp.OVERHANG + sp.OVERHANG_BAND:g} degrees from "
      "upright in this orientation. It needs support. \"Seen face at 45 deg\": area within "
      f"{sp.OVERHANG_BAND:g} degrees of {sp.OVERHANG:g}. These are the facets of the rear shelf, the roofs of the hand-holds and the base "
      "facet, which are 45 degrees by design and print without support. \"Shallow tops\": faces seen at 1 to 25 degrees from "
      "level, which show layer terraces before primer. The floor tiles are measured as the floor of the skin; the floor "
      f"that the owner chose is a sandwich of {st.FLOOR_T:g} mm.")
    w("")
    w("## Seams")
    w("")
    w("| Seam | Class | Where | Joint | Faces crossed | Seen length (mm) | Hardware within 18 mm | How it reads |")
    w("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for name, s in res["seams"].items():
        if s["side"] == "L":
            continue
        ls = lines_[name]["lines"]
        other = lines_.get(f"{s['label']} L", {}).get("lines", [])
        near = near_hardware(ls + other, boxes)
        w(f"| {s['label']} | {seam_kind(s)} | {sp.CLASS_WORDS[s['cls']]} | {s['joint']} | {', '.join(crossed(ls, tree, fids))} | "
          f"{s['seen_mm']:.0f}{' each side' if other else ''} | {', '.join(near) if near else 'none'} | {s['reads']} |")
    for label, what, joint, words in sp.EXISTING:
        w(f"| {label} | service | in a design line | {joint} | {what} | existing | | {words} |")
    w("")
    w(f"**Rear door.** {lay.door}")
    w("")
    w(f"**What opens for service.** {lay.service}")
    w("")
    w("**Order of assembly.**")
    w("")
    for i, step in enumerate(lay.assembly, 1):
        w(f"{i}. {step}")
    w("")
    w("## The bezel plate")
    w("")
    pieces_table(w, meas[sp.PLATE], sp.BEZEL)
    w("")
    w("The plate is cut in the first of three ways. Decision record 0006 does not name the way, so the list stays:")
    w("")
    for key, title, words in sp.BEZEL_OPTIONS:
        w(f"{key}. **{title}.** {words}")
    w("")

    # ---------- structure ----------
    w("## Structure")
    w("")
    w("The shell is a stressed skin (decision record 0006). The values that follow are hand estimates at concept level.")
    w("")
    mass = st.total_mass(st.skin_kg(rows), st.FLOOR_DM2)
    com = st.centre_of_mass(rows, mass, d)
    w("### Mass")
    w("")
    w("| Part | kg |")
    w("| --- | --- |")
    for k, label in (("skin", "printed skin, without the floor"), ("joints_and_ribs", "ribs, flanges, splice plates, inserts, screws (25 % of the skin)"),
                     ("floor", f"printed floor, sandwich of {st.FLOOR_T:g} mm"), ("hardware", "hardware")):
        w(f"| {label} | {mass[k]:.2f} |")
    w(f"| **total** | **{mass['total']:.2f}** |")
    w("")
    w(f"Centre of mass: y {com[0]:.0f}, z {com[1]:.0f} (ESTIMATED: each piece at the middle of its box, each hardware item at the middle of its envelope).")
    w("")
    w("### Hand-holds")
    w("")
    hh = st.hand_holds(mass["total"], com[0], d)
    x0, x1, y0, y1, z0, z1 = hh["grip"]
    w(f"Each hand-hold is a recess in the rear wall of the head: x {x0:g} to {x1:g} on each side, z {z0:g} to {z1:g}, {d.grip_depth:g} deep. "
      f"The roof falls 45 degrees from its rim on the rear wall to the back of the recess. The fingers pull up on the roof. "
      f"The wall above the rim is {hh['wall_above']:.1f} high (to the body top less the seam groove).")
    w("")
    w(f"The lift of the owner (2026-11-11): one person lifts the back by the two hand-holds, and the cabinet pivots on {hh['pivot']}. "
      f"The weight is {hh['weight_N']:.0f} N. The hand-holds are at y {hh['grip_y']:.0f}, so they carry {hh['lift_N']:.0f} N and the front "
      f"edge carries {hh['edge_N']:.0f} N. With a factor of 2 for a jerk, the design load in each recess is {hh['each_design_N']:.0f} N.")
    w("")
    w("| Estimate | Lift with the pivot | Straight lift (the whole weight on the two recesses, factor 2) |")
    w("| --- | --- | --- |")
    a, b = hh["pivot_lift"], hh["straight_lift"]
    for k, label, unit in (("load_N", "Design load in each recess", "N"),
                           ("roof_plate_mm", f"Roof as a plate on four edges ({hh['roof_slope']:.1f} x {hh['roof_span']:.0f} x {d.wall_t:g}), load at its middle: deflection", "mm"),
                           ("roof_strip_MPa", f"Roof as a strip {hh['hand_w']:.0f} wide from the rim to the back wall, load at mid span: bending stress", "MPa"),
                           ("roof_edge_shear_MPa", "Shear where the roof joins the rear wall and the back wall", "MPa"),
                           ("wall_above_MPa", f"Wall above the rim ({hh['wall_above']:.1f} x {d.wall_t:g}) as a beam with fixed ends, half the load: bending stress", "MPa")):
        w(f"| {label} | {a[k]:.2f} {unit} | {b[k]:.2f} {unit} |")
    w("")
    w(f"Printed PETG holds about {hh['yield_MPa']:.0f} MPa for a short time and {st.CREEP_MPA:g} MPa for a long time (ESTIMATED from data sheets). "
      "A lift is a short load.")
    walls = struct.get("hand_hold_walls")
    if walls:
        w("")
        w("The wall round the right recess, measured on the skin: " + "; ".join(
            f"{k} {v['wall']:.2f}" if v else f"{k} not found" for k, v in walls.items()) + ". "
          f"The roof is {d.wall_t:g} thick square to its face, which is {d.wall_t * 2 ** 0.5:.2f} straight up.")
    w("")
    w("### Load cases")
    w("")
    est = st.estimates(mass, d)
    w(f"- Straight lift by the two hand-holds: {est['lift']['note']}; shear {est['lift']['rim_shear_MPa']:.2f} MPa.")
    w(f"- Lean on the deck front: {est['lean']['note']}; {est['lean']['stress_MPa']:.2f} MPa.")
    w(f"- Hit on the control panel: {est['panel']['note']}; deflection {est['panel']['deflection_mm']:.2f} mm.")
    w(f"- Racking: {est['racking']['note']}; moment at the body top {est['racking']['moment_body_top_Nm']:.1f} N m, at the floor "
      f"{est['racking']['moment_floor_Nm']:.1f} N m; sway of a portal {est['racking']['portal_mm']:.2f} mm.")
    for k, v in est["finger"].items():
        w(f"- Finger push of 20 N on the skin, {k}: deflection {v:.2f} mm.")
    w(f"- Rib spacing for 0.3 mm under 20 N: {est['rib_spacing_mm']:.0f} mm on the {d.wall_t:g} mm skin.")
    w(f"- Monitor on its cradle: {est['monitor']['note']}; {est['monitor']['clamp_stress_MPa']:.2f} MPa (limit for a long load {est['monitor']['creep_limit_MPa']:g} MPa).")
    w(f"- Hot air: {est['heat']['note']}; rise {est['heat']['exhaust_dT_K']:.0f} K.")
    w("")
    w("### Members")
    w("")
    w("| Member | Kind | Note |")
    w("| --- | --- | --- |")
    for m in st.members(d, ds.board_x()):
        w(f"| {m.name}{' (each side)' if m.mirror else ''} | {st.KIND_WORDS[m.kind]} | {m.note} |")
    w("")
    w("### Mounts")
    w("")
    w("| Component | Mount | On |")
    w("| --- | --- | --- |")
    for m in st.mounts():
        w(f"| {m.item} | {m.how} | {m.on} |")
    w("")
    w("### Cable routes")
    w("")
    for r in st.ROUTES:
        w(f"- **{r.name}.** {r.crossings}")
    w("")
    w("### Air path")
    w("")
    w("| Part | Where | What it does |")
    w("| --- | --- | --- |")
    for part, where, what in st.AIR:
        w(f"| {part} | {where} | {what} |")
    w("")
    if struct:
        w("### The hardware in the skin")
        w("")
        move = "; ".join(f"{m['dy']:g} forward: {'no clash' if not m['hits'] else ', '.join(f'{k} {v} mm3' for k, v in m['hits'].items())}" for m in struct["compute_move"])
        w(f"- The compute module moved toward the front: {move}.")
        out = ", ".join(f"{m['out_mm']:g}: {m['in_skin_mm3']} mm3" for m in struct["monitor_path"])
        w(f"- The room for any 16:10 monitor pulled out to the front, its volume in the skin at each step: {out}.")
        w("")
    w("## Joints")
    w("")
    w("`joints.png`. Every bonded joint works in two steps: a key, cone or pin sets the one right place, so that a dry "
      "assembly held by screws alone has its final shape; then the same joint is bonded, the screws clamp it while the "
      "adhesive cures and stay in, and filler goes into a V-groove on the outside.")
    w("")
    w("| Joint | Locates | Clamps and stays | Spacing | Bond area | Outside | Prints without support |")
    w("| --- | --- | --- | --- | --- | --- | --- |")
    J, O, g = jt.JOINT, jt.OTHER_JOINTS, ds.g
    w(f"| 1 skin to skin (wall or curved face) | inside flange {g(J.flange_t)} x {g(J.flange_h)} on both pieces, a key "
      f"{g(J.key_proj)} x {g(J.key_w)} on one face in a groove of the other (+{g(J.groove_clearance)}, the coupon sets it) | "
      f"thread-forming screw {g(J.screw_d)} x {g(J.screw_l)} for plastics through both flanges; {ds.pilot_words()} | "
      f"{g(J.screw_pitch)} | {g(ds.bond_width())} per mm of seam beside the groove, plus the {g(J.wall_t)} mm butt | "
      f"V-groove {g(J.vgroove_w)} wide, {g(J.vgroove_d)} deep | yes: a level flange has a {g(J.gusset_angle)} deg gusset "
      "under it; an upright flange is a wall |")
    w(f"| 2 floor tile to tile | half-lap {g(O.lap_w)} wide, each lap {g(st.FLOOR_T / 2)}; a cone {g(O.cone_d)} x "
      f"{g(O.cone_h)} in the lower lap, socket in the upper | thread-forming {g(O.base_screw_d)} x {g(O.lap_screw_l)} from "
      f"below | {g(O.lap_screw_pitch)} | {g(O.lap_w)} per mm | none (under the cabinet) | yes: both laps print flat |")
    w(f"| 3 wall foot to floor | key {g(O.foot_key_w)} x {g(O.foot_key_h)} under the foot flange in a slot of the floor | "
      f"thread-forming {g(O.base_screw_d)} x {g(O.foot_screw_l)} up from below | {g(O.foot_screw_pitch)} | {g(J.foot_h)} per mm "
      "| none | yes: the flange is at the bed in the upright print |")
    w(f"| 4 node (three pieces meet: L1 or B1 with S1, P1 with L1, the rear corners) | a cone in each flange, sockets in a "
      f"node plate {g(O.node_plate)} x {g(O.node_plate)} x {g(O.node_plate_t)} | one thread-forming screw into each piece | "
      "one plate | the plate | none | the plate prints flat |")
    w(f"| 5 service (door, hood, bezel plate, panel, USB plate) | two pins {g(O.pin_d)} dia, +{g(O.pin_clearance)} | "
      f"{O.insert} heat-set insert in the fixed part, {O.insert} screw | {g(O.service_pitch_min)} to {g(O.service_pitch_max)} | "
      f"none: never bonded | chamfer {g(O.service_chamfer)} on both edges | yes: bosses on the flanges, inside |")
    w("")
    w("Adhesive and filler: the classes of `docs/research/petg-finishing.md` (section 1), to prove on the coupon. No "
      "strength for printed PETG is claimed.")
    w("")
    w(f"**Coupon test before the real parts** (`joints.png`, panel 6): three pairs of joint 1 on a curved face of radius {g(ds.cp.RADIUS)}, "
      f"printed in the real orientation, with groove clearances of {', '.join('+' + g(c) for c in ds.cp.CLEARANCES)}. It must prove the "
      "clearance that locates with no play and no force, the adhesive, and the filler and paint over the joint.")
    w("")
    w("**Assembly in two passes.** Pass 1, dry: screw every bonded joint with its thread-forming screws, fit all the "
      "hardware, and correct the fit. Pass 2, bond, in batches of one to three seams: open the batch, put adhesive on "
      "its flange faces, screw it again in the same holes, and let it cure. Then fill the V-grooves, sand, prime and "
      "paint. The finish pieces are painted alone and fastened last.")
    w("")
    w("## Alignment and dry assembly")
    w("")
    w("| Seam | Joint | What locates it | Directions fixed |")
    w("| --- | --- | --- | --- |")
    for seam, joint, how, fixed in st.ALIGNMENT:
        w(f"| {seam} | {joint} | {how} | {fixed} |")
    w("")
    w("n: square to the seam. t: across the wall, so that the faces lie flush. s: along the seam. The joint numbers are those of `joints.py` and sheet 11.")
    w("")
    w("## How the numbers were made")
    w("")
    w("- The cut: `candybar.shell.split` splits the skin (the outer form less the cavity) with the seam polygons and measures each piece in its print orientation.")
    w("- The structure: `candybar.shell.structure` holds the members, the mounts, the routes and the hand estimates. Its run moves the hardware of the fit study in the skin and measures the walls of the hand-hold.")
    w("- Flanges, keys, ribs and carriers are not modelled yet. The masses are those of the plain skin.")
    return "\n".join(L) + "\n"
