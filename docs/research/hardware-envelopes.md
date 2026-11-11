# Provisional hardware envelopes

Research date: 2026-11-09. All dimensions in millimetres.

These numbers let the FreeCAD parameter sheet be laid out before caliper measurements exist.
Every number is provisional. Replace it with a measured value before any part that touches
the hardware is printed.

## Status tags

| Tag | Meaning |
| --- | --- |
| SOURCED | Stated by a manufacturer, seller or reviewer. The URL is given. |
| MEASURED-FROM-CAD | Measured with FreeCAD 1.1.4 from a CAD file. The file path is given. |
| STANDARD | Fixed by a published specification. The specification is named. |
| ESTIMATED | Derived by calculation, or read off a render or photo. The method is given. |

Community CAD models are reverse-engineered by hobbyists. A MEASURED-FROM-CAD number is exact
for the file, not for the real part.

## Files used

The reference CAD is in `cad/vendor/`. Git ignores that directory. `cad/tools/fetch_vendor.sh`
fetches the repositories at the commits below and checks the downloaded files against their
SHA-256 values.

| Path under `cad/vendor/` | Source | License |
| --- | --- | --- |
| `onemorecap-bc250-shell/` | https://github.com/onemorecap/bc-250-shell-case at `ea2e59bab5ea5f5bd4cfce69b72c4a192391daea` | None declared. Dimensional reference only. |
| `mandic-bc250-board/BC250_Completeish_V1.step` | https://www.printables.com/model/1828755-asrock-bc250-complete-ish-cad-model (MandicReally) | CC BY-NC-SA 4.0 |
| `shinf1x-bc250-dim/bc250_radiator.step` | https://www.printables.com/model/1677793-asrock-bc250-dimension-model (shinf1x) | CC BY-NC 4.0 |
| `mkuu-plus-case/BC250_Case_MKUU_Plus_FSP_Version.3mf` | https://www.printables.com/model/1835961-bc250-case-mkuu-fsp-apevia-metalfish-psu (derps) | CC BY-NC-SA 4.0 |

The MEASURED-FROM-CAD values came from FreeCAD 1.1.4: `Part.read(path)`, then bounding boxes,
cylindrical faces for holes, and section cuts. The measuring scripts and their raw output were
temporary and are not in the repository. `BoundBox` over-reports some of the onemorecap STEP
files; section 3 gives the corrected sizes.

## Inaccessible or partly accessible sources

| Source | Result |
| --- | --- |
| https://www.amazon.com/dp/B0F99H1KSL | Direct fetch not tried. The Kagi extract tool returned the full listing. Usable. |
| https://www.ekwb.com/shop/ek-atx-bridging-plug-24-pin | INACCESSIBLE. HTTP 403 to two fetch methods. Only the search-result summary was read. No dimensions found. |
| https://bambulab.com/en/a1/tech-specs | INACCESSIBLE to direct fetch (HTTP 403). Search-result summary used. |
| https://wiki.bambulab.com/en/a1/manual/faq | INACCESSIBLE to direct fetch (HTTP 402). Search-result summary used. |
| https://www.arctic.de/us/P12-Pro/ACFAN00305A | Page text truncated. The official spec sheet PDF was read instead. |
| https://www.startech.com/en-us/audio-video-products/dp2hd4k60s | Spec table not returned. Adapter dimensions are ESTIMATED. |
| https://www.techpowerup.com/articles/160/images/ATX_2_2.pdf | Blocked. The same document was read from a mirror. |
| UPERFECT user manual | Not found. Port and control positions come from manufacturer renders and one review. |

---

## 1. UPERFECT 16-inch monitor

### Identity

| Item | Value | Status |
| --- | --- | --- |
| Manufacturer model | BE16CU, formerly sold as "UColor T6". Image file names on the product page carry the code `m160t06`. | SOURCED https://uperfect.com/products/16-inch-4k-sunlight-readable-monitor |
| Amazon identifiers | ASIN B0F99H1KSL, "Model Number 60T", "Model Name 16006DD" | SOURCED https://www.amazon.com/dp/B0F99H1KSL |
| Variant | The Amazon title says "VESA & Smart Case". That is the flat BE16CU with a magnetic cover. | SOURCED (Amazon) |
| Sister variant | BE16DU Gen 2 has a built-in "LS" stand and is 357 x 240 x 15. Rule this out on the real unit. | SOURCED (uperfect.com) |

### Envelope

| Item | Value | Status |
| --- | --- | --- |
| Body W x H x T | 354 x 230 x 10 | SOURCED (uperfect.com, "Product Size") |
| Body W x H x T, second source | 355.3 x 228.6 x 10.2 (13.99 in x 9 in x 0.4 in) | SOURCED (Amazon "Item Dimensions") |
| CAD envelope to reserve | 356 x 231 x 11 | ESTIMATED: larger of the two sources, plus 1 |
| Thickness profile | Uniform slab. No thicker chin or port bump. | ESTIMATED: manufacturer side renders in the product gallery |
| Small protrusions | Two rubber feet on the bottom edge. Power button and scroll wheel stand proud of the right edge by about 1 to 1.5. | ESTIMATED: manufacturer front render |
| Active area | 344.678 x 215.424 | SOURCED (uperfect.com, "Viewable Area") |
| Pixel pitch | 0.0898 (344.678 / 3840) | ESTIMATED: calculation. The page rounds it to 0.09. |
| Side bezels | 4.66 each | ESTIMATED: (354 - 344.678) / 2, assumes symmetry |
| Top plus bottom bezel | 14.58 total. Split about 5 top and 9.6 bottom. | ESTIMATED: 230 - 215.424. The split is read off a render and is weak. |
| Weight | 0.82 kg (1.8 lb) | SOURCED (uperfect.com, Amazon) |
| Power | 14 W rated (uperfect.com). Amazon states 30 W. | SOURCED, sources disagree |

### Mounting

