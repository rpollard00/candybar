# Candybar CAD

This directory holds the FreeCAD model of the cabinet. Python scripts generate the model. FreeCAD 1.1 runs the scripts.

There is one model: the blueprint shell (`candybar/shell/`). `docs/blueprint/index.md` describes it. `docs/design/one-model.md` says what became of the older generator.

## Status

| Item | State |
| --- | --- |
| Outer form | Revision 7 (decision record 0007): the deck, the body, the hood, the bezel plate and the control panel plate, as solids. The marquee lip, the speaker forms and the logo form are provisional. |
| Skin | The outer form less the cavity, with a wall of 4 mm |
| Monitor, BC-250, power supply, cable bundle, lever, buttons, encoder, USB sockets, hub | Envelope solids and keep-out zones in the cavity (the fit study). The dimensions come from data sheets and community CAD, not from the real parts. |
| Split | 32 pieces for the printer, with the joints as data. The pieces have no flanges, keys or ribs. |
| Monitor cradle, compute mount, ducts, power supply mount, rear door, control panel frame | Not designed. The keep-out zones hold their space. |

## Build, check, test

Requirements: FreeCAD 1.1 (`freecadcmd` and `freecad`). The drawing tools use the Python of `cad/.venv-tools`, and the renders use Blender.

```sh
cad/build.sh    # build the model (2 minutes)
cad/check.sh    # run the checks of the design on the build (about 1 hour)
cad/test.sh     # run the tests of the code (about 30 minutes)
```

`cad/build.sh` writes these files into `cad/out/shell-rev7/`. Git ignores `cad/out/`. `CANDYBAR_OUT` sets a different directory.

| File | Content |
| --- | --- |
| `<part>.brep`, `<part>.stl` | One pair for each part |
| `shell.step` | All parts |
| `shell.FCStd` | The FreeCAD document, with the colours of the parts |
| `manifest.json`, `report.json` | The list of the parts, and their volumes, face counts and the lines of the build log |
| `focus.json`, `edges.json` | The cameras and the edges for the renders |

If a part is not one valid solid, `cad/build.sh` returns a non-zero exit status. The script removes the part files of an earlier build before it starts.

The build has two steps. The first step runs `freecadcmd` and makes the parts. The second step runs the FreeCAD GUI program without a window and writes `shell.FCStd`. A document that is saved without the GUI opens with all solids hidden.

`cad/check.sh` runs these checks, one FreeCAD process at a time. It writes the text of each check to `cad/out/shell-rev7/check/`. If a check fails, the exit status is 1.

| Check | The check fails when |
| --- | --- |
| `tools.check_solids` | A solid is more than 0.5 mm from the faces of the blueprint |
| `tools.face_check` | A face of a part is not a reveal, an edge break or a known item |
| `tools.edge_finish` | A printed part has a convex edge that shows and is fully sharp |
| `candybar.shell.fit` | A hardware item breaks a rule of the fit study (see "Rules of the fit study") |
| `candybar.shell.split` | A piece of the split does not fit the printer |
| `candybar.shell.structure` | The run breaks. This step measures and has no limit of its own. |
| `candybar.shell.rear` | A rule of the rear door, its vents, the shroud or the openings fails |

`cad/test.sh <name-fragment>` runs only the tests whose name contains the fragment.

## The studies and the drawings

The commands that follow run one study or make one drawing. `docs/blueprint/index.md` (section "How to build and check the solids") has the commands for the solids and their checks. Run one FreeCAD or Blender process at a time. `candybar/freecad-run.sh` holds this rule: each run takes one lock for the machine and waits for it, and a guard stops `freecadcmd` when it uses more than 9.5 GB or the machine has less than 3 GB left. Start a direct `freecadcmd` or `blender` command through `tools/cad-lock.sh`, which takes the same lock.

The fit study, the split and the structure follow revision 7. The skin (the outer form less the cavity) takes about 20 minutes to make and needs 6 GB of memory. The split keeps it in `cad/out/shell-rev7/split/cache`, under a fingerprint of `dims.py`, `profiles.py`, `solids.py` and `cavity.py`. When one of them changes, the next run makes the skin again.

