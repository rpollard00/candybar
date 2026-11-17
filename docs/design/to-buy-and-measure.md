# To buy and to measure

Date: 2026-11-17. All lengths are in millimetres.

This sheet is for the desk. It lists what to buy, what to measure, what to try on the bench and what to print first. Each value comes from the document in the "Source" column. The reasons are in those documents. This sheet does not repeat them.

"Not in the documents" means that no document of this repository gives the value.

The full parts list, with the alternatives and the prices, is [hardware-list.md](hardware-list.md).

## 1. To buy

The column "Model" tells if the model depends on the exact size of the part. "Yes" names the part of the model that changes.

### 1.1 Leads and plugs

| Item | For | Qty | Size or specification | Model | Source |
| --- | --- | --- | --- | --- | --- |
| HDMI lead, right-angle at each end | Video and sound from the adapter to the monitor | 1 | HDMI type A to mini-HDMI type C, HDMI 2.0, 0.5 m. **Adapter end:** the lead leaves along the short axis of the adapter's HDMI socket, toward the front of the cabinet. Plug body at most 23 along the socket's long axis, 13.5 along its short axis, 24 long out of the adapter. **Monitor end:** the lead leaves parallel to the left edge, toward the bottom edge (the plug turns along the long axis of the socket). Stand-out 22 or less. Choose by a picture: the sellers' names for the angles differ. Hold the adapter in the board's socket and look before you buy. | Yes: the opening of the duct's end wall (25 x 14.5) and the plug room of 22 at the monitor | [hardware-list.md](hardware-list.md) 1.2, [monitor-cradle-and-bezel.md](monitor-cradle-and-bezel.md) "The cable channel" |
| USB-C lead, right-angle at the monitor | Power from the charging hub to the monitor | 1 | USB-C to USB-C, 3 A, right-angle plug at the monitor. Route about 600 to 800 (estimated). Stand-out in the plug room of 22. | Yes: the plug room of 22 at the monitor's left edge | [monitor-power-and-video.md](../research/monitor-power-and-video.md) 4 |
| Molex to barrel lead | 12 V to the charging hub | 1 | Four-pin (Molex) plug to a barrel plug 5.5 x 2.5, 12 V version, centre positive. A 5.5 x 2.1 plug does not fit. | No | [monitor-power-and-video.md](../research/monitor-power-and-video.md) 4 |
| In-line fuse holder and fuse | The 12 V wire of the charging hub, near the Molex plug | 1 | About 3 A for the monitor only. About 5 A if the hub's USB-A ports carry a load. | No | [monitor-power-and-video.md](../research/monitor-power-and-video.md) 4 |
| SATA to barrel lead | 5 V to the front USB hub | 1 | SATA 15-pin to a DC barrel plug, 5 V version. Plug size to suit the hub (5.5 x 2.1 or 3.5 x 1.35 are common). Check the polarity. | No | [pc-panel-and-front-usb.md](../research/pc-panel-and-front-usb.md) A3 |
| USB lead, board to hub | One lead from the compute module to the hub | 1 | USB-A to the hub's input, about 600 | No | [hardware-list.md](hardware-list.md) 1.5 |
| USB lead, control panel | One lead for each panel to the cabinet | 1 for each panel | Right-angle USB-C at the encoder to USB-A, with a loop of 200 | No | [control-panel.md](control-panel.md) "Assumptions", [hardware-list.md](hardware-list.md) 1.3 |
| Mains lead | The supply's C14 inlet | 1 | Right-angle C13 plug (about 25 behind the cabinet). Sold with the cable down, up, left or right: the cable must go away from the vent. Look at the real supply before you buy. | No | [hardware-list.md](hardware-list.md) 2.9 |
| Multi-pin plug pair | The speakers and the marquee light at the foot of the hood | 1 pair | 4 pins for the speakers, and the marquee's wires. About 200 of slack on the hood's side. | No | [hardware-list.md](hardware-list.md) 1.6 |
| In-line plugs | The power button and the volume control, behind the socket plate | 1 four-pin, 1 three-pin | Plugs that lock | No | [front-socket-plate.md](front-socket-plate.md) "Behind the plate" |
| Small connectors | Each part that comes out: the compute module, the hood, the socket plate | A few | 2-pin and 4-pin, that lock | No | [hardware-list.md](hardware-list.md) 1.11 |
| Wire | Button, LED and speakers | A few metres | Stranded, 0.25 to 0.5 mm2. Speakers: two twisted pairs. | No | [audio.md](../research/audio.md) 5 |
| Cable ties | Cradle channels, staples, docks | As necessary | 2.5 wide for the cradle channels | Yes: the tie slots of 4 x 2.5 | [monitor-cradle-and-bezel.md](monitor-cradle-and-bezel.md) "Parts" |

