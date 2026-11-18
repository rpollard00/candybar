# The mounts of the hardware in the shell

Date: 2026-11-14. Status: a proposal for the owner's review. No part is printed.

The fit study (`cad/candybar/shell/fit.py`) puts the hardware in the cavity as boxes. This document describes what holds each item. The module `cad/candybar/shell/mounts.py` makes the parts and does the checks. The class `Mounts` in that module holds each value. The words are those of `CONTEXT.md`. The new words are in the section "Words".

All dimensions are in millimeters. The frame is the frame of the cabinet: x to the right of the player, y from the front of the deck to the rear, z up from the desk. "Left" and "right" are the left and the right of the player.

## Words

**Printed part**: a loose part that a person fastens with screws or with a snap fit.

**Boss**: a solid that is added to a piece of the shell or to a floor tile, and that prints with that piece. The module makes each boss as a net solid and a root. The net solid stands 0.1 mm off the skin. The root goes 1 mm into the skin, so that the boss and the piece become one solid when they are fused.

**Tray**: the printed part on the back of the BC-250. It has two halves.

**Dock**: the printed plate on the side wall that a tray half hangs on.

**Compute module**: the BC-250 with its heatsink, its fan, the shroud, the exhaust duct and the tray. It goes in and out as one unit.

## Build

Run these commands from the root of the repository. The skin of the split must be in the cache (`cad/out/shell-rev7/split/cache`), and the default build with its fit study must be in `cad/out/shell-rev7`.

1. Make the parts, the checks and the scenes: `CANDYBAR_OUT=cad/out/mounts cad/candybar/freecad-run.sh candybar.shell.mounts`
2. Render the sheets: `cad/.venv-tools/bin/python cad/tools/draw_mounts.py cad/out/mounts`
3. Write the document for FreeCAD: `CANDYBAR_OUT=cad/out/mounts cad/candybar/freecad-run.sh --gui candybar.shell.mounts_scenes`
4. Do the tests: `cad/test.sh test_mounts`

Step 1 exits with 1 if a check fails. It takes 2 minutes. The first run takes 3 minutes more, because it cuts the zones of the skin and keeps them in the cache.

| Output in `cad/out/mounts` | Content |
| --- | --- |
| `report.md`, `report.json` | Each value, each check, the loads, the screws, the interfaces |
| `parts/` | BREP and STL of each part and each boss, `manifest.json`, `edges.json` |
| `sheets/` | 24 pictures with each BREP edge drawn |
| `shell.FCStd` | The skin (70 % transparent), the hardware boxes, the keep-out zones (hidden), the parts, the bosses and the places, in groups |

## The parts

| Part | Kind | Count | Fastened to | Mass (g) |
| --- | --- | --- | --- | --- |
| `TrayL`, `TrayR` | printed | 1 each | the board (2 screws each), then the docks | 60.5, 49.8 |
| `DockL`, `DockR` | printed | 1 each | its boss (2 screws) | 31.9, 35.8 |
| `BossL`, `BossR` | boss | 1 each | the pieces middle L and middle R | 28 each |
| `PsuRailL`, `PsuRailR`, `PsuStopL`, `PsuStopR` | boss | 1 each | the floor tiles rear side L and rear centre | 34 in total |
| `HubRailIn`, `HubRailOut` | boss | 1 each | the floor tile middle side R | 11 in total |
| `HubSaddle` | printed | 1 | the two hub rails (snap fit) | 9.9 |
| 16 floor staples, 2 wall staples | boss | 18 | 7 floor tiles, the pieces rear lower L and rear lower R | 0.8 to 1.1 each |
| `ChargerRib1`, `ChargerRib2` | boss | 1 each | the floor tile rear side R | 2.3 each |

All screws are M3 socket head screws in M3 heat-set inserts (hole 4.0, depth 6.5: `m3_insert_d`, `m3_insert_depth`). They are not the M4 inserts of the seams (`joints.py`). One 2.5 mm hex driver does all of them. The four screws of the power supply are the 6-32 screws that come with it.

## The compute module

### Parts

