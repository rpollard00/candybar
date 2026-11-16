"""The larger-monitor study (docs/research/larger-monitor.md): the free room in the sections, and the way in.

It reads cuts.json of candybar.shell.monitor_study and writes limits.json and path.json beside it:

    cad/.venv-tools/bin/python cad/tools/larger_monitor_room.py            # both
    cad/.venv-tools/bin/python cad/tools/larger_monitor_room.py limits

The work is in two dimensions, in the side sections: v is up the screen face from the centre of the image, t is the
depth behind the screen face. A section is a raster of 0.5 mm in which a cell is material or free. The skin is
material by the even-odd rule over its loops. The lugs and the other parts of the cradle are not material: a new
unit gets a new cradle.

limits  for a flat body with its glass on the glass plane: how far it can reach down and up the face in each side
        section, and how wide it can be in each section across the face
path    for each unit of monitor_pictures.UNITS: a search for a way from its place to the outside. The unit is a
        rectangle (height x thickness) that moves and tilts in the side view. It must stay clear of the union of the
        side sections that it spans. Front: with the hood on, out through the opening. Top: with the hood off (and the
        speakers and the marquee with it), out past the body top. A way that the search does not find at its step
        size can exist; a way that it finds is free at each step in each section, but the steps between are not swept.
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import deque

import numpy as np
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from candybar.shell import monitor_pictures as mp  # noqa: E402

OUT = os.environ.get("CANDYBAR_OUT") or os.path.join(ROOT, "out", "larger-monitor")
CELL = 0.5
V0, V1, T0, T1 = -330.0, 380.0, -260.0, 240.0
OWN = ("hw_Monitor",)                                # the present monitor, its room and its cables
HOOD = ("skin_hood", "hw_Speaker", "hw_Marquee")     # what leaves with the hood
MARGIN = 1.0                                         # the unit keeps this clear of each part on its way


def grid() -> tuple[np.ndarray, tuple[int, int]]:
    nv, nt = int((V1 - V0) / CELL), int((T1 - T0) / CELL)
    v = V0 + (np.arange(nv) + 0.5) * CELL
    t = T0 + (np.arange(nt) + 0.5) * CELL
    vv, tt = np.meshgrid(v, t, indexing="ij")
    return np.column_stack([vv.ravel(), tt.ravel()]), (nv, nt)


def raster(cut: dict, pts: np.ndarray, shape: tuple[int, int], skip: tuple[str, ...], ix: int = 1, iy: int = 2) -> dict[str, np.ndarray]:
    """The material of one section: 'skin' (even-odd over the loops of the skin) and 'hardware' (each loop filled)."""
    skin = np.zeros(len(pts), dtype=bool)
    hard = np.zeros(len(pts), dtype=bool)
    for name, loops in cut.items():
        if name.startswith("cradle_") or name.startswith(OWN) or name.startswith(skip):
            continue
        for loop in loops:
            if len(loop) < 3:
                continue
            xy = np.array([[p[ix], p[iy]] for p in loop])
            lo, hi = xy.min(axis=0), xy.max(axis=0)
            box = (pts[:, 0] >= lo[0]) & (pts[:, 0] <= hi[0]) & (pts[:, 1] >= lo[1]) & (pts[:, 1] <= hi[1])
            inside = np.zeros(len(pts), dtype=bool)
            inside[box] = Path(xy).contains_points(pts[box])
            if name.startswith("skin_"):
                skin ^= inside
            else:
                hard |= inside
    return {"skin": skin.reshape(shape), "hardware": hard.reshape(shape)}


def col(t: float) -> int:
    return int((t - T0) / CELL)


def row(v: float) -> int:
    return int((v - V0) / CELL)


def reach(mask: np.ndarray, t0: float, t1: float) -> tuple[float, float]:
    """How far a body between the depths t0 and t1 reaches down and up the face from v = 0 before it meets material."""
    band = mask[:, col(t0):col(t1) + 1].any(axis=1)
    mid = row(0.0)
    up = next((i for i in range(mid, len(band)) if band[i]), len(band))
    down = next((i for i in range(mid, -1, -1) if band[i]), -1)
    return V0 + (down + 1) * CELL, V0 + up * CELL


def limits(cuts: dict) -> dict:
    pts, shape = grid()
    g = cuts["frame"]["glass_t"]
    out = {"glass_t": g, "side": [], "face": []}
    for x, cut in cuts["side"].items():
        m = raster(cut, pts, shape, ())
        for where, front in (("in the opening", g), ("behind the ledges", mp.GLASS_BEHIND)):
            for thick in (11.0, 20.0, 50.0):
                lo, hi = reach(m["skin"], front, front + thick)
                lo2, hi2 = reach(m["skin"] | m["hardware"], front, front + thick)
                out["side"].append({"x": float(x), "glass": where, "thick": thick, "skin": [lo, hi], "skin and hardware": [lo2, hi2]})
    # across the face: in a section v = const a point is (x, t); the same raster with x in place of v
    for v, cut in cuts["face"].items():
        m = raster(cut, pts, shape, (), ix=0, iy=2)
        for name, (t0, t1) in (("in the opening", (g, 11.0)), ("behind the jambs", (mp.GLASS_BEHIND, mp.GLASS_BEHIND + 11.0)), ("behind the jambs, 50 deep", (mp.GLASS_BEHIND, mp.GLASS_BEHIND + 50.0))):
            lo, hi = reach(m["skin"], t0, t1)
            lo2, hi2 = reach(m["skin"] | m["hardware"], t0, t1)
            out["face"].append({"v": float(v), "where": name, "skin": [lo, hi], "skin and hardware": [lo2, hi2]})
    return out


def outline(h: float, t: float, step: float = 1.0) -> np.ndarray:
    """Points on the rim of a rectangle h x t (and on lines through it, so that no part passes inside it), about its centre."""
    hv = np.arange(-h / 2, h / 2 + step / 2, step)
    ht = np.arange(-t / 2, t / 2 + step / 2, step)
    pts = [np.column_stack([hv, np.full_like(hv, c)]) for c in np.linspace(-t / 2, t / 2, max(2, int(t / 4) + 2))]
    pts += [np.column_stack([np.full_like(ht, c), ht]) for c in (-h / 2, h / 2)]
    return np.vstack(pts)


def way(mask: np.ndarray, h: float, t: float, seat: tuple[float, float], frame: dict, goal: str) -> dict:
    """A search over (tilt, v, t) of the centre of the rectangle, from its seat to the goal, through free poses."""
    rim = outline(h + 2 * MARGIN, t + 2 * MARGIN)
    tilts = np.arange(-30.0, 91.0, 2.0)
    step = 3.0
    av = np.arange(-240.0, 300.0, step)
    bt = np.arange(-240.0, 180.0, step)
    cz, upz, intoz = frame["c"][2], frame["up"][2], frame["into"][2]

    def pose(k):
        a = math.radians(tilts[k[0]])
        c, s = math.cos(a), math.sin(a)
        # a positive tilt moves the top of the unit to the front
        return np.column_stack([av[k[1]] + rim[:, 0] * c + rim[:, 1] * s, bt[k[2]] - rim[:, 0] * s + rim[:, 1] * c])

    def free(p):
        i = ((p[:, 0] - V0) / CELL).astype(int)
        j = ((p[:, 1] - T0) / CELL).astype(int)
        ok = (i >= 0) & (i < mask.shape[0]) & (j >= 0) & (j < mask.shape[1])
        return not mask[i[ok], j[ok]].any()

    def done(p):
        if goal == "front":
            return bool((p[:, 1] < -15.0).all())
        return bool((cz + upz * p[:, 0] + intoz * p[:, 1] > frame["top_z"] + 15.0).all())

    start = (int(np.argmin(abs(tilts))), int(np.argmin(abs(av - seat[0]))), int(np.argmin(abs(bt - seat[1]))))
    if not free(pose(start)):
        return {"found": False, "why": "the unit is not free at its seat"}
    seen = {start: None}
    queue = deque([start])
    while queue:
        k = queue.popleft()
        if done(pose(k)):
            steps = []
            while k is not None:
                steps.append([float(tilts[k[0]]), float(av[k[1]]), float(bt[k[2]])])
                k = seen[k]
            return {"found": True, "poses": steps, "largest_tilt": max(abs(s[0]) for s in steps),
                    "deepest": max(s[2] + abs(math.sin(math.radians(s[0]))) * h / 2 for s in steps)}
        for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            n = (k[0] + d[0], k[1] + d[1], k[2] + d[2])
            if n in seen or not (0 <= n[0] < len(tilts) and 0 <= n[1] < len(av) and 0 <= n[2] < len(bt)):
                continue
            seen[n] = k
            if free(pose(n)):
                queue.append(n)
    return {"found": False, "why": f"no free way in {len(seen)} poses"}


def paths(cuts: dict) -> list[dict]:
    pts, shape = grid()
    g = cuts["frame"]["glass_t"]
    frame = dict(cuts["frame"])
    sides = {float(x): cut for x, cut in cuts["side"].items()}
    cache: dict = {}

    def mask(half: float, hood: bool) -> np.ndarray:
        key = (tuple(x for x in sides if x <= half), hood)
        if key not in cache:
            m = np.zeros(shape, dtype=bool)
            for x in key[0]:
                r = raster(sides[x], pts, shape, () if hood else HOOD)
                m |= r["skin"] | r["hardware"]
            cache[key] = m
        return cache[key]

    # the body top: the highest point of the skin of the body in the centre section
    frame["top_z"] = max(p[4] for loop in sides[0.0]["skin_body"] for p in loop)
    rows = []
    for u in mp.UNITS:
        for turned in (False, True):
            w, h, up = (u.h, u.w, 0.0) if turned else (u.w, u.h, u.up)
            seat = (-up, mp.glass_t(w, h) + u.t / 2)
            for goal in ("front", "top"):
                r = way(mask(w / 2, goal == "front"), h, u.t, seat, frame, goal)
                r.update({"key": u.key, "turned": turned, "goal": goal, "w": w, "h": h, "t": u.t})
                rows.append(r)
                print(u.key, "turned" if turned else "", goal, r["found"], r.get("why", ""), round(r.get("largest_tilt", 0)), round(r.get("deepest", 0)), flush=True)
    return rows


def main() -> None:
    what = sys.argv[1:] or ["limits", "path"]
    cuts = json.load(open(os.path.join(OUT, "cuts.json"), encoding="utf-8"))
    if "limits" in what:
        json.dump(limits(cuts), open(os.path.join(OUT, "limits.json"), "w", encoding="utf-8"), indent=1)
    if "path" in what:
        json.dump(paths(cuts), open(os.path.join(OUT, "path.json"), "w", encoding="utf-8"))


if __name__ == "__main__":
    main()
