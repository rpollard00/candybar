"""Draw the blueprint of the cabinet: the target's sheets from its profiles, and the reference sheets.

    cad/.venv-tools/bin/python cad/tools/draw_blueprint.py target      -> docs/blueprint/*.svg, *.png, faces.md
    cad/.venv-tools/bin/python cad/tools/draw_blueprint.py band-options -> cad/out/shell-bp/compare/hood-band-options.png
    cad/.venv-tools/bin/python cad/tools/draw_blueprint.py screen-drop-options -> cad/out/shell-bp/compare/screen-drop-options.png
    cad/.venv-tools/bin/python cad/tools/draw_blueprint.py fit         -> docs/blueprint/09-hardware.svg, .png (from candybar.shell.fit)
    cad/.venv-tools/bin/python cad/tools/draw_blueprint.py reference   -> cad/out/shell-d/reconstruction/k-*.png
    cad/.venv-tools/bin/python cad/tools/draw_blueprint.py photos      -> cad/out/shell-d/reconstruction/m-*.png, r-*.png
    cad/.venv-tools/bin/python cad/tools/draw_blueprint.py compare     -> cad/out/shell-d/sheet-side-profile.png
    cad/.venv-tools/bin/python cad/tools/draw_blueprint.py overlays    -> cad/out/shell-d/reconstruction/overlay-*.png

target draws from cad/candybar/shell/profiles.py and dims.Blueprint only (plus the hardware outlines of the
last build, cad/out/shell-d/3-short-band/overlay.json, when they exist). Every view is an orthographic
projection of the labelled faces, painted from the far side to the near side; every section is the cut of the
same faces with a plane. reference draws the 3D reference model (a mesh, third-party material) the same way,
with its triangles sorted into the same face IDs by rule, and writes only below cad/out.

Needs numpy and matplotlib (cad/.venv-tools).
"""
from __future__ import annotations

import colorsys
import json
import math
import os
import struct
import sys
from dataclasses import dataclass, replace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.collections import LineCollection, PolyCollection  # noqa: E402
from matplotlib.path import Path as MplPath  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(HERE)
REPO = os.path.dirname(CAD)
sys.path.insert(0, CAD)
from candybar.shell import profiles as pr  # noqa: E402
from candybar.shell.dims import MON_ACTIVE_H, Blueprint, Dims  # noqa: E402

OUT = os.path.join(REPO, "docs", "blueprint")
RECON = os.path.join(CAD, "out", "shell-d", "reconstruction")
INK, RED, BLUE = "#1c1c1f", "#b0302a", "#1f4e8c"
HUES = {"DK": 0.58, "CP": 0.75, "FB": 0.12, "RL": 0.33, "BZ": 0.0, "SC": 0.0, "RB": 0.08, "HC": 0.50, "MQ": 0.27, "HB": 0.92, "SP": 0.83, "LG": 0.42, "FL": 0.0}
GROUP = {"DK": "deck", "CP": "deck", "FB": "front body", "RL": "front body", "BZ": "front body", "SC": "front body", "RB": "rear body", "FL": "rear body",
         "HC": "hood", "MQ": "hood", "HB": "hood", "SP": "hood", "LG": "hood"}
GROUP_COLOUR = {"deck": "#8fb8de", "front body": "#f2d28a", "rear body": "#d9a48f", "hood": "#9fd6b8"}


def colour(face_id: str) -> tuple[float, float, float]:
    """A flat false colour for a face: the hue of its component, a lightness from its number."""
    k = int(face_id[2:])
    if face_id[:2] in ("BZ", "SC", "FL"):
        v = 0.25 + 0.12 * k
        return v, v, v + 0.05
    return colorsys.hls_to_rgb((HUES[face_id[:2]] + 0.017 * k) % 1.0, 0.48 + 0.27 * ((k * 5) % 7) / 7, 0.62)


@dataclass(frozen=True)
class View:
    name: str
    right: tuple[float, float, float]
    up: tuple[float, float, float]
    toward: tuple[float, float, float]


VIEWS = {"front": View("front elevation", (1, 0, 0), (0, 0, 1), (0, -1, 0)),
         "side": View("right side elevation", (0, 1, 0), (0, 0, 1), (1, 0, 0)),
         "top": View("top view", (1, 0, 0), (0, 1, 0), (0, 0, 1)),
         "rear": View("rear elevation", (-1, 0, 0), (0, 0, 1), (0, 1, 0))}


def dim(ax: Axes, p: tuple[float, float], q: tuple[float, float], text: str, shift: tuple[float, float] = (0.0, 0.0),
        size: float = 7.5, ha: str = "center", turn: float = 0.0, colour_: str = RED) -> None:
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="<->", color=colour_, lw=0.8, shrinkA=0, shrinkB=0), zorder=9000)
    ax.text((p[0] + q[0]) / 2 + shift[0], (p[1] + q[1]) / 2 + shift[1], text, color=colour_, fontsize=size, ha=ha, va="center", rotation=turn,
            zorder=9001, bbox=dict(fc="white", ec="none", pad=0.5, alpha=0.85))


def note(ax: Axes, at: tuple[float, float], text: str, to: tuple[float, float] | None = None, size: float = 7.5, ha: str = "left",
         colour_: str = BLUE) -> None:
    box = dict(fc="white", ec="none", pad=0.4, alpha=0.8)
    if to is None:
        ax.text(*at, text, color=colour_, fontsize=size, ha=ha, va="center", zorder=9001, bbox=box)
    else:
        ax.annotate(text, xy=to, xytext=at, color=colour_, fontsize=size, ha=ha, va="center", zorder=9001, bbox=box,
                    arrowprops=dict(arrowstyle="-", color=colour_, lw=0.6))


def tag(ax: Axes, at: tuple[float, float], text: str, to: tuple[float, float] | None = None, size: float = 6.5) -> None:
    """A face ID on a drawing, with a leader when it stands off the face."""
    box = dict(boxstyle="round,pad=0.15", fc="white", ec=INK, lw=0.5)
    if to is None:
        ax.text(*at, text, fontsize=size, ha="center", va="center", zorder=9500, bbox=box, color=INK, family="DejaVu Sans Mono")
    else:
        ax.annotate(text, xy=to, xytext=at, fontsize=size, ha="center", va="center", zorder=9500, bbox=box, color=INK, family="DejaVu Sans Mono",
                    arrowprops=dict(arrowstyle="-", color=INK, lw=0.5, shrinkA=0, shrinkB=0))


def project(points: np.ndarray, view: View) -> tuple[np.ndarray, np.ndarray]:
    r, u, t = (np.array(v, float) for v in (view.right, view.up, view.toward))
    return np.stack([points @ r, points @ u], axis=-1), points @ t


def paint(ax: Axes, faces: dict[str, pr.Face], view: View, fill: str, only: set[str] | None = None, lw: float = 0.55) -> dict[str, tuple[float, float]]:
    """Paint the faces from far to near; fill is 'white', 'colour' or 'group'. Returns where each visible face can carry its ID."""
    items = []
    for face in faces.values():
        if only is not None and face.id not in only:
            continue
        polys = [project(np.array(p, float), view) for p in face.polys]
        polys = [(xy, float(depth.mean())) for xy, depth in polys if abs(_area(xy)) > 1e-3]
        if not polys:
            continue
        near = max(k for _, k in polys)
        items += [(k, 0, face.id, xy) for xy, k in polys]
        items.append((near + 1e-3, 1, face.id, [project(np.array(e, float), view)[0] for e in face.edges]))
    items.sort(key=lambda it: (it[0], it[1]))
    ax.set_rasterization_zorder(8000.0)
    z = 10.0
    step = min(1.0, 7900.0 / max(len(items), 1))
    for key, kind, fid, data in items:
        z += step
        if kind == 0:
            c = "white" if fill == "white" else GROUP_COLOUR[GROUP[fid[:2]]] if fill == "group" else colour(fid)
            ax.add_collection(PolyCollection([data], facecolors=[c], edgecolors=[c], linewidths=0.5, zorder=z, antialiaseds=False))
        elif data:
            ax.add_collection(LineCollection(data, colors=INK, linewidths=lw, zorder=z))
    spots: dict[str, tuple[float, float]] = {}
    covers = [(key, MplPath(xy)) for key, kind, _, xy in items if kind == 0]
    cover_depth = np.array([k for k, _ in covers])
    cover_box = np.array([[*xy.min(axis=0), *xy.max(axis=0)] for key, kind, _, xy in items if kind == 0]).reshape(-1, 4)
    probes = np.array([[0.0, 0.0], [0.4, 0.3], [-0.3, 0.4], [0.3, -0.4]])

    def covered(c: np.ndarray, k: float) -> bool:
        """Whether a nearer polygon covers the point c: only those whose box holds it are tested."""
        near = np.nonzero((cover_depth > k + 0.5) & (cover_box[:, 0] <= c[0] + 0.5) & (cover_box[:, 2] >= c[0] - 0.5)
                          & (cover_box[:, 1] <= c[1] + 0.5) & (cover_box[:, 3] >= c[1] - 0.5))[0]
        return any(covers[i][1].contains_points(c + probes).any() for i in near)
    for face in faces.values():
        if only is not None and face.id not in only:
            continue
        seen = []
        for p in face.polys:
            pts = np.array(p, float)
            if pts[:, 0].mean() < -1.0:
                continue
            xy, depth = project(pts, view)
            area, c, k = abs(_area(xy)), xy.mean(axis=0), float(depth.mean())
            if area > 4.0 and not covered(c, k):
                seen.append((area, c, MplPath(xy)))
        if not seen:
            continue
        mean = sum(a * c for a, c, _ in seen) / sum(a for a, _, _ in seen)
        inside = any(path.contains_point(mean) for _, _, path in seen)
        best = mean if inside else max(seen, key=lambda t: t[0])[1]
        spots[face.id] = (float(best[0]), float(best[1]))
    ax.set_aspect("equal")
    ax.autoscale_view()
    return spots


def _area(xy: np.ndarray) -> float:
    x, y = xy[:, 0], xy[:, 1]
    return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def cut(faces: dict[str, pr.Face], axis: int, at: float) -> dict[str, list[np.ndarray]]:
    """The cut of every face with the plane axis = at: for each face, segments in the two other coordinates."""
    keep = [i for i in range(3) if i != axis]
    out: dict[str, list[np.ndarray]] = {}
    for face in faces.values():
        for p in face.polys:
            pts = np.array(p, float)
            side = pts[:, axis] - at
            hits = []
            for i in range(len(pts)):
                a, b = i, (i + 1) % len(pts)
                if (side[a] > 0) != (side[b] > 0):
                    k = side[a] / (side[a] - side[b])
                    hits.append(pts[a] + k * (pts[b] - pts[a]))
            if len(hits) >= 2:
                out.setdefault(face.id, []).append(np.array([hits[0][keep], hits[1][keep]]))
    return out


def draw_cut(ax: Axes, segs: dict[str, list[np.ndarray]], flip: bool = False, lw: float = 1.3, coloured: bool = True) -> None:
    for fid, lines in segs.items():
        data = [l[:, ::-1] if flip else l for l in lines]
        ax.add_collection(LineCollection(data, colors=[colour(fid)] if coloured else INK, linewidths=lw, zorder=50, capstyle="round"))
    ax.set_aspect("equal")


def tag_cut(ax: Axes, segs: dict[str, list[np.ndarray]], window: tuple[float, float, float, float], off: float = 9.0, flip: bool = False,
            place: dict[str, tuple[float, float]] | None = None, skip: set[str] | None = None) -> None:
    """Put the ID of every face that the cut shows inside the window beside its longest piece there."""
    x0, x1, y0, y1 = window
    for fid, lines in segs.items():
        if skip and fid in skip:
            continue
        best = None
        for l in lines:
            l = l[:, ::-1] if flip else l
            m = l.mean(axis=0)
            if x0 <= m[0] <= x1 and y0 <= m[1] <= y1:
                length = float(np.linalg.norm(l[1] - l[0]))
                run = sum(float(np.linalg.norm(o[1] - o[0])) for o in lines)
                if best is None or length > best[0]:
                    best = (length, m, l[1] - l[0], run)
        if best is None:
            continue
        _, m, v, _ = best
        n = np.array([-v[1], v[0]]) / (np.linalg.norm(v) + 1e-9)
        centre = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
        if np.dot(n, m - centre) < 0:
            n = -n
        at = tuple(place[fid]) if place and fid in place else tuple(m + off * n)
        tag(ax, at, fid, to=(float(m[0]), float(m[1])))


def frame(ax: Axes, title: str, xlim: tuple[float, float], ylim: tuple[float, float], xlabel: str = "", ylabel: str = "", grid: bool = True) -> None:
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=9.5)
    ax.tick_params(labelsize=6.5)
    ax.set_xlabel(xlabel, fontsize=7.5)
    ax.set_ylabel(ylabel, fontsize=7.5)
    if grid:
        ax.grid(True, color="#ececec", lw=0.4, zorder=0)


def save(fig: plt.Figure, name: str, out: str = OUT, svg: bool = True) -> None:
    os.makedirs(out, exist_ok=True)
    fig.savefig(os.path.join(out, name + ".png"), dpi=130, bbox_inches="tight")
    if svg:
        fig.savefig(os.path.join(out, name + ".svg"), bbox_inches="tight", dpi=220)
    plt.close(fig)
    print("draw_blueprint:", os.path.relpath(os.path.join(out, name + ".png"), REPO))


def hardware() -> list[dict]:
    path = os.path.join(CAD, "out", "shell-d", "3-short-band", "overlay.json")
    return json.load(open(path)) if os.path.exists(path) else []


def hardware_of(d: Blueprint) -> list[dict]:
    """The hardware of the last build, with the monitor moved square to the screen to the blueprint's screen plane."""
    su, cu = d.u
    move = Dims().mon_setback - d.mon_setback
    out = []
    for item in hardware():
        corners = np.array(item["corners"], float)
        if item["name"].startswith("Monitor"):
            corners += (0.0, -move * cu, move * su)
        out.append({**item, "corners": corners})
    return out


def draw_hardware(ax: Axes, view: View, d: Blueprint, names: tuple[str, ...] = ("Monitor_Body", "PSU_Body", "Compute_")) -> None:
    for item in hardware_of(d):
        if not item["name"].startswith(names):
            continue
        xy, _ = project(item["corners"], view)
        hull = _hull(xy)
        ax.plot(*np.vstack([hull, hull[:1]]).T, color=item["colour"], lw=0.9, ls="--", zorder=8500)


def _hull(p: np.ndarray) -> np.ndarray:
    pts = sorted(set(map(tuple, p.round(3))))

    def half(seq: list) -> list:
        out: list = []
        for q in seq:
            while len(out) >= 2 and (out[-1][0] - out[-2][0]) * (q[1] - out[-2][1]) - (out[-1][1] - out[-2][1]) * (q[0] - out[-2][0]) <= 0:
                out.pop()
            out.append(q)
        return out
    lower, upper = half(pts), half(list(reversed(pts)))
    return np.array(lower[:-1] + upper[:-1])


# ---------- the target ----------

