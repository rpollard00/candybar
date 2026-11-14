# The coupons: test prints before the cabinet

Date: 2026-11-14. Status: designed and built as models. No coupon is printed yet.

The coupons are small test prints. They prove the things that the design rests on, before the owner prints 12 kg of pieces. This sheet tells you what to print, in which order, what to measure, the value that passes, and what changes in the design if a coupon fails.

`cad/candybar/shell/coupons.py` makes the parts and the numbers in this sheet. `cad/candybar/shell/coupon.py` makes the pairs of joint 1 and the plaques. Build the set with these commands:

```sh
CANDYBAR_OUT=cad/out/coupons cad/candybar/freecad-run.sh candybar.shell.coupons            # parts, checks, plates
CANDYBAR_OUT=cad/out/coupons cad/candybar/freecad-run.sh --gui candybar.shell.coupons_doc  # shell.FCStd
cad/.venv-tools/bin/python cad/tools/draw_coupon.py cad/out/coupons --set                  # coupons.png, plates.png
```

| File in `cad/out/coupons/` | Content |
| --- | --- |
| `stl/`, `brep/` | One STL and one BREP for each part, in its print orientation. Do not turn a part in the slicer. |
| `shell.FCStd` | All parts in their places on the eight plates, with one group for each plate |
| `coupons.png` | Each part with all its edges, its name, its size, its plate, its mass and its time |
| `plates.png` | The eight plates from above |
| `coupons.json` | The checks of the model, with numbers |

Three coupons are cut from the real skin of the body: `facet45`, `cut-in` and `hand-hold`. They need the skin in `cad/out/shell-rev7/split/cache` (made by `candybar.shell.split`).

## The rule for the estimates

The mass is the printed volume times 1.27 g/cm3. The printed volume is the full volume for the parts of the skin. For the floor parts it is 54 % (two skins of 1.2 mm and a gyroid core of 40 %). For the two edge bars it is 55 % (four wall loops and 15 % infill). The time is the printed volume divided by 21.6 cm3/h (6 mm3/s on average), plus 6 minutes for each plate. These are estimates. The slicer gives the true values.

## The plates and the order

Print the plates in this order. Plate 1 gives the shrink value for the slicer, so that every later coupon has the correct size. Plate 3 chooses the groove clearance for plate 7.

| Plate | Content | Parts | PETG (g) | Time (h) | Print it |
| --- | --- | --- | --- | --- | --- |
| 1 | Shrink and warp | 3 | 125 | 4.7 | First |
| 2 | Holes, inserts and the cone | 7 | 133 | 4.9 | After the shrink value is in the slicer |
| 3 | Joint 1: the fit | 6 | 392 | 14.4 | After plate 1 |
| 4 | Joints 2, 3 and 5 | 6 | 148 | 5.5 | After plates 2 and 3 (they give the insert hole and the key clearance) |
| 5 | The form: facet, edges, cut-in, hand-hold | 5 | 108 | 4.0 | At any time after plate 1 |
| 6 | The floor tile | 1 | 154 | 5.7 | At any time after plate 1 |
| 7 | The finish: four pairs | 8 | 523 | 19.1 | After plate 3 chooses the clearance |
| 8 | The finish: four plaques | 4 | 164 | 6.1 | With plate 7 |
| | All | 40 | 1747 | 64.5 | |

Each plate fits the usable bed of 240 x 240 mm (`cad/params/printer.csv`), with 5 mm between the parts.

## Slicer settings

Use the profile of the real shell pieces. These settings are the same on the coupons and on the cabinet:

- Dry the filament before you print.
- Fill the 4 mm skin with wall loops, so that the skin has no infill.
- Use one layer height for the coupons and the cabinet.
- Put the seam of the layers on the inside.
- Use no hole compensation. The coupons measure the holes as printed.
- Use no support, with one exception: `joint3-wall` (see plate 4).
- Floor parts (`joint2-*`, `joint3-floor`, `floor-tile`): two skins of 1.2 mm and a gyroid core of 40 %.

## The marks

Sunk dots identify the variants. One dot is the first value in the list, two dots the second, three dots the third.

