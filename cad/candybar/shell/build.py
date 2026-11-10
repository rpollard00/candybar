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

from . import hood, parts
from .dims import EYE, EYE_LOW, OPTIONS, Dims, option, sight

V = FreeCAD.Vector
FINISH = {"body": "white", "deck": "white", "control_panel": "black", "bezel": "black", "band": "white",
          "hood": "white", "hood_band": "white", "speaker_left": "black", "speaker_right": "black",
          "logo_plate": "#2f4f3a", "marquee_cover": "#5e9c46", "marquee": "#9be070", "rear_door": "white", "screen": "#3a4250"}
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


def build_shell(d: Dims, hw: Hardware | None = None, log: list[str] | None = None) -> dict[str, Part.Shape]:
    """Every outer-form part of variant D (plus the lit screen, for renders)."""
    log = [] if log is None else log
    out: dict[str, Part.Shape] = {}
    body, deck, panel = parts.body_and_deck(d, log)
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
    out["body"], out["deck"], out["control_panel"] = body, deck, panel
    out["bezel"] = parts.bezel(d)
    out.update(hood.hood_parts(d, log))
    out["rear_door"] = door
    out["screen"] = parts.screen(d)
    return out


def band_width_survey(d: Dims) -> list[tuple[str, float]]:
    """Width of the rail's flat facet, in sections across it, from the table up to the hood seam."""
    solid = parts.rail_solid(d, [])
    su, cu = d.u
    w = d.width
    stations = []
    s_top = (d.body_top - d.deck_top) / cu
    for s_ in [(20 - d.deck_top) / cu, (50 - d.deck_top) / cu] + [s_top * k for k in (0.15, 0.4, 0.65, 0.9)]:
        y, z = d.face(s_)
        stations.append((f"facet at z={z:.0f}", V(w / 2, y, z), V(0, su, cu)))
    out = []
    for name, p, n in stations:
        n.normalize()
        best = None
        for wire in solid.slice(n, n.dot(p)):
            for e in wire.Edges:
                a, b = e.Vertexes[0].Point, e.Vertexes[-1].Point
                if abs(e.Length - (b - a).Length) > 0.05:
                    continue
                if (a - p).Length < 45 and (b - p).Length < 45 and 15 < e.Length < 45:
                    if best is None or abs(e.Length - 28) < abs(best - 28):
                        best = e.Length
        out.append((name, round(best, 2) if best else -1.0))
    return out


def deck_section(d: Dims, deck: Part.Shape) -> list[list[float]]:
    """The deck's front edge in true side section at the centre line, as (y, z) points."""
    pts = []
    for wire in deck.slice(V(1, 0, 0), 0.0):
        for e in wire.Edges:
            for p in e.discretize(Distance=0.5):
                if p.y < 60:
                    pts.append([round(p.y, 3), round(p.z, 3)])
    return pts


def overhang_check(shell: dict[str, Part.Shape], d: Dims) -> dict:
    """No rail overhangs the deck: in front of the step line, the plan outline above deck height lies inside the
    outline under the band, and the front-view width is the same."""
    solids = [s for k, s in shell.items() if k in ("body", "deck")]
    fused = solids[0].fuse(solids[1:])
    z_cut = d.deck_top - d.band_drop - 2
    faces = [Part.Face(wr) for wr in fused.slice(V(0, 0, 1), z_cut)]
    prism = faces[0].extrude(V(0, 0, 2000)) if faces else None
    for f in faces[1:]:
        prism = prism.fuse(f.extrude(V(0, 0, 2000)))
    front = fused.common(parts.halfspace((0, d.step_y0 - 10, 0), (0, -1, 0)))
    above = common_z(front, d.deck_top + 0.5)
    outside = above.cut(prism).Volume if prism is not None else math.inf
    bb_all, bb_low = fused.BoundBox, common_z(fused, -1, z_cut).BoundBox
    return {"plan_volume_outside_mm3": round(outside, 2), "front_x_extent_all": [round(bb_all.XMin, 2), round(bb_all.XMax, 2)],
            "front_x_extent_below_band": [round(bb_low.XMin, 2), round(bb_low.XMax, 2)]}


def common_z(shape: Part.Shape, z0: float, z1: float | None = None) -> Part.Shape:
    s = shape.common(parts.halfspace((0, 0, z0), (0, 0, 1))) if z0 > -0.5 else shape
    return s.common(parts.halfspace((0, 0, z1), (0, 0, -1))) if z1 is not None else s