PROPORTIONS = [
    # quantity, 3D model (exact), maker's mini, real cabinet, why this cabinet differs
    ("Body width W, mm", "270.0", "246.9 +-2.4 (measured)", "750 (published)", "{width:.1f}",
     "16-inch 16:10 monitor (354 wide) with its cradle, between two rails"),
    ("Deck width / W", "1.000", "1.02 +-0.03 (measured)", "about 1.0", "1.000", "same: the deck's side is flush with the side band"),
    ("Depth / W", "1.252", "about 1.3 (estimated)", "1.207 (published)", "{depth_r:.3f}",
     "540 at the desk holds the power supply and the BC-250; the upper rear is 40 proud for the hood"),
    ("Height / W", "1.172", "about 1.25 (estimated)", "1.927 (floor cabinet)", "{height_r:.3f}", "a 16:10 screen is lower than 4:3 at the same width"),
    ("Deck top above the desk / W", "0.185", "about 0.2 (estimated)", "not comparable", "{deck_r:.3f}", "70 mm panel height for the hands; 58 inside is enough for the lever"),
    ("Deck front to screen foot / W", "0.380", "about 0.42 (estimated)", "0.49 (estimated)", "{foot_r:.3f}", "396 x 175 control panel (166.4 deep at the sides, the front follows the deck) with its border"),
    ("Recline of the screen and of the rail's chord, deg", "32.5", "about 30 (estimated)", "26 (estimated)", "{recline:.0f}", "owner's choice for the 16:10 bezel"),
    ("Rail arc in side view, sagitta / chord", "0.091 (one arc, R 1.154 W)", "0.000 +-0.002 (measured: straight)", "not measured (+-0.03)", "{rail_k:.3f}",
     "a subtle arc between the maker's straight rail and the 3D model's strong one; sagitta {rail_s:.1f}, turn {rail_turn:.0f} deg"),
    ("Body side below the tuck", "vertical, flat", "straight (measured); its lean is not measurable", "straight (measured); its lean is not measurable", "vertical, flat",
     "same as the 3D model"),
    ("Body side bow (widest at mid height) / W", "0.000", "0.000 +-0.004 (measured)", "0.000 +-0.003 (measured)", "{bow:.3f}", "same: no bow"),
    ("Body tuck toward the hood, each side at the seam / W", "0.000 (the hood leans 13.5 deg from the seam)", "0.010 +-0.006 (measured)", "0.018 +-0.006 (measured, an upper limit)", "{tuck:.3f}",
     "owner's choice: more than both, over the top third; starts at {tuck_from:.3f} of the body height, {tuck_lean:.1f} deg at the seam"),
    ("Hood crown across the width / W", "0.000", "0.000 +-0.005 (measured)", "0.000 +-0.001 (measured)", "{crown:.3f}", "same: the hood top is straight across"),
    ("Seam (body top) above the desk / W", "0.916", "0.88 (estimated)", "not comparable", "{seam_r:.3f}", "follows from the bezel: 215 image + 2 x 45 frame + {apron:.0f} apron + {brow:.0f} brow"),
    ("Hood height over the seam / W", "0.256", "0.33 (0.35 to bezel top)", "0.25 to 0.33 (0.36 to bezel top)", "{hood_r:.3f}", "{hood_bezel_r:.3f} to the bezel top; a flat top below the top of the rear arc"),
    ("Hood depth at the seam / W", "0.335", "0.28 (estimated)", "0.30 (estimated)", "{hood_d_r:.3f}", "needs the upper rear 40 proud; the front foot stands on the line of the rail"),
    ("Screen inset below the rail land at mid height / W", "0.096 (cheek 25.9 proud)", "about 0.05 (estimated)", "deep (CRT)", "{inset_r:.3f}",
     "flat screen {setback:.1f} behind the chord; {depth_top:.1f} below the land at the window top"),
    ("Bezel width / W", "0.885", "0.858 +-0.016 (measured)", "about 0.79", "{bezel_r:.3f}", "344.7 image + 2 x 45 frame"),
    ("Rail land / W", "0.016", "0.05 +-0.015 (estimated)", "not read", "{land_r:.3f}", "what the bezel leaves, less the edge section; {land_top:.1f} at the bezel top (the tuck)"),
    ("Rail edge, in x back / W", "0.039 x 0.039 (45 deg facet)", "0.03 x 0.12 (band 10 to 18 deg)", "not read", "{edge_in_r:.3f} x {edge_back_r:.3f}",
     "the deck's own edge section (10 deg band), so the edge follows through"),
    ("Side band depth at the desk / W", "0.277", "0.27 (estimated)", "not read", "{band_r:.3f}", "follows both references; the built model has 0.35"),
    ("Rear body narrower, each side / W", "0.074", "0.01 to 0.03 (uncertain)", "not read", "{step_r:.3f}", "a shallow step behind the side band"),
    ("Hood foot width / W", "0.990", "0.94 to 0.96 (measured)", "0.95 (measured)", "{hood_foot_r:.3f}", "the outline of the body top: no shoulder, a groove at the seam"),
    ("Hood side lean, seam to top corner, deg", "13.5 to 22 (one arc)", "about 6, then one long blend (estimated)", "11 to 19 (measured +-3)",
     "{lean0:.1f} to {lean1:.1f}", "tangent to the tuck, then near straight (R {side_r:.1f} W), as on the real cabinet"),
    ("Hood top corner radius / W", "0.074", "none: one long blend (estimated)", "0.06 to 0.07 (measured, left)", "{corner_r:.3f}",
     "the real cabinet's tight corner"),
    ("Hood top flat / W", "0.713", "0.66 (estimated)", "about 0.68 (estimated, owner-ref-1)", "{top_flat_r:.3f}",
     "follows from the side and the corner; straight marquee window {mq:.0f}"),
]


def panel_text(d: Blueprint) -> str:
    """The size of the control panel: its depth at the centre line and at the sides (the front follows the deck)."""
    o = pr.panel_outline(d)
    return f"control panel {d.panel_w:.0f} x {o[-1][1] - o[1][1]:.0f}, {o[-1][1] - o[0][1]:.1f} at the sides"


def proportions(d: Blueprint) -> list[tuple[str, str, str, str, str, str]]:
    h = pr.hood(d)
    fr = pr.front(d)
    w = d.width
    v = dict(width=w, depth_r=d.depth / w, height_r=(h.origin[2] + h.height) / w, apron=d.band_len, brow=d.brow_ledge,
             hood_bezel_r=(h.origin[2] + h.height - d.face(d.bezel_s1)[1]) / w, deck_r=d.deck_top / w, foot_r=d.foot_y / w, recline=d.recline,
             seam_r=d.body_top / w, hood_r=(h.origin[2] + h.height - d.body_top) / w, hood_d_r=h.depth / w, bezel_r=d.bezel_w / w, land_r=d.rail_land / w,
             edge_in_r=d.edge_in / w, edge_back_r=d.deck_lean_h / w, step_r=(w - d.rear_w) / 2 / w, band_r=(d.step_y0 - d.foot_y + d.bend_t) / w,
             hood_foot_r=2 * h.half_base / w, top_flat_r=2 * h.half_top / w, rail_k=d.rail_sagitta_ratio, rail_s=fr.sagitta, rail_turn=d.rail_turn,
             bow=d.body_bow_ratio, tuck=d.body_tuck_ratio, tuck_from=d.body_tuck_from, tuck_lean=d.tuck_lean, crown=d.hood_crown_ratio,
             inset_r=(d.mon_setback + fr.rise(d, d.image_s)) / w, setback=d.mon_setback, depth_top=d.mon_setback + fr.rise(d, d.image_s + MON_ACTIVE_H / 2),
             land_top=d.side_x(fr.on_rail(d, d.bezel_s1)[1]) - d.edge_in - d.bezel_w / 2 - d.panel_gap,
             lean0=d.tuck_lean, lean1=d.tuck_lean + d.hood_side_turn, side_r=h.side_arc.r / w if isinstance(h.side_arc, pr.Arc) else math.inf,
             corner_r=d.hood_corner_ratio, mq=pr.marquee_window(d, h)[0])
    return [(q, k, m, r, t.format(**v), why.format(**v)) for q, k, m, r, t, why in PROPORTIONS]


def sheet_elevations(d: Blueprint, faces: dict[str, pr.Face]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(17, 15))
    w, hw, top = d.width, d.width / 2, d.body_top + d.hood_h
    h = pr.hood(d)
    tri, ids = triangles_of(faces)
    lim = {"front": (-320, 320, -70, 660), "side": (-90, 700, -70, 660), "top": (-320, 320, -70, 660), "rear": (-320, 320, -70, 660)}
    for ax, key in zip(axes.ravel(), ("front", "side", "top", "rear")):
        show(ax, raster(tri, ids, VIEWS[key], lim[key], closed=False), "white", VIEWS[key].name.capitalize())
    a = axes[0, 0]
    dim(a, (-hw, -30), (hw, -30), f"width {w:.1f}", (0, -12))
    dim(a, (-h.half_base, top + 16), (h.half_base, top + 16), f"hood foot {2 * h.half_base:.1f}", (0, 11))
    dim(a, (-h.half_top, top + 42), (h.half_top, top + 42), f"top flat {2 * h.half_top:.1f}", (0, 11))
    dim(a, (hw + 22, 0), (hw + 22, d.deck_top), f"{d.deck_top:.0f}", (14, 0))
    dim(a, (hw + 22, d.deck_top), (hw + 22, d.body_top), f"{d.body_top - d.deck_top:.1f}", (20, 0))
    dim(a, (hw + 22, d.body_top), (hw + 22, top), f"{d.hood_h:.1f}", (20, 0))
    dim(a, (-hw - 26, 0), (-hw - 26, top), f"height {top:.1f}", (-10, 0), turn=90)
    dim(a, (-d.bezel_w / 2, 250), (d.bezel_w / 2, 250), f"bezel {d.bezel_w:.1f}", (0, -13))
    a = axes[0, 1]
    dim(a, (0, -30), (d.depth, -30), f"depth {d.depth:.0f}", (0, -12))
    dim(a, (0, -52), (d.body_d, -52), f"at the desk {d.body_d:.0f}", (0, -11))
    dim(a, (0, top + 14), (d.foot_y - d.bend_t, top + 14), f"deck {d.foot_y - d.bend_t:.0f}", (0, 11))
    dim(a, (d.seam_y, top + 14), (d.depth, top + 14), f"body top {d.depth - d.seam_y:.0f}", (0, 11))
    dim(a, (h.origin[1], top + 40), (h.origin[1] + h.depth, top + 40), f"hood {h.depth:.0f}", (0, 11))
    dim(a, (-28, 0), (-28, d.deck_top), f"{d.deck_top:.0f}", (-14, 0))
    dim(a, (-28, d.deck_top), (-28, d.body_top), f"seam {d.body_top:.1f}", (-12, 0), turn=90)
    dim(a, (-28, d.body_top), (-28, top), f"{d.hood_h:.1f}", (-20, 0))
    dim(a, (d.depth + 30, 0), (d.depth + 30, top), f"height {top:.1f}", (12, 0), turn=90)
    y, z = pr.front(d).on_rail(d, (d.bezel_s0 + d.bezel_s1) / 2)
    note(a, (y - 190, z + 40), f"rail: a convex arc, chord reclined {d.recline:.0f} deg", to=(y - 6, z))
    note(a, (385, 345), f"upper rear {d.rear_proud:.0f} proud", to=(d.depth - 1, d.rear_step_z1 + 12))
    a = axes[1, 0]
    dim(a, (-hw, -30), (hw, -30), f"{w:.1f}", (0, -12))
    dim(a, (-d.rear_w / 2, d.depth + 55), (d.rear_w / 2, d.depth + 55), f"rear body {d.rear_w:.0f}", (0, 11))
    dim(a, (hw + 24, 0), (hw + 24, d.depth), f"{d.depth:.0f}", (12, 0), turn=90)
    dim(a, (-hw - 24, 0), (-hw - 24, d.foot_y - d.bend_t), f"{d.foot_y - d.bend_t:.0f}", (-16, 0))
    dim(a, (-d.panel_w / 2, 113), (d.panel_w / 2, 113), panel_text(d), (0, 12))
    a = axes[1, 1]
    dim(a, (-hw, -30), (hw, -30), f"{w:.1f}", (0, -12))
    dim(a, (-d.rear_w / 2, -52), (d.rear_w / 2, -52), f"rear body {d.rear_w:.0f}", (0, -11))
    dim(a, (hw + 22, 0), (hw + 22, d.rear_step_z0), f"{d.rear_step_z0:.0f}", (16, 0))
    dim(a, (hw + 22, d.rear_step_z1), (hw + 22, d.body_top), f"{d.body_top - d.rear_step_z1:.1f}", (18, 0))
    fig.suptitle("Blueprint 02: elevations of the target, one scale (mm)", fontsize=14, y=0.995)
    fig.tight_layout()
    save(fig, "02-elevations")


SKIP_ON_MAP = {"BZ3", "SP3", "LG3", "FL1"}
FACE_SPOTS: dict[str, dict[str, tuple[float, ...] | None]] = {
    "front": {"RL1": (292, 330), "RL2": (292, 300), "RL3": (292, 270), "DK2": (292, 80), "DK3": (292, 55), "DK6": (292, 25), "HC1": (292, 470), "HC4": (292, 560),
              "HC13": (-292, 524), "MQ1": (-292, 548), "HB1": (-292, 470), "SP1": (-292, 497), "LG1": (-292, 446), "HC3": (-292, 428), "FB3": (-292, 410), "BZ2": (-292, 375),
              "HC2": (-292, 575), "FB1": (-292, 85), "FB4": (-292, 395)},
    "side": {"RL2": (285, 470), "RL3": (320, 440), "DK2": (40, 115), "DK3": (95, 115), "DK5": (-45, 20), "DK6": (-45, 45), "HC4": (400, 545), "RB2": (640, 120)},
    "top": {"RL1": (292, 350), "RL2": (292, 320), "RL3": (292, 290), "DK2": (292, 130), "DK3": (292, 100), "HC7": (-292, 478), "HC4": (-292, 452), "HC6": (292, 500),
            "HC5": (292, 530), "FB4": (292, 562), "FB3": (-292, 432), "BZ2": (-292, 395), "BZ1": (-292, 375), "FB1": (-292, 222), "DK1": (-292, 190),
            "RL4": None, "RB2": None},
    "rear": {"RB2": (-292, 150), "RL4": (-292, 250), "RB3": (0, 50, 0, 75), "HC1": None, "HC4": None, "HC5": None, "HC6": None}}


def sheet_face_map(d: Blueprint, faces: dict[str, pr.Face]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(18, 16))
    lim = {"front": ((-330, 330), (-40, 640)), "side": ((-70, 680), (-40, 640)), "top": ((-330, 330), (-40, 640)), "rear": ((-330, 330), (-40, 640))}
    for ax, key in zip(axes.ravel(), ("front", "side", "top", "rear")):
        spots = paint(ax, faces, VIEWS[key], "colour")
        frame(ax, VIEWS[key].name.capitalize(), *lim[key], grid=False)
        ax.axis("off")
        ax.set_title(VIEWS[key].name.capitalize(), fontsize=11)
        placed = FACE_SPOTS.get(key, {})
        for fid, at in spots.items():
            if fid in SKIP_ON_MAP:
                continue
            if fid in placed:
                if placed[fid] is None:
                    continue
                to = (-at[0], at[1]) if placed[fid][0] < 0 < at[0] and key != "side" else at
                tag(ax, placed[fid][:2], fid, to=placed[fid][2:] or to)
            else:
                tag(ax, at, fid)
    fig.suptitle("Blueprint 07: face map of the target (flat false colours; the IDs are those of the table in index.md)", fontsize=14, y=0.995)
    fig.tight_layout()
    save(fig, "07-face-map")


def sheet_volumes(d: Blueprint, faces: dict[str, pr.Face]) -> None:
    fig = plt.figure(figsize=(20, 14.5))
    grid = fig.add_gridspec(2, 3, height_ratios=[1.45, 1.0], hspace=0.02, wspace=0.02, top=0.95, bottom=0.02, left=0.02, right=0.98)
    w, hw, top = d.width, d.width / 2, d.body_top + d.hood_h
    h = pr.hood(d)
    r = lambda v: f"{v:.0f} ({v / w:.2f} W)"
    lim = {"front": ((-400, 400), (-95, 665)), "side": ((-110, 690), (-95, 665)), "top": ((-400, 400), (-95, 665))}
    axes = {}
    for i, key in enumerate(("front", "side", "top")):
        ax = fig.add_subplot(grid[0, i])
        paint(ax, faces, VIEWS[key], "group", lw=0.35)
        draw_hardware(ax, VIEWS[key], d)
        frame(ax, VIEWS[key].name.capitalize(), *lim[key], grid=False)
        ax.axis("off")
        ax.set_title(VIEWS[key].name.capitalize(), fontsize=11)
        axes[key] = ax
    a = axes["front"]
    dim(a, (-hw, -28), (hw, -28), f"body width W = {w:.1f}", (0, -13))
    dim(a, (-h.half_base, top + 16), (h.half_base, top + 16), "hood foot " + r(2 * h.half_base), (0, 12))
    dim(a, (hw + 20, 0), (hw + 20, d.deck_top), r(d.deck_top), (0, -48), ha="center")
    dim(a, (hw + 20, d.deck_top), (hw + 20, d.body_top), r(d.body_top - d.deck_top), (12, 0), turn=90)
    dim(a, (hw + 20, d.body_top), (hw + 20, top), r(d.hood_h), (12, 0), turn=90)
    dim(a, (-hw - 22, 0), (-hw - 22, top), "height " + r(top), (-12, 0), turn=90)
    note(a, (-60, 36), "DECK", colour_=INK, size=9)
    note(a, (-90, 110), "FRONT BODY", colour_=INK, size=9)
    note(a, (-40, 500), "HOOD", colour_=INK, size=9)
    a = axes["side"]
    dim(a, (0, -28), (d.depth, -28), "depth " + r(d.depth), (0, -13))
    dim(a, (0, -58), (d.body_d, -58), "at the desk " + r(d.body_d), (0, -13))
    dim(a, (0, top + 16), (d.foot_y, top + 16), "deck front to screen foot " + r(d.foot_y), (30, 12))
    dim(a, (h.origin[1], top + 44), (h.origin[1] + h.depth, top + 44), "hood " + r(h.depth), (0, 12))
    dim(a, (d.depth + 26, d.body_top), (d.depth + 26, top), r(d.hood_h), (12, 0), turn=90)
    dim(a, (-30, 0), (-30, d.body_top), "seam " + r(d.body_top), (-12, 0), turn=90)
    note(a, (60, 36), "DECK", colour_=INK, size=9)
    note(a, (330, 150), "FRONT BODY", colour_=INK, size=9)
    note(a, (450, 60), "REAR BODY", colour_=INK, size=9)
    note(a, (470, 500), "HOOD", colour_=INK, size=9)
    y, z = pr.front(d).on_rail(d, d.image_s)
    note(a, (60, 330), f"rail: a convex arc, chord reclined {d.recline:.0f} deg", to=(y - 8, z))
    a = axes["top"]
    dim(a, (-d.rear_w / 2, d.depth + 22), (d.rear_w / 2, d.depth + 22), "rear body " + r(d.rear_w), (0, 12))
    dim(a, (hw + 22, 0), (hw + 22, d.foot_y - d.bend_t), "deck " + r(d.foot_y - d.bend_t), (12, 0), turn=90)
    dim(a, (hw + 22, d.seam_y), (hw + 22, d.depth), "body top " + r(d.depth - d.seam_y), (12, 0), turn=90)
    dim(a, (-d.panel_w / 2, 113), (d.panel_w / 2, 113), panel_text(d), (0, 12))
    for ax in axes.values():
        ax.plot([], [], color="#1f77d0", ls="--", lw=0.9, label="monitor 354 x 230 x 10")
        ax.plot([], [], color="#d62728", ls="--", lw=0.9, label="power supply")
        ax.plot([], [], color="#2ca02c", ls="--", lw=0.9, label="BC-250 module")
    for name, c in GROUP_COLOUR.items():
        axes["front"].fill([], [], fc=c, ec=INK, lw=0.4, label=name)
    handles, labels = axes["front"].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.455), ncol=7, fontsize=8.5, frameon=False)
    t = fig.add_subplot(grid[1, :])
    t.axis("off")
    rows = proportions(d)
    table = t.table(cellText=[list(row) for row in rows], cellLoc="left", loc="upper center",
                    colLabels=["Ratio to the body width W", "3D reference model (exact)", "maker's mini (photos)", "real New Astro City", "this cabinet", "why it differs"],
                    colWidths=[0.17, 0.13, 0.14, 0.14, 0.08, 0.34])
    table.auto_set_font_size(False)
    table.set_fontsize(7.5)
    table.scale(1.0, 1.45)
    for (row, col), cell in table.get_celld().items():
        cell.set_linewidth(0.3)
        if row == 0:
            cell.set_facecolor("#e8e8ec")
            cell.set_text_props(weight="bold")
        elif col == 4:
            cell.set_facecolor("#eef6ee")
    fig.suptitle("Blueprint 01: the big volumes of the target, with the hardware inside (dashed) and the proportions beside the references", fontsize=14, y=0.985)
    save(fig, "01-volumes")


