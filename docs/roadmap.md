# Roadmap

Last update: 2026-11-11. Update this file at the end of each work session.

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
3. The outer form is built as 11 solids from the same profiles and dimensions that draw the blueprint (`cad/candybar/shell/solids.py`, output in `cad/out/shell-bp/`). `cad/tools/check_solids.py` compares the solids with the blueprint faces in three views and eleven section planes; all are within 0.5 mm. The owner must judge the form on the renders before more work. The solid code of the earlier form is removed (2026-11-11): `parts.py`, `hood.py`, `build.py`, `hood_sheet.py`, `hood_review.py`, `hood_overlay.py`, `section_sheet.py`, and the parts of `dims.py` that only they used (`HoodStations`, `hood_stations`, `OPTIONS`, `option`, `frame_for_sight`, `sight`, `EYE`, `EYE_LOW`). The older generator (`massing.py`, `cabinet.csv`, `panel.py`, `build.sh`) stays until step 4 replaces it.
4. Fit study: done on 2026-11-10. The shell has a skin of 4 mm (`cad/candybar/shell/cavity.py`) and the hardware is in it (`cad/candybar/shell/fit.py`). The checks pass: interference, keep-out zones, containment, the air path and the sight line. The results are in `docs/blueprint/index.md` ("Hardware in the shell") and on sheet 09. The shell does not change without the owner. Still to do in this step: put the shell into the generator in place of the outline shell (`massing.py`) and make its checks pass. The generator still has a rectangular control panel.
5. Revision 5 of the outer form, 2026-11-10, from the owner's review of the front and top views: the screen is 12 mm lower on the face, and the front edge of the control panel follows the front contour of the deck. The fit study passes with it.
6. Structure, mounting and seams: the study is done (2026-11-11) and the owner chose from it (see "Settled by the owner" and decision record 0006). Its text is a build output: `cad/out/shell-bp/split/proposal.md`. In work now: (a) the joint coupon as a printable part, in the clearances that the coupon test needs, for PETG and for ABS; (b) the chosen split as the one layout in the model, with the stiffer floor, the hand-holds at the back corners, the keyed hood, the bezel plate with no side ledges, and a fit check that also compares the air spaces of the parts with each other (the study found that the duct of the BC-250 and the fan space of the power supply overlap by 7.2 cm3, and the fit study did not see it). Done on 2026-11-11: the bezel plate has no side ledges, the fit study has rule R2b for the air zones and passes (the BC-250 stands 1 mm higher, the hub stands on the 7 mm floor), and the chosen split and the joints are in the blueprint (sheets 10 and 11). `cad/candybar/shell/joints.py` is the one source of the joint values. Then model the pieces with their flanges, keys and ribs.
7. Detail pass on the outer form: revision 6 is built (2026-11-11). The vertical corners of the back have one round of R 18 in plan, from the floor to the roof of the hood. The step of 12 mm limits the radius. The same pass put the floor on the table (a sandwich of 10 mm, so the power supply, the BC-250 and the hub stand 3 mm higher), made the door opening 426.7 x 182, moved the power supply 11 mm and the BC-250 15 mm toward the centre, put the make-up air inlet in the rear lower wall as a slot grille below the door, and placed the rear grips as data. The fit study passes. Open for the owner: the small questions on `cad/out/shell-bp/compare/detail-options.png` (the edge of the rail, the step, the legs of the hood, the corners of the hood opening, a smallest edge radius of 2 mm, the speaker grille).
8. Design the rear door with its vents, the hand-holds, and the shroud with its exhaust duct. From the fit study: the power supply needs a grille in the rear wall below the door, the cabinet needs an inlet for make-up air, and the door opening (447 x 186 mm) is wider than the bed, so the door has two parts or more.
9. Design the control panel frame, its latch, and the cut plates. Make the drawings for the cutting service.
10. Design the monitor cradle. From the fit study: clamps on the top edge and the bottom edge, 8 mm of adjustment each way, a cable channel on each side, and right-angle plugs (straight plugs do not fit: they are 15 to 19 mm too long at the sides).

Modelling and iteration run on Opus subagents. The main session writes the brief and reviews. The owner asked for a Fable agent on the hood; that agent now makes the blueprint.

The photo tools are in `cad/tools/`, their picked points in `cad/reference/`, and their results in `docs/research/photo-measurements.md`.

## Waiting for the owner

