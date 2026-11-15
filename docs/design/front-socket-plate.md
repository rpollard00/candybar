# The front socket plate

Date: 2026-11-14. All dimensions are in millimeters.

This document gives the design of the removable plate that carries the four USB sockets, the everyday power button and, as an option, the volume control. The values are in `cad/candybar/shell/socket_plate.py` (class `SocketPlate`, and `VARIANTS` for the arrangements). The checks are in `cad/out/socket-plate/report.md`. This is a proposal. The owner decides the look and the hardware.

## Summary

- The plate is in the right side face of the deck, where `fit.Layout` has the four USB sockets. It is not in the front face of the deck.
- The plate is 142 x 33 x 4, with round ends. It lies flush in a recess, with a reveal of 1 round it.
- The four sockets are a block of two rows: the two USB-A sockets in one column and the two USB-C sockets in a second column. One row of four sockets and a button is longer than the flat part of the deck side.
- There are four variants: two layouts, each with the knob and without it. All four go into one opening and use the same two plate screws.
- The audio research (2026-11-14) recommends the volume control on the plate, beside the power button. That is variant `b-knob`, and it is the default of the module. The owner likes `b-knob` (2026-11-14, evening). The other variants stay. The plate is not in the default build of the shell.
- The button, the knob and the four sockets fit in one plate. A second plate is not necessary. "The knob on the left side" shows that alternative.
- Two M3 screws hold the plate from the front. The plate comes out to the outside with its leads.
- The edge rule holds on the plate and on the opening. The rules of the fit study hold with the hardware of the plate. The numbers are in "Checks".

## Where the plate is

The work package says "the front of the cabinet". The owner settled two things that decide the place (`docs/roadmap.md`, "Settled by the owner" and "Variant D"):

- The four USB ports are "in the right side face of the deck toward the front, out of view".
- There are "no holes in the front face of the deck".

`fit.Layout` follows this: its USB row is in the right side of the deck. Thus the plate is in the right side face of the deck. The power button is then on the right side of the deck, near the front corner. A person at the seat cannot see it, but the right hand finds it round the corner. This is the first open question for the owner.

The side of the deck is flat from y 54.0 (the end of the front corner) to y 207.0 (seam D2, where the deck meets the body). It is upright from z 5 (the base facet) to z 48 (the crease of the edge section). This flat face is 153.0 x 43.0 (measured on the form: `socket_plate.flat_face()`).

The recess must stay 5 in front of D2 and 3 behind the front corner (a strip of face of 2 beside the edge break). Thus the longest recess is 145 and the longest plate is 143. The plate is 142.

| Item | Value |
| --- | --- |
| Center of the plate on the outer face | x 247.3, y 130.0, z 26.5 |
| Plate | y 59.0 to 201.0, z 10.0 to 43.0 |
| Recess | y 58.0 to 202.0, z 9.0 to 44.0 |
| Print piece of the split | `deck side R` |

The plate is at mid-height of the upright face. The frame of the plate in the module: `s` goes along +y (toward the rear) and `t` along +z, from the center of the plate. Seen from outside, the front of the cabinet is on the left.

## The plate

| Value | mm | Status |
| --- | --- | --- |
| Length x height | 142 x 33 | PROVISIONAL |
| Ends | Round, radius 16.5 (half the height) | PROVISIONAL |
| Thickness | 4.0, the same as the skin | PROVISIONAL |
| Web behind the sockets and the knob | 2.4 | PROVISIONAL. The sockets mate fully through 2.5 at most (SOURCED). |
| Reveal round the plate | 1.0, the same as the control panel and the bezel plate | PROVISIONAL |
| Edge break | R 1 on the outer rim and on the rims of the socket openings | Decision record 0007 |

The outline is a level slot with round ends. The rear of the cabinet has the same shape in its cut-ins and its hand-holds. The plate has planes, cylinders and the rounds of the edge break only.

The back of the plate has one pocket for each column of sockets, 1.6 deep. The two flanges of a column lie in the pocket. A round pocket of 19 takes the body of the volume control.

## What the plate carries

