# The hood band: speaker grilles, marquee and logo field

Date: 2026-11-14. State: a design study with three variants. The owner chooses.

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

The fit study gives 53.9 as the largest round driver frame. This study examined the number. It is correct for the stand-in, and it is not a limit of the skin:

- 53.9 is the height of the stand-in form (57.9) less a margin of 2 on each side (`fit.Layout.speaker_frame_margin`). The test `test_the_driver_is_inside_the_largest_frame_of_the_fit_study` calculates it again.
- The band is 67.9 high. Behind the wall, the cavity is open down into the body and up to the light box.
- The limit in height is the light box. Its flange starts at z 86.9. The driver seat of this study ends at z 82.95.

The study uses a driver of the 50 mm class with a square frame of 50 (`hood_band.Driver`). It is inside 53.9, and it is inside the range of 40 to 50 that the research recommends.

A driver with a frame of 57 does not fit in variants A and C. The tunnel of the pod must then be 59 high, and the pod (63.9 high) has 2.45 of wall left at its top and bottom. That is less than the front round and the edge break need (3.5). The pod cannot be higher than the band. In variant B a frame of 57 fits if the seat flange is 4 and not 6: the opening is then 59 high (z 21.5 to 80.5), and the flange ends at z 84.5, which is 2.4 below the light box.

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
| Speaker opening | 52 high (z 24.95 to 76.95), corner radius 4. Variants A and C: 64 wide, centre at x 151.1. Variant B: from x 112 to 10 inside the leg, centre at x 153.1. |
| Driver (envelope, assumption) | Frame 50 x 50 x 2, corner radius 3. Basket 47 in diameter and 12 deep. Magnet 36 in diameter and 14 deep. Total depth 28. Cone 44 in diameter. |
| Driver seat | A flange of 6 behind the wall, 5 thick, and an island that fills the opening. The seat face is 3.5 behind the front of the wall. A pocket of 1.9 holds the frame 0.1 proud. Hole for the basket: 48. |
| Fasteners | Two M3 screws through the grille, 29 left and right of the centre. Two M3 heat-set inserts in the seat (holes of 4.0, 5.65 deep). |
| Grille | A plate of 2.4 with a gap of 0.15 to its opening. |

In variants A and C, two clamp bars (8 x 40) stand behind the grille plate and reach back to the frame. In variant B the plate lies on the frame. In each variant the two screws press the frame onto the seat.

The driver, its seat and the grille come out to the front. The wires stay in the hood.

The rear of the driver is at y 490.4 of the cabinet. The rear wall of the hood is 85.6 behind it. The monitor is in the body, below the seam, and no part of the band is below z 18.9 of the hood.

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

**A small display in place of the lit window.** The lit window is the base. The window of the blueprint, 352 x 34, is eleven modules of 32. This agrees with LED dot-matrix modules of 32 x 32 with 8 x 8 points (not verified against a data sheet in this study). Such a row needs 352 x 32 behind the window and about 15 to 25 of depth. The light box has this room: 356 x 34 x 25. The front then becomes a tinted cover. A bar LCD is a different case. The usual bar panels of 7.9 and 8.8 inches are about 60 to 70 high with their frame (from memory, not verified). The marquee opening is 36.1 high. The lip must then move down by 25 to 35, the band becomes 33 to 43 high, and a 50 mm driver does not fit in it. A bar LCD needs a new band.

### The logo field

No part carries a name or a logo. The field is plain, for the owner's own mark. The badge is a separate plate, 165.4 x 39.3 x 2.2, with corners of radius 2.7. It lies 1.0 below the rim of its recess. The owner prints it or has it cut.

## 4. The variants

| | A: pods | B: flush | C: frames |
| --- | --- | --- | --- |
| Idea | The band of the reference cabinet | The flat band of the maker's wide cabinet | Between A and B |
| Round each speaker | A pod, 13 proud, 90 x 63.9, corners R 8, front edge R 2.5 | Nothing. The opening is in the band. | A frame, 5 proud, same outline as the pod |
| Outer end | The pod's end is parallel to the leg | The opening's end is parallel to the leg | The frame's end is parallel to the leg |
| Grille | A field of holes: 3.8 in diameter, pitch 5.2 | Six level slots of 3.4, pitch 7, a centre bar of 5.6. The slot ends follow the leg. | Six upright slots of 3.4, pitch 7, a centre bar of 5.6 |
| Grille set back | 1.5 behind the front of the pod | 1.0 behind the band | 1.5 behind the front of the frame |
| Open area in front of the cone | 44% | 46% | 46% |
| Logo | A raised field, 176 x 49.9, 5 proud, with a recess of 3.2 for the badge | A recess in the band for the badge: an opening in the wall with a backer behind it | No field. The band is plain. |
| Parts of the band | 18 | 16 | 16 |

The pod is 0.18 W wide and 0.13 W high. The pods of the references are 0.18 to 0.20 W wide and 0.145 to 0.163 W high. The band of this hood is 0.137 W high, so a pod cannot have the height of the references.

The front round of a pod is R 2.5. The blueprint gives R 4 for the stand-in. With R 4, the land between the round and the tunnel is 1.0 at the top and bottom of the pod. With R 2.5 it is 2.5.

## 5. Checks

`hood_band.check` does these checks on each variant and writes `check.md` and `report.json` into the folder of the variant.

