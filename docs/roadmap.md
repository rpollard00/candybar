# Roadmap

Last update: 2026-11-10. Update this file at the end of each work session.

The goal is a cabinet that can be printed on the Bambu A1 and assembled, and that looks like the reference cabinet. `CONTEXT.md` defines the words. `docs/adr/` records the decisions that are hard to reverse.

## Phases

| Phase | Result | State |
| --- | --- | --- |
| 1. Layout study | Hardware envelopes, keep-out zones, two control panel tiles, layout checks | Done. All dimensions are sourced or provisional. |
| 2. Shell form | The massing has the proportions and the main forms of the reference | Done for now: centered screen on an apron, deck that ends behind the screen face, taper. 470 x 520 x 624 mm. The sight line is 23.8 degrees. |
| 3. Shell detail | Facets on the cheeks and the rear, blended hood corners, hood as an open arch, rear door, hand-holds | Not started. Needs a change of modelling method: solid operations at build time. |
| 4. Printable modules | The shell divided into parts for the 256 mm bed, with joints, inserts and ribs. Monitor cradle, compute module mount, power supply mount, control panel latch, bezel plate mount. | Not started |
| 5. Print checks | Each part sliced for the A1. Fit coupons for inserts, joints and button holes. | Not started |
| 6. Dry assembly and finish | As in the project brief, sections 4 and 5 | Not started |

## Next steps

1. Apply the measurements of the Mini New Astro City files and the panel research when they come.
2. Change the shell to solid modelling. Add the cheek facets, the rear facets and the blended hood corners. Make Blender renders from the angles of the reference photos.
3. Design the rear door with its vents, the hand-holds, and the shroud with its exhaust duct.
4. Design the control panel frame, its latch, and the cut plates. Make the drawings for the cutting service.

## Waiting for the owner

- [ ] Monitor: body width, height and thickness. Is it the flat model with no stand? Heights of the three ports on the left edge. Plug length with the bend, for the real cables.
- [ ] Player, seated as for play: eye height above the desk, and eye position in front of the cabinet front edge.
- [ ] BC-250 on the first console: how far the fan face is above the board, and where the shroud sits along the board. On the second board: the width and height of the fin block.
- [ ] Lever and buttons when they arrive: the dimensions that `cad/out/report.md` lists.
- [ ] The Mini New Astro City files from MakerWorld (model 700005). They need a login. The owner will get them. They are a different design from the reference cabinet, but they give real Astro City curves to measure.
- [ ] A photo of the reference cabinet from the side, if one exists.
- [ ] A look at the apron in the third pass (decision record 0003 is a proposal).

`cad/out/report.md` has the full list of dimensions to measure, with instructions.

## Open decisions

| Decision | Options | Depends on |
| --- | --- | --- |
| Fan shroud details | The air space between the fan and the fins (10 mm is the plan), the seal to the rear door, and the hood that turns the hot air to the door vents | A test print on the board |
| What the apron carries | Nothing. Or the start, coin and menu buttons, which lets the control panel be less deep. | Owner |
| Button nuts | Seimitsu nuts, snap-in buttons, or a layout spread by half a millimeter. Three pairs of Sanwa screw nuts overlap by 0.15 to 0.28 mm. | Owner |
| Marquee and speakers | No hardware is chosen. The hood band has provisional openings. | Owner |
| One encoder for each control panel | Research recommends it: one USB cable is then the only connection of a panel. | Owner |
| Control panel tops as cut plates | A mail-order service cuts the top plate of each control panel from a drawing that the model makes: a switch plate for the keyboard, and possibly one plate for the lever and buttons in place of two printed tiles. Open: material and thickness, and whether the arcade panel also gets one. | Research, then owner |
| The keyboard | 60%, built into the PC control panel by the owner. Open: the PCB (a standard hot-swap 60% board or hand wiring), the layout, and a pointing device beside it or none. | Owner |
| Front USB hardware | Open: the hub, panel-mount sockets or a hub without its shell, and powered or not. | Research |

## Settled by the owner

- The look follows the reference cabinet. Practical choices belong to this project (decision record 0002).
- Eight action buttons.
- The image is centered in the bezel. The sight line is in the 15 to 25 degree range.
- Bezel plates are swappable: 16:9, 16:10, 4:3 and vertical.
- Control panels are swappable. A control panel for PC games is wanted beside the arcade one. It holds a keyboard, and a mouse area if there is room.
- Four USB ports that the player can reach, for controllers: two USB-C and two USB-A, in the right side face of the deck toward the front, out of view. They go through a hub inside the cabinet.
- The PC control panel has a 60% keyboard that the owner builds.
- This is a personal project. The reference cabinet is the inspiration, and this design goes its own way.
- The speaker fronts follow the contour of the hood.
- Power supply: EVGA SuperNOVA 1000 P5, fully modular, 150 mm deep.
- Fan: ARCTIC P12 Pro on the BC-250 heatsink. The fin tops are opened under the fan, as on the first console. The shroud is a design for this cabinet: the fan blows down into the fins and the air leaves at the I/O end.
- All vents are in the rear door, as on the reference: the fan vent in the middle and slot vents for the hot air at the I/O end. The side panels have no vents.
- Control panel tops are cut plates. The arcade panel is an aluminum plate with a clear polycarbonate cover and the art between them.

## Where things are

| Path | Content |
| --- | --- |
| `docs/Arcade_Project_Current_Design_2026-11-09.md` | The project brief |
| `CONTEXT.md` | The glossary |
| `docs/adr/` | Decision records |
| `docs/research/` | Research notes: reference cabinets, hardware envelopes, controls and ergonomics |
| `cad/README.md` | How to build, check and view the model |
| `cad/params/` | All dimensions, with their status and source |
| `cad/out/report.md` | Check results and the list of dimensions to measure (a build output) |
| `cad/vendor/` | Reference photos and third-party CAD (not in git) |
