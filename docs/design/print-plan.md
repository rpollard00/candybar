# Print plan

Date: 2026-11-14. Each source was read on this date unless the text gives a different date.

This plan is for the shell of revision 7, as `cad/out/shell-rev7/split/report.md` cuts it: 23 printed
pieces, 9 floor tiles and 2 halves of a bezel plate. The printer is the Bambu A1, and the material is
PETG. The finishing steps are those of `docs/research/petg-finishing.md`.

The pieces are not ready to print. The split is the bare 4 mm skin: the flanges, the keys, the ribs
and the carriers are not modelled (roadmap, phase 4). Each mass and each time in this plan is an
estimate by a rule of thumb. It is not a slicer result. Slice each piece before a decision that
depends on time or filament.

## Status tags

| Tag | Meaning |
| --- | --- |
| REPORT | A value of the split report or of a different build output. The file is named. |
| SOURCED [id] | Written in the source with that number in section 8. |
| ESTIMATED | Calculated here. The rule is given. |
| PROVISIONAL | A setting or an order proposed here. A test or the owner can change it. |

## 1. Summary

1. The shell, the floor, one bezel plate, the inside parts and the coupons are about 12.2 kg of PETG and
   about 410 printer hours. With 20 % more for failed prints and second prints, the plan is 15 spools
   of 1 kg and about 500 hours.
2. No piece needs support on a large seen face. Support touches 22.7 cm2 of seen face in total, most of
   it on the two hood sides.
3. Print the coupons first. The joint coupon gives the key clearance and the pilot hole in the first
   days. The pieces can then be printed and assembled dry while the paint coupons cure. Only the
   bond waits for the result of the paint coupons, which takes about three weeks.
4. The largest risks are not the print time. The first is the shrink of PETG across the large
   openings (the door and the bezel). The second is the seen facets at 45 degrees, which print with no
   support. The third is the first layer at each joint that prints on the bed. A coupon or a
   measurement answers each one before the large pieces are printed.
5. Only joint 1 has a coupon. Joints 2, 3 and 5 (the floor lap, the wall foot, the insert boss with its
   pins) need a small coupon too.

## 2. The rules of thumb

| Rule | Value | Basis |
| --- | --- | --- |
| Printed mass of a wall piece or a door half | Skin mass x 1.30 | The split report adds 25 % to the skin for ribs, flanges, splice plates, inserts and screws. 5 % more is for the brim, the start line and small supports. ESTIMATED |
| Printed mass of a trim piece (speaker form, logo form, bezel half) | Skin mass x 1.10 | These pieces have no seam flange. 10 % is for the brim and waste. ESTIMATED |
| Printed mass of a floor tile | Mass as a 4 mm skin x 1.42 x 1.05 | The report measures the tiles as a 4 mm skin (1.26 kg) and gives 1.79 kg for the sandwich of 10 mm. 5 % more is for the brim and waste. REPORT and ESTIMATED |
| Print rate of a seen piece | 27 g in 1 hour | An average flow of 6 mm3/s at a density of 1.25 g/cm3. The slicer's limit for Bambu PETG Basic on the A1 is 13 mm3/s [B1]. The average is less than half of the limit, because of outer walls, corners, small layers and travel. ESTIMATED |
| Print rate of a hidden piece (floor tile) | 40 g in 1 hour | An average flow of 9 mm3/s, with thicker layers and infill. ESTIMATED |
| Print rate of the inside parts | 35 g in 1 hour | The published profile of the Mini New Astro City model: 1950 g in 55.5 h (`docs/research/mini-new-astro-city-geometry.md` 8.2). |
| Failed prints and second prints | 20 % more filament and time | `docs/research/abs-switch.md` 8.1 gives 15 % to 25 % for PETG. |
| Inside parts that are not designed | 2.0 kg | An allowance for the monitor cradle, the BC-250 carrier, the shroud, the duct, the saddle of the supply, the panel frame, two printed panel plates, the baffles and the node plates. Nothing is modelled. ESTIMATED |
| Coupons | 1.3 kg | Seven pairs of the joint coupon and four plaques (about 1.0 kg), and the small coupons of section 4. ESTIMATED from their print boxes |

