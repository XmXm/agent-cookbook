#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f .gitmodules ]]; then
  echo "ERROR: .gitmodules not found" >&2
  exit 1
fi

submodules=()
while IFS= read -r path; do
  submodules+=("${path}")
done < <(git config -f .gitmodules --get-regexp '^submodule\.refs/.*\.path$' | awk '{print $2}')

if [[ ${#submodules[@]} -eq 0 ]]; then
  echo "No refs/ submodules found in .gitmodules"
  exit 0
fi

for path in "${submodules[@]}"; do
  branch="$(git config -f .gitmodules --get "submodule.${path}.branch" || true)"
  branch="${branch:-main}"

  echo "==> Updating ${path} to origin/${branch}"
  git submodule update --init -- "${path}"
  git -C "${path}" fetch origin "${branch}"
  git -C "${path}" checkout "${branch}"
  git -C "${path}" reset --hard "origin/${branch}"
done

echo
echo "Updated refs/ submodules. Review and commit pointer changes with:"
echo "  git status --short refs"
echo "  git add refs && git commit -m 'Update refs submodules'"
