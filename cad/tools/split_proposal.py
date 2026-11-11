"""Write cad/out/shell-bp/split/proposal.md: the seam options, their structure, the mounts, the cable routes, the air
path, the joints, the finishing audit and the width study. draw_split.py calls write(); the numbers come from the
cut (split/measurements-*.json), the frame check (split/structure.json), the fit study (fit/report.json,
fit/sections.json) and the hand estimates of candybar.shell.structure. The words are Simplified Technical English.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date


HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(HERE)
sys.path.insert(0, CAD)
sys.path.insert(0, HERE)
import draw_structure as ds  # noqa: E402
from candybar.shell import split as sp  # noqa: E402
from candybar.shell import structure as st  # noqa: E402
from candybar.shell.dims import Blueprint  # noqa: E402

OUT = ds.OUT
SHELL = ds.SHELL
FLOOR_DM2 = 4.866 * 5.32


def widest(wd: dict) -> str:
    return "575 or more (+80 tested)" if wd["max_dw"] >= 80 else f"{494.7 + wd['max_dw']:.0f} (+{wd['max_dw']:.0f})"


REMEDY = {"hood half": "the hood in three pieces (H1 at x = +-106, the hood of A): one piece more",
          "rear lower": "the rear wall below the door in three (R2 at x = +-106, as A): one piece more",
          "door half": "the door in three (R4 at x = +-106, as A): one piece more"}


def fmt(v: float) -> str:
    return f"{v:.0f}"


def seam_kind(s: dict) -> str:
    return "service" if s["joint"] == "service" else "bonded"


def printed(rows: dict) -> dict:
    return {n: r for n, r in rows.items() if r["module"] != "base"}


def skin_kg(rows: dict) -> float:
    return sum(r["mass_g"] for n, r in rows.items() if r["module"] not in ("base", "bezel")) / 1000


def centre_of_mass(rows: dict, mass: dict) -> tuple[float, float]:
    items = {b["solid"]: b for b in ds.sections()["rear"]["items"]}
    pts = []
    for r in rows.values():
        if "cabinet" in r and r["module"] != "base":
            x0, x1, y0, y1, z0, z1 = r["cabinet"]
            pts.append((r["mass_g"] / 1000 * 1.25, (y0 + y1) / 2, (z0 + z1) / 2))
    pts.append((mass["floor"], 270.0, 3.5))
    for solid, kg in (("PSU_Body", 3.27), ("Monitor_Body", 0.82), ("Compute_Heatsink", 1.4), ("CableBundle_Body", 0.6)):
        b = items[solid]
        pts.append((kg, (b["y"][0] + b["y"][1]) / 2, (b["box"][1] + b["box"][3]) / 2))
    pts.append((1.2, 110.0, 60.0))  # control panel and its controls
    pts.append((0.7, 500.0, 480.0))  # speakers and marquee
    m = sum(p[0] for p in pts)
    return sum(p[0] * p[1] for p in pts) / m, sum(p[0] * p[2] for p in pts) / m


def write(meas: dict, opts: dict, d: Blueprint, face_cloud, crossed, near_hardware, boxes) -> str:
    tree, fids = face_cloud(d)
    lim = meas["printer"]
    struct = json.load(open(os.path.join(OUT, "structure.json")))
    fit = json.load(open(os.path.join(SHELL, "fit", "report.json")))
    width = ds.width_study(meas)
    seam = ds.panel_seam()
    L: list[str] = []
    w = L.append

    w("# Seam, structure and mounting proposal for the printed shell")
    w("")
    w(f"Date: {date.today().isoformat()}. Status: a proposal for the owner, at concept level. Nothing is cut or joined in "
      "the model, and no part is designed. `cad/tools/draw_split.py` writes this file from the seam data "
      "(`cad/candybar/shell/split.py`), the structure data (`cad/candybar/shell/structure.py`) and the cut and the checks "
      "that those modules run under FreeCAD. Do not edit it by hand.")
    w("")
    w("| Sheet | Content |")
    w("| --- | --- |")
    w("| `options.png`, `option-A.png`, `option-B.png`, `option-C.png` | Front, side, top and rear of each option, each piece "
      "in a soft tint and numbered, every seam drawn and labelled: blue in a design line, red on an open face |")
    w("| `renders/<option>/three-quarter-front-left.png`, `three-quarter-rear-left.png` | Renders with the pieces tinted |")
    w("| `structure-A.png`, `structure-B.png`, `structure-C.png` | Side view and plan: floor, ring frames, cross-members, ribs, "
      "the frame of C, with the hardware of the fit study |")
    w("| `services.png` | Cable routes with the plugs at the parts that open, and the air path with the optional duct fan |")
    w("| `joints.png` | Dimensioned sections of the joints (with the hood, keyed to bolt or to bond), the named values and the coupon pair |")
    w("| `chosen.png`, `structure-chosen.png`, `renders/chosen/` | The chosen layout |")
    w("")
    w("## Decided by the owner (2026-11-11)")
    w("")
    for line in ("Width: +0 (494.7). The bezel plate has no ledge at its sides, so the monitor comes out to the front "
                 "with 7.3 to spare on each side.",
                 "Seams: B with the hood of A (the chosen layout, `chosen.png`).",
                 "Hood: keyed on the body top; the same parts take bolts or adhesive (joint 7). The owner may bolt or bond it.",
                 "Floor: printed PETG, made stiffer than the 7 mm sandwich: see \"Floor\".",
                 "Hand-holds: at the back corners: see \"Hand-holds\".",
                 "Material: open (PETG on the A1, or ABS on an enclosed printer): see \"Material\"."):
        w(f"- {line}")
    w("")

    # ---------- what decides ----------
    w("## What decides the seams")
    w("")
    w("**Finish (the owner, 2026-11-11).** The shell is filled, finished and painted, and it is not taken apart after "
      "that. The brief says the same: \"Fill only permanent seams and apply the coupon-proven finish\", and \"Keep "
      "permanent filled seams within cosmetic subassemblies; do not fill joints needed to remove the monitor, controls "
      "or computer.\" Thus there are three classes of seam:")
    w("")
    w("- **Bonded seam.** Permanent: locked, screwed, bonded, filled and painted. It does not show, so its place comes "
      "from print quality, strength and a low piece count. It must not move: filler and paint crack over a joint "
      "that flexes or peels. It must not cross a place that flexes or carries a peel load, nor the palm rest and the "
      "lever (the brief: \"Put seams away from high-load palm-rest and joystick areas.\").")
    w("- **Service seam.** It opens again, so it stays open and visible, and it must be a design line: the rear door "
      "(DR or DB), the control panel (pocket DK8), the bezel plate (reveal BZ4; the monitor comes out behind it), the "
      "USB socket plate, and the hood on its groove (FB5 / HC15).")
    w("- **Finish seam.** A piece that has another colour than its neighbour, or that makes a tight inside corner with "
      "it, is a separate piece. It is sanded and painted alone and fastened from the inside after the paint, so that "
      "the tight corner is the edge between two finished pieces. See \"Finishing\".")
    w("")
    w("In the drawings the colour of a seam still says where it lies (blue: in a design line; red: on an open face). In "
      "the tables the class is given. A red bonded seam is filled and does not show.")
    w("")
    w(f"**Printer.** {lim['source']}: {lim['xy']:.0f} x {lim['xy']:.0f} on the bed, {lim['z']:.0f} high (bed {lim['bed']:.0f}). "
      "A piece may turn on the bed. The body is 494.7 wide, so half of it (247.4) is more than the bed: every part that "
      "spans the full width needs three pieces across. Only the hood, the rear wall and the door (narrower than 480) can "
      "be halves.")
    w("")

    # ---------- glance and ranking ----------
    w("## The options at a glance")
    w("")
    w("| Option | Architecture | Printed pieces | Largest piece (print box) | All fit | Widest cabinet that still fits | 514.7 (+20) | 533.2 (+38.5) |")
    w("| --- | --- | --- | --- | --- | --- | --- | --- |")
    arch = {"A": "stressed skin", "B": "stressed skin", "C": "2020 chassis, skin carries no load", "chosen": "stressed skin (decided)"}
    for key, opt in opts.items():
        res = meas["options"][key]
        pr_ = printed(res["pieces"])
        big = max(pr_.items(), key=lambda kv: max(kv[1]["x"], kv[1]["z"]))
        wd = width[key]
        verdict = lambda bad: "fits" if not bad else "fails: " + ", ".join(sorted({b.rsplit(' ', 1)[0] if b.endswith((' R', ' L')) else b for b in bad}))
        w(f"| {opt.title} | {arch[key]} | {len(pr_)} + 9 floor tiles | {big[0]}: {fmt(big[1]['x'])} x {fmt(big[1]['y'])} x "
          f"{fmt(big[1]['z'])} | {'yes' if res['fits'] else 'NO'} | {widest(wd)} | "
          f"{verdict(wd['at_20'])} | {verdict(wd['at_38'])} |")
    w("")
    w("**Ranking.** With the bonded seams filled and painted, a seam in a design line no longer wins on looks; it wins only "
      "where it gives a better print, a stiffer joint or fewer pieces. The ranking changes:")
    w("")
    w("1. **B with the hood of A** (22 printed pieces). B has the fewest pieces, and its centre seams (rear wall, door) "
      "are filled or lie on the back. The hood of A (three pieces at x = +-106) replaces B's hood halves: A's centre "
      "piece is a straight extrusion that prints with no support and no layer steps, where B's halves need support "
      "across the marquee opening; and B's hood halves stop fitting when the cabinet is 9 wider (see \"Width\").")
    w("2. **A** (24): the same structure and the same print quality, two more pieces on the back; the most tolerant "
      "of a wider cabinet (fits beyond 575).")
    w("3. **C** (30 and a 2020 frame): its strength was dry, removable seams with no filler. The owner fills and paints "
      "and does not take the shell apart, so that strength no longer counts, and the frame costs parts, tools and room. "
      "Before the owner's answer the ranking was A, B, C.")
    w("")

    # ---------- per option ----------
    for key, opt in opts.items():
        res = meas["options"][key]
        lines_ = json.load(open(os.path.join(OUT, key, "seams.json")))
        w(f"## {opt.title}")
        w("")
        w(opt.idea)
        w("")
        sheet = "chosen.png" if key == sp.CHOSEN else f"option-{key}.png"
        w(f"Drawings: `{sheet}`, `structure-{key}.png`, `renders/{key}/`.")
        w("")
        w("### Pieces")
        w("")
        w("| # | Piece | Print box (mm) | Fits | On the bed | Skin (g) | Seen (cm2) | Seen face over 45 deg (cm2) | Shallow tops (cm2) | Why this way |")
        w("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        nums = {n: i + 1 for i, n in enumerate(n for n in res["pieces"] if not n.startswith(("base", "floor")))}
        pieces = {p.full: p for p in sp.expanded(opt)[1]}
        for n, r in res["pieces"].items():
            p = pieces[n]
            why = "as R" if p.side == "L" and (n[:-1] + "R") in pieces else p.why
            w(f"| {nums.get(n, '')} | {n} | {fmt(r['x'])} x {fmt(r['y'])} x {fmt(r['z'])} | {'yes' if r['fits'] else '**no**'} | "
              f"{p.bed} | {r['mass_g']} | {r.get('seen', '')} | {r.get('overhang_seen', '')} | {r.get('terrace_seen', '')} | {why} |")
        w("")
        w(f"Skin of the printed pieces without the floor: {skin_kg(res['pieces']):.2f} kg (solid 4 mm skin; ribs and flanges "
          "not in it). The floor tiles are measured as the 4 mm floor of the skin; the floor that the owner chose is 7 mm "
          "(see \"Floor\"). \"Seen face over 45 deg\": area that a person sees and that needs support in this orientation. "
          "\"Shallow tops\": faces seen at 1 to 25 degrees from level, which show layer terraces before primer.")
        if res["problems"]:
            w("")
            w("Problems of the cut: " + "; ".join(json.dumps(q) for q in res["problems"]))
        w("")
        w("### Seams")
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
        w(f"**Rear door.** {opt.door}")
        w("")
        if opt.against:
            w(f"**Against it.** {opt.against}")
            w("")

    # ---------- alignment ----------
    w("## Alignment and dry assembly (chosen layout)")
    w("")
    w("The owner asks: are all the panels keyed together, how is the structure aligned, and can it be dry-fitted "
      "before finishing? Yes to all three, in the concept: every seam of the chosen layout has a feature that sets "
      "its place, and the whole shell goes together with screws only before any adhesive. None of these features is "
      "modelled yet; they are drawn on `joints.png` and their values are named (`structure.JOINT`).")
    w("")
    w("**Datum.** The floor, its nine tiles screwed together (joint 2), on a flat table. Every lower piece stands on "
      "it with a key under its foot flange (joint 3). The rest is set by the pieces below it.")
    w("")
    w("| Seam | Joint | What locates it | Fixes |")
    w("| --- | --- | --- | --- |")
    for seam_, joint, feat, fixes in st.ALIGNMENT:
        w(f"| {seam_} | {joint} | {feat} | {fixes} |")
    w("")
    w("Fixes: n, square to the seam (the butt); t, across the wall (the key, so that the faces lie flush); s, along "
      "the seam (a cone or a node). A key alone fixes n and t; each seam therefore has at least one cone or node.")
    w("")
    w("**Order of assembly**: floor; rear lower halves; deck nose and deck sides; apron and the two lower pieces "
      "(through S1, D1, D2, F1, F2, P1); the fixed monitor cradle, put in from the top; the two middle pieces (L1); the "
      "BC-250 carrier and the power supply through the door opening; the two upper pieces, the brow and the upper rear, "
      "set in from above (B1, W1, R1, R3); the door, the hood, the bezel plate and the control panel.")
    w("")
    w("**Where each ring closes.** The L1 ring (sides and rear) closes at the second middle piece; the B1 ring closes at "
      "the upper rear, which drops in between the two upper pieces; the top ring closes at the brow, which drops in "
      "between the two upper pieces at the front. The closing piece goes in last, from above, into two seams at once, "
      "so those two seams get 0.5 mm of design gap at each side: the methacrylate fills gaps of 0.25 to 3.2 "
      "(`docs/research/petg-finishing.md`). Every other seam has 0.2 (the key clearance; the coupon sets it).")
    w("")
    w("**Trapped pieces.** None, if the order above is kept. Two pieces need the order: the fixed monitor cradle "
      "(422 wide) goes in from the top before the upper pieces, or later through the bezel opening (434.7 wide with no "
      "side ledge); the power supply (86 tall) goes in through the door opening (186 tall) and is lifted over the "
      "112 mm sill before the BC-250 carrier is in.")
    w("")
    w("**A thread-forming screw driven again into the same hole.** The dry pass drives each screw once, the bonding "
      "pass a second time. How many times a thread-forming screw holds in printed PETG (or ABS) is **unknown**: no "
      "source was found. The coupon test must count it: drive, remove and drive again five times, and measure the "
      "torque at which the thread strips each time.")
    w("")
    w("**Seams with no locating feature yet**: none in the concept. In the model, none of the features exists.")
    w("")

    # ---------- floor and hand-holds ----------
    fl = st.floor_options(0.0)
    w("## Floor")
    w("")
    w(f"The 7 mm sandwich was chosen for room, not for stiffness. Compared here: the floor under the power supply when "
      f"the cabinet is lifted ({fl['load_N']:.0f} N: the supply with a factor of 2), as a strip 150 wide from the deck's "
      "back frame to the rear wall (329 span), and at a tile joint:")
    w("")
    w("| Section | Sag under the supply (mm) |")
    w("| --- | --- |")
    for k, v in fl.items():
        if isinstance(v, dict):
            w(f"| {k} | {v['sag_mm']:.2f} |")
    w("")
    w(f"Recommendation: **the 7 mm sandwich with ribs under it** ({fl['rib_h']:.0f} deep, 2.4 thick, every 50, a rib "
      "splice bonded across each tile joint). It is the stiffest, it keeps the power supply where it is (z 7), and "
      f"the ribs use room that is free: the cabinet stands on feet **{fl['foot_h']:.0f} mm high**, which also give the "
      "make-up air its inlet under the floor and room for fingers at the front grip. The 10 mm sandwich would raise "
      "the power supply and the BC-250 by 3 mm. At a tile joint the bonded lap alone is weaker than the ribbed tile, "
      "so the rib splice carries the ribs across it.")
    w("")
    hh = st.hand_holds(st.total_mass(skin_kg(meas["options"][sp.CHOSEN]["pieces"]), FLOOR_DM2)["total"], 396.0)
    w("## Hand-holds")
    w("")
    w(f"The centre of mass is about y {hh['com_y']:.0f}, {hh['com_to_rear']:.0f} in front of the rear plane (estimated). "
      "Three places, compared:")
    w("")
    w("| Grip | Balance | Load path | Sanding reach | Seen from the seat |")
    w("| --- | --- | --- | --- | --- |")
    w(f"| pockets up into the overhang of the upper rear (40 proud), near each rear corner | {hh['rear_only']}; with a "
      f"second grip under the deck nose the rear grips take {hh['rear_N_each']:.0f} N each and the front {hh['front_N']:.0f} N "
      f"({hh['rear_share']:.0%} / {hh['front_share']:.0%}) | into the slope and the B1 ring in the slope crease, in shear "
      "and tension (no peel at the bond) | yes: open downward, 100 x 25 deep | no |")
    w("| recesses in the rear corner faces | as above | into the corner of the side and rear walls, across the L1 and B1 "
      "rings | finger only: three inside corners | no (seen from the side) |")
    w("| recesses in the side band under B1 (the earlier proposal) | balanced: they bracket the centre of mass, so one "
      "person lifts it level | into the B1 ring | yes | partly, from the side |")
    w("")
    w("Recommendation: **the pockets under the overhang at the back corners, with a front grip under the deck nose** "
      "(in the 18 mm that the feet give). Lifted at the back alone the cabinet tips onto its deck front, so a carry "
      "uses both grips: two people, or one who lifts the back and slides a hand under the nose. If the owner wants "
      "one person to carry it level, the side recesses are the grip for that.")
    w("")

    # ---------- structure ----------
    w("## Structure")
    w("")
    a = meas["options"]["A"]["pieces"]
    mass = st.total_mass(skin_kg(a), FLOOR_DM2)
    est = st.estimates(mass, d)
    com = centre_of_mass(a, mass)
    w("**A and B: a stressed skin.** The skin carries the loads. Each bonded seam has an inside flange on both pieces "
      "(joint 1), and these flanges are the ring frames: L1 at the bezel's bottom corner and B1 at the slope crease run "
      "round the sides and the rear; the top ring under the groove closes the open body top and carries the hood; the "
      "flanges of D1 and D2 make a frame across the back of the deck; the flanges round the door opening make the rear "
      "ring, which the door closes when it is screwed shut. The printed floor is the datum: every lower piece bolts to "
      "it. The hardware carriers are cross-members: the fixed part of the monitor cradle between the two rails, the "
      "carrier of the BC-250, the control panel frame. Ribs on the inside of the large near-flat walls (side band, rear "
      "side, rear wall) keep them flat. `structure-A.png`, `structure-B.png`.")
    w("")
    w("**C: a chassis with a skin.** A frame of 2020 aluminium extrusion stands on the printed floor and carries all the "
      "hardware; it stands without the shell. The shell pieces hang on it with screws into the frame's slots and carry "
      "no load. The frame is the only one that fits the room the hardware leaves (checked below). `structure-C.png`.")
    w("")
    w("Frame of C, each member placed in the cavity and against the boxes of the fit study's hardware and keep-out zones "
      "(`candybar.shell.structure`):")
    w("")
    w("| Member | Length (mm) | In the skin (mm3) | Hits | Nearest item (mm) | Note |")
    w("| --- | --- | --- | --- | --- | --- |")
    for r in struct["frame"]:
        hits = ", ".join(h["item"] for h in r["hits"]) or "none"
        w(f"| {r['member']} | {r['length_mm']} | {r['in_skin_mm3']} | {hits} | {r['nearest_mm']}: {r['nearest']} | {r['note']} |")
    w("")
    w(f"Where the frame of C does not fit, plainly: no member reaches the rear corners, because the power supply (left) "
      "and the exhaust duct fill the left rear corner and the rear wall leaves only 8 mm beside the door opening; so C "
      "has no rear posts, and the rear of its frame is a beam above the door on two arms. The side rails cannot run "
      "upright: the rails of the cabinet and the bezel leave room only for a rail inclined 30 degrees, between the "
      "monitor's plug space (x 210) and the side wall (x 241.7, the wall is 5.6 thick there), with 0.9 mm to the hub "
      "at its foot. The tuck stops the rails at z 350; a short post goes on to the top beam, and it still nicks the "
      "skin by 0.2 cm3 at the tuck (trim its corner by 3 mm). The two monitor beams sit 1.2 and 2.9 mm from the room "
      "for any 16:10 monitor. The floor (7 mm) meets the hub, which stands on the 4 mm floor now (see \"Floor\").")
    w("")
    w(f"Cost of the frame of C: {struct['frame_length_m']:.1f} m of 2020 extrusion, {struct['frame_kg']:.1f} kg (ESTIMATED at "
      f"{st.EXTRUSION_KG_M} kg/m), about 16 corner brackets, 60 T-nuts and screws, a saw and a drill or a cutting "
      "service; and the room: 20 mm round the monitor room at both sides and behind it.")
    w("")
    w("### Mass")
    w("")
    w("| Part | kg | Status |")
    w("| --- | --- | --- |")
    w(f"| skin of the printed pieces (option A) | {mass['skin']:.2f} | measured from the cut |")
    w(f"| ribs, flanges, splice plates, inserts (25 % of the skin) | {mass['joints_and_ribs']:.2f} | estimated |")
    w(f"| floor, 7 mm sandwich, {FLOOR_DM2:.0f} dm2 | {mass['floor']:.2f} | estimated |")
    for item, kg, status, src in st.HARDWARE:
        if kg:
            w(f"| {item} | {kg:.2f} | {status}{': ' + src if src else ''} |")
    w(f"| **total, A or B** | **{mass['total']:.1f}** | estimated |")
    w(f"| frame of C, more | {struct['frame_kg']:.1f} | estimated |")
    w("")
    w(f"Centre of mass (A, estimated): {com[0]:.0f} behind the deck front, {com[1]:.0f} above the desk.")
    w("")
    w("### Load cases")
    w("")
    ll = est["lift"]
    w(f"- **Lifted by the hand-holds** with all hardware: {ll['weight_N']:.0f} N. Two holds with a factor of 2 for a jerk: "
      f"{ll['per_hold_N']:.0f} N each. Path (chosen): the grips are pockets in the overhang of the upper rear at the back "
      f"corners, with a front grip under the deck nose (see \"Hand-holds\"); the load goes into the B1 ring in the "
      f"slope crease and down the walls to the floor, which carries the power supply (3.3 kg). Shear in 100 mm of flange in a 4 mm wall: "
      f"{ll['flange_shear_MPa']:.2f} MPa, far below the strength of PETG. Path (C): the hold is a printed handle "
      "screwed to the side rail; the skin carries nothing.")
    w(f"- **A person leans on the deck front, 200 N**: compression in the front wall of the deck nose, "
      f"{est['lean']['stress_MPa']:.2f} MPa, straight into the floor. The flank seams F1 and F2 are 62 mm outside the lever "
      "axis and in compression here, not in peel. **A hit on the control panel**, 200 N at its centre: the 2.0 mm "
      f"aluminium plate bends {est['panel']['deflection_mm']:.2f} mm on its ledge (simply supported; the cover makes it "
      "stiffer). A printed PETG plate 5 mm thick bends about three times as much: give it ribs under the plate outside "
      "the button field (controls-ergonomics.md: no rib fits between buttons at 36 pitch).")
    rk = est["racking"]
    w(f"- **50 N sideways on the hood**: {rk['moment_body_top_Nm']:.1f} N m at the groove, {rk['moment_floor_Nm']:.1f} N m at "
      "the floor. The hood's pins and screws take the shear at the groove; the top ring carries it into the body. In "
      "the body the front portal (rails, apron, brow round the bezel) and the rear portal (round the door) resist it; "
      f"a portal of two rails 300 tall sways about {rk['portal_mm']:.2f} mm (ESTIMATED section). The rear portal is the "
      "weak one: the rear wall leaves strips of only 12 mm beside the door. The door, screwed shut all round, closes "
      "it. In C the frame takes it.")
    w(f"- **20 N with a finger on the largest spans** (4 mm skin, simply supported, centre load):")
    for k, v in est["finger"].items():
        w(f"  - {k}: {v:.2f} mm")
    w(f"  Rib rule: to keep this under 0.3 mm, put a rib or a flange at most {est['rib_spacing_mm']:.0f} mm apart on a 4 mm "
      f"wall ({est['rib_spacing_3mm']:.0f} mm on 3 mm). Ribs 8 deep, 2 thick at the root.")
    mo = est["monitor"]
    w(f"- **The monitor on its cradle, long term**: 0.82 kg at 30 degrees of recline puts {mo['along_face_N']:.1f} N along "
      f"the face on the bottom clamps and {mo['into_cradle_N']:.1f} N into the cradle. In a clamp tab 20 wide and 4 thick "
      f"with the load 10 from its root: {mo['clamp_stress_MPa']:.1f} MPa, below the {mo['creep_limit_MPa']:.0f} MPa that this "
      "proposal uses as the limit for sustained load on PETG (ESTIMATED). The fixed part of the cradle is screwed to "
      "the rails' inner flanges at four corners, so no clamp hangs on a thin skin.")
    w(f"- **Warm air**: the exhaust is about {est['heat']['exhaust_dT_K']:.0f} K above the intake at 200 W "
      "(bc250-cooling-and-psu.md). The owner has a PETG case for a BC-250 in use that does not soften, so this "
      "proposal sets no temperature limit on PETG near the air path.")
    w("")
    w("**Weak points, honestly.** (1) The three large openings: the bezel opening (422.7 x 293.4) leaves the rails as "
      "the only members up the front; the control panel opening leaves a 25 mm nose and two arms of 48 mm; the door "
      "opening leaves 12 mm strips at the rear corners. Each opening needs its plate or door screwed shut to be "
      "stiff, so the bezel plate (on magnets) adds nothing, and the rails and the monitor cradle's fixed frame between "
      "them must do the work. (2) The rail land beside the bezel's top corners is 9 mm wide and in the upper pieces; "
      "keep it out of any seam (it is: L1 and B1 cross the land where it is 16 wide) and stiffen it with the top "
      "ring. (3) Joints in peel: a flange that a load pries open. The hand-hold must pull the flange in shear, not "
      "peel it; the hood's screws pull in tension, so they go into inserts in the top ring, not into the skin.")
    w("")

    # ---------- mounts ----------
    w("## Mounts")
    w("")
    for key in ("A", "C"):
        w(f"| Component ({'A and B' if key == 'A' else 'C'}) | Mount | On |")
        w("| --- | --- | --- |")
        for m in st.mounts(key):
            w(f"| {m.item} | {m.how} | {m.on} |")
        w("")
    w("**The BC-250 on a fixed mount (the owner, record 0005).** The rear door is a cover with the vents and nothing "
      "wired to it. The BC-250 stands on its long edge where the fit study has it, on a printed carrier: two uprights "
      "joined by rails that hold the board's edges (as the MKUU+ case does). The right upright stands on the floor "
      "(x 130 to 155, clear of the power plug and the cable bundle); the left one has no floor under it, because the "
      "power supply is there, so it stands on the sill of the door opening and screws to the opening's flanges. Its "
      "lower rail sits 6 mm into the 25 mm air space over the power supply's fan; 19 mm stay, more than the 12.7 mm "
      "minimum of the ATX guide. The shroud and the duct stay with the board and meet the door with a soft seal.")
    w("")
    mv = struct["compute_move"]
    first = next((m for m in mv if m["dy"] > 0 and m["hits"] and len(m["hits"]) > len(mv[0]["hits"])), None)
    w(f"How far it must move for the seal: **0 mm**. The fan's face is already 5 mm from the door (`bc_gap_door`), and "
      "the shroud ends there; the duct's rigid wall must end 5 mm short of the door, and a foam strip (8 free, 5 "
      "closed) fills the gap on both. The module cannot move forward: checked with the solids of `fit.py`, moved "
      f"forward by 2 mm its underside air space enters the monitor's cable channel across ({first['hits'] if first else ''}). "
      "At 0 mm the exhaust duct already shares 7.2 cm3 with the power supply's fan space (both are keep-out zones, "
      "which the fit study does not compare). To change in `fit.py` later: the duct's rigid depth (70 to 65) and the "
      "seal; and, if more room is wanted, the cable channel across (y 430 to 450) moves down or forward.")
    w("")
    w("**The air zones in the fit study (new rule R2b).** The fit study compared a solid only with the keep-out zones of "
      "others, never two zones, so it missed the overlap of the duct and the power supply's fan space. It now compares "
      "each air zone (exhaust duct, fan shroud, the air under the board, the fan space of the power supply) with every "
      "solid of another item, and a test fails when two of them overlap. Its rows in `fit/report.md`:")
    w("")
    w("| Level | Subject | Detail |")
    w("| --- | --- | --- |")
    for lv, subj, det in fit["rules"].get("R2b air zones", []):
        w(f"| {lv} | {subj} | {det} |")
    w("")
    w(f"Result of the fit study: **{fit['result']}**. The fix: the BC-250 stands 1 mm higher (`Layout.bc_above_psu` 2 to "
      "3), so its duct no longer reaches into the 25 mm over the supply's fan; the hub stands on the 7 mm floor "
      "(`Layout.floor_t`). The duct's keep-out zone stays 70 deep: the rigid duct (65) and the 5 mm seal to the door.")
    w("")
    w("Reach: lift the door off (four thumb screws). The fan and the shroud face are then in the opening; the board's "
      "I/O end (DisplayPort, LAN, USB) is at the left end, behind the duct: two screws take the duct off. The power "
      "plug and the fan header are at the top right of the board, 0 to 20 mm above the top edge of the opening, and "
      "a hand reaches them from below. The board comes out through the opening (446.7 x 186) on its carrier rails.")
    w("")
    pathm = struct["monitor_path"]
    free = max(m["out_mm"] for m in pathm if m["in_skin_mm3"] == 0)
    ps = fit["monitor"]["pass"]
    w(f"**The monitor comes out to the front (decided).** The opening behind the bezel has its ledge at the top and the "
      f"bottom only (`cavity.Openings.bezel_side_ledge` = 0), so it is {2 * ps['opening_half']:.1f} wide. The fit study "
      f"reports: any 16:10 monitor with its right-angle plug space passes with {ps['room_gap']:.1f} on each side; its "
      f"carrier with the side flanges passes with {ps['flange_gap']:.1f}. The carrier's side flanges (4 wide) hold the "
      "sides of the bezel plate; behind the 1 mm reveal the rail's recess wall closes the gap. The plate fastens with "
      "no tool: magnets on the fixed part of the cradle (or a magnet in the plate against a steel strip on it), so that "
      "the 8 mm adjustment of the carrier does not move the plate; two pins in the bottom ledge set its place; a "
      "finger notch in its lower edge lifts it off. Check the monitor for a magnetic sleep sensor before the magnets "
      "go near its edge. Checked with "
      f"the solids of `fit.py` moved out square to the screen: the room comes {free:.0f} mm out with no contact with the "
      "skin. The adjustment of 8 mm each way is made from the front, with the plate off, on slotted holes in the "
      "carrier. Cable slack: the monitor must come about 50 mm out before the plugs at its side edges are in reach "
      "(20.6 monitor, 7.2 behind the chord, up to 13 of rail arc in front of it, and the carrier), so give each lead "
      "150 mm of slack in its channel. Straight plugs never pass the opening: the monitor comes forward with "
      "right-angle plugs in place, or the cables come off by hand first.")
    w("")
    w("**Floor (the owner: printed PETG).** Nine tiles (the bed is 256; each tile is at most 212 x 190). Section: a "
      f"sandwich {st.FLOOR_T:.0f} mm thick, two skins of {st.FLOOR_SKIN} mm and a gyroid core of {st.FLOOR_INFILL:.0%}. "
      f"Its stiffness is {est['floor']['sandwich_Nmm'] / est['floor']['solid4_Nmm']:.1f} times that of the 4 mm floor of "
      f"the skin; the power supply on one tile sags {est['floor']['psu_sag_mm']:.2f} mm (with a factor of 2). The tiles "
      "join with half-laps (joint 2): the ring flanges of the walls cross the tile joints, so that no joint is a "
      "hinge. Room: the power supply stands 3 mm above the present 4 mm floor, so a 7 mm floor costs no room under it. "
      "The hub stands on the 4 mm floor now (z 4.1): it must rise 3 mm (a change for `fit.py`). Under the cabinet, "
      "ribs could go down into the 10 mm that the feet give, if the floor must be stiffer.")
    w("")
    w(f"**Control panel plate, printed PETG (the owner, for proving).** The outline (396 wide) is wider than the bed, "
      f"so the plate has one seam. It goes across at x = {seam['x']}, between the lever and the buttons: "
      f"{seam['nearest'][2][0]:.1f} mm from the lever's mounting plate, {seam['nearest'][1][0]:.1f} mm from the nut of "
      f"button 1, {seam['nearest'][0][0]:.1f} mm from the lever's body under the plate. The halves are "
      f"{seam['halves'][0]} and {seam['halves'][1]} wide (the larger one fits the bed with 0.8 mm). The halves join "
      "under the plate on a printed splice bar 30 wide, bonded and screwed with thread-forming screws, with two pins; "
      "the bar runs between the lever plate and button 1 and is clear of both. The cut clear cover (one piece, 396 "
      "wide, with the art under it) hides the seam on top. Thickness: Sanwa snap-in buttons take 3.9 mm at most "
      "(controls-ergonomics.md: design 3.0 to 3.5), the plate and the cover together. A printed plate needs 5 mm or "
      "more to be stiff, so each snap-in seat is thinned from below to 2.0 mm round a 30 mm hole (2.0 + 1.5 cover = "
      "3.5); or use screw-in buttons (OBSN-30: 5 max, 6 with the nut fully engaged), which take a 5 mm plate without a "
      "seat. The lever mounts from below through the plate as before. The cut aluminium plate stays the later choice "
      "with the same outline.")
    w("")

    # ---------- cables, air ----------
    w("## Cable routes")
    w("")
    w("`services.png`. X marks a plug where a part opens for service.")
    w("")
    w("| Route | Where it runs, and what it crosses |")
    w("| --- | --- |")
    for r in st.ROUTES:
        words = r.crossings.replace("The door opens: unplug at the board, and a 150 mm loop lets the door swing down first.",
                                    "The door carries nothing, so this lead stays in place when the door comes off.")
        w(f"| {r.name} | {words} |")
    w("")
    w("No route crosses a bonded seam where it matters: the leads cross D2 and L1 inside the cabinet, under the flanges. "
      "Leave a gap of 15 mm under each flange at a crossing, or a notch in the flange.")
    w("")
    w("## Air path")
    w("")
    w("| Part | Belongs to | What it does |")
    w("| --- | --- | --- |")
    for part, on, what in st.AIR:
        on = on.replace("door's inner frame", "the BC-250's carrier")
        w(f"| {part} | {on} | {what} |")
    w("")
    w("**A second fan in the exhaust duct (the owner's idea).** The duct of the fit study is 106.3 x 129 in section "
      "along the door and 70 deep. A 92 mm fan (92 x 92 x 25) fits in front of the slot vents with 7 mm round it; it "
      "takes 25 of the 70 mm depth and leaves 45 mm of plenum. An 80 mm fan fits with more room; a 120 mm fan does "
      "not (129 tall but only 106 wide). The tightest point of the path is the passage through the fins (about 3,119 "
      "mm2), so the second fan does not add flow by its size; it adds pull (push-pull), which research reports as a "
      "small gain on this heatsink (\"the stock heatsink is the limiter, not the fans\"). It needs: four screw bosses "
      "on the duct (it stays with the BC-250, not on the door), the soft seal round its face to the door, and a 4-pin "
      "lead to a fan header (a Y-splitter on the P12's header if the board has only one). It is dashed on "
      "`services.png`. Recommendation: leave room and bosses for it, and fit it only if the closed-cabinet test of "
      "the brief shows a need.")
    w("")

    # ---------- joints ----------
    w("## Joints")
    w("")
    w("`joints.png`. Every bonded joint works in two steps: a key, cone or pin sets the one right place, so that a dry "
      "assembly held by screws alone has its final shape; then the same joint is bonded, the screws clamp it while the "
      "adhesive cures and stay in, and filler goes into a V-groove on the outside.")
    w("")
    w("| Joint | Locates | Clamps and stays | Spacing | Bond area | Outside | Prints without support |")
    w("| --- | --- | --- | --- | --- | --- | --- |")
    w("| 1 skin to skin (wall or curved face) | inside flange 6 x 12 on both pieces, a key 1.5 x 4 on one face in a groove "
      "of the other (+0.2, the coupon sets it) | thread-forming screw 3.0 x 16 for plastics through both flanges | 60 | "
      "12 per mm of seam, plus the 4 mm butt | V-groove 1.0 wide, 0.8 deep | yes: a level flange has a 45 deg gusset under it; "
      "an upright flange is a wall |")
    w("| 2 floor tile to tile | half-lap 20 wide, each lap 3.5; a cone 8 x 3 in the lower lap, socket in the upper | "
      "thread-forming 3.5 x 12 from below | 50 | 20 per mm | none (under the cabinet) | yes: both laps print flat |")
    w("| 3 wall foot to floor | key 3 x 2.5 under the foot flange in a slot of the floor | thread-forming 3.5 x 16 up from "
      "below | 80 | 12 per mm | none | yes: the flange is at the bed in the upright print |")
    w("| 4 node (three pieces meet: L1 or B1 with S1, P1 with L1, the rear corners) | a cone in each flange, sockets in a "
      "node plate 24 x 24 x 4 | one thread-forming screw into each piece | one plate | the plate | none | the plate prints flat |")
    w("| 5 service (door, hood, bezel plate, panel, USB plate) | two pins 4 dia, +0.1 | M4 heat-set insert in the fixed part, "
      "M4 screw | 80 to 100 | none: never bonded | chamfer 0.5 on both edges | yes: bosses on the flanges, inside |")
    w("")
    w("Adhesive and filler: the classes of `docs/research/petg-finishing.md` (section 1), to prove on the coupon. No "
      "strength for printed PETG is claimed.")
    w("")
    w("- Bond: a slow two-part methacrylate (example Plexus MA310), first candidate; two PETG sheet makers list it, it "
      "fills gaps of 0.25 to 3.2, and it gives 15 to 18 minutes of working time. Second candidate: a solvent cement "
      "that lists PETG, run into the clamped flange (no gap filling). The 3M plastic adhesives for polyolefins are a "
      "poor fit.")
    w("- Groove: a two-part polyester glazing putty that lists plastics (example Evercoat Metal Glaze), thin, not "
      "polyester body filler (its data sheet does not list thermoplastics, and it cracks over seams that flex). "
      "Optional, if the coupon allows: weld the groove with the same PETG (friction weld or a 3D pen) before the putty.")
    w("- Wet-sand PETG (it gums dry), scuff and prime every face; never put colour on bare PETG.")
    w("")
    w("Because the methacrylate works for 15 to 18 minutes, bond a few pieces at a time: one batch is one to three "
      "seams, about 500 mm of seam at most, all screwed in the dry pass and only opened and glued in that batch.")
    w("")
    w("**Coupon test before the real parts** (the brief asks for a 100 to 150 mm two-piece curved coupon; `joints.png`, "
      "panel 6): three pairs of joint 1 on a curved face of radius 300, printed in the real orientation, with groove "
      "clearances of +0.1, +0.2 and +0.3. It must prove: the clearance that locates with no play and no force; the "
      "adhesive (bonded pair pulled and bent to failure: the break must be in the plastic, not in the bond); and the "
      "filler and paint over the joint after the pair is bent to the deflection of the finger case (0.3 to 0.8 mm over "
      "the span) a few hundred times: no line may show.")
    w("")
    w("**Assembly in two passes.** Pass 1, dry: screw every bonded joint with its thread-forming screws, fit all the "
      "hardware, run the brief's dry-assembly tests (section 4), and correct the fit. Pass 2, bond, in batches of one "
      "to three seams: open the batch, put adhesive on its flange faces, screw it again in the same holes, let it cure; "
      "next batch. Order of the batches: floor tiles; rear lower pieces to the floor; deck; apron and lower pieces; "
      "middle pieces; top tier; then separately the hood pieces, the door pieces and the bezel halves. Then fill the "
      "V-grooves, sand, prime and paint. The finish pieces are painted alone and fastened last.")
    w("")
    for key, opt in opts.items():
        w(f"- {opt.title}: " + " ".join(f"({i}) {s}" for i, s in enumerate(opt.assembly, 1)))
    w("")

    # ---------- finishing ----------
    w("## Finishing")
    w("")
    w("**Finish pieces** (another colour, or a tight corner with the neighbour): each is painted alone and fastened from "
      "the inside after the paint, with no fastener on the outside.")
    w("")
    w("| Piece | Why | How it fastens from the inside |")
    w("| --- | --- | --- |")
    w("| bezel plate (black) | colour; tight reveal | magnets and pins (service); its halves are bonded and painted together |")
    w("| speaker forms (2, black) | colour; they stand 13 proud of the band, 4 above the ledge and 8 from the legs | "
      "two M3 screws each from behind the hood band into inserts in the form |")
    w("| logo form (green) and logo plate | colour | two M3 screws from behind the band |")
    w("| marquee lip | a 5 mm edge in the 36 mm marquee opening, under the 3.5 mm soffit: no sanding reach | it is part of "
      "the hood now (the cut fuses it); make it a separate white piece (393 long: two halves of 197), screwed from behind "
      "the band |")
    w("| marquee cover | tinted, not printed | screwed from inside to the hood's leg flanges |")
    w("| control panel and its cover | colour, art | the panel latch |")
    w("")
    w("Audit of the exterior with the bonded shell as one piece (block: a 25 mm sanding block; finger: a finger with "
      "paper):")
    w("")
    w("| Place | Width, depth, angle | Block | Finger | Proposal |")
    w("| --- | --- | --- | --- | --- |")
    rows = [
        ("groove between hood and body (FB5 / HC15)", "gap 1.5, bevel 3 x 3 on each part", "yes, on each part apart",
         "yes", "accept: the hood is a separate part (service), so each bevel is an outside edge when it is finished; the bonded "
         "seams' V-grooves take glazing putty, not body filler"),
        ("marquee opening under the top bar", "36.1 high, 3.5 to 4.8 deep; soffit 3.5", "no", "yes",
         "accept the soffit (a strip of 3.5; paper on a stick); make the lip a finish piece"),
        ("lip with its 5 mm edge", "6 high, 5 proud, 90 deg corners", "no", "partly", "finish piece (above)"),
        ("ledge on the sill and the band behind it", "ledge 13.9 deep, 90 deg inside corner to the band", "no", "yes",
         "accept; with the speaker forms off, the band is open"),
        ("speaker forms on the band", "13 proud; gap 4 above the ledge, 8 to the legs", "no", "no",
         "finish pieces (above): the gap of 4 under a 13 overhang cannot be sanded"),
        ("bottom corners of the hood opening", "radius 6, inside", "no", "yes",
         "accept; or radius 10 (a change for the owner)"),
        ("reveal round the bezel plate (BZ4)", "1 wide, 2 deep; the recess behind it 9 to 20 deep", "n/a", "no",
         "accept: only the rail land's edge shows; spray the recess walls"),
        ("pocket of the control panel (DK8)", "1 wide, 2 deep; seat 5 below the top", "n/a", "no",
         "accept: spray; the panel covers it"),
        ("concave bend between deck and screen face (FB1)", "radius 50, turns 68 deg", "no (a flat 25 block "
         "touches only along a line)", "yes", "accept; sand with a foam pad of radius 40 or less"),
        ("crease behind the stripe (RL3 / RL4)", "a turn of 10 deg, open", "yes", "yes", "accept"),
        ("the step (RB2)", "12 deep, 45 deg in plan, inside corners of 135 deg", "yes", "yes", "accept"),
        ("rear corner faces (HC16) and rear corners", "45 deg faces, outside corners", "yes", "yes", "accept"),
        ("rear door vent slots", "not designed", "n/a", "n/a",
         "make the slots 4 wide or more; the door is finished apart (service part)"),
        ("flank break and panel corner on the deck nose", "crease R 6, open", "yes", "yes", "accept"),
    ]
    for r in rows:
        w("| " + " | ".join(r) + " |")
    w("")
    w("Proposed changes of the form for the owner to approve: none is needed. Optional: a radius of 10 at the bottom "
      "corners of the hood opening (6 now).")
    w("")
    w("**Inside features that can print through.** A heat-set insert boss or a thick rib behind a 4 mm wall changes "
      "how the wall cools and can show as a mark on the outside. Rules: no boss on the back of a large visible face "
      "(side band, deck front, apron, hood top bar): bosses sit on the flanges, square to the skin; ribs are 2 thick "
      "at the root (half the wall) with a small fillet; the thread-forming screws of the bonded joints go through the "
      "flanges, never into the skin.")
    w("")

    # ---------- width ----------
    w("## Width")
    w("")
    w("**Decided: +0 (494.7).** The width study's candidates were 494.7 (now), 514.7 with the growth in the rails "
      "only, 514.7 split (its recommendation: each rail land +5 and each side bar of the bezel frame +5, so the bezel "
      "plate is 444.7 wide, with no ledge at the sides of the plate), and 533.2. The usable bed stays "
      f"{lim['xy']:.0f} (params/printer.csv). Model: each piece's points outside x = +-218.3 (body, floor) or +-174 (hood) "
      "move out by half the growth, and the print box is measured again; the seams stay where they are. ESTIMATED: the "
      "split variant also moves the bezel's side bars, which this model puts into the rails.")
    w("")
    w("| Option | Widest that fits | At 514.7 | At 533.2 | Seam it adds |")
    w("| --- | --- | --- | --- | --- |")
    for key, opt in opts.items():
        wd = width[key]
        f = lambda bad: "fits" if not bad else "no longer fit: " + ", ".join(bad)
        fam = sorted({b.rsplit(" ", 1)[0] for b in wd["at_20"] + wd["at_38"]})
        adds = "; ".join(REMEDY.get(n, n) for n in fam) or "none"
        w(f"| {opt.title} | {widest(wd)} | {f(wd['at_20'])} | {f(wd['at_38'])} | {adds} |")
    w("")
    w("A seam on the centre line has a hard limit: a half of W / 2 must fit the bed. At 514.7 a half of the body is 257.3, "
      "more than the bed itself (256). Thus the halves of B (hood, rear wall, door) are the first to fail, and the "
      "three-piece splits of A, whose side pieces take the growth, still fit beyond 575. The recommendation (B with the "
      "hood of A) fits at 514.7 with no new seam; at 533.2 its rear wall below the door and its door need the split of "
      "A (two pieces more).")
    w("")
    w("A bezel plate with no side ledge (the width study's recommendation) changes two things here. (1) The monitor "
      "passes the opening with 7.3 each side at 494.7 and 12.3 at 514.7 split, more than the 1.3 with the ledge. (2) "
      "Nothing closes the 1 mm reveal at the plate's sides from behind: the monitor carrier gets a flange on each side "
      "that stands behind the reveal and comes out with the carrier. The plate then rests and fastens at its top and "
      "bottom only: a lip on the bottom ledge, magnets and pins in the top and bottom ledges.")
    w("")
    w("**Seams that exist only because of the 256 mm bed** (method of `docs/research/abs-switch.md` section 6: usable = "
      "bed less 10; the plan stays PETG on the A1):")
    w("")
    w("| Seam | Why it exists | 300 bed (290 usable) | 350 bed (340 usable) |")
    w("| --- | --- | --- | --- |")
    for r in (("F1, F2, P1 (deck and apron in three)", "494.7 needs three pieces of 240", "two pieces: one seam on the centre line in place of two", "the same"),
              ("W1, H1 (brow and hood in three)", "the brow is 437, the hood 472", "brow and hood halves", "the same"),
              ("R2, R4 (rear wall and door in three, A)", "446.7 and 470.7 wide", "halves", "halves (446.7 > 340)"),
              ("floor tiles BA1 to BA3 (nine)", "487 x 532", "four tiles", "four tiles"),
              ("L1 (level at the bezel's bottom corner)", "the side band below B1 is 303 deep", "stays", "goes: one side piece from the floor to B1"),
              ("B1 (belt in the slope crease)", "the side above L1 is 290 tall", "stays", "goes only on a printer 300 tall"),
              ("D1, D2, S1, DR, the groove", "design breaks and service seams", "stay", "stay")):
        w("| " + " | ".join(r) + " |")
    w("")

    w("## Material")
    w("")
    w("The material is open: PETG on the A1 (the plan), or ABS on an enclosed printer. The seams, the pieces and the "
      "joint values do not change; the clearances are named values (`structure.JOINT`) that the coupon of each material "
      "sets. What changes for ABS (`docs/research/abs-switch.md`):")
    w("")
    w("| Step | PETG | ABS |")
    w("| --- | --- | --- |")
    for step, petg, abs_ in st.ABS_CHANGES:
        w(f"| {step} | {petg} | {abs_} |")
    w("")

    # ---------- bezel, recommendation, questions ----------
    bz = meas["options"].get("bezel", {})
    w("## The bezel plate")
    w("")
    for k, title, words in sp.BEZEL_OPTIONS:
        w(f"{k}. **{title}.** {words}")
    w("")
    if bz:
        beds = {p.full: p.bed for p in sp.expanded(sp.BEZEL)[1]}
        for n, r in bz["pieces"].items():
            w(f"- {n}: {fmt(r['x'])} x {fmt(r['y'])} x {fmt(r['z'])}, fits: {'yes' if r['fits'] else 'no'}, {beds[n]}, "
              f"{r['mass_g']} g solid, seen face over 45 deg {r['overhang_seen']} cm2.")
        w("")
    w(f"Recommendation: option {sp.BEZEL_RECOMMENDED}: two halves, bonded and painted black as one plate (a finish "
      "piece), fastened with magnets and pins (no tool).")
    w("")
    w("## Recommendation")
    w("")
    w("Decided by the owner: the chosen layout (B with the hood of A), +0 width, the hood keyed to bolt or to bond, "
      "a floor that is stiffer than 7 mm. Proposed, and not decided: the ribs under the floor with feet of 18 mm "
      "(the cabinet then stands 18 mm above the table), and the grips at the back corners with a front grip under "
      "the deck nose.")
    w("")
    w("**An internal frame: no.** Build a stressed skin (B with the hood of A) with a printed floor, ring frames from "
      "the seam flanges, and three cross-members that carry the hardware: the fixed monitor cradle between the rails, "
      "the BC-250 carrier on the floor and the door sill, the control panel frame. Reasons, with numbers:")
    w("")
    w(f"- The skin is strong enough for every load case: the highest stress is {est['lift']['flange_shear_MPa']:.2f} MPa "
      f"at a hand-hold; a finger push gives up to {max(est['finger'].values()):.2f} mm on the largest span, and ribs "
      f"{est['rib_spacing_mm']:.0f} apart bring it under 0.3 mm.")
    w(f"- A frame finds little room: the only path from floor to top on each side is an inclined rail with 0.9 mm to "
      "the hub and 1.2 mm to the monitor room; no rear posts fit at all. It adds "
      f"{struct['frame_kg']:.1f} kg, {struct['frame_length_m']:.1f} m of extrusion and about 16 brackets.")
    w("- The owner fills, paints and does not take the shell apart, so the frame's one strength (dry, removable "
      "panels) does not count.")
    w(f"- Total mass about {mass['total']:.0f} kg (estimated): light enough for two hand-holds.")
    w("- It survives the width study's recommendation (514.7) with no new seam; a frame would have to be redesigned for it.")
    w("")
    w("**Hood: keyed, then bolted (recommended) or bonded with the same parts.** The speakers, the marquee modules and their controller are in the "
      "hood, and the brief expects the marquee to change (\"A removable top module would allow this to evolve\"). "
      "Bolted, the hood lifts off (two pins, two M4 screws at the rear) and every part in it is in reach from below. "
      "Bonded, the speakers and the marquee would be reached only through the body (behind the monitor) or the hood "
      "band's openings.")
    w("")
    w("## Questions for the owner")
    w("")
    for q in (
        "Hood: bolt it (recommended), or bond it? The parts allow both.",
        "Grips: the pockets under the overhang at the back corners with a front grip under the deck nose (recommended), "
        "or the side recesses for a one-person level carry?",
        "Monitor: does the unit have a magnetic sleep sensor near its edge (then the bezel plate's magnets move to a "
        "steel strip away from it)?",
        "The second fan in the duct: leave room and bosses only, and fit it after the closed-cabinet test?",
        "Control panel plate for proving: a 5 mm printed plate with thinned seats for snap-in buttons, or screw-in "
        "buttons?",
        "The marquee lip as a separate finish piece (two halves): accept?",
        "Bottom corners of the hood opening: keep radius 6, or 10 for sanding?",
        "Material: PETG on the A1, or ABS on an enclosed printer? The coupons of both decide it.",
    ):
        w(f"1. {q}")
    w("")
    w("## How the numbers were made, and what is not checked")
    w("")
    w("- The skin is the outer form less the cavity of `cavity.py`; its inner face is stepped (1 mm slabs). The cut "
      "removes a slab of 0.1 mm along each seam (a split by the bare face left the stepped skin in one piece).")
    w("- Print boxes: the piece's tessellation turned on the bed in steps of 0.5 degrees.")
    keys = {k: json.load(open(os.path.join(OUT, f"measurements-{k}.json")))["skin_key"] for k in (*sp.ALL, "bezel")}
    w(f"- Skin versions: the chosen layout was cut on skin {keys[sp.CHOSEN]} (the bezel opening with no side ledge); "
      f"A, B and C on skin {keys['A']} (with the 6 mm side ledge), which differs only behind the sides of the bezel "
      "plate. `tests/test_split.py` cuts all four layouts on the current skin on every run and checks that every piece fits.")
    w("- \"Hardware within 18 mm\" and the frame check of C use the boxes of `fit/sections.json`; the monitor's path and "
      "the move of the compute module use the solids of `fit.py`.")
    w("- Hand estimates use plate and beam formulas with E = 2 GPa for printed PETG (ESTIMATED); they are first "
      "numbers, not a strength analysis.")
    w("- Not modelled: the joints, ribs, carriers, cradle and frame brackets; the warp of long pieces on the bed; slicer "
      "times; the fillet of the rear corners of the detail pass.")
    w("")
    return "\n".join(L)
