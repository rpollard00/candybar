# Control panel

Date: 2026-11-14. Roadmap step 12. This document is a proposal. The owner did not review it.

A control panel is a service part. It lifts out of the pocket of the deck, and a different control panel goes in. This document describes the arcade panel as printed parts, the frame that stays in the cabinet, the latch, the cable, and the interface that all control panels share.

The source is `cad/candybar/shell/panel_frame.py`. The tests are in `cad/tests/test_panel_frame.py`. The build output is `cad/out/control-panel/` (not in git).

All dimensions are in millimetres. The frame of reference is that of `dims.py`. A depth with the name `yl` is a distance from the front edge of the panel at the centre line (y - 26).

## The parts

All parts are printed in PETG. The mass is the mass of the solid volume.

| Part | Quantity | Function | Box on the printer | Mass, g |
| --- | --- | --- | --- | --- |
| `frame_left`, `frame_right` | 1 each | The frame. It stays in the cabinet. | 197.2 x 174.0 x 19.1 | 84, 83 |
| `post_*` | 4 | A post between the floor and the frame | 38.6 x 20.0 x 7.5 | 7 |
| `panel_lever_tile` | 1 | Arcade panel: the lever and the encoder | 174.4 x 158.7 x 20.0 | 250 |
| `panel_button_tile` | 1 | Arcade panel: the buttons | 236.7 x 174.4 x 20.0 | 251 |
| `blank_left_tile`, `blank_right_tile` | 1 each | The blank panel, which proves the interface | 197.7 x 174.4 x 20.0 | 256, 254 |

The outer form does not change. The shell gets no new opening and no cutter. All parts are inside the opening that `cavity.Openings` makes below the control panel.

Bought parts for the arcade panel and the frame:

- 4 screws M4 x 16, countersunk (ISO 10642), and 4 heat-set inserts M4 x 8 for the latch.
- 4 heat-set inserts M4 for the lever, and 4 screws M4 for its plate.
- 4 screws M3 x 12 with nuts for the seam between the two tiles.
- 4 thread-forming screws 3.0 for the encoder.

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
| Latch screws (4) | 4.5, countersink 9 | The four latch points |

A printed hole is drawn 0.3 larger than the hole of the data sheet (`hole_allow`). A coupon must confirm this value.

**The buttons are snap-in buttons** (`Arcade.buttons = "snap-in"`, Sanwa OBSF). Three pairs of screw nuts overlap by 0.15 to 0.28 in this layout. Snap-in buttons have no nut. They are also the buttons of the aluminium plate that comes later, so the printed plate proves the same parts. A snap-in button holds in a plate of 3.9 or less. Thus each button hole has a counterbore from below, 2 wide, and the plate is 3.0 thick there (`seat_t`). The other value is `"spread"`: the layout becomes 1.02 times larger about its middle, the nearest pair is then 36.4 apart, and the plate keeps its full thickness for screw nuts. The ribs keep clear of the nut envelopes, so both values fit.

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

The top edge of the outline has the edge break of R 1, because it shows in the reveal. The four upright corners of the plate have the same break, so that the round goes round each corner with no mitre. At each corner the three rounds meet in a ball of R 1, as on the hood. The top edges of the holes are sharp. The rim of each button, the dust washer of the lever and the head of each screw cover them.

## The frame

The frame is a ring of two halves, with a gap of 0.5 between them at the centre line. It is bonded below the ledge of the opening, with a bond gap of 0.2.

- **The bar** is 7.7 wide and 12 high. It lies below the ledge, which is 8 wide and 4 thick.
- **A pad** stands in each corner of the opening (radius 21). It has the insert of one latch point. Its two straight sides lie 0.2 from the edges of the opening. Thus the four pads locate the frame in the opening.
- **Two smaller pads** (radius 12) stand at the rear edge, at x -120 and x +120. Each has a locating cone: 8 at its base, 5 at its top, 3 high.
- **The anchor** of the cable is a clip at the rear edge, at x -80.
- **Four posts** (20 x 7.5) stand between the floor and the bar, at x -66 and x +66, at the front and at the rear.

**Rest.** The plate rests on the ledge of the skin, all round. The tops of the pads are 0.1 below the rest face, so that the plate does not rock on a pad.

**Location.** The plate stands 0.3 inside its seat. The two cones locate it: the panel has a round socket at x -120 and a slot along X at x +120 (clearance 0.15). The slot lets two prints differ in size. The panel goes in one way only: its front edge has two corners that its rear edge does not have, and the two sockets are different.

**Flush.** The top of the plate is in the plane of the step of 1 that the pocket has round the panel (z 70). The rest face and the thickness of the plate set this height.

**The load of the lever.** The lever puts a couple on its seat. The ribs on each side of the seat carry it to the front and rear edges of the plate. One edge pushes down on the ledge: the bar and the posts below it carry this to the floor. The other edge pulls up: the screws carry this into the pads, and the bonded bar carries it into the skin of the deck. No load goes through a painted seam.

