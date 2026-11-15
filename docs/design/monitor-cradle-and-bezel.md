# The monitor cradle and the bezel plate

Date: 2026-11-14. Roadmap step 13, and the bezel plate as a printed part.

This document describes a proposal. The owner did not review it. The module is `cad/candybar/shell/cradle.py`, and its values are in the dataclass `Cradle`. The build output is `cad/out/cradle/` (not in git).

All lengths are millimetres. This document uses the frame of the module: `x` is across the cabinet, `v` is up the screen face from the centre of the image, and `t` is the depth behind the screen face. The back of the bezel plate is the plane `t` = 7.2 (`mon_setback`).

## Summary

- The monitor lies in four jaws on two uprights. The uprights stand behind the monitor, between the bottom ledge and the top ledge of the opening.
- The monitor comes out to the front with one tool, a 2.5 mm hexagon key. The bezel plate comes off by hand.
- The bezel plate is two printed halves with a seam on the centre line. It has the edge break on each edge that shows.
- Four magnets hold the plate. Four pins in radial slots put it in its place.
- The outer form does not change. The shell gets eight added solids on its inside: four lugs and four bosses. It gets no new opening.

## The opening, as the shell has it

The opening behind the bezel plate is 434.7 x 293.4. A ledge of 6 x 4 is at its bottom and at its top. Each side is a wall (the jamb) that goes from the rail land back to `t` = 11.2. Behind each jamb the rail is hollow, out to the inner face of the side at `x` = 243.

