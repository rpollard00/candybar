# Audio: speakers, enclosure, amplifier and volume control

Research date: 2026-11-14. Each source was read on this date.

**DRAFT. The work stopped before it was complete. Each section that is not complete has the words NOT FINISHED.**

This note answers the owner's questions of 2026-11-14 on the speakers and the volume control.
Nothing was tested for this note. No part was bought.

## Status tags

| Tag | Meaning |
| --- | --- |
| MAKER [id] | From the maker of the part: a product page or a data sheet. |
| SOURCED [id] | Written in the source with that number in section 8. The page was read. |
| SOURCED (summary) | Read in a search-result summary only. |
| BUILD | A value of this repository: `cad/candybar/shell/dims.py`, `fit.py`, or the fit report. |
| ESTIMATED | Calculated or reasoned here. The method is given. |
| NOT CONFIRMED | No source says it. A test must show it. |

## 1. The room in the hood as it is

The front opening of the hood is 148 mm high. From the bottom up it has five parts.

| Part | Height | Named value | Status |
| --- | --- | --- | --- |
| Sill | 17.0 mm | `hood_sill_h` | BUILD |
| Hood band | 67.9 mm | `z_band_top` less `hood_sill_h` | BUILD (calculated from `profiles.hood`) |
| Marquee lip | 6.0 mm | `hood_rail_h` | BUILD |
| Marquee opening | 36.1 mm (window 34 mm) | `hood_marquee_open_h` | BUILD |
| Top bar | 21.0 mm | `hood_bar` | BUILD |

| Item | Value | Status |
| --- | --- | --- |
| Speaker form | 95.9 mm wide x 57.9 mm high, 13 mm proud of the band | BUILD (fit report, print table) |
| Height of the form | The band (67.9 mm) less a gap of 4 mm at the foot and 6 mm at the head | BUILD (`speaker_foot_gap`, `speaker_head_gap`) |
| Largest round frame | 53.9 mm. This is the height of the form less a margin of 2 mm at each side. | BUILD (fit report). Confirmed: 57.9 less 4.0. |
| What limits the frame | The height of the form. The width does not: the form is 95.9 mm wide. | ESTIMATED from the two values above |
| Depth behind the band | 109.1 mm, to the skin or to the room of the marquee modules | BUILD (fit report) |
| Centre of each form | x 136.4 mm from the centre line, z 475.3 mm | BUILD (fit report data) |
| Wall of the band | 4.0 mm | BUILD (fit report, "Wall") |

Thus the earlier number of 53.9 mm is correct. The depth is not a limit for a small driver. An oval
driver (for example 50 mm x 90 mm) can use the width of the form. NOT FINISHED: no oval driver was
read yet.

## 2. Drivers for the hood as it is (40 mm to 52 mm)

NOT FINISHED. Only one driver has a complete row.

| Driver | Frame | Depth | Impedance | Power | Range | Sensitivity | Fs, Qts, Vas | Price | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Dayton Audio DMA45-8 | 46 mm x 46 mm, holes on a circle of 50.2 mm | 26.1 mm | 8 ohm | 10 W RMS, 20 W maximum | 150 Hz to 20 kHz | 76.9 dB at 2.83 V and 1 m | 150.7 Hz, 0.59, 0.002 ft3 (0.06 l) | USD 11.99 (list) | MAKER [A1]. The frame and the depth are from `docs/design/hardware-list.md` 2.5. |
| Visaton FRS 5 X, 8 ohm | Not read | Not read | 8 ohm | 5 W | 120 Hz to 20 kHz | 86 dB (1 W, 1 m) | Not read | Not read | From `docs/design/hardware-list.md` 2.5. The data sheet is still to read. |
| Dayton Audio CE32A-8 | 32 mm x 32 mm | 15.5 mm | 8 ohm | 2 W | 240 Hz to 20 kHz | 77.9 dB | Not read | Not read | From `docs/design/hardware-list.md` 2.5 |

## 3. Drivers for an expanded hood band (57 mm, 66 mm, 77 mm)

NOT FINISHED.

| Driver | Size | Impedance | Power | Range | Sensitivity | Fs, Qts, Vas | Price | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Dayton Audio DMA70-4 (probably: the page gives a nominal diameter of 2.5 inch and 4 ohm) | 2.5 inch | 4 ohm | 20 W RMS | 110 Hz to 20 kHz | 86.2 dB at 2.83 V and 1 m (2 W into 4 ohm) | 113.0 Hz, 0.44, 0.02 ft3 (0.57 l) | USD 20.99 (list) | MAKER [A2]. Confirm the model. The frame, the cut-out and the depth were not on the page. |
| Dayton Audio DMA80-8 | 3 inch | 8 ohm | 25 W | 90 Hz to 20 kHz | Not read | Fs 97.6 Hz | Not read | SOURCED (summary) [A3] |