```sh
# the fit study: the hardware in the cavity (about 30 minutes); exit status 1 when an item does not fit
CANDYBAR_OUT=cad/out/shell-rev7 cad/candybar/freecad-run.sh candybar.shell.fit
# the split: cut the skin into the pieces of the layout and measure them
CANDYBAR_OUT=cad/out/shell-rev7 cad/candybar/freecad-run.sh candybar.shell.split
# the structure: move the hardware of the fit study in the skin, measure the walls of the hand-holds (split/structure.json)
CANDYBAR_OUT=cad/out/shell-rev7 cad/candybar/freecad-run.sh candybar.shell.structure
# the sheets and report.md (with "report": without the elevations, which take minutes)
cad/.venv-tools/bin/python cad/tools/draw_split.py
cad/.venv-tools/bin/python cad/tools/draw_split.py render       # renders of the pieces (Blender)
cad/.venv-tools/bin/python cad/tools/draw_blueprint.py fit      # docs/blueprint/09-hardware
cad/.venv-tools/bin/python cad/tools/draw_split.py blueprint    # docs/blueprint/10-split and 11-joints
# the detail pass: the open small questions of the form
cad/.venv-tools/bin/python cad/tools/draw_detail.py detail-options
# the joint coupon: printable parts, checks and README.md in cad/out/coupon; then its drawing and renders
CANDYBAR_OUT=cad/out/coupon cad/candybar/freecad-run.sh candybar.shell.coupon
cad/.venv-tools/bin/python cad/tools/draw_coupon.py cad/out/coupon
# the width study: the cavity probe of a wider variant (here +20) in its own directory, then the sheets
CANDYBAR_WIDEN=20 CANDYBAR_WIDEN_STEP=probe CANDYBAR_OUT=cad/out/probe/probe-w20 cad/candybar/freecad-run.sh candybar.shell.width_run
cad/.venv-tools/bin/python cad/tools/draw_widths.py options          # cad/out/shell-bp/compare/width-options.png
cad/.venv-tools/bin/python cad/tools/draw_widths.py table cad/out/probe   # the numbers as Markdown
```

### The parts of the work packages

Each package has its own module, its own output folder under `cad/out/` and a design document in `docs/design/`. None of them changes the default build of the outer form. Each needs the default build in `cad/out/shell-rev7` with its fit study, and the skin in the cache of the split.

```sh
# the print pieces with joint 1, the floor tiles and the ribs (about 20 minutes; docs/design/print-pieces.md)
CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh candybar.shell.pieces
CANDYBAR_PIECES=check CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh candybar.shell.pieces   # the checks again, on the files
CANDYBAR_PIECES=views CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh candybar.shell.pieces   # the folders for the sheets
cad/.venv-tools/bin/python cad/tools/draw_pieces.py                                                  # the sheets and report.md
CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc                 # shell.FCStd
# the mounts of the hardware: tray, docks, fence, saddle, tie points, places (2 minutes; docs/design/hardware-mounts.md)
CANDYBAR_OUT=cad/out/mounts cad/candybar/freecad-run.sh candybar.shell.mounts                        # CANDYBAR_MOUNT_SCENES=0: no scenes
cad/.venv-tools/bin/python cad/tools/draw_mounts.py cad/out/mounts                                   # the sheets
CANDYBAR_OUT=cad/out/mounts cad/candybar/freecad-run.sh --gui candybar.shell.mounts_scenes           # shell.FCStd
# the control panel: two printed tiles, the frame, the latch, a blank panel (2 minutes; docs/design/control-panel.md)
CANDYBAR_OUT=cad/out/control-panel cad/candybar/freecad-run.sh candybar.shell.panel_frame            # parts, checks, report.md
CANDYBAR_OUT=cad/out/control-panel cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc          # shell.FCStd
cad/.venv-tools/bin/python cad/tools/draw_panel.py                                                   # renders and sheets
CANDYBAR_OUT=cad/out/control-panel/parts cad/candybar/freecad-run.sh tools.edge_finish               # the edge rule on its parts
CANDYBAR_OUT=cad/out/control-panel/parts cad/candybar/freecad-run.sh tools.face_check                # the face check on its parts
# the monitor cradle and the printed bezel plate (4 minutes; docs/design/monitor-cradle-and-bezel.md)
CANDYBAR_OUT=cad/out/cradle cad/candybar/freecad-run.sh candybar.shell.cradle                        # parts, checks, report.md
CANDYBAR_OUT=cad/out/cradle cad/candybar/freecad-run.sh --gui candybar.shell.cradle_view             # shell.FCStd
cad/.venv-tools/bin/python cad/tools/draw_cradle.py                                                  # the sheets
CANDYBAR_OUT=cad/out/cradle/print cad/candybar/freecad-run.sh tools.edge_finish                      # the edge rule on its print parts
CANDYBAR_OUT=cad/out/cradle/print cad/candybar/freecad-run.sh tools.face_check                       # the face check on its print parts
# the front socket plate, four variants (about 20 minutes; not in the default build; docs/design/front-socket-plate.md)
CANDYBAR_SHELL=cad/out/shell-rev7 CANDYBAR_OUT=cad/out/socket-plate cad/candybar/freecad-run.sh candybar.shell.socket_plate
cad/.venv-tools/bin/python cad/tools/draw_socket_plate.py all                                        # shell.FCStd, renders, sheets
CANDYBAR_OUT=cad/out/socket-plate/b-knob cad/candybar/freecad-run.sh tools.edge_finish               # the edge rule on the default variant
CANDYBAR_OUT=cad/out/socket-plate/b-knob cad/candybar/freecad-run.sh tools.face_check                # the face check on it
# the hood band: bands A (the owner's choice), B and C, and the studies of a taller hood (7 minutes; not in the default build; docs/design/hood-band.md)
CANDYBAR_OUT=cad/out/hood-band cad/candybar/freecad-run.sh candybar.shell.hood_band                  # HOOD_BAND_VARIANTS=A, HOOD_BAND_TALL=
CANDYBAR_OUT=cad/out/hood-band/A cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc            # shell.FCStd of one variant
cad/.venv-tools/bin/python cad/tools/draw_hood_band.py                                               # the sheets
```

