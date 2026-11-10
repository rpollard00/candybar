# Blueprint of the cabinet

Date: 2026-11-10. Status: a proposal for the owner's review. It is not built yet.

This directory holds the target form of the cabinet as drawings: the big volumes first, then elevations, sections, the hood, the two junctions, and a map of every face. The drawings come from data. `cad/candybar/shell/dims.py` (class `Blueprint`) holds the named dimensions. `cad/candybar/shell/profiles.py` turns them into profiles and labelled faces. `cad/tools/draw_blueprint.py` draws the sheets from the profiles. The solids are to be built from the same profiles after the review, so the drawing and the model cannot drift apart. `parts.py`, `hood.py` and `build.py` still build the earlier form.

Words are those of `CONTEXT.md`. New words are in the section "Words". `W` is the body width: 494.7 mm.

## Sheets

Each sheet is an SVG file and a PNG file with the same name.

| Sheet | Content |
| --- | --- |
| `01-volumes` | The cabinet as four blocks (deck, front body, rear body, hood) from the front, the side and above, with the monitor, the power supply and the BC-250 module inside, and the proportion table |
| `02-elevations` | Front, right side, top and rear elevations, one scale, with dimensions |
| `03-side-section` | The side section at the center line, and the edge section that the deck and the rail share |
| `04-plan-sections` | Four horizontal sections through the right side: a hood leg, the rail at mid screen, the rail's foot in the sweep, the deck's side |
| `05-hood` | The hood: front elevation and two side sections |
| `06-junctions` | Hood to body and body to deck, large, from the side, the front and above |
| `07-face-map` | Every face in a flat false color with its ID |

Drawings of the references are third-party material. They are in `cad/out/shell-d/reconstruction/` (ignored by git):

| File | Content |
| --- | --- |
| `k-01-elevations.png` | The 3D reference model: four elevations, exact |
| `k-02-face-map.png` | The 3D reference model: face map with the same IDs |
| `k-03-sections.png`, `k-04-rail-sections.png` | The 3D reference model: side section and horizontal sections (exact slices) |
| `k-05-hood.png` | The 3D reference model: the hood |
| `m-faces-hood.png`, `m-faces-body.png` | The maker's mini: the face IDs on the photo, each reading marked estimated or uncertain |
| `r-faces.png` | The real New Astro City: the face IDs on the photo |
| `../sheet-side-profile.png` | Side profiles and hood outlines of the references and of the target, over each other |

## Proportions of the big volumes

`measured` is a value from the photo tools (`docs/research/photo-measurements.md`). `estimated` is a reading by eye or a trace with an assumed camera. The 3D reference model is exact.

