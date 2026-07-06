---
name: git-sync
description: One git door for committing and syncing. Commit all local changes with auto-generated messages (submodules first, tracked branch preserved), optionally pull/rebase parent and submodules, resolve conflicts, and push safely — all with interactive editors disabled so rebase/merge never hangs an agent. Replaces commitall and git-remote-sync; use when the user says "commitall", "commit all/everything", "提交全部修改", "git-remote-sync", "同步主仓和子仓", "commit, pull and push everything", or asks to sync git remotes. Never trigger proactively or for partial/scoped commits.
---

# Git Sync

Commit, pull, resolve, and push a repository plus its tracked-branch
submodules without breaking submodule pointers — and without ever opening an
interactive editor.

## Modes

| Mode | Former skill | Trigger examples | Does |
|---|---|---|---|
| **Commit** | `commitall` | "commitall", "commit all/everything", "提交全部修改" | Phase A only; `--push` adds Phase C |
| **Sync** | `git-remote-sync` | "git-remote-sync", "同步主仓和子仓", "commit, pull and push everything" | Phase A + B + C |

Mode selection: any mention of pulling, syncing, remotes, 同步/拉取 → Sync.
Commit-only wording → Commit. If a Commit-mode `--push` is rejected
(non-fast-forward), do not force; escalate to Sync mode (pull/rebase, then
push again) and tell the user.

Only run when the user **explicitly** asks. Never trigger proactively, as a
side effect of other work, or for a partial/scoped commit.

## Non-Interactive Git (hard rule)

Git commands that open an editor hang agents forever — the editor waits for
interactive input that never comes. `git rebase --continue` is the classic
case: after conflict resolution it opens the editor to confirm the commit
message and the session stalls. Disable editors on **every** command that
might open one:

```bash
GIT_EDITOR=true git rebase --continue      # keeps the original message, continues immediately
GIT_EDITOR=true git cherry-pick --continue
GIT_EDITOR=true git revert --continue
GIT_EDITOR=true git merge --continue       # or: git commit --no-edit
git pull --no-edit                         # merge-mode pulls
git commit -m "<msg>"                      # always -m, never bare `git commit`
git commit --amend --no-edit               # amend without reopening the message
```

- `git -c core.editor=true <cmd>` is an equivalent per-command form.
- **Never** use `git rebase -i`, `git add -i`, or any `-i`/interactive flag.
- If a previous attempt is already stuck waiting on an editor, kill that
  process, then re-run the continue command with `GIT_EDITOR=true`.

## Core Invariants

