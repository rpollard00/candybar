# The power and the video of the monitor

Research date: 2026-11-14. Each source was read on this date.

This note answers one question of the owner (2026-11-14): can USB power run the monitor, and does
the BC-250 or a hub give sufficient power? It also records the video path that the owner chose on
the same day. It extends `docs/research/hardware-envelopes.md` (section 1) and
`docs/design/hardware-list.md` (section 2.11, question 5).

Nothing was tested for this note. No part was bought. Section 9 lists the bench tests that decide.

## Status tags

| Tag | Meaning |
| --- | --- |
| MAKER [id] | From the maker of the part: a product page, a data sheet, a manual or the maker's answer to a customer. |
| SOURCED [id] | Written in the source with that number in section 10. The page was read. |
| SOURCED (summary) | Read in a search-result summary only. The page was not read. |
| OWNER | Told by the owner on 2026-11-14, from the owner's own hardware. |
| BUILD | A value of this repository: the fit report or an earlier note. The place is named. |
| STANDARD | From a published specification. The specification is named. |
| ESTIMATED | Calculated or reasoned here. The method is given. |
| NOT CONFIRMED | No source says it, or the sources do not agree. A test must show it. |

## 1. Summary

1. **A USB port of the BC-250 cannot run the monitor.** The monitor draws 5.1 W at its lowest
   brightness and 14.9 W at full brightness (one reviewer's measurement). A USB 3.0 port of type A
   gives 4.5 W by the standard. One community report gives 5 W for the two USB 3.0 ports together.
2. **A hub port cannot run it with a margin.** A port of type A gives 4.5 W, or 7.5 W if it is a
   charging port. A USB-C port at 5 V and 3 A gives 15 W, which is the full draw with no margin.
3. **The maker asks for a USB power delivery source of 30 W or more.** The monitor also runs from the
   5 V of a laptop port, with less brightness. The voltage that it asks for is not confirmed.
4. **The video path is the owner's choice:** an active DisplayPort to HDMI adapter (UGREEN, owned) and
   an HDMI lead to the mini-HDMI input of the monitor. It carries picture and sound.
5. **The monitor then needs power only, on one of its two USB-C ports.** Recommendation: a 12 V to
   USB-C power delivery board on the 12 V rail of the supply. It gives each voltage that the monitor
   can ask for, and it goes off with the supply.
6. **The largest open risk is the start.** No source says that the monitor starts when its power
   arrives. Its power button is on its right edge, inside the cabinet. Bench test 3 decides.

## 2. What the monitor needs

The unit is the UPERFECT BE16CU (before: "UColor T6"), 16 inch, 3840 x 2400, 1200 cd/m2.

| Item | Value | Status |
| --- | --- | --- |
| Ports | 2 x USB-C "full-featured" (audio and video input), 1 x mini-HDMI (audio and video input), 1 x 3.5 mm audio output | MAKER [M1] |
| The HDMI socket | Mini-HDMI (HDMI type C). The box has a "mini HDMI to HDMI Cable". | MAKER [M1] |
| Where the ports are | The two USB-C ports and the mini-HDMI port are on the left edge. The power button, the wheel and the 3.5 mm output are on the right edge. | SOURCED [R1] (photos). The heights are in `docs/research/hardware-envelopes.md` section 1 (estimated). |
| USB-C video | "This monitor's USB-C port has DP Alt mode." | MAKER [M1] (answer of 2025-10-03) |
| One lead for power and video | Yes, from a source with USB-C video and sufficient power. "All the machines worked with a single USB-C connection for both display and power." | SOURCED [R1] (six mini PCs and three laptops) |
| One lead, the limit | "the brightness will be lower than the maximum 1200 nits because the monitor's power supply is limited by the laptop's USB-C output". If the power is not sufficient: "unstable display, flickering, or other abnormal behavior". | MAKER [M1] (answer of 2026-08-06) |
| Two leads | "Setup is simple with just two included cables, one for power and one USB-C for data" | SOURCED (summary) [M2] |
| What the maker asks for | "requires a power supply with a PD30W rating or higher. When using the USB-C power port, a power adapter that supports the PD3.0 protocol is required, with adjustable voltages of 5V, 9V, 15V, and 20V." | MAKER [M1] (answer of 2025-09-10) |
| Rated power | 14 W | MAKER [M1] (parameter table) |
| Power on the retail listing | "Power Consumption 30 watts", "Voltage 5 volts" | SOURCED [R2]. The 30 W is probably the size of the adapter. ESTIMATED. |
| Measured draw | 5.1 W at 0 % brightness, 7.4 W at 25 %, 9.8 W at 50 %, 12.3 W at 75 %, 14.9 W at 100 % | SOURCED [R1] (one reviewer, with the supplied adapter, contrast at its default) |
| Brightness for indoor use | "Indoors, I'm usually comfortable running the screen at just 25% brightness." | SOURCED [R1] |
| Full brightness | "Peak brightness is achieved when connected to power and using a white background" | SOURCED [R2] |
| In the box | 2 x USB-C to USB-C cable, 1 x mini-HDMI to HDMI cable, 1 x power adapter, the manual | MAKER [M1] |
| The adapter in the box | A customer writes that it "states several voltages, from 3V to 20V". | MAKER [M1] (a customer's question). The label was not read. |
| Does it take 5 V only, or more? | NOT CONFIRMED. It runs on 5 V from a laptop port. A power delivery source also gives 9 V, 15 V and 20 V. No source says which voltage the monitor asks for. | Bench test 1 |
| Does it start when power arrives? | NOT CONFIRMED | Bench test 3 |
| The user manual | Not found. The maker sends it by e-mail on request. | MAKER [M1] |

Current of the monitor at each voltage (ESTIMATED: the measured draw divided by the voltage, with
no loss):

| Voltage | At 5.1 W (0 % brightness) | At 7.4 W (25 %) | At 14.9 W (100 %) |
| --- | --- | --- | --- |
| 5 V | 1.0 A | 1.5 A | 3.0 A |
| 9 V | 0.6 A | 0.8 A | 1.7 A |
| 15 V | 0.3 A | 0.5 A | 1.0 A |
| 20 V | 0.3 A | 0.4 A | 0.7 A |

## 3. What the BC-250 gives

| Item | Value | Status |
| --- | --- | --- |
| Video output | 1 x DisplayPort 1.4, full size. No HDMI. | SOURCED [B1][B4] |
| USB-C, DisplayPort alternate mode | None. "board doesn't have USB-C DisplayPort alt mode" | SOURCED [B2] |
| USB ports | 2 x USB 3.0 and 2 x USB 2.0, all type A | SOURCED [B1][B4] |
| Current of a port, by the standard | 0.5 A (2.5 W) for USB 2.0, 0.9 A (4.5 W) for USB 3.0 | STANDARD (USB 2.0, USB 3.0) |
| Current of a port, on this board | No document gives a number for each port. One user: "rear USB 3.0 ports are specced for 5 W total". | SOURCED [B3] (one user, no measurement) |
| The 5 V of the board | Weak. "the ports are very anemic when it comes to power delivery". Some boards have no 5 V at the ports. | SOURCED (summary) [B5]. SOURCED [B3]. See `docs/research/pc-panel-and-front-usb.md` A1. |
| A second screen | "Maximum 2 screens" through a DisplayPort multi-stream hub. One hub "Worked consistently". Two others gave only a mirror image. | SOURCED [B6] |
| Audio | "Audio over DisplayPort (compatibility varies)". No analogue output. | SOURCED [B1] |

Can a port run the monitor?

| Source | Power it gives | The monitor needs | Result |
| --- | --- | --- | --- |
| One USB 2.0 port of the board | 2.5 W | 5.1 W to 14.9 W | No |
| One USB 3.0 port of the board | 4.5 W by the standard. 5 W for the two ports together (one user). | 5.1 W to 14.9 W | No |
| A powered hub, port of type A | 4.5 W (USB 3.0). 7.5 W if the port is a charging port (1.5 A). | 5.1 W to 14.9 W | No for a plain port. A charging port is at its limit at 25 % brightness (7.4 W). ESTIMATED from [R1]. |
| A powered hub, USB-C port at 5 V and 3 A | 15 W | 14.9 W at full brightness | No margin. The maker warns of flicker when the power is not sufficient. |
| The hub board of the earlier note (Coolgear, "Up to 2 A for each port") | 10 W | 5.1 W to 14.9 W | Only below about 50 % brightness. ESTIMATED from [R1]. |
| The 5 V rail of the supply | 24 A (120 W together with the 3.3 V rail) | 3.0 A | The rail has sufficient power. The problem is the plug: see way (2) in section 4. |

## 4. Ways to power the monitor from the supply

The supply is the EVGA SuperNOVA 1000 P5: 5 V at 24 A, 12 V at 83.3 A, standby 5 V at 3 A. MAKER [P1].

| Way | Parts | For | Against | Status |
| --- | --- | --- | --- | --- |
| (1) A 12 V to USB-C power delivery board | Example: Coolgear CG-PDC65W-PCBA. Input 12 V to 24 V (limits 9 V and 28 V) on a 2-pin terminal. Output 5 V 3 A, 9 V 3 A, 12 V 3 A, 15 V 3 A, 20 V 3.25 A. It is a buck-boost converter, so 15 V and 20 V come from a 12 V input. Idle draw 5 mA at 12 V. 49 mm x 45 mm x 13 mm. One USB-C socket. | It is the kind of source that the maker asks for (power delivery, 30 W or more). It gives each voltage of the maker's answer. It goes off with the supply. | The vendor sells it as a development product ("intended for integration, evaluation, and testing purposes"). The price and the stock were not read: the product page refused the request. | MAKER [C1] (the data sheet) |
| (2) Plain 5 V from the 5 V rail to a USB-C plug | A lead from a SATA or a four-pin connector to a USB-C plug | The fewest parts. The retail listing gives "Voltage 5 volts". | The draw at full brightness is 3.0 A, which is the limit of a USB-C plug at 5 V. A drop of voltage in a thin lead makes it worse. The plug must tell the monitor that 3 A is available (see the note that follows). No such lead with a data sheet was found. | NOT CONFIRMED |
| (3) The monitor's own mains adapter | The adapter in the box | The maker's part. No question of voltage. | Inside the shell it needs mains wiring, which the brief excludes ("Avoid adding DIY mains distribution just to hide external adapters"). Outside the shell it is a second mains plug, and it does not go off with the supply. | The brief, "Electrical integration boundaries" |

How a plain 5 V source tells the current (way 2): a USB-C source has a pull-up resistor on its CC
pins, and "The values of Rp determine the current-carrying capability". SOURCED [T1]. The values are
56 kΩ for the default USB current, 22 kΩ for 1.5 A and 10 kΩ for 3 A, with 5.1 kΩ in the device.
STANDARD (USB Type-C specification. These four values are recalled and were not read again). A common
USB-A to USB-C lead has the 56 kΩ resistor. A device that obeys it takes 0.5 A to 0.9 A only.

Parts for way (1), from the supply to the monitor:

| Part | Detail | Status |
| --- | --- | --- |
| Lead from the supply | A SATA or four-pin lead of the supply, with an adapter to two bare wires for the 12 V and ground | One SATA connector gives 4.5 A at 12 V (`docs/research/pc-panel-and-front-usb.md` A3). The board takes 2 A at most for 20 W. ESTIMATED. |
| Fuse | An in-line fuse of about 3 A in the 12 V wire | ESTIMATED: the 12 V rail can give 83 A into a fault. No source was read. |
| The board | Coolgear CG-PDC65W-PCBA, or a board of the same kind | MAKER [C1] |
| Lead to the monitor | USB-C to USB-C, 3 A, with a right-angle plug at the monitor. The route is about 600 mm to 800 mm. | The length is from `docs/design/hardware-list.md` 1.2 (estimated). |

Risks:

| Risk | Detail | Answer |
| --- | --- | --- |
| The monitor asks for power delivery and gets plain 5 V | With way (2) the monitor gets no answer to its request. It then runs as on a laptop port: the brightness is lower, and it can flicker. | Use way (1). Bench test 2 shows what plain 5 V does. |
| The power delivery board does not start, or starts late | The board starts when the 12 V arrives. The monitor then makes its request. If this takes too long, the BC-250 finds no screen at its start. | NOT CONFIRMED. Bench test 4. |
| Back-feed through the video lead | The monitor has its own power, and the HDMI lead has a 5 V pin from the adapter. | Small. The board, the adapter and the monitor have their power from the same supply, and they go off together. ESTIMATED: no source was read. |
| Back-feed through USB | A USB-C lead from the monitor to a port of the board or of the hub joins two 5 V sources. | Do not connect the monitor to a USB port of the board or of the hub. The monitor has no touch screen, so it needs no USB data. |
| Heat | The monitor gives up to 15 W behind the bezel plate, and the board loses about 1 W to 2 W. | ESTIMATED: an efficiency of about 90 %. The heat is in `docs/research/hardware-envelopes.md` section 2 ("Heat to remove"). |

## 5. The video path

The owner chose the path on 2026-11-14: an active DisplayPort to HDMI adapter at the board, and an
HDMI lead to the mini-HDMI input of the monitor. The owner has the adapter and uses the same type on a
second BC-250. OWNER.

| Item | Value | Status |
| --- | --- | --- |
| The adapter | UGREEN "8K@60Hz 2K@240Hz Active DisplayPort to HDMI Unidirectional Adapter", model 85996. DisplayPort 1.4 plug to HDMI 2.1 socket, 32.4 Gbit/s, HDCP 2.3. | SOURCED [U1] (the retail listing). OWNER. |
| Price | USD 19.99 | SOURCED [U1], 2026-11-14. The owner has the part. |
| Picture and sound | "It carries sound: the monitor gets both picture and sound over HDMI." | OWNER |
| The same type in the community documents | A UGREEN 8K active adapter is "verified working". Its chip is a Realtek RTD2173. | SOURCED [B2][B6] |
| Sound and the kernel | With an active adapter the sound is "Silent or slow on older kernels". "Kernel 7.2 and newer fix it completely, and current longterm kernels fix the large error." | SOURCED [B2][B6]. The owner's system has the sound. |
| Size of the adapter | The listing gives no size. It names two versions: a short adapter, and one with a lead of 0.66 ft (200 mm). Estimate: a DisplayPort plug of about 45 mm x 21 mm x 13 mm, and an HDMI socket body of about 50 mm x 25 mm x 14 mm. | SOURCED [U1] for the versions. The sizes are the estimate of `docs/research/hardware-envelopes.md` section 8. Measure the owner's part. |
| Room at the board | The DisplayPort socket is on the I/O edge, 48.6 mm to 66.4 mm from the straight long edge. The plug and the adapter stand in the exhaust duct. | BUILD (`docs/research/hardware-envelopes.md` section 2). The fit study keeps 45 mm in front of the I/O edge. |
| The HDMI socket of the monitor | Mini-HDMI (type C), on the left edge, about 49 mm above the bottom edge | MAKER [M1]. The height is estimated (`docs/research/hardware-envelopes.md` section 1). |
| The lead | HDMI plug (type A) to mini-HDMI plug (type C), for 18 Gbit/s (HDMI 2.0), with a right-angle plug at the mini-HDMI end | See the table that follows |
| The mode | 3840 x 2400 at 60 Hz has a pixel clock of 592.6 MHz with reduced blanking. The limit of HDMI 2.0 is 600 MHz. Thus the mode is 1 % below the limit. | ESTIMATED: 4000 x 2469 x 60 (CVT reduced blanking). The limit is STANDARD (HDMI 2.0, recalled). |
| The HDMI version of the monitor's input | NOT CONFIRMED. The maker's page does not give it. | Bench test 5 |

Leads with a right-angle mini-HDMI plug. Each row is a retail listing, read as a search summary
only. No maker's data sheet was found for a lead of this kind.

| Lead | What the listing says | Status |
| --- | --- | --- |
| YOUCHENG, 15 cm | "Mini HDMI to HDMI Short Cable, 90 Degree Right Angle", "HDMI 2.0", "4k@60HZ" | SOURCED (summary) [L1] |
| Duttek, short and thin | "Ultra-Thin Short 90 Degree HDMI to Mini HDMI Cable" | SOURCED (summary) [L1] |
| RIIEYOCA, 1 m | "8K Mini HDMI to HDMI 2.1 Adapter Cable, 90 Degree Down Angle" | SOURCED (summary) [L1] |
| A right-angle adapter on the supplied cable | "Right Angle mini hdmi 90 Degree Adapter", mini-HDMI plug to mini-HDMI socket, about 15 cm | SOURCED (summary) [L1]. It adds one more joint at the weak socket. |

The direction of the angle:

- A mini-HDMI plug has a wide side and a narrow side. Thus a right-angle plug has four directions: up,
  down, left and right.
- The socket lies along the edge of the monitor, because the body is 10 mm thick and the plug is
  10.4 mm wide. ESTIMATED from these two values.
- An "up" or "down" plug turns the lead toward the back or the front of the monitor. A "left" or
  "right" plug turns it along the edge.
- The cable channel of the fit study starts at each side of the monitor and goes back to the compute
  module. Thus the lead must turn toward the back. If the socket has its wide side to the back, the
  plug is the "up" type. If not, it is the "down" type. Look at the unit before the lead is bought.
  NOT CONFIRMED: the photos do not show the direction.
- The fit study gives each side edge 22 mm for a right-angle plug. Measure the plug: the estimate of
  the earlier note is 15 mm to 20 mm.

Length: the adapter is at the I/O end of the board. The route to the left edge of the monitor is about
600 mm to 800 mm (`docs/design/hardware-list.md` 1.2, estimated). Leads of 15 cm are too short. A lead
of 1 m is the first size to buy.

A path that is not used: an adapter from DisplayPort to the USB-C port of the monitor exists (for
example Delock 61059, with a power input, SOURCED (summary) [D1]). It puts the picture and the power
on one plug. The owner's adapter makes it unnecessary. It stays as a fallback if the mini-HDMI socket
gives problems.

## 6. What goes off at a shutdown, and the start

| Event | What occurs | Status |
| --- | --- | --- |
| The system shuts down | The adapter board of the power button releases `PS_ON`. The 12 V rail and the 5 V rail go off. The power delivery board and the monitor go off with them. | `docs/research/bc250-power-button.md` section 5. STANDARD (ATX12V design guide, in that note). |
| The standby 5 V | It stays on. Nothing of the monitor is on it. | The same |
| The button is pressed | The 12 V arrives. The BC-250 and the power delivery board start at the same time. | ESTIMATED |
| The monitor | NOT CONFIRMED: no source says that it starts with no button press. If it does not, a person must press its power button, which is on its right edge behind the cheek. | Bench test 3. The monitor cradle must then give access to the button, or the owner takes a monitor that starts by itself. |

## 7. Recommendation

The owner decides. This is the recommendation and its reasons.

1. **Power: way (1), a 12 V to USB-C power delivery board on the 12 V rail.** It is the only way that
   gives what the maker asks for with no mains part in the shell. It has a margin: the board gives
   15 W at 5 V and more at each higher voltage, and the monitor takes 14.9 W at most.
2. **Video: the owner's adapter and a lead of 1 m with a right-angle mini-HDMI plug.** Buy the lead
   after a look at the socket of the unit (the direction of the angle).
3. **Use the upper USB-C port for the power.** It is about 37 mm from the mini-HDMI port, and the
   lower one is about 19 mm from it. ESTIMATED from the port heights of the earlier note.
4. **Set the brightness low.** At 25 % the monitor takes 7.4 W, and the reviewer finds this
   comfortable indoors. The cabinet then has 7 W less heat behind the bezel plate.
5. **Do the bench tests first.** Tests 1 and 3 decide the power part and the access to the button.

## 8. What the shell must provide

| Item | Value | Status |
| --- | --- | --- |
| Plug space at the left edge of the monitor | Two right-angle plugs: mini-HDMI at about 49 mm and USB-C at about 86 mm above the bottom edge. The fit study has 22 mm on each side edge over the full height. | BUILD (fit report). No change. |
| Cable channel | One HDMI lead (5 mm to 7 mm) and one USB-C lead (3.5 mm to 4.5 mm). The fit study has a channel of 20 mm on each side. | BUILD (`mon_cable_w`). No change. |
| Cable clamp | Within 50 mm of the mini-HDMI plug | `docs/research/hardware-envelopes.md` section 8 |
| A place for the power delivery board | 49 mm x 45 mm x 13 mm, with room for a USB-C plug at one end and two wires at the other: about 110 mm x 50 mm x 20 mm. On the monitor cradle or on the floor near the compute module. Four small posts or a clip. | ESTIMATED from [C1]. The hole pattern of the board was not read. |
| Room for the adapter at the board | 45 mm in front of the I/O edge is in the fit study. The adapter with its HDMI plug is longer: about 100 mm to 250 mm with its lead. The lead can turn in the exhaust duct. | NOT CONFIRMED. Measure the owner's adapter and put it into the fit study. |
| Access to the monitor's power button | Only if bench test 3 fails: a hole or a push pin in the cradle at the right edge, about 66 mm above the bottom edge | The height is estimated (`docs/research/hardware-envelopes.md` section 1) |
| Access to the 3.5 mm output | Only if the monitor is the audio source: a right-angle 3.5 mm plug at the right edge, about 30 mm above the bottom edge | See `docs/research/audio.md` section 8 |

## 9. Bench tests on the real unit

1. Put a USB-C power meter between the supplied adapter and the monitor. Write down the voltage that
   the monitor asks for. Write down the current at 0 %, 25 %, 50 % and 100 % brightness.
2. Feed the monitor from a plain 5 V source of 3 A. Write down if it starts, and the brightness at
   which it flickers.
3. Remove the power and connect it again, with the video lead connected. Write down if the monitor
   starts with no button press, and which input it selects.
4. With the power delivery board on the 12 V of the supply: start the system ten times with the power
   button. Write down if the BC-250 finds the screen each time.
5. Connect the BC-250 through the adapter and the lead. Write down the mode (3840 x 2400 at 60 Hz or
   not) and if the sound works.
6. Measure the adapter, the plug of the HDMI lead and the right-angle plugs. Write the values into
   `cad/params/hardware.csv`.
7. Read the label of the supplied adapter (its voltages and currents).

## 10. Sources

| No. | Source | What it is |
| --- | --- | --- |
| M1 | https://uperfect.com/products/16-inch-4k-sunlight-readable-monitor | The maker's product page: the parameter table, the box contents, and the maker's answers to customers |
| M2 | https://uperfect.com/ | Summary only: the two included cables |
| R1 | https://www.linuxlinks.com/uperfect-ucolor-t6-review/ | A review with photos of the two side edges and a chart of the draw at five brightness levels |
| R2 | https://www.amazon.com/dp/B0F99H1KSL | The retail listing of the owner's unit: power, voltage, the note on peak brightness |
| B1 | https://elektricm.github.io/amd-bc250-docs/hardware/specifications/ | Community documentation of the board: ports, video, audio |
| B2 | https://elektricm.github.io/amd-bc250-docs/troubleshooting/display/ | Community documentation: adapters, sound through DisplayPort, no USB-C video |
| B3 | https://github.com/katzzero/bc250-unofficial-community-guide/blob/main/10-troubleshooting.md | Community guide: USB power, the 5 V rail, sound |
| B4 | https://github.com/katzzero/bc250-unofficial-community-guide/blob/main/01-hardware-specs.md | Community guide: the connector table |
| B5 | https://www.reddit.com/r/BC250Gaming/comments/1s07n2c/a_simple_fix_for_most_broken_usb_ports/ | Summary only |
| B6 | https://elektricm.github.io/amd-bc250-docs/hardware/display/ | Community documentation: adapters, the kernel fix for the sound, multi-stream hubs |
| P1 | https://www.evga.com/support/manuals/files/220-P5-1000-X1.pdf | The manual of the supply: the table of the rails |
| C1 | https://www.coolgear.com/wp-content/uploads/CG-PDC65W-PCBA_Technical-Data-Sheet-06-250613.pdf | Data sheet of a 12 V to USB-C power delivery board |
| T1 | https://www.ti.com/lit/an/slyy109b/slyy109b.pdf | A chip maker's primer on USB Type-C and power delivery |
| U1 | https://www.amazon.com/UGREEN-Unidirectional-Aluminum-Converter-Compatible/dp/B0FQCGSWW3 | The retail listing of the owner's adapter: the model number, the price, the versions |
| L1 | Retail listings of mini-HDMI leads and adapters with a right-angle plug (search of 2026-11-14) | Summaries only |
| D1 | https://www.delock.com/produkt/61059/merkmale.html | Summary only: a DisplayPort to USB-C adapter with a power input |

## 11. Not confirmed, and sources that were not accessible

| Item | Result |
| --- | --- |
| The voltage that the monitor asks for | No source. Bench test 1. |
| The start of the monitor when power arrives | No source. Bench test 3. |
| The user manual of the monitor | Not published. The maker sends it by e-mail. |
| The current of each USB port of the board | No measurement was found. One user report. |
| The price and the stock of the power delivery board | The product page answered HTTP 403. The data sheet was read. |
| A second power delivery board with a data sheet | Not found in the time. Boards of this kind are common in retail with no data sheet. |
| A lead from the 5 V rail to USB-C with the 3 A resistor | Not found. |
| The size of the UGREEN adapter | Not in the listing text. |
| The direction of the mini-HDMI socket in the monitor | The photos do not show it. |
| The Delock data sheet | The maker's site answered HTTP 401. Summary only. |
| The USB Type-C resistor values | Recalled. The primer [T1] gives the principle and no values in the text that was read. |
| The pixel clock | Calculated here from the CVT reduced-blanking rule. Read the mode on the bench (`xrandr --verbose` or the log of the compositor). |