def sheet_side_section(d: Blueprint, faces: dict[str, pr.Face]) -> None:
    fig = plt.figure(figsize=(19, 12.8))
    grid = fig.add_gridspec(1, 2, width_ratios=[2.6, 1.0], wspace=0.08, top=0.93, bottom=0.05, left=0.04, right=0.98)
    ax = fig.add_subplot(grid[0, 0])
    segs = cut(faces, 0, 0.01)
    draw_cut(ax, segs, lw=1.6)
    draw_hardware(ax, VIEWS["side"], d)
    top = d.body_top + d.hood_h
    h = pr.hood(d)
    frame(ax, "Side section at the centre line (the outer skin; each line in the colour of its face)", (-95, 700), (-70, 690), "y, from the deck front (mm)", "z, above the desk (mm)")
    place = {"DK1": (20, 105), "CP1": (115, 100), "FB1": (190, 110), "FB2": (300, 120), "BZ1": (330, 150), "BZ2": (400, 185), "SC1": (430, 215), "BZ3": (360, 168), "FB3": (385, 440),
             "FB4": (520, 400), "RB5": (630, 395), "RB4": (625, 322), "RB3": (585, 150), "RB6": (585, 215), "DK3": (-45, 58), "DK2": (-45, 80), "DK4": (-45, 25),
             "HC3": (370, 450), "HC12": (370, 465), "HB1": (370, 480), "LG1": (370, 495), "LG2": (370, 510), "HC13": (370, 525), "MQ1": (370, 540), "MQ2": (370, 555),
             "HC10": (370, 570), "HC2": (370, 585), "HC4": (400, 600), "HC7": (505, 602), "HC8": (610, 585), "HC9": (630, 470)}
    tag_cut(ax, segs, (-95, 700, -70, 660), place=place)
    dim(ax, (0, -28), (d.body_d, -28), f"{d.body_d:.0f} at the desk", (0, -11))
    dim(ax, (0, -52), (d.depth, -52), f"depth {d.depth:.0f}", (0, -11))
    dim(ax, (d.body_d, 20), (d.depth, 20), f"{d.rear_proud:.0f}", (0, 10))
    ya = d.foot_y - d.bend_t
    dim(ax, (0, top + 36), (ya, top + 36), f"deck {ya:.1f}", (0, 10))
    dim(ax, (ya, top + 36), (d.foot_y, top + 36), f"{d.bend_t:.1f}", (0, 10))
    dim(ax, (d.foot_y, top + 36), (d.seam_y, top + 36), f"screen face runs back {d.seam_y - d.foot_y:.1f}", (0, 10))
    dim(ax, (d.seam_y, top + 36), (d.depth, top + 36), f"body top {d.depth - d.seam_y:.1f}", (0, 10))
    dim(ax, (h.origin[1], top + 66), (h.origin[1] + h.depth, top + 66), f"hood {h.depth:.1f}", (0, 10))
    dim(ax, (-62, 0), (-62, d.deck_top), f"{d.deck_top:.0f}", (-12, 0))
    dim(ax, (-62, d.deck_top), (-62, d.body_top), f"body top {d.body_top:.1f}", (-9, 0), turn=90)
    dim(ax, (-62, d.body_top), (-62, top), f"hood {d.hood_h:.1f}", (-9, 0), turn=90)
    dim(ax, (d.depth + 52, 0), (d.depth + 52, top), f"height {top:.1f}", (9, 0), turn=90)
    dim(ax, (d.depth + 22, 0), (d.depth + 22, d.rear_step_z0), f"{d.rear_step_z0:.0f}", (10, 0), turn=90)
    dim(ax, (d.depth + 22, d.rear_step_z1), (d.depth + 22, d.body_top), f"{d.body_top - d.rear_step_z1:.1f}", (10, 0), turn=90)
    for s0, s1, text in ((d.bend_t, d.bezel_s0, f"apron {d.band_len:.0f}"), (d.bezel_s0, d.bezel_s1, f"bezel {d.bezel_len:.1f}"), (d.bezel_s1, d.top_s, f"{d.brow_ledge:.0f}")):
        (y0, z0), (y1, z1) = d.face(s0), d.face(s1)
        o = (-34 * d.u[1], 34 * d.u[0])
        dim(ax, (y0 + o[0], z0 + o[1]), (y1 + o[0], z1 + o[1]), text, (-14 * d.u[1], 14 * d.u[0]), turn=90 - d.recline)
    fr = pr.front(d)
    rail = np.array([(y, z) for y, z, _ in fr.chain()])
    ax.plot(rail[:, 0], rail[:, 1], color=INK, lw=0.9, zorder=40)
    p0, p1 = fr.rail.at(fr.rail.a0), fr.rail.at(fr.rail.a1)
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=INK, lw=0.6, ls="--", zorder=40)
    pm = fr.rail.at((fr.rail.a0 + fr.rail.a1) / 2)
    cm = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    dim(ax, cm, pm, "", size=7)
    note(ax, (40, 330), f"RL1, the rail land at the sides (black line): one arc,\nsagitta {fr.sagitta:.1f} = {d.rail_sagitta_ratio:.3f} of its chord {fr.chord:.1f} (dashed),\nR {fr.rail.r:.0f} = {fr.rail.r / d.width:.2f} W, turning {d.rail_turn:.0f} deg", to=pm)
    note(ax, (40, 262), f"chord and flat screen reclined {fr.recline:.0f} deg; the rail leans\n{fr.foot_lean:.0f} deg at its foot and {fr.top_lean:.0f} deg at the seam; sweep R {d.bend_r:.0f}", to=(p0[0] - 4, p0[1] - 6))
    note(ax, (40, 575), f"screen {d.mon_setback + fr.rise(d, d.image_s):.0f} below the rail land at mid height,\n{d.mon_setback + fr.rise(d, d.image_s + 107.7):.0f} at the top of the window", size=7)
    note(ax, (40, 530), f"monitor, power supply and BC-250: outlines of the\nlast build (dashed); the monitor moved {Dims().mon_setback - d.mon_setback:.1f} forward\nwith the screen", size=7)
    bx = fig.add_subplot(grid[0, 1])
    sec = pr.deck_front_section(d)
    bx.plot([p[0] for p in sec], [p[1] for p in sec], color=INK, lw=1.6)
    frame(bx, "The edge section, large: here on the deck's front;\nthe same section runs up the rail", (-22, 40), (-8, d.deck_top + 12), "in from the outer face (mm)", "z (mm)")
    t = math.radians(90 - d.deck_lean)
    zr = d.deck_top - d.deck_top_r * (1 - math.cos(t))
    zc = d.deck_top - d.deck_lean_h
    dim(bx, (-12, zc), (-12, d.deck_top), f"crease {d.deck_lean_h:.0f} below the top", (-4, 0), turn=90)
    dim(bx, (0, d.deck_top + 5), (d.edge_in, d.deck_top + 5), f"{d.edge_in:.1f} in", (0, 3.5))
    note(bx, (12, zr + 6), f"DK2 / RL2: radius {d.deck_top_r:.1f},\nturning {90 - d.deck_lean:.0f} deg", to=(d.edge_in - 6, d.deck_top - 2.5))
    note(bx, (12, (zr + zc) / 2), f"DK3 / RL3: band leaning {d.deck_lean:.0f} deg,\n{zr - zc:.1f} high", to=(1.5, (zr + zc) / 2))
    note(bx, (12, zc - 6), f"crease, {d.deck_lean_h / d.deck_top:.2f} of the front height", to=(0, zc))
    note(bx, (12, 25), "DK4 to DK7 / RL4: the outer face\n(deck front and sides, side band)", to=(0, 25))
    note(bx, (12, 5), f"bottom radius {d.bottom_r:.0f}", to=(1.2, 1.2))
    fig.suptitle("Blueprint 03: side section at the centre line, and the edge section that the deck and the rail share", fontsize=14, y=0.985)
    save(fig, "03-side-section")


def sheet_plan_sections(d: Blueprint, faces: dict[str, pr.Face]) -> None:
    h = pr.hood(d)
    hw = d.width / 2
    zs = d.face(d.image_s)[1]
    cuts = [("A. through a hood leg", h.origin[2] + 60.0, (150, 275), (370, 650)),
            ("B. through the rail at mid screen", zs, (150, 275), (320, 600)),
            ("C. at the rail's foot, in the sweep", d.deck_top + 13.0, (150, 275), (150, 430)),
            ("D. through the deck's side, below the crease", d.deck_top - 32.0, (110, 275), (-20, 260))]
    fig, axes = plt.subplots(1, 4, figsize=(21, 12.5), gridspec_kw={"width_ratios": [125, 125, 125, 165], "top": 0.9, "bottom": 0.06, "left": 0.04, "right": 0.99})
    for ax, (title, z, xlim, ylim) in zip(axes, cuts):
        segs = cut(faces, 2, z)
        draw_cut(ax, segs, lw=2.2)
        frame(ax, f"{title}\n(cut at z = {z:.0f}, seen from above)", xlim, ylim, "x, from the centre line (mm)", "y, from the deck front (mm)")
        tag_cut(ax, segs, (*xlim, *ylim), off=11.0)
        ax.axvline(hw, color=RED, lw=0.5, ls=":")
        ax.text(hw + 2, ylim[1] - 4, f"side plane x = {hw:.1f}", color=RED, fontsize=6.5, rotation=90, va="top")
    a = axes[1]
    yf = pr.front(d).on_rail(d, d.image_s)[0]
    dim(a, (d.bezel_w / 2 + d.panel_gap, yf - 14), (hw - d.edge_in, yf - 14), f"land {d.rail_land:.1f}", (-4, -8))
    dim(a, (hw - d.edge_in, yf - 14), (hw, yf - 14), f"{d.edge_in:.1f}", (2, -8))

    note(a, (153, 560), f"RL4 side band: in the side plane up to z {d.tuck_z0:.0f}, flush\nwith the deck's side DK7; above that it leans in\ntoward the hood. It carries the stripe. Behind it\nthe step RB2 turns in 12 to the rear body side RB1.", size=7.5)
    note(a, (153, 420), "RL1 land, RL2 radius, RL3 band leaning 10 deg,\ncrease, RL4: the deck's edge section on its side.\nThe crease lies 24 behind the land, square to the\nrail arc. BZ1, BZ2: the bezel land and inner frame.", size=7.5)
    note(axes[2], (153, 400), "The same section, carried round the sweep:\nRL2 and RL3 run on into DK2 and DK3 of the deck.\nThe land RL1 turns into the deck top DK1.", size=7.5)
    note(axes[3], (113, 235), "DK7 (deck side) and RL4 (side band) are one plane.\nAbove the crease (z 48 to 63) the band DK3 leans in\n10 deg, up to 2.7; see sheet 03.", size=7.5)
    note(axes[0], (153, 632), "The leg of the hood, 60 above the seam. Its side HC5\nis already in from the side plane: it leaves the seam\non the tangent of the body's tuck. HC4 is the soft edge.", size=7.5)
    fig.suptitle("Blueprint 04: horizontal sections through the right side of the target, one scale (each line in the colour of its face)", fontsize=14, y=0.985)
    save(fig, "04-plan-sections")


HOOD_IDS = {"HC1", "HC2", "HC3", "HC4", "HC5", "HC6", "HC7", "HC8", "HC9", "HC10", "HC11", "HC12", "HC13", "MQ1", "MQ2", "HB1", "SP1", "SP2", "LG1", "LG2"}


def sheet_hood(d: Blueprint, faces: dict[str, pr.Face]) -> None:
    h = pr.hood(d)
    ox, oy, oz = h.origin
    hw = d.width / 2
    fig = plt.figure(figsize=(20, 15))
    grid = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.25], hspace=0.14, wspace=0.08)
    a = fig.add_subplot(grid[0, :])
    paint(a, faces, VIEWS["front"], "white", only=HOOD_IDS, lw=0.7)
    frame(a, "Front elevation of the hood", (-330, 330), (oz - 40, oz + h.height + 50), "x (mm)", "z, above the desk (mm)", grid=False)
    a.plot([-hw, hw], [d.body_top, d.body_top], color="#777", lw=1.0)
    w, mh = pr.marquee_window(d, h)
    top = oz + h.height
    dim(a, (-h.half_base, oz - 16), (h.half_base, oz - 16), f"foot {2 * h.half_base:.1f} = the body top (body {d.width:.1f} below the tuck): no shoulder, a groove of {d.seam_groove:.0f} at the seam", (0, -9))
    dim(a, (-h.half_top, top + 14), (h.half_top, top + 14), f"top flat {2 * h.half_top:.1f} = {2 * h.half_top / d.width:.3f} W", (0, 9))
    dim(a, (h.half_base + 40, oz), (h.half_base + 40, oz + h.z_corner), f"side: tangent to the tuck\nat the seam, near straight,\n{d.tuck_lean:.1f} to {d.tuck_lean + d.hood_side_turn:.1f} deg", (48, 0), ha="center")
    dim(a, (h.half_base + 40, oz + h.z_corner), (h.half_base + 40, top), f"top corner R {h.corner.r:.1f}\n= {d.hood_corner_ratio:.2f} W", (40, 0), ha="center")
    xb = h.half_width(h.z_corner)
    dim(a, (h.half_top, top + 34), (xb, top + 34), f"corner {xb - h.half_top:.0f} wide", (0, 9))
    dim(a, (-h.half_base - 30, d.body_top), (-h.half_base - 30, top), f"hood {d.hood_h:.1f} = {d.hood_h / d.width:.2f} W", (-9, 0), turn=90)
    dim(a, (-w / 2, oz + (h.z_rail_top + h.z_open_top) / 2), (w / 2, oz + (h.z_rail_top + h.z_open_top) / 2), f"marquee window {w:.0f} x {mh:.0f}, straight ({int(w // d.marquee_module)} modules of {d.marquee_module:.0f})", size=8)
    dim(a, (-60, oz + h.z_open_top), (-60, top), f"top bar {d.hood_bar:.0f}", (-30, 0))
    xs = h.half_width(h.z_sill + 30, h.opening)
    dim(a, (xs, oz + h.z_sill + 30), (h.half_width(h.z_sill + 30), oz + h.z_sill + 30), f"leg {d.hood_bar:.0f}", (0, 9))
    note(a, (-325, oz + 6), f"bottom corners of the opening R {d.hood_sill_corner_r:.0f};\nsill {d.hood_sill_h:.0f} high", to=(-h.half_width(h.z_sill, h.opening) + 4, oz + h.z_sill + 3))
    for fid, at in (("HC1", (h.half_width(40) - 9, oz + 40)), ("HC2", (0, top - d.hood_bar + 2.5)), ("HC3", (0, oz + 8)), ("HC4", (h.half_top - 40, top - 7)),
                    ("MQ2", (-w / 2 + 30, oz + h.z_rail_top + 10)), ("MQ1", (w / 2 + 10, oz + h.z_rail_top + 8)), ("HC13", (0, oz + (h.z_band_top + h.z_rail_top) / 2)),
                    ("HB1", (d.logo_w / 2 + 9, oz + 60)), ("SP1", (150, oz + h.z_band_top - 9)), ("SP2", (150, oz + 55)), ("LG1", (-d.logo_w / 2 + 12, oz + h.z_band_top - 14)), ("LG2", (0, oz + 55))):
        tag(a, at, fid)
    for i, (x, title) in enumerate(((0.01, "Side section of the hood at the centre line"), (speaker_x(d), "Side section of the hood through a speaker"))):
        b = fig.add_subplot(grid[1, i])
        segs = {k: v for k, v in cut(faces, 0, x).items() if k in HOOD_IDS | {"FB3", "FB4", "RB5", "RB4", "BZ1"}}
        draw_cut(b, segs, lw=1.8)
        frame(b, title, (oy - 70, oy + h.depth + 75), (oz - 45, top + 48), "y, from the deck front (mm)", "z, above the desk (mm)")
        tag_cut(b, segs, (oy - 70, oy + h.depth + 75, oz - 45, top + 42), off=10.0, skip={"HC5", "HC6", "HC11", "HC1"},
                place={"HC13": (oy + 78, oz + h.z_band_top + 4), "MQ1": (oy + 78, oz + h.z_rail_top + 16), "HB1": (oy + 78, oz + h.z_band_top - 14),
                       "HC4": (oy + 6, top + 12), "HC7": (oy + 46, top + 12)})
        if i == 0:
            dim(b, (oy, top + 34), (oy + h.depth, top + 34), f"depth {h.depth:.1f} = {h.depth / d.width:.3f} W", (0, 6))
            dim(b, (oy, top + 22), (oy + d.hood_edge_back, top + 22), f"soft edge {d.hood_edge_back:.0f} back,\n{d.hood_edge_in:.0f} down", (-38, 0))
            dim(b, (oy + h.depth - d.hood_rear_arc_d, top + 22), (oy + h.depth, top + 22), f"rear arc {d.hood_rear_arc_d:.0f} deep", (0, 6))
            dim(b, (oy + h.depth + 22, top - d.hood_rear_arc_h), (oy + h.depth + 22, top), f"{d.hood_rear_arc_h:.0f} high", (9, 0), turn=90)
            x0 = oy - 36
            for z0, z1, text in ((0, h.z_sill, f"sill {h.z_sill:.0f}"), (h.z_sill, h.z_band_top, f"band {h.z_band_top - h.z_sill:.1f}"), (h.z_band_top, h.z_rail_top, f"lip {d.hood_rail_h:.0f}"),
                                 (h.z_rail_top, h.z_open_top, f"marquee {h.z_open_top - h.z_rail_top:.1f}"), (h.z_open_top, h.height, f"top bar {d.hood_bar:.0f}")):
                dim(b, (x0, oz + z0), (x0, oz + z1), text, (-4, 0), ha="right")
            tb = math.radians(d.hood_band_tilt)
            rear = h.y_band_top + d.hood_band_t / math.cos(tb)
            dim(b, (oy + rear, oz + h.z_band_top - 4), (oy + h.y_rear(h.z_band_top) - d.hood_wall, oz + h.z_band_top - 4),
                f"{h.y_rear(h.z_band_top) - d.hood_wall - rear:.0f} clear behind the band", (0, -7))
            dim(b, (oy, oz + h.z_band_top - 10), (oy + h.y_band_top, oz + h.z_band_top - 10), f"band {h.y_band_top:.1f} back", (-4, -7))
            yr = h.y_band_top - d.hood_rail_proud
            dim(b, (oy + yr, oz + h.z_rail_top + 4), (oy + h.y_marquee_bottom, oz + h.z_rail_top + 4), f"edge {h.y_marquee_bottom - yr:.1f}", (16, 5))
            yf = h.front_y(h.z_open_top)
            dim(b, (oy + yf, oz + h.z_open_top - 6), (oy + h.y_marquee_top, oz + h.z_open_top - 6), f"soffit {h.y_marquee_top - yf:.1f}", (22, 0))
            note(b, (oy + h.depth + 8, oz + 60), f"band upright, {d.hood_band_recess:.0f} behind the hood front\nat its top; the marquee upright in the\nplane of the band, an edge of {d.hood_marquee_edge:.0f}\non top of the lip;\nfront leans back {d.hood_front_lean_low:.0f}, then {d.hood_front_lean_up:.0f} deg;\nfoot on the line of the rail;\nrear flush with the upper rear", size=7)
        else:
            ys = h.y_band_top - d.speaker_proud
            zb, zt = h.z_sill + d.speaker_foot_gap, h.z_band_top - d.speaker_head_gap
            note(b, (oy + h.depth + 8, oz + 60), f"speaker form {d.speaker_proud:.0f} proud, its front\nupright: it fires straight forward;\n"
                 f"its front is {h.front_y(zt) - ys:.1f} ahead of the hood\nfront at its top, {h.front_y(zb) - ys:.1f} at its foot", size=7)
    fig.suptitle("Blueprint 05: the hood of the target", fontsize=14, y=0.985)
    save(fig, "05-hood")