### 1.2 Power, display and USB parts

| Item | For | Qty | Size or specification | Model | Source |
| --- | --- | --- | --- | --- | --- |
| 12 V to USB-C charging hub | Power for the monitor | 1 | SlimQ M0002, 74.7 x 51.3 x 22.6, 80 g. Input 5.5 x 2.5 barrel. | Yes: its place (156.7 x 60 x 30 with plugs) and the two ribs | [hardware-mounts.md](hardware-mounts.md) "The places of the small items" |
| Power button adapter | The everyday power button on `PS_ON` | 1 | mosfet.party "ps_on adapter - ATX 24pin edition + button" (with a 16 mm lit button). If it is not in stock: the LITE edition and a 16 mm button. | Yes: its place, 60 x 25 x 20 (estimated) | [bc250-power-button.md](../research/bc250-power-button.md) 6 and 8 |
| Power button | Socket plate | 1 | Momentary, 16 mm thread, LED ring, four wires (comes with the 24-pin edition) | Yes: the hole (16.0 to 16.4 on the coupon), the flat face of 22, 45 clear behind | [front-socket-plate.md](front-socket-plate.md) "What the plate carries" |
| Front USB hub | The four front sockets | 1 | Powered. Two USB-C and two USB-A ports for the sockets. Own DC input. Model not chosen. | Yes: the hub rails and the saddle (`usb_hub_l`, `usb_hub_w`, `usb_hub_h`) | [hardware-list.md](hardware-list.md) 1.5, [hardware-mounts.md](hardware-mounts.md) "The hub" |
| USB-A panel socket on a cable | Socket plate | 2 | Screw flange, holes 30.0 apart, cut-out 14.7 x 7.3 (example: DataPro 1698). Lead 300. USB 2 or USB 3: open. | Yes: the cut-outs, the flange holes and the back pockets | [front-socket-plate.md](front-socket-plate.md), [pc-panel-and-front-usb.md](../research/pc-panel-and-front-usb.md) A5 |
| USB-C panel socket on a cable | Socket plate | 2 | Screw flange, holes 20.0 apart, cut-out 10.5 x 4.6, male to female (example: DataPro 1678). Lead 300. | Yes: as above | The same |
| Flange screws | USB sockets | 8 | No. 4-40, into the nuts of the flanges | No (the heads show) | [hardware-list.md](hardware-list.md) 1.5 |
| Storage | The BC-250's M.2 socket | 1 | M.2 2280, SATA or NVMe | No | [hardware-list.md](hardware-list.md) 1.1 |
| Thermal pads or putty | Only if the heatsink comes off | As necessary | Thickness to the measured gaps | No | [hardware-list.md](hardware-list.md) 1.1 |
| Duct fan (option) | Exhaust duct | 0 or 1 | 92, on four screws. A thermal test decides. | Yes, if fitted: not modelled | [hardware-list.md](hardware-list.md) 1.1 |

### 1.3 Audio

The chain is open until the bench tests of section 3. Chain (B) has the parts below. Chain (A) has the same parts with no sound adapter and with a 3.5 mm lead of about 0.8 m from the monitor.

| Item | For | Qty | Size or specification | Model | Source |
| --- | --- | --- | --- | --- | --- |
| Amplifier | Speakers | 1 | Adafruit 1752 (MAX9744), 54 x 41, on 12 V | Yes: its place on the floor, 54 x 41 x 20 | [audio.md](../research/audio.md) 3 and 5, [hardware-mounts.md](hardware-mounts.md) |
| Fuse for the amplifier | 12 V branch of the Molex lead | 1 | About 3 A | No | [audio.md](../research/audio.md) 5 |
| USB sound adapter (chain B) | Sound source | 1 | Sabrent AU-MMSA or Adafruit 1475 (43.8 x 23.2 x 12.0) | Yes: its place, 44 x 23 x 12 | [audio.md](../research/audio.md) 4 |
| Signal lead | Adapter to amplifier | 1 | 3.5 mm stereo plug to plug, 0.15 to 0.3 m | No | [audio.md](../research/audio.md) 5 |
| Volume potentiometer | Socket plate | 1 | 1 kΩ, linear, threaded bushing M9 x 0.75, shaft 6.0 with a flat (example: Bourns PTV09, version 6) | Yes: the hole 9.4, the wall 2.4, 20 clear behind | [audio.md](../research/audio.md) 7 |
| Knob | Potentiometer | 1 | For a 6 shaft with a flat, 15 to 20 across | Yes: the flat circle of 22 | [audio.md](../research/audio.md) 7 |
| Speaker driver | Hood band A | 2 | Tectonic TEBM35C10-4, square frame 51.8. Second choice: Visaton FRS 5 X (it needs its own seat pocket). | Yes: the seat pocket, the basket hole of 48, the sealed enclosure of 0.45 l | [hardware-list.md](hardware-list.md) 1.6, [audio.md](../research/audio.md) 14 |
| Grille screws | Band A grilles | 2 for each grille | M3 button head (ISO 7380), into M3 inserts in the seat. Length: not in the documents. | Yes: the insert holes 4.0, 5.65 deep | [hardware-list.md](hardware-list.md) 1.6 |
| Enclosure screws | Speaker enclosures | 4 for each enclosure | M3, through the ears into M3 inserts in the baffle. Length: not in the documents. | Yes: the ears and the baffle | [hood-band.md](hood-band.md) 3 |
| Foam ring | Driver to baffle, enclosure to baffle | 2 for each speaker | Closed-cell foam, 2 to 3 thick | No (not modelled) | [audio.md](../research/audio.md) 13 |
| Polyester fibre | Damping in the enclosures | A little | Loose fill | No | [audio.md](../research/audio.md) 13 |
| Ferrite beads | Speaker wires at the amplifier | Not in the documents | Not in the documents | No | [audio.md](../research/audio.md) 2.4 |
| Ground loop isolator | Only if there is hum | 0 or 1 | For a 3.5 mm lead | No | [audio.md](../research/audio.md) 5 |

