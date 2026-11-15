# The hood band: speaker grilles, marquee and logo field

Date: 2026-11-14. State: a design study with three variants on the hood as it is, and two studies of a taller hood. The owner chooses.

The hood band is the strip across the front of the hood. The default build has four stand-ins there: `marquee_lip`, `speaker_left`, `speaker_right` and `logo_form`. This study replaces them with designed parts. The module is `cad/candybar/shell/hood_band.py`. It does not change the outer form: the cap of the hood is the cap of `solids.py`, and each opening of the band is a cutter that the module makes.

All lengths are in mm. `W` is the width of the cabinet, 494.7. In this document, z is the height above the foot of the hood (the hood stands on z 425.36 of the cabinet), and x is the distance from the centre line.

## 1. What the references have

The sources are `docs/research/photo-measurements.md` (section B), `docs/research/mini-new-astro-city-geometry.md` (section 6) and the photos in `cad/vendor/`. The column "at this size" is the ratio multiplied by 494.7.

| Item | Real cabinet | Maker's mini | 3D reference model | At this size |
| --- | --- | --- | --- | --- |
| Lit strip, height | 0.16 W with the brow | 0.049 W | 0.046 W | 24 (maker) to 79 (real) |
| Lit strip, width | about 0.9 W | 0.82 W | about 0.71 W | 351 to 445 |
| Lit strip, place | It is the brow of the hood | Under the top bar, set back | Under the top bar, 15.9 behind its nose | |
| Speaker pod, width x height | 0.19 x 0.145 W | 0.176 x 0.163 W | 0.204 x 0.147 W (55.1 x 39.8) | 87 to 101 wide, 72 to 81 high |
| Pod centres from the centre line | 0.35 W | 0.289 W | 0.272 W (73.5) | 135 to 173 |
| Pod depth | Not measured | About 0.12 W (estimate) | 0.011 W ahead of the bezel top | 5 to 59 |
| Pod front | A square black field with a round driver behind it | A square black cloth field | An open front, 48.0 x 33.0, with a separate grille | |
| Logo plate, width x height | About 0.30 x 0.125 W | 0.369 x 0.133 W | Recess 0.260 x 0.187 W | 148 to 183 wide, 62 to 66 high |
| Logo plate, form | A tilted plate with printed art between the pods | A tilted black plate with art, four screws | A recess for a small display | |
| Band tilt | Not measured | Less than the model (estimate) | 44 degrees | |

What the photos show, in words:

- **Marquee.** A translucent strip with art, lit from behind. On the real cabinet it fills the brow. On the maker's mini it lies under a thin top bar.
- **Speakers.** Two white pods stand forward of the band, one at each end. The front of a pod is upright and square, with a black field. The grille is cloth or mesh, not slots.
- **Logo.** A plate with printed art between the pods. It is a separate plate with visible screws.
- **A second cabinet of the same maker** (the wide cabinet in `photo-a.png`) has no pods. Its band is flat, with level slots on each side of a badge. Variant B follows this idea.

The owner set three rules before this study (`docs/blueprint/index.md`): the band is upright, the speaker fronts follow the contour of the hood, and the marquee is upright with a small edge below it.

## 2. The space in this hood

| Value | Size | Source |
| --- | --- | --- |
| Band wall, front | 18.77 behind the foot of the hood front, upright | `profiles.hood` |
| Band height | 67.9 (z 17.0 to 84.9) | `profiles.hood` |
| Band width | 419.9 above the corner rounds of the sill, 393.4 at the lip | `Hood.half_open` |
| Lip | z 84.9 to 90.9 | `profiles.hood` |
| Marquee opening | z 90.9 to 127.0 (36.1 high) | `profiles.hood` |
| Marquee window of the blueprint | 352 x 34 (z 91.9 to 125.9) | `profiles.marquee_window` |
| Wall | 4.0 (4.05 at each second slab) | `cavity.py` |
| Seam H1 of the hood | x 106 | `split.py` |
| Free depth behind the band wall | 109.1 to the rear wall of the hood | fit report |

