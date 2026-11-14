# Audio: the source, the amplifier, the volume control and the speakers

Research date: 2026-11-14. Each source was read on this date.

This note answers the owner's questions of 2026-11-14 on the sound of the cabinet. The owner then
made the question smaller: "let's just figure out if it's small amp or DAC and audio over USB".
Part 1 answers that. Part 2 has the volume control and its place. Part 3 has the speakers, for the
hood as it is and for a larger hood band. It extends `docs/design/hardware-list.md` section 2.5.

Nothing was tested for this note. No part was bought. Section 6 lists the bench tests that decide.

## Status tags

| Tag | Meaning |
| --- | --- |
| MAKER [id] | From the maker of the part: a product page or a data sheet. |
| SOURCED [id] | Written in the source with that number in section 16. The page was read. |
| SOURCED (summary) | Read in a search-result summary only. The page was not read. |
| OWNER | Told by the owner on 2026-11-14, from the owner's own hardware. |
| BUILD | A value of this repository: `cad/candybar/shell/dims.py`, `fit.py`, the fit report or an earlier note. |
| ESTIMATED | Calculated or reasoned here. The method is given. |
| PROVISIONAL | A design value proposed here. A test or the owner can change it. |
| NOT CONFIRMED | No source says it. A test must show it. |

## 1. Summary

1. **The two chains differ in one part only.** Chain (A) takes the sound from the 3.5 mm output of
   the monitor. Chain (B) takes it from a USB sound adapter on the BC-250. The amplifier, the volume
   knob and the speakers are the same. Thus the shell does not wait for this decision.
2. **Recommendation: chain (B).** A USB sound adapter (about USD 5 to 10) on a USB 2.0 port of the
   board, a stereo class D amplifier on the 12 V of the supply, and a volume knob on the amplifier.
   The reasons: the level does not depend on a setting of the monitor, the monitor can change, and
   the 3.5 mm output of the monitor is not documented.
3. **Chain (A) costs nothing to try.** All its parts are in chain (B). Do the bench test of chain (A)
   first. If it passes three checks (section 6), the owner can keep it and save the adapter.
4. **The amplifier:** the Adafruit board with the MAX9744 (USD 19.95). Its volume input takes one
   potentiometer of 1 kΩ on three wires, and the maker says that the potentiometer can be "mounted to
   the outside of a box". The knob then works with each source and with no software.
5. **The knob:** on the USB socket plate, beside the power button (section 8).
6. **Speakers for the hood as it is:** the room takes a round frame of 53.9 mm (confirmed) and
   109 mm of depth. Recommendation: Tectonic TEBM35C10-4 (51.8 mm), in a sealed printed pod of
   0.45 l. The maker gives 154 Hz as the low limit in that volume.
7. **A larger hood band:** 2 mm more height takes a 2 inch driver, which gives no gain. 16 mm more
   takes a 2.5 inch driver or a module with its own passive radiator (80 Hz). 26 mm more takes a
   3 inch driver. A larger sealed driver plays louder in the low end. It does not play much lower.

---

## Part 1. The source and the amplifier

## 2. The main decision: chain (A) or chain (B)

| | Chain (A): the monitor's output | Chain (B): audio over USB |
| --- | --- | --- |
| Path of the sound | BC-250, DisplayPort, the owner's adapter, HDMI, the monitor, its 3.5 mm output, the amplifier, the speakers | BC-250, a USB port, a USB sound adapter, its 3.5 mm output, the amplifier, the speakers |
| Parts to buy | The amplifier | The amplifier and a USB sound adapter |
| Boxes | 1 (the amplifier) | 2 (the adapter and the amplifier) |
| Signal leads | One 3.5 mm lead of about 0.8 m, from the right edge of the monitor to the amplifier, with a right-angle plug at the monitor | One 3.5 mm lead of 0.15 m to 0.3 m. One USB extension of about 0.6 m if the adapter is not at the board. |
| Other leads (the same in the two chains) | The power lead of the amplifier, three wires to the volume potentiometer, two pairs of speaker wires to the plug at the foot of the hood | The same |
| A USB port of the board | Not used | One. A USB 2.0 port is sufficient. The port plan keeps one for this (`docs/research/pc-panel-and-front-usb.md` A3). |
| Depends on the monitor | Yes. A different monitor can have no output, or an output on a different edge. | No |
| Depends on sound through DisplayPort | Yes. It works on the owner's second board with the same adapter. | No. The community documents name it as the fallback: "USB audio adapter ($10) as fallback." |
| The level | NOT CONFIRMED: the volume setting of the monitor can change it. The monitor then has a second volume control that a person cannot reach in the cabinet. | Fixed. The system sets it one time. |
| The monitor's own speakers | NOT CONFIRMED: a plug in the output must make them silent. | Silent: the system sends the sound to the adapter only. |
| Software | None. The sound goes where the picture goes. | The system must have the adapter as its output device. This is one setting. |
| Status of the key facts | Section 2.1 | Section 2.2 |

### 2.1 What is confirmed for chain (A)

| Question | Answer | Status |
| --- | --- | --- |
| Does the board send sound through the adapter? | Yes. "It carries sound: the monitor gets both picture and sound over HDMI." | OWNER (a second BC-250 with the same adapter type) |
| Does the monitor have a 3.5 mm output? | Yes. "1 × 3.5mm AUX for audio output". It is on the right edge, about 30 mm above the bottom edge. | MAKER [M1]. The edge is SOURCED [R1] (a photo). The height is estimated in `docs/research/hardware-envelopes.md` section 1. |
| Does the output work with the HDMI input? | Yes, by one review: "The 3.5mm audio output gives you another option when using HDMI or USB-C audio from a connected device." | SOURCED [R1] |
| What is the output: headphone level or line level? | NOT CONFIRMED. The maker calls it "AUX". The manual is not published. | Bench test 1 |
| Does the monitor's volume setting change its level? | NOT CONFIRMED. The monitor has a volume setting in its menu. | SOURCED [R1] for the setting. Bench test 1. |
| Does a plug make the built-in speakers silent? | NOT CONFIRMED | Bench test 1 |
| Noise of the output | NOT CONFIRMED | Bench test 1 |
| The monitor's speakers | Two of 8 Ω and 1 W. "The speakers are clear but obviously lack bass." The owner calls them poor. | MAKER [M1]. SOURCED [R1]. OWNER. |

