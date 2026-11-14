#!/usr/bin/env bash
# Build the model: the outer form of the blueprint shell, in two steps:
#   1. headless (candybar.shell.solids): one BREP and one STL file for each part, a STEP file of all parts,
#      the manifest and the report of the parts;
#   2. offscreen GUI (candybar.shell.viewdoc): shell.FCStd, the document to open in FreeCAD. A document that
#      is saved headless opens with every solid hidden.
# Exits non-zero when a part is not one valid solid or a step breaks.
# cad/check.sh runs the checks of the design on this build.
#
# Usage: cad/build.sh
#   CANDYBAR_OUT  output directory (default: cad/out/shell-rev7)
set -eu

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
if [ $# -gt 0 ]; then
  echo "usage: $0" >&2
  exit 2
fi
export CANDYBAR_OUT=${CANDYBAR_OUT:-$here/out/shell-rev7}

# The part files of an earlier build go first. If this build breaks, they would stay and look current.
# The fit study, the split and the skin cache are in directories of their own and stay.
rm -f "$CANDYBAR_OUT"/*.brep "$CANDYBAR_OUT"/*.stl "$CANDYBAR_OUT/shell.step" "$CANDYBAR_OUT/shell.FCStd" \
  "$CANDYBAR_OUT/manifest.json" "$CANDYBAR_OUT/report.json" "$CANDYBAR_OUT/focus.json" "$CANDYBAR_OUT/edges.json"

"$here/candybar/freecad-run.sh" candybar.shell.solids
if ! "$here/candybar/freecad-run.sh" --gui candybar.shell.viewdoc; then
  echo "View step failed: $CANDYBAR_OUT has no shell.FCStd." >&2
  exit 1
fi
