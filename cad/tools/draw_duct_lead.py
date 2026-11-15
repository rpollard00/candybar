"""The sheets for the owner of the DisplayPort to HDMI adapter and the exhaust duct (docs/design/duct-lead-exit.md):
  1-way-1.png   the adapter straight in the board's socket
  2-way-2.png   a short extension lead, and the adapter on the left dock
  3-places.png  the places where a lead can leave the duct's zone, with the recommended one
Each sheet has a view from above and a view in perspective with the duct cut open, and its key numbers. Every face
edge is drawn.

    CANDYBAR_OUT=cad/out/duct-lead cad/candybar/freecad-run.sh candybar.shell.duct_lead
    cad/.venv-tools/bin/python cad/tools/draw_duct_lead.py cad/out/duct-lead    # --no-render: compose only

It renders the scenes with tools/render_views.py (Blender, one at a time under the lock of tools/cad-lock.sh).
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
SCENES = ("way-1", "way-2", "places")
VIEWS = {"plan": "From above, cut at z {cut_z:g} (above the adapter)", "open": "In perspective from the rear right, the duct cut open"}


def render(out: str) -> None:
    for scene in SCENES:
        for view in VIEWS:
            subprocess.run([os.path.join(HERE, "cad-lock.sh"), sys.executable, os.path.join(HERE, "render_views.py"),
                            os.path.join(out, "renders", scene), os.path.join(out, "scenes", scene, view), "--views", view, "--size", "1500"],
                           check=True)


def legend(n: dict) -> dict[str, tuple[str, list[str], list[tuple[str, str]]]]:
    a = n["adapter"]
    room = f"{n['room_beside_duct']:g} between the end wall of the duct and the side wall"
    return {
        "way-1": ("Way 1: the adapter straight in the board's DisplayPort socket", [
            f"The adapter (blue) is {a[0]:g} x {a[1]:g} x {a[2]:g}, measured. Its plug goes about {n['dp_in']:g} into the socket (ESTIMATED).",
            f"Its body then ends {n['adapter_to_end_wall']:g} before the end wall of the duct: all of it is in the hot exhaust air.",
            f"The HDMI plug (black, right-angle, about {n['hdmi_head'][0]:g} x {n['hdmi_head'][1]:g} x {n['hdmi_head'][2]:g}, ESTIMATED) must go through",
            f"an opening in the end wall (blue frame) and turn in the {room}.",
            f"After the plug, {n['hdmi_room_left']:g} are left to the side wall for the bend of the lead.",
            "Needs: a right-angle HDMI plug and a sealed opening in the end wall. The adapter stays hot.",
        ], [("#1f4e9c", "adapter"), ("#202020", "HDMI plug and lead"), ("#b9783a", "exhaust duct"), ("#d04040", "edge of the clear space over the PSU fan (z 121)")]),
        "way-2": ("Way 2: a short DisplayPort extension lead, and the adapter on the left dock", [
            f"The plug of the extension lead (about {n['ext_head'][0]:g} long, ESTIMATED) stays in the duct; only the lead leaves it, through place C.",
            f"The adapter stands in its place on the left dock (x {n['place_dp'][0]:g} to {n['place_dp'][1]:g}, z {n['place_dp'][4]:g} to {n['place_dp'][5]:g}), out of the hot air,",
            "its DisplayPort plug down.",
            f"FINDING: the in-line socket of the lead (about {n['ext_socket'][0]:g} long, ESTIMATED) then reaches down to z {n['ext_socket_low_z']:g}.",
            f"The clear space over the PSU fan starts at z {n['fan_space_top_z']:g}: {n['socket_in_fan_space_mm3']:g} mm3 of the socket is in it (red).",
            "Fix one of these before a build: the adapter turned over, a lead with a right-angle socket, or the place moved up.",
            "Measure the lead that the owner buys first.",
        ], [("#1f4e9c", "adapter"), ("#202020", "extension plug, lead and socket"), ("#d02020", "socket in the PSU fan space"), ("#d04040", "edge of the clear space over the PSU fan (z 121)")]),
        "places": ("Where a lead can leave the duct's zone", [
            "A (orange, partly behind C): a slot of 24 x 12 in the duct's floor, x -199 to -175, z 125 to 137. The plug must pass it on the bench.",
            "B (blue): a hole of 24 x 12 in the end wall, y 470 to 494, z 128 to 140. The lead then runs in the narrow room beside the side wall.",
            "C (green), RECOMMENDED: the cable notch moved to the front lower edge of the duct, x -200 to -175, 12 into the floor",
            "and 12 into the lower side wall. Open on two faces: no plug has to pass. All leads of the I/O end stay above",
            f"z {n['fan_space_top_z']:g} and do not cross the clear space over the PSU fan. Only the duct body changes.",
            f"The present notch (the open cut in the lower side wall, under the green mark, {n['present_notch'][1] - n['present_notch'][0]:g} wide) opens down into that space.",
        ], [("#e08a2a", "A"), ("#3a78c8", "B"), ("#2aa84a", "C (recommended)"), ("#d04040", "edge of the clear space over the PSU fan (z 121)")]),
    }


CAPTION = {"way-2": {"open": "From the left, the side wall left out: the adapter, the lead and its socket"}}


def sheet(out: str, scene: str, n: dict, title: str, lines: list[str], keys: list[tuple[str, str]], name: str) -> str:
    imgs = [Image.open(os.path.join(out, "renders", scene, f"{v}.png")).convert("RGB") for v in VIEWS]
    w = max(i.size[0] for i in imgs)
    scale = 1100 / w
    imgs = [i.resize((int(i.size[0] * scale), int(i.size[1] * scale))) for i in imgs]
    margin, gap, head = 40, 30, 120
    width = 2 * margin + sum(i.size[0] for i in imgs) + gap
    text_h = 40 + 34 * len(lines) + 50
    height = head + 50 + max(i.size[1] for i in imgs) + text_h + 40
    s = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(s)
    d.text((margin, 30), title, font=font(40, True), fill="black")
    d.text((margin, 82), "All sizes in mm, in the frame of the cabinet (x to the player's right, y to the rear, z up). Face edges drawn.",
           font=font(22), fill="black")
    x = margin
    for img, (v, cap) in zip(imgs, VIEWS.items()):
        d.text((x, head), CAPTION.get(scene, {}).get(v, cap).format(**n), font=font(24, True), fill="black")
        s.paste(img, (x, head + 40))
        x += img.size[0] + gap
    y = head + 50 + max(i.size[1] for i in imgs) + 10
    for line in lines:
        d.text((margin, y), line, font=font(26), fill="black")
        y += 34
    y += 12
    x = margin
    for colour, label in keys:
        d.rectangle((x, y, x + 28, y + 28), fill=colour, outline="black")
        d.text((x + 38, y), label, font=font(24), fill="black")
        x += 60 + int(d.textlength(label, font=font(24)))
    path = os.path.join(out, name)
    s.save(path)
    return path


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    out = os.path.abspath(args[0] if args else "cad/out/duct-lead")
    n = json.load(open(os.path.join(out, "scene.json")))
    if "--no-render" not in argv:
        render(out)
    for i, (scene, (title, lines, keys)) in enumerate(legend(n).items(), 1):
        print("draw_duct_lead:", sheet(out, scene, n, title, lines, keys, f"{i}-{scene}.png"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
