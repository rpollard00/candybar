# One model, not two

Date: 2026-11-14. Status: the plan of the work package "one model". The section "Result" at the end gives what was done.

The repository had two models. The older generator made a massing model from the parameter sheets, with its own checks, drawings and exports. The blueprint shell (`cad/candybar/shell/`) is the design since revision 5. The owner rejected the shell of the older generator on 2026-11-10. This plan removes the older generator and keeps the parts of it that the blueprint shell uses.

## What the blueprint shell uses

The fit study (`shell/fit.py`) is the only heavy user. The width study and the structure use the sheets through it.

| Older module | Used by the blueprint shell | Not used |
| --- | --- | --- |
| `params.py` | `load`, `Param`, `ParamError`, `write_sheet`, `value` (the fit study, `width_run.py`, `structure.py`) | `edit` (the saved document). `table` served the older report only. |
| `model.py` | `Model.expr`, `number`, `bind`, `place`, `pose`, `assembly`, `solid`; `Prim`, `box`, `cyl`, `ball`; `Pose`, `leaning_back`, `Assembly`; `tag`, `Placed`, `placed`, `world_shape` | The sketches, the PartDesign bodies, the booleans, `Corner`, `Side`, `fingerprint`. `errors` had no caller in the fit study. |
| `hardware.py` | `MONITOR`, `COMPUTE`, `PSU`, `CABLE_BUNDLE` | `ASSEMBLIES`, `build` |
| `panel.py` | The lever, the action buttons, the encoder, the nut tags, `SERVICE_COUNT` | The two printed deck tiles, the bosses, the fixing holes, the service buttons at `svc_y` |
| `check.py` | The levels, `VOLUME_TOLERANCE`, `Scene`, rules R1, R2 and R5 (called by their private names) | R0, R3, R4, R6, R7, the report and its writers |
| `massing.py`, `build.py`, `decorate.py`, `export.py`, `render.py`, `style.py` | Nothing | All |
| `params/printer.csv`, `hardware.csv`, `controls.csv` | The fit study, the split, the coupon | Some rows that only the deck tiles and the outline shell read |
| `params/cabinet.csv` | `psu_raise`, `bc_gap_door`, `cradle_t`, `vent_out_w`, `vent_out_h`. The fit study replaces 23 more rows with its anchors. | 84 rows of the outline shell and of its checks |

The tools:

- `cad/build.sh` builds the older model only.
- `tools/fcrpc.py show` opens `cad/out/candybar.FCStd` and uses `style.py`.
- `tools/fit_reference.py` belongs to the study of variants A to C (2026-11-09). Its command `export-hardware` reads a built `candybar.FCStd`. Nothing calls this tool.

The tests: 80 tests in 9 files run the older generator. They take the document from `build.run` or from `cad/build.sh`.

## Decision record 0001

Decision record 0001 says three things. This is what stays true.

| Statement of the record | After this work |
| --- | --- |
| The FreeCAD document is a build output and git does not track it. | True. `shell.FCStd` is a build output. |
| The scripts generate the model from the CSV sheets in `cad/params`, so that a changed dimension is checked again. | True for the hardware: each size of a purchased part comes from a sheet, and the fit study binds each envelope to the sheet. Not true for the outer form since revision 1 of the blueprint: `shell/dims.py` (class `Blueprint`) holds it. |
| The document follows an edit of its own parameter sheet. | No longer true. No saved document has a parameter sheet. The fit study makes its document, checks it and closes it. |

The record needs a note from the owner about the second and the third row. This work does not edit the record.

## What moves, and where

All of it moves into `cad/candybar/shell/`, because the other modules of the design are there. The file names stay where the content stays, so that a caller changes one import line.

| From | To | Change |
| --- | --- | --- |
| `candybar/params.py` | `candybar/shell/params.py` | Without `edit`. `table` stays, for the list of rule R7. |
| `candybar/model.py` | `candybar/shell/model.py` | Only the parts in the table above. `errors` stays without its sketch rule, and the fit study calls it. |
| `candybar/hardware.py` | `candybar/shell/hardware.py` | The four assemblies. No `build`. |
| `candybar/panel.py` | `candybar/shell/controls.py` | The lever, the buttons and the encoder. The control panel of the fit study (`control_panel`) moves here from `fit.py`, with the rule for `btn_count`. The new name says what is left: the tiles are gone, and "panel" is the plate of the blueprint. |
| `candybar/check.py` | `candybar/shell/check.py` | The levels, the tolerance, `Scene`, and the rules with public names: `interference`, `keepout`, `button_spacing`. With `ergonomics` for the two targets of R6 that have no other check, and `to_measure` and `status_counts` of R7. |