- [ ] Monitor: the outer case width, height and thickness of the present unit (UPERFECT 16 inch 3840 x 2400, confirmed by the owner on 2026-11-11). This is useful and not necessary: the mount is designed for a generic 16 inch 16:10 travel monitor.
- [x] Player eye position: not needed. The owner said on 2026-11-11 that the cabinet must work for the average person, children and other adults included. The sight line is checked for a child, a small adult and a tall adult from published data.
- [ ] BC-250 on the first console: board top face up to the outer face of the fan, with a ruler, to the nearest 2 mm. Low priority: this cabinet gets its own shroud, so the height of the stack is a design value.
- [ ] Lever and buttons when they arrive: the dimensions that `cad/out/report.md` lists.
- [ ] A review of revision 5: the screen position (`cad/out/shell-bp/compare/screen-drop-options.png` shows drops of 8, 12 and 16 mm; 12 is built) and the outline of the control panel.
- [ ] Answers to the open questions 1, 2, 3 and 5 in `docs/blueprint/index.md`. Question 2 matters most: the rail land beside the top corners of the bezel is 9 mm, and 16 mm lower down.
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
- The monitor is replaceable. The mount must take another 16 inch 16:10 travel monitor: plug space and a cable channel on both side edges, and a way to shim or adjust the body across and along the screen face so that the image is centred in the window (2026-11-11).
- The sight line must work for the average person, children and other adults included, not for the owner's eye position (2026-11-11).
- The bezel must stand clear of the tuck at its top corners. The screen is 12 mm lower on the face than in revision 4: the strip of face above the bezel is 32 mm and the band below it 40 mm (2026-11-10).
- The front edge of the control panel follows the front contour of the deck. It is not a rectangle (2026-11-10).
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
- Control panel tops are cut plates. The arcade panel is an aluminum plate with a clear polycarbonate cover and the art between them. A printed PETG plate comes first, for construction and proving at least (2026-11-11). The maker of the reference cabinet prints his plates in ABS and puts cut acrylic on top.
- The compute module has a fixed mount behind the rear door. The door is a cover with the vents and has no cable on it (2026-11-11, decision record 0005).
- The floor is a rigid printed PETG part with more infill. No plywood and no aluminum (2026-11-11).
- The shell is permanent. The owner does not disassemble it after it is built: it is filled, finished and painted. The pieces first lock together rigidly in the correct position, and are then fastened for good (2026-11-11). Thus a bonded seam does not show, and only the service seams stay visible: the rear door, the control panel, the bezel plate, and the hood if it must come off.
- The exterior has no acute, narrow or tight visible place that a person cannot reach to fill, sand and paint. The inside does not get the finish of the exterior (2026-11-11).
- The monitor comes out to the front for service, through the opening behind the bezel plate (2026-11-11). A gap of 1.3 mm each side for the monitor with its plugs is too small.
- The width stays 494.7. The owner examined +20 and +38 mm and kept the present width, because a bezel plate with no ledge at its sides gives the monitor 7.3 mm each side (2026-11-11). The cabinet does not become deeper, and it has sufficient height.
- No internal frame. The shell is a stressed skin with a printed floor (decision record 0006). The seams are those of option B with the hood of option A (2026-11-11).
- The hood has keys, so that it bolts on easily. The owner will look at both a bolted and a bonded hood (2026-11-11).
- The floor is stiffer than the 7 mm of the study, and it stands on the table: a sandwich of 10 mm, with thin non-slip pads that the owner sticks under it. No feet of 18 mm and no ribs under the floor (2026-11-11).
- Hand-holds: only at the rear, as pockets up into the overhang of the upper rear near each back corner. No grip at the front: the owner does not move the cabinet often (2026-11-11).
- The owner still considers ABS on an enclosed printer, for a simpler finish. The design stays correct for PETG and for ABS until the coupons decide (2026-11-11).
- PETG is satisfactory near the BC-250. The owner's first console has a PETG case and it does not soften. A fan in the exhaust duct, which pushes the hot air out, is an option to examine (2026-11-11).

## Where things are

| Path | Content |
| --- | --- |
| `docs/Arcade_Project_Current_Design_2026-11-09.md` | The project brief |
| `CONTEXT.md` | The glossary |
| `docs/adr/` | Decision records |
| `docs/blueprint/` | The blueprint of the target cabinet: volumes, elevations, sections, junctions, the face map, the face table, the hardware in the shell, the chosen split, the joints and the open questions |
| `docs/research/` | Research notes: reference cabinets, the measured Mini New Astro City model, measurements from the reference photos, hardware envelopes, controls and ergonomics, cooling and the power supply, the PC control panel and the USB sockets, the finishing of PETG (bond, filler, primer, paint, and a coupon test plan), and a study of a change to ABS with a budget for an enclosed printer (the owner examines this; the plan stays PETG until the owner decides) |
| `cad/reference/` | The picked points and known sizes for each reference photo, which the photo tools use |
| `cad/README.md` | How to build, check and view the model |
| `cad/params/` | All dimensions, with their status and source |
| `cad/out/report.md` | Check results and the list of dimensions to measure (a build output) |
| `cad/vendor/` | Reference photos and third-party CAD (not in git) |
