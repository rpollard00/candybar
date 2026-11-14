# ABS on the Qidi Q2: what changes in the design

Research date: 2026-11-14. Each source was read on this date unless the text gives a different date.
All dimensions are in millimetres unless a unit is given.

The owner decided on 2026-11-14: the material of the shell is ABS, and the printer is a Qidi Q2. Until
this date the design assumed PETG on a Bambu A1. This note tells what the decision changes in the
design. `docs/design/print-plan-abs.md` is the print plan that follows from it.

This note continues `docs/research/abs-switch.md` (the "earlier note", 2026-11-11), which examined the
change before the decision. It does not repeat the budget, the printer survey or the health studies of
that note. It uses them.

Nothing was printed or tested for this note. No product was bought. No CAD was run. The numbers of
the pieces come from the build output `cad/out/shell-rev7/split/` (the report, `measurements.json` and
the piece files).

## Status tags

| Tag | Meaning |
| --- | --- |
| MAKER [id] | From the maker of the part: a specification, a data sheet, a manual, a slicer profile or a product page. The page was read. |
| SOURCED [id] | Written in a source that is not the maker of the part: a health body, or a maker of a different part. The page was read. |
| STUDY [id] | A published test with a stated method. The text says if only the abstract was read. |
| USERS [id] | Reports from users or a review. The count of reports is given. A report is not a measurement. |
| SOURCED (summary) [id] | Read in a search-result summary only. The page was not read. |
| EARLIER [S-number] | A source of `docs/research/abs-switch.md`, read by that note on 2026-11-11. It was not read again. |
| REPORT | A value of a build output of this repository. The file is named. |
| ESTIMATED | Calculated or reasoned here. The method is given. |
| PROVISIONAL | A value proposed here. A test or the owner can change it. |
| NOT CONFIRMED | No source says it, or the sources do not agree. A test must show it. |

The source numbers point to section 8.

---

## 1. Summary

1. **The printer.** The maker gives the print size of the Q2 as 270 x 270 x 256 (width, depth, height).
   The bed is 270 x 270 and the height is 256. The owner wrote 256 x 256 x 270. The numbers are correct,
   but the order is the other way round: the long dimension is the bed, not the height. MAKER [Q1][Q2]
2. **The height does not change.** The A1 is 256 high and the Q2 is 256 high. No piece can become
   taller. The bed is 14 mm longer in X and in Y.
3. **The piece limit.** A limit of 250 x 250 on the bed and 250 high is correct for the Q2 (it was
   240 x 240 x 245). In the model the footprint limit is 248, because the slicer makes the piece
   larger to compensate the shrink. PROVISIONAL
4. **The split stays.** Each of the 32 pieces fits. Two pairs can become one piece each (upper with
   upper rear, right and left), which gives 30 pieces and removes seam R3. The joined piece has 1 of
   spare room on the bed. The recommendation is to keep the 32 pieces until the warp results are known.
5. **The material.** ABS and PETG have about the same stiffness. ABS softens 22 K to 36 K higher. The
   shell is about 1.35 kg lighter. In a slow pull, ABS is stronger across the layers than PETG. In a
   shock, it is weaker across the layers. MAKER [M1][M2][M3]
6. **Shrink.** One study measured printed ABS 0.59 % to 0.69 % short in the bed plane, about the
   same as PETG. A printer maker gives 1 % to 2 %. The slicer has a setting that compensates it. The
   carrier of the monitor has 3.3 on each side, so the compensation is necessary. STUDY [M5]
7. **Warp is the main risk.** The flat pieces are the problem: the nine floor tiles and the two door
   halves. The walls are curved and stand upright, which is the good case. The floor has three
   options (section 5, rule 20).
8. **The seam becomes a weld.** A solvent cement or ABS dissolved in acetone joins ABS to ABS. Maker
   data for sheet ABS give 6.9 MPa after 24 hours. The loads on the seams are less than 0.5 MPa.
   The risk is new: a solvent can crack ABS where it is under stress, at a screw or an insert.
9. **One print setting needs a test.** The ABS profiles of the maker's slicer set the part fan to 80 %
   on an overhang. A face at 45 degrees is such an overhang. The roofs of the hand-holds are faces at
   45 degrees, and they carry the lift. A cold layer bond there is a risk. ESTIMATED from the profile
10. **The filter does not make the room safe.** The Q2 has a filter for particles and a carbon stage.
    The ABS profiles set the exhaust fan to 0 % while the print runs. The maker says that carbon
    gives no sign when it is full. The printer must stand in a room that is not a living room, with
    a vent to the open air.
11. **Design values that change:** the piece limit, the density, the strength values of the
    structure estimate, the pilot hole (2.4 as the first candidate), the bond of the two closing
    seams of each ring, and the material of the floor. The form does not change. Section 6 has the list.

---

## 2. The printer

### 2.1 What the maker says

| Item | Value | Tag |
| --- | --- | --- |
| Print size (W x D x H) | 270 x 270 x 256 mm | MAKER [Q1][Q2][Q4] |
| Printable area in the slicer | X 0 to 270, Y 0 to 270, height 256 | MAKER [Q5] |
| Outer size of the printer | 402 x 438 x 494 mm. The maker asks for more room at the back, the sides and the top. | MAKER [Q1][Q3] |
| Net mass | 18.1 kg | MAKER [Q1] |
| Motion | CoreXY. The bed moves in Z only. | MAKER [Q1][Q2] |
| Chamber heating | A heater with a fan (PTC), "up to 65 °C", 280 W, apart from the bed | MAKER [Q1][Q2] |
| Chamber heating, in the user guide | "Up to 60 °C" | MAKER [Q4]. The guide and the data sheet do not agree. |
| Chamber limit in the slicer | 65 °C | MAKER [Q5] |
| Bed | Aluminium bed with a heater, 120 °C at most. The plate is magnetic, with textured PEI on its two sides. | MAKER [Q1][Q2] |
| Bed, in the wiki | "a maximum temperature of 110 °C" | MAKER [Q6]. The wiki and the data sheet do not agree. |
| Hot end | 370 °C at most. Ceramic heater. | MAKER [Q1][Q2] |
| Nozzle | 0.4 mm, bimetal with a hardened tip. 0.2 mm, 0.6 mm and 0.8 mm are options. | MAKER [Q1] |
| Part cooling | A radial fan (5015) with two ducts at the nozzle, and an auxiliary fan on the right side of the chamber | MAKER [Q6] |
| Filament system | 1.75 mm. A direct extruder with hardened steel gears. A spool holder on the side. A filament cutter. | MAKER [Q1][Q2] |
| Filament box (an option) | The "QIDI Box" holds four spools, heats them to 65 °C and feeds them. The Q2 Combo has one. | MAKER [Q3] |
| Filter | "3-in-1": a G3 pre-filter, an H12 HEPA element and coconut-shell activated carbon | MAKER [Q1][Q2] |
| Firmware | Klipper | MAKER [Q3] |
| Slicer | QIDI Studio. OrcaSlicer and PrusaSlicer also work, but "certain advanced features may not be supported". | MAKER [Q2][Q3] |
| Bed levelling | Automatic. The nozzle is the sensor (a load cell in the hot end). | MAKER [Q1] |
| Price on the maker's page | 449 USD (the page shows 499 USD as the regular price), shipped from China. The US store was not read. | MAKER [Q3] |

The owner decides the purchase. The price is here only because the page showed it on this date.

### 2.2 What the slicer's machine profile says

The maker's slicer is open source. Its profile for the Q2 with the 0.4 mm nozzle gives the limits of
the bed. MAKER [Q5]

| Item | Value | What it means |
| --- | --- | --- |
| `printable_area` | 0x0, 270x0, 270x270, 0x270 | The full plate is printable. |
| `printable_height` | 256 | The full height is printable. |
| `bed_exclude_area` | 0x0, 11x0, 11x16, 0x16 | A corner of 11 mm x 16 mm at X 0, Y 0 is not printable. |
| Start code, first line | From X 108 to X 158 at Y 1 | A purge line on the plate at the front edge |
| Start code, second line | From X 108 to X 158 at Y 2.5 | A second purge line |
| `brim_width` (default of the print profiles) | 5 mm | A brim takes 5 mm on each side of a piece. |
| `elefant_foot_compensation` (profiles of 0.12 mm, 0.16 mm and 0.20 mm) | 0.15 mm | The first layer is made 0.15 mm smaller. The A1 profile has 0.075 mm. |
| `xy_hole_compensation` | 0 | The slicer does not change the holes. |
| `support_threshold_angle` (profile of 0.16 mm) | 25 degrees | If support is on, the slicer makes it only where a face is less than 25 degrees from level. |
| Outer wall and inner wall speed (profile of 0.16 mm) | 200 mm/s and 300 mm/s | The same order as the A1 profile |

