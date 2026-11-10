# Mini New Astro City, 9.7 inch: measured geometry

Research date: 2026-11-09. Scope: the shape, the proportions and the part division of the "Mini New Astro City Arcade Machine" (9.7 inch 4:3 screen) from MakerWorld model 700005. This document calls it "the model". The model is a different design from the reference cabinet of `CONTEXT.md`. It is a reference to measure. It is not a design to copy or to scale.

Section 5 of `docs/research/cabinet-references.md` holds what the web pages say about the model. This document adds what the files say.

## How to read the numbers

All lengths are in millimeters. All angles are in degrees.

The frame is the frame of the project: X to the right of the player, Y from the deck front toward the rear, Z up from the floor underside. The deck front is Y=0. The model has no feet, so Z=0 is the table.

`W` is the width of the model at the cheeks and at the deck: 270.0 mm. Each ratio is a length divided by `W`. This project has a body width of 422 mm, so the scale factor is 1.563.

| Tag | Meaning |
| --- | --- |
| MEASURED | Measured with a script from the mesh files. The method code and the part come after the tag. Section 3 gives the file of each part. |
| SOURCED | Read from the metadata files of the 3MF project. |
| ESTIMATED | Derived from other numbers, from a view, or from a fit that has more than one solution. The basis is given. |

Method codes for MEASURED values:

| Code | Method |
| --- | --- |
| B | Bounding box of the vertices of a part or of the assembly. |
| P | Plane: triangles grouped by normal and offset. The value is the normal, the offset or the extent of the group. |
| S | Section: the part is cut with a plane. The value comes from the corner points of the loops, or from lines cast at a step of 0.05 to 0.25 mm. |
| F | Fit: a least-squares circle through section points. The text gives the rms error where it matters. |
| H | Hole: a circle fit to a closed loop of a section, at 1 mm steps along the hole axis. |

The words "left" and "right" are the left and the right of the player.

## 1. Source files and terms

| Item | Value |
| --- | --- |
| Download directory | `cad/vendor/mini-new-astro-city/download/` (ignored by git) |
| `ASTRO+ARCADE+bambu.3mf` | 4202925 bytes, sha256 `973986d3...2e511c81`. A Bambu Studio project: 16 objects on 13 plates. |
| `Mini+New+Astro+City+Arcade+Machine.zip` | 2134482 bytes, sha256 `a511de1c...d853d6ed`. It holds `ASTRO ARCADE.zip`, which holds 16 binary STL files. |
| Extracted copies | `cad/vendor/mini-new-astro-city/3mf/`, `zip/`, `zip-inner/` |
| Designer in the metadata | CabLab (the remix author). The description names Game-Makers as the creator of the design. SOURCED |
| License in the metadata | `Standard Digital File License`. The `Copyright` field is empty. SOURCED |
| License text | The files do not contain it. The two archives contain no readme and no license file. |
| Slicer | Bambu Studio 01.10.01.50, created 2025-02-04. SOURCED |

The files give the name of a license and not its terms. This project uses the files as a reference for personal use only. The files stay in the ignored vendor directory. This document holds measurements, ratios and descriptions only.

The STL files are the same 16 objects as the 3MF project, exported in the plate positions. The 3MF project also holds the cut data, the plate data and the slicer settings. All measurements use the 3MF objects. The STL files gave a cross-check of the volumes.

The 3MF folder `Auxiliaries/Assembly Guide/` holds one PDF. It is a sticker sheet, not an assembly guide. The folder `Auxiliaries/Model Pictures/` holds two photos of a finished cabinet. The photos confirm the lever on the left and six buttons on the right. They also confirm two buttons in the deck front face on the right, and two speaker pods in the hood band.

## 2. Method

- A script listed each archive, then extracted it into a new empty directory. The script refuses absolute paths, links and paths that leave the target directory. It refused no entry.
- The study executed no file from the archives. The archives contain no `.FCStd` file.
- Python 3.14 with `-I`, numpy and matplotlib parsed the 3MF XML and the STL files as data. FreeCAD was not necessary.
- Pillow and `pdftoppm` converted the two photos and the PDF to PNG for viewing only.
- Copies of the scripts are in `cad/vendor/mini-new-astro-city/analysis/scripts/`. The full number record is `cad/vendor/mini-new-astro-city/analysis/measurements.txt`.
- The transform of each part into the frame of this document is in `cad/vendor/mini-new-astro-city/analysis/placement.json`.

The 16 STL files have no open edge. Five files have 2 to 24 edges that more than two triangles share. These edges do not change a measurement.

## 3. Part inventory

The "as printed" size is the bounding box of the part on its plate, X by Y by Z. The time and the mass are the slicer predictions for the plate. SOURCED

