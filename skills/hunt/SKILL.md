---
name: hunt
description: >-
  Finds root cause before applying fixes for errors, crashes, regressions, failing tests,
  broken behavior, and screenshot-reported defects. Use when users report in any language
  errors, crashes, broken behavior, regressions, failing tests, screenshot evidence, or
  something that used to work and now fails. Not for code review or new features.
when_to_use: "排查, 查查, 报错, 崩溃, 不工作, 不对, 跑不通, 以前是好的, 回归, 截图回归, 判断错误原因, 判断为什么报错, 反复修不好, debug, regression, used to work, broke after update, why broken, not working, what's wrong, fix error, stack trace"
dispatch_intent: "Error, crash, regression, screenshot-reported defect, test failure, runtime boundary, why broken"
---

<!-- Forked from Waza (MIT, © 2026 Tw93). Stripped update-check and durable-context
     references, added project knowledge hooks and routing table. -->

# Hunt: Diagnose Before You Fix

A patch applied to a symptom creates a new bug somewhere else.

## Outcome Contract

- Outcome: the root cause is identified before any fix is applied.
- Done when: one sentence explains the cause, every observed symptom fits it, and the fix or handoff is verified against a reproducible check.
- Evidence: source trace, repro command or UI path, logs or state, targeted test/build output, and runtime evidence for UI or native defects.
- Output: root cause, fix or handoff, verification result, and any unswept sibling risks.

**Do not touch code until you can state the root cause in one sentence:**
> "I believe the root cause is [X] because [evidence]."

Name a specific file, function, line, or condition. "A state management issue"
is not testable. Be that specific or you do not have a hypothesis yet.

## Knowledge Preflight

Before forming hypotheses, run the preflight defined in
`shared/knowledge-preflight.md`: search nmem for prior debugging decisions;
search the project KB (per `shared/project-routing.md`, if mounted) for
symptoms, similar cases, and bug history. If either source is unavailable,
state so and proceed — preflight is non-blocking.

## Project Routing

If a project layer is mounted at `shared/project-routing.md`, check its hunt
route-instead table: when the problem matches a more specific project skill,
route there instead of staying in hunt. No routing table → stay in hunt.

## Hard Rules

- **Same symptom after a fix is a hard stop.** Re-read the execution path from scratch.
- **After three failed hypotheses, stop.** Use the Handoff format below to surface what was checked, ruled out, and unknown.
- **Verify before claiming.** Never state versions, function names, or file locations from memory. Run the check first.
- **System/tooling symptoms need a lower-layer baseline.** Measure the raw lower layer before blaming the visible app.
- **Fix the cause, not the symptom.** If the fix touches more than 5 files, pause and confirm scope.

## Diagnosis Signals

Good progress: a log line matches the hypothesis, you can predict the next error
before running it, you understand the propagation path from root cause to
symptom. At each signal, find one more independent piece of evidence.

Hypothesis quality gate: list all observable symptoms. The hypothesis must
explain every symptom; if it only covers some, it is a symptom-level guess.

## Bisect Mode

Activate when: "以前是好的", "used to work", "broke after update".

0. Protect the worktree: `git status --short --branch`. If dirty, create a temporary detached worktree for bisect.
1. Find candidate good tag or ask for last known-good commit.
1b. If only one or a few releases back, `git diff <good>..HEAD -- <suspect path>` first — regression is often visible directly.
2. Define a non-interactive pass/fail test command.
3. `git bisect start && git bisect bad HEAD && git bisect good <tag>`
4. At each step run the test, mark good/bad.
5. When bisect names the culprit, read only that diff.
6. `git bisect reset` when done.

## Scope Blast Mode

Activate after fixing a root-cause pattern. Extract the pattern signature,
`grep -rn` across the repo, list every match, and for each answer: same bug /
leave (explain why safe) / unsure (ask). Do not claim "fixed" until blast report
is in Outcome.

## Runtime Evidence Ladder

1. Source trace: exact function, file, line, condition.
2. Deterministic repro: smallest command or scenario.
3. Logs/state/cache: runtime state proving the path was reached.
4. Build/test: narrow test exercising the fix.
5. Real runtime check: for UI/native/visual bugs, verify the visible result.

## Targeted Logging

Use logs as a scalpel. Before adding a log, write the question it answers.
Load `references/logging-techniques.md` for the full playbook.

## Fix-After Prompt

After fixing a root cause worth preserving, consider writing up the finding:
personal learnings via nmem (`nmem m add`), domain knowledge via the writeback
route in `shared/project-routing.md` (if mounted). This is a prompt, not
a requirement.

## Gotchas

| What happened | Rule |
|---|---|
| Patched the wrong component | Trace the execution path backward before touching any file |
| MCP not loading, switched tools instead of diagnosing | Check server status, API key, config before switching |
| Blamed the app before measuring the lower layer | Measure lower layer first, retire ruled-out hypotheses |
| Race condition diagnosed as stale state | Inspect event timestamps and ordering before state |
| Added logs everywhere, still could not explain | Rewrite each log as a yes/no question, delete non-discriminating ones |
| Build passed but UI still wrong | Move up the Runtime Evidence Ladder |

## Outcome

### Success Format

```
Root cause:        [what was wrong, file:line]
Fix:               [what changed, file:line]
Confirmed:         [evidence or test that proves the fix]
Tests:             [pass/fail count, regression test location]
Regression guard:  [test file:line] or [none, reason]
```

Status: **resolved**, **resolved with caveats**, or **blocked**.

### Handoff Format (after 3 failed hypotheses)

```
Symptom:           [one sentence]
Hypotheses Tested:
1. [H1] → [test] → [ruled out because...]
2. [H2] → [test] → [ruled out because...]
3. [H3] → [test] → [ruled out because...]
Evidence Collected: [logs, traces, env info]
Ruled Out:         [eliminated causes]
Unknowns:          [what is still unclear]
Suggested Next:    [directions, tools, context needed]
```

Status: **blocked**
