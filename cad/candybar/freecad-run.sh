#!/usr/bin/env bash
# Usage: freecad-run.sh [--gui] <python.module>
# Calls <python.module>.main() inside FreeCAD and exits with the integer it returns.
#
# Without --gui it runs headless, under freecadcmd. With --gui it runs the GUI
# binary on Qt's offscreen platform: view providers exist, no window opens.
#
# FreeCAD's own exit status does not follow Python errors, so the result
# travels through a status file, and a missing result counts as a failure.
# Each run gets a fresh FreeCAD user directory inside the output directory and
# removes it afterwards, so it neither reads nor rewrites ~/.config/FreeCAD,
# loads no addon, and leaves no settings behind for the next run.
set -u

gui_limit_seconds=300

runner=(freecadcmd)
if [ "${1:-}" = --gui ]; then
  shift
  # The GUI binary never exits by itself, so a launcher that fails to start would hang the build.
  runner=(timeout "$gui_limit_seconds" freecad)
  export QT_QPA_PLATFORM=offscreen
fi
module=$1
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
out=${CANDYBAR_OUT:-$root/out}
state=$out/.freecad
mkdir -p "$state"
log=$state/$module.log
home=$(mktemp -d "$state/home.XXXXXX") || exit 1
trap 'rm -rf "$home"' EXIT
status=$home/status

CANDYBAR_ROOT=$root CANDYBAR_OUT=$out CANDYBAR_MODULE=$module CANDYBAR_STATUS=$status FREECAD_USER_HOME=$home \
  "${runner[@]}" "$root/candybar/launch.FCMacro" 3>&1 4>&2 >"$log" 2>&1 </dev/null
ended=$?

code=$(cat "$status" 2>/dev/null)
if [[ $code =~ ^[0-9]+$ ]]; then
  exit "$code"
fi
if [ "$ended" -eq 124 ]; then
  echo "FreeCAD did not finish $module within $gui_limit_seconds s and was stopped. Log: $log" >&2
else
  echo "FreeCAD ended without reporting a result for $module. Log: $log" >&2
fi
exit 1
