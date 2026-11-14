# Print plan for ABS on the Qidi Q2

Date: 2026-11-14. Each source was read on this date unless the text gives a different date.

The owner decided on 2026-11-14: the shell is ABS, and the printer is a Qidi Q2. This plan is
`docs/design/print-plan.md` (the "first plan", for PETG on the Bambu A1) done again for that decision.
`docs/research/abs-on-the-q2.md` (the "ABS note") has the research and the sources. The source numbers
in square brackets, for example [Q5], are those of section 8 of the ABS note.

The shell is that of revision 7, as `cad/out/shell-rev7/split/report.md` cuts it: 23 printed pieces,
9 floor tiles and 2 halves of a bezel plate. The split does not change for this plan.

The pieces are not ready to print. The split is the bare 4 mm skin: the flanges, the keys, the ribs
and the carriers are not modelled. Each mass and each time in this plan is an estimate by a rule of
thumb. It is not a slicer result. Nothing was printed, and no piece was sliced.

## Status tags

| Tag | Meaning |
| --- | --- |
| REPORT | A value of the split report or of a different build output. The file is named. |
| MAKER [id], STUDY [id], USERS [id] | From a source of the ABS note, with its number there |
| ESTIMATED | Calculated here. The rule is given. |
| PROVISIONAL | A setting or an order proposed here. A test or the owner can change it. |
| NOT CONFIRMED | No source says it. A test must show it. |

## 1. Summary

1. The shell, the floor, one bezel plate, the inside parts and the coupons are about 10.3 kg of ABS
   and about 420 hours of printing. With 30 % more for failed prints and second prints, the plan is
   14 spools of 1 kg and about 540 hours.
2. ABS adds time in which the printer does not print: a heat soak before each job and a slow
   cool-down after it. This is about 150 hours more for the printer.
3. Each of the 32 pieces fits the Q2 with more room than on the A1. The Q2 is not taller than the
   A1, so no piece changes.
4. No piece needs support on a large seen face. Support touches 22.7 cm2 of seen face in total, as in
   the first plan.
5. Print the coupons first. Four results stop the large pieces until they are known: the shrink of the
   filament, the warp of a floor tile, the face at 45 degrees, and the tall wall.
6. The largest risks are the warp of the flat pieces, cracks between layers, the shrink across the
   large openings, and cracks from a solvent at a screw or an insert. A coupon or a measurement
   answers each one.
7. The seams are welded, not bonded with an adhesive. A weld sets in minutes, so the seams are
   welded one at a time.
8. The printer stands in a room that is not a living room, with a vent to the open air. The filter
   of the printer is not sufficient by itself.

## 2. What stays true from the first plan, and what is replaced

| Part of the first plan | For ABS on the Q2 |
| --- | --- |
| The pieces, their orientation and their print boxes | Stay. The split does not change. |
| The limit of the printer (240 x 240 x 245) | Replaced: 250 x 250 x 250 on the bed (the ABS note, 2.3) |
| The masses | Replaced. ABS has a density of 1.05 g/cm3, and the split used 1.27 g/cm3 for PETG. |
| The print times of the pieces | Stay within 2 %: the volumes and the flows are the same. The heat soak and the cool-down are new. |
| The 20 % for failed prints | Replaced: 30 % |
| The support on seen faces (22.7 cm2) and the faces at 45 degrees (489.6 cm2) | Stay. They come from the form and the orientation. |
| The list of coupons C1 to C11 | Stays. Each coupon is printed in ABS, and what it must prove changes. Coupon C3 becomes the weld coupon. Four tests are new. |
| The order of the pieces (the groups of the dry assembly) | Stays |
| Stage 5, the bond with a methacrylate adhesive | Replaced by the weld. The adhesive stays as one candidate. |
| Stage 6, the fillers and the primers for PETG | Replaced by products for ABS. The wait times change. |
| The slicer settings | Replaced. The rules for the slicer seam, the support and the holes stay. |
| Risk 1, warp | Replaced. It is the main risk now. |
| Risk 2, shrink | Stays, with the ABS numbers and a setting in the slicer |
| Risk 3, the faces at 45 degrees | Stays, and it is larger: the fan now also changes the layer bond |
| Risk 4, seams | Stays. The cause of a ghost line changes: solvent that leaves the seam. |
| Risk 5, the first layer at the joints | Stays. The profile of the Q2 compensates 0.15 mm, not 0.075 mm. |
| Risk 6, tall thin walls on a bed that moves | Goes. The bed of the Q2 moves in Z only [Q1]. Cracks between layers take its place. |
| Risks 7, 8 and 9 (wet filament, layer steps, a long print that fails) | Stay |
| The Bambu A1 | It is free. It can print the inside parts and the jigs in PETG at the same time. |

## 3. The rules of thumb