| Part (word of this project) | Name in the model, STL file | 3MF object | Triangles | Volume cm3 | Size as printed | Plate | Orientation on the plate | Cut piece |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Body, upper right | `BodyV2.stl.stl` | 11 | 3158 | 482.6 | 135.0 x 206.4 x 132.2 | 12 UPPER BODY | Upright. It stands on the cut face. | Yes |
| Body, upper left | `BodyV2.stl(1).stl` | 20 | 3172 | 510.8 | 135.0 x 206.4 x 132.2 | 12 UPPER BODY | Upright. It stands on the cut face. | Yes |
| Body, lower rear left | `BodyV2.stl(2).stl` | 44 | 5296 | 386.9 | 119.9 x 98.4 x 125.0 | 10 BODY3 | Upright, floor on the bed | Yes |
| Body, lower front left | `BodyV2.stl(3).stl` | 57 | 7706 | 520.7 | 135.0 x 155.3 x 125.0 | 11 BODY4 | Upright, floor on the bed | Yes |
| Body, lower rear right | `BodyV2.stl(4).stl` | 69 | 4466 | 400.5 | 134.8 x 115.3 x 125.0 | 9 BODY2 | Upright, floor on the bed | Yes |
| Body, lower front right | `BodyV2.stl(5).stl` | 82 | 6704 | 509.1 | 135.0 x 138.4 x 125.0 | 4 BODY1 | Upright, floor on the bed | Yes |
| Deck | `Front Panel.stl.stl` | 24 | 11350 | 416.3 | 248.4 x 249.3 x 50.0 | 6 FRONT PANEL BASE | Upright, floor on the bed, turned 45.2 | No |
| Control panel | `Panel full.stl.stl` | 26 | 6736 | 129.8 | 225.7 x 222.5 x 34.8 | 7 FRONT PANEL TOP | Top face on the bed, turned 44.2 | No |
| Hood | `Topper.stl.stl` | 32 | 12796 | 277.8 | 211.9 x 236.5 x 85.7 | 8 TOPPER | Rear face on the bed, turned 50.9 | No |
| Hood band, marquee version | `Face topper.stl.stl` | 88 | 6572 | 53.7 | 242.3 x 72.1 x 34.0 | 13 TFT SPEAKERS | Rear side of the plate on the bed, pods up | No |
| Hood band, plain version | `Face topper Sticker.stl.stl` | 22 | 3866 | 62.8 | 242.3 x 72.1 x 34.0 | 5 SPEAKERS SET | Rear side of the plate on the bed, pods up | No |
| Speaker grilles (two in one file) | `Speakers.stl.stl` | 28 | 2088 | 34.1 | 112.0 x 32.4 x 48.6 | 5 SPEAKERS SET | Each grille stands on a 48.0 x 32.4 face | No |
| Speaker plate | `Support HP.stl.stl` | 30 | 8348 | 75.1 | 239.2 x 80.2 x 6.1 | 5 SPEAKERS SET | Flat | No |
| Hood rear vent plate | `Air Wings.stl.stl` | 2 | 14152 | 28.7 | 209.7 x 197.5 x 7.1 | 1 AIR VENT | Flat, louvers up, turned 42.1 | No |
| Bezel plate | `Bezel.stl.stl` | 84 | 1860 | 157.7 | 238.9 x 217.1 x 10.0 | 2 BEZEL | Flat, front face on the bed | No |
| Bezel plate, version turned 180 | `BEZEL MODIFICATO.stl.stl` | 86 | 2542 | 156.4 | 238.9 x 217.1 x 10.0 | 3 BEZEL 180 | Flat, front face on the bed | No |

The triangle counts are those of the main volume in the 3MF object. The STL files of the body pieces have more triangles, because the export adds the dowels and the sockets. MEASURED B

Groups:

- Body: the six cut pieces. Together they are one monocoque part: floor, two side walls with the cheeks, rear wall, and the apron bar at the foot of the screen face.
- Hood: the hood, one hood band, the two speaker grilles and the hood rear vent plate. The speaker plate closes the top of the body under the hood.
- Deck: the deck part and the control panel.
- Bezel: one bezel plate. The second version is for an LCD that shows its image turned 180 degrees.
- Control panel: one part. It is a 5.0 mm plate with a skirt.
- Rear door: the model has none. The rear wall is part of the body. Access is through the top (the hood lifts off) and through the bezel opening.

Plate data. SOURCED

| Plate | Time | Mass g |
| --- | --- | --- |
| 1 AIR VENT | 1 h 04 | 33.7 |
| 2 BEZEL | 2 h 32 | 90.3 |
| 3 BEZEL 180 | 2 h 33 | 90.2 |
| 4 BODY1 | 5 h 22 | 202.4 |
| 5 SPEAKERS SET | 5 h 01 | 156.4 |
| 6 FRONT PANEL BASE | 5 h 34 | 207.4 |
| 7 FRONT PANEL TOP | 3 h 05 | 108.5 |
| 8 TOPPER | 4 h 07 | 131.4 |
| 9 BODY2 | 5 h 44 | 195.0 |
| 10 BODY3 | 5 h 42 | 187.5 |
| 11 BODY4 | 5 h 49 | 217.0 |
| 12 UPPER BODY | 11 h 32 | 420.7 |
| 13 TFT SPEAKERS | 1 h 51 | 56.5 |
| All 13 plates | 59 h 56 | 2097 |

One cabinet needs one bezel plate and one hood band. With the plain hood band that is about 1950 g and 55.5 h. ESTIMATED (plate sums)

Slicer settings in the project. SOURCED

| Setting | Value |
| --- | --- |
| Printer profile | Bambu Lab X1 Carbon, 0.4 nozzle, bed 256 x 256, height 250 |
| Layer height | 0.2 |
| Wall loops | 3 (line width 0.42, so each skin is about 1.26 mm) |
| Infill | 15 percent, grid |
| Top and bottom layers | 4 |
| Supports | On, tree (organic), threshold angle 10. The slicer reports "support used" on all 13 plates. |
| Brim | Automatic, 5 mm |
| Filament | Generic PETG |

## 4. Assembly

The files hold the parts in their print positions. A script assembled the parts numerically. Confidence is high.

The placement of each part:

- Body. The six cut pieces share one frame in the 3MF project, and the assemble data gives them the same transform. Their cut faces are coplanar and their outlines match. No fit was necessary.
- Deck. Its rear face is on the front face of the body. The two side lugs of the body are in the two pockets of the deck. The five floor lugs of the deck are in the five slots of the body floor. The undersides are flush.
- Control panel. Its print position is top down, so the assembly turns it over. Its skirt stands on the ledge of the deck at Z=15.0. Its flange sits between the front wall of the deck and the apron bar.
- Hood. Its bottom face is on the top face of the body at Z=247.25. Its rear face continues the 16.0 degree lean of the top of the rear wall. The four body lugs are in the four hood pockets.
- Hood band. Its plate is on the lip plane inside the hood. Its lower edge has a facet that sits flat on the body top. Its upper flap is in a slot under the hood top.
- Bezel plate. Its lower end is on the flat ledge of the apron bar at Z=64.86. Its hooks are in the slot of the apron bar and in the slot of the speaker plate.
- Speaker plate. It lies on ledges 6.3 mm under the body top. Its angled front edge continues the front face of the bezel plate.
- Hood rear vent plate. It is on the outside of the hood rear face. The six holes of the plate match the six holes of the hood.

