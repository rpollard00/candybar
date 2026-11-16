# A larger monitor in the same shell

Date: 2026-11-16. This document is a study for a question of the owner. It is not a proposal, and it changes no part of the design.

## The answer

1. Yes. The shell can take a larger screen with no change to its outside.
2. The opening behind the bezel plate is 434.7 x 293.4. This opening is the limit. No screen shows more than this.
3. Wide pictures: a 19 inch 16:10 panel gives 19.0 inches where the present unit gives 16.0 (+18 %). An 18 inch 16:10 portable unit gives 18.0 (+12 %).
4. Old games: a 19 inch 5:4 panel gives a 4:3 picture of 18.4 inches where the present unit gives 14.1 (+30 %). Its tate picture is 13.8 inches, not 10.6.
5. The largest wide unit is a bare panel with a controller board, not a monitor in a housing. The 5:4 unit can be a bare panel, an open-frame monitor or a desktop monitor.
6. The price in pixels is high: the present unit has 3840 x 2400 pixels, the 19 inch 16:10 panel 1440 x 900, the 5:4 panel 1280 x 1024.
7. The price in the design: a new cradle, new lugs on the apron and the brow, and a new interface of the bezel plate. The frame round the picture is 12 to 31, not 45.
8. The two largest candidates drop the decided rule that the cradle takes each 16 inch 16:10 portable monitor.
9. The 18 inch portable unit costs least. It keeps the cradle as it is designed, with new jaws, but its side plugs have 17.3 of room, not 22.
10. Software can keep the picture in the window after the system starts. The firmware screen and the boot loader cannot.

Lengths are millimetres. Screen diagonals are inches. The frame is that of the cradle: `x` across the cabinet, `v` up the screen face from the centre of the image, `t` behind the screen face.

Each value has one of these marks:

| Mark | Meaning |
| --- | --- |
| MODEL | Measured on the built model: the skin of the shell, the cradle and the hardware of the fit study, as the laptop built them on 2026-11-15 |
| OWNER | Measured by the owner on the real monitor |
| SOURCED | From a maker or a seller. The link is in "Sources", and each page was read on 2026-11-16 |
| ESTIMATE | Calculated from other values, or a judgement |

## The pictures

All pictures are in `cad/out/larger-monitor/` (not in git).

| File | Content |
| --- | --- |
| `front.png` | The front of the cabinet, square to the screen face, four times at one scale: the present unit and three candidates. Each has its 16:9, 4:3 and tate window. Hidden edges are removed. |
| `section-side.png` | The screen zone cut from the side, with the limits as numbers and the outlines of five units |
| `section-above.png` | The screen zone cut across the face, seen from above, with the same units |
| `pictures.md` | The table of the pictures, as the script calculates it |

## The limits

### What was measured

`cad/candybar/shell/monitor_study.py` cuts the skin, the cradle and the hardware with 28 planes, and it sends rays from the glass plane to the first face. `cad/tools/larger_monitor_room.py` reads the sections. The raster of the sections is 0.5, so a value from a section is good to 0.5. A value from a ray is good to 0.01.

### The limits of the shell

The shell is permanent. These limits cannot move.

| Limit | Value | Where it was measured | Mark |
| --- | --- | --- | --- |
| Opening behind the bezel plate, between the jambs | 434.68 | Rays along `x` at `v` -120 to 120, 2.0 behind the back of the plate | MODEL |
| Opening between the bottom ledge and the top ledge | 293.42 | Rays along `v` at `x` 0 to 210, same depth | MODEL |
| Depth of the ledges and the jambs | They end at `t` 11.2 | Sections at `x` 0 and at `v` 0 | MODEL |
| Recess of the bezel plate in the body | 434.7 x 305.4 | `docs/design/monitor-cradle-and-bezel.md` | MODEL (not measured again) |
| Width between the inner faces of the sides, behind the jambs | 484 at `v` 0, 482 at `v` -150, 470 at `v` +150, 464 at `v` +170, 460 at `v` +180 | Sections at each `v`, from `t` 12.4 to 62.4. The tuck makes the cavity narrow at the top. | MODEL |
| Room along the face behind the ledges, down | To `v` -286.5 for a body 11 thick, -282 for 20 thick, -264.5 for 50 thick. The sweep and the deck stop the body. | Sections at `x` 0 to 215 | MODEL |
| Room along the face behind the ledges, up | To `v` +209 at least. The sill of the hood stops the body. | Sections at `x` 0 to 215 | MODEL |
| Rear door opening | 422.7 x 165 | `fit/report.json` of the built shell | MODEL (not measured again) |

The diagonal of the opening is 524.4, or 20.6 inches, and its shape is 1.48 to 1. A screen cannot show a larger picture than this rectangle. A screen that is larger than the opening is useful only as far as the opening shows it.

