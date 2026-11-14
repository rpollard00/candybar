#!/usr/bin/env bash
# Run the checks of the design on the build that cad/build.sh made:
#   tools.check_solids        the solids against the faces of the blueprint
#   tools.face_check          the faces of each part
#   tools.edge_finish         the convex edges that are still sharp
#   candybar.shell.fit        the fit study: the hardware in the cavity
#   candybar.shell.split      the split: each piece against the printer
#   candybar.shell.structure  the hardware in the skin, the walls of the hand-holds
# One FreeCAD process runs at a time. Each check runs, also after one that failed. The text of each check goes to
# <out>/check/<module>.txt. Exits 1 when a check fails, and 2 when there is no build.
#
# Usage: cad/check.sh
#   CANDYBAR_OUT  the directory of the build (default: cad/out/shell-rev7)
set -u

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
if [ $# -gt 0 ]; then
  echo "usage: $0" >&2
  exit 2
fi
export CANDYBAR_OUT=${CANDYBAR_OUT:-$here/out/shell-rev7}
if [ ! -f "$CANDYBAR_OUT/manifest.json" ]; then
  echo "No build in $CANDYBAR_OUT. Run cad/build.sh first." >&2
  exit 2
fi

mkdir -p "$CANDYBAR_OUT/check"
failed=0
for module in tools.check_solids tools.face_check tools.edge_finish candybar.shell.fit candybar.shell.split candybar.shell.structure; do
  text=$CANDYBAR_OUT/check/$module.txt
  start=$SECONDS
  if "$here/candybar/freecad-run.sh" "$module" >"$text" 2>&1; then
    echo "PASS $module ($((SECONDS - start)) s)"
  else
    echo "FAIL $module ($((SECONDS - start)) s): $text"
    failed=1
  fi
done
exit "$failed"
