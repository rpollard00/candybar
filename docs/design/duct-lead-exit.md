# A way out of the exhaust duct's zone for a lead

Date: 2026-11-15. Status: decided. **The owner chose way 1** (the adapter straight in the board's socket, in the exhaust air of the duct): "I think the adapter will be fine in the heat, if it fails they are inexpensive and we can buy a new one and do the lead." Way 2 below is the fall-back for later; it is not built.

All dimensions are in millimetres, in the frame of the cabinet: x to the player's right, y from the front of the deck to the rear, z up from the desk. The values come from `candybar.shell.rear` and `candybar.shell.mounts` as built on 2026-11-15.

## The problem

Way 2 for the adapter is a short DisplayPort extension lead from the board's socket to the adapter, which stands in its place on the left dock, out of the warm air. The board's DisplayPort socket is at the I/O end of the board, inside the zone of the exhaust duct. The lead must leave that zone.

In the present model the duct has one opening for leads: the cable notch in its lower side wall (x -200.15 to -160.15, 16 high from the top face of the board, y 465.9 to 481.9). It opens downward at z 121. Directly below it is the clear space over the fan of the power supply (`PSU_FanAir`, x -223.35 to -73.35, z 96 to 121). A lead through the notch crosses that space.

## What is round the duct

| Item | Where |
| --- | --- |
| The duct body | x -204.35 to -98.05, y 463.5 to 530.9, z 121 to 250. Walls 2.4 thick. Open toward the door. |
| Its floor (the face toward the front of the cabinet) | y 463.5 to 465.9, x -204.35 to -155.45 |
| Its end wall (toward the left side wall) | x -204.35 to -201.95 |
| Its lower side wall | z 121 to 123.4 |
| The left upright of the tray, under the duct's floor | x -168.65 to -156.65, z 124.5 to 272 |
| The place of the adapter, on the left dock | x -194.88 to -175.0, y 444.35 to 454.19, z 128.0 to 180.43 |
| The left side wall, inner face | x -231.0 |
| The clear space over the fan of the supply | z 96 to 121, below the duct |
| The hot-air vent in the door | 82.3 cm2 open |

The DisplayPort plug of an extension lead is about 20 x 10 in section, and its lead about 6 thick (ESTIMATED: common moulded plugs; not measured).

## Three places

### A. A slot in the duct's floor

- **Opening:** 24 x 12 with round ends, at x -199 to -175 and z 125 to 137, through the floor (2.4). It stays 2 from the end wall and 6 from the left upright.
- **The plug:** it passes the slot with 2 of clearance. The lead is put through before the duct is screwed to the tray, on the bench.
- **The route:** out of the floor toward the front, 9.3 to the rear face of the adapter's place. It is the shortest route.
- **The seal and the air:** an open slot is 2.6 cm2, 3.1 % of the hot-air vent. A split foam grommet round the lead closes most of it. The seals between the duct and the door do not change: they are on the other side.
- **Part that changes:** `duct_body` (the slot), and a foam grommet.

### B. A hole in the duct's end wall

- **Opening:** 24 x 12 with round ends, through the end wall, at y 470 to 494 and z 128 to 140.
- **The plug:** as in A, with the duct off the tray.
- **The route:** out of the end wall into the room of 26.65 between the duct and the side wall, then 16 toward the front and about 10 back toward the centre, to the adapter's place. It is about 40 longer than A.
- **The seal and the air:** the same open area as A (2.6 cm2), but into the narrow room beside the side wall, which is not open to the hot-air vent. Warm air stays there. The compute module comes out through the door with 7.0 at its left side (`docs/design/hardware-mounts.md`), so a lead in that room must be unplugged first. It is unplugged in any case.
- **Part that changes:** `duct_body` (the hole), and a foam grommet.

### C. The cable notch moved to the front lower edge of the duct

- **Opening:** the present notch (40 wide, 16 high, in the lower side wall) is replaced by a notch at the edge where the lower side wall meets the floor: x -200 to -175, 12 into the floor and 12 into the lower side wall. It is open on the two faces, so a lead goes in from the outside: no plug has to pass.
- **The route:** the leads of the I/O end, the extension lead among them, leave toward the front and stay above z 121. They do not cross the clear space over the fan of the supply. The extension goes 9.3 to the adapter's place, as in A.
- **The seal and the air:** the open area is about 3 cm2 less the leads, which is less than the present notch (5.4 cm2: 40 x 16 less its two corner cuts). The seals to the door do not change.
- **Part that changes:** `duct_body` only (the notch moves). The lower side wall keeps its height of 2.4 behind the notch.

## Recommendation (of the study, before the owner chose way 1)

C. It is one opening for every lead of the I/O end, so the present fault (leads across the clear space over the fan of the supply) goes away for all of them, not only for the extension. No plug has to pass an opening, the leak is less than now, and only the duct body changes. A is the second choice: it is as short, but the plug must be put through the slot on the bench.

## A finding for way 2

The place of the adapter on the left dock is 52.43 high, the length of the adapter, with its DisplayPort plug at the lower end (z 128). An extension lead ends in a DisplayPort socket of about 25 to 35 (ESTIMATED), in line with the adapter's plug. Below the place there are 7 to the top of the clear space over the fan of the supply (z 121), and above it the cable channel of the monitor starts at z 186. The place is thus about 20 to 30 too short for the adapter and the socket of the lead in line. Way 2 needs one of these: the adapter turned over (the plug up and the HDMI lead down and round), a lead with a right-angle socket, or the place moved. Measure the extension lead that the owner buys before the place is changed.

## The sheets

The owner asked for pictures (2026-11-15). `candybar.shell.duct_lead` writes the scenes from the real parts (the board's socket, the duct, the left dock and tray, the skin, the clear space over the fan of the supply), and `tools/draw_duct_lead.py` writes three sheets in `cad/out/duct-lead/`, each with a view from above and one in perspective, every face edge drawn, and the key numbers:

1. `1-way-1.png`: the adapter straight in the board's socket. Its body ends 1.87 before the end wall, in the hot air. A right-angle HDMI plug (ESTIMATED 14 x 21 x 12) passes an opening in the end wall and leaves 16.92 to the side wall in the room of 26.65.
2. `2-way-2.png`: a short extension lead out through place C, and the adapter on the left dock. It shows the finding: an in-line socket (ESTIMATED 30 long) reaches down to z 107, and 2800 mm3 of it is in the clear space over the fan of the supply (z 96 to 121).
3. `3-places.png`: A, B and C marked on the duct, C recommended, and the present notch.

The sizes of the plugs, the socket and the leads are estimates. The scenes are not parts of the build.

## Way 1 as built

- **The opening of the end wall** (`rear.hdmi_cuts`): 25 along the adapter's width by 14.5 along its thickness, round the axis of the board's socket, from 1.0 below the top of the duct's floor. It passes the plug of about 21 x 12 (ESTIMATED) with 2 at each side. With the plug 3 deeper in the socket than the estimate of 9, the adapter's own body (19.88 x 9.84) goes 1.1 into the opening, which passes it too; 3 less, and the plug still stands through the wall. The floor has a relief 1.0 deep, 8 long, under the plug: centred on the adapter, a plug of 12 reaches 0.5 below the top of the floor. `rear.adapter_rows` and `tests/test_rear.py` hold this at 6, 9 and 12 in the socket.
- **The seal** (`rear.hdmi_seal`): a pad of closed-cell foam 3 thick on the outside of the end wall, 5 beyond the opening on each side, with a hole cut to the plug. With the pad nothing is open round the plug; without it, 1.1 cm2 (1.3 % of the hot-air vent).
- **The order.** In: the board on its tray with the duct; the adapter into the board's socket through the open side of the duct (toward the door); the HDMI plug into the adapter from outside, through the opening; the foam pad over the plug; the lead along the side wall to the left cable channel; the door last. Out: the door first; nothing is unplugged, because the duct, the adapter and the lead stay with the cabinet and the door only presses on the foam strip of the duct. To take the compute module out: the door off, the HDMI plug out of the adapter (it goes back through the opening; the foam pad comes off with it), then the adapter out of the board's socket through the open side of the duct, then the tray. `cad/out/duct-lead/4-built.png` shows the parts and the order.
- **The lead's path.** The plug turns the lead toward the front of the cabinet, so the lead turns in its plug and not in the room of 26.65 beside the duct; that room needs only the lead's diameter (6, with 16.9 left after the plug). The lead runs along the side wall to the left cable channel and in it to the mini-HDMI socket: about 205, and the monitor needs 100 of slack to come forward. A lead of 0.5 m. The route is a schematic line on the sheet: it is not checked against the tray, the dock or the other leads there. The bend radius of a lead of 6 is about 30 (ESTIMATED: five times its diameter, a common rule for copper leads); its bends are in the open room, not in the 17.
- **The lead to buy** is in `docs/design/hardware-list.md` ("Video cable"), by the geometry of each end.

## What way 2 would still need

The fix for the extension's socket in the clear space over the supply's fan (2800 mm3 of it is there: the adapter turned over, a lead with a right-angle socket, or the place moved up), and notch C in the duct body. The place on the left dock stays for it and holds nothing.

## Not done

Nothing is modelled. The sizes of the extension's plug and socket are estimates. The leak is an estimate from areas; no air flow was calculated.
