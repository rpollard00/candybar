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

All screws are M3 socket head screws in M3 heat-set inserts (hole 4.0, depth 6.5). One 2.5 mm hex driver does all of them. The four screws of the power supply are the 6-32 screws that come with it.

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

### The interface to the shroud

The tray gives four screw points to the shroud and the exhaust duct. Each is an M3 insert with its axis along y. Its face is in the plane of the top face of the board (y 465.9).

| Point | x | z | Where |
| --- | --- | --- | --- |
| Left, lower | -165.65 | 129.8 | Under the exhaust duct, 7.5 left of the I/O edge of the board |
| Left, upper | -165.65 | 241.3 | Under the exhaust duct |
| Right, lower | 156.95 | 129.8 | 25.7 right of the end of the shroud (x 131.25) |
| Right, upper | 156.95 | 241.3 | 25.7 right of the end of the shroud |

The z values are 4 inside the two long sides of the fin block (z 125.8 and 245.3). The points are at the ends of the board and not at the corners of the fin block (x -111.0 and 128.5). A point at a corner of the fin block must be below or above the board. Below the board at the left, the air zone of the power supply starts 3 mm under the board. The shroud needs lugs that go to the uprights.

The module goes up 5 mm before it comes out. The shroud and the duct must have 5 mm of clear space above them (their top is at z 250, the top of the door opening is at z 281). The seal between the fan and the door must permit this movement.

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

The owner named four small items on 2026-11-14. Only the charging hub is a known part. Each item has a place: a box of room that the checks keep clear, and a tie point. Each size is an estimate, but the size of the charging hub is from its maker. `Mounts` has the sizes and the positions.