### 2.3 The usable volume and the limit for a piece

| Step | X | Y | Z | Tag |
| --- | --- | --- | --- | --- |
| The plate and the height | 270 | 270 | 256 | MAKER [Q1][Q5] |
| Less a brim of 5 mm on each side | 260 | 260 | 256 | ESTIMATED from `brim_width` |
| Less a margin of 5 mm on each side | 250 | 250 | 256 | PROVISIONAL. At the front, the margin holds the two purge lines. At the other edges, the temperature and the hold of the plate are not confirmed. |
| Less 6 mm of height | 250 | 250 | 250 | PROVISIONAL. Room for the lift of the nozzle at the top. |

The proposal for `cad/params/printer.csv`:

| Value | Now (A1) | Proposal (Q2) | Tag |
| --- | --- | --- | --- |
| Bed | 256 | 270 | MAKER [Q1] |
| Height | 256 | 256 | MAKER [Q1] |
| Largest side of a piece on the bed | 240 | 250 | PROVISIONAL |
| Largest side of a piece in the model | 240 | 248 | PROVISIONAL. See the note on shrink. |
| Largest height of a piece | 245 | 250 | PROVISIONAL |

Notes:

- **Shrink.** The slicer scales a piece in X and Y to compensate the shrink of the filament
  (section 3.2). A piece of 248 mm with a compensation of 0.7 % is 249.7 mm on the bed. Thus the limit
  in the model is 248 mm. The slicer makes this change after its checks of the plate. MAKER [Q5]
- **The excluded corner.** A box of 250 x 250 that starts at X 12, Y 12 is clear of the corner and of
  the purge lines. A brim of 5 mm at that place comes to X 7, Y 7, which touches the corner. Most pieces
  have no material in the corner of their box. ESTIMATED
- **Flat pieces.** The bed is not the limit for a flat ABS piece. Warp is (section 3.3). Keep the
  flat pieces as they are (212 x 188 at most) until a tile is printed. PROVISIONAL
- **A test.** A single layer of 250 x 250 with a brim shows the reach and the first layer at the
  edges. The print plan has it.

### 2.4 Which pieces can join

The height of the Q2 is the height of the A1. Thus no two pieces that stand one on the other can
become one piece. The gain is in the footprint only.

Method: the points of the piece files of the split (`cad/out/shell-rev7/split/shell/*.stl`) were put
together for each pair. The box was measured by the rule of `split.print_box`. The rule gave the same
box as the report for each single piece. ESTIMATED: no cut was made, and a joined piece has no flange
inside it.

| Pair | Box of the joined piece | Limit 250 x 250 x 250 | Result |
| --- | --- | --- | --- |
| upper R with upper rear R (and the same on the left) | 247.3 x 231.4 x 142.8 | Fits. With the shrink compensation it is 249.0 on the bed. | **Possible.** 32 pieces become 30. Seam R3 goes (206 mm of seen seam on each side of the back). |
| lower R with middle R | 287.5 x 286.7 x 293.0 | Too tall and too wide | No |
| rear lower R with middle R | 273.6 x 271.8 x 293.0 | Too tall and too wide | No |
| middle R with upper R | 240.8 x 240.1 x 307.8 | Too tall | No |
| lower R with rear lower R | 347.9 x 247.3 x 134.2 | Too long | No |
| deck side R with lower R | 311.7 x 309.9 x 134.2 | Too long | No |
| deck nose with deck side R | 346.0 x 346.0 x 72.0 | Too long | No |
| upper R with the brow | 337.5 x 336.0 x 130.8 | Too long | No |
| upper rear R with upper rear L | 330.0 x 330.0 x 142.8 | Too long | No |
| rear lower R with rear lower L | 456.8 x 456.8 x 115.9 | Too long | No |
| hood centre with hood side R, on the cut face | 148.0 x 138.8 x 341.2 | Too tall | No |
| door half R with door half L | 415.4 x 415.4 x 4.4 | Too long | No |
| bezel half R with bezel half L | 222.9 x 222.6 x 434.7 | Too tall | No |
| The floor as six tiles: a seam on the centre line in place of the two seams at x 106 | 243 x 188 at most | Fits | Possible, not recommended |

The joined upper piece:

- It is the right rear quarter of the head: the side, the rear corner and half of the rear wall, with
  one hand-hold.
- It removes a seam on an open face of the back, 41 mm from the hand-hold.
- It has 1.0 mm of spare room on the bed after the shrink compensation. A brim of 5 mm then ends
  5.5 mm from the edge of the plate.
- It is a larger ABS piece, with a rear wall of about 245 mm. A larger piece warps more.
- Recommendation: keep the 32 pieces for the first build. Examine the joined piece in a later
  re-split, after the warp of "rear lower" (229 x 228) is known on the Q2.

The floor as six tiles:

- Each tile is 243 mm wide. A flat tile of that size is the worst case for warp in ABS.
- The seam on the centre line lies below seams R2, R4 and R5, which are on the centre line of the
  rear. Then one plane cuts the floor and the rear. The seams at x 106 do not do this.
- Recommendation: keep the nine tiles. ESTIMATED

### 2.5 The slicer's ABS profiles for the Q2

QIDI Studio has ABS profiles for the Q2 for these filaments: QIDI ABS Rapido, QIDI ABS Odorless, QIDI
ABS Rapido Metal, QIDI ABS-GF, Generic ABS, Bambu ABS, PolyLite ABS, HATCHBOX ABS and Overture ABS.
MAKER [Q5]

| Setting | Generic ABS | QIDI ABS Rapido | Bambu ABS | PolyLite ABS | QIDI ABS-GF |
| --- | --- | --- | --- | --- | --- |
| Nozzle | 250 °C | 260 °C | 260 °C | 255 °C | 270 °C |
| Nozzle range | 240 °C to 280 °C | 240 °C to 280 °C | 240 °C to 280 °C | 240 °C to 280 °C | 240 °C to 280 °C |
| Bed, textured plate | 90 °C | 90 °C | 90 °C | 90 °C | 100 °C |
| Chamber | Not set: the shared value is 0 (off) | 55 °C | 55 °C | 60 °C | 0 (off) |
| Part fan, lowest to highest | 10 % to 80 % | 20 % to 80 % | 20 % to 80 % | 20 % to 80 % | 20 % to 20 % |
| Part fan on an overhang | 80 %, from 25 % of the line width | 80 %, from 25 % | 80 %, from 25 % | 80 %, from 25 % | 80 %, from 25 % |
| No part fan on the first layers | 3 layers | 3 layers | 3 layers | 3 layers | 3 layers |
| Exhaust fan while the print runs | 0 % | 0 % | 0 % | 0 % | 0 % |
| Largest flow | 17 mm3/s | Not set: the shared value is 24.5 mm3/s | Not set | 17 mm3/s | 12 mm3/s |
| Density | 1.04 g/cm3 | 1.05 g/cm3 | 1.05 g/cm3 | 1.12 g/cm3 | 1.15 g/cm3 |
| Flow ratio | 0.95 | 0.95 | 0.95 | 0.96 | 0.95 |

The maker's user guide gives different values for the same machine. MAKER [Q4]

| Filament | Chamber | Bed | Nozzle | Part fan | Drying | Annealing |
| --- | --- | --- | --- | --- | --- | --- |
| QIDI ABS Rapido | 50 °C | 100 °C | 250 °C to 280 °C | 30 % | 70 °C, 8 h | 80 °C to 90 °C, 6 h to 8 h |
| Generic ABS | 45 °C | 100 °C | 240 °C to 280 °C | 30 % | 70 °C, 8 h | 80 °C to 90 °C, 6 h to 8 h |

The guide also says: "Some other brands of ABS filaments are less heat resistant and it is recommended
to set the chamber temperature no more than 55 degrees Celsius. Otherwise the filaments may be softened
in advance and cause clogging." MAKER [Q4]

What this means:

- The profile "Generic ABS" does not start the chamber heater. Set the chamber temperature by hand, or
  use the profile of the filament that is bought. ESTIMATED from the profile files. Look at the
  value in the slicer before the first print.
- The chamber value to start with is 55 °C. The makers of two filaments give 45 °C to 60 °C for ABS.
  MAKER [M1][Q4]
