# The marquee as a display

Research date: 2026-11-14. Each source was read on this date.

The base plan is a lit window with printed art. The owner asked on 2026-11-14 for a scrolling or
LED-pixel display, if a part that can be bought works. This note gives the kinds of display, what
drives each, the window that each needs, and the smallest change of the hood that lets a better
display fit. It extends `docs/design/hardware-list.md` section 2.6.

Nothing was tested for this note. No part was bought. Section 9 lists the tests that decide.

## Status tags

| Tag | Meaning |
| --- | --- |
| MAKER [id] | From the maker of the part: a product page, a wiki page or a data sheet. |
| SOURCED [id] | Written in the source with that number in section 10. The page was read. |
| SOURCED (summary) | Read in a search-result summary only. The page was not read. |
| BUILD | A value of this repository: `cad/candybar/shell/dims.py`, `fit.py`, the fit report or the blueprint. |
| ESTIMATED | Calculated or reasoned here. The method is given. |
| NOT CONFIRMED | No source says it. A test or a measurement must show it. |

## 1. Summary

1. **The window as built is 352 mm x 34 mm.** No full-colour display that can be bought is that low.
   The lowest LED matrix panel is 80 mm high. The lowest bar LCD of a useful width is 54 mm to 64 mm
   high.
2. **One kind fits the window now:** a row of single-colour LED modules of 32 mm, with 88 x 8 pixels.
   It shows scrolling text in one colour. It shows no art.
3. **The display that the arcade world uses is an LED matrix of 128 x 32 pixels.** At a pitch of
   2.5 mm it is 320 mm x 80 mm. A finished product (Pixelcade) and an open firmware (ZeDMD) drive it
   on USB, and each follows the selected game. It needs 46 mm more window height.
4. **A bar LCD needs 20 mm to 30 mm more height,** and it needs a second video output. The BC-250
   gives one through a multi-stream hub (two screens at most). This is the weaker way: it depends on
   the hub and on the screen set-up of the system.
5. **Recommendation:** if the owner accepts a hood that is 46 mm higher, design the window for the
   LED matrix of 320 mm x 80 mm. If not, keep the window of 352 mm x 34 mm for the lit art, with the
   single-colour text row as the scrolling option. In each case the same opening takes the plain lit
   window.
6. **Test before the form changes.** Two panels and a controller cost about EUR 39 (one wiki's value
   of 2024). Run them on the owner's system first.

## 2. The window as it is

| Item | Value | Status |
| --- | --- | --- |
| Window | 352 mm x 34 mm, straight | BUILD (fit report, `marquee_h`) |
| Opening between the lip and the top bar | 36.1 mm high | BUILD (`hood_marquee_open_h`) |
| Room behind the cover | 82.3 mm deep | BUILD (fit report) |
| Depth that the layout keeps for the light modules | 25 mm | BUILD (`mq_led_depth` in `cad/params/hardware.csv`, provisional) |
| Cover | 3 mm | BUILD (`marquee_cover_t`) |
| Position | Upright, in the plane of the hood band, 3.5 mm to 4.8 mm behind the hood front. Its lower edge is 517.3 mm above the desk. | BUILD (`docs/blueprint/index.md`, fit report data) |
| The plan of the layout | Eleven modules of 32 mm (352 mm) | BUILD (`marquee_module`) |
| Why 352 mm | The top corners of the hood opening limit the straight width at the top of the window | BUILD (`profiles.marquee_window`) |

The opening of the hood is 148 mm high. From the bottom up: the sill (17 mm), the hood band with the
speakers (67.9 mm), the lip (6 mm), the marquee opening (36.1 mm) and the top bar (21 mm). BUILD.

## 3. The kinds of display