A bezel plate needs material round its window. The plate is 433.7 x 304.4, and it lies on the two ledges (6 at each end). This study uses a smallest bar of 12 between the outline of the plate and the window (ESTIMATE: no plate with a bar of 12 was designed). The largest window is then 409.7 x 280.4. The table of the pictures uses this window.

### The limits of the inside parts

These parts are proposals of step 12. A proposal can change them.

| Part | Limit | Mark | What a larger unit needs |
| --- | --- | --- | --- |
| Lugs (4, on the apron and the brow) | They stand 11.1 into the opening at `x` 30 to 72. The clear height between them is 271.2. | MODEL | A body higher than 271 or a window higher than 271 needs lugs at a different place. |
| Uprights (2) | Their front faces are at `t` 33.8. The room from the glass plane is 25.6. | MODEL | A body thicker than 20.6 needs a different support. |
| Jaws (4) | A jaw needs about 16 beyond the top or the bottom edge of the body, inside the opening. Thus the highest body is about 261. | ESTIMATE from the values of `Cradle` | A body higher than 261 cannot have jaws on its edges. |
| Cable channels and bosses (2 + 4) | Their inner faces are at `x` 211, from `t` 22 to 50, from `v` -112 to -12. | MODEL | A body wider than 422 that is thicker than 13.8 touches them. |

### The limits of the hardware behind the screen

| Limit | Value | Mark |
| --- | --- | --- |
| From the glass plane to the keep-out zone of the compute module, on rays square to the glass | 88.4 at `v` +40, 111.5 at `v` 0, 134.6 at `v` -40 | MODEL |
| From the glass plane to the nearest point of that keep-out zone | 65.5 (the distance between the solids, for a body 400 x 260) | MODEL |
| From the glass plane to the nearest point of the compute module itself | 91.7 | MODEL |
| From the back of the present unit to the compute module | 81.1 | MODEL |
| Hub, at the right side under the screen | It limits a body at `x` 190 to 215 to `v` -256.5. No unit of this study goes that far down. | MODEL |
| Speakers and marquee in the hood | The keep-out zone of a speaker starts 225 above the centre of the image at `x` 120. | MODEL |

The depth is not a limit for a flat unit. A unit that is 50 thick behind the ledges has its back at `t` 62.4. This back is 11.3 from the keep-out zone of the compute module and 37.5 from the module (MODEL). Thus plugs at the back of such a unit must point down or to a side.

### The limits that only the present monitor has

| Limit | Value | Mark |
| --- | --- | --- |
| Plug room beside each side edge | 22, for a right-angle plug. The sockets of the present unit are in its left and right edges. | Design value (`mon_side_clear`) |
| Body that the cradle must take | 360 x 247.1 x 20.6, with a movement of 8 each way | Design value (the survey of five 16 inch units) |
| Push rod for the power button on the right edge | An option | Design value |

A unit with its sockets at the back does not need the 22 at each side. The room in the opening is then free for the body: 434.7 less 1 on each side.

### Where a large body lies

A body that is at most 432.7 x 291.4 goes into the opening. Its glass is then 1.0 behind the back of the plate, as the glass of the present unit.

A body that is larger lies behind the ledges and the jambs. Its glass is then 12.4 behind the screen face: 5.2 behind the back of the plate. The rim of a window then hides a strip of the picture from an eye that is not square to the screen: 3.0 at 30 degrees (ESTIMATE: 5.2 x tan 30).

## How a larger unit gets in

`cad/tools/larger_monitor_room.py` moves each unit as a rectangle in the side view. It tries tilts of 2 degrees and steps of 3. It keeps 0.6 clear of the skin and of the hardware in each section that the unit spans. The cradle is not in this search, because a new unit gets a new cradle. A way that the search finds is free at each step, but the movement between two steps is not swept. The search does not turn the unit about the two other axes.

| Way | Result | Mark |
| --- | --- | --- |
| Through the front opening, straight | Each body up to 432.7 x 291.4 | MODEL |
| Through the front opening, tilted | The bare 19 inch 5:4 panel (324 high): a tilt of 6 degrees and a movement of 18 along the face. The 19 inch 5:4 open-frame and desktop monitors (343 and 334 high, 50 thick): a tilt of 14 degrees, a movement of 27, and a reach of 67 behind the screen face. The 17 inch 5:4 panel: a tilt of 6 degrees. | MODEL |
| With the hood off, from above | Each unit of the study has a free way. A thin unit moves up along the screen face (a tilt of 30 degrees to the upright). The two thick 5:4 units turn to the level on their way. | MODEL |
| Through the rear door | Not examined. The door is 422.7 x 165, and the compute module stands behind it. A unit must turn about two axes on this way. | - |
| A body wider than 434.7 | It does not go through the front opening in the side view. It needs a turn about the upright axis behind a jamb, with 24 of room there. Not examined. | - |

