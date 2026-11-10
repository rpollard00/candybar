# Roadmap

Last update: 2026-11-10. Update this file at the end of each work session.

The goal is a cabinet that can be printed on the Bambu A1 and assembled, and that looks like the reference cabinet. `CONTEXT.md` defines the words. `docs/adr/` records the decisions that are hard to reverse.

## Phases

| Phase | Result | State |
| --- | --- | --- |
| 1. Layout study | Hardware envelopes, keep-out zones, two control panel tiles, layout checks | Done. All dimensions are sourced or provisional. |
| 2. Shell form | The massing has the proportions and the main forms of the reference | Rejected by the owner on 2026-11-10: the third pass does not read as a New Astro City. Its layout, its checks and its dimensions stay. Its outline shell goes. |
| 3. Shell rebuild | A shell that reads as a New Astro City: the cheek whose front edge is one long arc, facets on the cheeks, the deck and the hood, a framed bezel, a tilted hood band, a stepped rear body. The MakerWorld Mini New Astro City model is the form reference. | In work. Step 1: fit the reference to this hardware as a target, in three variants, with a render harness. Step 2: model solids against the chosen target and iterate on renders. |
| 4. Printable modules | The shell divided into parts for the 256 mm bed, with joints, inserts and ribs. Monitor cradle, compute module mount, power supply mount, control panel latch, bezel plate mount. | Not started |
| 5. Print checks | Each part sliced for the A1. Fit coupons for inserts, joints and button holes. | Not started |
| 6. Dry assembly and finish | As in the project brief, sections 4 and 5 | Not started |

## Next steps

1. The blueprint is in `docs/blueprint/` (seven sheets and `index.md`), made on 2026-11-10. The drawings of the references are in `cad/out/shell-d/reconstruction/`.
2. The owner reviewed the first blueprint on 2026-11-10 and found it too simple: it has straight lines where the real cabinet has curves. The body must lean and bow inward into the hood as one curve, with a bevel cut at the seam. The side profile must be a convex arc that follows the contour of a CRT. Revision 2 of the blueprint added the curves. The owner then chose their strengths, and revision 3 holds them: a rail arc of 0.035 of its chord, a tuck of 0.023 W toward the hood over the top third of the body, a hood with near-straight sides and tight top corners (0.07 W), and a screen 14 to 20 mm below the rail land. Questions 1 to 7 in `docs/blueprint/index.md` are open; the blueprint draws a default for each.
3. The outer form is built as 11 solids from the same profiles and dimensions that draw the blueprint (`cad/candybar/shell/solids.py`, output in `cad/out/shell-bp/`). `cad/tools/check_solids.py` compares the solids with the blueprint faces in three views and eleven section planes; all are within 0.5 mm. The owner must judge the form on the renders before more work. When the owner accepts it, remove the solid code of the earlier form: `parts.py`, `hood.py`, `build.py`, `hood_sheet.py`, `hood_review.py`, `hood_overlay.py`, `section_sheet.py`, and the parts of `dims.py` that only they use.
4. Make the outer form hollow, put it into the generator in place of the outline shell, and make the checks pass.
5. Do a detail pass on the outer form. The owner asked on 2026-11-10 for a fillet on the vertical corners of the back surface, of the body and of the hood.
6. Design the rear door with its vents, the hand-holds, and the shroud with its exhaust duct.
7. Design the control panel frame, its latch, and the cut plates. Make the drawings for the cutting service.

Modelling and iteration run on Opus subagents. The main session writes the brief and reviews. The owner asked for a Fable agent on the hood; that agent now makes the blueprint.

The photo tools are in `cad/tools/`, their picked points in `cad/reference/`, and their results in `docs/research/photo-measurements.md`.

## Waiting for the owner

- [ ] Monitor: body width, height and thickness. Is it the flat model with no stand? Heights of the three ports on the left edge. Plug length with the bend, for the real cables.
- [ ] Player, seated as for play: eye height above the desk, and eye position in front of the cabinet front edge. This is the most important measurement now: it decides how high the screen must sit, and so the proportion of the bezel.
- [ ] BC-250 on the first console: how far the fan face is above the board, and where the shroud sits along the board. On the second board: the width and height of the fin block.
- [ ] Lever and buttons when they arrive: the dimensions that `cad/out/report.md` lists.
- [ ] A review of the revised blueprint in `docs/blueprint/` after the curvature pass: are the big volumes and their curves right, are the faces on the face map read correctly, and answers to the open questions in `index.md`.
- [ ] A photo of the reference cabinet from the side, if one exists.

`cad/out/report.md` has the full list of dimensions to measure, with instructions.

## Open decisions