The board has four backplate standoffs. They are the only fixing points behind the board (`docs/research/hardware-envelopes.md`, section 2). The heatsink covers three of them, so a screw cannot go in from the rear. Thus the tray is fastened to the board on the bench, from the front of the board.

- **The tray** has two halves, because one part of 320 mm does not fit the printer. Each half has an upright 12 wide beside one end of the board, 1.5 from its edge. Two arms 14 x 6 go from the upright to the two standoffs at that end. The arms lie in front of the air zone behind the backplate. A post of diameter 9 goes from each arm through the air zone (10 mm) to the backplate. An M3 x 20 screw goes through the arm and the post into the standoff. The board and its backplate connect the two halves.
- **The dock** is a plate 6.5 thick, 58 high (z 126 to 184), in the plane y 437.85 to 444.35. It is below the cable channel of the monitor (z 186 to 206). Its outer end lies on a boss, and two M3 x 12 screws at x 206 (left: -206) hold it. Its inner end is in front of the upright.
- **The boss** is a bracket on the side wall of the lower body, 14 thick, with its tip 32 from the wall. Its underside is 45 degrees, so the piece prints upright with no support. A pad 3 thick and 24 long on the wall behind the boss spreads the moment in the wall. The side wall is flat there (x 231.0, behind the crease of the band).
- **The hanging screw**: each dock has one M3 x 10 screw at z 178 whose head stands 3.3 proud. Each upright has a keyhole in a web 3 thick, with a pocket behind the web for the head. The module goes on with the heads through the round ends of the keyholes. Then it goes down 5 mm, and the shanks are in the slots.
- **The two screws that fasten the module** (M3 x 18) go through the right upright into the right dock, at x 156.95, z 141 and z 162. Their heads are in counterbores 8 deep.

The left end has no screw of its own. The exhaust duct covers the left upright from z 121 to z 250 when you look through the door, and the side wall above z 185 is the band, which is not flat. Thus the left end hangs on its screw head, which holds it to the front, to the rear and down. The two screws of the right tray stop the module from going up.

### Print

| Part | Print box | On the bed | Bridges and overhangs |
| --- | --- | --- | --- |
| `TrayL` | 145.1 x 109.9 x 21.6 | The front face: the face of the arms. It is the flattest side. | The notch for the cable channel: a bridge of 22. The pocket of the keyhole: a bridge of 12. The posts stand up. |
| `TrayR` | 116.9 x 116.6 x 21.6 | The front face | As `TrayL`. The counterbores open upward. |
| `DockL`, `DockR` | 67.8 x 58.0 x 6.5, 76.5 x 58.0 x 6.5 | The front face (toward the boss) | None |
| `BossL`, `BossR` | 33 x 38 x 53 | They print with the pieces middle L and middle R, which stand upright | The underside of the bracket and of the pad: 45 degrees |

### The path of the board

The board comes out through the rear door opening with one 2.5 mm hex driver. Sheet `board-out.png` shows it.

1. Disconnect the leads of the board (power, video, USB, fan).
2. Remove the 2 screws of the right tray.
3. Lift the module 5 mm.
4. Pull the module straight to the rear.

The module is 370.3 wide (x -207.35 to 162.95, the exhaust duct included) and 151 high. When it is lifted, it has 4.0 at the left side of the opening, 48.4 at the right, 10.0 above the sill and 4.0 below the top edge. Nothing that stays is in its path.

### The interface to the shroud and the duct

The tray gives four screw points to the shroud and the exhaust duct. This is the one interface between the compute module's printed parts and the tray, and `rear.carrier_points` holds it: the mounts read the points from there. Each point is an M3 heat-set insert in the tray (hole 4.0, depth 6.5) with its axis along y, at the face where the part lies on the tray. The screws are M3 x 10, driven on the bench.

| Point | x | y | z | Part |
| --- | --- | --- | --- | --- |
| Left, lower | -162.65 | 463.5 | 129.8 | The floor of the exhaust duct lies on the top face of the left upright. Two screws go through the floor. |
| Left, upper | -162.65 | 463.5 | 241.3 | The same |
| Right, lower | 159.95 | 496.0 | 129.8 | An ear of the shroud (12 x 6, at the plane of its seat) lies on a post of the right upright |
| Right, upper | 159.95 | 496.0 | 241.3 | The same |