The owner decided that the monitor comes out to the front (2026-11-11). The hood on the body top is a service seam, but the roadmap has it as a seam that opens "if it must come off". Thus the way from above is a second way, not the service way.

## The kinds of screen

### Portable monitors

| Item | 17.3 inch 16:9 | 18 inch 16:10 | 18.5 inch 16:9 |
| --- | --- | --- | --- |
| Example | UPERFECT BE173BF | UPERFECT GR18BQ | UPERFECT GR185BF |
| Body | 398 x 247 x 12 | 400 x 260 x 10 | 425 x 250 x 18, with a stand |
| Lit picture | 381.9 x 214.8 | 387.8 x 242.4 | 409.0 x 230.0 |
| Pixels | 1920 x 1080 | 2560 x 1600 | 1920 x 1080 |
| Frame of the body | 8 at each side. 32 for the top and the bottom together | 6 at each side. 18 for the top and the bottom together | 8 at each side. 20 for the top and the bottom together |
| Mount | VESA 75, M4 x 4 | VESA 75, M4 x 4 | VESA 75, M4 x 4 |
| Power | USB-C, 8 W | USB-C, 14 W | USB-C, 14 W |
| Sound | 2 x 1 W, 3.5 mm output | 2 x 1 W, 3.5 mm output | Not read |
| Mass | 0.91 kg | 0.87 kg | 1.12 kg |
| Price | 220 USD | 280 USD | 220 USD |

All values in this table are SOURCED. The frame values are ESTIMATES: the body less the lit picture.

- **Sockets.** The maker's pages do not give the edge. The present unit of this maker has them in the side edges, and this study takes the same for these units (ESTIMATE). Thus these units need plug room at the sides.
- **Plug room.** With the body in the opening, the room beside an 18 inch body is 17.3 on each side (MODEL), and 18.3 beside the 17.3 inch body. The rule of the cradle is 22. A right-angle plug stands out 15 to 20 (ESTIMATE, from the cradle document, not measured). Thus the plug room is too small by the rule, and a real plug decides.
- **Power, sound and heat.** They are the same as for the present unit: USB-C power from the hub, sound through HDMI, 8 to 14 W of heat.
- **Result.** The 18 inch 16:10 unit is the best portable unit. The 18.5 inch unit gives 18.5 inches at 16:9, but it leaves 4.9 on each side, so its side plugs do not fit.

### Desktop monitors without their stand

| Item | 19 inch 5:4 | 18.5 inch 16:9 |
| --- | --- | --- |
| Example | Dell P1917S | Dell E1920H |
| Body without the stand | 405.6 x 334.3 x 50.3 | About 445.5 wide |
| Lit picture | 376.3 x 301.1 | 409.8 x 230.4 |
| Pixels | 1280 x 1024, IPS | 1366 x 768, TN |
| Sockets | At the back, toward the bottom edge: HDMI, DisplayPort, VGA | The same place |
| Mount | VESA 100 | VESA 100 |
| Power | Mains, with the supply in the housing | Mains |
| Sound | None | None |
| Mass | Not found | 2.19 kg |
| Price | Not read | Not read |

The body values and the pixels are SOURCED. The place of the sockets is an ESTIMATE from the usual form of these monitors.

- A wide desktop monitor does not fit: its housing is wider than the opening, and its picture is no larger than that of a bare panel of the same size.
- A 5:4 desktop monitor fits behind the ledges. It needs a mains lead in the cabinet. The power supply of the cabinet has no mains output, so the lead must branch before the inlet of the power supply.
- The housing adds 15 to 17 on each edge of the picture, and it is 50 deep. The panel inside is the same class as the bare panel that follows.

### Open-frame and industrial monitors

| Item | 19 inch 5:4 | 19 inch 5:4, second maker |
| --- | --- | --- |
| Example | Elo 1990L (the model with a bezel) | Winmate R19L300-OFA1 |
| Body | 414.7 x 342.7 x 50 | 445 x 355 x 56 |
| Lit picture | 376.32 x 301.06 | 376.32 x 301.06 |
| Pixels | 1280 x 1024 | 1280 x 1024 |
| Sockets | HDMI, DisplayPort, VGA, 12 V barrel socket. A box on a lead holds the controls. | VGA. HDMI is an option. |
| Mount | VESA 75 and 100, and two holes on each of the four sides | VESA or rear mount |
| Power | 12 V DC +/- 5 %, 11.8 W | 12 V DC |
| Sound | None | An option |
| Mass | 4.6 kg | Not given |
| Price | 556 to 587 USD | Not read |

