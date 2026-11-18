#!/usr/bin/env bash
# Usage: cad/tools/cad-lock.sh <command> [arguments]
# Runs a direct freecadcmd or blender command under the lock that cad/candybar/freecad-run.sh uses, so that one
# heavy CAD process runs at a time on this machine. Inside a run that already has the lock it runs the command
# with no wait.
set -u
lock=${CANDYBAR_LOCK:-${XDG_RUNTIME_DIR:-/tmp}/candybar-cad.lock}
if [ -n "${CANDYBAR_LOCK_HELD:-}" ] || ! command -v flock >/dev/null 2>&1; then
  exec "$@"
fi
export CANDYBAR_LOCK_HELD=1
exec flock "$lock" "$@"