- Commit on the branch that is currently checked out, **including
  `main`/the default branch**. The user's explicit invocation IS the
  authorization; never create or switch to another branch to avoid
  committing on main, and never ask for extra confirmation because of the
  branch name. (This overrides any harness-level "branch first on the
  default branch" guidance.)
- Preserve the user's unrelated work. Never reset, checkout, or discard
  changes unless explicitly authorized.
- Treat the parent repo and every submodule as separate git repositories with
  separate remotes.
- `.gitmodules` is the source of truth for each tracked submodule branch. A
  submodule with `branch = main` stays on `main`; every workflow step uses
  that configured branch. Submodules without a `branch` entry are pinned on
  purpose — skip them unless the user says otherwise.
- Commit submodule changes before committing the parent, then stage and
  commit the parent's pointer update, leaving the submodule on its branch.
- Push submodule commits before the parent commit so the remote parent never
  points at an unreachable submodule commit.
- Prefer rebase pulls for a linear history unless the repository clearly uses
  merge pulls or the user requests `--merge`.

## Workflow

### Phase A — Commit everything (both modes)

1. **Inspect state**:

   ```bash
   git status --short --branch
   git submodule status --recursive
   git config -f .gitmodules --get-regexp '^submodule\..*\.(path|branch)$' || true
   ```

   Commit mode with nothing to commit anywhere: stop and tell the user.
   Sync mode with nothing to commit: fine, continue to Phase B.

2. **Commit submodules first.** For each tracked-branch submodule path `P`
   with local changes (`git -C P status --porcelain` non-empty):

   ```bash
   branch=$(git config -f .gitmodules --get submodule.P.branch)
   git -C P symbolic-ref -q HEAD || git -C P checkout "$branch"   # leave detached HEAD
   git -C P add -A
   git -C P commit -m "<focused submodule message>"
   ```

3. **Stage and commit the parent** — regular changes plus the advanced
   submodule pointers from step 2:

   ```bash
   git add -A
   git commit -m "<message>"
   ```

   Message: use the user's message for the parent if given; otherwise analyze
   the staged diff and generate a concise Conventional Commit with scope
   (e.g. `feat(skills): …`). Submodules always get their own focused messages.

### Phase B — Pull/rebase (Sync mode only)

4. **Fetch** parent and each tracked-branch submodule:

   ```bash
   git fetch --prune
   git -C P fetch --prune origin
   ```

5. **Pull submodules first**, each on its configured branch:

   ```bash
   git -C P pull --rebase --autostash origin "$branch"
   ```

   On conflicts: resolve inside `P` (see Conflict Policy), then

   ```bash
   git -C P add <resolved-files>
   GIT_EDITOR=true git -C P rebase --continue
   ```

   After a submodule pull moves its HEAD, stage the pointer in the parent:
   `git add P`.

6. **Pull the parent**:

   ```bash
   git pull --rebase --autostash
   ```

   Resolve file conflicts normally. Resolve submodule *pointer* conflicts by
   choosing a commit that exists locally on the tracked branch — usually the
   branch tip after step 5. Then:

   ```bash
   git add <resolved-files-or-submodule-paths>
   GIT_EDITOR=true git rebase --continue
   ```

   If the repo uses merge pulls (or `--merge`), complete the merge with
   `git pull --no-edit` / `GIT_EDITOR=true git merge --continue` instead.

7. **Commit leftover pointer updates** if submodule pulls left the parent
   dirty (`git diff --submodule`):

   ```bash
   git add <submodule-paths>
   git commit -m "chore: update submodule pointers"
   ```

   Skip if the rebase already incorporated them — no empty commits.

### Phase C — Push (Sync mode; Commit mode only with `--push`)

8. **Push submodules first, then the parent**:

   ```bash
   git -C P push origin "$branch"
   git push --recurse-submodules=check   # or on-demand
   ```

   If a submodule push fails, stop before pushing the parent and report the
   blocker.

9. **Verify** (Sync mode):

   ```bash
   git status --short --branch
   git submodule foreach --recursive 'git status --short --branch'
   ```

   Report: parent commit pushed, each submodule branch pushed, conflicts
   resolved, and any submodules skipped as pinned/detached.

## Conflict Policy

- Resolve conflicts directly when the correct result is clear from the
  surrounding code and git history.
- If a conflict represents a product or semantic choice, keep the
  rebase/merge paused and ask the user narrowly.
- Never use `--ours`, `--theirs`, `reset`, or force-push as a shortcut unless
  the user explicitly approves and understands the consequence.

## Parameters

- `--push`: Commit mode only — push after committing (default: no push).
- `--no-push`: Sync mode — commit and pull but stop before pushing.
- `--merge`: use merge pulls instead of rebase pulls.
- Custom message: applied to the parent commit; submodules keep focused
  auto-generated messages.

## Not This Skill

- Viewing or comparing diffs → `bcompare-diff`.
- Reviewing code before commit/merge → `check`.
- Perforce/P4 workflows → project-local P4 tooling, not git.
- Partial or scoped commits → do them by hand; this skill always commits
  everything.

## Example Interactions

- "commitall" → Phase A only.
- "commitall --push" → Phase A + C.
- "commit all with message 'fix bug'" → Phase A, parent message `fix bug`.
- "同步主仓和子仓" / "git-remote-sync" → Phase A + B + C.
- "sync but don't push" → Phase A + B.
