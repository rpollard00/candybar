# Control panel latch

Date: 2026-11-16. Roadmap step 12. This document gives the latch of the control panel that the owner chose, in its final form, as a proposal. It also keeps the study that led to it.

The owner rejected the screws of option A (2026-11-14): "I don't like screws as it defeats how swappable it is. Magnets plus a printed latch mechanism to keep it from moving? We can fall back to screws but we should investigate more." The study built four latches with no tool. The owner chose B (2026-11-15): "Yeah we can do the button on the decks front face. Ideally on the center line. I don't think it needs to pop up, pushing it in should allow it to be lifted out. I think simpler is better here with less chance of failure."

The source is `cad/candybar/shell/panel_latch.py`. The tests are in `cad/tests/test_panel_latch.py`. The drawings come from `cad/tools/draw_panel_latch.py`. The build output is `cad/out/panel-latch/` (not in git). Since 2026-11-16 B is the default of the build: `panel_frame.Interface.latch` is `PUSH_BOLT`, its values are `panel_frame.PushBolt`, and its functions are in `panel_frame.py` (see "For the shared files", done). This module builds B from there and keeps M, H and Q as the record of the study.

All dimensions are in millimetres, in the frame of `dims.py`. A depth with the name `yl` is a distance from the front edge of the panel at the centre line, as in `control-panel.md`. A value marked ESTIMATED is a calculation, not a test.

## The latch: hooks and a push bolt (B)

Two hooks under the rear edge of the panel hold the rear edge. One bolt at the front centre holds the front edge. Four magnet pairs hold the corners down. Nothing shows on the top face of the panel.

- **The rear hooks.** Two hooks under the rear edge of the panel, at x -100 and x +100, go into notches in the rear bar of the frame. The top and the bottom of each toe are arcs about the rear top edge of the plate. Thus the toe slides out of its notch when the front of the panel goes up.
- **The bolt.** A printed bar 12 x 6 along the centre line, under the front bar of the frame. It slides in a tunnel that is one print with the left half of the frame. Its front end is a flush button in the front face of the deck.
- **The strike.** Two legs under the front edge of the panel, each side of the bolt, with a lip on each leg in under the bolt.
- **The spring.** A steel spring pushes the bolt forward. The underside of the bolt and the top of each lip meet at 8 degrees. Thus the spring pulls the panel down through the wedge (the preload). A lift of the panel cannot push the bolt back while the friction coefficient is more than 0.14. ABS on ABS is 0.25 to 0.45 (ESTIMATED).
- **The gate.** A small printed plate dropped into a slot at the rear of the tunnel. The spring pushes against it. The plate of a seated panel stands 0.7 above the gate, so the gate cannot leave its slot while a panel is in.
- **The magnets.** A magnet of 12 x 2 in the frame at each of the four latch points of `control-panel.md`, and a steel disc of 12 x 2 above it in the panel (the user, 2026-11-16). The two at the front keep the front corners down (see "The front corners").
- **The button.** The outline of its hole moved in by 0.3: the gap is 0.3 all round. The hole's corners are R 1.5 and the button's R 1.2 (2026-11-16; before, a sharp button in corners of 0.5 had 0.292 at the corners).

### To take the panel out

1. Push the button in and hold it. The bolt slides back 5. After 4.25 the lips are free.
2. Lift the front edge of the panel: by the lever, or a panel with nothing to hold by its finger hole.
3. The panel turns about its rear edge. Lift it up and pull it forward.
4. Release the button. The spring pushes the bolt forward again.

### To put the panel in

1. Hold the panel with its front edge up. Put its rear edge down against the rear of the pocket.
2. Push the button in and hold it.
3. Lower the front edge into the pocket.
4. Release the button.

If the button is not held, the lips land on the bolt. The front of the panel then stands 8 high and does not go down. The player sees at once that the panel is not seated.

### What changed from the study

| | B as studied (2026-11-15) | B final (2026-11-16) |
| --- | --- | --- |
| Printed parts in the cabinet | Frame halves (2), posts (4), housing, cover, bolt: 9 | Frame halves (2, the tunnel is a part of the left half), posts (4), bolt, gate: 8 |
| Printed latch parts that are separate parts | Housing, cover, bolt: 3 | Bolt, gate: 2 |
| Springs | 3 (the bolt spring and two lift springs) | 1 (the bolt spring) |
| Screws | 2 (the cover) | 0 |
| Magnets | 2 in the frame (rear), 2 in each panel | 4 in the frame, 4 in each panel |
| Printed parts on each panel | 2 hooks and 1 strike, with the tiles | The same |
| Hold: worst factor | 2.4 | 2.9 |
| No click in normal play: factor on the preload | 2.1 | 8.2 |
| Preload at the front | 17 N from the wedge less 8 N from the lift springs: 9 N | 15 N from the wedge |
| To lift out with the button held | The springs lifted the front edge 7.7 | 55 N up on the lever, 35 N at the finger hole of a blank panel |

## The hold