### The largest driver

The fit study gives 53.9 as the largest round driver frame. This study examined the number, and the audio research of 2026-11-14 agrees:

- 53.9 is the height of the stand-in form (57.9) less a margin of 2 on each side (`fit.Layout.speaker_frame_margin`). The width of the form (95.9) does not limit it. The test `test_the_driver_is_inside_the_largest_frame_of_the_fit_study` calculates the number again.
- The band is 67.9 high. Behind the wall, 109.1 of depth is free.
- The limit in height behind the wall is the light box. Its flange starts at z 86.9.

The driver of this study is the one that the research recommends: the Tectonic TEBM35C10-4, with a square frame of 51.8, in a sealed enclosure of 0.45 l behind each grille. The frame of 51.8 is inside 53.9. `hood_band.Driver` has the frame from the research. Its depth of 28, its basket and its magnet are an envelope that this study did not compare with a data sheet.

The fallback of the research is the Visaton FRS 5 X. Its frame is smaller (50), so it passes each opening. It needs its own seat pocket: the pocket follows `Driver.frame`.

A driver with a frame of 57 does not fit in variants A and C. The tunnel of the pod must then be 59 high, and the pod (64.9 high) has 2.95 of wall left at its top and bottom. The front round (2), the edge break (1) and a land of 2 need 5. The pod cannot be higher than the band. In variant B a frame of 57 fits: the opening is then 59 high (z 21.5 to 80.5), inside the baffle.

## 3. Decisions that all variants share

### The grille is a printed insert

The grille is a separate black part in an opening of the band. It is not a field of slots in the printed hood. The reasons:

- The owner's rule: the exterior has no narrow place that a person cannot fill, sand and paint. Slots of 3.4 through a painted wall of 4 are such places.
- The hood side prints upright. A level slot in an upright wall is a bridge. The insert prints with its front face on the bed, and its holes or slots go straight up.
- A black insert in a white hood needs no masking.
- The insert clamps the driver. Two screws from the front release the grille and the driver. The owner can service the speaker when the hood is bonded.
- The owner can change the grille pattern later. The opening stays the same.

### The speaker assembly

| Part | Values |
| --- | --- |
| Speaker opening | 54 high (z 23.95 to 77.95), corner radius 4. Variants A and C: 64 wide, centre at x 151.1. Variant B: from x 112 to 10 inside the leg, centre at x 153.1. |
| Driver | Tectonic TEBM35C10-4 (the research). Frame 51.8 x 51.8 from the research. Envelope, not verified: frame 2 thick with corners of radius 3, basket 47 in diameter and 12 deep, magnet 36 in diameter and 14 deep, total depth 28, cone 44 in diameter. |
| Driver seat | A baffle behind the wall, 110 x 68.9 x 5 (z 16.5 to 85.4), and an island that fills the opening. The seat face is 3.5 behind the front of the wall. A pocket of 1.9 holds the frame 0.1 proud. Hole for the basket: 48. |
| Sealed enclosure | A box that is open to the front and closes on the rear of the baffle. Walls 2.4. Inside 87.2 x 62.1 x 87.8, which is 0.45 l of air after the driver (25.3 cm3). Outside 92 x 66.9 x 90.2, with an ear of 9 on each side. |
| Fasteners of the grille | Two M3 screws through the grille, 29 left and right of the centre, into heat-set inserts in the seat (holes of 4.0, 5.65 deep). |
| Fasteners of the enclosure | Four M3 screws through the ears into heat-set inserts in the baffle, 50.5 left and right of the centre and 20 above and below it. |
| Grille | A plate of 2.4 with a gap of 0.15 to its opening. |

The research asks for four bosses on the band for each enclosure. In this study the four inserts are in the baffle. The baffle is bonded behind the band, so it is the boss plate. A gasket between the enclosure and the baffle is not modelled.

In variants A and C, two clamp bars (8 x 40) stand behind the grille plate and reach back to the frame. In variant B the plate lies on the frame. In each variant the two screws press the frame onto the seat.

