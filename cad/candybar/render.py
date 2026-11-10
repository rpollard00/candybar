from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
from xml.sax.saxutils import escape

import FreeCAD as App
import Part

from . import model, params
from .style import ROLE_STYLES

FOLDER = "views"
OUTPUTS = (FOLDER,)
LONG_SIDE = 1600
MARGIN = 40
HEADER = 120
LEGEND_WIDTH = 300
CURVE_DEFLECTION = 0.02
EDGE_KINDS = ("Sharp", "OutLine")
NOTE = "Each solid is drawn with its own hidden lines removed; solids do not hide each other."
BASE_CSS = (
    "path { fill: none; stroke-width: 1.6; stroke-linecap: round; stroke-linejoin: round; } "
    "text { font-family: sans-serif; fill: #222; }"
)

Polyline = list[tuple[float, float]]


@dataclass(frozen=True)
class View:
    """`eye` points from the layout toward the viewer; `up` is the direction drawn upward."""

    name: str
    caption: str
    eye: tuple[float, float, float]
    up: tuple[float, float, float]


VIEWS = (
    View("front", "Front, seen from the player's side", (0, -1, 0), (0, 0, 1)),
    View("right", "Right side, cabinet front on the left", (1, 0, 0), (0, 0, 1)),
    View("top", "Top, player at the bottom", (0, 0, 1), (0, 1, 0)),
    View("iso", "Isometric, from the player's right", (1, -1, 1), (0, 0, 1)),
)


def write(doc: App.Document, out_dir: Path) -> None:
    views_dir = out_dir / FOLDER
    views_dir.mkdir()
    solids = model.placed(doc)
    width, depth, height = (params.value(doc, name) for name in ("outer_w", "cab_d", "cab_h"))
    size = f"W x D x H = {width:.0f} x {depth:.0f} x {height:.0f} mm"
    for view in VIEWS:
        svg = views_dir / f"{view.name}.svg"
        svg.write_text(_svg(view, solids, size), encoding="utf-8")
        png = svg.with_suffix(".png")
        subprocess.run(["rsvg-convert", "--background-color", "white", "--output", str(png), str(svg)], check=True)


def _project(shape: Part.Shape, view: View) -> list[Polyline]:
    eye, up = App.Vector(*view.eye), App.Vector(*view.up)
    lines: list[Polyline] = []
    for kind in EDGE_KINDS:
        projected = shape.reflectLines(ViewDir=eye, ViewPos=App.Vector(), UpDir=up, EdgeType=kind, Visible=True, OnShape=False)
        for edge in projected.Edges:
            lines.append([(point.x, point.y) for point in edge.discretize(Deflection=CURVE_DEFLECTION)])
    return lines


def _svg(view: View, solids: Sequence[model.Placed], size: str) -> str:
    drawn = [(solid, _project(solid.world, view)) for solid in solids]
    xs = [x for _, lines in drawn for line in lines for x, _ in line]
    ys = [y for _, lines in drawn for line in lines for _, y in line]
    left, top = min(xs), max(ys)
    scale = (LONG_SIDE - 2 * MARGIN) / max(max(xs) - left, top - min(ys))
    width = round((max(xs) - left) * scale + 2 * MARGIN)
    height = round((top - min(ys)) * scale + 2 * MARGIN + HEADER)

    def pixel(x: float, y: float) -> str:
        return f"{MARGIN + (x - left) * scale:.1f},{HEADER + MARGIN + (top - y) * scale:.1f}"

    def path(lines: list[Polyline]) -> str:
        return " ".join("M" + " L".join(pixel(x, y) for x, y in line) for line in lines)

    paths = [
        f'<path id="{solid.name}" class="{role}" d="{path(lines)}"/>'
        for role in ROLE_STYLES
        for solid, lines in drawn
        if solid.role == role and lines
    ]
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            f"<style>{_css()}</style>",
            f'<rect width="{width}" height="{height}" fill="white"/>',
            *paths,
            *_header(view, size, width),
            "</svg>",
        ]
    )


def _css() -> str:
    rules = [BASE_CSS]
    for role, style in ROLE_STYLES.items():
        dash = " stroke-dasharray: 7 5;" if style.dashed else ""
        rules.append(f".{role} {{ stroke: {style.hex};{dash} }}")
    return " ".join(rules)


def _header(view: View, size: str, width: int) -> list[str]:
    legend_x = width - MARGIN - LEGEND_WIDTH
    lines = [
        f'<text x="{MARGIN}" y="44" font-size="26" font-weight="bold">{escape(view.caption)}</text>',
        f'<text x="{MARGIN}" y="76" font-size="20">{escape(size)}</text>',
        f'<text x="{MARGIN}" y="102" font-size="14">{escape(NOTE)}</text>',
    ]
    for row, (role, style) in enumerate(ROLE_STYLES.items()):
        y = 26 + row * 21
        lines.append(f'<path class="{role}" d="M{legend_x},{y} L{legend_x + 44},{y}" style="stroke-width: 3"/>')
        lines.append(f'<text x="{legend_x + 54}" y="{y + 5}" font-size="15">{escape(style.label)}</text>')
    return lines