- x is 7.5 outside the end of the board: the middle of the upright, which is 12 wide and 1.5 from the board (`Rear.carrier_x`).
- z is 4 inside the two long sides of the fin block (`Rear.carrier_inset`).
- The left upright ends 2.4 below the top face of the board, under the floor of the duct (y 463.5 to 465.9). The floor of the duct is the floor of the I/O end, in front of the board's edge.
- The right upright has two posts, 12 x 12, from the top face of the board up to y 496.0. The ears of the shroud reach from its right end wall (x 134.25) out past the post. They stand 30 above the board, over the part of the board that is right of the fin block.

This replaces the four ears of the rear package, which were at x 24.85 and 114.85 outside the long sides of the shroud, for screws into a carrier that is not there. It also removes a clash: the server's left upright went up to the top face of the board, and the real floor of the duct (made by the rear package) was in it. The rule "rear parts" of the fit study now runs in the mounts' checks, with the mounts as hardware. It finds no common volume between the 15 parts of the rear and the 117 solids of the hardware and the mounts.

The module goes up 5 mm before it comes out. The shroud and the duct have 5 mm of clear space above them (their top is at z 250, the top of the door opening is at z 281). The seal between the fan and the door must permit this movement.

## The power supply

- **The fence** is four bosses on the floor: a rail 5 wide and 12 high along each side (0.5 from the supply), and a stop 8 thick and 9.5 high in front of it. The stop is below the plug zone (z 20). It has a gap of 16 at the seam of the floor tiles (x -106).
- **The supply stands on the floor.** The fence holds it to the left, to the right and to the front. The lower rear wall holds it to the rear.
- **The four screws of its rear face** hold it against a pull to the front and against a lift. This is the usual fixing of an ATX supply. The fence does not hold the supply down, because a clamp above it is in the air zone of its fan.

### The interface to the opening of the supply

The lower rear wall needs four holes of diameter 4.0 for 6-32 screws. These are their centers on the inner face of the wall (y 535.9), for the standard ATX pattern with the fan face up:

| Hole | x | z |
| --- | --- | --- |
| 1 | -79.35 | 90.0 |
| 2 | -217.35 | 90.0 |
| 3 | -79.35 | 26.0 |
| 4 | -193.35 | 16.0 |

The rear face of the supply is x -223.35 to -73.35, z 10 to 96. The opening must leave wall round these holes. A margin of 6 at each side of the face is sufficient for the holes, which are 6 from the edges.

### The path of the supply

The supply comes out through the rear door opening. The compute module and the stowed cables come out first.

1. Remove the four screws of the rear face from behind the cabinet.
2. Lift the supply 13 mm, above the fence.
3. Move it 20 mm to the front, off the rear wall and its flanges.
4. Move it 64.7 mm to the right, past the left dock.
5. Lift it 95 mm more, to 2 mm above the sill.
6. Pull it out to the rear. It has 52.7 at the left side of the opening and 77.0 below the top edge.

## The hub

- **Two rails** on the floor, 5 wide and 8 high, 0.5 from each long side of the hub. Each rail has a bead of 1.5 on its outer face.
- **The saddle** is a printed strap 30 wide over the middle of the hub. Its two legs go down outside the rails, and a hook on each leg snaps under the bead. The saddle has no screw. To remove it, pull the two legs apart.
- The saddle is 0.5 above the hub. Put a foam pad of 1 mm there, so that the hub cannot move along the rails.
- The ends of the hub stay free for the plugs.

The size of the hub is an estimate (110 x 45 x 20). When the hub is chosen, change `usb_hub_l`, `usb_hub_w` and `usb_hub_h` in the parameter sheet. The rails and the saddle follow.

## The tie points

A staple is a bar 20 x 6 x 3 on two legs, with an opening 12 x 4 for a cable tie or a strap. A staple on a wall has a 45 degree gusset under each leg, so it prints with its piece.

