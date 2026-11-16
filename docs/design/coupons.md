# The coupons: test prints before the cabinet

Date: 2026-11-14. Status: designed and built as models. No coupon is printed yet.

The owner chose ABS on an enclosed printer, a Qidi Q2, on 2026-11-14. This sheet is for ABS. Where a value comes from the PETG study and no ABS value exists, the sheet says so, and the coupon gives the value.

The coupons are small test prints. They prove the things that the design rests on, before the owner prints the pieces of the cabinet. This sheet tells you what to print, in which order, what to measure, the value that passes, and what changes in the design if a coupon fails.

`cad/candybar/shell/coupons.py` makes the parts and the numbers in this sheet. `cad/candybar/shell/coupon.py` makes the pairs of joint 1 and the plaques. Build the set with these commands:

```sh
CANDYBAR_OUT=cad/out/coupons cad/candybar/freecad-run.sh candybar.shell.coupons            # parts, checks, plates
CANDYBAR_OUT=cad/out/coupons cad/candybar/freecad-run.sh --gui candybar.shell.coupons_doc  # shell.FCStd
cad/.venv-tools/bin/python cad/tools/draw_coupon.py cad/out/coupons --set                  # coupons.png, plates.png
```

| File in `cad/out/coupons/` | Content |
| --- | --- |
| `stl/`, `brep/` | One STL and one BREP for each part, in its print orientation. Do not turn a part in the slicer. |
| `shell.FCStd` | All parts in their places on the nine plates, with one group for each plate |
| `coupons.png` | Each part with all its edges, its name, its size, its plate, its mass and its time |
| `plates.png` | The nine plates from above |
| `coupons.json` | The checks of the model, with numbers |

Three coupons are cut from the real skin of the body: `facet45`, `cut-in` and `hand-hold`. They need the skin in `cad/out/shell-rev7/split/cache` (made by `candybar.shell.split`).

## The printer and the plates

The print size of the Qidi Q2 is 270 x 270 x 256 mm (width, depth, height), from the maker's specification. The limit of a piece of the cabinet is 250 x 250 mm on the bed and 250 mm high. The footprint in the model is 248 x 248 mm, because the slicer makes a piece larger to compensate the shrink. The margins are estimates.

The plates use 248 x 248 mm. This leaves 11 mm at each side of the bed, for brim ears and the purge line. The parts have 5 mm between them. The height limit is 250 mm. The highest part is 100 mm.

## The rule for the estimates

The mass is the printed volume times 1.05 g/cm3 (ABS). The printed volume is the full volume for the parts of the skin. For the floor parts it is 54 % (two skins of 1.2 mm and a gyroid core of 40 %). For the two edge bars it is 55 % (four wall loops and 15 % infill). The time is the printed volume divided by 21.6 cm3/h (6 mm3/s on average), plus 6 minutes for each plate. These are estimates. The slicer gives the true values.

## The plates and the order

Print the plates in this order. Plate 1 gives the shrink value for the slicer, so that every later coupon has the correct size. Plate 2 shows if large ABS parts stay flat on this printer. Plate 4 chooses the groove clearance for plates 5 and 8.

| Plate | Content | Prints | ABS (g) | Time (h) | Print it |
| --- | --- | --- | --- | --- | --- |
| 1 | Shrink | 2 | 20 | 1.0 | First |
| 2 | Warp: two walls and the flat strip | 3 | 226 | 10.1 | After the shrink value is in the slicer |
| 3 | Holes, inserts and the cone | 7 | 110 | 4.9 | After plate 1 |
| 4 | Joint 1: the fit | 6 | 324 | 14.4 | After plate 1 |
| 5 | The weld pairs and joints 2, 3 and 5 | 12 | 193 | 8.6 | After plates 3 and 4 (they give the insert hole and the key clearance) |
| 6 | The form: facet, edges, cut-in, hand-hold | 7 | 129 | 5.8 | After plate 2 |
| 7 | The floor tile | 1 | 128 | 5.7 | After plate 2 |
| 8 | The finish: four pairs | 8 | 432 | 19.1 | After plate 4 chooses the clearance and plate 5 chooses the weld |
| 9 | The finish: four plaques | 4 | 136 | 6.1 | With plate 8 |
| | All | 50 | 1697 | 75.7 | |

The ABS note says to print few parts on one plate, because a short layer time decreases the layer bond. If a plate with many parts shows weak layers, divide it.

## Printer and slicer settings for ABS

The settings are those of the real shell pieces. Write down the values that you use, because the cabinet must use the same values.