| Hardware | Values | Status |
| --- | --- | --- |
| USB-A socket with a screw flange (example: DataPro 1698), 2 off | Cut-out 14.7 x 7.3, radius 1.6. As printed 15.1 x 7.7, radius 1.8. Two flange holes 30.0 apart, printed at 3.4. Space behind the panel 39 x 13. | SOURCED (`docs/research/pc-panel-and-front-usb.md`, A4 and A5). The print sizes are PROVISIONAL. |
| USB-C socket with a screw flange (example: DataPro 1678), 2 off | Cut-out 10.5 x 4.6, radius 2.0. As printed 10.9 x 5.0 with round ends (radius 2.5). Two flange holes 20.0 apart, printed at 3.4. Space behind the panel 28.2 x 8.7. | SOURCED. The round ends are PROVISIONAL: a radius of 2.2 leaves a flat of 0.6 at each end. |
| Socket body and cable | Body 32 behind the flange. 60 clear behind the flange for the body and the cable bend. | ESTIMATED (`cad/params/hardware.csv`) |
| Flange screws | 4-40, into the nuts of the flange. Eight heads show. Head 5.7 x 1.65 in the model. | The thread is SOURCED. The head is ESTIMATED. |
| Power button | Thread 16. Hole as printed 16.3. A flat face of 22 round the hole. Rim 19 x 2 and a nut of 22 in the model. 45 clear behind the plate. Four wires. | ESTIMATED until the part is measured |
| Volume control | The potentiometer of the amplifier: 1 kOhm, three wires that carry no sound. Hole 9.4. Wall at the hole 2.4 (the research asks for 2 to 3). 20 clear behind the plate. A flat circle of 22 outside for the knob. Knob 18 x 15 and body 17 x 12 in the model. The nut is on the front, below the knob. | The hole, the wall, the clear depth and the flat circle are from the audio research (2026-11-14). The knob and the body are ESTIMATED. |
| Plate screws | 2 x M3 x 8 with a button head, into heat-set inserts in the frame. Hole in the plate 3.4. Hole for the insert 4.0. | PROVISIONAL |

The two rows are 14 apart: the flange is 13 high, and 1 is between two flanges. Two USB-A plugs (8 high) then have 6 between them. A thick USB stick in one USB-A socket can block the other one.

## The layouts

One row is not possible on this face:

- The flat is 153.0 long, and the longest plate on it is 143.
- The four flanges in one row are 39 + 28.2 + 39 + 28.2 = 134.4. With gaps of 2 and the two plate screws, the sockets alone need a plate of 164.
- With the button and the knob (a flat of 22 each), one row needs 212. The research note gives about 150 + 26 + 26 = 202 for the same row.

Thus the sockets are in two rows: the two USB-A sockets in one column, the two USB-C sockets in a second column. The two columns are 67.2 wide. Then the button, the knob and the four sockets fit in one plate of 142.

| Variant | Button, s | USB-A column, s | USB-C column, s | Knob, s | Idea |
| --- | --- | --- | --- | --- | --- |
| `a-knob` | -48.0 | -15.5 | 21.1 | 48.0 | Layout A: the controls at the two ends, the sockets between them |
| `a-plain` | -48.0 | -3.6 | 33.0 | none | Layout A without the knob: the sockets are in the middle of the remaining length |
| `b-knob` | -48.5 | 6.5 | 43.1 | -25.0 | Layout B: the button and the knob together at the front end, the sockets behind them |
| `b-plain` | -48.5 | 6.5 | 43.1 | none | Layout B without the knob: the button is apart at the front end, as the main control |

The button is at the front end in all variants, because that end is nearest to the player. The audio research recommends the knob beside the button: that is `b-knob`, the default. `report.md` has two tables of gaps for each variant: behind the plate (nuts, flanges, bodies) and on the front (the flat faces and the screw heads). The smallest gap behind the plate is 1.0, from the nut of the button to the front end of the window in layout B. The smallest gap on the front is 1.5, between the flat face of the button and the flat circle of the knob in `b-knob`.

Sheets: `cad/out/socket-plate/sheets/1-cabinet-with-each-variant.png` and `2-plate-close-up.png`.

Notes on the layouts:

- Layout A is symmetric. A hand that turns the knob is far from the button.
- In layout B the knob (18) is 5 from the rim of the button (19). A hand on the knob can push the button by accident. A short press shuts the system down (way (a) of the open decision "The everyday power button").
- The knob stands 17 out of the side of the deck. It is the only part that a person at the seat can see.
- `a-plain` and `b-plain` are the same plate as the knob forms, without the hole and the pocket of the knob. In `a-plain` the sockets move, because a blank end does not look correct.

## The knob on the left side (the alternative)

The audio research asks for this alternative if one plate is too short. One plate is not too short. The alternative is built so that the owner can compare: folder `knob-left`, sheet `7-knob-on-the-left.png`.

| Item | Value |
| --- | --- |
| Small plate | 50 x 33 x 4, round ends, the same reveal, edge break and two M3 screws |
| Place | The left side face of the deck, at the front end of the flat: y 59 to 109, center z 26.5. It is opposite the front end of the socket plate. |
| Window | 28 x 28 |
| Right plate | The plain form of the layout (`b-plain`): the button and the four sockets |
| Deepest point behind the plate | x -223.3 (20 clear behind the plate) |

For: the knob is far from the power button, and the left hand can turn it. Against: a second opening, in the print piece `deck side L`, with its own frame, floor notch and support in the print. The knob lead is three wires and can be long, so the lead is not a problem. The rules of the fit study were not run for the small plate. The nearest item of `fit.Layout` on that side is the encoder, 35 away (from its anchors, not from a run).

## The seat in the shell

The opening is a cut in the deck. `socket_plate.cutter()` is the cutter, and `socket_plate.seat()` makes the cut on a part.

| Part of the seat | Values |
| --- | --- |
| Recess | The outline of the plate plus the reveal: 144 x 35, round ends of 17.5, 4.0 deep (through the skin) |
| Window | 121 x 28, corners of R 6, through the skin and the frame |
| Ledge | 2.5 wide at the top and the bottom. The plate rests on it. |
| Frame | A ring behind the skin, 4.0 thick, 3.0 wider than the recess. Its inner edge has a facet of 45 degrees. |
| Inserts | Two holes of 4.0 in the frame, on the center line, 6 from each end of the plate |
| Edge break | R 1 on the rim of the recess |

The cut takes 36.1 cm3 out of the outer form of the deck, in the box y 57 to 203, z 8 to 45, to 9 deep. `seat()` is the step that `solids.deck` must get (see "What to merge").

The owner can choose the outline and the seat. Sheet `3-outline-and-seat.png` shows three forms of the default variant:

| Form | For | Against |
| --- | --- | --- |
| Round ends, flush with a reveal of 1 (the proposal) | It uses the shape of the cut-ins and the hand-holds. The button and the knob are near the centers of the round ends. | The roof of the recess needs a support in the print. |
| Square ends with corners of R 6, flush | The service doors below the control panel of the full-size cabinet have this shape: flat, flush, with a thin reveal. | The corners are near the screw heads. The same support is necessary. |
| Proud: the plate lies on the face of the deck, 4 high | No recess, so no support at a face that shows. | The plate does not read as a part of the form. Its rim stands out of the side. |

## How the plate fastens

Two M3 screws go from the front through the plate into heat-set inserts in the frame. They are on the center line, 6 from each end. Their heads show, together with the eight heads of the flange screws. All ten heads are of one type in the model.

The earlier note in `structure.py` says "screwed from inside". This design does not do that, for two reasons:

- A screw from inside is 50 outboard of the edge of the control panel opening and 40 below the deck top. A person cannot see it.
- The eight flange screws show in all cases. Two more heads on the center line make a regular pattern.

An option hides all ten heads: a printed clamp bar behind each column holds the flanges, and two screws from inside hold the plate. This option is not built.

## Behind the plate

The rules of the fit study were run with the hardware of the plate in place of `fit.usb_row()`. `fit.py` is not changed. `socket_plate.fitted()` builds the same items from the functions of `fit.py`. The opening is added to the cavity, and the frame and the plate count as walls.