All values in this table are SOURCED. The first maker makes 15 inch 4:3 and 17 inch 5:4 units in the same series.

- An open-frame monitor is made for this use: a metal frame with holes on its sides, 12 V from the supply of the cabinet, and no button on its edges.
- It is heavy: 4.6 kg, where the present unit has 0.82 kg. It costs 556 to 587 USD.
- The second example is 445 wide. It lies behind the jambs, and it cannot come out to the front.
- It has no sound output. The sound must then come from the compute board or from an HDMI audio extractor.

### Bare panels with a controller board

| Item | 19 inch 16:10 | 19 inch 5:4 | 18.5 inch 16:9 | 17 inch 5:4 | 15 inch 4:3 | 19.5 inch 16:9 |
| --- | --- | --- | --- | --- | --- | --- |
| Example | AUO M190PW01 V8 | AUO M190EG02 V9 | AUO M185XTN01.2 | AUO M170EG01 V7 | AUO G150XTN06 | AUO M195RTN01.1 |
| Outline | 428 x 278 x 10.8 | 396 x 324 x 11.4 | 430.4 x 254.6 x 10.4 | 358.5 x 296.5 x 17.5 | 326.5 x 253.5 | 452 x 263 x 11 |
| Lit picture | 408.24 x 255.15 | 376.32 x 301.06 | 409.8 x 230.4 | 337.92 x 270.34 | 304.13 x 228.10 | 433.92 x 236.34 |
| Pixels | 1440 x 900 | 1280 x 1024 | 1366 x 768 | 1280 x 1024 | 1024 x 768 | 1600 x 900 |
| Mass | 2.12 kg (the older model with lamps) | 1.8 kg | Not read | Not read | Not read | Not read |

All values in this table are SOURCED from the text that panel traders give. The panel data base asks for a check by a human, so the data sheets were not read.

- **Controller.** A board of the class M.NT68676 is 139 x 58 x 17. It takes 12 V (9 to 16 V), and it has HDMI and VGA inputs, a sound input and 2 x 1 W for speakers (SOURCED). The LED backlight of these panels has no driver, so the kit needs a driver board too. A small board with five keys sets the picture.
- **Power.** 12 V from the supply of the cabinet. The power of a panel with its backlight is about 15 to 20 W (ESTIMATE).
- **Sockets.** They are on the controller board, on leads behind the panel. The panel needs no plug room at its edges.
- **Mount.** A bare panel has screw holes in the side faces of its metal frame. The cradle must hold it by these or by its edges. The data sheet gives the holes, and it was not read.
- **Price.** A 19 inch 5:4 panel is 35 to 50 USD in a trader's text (SOURCED). The price of a controller kit was not read (ESTIMATE: 25 to 40 USD).
- **Quality.** These are office panels of an old class: 84 to 94 pixels for each inch, where the present unit has 283. Most are TN panels, which change colour when the eye moves up or down. The screen leans back 30 degrees, and players of three heights look at it.
- The 19.5 inch panel is wider than the opening. Its picture (433.9) is as wide as the opening, so a plate cannot frame it. This study does not take it as a candidate.

### Squarer monitors for arcade cabinets

Makers of arcade parts sell 4:3 and 5:4 monitors with a frame for a cabinet: 17, 19, 20.1 and 21.3 inch (SOURCED: the list of one maker). The 19 inch units have the 5:4 panel of this study. A 20.1 inch 4:3 picture is 408 x 306 (ESTIMATE: from the diagonal). Its body is wider than the opening. No size was read from a data sheet for these units.

## The candidates

### A. The 18 inch 16:10 portable monitor (example: UPERFECT GR18BQ)

- **Where it sits.** In the opening, on the present glass plane, with the centre of its picture on the centre of the image.
- **What clears.** The body shares no volume with the skin, the cradle or the hardware. Gaps: 17.3 to each jamb, 16.7 to each ledge, 5.6 to the lugs, 6.1 to the uprights, 11.6 to the channels, 81.7 to the compute module, 55.5 to its keep-out zone (MODEL).
- **What changes.** Four new jaws. A new bezel plate with a window of 387.8 x 242.4: its frame is 23 at the sides and 31 at the top and the bottom.
- **What stays.** The lugs, the uprights, the shoes, the channels, the pins and the magnets, the hub, the leads.
- **What is lost.** The plug room at each side is 17.3, not 22. The movement of the jaws along the face is about 1 where it was 8 (ESTIMATE). The cradle then takes this unit and smaller units only.
- **Way in.** To the front, straight, as the present unit. With side plugs in their sockets, the unit is 444 wide and does not pass the opening. The owner must fit the plugs with the unit tilted in the opening. This was not examined.

