# The shell is ABS, printed on a Qidi Q2, and the seams can be solvent welded

The printed parts of the cabinet are ABS. They are printed on a Qidi Q2, an enclosed printer with a heated chamber. The print size of the Q2 is 270 x 270 x 256: a bed of 270 x 270 and a height of 256. The seams of the shell can be welded with a solvent cement or with ABS dissolved in acetone, in place of an adhesive.

The owner chose this on 2026-11-14. Decision record 0006 left the material open: PETG on the Bambu A1, or ABS on an enclosed printer. `docs/research/abs-on-the-q2.md` has the values and the sources, and `docs/design/print-plan-abs.md` has the print plan.

## Consequences

- The piece limit of the split is 250 x 250 x 250, with 248 for the footprint in the model, because the slicer makes a piece larger to compensate the shrink. The height of 256 is the same as on the A1, so no piece can become taller. All 32 pieces of the split pass this limit.
- The masses in the model use the density of ABS, 1.05 g/cm3 (1.12 if the owner buys PolyLite ABS).
- A weld sets in minutes and it cannot be opened again. The seams are welded one at a time, after a dry assembly with screws.
- A solvent can crack ABS where it is under stress, at a screw or an insert. The weld coupon (C3) looks for these cracks.
- Warp is the main risk of ABS. The flat pieces are the problem: the floor tiles and the two door halves. The material of the floor is open again.
- The printer must stand in a room that is not a living room, with a vent to the open air.
- The coupons prove the joint, the weld, the shrink and the paint in ABS before the pieces are printed.
