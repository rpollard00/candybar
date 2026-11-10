# Generate the model from parameter sheets

The FreeCAD document is a build output. Scripts generate it from the CSV parameter sheets in `cad/params`, and a rebuild overwrites it, so it is not tracked in git. We chose this over drawing the model by hand in FreeCAD because the layout must be checked again each time a dimension changes, and most dimensions will change when the real parts are measured. A person who edits the document in FreeCAD loses that edit on the next build: a lasting change goes into a parameter sheet or a script.

## Considered options

- Draw the model by hand in FreeCAD and track the document. Rejected: no repeatable source, no automatic checks, and a binary file that changes on each save.
- Calculate all geometry in Python with fixed numbers. Rejected for the layout: the document would not follow an edit of its own parameter sheet.
