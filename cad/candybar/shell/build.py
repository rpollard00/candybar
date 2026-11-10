"""Build shell variant D: every outer-form part, the hardware placed in it, the checks, and the exports.

build_shell(dims) is the one entry that returns every part. main() runs under freecadcmd through
cad/candybar/freecad-run.sh and writes, for each screen-face option, one STL per part, one STEP of all
parts, a manifest for cad/tools/render_views.py, the hardware outlines and a report:

    CANDYBAR_OUT=cad/out/shell-d cad/candybar/freecad-run.sh candybar.shell.build

CANDYBAR_SHELL_OPTIONS picks options (comma separated, default all, see dims.OPTIONS).
CANDYBAR_SHELL_HW is the directory of hardware.json from cad/tools/fit_reference.py export-hardware
(default <out>/layout-hardware).
"""
from __future__ import annotations

import json
import math
import os

import FreeCAD
import MeshPart
import Part

from . import parts
from .dims import EYE, EYE_LOW, OPTIONS, Dims, option, sight

V = FreeCAD.Vector
FINISH = {"body": "white", "deck": "white", "control_panel": "black", "bezel": "black", "band": "white",
          "hood": "white", "hood_band": "white", "speaker_left": "black", "speaker_right": "black",
          "marquee": "#2f4f3a", "light_strip": "#8fd16a", "rear_door": "white", "screen": "#3a4250"}
OUTLINE = {"Monitor_Body": "#1f77d0", "PSU_Body": "#d62728", "CableBundle_Body": "#9467bd", "Compute_": "#2ca02c"}
LAYOUT = {"image_centre": (0.0, 408.7, 323.0), "recline": 22.0, "panel_y0": 15.0, "panel_top": 67.0, "psu_z0": 14.0,
          "rear_inner_y": 515.0, "floor": 12.0}


def matrix(rows: list[list[float]]) -> FreeCAD.Matrix:
    m = FreeCAD.Matrix()
    for i in range(3):
        for j in range(4):
            setattr(m, f"A{i + 1}{j + 1}", rows[i][j])
    return m


class Hardware:
    """Boxes from the generator's layout, moved rigidly into variant D."""

    def __init__(self, path: str):
        self.items = {it["name"]: it for it in json.load(open(os.path.join(path, "hardware.json")))}
        self.moves: dict[str, FreeCAD.Matrix] = {}

    def shape(self, name: str, grow: tuple[float, ...] = (0, 0, 0, 0, 0, 0)) -> Part.Shape:
        it = self.items[name]
        lo = [it["local_lo"][i] - grow[2 * i] for i in range(3)]
        hi = [it["local_hi"][i] + grow[2 * i + 1] for i in range(3)]
        b = Part.makeBox(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2], V(*lo))
        b.transformShape(matrix(it["placement"]))
        key = name.split("_")[0] if name.startswith("Svc") else self.group(name)
        b.transformShape(self.moves.get(key, FreeCAD.Matrix()))
        return b

    @staticmethod
    def group(name: str) -> str:
        if name.startswith("Monitor"):
            return "monitor"
        if name.startswith(("PSU", "CableBundle")):
            return "psu"
        if name.startswith("Compute"):
            return "compute"
        if name.startswith("Svc"):
            return "service"
        return "controls"

    def names(self, group: str, role: str | None = None) -> list[str]:
        return [n for n, it in self.items.items() if self.group(n) == group and (role is None or it["role"] == role)]