| Part | The dots give |
| --- | --- |
| `shrink-x`, `shrink-y` | One dot on the end stop: the bar along X. Two dots: the bar along Y. |
| `insert` | The hole below the dots, and the level hole at the same place: 5.6, 5.7, 5.8 |
| `holes-buttons` | One dot: the hole that is 0.3 larger (30.3 and 24.3) |
| `holes-power` | 16.0, 16.2, 16.4 |
| `cone-gauge` | The socket beside the dots: clearance 0.05, 0.15, 0.25 |
| `joint1-*`, `finish-*` | The groove clearance in tenths: +0.1, +0.2, +0.3. The bar under a pilot hole marks the smaller hole (2.25). |
| `joint2-upper`, `joint3-wall` | One dot: the side with the smaller pilot hole (2.6). The other pilot hole is 2.8. |
| `plaque-P1` to `plaque-P4` | The number of the primer test |

## Plate 1: shrink and warp

| Part | Count | Print box (mm) | Orientation | PETG (g) | Time (h) |
| --- | --- | --- | --- | --- | --- |
| `shrink-x` | 1 | 220 x 12 x 8 | Flat, along X of the bed | 11 | 0.4 |
| `shrink-y` | 1 | 12 x 220 x 8 | Flat, along Y of the bed | 11 | 0.4 |
| `warp-wall` | 1 | 180 x 16 x 100 | Upright on its foot flange, as the wall pieces print | 102 | 3.7 |

**Shrink.** Each bar has three stops. The outer faces of the stops are 110.00 and 220.00 mm from the first face. The stops stand above the base, so the first layer does not change the measurement. One study measured printed PETG 0.54 % to 0.76 % short. Thus the bar can be 218.3 to 218.8 mm.

1. Let the bars cool to room temperature.
2. Measure 110 and 220 on each bar with a caliper, over the outer faces of the stops.
3. Calculate the shrink in percent for X and for Y.
4. Set the shrink compensation of the filament in the slicer to the measured value.
5. Print the two bars again and measure them again.

- Pass: after the compensation, each length is in the range 219.8 to 220.2 mm (0.1 %). X and Y differ by less than 0.2 percentage points.
- If it fails: do not change the model. If X and Y differ by more, set different values for X and Y in the slicer. If the slicer cannot do that, the closing gap of 0.5 mm (`OtherJoints.closing_gap`) becomes too small for the pieces that are 229 mm long. Then increase that gap.

**Warp.** The wall is the skin (4 mm) on the foot flange of a lower piece, 180 long and 100 high.

1. Let the wall cool on the bed. Then remove it.
2. Put the wall on a flat surface. Measure the gap below each end of the foot with a feeler gauge.
3. Hold a straight edge along the top edge. Measure the bow.
4. Measure the height.

- Pass: gap at each end less than 0.3 mm. Bow of the top edge less than 0.5 mm. Height in the range 99.8 to 100.2 mm.
- If it fails: add brim ears at the ends, decrease the part fan, and print the wall again. If the wall still lifts, the largest pieces (229 x 228) need ribs on their flat walls or a smaller size, and the split changes. This result also counts in the choice between PETG and ABS.

## Plate 2: holes, inserts and the cone

| Part | Count | Print box (mm) | Orientation | PETG (g) | Time (h) |
| --- | --- | --- | --- | --- | --- |
| `insert` | 1 | 50 x 18 x 46.5 | Upright: the ring on its 45 degree gusset | 37 | 1.3 |
| `holes-buttons` | 1 | 145 x 42 x 5 | Flat, the panel top on the bed | 24 | 0.9 |
| `holes-lever` | 1 | 63 x 105 x 9.2 | Flat, the panel top on the bed | 40 | 1.5 |
| `holes-power` | 1 | 84 x 16 x 32 | Upright on its foot flange | 16 | 0.6 |
| `holes-usb` | 1 | 86 x 25 x 5 | Flat, the outer face on the bed | 10 | 0.3 |
| `cone-gauge` | 1 | 52 x 14 x 6 | Flat, the sockets open to the top | 5 | 0.2 |
| `cone-plug` | 1 | 14 x 14 x 9 | Flat, the cone on top | 2 | 0.1 |

**`insert`: the M4 heat-set insert.** The coupon is a wall of the skin with two flanges. The top ring (14 wide, on a 45 degree gusset) has three holes with an upright axis, as the ring below the hood. The thick foot has three holes with a level axis, as the frame of the rear door. The holes are 5.6, 5.7 and 5.8 mm, 9.5 deep, in 13 mm of material. The insert is 8.1 long. A printed hole is about 0.25 mm smaller than its model.

