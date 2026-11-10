"""FreeCAD startup script: start the FreeCAD MCP addon's RPC server.

Run by `cad/tools/freecad-gui.sh`. The RPC server listens on 127.0.0.1:9875 and
executes Python sent to it, so it runs only when FreeCAD is started through that launcher.
"""
import FreeCAD
from rpc_server import rpc_server

FreeCAD.Console.PrintMessage("[candybar] " + str(rpc_server.start_rpc_server()) + "\n")