- The profile and the guide do not agree on the bed (90 °C and 100 °C) and on the part fan. A coupon
  must set them.

### 2.6 What users and one review report

| Report | Tag |
| --- | --- |
| A review of the Q2 (in German, read in translation) says that ABS gains much from the closed chamber. Cracks and warp mostly stayed away in its test. It does not give the size of the test parts. It calls the side spool holder unsteady. It says that the filter reduces the smell of ABS and ASA, but that it is no replacement for an extraction. | USERS [Q10], one review, 2026-01-08 |
| A first large ASA part on a Q2 failed after 10 mm of height. The chamber was at 55 °C and the bed at 90 °C. The brim had a gap of 0.25 mm. | USERS [Q11], one report |
| Replies to that report give a bed of 105 °C to 110 °C and a chamber of 60 °C to 65 °C. They give a heat soak of about 20 minutes and a brim with no gap. One reply waits 1 hour to 2 hours before the door is opened. | USERS [Q11], four reports |
| "65c is a very safe limit for most components" of the printer. | USERS [Q11], one report |
| A long-term review in a user group says that warp is "still reported with the chamber in use". | SOURCED (summary) [Q12]. The page needs a log-in and was not opened. |

ASA is not ABS, but the two behave alike in warp. No report of a large ABS shell on a Q2 was found.

### 2.7 Not confirmed for the printer

- The temperature that the chamber holds with a large ABS piece and the door closed (60 °C or 65 °C).
- The time that the chamber needs to get to 55 °C.
- The largest bed temperature (110 °C or 120 °C).
- The temperature and the hold of the plate in its last 10 mm.
- If the firmware runs the exhaust fan when the profile says 0 %.

---

## 3. ABS against the PETG values of the design

### 3.1 The values

The two first columns are from one maker with the same test methods, so they compare. The third
column is a second ABS. Its samples were printed in a chamber of 90 °C, which the Q2 cannot do.

| Property | Bambu ABS [M1] | Bambu PETG HF [M2] | PolyLite ABS [M3] |
| --- | --- | --- | --- |
| Density | 1.05 g/cm3 | 1.28 g/cm3 | 1.12 g/cm3 |
| Young's modulus, in the layer plane | 2200 ± 190 MPa | 1810 ± 190 MPa | 2247 ± 58 MPa |
| Young's modulus, across the layers | 1960 ± 110 MPa | 1540 ± 130 MPa | 2081 ± 93 MPa |
| Bending modulus, in the layer plane | 1880 ± 110 MPa | 2050 ± 120 MPa | 2127 ± 30 MPa |
| Bending modulus, across the layers | 1590 ± 100 MPa | 1810 ± 140 MPa | Not given |
| Tensile strength, in the layer plane | 41 ± 1 MPa | 34 ± 4 MPa | 33.4 ± 0.6 MPa |
| Tensile strength, across the layers | 32 ± 2 MPa | 23 ± 4 MPa | 29.7 ± 0.3 MPa |
| Across the layers as a part of in the plane | 78 % | 68 % | 89 % |
| Elongation at break, across the layers | 4.7 ± 0.8 % | Not read | 3.1 ± 0.3 % |
| Impact strength, across the layers | 7.4 ± 1.2 kJ/m2 | 10.6 ± 1.2 kJ/m2 | Not given |
| Heat deflection temperature at 1.8 MPa | 84 °C | 62 °C | 98 °C |
| Heat deflection temperature at 0.45 MPa | 87 °C | 69 °C | 100 °C |
| Vicat softening temperature | 94 °C | 69 °C to 70 °C (the PETG note) | 104 °C |
| Glass transition | Not given | Not read | 101 °C |
| Chamber temperature, recommended | 45 °C to 60 °C | 35 °C to 50 °C | "Needed" |
| Part fan, recommended | 0 % to 80 % | 0 % to 60 % | Off |
| Largest overhang angle | About 70 degrees | About 70 degrees | Not given |
| Largest bridge | About 40 mm | About 30 mm | Not given |
| Drying | 80 °C, 8 h | Not read | 70 °C, 6 h |

All values are MAKER. The makers say that the values are for comparison and not for design.

What the table means for the shell:

| Point | Result | Tag |
| --- | --- | --- |
| Stiffness of the 4 mm skin | About equal. ABS is 22 % stiffer in tension and 8 % less stiff in bending. | ESTIMATED from [M1][M2] |
| Strength across the layers, slow load | ABS is higher: 32 MPa against 23 MPa. | MAKER [M1][M2] |
| Strength across the layers, shock | ABS is lower: 7.4 kJ/m2 against 10.6 kJ/m2. A knock or a fall cracks a layer bond more easily. | MAKER [M1][M2] |
| The hand-holds | The estimate of the split report is 7.5 MPa in the wall above the rim (11.0 MPa for a straight lift). This is 23 % (34 %) of 32 MPa. | REPORT and ESTIMATED |
| Mass | The printed shell and the floor are 1.35 kg lighter: 6.43 kg against 7.78 kg. The cabinet is 15.9 kg against 17.25 kg. | ESTIMATED: the masses of the split report times 1.05 / 1.27 |
| Heat | See 3.5. | |

### 3.2 Shrink, and how to compensate it

| Fact | Tag |
| --- | --- |
| One study printed PLA, PETG and ABS parts on one small printer and measured them. ABS was 0.59 % short in X and 0.69 % short in Y. It was 0.92 % long in Z. PETG was 0.76 % short in X, 0.54 % short in Y and 0.73 % short in Z. | STUDY [M5]. The paper was read. The parts were small covers. It is a student paper from a conference. |
| A printer maker gives a shrink of 1 % to 2 % for ABS. | EARLIER [S8] |
| The cause is the same for the two numbers: the plastic gets smaller when it cools from its glass transition (about 100 °C) to the room. A warm chamber makes the stress smaller, not the final size. | MAKER [M4] for the cause. The last sentence is ESTIMATED. |
| The slicer has a filament setting "Shrinkage". "Enter the shrinkage percentage that the filament will get after cooling (94% if you measure 94mm instead of 100mm). The part will be scaled in xy to compensate." | MAKER [Q5], the source code of QIDI Studio |
| The setting scales X and Y only. The slicer does the scaling after its checks of the plate. | MAKER [Q5] |
| The default value of the slicer is 100 % (no compensation). No ABS profile of the Q2 that was read changes it. | MAKER [Q5] |

What an uncompensated shrink does to the large dimensions. ESTIMATED from the two numbers above:

| Dimension | Length | Short at 0.59 % to 0.69 % | Short at 1 % to 2 % |
| --- | --- | --- | --- |
| The largest piece (rear lower) | 229.4 mm | 1.4 mm to 1.6 mm | 2.3 mm to 4.6 mm |
| The door opening | 422.7 mm | 2.5 mm to 2.9 mm | 4.2 mm to 8.5 mm |
| The opening behind the bezel plate | 434.7 mm | 2.6 mm to 3.0 mm | 4.3 mm to 8.7 mm |
| The width of the cabinet | 494.7 mm | 2.9 mm to 3.4 mm | 4.9 mm to 9.9 mm |
| The depth of the floor | 527.6 mm | 3.1 mm to 3.6 mm | 5.3 mm to 10.6 mm |

Two pieces that meet at a seam shrink the same, so the seams fit. A bought part does not shrink. The
tightest place is the carrier of the monitor in the opening behind the bezel plate: 3.3 mm on each
side (the fit report). A shrink of 0.6 % takes 1.3 mm of each 3.3 mm. A shrink of 2 % takes 4.3 mm, which
is more than the room.

How to compensate:

1. Print bars of 200 mm in X and in Y, and a post of 100 mm in Z, in the filament and with the settings
   of the pieces.
2. Measure them at room temperature, one day after the print.
3. Set "Shrinkage" in the filament profile to the measured value. Use one value for each piece.
4. Do not scale a piece by hand also.
5. Measure the door opening and the bezel opening at the dry fit.

The Z value is not compensated by the slicer. The study found that ABS grew in Z. The pieces that
stand one on the other grow the same, so the level seams fit. The height of the door opening (165 mm)
is inside one ring of pieces, and a change of 1 % is 1.7 mm. The dry fit shows it. NOT CONFIRMED

### 3.3 Warp, and what holds it

