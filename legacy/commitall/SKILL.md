---
name: commitall
description: Commit all local changes in a git repository with an auto-generated commit message, including submodules. When a submodule tracks a branch (e.g. main), commit inside the submodule first, then update the parent repo's pointer while keeping the submodule on that branch. Accepts --push to also push (disabled by default). Only use when the user explicitly triggers it or explicitly asks to commit all changes — e.g. "commit all", "commit everything", "commitall", "提交全部修改". Never trigger proactively or for partial/scoped commits.
---

# CommitAll

Quickly commit all local changes, including submodule changes.

## When To Use

Only run this skill when the user **explicitly** triggers it or asks to commit
everything. Do **not** trigger it proactively, as a side effect of other work,
or for a partial/scoped commit.

Matching requests:
- "commit all changes"
- "commit everything"
- "commitall"
- "commitall --push"
- "commit all and push"
- "提交全部修改"

## Workflow

### 1. Inspect state

- `git status` to confirm there are changes to commit.
- `git submodule status` to detect submodules with changes (a leading `+`
  means the checked-out commit differs from the recorded pointer; dirty content
  shows up under the submodule path).
- If there are no changes anywhere, stop and tell the user.

### 2. Commit submodules first (if any)

For each submodule path `P` listed in `.gitmodules`:

1. Read its tracking branch: `git config -f .gitmodules --get submodule.P.branch`.
   Only auto-commit submodules that declare a branch (e.g. `main`). Skip ones
   that pin a detached commit on purpose unless the user says otherwise.
2. Check for local changes: `git -C P status --porcelain`. If empty, skip `P`.
3. Keep the submodule on its branch. If `git -C P symbolic-ref -q HEAD` shows a
   detached HEAD, run `git -C P checkout <branch>` so the commit lands on the
   tracked branch instead of a detached HEAD.
4. Stage and commit inside the submodule:
   - `git -C P add -A`
   - `git -C P commit -m "<submodule message>"` (auto-generated, see step 4).

This satisfies the rule: **commit the submodule's own changes first, then
update the parent pointer, leaving the submodule on its tracked branch.**

### 3. Stage the parent repo

- `git add -A` in the parent. This stages regular file changes **and** the
  advanced submodule pointers committed in step 2.

### 4. Generate the commit message (if none provided)

- Analyze staged changes (files modified, added, deleted; submodule bumps).
- Write a concise conventional commit message.
- Use a separate, focused message for each submodule commit.

### 5. Commit the parent

- `git commit -m "<message>"`.

### 6. Push (only with `--push`)

- Push submodules before the parent so the recorded pointers exist on their
  remotes, then push the parent:
  - `git push --recurse-submodules=on-demand`
  - or push each submodule with `git -C P push origin <branch>`, then `git push`.

## Parameters

- `--push`: Push to remote after commit (default: false). With submodules,
  push the submodules too so pointers resolve on the remote.
- Custom message: the user can provide a specific commit message for the parent.

## Example Interactions

**User**: "commitall"
→ Commit any submodule changes on their tracked branch, bump pointers, stage all, generate message, commit parent (no push).

**User**: "commitall --push"
→ Same as above, then push submodules and parent.

**User**: "commit all with message 'fix bug'"
→ Commit submodule changes first, then commit parent with "fix bug" (no push).

**User**: "commitall --push 'release v1.0'"
→ Commit submodules, bump pointers, commit parent with "release v1.0", push everything.
