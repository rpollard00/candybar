# Arcade project current design

**BC250 tabletop candy cabinet for Reese**

Design snapshot updated November 9, 2026

Build a single-player, candy-cab-style tabletop arcade around the spare BC-250, the existing 16-inch UPERFECT monitor, and the spare ATX power supply. The monitor will stay fixed in horizontal 16:10 orientation, with interchangeable control panels for arcade and PC games. Portrait games can run within the horizontal screen at their correct aspect ratio. Physical screen rotation is deferred; an optional printed vertical bezel may be added later without rotating the monitor, accepting a smaller usable image area. A scrolling marquee remains a likely addition, with its hardware and implementation still open.

The next step is a playable bench setup and simple, targeted tests of height, reach and feel, rather than a full-size cardboard cabinet mockup. Establish the fixed screen position, control ergonomics, power-supply packaging and cooling path before committing to the outer shell. FreeCAD is the chosen CAD tool. This is a current design brief and build plan; final dimensions and printable CAD remain to be developed.

## Current configuration

| Area | Current direction |
| --- | --- |
| Computer | Reuse the second BC-250. The first BC-250 console build is the practical cooling and software reference. |
| Display | Reuse the UPERFECT 16-inch portable monitor, 3840 × 2400, fixed horizontally at 16:10. Defer physical rotation. An optional printed vertical bezel may frame portrait content later, with less usable screen area. |
| Controls | One adult player; swappable panels for arcade and PC use. Exact layouts and parts remain open. |
| Power | Reuse the existing non-modular ATX PSU from the Ryzen 9950X / RTX 3080 Ti PC. No new PSU shopping in the current plan. |
| Cooling | Reuse the spare ARCTIC P12 Pro in a removable, ducted BC-250 assembly. Final exhaust arrangement depends on testing. |
| Cabinet | Custom printed candy-cab shell with reinforced structural interfaces and service access. Plywood is optional, not required. |
| Printer and material | Bambu A1. PETG is the current recommended cabinet material; split parts for the 256 mm build volume. |
| CAD | FreeCAD is selected for the parametric design and editable native project. |
| Marquee | Likely scrolling marquee; not yet a specified or purchased subsystem. |

### Status language

Current direction means the latest project plan. Recommended means a proposed implementation that still needs validation. Open means a choice, measurement or test is required before that part of the design is fixed.

## What changed from the first guide

The November 1 guide described a small, mostly new-parts build. The later discussions turn it into a larger salvage-based all-in-one with more capable hardware and a custom modular cabinet.

| Earlier concept | Latest version |
| --- | --- |
| Buy a Raspberry Pi or mini PC. | Reuse the spare BC-250. The Beelink N5095 remains an alternative only for a separate, genuinely miniature classics cabinet. |
| Buy a roughly 9.7 or 10-inch 4:3 display. | Reuse the existing 16-inch UPERFECT. The two spare 24-inch monitors are outside the current baseline. |
| Start with fixed landscape; rotation optional. | Keep the 16:10 screen fixed horizontally. Physical rotation is deferred. Vertical shooters use a portrait-shaped image within the fixed screen; a printed vertical bezel is a possible later addition. |
| A removable conventional arcade deck. | Interchangeable panels for arcade games and PC games; define a common mechanical and electrical interface. |
| Plywood load frame and printed cosmetic panels. | Printed modules with reinforcement, through-bolts and optional metal rails. Wood remains available if useful, but is not a requirement. |
| Printer unknown; several material paths. | Bambu A1 confirmed. PETG recommended; do not carry over ABS/resin settings from reference builds. |
| Possible new Flex PSU and proprietary adapter. | Reuse the spare non-modular ATX PSU. Drop dependence on the sold-out FSP bargain and proprietary breakout board. |
| FreeCAD or code-based CAD as the first route. | FreeCAD is now the confirmed choice, superseding the later Onshape recommendation. |
| Skip an active marquee on version one. | Reopened by the later request for a likely scrolling marquee. Keep it optional until the type and integration are chosen. |
| Roughly 350 mm width and new-parts budgets. | No fixed overall dimensions or current total budget. The larger display and reused hardware invalidate the old assumptions, even without a rotation mechanism. |

### Display specification correction