def sheet_junctions(d: Blueprint, faces: dict[str, pr.Face]) -> None:
    h = pr.hood(d)
    oy, oz = h.origin[1], h.origin[2]
    hw, bt, ys = d.width / 2, d.body_top, d.seam_y
    fig, axes = plt.subplots(2, 3, figsize=(21, 15))
    panels = [
        ("side", (oy - 50, oy + h.depth + 45), (bt - 70, bt + 95), "Hood to body, from the right side",
         [("HC4", (oy + 16, bt + 60), None), ("HC5", (oy + 80, bt + 60), None), ("RL4", (oy + 80, bt - 40), None), ("RL3", (oy - 30, bt - 60), (ys + 7, bt - 20)),
          ("RL2", (oy - 44, bt - 42), (ys - 7, bt - 20)), ("FB4", (oy + 150, bt + 22), (oy + 120, bt)), ("RB5", (oy + 160, bt - 45), (d.depth, bt - 40)),
          ("HC9", (oy + 160, bt + 50), (oy + h.depth, bt + 45)), ("FB5", (oy + 110, bt - 20), (oy + 100, bt - 1.5)),
          ("HC15", (oy + 110, bt + 25), (oy + 100, bt + d.seam_gap + 1.5))]),
        ("front", (hw - 95, hw + 22), (bt - 70, bt + 95), "Hood to body, from the front: the right foot",
         [("HC1", (hw - 62, bt + 78), (h.half_width(60.0, h.opening) + 2.5, bt + 60)), ("HC4", (hw + 10, bt + 85), (h.half_width(60.0) - 8, bt + 60)), ("HC3", (hw - 80, bt + 9), None),
          ("RL1", (hw - 21, bt - 45), None), ("RL2", (hw + 12, bt - 30), (hw - 8.5, bt - 30)), ("RL3", (hw + 12, bt - 55), (hw - 1.5, bt - 55)), ("FB3", (hw - 70, bt - 6), None),
          ("BZ1", (hw - 70, bt - 40), None), ("FB5", (hw + 14, bt + 5), (d.side_x(d.body_top) - 1.0, bt - 1.0)),
          ("HC15", (hw + 14, bt + 22), (h.half_base - 1.0, bt + d.seam_gap + 1.0))]),
        ("top", (hw - 95, hw + 22), (ys - 25, ys + 95), "Hood to body, from above: the right foot on the body top",
         [("FB4", (hw - 6, ys + 62), None), ("HC4", (hw - 50, ys + 20), None), ("HC5", (hw + 12, ys + 84), (hw - 16, ys + 84)), ("RL1", (hw - 21, ys - 12), None),
          ("RL2", (hw + 12, ys - 6), (hw - 8, ys + 3)), ("RL3", (hw + 12, ys + 24), (hw - 2, ys + 14)), ("FB3", (hw - 70, ys - 5), None),
          ("FB5", (hw + 12, ys + 50), (d.side_x(d.body_top) - 1.5, ys + 50))]),
        ("side", (130, 330), (-12, 175), "Body to deck, from the right side",
         [("RL4", (300, 40), None), ("DK7", (165, 25), None), ("RL3", (318, 166), (288, 130)), ("RL2", (238, 166), (274, 130)), ("DK3", (165, 100), (165, 56)),
          ("DK2", (142, 100), (150, 68))]),
        ("front", (hw - 110, hw + 22), (-12, 175), "Body to deck, from the front",
         [("RL1", (hw - 21, 140), None), ("RL2", (hw + 12, 150), (hw - 8.5, 150)), ("RL3", (hw + 12, 125), (hw - 1.5, 125)), ("DK2", (hw + 12, 90), (hw - 7, 68)),
          ("DK3", (hw + 12, 60), (hw - 1.2, 56)), ("DK6", (hw - 19, 25), None), ("DK5", (hw - 77, 25), None), ("FB2", (hw - 72, 135), None), ("FB1", (hw - 72, 85), None),
          ("BZ1", (hw - 72, 165), None)]),
        ("top", (hw - 110, hw + 22), (150, 320), "Body to deck, from above",
         [("DK1", (hw - 32, 180), None), ("CP1", (hw - 82, 175), None), ("RL1", (hw - 21, 300), None), ("FB1", (hw - 72, 225), None), ("FB2", (hw - 72, 262), None),
          ("RL2", (hw + 12, 290), (hw - 8.5, 290)), ("RL3", (hw + 12, 260), (hw - 1.5, 260)), ("DK2", (hw + 12, 185), (hw - 8.5, 185)), ("DK3", (hw + 12, 165), (hw - 1.5, 165)),
          ("BZ1", (hw - 72, 305), None)])]
    for ax, (key, xlim, ylim, title, tags) in zip(axes.ravel(), panels):
        paint(ax, faces, VIEWS[key], "colour", lw=0.7)
        frame(ax, title, xlim, ylim, grid=False)
        for fid, at, to in tags:
            tag(ax, at, fid, to=to, size=7.5)
    a = axes[0, 0]
    note(a, (oy - 46, bt + 84), f"The cap stands on the body top with a seam of {d.seam_gap:.1f}. Its foot lies on the line of the rail; its front\nleans back {d.hood_front_lean_low:.0f} deg, less than the rail ({pr.front(d).top_lean:.0f} deg), then {d.hood_front_lean_up:.0f} deg.\nThe groove is level all round: a bevel of {d.seam_groove:.0f} on each part. The rear of the cap is flush with the upper rear.", size=7.5)
    a = axes[0, 1]
    dim(a, (h.half_base, bt - 22), (hw, bt - 22), f"tuck {d.tuck:.1f}", (2, -7))
    note(a, (hw - 92, bt - 62), f"The side of the hood HC5 leaves the seam on the tangent of the body side RL4:\nno shoulder, a groove of {d.seam_groove:.0f}: FB5 below, HC15 above. The leg stands over the land RL1 and the edge RL2, RL3.", size=7.5)
    note(axes[0, 2], (hw - 92, ys + 88), "From above, the foot of the leg lies inside the\noutline of the body top everywhere.\n"
         f"The seam groove: a bevel of {d.seam_groove:.0f} on each part, at one height all round:\nalong the sides, round the front corners, across the front.\n"
         f"FB5 runs round the body top, HC15 round the foot of the cap.", size=7.5)
    note(axes[1, 0], (135, 150), "RL2 and RL3 come down the rail arc, turn through the sweep\nand run on along the deck as DK2 and DK3: one section,\none width, no jump. RL4 and DK7 are one plane.", size=7.5)
    a = axes[1, 1]
    dim(a, (hw - d.edge_in, 170), (hw, 170), f"{d.edge_in:.1f}", (-16, 0))
    note(a, (hw - 106, 45), "The deck's side DK7 and the side band RL4\nlie in one plane: flush.", size=7.5)
    note(axes[1, 2], (hw - 106, 312), "The edge keeps its width in plan.", size=7.5)
    fig.suptitle("Blueprint 06: the two junctions of the target, large (hood to body above, body to deck below)", fontsize=14, y=0.995)
    fig.tight_layout()
    save(fig, "06-junctions")


GHOSTS = {
    # the same curves on the references, as ratios, for the ghost lines of sheet 08: (value, where the tuck starts)
    "tuck": {"maker's mini: 0.010 W from 0.75": (0.010, 0.75), "real New Astro City: 0.018 W from 0.78 (upper limit)": (0.018, 0.78)},
    "rail": {"maker's mini: straight (0.000 +-0.002)": 0.0, "3D reference model: 0.091 of the chord": 0.091},
}


