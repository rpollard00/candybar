# Cabinet reference builds: construction notes

Research date: 2026-11-09. Scope: construction techniques, proportions and reusable component CAD from the cabinet references in `docs/Arcade_Project_Current_Design_2026-11-09.md`. These are construction references. None of them is a cabinet to copy or to scale.

## How to read the numbers

Every number carries one of these tags.

| Tag | Meaning |
| --- | --- |
| `[S:key]` | SOURCED. Stated by the source. The key points to the URL table below. |
| `[M]` or `[M:path]` | SOURCED by measurement. Measured with a script from the upstream file in the vendored clone. The path is relative to the clone; a bare `[M]` refers to the file named earlier in the same paragraph or table. The upstream URL and commit are in the clone table. |
| `[E]` | ESTIMATED. Derived from images, drawings or arithmetic on other numbers. The basis is stated next to the value. |

Source keys:

| Key | URL |
| --- | --- |
| BARTOP | https://github.com/multigamesystem/MGS004NSM-MVS-U4-Bartop-Arcade (commit `111b091`) |
| PARTS | https://docs.google.com/spreadsheets/d/1pxXt8bnTfDVqlSbCJ7jat37W06VcVyOz38HlE5kr99o ("MGS004 NSM Parts + Materials", linked from the BARTOP README through https://drive.google.com/drive/folders/1Mat5i3Aj4ehOi_3efJd82ZhYPgAkP_4D) |
| CADLIB | https://github.com/multigamesystem/MGS-CAD-Files (commit `c2cc26b`) |
| GH | https://github.com/multigamesystem and https://api.github.com/users/multigamesystem/repos |
| MW | https://makerworld.com/en/models/700005-mini-new-astro-city-arcade-machine |
| MUTE | https://www.hangedmandesign.com/mute-city-arcade/ |
| NACMAN | https://www.hard--candy.com/wiki/uploads/NewAstroCity/Downloads/NewAstroCity-Manual.pdf (Sega New Astro City Serviceman Manual, no. 420-6294-01, 58 PDF pages, scanned) |
| AOW | https://wiki.arcadeotaku.com/w/Sega_New_Astro_City |
| AOWSTRIP | https://wiki.arcadeotaku.com/w/New_Astro_City_Strip_Down_Guide |
| HC | https://www.hard--candy.com/wiki/candy/New_Astro_City |
| UKVAC | https://www.ukvac.com/forum/threads/sega-candy-cab-cp-height.85435/ |

Vendored clones (shallow, `--depth 1`):

| Directory | Upstream | Commit SHA | Commit date | Size |
| --- | --- | --- | --- | --- |
| `cad/vendor/mgs-cad-files` | CADLIB | `c2cc26be009e7c2825ff7b8162e8863d88b8be08` | 2023-04-20 | 47 MB of files, 11.5 MB on GitHub |
| `cad/vendor/mgs-mvs-u4-bartop` | BARTOP | `111b091500b99a94ab7690a2081f26b4a0b11d9c` | 2026-10-14 | 31 MB of files, 19.6 MB on GitHub |

Both clones contain their own `.git` directory. They are untracked in the worktree. Decide before the first `git add` whether `cad/vendor/` is ignored, kept as submodules, or committed. See the license notes in section 4 before committing `mgs-cad-files`.

Method: no file from the clones was executed, and no third-party `.FCStd` was opened (neither repository contains one). STEP files were read with `Part.read()` in `freecadcmd` 1.1.4. STL, 3MF and SVG files were parsed as data by scripts written for this task. The 3MF files are zip containers; they were read in memory only. The mean wall thickness figures come from pairs of opposite parallel planes in the mesh.

---

## 1. Reddit inspiration build: the aesthetic goal

URL: https://www.reddit.com/r/cade/comments/1xl7lxk/my_latest_two_builds_i_designed_in_cad_3d_printed/

The page stays INACCESSIBLE to automated tools: every fetch was blocked, and a real browser got a human-verification page. On 2026-11-09 the owner supplied three photos from the post. They are in `cad/vendor/reddit-mgs-mini-astro/` (`photo-a.png` three-quarter view from the right, `photo-b.png` front view, `photo-c.png` three-quarter view from the left, low resolution). Git ignores that directory. The photos belong to the builder.

The post shows two builds by the MGS builder. The larger one is a two-player Neo Geo style bartop. **The smaller one, a one-player New Astro City mini with an 8 inch 4:3 screen, is the aesthetic goal of this project.** It is not the MVS-U4 bartop of section 3, and no CAD file of it was found. The owner reports that the builder sells finished units of it and does not publish or sell its files. His GitHub account (section 2) holds other designs only.

### What the photos show

All values are ESTIMATED from pixel positions in `photo-b.png`. The scale is 3.26 px per mm, set by the lit 8 inch 4:3 image (162.6 mm wide). Parts nearer the camera read large, so treat each value as plus or minus 15 percent.

| Feature | Reading |
| --- | --- |
| Body width at screen height | about 230 mm |
| Control deck width | about 265 to 285 mm. The deck is wider than the body: about 1.15 to 1.25 times. |
| Overall height | about 360 to 400 mm, which is about 1.6 to 1.7 times the body width |
| Hood height | about 80 mm, which is about 0.35 of the body width |
| Black bezel face | about 204 mm wide, and about as tall as it is wide when seen from the front. The 4:3 image sits in the middle with thick black margins above and below (about 40 mm each) and thin ones at the sides (about 20 mm). |
| White frame beside the bezel | thin, about 4 percent of the body width on each side |
| Control deck front face | about 40 mm tall |
| Screen recline | about 20 to 25 degrees from vertical, read from the two three-quarter views, low confidence |

### Design language

- **Hood.** A separate rounded cap. Its top front edge and its top corners in front view have a large radius. A lit translucent strip follows the top front edge. Below the strip is a recessed band that holds two speaker pods and a marquee plate between them. The pods are square boxes that face straight forward. The hood projects forward of the screen face as a visor.
- **Screen face.** A black bezel sits back between two raised white side cheeks. The front edges of the cheeks are rounded. The bezel is a rounded rectangle.
- **Cheek to deck transition.** The reclined front edge of each cheek does not meet the deck at a corner. It sweeps forward in a concave curve into the side rail of the deck.
- **Body taper.** In front view the body is narrower at the hood than at the deck.
- **Control deck.** A thick slab. Its front edge, from the top down, is a radius, a shallow bevel band over about the upper 40 percent of the front, and then a front face that is close to vertical. Flat faces cut the front corners, seen from above. (An earlier reading, that the lower part was cut back, was wrong: the owner corrected it from `photo-e-three-quarter.png`.) The control plate is a separate inset panel with a clear cover and four corner screws, with a border of white deck around it. It carries a ball-top lever, six buttons in two arcs, and a start button at the right.
- **Sides.** Flat side panels with a vertical rear edge. A colored stripe follows the front edge. Three short horizontal slots sit near the top of the side panel.
- **Finish.** Gloss white body, one accent color for the lever, buttons, stripe and light strip. Small black feet.

### Two more photos, from the builder's Instagram

`photo-e-three-quarter.png` shows the finished cabinet from the front right. `photo-d-unpainted-shell.png` is a frame from a video of the bare printed shell. Readings, all ESTIMATED from the images:

