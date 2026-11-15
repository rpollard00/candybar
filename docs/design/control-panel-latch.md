# Control panel latch: a study

Date: 2026-11-15. Roadmap step 12. This document is a study. It does not change the default: `panel_frame.Interface.latch` stays `SCREW` (option A), and option B (magnets) stays as it is.

The owner rejected the screws of option A: "I don't like screws as it defeats how swappable it is. Magnets plus a printed latch mechanism to keep it from moving? We can fall back to screws but we should investigate more." This study looks for the best latch that needs no tool. It builds four candidates, compares them, and recommends one.

The source is `cad/candybar/shell/panel_latch.py`. The tests are in `cad/tests/test_panel_latch.py`. The drawings come from `cad/tools/draw_panel_latch.py`. The build output is `cad/out/panel-latch/` (not in git).

All dimensions are in millimetres, in the frame of `dims.py`. A depth with the name `yl` is a distance from the front edge of the panel at the centre line, as in `control-panel.md`. A value marked ESTIMATED is a calculation, not a test.

## What the latch must do

1. No tool and no loose part. One person changes the panel in a few seconds, from above or from the front.
2. The look comes first. Nothing on the top face is best.
3. The panel stays seated under a pull of 80 N upward on the lever, and under a push of 50 N at the ball in each horizontal direction, and under the two together. It sits without play or a click in normal play (15 N at the ball).
4. It lasts in ABS. A printed spring that stays bent when the panel is latched creeps. A rigid lock for the lift is better, with magnets or a spring that is not bent for the preload.
5. All panels share one interface. A blank panel must be easy to make.

## The candidates

Each candidate starts from option B: a magnet pair at each of the four latch points of `control-panel.md`. The magnet pocket in the plate (12.2 x 2.2) does not change. The two cones at the rear edge stay and locate the panel in every candidate.

**M. Magnets only.** The baseline. It has the largest frame magnet that a pad takes: two discs of 12 x 5 stacked (12 x 10). To take the panel out, pull it straight up.

**H. Rear hooks and magnets (hook and drop).** Two hooks under the rear edge of the panel, at x -100 and x +100, go into notches in the rear bar of the frame. The top and the bottom of each toe are arcs about the rear top edge of the plate. Thus the toe slides out of its notch when the front of the panel goes up. The two front magnets hold the front edge.

The hooks are at the rear edge for two reasons. First, the hands are at the front: a person lifts the front edge and the panel turns about the rear. Second, a hook at the front edge is near the palms, and the rear edge is near the screen, where a hand cannot get under it.

**B. Rear hooks and a push bolt.** The rear hooks of H hold the rear edge. At the front centre, a printed bolt goes over two lips of a strike under the panel. The bolt is a bar 12 x 6 along y in a housing under the front bar of the frame. Its front end is a flush button in the front face of the deck.

- A steel spring pushes the bolt forward. The underside of the bolt and the top of each lip meet at 8 degrees. Thus the spring pulls the panel down through the wedge (the preload).
- The wedge locks by friction: a lift of the panel cannot push the bolt back while the friction coefficient is more than 0.14. ABS on ABS is 0.25 to 0.45 (ESTIMATED).
- Push the button: the bolt slides back 5, and a narrow neck of the bolt comes over the lips. The lips are free. Two springs in the housing lift the front edge of the panel 7.7.

**Q. Rear hooks and two quarter-turn cams.** The rear hooks of H hold the rear edge. Two printed cams go through the panel at x -128.5 and x +128.5, 17 from its front edge. Each cam has a flush head with a finger bar on the top face. Under the panel its tongue turns under the front bar of the frame. Q is the comparison for "almost no tool": two heads show.

### Candidates that this study did not build

**D. A detent.** A printed arm with a bump that drops into a groove holds up to a set force and lets go above it. An arm of 20 x 10 x 2 with a bump of 1 can hold 40 N with a ramp of 45 degrees. It bends to 0.75 % strain only while the panel goes in or out (ESTIMATED). The problem is the release. A detent that holds the front edge against the lever lets go only above its hold. Thus a person must pull the lever up with about 78 N to take the panel out, and a hard input of the same size also opens it. The hold and the release are the same force at the same place. M and H show the same problem with magnets. D adds a part that wears and gives nothing that H does not give. It is not built.

