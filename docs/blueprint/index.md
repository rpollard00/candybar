# Blueprint of the cabinet

Date: 2026-11-10. Status: a proposal for the owner's review. It is not built yet. Revision 2 adds the curves of the form: the owner found the first revision too simple, with straight lines where the references have subtle curves. Revision 3 applies the owner's answers to questions 8 to 12: a larger tuck over the top third of the body, a hood with near-straight sides and tight top corners, and a screen 10.8 mm nearer the bezel.

This directory holds the target form of the cabinet as drawings: the big volumes first, then elevations, sections, the hood, the two junctions, and a map of every face. The drawings come from data. `cad/candybar/shell/dims.py` (class `Blueprint`) holds the named dimensions. `cad/candybar/shell/profiles.py` turns them into profiles and labelled faces. `cad/tools/draw_blueprint.py` draws the sheets from the profiles. `cad/candybar/shell/solids.py` builds the solids from the same profiles, so the drawing and the model cannot drift apart. `cad/tools/check_solids.py` measures the solids against the faces. The solid code of the earlier form is removed (2026-11-11).

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
| `08-curvature` | Each curved line against its straight chord, with the deviation drawn five times too large, and the same curve on the references as ghost lines |
| `09-hardware` | The fit study: the hardware and its keep-out zones in the cavity of a 4 mm skin. Two side sections, three plan sections, the rear view with a proposed door opening, the sight lines of three players. Made from `cad/out/shell-bp/fit/sections.json` (see "Hardware in the shell") |
| `10-split` | The split that the owner chose: front, right side, top and rear, each piece numbered and tinted, every seam drawn and labelled (blue in a design line, red on an open face), and the piece list with the print box of each piece. Made from the cut of `candybar.shell.split` (see "The split") |
| `11-joints` | The joints: dimensioned sections of joints 1 to 7, the coupon pair and the named values. Every value comes from `cad/candybar/shell/joints.py` (see "The joints") |

Drawings of the references are third-party material. They are in `cad/out/shell-d/reconstruction/` (ignored by git):

| File | Content |
| --- | --- |
| `k-01-elevations.png` | The 3D reference model: four elevations, exact |
| `k-02-face-map.png` | The 3D reference model: face map with the same IDs |
| `k-03-sections.png`, `k-04-rail-sections.png` | The 3D reference model: side section and horizontal sections (exact slices) |
| `k-05-hood.png` | The 3D reference model: the hood |
| `m-faces-hood.png`, `m-faces-body.png` | The maker's mini: the face IDs on the photo, each reading marked estimated or uncertain |
| `r-faces.png` | The real New Astro City: the face IDs on the photo |
| `../sheet-side-profile.png` | Side profiles and hood outlines of the references and of the target, over each other (the target on the exact slices of the 3D reference model) |
| `overlay-owner-ref-1.png`, `overlay-photo-g-video-arc-toward-hood.png`, `overlay-owner-ref-3-real-three-quarter-left.png` | The silhouette of the blueprint on three photos, after a camera fit on the top edge and the width of the bezel |
| `curves/` | Traces of the silhouettes and stripes in the photos, and the scripts that made them |

## Proportions of the big volumes

`measured` is a value from the photo tools (`docs/research/photo-measurements.md`). `estimated` is a reading by eye or a trace with an assumed camera. The 3D reference model is exact.

<!-- proportions:begin -->
| Ratio to the body width W | 3D reference model (exact) | Maker's mini (photos) | Real New Astro City | This cabinet | Why it differs |
| --- | --- | --- | --- | --- | --- |
| Body width W, mm | 270.0 | 246.9 +-2.4 (measured) | 750 (published) | 494.7 | 16-inch 16:10 monitor (354 wide) with its cradle, between two rails |
| Deck width / W | 1.000 | 1.02 +-0.03 (measured) | about 1.0 | 1.000 | same: the deck's side is flush with the side band |
| Depth / W | 1.252 | about 1.3 (estimated) | 1.207 (published) | 1.172 | 540 at the desk holds the power supply and the BC-250; the upper rear is 40 proud for the hood |
| Height / W | 1.172 | about 1.25 (estimated) | 1.927 (floor cabinet) | 1.159 | a 16:10 screen is lower than 4:3 at the same width |
| Deck top above the desk / W | 0.185 | about 0.2 (estimated) | not comparable | 0.146 | 70 mm panel height for the hands; 58 inside is enough for the lever |
| Deck front to screen foot / W | 0.380 | about 0.42 (estimated) | 0.49 (estimated) | 0.477 | 396 x 175 control panel (166.4 deep at the sides, the front follows the deck) with its border |
| Recline of the screen and of the rail's chord, deg | 32.5 | about 30 (estimated) | 26 (estimated) | 30 | owner's choice for the 16:10 bezel |
| Rail arc in side view, sagitta / chord | 0.091 (one arc, R 1.154 W) | 0.000 +-0.002 (measured: straight) | not measured (+-0.03) | 0.035 | a subtle arc between the maker's straight rail and the 3D model's strong one; sagitta 13.0, turn 16 deg |
| Body side below the tuck | vertical, flat | straight (measured); its lean is not measurable | straight (measured); its lean is not measurable | vertical, flat | same as the 3D model |
| Body side bow (widest at mid height) / W | 0.000 | 0.000 +-0.004 (measured) | 0.000 +-0.003 (measured) | 0.000 | same: no bow |
| Body tuck toward the hood, each side at the seam / W | 0.000 (the hood leans 13.5 deg from the seam) | 0.010 +-0.006 (measured) | 0.018 +-0.006 (measured, an upper limit) | 0.023 | owner's choice: more than both, over the top third; starts at 0.667 of the body height, 11.1 deg at the seam |
| Hood crown across the width / W | 0.000 | 0.000 +-0.005 (measured) | 0.000 +-0.001 (measured) | 0.000 | same: the hood top is straight across |
| Seam (body top) above the desk / W | 0.916 | 0.88 (estimated) | not comparable | 0.857 | follows from the bezel: 215 image + 2 x 45 frame + 40 apron + 32 brow |
| Hood height over the seam / W | 0.256 | 0.33 (0.35 to bezel top) | 0.25 to 0.33 (0.36 to bezel top) | 0.302 | 0.358 to the bezel top; a flat top below the top of the rear arc |
| Hood depth at the seam / W | 0.335 | 0.28 (estimated) | 0.30 (estimated) | 0.283 | needs the upper rear 40 proud; the front foot stands on the line of the rail |
| Screen inset below the rail land at mid height / W | 0.096 (cheek 25.9 proud) | about 0.05 (estimated) | deep (CRT) | 0.041 | flat screen 7.2 behind the chord; 15.9 below the land at the window top |
| Bezel width / W | 0.885 | 0.858 +-0.016 (measured) | about 0.79 | 0.879 | 344.7 image + 2 x 45 frame |
| Rail land / W | 0.016 | 0.05 +-0.015 (estimated) | not read | 0.032 | what the bezel leaves, less the edge section; 9.0 at the bezel top (the tuck) |
| Rail edge, in x back / W | 0.039 x 0.039 (45 deg facet) | 0.03 x 0.12 (band 10 to 18 deg) | not read | 0.026 x 0.049 | the deck's own edge section (10 deg band), so the edge follows through |
| Side band depth at the desk / W | 0.277 | 0.27 (estimated) | not read | 0.279 | follows both references; the built model has 0.35 |
| Rear body narrower, each side / W | 0.074 | 0.01 to 0.03 (uncertain) | not read | 0.024 | a shallow step behind the side band |
| Hood foot width / W | 0.990 | 0.94 to 0.96 (measured) | 0.95 (measured) | 0.954 | the outline of the body top: no shoulder, a groove at the seam |
| Hood side lean, seam to top corner, deg | 13.5 to 22 (one arc) | about 6, then one long blend (estimated) | 11 to 19 (measured +-3) | 11.1 to 13.1 | tangent to the tuck, then near straight (R 7.2 W), as on the real cabinet |
| Hood top corner radius / W | 0.074 | none: one long blend (estimated) | 0.06 to 0.07 (measured, left) | 0.070 | the real cabinet's tight corner |
| Hood top flat / W | 0.713 | 0.66 (estimated) | about 0.68 (estimated, owner-ref-1) | 0.713 | follows from the side and the corner; straight marquee window 352 |
<!-- proportions:end -->

## Curves

The owner's words on revision 1: "the geometry we have is too simple, straight lines where the real thing as well as bar tops we've looked at have subtle curves", "the top of the front body curves inward smoothly toward the hood", "the hood and body meet in one smooth curve with a bevel cut between them", and in profile "a convex arc which follows the contour of the CRT".

### How the curves were measured

- **3D reference model.** Exact slices of the meshes.
- **Photos.** A row-by-row trace of a brightness or color edge, then a fit. The picks and the readings are in `cad/reference/owner-ref-1.json`, `photo-g-video-arc-toward-hood.json` and `owner-ref-3-real-three-quarter-left.json`. The traces are in `cad/out/shell-d/reconstruction/curves/`.
- **Correction for the camera.** A camera turns a straight edge into a straight line in the photo, whatever its position and tilt. So each curve is measured as the distance of the traced edge from a straight line: the line through the lower, straight part of the body side for the tuck, and the chord for an arc. A tilt of the camera cannot make this distance. It does not need a focal length. Widths are not compared between heights.
- **The limit of this correction.** The distance shows that the edge is curved in space. It does not show in which direction. An edge that curves away from the camera gives the same trace as an edge that curves sideways. Two views are necessary to separate them, and no reference has two good views.

### Survey

Ratios are to the body width `W` unless a chord is named.