### B. The 19 inch 16:10 bare panel (example: AUO M190PW01 V8) with a controller board

- **Where it sits.** In the opening, on the present glass plane. It fills the opening: 3.3 at each side, 7.7 at the top and at the bottom.
- **What clears.** The panel shares no volume with the skin or the hardware. It shares 2813 mm3 with the lugs and 780 mm3 with the ears of the uprights. Gaps: 3.3 to each jamb, 7.7 to each ledge, 3.0 to the channels, 80.9 to the compute module, 54.7 to its keep-out zone (MODEL).
- **What changes.** The lugs must move: the panel is 278 high and the lugs leave 271.2. With the lugs, the pins and the magnets of the bezel plate move, and the screws of the uprights. The jaws cannot hold its edges. The controller board, the driver board and the keys need a place and a 12 V lead.
- **What stays.** The uprights can stay as the bed behind the panel, with new fastening points. The channels stay for the leads of the controller.
- **What is lost.** The bezel plate has a frame of 12.7 at the sides. The hub for USB-C power has no use. The adjust range for another monitor is nil.
- **Way in.** To the front, straight.

### C. The 19 inch 5:4 screen (examples: AUO M190EG02 V9 as a bare panel, Elo 1990L as an open-frame monitor)

- **Where it sits.** Behind the ledges, with its glass 12.4 behind the screen face. The bare panel is 324 high: it stands 15.3 behind each ledge. The open-frame monitor is 342.7 high.
- **What clears.** Neither body shares volume with the skin or the hardware. The bare panel shares 2496 mm3 with the lugs and 6450 mm3 with the uprights. Its gaps: 13.0 to the channels, 76.1 to the compute module, 49.9 to its keep-out zone, 56.1 to the room of the speakers. The open-frame monitor takes the place of the uprights. Its gaps: 3.7 to the channels, 37.5 to the compute module, 11.3 to its keep-out zone, 35.5 to the fan room of the power supply (MODEL).
- **What shows.** The opening shows 293.4 of the 301.1 of lit height, and a plate with bars of 12 shows 280.4. The lit width of 376.3 leaves bars of 28.7 at the sides.
- **What changes.** The lugs and the uprights go. A new mount holds the panel by its side holes, or the open-frame monitor by its VESA holes or its side holes. The open-frame monitor is 4.6 kg, so the mount must carry it without friction joints.
- **What stays.** The pins and the magnets of the bezel plate stay as parts. Their lugs must move out of the window, to `x` beyond 190 or to the ledges.
- **What is lost.** The glass is 5.2 behind the plate, not 1.0. The way to the front is a tilted way, not a straight way. Sound from the monitor is lost with the open-frame unit.
- **Way in.** To the front, with a tilt: 6 degrees for the bare panel, 14 degrees for the open-frame monitor (MODEL, in the side view, with no mount in the cabinet). The top edge goes up behind the top ledge first. The mount must leave this way free, and this study did not design it.

### What does not fit, or gives nothing

| Unit | Reason |
| --- | --- |
| 18.5 inch 16:9, portable or bare panel | It fits (4.9 or 2.1 at each side). Its 16:9 picture is 18.5 inches, but the 19 inch 16:10 panel gives 18.4 at 16:9 and more at each other shape. |
| 19.5 inch 16:9 and larger wide units | The picture is as wide as the opening or wider. The body does not pass the opening. |
| 20.1 inch 4:3 | The opening cuts its picture to 293.4 high. It then shows less than 0.8 inch more than the 19 inch 5:4 screen, and its body is wider than the opening. |
| 17 inch 5:4 and 15 inch 4:3 | They fit. They give 16.6 and 15.0 inches at 4:3. The 19 inch 5:4 screen gives 18.4. |
| Desktop monitors, wide | The housing is wider than the opening. |

## What each bezel shows

A picture is the largest rectangle of one shape that lies in the lit area and in the largest window (409.7 x 280.4). Each cell gives the diagonal in inches (bold), the size in millimetres, and the diagonal against the present unit for the same shape. `monitor_pictures.py` calculates the table, and `tests/test_monitor_pictures.py` holds the calculation. The sizes are derived from SOURCED lit areas and the MODEL opening.