- **The deck is a tray at the front only.** Behind the cheek sweep the body sides drop straight to the table at the body width. The wide deck does not run to the rear.
- **The cheek front edge is a wide facet, not a sharp corner.** A band about as wide as the cheek runs at an angle between the side panel and the front face, from the hood down into the deck.
- **The bezel is a separate frame** in a darker material, fitted from the front into the recess. It has a stepped inner edge around the screen opening.
- **The hood is an open arch.** Its top and sides are thick rounded bars. The speaker and marquee band is a separate part set back under the brow of the arch.
- **The deck top is part of the shell** in this build, with the lever and button holes printed in. It is not a removable plate. The colored control plate of the finished cabinet sits on top of it.
- **The shell is hollow with open back and ribs on the floor.** The side panel has a shallow round recess.
- **The side stripe** follows the cheek facet and ends in four short bars near the hood. The bars are part of the graphic, not vents.
- **Feet:** small black feet under the deck front and the body rear.

### The rear, from the builder's Instagram

`photo-f-rear.png` shows the bare shell from behind, with the hood open and two loose plates beside it. Readings, all ESTIMATED from the image:

- **Service opening.** A large rectangular opening low in the rear wall, with a screw boss at each corner. A separate door plate covers it. The door plate lies on the mat, partly hidden behind the cabinet. It has one large round vent in the middle and slot vents at its sides. The owner confirmed this reading.
- **Decorative slots.** Four short horizontal slots on each side of the service opening, in the rear wall. The owner reads them as decoration, not vents. The real vents are in the door.
- **Two recessed pockets** high on the rear wall, side by side. They are hand-holds for carrying, or recessed vents. Their floors slope.
- **Sculpted rear.** The upper rear stands proud of the lower rear. A curved step line divides them above the service opening.
- **Faceted rear corners.** The rear vertical edges are cut back at an angle, so the rear face is narrower than the body. The bottom edge is cut back in the same way.
- **Hood.** The hood is a separate module that bolts to the top of the body. From behind it shows two perforated speaker grilles at the outer ends, a marquee holder between them, and screw bosses along the top and bottom rails.
- **Floor.** The floor inside has ribs and slots.
- **A small round hole** low on the rear wall, beside the service opening, for a switch or a power jack.

This supports the layout of this project: a rear door that carries the fan vent. In the reference all the ventilation is in the door, and the side panels have none.

### Owner's direction, 2026-11-09

- Reconstruct this look as well as the photos allow, and change what the build needs.
- Speakers: the speaker fronts must follow the contour of the hood. Do not copy the square pods that face straight forward.
- Screen: the 16:10 screen stays usable. A 16:9 bezel is a candidate for the default, because 16:9 is the more common resolution and gives a more interesting bezel.
- Bezels are removable and swappable: 16:10 or 16:9 for PC games, 4:3 for arcade titles, and possibly a vertical (TATE) bezel.
- The display is centered in the bezel, and the cabinet height follows from that.
- The sight line to the screen center must be in the 15 to 25 degree range.
- Eight action buttons.
- The power supply is an EVGA SuperNOVA 1000 P5 (220-P5-1000-X1): fully modular, 150 mm deep.
- The fan is an ARCTIC P12 Pro on top of the BC-250 heatsink. The shroud is open: an available shroud design or one made for this cabinet.
- Practical choices for cooling, the wide screen and the controls belong to this project. The reference sets the look only.

---

## 2. Robert Dunn / multigamesystem GitHub profile

Profile name "Rob - Multi Game System", Massachusetts, USA, linked Instagram `robertdunnart` `[S:GH]`. Seven public repositories `[S:GH]`:

| Repository | License reported by GitHub | Relevance |
| --- | --- | --- |
| `MGS004NSM-MVS-U4-Bartop-Arcade` | `NOASSERTION` by the API; the `LICENSE` file is CC BY-NC 4.0 (section 3.11) | Cabinet print files. Section 3. |
| `MGS-CAD-Files` | none | Component STEP library. Section 4. |
| `MGS-3D-Print-Files` | none | One file, `Funnel Tray v2.stl`. Not relevant. |
| `MGS-Pico-Joystick` | GPL-3.0 | Pico joystick firmware. Not cabinet CAD. |
| `PicoFightingBoard` (fork) | none | Encoder PCB. Not cabinet CAD. |
| `Pico-Fighting-Board-Configuration` | none | Wiring help for that PCB. |
| `retro-pico-switch` (fork) | MIT | Not relevant. |

Only the two repositories named in the brief contain cabinet or component geometry.

---

## 3. MGS004 NSM, MVS-U4 style bartop

Local path: `cad/vendor/mgs-mvs-u4-bartop`. The repository has STL files for three of the five assemblies, six Bambu Studio 3MF projects, eight SVG outlines for laser-cut parts, reference renders and slicer plate screenshots. There is no STEP, F3D or other parametric source. The back-case panels exist only inside `BambuStudio 3MF/Back Case.3mf`.

### 3.1 Overall size and screen

| Item | Value | Tag |
| --- | --- | --- |
| Screen | 8 inch, 1024 x 768, IPS, panel HJ080IA-01E with driver board, landscape 4:3 | `[S:PARTS]` |
| Visible screen window in the bezel | 163.6 x 123.3 mm | `[M:stl/Front Assembly/Sceen Frame.stl]` |
| Cabinet width | 231.21 mm (same value on the front case, back frame, top case and control box) | `[M:stl/Front Assembly/Front Case Main.stl]` |
| Body height, base to top of body | 204.45 mm | `[M:BambuStudio 3MF/Back Case.3mf]` |
| Marquee (top case) height | 74.7 mm | `[M:stl/Top Case Assembly/Top Case Base.stl]` |
| Total height without feet | about 279 mm | `[E]` body plus top case, stacked as in the photos |
| Body depth without control box | about 195 mm, tolerance 10 mm | `[E]` from the back-case side outline (184.3 mm) plus the front wall offset; the parts are exported in separate frames, so the stack-up is inferred |
| Control box depth | 110.51 mm | `[M:stl/Joystick Assembly/Joystick Case.stl]` |
| Total depth | about 305 mm, tolerance 10 mm | `[E]` sum of the two rows above |

The cabinet width is below the 256 mm bed limit of the printer used (Bambu Lab P1S, 256 x 256 x 250 mm `[M:BambuStudio 3MF/*.3mf project settings]`). No part is split across the width. This is the main reason the design cannot be scaled to a 16 inch monitor: at the required width every cross-width part must be divided, and MGS has no joint for that.

### 3.2 Module split

Five bolted modules. Each module is small enough to print in a few pieces.