| Line | Revision 1 | 3D reference model (exact) | Maker's mini | Real New Astro City | Revision 3 |
| --- | --- | --- | --- | --- | --- |
| Rail (cheek front line) in side view | Straight, 30 degrees, one radius at the foot | One arc: sagitta 0.091 of its chord, R 1.154 W, lean 12 degrees at the foot and 52 at the top | Straight: 0.000 ± 0.002 of the chord (photo-e: the front edge of the stripe departs 0.5 px from a line over 671 px, at about 42 degrees to the side) | Not measured. The stripe and the highlight of the cheek are straight above the sweep within ± 0.008 of their length in two views that are only 15 to 20 degrees off the front. That allows 0 to 0.03 of the chord. | One arc: sagitta 0.035 of the chord (13.0 mm), R 2.69 W, lean 22 degrees at the foot and 38 at the seam |
| Body side below the tuck, front view | Vertical, straight | Vertical, straight | Straight within 0.004 W (photo-g) | Straight within 0.003 W (owner-ref-1) | Vertical, straight |
| Body side, the top part (the tuck), front view | None. A shoulder of 12 under a narrower hood. | None. The hood is 1.4 narrower and leans 13.5 degrees from the seam: a kink. | 0.010 ± 0.006 W at the seam. Photo-b: 0.014 W, from about 0.70 of the body height. Photo-g: 0.003 W, then a corner radius of 0.015 W at the top. | 0.018 ± 0.006 W at the seam, from 0.78 of the body height (owner-ref-1). An upper limit: see below. | 0.023 W (11.4 mm) at the seam, from 0.667 of the body height, on one arc of R 1.23 W. 11.1 degrees at the seam. |
| Side of the hood over the seam, front view | An arc of R 1.3 W that starts at 7 degrees, on a shoulder | An arc of R 1.29 W, 13.5 to 22 degrees | About 6 degrees, a small lip at the foot, then one long blend | The slope is continuous over the seam: 8.5 ± 3 degrees below it, 11 to 15 above it. The hood foot is 0.95 W. | Tangent to the tuck at the seam: 11.1 degrees. Near straight: one arc of R 7.7 W that turns 2 degrees, to 13.1 degrees at 130 above the seam. Then a top corner of R 0.07 W. No shoulder. A groove of 3 at the seam. |
| Top of the hood across the width (crown) | Straight | Straight | Straight within 0.005 W (photo-b) | Straight within 0.001 W (owner-ref-1) | Straight |
| Hood in side view | Soft edge, short roof, one arc down the rear | A 42 degree facet, a flat top, a rear that leans 16 degrees | One arc down the rear (estimated trace) | Not read | No change |
| Bezel | A flat frame with one step | A flat plate, 6 to 26 behind the cheeks | A flat land, then an inner frame that slopes in to the screen (photo-g, estimated) | A deep surround for the tube | A land that follows the rail arc, then an inner frame that slopes in to the flat screen |
| Sides in plan, step, rear walls, body top, deck front in plan | Straight or flat | Straight or flat | Straight where a photo shows them | Not readable | No change |

What I could not measure:

- The rail arc of the real cabinet. No photo shows the cabinet from the side.
- The real cabinet's tuck without the effect of its rail. In the front photo the top of the rail is farther from the camera than its middle. If the real rail curves back at its top, a part of the 0.018 W is that curve and not a narrower body. So 0.018 W is an upper limit.
- The focal length of each photo. The overlays assume one (it is in each annotation file). The survey numbers do not use it.

Where the photos disagree with each other, or with what was said:

- "The real thing and recreations have a convex arc" in profile. The 3D reference model (a recreation) has a strong one. The maker's mini has none that I can measure: its rail is straight. For the real cabinet the photos neither confirm nor exclude an arc. In `owner-ref-3` two things read as an arc of the main body: the outer line of the side at the right, which bulges 0.033 of its length (that is the rear of the body, deeper at the height of the tube), and the stripe, which bends where the sweep starts.
- The two front photos of the maker's mini disagree on the tuck: 0.014 W in photo-b, 0.003 W and a corner radius in photo-g. Photo-b is small (the body is 318 px wide). Photo-g is sharper, and its right side is white on white.
- The coordinator read 318, 302 and 260 px for the widths in `owner-ref-1`. The trace gives 353 px above the deck, 337 below the seam and 277 at 0.8 of the hood height, in the full-size file. The ratio at the seam agrees: 0.95.

### The amount of each curve, as named values

Each curve is one value in `dims.Blueprint`. Sheet 08 shows our value beside the values of the references.

| Value | Now | Maker's mini | Real cabinet | 3D model | Why this value |
| --- | --- | --- | --- | --- | --- |
| `body_tuck_ratio` | 0.023 | 0.010 ± 0.006 | 0.018 ± 0.006, an upper limit | 0 | The owner's choice (option 4 of 2026-11-10). It is more than both references. The land at the top of the bezel is 9.0 mm (revision 5). |
| `body_tuck_from` | 0.667 | 0.70 to 0.95 | 0.78 | not applicable | The owner's choice: the tuck acts over the top third of the body (option 2 of 2026-11-10) |
| `hood_side_turn` | 2 degrees | one long blend | 11 to 19 degrees (measured ± 3) | 13.5 to 22 degrees | The owner's choice: a hood side that runs near straight, toward the real cabinet |
| `hood_corner_ratio` | 0.07 | none: one long blend | 0.06 to 0.07 (measured) | 0.074 | The real cabinet's corner. See "The top corner of the real hood" below. |
| `rail_sagitta_ratio` | 0.035 | 0.000 | not measured | 0.091 | The owner's choice (option 2 of 2026-11-10). The maker's cabinet has none and the 3D model has a strong one. 0.035 is a visible arc that keeps the screen less than 21 mm below the rail. A 29 inch tube of that time has a sagitta of about 0.03 to 0.05 of its height (ESTIMATED from a face radius of 1.0 to 1.5 m). |
| `hood_crown_ratio` | 0 | 0 | 0 | 0 | All three are straight |
| `body_bow_ratio` | 0 | 0 | 0 | 0 | All three are straight below the tuck |

### A flat monitor in a convex body

- The convex form is in the shell. The rails arc in side view. The body sides tuck in toward the hood in front view.
- The screen stays flat and reclined 30 degrees. Revision 3 moves it 10.8 mm forward, square to its face: it is now 7.2 mm behind the chord of the rail arc (`mon_setback`). The sight line changes little. (Revision 4 replaces the two eye heights of 530 and 450 with three players: see "Hardware in the shell".) The monitor and its cradle move with the screen. The power supply and the BC-250 module stay where the last build checked them.
- **Recline** now has this definition: the angle of the chord of the rail arc. It is also the tangent of the arc at mid chord and the angle of the flat screen.
- The rim of the bezel plate follows the rails. The bezel land (20 wide) is a part of the same cylinder, 2 mm below the rail land. Inside it an inner frame (25 wide) slopes down to a flat rim 2 mm above the screen. The slope is 16 to 33 degrees from the land (it was 36 to 47): the least at the top edge, the most at the sides near mid height.
- The screen is 14.0 mm below the rail land at the top of the window, 20.2 at the screen center and 17.7 at the bottom of the window. Revision 2 had 24.8, 31.0 and 28.5. The inset is largest near mid height, as on a tube surround.
- The monitor (354 x 230 x 10) and its cradle stay behind the bezel. Its top edge is 5 mm above the window, under the inner frame, which is 25 mm wide. The land of the bezel at the top edge lies 0.4 mm behind the chord, so the plate between the land and the monitor face is about 6.8 mm thick there (ESTIMATED: the back of the plate is not drawn yet).
- The bezel plate stays removable: it comes out square to the screen, and no part of it is behind a rail. Its back is flat.
- Print: a plate that lies with its flat back on the bed has layer steps on the curved land (8 mm of rise over 305). A plate that stands on its long edge has the arc in the layer plane and prints smooth. The plate is larger than the bed in both cases, so it is two halves, as before.

Numbers at `W` = 494.7:

| Check | Value |
| --- | --- |
| Sagitta of the rail over its chord (370.5) | 13.0 mm. Over the height of the bezel the rail stands 6.8 mm in front of the chord at the lower edge, 13.0 at the screen center, 1.6 at the upper edge. |
| Monitor at its top corners | The top front corner of the monitor is at z 375.2, the top rear corner of the cradle at z 360.2. The tuck is 3.9 mm at z 375. The outer skin is 63.7 mm outside the monitor's top front corner and 68.0 mm outside the cradle's top rear corner (41.7 and 46.0 outside the 22 mm side clearance). No conflict: W does not change. The wall thickness is not designed yet. The build check does not know the tuck yet. |
| Rail land | 16.0 at the bottom of the bezel and at mid height, 9.0 at the top of the bezel (revision 5; it was 7.5 in revision 4) |
| Hood | Foot 471.9 (0.954 W), top flat 348.8 (0.705 W), top corner R 34.6 (0.07 W) |
| Marquee window | 352 x 34, eleven modules of 32 |
| Sweep | Turns 68 degrees (it was 60). Its end is 6 mm higher. The deck does not change. |

### Conflicts and options

Revision 2 found that the tuck costs width in two places: the land at the top of the bezel and the marquee window. The table gives the costs for a hood side that carries on the arc of the tuck into a long blend (revision 2).

