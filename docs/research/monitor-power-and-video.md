# The power and the video of the monitor

Research date: 2026-11-14. Each source was read on this date.

**DRAFT. The work stopped before it was complete. Each section that is not complete has the words NOT FINISHED.**

This note answers one question of the owner (2026-11-14): can USB power run the monitor, and does
the BC-250 or a hub give sufficient power? Nothing was tested for this note. No part was bought.

## Status tags

| Tag | Meaning |
| --- | --- |
| MAKER [id] | From the maker of the part: a product page, a data sheet, a manual or the maker's answer to a customer. |
| SOURCED [id] | Written in the source with that number in section 8. The page was read. |
| SOURCED (summary) | Read in a search-result summary only. The page was not read. |
| STANDARD | From a published specification. The specification is named. |
| ESTIMATED | Calculated or reasoned here. The method is given. |
| NOT CONFIRMED | No source says it, or the sources do not agree. A test must show it. |

## 1. Summary

1. A USB port of the BC-250 cannot run the monitor. The monitor draws 5.1 W at its lowest brightness
   and 14.9 W at full brightness (one reviewer's measurement). A USB 3.0 port of type A gives 4.5 W by
   the standard, and one community report gives 5 W for the two USB 3.0 ports of the board together.
2. The board has no USB-C port and no DisplayPort alternate mode. Thus one lead from the board for
   power and video is not possible without an adapter.
3. The maker says that the monitor needs a USB power delivery source of 30 W or more. The monitor
   also runs from a 5 V laptop port with less brightness. The voltage that it asks for is not
   confirmed.
4. Recommendation (provisional): a 12 V to USB-C power delivery board on the 12 V rail of the supply.
   It gives each voltage that the monitor can ask for, and it goes off with the supply.
5. A hub port is not a safe source. Its limit is 4.5 W to 7.5 W for a port of type A.

## 2. What the monitor needs

The unit is the UPERFECT BE16CU (before: "UColor T6"), 16 inch, 3840 x 2400, 1200 cd/m2.

| Item | Value | Status |
| --- | --- | --- |
| Ports | 2 x USB-C "full-featured" (audio and video input), 1 x mini-HDMI (audio and video input), 1 x 3.5 mm audio output | MAKER [M1] |
| USB-C video | "This monitor's USB-C port has DP Alt mode." | MAKER [M1] (answer of 2025-10-03) |
| One lead for power and video | Yes, from a source with USB-C video and sufficient power. "All the machines worked with a single USB-C connection for both display and power." | SOURCED [R1] (six mini PCs and three laptops) |
| One lead, the limit | "the brightness will be lower than the maximum 1200 nits because the monitor's power supply is limited by the laptop's USB-C output". If the power is not sufficient: "unstable display, flickering, or other abnormal behavior". | MAKER [M1] (answer of 2026-08-06) |
| What the maker asks for | "requires a power supply with a PD30W rating or higher. When using the USB-C power port, a power adapter that supports the PD3.0 protocol is required, with adjustable voltages of 5V, 9V, 15V, and 20V." | MAKER [M1] (answer of 2025-09-10) |
| Rated power | 14 W | MAKER [M1] (parameter table) |
| Power on the retail listing | "Power Consumption 30 watts", "Voltage 5 volts" | SOURCED [R2]. This is the size of the adapter, not the draw. ESTIMATED. |
| Measured draw | 5.1 W at 0 % brightness, 7.4 W at 25 %, 9.8 W at 50 %, 12.3 W at 75 %, 14.9 W at 100 % | SOURCED [R1] (one reviewer, with the supplied adapter, contrast at its default) |
| Brightness for indoor use | "Indoors, I'm usually comfortable running the screen at just 25% brightness." | SOURCED [R1] |
| Full brightness | "Peak brightness is achieved when connected to power and using a white background" | SOURCED [R2] |
| In the box | 2 x USB-C to USB-C cable, 1 x mini-HDMI to HDMI cable, 1 x power adapter, the manual | MAKER [M1] |
| The adapter in the box | A customer writes that it "states several voltages, from 3V to 20V". | MAKER [M1] (a customer's question). The label was not read. |
| Does it take 5 V only, or more? | NOT CONFIRMED. It runs on 5 V from a laptop port. A power delivery source can also give 9 V, 15 V and 20 V. No source says which voltage the monitor asks for. | Bench test 1 |
| Current at 5 V | 1.0 A to 3.0 A. | ESTIMATED: 5.1 W and 14.9 W divided by 5 V |
| Does it start when power arrives? | NOT CONFIRMED | Bench test 3 |
| The user manual | Not found. The maker sends it by e-mail on request. | MAKER [M1] |

## 3. What the BC-250 gives

| Item | Value | Status |
| --- | --- | --- |
| Video output | 1 x DisplayPort 1.4, full size. No HDMI. | SOURCED [B1][B4] |
| USB-C, DisplayPort alternate mode | None. "board doesn't have USB-C DisplayPort alt mode" | SOURCED [B2] |
| USB ports | 2 x USB 3.0 and 2 x USB 2.0, all type A | SOURCED [B1][B4] |
| Current of a port, by the standard | 0.5 A (2.5 W) for USB 2.0, 0.9 A (4.5 W) for USB 3.0 | STANDARD (USB 2.0, USB 3.0) |
| Current of a port, on this board | No document gives a number for each port. One user: "rear USB 3.0 ports are specced for 5 W total". | SOURCED [B3] (one user, no measurement) |
| The 5 V of the board | Weak. "the ports are very anemic when it comes to power delivery". Some boards have no 5 V at the ports. | SOURCED (summary) [B5]. SOURCED [B3]. See `docs/research/pc-panel-and-front-usb.md` A1. |
| Audio | "Audio over DisplayPort (compatibility varies)". No analogue output. | SOURCED [B1] |

Can a port run the monitor?

| Source | Power it gives | The monitor needs | Result |
| --- | --- | --- | --- |
| One USB 2.0 port of the board | 2.5 W | 5.1 W to 14.9 W | No |
| One USB 3.0 port of the board | 4.5 W by the standard. 5 W for the two ports together (one user). | 5.1 W to 14.9 W | No |
| A powered hub, port of type A | 4.5 W (USB 3.0). 7.5 W if the port is a charging port (1.5 A). | 5.1 W to 14.9 W | No for a plain port. A charging port runs the monitor only below about 25 % brightness. ESTIMATED from [R1]. |
| A powered hub, port of type C at 5 V and 3 A | 15 W | 14.9 W at full brightness | No margin. Not recommended. ESTIMATED. |
| The 5 V rail of the supply | 24 A (120 W together with 3.3 V) | 3.0 A | The rail has sufficient power. The problem is the plug: see section 4. |

## 4. Ways to power the monitor from the supply

NOT FINISHED. The parts in this section need more sources.

The supply is the EVGA SuperNOVA 1000 P5: 5 V at 24 A, 12 V at 83.3 A, standby 5 V at 3 A. MAKER [P1].

| Way | Parts | For | Against | Status |
| --- | --- | --- | --- | --- |
| (1) A 12 V to USB-C power delivery board | Example: Coolgear CG-PDC65W-PCBA. Input 12 V to 24 V (9 V to 28 V limits) on a 2-pin terminal. Output 5 V 3 A, 9 V 3 A, 12 V 3 A, 15 V 3 A, 20 V 3.25 A. Buck-boost, so 20 V comes from a 12 V input. 49 mm x 45 mm x 13 mm. | It gives each voltage of the maker's answer. It is the kind of source that the maker asks for. It goes off with the supply. | The vendor sells it as a development product. The price and the stock were not read (the product page refused the request). | MAKER [C1] (the data sheet) |
| (2) Plain 5 V from the 5 V rail to a USB-C plug | A lead from a SATA or a four-pin connector to a USB-C plug | The fewest parts | The monitor can ask for power delivery and get plain 5 V. The plug needs the correct resistors on its CC pins. At full brightness the draw is at the 3 A limit of the plug. | NOT CONFIRMED. No part was found yet. |
| (3) The monitor's own mains adapter | The adapter in the box, outside the cabinet or inside | The maker's part | The brief says: do not add mains wiring inside the shell to hide an adapter. Outside, it does not go off with the supply. | The brief, section "Electrical integration boundaries" |

Risks to examine (NOT FINISHED):

- A monitor that asks for power delivery and gets plain 5 V.
- Back-feed through the video lead.
- The resistor values on the CC pins of a plain 5 V source (USB Type-C specification). Not read yet.

What goes off at a shutdown: the 5 V rail and the 12 V rail go off when the adapter of the power
button releases `PS_ON` (`docs/research/bc250-power-button.md`). Thus way (1) and way (2) go off with
the supply. STANDARD (ATX12V design guide, in that note).

## 5. The video path

NOT FINISHED.

| Path | Parts | Facts | Status |
| --- | --- | --- | --- |
| (A) DisplayPort to mini-HDMI | An active DisplayPort to HDMI 2.0 adapter and an HDMI to mini-HDMI cable | A passive adapter is "Limited to 1080p60 or 1440p60 typically". An active adapter "Supports 4K60Hz". With an active adapter the sound is "silent on kernels without the DP audio clock fix". "Kernel 7.2 and newer fix it completely". One active unit (UGREEN, 8K) is "verified working". | SOURCED [B2] |
| (B) DisplayPort to the USB-C port of the monitor | An adapter that makes DisplayPort alternate mode from a DisplayPort source. Example: Delock 61059, "Adapter DisplayPort female to USB Type-C male (DP Alt Mode) 4K with PD 85 W", a tail of 15 cm, 3840 x 2160 at 60 Hz. | One plug at the monitor for video and power. No mini-HDMI plug, which is the weak connector. The power comes from a power delivery source on the adapter. | SOURCED (summary) [D1]. The maker's page refused the request. |
| (B) with a cable | Cables "DisplayPort to USB-C with power" from retail brands with no data sheet | The same idea in one cable, with a USB-A plug for the power | SOURCED (summary) [D2] |

Not confirmed for the two paths:

- 3840 x 2400 at 60 Hz through HDMI 2.0. The pixel clock is about 593 MHz with reduced blanking,
  and the limit of HDMI 2.0 is 600 MHz. ESTIMATED: 4000 x 2469 x 60. The value needs a check.
- 3840 x 2400 through the adapter of path (B). Its data gives 3840 x 2160.
- The HDMI version of the mini-HDMI input of the monitor.
- Right-angle plugs for each path. The fit study found straight plugs 15 mm to 19 mm too long.

## 6. Recommendation

NOT FINISHED. Provisional: way (1) for the power. The video path waits for the open points of section 5.

## 7. Bench tests on the real unit

1. Put a USB-C power meter between the supplied adapter and the monitor. Write down the voltage
   that the monitor asks for, and the current at 0 %, 25 %, 50 % and 100 % brightness.
2. Feed the monitor with plain 5 V at 3 A. Write down if it starts, and the brightness at which it
   flickers.
3. Remove the power and connect it again. Write down if the monitor starts with no button press.
4. Connect the BC-250 through the chosen video path. Write down the mode (3840 x 2400 at 60 Hz or
   not) and if the sound works.

NOT FINISHED: more tests follow from sections 4 and 5.

## 8. Sources

| No. | Source | What it is |
| --- | --- | --- |
| M1 | https://uperfect.com/products/16-inch-4k-sunlight-readable-monitor | The maker's product page: the parameter table, the box contents, and the maker's answers to customers |
| R1 | https://www.linuxlinks.com/uperfect-ucolor-t6-review/ | A review with a measurement of the draw at five brightness levels (a chart) |
| R2 | https://www.amazon.com/dp/B0F99H1KSL | The retail listing of the owner's unit: power, voltage, the note on peak brightness |
| B1 | https://elektricm.github.io/amd-bc250-docs/hardware/specifications/ | Community documentation of the board: ports, video, audio |
| B2 | https://elektricm.github.io/amd-bc250-docs/troubleshooting/display/ | Community documentation: adapters, sound through DisplayPort, no USB-C video |
| B3 | https://github.com/katzzero/bc250-unofficial-community-guide/blob/main/10-troubleshooting.md | Community guide: USB power, the 5 V rail, sound |
| B4 | https://github.com/katzzero/bc250-unofficial-community-guide/blob/main/01-hardware-specs.md | Community guide: the connector table |
| B5 | https://www.reddit.com/r/BC250Gaming/comments/1s07n2c/a_simple_fix_for_most_broken_usb_ports/ | Summary only |
| P1 | https://www.evga.com/support/manuals/files/220-P5-1000-X1.pdf | The manual of the supply: the table of the rails |
| C1 | https://www.coolgear.com/wp-content/uploads/CG-PDC65W-PCBA_Technical-Data-Sheet-06-250613.pdf | Data sheet of a 12 V to USB-C power delivery board |
| D1 | https://www.delock.com/produkt/61059/merkmale.html | Summary only: a DisplayPort to USB-C adapter with a power input |
| D2 | Retail listings of DisplayPort to USB-C cables with power | Summaries only |

## 9. Still to read

- The USB Type-C specification, or a maker's application note, for the CC resistors of a 5 V source.
- A second 12 V to USB-C power delivery part, with a price.
- The Delock data sheet of item 61059 from a second place, and one more adapter of the same kind.
- Right-angle USB-C and mini-HDMI plugs and adapters, with their sizes.
- An active DisplayPort to HDMI 2.0 adapter with a maker's data sheet.
- The timing of 3840 x 2400 at 60 Hz (the exact pixel clock).
- Back-feed through HDMI.