`CANDYBAR_WIDEN_STEP` is `solids`, `check`, `probe` or `fit`. `CANDYBAR_SPLIT_CACHE` sets another directory for the skin. `candybar/shell/joints.py` is the one source of the joint values; `tests/test_joints.py` fails when a second module sets one.

Large outputs go under `cad/out/`, which git ignores. Do not write them to `/tmp`: on this machine `/tmp` is memory. Scratch files go under `cad/out/_scratch/`.

## Parameters

The dimensions of the outer form are in `candybar/shell/dims.py` (class `Blueprint`). The joint values are in `candybar/shell/joints.py`.

The dimensions of the purchased parts and of the printer are in `cad/params/*.csv`. The fit study copies them into the `Params` sheet of its document. Each envelope and each keep-out zone refers to the sheet by name. The fit study calculates where each item stands (the anchors) from `Blueprint` and from `fit.Layout`, and it adds these values to the sheet as derived rows.

| File | Content |
| --- | --- |
| `printer.csv` | The bed and the largest part |
| `hardware.csv` | The monitor, the BC-250, the fan, the power supply, the USB parts, the marquee |
| `controls.csv` | The lever, the buttons, the encoder |
| `cabinet.csv` | Five layout values that the envelopes need, and the targets for the panel top and the palm rest |

| Column | Content |
| --- | --- |
| `name` | The parameter name. The model refers to this name. |
| `value` | A number, or a FreeCAD expression that starts with `=` |
| `unit` | `mm`, `deg`, or empty for a count |
| `status` | `measured`, `sourced`, `provisional`, or `derived` |
| `measure` | What to measure on the real part |
| `source` | Where the value came from |
| `note` | What the parameter means |

| Status | Meaning |
| --- | --- |
| `measured` | You measured the value on the real part. |
| `sourced` | A data sheet, a standard, or a community CAD model gives the value. |
| `provisional` | A design choice or an estimate. A test or a decision can change it. |
| `derived` | An expression calculates the value from other parameters. |

### Enter a measurement

1. Open the CSV file that holds the parameter. `cad/out/shell-rev7/fit/warnings.md` lists the parameters and their files under "Still to measure".
2. Replace the number in the `value` column.
3. Change the `status` column to `measured`.
4. Run the fit study: `CANDYBAR_OUT=cad/out/shell-rev7 cad/candybar/freecad-run.sh candybar.shell.fit`.
5. Read `cad/out/shell-rev7/fit/report.md` and `warnings.md`.

### Rules for values

- An expression uses FreeCAD syntax and other parameter names: `=bc_shroud_w - 12 mm`.
- A number in an expression needs its unit: `12 mm`, not `12`.
- A name cannot be a unit (`mm`, `d`, `h`) or look like a cell address (`A1`, `BC250`).
- `btn_count` sets how many action buttons exist: 6 or 8.