The concept-image request used “16:9” and “2k” as shorthand. The identified monitor is 3840 × 2400, which is 16:10. The November 8 correction supersedes the earlier 16:9 dimensions. Use the actual monitor body, mounting points and cables for the CAD, not a render or an assumed screen rectangle.

### Keep the useful foundations

Bench testing, real-size ergonomic checks, removable service parts, rigid load paths, test prints and a fully finished paint sample still apply. A full-size cabinet mockup is not required. The original shopping totals and small-screen dimensions do not carry forward.

## Cabinet and fixed horizontal display

### Build the cabinet around removable assemblies

- Display assembly: keep the UPERFECT intact in a supported, fixed horizontal cradle behind the bezel. A VESA-based cradle is the proposed route, subject to the actual hole pattern and mounting limits. Keep the assembly removable for service, without adding a pivot or two-position mount.
- Compute assembly: BC-250 and cooler on a rear-accessible removable tray, below or behind the reclined screen. Give this assembly a direct air path to outside vents.
- Control assembly: rigid, full-size one-player panels with a repeatable attachment interface. Joystick force should not flex painted seams.
- Base and service enclosure: support the ATX supply low in the cabinet, reserve space for its fixed cable bundle, and provide non-slip feet and rear service access.

Use ribs, broad flanges, through-bolts and backing structures where loads require them. Optional metal rails or a rigid subplate are more useful than simply increasing infill. Keep permanent filled seams within cosmetic subassemblies; do not fill joints needed to remove the monitor, controls or computer.

### Fix the screen horizontally for this build

Design the cabinet around one horizontal 16:10 screen position. Physical rotation is deferred, so the current design does not need a rotation sweep, pivot, indexed portrait seat or a cable loop sized for rotation. A removable service assembly is still useful, but it is not a rotating-screen mechanism.

| Geometry | Working information |
| --- | --- |
| Native image | 3840 × 2400, 16:10. If the active diagonal is exactly 16 inches, the image area is approximately 345 × 215 mm. |
| Monitor body | An earlier listing-based estimate was about 355 × 229 × 10 mm. Measure the actual unit before designing the cradle. |
| Fixed-screen fit | Check landscape width against the cabinet sides and the chosen screen height and tilt against the hood/marquee and control deck. Allow for the cradle, bezel, connector bodies, cable bends and service-removal path. |

- Provide positive support and retention in the fixed position. Magnets may locate trim; they should not be the sole support for the monitor.
- Protect mini-HDMI and USB-C connectors with strain relief and enough service slack for safe removal. Preserve access to display controls and power connections.
- Test operating-system output, front end and individual game/emulator settings on the fixed horizontal screen. Portrait content must display upright at its correct aspect ratio without physically rotating the panel.

### Optional printed vertical bezel later

A removable printed bezel with a vertical opening may be added for portrait games. The monitor stays horizontal. Configure the game or emulator to place the full portrait image inside that opening, leaving the unused screen area masked rather than stretching or cropping the game to fill the horizontal display.

- This uses less screen real estate than physically rotating the monitor. The vertical opening and image must fit within the fixed screen's height; final dimensions depend on the games' aspect ratios and the measured active display area.
- Treat the bezel as optional trim, with its attachment and aperture to be designed later. It is not required for the first playable build and does not commit the cabinet to future screen rotation.
- If added, verify image alignment, viewing angle, clearance from the screen surface, access to controls and removal without disturbing the monitor mount.

### Prove the proportions before styling

At the actual table and chair, test height and feel with the real screen and a temporary control panel. A stable adjustable screen stand, securely supported panel, simple spacers and paper control layouts are possible ways to try positions without building a full-size cardboard cabinet. Check wrist support, reach, viewing angle and the likely footprint; use measurements and CAD to work through cable exits and service access, then verify those on the dry assembly. The adult control layout should not shrink to match a miniature reference.

## BC250 cooling and power

### Use the existing build as the reference

The first BC-250 console runs CachyOS in the Printables MKUU/FSP/Apevia/Metalfish case family. Its setup uses an FSP500-30AS Flex supply and a Mosfet.party breakout board, an ARCTIC P12 Pro at the front, and a small Noctua exhaust fan at the rear. The heatsink fins were opened up where the fan/shroud mounts, with thermal putty and phase-change material used during the rebuild.