| Unit | 16:10 | 16:9 | 4:3 | tate 3:4 | tate 9:16 |
| --- | --- | --- | --- | --- | --- |
| Present unit, 16.0 in 16:10 | **16.0** (345 x 215) 0 % | **15.6** (345 x 194) 0 % | **14.1** (287 x 215) 0 % | **10.6** (162 x 215) 0 % | **9.7** (121 x 215) 0 % |
| Present unit, turned 90 degrees | **10.0** (215 x 135) -38 % | **9.7** (215 x 121) -38 % | **10.6** (215 x 162) -25 % | **13.8** (210 x 280) +30 % | **12.7** (158 x 280) +30 % |
| 17.3 in 16:9 portable | **16.0** (344 x 215) 0 % | **17.3** (382 x 215) +11 % | **14.1** (286 x 215) 0 % | **10.6** (161 x 215) 0 % | **9.7** (121 x 215) 0 % |
| A. 18 in 16:10 portable | **18.0** (388 x 242) +12 % | **17.5** (388 x 218) +12 % | **15.9** (323 x 242) +12 % | **11.9** (182 x 242) +12 % | **10.9** (136 x 242) +12 % |
| A, turned 90 degrees | **11.3** (242 x 152) -30 % | **10.9** (242 x 136) -30 % | **11.9** (242 x 182) -16 % | **13.8** (210 x 280) +30 % | **12.7** (158 x 280) +30 % |
| 18.5 in 16:9, portable or panel | **17.1** (369 x 230) +7 % | **18.5** (410 x 230) +19 % | **15.1** (307 x 230) +7 % | **11.3** (173 x 230) +7 % | **10.4** (130 x 230) +7 % |
| B. 19 in 16:10 panel | **19.0** (408 x 255) +18 % | **18.4** (408 x 230) +18 % | **16.7** (340 x 255) +18 % | **12.6** (191 x 255) +18 % | **11.5** (144 x 255) +18 % |
| C. 19 in 5:4: panel, open frame or desktop | **17.5** (376 x 235) +9 % | **17.0** (376 x 212) +9 % | **18.4** (374 x 280) +30 % | **13.8** (210 x 280) +30 % | **12.7** (158 x 280) +30 % |
| 17 in 5:4 panel | **15.7** (338 x 211) -2 % | **15.3** (338 x 190) -2 % | **16.6** (338 x 253) +18 % | **13.3** (203 x 270) +26 % | **12.2** (152 x 270) +26 % |
| 15 in 4:3 panel | **14.1** (304 x 190) -12 % | **13.7** (304 x 171) -12 % | **15.0** (304 x 228) +6 % | **11.2** (171 x 228) +6 % | **10.3** (128 x 228) +6 % |

- A masked picture uses a part of a fixed panel. The pixels of that part are the pixels of the picture.
- **Tate.** The height of the window (280.4) is the limit for each tate picture. A unit that is turned 90 degrees gives 13.8 inches at 3:4, and so does the 19 inch 5:4 screen that is not turned.
- **A turned unit.** The present unit, turned, is 354 high. It lies behind the ledges, and it needs a second cradle. Its tate picture is then 13.8 inches with 2342 x 3123 pixels. The 5:4 screen gives the same size with 715 x 954 pixels, and with no turn.
- **With bars narrower than 12.** A plate can show the full opening height of 293.4. The 5:4 screen then gives 18.5 inches at 4:3 (376.3 x 282.2) and 14.4 inches at tate 3:4.

## The software side

The assumption is correct for the time after the system starts. It is not correct for the first seconds.

| Level | What does it | Limit |
| --- | --- | --- |
| Kernel | The parameter `video=` sets a mode for a connector, and it takes `rotate`, `panel_orientation` and four margins in pixels. | The margins were made for the overscan of a television. The kernel text does not say that each driver obeys them. This needs a test on the BC-250. |
| Display server, X11 | `xrandr` scales and moves an output (`--scale`, `--transform`, `--fb`, `--panning`), and it turns an output (`--rotate`). | It is not available under Wayland. |
| Compositor for games | `gamescope` gives a game a resolution of its own (`-w`, `-h`) and scales it into the output (`-W`, `-H`), with bars at the sides when the shapes differ. | It puts the picture in the centre. Its text gives no option for an offset. A centred window is thus the simple case. |
| Emulator front end | RetroArch has a custom viewport: a position and a size in pixels (`custom_viewport_x`, `_y`, `_width`, `_height`) with `aspect_ratio_index = "22"`. It can save these for one core or one game. It turns the picture for tate games. | Each emulator that is not a RetroArch core needs its own setting. |
| Games for the PC | The game gets a mode of the size of the window from `gamescope` or from a custom mode. | A game that sets its own mode can go outside the window. |

What does not obey the window:

- The firmware screen and the boot loader use the full panel in its native direction. A plate hides a part of them.
- The boot text and the boot picture obey `video=` and `fbcon=rotate` only when the driver takes them. Users report that the boot picture of a turned panel stays turned on some machines.
- The menu of the monitor itself uses the full panel. A part of it can be behind the plate.
- A picture that is not on the centre of the panel needs an offset at one level. If the window of each plate is on the centre of the panel, no offset is necessary.