**Larger magnets at new points.** A disc of 20 can go in a pad if the latch point moves 7 farther into the opening. The pull of a pair goes up about 60 %. M then holds the pull of 80 N with a factor of about 1.3, and the release is still 140 N on the lever. It changes the interface for little gain. It is not built.

**A slide-in tongue.** A tongue under the rear edge, and the panel slides back to lock. The slide needs a gap of 4 to 6 at the front or at the rear edge of the pocket, which shows. It is not built.

**A toggle (draw) latch.** It gives a good preload, but it needs a lever that a hand reaches. Under the panel no hand reaches it, and on the top face it shows more than a cam head. It is not built.

## The comparison

| | M. Magnets only | H. Hooks and magnets | B. Hooks and push bolt | Q. Hooks and two cams |
| --- | --- | --- | --- | --- |
| On the top face, panel in | Nothing | Nothing | Nothing | Two round heads of 16, flush, each with a finger bar 1.5 high (0.5 below the deck top), at x -128.5 and +128.5, 17 behind the front edge |
| At the gap round the panel | 0.3 all round, no change | 0.3, no change | 0.3, no change | 0.3, no change |
| On the front face of the deck | Nothing | Nothing | A button of 14 with two flats (12 wide), flush with the leaning band at the centre line, 55 above the desk, gap 0.3 | Nothing |
| Panel out | The frame: four pads with magnets, two cones, the cable clip | As M, and two notches of 16 in the rear bar | As H (magnets in the rear pads only), and at the front centre: the bolt, the cover of its housing, two springs | As H |
| The way out | Pull straight up | Pull the front up (by the lever), the panel turns about its rear edge, then up and forward | Push the button, the front edge rises 7.7 by itself, lift the edge, then up and forward | Turn the two heads a quarter turn, lift the front (lever or finger bars), then up and forward |
| Force to take it out | 90 N up on the lever. A panel with no lever has no grip. | 83 N up on the lever. A panel with no lever has no grip. | 16 N on the button. Then the front has no hold. | Turn two heads. Then 60 N on the lever, or a pull on the two finger bars. |
| Hold: worst factor (80 N up and 50 N at the ball) | **0.83**: the panel comes out | **0.74**: the panel comes out | **2.4** (the strike) | **5.5** (the cams) |
| Normal play without a click: factor on the preload | 12 | 10 | 2.1 | 7.0 |
| Printed latch parts | None but the frame and the plate | 2 hooks on each panel (with the tiles) | Bolt, housing and cover in the cabinet. 1 strike and 2 hooks on each panel. | 2 hooks on each panel. 2 studs and 2 tongues for each panel. |
| Bought parts | 8 magnets 12 x 5 (frame), 4 magnets 12 x 2 for each panel | 4 magnets 12 x 5, 4 magnets 12 x 2 for each panel | 2 magnets 12 x 2 (frame) and 2 for each panel. 1 bolt spring, 2 lift springs, 2 screws 3.0 x 10. | 4 magnets 12 x 2 (frame) and 4 for each panel. 2 steel pins 3 x 14 and 2 O-rings for each panel. |
| Change of the interface | None | 2 hooks | 2 hooks, 1 strike, a box of the room for the bolt, a flat place on the lower face for the lift springs | 2 hooks, 2 cam holes with a boss under the plate, the sweep of the tongues. 2 cams with each panel. |
| Change outside the panel files | None | None | A hole in the deck nose for the button | None |
| Risk | Does not meet the load. A hard pull lifts the panel out. | Does not meet the load at the front. No grip without a lever. | The wedge holds by friction. The button is a new mark on the front face. More parts in the cabinet. | Two heads on the top face. Each panel needs two cams. A cam left open is not seen. |