## Rules of the fit study

| Rule | The fit study fails when |
| --- | --- |
| Object state | An item does not recompute, or is not one valid solid. The study stops. |
| R1 interference | Two solids of different owners share more than 1 mm3. An owner is one purchased part. Two button nuts are compared by R5 only. |
| R2 keep-out | A solid of one owner is in a keep-out zone of a different owner |
| R2b air zones | An air zone shares room with a solid or a zone of a different item |
| R5 button spacing | Two button nuts overlap by more than 1 mm. A smaller overlap gives a warning. |
| Containment in the cavity | A hardware solid or a keep-out zone is in the skin, in a plate, or outside the form |
| Door service | The compute module and its exhaust duct are not inside the door opening, or the rear face of the power supply is not on the flat of the lower rear wall |

`fit/warnings.md` has the items that do not fail the study: the height of the panel top and the palm rest against their targets, the count of the parameters by status, and the list of what is still to measure.

## View the model

Open `cad/out/shell-rev7/shell.FCStd` in FreeCAD. It holds the parts of the outer form. The hardware is not in this document: sheet 09 of the blueprint and the cutaway meshes in `cad/out/shell-rev7/fit/cutaway/` show it.

### Live session for Claude

The FreeCAD MCP addon (`neka-nat/freecad-mcp` 0.1.30) is installed in `~/.local/share/FreeCAD/v1-1/Mod/FreeCADMCP`. The MCP server is registered in Claude Code as `freecad`.

```sh
cad/tools/freecad-gui.sh             # start FreeCAD with the RPC server
cad/tools/fcrpc.py show              # open shell.FCStd in the running FreeCAD
cad/tools/fcrpc.py shot view.png --view Right
```

CAUTION: The RPC server runs all Python code that a local program sends to port 9875. Start FreeCAD with `cad/tools/freecad-gui.sh` only when you want that access. FreeCAD started from the desktop does not start the server.

## Frames and roles

The global frame has its origin on the desk, at the cabinet front face, on the center line. X points to the right of the player. Y points from the front face to the rear. Z points up.

Each hardware assembly of the fit study is an `App::Part` with its own local frame. The module that defines the assembly describes the frame.

Each solid of the fit study has a `CB_Role` property. The rules use this property.

| Role | Meaning |
| --- | --- |
| `hardware` | A purchased part |
| `protrusion` | Hardware that goes through the control panel: the lever shaft, the ball, the button caps |
| `keepout` | Space for a plug, a cable, airflow, or a part that is not designed |

## Code

| Path | Content |
| --- | --- |
| `build.sh`, `check.sh`, `test.sh` | Build the model, run the checks of the design, run the tests of the code |
| `candybar/freecad-run.sh`, `launch.FCMacro` | Run one module in FreeCAD and return its exit status |
| `candybar/shell/dims.py`, `profiles.py`, `solids.py` | The dimensions, the profiles and the solids of the outer form |
| `candybar/shell/cavity.py` | The cavity and the skin |
| `candybar/shell/viewdoc.py` | Writes `shell.FCStd` |
| `params/` | The parameter sheets of the purchased parts |
| `candybar/shell/params.py` | Loads and validates the sheets. Writes the `Params` sheet. |
| `candybar/shell/model.py` | The FreeCAD mechanics of the hardware items: bound placements, solids, roles |
| `candybar/shell/hardware.py`, `controls.py` | The envelopes and the keep-out zones, written as tables |
| `candybar/shell/check.py` | Rules R1, R2 and R5, and the warnings |
| `candybar/shell/fit.py` | The fit study: the anchors, the items, the rules that need the cavity, the report |
| `candybar/shell/split.py`, `structure.py`, `joints.py`, `coupon.py` | The split, the structure, the joint values, the joint coupon |
| `candybar/shell/widths.py`, `width_run.py` | The width study |
| `tests/` | The tests |
| `tools/` | The checks of the solids, the drawings, the renders, the photo tools, the FreeCAD launcher, the RPC client, the vendor fetch script |

## Reference CAD

`cad/tools/fetch_vendor.sh` fetches three third-party repositories into `cad/vendor/`. It also examines three files from Printables, which you must download by hand. The script gives a non-zero exit status until these files are there. Git ignores `cad/vendor/`. The licenses of these files do not permit redistribution, so do not copy their geometry into tracked files. The build does not use them.

The research notes are in `docs/research/`.