1. Measure each hole with the shank of a drill. Write down the largest shank that goes in.
2. Put an insert into each of the six holes with a soldering iron.
3. Put an M4 screw with a washer into each insert and tighten it by hand.

- Pass: the insert is flush with the face or 0.1 mm below it, and square. No bulge shows on the wall face behind the hole. The insert does not turn and does not come out when you tighten the screw.
- Choose the smallest hole that passes, for the upright axis and for the level axis.
- If it fails or the choice is not 5.6: change `OtherJoints.insert_hole_d`. If the depth of 9.5 and the 13 mm of material pass, change `insert_l` to the hole depth of 9.5 and `service_boss` to 13 in `joints.py`. The lever's mount uses the same insert (`stick_insert_d` in `cad/params/controls.csv`).

**`holes-buttons`: the button holes.** A plate of the panel thickness (5 mm) with holes of 30.0, 30.3, 24.0 and 24.3 mm.

- Pass: the Sanwa button goes in by hand. The play is less than 0.3 mm. The nut tightens and the rim covers the hole.
- If it fails: change `btn_hole_d` and `svc_hole_d` in `cad/params/controls.csv` to the hole that passes.

**`holes-lever`: the mount of the lever.** A plate of the panel thickness with the shaft hole (24 mm) and four bosses (10 mm wide, 4.25 high) at 40 x 85 mm. Each boss has an insert hole of 5.6 mm, 6.5 deep.

- Pass: the four screws of the lever plate go into the four inserts with no force. The shaft and its dust washer turn free in the 24 mm hole. No boss cracks when you put the insert in.
- If it fails: the wall round the insert is 2.2 mm, which is thin. Increase `stick_boss_d` to 13 and `stick_insert_depth` to the depth that the `insert` coupon proves.

**`holes-power`: the 16 mm power button.** A wall of the skin, upright, with holes of 16.0, 16.2 and 16.4 mm. The axis is level, so the top of each hole is an overhang. That is the test.

- Pass: the thread of the button goes through with no force and the nut seats flat. The top of the hole does not sag into the thread.
- Choose the smallest hole that passes. The place of the button is not decided yet (`docs/roadmap.md`, "The everyday power button").

**`holes-usb`: the USB sockets.** A plate 5 mm thick with one USB-A and one USB-C cut-out (15.1 x 7.7 and 10.9 x 5.0 mm) in a web of 2.0 mm, the two pockets behind the web, and the flange holes of 3.4 mm.

- Pass: each socket goes through its cut-out and its flange sits in the pocket. The two screws go in. A plug mates fully through the 2.0 mm web.
- If it fails: change the values in `docs/research/pc-panel-and-front-usb.md`, section A5, and the socket plate that is made from them.

**`cone-gauge` and `cone-plug`: the cone that locates a seam.** The plug has one cone (8 wide, 3 high). The gauge has three sockets with a clearance of 0.05, 0.15 and 0.25 mm.

- Put the cone into each socket.
- Pass: the cone seats fully by hand, and you feel no play.
- Choose the smallest clearance that passes. If it is not 0.15, change `OtherJoints.cone_clearance`.

## Plate 3: joint 1, the fit

| Part | Count | Print box (mm) | Orientation | PETG (g) | Time (h) |
| --- | --- | --- | --- | --- | --- |
| `joint1-lower-c01` | 1 | 129 x 22.6 x 61.5 | Upright, the seam at the top | 71 | 2.6 |
| `joint1-upper-c01` | 1 | 129 x 22.6 x 60 | Upright, the seam on the bed | 60 | 2.2 |
| `joint1-lower-c02` | 1 | 129 x 22.6 x 61.5 | Upright, the seam at the top | 71 | 2.6 |
| `joint1-upper-c02` | 1 | 129 x 22.6 x 60 | Upright, the seam on the bed | 60 | 2.2 |
| `joint1-lower-c03` | 1 | 129 x 22.6 x 61.5 | Upright, the seam at the top | 71 | 2.6 |
| `joint1-upper-c03` | 1 | 129 x 22.6 x 60 | Upright, the seam on the bed | 60 | 2.2 |

These are the three pairs of the joint coupon, with a groove clearance of +0.1, +0.2 and +0.3 mm. The procedure for the fit test and for the repeated-drive test is in `cad/out/coupon/README.md` (made by `candybar.shell.coupon`). The parts here are the same solids with the names of this set.