The driver and the grille come out to the front. The enclosure stays in the hood.

The rear of the enclosure is at y 558.2 of the cabinet. The inner face of the rear wall of the hood is at y 576, so 17.8 is free. The top of the enclosure is 2.5 below the flange of the light box. The monitor is in the body, below the seam, and no part of the band is below z 16.5 of the hood.

The baffle starts at x 96.1 in variants A and C. It goes across the seam H1 (x 106) on the inside, as the light box does.

### The marquee

The marquee is a lit window under the top bar. It is the same in all variants.

| Part | Values |
| --- | --- |
| Window in the wall | 352 x 32 (z 92.9 to 124.9), corner radius 3. It is the marquee window of the blueprint less 1 at its top and bottom. |
| Lip | A bar across the opening, z 84.9 to 90.9, 4.5 proud of the band (the stand-in is 5). A fence 2 thick with a round top (R 1). Behind the fence, a groove 2.5 wide and 1.0 deep. The lower front edge has the edge break. Two halves. |
| Front | A printed translucent plate, 2.2 thick, in front of the wall. Its foot stands in the groove of the lip. A gap of 2 separates it from the legs and from the top bar. Two halves with a lap of 8 on the centre line. |
| Hooks | One at each end of the front, 6 x 8, outside the lit window. Each goes through a slot in the wall (6.6 x 12). The nose holds 1.3 behind the wall. |
| Light box | Black, closed, inside 356 x 34 x 25 deep, walls 2, a flange of 3 on the rear of the wall. Two halves. |
| Light (assumption) | One LED strip, 10 wide, 350 long, on the rear wall of the box. A strip of 60 LEDs for each metre has a pitch of 16.7. |
| Diffuser distance | 26.6 from the face of the strip to the rear of the front. This is more than the pitch of the LEDs. |

The lip stands 0.5 behind the front of the hood. Thus its ends lie on the wall of the leg, behind the edge break of the leg's rim, and the joint has no sharp edge that shows.

**How the front comes out.** Lift the front by 1.9. The hooks are then in line with their slots, and the foot is above the fence. Pull the front to the front. No tool and no fastener is necessary. The test `test_the_marquee_front_comes_out_when_it_is_lifted` moves the solid along this path against the skin of the hood.

**The art.** The front is the diffuser. The art is a film on the rear of the front, or the first layers of the front in color. This is the owner's choice.

**How the light stays in.** The light box is the only lit space. It is black and closed, and its flange lies on the rear of the wall round the window. Light does not get to the white skin, to the seam between the hood and the body, or to the speaker openings. The front overlaps the wall by 2 at the top and bottom of the window and by 5 to 17 at its ends. The foot of the front is in the groove. At the top, a matte black margin on the rear of the front stops the light in the gap under the top bar. The cable leaves the box through a hole that the owner seals. That hole is not modelled.

**The seam H1.** The window and the lip go across the seams of the hood at x 106 and -106. The light box is bonded across these seams on the inside.

**What a cut plate changes.** A printed front is two halves, because 387 is longer than the printer. The lap shows as a fine line in the lit window. A cut plate of opal acrylic, 2 or 3 thick, is one piece with no line. For a plate of 3, the groove of the lip becomes 3.3 wide, and the lip becomes 5.3 proud. The lip then stands 0.3 in front of the hood front, or the fence becomes 1.2 thick. The hooks become two printed clips that are bonded to the plate.

**A display in place of the lit window.** The lit window is the base. The marquee research of 2026-11-14 gives these facts. No full-color display that can be bought is as low as the window (352 x 34, with 82.3 of depth). Lit art fits in it, or a row of single-color text modules. The window of the blueprint is eleven modules of 32, and the light box of this study (356 x 34 x 25) is the room for such a row. Each larger display needs a taller hood. Section 8 shows two of them as built studies.

### The logo field

No part carries a name or a logo. The field is plain, for the owner's own mark. The badge is a separate plate, 165.4 x 39.3 x 2.2, with corners of radius 2.7. It lies 1.0 below the rim of its recess. The owner prints it or has it cut.

