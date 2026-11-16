# The print pieces with their joints

This document describes the 32 print pieces of the shell as printable parts. The split (`cad/candybar/shell/split.py`) cuts the hollow skin into plain pieces. `cad/candybar/shell/pieces.py` gives each piece its joints. Decision record 0006 sets the rules: each seam is a joint and a rib, a joint is rigid, and the pieces locate each other.

The values of the joint are in `cad/candybar/shell/joints.py` (`Joint`, `OtherJoints`). The values that say how the joint goes on a seam are in `pieces.Build` and `pieces.Floor`.

The owner chose ABS on a Qidi Q2 on 2026-11-14 (decision record 0008). The piece limit is now 248 x 248 x 250, and the masses use 1.05 g/cm3. The split and the joint stay as they are. The section "What ABS changes at a joint" gives the effects. The section "On the main line" at the end gives what changed when this package was merged.

## How to build

```
CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh candybar.shell.pieces                        # every piece, the files and the checks
CANDYBAR_PIECES=pilot  CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh candybar.shell.pieces # the two pilot pairs only
CANDYBAR_PIECES=check  CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh candybar.shell.pieces # the checks again, on the files
CANDYBAR_PIECES=views  CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh candybar.shell.pieces # the folders for the sheets
cad/.venv-tools/bin/python cad/tools/draw_pieces.py                                                  # the sheets and report.md
CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc                 # shell.FCStd
cad/test.sh test_pieces                                                                              # the tests
```

The build needs the skin in the cache of the split and the outer solids of the default build (`cad/out/shell-rev7/*.brep`). The first run cuts the skin again and keeps the plain pieces in `cad/out/pieces/cache`. That cut takes 3 minutes. The full build takes 32 minutes.

The build writes these files into `cad/out/pieces/`:

- One BREP file and one STL file for each piece.
- `manifest.json` and `edges.json`, for the renders.
- `seams.json`: what the generator made on each seam.
- `check.json`: the checks of the whole set.
- `joints/`: the added solids alone, for `tools/face_check.py`.
- `report.md`: the tables of this document, made by `tools/draw_pieces.py`.
- `sheets/`: the sheets.
- `shell.FCStd`: the assembly.

## The joint as built

Joint 1 of `joints.py` is on every bonded seam of the walls and of the hood. The numbers that follow are the values of `Joint`.

| Part of the joint | Value | Where |
| --- | --- | --- |
| Flange | 12 inward of the skin, 6 thick | On both pieces, on the inside |
| Gusset | 45 degrees, from the flange tip to the skin, 12 high | On both pieces |
| Key | 4 wide, 1.5 high, 8 to 12 from the outer face | On the piece with the pilot holes (one exception, see below) |
| Groove | The key with 0.2 on each side, 0.5 deeper, a chamfer of 0.3 at its mouth | In the other piece |
| Screw | Thread-forming, 3.0 x 16, 9 from the outer face, pitch 60 | Square to the seam |
| Pilot hole | 2.25 diameter, 11 deep, counterbore 3.2 x 0.5 | In the flange and the gusset of one piece |
| Clearance hole | 3.4 diameter | Through the flange of the other piece |
| Head pocket | 9 diameter | Through the gusset of that piece |
| V | 0.8 deep, 1.0 wide over the two pieces | On the outer edge of each seam that the owner fills |
| Bond line | 0.1 | The slab that the split removes (`split.KERF`) |

The pilot hole of `Joint` is open until the coupon decides. The pieces use 2.25, the table value for PET (`pieces.joint`).

### How the generator makes it

The generator works in the plane of a seam.

1. A plain piece has one flat cut face on each seam polygon. This face is the section of the wall.
2. The edges of the cut face that lie on the outside of the form are the outer line of the seam.
3. The generator makes the outer line simple. An edge shorter than 4.5 (an edge break, a step of 1 mm) becomes a sharp corner. An arc of a radius of 25 or more stays an arc. A tighter curve becomes chords of 6 or less. The result has straight segments and wide arcs only.
4. The section of the joint is a polygon in (u, z). u is the distance inward from the outer line. z is the distance into the piece. The generator extrudes this section along each straight segment and revolves it along each arc.
5. Where two segments open toward the inside, the generator revolves the section about the corner. Where they close, the two solids overlap and make a mitre.
6. The generator fuses these solids. Then it keeps only the part that is inside the outer form.
7. The cut faces of the other seams, the printed floor and the zone round the rear door trim the result. Only a solid that touches the piece stays.
8. The face of the flange on the seam plane is the mating face. The screws, the key and the groove are made where the mating faces of the two pieces lie on each other.

The outer face of the cabinet does not change, apart from the V. The simple line is used for the inside faces only.

### The three cases

- **A straight seam.** Example: D2, between a deck side and a lower piece. The outer line goes across the deck border, round the deck edge and down the side. The flange follows it.
- **A seam in a crease.** Example: B1, in the crease of the rear shelf. Above the seam the wall of the upper piece leaves the seam plane outward at 45 degrees. The generator finds this for each segment of the outer line. It tests points 1 mm and 5 mm outside the line at the depth of the flange. On such a segment the flange starts 8 mm outside the outer line, and the form trims it. The flange then fills the corner up to the wall. There is no gusset on that segment, because the wall itself carries the flange. A screw cannot have its thread on that side, because the pilot hole needs the gusset. The generator puts the pilot holes in the other piece.
- **Three pieces meet.** Example: S1 and L1, where a lower piece, a rear lower piece and a middle piece meet. The flange of each piece ends at the cut face of the next seam. The flanges of two seams on one piece fuse into a corner. No flange enters the volume of another piece. The node plate of the joint sheet (joint 4) is not modelled.

### Which piece gets the screw heads

The generator puts candidate screws on each run of the mating face at the pitch of 60. A run ends at a corner of the outer line. A run shorter than 22 has no screw.

A screw fits when these conditions are true:

- The pilot hole is in the flange and the gusset of its piece.
- The pilot hole and the head pocket stay 1.2 from the outside of the form.
- A shaft of 8 mm has 40 mm of clear length behind the head. This is a 25 mm bit in a flat ratchet.

