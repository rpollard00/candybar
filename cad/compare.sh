#!/usr/bin/env bash
# Compare the default build of the outer form with an accepted one (tools/compare_parts.py, tolerance 0.000001).
#
# The accepted outer form is the build of a commit: cad/BASELINE names it. The first run builds that commit's outer
# form once, from its own source (git archive), into cad/out/baseline/<commit>, and keeps it there. The comparison
# passes when no part moved and fails when one did, or when a part of the baseline has no partner.
#
# Usage: cad/compare.sh [commit] [build]
#   commit  the baseline (default: the commit in cad/BASELINE)
#   build   the folder of the build to compare (default: cad/out/shell-rev7, which cad/build.sh makes)
# The result goes to <build>/compare-<commit>/compare.md. One FreeCAD process runs at a time (freecad-run.sh).
set -eu

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
if [ $# -gt 2 ]; then
  echo "usage: $0 [commit] [build]" >&2
  exit 2
fi
rev=${1:-$(tr -d '[:space:]' < "$here/BASELINE")}
build=$(cd "${2:-$here/out/shell-rev7}" && pwd)
base=$here/out/baseline/$rev
if [ ! -f "$base/manifest.json" ]; then
  echo "building the outer form of $rev into $base"
  rm -rf "$base/src"
  mkdir -p "$base/src"
  git -C "$here/.." archive "$rev" cad/candybar cad/params cad/tools | tar -x -C "$base/src"
  CANDYBAR_OUT=$base "$base/src/cad/candybar/freecad-run.sh" candybar.shell.solids
fi
out=$build/compare-$rev
mkdir -p "$out"
CANDYBAR_A=$base CANDYBAR_B=$build CANDYBAR_OUT=$out CANDYBAR_TOL=${CANDYBAR_TOL:-0.000001} "$here/candybar/freecad-run.sh" tools.compare_parts