## 4. The variants

| | A: pods | B: flush | C: frames |
| --- | --- | --- | --- |
| Idea | The band of the reference cabinet | The flat band of the maker's wide cabinet | Between A and B |
| Round each speaker | A pod, 13 proud, 90 x 64.9, corners R 8, front edge R 2 | Nothing. The opening is in the band. | A frame, 5 proud, same outline as the pod |
| Outer end | The pod's end is parallel to the leg | The opening's end is parallel to the leg | The frame's end is parallel to the leg |
| Grille | A field of holes: 3.8 in diameter, pitch 5.2 | Six level slots of 3.4, pitch 7, a centre bar of 5.6. The slot ends follow the leg. | Six upright slots of 3.4, pitch 7, a centre bar of 5.6 |
| Grille set back | 1.5 behind the front of the pod | 1.0 behind the band | 1.5 behind the front of the frame |
| Open area in front of the cone | 44% | 46% | 46% |
| Logo | A raised field, 176 x 49.9, 5 proud, with a recess of 3.2 for the badge | A recess in the band for the badge: an opening in the wall with a backer behind it | No field. The band is plain. |
| Parts of the band | 20 | 18 | 18 |

The pod is 0.18 W wide and 0.13 W high. The pods of the references are 0.18 to 0.20 W wide and 0.145 to 0.163 W high. The band of this hood is 0.137 W high, so a pod cannot have the height of the references.

The front round of a pod is R 2. The blueprint gives R 4 for the stand-in. With R 4, the land between the round and the tunnel is 0.45 at the top and bottom of the pod. With R 2 it is 2.45.

## 5. Checks

`hood_band.check` does these checks on each variant and writes `check.md` and `report.json` into the folder of the variant.

- **Edge rule.** The rule holds on each part that shows (`hood_band.SHOWN`): the painted parts (the hood, the lip, the pods and the logo field), the black grilles, the translucent marquee front and the badge. A convex edge that turns more than 45.5 degrees and has no round fails when it shows. An edge does not show when it lies in a joint, or when five rays from it toward the player all meet a part. The sharp edges of a part in `hood_band.open_edges` are an open item for the owner: they are listed and do not fail.
- **Face check.** `tools/face_check.py` on each part that shows, with the reveals and the known items of the shell. A finding fails when it shows.
- **Room.** No inside part and no hardware envelope shares volume with another one or with the skin of the hood.
- **Open area.** The holes or slots of the grille, inside the circle of the cone, are 40% of that circle or more.
- **Print.** Each part of the band fits the limit of the Q2 from `cad/params/printer.csv` (248 x 248 x 250; it was 240 x 240 x 245 on the server).

| Check | A | B | C |
| --- | --- | --- | --- |
| Sharp edges that show, on the parts that show | 0 | 0 | 0 |
| Sharp edges that are an open item for the owner | the hole grille | 0 | the rear rims of the slots |
| Face-check findings that show | 0 | 0 | 0 |
| Face-check findings that do not show | 4 | 4 | 4 |
| Inside parts or hardware that share volume | 0 | 0 | 0 |
| Open area | 44% | 46% | 46% |
| Parts that do not fit the printer | 0 | 0 | 0 |
| Result | PASS | PASS | PASS |

The four findings that do not show are the same in each variant: the two steps of the lap between the halves of the marquee front, 1.1 wide. They lie inside the joint.

`tools/edge_finish.py` and `tools/face_check.py` run as programs on the folder of each variant (section 14).

The fit study (`candybar.shell.fit`) was not run with these parts. The tests compare the band with its values: the driver frame against the largest frame of the fit study, and the mouth of the light box against the marquee room of the fit study (they are the same box).

## 6. Print