| Fact | Tag |
| --- | --- |
| There are two causes. The first is the shrink on cooling. The second is the stress that stays in the part, because the glass transition of ABS is far above room temperature. | MAKER [M4] |
| A warm chamber "can effectively reduce internal stress caused by material shrinkage". | MAKER [M4] |
| Glue on the plate and a brim hold the first layer. The maker of one ABS says glue is necessary. | MAKER [M4][M1] |
| "Avoid a fill rate above 50% and wall count greater than 6 layers to reduce shrinkage." More walls and more infill raise the risk of warp. | MAKER [M4] |
| A crack between layers comes when the stress from cooling is more than the layer bond. The causes in the maker's table: too much fan, a cold chamber, too little melt. | MAKER [M4] |
| Where a large base meets a thin wall, a ring shows on the outer wall. The cure is an inner fillet between the two. | MAKER [M4] |
| Many small parts on one plate make a long layer time, and the layer bond is then weaker. Print few parts at one time. | MAKER [M4] |
| A flat part that filled the plate of a different printer warped at a chamber of 65 °C. The advice from users: grooves that break a long flat face, a filled grade, less fan. | EARLIER [S40], one report |
| A different printer with no heater printed ABS with no warp "unless it is a large flat surface with very sharp corners". | EARLIER [S42], one report |
| No source gives a largest size for an ABS part. | NOT CONFIRMED |

What this means for the shell. ESTIMATED:

| Geometry of the shell | Good or bad for warp | Reason |
| --- | --- | --- |
| The wall pieces stand upright and are curved in plan or have a return | Good | The footprint on the bed is a thin curved line with a flange. A curved wall is stiff against a bow. |
| The round of R 3 on the upright rear corners, and the ellipse column | Good | No sharp corner in the footprint at these places |
| The ends of a wall piece at an upright seam | Bad | The footprint ends in a narrow tip with square corners. A tip lifts first. Brim ears go there. |
| The flange of 6 x 12 with its gusset at a level seam | Mixed | It is a thick solid band at the bed or at the top. The gusset of 45 degrees is the gradual change that the maker asks for. |
| The solid skin of 4 mm | Mixed | A solid wall of 4 mm is more than 6 walls of plastic. It is one thin wall, not a block. The tall wall coupon shows if it cracks. |
| The cut-ins | Good | They are shallow grooves that break the flat lower rear corner. |
| The floor tiles (212 x 188 x 10 at most, flat) | Bad | Large and flat. The sandwich with a core of 40 % has less plastic than a solid plate. |
| The door halves (211 x 165 x 4, flat on the bed, with ribs that stand up) | Bad | A thin flat plate. The ribs shrink on one side of it and bend it. |
| The rear lower pieces (229 x 228, a straight rear wall of 235) | The largest risk of the walls | The longest straight wall on the bed |

### 3.4 Layer bond and the direction of the loads

- The wall pieces print upright. A load that bends a wall about a level axis pulls across the layers.
- The data sheets give 32 MPa (Bambu ABS) and 29.7 MPa (PolyLite ABS, printed in a chamber of 90 °C)
  across the layers. The Q2 has a chamber of 55 °C to 65 °C and a part fan. The real value on the Q2 is
  NOT CONFIRMED.
- The maker's page for the Q2 says that the chamber heating increases the layer bond for ABS. It gives
  no number. MAKER [Q3]
- The loads on the seams in the split report are 0.14 MPa to 0.42 MPa in shear. The largest stress is
  at the hand-holds (3.1).
- A shock is the weak case. Do not let a bare piece fall on a hard floor. After the weld and the
  paint, the shell is one body and the flanges are ring frames.

### 3.5 The temperature at which it softens

| Fact | Tag |
| --- | --- |
| The hot air of the BC-250 leaves about 15 K above the intake at 200 W and 40 m3/h. | REPORT (the split report, "Load cases") |
| The shell near the exhaust reaches 40 °C to 50 °C. | The earlier note, section 1 |
| ABS: heat deflection at 84 °C to 98 °C, Vicat at 94 °C to 104 °C | MAKER [M1][M3] |
| PETG HF: heat deflection at 62 °C, Vicat at 69 °C to 70 °C | MAKER [M2] and the PETG note |
| The chamber of the Q2 is hotter (55 °C to 65 °C) than the inside of the cabinet. | MAKER [Q1] |

ABS has 34 K to 48 K of margin at 50 °C (heat deflection at 1.8 MPa). PETG had 12 K. The vents and the
duct do not change. The owner already found PETG satisfactory near the BC-250, so this is more margin
and not a repair.

### 3.6 Overhangs and bridges with little part cooling

| Fact | Tag |
| --- | --- |
| One maker gives "Max Overhang Angle ~ 70°" and "Max Bridging Length ~ 40 mm" for its ABS. It gives the same angle and 30 mm for its PETG. The sheet does not say how the angle is measured. | MAKER [M1][M2] |
| The recommended part fan for ABS is "Off" (one maker), 0 % to 80 % (a second maker), and 30 % (the guide of the Q2). | MAKER [M3][M1][Q4] |
| The ABS profiles of the Q2 set the part fan to 80 % on an overhang. An overhang is where more than 25 % of the width of a line has no layer below it. | MAKER [Q5] |
| On a face at 45 degrees each layer stands out by one layer height. At a layer of 0.16 mm and a line of 0.42 mm this is 38 % of the line. At 0.12 mm it is 29 %. At 0.10 mm it is 24 %. | ESTIMATED |
| Thus the profile cools the facets of 45 degrees with 80 % fan at a layer of 0.12 mm or 0.16 mm. | ESTIMATED |
| Too much fan is a cause of cracks between layers in ABS. | MAKER [M4] |
| The angle at which ABS prints clean with no support on the Q2 | NOT CONFIRMED. No source with a measurement was found. |

The design has 489.6 cm2 of seen face at 45 degrees with no support. 149.7 cm2 is on each upper rear
piece: the rear facet of the rear shelf and the roof of the hand-hold. The roof carries the lift. Two
things pull in opposite directions there. More fan gives a cleaner face. Less fan gives a stronger
layer bond. Only the facet coupon settles this (section 7).

The bridge over the groove of joint 1 is 4.2 mm to 4.6 mm. This is far less than 40 mm.

### 3.7 Holes and heat-set inserts

| Fact | Tag |
| --- | --- |
| The makers' hole for an M4 insert (8.1 mm long, 6.3 mm outside) is 5.6 mm, straight, with no taper. | `docs/design/hardware-list.md` 2.1 |
| "Holes in 3D printed parts usually come out smaller than in CAD". The maker of the inserts has a test part to find the hole. | SOURCED [M7] |
| In that maker's test, in PLA, the holes were about 0.25 mm small. | `docs/design/hardware-list.md` 2.1 |
| The shrink of ABS changes a hole of 5.6 mm by 0.03 mm to 0.04 mm. This is small against 0.25 mm. | ESTIMATED from 3.2 |
| The slicer of the Q2 does not change the holes (`xy_hole_compensation` 0). | MAKER [Q5] |
| The temperature of the iron for ABS is "265 °C" (245 °C for PETG). | SOURCED [M7] |
| A blind hole is about 1 mm deeper than the insert. | SOURCED [M7] |
| No maker's table and no test for the hold of an insert in printed ABS was found. | NOT CONFIRMED |
| A thread-forming screw of 3.0 mm in ABS: pilot hole 2.4 mm (0.8 of the diameter). ABS is in the table of the screw maker. PETG was not. | `cad/candybar/shell/joints.py` |

ABS adds one risk: a solvent on plastic that is under stress. A boss with an insert and a hole with a
thread-forming screw are such places (section 4.3).

### 3.8 Thermal expansion in use

| Fact | Tag |
| --- | --- |
| ABS sheet: 90 x 10^-6 per K (23 °C to 60 °C), and 5.3 to 5.6 x 10^-5 per °F, which is 95 to 101 x 10^-6 per K | SOURCED (summary) [M6], three data sheets |
| PETG sheet: 68 x 10^-6 per K | The PETG note, 2.0 |
| The width of 494.7 mm grows 0.94 mm in ABS for 20 K. In PETG it grows 0.67 mm. | ESTIMATED |
| An aluminium panel of 396 mm in an ABS deck: 0.29 mm of difference for 10 K. The gap round the panel is 1.0 mm. | ESTIMATED |

No design value changes. The expansion of printed ABS was not found.

---

## 4. Bonding and finishing in ABS

The earlier note has the comparison with the PETG system (its section 2). This section adds the values
that the plan needs.

### 4.1 Solvent welding

A solvent softens the two faces. They flow into each other, and the solvent leaves. The joint is
then ABS.