def sheet_curvature(d: Blueprint, faces: dict[str, pr.Face]) -> None:
    """Every curved line against its straight chord, with the deviation drawn five times too large."""
    fr, h = pr.front(d), pr.hood(d)
    k = 5.0
    fig = plt.figure(figsize=(21, 14.5))
    grid = fig.add_gridspec(2, 3, hspace=0.24, wspace=0.2, top=0.92, bottom=0.05, left=0.045, right=0.985)

    a = fig.add_subplot(grid[0, 0])
    t = np.linspace(0.0, fr.chord, 80)
    arc = lambda ratio: (np.sqrt((fr.chord / (2 * math.sin(2 * math.atan(2 * ratio)))) ** 2 - (t - fr.chord / 2) ** 2)
                         - (fr.chord / (2 * math.sin(2 * math.atan(2 * ratio))) - ratio * fr.chord)) if ratio > 0 else np.zeros_like(t)
    a.plot(t, np.zeros_like(t), color=INK, lw=0.8, ls="--", label="chord (the blueprint before: a straight rail)")
    for (label, ratio), c in zip(GHOSTS["rail"].items(), ("#2ca02c", "#1f77b4")):
        a.plot(t, k * arc(ratio), color=c, lw=1.2, ls=":" if ratio == 0 else "-", alpha=0.8, label=label)
    a.plot(t, k * arc(d.rail_sagitta_ratio), color=RED, lw=2.4, label=f"this cabinet: {d.rail_sagitta_ratio:.3f} of the chord")
    dim(a, (fr.chord / 2, 0.0), (fr.chord / 2, k * fr.sagitta), f"sagitta {fr.sagitta:.1f}", (38, 0))
    for s_, name in ((d.bezel_s0, "bezel bottom"), (d.image_s, "screen centre"), (d.bezel_s1, "bezel top")):
        x = (s_ - d.bend_t) / (d.top_s - d.bend_t) * fr.chord
        a.plot([x, x], [0, k * fr.rise(d, s_)], color=RED, lw=0.6)
        a.text(x, -9, f"{name}\n{fr.rise(d, s_):.1f}", fontsize=7, ha="center", va="top", color=RED)
    frame(a, f"1. Rail land in side view (RL1): deviation from its chord, drawn x{k:.0f}\nchord {fr.chord:.0f} long, reclined {fr.recline:.0f} deg; foot at the left, seam at the right",
          (-10, fr.chord + 10), (-32, k * 0.091 * fr.chord + 14), "along the chord (mm)", f"in front of the chord (mm x {k:.0f})")
    a.set_aspect("auto")
    a.set_yticks([k * v for v in (0, 10, 20, 30)], ["0", "10", "20", "30"])
    a.legend(loc="upper left", fontsize=7.5, frameon=False)

    b = fig.add_subplot(grid[0, 1])
    top = d.body_top + d.hood_h
    zs = np.linspace(d.deck_top, d.body_top, 120)
    hw = d.width / 2

    def tuck_line(ratio: float, start: float) -> np.ndarray:
        z0 = d.deck_top + start * (d.body_top - d.deck_top)
        lean = 2 * math.atan2(ratio * d.width, d.body_top - z0)
        r = (d.body_top - z0) / math.sin(lean)
        return np.where(zs > z0, r - np.sqrt(np.maximum(r ** 2 - (zs - z0) ** 2, 0.0)), 0.0)

    b.plot([0, 0], [d.deck_top, d.body_top], color=INK, lw=0.8, ls="--", label="side plane (the blueprint before: a straight side)")
    b.plot([k * 12, k * (12 + 45 * math.tan(math.radians(7)))], [d.body_top, d.body_top + 45], color=INK, lw=0.8, ls=":")
    b.plot([0, k * 12], [d.body_top, d.body_top], color=INK, lw=0.8, ls=":", label="the blueprint before: a shoulder of 12 under the hood")
    for (label, (ratio, start)), c in zip(GHOSTS["tuck"].items(), ("#2ca02c", "#ff7f0e")):
        b.plot(k * tuck_line(ratio, start), zs, color=c, lw=1.3, alpha=0.85, label=label)
    b.plot(k * np.array([hw - d.side_x(z) for z in zs]), zs, color=RED, lw=2.4, label=f"this cabinet: {d.body_tuck_ratio:.3f} W from {d.body_tuck_from:.2f}")
    hz = np.array([z for x, z in h.outline if z <= 45.0])
    hx = np.array([x for x, z in h.outline if z <= 45.0])
    b.plot(k * (hw - hx), h.origin[2] + hz, color=RED, lw=2.4)
    b.plot([-4, k * 16], [d.body_top + d.seam_gap / 2] * 2, color="#888", lw=0.6)
    b.text(k * 13.2, d.body_top - 7, f"seam: a groove of {d.seam_groove:.0f}", fontsize=7, va="center", color="#555")
    b.plot([-6, 6], [d.tuck_z0, d.tuck_z0], color=RED, lw=0.6)
    b.text(8, d.tuck_z0 - 5, f"the tuck starts at z {d.tuck_z0:.0f}\n({d.body_tuck_from:.2f} of the body height)", fontsize=7, va="top", color=RED)
    dim(b, (0, d.body_top + 12), (k * d.tuck, d.body_top + 12), f"{d.tuck:.1f} in at the seam, {d.tuck_lean:.1f} deg there", (0, 9))
    frame(b, f"2. Body side and the foot of the hood in front view (RL4, HC5): distance in from the side plane, drawn x{k:.0f}\nthe tuck: one arc of R {d.tuck_r:.0f} ({d.tuck_r / d.width:.2f} W) up to the seam; the hood side leaves it on its tangent: no shoulder, no corner",
          (-6, k * 23), (d.deck_top - 10, d.body_top + 62), f"in from the side plane (mm x {k:.0f})", "z, above the desk (mm)")
    b.set_aspect("auto")
    b.set_xticks([k * v for v in (0, 5, 10, 15, 20)], ["0", "5", "10", "15", "20"])
    b.legend(loc="lower right", fontsize=7.5, frameon=False)

    c = fig.add_subplot(grid[0, 2])
    ss = np.linspace(d.bezel_s0, d.bezel_s1, 120)
    land = np.array([fr.rise(d, v) for v in ss])
    win0, win1 = d.image_s - 107.712, d.image_s + 107.712
    c.plot(ss - d.bezel_s0, k * land, color=RED, lw=2.4, label="rail land RL1 (the bezel land BZ1 lies 2 below it)")
    c.plot(ss - d.bezel_s0, np.zeros_like(ss), color=INK, lw=0.8, ls="--", label="chord of the rail (the flat front of the blueprint before)")
    c.plot([win0 - d.bezel_s0, win1 - d.bezel_s0], [-k * d.mon_setback] * 2, color="#1f77d0", lw=2.4, label=f"screen SC1: flat, {d.mon_setback:.1f} behind the chord")
    inner0, inner1 = d.bezel_land, d.bezel_len - d.bezel_land
    for s_in, s_win in ((inner0, win0 - d.bezel_s0), (inner1, win1 - d.bezel_s0)):
        c.plot([s_in, s_win, s_win], [k * (fr.rise(d, d.bezel_s0 + s_in) - 2), -k * (d.mon_setback - d.bezel_rim), -k * d.mon_setback], color="#555", lw=1.4)
    c.plot([], [], color="#555", lw=1.4, label="bezel inner frame BZ2 and rim BZ3")
    for s_, text in ((win0, "bottom of the window"), (d.image_s, "screen centre"), (win1, "top of the window")):
        x = s_ - d.bezel_s0
        dim(c, (x, -k * d.mon_setback), (x, k * fr.rise(d, s_)), f"{d.mon_setback + fr.rise(d, s_):.1f}", (11, 0), size=7.5)
    frame(c, f"3. Flat screen in the convex body: depth of the screen below the rail land, drawn x{k:.0f}\nalong the bezel from its bottom edge (left) to its top edge (right)",
          (-8, d.bezel_len + 8), (-k * 24, k * 22), "along the bezel (mm)", f"in front of the chord (mm x {k:.0f})")
    c.set_aspect("auto")
    c.set_yticks([k * v for v in (-20, -10, 0, 10, 20)], ["-20", "-10", "0", "10", "20"])
    c.legend(loc="upper center", fontsize=7.5, frameon=False, ncol=2)

    e = fig.add_subplot(grid[1, 0])
    out = np.array(h.outline)
    e.plot(out[:, 0], out[:, 1], color=RED, lw=2.2, label="this cabinet")
    e.plot(-out[:, 0], out[:, 1], color=RED, lw=2.2)
    body = np.array([(d.side_x(z), z - h.origin[2]) for z in np.linspace(d.body_top - 130, d.body_top, 40)])
    for sgn in (1, -1):
        e.plot(sgn * body[:, 0], body[:, 1], color=RED, lw=1.2)
        e.plot([sgn * hw, sgn * hw], [-130, -d.seam_gap], color=INK, lw=0.7, ls="--")
        e.plot([sgn * hw, sgn * (hw - 12), sgn * (hw - 12 - 60 * math.tan(math.radians(7)))], [-d.seam_gap, -d.seam_gap, 60], color=INK, lw=0.7, ls=":")
    e.plot([], [], color=INK, lw=0.7, ls=":", label="the blueprint before: straight side, shoulder 12, hood side 7 deg")
    xb_ = h.half_width(h.z_corner)
    e.plot([xb_, xb_ - (h.height - h.z_corner) * math.tan(math.radians(d.tuck_lean + d.hood_side_turn))], [h.z_corner, h.height], color=INK, lw=0.7, ls="--")
    e.plot([h.half_top, xb_ - (h.height - h.z_corner) * math.tan(math.radians(d.tuck_lean + d.hood_side_turn))], [h.height, h.height], color=INK, lw=0.7, ls="--")
    dim(e, (h.half_top, h.height + 10), (xb_, h.height + 10), f"corner R {h.corner.r:.0f} ({d.hood_corner_ratio:.2f} W)", (0, 9))
    dim(e, (-h.half_top, h.height + 10), (h.half_top, h.height + 10), f"top flat {2 * h.half_top:.0f}: straight across (crown {d.hood_crown_ratio:.0f})", (0, 9))
    note(e, (-150, 70), f"lean of the side: 0 below z {d.tuck_z0:.0f}, {d.tuck_lean:.1f} deg at the seam,\n{d.tuck_lean + d.hood_side_turn:.1f} deg where the top corner starts, {h.z_corner:.0f} above the seam", size=7.5)
    frame(e, "4. Upper body and hood in front view, true scale: one line from the side band over the seam into the top",
          (-270, 270), (-135, h.height + 32), "x (mm)", "z, above the seam (mm)")
    e.legend(loc="lower center", fontsize=7.5, frameon=False)

    f = fig.add_subplot(grid[1, 1])
    side = np.array(h.side)
    f.plot(side[:, 0], side[:, 1], color=RED, lw=2.2)
    y0, y1 = h.depth - d.hood_rear_arc_d, h.depth
    f.plot([y0, y1], [h.height, h.height - d.hood_rear_arc_h], color=INK, lw=0.7, ls="--")
    f.plot([0, d.hood_edge_back], [h.height - d.hood_edge_in, h.height], color=INK, lw=0.7, ls="--")
    mid = pr.Conic((y0, h.height), (y1, h.height), (y1, h.height - d.hood_rear_arc_h)).at(0.5)
    cm = ((y0 + y1) / 2, h.height - d.hood_rear_arc_h / 2)
    dim(f, cm, mid, f"{math.dist(cm, mid):.1f}", (-12, -8))
    note(f, (4, 40), f"rear arc HC8: a quarter ellipse {d.hood_rear_arc_d:.0f} deep and {d.hood_rear_arc_h:.0f} high;\nsoft edge HC4: a quarter ellipse {d.hood_edge_back:.0f} back and {d.hood_edge_in:.0f} down;\nroof between them {y0 - d.hood_edge_back:.0f} long, flat; front and rear walls upright", size=7.5)
    frame(f, "5. Hood in side view, true scale: the long arc from the roof down the rear", (-20, h.depth + 20), (-10, h.height + 20), "y, behind the front of the cap (mm)", "z, above the seam (mm)")

    g = fig.add_subplot(grid[1, 2])
    g.axis("off")
    rows = [("Hood top across the width (crown)", "straight", "0.000 +-0.001 W (owner-ref-1), 0.000 +-0.005 W (photo-b), 0 (3D model)", f"{d.hood_crown_ratio:.3f} W: straight"),
            ("Body side below the tuck (bow)", "straight", "0.000 +-0.003 W (owner-ref-1), 0.000 +-0.004 W (photo-g), 0 (3D model)", f"{d.body_bow_ratio:.3f} W: straight"),
            ("Front edge of the side band (crease RL3 / RL4)", "straight, parallel to the rail", "straight within 0.002 of its length on the maker's mini (photo-e)",
             "follows the rail arc, 24 behind it"),
            ("Sides in plan (side band, deck side)", "straight", "straight on the 3D model; deck sides parallel within 4 deg on the mini", "straight"),
            ("Deck front in plan", "three faces", "three faces, 0.56 of the width and 8 deg (measured)", "three faces, no change"),
            ("Step behind the side band", "straight, leans 28 deg", "straight on the 3D model and on the mini", "straight"),
            ("Rear walls, body top", "flat", "flat on the 3D model; hidden or not readable in the photos", "flat"),
            ("Hood front, hood band, marquee", "flat planes", "flat on all three", "flat planes")]
    import textwrap
    cols, widths = (0.0, 0.25, 0.42, 0.80), (24, 16, 38, 20)
    y = 0.97
    for row in [("Line", "Blueprint before", "What the references show", "Drawn now")] + rows:
        cells = [textwrap.fill(text, w) for text, w in zip(row, widths)]
        for x, cell in zip(cols, cells):
            g.text(x, y, cell, fontsize=7.5, va="top", weight="bold" if row[0] == "Line" else "normal", transform=g.transAxes)
        y -= 0.034 * max(cell.count("\n") + 1 for cell in cells) + 0.022
        g.plot([0, 1], [y + 0.011, y + 0.011], color="#bbb", lw=0.4, transform=g.transAxes)
    g.set_xlim(0, 1)
    g.set_ylim(0, 1)
    g.set_title("6. Lines that stay straight, because the references show them straight", fontsize=9.5)
    fig.suptitle(f"Blueprint 08: curvature. Panels 1 to 3 draw the deviation from the straight line {k:.0f} times too large; the ghost lines are the same curve on the references",
                 fontsize=13.5, y=0.975)
    save(fig, "08-curvature")


def write_tables(d: Blueprint) -> None:
    """Put the proportion table and the face table into docs/blueprint/index.md, between their markers."""
    path = os.path.join(OUT, "index.md")
    if not os.path.exists(path):
        return
    text = open(path).read()
    rows = ["| Ratio to the body width W | 3D reference model (exact) | Maker's mini (photos) | Real New Astro City | This cabinet | Why it differs |", "| --- | --- | --- | --- | --- | --- |"]
    rows += ["| " + " | ".join(r) + " |" for r in proportions(d)]
    faces = ["| ID | Name | Component | Which way it faces | Curvature | What sets it | Joins | How to build it, and the print |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    faces += [f"| {k} | {v[0]} | {v[1]} | {v[2]} | {v[5]} | {v[4]} | {v[3]} | {v[6]} |" for k, v in pr.FACES.items()]
    for key, body in (("proportions", rows), ("faces", faces)):
        begin, end = f"<!-- {key}:begin -->", f"<!-- {key}:end -->"
        if begin in text and end in text:
            text = text[:text.index(begin) + len(begin)] + "\n" + "\n".join(body) + "\n" + text[text.index(end):]
    open(path, "w").write(text)
    print("draw_blueprint: tables ->", os.path.relpath(path, REPO))


def target(only: str = "") -> None:
    d = Blueprint()
    faces = pr.faces(d)
    write_tables(d)
    sheets = {"01": sheet_volumes, "02": sheet_elevations, "03": sheet_side_section, "04": sheet_plan_sections, "05": sheet_hood, "06": sheet_junctions,
              "07": sheet_face_map, "08": sheet_curvature}
    for key, fn in sheets.items():
        if not only or key in only.split(","):
            fn(d, faces)


def speaker_x(d: Blueprint) -> float:
    """Where a side section cuts through the right speaker form."""
    return d.logo_w / 2 + d.logo_gap + 40.0


def band_options() -> None:
    """Three places in depth for the upright hood band, side by side to one scale: recessed (the build),
    flush with the hood front at the top of the band, and proud from the front edge of the sill."""
    d0 = Blueprint()
    h0 = pr.hood(d0)
    proud = h0.front_y(h0.z_sill) - h0.front_y(h0.z_band_top)
    options = (("a. recessed (built)", d0.hood_band_recess), ("b. flush at the top of the band", 0.0), ("c. proud, from the front edge of the sill", proud))
    fig, axes = plt.subplots(1, 3, figsize=(18, 8.5))
    x = speaker_x(d0)
    for ax, (title, recess) in zip(axes, options):
        d = replace(d0, hood_band_recess=recess)
        h = pr.hood(d)
        oy, oz = h.origin[1], h.origin[2]
        segs = {k: v for k, v in cut(pr.faces(d), 0, x).items() if k in HOOD_IDS | {"SP3", "FB3", "FB4"}}
        draw_cut(ax, segs, lw=1.8)
        front = np.array(pr.sample(h.front, 1.0))
        ax.plot(oy + front[:, 0], oz + front[:, 1], color=INK, lw=0.8, ls="--", zorder=40, label="outer front of the hood (the legs)")
        frame(ax, f"{title}\nhood_band_recess {recess:.1f}", (oy - 40, oy + 80), (oz - 12, oz + h.height + 8), "y, from the deck front (mm)", "z, above the desk (mm)")
        tag_cut(ax, segs, (oy - 40, oy + 80, oz - 12, oz + h.height + 8), off=9.0, skip={"HC1", "HC5", "HC6", "HC11"},
                place={"HC13": (oy - 20, oz + h.z_rail_top + 4), "SP3": (oy + 20, oz + h.z_sill - 6)})
        zb, zt = h.z_sill + d.speaker_foot_gap, h.z_band_top - d.speaker_head_gap
        ys = h.y_band_top - d.speaker_proud
        ahead = lambda y: f"{abs(y - ys):.1f} {'ahead of' if ys < y else 'behind'}"
        dim(ax, (oy + h.front_y(h.z_band_top), oz + h.z_band_top - 2), (oy + h.y_band_top, oz + h.z_band_top - 2),
            f"band face {abs(recess):.1f} {'behind' if recess >= 0 else 'ahead of'} the front", (36, -7), size=7)
        dim(ax, (oy + h.front_y(h.z_sill), oz + h.z_sill + 2), (oy + h.y_band_foot, oz + h.z_sill + 2), f"ledge {abs(h.y_band_foot - h.front_y(h.z_sill)):.1f}", (26, 0), size=7)
        dim(ax, (oy + h.y_band_top - d.hood_rail_proud, oz + h.z_rail_top + 2), (oy + h.y_marquee_bottom, oz + h.z_rail_top + 2),
            f"edge {h.y_marquee_bottom - h.y_band_top + d.hood_rail_proud:.1f}", (-16, 6), size=7)
        soffit = h.y_marquee_top - h.front_y(h.z_open_top)
        dim(ax, (oy + h.front_y(h.z_open_top), oz + h.z_open_top - 3), (oy + h.y_marquee_top, oz + h.z_open_top - 3),
            f"marquee {abs(soffit):.1f} {'behind' if soffit >= 0 else 'ahead of'} the top bar", (40, -7), size=7)
        note(ax, (oy + 22, oz + 45), f"speaker form {d.speaker_proud:.0f} proud, front upright:\nat its top (z {zt:.0f}) {ahead(h.front_y(zt))} the front,\n"
             f"at its foot (z {zb:.0f}) {ahead(h.front_y(zb))} the front;\n{ahead(h.front_y(0.0))} the foot of the front", size=7)
        ax.legend(loc="lower right", fontsize=6.5)
    fig.suptitle("Hood band, upright: three places in depth (side section through a speaker, x = "
                 f"{x:.0f}; the marquee {pr.marquee_window(d0, h0)[0]:.0f} x {d0.marquee_h:.0f}, upright, moves with the band: an edge of {d0.hood_marquee_edge:.0f} on the lip)", fontsize=12)
    save(fig, "hood-band-options", os.path.join(CAD, "out", "shell-bp", "compare"), svg=False)


# the screen face of revision 4, before the screen went down: the band below the bezel and the strip above it
REV4_BAND, REV4_BROW = 52.0, 20.0


def screen_face_numbers(d: Blueprint) -> dict[str, float]:
    """The strips above and below the bezel, and what the tuck leaves beside the bezel's top corner in front view."""
    fr = pr.front(d)
    z = fr.on_rail(d, d.bezel_s1)[1]
    brow = [p for q in pr.faces(d)["FB3"].polys for p in q]
    lo, hi = min(brow, key=lambda p: p[2]), max(brow, key=lambda p: p[2])
    return {"band": d.band_len, "brow": d.brow_ledge, "plain": math.dist(lo[1:], hi[1:]), "z_top": z,
            "gap": d.side_x(z) - d.bezel_w / 2, "land": d.side_x(z) - d.edge_in - d.bezel_w / 2 - d.panel_gap}


def screen_drop_options() -> None:
    """The screen face in front elevation for three drops of the bezel, the window and the screen down the face, side
    by side to one scale. Each drop is measured from revision 4 (band_len 52, brow_ledge 20); the body top stays."""
    d0 = Blueprint()
    drops = (8.0, REV4_BAND - d0.band_len, 16.0)
    fig, axes = plt.subplots(1, 3, figsize=(19, 5.6))
    extent = (-262.0, 262.0, 80.0, 445.0)
    for ax, drop in zip(axes, drops):
        d = replace(d0, band_len=REV4_BAND - drop, brow_ledge=REV4_BROW + drop)
        tri, ids = triangles_of(pr.faces(d))
        built = " (built)" if abs(d.band_len - d0.band_len) < 1e-9 else ""
        n = screen_face_numbers(d)
        show(ax, raster(tri, ids, VIEWS["front"], extent, px_per_mm=4.0, closed=False), "white",
             f"drop {drop:.0f}{built}: strip above {n['brow']:.0f}, strip below {n['band']:.0f}")
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
        hw, bw = d.width / 2, d.bezel_w / 2
        ax.plot([hw - 40, hw + 6], [d.tuck_z0, d.tuck_z0], color=BLUE, lw=0.8, ls="--", zorder=50)
        note(ax, (hw - 150, d.tuck_z0 - 10), f"tuck starts, z {d.tuck_z0:.0f}", size=7)
        z = n["z_top"]
        dim(ax, (bw, z + 4), (d.side_x(z), z + 4), f"{n['gap']:.1f}", (-22, 7), size=7)
        dim(ax, (bw + d.panel_gap, z - 5), (d.side_x(z) - d.edge_in, z - 5), f"land {n['land']:.1f}", (-34, -6), size=7)
        top = d.face(d.top_s)[1]
        su, cu = d.u
        dim(ax, (-60, d.face(d.bezel_s1)[1]), (-60, top), f"{n['brow']:.0f} on the face\n{n['plain']:.1f} plain", (-34, 0), size=7)
        dim(ax, (-60, d.face(d.bezel_s0 - d.band_len)[1]), (-60, d.face(d.bezel_s0)[1]), f"{n['band']:.0f} on the face", (-30, 0), size=7)
        note(ax, (-250, 92), f"bezel top z {z:.1f}; image centre z {d.face(d.image_s)[1]:.1f}", size=7)
    fig.suptitle("Screen face, front elevation: the bezel, the window and the screen moved down the face from revision 4 "
                 f"(band below {REV4_BAND:.0f}, strip above {REV4_BROW:.0f}). The body top, the rails and the hood stay. "
                 "Gap: bezel top corner to the side outline. Land: the rail land at that corner.", fontsize=10.5)
    fig.tight_layout()
    save(fig, "screen-drop-options", os.path.join(CAD, "out", "shell-bp", "compare"), svg=False)


# ---------- sheet 09: the hardware in the shell (from the fit study) ----------

FIT_DATA = os.path.join(CAD, "out", "shell-bp", "fit", "sections.json")
FIT_COLOUR = {"Monitor": "#3a4f80", "MonitorRoom": "#7a8fc0", "Cables": "#d07020", "Compute": "#2f7a3a", "PSU": "#6b6f78", "CableBundle": "#a07020",
              "Hub": "#6a4fa0", "Speaker": "#c04040", "Marquee": "#c08a10", "USB": "#2070c0", "Panel": "#202020"}
FIT_LABEL = {"MonitorRoom": "any 16:10 monitor", "Cables": "monitor cables", "Panel": "control panel", "CableBundle": "stowed cables",
             "Compute": "BC-250", "PSU": "power supply", "USB": "USB sockets"}
# what the rear view shows: the items near the rear door
FIT_REAR = ("Compute", "PSU", "CableBundle", "Cables", "Speaker", "Marquee")
# clearances at most this wide get a dimension, in the view whose plane is nearest to them, when it is this near
FIT_DIM_MAX, FIT_DIM_NEAR = 15.0, 60.0


def fit_items(ax: Axes, items: list[dict], flip: bool = False) -> None:
    """Hardware solid, keep-out zones dashed, one label for each item."""
    seen: dict[str, list[np.ndarray]] = {}
    for r in items:
        c = FIT_COLOUR.get(r["group"], INK)
        for line in r["lines"]:
            p = np.array(line)
            if flip:
                p[:, 0] = -p[:, 0]
            ax.plot(p[:, 0], p[:, 1], color=c, lw=1.1 if r["role"] == "hardware" else 0.8, ls="-" if r["role"] == "hardware" else "--", zorder=60)
            seen.setdefault(r["group"], []).append(p)
    for name, ps in seen.items():
        allp = np.concatenate(ps)
        ax.text(*allp.mean(axis=0), FIT_LABEL.get(name, name), fontsize=6.5, color=FIT_COLOUR.get(name, INK), ha="center", va="center", zorder=70,
                bbox=dict(fc="white", ec="none", pad=0.3, alpha=0.75))


def fit_shell(ax: Axes, outer: list, cavity: list, flip: bool = False) -> None:
    k = -1.0 if flip else 1.0
    for line in cavity:
        p = np.array(line)
        ax.fill(k * p[:, 0], p[:, 1], color="#eef3f8", zorder=1)
        ax.plot(k * p[:, 0], p[:, 1], color="#7a8ca0", lw=0.6, zorder=5)
    for line in outer:
        p = np.array(line)
        ax.plot(k * p[:, 0], p[:, 1], color=INK, lw=0.9, zorder=6)


def fit_dims(ax: Axes, rows: list[dict], axis: int, at: float, axes: tuple[int, int], planes: dict) -> None:
    """The tight clearances that lie nearest to this plane, as dimensions."""
    done = set()
    for r in rows:
        for key, pts, other in (("skin_gap", "skin_points", "skin"), ("neighbour_gap", "neighbour_points", r["neighbour"])):
            g, (a, b) = r[key], r[pts]
            if a is None or not 0.0 < g <= FIT_DIM_MAX:
                continue
            mid = [(a[i] + b[i]) / 2 for i in range(3)]
            nearest = min(planes.values(), key=lambda pl: abs(mid[pl["axis"]] - pl["at"]) if pl["axis"] != 1 else math.inf)
            if nearest["axis"] != axis or nearest["at"] != at or abs(mid[axis] - at) > FIT_DIM_NEAR:
                continue
            tag_ = tuple(sorted((r["item"], other))) + (round(g, 1),)
            if tag_ in done:
                continue
            done.add(tag_)
            p, q = (a[axes[0]], a[axes[1]]), (b[axes[0]], b[axes[1]])
            dim(ax, p, q, f"{g:.1f}", (8, 6), size=6.5)


def sheet_fit() -> None:
    data = json.load(open(FIT_DATA))
    secs, rear, rows = data["sections"], data["rear"], data["clearances"]
    fig = plt.figure(figsize=(24, 16))
    grid = fig.add_gridspec(2, 3, hspace=0.18, wspace=0.12)
    names = list(secs)
    places = [grid[0, 0], grid[0, 1], grid[1, 0], grid[1, 1], grid[1, 2]]
    for name, place in zip(names, places):
        s = secs[name]
        ax = fig.add_subplot(place)
        axes = tuple(i for i in range(3) if i != s["axis"])
        fit_shell(ax, s["outer"], s["cavity"])
        fit_items(ax, s["items"])
        fit_dims(ax, rows, s["axis"], s["at"], axes, secs)
        labels = {0: "x (mm)", 1: "y, from the deck front (mm)", 2: "z, above the desk (mm)"}
        pts = [p for l in s["outer"] for p in l]
        if name == names[0]:
            for r in data["sight"]:
                for edge in ("top", "bottom"):
                    ax.plot([r["eye_y"], r[edge][0]], [r["eye_z"], r[edge][1]], color=BLUE, lw=0.6, ls=":", zorder=55)
                ax.plot(r["eye_y"], r["eye_z"], "o", color=BLUE, ms=3, zorder=56)
                ax.text(r["eye_y"] - 6, r["eye_z"], f"{r['person']}\n{r['to_normal_deg']:.0f} deg to the normal", fontsize=6.5, color=BLUE, ha="right", va="center")
                pts.append((r["eye_y"] - 120, r["eye_z"]))
        frame(ax, f"{name} ({'xyz'[s['axis']]} = {s['at']:.0f})", (min(p[0] for p in pts) - 15, max(p[0] for p in pts) + 15),
              (min(p[1] for p in pts) - 15, max(p[1] for p in pts) + 15), labels[axes[0]], labels[axes[1]])
    ax = fig.add_subplot(grid[0, 2])
    for k, lines in rear["outer"].items():
        for line in lines:
            p = np.array(line)
            ax.plot(-p[:, 0], p[:, 1], color=INK if k.startswith("lower") else "#888", lw=0.9, zorder=6)
    for r in rear["items"]:
        if r["group"] not in FIT_REAR:
            continue
        x0, z0, x1, z1 = r["box"]
        c = FIT_COLOUR.get(r["group"], INK)
        ax.plot([-x0, -x1, -x1, -x0, -x0], [z0, z0, z1, z1, z0], color=c, lw=1.0 if r["role"] == "hardware" else 0.7,
                ls="-" if r["role"] == "hardware" else "--", zorder=40)
    door = rear["door"]
    ax.plot([-door["x0"], -door["x1"], -door["x1"], -door["x0"], -door["x0"]], [door["z0"], door["z0"], door["z1"], door["z1"], door["z0"]],
            color=RED, lw=1.4, ls="-.", zorder=50)
    dim(ax, (-door["x0"], door["z1"] + 12), (-door["x1"], door["z1"] + 12), f"door opening {door['w']:.0f} wide (proposed)", (0, 7))
    dim(ax, (-door["x1"] - 14, door["z0"]), (-door["x1"] - 14, door["z1"]), f"{door['h']:.0f}", (-12, 0), turn=90)
    allp = np.concatenate([np.array(l) for ls_ in rear["outer"].values() for l in ls_])
    frame(ax, "rear view, seen from behind: the lower rear wall (black), the upper rear (grey), the items\nnear the rear as boxes (BC-250, power supply, cables, speakers, marquee), the proposed door opening (red)",
          (-allp[:, 0].max() - 30, -allp[:, 0].min() + 30), (allp[:, 1].min() - 15, allp[:, 1].max() + 15), "x, seen from behind (mm)", "z, above the desk (mm)")
    fig.suptitle(f"Blueprint 09: the hardware in the shell, with a skin of {data['wall_t']:g} (fit study). Hardware solid, keep-out zones dashed, the cavity shaded;\n"
                 f"the clearances of {FIT_DIM_MAX:.0f} mm and less are dimensioned in the view nearest to them", fontsize=13, y=0.995)
    save(fig, "09-hardware")


# ---------- the 3D reference model (a mesh; third-party material, drawn only below cad/out) ----------

K_DIR = os.path.join(CAD, "vendor", "mini-new-astro-city", "assembled")
K_W = 270.0
BEZEL_N = (0.0, -math.cos(math.radians(32.5)), math.sin(math.radians(32.5)))


def load_stl(path: str) -> np.ndarray:
    """Triangles of a binary STL as an array (n, 3, 3)."""
    data = open(path, "rb").read()
    n = struct.unpack_from("<I", data, 80)[0]
    raw = np.frombuffer(data, dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]), count=n, offset=84)
    return raw["v"].astype(float)