- **Edge rule.** The painted parts are the hood, the lip, the pods and the logo field. A convex edge that turns more than 45.5 degrees and has no round fails when it shows. An edge does not show when it lies in a joint, or when five rays from it toward the player all meet a part.
- **Face check.** `tools/face_check.py` on each part that shows, with the reveals and the known items of the shell. A finding fails when it shows.
- **Room.** No inside part and no hardware envelope shares volume with another one or with the skin of the hood.
- **Open area.** The holes or slots of the grille, inside the circle of the cone, are 40% of that circle or more.
- **Print.** Each part of the band fits 240 x 240 x 245.

| Check | A | B | C |
| --- | --- | --- | --- |
| Sharp edges of painted parts that show | 0 | 0 | 0 |
| Face-check findings that show | 0 | 0 | 0 |
| Face-check findings that do not show | 4 | 4 | 4 |
| Inside parts or hardware that share volume | 0 | 0 | 0 |
| Open area | 44% | 46% | 46% |
| Parts that do not fit the printer | 0 | 0 | 0 |
| Result | PASS | PASS | PASS |

The four findings that do not show are the same in each variant: the two steps of the lap between the halves of the marquee front, 1.1 wide. They lie inside the joint.

`tools/edge_finish.py` and `tools/face_check.py` were not run as programs on the folders of the variants. `edge_finish.py` has a fixed list of part names, and a part that is not in the list fails. The module calls the functions of the two tools on its own parts.

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
| Driver seat, logo backer | Flange on the bed | The flange |

No face that shows on a band part needs support.

**The openings in the hood.** The hood side prints upright, so the top of each opening in the band wall is a bridge in a wall of 4. The speaker opening is a bridge of 64 in variants A and C, and of 76 in variant B. The marquee window is a bridge of 70 in each hood side. In variants A and C the rim of the speaker opening is under the pod, and a rough bridge does not show. In variant B the rim shows and has the edge break, so it needs a support in the opening or work after the print. The rim of the marquee window is behind the front in each variant. The hood centre prints on a cut face, and its openings have upright walls.

## 7. Recommendation

Variant A. It is the band that makes the hood read as a New Astro City: two white pods with black fronts and a logo plate between them. Its speaker openings are hidden, so the hood prints with no support that shows. The pods and the logo field print as separate flat parts.

Variant B is the cleanest to print and to paint. It has the fewest parts. It reads as the maker's wide cabinet, not as a New Astro City. Its speaker opening needs support.

Variant C has the print properties of A with a lower relief. It is the choice if the owner wants the marquee to carry the name and no logo field.

The parts can be mixed. The grille patterns fit each pod or frame, because the openings of A and C are the same. The logo options do not depend on the speakers.

## 8. Assumptions

1. The driver is a full-range unit of the 50 mm class with a square frame of 50 and a depth of 28. No model is chosen.
2. The driver plays into the open volume of the hood and the body. It has no closed box.
3. An open area of 40% of the cone is sufficient for a small full-range driver.
4. The grilles, the badge, the light box and the seats are black PETG as printed, and they are not painted. The edge rule is for painted parts.
5. The marquee light is one LED strip, 10 wide. The diffuser distance of 26.6 gives even light for a strip of 60 LEDs for each metre or more.
6. The pods, the logo field and the lip are bonded to the hood, filled and painted with it.
7. The hood form in the build folders is the solid outer form with the openings as pockets 8 deep, as the default build writes its parts. The sections use the printed skin from the cache of the split.
8. The seat, the light box and the logo backer are bonded behind the wall before the hood pieces are bonded.

## 9. Open questions for the owner

1. Which band: A, B, C, or a mix?
2. Which driver? The seat pocket and the clamp bars follow the frame.
3. Lit window or a row of dot-matrix modules in the marquee? The room is the same.
4. A printed front in two halves, or one cut plate?
5. The lip is 4.5 proud, 0.5 less than the stand-in. Accept?
6. Two black screw heads show on each grille. Accept, or a snap fit?
7. Variant B: accept a support in the speaker opening of the hood side?

## 10. Not done

- The fit study and the split were not run with the band parts. The pieces of the hood in the split do not have the openings.
- The amplifier, the wires, the cable hole of the light box and the plug at the foot of the hood are not modelled.
- The screws and the heat-set inserts are holes only.
- The halves of the light box meet on a plane. The joint has no lap.
- No part was sliced.

## 11. How to build

```sh
CANDYBAR_OUT=cad/out/hood-band cad/candybar/freecad-run.sh candybar.shell.hood_band      # the three variants and their checks
CANDYBAR_OUT=cad/out/hood-band/A cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc  # shell.FCStd of one variant
cad/.venv-tools/bin/python cad/tools/draw_hood_band.py                                    # the renders and the sheets
cad/test.sh test_hood_band                                                                # the tests
```

`HOOD_BAND_VARIANTS=A,B` builds only these variants. The first run makes the parts that the variants share and keeps them in `cad/out/hood-band/base`.

The sheets are in `cad/out/hood-band/sheets/`: `01-cabinet.png`, `02-band.png`, `03-sections.png` and `04-reference.png`.

### The default build on the server pal9000

On this machine `candybar.shell.solids` stops in the edge break of the hood: `the edge break of the hood: tool 1 still holds 0.013 mm3 of 0.013`. The one boolean of `solids.cut_near` with all 30 tools leaves 14 of them uncut. The second try then fails on the tool at the kink of the opening. The result is the same on one core and on 64. `hood_band.cap` calls `solids.cap` first. If that fails, it cuts the same tools one at a time. The cap then has 77 faces, as the roadmap records, and no sharp edge is left.