| Rule | Value | Basis |
| --- | --- | --- |
| Density of ABS | 1.05 g/cm3 | MAKER [M1], and the slicer's profiles of two ABS filaments [Q5]. One ABS has 1.12 g/cm3 [M3]: with it, each mass is 7 % more. |
| Skin mass of a piece | Its volume in `measurements.json` times 1.05 g/cm3 | REPORT and ESTIMATED |
| Printed mass of a wall piece or a door half | Skin mass x 1.30 | As the first plan: 25 % for ribs, flanges and plates, 5 % for the brim and waste |
| Printed mass of a trim piece (speaker form, logo form, bezel half) | Skin mass x 1.10 | As the first plan |
| Printed mass of a floor tile | Mass as a 4 mm skin x 1.42 x 1.05 | As the first plan: the sandwich of 10 mm against the 4 mm skin, and 5 % of waste |
| Print rate of a seen piece | 22.7 g in 1 hour | An average flow of 6 mm3/s, as the first plan. The slicer's limit for ABS on the Q2 is 17 mm3/s [Q5]. |
| Print rate of a hidden piece (floor tile) | 34 g in 1 hour | An average flow of 9 mm3/s, as the first plan |
| Print rate of the inside parts | 29 g in 1 hour | The 35 g in 1 hour of the first plan, by volume |
| Failed prints and second prints | 30 % more filament and time | `docs/research/abs-switch.md` 8.1 gives 25 % to 40 % for ABS |
| Inside parts that are not designed | 1.7 kg | The 2.0 kg of the first plan, by volume. They can be PETG on the A1. |
| Coupons | 1.3 kg | Eight pairs of the joint coupon, four plaques, and the small coupons of section 6.2. ESTIMATED from their print boxes |
| Heat soak and cool-down | 2 hours for each job | A heat soak of about 20 minutes and a wait of 1 hour to 2 hours before the door is opened. USERS [Q11], one report for each value |

All ESTIMATED. The time can be 30 % less or more. A layer of 0.12 mm in place of 0.16 mm makes a seen
piece about one third slower.

## 4. The pieces

The orientation and the print box are those of the split report. The limit is 250 mm x 250 mm on the
bed and 250 mm high. "Spare to the limit" is the limit less the box, in x, y and z. "Skin" is the solid
4 mm skin in ABS. "Support on a seen face" is the report's "seen face over 45 deg".

| # | Piece | On the bed | Print box (mm) | Spare to the limit (mm) | Skin (g) | Printed mass (g) | Time (h) | Support on a seen face | Note for ABS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | deck nose | upright, on the bed diagonal | 218 x 218 x 72 | 32, 32, 178 | 118 | 153 | 6.8 | No | A long thin wall with two tips: ears at the tips |
| 2, 3 | deck side R, L | upright | 186 x 185 x 72 | 64, 65, 178 | 160 each | 208 each | 9.2 each | Yes, 1.9 cm2 each | - |
| 4 | apron | on its rear edge, on the bed diagonal | 210 x 210 x 114 | 40, 40, 136 | 151 | 196 | 8.6 | Yes, 2.7 cm2 | It stands on a narrow edge: a brim on the inner side |
| 5, 6 | lower R, L | upright | 181 x 181 x 134 | 69, 69, 116 | 161 each | 209 each | 9.2 each | No | - |
| 7, 8 | middle R, L | upright, on the bed diagonal | 209 x 208 x 177 | 41, 42, 73 | 245 each | 319 each | 14.1 each | No | A tall thin wall with the cut-ins: cracks between layers |
| 9, 10 | upper R, L | upright | 206 x 205 x 131 | 44, 45, 119 | 191 each | 249 each | 11.0 each | Yes, 0.6 cm2 each | 28.6 cm2 at 45 degrees each |
| 11 | brow | upright | 170 x 170 x 38 | 80, 80, 212 | 46 | 60 | 2.7 | No | - |
| 12, 13 | upper rear R, L | upright | 180 x 180 x 143 | 70, 70, 107 | 169 each | 220 each | 9.7 each | No support. 149.7 cm2 at 45 degrees each. | The roof of the hand-hold carries the lift: risk 5 |
| 14, 15 | rear lower R, L | upright | 229 x 228 x 116 | 21, 22, 134 | 200 each | 260 each | 11.4 each | Yes, 0.3 cm2 each | The largest piece, with a straight wall of 235 mm: the first test of warp on a wall |
| 16, 17 | door half R, L | outer face on the bed | 211 x 165 x 4 | 39, 85, 246 | 147 each | 191 each | 8.4 each | No | A thin flat plate: risk 1. The door is in design, and its box changes. |
| 18 | hood centre | on a cut face | 148 x 139 x 212 | 102, 111, 38 | 354 | 460 | 20.3 | No | Tall: cracks between layers. The longest print. |
| 19, 20 | hood side R, L | upright | 139 x 129 x 148 | 111, 121, 102 | 277 each | 360 each | 15.9 each | Yes, 7.2 cm2 each | - |
| 21, 22 | speaker form R, L | front face on the bed | 94 x 76 x 13 | 156, 174, 237 | 71 each | 78 each | 3.4 each | No | Stand-ins |
| 23 | logo form | front face on the bed | 160 x 160 x 5 | 90, 90, 245 | 46 | 51 | 2.2 | No | A stand-in |
| - | floor front side R, L | flat | 188 x 132 x 10 | 62, 118, 240 | 100 each, as a 4 mm skin | 150 each | 4.4 each | Not seen | Flat: risk 1 |
| - | floor front centre | flat | 212 x 188 x 10 | 38, 62, 240 | 167, as a 4 mm skin | 249 | 7.3 | Not seen | The largest flat piece: coupon C9 |
| - | floor middle side R, L | flat | 163 x 137 x 10 | 87, 113, 240 | 94 each, as a 4 mm skin | 139 each | 4.1 each | Not seen | Flat: risk 1 |
| - | floor middle centre | flat | 212 x 163 x 10 | 38, 87, 240 | 145, as a 4 mm skin | 216 | 6.4 | Not seen | Flat: risk 1 |
| - | floor rear side R, L | flat | 177 x 137 x 10 | 73, 113, 240 | 92 each, as a 4 mm skin | 137 each | 4.0 each | Not seen | Flat: risk 1 |
| - | floor rear centre | flat | 212 x 177 x 10 | 38, 73, 240 | 158, as a 4 mm skin | 235 | 6.9 | Not seen | Flat: risk 1 |
| - | bezel half R, L | on its cut face, the profile on the bed diagonal | 223 x 223 x 217 | 27, 27, 33 | 315 each | 347 each | 15.3 each | No | The tallest piece: cracks between layers |