| Item | Place (x, y, z) | Held by | Path of its leads |
| --- | --- | --- | --- |
| DisplayPort to HDMI adapter (body 22 x 12 x 55) | x -200 to -178, y 444.35 to 456.35, z 128 to 183: on the rear face of the left dock, the HDMI socket up | A cable tie through two slots of the left dock (x -203 to -200 and x -178 to -175, z 146 to 153) | The plug is in the DisplayPort socket, in the plug space of the exhaust duct. The short cable of the adapter bends to the front round the left end of the board. The HDMI lead goes up 3 mm into the left cable channel (z 186 to 206) and to the monitor. |
| DC to USB charging hub that feeds the monitor (74.7 x 51.3 x 22.6, 80 g, from the maker's table) | x 115 to 189.7, y 384 to 435.3, z 15 to 37.6: behind the hub, its length across the cabinet. It lies on two ribs 5 high (`ChargerRib1`, `ChargerRib2`), so it has air below it. Its left end has the barrel socket and the two USB-A sockets. Its right end has the two USB-C sockets. A room of 40 is clear beyond each end (x 75 to 115 and x 189.7 to 229.7). | A strap from `TieChargerFront` (152.35, 377, 10) to `TieChargerRear` (152.35, 442.3, 10). The staple `TieBarrel` (62, 409.65, 10) holds the lead of the barrel plug, 13 from the plug room, so that the plug cannot come out. | 12 V comes from a Molex lead of the supply, with a fuse, along the floor through `TiePower` (40, 397, 10) and `TieBarrel`. The USB-C lead goes from the right end up the right side, through the tie slots of the right dock (180.45, 444.35, 175.5), into the right cable channel and to the monitor. A USB-A lead can go from the left end to the rear plugs of the hub. |
| Adapter of the power button, in its case on the 24-pin lead (60 x 25 x 20) | x -62 to -2, y 402 to 427, z 10 to 30: on the floor, right of the supply and in front of the stowed cables | A strap from the staple `TieButton` (-32, 396, 10) to `TieBundleFrontL` | The four-wire lead goes along the floor through `TieLead3` and `TieLead4`, then to the front through `TieDeck` (190, 170, 10) to the USB socket plate. The signal wire goes up with the 12 V lead to the board. |
| Audio amplifier (50 x 40 x 20) | x 112 to 162, y 262 to 302, z 10 to 30: on the floor, 14 left of the hub | A strap from `TieAmpFront` (137, 252, 10) to `TieAmpRear` (137, 312, 10) | Power comes from the hub side or from `TiePower`. The speaker leads come down from the hood (not designed). |

- The adapter is in front of the plane of the board and outside its left end. It is not in the shroud, the exhaust duct or an air zone.
- The charging hub is 32.4 behind the hub and 2.4 behind the plug zone of the hub. It has 5 of air below it and 86 above it to the board. It is 100.7 in front of the rear wall and its make-up air inlet.
- The right end of the charging hub is below the part of the door opening that is free at the right of the compute module (x 163 to 211). A hand gets to the whole unit when the compute module is out.
- The amplifier is 185 to the right of the power supply.
- The plug of the 24-pin lead is in the plug zone in front of the supply (z 20 to 60). The front stop is below it (z 19.5), and no mount is in that zone. A hand gets to the plug through the door opening when the compute module is out.
- The adapter of the power button leaves with the 24-pin lead before the supply comes out.
- The places are solids in the rules of the fit study. A new size changes the box, and the checks run again.

## Loads

These are hand estimates. The design load of a mount is its weight times 2, in the worst direction. This is the factor of `structure.hand_holds` for a lift. The limits are 50 MPa for a short load and 5 MPa for a load that stays (`structure.py`).

| Mount | Weight | Where the load goes | Estimate | Result |
| --- | --- | --- | --- | --- |
| Compute module | 1.69 kg (16.6 N): board 1.00, fan 0.18, shroud and duct 0.40, tray 0.11 | 54 % to the right dock, 46 % to the left. Dock, boss, then the side of the lower body in the pieces middle R and middle L. | Wall at the boss, weight times 2: 4.4 MPa. With the weight only: 2.2 MPa. Cabinet tilted, load along the cabinet: 3.2 MPa. | PASS |
| Compute module | | The longest arm of a tray (84 mm) | Load along the cabinet, times 2: 8.3 MPa. With the weight only, in the strong direction: 1.8 MPa. | PASS |
| Compute module | | The web of a keyhole on the shank of the hanging screw | Bearing 1.8 MPa (0.9 with the weight only) | PASS |
| Compute module | | The two inserts of a dock | 18 N against 600 N (estimate of 300 N for each insert) | PASS |
| Power supply | 3.27 kg (32 N) | The floor tiles rear side L and rear centre, then the table. The supply stands across the seam BA1. | Pressure 0.0014 MPa | PASS |
| Power supply | | The front stop, cabinet tilted 45 degrees, times 2: 45 N | Bending at the root: 0.17 MPa | PASS |
| Power supply | | A pull of 50 N on the mains lead: the four screws, then the piece rear lower L | Bearing in a wall of 4: 0.78 MPa | PASS |
| Hub | 0.2 kg with its sockets | The floor tile middle side R | A leg of the saddle bends 1.2 when it snaps on: strain 1.9 %, 38 MPa for a moment | PASS |
| Stowed cables | 0.6 kg | Two straps on four staples: floor rear centre and the lower rear wall | Bar of a staple: 2.0 MPa | PASS |

When a person lifts the cabinet by the hand-holds, it turns on the front edge of the deck. The supply then pushes on its front stop. The compute module pushes its trays against the docks, and the hanging screws and the two screws of the right tray hold it.

## Checks

The module does these checks in each run. `cad/out/mounts/report.md` has the numbers.

| Check | Result |
| --- | --- |
| No part and no net solid of a boss has volume in the skin. Each root is in the skin or in the floor. | PASS: 37 solids, 0 mm3 |
| No two solids of the mounts have a common volume. | PASS |
| The rules of the fit study on the hardware alone | PASS |
| The rules of the fit study with the 37 solids added as hardware (the six boxes of the places included): interference (3892 pairs), keep-out zones, containment (131 solids), air zones, door service | PASS, with one declared item (see "The declared item") |
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
5. One M3 heat-set insert in PETG holds 300 N.
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