The time can be 30 % less or more. A layer of 0.12 mm in place of 0.16 mm makes a seen piece about one
third slower. ESTIMATED: the time of a wall goes with the number of layers.

## 3. The pieces

The orientation and the print box are those of the split report. The limit of the printer is
240 mm x 240 mm on the bed and 245 mm high (`cad/params/printer.csv`). "Spare to the limit" is the limit
less the box, in x, y and z. "Skin" is the solid 4 mm skin of the report. "Support on a seen face" is
the report's "seen face over 45 deg".

| # | Piece | On the bed | Print box (mm) | Spare to the limit (mm) | Skin (g) | Printed mass (g) | Time (h) | Support | Support on a seen face |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | deck nose | upright, on the bed diagonal | 218 x 218 x 72 | 22, 22, 173 | 143 | 186 | 6.9 | None. The ledge for the panel has a 45 degree gusset. | No |
| 2, 3 | deck side R, L | upright | 186 x 185 x 72 | 54, 55, 173 | 193 each | 251 each | 9.3 each | A small one, or none: 1.9 cm2 of seen face overhangs. | Yes, 1.9 cm2 each |
| 4 | apron | on its rear edge, on the bed diagonal | 210 x 210 x 114 | 30, 30, 131 | 182 | 237 | 8.8 | At the lower end of the sweep (about 3 cm2). | Yes, 2.7 cm2. The control panel hides the rear wall of the pocket. |
| 5, 6 | lower R, L | upright | 181 x 181 x 134 | 59, 59, 111 | 195 each | 254 each | 9.4 each | None | No |
| 7, 8 | middle R, L | upright, on the bed diagonal | 209 x 208 x 177 | 31, 32, 68 | 297 each | 386 each | 14.3 each | None. The cut-ins face down 33 degrees at most. | No |
| 9, 10 | upper R, L | upright | 206 x 205 x 131 | 34, 35, 114 | 231 each | 300 each | 11.1 each | None, or a small one: 0.6 cm2. The side facet of the rear shelf is 45 degrees. | Yes, 0.6 cm2 each |
| 11 | brow | upright | 170 x 170 x 38 | 70, 70, 207 | 56 | 73 | 2.7 | None | No |
| 12, 13 | upper rear R, L | upright | 180 x 180 x 143 | 60, 60, 102 | 205 each | 266 each | 9.9 each | None. 149.7 cm2 of seen face is at 45 degrees (the rear facet, the roof of the hand-hold). | No support. See risk 3. |
| 14, 15 | rear lower R, L | upright | 229 x 228 x 116 | 11, 12, 129 | 242 each | 315 each | 11.7 each | None, or a small one: 0.3 cm2. The base facet is 45 degrees. | Yes, 0.3 cm2 each |
| 16, 17 | door half R, L | outer face on the bed | 211 x 165 x 4 | 29, 75, 241 | 177 each | 230 each | 8.5 each | None. The vents are not designed. | No |
| 18 | hood centre | on a cut face | 148 x 139 x 212 | 92, 101, 33 | 428 | 556 | 20.6 | None | No |
| 19, 20 | hood side R, L | upright | 139 x 129 x 148 | 101, 111, 97 | 335 each | 436 each | 16.1 each | At the top corner near the roof, and at the end of the soffit in the marquee opening. | Yes, 7.2 cm2 each |
| 21, 22 | speaker form R, L | front face on the bed | 94 x 76 x 13 | 146, 164, 232 | 86 each | 95 each | 3.5 each | None | No |
| 23 | logo form | front face on the bed | 160 x 160 x 5 | 80, 80, 240 | 56 | 62 | 2.3 | None | No |
| - | floor front side R, L | flat | 188 x 132 x 10 | 52, 108, 235 | 121 each, as a 4 mm skin | 180 each | 4.5 each | None | Not seen |
| - | floor front centre | flat | 212 x 188 x 10 | 28, 52, 235 | 202, as a 4 mm skin | 301 | 7.5 | None | Not seen |
| - | floor middle side R, L | flat | 163 x 137 x 10 | 77, 103, 235 | 113 each, as a 4 mm skin | 168 each | 4.2 each | None | Not seen |
| - | floor middle centre | flat | 212 x 163 x 10 | 28, 77, 235 | 176, as a 4 mm skin | 262 | 6.6 | None | Not seen |
| - | floor rear side R, L | flat | 177 x 137 x 10 | 63, 103, 235 | 111 each, as a 4 mm skin | 166 each | 4.1 each | None | Not seen |
| - | floor rear centre | flat | 212 x 177 x 10 | 28, 63, 235 | 191, as a 4 mm skin | 285 | 7.1 | None | Not seen |
| - | bezel half R, L | on its cut face, the profile on the bed diagonal | 223 x 223 x 217 | 17, 17, 28 | 381 each | 419 each | 15.5 each | None | No |