- Pass, fit: the halves go together by hand with no force, and you feel no play. The step between the two outer faces at the V-groove is less than 0.1 mm.
- Pass, screws: a pilot hole holds three drives of the same screw.
- Result: the groove clearance (`Joint.groove_clearance`) and the pilot hole (`Joint.pilot_d`: 2.25 or 2.4).
- If no pair passes: change the clearances in `coupon.CLEARANCES`, build again and print again.

## Plate 4: joints 2, 3 and 5

| Part | Count | Print box (mm) | Orientation | PETG (g) | Time (h) |
| --- | --- | --- | --- | --- | --- |
| `joint2-lower` | 1 | 100 x 44.8 x 10 | Flat, the table face on the bed | 24 | 0.9 |
| `joint2-upper` | 1 | 100 x 44.8 x 10 | Flat, the top face on the bed (turned over) | 24 | 0.9 |
| `joint3-floor` | 1 | 100 x 37 x 10 | Flat, the table face on the bed | 25 | 0.9 |
| `joint3-wall` | 1 | 100 x 16 x 40 | Upright. The foot flange is 10 mm above the bed: it needs support. | 29 | 1.1 |
| `joint5-frame` | 1 | 110 x 13 x 20 | Upright: the seat face is upright, the holes are level | 36 | 1.3 |
| `joint5-cover` | 1 | 110 x 20 x 4 | Flat, the outer face on the bed | 11 | 0.4 |

**Joint 2: floor tile to floor tile.** Two pieces of the 10 mm floor with a half-lap 20 mm wide. The lower lap has two cones. The upper lap has their sockets (clearance 0.15) and two pilot holes (2.6 and 2.8 mm). The lower lap has two clearance holes (3.95 mm) with a countersink for the head. The upper piece prints turned over, so that its lap is on the bed.

- Hardware: two countersunk thread-forming screws 3.5 mm, not longer than 9.5 mm. The 3.5 x 12 screw of the concept is 2 mm longer than the floor is thick.
- Pass: the cones seat and the laps meet. The step between the two top faces is less than 0.1 mm. The heads are flush with the table face or below it. Each pilot hole holds two drives.
- If it fails: change the lap, the cone or the screw in `OtherJoints` (`lap_w`, `cone_clearance`, `lap_screw_l`).

**Joint 3: wall foot on the floor.** The wall piece is the lower edge of a wall: the skin down to the table, the foot flange (12 x 4) on the floor, the key (3 x 2.5) below the flange, and a block above each screw. The floor piece has the slot (clearance 0.2) and two clearance holes with countersinks.

In the upright print of a lower piece, the foot flange and its key are a level overhang, 12 mm wide and 10 mm above the bed. This is a finding of the modelling. The coupon shows it.

- Print `joint3-wall` with support below the foot flange only.
- Hardware: two countersunk thread-forming screws 3.5 x 16.
- Pass: the flange lies flat on the floor (gap less than 0.1 mm). The key goes into the slot with no force. The wall is square to the floor within 0.5 mm over its 40 mm. Each pilot hole holds two drives.
- Examine the face of the flange where the support was. If it is not flat after you clean it, joint 3 must change: for example the key on the floor and the slot in the flange, or a foot flange that the bed carries.
- The 3.5 x 16 screw goes 2 mm through the 4 mm flange. The coupon has a block 6 mm high above each screw. The real pieces need the same block, or a screw of 12 mm.

**Joint 5: the service seam.** The frame is the fixed part: a flange 13 mm thick with two insert holes (5.6 mm, 9.5 deep, 80 apart) and two pin holes (4.0 mm, 5.5 deep). The cover is a strip of the rear door (4 mm): two clearance holes of 4.4 mm, one round pin hole and one long pin hole of 4.2 mm, 3 deep. Both parts have the 0.5 mm chamfer on the edges of the seam.

- Hardware: two M4 inserts, two M4 screws, two steel pins 4 x 8.
- Pass: the cover goes on the pins with no force, and the play is less than 0.2 mm. The screws go in. The gap round the cover is even. The cover comes off and goes on 10 times with no change.
- If it fails: change `pin_clearance` or the insert values in `OtherJoints`.
- If the `insert` coupon chose a hole that is not 5.6, change `insert_hole_d` first and build this pair again.

## Plate 5: the form