| Kind | Standard sizes near the window | Depth | Power | Brightness | Behind a tinted front | What drives it | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LED matrix panels (HUB75), full colour | 64 x 32 pixels: 160 mm x 80 mm (pitch 2.5 mm), 192 mm x 96 mm (3 mm), 256 mm x 128 mm (4 mm), 320 mm x 160 mm (5 mm). Also 128 mm x 128 mm (2 mm, 64 x 64) and 240 mm x 120 mm (2.5 mm, 96 x 48). No panel of this maker has less than 32 rows, and none is lower than 80 mm. | About 15 mm (the finished product of row 2) | 5 V. 2.5 A and 12 W at most for a panel of 160 mm x 80 mm. | Not stated | Made for it: see row 2 | A controller with the HUB75 connector: an ESP32, a Raspberry Pi Pico, a Raspberry Pi | MAKER [W1][W2] |
| The same as a finished marquee (Pixelcade LED) | 128 x 32 pixels. Pitch 2.5 mm: 317 mm x 79 mm x 15 mm. Pitch 3 mm: 380 mm x 97 mm x 15 mm. Larger sizes to 976 mm. | 15 mm | A power lead for a PC supply exists ("Pixelcade SATA power cable") | Not stated | The maker recommends grey tinted acrylic of 3 mm in front, with a light transmission of 36 % | Its own controller on USB | MAKER [P1][P2]. SOURCED [K1] for USB. |
| Single-colour LED modules (MAX7219 type) | A board of four modules: 128 mm x 33 mm, 32 x 8 pixels, red. Single modules of 32 mm exist. Eleven modules are 352 mm x 33 mm and 88 x 8 pixels. | Not read | 4.5 V to 5 V. The current was not read. | Not read | A red or smoke cover. NOT CONFIRMED. | Three signal wires from a small controller. The boards connect in a chain. | SOURCED (summary) [H1] |
| Addressable LED matrices (rigid and flexible) | Not read. The common flexible size is probably 8 x 32 LEDs on 80 mm x 320 mm. | - | - | - | - | A small controller | NOT CONFIRMED: no source was read. It is from memory. |
| Bar LCD with HDMI | 8.8 inch (1920 x 480): about 217 mm x 54 mm. 11.26 inch (1920 x 440): about 279 mm x 64 mm. 11.9 inch (1480 x 320): about 295 mm x 64 mm. 12.6 inch (1920 x 515): about 309 mm x 83 mm. 14 inch (3840 x 1100): about 342 mm x 98 mm. These are the lit areas. The bodies are larger. | Not stated | From USB. Not stated in watts. | Not stated | An LCD loses contrast behind a tint. Use a clear cover. ESTIMATED. | A second video output of the computer | MAKER [L1][L2] for two types and their prices. SOURCED (summary) [L3] for the others. The lit areas are ESTIMATED from the diagonal and the pixel count. |
| The same as a finished marquee (Pixelcade LCD) | 1920 x 360 pixels. 24 inch and 28 inch (613 mm wide and more) | - | - | - | - | Its own computer, on the network | MAKER [P1]. Too large for this cabinet. |
| OLED and e-paper bars | Not read | - | - | - | - | - | NOT CONFIRMED: not examined. From memory, OLED bars are much smaller than the window, and e-paper is too slow for a scroll. |

## 4. What drives it, and how the picture follows the game

### 4.1 Products and firmware for arcade marquees

| Name | What it is | Works with | How it follows the game | Status |
| --- | --- | --- | --- | --- |
| Pixelcade LED | A finished LED marquee of 128 x 32 pixels with its controller. "It connects by USB". The software has "thousands of marquee designs" in 8-bit form. | Linux front ends: Batocera, RCade, EmuELEC, RetroPie, RecalBox. Windows front ends: HyperSpin, BigBox, CoinOps, Attract Mode, GameEx, RetroBat. In Batocera it is built in since version 33, and x86_64 is in the list of platforms. | It shows the art of the selected game. With no art it shows a generic marquee of the emulator or scrolling text. It has a REST interface for other programs. | MAKER [P1]. SOURCED [K1]. The price was not read: the shop page does not show it. |
| ZeDMD | An open firmware for an ESP32 with two LED matrix panels. The result is 128 x 32 pixels. It connects by USB-C. | Batocera 40 and later (the service `dmd_real`) | "When you switch systems or select a game", the image of the game shows, or its name if there is no image. | SOURCED [K2] |
| A second screen as the marquee | A bar LCD on a second video output | Batocera 40 and 41: the marquee theme under "multiple screen" | It shows the images that the front end has for the game | SOURCED [K1] |
| A microcontroller with a matrix library | An ESP32 with the library `ESP32-HUB75-MatrixPanel-DMA` for LED matrix panels. A library for the single-colour modules exists too. | Each system: it is a USB serial device | The computer sends the text or the picture. It needs a program on the computer. | MAKER [W1] for the first library. The rest is ESTIMATED. |