For the arcade, reuse the spare P12 Pro and the proven mounting/airflow ideas, rather than putting a complete console enclosure inside another enclosure. The separate onemorecap BC-250 shell is also a useful mounting and duct reference; its dimensions should stay tied to the real board.

### Thermal plan

- Create an unobstructed intake, duct through the BC-250 heatsink and a clear exhaust path. Keep hot exhaust away from the monitor and prevent recirculation.
- Treat rear exhaust fans, guards, ducts and vent open area as a test-driven decision. The small Noctua belongs to the first build; a second matching fan is not confirmed in inventory.
- Bench-test the second board before unnecessary disassembly. Inspect temperatures and stability with the planned cooler, then repeat with the cabinet closed.
- Available thermal pads and phase-change material do not automatically replace putty. Match pad thickness and compressibility to measured gaps so they do not lift the heatsink off the GPU die.
- Validate PETG parts under actual sustained heat and load. Avoid placing plastic mounts or cable bundles directly in concentrated hot exhaust.

### Reuse the ATX power supply

The spare non-modular ATX supply previously powered the 9950X/3080 Ti system, so it became the chosen reuse path. Reserve its real dimensions, fan openings, connector access and unused cable bundle in CAD. Keep unused leads intact, insulated and secured; do not cut them off for packaging.

The previously discussed no-solder startup option is a commercial 24-pin ATX bridging plug, with the PSU’s native PCIe 6+2 power lead for the BC-250. Verify the exact board connector and PSU cabling before connection. Do not substitute a CPU/EPS lead or mix modular cables from another supply.

A bridging plug keeps the PSU enabled when mains is on; it does not provide coordinated soft shutdown. Define and test the actual startup and graceful shutdown sequence before choosing the cabinet power controls.

### Electrical integration boundaries

- Keep the ATX PSU in its factory enclosure and use its intended mains inlet. Do not open or modify its internal mains circuitry.
- Power the monitor, audio and any marquee only through documented, correctly rated paths. A shared supply is not assumed, and unrelated supply outputs must not be tied together.
- Provide strain relief, guarded fans, secured wiring and access to disconnect power. Avoid adding DIY mains distribution just to hide external adapters.
- Bench-test the BC-250 display-output chain, including the required DisplayPort-to-HDMI conversion and the monitor’s mini-HDMI connection. Verify audio, cold boot, sleep/wake and motion clarity.

## Controls software audio and marquee

### Swappable controls are part of the current design

The intended uses are arcade games and PC games. Each panel should use the same locating points and retention method, remain rigid during play, and disconnect without pulling on terminals. The exact panel lineup, button count, connector and latch system are still open.

| Panel or function | Starting point and remaining choice |
| --- | --- |
| Arcade panel | One joystick and full-size buttons. Six versus eight action buttons remains a choice driven by the games, not by the small reference cabinet. |
| PC panel | Define what “PC games” need: a gamepad arrangement, keyboard/mouse access or another control layout. No particular implementation has been chosen. |
| Four-way classics | If Pac-Man-style games matter, decide between a switchable restrictor and a dedicated panel. An ordinary eight-way setup is not an equivalent feel. |
| Service controls | Start, coin/select and a recessed menu/exit control remain useful. Prevent accidental destructive hotkey combinations. |
| Connection | USB encoder/harness is the starting architecture. Decide whether every panel has its own encoder or shares a common connection before laying out the interfaces. |

Earlier candidate parts included a Sanwa JLX2-TP-8YT joystick, OBSN-30 screw-in buttons and a GP2040-CE encoder, with Mini-PAC as an alternative. These are candidates, not purchases or locked specifications. Check button nuts/clips, permitted panel thickness, joystick shaft height, terminal depth and connector access with the actual parts.

### Software and game testing

CachyOS is proven on the first BC-250 and is the natural starting reference. The arcade OS, front end, storage and complete game list remain to be finalized. Do not carry over the original generic Batocera recommendation as a tested BC-250 configuration.

