# BC-250 cooling layout, fan shroud, and the EVGA 1000 P5

Research date: 2026-11-09. All dimensions in millimetres.

This file extends `docs/research/hardware-envelopes.md` sections 2 to 6. It does not repeat them.
The board datum is the one defined there: x' from the I/O edge toward the power end, y' from the
straight long edge toward the stepped long edge, z' up from the PCB top face.

## Status tags

| Tag | Meaning |
| --- | --- |
| SOURCED | Stated by a manufacturer, author, seller or reviewer. The URL is given. |
| MEASURED-FROM-CAD | Measured with FreeCAD 1.1.4 (`Part.read`, `Mesh`) from a file. The path is given. |
| ESTIMATED | Derived by calculation, or read off a photo or a mesh section. The method is given. |

The measuring scripts were temporary and are not in the repository. Mesh files (STL, 3MF) were
measured by bounding box, by the area of axis-aligned facets at each level, and by plane sections.

## Summary

1. No existing shroud-only part fits this cabinet. Recommendation: design our own shroud in
   FreeCAD. Use the MKUU+ shroud interfaces (measured below) as the starting point.
2. The MKUU+ shroud puts the fan outer face 74.6 above the PCB top face, not 55.9. The value 55.9
   is the height of the printed part. The fan sits on top of that part.
3. The MKUU+ shroud sits at the far end of the board. It starts at about x' = 199 and overhangs
   the PCB end by about 23.
4. The board in the CAD generator is a mirror image of the real board. With the I/O edge at the
   left wall and the heatsink toward the rear door, the stepped long edge (with the 8-pin
   connector) is on top, not at the bottom. See "Board orientation".
5. Community tests in October 2026 report that the stock heatsink runs 10 to 20 C cooler with the
   power connectors up. The corrected layout has the connectors up.
6. The PSU has both screw patterns, takes a fan-up position, and its fan will probably stay off
   in ECO mode at BC-250 loads.

## Sources that were not accessible

| Source | Result |
| --- | --- |
| https://www.reddit.com/r/BC250Gaming/ (threads 1xa646x, 1xcjwge, 1vuuyl1) | INACCESSIBLE. Reddit returned "blocked by network security" with a log-in request. Only search-result summaries were read. |
| https://www.youtube.com/watch?v=r8UnINT2OwE (Old Lamer, board orientation) | Title and search summary only. No description or transcript was returned. |
| https://www.facebook.com/groups/862004790072960/posts/1110623591877744/ | Not opened. Log-in wall. |
| MakerWorld downloads (models 3200968, 3223412, 3342544, 2749412, 3021754) | Page text was readable. Files need sign-in. Not downloaded. |
| https://www.evga.com/products/product.aspx?pn=220-P5-1000-X1 and https://www.evga.com/articles/01506/evga-p5-psu/ | INACCESSIBLE. Both fetch methods received an empty page shell. The EVGA manual PDF and a retailer copy of the EVGA specification sheet were read instead. |
| Discord threads cited by the community guide ("Stock Cooler Fan Performance") | Not accessible. Only the guide's quotations were read. |
| Thingiverse pages (things 7172528, 7165679, 7199561, 7214884) | Search-result summaries only. |
| Google Drive folder linked from Printables 1808802 | Not opened. |
| No review of the 1000 P5 with a fan-speed table was found. | A Cybenetics report for the sister unit 1000 G5 was used as a stand-in. |

---

## Part A. Fan shrouds and cooling layouts

### A1. Cooling layouts in use

| Layout | Fan axis | Fins | Used by |
| --- | --- | --- | --- |
| L1. Top-down at the centre. Air enters opened fins over the APU and leaves at both ends. | Perpendicular to the PCB | Opened at the centre | Gadget Minimalist V3 and later, acevisai sleeve, Benis, zip-tie and tape mounts, Lanboy |
| L2. Top-down at the far end, far end closed. Air leaves at the I/O end only. | Perpendicular to the PCB | Opened under the shroud | MK-ULTRA Uno, MKUU+ |
| L3. Top-down push-pull: intake at the far end, exhaust fan near the I/O end. | Perpendicular to the PCB | Opened under both fans | ViRazY |
| L4. End plenum. The fan is on top of a plenum beyond the far end. Air turns 90 degrees and runs the full fin length. | Perpendicular to the PCB | Not modified | onemorecap shell and sleeve A, Lieben |
| L5. In-line end push. The fan stands beyond a board end and blows along the fins. | Parallel to the PCB | Not modified | nyacom, GedV, Alien, onemorecap sleeve B, ZMASLO |
| L6. Stock heatsink removed. Tower cooler, AIO, or a replacement heatsink in a wind tunnel. | Various | None | NexGen3D, Old Lamer, MandicReally Wind Tunnel, Gadget Quiet Case |

The cabinet needs the fan axis perpendicular to the PCB and the fan inside the board length. The
board leaves about 38 at the far end and about 52 at the I/O end (`cad/params/cabinet.csv`,
`inner_w` 398, `bc_x0`). That removes L4 and L5. L6 is outside the request. L1, L2 and L3 remain.

### A2. Candidates

Printables model pages and file lists were read through the Printables public API.