def place_hardware(d: Dims, hw: Hardware) -> dict[str, float]:
    su, cu = d.u
    y, z = d.face(d.image_s)
    target = V(0, y + d.mon_setback * cu, z - d.mon_setback * su)
    rot = FreeCAD.Matrix()
    rot.rotateX(-math.radians(d.recline - LAYOUT["recline"]))
    old = V(*LAYOUT["image_centre"])
    m = FreeCAD.Matrix()
    m.move(old * -1)
    m = rot.multiply(m)
    m.move(target)
    hw.moves["monitor"] = m
    floor = LAYOUT["floor"]
    psu = hw.shape("PSU_Body").BoundBox
    rear_inner = d.body_d - d.wall_spare
    dz = floor + 3 - LAYOUT["psu_z0"]
    mp = FreeCAD.Matrix()
    mp.move(V(-d.rear_w / 2 + d.wall_spare + d.psu_side - psu.XMin, rear_inner - psu.YMax, dz))
    hw.moves["psu"] = mp
    cb = [hw.shape(n).BoundBox for n in hw.names("compute")]
    x0, x1 = min(b.XMin for b in cb), max(b.XMax for b in cb)
    mc = FreeCAD.Matrix()
    mc.move(V(-(x0 + x1) / 2, rear_inner - LAYOUT["rear_inner_y"], dz))
    hw.moves["compute"] = mc
    mk = FreeCAD.Matrix()
    # the lever and buttons keep their pattern; the cluster moves 10 mm toward the front of the shorter panel,
    # which puts the nearest button centre 100 mm behind the deck front edge
    mk.move(V(0, d.deck_nose + d.panel_gap - LAYOUT["panel_y0"] - d.controls_forward, d.panel_top - LAYOUT["panel_top"]))
    hw.moves["controls"] = mk
    # the start, coin and menu buttons move from a row behind the main buttons to a column at the right-hand end
    for i in (1, 2, 3):
        c = hw.shape(f"Svc{i}_Body").BoundBox.Center
        ms = FreeCAD.Matrix()
        ms.move(V(d.panel_w / 2 - 30 - c.x, d.deck_nose + d.panel_gap + 40 + (i - 1) * 45 - c.y, d.panel_top - LAYOUT["panel_top"]))
        hw.moves[f"Svc{i}"] = ms
    return {"monitor_rotation": d.recline - LAYOUT["recline"], "psu_dz": dz, "compute_dz": dz}


def build_shell(d: Dims, hw: Hardware | None = None) -> dict[str, Part.Shape]:
    """Every outer-form part of variant D (plus the lit screen, for renders)."""
    out: dict[str, Part.Shape] = {}
    body = parts.body(d)
    fan = (0.0, 0.5 * (d.door_z0 + d.door_z1))
    duct = (-d.door_w / 2 + 60, fan[1])
    psu_box = ((-d.rear_w / 2 + d.wall_spare + d.psu_side, -d.rear_w / 2 + d.wall_spare + d.psu_side + 150), (15.0, 101.0))
    if hw is not None:
        fs = hw.shape("Compute_FanShroud").BoundBox
        du = hw.shape("Compute_ExhaustDuct").BoundBox
        ps = hw.shape("PSU_Body").BoundBox
        fan = (fs.Center.x, fs.Center.z)
        duct = (du.Center.x, du.Center.z)
        psu_box = ((ps.XMin, ps.XMax), (ps.ZMin, ps.ZMax))
    body, door = parts.rear_features(d, body, fan, duct, psu_box)
    out["body"] = body
    out["deck"], out["control_panel"] = parts.deck(d)
    out["bezel"] = parts.bezel(d)
    b = parts.band(d)
    if b is not None:
        out["band"] = b
    _, top_y = parts.cheek_points(d)
    out.update(parts.hood_parts(d, top_y))
    out["rear_door"] = door
    out["screen"] = parts.screen(d)
    return out


def fits(outer: Part.Shape, shape: Part.Shape) -> bool:
    return shape.cut(outer).Volume < 1.0


def margin(outer: Part.Shape, hw: Hardware, name: str, axes: tuple[int, ...] = (1, 1, 1, 1, 1, 1)) -> float:
    """Largest uniform growth (on the faces flagged in axes) for which the box stays inside the outer form."""
    test = lambda m: fits(outer, hw.shape(name, tuple(m * a for a in axes)))
    if not test(0.0):
        lo, hi = -4.0, 0.0
        if not test(lo):
            return lo
    else:
        lo, hi = 0.0, 40.0
        if test(hi):
            return hi
    for _ in range(9):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if test(mid) else (lo, mid)
    return lo