## The latch

All panels use the same four latch points. Each is 12.5 from a corner of the opening, on the line that divides the corner in two: (-180.6, 49.8), (180.6, 49.8), (181.2, 184.2) and (-181.2, 184.2) in x and y.

Two options are built. `Interface.latch` selects one.

| | A. Screws (the default) | B. Magnets |
| --- | --- | --- |
| Parts | A flush M4 x 16 countersunk screw in each latch point, into a heat-set insert in the pad | A magnet of 12 x 5 in each pad, a magnet of 12 x 2 in the plate above it |
| Tool | A 3 mm hex key | None |
| Hold | Preload from the screws. An M4 insert in PETG holds much more than the 15 N that the lever applies. | ESTIMATED 20 N for each point: 40 N on one edge against 15 N from the lever, a factor of 2.6 |
| On the top face | Four screw heads, 9 across, one in each corner | Nothing |
| Risk | The four screws are loose parts | A hard input can lift an edge. A pull of 80 N on the lever lifts the panel out. The magnet values are not tested. |

Option A is the proposal. The research note (`docs/research/controls-ergonomics.md`, section 6.4) does not recommend magnets as the only latch, because a lever moment peels the panel off. Sheet 05 shows the two options side by side.

To remove the arcade panel, remove the four screws and lift the panel by the lever. A panel with no lever lifts with the hex key in a screw hole.

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
| Latch points (4) | 12.5 from each corner of the opening. Screw: a hole of 4.5 with a countersink of 9. Magnet: a pocket of 12.2 x 2.2 in the lower face. |
| Sockets (2) | At the rear edge, 6.5 inside the opening: a round socket at x -120, a slot (3 long) at x +120. Each is 8.3 across at the rest face, 5.3 at its end, and 3.3 deep. |
| Cable clip | Below the plate, x -93, yl 145.5. One USB cable. |
| Room below the plate | The opening less 0.7, from z 65 down to z 12. Not in the room: a circle of 21.5 round each corner of the opening, a circle of 12.5 round x -120 and x +120 on the rear edge, the anchor clip at x -80, and the space of the USB sockets (x more than 181, z less than 32.5). Volume 3015 cm3. |
| Ribs | Free in the room. The front rib and the rear rib of the two built panels are at yl 20 and yl 150. |
| Tiles | A panel is wider than the printer. Its seam can be at any x. The seam has a flange on each tile. |

The blank panel is made from these values only. It has a seam on the centre line and a rib at a quarter of the width on each side. It goes on the same frame with the same screws. Sheet 07 shows it.

For the PC panel: a 60 % keyboard needs 14 below the plate top. The room is 53 deep below the rest face.

## Checks

`candybar.shell.panel_frame` does these checks on the real skin of the deck (from the cached skin of the shell) and on the hardware of the fit study. All pass.

| Check | Result |
| --- | --- |
| Each part against the skin of the deck | 0.0 mm3 in common, for each of the 10 parts |
| Each part against each other part | 0.0 mm3 |
| Each part against the lever, the buttons, the encoder, the USB sockets and the hub (envelopes and keep-out zones) | 0.0 mm3. The fit rules permit 1. |
| Smallest gaps | Frame to the encoder 1.8. Frame to the nut of service button 1: 4.3. Frame to the USB sockets 18.3. Seam flanges to the lever body and to the nut of button 1: 1.0 each. Rib to the encoder 2.3. |
| The room below the plate | Free of the skin, the frame, the posts, the USB sockets and the hub. The arcade panel and all its hardware are in the room. |
| Lift out | The panel with its hardware goes straight up. At 3, 8, 16, 32 and 64 it has 0.0 mm3 in common with the deck and the frame. |
| Edge rule | No sharp convex edge shows on a top face. Each tile has 6 faces of the edge break. |
| Face check | No finding fails. Each tile has 8 allowed items: 6 rounds of the edge break and 2 corner balls. |
| Print | Each part fits 240 x 240 x 245. |

The tools `tools/edge_finish.py` and `tools/face_check.py`, as they are, exit with 1 on `cad/out/control-panel/parts`. `edge_finish` has no class for these parts. `face_check` does not know the 8 corner balls, and it also reports the known items of the shell, which are not in this directory. The module calls the functions of the two tools with the classes and the corner balls of these parts. The changes that the tools need are in "For the shared files".

The edge rule of this module: a sharp convex edge passes only if one of its faces lies against a cover. The covers are the seat of the plate, a hole through the plate, the room below the plate, and the other tile. On the top face, only a hole and the bonded seam hide an edge. A test makes sure that a plate with no edge break fails.

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
| Tiles | Top face on the bed. The ribs point up. | The top face: 264 to 335 cm2 | 3.5 to 4.5 cm2: the round of the edge break at the bed, and the countersinks |
| Frame halves | As in the cabinet. The lower face of the bar is on the bed. | The lower face of the bar and the pads: 52 cm2 | 0 |
| Posts | On the wide side | 7.7 cm2 | 0 |