- Name a small representative game set, including the most demanding PC game and a vertical shooter. Test it on this board before setting performance expectations.
- Native display resolution is 3840 × 2400; 1920 × 1200 was proposed as a lower rendering resolution. Preserve game aspect ratio rather than stretching the image.
- Test input mapping, menu navigation, panel swapping, landscape games and portrait games on the fixed horizontal display. Keep the game image upright and preserve its aspect ratio. If the optional vertical bezel is added, check that the software viewport fits its opening. Keep a USB keyboard available for recovery and back up the working configuration.
- The BC-250 is PS5-derived, but its enabled configuration and software environment are not equivalent to a complete PS5. Avoid blanket console-performance claims.

### Audio and marquee

No final audio system is selected. Test the monitor’s available audio path or a simple powered speaker setup first, then decide whether dedicated speakers, an amplifier and an accessible volume control are worthwhile. Match voltage, speaker impedance and amplifier wiring to the chosen hardware.

A scrolling marquee is a likely feature, not a settled LCD specification. Choose between a text/LED display and a secondary LCD, define its content and software, and budget its space, heat, power and cabling. A removable top module would allow this to evolve without redesigning the main cabinet. The earlier recommendation to omit an active marquee is no longer a firm project constraint.

## CAD printing and finish

### Learn the parts needed for this project

FreeCAD is the chosen CAD tool for this project. Use its parametric sketches and features to build editable parts, then arrange the measured hardware and cabinet modules in the assembly. The earlier Onshape recommendation is no longer the project direction.

Begin with one control panel: a dimensioned rectangle, thickness, joystick mounting and button holes. Then model the monitor as a measured envelope and establish its fixed horizontal position, viewing angle, mounting and cable clearances. Use sketches, dimensions, extrusions, cuts and assemblies before tackling the rounded outer shell.

- Build a parameter sheet for measured hardware, panel interfaces, clearances, wall thicknesses and printer limits. Distinguish measurements from provisional dimensions.
- An LLM can help with brackets, mounts, ribs, print splits and repetitive parameterized geometry. Keep editable source and review the resulting solids, dimensions and collisions.
- Preserve the native FreeCAD project (.FCStd), STEP interchange models, per-part STL/3MF files, assembly drawings and a fastener list. An STL or STEP alone does not preserve the original parametric history.

### Print for the Bambu A1

PETG is the current recommended material for the printed cabinet and reinforced deck. Split parts to fit the A1’s 256 mm build volume, allowing for orientation, brim and supports. The larger finished assemblies will require multiple pieces.

- Use natural module boundaries: sides, front/control surround, fixed monitor cradle and bezel, hood/marquee, rear cover and internal trays. A future vertical bezel can be a separate removable trim part. Put seams away from high-load palm-rest and joystick areas.
- Prototype ribs, backing flanges, insert bosses and locating features. Use heat-set inserts or captive nuts for service joints and through-bolts where the load warrants them.
- Print small interface tests first: button hole, insert boss, joint pair, monitor corner, panel latch/locator and painted clearance sample. Set final tolerances from these tests.
- The earlier 2.5–3 mm cosmetic skin and 0.16–0.20 mm layer suggestions are only trial starting points. Final walls, ribs and settings need stiffness, heat and slicer validation.

Do not transfer the MGS reference’s ABS recipe or resin grille process directly to the A1. Do not enclose the A1 just to force an ABS/ASA route; the previous recommendation was to stay with an A1-suitable material.

### Finish a joined PETG sample before the cabinet

Your Gunpla finishing experience applies, but a large FDM shell adds flexible panels and seams. Make a 100–150 mm curved, two-piece coupon using the real joint, filament and print orientation. Finish it fully and test adhesion, handling and seam visibility before committing to the paint system.

Dry-fit and stabilize the assembly; level only the necessary ridges; fill small defects with a tested compatible product; prime and guide-coat; sand according to the coating instructions; then apply color, graphics and optional clear. Let each product cure properly. Mask threads and locating surfaces, and never fill a service joint.

Use filler for appearance, not strength. PETG adhesion needs a real sample test. Follow the products’ SDS for ventilation and protection. Avoid solvent smoothing and isocyanate-containing 2K automotive clear as home shortcuts; an ordinary compatible finish is the sensible starting route.

## Inventory and decisions before CAD

### Reuse first