| Product class | What the source says | Tag |
| --- | --- | --- |
| Acetone alone | It evaporates fast. Users find it hard to get a good bond with it alone. | EARLIER [S23], three reports |
| ABS dissolved in acetone, thin ("glue") | 8 g of ABS in 50 ml of acetone. It stays wet longer and fills small gaps. | EARLIER [S24] |
| ABS dissolved in acetone, as an adhesive on printed ABS | Lap joints of printed ABS: 10 g of ABS in 50 ml of acetone gave the highest strength, 14.7 MPa. Cyanoacrylate gave 8.4 MPa. | STUDY [W4], abstract only |
| Acetone on printed ABS | The strength of the joints was "reasonably good and quite comparable when compared with single piece specimen". | STUDY [W3], abstract only |
| A thin cement with MEK (example: Weld-On 2354) | For ABS, styrene, acrylic and polycarbonate, each to itself. "Water thin". It is put on the edge of the closed joint and goes in by itself. Working time 3 minutes. | MAKER [W1], read on a seller's page |
| The same, strength on ABS sheet | 500 psi (3.4 MPa) after 2 hours, 1,000 psi (6.9 MPa) after 24 hours, 1,230 psi (8.5 MPa) after 1 week. The strength increases for some weeks. | MAKER [W1] |
| A thick cement with MEK (example: Weld-On 4707) | "ABS material to itself only". 4,000 cps. Working time 10 minutes. 400 psi (2.8 MPa) after 2 hours, 1,000 psi (6.9 MPa) after 24 hours, 1,100 psi (7.6 MPa) after 1 week. | MAKER [W2], read on a seller's page |
| A methacrylate adhesive (example: Plexus MA310) | Not a solvent weld. Its maker lists ABS. It fills gaps of 0.25 mm to 3.2 mm. Working time 15 minutes to 18 minutes. | `docs/research/petg-finishing.md` 1.1 |

The two pages also give a "fixture time" of 5 minutes and of 10 minutes to 15 minutes, as the time
to 80 % of the final strength. Their own tables show 41 % and 36 % of the strength of one week after
2 hours. Plan with the tables. The thin cement gets its final strength in 72 hours, and the thick one
gets "high strength in 24 to 72 hours". MAKER [W1][W2]

The thin cement "should not be used for joining dissimilar materials". Thus a solvent does not join
ABS to PETG. MAKER [W1]

**The design of a joint for a weld.**

| Rule | Source | Joint 1 as designed |
| --- | --- | --- |
| "Parts to be joined should fit without forcing." | MAKER [W1][W2] | The key locates. The groove is 0.5 mm deeper than the key, so the flange faces touch. Correct. |
| The faces are clean and smooth. A sanding with P200 to P400 is satisfactory. | MAKER [W1][W2] | One face is a top layer. The other face is the first layer on the textured plate. Scuff the two with P240. |
| A thin solvent fills no gap. The faces must touch. | EARLIER [S23] | Correct where the screws pull the faces together, every 60 mm |
| A thick cement or dissolved ABS fills a small gap. The largest gap is not known. | NOT CONFIRMED | The two closing seams of each ring have a gap of 0.5 mm on each side (`OtherJoints.closing_gap`). A thin solvent does not bond them. |
| A solvent cracks plastic that is under stress. | EARLIER [S29][S31][S33] | Each seam has a screw in a pilot hole every 60 mm. See 4.3. |
| The area of the weld | - | 7 mm for each mm of seam beside the groove, and the 4 mm of the skin edge (the split report) |

The weld is strong enough by a large margin: 6.9 MPa after one day against 0.14 MPa to 0.42 MPa of
load. The questions are the gap, the cracks at the screws, and the seam under the paint.

**Cure times for the plan.** PROVISIONAL, from the maker's table and from the earlier note:

| Step | Wait |
| --- | --- |
| The screws clamp the seam | At once. They stay in. |
| Before the next batch of seams | 2 hours |
| Before a load on the seam or a lift of the cabinet | 24 hours |
| Before the filler goes into the groove | 72 hours |
| Before the last block sanding of a filled groove | 7 days after the last filler with solvent in it |

### 4.2 Dissolved ABS as a filler

| Fact | Tag |
| --- | --- |
| A thick mix ("slurry") is about 20 g of ABS in 50 ml of acetone. It dries to ABS. | EARLIER [S24] |
| It shrinks and cracks when it is put on thick. Put it on in thin layers. | EARLIER [S25], one source |
| Solvent that stays in a seam leaves in the days after. The seam then sinks and shows. Model builders wait 24 hours or more. | EARLIER [S25c], one source |
| No test of a filled ABS seam under paint over some weeks was found. | NOT CONFIRMED |

The V-groove of joint 1 is 1.0 mm wide and 0.8 mm deep. It is small, which is correct for a filler
that shrinks. Fill it in two or three thin layers. For a dent or a support mark that is wider than
the groove, a two-part polyester putty that lists ABS has no solvent that must leave (EARLIER
[S26][S27]). Make the slurry from the filament of the shell. The coupon compares the two.

### 4.3 Putty, primer, paint and sanding

The earlier note has the sources (its sections 2.3 and 2.4). In short:

| Step | For ABS | Tag |
| --- | --- | --- |
| Sanding | ABS sands "wet or dry". It does not gum as PETG does. | EARLIER [S8] |
| Putty | Two-part polyester putties for plastic car parts list ABS by name. The common body filler does not list a thermoplastic. | EARLIER [S26][S27] |
| Primer | One-part plastic primers list ABS. One maker has a promoter for "solvent sensitive plastics, such as PC, ABS". | EARLIER [S28][S29][S30] |
| Colour | A hobby lacquer grips ABS, because it dissolves the surface a little. | EARLIER [S31] |
| The risk | Thin ABS is "easily damaged by solvent". Lacquer and enamel thinners crack ABS parts at press fits. Parts with no stress stayed good in one test. | EARLIER [S31][S33], more than five reports |
| The maker of the reference cabinet | He prints in ABS, and he fills large prints with body filler. | EARLIER [S70][S72] |

The rules that follow for the shell. ESTIMATED:

1. Prime each face before a lacquer or a thinner touches it. Put the primer on in light coats.
2. Keep liquid solvent away from the bosses of the inserts and from the screw holes. Put the weld on
   the flange faces between the screws. Do not flood the joint.
3. Do not wipe the shell with acetone. Clean it with isopropyl alcohol.
4. Do not sand an edge break with a machine. ABS sands fast, and the break of R 1 is small.

### 4.4 Vapour smoothing

| Fact | Tag |
| --- | --- |
| Acetone vapour makes the surface of printed ABS smooth. | EARLIER [S8] |
| With a long exposure (90 minutes in one study, 80 minutes in a second) "the sharp edges and corners are rounded off". | SOURCED (summary) [W5], two abstracts |
| One user had cracks across a part the day after the smoothing. | EARLIER [S34], one report |

It is of no use on this shell. The design has edges that must stay crisp: the breaks of R 1, the lips
of the cut-ins, the mitres of the facets and the creases. The shell gets filler primer on each face in
any case. The vapour puts solvent into a skin that has screws and inserts in it. A shell of
495 x 571 x 555 mm also needs a very large vessel of acetone vapour, which is a fire risk. Do not use
it. ESTIMATED

### 4.5 Safety

**While the printer runs.**

| Fact | Tag |
| --- | --- |
| ABS gives off about 100 times more ultrafine particles than PETG, and more than 10 times the VOC, mostly styrene. | EARLIER [S11][S12] |
| Styrene is "probably carcinogenic to humans" (IARC group 2A). | EARLIER [S14] |
| "At printing temperatures, ABS, ASA filaments release harmful gases such as styrene, which can be toxic and may cause dizziness or nausea." "Avoid prolonged printing in living areas such as bedrooms or living rooms." For a long job, wear a mask with a vapour filter. If a person with asthma, a pregnant woman or a child is there, increase the ventilation or stop. | MAKER [M4] |
| Control at the source: an enclosure with a vent to the open air. Three air changes in one hour were not sufficient in a room. | EARLIER [S15][S16] |

**What the filter of the Q2 does.**

| Fact | Tag |
| --- | --- |
| It has three stages: a G3 pre-filter, an H12 HEPA element and activated carbon. | MAKER [Q1][Q2] |
| The product page says: "Efficient Absorption of 99.5% Particulate". | MAKER [Q3] |
| It "filters air inside the chamber and vents it outside when the chamber circulation fan is running". | MAKER [Q7] |
| Service life: "approximately 1440 hours". | MAKER [Q7] |
| A new cartridge is listed at 9.99 USD. | MAKER [Q3][Q8] |