With one panel and three plates, the system must know which plate is on. No part of the design tells it. The owner selects the plate in the front end, or a sensor on the plate tells the system (not designed).

Sources: the kernel text on `video=`, the `xrandr` manual, the `gamescope` text, and the RetroArch forum, all in "Sources".

## What it costs in the design

| Decided thing | State now | What a larger unit reopens | Size of the work |
| --- | --- | --- | --- |
| The rule that the cradle takes each 16 inch 16:10 portable monitor (owner, 2026-11-11) | Settled | Each candidate drops it. Candidate A keeps it only in part. | A decision of the owner |
| The look of the screen face: an even frame of about 45 round the picture (owner) | Settled | The frame becomes 23 to 31 (A), 12.7 to 24.6 (B), 12 to 28.7 (C). | A decision of the owner. It needs a render. |
| The cradle (`cradle.py`, 41 tests) | A proposal, not reviewed | A: new jaws. B: new lugs, a new hold of the panel, no jaws. C: a new mount. | A: small. B and C: the cradle package again, about as large as the first time |
| The lugs on the apron and the brow | In the proposal. `split.py` does not know them yet. | B and C move them. The apron and the brow are print pieces. No piece is printed. | Small now. Large after the two pieces are printed |
| The interface of the bezel plate (pins at +-50, +-143, magnets at +-38, +-143) | In the proposal | B and C move the pins and the magnets, because they stand in the window. Each plate follows. | Medium. One interface for all plates |
| The bezel plate (two halves, edge break) | In the proposal | A new plate for each window in each case. A bar of 12 was not designed or printed. | Medium for each plate. A print test for the narrow bar |
| The cable channels and their bosses | In the proposal | They stay. B and C use them for the leads of a controller. | Small |
| The places of the small items (`mounts.py`) | In the proposal | B and C: a place for the controller board, the driver board and the keys. The hub for USB-C power goes. | Small to medium |
| The fit study (`fit.py`, `hardware.csv`) | Passes | The body, the plug room and the cable zones of the monitor change. The study must run again (30 minutes). | Small |
| The sight lines | The fit study checks the present window: a child of 8 loses 0.4 of the image at the bottom. | The window of a candidate goes 13 to 32 lower and higher than the present window. The check must run for the new window. | Small. The result can limit the window. |
| The sound path | HDMI to the monitor, 3.5 mm to the amplifier | C with an open-frame monitor has no sound output. | Small: one more part |
| The push rod | An option, off | It has no use for B and C. | Nil |

### Shared files that a proposal must change

- `cad/candybar/shell/dims.py`: `MON_ACTIVE_W` and `MON_ACTIVE_H` are the lit picture of the present unit. `Dims.bezel_w`, `Dims.bezel_len` and `Dims.width` are calculated from them. A larger monitor must not change these two values, or the shell changes. A proposal needs new values for the window that are not tied to the outer form.
- `cad/params/hardware.csv`: the rows `mon_*` and `mon_gen_*`.
- `cad/candybar/shell/fit.py`: `MONITOR_ANY` and `MONITOR_CABLES`.
- `cad/candybar/shell/cradle.py`: `Unit`, `Cradle`, the lugs, and the interface of the bezel plate.
- `CONTEXT.md`: the first line names a 16-inch monitor.

This study changed none of them.

## What was not found out

- The real sockets of each example: their edge, their height and their direction. The makers' pages do not give them.
- The mounting holes of the bare panels and their real thickness with a controller behind them. The data sheets are behind a check for a human.
- The power of a bare panel with its backlight.
- The picture quality of the 19 inch panels at 30 degrees of recline. No source gives this, and it needs the real part.
- The sight lines for a higher window. The study did not run them.
- The way through the rear door, and the way of a body that is wider than the opening.
- If the plugs of an 18 inch portable unit go into their sockets with 17.3 of room.
- If a bezel plate with bars of 12 prints flat and holds on four magnets.
- If the BC-250 obeys the margins of `video=`.
- The gap from each unit to the skin as one number from the solids. On this machine one such measurement takes an hour, so the sections give the room.
- Prices of the desktop monitors, of the controller kit and of the arcade monitors.

## What the owner must measure or buy to be sure

1. With the present monitor: set a window of 1280 x 960 pixels in the centre from RetroArch, and from a kernel margin. This shows which level works on the BC-250. It costs nothing.
2. With the present monitor: look at a 4:3 picture of 287 x 215 and decide if 374 x 280 is worth the change. `front.png` shows the two sizes at one scale. A print of it at full size on paper costs nothing.
3. Before candidate A: the stand-out of the real right-angle plugs (the same open item as for the present cradle). If it is more than 17, candidate A has no side plugs.
4. Before candidate B or C: buy one 19 inch panel with a controller kit (about 60 to 90 USD, ESTIMATE). Put it at 30 degrees of recline at the height of the cabinet, and look at it from the three eye heights. The panel is the largest risk, and this test is cheap.
5. Before candidate C with an open-frame monitor: the dimensional drawing of the maker for the side holes and the place of the sockets.