| Part | Count | Print box (mm) | Orientation | PETG (g) | Time (h) |
| --- | --- | --- | --- | --- | --- |
| `facet45` | 1 | 60 x 56 x 64 | Upright, as the upper rear piece prints: on the door's top edge | 28 | 1.0 |
| `cut-in` | 1 | 35.4 x 44 x 30 | Upright, as the middle piece prints: on its lower cut | 13 | 0.5 |
| `hand-hold` | 1 | 50 x 30.1 x 51.9 | Upright, as the upper rear piece prints: on its lower cut | 20 | 0.7 |
| `edges-level` | 1 | 60 x 30 x 24 | Lying: the edges are level, as on the rear shelf | 24 | 0.9 |
| `edges-upright` | 1 | 24 x 30 x 60 | On its end: the edges are upright, as on the band's stub | 24 | 0.9 |

`facet45`, `cut-in` and `hand-hold` are cut from the real skin. Their inner faces are the stepped faces of the cavity, as on the real pieces.

**`facet45`: the 45 degree facet.** 490 cm2 of face that shows prints at exactly 45 degrees with no support (the rear shelf, the band, the roofs of the hand-holds). The coupon is 60 mm of the upper rear piece (x 5 to 65): the frame above the door, the crease of the rear shelf, the rear facet, its round of 3 mm and the foot of the upper rear wall. A foot flange inside stands for the flange of the door frame.

- Print it with no support.
- Pass: the facet has no loops that hang and no curl at the crease. A straight edge on the facet shows a gap of less than 0.3 mm. A fingernail does not catch on the layers. The round is clean.
- Then prime and paint it with the system of plate 8. Pass: the facet reads as one flat face at 1 m.
- If it fails: the rear shelf and the band cannot print at 45 degrees with no support. The options are a steeper facet (a change of the form, decision record 0007), a tilted print of the upper rear pieces, or support and more work on 490 cm2.

**`cut-in`: a cut-in.** The right lower rear corner of the body (the ellipse column) with the second cut-in, whole: 1.5 mm deep, 10 high, with its round ends.

- Pass: the groove is clean, its lips are level and its ends are round. Its depth is in the range 1.3 to 1.7 mm. After primer and paint, the lips show no thin paint.
- If it fails: make the cut-in shallower, or increase the edge break on its lips (`dims.Blueprint`: `cut_in_depth`, `edge_break`).

**`hand-hold`: the rim and the roof of a hand-hold.** The outer end of the right hand-hold: the rim, the roof that falls 45 degrees, the wall above the rim (9.8 mm high) and the body top.

- Pass: the roof prints clean with no support. The rim is straight. The wall above the rim is not bent. After primer and paint, the rim shows no thin paint.
- The coupon does not prove the strength of the hand-hold. It is 50 mm wide.
- If it fails: the roof needs a steeper angle, or the upper rear piece needs support in the recess.

**`edges-level` and `edges-upright`: the edge finish and paint.** One bar, printed two times: lying (the edges are level and the layers make the round) and on its end (the edges are upright). The section has six edges:

| Edge | What it is |
| --- | --- |
| Top, 90 degrees, sharp | The control. Paint goes thin here. |
| Top, 90 degrees, break of 1 mm | The edge break of decision record 0007 |
| Side, 45 degree lip, break of 1 mm | As the edge of the band and the base facet |
| Side, round of 3 mm on a 45 degree turn, above a facet that faces down | As the top edge of the rear shelf |
| Inside crease, open to the top | A crease that the spray reaches |
| Inside crease below the 45 degree facet | As the crease of the rear shelf |

1. Prime and paint the two bars with the system of plate 8.
2. Examine each edge in raking light and with a magnifier.
3. Rub each edge 20 times with a cloth.

- Pass: the colour covers the break of 1 mm and the round of 3 mm fully, on the two bars. No primer shows after the rub. The creases have no dry spray and no run.
- The sharp edge is the control. If it shows no thin paint, the edge break can stay as it is.
- If the break of 1 mm shows thin paint: increase `edge_break` in `dims.Blueprint` (decision record 0007), or add a coat.

## Plate 6: the floor tile

| Part | Count | Print box (mm) | Orientation | PETG (g) | Time (h) |
| --- | --- | --- | --- | --- | --- |
| `floor-tile` | 1 | 137 x 162.9 x 10 | Flat, the table face on the bed | 154 | 5.6 |

