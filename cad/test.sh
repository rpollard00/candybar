#!/usr/bin/env bash
# Run the tests of the code under headless FreeCAD. Exits non-zero when a test fails.
#
# Usage: cad/test.sh [--slow | --all] [name-fragment]
#   (no flag)      the quick group: logic and small shapes, no build of the shell (about 2 minutes)
#   --slow         the slow group: the tests marked with tests.support.slow, which need the shell, the skin or a
#                  study, and protect what no build checks. They read the builds in cad/out/shell-rev7 and the caches;
#                  run them on the server (cad/verify-remote.sh) or before a push.
#   --all          both groups
#   name-fragment  run only the tests whose name contains it, for example test_params
# Some tests run cad/build.sh with stand-ins, and the GUI binary of FreeCAD offscreen. No window opens.
set -eu

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
group=quick
case "${1:-}" in
  --slow) group=slow; shift ;;
  --all) group=all; shift ;;
  --*) echo "usage: $0 [--slow | --all] [name-fragment]" >&2; exit 2 ;;
esac
if [ $# -gt 1 ]; then
  echo "usage: $0 [--slow | --all] [name-fragment]" >&2
  exit 2
fi
CANDYBAR_GROUP=$group CANDYBAR_TESTS=${1:-} exec "$here/candybar/freecad-run.sh" tests.run