Checks of the assembly. MEASURED H for the holes, S for the rest

| Check | Result |
| --- | --- |
| Interference | No vertex of a part is more than 0.2 mm inside a different part. The test used ray casting on all part pairs. |
| Deck to body, side screws | Clearance holes in the deck and pilot holes in the body lugs agree within 0.3 mm (two holes on each side). |
| Deck to body, floor screws | Pilot holes in the deck lugs and counterbores in the body floor agree within 0.3 mm (four holes). |
| Control panel to deck | Pilot holes in the panel and clearance holes in the deck agree within 0.06 mm (two holes). |
| Hood to body, cross screws | Agree within 0.02 mm (two holes). |
| Hood to body, vertical screws | Agree within 0.01 mm (four holes). |
| Vent plate to hood | Hole pattern 50.0 by 190 to 220 mm matches (six holes). |
| Lug in pocket | The deck side lugs have 0.4 to 0.6 mm clearance on each side at the left lug and 0.9 to 1.1 mm at the right lug. The lug tips have 1.4 mm. |

These hole pairs did not set the placement of the deck, the control panel or the hood. They are independent checks.

One placement is a fit, not a pure measurement. With the bezel plate hard on its seat, its lower hooks are 0.53 mm inside the wall of the apron slot. The screw holes resolve this. The speaker plate holes sit on the body pilot holes when the plate is 0.83 mm forward of lug contact. The bezel plate pilot holes then sit under the speaker plate holes when the bezel plate is 0.95 mm forward. In that position the bezel plate is 0.80 mm off its seat and all hooks are clear. ESTIMATED: the bezel plate depth is known within 0.5 mm.

The two speaker grilles are not placed. They go into the open fronts of the two pods of the hood band. They do not change an outline or a number in this document.

## 5. Images

All images are in `cad/vendor/mini-new-astro-city/analysis/` (ignored by git). Each image is about 1600 px on the long side. Each image has a scale bar and a 50 mm grid in the frame of this document.

| File | Content |
| --- | --- |
| `silhouette-side.png` | Side outline of the assembled shell, with depth, height and deck size |
| `silhouette-front.png` | Front outline, with width, height and the hood top flat |
| `silhouette-top.png` | Top outline, with the widths of the deck and of the rear body |
| `view-front.png`, `view-side.png`, `view-top.png`, `view-rear.png` | Shaded orthographic views, one color for each part |
| `view-three-quarter-front.png`, `view-three-quarter-rear.png` | Shaded three-quarter views |
| `section-plan-screen.png` | Horizontal section at the screen center height (Z=155.5): cheeks, cheek facets, bezel plate recess, side step, rear body |
| `section-plan-screen-cheek.png` | Detail of the right cheek in that section: land, facet, seat rail, bezel plate |
| `section-plan-deck.png` | Horizontal section through the deck at Z=30: deck walls, body lugs in the deck pockets, the 45 degree return |
| `section-plan-deck-top.png` | Horizontal section at Z=47: control panel, rim and facet of the deck |
| `section-plan-floor.png` | Horizontal section at Z=8: floor vents, deck lugs in the floor slots |
| `section-center-line.png` | Vertical section at X=0.3: deck, control panel, apron, bezel plate, speaker plate, hood, rear wall, floor. The hood band at X=40 and X=73 is dashed. |
| `section-cheek.png` | Vertical section through the right cheek at X=122: the arc of the cheek front edge, the foot fillet, the rear edge of the side band |
| `section-cheek-facet.png` | Vertical section at X=130, through the cheek facet |
| `section-side-wall.png` | Vertical section at X=110, inside the rear side wall |
| `section-front-hood.png` | Cross section at Y=286, seen from the front: hood side arc, hood corner, rear body |
| `section-front-screen.png` | Cross section at Y=180, seen from the front: cheeks, bezel plate, floor |
| `body-cuts-side.png`, `body-cuts-top.png`, `body-cuts-rear.png`, `body-cuts-front.png` | The six body pieces in six colors, with the 28 dowel positions |

The silhouettes show small white openings. These are paths through the bare shell: the screen opening without an LCD, the power inlet opening, the vent slots and the open speaker pods.

## 6. Measurements

### 6.1 Overall

| Item | Value | Ratio to W | Tag |
| --- | --- | --- | --- |
| Width at the deck | 270.0 | 1.000 | MEASURED B, deck |
| Width at the cheeks (outside to outside) | 270.0 | 1.000 | MEASURED P, body |
| Clear width between the cheeks | 240.0 | 0.889 | MEASURED P, body |
| Width of the rear body | 230.0 | 0.852 | MEASURED P, body |
| Width of the hood at its seam | 267.2 | 0.990 | MEASURED B, hood |
| Width of the hood top flat | 192.5 | 0.713 | MEASURED P and F, hood |
| Depth, deck front to rear wall | 338.1 | 1.252 | MEASURED B, assembly |
| Height, floor underside to hood top | 316.4 | 1.172 | MEASURED B, assembly |
| Height of the deck top | 50.0 | 0.185 | MEASURED P, deck |
| Height of the seam between body and hood | 247.25 | 0.916 | MEASURED P, body |
| Height of the screen center | 155.5 | 0.576 | MEASURED S, bezel plate |

The body at the screen has the same width as the deck. The deck is wider than the rear body only: 1.174 times.

The model has no feet. The body underside has four round recesses of 12 mm diameter. The deck underside has two of 13 mm. MEASURED H

### 6.2 Screen face and bezel plate

