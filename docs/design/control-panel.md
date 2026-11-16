# Control panel

Date: 2026-11-14. Roadmap step 12. This document is a proposal. The owner did not review it.

A control panel is a service part. It lifts out of the pocket of the deck, and a different control panel goes in. This document describes the arcade panel as printed parts, the frame that stays in the cabinet, the latch, the cable, and the interface that all control panels share.

Since 2026-11-16 the latch is the push bolt of `docs/design/control-panel-latch.md` (the owner's choice of 2026-11-15, candidate B of the latch study). It is the default of the build. The screws stay as the fall-back option, and the magnets alone stay as an option.

The source is `cad/candybar/shell/panel_frame.py`. The tests are in `cad/tests/test_panel_frame.py`. The build output is `cad/out/control-panel/` (not in git).

All dimensions are in millimetres. The frame of reference is that of `dims.py`. A depth with the name `yl` is a distance from the front edge of the panel at the centre line (y - 26).

## The parts

All parts are printed in ABS. The mass is the mass of the solid volume at 1.05 g/cm3.

| Part | Quantity | Function | Box on the printer | Mass, g |
| --- | --- | --- | --- | --- |
| `frame_left` | 1 | The left half of the frame, with the tunnel of the push bolt. It stays in the cabinet. | 217.2 x 174.0 x 19.1 | 80 |
| `frame_right` | 1 | The right half of the frame | 177.2 x 174.0 x 19.1 | 64 |
| `post_*` | 4 | A post between the floor and the frame | 38.6 x 20.0 x 7.5 | 6 |
| `latch_bolt` | 1 | The push bolt: a bar with the flush button at its front. It stays in the cabinet. | 52.5 x 52.2 x 15.0 (on its side) | 5 |
| `latch_gate` | 1 | The gate at the rear of the tunnel. It holds the spring of the bolt. | 19.0 x 12.3 x 7.6 | 1 |
| `panel_lever_tile` | 1 | Arcade panel: the lever and the encoder | 174.4 x 158.7 x 20.0 | 208 |
| `panel_button_tile` | 1 | Arcade panel: the buttons, the strike of the latch | 236.7 x 174.4 x 20.5 | 213 |
| `blank_left_tile`, `blank_right_tile` | 1 each | The blank panel, which proves the interface | 197.7 x 174.4 x 20.5 | 210, 208 |

The rear hooks and the strike print with the tiles of each panel. The outer form changes in one place only: the hole of the button in the deck nose (`Blueprint.latch_button_d`, a decision of 2026-11-15). All other parts are inside the opening that `cavity.Openings` makes below the control panel.

Bought parts for the arcade panel and the frame:

- 4 disc magnets N52 12 x 2, axial, for the frame (once), and 4 steel discs 12 x 2 for each panel (the user's decision of 2026-11-16: no pole to mind). Epoxy for both.
- 1 compression spring, steel, 4 outside, 22 free, about 1.2 N/mm, for the push bolt.
- 4 heat-set inserts M4 for the lever, and 4 screws M4 for its plate.
- 4 screws M3 x 12 with nuts for the seam between the two tiles.
- 4 thread-forming screws 3.0 for the encoder.

The latch has no screw and no insert. The fall-back option (screws) needs 4 screws M4 x 16, countersunk (ISO 10642), and 4 heat-set inserts M4 x 8.

## The plate

The outline is `profiles.panel_outline(d)`, moved in by 0.3 (`seat_gap`). Thus the front edge follows the deck. The top face is at `panel_top` (z 70), 2 below the deck top, as the form has it. The plate is 5 thick (`panel_t`), and its lower face is the rest face (z 65).

The plate is 396 wide, and the printer takes 240. Thus the arcade panel is two tiles. The seam is at x -39, which is 36 to the right of the lever. It goes through the corridor of 10 between the lever body and the nut of the first button. Each tile has a flange of 4 x 15 along the seam. The two flanges are bonded and held by four M3 screws. The seam is also the strongest rib of the panel.

Holes, from the positions of `fit.Layout` and the parameter sheets:

| Hole | Diameter | Position |
| --- | --- | --- |
| Lever shaft | 24 | x -75, yl 87.5 |
| Lever inserts (4) | 5.6, 6.5 deep from the seat | 40 x 85 round the shaft |
| Action buttons (8) | 30.3 | Sega Astro City layout, from the lever |
| Service buttons (3) | 24.3 | x 160, yl 42.5, 87.5 and 132.5 |
| Latch points (4) | A pocket of 12.2 x 2.2 from below for a steel disc of 12 x 2 | The four latch points |

A printed hole is drawn 0.3 larger than the hole of the data sheet (`hole_allow`). A coupon must confirm this value.

**The buttons are screw-in buttons** (`Arcade.buttons = "spread"`, Sanwa OBSN-30 with nuts of 36 across). The owner uses screw-in buttons (2026-11-14). In the layout of the parameter sheets three pairs of nuts overlap by 0.15 to 0.28. Thus the layout of the action buttons becomes 1.02 times larger about its middle, and the nearest pair is 36.4 apart. The plate keeps its full thickness of 5 round each hole, which is the largest panel that Sanwa gives for these buttons. The hole is 30.3 (30 and the print allowance of 0.3). The envelopes of the buttons in the checks of this module stand at the spread places. The other value is `"snap-in"` (Sanwa OBSF): the layout of the sheets, and a counterbore from below round each hole, 2 wide, so that the plate is 3.0 thick there (`seat_t`), because a snap-in button holds in a plate of 3.9 or less. The ribs keep clear of the nut envelopes, so both values fit.

The lever bolts below a pad. The seat of the pad is 9.25 below the top face (`stick_plate_drop`), which gives the standard lever height. The pad is 9.25 thick and goes from the rib beside the encoder to the flange of the seam.

Ribs, all 15 deep below the plate:

| Rib | Position | Thickness |
| --- | --- | --- |
| Front rib | yl 20 to 23, x -164 to 164 | 3 |
| Rear rib | yl 150 to 153, x -140.3 to 164 | 3 |
| Rib beside the encoder | x -140.3 to -137.3, between the encoder and the harness of the lever | 3 |
| Flanges of the seam | x -43 to -35 | 4 + 4 |
| Rib beside the service buttons | x 126.5 to 130.5 | 4 |

The button field has no rib, because the nut envelopes touch each other.

The encoder hangs below the left end of the plate on four bosses of 8 x 4, at the position of `fit.Layout`. The hole pattern is that of the RP2040 Advanced Breakout Board (36.95 x 87.96).

The top edge of the outline has the edge break of R 1, because it shows in the reveal. The four upright corners of the plate have the same break, so that the round goes round each corner with no mitre. At each corner the three rounds meet in a ball of R 1, as on the hood. The top edges of the holes are sharp. The rim of each button and the dust washer of the lever cover them.

Below the plate each panel has the parts of the latch: two rear hooks at x -100 and +100, and the strike at the front centre (yl 20.5 to 24.5). A rib that crosses the room of the bolt stops at it: the front rib of the arcade panel and the seam of the blank panel.

## The frame

The frame is a ring of two halves, with a gap of 0.5 between them at x 20 (not on the centre line: the tunnel of the bolt is whole in the left half). It is bonded below the ledge of the opening, with a bond gap of 0.2.

- **The bar** is 7.7 wide and 12 high. It lies below the ledge, which is 8 wide and 4 thick.
- **A pad** stands in each corner of the opening (radius 21). It has a magnet of 12 x 2 in a pocket of 12.2 x 2.2. Its two straight sides lie 0.2 from the edges of the opening. Thus the four pads locate the frame in the opening.
- **Two smaller pads** (radius 12) stand at the rear edge, at x -120 and x +120. Each has a locating cone: 8 at its base, 5 at its top, 3 high.
- **Two notches** in the rear bar, at x -100 and +100, take the toes of the rear hooks.
- **The tunnel** of the push bolt is a part of the left half: a floor under the bolt from the front bar to the rear of the tunnel, two walls and a roof round the bolt behind the strike, a shoulder that stops the bolt, and a slot for the gate. The bolt passes the front bar through a notch.
- **The anchor** of the cable is a clip at the rear edge, at x -80.
- **Four posts** (20 x 7.5) stand between the floor and the bar, at x -66 and x +66, at the front and at the rear.

**Rest.** The plate rests on the ledge of the skin, all round. The tops of the pads are 0.1 below the rest face, so that the plate does not rock on a pad.

**Location.** The plate stands 0.3 inside its seat. The two cones locate it: the panel has a round socket at x -120 and a slot along X at x +120 (clearance 0.15). The slot lets two prints differ in size. The panel goes in one way only: its front edge has two corners that its rear edge does not have, and the two sockets are different.

**Flush.** The top of the plate is in the plane of the step of 1 that the pocket has round the panel (z 70). The rest face and the thickness of the plate set this height.

**The load of the lever.** The lever puts a couple on its seat. The ribs on each side of the seat carry it to the front and rear edges of the plate. One edge pushes down on the ledge: the bar and the posts below it carry this to the floor. The other edge pulls up: the rear hooks, the bolt and the magnets carry this into the frame, and the bonded bar carries it into the skin of the deck. No load goes through a painted seam.

## The latch

All panels use the same four latch points. Each is 12.5 from a corner of the opening, on the line that divides the corner in two: (-180.6, 49.8), (180.6, 49.8), (181.2, 184.2) and (-181.2, 184.2) in x and y. `Interface.latch` selects the latch:

| | The push bolt (the default) | A. Screws (the fall-back) | B. Magnets alone |
| --- | --- | --- | --- |
| Parts | Two rear hooks and a strike on each panel; a printed bolt in a tunnel of the frame, its gate and one spring; a magnet of 12 x 2 in each pad and a steel disc of 12 x 2 above it in the plate | A flush M4 x 16 countersunk screw in each latch point, into a heat-set insert in the pad | A magnet of 12 x 5 in each pad, a magnet of 12 x 2 in the plate above it |
| Tool | None | A 3 mm hex key | None |
| Hold (ESTIMATED) | One latch point holds 14.1 N. In the worst load case the hold has a factor of 2.85; in normal play the preload has a factor of 7.3 (no click). | Preload from the screws | 20 N for each point: a hard input can lift an edge |
| On the top face | Nothing. A flush button in the front face of the deck, on the centre line | Four screw heads, 9 across | Nothing |

The values of the push bolt are in `panel_frame.PushBolt`, and `docs/design/control-panel-latch.md` has its study: the hold, the way out, the wedge, the failures, the print and the wear. Each option builds and passes the checks of this module (a test holds this).

**To take a panel out.** Push the button in and hold it: the bolt slides back 5, and the lips of the strike are free after 4.25 (9.3 N at the start, 15 N at the end of the travel). Lift the front edge by the lever (49.2 N, ESTIMATED) or, a panel with nothing to hold, by its finger hole of 22 (31.1 N). The panel turns about its rear edge; lift it up and forward. Release the button.

**The lift-out force.** About 55 N on the lever is the starting value (the user, 2026-11-16). With steel discs in the panel the estimate is 49.2 N; with a magnet pair it is 55 N. After the first print, the size of the front magnets is the value to change: weaker front magnets give less force, but then the front corners can click in hard play.

**The button.** The button is the outline of its hole moved in by 0.3 (`panel_frame.button_outline`): a round of 14, two flats 12 apart, and four corners of R 1.2 concentric with the hole's corners of R 1.5 (`solids.LATCH_CORNER`). Thus the gap is 0.3 all round, also at the corners (a test measures it). Before 2026-11-16 the button's corners were sharp in a hole with corners of 0.5, and the gap at the four corners was 0.292. The button's rim and the hole's rim have the edge break of R 1.

## The cable

One USB cable is the only connection of a panel. Each panel has its own encoder.

- The encoder is below the plate, at the left end. Its USB socket points to the rear. The room behind it is 31, so the plug must be a right-angle plug.
- The cable goes through a gate in the rib beside the encoder (8 x 7) to a clip below the plate at x -93, yl 145.5. The clip is the strain relief: a bore of 4.2 with a mouth of 3.4. The cable goes in through the mouth with no tool.
- A second clip of the same form is on the frame, at the rear edge, at x -80.
- Between the two clips the cable has 300 of slack, which lies on the floor of the deck. This is sufficient to lift the panel out and to put it on the deck with its lower face up.
- To change the panel, remove the cable from the clip of the panel and disconnect it from the encoder. The cable stays in the cabinet.

The research note recommends a direct connection to a USB 2.0 port of the BC-250, not through the hub.

## The interface of every control panel

A control panel that agrees with this table goes into the cabinet. The values are in `panel_frame.Interface`.

| Item | Value |
| --- | --- |
| Outline | `profiles.panel_outline(d)` moved in by 0.3. 396 wide, 175 deep at the centre line, 166.4 at the sides. |
| Upright corners | R 1 on the four corners. The two blunt corners of the front edge stay. |
| Top face | z 70 (`panel_top`). The top edge of the outline has a round of R 1. |
| Rest face | z 65, flat, 8 wide all round (the ledge). The plate is 5 thick at its edge. |
| Latch points (4) | 12.5 from each corner of the opening. A pocket of 12.2 x 2.2 in the lower face for a steel disc of 12 x 2 (the screw option: a hole of 4.5 with a countersink of 9). |
| Rear hooks (2) | At x -100 and +100, 14 wide. A stem 6 thick, its rear face at yl 165.8. A toe whose top and bottom are arcs of R 16.5 and R 20 about the rear top edge of the plate (yl 174.7, z 70). Its tip at yl 170.6. |
| Strike (1) | At the front centre, yl 20.5 to 24.5. Two legs at x 6.2 to 13.2 each side of the centre line, down to z 49.5. Each leg has a lip 3.4 in under the bolt. The top of each lip falls 8 degrees to the rear. |
| Sockets (2) | At the rear edge, 6.5 inside the opening: a round socket at x -120, a slot (3 long) at x +120. Each is 8.3 across at the rest face, 5.3 at its end, and 3.3 deep. |
| Cable clip | Below the plate, x -93, yl 145.5. One USB cable. |
| Room below the plate | The opening less 0.7, from z 65 down to z 12, less the box of the bolt (x -16.5 to +16.5, yl 0.5 to 55, z 48.3 to the rest face). Not in the room: a circle of 21.5 round each corner of the opening, a circle of 12.5 round x -120 and x +120 on the rear edge, the anchor clip at x -80, and the space of the USB sockets (x more than 181, z less than 32.5). Volume 3015 cm3. |
| Ribs | Free in the room. The front rib and the rear rib of the two built panels are at yl 20 and yl 150. |
| Tiles | A panel is wider than the printer. Its seam can be at any x. The seam has a flange on each tile. |

The blank panel is made from these values only. It has a seam on the centre line and a rib at a quarter of the width on each side. It goes on the same frame. It has nothing to hold, so it has a finger hole of 22 at x 50, yl 37, with the edge break on both rims (the user, 2026-11-16). The finger hole is a choice of the panel, not a row of the interface. Sheet 07 shows it.

For the PC panel: a 60 % keyboard needs 14 below the plate top. The room is 53 deep below the rest face.

## Checks

`candybar.shell.panel_frame` does these checks on the real skin of the deck (from the cached skin of the shell) and on the hardware of the fit study. All pass.

| Check | Result |
| --- | --- |
| Each part against the skin of the deck | 0.0 mm3 in common, for each of the 12 parts |
| Each part against each other part | 0.0 mm3 |
| Each part against the lever, the buttons, the encoder, the USB sockets and the hub (envelopes and keep-out zones) | 0.0 mm3. The fit rules permit 1. |
| Smallest gaps | Frame to the encoder 1.8. Frame to the nut of service button 1: 4.3. Frame to the USB sockets 18.3. Seam flanges to the lever body and to the nut of button 1: 1.0 each. Rib to the encoder 2.3. |
| The room below the plate | Free of the skin, the frame, the posts, the USB sockets and the hub. The arcade panel and all its hardware are in the room. |
| The way out | With the button held, the arcade panel with its hardware and the blank panel turn up about the rear edge and then go up and forward: at each of 19 steps, 0.0 mm3 in common with the deck, the frame, the gate and the bolt. The bolt alone at four places of its travel: 0.0 mm3. The options A and B lift straight out. |
| The lock | A lift of 1 makes the toes meet the roofs of their notches; a swing of 2 degrees with the bolt forward makes the lips meet the bolt. |
| Edge rule | No sharp convex edge shows on a top face or on the front of the button. |
| Face check | No finding fails. The allowed items are the rounds of the edge break, the corner balls of the plates and the four corner faces of the button (0.7 wide, a corner of 31 degrees). |
| Print | Each part fits 240 x 240 x 245. |

The edge rule of this module: a sharp convex edge passes only if one of its faces lies against a cover. The covers are the seat of the plate, a hole through the plate, the room below the plate (behind y 4: the front of the button shows), and the other tile. On the top face, only a hole and the bonded seam hide an edge. A test makes sure that a plate with no edge break and a button with no edge break fail.

### Deflection

This is a hand estimate with beam theory. E is 2000 MPa (printed PETG, ESTIMATED).

The load is 40 N on the ball, 60 above the panel. This is the upper value of the research note (section 6.3: 20 to 40 N). It is a couple of 2.4 N m at the seat of the lever. The bay of the lever is the plate between the rib beside the encoder and the flanges of the seam, 105 wide. It rests on the front and rear ledges, 159 apart.

| Case | Push forward: ball moves | Push sideways: ball moves |
| --- | --- | --- |
| With the ribs | 0.04 | 0.12 |
| A flat plate of 5 with no ribs | 0.63 | 1.59 |

A load of twice this value gives twice the movement: 0.08 and 0.24.

A hand of 100 N on the middle of the button field moves the plate 1.2 (0.12 for each 10 N). The field is 159 x 161.5 and has no rib. A button needs less than 2 N.

The estimate does not include the deflection of the ledge, the frame and the deck. A finite element analysis was not done.

## Print

| Part | Orientation | Flattest lower face | Faces that look down more than 45 degrees |
| --- | --- | --- | --- |
| Tiles | Top face on the bed. The ribs, the hooks and the strike point up. | The top face: 265 to 337 cm2 | 4.2 to 5.5 cm2: the round of the edge break at the bed, the toes of the hooks and the lips of the strike |
| Frame halves | As in the cabinet. The lower face of the bar is on the bed. | 67.5 and 47.7 cm2 | 3.8 (left: the roofs of the tunnel and of a notch, bridges) and 0.7 (right: the roof of a notch) |
| Posts | On the wide side | 7.7 cm2 | 0 |
| Bolt | On its side: the flat side on the bed | 3.5 cm2 | 1.0: the round of the button and the bore of the spring |
| Gate | Flat: its rear face on the bed | 2.3 cm2 | 0 |

No part needs support. The top face of a tile gets the surface of the bed plate. The round of R 1 at the bed starts with a short overhang. If it does not print cleanly, a flat break of 1 is the alternative.

## Build

```sh
CANDYBAR_OUT=cad/out/control-panel cad/candybar/freecad-run.sh candybar.shell.panel_frame          # parts, checks, report.md
CANDYBAR_OUT=cad/out/control-panel cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc        # shell.FCStd
cad/.venv-tools/bin/python cad/tools/draw_panel.py                                                 # renders and sheets
cad/test.sh test_panel_frame                                                                       # the tests of this module
```

The first command needs the skin of the shell in `cad/out/shell-rev7/split/cache`. It takes about 4 minutes; the way out of the push bolt is most of it.

| Output | Content |
| --- | --- |
| `report.md`, `report.json` | The results of the checks |
| `shell.FCStd` | The deck, the frame, the arcade panel and its hardware in position. The blank panel is 260 in front of the deck. |
| `parts/` | The 12 printed parts as BREP and STL |
| `scenes/`, `renders/` | The models and the renders of the sheets |
| `sheets/01` to `07` | The panel from above, the panel lifted out, the section through the lever, the push bolt (the button in its hole, the rim of the hole, the section through the bolt locked and with the button in), the latch options, the panel from below, the blank panel with its finger hole |

## Assumptions

1. The top of a control panel is 2 below the deck top, as the outer form has it. "Flush" means flush with the step of the pocket.
2. The buttons are Sanwa OBSF snap-in buttons. The parameter sheets have the sizes of the OBSN screw buttons, and the envelopes of the fit study keep the nuts.
3. The seat gap is 0.3, the bond gap 0.2, and the hole allowance 0.3. A coupon sets these values.
4. The printed floor is 10 thick (`fit.Layout.floor_t`). It is not a part of the model. The posts stop at z 10.
5. The plug at the encoder is a right-angle USB-C plug.
6. The encoder is the RP2040 Advanced Breakout Board, with its USB socket to the rear.
7. The pilot hole of the encoder screws is 2.6 for a 3.0 thread-forming screw. The joint coupon gives 2.25 to 2.4, and a disc below 2.55 across fails the face check.
8. The hold of the magnets is an estimate from supplier data. It is not tested. A steel disc of 12 x 2 gives about 10 % less than a magnet of 12 x 2 (ESTIMATED).
9. The frame is bonded. The owner does not disassemble the shell.

## Open questions for the owner

1. The latch: answered on 2026-11-15. The push bolt (`docs/design/control-panel-latch.md`); the screws are the fall-back.
2. The buttons: answered on 2026-11-14. The owner uses screw-in buttons, so the spread layout is the default. Snap-in stays as the option.
3. The top of the printed plate is 2 below the deck top. A cover of 1.5 with art makes it 0.5 below. Is this the look that the owner wants?
4. The corners of the plate have R 1 and the corners of the pocket are sharp. The gap at each corner is 0.7 on the diagonal.

## For the shared files

The hand-over of 2026-11-14. It is done ("On the main line").

Glossary (`CONTEXT.md`):

- **Panel frame**: The printed ring below the ledge of the deck's opening. It has the latch points, the locating cones and the cable anchor, and it stays in the cabinet. _Avoid_: carrier, subframe.
- **Ledge**: The strip of deck skin round the opening below a control panel. The control panel rests on it.
- **Latch point**: One of the four positions where a control panel is held down on the panel frame.
- **Seat** (of a control panel): The recess in the pocket that the plate of the control panel fills.
- **Blank panel**: A control panel with no hardware, made from the interface only.
- Change **Tile**: the arcade panel has a lever tile and a button tile, with a bonded seam at x -39.

Roadmap (`docs/roadmap.md`):

- Step 12: the control panel is designed as printed parts (`docs/design/control-panel.md`). The cut plates and their drawings are not done.
- Open decision "Button nuts": settled on 2026-11-14: screw-in buttons in the spread layout.
- Open decision "One encoder for each control panel": the design assumes it.
- Open decision "The arcade plate stack": the printed plate is 5 thick at its edge. A cut plate of 3.5 needs a spacer of 1.5 on the ledge, or a seat that is less deep.
- New open decision: the latch (screws or magnets).
- "Waiting for the owner": a review of sheets 01 to 07.

Tools:

- `tools/edge_finish.py`: add the 10 part names to `PRINTED`, and the covers of `panel_frame.JOINTS` to `JOINTS`.
- `tools/face_check.py`: add a reveal for the corner balls of the plates (`panel_frame.finish_rows` has it).
- `cad/README.md`: the commands of "Build" in this document.

No value in `dims.py`, `profiles.py`, `solids.py` or `cavity.py` changes. `cad/params/controls.csv` has the OBSN sizes. If the owner selects snap-in buttons, the rows `btn_nut_d`, `btn_nut_h` and `btn_depth` change (OBSF: no nut, 31.7 deep).

## On the main line

Date: 2026-11-16. The push bolt is the default (`Interface.latch` = `PUSH_BOLT`, the values in `PushBolt`). Its functions moved from `panel_latch.py` into this module; the study keeps the other candidates (M, H, Q) and the estimates of the hold, which `check()` reports for the default. The panels carry steel discs and the frame the magnets; the blank panel has the finger hole of 22; the button's gap is 0.3 all round. The latch coupon is on plate 10 of the coupon set (`docs/design/coupons.md`).

Date: 2026-11-14. The package was merged on the laptop after the print pieces and the mounts. What changed:

- **The buttons.** The default is the spread layout for screw-in buttons (the owner's decision). `hardware()` puts the envelopes of the action buttons at the spread places, so that the checks of the parts against the buttons see the holes where the buttons are. The test of the buttons checks the default: no counterbore, a plate of 5 or less, and no pair nearer than the nut.
- **The tools.** `tools/edge_finish.py` has the ten parts of this module in its class of printed parts, the covers of `panel_frame.JOINTS` as named joints, and the rule that only a hole or the other tile hides an edge of the top face. `tools/face_check.py` has the corner balls of the plates as a reveal. Both tools pass when they run on `cad/out/control-panel/parts`. The face check no longer reports a known item of the shell as missing when its part is not in the folder that it checks.
- **ABS.** The masses use 1.05 g/cm3 and the deflection uses E 2200. The latch stays with screws: the owner has not chosen.
- The module reads the moved modules of the shell (`controls.control_panel`, `params`, `model`).