| Module | Printed parts (size in mm) | Tag |
| --- | --- | --- |
| Front assembly (screen) | Front Case Main 144.95 x 231.21 x 179.91, one piece, with the reclined screen face. Front Case Bottom 28.56 x 231.21 x 43.57, the vertical wall below the screen. Screen Frame (bezel) 198.9 x 177.78 x 15.44. | `[M:stl/Front Assembly/*.stl]` |
| Back case (body) | Ten flat parts: Back Case Frame Outer 231.21 x 8.0 x 204.45, Back Case Frame Inner 219.84 x 7.0 x 193.08, Left and Right Panel 1.4 x 170.74 x 190.28, Left and Right Inner Panel 9.49 x 184.86 x 204.45, Bottom Panel 220.04 x 173.76 x 1.4, Bottom Inner Panel 220.24 x 184.86 x 6.89, Top Panel 212.24 x 59.51 x 1.4, Top Inner 220.04 x 70.51 x 6.89. | `[M:BambuStudio 3MF/Back Case.3mf]` |
| Top case (marquee and speakers) | Top Case Base 231.21 x 72.51 x 74.7, Top Cover 227.01 x 47.64 x 12.07, Back Cover 222.5 x 24.91 x 71.74 (a 3.0 mm plate on a slope), two speaker housings, two speaker covers, two resin grilles, two vents, three marquee holder parts. | `[M:stl/Top Case Assembly/*.stl]` |
| Joystick assembly (control box) | Joystick Case 110.51 x 231.21 x 40.82, Control Panel Inner 68.6 x 207.47 x 7.0, Joystick Bottom Panel 226.41 x 105.71 x 3.0. | `[M:stl/Joystick Assembly/*.stl]` |
| Back door (hardware carrier) | MVS Back Door 208.41 x 40.46 x 181.64, plus slot parts for the Neo Geo board. A second door for a PC or Raspberry Pi is shown only as a render (`Refrence Images/Back Case Door PC.png`); there is no file for it. | `[M:stl/MVS 1 Slot Assembly/*.stl]` |

Plate count in the 3MF projects: Back Case 9 plates, Top Case 8, MVS slot assembly 4, Joystick Case 3, Front Case 2, Screen Frame 1 `[M:BambuStudio 3MF/*.3mf]`.

### 3.3 Back case: flat-pack laminate

The body is not a printed box. It is assembled from flat parts that all print lying on the bed without support (`Slicer plate layouts/Back Case.png`).

- Each wall is two layers. The outer layer is a plain 1.4 mm skin `[M]`. The inner layer is a panel with a grid of ribs; its total thickness is 6.89 mm for top and bottom and 9.49 mm for the sides `[M]`. Rib cells on the bottom inner panel are about 30 x 35 mm `[M]`.
- The outer skin is smaller than the inner panel (170.74 x 190.28 against 184.3 x 203.3 mm `[M]`), so the skin sits in a recess and its edges are covered.
- Two rectangular frames (outer 231.21 x 204.45 with 8.0 mm depth, inner 219.84 x 193.08 with 7.0 mm depth `[M]`) close the rear and give the back door a seat. The outer frame has a recess of 219.8 x 193.1 mm that receives the inner frame, and a through opening of 212.5 x 185.8 mm `[M]`. The inner frame opening is 201.6 x 174.8 mm `[M]`. The door (208.41 x 181.64 mm) therefore sits inside the outer frame with about 2 mm clearance per side and rests on the inner frame with about 3.4 mm overlap per side `[E]` from those sizes.
- The layers are joined with solvent cement. The parts list specifies "Weld-On #4" cement for ABS `[S:PARTS]`. Solvent welding is what makes thin 1.4 mm skins practical in this design.
- Holes found in these parts: 2.6 mm (6 per inner side panel), 3.0 mm (16 in the inner frame), 4.2 mm (6 per side skin, 9 in the bottom skin, 3 in the top skin), 4.8 mm (5 in the bottom inner panel, 4 in the inner frame) `[M]`. These agree with M3 screws and the M3 x 5.7 x 4.6 mm heat-set inserts in the parts list `[S:PARTS]`. Which hole takes an insert and which is a clearance or pilot hole is `[E]`; the repository has no assembly drawing.

### 3.4 Wall and rib thickness

| Feature | Thickness | Tag |
| --- | --- | --- |
| Shell walls of the front case, bezel, control box, top case and back door | 2.0 mm (the dominant pair spacing in every one of these files) | `[M:stl/**]` |
| Secondary flanges and ribs in the same parts | 1.6 mm | `[M]` |
| Back-case outer skins | 1.4 mm | `[M]` |
| Back-case ribbed inner panels, total | 6.89 mm and 9.49 mm | `[M]` |
| Control-box bottom panel, top-case back cover | 3.0 mm (both also exist as laser-cut outlines, so they can be 3 mm acrylic) | `[M]` and `[S:PARTS]` |
| Control panel inner plate | 2.0 mm deck with ribs to 7.0 mm | `[M:stl/Joystick Assembly/Control Panel Inner.stl]` |

These walls are thin because the material is ABS printed solid: 0.2 mm layers, 6 wall loops, 100 percent infill, 270 C nozzle, 100 C bed, tree supports, 5 mm brim ears, enclosed printer `[M:BambuStudio 3MF/*.3mf]` and `[S:BARTOP]` README. The brief already says not to carry this recipe to PETG on the A1.

### 3.5 Monitor mounting and removal

- The LCD sits behind a separate printed bezel (Screen Frame). The bezel has a 2.0 mm wall and a chamfer about 10.2 mm wide and 9.1 mm deep around the window, which is a slope of about 42 degrees `[M]`.
- A 3 mm clear acrylic sheet, 199.3 x 159.0 mm with 3 mm corner radius, covers the bezel and the screen as one glossy face `[M:svg/Screen Glass_Faces.svg]` and `[S:PARTS]`. The acrylic is the same size as the bezel face (198.9 x 158.6 mm `[M]`), so no printed surface is visible around the screen.
- The front case is a tray with the screen face printed down on the bed, ribs standing up, and three lugs along its top edge (`Slicer plate layouts/Front Case Main.png`). The three lugs match three 4.2 mm holes in the back-case top panel `[M]`. The front assembly therefore lifts off the body as one unit after the screws at the top and at the lower wall are removed `[E]` from hole positions and renders.
- How the LCD is clamped inside the bezel is not documented in the repository. Treat this as unknown.

The parts list says the files fit only this LCD panel `[S:PARTS]`. Nothing here transfers to a portable monitor with its own housing.

### 3.6 Control panel

- Separate control box, 231.21 wide, 110.51 deep, 40.82 high. The top is flat and horizontal: tilt 0 degrees. The front edge has a chamfer 10.7 mm deep and 17.8 mm high `[M:stl/Joystick Assembly/Joystick Case.stl]`.
- The body has a vertical front wall of the same 40.82 mm height and the same outline as the rear of the control box `[M:stl/Front Assembly/Front Case Bottom.stl]`. The box butts against this wall. The wall has four small holes (two of 3.0 mm, two of 3.4 mm), a cable opening 28.8 x 33.8 mm and a D-sub shaped cutout 28.4 x 11.7 mm `[M]`. The rear face of the box has a matching cutout 27.8 x 10.3 mm, a 23.8 mm round hole, and pairs of 3.8, 4.8 and 5.0 mm holes `[M]`. The cutout size agrees with a 15-pin D-sub connector `[E]`. Which hole pair takes the fixing screws is `[E]`. The control box is a removable unit located by a wall, held by a few screws through its rear face, and connected through one multi-pin connector.
- Panel build-up: printed inner plate (carries the joystick and gives stiffness), then printed artwork, then a 3 mm acrylic overlay 201.87 x 63.0 mm held by six screws in 3.6 mm holes `[M:svg/Control Panel Acrylic_Faces.svg]`.
- Controls: Sanwa JLF with its steel mounting plate removed; the parts list says no other joystick fits `[S:PARTS]`. Four Seimitsu PS-14-DN 24 mm screw buttons `[S:PARTS]` in 24.8 mm holes at 30.68 mm pitch; joystick hole 18.0 mm; joystick centre to first button centre 46.7 mm `[M:svg/Control Panel Acrylic_Faces.svg]`. Three 12 mm auxiliary buttons (DS-227) in 12.5 mm holes `[M]` and `[S:PARTS]`.
- A Raspberry Pi Pico inside the box is the encoder and also drives the credit display `[S:PARTS]`.

