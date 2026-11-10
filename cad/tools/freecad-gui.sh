#!/usr/bin/env bash
# Start the FreeCAD GUI with the MCP addon's RPC server running.
# Any extra arguments (for example a .FCStd path) are passed to FreeCAD.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec freecad "$here/candybar_start_rpc.py" "$@"