<!-- proportions:begin -->
| Ratio to the body width W | 3D reference model (exact) | Maker's mini (photos) | Real New Astro City | This cabinet | Why it differs |
| --- | --- | --- | --- | --- | --- |
| Body width W, mm | 270.0 | 246.9 +-2.4 (measured) | 750 (published) | 494.7 | 16-inch 16:10 monitor (354 wide) with its cradle, between two rails |
| Deck width / W | 1.000 | 1.02 +-0.03 (measured) | about 1.0 | 1.000 | same: the deck's side is flush with the side band |
| Depth / W | 1.252 | about 1.3 (estimated) | 1.207 (published) | 1.172 | 540 at the desk holds the power supply and the BC-250; the upper rear is 40 proud for the hood |
| Height / W | 1.172 | about 1.25 (estimated) | 1.927 (floor cabinet) | 1.177 | a 16:10 screen is lower than 4:3 at the same width |
| Deck top above the desk / W | 0.185 | about 0.2 (estimated) | not comparable | 0.146 | 70 mm panel height for the hands; 58 inside is enough for the lever |
| Deck front to screen foot / W | 0.380 | about 0.42 (estimated) | 0.49 (estimated) | 0.477 | 396 x 175 control panel with its border |
| Recline of the screen face, deg | 32.5 | about 30 (estimated) | 26 (estimated) | 30 | owner's choice for the 16:10 bezel |
| Seam (body top) above the desk / W | 0.916 | 0.88 (estimated) | not comparable | 0.857 | follows from the bezel: 215 image + 2 x 45 frame + 60 apron |
| Hood height over the seam / W | 0.256 | 0.33 (0.35 to bezel top) | 0.25 to 0.33 (0.36 to bezel top) | 0.320 | 0.341 to the bezel top, inside 0.33 to 0.35 |
| Hood depth at the seam / W | 0.335 | 0.28 (estimated) | 0.30 (estimated) | 0.269 | was 0.188 in the built model; needs the upper rear 40 proud |
| Bezel width / W | 0.885 | 0.858 +-0.016 (measured) | about 0.79 | 0.879 | 344.7 image + 2 x 45 frame |
| Rail land / W | 0.016 | 0.05 +-0.015 (estimated) | not read | 0.032 | what the bezel leaves, less the edge section |
| Rail edge, in x back / W | 0.039 x 0.039 (45 deg facet) | 0.03 x 0.12 (band 10 to 18 deg) | not read | 0.026 x 0.049 | the deck's own edge section (10 deg band), so the edge follows through |
| Side band depth at the desk / W | 0.277 | 0.27 (estimated) | not read | 0.279 | follows both references; the built model has 0.35 |
| Rear body narrower, each side / W | 0.074 | 0.01 to 0.03 (uncertain) | not read | 0.024 | equal to the hood's shoulder: the hood's side stands over the rear body's side |
| Hood foot width / W | 0.990 | 0.94 to 0.96 (measured) | 0.94 to 1.0 (estimated) | 0.951 | shoulder 12 each side |
| Hood top flat / W | 0.713 | 0.66 (estimated) | not read | 0.64 | the widest blend that keeps a straight marquee window of 320 |
<!-- proportions:end -->

## What the reconstruction found

### Body to deck

The three references agree on how the side is made. The current model does not have it.

- **The band that carries the stripe is the side face.** On the 3D reference model the cheek is a slab 15 thick. Its front is a land 4.4 wide, then a 45 degree facet 10.6 wide, then a vertical face in the side plane, 75 to 78 deep. This document calls that face the side band. On the maker's mini the stripe is on the same face: its foot line on the floor is straight and continues the foot lines of the deck's side and of the rear body's side, so it is vertical and faces sideways. On the real cabinet the stripe is on the flat side panel.
- **The deck's side is flush with the side band.** On the 3D reference model both are in the plane x = W / 2, from the deck's front corner back to the step. On the maker's mini the deck is 1.02 ± 0.03 of the body width (measured), and the floor line passes the seam between deck and body without a jog (estimated: flush within 3 mm).
- **A narrow edge follows through, not a wide facet.** Between the land and the side band the 3D reference model has the 45 degree facet (0.039 W). The same facet is on the top edge of the deck, so one facet runs from the hood down the cheek, round a small fillet at the cheek's foot, and along the deck to its front. The maker's mini has a soft radius there (about 0.015 W, estimated). Its land sweeps forward into the deck top, and the soft edge follows the sweep into the top edge of the deck's side.
- **Behind the side band there is a step.** It leans 28 degrees on the 3D reference model (28.2, exact) and on the maker's mini (27.8, estimated). Its foot is 0.28 W behind the deck on the model and 0.27 W on the mini. It is 20 mm deep on the model (0.074 W). Its depth on the mini is uncertain (0.01 to 0.03 W).
- **The bezel** is 20 to 31 mm behind the land on the 3D reference model (the cheek has an inner wall, RL5). On the maker's mini it is about flush (2 mm or less, estimated). The target keeps flush, as the owner set it.

Where this contradicts the current model and earlier briefs:

1. The current model has a wide facet (17 in, 29.5 back, leaning 30 degrees from the side face) as one plane from the hood to the table. No reference has it. The hypothesis in the brief of 2026-11-10 is correct: the stripe band is the cheek's outer side face.
2. The current deck's side is inset from the foot of that facet. On the references it is flush.
3. The current step line starts 173 mm behind the deck (0.35 W). The references have 0.27 to 0.28 W.
4. `docs/research/photo-measurements.md` section C says that the facet runs to the table in its own plane and that the deck sits in front of it. The first part holds when "facet" is read as the side band. The second part does not hold: the deck is flush.
5. Not resolved: on the maker's mini the rail shows a radius only, and the deck shows a radius and a leaning band. The photos do not show how the two meet at the sweep. See question 1.

The target: the rail is a land (16.0), then the deck's own edge section turned on its side (a radius of 10.5 that turns 80 degrees, a band that leans 10 degrees, a crease 24 behind the land), then the side band. The same section runs down the screen face, round the sweep and along the deck, so the edges line up by construction. The side band and the deck's side are one plane. The step is 138 behind the deck at the desk (0.28 W) and 12 deep.

### Hood to body

- **3D reference model.** The body top is flat. The hood stands on it and is 1.4 mm narrower on each side. Its legs continue the cheek: their fronts lean 37 to 43 degrees, and the cheek's facet runs on up the leg. There is no sill: the hood band (44 degrees) starts at the seam, on the line of the screen face. The rear of the hood leans forward 16 degrees and continues the upper rear wall.
- **Maker's mini.** The hood is a cap on a flat body top. A shoulder shows at the sides (0.03 W, measured). The front of the cap is near upright, so the plane changes at the seam. The legs are thin from the front (0.03 W, measured) and turn into the hood's side with a soft corner. A white zone 0.088 W high (measured) lies between the hood band and the bezel. It holds the ledge, the sill and the brow band of the body. The seam is not visible on the front in the photos (uncertain). From the side the hood is upright in front and one long arc from the top down the rear to the seam (estimated trace). Its depth is 0.28 W, the same as the body top.
- **Real cabinet.** A cap on a shoulder. The hood is 0.30 W deep (estimated from the manual drawing).

Where this contradicts the current model: the current hood is 0.19 W deep on a body top 101 mm deep. Its rear is an upright wall with a 20 mm radius. Both references that show the side have a deeper hood whose top runs down the rear in one arc.

The target: the upper rear of the body stands 40 mm proud of the lower rear wall, so the body top is 141 deep (0.285 W) and the hood 133 (0.269 W). The cabinet is 580 deep (it was 540). The front of the cap is upright, 4 mm behind the front edge of the body top. Each leg stands over the land and the edge of the rail, with a shoulder of 12 mm at the side. The rear body is narrower than the side band by the same 12 mm, so the side of the hood stands over the side of the rear body.

### The hood

- **Outline from the front.** The 3D reference model has sides on one arc that lean 13.5 to 22 degrees, a corner radius of 0.074 W and a top flat of 0.713 W. The maker's mini has sides that lean about 6 degrees at the foot, and then one long blend over the upper half into a top flat of about 0.66 W (estimated from the picks in `cad/reference/photo-b.json`). A single radius does not describe it: the owner is right. The target follows the maker's mini: an arc of radius 1.3 W that leans 7 degrees at the foot, a conic blend from 0.45 of the height, and a top flat of 0.64 W. This is the widest blend that keeps a straight marquee window of 320 mm.
- **Bottom front corners.** On the maker's mini the legs come down near upright to a foot 0.94 to 0.96 W wide, and the bottom corners of the opening are near square. The target has a foot of 0.951 W and corners of radius 6. The current model has legs that lean 10 degrees and corners of radius 8.
- **Side profile.** Upright front, a soft top front edge (a quarter ellipse, 16 down and 32 back), a roof 6 mm long, then one arc 95 deep and 110 high down to an upright rear wall.
- **Inside the arch**, as before: the marquee under the top bar (window 322 x 34, 10 modules of 32 mm), a lip, the hood band with two speaker forms and the logo form, and the ledge on the sill. The deeper hood lets the band lean back 24 degrees (it was 16) with 67 mm clear behind it.

