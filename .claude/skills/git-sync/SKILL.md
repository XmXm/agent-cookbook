---
name: git-sync
description: >-
  The one git door for "commit and sync everything" in a repo with submodules:
  commit user-owned submodule work (mt-skills) plus parent work and the
  submodule pointer, pull remotes with rebase, refresh third-party ref
  submodules via the repo's update-submodules script, commit the resulting
  pointer bumps, and push — submodules always before the parent, interactive
  editors always disabled so rebase/merge never hangs an agent. Use when the
  user says "git-sync", "同步主仓和子仓", "提交并同步", "commitall",
  "commit all/everything", "提交全部修改", "更新子模块", "拉取远端并推送",
  "commit, pull and push everything", or asks to sync git remotes/submodules.
  Trigger only on explicit request — never proactively, never as a side effect
  of other work, never for partial/scoped commits.
---

# Git Sync

One linear pipeline that leaves the parent repo, its user-owned submodules,
and its third-party ref submodules committed, up to date, and pushed:

1. **Commit** — user-owned submodule work first, then parent work plus the
   advanced submodule pointer, in one parent commit.
2. **Pull** — tracked submodules and the parent, rebase by default.
3. **Refresh third-party submodules** — run the repo's update script.
4. **Commit pointer bumps** left by steps 2–3.
5. **Push** — submodules first, then the parent.

Run the pipeline only when the user explicitly asks. Never trigger
proactively or for a partial/scoped commit — this flow commits *everything*.

## Repo model

Roles come from `.gitmodules` (tracked branch per submodule) plus the repo's
own docs (AGENTS.md / README). In agent-cookbook:

| Role | Path | Rule |
|---|---|---|
| Parent | repo root | Commits its own changes and every pointer update; pushed last |
| User-owned submodule | `mt-skills` | Separate remote (company git). Commit inside it, push it before the parent |
| Third-party submodule | `refs/*` | Read-only upstream code. Never commit inside; only moved by the update script |

`.gitmodules` is the source of truth for each submodule's branch. A submodule
without a `branch` entry is pinned on purpose — leave it alone. In a repo
where ownership is unclear and a third-party-looking submodule has dirty
*content* (not just a moved pointer), stop and ask instead of committing
someone else's code.

Steps degrade gracefully: no user-owned submodule → skip its commits/pushes;
no update script → skip step 3; nothing to commit anywhere → still pull,
refresh, and push whatever is unpublished.

## Non-interactive git (hard rule)

Git commands that open an editor hang agents forever — the editor waits for
input that never comes. `git rebase --continue` is the classic case. Disable
editors on **every** command that might open one:

```bash
GIT_EDITOR=true git rebase --continue      # keeps the original message
GIT_EDITOR=true git merge --continue       # or: git commit --no-edit
git pull --no-edit                         # merge-mode pulls
git commit -m "<msg>"                      # always -m, never bare `git commit`
git commit --amend --no-edit
```

Never use `git rebase -i`, `git add -i`, or any interactive flag. If a
previous attempt is already stuck on an editor, kill that process, then re-run
the continue command with `GIT_EDITOR=true`.

## Core invariants

- Preserve the user's unrelated work. Never reset, checkout over, or discard
  changes unless explicitly authorized.
- Commit and push a submodule **before** the parent commit that references it,
  so the remote parent never points at an unreachable submodule commit.
- Prefer rebase pulls for linear history unless the repo clearly uses merge
  pulls or the user asks for `--merge`.
- No empty commits: skip any commit step whose tree is already clean.

## Pipeline

### 0 — Inspect

```bash
git status --short --branch
git submodule status --recursive
git config -f .gitmodules --get-regexp '^submodule\..*\.(path|branch)$' || true
```

Map each submodule to its role before touching anything.

### 1 — Commit local work

For each **user-owned** submodule `P` with dirty content:

```bash
branch=$(git config -f .gitmodules --get submodule.P.branch)
git -C P symbolic-ref -q HEAD || git -C P checkout "$branch"   # leave detached HEAD
git -C P add -A
git -C P commit -m "<focused submodule message>"
```

Then the parent — regular changes plus the pointer just advanced:

```bash
git add -A
git commit -m "<message>"
```

Use the user's message for the parent if given; otherwise read the staged
diff and write a concise Conventional Commit with scope (repo convention,
e.g. `feat(skills): …`). Submodules always get their own focused messages.

### 2 — Pull

**Parent first, then submodules.** Two git traps force this exact shape:

- `git pull --rebase` refuses outright (`cannot rebase with locally recorded
  submodule modifications`) when the commits being rebased touch gitlinks and
  submodule recursion is on — and step 1's parent commit touches gitlinks.
  Always pass `--no-recurse-submodules`; submodules get their own pulls next.
- `--autostash` cannot stash submodule pointer dirt, so pull the parent while
  its tree is still clean from step 1. If pointer dirt already exists, commit
  it as a pointer bump first.

```bash
git fetch --prune && git pull --rebase --autostash --no-recurse-submodules
git -C P fetch --prune origin && git -C P pull --rebase --autostash origin "$branch"
```

Resolve parent submodule-*pointer* conflicts by choosing a commit that exists
locally on the tracked branch. File conflicts follow the Conflict policy
below. Continue with `GIT_EDITOR=true git rebase --continue` after staging
resolutions. Pointer dirt left by the submodule pulls is committed in
step 4, not here.

### 3 — Refresh third-party submodules

From the repo root:

```bash
bash ./scripts/update-submodules.sh    # wraps: git submodule update --remote --merge
```

Skip with a note if the repo has no such script. For every submodule whose
HEAD moved, capture the delta for the final report:

```bash
git -C <path> log --oneline <old>..<new>
```

### 4 — Commit pointer bumps

If steps 2–3 left the parent dirty (`git status --short` shows submodule
paths):

```bash
git add <submodule-paths>
git commit -m "chore(refs): bump submodule pointers"
```

### 5 — Push

User-owned submodules first, then the parent:

```bash
git -C P push origin "$branch"
git push --recurse-submodules=check
```

If a submodule push fails, stop before pushing the parent and report the
blocker. If the parent push is rejected as non-fast-forward (a race with the
remote), repeat step 2 for the parent and push once more.

### Report

End with: what was committed (per repo, with messages), what was pulled, which
third-party submodules moved and their `--oneline` deltas (worth skimming for
ideas to distill — see AGENTS.md maintenance cadence), and what was pushed
where. Name anything skipped and why.

## Conflict policy

- Resolve directly when the correct result is clear from surrounding code and
  history.
- If a conflict encodes a product/semantic choice, keep the rebase paused,
  present both sides, and ask the user narrowly.
- Never `--ours`/`--theirs`, `reset`, or force-push as a shortcut unless the
  user explicitly approves.

## Partial runs

The steps are separable on request: "先别 push" / "don't push yet" → stop
after step 4 and say what remains; "只提交" / "just commit" → step 1 only;
"只更新子模块" → steps 3–5. Default with no qualifier: the full pipeline.

## Not this skill

- Viewing/comparing diffs → `bcompare-diff`.
- Reviewing code before commit/merge → `check`.
- Perforce/P4 workflows → project-local P4 tooling.
- Partial or scoped commits ("just commit file X") → do them by hand.
