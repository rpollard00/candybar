#!/usr/bin/env bash
# Run the tests of the code in many FreeCAD processes at once (cad/tests/parallel.py): first the builds that the
# tests read, then the test files and classes in parallel, then one summary with the verdict of cad/test.sh.
# Exits non-zero when a test fails. The run takes the lock of freecad-run.sh once, for the whole run.
#
# Usage: cad/test-parallel.sh [-j N] [--no-build] [--by-file] [name-fragment]
#   cad/container/run.sh cad/test-parallel.sh     the same, in the container of the reference FreeCAD
# The summary: cad/out/_parallel/summary.md; the log of each shard and step: cad/out/_parallel/logs/.
set -eu

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
lock=${CANDYBAR_LOCK:-${XDG_RUNTIME_DIR:-/tmp}/candybar-cad.lock}
if [ -z "${CANDYBAR_LOCK_HELD:-}" ] && command -v flock >/dev/null 2>&1; then
  export CANDYBAR_LOCK_HELD=1
  exec flock "$lock" "$0" "$@"
fi
python=$(command -v python3 || command -v python)
exec "$python" "$here/tests/parallel.py" "$@"