## Words

New words in this blueprint. They are not in `CONTEXT.md` yet.

| Word | Meaning |
| --- | --- |
| Front body | The part of the body with the screen face and the rails, back to the step |
| Rear body | The narrower part of the body behind the step |
| Rail | The member beside the bezel, from the hood seam to the deck: land, edge and side band. It is the cheek of `CONTEXT.md` when the bezel is flush. |
| Land | The front face of the rail, beside the bezel |
| Edge section | The section of a top or front edge: a radius, then a band that leans, then a crease |
| Side band | The face of the rail in the side plane, between the edge and the step. It carries the stripe. |
| Step | The face that turns in from the side band to the rear body |
| Body top | The flat top of the body under the hood. The shoulder is the bare strip of it round the foot of the hood. |
| Brow band | The strip of screen face above the bezel |
| Cap | The outer piece of the hood |
| Top bar, leg, sill | The members of the cap round its opening |
| Soft edge | The rounded edge round the front of the cap |
| Side blend | The surface where the side of the cap turns into its roof |
| Rear arc | The surface where the roof of the cap turns down to its rear wall |
| Soffit | The underside of the top bar |
| Ledge | The top of the sill, in front of the hood band |
| Marquee lip | The small bar between the marquee and the hood band (earlier notes call it the rail of the hood) |
| Speaker form, logo form | The raised forms on the hood band |
| Logo plate | The plate for printed art in the logo form |
| Marquee cover, marquee window | The tinted cover under the top bar, and the straight window in it for the display |

One change of meaning against `CONTEXT.md`: the marquee is the lit strip under the top bar. The glossary puts it in the middle of the hood band.

## Faces

The IDs are stable. A face of a reference that corresponds has the same ID.