def classify(part: str, tri: np.ndarray) -> np.ndarray:
    """A face ID for every triangle of a part of the reference model, by its normal and position ('' = inside or unnamed)."""
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    c = tri.mean(axis=1)
    nx, ny, nz = n.T
    x, y, z = c.T
    ax, out = np.abs(x), nx * np.sign(x)
    ids = np.full(len(tri), "", dtype=object)

    def put(mask: np.ndarray, fid: str) -> None:
        ids[mask & (ids == "")] = fid

    if part == "deck":
        put((nz > 0.95) & (z > 49.5), "DK1")
        put((nz > 0.5) & (nz < 0.9) & (z > 38), "DK3")
        put((nz < -0.95) & (z < 0.5), "FL1")
        vertical = np.abs(nz) < 0.2
        put(vertical & (out > 0.97) & (ax > 134.5), "DK7")
        put(vertical & (ny < -0.2) & (out > 0.08) & (ax > 100) & (y < 35), "DK6")
        put(vertical & (ny < -0.9) & (ax < 54) & (y < 1.0), "DK4")
        put(vertical & (ny < -0.9) & (y < 5.0), "DK5")
    elif part == "control_panel":
        put((nz > 0.95) & (z > 49), "CP1")
    elif part == "bezel":
        front, along = n @ np.array(BEZEL_N), c @ np.array(BEZEL_N)
        put((front > 0.98) & (along > along[front > 0.98].max() - 0.5), "BZ1")
        put(np.abs(front) < 0.3, "BZ3")
    elif part == "speaker_plate":
        put(n @ np.array(BEZEL_N) > 0.9, "FB3")
        put(nz > 0.9, "FB4")
    elif part == "body":
        put((nz < -0.95) & (z < 0.5), "FL1")
        put((nz > 0.95) & (z > 236), "FB4")
        put((out > 0.97) & (ax > 134.5), "RL4")
        put((out > 0.97) & (ax > 114.5) & (ax < 115.5) & (y > 190), "RB1")
        put((out > 0.5) & (out < 0.9) & (ny < -0.05) & (ax > 124) & (y < 262), "RL3")
        put((np.abs(nx) < 0.05) & (ny < -0.05) & (ax > 119.9) & (ax < 124.6) & (y < 262) & (z > 49), "RL1")
        put((out < -0.97) & (ax > 119.5) & (ax < 120.5) & (y < 245), "RL5")
        put((out > 0.15) & (ny > 0.15) & (ax > 114) & (y > 170) & (y < 337), "RB2")
        put((ny > 0.2) & (nz < -0.2) & (y > 290) & (z < 50), "RB8")
        put((ny > 0.9) & (y > 337) & (z < 172), "RB3")
        put((ny > 0.9) & (nz > 0.05) & (y > 318) & (z > 171), "RB5")
        put((np.abs(nx) < 0.05) & (ny < -0.3) & (nz > 0.3) & (ax < 120) & (z > 45) & (z < 66) & (y < 120), "FB2")
    elif part == "hood":
        put((nz > 0.97) & (z > 316), "HC7")
        put((np.abs(nx) < 0.05) & (ny < -0.5) & (nz > 0.5) & (z > 305) & (ax < 112), "HC4")
        put((np.abs(nx) < 0.05) & (ny < -0.9) & (z > 299) & (z < 307) & (ax < 112), "HC2")
        put((np.abs(nx) < 0.05) & (nz < -0.9) & (z > 299) & (z < 303), "HC10")
        put((ny > 0.9) & (y > 300), "HC9")
        put((np.abs(ny) < 0.05) & (out > 0.2) & (ax > 100) & (z < 298), "HC5")
        put((np.abs(ny) < 0.05) & (out > 0.2) & (ax > 90) & (z >= 298), "HC6")
        put((out > 0.2) & (ny < -0.2) & (ax > 85), "HC4")
        put((np.abs(nx) < 0.05) & (ny < -0.3) & (ax > 105) & (y < 266), "HC1")
        put((out < -0.9) & (ax > 100) & (ax < 121) & (y < 300), "HC11")
    elif part == "hood_band":
        put((np.abs(nx) < 0.05) & (ny < -0.95) & (y < 231), "SP1")
        put((np.abs(nx) < 0.05) & (ny < -0.95) & (z > 288), "MQ1")
        put((np.abs(nx) < 0.05) & (ny < -0.6) & (ny > -0.8) & (nz > 0.6), "HB1")
        put((y < 262) & ((np.abs(nx) > 0.9) | (np.abs(nz) > 0.9)) & (ax > 44) & (ax < 102), "SP3")
    return ids


def load_reference() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """All triangles of the reference model with a face ID and a part index for each."""
    manifest = json.load(open(os.path.join(K_DIR, "manifest.json")))
    tris, ids, parts = [], [], []
    for i, (part, entry) in enumerate(manifest.items()):
        t = load_stl(os.path.join(K_DIR, entry["file"]))
        tris.append(t)
        ids.append(classify(part, t))
        parts.append(np.full(len(t), i))
    return np.concatenate(tris), np.concatenate(ids), np.concatenate(parts)


def ear_clip(poly: np.ndarray) -> list[tuple[int, int, int]]:
    """Triangles of a planar polygon (n, 3) that may be concave, as index triples (ear clipping)."""
    normal = np.zeros(3)
    for a, b in zip(poly, np.roll(poly, -1, axis=0)):
        normal += np.cross(a, b)
    keep = [i for i in range(3) if i != int(np.argmax(np.abs(normal)))]
    pts = poly[:, keep]
    if _area(pts) < 0:
        pts = pts * np.array([1.0, -1.0])
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    idx = list(range(len(pts)))
    out = []
    guard = 0
    while len(idx) > 3 and guard < 20000:
        guard += 1
        for k in range(len(idx)):
            i, j, l = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            turn = cross(pts[i], pts[j], pts[l])
            if turn < -1e-9:
                continue
            if turn > 1e-9 and any(cross(pts[i], pts[j], pts[m]) > 1e-9 and cross(pts[j], pts[l], pts[m]) > 1e-9 and cross(pts[l], pts[i], pts[m]) > 1e-9
                                   for m in idx if m not in (i, j, l)):
                continue
            if turn > 1e-9:
                out.append((i, j, l))
            idx.pop(k)
            break
        else:
            break
    if len(idx) == 3:
        out.append(tuple(idx))
    return out


def triangles_of(faces: dict[str, pr.Face]) -> tuple[np.ndarray, np.ndarray]:
    """The polygons of the target's faces as triangles, with their IDs."""
    tris, ids = [], []
    for face in faces.values():
        for p in face.polys:
            poly = np.array(p, float)
            for i, j, l in ([(0, 1, 2), (0, 2, 3)] if len(poly) == 4 else ear_clip(poly)):
                tris.append(poly[[i, j, l]])
                ids.append(face.id)
    return np.array(tris, float), np.array(ids, dtype=object)


@dataclass
class Raster:
    ids: np.ndarray
    depth: np.ndarray
    normal: np.ndarray
    extent: tuple[float, float, float, float]
    names: list[str]

    def edges(self) -> np.ndarray:
        """Where a line belongs: a change of face, a crease, or a jump in depth."""
        e = np.zeros(self.ids.shape, bool)
        cover = self.ids < len(self.names)
        for axis in (0, 1):
            other = np.roll(self.ids, 1, axis=axis)
            e |= self.ids != other
            cosang = (self.normal * np.roll(self.normal, 1, axis=axis)).sum(-1)
            e |= cover & np.roll(cover, 1, axis=axis) & (cosang < math.cos(math.radians(24)))
            lap = np.roll(self.depth, 1, axis=axis) - 2 * self.depth + np.roll(self.depth, -1, axis=axis)
            e |= cover & np.roll(cover, 1, axis=axis) & np.roll(cover, -1, axis=axis) & (np.abs(lap) > 1.2)
        e[0, :] = e[-1, :] = e[:, 0] = e[:, -1] = False
        return e

    def image(self, fill: str, thick: int = 1) -> np.ndarray:
        """An RGB picture: 'white' (line drawing) or 'colour' (flat false colours), with the lines in ink."""
        rgb = np.ones((*self.ids.shape, 3))
        if fill == "colour":
            table = np.array([colour(n) if n else (0.82, 0.82, 0.84) for n in self.names] + [(1.0, 1.0, 1.0)])
            rgb = table[self.ids]
        from scipy import ndimage
        rgb[ndimage.binary_dilation(self.edges(), iterations=thick)] = (0.11, 0.11, 0.12)
        return rgb

    def spots(self, min_px: float = 5.0, right_only: bool = True) -> dict[str, tuple[tuple[float, float], float]]:
        """For each face that shows: the point deepest inside its largest visible region, and how far inside it is (mm)."""
        from scipy import ndimage
        x0, x1, y0, y1 = self.extent
        s = self.ids.shape[1] / (x1 - x0)
        out = {}
        for k, name in enumerate(self.names):
            if not name:
                continue
            mask = self.ids == k
            if right_only:
                half = np.zeros_like(mask)
                half[:, int((0.0 - x0) * s) - 2:] = True
                if (mask & half).sum() > 0.2 * mask.sum():
                    mask &= half
            lab, count = ndimage.label(mask)
            if not count:
                continue
            sizes = ndimage.sum(mask, lab, range(1, count + 1))
            dist = ndimage.distance_transform_edt(lab == int(np.argmax(sizes)) + 1)
            r, c = np.unravel_index(int(np.argmax(dist)), dist.shape)
            if dist[r, c] >= 1.5:
                out[name] = ((x0 + (c + 0.5) / s, y1 - (r + 0.5) / s), float(dist[r, c]) / s)
        return out