The factors are ESTIMATED (see "The hold"). A factor below 1 means that the panel comes out under that load.

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
| Strike of B | The lips, 4 x 2.3, in bending along the layers (the legs: 154 N; the cover of the housing: 241 N) | 145 N |
| Cam of Q | The tongue, 8 x 3.8, in bending along the layers (the shank: 754 N) | 135 N |

### The results

| Load case | M | H | B | Q |
| --- | --- | --- | --- | --- |
| Pull 80 up | 0.91 | 0.98 | 3.18 | 6.14 |
| Push 50 to the front | 4.0 | 28 | 28 | 28 |
| Push 50 to the rear | 3.7 | 3.0 | 9.7 | 22 |
| Push 50 to the left or the right | 8.7 | 37 | 45 | 59 |
| Pull 80 and push 50 to the front | 0.91 | 1.46 | 4.72 | 6.14 |
| Pull 80 and push 50 to the rear | 0.91 | 0.74 | 2.39 | 5.46 |
| Pull 80 and push 50 to the left | 1.02 | 0.98 | 3.18 | 6.86 |
| Pull 80 and push 50 to the right | 0.83 | 0.98 | 3.18 | 5.56 |
| **Worst** | **0.83** | **0.74** | **2.39** | **5.46** |

In M and H the magnet nearest the lever lets go first, and the panel peels off. In H, a push to the rear lifts the front edge, and only the two front magnets hold it.

For B, the worst case loads the strike with about 60 N. The case is a pull of 80 N and a push of 50 N to the rear at the same time.

### No click in normal play

In normal play the lever gives about 15 N at the ball. Then only the preload holds the panel on its ledge: the magnets and the weight, and for B the wedge of the bolt. The hooks, the cams and the bolt have play (0.2 to 0.4), so they do not count. The factor on the preload alone is 12 for M, 10 for H, 2.1 for B and 7.0 for Q.

In B the wedge pulls the strike down with 17 N. The two lift springs push it up with 8 N. Thus the net preload at the front is 9 N. The front edge lifts about 4.3 N in normal play.

## The motion and the checks

The module does every check of `panel_frame` on each candidate. It uses the real skin of the deck (from the cached skin of the shell) and the hardware of the fit study. All four candidates pass.

| Check | Result |
| --- | --- |
| Each part against the skin of the deck, against each other part and against the hardware (envelopes and keep-out zones) | 0.0 mm3 in common. The fit rules permit 1. |
| The blank panel of each candidate against the skin, the frame, the latch parts, the USB sockets and the hub | 0.0 mm3 |
| The room below the plate | Free of the skin and the frame. The arcade panel and all its hardware are in the room. The notches of the hooks and (B) the place of the strike and (Q) the place of the locked tongues count as room. |
| The way out, in steps | 0.0 mm3 at each step (see the list that follows) |
| The locks | A straight lift of 1 meets the roofs of the notches. A swing of 2 degrees with the bolt (B) or the cams (Q) locked meets the lock. Thus the panel cannot leave without the release. |
| Edge rule | No sharp convex edge shows. The rim of the button and the edges of the cam heads have the edge break of R 1. |
| Face check | No finding fails. No face is narrower than 2. |
| Print | Each part fits the printer. |

The way out is modelled as a real motion. At each step the moving group is the arcade panel with its lever, buttons, encoder and latch parts. The fixed group is the skin of the deck, the frame and the fixed latch parts:

- M: a straight lift of 2, 5, 10, 20, 40 and 80.
- H: a turn of the panel about its rear top edge (yl 174.7, z 70), front up, of 1, 2, 3, 4, 6, 8, 10, 13, 16 and 20 degrees. Then up 6 and forward 2 for each step, to 96 up.
- B: the bolt back by 1, 2.5 and 5, against the deck, the frame, the housing and the seated panel. Then the turn and the lift of H.
- Q: the cams turned by 15 to 90 degrees in steps of 15. Then the turn and the lift of H.

The checks found these faults in the first designs. Each one is corrected:

- In Q, the boss of each tongue stood 0.5 behind the front bar. In the turn it moves forward 0.15 for each 1 that it rises. Thus it touched the bar after a turn of 2 degrees. The boss now stands 3 behind the bar.
- In Q, the first cams were at x 150. That is outside the flank break of the deck front (x 138.5), where the front edge of the opening turns back 1.6. The cams are now at x 128.5, on the middle line of the rib beside the service buttons. Thus the rib crosses the boss of the cam cleanly.
- In B, the lips of the strike move forward 0.8 in the first 2 degrees of the turn. They touched the full section of the bolt in front of the neck. The neck is now 2 longer at its front end.
- In B, the stop block of the bolt stood out on both sides, so the bolt did not lie flat on the printer. It now stands out on one side only.
- In H, B and Q, the stem of the first hook left a strip 0.8 wide of its lower face beside the toe. The stem now goes down to the bottom arc of the toe.
- On the small latch parts, the face check found faces narrower than 2: the button cut by the crease of the front face, a spring bore larger than the bolt, the bottoms of pilot holes, the rings of thin bosses. The button now lies wholly in the leaning band, the bolt spring is 4 outside, the pilot holes go through, and the bosses are larger.

## Print, strain and wear

| Part | On the printer | Supports | What flexes when it moves |
| --- | --- | --- | --- |
| Tiles with hooks (H, B, Q) | Top face down, as the tiles of `control-panel.md`. The hooks stand up. | None. The top arc of each toe looks down 45 degrees or more over about 0.7 cm2 for each hook. It is a short overhang. | Nothing. The hooks are rigid. The toe has 0.3 of radial play under the roof of its notch. |
| Strike of B (with the tile) | Top face down: the legs stand up, and the lips are at their tips. | None. Each lip is an overhang of 3.4. It prints as a short overhang. | Nothing |
| Bolt of B | On its side: the flat side (x -6) on the bed. The button has two flats for this. | None. The round of the button and the spring bore look down over 0.9 cm2 in all. | Nothing. The steel spring takes the travel. |
| Housing of B | On its floor, as in the cabinet | None | Nothing |
| Cover of B | Its top on the bed | None | Nothing |
| Cam stud of Q | Upright, the end of the shank on the bed. A cone of 45 degrees under the head. | None | Nothing |
| Cam tongue of Q | Flat, the arm on the bed. The hole of the pin is level. | None | Nothing |
| Frame halves | As in `control-panel.md`. The notches of the hooks are open at the bottom. Their roof is a bridge of 16. | None | Nothing |

No printed part of the four built candidates bends when the latch moves. The parts that store energy are steel springs (B) and magnets. They do not creep.

What wears after some hundreds of swaps:

- The magnets do not wear. Their adhesive can let go after many swaps. Use epoxy, and a pocket that holds the magnet by its rim.
- The front edge of the roof of each notch and the top of each toe rub when the hooks go in. ABS on ABS gives a polished mark and no loss of fit.
- B: the lips and the wedge under the bolt rub at each lock. If the wedge wears smooth, the friction decreases. The wedge of 8 degrees holds while the friction coefficient is more than 0.14. The bolt is a part of its own, and a new one prints in 30 minutes. The button rubs in its hole in the deck wall.
- Q: the tongue rubs under the front bar at each turn. The finger bar of each head wears smooth first.

## The interface

A candidate adds these rows to the interface table of `control-panel.md`. All other rows stay.

| Item | M | H | B | Q |
| --- | --- | --- | --- | --- |
| Latch points (4) | Magnet: a pocket of 12.2 x 2.2 in the lower face, a disc of 12 x 2 in it (option B, no change) | As M | As M. The two front pockets stay empty. | As M |
| Rear hooks (2) | | At x -100 and +100, 14 wide. A stem 6 thick, its rear face at yl 165.8. A toe whose top and bottom are arcs of R 16.5 and R 20 about the rear top edge of the plate (yl 174.7, z 70). Its tip at yl 170.6. | As H | As H |
| Strike (1) | | | At the front centre, yl 20.5 to 24.5. Two legs at x 6.2 to 13.2 each side of the centre line, down to z 49.5. Each leg has a lip 3.4 in under the bolt. The top of each lip falls 8 degrees to the rear. | |
| Room below the plate | | The notches of the hooks are room. | Less the box of the bolt: x -26.5 to +26.5, yl 0.5 to 52.5, z 42.1 to the rest face. A rib that crosses it (the front rib of the arcade panel, the seam of the blank panel) stops at it. | Less a circle of 30 round each cam hole, from z 44.1 up: the sweep of the tongue |
| Lower face | | | Flat at x -20 and +20, yl 15: the two lift springs push there | |
| Cam holes (2) | | | | At x -128.5 and +128.5, yl 17.2: a hole of 8.4, a boss of 15 x 5 under the plate, a counterbore of 16.6 x 3.4 with a cone of 45 degrees under it. Each panel carries 2 cams. |