The generator tries both directions. The heads go into the piece where more screws fit. If the two counts are equal on a level seam, the heads go into the upper piece.

A screw that does not fit is left out. The seam table gives the count for each seam.

The key is on the piece with the pilot holes, as `joints.py` has it. There is one exception. A key must not stand on a face that lies on the printer bed. If the seam face of the pilot piece lies on the bed, the key goes on the other piece, and the groove goes into the pilot piece. This occurs where the screwdriver comes from below (L1 behind the band, B1) and on the hood centre, which prints on a cut face.

## The floor

Decision record 0006 has the floor as a rigid printed part. The owner set its thickness to 10 mm (2026-11-11). The split divides the floor into nine tiles on the seams BA1 (x = -106 and 106), BA2 (y = 194) and BA3 (y = 357).

The skin of the walls reaches the table round the floor. Thus the floor lies inside the walls. It does not lie under them. This changes joints 2 and 3 of the joint sheet. The values are in `pieces.Floor`.

- **Foot flange (joint 3 as built).** Each wall piece that stands on the table has a foot flange. It lies on the table, 16 wide from the outline of the cabinet and 5 thick. It is also the foot of the piece on the printer bed. The plain wall is only 4.3 wide at the table.
- **Rebate.** The edge of the floor is 5 inward of the outline of the cabinet. Under its edge the floor has a rebate, 16.3 wide and 5.2 high. The rebate lies on the foot flange. When a person lifts the cabinet, the foot flanges carry the floor from below.
- **Half-lap (joint 2 as built).** The lap is 20 wide and each half is 5 thick. A side tile lies under the centre tile beside it. A middle tile lies under the front tile and the rear tile. With this order no tile is longer than the bed.
- **Cones.** A cone of 8 x 3 on the lower half of a lap goes into a socket of the upper half (clearance 0.15). The cones locate the tiles.
- **Screws.** All floor screws are the same: thread-forming, 3.5 x 9.5, countersunk, from above. A screw of 9.5 does not come through a floor of 10. The lap screws alternate with the cones at a pitch of 25. The foot screws are at a pitch of 80 along the foot flange.
- **Notch.** The skin has a web between the deck and the body at y = 207, near each side. It stands in the plan of the floor. The tiles have a notch round it, with 0.5 of clearance.

A tile prints flat. The rebate and the upper half of each lap overhang when the bottom face is on the bed. The lower half of each lap overhangs when the top face is on the bed. The piece table gives the orientation with the smaller overhang. These faces are not seen.

### Where the loads go

The hardware stands on the top face of the floor, at z = 10 (`fit.Layout.floor_t`).

- **Power supply** (3.27 kg). It stands at x -223 to -73 and y 386 to 536. That is on tile floor rear side L and, for its last 33 mm, on tile floor rear centre. It lies across seam BA1 on the left. On the table the load goes straight down through the tiles and the pads. In a lift, tile floor rear side L rests with its rebate on the foot flanges of rear lower L, on two edges. Tile floor rear centre rests on the lower half of the lap of floor rear side L and on the foot flange of the rear wall.
- **Hub** (0.2 kg). It stands at x 176 to 221 and y 242 to 352. That is on tile floor middle side R only. This tile rests on the foot flange of lower R.
- **Centre column.** The three centre tiles touch a wall only at the front and at the rear. In a lift they rest on the lower halves of the laps of the six side tiles. The middle centre tile has no wall at all: the laps of the two middle side tiles carry it, and its own laps go under the front and the rear centre tile.

The foot flanges carry the floor by contact. The screws and the bond hold the tiles down on the flanges and together.

## The ribs

`structure.py` calls for ribs 8 high and 3 thick, at most 110 apart. A panel gets a rib when its hand estimate (`structure.plate_deflection`, a finger push of 20 N) is more than 0.3 mm. Each rib stands upright in the print orientation of its piece. Thus it needs no support.

| Piece | Rib | Panel | Estimate without the rib (mm) | Result |
| --- | --- | --- | --- | --- |
| middle R, middle L | In the plane y = 330 | Side band between L1 and B1, 127 x 159 | 0.33 | Made, from the flange of L1 to the flange of B1 |
| middle R, middle L | In the plane y = 460 | Side of the lower body between L1 and B1, 136 x 177 | 0.39 | Made. It is 50 in front of the cut-ins (y 510) |
| rear lower R | In the planes x = 78.5 and x = 156.9 | Lower rear wall below the door, 116 x 211 | 0.34 | Made, from the floor zone to the flange of L1 |
| rear lower L | In the planes x = -78.5 and x = -156.9 | The same | 0.34 | Left out. The power supply stands against this wall: less than half of each rib is clear of it |

The side of the lower body below L1 has an estimate of 0.27 mm. It gets no rib. The upper rear wall between the hand-holds has 0.19 mm. It gets no rib, and thus no rib is near a hand-hold.

The make-up air inlet of `structure.INLET` (x 95 to 205 on the lower rear wall) is not in the skin yet. The rib at x = 156.9 of rear lower R crosses it. The package that makes the inlet must move this rib or make it a bar of the grille.

## The seams