Notes on the table:

- The piece with the least spare room on the bed is "rear lower" (11 mm and 12 mm). The piece with the
  least spare height is the bezel half (28 mm), then the hood centre (33 mm).
- The longest single print is the hood centre, about 21 hours. Each other piece is less than 17 hours.
- The support that touches a seen face is 22.7 cm2 in total: 14.4 cm2 on the two hood sides, 2.7 cm2 on
  the apron, 3.8 cm2 on the two deck sides, 1.2 cm2 on the two upper pieces and 0.6 cm2 on the two rear
  lower pieces. REPORT
- The seen faces at 45 degrees are 489.6 cm2. They print with no support. REPORT
- The report measures the bezel plate in the first of three ways (two halves on the centre line). The
  owner did not choose the way. The table has one plate. The owner wants four plates.
- The door has its vents and the speaker forms, the logo form and the marquee lip are stand-ins. Their
  values change when they are designed.

## 4. The totals

| Group | Printed mass | Time |
| --- | --- | --- |
| The 23 pieces of the shell | 6.18 kg | 229 h |
| The 9 floor tiles | 1.88 kg | 47 h |
| One bezel plate (2 halves) | 0.84 kg | 31 h |
| Inside parts (allowance) | 2.00 kg | 57 h |
| Coupons | 1.30 kg | 48 h |
| **Subtotal** | **12.2 kg** | **412 h** |
| Failed prints and second prints, 20 % | 2.4 kg | 82 h |
| **Plan** | **14.6 kg, 15 spools of 1 kg** | **about 500 h** |
| Three more bezel plates, later | 2.5 kg | 93 h |

All ESTIMATED by the rules of section 2. For comparison: `docs/research/abs-switch.md` 8.1 gives 10 kg to
19 kg of PETG for the same shell, by area.

At 12 hours of printing each day, 500 hours are about six weeks. At 20 hours each day they are about
four weeks. ESTIMATED

Buy the filament of one maker and one type for the coupons and for the shell. The coupons prove the
bond and the paint on that filament only (`docs/research/petg-finishing.md` 2.4: filament grades
differ).

## 5. The order of work

### 5.1 Stage 1: the printer and the filament

| Step | What it proves | What to measure |
| --- | --- | --- |
| Dry the filament | No bubbles and no strings from wet PETG | The time and the temperature of the dryer. Keep them the same for each spool. |
| A single layer of 240 mm x 240 mm | The reach of the nozzle and the first layer at the edges of the plate (`docs/research/hardware-envelopes.md` 7) | Gaps or ridges in the layer at the four corners |
| A bar of 200 mm in X and a bar of 200 mm in Y | The shrink of this PETG on this printer | The length of each bar with a caliper. See risk 2. |

### 5.2 Stage 2: the coupons and the test prints

