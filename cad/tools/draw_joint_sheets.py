"""The sheet of the second pass on the joints of the print pieces: the closing gap and the top ring (joint 7).

    CANDYBAR_OUT=cad/out/pieces cad/candybar/freecad-run.sh candybar.shell.joint_sheets
    cad/.venv-tools/bin/python cad/tools/draw_joint_sheets.py cad/out/pieces     # --no-render: compose only

It renders the scenes of <out>/joints-2/scenes with tools/render_views.py (Blender, one at a time under the lock of
tools/cad-lock.sh) and writes <out>/joints-2/joints-2.png. Every face edge is drawn.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compose_sheet import font  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
VIEWS = [  # (scene, view, caption)
    ("w1", "w1-inside", "The brow (white) at W1 R: its seam face and flange stand 0.5 back from upper R"),
    ("r5r3", "r5-inside", "Upper rear R (white) at R5, from above: 0.5 back from upper rear L (blue)"),
    ("r5r3", "r3-inside", "Upper rear R (white) at R3 R, from above: 0.5 back from upper R"),
    ("ring", "ring-along", "Joint 7 at x 150: the top ring under the body top, the foot of the hood (green) on it"),
    ("ring", "ring-front-cone", "Section at the front cone: the cone 8 x 3 on the ring, in the socket of the foot"),
    ("ring", "ring-rear-cone", "Section at the rear cone"),
]


def render(out: str) -> None:
    scenes = sorted({s for s, _, _ in VIEWS})
    for s in scenes:
        views = ",".join(v for sc, v, _ in VIEWS if sc == s)
        subprocess.run([os.path.join(HERE, "cad-lock.sh"), sys.executable, os.path.join(HERE, "render_views.py"),
                        os.path.join(out, "joints-2", "renders", s), os.path.join(out, "joints-2", "scenes", s), "--views", views, "--size", "1200"],
                       check=True)


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    out = os.path.abspath(args[0] if args else "cad/out/pieces")
    if "--no-render" not in argv:
        render(out)
    seams = json.load(open(os.path.join(out, "seams.json")))
    imgs = [(Image.open(os.path.join(out, "joints-2", "renders", s, f"{v}.png")).convert("RGB"), cap) for s, v, cap in VIEWS]
    cw = 760
    imgs = [(i.resize((cw, int(i.size[1] * cw / i.size[0]))), cap) for i, cap in imgs]
    ch = max(i.size[1] for i, _ in imgs)
    margin, gap, head, cap_h = 40, 30, 150, 50
    cols, rows = 3, 2
    width = 2 * margin + cols * cw + (cols - 1) * gap
    height = head + rows * (cap_h + ch + gap) + 220
    sheet = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(sheet)
    d.text((margin, 30), "The joints of the print pieces, second pass: the closing gap and the top ring (joint 7)", font=font(40, True), fill="black")
    d.text((margin, 85), "All sizes in mm. Face edges drawn. The pieces as built in cad/out/pieces.", font=font(22), fill="black")
    for k, (img, cap) in enumerate(imgs):
        x = margin + (k % cols) * (cw + gap)
        y = head + (k // cols) * (cap_h + ch + gap)
        words, line, lines_ = cap.split(), "", []
        for w in words:   # wrap the caption to the width of its view
            if d.textlength(line + " " + w, font=font(18, True)) > cw and line:
                lines_.append(line)
                line = w
            else:
                line = (line + " " + w).strip()
        lines_.append(line)
        for i, t in enumerate(lines_[:2]):
            d.text((x, y + i * 22 - 4), t, font=font(18, True), fill="black")
        sheet.paste(img, (x, y + cap_h))
    y = head + rows * (cap_h + ch + gap)
    closing = "; ".join(f"{c['piece']} at {', '.join(c['seams'])}: {c['removed_mm3']:g} mm3 off" for c in seams.get("closing", []))
    ring = {}
    for r in seams.get("ring", []):
        ring[r["piece"]] = ring.get(r["piece"], 0.0) + r["cm3"]
    lines = [f"Closing gap 0.5 (OtherJoints.closing_gap): {closing}. The grooves of the closing pieces have 0.5 at each side (middle R at L1).",
             "Top ring: 14 wide (ring_w), 6 thick (ring_t) with the gusset of joint 1; it rises 1.4 inside the wall to the foot, so that the seam gap of",
             "the form stays open outside. Foot of the hood: 14 wide, 6 thick (hood_foot_t). Bond line 0.1. Four cones 8 x 3 at x +-150, front and rear.",
             "Ring and foot, cm3: " + ", ".join(f"{k} {v:.1f}" for k, v in ring.items()),
             "Not modelled: the M4 inserts of a bolted hood (ring_h 12 at an insert): the way to reach their screws is not chosen."]
    for line in lines:
        d.text((margin, y), line, font=font(22), fill="black")
        y += 34
    path = os.path.join(out, "joints-2", "joints-2.png")
    sheet.save(path)
    print(f"draw_joint_sheets: {path}")
    if seams.get("hood_screws"):
        hood_sheet(out, seams, "--no-render" not in argv)
    return 0


HOOD_VIEWS = [("hood-reach", "reach", "The right side cut open inside its wall, the rear door off: the two screws of the side, a key of 3 (red) in each"),
              ("hood-reach", "reach-close", "The same, close: the boss under the ring, the screw, the key; the monitor (blue) stays in"),
              ("hood-screw", "screw", "Section through the front screw: the ring's boss, the screw, the insert's hole in the foot's boss")]


def hood_sheet(out: str, seams: dict, render_now: bool) -> None:
    """The sheet of the bolted hood: how a key from the rear door reaches each screw."""
    if render_now:
        for s in sorted({s for s, _, _ in HOOD_VIEWS}):
            views = ",".join(v for sc, v, _ in HOOD_VIEWS if sc == s)
            subprocess.run([os.path.join(HERE, "cad-lock.sh"), sys.executable, os.path.join(HERE, "render_views.py"),
                            os.path.join(out, "joints-2", "renders", s), os.path.join(out, "joints-2", "scenes", s), "--views", views, "--size", "1400"],
                           check=True)
    imgs = [(Image.open(os.path.join(out, "joints-2", "renders", s, f"{v}.png")).convert("RGB"), cap) for s, v, cap in HOOD_VIEWS]
    cw = 760
    imgs = [(i.resize((cw, int(i.size[1] * cw / i.size[0]))), cap) for i, cap in imgs]
    ch = max(i.size[1] for i, _ in imgs)
    margin, gap, head, cap_h = 40, 30, 150, 50
    width = 2 * margin + 3 * cw + 2 * gap
    rows = seams["hood_screws"]
    chk = os.path.join(out, "check.json")
    reach = json.load(open(chk)).get("hood_reach", []) if os.path.exists(chk) else []
    lines = ["Four screws M4 x 20, socket head (ISO 4762), from below: up through a boss of 13 under the ring (its seat 12 below the ring's top) into",
             "an M4 x 8.1 insert in a boss of 13 x 12 on the foot of the hood. One tool: a hex key of 3 (ball end), from inside the body with the rear door off.",
             "Places (x, y, seat z): " + "; ".join(f"({r['at'][0]:g}, {r['at'][1]:g}, {r['at'][2]:g})" for r in rows)]
    if reach:
        lines.append("Free straight under each head: " + ", ".join(f"{r['free']:g} (then {r['first'] or 'nothing'})" for r in reach))
    height = head + cap_h + ch + 40 + 34 * len(lines) + 40
    sheet = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(sheet)
    d.text((margin, 30), "The bolted hood: four screws from below, reached through the rear door", font=font(40, True), fill="black")
    d.text((margin, 85), "All sizes in mm. Face edges drawn. The pieces as built in cad/out/pieces.", font=font(22), fill="black")
    for k, (img, cap) in enumerate(imgs):
        x = margin + k * (cw + gap)
        words, line, wrapped = cap.split(), "", []
        for w in words:
            if d.textlength(line + " " + w, font=font(18, True)) > cw and line:
                wrapped.append(line)
                line = w
            else:
                line = (line + " " + w).strip()
        wrapped.append(line)
        for i, t in enumerate(wrapped[:2]):
            d.text((x, head + i * 22 - 4), t, font=font(18, True), fill="black")
        sheet.paste(img, (x, head + cap_h))
    y = head + cap_h + ch + 30
    for line in lines:
        d.text((margin, y), line, font=font(22), fill="black")
        y += 34
    path = os.path.join(out, "joints-2", "hood-screws.png")
    sheet.save(path)
    print(f"draw_joint_sheets: {path}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