## Sources

Each page was read on 2026-11-16.

| Value | Link |
| --- | --- |
| 18 inch 16:10 portable (GR18BQ): body, lit area, mass, power, price | https://uperfect.com/products/18-inch-144hz-freesync-monitor |
| 17.3 inch 16:9 portable (BE173BF) | https://uperfect.com/products/uperfect-144hz-portable-monitor |
| 18.5 inch 16:9 portable (GR185BF) | https://uperfect.com/products/nxtled-one-plus |
| 19 inch open frame (Elo 1990L): all values | https://www.elotouch.com/open-frame-touchscreens-1990l.html |
| Elo 1990L: price | https://www.cdw.com/product/elo-open-frame-touchmonitors-1990l-led-monitor-19/4570719 (the text of the search result) |
| 19 inch open frame (Winmate R19L300-OFA1) | https://www.winmate.com/en/product/exportHtml/R19L300-OFA1 |
| 19 inch 5:4 desktop (Dell P1917S): body without the stand | https://www.dell.com/en-ed/work/shop/cty/pdp/spd/dell-p1917s-monitor (the text of the search result) |
| 18.5 inch desktop (Dell E1920H): width, mass | https://www.dell.com/en-us/shop/dell-19-monitor-e1920h/apd/210-aund/monitors-monitor-accessories and https://www.displayspecifications.com/en/model/934d1c8e (the text of the search results) |
| 19 inch 16:10 panel (M190PW01 V8) | https://www.enlcd.com/p/m190pw01_v8-lcd-panel/ and https://www.leehonlcd.com/product/auo/m190pw01-v8.html (the text of the search results) |
| 19 inch 5:4 panel (M190EG02 V9): outline, mass | https://www.panelook.com/M190EG02_V9_AUO_19.0_LCM_parameter_14786.html (the text of the search result: the page asks for a check by a human) |
| 18.5 inch panel (M185XTN01.2) | https://www.panelook.com/M185XTN01.2_AUO_18.5_LCM_parameter_16228.html (the text of the search result) |
| 17 inch 5:4 panel (M170EG01 V7) | https://www.twscreen.com/en/lcdpanel/9886/auo/m170eg01v7/17/1280x1024-Monitor-LCD-Panel (the text of the search result) |
| 15 inch 4:3 panel (G150XTN06) | https://www.youritech.com/products/g150xtn06-a-auo-15-inch-tft-lcd-display-1024x768-sunlight-readable-wide-temperature-lcd-panel.html (the text of the search result) |
| 19.5 inch panel (M195RTN01.1) | https://www.panelook.com/M195RTN01.1_AUO_19.5_LCM_parameter_19915.html (the text of the search result) |
| 19 inch 5:4 panel: price | https://www.ebay.com/itm/204232398091 (the text of the search result) |
| Controller board M.NT68676.2A | https://wiki.52pi.com/index.php/Z-0261 |
| Arcade monitors, 4:3 and 5:4 | https://www.arcooda.com/accessories/arcade-monitors/20-1-inch-lcd-arcade-monitor/ (the text of the search result) |
| Kernel: `video=`, `rotate`, `panel_orientation`, the margins | https://docs.kernel.org/fb/modedb.html |
| `xrandr` | https://x.org/releases/current/doc/man/man1/xrandr.1.xhtml |
| `gamescope` | https://github.com/ValveSoftware/gamescope |
| RetroArch custom viewport | https://forums.libretro.com/t/centering-viewport-with-retroarch-1-20/47179 and https://forums.libretro.com/t/changing-the-bezel-size-within-ra-to-fit/31959 |
| The boot picture of a turned panel | https://www.reddit.com/r/gpdwin/comments/7s0wsx/linux_screen_rotation_issue_fully_fixed_now/ (the text of the search result) |

## How to run the study again

```sh
CANDYBAR_OUT=cad/out/larger-monitor cad/candybar/freecad-run.sh candybar.shell.monitor_study   # cuts, room, units, front
cad/.venv-tools/bin/python cad/tools/larger_monitor_room.py                                   # limits.json, path.json
cad/.venv-tools/bin/python cad/tools/draw_larger_monitor.py                                   # the pictures and pictures.md
```

The study needs the built shell in `cad/out/shell-rev7`, with the skin in the cache of the split. It needs the cradle and the fit study of the present monitor in `cad/out/laptop-2026-11-15`. `MONITOR_STUDY_BUILT` sets a different folder. The rays of the step `room` take 20 minutes.