| Tuck at the seam | Rail land at the top of the bezel | Straight marquee window | What it needs |
| --- | --- | --- | --- |
| 0.010 W (maker's mini) | 12.0 | 336, ten modules | Nothing |
| 0.015 W (revision 2) | 10.1 | 326, ten modules | Top flat 0.66 W (it was 0.64) |
| 0.018 W (real, upper limit) | 8.9 | 318 with a top flat of 0.66 W, 322 with 0.68 W | A top flat of 0.68 W, which makes the top corners of the hood tighter. Or nine modules. |
| 0.023 W | 7.0 | 300 to 306 | Nine modules. Or a body 24 mm wider (519). Or a hood side that does not carry on the arc of the tuck: then the curvature jumps at the seam. |
| 0.023 W from 0.667, near-straight hood side, corner 0.07 W (revision 3) | 6.4 | 358, eleven modules | Nothing. The curvature changes at the seam (R 1.23 W below, R 7.7 W above), but the tangent is the same, so the outline has no corner. |
| 0.027 W | 5.4 | 284 | The land is less than 6 mm: a wider body or rounder top corners of the bezel |

The rail arc has no conflict with the monitor. Its cost is depth in front of the screen. The last column has the screen 7.2 mm behind the chord, as in revision 3:

| Sagitta / chord | Sagitta | Rail lean, foot and seam | Screen below the rail land at the center |
| --- | --- | --- | --- |
| 0 (maker's mini) | 0 | 30, 30 | 7.2 |
| 0.020 | 7.5 | 25, 35 | 14.6 |
| 0.035 (drawn) | 13.0 | 22, 38 | 20.2 |
| 0.050 | 18.4 | 19, 42 | 25.8 |
| 0.091 (3D model) | 32.8 | 10, 51 | 41.1: a deep well round the screen |

### The top corner of the real hood

No record had a usable size for this corner. The silhouette trace in `owner-ref-1.json` starts 18 px below the hood top. So I measured it on `owner-ref-1` (scratch script, not tracked):

- The edge of the cap was traced on each row and each column near the corner (a brightness step, with a sub-pixel peak). The top edge is at row 231.7. It is straight from x 187 to x 425 (0.68 W).
- A line was fitted to the side between rows 244 and 272. A circle tangent to that line and to the top edge was fitted to the points between them.
- Left corner: R 24.5 to 25.8 px (0.070 to 0.073 W), rms 0.15 to 0.17 px. A free circle gives 0.062 to 0.065 W. The body is 351 px wide (W).
- The right corner gives no stable result: the wall behind it is lit, and the trace jumps by 5 px on some rows.
- The photo is taken from above and tilted down. This changes the apparent lean of the side (14 degrees near the seam, 20 to 23 below the corner), and a little the apparent radius. So the corner is 0.06 to 0.07 W, and the target uses 0.07 W.

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

The target: the rail is a land (16.0), then the deck's own edge section turned on its side (a radius of 10.5 that turns 80 degrees, a band that leans 10 degrees, a crease 24 behind the land), then the side band. The same section runs down the rail arc, round the sweep and along the deck, so the edges line up by construction. Above the start of the tuck, the section is measured in from the side at the height of each point, so the crease lies on the side band and the side runs into the hood with no ledge. The side band and the deck's side are one plane up to 0.75 of the body height. Above that the side band leans in with the tuck. The step is 138 behind the deck at the desk (0.28 W) and 12 deep.

### Hood to body

- **3D reference model.** The body top is flat. The hood stands on it and is 1.4 mm narrower on each side. Its legs continue the cheek: their fronts lean 37 to 43 degrees, and the cheek's facet runs on up the leg. There is no sill: the hood band (44 degrees) starts at the seam, on the line of the screen face. The rear of the hood leans forward 16 degrees and continues the upper rear wall.
- **Maker's mini.** The hood is a cap on a flat body top. A shoulder shows at the sides (0.03 W, measured). The front of the cap is near upright, so the plane changes at the seam. The legs are thin from the front (0.03 W, measured) and turn into the hood's side with a soft corner. A white zone 0.088 W high (measured) lies between the hood band and the bezel. It holds the ledge, the sill and the brow band of the body. The seam is not visible on the front in the photos (uncertain). From the side the hood is upright in front and one long arc from the top down the rear to the seam (estimated trace). Its depth is 0.28 W, the same as the body top.
- **Real cabinet.** A cap on a shoulder. The hood is 0.30 W deep (estimated from the manual drawing).

Where this contradicts the current model: the current hood is 0.19 W deep on a body top 101 mm deep. Its rear is an upright wall with a 20 mm radius. Both references that show the side have a deeper hood whose top runs down the rear in one arc.

The target: the upper rear of the body stands 40 mm proud of the lower rear wall, so the body top is 141 deep (0.285 W) and the hood 140 at the seam (0.283 W). The rear wall of the hood is flush with the upper rear of the body. At each rear corner a flat upright face at 45 degrees in plan (HC16) carries the corner of the body top up into the hood, so the foot of the hood has the outline of the body top all round. HC16 runs out about 47 above the seam, where the side of the hood leans in past it. The cabinet is 580 deep (it was 540). The foot of the cap's front lies on the line of the rail at the seam. Its front leans back less than the rail: 16 degrees over its lower 0.29, then 2 degrees, with a radius of 40 between. Each leg stands over the land and the edge of the rail. At the sides there is no shoulder: the foot of the hood has the outline of the body top (471.9 wide, 0.954 W), and the side of the hood leaves the seam on the tangent of the body's tuck. The seam is a gap of 1.5 with a bevel of 3 on both parts: a groove across one surface. Each bevel has one height all round its part: it starts on the side 3 below the body top (3 above the foot of the cap) and runs in 3 to the top (to the foot). It goes along the sides, round the front corners and across the front, so that the seam is one level groove from the front to the rear (FB5 on the body, HC15 on the hood). It replaces the bevel of revision 3, which ran out at the front corners and left the front with no bevel. To make room for it across the front, the bezel, the window and the screen stand 8 lower on the face than in revision 3: the strip of face above the bezel is 20 (brow_ledge) and the band below it 52 (band_len). Revision 5 moves them 12 lower again (see "Revision 5"). Revision 1 had a shoulder of 12 here, from the maker's 0.03 W. The owner's front photo of the real cabinet shows none.

### The hood

- **Outline from the front.** The 3D reference model has sides on one arc that lean 13.5 to 22 degrees, a corner radius of 0.074 W and a top flat of 0.713 W. The maker's mini has sides that lean about 6 degrees at the foot, and then one long blend over the upper half into a top flat of about 0.66 W (estimated from the picks in `cad/reference/photo-b.json`). A single radius does not describe it. The real cabinet has steeper sides (11 to 19 degrees, measured ± 3) and tight top corners (0.06 to 0.07 W, measured), with a top flat of about 0.68 W. The owner chose the real cabinet's form (2026-11-10): the long blend reads as a dome. The target: the side of the hood leaves the seam on the tangent of the body's tuck (11.1 degrees). It is near straight: one arc of R 7.7 W that turns 2 degrees (`hood_side_turn`), up to 130 mm above the seam. Then one radius of 0.07 W (34.6 mm, `hood_corner_ratio`) turns it into the top flat. The top flat follows: 348.8 mm (0.705 W). The straight marquee window is 358 mm, eleven modules.
- **Bottom front corners.** On the maker's mini the legs come down near upright to a foot 0.94 to 0.96 W wide, and the bottom corners of the opening are near square. The target has a foot of 0.954 W, legs that lean 11.1 degrees at the seam, and corners of radius 6. The current model has legs that lean 10 degrees on a body with no tuck, and corners of radius 8.
- **Side profile.** The owner's sketch of 2026-11-10 (the markup on the side render). The front leans back 16 degrees over its lower 0.29, then 2 degrees, with a radius of 40 between. A soft top front edge of one radius (14). A flat top 148 above the foot of the cap. The rear is the arc of revision 3 (95 deep, 110 high from the old top), cut by the lower flat top, with a radius of 10 in the crease, then an upright rear wall.
- **Inside the arch**: the marquee under the top bar (window 352 x 34, 11 modules of 32 mm), a lip, the hood band with two speaker forms and the logo form, and the ledge on the sill. The hood band is upright, so that the speakers fire straight forward (the owner, 2026-11-10: "The speaker face should be a 90 so speakers fire straight forward"). Before, the band leaned back 24 degrees, and the bend of the hood front ran across the speakers. The band face is 5 behind the hood front at the top of the band (`hood_band_recess`). The ledge is what is left of the sill in front of it: 13.9. The speaker forms stand 13 proud of the band. Their fronts are 0.2 ahead of the hood front at their foot and 7.8 ahead at their top, and 5.8 behind the foot of the hood front. The lip moves forward with the band: its front is on the line of the hood front. The marquee is upright too, so that it faces directly forward (the owner, 2026-11-10: "I think we can make the marquee 90 face directly forward as well, then bring it forward and just leave a small edge below it"). It stands 5 behind the front of the lip (`hood_marquee_edge`), so the top of the lip is a small edge of 5. With the lip 5 proud of the band, this puts the marquee in the plane of the hood band. The soffit under the top bar is 3.5 deep, and the marquee is 3.5 to 4.8 behind the hood front at each height. Upright, the window is 352 x 34 (it was 362 x 34 when it faced down 18 degrees): its top is higher, where the corner of the opening is narrower. 352 is 11 modules of 32, so the display does not change. Between the lip and the top bar the opening is 36.1 high (`hood_marquee_open_h`): 1.0 below the window and 1.1 above it.

## Revision 5

Two changes from the owner, 2026-11-10. Nothing else of the outer form moves: the body top, the seam bevel, the hood, the rails, the deck, the recline, the size of the bezel and its frame stay.

**The screen is 12 lower on the face.** The owner's words: "move the screen down a bit". The top corners of the bezel came near the tuck, and the strip of face above the bezel was thin. The bezel, the window, the screen and the monitor move 12 down the face together. `band_len` goes from 52 to 40 and `brow_ledge` from 20 to 32. Their sum does not change, so the body top stays at 423.9. `cad/out/shell-bp/compare/screen-drop-options.png` shows drops of 8, 12 and 16, so that the owner can ask for a different amount.

| Value | Revision 4 | Revision 5 |
| --- | --- | --- |
| Strip of face above the bezel (`brow_ledge`), along the face | 20 (16.4 plain, then the seam bevel) | 32 (28.5 plain) |
| Band below the bezel (`band_len`), along the face | 52 | 40 |
| Top of the bezel, z | 407.9 | 398.2 |
| Front view: top corner of the bezel to the side outline | 21.5 | 23.1 |
| Rail land beside the top corner of the bezel | 7.5 | 9.0 |
| Screen below the rail land: top, centre, bottom of the window | 14.8, 20.3, 17.1 | 15.9, 20.4, 16.2 |
| Cavity half width at the top corners of the monitor room | 237.0 at z 379 | 239.0 at z 369 |
| Straight plugs: shortfall at the top corners, at mid image | 21.0, 15.0 | 19.0, 15.0 |
| Monitor, present unit: gap to the skin at the top, at the bottom | 34.0, 29.4 | 34.0, 29.4 |
| Monitor, any 16:10 unit: gap at the top, at the bottom | 1.3, 1.3 | 1.3, 1.3 |

The last row was true for revision 5. After it, the opening behind the bezel lost its side ledges, and the gap is now 3.3 (see "Hardware in the shell").

A check on side sections, before the fit run, found no limit up to a drop of 20. The nearest skin to the top and the bottom of the monitor room is the ledge of the opening behind the bezel (9.2 from the clamps), and it moves with the bezel. The sweep, the deck and the controls under the panel stay far from the monitor and its cradle (30 from the sweep at a drop of 20).

**The front of the control panel follows the deck.** Seen from above, the deck front is a centre face and two flanks that turn back `deck_flank` (8 degrees). The panel was a rectangle, so the border of deck in front of it became narrower toward its front corners. Now the front edge of the panel is three straight segments, parallel to the centre face and to the flanks, with one border all along: 26 from the deck front to the panel (25 to the pocket). The side edges and the back edge do not move. The front corners move back 8.6, so the panel is 175 deep at the centre line and 166.4 at the sides. The corners have no radii: a cutting service cuts straight lines. `profiles.panel_outline` is the one definition. The faces CP1 and DK8, the panel plate, the pocket, the opening in the skin under the plate and the drawings all use it. Both panels (arcade and PC) have this outline.

Corners of the panel plate (x, y from the deck front at the centre line): (-198.0, 34.6), (-136.7, 26.0), (136.7, 26.0), (198.0, 34.6), (198.0, 201.0), (-198.0, 201.0). The pocket is the same outline moved out by `panel_gap` (1). The opening in the skin is the outline moved in by the ledge (8).

No control moves. The lever, the eight buttons, start, coin and menu, and the encoder stay in the opening under the plate. Nearest to the new front edge is the nut of the front service button (Svc1): 16 from the front edge of the opening on the flank, 24 from the front edge of the plate.

The older generator (`cad/params/cabinet.csv`, `candybar/massing.py` and `candybar/panel.py`) still has a rectangular panel of `panel_w` x `panel_d`. The integration step must give it this outline.

## Revision 6

The detail pass on the back, 2026-11-11. The owner's words: "Bevel at the rear reads odd ... I think we might want to fillet the back surface corners". The vertical corners of the back are now one round of `rear_corner_r` (18) in plan, from the floor to the roof of the hood. Nothing else of the outer form moves.

**Which corners.** "The vertical corners of the back surface" are three edges on each side:

- the lower rear: the rear body side RB1 to the lower rear wall RB3, from the floor to z 310, and on up the rear slope RB4;
- the upper rear: RB1 to the upper rear wall RB5, from z 350 to the body top. Here the step RB2 leans back into the corner: in revision 5 it met the rear wall at z 419.4 and left a flat at 45 degrees in plan on the body top;
- the hood: the side HC5 to the rear wall HC9, with the flat corner face HC16 at 45 degrees over the lower 47, then the side to the rear arc HC8 up to the roof.

**What changed.**

- RB7 (new): the rear corner round of the body. It is tangent to the rear body side and the rear wall. On the slope it follows the slope (an oblique cylinder). Where the step comes nearer to the rear wall than 18 (from z 385.5), the round rolls round the step's inner crease and then lies tangent to the step.
- RB9 (new): a round on the step's outer edge. It grows from nothing at z 385.5 to 18 at z 422.1, where the step line touches the round and runs out into it. It is at most 1.5 deep. Above that height one round of 18 turns from the side band to the rear wall.
- HC16 (changed): the flat corner face is now the round of the cap, 18 in plan at every height, tangent to the side and to the rear wall or the rear arc, up to the roof. At the foot it has the outline of the body top, so the round passes through the seam groove with no jog.

| Value | Revision 5 | Revision 6 |
| --- | --- | --- |
| Lower rear corner | sharp | round R 18 |
| Upper rear corner | sharp; the step met the rear wall at z 419.4 | round R 18; the step runs out into it at z 422.1, inside the seam bevel |
| Body top and hood foot at the rear corner | a flat at 45 deg, 13.6 long | round R 18 (R 15 at the root of the groove) |
| Hood rear corner | a flat at 45 deg (HC16), then a sharp edge to the roof | round R 18 from the foot to the roof |
| Rear door opening | 446.7 wide | 426.7 wide: a flat land of 4 beside it, then the round |
| Power supply, left face | x -223.4 | x -212.4 (+11) |
| BC-250, its I/O edge | x -178.2 | x -163.2 (+15); its exhaust duct starts 5 inside the start of the round, 1 inside the door opening |

**The radius, and what limits it.** The owner's first aim was 20 to 25 (0.04 to 0.05 W). The step limits it:

1. At the foot of the rear slope (z 310) the rear body side is only 18.2 long between the step's inner crease and the lower rear wall. A round larger than 18.2 runs over the crease there too.
2. The step must run out into the round inside the seam bevel, so that the foot of the hood keeps the outline of the body top with one round and no flat. That needs 16.4 to 19.1.

18 meets both. It is 0.036 W: between the hood's top rear radius (10) and the deck's front corner (44.5). The body and the hood have the same radius. `cad/out/shell-bp/compare/rear-fillet-options.png` draws 10, 18 and 25 at three heights, with what limits each.

The other limits, checked:

- **Door.** The rear wall is 470.7 wide. The round starts 18 from each side, so the opening is 426.7 (20 narrower), with a flat land of 4 at each side (`fit.Layout.door_land`). The fit study checks that the board, the heatsink, the shroud and the duct of the BC-250 lie inside the opening (rule "door service").
- **Power supply.** It stands against the rear wall at the left. The inner skin of the round has a radius of 14, so the supply's left face moved 11 toward the centre line: it stands 5 inside the start of the round (`fit.Layout.corner_clear`). 1 would clear the true inner skin; the fit study needs 5, because its slab cavity is up to 4 narrower than a true offset in the round. Its rear face is on the flat of the rear wall, below the door. Its sockets are on the front face, away from the corner.
- **BC-250.** Its exhaust duct runs along the door to the left wall. It moved 15 toward the centre line, so that the duct stays 5 inside the start of the round and 1 inside the door opening. The slot vents stay inside the door.
- **The split.** The round lies inside the pieces rear lower R and L, middle R and L, upper R and L and the hood halves. The level seams L1 and B1 cross it square; R1 now runs up from the door's top corner at x 213.3, on the flat 4 from the round. No seam ends on the round. Sheet 10 has the pieces: the rounds made rear lower R and L 228 x 228 x 134 (they were 231 x 230), upper R and L 207 x 206 (210 x 209), middle R and L 205 x 204 (206 x 204), and the door halves 213 x 182 (223 x 185). All 22 pieces and 9 tiles fit the A1.
- **Grips.** Each grip pocket ends at x 213.3, in line with the side of the door, on the flat beside the round (`structure.grip_box`).

**The renders.** `cad/out/shell-bp/compare/rear-fillet-before-after.png` puts revision 5 and revision 6 side by side.

## Hardware in the shell

`cad/candybar/shell/fit.py` is a fit study of the hardware in the accepted form. It does not change the outer form. Sheet 09 draws it. `cad/out/shell-bp/fit/report.md` has all the numbers. The study exits 1 when an item does not fit. Result: PASS, with a skin of 4.

- **Skin.** `wall_t` (4.0) in `Blueprint`. `cavity.py` makes the cavity from side sections of the built parts, each offset inward by `wall_t`, one each mm across the width. Each slab of the cavity is the common of the offset sections over the slab and `wall_t` on each side. Thus the wall is never thinner than `wall_t`. It is thicker where the form turns across the width. Measured on 2151 points: smallest 4.00, median 4.00, largest 18.84. Examples: 5.6 at the sides of the body and the hood, 4.5 in the tuck, 12.5 at the rail edge at the middle of the bezel (square to the screen). The wall is open under the control panel (inside a ledge of 8, on the outline of the panel). It is open behind the bezel plate, with a ledge of 6 at the top and the bottom only. The body top is open into the hood.
- **Hardware.** The sizes come from `cad/params/*.csv`. The envelopes are those of `candybar/hardware.py` and `candybar/panel.py`. The anchors come from `Blueprint`. The layout choices are the named values of `fit.Layout`. New rows in `hardware.csv`: the USB sockets and the hub, the room for the marquee modules, and the generic monitor.
- **Floor.** The power supply and the hub stand on the printed floor of 10 (`Layout.floor_t`, decision record 0006). The floor stands on the table on thin non-slip pads (the owner, 2026-11-11). On the floor of 7 of the study everything stood 3 lower: the power supply is now at z 10, the BC-250's lower edge at z 124, the door sill at z 116, the hub at z 10.1.
- **Compute module.** The BC-250 has a fixed mount behind the rear door (decision record 0005). The door is a cover with the vents and has no cable on it. The fan stands 5 from the door, and the shroud seals the gap. The BC-250 stands 3 above the clear space over the fan of the power supply (`Layout.bc_above_psu`, 1 more than before), so that its exhaust duct stays out of that space. The proposed door opening is 426.7 x 182: revision 6 narrows it by 20 for the rear corner round, and the floor of 10 raises its sill by 3. The rule "door service" checks that the board, the heatsink, the shroud and the duct lie inside it, and that the power supply's rear face lies on the flat of the rear wall below it. The power supply stands at x -212.4 and the BC-250's I/O edge at x -163.2 (revision 6).
- **Air zones (rule R2b).** The rules R1 and R2 compare a solid with the solids and the keep-out zones of other items. They do not compare two keep-out zones. Rule R2b compares each air zone (the exhaust duct, the fan shroud, the air under the board, the fan space of the power supply) with every solid of every other item. Result: PASS, 4 air zones, no common volume with 81 solids of other items.
- **Monitor.** Any 16 inch 16:10 portable monitor must fit (`docs/research/hardware-envelopes.md` section 1). The room for it is the largest body of the survey (360 x 247.1 x 20.6), 8 of movement each way in the plane of the face, a clamp jaw of 6 on the top and bottom edges, the cradle (20) behind it, plug space of 22 (right-angle plugs) on both side edges over the full height, and a cable channel of 20 from each side to the BC-250. Straight plugs need 258 from the centre line, but the cavity is 243 at the middle of the image and 239 at the top corners (z 369). Thus the cabinet needs right-angle plugs. The gap from this room to the skin is 3.3 at its top and at its bottom. The present unit has 34.0 at the top and 29.4 at the bottom.
- **Monitor out to the front.** The monitor comes out to the front, through the opening behind the bezel plate (the owner, 2026-11-11). The opening is 434.7 wide, with its ledge at the top and the bottom only. Any 16:10 monitor with its plug space passes with 7.3 on each side. Its carrier, with the side flanges that hold the bezel plate (`Layout.carrier_flange`, 4), passes with 3.3 on each side.
- **Sight line.** Three players at a desk of 745 on a chair of 500, 60 in front of the deck, relaxed sitting 30 below the upright eye height. Child of 8 (DINBelg 2005, mean): eye 303 above the desk, 24.1 degrees from the screen normal; the bezel's inner frame hides 0.4 of the image at the bottom edge. Small adult (ANSUR II women, 5th percentile): eye 423, 8.5 degrees. Tall adult (ANSUR II men, 95th percentile): eye 585, 8.2 degrees. Each adult sees the full image.

## The split

Sheet 10 draws the split. `cad/candybar/shell/split.py` holds the seams as data and cuts the skin into pieces. `cad/out/shell-bp/split/proposal.md` is the full study, with the options that the owner did not choose (a build output). Decision record 0006 records the choice.

Decided by the owner (2026-11-11):

- The seams of option B with the hood of option A ("B with the hood of A").
- The width stays 494.7.
- No internal frame: a stressed skin with a printed floor.
- The bonded seams lock with keys first, and are then fastened for good. They are filled and painted.
- The hood has keys, so that it bolts on easily. The owner will look at both a bolted and a bonded hood.
- The floor stands on the table (2026-11-11). It is the 10 mm sandwich of the study, on thin non-slip pads (2 to 3 mm). There are no feet and no ribs under it.
- Hand-holds: only at the rear (2026-11-11). Each is a pocket up into the overhang of the upper rear near a back corner, open downward through the rear slope. There is no grip under the deck nose. One person lifts the back, and the cabinet pivots on the front bottom edge of the deck.
- The material is open: PETG on the A1, or ABS on an enclosed printer. The coupons decide.

Dropped: the ribs under the floor on feet of 18 mm, and the front grip under the deck nose.

The make-up air for the power supply comes in through a slot grille in the rear lower wall, right of the centre line and below the door. The gap under the floor (2 to 3 mm) is too thin for it. `cad/out/shell-bp/split/proposal.md` ("Air path") has the numbers.

Not modelled yet: the flanges, the keys, the ribs, the carriers, the grip pockets and the inlet grille. The grip pockets and the inlet are data in `cad/candybar/shell/structure.py` (`grip_box`, `INLET`). The cut is the bare 4 mm skin, with the rear corner round of revision 6.

### Pieces

22 printed pieces and 9 floor tiles. All fit the usable volume of the A1 (240 x 240 x 245). The largest is rear lower R (228 x 228 x 134; it was 231 x 230 x 134 before the rear corner round of revision 6).

| # | Piece | Print box (mm) | On the bed |
| --- | --- | --- | --- |
| 1 | deck nose | 218 x 218 x 72 | upright, on the bed diagonal |
| 2, 3 | deck side R, L | 186 x 185 x 72 | upright |
| 4 | apron | 210 x 210 x 113 | on its rear edge, on the bed diagonal |
| 5, 6 | lower R, L | 203 x 202 x 134 | upright |
| 7, 8 | middle R, L | 205 x 204 x 176 | upright, on the bed diagonal |
| 9, 10 | upper R, L | 207 x 206 x 126 | upright |
| 11 | brow | 170 x 170 x 38 | upright |
| 12 | upper rear | 181 x 181 x 126 | upright |
| 13, 14 | speaker form R, L | 94 x 76 x 13 | front face on the bed |
| 15 | logo form | 160 x 160 x 5 | front face on the bed |
| 16, 17 | rear lower R, L | 228 x 228 x 134 | upright |
| 18, 19 | door half R, L | 213 x 182 x 4 | outer face on the bed |
| 20 | hood centre | 148 x 139 x 212 | on a cut face |
| 21, 22 | hood side R, L | 139 x 129 x 148 | upright |
| - | floor tiles, front, middle and rear, each side R, centre, side L | 212 x 190 at most | flat |

The bezel plate is two halves, bonded and painted black as one plate (223 x 223 x 217 each). It is a finish piece.

### Seams

Class: a **bonded** seam is permanent: it is locked, screwed, bonded, filled and painted, so it does not show. A **service** seam opens again: it stays open and visible, in a design line. "Where" tells where the seam lies on the form.

| Seam | Class | Where | What it joins |
| --- | --- | --- | --- |
| D1 | bonded | in a design line | deck to body, under the control panel |
| D2 | bonded | on an open face | deck to body beside the panel, at the foot of the sweep |
| F1 | bonded | in a design line | deck nose to deck side, in the crease of the flank break |
| F2 | bonded | on an open face | deck nose to deck side, across the border to the front corner of the panel |
| P1 | bonded | on an open face | apron to the lower pieces, up to the bottom edge of the bezel |
| L1 | bonded | on an open face | lower to middle pieces: level at the bottom corner of the bezel, round the sides and the rear |
| B1 | bonded | on an open face | middle to upper pieces: the belt at the lower crease of the rear slope (z 310) |
| S1 | bonded | in a design line | front body to rear body, in the inner crease of the step |
| R1 | bonded | on an open face | 12 on the back, from the top corner of the door to the slope crease |
| R2 | bonded | on an open face | rear lower R to L, on the centre line below the door |
| R3 | bonded | on an open face | upper rear to the upper pieces, above the door, in line with H1 |
| R4 | bonded | on an open face | door half R to L, on the centre line; the door is bonded into one cover |
| W1 | bonded | on an open face | brow to the upper pieces, 32 upright above the bezel |
| H1 | bonded | on an open face | hood centre to hood side, between the logo form and the speaker form |
| BA1 to BA3 | bonded | in a design line | the floor tiles, under the cabinet |
| DR | service | in a design line | the rear door in its opening (426.7 x 182, the fit study) |
| G | service | in a design line | the hood on the body top, in the level groove FB5 / HC15 |
| BZ4 | service | in a design line | the bezel plate in its reveal |
| DK8 | service | in a design line | the control panel in its pocket |
| USB | service | in a design line | the USB socket plate in the right side of the deck |

### What opens for service

- The rear door lifts off (four thumb screws). The door has no cable on it. Through the opening a person reaches the BC-250, its fan headers and its I/O end.
- The bezel plate lifts out to the front (magnets and two pins, no tool). The monitor then comes out to the front on its carrier.
- The control panel lifts out of its pocket. Its latch is not designed yet.
- The USB socket plate comes out with its leads.
- The hood lifts off when it is bolted (two pins at the front, two M4 screws at the rear). When it is bonded, it does not open.

### Order of assembly and the datum

The datum is the floor: its nine tiles screwed together (joint 2), on a flat table. Each lower piece stands on the floor with a key under its foot flange (joint 3). The pieces below set the rest. The first pass is dry, with screws only. The second pass opens the seams in batches of one to three, bonds them and screws them again in the same holes.

1. The floor.
2. The rear lower halves.
3. The deck nose and the deck sides.
4. The apron and the two lower pieces (S1, D1, D2, F1, F2, P1).
5. The fixed monitor cradle, from the top.
6. The two middle pieces (L1).
7. The BC-250 carrier and the power supply, through the door opening.
8. The two upper pieces, the brow and the upper rear, from above (B1, W1, R1, R3).
9. The door, the hood, the bezel plate and the control panel.

### Where each ring closes

- The L1 ring (the sides and the rear) closes at the second middle piece.
- The B1 ring closes at the upper rear, which drops in between the two upper pieces.
- The top ring closes at the brow, which drops in between the two upper pieces at the front.

A closing piece goes in last, from above, into two seams at once. Those two seams get a design gap of 0.5 at each side (`OtherJoints.closing_gap`). Every other seam has the key clearance, 0.2 (`Joint.groove_clearance`). The coupon sets the clearance.

## The joints

Sheet 11 draws the joints. `cad/candybar/shell/joints.py` is the one source of their values: `Joint` for joint 1, `OtherJoints` for joints 2 to 7 and the cones. The sheet and the proposal read them, and `cad/tests/test_joints.py` fails when a joint value is set in a second place. Each bonded joint works in two steps: a key, a cone or a pin sets the place in a dry assembly held by screws; then adhesive, the same screws, and filler in the V-groove. The values are proposed. The coupon sets the clearances and the pilot hole.

1. **Skin to skin** (all bonded seams of the walls). An inside flange 6 x 12 on each piece, with a 45 degree gusset, so that it prints with no support. A key 1.5 x 4 on the flange of the piece below, in a groove of the piece above (+0.2 each side). Thread-forming screws 3.0 x 16 for plastics, every 60. The pilot hole is open: 2.25 (the value for PET) or 2.4 (the value for ABS); the coupon decides. A V-groove 1.0 wide and 0.8 deep on the outside takes the filler. This joint is modelled: the coupon (`cad/out/coupon/README.md`, built by `candybar.shell.coupon`) has three pairs on a wall of radius 300, with grooves of +0.1, +0.2 and +0.3, and one pilot of each candidate in each lower half.
2. **Floor tile to floor tile.** A half-lap 20 wide; a cone 8 x 3 in the lower lap; thread-forming screws 3.5 x 12 from below, every 50.
3. **Wall foot to floor.** The foot flange (12 x 4) of each lower piece lies on the floor, with a key 3 x 2.5 under it in a slot of the floor. Thread-forming screws 3.5 x 16 up from below, every 80.
4. **Node** (three pieces meet). A plate 24 x 24 x 4 bonded inside over the three flanges, with a cone in each flange.
5. **Service seam.** M4 heat-set inserts (hole 5.6, 8 deep) in the fixed part, M4 screws every 80 to 100, two pins of 4 (+0.1), a chamfer of 0.5 on both edges. Never bonded or filled.
6. **The coupon pair** for joint 1 (above).
7. **Hood on the body top.** A top ring of 14 on the body, cones 8 x 3 on the ring (two at the front, two at the rear corners), sockets in the foot flange of the hood. Bolted: M4 into inserts in the ring. Bonded: the same faces take adhesive.

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
| Rear corner round | The round of rear_corner_r in plan on each vertical corner of the back, from the floor to the roof of the hood |
| Run-out | Where the step leans into the rear corner round and ends in it, near the body top |
| Body top | The flat top of the body under the hood. The foot of the hood has its outline, so no strip of it is bare. |
| Rail arc | The convex arc of the rail land in side view, from the end of the sweep to the body top |
| Chord | The straight line between the two ends of the rail arc. Its angle is the recline. |
| Tuck | The inward lean of the body sides over the top third of the body, toward the hood |
| Seam groove | The beveled gap between the body and the hood, where one surface passes from one part to the other |
| Bezel land | The outer band of the bezel plate, which follows the rail arc |
| Bezel inner frame | The band of the bezel plate that slopes from the land down to the flat rim at the screen |
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
| ID | Name | Component | Which way it faces | Curvature | What sets it | Joins | How to build it, and the print |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DK1 | deck top border | deck | faces up | flat | deck_top 72; a border of deck_nose 25 in front of the pocket, the same all along the front: the pocket follows the deck's front contour | CP1, DK2, FB1, RL1 | extrusion |
| DK2 | deck edge radius | deck | turns from up to 10 deg off vertical | single-curved; double-curved round the corners | deck_top_r 10.5, turning 80 deg | DK1, DK3 | sweep of the edge section along the deck outline |
| DK3 | deck edge band | deck | leans 10 deg from vertical, faces out | flat; single-curved round the corners | deck_lean 10, crease deck_lean_h 24 below the top | DK2, DK4 to DK7 at the crease | the same sweep |
| DK4 | deck front, centre face | deck | faces the player, vertical | flat | deck_centre_frac 0.56 of the width | DK3, DK5 | extrusion of the deck outline |
| DK5 | deck front, flank | deck | vertical, turned back 8 deg | flat | deck_flank 8 | DK4, DK6 | extrusion of the deck outline |
| DK6 | deck front corner | deck | vertical, round in plan | single-curved | deck_corner_frac 0.09 of the width (R 44.5) | DK5, DK7 | extrusion of the deck outline |
| DK7 | deck side | deck | faces sideways, vertical | flat | at the full width; flush with RL4 | DK6, RL4 (same plane) | extrusion of the deck outline |
| DK8 | panel pocket | deck | the wall faces the pocket, the floor faces up | flat | deck_top - panel_top 2 deep, panel_gap 1 round the panel: six straight edges | DK1, CP1 | pocket cut from the panel outline moved out by panel_gap; the panel plate sits in a seat of panel_t below the floor |
| CP1 | control panel | control panel | faces up | flat | 396 wide, 175 deep at the centre line and 166.4 at the sides, 2 below the deck top; the front is three straight segments 26 behind the centre face and the flanks of the deck (panel_outline) | DK1 | cut plate: straight lines only |
| FB1 | sweep | front body | concave, from up to the foot of the rail arc | single-curved | bend_r 50, turning 68 deg | DK1, FB2, RL1 | extrusion of the side profile across the width |
| FB2 | apron | front body | faces the player; follows the rail arc | single-curved | band_len 40 | FB1, BZ1, RL1 | extrusion of the side profile across the width |
| FB3 | brow band | front body | faces the player; follows the rail arc | single-curved | brow_ledge 32: a plain strip of 28.5 above the bezel, then the seam bevel | BZ1, FB5, RL1 | extrusion of the side profile across the width |
| FB4 | body top | front body | faces up | flat | body_top 423.9; all under the hood: the foot of the hood has its outline | FB3, RL1 to RL3, FB5, RB2, RB5, HC14 | plane cut |
| FB5 | seam bevel, body | front body | faces out and up | flat on the straight runs; single-curved round the corners | seam_groove: from the side 3 below the body top, 3 in to the top; one height all round the body top | FB3, FB4, RL1 to RL4, RB2, RB5 | a ruled cut from the section of the body 3 below its top |
| RL1 | rail land | rail | faces the player; one convex arc in side view, chord reclined 30 deg | single-curved | rail_sagitta_ratio 0.035 of the chord (13.0); 16.0 wide, 9.0 at the top of the bezel | BZ1, FB1 to FB3, RL2, DK1 | extrusion of the side profile; on a print that stands upright the arc is in the layer plane and prints smooth |
| RL2 | rail edge radius | rail | turns from the land to 10 deg off the side | double-curved | same section as DK2; above the start of the tuck, measured in from the side at each height | RL1, RL3, DK2, FB5 | sweep of the edge section along the rail arc; above the start of the tuck the side leans in, so loft between sections there |
| RL3 | rail edge band | rail | leans 10 deg from the side | double-curved | same section as DK3: 13.0 in, crease 24 behind the land; the crease lies on RL4 | RL2, RL4 at the crease, DK3, FB5 | the same sweep and loft |
| RL4 | side band | rail | faces sideways; vertical up to 0.667 of the body height, then leans in on one arc | flat; single-curved above the start of the tuck | body_tuck_ratio 0.023 (11.4 in at the seam, 11.1 deg there), from body_tuck_from 0.667; carries the stripe | RL3, DK7 (same plane), RB2, FB5 | extrusion of the front outline of the side along the depth; a stripe decal lies flat on it |
| BZ1 | bezel land | bezel | faces the player; follows the rail arc, 2 below the rail land | single-curved | 434.7 x 305.4 outside, bezel_land 20 wide | RL1, FB2, FB3, BZ2 | extrusion; print the plate on its long edge, or the back down with layer steps on the land |
| BZ2 | bezel inner frame | bezel | slopes in toward the screen, 16 to 33 deg from the land | flat at the top and bottom; ruled and twisted at the sides | from the land down to a flat rim 2 above the screen | BZ1, BZ3 | loft between the inner edge of the land (an arc) and the rim (a line) |
| BZ4 | bezel reveal | bezel | the walls face the plate, the floor faces the player | single-curved | panel_gap 1 wide at the sides, bezel_drop 2 deep from the rail land to the bezel land | RL1, FB2, FB3, BZ1 | recess cut in the front body; the plate fills it below the bezel land |
| BZ3 | bezel rim wall | bezel | faces the centre of the screen | flat | bezel_rim 2 deep | BZ2, SC1 | extrusion |
| SC1 | screen | bezel | faces the player, flat, reclined 30 deg | flat | 344.7 x 215.4; mon_setback 7.2 behind the chord of the rail, 14.0 to 20.2 behind the rail land | BZ3 | the monitor |
| RB1 | rear body side | rear body | faces sideways; vertical, then leans in with the side band | flat; single-curved above the start of the tuck | 12 in from the side band; it ends where the step runs into the corner round | RB2, RB7 | extrusion of the front outline of the side |
| RB2 | step | rear body | faces out and back, 45 deg in plan, leans 28 deg | flat; twisted above the start of the tuck | foot 138 behind the deck (0.28 W); 12 deep; near the top it runs out into the corner round RB7, 1.2 above the start of the seam bevel | RL4, RB1, RB7, RB9, FB5 | loft between the two edges of the step |
| RB3 | lower rear wall | rear body | faces the rear, vertical | flat | body_d 540 | RB7, RB4, RB6 | extrusion |
| RB4 | rear slope | rear body | faces the rear and down, 45 deg | flat | z 310 to 350 | RB3, RB5, RB7 | extrusion |
| RB5 | upper rear wall | rear body | faces the rear, vertical | flat | rear_proud 40 behind the lower wall | RB4, RB7, FB5 | extrusion |
| RB7 | rear corner round | rear body | turns from the side to the rear, upright; on the slope it leans with it | single-curved: a cylinder on the walls, an oblique cylinder on the slope; a blend where it meets the step | rear_corner_r 18 in plan at every height; tangent to the rear body side and the rear wall, then to the step, and above the step's run-out to the side band | RB1, RB2, RB3 to RB5, RB9, FB5 | a cut by a loft of the round's sections at many heights; prints upright, the round in the layer plane |
| RB9 | step run-out round | front and rear body | turns from the side band to the step | double-curved | a round of the step's outer edge that grows from 0 where the corner round reaches the step (z 385.5) to rear_corner_r where the step runs out (z 422.1) | RL4, RB2, RB7, FB5 | a cut by a loft of the round's sections; at most 1.5 deep: it softens the step's top end into the corner round |
| RB6 | rear door | rear body | faces the rear, vertical | flat | 368 x 188 | RB3 | plate |
| FL1 | underside | floor | faces down | flat | on the desk (feet not designed) | DK4 to DK7, RL4, RB1 to RB3 | extrusion |
| HC1 | hood leg, front face | hood cap | faces the player; leans back 16 deg below the bend, 2 deg above it | single-curved | hood_bar 21 less the soft edge; its outline follows the side | HC4, HC11, HC3, HC15 | the front outline carried along the front of the side view |
| HC2 | hood top bar, front face | hood cap | faces the player; leans back 2 deg | flat | hood_bar 21 less the soft edge | HC4, HC10 | the front outline carried along the front of the side view |
| HC3 | hood sill, front face | hood cap | faces the player; leans back 16 deg | flat | hood_sill_h 17; on the lower part of the front | HC1, HC12, HC15 | the front outline carried along the front of the side view |
| HC4 | hood soft edge | hood cap | turns from the front to the side and the roof | single-curved along the top flat; double-curved along the side and the corner | a quarter circle of 14 (hood_edge_in, hood_edge_back), measured back from the leaning front | HC1, HC2, HC5 to HC7 | sweep of the quarter ellipse along the front outline: an extrusion along the top flat, revolutions round the arcs of the side and the corner |
| HC5 | hood side | hood cap | faces sideways; leans in 11.1 deg at the seam and 13.1 deg at the top corner | single-curved | tangent to the tuck at the seam; hood_side_turn 2 deg on one arc of 7.7 W; no shoulder | HC4, HC6, HC16, RL4 | extrusion of the front outline along the depth; print the cap on its rear face so that this outline is in the layer plane |
| HC6 | hood side blend | hood cap | turns from the side to the roof | single-curved | hood_corner_ratio 0.07: one radius of 34.6 up to the top flat | HC5, HC7 | the same extrusion |
| HC7 | hood roof | hood cap | faces up | flat | hood_flat_h 148 above the foot; 0.713 W wide: follows from the side and the corner; hood_crown_ratio 0: no crown | HC4, HC6, HC8 | the same extrusion |
| HC8 | hood rear arc | hood cap | turns from the roof to the rear | single-curved | conic 95 deep, 110 high from the top of revision 3, cut by the flat top; hood_top_rear_r 10 in the crease | HC7, HC9, HC16 | extrusion of the side profile across the width, cut by the extrusion of the front outline (the common of two extrusions) |
| HC9 | hood rear wall | hood cap | faces the rear, upright | flat | flush with the upper rear wall: hood_shoulder_rear 0 | HC8, HC16, HC15 | extrusion |
| HC10 | hood soffit | hood cap | faces down | flat | under the straight part of the top bar, 3.5 back to the marquee | HC2, HC11, MQ1 | extrusion |
| HC11 | hood leg, inner wall | hood cap | faces the centre line | single-curved | from the front plane back to the band | HC1, HB1, MQ1 | extrusion of the opening outline |
| HC12 | hood ledge | hood cap | faces up | flat | 13.9 deep: what the band leaves of the sill | HC3, HB1 | extrusion |
| HC13 | marquee lip | hood cap | faces the player; its top and bottom face up and down | flat | hood_rail_h 6 high, hood_rail_proud 5 proud: its front is flush with the hood front; its top is an edge of hood_marquee_edge 5 in front of the marquee; ends on the legs | MQ1, HB1, HC11 | extrusion across the width, cut by the opening |
| HC16 | hood rear corner round | hood cap | turns from the side to the rear, then to the rear arc and the roof | single-curved on the rear wall; double-curved round the rear arc, tangent to the roof at the top | rear_corner_r 18 in plan at every height, tangent to the side and to the rear: the body's corner round RB7 carried up, so that the foot of the cap has the outline of the body top | HC5, HC6, HC7, HC8, HC9, HC15 | a cut by a loft of the round's sections at many heights; print the cap on its rear face: the round stands in the layer plane |
| HC14 | hood foot | hood cap | faces down | flat | seam_gap 1.5 above the body top FB4 | HC1, HC3, HC4, HC9, HC15 | plane cut |
| HC15 | seam bevel, hood | hood cap | faces out and down | flat on the straight runs; single-curved round the corners | seam_groove: from the side 3 above the foot, 3 in to the foot; one height all round the foot of the cap | HC1, HC3, HC4, HC5, HC9, HC14 | a ruled cut from the section of the cap 3 above its foot |
| MQ1 | marquee cover | marquee | faces the player, upright: in the plane of the hood band | flat | ends follow the corner of the opening | HC10, HC11, HC13, MQ2 | plate |
| MQ2 | marquee window | marquee | faces the player, upright | flat | straight, 352 x 34, eleven modules of 32 | MQ1 | plate |
| HB1 | hood band | hood band | faces the player, upright | flat | hood_band_recess 5 behind the hood front at its top; foot on the ledge | HC12, HC11, HC13, SP1, LG1 | plate |
| SP1 | speaker form | hood band | faces the player, upright: the speaker fires straight forward | flat | 13 proud; outer end parallel to the leg | HB1, SP2 | extrusion square to the band |
| SP2 | speaker grille | hood band | faces the player, upright | flat | set 1.5 into the form | SP1 | plate |
| SP3 | speaker form walls | hood band | square to the band | flat | 13 high, top edge R 4 | SP1, HB1 | extrusion with a fillet |
| LG1 | logo form | hood band | faces the player, upright | flat | 5 proud | HB1, LG2 | extrusion square to the band |
| LG2 | logo plate | hood band | faces the player, upright | flat | 166 wide | LG1 | plate |
| LG3 | logo form walls | hood band | square to the band | flat | 5 high | LG1, HB1 | extrusion |
<!-- faces:end -->

### The same faces on the references

Only the faces that differ are listed. "Followed" names the reference that the target follows.

| ID | 3D reference model (exact) | Maker's mini (photos) | Real New Astro City | Followed |
| --- | --- | --- | --- | --- |
| DK2, DK3 | No radius. One 45 degree facet, 10.6 x 10.6 (0.039 W). | Radius over 0.11 to 0.13 of the front height, band over 0.20, crease at 0.33 (measured) | Soft edge (estimated) | Maker's mini |
| DK4, DK5, DK6 | Center flat 0.397 W, flanks swept 3.3 degrees, corner radius 0.111 W | Center 0.56 of the width, flanks 8 degrees, corner 0.09 (measured) | Not read | Maker's mini |
| DK7, RL4 | One plane, exact | One plane within 3 mm (estimated) | One plane (estimated) | All |
| RL1 | 4.4 wide (0.016 W). One arc, sagitta 0.091 of the chord. | About 0.05 W (estimated). Straight (measured). | Broad (estimated). Arc not measured. | Own: 16.0 wide (0.032 W), on an arc of 0.035 of the chord. See question 8. |
| RL4 | Vertical to the seam | Leans in 0.010 ± 0.006 W over the top quarter (measured) | Leans in up to 0.018 ± 0.006 W over the top 0.22 (measured) | Own: 0.023 W over the top third, by the owner's choice. See question 9. |
| RL2, RL3 | No radius. A 45 degree facet 10.6 wide (0.039 W). | A soft radius, about 0.015 W. A band is not visible (uncertain). | A large soft edge (estimated) | Own: the deck's edge section. See question 1. |
| RL5 (inner wall of the cheek) | 20 to 31 deep | None: the bezel is about flush | Deep (CRT) | Maker's mini: no such face |
| FB1 | Fillet R 3.9 | A sweep (estimated) | A large sweep | Own value: R 50 |
| FB2 | A 43.5 degree facet, 18.4 on the slope | A white band under the bezel (estimated) | None | Own value: 60, set by the owner |
| RB2 | 20 deep (0.074 W), 28.2 degrees | Depth 0.01 to 0.03 W (uncertain), 27.8 degrees | Not visible (uncertain) | Angle and position: both. Depth: own, 12. See question 3. |
| RB4, RB5 | The upper rear leans forward 11.6 degrees and is as wide as the cheeks | The upper rear stands proud of the lower rear (estimated) | Not read | Maker's mini in kind |
| RB8 (rear lower facet) | 43 degrees, 30.6 deep, 28.8 high | Present (estimated) | Not comparable | Left out: the power supply stands there |
| FB4 | Shoulder 1.4 (0.005 W) | Shoulder 0.030 ± 0.012 W (photo-b, measured); a small lip in photo-g | None at the sides: one line over the seam (owner-ref-1, measured) | Real cabinet, by the owner's direction: no shoulder at the sides, a groove |
| BZ1, BZ2 | A flat plate, 6 to 26 behind the cheeks | A flat land and a sloped inner frame (estimated) | A deep surround | Maker's mini in kind, on the rail arc |
| HC1 | Leans 37 to 43 degrees, continues the cheek | Near upright, 0.03 W wide (measured) | Near upright (estimated) | Maker's mini |
| HC2, HC4 | Top bar 15 thick (0.056 W). The top front edge is a 42 degree facet. | Top bar 0.037 W (measured), one soft edge | The lit strip fills the brow | Maker's mini in kind; 21 thick (0.042 W) |
| HC3, HC12 | None: the band starts at the seam | Ledge zone 0.088 W (measured) | Ledge zone 0.06 W (measured) | Maker's mini |
| HC5, HC6 | Arc R 1.29 W, 13.5 to 22 degrees; corner R 0.074 W | About 6 degrees, then one long blend (estimated) | 11 to 19 degrees (measured ± 3 in owner-ref-1), then a tight corner of 0.06 to 0.07 W (measured) | Real cabinet, by the owner's choice: 11.1 to 13.1 degrees, then a corner of 0.07 W |
| HC7, HC8, HC9 | Top flat 30 deep; rear leans forward 16 degrees | Almost no flat; one arc down the rear (estimated) | Not read | Maker's mini |
| HC13 | None | A white zone 0.043 W under the strip (uncertain: lip or top of the band) | A dip of 0.02 W | Own: a lip 6 high |
| MQ1, MQ2 | An upright strip 12.4 high (0.046 W), 15.9 behind the nose of the top bar | 0.049 W high, under the top bar, tilted down (estimated) | 0.16 W with the brow | Owner's rule: 34 high for the display, upright, in the plane of the hood band |
| HB1 | Leans 44 degrees | Leans less (estimated) | Not read | Owner's rule: upright, 5 behind the hood front at its top |
| SP1 to SP3 | Pods 0.204 x 0.147 W, fronts upright | Pods 0.176 x 0.163 W, fronts upright, 0.12 W deep | Pods 0.19 x 0.145 W at the ends | Owner's rule: forms 13 proud, fronts upright (the speakers fire straight forward) |
| LG2 | Recess 0.260 x 0.187 W | 0.369 x 0.133 W (measured) | About 0.30 x 0.125 W | Maker's mini: 0.34 x 0.10 W |

Uncertain readings, all on the maker's mini: the edge of the rail (RL2, RL3), the depth of the step (RB2), the seam on the front of the hood (HC3, FB3), the white zone under the lit strip (HC13 or HB1), the surface beside the right pod (SP3 or HB1), and the rear wall in the side trace.

## Open questions for the owner

Questions 1 to 7 are from revision 1. They are still open. The note says what revision 2 does to each.

1. **Edge of the rail.** The blueprint runs the deck's whole edge section (radius, 10 degree band, crease 24 mm behind the land) up the rail to the hood. The maker's mini shows only a soft radius on the rail (about 8 mm at this size). Whole section, or radius only? *Still open.*
2. **Land of the rail.** It is 16 mm (0.03 W). The maker's mini has about 0.05 W (25 mm at this size). Keep 16, or widen the cabinet by about 18 mm? *Still open, and it matters more now: the tuck makes the land narrow at the top of the bezel. Revision 5 moves the screen 12 down the face, and the land there is now 9.0 mm (it was 7.5).*
3. **The crease behind the stripe.** A step 12 mm deep, deeper (3D model 20), or only a shallow line? *Still open. Its reason changed: revision 1 made it equal to the shoulder of the hood, and that shoulder is gone.*
4. **Depth.** The hood is 140 mm deep at the seam (0.28 W) and the cabinet 580. Enough, or deeper (0.30 W gives a cabinet of 595)? *Answered 2026-11-10: keep 580. The owner's words: "We probably don't want to deepen it unless we deepen the whole cabinet - but I don't think we need to as I want it to actually fit on a surface somewhere."*
5. **Legs and top bar of the hood.** They are 21 mm (0.042 W). Keep 21? *Still open.*
6. **Marquee.** It sat 38 mm under the top bar and faced down 18 degrees. A standing person did not see its top. Accept? *Answered 2026-11-10 by the answer to question 14: the marquee is now upright, 3.5 behind the front of the top bar.*
7. **Rear.** The rear lower facet and the rear corner facets of the references are left out. Accept for now? *Answered in part 2026-11-10. The owner accepted the rear as built ("It's in the state that I meant, this looks good") and asked for a fillet on the vertical corners of the back surface in a detail pass. The facets stay left out. Revision 6 builds the fillet: a round of 18 on each vertical corner of the back, from the floor to the roof of the hood (see "Revision 6").*

New in revision 2, answered in revision 3:

8. **Rail arc.** Drawn at 0.035 of the chord (13 mm). The maker's rail is straight. The 3D model has 0.091 (33 mm at this size). Which amount? *Answered 2026-11-10: 0.035. The owner's words: "Rail arc, I like the second, subtle but it reads obvious to human eyes."*
9. **Tuck.** Drawn at 0.015 W (7.4 mm on each side at the seam). The maker's mini has about 0.010, the real cabinet at most 0.018. Which amount? *Answered 2026-11-10: 0.023 W (11.4 mm), over the top third of the body (from 0.667 of its height, 11.1 degrees at the seam). The owner's words: "For the arc toward the hood, agree, 4th", and "I like how 2 arcs just over the top 3rd of the body".*
10. **Side shoulder.** Revision 2 has none: the hood meets the body in one line with a groove, as in your photo of the real cabinet. The maker's mini has a small lip there. Is none correct? *Answered: yes, none. The owner's words: "the hood and body meet in one smooth curve with a bevel cut between them".*
11. **Hood side.** It carries on the arc of the tuck and then blends into the top as on the maker's mini. The real hood leans more and has tighter top corners. Keep the long blend? *Answered 2026-11-10: no. The owner's words: "lean towards the real cabinet, out of all the options drawn, 2 on the bottom row is the least domelike, somewhere between 2 and 4 for the front on view of the hood", and "4 has better proportions at the top of the hood". Revision 3 has a near-straight side (11.1 to 13.1 degrees), a top corner of 0.07 W and a top flat of 0.705 W.*
12. **Bezel.** A land of 20 mm that follows the rails, then an inner frame of 25 mm that slopes to the screen. The screen is 25 to 31 mm below the rails. Accept this depth? *Answered 2026-11-10: move the screen forward. The owner's words: "Sounds good on the bezel depth though the inset is probably a little different because I chose 2." The screen is now 14.0 mm below the rail land at the top of the window, 20.2 at the center and 17.7 at the bottom.*

New in revision 4:

13. **Depth of the upright hood band.** Three places, drawn in `cad/out/shell-bp/compare/hood-band-options.png` (side section through a speaker). (a) Recessed, as built: the band face is 5 behind the hood front at the top of the band, the ledge is 13.9, and the speaker fronts are 0.2 to 7.8 ahead of the hood front. (b) Flush at the top of the band: the ledge is 8.9, and the speaker fronts are 5.2 to 12.8 ahead of the hood front. (c) Proud, from the front edge of the sill: there is no ledge, the band face is 8.9 ahead of the hood front at its top, and the speaker fronts are 14.1 to 21.7 ahead of it, as a small version of the box on the real cabinet. Which one? *Kept at (a) on 2026-11-10. The marquee is now in the plane of the band, so (b) and (c) put the marquee 1.5 and 10.4 ahead of the top bar. The owner was told this and did not ask for a change.*
14. **Shelf under the marquee.** The lip moves forward with the band, but the marquee does not move. Thus the top of the lip is a flat shelf 36.5 deep (in a). To make it shorter, move the marquee forward (a smaller soffit) or make it face down less. Accept the shelf? *Answered 2026-11-10: no. The owner's words: "I think we can make the marquee 90 face directly forward as well, then bring it forward and just leave a small edge below it?" The marquee is now upright, with an edge of 5 on the lip.*

## How to draw the sheets again

```sh
cad/.venv-tools/bin/python cad/tools/draw_blueprint.py target      # docs/blueprint, and the two tables in this file
cad/.venv-tools/bin/python cad/tools/draw_blueprint.py band-options  # three depths of the hood band, to cad/out/shell-bp/compare
cad/.venv-tools/bin/python cad/tools/draw_blueprint.py screen-drop-options  # the screen face for drops of 8, 12 and 16, to cad/out/shell-bp/compare
cad/.venv-tools/bin/python cad/tools/draw_detail.py rear-options      # the rear corner round for three radii, to cad/out/shell-bp/compare
cad/.venv-tools/bin/python cad/tools/draw_detail.py before-after      # renders of revision 5 and 6 side by side
cad/.venv-tools/bin/python cad/tools/draw_detail.py detail-options    # the remaining small questions of the form
cad/.venv-tools/bin/python cad/tools/draw_blueprint.py reference   # the 3D reference model, to cad/out
cad/.venv-tools/bin/python cad/tools/draw_blueprint.py photos      # the face IDs on the photos, to cad/out
cad/.venv-tools/bin/python cad/tools/draw_blueprint.py compare     # side profiles over each other, to cad/out
cad/.venv-tools/bin/python cad/tools/draw_blueprint.py overlays    # the blueprint's silhouette on the annotated photos, to cad/out
```

`reference` needs the slices of the model: run `candybar.shell.reconstruct_slices` with `cad/candybar/freecad-run.sh` (the example is at the top of that file). `photos` reads the picks in `cad/out/shell-d/reconstruction/face-picks.json`.

## How to build and check the solids

```sh
CANDYBAR_OUT=cad/out/shell-bp cad/candybar/freecad-run.sh candybar.shell.solids   # one STL and one BREP for each part, a STEP of all parts, the manifest, the report
CANDYBAR_OUT=cad/out/shell-bp cad/candybar/freecad-run.sh tools.check_solids      # the solids against the faces; exit status 1 when a distance is more than 0.5 mm
CANDYBAR_OUT=cad/out/shell-bp cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc   # shell.FCStd with colours, to open in FreeCAD
python3 cad/tools/render_views.py cad/out/shell-bp/renders cad/out/shell-bp        # the fixed views (both rear three-quarters) and the close-ups of the junctions
CANDYBAR_OUT=cad/out/shell-bp cad/candybar/freecad-run.sh candybar.shell.fit      # the fit study (about 10 minutes); exit status 1 when an item does not fit
cad/.venv-tools/bin/python cad/tools/draw_blueprint.py fit                          # sheet 09 from the fit study
cad/.venv-tools/bin/python cad/tools/draw_split.py blueprint                       # sheets 10 and 11, from the cut of the split and joints.py
python3 cad/tools/render_views.py cad/out/shell-bp/fit/renders cad/out/shell-bp/fit/cutaway --views three-quarter-front-left,three-quarter-rear-left   # the cut-away
```