| Part | Orientation | Flattest underside |
| --- | --- | --- |
| Hood | As in the split: the centre on a cut face, each side upright | See the note that follows |
| Lip (two halves) | On its rear face | The rear face, 196.7 x 6 |
| Pod or frame | Front face on the bed | The front face |
| Logo field | Rear face on the bed | The rear face, 176 x 49.9 |
| Grille | Front face on the bed | The front face |
| Badge | Flat | The front face |
| Marquee front (two halves) | Flat, front face on the bed | The front face. The nose of a hook is a bridge of 2. |
| Light box (two halves) | Mouth on the bed | The flange. The rear wall is a bridge of 38. |
| Driver seat, logo backer | Baffle or flange on the bed | The baffle or the flange |
| Sealed enclosure | Rear wall on the bed, mouth up | The rear wall, 92 x 66.9 |

No face that shows on a band part needs support.

**The openings in the hood.** The hood side prints upright, so the top of each opening in the band wall is a bridge in a wall of 4. The speaker opening is a bridge of 64 in variants A and C, and of 76 in variant B. The marquee window is a bridge of 70 in each hood side. In variants A and C the rim of the speaker opening is under the pod, and a rough bridge does not show. In variant B the rim shows and has the edge break, so it needs a support in the opening or work after the print. The rim of the marquee window is behind the front in each variant. The hood centre prints on a cut face, and its openings have upright walls.

## 7. Recommendation

Variant A. It is the band that makes the hood read as a New Astro City: two white pods with black fronts and a logo plate between them. Its speaker openings are hidden, so the hood prints with no support that shows. The pods and the logo field print as separate flat parts.

Variant B is the cleanest to print and to paint. It has the fewest parts. It reads as the maker's wide cabinet, not as a New Astro City. Its speaker opening needs support.

Variant C has the print properties of A with a lower relief. It is the choice if the owner wants the marquee to carry the name and no logo field.

The parts can be mixed. The grille patterns fit each pod or frame, because the openings of A and C are the same. The logo options do not depend on the speakers.

## 8. A taller hood for a display

The research gives the room that a display needs. This study built two cabinets with a taller hood, each with band A: `H20` for a bar LCD of 8.8 inch, and `H46` for an LED matrix of 128 x 32 points (two panels of 160 x 80). Each is a `Blueprint` that `hood_band.tall_blueprint` makes from the default one. `dims.py` and `solids.py` do not change. The sheet `05-taller-hood.png` shows the hood as it is, +20 and +46 from the front, three-quarter front and the side.

All the added height goes into the marquee opening. The band, the lip, the top bar (21) and the lower front of the hood stay as they are.

| Value | As it is | H20 | H46 |
| --- | --- | --- | --- |
| Display | Lit art, or a row of text modules | Bar LCD, 8.8 inch | LED matrix, 320 x 80 |
| Window in the wall | 352 x 32 | 217 x 54 | 321 x 81 |
| Marquee opening, height | 36.1 | 56.1 | 82.1 |
| Depth of the box behind the window | 25 | 15 (assumption) | 40 |
| Flat top of the hood above its foot | 148 | 168 | 194 |
| The same, as a part of the width | 0.30 | 0.34 | 0.39 |
| Height of the cabinet | 573.4 | 593.4 | 619.4 |
| Top flat of the hood, width | 352.5 | 344.0 | 332.8 |
| Centre of the window above the desk | 534.3 | 544.3 | 557.3 |

The references have a hood of 0.25 to 0.33 of the width. H20 is at the upper end of that range. H46 is above it, and the sheet shows it: the hood becomes a tower above the screen.

What else moves when the hood grows:

- **The height of the cabinet.** It grows by 20 or by 46. The depth and the width do not change.
- **The top flat.** The sides of the hood lean in, so the top flat becomes 8.5 or 19.7 narrower. The window of 321 clears the corners of the opening by 9.7 on each side at its top.
- **The print pieces of the hood.** The hood side prints upright. Its height becomes 168 or 194, and the limit is 250 (the Q2). The hood centre prints on a cut face. Its box becomes 168 x 139 x 212 or 194 x 139 x 212, and the limit is 248 x 248. Each piece fits. These numbers come from the piece sizes of the split and the added height. The split was not run again.
- **The speakers.** Their room does not change. The band is the same, and the enclosure of 0.45 l is the same. The box of the display is above the enclosure in each study.
- **The sight lines.** The sill and the lower front of the hood do not move, so the hood hides no more of the screen than it does now. The fit study was not run again. The display is higher: its centre is 10 or 23 higher above the desk.
- **The front of the marquee.** For a display it is a tinted cover, not a diffuser. The sheet shows it dark.
- **The weight.** The skin of the hood grows by about 90 cm3 or 210 cm3 (an estimate: its outline, 4 thick), which is about 0.09 kg or 0.22 kg of ABS (1.05 g/cm3).

What the studies do not have:

- The checks of a study do not pass, and the run does not fail for them. H20 has 10 findings and H46 has 12. The window stands 1.05 (H20) or 0.55 (H46) below the top bar, so a strip of wall less than 2 wide is left there, with a sharp edge that shows through the gap above the front. A finished design cuts the window up to the top bar. The other findings are the known items of the hood at their new height.
- The edge break of the cap is complete in both studies (`solids.cap` made it).
- No skin, no fit study, no split and no section with the skin. The sections of the studies are not on a sheet.
- The depth of 15 for the bar LCD is an assumption of this study.

## 9. Assumptions

1. The driver is the Tectonic TEBM35C10-4 with a frame of 51.8 (the research). Its depth of 28 and the sizes of its basket and magnet are not verified.
2. The enclosure is sealed by a gasket on the baffle. The wires go through a sealed hole. Neither is modelled.
3. An open area of 40% of the cone is sufficient for a small full-range driver.
4. The grilles, the badge, the light box and the seats are black ABS as printed (the owner may print every part in ABS), and they are not painted. The edge rule holds on each of them that shows (section 14).
5. The marquee light is one LED strip, 10 wide. The diffuser distance of 26.6 gives even light for a strip of 60 LEDs for each metre or more.
6. The pods, the logo field and the lip are bonded to the hood, filled and painted with it.
7. The hood form in the build folders is the solid outer form with the openings as pockets 8 deep, as the default build writes its parts. The sections use the printed skin from the cache of the split.
8. The seat, the light box and the logo backer are bonded behind the wall before the hood pieces are bonded.

## 10. Open questions for the owner

1. Which hood: answered on 2026-11-14: the hood as it is. The +20 hood stays as a variant ("I don't think the midsize marquee is bad"), and the +46 hood stays as a study.
2. Which band: answered on 2026-11-14: band A. B and C stay as variants (`hood_band.CHOICE`).
3. On the hood as it is: lit art or a row of text modules in the marquee? The room is the same.
4. A printed front in two halves, or one cut plate?
5. The lip is 4.5 proud, 0.5 less than the stand-in. Accept?
6. Two black screw heads show on each grille. Accept, or a snap fit?
7. Variant B: accept a support in the speaker opening of the hood side?
8. The hole grille of band A: its webs (1.4) are too narrow for the edge break of R 1. Larger holes at a larger pitch (6 at 9 keeps 40 % open), slots, or sharp hole rims on a black part?
9. The upright slots of band C: their rear rims show through the slots. A grille of 3.4 with a break on both faces, or sharp rear rims on a black part?

## 11. Not done

- The fit study and the split were not run with the band parts. The pieces of the hood in the split do not have the openings.
- The amplifier, the wires, the cable hole of the light box, the gasket of the enclosure and the plug at the foot of the hood are not modelled.
- The screws and the heat-set inserts are holes only.
- The halves of the light box meet on a plane. The joint has no lap.
- No part was sliced.

## 12. How to build

```sh
CANDYBAR_OUT=cad/out/hood-band cad/candybar/freecad-run.sh candybar.shell.hood_band      # the three variants and their checks
CANDYBAR_OUT=cad/out/hood-band/A cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc  # shell.FCStd of one variant
cad/.venv-tools/bin/python cad/tools/draw_hood_band.py                                    # the renders and the sheets
cad/test.sh test_hood_band                                                                # the tests
```

