"""How the layout looks: one style per role for the line drawings and for the document's 3D view.

View settings live in view providers, which exist only when FreeCAD's GUI is
up. `apply`, `see_through` and `frame` therefore do nothing headless.
"""
from __future__ import annotations

from dataclasses import dataclass

import FreeCAD as App

Rgb = tuple[int, int, int]

SHELL_ROLES = ("massing", "trim")
SEE_THROUGH_TRANSPARENCY = 80


@dataclass(frozen=True)
class RoleStyle:
    """`line` is the stroke in the drawings. `surface` is the colour in the 3D view, where it differs."""

    label: str
    line: Rgb
    transparency: int = 0
    dashed: bool = False
    surface: Rgb | None = None

    @property
    def hex(self) -> str:
        return "#{:02x}{:02x}{:02x}".format(*self.line)

    @property
    def shape_colour(self) -> tuple[float, float, float]:
        red, green, blue = (channel / 255 for channel in self.surface or self.line)
        return (red, green, blue)


ROLE_STYLES: dict[str, RoleStyle] = {
    "massing": RoleStyle("Cabinet shell (massing)", (120, 126, 136), surface=(240, 240, 236)),
    "trim": RoleStyle("Bezel and hood trim", (20, 20, 24), surface=(26, 26, 30)),
    "keepout": RoleStyle("Keep-out zone", (168, 60, 200), transparency=85, dashed=True),
    "printable": RoleStyle("Printable part", (24, 138, 66)),
    "hardware": RoleStyle("Hardware", (28, 78, 160)),
    "protrusion": RoleStyle("Protrusion above the panel", (214, 78, 20)),
}


def apply(doc: App.Document) -> None:
    """Set the visibility, colour and transparency of every object from its role.

    Shown: assemblies, every tagged solid that is neither a keep-out nor an
    alternate, and the tip feature through which a PartDesign body is drawn.
    Hidden: everything else, which covers sketches, earlier features, origins
    and tool shapes. The shell is opaque, so it hides the hardware inside.
    """
    if not App.GuiUp:
        return
    tips = {obj.Tip.Name for obj in doc.Objects if obj.isDerivedFrom("PartDesign::Body") and obj.Tip}
    for obj in doc.Objects:
        role = getattr(obj, "CB_Role", "")
        on_show = role not in ("", "keepout") and not getattr(obj, "CB_Alternate", False)
        obj.ViewObject.Visibility = on_show or obj.isDerivedFrom("App::Part") or obj.Name in tips
        if role:
            obj.ViewObject.ShapeColor = ROLE_STYLES[role].shape_colour
            obj.ViewObject.Transparency = ROLE_STYLES[role].transparency
    # Changing a child's visibility marks its assembly as touched. No geometry
    # depends on visibility, so this recompute only clears those marks.
    doc.recompute()


def see_through(doc: App.Document, on: bool = True) -> None:
    """Make the shell and its trim translucent, to look at the hardware inside, or opaque again."""
    if not App.GuiUp:
        return
    for obj in doc.Objects:
        role = getattr(obj, "CB_Role", "")
        if role in SHELL_ROLES:
            obj.ViewObject.Transparency = SEE_THROUGH_TRANSPARENCY if on else ROLE_STYLES[role].transparency


def frame(doc: App.Document) -> None:
    """Point the document's 3D view at the whole visible layout, in FreeCAD's isometric view.

    That view looks from the player's front right, the same side as views/iso.png.
    """
    if not App.GuiUp:
        return
    view = App.Gui.getDocument(doc.Name).ActiveView
    animated = view.isAnimationEnabled()
    # An animated camera move needs a running event loop; a script run at start-up has none.
    view.setAnimationEnabled(False)
    view.viewIsometric()
    view.fitAll()
    view.setAnimationEnabled(animated)