| Tie point | At (x, y, z) | On | For |
| --- | --- | --- | --- |
| `TieBundleFrontL`, `TieBundleFrontR` | (-45, 437.9, 10), (45, 437.9, 10) | floor rear centre | The strap of the stowed cables |
| `TieBundleRearL`, `TieBundleRearR` | (-45, 535.9, 84), (45, 535.9, 84) | rear lower L, rear lower R | The strap of the stowed cables: it goes over the bundle from the floor to the rear wall |
| `TieLead1` to `TieLead4` | x -150, -50, 50, 150 at y 230, z 10 | floor middle side L, centre, side R | The leads from the control panel to the hub |
| `TiePower` | (40, 397, 10) | floor rear centre | The 12 V lead to the BC-250, the Molex lead to the charging hub and the 5 V lead to the hub |
| Tie slots of the dock L | (-189.15, 444.35, 175.5) | `DockL` | The video lead from the I/O end to the left cable channel of the monitor |
| Tie slots of the dock R | (180.45, 444.35, 175.5) | `DockR` | The USB-C lead from the charging hub to the monitor, the 12 V lead where it goes up, the leads from the hood |

The tie points of the small items are in the section "The places of the small items". No tie point is in an air zone or in a keep-out zone. The leads from the hood have no tie point above the docks: the hood and its hardware are not designed.

## The places of the small items

The owner and the research named five small items on 2026-11-14. Each item has a place: a box of room that the checks keep clear, and a tie point. The sizes of the charging hub and of the amplifier are those of the parts. The other sizes are estimates. `Mounts` has the sizes and the positions.

| Item | Place (x, y, z) | Held by | Path of its leads |
| --- | --- | --- | --- |
| DisplayPort to HDMI adapter (UGREEN, a rigid block, in line: 52.43 long with its plug, 19.88 wide, 9.84 thick, MEASURED by the owner on 2026-11-14) | x -194.88 to -175.0, y 444.35 to 454.19, z 128.0 to 180.43: on the rear face of the left dock, the HDMI socket up | A cable tie through two slots of the left dock, beside the place | For this place the adapter needs a short DisplayPort extension lead from the board: see "The room at the DisplayPort socket". The HDMI lead goes up into the left cable channel (z 186 to 206) and to the monitor. |
| DC to USB charging hub that feeds the monitor (74.7 x 51.3 x 22.6, 80 g) | Body: x 115 to 189.7, y 386.35 to 437.65, z 15 to 37.6, behind the hub, its length across the cabinet. With its plugs: x 74 to 230.7, y 382 to 442, z 15 to 45, which is 156.7 x 60 x 30. It lies on two ribs 5 high (`ChargerRib1`, `ChargerRib2`). The two USB-C sockets are at the left end. The barrel socket and the two USB-A sockets are at the right end. | A strap from `TieChargerFront` (152.35, 379.35, 10) to `TieChargerRear` (152.35, 444.65, 10). The staple `TieBarrel` (205, 452, 10) holds the lead of the barrel plug and its in-line fuse, 10 behind the room of the plug. | 12 V comes from a Molex lead of the supply along the floor through `TiePower` (40, 397, 10), in front of the unit, to `TieBarrel`. The USB-C lead goes from the left end back above the unit, up through the tie slots of the right dock (180.45, 444.35, 175.5), into the right cable channel and to the monitor. A USB-A lead goes from the right end to the hub. |
| Adapter of the power button, in its case on the 24-pin lead (60 x 25 x 20, an estimate) | x -62 to -2, y 402 to 427, z 10 to 30: on the floor, right of the supply and in front of the stowed cables | A strap from the staple `TieButton` (-32, 396, 10) to `TieBundleFrontL` | See "One path to the front of the deck". The signal wire goes up with the 12 V lead to the board. |
| Audio amplifier, Adafruit MAX9744 (54 x 41 x 20), fed from 12 V | x 108 to 162, y 262 to 303, z 10 to 30: on the floor of the body, 14 left of the hub | A strap from `TieAmpFront` (135, 252, 10) to `TieAmpRear` (135, 313, 10) | 12 V comes along the floor through `TiePower`. The speaker leads come down from the hood (not designed). |
| USB sound adapter on a short lead (44 x 23 x 12) | x 118 to 162, y 320 to 343, z 10 to 22: on the floor behind the amplifier, 14 left of the hub | A cable tie on `TieAmpRear`, which is 4 in front of it | Its lead goes to a rear plug of the hub. Its audio lead goes 17 to the front to the amplifier. |

