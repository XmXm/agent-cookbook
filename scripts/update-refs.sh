#!/usr/bin/env bash
# Bootstrap and update the nested repos (not submodules, plain git clones
# ignored by the parent repo). Clone if missing, otherwise fast-forward pull.
set -euo pipefail

cd "$(dirname "$0")/.."

# path|url|branch
repos=(
  "mt-skills|git@lf.git.oa.mt:brianzuo/mt-skills.git|main"
  "refs/Waza|git@github.com:tw93/Waza.git|main"
  "refs/mattpocock-skills|git@github.com:mattpocock/skills.git|main"
  "refs/lark-skills|git@github.com:larksuite/cli.git|main"
  "refs/hai-stack|git@github.com:hylarucoder/hai-stack.git|main"
  "refs/ponytail|git@github.com:DietrichGebert/ponytail.git|main"
)

for entry in "${repos[@]}"; do
  IFS='|' read -r path url branch <<<"$entry"
  if [ ! -d "$path/.git" ]; then
    echo "==> clone $path"
    git clone --branch "$branch" "$url" "$path"
  else
    echo "==> pull $path"
    old=$(git -C "$path" rev-parse HEAD)
    git -C "$path" pull --ff-only origin "$branch"
    new=$(git -C "$path" rev-parse HEAD)
    if [ "$old" != "$new" ]; then
      git -C "$path" log --oneline "$old..$new" | sed 's/^/    /'
    fi
  fi
done
