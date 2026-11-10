# Controls and ergonomics research

Research notes for the arcade control panel and the cabinet side profile.
Compiled 2026-11-09. Units are millimetres and degrees.

## How to read this file

- **SOURCED [Sn]** means the number is printed in the source listed under [Sources](#sources).
- **SCALED [Sn]** means the number was measured from a dimensioned drawing in that source (pixel scaling against a printed dimension). Accuracy is about ±0.5 mm.
- **ESTIMATED** means the number was derived here. The derivation is stated next to it.
- **CONFIRM** marks a number that must be measured on the physical part before the panel is printed.
- Layout coordinates use the joystick centre as origin, **X to the player's right, Y away from the player**.
- No parts are purchased. Every part number below is a candidate.

Caveat for the joystick: no JLX2-specific dimension drawing was found. The drawings used here are Sanwa's JLF-TP-8 series drawings. A Japanese retailer shows those same drawings on its JLX2 product page [S2], and Sanwa sells one flat plate, one harness and one shaft-cover set for both families [S4][S5][S6]. That supports a shared envelope. It does not prove it.

---

## 1. Sanwa JLX2-TP-8YT joystick

### 1.1 What it is

| Fact | Value | Status |
| --- | --- | --- |
| Family | JLX (2023) was the first successor to the JLF. JLX2 (2025) is the revised successor. | SOURCED [S1][S3] |
| JLX2 changes from JLX | Returns to the black JLF actuator, 15.8 diameter (JLX used a white 16.2 actuator). New X-shaped washer and revised M base that stop the washer rotating and lifting. | SOURCED [S1][S3] |
| JLX2 changes from JLF | M base changed from nylon to POM. Bearing changed from POM to nylon. Thicker base washer. PCB material changed from paper phenol to CEM-3. GT-8X restrictor fitted as standard. | SOURCED [S1][S2] |
| Restrictor | GT-8X, square gate. Supplied in 8-way. Remove the centre insert and refit it rotated 45 degrees for 4-way. | SOURCED [S2][S3] |
| Part-number suffixes | `TP-8` no base, connector parallel to the two mounting ears. `TP-8Y` no base, connector perpendicular. `TP-8T` flat plate, parallel. `TP-8YT` flat plate, perpendicular. `TP-8S` stepped plate. `-SK` adds the shaft cover. | SOURCED [S2] |
| Interchange | Sanwa states the JLX2 replaces JLF and JLX levers. JLF-P-1 flat plate, JLF-H 5-pin harness, JLF-CD shaft cover and dust disc, and M6 ball tops are shared. | SOURCED [S2][S3][S4][S5][S6] |
| Not interchangeable | JLX bearing (JLX-P-4), JLX2 M base (JLX-P-2) and JLX2 washer (JLX2-MW) do not fit a JLF. Do not mix JLF and JLX2 pivot parts. | SOURCED [S1][S2] |
| Supplied with the plain `-8YT` | Flat plate and two dust washers. No ball top and no 5-pin harness. A shaft cover comes only with `-SK` or as a retailer bundle. | SOURCED [S2][S7] |

### 1.2 Mounting plate (JLF-P-1 flat plate)

Plate coordinates: origin at the shaft centre, `u` along the plate's short side, `v` along the long side.

| Feature | Value | Status |
| --- | --- | --- |
| Official mounting size | 85 × 40 | SOURCED [S4] (Sanwa: "取付サイズ85×40(mm)") |
| Plate outline | 53 × 95, corner radius 3 | SOURCED [S2] (Sanwa drawing) |
| Plate thickness | 1.6 | SOURCED [S2][S9] |
| Four corner slots | Width 5.5 ("4-φ5.5 長穴"). Centres at u = ±20 (dimension 40). The drawing gives 80 and 85 on the long axis; read here as the slot's pitch range. | SOURCED [S2]; the range reading is an interpretation. CONFIRM |
| Slot length | About 8.3. With an M4 screw the usable pitch is about 78 to 86.5. | SCALED [S2]. CONFIRM |
| Two centre-line holes | φ6 at (0, ±42.5). Two-point mounting at 85 pitch. | SOURCED [S2][S13] |
| Two offset holes | φ5 at (+10, +42.5) and (−10, −42.5) | SOURCED [S2][S13] |
| Body ears (no plate) | Two φ5 holes at 65 pitch on the long axis. Ear width 10. | SOURCED [S2] |
| Stepped (S) plate | 96 pitch, two-point (Tops). Step height 9 (slagcoin). | SOURCED [S2][S9] |
| Community pattern | 85 × 40 or 80 × 40 both work for the JLF flat plate. | SOURCED [S8] |
| Plate-to-body screws | M3 × 8 countersunk with M3 nuts (kit name JLF-P-1/SB-3-8/N-3). | SOURCED [S5] |

Recommendation for CAD: four M4 fixings at **u = ±20, v = ±42.5** (40 × 85). Keep both pitches as parameters.

### 1.3 Body, shaft and clearances

Heights are measured from the body-to-plate interface, which is the reference face in the Sanwa section view.

| Feature | Value | Status |
| --- | --- | --- |
| Body width across the plate's short axis | 62. It reaches 31 on one side and 33 on the connector side. The body is wider than the 53 plate. | SOURCED [S2] |
| Body length along the plate's long axis | 75 over the ears | SOURCED [S2] |
| PCB | About 53 × 53 | SOURCED [S2] (dimension 53 shown twice) |
| Body depth | 26.4, plus 3 for the gate clips, total 29.4 | SOURCED [S2] |
| Shaft tip (E-ring end) below the interface | 34 | SOURCED [S2] |
| Ball seat above the interface | 34 | SOURCED [S2] |
| Shaft length, tip to thread shoulder | 68 | SOURCED [S10]; agrees with 34 + 34 |
| Ball seat above the plate's panel-side face | 32.4 (34 − 1.6). Slagcoin lists 32. | ESTIMATED from [S2]; SOURCED [S9] |
| Shaft tip below the plate's panel-side face | 35.6 (34 + 1.6). Slagcoin lists 36. | ESTIMATED from [S2]; SOURCED [S9] |
| Tilt | ±8.5 degrees | SOURCED [S2][S4] |
| Pivot centre | About 8 below the interface | SCALED [S2] |
| Shaft cover diameter | 11.6 at the top, 12.3 at the bottom | SOURCED [S11] (search summary; page returned 403) |
| Dust washer diameter | 38 (replacement part sold as a drop-in) or about 41 (scaled from the Sanwa drawing) | SOURCED [S12] / SCALED [S2]. CONFIRM |
| Dust washer thickness | About 1 each | SOURCED [S8] |
| Ball top | 35 diameter (LB-35), M6 thread | SOURCED [S1] |
| Weight | About 185 g (JLF) | SOURCED [S9] |

### 1.4 Panel hole for the shaft

| Item | Value | Status |
| --- | --- | --- |
| Standard hole | 24 diameter, "plus or minus a few millimetres" | SOURCED [S8] |
| Geometric minimum | 16.7 for a 5 thick deck, 17.9 for a 9 thick deck | ESTIMATED: (pivot depth + deck thickness) × tan 8.5° + 6.15 cover radius |
| Alternative bore | 35.25 if the plate sits in a recess | SOURCED [S13] |

Use 24. The 38 to 41 dust washer covers it at full tilt.

### 1.5 Panel thickness and lever height

| Item | Value | Status |
| --- | --- | --- |
| Arcade-standard lever height | 23 to 24 between the panel top and the bottom of the ball | SOURCED [S8][S9] |
| Shaft exposure with the plate bolted under a panel of thickness `t` | 32.4 − t | ESTIMATED from [S2] |
| Depth of the plate's top face below the panel top for the standard height | 8.5 to 9.5 | ESTIMATED: 32.4 − (23 to 24) |
| Taito Vewlix practice | Steel panel 1.16 to 1.5, total 1.75 to 2.2 with overlay. Spacers of about 7.5 between plate and panel. M4 studs, 10 long. Result: 9.25 from panel top to plate top. | SOURCED [S14] |
| Acceptable range | 3.2 to 12.7 below the panel top (slagcoin: 1/8 to 1/2 inch) | SOURCED [S9] |
| Common fight-stick mounting | Plate 6 to 8 under the panel top | SOURCED [S8] |
| Thick wooden panels | An extended shaft adds 15 for panels up to 18 | SOURCED [S10] |

For the printed panel:

- **Under-mount, recommended.** Put the plate's top face 9.0 to 9.5 below the finished top surface. Use a locally 9 thick deck, or a 5 deck with 4 to 4.5 spacer bosses as the Vewlix does.
- **Top-mount.** The plate drops into a pocket from above and needs a cover layer. This suits a plexi-over-metal stack. It gives no benefit on a printed deck.
- **Resulting envelope** with the plate top 9.25 below the surface: shaft tip 44.9 below the panel top, ball seat 23.2 above it, top of a 35 ball about 57 above it. ESTIMATED from [S2].

### 1.6 Connector and harness

| Item | Value | Status |
| --- | --- | --- |
| Connector | JST 5-pin header, marked "BS-5P-SHF (JST)" on the Sanwa drawing. Retailers call it JST NH 5-pin. | SOURCED [S2][S15] |
| Pin 1 | Common (ground). Pins 2 to 5 are the four switches. | SOURCED [S2] |
| Connector position on a `-8YT` | On the long edge of the body. Pins point along the plate's short axis. | SOURCED [S2] |
| Connector housing edge | 33 from the shaft centre | SOURCED [S2] |
| Pin tips | About 38.7 from the shaft centre | SCALED [S2] |
| Connector offset along the plate's long axis | About 19.5 from the shaft centre | SCALED [S2]. CONFIRM |
| Harness clearance | Keep 60 clear from the shaft centre on the connector side | ESTIMATED: 38.7 + about 10 for the mating housing + about 10 wire bend. CONFIRM |

Orientation for the panel:

- Run the plate's long axis **front to back** (along Y). The plate then spans X ±26.5 and the body spans X −33 to +31.
- If the long axis ran left to right, the plate would reach X = 47.5 and hit the first button nut at X = 41. ESTIMATED from [S2] and section 3.
- Point the connector to the **left** (−X), away from the buttons. Remap directions in the encoder if needed.

---

## 2. Push buttons

### 2.1 Sanwa 30 mm

| Feature | OBSN-30 (screw-in) | OBSF-30 (snap-in) | Status |
| --- | --- | --- | --- |
| Panel hole | φ30 ±0.1 | φ30 ±0.1 (drawing shows +0.1/0) | SOURCED [S16][S17][S18] |
| Rim outer diameter | 33.2 | 33.2 | SOURCED [S18][S19] |
| Plunger diameter | 25 | 25 | SOURCED [S18][S19] |
| Thread or body diameter | 29.5 | 30.3 measured | SOURCED [S18] / [S9] |
| Nut outer diameter | 36 | none | SOURCED [S18][S9] |
| Nut height | 11 | none | SOURCED [S18] |
| Height above the panel | 6.4 (rim 3 + plunger 3.4) | 6.5 (3 + 3.5) | SOURCED [S18][S19] |
| Body below the panel top | 17 threaded | 19.2 | SOURCED [S18][S19] |
| Switch and terminals below the body | 17.5 | 12.5 | SOURCED [S18][S19] |
| **Total below the panel top, to terminal tips** | **34.5** | **31.7** | SOURCED [S18][S19] |
| Slagcoin "depth" | 32 | 32 | SOURCED [S9] |
| Terminals | #110 tab (2.8) | #110 tab (2.8) | SOURCED [S18][S19] |
| Switch | SW-68. A connector version (SW-68CAU) is offered. | Same | SOURCED [S16][S17] |
| Panel thickness, Sanwa | **5 max** | **3.9 max** (Sanwa shop); 3.7 max (Tops) | SOURCED [S16][S17][S19] |
| Panel thickness, measured by slagcoin | 0 to 11 | 2.4 to 4.2 | SOURCED [S9] |
| Hole edge in acrylic | not stated | chamfer C0.3 to C0.5 | SOURCED [S19] |

Where the sources disagree:

- **OBSN-30 panel thickness.** Sanwa says 5 max. Slagcoin measured 0 to 11. Trust Sanwa's 5 for design. The thread is 17 long and the nut is 11 tall, so a 6 panel is the last thickness that leaves the nut fully engaged. Slagcoin's 11 is the physical limit with a few threads holding. Slagcoin also advises staying 2 under the maximum.
- **OBSF-30 panel thickness.** Use 3.0 to 3.5 as the design value. It is inside all three ranges.
- **Depth.** Trust the Sanwa drawings (34.5 and 31.7) over slagcoin's rounded 32.

Depth with 2.8 quick-disconnects:

| Item | Value | Status |
| --- | --- | --- |
| Straight insulated 2.8 female terminal beyond the tab tip | About 13, plus about 10 for the wire bend | ESTIMATED from typical terminal length of about 19 with about 6 of tab engaged. CONFIRM |
| Clear depth below the panel top, OBSN-30 | 55 minimum, 60 preferred | ESTIMATED: 34.5 + 13 + bend |
| Clear depth below the panel top, OBSF-30 | 52 minimum | ESTIMATED: 31.7 + 13 + bend |
| Saving from bent tabs | Up to 7 | SOURCED [S9] |

### 2.2 Spacing forced by the nut

| Item | Value | Status |
| --- | --- | --- |
| Minimum centre distance, OBSN-30 with Sanwa nut | 36 | SOURCED [S18][S20] |
| Minimum centre distance with a Seimitsu nut | 35. The nut fits Sanwa 30 buttons. | SOURCED [S9][S20] |
| Minimum centre distance, OBSF-30 | 33.2 (rim to rim) | ESTIMATED from [S19] |
| Common spacing | 36 to 36.5 between centres. Rows 36 or 39 apart. | SOURCED [S20] |
| Material left between two φ30 holes at 36 | 6 | ESTIMATED |

The standard arcade layouts break the 36 rule. See section 3.4.

### 2.3 Sanwa 24 mm (start, coin, menu)

| Feature | OBSN-24 (screw-in) | OBSF-24 (snap-in) | Status |
| --- | --- | --- | --- |
| Panel hole | φ24 ±0.1 | φ24 ±0.1 | SOURCED [S21][S22] |
| Rim outer diameter | 27.3 | 27.2 | SOURCED [S23] / [S9] |
| Plunger diameter | 19.5 | 19.5 | SOURCED [S23][S9] |
| Thread or body diameter | 23.5 | 23.5 | SOURCED [S23][S24] |
| Nut outer diameter | 29.5 | none | SOURCED [S23][S9] |
| Height above the panel | 6.0 | 5.8 | SOURCED [S23][S24] |
| Body below the panel top | 14.7 | 18.2 | SOURCED [S23][S24] |
| Switch and terminals | 16.9 | 13.8 | SOURCED [S23][S24] |
| **Total below the panel top** | **31.6** | **32.0** | SOURCED [S23][S24] |
| Panel thickness, Sanwa | 5 max | 3.9 max | SOURCED [S21][S22] |
| Panel thickness, slagcoin | 0 to 11 | 2 to 4.2 | SOURCED [S9] |
| Minimum centre distance | 29.5 (nut). Slagcoin says "more like 29". | SOURCED [S23][S20] |

Sanwa and Seimitsu 24 nuts do not interchange [S8].

### 2.4 Consequences for a printed deck

- The deck can be at most 5 thick where an OBSN button sits, and 3.0 to 3.5 where an OBSF button sits.
- The lever wants 9 to 9.5 (section 1.5). Use a 5 deck with a local 9 pad or bosses under the lever.
- OBSN nuts at 36 pitch touch each other. No rib fits between adjacent buttons. Stiffen the button field with a perimeter frame and ribs outside the cluster.
- Printed holes come out small. Model the hole as a parameter and start the test coupon at φ30.2 to 30.4 and φ24.2 to 24.4. ESTIMATED; the project brief already calls for a button-hole coupon.

---

## 3. Button layouts

### 3.1 Sources and verification

The coordinates come from slagcoin's dimensioned diagrams [S20]. Each one was checked two ways:

1. Decoded from the printed dimensions, then confirmed by locating the button centres in the image by pixel analysis.
2. Compared with the DXF files of the JasensCustoms FightStickLayoutProject [S13], which uses the same origin and axes. The DXF circle centres match to 0.0.

### 3.2 Coordinate table

Buttons are named by row and column. `B` is the bottom row (nearest the player). `T` is the top row. Column 1 is the index finger.

| Button | Sega Astro City P1 | Sega P2, stick at 59 | Sega P2, stick at 63 | Taito Vewlix |
| --- | --- | --- | --- | --- |
| B1 | (59, −14) | (59, −20) | (63, −20) | (59, −28) |
| B2 | (92, 0) | (89.5, 0) | (93.5, 0) | (92, −15) |
| B3 | (128, −6) | (125.5, 0) | (129.5, 0) | (128, −15) |
| B4 | (162, −21) | (161, −9) | (165, −9) | (164, −15) |
| T1 | (66, 24.5) | (59, 19) | (63, 19) | (66, 10) |
| T2 | (99, 38.5) | (89.5, 39) | (93.5, 39) | (99, 24) |
| T3 | (134.5, 32.5) | (125.5, 39) | (129.5, 39) | (135, 24) |
| T4 | (168.5, 17.5) | (161, 30) | (165, 30) | (171, 24) |
| Status | SOURCED [S20][S13] | SOURCED [S20] | SOURCED [S20][S13] | SOURCED [S20][S13] |

Notes on each layout:

- **Sega Astro City P1.** Used in Astro City, Blast City, Net City and Versus City for player 1 or single player. Slagcoin calls it the standard Japanese arcade layout. Blast City moves B2 0.5 to the right and uses the higher stick position. SOURCED [S20].
- **Astro City alternative stick position.** 14.5 further from the player, which puts the stick 10 below T1. Subtract 14.5 from every button Y to use it. SOURCED [S20] (decoded).
- **Sega P2 ("Sega 2P").** The non-slanted player-2 layout. Slagcoin draws two stick distances, 59 and 63. Alternative pinky positions: (156, −20)/(156, 19) and (161.5, 0)/(161.5, 39) for the stick at 59. SOURCED [S20].
- **Taito Vewlix.** The real panel has seven buttons; B4 is the optional eighth. The table uses the drawn stick position, 15 above the bottom row. Slagcoin also marks a stick level with the bottom row (add 15 to every Y) and a 63 stick distance (add 4 to every X). SOURCED [S20][S13].
- **Six-button form.** Use columns 1 to 3 of any layout. The Sega 1L6B panel is the Astro City layout without column 4.

Row and column offsets, SOURCED [S20]:

| Layout | Row spacing | Top row shift in X | Column drops (Y relative to column 2) |
| --- | --- | --- | --- |
| Astro City P1 | 38.5 | +7, +7, +6.5, +6.5 | −14, 0, −6, −21 |
| Sega P2 | 39 | 0 | −20, 0, 0, −9 |
| Vewlix | 39 for columns 2 to 4; 38 for column 1 | +7 | −13 bottom and −14 top for column 1; others 0 |

### 3.3 Stick-to-button spacing

| Item | Value | Status |
| --- | --- | --- |
| Common horizontal distances, stick to first column | 59, 63 or 95 | SOURCED [S20] |
| Extra variant in the DXF set | 82 | SOURCED [S13] |
| Japanese cabinet standard | 59 (Astro City, Vewlix as drawn) | SOURCED [S20][S13] |
| Nearest button centre to the stick | 60.6 (Astro), 62.0 (Sega P2 at 59), 65.3 (Vewlix) | ESTIMATED from the table |

### 3.4 Nut clearance check

Centre distances below 36 clash with the Sanwa OBSN-30 nut. ESTIMATED from the table; the conclusion is confirmed in [S20] and [S13].

| Layout | Pairs under 36 | Smallest |
| --- | --- | --- |
| Astro City P1 | B2–T1 35.72, B1–B2 35.85, T1–T2 35.85 | 35.72 |
| Sega P2 | B2–T1 35.93 | 35.93 |
| Vewlix | B1–B2 35.47, T1–T2 35.85 | 35.47 |

Ways out, in order of preference:

1. Use Seimitsu 35 nuts on the OBSN-30 buttons [S9][S20].
2. Use OBSF-30 snap-ins on a 3.0 to 3.5 deck.
3. Scale the button coordinates by 1.02 about the cluster. Astro City then has a 36.4 minimum. ESTIMATED; this departs from the arcade layout.

### 3.5 Namco Noir

- No dimensioned Noir drawing was reachable. Slagcoin does not publish one [S20]. The JasensCustoms set has none [S13].
- Forum search summaries describe a community diagram on r/fightsticks and describe Noir as a slight change to the Sega P2 layout with the stick further left [S25]. Reddit blocked automated fetches. INACCESSIBLE.
- Do not model Noir until a drawing is traced by hand. Sega P2 is the closest sourced layout.

### 3.6 Panel size the layouts need

All values ESTIMATED unless marked.

| Item | Value | How |
| --- | --- | --- |
| Button field, Astro City 8 | X 59 to 168.5, Y −21 to 38.5 | Table |
| Button field with rims | X 42.4 to 185.1, Y −37.6 to 55.1 | ±16.6 rim radius |
| Left margin from the stick | 100 to 110 | Room for the left hand around the lever |
| Right margin from the last rim | 35 or more | Edge distance and little-finger rest |
| Minimum width, 8 buttons | About 320 | 100 + 185 + 35 |
| Minimum width, 6 buttons | About 285 | 100 + 151 + 35 |
| Palm rest in front of the lowest button centre | 100 to 120 | Section 5 |
| Front edge | Y = −125 to −140 | −21 − (100 to 120) |
| Space behind the top row for a row of 24 buttons | About 70 from the top-row centres | 16.6 + 15 gap + 27.3 + 10 edge |
| Rear edge | About Y = +108 | 38.5 + 70 |
| Depth | 233 to 248 | Sum |
| Commercial reference | Fight-stick DIY case 451 × 303 inside, 62.2 tall stack | SOURCED [S13] |

Printer consequence: the depth fits the 256 bed. The width does not. A straight seam at about **X = +36** runs through the 10 wide corridor between the lever body (X = +31) and the first button nut (X = +41). It gives a lever tile and a button tile that each stay under 250 wide for decks up to about 480. The seam lies between the hands, so both tiles need full-width rails or a subplate under them.

---

## 4. Encoders and the panel connection

### 4.1 Boards

| Board | Size | Mounting holes | Inputs and connectors | USB | Status |
| --- | --- | --- | --- | --- | --- |
| RP2040 Advanced Breakout Board (GP2040-CE reference design) | 96.30 × 45.31 | Four, drill 3.6, at 87.96 × 36.95 centres, about 4.2 from each edge | 20-way screw terminal row along the top edge (3.5 pitch; 3.81 on the passthrough version). 2×10 2.54 header at the bottom left with the Brook pinout. JST 2.0 for extras. | USB-C on the right short edge. A USB-B build also exists. | SOURCED [S26]; outline and holes read from the published Gerber files |
| Brook Universal Fighting Board | 96.3 × 45.3 | Four at 88 × 37, hole 3.1 | 20-pin header, screw terminals | not checked | SOURCED [S27] (forum summary) |
| Raspberry Pi Pico | 51 × 21, PCB 1 thick | Four, 2.1 (±0.05) | Solder pads or pin headers, 2.54 pitch. No terminals. | Micro-USB B overhanging one short edge | SOURCED [S28] |
| Raspberry Pi Pico hole pitch | 11.4 × 47 | | | | ESTIMATED: recalled from the datasheet's mechanical drawing, which is an image. CONFIRM |
| Ultimarc Mini-PAC | 57 × 38 (2 1/4 × 1 1/2 inch) | Two holes near the header take optional PCB feet | 40-way 2.54 pin header (IDE style). Harness with 2.8 or 4.8 female terminals. 32 inputs. Harness wires 330 long. | "USB cable supplied". Connector type not stated. CONFIRM | SOURCED [S29][S30] |

GP2040-CE facts, SOURCED [S31]:

- Runs on the Raspberry Pi Pico and other RP2040 boards.
- 14 input modes, including XInput, D-Input, Switch, PS4/PS5 and Keyboard.
- Average latency 0.76 ms in XInput at 1000 Hz polling.
- Configured through a web page served by the board. Settings stay on the board.

### 4.2 Recommendation: one encoder per panel, one USB cable

Give every panel its own encoder. Make a single USB cable the only electrical connection between a panel and the cabinet.

Evidence:

- **Signal count.** An arcade panel has 4 directions, 8 buttons and at least 3 service buttons. That is 15 signals plus ground. A shared encoder needs a 16-way or larger connector mated at every swap. Hobby builds that share an encoder use DB15 or DB25 for this [S32].
- **Panel identity.** GP2040-CE stores mode and mapping on the board [S31]. The arcade panel can present as a gamepad and the PC panel as a keyboard or another device. A shared encoder forces one device type and one pin map on every panel.
- **Brief requirement.** The brief asks that a panel "disconnect without pulling on terminals". A panel-mounted USB socket or a strain-relieved pigtail does that. A 2.54 header or loose terminals do not.
- **Size.** The largest board is 96 × 45 and fits under the deck beside the lever with room to spare.

Trade-offs:

- One encoder must be bought per panel.
- The operating system sees a different device for each panel. The front end needs an input profile per panel, and it must cope with hot-plugging.
- A shared encoder keeps one device identity, which is simpler for software. It costs a many-pin connector and fixes the pin map for all panels.

Cabinet-side detail: keep the USB cable long enough to lift the panel clear before unplugging, or fit a panel-mount USB-C socket at a fixed position on every panel.

---

## 5. Ergonomics for seated play

### 5.1 Reference cabinets

| Item | Value | Status |
| --- | --- | --- |
| Sega New Astro City footprint | 750 wide × 905 deep | SOURCED [S33] (service manual) |
| Sega New Astro City height | 1445 | SOURCED [S33] |
| Sega New Astro City weight | 93 kg (manual); 95 kg (wiki) | SOURCED [S33][S34] |
| Monitor | 29 inch CRT, Nanao MS9-29A | SOURCED [S34] |
| Astro City control panel top above the floor | 660 | SOURCED [S35] (owner measurement) |
| New Astro City control panel top above the floor | 650 | SOURCED [S35] (owner measurement) |
| Taito stool height for Astro-type cabinets | 430 | SOURCED [S36] |
| Taito stool height for the Vewlix | 480 | SOURCED [S36] |
| Sega bench height | 400. "Knees just barely fit" for a 180 cm player. | SOURCED [S35] |
| Panel above the seat, Astro City type | 220 to 230 | ESTIMATED: 650 to 660 minus 430 |
| Vewlix panel height | not found | INACCESSIBLE |
| Vewlix panel above the seat | Assume the same 220 to 250 | ESTIMATED from the stool pairing |
| Control panel slope, any candy cabinet | not found | INACCESSIBLE |
| Monitor recline, any candy cabinet | not found | INACCESSIBLE |
| Blast City and Egret II dimensions | not found. Their panels share the Sega Astro format. | INACCESSIBLE; format SOURCED [S37] |

### 5.2 Body dimensions

Computed here from the public ANSUR II data set (4082 men, 1986 women) [S38]. Values are 5th / 50th / 95th percentile.

| Measure | Men | Women |
| --- | --- | --- |
| Eye height above the seat | 750 / 804 / 860 | 698 / 748 / 799 |
| Elbow rest height above the seat | 197 / 246 / 291 | 189 / 233 / 275 |
| Thigh clearance above the seat | 157 / 180 / 207 | 145 / 167 / 191 |
| Popliteal height (seat height for flat feet) | 390 / 430 / 471 | 350 / 387 / 428 |
| Hand length | 177 / 193 / 210 | 165 / 180 / 199 |

Reading: on an Astro City the panel is about 20 **below** the median male elbow height. That is the relationship to aim for.

### 5.3 Screen guidance

SOURCED [S39] (OSHA computer workstation guidance):

- Viewing distance 500 to 1000 (20 to 40 inches). At least 500.
- Top line of the screen at or below eye level.
- Screen centre 15 to 20 degrees below horizontal eye level.
- Screen tilt no more than 10 to 20 degrees.
- Downward viewing angle never more than 60 degrees.

### 5.4 What a 730 to 760 desk changes

- A candy cabinet stands on the floor and the player sits low. The panel is 650 to 660 high and the seat 430.
- A tabletop cabinet adds its control box height to the desk height. With a 60 box on a 745 desk the panel is at 805.
- To keep the Astro relationship the seat would have to be about 560 to 585. A seat that high leaves less than the median thigh clearance under the desk. ESTIMATED: desk underside about 715, minus 180 thigh clearance, gives a 535 seat limit.
- So the panel will sit higher against the body than on a candy cabinet. Expect 260 to 320 above the seat, which is 15 to 75 above the median male elbow. This is the same posture as a fight stick used on a desk.
- Every millimetre of control box height goes straight into wrist height. Keep the box as shallow as the parts allow.
- Option to test: let the control deck overhang the front edge of the desk. The deck can then sit at desk level or lower. The overhang adds a tipping moment that the power supply at the rear must balance. ESTIMATED; not sourced.

### 5.5 Recommended targets

For one adult in a standard chair at a 730 to 760 desk. All are starting values for the bench test in the project brief.

| Quantity | Target range | Status |
| --- | --- | --- |
| Clear depth inside the control box, below the panel top | 55 to 60 | ESTIMATED, sections 1.5 and 2.1 |
| Panel top above the desk, front edge | 60 to 75. Lower is better. | ESTIMATED: clear depth plus floor |
| Panel top above the floor | 790 to 835 | ESTIMATED |
| Chair seat height | 480 to 530. Use a footrest if the feet lift. | ESTIMATED from 5.4 |
| Panel top above the seat | 260 to 320. Astro reference is 220 to 230. | ESTIMATED / SOURCED [S35][S36] |
| Panel tilt | 0 to 5 degrees, rear edge higher. Start flat. | ESTIMATED: fight-stick and candy panels are near flat; no sourced angle |
| Palm rest, lowest button centre to the front edge | 100 to 120 | ESTIMATED: 0.52 to 0.62 of the 193 median hand length |
| Front edge profile | Radius 10 or more | ESTIMATED |
| Stick to first button column | 59 to 63 | SOURCED [S20] |
| Button pitch | 36 nominal, rows 38.5 to 39 | SOURCED [S20] |
| Eye to screen centre | 450 to 600. Start at 500. | ESTIMATED from [S39] and screen size |
| Screen centre below horizontal eye level | 15 to 25 degrees | SOURCED [S39] for 15 to 20; upper end ESTIMATED |
| Screen recline from vertical | 15 to 25 degrees. Start at 20. Match it to the sight line. | ESTIMATED; [S39] limits tilt to 10 to 20 |
| Top of the image | At or below eye level | SOURCED [S39] |
| Eye height above the desk, median man | About 530 | ESTIMATED: 500 seat + 804 − 30 slump − 745 desk |
| Screen centre above the desk | 320 to 400 for that eye height. General rule: eye height minus 130 to 210. | ESTIMATED: 500 × sin(15 to 25 degrees) |
| Screen centre behind the panel's front edge | 370 to 480 | ESTIMATED: 500 × cos(15 to 25 degrees), with the eyes between the front edge and 80 on the player's side of it |

Screen size check, ESTIMATED: the 345 wide image subtends 38 degrees at 500. A 29 inch 4:3 tube (589 wide) at 650 subtends 49 degrees. Matching that would need a 380 viewing distance, which is below the OSHA minimum. Accept the smaller image.

Measure the real player's seated eye height and elbow height first. They replace the median values above.

---

## 6. Swappable panel mechanics

### 6.1 How commercial cabinets do it

| Cabinet | Method | Status |
| --- | --- | --- |
| Sega New Astro City | The plastic control panel base hinges open after two locks on its back side are released. One lock is also screwed shut with an M4 × 30 screw at the factory. | SOURCED [S33] (manual page 11) |
| Sega New Astro City, panel plate | The steel panel is held to the base by six M4 × 16 carriage bolts with M4 flange nuts. To swap: open the base, unplug the connectors, remove the earth-wire screw (M4 × 8), remove the six nuts. | SOURCED [S33] |
| Sega Astro City repro panels | Steel, with M4 × 20 studs for the stick and M4 flange nuts. Fit Astro City, Blast City and Naomi cabinets. | SOURCED [S40] |
| Taito Vewlix | Steel panel 1.16 to 1.5 thick. M4 studs 10 long. Stick spaced 7.5 below the panel. Hinge and lock details were not confirmed. | SOURCED [S14]; mechanism INACCESSIBLE |
| Sega panel format | Astro City, Blast City and Net City panels interchange. They also fit Taito Egret II and Egret III. | SOURCED [S37] |

Pattern: a rigid metal plate, bolted to a carrier, with the carrier hinged and locked. Swaps need tools and several minutes.

### 6.2 DIY practice

| Example | Method | Status |
| --- | --- | --- |
| 3D-printed modular cabinet (MakerWorld, 2025) | Neodymium magnets in a printed frame. About 20 s per swap. Printed in PLA. | SOURCED [S41] (search summary) |
| Hobby cabinets on r/cade | Removable panels with DB15 or DB25 connectors | SOURCED [S32] (search summary) |
| Build Your Own Arcade Controls forum threads | not reachable | INACCESSIBLE |

### 6.3 Stiffness of a printed panel

All ESTIMATED.

- PETG has a flexural modulus of about 2.1 GPa. Steel is about 200 GPa. These are typical data-sheet values, not measured for this filament.
- For the same bending stiffness as a flat 1.6 steel plate, solid PETG must be about 7.3 thick: 1.6 × (200 / 2.1)^(1/3).
- The buttons cap the deck at 5 (section 2.4). So the deck cannot match a steel panel by thickness alone. It needs ribs outside the button field, a perimeter frame, and the steel lever plate used as a local stiffener.
- Lever load: a hard input puts roughly 20 to 40 N sideways on the ball, about 60 above the panel. That is a 1.2 to 2.4 N·m moment at the lever seat, reversing constantly. Palms add steady downward load at the front edge.

### 6.4 Assessment of latching options

| Option | Suits printed PETG? | Reason |
| --- | --- | --- |
| Rear tongue and front clamp | Yes | Loads go into wide printed flanges in compression. The clamp gives preload, so nothing rattles. |
| Drop-in tray with pins and screws | Yes | Pins take shear. Screws into metal inserts take lift. The perimeter ledge supports the deck edge. |
| Hinge with latches (Sega style) | Partly | Good for service access. A hinge does not make a panel swappable. |
| Slide-in rails | Partly | Long printed rails need clearance, and clearance rattles under lever load. Needs a clamp anyway. |
| Quarter-turn fasteners | Yes, as the clamp | Fast and positive. Use metal receptacles. |
| Toggle (draw) latches | Yes, as the clamp | Over-centre preload. Bolt them through the PETG with backing washers. |
| Magnets with pins | No, as the only retention | Magnets resist sliding and peeling poorly. Lever moments peel the panel. Use magnets only to seat the panel. |

### 6.5 The two approaches to prototype

**A. Rear tongue plus front clamp.**

- The panel's rear edge carries a tongue that slides under a lip in the cabinet. The tongue locates the panel and takes upward load.
- Two clamps at the front pull the panel down and back: draw latches under the front edge, or two captive M4 thumbscrews into heat-set inserts.
- This mirrors the Sega hinge-and-two-locks idea with the fixed edge moved to the rear.

**B. Drop-in tray on a ledge, two dowel pins, four fasteners.**

- The panel drops onto a continuous ledge around the opening.
- Two steel dowel pins locate it. One sits in a round hole and one in a slot, so print shrinkage cannot bind them.
- Four captive M4 thumbscrews or quarter-turn fasteners at the corners hold it down. They go into heat-set inserts or metal receptacles.
- Magnets may be added to seat the panel before the fasteners are turned.

Common rules for both: put the fasteners in metal, keep preload on the joint, and print a latch-and-locator coupon before the full panel.

---

## 7. Confirm on the physical parts before printing

1. JLX2-TP-8YT body depth below the plate (expected 29.4) and shaft-tip depth (expected 34).
2. JLX2 plate: outline 53 × 95, slot pitch window, slot width 5.5, thickness 1.6.
3. Ball-seat height above the plate (expected 32.4) and the lever height that feels right. This sets the 9.0 to 9.5 seat depth.
4. 5-pin connector position, direction and the room the mated harness needs (expected 60 from the shaft centre).
5. Dust washer diameter (38 or 41) and shaft cover diameter.
6. OBSN-30 nut diameter (expected 36) and whether the nut grips on a 5 deck. Seimitsu nut diameter (expected 35) if those are used.
7. OBSN-30 and OBSN-24 thread diameters (29.5 and 23.5) against printed hole coupons.
8. OBSF-30 and OBSF-24 snap fit on 3.0 and 3.5 coupons, if snap-ins are chosen.
9. Depth below the panel with the actual 2.8 terminals and wire fitted.
10. Encoder board: outline, hole pattern and USB connector type and direction.
11. The player's seated elbow height and eye height at the real desk and chair.
12. Palm-rest depth and panel height in a 20 to 30 minute play test.

---

## Inaccessible sources

| Source | Result |
| --- | --- |
| forum.arcadecontrols.com (ergonomics and removable-panel threads) | Connection refused on HTTP and HTTPS |
| wiki.arcadeotaku.com (cabinet pages) | Blocked by bot protection |
| reddit.com threads (Noir layout, Vewlix display angle, Vewlix panel height, modular cabinet) | Fetch blocked; extract timed out. Only search summaries were used. |
| support.focusattack.com (shaft cover article) | HTTP 403. Search summary used. |
| sanwa-d.co.jp product pages | Text is legacy-encoded and the pages carry no drawings. The official shop pages were decoded instead. |
| New Astro City manual | Scanned images without text. Pages 3 and 11 were read as images. No panel-height or monitor-angle drawing was found in the first 30 pages. |

---

## Sources

- [S1] Focus Attack, Sanwa JLX2-TP-8YT: https://focusattack.com/sanwa-jlx2-tp-8yt-joystick-successor-to-sanwa-jlx/
- [S2] Tops Game, Sanwa JLX2-TP-8 series, with Sanwa dimension drawings (image files `JLF-TP-8_0010.jpg` and `JLF-TP-8_0012.jpg`): https://www.tops-game.jp/products/detail.php?product_id=7536
- [S3] Arcade Shock, Sanwa JLX2-TP-8YT: https://arcadeshock.com/products/sanwa-denshi-jlx2-tp-8yt
- [S4] Sanwa Denshi official shop, JLX2-TP-8YT: https://www.sanwa-d.shop/shopdetail/000000000104/
- [S5] Sanwa Denshi official shop, JLF-P-1 flat plate for JLF/JLX/JLX2: https://www.sanwa-d.shop/shopdetail/000000000118/
- [S6] Sanwa Denshi official shop, JLF-CD shaft cover and disc set for JLF/JLX/JLX2: https://www.sanwa-d.shop/shopdetail/000000000120/
- [S7] Arcade Express, Sanwa JLX2-TP-8YT: https://www.arcadexpress.com/en/joysticks/900-arcade-joystick-sanwa-jlx-tp-8y.html
- [S8] Slagcoin, Panel Mounting and Layering (includes `mounting_layering/plate.png`): https://www.slagcoin.com/joystick/mounting_layering.html
- [S9] Slagcoin, Attributes and Brand Parts (includes `attributes_brands/chart.png` and `chart_b.png`): https://www.slagcoin.com/joystick/attributes_brands.html
- [S10] Focus Attack, Extended Sanwa JLF Joystick Shaft: https://focusattack.com/extended-sanwa-jlf-joystick-shaft/
- [S11] Focus Attack support, shaft cover diameter: https://support.focusattack.com/hc/en-us/articles/360000253623-What-is-the-diameter-of-a-Sanwa-JLF-shaft-cover
- [S12] Focus Attack, Solo Sanwa JLF Dustwasher: https://focusattack.com/solo-sanwa-jlf-dustwasher-fits-sanwa-jlf-with-shaft-cover-set-of-2/
- [S13] JasensCustoms FightStickLayoutProject (README and `dxf/sega1_s.dxf`, `sega2_s.dxf`, `vewlix_s.dxf`, `vewlix_s_8button.dxf`): https://github.com/JasensCustoms/FightStickLayoutProject
- [S14] Arcade-Projects, All about Vewlix control panels: https://www.arcade-projects.com/threads/all-about-vewlix-control-panels-vewlix-chewlix-rt-repos-etc.15338/
- [S15] Jasen's Customs, Sanwa JLX-TP-8YT: https://jasenscustoms.com/products/sanwa-jlx-tp-8yt-joystick
- [S16] Sanwa Denshi official shop, OBSN-30: https://www.sanwa-d.shop/shopdetail/000000000178/
- [S17] Sanwa Denshi official shop, OBSF-30: https://www.sanwa-d.shop/shopdetail/000000000109/
- [S18] Tops Game, OBSN-30, with Sanwa drawing `OBSN-30_05.jpg`: https://www.tops-game.jp/products/detail.php?product_id=6732
- [S19] Tops Game, OBSF-30, with Sanwa drawing `OBSF-30_05.jpg`: https://www.tops-game.jp/products/detail.php?product_id=2634
- [S20] Slagcoin, Panel Layout (diagrams `layout/sega1_l.png`, `sega2_l.png`, `vewlix_l.png`): https://www.slagcoin.com/joystick/layout.html
- [S21] Sanwa Denshi official shop, OBSN-24: https://www.sanwa-d.shop/shopdetail/000000000179/
- [S22] Sanwa Denshi official shop, OBSF-24: https://www.sanwa-d.shop/shopdetail/000000000110/
- [S23] Tops Game, OBSN-24, with Sanwa drawing `OBSN-24_05.jpg`: https://www.tops-game.jp/products/detail.php?product_id=6727
- [S24] Tops Game, OBSF-24, with Sanwa drawing `OBSF-24_05.jpg`: https://www.tops-game.jp/products/detail.php?product_id=6733
- [S25] Reddit r/fightsticks, Namco Noir layout threads (search summaries only): https://www.reddit.com/r/fightsticks/comments/v4x1yy/namco_noir_layout/
- [S26] OpenStickCommunity Hardware, RP2040 Advanced Breakout Board (README and Gerber archive v5.3E): https://github.com/OpenStickCommunity/Hardware/tree/main/Boards/GP2040-CE%20Official%20Boards/RP2040%20Advanced%20Breakout%20Board
- [S27] Reddit r/fightsticks, Brook UFB dimensions (search summary only): https://www.reddit.com/r/fightsticks/comments/xjx26d/brook_ufb_dimensions/
- [S28] Raspberry Pi Pico datasheet: https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf
- [S29] Ultimarc, Mini-PAC: https://www.ultimarc.com/control-interfaces/mini-pac-en/mini-pac/
- [S30] Ultimarc, Mini-PAC user guide: https://www.ultimarc.com/Mini-PAC%20Manual1.pdf
- [S31] GP2040-CE project site: https://gp2040-ce.info/
- [S32] Reddit r/cade, swappable control panels (search summary only): https://www.reddit.com/r/cade/comments/1ge71yc/do_many_people_here_have_swappable_control_panels/
- [S33] Sega New Astro City Serviceman Manual, No. 420-6294-01, pages 3 and 11: https://www.hard--candy.com/wiki/uploads/NewAstroCity/Downloads/NewAstroCity-Manual.pdf
- [S34] Hard*Candy wiki, New Astro City: https://www.hard--candy.com/wiki/candy/New_Astro_City
- [S35] ukVac forum, Sega candy cab CP height: https://www.ukvac.com/forum/threads/sega-candy-cab-cp-height.85435/
- [S36] Arcade-Projects, The perfect stool height for a candy cab: https://www.arcade-projects.com/threads/the-perfect-stool-height-for-a-candy-cab.19152/
- [S37] Arcade-Projects, Candy Cab Panel Scans (search summary): https://www.arcade-projects.com/threads/candy-cab-panel-scans.1850/
- [S38] ANSUR II public data, Penn State OPEN Design Lab: https://www.openlab.psu.edu/ansur2/
- [S39] OSHA Computer Workstations eTool, Monitors: https://www.osha.gov/etools/computer-workstations/components/monitors
- [S40] Arcade Art Shop, repro Sega Astro City 1L6B panel: https://www.arcadeartshop.com/product/repro-sega-astro-city-1-player-control-panel-with-overlay-1l6b/
- [S41] Reddit r/3Dprinting, modular arcade cabinet with magnetic swappable panels (search summary only): https://www.reddit.com/r/3Dprinting/comments/1ooiy7f/designed_a_modular_arcade_cabinet_with_magnetic/