| Item | Value | Ratio to W | Tag |
| --- | --- | --- | --- |
| Recline of the screen face | 32.50 | | MEASURED P, front face of the bezel plate. The seat plane of the body has the same normal. |
| Bezel plate, width x length x thickness | 238.9 x 208.55 x 10.0 | 0.885 x 0.772 | MEASURED S and P, bezel plate |
| Window | 201.0 x 152.0 | 0.744 x 0.563 | MEASURED S, bezel plate |
| Border below the window, along the slope | 31.5 | 0.117 | MEASURED S |
| Border above the window, along the slope | 25.0 | 0.093 | MEASURED S |
| Border at each side | 18.95 | 0.070 | MEASURED S |
| Lower edge of the bezel plate, height | 64.86 | 0.240 | MEASURED S |
| Upper edge of the bezel plate, height | 240.75 | 0.892 | MEASURED S |
| Pocket for the LCD at the rear of the plate | 211.0 x 171.0, 7.0 deep | | MEASURED P. The lip around the window is 3.0 thick. |
| Gap between the bezel plate and each cheek | 0.55 | | MEASURED P |
| Seat rail on the inner face of each cheek | 9.9 wide, 4.8 thick | | MEASURED S, body |

The bezel plate is recessed between the cheeks. The recess depth changes with height. Section 6.3 gives it as the cheek projection.

How the bezel plate is held. MEASURED S and H

- The rear face rests on two seat rails, one on each cheek. The lower end stands on a flat ledge of the apron bar.
- Three hooks at the lower end go into a slot in the apron bar. The slot is 4.6 wide. The hooks are 4.0 thick.
- Three hooks at the upper end go into three slots (21.0 x 8.6) in the underside of the speaker plate.
- Two screws go down through the speaker plate into the upper end of the bezel plate. The clearance holes are 2.2 in diameter and the pilot holes are 1.8.
- The screen face shows no fastener.

### 6.3 Cheek

| Item | Value | Ratio to W | Tag |
| --- | --- | --- | --- |
| Cheek thickness (X 120 to 135) | 15.0 | 0.056 | MEASURED P, body |
| Front land of the cheek, width | 4.4 | 0.016 | MEASURED S at Z=150 and Z=155.5 |
| Facet between the side wall and the land, width in X | 10.6 | 0.039 | MEASURED S |
| Facet angle to the side wall, in a true section | 44.9 | | MEASURED P: mean X component of the facet normals is 0.709 |
| Facet width on its slope | 15.0 | 0.056 | ESTIMATED from 10.6 at 45 degrees |
| Front edge of the cheek, shape | One circular arc | | MEASURED F at X=122 and X=-122, 747 points, rms 0.016 |
| Arc radius | 311.6 | 1.154 | MEASURED F |
| Arc center | Y=413.4, Z=-8.1 | | MEASURED F |
| Arc extent | Z=53 to Z=240.5, 41.5 degrees | | MEASURED F |
| Chord of the arc | 221.0 long, 32.1 from vertical | 0.819 | MEASURED F. The chord is parallel to the screen face within 0.4 degrees. |
| Sagitta of the arc | 20.2 | 0.075 | MEASURED F. The sagitta is 0.091 of the chord. |
| Lean of the edge from vertical | 12.3 at the foot, 29.9 at Z=150, 52.1 at Z=238 | | MEASURED S |
| Top of the edge | The last 6.5 mm under the hood seam is straight, at 47 from vertical | | MEASURED S |
| Edge radii | None. The land, the facet and the side wall meet at sharp edges. | | MEASURED S |

Cheek projection: the distance from the cheek land to the plane of the bezel plate front face, normal to that plane. MEASURED S at X=122

| Height | Projection | Ratio to W |
| --- | --- | --- |
| Lower edge of the bezel plate (Z=64.9) | 9.1 | 0.034 |
| Z=100 | 18.9 | 0.070 |
| Z=160.6, the maximum | 25.9 | 0.096 |
| Z=200 | 21.8 | 0.081 |
| Upper edge of the bezel plate (Z=240.8) | 6.2 | 0.023 |
| Mean over the bezel plate | 20.0 | 0.074 |
| Mean over the window | 22.8 | 0.084 |

At the screen center the bezel plate front is about 30.6 mm behind the land in a horizontal section.

The cheek is not a separate strip. It is the front part of a wide band of the side wall. This document calls it the side band. The side band is 66 to 87 mm deep in plan (0.24 to 0.32 W) and stands 20.0 mm proud of the rear side wall. Section 6.7 gives its rear edge. MEASURED S

### 6.4 Sweep and apron

The model has no large sweep. MEASURED S and F

| Item | Value | Ratio to W | Tag |
| --- | --- | --- | --- |
| Fillet at the foot of the screen face, on the cheek land | R 3.9 | 0.014 | MEASURED F at X=122, rms 0.011 |
| The same fillet at the center line | R 3.90 | 0.014 | MEASURED F at X=0.3, rms 0.005 |
| The same fillet at the outer edge of the cheek facet | R 14.4 | 0.053 | MEASURED F at X=134.9, rms 0.020 |
| Fillet center | Y=104.1, Z=54.0 | | MEASURED F. One center for all three fits. |
| Apron between the cheeks | A facet at 43.5 from horizontal | | MEASURED P and S, body |
| Apron facet size | 13.3 deep, 12.6 high, 18.4 on the slope | 0.049, 0.047, 0.068 | MEASURED S |
| Flat ledge above the apron facet | 12.0 deep at Z=64.86 | | MEASURED S. The bezel plate covers it. |
| Shelf | None. The gap between the control panel and the apron is 0.13. | | MEASURED S |

The fillet runs the full width at Y=104.1. Between the cheeks the facet of the apron starts from it. On each cheek the arc of the cheek edge starts from it. The fillet looks larger on the cheeks because the cheek facet widens it from R 3.9 to R 14.4.

### 6.5 Deck and control panel