| # | Print | What it proves | What to measure | Source |
| --- | --- | --- | --- | --- |
| C1 | Joint coupon, three pairs with groove clearances of 0.1 mm, 0.2 mm and 0.3 mm | The key clearance of joint 1. That the gusset and the groove bridge print clean with no support. | The force to put the halves together, and the play. The step at the V-groove with a feeler gauge. | `cad/out/coupon/README.md`, fit test |
| C2 | The repeated-drive test on one pair of C1 | The pilot hole: 2.25 mm or 2.4 mm | The number of the first drive at which the thread does not hold, for each hole. A crack in the flange. | The same file |
| C3 | Four pairs at the chosen clearance (A, B, C, D) and four plaques | The adhesive, the weld of the groove, the filler, the primer and the paint | The six tests of `docs/research/petg-finishing.md` 4.4: tape, flex, warm soak, fingernail, seam look, break | That note, section 4 |
| C4 | Insert coupon: bosses with holes of 5.6 mm, 5.7 mm and 5.8 mm for M4, and 4.0 mm, 4.1 mm and 4.2 mm for M3. Hole depth 9.5 mm for M4. Bosses of 12 mm and 13 mm. | The hole for a heat-set insert in this PETG | Does the insert seat flush with a small resistance? Does the boss bulge or crack? Tighten a screw until it fails, and write down what fails. | `docs/design/hardware-list.md` 2.1 |
| C5 | Hole coupon: 30.2 mm to 30.4 mm and 24.2 mm to 24.4 mm for the buttons, 16.2 mm to 16.4 mm for the power button, a pin hole of 4.1 mm, the two USB cut-outs with their web of 2.0 mm | The printed size of each hole | The fit of the real part, when it is there. If not, the hole with a caliper. | `docs/research/controls-ergonomics.md` 2.4, `docs/research/pc-panel-and-front-usb.md` A5, `docs/research/bc250-power-button.md` 9.1 |
| C6 | Facet coupon: a slice of 60 mm of the upper rear piece, with the rear facet and the roof of a hand-hold, upright as the piece prints | The surface of a seen face at 45 degrees with no support | Look at the facet under raking light. Print it at 0.12 mm and at 0.16 mm. | Risk 3 |
| C7 | Tall wall coupon: a slice of 60 mm of the middle piece, 177 mm tall, with its two flanges | That a tall thin wall prints on a bed that moves | Lines from the movement of the bed. The wall thickness at the top and at the bottom. A split between layers. | `docs/research/hardware-envelopes.md` 7 and risk 6 |
| C8 | Floor coupon: two tile corners with a half-lap, a cone and its socket, and a short wall foot with its key | The clearances of joints 2 and 3, which have no coupon | The fit of the cone and of the key. The step between the two tiles on a flat table. | `joints.py`, `OtherJoints`: "the coupon of each joint sets its clearances" |
| C9 | The first real floor tile: front centre, 212 mm x 188 mm x 10 mm | The warp of the largest flat piece. It is also the first part of the cabinet. | The lift of each corner on a flat table with a feeler gauge. The length and the width against the model. | Risk 1 and risk 2 |
| C10 | Warm coupon: a plaque in PETG | That the PETG and its paint stay good at the temperature of the exhaust | One hour at the measured exhaust temperature, and 24 hours at 50 C for the painted coupons | `docs/research/hardware-envelopes.md` 7 and `docs/research/petg-finishing.md` 4.4, test 3 |
| C11 | Latch coupon for the control panel, when the latch is designed | The latch and the locators under a lever load | Play and rattle | `docs/research/controls-ergonomics.md` 6.5 |

What must be done before the large pieces: C1, C2, C4, C6, C7, C8, C9 and the two bars. They take a few
days. C3 runs for about three weeks, because the paint cures for 7 days and the seam is looked at after
14 days more. The pieces can be printed and assembled dry in that time.

### 5.3 Stage 3: the pieces, in the order of the dry assembly

The order follows "Order of assembly" in the split report and in the blueprint. The floor is the
datum. Each group can be put on the cabinet when it comes off the printer, with screws only.

Print the right piece of a pair first and fit it. Then print the left one. A right piece and its left
twin are alike, so an error shows on the first one.