What the hood band must give, as a rule (ESTIMATED from section 1): the band must be as high as
the frame of the driver and 14 mm more (4 mm of margin, 4 mm at the foot, 6 mm at the head). A frame
of 66 mm needs a band of 80 mm, which is 12 mm more than the band has. A frame of 77 mm needs
91 mm, which is 23 mm more. The frame sizes of real drivers are still to read.

Still to do: the 2 inch drivers (57 mm), a passive radiator or a small woofer in the cabinet with
small drivers in the hood, and the gain in low end and level in plain numbers.

## 4. The enclosure

NOT FINISHED. Nothing was read yet. The printed hood is not sealed, so each driver needs a sealed
pod behind the grille. The volume follows from Vas and Qts of the chosen driver.

## 5. The amplifier and the audio source

NOT FINISHED.

| Item | Fact | Status |
| --- | --- | --- |
| Audio outputs of the BC-250 | "Audio over DisplayPort (compatibility varies)". The board has no analogue output and no audio header in the connector list. | SOURCED [B1][B6] |
| Sound through an active DisplayPort to HDMI adapter | "silent on kernels without the DP audio clock fix". "Kernel 7.2 and newer fix it completely". | SOURCED [B2] |
| Level of the sound through DisplayPort | "DP audio volume is very low, requires massive amplifier gain." | SOURCED [B3] (a user report in the guide) |
| The fallback of the community | "USB audio adapter ($10) as fallback." | SOURCED [B3] |
| Audio from the monitor | The monitor has a 3.5 mm output and two speakers of 8 ohm and 1 W. | MAKER [M1] |
| Rails of the supply | 5 V at 24 A, 12 V at 83.3 A | MAKER [P1] |
| Amplifier boards | PAM8403 (5 V) and TPA3110D2 (12 V) are in `docs/design/hardware-list.md` 2.5. | Still to read: the data sheets, a board with a volume input on a DC voltage, the noise on a PC rail. |

## 6. The volume control

NOT FINISHED. Nothing was read yet. The four ways and the four places of the brief are still to compare.

## 7. Recommendation

NOT FINISHED.

## 8. Sources

| No. | Source | What it is |
| --- | --- | --- |
| A1 | https://www.daytonaudio.com/product/1613/dma45-8-1-1-2-dual-magnet-aluminum-cone-full-range-driver-8-ohm | Maker's product page |
| A2 | https://www.daytonaudio.com/product/1616/dma58-8-2-dual-magnet-aluminum-cone-full-range-driver-8-ohm | Maker's product page. The address names the DMA58-8, but the page shows a 2.5 inch driver of 4 ohm. |
| A3 | https://www.daytonaudio.com/images/resources/295-587--dayton-audio-dma80-8-specification-sheet.pdf | Summary only. The file did not download as a PDF. |
| B1 | https://elektricm.github.io/amd-bc250-docs/hardware/specifications/ | Community documentation of the board |
| B2 | https://elektricm.github.io/amd-bc250-docs/troubleshooting/display/ | Community documentation: sound through DisplayPort |
| B3 | https://github.com/katzzero/bc250-unofficial-community-guide/blob/main/10-troubleshooting.md | Community guide: sound |
| B6 | https://github.com/mothenjoyer69/bc250-documentation/blob/main/hardware.md | Connector reference of the board |
| M1 | https://uperfect.com/products/16-inch-4k-sunlight-readable-monitor | The maker's page of the monitor |
| P1 | https://www.evga.com/support/manuals/files/220-P5-1000-X1.pdf | The manual of the supply |

## 9. Still to read

- Data sheets with dimension drawings: Dayton DMA45, DMA58, DMA70, DMA80 and ND65. Visaton FRS 5 X,
  SC 4.7, SC 5.9, FRS 7 and FRS 8. Peerless and Tang Band drivers of 1.5 inch to 3 inch. Tang Band
  modules with a passive radiator.
- Passive radiators of the Dayton DMA series.
- Amplifier data sheets: PAM8403, TPA3110D2, MAX9744, and one board of each.
- A source on ground loops with a PC supply.
- Potentiometer and encoder data sheets (shaft, bushing, depth), and USB volume knobs.