| Item | Value | Ratio to W | Tag |
| --- | --- | --- | --- |
| Deck part, width x depth x height | 270.0 x 102.55 x 50.0 | 1.000 x 0.380 x 0.185 | MEASURED P, deck |
| Front face, vertical part | 39.36 high | 0.146 | MEASURED S |
| Top edge | A facet at 45.0, 10.63 x 10.63, on the front and on both sides | 0.039 | MEASURED P and S. No radius. |
| Rim flat between the facet and the control panel | 4.37 | 0.016 | MEASURED S |
| Lower facet | None. The front face is vertical down to the underside. | | MEASURED S |
| Plan corner radius | 30.0 | 0.111 | MEASURED F at Z=8 and Z=37, rms 0.011 |
| Front face in plan | Flat for the middle 107.2. Then swept back 3.31 degrees to X=106.7 on each side (3.08 mm). | 0.397 | MEASURED S |
| Border of deck in front of and beside the control panel | 15.0 | 0.056 | MEASURED P |
| Deck walls | 15.0 thick | | MEASURED P |
| Deck floor | 5.0 thick in the middle, with a ledge at Z=15.0 | | MEASURED P |
| Control panel, width x depth | 239.7 x 88.9 | 0.888 x 0.329 | MEASURED B, control panel |
| Control panel plate | 5.0 thick. Top at Z=49.81, 0.19 under the rim. | | MEASURED P |
| Control panel skirt | 34.8 high, 3.65 to 3.75 thick | | MEASURED P |
| Lever hole | 22.0 in diameter at X=-59.9, Y=61.1, with four 5.4 holes on a 32 mm circle | | MEASURED H |
| Button holes in the panel | Six of 30.0 in diameter. Pitch 33 to 34.5 across, 36.0 front to rear. | | MEASURED H |
| Button holes in the deck front face | Two of 24.0 in diameter at X=67.5 and X=96.5, Z=22 | | MEASURED H |

How far the deck is wider than the body. MEASURED P

- Against the side band and the cheeks: 0. The deck sides are flush with the side band.
- Against the rear body: 20.0 mm on each side (0.074 W).

Where the deck ends. MEASURED S

- The deck part ends at Y=102.55, on the front face of the body. The seam is at the foot of the cheeks.
- The body continues the full width of 270 under the side band, back to Y=177.2. That is 0.656 W, or 52 percent of the depth.
- From Y=177.2 to Y=197.2 a vertical facet at 45 degrees in plan returns to the rear body side. The facet is 20 x 20 mm and goes from Z=0 to Z=40.6.
- Above Z=40.6 the return becomes the rear edge of the side band, which leans back.

### 6.6 Hood

| Item | Value | Ratio to W | Tag |
| --- | --- | --- | --- |
| Hood height, seam to top | 69.1 | 0.256 | MEASURED B, hood |
| Hood top above the upper edge of the bezel plate | 75.6 | 0.280 | MEASURED S |
| Tilt of the hood band from vertical | 44.0 | | MEASURED P, hood band and the lip plane of the hood |
| Hood band, visible slope | 58.0 long, from Z=247.25 to Z=288.98 | 0.215 | MEASURED S at X=40 |
| Vertical strip above the slope | 12.4 high at Y=277.2 | 0.046 | MEASURED S |
| Hood top bar (the brow), thickness | 15.0 | 0.056 | MEASURED S at X=0.3 |
| Brow in front of the vertical strip | 15.9 | 0.059 | MEASURED S |
| Nose of the brow | 5.45 high, leans back 7.5 | | MEASURED S and F. It is flat, not round. |
| Top front edge seen from the side | A facet at 42.1 below horizontal, 14.25 long (10.58 deep, 9.55 high) | 0.053 | MEASURED P and S. No radius. |
| Top flat | 30.05 deep, 192.5 wide | 0.111, 0.713 | MEASURED S and P |
| Rear face | Leans forward 16.0 | | MEASURED P |
| Hood side seen from the front | One arc of R 348, rms 0.011 | 1.29 | MEASURED F at Y=286, Z 247.5 to 290 |
| Lean of the hood side | 13.5 at the seam, 21.0 at Z=290, 22.3 at Z=298. The corner radius starts above that. | | MEASURED S |
| Top corner seen from the front | R 20.1 (20.8 in a second fit) | 0.074 | MEASURED F, rms 0.010 |
| Hood width lost on each side, seam to top flat | 37.3 | 0.138 | MEASURED S |
| Side walls of the hood | 15.0 thick, normal to the face | 0.056 | MEASURED S at Y=286 |
| Rear wall of the hood | 13.1 to 14.5 thick, with two openings behind the vent plate | | MEASURED S and P |

How the corners are blended. MEASURED P (area of the hood triangles by normal direction)

- 23 percent of the hood surface has no Y component in its normal. These are the side surfaces. They are extruded along the depth.
- 42 percent has no X component. These are the front, top and rear surfaces. They are extruded across the width.
- 28 percent is axis-aligned.
- 6 percent has X and Y components together. It is a facet strip on the front edge of each side wall, and the frame of the rear openings.

The hood is the intersection of two extruded profiles: the front outline and the side outline. The model has no sphere-like blend. Where the side surface meets the front surfaces, the 45 degree facet of the cheek continues up the edge. The X component of its normals goes from 0.71 to 0.31 toward the top.

Hood projection in front of the screen face. MEASURED S

- At the center line the hood band starts on the line of the screen face. The angled edge of the speaker plate is flush with the bezel plate front within 0.2 mm.
- The screen face (32.5) and the hood band (44.0) meet at a knuckle of 11.5 degrees at the hood seam.
- The side walls of the hood continue the cheek edge. Their front edge leans 43 to 37 degrees from vertical.
- The speaker pods are the foremost part of the hood. Their fronts are vertical at Y=230.3. That is 2.9 mm in front of the upper edge of the bezel plate and 3.0 mm in front of the cheek tops.
- The nose of the brow is at Y=261.3. That is 28.1 mm behind the upper edge of the bezel plate.

The hood does not overhang the screen. It reads as a visor because of the pods and because of the brow over the recessed strip.

Hood band details. MEASURED S, P, H