### 2.2 What is confirmed for chain (B)

| Question | Answer | Status |
| --- | --- | --- |
| Does a USB sound adapter work on Linux with no driver? | Yes, if it follows the USB audio class. One adapter: "Compliant with USB Audio Device Class Specification 1.0. Driverless for ... Linux". A second one: "We've tested it successfully with Raspbian". A third board: "Driver-free, plug-and-play. Compatible with Windows, Mac OS, Linux, and Android." | SOURCED (summary) [D2]. MAKER [D1][D3]. |
| Is it used on the BC-250? | Yes. The community guide gives it as the answer to three sound problems: "USB audio adapter ($10) as fallback", "Use a USB audio adapter as fallback", "Use USB DAC for audio". | SOURCED [B3][B2] |
| Can the sound go to USB while the picture goes over HDMI? | Yes. The sound device and the screen are separate in the system. The community text "audio shifts from DP to USB DAC" shows the two devices side by side. | SOURCED [B3]. ESTIMATED for the rule. Bench test 2 confirms it on the owner's system. |
| Where does the data lead go? | To a USB port of the board or of the hub. The owner's power unit has USB sockets, but it carries no data. | OWNER |
| The 5 V of the port | The adapter takes little current (not stated in the sources). The ports of the board are weak, so a noisy 5 V is possible. | NOT CONFIRMED. Bench test 2 (listen for hiss). |
| Sleep | The board has no sleep state that works. The documents say: do not let it sleep. | `docs/research/bc250-power-button.md` section 4 |
| Clicks when a sound starts | The sound server stops an output device that is idle. Some USB adapters click when it starts again. The cure is one setting: `session.suspend-timeout-seconds = 0` in WirePlumber. | SOURCED (summary) [W1] (user reports for other adapters). NOT CONFIRMED on this system. |
| Pops at the start and at a shutdown | NOT CONFIRMED. The adapter and the amplifier lose their power in the same second. The data sheet of one amplifier chip says that a larger bypass capacitor "reduces clicking and popping noise from power on/off". | MAKER [E1]. Bench test 3. |

### 2.3 What powers the amplifier

The owner's power unit for the monitor (SlimQ M0002, `docs/research/monitor-power-and-video.md`
section 4) has two USB-A sockets with 5 V and 3 A each, and a second USB-C socket.

| Source | For which amplifier | For | Against |
| --- | --- | --- | --- |
| The 12 V rail of the supply, on a second branch of the Molex lead, with a fuse | A 12 V amplifier (MAX9744, TPA3110D2) | The full power of the amplifier. No converter between. It goes off with the supply. | The 12 V rail also carries the BC-250 (up to 20 A in steps). Noise from it can come through. |
| A USB-A socket of the power unit, 5 V 3 A | A 5 V amplifier (PAM8403, MAX98306). The MAX9744 also runs on 5 V, with less power. | A ready-made lead from USB-A to a barrel plug or to bare wires. The amplifier and the monitor then have one power part. | The 5 V comes from a switching converter, which is a second source of noise. A fault in the unit stops the screen and the sound together. |
| The 5 V rail of the supply, from a SATA lead | A 5 V amplifier | 24 A are available. The hub has the same rail. | The hub and its devices are on the same rail. |
| The second USB-C socket of the power unit | A 12 V amplifier, through a small trigger board that asks for 12 V | - | One more part. Not recommended. |

Recommendation: the 12 V rail for the MAX9744 board. If bench test 4 finds noise from the rail, move
the amplifier to a USB-A socket of the power unit, at 5 V.

How much power is necessary (ESTIMATED): the player sits about 0.5 m from the speakers (the fit
report gives 415 mm to 525 mm from the eye to the screen). Two speakers at 0.5 m give about 9 dB more
than one speaker at 1 m. With 1.4 W, a driver of 86 dB then gives about 96 dB, and a driver of 80 dB
gives about 90 dB. This is louder than a game needs. Thus a 5 V amplifier is sufficient for a
sensitive driver. A 12 V amplifier gives a margin for the low end.

### 2.4 Hum and whine from a shared ground

| Item | Detail | Status |
| --- | --- | --- |
| The cause | "Ground loops occur when the grounds of the two units are also tied together in another place". The noise comes when "this current flows through a unit's audio signal ground". | SOURCED [G1] |
| In chain (A) | The ground of the monitor goes to the board through the HDMI lead, and to the power unit through the USB-C lead. The ground of the amplifier goes to its supply. The 3.5 mm lead closes the loop. | ESTIMATED from the wiring |
| In chain (B) | The ground of the adapter goes to the board through USB. The ground of the amplifier goes to the supply. The 3.5 mm lead closes the loop. A whine that changes with the load of the board is the usual sign. | ESTIMATED from the wiring |
| The cure for a lead of this kind | "transformer isolate all unbalanced connections". A ground loop isolator for a 3.5 mm lead has two small transformers. It goes between the source and the amplifier. | SOURCED [G1]. No isolator was read from a data sheet. |
| An amplifier with differential inputs | It measures the signal between two wires, not against its ground. The MAX98306 board has "Differential" inputs. The inputs of the PAM8403 are single-ended. | MAKER [E3][E1]. That it removes the loop noise here is ESTIMATED. |
| Noise from the supply rail | The PAM8403 rejects ripple on its supply by 59 dB at 100 Hz. Its data sheet asks for capacitors at the chip and gives a capacitor of 1000 µF at the supply terminal against interference. The Adafruit MAX9744 board has a 470 µF capacitor. | MAKER [E1][E2] |
| Radio noise from the speaker wires | A class D output is a square wave. The MAX98306 "Passes EMI limit unfiltered with up to 12 inches (30 cm) of speaker cable." The wires to the hood are about 0.6 m to 1.0 m. Twist each pair. Fit ferrite beads at the amplifier, as the PAM8403 data sheet shows. | MAKER [E3][E1]. The wire length is ESTIMATED from the fit report. |

