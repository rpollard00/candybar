# Hardware list

Date: 2026-11-14. Each source was read on this date unless the text gives a different date.

This is the list of all that is bought and not printed. Part 1 is the list, one table for each
subsystem, with the same columns in each table. Part 2 is the research for the items that the design
does not fix yet, as options with a recommendation. The owner decides looks, hardware and money.

Nothing was bought or tested for this list. Measure each real part before a printed part that touches
it is made.

## How to read the list

| Column | Meaning |
| --- | --- |
| Item | What it is. "Owned" means that the owner has the part. |
| Size or standard | The size, the thread or the standard that the design uses. |
| Qty | The quantity, as far as the design fixes it. "about" is an estimate. Its method is in the notes under the table. |
| Why this kind | The reason, with the place in the repository that fixes it. |
| Alternatives | Other kinds that can do the same work. |
| Open | What is not decided or not confirmed. |

Where the design fixes a value, the source is a file of this repository:

| Short name | File |
| --- | --- |
| joints | `cad/candybar/shell/joints.py` (the one source of the joint values) and decision record 0006 |
| split report | `cad/out/shell-rev7/split/report.md` (a build output) |
| fit report | `cad/out/shell-rev7/fit/report.md` (a build output) and `cad/candybar/shell/fit.py` |
| params | `cad/params/hardware.csv`, `cad/params/controls.csv` |
| envelopes | `docs/research/hardware-envelopes.md` |
| cooling | `docs/research/bc250-cooling-and-psu.md` |
| controls | `docs/research/controls-ergonomics.md` |
| panel and USB | `docs/research/pc-panel-and-front-usb.md` |
| finishing | `docs/research/petg-finishing.md` |
| power button | `docs/research/bc250-power-button.md` |

A price is in the list only where a source gave it. The source and the date are in section 2.10.

---

## Part 1. The list

### 1.1 Compute and power