- The adapter at the left dock is in front of the plane of the board and outside its left end. It is not in the shroud, the exhaust duct or an air zone.
- The sound adapter is on the floor at the right, more than 200 from the exhaust duct. The exhaust air does not go there.
- The amplifier is 181 to the right of the power supply.
- The plug of the 24-pin lead is in the plug zone in front of the supply (z 20 to 60). The front stop is below it (z 19.5), and no mount is in that zone. A hand gets to the plug through the door opening when the compute module is out.
- The adapter of the power button leaves with the 24-pin lead before the supply comes out.
- The places are solids in the rules of the fit study. A new size changes the box, and the checks run again.

### The room of the charging hub

The research asks for about 160 x 60 x 30 with the two plugs fitted. The place has 156.7 x 60 x 30. The stowed cables end at x 72.65 and the side wall is at x 231.0, so 158.35 is all the length there is at this place. Each plug has 41 beyond the end of the unit.

The unit has 5 of air below it and 86 above it to the board. It is 94 in front of the rear wall and the make-up air inlet. It is 0.4 behind the plug zone of the hub.

The barrel plug and the fuse are at the right end, below the part of the door opening that the compute module leaves free (x 163 to 211, 48 wide). `TieBarrel` is 84 inside the rear wall. A hand gets to the fuse there when the compute module is out. With the module in place, the opening of 48 is narrow for a hand: this is not proved.

### The room at the DisplayPort socket

The adapter is a rigid block, in line: the DisplayPort plug is at one end and the HDMI socket at the other. The owner measured it on 2026-11-14: 52.43 long with its plug, 19.88 wide, 9.84 thick. The place on the left dock was made for the estimate of 22 x 12 x 55, so the real body fits in it with 2.12, 2.16 and 2.57 to spare.

The fit study keeps 45 beyond the I/O edge of the board for the plug (`bc_dp_clear`), and the exhaust duct is in that room. This is all the room that there is: straight out from the I/O edge (x -155.15) to the side wall (x -231.0) is 75.85. The first 49.2 are inside the zone of the exhaust duct, up to its end wall, and the last 26.65 are between the duct and the wall. (With the board 3 farther to the left, before the rear door was designed, these numbers were 72.85 and 23.65.)

There are two ways. Neither is designed.

1. **The adapter straight in the board's socket.** The depth of the plug in the socket is not measured. A DisplayPort plug goes in about 8 to 10 (ESTIMATED). The body then ends near the end wall of the duct, 42 to 44 from the I/O edge, inside the duct, in the warm exhaust air. The HDMI lead must go through the end wall and turn in the room between the duct and the side wall. This needs a right-angle HDMI plug and an opening with a seal in the end wall of the duct.
2. **A short DisplayPort extension lead** (plug to socket) from the board to the adapter, and the adapter in its place on the left dock, out of the exhaust air. Then only a lead goes out of the zone of the duct. FINDING: the present model has no way out of that zone for this lead that does not go through a keep-out zone. The only opening for the cables of the I/O end is the notch in the lower side wall of the duct (x -200.15 to -160.15, 16 high from the top face of the board). It opens down at z 121, into the clear space over the fan of the power supply (`PSU_FanAir`, x -223.35 to -73.35, z 96 to 121). The floor of the duct closes the side toward the front of the cabinet, and the end wall the side toward the side wall.

**The owner chose way 1 (2026-11-15):** "I think the adapter will be fine in the heat, if it fails they are inexpensive and we can buy a new one and do the lead." The adapter goes straight into the board's socket, in the exhaust air. The HDMI plug leaves through an opening of the duct's end wall, 25 x 14.5, with a pad of closed-cell foam round it (`rear.hdmi_cuts`, `rear.hdmi_seal`; `docs/design/duct-lead-exit.md`). The place on the left dock (`PlaceDpAdapter`) stays as the room for way 2, the fall-back, and holds nothing in the default scene. `tests/test_mounts.py` holds that the adapter in the socket is clear of that place.

