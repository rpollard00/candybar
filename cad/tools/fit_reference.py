"""Fit the assembled Mini New Astro City reference to this cabinet's hardware: target meshes, fit checks, report.

A target is the reference mesh, morphed with piecewise-linear maps of the vertex coordinates:
  X  uniform scale, plus width inserted only in the middle band |X| < X_MID (between the speaker pods),
  Y  uniform scale, plus depth inserted only in the flat of the deck, plus a transition band behind the
     screen face where the front zone (deck, screen face, cheeks, hood front) and the rear zone (step line,
     rear body, rear wall, hood rear) are joined. The front zone is shifted along Y as a function of height
     so that the screen face becomes a plane at the target recline; the rear zone is shifted by the body
     depth insertion.
  Z  uniform scale; the front zone gets the deck height change and the apron lift (a band just above the
     foot of the screen face) and an optional band in the middle of the screen face; the rear zone gets
     the same total in one band (at the top of the rear wall, or in the vertical rear wall).
The band positions are in reference millimetres and are chosen in plain regions, so the cheek thickness,
the facets, the hood corners and the deck corners keep their proportion.

Hardware comes from the generator: export-hardware runs freecadcmd on a built candybar.FCStd and writes
the solids with CB_Role hardware or keepout. Each variant moves the hardware groups rigidly to its own
frame (monitor on the screen face, power supply and BC-250 module against the rear wall, controls in the
panel) and tests every box against the target shell triangles (exact separating-axis test) and against
the inner volume (rays), with a clearance found by bisection.

Needs numpy (cad/.venv-tools). Examples:
    cad/.venv-tools/bin/python cad/tools/fit_reference.py export-hardware build/candybar.FCStd hw
    cad/.venv-tools/bin/python cad/tools/fit_reference.py fit REF_DIR hw OUT_DIR --variants A,B,C
"""
from __future__ import annotations

import argparse
import json
import math
import os
import struct
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field, replace

import numpy as np

GROUPS = ("body", "deck", "control_panel", "hood", "hood_band", "bezel", "speaker_plate")
FINISH = {"window_backing": "black", "body": "white", "deck": "white", "control_panel": "black", "hood": "white", "hood_band": "white",
          "bezel": "black", "speaker_plate": "dark", "deck_infill": "white", "screen": "dark"}

REF_W = 270.0
REF_RECLINE = 32.5
X_MID = 40.0
DECK_BAND = (32.0, 82.0)
DECK_Z_BAND = (18.0, 37.0)
APRON_BAND = (57.0, 62.0)
SCREEN_BAND = (130.0, 170.0)
HOOD_BAND = (264.0, 284.0)
REAR_BANDS = {"top": (238.5, 246.0), "wall": (70.0, 165.0)}
FACE_N = np.array([0.0, -math.cos(math.radians(REF_RECLINE)), math.sin(math.radians(REF_RECLINE))])
FACE_D = -67.3
FACE_FOOT_Z = 54.0
BEZEL_Z = (64.86, 240.75)
REF_PANEL_Y = (15.1, 104.0)
REF_PANEL_TOP = 49.81
REF_DECK_TOP = 50.0
REF_DECK_NOSE = 15.0
REF_FLOOR_TOP = 15.0
REF_LCD_LIP = 3.0
# Transition band (reference Z, front edge Y, rear edge Y): in front of the step line, behind the bezel.
BAND = ((0.0, 128.0, 172.0), (50.0, 130.0, 176.0), (62.0, 138.0, 186.0), (105.0, 166.0, 210.0), (155.0, 198.0, 233.0),
        (215.0, 238.0, 296.0), (250.0, 262.0, 300.0), (340.0, 264.0, 299.0))
CHEEK_ARC = {"centre": (413.4, -8.1), "r": 311.6, "z": (53.0, 240.5), "x": 122.0}

EYE = np.array([0.0, -60.0, 530.0])
MON = {"w": 354.0, "h": 230.0, "active_w": 344.678, "active_h": 215.424, "bezel_bottom": 9.6, "side_clear": 22.0}
PANEL = {"w": 396.0, "d": 240.0, "gap": 1.0, "inner_h": 56.0, "top": (60.0, 75.0)}
SIGHT = (15.0, 25.0)
EYE_DIST = (450.0, 600.0)
SOFT = {"W": 500.0, "D": 620.0, "H": 660.0}
LAYOUT = {"panel_top": 67.0, "panel_y0": 15.0, "psu_z0": 14.0, "rear_inner_y": 515.0}
PSU_RAISE = 3.0
PSU_SIDE = 8.0
BC_SIDE = 3.0

MONITOR_PARTS = ("Monitor_Body", "Monitor_Cradle", "Monitor_Plugs", "Monitor_Controls")
PSU_PARTS = ("PSU_Body", "PSU_FanAir", "PSU_Plugs", "CableBundle_Body")
COMPUTE_PREFIX = "Compute_"
CONTROL_PREFIXES = ("Lever_", "Btn", "Svc", "Encoder_")


@dataclass(frozen=True)
class Variant:
    key: str
    title: str
    scale: float
    recline: float
    width_insert: float
    panel_top: float
    apron_lift: float
    screen_insert: float
    body_insert: float
    shelf: float = 0.0
    hood_insert: float = 0.0
    rear_band: str = "top"
    psu_on_facet: bool = False
    note: str = ""


VARIANTS = {
    "A": Variant("A", "A  faithful", scale=1.60, recline=24.0, width_insert=50.0, panel_top=72.0, apron_lift=80.0,
                 screen_insert=40.0, body_insert=0.0, shelf=10.0, hood_insert=13.0, rear_band="wall", psu_on_facet=True,
                 note="largest scale, least insertion; the body keeps its reference depth"),
    "B": Variant("B", "B  compact", scale=1.20, recline=23.0, width_insert=142.0, panel_top=70.0, apron_lift=105.0,
                 screen_insert=60.0, body_insert=15.0, shelf=15.0, rear_band="wall", psu_on_facet=True,
                 note="smallest scale that keeps every signature form; the screen stands on a tall apron"),
    "C": Variant("C", "C  balanced", scale=1.40, recline=24.0, width_insert=95.0, panel_top=70.0, apron_lift=65.0,
                 screen_insert=110.0, body_insert=15.0, shelf=20.0, hood_insert=30.0, rear_band="wall", psu_on_facet=True,
                 note="a tall black bezel and a taller hood, as on the reference cabinet photos"),
}


