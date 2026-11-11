# Measurements from the reference photos

Research date: 2026-11-09. Scope: form of the reference cabinet (the maker's New Astro City mini) and of the real Sega New Astro City, read from photos with the photo tools in `cad/tools/`. Every picked point, probe and known dimension is in `cad/reference/<photo>.json`. Each file names its photo by path and SHA-256. The evidence images are in `cad/out/photo-evidence/<photo>/` (ignored by git). To re-run a number, run the tool on the annotation file named in its row.

## How to read the numbers

`W` is the width of the body of the reference cabinet outside the cheeks at screen height: 246.9 ± 2.4 mm. This is MEASURED in `photo-b.json` in the screen plane, which is scaled by the lit 8 inch 4:3 image (162.56 × 121.92 mm). A ratio is a length divided by `W` of the same cabinet. For the real cabinet, `W` is replaced by the width of the hood front (see B).

| Tag | Meaning |
| --- | --- |
| MEASURED (tool, file) | Computed by the tool from the picks in the file. The ± is from moving each picked point by its sigma (1 to 4 px) and combining the changes as a root sum of squares. The text names any extra systematic error. |
| ESTIMATED | A reading or a calculation that needs an assumption. The assumption is given. |

Tools: `photo_detail.py` (brightness profiles), `photo_rectify.py` (planes and measures), `photo_overlay.py` (model against photo), `photo_profile.py` (side views: level, scale, measure, overlay), `photo_annot.py` (picks, crops, snapping). A focal length that is not measured is a stated assumption. Where it matters, the number is given for a range of focal lengths.

## A. The deck front edge (reference cabinet)

Method: three vertical probes down the deck front in `photo-b.png` (nearly frontal), at x = 120, 200 and 280 px. MEASURED with `photo_detail.py` from `photo-b.json`, region `deck-front`. Sheet: `photo-b/detail-deck-front.png`. The span of each probe runs from where the radius starts (the end of the plateau of the deck top border) to the bottom edge. Its two ends are picked with sigma 2 px and 1 px. The span is 60 px, so one pixel is 0.017 of the span.

| Feature, from the top border down | Probe 1 | Probe 2 | Probe 3 | Reading |
| --- | --- | --- | --- | --- |
| Radius: a highlight that rises and falls | 0 to 0.14 | 0 to 0.13 | 0 to 0.13 | 0.13 ± 0.03 of the front |
| Band: a plateau as bright as the deck top border (178 to 187) | 0.14 to 0.30 | 0.13 to 0.28 | 0.13 to 0.28 | 0.15 to 0.16 flat, 0.20 ± 0.03 to the crease |
| Crease: a sharp step down (centre) | 0.339 | 0.333 | 0.325 | 0.333 ± 0.02 |
| Lower face: a plateau (101 to 121), flat within 1 to 2 levels | 0.39 to 0.96 | 0.38 to 0.96 | 0.38 to 0.96 | 0.67 ± 0.03 |
| Bottom edge | 1.00 | 1.00 | 1.00 | |

Correction for the view: the camera looks down about 27 ± 5 degrees. This is ESTIMATED from the lit screen, which appears as an undistorted 4:3, so the view is square to the reclined screen face. A vertical face then appears shortened by cos 27 = 0.89 and a band that leans 10 degrees by cos 17 = 0.96. Corrected, the true heights are about: radius 0.11, band 0.20, vertical face 0.69. ESTIMATED, ± 0.03 each.

Cross-checks:

- `photo-e-three-quarter.png`, three probes (`photo-e-three-quarter/detail-deck-front.png`): the upper zone (deck top, radius and band together, 235) ends in one step 6 to 8 px wide (the crease). Below it the face holds 215 to 216 ± 0.5 levels over 60 px. MEASURED.
- `photo-d-unpainted-shell.png`, three probes (`photo-d-unpainted-shell/detail-deck-front.png`): the step from 220 to 186 is 5 to 6 px wide. Below it the face holds 185 to 189 ± 1 over 37 to 42 px. MEASURED.
- In both photos the lower face is one flat surface. A curved face would show a gradient, and none shows.

Answer:

- The owner's reading holds. From the top down: a soft radius over about 0.11 to 0.13 of the front, a band over about 0.20 (a fifth, a little less than the owner's quarter), a sharp crease at 0.33 from the top, and a flat lower face over the remaining two thirds.
- Not measured: the angle of the band and whether the lower face is exactly vertical. A single view cannot give these without a known reference in that face.
- One caution: in all three photos the band is as bright as the deck top and much brighter than the lower face. Under an overhead light, that fits a lean larger than 10 degrees. A reflection of a bright ceiling on gloss white gives the same result, so the brightness does not prove a steeper lean. ESTIMATED: 10 to 25 degrees.