Notes on the table:

- The piece with the least spare room on the bed is "rear lower" (21 mm and 22 mm). On the A1 it had
  11 mm and 12 mm.
- The piece with the least spare height is the bezel half (33 mm), then the hood centre (38 mm).
- The longest single print is the hood centre, about 20 hours. Each other piece is less than
  16 hours.
- The support that touches a seen face is 22.7 cm2 in total: 14.4 cm2 on the two hood sides, 2.7 cm2 on
  the apron, 3.8 cm2 on the two deck sides, 1.2 cm2 on the two upper pieces and 0.6 cm2 on the two rear
  lower pieces. REPORT
- The seen faces at 45 degrees are 489.6 cm2. They print with no support. REPORT
- With the shrink compensation of the slicer, each piece is 0.6 % to 0.7 % larger on the bed than its
  box in this table. The largest piece is then 231 mm.
- The floor can be PETG on the A1. Then its masses and times are those of the first plan (1.88 kg and
  47 hours), and the Q2 does not print it. The owner decides (the ABS note, section 5, rule 20).
- The table has one bezel plate. The owner wants four.

## 5. The totals

| Group | Printed mass | Time |
| --- | --- | --- |
| The 23 pieces of the shell | 5.1 kg | 225 h |
| The 9 floor tiles | 1.55 kg | 46 h |
| One bezel plate (2 halves) | 0.69 kg | 31 h |
| Inside parts (allowance) | 1.7 kg | 57 h |
| Coupons | 1.3 kg | 57 h |
| **Subtotal** | **10.3 kg** | **416 h** |
| Failed prints and second prints, 30 % | 3.1 kg | 125 h |
| **Plan** | **13.4 kg, 14 spools of 1 kg** | **about 540 h of printing** |
| Heat soak and cool-down, about 75 jobs | - | about 150 h |
| Three more bezel plates, later | 2.1 kg | 92 h |

All ESTIMATED by the rules of section 3. For comparison: the first plan has 14.6 kg of PETG and about
500 hours. `docs/research/abs-switch.md` 8.1 gives 9 kg to 18 kg of ABS for the same shell, by area.

The printer is in use for about 690 hours. At 12 hours each day, this is about eight weeks. At
20 hours each day, it is about five weeks. ESTIMATED

If the A1 prints the floor and the inside parts in PETG, the Q2 has about 135 hours less of printing,
and the plan needs 10 spools of ABS. ESTIMATED: 46 hours and 57 hours, with 30 % more.

Buy the filament of one maker, one type and one colour for the coupons and for the shell. The
coupons prove the weld, the paint and the shrink on that filament only. Make the dissolved ABS for
the weld and the filler from the same spools.

The filter of the printer: the maker gives a change of the carbon every 200 hours to 300 hours for
materials such as ABS [Q8]. The plan thus needs two or three spare cartridges.

## 6. The order of work

### 6.1 Stage 1: the place, the printer and the filament

Do these steps before the first ABS print.