The 40.82 mm box height works only because the joystick plate is removed and the buttons are 24 mm. The joystick model in the CAD library needs 34.0 mm below the underside of its mounting plate `[M:CADLIB joystick STEP]`. A full-size panel with 30 mm buttons and a plate-mounted joystick needs more depth and more height than this box.

### 3.7 Computer and power

- All electronics mount on the inside of the removable back door (`Refrence Images/MVS 1 Slot Assembly Inside.png`). The door is 208.41 x 181.64 mm and drops into the rear frame `[M]`.
- Two door variants. One carries a Neo Geo MV-1C board, a video scaler, an ESP8266 board and an ATX breakout board `[S:PARTS]`. The other is for a PC or Raspberry Pi; its render shows a fan, an HDMI pass-through, two USB ports, a push button and a knob `[E]` read from `Refrence Images/Back Case Door PC.png`.
- Power is external: a 12 V 8 A brick and a 12 V input Pico PSU inside `[S:PARTS]`. There is no mains wiring and no internal power supply. This cabinet gives no guidance for an ATX supply in the base.

### 3.8 Ventilation

- One fan in the centre of the back door. Opening diameter 60.0 mm `[M:stl/MVS 1 Slot Assembly/MVS Back Door.stl]`.
- 36 slots of 20.7 x 2.0 mm in the floor skin, about 1490 mm2 open area `[M]` (area is `[E]`, count times slot size).
- Two louvre vent inserts in the top case, each 46.19 x 13.18 x 12.79 mm `[M:stl/Top Case Assembly/Vent 1.stl]`.
- Flow path: floor slots and top vents with a fan at the rear `[E]` from part positions. The heat load is a few watts to a few tens of watts. It is not a model for a BC-250.

### 3.9 Acrylic and other non-printed layers

All acrylic is 3 mm clear cast sheet, laser cut `[S:PARTS]`. Outlines in `svg/` (units are centimetres in the files; values below are converted):

| File | Size (mm) | Holes | Tag |
| --- | --- | --- | --- |
| `svg/Screen Glass_Faces.svg` | 199.30 x 158.98 | none | `[M]` |
| `svg/Control Panel Acrylic_Faces.svg` | 201.87 x 63.00 | 4 x 24.8, 1 x 18.0, 6 x 3.6 | `[M]` |
| `svg/Marquee_Faces.svg`, `svg/Marquee Clear_Faces.svg` | 173.00 x 72.00 | 3 x 3.4 | `[M]` |
| `svg/Top Case Back Cover_Faces.svg` | 222.50 x 74.20 | 6 x 3.0 | `[M]` |
| `svg/Credit Marquee Acrylic_Faces.svg` | 148.12 x 20.15 | 3 slots | `[M]` |
| `svg/Game Marquee 4 slots_Faces.svg` | 147.46 x 45.62 | 4 windows | `[M]` |
| `svg/Game Marquee Slot 1_Faces.svg` | 45.62 x 36.86 | none | `[M]` |

There is no metal reinforcement anywhere in the design. Stiffness comes from solid ABS, the laminate, and the acrylic faces. The speaker grilles are resin prints `[S:BARTOP]`. Speakers are Dayton Audio CE32A-8, 1-1/4 inch, with a PAM8403 amplifier `[S:PARTS]`.

### 3.10 Profile geometry

| Feature | Value | Tag |
| --- | --- | --- |
| Screen recline from vertical | 35.6 degrees (the screen face normal is 54.41 degrees from vertical; the back-case side outline gives 35.58 degrees) | `[M:stl/Front Assembly/Front Case Main.stl]` and `[M:BambuStudio 3MF/Back Case.3mf]` |
| Body side outline, rear at 0, floor at 0 (depth, height) | (0, 0) (184.3, 0) (184.3, 4.8) (70.0, 164.6) (70.0, 203.3) (0, 203.3) | `[M:BambuStudio 3MF/Back Case.3mf, object_11]` |
| Body top depth and bottom depth | 70.0 mm and 184.3 mm | `[M]` |
| Control panel tilt | 0 degrees | `[M]` |
| Control panel depth | 110.51 mm, which is 0.48 of the cabinet width | `[M]`, ratio `[E]` |
| Control surface height above the table | 40.82 mm plus feet | `[M]` |
| Height above the control surface | about 238 mm, which is 1.03 of the cabinet width | `[E]` 204.45 + 74.7 - 40.82 |
| Marquee module | 74.7 mm high (0.32 of width), 72.51 mm deep at the base and 47.2 mm at the top; front face vertical; rear face leans forward 17.3 degrees | `[M:stl/Top Case Assembly/Top Case Base.stl]` |
| Marquee window | 177.8 x 67.2 mm with a 25.7 mm speaker column on each side | `[M]` |
| Hood overhang | none; the marquee face is vertical and starts at the top edge of the reclined screen face | `[E]` from renders and photos |
| Screen window width to cabinet width | 0.71 | `[E]` 163.6 / 231.21 |
| Bezel margin around the window | about 17.6 mm on all four sides | `[E]` from measured frame and window |

### 3.11 License of the bartop repository

The `LICENSE` file is the unmodified Creative Commons Attribution-NonCommercial 4.0 International legal code. A diff against https://creativecommons.org/licenses/by-nc/4.0/legalcode.txt shows only a missing final newline. SHA-256 of the file: `3711f963c05d0be80d53e5923308a6dee31b203da23435c9cfb7c7b6e4dd5e19`. GitHub reports `NOASSERTION` only because its detector does not classify this text.

Terms that matter (section numbers refer to the legal code):

- Permitted: copy and redistribute the material in any medium or format, and produce and share adapted material, for NonCommercial purposes only (2.a.1). NonCommercial means "not primarily intended for or directed towards commercial advantage or monetary compensation" (1.i).
- Attribution when sharing, also in modified form (3.a.1): keep the identification of the creator, any copyright notice, the license notice, the warranty disclaimer notice, and a link to the material where practical; state whether you changed it and keep notice of earlier changes; state that it is under CC BY-NC 4.0 and give the license text or link. Any reasonable manner is acceptable (3.a.2).
- No required wording is given. Neither `LICENSE` nor `README.md` specifies an attribution string. A sufficient form is: "Based on MGS004 NSM MVS-U4 Bartop Arcade by Robert Dunn (multigamesystem), https://github.com/multigamesystem/MGS004NSM-MVS-U4-Bartop-Arcade, licensed CC BY-NC 4.0. Modified." Remove "Modified" if the file is unchanged.
- Derivatives: allowed. There is no ShareAlike condition. Your own license on an adaptation must not stop recipients from following CC BY-NC for the MGS material (3.a.4), so the noncommercial and attribution conditions stay attached to anything derived from these files.
- No added restrictions or technical protection measures on the licensed material (2.a.5.B). No implied endorsement (2.a.6). Patent and trademark rights are not licensed (2.b.2); the Neo Geo, MVS and SNK marks on the artwork are not covered.
- The license ends automatically on a breach and is restored if the breach is corrected within 30 days of discovery (6.a, 6.b). No warranty (5).
- The author offers vinyl graphics, laser-cut parts and UV-printed acrylic on request through social media `[S:BARTOP]` README. Selling parts made from these files is not permitted to others.