| Group | Pieces | Estimate | Dry fit when the group is printed |
| --- | --- | --- | --- |
| 1. The floor | 9 floor tiles | 47 h | Screw the tiles together on a flat table. Measure the flatness and the outline. Put the supply and the hub on it. |
| 2. The rear, low | rear lower R, L | 23 h | Stand them on the floor (seam R2). Put the supply against the rear wall: its rear face, its screws, the opening. |
| 3. The deck | deck nose, deck side R, L | 26 h | Seams F1 and F2. Lay a printed control panel plate in the pocket. Fit the USB socket plate. |
| 4. The front, low | apron, lower R, L | 28 h | Seams D1, D2, P1 and S1. The deck now joins the rear. Sit in front of it: the height of the deck and the reach. |
| 5. The middle | middle R, L | 29 h | Seam L1. The ring closes at the second piece. Measure the door opening (422.7 mm x 165 mm) and the opening behind the bezel (434.7 mm). Fit the monitor cradle and the BC-250 carrier when they exist. |
| 6. The head | upper R, L, brow, upper rear R, L | 45 h | Seams B1, W1, R1, R3 and R5. The brow and the second upper rear half close their rings from above. Lift the cabinet by the two hand-holds, with no hardware in it at first. |
| 7. The parts that come off | door half R, L, hood centre, hood side R, L, speaker form R, L, logo form, bezel half R, L | 110 h | Bond the door halves on a flat table (R4) and the hood pieces (H1) after the coupon result. Before that, fit them with screws. |

The longest prints are in group 7. They are not necessary for the first fit of the hardware, so they can
run last or between the other groups.

### 5.4 Stage 4: the dry assembly with all hardware

This is pass 1 of the split report: each bonded joint has its screws only, and all the hardware is in.
Do the tests of the brief, section "Dry assemble before paint": remove and fit the monitor, the compute
module, the rear door and the control panels several times, and run the hardest load with the covers on.
Correct or print again each piece that does not fit. Do not bond before this pass is complete.

### 5.5 Stage 5: bond

This is pass 2. It needs the result of coupon C3 (the adhesive).

1. Take the hardware out.
2. Open one batch of one to three seams. Follow the order of the split report: the floor tiles, the
   rear lower pieces, the deck, the apron and the lower pieces, the middle pieces, then the brow, the
   upper pieces and the upper rear pieces.
3. Scuff the flange faces (P180) and clean them with isopropyl alcohol (`docs/research/petg-finishing.md` 2.1).
4. Put the adhesive on the flange faces. Put the same screws into the same holes. The work time of the
   first candidate adhesive is 15 minutes to 18 minutes at 24 C.
5. Let the batch cure before the next batch.
6. Bond the two door halves and the three hood pieces apart from the cabinet, on a flat table.
7. Do not bond a service seam: the rear door, the hood (bolted since 2026-11-16: four screws from below, reached through the rear door), the bezel plate, the
   control panel and the USB socket plate. Mask their threads, pins and seats.

### 5.6 Stage 6: fill, prime and paint

The steps and the wait times are those of `docs/research/petg-finishing.md` 1.1. The coupon can change
each product.

| Step | Work | Wait |
| --- | --- | --- |
| 1 | Weld the V-groove with the same PETG, if coupon D was better than coupon A | - |
| 2 | Level the ridges: wet, by hand and block, P180 then P240 | - |
| 3 | Fill the groove and the defects with a polyester glazing putty that lists plastics. Not more than 3 mm thick. | 24 h or more before the last block sanding |
| 4 | Sand the support marks on the seen faces of section 3 (22.7 cm2) | - |
| 5 | Seal and prime with the primer that the plaques chose | By the product |
| 6 | Build with a one-part filler primer. It fills the layer lines and the layer steps on the shallow faces. | 48 h or more before its last sanding (P400 to P600, wet) |
| 7 | Spot putty on pinholes, over primer only | - |
| 8 | Colour | 7 days or more before the shell goes near the warm exhaust |
| 9 | Clear coat (optional). No isocyanate product. | By the product |