### 4.2 The owner's system

The brief names CachyOS as the starting reference. The front end is not chosen.

| System | What is ready | Status |
| --- | --- | --- |
| Batocera | Pixelcade, ZeDMD and a second screen are built in | SOURCED [K1][K2] |
| A plain Linux with the ES-DE front end | ES-DE runs scripts at events: `game-start`, `game-end`, `game-select`, `system-select` and more. A script gets the path of the game, its name and the name of the system. The scripts are in `~/ES-DE/scripts/`, and the setting "Enable custom event scripts" turns them on. A script can thus send the name of the game to each display of section 4.1. | SOURCED [E1]. That Pixelcade or ZeDMD works this way on the owner's system is NOT CONFIRMED: Pixelcade does not list ES-DE. |
| A game session with no front end | No source was found for a hook | NOT CONFIRMED |

### 4.3 A second video output from the BC-250

| Way | Facts | Status |
| --- | --- | --- |
| A DisplayPort multi-stream hub | "Maximum 2 screens" on the BC-250. It "Shares bandwidth between displays". One hub, the StarTech MST14DP122DP (DisplayPort 1.4), "Worked consistently with different monitors and DP cables". Two hubs for DisplayPort 1.2 gave only a mirror image. | SOURCED [B6] |
| Is the bandwidth sufficient? | The main screen (3840 x 2400 at 60 Hz) needs 14.2 Gbit/s. A bar LCD of 1920 x 480 needs about 1.5 Gbit/s. The sum is below the 25.9 Gbit/s of DisplayPort 1.4. | ESTIMATED: pixel clock times 24 bits. The limit is recalled from the standard. |
| A USB display adapter (DisplayLink) | "Works for desktop use". "Not suitable for gaming". It "Does not work in Steam Deck game mode". | SOURCED [B6] |
| A bar display that is a USB device | Not examined | NOT CONFIRMED |
| The board itself | One DisplayPort 1.4 output. No second output. | SOURCED [B1] |

A display on USB (the LED matrix) does not use the video output. Thus it does not depend on the hub
and on the screen set-up of the game session. This is the main reason to prefer it.

## 5. The candidates and the window that each needs

### Candidate A: an LED matrix of 128 x 32 pixels at a pitch of 2.5 mm