No module keeps an old name for a caller, and there is no compatibility layer.

## What happens to each check

| Rule of the older generator | After this work |
| --- | --- |
| R0 object state | `fit.build_items` calls `model.errors` and stops when an item is not one valid solid. Before, the fit study left such an item out of its checks and said nothing. The rule for sketches goes with the sketches. |
| R1 interference, R2 keep-out, R5 button spacing | The same code, in `shell/check.py`. The fit study runs them, as before. |
| R3 containment in the outline shell | Gone. The fit study has "containment in the cavity" since 2026-11-10. |
| R4 print fit of the deck tiles | Gone with the tiles. The split measures each piece against the printer (`split.py`, `tests/test_split.py`). |
| R6 ergonomics | The sight line and the eye distance: `fit.sight_lines` for three players (the owner's rule of 2026-11-11). The height of the panel top and the palm rest: the fit study writes them to `fit/warnings.md` with their targets. They were warnings, and they stay warnings. |
| R7 parameter status, "Still to measure" | The fit study writes the list to `fit/warnings.md`. `docs/roadmap.md` points to `cad/out/report.md` for this list. |

`fit/report.md`, `fit/report.json` and `fit/sections.json` do not change. `fit/warnings.md` is a new file beside them.

## The parameter sheets

`printer.csv`, `hardware.csv` and `controls.csv` keep all their rows. They are the dimensions of the purchased parts, and the roadmap says that the dimensions stay.

`cabinet.csv` loses each row that the blueprint shell does not read:

- The 84 rows of the outline shell go (for example `cab_d`, `hood_r`, `sweep_r`, the bezel windows, the eye position and its two targets).
- The 23 rows that the fit study replaced go. The fit study calculates these values from `Blueprint` and `Layout`, and it adds them to the sheet as derived rows. A row in the CSV file with a different number was wrong.
- Nine rows stay: `psu_raise`, `bc_gap_door`, `cradle_t`, `vent_out_w`, `vent_out_h`, and the four limits of the targets `tgt_panel_top` and `tgt_palm` for `fit/warnings.md`.

## What is deleted

- `candybar/massing.py`, `build.py`, `decorate.py`, `export.py`, `render.py`, `style.py`, and the five modules that moved.
- `tools/fit_reference.py`. Its hardware export needs a document that no build makes. Its results are in `docs/research/`.
- The options `--inside` and `--keepouts` of `tools/fcrpc.py show`. `shell.FCStd` holds the outer form only. `show` opens `shell.FCStd`.

## The tests

The older tests go in the same step as the code that they run. Each row says what a group protected and which test protects it after this work.

| Tests (count) | Protected | After this work |
| --- | --- | --- |
| `test_params.py` (11) | The loader and the sheet | 10 stay, on `shell/params.py`. The test of `edit` goes with `edit`. The test of a formula that names a later row stays without its edit. |
| `test_check.py` (20) | The rules on the older document | R1 between two purchased parts, R2, R5 and the state of an item: new tests on the document of the fit study (`test_fit.py`, class `ItemRulesTest`). The warnings of R6 and R7: class `WarningsTest`. The tests of R3, R4, the skin, the trim plates and the report go with their code. `FitOnTheRealCavityTest` protects containment. |
| `test_build.py` (8) | The envelopes of the BC-250, `btn_count`, the tiles, the GUI rebuild | The board on its straight edge and the rule for `btn_count`: new tests in `test_fit.py` (class `EnvelopeTest`). The vents in the rear wall of the outline shell: `FitOnTheRealCavityTest` (the duct inside the door). The tiles and the GUI rebuild go. |
| `test_live.py` (6) | The envelopes follow the sheet | The monitor leans by the recline, the power supply is measured from the rear of its bay, a button follows its offset: new tests in `test_fit.py` (class `EnvelopeTest`), each on a document made with a changed value. The tests of the tiles go. |
| `test_shell.py` (18) | The outline shell | Gone. `test_blueprint_solids.py`, `test_face_check.py` and `test_edge_finish.py` protect the form of the blueprint. |
| `test_export.py` (4) | The STEP and STL files of the older model | New tests of `solids.export` (`test_outputs.py`): each part has a BREP and an STL file, the BREP file reads back with the same volume, and the STEP file holds each part. |
| `test_view.py` (11), `test_decorate.py` (4), `view_probe.py` | The saved document shows its solids, and the view step does not change FreeCAD's settings of a person | New tests of `shell/viewdoc.py` (`test_outputs.py`): each solid of `shell.FCStd` is on show with its colour. `viewdoc` gets the guard of `decorate` (it refuses to run outside the throwaway user directory), with its tests. |
| `test_exit_status.py` (7) | The exit status of `cad/build.sh`, and no stale output after a build that broke | New tests of the new `cad/build.sh` and of `freecad-run.sh` (`test_build_entry.py`): a module's result is the exit status, an error gives status 1, and a build that cannot start leaves no part file of an earlier build. |

## The build entry

`cad/build.sh` stays and builds the blueprint shell. A person who knows the repository types this command, and the roadmap and the tests name it. `cad/check.sh` is new.

| Command | Does | Time |
| --- | --- | --- |
| `cad/build.sh` | Removes the part files of an earlier build, builds the outer form (`shell.solids`), and writes `shell.FCStd` (`shell.viewdoc`) | 2 minutes |
| `cad/check.sh` | Runs each check of the design on the build: the solids against the faces, the faces, the edge finish, the fit study, the split and the structure. The exit status is 1 when a check fails. | About 1 hour with the skin in the cache |
| `cad/test.sh` | Runs the tests of the code | About 30 minutes |

## Steps

Each step leaves the tests in a passing state, and each step is one commit.

1. This plan.
2. The replacements first: the new tests of the envelopes and of the rules on the document of the fit study, the state rule in `fit.build_items`, `fit/warnings.md`, the guard and the test of `viewdoc`, the test of `solids.export`. The older generator is still there, so both sets of tests pass.
3. The older generator goes: `massing.py`, `build.py`, `decorate.py`, `export.py`, `render.py`, `style.py`, their tests, `tools/fit_reference.py`, and the older `cad/build.sh`. `tools/fcrpc.py` opens `shell.FCStd`.
4. The five modules that the fit study uses move into `candybar/shell/`, without the parts that have no caller. Each caller changes in the same commit.
5. `cabinet.csv` loses the rows that the blueprint shell does not read.
6. The build entry: `cad/build.sh`, `cad/check.sh`, their tests, `cad/README.md`.
7. The proof, and the result in this file.

## Result

Date: 2026-11-14. The steps are done, and each is one commit on the branch `t3/pal-remove-older-generator`.

### What changed against the plan

- `params.table` stays, because `fit/warnings.md` uses it.
- The tests of `solids.export` and of `viewdoc` are in `tests/test_outputs.py`. The tests of `freecad-run.sh`, `cad/build.sh` and `cad/check.sh` are in `tests/test_build_entry.py`.

### The proof

The proof ran on the server (FreeCAD 1.1.4). On this machine the code of commit 3633457 does not give the results that the roadmap records. These faults are older than this work, and this work does not touch their code:

- `candybar.shell.solids` stops at the edge break of the hood: `tool 1 still holds 0.013 mm3 of 0.013`. The same error comes in each run, also on one processor core.
- The body has 47166388.0 mm3 here. The reference build (`~/.local/share/candybar/out/shell-rev7`) has 47165352.4 mm3. The face count is the same (191).
- The split stops: the skin of the body from the cache is not a valid shape (158 of 16248 faces).
- Three tests of the joint coupon fail (clearance 0.2, part `upper-c02`).

Thus each proof run used the same aid before and after: the hood comes from the reference build (`hood.brep`), and the build makes each other part. The aid is `cad/out/_proof.py`. It is not in git.

| Item | Before (3633457) | After | Result |
| --- | --- | --- | --- |
| Parts: volume and face count | 10 parts | 10 parts | The same for each part |
| Parts: BREP files | | | 9 of 10 have the same bytes. `deck.brep` has the same records in a different sequence. |
| Parts: `tools/compare_parts.py`, tolerance 0.000001 | | | Pass. The largest distance is 0.0000 for the deck and for each small part. The body and the hood have the same bytes. |
| Fit study: `report.md`, `report.json`, `sections.json` | PASS | PASS | The same bytes |
| Split | Stops at the skin from the cache | Stops at the same line | No report on this machine. `split.py`, `joints.py`, `printer.csv` and the four files of the skin fingerprint have no change, and the fingerprint is `6399ee9bd8a99553` in the two runs. |
| Tests, with the aid | 214 run, 5 failures, 1 error, 53 minutes | 173 run, 5 failures, 1 error, 50 minutes | The same 6 items fail. No test changed its result. |
| Tests, without the aid | 163 run, 3 failures, 7 errors, 18 minutes | 122 run, 3 failures, 7 errors, 15 minutes | The same 10 items fail. No test changed its result. |

The 6 items that fail with the aid are the three coupon tests, two tests of the face check on the default build, and the class `SplitTest` (9 tests that do not run). On a machine where the suite of commit 3633457 passes with 223 tests, the count after this work is 182. This number is not verified.

The split report and the full suite must run again on the machine that made the reference build.

### Tests that are gone

78 tests are gone, and 37 are new.

| File | Count | Reason |
| --- | --- | --- |
| `test_build.py` | 7 | Ran `build.build_document`. The envelope of the BC-250 and the rule for `btn_count` have new tests in `test_fit.py`. |
| `test_check.py` | 20 | Ran the rules on the older document. R1, R2, R5 and the state rule have new tests in `test_fit.py`. |
| `test_live.py` | 6 | Edited the saved document. The monitor, the power supply and the button offset have new tests in `test_fit.py`. |
| `test_shell.py` | 18 | Tested the outline shell. |
| `test_export.py` | 4 | Tested the files of the older build. `test_outputs.py` tests `solids.export`. |
| `test_view.py`, `test_decorate.py` | 11, 4 | Tested the saved document of the older build. `test_outputs.py` tests `viewdoc`. |
| `test_exit_status.py` | 7 | Ran the older `cad/build.sh`. `test_build_entry.py` tests the launcher and the two scripts. |
| `test_params.py` | 1 | Tested `params.edit`, which is gone. |

### A finding for the owner

`fit/warnings.md` shows the palm rest at 92.5 mm against a target of 100 to 120 mm. The front edge of the cabinet to the centre of the nearest action button is shorter since the deck became shorter. The older generator had this check on its own, longer panel, where the value was in the range.

### The proof on the laptop

Date: 2026-11-14. The proof ran again on the laptop, which has OpenCascade 7.9.3 and made the reference build. Here the default build ends, and no aid was used. The "before" run used the code of commit b80698c (the main line with the rear door). The "after" run used the merge of this branch, with the imports of `rear.py` and `tests/test_rear.py` changed to `candybar.shell`. Each run made the solids, the fit study, the split, the structure and the rear.

| Item | Before | After | Result |
| --- | --- | --- | --- |
| Parts: volume and face count | 10 parts | 10 parts | The same for each part |
| Parts: BREP files | | | 8 of 10 have the same bytes. `deck.brep` and `hood.brep` have the same records in a different sequence. |
| Parts: `tools/compare_parts.py`, tolerance 0.000001 | | | Pass. The largest distance is 0.0000. On the faces of the edge break of the hood it is 0.0001. |
| Fit study: the rules | PASS | PASS | The same rules and the same results |
| Fit study: `report.json` | | | The same, except two numbers: the probe of the wall measured 2642 and 2646 points, and the cavity volume differs by 3e-12 l |
| Fit study: `sections.json` | | | 197 polylines. Each has the same points; some start at a different point. |
| Split: `measurements.json` | | | The same bytes |
| Structure: `structure.json` | | | The same bytes |
| Rear: `report.json`, `report.md`, `sections.json` | PASS | PASS | The same bytes |

The hood of the reference build in `cad/out/shell-rev7` has the bytes of the "after" run. Thus the sequence of the records in the hood changes from one run to the next, and this work does not cause it.