The parts that come off (the bezel plate, the speaker forms, the rear door) are painted alone and
fastened last. The inside does not get the finish of the exterior (roadmap, "Settled by the owner").

### 5.7 Stage 7: final assembly

Put the hardware in again. Stick the non-slip pads under the floor. Write down the print settings, the
real part numbers and the fasteners (the brief, section 5 of the checklist).

## 6. Slicer settings to keep the same on each piece

These are the settings of the coupon README (`cad/out/coupon/README.md`). The coupons prove the
joint only if the pieces have the same settings.

| Setting | Value | Reason |
| --- | --- | --- |
| Skin | Solid. About 10 wall loops at a line width of 0.4 mm to 0.45 mm, so that the 4 mm skin, the flange and the gusset have no infill. | Sanding must not get to infill (`docs/research/petg-finishing.md` 2.6) |
| Layer height | One value for the coupons and the seen pieces: 0.12 mm or 0.16 mm. Coupon C6 decides. | The step on a sloped face goes with the layer height |
| Slicer seam | On the inner face or on the flange, by seam painting. Never on the outer face. | Risk 4 |
| Support | None on an outer face, except the places of section 3. Paint the support on by hand at these places. | The support marks must stay small |
| Brim | None on the outer edge. Brim ears at the corners or at the ends of an arc, if a piece lifts. | A brim on a seen edge leaves a line to sand |
| Holes | No hole compensation on the pilot holes | The repeated-drive test measures the pilot as printed |
| Plate and temperatures | Textured PEI plate. The slicer's Bambu PETG profiles for the A1: nozzle 240 C to 245 C, bed 70 C, part fan 30 % to 50 %. | SOURCED [B1]. Do not print PETG on a smooth PEI plate: "the adhesion may be too strong" [P3]. |
| Floor tiles | Two skins of 1.2 mm and a gyroid core of 40 % (the split report). A layer of 0.2 mm to 0.24 mm. | Not seen. Faster. |

## 7. The risks of a large PETG shell

### Risk 1: warp of the long flat pieces

The flat pieces are the floor tiles (212 mm x 188 mm at most) and the door halves (211 mm x 165 mm x 4 mm).

| What the sources say | Source |
| --- | --- |
| Warp comes when the plastic shrinks and lifts from the bed, "most often at the corners of large parts". Draughts from an open window or an air conditioner make it worse. A brim adds adhesion. | SOURCED [P1] |
| The same maker says that PETG "does not shrink or warp", and calls it suitable for large models. | SOURCED [P3] |
| On an open printer, long flat parts lift at the corners. | `docs/research/hardware-envelopes.md` 7 (an estimate from the machine layout) |
| ABS is much worse: a full-plate flat part warped in a heated chamber. This is a reason against a change to ABS for the floor. | `docs/research/abs-switch.md` 3.1 |

The sources do not agree for PETG. Coupon C9 measures it.

| Answer | Where |
| --- | --- |
| The floor is nine tiles, and no tile is longer than 212 mm. | Design: the split |
| The half-laps and their screws pull the tiles flat against each other, on a flat table. | Design: joint 2 |
| The floor is a sandwich with a core, not a solid plate, so less plastic shrinks. | Design: the owner's floor |
| The walls print upright. They are curved, and a flange stiffens each edge. | Design: the orientation |
| The door halves are bonded into one cover on a flat table. | Design: seam R4 |
| A clean textured plate, brim ears at the corners, no draught, and the part fan as the profile sets it. | Slicer and room [P1][B1]. `docs/research/cabinet-references.md` has brim ears of 5 mm. |
| If a door half warps: print it with ribs up, or make it thicker at the edges. | A change of the design, for the owner |

### Risk 2: shrink across the large openings

| Fact | Source |
| --- | --- |
| One study measured printed PETG 0.76 % short in X and 0.54 % short in Y. | `docs/research/abs-switch.md` 3.3 (a study read through a second source) |
| At these values a piece of 229 mm is 1.2 mm to 1.7 mm short. The opening behind the bezel (434.7 mm, two pieces) is 2.3 mm to 3.3 mm narrow. The door opening (422.7 mm) is 2.3 mm to 3.2 mm narrow. | ESTIMATED from the line above |
| The carrier of the monitor passes the opening with 3.3 mm on each side. A shrink of 3.3 mm takes half of this room. | The fit report. ESTIMATED |