| Decision | Options | Depends on |
| --- | --- | --- |
| Fan shroud details | The air space between the fan and the fins (10 mm is the plan), the seal to the rear door, and the hood that turns the hot air to the door vents | A test print on the board |
| What the apron carries | Nothing. Or the start, coin and menu buttons, which lets the control panel be less deep. | Owner |
| Button nuts | Seimitsu nuts, snap-in buttons, or a layout spread by half a millimeter. Three pairs of Sanwa screw nuts overlap by 0.15 to 0.28 mm. | Owner |
| Marquee and speakers | No hardware is chosen. The hood band has provisional openings. | Owner |
| One encoder for each control panel | Research recommends it: one USB cable is then the only connection of a panel. | Owner |
| The arcade plate stack | Research gives: 2.0 mm aluminum under a 1.5 mm clear cover (3.5 mm in total, inside the 3.9 mm limit of Sanwa snap-in buttons), or 3.2 mm aluminum with no cover. The owner wants the cover with art. Open: confirm 2.0 + 1.5 and snap-in buttons. | Owner |
| The keyboard | 60%, built into the PC control panel by the owner. Research gives: a 1.6 mm aluminum switch plate, 14 mm clear below it, key tops 13 to 16 mm above it. Open: a bought hot-swap PCB (GH60 form) or hand wiring, a small switch plate or a full-panel plate, and a touchpad beside it or none. | Owner |
| Front USB hardware | Research gives: screw-flange sockets on short cables in a removable printed socket plate, and a hub with its own 5 V supply from a SATA lead, because the 5 V of the BC-250 is weak. The flange screws are visible. Open: the hub model, and USB 2 or USB 3 at the sockets. | Owner |

## Variant D of the shell, as the owner set it

- The size of target variant B (about 466 x 571 x 555 mm), with the hood proportion of variants A and C.
- The reference cabinet in the photos leads the look. The MakerWorld model gives measured curves where the photos give none.
- Deeper cheeks, with the wide facet on the front edge.
- A cheek curve that is more subtle than on the MakerWorld model, and that runs smoothly all the way into the deck.
- No holes in the front face of the deck.
- A deck with the additional faces of the reference cabinet. Seen from above, the front is three faces: a center face that is square to the player and about half the width, and a face on each side of it that turns slightly outward. The turn is very subtle. (An earlier reading, flat faces that cut the corners at 45 degrees, was wrong.)
- Measured from the photos (see `docs/research/photo-measurements.md`): the center face is 0.56 of the deck width; each flank turns back about 8 degrees; the corner radius is about 0.09 of the deck width; the crease on the front is one third of the way down, with the leaning band about one fifth of the front. The model has these values since round 11.
- A visible cut between the top of the bezel and the hood.
- A shorter deck. The control panel becomes about 396 x 175 mm (it was 396 x 240). The start, coin and menu buttons move from a row behind the main buttons to the right end of the panel, as on the reference cabinet. The deck is then about 195 to 215 mm from its front edge to the foot of the screen face.
- The screen face: a bezel in the proportion of the 16:10 screen with an even frame of about 45 mm, on a body-colored band of about 60 mm, with a recline of about 30 degrees. The owner accepts a steeper sight line for this (about 36 degrees with the estimated eye position).
- The bezel is about flush with the rails, and the screen is inset in the bezel. The rails read as broad members with a wide facet.
- The front surface is continuous: the deck top, one concave bend, the screen face, and then the hood. The facet on the outside runs without a break from the front of the deck to the top of the hood.
- The front edge of the deck, from the top down: the flat border, a soft radius that turns almost a right angle (about 80 degrees), then about a quarter of the front face that leans slightly forward, and then a vertical front face. Nothing on the deck reads as a 45 degree bevel. The wide facet of the rail is a different band: it runs from the hood to the table.

## Settled by the owner

- The look follows the reference cabinet. Practical choices belong to this project (decision record 0002).
- Eight action buttons.
- The cabinet must fit on a normal surface. Do not make the hood deeper unless the whole cabinet becomes deeper, and the owner does not want a deeper cabinet (2026-11-10).
- The image is centered in the bezel. The owner first asked for a sight line of 15 to 25 degrees, and then chose a 16:10 bezel with more recline, which gives a steeper sight line.
- Bezel plates are swappable: 16:9, 16:10, 4:3 and vertical.
- Control panels are swappable. A control panel for PC games is wanted beside the arcade one. It holds a keyboard, and a mouse area if there is room.
- Four USB ports that the player can reach, for controllers: two USB-C and two USB-A, in the right side face of the deck toward the front, out of view. They go through a hub inside the cabinet.
- The PC control panel has a 60% keyboard that the owner builds.
- This is a personal project. The reference cabinet is the inspiration, and this design goes its own way.
- The speaker fronts follow the contour of the hood.
- Power supply: EVGA SuperNOVA 1000 P5, fully modular, 150 mm deep.
- Fan: ARCTIC P12 Pro on the BC-250 heatsink. The fin tops are opened under the fan, as on the first console. The shroud is a design for this cabinet: the fan blows down into the fins and the air leaves at the I/O end.
- All vents are in the rear door, as on the reference: the fan vent in the middle and slot vents for the hot air at the I/O end. The side panels have no vents.
- Control panel tops are cut plates. The arcade panel is an aluminum plate with a clear polycarbonate cover and the art between them.

## Where things are

| Path | Content |
| --- | --- |
| `docs/Arcade_Project_Current_Design_2026-11-09.md` | The project brief |
| `CONTEXT.md` | The glossary |
| `docs/adr/` | Decision records |
| `docs/blueprint/` | The blueprint of the target cabinet: volumes, elevations, sections, junctions, the face map, the face table and the open questions |
| `docs/research/` | Research notes: reference cabinets, the measured Mini New Astro City model, measurements from the reference photos, hardware envelopes, controls and ergonomics, cooling and the power supply, the PC control panel and the USB sockets |
| `cad/reference/` | The picked points and known sizes for each reference photo, which the photo tools use |
| `cad/README.md` | How to build, check and view the model |
| `cad/params/` | All dimensions, with their status and source |
| `cad/out/report.md` | Check results and the list of dimensions to measure (a build output) |
| `cad/vendor/` | Reference photos and third-party CAD (not in git) |