| Item | Value | Status |
| --- | --- | --- |
| Parts, bought as a product | Pixelcade LED, size P2.5: 317 mm x 79 mm x 15 mm, with its controller and software | MAKER [P2] |
| Parts, built | Two panels of 64 x 32 pixels, 160 mm x 80 mm each (for example Waveshare RGB-Matrix-P2.5-64x32), an ESP32 board and jumper wires. "Total cost was about 39€ as of April 2024." | MAKER [W2]. SOURCED [K2]. |
| The lit area | 320 mm x 80 mm | MAKER [W2] |
| Window | 321 mm x 81 mm (0.5 mm of clearance at each side) | PROVISIONAL |
| Depth | 15 mm for the panel. Reserve 40 mm for the connectors and the flat cable behind it. The room is 82.3 mm deep. | MAKER [P2]. The 40 mm is ESTIMATED. |
| How it mounts | A printed frame behind the cover holds the two panels by their rear screw holes | NOT CONFIRMED: the hole positions and the thread were not read. Measure the panel. |
| Cover | Grey tinted acrylic, 3 mm, with a light transmission of about 36 % (the Pixelcade maker's advice). The tint hides the panel when it is off and makes the dots softer. | MAKER [P2] |
| Power | 5 V. At most 2.5 A for each panel, 5 A and 24 W for the two at full white. The firmware page says that a display of this size can run from the USB port with no supply, so the usual draw is much lower. | MAKER [W2]. SOURCED [K2]. |
| From the supply | The 5 V rail, on a Molex lead. One SATA connector gives 4.5 A at 5 V, which is less than the largest draw. | `docs/research/pc-panel-and-front-usb.md` A3 |
| At a shutdown | It goes off with the 5 V rail | `docs/research/bc250-power-button.md` section 5 |
| Data | One USB lead from the controller to the board or the hub | SOURCED [K1][K2] |
| Not confirmed | The brightness in cd/m2. The thickness and the holes of a bare panel. The software on the owner's system. The price of the Pixelcade product. | - |

### Candidate B: a bar LCD

| Item | Value | Status |
| --- | --- | --- |
| Parts | A bar LCD with an HDMI input. Two types with a maker's page: Waveshare "8.8inch Side Monitor" (480 x 1920, no touch, USD 69.99) and Waveshare "11.9inch HDMI LCD" (320 x 1480, with touch, USD 102.99). A type of 11.26 inch with 1920 x 440 is in retail. | MAKER [L1][L2]. SOURCED (summary) [L3]. |
| The lit area | 8.8 inch: about 217 mm x 54 mm. 11.26 inch: about 279 mm x 64 mm. 11.9 inch: about 295 mm x 64 mm. | ESTIMATED from the diagonal and the pixel count |
| Window | The lit area. The body behind the cover is larger. | NOT CONFIRMED: the makers' pages show the outline in a picture only. |
| Also necessary | A multi-stream hub (section 4.3), a second HDMI lead, a USB lead for the power | SOURCED [B6] |
| How it follows the game | Batocera: built in. A different system: a script and a picture viewer on the second screen. | SOURCED [K1]. ESTIMATED. |
| Not confirmed | The outline, the depth, the brightness and the power. That the hub works with the owner's adapter in the same chain. That the game session keeps the second screen. | - |

### Candidate C: a row of single-colour modules in the present window

| Item | Value | Status |
| --- | --- | --- |
| Parts | Two boards of four modules (128 mm x 33 mm each) and three single modules of 32 mm. Together 352 mm and 88 x 8 pixels. A small controller on USB. | SOURCED (summary) [H1]. That the single modules chain with the boards of four is ESTIMATED. |
| Window | 352 mm x 33 mm. It is the window as built. The opening of 36.1 mm takes the boards of 33 mm. | BUILD. SOURCED (summary) [H1]. |
| What it shows | Text of one line in one colour: the name of the game, a greeting, a score | ESTIMATED |
| Not confirmed | The depth, the current, the colours that can be bought, the fit of the board's edge connectors between the modules | - |

### The lit window (the base plan)

It fits each of the three windows. A strip and a diffuser are in `docs/design/hardware-list.md` 2.6.

## 6. The smallest change of the hood for a better display

The marquee opening is the window and 2.1 mm more (36.1 mm for 34 mm). The hood opening is the sum
of its five parts. If the speakers and the other parts stay, each mm of window is one mm of hood.
BUILD for the parts. ESTIMATED for the sums.

| Display | Window (width x height) | More window height than now | Hood opening | Hood height over the seam, as a share of the body width | What the change gives |
| --- | --- | --- | --- | --- | --- |
| Lit art, or the single-colour text row | 352 mm x 34 mm | 0 | 148 mm | 0.30 | Text in one colour that scrolls. No art. |
| A bar LCD of 8.8 inch | 217 mm x 54 mm | 20 mm | 168 mm | 0.34 | Full-colour art and video, on 62 % of the width of the present window. |
| A bar LCD of 11.26 inch or 11.9 inch | 279 mm to 295 mm x 64 mm | 30 mm | 178 mm | 0.36 | Full-colour art and video, on 79 % to 84 % of the width. |
| An LED matrix of 128 x 32 pixels, pitch 2.5 mm | 320 mm x 80 mm | 46 mm | 194 mm | 0.39 | The LED-pixel marquee of the arcade products, on 91 % of the width. |

Notes for the agent that judges the form:

- The smallest step that gives a better display is 20 mm, and it gives a small LCD. The first step
  that gives a display of nearly the full width is 30 mm (an LCD). The LED-pixel display needs 46 mm.
- The LCD rows give the lit area. The body of an LCD is larger, so the opening behind the cover is
  more than the window. Measure the part.
- The references have a hood height of 0.25 to 0.33 of the body width (`docs/blueprint/index.md`,
  the proportion table). This cabinet has 0.30 now. With 30 mm more it has 0.36. With 46 mm more it
  has 0.39. The owner said on 2026-11-11 that the cabinet has sufficient height.
- A wider window is not necessary: each display is narrower than 352 mm. The window can be narrower
  and higher. Lower in the opening, the opening is wider.
- Height can also come from the other parts of the opening: a hood band of 60 mm in place of 67.9 mm
  (with a speaker of 46 mm, `docs/research/audio.md` section 10) gives 7.9 mm.
- A larger speaker asks for the same height (`docs/research/audio.md` section 11). The two wishes
  compete.
- A way with no change of height: a display in the middle of the hood band, in the place of the logo
  form. The glossary has the marquee there. The free zone between the two speaker forms is 212 mm
  wide and 67.9 mm high. A bar LCD of 7.9 inch (about 192 mm x 60 mm lit) is the only display of
  this note that is near this size. Its body size is NOT CONFIRMED. The window at the top then stays
  a lit strip.

## 7. Recommendation

The owner decides the look. This is the recommendation and its reasons.

1. **The display to design for: candidate A, the LED matrix of 320 mm x 80 mm.** The reasons:
   - It is the LED-pixel display that the owner asked for.
   - It can be bought as a finished product, and as two standard panels with an open firmware.
   - It is a USB device. It does not use the one video output of the board.
   - Ready-made software follows the game.
2. **It costs 46 mm of hood height.** If the owner does not accept this, do not take a smaller LED
   matrix: there is none. Keep the window of 352 mm x 34 mm for the lit art, and keep candidate C
   (scrolling text) as an option that fits the same window.
3. **Candidate B (the LCD) is the third choice.** It needs 20 mm to 30 mm, a hub, and a second
   screen that the game session must keep. Each of the three is a risk.
4. **The fallback.** A window of 321 mm x 81 mm takes a lit window with printed art of the same
   size. A window of 352 mm x 34 mm takes the lit art or the text row. Thus the hood can be built
   before the display is bought, in each case.
5. **Buy the test parts first.** Two panels, an ESP32 and a sample of tinted acrylic show the look
   and the software on the owner's system, before the form of the hood changes.

## 8. What the shell must provide

| Item | For candidate A | For the present window (lit art or candidate C) | Status |
| --- | --- | --- | --- |
| Window | 321 mm x 81 mm | 352 mm x 34 mm (as built) | PROVISIONAL. BUILD. |
| Opening between the lip and the top bar | About 83 mm | 36.1 mm (as built) | ESTIMATED: the window and 2.1 mm |
| Depth behind the cover | 40 mm | 25 mm (as kept now) | ESTIMATED. BUILD. |
| Cover | Grey tinted acrylic, 3 mm, in a rebate | Opal acrylic for the lit art, or a tinted cover for the text row | MAKER [P2]. `docs/design/hardware-list.md` 2.6. |
| A frame behind the cover | It holds two panels of 160 mm x 80 mm by their rear holes. It must come out to the rear of the hood for service. | Clips for the modules or for the strip | NOT CONFIRMED: measure the panels |
| A place for the controller | An ESP32 board, about 55 mm x 30 mm, behind the panels | A small controller, or none for the lit art | ESTIMATED: the board size was not read |
| Pins in the plug at the foot of the hood | 5 V and ground for 5 A (two pins each), and a USB lead (four wires, or a USB lead that goes past the plug) | 12 V and ground for a strip. 5 V, ground and USB for the text row. | ESTIMATED |
| The speakers | No change, if the hood is 46 mm higher | No change | Section 6 |

## 9. Tests before the choice

1. Buy two LED matrix panels of 64 x 32 pixels with a pitch of 2.5 mm and an ESP32 board. Put the
   ZeDMD firmware on the board. Connect it to the owner's system.
2. Write down if the system finds the display, and what software sends a picture to it.
3. Hold a sample of grey tinted acrylic of 3 mm in front of the panels. Look at it at 0.5 m, in a
   bright room and in a dark room. The owner judges the look.
4. Measure the 5 V current at the brightness that the owner likes, and at full white.
5. Measure a panel: its thickness, its rear holes and their thread, and the room for its
   connectors.
6. If the owner wants the LCD: connect the hub, the owner's adapter and a second screen. Write down
   if the two screens work in the game session.

## 10. Sources

| No. | Source | What it is |
| --- | --- | --- |
| W1 | https://docs.waveshare.com/LED | A maker's list of LED matrix panels: pitch, pixel count, outline |
| W2 | https://docs.waveshare.com/RGB-Matrix-Px-64x32 | The maker's page of the panels of 64 x 32 pixels: outline, supply, largest power, controllers |
| P1 | https://pixelcade.org/ | The maker's page of the Pixelcade products: sizes, pixel counts, front ends, the REST interface |
| P2 | https://pixelcade.org/mounting/ | The maker's mounting guide: the sizes in mm, the thickness, the tinted acrylic |
| K1 | https://wiki.batocera.org/hardware:lcd_led_marquees | The Batocera wiki: Pixelcade LED and LCD, the second screen, the platforms |
| K2 | https://wiki.batocera.org/hardware:diy_zedmd | The Batocera wiki: the ZeDMD build, its parts, its cost, its firmware |
| H1 | https://handsontec.com/index.php/product/max7219-32x8-dot-matrix-display-module/ | Summary only: a board of four single-colour modules, 128 mm x 33 mm |
| L1 | https://www.waveshare.com/8.8inch-side-monitor.htm | The maker's page of a bar LCD of 8.8 inch: pixel count, HDMI, price |
| L2 | https://www.waveshare.com/11.9inch-hdmi-lcd.htm | The maker's page of a bar LCD of 11.9 inch: pixel count, HDMI, price |
| L3 | Retail listings of bar LCD panels of 8.8 inch, 11.26 inch and 12.6 inch (search of 2026-11-14) | Summaries only: the sizes and the pixel counts |
| B1 | https://elektricm.github.io/amd-bc250-docs/hardware/specifications/ | Community documentation of the board: one DisplayPort output |
| B6 | https://elektricm.github.io/amd-bc250-docs/hardware/display/ | Community documentation: multi-stream hubs, USB display adapters |
| E1 | https://gitlab.com/es-de/emulationstation-de/-/raw/master/INSTALL.md | The ES-DE install guide: the custom event scripts |

## 11. Not confirmed, and sources that were not accessible

| Item | Result |
| --- | --- |
| The brightness of the LED matrix panels | Not on the maker's pages. |
| The thickness, the rear holes and the thread of a bare panel | Not on the maker's pages. |
| The price of the Pixelcade products | Not on the pages that were read. |
| Pixelcade or ZeDMD on the owner's system (not Batocera) | No source. Test 2. |
| A panel of 64 x 32 pixels with a pitch of 2 mm (128 mm x 64 mm) | Not in the maker's list. Two of them are 256 mm x 64 mm, which needs 30 mm in place of 46 mm. Not searched more. |
| The outline, the depth, the brightness and the power of the bar LCD panels | The makers' pages give them in pictures only, or not. |
| The single-colour modules | One seller's summary. No data sheet was read: the depth, the current and the colours are open. |
| Addressable LED matrices, OLED bars and e-paper bars | Not read. The rows in section 3 are from memory. |
| A bar display that is a USB device, on Linux | Not examined. |
| The second screen in the game session of the owner's system | No source. Test 6. |
| The hub with the owner's active adapter behind it | No source. Test 6. |
