#!/usr/bin/env bash
# Fetch the third-party reference CAD at pinned revisions.
#
#   cad/tools/fetch_vendor.sh [target-dir]      default target: cad/vendor
#
# These files are dimensional references. Git ignores cad/vendor because the licenses
# do not permit redistribution. Do not copy their geometry into tracked files.
set -euo pipefail

vendor="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/vendor}"
missing=0

repos=(
  "mgs-cad-files|https://github.com/multigamesystem/MGS-CAD-Files|c2cc26be009e7c2825ff7b8162e8863d88b8be08|none declared"
  "mgs-mvs-u4-bartop|https://github.com/multigamesystem/MGS004NSM-MVS-U4-Bartop-Arcade|111b091500b99a94ab7690a2081f26b4a0b11d9c|CC BY-NC 4.0"
  "onemorecap-bc250-shell|https://github.com/onemorecap/bc-250-shell-case|ea2e59bab5ea5f5bd4cfce69b72c4a192391daea|none declared"
)

# Printables gives no stable download link, so these are downloaded by hand from the page.
files=(
  "mandic-bc250-board/BC250_Completeish_V1.step|28c4ac1f2d2fc06fbc903aed8aa44565352439ad5fb0b088c14d40eeeb78882e|https://www.printables.com/model/1828755-asrock-bc250-complete-ish-cad-model|CC BY-NC-SA 4.0"
  "shinf1x-bc250-dim/bc250_radiator.step|31ddb25df676fdc3630f2b666d38ce0565eedafa5efb5213eaed02687d24bd30|https://www.printables.com/model/1677793-asrock-bc250-dimension-model|CC BY-NC 4.0"
  "mkuu-plus-case/BC250_Case_MKUU_Plus_FSP_Version.3mf|a840536ba1e19ef17f1ee4b91ecd1f39bf8a46fd121990a038c58f6953b2864d|https://www.printables.com/model/1835961-bc250-case-mkuu-fsp-apevia-metalfish-psu|CC BY-NC-SA 4.0"
)

mkdir -p "$vendor"

for entry in "${repos[@]}"; do
  IFS='|' read -r name url commit license <<<"$entry"
  dir="$vendor/$name"
  if [ "$(git -C "$dir" rev-parse HEAD 2>/dev/null || true)" = "$commit" ]; then
    echo "ok       $name ($license)"
    continue
  fi
  if [ ! -d "$dir/.git" ]; then
    git init -q "$dir"
    git -C "$dir" remote add origin "$url"
  fi
  git -C "$dir" fetch -q --depth 1 origin "$commit"
  git -C "$dir" checkout -q --detach FETCH_HEAD
  echo "fetched  $name at ${commit:0:12} ($license)"
done

for entry in "${files[@]}"; do
  IFS='|' read -r path sha page license <<<"$entry"
  file="$vendor/$path"
  if [ ! -f "$file" ]; then
    echo "missing  $path: download it from $page ($license)"
    missing=1
  elif [ "$(sha256sum "$file" | cut -d' ' -f1)" = "$sha" ]; then
    echo "ok       $path ($license)"
  else
    echo "changed  $path: the checksum is not the recorded one. Source: $page"
    missing=1
  fi
done

exit "$missing"