Using the files privately as a reference does not involve sharing, so the attribution conditions apply when CAD, files or a write-up derived from them are published. This is a reading of the license text, not legal advice.

---

## 4. MGS-CAD-Files component library

Local path: `cad/vendor/mgs-cad-files`. Ten STEP files (ISO 10303-21, schema AP214 `AUTOMOTIVE_DESIGN`), each with a PNG or JPG preview, all in one directory, `STEP files with images/`. All ten loaded in FreeCAD 1.1.4 and all report a valid shape `[M]`. The full inventory with measured envelopes is in the last section.

Findings:

- The library is small. It has one joystick, one 12 mm push button, three Raspberry Pi boards, one encoder PCB, two connectors, a Pi mount and a workshop tray.
- It has no 30 mm button, no 24 mm button, no speaker, no fan, no power inlet, no switch, no foot, no fastener or insert, no LCD and no power supply. The brief expected some of these. Those envelopes must come from manufacturer drawings or from measurement of the purchased parts.
- License: the repository has no `LICENSE` file and GitHub reports no license `[S:GH]`. The README says the files are ones the author "created or found on the internet" and that they "should prove useful for anyone looking to create their own custom arcade or game hardware" `[S:CADLIB]`. That is an invitation to use them. It is not a license, and the authorship of each file is not stated. The CC BY-NC license of the bartop repository does not extend to this repository.
- Practical rule: use these STEP files as local reference envelopes. Do not redistribute them, and do not publish a project that contains them, without permission from the author. For any published FreeCAD project, model simplified envelopes from manufacturer data.

---

## 5. Mini New Astro City, 9.7 inch (MakerWorld 700005)

Status: PARTLY ACCESSIBLE. The MakerWorld page was read through the Kagi extract tool. The model files need a MakerWorld login and were not downloaded. The original designer's page (https://www.game-makers.xyz/mini-new-astro-city/index.html) failed with a TLS error and a timeout; the Cults3D listing returns HTTP 410.

| Item | Value | Tag |
| --- | --- | --- |
| Design origin | Game-Makers "Mini New Astro City", a one-player bartop with a 9.7 inch 4:3 LCD, a small TFT marquee and a Raspberry Pi 3 | `[S:MW]` and search snippet of the Game-Makers page |
| This listing | A remix by CabLab that cuts the original parts for beds smaller than the 300 x 300 mm the original needs | `[S:MW]` |
| Print profile | 13 plates, 61.8 hours, 2109 g PETG, 0.2 mm layers, 3 walls, 15 percent infill | `[S:MW]` |
| Joints between cut parts | cyanoacrylate glue, then putty over the seams "to make them invisible" | `[S:MW]` |
| Computer | Raspberry Pi 3 or 4; controls through GPIO or a zero-delay USB encoder | `[S:MW]` |
| Printer reports | users report complete prints on a Bambu A1 and a P1S | `[S:MW]` comments, and search snippet of r/cade thread 1pzedf8 |
| Overall dimensions | not stated on any page that could be read | n/a |
| Active area of a 9.7 inch 4:3 panel | about 197 x 148 mm | `[E]` from the diagonal |

Shell split, from the designer's exploded render (reproduced on the Mute City page, `img09.JPG`) `[E]` from the image:

- One main body: two side cheeks, back and floor as a single monocoque part. The back wall has perforated vent fields and the board ports.
- A flat monitor bezel frame that fastens to the front of the body, with the LCD behind it.
- A hood ("topper") on top and a separate speaker panel under it. The speaker panel exists in a plain version and a version with a TFT marquee `[S:MW]`.
- A control box in two parts: the top with the button holes and a front fascia with two more buttons. Six action buttons in the original.

Problems reported by users `[S:MW]` comments:

- A user who scaled the model to 195 percent could not print the hood in two vertical halves with tree supports and asked for a split that prints flat.
- Users asked for a longer control deck with more palm rest, two more buttons, a swappable two-player deck and a digital marquee. The stock control deck is short for adult hands.
- The power inlet cutout changed between versions of the original; cutouts for bought components must be checked against the part in hand.

Profile: the silhouette copies the New Astro City at reduced scale, with curved cheeks, a reclined screen and a hood that projects forward. No angle is published. The recline looks like 20 to 25 degrees in the render `[E]`, low confidence, perspective image.

---

## 6. Mute City (larger Astro-style adaptation)

Status: ACCESSIBLE. Full article read.

| Item | Value | Tag |
| --- | --- | --- |
| Base model | Game-Makers Mini New Astro City STL files, scaled up uniformly in Bambu Studio | `[S:MUTE]` |
| Scaling rule | scaled until the monitor enclosure between the two sides was "exactly 400mm wide" | `[S:MUTE]` |
| Scale factor | about 2 | `[E]` 20.1 inch screen in place of 9.7 inch |
| Screen | Dell 2007FPb 4:3 LCD; a smaller 16:9 LCD was tried first and looked too small in the frame | `[S:MUTE]` |
| Printer and bed | Bambu A1, 256 mm cube; the source model assumes a 300 mm cube | `[S:MUTE]` |
| Material | 5 to 6 kg of white PETG, plus small amounts of other PET and PETG | `[S:MUTE]` |
| Cost | about 250 USD for all materials except the game computer | `[S:MUTE]` |
| Overall dimensions | not stated | n/a |
| Outer width | about 470 to 490 mm | `[E]` 400 mm inner width plus two hollow side cheeks seen in the Blender screenshot |

Shell split `[S:MUTE]`:

- The main body mesh was cut into four major pieces: two sides, upper back, and lower back with floor. Each was cut again into four. That is 16 body pieces.
- The control box, hood, speaker box and bezel were also cut, most of them into two plates.
- All cuts were made in the slicer on a mesh, after the model was scaled.

Joints `[S:MUTE]`:

- Slicer-generated connectors: round posts with matching sockets, and dovetails. Fixed with gel cyanoacrylate. No mechanical fasteners in the shell seams.
- Assorted bolts, nuts, wing nuts and threaded rod are used for the monitor enclosure, an internal shelf and the port covers.
- The author reports "mixed results": gaps in the body where cut lines were badly placed, and places where posts were forgotten. Two front brackets that join the control box to the body were cut off by mistake and had to be redesigned. A dovetail used to hang a USB hub enclosure from a cover "wasn't a great idea".

