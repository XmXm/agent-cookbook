---
name: check
description: >-
  Code review door: reviews diffs and PRs, executes an approved implementation plan
  ("按计划实施"), runs a pre-ship or release gate, and performs a project-wide audit or
  scorecard. User-invoked only: enter this skill when the user names it — "/check",
  "用 check", "走 check", "check 一下" — or explicitly asks for a code review ("review
  一下", "review this diff/PR", "帮我 review 代码"). Never trigger proactively from a
  diff you happen to see, a commit or push, a completed task, or a plan that looks ready
  to implement; handle those directly and mention that /check is available if a full
  review would help. Route root-cause diagnosis to hunt and prose review to write.
when_to_use: "/check, 用 check, 走 check, check 一下, 跑一下 check, review 一下, review this diff, review this PR, review my code, 帮我 review 代码, 用 check 按计划实施"
dispatch_intent: "Explicit /check invocation or an explicit code review request; never inferred from commit/push, plan execution, release, or audit wording"
---

<!-- Forked from Waza (MIT, © 2026 Tw93). Stripped GitHub-specific flows, added
     project knowledge hooks and diff-source routing. -->

# Check: Review Before You Ship

Read the diff, find the problems, fix what can be fixed safely, ask about the rest.
Done means verification ran in this session and passed.

## Activation Boundary

User-invoked only. Enter this skill when the user names it ("/check", "用 check",
"走 check", "check 一下") or explicitly asks for a code review ("review 一下", "review
this diff/PR", "帮我 review 代码") — then pick the mode from what they ask for: review,
approved-plan implementation, ship/release gate, or project-wide audit/scorecard. Do not
infer entry from other wording: "按计划实施", "推送前检查一下", "给项目打分" without
naming check or asking for a review are handled directly, with a one-line note that
/check is available if a full review would help. A bare "push" / "commit" / "推送一下"
is a plain Git operation. Read-only inspection requests use direct repository or
session inspection and return a concise status report.

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
| "检查后再推", "review then push", "publish", "release" | [Ship / Release Follow-through](#ship--release-follow-through) |
| Bare "push" / "commit" / "推送一下", no check intent | Not this skill — plain Git operation, do it directly |
| "audit", "项目体检", "项目评分", "scorecard" | [Project Audit](#project-audit-mode) |
| Document, PDF, prose review | Delegate to `/write` |

## Plan Execution Mode

Once inside check (user invoked it), use this mode when the message says "Implement
the following plan", "按计划实施", "可以干", "直接改", or links to a `/plan` output.
Those phrases alone, without `/check`, do not open this skill.

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

Activate only when the user asks for a checked ship: "检查后再推", tag, release,
or publish. A bare "push" or "commit" with no check intent never enters this mode.

**Short-circuit rule**: if the changes being shipped were already reviewed in this
session, or this turn adds no new code diff, skip all review — no scope
classification, no specialists, no re-verification. Run only the Worktree Safety
Preflight, then execute the steps below.

**User override**: if the user says "直接推" / "不要 review" / "skip the review",
push immediately after the Worktree Safety Preflight. Do not re-run tests or
re-inspect commits.

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
