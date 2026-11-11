# PC control panel, cut plates and front USB ports

Research date: 2026-11-10. All dimensions in millimetres unless a unit is given.

These notes give the facts that the CAD needs for two decisions: four front USB ports in the
deck front face, and a PC control panel with a built-in 60% keyboard on a cut plate. No part
was bought. Every product is an example. Measure the real part before a part that touches it
is printed or ordered.

## Status tags

| Tag | Meaning |
| --- | --- |
| SOURCED [id] | Printed in the source listed under [Sources](#sources). |
| SOURCED (summary) | Read only in a search-result summary. The page itself was not read. |
| MEASURED-FROM-CAD | Read from a published CAD or source file. The file is named. |
| STANDARD | Fixed by a published specification. The specification is named. |
| ESTIMATED | Derived here. The method is given. |
| PROVISIONAL | A design choice proposed here. A test or the owner can change it. |

## Summary of recommendations

1. Use a self-powered hub for the front ports. Feed it from the ATX supply, not from the board.
   Connect it to one of the two USB 3.0 ports of the BC-250.
2. Connect the control panel directly to a USB 2.0 port of the BC-250. Do not put it on the hub.
3. Use screw-flange panel-mount sockets on short cables, in a removable printed socket plate.
   Thin the wall to 2.0 behind each socket. Use male-to-female USB-C extensions into real USB-C
   hub ports. Do not use USB-C female-to-female couplers.
4. Use a GH60-compatible hot-swap PCB under a 1.6 aluminium switch plate. Hold the PCB on
   printed posts at the standard holes. Keep 14 clear below the plate top.
5. Order cut plates from SendCutSend as DXF files. Order a small test coupon first.

---

## Part A. USB on the BC-250 and the front ports

### A1. What is known about USB on the BC-250

| Item | Value | Status |
| --- | --- | --- |
| Ports | 2 x USB 3.0 Type-A (stacked) and 2 x USB 2.0 Type-A (stacked), all on the I/O edge | SOURCED [B1][B3][B4] |
| Positions on the board | See `docs/research/hardware-envelopes.md` section 2, "Connectors" | MEASURED-FROM-CAD (existing notes) |
| USB-C port, DisplayPort alternate mode, Thunderbolt | None. "board doesn't have USB-C DisplayPort alt mode". | SOURCED [B1][B9] |
| Internal USB header | None documented. The connector reference lists M.2, jumpers, I2C, fan headers, power connectors, SPI flash, LPC/TPM and a debug footprint. It lists no USB header. | SOURCED [B2] (by absence) |
| Chipset | AMD A68H "Bolton-D2H" FCH, part 218-0844029 | SOURCED [B2] |
| What the chipset provides | 2 USB 3.0 ports, 10 USB 2.0 ports, 2 USB 1.1 ports | SOURCED (summary) [B12] |
| Which controller drives each port | "Ethernet and USB 2.0 run through" the A68H. The docs do not say which controller drives the two USB 3.0 ports. The FCH has exactly two USB 3.0 ports, so it is the likely source. | SOURCED [B4]; the USB 3.0 statement is ESTIMATED |
| Speed | USB 3.0 ports: 5 Gbit/s. USB 2.0 ports: 480 Mbit/s. "USB 3.0 port can handle external SSDs". | STANDARD (USB 3.0, USB 2.0); SOURCED [B1] |
| Source of the 5 V for USB | The board takes 12 V only. It makes its own 5 V with an on-board converter. | SOURCED [B1][B7] |
| Current limit, community statement | "rear USB 3.0 ports are specced for 5 W total". One user. No measurement was published. | SOURCED [B6] |
| Current limit, by specification | 0.5 A for each USB 2.0 port and 0.9 A for each USB 3.0 port | STANDARD (USB 2.0, USB 3.0) |

Known problems:

| Problem | Detail | Status |
| --- | --- | --- |
| Weak or dead 5 V rail | Some boards have no USB at all, also in the BIOS. The cause given is the 5 V rail. The repair is on the board. The workaround is a powered hub. One user powers a hub from the 5 V rail of the ATX supply and cut the 5 V wire from the board "to prevent back feeding". | SOURCED [B6][B11]; SOURCED (summary) [B13] |
| USB storage drops out under load | A 2.5 inch drive plus a dongle overloads the rear ports. Fix: power the drive from the supply. If it still drops, turn off autosuspend for that port: `echo on > /sys/bus/usb/devices/usbN/power/control`. | SOURCED [B6] |
| 2.4 GHz interference | The USB 3.0 ports jam wireless dongles that are plugged into them (Bluetooth lag, drop-outs). Fix: put the dongle on a USB 2.0 port or on a short extension, away from the I/O edge. | SOURCED [B5] |
| Slow or frozen boot with some devices | A USB device can stall enumeration at boot. One wireless adapter "froze the whole display when behind a case USB hub". It worked on a rear port. | SOURCED [B6] |
| Suspend | The board offers `s2idle` only. Resume is not reliable. The docs say: never let it suspend, and mask the sleep targets. USB wake-up is therefore not usable. A modified BIOS with S3 was reported in October 2026. It is experimental. | SOURCED [B8][B6][B14] |
| BIOS | Use the community P3.00 BIOS. P5.00_clv "may cause ReBAR/USB issues". | SOURCED [B10] |
| BIOS with hubs | A USB keyboard works in the BIOS on the board's own ports. No source says if a keyboard behind a hub works in the BIOS. | SOURCED [B5]; the hub case is not documented |

No kernel parameter for USB is required by the docs. The only kernel-level setting found is the
autosuspend switch above.

### A2. Will a hub with USB-C downstream ports work?

Yes. A hub is an ordinary USB device. The connector type of its downstream ports does not
matter to the board.

- Connect the hub to a USB-A port of the board with its own USB-A cable, or with a standard
  USB-A to USB-C cable if the hub has a USB-C upstream port. STANDARD (USB Type-C: legacy
  A-to-C cable).
- A USB-C downstream port on the hub gives USB data and 5 V. The speed is limited by the
  board: 5 Gbit/s on a USB 3.0 port, 480 Mbit/s on a USB 2.0 port.
- It gives no display output. The board has no alternate-mode source [B9].
- It gives no fast charging above 5 V. USB Power Delivery needs a hub with its own PD source.
  Controllers charge at 5 V.
- A controller with a USB-C socket works on such a port with a USB-C to USB-C cable.

### A3. Hub arrangement

Recommendation:

| Board port | Use | Reason |
| --- | --- | --- |
| USB 3.0, first | Front hub, four downstream ports | One cable from the compute module to the deck. A USB 2.0 hub also works here. |
| USB 2.0, first | Control panel (one cable) | No hub between the board and the keyboard. The keyboard works in the BIOS. |
| USB 2.0, second | Wireless dongle on a short extension, if one is used. If not, the marquee controller. | Dongles must stay off the USB 3.0 ports [B5]. |
| USB 3.0, second | Spare: service port, USB audio, or the marquee controller | - |

Port count: four front ports, one control panel, one marquee controller, one spare. That is
seven. The split above needs a four-port hub only. A seven-port powered hub on one USB 3.0
port is the alternative if the board ports must stay free. ESTIMATED from the roadmap list.

Use a self-powered hub:

- The board's 5 V is the weakest known part of its USB [B6].
- Four controllers that charge can draw 4 x 0.9 A = 3.6 A, which is 18 W. STANDARD limits;
  ESTIMATED total. The community figure for the board is 5 W for both USB 3.0 ports [B6].

Power for the hub from the ATX supply, with off-the-shelf parts:

| Method | Parts | Notes | Status |
| --- | --- | --- | --- |
| 5 V hub on the 5 V rail | A hub with a 5 V barrel input, and a "SATA 15-pin to DC 5.5 x 2.1" cable in the 5 V version | These cables are sold in a 5 V and a 12 V version. Buy the 5 V version. Check the plug size and the polarity against the hub. Many small hubs use 3.5 x 1.35. Listings give 24 AWG wire, 180 long. | SOURCED (summary) [U14] |
| 12 V hub on the 12 V rail | A hub that accepts a wide DC input, and a SATA or Molex to barrel cable in the 12 V version, or a Molex pigtail into a terminal block | Coolgear hub boards accept 7 to 14 V on a 5.5 x 2.5 barrel. StarTech ST7300USBME accepts 7 to 48 V on a terminal block. | SOURCED [U11]; SOURCED (summary) [U12] |
| Current available on one SATA lead | 4.5 A at 5 V (three contacts at 1.5 A) | Enough for four ports at 0.9 A. Use a Molex lead for more. | STANDARD (Serial ATA power connector) |

The 5 V rail of the supply is on when the supply is on. The board then also runs. The hub and
the board start together.

Risk: a cheap powered hub can feed its 5 V back into the board through the upstream cable.
Measure the voltage on the hub's upstream plug with the hub powered and the plug disconnected.
It must be 0 V. ESTIMATED risk; one user reports the same concern (summary) [B13].

Test before the deck is printed: boot the board ten times with the hub connected and all four
ports in use. See the boot problem in A1.

### A4. Front socket hardware

The wall is 5 thick and about 31 tall. Two facts decide most of this section:

1. Screw-flange sockets and bare hub connectors mate fully only through a panel of 2.5 or less
   [U6][U7]. A keystone latch needs a ledge of about 1.5, and 2.0 at most [U4]. A plain 5 wall
   fits none of them. The wall must be thinned from behind, or it must carry a printed receptacle.
2. A USB-C female-to-female coupler works in only half of the plug orientations. A plug carries
   one CC wire. In a cable, coupler, cable chain the two CC wires meet only when the two plugs
   are aligned. "Even a flawlessly built coupler hands every user a coin flip." [U5]

#### Option 1: keystone modules

| Item | Value | Status |
| --- | --- | --- |
| Module face | 14.5 wide x 16.0 high | SOURCED [U1] |
| Port cut-out, sheet-metal mountings | 14.9 x 19.2 | SOURCED [U2] |
| Module width behind the face | USB 2.0 A coupler 16.8. USB 3.0 A coupler 17.3. USB 3.0 A with cable 17.8. | SOURCED [U2] |
| Ledge thickness that the latch clips to | 1.5 in steel patch panels. In a printed panel, 2.5 was too thick and 2.0 was "barely" tolerated. A test ladder used 1.3, 1.5 and 1.7. | SOURCED (summary) [U4] |
| Printed receptacle, community model | Front opening 14.9 x 16.3, 3.0 deep. Behind it the cavity is 14.9 x 24.4. Receptacle depth 9.7. Catches 1.3 to 1.4 deep. Outer block 19.9 wide x 27.5 high. | MEASURED-FROM-CAD [U3] (`KeystoneJack.scad`, read as text) |
| Formal standard | None found. The dimensions are a de facto standard. | - |
| Pitch for four in a row | 20.0 | ESTIMATED: 17.3 module + 2.7 wall |
| Row width, four ports | 80 | ESTIMATED: 3 x 20 + 19.9 |
| Fit in the wall | The receptacle is 27.5 high in a 31 wall. It needs a boss 9.7 deep, so 4.7 more than the wall. | ESTIMATED |
| Depth behind the wall, coupler plus straight plug | About 80 | ESTIMATED: 26 coupler behind the face (listing gives 29 x 16 x 15 overall [U17]) + 30 plug overmould + 25 cable bend |
| Depth behind the wall, module with its own cable | About 65 | ESTIMATED from the product photo [U8]: 38 body and strain relief + 25 bend |
| USB 3 speed | USB-A coupler: only with a USB 3 A-to-A cable behind it, which is not a standard cable. A module with a fixed A plug avoids this. | ESTIMATED from the connector definitions; [U2] lists such a module |
| USB-C orientation | Female-to-female coupler: not kept. See fact 2. Male-to-female keystone extension into a USB-C hub port: kept. | SOURCED [U5] |

Products: DataPro 1673 keystone USB-C extension, male to female, 10 Gbit/s, 300 long,
USD 19.95, in stock on the research date [U8]. Delock 86399 keystone USB-C female to USB-C
male, 5 Gbit/s, 250 long [U16] (stock in the USA not confirmed). Tripp Lite U325-000-KP-BK
USB 3.0 A coupler [U18] and generic USB-C couplers such as BERLAT [U17] (listings not
confirmed as currently sold; the USB-C coupler type is not recommended).

#### Option 2: screw-flange panel-mount sockets on a cable

| Item | USB-A (DataPro 1698) | USB-C (DataPro 1678) | Status |
| --- | --- | --- | --- |
| Cut-out | 14.7 x 7.3, corner radius 1.6 | 10.5 x 4.6, corner radius 2.0 | SOURCED [U6][U7] (cut-out drawings on the product pages) |
| Flange holes | 2 x diameter 3.2, 30.0 apart | 2 x diameter 3.2, 20.0 apart | SOURCED [U6][U7] |
| Space needed behind the panel | 39 x 13 | 28.2 x 8.7 | SOURCED [U6][U7] |
| Screws | 4-40, into nuts embedded in the flange | Same | SOURCED [U6][U7] |
| Panel thickness for full mating | 2.5 maximum | 2.5 maximum | SOURCED [U6][U7] |
| Speed | Tested to 10 Gbit/s | 10 Gbit/s (USB 3.x) | SOURCED [U6][U7] |
| Shortest cable | 150 (6 inch), USD 16.45 | 150 (6 inch), USD 19.45 | SOURCED [U6][U7]; in stock on the research date |
| Body and strain relief behind the flange | About 30 | About 32 | ESTIMATED: scaled from the product photos against the flange width. The dimension drawings need an account. |

The same hole spacing is used by a second vendor: Adafruit 908 (USB-A, M3 screws 30 apart) and
Adafruit 4053 (USB-C socket to USB-A plug, M3 screws 20 apart) [U10]. Treat 30 and 20 as the
common pattern. Both Adafruit parts are USB 2.0.

- USB 3 speed: kept by the DataPro parts.
- USB-C orientation: kept, if the socket is a male-to-female extension with all pins wired and
  its plug goes into a real USB-C port of the hub. The plug then behaves as if it were inserted
  directly. ESTIMATED from the connector wiring and [U5]. Test both orientations of each socket
  on arrival.
- A USB-C socket on a USB-A plug (Adafruit 4052 and 4053, or DataPro 1679 reversed) is simpler.
  It needs only USB-A hub ports. At USB 2.0 both orientations work. At USB 3 speed only one
  orientation can carry the fast lanes; the other falls back to USB 2.0. ESTIMATED from the
  pin-out; [U5] measured this fall-back.
- Right-angle versions exist: "Panel Mount USB-C Extension Cable Right Angle" and "Panel Mount
  USB 2.0 Right Angle Down Extension Cable" [U9]. Their dimensions were not read.

No-screw variant, USB 2.0 only: Adafruit snap-in cables [U10].

| Part | Cut-out | Panel thickness | Bezel on the outside |
| --- | --- | --- | --- |
| 4052, USB-C socket to USB-A plug, 300 long | 21.8 x 10.9 | up to 5 | 28 x 16 x 2.7 |
| 4055, USB-A extension, 300 long | 26.5 x 12.3 | up to 4 | 28 x 18 x 4 |

Round-hole variant: Adafruit 6069, USB-C male to female, hole 12 to 18, panel up to 13 thick.
Adafruit 4218, hole 21.5 to 27, panel up to 16, nut diameter about 29.5 [U10]. The number of
wired pins is not stated.

All Adafruit parts above showed "In Stock" on the research date.

#### Option 3: a hub board with no shell, behind a slot

| Item | Value | Status |
| --- | --- | --- |
| Example | Coolgear CG-817X2CX2AX1C-PD-PCBA: bare board, 2 x USB-C and 2 x USB-A downstream at 5 Gbit/s, USB-C upstream, VL817 hub | SOURCED [U11] |
| Size | 44.5 x 38.1 x 19.1 (1.75 x 1.5 x 0.75 inch) | SOURCED [U11] |
| Power | 7 to 14 V DC, barrel 5.5 x 2.5, centre positive. No bus power. Up to 2 A for each port. | SOURCED [U11] |
| Price and terms | USD 70.29, in stock on the research date. Sold as a development product, "as-is" and not returnable, shipped in the USA only. | SOURCED [U11] |
| Cut-out | One slot for the connector group, about 45 x 17 | ESTIMATED from the board size. The port layout was not confirmed. A 3D model is offered on the product page. |
| Depth behind the wall | 38 for the board, if the cables leave sideways. More if the upstream or power connector is on the rear edge. | ESTIMATED |
| USB 3 speed and USB-C orientation | Both kept. There is no extra junction. | ESTIMATED |

The same vendor sells a four USB-A version (CG-817X4AX1C-PD-PCBA, 47.8 x 40.1 x 18.3,
USD 74.29) and a cased hub with two USB-C and two USB-A downstream ports (CG-4P31CHUB,
152 x 62.5 x 30, USD 141.29) [U11]. A retail hub with its shell removed is the cheap form of
this option. Its connector spacing is then fixed by that hub.

Costs of this option: one source, a slot that fits one board only, and plug forces that go into
the solder joints unless the printed cradle supports the connector shells. The wall must be
about 1.5 at the slot so that the plugs seat.

#### Comparison

| | Keystone | Screw-flange on a cable | Bare hub board |
| --- | --- | --- | --- |
| Cut-out | 14.9 x 16.3 opening in a 19.9 x 27.5 receptacle | 14.7 x 7.3 and 10.5 x 4.6, two holes each | One slot, about 45 x 17 |
| Row width for four | 80 | 150 | 45 |
| Clear depth behind the wall | 65 to 80 | 60. About 50 if the cable turns at once. | 40 to 45 |
| USB 3 speed | With the right module | Yes | Yes |
| USB-C orientation | Only with a male-to-female module | Yes, into a USB-C hub port | Yes |
| Fit in a 5 x 31 wall | Tight. Needs a 9.7 deep boss. | Good. Needs a pocket that leaves 2.0. | Good. Needs a 1.5 web and a cradle. |
| Replace a socket later | Snap out | Two screws | Replace the hub |

#### Recommendation

Use screw-flange sockets on short cables (option 2), mounted from behind in a small removable
printed socket plate. The hub stays whole and hidden. Reasons:

- The cut-outs are published and two vendors share the hole pattern.
- The sockets are low. They leave more of the 31 wall than a keystone receptacle.
- USB 3 and both USB-C orientations work with male-to-female parts and a hub that has two
  USB-C and two USB-A downstream ports.
- A socket plate that is separate from the deck can be reprinted when the hardware changes.

If the owner accepts USB 2.0 on the front ports, the Adafruit snap-in cables are the simplest
choice. They need no screws and no thinned wall for USB-C. They need USB-A hub ports only.

Option 3 is the fallback if the clear depth behind the wall is less than 50.

### A5. Numbers for the CAD

Recommended option, screw-flange sockets:

| Parameter | Value | Status |
| --- | --- | --- |
| USB-A cut-out, as sourced | 14.7 x 7.3, radius 1.6 | SOURCED [U6] |
| USB-A cut-out, as printed | 15.1 x 7.7 | PROVISIONAL: 0.2 added on each side. Print a coupon. |
| USB-C cut-out, as sourced | 10.5 x 4.6, radius 2.0 | SOURCED [U7] |
| USB-C cut-out, as printed | 10.9 x 5.0 | PROVISIONAL |
| Flange holes | USB-A: 2 at +/-15.0 from the socket centre. USB-C: 2 at +/-10.0. Print at diameter 3.4. | SOURCED [U6][U7]; the print diameter is PROVISIONAL |
| Web left in front of the flange | 2.0 | PROVISIONAL: below the 2.5 limit [U6][U7] |
| Pocket behind the wall, USB-A | 41 x 15, 3.0 deep | ESTIMATED: 39 x 13 + 1 on each side; 5.0 - 2.0 |
| Pocket behind the wall, USB-C | 30.2 x 10.7, 3.0 deep | ESTIMATED: 28.2 x 8.7 + 1 on each side |
| Socket order | A, C, A, C | PROVISIONAL: gives one pitch |
| Centre-to-centre pitch | 38.0 | ESTIMATED: 20.5 + 15.1 + 2.0 rib = 37.6, rounded up |
| Row width over the pockets | 150 | ESTIMATED: 3 x 38 + 20.5 + 15.1 |
| Pitch if the order is A, A, C, C | 43, 38, 33 | ESTIMATED |
| Height of the socket centre line | Mid-height of the vertical wall | PROVISIONAL. The tallest pocket is 15. |
| Clear depth behind the inner wall face | 60 | ESTIMATED: 32 body + 25 cable bend (5 x a 5 cable), rounded up |
| Clear depth in front of the wall | 45 for a plug and its cable | ESTIMATED: 12 plug shell + 30 overmould |
| Plug overmould to clear on the outside | USB-A 16 x 8 maximum. USB-C about 12.35 x 6.5. | USB-A: SOURCED (summary) [U15]. USB-C: ESTIMATED, recalled from the USB Type-C specification and not re-read. |

The keep-out zone behind the wall is under the control panel. Check it against the button
terminals of the arcade panel, which reach 34.5 below the panel top
(`docs/research/controls-ergonomics.md` section 2.1).

Reference numbers for the other options:

| Option | Cut-out | Pitch | Clear depth behind the wall |
| --- | --- | --- | --- |
| Keystone | 14.9 x 16.3 front, 14.9 x 24.4 rear, receptacle 9.7 deep | 20 | 80 with a coupler, 65 with a cabled module |
| Adafruit snap-in | USB-C 21.8 x 10.9. USB-A 26.5 x 12.3. Thin the wall to 4.0 for USB-A. | 32 | 60 (body length not published; same estimate) |
| Bare hub board | About 45 x 17. Confirm on the part. | - | 45 |

---

## Part B. The keyboard plate and cut plates

### B1. Switch plate facts

| Item | Value | Status |
| --- | --- | --- |
| Switch cut-out | 14.0 x 14.0, tolerance +/-0.05 (0.551 +/-0.002 inch) | SOURCED [K1] |
| Corner radius of the cut-out | 0.3 maximum (0.012 inch) | SOURCED [K1] |
| Plate thickness | 1.5 +/-0.1 (0.06 +/-0.004 inch) | SOURCED [K1] |
| Key pitch | 19.05 (0.75 inch) | SOURCED [K2] ("Standard is 19.05mm") |
| Plate top to PCB top | 5.0, tolerance +0.3 (0.197 +0.012 inch) | SOURCED [K1] |
| PCB thickness | 1.5 +/-0.15 in the data sheet. 1.6 for the GH60 and for current PCBs. | SOURCED [K1][K4] |
| Switch housing | 15.6 x 15.6. Housing top 6.6 above the plate top. | SOURCED [K1] (11.6 less 5.0) |
| Stem top, not pressed | 10.2 above the plate top | SOURCED [K1] (housing 6.6 plus stem 3.6) |
| Pins below the PCB top face | 3.3 | SOURCED [K1] |
| Travel | 4.0 (0.16 inch) | SOURCED [K1] |
| Hot-swap socket, Kailh CPG151101S11 | 1.80 +/-0.05 below the PCB. 3.10 over all with the bosses that sit in the PCB. 14.5 long. | SOURCED [K3] |
| 60% key block | 15u x 5u = 285.75 x 95.25 | STANDARD (15 and 5 times 19.05); SOURCED [K5] |

Stabiliser cut-outs. The switch centre is the origin. Positive Y is away from the user for a
key in the normal orientation. Spacebar stabilisers are often turned by 180 degrees; follow
the PCB.

| Item | Value | Status |
| --- | --- | --- |
| Stabiliser centres, 2u, 2.25u and 2.75u keys | +/-11.94 (0.94 inch over all) | SOURCED [K1][K2] |
| Stabiliser centres, 6.25u key | +/-50.0 | SOURCED [K2]; SOURCED (summary) [K8]. The Cherry table has no 6.25u entry. |
| Stabiliser centres, 7u key | +/-57.15 (4.5 inch over all) | SOURCED [K1][K2] |
| Cherry specification opening, for each stabiliser | 6.65 wide x 12.29 high (0.262 x 0.484 inch). Top edge at Y +5.69, bottom edge at Y -6.60. | SOURCED [K1]; the Y positions are from [K2], which implements the data sheet |
| Wire tab at the bottom | 3.05 wide, down to Y -7.77 | SOURCED [K1][K2] |
| Side notch | 0.86 deep in [K2] (0.81 in the data sheet), from Y -0.51 to Y +2.29 | SOURCED [K1][K2] |
| Simplified opening, "MX Basic" | 7.0 wide, from Y +6.0 to Y -9.0 | SOURCED [K2] |
| Simplified opening, "Tight Fit" | 6.75 wide, from Y +6.0 to Y -8.0 | SOURCED [K2] |
| Plate-mount stabiliser | Clips into the plate. Needs the 1.5 plate and the Cherry opening or the tight opening. | SOURCED [K1][K2] |
| PCB-mount stabiliser | Fixed to the PCB. The plate needs clearance only. The simplified opening is enough. | SOURCED [K1] ("Spacebar without frame"); the clearance statement is ESTIMATED |
| PCB holes for a PCB-mount stabiliser | Diameter 4.0 and diameter 3.05, 15.24 apart. The upper hole is 6.99 above the switch centre. | SOURCED [K1] |
| Narrowest web, switch cut-out to simplified stabiliser opening | 1.44 | ESTIMATED: 11.94 - 7.0 - 3.5 |

Vertical stack, from the plate top downward:

| Layer | Thickness | Running depth below the plate top | Status |
| --- | --- | --- | --- |
| Plate top to PCB top | 5.0 | 5.0 | SOURCED [K1] |
| PCB | 1.6 | 6.6 | SOURCED [K4] |
| Hot-swap sockets | 1.8 | 8.4 | SOURCED [K3] |
| Worst case of the three | - | 9.0 | ESTIMATED: 5.3 + 1.75 + 1.95 |
| USB-C receptacle under the PCB, rear left | about 3.2 | 9.8 | ESTIMATED: shell 3.16 high with its centre 1.58 below the PCB [K5] |
| USB-C plug overmould | - | 11.5 | ESTIMATED: centre 1.58 below the PCB plus half of 6.5 |

- **Depth that a hot-swap 60% PCB needs below the plate top: 8.4 nominal, 9.0 worst case, and
  11.5 where the USB plug is.**
- **Design value: keep 14 clear below the plate top over the PCB area.** ESTIMATED: 9.0 plus
  2.0 of air plus a 3.0 printed floor. The deck has 56.

Key top height above the plate top:

| Keycap | Height above the plate top | Status |
| --- | --- | --- |
| Lower edge of a keycap, not pressed | 5.9 | ESTIMATED: the data sheet shows 0.43 inch above the PCB top; the reading of that dimension is an interpretation |
| Lower edge of a keycap, pressed | 1.9 | ESTIMATED: 5.9 less 4.0 travel |
| Cherry profile, by row | Row E (numbers) 15.8. Row D 13.7. Row C (home) 12.9. Row B 13.8. | ESTIMATED: data sheet heights of 0.82, 0.736, 0.704 and 0.74 inch above the PCB top, less 5.0 [K1] |
| OEM profile, tallest row | about 17.8 | ESTIMATED: 5.9 plus the published 11.9 [K6] |
| SA profile, tallest row | about 22.4 | ESTIMATED: 5.9 plus 16.5 [K6] |
| XDA and DSA (uniform) | about 15.0 and 13.5 | ESTIMATED: 5.9 plus 9.1 and 7.6 [K6] |

- **Key tops are 13 to 16 above the plate top with Cherry-profile keycaps, and up to 22 with SA.**
- If the plate top is 6.0 below the top of the panel frame, the lower edges of the keycaps are
  level with the frame. The frame opening must then be at least 286.8 x 96.3. PROVISIONAL:
  the key block plus 0.5 on each side.

### B2. The GH60 form factor

All positions are from the rear left corner of the PCB, seen from the switch side. X is to the
right. Y is toward the user.

| Item | Value | Status |
| --- | --- | --- |
| Outline | 285.0 x 94.6, corner radius 2.0, thickness 1.6 | MEASURED-FROM-CAD [K4] (`keyboard.kicad_pcb`, revision B, edge-cut lines) |
| Position of the key block on the PCB | Centred. The block overhangs the PCB by 0.375 at the left and right and by 0.325 at the rear and front. | MEASURED-FROM-CAD [K4] (switch positions) |
| Centre of the Esc key | (9.15, 9.20) | MEASURED-FROM-CAD [K4] |
| Hole H1, rear left | (25.2, 27.9), round, diameter 2.5 | MEASURED-FROM-CAD [K4]; agrees with [K5] |
| Hole H2, centre | (128.2, 47.0), slot 5.0 x 2.5 | MEASURED-FROM-CAD [K4]; agrees with [K5] |
| Hole H3, front right | (190.5, 85.2), slot 5.0 x 2.5 | MEASURED-FROM-CAD [K4]; agrees with [K5] |
| Hole H4, rear right | (260.05, 27.9), slot 5.0 x 2.5 | MEASURED-FROM-CAD [K4]; agrees with [K5] |
| Edge slots H5 and H6 | Open slots 2.5 wide at Y 56.5. The slot ends are at X 3.71 and X 281.29. | MEASURED-FROM-CAD [K4]; agrees with [K5] |
| Copper pad around each hole | Diameter 7.0 | MEASURED-FROM-CAD [K4]. A support post must be 7.0 or less. |
| Screw | M2 | ESTIMATED: the holes are 2.5 |
| USB connector | On the rear edge, under the PCB. Centre at X 18.2 on the GH60 (Mini-B). USB-C on current PCBs is at X 18.2 to 18.7. | MEASURED-FROM-CAD [K4]; SOURCED [K5] |
| Case opening for a USB-C plug | 17 x 10.5, centre at X 18.5 and 1.75 below the PCB bottom face | SOURCED [K5] (a design proposal in that article; not tested there) |

Differences between "GH60-compatible" PCBs [K5]:

- Outlines run from 283 x 94 to 285 x 95.1. Design the PCB bay as 286.2 x 96.3.
- H2 is 0.3 nearer the front on some PCBs. Some PCBs have no H3. Make the posts for H2 and H3
  removable, or leave them as plain supports with no screw.
- PCBs for gasket-mount cases (for example the bakeneko-60) have no tray holes. They carry a
  JST connector for a USB daughterboard instead of a USB socket.

Currently sold hot-swap ANSI 60% PCBs:

| PCB | Evidence | Status |
| --- | --- | --- |
| KBDfans DZ60RGB-ANSI v2 | USD 55.00, "Add to cart" shown on the research date. Hot-swap, USB-C, VIA, 3-pin and 5-pin MX switches. Listed as compatible with the Tofu60 tray-mount case. | SOURCED [K7]. The hole pattern is not stated on the page; it follows from the case list. CONFIRM on the part. |
| KBDfans DZ60RGB v2 | USD 55.00. 63-key layout with arrow keys. Hot-swap, USB-C. | SOURCED (summary) [K7] |
| KBDfans Redux 60 RGB ANSI | USD 35.00. Hot-swap, USB-C, 1.6 thick. | SOURCED (summary) [K7]. Mounting holes not confirmed. |
| KPrepublic BM60 RGB | Sold as "60% gh60 hot swappable PCB ... type c" | SOURCED (summary) [K7]. Stock not confirmed. |

A hot-swap PCB has one fixed layout. Draw the plate from the layout file of the PCB that is
bought, with its stabiliser positions and orientations.

How to hold the PCB under a custom plate:

| Method | How it works | What the printed frame must give |
| --- | --- | --- |
| Tray mount (recommended) | M2 screws through the standard holes into printed posts. The plate is fixed to the same frame. | A seat for the plate. Posts at H1 to H4, 7.0 diameter or less, with M2 heat-set inserts. Post tops 5.0 below the plate seat for a 1.6 plate and a 1.6 PCB (ESTIMATED: 5.0 + 1.6 - 1.6). A floor at least 2.5 below the post tops, for the sockets. An opening for the USB plug at the rear left, or a short internal cable. |
| Plate mount | The PCB hangs from the switches. Nothing else holds it. | A seat and screws for the plate. An open bay 14 deep. |

Reasons for the tray mount: on a hot-swap PCB only the socket contacts hold the PCB to the
switches. Each switch that is pushed in pushes the PCB down. Posts take that load. The plate
seat and the post tops are in one printed part, so one printed height sets the 5.0 distance.
The slots give sideways play. If the plate mount is chosen, add printed pads 0.3 to 0.5 below
the PCB as a backstop. ESTIMATED; no source compares the two for a printed frame.

### B3. Mail-order cutting services

SendCutSend (USA):

| Item | Value | Status |
| --- | --- | --- |
| Files | DXF preferred. DWG, AI, EPS, STEP also accepted. SVG is not on the list. | SOURCED [C1] |
| Tolerance, laser | +/-0.13 (0.005 inch) on parts under 305 (12 inch). +/-0.25 (0.010 inch) on larger parts. | SOURCED [C1] |
| Kerf | Compensated by the service. "design your part exactly as you'd like it to turn out". | SOURCED [C1][C8] |
| Smallest internal hole, laser | 50% of the material thickness | SOURCED [C1] |
| Smallest and largest part, aluminium | 6.4 x 9.5 to 1118 x 1727 | SOURCED [C2] |
| Order minimum | No minimum quantity. Free shipping in the USA from USD 39. | SOURCED [C7] |
| Lead time | 2 to 4 days for 5052 aluminium. Finishing adds 1 to 7 days. | SOURCED [C2][C6] |
| 5052-H32 aluminium | 1.02, 1.60, 2.03, 2.29, 2.54, 3.18, 4.75 and thicker | SOURCED [C2] |
| 6061-T6 aluminium | 1.02, 1.60, 2.03, 2.54, 3.18, 4.75 and thicker | SOURCED [C3] |
| Other sheet materials | Mild steel 0.76 to 3.4 and thicker. Stainless steel, acrylic, polycarbonate, G10/FR4 and carbon fibre have pages. Their thickness lists were not read. | SOURCED [C13] for mild steel; the other pages are linked from [C2] |
| Anodising | Aluminium from 1.60. Clear, black, blue, gold, red. Largest part 584 x 584. The part needs one hole of 1.6 or more. | SOURCED [C6] |
| Powder coating | Offered for 5052 from 1.60 | SOURCED [C2] |
| Tapping | M2 to M10. Offered for 5052 from 1.60. Draw the hole; the service resizes it. | SOURCED [C2][C5] |
| Countersinking | 82 and 90 degrees. Depth at most 60% of the thickness. Accuracy +/-0.38. For 5052 it is offered from 3.18 only. Draw the small hole only. | SOURCED [C2][C4] |
| Bending, deburring, press-in hardware (nuts, studs, standoffs) | Offered for 5052 from 1.60 | SOURCED [C2] |
| Price for one 396 x 240 plate | Not obtained. A quote needs an upload in an account. | INACCESSIBLE |
| Price, rough | USD 35 to 70 for a 396 x 240 aluminium plate with holes. USD 30 to 50 for a 60% switch plate. Anodising extra. | ESTIMATED: the price examples for small parts start at USD 19.51 [C7]; a European keyboard-plate service starts at EUR 27 [C11]. Get a quote before any decision that depends on price. |

Alternatives:

| Service | Facts read | Status |
| --- | --- | --- |
| OSH Cut (USA) | Files: DXF, SVG, AI, STEP and others. Standard tolerance +/-0.13. Tapping from M3. Countersinking at 82 and 90 degrees. Powder coating. Anodising was not listed. | SOURCED [C9] |
| Fabworks (USA) | Files: DXF or STEP. No order minimum. Steel, stainless steel and aluminium. Countersinking, tapping, hardware, powder coating. | SOURCED [C10] |
| LaserBoost (Spain) | A keyboard-plate service. "Your Plate from 27 EUR", no order minimum, production in 48 hours. Aluminium, stainless steel, brass, copper. Shipping cost and duty to the USA were not read. | SOURCED [C11] |

Are 14.0 cut-outs cut reliably?

- The stated tolerance is +/-0.13. The Cherry tolerance is +/-0.05. The service does not
  promise the Cherry tolerance. SOURCED [C1][K1].
- Laser-cut plates are common in the keyboard hobby, and services sell them as a product
  [C11][C12]. No statement about switch fit in SendCutSend plates was found.
- Draw the cut-outs at 14.00 with no kerf offset, because the service compensates the kerf.
  The plate generator has a kerf setting for services that do not: "Positive values yield
  smaller cutouts" [K2]. Do not compensate twice.
- A 60% plate that is 304 or shorter stays in the tighter tolerance class. ESTIMATED from the
  rule in [C1].
- Order a test coupon first: a 3 x 3 block of switch cut-outs, one 2u stabiliser, one hole of
  30 and one of 24. PROVISIONAL.

Material and thickness:

| Plate | Choice | Reason | Status |
| --- | --- | --- | --- |
| Keyboard switch plate | 5052-H32 aluminium, 1.60, anodised | 1.60 is the upper limit of 1.5 +/-0.1. Anodising and tapping are offered at this thickness. | PROVISIONAL |
| Arcade panel top, with a clear cover | 5052-H32 aluminium, 2.03, plus a 1.5 cover. Total 3.5. | Inside the 3.9 limit of the snap-in buttons. | PROVISIONAL |
| Arcade panel top, bare | 5052-H32 aluminium, 3.18, anodised or powder coated | Inside both button limits. The only thickness in this range with countersinking. | PROVISIONAL |
| Stiffness check | 2.1 aluminium bends like 1.5 steel. Arcade panels use 1.2 to 1.5 steel. | ESTIMATED: thickness cubed times the modulus, 70 against 200 GPa. Steel figure from `docs/research/controls-ergonomics.md` section 6.1 |

What to put in the drawing:

1. One DXF for each part, at scale 1:1, in millimetres.
2. Closed outlines only: the outer profile and every cut-out, at nominal size.
3. No dimensions, text, centre lines, title block or duplicate lines.
4. Holes of at least half the thickness. Webs of about one thickness or more.
5. Corner radius 0.3 on switch cut-outs. Radius 0.5 or more elsewhere.
6. Tapped holes drawn as plain holes. Choose the thread in the order form.
7. Countersunk holes drawn as the small hole only. Choose the side in the order form.
8. A separate drawing with dimensions for the owner's own check. Do not upload it.

### B4. The arcade panel as a cut plate

| Item | Value | Status |
| --- | --- | --- |
| Sanwa OBSF-30 snap-in, panel thickness | 3.9 maximum (Sanwa shop). 3.7 maximum (Tops). Slagcoin gives 2 to 4. | CONFIRMED: SOURCED in `docs/research/controls-ergonomics.md` section 2.1; SOURCED [A1] |
| Sanwa OBSN-30 screw-in, panel thickness | 5 maximum (Sanwa). Slagcoin gives 0 to 8. | CONFIRMED: same sources |
| Design value for snap-in buttons | 3.0 to 3.5 in total, including a cover | From the existing notes |
| Button holes | Diameter 30 and 24. With a +/-0.13 service tolerance, draw 30.1 and 24.1 and test on the coupon. | SOURCED [A1]; the drawn size is PROVISIONAL |
| Lever hole in the panel | Diameter 24 | SOURCED [A1] |
| How a Sanwa lever mounts under a metal panel | The flat plate of the lever hangs from four M4 fixings on a 40 x 85 pattern. Metal arcade panels have studs fixed to the underside, so nothing shows on top. The Vewlix panel has M4 studs 10 long. | SOURCED [A1] ("bolts soldered or welded to the bottom"); `docs/research/controls-ergonomics.md` sections 1.2 and 6.1 |
| Ways to get the four fixings on a cut plate | 1. Press-in M4 studs, fitted by the service. 2. Countersunk M4 screws from the top, under the artwork and the cover. This needs a 3.18 plate. 3. Tapped M4 holes in a 3.18 plate, screws from below. | ESTIMATED from [C2][C4][C5]. The stud sizes in the hardware catalogue were not read. |
| Clear cover with artwork | Common. "cover with artwork then a sheet of clear plexi on top". Metal arcade panels "often use this with acrylic glass". | SOURCED [A1]; SOURCED (summary) [A3] |
| Cover thickness | 1.5 when it only protects the artwork. 3 when it carries load. Retail fight sticks use about 3. | SOURCED (summary) [A3] |
| Cover on this panel | 1.5 polycarbonate or acrylic on a 2.03 plate | PROVISIONAL: the total stays below 3.9 |

The cover can be cut from the same drawing by the same service, in acrylic or polycarbonate.
Sanwa asks for a small chamfer on button holes in acrylic (existing notes, section 2.1).

### B5. Small pointing devices

The space beside a 60% key block in the 396 opening is about 110 wide.

| Device | Size | Interface | Notes | Status |
| --- | --- | --- | --- | --- |
| Perixx PERIPAD-501 II touchpad | 86 x 75 x 11 | USB, standard mouse device, two buttons | Fits whole in a pocket in the panel. | SOURCED (summary) [D3]. Stock not confirmed. |
| Azoteq TPS65 touchpad module | 65 x 49 | I2C, 6-pin flat cable | Needs a controller. QMK has a driver. Multi-touch. | SOURCED (summary) [D2]; SOURCED [K9] |
| Azoteq TPS43 touchpad module | 43 x 40 | I2C | Same | SOURCED (summary) [D2]; SOURCED [K9] |
| Cirque GlidePoint circle trackpad | Diameter 40, 35 or 23. The 23 size is 5.05 thick. | I2C or SPI | Needs a controller. QMK has a driver. | SOURCED [D1][K9] |
| Ploopy Trackpad | Not confirmed. The shipping size is 190 x 140 x 20. | USB, runs QMK | Open hardware. Probably too large for the space. | SOURCED [D4] |
| Ploopy trackballs (Nano 2, Adept) | Not confirmed. The Adept ships in 130 x 130 x 60. | USB, runs QMK | Open hardware. The sensor board and ball could be built into the panel. | SOURCED [D4] |
| Pimoroni Trackball Breakout | Not read | I2C | Thumb-size ball. QMK has a driver. | SOURCED [K9]; the product page was INACCESSIBLE |
| Ultimarc U-Trak arcade trackball | 2.25 inch ball. Panel up to 19 thick. | USB version offered | Out of stock on the research date. Body depth not read. Probably too large. | SOURCED [D5] |

Two types exist:

- A complete USB device. It needs a second USB connection in the panel. Put a small USB 2.0
  hub inside the panel so that the panel keeps one cable.
- A bare I2C or SPI module. It needs a controller that runs QMK. A bought 60% PCB has no
  documented spare bus pins, so use a separate small controller board, which is again a
  second USB device.

---

## What the owner must decide

1. Front ports at USB 2.0 only, or at USB 3 speed. USB 2.0 is enough for controllers and
   allows the simplest sockets.
2. Socket style: screw-flange (eight screw heads show on the front), snap-in bezels, keystone,
   or a bare hub board.
3. The hub: the model, its place (deck or body), and 5 V or 12 V supply.
4. The keyboard PCB: a bought GH60 hot-swap PCB, or hand wiring.
5. The plate: a small switch plate in a printed frame, or one plate for the whole panel top.
   Keycaps level with the frame (plate 6.0 down) or standing free.
6. Stabilisers: PCB-mount or plate-mount. This sets the cut-out type.
7. A pointing device, and which type.
8. The arcade panel: printed tiles or a cut plate. If a plate: with a clear cover or bare.
   Snap-in or screw-in buttons.
9. Whether to order a test coupon before the real plates. Recommended.

## Must measure or test

1. The 5 V at a board USB port, idle and with a controller that charges.
2. Back-feed from the chosen hub: 0 V at its upstream plug when it is not connected.
3. Ten cold boots with the hub and four devices connected.
4. Both plug orientations at each front USB-C socket, with a USB 3 drive and with a controller.
5. The real sockets: flange size, hole spacing, body length behind the flange, cable diameter.
6. A printed coupon of the socket cut-outs and pockets with the 2.0 web.
7. The bought PCB: outline, hole positions, USB position, and the height of the lowest part.
8. A cut test coupon: switch fit, stabiliser fit, and the fit of a 30 and a 24 button.

## Inaccessible or partly accessible sources

| Source | Result |
| --- | --- |
| Reddit threads on BC-250 USB faults [B13] | INACCESSIBLE: blocked ("blocked by network security") or timed out. Search-result summaries only. |
| DataPro dimension drawings (PDF) for parts 1678 and 1698 | INACCESSIBLE: an account is needed. The cut-out drawings on the product pages were used. Body lengths are estimated from photos. |
| electronics.stackexchange.com | INACCESSIBLE: HTTP 403. Search-result summaries only. |
| kbdfans.com, kprepublic.com, sabrent.com, perixx.com, shop.pimoroni.com | HTTP 429 to direct fetch. One KBDfans page was read through the extract tool. The others: search-result summaries only. |
| forum.arcadecontrols.com | INACCESSIBLE: no response. |
| SendCutSend price for a 396 x 240 plate | INACCESSIBLE: needs an upload in an account. Not done. |
| SendCutSend stainless steel, acrylic and polycarbonate thickness lists | Not read. |
| AMD Bolton FCH databook | Not opened. Search-result summary only. |
| Coolgear data sheet and 3D model | Not opened. The port layout of the hub board is not confirmed. |
| USB Type-C specification | Not re-read. The USB-C overmould size is recalled, not sourced. |
| StarTech ST7300USBME page | The specification text was not returned. Search-result summary only. |
| Ploopy, Ultimarc, Pimoroni device dimensions | Not published on the pages read, or the page was not reachable. |

## Method notes

- The BC-250 documentation repositories were downloaded as archives and searched as text.
- The GH60 numbers come from a text parse of `keyboard.kicad_pcb` in [K4]: the edge-cut lines,
  the hole footprints, the USB footprint and the switch positions. The article [K5] gives the
  same hole positions from its own CAD comparison.
- The Cherry and Kailh numbers were read from the drawings in the data sheets [K1][K3].
- The scripts and downloads were temporary and are not in the repository.

## Sources

BC-250:

- [B1] elektricM, AMD BC250 Documentation, Hardware Specifications: https://elektricm.github.io/amd-bc250-docs/hardware/specifications/
- [B2] mothenjoyer69, bc250-documentation, `hardware.md`: https://github.com/mothenjoyer69/bc250-documentation/blob/main/hardware.md
- [B3] mothenjoyer69, bc250-documentation, README: https://github.com/mothenjoyer69/bc250-documentation
- [B4] katzzero, bc250-unofficial-community-guide, `01-hardware-specs.md`: https://github.com/katzzero/bc250-unofficial-community-guide/blob/main/01-hardware-specs.md
- [B5] Same guide, `09-wifi-and-peripherals.md`: https://github.com/katzzero/bc250-unofficial-community-guide/blob/main/09-wifi-and-peripherals.md
- [B6] Same guide, `10-troubleshooting.md`: https://github.com/katzzero/bc250-unofficial-community-guide/blob/main/10-troubleshooting.md
- [B7] Same guide, `03-power-supply-guide.md`: https://github.com/katzzero/bc250-unofficial-community-guide/blob/main/03-power-supply-guide.md
- [B8] elektricM, Stability troubleshooting, "System Freezes When Sleeping": https://elektricm.github.io/amd-bc250-docs/troubleshooting/stability/
- [B9] elektricM, Display troubleshooting: https://elektricm.github.io/amd-bc250-docs/troubleshooting/display/
- [B10] elektricM, Debian page: https://elektricm.github.io/amd-bc250-docs/linux/debian/
- [B11] elektricM/amd-bc250-docs issue 7, "USB not working": https://github.com/elektricM/amd-bc250-docs/issues/7
- [B12] AMD, Bolton-D2/D2H/D3/D4 FCH Databook (summary only): https://www.amd.com/content/dam/amd/en/documents/archived-tech-docs/datasheets/Bolton_D2-D2H-D3-D4_Databook.pdf
- [B13] Reddit (summaries only): https://www.reddit.com/r/BC250Gaming/comments/1s07n2c/a_simple_fix_for_most_broken_usb_ports/ , https://www.reddit.com/r/linux_gaming/comments/1q7xgbp/amd_bc250_having_usb_issue/ , https://www.reddit.com/r/linux_gaming/comments/1pv5f1v/amd_bc250_usb_30_issue/ , https://www.reddit.com/r/Bazzite/comments/1qy27wb/complete_noob_hear_i_made_a_bootable_usb_but_its/
- [B14] katzzero guide, `02-bios-and-firmware.md`: https://github.com/katzzero/bc250-unofficial-community-guide/blob/main/02-bios-and-firmware.md

USB hardware:

- [U1] Wikipedia, Keystone module: https://en.wikipedia.org/wiki/Keystone_module
- [U2] Delock, Keystone compatibility: https://www.delock.com/infothek/Keystone_Modulabmessungen/keystone_kompatibilitaet_e.html
- [U3] spuder, 10-Inch-Rack-OpenSCAD, `KeystoneJack.scad`: https://github.com/spuder/10-Inch-Rack-OpenSCAD/blob/main/KeystoneJack.scad
- [U4] davidwkeith/rack-build pull requests 6 and 9 (summaries only): https://github.com/davidwkeith/rack-build/pull/6 , https://github.com/davidwkeith/rack-build/pull/9 ; CRXCONEC catalogue, patch panel in 1.5 steel (summary only): https://www.crxconec.com/Templates/att/Catalogue%20full%20version-2025.pdf?lng=en
- [U5] Computer Cable Store, "Why Does My USB-C Adapter Only Work One Way Up?": https://www.computercablestore.com/why-does-my-usb-c-adapter-only-work-one-way-up
- [U6] DataPro 1698, USB 3.2 panel-mount extension: https://www.datapro.net/products/usb-3-2-super-speed-panel-mount-extension.html ; cut-out drawing: https://www.datapro.net/images/cutouts/usb-a.jpg
- [U7] DataPro 1678, USB-C panel-mount extension: https://www.datapro.net/products/usb-c-panel-mount-extension-cable.html ; cut-out drawing: https://www.datapro.net/images/cutouts/usb-c.jpg
- [U8] DataPro 1673, keystone-mount USB-C extension: https://www.datapro.net/products/keystone-mount-usb-c-extension-cable-m-f.html
- [U9] DataPro, panel-mount USB-C and USB-A lists: https://www.datapro.net/catalog/panel-mount-usb-c-cables.html , https://www.datapro.net/catalog/panel-mount-usb-a-cables.html ; part 1679: https://www.datapro.net/products/panel-mount-usb-type-a-to-usb-c-3-1-extension-cable.html
- [U10] Adafruit products 908, 4053, 4052, 4055, 6069, 4218: https://www.adafruit.com/product/908 (replace the number for the others)
- [U11] Coolgear hub boards and hub: https://www.coolgear.com/product/4-port-type-a-c-usb-3-2-gen-1-micro-powered-hub-pcba-w-esd-surge-protection , https://www.coolgear.com/product/4-port-usb-3-2-gen-1-micro-powered-hub-pcba-w-esd-surge-protection , https://www.coolgear.com/product/4-port-type-c-usb-3-1-gen2-hub-with-din-rail-mounting-kit
- [U12] StarTech ST7300USBME (summary only): https://www.startech.com/en-us/usb-hubs/st7300usbme
- [U13] Sabrent HB-MC7B, 7-port hub with a 5 V 4 A adapter (summary only): https://sabrent.com/products/hb-mc7b
- [U14] SATA to barrel power cables (summaries only): https://www.amazon.com/HYAGBCOP-5-5mm-Converter-Adapter-Supply/dp/B0FKTHVFTL , https://www.amazon.com/YSJJZRL-15-Pin-5-5mm-2-1mm-Adapter/dp/B0C85RF8QD
- [U15] Electronics Stack Exchange, USB-A plug envelope of 16 x 8 (summary only): https://electronics.stackexchange.com/questions/696802/is-there-any-minimal-distance-recommendation-between-two-usb-female-ports
- [U16] Delock 86399 (summary only): https://www.delock.com/produkt/86399/merkmale.html
- [U17] BERLAT keystone USB-C coupler listing (summary only): https://www.amazon.com/BERLAT-Keystone-Adapters-Connector-Interface/dp/B0F6MP92W6
- [U18] Tripp Lite U325-000-KP-BK data sheet (no module dimensions in it): https://assets.tripplite.com/product-pdfs/en/u325000kpbk.pdf

Keyboard:

- [K1] Cherry, MX Series keyswitch data sheet, pages 10-1 to 10-4 (copy hosted by SparkFun): https://cdn.sparkfun.com/datasheets/Components/Switches/MX%20Series.pdf
- [K2] ai03 Plate Generator, source files `src/cutouts/SwitchMXBasic.js`, `StabilizerMXBasic.js`, `StabilizerMXSmall.js`, `StabilizerMXSpec.js`, `src/HelpPanes.js`: https://github.com/ai03-2725/yet-another-keyboard-builder
- [K3] Kailh, CPG151101S11 hot-swap socket data sheet: http://www.kailh.com/en/Products/Ks/HPC/CPG151101S11-16.pdf
- [K4] komar007, GH60, `keyboard.kicad_pcb` (revision B): https://github.com/komar007/gh60
- [K5] skeletonkbd, "Investigating PCB mounting holes, external dimensions, and USB positions to design a GH60-compatible case 2026" (written with an AI model, from CAD; no physical test): https://note.com/skeletonkbd/n/n7fdfaac9bd8c?hl=en
- [K6] KeycapCompare, Keycap Profile Height Chart: https://keycapcompare.com/posts/keycap-profile-height-chart/
- [K7] KBDfans DZ60RGB-ANSI v2: https://kbdfans.com/products/dz60rgb-ansi-mechanical-keyboard-pcb ; KBDfans 60% PCB list (summary only): https://kbdfans.com/collections/pcb/60-pcb ; BM60 listing (summary only): https://www.keyboardselect.com/product/bm60-rgb-60-gh60-hot-swappable-pcb-programmed-qmk-firmware-type-c/
- [K8] Geekhack, stabiliser spacing for a 6.25u key (summary only): https://geekhack.org/index.php?topic=113777.0
- [K9] QMK, Pointing Device: https://docs.qmk.fm/features/pointing_device

Cutting services:

- [C1] SendCutSend, cut tolerance FAQ and sheet cutting comparison: https://sendcutsend.com/faq/what-is-your-cut-tolerance/
- [C2] SendCutSend, 5052 H32 aluminium: https://sendcutsend.com/materials/5052-aluminum/
- [C3] SendCutSend, 6061 T6 aluminium: https://sendcutsend.com/materials/6061-aluminum/
- [C4] SendCutSend, countersinking: https://sendcutsend.com/services/countersinking/
- [C5] SendCutSend, tapping: https://sendcutsend.com/services/tapping/
- [C6] SendCutSend, anodising: https://sendcutsend.com/services/anodizing/
- [C7] SendCutSend, pricing: https://sendcutsend.com/pricing/
- [C8] SendCutSend, kerf FAQ (summary only): https://sendcutsend.com/faq/what-is-the-size-of-your-laser-kerf/
- [C9] OSH Cut, capabilities: https://www.oshcut.com/capabilities
- [C10] Fabworks: https://www.fabworks.com/
- [C11] LaserBoost, keyboard plates: https://www.laserboost.com/keyboards/
- [C12] KeebTalk, list of laser cutting services (summary only): https://www.keebtalk.com/t/list-of-laser-cutting-services/2500
- [C13] SendCutSend, mild steel: https://sendcutsend.com/materials/mild-steel/

Arcade panel and pointing devices:

- [A1] Slagcoin, Panel Mounting and Layering: https://www.slagcoin.com/joystick/mounting_layering.html
- [A3] Reddit r/cade and r/fightsticks (summaries only): https://www.reddit.com/r/cade/comments/1qnr33u/mounting_jlf_sanwa_joysticks_buttons/ , https://www.reddit.com/r/fightsticks/comments/4l5cq4/plexiglassacrylic_thickness/ , https://www.reddit.com/r/fightsticks/comments/yrkgun/need_qanba_obsidian_dimensions_for_project/
- [D1] Cirque, GlidePoint circle trackpads: https://www.cirque.com/glidepoint-circle-trackpads
- [D2] Azoteq, I2C trackpad modules (summary only): https://www.azoteq.com/product/i2c-trackpad-modules/
- [D3] Perixx PERIPAD-501 (summaries only): https://perixx.com/products/peripad-501 , https://www.ebay.com/p/26017026281
- [D4] Ploopy Trackpad and Adept: https://ploopy.co/shop/trackpad-fully-assembled/ , https://ploopy.co/shop/adept-trackball-fully-assembled/
- [D5] Ultimarc U-Trak: https://www.ultimarc.com/trackballs-and-spinners/trackballs/u-trak/
