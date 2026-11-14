# The marquee as a display

Research date: 2026-11-14.

**DRAFT. The work stopped before the research for this note started. Only section 1 has confirmed values. Each other section has the words NOT FINISHED.**

The base plan is a lit window with printed art. The owner asked on 2026-11-14 for a scrolling or
LED-pixel display, if a part that can be bought works. No source was read for this note yet.

## Status tags

| Tag | Meaning |
| --- | --- |
| BUILD | A value of this repository: `cad/candybar/shell/dims.py`, `fit.py`, or the fit report. |
| NOT CONFIRMED | No source was read. A statement with this tag is from memory and must be confirmed. |

## 1. The window as it is

| Item | Value | Status |
| --- | --- | --- |
| Window | 352 mm x 34 mm, straight | BUILD (fit report; `marquee_h`) |
| Opening between the lip and the top bar | 36.1 mm high | BUILD (`hood_marquee_open_h`) |
| Room behind the cover | 82.3 mm deep | BUILD (fit report) |
| Depth that the layout keeps for the light modules | 25 mm | BUILD (`mq_led_depth` in `cad/params/hardware.csv`, provisional) |
| Cover | 3 mm | BUILD (`marquee_cover_t`) |
| Position | Upright, in the plane of the hood band, 3.5 mm to 4.8 mm behind the hood front. Its lower edge is at z 517.3 mm. | BUILD (`docs/blueprint/index.md`, fit report data) |
| The plan of the layout | Eleven modules of 32 mm (352 mm) | BUILD (`marquee_module`) |
| The parts round it | A top bar of 21 mm above. A lip of 6 mm, the hood band of 67.9 mm and a sill of 17 mm below. The opening of the hood is 148 mm high in total. | BUILD |

## 2. The kinds of display

NOT FINISHED. No source was read. The rows are a plan of the research, from memory.

| Kind | What to confirm | Status |
| --- | --- | --- |
| LED matrix panels (HUB75) | The standard sizes by pixel pitch. The smallest common panel is probably 64 mm high, which is more than the window of 34 mm. | NOT CONFIRMED |
| Single-colour matrix modules of 32 mm x 32 mm (8 x 8 LEDs) | Eleven of them are 352 mm x 32 mm, which is the window. They give text of 8 pixels in one colour. | NOT CONFIRMED |
| Addressable LED matrices, rigid and flexible | The pitch and the sizes. Most are probably too high for 34 mm. | NOT CONFIRMED |
| Stretched bar LCD panels with HDMI | The sizes near 350 mm wide. They are probably 55 mm high or more. | NOT CONFIRMED |
| OLED and e-paper bars | Probably too small or too slow. | NOT CONFIRMED |

## 3. What drives it

NOT FINISHED. To read: the products made for arcade marquees and their software, open firmware for
a microcontroller, a second video output from the one DisplayPort of the BC-250, USB displays on
Linux, and how the picture follows the game.

One fact is confirmed: the BC-250 has one DisplayPort 1.4 output and no other video output
(https://elektricm.github.io/amd-bc250-docs/hardware/specifications/, read on 2026-11-14).

## 4. The best candidates and their windows

NOT FINISHED.

## 5. Recommendation

NOT FINISHED.

## 6. Still to read

- HUB75 panel sizes from a maker or a seller with data sheets.
- Single-colour matrix modules (MAX7219 type): size, depth, current.
- Bar LCD panels with HDMI: active area, outline, depth, power, brightness.
- Products for arcade marquees and the software that they work with on Linux.
- Open firmware for LED matrices on a microcontroller.
- A second display from one DisplayPort (a multi-stream hub) and USB display adapters on Linux.
- Diffuser and tinted cover material for an LED matrix.