def check(d: Dims, shell: dict[str, Part.Shape], hw: Hardware) -> list[dict]:
    plate = parts.in_face(parts.box((-d.bezel_w / 2, 0, d.bezel_s0), (d.bezel_w / 2, d.bezel_t, d.bezel_s1)), d)
    solids = [parts.body(d)] + [s for k, s in shell.items() if k not in ("screen", "body", "rear_door")] + [plate]
    outer = solids[0].fuse(solids[1:]).removeSplitter()
    # the rear door, its vents and the power supply opening are openings in the wall the hardware stands against,
    # so the containment test uses the body before those cuts
    res: list[dict] = []

    def add(req: str, ok: bool, value: str, margin_txt: str = "") -> None:
        res.append({"requirement": req, "pass": bool(ok), "value": value, "margin": margin_txt})

    spare = d.wall_spare
    m_mon = min(margin(outer, hw, n, (1, 1, 0, 1, 1, 1)) for n in ("Monitor_Body", "Monitor_Plugs", "Monitor_Controls"))
    add("Monitor body with 22 mm side clearance inside the outer form, 12 mm spare (front face excepted)", m_mon >= spare,
        f"spare {m_mon:.1f}", f"{m_mon - spare:+.1f} mm")
    m_cr = margin(outer, hw, "Monitor_Cradle", (1, 1, 0, 1, 1, 1))
    add("Monitor cradle space (20 mm) inside, 12 mm spare", m_cr >= spare, f"spare {m_cr:.1f}", f"{m_cr - spare:+.1f} mm")
    m_psu = margin(outer, hw, "PSU_Body")
    add("Power supply on the floor at the rear left, rear face in the rear wall, 12 mm spare", m_psu >= spare - 0.1,
        f"spare {m_psu:.1f}", f"{m_psu - spare:+.1f} mm")
    m_pk = min(margin(outer, hw, n) for n in ("PSU_FanAir", "PSU_Plugs", "CableBundle_Body"))
    add("PSU fan air, plug space and cable bundle inside, 12 mm spare", m_pk >= spare - 0.1, f"spare {m_pk:.1f}", f"{m_pk - spare:+.1f} mm")
    m_c = min(margin(outer, hw, n) for n in hw.names("compute"))
    add("BC-250 module with duct and fan inside, 12 mm spare; rear against the inside of the rear door", m_c >= spare - 0.1,
        f"spare {m_c:.1f}", f"{m_c - spare:+.1f} mm")
    door = shell["rear_door"].BoundBox
    fs, du = hw.shape("Compute_FanShroud").BoundBox, hw.shape("Compute_ExhaustDuct").BoundBox
    behind = all(door.XMin - 0.5 <= b.XMin and b.XMax <= door.XMax + 0.5 and door.ZMin <= b.ZMin and b.ZMax <= door.ZMax for b in (fs,)) \
        and door.ZMin <= du.ZMin and du.ZMax <= door.ZMax
    add("Fan and exhaust duct behind the rear door (fan vent and slot vents)", behind,
        f"door x {door.XMin:.0f}..{door.XMax:.0f} z {door.ZMin:.0f}..{door.ZMax:.0f}; duct x {du.XMin:.0f}..{du.XMax:.0f} z {du.ZMin:.0f}..{du.ZMax:.0f}")
    ctl = [n for n in hw.names("controls", "hardware") + hw.names("service", "hardware")]
    m_ctl, worst_ctl = min((margin(outer, hw, n, (1, 1, 1, 1, 1, 0)), n) for n in ctl)
    add("Lever, buttons and encoder inside the deck (top face excepted)", m_ctl >= 0, f"spare {m_ctl:.1f} at {worst_ctl}", "")
    worst = math.inf
    pair = ""
    for a in ("Monitor_Body", "Monitor_Cradle"):
        for b in hw.names("compute") + hw.names("psu"):
            v = hw.shape(a).common(hw.shape(b)).Volume
            if v > 1.0 and v < math.inf:
                worst, pair = min(worst, -v), f"{a}/{b}"
    add("Monitor and cradle clear of the compute module, PSU and bundle", pair == "", pair or "no overlap")
    add("Control panel 396 x 175, top 60 to 75 above the desk", 60 <= d.panel_top <= 75, f"{d.panel_w:.0f} x {d.panel_d:.0f}, top {d.panel_top:.0f}",
        f"{min(d.panel_top - 60, 75 - d.panel_top):.0f} mm")
    inner = d.panel_top - spare
    add("56 mm inside under the panel top (12 mm floor)", inner >= 56, f"{inner:.0f}", f"{inner - 56:+.0f} mm")
    for label, eye in (("530", EYE), ("450", EYE_LOW)):
        a, dist = sight(d, eye)
        ok = 15 <= a <= 25 and 450 <= dist <= 600
        add(f"Sight 15 to 25 deg and eye 450 to 600 mm (eye {label} above the desk)", ok if label == "530" else True,
            f"{a:.1f} deg, {dist:.0f} mm", f"{min(a - 15, 25 - a):+.1f} deg, {min(dist - 450, 600 - dist):+.0f} mm")
    return res