Result: all four variants pass every rule (R1 interference, R2 keep-out, R5 button spacing, containment in the cavity, the air zones, the door service). The table is for `b-knob`. `report.md` has it for each variant.

| Item | Gap to the skin and the frame | Nearest other item | Gap | Above the floor |
| --- | --- | --- | --- | --- |
| USB_A1 | 0.5 | USB_A3 | 1.0 | 17.0 |
| USB_C2 | 1.7 | USB_A1 | 3.0 | 19.2 |
| USB_A3 | 0.5 | USB_A1 | 1.0 | 3.0 |
| USB_C4 | 1.7 | USB_A3 | 3.0 | 5.2 |
| PowerButton | 1.0 | VolumeKnob | 4.0 | 5.5 |
| VolumeKnob | 5.5 | USB_A1 | 3.5 | 8.0 |

The gap of 0.5 is between a USB-A flange and the ledge. The two USB-A bodies are 1.0 apart. No item of the control panel is the nearest neighbor of an item of the plate: the pocket of the control panel is clear above the plate.

The sockets moved from their places in `fit.Layout`, because a row of four does not go on a plate that ends 5 in front of D2:

| Socket | In `fit.Layout` (y, z) | On the plate, `b-knob` (y, z) | Moved in y | Moved in z |
| --- | --- | --- | --- | --- |
| USB_A1 | 73.5, 24.0 | 136.5, 33.5 | +63.0 | +9.5 |
| USB_C2 | 111.5, 24.0 | 173.1, 33.5 | +61.6 | +9.5 |
| USB_A3 | 149.5, 24.0 | 136.5, 19.5 | -13.0 | -4.5 |
| USB_C4 | 187.5, 24.0 | 173.1, 19.5 | -14.4 | -4.5 |

The row of `fit.Layout` goes from y 54.0 to y 201.6, which is the full flat. A plate round that row cannot keep clear of the front corner and of D2. The center line moved from z 24.0 to z 26.5, the middle of the upright face.

The hub stays where `fit.Layout` has it: on the floor behind the plate, x 176 to 221, y 242 to 352. Its front plugs are 40 to 70 behind the rear end of the plate.

Where the leads go:

| Lead | Route | Joint for service |
| --- | --- | --- |
| Four USB leads | From the sockets toward the rear, along the floor, to the front plugs of the hub (route "hub to the USB sockets" in `structure.py`) | The USB plugs at the hub |
| Power button, four wires | Two for the switch and two for the lit ring. Along the right side at the floor to the rear, then to the compute module or to the adapter board. The end depends on the open decision "The everyday power button". | An inline plug with four pins, behind the plate |
| Volume control, three wires | To the amplifier. The wires carry no sound, so the lead can be long. The place of the amplifier is open. | An inline plug with three pins, behind the plate |

The shortest socket lead that the example vendor sells is 150 long. From the USB-A column to the hub is 110 to 130 in a straight line. A lead of 300 is the safe choice.

To remove the plate for service:

1. Lift the control panel out of its pocket.
2. Through the panel opening, disconnect the four USB plugs from the hub.
3. Disconnect the inline plug of the button. If the plate has the knob, disconnect its inline plug.
4. Remove the two plate screws from the outside.
5. Pull the plate out to the right. The leads and their plugs come out through the window.

The window is 121 x 28. A USB-A plug with its overmold is 16 x 8, so each plug goes through. Sheets: `4-plate-out.png`, `5-behind-the-plate.png` and `6-sections.png` (sections through the button, the two socket columns and the knob).

Two conflicts with parts that are not designed yet:

- **The floor.** The floor is 10 thick (`fit.Layout.floor_t`). The lower part of the frame is at z 6 to 10. The floor tile `floor front side R` must have a notch there: 150 long (y 55 to 205), 8 wide from the inner face of the side. The hardware itself is above the floor: the lowest flange is at z 13.0.
- **The foot flange of joint 3.** `joints.py` has a foot flange 12 wide and 4 high on the floor, along the wall. Along the plate it is at z 10 to 14, and the lower flanges of the sockets start at z 13.0. The foot flange must stop along the plate (y 55 to 205). The frame can do its work there.

## The opening and the split