| Item | Value | Ratio to W |
| --- | --- | --- |
| Width at the lower edge | 242.3 | 0.897 |
| Plate thickness | 2.8 | |
| Speaker pod, outside | 55.1 wide, 39.8 high | 0.204, 0.147 |
| Speaker pod, front opening | 48.0 x 33.0 | |
| Speaker pod, wall | 3.4 to 3.65 | |
| Pod centers | X=73.5 and X=-73.5 | 0.272 |
| Recess for the marquee display at the rear of the plate | 70.1 x 50.5 | |
| Speaker holes in the speaker plate | Two of 45.0 in diameter | |
| Hood rear vent plate | 249.0 x 64.9, 2.0 thick, four louver openings of 34.0 x 6.8 | |

### 6.7 Body: sides, rear and floor

| Item | Value | Ratio to W | Tag |
| --- | --- | --- | --- |
| Taper of the body toward the hood | None. The side faces are vertical at X=135 and X=-135 up to Z=241.4. | | MEASURED P |
| Side step between the side band and the rear body | 20.0 on each side, at 45 degrees in plan | 0.074 | MEASURED P and S |
| Rear edge of the side band, lower part | Leans 28.2 from vertical, from (Y=177, Z=41) to about (Y=260, Z=194) | | MEASURED P and S |
| Rear edge of the side band, upper part | Leans 56.7 from vertical, to about (Y=325, Z=237) | | MEASURED P and S |
| Rear wall, lower part | Vertical from Z=48.3 to Z=171.8, 230 wide | | MEASURED P and S at X=0.3 |
| Rear wall, upper part | Leans forward 11.6 from Z=171.8 to Z=236.6. It has the full width of 270. | | MEASURED P |
| Top of the rear wall | Leans 16.0 for the last 5 mm, as the hood rear | | MEASURED P |
| Rear lower facet | 43.2 from horizontal, 30.6 deep, 28.8 high | 0.113, 0.107 | MEASURED P and S |
| Round under the rear lower facet | R 14.6 | 0.054 | MEASURED F, rms 0.014 |
| End of the floor underside | Y=302.8, 35.2 in front of the rear face | 0.130 | MEASURED S |
| Rear corners in plan | Square. No facet. | | MEASURED S |
| Notches at each rear corner | Four, 3.7 high, pitch 8.0, 13.1 deep, Z=85 to Z=112.7 | | MEASURED S at X=114.5 |
| Pockets high on the rear wall | Two, each 55 wide, 26 high, about 14 deep, with a sloped upper face | 0.204, 0.096 | MEASURED S at X=72 and Z=229 |

The upper rear is wider than the lower rear. The side step line divides them on each side.

Openings and vents. MEASURED S unless noted

| Item | Value |
| --- | --- |
| Rear wall, power inlet opening | 28.0 wide, 42 to 47.6 high, at X=-90.5 to -62.5 |
| Rear wall, low slot | 26.0 x 8.5 at X=62.4 to 88.4, Z=53.9 to 62.4 |
| Left side wall | One round opening of 38 with four holes of 3.8 on a 32 mm square (the pattern of a 40 mm fan). One round opening of 20. |
| Right side wall | Three openings of about 15 x 15 at Z=24 to Z=39 |
| Floor, left field | 32 slots of 2.0 x 28.75 at 3.5 pitch, in two rows. Open area 1840 mm2. |
| Floor, right rear field | 20 slots of 2.0 x 24.7 to 29.2 at 4.0 pitch. Open area 1078 mm2. |
| Rear lower facet | 82 square holes of 3.0 at 6.0 pitch, in three rows. Open area about 740 mm2. |
| Upper rear wall | Holes of 3.0 x 3.9 at 8.0 pitch. 68 holes in five rows (8, 8, 8, 20 and 24). ESTIMATED: the count is from the rear view. |

### 6.8 Walls, bosses and fasteners

| Item | Value | Tag |
| --- | --- | --- |
| Typical wall | 15.0. Floor, rear wall, rear side walls, cheeks, deck walls and hood top have this thickness. | MEASURED P and S |
| Wall build | The mesh is solid. The slicer makes two skins of about 1.26 mm with 15 percent infill between them. | SOURCED (slicer settings) |
| Plastic volume against mesh volume, body | About 34 percent: 1223 g of PETG for 2811 cm3 of mesh | ESTIMATED with a density of 1.27 g/cm3. The mass includes supports. |
| Thinnest wall of the body | 3.75, at an inner pocket of 48 x 103 in the right side wall | MEASURED P |
| Thinnest plates | Vent plate 2.0. Hood band plate 2.8. Bezel plate lip 3.0. Pod walls 3.4. Skirt of the control panel 3.65. Deck floor and control panel plate 5.0. | MEASURED P |
| Ribs | None in any part | MEASURED S (all sections) |
| Screw bosses | Four standoffs on the floor: 8.0 in diameter, 6.4 high, with a spigot of 5.0 x 2.0 and a pilot hole of 2.0 | MEASURED H, body |
| Screw holes | Pilot 1.8. Clearance 2.2. Counterbores 4.0, 5.0, 6.0 and 7.0. All screws go into plain plastic. | MEASURED H |

All other screws go into pilot holes in a thick wall or in a lug. The model has no insert and no nut pocket.

Joints between the parts of the designer. MEASURED S and H

| Joint | Alignment | Fasteners |
| --- | --- | --- |
| Deck to body | Two side lugs on the body, each 7.0 thick, 30 high and 17.5 long, in deck pockets with 0.5 to 1.0 clearance on each side. Five floor lugs on the deck, each 20 wide, 5.0 thick and 10.5 long, at 50 pitch, in slots in the body floor. | Two cross screws on each side, from inside the deck. Four screws from the underside through the floor lugs. |
| Control panel to deck | The skirt in the deck opening. The flange between the deck front wall and the apron bar, with 0.13 to 0.2 clearance. | Two screws from the deck underside, in counterbores 11 deep |
| Hood to body | Four lugs on the body top, each 32.0 x 7.0 and about 9 high, in hood pockets | One cross screw through each side lug. Four vertical screws along the rear, through the rear openings of the hood. |
| Hood band to hood | The plate behind two lips of the hood. The upper flap in a slot 4.0 wide. The lower facet on the body top. | None. The hood holds it on the body. |
| Bezel plate | Seat rails, six hooks | Two screws through the speaker plate |
| Speaker plate to body | Ledges and three rear lugs | Two screws |
| Vent plate to hood | Hole pattern | Six screws, clearance 3.0 |