| Available | How it fits |
| --- | --- |
| Second BC-250 | Core computer for this build; confirm storage, connections and condition during bench assembly. |
| UPERFECT 16-inch monitor | Main display; measure body, mounting holes, controls and plugs. |
| Non-modular ATX PSU | Current power-supply choice; measure its case and fixed cable bundle. |
| Spare ARCTIC P12 Pro | Primary cooling-fan candidate for the new BC-250 module. |
| Thermal pads and phase-change material | Available for justified service work; adequate putty for another complete rebuild is not confirmed. |
| Bambu A1 and existing tools | Printing, woodworking and Gunpla finishing experience support the build; buy only missing tools and consumables. |

### Measure or decide before freezing the design

| Item | Required information |
| --- | --- |
| Screen assembly | Actual outer dimensions, VESA pattern/fastener limits, weight, connector bodies and cable bends; fixed horizontal position and tilt; secure retention and service-removal path. A future vertical bezel remains optional. |
| Cabinet geometry | Table/chair height, viewing angle, wrist support, footprint, carrying points, stability and service-removal path. |
| Compute and power | Board/heatsink/shroud envelope and holes; PSU dimensions and connector check; airflow direction, cable-bundle space and startup/shutdown behavior. |
| Control panels | Desired games; six/eight-button choice; PC layout; joystick/button models; common mechanical interface and wiring/encoder approach. |
| Software and storage | OS/front end, storage device/capacity, representative games, aspect-ratio and viewport settings for portrait content on the horizontal screen, and backup method. |
| Audio and marquee | Speaker/amplifier/volume path; whether the marquee is text/LED or LCD; its dimensions, power and control software. |
| Appearance and budget | Final proportions, color/graphics and finish system; current budget based on missing parts and actual slicer estimates. |

### Purchase only after the relevant fit test

Likely remaining categories are controls and encoder/harnesses, display adapters/cables, an ATX bridging plug or another verified startup solution, fixed monitor-mounting hardware, fasteners/inserts, feet/grommets/strain relief, filament and tested finishing supplies. Add audio and marquee parts only after those choices are made.

No current total is fixed. Do not reuse the original Pi/mini-PC budget or its 350 mm shell material allowances: the computer, display, PSU, cabinet scale and print strategy have all changed. Price the missing parts and use slicer mass/time once CAD exists.

## Build checklist and acceptance tests

### 1  Make the electronics playable

- Lay out the actual BC-250, P12 Pro, PSU and monitor on the bench. Verify safe, documented power connections and the complete video chain.
- Test cold boot, graceful shutdown, display wake, sound, and representative landscape and portrait games on the fixed horizontal monitor. Check demanding-game performance at chosen render settings.
- Test the intended arcade controls on a temporary panel. Identify any missing analog controls, four-way needs or menu/recovery problems.

### 2  Test height feel and packaging

- Use the real screen and a securely supported temporary control panel at the intended table and chair. Play for 20–30 minutes, adjusting screen height, wrist support, deck reach and screen angle. Use simple supports and layout checks instead of a full-size cabinet mockup.
- Check the fixed horizontal screen position and cable routing, including clearance beneath the proposed hood. Confirm the service-removal path without requiring screen rotation. If trying a vertical bezel opening, test its smaller image area in software before printing the trim.
- Lay out and measure the PSU and its unused leads, the compute air path and service access. Check the proposed footprint and weight distribution, then confirm during dry assembly that the cabinet will not tip or slide under normal vigorous play.

### 3  Build the FreeCAD model and small test parts

- In FreeCAD, model measured hardware envelopes first, interfaces second and outer styling third. Define the common panel attachment and electrical connection.
- Print fit, insert, joint, monitor-support and finish coupons. Check that critical parts fit within the A1’s usable build area.
- Test changing a key FreeCAD parameter. Verify walls, fastener lengths, tool access, cable bends and collision-free removal of service parts.

### 4  Dry assemble before paint

- Print and assemble the unfinished cabinet with all hardware installed. Do not force the monitor, pinch cables or let screw tips approach glass or boards.
- Remove and refit the screen, computer tray, rear cover and control panels repeatedly. Resolve flex, rattles and awkward service access.
- Run the hardest intended workload with the covers installed. Verify temperatures, stable performance, noise and lack of plastic distortion.

