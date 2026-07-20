---
name: check
description: >-
  Reviews code diffs, PRs, issue queues, release readiness, git ship follow-through,
  and project audits. Use when users ask in any language for code review, issue or PR triage,
  release gates, publishing follow-through, or project audits.
  Not for debugging root causes, prose review, or executing non-git VCS submits
  (P4/SVN changelists route to explicit-only project skills).
when_to_use: "review, 看看代码, 合并前, 看看issue, 看看PR, review my code, check changes, before merge, before release, release gate, git 提交前, git commit and push, publish follow-through, code review, code-review, audit, project audit, 项目体检, 项目评分, 给项目打分, 深入分析项目代码, 评估项目质量, 代码质量评分, scorecard, linus review, rate this codebase, score this project, 按计划实施, implement this plan"
dispatch_intent: "Code review, before merge, release gates, plan execution, project-wide audit"
---

<!-- Forked from Waza (MIT, © 2026 Tw93). Stripped GitHub-specific flows, added
     project knowledge hooks and diff-source routing. -->

# Check: Review Before You Ship

Read the diff, find the problems, fix what can be fixed safely, ask about the rest.
Done means verification ran in this session and passed.

## Outcome Contract

- Outcome: a review, release decision, or maintainer action grounded in the current diff, project context, and live evidence.
- Done when: findings, fixes, shipped state, or blockers are stated with the commands, artifacts, or remote state that prove them.
- Evidence: worktree status, diff, public project docs, manifests, CI, package contents, release or registry state, and current command output.
- Output: concise findings first, then verification and shipped-state summary when applicable.

## Knowledge Preflight

Before opening a review, run the preflight defined in `shared/knowledge-preflight.md`:
search the project KB (per `shared/project-routing.md`, if mounted and the
current work is within its declared Scope) for known anti-patterns and gotchas
related to the subsystem being reviewed; search nmem for prior review
decisions. If either source is unavailable or out of scope, state so and
proceed — preflight is non-blocking.

## Diff Source Routing

git diffs (local branch, PR, commit range) are reviewed in this skill. If a
project layer is mounted at `shared/project-routing.md`, check its check
signals table first: sources listed there (e.g. other VCS changelists) route
to their explicit-only project skills instead. No routing table → review here.

## Review Baseline

Apply the review baseline from `shared/common-core.md` (style, security,
testing), plus `shared/languages.md` for language-specific checks.

Project-specific review baselines (per-language coding skills, domain style
references) are declared in `shared/project-routing.md` when mounted — route
by name, do not copy their content here.

## Worktree Safety Preflight

Before any review, triage, ship, release, or PR operation, read the current worktree with:

```bash
git status --short --branch
```

Treat modified, staged, and untracked files as user work. Do not move, hide,
overwrite, clean, or discard them without explicit user approval in the current turn.

Do not run `git switch`, `git checkout`, `git reset --hard`, `git clean`,
`git stash -u`, `git stash --all`, or `gh pr checkout` as default review setup.
If a branch change is genuinely required, stop and ask.

## Mode Picker