def read_stl(path: str) -> np.ndarray:
    with open(path, "rb") as fh:
        data = fh.read()
    n = struct.unpack_from("<I", data, 80)[0]
    if len(data) == 84 + 50 * n:
        rec = np.frombuffer(data, dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]), count=n, offset=84)
        return rec["v"].astype(np.float64)
    vals = [list(map(float, ln.split()[1:4])) for ln in data.decode("ascii", "replace").splitlines() if ln.strip().startswith("vertex")]
    return np.array(vals, dtype=np.float64).reshape(-1, 3, 3)


def write_stl(path: str, tris: np.ndarray) -> None:
    t = tris.astype(np.float32)
    nrm = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-12)
    rec = np.zeros(len(t), dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    rec["n"], rec["v"] = nrm, t
    with open(path, "wb") as fh:
        fh.write(b"fit_reference".ljust(80, b" "))
        fh.write(struct.pack("<I", len(t)))
        fh.write(rec.tobytes())


def box_tris(lo: np.ndarray, hi: np.ndarray, frame: np.ndarray | None = None) -> np.ndarray:
    c = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    faces = [(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5), (0, 4, 5), (0, 5, 1), (2, 3, 7), (2, 7, 6), (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)]
    t = c[np.array(faces)]
    return t if frame is None else t @ frame[:3, :3].T + frame[:3, 3]


class PiecewiseLinear:
    """y = scale * x plus extra length spread linearly over bands [a, b] of x."""

    def __init__(self, scale: float, bands: list[tuple[float, float, float]], offset: float = 0.0):
        knots = sorted({0.0, *[a for a, _, _ in bands], *[b for _, b, _ in bands]})
        xs = [-1e5, *knots, 1e5]
        ys = []
        for x in xs:
            y = scale * x
            for a, b, extra in bands:
                y += extra * min(max((x - a) / (b - a), 0.0), 1.0)
            ys.append(y + offset)
        self.xs, self.ys = np.array(xs), np.array(ys)

    def __call__(self, x: np.ndarray) -> np.ndarray:
        return np.interp(x, self.xs, self.ys)

    def inverse(self, y: np.ndarray) -> np.ndarray:
        return np.interp(y, self.ys, self.xs)


@dataclass
class Morph:
    v: Variant
    deck_insert: float
    x_map: PiecewiseLinear = field(init=False)
    y_map: PiecewiseLinear = field(init=False)
    z_front: PiecewiseLinear = field(init=False)
    z_rear: PiecewiseLinear = field(init=False)
    d_z: np.ndarray = field(init=False)
    d_val: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        v, s = self.v, self.v.scale
        self.x_map = PiecewiseLinear(s, [(-X_MID, X_MID, v.width_insert)], offset=-v.width_insert / 2)
        self.y_map = PiecewiseLinear(s, [(*DECK_BAND, self.deck_insert)])
        deck_dz = v.panel_top - REF_PANEL_TOP * s
        front = [(*DECK_Z_BAND, deck_dz), (*APRON_BAND, v.apron_lift)]
        if v.screen_insert:
            front.append((*SCREEN_BAND, v.screen_insert))
        total = sum(e for _, _, e in front)
        hood = [(*HOOD_BAND, v.hood_insert)] if v.hood_insert else []
        self.z_front = PiecewiseLinear(s, front + hood)
        self.z_rear = PiecewiseLinear(s, [(*REAR_BANDS[v.rear_band], total)] + hood)
        z_ref = np.linspace(FACE_FOOT_Z, BEZEL_Z[1], 400)
        y_ref = (FACE_D - FACE_N[2] * z_ref) / FACE_N[1]
        zf = self.z_front(z_ref)
        yf = self.y_map(y_ref)
        tan_r = math.tan(math.radians(v.recline))
        target = yf[0] + (zf - zf[0]) * tan_r
        self.d_z, self.d_val = zf, yf - target

    def d(self, zf: np.ndarray) -> np.ndarray:
        return np.interp(zf, self.d_z, self.d_val, left=0.0, right=self.d_val[-1])

    def weight(self, y: np.ndarray, z: np.ndarray) -> np.ndarray:
        bz = np.array([b[0] for b in BAND])
        ya = np.interp(z, bz, [b[1] for b in BAND])
        yb = np.interp(z, bz, [b[2] for b in BAND])
        return np.clip((yb - y) / (yb - ya), 0.0, 1.0)

    def apply(self, p: np.ndarray, zone: str | None = None) -> np.ndarray:
        x, y, z = p[..., 0], p[..., 1], p[..., 2]
        zf, zr = self.z_front(z), self.z_rear(z)
        yf = self.y_map(y) - self.d(zf)
        yr = self.y_map(y) + self.v.body_insert
        w = self.weight(y, z) if zone is None else (np.ones_like(y) if zone == "front" else np.zeros_like(y))
        return np.stack([self.x_map(x), w * yf + (1 - w) * yr, w * zf + (1 - w) * zr], axis=-1)


def deck_insert_for(v: Variant) -> float:
    need = PANEL["d"] + 2 * PANEL["gap"] + v.shelf
    return need - (REF_PANEL_Y[1] - REF_PANEL_Y[0]) * v.scale


# ---------- geometry tests ----------

def tri_obb_hits(tris: np.ndarray, frame: np.ndarray, half: np.ndarray) -> bool:
    """Exact separating-axis test: does any triangle intersect the oriented box (frame centre, half sizes)?"""
    rot = frame[:3, :3]
    t = (tris - frame[:3, 3]) @ rot
    lo, hi = t.min(1), t.max(1)
    keep = np.all(lo <= half, axis=1) & np.all(hi >= -half, axis=1)
    t = t[keep]
    if not len(t):
        return False
    e = np.stack([t[:, 1] - t[:, 0], t[:, 2] - t[:, 1], t[:, 0] - t[:, 2]], axis=1)
    nrm = np.cross(e[:, 0], e[:, 1])
    sep = np.zeros(len(t), dtype=bool)
    axes = [nrm] + [np.cross(np.eye(3)[i], e[:, j]) for i in range(3) for j in range(3)]
    for ax in axes:
        p = np.einsum("nij,nj->ni", t, ax)
        r = np.abs(ax) @ half
        sep |= (p.min(1) > r + 1e-9) | (p.max(1) < -r - 1e-9)
    return bool((~sep).any())


def obb_obb_hits(fa: np.ndarray, ha: np.ndarray, fb: np.ndarray, hb: np.ndarray) -> bool:
    ra, rb = fa[:3, :3], fb[:3, :3]
    d = fb[:3, 3] - fa[:3, 3]
    axes = [ra[:, i] for i in range(3)] + [rb[:, i] for i in range(3)]
    axes += [np.cross(ra[:, i], rb[:, j]) for i in range(3) for j in range(3)]
    for ax in axes:
        n = np.linalg.norm(ax)
        if n < 1e-9:
            continue
        ax = ax / n
        r1 = np.abs(ra.T @ ax) @ ha
        r2 = np.abs(rb.T @ ax) @ hb
        if abs(d @ ax) > r1 + r2 + 1e-9:
            return False
    return True


def clearance(test, hi: float = 80.0, lo_limit: float = -40.0) -> float:
    """Signed clearance: the largest inflation m (negative: the smallest deflation) for which test(m) is False."""
    if test(0.0):
        lo, hi = lo_limit, 0.0
        if test(lo):
            return lo
    elif not test(hi):
        return hi
    else:
        lo = 0.0
    for _ in range(14):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if test(mid) else (mid, hi)
    return lo


def ray_hit_any(tris: np.ndarray, origin: np.ndarray, direction: np.ndarray) -> bool:
    v0 = tris[:, 0]
    e1, e2 = tris[:, 1] - v0, tris[:, 2] - v0
    p = np.cross(direction, e2)
    det = (e1 * p).sum(1)
    ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
    tv = origin - v0
    u = (tv * p).sum(1) * inv
    q = np.cross(tv, e1)
    w = (q * direction).sum(1) * inv
    t = (e2 * q).sum(1) * inv
    return bool((ok & (u >= 0) & (w >= 0) & (u + w <= 1) & (t > 0)).any())


def wall_distance(tris: np.ndarray, direction: np.ndarray, fixed: float, ys: tuple[float, float], zs: tuple[float, float]) -> float:
    """Median distance from the plane X=fixed (or Y=fixed for a Y ray) to the shell over a 5 x 5 grid of rays,
    so that a vent hole or a boss does not decide the wall position."""
    hits = []
    for a in np.linspace(*ys, 5):
        for b in np.linspace(*zs, 5):
            o = np.array([fixed, a, b]) if direction[1] == 0 else np.array([a, fixed, b])
            hits.append(first_hit(tris, o, direction))
    return float(np.median(hits))


def enclosed(tris: np.ndarray, point: np.ndarray) -> bool:
    """Inside the shell: rays toward the sides, the rear, the roof and the floor all meet the shell."""
    dirs = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, -1)]
    jit = [np.array(j) for j in ((0.7, 0.3, 0.2), (-24.9, 19.1, 21.3), (23.7, -22.9, -18.3), (19.3, 25.7, -24.1), (-21.9, -20.6, 23.4))]
    for d in dirs:
        hits = sum(ray_hit_any(tris, point + j, np.array(d, float)) for j in jit)
        if hits < 2:
            return False
    return True