**What it does not do.**

| Fact | Tag |
| --- | --- |
| "A HEPA element alone will not touch VOCs." The carbon stage takes the VOC. | MAKER [Q8] |
| "When the available surface saturates, the filter stops working", and "it gives you no warning signal". "Saturated carbon can release what it holds." | MAKER [Q8] |
| The maker's blog gives a change of the carbon "roughly every 200–300 hours" for high-temperature materials. The wiki gives 1440 hours. | MAKER [Q8][Q7]. The two do not agree. |
| What many makers call "H12" is class E12 in the present standard: 99.5 % or more at the worst particle size. | MAKER [Q8] |
| The ABS profiles of the Q2 set the exhaust fan to 0 % while the print runs. Then no air goes through the filter. | MAKER [Q5] for the value. The result on the machine is NOT CONFIRMED. |
| With chamber heating, "the air filtration of ABS and ASA will get worse". | MAKER [Q5], the help text of the chamber setting |
| "Direct exhaust is the strongest control because it removes contaminants from the building." A filter that returns the air removes nothing from the room. | MAKER [Q8] |
| The mass of carbon in the cartridge, and the part of the styrene that it takes | NOT CONFIRMED |
| How much air leaks from the closed chamber | NOT CONFIRMED |

What to do. ESTIMATED from the sources above:

1. Put the printer in a room that is not a living room or a bedroom.
2. Vent that room to the open air with a window fan or a duct while the printer runs and while it cools.
3. Let the chamber cool with the door closed before a piece comes out. This is also good for the piece.
4. Change the cartridge every 200 hours to 300 hours of ABS. The plan has about 540 hours of printing.
5. Do not count on the filter alone. The profile keeps the exhaust fan off while the print runs. If
   the fan is set to run, the filter works during the print, but the chamber loses heat.

**While the seams are welded.**

| Fact | Tag |
| --- | --- |
| Acetone: flash point 0 °F (-18 °C). The vapour burns from 2.5 % in air. Limits for the air at work: 250 ppm (NIOSH), 1000 ppm (OSHA). It irritates the eyes, the nose and the throat, and it causes headache and dizziness. | SOURCED [W6] |
| The MEK cements: "FLAMMABLE. VAPOR HARMFUL." Keep them away from heat, sparks and flames. Use them with ventilation. Wear gloves and goggles. | MAKER [W1][W2] |
| Some cements for plastics contain methylene chloride. | `docs/research/petg-finishing.md`, section 6 |

Weld with a window open or outdoors, with no flame, no heater and no spark near it. Do not weld
inside the closed shell with the head near the opening: the vapour collects in it. Wear gloves that
resist ketones, and goggles. Choose a cement with no methylene chloride. Keep the mixes in closed
glass or metal, with a label.

---

## 5. What it means for the design rules

"Holds" means that the value stays. "How sure" is the confidence in that answer.