## B. The hood

Sources: widths of the reference cabinet come from `photo-b.json` (screen plane, MEASURED with `photo_rectify.py`). Heights come from `photo-e-three-quarter.json`, in the plane spanned by the cabinet's width direction and the vertical (MEASURED with `photo_rectify.py`, plane `front`). Each height is first divided by the width of the right speaker pod in the same plane, then multiplied by pod width / W from photo-b (0.176). The vertical lines in photo-e are parallel within 0.5 degrees, so the camera is level. The principal row is taken on the horizon (y = 129). The focal length 2268 px comes from the bezel outline with the aspect ratio of photo-b, but this fit is weak (see Limits). A focal length of 1900 to 2700 px changes every height by ± 9 percent, and that error is included in the ± below. The real cabinet comes from `photo-real-three-quarter.json`, in the plane of the two pod fronts. That plane needs an assumed focal length of 900 px (26 mm equivalent, an uncropped phone photo). 750 to 1100 px changes heights by ± 8 percent, which is included. Its ratios are to the width of the hood front at the pods, about 0.95 to 1.0 of the body width (ESTIMATED). The reference model values are MEASURED from the mesh in `docs/research/mini-new-astro-city-geometry.md` §6.6 (W = 270 mm).

| Quantity (ratio to W) | Real New Astro City | Reference cabinet (maker) | 3D reference model |
| --- | --- | --- | --- |
| Hood height: top front edge to top of bezel | 0.36 ± 0.04 (top seen in silhouette) | 0.35 ± 0.04 | 0.280 (0.256 seam to top) |
| Top bar (brow), front face height | Lit strip fills the brow: brow and strip together 0.16 ± 0.02 | 0.037 ± 0.006 | 0.056 thick, nose 5.45 mm high |
| Legs of the arch, front face width | not measured (left leg seen from the side) | 0.029 ± 0.008 | 0.056 (side walls) |
| Top corner radius, seen from the front | not measured | 0.23 ± 0.03 (one large curve that blends into the leaning side; ESTIMATED as a radius) | 0.074, sides lean 13.5 to 22 degrees |
| Lit marquee strip, height / width | see the brow row; width about 0.9 | 0.049 ± 0.006 / 0.82 ± 0.02 | 0.046 (vertical strip) / about 0.71 |
| Strip position | top of the hood front | directly under the brow, 0.037 below the top edge | under the brow |
| Strip setback behind the brow | not measured | ESTIMATED 0.04 to 0.08 (photo-e: the brow's under face is visible) | 0.059 |
| Recessed band, strip bottom to logo plate top | about 0.02 (the dip under the strip) | 0.043 ± 0.005 | 0.215 along a 44 degree slope |
| Speaker pod width × height | 0.19 ± 0.01 × 0.145 ± 0.02 | 0.176 ± 0.006 × 0.163 ± 0.02 | 0.204 × 0.147 |
| Pods, outer span (centres) | 0.89 ± 0.02 (± 0.35) | 0.753 ± 0.015 (± 0.289) | 0.748 (± 0.272) |
| Pod projection | not measured | ESTIMATED 0.12 ± 0.04 deep boxes (photo-e side faces) | 0.011 ahead of the bezel top |
| Logo plate width × height | about 0.30 × 0.125 ± 0.015 | 0.369 ± 0.008 × 0.133 ± 0.015 | marquee recess 0.260 × 0.187 |
| Logo plate tilt | not measured | not measured | 44 degrees (whole band) |
| Shoulder (hood side inset from body side) | ESTIMATED 0 to 0.03 | 0.030 ± 0.012 each side | 0.005 |
| Ledge: logo plate bottom to top of bezel | 0.06 ± 0.01 | 0.088 ± 0.01 | 0 (speaker plate flush with the bezel) |

Differences that matter:

- **Pods.** The real cabinet puts its pods at the very ends of the hood front (outer span 0.89). The maker and the model keep them inboard (0.75), with a leg of the arch outside each pod.
- **Brow and strip.** The real cabinet's lit strip is the whole brow, a tall lit band (0.16 together). The maker's cabinet has a thin white brow (0.04) with a separate lit strip of 0.05 under it.
- **Height.** Both cabinets have a hood about 0.35 W tall above the bezel top. The model is lower (0.28).
- **Ledge.** The maker's cabinet has a white ledge about 0.09 W tall between the logo plate and the bezel. The real cabinet's ledge is about 0.06. The model has none.
- **Pod depth.** The maker's pods are deep boxes. The model's pods barely stand forward.

## C. The rail beside the bezel (reference cabinet)

Sources: `photo-e-three-quarter.json`, region `rail`, three probes across the right rail at y = 700, 800 and 900 (sheet `photo-e-three-quarter/detail-rail.png`). Cross-check: the right cheek in `photo-b.json`.

| Quantity | Value | Tag |
| --- | --- | --- |
| White front land, width / bezel width | 0.07 ± 0.02 | MEASURED, `photo_detail.py` rail probes. Bezel edge to the first line of the facet is 30 px. The bezel width at the same height is about 393 px, at nearly the same depth. |
| Stripe facet, width on its own surface / bezel width | 0.18 ± 0.05 | ESTIMATED. The facet is 100 px wide in photo-e and is seen nearly square on. It is scaled by the land, which is foreshortened by cos 42 degrees. |
| Land and facet seen from the front / bezel width | 0.11 ± 0.01 | MEASURED, `photo_rectify.py`, `photo-b.json` (`cheek_right_mm` / `bezel_w_mm`). |
| Bezel front behind the land | about 0 (flush), ≤ 2 mm | ESTIMATED. The near-side bezel edge in photo-e departs from a straight line by 3.4 px over 400 px. The bezel plate is flat, so the land is no more than about 1 to 2 mm proud of it at mid height. This supports the owner's "flush". |
| Screen inset in the bezel | 12 ± 6 mm (0.06 of the bezel width) | ESTIMATED from parallax in photo-b. The screen centre is 3.5 px right of the bezel centre, and the camera is about 13 degrees to the right. |
| Deck side against the lower end of the facet | The facet runs to the table in its own plane, and the deck sits in front of it. Confidence about 70 percent. | Reading of `photo-e-three-quarter/detail-cheek-foot.png`. Both boundary lines of the facet and the stripe's end bars run straight and unbroken to the carpet (probes foot-1 to foot-4). No line turns along the deck. The deck's white side meets the facet's front boundary line and does not wrap it. Doubt: at y = 1280 to 1320 the deck top is close in brightness to the facet, so a short return of 1 or 2 mm cannot be excluded. |

## D. The deck front in plan (reference cabinet)

Method: `photo_rectify.py` with the plane `top` in `photo-d-unpainted-shell.json`. The plane comes from the button holes: the tool finds the hole outlines (threshold 215, so the lit inner wall counts as hole) and fits the homography that makes them round. 8 holes are found and the lever hole is dropped as an outlier. Check 1: roundness (max − min)/(max + min) of the hole ellipses falls from 0.18–0.27 to 0.010–0.032 for the six large holes, and their diameters agree within ± 4 percent. Two holes are smaller by 20 to 30 percent: they appear to be the 24 mm holes. Check 2: the recess for the control plate comes out at 88.2 ± 1.3 degrees between its left and front edges. The deck front edge was traced at 25 columns: each point is the step from the deck top (216) to the front face (186). Sheet: `photo-d-unpainted-shell/rectified-top.png`, which shows the faces, the recess and their angles. Cross-check: a horizontal probe along the deck front in `photo-b.json` (`photo-b/detail-deck-plan.png`).

| Quantity | Value | Tag and trust |
| --- | --- | --- |
| Centre face width / deck width | 0.56 ± 0.02 | MEASURED, photo-b. The brightness steps on the front face at x = 88 and 269 are the bends. The deck spans x = 30 to 352. Both lie at the same depth, so the ratio does not depend on the scale. Good. |
| The same, from photo-d | 0.54 ± 0.05 | ESTIMATED: centre face 922 plane units between the fitted bends, left flank and corner measured, right side taken as a mirror of the left. |
| Left flank, angle to the centre face, in the deck top plane | 8.1 ± 2.5 degrees, turning back toward the corner | MEASURED, `angle_lines`. ± 1.4 from the picks, plus about 2 from the hole fit. Fair. |
| Right flank, the same | 8.4 ± 3 degrees | MEASURED, five trace points only. Fair. |
| Flank length (bend to the start of the corner) | about 57 mm, 0.19 of the deck width | ESTIMATED: 312 plane units, scaled by 30 mm holes (0.18 mm per unit). |
| Front corner radius in plan | about 29 mm, 0.09 ± 0.03 of the deck width | ESTIMATED: the trace turns 17 degrees per 49 units (R about 160 units). Only three points lie in the corner. Low trust. |
| Recess front edge, angle to the centre face | 0.9 ± 0.6 degrees | MEASURED. The recess and the plate stay rectangular and square to the centre face. They do not follow the flanks. Fair: the recess groove is faint (6 levels). |
| Deck sides | Left side within about 4 degrees of square to the centre face, so parallel. Right side not measured. | ESTIMATED from two picks. Low trust. |
| Deck width | about 310 ± 25 mm, 1.25 W | ESTIMATED: 1700 plane units at 0.18 mm per unit. The deck is wider than the body, as section 1 of `cabinet-references.md` says. |

The owner's description holds: a centre face square to the player, about half the width (0.54 to 0.56). Two flanks turn back about 8 degrees, then a rounded corner.

## E. The real cabinet in profile (owner-ref-4)

Photo: `cad/vendor/sega-new-astro-city/owner-ref-4-profile.png` (540 × 720), a true side view of a real New Astro City (a floor cabinet), front to the right. The picks and traces are in `cad/reference/owner-ref-4-profile.json`. Tool: `photo_profile.py` (`measure` gives the table, `overlay` gives the pictures in `cad/out/shell-d/reconstruction/`).

Scale. The floor line sets the level (the floor tilts 0.3 degrees in the photo). The height (floor to hood top, 1445 mm) gives 2.374 mm per px. The depth (rear wall to deck front, 905 mm) gives 2.457 mm per px. The service manual gives both sizes [S33]. The two scales differ by 3.5 percent: this is the error from perspective. Each line is also computed with one scale on both axes; the "range" column gives the spread. The traces are snapped to edges (sigma 1 px). Short lengths carry about ± 1.5 px more: ± 0.006 W on the hood parts and ± 0.007 W on the overhang. A check: the deck top reads 626 mm above the floor. Owners measure 650 mm, so the photo reads about 4 percent low.

`W` is the body width: 750 mm for the real cabinet, 494.7 mm for this cabinet. The real cabinet is a floor cabinet with a 29 inch tube. Compare the shape, not the sizes.

| Line | Real cabinet (MEASURED) | Range | This cabinet | Difference |
| --- | --- | --- | --- | --- |
| Rail arc, sagitta / chord (chord from the top of the sweep to the seam) | 0.033 | 0.032 to 0.033 | 0.035 | +0.002 |
| Recline of the rail chord, degrees from upright | 29.1 | 28.3 to 29.1 | 30.1 | +0.9 |
| Rail arc radius / W (circle fit, rms 1.8 mm) | 2.97 | 2.97 to 3.10 | 2.69 | -0.28 |
| Sweep radius / W | 0.143 | 0.141 to 0.146 | 0.101 | -0.042 |
| Rail chord / W | 0.849 | 0.842 to 0.871 | 0.749 | -0.100 |
| Seam (foot of the hood) above the deck top / W | 0.872 | 0.872 to 0.902 | 0.714 | -0.158 |
| Hood height over the seam / W | 0.220 | 0.220 to 0.227 | 0.317 | +0.097 |
| Hood depth at the seam / W | 0.325 | 0.314 to 0.325 | 0.269 | -0.056 |
| Hood front beyond the rail top at the seam / W | 0.018 | 0.018 | -0.008 (4 behind) | -0.026 |
| Front box of the hood (speakers and marquee): top above the seam / W | 0.103 | 0.103 to 0.107 | none | |
| Front box: depth in front of the upper part / W | 0.097 | 0.093 to 0.097 | none | |
| Step from the top of the front box up to the hood top / W | 0.116 | 0.116 to 0.120 | 0 | -0.116 |
| Flat hood top, depth / W | 0.147 | 0.142 to 0.147 | 0.012 | -0.135 |
| Hood rear: lean forward from upright, degrees (straight) | 17.6 | 17.1 to 17.6 | 0: an arc down to an upright wall | |
| Body rear wall above the deck: lean forward from upright, degrees | 13.6 | 13.1 to 13.6 | 0: upright, the upper rear 40 proud | |
| Side band: rail edge to the step, at mid rail / W | 0.326 | 0.315 to 0.326 | 0.336 | +0.010 |
| Rail edge to the line behind it, at mid rail / W | 0.159 | 0.154 to 0.159 | 0.056 (the crease) | -0.104 |
| The same at a quarter and at three quarters of the rail height / W | 0.165, 0.137 | ± 0.005 | 0.054, 0.058 | |

What the profile shows:

- **Rail.** A concave sweep at the deck, then one convex arc to the seam. The arc fits one circle with an rms error of 1.8 mm. Its sagitta is 0.033 of the chord (0.032 to 0.033 when the lower end moves 24 px). This is the value that the earlier photos could not give. It agrees with this cabinet (0.035) within the error. The real chord reclines 29 degrees (this cabinet: 30).
- **Hood.** Two parts with a step. A front box (speakers and marquee) stands over the top of the rail. Its front is upright and 0.018 W in front of the rail top. Its top is 0.10 W above the seam. Behind it, a taller upper part rises to 0.22 W. Its front is near upright (6 degrees) and its top is flat for 0.15 W. Its rear is straight and leans forward 17.6 degrees, with small corners. There is no rear arc. The step between the two tops is a near-upright face, not a slope. The hood is 0.325 W deep at the seam and 0.22 W high: it is deeper and lower than this cabinet's (0.269 W, 0.32 W).
- **Rear.** Above the deck, the rear wall of the body leans forward 13.6 degrees. It runs into the hood rear (17.6 degrees) in almost one line, so the profile narrows to the top. Below the deck the base is set in by about 0.09 W.
- **Side band.** The step face shows as a dark band. Its inner edge is sharp, and it leans back 25 degrees (this cabinet: 28). From the rail edge to it is 0.33 W at mid rail, close to this cabinet. A thin line runs 0.14 to 0.17 W behind the rail edge. It is straight, but the rail edge curves, so the band between them is narrowest at the top. It is a crease or a joint of the side panel (not determined). This cabinet's edge crease is 24 mm (0.05 W) behind the land.

Not measured: the width of anything (one view), the outer edge of the step band (a soft shade), how the front box meets the rail top (in shadow), the depth of the seam groove, and the shape of the hood front in plan.

## Model against photo

`photo_overlay.py` on `photo-e-three-quarter.json`, with the 3D reference model (`photo-e-three-quarter/overlay-full/` and `overlay-plane/`). The full fit uses six anchors: the four bezel corners, the deck front centre and the hood top centre. Its rms error is 35 px, because the model has different proportions. The fit on the screen face alone matches the four bezel corners at 10 px rms. With that fit, the model's deck front lands about 83 px below the photo's and its hood top 71 px off. The model's steeper recline (32.5 degrees) and lower hood show directly.

## Limits

- One view gives no absolute angles of surfaces without a known shape in them. The band lean (A) and the verticality of the lower deck face are not measured.
- Photo-e and photo-d are screenshots, probably cropped, so the principal point is not known. The camera of photo-e rests on the bezel outline and the horizon. Its recline estimate (12 degrees from the bezel plane, 24 to 30 degrees from the bezel side edges) is not consistent, so photo-e gives no recline. Its heights carry ± 9 percent for the focal length.
- The real cabinet has two photos. In the three-quarter view the camera is an assumed phone lens. The profile view (E) needs no camera model, but its two scales differ by 3.5 percent.
- A point used in a plane must lie in that plane. Widths taken in photo-b's screen plane for parts in front of it (deck, hood front) read about 2 to 4 percent large.
- **Least trusted:** the maker's top corner radius (0.23 W). The front silhouette in photo-b is one long blend from the top flat into the leaning side, so "a radius" fits it poorly. Next: the facet width in C, which depends on an assumed facet angle.
- Monocular depth and normal estimators: not attempted. The time went to the three measuring tools and question D. The flat plateaus in A (± 0.5 levels on gloss white) give such a model little to read. A 10 degree lean would not show without specular cues.