The opening is in the print piece `deck side R` only. It crosses no seam.

| From the rim of the recess to | Distance |
| --- | --- |
| Seam D2 (deck to body), behind the recess | 5.0 |
| The start of the front corner of the deck, in front of the recess | 4.0 |
| The crease of the edge section, above the recess | 4.0 |
| The edge of the base facet, below the recess | 4.0 |
| Seam D1 (under the control panel), across the deck | 48.8 |
| Seam F1 / F2 (the flank break of the deck front), across the deck | 112.9 |

The edge break of R 1 on the rim takes 1 from each of the first four distances.

The floor seam BA2 (y 194) is in the floor tiles, not in the deck side. It goes below the rear end of the plate, and the notch for the frame crosses it.

## Print

| Part | Orientation | Flattest underside | Support |
| --- | --- | --- | --- |
| Socket plate | Front face on the bed | The front face: flat over 140 x 31, with the edge break of R 1 round it | None. The pockets are open to the top. The holes are upright. |
| `deck side R` with the seat | Upright, as `split.py` has it. Box 184.3 x 183.5 x 72.0: the seat does not change it. | Its foot, as before | See the list that follows |

The seat on the upright piece:

- The roof of the recess faces down. It is 109 x 4 level, plus the top 13.7 of the round at each end: 5.5 cm2. It needs a support, which is sanded before primer. This face is in the reveal, above the top edge of the plate. The apron has a support of about 3 cm2 for the same reason.
- The top of the window is a bridge of 109 between its corners. The plate hides it.
- The frame grows out of the wall with a facet of 45 degrees, so it prints without support.
- The edge break on the front rim of the plate lies on the bed. Its first millimeter overhangs. Sand it before primer, or print the plate with its back on the bed and a support in the pockets.

The proud seat has no recess, and then no face that shows needs a support.

**Material and printer.** The owner prints the cabinet in ABS on a Qidi Q2 (bed 270 x 270, height 256; decision record 0008), not in PETG on the A1. Nothing in this part depends on that choice:

- The plate is 142 x 33 x 4, and `deck side R` is 184.3 x 183.5 x 72.0. Both fit both printers.
- No value of `SocketPlate` comes from a property of PETG. Heat-set inserts work in ABS.
- Two things must be tested again in the material that is used: the print allowances of the holes (0.2 to 0.4), and the bridge of 109 over the window.
- `print_rows()` reads the limit from `cad/params/printer.csv`, which has the Q2 (248 x 248 x 250).

## Checks

| Check | Result |
| --- | --- |
| Fit rules, four variants | PASS, no finding |
| Edge rule, plate | 0 sharp edges that show. With the knob: 12 sharp rims of round holes, each under hardware, and 57 sharp edges on the back. Without the knob: 11 and 55. |
| Edge rule, seat in the deck | 0 sharp edges that show. 10 sharp edges are on the ledge and in the window, behind the back of the plate. |
| Edge rule, options `square`, `proud` and the small plate for the knob | 0 sharp edges that show |
| Face check, plate | 0 findings that fail. With the knob: 90 faces, 69 narrow faces allowed by name. Without the knob: 87 and 68. |
| Face check, deck at the seat | 0 findings that fail. 4 allowed: the rounds of the edge break on the rim. |
| Solids | Each plate is one valid solid. The deck with the seat is one valid solid. |
| Tests | `cad/test.sh test_socket_plate`: 28 tests. 27 pass on pal9000. The fit test cannot start there, because the default build of the shell stops at the edge break of the hood. |

The tools `edge_finish.py` and `face_check.py` work on the parts of the shell by name. They do not know the part `socket_plate`. Thus the module makes the two checks with the functions of these tools (`socket_plate.edge_finish()` and `socket_plate.face_rows()`):

- **Edge rule.** The check finds each convex edge that turns more than 45.5 degrees and has no round. Such an edge fails if it shows: it is on the front of the plate or on the outer face of the deck, and no part covers it. The rims of the round holes are sharp. Each one is under the rim of the button, the nut of the knob or a screw head.
- **Face check.** Two groups of narrow faces are allowed by name. The first group is the rounds of the edge break. The second group is the faces behind the edge break inside the plate: the walls of the socket openings (1.4 wide) and the walls of the pockets (1.6 deep). The web of 2.4 makes these faces narrow. A narrow face on the front of the plate is not allowed.