No fastener is visible on the front, the sides or the top. The screws are under the floor, inside the deck, inside the hood and on the hood rear.

### 6.9 The cut of the body

The remix author cut the body with the cut tool of the slicer. The cut data is in `Metadata/cut_information.xml`: one cut identifier (6100) on six objects, with 28 connectors. SOURCED

| Item | Value | Tag |
| --- | --- | --- |
| Horizontal seam | Z=125.0. It crosses both cheeks, both side walls and the rear wall. | MEASURED P |
| Center seam | X=0. It crosses the floor, the rear wall and the apron bar. | MEASURED P |
| Transverse seam, right half | Y=222.7, below Z=125 | MEASURED P |
| Transverse seam, left half | Y=239.7, below Z=125 | MEASURED P |
| Dowels | Round, 5.0 in diameter, 3.0 long. A dowel is printed on one piece. | MEASURED B |
| Sockets | 5.0 in diameter, 3.1 deep. No radial clearance in the model. | MEASURED B |
| Dowels on the horizontal seam | 10 | SOURCED and MEASURED B |
| Dowels on the center seam | 8 (2 in the upper pieces, 6 in the lower pieces) | SOURCED and MEASURED B |
| Dowels on each transverse seam | 5 | SOURCED and MEASURED B |
| Bed contact of one upper piece | 41.8 cm2 for a height of 132.2 | MEASURED P |

The two transverse seams are 17 mm apart, so no point has four pieces. The description in the metadata says that the author glued the pieces with cyanoacrylate and then filled the seams with putty.

## 7. Comparison with the photos of the reference cabinet

Section 1 of `docs/research/cabinet-references.md` reads the photos of the reference cabinet. The model shares these forms with those readings:

- The cheek edge has a wide facet between the side wall and the front.
- The deck is a tray at the front only, and the body behind it is narrower.
- The upper rear stands proud of the lower rear, with a step line between them.
- Two recessed pockets are high on the rear wall.
- Short horizontal slots are near the rear corners.
- The hood is a separate module on top of the body.

The model differs from those readings in these points:

| Item | Photo reading of the reference cabinet | Model |
| --- | --- | --- |
| Deck width against body width | 1.15 to 1.25 | 1.00 against the cheeks, 1.174 against the rear body |
| Overall height against body width | 1.6 to 1.7 | 1.172 |
| Hood height against body width | About 0.35 | 0.256 (0.280 above the bezel plate) |
| Recline | 20 to 25, low confidence | 32.5 |
| Lower facet on the deck faces | Present | Absent. The model has a facet on the top edge. |
| Rear door | Present | Absent |
| Hood projection | A visor in front of the screen face | No overhang. Pods and brow only. |

## 8. Lessons for this project

### 8.1 The look

These forms and proportions make the model read as an Astro City. Each value is a ratio to the body width at the cheeks.

1. The side band is flush with the deck. The rear body is narrower by 0.074 on each side. The step line leans 28 degrees from vertical.
2. The cheek front edge is one arc. Its chord is parallel to the screen face. Its sagitta is 0.075 (0.091 of the chord), its radius is 1.154 and it turns 41.5 degrees.
3. The screen is deep between the cheeks. The cheek projection is 0.034 at the lower edge of the bezel plate, 0.096 at the screen center and 0.023 at the upper edge.
4. The cheek is 0.056 thick. A 45 degree facet takes 0.039 of that on the outside. The same facet runs along the deck top edge and up the hood side.
5. The screen face reclines 32.5 degrees. The hood band tilts 11.5 degrees more. The hood has no overhang.
6. The hood is 0.256 high. Its sides lean in 13.5 to 23 degrees on a large arc. Its top flat is 0.713 wide. Its top corners have a radius of 0.074.
7. The hood top front edge is a facet of 0.053, not a radius. The brow is 0.056 thick and stands 0.059 in front of a recessed strip.
8. The speaker pods are 0.204 wide and 0.147 high. Their centers are at 0.272 from the center line. Their fronts are vertical.
9. The deck is 0.185 high and 0.380 deep in front of the body. Its plan corners have a radius of 0.111. Its front face is bowed by 3.3 degrees outside the middle 0.397.
10. The model has no shelf. A 43.5 degree apron facet of 0.049 by 0.047 starts at the rear edge of the control panel.
11. The rear wall is vertical up to 0.636, then leans 11.6 degrees. A 43 degree facet of 0.113 by 0.107 cuts the rear lower corner.
12. The depth is 1.252 and the height is 1.172.

Suggested values for the parameters of `cad/params/cabinet.csv`, for a body width of 422 mm. Each scaled value is the model value times 1.563.