def hood_overhang(d: Dims, shell: dict[str, Part.Shape]) -> float:
    """Volume of the hood that lies outside the plan outline of the body top."""
    faces = [Part.Face(w) for w in shell["body"].slice(V(0, 0, 1), d.body_top - 0.05)]
    column = max(faces, key=lambda f: f.Area).extrude(V(0, 0, 400.0))
    return sum(shell[k].cut(column).Volume for k in shell if k.startswith(("hood", "speaker", "logo", "marquee")))


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
    plate = parts.in_face(parts.box((-d.bezel_w / 2, 0, d.bezel_s0), (d.bezel_w / 2, d.bezel_t + 2.0, d.bezel_s1)), d)
    solids = [parts.body_and_deck(d, [])[0]] + [s for k, s in shell.items() if k not in ("screen", "body", "rear_door")] + [plate]
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
    hs = hood.survey(d, shell)
    behind = hs["depth_behind_band_min"]
    add("At least 50 mm clear behind the hood band, inside the rear wall of the hood", behind >= 50.0, f"{behind:.1f}", f"{behind - 50:+.1f} mm")
    mw, mh = hs["marquee_window"]
    add("Marquee window straight, 32 to 40 mm high", 32.0 <= mh <= 40.0, f"{mw:.0f} x {mh:.0f}, {hs['marquee_modules']} modules of {d.marquee_module:.0f}",
        f"{min(mh - 32, 40 - mh):.0f} mm")
    add("The hood stands inside the outline of the body top", hood_overhang(d, shell) < 1.0, f"{hood_overhang(d, shell):.1f} mm3 outside")
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
              "bezel_top": list(d.face(d.bezel_s1)), "bezel_foot_line": list(d.face(d.bezel_s0)),
              "sight_530": [round(a530, 1), round(d530)], "sight_450": [round(a450, 1), round(d450)], "checks": checks}
    json.dump(report, open(os.path.join(out, "report.json"), "w"), indent=1)
    return report


def main() -> int:
    root = os.environ.get("CANDYBAR_OUT", "cad/out/shell-d")
    hw_dir = os.environ.get("CANDYBAR_SHELL_HW", os.path.join(root, "layout-hardware"))
    names = [n for n in os.environ.get("CANDYBAR_SHELL_OPTIONS", "3-short-band").split(",") if n]
    failed = 0
    for name in names:
        d = option(name)
        hw = Hardware(hw_dir)
        place_hardware(d, hw)
        log: list[str] = []
        shell = build_shell(d, hw, log)
        checks = check(d, shell, hw)
        r = export(os.path.join(root, name), shell, d, hw, checks, name)
        r["modelling_log"] = log
        r["band_width"] = band_width_survey(d)
        r["overhang"] = overhang_check(shell, d)
        json.dump(r, open(os.path.join(root, name, "report.json"), "w"), indent=1)
        json.dump({**parts.focus_points(d), **hood.focus_points(d)}, open(os.path.join(root, name, "focus.json"), "w"), indent=1)
        r["hood"] = hood.survey(d, shell)
        json.dump(hood.section_data(d, shell), open(os.path.join(root, name, "hood-section.json"), "w"))
        json.dump(r, open(os.path.join(root, name, "report.json"), "w"), indent=1)
        print("  hood:", r["hood"])
        json.dump({"points": deck_section(d, shell["deck"]), "dims": {k: getattr(d, k) for k in
                   ("deck_top", "deck_top_r", "deck_lean", "deck_lean_h", "bottom_r", "deck_corner", "deck_corner_r")}},
                  open(os.path.join(root, name, "deck-section.json"), "w"))
        widths = [w for _, w in r["band_width"] if w > 0]
        print("  log:", "; ".join(log))
        print("  band width:", r["band_width"])
        print(f"  facet flat width {min(widths):.2f} to {max(widths):.2f} over {len(widths)} of {len(r['band_width'])} stations; overhang {r['overhang']}")
        fails = [c["requirement"] for c in checks if not c["pass"]]
        failed += bool(fails)
        print(f"{name}: {' x '.join(f'{v:.0f}' for v in r['outside'])}  recline {d.recline:.0f}  frame {d.frame_side:.0f}/{d.frame_v:.0f}"
              f"  band {d.band_len:.0f}  sight {r['sight_530']} low-eye {r['sight_450']}  fails: {fails or 'none'}")
    return 0