## What to merge into the shared files

| File | Change |
| --- | --- |
| `solids.py`, `deck()` | After the edge break of the pocket rim: `solid = socket_plate.seat(solid, SocketPlate(), d, hollow=False)`. For the hollow skin, `seat(..., hollow=True)` adds the frame. A new part `socket_plate` in `build()` (variant `a-knob` until the owner chooses), with a finish in `FINISH`. |
| `cavity.py` | The opening of the plate as a third opening (`socket_plate.cutter()`), and the frame as a part of the skin. The fingerprint of the skin cache changes, so the skin is made again (about 18 minutes). |
| `fit.py` | `usb_row()` becomes the hardware of the plate (`socket_plate.assemblies()`): the sockets in two rows, the button and the knob. `usb_row_z` becomes 26.5 (it was 24.0). `Layout.usb_front_gap` and the parameter `usb_pitch` are then not used. The plan section "plan, deck" must go through z 26.5. |
| `split.py` | `EXISTING`: the text of the item `USB` (the recess ends 5 in front of D2, it is 4 behind the front corner, the plate is in `deck side R`). `WHY["deck side"]`: the support at the roof of the recess. |
| `structure.py` | `mounts()`: "USB socket plate" is screwed from the outside with two M3 screws into inserts in the frame. `ROUTES`: the leads of the button and of the knob. |
| `joints.py` | The foot flange of joint 3 stops along the plate (y 55 to 205) on the right side of the deck. |
| `cad/tools/edge_finish.py` | `socket_plate` in `PRINTED`. The joints `("deck", "socket_plate")` and `("socket_plate", "deck")` in `JOINTS`, and the hardware that covers the rims of the round holes. |
| `cad/tools/face_check.py` | A reveal "socket plate" (the walls of the socket openings and of the back pockets). |
| `cad/params/hardware.csv` | Rows for the power button, the volume control, the flange holes and the plate screws. The values are in `SocketPlate`. |
| `docs/roadmap.md` | "Front USB hardware" and "The everyday power button": a link to this document. Step 11 or a new step: the socket plate. |
| `docs/blueprint/index.md` | "Hardware in the shell" and the service table: the plate, its place and its checks. Sheet 09 shows a row of four sockets and must change. |
| `CONTEXT.md` | A term **Socket plate**: the removable printed plate in the right side of the deck that carries the USB sockets, the power button and the volume control. Avoid: USB plate, I/O panel. |
| `cad/README.md` | The module `socket_plate.py`, the tool `draw_socket_plate.py` and the commands in "How to build". |

## Assumptions

1. "Front" in the work package means the front USB ports. The place is the right side face of the deck, as the owner settled it and as `fit.Layout` has it.
2. The sockets are the two DataPro examples of the research note, with the sizes that the note gives.
3. The flange is as large as the "space behind the panel" (39 x 13 and 28.2 x 8.7). Its thickness is not known. The model gives it no thickness of its own: the body starts at the web.
4. Two flanges can be 1 apart. If the real flange is higher than 13, the plate must be higher or the rows must be farther apart. The face of 43 has only 4 above and below the recess.
5. The flange screws and the plate screws have button heads of 5.7 x 1.65.
6. The button has a rim of 19 x 2, a nut of 22 across its corners and a body 28 long. Its lit ring in the views is decoration.
7. The volume control has its nut on the front, a body of 17 x 12 and a knob of 18 x 15. Its hole, wall, clear depth and flat circle are those of the audio research.
8. The floor is 10 thick and reaches the inner face of the deck side.
9. The M3 inserts are 4 long and go into a hole of 4.0. No insert is chosen.
10. The plate and the deck have the same paint.

## Open questions for the owner