| # | Rule of the design | Value now | For ABS on the Q2 | What changes | How sure | A test settles it |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | The skin | 4 mm (`Blueprint.wall_t`) | Holds | No change. How it is printed is open: solid, or three wall loops on each side with a core. Three loops are 1.3 mm of solid wall, more than the V-groove of 0.8 mm. | High for strength and stiffness (data sheets). Medium for the print. | Tall wall coupon |
| 2 | The limit for a piece | 240 x 240 x 245 | Changes | 250 x 250 x 250 on the bed. 248 for the footprint in the model. | High for the bed (maker). Medium for the margins. | Single layer of 250 x 250 |
| 3 | The split | 32 pieces | Holds | No new split is necessary. Two pairs can join later (30 pieces). | Medium: the boxes are estimates. | The warp of the largest wall piece |
| 4 | The flat pieces | 212 x 188 at most | Holds as a limit | Do not make a flat piece larger than now. | Medium | First floor tile |
| 5 | Joint 1: the flange and the gusset | 6 x 12, gusset of 45 degrees | Holds | No change. Look for a mark on the outer face at the flange and for a crack at the gusset. | Medium | Joint coupon, tall wall coupon |
| 6 | The key clearance | 0.2 on each side, 0.1 to 0.3 on the coupon | Open, as before | No change to the start value. Print the three pairs in ABS. The first-layer compensation of the Q2 profile is 0.15 mm, twice that of the A1. | Low | **Only the joint coupon** |
| 7 | The groove: 0.5 deeper than the key, chamfer of 0.3 | As given | Holds | No change. It makes the flange faces touch, which a weld needs. | Medium | Joint coupon |
| 8 | The pilot hole of the 3.0 mm screw | Open: 2.25 or 2.4 | Changes | 2.4 is the first candidate. It is the screw maker's value for ABS. | Medium | Repeated-drive test in ABS |
| 9 | The screws stay in a bonded seam | Yes | Holds, with a new risk | Solvent and a stressed hole can give a crack. Keep the weld between the screws. Examine the coupon after two weeks. | Low | **Only the weld coupon** |
| 10 | The V-groove | 1.0 wide, 0.8 deep | Holds | No change. A small groove is correct for a filler that shrinks. | Medium | Weld coupon |
| 11 | The closing gap | 0.5 on each side, at two seams of each ring | Holds, the bond changes | A thin solvent does not fill 0.5 mm. Bond these seams with dissolved ABS, a thick cement or the methacrylate adhesive. | Medium | A coupon pair with a shim of 0.5 mm |
| 12 | The hole for the M4 insert | 5.6 | Open, as before | No change to the value. The shrink of ABS changes it by 0.04 mm. The coupon has 5.6, 5.7 and 5.8. Iron at 265 °C. | Medium | **Only the insert coupon** |
| 13 | The depth of the insert hole | "8 deep" in the blueprint | Changes, not because of ABS | 9.5 mm. The hardware list found this. | High | - |
| 14 | The boss of a service seam | 12 (`service_boss`) | Changes, not because of ABS | 13 mm. The hardware list found this. In ABS a boss that is too thin cracks more easily. | Medium | Insert coupon |
| 15 | The pins of a service seam | 4, with 0.1 of clearance | Holds | No change. | Medium | Hole coupon |
| 16 | The edge break and the round | R 1 and R 3 | Holds | No change. No vapour smoothing. Sand the breaks by hand. | High | - |
| 17 | The facets of 45 degrees with no support | 489.6 cm2 of seen face | Open | The form does not change. The fan on these faces and the layer height are open. The roofs of the hand-holds carry the lift. | Low | **Only the facet coupon** |
| 18 | The cut-ins | 1.5 deep, 10 high, lips at 33 degrees | Holds | No change. A shallow groove is good against warp. | Medium | Tall wall coupon (it has a cut-in) |
| 19 | The land beside the rear door | 4 (`door_land`) | Holds | No change. The pieces on its two sides shrink the same. | Medium to high | Dry fit |
| 20 | The floor | A sandwich of 10 mm in nine tiles, "printed PETG" | Open | Three options: (a) ABS on the Q2, (b) ABS with glass fibre on the Q2, (c) PETG on the A1. See the text below. | Low | **Only the first tile** |
| 21 | The door halves | 211 x 165 x 4, the outer face on the bed | At risk | A thin flat plate in ABS. If it warps: thicker edges, ribs that are low and many, or the plate on its long edge. | Low | The first door half |
| 22 | The ribs of the walls | 8 high, 3 thick, 110 apart at most | Holds, with a rule | Make a rib upright in the print where the form lets you. Give each rib root an inner fillet. A level rib needs its gusset. | Medium (the maker's rule) | Tall wall coupon |
| 23 | The room for the monitor | 7.3 on each side, 3.3 for the carrier | Holds only with the shrink compensation | No change to the value. Measure the shrink, set it in the slicer, and measure the opening at the dry fit. | Medium | The bars, then the dry fit |
| 24 | The door opening | 422.7 x 165 | Holds with the shrink compensation | No change. The door shrinks as the opening does. | Medium to high | Dry fit |
| 25 | The gap round the control panel | 1.0 | Holds | No change. 0.29 mm of difference for 10 K. | High | - |
| 26 | The mass and the lift load | 17.25 kg, 116 N in each hand-hold | Changes | 15.9 kg, and about 107 N. | High | - |
| 27 | The values of the structure estimate | E 2000 MPa, 50 MPa short, 5 MPa long | Changes | E 2200 MPa in the layer plane and 1960 MPa across it. Strength 41 MPa in the plane and 32 MPa across it. | Medium: data sheets, not this printer | - |
| 28 | The parts near the hot air | PETG is satisfactory | Better | No change to the vents. | High | Warm coupon, for the paint |

**The floor (rule 20).** The owner settled on 2026-11-11 that the floor is a printed PETG part. The
material is now ABS, and a large flat tile is the worst case for ABS.

| Option | For | Against |
| --- | --- | --- |
| (a) ABS on the Q2 | One material. The tiles weld to each other and to the wall feet. | The risk of warp. A tile that is not flat makes the datum of the cabinet wrong. |
| (b) ABS with glass fibre on the Q2 | A maker of such a filament says that it warps less (EARLIER [S47]). The floor is not seen. The Q2 has a hardened nozzle, which the fibre needs. | A second filament. Its weld to plain ABS was not examined. |
| (c) PETG on the A1 | The owner's first decision. No warp problem. The A1 prints the floor while the Q2 prints the walls. | Two materials. No solvent weld between PETG and ABS: the wall feet get screws and the methacrylate adhesive. The expansion differs by 0.21 mm on 527.6 mm for 15 K. |

Recommendation: print the first tile (front centre, 212 x 188 x 10) in ABS on the Q2. If each corner
lies within 0.5 mm of a flat table, use option (a). If not, use option (c), because the A1 and the
PETG values exist. The limit of 0.5 mm is PROVISIONAL. The owner decides.

---

## 6. The values to change

Nothing was changed for this note. This is the list for the person who changes the code and the
shared documents.

### 6.1 Code and parameter sheets

| File | Now | Change to | How sure |
| --- | --- | --- | --- |
| `cad/params/printer.csv` | `a1_bed` 256, `a1_part_max_xy` 240, `a1_part_max_z` 245 | Rows for the Q2: bed 270 (sourced), height 256 (sourced), largest side 248 (provisional), largest height 250 (provisional). Keep the A1 rows if the A1 prints inside parts. | High for the bed and the height. Medium for the two limits. |
| `cad/candybar/shell/split.py`, `printer()` | Reads `a1_part_max_xy`, `a1_part_max_z`, `a1_bed` | Read the rows of the Q2 | - |
| `cad/candybar/check.py` line 156, `cad/candybar/shell/fit.py` line 669, `cad/candybar/shell/coupon.py` line 58 | Read the `a1_` rows | Read the rows of the Q2 | - |
| `cad/candybar/shell/split.py`, `PETG_G_PER_CM3` | 1.27 | 1.05 for ABS (1.12 if the owner buys PolyLite ABS). A new name. | High. The value depends on the filament. |
| `cad/candybar/shell/joints.py`, `Joint.pilot_d` | Open (`None`) | `pilot_d_abs` (2.4) as the first candidate. The repeated-drive test in ABS confirms it. | Medium |
| `cad/candybar/shell/joints.py`, `OtherJoints.service_boss` | 12.0 | 13.0 | Medium |
| `cad/candybar/shell/joints.py`, `OtherJoints` | `insert_l` 8.0, no depth of the hole | Add the depth of the hole: 9.5 | High |
| `cad/candybar/shell/joints.py`, `OtherJoints.closing_gap` | 0.5 | The value stays. Add to its comment that the seam needs a bond that fills a gap. | Medium |
| `cad/candybar/shell/joints.py`, `Joint.groove_clearance` | 0.2 | The value stays until the ABS coupon. | Low |
| `cad/candybar/shell/structure.py`, `E_PETG`, `YIELD_MPA`, `CREEP_MPA` | 2000, 50, 5 | 2200 in the layer plane, and a strength of 41 in the plane and 32 across the layers. No value for a long load was found: keep one tenth of the strength (3 to 4). | Medium |
| `cad/candybar/shell/structure.py`, texts | "printed PETG sandwich", "no limit on PETG near it" | The material that the owner chooses for the floor. ABS for the shell. | - |
| `cad/tools/split_report.py` lines 171 and 257 | "Printed PETG holds about ...", "No strength for printed PETG is claimed." | ABS, with the values above | - |
| `cad/candybar/shell/coupon.py`, the README text | "PETG (the plan)", "ABS (an option)", ABS on the open A1 | ABS on the Q2 is the plan. The rules for ABS on the A1 go. The count of pairs and plaques is in the print plan. | - |
| `cad/tools/draw_structure.py` line 456 | "PETG and ABS use the same values" | ABS | - |

### 6.2 Documents

| Document | Line | Change |
| --- | --- | --- |
| `docs/roadmap.md` | Line 5: "printed on the Bambu A1" | The Qidi Q2, in ABS |
| `docs/roadmap.md` | Phase 4: "for the 256 mm bed" | For the bed of 270 x 270 mm and the height of 256 mm of the Q2 |
| `docs/roadmap.md` | Phase 5: "Each part sliced for the A1" | Sliced for the Q2 in ABS |
| `docs/roadmap.md` | Step 9, "Split": "the limit is 240 x 240 x 245" | The new limit, when the split is cut again |
| `docs/roadmap.md` | Step 9, "Structure": "17.2 kg", "about 50 MPa for a short load on PETG" | 15.9 kg, and the ABS values |
| `docs/roadmap.md` | "Settled by the owner": "The owner still considers ABS on an enclosed printer ... until the coupons decide" | Decided on 2026-11-14: ABS, on a Qidi Q2 |
| `docs/roadmap.md` | "Settled by the owner": "The floor is a rigid printed PETG part" | Open again. See section 5, rule 20. |
| `docs/roadmap.md` | "Settled by the owner": "PETG is satisfactory near the BC-250" | No longer applicable. ABS has more margin. |
| `docs/roadmap.md` | "Settled by the owner": "A printed PETG plate comes first" (the control panel) | The owner's choice: ABS on the Q2, or PETG on the A1 |
| `docs/roadmap.md` | "Open decisions" | New rows: the floor material, the ABS filament, the place and the vent of the printer |
| `docs/roadmap.md` | "Where things are", the row of `docs/research/` | Add this note. Remove "the plan stays PETG until the owner decides". Add `docs/design/print-plan-abs.md`. |
| `docs/adr/0006-...` | "The material is open: PETG on the A1, or ABS on an enclosed printer. The split and the joints must work for both." | The material is ABS and the printer is a Qidi Q2 (2026-11-14). A new decision record is cleaner than a change to 0006: "The shell is ABS, printed on a Qidi Q2, and the seams are welded." Record 0006 then gets one line that points to it. |
| `docs/adr/0006-...` | "A coupon proves the joint, its clearance and the adhesive" | "the adhesive" becomes "the weld" |
| `docs/blueprint/index.md` | Line 401: "The material is open ..." | ABS on the Q2 |
| `docs/blueprint/index.md` | Line 419: "the usable volume of the A1 (240 x 240 x 245)" | The limit of the Q2 |
| `docs/blueprint/index.md` | Joint 1: "The pilot hole is open: 2.25 (the value for PET) or 2.4 (the value for ABS)" | 2.4 first |
| `docs/blueprint/index.md` | Joint 5: "(hole 5.6, 8 deep)" | Hole 5.6, 9.5 deep, boss 13 |
| `docs/design/print-plan.md` | The whole plan | Replaced by `docs/design/print-plan-abs.md` for the shell. That plan says what stays true. |
| `docs/design/hardware-list.md` | 1.8 "Adhesive, filler, primer, paint", 1.11 "Filament", 2.1 "in printed PETG", 2.2 | ABS: the weld products, the ABS filament, the iron at 265 °C, the pilot of 2.4 |
| `docs/research/petg-finishing.md`, `docs/research/abs-switch.md` | - | No change. They are the record of the PETG plan and of the study. |
| `CONTEXT.md` | - | No change. No word of the glossary names a material. |

---

## 7. What only a coupon can settle

| Question | Why no source answers it | The coupon |
| --- | --- | --- |
| The key clearance of joint 1 in ABS | It depends on this printer, this filament and the first layer on this plate. | The joint coupon, three pairs |
| The pilot hole, and a crack at a screw after a weld | No test of a thread-forming screw in a welded printed flange was found. | The repeated-drive test, and the weld coupon after two weeks |
| The weld product, and a gap of 0.5 mm | The studies used flat lap joints. No source gives the largest gap. | The weld coupon, with one pair on a shim |
| The seam under paint after some weeks | No published test | The weld coupon: the seam look at one week and at two weeks |
| The hole for the insert, and a crack at a boss under primer and lacquer | The makers' tests were in PLA. | The insert coupon |
| The face at 45 degrees: the surface against the layer bond | No measurement of ABS overhangs on the Q2 was found. | The facet coupon, at two fan values, with a load on the roof |
| The solid skin against a skin with a core | The maker's rule is for blocks, not for one wall of 4 mm. | The tall wall coupon, in the two ways |
| The warp of a flat tile | No source gives a size limit. | The first floor tile |
| The shrink of this filament on this printer | Published values go from 0.6 % to 2 %. | The bars |
| The chamber temperature that this filament takes with no clog | The guide warns for other brands. | The first long print |

`docs/design/print-plan-abs.md` has the coupons with what each one must prove.

---

## 8. Sources

### The printer

| No. | Source | What it is |
| --- | --- | --- |
| Q1 | https://qidi3d.com/pages/qidi-q2-techspecs | The maker's specification page of the Q2 |
| Q2 | https://cdn.shopify.com/s/files/1/0587/5282/7532/files/QIDI-Q2-TDS.pdf?v=1755582794 | The maker's technical data sheet of the Q2 (PDF, linked from Q1) |
| Q3 | https://qidi3d.com/products/qidi-q2 | The maker's product page: features, the answers on the slicer and the firmware, the prices as shown |
| Q4 | https://gzhls.at/blob/ldb/4/6/7/5/ca179b8075825cea3d83a4cc055473b7f22c.pdf | The user guide of the Q2 ("Please read this guide carefully before using this product"): the filament tables, the tips, the specification. This is a copy on a price-comparison site. The maker's own copy was not found. |
| Q5 | https://github.com/QIDITECH/QIDIStudio (commit 21d4745791 of 2026-11-05) | The maker's slicer. Files in `resources/profiles/Q Series/`: `machine/Qidi Q2 0.4 nozzle.json`, `machine/fdm_q_common.json`, `filament/Generic ABS @Q2.json`, `filament/QIDI ABS Rapido @Q2.json`, `filament/QIDI ABS Odorless @Q2.json`, `filament/Bambu ABS @Q2.json`, `filament/PolyLite ABS @Q2.json`, `filament/QIDI ABS-GF @Q2.json`, `filament/fdm_filament_common.json`, `process/0.12mm Fine @Q2.json`, `process/0.16mm Optimal @Q2.json`, `process/0.20mm Standard @Q2.json`, `process/fdm_process_common.json`. The help texts are in `src/libslic3r/PrintConfig.cpp`. |
| Q6 | https://wiki.qidi3d.com/en/Q2/intro-Q2 | The maker's wiki, introduction of the Q2: the hot bed, the cooling system |
| Q7 | https://wiki.qidi3d.com/en/Q2/Activated-Carbon-Air-Filter | The maker's wiki: the filter, its place and its service life |
| Q8 | https://qidi3d.com/blogs/news/safe-home-3d-printing-air-filtration | The maker's article on filters and ventilation (2025-09-24) |
| Q9 | https://qidi3d.com/blogs/news/temperature-controlled-chamber | The maker's article on chamber temperature. It gives no number for ABS. |
| Q10 | https://www.smartzone.de/qidi-q2-test/ | A review of the Q2 in German (2026-01-08) |
| Q11 | https://www.reddit.com/r/QIDI/comments/1tf1t05/qidi_q2_asa_chamber_temperature_vs_printer/ | A user thread: a failed large ASA part on a Q2, and five replies (2026-05-14) |
| Q12 | https://www.facebook.com/groups/qidi.functional/posts/2408491066241816/ | A user review after 2200 hours. Search summary only. |

### The material

| No. | Source | What it is |
| --- | --- | --- |
| M1 | https://cdn.shopify.com/s/files/1/0584/7236/6216/files/Bambu_ABS_Technical_Data_Sheet.pdf | Bambu ABS, technical data sheet V2.0. The maker's wiki links a V3, which was not read. |
| M2 | https://store.bblcdn.com/3a230e260a3a47c2b0db0156e07eef91.pdf | Bambu PETG HF, technical data sheet |
| M3 | https://wiki.polymaker.com/polymaker-products/more-about-our-products/documents/technical-data-sheets/abs-asa/polylite-tm-abs | Polymaker PolyLite ABS, technical data sheet, as the maker's wiki shows it |
| M4 | https://wiki.bambulab.com/en/filament/abs_asa_pc | A filament maker's guide for ABS, ASA and PC: warp, cracks, chamber, health (last edit 2026-07-26) |
| M5 | https://ieworldconference.org/content/WP2021/Papers/GDRKMCC_21_35.pdf | Weiser and others, "Shrinkage Compensation for FFF Printing for PLA, ABS, and PETG Thermoplastics", Binghamton University, a conference of 2021-04-29. Printer: QIDI X-One2. |
| M6 | https://plastim.co.uk/wp-content/uploads/2019/07/ABS-Technical-Data-Sheet.pdf, https://www.curbellplastics.com/wp-content/uploads/2022/11/Curbell-Plastics-ABS-Data-Sheet.pdf, https://laminatedplastics.com/abs.pdf | Three data sheets of ABS sheet: the thermal expansion. Search summaries only. |
| M7 | https://www.cnckitchen.com/blog/tips-and-tricks-for-heat-set-inserts | A maker of inserts for printed parts: the iron temperature for each material, the depth and the shape of the hole (2021-10-01) |

### The weld and the finish

| No. | Source | What it is |
| --- | --- | --- |
| W1 | https://plastic-craft.com/product/scigrip-ips-weld-on-2354/ | A seller's page with the maker's data for a thin MEK cement for ABS |
| W2 | https://plastic-craft.com/product/scigrip-ips-weld-on-4707/ | A seller's page with the maker's data for a thick MEK cement for ABS |
| W3 | https://www.sciencedirect.com/science/article/abs/pii/S1755581720300857 | Saraf and others, 2020: joints of printed ABS with acetone. Abstract, in a search summary. |
| W4 | https://www.sciencedirect.com/science/article/abs/pii/S0143749625002933 | A paper of 2025: adhesives and dissolved ABS on printed ABS lap joints. Abstract, in a search summary. |
| W5 | https://www.sciencedirect.com/science/article/abs/pii/S135983681730152X, https://www.sciencedirect.com/science/article/abs/pii/S2214785320331758 | Two papers on vapour smoothing and dimensions. Abstracts, in search summaries. |
| W6 | https://www.cdc.gov/niosh/npg/npgd0004.html | NIOSH pocket guide: acetone |

### Files of this repository

`docs/research/abs-switch.md` (its sources S8, S11, S12, S14, S15, S16, S23, S24, S25, S25c, S26 to S31,
S33, S34, S40, S42, S47, S70 and S72), `docs/research/petg-finishing.md`, `docs/design/hardware-list.md`,
`docs/design/print-plan.md`, `cad/candybar/shell/joints.py`, `cad/candybar/shell/split.py`,
`cad/params/printer.csv`, and the build outputs `cad/out/shell-rev7/split/report.md`,
`cad/out/shell-rev7/split/measurements.json`, `cad/out/shell-rev7/split/shell/*.stl`,
`cad/out/shell-rev7/fit/report.md` and `cad/out/coupon/README.md` (read in the main checkout).

## 9. Not confirmed, and sources that were not accessible

| Item | Result |
| --- | --- |
| A review of the Q2 Combo by a large hardware site | The page gave its title only. Not used. |
| The glossary of the maker's wiki (the chamber circulation fan) | The page gave its title only. The search summary says that the fan "pulls air from inside the chamber". |
| The data sheet of a plastics seller for ABS sheet | HTTP 403. The value is from a search summary [M6]. |
| A V3 of the Bambu ABS data sheet | Not read. V2.0 was read. |
| A data sheet of QIDI ABS Rapido | Not looked for. The profile gives a density of 1.05 g/cm3 and an impact strength across the layers of 7.4. |
| The hold of a heat-set insert in printed ABS | No test found. |
| The largest gap that a solvent weld fills | No value found. |
| A creep value or a value for a long load on printed ABS | Not found, as in the earlier note. |
| The thermal expansion of printed ABS | Not found. The values are for sheet. |
| A measured overhang angle for ABS with little cooling | Not found. |
| The carbon mass of the Q2 cartridge and its capture of styrene | Not found. |
| A report of a large ABS shell printed on a Q2 | Not found. |
| The US price of the Q2 | Not read. |