Two pieces that meet at a seam shrink the same, so the seams still fit. The hardware does not
shrink. Thus the risk is at each place where a bought part goes into a printed opening.

| Answer | Where |
| --- | --- |
| Measure the two bars of stage 1 and the first floor tile. | Coupon C9 |
| Set the shrink compensation of the filament in the slicer to the measured value, or scale each piece by it. Use one value for all pieces. | Slicer. The coupon README gives the same method for ABS. |
| Measure the door opening and the bezel opening at the dry fit of group 5. | Stage 3 |

### Risk 3: the seen facets at 45 degrees

The rear facet of the rear shelf, the roofs of the hand-holds and the base facet are 45 degrees by
design. They are 489.6 cm2 of seen face, and 149.7 cm2 is on each upper rear piece. A face at 45
degrees prints with no support, but it is at the limit. Its surface can be rough, and a player sees the
rear shelf from the side.

| Answer | Where |
| --- | --- |
| Print the facet coupon at two layer heights before the upper rear pieces. | Coupon C6 |
| Use the thinner layer on these pieces. | Slicer |
| The filler primer and the sanding of stage 6 level what stays. The facets are flat, so a hard block works. | Finish |
| If the coupon is bad: a support on the facet (a seen face, more sanding), or a different orientation of the upper rear pieces. | A change of the print plan |

### Risk 4: seams

Two things have the name "seam".

The slicer seam is the line where each layer starts and stops.

| Answer | Where |
| --- | --- |
| Paint the seam on the inner face or on the flange. | Slicer. The coupon README. |
| Each piece has an inside flange at each edge, so a place for the seam is always there. | Design: joint 1 |

The bonded seam is the line between two pieces. It can show again through the paint as a ghost line.

| Cause | Answer | Source |
| --- | --- | --- |
| The joint moves, and the filler cracks. | The flange, the key, the adhesive on the full length and the screws make a stiff joint before the filler goes on. | `docs/research/petg-finishing.md` 2.3 and decision record 0006 |
| The filler or the primer shrinks after the sanding. | The wait times of stage 6. A groove of only 1.0 mm x 0.8 mm keeps the filler thin. | The same note and `joints.py` |
| The filler is a different material from the PETG. | Weld the groove with PETG, if coupon D shows less change than coupon A. | The same note, 4.4 |
| A seam on an open face. | Most seams lie in a line of the form. The seams on open faces are in the list of the split report, with their seen lengths. | The split report, "Seams" |

### Risk 5: the first layer at the joints (elephant foot)

The first layer is pressed on the bed, and it comes out wider than the model [P2]. A piece above a
seam prints with the seam on the bed. Its flange face, its groove and its half of the V-groove are
thus in the first layer. A lower piece stands on its foot flange, and the key of joint 3 is in the
first layer.

| Answer | Where |
| --- | --- |
| The mouth of the groove has a chamfer of 0.3 mm "against the first-layer squish on the bed". | Design: `joints.py`, `groove_chamfer` |
| The groove is 0.5 mm deeper than the key, so the depth does not locate. | Design: `groove_extra_depth` |
| The half V-groove is at the edge that is on the bed. A small flare there goes into the groove, and the filler covers it. | Design: `vgroove_w`, `vgroove_d` |
| The pilot hole has a counterbore at its mouth, so that no bulge lifts the faces. | Design: `pilot_counterbore_d` |
| The slicer's profile of 0.16 mm for the A1 has an elephant foot compensation of 0.075 mm. Do not set it to 0. | Slicer [B1] |
| A large compensation makes the brim hold less. | SOURCED [P2] |
| The coupon measures the step at the V-groove. If the step is more than the filler can hide, increase the compensation and print the pair again. | Coupon C1 |
| The key of joint 3 and the cone of joint 2 have no coupon. | Coupon C8 |