| User intent | Mode |
|---|---|
| "implement this plan", "按计划实施", "可以干", "直接改" | [Plan Execution](#plan-execution-mode) |
| Diff or PR ready, "review", "看看代码", "合并前" | Default review (start at [Get the Diff](#get-the-diff)) |
| "commit", "push", "publish", "release" | [Ship / Release Follow-through](#ship--release-follow-through) |
| "audit", "项目体检", "项目评分", "scorecard" | [Project Audit](#project-audit-mode) |
| Document, PDF, prose review | Delegate to `/write` |

## Plan Execution Mode

Activate when the user's message starts with "Implement the following plan",
"按计划实施", "可以干", "直接改", or links to a `/plan` output.

1. State which plan is being executed (first heading or summary line).
2. Check for repo drift: `git status --short --branch` and skim changed files that contradict the plan. If drift makes the plan unsafe, name the conflict and stop.
3. Work through each plan item as a to-do. Mark each complete as you go.
4. If the plan lives in a `.plans/<NNN>-*/` directory, update `progress.md` as phases complete (if present; create it only when execution spans sessions or is long-running), per the `shared/plan-artifacts.md` contract — rolling summaries, completed phases fold into one line.
5. After all items are done, run the project's verification command. If the
   project documents none, run `bash <skill-base-dir>/scripts/run-tests.sh`
   from the project root — it auto-detects the test command.
6. Transition into Ship mode if the context indicates review-then-ship.

## Get the Diff

Get the full diff between the current branch and the base branch. If unclear, ask.

## Scope

Measure the diff and classify depth:

| Depth | Criteria | Reviewers |
|---|---|---|
| **Quick** | Under 100 lines, 1-5 files | Base review only |
| **Standard** | 100-500 lines, or 6-10 files | Base + conditional specialists |
| **Deep** | 500+ lines, 10+ files, or touches auth/payments/data mutation | Base + all specialists + adversarial pass |

State the depth before proceeding.

## Did We Build What Was Asked?

Before reading code, check scope drift: do the diff and the stated goal match?
Label: **on target** / **drift** / **incomplete**.

## Pattern-Fix Completeness

When the diff fixes one instance of a class-of-bug, extract the pattern
signature, `grep -rn` it across the repo, and confirm sibling instances were
handled. List unswept siblings.

## Hard Stops (fix before merging)

- **No unverified claims.** Do not write "I verified X" unless the shell output is in this turn's transcript.
- **Re-read before citing facts.** Before writing a line number or state into a report, re-read the source in this turn.
- **Destructive auto-execution**: any task marked "safe" that modifies user-visible state must require explicit confirmation.
- **Generated artifact drift**: if source changes require generated outputs, verify they were regenerated.
- **Unknown identifiers in diff**: any function or type introduced in the diff that does not exist in the codebase is a hard stop. Grep before approving.
- **Injection and validation**: SQL, command, path injection at system entry points. Credentials hardcoded, logged, or committed.
- **Dependency changes**: unexpected additions or version bumps. Flag any new dependency not required by the diff.
- **Safety sinks**: destructive file operations, shell construction, symlink traversal, approval boundary changes need explicit review.

## Finding Quality Gate

Before writing any finding into the report:

1. Can I cite the exact file:line?
2. Can I describe the specific input or state that triggers the bad outcome?
3. Have I read the upstream callers / downstream consumers?
4. Is the severity defensible?

If any answer is "no", drop or downgrade the finding. A clean review with zero
findings is a valid outcome — do not manufacture findings to justify invocation.

## Autofix Routing

| Class | Action |
|---|---|
| `safe_auto` — unambiguous, risk-free (typos, imports, style) | Apply immediately |
| `gated_auto` — likely correct but changes behavior | Batch into one user confirmation block |
| `manual` — requires judgment | Present in sign-off |

## Specialist Review (Standard and Deep only)

Load `references/persona-catalog.md` to determine which specialists activate.
Launch specialists in parallel when the environment supports it; merge findings
by severity.

## Ship / Release Follow-through

Activate when the user asks to commit, tag, release, publish, or push.

1. Extract release rules per `references/project-context.md` (context shape,
   Release Gate 2.0 matrix, Safety Sink review).
2. Verify generated outputs, version fields, and required artifacts are in sync.
3. Commit only intended files. Preserve unrelated dirty work.
4. Push, publish, tag, or release only with explicit user approval.

## Project Audit Mode

Activate for "audit", "项目体检", "scorecard", "linus review".

1. Run `python3 scripts/audit_signals.py --root <project>`.
2. Score on four axes (Architecture, Code Quality, Engineering, Perf & Risk), each 0-10.
3. Surface 3-7 concrete findings per axis with file:line, severity (CRIT/STRUCT/INCR), and one-line fix.
4. Output to terminal only — do not create files unless asked.

## Gotchas

| What happened | Rule |
|---|---|
| Posted a public reply to the wrong issue | Re-read the target and confirm identity before acting |
| PR comment sounded like a report | 1-2 sentences, natural, like a colleague |
| New file name duplicated a convention | Check the target directory's naming convention first |
| Push failed from auth mismatch | Check `git remote -v` and auth identity before pushing |

## Sign-off

```
files changed:    N (+X -Y)
scope:            on target / drift: [what]
review depth:     quick / standard / deep
hard stops:       N found, N fixed, N deferred
specialists:      [security, architecture] or none
new tests:        N
doc debt:         none / AGENTS.md needs X
verification:     [command] -> pass / fail
```