### 2.5 The volume knob in each chain

| Knob | Chain (A) | Chain (B) | With no keyboard, in each game | Keeps its setting |
| --- | --- | --- | --- | --- |
| A potentiometer on the amplifier | Works | Works | Yes. It needs no software. | Yes: the position of the knob |
| A knob that the system reads (a USB device) | Works only if the system changes the HDMI level | Works | Only while the system runs, and only if the game session reads volume keys. NOT CONFIRMED. | The system keeps the value |
| The wheel of the monitor | Changes the monitor's own speakers. It can change the 3.5 mm output (NOT CONFIRMED). | No effect | No: the wheel is on the right edge of the monitor, inside the cabinet | - |

Thus the knob is a potentiometer on the amplifier in the two chains. Set the source to a fixed level:
the volume of the system in chain (B), and also the volume of the monitor in chain (A).

### 2.6 Boards that are a sound card and an amplifier in one

| Board | Data | Result |
| --- | --- | --- |
| Waveshare "USB TO AUDIO" | Chip SSS1629A5. "Driver-free, plug-and-play. Compatible with Windows, Mac OS, Linux, and Android." Speaker output "2.6W per channel (4Ω BTL)" on a PH2.0 connector. The page is not clear on one or two speaker channels. It takes its power from the USB port. The volume is set in the system, and by a small screw on the board. | Not recommended. It has no input for a volume knob. Two channels of 2.6 W take about 1.2 A at 5 V, which is more than a port of the board gives. ESTIMATED: 5.2 W at an efficiency of 85 %. MAKER [D3]. |

## 3. Amplifier boards

