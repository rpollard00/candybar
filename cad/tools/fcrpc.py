#!/usr/bin/env python3
"""Command-line client for the FreeCAD MCP addon's XML-RPC server.

It gives a shell the same reach as the MCP tools: run Python inside the live FreeCAD
session and capture the 3D view.

    fcrpc.py ping
    fcrpc.py exec path/to/script.py
    fcrpc.py exec -c "print(FreeCAD.ActiveDocument.Name)"
    fcrpc.py shot out.png --view Isometric --width 1600 --height 1000
    fcrpc.py show [--keepouts]
"""
import argparse
import base64
import sys
import xmlrpc.client
from pathlib import Path

URL = "http://127.0.0.1:9875"
VIEWS = ["Isometric", "Front", "Top", "Right", "Back", "Left", "Bottom", "Dimetric", "Trimetric"]
SAVED = Path(__file__).resolve().parents[1] / "out" / "candybar.FCStd"

# An earlier copy of the document is closed first, unless it has unsaved
# changes: those belong to the person at the screen.
SHOW = """
import FreeCAD
import FreeCADGui

path = {path!r}
for open_doc in list(FreeCAD.listDocuments().values()):
    if open_doc.FileName != path:
        continue
    if FreeCADGui.getDocument(open_doc.Name).Modified:
        raise RuntimeError(open_doc.Name + " has unsaved changes. Save or close it in FreeCAD first.")
    FreeCAD.closeDocument(open_doc.Name)
doc = FreeCAD.openDocument(path)
if {keepouts!r}:
    for obj in doc.Objects:
        if getattr(obj, "CB_Role", "") == "keepout":
            obj.ViewObject.Visibility = True
    doc.recompute()
    FreeCADGui.getDocument(doc.Name).Modified = False
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
print("showing", path, "with", len(doc.Objects), "objects")
"""


def cmd_ping(server, _args):
    status = server.get_rpc_status()
    print(f"ok: addon {status.get('addon_version', '?')}")
    return 0


def cmd_exec(server, args):
    code = args.code if args.code is not None else Path(args.script).read_text()
    result = server.execute_code(code, args.timeout)
    print(result.get("message") or result.get("error") or result)
    return 0 if result.get("success") else 1


def cmd_shot(server, args):
    png = server.get_active_screenshot(args.view, args.width, args.height, args.focus)
    if not png:
        print("no image: the front tab in FreeCAD is not a 3D view", file=sys.stderr)
        return 1
    Path(args.out).write_bytes(base64.b64decode(png))
    print(args.out)
    return 0


def cmd_show(server, args):
    result = server.execute_code(SHOW.format(path=str(SAVED), keepouts=args.keepouts), 120)
    print(result.get("message") or result.get("error") or result)
    return 0 if result.get("success") else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("ping").set_defaults(run=cmd_ping)

    p_exec = sub.add_parser("exec")
    source = p_exec.add_mutually_exclusive_group(required=True)
    source.add_argument("script", nargs="?")
    source.add_argument("-c", dest="code")
    p_exec.add_argument("--timeout", type=int, default=300)
    p_exec.set_defaults(run=cmd_exec)

    p_shot = sub.add_parser("shot")
    p_shot.add_argument("out")
    p_shot.add_argument("--view", default="Isometric", choices=VIEWS)
    p_shot.add_argument("--width", type=int)
    p_shot.add_argument("--height", type=int)
    p_shot.add_argument("--focus")
    p_shot.set_defaults(run=cmd_shot)

    p_show = sub.add_parser("show", help="open cad/out/candybar.FCStd in the running FreeCAD")
    p_show.add_argument("--keepouts", action="store_true", help="also show the keep-out zones")
    p_show.set_defaults(run=cmd_show)

    args = parser.parse_args()
    server = xmlrpc.client.ServerProxy(URL, allow_none=True)
    try:
        return args.run(server, args)
    except ConnectionRefusedError:
        print(f"FreeCAD RPC server is not reachable at {URL}. Start it with cad/tools/freecad-gui.sh", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
