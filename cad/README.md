# Candybar CAD

This directory holds the FreeCAD model of the cabinet. Parameter sheets and Python scripts generate the model. FreeCAD 1.1 runs the scripts.

## Status

The model is a layout study, not a set of finished parts.

| Item | State |
| --- | --- |
| Monitor, BC-250, power supply, cable bundle, lever, buttons, encoder | Envelope solids and keep-out zones. The dimensions come from data sheets and community CAD, not from the real parts. |
| Control deck | Two printable tiles: a lever tile and a button tile. The splice between the tiles and the panel latch are not designed. |
| Cabinet shell | Styled massing: one solid that follows the reference cabinet in `docs/research/cabinet-references.md` section 1. It has the hood, the cheeks, the deck, the panel opening, the rear cut-outs and the side vent. It is not divided into printable parts. |
| Bezel | Four plates for one opening: 16:9, 16:10, 4:3 and vertical. The document shows the 16:9 plate. The other three plates are hidden alternates. |
| Hood face | Flush plates for the marquee, two speaker grilles and a light strip. No hardware is chosen for them. |
| Monitor cradle, compute tray, ducts, power supply mount | Not designed. The keep-out zones hold their space. |

## Build

Requirements: FreeCAD 1.1 (`freecadcmd` and `freecad`) and `rsvg-convert`.

```sh
cad/build.sh    # build, check, export, render
cad/test.sh     # run the tests
```

`cad/build.sh` writes these files into `cad/out/`. Git ignores this directory.

| File | Content |
| --- | --- |
| `candybar.FCStd` | The native FreeCAD document |
| `report.md`, `report.json` | The check results, the overall dimensions, and the list of measurements that are not done |
| `views/front.png`, `right.png`, `top.png`, `iso.png` | Line drawings of the layout |
| `step/`, `stl/` | One file for each printable part |
| `candybar.step` | The full layout without the keep-out zones |

If a check fails, `cad/build.sh` returns a non-zero exit status.

The build has two steps. The first step runs `freecadcmd`: it generates the document, does the checks, and writes the exports and the drawings. The second step runs the FreeCAD GUI program without a window and stores the view settings in the document. Without the second step, FreeCAD opens the document with all solids hidden.

## The blueprint shell: split, structure, joints, coupon and width

The blueprint shell (`candybar/shell/`) is a second model beside the older generator. `docs/blueprint/index.md` describes it, and its section "How to build and check the solids" gives the commands for the solids, their checks and the fit study. The default build is revision 7 of the outer form (decision record 0007), and it writes to `cad/out/shell-rev7`. These commands make the split, the structure, the joint coupon and the width study. Run one FreeCAD or Blender process at a time.

The fit study, the split and the structure are those of revision 6. They run on revision 7, but their layout, their seams and their door are not yet changed for it (see `docs/roadmap.md`).

CAUTION: Do not start the split or the structure on revision 7 without the skin files in `cad/out/shell-rev7/split/cache`. The step "making the skin" of `split.py` used 12.8 GB of memory for revision 7 and did not end. The skin files in that cache come from a scratch run that cut the cavity away in steps (`docs/roadmap.md`, step 9). They apply only while `dims.py`, `profiles.py`, `solids.py` and `cavity.py` do not change.