- Dry the filament before you print.
- Heat the chamber. The ABS note gives 60 C for large or dense parts. Preheat the chamber before the first layer.
- Examine the chamber setting in the filament profile before each print. The "Generic ABS" profile for the Q2 has the chamber heater off.
- The part fan: the ABS profiles for the Q2 put 80 % fan on overhangs. By the calculation of the research, this includes the 45 degree facets at layers of 0.12 or 0.16 mm. More fan gives a cleaner face and a weaker bond between layers. Plate 6 compares two fan values.
- The skin is 4 mm. Bambu warns that more than 6 wall loops and infill of more than 50 % increase warp in ABS. A skin that is all wall loops has about 10 loops. The two prints of `warp-wall` compare the two builds of the skin (plate 2).
- Put the seam of the layers on the inside.
- Use no hole compensation. The coupons measure the holes as printed.
- Use no support, with one exception: `joint3-wall` (plate 5).
- Floor parts (`flat-strip`, `joint2-*`, `joint3-floor`, `floor-tile`): two skins of 1.2 mm and a gyroid core of 40 %.
- Use the plate and the adhesion aid that the maker of the printer gives for ABS. Do not put acetone "ABS juice" on a PEI plate.

WARNING: Do not print ABS in a living area. ABS gives off styrene and many fine particles. Put the printer where it has a duct to the outdoors (`docs/research/abs-switch.md`, section 3.6).

CAUTION: Keep acetone, slurry and thinner away from heat-set inserts, screws and press fits in bare ABS. A solvent on ABS that is under stress can start cracks.

## The marks

Sunk dots identify the variants. One dot is the first value in the list, two dots the second, three dots the third.

| Part | The dots give |
| --- | --- |
| `shrink-x`, `shrink-y` | One dot on the end stop: the bar along X. Two dots: the bar along Y. |
| `insert` | The hole below the dots, and the level hole at the same place: 5.6, 5.7, 5.8 |
| `holes-buttons` | One dot: the hole that is 0.3 larger (30.3 and 24.3) |
| `holes-power` | 16.0, 16.2, 16.4 |
| `cone-gauge` | The socket beside the dots: clearance 0.05, 0.15, 0.25 |
| `joint1-*`, `finish-*` | The groove clearance in tenths: +0.1, +0.2, +0.3. The bar below a pilot hole marks the smaller hole (2.25). |
| `joint2-upper`, `joint3-wall` | One dot: the side with the smaller pilot hole (2.6). The other pilot hole is 2.8. |
| `plaque-P1` to `plaque-P4` | The number of the primer test |

`warp-wall` and the weld pairs have no marks. Write a letter on the inside with a pen.

## Plate 1: shrink

| Part | Count | Print box (mm) | Orientation | ABS (g) | Time (h) |
| --- | --- | --- | --- | --- | --- |
| `shrink-x` | 1 | 230 x 12 x 8 | Flat, along X of the bed | 10 | 0.4 |
| `shrink-y` | 1 | 12 x 230 x 8 | Flat, along Y of the bed | 10 | 0.4 |

Each bar has three stops. The outer faces of the stops are 115.00 and 230.00 mm from the first face. The two bars fill one plate. The stops stand above the base, so the first layer does not change the measurement.

One study measured printed ABS 0.59 % to 0.69 % short in the plane of the bed, and 0.92 % long in Z (`abs-switch.md`, section 3.3). A printer maker gives 1 % to 2 % for ABS. Thus the bar can be 228.4 to 228.6 mm, or as short as 225.4 mm. The sources do not agree, so the bars must give the value for this printer and this filament.

1. Let the bars cool to room temperature.
2. Measure 115 and 230 on each bar with a caliper, over the outer faces of the stops.
3. Calculate the shrink in percent for X and for Y.
4. Set the shrink compensation of the filament in the slicer to the measured value.
5. Print the two bars again and measure them again.

- Pass: after the compensation, each length is in the range 229.8 to 230.2 mm (0.1 %). X and Y differ by less than 0.2 percentage points.
- If it fails: do not change the model. If X and Y differ by more, set different values for X and Y in the slicer. If the slicer cannot do that, the closing gap of 0.5 mm (`OtherJoints.closing_gap`) becomes too small for the pieces that are 229 mm long. Then increase that gap.
- Shrink in Z: plate 2 measures it on the wall.

## Plate 2: warp

| Part | Count | Print box (mm) | Orientation | ABS (g) | Time (h) |
| --- | --- | --- | --- | --- | --- |
| `warp-wall` | 2 | 180 x 16 x 100 | Upright on its foot flange, as the wall pieces print | 169 | 7.5 |
| `flat-strip` | 1 | 248 x 40 x 10 | Flat, the table face on the bed | 57 | 2.5 |

Warp is the largest risk of ABS for this cabinet. The ABS note found no published limit for the size of a part. Large flat dense parts warp even in a chamber of 65 C. These coupons give the limit for this printer. The pass values are the values that the joints need. They are not from a source.

**`warp-wall`: a tall wall.** The wall is the skin (4 mm) on the foot flange of a lower piece, 180 long and 100 high. Print it two times:

- Wall A: the skin is all wall loops (about 10 loops).
- Wall B: four wall loops at each face and gyroid infill between them.

1. Let each wall cool in the closed chamber. Then remove it.
2. Put the wall on a flat surface. Measure the gap below each end of the foot with a feeler gauge.
3. Hold a straight edge along the top edge. Measure the bow.
4. Measure the height. Calculate the change in Z in percent.
5. Examine the wall for cracks between layers.

- Pass: gap at each end less than 0.3 mm. Bow of the top edge less than 0.5 mm. No crack between layers. Height in the range 99.8 to 100.2 mm after you set the compensation for Z.
- Choose the build of the skin: wall A if it passes, because sanding cannot get to infill. Wall B if only wall B passes.
- If the two walls fail: increase the chamber temperature, decrease the fan, add brim ears, and print again. If a wall still fails, the largest pieces (229 x 228) need ribs on their flat walls or a smaller size, and the split changes.

**`flat-strip`: a long flat piece on the bed.** A strip of the floor (the 10 mm sandwich), 248 x 40 mm, as long as the plate allows. It has sharp corners, as the floor tiles have. The corners show the lift.

1. Look at the four corners during the print. Write down the height at which a corner lifts from the bed.
2. Let the strip cool in the closed chamber. Then remove it.
3. Put the strip on a flat surface, table face down. Measure the gap below each corner with a feeler gauge.
4. Hold a straight edge along the top face. Measure the bow over the 248 mm.

- Pass: no corner lifts during the print. Gap below each corner less than 0.3 mm. Bow less than 0.5 mm over 248 mm.
- If it fails: print it again with brim ears on the four corners. If it passes with ears, all flat pieces of the cabinet get ears.
- If it fails with ears: the floor tiles (up to 212 x 188) cannot print flat in this ABS. The options from the ABS note are smaller tiles, shallow grooves in the table face that divide the long flat face, round corners, or a glass-filled ABS for the floor.

## Plate 3: holes, inserts and the cone

| Part | Count | Print box (mm) | Orientation | ABS (g) | Time (h) |
| --- | --- | --- | --- | --- | --- |
| `insert` | 1 | 50 x 18 x 46.5 | Upright: the ring on its 45 degree gusset | 30 | 1.3 |
| `holes-buttons` | 1 | 145 x 42 x 5 | Flat, the panel top on the bed | 20 | 0.9 |
| `holes-lever` | 1 | 63 x 105 x 9.2 | Flat, the panel top on the bed | 33 | 1.5 |
| `holes-power` | 1 | 84 x 16 x 32 | Upright on its foot flange | 13 | 0.6 |
| `holes-usb` | 1 | 86 x 25 x 5 | Flat, the outer face on the bed | 8 | 0.3 |
| `cone-gauge` | 1 | 52 x 14 x 6 | Flat, the sockets open to the top | 4 | 0.2 |
| `cone-plug` | 1 | 14 x 14 x 9 | Flat, the cone on top | 1 | 0.1 |

**`insert`: the M4 heat-set insert.** The coupon is a wall of the skin with two flanges. The top ring (14 wide, on a 45 degree gusset) has three holes with an upright axis, as the ring below the hood. The thick foot has three holes with a level axis, as the frame of the rear door. The holes are 5.6, 5.7 and 5.8 mm, 9.5 deep, in 13 mm of material. The insert is 8.1 long.

The research gives a printed hole about 0.25 mm smaller than its model. It does not give this value for ABS, and it gives no iron temperature for ABS. The coupon gives the two values.

1. Measure each hole with the shank of a drill. Write down the largest shank that goes in.
2. Put an insert into each of the six holes with a soldering iron. Write down the temperature.
3. Put an M4 screw with a washer into each insert and tighten it by hand.
4. After one day, examine the ABS round each insert for cracks.

- Pass: the insert is flush with the face or 0.1 mm below it, and square. No bulge shows on the wall face behind the hole. The insert does not turn and does not come out when you tighten the screw. No crack shows after one day.
- Choose the smallest hole that passes, for the upright axis and for the level axis.
- If it fails or the choice is not 5.6: change `OtherJoints.insert_hole_d`. If the depth of 9.5 and the 13 mm of material pass, change `insert_l` to the hole depth of 9.5 and `service_boss` to 13 in `joints.py`. The lever's mount uses the same insert (`stick_insert_d` in `cad/params/controls.csv`).
- Keep this coupon for the stress-crack test of plate 8.

**`holes-buttons`: the button holes.** A plate of the panel thickness (5 mm) with holes of 30.0, 30.3, 24.0 and 24.3 mm.

- Pass: the Sanwa button goes in by hand. The play is less than 0.3 mm. The nut tightens and the rim covers the hole.
- If it fails: change `btn_hole_d` and `svc_hole_d` in `cad/params/controls.csv` to the hole that passes.