The fit study has two monitor bodies. The present unit is 354 x 230 x 10.6 (the thickness measured by the owner, 10.45 to 10.6; the width and the height are the maker's). The body that the cabinet must take is 360 x 247.1 x 20.6, with a movement of 8 each way and a plug room of 22 on each side.

## The cradle

### Parts

| Part | Count | What it is |
| --- | --- | --- |
| Lug | 4 | An added solid on the body. It makes a ledge 11.1 wider and 6 thick, from `x` 30 to 72 on each side of the centre line. |
| Upright | 2 | A bar of 24 x 12, 301.2 long, at `x` 84 on each side. Each end has a slot of 4.5 x 29 and an ear with an M4 heat-set insert. |
| Jaw | 4 | A slider on an upright. It has a wall beside the edge of the monitor, a rest behind the monitor, and a land for the lock screw. |
| Shoe | 4 | A block behind the slot of the upright. It holds the M4 nut of a lock screw. |
| Cable channel | 2 | A C section on the inner face of each side, 100 long, with slots for cable ties. |
| Boss | 4 | An added solid on the inner face of each side. It holds an M3 heat-set insert for a cable channel. |

Bought parts: 4 screws M4 x 25 and 4 screws M4 x 12 with a button head (ISO 7380), 4 hexagon nuts M4, 4 washers M4, 4 heat-set inserts M4, 4 heat-set inserts M3, 4 screws M3 x 8, 4 dowel pins 4 x 12, 4 dowel pins 4 x 16 for the seams, 8 disc magnets 8 x 3, cable ties 2.5 wide, cellular rubber strip 2 thick, felt 1 thick.

### How the monitor is held

The front faces of the uprights are at `t` = 33.8. This is behind the thickest monitor of the survey (20.6), its felt (1) and a rest of 4.

A jaw is printed for one monitor. Its rest is as deep as that monitor is thin, so the glass of each monitor is at the same depth. Its other dimensions are the same for each monitor. The model has the jaws of the present unit.

The glass stands 1.0 behind the back of the plate (`glass_gap`). In the fit study the glass is on the plane of the back of the plate. With no gap, the plate presses on the glass. The gap also lets a fingernail or a card go behind the rim of the window.

Each jaw has a pad of cellular rubber, 2 thick, on its wall. The two top jaws press the pads together by 0.5. The jaws have no lip in front of the glass, because the back of the plate is 1.0 in front of the glass and the plate is 2 thick at the rim of the window.

### The thickness of the housing

The owner measured the housing with a caliper: 10.45 to 10.6, all the way round (2026-11-14). The maker gives 10, and the second source 10.2. The model uses 10.6 (`PRESENT.t`), so that each part clears the thickest housing. The reserved room of 11 has 0.4 to spare.

The screen leans back 30 degrees, so the housing lies on the felt of the rests of the bottom and top jaws. The felt is not pressed by the thickness: the weight holds the housing on it. The rests are made for 10.6. A housing of 10.6 has its glass 1.0 behind the back of the plate (`glass_gap`). A housing of 10.45 lies on the same felt and has its glass 1.15 behind the plate. The edge pads hold the top and the bottom edge in both cases: they press across the face, not through the thickness.

What was made for 10 before, and is made for 10.6 now: the rest of each jaw (0.6 farther back), the box of the monitor and its plug room in the depth (the sockets and the button are in the middle of the edge, so they stand 0.3 farther back), the place of the power button for the push rod (0.3 farther back), and the body of the monitor in the fit study (`mon_t` in `cad/params/hardware.csv`). The glass does not move: the plate and the window do not change.

### Adjustment

- Along the face: each jaw moves along the slot of its upright. The slot takes each body of the survey with a movement of 8 each way.
- Across the face: the monitor moves sideways on the pads before the top jaws are tight. The jaws have no side stop.
- The position of the image does not depend on the dimensions of the body. Thus the adjustment also takes the shrink of the printed parts.

### How to take the monitor out

1. Pull the bezel plate off.
2. Loosen the two top lock screws with the 2.5 mm hexagon key.
3. Push the two top jaws up.
4. Tip the top of the monitor forward.
5. Pull the plugs out of the monitor.
6. Lift the monitor off the bottom jaws.

The bottom jaws stay in their position. Thus the next monitor of the same type goes back to the same place.

### How to put the monitor in

The plug room beside each side edge is 22. A right-angle plug goes into its socket only when the monitor is out of its place. The owner accepts the 22 on this condition (2026-11-14). The leads have a slack of about 100 in the cable channels for this.

1. Hold the monitor about 100 in front of its place, with the bezel plate off.
2. Push the plugs into the monitor: the mini-HDMI and the USB-C on the left edge.
3. Put the monitor back on the bottom jaws, its glass to the front.
4. Push the two top jaws down onto the top edge, and tighten their lock screws.
5. Put the leads in their ties on the channels. Put the bezel plate on.

### Where the cradle fastens to the body

Each upright has one screw at each end. The screw goes from the front through a lug into the insert in the ear of the upright. The head of the screw is in a counterbore under the bezel plate. The hole in the lug is a slot of 2.5 along the face, so that an upright and a body with different shrink go together.

The lugs are inside the centre pieces of the split: the bottom lugs are on the apron (it ends at `x` 137), and the top lugs are on the brow (it ends at `x` 106).

### The load path

The cabinet is upright. The screen face leans back 30 degrees.

1. The weight of the monitor along the face goes into the two bottom jaws.
2. The lock screw holds each bottom jaw on its upright by friction.
3. The upright puts the load into its bottom lug through the screw and the ear.
4. The lug puts the load into the bottom ledge, in the plane of the ledge. The ledge is the top edge of the apron, and the apron stands on the deck.
5. The weight of the monitor square to the face goes into the four rests, and from them through the uprights into the four lugs.

The uprights also connect the brow to the apron at two points across the opening.

### Load check

These numbers are estimates. `Cradle` names the values that are assumptions: the mass of the heaviest monitor (1.5 kg), the torque of the lock screw (0.4 N m), the share of the preload that stays after PETG relaxes (0.4), the friction of PETG on PETG (0.25), the stiffness and the friction of the pad (0.04 MPa, 0.6), and the shock (3 g).

| Value | Present unit, 0.82 kg | Heaviest unit, 1.5 kg |
| --- | --- | --- |
| Weight | 8.0 N | 14.7 N |
| Along the face, on the two bottom jaws | 7.0 N | 12.7 N |
| Square to the face, into the rests | 4.0 N | 7.4 N |
| Friction of the two bottom jaws (100 N), over the load | 14.4 | 7.8 |
| The same at 3 g | 4.8 | 2.6 |

The cabinet tilted forward (the owner lifts the back by the hand-holds, and the cabinet turns about the front edge of the deck):

| Tilt | Force out of the cradle, present unit | Grip of the pads (21 N) over it | Heaviest unit | Grip over it |
| --- | --- | --- | --- | --- |
| 30 degrees | 0 N | no force | 0 N | no force |
| 45 degrees | 2.1 N | 10.1 | 3.8 N | 5.5 |
| 60 degrees | 4.0 N | 5.2 | 7.4 N | 2.9 |
| 90 degrees (the face down) | 7.0 N | 3.0 | 12.7 N | 1.6 |

Up to a tilt of 30 degrees the monitor leans into its rests. Above 30 degrees only the grip of the pads holds the monitor in the jaws. The bezel plate is a second stop in front of the glass: its magnets hold about 20 N, and the plate weighs 3.3 N (printed) to 7.4 N (solid).

Other results: the bending stress in a lug is 0.08 MPa. A push of 50 N on the middle of the screen gives 0.5 MPa in an upright. PETG takes about 50 MPa for a short load.

The friction of the bottom jaws is the weak point of this design. If the coupon tests show that PETG relaxes more than the estimate, a printed block between each bottom jaw and its ear makes the support positive. The block is not in the model.

## The cable channel

Each side has one channel on the inner face of the side, in the hollow of the rail, from `v` -112 to -12. Its clear section is 21 x 22. It is open toward the edge of the monitor through a slot of 9. Two screws M3 hold it on two bosses.

The channel holds the leads and their slack. The monitor needs a slack of about 100 to come forward before the plugs are pulled.

The leads of the present unit (the owner and the monitor research, 2026-11-14):

| Lead | Diameter (estimate) | Socket on the monitor | Channel | Lead clamp |
| --- | --- | --- | --- | --- |
| HDMI to mini HDMI, picture and sound | 5 to 7 | Left edge, about 49 above the bottom edge | Left | 44.0 from the socket |
| USB-C, power (30 W) | 3.5 to 4.5 | Left edge, the upper USB-C socket, about 86 above the bottom edge | Left | 44.0 from the socket |
| 3.5 mm audio | 3 to 4 | Right edge, about 30 above the bottom edge | Right | 44.0 from the socket |

The sides are those that a person sees from the front. The maker's page confirms the sides. The owner's product pictures agree: one shows two USB-C sockets and the mini HDMI socket on the left edge, and a second shows the button, the wheel and a jack on the right edge. The heights of the sockets are estimates from a render (`docs/research/hardware-envelopes.md`, section 1). The height of the button is measured (63.5).

**The lead clamp.** The small mini HDMI plug must not carry the weight of its lead. The front arm of each channel has four pairs of slots (4 x 2.5) at `v` -88, -70, -50 and -30. A cable tie through one pair holds the leads on the channel. The check measures the distance from each socket to the middle of its tie. The limit is 50.

**The direction of the mini HDMI socket** (given by the owner, 2026-11-14): the socket is on the left edge, and its long axis runs along the edge. The narrow long face of the socket is toward the display (the front), and the wide long face toward the back.

The lead goes down along the edge to the left channel (the socket is at `v` about -68, inside the channel's run from -112 to -12). Thus the plug must turn its lead along the long axis of the socket. With the plug in the socket:

- the lead leaves the plug parallel to the left edge, toward the bottom edge of the monitor;
- the wide face of the plug's body is toward the back of the monitor and the narrow face toward the glass, as the socket has them;
- the body of the plug stands out from the edge by its stand-out, in the plug room of 22.

A plug that turns its lead along the short axis of the socket sends it toward the back of the monitor (or into the glass). It does not suit this place: behind the left edge there are the jaws and the upright, and the lead would not go to the channel. "Up or down", the words of the first version of this document, did not say which axis. The sellers' names for the angles (up, down, left, right, 90, 270) are not the same from one seller to the next, so buy by a picture that shows the lead leaving along the long side of the plug, toward the side where the wide face is not. Check it with the monitor in the hand: the lead must point to the bottom edge.

The stand-out of such a plug is an estimate of 15 to 20, not measured. It fits the plug room of 22 with 2 to 7 to spare. Its body runs along the edge toward the bottom edge, from the socket at about 49 above that edge, so it stays above the bottom jaws. Not measured: the real plug.

The three leads have a total section of about 70 mm2. One channel has 462 mm2. Thus one channel takes all three leads, and each side has a channel for a replacement monitor with other sockets.

The plug room is 22 beside each side edge, as in the fit study. Right-angle plugs are necessary. The stand-out of a right-angle mini HDMI plug is an estimate (15 to 20) and is not measured.

The channels do not touch the cable zones of the fit study (`MonitorCables_Left`, `MonitorCables_Right`): the gap is 1.0.

## The power button of the monitor (an option)

The power button is on the right edge of the monitor, 63.5 above the bottom edge of its housing (measured by the owner, 2026-11-14). With the bezel plate on, it is behind the right bar of the plate.

The monitor turns on by itself when its USB-C socket gets power (the owner's test on the real unit, 2026-11-14). Thus a person does not need the button to start it. The wake from sleep is not tested yet. The owner wants the push rod as a fallback, in case the monitor does not always start. The option is complete and tested. One value, `Cradle.push_rod`, puts it in the document in place of the plain plate. It is off until the owner has seen its mark on the face of the plate (an open decision in the roadmap).

The ways to the button, without a change to the outer form:

| Way | Result |
| --- | --- |
| Through the reveal | Not possible. The reveal is 1 wide and 2 deep, and its floor is the body. The gap between the plate and the jamb is 0.5. |
| From below the bezel plate | Not possible. The apron below the plate is closed, and the gap at the end of the plate is 0.5. |
| The plate off | Possible with no part. Pull the plate off (magnets), push the button with a finger, put the plate back. |
| Through the plate (the option) | A push rod in the inner frame of the right bar. It puts one mark of 4.4 x 4.4 on the face of the plate. |

The option has three printed parts, and they leave with the plate:

- A square push rod of 4 x 4 goes through a hole in the inner frame at `x` 192.5. It stands 1.5 out of the face. Its inner end has a slope of 45 degrees.
- A striker of 6 x 6 moves across the face in a guide. The slope of the rod moves it onto the button. Its nose is 1.0 from the button, and the travel is 2.0.
- The guide is bonded to the back of the plate, in the plug room of the right edge. The present unit has no socket at that height.

The spring of the button moves the striker and the rod back. The option is in `cradle.button_option`. It is not in the default plate. The rod and the striker follow the button: with the measured height of 63.5 they stand 2.5 lower than with the estimate of 66. At that height the checks find no clash with the monitor, the jaws, the skin, the right channel, the lugs, and the pins and the magnets of the plate, and the striker is 1.0 from the button.

**The stop** (2026-11-15). When the plate is off, the rod and the striker stay in their places:

- The rod has a collar behind the plate, 1.5 wider than the rod on each side and 1.0 thick. The collar rests on the back of the plate, so the rod cannot go out to the front. It travels in a pocket of the guide, which stops it after its travel of 2.0 (and the fit of 0.2).
- The tip of the rod goes on past the striker by the travel. The guide has a pocket for it in its back wall. Without this pocket the rod stopped on the back wall after about 1.2 of its travel, so the striker reached the button but pressed it by about 0.2 only. This was a fault of the first design.
- The guide has a lip of 1.0 across the upper half of its open end. The upper half of the striker is cut back near its nose, so that its step stops on the lip just past the travel. The lower half of the striker still reaches the button.

**The sheet for the owner** (`cad/out/push-rod-mark/push-rod-mark.png`, made by `candybar.shell.rod_mark` and `tools/draw_push_rod.py`): the front of the cabinet with the printed bezel plate, without the rod and with it, from one camera 1.0 m in front of the screen; the same place of the two views at the size of the render (3.5 pixels for each mm); and a close view of the right bar with the mark and a ruler of 1 mm ticks. Every face edge is drawn.

`tests/test_cradle.py` holds the stop: the rod cannot go out to the front, the full travel of the rod and of the striker is free, and each one is stopped 0.5 past its travel and the fit.

## The bezel plate as a printed part

### The choice: two halves

| Way | Pieces | Seams on the face | Print |
| --- | --- | --- | --- |
| Two halves, seam on the centre line (chosen) | 2 | 2 seams of 45 (top bar and bottom bar) | On the outer side face, 216.8 high |
| Four bars with mitres | 6 | 4 mitres of about 51 and 2 seams of 45 | On the outer edge of each bar |

The top bar and the bottom bar are 434.7 long. The longest part on the bed diagonal is about 339 less its width. Thus a bar of that length is two pieces, and the four bars are six pieces. The halves have fewer seams for the same face. The sheet `01b-bezel-plate-options.png` shows the two ways.

A cut plate (`split.BEZEL_OPTIONS`, option 3) is not examined: the owner said that each part is printed.

### How a half prints

A half stands on its outer side face. The side bar lies on the bed along the bed diagonal (304.4 x 18.4, the diagonal needs 228.3 of 240). The two half bars stand up, and the cut faces are on top at 216.8.

- The land, the inner frame and the rim wall are walls or face up. No face that shows has a support.
- `split.BEZEL` puts the half on its cut face. In that position the rim wall of the side bar faces down over a length of 215 (from the geometry; it is not sliced). This document does not use that position.
- The layers are square to the plane of the plate. Thus the shrink of a layer does not curl the plate out of its plane.
- The faces that look down are the roofs of the two magnet pockets, of the two pin slots and of the dowel holes, and the first layers of the edge break beside the bed (301.5 mm2 in total). The edge break beside the bed is on an edge that shows. It needs a light sanding before primer.

Two dowels of 4 in each seam put the halves in line. The seams are bonded, filled and painted with the plate.

### What does not change

The front of the plate is the form of `solids.bezel`: the land on its cylinder, the inner frame, the rim wall and the window. A test compares the plate with that form. The recess and the reveal in the body do not change.

### What changes

- **The fit.** The printed plate is 0.5 smaller than its recess on each side and at each end (`plate_fit`). In `solids.bezel` the plate has no clearance to the walls of its recess. From the front, the gap of 0.5 lies beside the reveal at the sides, and it is a shadow line at the top and at the bottom.
- **The edge break.** 12 edges have a round of R 1: the 4 edges between the inner frame and the rim wall of the window, the 4 edges round the land, and the 4 corners of the outline. The plate has 12 faces of the break and 4 corner balls. No convex edge that shows is sharp.
- **The back.** Four slots for the pins and four pockets for the magnets.

### Known items of the face check

| Item | Count | Reason |
| --- | --- | --- |
| Corner of the window: a face of 0.2 mm2 with a narrow tip, and a point where 5 edges meet | 4 corners | OpenCascade does not make the round on the four edges of the window in one step. The module makes the top edge and the bottom edge first, and then the two side edges. Where two rounds meet in the concave corner, OpenCascade makes a small patch. |
| Rim wall of the window, 1.3 to 1.4 wide | 4 | The rim wall is 2 deep by design (`bezel_rim`). The edge break takes 0.6 to 0.7 of it. |
| Corner ball, 1.15 wide | 4 | The ball where three broken edges meet at a corner of the outline. |

## The mount of the bezel plate

### The decision: magnets and pins

The owner decided this way on 2026-11-15 ("Bezel plate should definitely be magnets"). Pins put the plate in its place, magnets hold it, and no screw is used.


- **Rest.** The back of the plate lies on the two ledges and on the four lugs.
- **Location.** Four dowel pins of 4 x 12 are pressed into the lugs at `x` 50 and `v` 143 on each side, at the top and at the bottom. Each pin goes 6 into a slot in the back of the plate. A slot is 4.3 wide and lets its pin move 2 each way. The long axis of each slot points at the centre of the image.
- **Hold.** Four pairs of disc magnets 8 x 3, at `x` 38 and `v` 143: one in each lug and one in the back of the plate. The estimate is 5 N for each pair.
- **To take the plate off.** Put the fingernails or a card behind the bottom rim of the window and pull. The gap of 1.0 between the plate and the glass makes room for this.

The radial slots keep the centre of the plate on the centre of the image when the plate and the body shrink by different amounts. The plate goes back in the same place, because four pins of 4 in slots of 4.3 leave a play of 0.15.

The fastening has no part on the face of the plate.

### The other way: screws (not chosen)

Two screws through the top of the inner frame into the top lugs hold the plate without magnets. They are positive, and they need no pull on the rim. But their heads are on the face of the plate. The owner asked for a plate with no mark on its face and chose the magnets, so this way is not built. The code has no screw option for the plate.

Screws that are hidden need access from the front, and the only faces in front of the lugs are the faces of the plate. A hole of 3.5 for the key on the seam beside the plate is a third way. It makes a notch in the edge of the plate and in the rail land.

## The interface for other bezel plates

A plate for another aspect ratio (16:9, 4:3, vertical) must match these items. The function `cradle.bezel_plate` is the reference.

| Item | Value |
| --- | --- |
| Outline | 433.7 x 304.4: the recess of `solids.bezel_box` (434.7 x 305.4) less 0.5 on each side and at each end. The ends are square to the chord of the rail arc. |
| Front | The land is on the cylinder 2 below the rail arc (`bezel_drop`). The land is 20 wide (`bezel_land`). |
| Back | Flat, on the plane `t` = 7.2 (`mon_setback` behind the screen face). |
| Rest faces | The back, in the two strips of 6 at the bottom end and at the top end (the ledges), and on the four lugs: `x` 30 to 72 on each side, `v` 135.6 to 152.7 at the bottom and at the top. Nothing stands behind the back plane there. |
| Locating slots | Four, at (`x`, `v`) = (+-50, +-143). Each is 4.3 wide, 8 long and 6.5 deep, with its long axis on the line to the centre of the image. |
| Magnets | Four pockets of 8.2 x 3.1 in the back at (+-38, +-143). The poles must attract the magnets in the lugs. |
| Screw heads | The heads of the four upright screws are at (+-66, +-143). They are below the plane of the back. |
| Window | It is free, inside the land. Its rim is 2 thick (`bezel_rim`), and the glass is 1.0 behind the back. |
| Edges | The edge break of R 1 on each convex edge that shows. |

The window of a 16:9 or a 4:3 plate is smaller than the lit image. A vertical plate needs a monitor on its side, and the uprights and the jaws of this proposal do not hold that. It is a separate design.

## Shrink

The cabinet is printed in ABS on a Qidi Q2 (decision record 0008). One study measured printed ABS 0.59 % to 0.69 % short in X and Y (`docs/research/abs-on-the-q2.md`), and the model uses these values (`Cradle.shrink`). The monitor does not shrink. The print checks use the limit of the Q2 from `cad/params/printer.csv` (248 x 248 x 250). The table that follows has the numbers of the server for the PETG values (0.54 % and 0.76 %); `cad/out/cradle/report.md` has the numbers for ABS.

| Value | As designed | 0.54 % | 0.76 % |
| --- | --- | --- | --- |
| Opening | 434.7 x 293.4 | 432.3 x 291.8 | 431.4 x 291.2 |
| Present unit with plugs, room on each side | 18.3 | 17.2 | 16.7 |
| Any unit with plugs at full adjustment, room on each side | 7.3 | 6.2 | 5.7 |
| Present unit, room at the bottom and at the top | 29.4, 34.0 | 28.6, 33.2 | 28.3, 32.9 |
| Any unit at full adjustment, room at the bottom and at the top | 15.2 | 14.4 | 14.1 |
| Lock screw of a jaw, inside the edge of the opening (any unit, full adjustment) | 4.2 | 3.4 | 3.1 |

- The cradle has no part that goes through the opening with the monitor. The fit study had side flanges of 4 on a carrier, which left 3.3 on each side. This proposal has no carrier and no flange.
- The adjustment is on the jaws. It sets the image to the window, and the window follows the pins. Thus a shift of the opening does not move the image out of the window.
- If the plate and the body shrink by the same amount, the gap round the plate does not change.
- If the plate and the body differ by the full spread (0.22 %), a pin moves 0.33 along its slot (the slot takes 2). The gap round the plate decreases from 0.5 to 0.02 at each side and to 0.16 at each end. The plate does not jam, but the margin is small. The joint coupon gives the real shrink. Then the slicer can scale the plate.
- The uprights are 301.2 long. With the full spread, the screw holes of an upright and its lugs differ by 0.63. The slot of 2.5 in each lug takes this.

## Checks

The command `candybar.shell.cradle` writes `cad/out/cradle/report.md` and `report.json`. Result: PASS.

| Check | Result |
| --- | --- |
| Solids | Each part is made of valid closed solids (9 parts, and the two halves). |
| Clash | 183 pairs: each part against the skin, against each other part, against the monitor and its plug room, and against each solid of the compute module, the speakers, the marquee and the monitor cables of the fit study. No pair has a common volume. |
| Smallest gaps | Uprights to the lugs 0.2. Plate to the glass 1.0. Jaws to the plate 1.5. Uprights to the skin 2.15. Channels to the skin 5.0. Channels to the cable zones of the fit study 1.0. |
| Added solids | Each lug has 1516 to 1519 mm3 in common with the skin, and each boss has 78.5 mm3. They are one solid with the skin. |
| Way out | The present unit with its plugs, and any unit with its plug room at full adjustment, at 0, 30, 60 and 150 out: no common volume with the skin, the lugs, the bosses, the uprights and the channels. The prism of 200 that any unit passes through has no common volume, and its smallest gap is 1.0. |
| Sight lines | The same as in the fit study: the child of 8 loses 0.4 of the image at the bottom, and the adults lose nothing. |
| Edge rule on the plate | 12 faces of the break. The 32 convex edges that stay sharp are those of the back, against the monitor. |
| Face check | No finding without a reason. The known items are in the table of the plate, and one more: the seat of the M4 nut in each shoe is a ring 1.25 wide. |
| Lead clamps | Each of the three leads has a tie 44.0 from its socket (the limit is 50). |
| Power-button option | The three parts and the plate with the hole are valid solids with no clash. The striker is 1.0 from the button. |
| Print | Each part fits 240 x 240 x 245. |

The skin comes from the cache of the split. On this machine FreeCAD 1.1.4 says that this skin is not a valid shape, and the booleans with it give results that agree with the sections. The fit study is not run again: the positions of the hardware come from `fit/report.json` of the built shell.

## Print

| Part | Count | Position on the bed | Box | Flattest underside | Solid mass |
| --- | --- | --- | --- | --- | --- |
| Bezel half | 2 | On its outer side face, on the bed diagonal | 304.4 x 18.4 x 216.8 | The outer side face, 304 x 10 to 18 | 374 g |
| Upright | 2 | On its back, on the bed diagonal (needs 238.4 of 240). The ears stand up. | 301.2 x 36 x 32.4 | The back of the bar, 301 x 24 | 120 g |
| Jaw | 4 | On a side face | 32 x 25.1 x 23 | The side face, which is the whole profile | 12 g |
| Shoe | 4 | On its back. The lip stands up. | 25.2 x 14 x 10 | The back, 25 x 14 | 3 g |
| Cable channel | 2 | On one end. The roofs of the tie slots are bridges of 4. | 28 x 27 x 100 | The end face, which is the whole section | 34 g |

The lugs print with the apron and the brow. The apron stands with the chord of the screen face upright, so the bottom lugs are at its top. The back of each lug ends in a slope of 45 degrees.

The brow is "upright" in the split. In that position the top lugs hang 11.1 below the ledge, which is on the bed. Two ways are possible: the brow prints on its top face (the level face under the hood seam), or the two top lugs are separate blocks that are bonded to the ledge. The first way is not examined in a slicer.

## Assumptions

1. A jaw is printed for one monitor. A new monitor of a different thickness gets four new jaws.
2. The heaviest 16 inch 16:10 unit is 1.5 kg. The survey gives the mass of the present unit only.
3. The glass 1.0 behind the plate is permitted. In the fit study the gap is 0.
4. A plate that is 0.5 smaller than its recess is permitted.
5. The estimates of the load check, as the section "Load check" names them.
6. The magnets and the pull at the rim are not tested on a real part.
7. The sockets and the power button of the present unit are where the research note and the product pictures show them. The real unit is not measured.
8. The material values of the load check are for PETG. ABS is not examined.

## Not done

- No slicer run on a part.
- No real test of the magnets, the pads and the lock screws.
- No printed stop under the bottom jaws.
- No plate for 16:9, 4:3 or vertical.
- No mount for the DisplayPort to HDMI adapter, the USB-C power board or the amplifier. The channels end at the cable zones of the fit study.
- The lugs and the bosses are not in the pieces of the split. `split.py` does not know them.

## On the main line

Date: 2026-11-14. The package was merged on the laptop after the control panel. What changed:

- **The owner's measurements and facts.** The power button is 63.5 above the bottom edge of the housing (it was an estimate of 66). The bottom bezel is 8.9 (it was an estimate of 9.6), so the cradle puts the bottom edge of the housing 8.9 below the lit picture. The side bezels are 4.0 and the top bezel 3.4; across the face the monitor is set by hand on its pads, so the side bezels change no value of the model. The width and the height of the housing stay the maker's 354 x 230 until the owner measures them, and the reserved room of 356 x 231 x 11 stays. The top jaws hold the top edge of the housing, which the model puts 230 above the bottom edge: that value needs the real height of the housing, and it is in the list of things to measure.
- **The window and the picture.** The rim of the window lies on the edge of the lit area (BZ3 is made from the lit area). With the monitor where the cradle puts it, the margin between the window and the lit picture is 0 at the left, at the right, at the bottom and at the top. With the old bottom bezel of 9.6 the picture would have stood 0.7 low: 0.7 of it behind the rim at the bottom, and 0.7 of black bezel in the window at the top. The jaws move 8 each way, so a person sets the picture to the window by hand in any case.
- **The push rod.** `Cradle.push_rod` (off) puts the option in the document. It is tested as before, at the new height of the button.
- **The mini HDMI plug** is described by its geometry (see "The cable channel").
- **The plug order** is in the steps "How to put the monitor in".
- **ABS.** The density is 1.05, the shrink 0.59 % to 0.69 %, and the print limit that of the Q2.
- **The skin.** On the laptop the skin of the cache reads as a valid shape.
- **The thickness** of the housing is the owner's measurement (see "The thickness of the housing").
- **The fit study** reads the measured bottom bezel too (`mon_bezel_bottom` 8.9 in `cad/params/hardware.csv`, status measured), so that its monitor and the cradle's monitor are one body. It passes.
- **The checks of the push rod** now include the pins and the magnets of the plate: no common volume.
- **The tools.** `tools/edge_finish.py` has the two halves of the plate as printed parts, with two named joints (the screen behind the window, and the other half at the seam), and the upright, the jaw, the shoe and the channel in a new class: printed parts inside the shell that are not painted. `tools/face_check.py` takes the known items of this module (`cradle.face_known`). Both pass when they run on `cad/out/cradle/print`.
- **The bezel plate of the default build** is now in the class "provisional" of the edge tool: a stand-in for the printed plate of this module, because the owner chose a printed plate. The default build keeps the plain plate of the form.