```sh
# the split: cut the skin into pieces for each seam option and measure them (the skin is cached: about 12 minutes when it changes)
CANDYBAR_OUT=cad/out/shell-rev7 CANDYBAR_SPLIT_CACHE=cad/out/shell-rev7/split/cache cad/candybar/freecad-run.sh candybar.shell.split
# the structure: place the frame of option C in the skin, against the hardware of the fit study (split/structure.json)
CANDYBAR_OUT=cad/out/shell-rev7 CANDYBAR_SPLIT_CACHE=cad/out/shell-rev7/split/cache cad/candybar/freecad-run.sh candybar.shell.structure
# the sheets and proposal.md (without "proposal": also the elevations of each option, which take minutes)
cad/.venv-tools/bin/python cad/tools/draw_split.py proposal
cad/.venv-tools/bin/python cad/tools/draw_split.py render       # renders of the chosen layout (Blender)
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

`CANDYBAR_WIDEN_STEP` is `solids`, `check`, `probe` or `fit`. `CANDYBAR_SPLIT_OPTIONS` (for example `A,bezel`) limits a split run to some options. `candybar/shell/joints.py` is the one source of the joint values; `tests/test_joints.py` fails when a second module sets one.

Large outputs go under `cad/out/`, which git ignores. Do not write them to `/tmp`: on this machine `/tmp` is memory. Scratch files go under `cad/out/_scratch/`.

## Parameters

All dimensions are in `cad/params/*.csv`. The build copies them into the `Params` sheet of the document. Each solid, sketch dimension and position refers to the sheet by name.

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

1. Open the CSV file that holds the parameter. `cad/out/report.md` lists the parameters and their files under "Still to measure".
2. Replace the number in the `value` column.
3. Change the `status` column to `measured`.
4. Run `cad/build.sh`.
5. Read `cad/out/report.md`.

### Rules for values

- An expression uses FreeCAD syntax and other parameter names: `=cp_depth + shelf_depth`.
- A number in an expression needs its unit: `=stick_x + 36 mm`.
- A name cannot be a unit (`mm`, `d`, `h`) or look like a cell address (`A1`, `BC250`).
- `btn_count` sets how many buttons exist. A change of this value needs a rebuild.

### Try a value in FreeCAD

You can change a cell in the `Params` sheet of `candybar.FCStd`. The model follows the change after a recompute. Type a negative value as an expression: `=-75 mm`. A rebuild overwrites the document, so put a value that you want to keep into the CSV file.

## Checks

| Rule | The build fails when |
| --- | --- |
| R0 object state | An object does not recompute, or a sketch is not fully constrained |
| R1 interference | Two solids of different owners share more than 1 mm3. An owner is one purchased part, the shell, the bezel, or the hood face. A printable part is also compared with all hardware. Two button nuts are compared by R5 only. |
| R2 keep-out | A solid of one owner is in a keep-out zone of a different owner |
| R3 containment | A hardware solid or a trim plate is outside the shell envelope |
| R4 print fit | A printable part is larger than the 256 mm bed. More than 240 mm gives a warning. |
| R5 button spacing | Two button nuts overlap by more than 1 mm. A smaller overlap gives a warning. |

R6 compares the ergonomic values with their target ranges. R7 counts the parameters that are not measured. These two rules give warnings only.

## View the model

Open `cad/out/candybar.FCStd` in FreeCAD. The shell is opaque, so the hardware inside is not visible. The keep-out zones and the alternate bezel plates are hidden. To show or hide an object, select it in the tree and press the space bar.

### Live session for Claude

The FreeCAD MCP addon (`neka-nat/freecad-mcp` 0.1.30) is installed in `~/.local/share/FreeCAD/v1-1/Mod/FreeCADMCP`. The MCP server is registered in Claude Code as `freecad`.

```sh
cad/tools/freecad-gui.sh             # start FreeCAD with the RPC server
cad/tools/fcrpc.py show              # open the built model in the running FreeCAD
cad/tools/fcrpc.py show --inside     # the same, with a translucent shell
cad/tools/fcrpc.py show --keepouts   # the same, with the keep-out zones
cad/tools/fcrpc.py shot view.png --view Right
```

CAUTION: The RPC server runs all Python code that a local program sends to port 9875. Start FreeCAD with `cad/tools/freecad-gui.sh` only when you want that access. FreeCAD started from the desktop does not start the server.

## Frames and roles

The global frame has its origin on the desk, at the cabinet front face, on the center line. X points to the right of the player. Y points from the front face to the rear. Z points up.

Each assembly is an `App::Part` with its own local frame. The module that defines the assembly describes the frame.

Each solid has a `CB_Role` property. The checks use this property.

| Role | Meaning |
| --- | --- |
| `hardware` | A purchased part |
| `protrusion` | Hardware that goes through the shell: the lever shaft, the ball, the button caps |
| `keepout` | Space for a plug, a cable, airflow, or a part that is not designed |
| `massing` | The shell solid |
| `trim` | A visible plate in the shell: a bezel plate, a speaker grille, the marquee window, the light strip |
| `printable` | A designed part for the printer |

## Code

| Path | Content |
| --- | --- |
| `params/` | The parameter sheets |
| `candybar/params.py` | Loads and validates the sheets. Writes the `Params` sheet. |
| `candybar/model.py` | The FreeCAD mechanics: bound placements, solids, sketches, roles |
| `candybar/hardware.py`, `panel.py`, `massing.py` | The assemblies, written as tables |
| `candybar/check.py` | The rules |
| `candybar/export.py`, `render.py` | STEP and STL files, line drawings |
| `candybar/style.py`, `decorate.py` | Colors and visibility for each role, and the build step that stores them |
| `candybar/freecad-run.sh`, `launch.FCMacro` | Run one module in FreeCAD and return its exit status |
| `tests/` | The tests |
| `tools/` | The FreeCAD launcher, the RPC client, the vendor fetch script |

## Reference CAD

`cad/tools/fetch_vendor.sh` fetches three third-party repositories into `cad/vendor/`. It also examines three files from Printables, which you must download by hand. The script gives a non-zero exit status until these files are there. Git ignores `cad/vendor/`. The licenses of these files do not permit redistribution, so do not copy their geometry into tracked files. The build does not use them.

The research notes are in `docs/research/`.
