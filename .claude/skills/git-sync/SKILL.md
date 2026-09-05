---
name: git-sync
description: >-
  The one git door for "commit and sync everything" in a repo with nested
  clones: commit user-owned nested-repo work (mt-skills) and parent work,
  pull remotes with rebase, refresh third-party ref clones via the repo's
  update-refs script, and push — nested repos and parent are independent, so
  order is loose, but interactive editors are always disabled so rebase/merge
  never hangs an agent. Use when the user says "git-sync", "同步主仓和子仓",
  "提交并同步", "commitall", "commit all/everything", "提交全部修改",
  "更新子仓", "拉取远端并推送", "commit, pull and push everything", or asks
  to sync git remotes/nested repos. Trigger only on explicit request — never
  proactively, never as a side effect of other work, never for
  partial/scoped commits.
---

# Git Sync

One linear pipeline that leaves the parent repo and its nested clones
committed, up to date, and pushed:

1. **Commit** — user-owned nested-repo work (mt-skills), then parent work.
2. **Pull** — parent and user-owned nested repos, rebase by default.
3. **Refresh third-party clones** — run the repo's update-refs script.
4. **Push** — user-owned nested repos and the parent.

Run the pipeline only when the user explicitly asks. Never trigger
proactively or for a partial/scoped commit — this flow commits *everything*.

## Repo model

The parent repo gitignores its nested clones; each nested repo has its own
remote and history, and the parent tracks nothing about them. Roles come from
the repo's own docs (AGENTS.md / README). In agent-cookbook:

| Role | Path | Rule |
|---|---|---|
| Parent | repo root | Commits only its own tracked files; knows nothing of nested repos |
| User-owned nested repo | `mt-skills` | Separate remote (company git). Commit, pull, push inside it |
| Third-party clone | `refs/*` | Read-only upstream code. Never commit inside; only moved by `scripts/update-refs.sh` |

In a repo where ownership is unclear and a third-party-looking clone has
dirty content, stop and ask instead of committing someone else's code.

Steps degrade gracefully: no user-owned nested repo → skip its commits and
pushes; no update script → skip step 3; nothing to commit anywhere → still
pull, refresh, and push whatever is unpublished.

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
- Prefer rebase pulls for linear history unless the repo clearly uses merge
  pulls or the user asks for `--merge`.
- No empty commits: skip any commit step whose tree is already clean.
- Company-git content (mt-skills) and personal-GitHub content (parent) stay
  in their own repos; never move files across that boundary as part of a sync.

## Pipeline

### 0 — Inspect

```bash
git status --short --branch
git -C mt-skills status --short --branch
```

Map each nested repo to its role before touching anything.

### 1 — Commit local work

For each **user-owned** nested repo `P` with dirty content:

```bash
git -C P add -A
git -C P commit -m "<focused message>"
```

Then the parent:

```bash
git add -A
git commit -m "<message>"
```

Use the user's message for the parent if given; otherwise read the staged
diff and write a concise Conventional Commit with scope (repo convention,
e.g. `feat(skills): …`). Nested repos always get their own focused messages.

### 2 — Pull

Parent and user-owned nested repos are independent; pull each:

```bash
git fetch --prune && git pull --rebase --autostash
git -C P fetch --prune origin && git -C P pull --rebase --autostash origin main
```

File conflicts follow the Conflict policy below. Continue with
`GIT_EDITOR=true git rebase --continue` after staging resolutions.

### 3 — Refresh third-party clones

From the repo root:

```bash
bash ./scripts/update-refs.sh    # clone if missing, else fast-forward pull
```

Skip with a note if the repo has no such script. The script prints
`--oneline` deltas for every clone that moved — capture them for the final
report.

### 4 — Push

```bash
git -C P push origin main
git push
```

If a push is rejected as non-fast-forward (a race with the remote), repeat
step 2 for that repo and push once more.

### Report

End with: what was committed (per repo, with messages), what was pulled,
which third-party clones moved and their `--oneline` deltas (worth skimming
for ideas to distill — see AGENTS.md maintenance cadence), and what was
pushed where. Name anything skipped and why.

## Conflict policy

- Resolve directly when the correct result is clear from surrounding code and
  history.
- If a conflict encodes a product/semantic choice, keep the rebase paused,
  present both sides, and ask the user narrowly.
- Never `--ours`/`--theirs`, `reset`, or force-push as a shortcut unless the
  user explicitly approves.

## Partial runs

The steps are separable on request: "先别 push" / "don't push yet" → stop
after step 3 and say what remains; "只提交" / "just commit" → step 1 only;
"只更新子仓" → step 3 (plus push nothing). Default with no qualifier: the
full pipeline.

## Not this skill

- Viewing/comparing diffs → `bcompare-diff`.
- Reviewing code before commit/merge → `check`.
- Perforce/P4 workflows → project-local P4 tooling.
- Partial or scoped commits ("just commit file X") → do them by hand.