### One path to the front of the deck

The lead of the power button and the lead of the volume potentiometer go to the front socket plate on one path. It is on the floor: `TieLead3` (50, 230, 10), `TieLead4` (150, 230, 10), then `TieDeck` (190, 170, 10), then the socket plate in the right side of the deck. The lead of the power button comes from its adapter (x -62 to -2, y 402 to 427) to `TieLead3`. The lead of the potentiometer comes from the amplifier (x 108 to 162, y 262 to 303) to `TieLead4`. The leads from the control panel to the hub use `TieLead1` to `TieLead4` too.

## The material

The owner prints the cabinet in ABS on a Qidi Q2, not in PETG (2026-11-14, decision record 0008). For the first attempt the floor is ABS too, and the owner may print every part in ABS, the parts inside included. The estimates of this document use the values of `structure.py` for ABS: E 2200, a strength of 41 MPa for a short load and 4.1 MPa for a load that stays.

- **The saddle of the hub depends on the material.** With legs 2.4 thick, a leg strained 1.9 % when it snaps on: 42 MPa at the E of ABS, more than the 41 MPa of the estimate. The legs are now 2.0 thick: the strain is 1.6 % and the stress 35 MPa. The hold of the snap is then less. Print one saddle in ABS on its side (the legs bend in the plane of the layers) and test the snap before the floor tile is printed. If it cracks or holds too little, change the mount (a screw in place of the snap).
- **The trays are better in ABS.** The posts touch the backplate of the board, which is warm. ABS stays stiff to about 100 degrees C, PETG to about 75.
- **The fence of the power supply is better in ABS** for the same reason.
- The inserts, the bosses and the staples do not depend on the material. The stresses are 8.3 MPa or less, and the two materials have almost the same strength for a short load. The bridges (22 and 12) and the 45 degree undersides print in the two materials.
- The print boxes are for the limit of the Q2 (248 x 248 x 250). The largest part is 145.1 x 109.9.

## Loads

These are hand estimates. The design load of a mount is its weight times 2, in the worst direction. This is the factor of `structure.hand_holds` for a lift. The limits are 41 MPa for a short load and 4.1 MPa for a load that stays (`structure.py`, ABS). The numbers in the table are those of the server; `cad/out/mounts/report.md` has the present ones.

| Mount | Weight | Where the load goes | Estimate | Result |
| --- | --- | --- | --- | --- |
| Compute module | 1.69 kg (16.6 N): board 1.00, fan 0.18, shroud and duct 0.40, tray 0.11 | 54 % to the right dock, 46 % to the left. Dock, boss, then the side of the lower body in the pieces middle R and middle L. | Wall at the boss, weight times 2: 4.4 MPa. With the weight only: 2.2 MPa. Cabinet tilted, load along the cabinet: 3.2 MPa. | PASS |
| Compute module | | The longest arm of a tray (84 mm) | Load along the cabinet, times 2: 8.3 MPa. With the weight only, in the strong direction: 1.8 MPa. | PASS |
| Compute module | | The web of a keyhole on the shank of the hanging screw | Bearing 1.8 MPa (0.9 with the weight only) | PASS |
| Compute module | | The two inserts of a dock | 18 N against 600 N (estimate of 300 N for each insert) | PASS |
| Power supply | 3.27 kg (32 N) | The floor tiles rear side L and rear centre, then the table. The supply stands across the seam BA1. | Pressure 0.0014 MPa | PASS |
| Power supply | | The front stop, cabinet tilted 45 degrees, times 2: 45 N | Bending at the root: 0.17 MPa | PASS |
| Power supply | | A pull of 50 N on the mains lead: the four screws, then the piece rear lower L | Bearing in a wall of 4: 0.78 MPa | PASS |
| Hub | 0.2 kg with its sockets | The floor tile middle side R | A leg of the saddle (2.0 thick) bends 1.2 when it snaps on: strain 1.6 %, 35 MPa for a moment | PASS |
| Stowed cables | 0.6 kg | Two straps on four staples: floor rear centre and the lower rear wall | Bar of a staple: 2.0 MPa | PASS |