| # | Name, author | URL | License | Formats | Layout |
| --- | --- | --- | --- | --- | --- |
| 1 | BC250 Case MKUU+ fan shroud, derps (remix of morph91) | https://www.printables.com/model/1835961-bc250-case-mkuu-fsp-apevia-metalfish-psu | CC BY-NC-SA 4.0 | 3MF only | L2 |
| 2 | Yet Another BC-250 Fan Shroud, ViRazY | https://www.printables.com/model/1339540-yet-another-bc-250-fan-shroud | CC BY 4.0 | STL only | L3 |
| 3 | BC-250 Dual Fan Sleeve Shroud, acevisai | https://makerworld.com/en/models/3200968-bc-250-dual-fan-sleeve-shroud | CC BY-NC 4.0 | 3MF behind sign-in | L1 plus a rear fan |
| 4 | BC250 to ATX case adapter: single fan sleeve and low-profile mount, Gadget | https://www.printables.com/model/1743485-bc250-to-atx-case-adapter | CC BY-NC 4.0 | STL. STEP for the adapter only | L1 |
| 5 | BC-250 120mm Fan Shroud, strawberrygrl | https://makerworld.com/en/models/3223412-bc-250-120mm-fan-shroud | CC BY-NC 4.0 | 3MF behind sign-in | Not stated. 24 g of PETG |
| 6 | ASRock BC-250 cooling fan shroud (no fin mod needed), nyacom | https://www.printables.com/model/1710288-asrock-bc-250-cooling-fan-shroud-no-fin-mod-needed | CC BY-NC-SA 4.0 | STL, 3MF | L5 |
| 7 | BC250 stock fin air push shroud, Laurent Lieben | https://www.printables.com/model/1808802-bc250-stock-fin-air-push-shroud | CC0 | STEP | L4 |
| 8 | AMD BC-250 Cooling Fan Duct Shroud, GedV | https://www.printables.com/model/1850968-amd-bc-250-cooling-fan-duct-shroud | CC BY-NC 4.0 | 3MF | L5 |
| 9 | Cooling Fan Duct Shroud and Bellmouth Set, Alien | https://www.printables.com/model/1864736-amd-bc-250-cooling-fan-duct-shroud-and-bellmouth-s | CC BY-SA 4.0 | STEP, STL, F3D, 3MF | L5 |
| 10 | BC-250 Fan Sleeve/Adapter A and B, onemorecap | https://github.com/onemorecap/bc-250-sleeve-adapter | CC BY-NC-SA 4.0 | STEP | A: L4. B: L5 |
| 11 | AMD BC-250 Case ATX PSU and Fan Duct, ZMASLO | https://www.printables.com/model/1616167-amd-bc-250-case-atx-psu-fan-duct | CC BY-NC 4.0 | STL, STEP of the whole case | L5 |
| 12 | AMD BC-250 Cooling Solution, Benis | https://www.printables.com/model/1385007-amd-bc-250-cooling-solution | CC BY 4.0 | STL | L1, two fans, middle fins removed |
| 13 | Minimalist BC-250 Case, Gadget, and the mid-fan remix by Murat Serdar OZEL | https://www.printables.com/model/1581724-minimalist-bc-250-case and https://www.printables.com/model/1694403 | CC BY-NC 4.0 | STL | L1. Full case. The board stands on a long edge |
| 14 | The Lanboy, a BC250 portable arcade machine, Gadget | https://www.printables.com/model/1746364-the-lanboy-a-bc250-portable-arcade-machine | CC BY-NC 4.0 | STL | L1. Fan in the back panel over the middle fins |

Details for each candidate:

| # | Attachment | Fan position and height | Fin and bracket changes | Results and feedback | Access to 8-pin, M.2, I/O |
| --- | --- | --- | --- | --- | --- |
| 1 | Two slots grip the PCB long edges. One tab at the far end. No screws. | See A3. Fan face z' 74.6. | Fins opened under the shroud. The case instructions remove the I/O bracket; the shroud does not need that. | Author: opened fins plus stick-on heatsinks gave up to 10 C. One exhaust fan gave about 1 C. SOURCED (Printables 1835961). | All free. ESTIMATED from the sections in A3. |
| 2 | Clips on the PCB edges, plus screws in the holes of the two stock brackets. | 120 frame near the I/O end, 140 frame at the far end. Both seats at z' 30.5, so the fan face is at z' 55.5. MEASURED-FROM-CAD (`cad/vendor/shroud-virazy/bc250-shroud-front.stl`: rest faces at 0, hooks at -2.0, top at 30.5). | Fins partly opened under both fans. Uses the screw holes of both stock brackets. | 53 C idle, 65 C in games at 2000 MHz and 950 mV, two ARCTIC P fans, new MX-4. SOURCED (Printables 1339540). 785 downloads. | Fan cables run under the heatsink. Access not stated. |
| 3 | One band slides on from the I/O end and stops on the PCB step. Friction. | Centred over the APU. The 30 screw limit shows the fan sits almost on the fins. | Centre fins opened. Needs a 160 x 80 x 20 heatsink on the back. | "65 to 75 C under sustained load". One user: about 70 C in FurMark at 80 % fan, 40 CU. SOURCED (MakerWorld 3200968). | Window for the power connectors. CR2032 and M.2 stay accessible. SOURCED. |
| 4 | Four fan screws into the side holes of Gadget's ATX tray. | Low-profile mount is 132 x 145 x 49. MEASURED-FROM-CAD (`cad/vendor/shroud-gadget-atx-sleeve/Single_Fan_Mount_low_profile.stl`). | Opened fins assumed. | None stated. | Depends on the tray. |
| 6 | Fan plate at a board end. | Fan beyond the board end. Part is 55 x 116.5 x 130. MEASURED-FROM-CAD (`cad/vendor/shroud-nyacom-nofinmod/ASRock_BC-250-FAN-shroud-back-plate2.stl`). | None. | 56 to 58 C idle, about 75 C in games with a P12 Pro. SOURCED (Printables 1710288). | Free. |
| 7 | Sleeve over the board end, 32 high inside. | Fan on top, centre 62.5 from the closed end. Part is 124.5 x 162 x 55. MEASURED-FROM-CAD (`cad/vendor/shroud-lieben-air-push/venti2.stp`). | None. | None stated. Meant for push-pull. | Not stated. |
| 9 | Friction on the fin end. | In-line duct, 148.7 x 123.0 x 117.5. MEASURED-FROM-CAD (`cad/vendor/shroud-alien-duct/120mm_Fan_to_BC250_Guide.step`). | None. | 54 C in the BIOS screen with a low-speed San Ace fan. The author calls that not enough for normal use. SOURCED (Printables 1864736). | Free. |
| 10 | Two halves slide on. Friction, joined by the PSU or a plate. | Sleeve A: fan hole diameter 116.7, centre 43 beyond the board end. The sleeve reaches 113 beyond the board end. MEASURED-FROM-CAD (`cad/vendor/shroud-onemorecap-sleeve/bc-250-fan-sleeve-adapter-a2.step` and `bc-250-body.step`). | None. | Below 68 to 70 C at 150 W with the fan at 2200 rpm. SOURCED (GitHub README). | Free. |

Judgement for this cabinet:

| # | Fan can face the door, inside the board length | Exhaust steerable to the I/O end | Holds the fan sideways | Stack depth | Verdict |
| --- | --- | --- | --- | --- | --- |
| 1 MKUU+ | Yes. Overhangs the far end by about 23. 38 is free there. | Yes | Yes. The side walls bear on the fin block. | 74.6 | Works as a fallback. Mesh only. Sends part of the air round the board end into the cabinet. |
| 2 ViRazY | Yes | No. It needs a second fan as exhaust. | Yes | 55.5 | Good reference for a low stack. STL only. |
| 3 acevisai | Yes | No. Air leaves at both ends. | Yes | Not known | Two fans. Needs space behind the board. No file without sign-in. |
| 4 Gadget | Yes | No | Only on Gadget's tray | About 49 above the tray | Tied to another tray. |
| 5 strawberrygrl | Not known | Not known | Not known | Not known | No description. No file without sign-in. |
| 6 to 11 | No. The fan is beyond a board end or parallel to the board. | - | - | - | Do not fit. |
| 12 to 14 | Yes | No | Part of a full case | - | Layout references only. |

### A3. The MKUU+ shroud, measured

File: `cad/vendor/mkuu-plus-case/BC250_Case_MKUU_Plus_FSP_Version.3mf`. Objects
`heatsinkShroudAir 25mm.stl` and `heatsinkShroudAir 30mm.stl`. The "original" variant
(129.30 long, same heights, same fan opening) was not sectioned. The part is a tray that is
printed plate-down and fitted plate-up. The closed end goes to the far end of the board: the page
puts the shroud at "the side where cmos battery is".

| Feature | Value | Status |
| --- | --- | --- |
| Outer size | 131.35 x 129.00 x 55.90 (25 fan) and 50.90 (30 fan). 123.0 wide without the clip ribs. | MEASURED-FROM-CAD |
| Fan plate | 2.0 thick. Opening diameter 115.0. Four fan holes on 105 x 105. | MEASURED-FROM-CAD |
| Fan opening centre in the tray | 2.5 toward the far end from the tray centre, 1.0 off the centre line | MEASURED-FROM-CAD |
| Clear width between the side walls | 119.0. Walls 2.0 thick. | MEASURED-FROM-CAD. The Mandic fin block is 119.5 wide. Measure the real fin block. |
| Fan position | The fan is outside the tray, on the plate. A 120 fan does not fit in 119.0. The 30 version is 5.0 lower, so the fan outer face stays at one height. | ESTIMATED from the two variants and the clear width |
| PCB edge slots | 2.2 high, 2.0 deep, in both side walls, over the last 7.2 at the I/O-side end. The wall tip is the upper slot face. | MEASURED-FROM-CAD (sections at tray x = -63 and -60) |
| Fan seat above the PCB top face | 49.6 (25 fan), 44.6 (30 fan). Up to 0.65 more: the slots are 0.65 higher than the 1.55 PCB. | MEASURED-FROM-CAD, with the wall tips on the PCB top face |
| Fan outer face above the PCB top face | 74.6 for both variants (74.6 to 75.3 with the slot play) | MEASURED-FROM-CAD plus the fan thickness |
| Air space between fin tops and plate | 21.5 (25 fan), 16.5 (30 fan) | MEASURED-FROM-CAD plus `bc_fin_h` 26.1 |
| I/O-side end | Open. A wedge hangs 13.4 below the plate. It leaves a slot 8.1 high above the fin tops. | MEASURED-FROM-CAD |
| Side posts at the I/O-side end | Two posts, 2.5 wide, inside the side walls, down to z' 24.7. With fins 119.5 wide and 26.1 high they would cut 1.4 into the fin block. So the real fin block is narrower than 114 at the top, or lower than 25.4 at its edges. | MEASURED-FROM-CAD (posts). ESTIMATED (conclusion). Measure the fin block. |
| Far end | Closed. The wall curves under the board end. A centre tab 10 wide has a slot 3.1 high and 3.9 deep. | MEASURED-FROM-CAD |
| Position along the board | Tray from x' 199.1 to 330.5. Fan centre x' 267.3. Fan from x' 207.3 to 327.3. Clips from x' 199.1 to 206.3. | ESTIMATED: the centre tab stops on the PCB end at x' 307.6. Check: the clips then end 1.1 before the PCB step at 207.4, and the fan starts at the step. |
| Position across the board | Centred on the fin block, y' 0.05 to 123.05. Clip ribs to y' -2.95 and 126.05. | ESTIMATED: the walls enclose the fin block |

This replaces the estimate "about 53" in `docs/research/hardware-envelopes.md` section 4. The
parameter `bc_shroud_h` = 55.9 in `cad/params/hardware.csv` is the part height, not the fan face.
Only 79 of the 120 fan width is over fins. The rest of the air goes over the far end of the PCB
and round the board end to the backplate. This agrees with the author's text: "directs airflow in
3 ways".

### A4. Board orientation

**The generator places a mirror image of the board.** `cad/candybar/hardware.py`, as read on
2026-11-09, rotates the board datum by -90 degrees about X. The datum is left-handed: `hardware-envelopes.md` defines
y' = 71.83 - Y of the model. A rotation of a left-handed frame gives a mirrored part.

Check on the real geometry:

| Fact | Status |
| --- | --- |
| In the model the I/O edge is at X = -153.0, the straight edge at Y = +71.83, the PCB step at X = 54.4 toward Y = -72.17, the 8-pin header at X 71.6 to 90.0, Y -72.0 to -59.5, and the heatsink at +Z. | MEASURED-FROM-CAD (`cad/vendor/mandic-bc250-board/BC250_Completeish_V1.step`) |
| With model +X to cabinet +X (I/O at the left wall) and model +Z to cabinet +Y (heatsink to the rear), model +Y goes to cabinet -Z. The straight edge is down. The 8-pin header is up. | ESTIMATED: R(Y) = R(Z) x R(X) = (+Y) x (+X) = -Z |
| The onemorecap shell has its 8-pin opening on the -Y wall with the I/O end at -X and the fan on +Z. Same handedness. | MEASURED-FROM-CAD (`hardware-envelopes.md` section 3) |
| The connector list in the hardware reference "proceeds around the board clockwise from the M.2 header". The datum positions of M.2, jumpers, fan headers, J2000, J1000 give that order only with the straight edge at the top when the I/O edge is at the left, seen from the heatsink side. | SOURCED https://github.com/mothenjoyer69/bc250-documentation/blob/main/hardware.md |

Effects in the cabinet, with the I/O edge at the left wall and the heatsink toward the door:

- The 144-wide part and the 8-pin plug zone are at the top. The plug enters from above.
- The straight edge faces the PSU. No plug stands in the PSU fan air.
- The fan centre and the vent heights must be counted up from the lower edge:
  z = `bc_bottom_z` + y'.
- The PCIe lead must reach the top edge of the board.

**Heat pipes and gravity.** The stock heatsink has heat pipes. Reports from October 2026:

| Report | Status |
| --- | --- |
| "power connectors UP or backplate-DOWN flat run cooler, connectors DOWN run hotter". Rotating a running board by 180 degrees moved the temperature by about 10 C. Still called an open question. | SOURCED https://github.com/katzzero/bc250-unofficial-community-guide/blob/main/04-cooling-guide.md (capt.cat_13, 13/10/2026) |
| Untouched stock heatsink, Superposition Extreme: 61 C upside down, 83 C right side up, scores equal. A second board: 63 C and 84 C. | SOURCED, same page (dominic61, 13 and 16/10/2026) |
| Counter-examples: no difference on boards with other coolers. Heatsink revisions and board voltages differ. | SOURCED, same page |
| Gadget released a "Reverso" case revision on 25-oct-2026 that runs "with the PSU and connectors upward in order to improve heatpipes position". In that case the board stands on a long edge. | SOURCED https://www.printables.com/model/1581724-minimalist-bc-250-case |
| With the connectors up the heat pipes are in a "UU" position and gravity helps them. | SOURCED, search summary of https://www.reddit.com/r/BC250Gaming/comments/1xcjwge/ (page not accessible) |

The corrected cabinet layout has the connectors up. That is the position these reports prefer.
Do not mirror the cabinet to put the I/O edge at the right wall: that would put the connectors down.

### A5. Other evidence used for the design rules

| Evidence | Status |
| --- | --- |
| "Single fan in center = best for most builds." A second fan beside the first makes a dead zone over the APU. | SOURCED (katzzero guide, community advice) |
| Gadget moved the fan to the centre "so you don't have to strip side fins (only center ones)". | SOURCED (Printables 1581724, 25-jul-2026) |
| Opening only the centre keeps the air fast over the hot part. No measurement published. | SOURCED (katzzero guide, land_and_air, 02/10/2026) |
| Open fins only under the shroud. Keep the first and last two fins. | SOURCED (Printables 1835961) |
| A P12 taped to the opened fins with aluminium tape: 75 to 62 C in one game. | SOURCED (katzzero guide, widdlemama, 09/06/2026) |
| "second fan doesnt add that much more cooling". "One fan will give you 80% of the performance". | SOURCED (katzzero guide, hojnikb and holde) |
| One-way flow through the full length of unmodified fins, one P12 Pro PST, FurMark, 28 C room, 40 CU at 1500 MHz: CPU 84.1, GPU 84.0, backplate 47 C, 51 dB at 300. The low-noise P12 Pro PST LN reached 99 C and the test was stopped. | SOURCED https://www.printables.com/model/1737913 (nyacom fan comparison) |
| Stock heatsink with two P12 Max in push-pull, 10 minutes at 40 CU and 2 GHz: GPU 89.6 C average, 136 W average. "The stock heatsink is the limiter, not the fans." | SOURCED https://elektricm.github.io/amd-bc250-docs/hardware/cooling/ |
| Heatsink variant C is 8 to 9 C cooler than variant B in FurMark. | SOURCED (katzzero guide, serverror, 13/09/2026) |
| Fan curve in use: 30 % at 40 C, 50 % at 60 C, 75 % at 70 C, 100 % at 80 C. | SOURCED (katzzero guide) |
| The main fan is `pwm2` on the NCT6686D. Control needs the `nct6687` module. | SOURCED (elektricM cooling page) |
| Material: "Tg 80C or higher, PLA not recommended" (MKUU+). "PETG, ABS or ASA, this part hugs a hot heatsink; PLA will creep" (acevisai). PETG-GF and PETG-CF (Gadget). | SOURCED (the pages above) |
| The GDDR6 on the underside has no sensor before BIOS P3.00. A heatsink or airflow on the backplate is advised after the 40 CU unlock. | SOURCED (katzzero guide) |
| P12 Pro pressure at reduced speed: 3.1 mmH2O at 2000 rpm, 1.7 at 1500, 0.8 at 1000. | ESTIMATED: 6.9 mmH2O at 3000 rpm, pressure in proportion to speed squared |
| Exhaust air is about 15 K above the intake at 200 W and 40 m3/h. | ESTIMATED: dT = P / (1.2 x 1005 x Q) |

### A6. Recommendation

Design our own shroud as a FreeCAD part of this project. Reasons:

1. The existing shroud-only parts that keep the fins closed need 55 to 115 beyond a board end, or
   turn the fan parallel to the board. The cabinet has 38 at the far end, and the fan must face
   the door.
2. The existing top-down parts do not steer the exhaust (ViRazY, acevisai, Gadget), except MKUU+.
   MKUU+ is a mesh, stands 74.6 high, and sends part of its air into the cabinet.
3. The cabinet adds three needs that no part has: a seal between fan and door grille, a closed
   path from the fin exit to the side vent, and a fan held with its axis horizontal.

MKUU+ printed unchanged is the fallback. It is known to work on the first console. Its license
(CC BY-NC-SA 4.0) permits a private remix, but a mesh is hard to change.

Design rules:

| Topic | Rule | Basis |
| --- | --- | --- |
| Flow direction | One way. Close the far end of the fin block with a wall. All air leaves at the I/O end. | MKUU+ layout. The exhaust must reach the left vent. |
| Fan position along the fins | Whole fan over the fin block, far edge of the fan at the end of the fin block: x' 166.7 to 286.7. The APU centre (x' 172.2) is under the downstream edge. | ESTIMATED. No test compares positions. This keeps the fan upstream of the APU (MKUU+), as near to the centre as one-way flow allows (community rule), with no overhang. |
| Opened fins | Open the fin tops only inside the shroud, x' 168.7 to 284.7. Keep two fins closed on each side. | SOURCED (Printables 1835961) |
| Corner without fins | The fin block has a notch at x' 242.25 to 286.68, y' 1.8 to 30.8. Close it with a floor at fin-top height. | MEASURED-FROM-CAD (`hardware-envelopes.md` section 2). Otherwise the air leaves through the notch. |
| Air space above the fins | 10 as the first value. Make it a parameter. 1.4 (ViRazY) and 21.5 (MKUU+) both work. | ESTIMATED. No test compares heights. |
| Seal to the fins | Side walls 0.25 clear of the fin block sides. 3 thick closed-cell foam on the fin tops at the downstream wall. | ESTIMATED. Measure the real fin block first. |
| Seal to the door | A foam ring between the fan face and the door, compressed to the 5 gap (`bc_gap_door`). The fan must draw outside air only. | ESTIMATED |
| Door grille | At least 70 % open. No solid part within 12.7 of the fan inlet. | `hardware-envelopes.md` section 5 |
| Attachment | PCB edge slots like MKUU+ (2.2 high, 2.0 deep) at x' 199 to 206, both edges. Add two screws into the board tray. The fan weight (183 g) acts across the board; the side wall on the fin block takes it. | MEASURED-FROM-CAD (A3) and ESTIMATED |
| Exhaust path | A hood over the I/O zone from the fin exit (x' 47.14) to the left wall, roof 2 above the fin tops, foam at the wall. One foam-lined notch for the DisplayPort, USB and network cables. | ESTIMATED. The fin exit is 119.5 x 26.1. The hood is 124 x 28 inside. |
| Side vent | Free area of the part behind the hood at least 30 cm2. | ESTIMATED: 1.5 times the free area of the fin exit, taken as 65 % of 31 cm2 |
| Second fan | None at the exhaust. | SOURCED: about 1 C (Printables 1835961) |
| Backplate and far end of the PCB | No forced air reaches them in this layout. Keep the 10 gap behind the backplate open at top and bottom. Add a closable bleed slot of about 5 cm2 in the far-end wall only if tests need it. | ESTIMATED. MKUU+ sends air there. |
| Fan speed | Use the standard P12 Pro, not the LN type. Let the curve reach 100 % at 80 C. | SOURCED (nyacom comparison) |
| Material | PETG is the community standard for this part. Put no clip under load against the heatsink base. Bear on the PCB, the fin tops near the inlet, and the tray. | SOURCED (A5) and ESTIMATED |

### A7. Numbers for the CAD

Board datum. Option A is the recommended own design. Option B is MKUU+ as printed.

| Parameter | Option A | Status | Option B | Status |
| --- | --- | --- | --- | --- |
| Shroud start along x' | 164.0 | ESTIMATED: fan 166.7 less 0.3 clearance and a 2.4 wall | 199.1 | ESTIMATED (A3) |
| Shroud length along x' | 125.4, to x' 289.4 | ESTIMATED: far wall 2.4 thick behind the fin block end at 286.68 | 131.35, to x' 330.5 | MEASURED-FROM-CAD |
| Shroud offset in y' | -3.0 | ESTIMATED: same clip ribs as MKUU+ | -2.95 | ESTIMATED (A3) |
| Shroud width in y' | 129.0. Body 123.0, y' 0.05 to 123.05. | ESTIMATED from MKUU+ | 129.0 | MEASURED-FROM-CAD |
| Fan centre (x', y') | (226.7, 61.55) | ESTIMATED | (267.3, 61.55 plus or minus 1.0) | ESTIMATED (A3) |
| Fan seat above the PCB top face | 38.1 | ESTIMATED: 26.1 fins + 10.0 air + 2.0 plate | 49.6 | MEASURED-FROM-CAD |
| Fan outer face above the PCB top face | 63.1 | ESTIMATED: seat + 25.0 | 74.6 to 75.3 | MEASURED-FROM-CAD |
| Value to reserve for `bc_shroud_h` | 76.0 until the air space is fixed by a test. It also admits Option B. Lowest possible value: 56.0 (air space 2.9; ViRazY reaches 55.5). | ESTIMATED | 76.0 | ESTIMATED: 75.3 plus margin |
| Space beyond the PCB far end | 0 | - | 22.9 | ESTIMATED (A3) |

Extra keep-out zones for Option A:

| Zone | Box in the board datum | Status |
| --- | --- | --- |
| Exhaust hood | x' from the left wall (-52.2 with the present `bc_dp_clear`) to 57.1, y' -3.0 to 125.2, z' 0 to 30.1 | ESTIMATED: 10 overlap on the fin block, 2.4 walls, 2.0 roof, 2.0 above the fin tops |
| Cable notch in the hood | 40 x 16, in the hood wall on the straight long edge (the lower edge in the cabinet), near x' -25 | ESTIMATED |
| Door seal | Ring, 116 inside, 140 outside, 5 thick, on the fan outer face | ESTIMATED |
| Fan cable | Channel 10 x 10 from the fan corner at (286.7, 121.5) to the fan headers at x' 286.5 to 302.2, y' 119.8 to 141.3. Stow 400 of cable in 40 x 25 x 12 at x' 290 to 307. | ESTIMATED. Header positions MEASURED-FROM-CAD (`hardware-envelopes.md`). |
| 8-pin plug | No change in the datum. The shroud ends at y' 126.0. The header starts at y' 131.3. | MEASURED-FROM-CAD |
| Power button | Inside the hood at y' 18.6 to 27.0. Not reachable. The board starts by itself when power is applied (AUTO_PWRON1 default). | SOURCED (`hardware-envelopes.md`) |
| CR2032 | Under the notch floor. Remove the shroud to change it. | ESTIMATED |

### A8. Downloads

Nothing from these files was executed. No `.FCStd` file was opened.

| Path | Source | License | SHA-256 |
| --- | --- | --- | --- |
| `cad/vendor/shroud-lieben-air-push/venti2.stp` | https://www.printables.com/model/1808802-bc250-stock-fin-air-push-shroud (file 7555823) | CC0 | `33b7c6fa8332194357dd53892e37033ffb597a51d8b2053f1f3c47e53e67a5c4` |
| `cad/vendor/shroud-alien-duct/120mm_Fan_to_BC250_Guide.step` | https://www.printables.com/model/1864736-amd-bc-250-cooling-fan-duct-shroud-and-bellmouth-s (file 7791187) | CC BY-SA 4.0 | `ff1470cf20a8e211474813e26bad4251865885787389f53d73ae2b73f319e95f` |
| `cad/vendor/shroud-alien-duct/120mm_Fan_to_BC250_Guide_Strato_Pin_Guide_Vane.step` | same model (file 7949313) | CC BY-SA 4.0 | `c6e1c765fa08969aa47773fd5eb7283c0cb035b776b112644f4dfa9e63476a7e` |
| `cad/vendor/shroud-alien-duct/120mm_Fan_to_BC250_Guide_Insert_Ring.stl` | same model (file 7791185) | CC BY-SA 4.0 | `e9f1230e2b5d4ae0f1e9e7abb064856177038aea82f2aebf31bebadf19aadbc0` |
| `cad/vendor/shroud-nyacom-nofinmod/ASRock_BC-250-FAN-shroud.3mf` | https://www.printables.com/model/1710288-asrock-bc-250-cooling-fan-shroud-no-fin-mod-needed (file 7139766) | CC BY-NC-SA 4.0 | `05b26da99b0ce0017bb30368abfa36f18da04adac313e82b6ce51448b07ed827` |
| `cad/vendor/shroud-nyacom-nofinmod/ASRock_BC-250-FAN-shroud-back-plate.stl` | same model (file 7139765) | CC BY-NC-SA 4.0 | `297566f47dfb941ad225aaa3570af02ec7786788d860f449512bc1e61dd492b0` |
| `cad/vendor/shroud-nyacom-nofinmod/ASRock_BC-250-FAN-shroud-back-plate2.stl` | same model (file 7139764) | CC BY-NC-SA 4.0 | `137ccacaa531be1b8541d82cb8d84c691078dd2d30178b7c11b300fbdef7da18` |
| `cad/vendor/shroud-virazy/bc250-shroud-front.stl` | https://www.printables.com/model/1339540-yet-another-bc-250-fan-shroud (file 5633920) | CC BY 4.0 | `47d7cbc62eb88cd391952bfc9574e564fb3c37d0e74a43e20a48affdb6ac2297` |
| `cad/vendor/shroud-virazy/bc250-shroud-rear.stl` | same model (file 5633921) | CC BY 4.0 | `de113afb3b8e0fa8d88130e718b181e120e396d460ce639c55c970d48667f2f0` |
| `cad/vendor/shroud-gadget-atx-sleeve/Single_Fan_Sleeve.stl` | https://www.printables.com/model/1743485-bc250-to-atx-case-adapter (file 7569751) | CC BY-NC 4.0 | `cde82ebe7d106c9a64c58f05507d7cc37baf19b590e5991a36a8eb97cb8cb77f` |
| `cad/vendor/shroud-gadget-atx-sleeve/Single_Fan_Mount_low_profile.stl` | same model (file 7787928) | CC BY-NC 4.0 | `742ba33cc7978da1f1db747690325e7d0cf4d43792f7e527b303a4dfb8e8bd88` |
| `cad/vendor/shroud-gadget-atx-sleeve/ATX_Adapter.step` | same model (file 7288375) | CC BY-NC 4.0 | `7cb4a835bba840a2f844159fe4366a7cd86f75a3eef9cc050897f947a4582ef9` |
| `cad/vendor/shroud-onemorecap-sleeve/bc-250-fan-sleeve-adapter-a1.step` | https://github.com/onemorecap/bc-250-sleeve-adapter at `05162a8defdb44d7fdbedbcde4e7c421df18c950` | CC BY-NC-SA 4.0 | `d78f9bf76f7c48ce78b911833b805f32b2ec423e991ede0e4bfe29ae7c966f9f` |
| `cad/vendor/shroud-onemorecap-sleeve/bc-250-fan-sleeve-adapter-a2.step` | same commit | CC BY-NC-SA 4.0 | `753f59cc3c7de4c1fad67a65bb2c52eee2287182d3a1faf5460ab2ecad53d0d0` |
| `cad/vendor/shroud-onemorecap-sleeve/bc-250-fan-sleeve-adapter-b1.step` | same commit | CC BY-NC-SA 4.0 | `b5f6d02ce9f5a016df15c0e1d20a5d3fec035038b206606997323613d1706926` |
| `cad/vendor/shroud-onemorecap-sleeve/bc-250-fan-sleeve-adapter-b2.step` | same commit | CC BY-NC-SA 4.0 | `e7db628789a1ec720f8f1305ebde58ea33bdc28e731038f7eaad8519a6ded254` |
| `cad/vendor/shroud-onemorecap-sleeve/bc-250-body.step` | same commit | CC BY-NC-SA 4.0 | `10b727fa35ba6691b7137d320e6c20355389e02d2ee9e0b9dc6d216be813f071` |
| `cad/vendor/shroud-onemorecap-sleeve/lop-300-dummy-plate.step` | same commit | CC BY-NC-SA 4.0 | `c22242f9af28198944f3513baf16f46dcd805de3c658deec7035984e78f6e731` |
| `cad/vendor/shroud-onemorecap-sleeve/README.md` | same commit | CC BY-NC-SA 4.0 | `a133a501d84d5b4e772fd664e33a68f013bbbdda13fb2168f038a3f92a1c9a6f` |

The Printables files were saved with underscores in place of spaces. `cad/vendor/` is ignored by
git. `cad/tools/fetch_vendor.sh` does not fetch these files yet.

Bounding boxes, all MEASURED-FROM-CAD:

| File | Size |
| --- | --- |
| `shroud-lieben-air-push/venti2.stp` | 124.5 x 162.0 x 55.0, one solid |
| `shroud-alien-duct/120mm_Fan_to_BC250_Guide.step` | 148.7 x 123.0 x 117.5, three solids |
| `shroud-alien-duct/120mm_Fan_to_BC250_Guide_Strato_Pin_Guide_Vane.step` | 123.0 x 123.0 x 63.7, four solids |
| `shroud-nyacom-nofinmod/ASRock_BC-250-FAN-shroud-back-plate.stl` | 58.0 x 155.2 x 130.0 |
| `shroud-nyacom-nofinmod/ASRock_BC-250-FAN-shroud-back-plate2.stl` | 55.0 x 116.5 x 130.0 |
| `shroud-virazy/bc250-shroud-front.stl` (120 fan) | 129.0 x 132.0 x 35.0 |
| `shroud-virazy/bc250-shroud-rear.stl` (140 fan) | 151.0 x 147.5 x 35.0 |
| `shroud-gadget-atx-sleeve/Single_Fan_Sleeve.stl` | 131.5 x 145.0 x 76.0 |
| `shroud-gadget-atx-sleeve/Single_Fan_Mount_low_profile.stl` | 132.0 x 145.0 x 49.0 |
| `shroud-gadget-atx-sleeve/ATX_Adapter.step` | 171.0 x 248.5 x 82.0, four solids |
| `shroud-onemorecap-sleeve/bc-250-fan-sleeve-adapter-a1.step` and `-b1.step` | 45.0 x 148.0 x 40.9 |
| `shroud-onemorecap-sleeve/bc-250-fan-sleeve-adapter-a2.step` | 170.0 x 148.0 x 40.9 |
| `shroud-onemorecap-sleeve/bc-250-fan-sleeve-adapter-b2.step` | 149.0 x 148.0 x 124.05 |
| `shroud-onemorecap-sleeve/bc-250-body.step` | 310.0 x 144.0 x 31.9, 21 solids |

### A9. Board models

| Model | URL | License | Formats | Note |
| --- | --- | --- | --- | --- |
| MandicReally Complete-ish V1 (in use) | https://www.printables.com/model/1828755-asrock-bc250-complete-ish-cad-model | CC BY-NC-SA 4.0 | STEP, F3D | Still V1, dated 2026-09-06. Also on MakerWorld (model 3250483). |
| torassk "Accurate 3D model" | https://www.printables.com/model/1341336-accurate-3d-model-of-the-amd-bc-250-board | Standard Digital File License | STEP 137 kB, STL | Simple. Most downloaded. |
| Joseph Prust "AMD BC-250 STEP File" | https://www.printables.com/model/1537364-amd-bc-250-step-file | CC BY-NC-ND 4.0 | STEP 128 kB | Simple. |
| Fahad_Alduraibi "Accurate dimensions" | https://www.printables.com/model/1651082-amd-bc-250-model-accurate-dimenstions | CC BY-SA 4.0 | STL, 3MF, OpenSCAD | Envelope model. |
| castor "AMD BC250 Board" | https://www.printables.com/model/1103626-amd-bc250-board | CC BY-SA 4.0 | STL | Mesh only. |
| onemorecap `bc-250-body.step` | https://github.com/onemorecap/bc-250-sleeve-adapter | CC BY-NC-SA 4.0 | STEP | Mock-up, 310 x 144 x 31.9. Now in `cad/vendor/shroud-onemorecap-sleeve/`. |

No model is clearly better than the MandicReally STEP. None was downloaded for that purpose. No
public ASRock CAD was found. One author states that he used "ASRock's own board CAD data" and that
"the physical PCB is wider than the CAD outline at the connector end" (SOURCED, MakerWorld
3200968). Measure the PCB width at the power end before the tray is printed.

---

## Part B. EVGA SuperNOVA 1000 P5 (220-P5-1000-X1)

Sources:

- S1: EVGA specification sheet, retailer copy:
  https://cdn.cyberpuerta.mx/storage/articles/multimedia/220P51000X1.pdf
- S2: EVGA user manual: https://www.evga.com/support/manuals/files/220-P5-1000-X1.pdf
- S3: retailer product photos:
  https://c1.neweggimages.com/productimage/nb1280/17-438-222-V07.jpg (rear face),
  `...-V80.jpg` (fan face, socket face, size arrows), `...-V06.jpg` (side)
- S4: Cybenetics report for the EVGA SuperNOVA 1000 G5, the Gold unit of the same 150 series:
  https://www.cybenetics.com/evaluations/psus/811/pdf/
- S5: https://elektricm.github.io/amd-bc250-docs/hardware/power/ and
  https://github.com/mothenjoyer69/bc250-documentation/blob/main/hardware.md

| Item | Value | Status |
| --- | --- | --- |
| Case size | 86 high x 150 wide x 150 long | SOURCED (S1, S2). S3 shows 3.40 x 5.90 x 5.90 inches. |
| Weight | 7.2 lb (3.27 kg) "net weight" | SOURCED (S1). It probably includes the cables. Weigh the unit. |
| Output | 1000 W at 50 C. 12 V, 83.3 A. Operating range 0 to 50 C. | SOURCED (S1) |
| Efficiency | 92 % at 115 V under typical load | SOURCED (S1) |
| Fan | 135 fluid dynamic bearing. In the 150 x 150 face opposite the circuit board. | SOURCED (S1, S2), face from S3 |
| Fan centre | Within about 5 of the centre of the 150 x 150 face | ESTIMATED from photo S3 (V80) |
| Air path | In through the fan face, out through the honeycomb rear face | ESTIMATED from S3 and the usual ATX layout |
| ECO switch | Slide switch on the rear face, beside the mains rocker | SOURCED (S2: "a simple switch directly on the power supply"), position from S3 (V07) |
| ECO mode | The fan is off "during low to moderate operation loads" and starts "based on the loading". With ECO off the fan always turns. No wattage is published. | SOURCED (S2) |
| ECO mode, sister unit 1000 G5 | Fan at 0 rpm at 100 W and at 200 W. 1286 rpm at 300 W. Intake air 41 to 46 C. | SOURCED (S4) |
| Fan at BC-250 loads | Probably off up to about 200 W. It may start near the 235 W peak or in a warm cabinet. | ESTIMATED from S4. The P5 loses less heat than the G5. |
| Heat from the PSU | About 12 to 17 W at 100 W output, about 20 to 25 W at 200 W | ESTIMATED: 87.6 % and 90.6 % measured on the G5 (S4); Platinum is about 2 points better |
| Mounting position | "Recommended ... fan facing down." Fan up is named for a case with no vent below. | SOURCED (S2) |
| In the box | PSU, 4 screws, 24-pin PSU tester, cables, mains cord | SOURCED (S2) |

Rear face. Frame: seen from outside, fan up as in the cabinet, origin at the lower left corner,
x to the right, z up. All ESTIMATED from photo S3 (V07), scaled to 150 x 86 and turned by 180
degrees, because the photo shows the fan-down position.

| Feature | Position |
| --- | --- |
| IEC C14 inlet | x 88 to 119, z 34 to 57. Centre (103.5, 45.5). |
| Mains rocker switch | x 128 to 142, z 35 to 55. Centre (135, 45). |
| ECO slide switch | x 128 to 142, z 21 to 31. Centre (135, 26). Below the rocker. |
| "E" logo LED | Centre (102.5, 66). Above the inlet. |
| Vent | Honeycomb over the rest of the face, mainly x 0 to 88 |
| Screw holes | The standard ATX pattern of `hardware-envelopes.md` section 6 is present, and so is the same pattern turned by 180 degrees: (144, 6), (6, 6), (144, 70), (30, 80) in the fan-down frame. The manual says "more than four screw holes". A wall drilled to the standard pattern fits the unit fan up or fan down. Confirm the hole at (30, 80) on the unit. |

Modular socket face. Frame: seen from the front, fan up. ESTIMATED from photo S3 (V80).

| Row | Sockets, left to right |
| --- | --- |
| Upper row | Blank area with the logo, then MB (18-pin and 10-pin), CPU2 (8), SATA3 (6), SATA2 (6) |
| Lower row, next to the underside | VGA4 (8), VGA3 (8), VGA2 (8), VGA1 (8), CPU1 (8), PERIF (6), SATA1 (6) |

- The sockets cover almost the full 150 width and about the lower 10 to 50 of the 86 height. The
  band next to the fan face is blank. ESTIMATED from the photo. Keep `psu_plug_h` = 86 until the
  unit is measured.
- Four VGA sockets serve five PCIe leads. SOURCED (S2 cable table), socket count from S3.
- The 24-pin lead has 28 pins at the PSU end. SOURCED (S2, German Q and A). The MB socket is two
  sockets, 18-pin and 10-pin. ESTIMATED from photo S3.

Cables (S1 for lengths, S2 for counts):

| Lead | Count | Length | Connectors |
| --- | --- | --- | --- |
| ATX 24-pin | 1 | 600 | 1 |
| PCIe 8-pin (6+2), single | 2 | 700 | 1 each |
| PCIe 8-pin (6+2), double | 3 | 700 to the first, 850 to the second | 2 each |
| EPS 8-pin (4+4) | 2 | 700 | 1 each |
| SATA | 3 | 550 to 850 | 4 each |
| Four-pin peripheral | 1 | 550 to 850 | 4 |
| Mains cord | 1 | 1500 | - |

Wire gauge is not stated. The BC-250 documentation asks for 16 AWG and reports melted 18 AWG
leads (SOURCED, S5). Read the gauge printed on the PCIe lead.

### Starting the PSU without a motherboard

1. Fit the 24-pin lead to the two MB sockets of the PSU. PS_ON exists only on that lead.
2. Fit the EVGA tester, or any 24-pin bridging plug, on the free end. It joins PS_ON (pin 16,
   green) to a ground pin. SOURCED (S2 installation step 2; S5 "Method 3").
3. Fit one single PCIe lead from a VGA socket to J1000 on the BC-250.
4. The rear rocker switch then switches the 12 V output. The board starts by itself when 12 V
   appears (AUTO_PWRON1 pins 1-2, the default). SOURCED (S5).

Without the 24-pin lead the PSU stays in standby. A latching switch across PS_ON and ground,
in place of the fixed bridge, gives a power switch that does not carry mains.

J1000 "is a standard 8-pin PCIe connector". A standard PCIe 6+2 lead fits. One 8-pin plug has
three 12 V contacts of up to 9 A each. SOURCED (S5, both pages). At 235 W each contact carries
6.5 A. ESTIMATED: 235 / 12 / 3.

### Fan up, in a closed cabinet, 25 below another part

| Point | Status |
| --- | --- |
| Fan up is a permitted position. | SOURCED (S2) |
| 25 above the fan face is twice the 12.7 minimum of the ATX guide. | `hardware-envelopes.md` section 6 |
| With ECO on, the fan is off most of the time. The heat (about 12 to 25 W) rises out of the fan grille into the cabinet. The cabinet needs a vent high up. | ESTIMATED |
| With ECO off, the fan always turns. It draws cabinet air down and pushes it out of the rear face. That gives the cabinet, and the back of the BC-250, a steady exhaust. | ESTIMATED. Compare both switch positions in a test. |
| Screws and dust can fall into an upward fan. Fit a mesh or work with care. | ESTIMATED |
| The rear wall needs an opening for the whole 150 x 86 face: vent, inlet, rocker and ECO switch. | ESTIMATED from S3 |

### Effects on the cabinet layout

1. Correct the mirrored board first (A4). The 8-pin plug zone moves to the top edge.
2. The single PCIe lead is 700 long. From a VGA socket on the lower row to the top edge of the
   board is about 86 + 27 + 144 = 257 of height plus the horizontal run. Check the route against
   700. ESTIMATED.
3. `psu_d` = 150 is confirmed. SOURCED (S1).
4. `bc_shroud_h`: reserve 76.0, or 63.1 if Option A with 10 air space is accepted. `cab_d` and
   `bc_pcb_y` follow.
5. Option B needs 22.9 beyond the PCB far end. 38 is free.
6. Count `vent_fan_z` and `vent_out_z0` up from `bc_bottom_z`.
7. The hood changes the left vent: the part behind the hood is the BC-250 exhaust.
8. The rocker and ECO switches are at the right-hand end of the rear face, seen from behind,
   with the fan up.

---

## Must measure or decide

On the first console (MKUU+):

1. PCB top face to the fan outer face. Expected 74.6 to 75.3.
2. I/O edge of the PCB to the near wall of the shroud. Expected 199. Overhang beyond the PCB end.
   Expected 23.
3. Extent of the opened fins along x' and across y'.
4. Temperatures in one fixed game, with the board flat and with the board on its long edge,
   connectors up and connectors down.

On the second board:

5. Fin block width and length. Height of the fin tops above the PCB.
6. Heatsink variant (QR code beside the 8-pin header), fin-top condition.
7. PCB width at the power end.

On the PSU:

8. Weight of the bare unit.
9. Rear face: inlet, rocker, ECO switch and all screw holes, against the estimates above.
10. Socket face: height of both socket rows above the underside, fan up.
11. Wire gauge and real length of the single PCIe lead.
12. Load at which the fan starts with ECO on.

Decisions:

13. Own shroud (Option A) or MKUU+ unchanged (Option B).
14. Air space above the fins: 10 as proposed, or 21.5 as on MKUU+. Print two plates and compare.
15. ECO switch on or off.
16. Bridging plug only, or a latching switch on PS_ON.