**`holes-lever`: the mount of the lever.** A plate of the panel thickness with the shaft hole (24 mm) and four bosses (10 mm wide, 4.25 high) at 40 x 85 mm. Each boss has an insert hole of 5.6 mm, 6.5 deep.

- Pass: the four screws of the lever plate go into the four inserts with no force. The shaft and its dust washer turn free in the 24 mm hole. No boss cracks when you put the insert in, or one day later.
- If it fails: the wall round the insert is 2.2 mm, which is thin. Increase `stick_boss_d` to 13 and `stick_insert_depth` to the depth that the `insert` coupon proves.

**`holes-power`: the 16 mm power button.** A wall of the skin, upright, with holes of 16.0, 16.2 and 16.4 mm. The axis is level, so the top of each hole is an overhang. That is the test. In ABS the fan is low, so the top of a level hole can sag more.

- Pass: the thread of the button goes through with no force and the nut seats flat. The top of the hole does not sag into the thread.
- Choose the smallest hole that passes. The place of the button is not decided yet (`docs/roadmap.md`, "The everyday power button").

**`holes-usb`: the USB sockets.** A plate 5 mm thick with one USB-A and one USB-C cut-out (15.1 x 7.7 and 10.9 x 5.0 mm) in a web of 2.0 mm, the two pockets behind the web, and the flange holes of 3.4 mm.

- Pass: each socket goes through its cut-out and its flange sits in the pocket. The two screws go in. A plug mates fully through the 2.0 mm web.
- If it fails: change the values in `docs/research/pc-panel-and-front-usb.md`, section A5, and the socket plate that is made from them.

**`cone-gauge` and `cone-plug`: the cone that locates a seam.** The plug has one cone (8 wide, 3 high). The gauge has three sockets with a clearance of 0.05, 0.15 and 0.25 mm.

- Put the cone into each socket.
- Pass: the cone seats fully by hand, and you feel no play.
- Choose the smallest clearance that passes. If it is not 0.15, change `OtherJoints.cone_clearance`.