| Seam | Pieces | Flange and gusset (cm3) | Mating run (mm) | Pairs with a key | Screws placed of the candidates | Heads in | Least room behind a head (mm) | What was done |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | middle, upper | 171 | 530 | 2 of 2 | 4 of 10 | middle | 134 | Seam in the crease of the rear shelf. The upper piece is the crease side: its flange starts outside the outer line and has no gusset there. The pilot holes are in the upper piece where its wall is upright (in front of the crease), and the screwdriver comes from below. Six of ten screws are left out: in the crease the pilot hole has no gusset, and at the rail the wall leans. The key is on the middle piece. |
| D1 | deck side, lower | 23 | 16 | 0 of 4 | 0 of 0 | - | - | Three short faces under the control panel. Each has a stub of flange. The run is too short for a key or a screw. D2 beside it holds the pieces. |
| D2 | deck side, lower | 76 | 206 | 2 of 2 | 4 of 4 | deck side | 148 | As defined. The flange of deck side R is cut back for the body of the fourth USB socket. |
| F1 | deck nose, deck side | 31 | 74 | 2 of 2 | 0 of 2 | - | - | Flange and key as defined. No screw: the deck is 72 high, and the room behind a screw head is less than 40. |
| F2 | deck nose, deck side | 41 | 116 | 0 of 2 | 0 of 2 | - | - | Flange as defined. It fills the section of the deck border. No key: the outer line turns often, and no straight run is long enough for one. No screw, for the same reason as F1. F1 is on the same plane between the same two pieces, and its key locates them. |
| H1 | hood centre, hood side | 266 | 705 | 2 of 2 | 10 of 10 | hood side | 67 | As defined, round the section of the hood. The flange is cut back for the room of the marquee modules and of the speaker drivers. |
| L1 | lower, middle, rear lower | 237 | 645 | 4 of 4 | 8 of 10 | middle, rear lower | 54 | Two levels. In front of the band the wall leans in above the seam, so one of two screws on each side has no room for a screwdriver. Behind the band the heads are in the rear lower piece (the screwdriver comes from below), and the key is on the rear lower piece. The flange passes 10 under the lowest cut-in and does not reach the stepped skin behind it. On the left it is cut back for the air space of the power supply's fan. It stops 10 from the door opening. |
| P1 | apron, lower | 114 | 252 | 2 of 2 | 4 of 4 | apron | 200 | As defined. The flange follows the sweep and the rail. |
| R1 | middle, upper rear | 3 | 0 | 0 of 2 | 0 of 0 | - | - | 12 long, and all of it is in the 10 mm zone round the door opening. A stub of flange only: no key and no screw. The frame of the door opening must join these two pieces. |
| R2 | rear lower | 18 | 34 | 1 of 1 | 1 of 1 | rear lower | 70 | The flange is cut back for the stowed cables, which stand against the rear wall on the centre line. A mating run of 34 mm and one screw are left. |
| R3 | upper, upper rear | 117 | 295 | 2 of 2 | 2 of 4 | upper rear | 188 | Flange and key as defined. One screw of two on each side: the other has 30 mm of room for the screwdriver. |
| R5 | upper rear | 62 | 149 | 1 of 1 | 2 of 2 | upper rear | 58 | As defined. The flange starts 10 above the door opening. |
| S1 | lower, middle, rear lower | 81 | 267 | 4 of 8 | 4 of 4 | lower | 93 | Seam in the crease of the band, on three planes. The lower piece is the crease side (the band leaves the seam at 45 degrees in plan). The pilot holes are in the rear lower piece. On the left the flange is cut back for the power supply and its plugs. |
| W1 | brow, upper | 46 | 104 | 0 of 2 | 2 of 2 | upper | 112 | Flange as defined, and one screw on each side. No key: no straight run is long enough (as F2). The flange is cut back by 18 mm3 for the room of the monitor's top clamp. |

The values are for both sides of the cabinet together. "Room behind a head" is the clear length for the screwdriver, measured past the finished pieces, up to 200.

Seams that this package does not make:

- DR, the outline of the rear door, and R4, the centre seam of the door. The door and the frame of its opening are another package. The two door halves are plain pieces here.
- G, the hood on the body top (joint 7), the bezel plate, the control panel and the USB plate. These are service seams of the form. The split does not cut them.

## The pieces