Monitor mount `[S:MUTE]`: the bezel attachment of the original model was kept. A new bezel was made by filling the aperture and subtracting a box the size of the monitor. The first enclosure fitted the 16:9 LCD. The second, for the heavier 4:3 monitor, needed several redesigns and is held together with threaded rods. It was painted black to cut glare.

Control panel `[S:MUTE]`: separate control box in two halves. The top was rebuilt from a flat surface with a Vewlix button layout subtracted. It flexed when buttons were pressed until support posts were added under it. Sanwa JLF and buttons, Brook Universal Fighting Board.

Computer and power `[S:MUTE]`: any HDMI and USB device is placed inside; a MiSTer FPGA was used. A surge-protected power strip with USB ports sits inside. An internal shelf stands on threaded-rod standoffs over the floor fan ports. A USB hub is reachable from outside through one port cover.

Ventilation `[S:MUTE]`: one standard opening, the cutout and screw pattern of an 80 mm case fan, was subtracted at several places on the sides, back and floor. The Blender screenshot shows eight `[E]`. Each opening takes a grille, a blank cover or a recessed peripheral cover. The covers are screwed from inside so they cannot be removed from outside. The covers came from a parametric grille generator.

Wall and rib thickness: not stated. The side cheeks are hollow box sections several centimetres thick in the screenshots `[E]`.

Reinforcement: no acrylic or metal layers. Threaded rod is the only metal structure.

Finish `[S:MUTE]`: enamel primer and gloss spray paint are listed, with vinyl graphics. The photos of the finished cabinet show the cut lines across the hood centre and across both side cheeks `[E]` from the photos. The seams were not filled.

The author's own verdict: "if I was making a second one I'd do just about everything differently" `[S:MUTE]`.

---

## 7. Sega New Astro City (styling reference)

### 7.1 Published data