| Board | Supply | Output | Volume | Inputs | Size | Price | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Adafruit 1752, "Stereo 20W Class D Audio Amplifier - MAX9744" | 4.5 V to 14 V (the chip). "Power it with 5-12VDC using the onboard DC power jack." | "20W Stereo Output (4Ω, VDD = 12V, THD+N = 10%)". For 8 Ω and for 5 V the page gives no value. Estimates: about 10 W into 8 Ω at 12 V, about 3.5 W into 4 Ω at 5 V. | One potentiometer of 1 kΩ for the two channels, or 64 steps on an I2C bus. The potentiometer can be on wires away from the board. | A 3.5 mm socket and terminal blocks, line level up to 3 V peak to peak | 54 mm x 41 mm, 11 g | USD 19.95. "Out of stock" at the maker's shop on 2026-11-14. | MAKER [E2][E4]. The two estimates are from the square of the voltage and from half the power at double the load. |
| Adafruit 987, "Stereo 3.7W Class D Audio Amplifier - MAX98306" | 2.7 V to 5.5 V | At 5 V: 3.7 W into 3 Ω and 1.7 W into 8 Ω (10 % distortion) | None. Five fixed gains, 6 dB to 18 dB. | Differential, on a terminal block | 28.1 mm x 24.0 mm x 10.4 mm | USD 8.95, in stock | MAKER [E3] |
| A board with the PAM8403 (many sellers, no maker's page for a board) | 2.5 V to 5.5 V | At 5 V: 3.2 W into 4 Ω and 1.8 W into 8 Ω (10 % distortion). 2.5 W and 1.4 W at 1 % distortion. | Some boards have a potentiometer in the signal path | Single-ended | Not read | Not read | MAKER [E1] (the data sheet of the chip). The maker of the reference cabinet uses this chip. |
| A board with the TPA3110D2 (many sellers) | 8 V to 26 V | 10 W into 8 Ω at 13 V. About 8.5 W at 12 V. | Some boards have a potentiometer in the signal path | Not read | Not read | Not read | `docs/design/hardware-list.md` 2.5. The 12 V value is ESTIMATED from the square of the voltage. |

Why the MAX9744 board: a single potentiometer sets the two channels, so it does not carry the sound.
It gives a control voltage to the chip. ESTIMATED from "The potentiometer sets the volume for both
channels" [E4]. Wires with a control voltage can be long and need no shield. A potentiometer in the
signal path needs a shielded lead for each channel.

## 4. USB sound adapters for chain (B)

| Adapter | Data | Price | Status |
| --- | --- | --- | --- |
| Adafruit 1475, "USB Audio Adapter - Works with Raspberry Pi" | USB-A plug on a lead of 140 mm. Body 43.8 mm x 23.2 mm x 12.0 mm. Output and line-level input. "We've tested it successfully with Raspbian". | USD 4.95, in stock | MAKER [D1] |
| Sabrent AU-MMSA | "Compliant with USB Audio Device Class Specification 1.0. Driverless for ... Linux". "USB bus-powered, no external power required." 3.5 mm headphone and microphone sockets. | Not read | SOURCED (summary) [D2] |
| The adapter of the community guide | "USB audio adapter ($10)". No type is named. | - | SOURCED [B3] |

The noise of a low-cost adapter is not in its data. Buy one, do bench test 2, and change the type if
it hisses.

## 5. Recommendation for part 1

The owner decides. This is the recommendation and its reasons.

**Chain (B).** The reasons, in order:

1. The monitor is a part that can change (settled by the owner). Chain (B) does not use it.
2. The level is fixed in the system. The knob on the amplifier is then the only volume control. In
   chain (A) the monitor can have a second one that nobody can reach.
3. The 3.5 mm output of the monitor has no data: its level, its noise, and what it does to the
   built-in speakers are not known.
4. The cost is one small part and one USB port.

The parts of the recommended chain:

| Part | Type | Connects to |
| --- | --- | --- |
| USB sound adapter | Sabrent AU-MMSA or Adafruit 1475 | A USB 2.0 port of the board. If the adapter is in the hot air at the I/O end, put it on a USB extension of 0.3 m to 0.6 m. |
| Signal lead | 3.5 mm stereo plug to 3.5 mm stereo plug, 0.15 m to 0.3 m | The 3.5 mm socket of the amplifier |
| Amplifier | Adafruit 1752 (MAX9744) | 12 V from a second branch of the Molex lead, with a fuse of about 3 A. ESTIMATED: 20 W of sound at an efficiency of 90 % is less than 2 A. |
| Volume potentiometer | 1 kΩ, linear, with a threaded bushing (section 7) | Three wires to the volume pads of the amplifier |
| Speaker wires | Two twisted pairs, 0.25 mm2 to 0.5 mm2 | The multi-pin plug at the foot of the hood (four pins) |
| Speakers | Two drivers, each in a sealed pod (part 3) | - |
| Only if there is hum | A ground loop isolator in the signal lead | - |

Chain (A) is the same list with no adapter, and with a 3.5 mm lead of about 0.8 m from the monitor.

## 6. Bench tests, in this order

Do the tests with the amplifier, one speaker pair and the real supply, before the hood is printed.

1. **Chain (A).** Connect the 3.5 mm output of the monitor to the amplifier. Play a game sound.
   - Change the volume setting of the monitor. Write down if the level at the amplifier changes.
   - Write down if the built-in speakers are silent with the plug in.
   - Stop the sound. Set the knob to the usual position. Listen at 0.5 m for hiss, hum and whine.
     Start a game with a high load and listen again.
2. **Chain (B).** Connect the USB sound adapter to a USB 2.0 port of the board. Select it as the
   output device. Do the three listening checks of test 1 again. Write down if the sound goes to
   the adapter while the picture is on the monitor.
3. **Start and shutdown.** With each chain: start the system and shut it down five times, with the
   knob at the usual position. Write down each pop.
4. **The supply of the amplifier.** Compare the 12 V rail with a USB-A socket of the power unit
   (5 V). Listen for whine in the two cases.
5. **Hum.** If test 1, 2 or 4 has hum or whine, put a ground loop isolator into the signal lead and
   listen again.
6. **Idle clicks, chain (B).** Stop all sound for one minute, then play a short sound. If it clicks,
   set `session.suspend-timeout-seconds = 0` and do the test again.

Chain (A) passes if the level does not change with the monitor's setting, or the setting stays after
a power loss; if the built-in speakers are silent; and if the noise is not more than in chain (B).

---

## Part 2. The volume control

## 7. The ways and the parts

| Way | What it is | Works with no software | Keeps its setting | Hole in the shell | Notes |
| --- | --- | --- | --- | --- | --- |
| (1) The volume potentiometer of the amplifier, on a lead | 1 kΩ on the volume input of the MAX9744 board | Yes | Yes | One hole for a bushing (see the table that follows) | Three wires with a control voltage. The lead can be 1 m and more. Recommended. |
| (2) A potentiometer in the signal path | Two gangs of 10 kΩ with an audio taper before the amplifier, or the potentiometer of a PAM8403 or TPA3110D2 board moved to a lead | Yes | Yes | The same | Six wires that carry the sound. They need a shield and must be short. |
| (3) A rotary encoder with a small controller | The controller sets the 64 steps of the MAX9744 on its I2C bus | Yes, with its own firmware | Only if the firmware stores the value | The same | More parts and firmware for no gain over way (1). |
| (4) A USB volume knob that the system reads | Example: Adafruit 4964 "Rotary Trinkey" (USD 6.95, 32.4 mm x 16.5 mm x 4.0 mm) with an encoder of the PEC11 type. The encoder is not included. It can be a "Keyboard/Mouse HID device". | No | The system keeps the value | The same, and a USB lead to the board or the hub | It works only while the system runs. That the game session obeys volume keys is NOT CONFIRMED. MAKER [V2]. |
| (5) The wheel of the monitor | On the right edge of the monitor | - | - | It needs an opening in the cheek | Not usable: it is inside the cabinet. |

A potentiometer for way (1). MAKER [V1] (Bourns PTV09 series, one example):

| Item | Value | Status |
| --- | --- | --- |
| Body | 9 mm class | MAKER [V1] |
| Shaft | 6.0 mm diameter, flat type, 15 mm, 20 mm, 25 mm or 30 mm long | MAKER [V1] |
| Bushing | Version 6 has a metal threaded bushing, M9 x 0.75, with one nut and one washer | MAKER [V1] |
| Values and tapers | 1 kΩ to 1 MΩ, linear and audio | MAKER [V1] |
| Life | 10,000 cycles | MAKER [V1] |
| Terminals | Pins for a circuit board. Solder the three wires to the pins and cover them. | MAKER [V1]. A panel potentiometer of 16 mm with solder lugs is the more usual part. No data sheet of that type was read. |
| Hole as printed | 9.4 mm. Print a coupon with 9.3 mm, 9.4 mm and 9.5 mm. | PROVISIONAL: a printed hole comes out small (`docs/design/hardware-list.md` 2.1) |
| Wall at the hole | 2.0 mm to 3.0 mm, so that the nut has thread. The socket plate has a web of 2.0 mm at its sockets. | ESTIMATED: the length of the bushing was not read clearly from the drawing. Measure the part. |
| Depth behind the wall | 20 mm for the body, its pins and the wire bend | ESTIMATED |
| Knob | For a 6 mm shaft with a flat. A diameter of 15 mm to 20 mm suits a wall of 31 mm. | ESTIMATED. No knob was read from a data sheet. |
| Turn stop | The body needs a small pocket or a pin in the printed part, so that it does not turn with the knob | ESTIMATED |

## 8. The place of the knob

Values of the shell are BUILD (the fit report, `dims.py`, `docs/blueprint/index.md`). Each lead
length has 0.2 m of slack and is ESTIMATED.

| Place | Reach while playing | Look | Lead | Notes |
| --- | --- | --- | --- | --- |
| The USB socket plate, on the right side face of the deck, beside the power button | Good. The right hand goes from the buttons to the side of the deck, about 150 mm. The player finds a knob by feel. | Out of view, as the USB sockets are | 0.3 m to an amplifier in the deck. About 1.2 m to an amplifier in the hood. | The plate is a service part: it can be printed again. The wall is 31 mm high. The row of four sockets is 150 mm long. A button and a knob add about 26 mm each (PROVISIONAL). The CAD agent must find if the flat part of the side face is long enough. |
| The hood band | Poor. The band is about 400 mm above the deck top (z 475 mm against z 70 mm). The player lets go of the controls and reaches up. | The knob is in full view, on the face that carries the speakers and the logo | 0.2 m to an amplifier in the hood | The band has no underside that can take a knob. The ledge under it is 13.9 mm deep, and the speaker forms stand 4 mm above the ledge. The only free face is the strip of 18 mm between a speaker form and the logo form (`logo_gap`). A knob of 14 mm fits there. |
| The side of the cabinet, above the deck, near the front | Good: about 200 mm from the buttons | In view from the side. It is a hole in a bonded and painted piece. | 0.4 m to an amplifier in the deck | The owner set that the side panels have no vents. A knob there also changes a plain side. |
| The rear | None while playing | Out of view | 0.3 m to an amplifier at the rear | Only for a level that a person sets one time. |

Recommendation: the USB socket plate, beside the power button. The reasons are reach, look and
service, in this order. With way (1) the length of the lead has no effect on the sound, so the
amplifier can be in the deck or in the body.

If the side face is not long enough for four sockets, the button and the knob in one row: make the
socket pitch smaller, or put the knob in a second small plate on the left side face of the deck. The
owner decides.

---

## Part 3. The speakers

## 9. The room in the hood as it is

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
| Largest round frame | 53.9 mm: the height of the form less a margin of 2 mm at each side | BUILD (fit report). Confirmed: 57.9 less 4.0. |
| What limits the frame | The height of the form. The form is 95.9 mm wide, so an oval driver can use the width. | ESTIMATED from the two values above |
| Depth behind the band | 109.1 mm, to the skin or to the room of the marquee modules | BUILD (fit report) |
| Centre of each form | 136.4 mm from the centre line, 475.3 mm above the desk | BUILD (fit report data) |
| Wall of the band | 4.0 mm | BUILD (fit report, "Wall") |

The rule for the band, from these values: the band is as high as the frame of the driver and 14 mm
more (2 mm of margin at each side, 4 mm at the foot, 6 mm at the head). ESTIMATED.

## 10. Drivers for the hood as it is

Each driver can be bought as one unit. The sensitivity of the Dayton and the Tectonic drivers is at
2.83 V and 1 m. This is 1 W into 8 Ω and 2 W into 4 Ω. The Visaton values are the maker's mean level
at 1 W and 1 m, which is a different method.

| Driver | Frame | Cut-out | Depth | Impedance, power | Range (maker) | Sensitivity | Fs, Qts, Vas | Maker's sealed volume and low limit | Price | Fit | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tectonic TEBM35C10-4 (a balanced mode radiator) | 51.8 mm round | 42.9 mm | 24.9 mm | 4 Ω, 10 W | 100 Hz to 20 kHz | 83 dB (about 80 dB at 1 W) | 145 Hz, 0.83, 0.178 l | 0.45 l, 154 Hz | EUR 21.45. Out of stock at this seller on the date. | Yes: 1.0 mm inside the limit at each side | SOURCED [A2] (a seller's copy of the maker's data) |
| Visaton FRS 5 X, 8 Ω | 52.5 mm round, 68 mm over its two lugs, holes of 4.2 mm, 60 mm apart | 46 mm | 35.0 mm | 8 Ω, 5 W | 120 Hz to 20 kHz (at -10 dB) | 86 dB | 190 Hz, 0.70, 0.23 l | Not stated | Not read | Yes, with the lugs along the width: 0.7 mm inside the limit at each side | MAKER [A5] (the page and the drawing) |
| Dayton Audio DMA45-8 | 46.0 mm square | 39.9 mm | 25.9 mm | 8 Ω, 10 W | 150 Hz to 20 kHz | 76.9 dB | 150.7 Hz, 0.59, 0.055 l | 0.05 l, 216 Hz | USD 11.99 (list), EUR 14.65 | Yes | MAKER [A1]. SOURCED [A2] for the frame and the enclosure. |
| Visaton SC 5.9 FLX, 8 Ω (oval, 5 cm x 9 cm) | Not read. The cut-out of the sister type SC 5.9 ND is 43 mm x 82 mm. | - | Not read | 8 Ω, 4 W | 85 Hz to 20 kHz (at -10 dB) | 82 dB | 141 Hz, 1.41, 0.42 l | Not stated | Not read | Probably, with the long side along the width. NOT CONFIRMED. | MAKER [A6] |
| Dayton Audio CE32A-8 (the driver of the reference cabinet's maker) | 32 mm square | - | 15.5 mm | 8 Ω, 2 W | 240 Hz to 20 kHz | 77.9 dB | Not read | Not read | Not read | Yes | `docs/design/hardware-list.md` 2.5 |

Notes:

- The Tectonic driver has the lowest limit of the three round drivers (154 Hz against about 200 Hz),
  and the most cone travel (2.5 mm).
- The Visaton FRS 5 X is the most sensitive. It is the choice for a 5 V amplifier.
- The DMA45-8 is 6 dB to 9 dB quieter for the same power. It needs the 12 V amplifier.
- The oval Visaton has a cone area of 26.8 cm2, which is more than a round 2.5 inch driver has
  (22.9 cm2). Its Qts of 1.41 is that of a driver for a television set with an open back. Its frame
  and its cone travel were not read.

## 11. Drivers for an expanded hood band

| Driver | Frame | Cut-out | Depth | Impedance, power | Range (maker) | Sensitivity | Fs, Qts, Vas | Maker's sealed volume and low limit | Maker's vented volume and low limit | Price | Band must be | More than now | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Dayton Audio DMA58-8 (2 inch) | 55.9 mm square | 49.8 mm | 31.8 mm | 8 Ω, 15 W | 160 Hz to 20 kHz | 82.5 dB | 166 Hz, 0.54, 0.136 l | 0.08 l, 263 Hz | 0.51 l, 105 Hz | EUR 19.95 | 69.9 mm | 2.0 mm | SOURCED [A2][A4] |
| Tang Band T2-2136S (a module: a 57 mm driver, a box and a passive radiator in one) | 70 mm x 70 mm, holes on 59 mm x 59 mm | The whole module | 58 mm | 4 Ω, 10 W | 80 Hz to 20 kHz | 80 dB (1 W, 1 m) | The system: 80 Hz | Its own box | - | Not read | 84.0 mm | 16.1 mm | MAKER [A7] (the specification sheet) |
| Dayton Audio DMA70-8 (2.5 inch) | 69.9 mm square | 63.8 mm | 38.4 mm | 8 Ω, 20 W | 110 Hz to 20 kHz | 82.9 dB | 113.7 Hz, 0.50, 0.566 l | 0.37 l, 179 Hz | 1.02 l, 88 Hz | USD 22.99 (list), EUR 27.95 | 83.9 mm | 16.0 mm | MAKER [A3]. SOURCED [A2]. |
| Dayton Audio DMA80-8 (3 inch) | 80.3 mm square | 74.4 mm | 38.9 mm | 8 Ω, 25 W | 90 Hz to 20 kHz | 85.3 dB | 97.6 Hz, 0.47, 1.13 l | 0.99 l, 174 Hz | 1.5 l, 91 Hz | USD 23.99 (list), EUR 29.95 | 94.3 mm | 26.4 mm | MAKER [A3]. SOURCED [A2]. |

The depth is no problem: each driver is less than 109 mm deep. The width is no problem: the form is
95.9 mm wide. Only the height of the band changes.

What a larger driver gives, in plain numbers. The sealed low limit of column 3 is ESTIMATED with the
closed-box rule from Fs, Qts and Vas. The air volume is the cone area times the cone travel. Each
6 dB is double the sound pressure.

| Driver | Low limit, maker's sealed box | Low limit in a pod of 0.45 l | Air volume that the cone moves | Low-end level against the DMA45-8 | Loudest level at 1 m, at rated power | More band height |
| --- | --- | --- | --- | --- | --- | --- |
| DMA45-8 | 216 Hz | 183 Hz | 1.7 cm3 | 0 dB | 87 dB | 0 |
| Visaton FRS 5 X | - | 199 Hz | 2.5 cm3 | +3 dB | 93 dB | 0 |
| Tectonic TEBM35C10-4 | 154 Hz | 136 Hz | Not read | - | 90 dB | 0 |
| DMA58-8 | 263 Hz | 221 Hz | 2.9 cm3 | +5 dB | 94 dB | 2.0 mm |
| Tang Band T2-2136S | 80 Hz (with its passive radiator) | - | Not read | - | 90 dB | 16.1 mm |
| DMA70-8 | 179 Hz | 161 Hz | 4.6 cm3 | +9 dB | 96 dB | 16.0 mm |
| DMA80-8 | 174 Hz | 154 Hz (147 Hz in 1.0 l) | 7.8 cm3 | +13 dB | 99 dB | 26.4 mm |

What the table shows:

1. **2 mm more (a 2 inch driver) gives nothing.** The Tectonic driver fits now and goes lower.
2. **16 mm more is the first step with a gain.** The DMA70-8 has 9 dB more low-end level than the
   smallest driver, and a limit of about 160 Hz to 180 Hz. The Tang Band module goes to 80 Hz, which
   is one octave lower than each sealed driver of this note.
3. **26 mm more (a 3 inch driver)** gives 13 dB more low-end level and the highest sensitivity. Its
   sealed limit is still about 150 Hz to 175 Hz. It needs a pod of 1 l.
4. **A sealed box of this size does not go below about 140 Hz.** Only a passive radiator or a vent
   gives the 80 Hz to 105 Hz of the "vented" column.

What the hood band must give (for the agent that judges the form):

| For | Band height | Speaker form height | Change |
| --- | --- | --- | --- |
| Now | 67.9 mm | 57.9 mm | - |
| A 2 inch driver with a square frame of 55.9 mm | 69.9 mm | 59.9 mm | +2.0 mm. Or no change, with a margin of 1 mm in place of 2 mm. |
| A 2.5 inch driver or the Tang Band module (70 mm) | 84.0 mm | 74.0 mm | +16.1 mm |
| A 3 inch driver (80.3 mm) | 94.3 mm | 84.3 mm | +26.4 mm |

The opening of the hood is 148 mm, and all of it is in use. More band height comes from a higher
hood, from a lower marquee, or from a thinner top bar. The marquee note
(`docs/research/marquee-display.md` section 7) has the same sum for a taller display. The two wishes
compete for the same height.

## 12. More low end with no change of the hood

| Way | What it is | What it gives | What it needs | Result |
| --- | --- | --- | --- | --- |
| A passive radiator in the same pod, beside the driver | Dayton sells passive radiators for the DMA series (DMA45-PR, DMA58-PR, DMA70-PR, DMA80-PR). A DMA45-8 and a DMA45-PR side by side are 92 mm wide. The form is 95.9 mm wide. | The maker's vented value for the DMA45-8: 0.34 l, 88 Hz. That a passive radiator gives the same is NOT CONFIRMED. | A sealed pod of 0.34 l to 0.45 l. The gaps between the two frames and the form are 1.3 mm. The radiator needs mass for its tune. | Possible, but the DMA45-8 is the quietest driver. A simulation or a test pod must come first. MAKER [A3] for the series. The size of the DMA45-PR was not read. |
| A passive radiator at the rear of the pod | The radiator moves air into the hood | - | The hood is open to the body, and the body is open at the rear door | Not recommended: the sound of the radiator stays in the cabinet. ESTIMATED. The Tang Band module has its radiator at the rear, so the same question applies to it. |
| A small woofer in the body (a 2.1 system) | A 3 inch driver in its own box of 1.5 l, with a third amplifier channel | About 90 Hz (the maker's vented value for the DMA80-8), one octave below the hood drivers | A box of 1.5 l and more in the lower body. An opening with a grille in a fixed wall: the owner excludes the front of the deck and the sides, and the rear door carries no part. That leaves the lower rear wall. A 2.1 amplifier. | Not for the first build. The room and the sound path are not examined in CAD. Low tones spread in each direction, so an opening at the rear works near a wall. ESTIMATED: no source was read. |

## 13. The enclosure

The printed hood is not sealed: it is open to the body, and the body has vents. A small driver in
an open space loses its low end, because the sound from its rear cancels the sound from its front.
Thus each driver gets its own sealed pod.

| Item | Value | Status |
| --- | --- | --- |
| Volume for the three round drivers of section 10 | 0.45 l. It is the maker's volume for the Tectonic driver. For the two others, a larger pod changes the low limit by less than 5 Hz. | SOURCED [A2]. ESTIMATED (closed-box rule). |
| Volume that the room gives | 0.48 l for a pod with the outline of the speaker form: 91 mm x 53 mm inside, 100 mm deep. 0.63 l for a pod as high as the band: 100 mm x 63 mm x 100 mm. | ESTIMATED from the fit report values, with walls of 2.4 mm |
| Volume for a larger driver | 0.37 l for the DMA70-8, 0.99 l for the DMA80-8 (the maker's sealed values) | SOURCED [A2] |
| The part | A printed box with an open front. Its front flange is the baffle: the driver sits on it with four M3 screws in heat-set inserts. The box goes in from behind the band. Four screws hold it to bosses on the band. | PROVISIONAL. The inserts are those of `docs/design/hardware-list.md` 1.9. |
| Seals | A ring of closed-cell foam (2 mm to 3 mm) between the driver and the baffle, and between the pod and the band. Seal the wire hole with a grommet or with glue. | ESTIMATED: usual practice. No source was read. |
| Walls | 2.4 mm to 3 mm, with four wall lines or more, so that the print is airtight. Paint the inside if a leak test fails. | ESTIMATED. Do a leak test: push the cone in gently. It must come back slowly. |
| Damping | A loose fill of polyester fibre | ESTIMATED: usual practice. No source was read. |
| The grille | The speaker front follows the contour of the hood (settled by the owner). The open area of the grille is not examined. | Roadmap, "Settled by the owner" |
| Service | The driver comes out with its pod, from inside the hood, after the hood is off the body | BUILD: the hood lifts off (`docs/blueprint/index.md`) |

## 14. Recommendation for the speakers

1. **Keep the hood band as it is for the first build.** Use the Tectonic TEBM35C10-4 in a sealed pod
   of 0.45 l. If it cannot be bought, use the Visaton FRS 5 X.
2. **Design the pod, not the hood, for the driver.** The pod is a small part. A different driver
   needs a new pod and a new baffle hole only.
3. **A larger band is worth it only from 16 mm.** If the owner wants more low end, the Tang Band
   module (80 Hz) and the DMA70-8 are the two candidates at 16 mm. The module must have free air
   behind its radiator, which the hood does not give with certainty. Test one module before the
   form changes.
4. **Do a listening test before a change of the form.** One pair of the Tectonic drivers in two test
   pods on the bench shows if the low end is sufficient for the owner.

## 15. What the shell must provide

| Item | Value | Status |
| --- | --- | --- |
| A hole for the volume potentiometer | In the USB socket plate: 9.4 mm as printed, a wall of 2 mm to 3 mm at the hole, 20 mm clear behind it, a flat circle of 22 mm outside for the knob | PROVISIONAL (section 7) |
| Length on the socket plate | About 26 mm more for the knob, beside the power button | PROVISIONAL. The CAD agent must find the free length. |
| A place for the amplifier | 54 mm x 41 mm, and about 20 mm high with its capacitor and terminals. On four posts or in a printed clip, in the deck near the socket plate or on the floor of the body. | MAKER [E2] for the board. The height and the hole pattern were not read. |
| A place for the USB sound adapter (chain B) | 44 mm x 23 mm x 12 mm on a lead, held by a clip or a tie, out of the exhaust air | MAKER [D1] |
| Two pods in the hood | Each 0.45 l, behind a speaker form, with four bosses on the band | Section 13 |
| Four pins in the plug at the foot of the hood | For two speaker pairs | BUILD (`docs/design/hardware-list.md` 1.6) |
| A route for a 3.5 mm lead from the right edge of the monitor (chain A only) | A right-angle 3.5 mm plug in the plug space of 22 mm, and the cable channel of the right side | BUILD (fit report). No change. |
| No change of the hood band | For the recommended driver | Section 14 |

## 16. Sources

Speakers:

| No. | Source | What it is |
| --- | --- | --- |
| A1 | https://www.daytonaudio.com/product/1613/dma45-8-1-1-2-dual-magnet-aluminum-cone-full-range-driver-8-ohm and https://www.daytonaudio.com/images/resources/295-581--dayton-audio-dma45-8-specification-sheet.pdf | Maker's product page and specification sheet |
| A2 | https://www.soundimports.eu/en/dayton-audio-dma45-8.html (and `dma58-8`, `dma70-8`, `dma80-8`, `tectonic-elements-tebm35c10-4` at the same address) | A seller's copy of the makers' data: frame, cut-out, depth, sealed and vented volume, low limit, price |
| A3 | https://www.daytonaudio.com/product/1617/dma70-8-2-1-2-dual-magnet-aluminum-cone-full-range-driver-8-ohm , https://www.daytonaudio.com/product/1619/dma80-8-3-dual-magnet-aluminum-cone-full-range-driver-8-ohm , https://www.daytonaudio.com/category/220/dma-series | Maker's product pages and the list of the series with its passive radiators |
| A4 | https://loudspeakerdatabase.com/Dayton/DMA58-8 | A database copy of the maker's parameters |
| A5 | https://www.visaton.de/en/products/drivers/fullrange-systems/frs-5-x-8-ohm and its drawing `frs5x_tz.gif` | Maker's product page and dimension drawing |
| A6 | https://www.visaton.de/en/products/drivers/fullrange-systems/sc-59-flx-8-ohm and https://www.visaton.de/en/products/drivers/fullrange-systems/sc-59-nd-8-ohm | Maker's product pages of two oval drivers |
| A7 | https://www.parts-express.com/pedocs/manuals/264-938--tang-band-t2-2136sa-spec-sheet.pdf | Maker's specification sheet of the module, on a seller's site |

Amplifiers and the volume control:

| No. | Source | What it is |
| --- | --- | --- |
| E1 | https://www.diodes.com/assets/Datasheets/PAM8403.pdf | Data sheet of the amplifier chip |
| E2 | https://www.adafruit.com/product/1752 | Product page of the MAX9744 board |
| E3 | https://www.adafruit.com/product/987 | Product page of the MAX98306 board |
| E4 | https://learn.adafruit.com/adafruit-20w-stereo-audio-amplifier-class-d-max9744/analog-control | The maker's guide: the volume potentiometer |
| V1 | https://www.bourns.com/docs/Product-Datasheets/PTV09.pdf | Data sheet of a potentiometer series |
| V2 | https://www.adafruit.com/product/4964 | Product page of a USB board for a rotary encoder |
| G1 | https://www.ranecommercial.com/legacy/note110.html | An audio maker's note on ground loops and their cure |

Sources of the sound:

| No. | Source | What it is |
| --- | --- | --- |
| D1 | https://www.adafruit.com/product/1475 | Product page of a USB sound adapter |
| D2 | https://sabrent.com/products/au-mmsa | Summary only: a USB sound adapter of the USB audio class |
| D3 | https://www.waveshare.com/wiki/USB_TO_AUDIO | Maker's page of a USB sound card with a speaker amplifier |
| W1 | https://unix.stackexchange.com/questions/733143/fiio-k3-popping-on-start-some-time-after-last-sound and https://unix.stackexchange.com/questions/676846/ | Summaries only: clicks of a USB sound device after an idle time, and the setting that stops them |
| M1 | https://uperfect.com/products/16-inch-4k-sunlight-readable-monitor | The maker's page of the monitor |
| R1 | https://www.linuxlinks.com/uperfect-ucolor-t6-review/ | A review of the monitor |
| B1 | https://elektricm.github.io/amd-bc250-docs/hardware/specifications/ | Community documentation of the board: "Audio over DisplayPort (compatibility varies)" |
| B2 | https://elektricm.github.io/amd-bc250-docs/troubleshooting/display/ | Community documentation: sound through DisplayPort, "Use USB DAC for audio" |
| B3 | https://github.com/katzzero/bc250-unofficial-community-guide/blob/main/10-troubleshooting.md | Community guide: the USB audio adapter as the fallback |

## 17. Not confirmed, and sources that were not accessible

| Item | Result |
| --- | --- |
| The 3.5 mm output of the monitor: its level, the effect of the monitor's volume setting, the built-in speakers with a plug in, its noise | No source. The manual is not published. Bench test 1. |
| The noise of a low-cost USB sound adapter on the board's 5 V | No source. Bench test 2. |
| Pops at the start and at a shutdown | No source. Bench test 3. |
| The output of the MAX9744 board into 8 Ω, and at 5 V | Not on the product page. The data sheet of the chip did not load (two time-outs). The values in section 3 are estimates. |
| The hole pattern and the height of the amplifier boards | Not on the pages that were read. |
| The Dayton specification sheets with the dimension drawings | The maker's server refused the files (a block page). A seller's copy of the same data was used. The page for the DMA45-8 was read. |
| The frame and the cone travel of the oval Visaton drivers | Not on the pages that were read. |
| The price of the Visaton drivers and of the Tang Band module | Not read. |
| The size and the mass of the Dayton passive radiators | Not read. One seller's summary gives the DMA58-PR: 2.2 inch square, cut-out 1.97 inch, 1.5 inch deep. |
| A passive radiator in the pod | Not calculated. It needs a simulation with the parameters of the radiator. |
| A woofer in the body | Not examined in CAD. |
| A ground loop isolator, a knob and a panel potentiometer of 16 mm | No data sheet was read. |
| That the game session of the system obeys volume keys | No source. It matters only for a knob that the system reads. |
| The loudness estimates | Calculated from the makers' sensitivity and power. No listening test. |