The hooks print with the tiles of every panel. A blank panel of H or B needs no part that the arcade panel does not have. A blank panel of Q needs its own two cams, pins and O-rings.

## The recommendation

**B: rear hooks and a push bolt, with magnets at the rear.**

- B is the only candidate with nothing on the top face, no tool and a rigid lock against the full pull. Its factor is 2.4.
- M and H keep the top face clear, but they do not hold the pull of 80 N, and their release is the same pull on the lever. A magnet strong enough to hold the panel is too strong to release it by hand.
- Q holds best (5.5), but it shows two heads on the top face and each panel needs two cams.
- B releases with one push of 16 N, and the front edge then rises 7.7 by itself. Thus a blank panel with no lever comes out as easily as the arcade panel.
- In B, the latch parts that move and wear are in the cabinet, once. A panel gets only two hooks and one strike, and these print with its tiles.

The cost of B is a button on the front face of the deck, a hole in the deck nose, and three printed parts and three springs in the cabinet. If the owner does not accept a button on the front face, Q is the second choice.

## The first test piece

Print a coupon of the front centre and of one rear corner before the full panel:

1. A strip of the deck nose with the button hole, the front bar of the frame with its notch, the housing, the cover and the bolt.
2. A strip of a tile, 60 wide, with the strike.
3. A piece of the rear bar of the frame with one notch, and a piece of a tile with one hook and one magnet pocket.

The coupon must prove these points:

- The bolt slides through its full stroke of 5 with no bind, and the spring pushes it back.
- A fingertip pushes the flush button through 5. If it does not, the stroke or the button size must change.
- The wedge holds. Pull the strike up with 120 N (twice the load in the worst case). The bolt must not move back. If it moves, the wedge angle must decrease or the friction must increase.
- The panel has no click. Press the strike down and pull it up with 15 N. No movement must be felt.
- The lips of the strike print cleanly with no support, and the overhang of 3.4 gives a flat face for the wedge.
- The toe of the hook goes into its notch and comes out when the tile turns about its rear top edge. It must not catch.
- The real pull of one magnet pair at a gap of 0.3. Measure it with a spring balance. Compare it with 16 N (12 x 2 and 12 x 2) and 22 N (12 x 5 and 12 x 2).
- The two lift springs lift the strip when the bolt is back.

## Pictures

The sheets are in `cad/out/panel-latch/sheets/`. Every BREP edge is drawn.