def raster(tri: np.ndarray, ids: np.ndarray, view: View, extent: tuple[float, float, float, float], px_per_mm: float = 3.0, closed: bool = True) -> Raster:
    """A z-buffer picture of triangles in an orthographic view: for each pixel the face ID, the depth and the normal.

    closed: the triangles are a closed mesh with outward normals, so those that face away are left out. For
    an open skin with mixed winding (the target's faces) every triangle is drawn and its normal turned to the viewer.
    """
    r, u, t = (np.array(v, float) for v in (view.right, view.up, view.toward))
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    names = sorted(set(ids))
    index = {name: i for i, name in enumerate(names)}
    x0, x1, y0, y1 = extent
    w, h = int(round((x1 - x0) * px_per_mm)), int(round((y1 - y0) * px_per_mm))
    px = np.stack([(tri @ r - x0) * px_per_mm, (y1 - tri @ u) * px_per_mm], axis=-1)
    dz = tri @ t
    idm = np.full((h, w), -1, int)
    dm = np.full((h, w), -np.inf)
    tm = np.full((h, w), -1, int)
    facing = n @ t
    if not closed:
        n = n * np.where(facing < 0, -1.0, 1.0)[:, None]
    for i in np.nonzero((facing if closed else np.abs(facing)) > 1e-4)[0]:
        (ax, ay), (bx, by), (cx, cy) = px[i]
        c0, c1 = max(int(math.floor(min(ax, bx, cx))), 0), min(int(math.ceil(max(ax, bx, cx))), w)
        r0, r1 = max(int(math.floor(min(ay, by, cy))), 0), min(int(math.ceil(max(ay, by, cy))), h)
        det = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if c1 <= c0 or r1 <= r0 or abs(det) < 1e-9:
            continue
        gx = np.arange(c0, c1) + 0.5
        gy = (np.arange(r0, r1) + 0.5)[:, None]
        l0 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / det
        l1 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / det
        l2 = 1.0 - l0 - l1
        depth = l0 * dz[i, 0] + l1 * dz[i, 1] + l2 * dz[i, 2]
        win = dm[r0:r1, c0:c1]
        hit = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6) & (depth > win)
        win[hit] = depth[hit]
        idm[r0:r1, c0:c1][hit] = index[ids[i]]
        tm[r0:r1, c0:c1][hit] = i
    normal = np.where(tm[..., None] >= 0, n[np.clip(tm, 0, None)], 0.0)
    return Raster(np.where(idm >= 0, idm, len(names)), np.where(np.isfinite(dm), dm, 0.0), normal, extent, names)


def show(ax: Axes, ras: Raster, fill: str, title: str, thick: int = 1) -> None:
    ax.imshow(ras.image(fill, thick), extent=ras.extent, interpolation="antialiased", zorder=1)
    ax.set_title(title, fontsize=11)
    ax.set_aspect("equal")
    ax.axis("off")


def label_raster(ax: Axes, ras: Raster, placed: dict[str, tuple[float, ...] | None] | None = None, size: float = 6.5) -> None:
    """Put the ID of every face that shows on the picture: inside the face when it has room, else beside it with a leader."""
    placed = placed or {}
    x0, x1, y0, y1 = ras.extent
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for name, (at, room) in ras.spots().items():
        if name in placed:
            if placed[name] is not None:
                tag(ax, placed[name][:2], name, to=placed[name][2:] or at, size=size)
        elif room * 72 / 25.4 > 0.0 and room > 3.2:
            tag(ax, at, name, size=size)
        else:
            v = np.array([at[0] - cx, at[1] - cy])
            v = v / (np.linalg.norm(v) + 1e-9) * 22.0
            tag(ax, (at[0] + v[0], at[1] + v[1]), name, to=at, size=size)


K_VIEWS = {"front": (-160, 160, -25, 345), "side": (-30, 370, -25, 345), "top": (-160, 160, -25, 345), "rear": (-160, 160, -25, 345)}


def reference_elevations(tri: np.ndarray, ids: np.ndarray) -> dict[str, Raster]:
    pics = {key: raster(tri, ids, VIEWS[key], K_VIEWS[key]) for key in K_VIEWS}
    fig, axes = plt.subplots(2, 2, figsize=(15, 15.5))
    for ax, key in zip(axes.ravel(), K_VIEWS):
        show(ax, pics[key], "white", VIEWS[key].name.capitalize())
    a = axes[0, 0]
    dim(a, (-135, -12), (135, -12), "width W = 270.0", (0, -7))
    dim(a, (-96.25, 326), (96.25, 326), "hood top flat 192.5 (0.713 W)", (0, 6))
    dim(a, (145, 0), (145, 50), "50.0", (9, 0))
    dim(a, (145, 50), (145, 247.25), "seam 247.25 (0.916 W)", (5, 0), turn=90)
    dim(a, (145, 247.25), (145, 316.4), "hood 69.1 (0.256 W)", (5, 0), turn=90)
    dim(a, (-146, 0), (-146, 316.4), "height 316.4 (1.172 W)", (-5, 0), turn=90)
    a = axes[0, 1]
    dim(a, (0, -12), (338.1, -12), "depth 338.1 (1.252 W)", (0, -7))
    dim(a, (0, 326), (102.55, 326), "deck 102.6 (0.380 W)", (0, 6))
    dim(a, (233.3, 326), (323.7, 326), "hood 90.4 (0.335 W)", (0, 6))
    dim(a, (-14, 0), (-14, 50), "50", (-8, 0))
    dim(a, (352, 0), (352, 316.4), "316.4", (6, 0), turn=90)
    note(a, (20, 190), "screen face reclined 32.5 deg;\ncheek front edge: one arc R 311.6", to=(165, 150), size=7)
    a = axes[1, 0]
    dim(a, (-135, -12), (135, -12), "270.0", (0, -7))
    dim(a, (-115, 348), (115, 348), "rear body 230.0 (0.852 W)", (0, -7))
    dim(a, (146, 0), (146, 338.1), "338.1", (6, 0), turn=90)
    a = axes[1, 1]
    dim(a, (-135, -12), (135, -12), "270.0", (0, -7))
    dim(a, (-115, 30), (115, 30), "230.0", (0, 6))
    fig.suptitle("3D reference model (MakerWorld Mini New Astro City, 9.7 inch): elevations, exact, one scale (mm)", fontsize=13, y=0.995)
    fig.tight_layout()
    save(fig, "k-01-elevations", RECON, svg=False)
    return pics


K_PLACED: dict[str, dict[str, tuple[float, ...] | None]] = {
    "front": {"RL3": (152, 150, 129.7, 150), "RL1": (152, 175, 122.2, 190), "RL5": (152, 200, 119.2, 215), "RL4": None, "HC4": (152, 300, 124, 280),
              "HC1": (152, 262, 119, 255), "HC5": None, "HC6": None, "DK3": (152, 45), "DK6": (152, 20), "DK7": None, "FB2": (-150, 58, -60, 58),
              "FB3": (-150, 244, -60, 244), "HC2": (-150, 303, -60, 303), "MQ1": (-150, 290, -60, 294), "HC7": None, "HC10": None, "HC11": None, "SP3": None,
              "BZ3": (-150, 100, -100, 100), "DK1": None, "RB2": None, "FB4": None},
    "side": {"RL3": (150, 230, 205, 215), "RL1": None, "DK3": (60, 62, 60, 46), "DK6": (-18, 20), "DK5": None, "DK4": None, "HC4": (215, 300, 247, 285), "HC1": None,
             "HC6": (300, 330, 290, 308), "HC7": None, "RB8": (350, 20), "FB4": None, "HC9": (350, 280, 322, 280), "RB5": (352, 205, 334, 205), "RB3": (352, 100, 338, 100), "SP3": None,
             "SP1": None, "HB1": None, "MQ1": None},
    "top": {"RL3": (152, 150, 130, 150), "RL1": (152, 175, 122, 175), "RL4": None, "DK3": (152, 60), "DK7": None, "DK6": None, "HC4": (152, 262, 110, 263),
            "HC6": (152, 300, 123, 300), "HC5": (152, 285, 131, 285), "HC1": (152, 245, 119, 242), "FB3": None, "SP3": (-150, 236, -90, 236), "SP1": None,
            "FB2": (-150, 108, -60, 108), "MQ1": None, "HC2": None, "RB2": (152, 215, 126, 215), "RB1": None, "RL5": None, "BZ3": None, "FB4": None, "HC9": None, "RB5": None},
    "rear": {"HC5": (-152, 270, -131, 270), "HC6": (-152, 305, -120, 308), "RB2": (-152, 120, -126, 120), "RL4": None, "RB8": (0, 22), "FL1": None, "HC7": None,
             "FB4": None, "DK7": None, "RB1": None, "BZ3": None, "BZ1": None}}


def reference_face_map(pics: dict[str, Raster]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(15, 15.5))
    for ax, key in zip(axes.ravel(), K_VIEWS):
        show(ax, pics[key], "colour", VIEWS[key].name.capitalize())
        label_raster(ax, pics[key], K_PLACED.get(key))
    fig.suptitle("3D reference model: face map (the same IDs as the target; grey = inside faces and unnamed details)", fontsize=13, y=0.995)
    fig.tight_layout()
    save(fig, "k-02-face-map", RECON, svg=False)


PART_COLOUR = {"body": "#f2d28a", "deck": "#8fb8de", "control_panel": "#b98fe0", "bezel": "#5a5a66", "speaker_plate": "#c9c9cf", "hood": "#9fd6b8", "hood_band": "#e79ab8"}


def fill_slice(ax: Axes, data: dict, plane: str, axes: tuple[int, int], parts: tuple[str, ...] | None = None) -> None:
    """Fill the loops of one plane of slices-k.json, each part in its colour (even-odd, so pockets stay empty)."""
    for part, cuts in data["parts"].items():
        if parts is not None and part not in parts:
            continue
        verts, codes = [], []
        for loop in cuts.get(plane, []):
            pts = [(p[axes[0]], p[axes[1]]) for p in loop]
            if len(pts) < 3:
                continue
            verts += pts + [pts[0]]
            codes += [MplPath.MOVETO] + [MplPath.LINETO] * (len(pts) - 1) + [MplPath.CLOSEPOLY]
        if verts:
            from matplotlib.patches import PathPatch
            ax.add_patch(PathPatch(MplPath(verts, codes), fc=PART_COLOUR[part], ec=INK, lw=0.7, zorder=5))
    ax.set_aspect("equal")


def tags(ax: Axes, items: list[tuple[str, tuple[float, float], tuple[float, float] | None]], size: float = 7.0) -> None:
    for fid, at, to in items:
        tag(ax, at, fid, to=to, size=size)


def reference_sections(data: dict) -> None:
    fig = plt.figure(figsize=(21, 13.5))
    grid = fig.add_gridspec(2, 4, width_ratios=[2.2, 1, 1, 1], hspace=0.22, wspace=0.2, top=0.92, bottom=0.05, left=0.04, right=0.99)
    a = fig.add_subplot(grid[:, 0])
    fill_slice(a, data, "centre", (1, 2))
    frame(a, "Side section at the centre line (x = 0.3); each part in its colour", (-25, 365), (-20, 345), "y (mm)", "z (mm)")
    tags(a, [("DK4", (-14, 25), (0, 25)), ("DK3", (-12, 58), (5, 45)), ("DK1", (12, 66), (13, 50)), ("CP1", (60, 66), (60, 50)), ("FB2", (88, 80), (110, 58)),
             ("BZ1", (120, 165), (163, 130)), ("FB3", (205, 262), (238, 245)), ("HB1", (215, 285), (250, 262)), ("MQ1", (240, 310), (277, 296)), ("HC2", (236, 322), (261, 303)),
             ("HC4", (262, 334), (266, 311)), ("HC7", (290, 334), (290, 316.4)), ("HC9", (350, 285), (321, 285)), ("RB5", (352, 205), (331, 205)), ("RB3", (352, 110), (338, 110)),
             ("RB8", (352, 22), (325, 22)), ("FL1", (200, -12), (200, 0)), ("FB4", (300, 232), (300, 247)), ("HC10", (300, 290), (285, 301))])
    dim(a, (0, -8), (338.1, -8), "338.1", (60, -6))
    dim(a, (-18, 0), (-18, 316.4), "316.4", (6, 0), turn=90)
    note(a, (30, 215), "screen face reclined 32.5 deg;\nhood band 44 deg: a knuckle of 11.5 deg at the seam;\nno sill, no ledge, no rail; the pods (dashed in the\nhood sheet) stand in front of the band", size=7)
    for part, c in PART_COLOUR.items():
        a.fill([], [], fc=c, ec=INK, lw=0.5, label=part.replace("_", " "))
    a.legend(loc="lower right", fontsize=7, frameon=False, ncol=2, bbox_to_anchor=(0.92, 0.02))
    cuts = [("A. through a hood leg (z = 275)", "hood_leg", (88, 142), (222, 330),
             [("HC1", (103, 246), (113, 253)), ("HC4", (134, 250), (121, 258)), ("HC5", (136, 290), (125.7, 290)), ("HC11", (97, 285), (109.8, 272)), ("HB1", (97, 275), (105, 265.5)),
              ("SP3", (112, 236), (100.9, 245)), ("HC9", (120, 326), (116, 316))]),
            ("B. through the cheek at mid screen (z = 155.5)", "screen", (88, 142), (140, 345),
             [("RL1", (112, 141), (122.2, 148.2)), ("RL3", (137, 146), (130, 154.5)), ("RL4", (139, 200), (135, 200)), ("RL5", (108, 162), (120, 165)), ("BZ1", (96, 172), (108, 178.9)),
              ("RB2", (137, 252), (126, 249)), ("RB1", (124, 300), (115, 300)), ("RB3", (108, 342), (108, 338.1))]),
            ("C. at the cheek foot (z = 60)", "foot", (88, 142), (100, 345),
             [("RL1", (112, 104), (122.2, 109.3)), ("RL3", (138, 110), (130, 115)), ("RL4", (139, 155), (135, 155)), ("RL5", (108, 125), (120, 130)), ("RB2", (137, 203), (126, 198)),
              ("RB1", (124, 280), (115, 280))]),
            ("D. through the deck's side (z = 30)", "deck", (88, 142), (-8, 235),
             [("DK7", (139, 60), (135, 60)), ("DK6", (136, 6), (128, 13.5)), ("RL4", (139, 140), (135, 140)), ("RB2", (137, 192), (126, 186)), ("RB1", (124, 215), (115, 212)),
              ("DK4", (100, -4), (100, 3))])]
    for i, (title, plane, xlim, ylim, items) in enumerate(cuts):
        b = fig.add_subplot(grid[:, i + 1]) if i < 3 else None
        if b is None:
            break
        fill_slice(b, data, plane, (0, 1))
        frame(b, title + "\nseen from above, right side", xlim, ylim, "x (mm)", "y (mm)")
        tags(b, items)
        b.axvline(135.0, color=RED, lw=0.5, ls=":")
    fig.suptitle("3D reference model: sections (exact slices of the meshes)", fontsize=13, y=0.985)
    save(fig, "k-03-sections", RECON, svg=False)
    fig, axes = plt.subplots(1, 3, figsize=(16, 11), gridspec_kw={"top": 0.9, "bottom": 0.06, "left": 0.05, "right": 0.99, "wspace": 0.25})
    for b, (title, plane, xlim, ylim, items) in zip(axes, [cuts[3], cuts[2], cuts[1]]):
        fill_slice(b, data, plane, (0, 1))
        frame(b, title + "\nseen from above, right side", xlim, ylim, "x (mm)", "y (mm)")
        tags(b, items, size=8)
        b.axvline(135.0, color=RED, lw=0.6, ls=":")
        b.text(135.6, ylim[0] + 3, "side plane x = 135", color=RED, fontsize=7, rotation=90, va="bottom")
    dim(axes[2], (120, 144), (124.4, 144), "land 4.4", (-9, -3), size=7)
    dim(axes[2], (124.4, 144), (135, 144), "facet 10.6 at 45 deg", (6, -3), size=7)
    dim(axes[2], (115, 270), (135, 270), "rear body 20 in", (0, 4), size=7)
    note(axes[0], (89, 228), "The deck's side DK7 and the side band RL4 are one plane (x = 135)\nfrom the deck's front corner back to the step RB2.", size=7.5)
    note(axes[2], (89, 320), "The cheek: land RL1 4.4, a 45 deg facet RL3 10.6 wide,\nthen the side band RL4, 78 deep here. The bezel sits\n30.6 behind the land (inner wall RL5).", size=7.5)
    fig.suptitle("3D reference model: what the rail is in section, and how it meets the deck (exact slices)", fontsize=13, y=0.975)
    save(fig, "k-04-rail-sections", RECON, svg=False)


K_HOOD_PLACED: dict[str, tuple[float, ...] | None] = {
    "HC4": (140, 322, 112, 308), "HC1": (146, 262, 116, 262), "HC5": None, "HC6": None, "HC2": (-140, 322, -60, 303.5), "MQ1": (-146, 296, -70, 294), "HC7": None,
    "HB1": (0, 256), "SP1": (146, 280, 99.5, 268), "SP3": (146, 240, 96, 251), "HC10": None, "HC11": None, "FB3": (-146, 240, -60, 243.5), "FB4": None,
    "RL1": None, "RL3": None, "RL4": None, "BZ1": None, "RL5": None, "BZ3": None}