| Item | Size or standard | Qty | Why this kind | Alternatives | Open |
| --- | --- | --- | --- | --- | --- |
| ASRock BC-250, with its heatsink and backplate (owned) | Board 307.6 mm x 144.0 mm. 12 V on an 8-pin PCIe connector (`J1000`). | 1 | The brief. Decision records 0004 and 0005. | None | The heatsink variant. The board dimensions are from a community model (envelopes, section 2). |
| Fan, ARCTIC P12 Pro (owned) | 120 mm x 120 mm x 25 mm, holes on 105 mm, 4-pin PWM, cable 400 mm | 1 | Settled by the owner. Use the standard type, not the low-noise type (cooling, A6). | P12 Pro PST (the same fan with one more plug) | None |
| Fan screws | With the fan | 4 | In the fan's box (envelopes, section 5) | M4 screws into inserts in the shroud | How the fan is held on the printed shroud |
| Power supply, EVGA SuperNOVA 1000 P5 (owned) | ATX, 150 mm x 86 mm x 150 mm, fully modular | 1 | Settled by the owner | None | The weight of the bare unit. The positions on its rear face (cooling, Part B). |
| Supply leads (owned, in the supply's box) | 24-pin lead (600 mm). One single PCIe 6+2 lead (700 mm). One SATA lead. | 1 each | Only these three leads are fitted (cooling, Part B) | None | The wire size of the PCIe lead: the board needs 16 AWG (cooling, Part B). |
| Supply screws (in the supply's box) | No. 6-32 UNC | 4 | They locate the supply on the rear wall. No weight hangs on them (split report, "Mounts"). | None | None |
| Mains lead (in the supply's box) | IEC C13 plug, 1500 mm | 1 | The supply has its own C14 inlet. No mains wiring is in the shell (roadmap, "Mains entry"). | A lead with a right-angle C13 plug (section 2.9) | The lead type |
| Rubber pads under the supply | Adhesive pads, about 3 mm | 4 | The supply "stands on rubber pads in a printed saddle" (split report, "Mounts") | A strip of foam rubber | Size and material |
| Straps over the supply | Hook-and-loop strap or a printed strap | 2 | Split report, "Mounts" | Two printed clamps with screws | The kind of strap |
| Everyday power button and its adapter | A button of 16 mm. An adapter board on `PS_ON`, or a latching switch. | 1 | Power button note, section 8 | The three ways of that note | The way, the place, the button |
| Storage | M.2 2280 drive, SATA or NVMe (the socket has two lanes of PCIe 2.0) | 1 | The board has one M.2 socket (envelopes, section 2) | None | The drive and its size. The brief leaves the storage open. |
| Thermal material | Thermal pads or putty, phase-change sheet | As necessary | The brief: "Match pad thickness and compressibility to measured gaps" | None | Only if the heatsink comes off |
| Foam seal, fan to rear door | Closed-cell foam ring, 116 mm inside, 140 mm outside, compressed to the 5 mm gap | 1 | The fan must take outside air only (cooling, A6 and A7) | A printed lip with a soft gasket strip | The foam type and its thickness before compression |
| Foam seal, shroud and exhaust duct | Closed-cell foam strip, 3 mm | About 1 m | Cooling, A6 | Felt strip | Lengths, after the shroud and the duct are designed |
| Duct fan (optional) | 92 mm, on four screws | 0 or 1 | The owner wants to examine a fan in the exhaust duct (roadmap) | No fan | If it is necessary: a thermal test decides |

### 1.2 Display

| Item | Size or standard | Qty | Why this kind | Alternatives | Open |
| --- | --- | --- | --- | --- | --- |
| Monitor, UPERFECT 16 inch 3840 x 2400 (owned) | Body 354 mm x 230 mm x 10 mm (the maker's values) | 1 | The brief. The mount takes any 16 inch 16:10 portable monitor (roadmap). | Each unit of the survey in envelopes, section 1 | The measured body size |
| Video adapter | Active DisplayPort to HDMI 2.0 adapter | 1 | The board has DisplayPort only. The monitor has mini-HDMI. | A DisplayPort to mini-HDMI cable, if an active one exists | The product. Its two bodies and its tail (envelopes, section 8). |
| Video cable | HDMI (type A) to mini-HDMI (type C), a right-angle plug at each end | 1 | Way 1 (the owner, 2026-11-15): the adapter is in the board's socket, in the duct, and its HDMI plug leaves through the end wall of the duct; straight plugs do not fit beside the monitor (fit report) | A right-angle adapter on a straight cable | **At the adapter (full-size HDMI):** with the plug in the adapter, the lead leaves along the short axis of the adapter's HDMI socket, toward the front of the cabinet. Which of the two short-axis turns that is depends on how the adapter's socket sits: hold the adapter in the board's socket and look before buying. The plug body: at most 23 along the socket's long axis and 13.5 along its short axis (the opening of the end wall is 25 x 14.5), and at most 24 long out of the adapter (30.9 from the adapter's face to the side wall, less the lead). **At the monitor (mini-HDMI):** with the plug in the socket, the lead leaves parallel to the left edge, toward the bottom edge of the monitor (the plug turns along the long axis of the socket: long axis along the edge, narrow face to the glass); the plug stands out 22 or less. Sellers' names for the angles differ: choose by a picture. **Length 0.5 m:** the route is about 205 (the adapter to the left cable channel along the side wall, then in the channel to the socket) and the monitor needs 100 of slack to come forward; the rest lies in the channel. The bend radius of an HDMI lead of 6 is about 30 (ESTIMATED: five times its diameter, a common rule for copper leads, not from a data sheet); the lead turns in its plugs, and its own bends are in the open room beside the duct. |
| Power cable of the monitor | USB-C, right-angle plug at the monitor | 1 | Fit report | None | Where the monitor gets its power. See section 2.11, question 5. |
| Cable clamp at the monitor | A printed clamp or a P-clip within 50 mm of the mini-HDMI plug | 1 | "The mini-HDMI socket is a weak connector" (envelopes, section 8) | None | A part of the monitor cradle (roadmap step 13) |
| Screws for the monitor cradle | M4 into heat-set inserts in the middle pieces | 4 | The cradle is "screwed at four corners to the inner flanges of the two middle pieces" (split report) | Thread-forming screws | The cradle is not designed |

### 1.3 Controls: the arcade control panel

| Item | Size or standard | Qty | Why this kind | Alternatives | Open |
| --- | --- | --- | --- | --- | --- |
| Lever | Sanwa JLX2-TP-8YT, flat plate 53 mm x 95 mm, slots on 40 mm x 85 mm | 1 | Controls, section 1. Params. | Sanwa JLF with the same plate | Not bought. The values are from drawings. |
| Ball top | Sanwa LB-35, 35 mm, M6 | 1 | The lever comes with no ball top (controls, 1.1) | Each M6 ball top or bat top | None |
| Lever harness | Sanwa JLF-H, 5 pins | 1 | The lever comes with no harness (controls, 1.1) | None | None |
| Lever fixings | M4, four positions | 4 | Printed plate: M4 heat-set inserts (params: hole 5.6 mm). Cut plate: press-in studs, or countersunk screws (panel and USB, B4). | See B4 of that note | The plate stack |
| Action buttons | Sanwa 30 mm: OBSF-30 (snap-in) or OBSN-30 (screw-in) | 8 | Eight buttons are settled. Snap-in buttons need a panel of 3.9 mm or less. | Seimitsu nuts on OBSN-30 | Snap-in or screw-in (roadmap, "Button nuts") |
| Start, coin and menu buttons | Sanwa 24 mm: OBSF-24 or OBSN-24 | 3 | Controls, 2.3 | None | Where they are, if the apron carries them (roadmap) |
| Encoder | RP2040 Advanced Breakout Board (GP2040-CE), 96.3 mm x 45.3 mm, holes for M3 | 1 for each panel | "one encoder per panel, one USB cable" (controls, 4.2) | Brook board, Raspberry Pi Pico, Ultimarc Mini-PAC | The owner must confirm one encoder for each panel (roadmap) |
| Encoder screws and inserts | M3 heat-set inserts, M3 x 6 screws | 4 for each panel | The board holes are 3.6 mm (controls, 4.1) | Printed posts with thread-forming screws | None |
| Button wires | Wires with 2.8 mm (#110) female terminals, and a ground chain | 11 signal wires and the ground chain for each panel | The Sanwa terminals are 2.8 mm tabs (controls, 2.1) | A bought 20-pin harness for the encoder | None |
| USB cable, panel to cabinet | USB-C or USB-B to USB-A, with a loop of 200 mm | 1 for each panel | Split report, "Cable routes" | A panel-mount socket on each panel | The connector on the encoder |
| Top plate | 5052-H32 aluminium, 2.03 mm, cut by a service | 1 | Panel and USB, B3 and B4 | 3.18 mm aluminium with no cover. A printed plate (ABS) comes first (roadmap). | The plate stack (roadmap, "The arcade plate stack") |
| Clear cover | Polycarbonate or acrylic, 1.5 mm, cut from the same drawing | 1 | The owner wants a cover with art under it | None | Confirm 2.0 + 1.5 mm with snap-in buttons |
| What holds the panel | The push bolt (`docs/design/control-panel-latch.md`): two rear hooks and a strike on each panel, a printed bolt, one spring, and four magnets in the frame | See the next rows | The owner's choice, 2026-11-15 | Four M4 x 16 countersunk screws into M4 inserts (the fall-back) | The size of the front magnets after the first print (the force to lift the panel out) |
| Latch magnets | Disc magnet N52, 12 x 2, axial | 4 (in the frame, once) | `panel_frame.PushBolt`: one in each pad | Steel discs in the frame and magnets in the panel | The pull, ESTIMATED 14.1 N for each latch point |
| Latch steel discs | Steel disc 12 x 2 | 4 for each panel | The user, 2026-11-16: no pole to mind, about 10 % less pull than a magnet | A magnet of 12 x 2 | None |
| Spring of the push bolt | Compression spring, steel, 4 outside, 22 free, about 1.2 N/mm | 1 | `PushBolt.bolt_spring_*` | None | The maker's part |
| Epoxy for the magnets and discs | Two-part epoxy | A little | A pocket that holds the disc by its rim, and epoxy | Cyanoacrylate | None |

### 1.4 Controls: the PC control panel

| Item | Size or standard | Qty | Why this kind | Alternatives | Open |
| --- | --- | --- | --- | --- | --- |
| Keyboard PCB | 60 %, GH60 form, hot-swap, USB-C, 285 mm x 94.6 mm | 1 | Panel and USB, B2 | Hand wiring | Bought PCB or hand wiring (roadmap, "The keyboard") |
| Switches, keycaps, stabilisers | MX type, for the layout of the PCB | 61 switches for an ANSI 60 % layout | The owner builds the keyboard | None | The layout. PCB-mount or plate-mount stabilisers. |
| Switch plate | 5052-H32 aluminium, 1.60 mm, cut by a service | 1 | Panel and USB, B1 and B3 | A plate for the full panel | Small plate or full plate |
| PCB screws and inserts | M2 screws into M2 heat-set inserts in printed posts | 4 to 6 | The tray mount of panel and USB, B2 | Plate mount with no screws | None |
| Pointing device | Not chosen | 0 or 1 | Panel and USB, B5 | A touchpad, a trackball | If one is wanted |
| Small hub in the panel | USB 2.0, two ports | 0 or 1 | Only with a pointing device, so that the panel keeps one cable | None | Follows the line above |

### 1.5 Front USB

| Item | Size or standard | Qty | Why this kind | Alternatives | Open |
| --- | --- | --- | --- | --- | --- |
| USB-A panel socket on a cable | Screw flange, holes 30.0 mm apart, cut-out 14.7 mm x 7.3 mm (example: DataPro 1698) | 2 | Panel and USB, A4 and A5. Params. | Snap-in sockets, keystone modules, a bare hub board | USB 2 or USB 3 (roadmap) |
| USB-C panel socket on a cable | Screw flange, holes 20.0 mm apart, cut-out 10.5 mm x 4.6 mm, male to female (example: DataPro 1678) | 2 | The same | The same | The same. Do a test of the two plug directions. |
| Flange screws | No. 4-40 | 8 | The sockets have nuts in their flanges | M3 with the sockets of a second vendor | The heads show on the socket plate |
| Hub | Powered, with two USB-C and two USB-A ports for the sockets, and its own DC input | 1 | The 5 V of the board is weak (panel and USB, A1 and A3) | A seven-port hub | The model. 5 V or 12 V input. The params have an estimate of 110 mm x 45 mm x 20 mm. |
| Hub power cable | SATA 15-pin to a DC barrel plug, in the 5 V version | 1 | The supply's 5 V rail, with no mains adapter | A Molex lead and a terminal block | The barrel size of the hub |
| Hub to board cable | USB-A to the hub's input, about 600 mm | 1 | One cable from the compute module to the deck | None | The length |
| Screws of the socket plate | M4 into heat-set inserts round the opening (joint 5) | About 4 | "Screwed from inside into a frame of inserts" (split report) | M3 | The count |

### 1.6 Audio

| Item | Size or standard | Qty | Why this kind | Alternatives | Open |
| --- | --- | --- | --- | --- | --- |
| Speaker | Tectonic TEBM35C10-4, square frame 51.8 mm, in a sealed enclosure of 0.45 l (band A, docs/design/hood-band.md). The room behind each pod takes a round frame of 53.9 mm and 109 mm of depth (fit report). | 2 | The audio research of 2026-11-14 | Visaton FRS 5 X (frame 50: it needs its own seat pocket) | The driver's body is an envelope, not checked against a data sheet |
| Grille screws and inserts | M3 button head (ISO 7380) into M3 heat-set inserts in the driver seat; the grille clamps the driver's frame | 2 for each grille | Band A: the driver and the grille come out to the front | A snap fit | The length of the screw |
| Amplifier | Stereo class D board, on the 5 V or the 12 V of the supply | 1 | See 2.5 | The speakers of the monitor (2 x 1 W), with no amplifier | The board. The volume control. |
| Audio source | The 3.5 mm output of the monitor, or a USB audio adapter | 1 | The board has no analogue audio output (envelopes, section 2: port list) | Audio over HDMI to the monitor only | A bench test of the monitor's output |
| Plug at the foot of the hood | One multi-pin connector for the speakers and the marquee light, with about 200 mm of slack on the hood's side: the hood lifts and tips back, then the plug comes apart (the bolted hood, 2026-11-16) | 1 pair | "The hood lifts off: one multi-pin plug at the hood's foot" (split report) | Two small connectors | The pin count: 4 for the speakers, and the marquee's wires |

### 1.7 Marquee

| Item | Size or standard | Qty | Why this kind | Alternatives | Open |
| --- | --- | --- | --- | --- | --- |
| Light source | Not chosen. The window is 352 mm x 34 mm. The room behind the cover is 82 mm deep, and the params keep 25 mm for the modules. | - | Roadmap: no hardware is chosen | A lit marquee (a strip and a diffuser), or a scrolling one (LED matrix modules). See 2.6. | Lit or scrolling |
| Cover | A printed or cut plate in the window | 1 | The hood band has a provisional opening | Opal acrylic, 3 mm | Follows the line above |
| Controller | For a scrolling marquee: a small controller on USB | 0 or 1 | Panel and USB, A3, keeps a board port for it | None | Follows the line above |

### 1.8 The shell: bonded seams

The values are those of joints. The quantities are estimates: the flanges are not modelled yet.

| Item | Size or standard | Qty | Why this kind | Alternatives | Open |
| --- | --- | --- | --- | --- | --- |
| Screws for joint 1 (skin to skin) | Thread-forming screw for plastics, 3.0 mm x 16 mm, pan head, 30 degree thread (EJOT PT type) | About 80 | They hold the dry assembly, clamp the bond and stay in. Pitch 60 mm. | A screw for plastics of the same size from a different maker. Not a sheet metal screw. | The pilot hole: 2.25 mm or 2.4 mm. The coupon decides. |
| Screws for joint 4 (node plates) | Thread-forming, 3.0 mm | About 30 | One screw into each of the three pieces at a node | None | The length. The count of nodes (about 10). |
| Screws for joint 2 (floor tile to tile) | Thread-forming, 3.5 mm x 12 mm, from below | About 40 | Pitch 50 mm in the half-laps | None | None |
| Screws for joint 3 (wall foot to floor) | Thread-forming, 3.5 mm x 16 mm, up from below | About 25 | Pitch 80 mm | None | None |
| Screws for the coupons | 3.0 mm x 16 mm | 50 | The coupon README: "Buy 50" | None | None |
| Weld, filler, primer, paint | ABS: a solvent cement or ABS dissolved in acetone for the seams, ABS slurry or a putty that names ABS in the groove (`docs/research/abs-on-the-q2.md`, section 4) | See that note | The weld coupon (plate 5) and the finish coupons (plates 8 and 9) prove them | The methacrylate adhesive of the PETG plan, as the control | The coupons decide |

Method of the estimates: the seen length of the bonded seams in the split report is 4.3 m. With the
hidden part of seam D1 the total is about 4.7 m. At a pitch of 60 mm this gives about 80 screws. The
laps of the nine floor tiles are about 2.0 m (two lines of 480 mm and two of 528 mm). The outline of the
floor is about 2.0 m. ESTIMATED from the print boxes of the tiles.

### 1.9 The shell: service seams and what comes off

| Item | Size or standard | Qty | Why this kind | Alternatives | Open |
| --- | --- | --- | --- | --- | --- |
| Heat-set insert, M4 | Brass, M4 x 8.1 mm, outside 6.3 mm, hole 5.6 mm | About 30 to 40 | Joint 5: "M4 heat-set insert in the fixed part". The values agree with two makers' tables (section 2.1). | M4 square nuts in pockets | The hole as printed, and its depth (section 2.1) |
| Heat-set insert, M3 | Brass, M3 x 5.7 mm, outside 4.6 mm, hole 4.0 mm | About 20 to 30 | The encoder, the speakers, small covers | Thread-forming screws | None |
| Heat-set insert, M2 | Brass, M2 x 4.0 mm, outside 3.6 mm, hole 3.2 mm | 4 to 6 | The keyboard PCB posts | None | Only with a bought PCB |
| Machine screws, M4 | Button head or pan head, 10 mm to 16 mm; for the hood 4 socket head M4 x 20 (ISO 4762, a 3 mm hex key) | About 30 | For the M4 inserts | None | The lengths, when the parts are modelled |
| Locating pins | Steel dowel pin, 4 mm, in holes with 0.1 mm of clearance | About 16 | Joint 5: "two pins 4 dia, +0.1" for each service part | Printed pins | The length. Steel or printed. |
| Rear door: what holds it | The plan: four thumb screws, two pins and a lip on the sill | 4 thumb screws | Blueprint, "What opens for service" | See 2.3 and 2.4 | The owner's choice |
| Bezel plate: what holds it | The plan: magnets and two pins. The plate rests on the ledge below it. | See 2.3 | Split report: "held by magnets and two pins (trim: no load)" | See 2.3 | The magnet size and count |
| Hood: what holds it | Four cones of the top ring locate it; four M4 x 20 socket head screws (ISO 4762) from below, up through bosses of the ring into M4 heat-set inserts in the hood's foot. A 3 mm hex key, from inside the body with the rear door off. | 4 screws, 4 inserts | The owner, 2026-11-16: "for the hood - we can bolt it on" (`docs/design/print-pieces.md`, "The bolted hood") | A bonded hood | None |
| Control panel: what holds it | The push bolt (section 1.3) | - | The owner, 2026-11-15 | Screws (the fall-back) | None |

Method of the insert estimate: the rear door (4), the hood (4), the USB socket plate (4), the control
panel (2 to 4 for each cabinet), the lever on a printed plate (4), the monitor cradle (4), the saddle of
the supply (4), the BC-250 carrier (4 to 6), the duct fan (4). ESTIMATED: these parts are not designed.

### 1.10 Under the floor

| Item | Size or standard | Qty | Why this kind | Alternatives | Open |
| --- | --- | --- | --- | --- | --- |
| Non-slip pads | Adhesive pads, 2 mm to 3 mm thick | About 9 to 12 | Settled by the owner: the floor stands on the table on thin non-slip pads. No feet of 18 mm. | See 2.8 | The kind, the size and the places |

### 1.11 Cables and small parts

| Item | Size or standard | Qty | Why this kind | Alternatives | Open |
| --- | --- | --- | --- | --- | --- |
| Cable tie mounts and ties | Adhesive or screwed mounts, reusable ties | As necessary | The brief: "strain relief, guarded fans, secured wiring" | Printed clips on the flanges | Places, after the carriers are designed |
| Wire for the button, the LED and the speakers | 0.25 mm2 to 0.5 mm2 stranded wire | A few metres | Low current | None | None |
| Small connectors | 2-pin and 4-pin connectors that lock | A few | For each part that comes out: the compute module, the hood, the socket plate | None | The type |
| Filament | ABS, 1.75 mm (decision record 0008) | See `docs/design/print-plan-abs.md` and the coupons (`docs/design/coupons.md`) | The owner chose ABS on a Qidi Q2 (2026-11-14) | PolyLite ABS (1.12 g/cm3) | Which ABS filament; the coupons are printed with it |

---

## Part 2. Research for what is not fixed

### 2.1 Heat-set inserts in printed PETG (the cabinet is now ABS: `docs/research/abs-on-the-q2.md` gives the iron at 265 C, the hole depth of 9.5 and the boss of 13)

Sizes from two makers of inserts for 3D prints (CNC Kitchen and ruthex), as a retailer shows them [H1][H2]:

| Thread | Length | Outside diameter | Hole diameter | Smallest wall round the hole | Status |
| --- | --- | --- | --- | --- | --- |
| M2 | 4.0 mm | 3.6 mm | 3.2 mm | 1.3 mm | SOURCED [H2] |
| M3 (standard) | 5.7 mm | 4.6 mm | 4.0 mm | 1.6 mm | SOURCED [H1][H2] |
| M4 (standard) | 8.1 mm | 6.3 mm | 5.6 mm | 2.1 mm | SOURCED [H1][H2] |
| M5 (standard) | 9.5 mm | 7.1 mm | 6.4 mm | 2.6 mm | SOURCED [H2] |

Rules from the makers:

| Rule | Value | Source |
| --- | --- | --- |
| Hole shape | Straight, not tapered. No chamfer at the edge. | CNC Kitchen [H3] |
| Hole depth | The insert length and about 1 mm (CNC Kitchen). The insert length and two thread pitches (SPIROL). For M4 x 8.1 mm this is 9.1 mm to 9.5 mm. | [H3][H5] |
| A printed hole comes out small | Printed holes were about 0.25 mm smaller than the model in the maker's test. The maker suggests 0.2 mm to 0.3 mm more in the model, and 4.2 mm for M3. The test was in PLA only. | CNC Kitchen [H4] |
| Hole too large or too small | "Larger holes decrease performance, while smaller holes induce undesirable stresses and potential cracks in the plastic." | SPIROL [H5] |
| Wall round the insert | The maker's smallest wall is in the table. SPIROL gives a boss of two to three times the insert diameter as the optimum. | [H1][H5] |
| Depth of the insert | Flush with the surface, 0.13 mm above it at most | SPIROL [H5] |
| Iron temperature for PETG | 245 C: 10 C to 20 C more than the print temperature | CNC Kitchen [H3] |
| The screw must not reach the bottom of the hole | It pushes the insert out | SPIROL [H5] |

What this means for the design:

1. `joints.py` has the M4 insert with a hole of 5.6 mm. This is the nominal value of the makers. A
   printed hole of 5.6 mm in the model can come out near 5.35 mm. Put holes of 5.6 mm, 5.7 mm and 5.8 mm
   on the insert coupon, and choose the one that seats the insert with a small resistance.
2. The blueprint gives the hole as "8 deep". The insert is 8.1 mm long. Make the hole 9.5 mm deep.
3. `joints.py` has a boss of 12 mm for the service seams. The maker's smallest wall gives 10.5 mm
   (6.3 mm and two walls of 2.1 mm). The SPIROL optimum starts at 12.6 mm. A boss of 13 mm is inside
   the two rules.
4. No maker's table names PETG. The pull-out test was in PLA. The insert coupon of the brief must
   prove the hold in PETG.

### 2.2 Screws into printed PETG (for ABS the pilot hole of 2.4, 0.8 d, is the first candidate)

The joints use thread-forming screws for plastics with a 30 degree thread. `joints.py` gives the
source of the pilot holes: an EJOT distributor table, with 0.75 d for PET and 0.8 d for ABS. PETG is
not in that table. The coupon compares the two holes in a repeated-drive test (the coupon README).
This list adds no new value.

Use a machine screw in a heat-set insert where a part comes off often. A thread that the screw forms
in the plastic wears each time. The coupon README needs only two or three drives for a bonded seam.

### 2.3 What holds a service part that comes off often

Facts:

| Kind | Fact | Status |
| --- | --- | --- |
| Disc magnet, 8 mm x 3 mm, N45 | Pull about 1.5 kg. Force to slide it about 0.29 kg. Up to 80 C. 1.1 g. | MAKER [M1] |
| Disc magnet, 10 mm x 3 mm, N42 | Pull about 1.8 kg. Up to 80 C. 1.8 g. | MAKER [M2] |
| Magnets in general | The pull is the value on steel, in contact. A magnet resists a slide with about one fifth of its pull (0.29 kg against 1.5 kg above). | MAKER [M1] for the two numbers. The condition "on steel, in contact" was not read on the page: NOT CONFIRMED. |
| Magnets and heat | The limit is 80 C. Do not press a magnet in with a hot iron. Bond it in a pocket. | MAKER [M1]. The advice is ESTIMATED. |
| Magnets under lever load | "Magnets resist sliding and peeling poorly. Lever moments peel the panel. Use magnets only to seat the panel." | Controls, 6.4 |
| Quarter-turn fastener, small series (Southco DZUS 81, 82, 85) | A stud with a head of about 9.5 mm in a panel hole of 6.4 mm, and a receptacle on the fixed part. Slotted, hex and wing heads exist. | SOURCED [Q1], read from a catalogue page whose text did not extract cleanly. Confirm on the maker's sheet. The maker's page refused the request [Q2]. |
| Thumb screw | M4, knurled head, into an M4 heat-set insert | Joint 5 of joints. No data sheet was read for the head sizes. |
| Captive thumb screw | The screw stays in the part when it is loose | Controls, 6.5 |

Options for each part. The first option in each row is the plan in the repository.

| Part | Mass and load | Options | Recommendation and reason |
| --- | --- | --- | --- |
| Rear door (422.7 mm x 165 mm, two halves bonded into one) | About 0.35 kg of skin (split report). The foam seals push it out. It carries no cable. | (1) A lip on the sill, two pins, four thumb screws. (2) The lip, the pins, and two quarter-turn fasteners at the top. (3) The lip, the pins, and magnets at the top. (4) Lift-off hinges on one side (2.4). | Option 1 or 2. The foam seals need a force that stays, and a screw or a quarter-turn gives it. Magnets are a risk here: the force of the seals is not known. |
| Bezel plate (four plates, one for each aspect ratio) | About 0.76 kg of skin (split report). It leans on a face reclined 30 degrees and rests on its bottom ledge. | (1) Two pins in the bottom ledge and magnets on the fixed cradle. (2) Two pins and two screws from the front (they show). | Option 1. The plate carries no load, and the player changes it by hand. Start with four pairs of 8 mm x 3 mm magnets, and add pairs if the plate rattles. |
| Control panel | The lever puts a moment of 1.2 N m to 2.4 N m on it (controls, 6.3). | (A) A tongue at the rear and two clamps at the front. (B) A ledge, two pins and four captive thumb screws or quarter-turns. Magnets only seat the panel. | Follow controls, 6.5: make a coupon of the two. The fasteners go into metal. |
| Hood | It lifts off for service only. | Four cones and four M4 screws from below (2026-11-16). | Bolted. The rear door comes off first to reach the screws. |
| USB socket plate | It comes off only when a socket changes. | M4 screws from inside into inserts. | As the plan. No change. |

Magnet count for the bezel plate, as a first value: the plate weighs about 7.5 N. The face is reclined
30 degrees. Thus 87 % of the weight acts along the face, and the ledge takes it. Half of the weight
pushes the plate onto its seat. The magnets do not carry the plate: they stop a rattle, and they hold
the plate when a person moves the cabinet. Four pairs with 1.5 kg each give a pull of about 59 N in
contact. A layer of plastic or paint between the magnets makes this much less, so the count is a
value for the coupon. ESTIMATED.

### 2.4 Hinges or lift-off pins for the rear door

| Option | What it needs | For | Against |
| --- | --- | --- | --- |
| Lift-off, with a lip and pins (the plan) | A lip on the sill, two pins of 4 mm, and the fasteners of 2.3 | No hardware shows except the fasteners. The door needs no room to swing. One person lifts it away, because no cable is on it (decision record 0005). | The door is loose in the hand when it is off. |
| Lift-off (flag) hinges on one side | Two hinges in a left-hand or a right-hand version, of about 50 mm (2 inch), with screws into inserts | The door stays on the cabinet, or lifts off when it is open | The door needs about 423 mm of room behind the cabinet to swing. The hinge shows on a rear that the owner made planar. The hinge side needs a thicker frame. |
| A hinge at the sill (the door folds down) | Two small hinges at the bottom edge | The door hangs down on the table | It needs 165 mm of room behind the cabinet. The hinge shows. |

No data sheet of a hinge was read. The sizes are those of retail listings (SOURCED (summary) [Q3]).

Recommendation: keep the lift-off door. The cabinet stands near a wall, the owner does not want a
deeper cabinet, and the rear is planar. A hinge adds a part that shows and room that the desk does not have.

### 2.5 Speakers and amplifier

The room is the limit. The fit report gives, behind each speaker form, a round frame of 53.9 mm and a
depth of 109 mm.

| Driver | Frame | Depth | Power | Sensitivity and range | Fits the room | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Dayton Audio CE32A-8 (the driver of the reference cabinet's maker) | 32 mm x 32 mm | 15.5 mm | 2 W | 77.9 dB, 240 Hz to 20 kHz | Yes | MAKER [A1]. See also `docs/research/cabinet-references.md` 3.9. |
| Dayton Audio DMA45-8 | 46 mm x 46 mm, four holes of 3.3 mm on a circle of 50.2 mm | 26.1 mm behind a flange of 3.0 mm | 10 W | 76.9 dB at 2.83 V, 150 Hz to 20 kHz | Probably. The corners of the square frame reach about 58 mm. Put it in the fit study. | MAKER [A2] (the drawing on the specification sheet). The corner value is ESTIMATED. |
| Visaton FRS 5 X, 8 ohm | 5 cm (2 inch), two fixing lugs, opening in the baffle 46 mm | Not read | 5 W rated, 8 W music | 86 dB (1 W, 1 m), 120 Hz to 20 kHz | Not confirmed: the frame size with its lugs was not read | MAKER [A3] |
| A driver of 57 mm | - | - | - | - | No. The frame is larger than 53.9 mm. | Fit report |

The Visaton driver is 8 dB to 9 dB louder for the same power than the two Dayton drivers. This matters
with a small amplifier.

| Amplifier | Supply | Output | Notes | Status |
| --- | --- | --- | --- | --- |
| PAM8403 board | 2.5 V to 5.5 V | About 3 W for each channel into 4 ohm at 5 V. Less into 8 ohm. | The maker of the reference cabinet uses it. Small boards exist with a volume control. | `docs/research/cabinet-references.md` 3.9. The output values are recalled from the data sheet and were not read again: the maker's site refused the request. |
| TPA3110D2 board | 8 V to 26 V | 10 W for each channel into 8 ohm at 13 V, 10 % distortion. 15 W at 16 V. | Class D, 90 % efficiency, no output filter necessary. It runs on the 12 V of the supply. | MAKER [A4] |

Recommendation: the Visaton FRS 5 X or the DMA45-8 with a PAM8403 board on the 5 V rail, as the first
bench set-up. It is the lowest cost, and 2 W to 3 W is sufficient at the player's distance of about
0.5 m. Take the TPA3110D2 board if the sound is too quiet. ESTIMATED: no listening test.

Not confirmed:

- The audio source. The monitor has a 3.5 mm output (envelopes, section 1). A bench test must show
  that it works with the HDMI input, and that it has no noise.
- Noise from the supply. An amplifier on the same 5 V as the hub can pick up noise. A USB audio adapter
  or a ground-loop isolator is the usual answer. No source was read for this.
- A volume control that the player can reach. The owner decides if one is wanted and where.

### 2.6 The marquee

Two kinds. The owner decides.

| Kind | Parts | Facts | Status |
| --- | --- | --- | --- |
| Lit marquee: a strip and a diffuser | A COB strip of 12 V, 8 mm wide, one length of about 340 mm. A diffuser of opal acrylic, 3 mm. The art is a print on film behind the cover. | Example strip: 480 LEDs in 1 m, 10 W in 1 m, 12 V, smallest cut length 25 mm. A length of 340 mm takes about 3.4 W. | SOURCED [L1] (a seller's page). The watts are ESTIMATED from 10 W in 1 m. |
| Lit marquee with colour | An addressable 5 V strip, 60 LEDs in 1 m, on a small controller | Each LED draws up to 60 mA at full white. The rule of thumb is 20 mA for each LED. 20 LEDs: 0.4 A to 1.2 A at 5 V. | SOURCED [L2] |
| Scrolling marquee: LED matrix modules | Modules of 32 mm x 32 mm (8 x 8 LEDs) in a row, and a controller on USB | The window of 352 mm is 11 modules of 32 mm. The params keep 25 mm of depth for them. | ESTIMATED from the fit study values. No module was read from a data sheet. |

Distance from the strip to the diffuser: a strip with separate LEDs shows dots unless the diffuser is
about one LED pitch away or more. A COB strip has no dots. The room is 82 mm deep, so the two kinds have
sufficient distance. ESTIMATED: a rule of thumb, with no source read.

Recommendation: decide lit or scrolling first, because the cover and the room follow from it. For a lit
marquee, the 12 V COB strip is the simplest: it has two wires, it needs no controller, and it goes off
with the supply.

### 2.7 Front USB

`docs/research/pc-panel-and-front-usb.md` has the research. This list takes its recommendation: screw-flange
sockets on short cables in a removable printed socket plate, and a hub with its own 5 V from a SATA
lead. Still open: the hub model, and USB 2 or USB 3 at the sockets. The power button can sit in the
same plate (power button note, section 9.2).

### 2.8 Pads under the floor

The owner settled thin non-slip pads of 2 mm to 3 mm, and no feet.

| Option | Facts | For | Against |
| --- | --- | --- | --- |
| Moulded polyurethane bumper pads with adhesive (3M Bumpon type) | "Excellent skid-resistance, high coefficient of friction." Solid polyurethane with a rubber adhesive. | Made for this use. Many shapes. | The maker's data sheets refused the request, so no size was read. Many shapes are higher than 3 mm. |
| Pads cut from a sheet of the same material | A roll or a sheet, cut to squares | The owner sets the thickness and the size | The cut edges are less neat |
| Silicone or rubber sheet, 2 mm, with adhesive tape | A common material | Low cost | The bond of tape to silicone is poor. Rubber can mark a painted or oiled desk. Not confirmed. |

Status of the facts: SOURCED (summary) [F1].

Load: the cabinet is about 17.3 kg (split report), which is 169 N. On 12 pads this is 14 N for each
pad. ESTIMATED. Put pads under the wall feet, under the supply, and under the front edge of the deck,
where the hands press. The bottom of the PETG floor needs a clean, scuffed face for the adhesive
(finishing, 2.1).

### 2.9 The mains lead and the rear face of the supply

| Item | Value | Status |
| --- | --- | --- |
| Lead in the supply's box | C13 plug, 1500 mm | Cooling, Part B (the maker's sheet) |
| What the lower rear wall must have | One opening for the 150 mm x 86 mm rear face: the vent, the C14 inlet, the rocker and the ECO switch. The four No. 6-32 screws locate the supply. | Roadmap, "Mains entry". Cooling, Part B. |
| Clear space behind the exhaust | 12.7 mm at least | STANDARD (ATX12V design guide, in envelopes, section 6) |
| Depth of a straight C13 plug behind the cabinet | About 80 mm with the cable bend | ESTIMATED: a plug body of about 45 mm and a bend |
| Depth of a right-angle C13 plug | "It extends approximately 1 inch" (25 mm) | SOURCED (summary) [C1] (one retail listing) |
| Right-angle leads | Sold with the cable down, up, left or right. 16 AWG, 13 A at 125 V. | SOURCED (summary) [C1] |

The inlet is at x 88 mm to 119 mm of the rear face with the fan up (cooling, Part B, estimated from
a photo). The direction of the angle must take the cable away from the vent. Look at the real unit
before the lead is bought.

Recommendation: a right-angle C13 lead, so that the cabinet can stand about 60 mm nearer the wall. The
owner set that the cabinet must fit on a normal surface.

### 2.10 Prices found

No price was invented. The list has only these.

| Item | Price | Source and date |
| --- | --- | --- |
| CNC Kitchen M4 x 8.1 mm inserts, 50 pieces | USD 11.04 without VAT | [H1], 2026-11-14 |
| CNC Kitchen M3 x 5.7 mm inserts, 100 pieces | USD 11.04 without VAT | [H1], 2026-11-14 |
| Disc magnet 8 mm x 3 mm | EUR 0.43 each for 10 | [M1], 2026-11-14 |
| Disc magnet 10 mm x 3 mm | EUR 0.50 each for 10 | [M2], 2026-11-14 |
| Dayton Audio DMA45-8 | USD 11.99 (the maker's list price) | [A2], 2026-11-14 |
| Adapter for the power button, 24-pin edition with a button | USD 45.00 | Power button note, 2026-11-14 |
| Adapter, LITE edition | USD 20.00 | Power button note, 2026-11-14 |
| Latching button of 16 mm with an LED ring | USD 4.95 | Power button note, 2026-11-14 |
| USB-A panel socket, DataPro 1698, 150 mm | USD 16.45 | Panel and USB, 2026-11-10 |
| USB-C panel socket, DataPro 1678, 150 mm | USD 19.45 | Panel and USB, 2026-11-10 |
| Keyboard PCB, KBDfans DZ60RGB-ANSI v2 | USD 55.00 | Panel and USB, 2026-11-10 |
| Structural adhesive, Plexus MA310, 50 ml | USD 29 to 35 | Finishing, 2026-11-11 |
| PETG filament | USD 10.00 to 13.99 for 1 kg | `docs/research/abs-switch.md` 8.2, 2026-11-11 |

### 2.11 Open questions for the owner

1. The rear door: four thumb screws, or two quarter-turn fasteners with the lip and the pins? Do the
   fasteners on the back matter for the look?
2. The marquee: lit or scrolling?
3. The speakers: is the sound of a driver of 40 mm to 50 mm sufficient, or must the hood band give
   more room?
4. A volume control: is one wanted, and where?
5. The power for the monitor. The fit study routes a USB-C power cable to it, but no document says
   where the power comes from. Options: the monitor's own mains adapter outside the cabinet, the 5 V
   rail of the supply (only if the monitor runs on 5 V and 3 A, which is not confirmed), or a 12 V
   to USB-C converter on the supply. A bench test must show what the monitor accepts.
6. The lift-off door stays as the plan, unless the owner wants a hinge.

### 2.12 Sources

| No. | Source | What it is |
| --- | --- | --- |
| H1 | https://www.3djake.com/cnc-kitchen/threaded-inserts-m4-standard and https://www.3djake.com/cnc-kitchen/threaded-inserts-m3-standard | A retailer's copy of the insert maker's table: length, diameters, hole, wall, price |
| H2 | https://www.3djake.com/ruthex/m2-m3-m4-m5-threaded-insert-assortment-box | A retailer's copy of a second maker's table, M2 to M5 |
| H3 | https://www.cnckitchen.com/blog/tips-and-tricks-for-heat-set-inserts | The insert maker's design rules and iron temperatures |
| H4 | https://www.cnckitchen.com/blog/are-our-heat-set-insert-datasheets-wrong | The insert maker's pull-out test against the hole diameter (PLA) |
| H5 | https://www.spirol.com/resources/white-papers/how-to-design-the-proper-hole-for-heat-ultrasonic-inserts/ | An insert maker's white paper: hole, depth, boss, position |
| M1 | https://www.supermagnete.de/eng/disc-magnets-neodymium/disc-magnet-8mm-3mm_S-08-03-N | Magnet data: pull, slide force, temperature, price |
| M2 | https://www.supermagnete.de/eng/disc-magnets-neodymium/disc-magnet-10mm-3mm_S-10-03-N | Magnet data |
| Q1 | https://www.aircraftspruce.com/catalog/pdf/dzus82receptacles.pdf | A reseller's copy of a catalogue page of small quarter-turn fasteners |
| Q2 | https://southco.com/en_us_int/fasteners/emdzusemreg-quarter-turn-fasteners | The maker's page for quarter-turn fasteners. Summary only: HTTP 403 to the fetch. |
| Q3 | Search results for lift-off hinges (retail listings) | Summaries only |
| A1 | https://www.daytonaudio.com/images/resources/285-101-dayton-audio-ce32a-8-spec-sheet.pdf | Maker's specification sheet |
| A2 | https://www.daytonaudio.com/images/resources/295-581--dayton-audio-dma45-8-specification-sheet.pdf and https://www.daytonaudio.com/product/1613/dma45-8-1-1-2-dual-magnet-aluminum-cone-full-range-driver-8-ohm | Maker's specification sheet with a dimension drawing, and the product page |
| A3 | https://www.visaton.de/en/products/drivers/fullrange-systems/frs-5-x-8-ohm | Maker's product page |
| A4 | https://www.ti.com/product/TPA3110D2 | Maker's page of the amplifier chip |
| L1 | https://www.ledbe.com/8mm-12v-24v-cob-led-strip | A seller's page of a COB strip |
| L2 | https://learn.adafruit.com/adafruit-neopixel-uberguide/powering-neopixels | A maker's guide: current of addressable LEDs |
| F1 | 3M Bumpon protective products (search summaries of the maker's data sheets on multimedia.3m.com) | Summaries only: HTTP 403 to the fetch |
| C1 | https://www.amazon.com/Cable-Matters-2-Pack-Profile-Angled/dp/B07574DZM9 and a search for right-angle C13 leads | Summaries only |

### 2.13 Not confirmed, and sources that were not accessible

| Item | Result |
| --- | --- |
| A maker's table that names PETG for inserts | Not found. The pull-out test was in PLA. |
| The insert maker's own dimension poster | An image. The retailer's text copy was used. |
| The data sheet of the PAM8403 | The maker's site answered HTTP 403. The values are recalled. |
| The size of the Visaton frame with its lugs, and its depth | Not on the page that was read. The data sheet was not opened. |
| A 2 inch Peerless full-range driver | Not read. The part that the search gave (P830986) is a 3 inch driver, which does not fit. |
| The maker's sheets of quarter-turn fasteners and of thumb screws | Not read (HTTP 403). One reseller's catalogue page was read in part. |
| Hinge data sheets | Not read. Retail listings in search summaries only. |
| The pad maker's data sheets (3M) | HTTP 403. Summaries only. No size was read. |
| A data sheet for LED matrix modules and for opal acrylic | Not read. |
| The pull of a magnet through a layer of plastic | No value was read. |
