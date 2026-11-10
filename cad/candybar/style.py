"""How the layout looks: one palette per role for the line drawings, and the document's view settings.

View settings live in view providers, which exist only when FreeCAD's GUI is
up. `apply` and `frame` therefore do nothing headless.
"""
from __future__ import annotations

from dataclasses import dataclass

import FreeCAD as App


@dataclass(frozen=True)
class RoleStyle:
    label: str
    rgb: tuple[int, int, int]
    transparency: int
    dashed: bool

    @property
    def hex(self) -> str:
        return "#{:02x}{:02x}{:02x}".format(*self.rgb)

    @property
    def shape_colour(self) -> tuple[float, float, float]:
        red, green, blue = (channel / 255 for channel in self.rgb)
        return (red, green, blue)


# Listed back to front: the order the line drawings paint in.
ROLE_STYLES: dict[str, RoleStyle] = {
    "massing": RoleStyle("Shell massing (provisional)", (140, 146, 156), 75, False),
    "keepout": RoleStyle("Keep-out zone", (168, 60, 200), 85, True),
    "printable": RoleStyle("Printable part", (24, 138, 66), 0, False),
    "hardware": RoleStyle("Hardware", (28, 78, 160), 0, False),
    "protrusion": RoleStyle("Protrusion above the panel", (214, 78, 20), 0, False),
}


def apply(doc: App.Document) -> None:
    """Set the visibility, colour and transparency of every object from its role.

    Shown: assemblies, every tagged solid that is not a keep-out, and the tip
    feature through which a PartDesign body is drawn. Hidden: everything else,
    which covers keep-outs, sketches, earlier features, origins and tool shapes.
    """
    if not App.GuiUp:
        return
    tips = {obj.Tip.Name for obj in doc.Objects if obj.isDerivedFrom("PartDesign::Body") and obj.Tip}
    for obj in doc.Objects:
        role = getattr(obj, "CB_Role", "")
        obj.ViewObject.Visibility = obj.isDerivedFrom("App::Part") or obj.Name in tips or role not in ("", "keepout")
        if role:
            _colour(obj, ROLE_STYLES[role])
    # Changing a child's visibility marks its assembly as touched. No geometry
    # depends on visibility, so this recompute only clears those marks.
    doc.recompute()


def _colour(obj: App.DocumentObject, style: RoleStyle) -> None:
    features = [member for member in getattr(obj, "Group", ()) if member.isDerivedFrom("PartDesign::Feature")]
    for target in (obj, *features):
        target.ViewObject.ShapeColor = style.shape_colour
        target.ViewObject.Transparency = style.transparency


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