| Item | Value | Status |
| --- | --- | --- |
| VESA pattern | 75 x 75 | SOURCED (uperfect.com, Amazon, Newegg) |
| Thread | M4 | SOURCED ("75*75mm@M4*4mm") |
| Usable thread depth | 4. Screw engagement into the monitor must not exceed 4. | SOURCED (uperfect.com: "standard M4*4mm screws") |
| Pattern position | Centred left to right. Vertical centre about 113 to 115 from the top edge. | ESTIMATED: manufacturer rear render, about +/-3 |
| Built-in kickstand | None on BE16CU ("Stand Holder: No", "Cover Case: Yes"). The back is flat. | SOURCED (uperfect.com; https://www.linuxlinks.com/uperfect-ucolor-t6-review/) |

### Connectors and controls

Edges are named as seen from the front, screen in landscape.

| Item | Edge | Height above bottom edge | Status |
| --- | --- | --- | --- |
| USB-C, full function (video, audio, power) | Left | about 86 | Edge: SOURCED (LinuxLinks photo "Left Hand Side", manufacturer render). Height: ESTIMATED from render, +/-5. |
| USB-C, full function | Left | about 68 | Same |
| Mini-HDMI (HDMI Type C) | Left | about 49 | Same |
| Power button | Right | about 66 | Edge: SOURCED (LinuxLinks photo "Right Hand Side"). Height: ESTIMATED from render, +/-5. |
| Status LED | Right | between the button and the wheel | Same |
| Scroll wheel (OSD) | Right | about 50 | Same |
| 3.5 mm audio output | Right | about 30 | Same |
| Speakers, 2 x 8 ohm 1 W | Slot groups in the left and right edges | about 130 to 151 | Rating: SOURCED (uperfect.com). Position: ESTIMATED from render. |

All plugs enter sideways, parallel to the screen. No connector is on the back or the bottom.

### Other 16 inch 16:10 portable monitors (survey of 2026-11-10)

The owner wants the cabinet to take a replacement monitor. A 16.0 inch 16:10 panel has the same lit area on all these units (344.68 x 215.42 where the maker gives it), so the bezel window stays. The body changes. Values are the maker's numbers unless the status says otherwise.

| Model | Body W x H x T | Bezel each side across / along (ESTIMATED: (body - lit area) / 2) | Ports | VESA | Status |
| --- | --- | --- | --- | --- | --- |
| UPERFECT BE16CU (the present unit) | 354 x 230 x 10 | 4.7 / 7.3 | Left: 2 x USB-C, mini-HDMI. Right: controls, 3.5 mm jack. | 75 x 75, M4 | SOURCED, see above |
| ASUS ZenScreen MB16QHG | 359.7 x 247.1 x 7 to 20.6 (built-in kickstand) | 7.5 / 15.8 | 2 x USB-C, HDMI, 3.5 mm jack; edge not stated | None. A 1/4 inch tripod socket. | SOURCED https://www.asus.com/displays-desktops/monitors/zenscreen/asus-zenscreen-mb16qhg/techspec/ |
| ViewSonic VG1656-2K | 356.7 x 234.9 x 9.6 | 6.0 / 9.7 | One USB-C on the left, one on the right | Not stated | SOURCED https://www.viewsonic.com/global/products/sheet/VG1656-2K |
| Lenovo ThinkVision M16 | 360.0 wide; 252.1 high with its stand at the lowest position; panel 7 thick, 27 with the stand | 7.7 / not read | One USB-C on the left, one on the right | Not stated | SOURCED https://psref.lenovo.com (ThinkVision M16 spec); thickness SOURCED (summary) from notebookcheck.net |
| Arzopa Z1RC | 356 x 240 x 9 (retail listings; one review measured 14 x 9 7/16 x 5/16 in) | 5.7 / 12.3 | Not read | Not read | SOURCED (summary) from retailer pages and the-gadgeteer.com; no maker page read |

Result, the generic body the cabinet must take (`hardware.csv`):

| Value | Named value | From |
| --- | --- | --- |
| Width 360 | `mon_gen_w` | Lenovo ThinkVision M16 |
| Height 247.1 | `mon_gen_h` | ASUS MB16QHG. The M16 height without its stand is not stated. |
| Thickness 20.6, thinnest 7 | `mon_gen_t`, `mon_gen_t_min` | ASUS MB16QHG at its kickstand and at its thin edge |
| Movement in the plane of the face, 8 each way | `mon_adjust` | Half the spread of the bezel widths is 1.5 across and 4.3 along the face. Both are below the floor of 8, so 8 is used. PROVISIONAL |

Notes:

- Two of five units have no VESA holes, or none that the maker states. The mount must not need them: a clamp on the top and bottom edges (`mon_clamp_edge`) holds any of these bodies.
- Three of five units have ports on both side edges. The cabinet keeps plug space on both side edges over the whole height.
- 15.6 inch 16:9 units (for example ASUS MB16AWP, 344.16 x 193.59 lit) do not fit the window. They are not in the survey.

### Keep-out zones

- Left edge, lower half: a straight plug plus cable bend needs 65 to 75 beyond the body edge.
  A right-angle plug or adapter needs 15 to 20. See section 8. ESTIMATED.
- Right edge, lower half: finger access to the button and wheel, or a tested "always on"
  behaviour. Leave the 3.5 mm jack reachable if monitor audio is used.
- Both side edges at mid height: do not seal the speaker slots if the built-in speakers are used.
- Back: flat. A VESA plate 75 x 75 with four M4 screws. Screw length = plate thickness + 4 maximum.
- The cradle must also support the bottom edge. Four M4 threads with 4 of engagement in a
  10-thick aluminium body are retention, not the only support.

### Must measure on the real unit

1. Body width, height and thickness, including the feet and the button protrusion.
2. Whether a built-in stand exists (BE16CU or BE16DU Gen 2).
3. VESA hole centres to the left edge and to the bottom edge. Real thread depth.
4. Port centre heights on the left edge and their offset from the front face.
5. Active area position: left, right, top and bottom bezel, measured to the lit pixels.
6. Button, wheel and jack heights on the right edge.
7. Plug length plus bend of the actual cables that will be used.
8. Weight.
9. Behaviour after power loss: does the monitor turn on without a button press.

---

## 2. ASRock BC-250

Primary geometry source: MandicReally "ASRock BC250 Complete-ish CAD Model", measured from
`cad/vendor/mandic-bc250-board/BC250_Completeish_V1.step`. The author states that it was
reverse-engineered with calipers and corrected photos, and that it is not manufacturer CAD.
Cross-checks: the second community model (`cad/vendor/shinf1x-bc250-dim/bc250_radiator.step`) and the
onemorecap shell cavity (section 3). The three agree within about 1.

### Board datum used below

- Origin: PCB corner at the I/O end, on the long edge that is straight for the full length.
- x' runs from the I/O edge toward the power-connector end.
- y' runs from the straight long edge toward the stepped long edge.
- z' = 0 at the PCB top face (heatsink side). +z' is toward the heatsink.
- Conversion from the model: x' = X + 153.0, y' = 71.83 - Y, z' = Z - 1.6.
- In the model, the stock heatsink group is displaced by +200 in Y and the backplate by -200 in Y.
  The values below are corrected. The hole positions confirm the correction.

### PCB

| Item | Value | Status |
| --- | --- | --- |
| Overall | 307.6 x 144.0 x 1.55 | MEASURED-FROM-CAD (Mandic STEP, part `PCB/SOLID001`) |
| Outline | L-shape. From x' = 0 to 207.4 the board is 122.21 wide (y' 0 to 122.21). From x' = 207.4 to 307.6 it is 144.0 wide (y' 0 to 144.0). Corner radius 2.0. | MEASURED-FROM-CAD |
| Width, second source | "Approximately 115", length "340 / 310 depending on measurement method" | SOURCED https://elektricm.github.io/amd-bc250-docs/hardware/specifications/ (less precise; the CAD value is preferred) |