### The loads

The lever stands at x -75, yl 87.5. The ball centre is 40.65 above the top face of the panel and 45.65 above the rest face. The load cases at the ball are:

- A pull of 80 N upward.
- A push of 50 N to the front, to the rear, to the left and to the right.
- The pull and each push together.

The weight of the panel (5 N) holds it down a little.

### The method

The plate rests on its ledge. The ledge can push up but it cannot pull down. Thus the plate can leave its ledge in two ways only: a straight lift, or a turn about a line that touches the outline of the plate or lies outside it. The module tries the straight lift and 1080 lines (180 directions, 6 places for each).

For each way, the restraints and the weight do work against the work of the load. The smallest ratio is the factor of the load case. A restraint does work only where it goes up. A hook does not count in the turn about the rear top edge, because that turn is how it lets go. This is a rigid-plastic bound: it uses the full capacity of every restraint that moves.

### The magnets (ESTIMATED)

Maker's data for an N52 disc on thick steel, at contact (pull case 1):

- 12 x 5: 46 N (one maker).
- 12.7 x 4.76: 50 N (a second maker).

For other thicknesses, a fit to these values gives F = 75.6 (1 - exp(-h / 5.25)) N for a disc of 12. Then:

1. A pair of magnets at contact pulls about as one magnet of the two thicknesses together, less 25 %.
2. The gap is 0.3: the pad stands 0.1 below the rest face, and 0.2 is for the adhesive and the print. A gap of 1 loses more than half of the pull (maker's chart). The estimate uses exp(-gap / 1.0), which gives 0.74 for 0.3.
3. A use factor of 0.7 is for tilt, the coating, 40 degrees C in the cabinet and a pocket that is not square.

| Frame magnet | Plate magnet | Case 1 of the frame magnet | Pair at contact | Pull of the pair (ESTIMATED) | Used in |
| --- | --- | --- | --- | --- | --- |
| 12 x 10 (two of 12 x 5) | 12 x 2 | 64 N | 51 N | 26 N | M |
| 12 x 5 | 12 x 2 | 46 N | 42 N | 22 N | H |
| 12 x 2 | 12 x 2 | 24 N | 30 N | 16 N | B, Q |

A steel disc of 12 x 2 in the plate in place of the magnet removes the risk of a wrong pole. It saturates and gives about 10 % less pull (ESTIMATED). The magnets go in after the print, with epoxy.

### The rigid parts (ESTIMATED)

Printed ABS is taken as 35 MPa along the layers and 15 MPa across them. The weakest section of each part sets its value.

| Part | Weakest section | Capacity |
| --- | --- | --- |
| Rear hook | The stem, 14 x 6, in tension and bending across the layers (the tile prints top face down, so the stem stands upright) | 175 N |
| Strike of B | The lips, 4 x 2.3, in bending along the layers (the legs: 154 N, the roof of the tunnel: 241 N) | 145 N |
| Cam of Q | The tongue, 8 x 3.8, in bending along the layers (the shank: 754 N) | 135 N |

### The results

| Load case | M | H | B (final) | Q |
| --- | --- | --- | --- | --- |
| Pull 80 up | 0.91 | 0.98 | 3.85 | 6.14 |
| Push 50 to the front | 4.0 | 28 | 29 | 28 |
| Push 50 to the rear | 3.7 | 3.0 | 12 | 22 |
| Push 50 to the left or the right | 8.7 | 37 | 48 | 59 |
| Pull 80 and push 50 to the front | 0.91 | 1.46 | 5.01 | 6.14 |
| Pull 80 and push 50 to the rear | 0.91 | 0.74 | 2.90 | 5.46 |
| Pull 80 and push 50 to the left | 1.02 | 0.98 | 3.85 | 6.86 |
| Pull 80 and push 50 to the right | 0.83 | 0.98 | 3.85 | 5.56 |
| **Worst** | **0.83** | **0.74** | **2.90** | **5.46** |

In M and H the magnet nearest the lever lets go first, and the panel peels off. In H, a push to the rear lifts the front edge, and only the two front magnets hold it. For B, the worst case is a pull of 80 N and a push of 50 N to the rear at the same time. It loads the strike with about 50 N.

### No click in normal play

In normal play the lever gives about 15 N at the ball. Then only the preload holds the panel on its ledge: the magnets, the weight, and for B the wedge of the bolt. The hooks, the cams and the bolt have play (0.2 to 0.4), so they do not count. The factor on the preload alone is 12 for M, 10 for H, 8.2 for B and 7.0 for Q.

In B the spring pushes the bolt forward with 7.0 N. Through the wedge, this pulls the strike down with 15 N. The front edge lifts about 4.3 N in normal play.

### The front corners

The bolt holds the front edge only at the centre, and the lever is left of the centre. Thus a push at the ball to the rear lifts the front edge to the left of the bolt. The couple goes into the two ribs of the lever's bay (the rib beside the encoder at x -138.8 and the flanges of the seam at x -39). Each rib puts half of the lift up at the front edge.

The estimate treats the front strip of the plate (the plate 5 thick from the front edge to yl 40, with the front rib 3 x 15) as a beam along x. Its second moment of area is 4934 mm4, and E is 2200 MPa (ESTIMATED).

| Load at the ball, to the rear | Lift at the front edge | No front magnets: the front left corner lifts | With a magnet pair at the front left pad: largest lift | Share of the corner / pull of the magnet |
| --- | --- | --- | --- | --- |
| 15 N (normal play) | 4.3 N | 0.32 | 0.03 | 2.1 N / 16 N: factor 7.4 |
| 50 N (hard input) | 14 N | 1.06 | 0.10 | 7.1 N / 16 N: factor 2.2 |

Without front magnets, the strip is a cantilever from the bolt, and the corner is free. It lifts 0.3 in normal play and comes back down on the ledge: that is a click. With the magnets, the strip is held at the bolt and at the corner. It only bends 0.03 to 0.10 between them, and the magnet keeps its share with a factor of 2.2 or more. Thus the two front magnets are necessary. They are in the pockets that the interface already has.

The cost of the front magnets is the force to lift the panel out (see "To lift the panel out"). The beam estimate is a bound: the plate also carries some load from the corner to the rear magnet, so the real lift without front magnets is less than 0.32.

### To lift the panel out

With the button held, only the four magnets and the weight hold the panel. The module finds the smallest upward pull that frees the panel, with the same method as the hold. The hooks are free in the swing.

| Where the hand pulls | Force (ESTIMATED) |
| --- | --- |
| The ball of the lever, straight up | 55 N |
| The middle of the front edge | 28 N |
| The finger hole of a blank panel | 35 N |

55 N on the lever is a firm pull: the four magnets let go one by one as the panel turns. Steel discs in the panel in place of the magnets give about 10 % less.

## The grip of a panel with nothing to hold

The arcade panel lifts by its lever. A blank panel sits flush in its pocket with a gap of 0.3, and with the button held it still needs a pull of 28 to 35 N. Two ways add no part and no spring. Sheet `06-B-grip-for-a-blank-panel.png` shows both.

**A. A finger hole in the panel (the proposal).** A hole of 22 through the plate of the blank panel, at x 50, yl 37, with the edge break of R 1 on both rims. A finger goes in, hooks under the plate and lifts it (35 N with the button held). It shows on the top face of the blank panel only. No part of the cabinet changes, and the hold does not change. It is not a part of the interface: a panel with a lever, buttons or keys lifts by them.

**B. A rigid ramp on the bolt (not taken).** A ramp of 45 degrees on the bolt lifts the strike 2.5 after the lips are free. The front edge then rises 2.9, and stands 0.9 above the deck top while the button is held. Nothing shows. But:

- The button must travel 7.8 in place of 5. A fingertip does not go that far into a flush hole of 14.6.
- The ramp lifts the front against the front magnets (32 N at the strike). Thus the button needs about 75 N.
- The bolt gets longer, and the floor of the tunnel must go down.
- An edge 0.9 above the deck top is too low to hold well.

A is simpler, adds no way to fail, and only a panel with nothing to hold carries it.

## The parts in the cabinet

### The tunnel, one print with the frame

The study had a housing and a cover with two screws. Now the tunnel of the bolt is a part of the left half of the frame:

- The halves of the frame now meet at x 20, not on the centre line. Thus the tunnel is whole in the left half. The left half is 217.2 x 174 x 19.1 and fits the printer (248 x 248 x 250).
- The floor of the tunnel lies in the plane of the lower face of the bar (z 48.8), from the front bar to yl 52.5, 32 wide. The half prints on that plane as before. A window in the floor takes the legs of the strike.
- The bolt passes the front bar through a notch above the floor. Under the bolt the bar stays whole.
- Behind the strike, two walls and a roof close round the bolt. The roof is a bridge of 12.4 and 15.4 on the printer. It carries the lift of the bolt (241 N, ESTIMATED).
- The right wall stands back from yl 34.7 to the rear, so that the stop block of the bolt goes in from the rear. A shoulder in it stops the bolt 0.3 in front of its locked place when no panel is in.
- At the rear, a slot through the roof and into the walls takes the gate.

A cover that snaps on is possible, but a snap stays bent or must bend each time. The gate needs no snap: the spring pushes it against the rear face of its slot, and the plate of the panel stands above it.

### What the frame print gains and loses

- One part less to print and to align. No screws, no inserts.
- No bond between the housing and the frame. The load of the bolt goes into the frame through printed material only.
- The left half has 3.8 cm2 of faces that look down: the roofs of the notch and of the tunnel. These are bridges of 16 or less, and they print with no support. The right half has 0.7 cm2 (the roof of its notch).
- The frame goes in from below before the floor. The left half goes in first and the right half after it. The tunnel is inside the left half, so it does not stop the right half.

### Assembly of the bolt (once, with the panel out)

1. Put the button end of the bolt into the hole in the front face of the deck from inside, through the opening. Lay the bolt in the tunnel.
2. Put the spring into the bore at the rear of the bolt.
3. Push the gate down into its slot. Its peg goes into the end of the spring.

To service the bolt, take the panel out, pull the gate up by its tab, and slide the bolt out to the rear.

## The button

- **Its place.** The hole in the deck nose stays as the study gave it: x 0, z 55.3, 14.6 across with two flats 12.6 apart, the rim with the edge break of R 1. The deck nose is one print piece, 218 wide, with its seams at x 137 each side. Thus the centre line has no seam.
- **Force and travel.** The button starts to move at 9.3 N: the spring (7.0 N), and the friction of the wedge less its slope. At the end of its travel of 5 it needs 15 N. The lips are free only after 4.25.
- **An unwanted push.** With no lift springs, a push only unlocks while it is held. If a push lets go before the panel is lifted, the bolt goes back over the lips and the panel stays locked. The button is flush in a hole of 14.6. A flat thing against the front face (a knee, a forearm, the edge of a desk) cannot push it in: only a fingertip can. Thus the button stays flush. A recess of 0.5 to 1 adds little protection and takes from the reach of a fingertip.

## Putting the panel in: no self-latching slope

A slope on the nose of the bolt or on the strike can let the panel push the bolt back as it goes down. This is not done:

- The bolt must move 5 for the lips to pass. A slope that does this needs 5 of height. The lock section of the bolt is 6 high, and the lips are 2.3 high. A slope of 5 on the bolt leaves 0.7 to 1.2 of material over the front of the lips, so the hold drops below 2. A slope on the lips can give only 2.3.
- With no slope, a panel that is not latched cannot sit flush: it stands 8 high at the front. With a slope and a bolt that sticks, a panel can sit flush and not be latched, and nothing shows it.

## What happens when it fails

| Failure | What the player notices | How the owner gets the panel out |
| --- | --- | --- |
| The spring breaks or goes weak | The button does not come back out after a push, or comes back slowly. The front can tick in hard play: the wedge has no preload, and only the magnets hold the front. | Push the button and lift the panel as usual. Then pull the gate up and put in a new spring. |
| The bolt sticks when it is locked (grit, a swollen print, a wedge pulled tight by a hard pull) | The button does not go in. | Press the front edge of the panel down with one hand: the wedge then has no load. Push the button with the other hand, with a pen if necessary. The bolt is one solid bar from the button to the lock, so a push on the button always reaches the lock. Its weakest section in compression (the neck, 4 x 6) takes about 800 N. |
| The bolt sticks when it is open | The button stays 5 deep in its hole. The panel sits on its magnets and is not locked. | Lift the panel out. Push the bolt forward with a finger through the opening, or take it out to clean it. |
| A rear hook breaks | The rear edge lifts in a hard pull, and the rear magnets pull it back with a tick. | Push the button and lift the panel as usual. A hook prints with its tile, so the tile must be printed again. |
| Grit in the tunnel | The button goes in stiffly, or comes back slowly. | Take the panel out, pull the gate, slide the bolt out and clean the tunnel. It is open at the front (the hole in the deck) and at the rear (the gate). |

The last way out is force. The strike on the panel is the weakest part of the latch (145 N, ESTIMATED). A part of the panel breaks before a part of the cabinet.

## Print, strain and wear

| Part | On the printer | Supports | What flexes when it moves |
| --- | --- | --- | --- |
| Tiles with the hooks and the strike | Top face down, as the tiles of `control-panel.md`. The hooks and the legs of the strike stand up. | None. The top arc of each toe looks down over about 0.7 cm2 for each hook. Each lip of the strike is an overhang of 3.4. Both print as short overhangs. | Nothing. The hooks are rigid. The toe has 0.3 of radial play under the roof of its notch. |
| Left half of the frame, with the tunnel | As the frame of `control-panel.md`: the lower face of the bar on the bed | None. The roofs of the tunnel and of the notch are bridges. | Nothing |
| Right half of the frame | The same | None. The roof of its notch is a bridge of 16. | Nothing |
| Bolt | On its side: the flat side (x -6) on the bed. The button has two flats for this. | None. The round of the button and the spring bore look down over 0.9 cm2 in all. | Nothing. The steel spring takes the travel. |
| Gate | Flat: its rear face on the bed, the peg up | None | Nothing |
| Blank panel with its finger hole | Top face down | None | Nothing |

No printed part bends when the latch moves. The parts that store energy are one steel spring and the magnets. They do not creep.

What wears after some hundreds of swaps:

- The magnets do not wear. Their adhesive can let go after many swaps. Use epoxy, and a pocket that holds the magnet by its rim.
- The front edge of the roof of each notch and the top of each toe rub when the hooks go in. ABS on ABS gives a polished mark and no loss of fit.
- The lips and the wedge under the bolt rub at each lock. If the wedge wears smooth, the friction decreases. The wedge of 8 degrees holds while the friction coefficient is more than 0.14. The bolt is a part of its own, and a new one prints in 30 minutes.
- The button rubs in its hole in the deck wall.

## The interface

These rows go into the interface table of `control-panel.md`. All other rows stay.

| Item | Value |
| --- | --- |
| Latch points (4) | Magnet: a pocket of 12.2 x 2.2 in the lower face, a disc of 12 x 2 (or a steel disc of 12 x 2) in it. This is the row of option B, with no change. |
| Rear hooks (2) | At x -100 and +100, 14 wide. A stem 6 thick, its rear face at yl 165.8. A toe whose top and bottom are arcs of R 16.5 and R 20 about the rear top edge of the plate (yl 174.7, z 70). Its tip at yl 170.6. |
| Strike (1) | At the front centre, yl 20.5 to 24.5. Two legs at x 6.2 to 13.2 each side of the centre line, down to z 49.5. Each leg has a lip 3.4 in under the bolt. The top of each lip falls 8 degrees to the rear. |
| Room below the plate | Less the box of the bolt: x -16.5 to +16.5, yl 0.5 to 52.5, z 48.3 to the rest face. A rib that crosses it (the front rib of the arcade panel, the seam of the blank panel) stops at it. |
| Sockets (2) | No change: the two cones locate the panel. |

The hooks and the strike print with the tiles of every panel. A blank panel needs no part that the arcade panel does not have. A panel with nothing to hold also has a finger hole (see "The grip"). That hole is a choice of the panel, not a row of the interface.

## Parts to print and to buy

To print, in the cabinet (once):

- The left half of the frame, with the tunnel of the bolt.
- The right half of the frame.
- The four posts (no change).
- The bolt.
- The gate.

To print, on each panel: the tiles, with the two rear hooks and the strike.

To buy: see [to-buy-and-measure.md](to-buy-and-measure.md) 1.4. The panels carry steel discs 12 x 2 (the user, 2026-11-16).

No screw, no insert.

## The first test piece

Print a strip of the front centre and a piece of one rear corner before the full panel:

1. A strip of the deck nose, 60 wide at the centre line, with the button hole.
2. The middle of the left half of the frame, 60 wide, with the tunnel, the notch of the front bar and the front ledge.
3. The bolt and the gate, with the bought spring.
4. A strip of a tile, 60 wide, with the strike.
5. A piece of the rear bar of the frame with one notch, and a piece of a tile with one hook and one magnet pocket.

The strip of the deck nose with the latch must prove these points:

- The button sits flush in the hole with a gap of 0.3 all round, and the rim of the hole has its edge break.
- A fingertip pushes the flush button through 5. If it does not, the stroke must decrease or the hole must increase.
- The bolt slides through its full stroke with no bind, and the spring pushes it back to the stop, flush.
- The bolt goes into the tunnel from the rear, and the gate drops into its slot. The tunnel roof prints as a bridge with no sag that touches the bolt.
- The wedge holds. Pull the strike up with 100 N (twice the load in the worst case). The bolt must not move back. If it moves, the wedge angle must decrease or the friction must increase.
- The strike has no click. Press it down and pull it up with 15 N. No movement must be felt.
- With the button held, the strike lifts out freely.
- With the button not held, the strike cannot go down.
- The lips of the strike print cleanly with no support, and the overhang of 3.4 gives a flat face for the wedge.

The piece of the rear corner must prove these points:

- The toe of the hook goes into its notch and comes out when the tile turns about its rear top edge. It must not catch.
- The real pull of one magnet pair at a gap of 0.3. Measure it with a spring balance and compare it with 16 N.

## The study

The study compared four latches with no tool. Each one starts from option B of `control-panel.md`: a magnet pair at each of the four latch points. The two cones at the rear edge stay in every candidate.

- **M. Magnets only.** The baseline, with the largest frame magnet that a pad takes (12 x 10). Pull it straight up.
- **H. Rear hooks and magnets (hook and drop).** The rear hooks of B. The front magnets (12 x 5) hold the front edge. The hooks are at the rear because the hands are at the front: a person lifts the front edge and the panel turns about the rear.
- **B. Rear hooks and a push bolt.** The final form is above. As studied, it had a housing and a cover with two screws, and two springs that lifted the front edge 7.7.
- **Q. Rear hooks and two quarter-turn cams.** Two printed cams go through the panel at x -128.5 and x +128.5, 17 from its front edge. Each cam has a flush head with a finger bar on the top face. Under the panel its tongue turns under the front bar of the frame.

| | M. Magnets only | H. Hooks and magnets | B. Hooks and push bolt (final) | Q. Hooks and two cams |
| --- | --- | --- | --- | --- |
| On the top face, panel in | Nothing | Nothing | Nothing | Two round heads of 16, flush, each with a finger bar 1.5 high, at x -128.5 and +128.5 |
| At the gap round the panel | 0.3, no change | 0.3, no change | 0.3, no change | 0.3, no change |
| On the front face of the deck | Nothing | Nothing | A flush button of 14 with two flats (12 wide), at the centre line, 55 above the desk, gap 0.3 | Nothing |
| Panel out | The frame: four pads with magnets, two cones, the cable clip | As M, and two notches of 16 in the rear bar | As H, and at the front centre the bolt, its tunnel and the tab of the gate | As H |
| The way out | Pull straight up | Pull the front up by the lever, the panel turns about its rear edge, then up and forward | Hold the button in, lift the front (lever or finger hole), then up and forward | Turn the two heads a quarter turn, lift the front, then up and forward |
| Force to take it out | 90 N up on the lever. A panel with no lever has no grip. | 83 N up on the lever. A panel with no lever has no grip. | 9.3 to 15 N on the button, then 55 N on the lever or 35 N at a finger hole | Turn two heads, then 60 N on the lever or a pull on the finger bars |
| Hold: worst factor | **0.83** | **0.74** | **2.9** | **5.5** |
| No click in normal play | 12 | 10 | 8.2 | 7.0 |
| Printed latch parts | None but the frame and the plate | 2 hooks on each panel | Bolt and gate in the cabinet (the tunnel is a part of the frame). 1 strike and 2 hooks on each panel. | 2 hooks on each panel. 2 studs and 2 tongues for each panel. |
| Bought parts | 8 magnets 12 x 5 (frame), 4 magnets 12 x 2 for each panel | 4 magnets 12 x 5, 4 magnets 12 x 2 for each panel | 4 magnets 12 x 2 (frame) and 4 for each panel. 1 spring. | 4 magnets 12 x 2 (frame) and 4 for each panel. 2 steel pins 3 x 14 and 2 O-rings for each panel. |
| Change of the interface | None | 2 hooks | 2 hooks, 1 strike, a box of the room | 2 hooks, 2 cam holes with a boss under the plate, the sweep of the tongues. 2 cams with each panel. |
| Change outside the panel files | None | None | A hole in the deck nose for the button | None |
| Risk | Does not meet the load. A hard pull lifts the panel out. | Does not meet the load at the front. No grip without a lever. | The wedge holds by friction. A new mark on the front face. | Two heads on the top face. Each panel needs two cams. A cam left open is not seen. |

### Candidates that the study did not build

**D. A detent.** A printed arm with a bump that drops into a groove holds up to a set force and lets go above it. An arm of 20 x 10 x 2 with a bump of 1 can hold 40 N with a ramp of 45 degrees. It bends to 0.75 % strain only while the panel goes in or out (ESTIMATED). But a detent that holds the front edge against the lever lets go only above its hold. Thus a person must pull the lever up with about 78 N to take the panel out, and a hard input of the same size also opens it. M and H show the same problem with magnets. It is not built.

**Larger magnets at new points.** A disc of 20 can go in a pad if the latch point moves 7 farther into the opening. M then holds the pull of 80 N with a factor of about 1.3, and the release is still 140 N on the lever. It is not built.

**A slide-in tongue.** The slide needs a gap of 4 to 6 at the front or at the rear edge of the pocket, which shows. It is not built.

**A toggle (draw) latch.** It needs a lever that a hand reaches. Under the panel no hand reaches it, and on the top face it shows more than a cam head. It is not built.

### The checks

The module does every check of `panel_frame` on each candidate. It uses the real skin of the deck (from the cached skin of the shell) and the hardware of the fit study. All four candidates pass, B in its final form included.

| Check | Result |
| --- | --- |
| Each part against the skin of the deck, against each other part and against the hardware (envelopes and keep-out zones) | 0.0 mm3 in common. The fit rules permit 1. |
| The blank panel of each candidate against the skin, the frame, the latch parts, the USB sockets and the hub | 0.0 mm3 |
| The room below the plate | Free of the skin and the frame. The arcade panel and all its hardware are in the room. The notches of the hooks and (B) the place of the strike and (Q) the place of the locked tongues count as room. |
| The way out, in steps | 0.0 mm3 at each step (see the list that follows) |
| The locks | A straight lift of 1 meets the roofs of the notches. A swing of 2 degrees with the bolt (B) or the cams (Q) locked meets the lock. Thus the panel cannot leave without the release. |
| Edge rule | No sharp convex edge shows. The rim of the button, the rims of the finger hole and the edges of the cam heads have the edge break of R 1. |
| Face check | No finding fails. No face is narrower than 2. |
| Print | Each part fits the printer. |

The way out is modelled as a real motion. At each step the moving group is the arcade panel with its lever, buttons, encoder and latch parts. The fixed group is the skin of the deck, the frame and the fixed latch parts:

- M: a straight lift of 2, 5, 10, 20, 40 and 80.
- H: a turn of the panel about its rear top edge (yl 174.7, z 70), front up, of 1, 2, 3, 4, 6, 8, 10, 13, 16 and 20 degrees. Then up 6 and forward 2 for each step, to 96 up.
- B: the bolt back by 1, 2.5 and 5, against the deck, the frame with its tunnel, the gate and the seated panel. Then the turn and the lift of H.
- Q: the cams turned by 15 to 90 degrees in steps of 15. Then the turn and the lift of H.

The checks found these faults in the first designs. Each one is corrected:

- In Q, the boss of each tongue stood 0.5 behind the front bar. In the turn it moves forward 0.15 for each 1 that it rises, so it touched the bar after a turn of 2 degrees. The boss now stands 3 behind the bar.
- In Q, the first cams were at x 150, outside the flank break of the deck front (x 138.5), where the front edge of the opening turns back 1.6. The cams are now at x 128.5, on the middle line of the rib beside the service buttons.
- In B, the lips of the strike move forward 0.8 in the first 2 degrees of the turn. They touched the full section of the bolt in front of the neck. The neck is now 2 longer at its front end.
- In B, the stop block of the bolt stood out on both sides, so the bolt did not lie flat on the printer. It now stands out on one side only.
- In H, B and Q, the stem of the first hook left a strip 0.8 wide of its lower face beside the toe. The stem now goes down to the bottom arc of the toe.
- On the small latch parts, the face check found faces narrower than 2. In the final B, the seat of the spring in the gate was a pocket 1.5 deep: it is now a peg.

## Pictures

The sheets are in `cad/out/panel-latch/sheets/`. Every BREP edge is drawn.

| Sheet | Content |
| --- | --- |
| `01-M-magnets-only.png` | M (the study) |
| `02-H-hooks-and-magnets.png` | H (the study) |
| `03-B-hooks-and-a-push-bolt.png` | B in its final form |
| `04-Q-hooks-and-two-quarter-turn-cams.png` | Q (the study) |
| `05-side-by-side.png` | The four candidates of the study from the same camera. It shows B as studied. From the front and from above, the final B looks the same. |
| `06-B-grip-for-a-blank-panel.png` | The finger hole (the proposal) and the ramp on the bolt (not taken) |

Each sheet of a candidate has nine pictures:

- What the player sees.
- The front face of the deck.
- A section through the latch, locked and released.
- The way out in four steps.
- The latch parts apart.

## Build

```sh
CANDYBAR_OUT=cad/out/panel-latch cad/candybar/freecad-run.sh candybar.shell.panel_latch     # 8 minutes: parts, checks, scenes
cad/.venv-tools/bin/python cad/tools/draw_panel_latch.py                                     # renders and sheets
cad/test.sh test_panel_latch                                                                 # 34 tests, 6 minutes
```

`CANDYBAR_LATCH=B` builds only B. The results of the other candidates stay in `summary.json`. `CANDYBAR_LATCH_SCENES=0` writes no scenes. `draw_panel_latch.py B` renders B only and makes sheets 03 and 06. The first command needs the skin of the shell in `cad/out/shell-rev7/split/cache`, as `panel_frame` does.

| Output | Content |
| --- | --- |
| `report.md`, `summary.json` | The results of the four candidates |
| `<candidate>/report.json`, `<candidate>/report.md` | Every row of the checks of one candidate |
| `<candidate>/parts/` | The printed parts as BREP and STL |
| `<candidate>/scenes/`, `<candidate>/renders/` | The models and the renders of its sheet |
| `scenes/compare-*`, `renders/compare-*` | The side-by-side views |

## Where this was built

The latch was built and tested on the server (OpenCascade 7.8.1). The laptop (OpenCascade 7.9.3) is the reference and must build it again before a merge.

- The default build of the shell does not complete on the server: it stops at the edge break of the hood. The study uses the parts and the cached skin that the laptop built (`cad/out/shell-rev7`). The outer form has not changed since then.
- The edge break of the button, of the rims of the finger hole and of the cam heads tries R 1. For the button and the cam heads a smaller round is the fall-back if R 1 fails. On the server, R 1 worked on each part. If the laptop needs the smaller round, the face check reports the break faces, and the test `test_no_check_fails` fails.
- No other part of the code depends on the kernel.

## Assumptions

1. The magnet pulls are ESTIMATED from maker's data for two sizes. The gap, the pair and the use factors are estimates. Nothing is tested.
2. The strength of printed ABS is 35 MPa along the layers and 15 MPa across them (ESTIMATED).
3. The friction coefficient of ABS on ABS is 0.25 to 0.45. The latch uses 0.3.
4. The spring of the bolt is a standard steel compression spring: 4 outside, 22 free, about 1.2 N/mm. It is 5.8 shorter than free at the lock and 10.8 shorter at the end of the stroke. Measure the bought spring.
5. A fingertip goes 4.5 to 6 into a hole of 14.6 with a soft pad. The test piece must show it.
6. The hold method treats the plate as rigid. The plate bends a little under the lever (`control-panel.md`, "Deflection"). This moves load from the far restraints to the near ones, so the real factor can be lower than the calculated one. "The front corners" gives a beam estimate of the bend at the front edge.

## Open questions for the owner

Answered by the user on 2026-11-16:

1. The lift-out force of about 55 N on the lever is the starting value. With steel discs in the panel the estimate is 49.2 N on the lever and 31.1 N at the finger hole (the build of 2026-11-16, `cad/out/control-panel/report.md`). After the first print, the size of the front magnets is the thing to change: weaker front magnets give less force, but the front corners can then click in hard play.
2. The blank panel has the finger hole of 22.
3. The panels carry steel discs of 12 x 2, and the frame carries the magnets. With steel discs one latch point holds 14.1 N (ESTIMATED), the hold in the worst case has a factor of 2.85 and the preload in normal play a factor of 7.3.

## For the shared files

Done on 2026-11-16, with these differences: the values of B are in `panel_frame.PushBolt` (a field of `Interface`), not in `Interface` itself; the estimates of the hold stay in `panel_latch.py`, and `panel_frame.check()` reports them for the default (`panel_latch.default_hold`); the halves of the frame are cut at x 20 directly, not joined again and cut (the study's `resplit`); the room of the bolt reaches 3 behind the tunnel (0.5 before), because the seam rib of the blank panel swings into the end of the roof at 3 to 4 degrees.

### `cad/candybar/shell/panel_frame.py` (on the laptop)

- Add a value `PUSH_BOLT = "push-bolt"` for `Interface.latch`, and make it the default. `SCREW` stays as the fall-back option and `MAGNET` stays as an option. The tests of options A and B stay.
- With `PUSH_BOLT`:
  - The frame has the magnets of option B in all four pads (12 x 2).
  - The halves of the frame meet at x 20. The left half has the tunnel (`panel_latch.tunnel`) and the notch of the front bar (`panel_latch.front_notch`). Both halves have the notches of the hooks (`panel_latch.notches`).
  - Every panel has the two rear hooks (`panel_latch.hook`), the strike (`panel_latch.strike`), and the box of the bolt cut from its ribs (`panel_latch.bolt_room`).
  - The parts that stay in the cabinet are the bolt (`panel_latch.bolt`) and the gate (`panel_latch.gate`).
  - The blank panel has the finger hole (`panel_latch.finger_hole`).
- The values of `Latch` that B uses (the hooks, the push bolt, the tunnel) move into `Interface`, and the functions of B move from `panel_latch.py` into `panel_frame.py`. The check of the way out (`panel_latch.motion_rows`, `locked_rows`) replaces the straight lift of `lift_rows` for this latch.
- `panel_latch.py` then keeps M, H and Q as the record of the study, or goes. The owner decides.

### `docs/design/control-panel.md`

- "The latch": the latch is the push bolt of `control-panel-latch.md`. The table of options gets a row for it. Screws stay as the fall-back.
- "The interface of every control panel": the rows of "The interface" in this document.
- "The parts": the left half of the frame with the tunnel, the right half, the bolt and the gate. The masses: left half 80 g, right half 64 g, bolt 5 g, gate 1 g.
- "To remove the arcade panel": the steps of "To take the panel out" in this document.

### The shell (on the laptop)

The hole for the button in the deck nose: x 0, z 55.3, 14.6 across with two flats 12.6 apart, through the wall, horizontal. Its rim needs the edge break of R 1. The deck nose is the print piece "deck nose". Its seams F1 and F2 are at x 137, so the hole is not near a seam.

### Glossary (`CONTEXT.md`)

- **Push bolt**: The printed bolt of the latch of a control panel. It slides along the centre line in a tunnel of the panel frame, and its front end is a flush button in the front face of the deck. _Avoid_: slider, catch.
- **Strike**: The part under the front edge of a control panel that the push bolt holds: two legs with a lip on each.
- **Rear hook**: One of the two hooks under the rear edge of a control panel. Its toe goes into a notch in the rear bar of the panel frame.
- **Gate** (of the push bolt): The printed plate in a slot at the rear of the tunnel that holds the spring of the push bolt.
- Change **Latch point**: one of the four places where a magnet pair holds a control panel down on the panel frame.
- Change **Panel frame**: it has the tunnel of the push bolt and the notches of the rear hooks. Its halves meet at x 20.

### Roadmap (`docs/roadmap.md`)

- Step 12: the latch of the control panel is the push bolt (the owner, 2026-11-15, `docs/design/control-panel-latch.md`). Screws stay as the fall-back.
- Open decision "The latch": settled on 2026-11-15.
- Next: move the push bolt into `panel_frame.py` as the default, and cut the button hole into the deck nose. Print the test piece of the front centre.

### Hardware list (`docs/design/hardware-list.md`)

- 4 disc magnets N52 12 x 2, axial, for the frame, and 4 for each panel (or steel discs 12 x 2 in the panel).
- 1 compression spring, steel, 4 outside, 22 free, about 1.2 N/mm.
- The 4 screws M4 x 16 and the 4 inserts M4 of option A are no longer bought, unless screws are the fall-back.

### `cad/README.md`

The commands of "Build" in this document.

No value in `profiles.py`, `solids.py` or `cavity.py` changes.