| Step | What it proves or gives | What to measure |
| --- | --- | --- |
| Choose the place of the printer | A room that is not a living room or a bedroom, with a window fan or a duct to the open air | The room stays above 15 °C in winter (`docs/research/abs-switch.md` 3.6) |
| Set up the Q2 and run its calibration | The machine works | The first layer of the maker's test print |
| T1. Dry the filament | No bubbles and no strings | 70 °C for 8 hours [Q4], or 80 °C for 8 hours [M1]. Keep the same value for each spool. |
| T2. A single layer of 250 mm x 250 mm with a brim of 5 mm | The reach of the nozzle, the first layer at the edges, the excluded corner and the purge lines | Gaps or ridges at the four corners. The place of the purge lines. |
| T3. A bar of 200 mm in X, a bar of 200 mm in Y and a post of 100 mm in Z | The shrink of this ABS on this printer | Each length with a caliper, one day after the print. Then set "Shrinkage" in the filament profile. |
| T4. The chamber | The temperature that the chamber holds, and the time to get there | A thermometer in the chamber at 55 °C and at 60 °C, for one hour |

Print T3 with the settings of the pieces: the solid 4 mm wall and the chamber of the pieces.

### 6.2 Stage 2: the coupons and the test prints

The numbers C1 to C11 are those of the first plan. Each coupon is printed in ABS on the Q2, with the
settings of section 7.