1. **The place.** Is the right side face of the deck correct for the power button? The button is then out of view from the seat. The front face of the deck has no holes by an earlier decision.
2. **The layout.** Answered on 2026-11-14: the owner likes B with the knob (`b-knob`). The other variants stay in the module.
3. **The knob.** The audio research recommends it on this plate, beside the button (`b-knob`). The alternative is a small plate on the left side. Both forms of the socket plate use one opening, so this choice can come after the shell is printed. The left plate needs its opening before the print.
4. **The outline.** Round ends, or square ends with corners of R 6 as on the full-size cabinet?
5. **The seat.** Flush with a reveal (a support in the print), or proud (no support)?
6. **The screw heads.** Ten heads show. Is that acceptable, or must the clamp bar option be designed?
7. **Two rows of sockets.** Are two USB-A sockets 14 apart acceptable? A thick USB stick can block the second one.
8. **USB-C orientation.** The USB-C openings are level. They can be upright (the plug is the same in both directions), which makes the column 19 narrower.

## Not done

- No part was measured. Every hardware size is sourced from a page or estimated.
- No coupon of the socket openings, the web and the pockets was designed. The research note asks for one.
- The clamp bar option and the fastening from inside were not modeled.
- The leads were not modeled as solids. The sheets show the room for them as boxes.
- The notch in the floor tile and the end of the foot flange are described here and not modeled.
- The anti-rotation tab of the volume control has no hole. Its position on the real part is not known.
- The rules of the fit study were not run for the small plate on the left side.
- The plate was not added to the default build, the cavity, the fit study or the split, because those files are shared.

## How to build

```sh
# all variants: BREP, meshes, edges, sections and report.md (about 20 minutes: the cavity of the fit study takes most of it)
CANDYBAR_OUT=cad/out/socket-plate cad/candybar/freecad-run.sh candybar.shell.socket_plate
#   CANDYBAR_SHELL=<folder>   read the outer form from a build of candybar.shell.solids, and do not build it again
#   CANDYBAR_PLATE_FIT=0      leave the fit rules out (about 2 minutes)

# shell.FCStd in each folder, the renders with every edge, and the sheets
cad/.venv-tools/bin/python cad/tools/draw_socket_plate.py all

cad/test.sh test_socket_plate
```

Folders in `cad/out/socket-plate/`: `a-knob`, `a-plain`, `b-knob`, `b-plain` (the plate in the shell), `square` and `proud` (the options of sheet 3), `knob-left` (the alternative of sheet 7), `behind` and `out` (the print piece `deck side R` with the seat), and `sheets`.

## On the main line

Date: 2026-11-14. The package was merged on the laptop after the monitor cradle. What changed:

- The module reads the moved modules of the shell (`controls.control_panel`, `params`, `model`, `check`, `hardware`).
- `b-knob` stays the default of the module, as the owner likes it. All variants stay. The plate is not in the default build of the shell, the cavity, the fit study or the split.
- **The tools.** `tools/edge_finish.py` has `socket_plate` as a printed part and the bought parts of a variant folder in a class of their own. A sharp edge of the plate passes under a bought part (the rim of the button, the nut of the knob, a screw head) by the rule of this module (`socket_plate.covered`), or against the inside of the shell behind the web (`socket_plate.inside_covers`); the seat of the deck behind the plate is inside the shell too. `tools/face_check.py` has the reveal of the socket openings and the back pockets (`socket_plate.face_reveal`) and leaves the bought parts out. Both tools pass on `cad/out/socket-plate/b-knob`.
- **The fit test** of the package ran here: both layouts with the knob pass the rules of the fit study.
- **The print pieces with the plate** (2026-11-15). `pieces.py` builds the pieces with the plate when `CANDYBAR_PIECES_SOCKET_PLATE=1` (the default build stays without it). Then deck side R has the seat and its frame (`pieces.with_socket_plate`), the floor tile under the frame has its notch (the floor cuts a notch round each part of a wall in its plan, with 0.5 of clearance), and the foot flange of deck side R stops along the plate (a zone of the plate's length, `pieces.socket_plate_items`), so that no foot screw goes where no tile lies. The plate and the bought parts of all four variants are obstacles of the flanges and are checked against the tiles: none meets a tile. The frame and the plate keep their form; only the inside parts (the tile and the foot flange) change. `tests/test_pieces.py`, class `SocketPlateTest`.