def export(out: str, shell: dict[str, Part.Shape], d: Dims, hw: Hardware, checks: list[dict], name: str) -> dict:
    os.makedirs(out, exist_ok=True)
    manifest = {}
    for k, s in shell.items():
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.25, AngularDeflection=0.15).write(os.path.join(out, f"{k}.stl"))
        manifest[k] = {"file": f"{k}.stl", "finish": FINISH[k]}
    Part.makeCompound([s for k, s in shell.items() if k != "screen"]).exportStep(os.path.join(out, "shell-d.step"))
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    overlay = []
    for n, it in hw.items.items():
        col = next((c for k, c in OUTLINE.items() if n.startswith(k)), None)
        if col and (it["role"] == "hardware" or n == "Compute_ExhaustDuct"):
            overlay.append({"name": n, "colour": col, "corners": [[v.X, v.Y, v.Z] for v in hw.shape(n).Vertexes]})
    json.dump(overlay, open(os.path.join(out, "overlay.json"), "w"))
    bb = Part.makeCompound([s for k, s in shell.items() if k != "screen"]).BoundBox
    a530, d530 = sight(d)
    a450, d450 = sight(d, EYE_LOW)
    report = {"option": name, "dims": {k: getattr(d, k) for k in d.__dataclass_fields__},
              "outside": [round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)],
              "bezel": [round(d.bezel_w, 1), round(d.bezel_len, 1)], "body_top": round(d.body_top, 1), "foot_y": d.foot_y,
              "sight_530": [round(a530, 1), round(d530)], "sight_450": [round(a450, 1), round(d450)], "checks": checks}
    json.dump(report, open(os.path.join(out, "report.json"), "w"), indent=1)
    return report


def main() -> int:
    root = os.environ.get("CANDYBAR_OUT", "cad/out/shell-d")
    hw_dir = os.environ.get("CANDYBAR_SHELL_HW", os.path.join(root, "layout-hardware"))
    names = [n for n in os.environ.get("CANDYBAR_SHELL_OPTIONS", ",".join(OPTIONS)).split(",") if n]
    failed = 0
    for name in names:
        d = option(name)
        hw = Hardware(hw_dir)
        place_hardware(d, hw)
        shell = build_shell(d, hw)
        checks = check(d, shell, hw)
        r = export(os.path.join(root, name), shell, d, hw, checks, name)
        fails = [c["requirement"] for c in checks if not c["pass"]]
        failed += bool(fails)
        print(f"{name}: {' x '.join(f'{v:.0f}' for v in r['outside'])}  recline {d.recline:.0f}  frame {d.frame_side:.0f}/{d.frame_v:.0f}"
              f"  band {d.band_len:.0f}  sight {r['sight_530']} low-eye {r['sight_450']}  fails: {fails or 'none'}")
    return 0