| # | Print | What it must prove for ABS | What to measure |
| --- | --- | --- | --- |
| C1 | Joint coupon, three pairs with groove clearances of 0.1 mm, 0.2 mm and 0.3 mm | The key clearance in ABS, with the first-layer compensation of the Q2 (0.15 mm). That the gusset and the bridge over the groove print clean with little fan. That the flange faces touch, which a weld needs. | The force to put the halves together, and the play. The step at the V-groove with a feeler gauge. A gap between the flange faces against the light. |
| C2 | The repeated-drive test on one pair of C1 | The pilot hole: 2.4 mm (the screw maker's value for ABS) against 2.25 mm. That the flange does not split across the layers. | The number of the first drive at which the thread does not hold, for each hole. A crack in the flange or the gusset. |
| C3 | Weld coupon: five pairs at the chosen clearance, and four plaques | The weld product, the filler in the groove, the primer and the paint. That no crack starts at a screw. That the seam does not show after two weeks. | The six tests of `docs/research/petg-finishing.md` 4.4. A look for cracks at each screw after one week and after two weeks. |
| C4 | Insert coupon: holes of 5.6 mm, 5.7 mm and 5.8 mm for M4 and of 4.0 mm, 4.1 mm and 4.2 mm for M3. Hole depth 9.5 mm for M4. Bosses of 12 mm and 13 mm. | The hole in ABS with the iron at 265 °C. That a boss does not crack when primer and lacquer go on it. | Does the insert seat flush with a small resistance? Tighten a screw until it fails. Put primer and lacquer on one boss, and look for cracks after one week. |
| C5 | Hole coupon: the button holes, the hole of the power button, a pin hole of 4.1 mm, the two USB cut-outs | The printed size of each hole with the shrink compensation on | The fit of the real part, or the hole with a caliper |
| C6 | Facet coupon: a slice of 130 mm of the upper rear piece, with the rear facet and one whole hand-hold (the first plan had a slice of 60 mm). Two prints: one with the fan of the profile on overhangs (80 %), one with 30 %. | The surface of a seen face at 45 degrees with no support. The layer bond of the roof that carries the lift. | The facet under raking light. Then hang 12 kg on the roof for one minute (the design load is 116 N). Then load it until it breaks, and write down the load and the place of the break. |
| C7 | Tall wall coupon: a slice of 60 mm of the middle piece, 177 mm tall, with its two flanges and one cut-in. Two prints: the solid skin, and three wall loops on each side with a core. | That a tall wall of 4 mm does not crack between layers. That the flange makes no mark on the outer face. Which skin warps less. | A crack at the cut-in or at the gussets. The bow of the free ends on a flat table. The outer face under raking light at the flanges. |
| C8 | Floor coupon: two tile corners with a half-lap, a cone and its socket, and a short wall foot with its key | The clearances of joints 2 and 3 in ABS | The fit of the cone and of the key. The step between the two tiles on a flat table. |
| C9 | The first real floor tile: front centre, 212 mm x 188 mm x 10 mm | The warp of the largest flat piece. It decides the material of the floor. | The lift of each corner on a flat table with a feeler gauge. The limit is 0.5 mm (PROVISIONAL). The length and the width against the model. |
| C10 | Warm coupon: a painted plaque | That the paint on ABS stays good near the warm exhaust | 24 hours at 50 °C, as test 3 of the PETG note |
| C11 | Latch coupon for the control panel, when the latch is designed | The latch and the locators under a lever load | Play and rattle |
| C12 | The first real wall piece: rear lower R, 229 mm x 228 mm x 116 mm | The warp of the largest wall piece, and its size after the shrink compensation | The lift of the two ends and of the corner. The length against the model. |

The five pairs of the weld coupon (C3). PROVISIONAL:

| Pair | Weld | Why |
| --- | --- | --- |
| A | ABS dissolved in acetone, 10 g in 50 ml, on the flange faces | The mix with the highest strength in one study [W4]. One material in the seam. |
| B | A thick cement with MEK for ABS, on the flange faces | A maker's product with a data sheet and a working time of 10 minutes [W2] |
| C | A thin cement with MEK, or acetone, into the closed joint from the inner edge | The least work, if it gets between the faces [W1] |
| D | The methacrylate adhesive of the PETG plan | The control: no solvent, and it fills a gap |
| E | The best of A, B and D, with a shim of 0.5 mm between the flange faces | The two closing seams of each ring have this gap |

On each pair, fill one half of the V-groove with dissolved ABS (20 g in 50 ml, in thin layers) and
the other half with a polyester putty that lists ABS. The four plaques compare the primers: a
one-part plastic primer that lists ABS, an adhesion promoter with a filler primer, a filler primer
direct, and a hobby lacquer primer direct.

What must be done before the large pieces: T2, T3, C1, C2, C4, C6, C7, C8 and C9. They take about one
week. C12 is then the first large piece. Coupon C3 runs for about four weeks: 3 days for the weld, 7 days for the filler, 7 days for
the paint, and a look at the seam after 14 days more. The pieces can be printed and assembled dry in
that time.

### 6.3 Stage 3: the pieces, in the order of the dry assembly

The order is that of the first plan and of the split report. The floor is the datum. Print the right
piece of a pair first and fit it. Then print the left one.

Print one piece in each job. Many parts on one plate make a long layer time, and the layer bond is
then weaker [M4].

| Group | Pieces | Estimate | Dry fit when the group is printed |
| --- | --- | --- | --- |
| 1. The floor | 9 floor tiles | 46 h | Screw the tiles together on a flat table. Measure the flatness and the outline. |
| 2. The rear, low | rear lower R, L | 23 h | Stand them on the floor (seam R2). Put the supply against the rear wall. |
| 3. The deck | deck nose, deck side R, L | 25 h | Seams F1 and F2. Lay a printed control panel plate in the pocket. |
| 4. The front, low | apron, lower R, L | 27 h | Seams D1, D2, P1 and S1. |
| 5. The middle | middle R, L | 28 h | Seam L1. Measure the door opening (422.7 mm x 165 mm) and the opening behind the bezel (434.7 mm). |
| 6. The head | upper R, L, brow, upper rear R, L | 44 h | Seams B1, W1, R1, R3 and R5. Lift the cabinet by the two hand-holds, with no hardware in it. |
| 7. The parts that come off | door half R, L, hood centre, hood side R, L, speaker form R, L, logo form, bezel half R, L | 109 h | Fit them with screws. |

The two openings of group 5 show if the shrink compensation is correct. If an opening is more than
1 mm from the model, correct "Shrinkage" before group 6.

### 6.4 Stage 4: the dry assembly with all hardware

This stage does not change. It is pass 1 of the split report: each seam has its screws only, and all
the hardware is in. Do not weld before this pass is complete. A weld cannot be opened again.

### 6.5 Stage 5: weld

This is pass 2. It needs the result of coupon C3.

Do this work with a window open or outdoors. Keep flames, heaters and sparks away. Wear gloves that
resist ketones, and goggles.

1. Take the hardware out.
2. Open one seam. Follow the order of the split report.
3. Scuff the two flange faces with P240. Remove the dust.
4. Clean the faces with isopropyl alcohol. Let them dry.
5. Put the weld product on the flange faces, between the screws.
6. Keep the weld product out of the pilot holes and off the outer face.
7. Close the seam. Put the same screws into the same holes.
8. Tighten each screw until the flange faces touch.
9. Do not wipe the outer face with a solvent.
10. Wait 2 hours before you open a seam that touches the same piece.

More rules for this stage:

- Open one seam at a time. The working time of a weld is 3 minutes to 10 minutes [W1][W2]. The first
  plan opened one to three seams, because its adhesive had 15 minutes.
- For the two closing seams of each ring, use the product that pair E chose. A thin solvent does not
  fill their gap of 0.5 mm.
- Weld the two door halves and the three hood pieces apart from the cabinet, on a flat table.
- Do not weld a service seam: the rear door, the hood (if the owner bolts it), the bezel plate, the
  control panel and the USB socket plate. Mask their threads, pins and seats.
- If the floor is PETG, a solvent does not join it to the ABS wall feet [W1]. Use the screws and the
  methacrylate adhesive there.

| After the weld | Wait |
| --- | --- |
| A lift of the cabinet or a load on a seam | 24 hours |
| The filler in the groove | 72 hours |

### 6.6 Stage 6: fill, prime and paint

The coupon can change each product. The classes and their sources are in the ABS note, 4.2 and 4.3.

| Step | Work | Wait |
| --- | --- | --- |
| 1 | Level the ridges at the seams by hand and block, P180 then P240. ABS sands wet or dry. | - |
| 2 | Fill the V-groove. With dissolved ABS: two or three thin layers. With a polyester putty that lists ABS: one layer. | Dissolved ABS: 24 hours between layers, and 7 days before the last block sanding. Putty: 24 hours. |
| 3 | Fill the dents and the support marks on the seen faces (22.7 cm2) with the putty. Not more than 3 mm thick. | 24 hours |
| 4 | Clean the shell with isopropyl alcohol. Do not use acetone or a thinner on bare ABS. | - |
| 5 | Prime each face with the primer that the plaques chose. Use light coats. | By the product |
| 6 | Build with a one-part filler primer. It fills the layer lines and the layer steps on the shallow faces. | 48 hours or more before its last sanding (P400 to P600) |
| 7 | Spot putty on pinholes, over primer only | - |
| 8 | Colour | 7 days or more before the shell goes near the warm exhaust |
| 9 | Clear coat (optional). No isocyanate product. | By the product |

Sand each edge break by hand. ABS sands fast, and a machine removes a break of R 1 in seconds.

The parts that come off (the bezel plate, the speaker forms, the rear door) are painted alone and
fastened last. The inside does not get the finish of the exterior.

From the last weld to the last coat, the wait times are about three weeks. ESTIMATED: 3 days, 7 days,
2 days and 7 days.

### 6.7 Stage 7: final assembly

Put the hardware in again. Stick the non-slip pads under the floor. Write down the print settings, the
measured shrink, the real part numbers and the fasteners.

## 7. Slicer settings for ABS on the Q2

The values are a start. The coupons can change each one. Use the same settings on the coupons and on
the pieces.

| Setting | Value | Reason |
| --- | --- | --- |
| Slicer and profile | QIDI Studio, the Q2 with the 0.4 mm nozzle, and the profile of the filament that is bought | MAKER [Q5] |
| Nozzle | 250 °C to 260 °C, as the profile | MAKER [Q5] |
| Bed | 90 °C on the textured plate, as the profile. 100 °C if a corner lifts. | MAKER [Q5][Q4] |
| Chamber | 55 °C. 60 °C if a piece warps or cracks and the filament does not clog. Never off: the profile "Generic ABS" has no chamber value. | MAKER [Q4][Q5][M1] |
| Heat soak | Bed and chamber on for about 20 minutes before the print | USERS [Q11], one report |
| Part fan | As the profile: off on the first three layers, then low. The fan on overhangs: the result of coupon C6. | MAKER [Q5] |
| Auxiliary fan | Off | MAKER [Q5] |
| Skin | Solid: enough wall loops that the 4 mm skin, the flange and the gusset have no infill. Or three loops on each side with a core, if coupon C7 shows less warp and no weak place. | The first plan, and MAKER [M4] |
| Layer height | One value for the coupons and the seen pieces: 0.16 mm or 0.12 mm. Coupon C6 decides. | The first plan |
| Slicer seam | On the inner face or on the flange. Never on the outer face. | The first plan |
| Support | None on an outer face, except the places of section 4. Paint the support on by hand there. | The first plan |
| Brim | Ears at the two ends of a wall piece and at each corner of a flat piece. A full brim of 5 mm with no gap if a piece lifts. | MAKER [M4], USERS [Q11]. A brim on a seen edge leaves a line to sand. |
| Plate | The textured plate, clean. Glue from a glue stick if a corner lifts. | MAKER [M4] |
| First-layer compensation | 0.15 mm, as the profile. Coupon C1 measures the step at the V-groove. | MAKER [Q5] |
| Shrinkage | The value that test T3 measured. One value for each piece. | MAKER [Q5] |
| Holes | No hole compensation on the pilot holes | The first plan |
| Jobs | One piece in each job | MAKER [M4] |
| Cool-down | Leave the door closed for 1 hour to 2 hours after the print | USERS [Q11], one report |
| Floor tiles | Two skins of 1.2 mm and a gyroid core of 40 %. A layer of 0.2 mm to 0.24 mm. | The split report. The core is below the 50 % that one maker gives as the limit for warp [M4]. |
| Filament | Dry each spool before a seen piece. Keep it dry while it prints. | MAKER [M1][Q4] |
| Filter | Change the cartridge every 200 hours to 300 hours. Run the room vent for each print. | MAKER [Q8] |

## 8. The risks of a large ABS shell

### Risk 1: warp of the flat pieces

The flat pieces are the floor tiles (212 mm x 188 mm x 10 mm at most) and the door halves
(211 mm x 165 mm x 4 mm). ABS warps on a large flat face, also in a heated chamber (the ABS note, 3.3).

| Answer | Where |
| --- | --- |
| Print the first floor tile before the other tiles. | Coupon C9 |
| The floor is nine tiles, and no tile is longer than 212 mm. Do not join tiles for the larger bed. | Design: the split |
| The floor is a sandwich with a core of 40 %, not a solid plate. | Design: the owner's floor |
| The chamber at 55 °C to 60 °C, a heat soak, ears at the corners, glue, and a slow cool-down | Slicer and printer |
| If the tile lifts more than 0.5 mm: print the floor in PETG on the A1, or in ABS with glass fibre. | The owner (the ABS note, section 5, rule 20) |
| The half-laps and their screws pull the tiles against each other on a flat table. A tile of 10 mm is stiff, so this corrects little. | Design: joint 2 |
| The door halves are welded into one cover on a flat table. | Design: seam R4 |
| If a door half warps: make its edges thicker, use more ribs that are less high, or print it on its long edge. | A change of the design, for the owner |

### Risk 2: the ends and the corners of the wall pieces lift

A wall piece stands on a thin line. At an upright seam the line ends in a tip. The largest piece,
"rear lower", has a straight wall of 235 mm.

| Answer | Where |
| --- | --- |
| The wall pieces are curved in plan or have a return, and a flange with a gusset is at each edge. | Design |
| The upright rear corners have a round of R 3. | Design: decision record 0007 |
| Ears at each tip, and a full brim if a tip lifts | Slicer |
| Print "rear lower R" as the first wall piece. | Coupon C12 |
| A piece that lifts at one end is not flush at its seam. The dry fit shows it before a weld. | Stage 4 |

### Risk 3: cracks between layers

A crack comes when the stress from cooling is more than the layer bond [M4]. The tall pieces are the
bezel half (217 mm), the hood centre (212 mm) and the middle pieces (177 mm). ABS is weaker than PETG
across the layers in a shock: 7.4 kJ/m2 against 10.6 kJ/m2 [M1][M2].

| Answer | Where |
| --- | --- |
| Print the tall wall coupon first, in the two ways. | Coupon C7 |
| The chamber at 55 °C to 60 °C. The door and the top cover closed. Little fan. | Slicer and printer [M4] |
| One piece in each job, so that a layer does not cool before the next one comes | Slicer [M4] |
| A slow cool-down in the closed chamber | Printer |
| Do not let a bare piece fall. Carry the tall pieces with two hands. | Handling |
| The cut-ins and the gussets are the places to examine first. | Coupon C7 |

### Risk 4: shrink across the large openings

| Fact | Source |
| --- | --- |
| One study measured printed ABS 0.59 % short in X and 0.69 % short in Y. A printer maker gives 1 % to 2 %. | The ABS note, 3.2 |
| At 0.6 % to 0.7 % the opening behind the bezel (434.7 mm) is 2.6 mm to 3.0 mm narrow. The carrier of the monitor has 3.3 mm on each side. | ESTIMATED |
| At 2 % it is 8.7 mm narrow, and the carrier does not pass. | ESTIMATED |

| Answer | Where |
| --- | --- |
| Measure the bars and set "Shrinkage" in the filament profile. | Test T3 |
| Use one filament and one value for each piece. | Section 5 |
| Measure "rear lower R" and the first floor tile against the model. | Coupons C12 and C9 |
| Measure the two openings at the dry fit of group 5. | Stage 3 |

### Risk 5: the seen faces at 45 degrees, and the hand-holds

The faces at 45 degrees are 489.6 cm2 of seen face, and 149.7 cm2 is on each upper rear piece. The ABS
profiles of the Q2 put 80 % fan on such a face at a layer of 0.12 mm or 0.16 mm (the ABS note, 3.6).
More fan gives a cleaner face and a weaker layer bond. The roof of each hand-hold is such a face, and
it carries the lift of the cabinet.

| Answer | Where |
| --- | --- |
| Print the facet coupon at the two fan values, look at the face, and load the roof. | Coupon C6 |
| The estimate for the lift is 7.5 MPa (11.0 MPa for a straight lift). The data sheet gives 32 MPa across the layers. | The split report and [M1] |
| The cabinet is 8 % lighter in ABS (15.9 kg), so the lift load is less. | ESTIMATED |
| The filler primer and the sanding of stage 6 level a rough facet. The facets are flat, so a hard block works. | Finish |
| If the roof breaks below 350 N on the coupon (three times the design load, PROVISIONAL): less fan, a thicker roof, or a rib behind the roof. | A change of the settings or of the design |

### Risk 6: the welded seam shows again

| Cause | Answer |
| --- | --- |
| Solvent that stays in the seam leaves in the weeks after, and the seam sinks. | A thin layer of weld product. The wait times of stage 5 and stage 6. The seam look after two weeks on coupon C3. |
| The filler shrinks. | The groove is only 1.0 mm x 0.8 mm. Thin layers. A putty with no solvent on the second half of each coupon. |
| The joint moves. | The flange, the key, the weld on the full length and the screws |
| A seam on an open face | The list of the split report. It does not change. |

The slicer seam goes on the inner face or on the flange, as in the first plan.

### Risk 7: a solvent cracks the ABS where it is under stress

ABS is a "solvent sensitive" plastic. A lacquer thinner or a cement cracks it at a press fit (the ABS
note, 4.3). The shell has such places: each thread-forming screw, each insert, and the print stress in
the skin.

| Answer | Where |
| --- | --- |
| Look for cracks at the screws of the weld coupon and at the bosses of the insert coupon, after one week and after two weeks. | Coupons C3 and C4 |
| Put the weld product between the screws, not into the pilot holes. | Stage 5 |
| The pilot hole of 2.4 mm gives less stress than 2.25 mm. | Coupon C2 |
| Prime each face before a lacquer touches it. Light coats. | Stage 6 |
| Do not wipe the shell with acetone. | Stage 6 |
| Pair D of the weld coupon has no solvent. If the solvent pairs crack and pair D does not, use the adhesive. | Coupon C3 |

### Risk 8: the first layer at the joints

A piece above a seam prints with the seam on the bed. Its flange face, its groove and its half of the
V-groove are in the first layer. The bed is at 90 °C to 100 °C, near the temperature at which ABS
softens, so the first layers stay soft longer. ESTIMATED

| Answer | Where |
| --- | --- |
| The mouth of the groove has a chamfer of 0.3 mm, and the groove is 0.5 mm deeper than the key. | Design: `joints.py` |
| The profile of the Q2 compensates 0.15 mm. Do not set it to 0. | Slicer [Q5] |
| The coupon measures the step at the V-groove and the gap between the flange faces. | Coupon C1 |
| The key of joint 3 and the cone of joint 2 have their coupon. | Coupon C8 |

### Risk 9: a flange or a rib shows on the outer face

Where a thin wall meets a thick section, a ring shows on the outer wall. The maker's cure is an inner
fillet at the junction [M4]. The level flanges of joint 1 have a gusset of 45 degrees, which is such a
gradual change. A level rib with a square root is not.

| Answer | Where |
| --- | --- |
| Look at the outer face of the tall wall coupon at its two flanges. | Coupon C7 |
| When the ribs are modelled: make a rib upright in the print where the form lets you, and give each root a fillet. | Design, phase 4 |
| The filler primer levels a small mark. | Stage 6 |

### Risk 10: the air in the room

ABS gives off styrene and many ultrafine particles (the ABS note, 4.5). The plan has about 540 hours
of printing.

| Answer | Where |
| --- | --- |
| The printer stands in a room that is not a living room or a bedroom. | Stage 1 |
| A window fan or a duct moves the air of that room to the open air while the printer runs and cools. | Stage 1 |
| The door stays closed until the chamber is cool. | Section 7 |
| A new filter cartridge every 200 hours to 300 hours | Section 5 |
| A mask with a vapour filter for work near the open printer after a long job | The filament maker's advice [M4] |
| The weld and the paint are done with a window open or outdoors, with no flame near. | Stage 5 and stage 6 |

### Risk 11: the filament

| Risk | Answer |
| --- | --- |
| A filament of a different brand gets soft in the feed path at a chamber above 55 °C, and the nozzle clogs [Q4]. | Start at 55 °C. Increase to 60 °C only after a long print with no clog. |
| ABS takes up water (0.65 % for one ABS [M1]). | Dry each spool. Keep it dry while it prints. |
| Two filaments shrink and weld differently. | One maker, one type, one colour |
| The side spool holder is unsteady in one review [Q10]. | Look at it on the first long print. |

### Risk 12: a long print that fails

The hood centre is about 20 hours, and four more pieces are about 15 hours or more. A print that fails
late costs a day and up to 0.46 kg of filament. Print the long pieces when a person can look at the
first layers. Keep one spare spool. The 30 % of section 5 is for this. The Q2 has a camera and a
power-loss recovery [Q1].

### Risk 13: a new printer

The Q2 is new to the owner, and five of its values are not confirmed (the ABS note, 2.7). The first
weeks are calibration, not pieces. Stage 1 and the coupons are that calibration. Do not print a large
piece before test T2, test T3, coupon C7 and coupon C9 are done.

### Risk 14: layer steps on the shallow faces

This risk does not change. The faces at 1 degree to 25 degrees from level show layer steps: 22.3 cm2
on each lower piece, 17.0 cm2 and 16.4 cm2 on the hood sides, and 11.7 cm2 on each deck piece. The
filler primer and the sanding of stage 6 level them. ABS sands more easily than PETG.

## 9. Sources

The sources with their numbers are in `docs/research/abs-on-the-q2.md`, section 8: the printer [Q1]
to [Q12], the material [M1] to [M7], and the weld and the finish [W1] to [W6].

Files of this repository: `docs/design/print-plan.md`, `docs/research/abs-on-the-q2.md`,
`docs/research/abs-switch.md`, `docs/research/petg-finishing.md`, `docs/design/hardware-list.md`,
`cad/candybar/shell/joints.py`, and the build outputs `cad/out/shell-rev7/split/report.md`,
`cad/out/shell-rev7/split/measurements.json` and `cad/out/coupon/README.md` (read in the main checkout).

Not done: no piece was sliced. No print was made. No coupon exists in ABS.