| Parameter | Value now | Model | Ratio to W | Suggested | Note |
| --- | --- | --- | --- | --- | --- |
| `recline` | 22 | 32.5 | | 25 | 32.5 is outside the 15 to 25 range of the ergonomics study. 25 is the nearest value in the range. |
| `hood_h` | 135 | 75.6 above the bezel plate | 0.280 | 118 | |
| `hood_r` | 35 | No radius. A facet of 10.6 deep by 9.6 high. | 0.039 by 0.035 | 0, with a facet of 16.5 by 15 | The model supports a facet, not a radius. |
| `hood_corner_r` | 40 | 20.1 | 0.074 | 31 | The lean of the hood sides does more for the look than this radius: 13.5 to 23 degrees, 58 mm lost on each side at 422. |
| `hood_tilt` | 10 | 44.0 | | `recline` + 11.5 | 36.5 with a recline of 25. This keeps the knuckle between the screen face and the hood band. |
| `hood_overhang` | 30 | 0 | 0 | 0 | The model gets its visor from a brow of 0.059 (25 mm at 422) and from the pods. |
| `cheek_proud` | 10 | 9.1 at the ends of the bezel plate, 25.9 in the middle, mean 20.0 | 0.034, 0.096, 0.074 | 31 as one value | A better match is an arc: 14 at the lower edge, 40 in the middle, 10 at the upper edge. |
| `sweep_r` | 45 | 3.9 on the cheek land, 14.4 at the outer edge of the cheek facet | 0.014, 0.053 | 6 | Between the cheeks the model has an apron facet in place of a sweep: 21 by 20 at 422. |
| `deck_flare` | 24 | 0 against the cheeks, 20.0 against the rear body | 0, 0.074 | 0, with a side step of 31 | The wide deck of the model comes from a narrow rear body. |
| `deck_facet_h` | 30 | No lower facet | | No value | The model does not support this parameter. Its facet is on the top edge: 10.6 at 45 degrees, 16.6 at 422. |
| `deck_facet_in` | 14 | No lower facet | | No value | As `deck_facet_h`. |
| `deck_corner_r` | 22 | 30.0 | 0.111 | 47 | |
| `body_taper` | 6 | 0 | 0 | 0 | The body sides are vertical. The hood sides lean in. |
| `skin_t` | 5 | 15.0 for the floor and the rear wall, 5.0 for small plates | | 5 for plates, 12 to 15 for large walls | Wall thickness belongs to the print process. It does not scale with the cabinet. |
| `side_t` | 12 | 15.0 | 0.056 | 15 as a minimum | 23 keeps the proportion of the cheek. A land of 0.29 and a facet of 0.71 of the thickness keep its section. |

The model also gives values for parameters that the task did not name. `shelf_depth` is 0 in the model. `deck_nose` is 15.0 (0.056, 23 mm at 422). `deck_edge_r` is a 45 degree facet of 10.6 (16.6 mm at 422) in place of a radius.

If the cheek edge becomes an arc, set it from the screen face and not from the model. The chord is parallel to the screen face. The sagitta is 0.091 of the chord. The arc then turns 41.5 degrees. For a screen face of 455 mm that gives a sagitta of 42 mm and a radius of 643 mm. ESTIMATED

### 8.2 Printing and assembly

Module division of the model:

- Six modules make the outside: deck, control panel, body, bezel plate, hood, hood band. Two more plates are inside or behind: the speaker plate and the hood rear vent plate.
- Each seam between modules is on a line of the form. The deck seam is at the foot of the cheeks. The hood seam is horizontal at the top of the cheeks.
- The neighbors of the control panel and of the bezel plate capture these two plates. The front shows no fastener.

Things to copy:

- Put module seams where the form changes direction. A seam on a line of the form needs no filler.
- Join modules with lugs in pockets and with screws from hidden faces. The model uses 0.5 to 1.0 mm clearance on each side of a lug.
- Use lugs in two directions at one joint. The side lugs of the deck joint carry vertical load. The floor lugs carry pull.
- Capture each removable plate between two fixed parts, and release it with screws from below or from inside.
- Use one facet width on the deck edge, the cheek edge and the hood edge. A seam then crosses the facet at a right angle and is easy to align.
- Offset the transverse seams of the left half and the right half. No point then has four pieces.
- Print each flat plate with its visible face on the bed.
- Put a long part on the bed diagonal. A 256 mm bed takes a part of 270 x 115 mm at 45 degrees.

Things to avoid:

- Do not cut through a visible face. The cut at Z=125 crosses both cheeks, both sides and the rear wall. The cut at X=0 crosses the apron. The author had to fill and paint these seams.
- Do not rely on dowels of 5 x 3 mm with no clearance and glue. They align the pieces and carry no load. The builder of the Mute City cabinet reported gaps with this method.
- Do not print the cheeks upright if the surface matters. The arc and the facet lean 12 to 52 degrees from vertical, so the layers show as steps.
- Do not print tall wall pieces on a small footprint. An upper body piece is 132 mm high on 42 cm2 of bed contact.
- Do not keep the hood as one part at a larger size. At 422 it is 418 mm wide. It prints on its rear face and needs supports under the brow.
- Do not copy the screw size. Pilot holes of 1.8 in plain plastic suit a 2 kg cabinet. ESTIMATED: a cabinet of 5 kg or more needs larger screws with inserts or nuts.
- Do not copy the closed rear wall. The model has no rear door, and this project needs one.
- Do not copy the deck depth. 0.380 of the width is short for adult hands, as users of the model report.

Notes for a cabinet of about 470 x 520 x 620 mm on a 256 mm bed:

- A grid cut needs at least two pieces across, three in depth and three in height. That is 18 body pieces. The Mute City cabinet has 16. ESTIMATED
- The side step line, the apron top, the hood seam and the inside corners of the floor are lines of the form. Seams there stay hidden.
- The center seam is acceptable in the floor and in the rear wall. It is not acceptable in the apron and in the hood top, which the player sees.
- With walls built as in the model, the outside area gives about 6 kg and about 170 hours. ESTIMATED from the area ratio of 3.1 and from 1950 g and 55.5 h for one model
- The model has no ribs. Its 15 mm sandwich walls give flat inner faces, and a dowel or a screw can go at each point of a wall.

## 9. Not determined

- The height of the feet. The model has recesses for feet and no feet.
- The terms of the license. The files give the name of the license only.
- The fit of the printed parts. All clearances in this document are those of the model.
- The exact depth of the bezel plate on its seat. It is known within 0.5 mm (section 4).
- The position of the two speaker grilles. They are not placed.
- The type and the length of the screws. The files give hole diameters only.
- The shape of the body before the cut as a single file. The six pieces give the same shape, and the download has no uncut body.
- The print settings of the original designer. The settings in section 3 are those of the remix author.