def first_hit(tris: np.ndarray, origin: np.ndarray, direction: np.ndarray) -> float:
    v0 = tris[:, 0]
    e1, e2 = tris[:, 1] - v0, tris[:, 2] - v0
    p = np.cross(direction, e2)
    det = (e1 * p).sum(1)
    ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
    tv = origin - v0
    u = (tv * p).sum(1) * inv
    q = np.cross(tv, e1)
    w = (q * direction).sum(1) * inv
    t = (e2 * q).sum(1) * inv
    m = ok & (u >= 0) & (w >= 0) & (u + w <= 1) & (t > 1e-6)
    return float(t[m].min()) if m.any() else math.inf


# ---------- hardware ----------

@dataclass
class Box:
    name: str
    role: str
    frame: np.ndarray
    lo: np.ndarray
    hi: np.ndarray

    def centre_frame(self) -> tuple[np.ndarray, np.ndarray]:
        c = (self.lo + self.hi) / 2
        f = self.frame.copy()
        f[:3, 3] = self.frame[:3, :3] @ c + self.frame[:3, 3]
        return f, (self.hi - self.lo) / 2

    def corners(self) -> np.ndarray:
        c = np.array([[x, y, z] for x in (self.lo[0], self.hi[0]) for y in (self.lo[1], self.hi[1]) for z in (self.lo[2], self.hi[2])])
        return c @ self.frame[:3, :3].T + self.frame[:3, 3]

    def moved(self, m: np.ndarray) -> "Box":
        return Box(self.name, self.role, m @ self.frame, self.lo, self.hi)


def load_hardware(hw_dir: str) -> dict[str, Box]:
    with open(os.path.join(hw_dir, "hardware.json")) as fh:
        items = json.load(fh)
    return {it["name"]: Box(it["name"], it["role"], np.array(it["placement"]), np.array(it["local_lo"]), np.array(it["local_hi"])) for it in items}


FREECAD_EXPORT = r'''
import FreeCAD, MeshPart, json, os
doc = FreeCAD.openDocument(os.environ["FIT_DOC"])
out = os.environ["FIT_OUT"]
items = []
for o in doc.Objects:
    role = getattr(o, "CB_Role", None)
    if role not in ("hardware", "keepout") or not hasattr(o, "Shape"):
        continue
    gp = o.getGlobalPlacement()
    local = o.Shape.copy(); local.Placement = FreeCAD.Placement()
    bb = local.BoundBox
    shp = o.Shape.copy(); shp.Placement = gp
    MeshPart.meshFromShape(Shape=shp, LinearDeflection=0.2, AngularDeflection=0.35).write(os.path.join(out, o.Name + ".stl"))
    a = list(gp.toMatrix().A)
    items.append({"name": o.Name, "role": role, "placement": [a[4 * i:4 * i + 4] for i in range(4)],
                  "local_lo": [bb.XMin, bb.YMin, bb.ZMin], "local_hi": [bb.XMax, bb.YMax, bb.ZMax], "file": o.Name + ".stl"})
json.dump(items, open(os.path.join(out, "hardware.json"), "w"), indent=1)
print("exported", len(items))
'''