`HOOD_BAND_VARIANTS=A,B` builds only these variants. The first run makes the parts that the variants share and keeps them in `cad/out/hood-band/base`.

The sheets are in `cad/out/hood-band/sheets/`: `01-cabinet.png`, `02-band.png`, `03-sections.png`, `04-reference.png` and `05-taller-hood.png`.

`HOOD_BAND_TALL=` (empty) builds no study of a taller hood. `HOOD_BAND_TALL=H20` builds one.

### The default build on the server

On this machine `candybar.shell.solids` stops in the edge break of the hood: `the edge break of the hood: tool 1 still holds 0.013 mm3 of 0.013`. The one boolean of `solids.cut_near` with all 30 tools leaves 14 of them uncut. The second try then fails on the tool at the kink of the opening. The result is the same on one core and on 64. `hood_band.cap` calls `solids.cap` first. If that fails, it cuts the same tools one at a time. The cap then has 77 faces, as the roadmap records, and no sharp edge is left. The caps of the two taller hoods do not have this fault: `solids.cap` makes them on this machine.

## 13. On the main line

Date: 2026-11-14. The package was merged on the laptop (OpenCascade 7.9.3) after the socket plate.

- **The owner's choice.** Band A, on the hood as it is (`hood_band.CHOICE`). Bands B and C, the +20 hood and the +46 hood stay as variants and studies. None of them is in the default build of the shell.
- **The fall-back of the cap is removed.** On the laptop `solids.cap` makes the cap of the present hood and of the two taller hoods, with the edge break (30 tools in each). The fall-back that cut the tools one at a time was for the kernel of the server.
- **The printer.** The print check reads the limit of the Q2 from `cad/params/printer.csv`.
- **Result.** Variants A, B and C: PASS. The study H20 has 10 findings and H46 has 12 (they do not fail the run). In both, the top edge of the larger marquee opening is sharp on the centre line (211 and 315 long), and the face check finds narrow faces at the corners of the opening and at the rear of the cap. The known items of the face check are those of the present hood, so two of them have no finding in a taller hood. These are open items of the studies, to solve if the owner chooses a taller hood.
- `tests/test_hood_band.py`: 28 tests pass.

## 14. The edge rule on every part that shows

Date: 2026-11-15. The edge rule of the roadmap holds on each face that shows on the outside, painted or not. The first build held it on the painted parts only (assumption 4 of the first build). The parts that changed:

- **Grille, slots (B and C).** Each edge of the front face has the break of R 1: the rim of the plate and the mouth of each slot. The mouth of a screw hole lies under the head of its screw, and the bar between two slots (5.6) leaves no room for a break round a hole of 3.4.
- **Screw heads.** The two screws of each grille are now in the build as bought parts (`grille_screw_inner_*`, `grille_screw_outer_*`): an M3 button head of 5.7 x 1.65 (ISO 7380, ESTIMATED: the screw is not bought). They cover the mouths of the screw holes.
- **Marquee front.** Each edge of its front face has the break, before the split into the two halves, so that the halves agree at the lap. The rim behind the break is 1.2 (the front is 2.2 thick, for the groove of the lip).
- **Badge.** Each edge of its front face has the break.
- **Grille, holes (A).** No change. The webs are 1.4 on the front, and two breaks need 2. It is an open item (question 8).
- **Grille, upright slots (C).** The front has the break. The rear rims show through the slots, because the frame leaves the room behind the grille open. It is an open item (question 9).

`tools/face_check.py` now allows a narrow face that runs on, tangent, from a face of the edge break: the wall of a thin plate behind its break (1.4 in a grille of 2.4, 1.2 in the marquee front and the badge). It is listed as allowed with that reason.

| Tool | A | B | C |
| --- | --- | --- | --- |
| `hood_band` checks | PASS, 1 open item | PASS | PASS, 1 open item |
| `tools/edge_finish.py` | holds, 1 open item | holds | holds, 1 open item |
| `tools/face_check.py` | PASS | PASS | PASS |