### 1.4 Control panel

| Item | For | Qty | Size or specification | Model | Source |
| --- | --- | --- | --- | --- | --- |
| Disc magnet | Push bolt latch, in the frame (once) | 4 | N52, 12 x 2, axial | Yes: the pad pockets 12.2 x 2.2 | [control-panel-latch.md](control-panel-latch.md) "The interface" |
| Steel disc | Latch points in each panel | 4 for each panel | Steel, 12 x 2 | Yes: the pockets 12.2 x 2.2 | The same |
| Compression spring | Push bolt | 1 | Steel, 4 outside, 22 free, about 1.2 N/mm | Yes: the stroke, the gate's peg and the tunnel | [control-panel-latch.md](control-panel-latch.md) "Assumptions" |
| Epoxy | Magnets and discs | A little | Two-part | No | [hardware-list.md](hardware-list.md) 1.3 |
| Lever | Arcade panel | 1 | Sanwa JLX2-TP-8YT, plate 53 x 95, slots on 40 x 85 | Yes: the lever bosses and the shaft hole of 24 | [hardware-list.md](hardware-list.md) 1.3 |
| Ball top | Lever | 1 | Sanwa LB-35, M6 | No | The same |
| Lever harness | Lever | 1 | Sanwa JLF-H, 5 pins | No | The same |
| Lever fixings | Lever plate | 4 | M4 heat-set inserts and 4 M4 screws | Yes: insert hole 5.6, bosses | [control-panel.md](control-panel.md) "The parts" |
| Action buttons | Arcade panel | 8 | Sanwa 30 screw-in (OBSN-30), nuts of 36 | Yes: the holes (30.0 or 30.3 on the coupon) | [roadmap.md](../roadmap.md) "Settled by the owner" |
| Start, coin and menu buttons | Arcade panel | 3 | Sanwa 24 (OBSN-24 for screw-in) | Yes: the holes (24.0 or 24.3) | [hardware-list.md](hardware-list.md) 1.3 |
| Encoder | One for each panel | 1 for each panel | RP2040 Advanced Breakout Board (GP2040-CE), 96.3 x 45.3 | Yes: its posts | The same |
| Encoder screws | Encoder | 4 for each panel | Thread-forming, 3.0 | Yes: pilot hole 2.6 | [control-panel.md](control-panel.md) "The parts" |
| Tile seam screws | The seam between the two tiles | 4 for each panel | M3 x 12 with nuts | Not in the documents | The same |
| Button wires | Buttons to encoder | 11 signal wires and a ground chain for each panel | 2.8 (#110) female terminals | No | [hardware-list.md](hardware-list.md) 1.3 |
| Fall-back fixings (only if the latch fails) | Panel | 4 + 4 | M4 x 16 countersunk (ISO 10642) and M4 x 8 inserts | Yes | [control-panel.md](control-panel.md) "The parts" |
| Cut plate and clear cover (later) | Arcade panel top | 1 each | 5052-H32 aluminium 2.03, polycarbonate or acrylic 1.5 | Yes: the plate stack | [hardware-list.md](hardware-list.md) 1.3 |
| Keyboard parts (PC panel) | The owner's 60 % keyboard | 1 set | GH60 hot-swap PCB (285 x 94.6), MX switches (61 for ANSI), keycaps, stabilisers, 1.60 aluminium plate, M2 inserts and screws (4 to 6) | Yes: the PCB posts and the plate | [hardware-list.md](hardware-list.md) 1.4 |

### 1.5 Shell, cradle and mounts

| Item | For | Qty | Size or specification | Model | Source |
| --- | --- | --- | --- | --- | --- |
| Heat-set insert, M4 | Service seams, hood, cradle, lever | About 30 to 40 | Brass, M4 x 8.1, outside 6.3 | Yes: hole 5.6 (coupon), 9.5 deep, boss 13 | [hardware-list.md](hardware-list.md) 1.9 |
| Heat-set insert, M3 | Mounts, socket plate, cradle channels, speakers | About 20 to 30 | Brass, M3 x 5.7, outside 4.6 | Yes: hole 4.0, depth 6.5 (mounts) | [hardware-list.md](hardware-list.md) 1.9, [hardware-mounts.md](hardware-mounts.md) |
| Heat-set insert, M2 | Keyboard PCB posts | 4 to 6 | Brass, M2 x 4.0, outside 3.6 | Yes: hole 3.2 | [hardware-list.md](hardware-list.md) 1.9 |
| Screw, joint 1 | Skin to skin seams | 41 | Thread-forming for plastics, 3.0 x 16, pan head, 30 degree thread (EJOT PT type) | Yes: pilot hole 2.25 or 2.4 (coupon) | [print-pieces.md](print-pieces.md) "The checks of the whole set" |
| Screw, floor | Floor laps and foot flanges | 50 | Thread-forming, 3.5 x 9.5, countersunk, from above | Yes: pilot hole 2.6, countersink | [print-pieces.md](print-pieces.md) "The floor" |
| Screw, hood | Hood to top ring | 4 | M4 x 20 socket head (ISO 4762), into 4 M4 inserts | Yes: the bosses, insert hole 9.5 deep | [print-pieces.md](print-pieces.md) "The bolted hood" |
| Hex key | Hood screws | 1 | 3, ball end, long arm 100 or more | No | The same |
| Quarter-turn fastener | Rear door head | 2 | Panel quarter-turn, shank 6.0 to 6.4, head 15 at most, grip 7 (door 4, web 3), with a receptacle | Yes: hole 6.5, receptacle room 32 x 13 x 9, web hole 9 | [roadmap.md](../roadmap.md) step 11 |
| Dowel pin | Rear door halves | 2 | Steel, 4 x 10 | Yes: the pin holes | [roadmap.md](../roadmap.md) step 11 |
| Foam seal, fan to door | Fan vent | 1 | Soft closed-cell foam (5 kPa), ring 116 inside, 140 outside, to fill the gap of 7.0 | Yes: the push bows the door head (0.4 soft, 1.5 firm) | [hardware-list.md](hardware-list.md) 1.1, [roadmap.md](../roadmap.md) step 11 |
| Foam seal, duct to door and shroud | Exhaust duct | About 1 m | Closed-cell foam strip, 3 thick, soft. Gap at the duct 5.1. | Yes: as above | The same |
| Foam pad, HDMI seal | Duct end wall, round the HDMI plug | 1 | Closed-cell foam, 3 thick, 5 beyond the opening on each side, hole cut to the plug | Yes: `rear.hdmi_seal` | [duct-lead-exit.md](duct-lead-exit.md) "Way 1 as built" |
| Foam pad, hub | Between the hub and its saddle | 1 | 1 thick | Yes: the saddle stands 0.5 above the hub | [hardware-mounts.md](hardware-mounts.md) "The hub" |
| Cradle screws | Uprights and jaws | 4 + 4 | M4 x 25 and M4 x 12, button head (ISO 7380) | Yes: the uprights, lugs and shoes | [monitor-cradle-and-bezel.md](monitor-cradle-and-bezel.md) "Parts" |
| Cradle nuts and washers | Jaw lock screws | 4 + 4 | M4 hexagon nuts, M4 washers | Yes: the nut seat in each shoe | The same |
| Cradle inserts | Uprights, cable channels | 4 + 4 | M4 inserts (uprights), M3 inserts (channel bosses) | Yes | The same |
| Channel screws | Cable channels | 4 | M3 x 8 | Not in the documents | The same |
| Dowel pin | Bezel plate location | 4 | 4 x 12, pressed into the lugs | Yes: slots 4.3 wide | The same |
| Dowel pin | Bezel plate seams | 4 | 4 x 16 | Yes | The same |
| Disc magnet | Bezel plate | 8 (4 pairs) | 8 x 3 | Yes: pockets 8.2 x 3.1 | The same |
| Cellular rubber strip | Jaw pads | A little | 2 thick | Yes: the jaws press it 0.5 | The same |
| Felt | Jaw rests | A little | 1 thick | Yes: the rests are made for it | The same |
| Mount screws | Docks, hanging screws, right tray, shroud and duct | 4 + 2 + 2 + 4 | M3 socket head: M3 x 12 (docks), M3 x 10 (hanging), M3 x 18 (right tray), M3 x 10 (shroud and duct). One 2.5 hex driver. | Yes: inserts with hole 4.0, depth 6.5 | [hardware-mounts.md](hardware-mounts.md) |
| Tray screws | Tray to the board's standoffs | 4 | M3 x 20 (if the standoff thread is M3: measure it) | Yes: the posts | The same |
| Socket plate screws | Socket plate | 2 | M3 x 8 button head, into 2 M3 inserts | Yes: hole 3.4, insert hole 4.0 | [front-socket-plate.md](front-socket-plate.md) |
| Non-slip pads | Under the floor | About 9 to 12 | Adhesive, 2 to 3 thick | No | [hardware-list.md](hardware-list.md) 1.10 |
| Cable tie mounts and reusable ties | Inside | As necessary | Adhesive or screwed mounts, reusable ties | No | [hardware-list.md](hardware-list.md) 1.11 |
| Supply pads and straps | Under and over the supply | 4 pads, 2 straps | In the hardware list. The mounts proposal holds the supply with a printed fence and its four screws. | No | [hardware-list.md](hardware-list.md) 1.1, [hardware-mounts.md](hardware-mounts.md) |

### 1.6 Coupons, weld and finish

| Item | For | Qty | Size or specification | Model | Source |
| --- | --- | --- | --- | --- | --- |
| ABS filament | Coupons and shell | 14 spools of 1 kg (plan, with 30 % for failed prints). Coupons: 1748 g. | 1.75. One maker, one type, one colour for the coupons and the shell. Which ABS: open. | Yes: the shrink and the density (1.05) | [print-plan-abs.md](print-plan-abs.md) 5, [coupons.md](coupons.md) |
| Coupon screws | Plates 4, 5, 8 | 50 | 3.0 x 16 thread-forming | No | [hardware-list.md](hardware-list.md) 1.8 |
| Floor coupon screws | Joint 2 (plate 5) | 2 | Countersunk thread-forming 3.5, not longer than 9.5 | No | [coupons.md](coupons.md) plate 5 |
| Wall foot coupon screws | Joint 3 (plate 5) | 2 | Countersunk thread-forming 3.5 x 16 | No | The same |
| Joint 5 coupon parts | Plate 5 | 2 + 2 + 2 | M4 inserts, M4 screws, steel pins 4 x 8 | No | The same |
| Weld and filler | Plates 5 and 8 | See the source | Acetone, ABS slurry from the same spools, a polyester plastic putty that names ABS. Control: the methacrylate adhesive of the PETG plan. | No | [coupons.md](coupons.md) plates 5, 8, 9 |
| Primer and paint | Plates 6, 8, 9 | See the source | The four first coats of the PETG matrix, a hobby lacquer for the stress-crack test | No | [coupons.md](coupons.md) plates 8 and 9 |

### 1.7 Tools for the tests

| Item | For | Source |
| --- | --- | --- |
| Caliper, feeler gauges (0.05 and up), straight edge | Coupons | [coupons.md](coupons.md) |
| Soldering iron with a temperature setting | Inserts (265 C in the ABS note) | [hardware-list.md](hardware-list.md) 2.1 |
| Spring balance | Magnet pull, latch pull (100 N) | [control-panel-latch.md](control-panel-latch.md) "The first test piece" |
| USB-C power meter | Monitor power test | [monitor-power-and-video.md](../research/monitor-power-and-video.md) 9 |
| Wall-socket power meter | Power button tests | [bc250-power-button.md](../research/bc250-power-button.md) 10 |

Not chosen yet, so not in this list: the marquee light and its cover ([hardware-list.md](hardware-list.md) 1.7), a pointing device and a small hub for the PC panel (1.4).

## 2. To measure

"How good" is the status of the value that the model uses now.

| Thing | Value in the model | How good | Part that depends on it | How to measure |
| --- | --- | --- | --- | --- |
| Monitor housing, width and height | 354 x 230. Room reserved 356 x 231 x 11. | From a maker | Top jaws of the cradle (the top edge 230 above the bottom edge), fit study | Rule, about +/-0.5. Include the feet and the button. |
| Monitor: built-in stand or not | None (BE16CU) | From a maker | Cradle | Look at the back. BE16DU Gen 2 has a stand and is 357 x 240 x 15. |
| Monitor: socket heights on the left edge | USB-C about 86 (upper) and about 68, mini-HDMI about 49, above the bottom edge | Estimated (render, +/-5) | Lead clamps (44.0 from the socket, limit 50), channel run, plug room | Rule from the bottom edge of the housing to each socket centre. Also measure the offset from the front face. |
| Monitor: scroll wheel and 3.5 mm jack on the right edge | Wheel about 50, jack about 30 | Estimated (render) | Push rod guide in the right plug room, right channel, audio chain (A) | Rule from the bottom edge of the housing to each centre |
| Monitor: stand-out of the button and the wheel | About 1 to 1.5 | Estimated (render) | Push rod striker (1.0 from the button) | Caliper from the edge |
| Monitor: weight | 0.82 kg | From a maker | Cradle load check | Scale |
| Monitor: VESA hole centres and thread depth | 75 x 75, M4, depth 4, centre about 113 to 115 from the top | From a maker / estimated | Nothing now (the cradle holds the edges) | Caliper |
| DisplayPort plug depth in the board's socket | 9 (checked at 6, 9 and 12). Estimate 8 to 10. | Estimated | Duct end-wall opening and the floor relief (`rear.hdmi_cuts`): the opening takes 3 more or less | Put the adapter in the socket. Measure from the board's I/O edge to the adapter's body. Subtract from the adapter's length (52.43). |
| Right-angle HDMI plug at the adapter | About 21 x 12 (scene: 14 x 21 x 12). Limit 23 x 13.5, 24 long out of the adapter. | Estimated | Duct end-wall opening 25 x 14.5, room of 26.65 to the side wall | Caliper on the bought lead: section of the plug body and length out of the adapter |
| Right-angle mini-HDMI plug: stand-out from the monitor edge | 15 to 20. Limit 22 (17 for the larger monitor study). | Estimated | Plug room of 22 at the left edge, the way out of the monitor | Plug in. Caliper from the housing edge to the far face of the plug. |
| Right-angle USB-C plug at the monitor | Section at most 12.35 x 6.5. Length 22 to 35. | Standard / estimated | Plug room of 22 | As above. Also check that the two right-angle plugs on the left edge clear each other. |
| Lead diameters | HDMI 5 to 7, USB-C 3.5 to 4.5, 3.5 mm 3 to 4 | Estimated | Cable channels (462 mm2 each) | Caliper on the bought leads |
| Supply: rear face | Inlet x 88 to 119, z 34 to 57. Rocker x 128 to 142, z 35 to 55. ECO switch x 128 to 142, z 21 to 31. Screw holes on the ATX pattern. | Estimated (photo) | Openings and the four 4.0 holes of the lower rear wall (piece rear lower L), the direction of the mains plug | Fan up, seen from outside, origin at the lower left corner. Caliper to each feature edge and each hole centre. Confirm the hole at (30, 80) of the fan-down frame. |
| Supply: socket face | Socket rows in the lower 10 to 50 of the 86. `psu_plug_h` = 86. | Estimated (photo) | Plug zone in front of the supply | Rule from the underside, fan up |
| Supply: bare weight | 3.27 kg (probably with the cables) | From a maker | Mount loads, structure | Scale, without the leads |
| Supply: PCIe lead | 700 long. The board needs 16 AWG. | From a maker | Route to the board | Read the gauge on the lead. Measure the length. |
| Front USB hub, with its plugs in | 110 x 45 x 20. Front plugs 40 to 70 behind the socket plate. | Estimated | Hub rails and saddle (`usb_hub_l`, `usb_hub_w`, `usb_hub_h`) | Measure the chosen hub with each plug in, and the bend of each lead |
| Charging hub, with its plugs in | 74.7 x 51.3 x 22.6. Room 156.7 x 60 x 30, 41 for each plug. | From a maker | Its place and ribs | Measure the unit with the barrel plug and the USB-C plug in |
| Barrel plug of the Molex lead | 5.5 x 2.5, 12 V, centre positive | From a maker | None (safety) | Caliper and a meter, before the plug goes into the unit |
| Quarter-turn fasteners | Shank 6.0 to 6.4, head 15 at most, grip 7, receptacle room 32 x 13 x 9 | Assumed | Door hole 6.5, web hole 9, receptacle room | Caliper: the shank, the head, the grip range, the hole spacing and the depth of the receptacle |
| USB panel sockets | Flange 39 x 13 (A) and 28.2 x 8.7 (C). Flange thickness: not known. Body 32 behind the flange. | From a maker / estimated | Plate pockets, row pitch of 14, web 2.4 | Caliper: flange size and thickness, hole spacing, body length, cable diameter |
| Power button, 16 mm | Rim 19 x 2, nut 22, body 28, 45 clear behind | Estimated | Socket plate: flat face 22, depth behind the plate | Caliper on the bought button |
| Volume potentiometer and knob | Body 17 x 12, knob 18 x 15. Bushing length and the anti-rotation tab: not known. | Estimated | Socket plate: wall 2.4 at the hole, pocket of 19 | Caliper on the bought part |
| Push bolt spring | 4 outside, 22 free, about 1.2 N/mm. 5.8 shorter at the lock, 10.8 at the end of the stroke. | Estimated | Bolt stroke and gate | Caliper for the free length. Weights or a balance for the rate. |
| Speaker driver | Frame 51.8. Depth 28, basket 47, magnet 36: not verified. | From a maker (frame) / estimated | Driver seat, enclosure | Caliper on the bought driver |
| BC-250: standoff thread and centres | M3 assumed. Centres (51.85, 17.68), (82.25, 114.50), (277.45, 37.75), (292.25, 114.25). | Assumed / community model | Tray posts and screws | Thread gauge or a screw. Caliper from the I/O edge and the straight long edge. |
| BC-250: other | Heatsink variant, fin block size, DisplayPort centre height, 8-pin position | Community model | Shroud and duct | The lists in [hardware-envelopes.md](../research/hardware-envelopes.md) 2 and [bc250-cooling-and-psu.md](../research/bc250-cooling-and-psu.md) "Must measure or decide" |
| BC-250 on the first console | Board top face to the fan's outer face. Expected 74.6 to 75.3. | Estimated | Low priority: a design value now | Ruler, to the nearest 2 |
| Lever and buttons when they arrive | Sanwa drawing values | From a maker | Panel tiles | The list in `cad/out/shell-rev7/fit/warnings.md` (a build output) |
| Keyboard PCB when it arrives | GH60 form, 285 x 94.6 | From a maker | PC panel posts | Outline, holes, USB position, height of the lowest part |

## 3. To try on the bench before a print depends on it

Do these tests with the real parts. Write down each result. Send the results back.

| Test | What to do | What to record | What it decides | Source |
| --- | --- | --- | --- | --- |
| Audio, chain (A) | Connect the monitor's 3.5 mm output to the amplifier. Play a game sound. Change the monitor's volume. Stop the sound and listen at 0.5 m. Start a game with a high load and listen again. | Does the level change with the monitor's setting? Are the built-in speakers silent with the plug in? Hiss, hum, whine. | Chain (A) or (B) | [audio.md](../research/audio.md) 6 |
| Audio, chain (B) | Connect the USB sound adapter to a USB 2.0 port of the board. Select it. Do the checks of chain (A) again. | The same, and: does the sound go to the adapter while the picture is on the monitor? | The same | The same |
| Audio, start and shutdown | With each chain, start and shut down the system five times, with the knob at the usual position | Each pop | The chain | The same |
| Audio, supply of the amplifier | Compare the 12 V rail with a USB-A socket (5 V) of the charging hub | Whine in each case | The amplifier's supply | The same |
| Audio, hum | Only if a test has hum or whine: put a ground loop isolator in the signal lead | Hum with the isolator | The isolator | The same |
| Audio, idle clicks (chain B) | Stop all sound for one minute. Play a short sound. If it clicks, set `session.suspend-timeout-seconds = 0` and do it again. | Click or no click | Software setting | The same |
| Speakers, listening test | One pair of drivers in two test enclosures on the bench | Is the low end sufficient for the owner? | The hood band (no change, or a larger band) | [audio.md](../research/audio.md) 14 |
| Monitor, wake from sleep | Let the system put the monitor to sleep. Wake the system. | Does the picture come back with no press of the monitor's button? | Need of the push rod (it is in the default) | [monitor-cradle-and-bezel.md](monitor-cradle-and-bezel.md) "The power button of the monitor" |
| Monitor, the power it asks for | Put a USB-C power meter between the supplied adapter and the monitor. Read the label of the supplied adapter. | The voltage that the monitor asks for. The current at 0, 25, 50 and 100 % brightness. The label values. | Power part | [monitor-power-and-video.md](../research/monitor-power-and-video.md) 9 |
| Monitor, plain 5 V | Feed the monitor from a plain 5 V source of 3 A | Does it start? The brightness at which it flickers. | Power part | The same |
| Charging hub on the 12 V | Start the system ten times with the power button | Does the hub give its output with no button press? Does the BC-250 find the screen each time? | Power part | The same |
| Charging hub heat | Run the monitor at full brightness for one hour | Case temperature | Its place in free air | The same |
| Adapter with the lead | Connect the BC-250 through the adapter (in the board's socket) and the HDMI lead to the monitor | The mode (3840 x 2400 at 60 Hz or not). Does the sound work? | Video path | The same |
| Power button | Do the eight tests of the source: draw after a shutdown (ECO on and off), the board's own button with the jumper on 1-2 and 2-3, `TPMS1` pin 9, the adapter (10 starts and 10 shutdowns, a press while on, standby draw, rocker off and on), the hub on the 5 V | Each value in the list of the source | Power button wiring | [bc250-power-button.md](../research/bc250-power-button.md) 10 |
| Supply fan with ECO on | Load the system | The load at which the supply's fan starts | ECO switch on or off | [bc250-cooling-and-psu.md](../research/bc250-cooling-and-psu.md) "Must measure or decide" |
| USB hub and ports | Measure the 5 V at a board USB port, idle and with a controller that charges. Power the hub with its upstream plug out. Boot the board ten times cold with the hub and four devices in. Try both plug directions at each USB-C socket with a USB 3 drive and with a controller. | The 5 V values. The voltage on the upstream plug (it must be 0 V). Each boot. Each plug direction. | The hub, the sockets | [pc-panel-and-front-usb.md](../research/pc-panel-and-front-usb.md) "Must measure or test" |

## 4. To print first

Print in this order. The prints of stage 1 come before the coupons ([print-plan-abs.md](print-plan-abs.md) 6.1). The coupon plates are in [coupons.md](coupons.md), with the pass values and what changes if a coupon fails.

| Order | Print | What it proves | What to send back |
| --- | --- | --- | --- |
| T1 | Dry the filament | No bubbles and no strings | Pass or fail. The temperature and the time. |
| T2 | One layer of 250 x 250 with a brim of 5 | The reach of the nozzle and the first layer at the edges | Gaps or ridges at the four corners. The place of the purge lines. |
| T4 | The chamber | The temperature that the chamber holds | The temperature at 55 C and 60 C after one hour, and the time to get there |
| Plate 1 | Shrink bars `shrink-x`, `shrink-y` | The shrink for the slicer | The lengths at 115 and 230 on each bar, before and after the compensation. The shrink in % for X and Y. |
| Plate 2 | Warp: `warp-wall` A and B, `flat-strip` | Large ABS parts stay flat. The skin build. The shrink in Z. | The gap at each end and corner, the bow, the height of each wall. Cracks. The height at which a corner lifted. |
| Plate 3 | Holes, inserts, cone, push rod | The insert hole (5.6, 5.7, 5.8), the button holes, the lever mount, the power button hole, the USB cut-outs, the cone clearance, the rod fit | The largest drill shank in each hole. The iron temperature. The chosen insert hole (upright and level). Pass or fail of each hole. The chosen cone clearance and rod hole. The 250 N pull on a hood insert. Does the rod's travel of 2.0 turn the monitor on and off? |
| Plate 4 | Joint 1 pairs, clearance +0.1, +0.2, +0.3 | The groove clearance and the pilot hole | The chosen clearance. Pass or fail of the 2.4 hole after three drives. |
| Plate 5 | Weld pairs A, B, C and joints 2, 3, 5 | The weld, and the floor, foot and service seams | Where each weld pair broke and its work time. Pass or fail of each joint, and of the support face under the foot flange. |
| Plate 6 | The form: `facet45`, `cut-in`, `hand-hold`, edge bars | The 45 degree faces with no support, the bond in them, the edge break under paint | The chosen fan value. Pass or fail of each face. The cut-in depth. Thin paint on any edge. |
| Plate 7 | The floor tile | The 10 mm sandwich | The gap at each corner, the mass, the sag under 3.3 kg |
| Plates 8 and 9 | Finish pairs A to D and plaques P1 to P4 | The weld, the filler and the paint on ABS, over weeks | Does a seam or groove show at 1 m after 1 and 2 weeks and after the warm soak? Cracks round the insert. |
| Plate 10 | The latch: nose, frame strip, bolt, gate, strike, and the rear corner | The push bolt, the hook and the magnet pull | Pass or fail of each point of the plate. The pull of one magnet and disc at a gap of 0.3 with a spring balance (estimate 14.1 N with a steel disc). |
| Next | One hub saddle, on its side | The snap of the legs (2.0) in ABS | Cracks. Does it hold? |
| Next | Shroud air space: two plates, 10 and 21.5 | The air space above the fins | Temperatures in one fixed game |
| Next | First floor tile (front centre) and first wall piece (rear lower R) | Warp and size of the largest pieces | Lift of each corner and end. Length and width against the model. |

Stage 1 step T3 (bars of 200 and a post of 100) does the same work as plate 1 ([print-plan-abs.md](print-plan-abs.md) 6.1). The potentiometer hole (9.3, 9.4, 9.5) is in [audio.md](../research/audio.md) 7 and on no coupon plate yet.