| Item | Value | Tag |
| --- | --- | --- |
| Installation space | 750 mm wide x 905 mm deep | `[S:NACMAN]` specifications box, PDF page 3; also `[S:AOW]`, `[S:HC]` |
| Height | 1445 mm | `[S:NACMAN]` |
| Weight | 93 kg (the Hard-Candy page lists 95 kg) | `[S:NACMAN]`, `[S:HC]` |
| Power | 142 W | `[S:NACMAN]` |
| Monitor | 29 inch CRT, 15 and 24 kHz, Nanao MS9-29; can be installed horizontal or vertical by removing and refitting, no pivot | `[S:AOW]`, `[S:HC]` |
| Control panel height, floor to top surface | 650 mm on a New Astro City; 660 mm on an Astro City (forum members' own measurements) | `[S:UKVAC]` posts 2 and 4 |
| Seat height used with it | 400 to 450 mm | `[S:UKVAC]` posts 7 and 10 |
| Standard panel | 2L6B (two joysticks, six buttons each), removable plate on a hinged base with locking brackets; panels interchange across the Astro family | `[S:AOW]` |
| Speakers | two 4 ohm 10 W units above the monitor | `[S:AOW]` |
| Marquee lamp | 15 W fluorescent | `[S:AOW]` |
| Game board mounting board | about 483 x 400 x 10 mm | `[S:AOW]` |

The control panel angle, the monitor angle and the hood overhang are not published in the manual or on the wiki pages.

### 7.2 Profile estimated from the manual drawings

Basis: the side elevation "ASSY SUB-CABINET CE (NAS-1001CE)" on PDF page 34 (printed page 31) of `[S:NACMAN]`, and the side view of "ASSY FRONT PANEL CE (NAS-1100CE)" on PDF page 35 (printed page 32). Pixel positions were read from 250 and 300 dpi renders. The scale is 1.025 mm per pixel on page 34, fixed by setting the drawn depth equal to 905 mm. Two checks support the scale: it puts the control-panel shelf at about 616 mm, and a panel assembly on top of the shelf reaches the measured 650 mm; and the hood height read from page 35 puts the top at about 1455 to 1470 mm against the published 1445 mm. Parts-catalogue drawings are not dimensioned, so every value in this table is `[E]` with an uncertainty of about 5 percent, or 2 degrees for the angle.

| Feature | Estimate | Ratio |
| --- | --- | --- |
| Recline of the monitor mounting plane from vertical | 26 degrees (three parallel lines on page 34 give 25.9, 26.6 and 27.0; page 35 gives 25.8) | n/a |
| Control panel tilt | about 0 degrees; the shelf is drawn horizontal | n/a |
| Top of rear cabinet, without the hood | about 1255 mm | 0.87 of height |
| Hood (billboard) height above the rear cabinet top | about 190 mm (1445 minus 1255) | 0.13 of height, 0.25 of width |
| Height above the control surface | 795 mm (1445 minus 650, both sourced) | 1.06 of width |
| Control shelf front edge to the foot of the screen plane | about 370 mm | 0.41 of depth, 0.49 of width |
| Body depth behind the foot of the screen plane | about 535 mm | 0.59 of depth, 0.71 of width |
| Control shelf overhang in front of the lower front panel (knee space) | about 250 mm | 0.27 of depth |
| Lower body depth, lower front panel to rear wall | about 655 mm | 0.73 of depth |
| Flat top of the rear cabinet | about 145 mm deep | 0.16 of depth |
| Hood base depth | about 220 to 235 mm | n/a |
| Speaker pod face in front of the screen plane at the top edge of the screen | about 65 to 70 mm | 0.09 of width |
| Bezel side wings in front of the screen plane at mid height | about 130 mm, low confidence | 0.17 of width |
| Tube face of a 29 inch 4:3 CRT | about 590 x 440 mm; the visible picture is smaller | 0.79 of width |

Side silhouette `[E]` from the drawings and the photos on `[S:HC]`: the rear wall is vertical through the monitor zone, steps inward toward the base and has four vent slots at monitor height. The upper front runs up and back in a straight line from the control panel to the hood. The side cheeks (bezel wings) curve forward of that line and are deepest near the bottom of the screen. The hood sits on top as a separate block with two speaker pods at its outer ends and the marquee between them. Below the control panel the front is recessed for the knees.

### 7.3 How the real cabinet is divided

From the parts catalogue in `[S:NACMAN]` and from `[S:AOWSTRIP]`:

- The body is two shells, a rear cabinet and a front lower section ("cash panel"). They join on a flange that runs up both sides and across the bottom, with 16 tapping screws 5 x 20 at a stated torque of 55 kgf cm, plus a retainer with M5 x 16 screws `[S:NACMAN]` PDF page 34.
- The monitor surround, with the speaker pods and marquee, is one front panel assembly. It lifts off after the screws under the control panel and one speaker connector are removed `[S:AOWSTRIP]`.
- The monitor bolts to an internal frame and lifts out forward `[S:AOWSTRIP]`.
- The control panel assembly fastens to the cabinet with six M4 x 16 carriage bolts and flange nuts `[S:NACMAN]` PDF page 30.
- Service access is from the front `[S:AOW]`.

The real cabinet uses the same division the brief asks for: a load-carrying body in two flanged shells, a cosmetic front assembly that lifts off, and a monitor on its own frame.

---

## 8. Profile numbers side by side

| Feature | New Astro City | MGS004 NSM | Mini New Astro City | Mute City |
| --- | --- | --- | --- | --- |
| Width x depth x height (mm) | 750 x 905 x 1445 `[S:NACMAN]` | 231 x about 305 x about 279 `[M]`/`[E]` | not published | inner width 400 `[S:MUTE]`, rest not published |
| Screen | 29 inch CRT 4:3 `[S:AOW]` | 8 inch LCD 4:3 `[S:PARTS]` | 9.7 inch LCD 4:3 `[S:MW]` | 20.1 inch class LCD 4:3 `[S:MUTE]`, size `[E]` |
| Screen recline from vertical | 26 degrees `[E]` | 35.6 degrees `[M]` | 20 to 25 degrees `[E]` low confidence | same shape as the mini `[E]` |
| Control panel tilt | about 0 degrees `[E]` | 0 degrees `[M]` | about 0 degrees `[E]` | about 0 degrees `[E]` |
| Control panel depth to width | 0.49 `[E]` | 0.48 `[M]` | short; users extended it `[S:MW]` | not measured |
| Height above control surface to width | 1.06 `[S]` | 1.03 `[E]` | not measured | not measured |
| Marquee or hood height to width | 0.25 `[E]` | 0.32 `[M]` | not measured | not measured |
| Hood in front of the screen plane at the screen top | about 0.09 of width `[E]` | none `[E]` | present `[E]` | present `[E]` |
| Screen width to cabinet width | 0.79 tube face `[E]` | 0.71 window `[E]` | not measured | not measured |

Notes for a 16 inch 16:10 screen:

- The candy-cab look comes from four things that are the same in the real cabinet and in the MGS miniature: a flat control deck about half as deep as the cabinet is wide, an upper body about as tall as the cabinet is wide, a straight reclined screen plane, and a marquee block about a quarter to a third of the width in height.
- All four references use a 4:3 screen. A 16:10 screen is lower for the same width. At equal proportions the cabinet will have either a larger bezel above and below the screen, a taller marquee, or a lower overall height. This is a styling decision for the lead designer.
- The real recline is about 26 degrees. The MGS value of 35.6 degrees suits a very small screen viewed from above at a desk. The ergonomic test in the brief should fix this angle.
- The active image is about 345 mm wide and the monitor body about 355 mm (both from the brief, both to be measured). With a screen to cabinet width ratio of 0.71 to 0.79 the outer width would be about 440 to 490 mm `[E]`. The minimum is the monitor body plus cradle clearance plus two side walls.

---

## Techniques worth adopting

Adopt:

1. Bolted modules with one job each. MGS has a front screen assembly, a body, a marquee module, a control box and a hardware door. The real cabinet has two body shells, a lift-off front assembly and a monitor frame. Use the same division: body and base, monitor cradle and bezel, hood, control deck, rear service cover or tray. Sources: section 3.2 and 7.3.
2. M3 heat-set inserts with M3 machine screws for every service joint. MGS specifies M3 x 5.7 x 4.6 mm inserts, quantity 100, and stainless button-head screws `[S:PARTS]`. Insert boss size for PETG must come from the insert coupon in the brief.
3. Flanged body joints with a row of fasteners, as in the real cabinet (16 screws on one flange line `[S:NACMAN]`). For a body wider than the bed, design a flange or a backing strip across each split and put screws through it. Do not rely on a butt joint.
4. Flat panels printed lying on the bed, stiffened by a second ribbed layer. The MGS body is 1.4 mm skin on a ribbed panel 6.9 to 9.5 mm thick with cells of about 30 x 35 mm `[M]`. The parts print without support, the visible face is the bed face, and each fits the plate. MGS bonds the layers with ABS solvent cement, which is not available for PETG. A PETG version must bond with a tested adhesive, or use screws, or print the skin and ribs as one part. The joined coupon in the brief should test this.
5. Put the visible face on the bed. The MGS front case prints with the screen face down and ribs up `[S:BARTOP]` plate layouts.
6. Cover faces with 3 mm acrylic. MGS covers the bezel and screen with one sheet, covers the control panel with a second, and uses a third for the marquee `[M]`. A sheet across a printed split also hides the seam and ties the two halves together. Use this at the centre split of the bezel, the hood and the control deck, where a seam would otherwise be most visible.
7. Build the control panel as a sandwich: a rigid inner plate that carries the joystick, then artwork, then an overlay `[M]`. For a full-size panel in PETG the inner plate should be a rigid subplate, as the brief already suggests. Add posts or ribs under the deck from the start; the Mute City deck flexed until posts were added `[S:MUTE]`.
8. A control box that meets a vertical wall on the body, with two screws and one multi-pin connector (section 3.6). This is a tested pattern for a swappable panel: the mechanical datum is the wall, and the electrical interface is one connector that cannot be pulled by its wires.
9. A rear door or tray that carries the electronics, with the fan and the external connectors on the same part (section 3.7). The BC-250 tray can follow this pattern. The door seats in a frame, so it locates without the screws.
10. One standard port opening repeated around the body, with interchangeable covers fixed from inside `[S:MUTE]`. For this build the pattern can be a 120 mm fan. It lets the exhaust and intake arrangement change after the thermal test without a reprint of the body.
11. Floor slots and high vents so that natural convection supports the fan (section 3.8).
12. Brim ears on the corners of large flat parts. MGS uses 5 mm ears `[M]`.
13. Through-rods to clamp a monitor enclosure and to carry shelves `[S:MUTE]`. This agrees with the through-bolt direction in the brief.
14. Record the print orientation of every part with the files. The MGS plate screenshots and 3MF projects make the build repeatable.

Avoid:

1. Uniform scaling of a small design. Screw holes, ports, connector cutouts and button spacing scale with it and stop fitting `[S:MUTE]`. The MGS control layout is 24 mm buttons at 30.68 mm pitch with the stick 46.7 mm from the first button `[M]`; it is not an adult layout.
2. Splits made in the slicer after the shape is final. Mute City had gaps, missing posts and removed brackets `[S:MUTE]`. Draw the splits and the joint features in FreeCAD as part of each module.
3. Glue-only seams on structural or service joints. The mini (2.1 kg `[S:MW]`) and Mute City rely on cyanoacrylate with posts. That is acceptable for small cosmetic subassemblies and wrong for joints that carry the monitor, the joystick or the power supply.
4. Dovetails that carry a hanging load in the layer direction `[S:MUTE]`.
5. A one-piece monocoque body (section 5). At this size it forces many arbitrary cuts and leaves no flat faces to print on the bed.
6. The MGS wall recipe as it stands: 2.0 mm shells in solid ABS, at a span of 231 mm `[M]`. The spans in this build are about twice as long and the material is PETG with normal infill. Treat 2 mm as a lower limit for small covers. Size walls and ribs from the stiffness coupons.
7. The MGS print settings: ABS, 100 percent infill, 6 walls, 270 C, 100 C bed, enclosure `[M]`. The brief excludes them.
8. Tall thin half-shells printed upright on tree supports. A user failed with the hood at 195 percent scale `[S:MW]`. Split the hood so that each piece lies flat.
9. A control box as low as the MGS one (40.82 mm `[M]`). It needs the joystick plate removed and 24 mm buttons.
10. Building a monitor mount before the monitor choice is final. Mute City made two enclosures `[S:MUTE]`.
11. Unfilled centre seams on the hood and the side cheeks. They are the first thing visible on the finished Mute City cabinet `[E]` from photos. Place splits on body lines, under trim, or under acrylic.

---

## Component CAD inventory

### MGS-CAD-Files (`cad/vendor/mgs-cad-files/STEP files with images/`)

All files are STEP AP214. Envelope sizes are bounding boxes measured in FreeCAD `[M]`. License: none stated (section 4).

| File | Size | Solids | Envelope X x Y x Z (mm) | Content and use in this build |
| --- | --- | --- | --- | --- |
| `Sanwa JLF-TP-8YT Joystick v55.step` | 3.0 MB | 40 | 95.0 x 70.4 x 102.0 | Joystick assembly. Mounting plate 95.0 x 53.0 x 1.5; main body 75.0 x 60.0 x 31.0; ball 35.0 diameter; lowest point 34.0 below the plate underside; ball top 66.5 above the plate top. Usable as the joystick envelope. The candidate in the brief is the JLX2-TP-8YT, a different model; check its drawing before the panel depth is fixed. Hole pattern not verified. |
| `Blue - Button - DS-227 - Updated v3.step` | 0.84 MB | 8 | 16.3 x 16.3 x 29.4 | 12 mm panel push button (thread about 11.9 diameter, head 16.3 diameter). Usable for service, menu or power buttons. It is not an arcade play button. |
| `Pico Fighting Board v1.1a.step` | 5.0 MB | 89 | 96.3 x 45.3 x 11.9 | Encoder PCB that carries a Raspberry Pi Pico; board 96.14 x 45.21 x 1.58. Usable only if this board is chosen for GP2040-CE. |
| `Raspberry Pi Pico-R3 v2.step` | 2.5 MB | 8 | 21.0 x 52.4 x 3.7 | Raspberry Pi Pico. Envelope for a bare Pico encoder or a marquee controller. |
| `JST - XH - Thru (V) - 5Pin - 2.54mm v1.step` | 0.49 MB | 1 | 14.8 x 5.8 x 10.2 | 5-pin vertical header. Clearance body for a harness connector; confirm the connector series on the real joystick. |
| `Raspberry Pi 4 Model B v4.step` | 17.5 MB | 109 | 89.0 x 58.4 x 19.9 | Board model. Useful only if the marquee uses a Pi. Slow to load. |
| `Raspberry Pi 3 v2.step` | 7.6 MB | 77 | 58.5 x 89.5 x 20.0 | Board model with microSD. Same note. |
| `Basic Raspberry Pi Mount v1.step` | 63 KB | 1 | 57.0 x 66.0 x 12.0 | Printable mount plate with posts. Reference for standoff design. |
| `Black Jamma (Jamma EDGE connector) v12.step` | 6.7 MB | 57 | 134.0 x 10.0 x 20.0 | JAMMA edge connector. Not needed. |
| `Funnel Tray v2.step` | 103 KB | 1 | 106.5 x 106.5 x 20.0 | Workshop tray. Not needed. |

Each STEP file has a preview image with the same base name (`.png` or `.jpg`). The joystick has two identical JPG previews.

Not in the library: 30 mm and 24 mm arcade buttons, speakers, fans, power inlets, rocker switches, feet, fasteners and inserts, LCD panels, power supplies, USB encoders other than the Pico boards.

### Useful reference files in the bartop repository (`cad/vendor/mgs-mvs-u4-bartop/`)

Meshes and 2D outlines only. License CC BY-NC 4.0 (section 3.11).

| File | Format | Envelope (mm) | Content and use |
| --- | --- | --- | --- |
| `svg/Control Panel Acrylic_Faces.svg` | SVG, units cm | 201.87 x 63.00 | Overlay with 24.8 mm button holes, 18.0 mm joystick hole and six 3.6 mm screw holes. Reference for an overlay drawing; the layout itself is too compact. |
| `svg/Screen Glass_Faces.svg` | SVG | 199.30 x 158.98 | Screen cover outline. Reference for a one-piece acrylic face over bezel and screen. |
| `svg/Marquee_Faces.svg` | SVG | 173.00 x 72.00 | Marquee sheet with three 3.4 mm holes on the top edge. |
| `svg/Top Case Back Cover_Faces.svg` | SVG | 222.50 x 74.20 | Rear cover of the marquee module with six 3.0 mm holes. |
| `stl/Joystick Assembly/Control Panel Inner.stl` | STL | 68.6 x 207.47 x 7.0 | Ribbed inner plate with the mounting bosses for a JLF without its steel plate. Reference for plate-less mounting. |
| `stl/Joystick Assembly/Joystick Case.stl` | STL | 110.51 x 231.21 x 40.82 | Control box shell with ribs, corner bosses and the rear connector cutout. |
| `stl/Front Assembly/Front Case Bottom.stl` | STL | 28.56 x 231.21 x 43.57 | Body front wall that the control box mates with. Reference for the panel interface. |
| `stl/Front Assembly/Sceen Frame.stl` | STL | 198.9 x 177.78 x 15.44 | Bezel with chamfered window. Reference for bezel section and chamfer. |
| `stl/MVS 1 Slot Assembly/MVS Back Door.stl` | STL | 208.41 x 40.46 x 181.64 | Hardware door with 60 mm fan opening, ribs and board bosses. Reference for the compute tray. |
| `stl/Top Case Assembly/Speaker Housing CE32A-A Left.stl` (and `Right`) | STL | 16.42 x 43.15 x 53.24 | Pocket for a Dayton CE32A-8 speaker. Usable as a speaker pocket reference if that speaker is chosen. |
| `stl/Top Case Assembly/Vent 1.stl` (and `Vent 2`) | STL | 46.19 x 13.18 x 12.79 | Louvre vent insert. |
| `stl/Top Case Assembly/Speaker Grille L.stl` (and `R`) | STL, 5.2 MB each | 18.99 x 62.39 x 10.14 | Fine grille for resin printing. Not printable on the A1. |
| `BambuStudio 3MF/Back Case.3mf` | 3MF (zip) | ten parts, see section 3.2 | The only source of the back-case panel meshes. Also holds the print settings. |
| `BambuStudio 3MF/*.3mf` (five more) | 3MF | n/a | Plate arrangement and print settings for the other modules. |
| `Slicer plate layouts/*.png` | PNG | n/a | Print orientation of every part. |
| `Refrence Images/*.png` | PNG | n/a | Renders of each module, including the PC back door and the board layout on the MVS door. |

---

## Open items

- Reddit thread: the text and comments are not read. Section 1 rests on three photos only. A straight side view and the rear of the mini are missing.
- Mini New Astro City: overall dimensions, screw sizes and the bezel attachment are on the Game-Makers page and in the model files, neither of which could be read.
- MGS: the LCD clamp behind the bezel and the exact role of each hole size are not documented. The repository README says the documentation is unfinished.
- New Astro City: the profile values in section 7.2 are read from undimensioned drawings. A measured side elevation from an owner would replace them.
- The Sanwa model in the library is the JLF, not the JLX2 candidate in the brief.
- The measurement scripts used for this note were temporary and are not in the repository. All values they produced are written in this file.
