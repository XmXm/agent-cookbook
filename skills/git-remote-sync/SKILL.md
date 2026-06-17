---
name: git-remote-sync
description: Commit all local changes, pull/rebase the parent repository and tracked-branch submodules, resolve conflicts, and push submodules plus parent remotes safely. Use when explicitly asked to sync git remotes, pull/push everything, git-remote-sync, or 同步主仓和子仓. Preserves submodule tracked branch correctness.
---

# Git Remote Sync

Commit, pull, resolve, and push a repository plus its tracked-branch submodules without breaking submodule pointers.

## When To Use

Use only when the user explicitly asks to synchronize a git repository with its remotes, especially requests like:

- `git-remote-sync`
- "commit, pull, and push everything"
- "sync main repo and submodules"
- "同步主仓和子仓"
- "主仓和子仓都 pull/push"

Do not trigger proactively after unrelated edits. This skill performs networked git operations and can require conflict resolution.

## Core Invariants

- Preserve the user's unrelated work. Never reset, checkout, or discard changes unless explicitly authorized.
- Treat the parent repo and every submodule as separate git repositories with separate remotes.
- For submodules that declare a tracked branch in `.gitmodules`, keep the working tree on that branch before committing, pulling, or pushing.
- Commit submodule changes before committing the parent repo, then stage and commit the parent submodule pointer update.
- Push submodule commits before the parent commit so the parent never records an unreachable submodule pointer on the remote.
- Prefer rebase pulls for a linear sync unless the repository clearly uses merge pulls or the user requests merge behavior.

## Workflow

### 1. Inspect repository topology and state

Run from the parent repository:

```bash
git status --short --branch
git submodule status --recursive
git config -f .gitmodules --get-regexp '^submodule\..*\.path$' || true
git config -f .gitmodules --get-regexp '^submodule\..*\.branch$' || true
```

For each submodule path `P` found in `.gitmodules`, inspect:

```bash
git -C P status --short --branch
git -C P remote -v
git -C P branch --show-current
```

If a submodule lacks a `.gitmodules` `branch` entry, do not move it to a branch automatically. Only sync pinned/detached submodules when the user explicitly requests it.

### 2. Commit all local changes first

Use the `commitall` workflow as the source of truth:

1. For every tracked-branch submodule with local changes, check out its configured branch if needed:
   ```bash
   branch=$(git config -f .gitmodules --get submodule.P.branch)
   git -C P symbolic-ref -q HEAD || git -C P checkout "$branch"
   ```
2. Commit inside the submodule first:
   ```bash
   git -C P add -A
   git -C P commit -m "<focused submodule message>"
   ```
3. Stage and commit the parent repo, including advanced submodule pointers:
   ```bash
   git add -A
   git commit -m "<focused parent message>"
   ```

If there are no local changes in a repository, skip its commit. If the user supplied a commit message, use it for the parent commit and generate focused messages for submodule commits.

### 3. Fetch remotes

Fetch the parent and each tracked-branch submodule before pulling:

```bash
git fetch --prune
git -C P fetch --prune origin
```

If a repository has no upstream, set or ask only when the correct remote/branch is ambiguous. Common default:

```bash
git push -u origin <branch>
```

### 4. Pull submodules first, preserving tracked branches

For each tracked-branch submodule `P`:

1. Ensure the submodule is on its configured branch:
   ```bash
   branch=$(git config -f .gitmodules --get submodule.P.branch)
   current=$(git -C P branch --show-current)
   test "$current" = "$branch" || git -C P checkout "$branch"
   ```
2. Pull remote changes:
   ```bash
   git -C P pull --rebase --autostash origin "$branch"
   ```
3. If conflicts occur, resolve them inside `P`, then continue:
   ```bash
   git -C P status
   # edit conflicted files
   git -C P add <resolved-files>
   git -C P rebase --continue
   ```
4. After a successful submodule pull, return to the parent and stage the pointer update:
   ```bash
   git add P
   ```

If a submodule was updated by pull, the parent repo must record that new submodule commit.

### 5. Pull the parent repo

Pull the parent after submodules have been committed and updated:

```bash
git pull --rebase --autostash
```

If conflicts occur:

1. Inspect `git status` and conflicted files.
2. Resolve normal file conflicts by editing the files, staging them, and continuing the rebase.
3. Resolve submodule pointer conflicts by choosing a submodule commit that exists locally and on the intended tracked branch. Usually this is the latest resolved submodule branch tip after step 4.
4. Continue:
   ```bash
   git add <resolved-files-or-submodule-paths>
   git rebase --continue
   ```

If the repository is configured for merge pulls, use the local pattern instead of rebase and complete the merge commit after resolving conflicts.

### 6. Commit any parent pointer changes after pulls

After submodule pulls, check whether the parent has staged or unstaged submodule pointer updates:

```bash
git status --short
git diff --submodule
```

If only submodule pointers changed because submodules were pulled, commit the parent pointer update:

```bash
git add <submodule-paths>
git commit -m "chore: update submodule pointers"
```

If the parent rebase already incorporated the pointer update in an existing commit, do not create an extra empty commit.

### 7. Push submodules before parent

Push each tracked-branch submodule first:

```bash
git -C P push origin "$branch"
```

Then push the parent:

```bash
git push
```

As an additional safety check, use one of these before or during the parent push:

```bash
git push --recurse-submodules=check
# or, when appropriate:
git push --recurse-submodules=on-demand
```

If a submodule push fails, stop before pushing the parent and report the blocker. Do not leave the remote parent pointing at a submodule commit that was not pushed.

### 8. Final verification

Verify both parent and submodules are clean and synced:

```bash
git status --short --branch
git submodule status --recursive
git submodule foreach --recursive 'git status --short --branch'
```

For tracked-branch submodules, confirm each branch remains checked out:

```bash
git -C P branch --show-current
```

Report:

- parent commit pushed
- each submodule commit/branch pushed
- conflicts resolved, if any
- any repositories that were skipped because they were pinned/detached or lacked a configured branch

## Conflict Policy

- Resolve conflicts directly when the correct result is clear from surrounding code and git history.
- If a conflict represents a product or semantic choice, ask the user narrowly and keep the rebase/merge paused.
- Never use `--ours`, `--theirs`, `reset`, or force-push as a shortcut unless the user explicitly approves and understands the consequence.

## Parameters

- `--merge`: use merge pulls instead of rebase pulls.
- `--no-push`: commit and pull but stop before pushing.
- Custom message: use for the parent commit; submodules still receive focused messages unless the user gives explicit submodule messages.

## Example Interaction

**User**: `git-remote-sync`

→ Commit tracked-branch submodule changes, commit parent pointer updates, fetch and pull submodules, fetch and pull parent, resolve conflicts if safe, commit any new parent pointer updates, push submodule branches, then push the parent.
