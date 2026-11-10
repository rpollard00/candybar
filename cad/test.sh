#!/usr/bin/env bash
# Run the generator's tests under headless FreeCAD. Exits non-zero when a test fails.
# Some tests run cad/build.sh and FreeCAD's GUI binary offscreen; no window opens.
#
# Usage: cad/test.sh [name-fragment]
#   name-fragment  run only the tests whose name contains it, for example test_params
set -eu

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
if [ $# -gt 1 ]; then
  echo "usage: $0 [name-fragment]" >&2
  exit 2
fi
CANDYBAR_TESTS=${1:-} exec "$here/candybar/freecad-run.sh" tests.run