### 5  Finish and document the working build

- Remove electronics and glass before sanding or painting. Fill only permanent seams and apply the coupon-proven finish.
- Allow full cure, then reassemble. Label the wiring, photograph the finished internals and save the software configuration and CAD source.
- Record final dimensions, actual part numbers, fasteners, print settings and costs so the finished machine can be serviced or reprinted.

### Acceptance gate

The cabinet is complete when it repeatedly boots and shuts down cleanly; runs the chosen games with the covers on; stays stable and comfortable; securely holds the screen horizontally without cable strain and displays the chosen landscape and portrait games correctly; allows practical panel swaps and service access; and has reliable audio and controls. If a marquee is added, include it in the power, thermal and startup tests. If a vertical bezel is added, check image fit and alignment on the unchanged horizontal screen, along with safe trim removal.

## Design history and reference links

Project history: November 1 established the single-player candy-cab idea and first build guide. November 2 selected the salvage hardware, Bambu A1, PETG direction, P12 Pro cooling and ATX reuse. November 3 added the Robert Dunn / MGS construction references. November 4 added the explicit swappable-panel, rotatable-screen and likely scrolling-marquee concept. November 8 added the CAD recommendation and corrected the monitor to 16:10. The November 9 update selects FreeCAD, replaces the planned full-size cardboard mockup with targeted height/feel tests, and defers physical rotation in favor of a fixed horizontal screen. An optional printed vertical bezel remains a later possibility, using a smaller portrait image on that same horizontal screen.

The November 1 Tabletop Candy Cabinet Build Guide remains an earlier planning reference. Its smaller display, plywood baseline, new-compute shopping and budget totals are superseded by this version. Fixed landscape is again the current direction for the larger 16:10 monitor; the intervening rotation requirement has been deferred.

### Project and cabinet references

[November 4 concept discussion](https://chatgpt.com/c/6aeaa079-3dd0-83e8-a56b-885da328e4b9?messageId=4c9116fb-6d38-463d-9404-995957d87e7f)

[Original Reddit build inspiration](https://www.reddit.com/r/cade/comments/1xl7lxk/my_latest_two_builds_i_designed_in_cad_3d_printed/)

[Robert Dunn / multigamesystem GitHub profile](https://github.com/multigamesystem)

[MGS MVS U4 bartop files and assembly references](https://github.com/multigamesystem/MGS004NSM-MVS-U4-Bartop-Arcade)

[MGS component CAD library](https://github.com/multigamesystem/MGS-CAD-Files)

[MGS project license](https://github.com/multigamesystem/MGS004NSM-MVS-U4-Bartop-Arcade/blob/main/LICENSE)

Use MGS as a construction reference, not a cabinet to scale uniformly. The discussed MVS-U4 design uses an 8-inch 4:3 display and compact four-button Neo Geo controls. Its modular parts, acrylic layers, inserts and component models are useful; its dimensions and print recipes do not define this build. File reuse requires checking and following its noncommercial and attribution terms.

[Mini New Astro City 9 point 7 inch reference](https://makerworld.com/en/models/700005-mini-new-astro-city-arcade-machine#profileId-629340)

[Mute City larger printed Astro style adaptation](https://www.hangedmandesign.com/mute-city-arcade/)

### Hardware and learning references

[Existing UPERFECT monitor listing](https://www.amazon.com/dp/B0F99H1KSL)

[Existing BC250 case family](https://www.printables.com/model/1835961-bc250-case-mkuu-fsp-apevia-metalfish-psu)

[Alternative BC250 cooling shell with STEP STL and 3MF](https://github.com/onemorecap/bc-250-shell-case)

[Commercial 24 pin ATX bridging plug example](https://www.ekwb.com/shop/ek-atx-bridging-plug-24-pin)

[Historical reference only: Onshape CAD Basics course](https://learn.onshape.com/learn/learning-path/introduction-to-cad)

[Historical reference only: Onshape plan details and public design caveat](https://www.onshape.com/en/pricing)

[FreeCAD features](https://www.freecad.org/features)

Reference links are for design context and the previously discussed products, not a current stock or checkout list. Measure owned hardware and check the exact product documentation before committing mounting, wiring or purchases.