### Risk 6: tall thin walls on a bed that moves

The bed of the A1 moves in Y. A tall thin part rocks at each change of direction, and a thin wall can
split between layers in a draught (`docs/research/hardware-envelopes.md` 7). The tall pieces are the
bezel half (217 mm), the hood centre (212 mm) and the middle pieces (177 mm).

| Answer | Where |
| --- | --- |
| The ratio of height to the smaller side of the box is 1.5 at most (the hood centre). The rule of the note is less than 4. | The split. ESTIMATED from the print boxes. |
| The wall pieces are curved in plan or have a return, and a flange with a gusset is at each edge. | Design |
| Print the tall wall coupon first. | Coupon C7 |
| If lines show: put the long side of the piece along X, or decrease the acceleration for the outer wall. | Slicer. PROVISIONAL |
| Keep the printer out of a draught. | Room [P1] |

### Risk 7: wet filament, strings and blobs on the seen faces

PETG takes up water. Wet PETG gives bubbles and strings (`docs/research/petg-finishing.md` 2.6). Strings
"can be moderated with higher retractions and lower nozzle temperature", and cooling keeps details sharp
[P3]. Dry each spool before a seen piece. Keep the profile that gives a good layer bond: the fan of
the Bambu PETG profiles for the A1 is 30 % to 50 % [B1].

### Risk 8: layer steps on the shallow faces

The report gives "shallow tops": faces at 1 degree to 25 degrees from level, which show layer steps. They
are 22.3 cm2 on each lower piece, 17.0 cm2 and 16.4 cm2 on the hood sides, and 11.7 cm2 on each deck
piece. The rail land on the middle pieces is reclined 25 degrees to 33 degrees and shows fine steps.
The filler primer and the sanding of stage 6 level them. A thinner layer on these pieces makes the
steps smaller.

### Risk 9: a long print that fails

The hood centre is about 21 hours, and four more pieces are about 15 hours or more. A print that fails
late costs a day and up to 0.56 kg of filament. Print the long pieces when a person can look at the first
layers. Keep one spare spool. The 20 % of section 4 is for this.

## 8. Sources

| No. | Source | What it is |
| --- | --- | --- |
| B1 | https://github.com/bambulab/BambuStudio/tree/master/resources/profiles/BBL (files `filament/Bambu PETG Basic @BBL A1.json`, `filament/Bambu PETG Basic @base.json`, `filament/Bambu PETG HF @BBL A1.json`, `filament/Bambu PETG HF @base.json`, `filament/fdm_filament_pet.json`, `process/0.16mm Optimal @BBL A1.json`, `process/fdm_process_single_0.16.json`) | The slicer's profiles: the largest flow (13 mm3/s for PETG Basic and 18 mm3/s for PETG HF on the A1), the density (1.25 g/cm3 and 1.28 g/cm3), the temperatures, the fan, the elephant foot compensation (0.075 mm), the wall speeds (200 mm/s outer, 300 mm/s inner) |
| P1 | https://help.prusa3d.com/article/warping_2011 | A printer maker's article on warp: cause and remedies |
| P2 | https://help.prusa3d.com/article/elephant-foot-compensation_114487 | A printer maker's article on the elephant foot and its compensation |
| P3 | https://help.prusa3d.com/article/petg_2059 | A printer maker's article on PETG: warp, adhesion to the plate, strings, cooling |

Files of this repository: `cad/out/shell-rev7/split/report.md` and `cad/out/shell-rev7/fit/report.md`
(build outputs, read in the main checkout), `cad/out/coupon/README.md` (a build output),
`cad/candybar/shell/joints.py`, `cad/params/printer.csv`, and the research notes that the text names.

Not accessible: the PETG guide of the printer's maker (https://wiki.bambulab.com/en/filament/petg)
answered HTTP 402 to the fetch. The statement that PETG takes up water is from
`docs/research/petg-finishing.md`, which read that guide on 2026-11-11.

Not done: no piece was sliced. No print was made.