<!-- faces:begin -->
| ID | Name | Component | Which way it faces | What sets it | Joins |
| --- | --- | --- | --- | --- | --- |
| DK1 | deck top border | deck | faces up | deck_top 72; flat border 12 or more in front of the panel | CP1, DK2, FB1, RL1 |
| DK2 | deck edge radius | deck | turns from up to 10 deg off vertical | deck_top_r 10.5, turning 80 deg | DK1, DK3 |
| DK3 | deck edge band | deck | leans 10 deg from vertical, faces out | deck_lean 10, crease deck_lean_h 24 below the top | DK2, DK4 to DK7 at the crease |
| DK4 | deck front, centre face | deck | faces the player, vertical | deck_centre_frac 0.56 of the width | DK3, DK5 |
| DK5 | deck front, flank | deck | vertical, turned back 8 deg | deck_flank 8 | DK4, DK6 |
| DK6 | deck front corner | deck | vertical, round in plan | deck_corner_frac 0.09 of the width (R 44.5) | DK5, DK7 |
| DK7 | deck side | deck | faces sideways, vertical | at the full width; flush with RL4 | DK6, RL4 (same plane) |
| CP1 | control panel | control panel | faces up | 396 x 175, 2 below the deck top | DK1 |
| FB1 | sweep | front body | concave, from up to the screen face | bend_r 50 | DK1, FB2, RL1 |
| FB2 | apron | front body | faces the player, reclined 30 deg | band_len 60 | FB1, BZ1, RL1 |
| FB3 | brow band | front body | faces the player, reclined 30 deg | brow_ledge 12 | BZ1, FB4, RL1 |
| FB4 | body top (shoulder) | front body | faces up | body_top 423.9; bare strip round the hood foot | FB3, RL1 to RL4, RB5, hood foot |
| RL1 | rail land | rail | faces the player, reclined 30 deg; follows the sweep | rail_land 16.0 | BZ1, FB1 to FB3, RL2, DK1 |
| RL2 | rail edge radius | rail | turns from the land to 10 deg off the side | same section as DK2 | RL1, RL3, DK2 |
| RL3 | rail edge band | rail | leans 10 deg from the side plane | same section as DK3: 13.0 in, crease 24 behind the land | RL2, RL4 at the crease, DK3 |
| RL4 | side band | rail | faces sideways, vertical | at the full width, 138 deep at the desk; carries the stripe | RL3, DK7 (same plane), RB2, FB4 |
| BZ1 | bezel face | bezel | faces the player, reclined 30 deg | 434.7 x 305.4, 2 behind the land | RL1, FB2, FB3, BZ2 |
| BZ2 | bezel step | bezel | faces the player, reclined 30 deg | 10 wide, 8 deeper | BZ1, SC1 |
| BZ3 | bezel step walls | bezel | face the centre of the screen | 8 deep each | BZ1, BZ2, SC1 |
| SC1 | screen | bezel | faces the player, reclined 30 deg | 344.7 x 215.4, 18 behind the land | BZ3 |
| RB1 | rear body side | rear body | faces sideways, vertical | rear_w 470.7: in by the hood's shoulder, so the hood's side stands over it | RB2, RB3 to RB5 |
| RB2 | step | rear body | faces out and back, 45 deg in plan, leans 28 deg | foot 138 behind the deck (0.28 W); 12 deep | RL4, RB1 |
| RB3 | lower rear wall | rear body | faces the rear, vertical | body_d 540 | RB1, RB2, RB4, RB6 |
| RB4 | rear slope | rear body | faces the rear and down, 45 deg | z 310 to 350 | RB3, RB5 |
| RB5 | upper rear wall | rear body | faces the rear, vertical | rear_proud 40 behind the lower wall | RB4, FB4 |
| RB6 | rear door | rear body | faces the rear, vertical | 368 x 188 | RB3 |
| FL1 | underside | floor | faces down | on the desk (feet not designed) | DK4 to DK7, RL4, RB1 to RB3 |
| HC1 | hood leg, front face | hood cap | faces the player, upright | hood_bar 21 less the soft edge; leans in with the side | HC4, HC11, HC3 |
| HC2 | hood top bar, front face | hood cap | faces the player, upright | hood_bar 21 less the soft edge | HC4, HC10 |
| HC3 | hood sill, front face | hood cap | faces the player, upright | hood_sill_h 17 | HC1, HC12 |
| HC4 | hood soft edge | hood cap | turns from the front to the side and the roof | quarter ellipse 16 in, 32 back | HC1, HC2, HC5 to HC7 |
| HC5 | hood side | hood cap | faces sideways, leans in 7 to 15 deg on one arc | arc R 1.3 W from the foot | HC4, HC6, HC9, FB4 |
| HC6 | hood side blend | hood cap | turns from the side to the roof | conic from 0.45 of the height to the top flat | HC5, HC7 |
| HC7 | hood roof | hood cap | faces up | top flat 0.64 W wide | HC4, HC6, HC8 |
| HC8 | hood rear arc | hood cap | turns from the roof to the rear | conic 95 deep, 110 high | HC7, HC9 |
| HC9 | hood rear wall | hood cap | faces the rear, upright | 4 in from the upper rear wall | HC8, HC5, FB4 |
| HC10 | hood soffit | hood cap | faces down | under the top bar, back to the marquee | HC2, MQ1 |
| HC11 | hood leg, inner wall | hood cap | faces the centre line | from the front plane back to the band | HC1, HB1, MQ1 |
| HC12 | hood ledge | hood cap | faces up | hood_ledge 14 | HC3, HB1 |
| HC13 | marquee lip | hood cap | faces the player | 6 high, 5 proud | MQ1, HB1 |
| MQ1 | marquee cover | marquee | faces down 18 deg toward the player | ends follow the blend of the opening | HC10, HC11, HC13, MQ2 |
| MQ2 | marquee window | marquee | faces down 18 deg toward the player | straight, 34 high | MQ1 |
| HB1 | hood band | hood band | leans back 24 deg | foot on the ledge | HC12, HC11, HC13, SP1, LG1 |
| SP1 | speaker form | hood band | parallel to the band | 13 proud; outer end parallel to the leg | HB1, SP2 |
| SP2 | speaker grille | hood band | parallel to the band | set 1.5 into the form | SP1 |
| SP3 | speaker form walls | hood band | square to the band | 13 high, top edge R 4 | SP1, HB1 |
| LG1 | logo form | hood band | parallel to the band | 5 proud | HB1, LG2 |
| LG2 | logo plate | hood band | parallel to the band | 166 wide | LG1 |
| LG3 | logo form walls | hood band | square to the band | 5 high | LG1, HB1 |
<!-- faces:end -->