| Sheet | Content |
| --- | --- |
| `01-M-magnets-only.png` | M |
| `02-H-hooks-and-magnets.png` | H |
| `03-B-hooks-and-a-push-bolt.png` | B |
| `04-Q-hooks-and-two-quarter-turn-cams.png` | Q |
| `05-side-by-side.png` | The four candidates from the same camera |

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
cad/test.sh test_panel_latch                                                                 # 26 tests, 5 minutes
```

`CANDYBAR_LATCH=B,Q` builds only some candidates. `CANDYBAR_LATCH_SCENES=0` writes no scenes. The first command needs the skin of the shell in `cad/out/shell-rev7/split/cache`, as `panel_frame` does.

| Output | Content |
| --- | --- |
| `report.md`, `summary.json` | The results of the four candidates |
| `<candidate>/report.json` | Every row of the checks of one candidate |
| `<candidate>/parts/` | The printed parts as BREP and STL |
| `<candidate>/scenes/`, `<candidate>/renders/` | The models and the renders of its sheet |
| `scenes/compare-*`, `renders/compare-*` | The side-by-side views |

## Where this was built

The study was built and tested on the server pal9000 (OpenCascade 7.8.1). The laptop (OpenCascade 7.9.3) is the reference and must build it again before a merge.

- The default build of the shell does not complete on pal9000: it stops at the edge break of the hood. The study uses the parts and the cached skin that the laptop built (`cad/out/shell-rev7`). The outer form has not changed since then.
- The edge break of the button (B) and of the cam heads (Q) tries R 1 first and a smaller round if R 1 fails. On pal9000, R 1 worked on each part. If the laptop needs the smaller round, the face check reports the break faces, and the test `test_no_check_fails` fails.
- No other part of the code depends on the kernel.

## Assumptions

1. The magnet pulls are ESTIMATED from maker's data for two sizes. The gap, the pair and the use factors are estimates. Nothing is tested.
2. The strength of printed ABS is 35 MPa along the layers and 15 MPa across them (ESTIMATED).
3. The friction coefficient of ABS on ABS is 0.25 to 0.45. The study uses 0.3.
4. The springs are standard steel compression springs. The bolt spring is 4 outside, 24 free, about 1.2 N/mm. The lift springs are 6 outside, 28 free, about 0.57 N/mm. Measure the bought springs.
5. A fingertip goes 4.5 to 6 into a hole of 14.6 with a soft pad. The test piece must show it.
6. The hold method treats the plate as rigid. The plate bends a little under the lever (`control-panel.md`, "Deflection"). This moves load from the far restraints to the near ones, so the real factor can be lower than the calculated one.

## Open questions for the owner

1. Do you accept a flush button of 14 (12 wide) on the front face of the deck, at the centre line, 55 above the desk? If not, is Q (two flush heads on the top face) acceptable?
2. The button can be at the centre line or below one hand. Where do you want it?
3. With B, the front edge rises 7.7 when you push the button. Is that the way that you want to take the panel out, or do you prefer to lift it by the lever with no lift springs?
4. Must a blank panel be removable with no grip at all? B and Q give one. M and H do not.
5. Steel discs or magnets in each panel? Steel discs give no polarity to mind and about 10 % less pull.

## For the shared files

Glossary (`CONTEXT.md`):

- **Push bolt**: The printed bolt of latch B. It slides along the centre line under the front bar of the panel frame, and its front end is a flush button in the front face of the deck. _Avoid_: slider, catch.
- **Strike**: The part under the front edge of a control panel that the push bolt holds: two legs with a lip on each.
- **Rear hook**: One of the two hooks under the rear edge of a control panel. Its toe goes into a notch in the rear bar of the panel frame.
- Change **Latch point**: one of the four places where a magnet pair holds a control panel down on the panel frame.

Roadmap (`docs/roadmap.md`):

- Step 12: a study of a latch with no tool (`docs/design/control-panel-latch.md`). Four candidates are built. B is recommended. The default stays A.
- Open decision "The latch": the owner chooses from A (screws), B of the study (push bolt), and Q of the study (cams).
- "Waiting for the owner": a review of the sheets in `cad/out/panel-latch/sheets/`.

Hardware list (`docs/design/hardware-list.md`), for B:

- 2 disc magnets N52 12 x 2 for the frame, and 2 for each panel.
- 1 compression spring, steel, 4 outside, 24 free, about 1.2 N/mm.
- 2 compression springs, steel, 6 outside, 28 free, about 0.57 N/mm.
- 2 thread-forming screws 3.0 x 10.

The shell (`dims.py`, the deck nose of the split and the print pieces), for B: a hole in the deck nose for the button, at x 0, z 55.3. The hole is 14.6 across with two flats 12.6 apart. Its rim needs the edge break of R 1. The deck nose is the print piece "deck nose" (seams F1 and F2 at x 137, so the hole is not near a seam).

`cad/README.md`: the commands of "Build" in this document.

No value in `profiles.py`, `solids.py` or `cavity.py` changes. `panel_frame.py` does not change.