**`rod-block` and `rod`: the push rod of the monitor's button** (2026-11-15). The rod of 4 x 4 runs through a hole of 4.4 in the inner frame of the bezel plate (`cradle.button_option`, 0.2 on each side). The block is 16 thick, as long as the rod's run through the plate, and has three square holes: 4.3, 4.4 (the plate's) and 4.5. It prints with its face on the bed, as the plate does. The rod is 40 long with the small break of 0.3 at its tip, and stands on its tip, as the real rod.

- Push the rod through each hole by hand. It must slide with no force and not rock more than a little.
- If 4.4 is tight: set `Cradle.rod_fit` to the clearance of the hole that slides (0.25 for 4.5). If 4.4 rocks and 4.3 slides: set it to 0.15.
- Then press the real button through the plate with the rod: the travel of 2.0 must turn the monitor on and off.

## Plate 4: joint 1, the fit

| Part | Count | Print box (mm) | Orientation | ABS (g) | Time (h) |
| --- | --- | --- | --- | --- | --- |
| `joint1-lower-c01` | 1 | 129 x 22.6 x 61.5 | Upright, the seam at the top | 58 | 2.6 |
| `joint1-upper-c01` | 1 | 129 x 22.6 x 60 | Upright, the seam on the bed | 50 | 2.2 |
| `joint1-lower-c02` | 1 | 129 x 22.6 x 61.5 | Upright, the seam at the top | 58 | 2.6 |
| `joint1-upper-c02` | 1 | 129 x 22.6 x 60 | Upright, the seam on the bed | 50 | 2.2 |
| `joint1-lower-c03` | 1 | 129 x 22.6 x 61.5 | Upright, the seam at the top | 58 | 2.6 |
| `joint1-upper-c03` | 1 | 129 x 22.6 x 60 | Upright, the seam on the bed | 50 | 2.2 |

These are the three pairs of the joint coupon, with a groove clearance of +0.1, +0.2 and +0.3 mm. The procedure for the fit test and for the repeated-drive test is in `cad/out/coupon/README.md` (made by `candybar.shell.coupon`). That file was written for PETG on the Bambu A1. Where it and this sheet differ, this sheet applies.

Each lower half has two pilot holes: 2.25 mm (the table value for PET) and 2.4 mm (the table value for ABS, 0.8 of the screw diameter). For ABS, 2.4 is the first candidate. The repeated-drive test confirms it: drive the same screw into the same hole several times.

For a weld with acetone the flange faces must touch, because acetone does not fill a gap. Thus the fit of the flange faces matters more in ABS than the fit of the key.

- Pass, fit: the halves go together by hand with no force, and you feel no play. The step between the two outer faces at the V-groove is less than 0.1 mm. The two flange faces touch along the full length: a feeler gauge of 0.05 mm does not go in.
- Pass, screws: the 2.4 pilot hole holds three drives of the same screw, and the flange does not crack.
- Result: the groove clearance (`Joint.groove_clearance`) and the pilot hole (`Joint.pilot_d`).
- If no pair passes: change the clearances in `coupon.CLEARANCES`, build again and print again.

## Plate 5: the weld pairs and joints 2, 3 and 5

| Part | Count | Print box (mm) | Orientation | ABS (g) | Time (h) |
| --- | --- | --- | --- | --- | --- |
| `weld-lower` | 3 | 40 x 16 x 31.5 | Upright, the seam at the top | 39 | 1.7 |
| `weld-upper` | 3 | 40 x 16 x 30 | Upright, the seam on the bed | 31 | 1.4 |
| `joint2-lower` | 1 | 100 x 44.8 x 10 | Flat, the table face on the bed | 20 | 0.9 |
| `joint2-upper` | 1 | 100 x 44.8 x 10 | Flat, the top face on the bed (turned over) | 20 | 0.9 |
| `joint3-floor` | 1 | 100 x 37 x 10 | Flat, the table face on the bed | 21 | 0.9 |
| `joint3-wall` | 1 | 100 x 16 x 40 | Upright. The foot flange is 10 mm above the bed: it needs support. | 24 | 1.1 |
| `joint5-frame` | 1 | 110 x 13 x 20 | Upright: the seat face is upright, the holes are level | 29 | 1.3 |
| `joint5-cover` | 1 | 110 x 20 x 4 | Flat, the outer face on the bed | 9 | 0.4 |

**The weld pair: the bond of ABS.** ABS welds to itself with a solvent. The pair is the real section of joint 1 on a straight seam 40 mm long: the skin, the flange 6 x 12 with its gusset, the key and the groove (clearance +0.2), the V-groove, and one screw 3.0 x 16 in a 2.4 pilot hole. Each half is 30 mm from the seam to its free edge. Print three pairs.

| Pair | Weld |
| --- | --- |
| A | Acetone only |
| B | ABS "glue": 8 g of the same ABS in 50 ml of acetone (`abs-switch.md`, section 2.2) |
| C | ABS slurry: about 20 g of the same ABS in 50 ml of acetone |

1. Put the halves of each pair together dry, with the screw. Make sure that the flange faces touch.
2. Open the pair. Put the solvent on the two flange faces and on the key. Do not put solvent into the pilot hole.
3. Put the pair together and drive the same screw into the same hole. Write down the time that you had to work.
4. Wait 24 hours or more.
5. Remove the screw. Hold the lower half in a vice and bend the upper half inward by hand until the pair breaks.

- Pass: the pair breaks in the ABS beside the joint, or the flange tears. Fail: the two flange faces come apart clean.
- The gap that slurry fills and its work time have no published value. This test gives them.
- Choose the weld for the cabinet: the one that passes with the longest work time. The longest seam (L1) is 333 mm on each side.
- If no weld passes: use the adhesive of the PETG plan (MMA) on ABS, and test it on a new pair.
- The finish coupon (plate 8) is the test of the weld under filler and paint. This pair is only the test of strength.

**Joint 2: floor tile to floor tile.** Two pieces of the 10 mm floor with a half-lap 20 mm wide. The lower lap has two cones. The upper lap has their sockets (clearance 0.15) and two pilot holes (2.6 and 2.8 mm). The lower lap has two clearance holes (3.95 mm) with a countersink for the head. The upper piece prints turned over, so that its lap is on the bed.

- Hardware: two countersunk thread-forming screws 3.5 mm, not longer than 9.5 mm. The 3.5 x 12 screw of the concept is 2 mm longer than the floor is thick.
- Pass: the cones seat and the laps meet. The step between the two top faces is less than 0.1 mm. The heads are flush with the table face or below it. Each pilot hole holds two drives. For ABS, 2.8 is the value to expect.
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
- Pass: the cover goes on the pins with no force, and the play is less than 0.2 mm. The screws go in. The gap round the cover is even. The cover comes off and goes on 10 times with no change. No crack shows round a pin or an insert after one day.
- If it fails: change `pin_clearance` or the insert values in `OtherJoints`.
- If the `insert` coupon chose a hole that is not 5.6, change `insert_hole_d` first and build this pair again.

## Plate 6: the form

| Part | Count | Print box (mm) | Orientation | ABS (g) | Time (h) |
| --- | --- | --- | --- | --- | --- |
| `facet45` | 2 | 60 x 56 x 64 | Upright, as the upper rear piece prints: on the door's top edge | 47 | 2.1 |
| `cut-in` | 1 | 35.4 x 44 x 30 | Upright, as the middle piece prints: on its lower cut | 10 | 0.5 |
| `hand-hold` | 2 | 50 x 30.1 x 51.9 | Upright, as the upper rear piece prints: on its lower cut | 33 | 1.4 |
| `edges-level` | 1 | 60 x 30 x 24 | Lying: the edges are level, as on the rear shelf | 20 | 0.9 |
| `edges-upright` | 1 | 24 x 30 x 60 | On its end: the edges are upright, as on the band's stub | 20 | 0.9 |

`facet45`, `cut-in` and `hand-hold` are cut from the real skin. Their inner faces are the stepped faces of the cavity, as on the real pieces.

**The 45 degree faces in ABS.** A face that points down 45 degrees needs cooling to print clean. ABS needs a low fan for the bond between layers. The two needs are opposite. The ABS profiles for the Q2 put 80 % fan on overhangs, which includes these faces. `facet45`, `cut-in` and `hand-hold` are the proof.

Print `facet45` and `hand-hold` two times. Write the letter on the inside with a pen.

- Print F: the fan of the profile (80 % on overhangs).
- Print L: less fan on overhangs. Start with half of the profile's value.

Compare the two prints of each coupon:

| Compare | How | Better is |
| --- | --- | --- |
| The face that points down 45 degrees | Raking light, a straight edge, a fingernail across the layers | No loops that hang, no curl at the lower edge, a gap of less than 0.3 mm |
| The bond between layers in the 45 degree face | Examine for cracks. Then, after all other tests, break the coupon by hand across the facet or the roof. | No crack. The break goes across the layers and does not divide two layers clean. |
| `hand-hold` only: the roof under load | Hook two fingers below the roof, hold the coupon in a vice by its lower end, and pull up hard | No crack and no sound. The roof carries the lift of the cabinet. |

- Choose the highest fan value whose bond passes. If print F passes the bond tests, use the profile as it is.
- If print L has a bad face and print F has a weak bond: print the pair again with a value between the two.
- Print `cut-in` and the two edge bars one time, with the fan of the profile.

**`facet45`: the 45 degree facet.** 490 cm2 of face that shows prints at exactly 45 degrees with no support (the rear shelf, the band, the roofs of the hand-holds). The coupon is 60 mm of the upper rear piece (x 5 to 65): the frame above the door, the crease of the rear shelf, the rear facet, its round of 3 mm and the foot of the upper rear wall. A foot flange inside stands for the flange of the door frame.

- Print it with no support.
- Pass: the facet has no loops that hang and no curl at the crease. A straight edge on the facet shows a gap of less than 0.3 mm. A fingernail does not catch on the layers. The round is clean. No crack shows between layers.
- Then prime and paint it with the system of plate 9. Pass: the facet reads as one flat face at 1 m.
- If no fan value gives a clean face and a good bond: the rear shelf and the band cannot print at 45 degrees in ABS with no support. The options are a steeper facet (a change of the form, decision record 0007), a tilted print of the upper rear pieces, or support and more work on 490 cm2.

**`cut-in`: a cut-in.** The right lower rear corner of the body (the ellipse column) with the second cut-in, whole: 1.5 mm deep, 10 high, with its round ends. The upper half of the groove points down 33 degrees at its lip.

- Pass: the groove is clean, its lips are level and its ends are round. Its depth is in the range 1.3 to 1.7 mm. After primer and paint, the lips show no thin paint.
- If it fails: make the cut-in shallower, or increase the edge break on its lips (`dims.Blueprint`: `cut_in_depth`, `edge_break`).

**`hand-hold`: the rim and the roof of a hand-hold.** The outer end of the right hand-hold: the rim, the roof that falls 45 degrees, the wall above the rim (9.8 mm high) and the body top.

- Pass: the roof prints clean with no support. The rim is straight. The wall above the rim is not bent. After primer and paint, the rim shows no thin paint.
- The roof carries the lift of the cabinet, and the ABS note gives a lower impact strength across the layers for ABS than for PETG. The pull test above compares the two fan values. It does not prove the full load: the coupon is 50 mm wide.
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

1. Prime and paint the two bars with the system of plate 9.
2. Examine each edge in raking light and with a magnifier.
3. Rub each edge 20 times with a cloth.

- Pass: the colour covers the break of 1 mm and the round of 3 mm fully, on the two bars. No primer shows after the rub. The creases have no dry spray and no run.
- The sharp edge is the control. If it shows no thin paint, the edge break can stay as it is.
- If the break of 1 mm shows thin paint: increase `edge_break` in `dims.Blueprint` (decision record 0007), or add a coat.

## Plate 7: the floor tile

| Part | Count | Print box (mm) | Orientation | ABS (g) | Time (h) |
| --- | --- | --- | --- | --- | --- |
| `floor-tile` | 1 | 137 x 162.9 x 10 | Flat, the table face on the bed | 128 | 5.6 |

A plate of the size of the smallest floor tile of the split (floor middle side R), as the sandwich of 10 mm. The tiles of the split do not have the laps of joint 2 yet, so this plate has none. It is a test of the sandwich and it is not a part of the cabinet. Print it after `flat-strip` passes, with the same aids (brim ears, if the strip needed them).

1. Put the tile on a flat surface. Measure the gap below each corner.
2. Weigh the tile.
3. Put the tile on two supports 150 mm apart. Put 3.3 kg (the mass of the power supply) on its middle. Measure the sag.

- Pass: gap at each corner less than 0.5 mm. Mass in the range 115 to 140 g. Sag less than 0.5 mm, and the tile comes back flat.
- The hand estimate of the sag is 0.18 mm (`structure.floor_stiffness`, with this span and width). The estimate uses the stiffness of PETG. The structure study has no ABS value.
- If it fails: increase the skins to 1.6 mm (`structure.FLOOR_SKIN`). Do not increase the core to more than 50 %, because dense infill increases warp in ABS. The mass of the floor changes with the skins.

## Plates 8 and 9: the finish

| Part | Count | Print box (mm) | Orientation | ABS (g) | Time (h) |
| --- | --- | --- | --- | --- | --- |
| `finish-lower-c02` | 4 | 129 x 22.6 x 61.5 | Upright, the seam at the top | 233 | 10.3 |
| `finish-upper-c02` | 4 | 129 x 22.6 x 60 | Upright, the seam on the bed | 199 | 8.8 |
| `plaque-P1` | 1 | 120 x 11.5 x 60 | Upright on its long edge | 34 | 1.5 |
| `plaque-P2` | 1 | 120 x 11.5 x 60 | Upright on its long edge | 34 | 1.5 |
| `plaque-P3` | 1 | 120 x 11.5 x 60 | Upright on its long edge | 34 | 1.5 |
| `plaque-P4` | 1 | 120 x 11.5 x 60 | Upright on its long edge | 34 | 1.5 |

This is the finish coupon of the owner's brief: a curved, two-piece coupon with the real joint, filament and print orientation. A pair is 130 mm along the arc (radius 300) and 120 mm across the seam. In ABS, this coupon is also the test of the weld, of the filler in the groove and of the paint on ABS.

The files have the clearance of +0.2. If plate 4 chooses +0.1 or +0.3, print `joint1-lower-c01` and `joint1-upper-c01` (or `-c03`) four times.

The four pairs follow the ABS set of `abs-switch.md`, section 10, item 2:

| Pair | Weld of the flanges | V-groove |
| --- | --- | --- |
| A | Acetone | Slurry, in thin layers |
| B | Acetone | A polyester plastic putty that names ABS on its data sheet |
| C | The weld that plate 5 chose | Slurry, in thin layers |
| D | The weld that plate 5 chose | A polyester plastic putty that names ABS |

1. Weld the pairs with the screws as clamps.
2. Fill the V-groove. Put slurry on in thin layers, because a thick layer shrinks and cracks.
3. Wait one week or more between the last slurry and the final block sanding. Solvent leaves a seam during days, and the seam then sinks.
4. Prime in light coats with flash time between them. Then put on the colour, and clear on half of each pair.
5. Do the tests 1 to 6 of `docs/research/petg-finishing.md`, section 4.4. The pass rules there are for the film and the seam, and they apply to ABS.
6. Do the stress-crack test: put the hobby lacquer over primer near a heat-set insert on the `insert` coupon, and examine it after one day and after one week.

- The most important pass rule: no seam or groove outline shows at 1 m, 1 and 2 weeks after the colour and after the warm soak. No test of a welded ABS seam under paint during weeks is published. This coupon is the test.
- Warm soak: the PETG note uses 50 C for 24 h. Use the same value for ABS. ABS has more margin (HDT 84 C).
- Pass, stress crack: no crack round the insert.
- If it fails: change the weld, the filler or the primer. If no system hides the seam, the seams on open faces (`bond-fill` in the split report) must move into design lines.

The plaques P1 to P4 are the primer tests. The matrix of the PETG note (section 4.2) names products for PETG. No matrix for ABS is written yet. The ABS note says that 1K plastic primers and polyester putties name ABS on their data sheets. Until an ABS matrix exists, use the four first coats of the PETG matrix. The scuffed and the wiped half stay. Do not wipe bare ABS with acetone or thinner.

## What changed for ABS

| Coupon | Change |
| --- | --- |
| `flat-strip` | New: a long flat strip of the floor (248 mm), to see the corners lift |
| `weld-lower`, `weld-upper` | New: three pairs for the solvent weld |
| `warp-wall` | Print two: one for each build of the skin |
| `shrink-x`, `shrink-y` | 230 mm long (they were 220), on a plate of their own. ABS values for the length to expect. |
| `joint1-*`, `joint2-*`, `joint3-*` | Same parts. The pilot hole to expect is the ABS value (2.4, and 2.8 for the 3.5 screw). The flange faces must touch for the weld. |
| `insert`, `holes-lever`, `joint5-*` | Same parts. A check for cracks after one day is new. |
| `facet45`, `hand-hold` | Same parts. Print two of each: one with the fan of the profile, one with less. They are the proof of the 45 degree faces in ABS. |
| `cut-in` | Same part. It is a proof of the 45 degree faces too. |
| `finish-*`, `plaque-*` | Same parts. The matrix is for ABS: weld, slurry or putty, wait, primer, lacquer, stress crack. |
| `floor-tile` | Same part. The mass range is for ABS. |
| All plates | Nine plates of 248 x 248 on the bed of 270 x 270 (a margin of 11 mm), with a height limit of 250. All masses are for ABS (1.05 g/cm3). |

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

The build checks each part: it is one valid solid, it fits the plate in its print orientation, and each face that points down more than 45 degrees has a stated reason. The build checks each pair: the two parts have no common volume, the key and the cone have the clearance of the joint, and the holes are on one axis. `cad/tests/test_coupons.py` holds these checks.

The model does not prove the print, the warp, the fit, the hold of a screw or an insert, the weld or the finish. Only the prints show these.

## On the main line

Date: 2026-11-15. The set was built again on the laptop (OpenCascade 7.9.3), from the skin in the cache of the split, after the other packages were merged. The owner prints from this build.

- **Result.** 37 parts, 50 prints on nine plates, 1697 g of ABS, about 76 h (estimates). Every check of the set passes: each part is one valid solid that fits its plate in its print orientation, each downward face has a stated reason, the pairs have the clearance of the joint, the cuts from the real skin hold the features they are for.
- **The STL files.** Every STL in `stl/` is a closed mesh with no non-manifold edge and no self-intersection (checked with FreeCAD's mesh tools). 36 meshes are closed as made. The mesh of `cut-in` had 24 open edges, each 0.004 long, where two slabs of the cavity meet; the writer makes points nearer than 0.001 one point (`coupons.closed_mesh`), and the mesh is closed with the volume of the solid. A test holds this for every part.
- **The work-arounds of the server are removed.** The repair of a cut from the skin (`mended`) and the turned dots in `coupon.py` are not needed here: the cuts are valid, and the tests of the joint coupon pass without the turn.
- **One new work-around for this kernel.** A plain translation of `cut-in` and `hand-hold` to the origin of the bed is not a valid shape with OpenCascade 7.9.3, although the cut is; ShapeFix does not mend it. `to_bed` then moves them with `transformGeometry`, which gives valid shapes (the volume changes by 0.04 and 0.005 mm3).
- **The three cuts from the real skin, as seen with every edge drawn** (renders in `cad/out/_scratch/integrate/real`): `facet45` has the strip above the door, the crease, the facet of 45 degrees with its round of 3 at the top, the upper rear wall and the foot flange on the bed. `cut-in` has the groove whole round the lower rear corner, clean on the outside, with its round ends. `hand-hold` has the rim with its round, the roof of 45 degrees, the round end of the recess, the wall above the rim and the seam bevel of the body top. The outer faces of all three are clean. Their inner faces have the steps of 1 of the cavity, as the real pieces have. They are right for what they test.
- **The output for the printer** is in `cad/out/coupons/`: `stl/` and `brep/` (each part in its print orientation), `shell.FCStd` (the plates), `plates.png` (the nine plates from above), `coupons.png` (each part with every edge drawn) and `coupons.json`.

## The edge finish and the face check

Date: 2026-11-15. `tools/edge_finish.py` and `tools/face_check.py` run on `cad/out/coupons`. The manifest of the layout now gives each entry its coupon, its group and its move onto the plate (`offset`), and for a cut from the real skin the move back into the cabinet (`to_cabinet`).

- **The classes.** The coupons of plate 6 test the form, the edge finish and the paint, so they are "printed" and the edge rule holds on them (`coupons.PAINTED`: `facet45`, `cut-in`, `hand-hold`, `edges-level`, `edges-upright`). The other coupons are "a test print": a fit, a hole, a weld, the shrink, the warp, the floor tile, and the finish pairs and the plaques, whose own edges are those of a test piece. Their findings are listed and do not fail.
- **The cuts from the real skin.** A face of `facet45`, `cut-in` or `hand-hold` lies against the rest of the shell when it is inside the outer form of the default build or beyond the box that cut it (`coupons.CUT_BOXES`), moved by `to_cabinet`. A face shows only when it is on the outside of the form (`edge_finish.face_on_skin`).
- **The edge bars.** The sharp top edge of 90 degrees is the control of the paint test (`coupons.control_edge`). The two ends and the bed face of a bar are not faces that the test looks at (`coupons.untested`).
- **Result.** Both tools pass. No sharp edge of the coupons of plate 6 shows on the outside. The face check lists the slivers of 0.01 on the inner face of the wall at the top of `hand-hold` (a step of 0.01 where the round of the cavity ends below the body top): they are not on the outside. No coupon changed.