When a person lifts the cabinet by the hand-holds, it turns on the front edge of the deck. The supply then pushes on its front stop. The compute module pushes its trays against the docks, and the hanging screws and the two screws of the right tray hold it.

## Checks

The module does these checks in each run. `cad/out/mounts/report.md` has the numbers.

| Check | Result |
| --- | --- |
| No part and no net solid of a boss has volume in the skin. Each root is in the skin or in the floor. | PASS: 38 solids, 0 mm3 |
| No two solids of the mounts have a common volume. | PASS |
| The rules of the fit study on the hardware alone | PASS |
| The rules of the fit study with the 38 solids added as hardware (the seven boxes of the places included): interference (3982 pairs), keep-out zones, containment (132 solids), air zones, door service | PASS, with one declared item (see "The declared item") |
| A driver of diameter 6 gets to each screw through the rear door opening | PASS: 6 screws. The smallest margin to the side of the opening is 2.35 (the screws of the docks). |
| The compute module comes out | PASS: margins 4.0, 48.4, 10.0, 4.0 |
| The power supply comes out | PASS: margins 52.7, 220.0, 2.0, 77.0 |
| Each boss is 6 or more from a seam and from the flange of a seam | PASS: the nearest is 7.8 (`BossL` and `BossR` behind the crease of the band, seam S1) |
| Each printed part fits the printer | PASS |
| Each estimate is below its limit | PASS |
| `tools/face_check.py` on each solid | PASS: no finding |

`fit.py` is not changed. The module calls `fit.anchors`, `fit.build_items`, `fit.items`, `fit.run_checks` and `fit.door_service`. No position of `fit.Layout` moves.

### The declared item

Each tray half has two posts through the air zone behind the backplate (`Compute_UndersideAir`). The rules R2 and R2b report this: 1091 mm3 for each half, 0.5 % of the zone. The standoffs of the board are behind the backplate, so a tray on the mounting holes of the board must go through this zone. The arms are in front of the zone, and the zone stays open at the top and at the bottom.

### Limits of the checks

- The rules of the fit study use the real skin only in five zones round the mounts, and the floor of the skin. A boolean with the whole skin takes 20 s for each solid. `tests/test_fit.py` does the test of the hardware against the whole skin.
- The path of the power supply is tested against the mounts and the hub. It is not tested against the skin. The flanges of the seams and of the door opening are not modelled.
- The check of the driver uses the opening of `dims.Blueprint`. The frame of the door is not designed.

## Seams

| Mount | Pieces of the split | Seams that it goes across |
| --- | --- | --- |
| Compute module | middle L and middle R (side walls, z 131 to 184) | None. The module connects the two side walls. Each boss is 11.1 above the flange of L1 and 7.8 behind S1. |
| Power supply | floor rear side L, floor rear centre, rear lower L | BA1 (x -106) is under the supply. The joint has no load from this: each tile stands on the table. The stop has a gap at BA1. |
| Hub | floor middle side R | None. The rails are 15.4 from BA3. |
| Strap of the stowed cables | floor rear centre, rear lower L, rear lower R | The strap goes from the floor to the rear wall, across the seam at the foot of the wall. It pulls the two together. The staples are 35 from R2. |
| Tie staples of the leads | floor middle side L, centre, side R | None. They are 33 from BA2. |

## Assumptions

1. The thread of the backplate standoffs is M3, and a longer screw can replace the stock screw. The thread is not known (`hardware-envelopes.md`). Measure it on the board.
2. The standoff positions are those of the community model: (51.85, 17.68), (82.25, 114.50), (277.45, 37.75), (292.25, 114.25) from the I/O edge and the straight long edge.
3. The power supply has the standard ATX screw pattern in its rear face with the fan face up (`bc250-cooling-and-psu.md`).
4. The mass of the board with its heatsink is 1.0 kg, and the shroud with the duct is 0.4 kg (`structure.py`).
5. One M3 heat-set insert holds 300 N. This is an estimate for PETG; plate 3 of the coupons measures it in ABS.
6. The cabinet is tilted 45 degrees at most when a person lifts it.
7. The floor is the 10 mm sandwich, and a boss can be printed on a tile.
8. The hub is 110 x 45 x 20.
9. The flanges of the seams are those of `structure.members`: 4 above and below L1, 8 below B1, 8 round the door opening.

