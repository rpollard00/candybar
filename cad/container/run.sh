#!/usr/bin/env bash
# Run a command in the container of the reference FreeCAD (cad/container/Dockerfile), with this checkout mounted at
# the same path, as the calling user. The command sees the same paths as the host, so the paths in logs and reports
# are those of the checkout.
#
# Usage: cad/container/run.sh <command> [arguments]
#   cad/container/run.sh cad/build.sh
#   cad/container/run.sh cad/candybar/freecad-run.sh candybar.shell.fit
#
#   CANDYBAR_OCCT    the build of OpenCascade: v3 (default), v4, znver4 or arch (see the Dockerfile)
#   CANDYBAR_IMAGE   the image (default: candybar-freecad:1.1.4-3-<OCCT>-<hash of the Dockerfile>; built when it
#                    is not there, in about 4 minutes; 4.7 GB)
#   CANDYBAR_VENDOR  a folder for cad/vendor when that is a link out of the checkout (default: where the link points)
#   CANDYBAR_MOUNTS  more folders to mount at their own path, separated by ':'
#   CANDYBAR_DOCKER_ARGS  more arguments for docker run, for example "--memory 200g"
set -eu

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cad=$(dirname "$here")
repo=$(dirname "$cad")
occt=${CANDYBAR_OCCT:-v3}
image=${CANDYBAR_IMAGE:-candybar-freecad:1.1.4-3-$occt-$(sha256sum "$here/Dockerfile" | cut -c1-8)}

if ! docker image inspect "$image" >/dev/null 2>&1; then
  echo "Building the image $image (about 4 minutes)." >&2
  docker build -q --build-arg "OCCT=$occt" -t "$image" "$here" >&2
fi

mounts=(-v "$repo:$repo")
# A git worktree keeps its git data in the main repository: mount it, so that git works in the container.
common=$(git -C "$repo" rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)
if [ -n "$common" ] && [ "${common#"$repo"/}" = "$common" ]; then
  mounts+=(-v "$common:$common")
fi
# cad/vendor and cad/.venv-tools are often links out of the checkout: mount what they point to, read-only.
for link in "$cad/vendor" "$cad/.venv-tools"; do
  if [ -L "$link" ]; then
    target=$(readlink -f "$link")
    [ -d "$target" ] && mounts+=(-v "$target:$target:ro")
  fi
done
IFS=: read -r -a extra <<<"${CANDYBAR_MOUNTS:-}"
for folder in "${extra[@]}"; do
  [ -n "$folder" ] && mounts+=(-v "$folder:$folder")
done

envs=()
for name in $(compgen -e | grep '^CANDYBAR_' || true); do
  envs+=(-e "$name")
done

tty=()
[ -t 0 ] && [ -t 1 ] && tty=(-it)
# The container has its own process table: the memory guard of freecad-run.sh (pkill -x freecadcmd) sees only the
# processes of this container. HOME is a folder inside the container, so nothing is written to the caller's home.
# shellcheck disable=SC2086
exec docker run --rm "${tty[@]}" --init --user "$(id -u):$(id -g)" -e HOME=/tmp -e QT_QPA_PLATFORM=offscreen \
  "${envs[@]}" \
  --shm-size 2g --tmpfs /tmp:exec,size=8g "${mounts[@]}" -w "$PWD" ${CANDYBAR_DOCKER_ARGS:-} "$image" "$@"