A plate of the size of the smallest floor tile of the split (floor middle side R), as the sandwich of 10 mm. The tiles of the split do not have the laps of joint 2 yet, so this plate has none. It is a test of the sandwich and it is not a part of the cabinet.

1. Put the tile on a flat surface. Measure the gap below each corner.
2. Weigh the tile.
3. Put the tile on two supports 150 mm apart. Put 3.3 kg (the mass of the power supply) on its middle. Measure the sag.

- Pass: gap at each corner less than 0.5 mm. Mass in the range 140 to 170 g. Sag less than 0.5 mm, and the tile comes back flat. The hand estimate of the sag is 0.18 mm (`structure.floor_stiffness`, with this span and width).
- If it fails: increase the skins to 1.6 mm or the core to 60 % (`structure.FLOOR_SKIN`, `FLOOR_INFILL`). The mass of the floor (1.79 kg) changes with them.

## Plates 7 and 8: the finish

| Part | Count | Print box (mm) | Orientation | PETG (g) | Time (h) |
| --- | --- | --- | --- | --- | --- |
| `finish-lower-c02` | 4 | 129 x 22.6 x 61.5 | Upright, the seam at the top | 282 | 10.3 |
| `finish-upper-c02` | 4 | 129 x 22.6 x 60 | Upright, the seam on the bed | 240 | 8.8 |
| `plaque-P1` | 1 | 120 x 11.5 x 60 | Upright on its long edge | 41 | 1.5 |
| `plaque-P2` | 1 | 120 x 11.5 x 60 | Upright on its long edge | 41 | 1.5 |
| `plaque-P3` | 1 | 120 x 11.5 x 60 | Upright on its long edge | 41 | 1.5 |
| `plaque-P4` | 1 | 120 x 11.5 x 60 | Upright on its long edge | 41 | 1.5 |

This is the finish coupon of the owner's brief: a curved, two-piece coupon with the real joint, filament and print orientation. A pair is 130 mm along the arc (radius 300) and 120 mm across the seam. Four pairs are the coupons A, B, C and D of `docs/research/petg-finishing.md`, section 4.2. The four plaques are the primer tests P1 to P4.

- The files have the clearance of +0.2. If plate 3 chooses +0.1 or +0.3, print `joint1-lower-c01` and `joint1-upper-c01` (or `-c03`) four times.
- Do the tests 1 to 6 of `docs/research/petg-finishing.md`, section 4.4, with the schedule of section 4.3. The pass rules and the decision rules are there.
- The most important pass rule: no seam or groove outline shows at 1 m, 1 and 2 weeks after the colour and after the warm soak.
- If it fails: change the adhesive, the filler or the primer by the decision rules of section 4.4. If no system hides the seam, the seams on open faces (`bond-fill` in the split report) must move into design lines.

## What the modelling found

These items are for the owner of `joints.py`. The coupons use the values in the right column.

| Item | Concept value | In the coupons |
| --- | --- | --- |
| Insert hole depth | 8 (`insert_l`) | 9.5 |
| Material round and behind an insert | 12 (`service_boss`) | 13 |
| Screw of joint 2 | 3.5 x 12 from below. The floor is 10 thick, so the screw comes out 2 mm. | A pilot hole through the upper lap, for a screw of 9.5 or less |
| Screw of joint 3 | 3.5 x 16 from below. The floor and the flange are 14 thick, so the screw comes out 2 mm. | A block 6 mm high above each screw |
| Foot flange of joint 3 | On the floor, with the key below it | The same. It is a level overhang in the upright print and needs support. |
| Pilot and clearance holes for the 3.5 screw | None | 2.6 and 2.8 (0.75 d and 0.8 d, as joint 1), clearance 3.95, countersink 7.0 |
| Pins of joint 5 | Diameter 4, clearance 0.1. No length and no depth. | Steel pins 4 x 8: 5.5 deep in the frame, 3 deep in the 4 mm cover |
| Boss of the lever's mount | 10 wide for a 5.6 hole: a wall of 2.2 (`controls.csv`) | The same, so that the coupon tests it |

## What the model proves and what it does not

The build checks each part: it is one valid solid, it fits the bed in its print orientation, and each face that points down more than 45 degrees has a stated reason. The build checks each pair: the two parts have no common volume, the key and the cone have the clearance of the joint, and the holes are on one axis. `cad/tests/test_coupons.py` holds these checks.

The model does not prove the print, the fit, the hold of a screw or an insert, the bond or the finish. Only the prints show these.