## What must go into the shared files

- `docs/roadmap.md`: phase 4 has a proposal for the compute module mount, the power supply mount, the hub mount and the tie points. Step 11 (the shroud and the door) gets the two interfaces of this document.
- `CONTEXT.md`: the words tray, dock, boss and compute module (this document, "Words").
- `docs/blueprint/index.md`, "Hardware in the shell": a reference to this document and to the sheets.
- `cad/README.md`: the four commands of "Build".
- `cad/candybar/shell/structure.py`, `mounts()` and `members()`: the text for the BC-250 says "two uprights and two rails, right upright on the floor, left upright on the door sill". The proposal is two docks on the side walls. The text for the power supply says "a saddle, two straps over it". The proposal is a fence and the four rear screws.
- The split and the floor: 2 bosses on the pieces middle L and middle R, 2 staples on the pieces rear lower L and rear lower R, and 24 bosses on seven floor tiles. `cad/out/mounts/report.md` ("Bosses") has the box of each. The opening of the supply in the piece rear lower L needs the four holes.

## On the main line

Date: 2026-11-14. The package was merged on the laptop after the rear door and the print pieces. What changed:

- **The board** stands 3 farther to the right (the I/O edge at x -155.15) since the rear door was designed. The tray, the docks and the places follow the anchors of the fit study, so they moved with it. The compute module comes out with margins of 7.0 at the left of the opening, 45.4 at the right, 10.0 above the sill and 4.0 below the top.
- **The interface to the shroud and the duct** is now one interface, in `rear.carrier_points` (see "The interface to the shroud and the duct").
- **The screws of the supply.** The rear package had four holes at the corners of the supply's face, (6, 6), (144, 6), (6, 80) and (144, 80). That is not the ATX pattern of `hardware-envelopes.md`, section 6, which this package uses. The rear now has the ATX pattern, (6, 80), (144, 80), (6, 16) and (120, 6), and the mounts read it from `rear.Rear.psu_screws`. The grille of the supply starts at u 10 (it was 7), so that its first slot stays 4 from the hole at (6, 16). The inlet is the mirror of that field and moved 3 outward: x 83.35 to 217.35.
- **The rule "rear parts"** of the fit study runs with the mounts as hardware: PASS.
- **ABS**, the saddle and the inserts: see "The material".
- **The adapter** has its measured size: see "The room at the DisplayPort socket".
- Result: PASS, with the declared item. `tests/test_mounts.py` checks the interface: each part lies on the tray at each point, the screw passes through a hole in the part into a hole in the tray, and the part and the tray have no common volume.

## The edge finish and the face check

Date: 2026-11-15. `tools/edge_finish.py` and `tools/face_check.py` run on `cad/out/mounts/parts`:

```sh
CANDYBAR_OUT=cad/out/mounts/parts cad/candybar/freecad-run.sh tools.edge_finish
CANDYBAR_OUT=cad/out/mounts/parts cad/candybar/freecad-run.sh tools.face_check
```

- **The classes.** Each solid is in a class by its name (`mounts.INSIDE_PREFIXES`, `mounts.PLACE_PREFIX`): the trays, the docks, the bosses, the rails, the stops, the saddle, the tie points and the charger rib are "inside, not painted". The places of the small items are "a place" and are not checked: they are volumes of room, not parts.
- **Edge finish.** The rule is for the faces that show on the outside, so it does not fail on an inside part. The tool lists the sharp edges of each part: they are the edges of printed brackets, and none is a print or an assembly problem.
- **Face check.** Six findings, listed and not failed: one sliver 1.10 wide on each boss (x ±231.4, y 442.8, z 131.1) and two on each rear bundle tie point (z 74.0). Each is the face of a root that stands 0.4 to 0.5 inside the wall, and it goes into the wall when the part is bonded. It is not a print or an assembly problem. No part changed.