### The same faces on the references

Only the faces that differ are listed. "Followed" names the reference that the target follows.

| ID | 3D reference model (exact) | Maker's mini (photos) | Real New Astro City | Followed |
| --- | --- | --- | --- | --- |
| DK2, DK3 | No radius. One 45 degree facet, 10.6 x 10.6 (0.039 W). | Radius over 0.11 to 0.13 of the front height, band over 0.20, crease at 0.33 (measured) | Soft edge (estimated) | Maker's mini |
| DK4, DK5, DK6 | Center flat 0.397 W, flanks swept 3.3 degrees, corner radius 0.111 W | Center 0.56 of the width, flanks 8 degrees, corner 0.09 (measured) | Not read | Maker's mini |
| DK7, RL4 | One plane, exact | One plane within 3 mm (estimated) | One plane (estimated) | All |
| RL1 | 4.4 wide (0.016 W) | About 0.05 W (estimated) | Broad (estimated) | Own value: 16.0 (0.032 W), from the bezel |
| RL2, RL3 | No radius. A 45 degree facet 10.6 wide (0.039 W). | A soft radius, about 0.015 W. A band is not visible (uncertain). | A large soft edge (estimated) | Own: the deck's edge section. See question 1. |
| RL5 (inner wall of the cheek) | 20 to 31 deep | None: the bezel is about flush | Deep (CRT) | Maker's mini: no such face |
| FB1 | Fillet R 3.9 | A sweep (estimated) | A large sweep | Own value: R 50 |
| FB2 | A 43.5 degree facet, 18.4 on the slope | A white band under the bezel (estimated) | None | Own value: 60, set by the owner |
| RB2 | 20 deep (0.074 W), 28.2 degrees | Depth 0.01 to 0.03 W (uncertain), 27.8 degrees | Not visible (uncertain) | Angle and position: both. Depth: own, 12. See question 3. |
| RB4, RB5 | The upper rear leans forward 11.6 degrees and is as wide as the cheeks | The upper rear stands proud of the lower rear (estimated) | Not read | Maker's mini in kind |
| RB8 (rear lower facet) | 43 degrees, 30.6 deep, 28.8 high | Present (estimated) | Not comparable | Left out: the power supply stands there |
| FB4 | Shoulder 1.4 (0.005 W) | Shoulder 0.030 ± 0.012 W (measured) | 0 to 0.03 W (estimated) | Maker's mini: 12 (0.024 W) |
| HC1 | Leans 37 to 43 degrees, continues the cheek | Near upright, 0.03 W wide (measured) | Near upright (estimated) | Maker's mini |
| HC2, HC4 | Top bar 15 thick (0.056 W). The top front edge is a 42 degree facet. | Top bar 0.037 W (measured), one soft edge | The lit strip fills the brow | Maker's mini in kind; 21 thick (0.042 W) |
| HC3, HC12 | None: the band starts at the seam | Ledge zone 0.088 W (measured) | Ledge zone 0.06 W (measured) | Maker's mini |
| HC5, HC6 | Arc R 1.29 W, 13.5 to 22 degrees; corner R 0.074 W | About 6 degrees, then one long blend (estimated) | A long blend (estimated) | Maker's mini |
| HC7, HC8, HC9 | Top flat 30 deep; rear leans forward 16 degrees | Almost no flat; one arc down the rear (estimated) | Not read | Maker's mini |
| HC13 | None | A white zone 0.043 W under the strip (uncertain: lip or top of the band) | A dip of 0.02 W | Own: a lip 6 high |
| MQ1, MQ2 | An upright strip 12.4 high (0.046 W), 15.9 behind the nose of the top bar | 0.049 W high, under the top bar, tilted down (estimated) | 0.16 W with the brow | Own: 34 high for the display, faces down 18 degrees |
| HB1 | Leans 44 degrees | Leans less (estimated) | Not read | Own: 24 degrees, which keeps 50 mm behind it |
| SP1 to SP3 | Pods 0.204 x 0.147 W, fronts upright | Pods 0.176 x 0.163 W, fronts upright, 0.12 W deep | Pods 0.19 x 0.145 W at the ends | Owner's rule: forms 13 proud, faces parallel to the band |
| LG2 | Recess 0.260 x 0.187 W | 0.369 x 0.133 W (measured) | About 0.30 x 0.125 W | Maker's mini: 0.34 x 0.10 W |