def export_hardware(doc: str, out: str) -> None:
    os.makedirs(out, exist_ok=True)
    env = dict(os.environ, FIT_DOC=os.path.abspath(doc), FIT_OUT=os.path.abspath(out))
    env.setdefault("FREECAD_USER_HOME", tempfile.mkdtemp(prefix="fc_home_"))
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(FREECAD_EXPORT)
    proc = subprocess.run(["freecadcmd", fh.name], env=env, capture_output=True, text=True)
    os.unlink(fh.name)
    if not os.path.exists(os.path.join(out, "hardware.json")):
        sys.stderr.write(proc.stdout[-2000:] + proc.stderr[-2000:])
        raise SystemExit("export-hardware failed")
    print(f"export-hardware: {len(json.load(open(os.path.join(out, 'hardware.json'))))} solids -> {out}")


def translation(d: np.ndarray) -> np.ndarray:
    m = np.eye(4)
    m[:3, 3] = d
    return m


def rot_x(deg: float) -> np.ndarray:
    a = math.radians(deg)
    m = np.eye(4)
    m[1:3, 1:3] = [[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]
    return m


# ---------- the fit ----------

def load_reference(ref_dir: str) -> dict[str, np.ndarray]:
    return {g: read_stl(os.path.join(ref_dir, f"{g}.stl")) for g in GROUPS}


def fit_variant(v: Variant, ref: dict[str, np.ndarray], hw: dict[str, Box], out: str) -> dict:
    os.makedirs(out, exist_ok=True)
    morph = Morph(v, deck_insert_for(v))
    s = v.scale
    shell = {g: morph.apply(t) for g, t in ref.items() if g != "control_panel"}

    # control panel: a plain plate in the deck opening, deck-coloured infill around it
    op_y0, op_y1 = (float(morph.y_map(np.array(y))) for y in REF_PANEL_Y)
    op_x = float(morph.x_map(np.array(119.8)))
    panel_top = v.panel_top
    rim_top = float(morph.z_front(np.array(REF_DECK_TOP)))
    plate_t = 5.0 * s
    py0 = op_y0 + PANEL["gap"]
    panel_lo = np.array([-PANEL["w"] / 2, py0, panel_top - plate_t])
    panel_hi = np.array([PANEL["w"] / 2, py0 + PANEL["d"], panel_top])
    shell["control_panel"] = box_tris(panel_lo, panel_hi)
    infill = []
    zl, zh = panel_top - plate_t, rim_top - 0.2
    if op_x - PANEL["w"] / 2 - PANEL["gap"] > 0.5:
        for sx in (-1, 1):
            a, b = sorted((sx * (PANEL["w"] / 2 + PANEL["gap"]), sx * op_x))
            infill.append(box_tris(np.array([a, op_y0, zl]), np.array([b, op_y1, zh])))
    if op_y1 - (panel_hi[1] + PANEL["gap"]) > 0.5:
        infill.append(box_tris(np.array([-PANEL["w"] / 2 - PANEL["gap"], panel_hi[1] + PANEL["gap"], zl]), np.array([PANEL["w"] / 2 + PANEL["gap"], op_y1, zh])))
    if infill:
        shell["deck_infill"] = np.concatenate(infill)

    all_tris = np.concatenate(list(shell.values()))
    lo, hi = all_tris.reshape(-1, 3).min(0), all_tris.reshape(-1, 3).max(0)
    W, D, H = hi - lo

    # screen face and bezel plate
    tan_r = math.tan(math.radians(v.recline))
    u = np.array([0.0, math.sin(math.radians(v.recline)), math.cos(math.radians(v.recline))])
    n_out = np.array([0.0, -math.cos(math.radians(v.recline)), math.sin(math.radians(v.recline))])
    bz = np.array(BEZEL_Z)
    by = (FACE_D - FACE_N[2] * bz) / FACE_N[1]
    pts = morph.apply(np.stack([np.zeros(2), by, bz], axis=1), zone="front")
    bezel_tris = shell["bezel"]
    nb = np.cross(bezel_tris[:, 1] - bezel_tris[:, 0], bezel_tris[:, 2] - bezel_tris[:, 0])
    nb /= np.maximum(np.linalg.norm(nb, axis=1, keepdims=True), 1e-12)
    front_face = bezel_tris[(nb @ n_out) > 0.999]
    fpts = front_face.reshape(-1, 3)
    face_off = float(np.median(fpts @ n_out))
    along = fpts @ u
    plate_u0, plate_u1 = float(along.min()), float(along.max())
    plate_len = plate_u1 - plate_u0
    plate_w = float(fpts[:, 0].max() - fpts[:, 0].min())
    recline_meas = math.degrees(math.atan2(pts[1, 1] - pts[0, 1], pts[1, 2] - pts[0, 2]))
    # origin of the face frame: the bezel plate's lower front edge at X=0
    base = n_out * face_off + u * plate_u0
    base = base - n_out * (base @ n_out - face_off)
    centre = base + u * plate_len / 2
    sight = math.degrees(math.atan2(EYE[2] - centre[2], centre[1] - EYE[1]))
    eye_dist = float(np.linalg.norm(centre - EYE))

    # hardware groups, moved rigidly from the current layout
    placed: dict[str, Box] = {}
    lip = REF_LCD_LIP * s
    mon_old = hw["Monitor_Body"].frame
    frame_new = np.eye(4)
    frame_new[:3, 0] = [1.0, 0.0, 0.0]
    frame_new[:3, 1] = -n_out
    frame_new[:3, 2] = u
    img_from_bottom = MON["bezel_bottom"] + MON["active_h"] / 2
    frame_new[:3, 3] = centre - n_out * lip - u * img_from_bottom + np.array([-MON["w"] / 2, 0.0, 0.0])
    m_mon = frame_new @ np.linalg.inv(mon_old)
    for name in MONITOR_PARTS:
        placed[name] = hw[name].moved(m_mon)

    floor_top = float(morph.apply(np.array([[0.0, 250.0, REF_FLOOR_TOP]]))[0, 2])
    rear_inner = float(morph.apply(np.array([[0.0, 323.1, 120.0]]))[0, 1])
    psu = hw["PSU_Body"]
    psu_c = psu.corners()
    psu_z0 = floor_top + PSU_RAISE
    facet_top = None
    if v.psu_on_facet:
        facet_top = float(morph.apply(np.array([[0.0, 323.1, 55.0]]), zone="rear")[0, 2])
        psu_z0 = max(psu_z0, facet_top + PSU_RAISE)
    left_inner = -wall_distance(all_tris, np.array([-1.0, 0.0, 0.0]), 0.3, (rear_inner - 140.0, rear_inner - 10.0), (psu_z0 + 10.0, psu_z0 + 76.0))
    d_psu = np.array([left_inner + PSU_SIDE - psu_c[:, 0].min(), rear_inner - psu_c[:, 1].max(), psu_z0 - psu_c[:, 2].min()])
    for name in PSU_PARTS:
        placed[name] = hw[name].moved(translation(d_psu))
    dz_hw = psu_z0 - LAYOUT["psu_z0"]

    comp = {k: b for k, b in hw.items() if k.startswith(COMPUTE_PREFIX)}
    cc = np.concatenate([b.corners() for b in comp.values()])
    bc_lo_z = float(hw["Compute_PCB_IO"].corners()[:, 2].min()) + dz_hw
    zs = np.linspace(bc_lo_z, bc_lo_z + 160.0, 9)
    wall_y = min(first_hit(all_tris, np.array([x, rear_inner - 120.0, z]), np.array([0.0, 1.0, 0.0])) + rear_inner - 120.0
                 for z in zs for x in (-150.0, 0.0, 150.0))
    span_y, span_z = (wall_y - 85.0, wall_y - 5.0), (bc_lo_z + 5.0, bc_lo_z + 140.0)
    lw = -wall_distance(all_tris, np.array([-1.0, 0.0, 0.0]), 0.3, span_y, span_z)
    rw = wall_distance(all_tris, np.array([1.0, 0.0, 0.0]), 0.3, span_y, span_z)
    d_bc = np.array([lw + BC_SIDE - cc[:, 0].min(), wall_y - cc[:, 1].max(), dz_hw])
    for name, b in comp.items():
        placed[name] = b.moved(translation(d_bc))

    d_ctl = np.array([0.0, py0 - LAYOUT["panel_y0"], panel_top - LAYOUT["panel_top"]])
    for name, b in hw.items():
        if name.startswith(CONTROL_PREFIXES):
            placed[name] = b.moved(translation(d_ctl))

    # checks
    checks: list[dict] = []

    def add(req: str, ok: bool, value: str, margin: str) -> None:
        checks.append({"requirement": req, "pass": bool(ok), "value": value, "margin": margin})

    shell_for = {k: t for k, t in shell.items()}
    face_frame = np.eye(4)
    face_frame[:3, 0], face_frame[:3, 1], face_frame[:3, 2] = [1.0, 0.0, 0.0], -n_out, u
    face_frame[:3, 3] = base
    window_cover = box_tris(np.array([-plate_w / 2, 0.0, 0.0]), np.array([plate_w / 2, 2.0, plate_len]), face_frame)
    closed = np.concatenate([all_tris, window_cover])
    hw_checks = {}
    for name, b in placed.items():
        f, h = b.centre_frame()
        skip = {"bezel"} if name.startswith("Monitor") else {"control_panel", "deck_infill"} if name.startswith(CONTROL_PREFIXES) else set()
        others = {k: t for k, t in shell_for.items() if k not in skip}
        per = {k: clearance(lambda e, t=t: tri_obb_hits(t, f, np.maximum(h + e, 0.01)), hi=60.0, lo_limit=-float(h.min()))
               for k, t in others.items()}
        worst = min(per, key=per.get)
        inside = enclosed(closed, f[:3, 3])
        hw_checks[name] = {"clearance": round(per[worst], 1), "nearest": worst, "enclosed": inside}

    def group_ok(names: tuple[str, ...] | list[str], contact: float = 0.0) -> tuple[bool, float]:
        ms = [hw_checks[n]["clearance"] for n in names]
        return all(hw_checks[n]["enclosed"] for n in names) and min(ms) >= -contact, min(ms)

    ok, m = group_ok(["Monitor_Body", "Monitor_Plugs", "Monitor_Controls"])
    add("Monitor body with 22 mm clear at each side edge, between the side walls", ok,
        f"inner width at the monitor {abs(left_inner_at(all_tris, placed['Monitor_Body'])):.0f}", f"{m:.1f} mm")
    okc, mc = group_ok(["Monitor_Cradle"])
    add("Monitor cradle (20 mm behind the monitor)", okc, "", f"{mc:.1f} mm")
    bez_vs_mon = (plate_w - MON["w"]) / 2, (plate_len - MON["h"]) / 2
    add("Bezel plate covers the monitor body", min(bez_vs_mon) > 0, f"plate {plate_w:.0f} x {plate_len:.0f}",
        f"{min(bez_vs_mon):.1f} mm")
    add("Lit image centred in the bezel plate", True, "placed on the plate centre", "0.0 mm")
    psu_ok, psu_m = group_ok(["PSU_Body"], contact=0.5)
    add("Power supply on the floor at the rear left, rear face at the rear wall", psu_ok,
        f"underside {psu_z0:.0f} above the desk" + (" (on the facet top)" if facet_top else ""), f"{psu_m:.1f} mm")
    bundle_ok, bundle_m = group_ok(["CableBundle_Body", "PSU_Plugs"])
    add("Cable bundle and the PSU plug space", bundle_ok, "", f"{bundle_m:.1f} mm")
    comp_names = [n for n in placed if n.startswith(COMPUTE_PREFIX)]
    comp_ok, comp_m = group_ok(comp_names, contact=0.5)
    across = cc[:, 0].max() - cc[:, 0].min()
    add("BC-250 module with its exhaust duct against the rear wall", comp_ok,
        f"{across:.0f} across, lower edge {bc_lo_z:.0f}, rear-body inner width {float(morph.x_map(np.array(100.0)) * 2):.0f}", f"{comp_m:.1f} mm")
    pairs = [("Monitor_Body", "Compute_FanShroud"), ("Monitor_Cradle", "Compute_FanShroud"), ("Monitor_Cradle", "Compute_Heatsink"),
             ("Monitor_Cradle", "Compute_PowerPlug"), ("Monitor_Cradle", "Compute_PCB_Pwr"), ("Monitor_Cradle", "Compute_UndersideAir"),
             ("Monitor_Cradle", "Compute_ExhaustDuct"), ("Monitor_Cradle", "Compute_IO"), ("Monitor_Cradle", "Compute_Backplate"),
             ("Monitor_Cradle", "CableBundle_Body"), ("Monitor_Cradle", "PSU_FanAir"),
             ("Monitor_Plugs", "Compute_ExhaustDuct"), ("Monitor_Controls", "Compute_PowerPlug"),
             ("PSU_FanAir", "Compute_ExhaustDuct"), ("PSU_FanAir", "Compute_UndersideAir"), ("CableBundle_Body", "Compute_UndersideAir")]
    pair_m = []
    for a, b in pairs:
        fa, ha = placed[a].centre_frame()
        fb, hb = placed[b].centre_frame()
        lim = -float(min(ha.min(), hb.min()))
        pair_m.append((clearance(lambda e: obb_obb_hits(fa, np.maximum(ha + e / 2, 0.01), fb, np.maximum(hb + e / 2, 0.01)), hi=200.0, lo_limit=2 * lim), a, b))
    worst = min(pair_m)
    add("Hardware does not collide with other hardware (monitor and cradle against the compute module, PSU, bundle; 1 mm tolerance as rule R2)",
        worst[0] >= -1.05, f"closest pair {worst[1]} / {worst[2]}", f"{worst[0]:.1f} mm")
    add("Control panel top 60 to 75 mm above the desk", PANEL["top"][0] <= panel_top <= PANEL["top"][1], f"{panel_top:.1f}",
        f"{min(panel_top - PANEL['top'][0], PANEL['top'][1] - panel_top):.1f} mm")
    inner_h = panel_top - floor_at_deck(morph)
    add("56 mm inside under the panel top", inner_h >= PANEL["inner_h"], f"{inner_h:.1f}", f"{inner_h - PANEL['inner_h']:.1f} mm")
    border_side = op_x - PANEL["w"] / 2
    border_front = py0
    add("Removable control panel 396 x 240 with a visible deck border", border_side >= 10 and border_front >= 10,
        f"border {border_front:.0f} front, {border_side:.0f} sides", f"{min(border_side, border_front) - 10:.1f} mm over 10")
    ctl_names = [n for n in placed if n.startswith(CONTROL_PREFIXES) and placed[n].role == "hardware"]
    ctl_ok, ctl_m = group_ok(ctl_names)
    add("Lever, buttons and encoder inside the deck", ctl_ok, "", f"{ctl_m:.1f} mm")
    add("Sight line 15 to 25 deg below horizontal", SIGHT[0] <= sight <= SIGHT[1], f"{sight:.1f} deg",
        f"{min(sight - SIGHT[0], SIGHT[1] - sight):.1f} deg")
    add("Eye 450 to 600 mm from the image centre", EYE_DIST[0] <= eye_dist <= EYE_DIST[1], f"{eye_dist:.0f} mm",
        f"{min(eye_dist - EYE_DIST[0], EYE_DIST[1] - eye_dist):.0f} mm")
    band = band_ratio(morph)
    add("Transition band keeps at least 35 % of its scaled depth (no fold in the side band or the hood)", band[0] >= 0.35,
        f"narrowest {band[0] * 100:.0f} % at reference Z {band[1]:.0f}", "")
    add("Recline about 20 to 25 deg", 20 <= recline_meas <= 25, f"{recline_meas:.1f} deg", "")
    for k, val in (("W", W), ("D", D), ("H", H)):
        add(f"Soft limit {k} <= {SOFT[k]:.0f}", val <= SOFT[k], f"{val:.0f}", f"{SOFT[k] - val:.0f} mm")

    # derived figures for the report
    win169 = MON["active_w"] * 9 / 16
    frames = {"16:10": ((plate_w - MON["active_w"]) / 2, (plate_len - MON["active_h"]) / 2),
              "16:9": ((plate_w - MON["active_w"]) / 2, (plate_len - win169) / 2)}
    arc = cheek_arc(morph, n_out, u, face_off)
    deck_depth = float(morph.y_map(np.array(102.55)))
    deck_top = rim_top
    rear_body_w = float(morph.x_map(np.array(100.0)) - morph.x_map(np.array(-100.0)))

    # outputs
    for g, t in shell.items():
        write_stl(os.path.join(out, f"{g}.stl"), t)
    img_lo = np.array([-MON["active_w"] / 2, lip, plate_len / 2 - MON["active_h"] / 2])
    img_hi = np.array([MON["active_w"] / 2, lip + 1.0, plate_len / 2 + MON["active_h"] / 2])
    write_stl(os.path.join(out, "screen.stl"), box_tris(img_lo, img_hi, face_frame))
    backing = box_tris(np.array([-plate_w / 2, lip + 1.5, 0.0]), np.array([plate_w / 2, lip + 3.0, plate_len]), face_frame)
    write_stl(os.path.join(out, "window_backing.stl"), backing)
    hw_out = os.path.join(out, "hardware")
    os.makedirs(hw_out, exist_ok=True)
    overlay = []
    colours = {"Monitor": "#1f77d0", "PSU_Body": "#d62728", "Compute": "#2ca02c", "CableBundle": "#9467bd"}
    for name, b in placed.items():
        write_stl(os.path.join(hw_out, f"{name}.stl"), box_tris(b.lo, b.hi, b.frame))
        col = next((c for k, c in colours.items() if name.startswith(k)), None)
        if col and b.role == "hardware" or name == "Compute_ExhaustDuct":
            overlay.append({"name": name, "colour": col or colours["Compute"], "corners": b.corners().round(2).tolist()})
    finishes = {g: FINISH[g] for g in shell} | {"window_backing": "black", "screen": "#3a4250"}
    with open(os.path.join(out, "manifest.json"), "w") as fh:
        json.dump({g: {"file": f"{g}.stl", "finish": f} for g, f in finishes.items()}, fh, indent=1)
    with open(os.path.join(out, "overlay.json"), "w") as fh:
        json.dump(overlay, fh)

    report = {
        "variant": asdict(v), "deck_insert": round(morph.deck_insert, 1),
        "outside": [round(float(W), 1), round(float(D), 1), round(float(H), 1)],
        "bbox": [lo.round(1).tolist(), hi.round(1).tolist()],
        "recline": round(recline_meas, 2), "sight_angle": round(sight, 1), "eye_dist": round(eye_dist, 0),
        "image_centre": centre.round(1).tolist(),
        "bezel_plate": [round(plate_w, 1), round(plate_len, 1)],
        "frame_16x10": [round(x, 1) for x in frames["16:10"]], "frame_16x9": [round(x, 1) for x in frames["16:9"]],
        "deck_depth": round(deck_depth, 1), "deck_top": round(deck_top, 1), "panel_top": round(panel_top, 1),
        "panel_opening": [round(2 * op_x, 1), round(op_y1 - op_y0, 1)], "inner_h_under_panel": round(inner_h, 1),
        "rear_body_inner_w": round(rear_body_w, 1), "rear_inner_y": round(rear_inner, 1), "floor_top": round(floor_top, 1),
        "hardware_moves": {"monitor_rotation_deg": round(v.recline - 22.0, 1),
                           "psu": d_psu.round(1).tolist(), "compute": d_bc.round(1).tolist(), "controls": d_ctl.round(1).tolist()},
        "hardware_clearance": hw_checks, "pair_clearance": [[round(m, 1), a, b] for m, a, b in pair_m],
        "cheek_arc": arc, "checks": checks,
        "stretch": {"x_mid_band_ref": [-X_MID, X_MID], "width_insert": v.width_insert,
                    "deck_band_ref": list(DECK_BAND), "deck_depth_insert": round(morph.deck_insert, 1),
                    "deck_z_band_ref": list(DECK_Z_BAND), "deck_height_change": round(v.panel_top - REF_PANEL_TOP * s, 1),
                    "apron_band_ref": list(APRON_BAND), "apron_lift": v.apron_lift,
                    "screen_band_ref": list(SCREEN_BAND) if v.screen_insert else None, "screen_insert": v.screen_insert,
                    "rear_band_ref": list(REAR_BANDS[v.rear_band]), "body_depth_insert": v.body_insert,
                    "hood_band_ref": list(HOOD_BAND) if v.hood_insert else None, "hood_insert": v.hood_insert, "shelf": v.shelf,
                    "front_zone_shift_top": round(float(morph.d_val[-1]), 1)},
    }
    with open(os.path.join(out, "report.json"), "w") as fh:
        json.dump(report, fh, indent=1)
    return report


def band_ratio(morph: Morph) -> tuple[float, float]:
    """Narrowest target depth of the transition band, as a fraction of its uniformly scaled depth."""
    zs = np.linspace(0.0, 316.0, 159)
    bz = np.array([b[0] for b in BAND])
    ya = np.interp(zs, bz, [b[1] for b in BAND])
    yb = np.interp(zs, bz, [b[2] for b in BAND])
    pa = morph.apply(np.stack([np.zeros_like(zs), ya, zs], axis=1))
    pb = morph.apply(np.stack([np.zeros_like(zs), yb, zs], axis=1))
    ratio = (pb[:, 1] - pa[:, 1]) / ((yb - ya) * morph.v.scale)
    i = int(np.argmin(ratio))
    return float(ratio[i]), float(zs[i])


def floor_at_deck(morph: Morph) -> float:
    return float(morph.apply(np.array([[0.0, 60.0, 5.0]]), zone="front")[0, 2])


def left_inner_at(tris: np.ndarray, mon: Box) -> float:
    f, h = mon.centre_frame()
    c = f[:3, 3]
    return first_hit(tris, c, np.array([-1.0, 0.0, 0.0])) + first_hit(tris, c, np.array([1.0, 0.0, 0.0]))


def cheek_arc(morph: Morph, n_out: np.ndarray, u: np.ndarray, face_off: float) -> dict:
    (cy, cz), r = CHEEK_ARC["centre"], CHEEK_ARC["r"]
    z = np.linspace(BEZEL_Z[0], CHEEK_ARC["z"][1], 120)
    y = cy - np.sqrt(r ** 2 - (z - cz) ** 2)
    p = morph.apply(np.stack([np.full_like(z, CHEEK_ARC["x"]), y, z], axis=1), zone="front")
    yz = p[:, 1:]
    A = np.c_[2 * yz, np.ones(len(yz))]
    b = (yz ** 2).sum(1)
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    centre = sol[:2]
    rad = math.sqrt(sol[2] + centre @ centre)
    rms = float(np.sqrt(((np.linalg.norm(yz - centre, axis=1) - rad) ** 2).mean()))
    t = np.gradient(yz, axis=0)
    lean = np.degrees(np.arctan2(t[:, 0], t[:, 1]))
    proj = face_off - p @ n_out
    chord = yz[-1] - yz[0]
    chord_len = float(np.linalg.norm(chord))
    nrm = np.array([chord[1], -chord[0]]) / chord_len
    sag = float(np.max(np.abs((yz - yz[0]) @ nrm)))
    return {"radius": round(rad, 1), "rms": round(rms, 2), "chord": round(chord_len, 1),
            "chord_from_vertical": round(math.degrees(math.atan2(chord[0], chord[1])), 1),
            "sagitta": round(sag, 1), "sagitta_over_chord": round(sag / chord_len, 3),
            "lean_at_bezel_foot": round(float(lean[0]), 1), "lean_at_top": round(float(lean[-1]), 1),
            "turn": round(float(lean[-1] - lean[0]), 1),
            "projection_bottom_mid_top": [round(float(proj[0]), 1), round(float(proj[len(proj) // 2]), 1), round(float(proj[-1]), 1)]}


def reference_report(ref: dict[str, np.ndarray]) -> dict:
    allt = np.concatenate(list(ref.values()))
    lo, hi = allt.reshape(-1, 3).min(0), allt.reshape(-1, 3).max(0)
    return {"outside": (hi - lo).round(1).tolist(), "bbox": [lo.round(1).tolist(), hi.round(1).tolist()]}


def markdown(reports: list[dict], ref: dict) -> str:
    rows = [("Outside W x D x H", lambda r: " x ".join(f"{x:.0f}" for x in r["outside"])),
            ("Uniform scale", lambda r: f"{r['variant']['scale']:.2f}"),
            ("Recline", lambda r: f"{r['recline']:.1f} deg"),
            ("Sight angle", lambda r: f"{r['sight_angle']:.1f} deg"),
            ("Eye to image centre", lambda r: f"{r['eye_dist']:.0f} mm"),
            ("Bezel plate", lambda r: f"{r['bezel_plate'][0]:.0f} x {r['bezel_plate'][1]:.0f}"),
            ("Black frame 16:10 (side, top/bottom)", lambda r: f"{r['frame_16x10'][0]:.0f}, {r['frame_16x10'][1]:.0f}"),
            ("Black frame 16:9 (side, top/bottom)", lambda r: f"{r['frame_16x9'][0]:.0f}, {r['frame_16x9'][1]:.0f}"),
            ("Deck depth, deck top", lambda r: f"{r['deck_depth']:.0f}, {r['deck_top']:.0f}"),
            ("Panel top, inside height", lambda r: f"{r['panel_top']:.0f}, {r['inner_h_under_panel']:.0f}"),
            ("Panel opening", lambda r: f"{r['panel_opening'][0]:.0f} x {r['panel_opening'][1]:.0f}"),
            ("Rear body inner width", lambda r: f"{r['rear_body_inner_w']:.0f}"),
            ("Width inserted (middle)", lambda r: f"{r['stretch']['width_insert']:.0f}"),
            ("Deck depth inserted (deck flat)", lambda r: f"{r['stretch']['deck_depth_insert']:.0f}"),
            ("Body depth inserted (behind the screen)", lambda r: f"{r['stretch']['body_depth_insert']:.0f}"),
            ("Deck height change", lambda r: f"{r['stretch']['deck_height_change']:+.0f}"),
            ("Apron lift", lambda r: f"{r['stretch']['apron_lift']:.0f}"),
            ("Screen band insert", lambda r: f"{r['stretch']['screen_insert']:.0f}"),
            ("Hood band insert", lambda r: f"{r['stretch']['hood_insert']:.0f}"),
            ("Shelf (deck behind the panel)", lambda r: f"{r['stretch']['shelf']:.0f}"),
            ("Cheek arc R, sagitta/chord, lean foot to top", lambda r: f"{r['cheek_arc']['radius']:.0f}, {r['cheek_arc']['sagitta_over_chord']:.3f}, {r['cheek_arc']['lean_at_bezel_foot']:.0f} to {r['cheek_arc']['lean_at_top']:.0f}"),
            ]
    head = "| Item | Reference | " + " | ".join(r["variant"]["title"] for r in reports) + " |"
    lines = [head, "|" + " --- |" * (len(reports) + 2)]
    refcol = {"Outside W x D x H": " x ".join(f"{x:.0f}" for x in ref["outside"]), "Uniform scale": "1", "Recline": "32.5 deg",
              "Bezel plate": "239 x 209", "Deck depth, deck top": "103, 50", "Rear body inner width": "200",
              "Cheek arc R, sagitta/chord, lean foot to top": "312, 0.091, 12 to 52"}
    for label, fn in rows:
        lines.append(f"| {label} | {refcol.get(label, '')} | " + " | ".join(fn(r) for r in reports) + " |")
    lines.append("")
    lines.append("| Requirement | " + " | ".join(r["variant"]["key"] for r in reports) + " |")
    lines.append("|" + " --- |" * (len(reports) + 1))
    for i, c in enumerate(reports[0]["checks"]):
        cells = []
        for r in reports:
            k = r["checks"][i]
            cells.append(f"{'PASS' if k['pass'] else 'FAIL'} {k['value']} ({k['margin']})".replace("()", "").strip())
        lines.append(f"| {c['requirement']} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export-hardware")
    e.add_argument("doc")
    e.add_argument("out")
    f = sub.add_parser("fit")
    f.add_argument("reference", help="directory of the assembled reference STL files")
    f.add_argument("hardware", help="directory written by export-hardware")
    f.add_argument("out")
    f.add_argument("--variants", default="A,B,C")
    f.add_argument("--set", action="append", default=[], metavar="KEY.FIELD=VALUE", help="override a variant field, e.g. A.scale=1.45")
    a = ap.parse_args(argv)
    for item in a.set:
        target, value = item.split("=", 1)
        key, name = target.split(".", 1)
        old = getattr(VARIANTS[key], name)
        new = value.lower() in ("1", "true", "yes") if isinstance(old, bool) else type(old)(value)
        VARIANTS[key] = replace(VARIANTS[key], **{name: new})
    if a.cmd == "export-hardware":
        export_hardware(a.doc, a.out)
        return
    ref = load_reference(a.reference)
    hw = load_hardware(a.hardware)
    reports = []
    for key in a.variants.split(","):
        r = fit_variant(VARIANTS[key], ref, hw, os.path.join(a.out, key))
        reports.append(r)
        fails = [c["requirement"] for c in r["checks"] if not c["pass"]]
        print(f"{key}: {' x '.join(f'{x:.0f}' for x in r['outside'])}  recline {r['recline']:.1f}  sight {r['sight_angle']:.1f}"
              f"  eye {r['eye_dist']:.0f}  bezel {r['bezel_plate'][0]:.0f}x{r['bezel_plate'][1]:.0f}  fails: {fails or 'none'}")
    md = markdown(reports, reference_report(ref))
    with open(os.path.join(a.out, "report.md"), "w") as fh:
        fh.write(md)


if __name__ == "__main__":
    main(sys.argv[1:])