| Piece | Print box (mm) | On the bed | Face on the bed (cm2) | Volume (cm3) | Joints, foot and ribs (cm3) | Mass at 1.27 g/cm3 (g) | Faces over 45 degrees (cm2) | The same on the plain piece (cm2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deck nose | 223 x 223 x 72 | upright, on the bed diagonal | 43.7 | 154.5 | 42.2 | 196 | 64.3 | 67.5 |
| deck side R | 186 x 185 x 72 | upright | 42.6 | 190.6 | 38.3 | 242 | 104.7 | 109.0 |
| deck side L | 186 x 185 x 72 | upright | 42.6 | 191.8 | 39.5 | 244 | 103.8 | 109.0 |
| apron | 219 x 219 x 130 | on its rear edge, on the bed diagonal | 0.0 | 180.4 | 36.8 | 229 | 55.6 | 39.2 |
| lower R | 184 x 184 x 136 | upright | 31.2 | 226.6 | 73.3 | 288 | 55.6 | 64.2 |
| lower L | 184 x 184 x 136 | upright | 31.2 | 224.7 | 71.4 | 285 | 55.5 | 64.2 |
| middle R | 211 x 210 x 178 | upright, on the bed diagonal | 18.0 | 301.9 | 68.3 | 383 | 35.5 | 9.8 |
| middle L | 211 x 210 x 178 | upright, on the bed diagonal | 12.6 | 296.8 | 63.2 | 377 | 40.2 | 9.8 |
| upper R | 205 x 205 x 131 | upright | 26.6 | 231.3 | 49.0 | 294 | 56.3 | 36.1 |
| upper L | 205 x 205 x 131 | upright | 26.6 | 231.2 | 49.0 | 294 | 56.3 | 36.1 |
| brow | 178 x 178 x 47 | upright | 0.0 | 60.1 | 16.0 | 76 | 42.2 | 17.8 |
| upper rear R | 189 x 189 x 143 | upright | 8.5 | 199.6 | 38.6 | 253 | 30.1 | 25.2 |
| upper rear L | 189 x 189 x 143 | upright | 8.5 | 201.5 | 40.5 | 256 | 29.2 | 25.2 |
| rear lower R | 232 x 231 x 118 | upright | 56.1 | 257.7 | 67.5 | 327 | 8.0 | 0.3 |
| rear lower L | 232 x 231 x 118 | upright | 56.2 | 242.7 | 52.5 | 308 | 5.7 | 0.3 |
| door half R | 211 x 165 x 4 | outer face on the bed | 348.4 | 139.7 | 0.0 | 177 | 0.0 | 0.0 |
| door half L | 211 x 165 x 4 | outer face on the bed | 348.4 | 139.7 | 0.0 | 177 | 0.0 | 0.0 |
| hood centre | 148 x 139 x 213 | on a cut face | 41.6 | 428.7 | 92.0 | 544 | 12.6 | 3.1 |
| hood side R | 139 x 129 x 148 | upright | 17.5 | 299.2 | 35.8 | 380 | 128.2 | 135.9 |
| hood side L | 139 x 131 x 148 | upright | 17.5 | 301.9 | 38.5 | 383 | 128.0 | 135.9 |
| speaker form R | 94 x 76 x 13 | front face on the bed | 52.1 | 67.7 | 0.0 | 86 | 0.0 | 0.0 |
| speaker form L | 94 x 76 x 13 | front face on the bed | 52.1 | 67.7 | 0.0 | 86 | 0.0 | 0.0 |
| logo form | 160 x 160 x 5 | front face on the bed | 87.8 | 43.9 | 0.0 | 56 | 0.0 | 0.0 |
| floor front side R | 184 x 151 x 10 | flat, top face on the bed | 230.6 | 218.5 | - | 278 | 30.7 | - |
| floor front side L | 184 x 151 x 10 | flat, top face on the bed | 230.6 | 218.5 | - | 278 | 30.7 | - |
| floor front centre | 212 x 184 x 10 | flat, top face on the bed | 385.3 | 323.6 | - | 411 | 2.4 | - |
| floor middle side R | 203 x 155 x 10 | flat | 289.5 | 253.5 | - | 322 | 17.7 | - |
| floor middle side L | 203 x 155 x 10 | flat | 289.5 | 253.5 | - | 322 | 17.7 | - |
| floor middle centre | 212 x 203 x 10 | flat | 348.1 | 345.3 | - | 439 | 62.5 | - |
| floor rear side R | 173 x 155 x 10 | flat, top face on the bed | 208.7 | 194.8 | - | 247 | 28.5 | - |
| floor rear side L | 173 x 155 x 10 | flat, top face on the bed | 208.7 | 194.8 | - | 247 | 28.5 | - |
| floor rear centre | 212 x 173 x 10 | flat, top face on the bed | 362.7 | 302.6 | - | 384 | 2.0 | - |

### Print

Each piece prints in the orientation that the split gives it. The joints are on the inside. The only change on the outside is the V on the edges of the seams. Thus the overhang of the faces that show is that of the plain pieces (the report of the split); it was not measured again on the finished pieces. The table gives all faces over 45 degrees, inside and outside. The gussets are at 45 degrees and do not count.

Faces over 45 degrees that the joints add, inside the piece (cm2): apron 16.4; middle 25.7; upper 20.2; brow 24.4; upper rear 4.9; rear lower 7.7; hood centre 9.5. They are the ends of flanges and ribs, the roofs of the grooves (2 mm above the bed, a bridge of 4.4) and of the notches for the hardware, and the seam face that follows.

**The middle pieces stand on two levels.** Seam L1 is at z = 116 behind the band and at z = 134 in front of it. A middle piece stands on its L1 face behind the band. Its L1 face in front of the band is then 18 mm above the bed: 17.5 cm2 of flange and skin on each middle piece. This face needs support, and it is a bond face. The plain piece of the split has the same step (its skin section only). A fix is a change of the split, which is not in this package: for example a level L1 at one height, or a print of the middle piece with its side on the bed.

## What ABS changes at a joint

The owner prints the cabinet in ABS on an enclosed printer (2026-11-14). The joint does not change. No value was changed for ABS. `docs/research/abs-switch.md` has the earlier study.

### The bond faces

After the dry assembly with screws, the seams can be solvent welded. A weld needs two flat faces in contact and a way for the solvent to get to them.

| Joint | Bond faces | Gap as modelled | How the solvent gets there |
| --- | --- | --- | --- |
| Joint 1, wall to wall | The cut face of the skin and the face of the flange on the seam plane, on both pieces: a flat band 16 wide along the seam | 0.1 | From inside, along the tip of the flange, which is open over the full length of the seam. From outside, along the V |
| Foot flange under the floor | The top face of the foot flange and the roof of the rebate of the tile: level, 11 wide | 0.2 | From above, down the gap between the edge of the floor and the wall (0.6 at the sides, 3.7 at the rear) |
| Half-lap of two tiles | The two level faces of the lap, 20 wide | 0.1 | From above and from below, along the two lines where the tiles meet (0.2 wide) |

The key and the groove are not bond faces. Their gap is 0.2 on each side and 0.6 at the bottom, which is too wide for a solvent with no filler in it.

The bond faces are flat by construction: each is a part of the seam plane. The screws pull the two faces together while the weld sets. Where a seam has no screw (F1, F2, D1, R1), a clamp must do this.

A bond face that prints on support is less flat. One seam face does (see "Print"): the L1 face of each middle piece in front of the band.

### How each long flange is held flat on the bed

ABS shrinks and warps more than PETG. A flange that lies on the bed is a wide foot, and it holds its piece down. A flange that stands upright is a rib along a free edge of the wall. A flange at the top of the piece does nothing for the bed.

| Piece | Flange | In the print | Longest straight run (mm) | What holds it |
| --- | --- | --- | --- | --- |
| deck nose | F1 | upright | 43 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| deck nose | F2 | upright | 16 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| deck nose | foot | on the bed | 276 | The flange is the foot of the piece on the bed. Add a brim outside the wall. |
| deck side | D1 | upright | 20 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| deck side | D2 | upright | 43 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| deck side | F1 | upright | 43 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| deck side | F2 | upright | 16 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| deck side | foot | on the bed | 153 | The flange is the foot of the piece on the bed. Add a brim outside the wall. |
| apron | P1 | upright | 12 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| lower | D1 | upright | 20 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| lower | D2 | upright | 48 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| lower | L1 | at the top | 83 | None. The gusset under it prints with no support. |
| lower | P1 | upright | 12 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| lower | S1 | upright | 70 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| lower | foot | on the bed | 172 | The flange is the foot of the piece on the bed. Add a brim outside the wall. |
| middle | B1 | at the top | 84 | None. The gusset under it prints with no support. |
| middle | L1 | on the bed | 160 | The flange is the foot of the piece on the bed. Add a brim outside the wall. |
| middle | R1 | upright | 12 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| middle | S1 | upright | 21 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| upper | B1 | on the bed | 84 | The flange is the foot of the piece on the bed. Add a brim outside the wall. |
| upper | R3 | upright | 88 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| upper | W1 | upright | 20 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| brow | W1 | upright | 20 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| upper rear | R1 | upright | 12 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| upper rear | R3 | upright | 88 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| upper rear | R5 | upright | 88 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| rear lower | L1 | at the top | 160 | None. The gusset under it prints with no support. |
| rear lower | R2 | upright | 110 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| rear lower | S1 | upright | 70 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |
| rear lower | foot | on the bed | 230 | The flange is the foot of the piece on the bed. Add a brim outside the wall. |
| hood centre | H1 | at the top | 68 | None. The gusset under it prints with no support. |
| hood centre | H1 | on the bed | 68 | The flange is the foot of the piece on the bed. Add a brim outside the wall. |
| hood side | H1 | upright | 68 | The flange stands as a rib on the edge of the wall and stiffens it against warp. Its lower end is on the bed or on the foot. |

Each piece that prints upright stands on the thin section of its wall where it has no flange on the bed. These pieces need a brim: the apron, the brow, the hood sides and the upper rear pieces.

The pieces whose longest flat edge on the bed is more than 200 mm:

- deck nose: 276 mm (the foot flange on the bed).
- rear lower: 230 mm (the foot flange on the bed).
- floor front centre: 212 mm (a flat tile).
- floor middle side: 203 mm (a flat tile).
- floor middle centre: 212 mm (a flat tile).
- floor rear centre: 212 mm (a flat tile).

### What the coupon must prove for ABS

- The clearance of the key in the groove (`Joint.groove_clearance`, 0.2 on each side), with the shrink of ABS.
- The pilot hole of the 3.0 screw: 2.25 or 2.4 (`Joint.pilot_d_pet`, `Joint.pilot_d_abs`). The pieces are modelled with 2.25. The change is one line in `pieces.joint`.
- The pilot hole of the 3.5 floor screw (`Floor.pilot_hole`, 2.6) and the thread in a foot flange of 5 mm.
- The hole of the heat-set insert: 5.6, 5.7 or 5.8 in diameter, 9.5 deep, in a boss of 13 (`OtherJoints.insert_hole_trials`, `insert_hole_depth`, `service_boss`). The research on inserts gave these values. No part of this package has an insert.
- The strength of a solvent weld on the flange face: a coupon pair that is welded, then pulled apart across the seam and peeled.
- That the solvent runs along a gap of 0.1 over the full width of 16.
- The V with the filler over a welded seam: no line shows after the paint.
- The warp of a flange of 240 mm that prints on the bed, with a brim.

## The checks of the whole set

- Pieces: 32. Each piece is one valid solid: yes. The check reads each piece from its BREP file.
- Printer limit 240 x 240 x 245: each piece fits: yes. The largest piece is rear lower R, 232 x 231 x 118.
- Clashes between pieces (a common volume of more than 1 mm3): 0.
- Clashes with the hardware and the keep-out zones of `fit.Layout`: 0.
- Screws of joint 1 (3.0 x 16): 41. Screws that a screwdriver does not reach: 0. Screws with less than 80 of room, which need a bit in a flat ratchet: 8.
- Floor screws (3.5 x 9.5, countersunk): 50 (30 in the laps, 20 into the foot flanges). Cones: 22.
- Mass of the pieces without the floor, solid, at 1.27 g/cm3: 5941 g. The plain skin is 4785 g (the report of the split: 4.79 kg). The joints, the feet and the ribs add 1156 g, 24 % of the skin. `structure.total_mass` allows 25 %.
- The foot flanges are 188 g of that and the ribs 39 g.
- Mass of the nine floor tiles as solid parts: 2928 g. As the sandwich of `structure.py` (two skins of 1.2 and a core of 40 %) the floor is about 1593 g.
- A right piece and its left twin that differ in volume: deck side, lower, middle, upper, upper rear, rear lower, hood side. The cause is the hardware on one side (the USB sockets, the power supply, the ribs behind it), a seam on the centre line (one twin has the key, the other the groove), or the hood centre, which has its key at one end and its groove at the other.

## The sheets

`cad/out/pieces/sheets/` has four sheets. Every BREP edge is drawn on the renders.

- `exploded.png`: the assembly moved apart, from the front and from the rear.
- `pilot.png`: the two pilot pairs, closed and open.
- `section.png`: the section through a screw of each pilot seam.
- `closeups.png`: seam L1 under the lowest cut-in, the land beside the door, the hand-hold, the node of S1, the floor from above and from below, the apron, and the two sides of seam H1.

## The tests

`cad/tests/test_pieces.py` has two parts.

- **The generator.** Three small shells, made with the real cut of the split and the real generator: a box with a level seam, a shell whose upper part leaves the seam at 45 degrees, and a box with a second seam in its lower half. These tests take about 25 seconds.
- **The whole set.** The test makes every piece from the skin in the cache and does the checks of this document. This takes about 33 minutes. `CANDYBAR_PIECES_SKIP_SET=1` leaves this part out.

## Known faults

- **A closed void in the upper pieces at B1.** The section sheet shows a void of about 6 x 2 mm inside upper R, between the flange and the stepped skin, near the pilot hole. The flange starts 8 mm outside the outer line there, and the fuse with the stepped skin leaves this pocket. The piece is one valid solid. Other crease sides can have the same.
- **A long stray edge in some plain pieces.** The exploded sheet shows thin lines across the cabinet. The plain pieces of the split already have them: the box of the plain upper pieces, upper rear pieces and hood sides is as wide as the cabinet, and their mesh is not. The edges were not found one by one. This package did not remove them.
- **The mesh of a shape in memory can have a triangle at the origin** (hood side). The build writes each STL file from the shape as its BREP file holds it, which does not have this fault.

## The second pass on the joints: the seams

Date: 2026-11-15. The owner asked that every seam of the 32 pieces closes and stays closed, during the solvent weld and in use. The values below are for one side of the cabinet (the left is the mirror). They come from `cad/out/pieces/seams.json` of the present build.

**The values used.** A solvent weld of ABS holds 5 MPa on its mating area (ESTIMATED and low on purpose: lap tests of welded ABS give 10 to 20 MPa; the weld pairs of plate 5 of the coupons measure it). The largest loads in use (ESTIMATED): a person leans on the deck nose with 500 N; a push of 300 N on the side of the hood; the cabinet is lifted by the rear hand-holds, 25 kg with a shock of 2 g, so 250 N at each hand-hold. No seam carries more than the whole of one of these loads.

| Seam | Pieces | Mating area, cm2 | Weld holds, kN | Screws | Key | What closes it during the weld | In use |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | deck nose, deck side | 5.9 | 3.0 | 0 | yes | A bar clamp across the deck, with pads on the two outer side faces at the height of the deck (z 30 to 40): it pushes both deck sides onto the nose and closes F1 and F2 on both sides at once. The key of F1 sets the place across the wall. | The weld: 3.0 + 3.8 kN against 250 N of the lean at each end of the nose (factor 27) |
| F2 | deck nose, deck side | 7.5 | 3.8 | 0 | no | The same clamp as F1 (the same plane, the same two pieces) | As F1 |
| D1 | deck side, lower | 0.5 and 2.2 | 0.2 and 1.1 | 0 | no | The two screws of D2, between the same two pieces, on the same plane (y 207) | Not needed: D2 (7.1 kN, 2 screws) carries the joint |
| D2 | deck side, lower | 14.2 | 7.1 | 2 | yes | Its screws | The weld and the screws |
| P1 | apron, lower | 21.6 | 10.8 | 2 | yes | Its screws | The weld and the screws |
| S1, lower to middle | lower, middle | 3.2 | 1.6 | 0 | no | The screw of L1 between the same middle piece and the lower piece, and the screws of S1 below | Not needed alone: L1 and S1 join the same pieces (10.3 and 8.1 kN) |
| S1, lower to rear lower | lower, rear lower | 5.4, 1.9, 10.8 | 2.7, 0.9, 5.4 | 2 | yes | Its screws | The weld and the screws |
| L1 | lower or rear lower, middle | 20.7 and 23.9 | 10.3 and 11.9 | 1 and 2 | yes | Its screws, and the weight of the middle piece on a level seam; tape over the outside at the front | The weld and the screws |
| B1 | middle, upper | 34.1 | 17.1 | 1 | yes | One screw at the rear; the upper piece lies on the middle piece (a level seam) and the key holds it across. Tape over the outside along the 264 mm of the run | The weld (17.1 kN) |
| W1 | brow, upper | 8.9 | 4.5 | 1 | no | Its screw | The weld and the screw |
| R2 | rear lower R, rear lower L | 6.3 | 3.1 | 1 | yes | Its screw, and the feet of both halves screwed to the floor | The weld and the screw |
| R3 | upper, upper rear | 21.8 | 10.9 | 1 | yes | Its screw; tape at the far end | The weld and the screw |
| R5 | upper rear R, upper rear L | 23.2 | 11.6 | 2 | yes | Its screws | The weld and the screws |
| H1 | hood side, hood centre | 52.1 | 26.1 | 5 | yes | Its screws | The weld and the screws |
| R1 | middle, upper rear | 0 | 0 | 0 | no | A stub of flange only: the frame of the door opening joins these two pieces (the rear package) | The frame of the door opening |

**F1 and F2: why no screw.** Every station has 0 to 8 mm behind the head for the screwdriver: the deck border is 72 high and turns at the flank break, so the shaft hits the wall of the nose or of the deck side at once. A screw from the outside would leave a head on a face that shows. A screw through the inner wall from the pocket finds only 4 of wall, and a boss for it stands in the pocket of the control panel, which another agent is changing. The weld alone carries a factor of 27 over the largest load. What the seam needs is a hand that holds it closed while the weld sets: the bar clamp across the deck does this for all four faces at once.

**What would add a fastener, if the owner wants one.** A foot screw of the nose near each end: the station at x 99.7 is left out today because it is 12 or less from the edge of its tile. Moving the tile seam or the rule of 12 there puts a screw 37 from F1 into the floor, and the floor then holds the bottom of the corner. This changes the floor tiles, so it is not done here.

## The closing gap

Date: 2026-11-15. A piece that closes a ring goes in last, into two seams at once (`docs/blueprint/index.md`, "Where each ring closes"). If the ring shrinks or grows by 1 %, the room for that piece changes by up to 2 mm, so it must not have to fit to the 0.2 of a groove. `pieces.CLOSING` names the three closing pieces:

| Ring | Closing piece | Its seams | What the gap does |
| --- | --- | --- | --- |
| The top ring | brow | W1 R, W1 L (upright, x +-106) | The two seam faces of the brow, with the faces of its flanges, stand 0.5 back from the seam plane (0.55 from the plane in all). W1 has no key. |
| The B1 ring | upper rear R | R5 (x 0), R3 R (x 211.4), both upright | The two seam faces stand 0.5 back. The grooves of both seams are in this piece and have 0.5 at each side. The keys stay on upper rear L and upper R. |
| The L1 ring | middle R | L1 R, front and rear (level) | The piece lies on level seams, so its faces do not move: only its two grooves have 0.5 at each side. |

The upper rear R is the closing half, not the left one, because then both keys of its seams stand on the other pieces. The faces that move are seam faces: the outer edge of each of these seams has the V of 1.0 that the owner fills, and the gap of 0.5 lies inside it. A thin solvent does not fill 0.5: these seams take a bond that fills a gap (dissolved ABS or a thick cement; `docs/design/print-plan-abs.md`, pair E of the coupons). The build removes 208 mm3 from the brow and 621 mm3 from upper rear R (`seams.json`, "closing"). `test_pieces` holds that no material of a closing piece is nearer to its seam plane than the gap.

## The top ring and the foot of the hood (joint 7)

Date: 2026-11-15. The hood had nothing to lie on but the body top, a land of 4 to 8, with the seam gap of the form (1.5) between the two. `pieces.top_ring` now makes joint 7 of the blueprint with the flange code of joint 1, on a level seam "G" at the body top:

- **The top ring** on the five pieces of the body top (brow, upper R and L, upper rear R and L): 14 wide inward of the outer line (`ring_w`), 6 thick (`ring_t`, new: the flange of joint 1), with the gusset of 45 degrees below it, so that it prints with no support. Inside the wall it rises 1.4 to the foot of the hood. The outer 4 of the seam gap, the part that shows, stays open (a test holds this).
- **The foot of the hood** on the three hood pieces: 14 wide, 6 thick (`hood_foot_t`), with its gusset. It lies on the ring with a bond line of 0.1.
- **Four cones** of 8 x 3 on the ring, at x +-150 at the front and at the rear, each in a socket of the foot (`OtherJoints.cone_clearance` 0.15). They put the hood in its place, bolted or bonded.
- The ring and the foot end at the cut faces of the other seams of their module (W1, R3, R5 on the body; H1 on the hood), as the flanges of joint 1 do. The closing gap of the brow and of upper rear R holds for the ring too.

| Piece | Ring or foot, cm3 |
| --- | --- |
| brow | 57.5 |
| upper R, upper L | 68.7 each |
| upper rear R, upper rear L | 56.7 each |
| hood centre | 103.5 (front and rear) |
| hood side R, hood side L | 85.9 each |

**What it costs.** The joints, feet and ribs of the set are now 1437 g at 1.05 g/cm3, 37 % of the plain skin (961 g, 24 %, before). The ring at 12 thick, the value of the blueprint (`ring_h`), was 420 cm3 in a trial build against 308 cm3 now: about 120 g more. `ring_h` stays the depth at an insert. `structure.EXTRAS_SHARE` is now 0.40 of the skin (it was 0.25), so the total mass and the centre of mass of the structure study carry the real joints.

**The checks.** Each piece stays one valid solid inside the limit. No clash between pieces, with the hardware, or with the parts of the rear. The ring and the foot alone have no common volume with any part of the cradle (`cad/out/cradle`) or with any part of hood band A (`cad/out/hood-band/A`).

**Not done.** The M4 inserts and screws of a bolted hood (the blueprint: two pins at the front, two M4 at the rear, inserts in the ring, `ring_h` 12 deep there). Their heads would be inside the hood, on its foot, and no way for the screwdriver to reach them is chosen: from inside the hood through the marquee opening, or from below with the inserts in the foot. The owner has not chosen between a bolted and a bonded hood. The cones and the faces serve both.

**The sheet.** `cad/out/pieces/joints-2/joints-2.png` (`candybar.shell.joint_sheets`, `tools/draw_joint_sheets.py`): the closing gap at W1, R5 and R3, the ring and the foot along the right side, and sections at the front and the rear cone. Every face edge is drawn.

## The edge finish and the face check

Date: 2026-11-15. `tools/edge_finish.py` and `tools/face_check.py` run on `cad/out/pieces`:

```sh
CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh tools.edge_finish     # about 50 minutes
CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh tools.face_check      # about 40 minutes
```

- **The classes.** The pieces of the walls and of the hood are "printed". The floor tiles are "inside, not painted". The pieces "logo form" and "speaker form L/R" are the stand-ins of the hood band and are "provisional, not finished".
- **What shows.** A face of a piece shows only when it is on the outside of the outer form of the default build (`edge_finish.face_on_skin`: its middle is on the form, and a point 0.5 off it, along its normal, is outside the form). The faces of the cavity, the flanges, the keys, the ribs and the seams do not show. On the outside, a face does not show when a part of the default build lies on it (the control panel, the bezel plate, the screen, the stand-ins of the hood band), with the fit of the skin's pockets (0.3); when it is a face of the stand-in of the marquee lip, which the skin of the hood carries; when the next piece lies on it; or when it lies in the V of a filled seam (`joints.vgroove_profile`).
- **Edge finish: one finding on each lower piece.** At the lower rim of the bezel recess, x ±199 to ±235, z 133.7, one sharp edge of 66.5 degrees, 35.4 long, between the sill and a flat of 0.2 at the seam L1. The default build has the same rim: its tool hides it because the middle of the long rim lies under the stand-in of the bezel plate, and here the rim is cut at the seam. The stand-in plate stands 1.9 from it. To break the rim changes the outer form, so this unit did not change it. It is open (see the roadmap).
- **Face check: 3184 findings on the outside faces, not changed.** They are in the faces of the skin, not in its form: 1134 on the underside (z 0, the face on the table), 212 at the seam on the body top, 62 along the line where the deck and the body meet (y 207), and 1776 at other places. The samples of these that were read are at the levels of the slabs of the cavity (z 65, 70, 72), at the cut-ins and at the bezel recess; not all 1776 were read. 2562 are splits (one surface cut into several faces), 248 crowded vertices, 224 slivers, 116 needles and 34 kinks. They do not change the printed form or the fit. The face check of the default build has none of them, because its parts are the outer form, not the skin.

## A trial: merged faces on one piece

Date: 2026-11-16. On `lower_R`, `Shape.removeSplitter()` merges the faces that lie in one surface. It takes 0.2 s. The piece stays one valid, closed solid (226562.7 and 226562.8 mm3). Its faces go from 1263 to 1149, and the findings of the face check on the outside of the shell from 241 to 61: splits 162 to 8, slivers 30 to 15, crowded corners 21 to 14, needles 25 to 22, kinks 3 to 2. It is not applied to the other pieces: the owner decides.

## The hole of the latch's button

Since 2026-11-15 the deck nose has the hole of the button of the control panel's latch (`Blueprint.latch_button_d`): it comes from the skin, so the piece needs nothing of its own. No seam is near (F1 and F2 at x 137).

## Assumptions

1. The pilot hole of joint 1 is 2.25 (`Joint.pilot_d_pet`). The coupon decides between 2.25 and 2.4.
2. A screwdriver needs 40 mm behind a screw head (`Build.driver_len`): a 25 mm bit in a flat ratchet. With 80 mm, fewer screws fit.
3. A hole or a head pocket must leave 1.2 of the skin to the outside (`Build.wall_left`).
4. A flange stays 2 from the hardware and from the keep-out zones of `fit.Layout` (`Build.hardware_gap`). Where a flange was in such a zone, it is cut back. The keep-out zones count as hardware. This includes the room for any 16:10 monitor, the air space of the power supply's fan and the room of the marquee modules.
5. The wall flanges stop 0.3 above the floor and 10 from the opening of the rear door.
6. The floor screws are 3.5 x 9.5, countersunk, from above, with a pilot hole of 2.6. The joint sheet has the floor screws from below. The cabinet stands on thin pads, so a screw head under the floor has no room.
7. The foot flange is 5 thick, not the 4 of `Joint.foot_t`, so that the thread of a floor screw has 5 mm.
8. The floor tiles are modelled as solid parts. The slicer makes the sandwich (two skins of 1.2 and a core of 40 %).
9. The masses use 1.27 g/cm3 (PETG), as the report of the split does. ABS is about 1.04 g/cm3: multiply by 0.82.
10. The outer solids come from the BREP files of the default build. The build of the outer solids did not end on the server (see "Not done").

## Not done

- **The rear door and the frame of its opening.** Another package. The door halves are plain pieces. Seam R1 has only a stub of flange.
- **The inserts of a bolted hood** (joint 7) and the other service seams: see "The top ring and the foot of the hood".
- **The node plate** (joint 4). The flanges of the three pieces meet at each node, but no plate goes over them.
- **The cones at the ends of the wall seams** (`OtherJoints.cone_d`). The key locates a seam across the wall and square to the seam. Along the seam, the seams that cross it locate the piece. Only the floor has cones.
- **The chamfer at the ends of a groove.** The long sides of a groove have the chamfer of 0.3. The ends do not.
- **More screws on the seams with few.** F1, F2, D1 and R1 have no screw. R2, and each side of R3, of W1 and of L1 in front of the band, have one. Clamps or tape must hold these seams while the bond sets.
- **A change of the split for the middle pieces.** See "Print": one seam face of each middle piece prints on support.
- **A slicer check.** No piece was sliced.
- **A face check of the joints.** `tools/face_check.py` fails on every finished piece, because the stepped inner face of the skin has faces of 1 mm. The folder `joints/` has the added solids alone. The check finds 3626 narrow faces there, but most of them are inside the skin after the fuse (the 0.5 mm lap of each flange into the skin). The joint has narrow faces by its definition: the sides of the key (1.5), the chamfer of the groove (0.42), the counterbore (0.5) and the V. No check separates these from a fault.

## On the main line

Date: 2026-11-14. The package was merged on the laptop (OpenCascade 7.9.3) after the rear door. These things changed:

- **The rear door.** The plain pieces are the pieces of `split.cut` finished by `rear.finish_pieces`, as `split.run` makes them: the door halves are the designed halves, and the rear lower, middle and upper rear pieces have the lip, the rib under the sill, the tongues, the posts and the openings of the lower wall. The source of `rear.py` is in the key of the cache. The parts of the rear that are not pieces (the head rails, the shroud, the fan, the duct and the seals) are in the list of hardware with the role "rear". A flange that goes into one of them is cut back, and the checks of the set include them. No flange, foot or rib goes into a part of the rear. The flanges still stop 10 from the opening (`Build.door_stop`).
- **Seam L1 at the cut-ins.** No screw of L1 is in the span of the cut-ins (`pieces.in_cut_in_span`, `Build.cut_in_clear` 10). The skin steps in behind the lowest cut-in, and a head pocket of 9 would cut 1.0 into that step of 1.5. The key and the bond hold the seam there. One station on each side was left out.
- **The rib on the inlet.** The rib of rear lower R at x 156.9 crossed the inlet. Each rib of the lower rear wall that is in the field of the slots goes to the middle of the nearest bar (`pieces.on_a_bar`): it is at x 155.6 (after the inlet moved 3 outward with the ATX screw pattern of the supply, see `hardware-mounts.md`). The section of each rib is now centred on its plane, so that this rib is cut from the bar and is whole (3.3 cm3). The rib at x 78.5 is outside the field. The ribs of rear lower L are left out, as before, because the power supply stands against that wall.
- **ABS.** The pilot hole of the model is 2.4 (`Joint.pilot_d_abs`), the first candidate for ABS. The limit is 248 x 248 x 250, and the density is 1.05.
- **The kernel.** On the laptop the skin of the cache reads as a valid shape. The repair of the skin with ShapeFix and the fall-back to a shared build on the server are removed. The repair of a piece that does not read back valid from its text BREP file stays: on the laptop deck side R needs it.

The table in "The pieces" and the numbers in "The checks of the whole set" are those of the server, before the merge. `tools/draw_pieces.py` writes the present values to `cad/out/pieces/report.md`.

The checks of the set on the laptop:

- Pieces: 32. Each is one valid solid inside 248 x 248 x 250. The largest is rear lower R, 232.3 x 231.3 x 121.0.
- Clashes between pieces: 0. Clashes with the hardware, the keep-out zones and the parts of the rear: 0.
- Screws of joint 1: 37. Each one has room for the screwdriver. Floor screws: 50. Cones: 22.
- Mass at 1.05 g/cm3: the pieces without the floor are 4889 g, the plain skin 3928 g. The joints, the feet and the ribs add 961 g (24 %): flanges and gussets 1351 g, feet 155 g, ribs 33 g, less the holes and grooves. The nine tiles as solid parts are 2421 g.
- Seams with a flange and a key but no screw: D1, F1, F2 and S1. Clamps or tape hold them while the weld sets.

## The front socket plate

Date: 2026-11-15. The socket plate is not in the default build. `CANDYBAR_PIECES_SOCKET_PLATE=1` builds the pieces with it:

- Deck side R has the seat of the plate: the opening, the frame behind the skin and the edge break of the rim (`socket_plate.seat`).
- The floor tile under the frame gets a notch round it, with 0.5 of clearance, as round each part of a wall that stands in the plan of the floor.
- The foot flange of deck side R stops along the plate. Over that length the tile has its notch, so a foot flange there would hold no tile and have no screw.
- The plate and the bought parts of all four variants (the sockets with the room of their leads, the button, the knob, the screws) are obstacles of the flanges, and the floor is checked against them.

The frame and the plate keep their form. Only the inside parts change: the tile and the foot flange. `tests/test_pieces.py` (class `SocketPlateTest`) holds this.
