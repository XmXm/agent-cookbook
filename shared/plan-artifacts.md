# Plan Artifacts Contract

The persistence and tracking contract for plan directories. Consumers: `plan`
(creates the directory at approval, reads it back in Review mode) and `check`
Plan Execution (updates `progress.md` while executing). A plan file is a
carrier for an approved decision, never the goal.

## When a plan file earns its keep

- **Persist when** the work is non-trivial — multi-phase, 3+ steps, or spanning
  sessions — or when the user asks for a plan file.
- **Skip when** the ask is a single-step or lightweight change: leave the
  approved plan in the conversation. Forcing a `.plans/` file for a one-line
  fix is over-engineering.

## Target directory

Use the directory the user names. If none is given, default to
`.plans/<NNN>-<slug>/`, where `<NNN>` is zero-padded and one greater than the
highest existing `.plans/NNN-*` (start at `001`), and `<slug>` is a short
kebab-case summary of the task.

```bash
NEXT=$(ls -d .plans/[0-9]* 2>/dev/null | sed 's|.plans/||;s/-.*//' | sort -n | tail -1)
printf ".plans/%03d-%s/\n" "$(( ${NEXT:-0} + 1 ))" "<slug>"
```

## Files and owners

| File | Content | Written by |
|---|---|---|
| `task_plan.md` | Line after the title must be a one-line `状态：<current state>` status header (see below). Then the design header (Goal, Building / Not Building, Approach, Key Decisions, Premise Collapse, External Dependencies, Verification Plan, Rollback) followed by phases, each with a concrete verification command; plus an optional Execution Playbook section (see below) | `plan`, at approval; anyone who changes the plan's state updates the header |
| `findings.md` | Research evidence and state snapshots; only when the work is research-heavy | `plan`; executors may append corrections |
| `research/<topic>.md` | Optional. Full research reports (one file per investigation topic), preserving the complete file:line evidence, call trees, and comparison tables that `findings.md` had to condense away | `plan`, at approval, when research came from fan-out agents |
| `progress.md` | Phase status as a rolling summary; only when execution spans sessions or is long-running | `plan` seeds it when warranted; `/check` Plan Execution updates it as phases complete |

### The status header — the only aggregation mechanism

`task_plan.md` opens with exactly one status line directly after the title
(blank line between them):

```text
# 045 管家 Owner 动作卡与安全交付计划

状态：已完成并部署（集成提交 `fe8f298`，生产 HEAD 已包含）
```

Freeform text after `状态：`, one line, current-state-first. Typical states:
`已批准待实施` / `Phase N 进行中` / `已完成并部署` / `已收口（遗留降级为按需另启，见 progress.md）` /
`已搁置`. Whoever changes the plan's real state — approval, phase completion,
closeout, shelving — updates this line in the same change.

This line is the *only* aggregation mechanism: "which plans are active" is
answered by `head -3 .plans/*/task_plan.md` (or grep `^状态：`), never by a
separate index file. Do not create `.plans/_index.json` or any status cache —
per-directory status lines are the single source of truth, and caches have
historically gone stale and misled sessions.

### research/ — why it exists

`findings.md` has a hard size budget, which forces condensation — and condensation
loses exactly the detail an implementer needs mid-phase (the step-by-step queue
chain, the full call tree, the per-item comparison table). When a plan was built
from multiple research agents, their full reports exist only in the originating
session and are lost once it ends. Persist them to `research/` at approval time:
one file per topic, a transcription of the agent's report (keep all file:line
evidence; strip only conversational framing). `findings.md` stays the condensed
index and must point to the `research/` files it summarizes. Skip `research/`
when findings alone carries all the evidence without loss.

### Execution Playbook — when the plan outlives the session

A plan that will be executed in a fresh session, or by parallel worker agents,
needs more than decisions — it needs the *operating procedure* that the planning
session learned. Add an `## Execution Playbook` section to `task_plan.md` when
execution is expected to span sessions or fan out across agents. Include:

- Branch discipline (always state it explicitly): the main checkout never
  leaves the baseline branch (e.g. `dev`) — feature branches are checked out
  only inside worktrees, and merges back to the baseline run on the baseline
  branch itself (in the main checkout, or in a dedicated merge worktree when
  the main checkout may be shared with another concurrent session). Worktrees
  exist only for true parallelism: a single-track plan develops and commits
  directly on the current branch, with no new branch and no worktree.
- Parallel orchestration discipline: which phases can run concurrently, worktree
  / branch setup commands, known file-conflict hotspots, merge order.
- The verification gate as copy-pasteable commands with expected outputs — not
  prose descriptions of them.
- Per-worker hard constraints (files that must never be touched, add/commit
  discipline, style boundaries).
- A context entry-point list: which files a fresh session must read, and any
  memory-store keywords that recover prior decisions.

Skip it for plans the current session will finish itself.

The persisted plan carries the same hard rules as the conversation plan: no
`TBD` / `TODO`, every phase independently mergeable. Write in the session
language; default to Chinese when mixed.

## Anti-bloat discipline

- `progress.md` uses rolling summaries — completed phases fold into a one-line
  conclusion.
- `findings.md` stays under ~400 lines; shrink before appending. When shrinking
  would lose implementation-grade evidence, move the full report to `research/`
  and keep the pointer — don't fight the budget by deleting detail outright.
- `research/` files are exempt from the findings budget: they are read on
  demand during the phase that needs them, never auto-loaded on session
  recovery. Keep them as faithful transcriptions, not growing documents —
  executors append corrections to `findings.md`, not here.
- These limits prevent the plan directory from becoming a session-recovery
  bottleneck (historical precedent: a plan once reached 3 300+ lines / 60k
  tokens and crippled session resumption).

Status dashboards, index caches, hooks, and session catch-up are out of scope.
