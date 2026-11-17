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

Requirements: FreeCAD 1.1 (`freecadcmd` and `freecad`). The drawing tools use the Python of `cad/.venv-tools`, and the renders use Blender. `cad/container/` has a container with FreeCAD and OpenCascade of the versions of the reference machine; its geometry is near, but not the same (`cad/container/README.md`).

```sh
cad/build.sh    # build the model (3 minutes)
cad/check.sh    # run the checks of the design on the build (about 1 hour)
cad/compare.sh  # compare the build with the accepted outer form, the commit in cad/BASELINE (0.000001)
cad/test.sh     # the quick tests of the code (about 1 minute)
cad/test.sh --slow   # the slow tests: they read the builds and the skin (61 minutes on the server; WholeSetTest is 37 of them)
```

### What runs when

A unit of work runs these, and nothing else:

1. Its builds: `cad/build.sh` and the build of each package that it changed. Each build fails on its own checks.
2. `cad/compare.sh`, when the unit can change the outer form. A part that has the same counts, volume, area and box as the baseline is the same; only a part that differs gets the full measure of the distance.
3. `cad/test.sh`, when the unit changed code that the quick tests cover. A test file has the name of its module: `test_<module>.py` tests `candybar/shell/<module>.py` or `tools/<module>.py`. Three files are different: `test_blueprint_solids.py` tests `solids.py` and `profiles.py`, `test_outputs.py` tests the export and `viewdoc.py`, and `test_build_entry.py` tests the scripts.

Before a push, run `cad/test.sh --slow`. It needs the builds of the unit in `cad/out/shell-rev7` and the skin in the cache of the split.

Do not write a test that asserts on a real output what the build of that output already checks and fails on. Put the check in the build.

The quick group (272 tests) tests logic and small shapes. It builds no shell and reads no cache, and it runs in one process in 101 s on the server (Zen 2, 2.4 GHz). The slow group (32 tests, marked with `tests.support.slow`) protects what no build checks yet:

| Tests | What they protect |
| --- | --- |
| `test_blueprint_solids.PlanarRearTest` (5) | The flat faces of decision record 0007, which a check at 0.5 mm cannot tell from a slight curve; the hand-holds print without support; the head and the hood line up across the seam |
| `test_blueprint_solids.BlueprintSolidsTest` (1) | The check of the solids against the blueprint can still fail |
| `test_edge_finish.ShellEdgeFinishTest` (3) | The edge break of the hood is the same on both sides, takes no more than its depth, and the cavity is taken from the hood before the break |
| `test_pieces.WholeSetTest` (14) | The rules of the joints on the whole set, and the 30 pieces. `pieces.check_set` does not check them yet. When it does, these tests go |
| `test_split.SplitTest` (1) | Each hand-hold stays whole in one piece |
| `test_panel_frame.ChecksTest` (5) | The checks can still fail on the real skin of the deck; the panel comes out with the button held and not with a hook under the ledge; the options still build |
| `test_rear` (2) | The door tilts out and lifts off; the rear changes no piece that it does not finish |
| `test_socket_plate.SeatTest` (1) | The cut of the seat changes the deck at the seat only |
| `test_hood_band.VariantsTest` (1) | The variants B and C still build and keep the outside of the hood |

The rules of the joints in `WholeSetTest` that go into `pieces.check_set`: the joints add no clash with the hardware; a right piece and its left twin differ only where the hardware differs; every bonded seam has a flange on both pieces or is a known exception; every seam longer than a screw run has screws; no key stands on a face that lies on the printer bed; the floor has nine tiles and each is screwed; each closing piece has the closing gap; joint 7 rings the body top; the hood is bolted with four screws that a key reaches; seam L1 has no screw in the span of the cut-ins; no flange is in a part of the rear; the flanges stop short of the door opening; and the split has 30 pieces.

`tests.support.shell()` and `tests.support.cavity()` keep the default shell and its cavity on disk in `cad/out/test-cache`, under a key of the values of `Blueprint()`, the source of the modules that build them, and the versions of FreeCAD and OpenCascade. `CANDYBAR_TEST_CACHE=off` makes them in the process. After the results, `cad/test.sh` prints the twenty slowest tests, each with the time of the set-up of its class.

The default build is the cabinet as the owner chose it: the hood band A (`candybar/shell/band.py`) and the front socket plate `b-knob` (`candybar/shell/socket_plate.py`) are in it since 2026-11-16. `cad/compare.sh` builds the outer form of the baseline commit once into `cad/out/baseline/<commit>` and writes `compare-<commit>/compare.md` beside the build; it fails when a part moved or has no partner. A decided change of the form gets a new baseline: the commit that makes it goes into `cad/BASELINE`.

The whole cabinet, with the printed bezel plate, the monitor and the control panel in, for the owner:

```sh
CANDYBAR_OUT=cad/out/cabinet cad/candybar/freecad-run.sh candybar.shell.cabinet          # after the builds of the shell, the cradle and the panel
CANDYBAR_OUT=cad/out/cabinet cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc    # cad/out/cabinet/shell.FCStd
cad/.venv-tools/bin/python cad/tools/draw_cabinet.py cad/out/cabinet                     # cad/out/cabinet/cabinet.png
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

`cad/test.sh [--slow | --all] <name-fragment>` runs only the tests whose name contains the fragment.

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
# the coupon set for ABS on the Qidi Q2: 44 parts on ten plates, the owner's next print (1 minute; docs/design/coupons.md)
CANDYBAR_OUT=cad/out/coupons cad/candybar/freecad-run.sh candybar.shell.coupons                      # stl/, brep/, coupons.json
CANDYBAR_OUT=cad/out/coupons cad/candybar/freecad-run.sh --gui candybar.shell.coupons_doc            # shell.FCStd, the plates
cad/.venv-tools/bin/python cad/tools/draw_coupon.py cad/out/coupons --set                            # coupons.png, plates.png
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
CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh candybar.shell.joint_sheets               # the sheet of the second pass on the joints: scenes
cad/.venv-tools/bin/python cad/tools/draw_joint_sheets.py cad/out/pieces                              # renders, joints-2/joints-2.png, joints-2/hood-screws.png
CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc                 # shell.FCStd
# the mounts of the hardware: tray, docks, fence, saddle, tie points, places (2 minutes; docs/design/hardware-mounts.md)
CANDYBAR_OUT=cad/out/mounts cad/candybar/freecad-run.sh candybar.shell.mounts                        # CANDYBAR_MOUNT_SCENES=0: no scenes
cad/.venv-tools/bin/python cad/tools/draw_mounts.py cad/out/mounts                                   # the sheets
CANDYBAR_OUT=cad/out/mounts cad/candybar/freecad-run.sh --gui candybar.shell.mounts_scenes           # shell.FCStd
# the control panel: two printed tiles, the frame, the push bolt (the latch), a blank panel (4 minutes; docs/design/control-panel.md)
CANDYBAR_OUT=cad/out/control-panel cad/candybar/freecad-run.sh candybar.shell.panel_frame            # parts, checks, report.md
CANDYBAR_OUT=cad/out/control-panel cad/candybar/freecad-run.sh --gui candybar.shell.viewdoc          # shell.FCStd
cad/.venv-tools/bin/python cad/tools/draw_panel.py                                                   # renders and sheets
CANDYBAR_OUT=cad/out/control-panel/parts cad/candybar/freecad-run.sh tools.edge_finish               # the edge rule on its parts
CANDYBAR_OUT=cad/out/control-panel/parts cad/candybar/freecad-run.sh tools.face_check                # the face check on its parts
# the latch study of the control panel: M, H and Q as the record, B from panel_frame (docs/design/control-panel-latch.md)
CANDYBAR_OUT=cad/out/panel-latch cad/candybar/freecad-run.sh candybar.shell.panel_latch              # the candidates, report.md
cad/.venv-tools/bin/python cad/tools/draw_panel_latch.py                                             # the sheets of the study
# the monitor cradle and the printed bezel plate (4 minutes; docs/design/monitor-cradle-and-bezel.md)
CANDYBAR_OUT=cad/out/cradle cad/candybar/freecad-run.sh candybar.shell.cradle                        # parts, checks, report.md
CANDYBAR_OUT=cad/out/cradle cad/candybar/freecad-run.sh --gui candybar.shell.cradle_view             # shell.FCStd
cad/.venv-tools/bin/python cad/tools/draw_cradle.py                                                  # the sheets
CANDYBAR_OUT=cad/out/push-rod-mark cad/candybar/freecad-run.sh candybar.shell.rod_mark               # the sheet of the push rod's mark: scenes
cad/.venv-tools/bin/python cad/tools/draw_push_rod.py cad/out/push-rod-mark                          # renders and push-rod-mark.png
CANDYBAR_OUT=cad/out/duct-lead cad/candybar/freecad-run.sh candybar.shell.duct_lead                  # the sheets of the adapter and the duct: scenes
cad/.venv-tools/bin/python cad/tools/draw_duct_lead.py cad/out/duct-lead                              # renders and 1-way-1.png, 2-way-2.png, 3-places.png
CANDYBAR_OUT=cad/out/cradle/print cad/candybar/freecad-run.sh tools.edge_finish                      # the edge rule on its print parts
CANDYBAR_OUT=cad/out/cradle/print cad/candybar/freecad-run.sh tools.face_check                       # the face check on its print parts
# the front socket plate, four variants (about 20 minutes; b-knob is in the default build; docs/design/front-socket-plate.md)
CANDYBAR_SHELL=cad/out/shell-rev7 CANDYBAR_OUT=cad/out/socket-plate cad/candybar/freecad-run.sh candybar.shell.socket_plate
cad/.venv-tools/bin/python cad/tools/draw_socket_plate.py all                                        # shell.FCStd, renders, sheets
CANDYBAR_OUT=cad/out/socket-plate/b-knob cad/candybar/freecad-run.sh tools.edge_finish               # the edge rule on the default variant
CANDYBAR_OUT=cad/out/socket-plate/b-knob cad/candybar/freecad-run.sh tools.face_check                # the face check on it
# the hood band: bands A (the owner's choice, in the default build), B and C, and the studies of a taller hood (7 minutes; docs/design/hood-band.md)
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