### Holes in the PCB

| Purpose | Diameter | Centres (x', y') | Status |
| --- | --- | --- | --- |
| Heatsink / cooler pattern, 95.75 x 95.75 square centred on the APU | 4.60 | (124.30, 13.31), (124.30, 109.06), (220.05, 13.31), (220.05, 109.06) | MEASURED-FROM-CAD (Mandic). The second model gives 96.0 x 96.0. A Printables comment states "95x95mm hole spacing" (https://www.printables.com/model/1042228-bc250-to-amd-cpu-cooler-mount/comments/2688862). |
| Backplate standoffs, 4 off | 3.3 to 3.5 | (51.85, 17.68), (82.25, 114.50), (277.45, 37.75), (292.25, 114.25) | MEASURED-FROM-CAD (Mandic). The second model agrees within 0.4 relative to the cooler pattern. |
| I/O bracket screws | 3.40 | (7.70, 12.71), (7.70, 112.51) | MEASURED-FROM-CAD |
| Unidentified pair near the far end | 4.00 | (298.60, 18.81), (298.60, 28.81) | MEASURED-FROM-CAD |
| APU package centre (reference) | - | (172.23, 61.31) | MEASURED-FROM-CAD |

The four standoff positions are the natural tray fixing points. The stock standoffs are 7.95
outside diameter and 4.0 long, between the backplate and the PCB. Thread size is not known.

### Stack and overall envelope

| Item | Value | Status |
| --- | --- | --- |
| Backplate | 285.1 x 120.9 x 1.2. x' 17.08 to 302.18, y' 0.88 to 121.78. Outer face at z' = -5.55. | MEASURED-FROM-CAD |
| PCB bottom face | z' = -1.55 | MEASURED-FROM-CAD |
| Stock heatsink fin block | 239.54 x 119.50. x' 47.14 to 286.68, y' 1.80 to 121.31. Top at z' = 26.10. | MEASURED-FROM-CAD (part `Heatsink/Heatsink Fin Array`; modelled as one block, not as single fins) |
| Fin block outline (x', y') | (47.14, 1.80) (242.25, 1.80) (242.25, 30.80) (286.68, 30.80) (286.68, 121.31) (83.99, 121.31) (83.99, 102.93) (47.14, 102.93) (47.14, 70.98) (56.99, 70.98) (56.99, 39.28) (47.14, 39.28) | MEASURED-FROM-CAD |
| Notch in the fin block | 44.4 x 29.0 at the far corner on the straight edge, for the CR2032 holder and jumpers | MEASURED-FROM-CAD |
| Overall height, backplate to fin top | 31.65 | MEASURED-FROM-CAD. The onemorecap cavity is 31.9 high. |
| Height above the PCB top face | 26.1 (heatsink). Tallest other part: power/status button, 22.85. | MEASURED-FROM-CAD |
| Overall module, no I/O bracket | 311.8 x 144.3 x 31.65. x' -4.2 to 307.6, y' 0 to 144.28, z' -5.55 to 26.10. | MEASURED-FROM-CAD |
| I/O bracket | Not modelled. The MKUU+ instructions remove it. | SOURCED (Printables 1835961, assembly step 1) |
| Fin direction | Fins run along the board length (x'). | SOURCED (elektricM docs: "Fins run front-to-back"; onemorecap render shows fin lines along the length) |
| Fin tops | The stock fin stack does not accept air from above until the fin tops are opened. Community builds "open" or "straighten" them under a top-mounted fan. | SOURCED (Printables 1835961; elektricM cooling page) |
| Heatsink variants | Three variants are reported (8-row and 9-row fins). | SOURCED https://elektricm.github.io/amd-bc250-docs/hardware/cooling/ |

### Connectors

| Item | Position (x', y', z' top) | Status |
| --- | --- | --- |
| I/O edge | The short edge at x' = 0. Connector faces overhang the PCB edge by 1.0 to 1.7. | MEASURED-FROM-CAD |
| Gigabit Ethernet (RJ45) | y' 89.18 to 104.93, top 13.8 | MEASURED-FROM-CAD |
| USB 3.0, two stacked | y' 69.61 to 84.06, top 16.47 | MEASURED-FROM-CAD |
| DisplayPort, full size | y' 48.61 to 66.40, top 10.96 | MEASURED-FROM-CAD |
| USB 2.0, two stacked | y' 31.13 to 46.53, top 15.80 | MEASURED-FROM-CAD |
| Power / status button | y' 18.60 to 27.00, top 22.85. Protrudes to x' = -4.2. | MEASURED-FROM-CAD |
| Port list | 1 x DisplayPort 1.4, 2 x USB 3.0, 2 x USB 2.0, 1 x GbE. No HDMI. | SOURCED (elektricM specifications) |
| M.2 socket (M key, 2280, PCIe 2.0 x2 or SATA) | Socket at x' 20.4 to 42.3, y' 6.6 to 12.6, top side. Standoff post at (31.4, 88.6). The drive lies across the board between the I/O connectors and the heatsink, about x' 20 to 43, y' 8 to 90, top at about z' 10. | MEASURED-FROM-CAD (position). SOURCED (type: elektricM; https://github.com/mothenjoyer69/bc250-documentation/blob/main/hardware.md) |
| 8-pin PCIe power, J1000 | x' 224.6 to 243.0, y' 131.3 to 143.8, top 11.35. Right-angle header on the stepped long edge. The plug enters from outside that edge, moving in -y'. | MEASURED-FROM-CAD (position). SOURCED (type: mothenjoyer69 hardware.md, "standard 8-pin PCIe connector"). The onemorecap shell has a 22 x 16 wall opening at the same place. |
| Micro-Fit 8-pin, J2000 and J2001 (rack power, unused here) | x' 246.0 to 285.1, y' 132.6 to 144.3 | MEASURED-FROM-CAD |
| Fan headers | CPU_FAN1 4-pin PWM and J4003 (2 x 8, 2.54 pitch). Two header bodies at x' 286.5 to 302.2, y' 119.8 to 141.3. Which body is which is not confirmed. | MEASURED-FROM-CAD (bodies). SOURCED (names: mothenjoyer69 hardware.md) |
| CR2032 holder | x' 264.5 to 286.6, y' 5.3 to 29.6, top 9.1 | MEASURED-FROM-CAD |
| External power switch | Onboard button only. No header. | SOURCED (elektricM specifications) |
| Auto power-on | Jumper AUTO_PWRON1, pins 1-2 = boot when power is applied (default). | SOURCED (mothenjoyer69 hardware.md) |

### Power and heat

| State | Power | Status |
| --- | --- | --- |
| Idle | 65 to 105 W | SOURCED (elektricM specifications, "Measured Power Draw") |
| Light gaming | 120 to 150 W | SOURCED (same) |
| AAA gaming | 160 to 200 W | SOURCED (same) |
| Maximum | 235 W ("220W TDP") | SOURCED (same) |
| Heat to remove from the cabinet | 250 to 300 W: board, plus PSU loss, plus monitor | ESTIMATED: 200 to 235 + about 12 % PSU loss + 14 to 30 |
| Airflow for that heat | about 50 m3/h at 15 K air temperature rise | ESTIMATED: Q = P / (1.2 x 1005 x dT) |
| Vent free area | at least 100 cm2 intake and 100 cm2 exhaust | ESTIMATED: equal to the swept area of one 120 mm fan |

### Airflow used by community cases with one 120 mm fan

- MKUU+ (section 4): the fan axis is perpendicular to the PCB. The fan sits over the heatsink at
  the CR2032 end (high x'), blows down into opened fins, and the air leaves along the fins toward
  the I/O end. Optional 40 or 50 mm exhaust fans sit at the I/O end of the case.
- onemorecap (section 3): the fan sits on the top face of a plenum at and beyond the high-x' end
  of the board. Air turns 90 degrees, travels the full fin length, and leaves at the open I/O end.
  The stock fins are not modified.
- Both move air from the power-connector end to the I/O end. The hot exhaust therefore passes over
  the DisplayPort plug and the USB cables.

### Keep-out zones

- Above the heatsink at the high-x' end: fan 25 plus a shroud or plenum. See sections 3 to 5.
- Beyond the stepped long edge at x' 220 to 248: 8-pin plug plus cable bend, 50 to 60. ESTIMATED.
- In front of the I/O edge: DisplayPort plug and adapter, 45 minimum, and this is the exhaust path.
- Below the backplate: the GDDR6 memory is on the underside and has no sensor. Keep an air gap
  and some airflow there. SOURCED (elektricM cooling page).
- Access to the power button at the I/O edge, y' 18.6 to 27.0.

### Must measure on the real unit

1. PCB length, both widths, and the position of the width step.
2. Height from backplate outer face to fin top. Height of the fan plus shroud stack that will be used.
3. The four standoff hole centres and their thread. Whether the stock backplate stays fitted.
4. Heatsink variant, fin direction, fin-top condition.
5. 8-pin PCIe connector position and orientation. Clearance with the real PSU lead plugged in.
6. DisplayPort centre height and position. Length of the chosen adapter chain.
7. M.2 drive fit and height, with the drive that will be used.
8. Fan header location and reach of the P12 Pro cable (400).
9. Weight of the assembled module.
10. Wall power under the hardest game, for the vent sizing.

---

## 3. onemorecap BC-250 shell

Path: `cad/vendor/onemorecap-bc250-shell`
Commit `ea2e59bab5ea5f5bd4cfce69b72c4a192391daea`. License: none declared.

### Files

| Folder | Files |
| --- | --- |
| `step/` | `connector.step`, `dummy-c14.step`, `front-shell.step`, `handle.step`, `rear-shell-a.step`, `rear-shell-b.step` |
| `stl/` | `connector.stl`, `dummy-c14.stl`, `front-shell.stl`, `handle.stl`, `rear-shell-a.stl`, `rear-shell-b.stl` |
| `3mf/` | `bc-250-shell-case-all-in-one.3mf`, `dummy-c14.3mf`, `front-shell.3mf`, `handle.3mf`, `rear-shell-a.3mf`, `rear-shell-b.3mf`, `shell-connector.3mf` |
| Other | `README.md`, `renders/` (7 PNG), `photos/` (8 JPG), `fan-test/` (P12, S12038-4K, T30 photos and videos), `bc-250-shell-case-fillament.png` |

The repository does not contain a model of the board. The all-in-one 3MF holds only the five
printed parts. No `.FCStd` file is present. Nothing from the repository was executed.

### Bounding boxes (shell coordinate system of the files)

All MEASURED-FROM-CAD from `step/*.step`. Each file holds one solid.

| Part | X range | Y range | Z range | Size |
| --- | --- | --- | --- | --- |
| `front-shell.step` | -172.60 to -55.00 | -56.20 to 74.80 | -8.30 to 31.60 | 117.60 x 131.00 x 39.90 |
| `rear-shell-a.step` | 53.00 to 158.00 | -77.20 to 74.80 | -8.30 to 31.60 | 105.00 x 152.00 x 39.90 |
| `rear-shell-b.step` | 152.00 to 243.00 | -77.20 to 74.80 | -8.30 to 31.60 | 91.00 x 152.00 x 39.90 |
| `handle.step` | -87.92 to 86.00 | 75.13 to 92.13 | 5.65 to 17.65 | 173.92 x 17.00 x 12.00 |
| `connector.step` | 139.00 to 169.00 | -73.20 to -70.20 | 5.60 to 17.60 | 30.00 x 3.00 x 12.00 |
| `dummy-c14.step` | 126.88 to 177.13 | 67.80 to 70.80 | 2.00 to 22.00 | 50.25 x 3.00 x 20.00 |

Note: FreeCAD `BoundBox` reports 96.32 x 164.52 for `rear-shell-b.step`, because of spline control
points. The STL of the same part and the section cuts give the true 91.00 x 152.00 used above.

Assembled shell: 415.6 long (X -172.6 to 243.0), 152.0 wide (169.3 with the handle), 39.9 high
without fan and feet. With a 25 fan on top and 6 feet it is about 71 high. MEASURED-FROM-CAD,
fan and feet added by calculation.

### What the geometry implies

| Feature | Value | Status |
| --- | --- | --- |
| Wall thickness | 4.0 | MEASURED-FROM-CAD |
| Front shell cavity | 123.0 wide (Y -52.2 to 70.8) x 31.9 high (Z -4.3 to 27.6), open at both ends | MEASURED-FROM-CAD (section at X = -100) |
| Rear shell cavity | 144.0 wide (Y -73.2 to 70.8) x 31.9 high | MEASURED-FROM-CAD (section at X = 60) |
| Cavity width step | A wall at X = 55 closes the extra 21 of width. The PCB step in the board model is at X = 54.4. | MEASURED-FROM-CAD, both files |
| Implied board envelope | 122 to 123 wide at the I/O end, 144 wide at the power end, 31.65 to 31.9 thick including heatsink and backplate. Matches section 2. | MEASURED-FROM-CAD |
| Implied board length | The I/O end sits at the open front end, X = -157.6. The shell splits at X = 152 and the PSU starts at X = 165. The module is therefore at most 322 long, and probably ends near X = 152 to 155 (310 to 312 long). | ESTIMATED from the shell. The board model gives 311.8. |
| Board fixing | None. The shells are a friction fit on the module. No board mounting holes exist in the shell. | MEASURED-FROM-CAD; SOURCED (README: "friction-fit design") |
| Uncovered middle | X -55 to 53 (108 long). The heatsink is exposed there. | MEASURED-FROM-CAD |
| Front retention tab | The front shell extends to X = -172.6 on the +Y side only, with one 4.1 hole along Y at X = -165.63, Z = 6.34. | MEASURED-FROM-CAD |
| Fan opening | Diameter 118, centre (X 170.0, Y -1.2), in the +Z face. It spans the split between rear-a and rear-b. | MEASURED-FROM-CAD |
| Fan screw holes | 4 x diameter 4.3 on a 105 x 105 square: (117.5, -53.7), (117.5, 51.3), (222.5, -53.7), (222.5, 51.3). Axis Z. | MEASURED-FROM-CAD; SOURCED (README: 120 x 120 x 25 fan, 105 mm spacing) |
| Fan position relative to the board | The opening covers X 111 to 229. About 43 of it lies over the far end of the board. The rest lies over the plenum beyond the board. | MEASURED-FROM-CAD plus board model |
| Duct layout | The rear shell is a closed plenum with a rounded end (inner radius 72, outer 76, centre X 169, Y -1.2, flat at X = 243). Air enters down through the fan opening, turns 90 degrees, runs through the fin stack along the board, and leaves at the open I/O end. The cavity is the same height as the module, so the fin stack is the only large air path. | ESTIMATED from the geometry and the renders |
| PSU bay | Four 4.25 insert holes in the floor at X 168.2 and 212.65, Y -47.65 and 47.6: a 44.45 x 95.25 pattern. This fits a 4 in x 2 in open-frame supply. | MEASURED-FROM-CAD. README names the Mean Well LOP-300-12. The match to that unit's hole pattern is ESTIMATED. |
| Mains inlet | IEC C14 in the +Y wall. Screw holes at X 132 and 172 (40 apart), Z 12. `dummy-c14` blanks the cut-out. | MEASURED-FROM-CAD; SOURCED (README) |
| Side opening for an external PSU lead | 22 x 16 in the -Y wall, X 70 to 92, Z -0.4 to 15.6. It lines up with the board's 8-pin PCIe header. | MEASURED-FROM-CAD plus board model |
| Feet | 4 recesses, diameter 14 x 1 deep, with 4.25 holes, in the -Z face: (-122.6, -37.2), (-122.6, 55.8), (132.0, -53.2), (132.0, 50.8). | MEASURED-FROM-CAD; SOURCED (README: 12 x 6 rubber feet) |
| Insert holes | Diameter 4.25 for M3 heat-set inserts | MEASURED-FROM-CAD; SOURCED (README) |
| Recommended fans | High static pressure, above 2000 rpm: Phanteks T30, ARCTIC P12 Max, ARCTIC S12038-4K, Noctua NF-F12 iPPC-3000. The P12 Pro is not in the list. | SOURCED (README) |

### Must measure on the real unit

1. Module cross-section at the I/O end and at the power end. A sleeve fit needs these within 0.3.
2. Module length from the I/O connector faces to the far PCB edge.
3. Whether the stock fins on the owned board are still closed on top. This design depends on it.
   The first build opened its fins. Check the second board before choosing this duct layout.

---

## 4. Printables BC250 Case MKUU+ (FSP / Apevia / Metalfish)

Page: https://www.printables.com/model/1835961-bc250-case-mkuu-fsp-apevia-metalfish-psu
Author derps. License CC BY-NC-SA 4.0. Remix of morph91 "BC-250 Gaming PC Case MK Ultra Uno"
(MakerWorld 2749412). The page text was readable. The page states no overall dimensions.

The FSP 3MF downloaded without sign-in, so the sizes below are measured from it.

| Part (name in the 3MF) | Size | Status |
| --- | --- | --- |
| Back case half, FSP (`backFSP w_ cableCutout`) | 89.38 x 180.45 x 173.90 | MEASURED-FROM-CAD (`cad/vendor/mkuu-plus-case/BC250_Case_MKUU_Plus_FSP_Version.3mf`) |
| Front case half (`FRONT FINISHED FINAL CLEANED`, and USB hub version) | 180.44 x 89.38 x 168.87 | MEASURED-FROM-CAD |
| Assembled case | about 343 x 180 x 89 | ESTIMATED: the two half lengths added, no overlap allowed for |
| Fan shroud, original variant, 25 fan | 129.30 x 129.00 x 55.90 | MEASURED-FROM-CAD |
| Fan shroud, original variant, 30 fan | 129.30 x 129.00 x 50.90 | MEASURED-FROM-CAD |
| Fan shroud, heatsink variant, 25 / 30 fan | 131.35 x 129.00 x 55.90 / 50.90 | MEASURED-FROM-CAD |
| Shroud extender, 120 / 150 version | 122.0 / 152.0 x 129.0 x 54.49 | MEASURED-FROM-CAD |
| Fan grill | 124 x 124 x 4 | MEASURED-FROM-CAD |

What the page states (all SOURCED from the Printables page):

- Fan: a high-static-pressure 120 mm fan is required. The ARCTIC P12 Pro PST is the budget choice.
  Separate shroud plates exist for 25 thick and 30 thick fans.
- Fan mounting: the fan is pinned to the printed shroud. The shroud slides onto the board and two
  clips latch on the PCB. It sits at "the side where cmos battery is", which is the power-connector
  end, opposite the I/O.
- Airflow: the shroud "directs airflow in 3 ways: to the stock heatsink, to the stick on
  heatsinks, and to the backplate". Optional 40 or 50 mm fans mount on the rear of the back half
  as exhaust. One exhaust fan gave about 1 C. The author does not plan a dual 120 version.
- Fins, no cutting: the case "can be used with 0 modifications to the stock heatsink". For best
  results, remove the heatsink from the board, then straighten (open) the fins under the shroud
  with a printed "fin scooper". Mark where the shroud ends and do not open fins past the mark.
  Keep the first and last two fins untouched. Blow out debris. The scooper takes 20 to 30 minutes
  and is preferred to pliers or scissors. The page describes opening, not cutting or removing fins.
- Effect: opened fins plus a stick-on heatsink lowered temperature by up to 10 C. PTM7950 gave
  10 C or more. Undervolting gave 15 C or more.
- Material: PETG for the case parts. "Make sure the glass transition temp is 80C or higher.
  PLA is not recommended."
- Board fixing: the board slides into inner rails by the edges of its aluminium backplate.
- Power: 8-pin PCIe main power. A 12 mm latching button shorts the PSU on.

The 5 difference between the 25 and 30 shrouds shows that the fan top stays at a fixed height.
The shroud is therefore a duct between the heatsink and the fan, and the fan sits on top of it.
Height of fan top above the PCB: about 55.9 + 25 - 28 = 53. ESTIMATED, weak: the 28 is the
assumed part of the shroud that wraps the board and heatsink.

### Must measure on the real unit (the first console is the reference)

1. Outer size of the owned MKUU case.
2. Height from the PCB top face to the fan top face, and to the fan inlet face.
3. Shroud footprint on the board and its distance from the far PCB edge.
4. How far along x' the fins were opened.
5. Exhaust fan size and position.

---

## 5. ARCTIC P12 Pro

Source for all SOURCED rows: ARCTIC spec sheet
https://www.arctic.de/media/f4/9f/31/1750412251/Spec_Sheet_P12_Pro_EN.pdf (SKU ACFAN00305A).
The PST variant (ACFAN00306A) has the same fan data and adds a daisy-chain plug.

| Item | Value | Status |
| --- | --- | --- |
| Frame | 120 x 120 x 25. It is not thicker than a standard fan. | SOURCED |
| Mounting hole spacing | 105 x 105 | SOURCED (dimension drawing) |
| Mounting hole diameter | 4.3 clearance in the mating part. The fan's own holes are about 4.3 to 4.5. | STANDARD practice for 120 mm case fans; not on the spec sheet |
| Weight | 183 g | SOURCED |
| Speed | 600 to 3000 rpm, PWM. 0 rpm below 5 % PWM. | SOURCED |
| Airflow, maximum | 77 cfm, 131 m3/h | SOURCED |
| Static pressure, maximum | 6.9 mmH2O | SOURCED |
| Supply | 12 V DC, 0.33 A, about 4 W. Start-up 3.3 V. | SOURCED (power by calculation) |
| Connector | 4-pin PWM fan plug. Pin 1 ground, 2 +12 V, 3 tachometer, 4 PWM. | SOURCED |
| Cable | 400 | SOURCED |
| Bearing | Fluid dynamic | SOURCED |
| Ambient | 0 to 40 C | SOURCED |
| Included | 4 mounting screws | SOURCED |
| Airflow direction | Air leaves on the side with the motor struts. Check the arrows moulded on the frame. | ESTIMATED: usual axial fan convention; not on the spec sheet |

Note: the elektricM cooling page gives "2100 RPM" for the P12 Pro. The ARCTIC sheet is authoritative.

Keep-out: 12.7 minimum of clear space on the inlet face, 25 or more preferred. A finger guard is
needed on any reachable face. A grill costs about 1 C (Printables 1835961).

### Must measure on the real unit

1. Frame thickness and the corner hole diameter.
2. Arrow direction on the frame.
3. Cable exit corner and usable cable length.
4. Whether it is the PST variant with the extra plug.

---

## 6. ATX power supply (unit not yet identified)

Specification: ATX12V Power Supply Design Guide, version 2.2, section 4.2 and Figures 9 and 10.
Read from https://theswissbay.ch/pdf/Datasheets/ATX12V_PSDG_2_2_public_br2.pdf (pages 32 to 34).

| Item | Value | Status |
| --- | --- | --- |
| Width x height | 150 x 86 | STANDARD (ATX12V PSDG 2.2, Figure 9) |
| Depth | 140 in the specification | STANDARD |
| Depth for an 850 to 1000 W unit | 140 to 180. Use 160 as the nominal parameter and size the bay for 180. | ESTIMATED: typical retail units of this class |
| Mounting thread | 4 x No. 6-32 UNC-2B in the rear face | STANDARD |
| Chassis hole for 6-32 | 4.0 clearance | ESTIMATED: standard clearance for 3.5 mm major diameter |
| Tolerance | X = +/-1, X.X = +/-0.5 | STANDARD (Figure 9 notes) |

Rear face screw pattern. Frame: look at the rear face from outside, with the vented top surface
of the specification upward. Origin at the lower left corner, X to the right, Y up.

| Hole | X | Y | Derived from |
| --- | --- | --- | --- |
| 1 | 6.0 | 80.0 | 6.0 from the left edge; 16.0 + 64.0 |
| 2 | 144.0 | 80.0 | 6.0 + 138.0; 6.0 + 74.0 |
| 3 | 6.0 | 16.0 | 16.0 above the bottom edge |
| 4 | 120.0 | 6.0 | 6.0 + 114.0; 6.0 above the bottom edge |

Status: STANDARD (ATX12V PSDG 2.2, Figure 9: dimensions 6.0, 138.0, 114.0, 64.0, 74.0, 16.0, 6.0).
The pattern is asymmetric, so it fixes the orientation of the unit.

| Item | Value | Status |
| --- | --- | --- |
| Fan | The specification shows an 80 mm rear fan. Modern 850 to 1000 W units use one 120 to 140 mm fan in the 150 x depth face, drawing air in. Exhaust leaves through the perforated rear face. | STANDARD for the rear vent; ESTIMATED for the modern fan layout |
| Mains inlet | IEC 320 (C14) on the rear face. A rocker switch is usually beside it. | STANDARD (section 4.4) for the inlet; ESTIMATED for the switch |
| Cable exit | Through the face opposite the rear face. Reference position in Figure 9: 16 from one side edge, 53 from the top edge. | STANDARD, reference dimensions only |
| Clearance at fan intake and exhaust | Minimum 12.7 (0.5 in): "avoid placing objects within 0.5 inches of the intake or exhaust of the fan itself". | STANDARD (section 4.3 "Airflow / Fan", Venting paragraph) |
| Recommended clearance | 25 to 30 at the fan face, and a free vent at the rear face | ESTIMATED: twice the minimum, for noise |
| Trunk bend at the cable exit | 50 to 60 of free length before the first bend | ESTIMATED: a 30 to 40 trunk of 60 or more wires |
| Mass | 1.5 to 2.5 kg | ESTIMATED |

Stowed cable bundle for a non-modular 850 to 1000 W unit: reserve 2.0 to 2.5 litres.
A practical bay is 150 x 86 x 160 to 200, directly in front of the cable-exit face. That is about
one more PSU volume. ESTIMATED as follows:

| Lead | Count | Length | Section | Volume |
| --- | --- | --- | --- | --- |
| 24-pin ATX | 1 | 600 | 250 mm2 | 150 cm3 |
| EPS 4+4 | 2 | 650 | 95 mm2 | 124 cm3 |
| PCIe 6+2, with pigtail | 2 | 900 | 95 mm2 | 170 cm3 |
| SATA chain | 3 | 850 | 40 mm2 | 102 cm3 |
| Molex chain | 2 | 750 | 35 mm2 | 52 cm3 |
| Total wire | | | | about 600 cm3 |

Folded leads with their connectors pack at 25 to 35 %, which gives 1.7 to 2.4 litres. One PCIe
lead goes to the BC-250 and the 24-pin lead needs room for the bridging plug.

### Must measure on the real unit

1. Make and model. Then take the depth from the data sheet and confirm it.
2. Which face holds the fan, its diameter and its centre. Which way the unit must face in the cabinet.
3. Rear face: inlet, switch and screw positions against the table above.
4. Cable exit position on the front face and the trunk diameter.
5. Number and length of the leads. Fold the bundle and measure the box it fills.
6. Length of the PCIe 6+2 lead that will reach the BC-250.
7. Mass.

---

## 7. Bambu Lab A1

| Item | Value | Status |
| --- | --- | --- |
| Build volume | 256 x 256 x 256 | SOURCED https://bambulab.com/en/a1/tech-specs (search summary) |
| Slicer printable area | 0 to 256 in X and Y, height 256 | SOURCED BambuStudio profile `fdm_bbl_3dp_001_common.json` and `Bambu Lab A1 0.4 nozzle.json` (https://github.com/bambulab/BambuStudio/tree/master/resources/profiles/BBL/machine) |
| Excluded bed area | None for the A1 (`"bed_exclude_area": []`). The A1 profile overrides the exclusion of the shared base profile (a 28 x 28 front-left corner plus an 8 wide left strip). | SOURCED (same profiles) |
| Start-up lines on the plate | The start G-code draws the flow-calibration line along X at Y = 1.0, from about X 108 to 153, when flow calibration is on. A second pass runs at Y = -0.5, off the printable area. | SOURCED BambuStudio `Bambu Lab A1 0.4 nozzle template machine_start_gcode.json` |
| Corner detection zone | X 226 to 256, Y 224 to 256 (`head_wrap_detect_zone`). Not an exclusion. | SOURCED (same profile) |
| Practical usable area | 250 x 250. Keep the front 3 to 5 clear. | ESTIMATED from the start line position |
| Maximum recommended part footprint | 240 x 240, which leaves 5 of brim on each side | ESTIMATED |
| Maximum recommended part height | 245 | ESTIMATED: 256 less margin; less for slender parts |
| Motion | Bed moves in Y ("printer_structure": "i3") | SOURCED (profile) |
| Hot end maximum | 300 C | SOURCED https://wiki.bambulab.com/en/a1/manual/faq (search summary) |
| Bed maximum | 100 C | SOURCED (same) |
| Not recommended materials | ABS, ASA, PC, PA, PA-CF/GF, PET-CF (open frame) | SOURCED (same) |
| PETG bed temperature | 80 on textured PEI and smooth high-temperature plate, 70 on SuperTack | SOURCED BambuStudio `fdm_filament_pet.json` |
| PETG nozzle temperature | 220 to 260 range. 245 for Bambu PETG Basic on the A1, 240 for PETG HF. | SOURCED BambuStudio filament profiles |
| PETG part cooling | Fan 30 to 50 % on the A1 profiles | SOURCED (same) |
| PETG service temperature | Softens at about 70 to 80 C | ESTIMATED: general material data. The MKUU+ page asks for a glass transition of 80 C or more near the BC-250. |

PETG and open-frame risks. ESTIMATED from the machine layout, not from a cited test:

- The bed carries the part in Y. A tall slender part rocks at each reversal. Keep the height to
  footprint ratio below about 4 to 1 in Y, or add a sacrificial brace or a wide brim.
- No enclosure. Long flat parts lift at the corners and tall thin walls can split between layers
  in a draught. Use a brim, rounded corners, and ribs in place of thick solid sections.
- Split cabinet panels at 240 or less in two axes. One axis may reach 250 with care.
- Dry the PETG before printing. Wet filament changes fit (Printables 1835961 gives 4 hours).

### Must measure or test

1. A 240 x 240 single-layer test, to confirm reach and first-layer quality at the plate edges.
2. One tall thin coupon in the planned orientation.
3. Fit coupons: insert boss, 4.3 and 4.0 clearance holes, a sliding joint.
4. A PETG coupon held at the measured exhaust temperature for one hour.

---

## 8. Small parts

| Part | Envelope | Status |
| --- | --- | --- |
| EK ATX bridging plug, 24-pin (EAN 3831109867716) | Body about 54 x 13 x 20 to 25. It adds 12 to 15 to the end of the PSU 24-pin plug. Mated assembly about 55 x 15 x 40. | ESTIMATED: 2 x 12 Mini-Fit Jr housing at 4.2 pitch (12 x 4.2 = 50.4 plus walls and latch). The EK page was INACCESSIBLE (403). Its summary states only "Fits 24 Pin ATX PSU's". |
| Active DisplayPort to HDMI 2.0 adapter (dongle type) | DP plug with latch about 45 x 21 x 13. Tail 150 to 200 long, 5 to 6 diameter. HDMI socket body about 50 x 25 x 14. Overall 200 to 250. | ESTIMATED: typical 4K60 active dongles. No product is chosen. |
| Full-size DP plug at the BC-250 | Needs 45 straight plus bend, in front of the I/O edge | ESTIMATED |
| Mini-HDMI (Type C) plug | Metal shell 10.42 x 2.42. Overmould about 18 to 20 x 9 to 10 x 30 to 40 long, plus strain relief 10. | STANDARD for the shell (HDMI Type C); ESTIMATED for the overmould |
| USB-C plug | Overmould at most 12.35 x 6.5 in section. Length 22 to 35, plus strain relief 10. | STANDARD for the section (USB Type-C Cable and Connector Specification); ESTIMATED for length |
| Bend radius, HDMI cable (5 to 7 diameter) | 30 to 40 minimum | ESTIMATED: 5 to 6 times the cable diameter |
| Bend radius, USB-C cable (3.5 to 4.5 diameter) | 20 to 25 minimum | ESTIMATED: 5 to 6 times the cable diameter |
| Space beside the monitor, straight plugs | 65 to 75 beyond the left edge | ESTIMATED: plug 35 to 45 plus bend 30 |
| Space beside the monitor, right-angle plugs | 15 to 20 beyond the left edge | ESTIMATED |
| 8-pin PCIe plug at the BC-250 | Housing about 18 x 10 x 20, plus bend 30. Reserve 50 to 60 beyond the board edge. | ESTIMATED: 2 x 4 Mini-Fit Jr housing |

The mini-HDMI socket is a weak connector. Clamp the cable to the cradle within 50 of the plug.

### Must measure on the real parts

1. Plug length, including strain relief, of the real mini-HDMI and USB-C cables.
2. The chosen DP to HDMI adapter: both bodies and the tail.
3. The bridging plug mated to the real 24-pin plug.
4. Whether right-angle mini-HDMI and USB-C plugs clear each other. The ports are about 18 apart.

---

## Parameter seeds for the FreeCAD sheet

| Parameter | Value | Status |
| --- | --- | --- |
| `mon_w`, `mon_h`, `mon_t` | 354, 230, 10 | SOURCED |
| `mon_active_w`, `mon_active_h` | 344.678, 215.424 | SOURCED |
| `mon_vesa`, `mon_vesa_thread_depth` | 75, 4 | SOURCED |
| `mon_port_side_clear` | 70 | ESTIMATED |
| `bc_pcb_l`, `bc_pcb_w_io`, `bc_pcb_w_pwr`, `bc_pcb_step_x` | 307.6, 122.2, 144.0, 207.4 | MEASURED-FROM-CAD |
| `bc_stack_h`, `bc_hs_top_above_pcb`, `bc_backplate_below_pcb_top` | 31.65, 26.1, 5.55 | MEASURED-FROM-CAD |
| `bc_cooler_pattern` | 95.75 | MEASURED-FROM-CAD |
| `bc_power_max_w` | 235 | SOURCED |
| `fan_frame`, `fan_t`, `fan_hole_pitch`, `fan_hole_d` | 120, 25, 105, 4.3 | SOURCED, hole diameter STANDARD |
| `psu_w`, `psu_h`, `psu_d`, `psu_d_max` | 150, 86, 160, 180 | STANDARD, depth ESTIMATED |
| `psu_cable_bay_l` | 180 | ESTIMATED |
| `psu_fan_clear_min` | 12.7 | STANDARD |
| `a1_bed`, `a1_part_max_xy`, `a1_part_max_z` | 256, 240, 245 | SOURCED, limits ESTIMATED |