No part needs support. The top face of a tile gets the surface of the bed plate. The round of R 1 at the bed starts with a short overhang. If it does not print cleanly, a flat break of 1 is the alternative.

## Build

```sh
CANDYBAR_OUT=cad/out/control-panel cad/candybar/freecad-run.sh candybar.shell.panel_frame          # parts, checks, report.md
CANDYBAR_OUT=cad/out/control-panel cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc        # shell.FCStd
cad/.venv-tools/bin/python cad/tools/draw_panel.py                                                 # renders and sheets
cad/test.sh panel_frame                                                                            # 30 tests, 1 minute
```

The first command needs the skin of the shell in `cad/out/shell-rev7/split/cache`. It takes 2 minutes.

| Output | Content |
| --- | --- |
| `report.md`, `report.json` | The results of the checks |
| `shell.FCStd` | The deck, the frame, the arcade panel and its hardware in position. The blank panel is 260 in front of the deck. |
| `parts/` | The 10 printed parts as BREP and STL |
| `scenes/`, `renders/` | The models and the renders of the sheets |
| `sheets/01` to `07` | The panel from above, the panel lifted out, the section through the lever, the latch, the two latch options, the panel from below, the blank panel |

## Assumptions

1. The top of a control panel is 2 below the deck top, as the outer form has it. "Flush" means flush with the step of the pocket.
2. The buttons are Sanwa OBSF snap-in buttons. The parameter sheets have the sizes of the OBSN screw buttons, and the envelopes of the fit study keep the nuts.
3. The seat gap is 0.3, the bond gap 0.2, and the hole allowance 0.3. A coupon sets these values.
4. The printed floor is 10 thick (`fit.Layout.floor_t`). It is not a part of the model. The posts stop at z 10.
5. The plug at the encoder is a right-angle USB-C plug.
6. The encoder is the RP2040 Advanced Breakout Board, with its USB socket to the rear.
7. The pilot hole of the encoder screws is 2.6 for a 3.0 thread-forming screw. The joint coupon gives 2.25 to 2.4, and a disc below 2.55 across fails the face check.
8. The hold of the magnets is an estimate from supplier data. It is not tested.
9. The frame is bonded. The owner does not disassemble the shell.

## Open questions for the owner

1. The latch: screws (four heads show) or magnets (nothing shows, less hold).
2. The buttons: snap-in or the spread layout with screw nuts.
3. The four screw heads are in the corners. The front two are near the hands. A different position is possible on the front and rear edges.
4. The top of the printed plate is 2 below the deck top. A cover of 1.5 with art makes it 0.5 below. Is this the look that the owner wants?
5. The corners of the plate have R 1 and the corners of the pocket are sharp. The gap at each corner is 0.7 on the diagonal.

## For the shared files

Glossary (`CONTEXT.md`):

- **Panel frame**: The printed ring below the ledge of the deck's opening. It has the latch points, the locating cones and the cable anchor, and it stays in the cabinet. _Avoid_: carrier, subframe.
- **Ledge**: The strip of deck skin round the opening below a control panel. The control panel rests on it.
- **Latch point**: One of the four positions where a control panel is held down on the panel frame.
- **Seat** (of a control panel): The recess in the pocket that the plate of the control panel fills.
- **Blank panel**: A control panel with no hardware, made from the interface only.
- Change **Tile**: the arcade panel has a lever tile and a button tile, with a bonded seam at x -39.

Roadmap (`docs/roadmap.md`):

- Step 12: the control panel is designed as printed parts (`docs/design/control-panel.md`). The cut plates and their drawings are not done.
- Open decision "Button nuts": the proposal is snap-in buttons, with a seat of 3.0.
- Open decision "One encoder for each control panel": the design assumes it.
- Open decision "The arcade plate stack": the printed plate is 5 thick at its edge. A cut plate of 3.5 needs a spacer of 1.5 on the ledge, or a seat that is less deep.
- New open decision: the latch (screws or magnets).
- "Waiting for the owner": a review of sheets 01 to 07.

Tools:

- `tools/edge_finish.py`: add the 10 part names to `PRINTED`, and the covers of `panel_frame.JOINTS` to `JOINTS`.
- `tools/face_check.py`: add a reveal for the corner balls of the plates (`panel_frame.finish_rows` has it).
- `cad/README.md`: the commands of "Build" in this document.

No value in `dims.py`, `profiles.py`, `solids.py` or `cavity.py` changes. `cad/params/controls.csv` has the OBSN sizes. If the owner selects snap-in buttons, the rows `btn_nut_d`, `btn_nut_h` and `btn_depth` change (OBSF: no nut, 31.7 deep).
