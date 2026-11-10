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
| R1 interference | Two solids of different assemblies share more than 1 mm3. A printable part is also compared with the hardware of its own assembly. |
| R2 keep-out | A solid of one assembly is in a keep-out zone of a different assembly |
| R3 containment | A hardware solid is outside the shell envelope |
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

`cad/tools/fetch_vendor.sh` fetches third-party reference CAD into `cad/vendor/`. Git ignores this directory. The licenses of these files do not permit redistribution, so do not copy their geometry into tracked files. The build does not use them.

The research notes are in `docs/research/`.
