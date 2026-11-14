# The rear is planar: flat facets on mitres, and a small round on the edges

The rear of the cabinet is made of flat faces, as on the reference cabinet. This is revision 7 of the outer form. It replaces the rear of revision 6.

The rear goes straight across. The head (the body above the rear shelf) has the full width back to the rear, and the hood has the outline of the head. Under the head is the rear shelf: two flat facets of 45 degrees, 12 mm deep on each side and 40 mm deep on the rear. They meet on the hip, at a sharp rear corner. The inner crease of the rear shelf is level at z 293.

On the rear edge of each side is the band, a facet of 45 degrees and 12 mm. Its outer edge in the side view is the stroke. The stroke is four straight lines: an upright stub of 20 mm, a kick of 28 degrees to the knee near z 85, the lean of 28 degrees, and a level run. The level run is the side facet of the rear shelf.

The edges obey one rule. The form is not rounded off, but no outside edge stays fully sharp, because paint goes thin on a sharp edge:

- A convex edge of the rear design that turns 40 degrees or more has a round of 3 mm.
- Each other convex edge that turns more than 45 degrees gets an edge break of 1 mm as the last modelling step.
- Concave creases and blunt mitres stay sharp.

The lower rear corner is upright. In plan it is the ellipse that the round of the hip makes, so the corner and the hip meet on one curve. The rear also has four cut-ins at each lower rear corner, two hand-holds in the rear wall of the head, and a base facet of 5 mm.

The owner chose this form on 2026-11-13, after a study of ten candidates. Revision 6 had a round of 18 mm on the vertical rear corners, and the step ran out in that round below the hood seam. That junction made a fan of faces less than 2 mm wide. Candidates with larger rounds (a roll under the head, a shelf with round corners) moved the fault to other corners. Two rounds of different depth cannot go round one corner as one section. Flat facets that meet on mitres remove the cause.

## Consequences

The side view shows the stroke as straight lines. The values of the form are in `dims.Blueprint`, and the default build makes this form.

The crease of the rear shelf limits the height of the rear door. The cut-ins take 20 mm of the lower rear wall at each side, which limits the width of the door. The hand-holds are part of the shell. The fit study, the split and the structure of revision 6 do not apply to this form without changes. They were changed for this form on 2026-11-13 (`docs/roadmap.md`, step 9).

A sharp edge in a drawing of the rear is an edge with the edge break. Where three small rounds meet at one corner, the model has faces less than 2 mm wide. The face check has one list of these places.
