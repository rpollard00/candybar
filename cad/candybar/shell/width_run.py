"""Run the solids, the solids check, the cavity probe or the fit study on a wider variant (widths.widened).

    CANDYBAR_WIDEN=20 CANDYBAR_WIDEN_STEP=solids CANDYBAR_OUT=cad/out/shell-bp-w20 cad/candybar/freecad-run.sh candybar.shell.width_run

CANDYBAR_WIDEN is the extra width in mm (default 0); CANDYBAR_WIDEN_BAR is how much of it, on each side, goes into
the side bars of the bezel frame (default 0: all into the rail lands). CANDYBAR_WIDEN_STEP is solids, check, probe or fit. The
modules are the usual ones; only the Blueprint they build from is replaced, so the default model does not change.
The run refuses the output directory of the accepted model (cad/out/shell-bp).

probe builds the solids and the cavity and measures the cavity half width at the monitor's top corners and at
mid image (as fit.monitor_margins does), into <out>/probe.json, without the rest of the fit study.

At some of the wider variants this FreeCAD's makeOffset2D returns a null result (a ValueError, which cavity.inner
does not catch) for a whole side section near x 210. The run offsets that section with its edges made polygons
within 0.01 mm instead (tolerant_inner, which prints each case), and stops if that fails too.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from . import widths

STEPS = ("solids", "check", "probe", "fit")


def tolerant_inner() -> None:
    """When the offset of a side section fails, offset the same section with its edges made polygons within 0.01 mm
    (an offset of straight edges is robust); never drop a section silently (that would leave a gap in the cavity)."""
    import Part
    from . import cavity
    original = cavity.inner

    def polygonal(face):
        out = []
        for f in face.Faces:
            wires = [Part.makePolygon(w.discretize(Deflection=0.01) + [w.discretize(Deflection=0.01)[0]]) for w in [f.OuterWire] + [w for w in f.Wires if not w.isSame(f.OuterWire)]]
            out.append(Part.Face(wires[0]) if len(wires) == 1 else Part.makeFace(wires, "Part::FaceMakerBullseye"))
        return out[0] if len(out) == 1 else Part.makeCompound(out)

    def inner(face, x, w):
        try:
            return original(face, x, w)
        except ValueError:
            print(f"cavity: the section at x {x:.0f} is offset as polygons within 0.01")
            return original(polygonal(face), x, w)
    cavity.inner = inner


def probe(d, out: Path) -> int:
    from .. import params
    from . import cavity, fit
    from . import solids as so
    V = fit.V
    root = Path(os.environ.get("CANDYBAR_ROOT", Path(__file__).resolve().parents[2]))
    base = fit.sheet(params.load(root / "params"), "FitBase")
    v = lambda name: params.value(base, name)
    parts = so.build(d)
    cav = cavity.build(parts, d)
    hw = d.width / 2
    swept = v("mon_gen_w") / 2 + v("mon_adjust")
    rows = []
    for where, s in (("top corners", d.image_s + v("mon_gen_h") / 2 + v("mon_adjust")), ("middle of the image", d.image_s)):
        p = so.on_screen(d, 0.0, s, d.mon_setback + v("mon_gen_t") / 2)
        inner = hw + fit.RAY - fit.first_hit(cav.pieces, V(hw + fit.RAY, p.y, p.z), V(-1, 0, 0))
        rows.append({"where": where, "z": p.z, "cavity_half_width": inner,
                     "right_angle_needs": swept + v("mon_side_clear"), "straight_needs": swept + v("mon_side_clear_straight")})
    out.mkdir(parents=True, exist_ok=True)
    (out / "probe.json").write_text(json.dumps({"width": d.width, "plugs": rows}, indent=1), encoding="utf-8")
    for r in rows:
        print(f"{r['where']:20s} z {r['z']:.0f}  cavity half width {r['cavity_half_width']:.1f}  "
              f"right-angle needs {r['right_angle_needs']:.1f}  straight needs {r['straight_needs']:.1f}")
    return 0


def main() -> int:
    extra = float(os.environ.get("CANDYBAR_WIDEN", "0"))
    bar = float(os.environ.get("CANDYBAR_WIDEN_BAR", "0"))
    step = os.environ.get("CANDYBAR_WIDEN_STEP", "")
    out = Path(os.environ.get("CANDYBAR_OUT", "cad/out/shell-bp")).resolve()
    root = Path(os.environ.get("CANDYBAR_ROOT", Path(__file__).resolve().parents[2]))
    if step not in STEPS:
        raise SystemExit(f"CANDYBAR_WIDEN_STEP must be one of {', '.join(STEPS)}")
    if out == (root / "out" / "shell-bp").resolve():
        raise SystemExit("width_run does not write into cad/out/shell-bp, the accepted model: set CANDYBAR_OUT")
    d = widths.widened(extra, bar)
    widths.use_module_window()
    tolerant_inner()
    print(f"width {d.width:.1f} (+{extra:g}), land {d.land:.1f}, frame_side {d.frame_side:.1f}, rear_w {d.rear_w:.1f}, hood_h {d.hood_h:.1f}")
    if step == "probe":
        return probe(d, out)
    make = lambda: d
    if step == "check":
        from tools import check_solids
        check_solids.Blueprint = make
        return check_solids.main()
    from . import solids
    solids.Blueprint = make
    if step == "solids":
        return solids.main()
    from functools import partial
    from . import fit
    fit.Blueprint = make
    # behind the step the 1 mm slabs of the cavity leave the duct of the BC-250 at its side gap 0.35 into the skin at
    # +20; one more mm keeps it clear (fit.Layout.bc_side_gap, 4 in the accepted model)
    gap = float(os.environ.get("CANDYBAR_WIDEN_BC_GAP", "5"))
    fit.Layout = partial(fit.Layout, bc_side_gap=gap)
    print(f"fit.Layout bc_side_gap {gap}")
    return fit.main()
