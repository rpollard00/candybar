#!/usr/bin/env bash
# Build the cabinet layout in two steps:
#   1. headless: load the parameter sheets, generate the FreeCAD document,
#      check it, export it and draw the views;
#   2. offscreen GUI: store view settings in the saved document, so that it
#      opens in FreeCAD with the layout on show instead of every solid hidden.
# Exits non-zero when a check fails or either step breaks.
#
# Usage: cad/build.sh [--no-render]
#   CANDYBAR_PARAMS  parameter directory (default: cad/params)
#   CANDYBAR_OUT     output directory, overwritten (default: cad/out)
set -eu

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
for arg in "$@"; do
  case $arg in
    --no-render) export CANDYBAR_RENDER=0 ;;
    *) echo "usage: $0 [--no-render]" >&2; exit 2 ;;
  esac
done
export CANDYBAR_OUT=${CANDYBAR_OUT:-$here/out}
saved=$CANDYBAR_OUT/candybar.FCStd

# The build clears its own outputs, but only once Python runs. If FreeCAD dies
# before that, the outputs of an earlier build would stay and look current.
rm -rf "$saved" "$CANDYBAR_OUT/report.md" "$CANDYBAR_OUT/report.json" "$CANDYBAR_OUT/candybar.step" \
  "$CANDYBAR_OUT/step" "$CANDYBAR_OUT/stl" "$CANDYBAR_OUT/views"

built=0
"$here/candybar/freecad-run.sh" candybar.build || built=$?

# A design that fails its checks is still saved and still worth looking at.
# A build that broke before saving has no document to give view settings to.
if [ -f "$saved" ] && ! "$here/candybar/freecad-run.sh" --gui candybar.decorate; then
  echo "View step failed: $saved has no view settings and opens in FreeCAD with every solid hidden." >&2
  exit 1
fi
exit "$built"