Uncertain readings, all on the maker's mini: the edge of the rail (RL2, RL3), the depth of the step (RB2), the seam on the front of the hood (HC3, FB3), the white zone under the lit strip (HC13 or HB1), the surface beside the right pod (SP3 or HB1), and the rear wall in the side trace.

## Open questions for the owner

1. **Edge of the rail.** The blueprint runs the deck's whole edge section (radius, 10 degree band, crease 24 mm behind the land) up the rail to the hood. The maker's mini shows only a soft radius on the rail (about 8 mm at this size). Whole section, or radius only?
2. **Land of the rail.** It is 16 mm (0.03 W). The maker's mini has about 0.05 W (25 mm at this size). Keep 16, or widen the cabinet by about 18 mm?
3. **The crease behind the stripe.** The blueprint makes it a step 12 mm deep, equal to the shoulder of the hood. The 3D reference model has 20 mm. The maker's mini reads shallower. 12, deeper, or only a shallow line?
4. **Depth.** The hood is 133 mm deep (0.27 W) and the cabinet 580. The maker's mini has 0.28 W, the real cabinet 0.30 W, the 3D reference model 0.335 W. Enough, or deeper (0.30 W gives a cabinet of 595)?
5. **Legs and top bar of the hood.** They are 21 mm (0.042 W). Thicker legs cost marquee width: 30 mm legs give a window of 304 mm, 9 modules. Keep 21?
6. **Marquee.** It sits 38 mm under the top bar and faces down 18 degrees. A seated player sees all of it. A standing person does not see its top. Accept?
7. **Rear.** The rear lower facet and the rear corner facets of the references are left out. Accept for now?

## How to draw the sheets again

```sh
cad/.venv-tools/bin/python cad/tools/draw_blueprint.py target      # docs/blueprint, and the two tables in this file
cad/.venv-tools/bin/python cad/tools/draw_blueprint.py reference   # the 3D reference model, to cad/out
cad/.venv-tools/bin/python cad/tools/draw_blueprint.py photos      # the face IDs on the photos, to cad/out
cad/.venv-tools/bin/python cad/tools/draw_blueprint.py compare     # side profiles over each other, to cad/out
```

`reference` needs the slices of the model: run `candybar.shell.reconstruct_slices` with `cad/candybar/freecad-run.sh` (the example is at the top of that file). `photos` reads the picks in `cad/out/shell-d/reconstruction/face-picks.json`.