def reference_hood(tri: np.ndarray, ids: np.ndarray, parts: np.ndarray, data: dict) -> None:
    names = list(json.load(open(os.path.join(K_DIR, "manifest.json"))))
    keep = np.isin(parts, [names.index(n) for n in ("hood", "hood_band", "speaker_plate", "body", "bezel")])
    ras = raster(tri[keep], ids[keep], VIEWS["front"], (-160, 160, 228, 332), px_per_mm=5.0)
    fig = plt.figure(figsize=(18, 14))
    grid = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.45], hspace=0.1, wspace=0.12, top=0.93, bottom=0.05, left=0.05, right=0.98)
    a = fig.add_subplot(grid[0, :])
    show(a, ras, "colour", "Front elevation of the hood")
    label_raster(a, ras, K_HOOD_PLACED, size=7.5)
    dim(a, (-133.6, 240), (133.6, 240), "hood at its seam 267.2 (0.990 W); body 270", (0, -4))
    dim(a, (-96.25, 323), (96.25, 323), "top flat 192.5 (0.713 W)", (0, 4))
    note(a, (-158, 275), "side: one arc R 348 (1.29 W),\nleaning 13.5 deg at the seam,\n22.3 deg under the corner", to=(-128, 275), size=7.5)
    note(a, (-158, 312), "top corner R 20.1 (0.074 W)", to=(-108, 309), size=7.5)
    note(a, (60, 232), "pods 55.1 x 39.8 (0.204 x 0.147 W), centres at +-73.5 (0.272 W), fronts upright", size=7.5)
    for i, (plane, title) in enumerate((("centre", "Side section of the hood at the centre line (x = 0.3)"), ("pod", "Side section of the hood through a pod (x = 73.5)"))):
        b = fig.add_subplot(grid[1, i])
        fill_slice(b, data, plane, (1, 2), ("hood", "hood_band", "speaker_plate", "body", "bezel"))
        frame(b, title, (205, 345), (225, 330), "y (mm)", "z (mm)")
        if i == 0:
            tags(b, [("HC2", (243, 310), (261.3, 303.5)), ("HC4", (252, 322), (266, 311)), ("HC7", (290, 324), (290, 316.4)), ("HC9", (336, 290), (321.5, 285)), ("HC10", (290, 292), (270, 301)),
                     ("MQ1", (262, 285), (277.2, 295)), ("HB1", (228, 272), (255, 266)), ("FB3", (222, 240), (236, 244)), ("FB4", (290, 238), (290, 247)), ("BZ1", (215, 232), (228, 234))], size=7.5)
            dim(b, (233.3, 250.5), (323.7, 250.5), "hood depth at the seam 90.4 (0.335 W)", (10, 4))
            dim(b, (330, 247.25), (330, 316.4), "69.1 (0.256 W)", (6, 0), turn=90)
            dim(b, (261.3, 306), (277.2, 306), "15.9", (0, 3.5), size=7)
            note(b, (207, 318), "top front edge: a facet 42 deg,\n14.25 long; top bar 15 thick;\ntop flat 30 deep", size=7.5)
            note(b, (207, 258), "band 44 deg, 58 on the slope", size=7.5)
            note(b, (300, 270), "rear face leans\nforward 16 deg", size=7.5)
        else:
            tags(b, [("SP1", (214, 268), (230.3, 268)), ("SP3", (245, 296), (245, 287.5)), ("HB1", (262, 262), (262, 273))], size=7.5)
            note(b, (207, 318), "pod front upright at y = 230.3,\n2.9 in front of the bezel's upper edge:\nthe pods are the foremost part of the hood", size=7.5)
    fig.suptitle("3D reference model: the hood (front elevation with face IDs; exact side sections)", fontsize=13, y=0.985)
    save(fig, "k-05-hood", RECON, svg=False)


def reference() -> None:
    tri, ids, parts = load_reference()
    pics = reference_elevations(tri, ids)
    reference_face_map(pics)
    data = json.load(open(os.path.join(RECON, "slices-k.json")))
    reference_sections(data)
    reference_hood(tri, ids, parts, data)


# ---------- the photographed references: face IDs on the photos ----------

def photos() -> None:
    """Draw the face readings of face-picks.json (below cad/out) on the reference photos."""
    from PIL import Image
    picks = json.load(open(os.path.join(RECON, "face-picks.json")))
    for sheet in picks["sheets"]:
        x0, y0, x1, y1 = sheet["box"]
        img = np.asarray(Image.open(os.path.join(REPO, sheet["photo"])).convert("RGB"))
        fig = plt.figure(figsize=(17, 17 * (y1 - y0) / (x1 - x0) * 0.72 + 1.2))
        ax = fig.add_axes([0.01, 0.02, 0.70, 0.93])
        ax.imshow(img, extent=(0, img.shape[1], img.shape[0], 0), zorder=1)
        ax.set_xlim(x0, x1)
        ax.set_ylim(y1, y0)
        ax.axis("off")
        for line in sheet["lines"]:
            pts = np.array(line["pts"], float)
            ax.plot(pts[:, 0], pts[:, 1], color="#00c8ff", lw=1.3, ls="--", zorder=20)
        rows = []
        for fid, at, to, status, text in sheet["tags"]:
            box = dict(boxstyle="round,pad=0.2", fc="white" if status == "e" else "#ffd98a", ec=INK, lw=0.6)
            arrow = dict(arrowstyle="-", color="#ff3b30", lw=0.9, shrinkA=0, shrinkB=0)
            if to is None:
                ax.text(*at, fid, fontsize=8, ha="center", va="center", bbox=box, zorder=30, family="DejaVu Sans Mono")
            else:
                ax.annotate(fid, xy=to, xytext=at, fontsize=8, ha="center", va="center", bbox=box, zorder=30, family="DejaVu Sans Mono",
                            arrowprops=arrow, annotation_clip=False)
            if text:
                rows.append((fid, "estimated" if status == "e" else "UNCERTAIN", text))
        side = fig.add_axes([0.72, 0.02, 0.27, 0.93])
        side.axis("off")
        y = 0.99
        side.text(0.0, y, "white = estimated, orange = uncertain;\ndashed = outlines picked by eye", fontsize=8.5, va="top", color=BLUE)
        y -= 0.06
        for fid, status, text in rows:
            import textwrap
            body = textwrap.fill(text, 46)
            side.text(0.0, y, fid, fontsize=8.5, va="top", family="DejaVu Sans Mono", weight="bold", color=RED if status == "UNCERTAIN" else INK)
            side.text(0.0, y - 0.022, body, fontsize=8, va="top")
            y -= 0.03 + 0.021 * (body.count("\n") + 1)
        fig.suptitle(sheet["title"], fontsize=13, y=0.985)
        fig.savefig(os.path.join(RECON, sheet["name"] + ".png"), dpi=110)
        plt.close(fig)
        print("draw_blueprint:", os.path.relpath(os.path.join(RECON, sheet["name"] + ".png"), REPO))


# ---------- the references and the target side by side ----------

def outline_of(ras: Raster) -> list[np.ndarray]:
    """The outer outline of a raster picture as polylines in millimetres."""
    x0, x1, y0, y1 = ras.extent
    mask = (ras.ids < len(ras.names)).astype(float)
    fig, ax = plt.subplots()
    cs = ax.contour(np.linspace(x0, x1, mask.shape[1]), np.linspace(y1, y0, mask.shape[0]), mask, levels=[0.5])
    lines = [seg for seg in cs.allsegs[0] if len(seg) > 40]
    plt.close(fig)
    return lines


def compare() -> None:
    d = Blueprint()
    faces = pr.faces(d)
    h = pr.hood(d)
    tri_t, ids_t = triangles_of(faces)
    tri_k, ids_k, _ = load_reference()
    side_t = raster(tri_t, ids_t, VIEWS["side"], (-40, 620, -20, 620), px_per_mm=2.0)
    side_k = raster(tri_k, ids_k, VIEWS["side"], (-30, 370, -20, 345), px_per_mm=3.0)
    trace = json.load(open(os.path.join(RECON, "trace-side-m.json")))
    mw, m = trace["W"], trace["points"]
    order = ["band_front_foot", "band_front_mid", "band_front_top", "hood_front_foot", "hood_front_top", "hood_top", "hood_r5", "hood_r4", "hood_r3", "hood_r2", "hood_r1",
             "hood_rear_foot", "rear_top", "rear_mid", "rear_facet_top", "floor_end", "floor_seam"]
    m_line = np.array([m[k] for k in order])
    m_step = np.array([m["step_foot"], m["step_top"]])
    m_deck = np.array([m["deck_top_seam"], m["deck_top_front"]])
    fig = plt.figure(figsize=(20, 13))
    grid = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.15], hspace=0.16, wspace=0.1, top=0.93, bottom=0.05, left=0.04, right=0.99)
    a = fig.add_subplot(grid[0, 0])
    show(a, side_k, "white", "3D reference model: side elevation (exact), W = 270", thick=2)
    a = fig.add_subplot(grid[0, 1])
    a.plot(m_line[:, 0], m_line[:, 1], color=INK, lw=1.4, marker="o", ms=3)
    a.plot(m_step[:, 0], m_step[:, 1], color=INK, lw=0.9, ls="--")
    a.plot(m_deck[:, 0], m_deck[:, 1], color=INK, lw=1.4, marker="o", ms=3)
    a.plot([m_deck[1][0] - 55, m_deck[1][0]], [m_deck[1][1]] * 2, color=INK, lw=0.9, ls=":")
    frame(a, f"Maker's mini: side elevation traced from photo-e (ESTIMATED, +-10 mm), W = {mw:.1f}", (-130, 270), (-20, 345), "y, from the deck's rear seam (mm)", "z (mm)")
    note(a, (-125, 300), "points picked on the right side and put\nin the side plane with the bezel's pose;\nthe deck front is not in this plane (dotted)", size=7)
    note(a, (60, 30), "step (crease), 28 deg", to=(100, 52), size=7)
    note(a, (-20, 150), "front edge of\nthe side band", to=(80, 105), size=7)
    note(a, (228, 120), "rear: uncertain", size=7, ha="left")
    a = fig.add_subplot(grid[0, 2])
    show(a, side_t, "white", f"Target (blueprint): side elevation, W = {d.width:.1f}", thick=2)
    b = fig.add_subplot(grid[1, 0:2])
    ya_t, ya_k = d.foot_y - d.bend_t, 102.55
    for line in outline_of(side_k):
        b.plot((line[:, 0] - ya_k) / K_W, line[:, 1] / K_W, color="#1f77b4", lw=1.3)
    for line in outline_of(side_t):
        b.plot((line[:, 0] - ya_t) / d.width, line[:, 1] / d.width, color=RED, lw=1.6)
    b.plot(m_line[:, 0] / mw, m_line[:, 1] / mw, color="#2ca02c", lw=1.3, marker="o", ms=3)
    b.plot(m_deck[:, 0] / mw, m_deck[:, 1] / mw, color="#2ca02c", lw=1.3, marker="o", ms=3)
    for c, label in (("#1f77b4", "3D reference model (exact)"), ("#2ca02c", "maker's mini (traced, estimated)"), (RED, "target (blueprint)")):
        b.plot([], [], color=c, lw=1.6, label=label)
    b.legend(loc="upper left", fontsize=8, frameon=False)
    frame(b, "Side outlines over each other: every length divided by the body width W, set on the deck's rear seam at the desk", (-0.55, 1.05), (-0.05, 1.3),
          "y / W", "z / W")
    c = fig.add_subplot(grid[1, 2])
    data = json.load(open(os.path.join(RECON, "slices-k.json")))
    loops = data["parts"]["hood"]["front_mid"]
    outer = max(loops, key=lambda l: max(p[0] for p in l) - min(p[0] for p in l))
    k = np.array([(p[0] / K_W, (p[2] - 247.25) / K_W) for p in outer])
    c.plot(k[:, 0], k[:, 1], color="#1f77b4", lw=1.3)
    mb = np.array([(0.478, 0.0), (0.467, 0.27), (0.4625, 0.42), (0.4466, 0.60), (0.4255, 0.75), (0.3847, 0.88), (0.332, 0.995), (0.0, 1.0)]) * np.array([1.0, 0.34])
    for sgn in (1, -1):
        c.plot(sgn * mb[:, 0], mb[:, 1], color="#2ca02c", lw=1.3, marker="o", ms=3)
        t = np.array(h.outline)
        c.plot(sgn * t[:, 0] / d.width, t[:, 1] / d.width, color=RED, lw=1.6)
        o = np.array([p for p in h.opening if p[1] >= h.z_sill])
        c.plot(sgn * o[:, 0] / d.width, o[:, 1] / d.width, color=RED, lw=0.8)
    c.plot([-0.5, 0.5], [0, 0], color="#888", lw=0.8)
    frame(c, "Hood outline from the front, divided by W (seam at 0)\nmaker's mini from photo-b picks (heights set to 0.34 W)", (-0.56, 0.56), (-0.05, 0.42), "x / W", "z / W")
    note(c, (-0.54, 0.39), "blue: 13.5 to 22 deg lean, corner R 0.074 W\ngreen: 6 deg lean, one long blend over the upper half\nred: 7 deg lean on an arc, conic blend from 0.45 of the height", size=7)
    fig.suptitle("Reconstruction: side profiles and hood outlines of the references and of the target", fontsize=13, y=0.985)
    save(fig, "sheet-side-profile", os.path.join(CAD, "out", "shell-d"), svg=False)


# ---------- the blueprint's silhouette on the reference photos ----------

OVERLAYS = {"owner-ref-1": (60, 180, 560, 800), "photo-g-video-arc-toward-hood": (40, 560, 900, 1500), "owner-ref-3-real-three-quarter-left": (60, 60, 470, 520)}
INNER_LINES = ("BZ1", "HC1", "HC2", "HC3", "RL3", "SC1", "MQ2")


def overlays() -> None:
    """Fit a camera to each annotated photo (cad/reference) on the top edge and the width of the bezel, and draw the blueprint over it.

    The photographed cabinets have other proportions (4:3 screens, a floor cabinet), so only the upper body and the
    hood compare. The four bezel corners picked in the photo are tied to a rectangle in the plane of our bezel
    that has our bezel's top edge and width and the photo bezel's aspect. The focal length is the assumption
    named in the annotation; the principal point is the centre of the picture.
    """
    import cv2
    d = Blueprint()
    faces = pr.faces(d)
    fr = pr.front(d)
    ty, tz = fr.on_rail(d, d.bezel_s1, 2.0)
    rho = math.radians(fr.recline)
    half = d.bezel_w / 2
    for stem, box in OVERLAYS.items():
        ann = json.load(open(os.path.join(CAD, "reference", stem + ".json")))
        img = cv2.imread(os.path.join(REPO, ann["photo"]))
        hgt, wid = img.shape[:2]
        drop = d.bezel_w / ann["bezel_aspect"]
        by, bz = ty - drop * math.sin(rho), tz - drop * math.cos(rho)
        obj = np.array([[-half, ty, tz], [half, ty, tz], [half, by, bz], [-half, by, bz]], float)
        pix = np.array([ann["points"][k][:2] for k in ("bz_tl", "bz_tr", "bz_br", "bz_bl")], float)
        f = ann["camera"]["f_px"]
        cam = np.array([[f, 0, wid / 2], [0, f, hgt / 2], [0, 0, 1]], float)
        ok, rvec, tvec = cv2.solvePnP(obj, pix, cam, None, flags=cv2.SOLVEPNP_IPPE)
        rot, _ = cv2.Rodrigues(rvec)
        err = np.linalg.norm(cv2.projectPoints(obj, rvec, tvec, cam, None)[0].reshape(-1, 2) - pix, axis=1)

        def to_px(points: list) -> np.ndarray:
            pts = np.array(points, float) @ rot.T + tvec.ravel()
            pts[:, 2] = np.maximum(pts[:, 2], 1.0)
            return (pts[:, :2] / pts[:, 2:]) * f + np.array([wid / 2, hgt / 2])

        mask = np.zeros((hgt, wid), np.uint8)
        for face in faces.values():
            for poly in face.polys:
                cv2.fillPoly(mask, [np.round(to_px(poly)).astype(np.int32)], 255)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        over = img.copy()
        for key in INNER_LINES:
            for e in faces[key].edges:
                cv2.polylines(over, [np.round(to_px(e)).astype(np.int32)], False, (255, 200, 0), 1, cv2.LINE_AA)
        cv2.drawContours(over, contours, -1, (255, 255, 0), 2, cv2.LINE_AA)
        for x, y in pix:
            cv2.circle(over, (int(x), int(y)), 5, (0, 0, 255), 1, cv2.LINE_AA)
        x0, y0, x1, y1 = box
        fig, axes = plt.subplots(1, 2, figsize=(15, 15 * (y1 - y0) / (x1 - x0) / 2 + 1.1))
        for ax, im, title in ((axes[0], img, "photo"), (axes[1], over, "blueprint silhouette (cyan), bezel, hood front and screen (blue), picked bezel corners (red)")):
            ax.imshow(cv2.cvtColor(im[y0:y1, x0:x1], cv2.COLOR_BGR2RGB))
            ax.set_title(title, fontsize=9)
            ax.axis("off")
        loc = (-rot.T @ tvec.ravel())
        fig.suptitle(f"{stem}: blueprint laid on the photo. Bezel top edges and bezel widths made equal; assumed focal length {f:.0f} px;\n"
                     f"camera at x {loc[0]:.0f}, y {loc[1]:.0f}, z {loc[2]:.0f} mm in our frame; corner error {err.mean():.1f} px. Only the upper body and the hood compare.", fontsize=10)
        fig.tight_layout()
        path = os.path.join(RECON, f"overlay-{stem}.png")
        fig.savefig(path, dpi=110)
        plt.close(fig)
        print("draw_blueprint:", os.path.relpath(path, REPO), f"corner error {err.round(1).tolist()} px")


if __name__ == "__main__":
    if sys.argv[1] == "overlays":
        overlays()
    elif sys.argv[1] == "fit":
        sheet_fit()
    elif sys.argv[1] == "screen-drop-options":
        screen_drop_options()
    elif sys.argv[1] == "band-options":
        band_options()
    elif sys.argv[1] == "target":
        target(sys.argv[2] if len(sys.argv) > 2 else "")
    elif sys.argv[1] == "reference":
        reference()
    elif sys.argv[1] == "photos":
        photos()
    elif sys.argv[1] == "compare":
        compare()
