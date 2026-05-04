# Code Review Flow

Review actual code changes for completed plan tasks. Validates that implementation matches plan intent and meets quality standards. This flow is reached via Entry Point (`INTENT = code_review`) or Mode D in the R2+ menu.

## Step 1: Identify Completed Tasks

**1a. Read plan to find completed tasks**

Read `$PLAN_DIR/task_plan.md` and `$PLAN_DIR/progress.md`. Identify tasks with status `completed` (or equivalent markers: all `[x]` checkboxes checked, "Status: completed" in plan section, split file headers with `Status: completed`).

**1b. Present task selection**

If multiple tasks are completed, ask the user which to review (use AskUserQuestion):

```
Completed tasks available for code review:
  [6] BaseEntityReplica lifecycle cleanup
  [7] BaseEntityReplica field trim
  [8] SyncFrom thread-safety refactor

Review which task(s)? (number, comma-separated, or "all")
```

If only one completed task exists, or the user already specified one, skip the prompt. If no completed tasks exist, inform the user and suggest running a plan review instead.

## Step 2: Resolve Code Changes

For each selected task, resolve the actual code diff using these sources in priority order:

1. **User-specified**: commits, file paths, or CL numbers from the user's message → use directly
2. **progress.md**: look for "Files created/modified" entries under the task's session dates
3. **Split file headers**: if task was split, check `$PLAN_DIR/tasks/task-NN-plan.md` for `Commits:` in the header
4. **Git history**: `git log --oneline --all --grep="task [N]"` or date-range from progress.md entries
5. **P4 changelists**: if working in P4 context, `p4 changes -l -u $USER //...@start,@end`

Collect into a **change manifest**:

```
Task 6 — Code Changes:
  Commits: abc1234, def5678
  Files changed (5):
    M Assets/Scripts/Logic/LogicFighter.cs
    M Assets/Scripts/Logic/LogicFighterReplica.cs
    A Assets/Scripts/Logic/BehaviorLockManager.cs
    M Assets/Scripts/Network/SyncProcessor.cs
    D Assets/Scripts/Legacy/OldBehaviorLock.cs
```

Confirm the change scope with the user before proceeding. If no changes can be resolved, ask the user to provide commit hashes or file paths.

## Step 3: Leader Deep-Read (Code)

This parallels the plan review deep-read but targets code:

**3a. Read the plan section** for the task under review — understand what was supposed to be implemented.

**3b. Read the diffs**: `git diff <base>...<commit>` or `git show <commit>` for each relevant commit. For P4: `p4 diff2` or `p4 describe -du <CL>`.

**3c. Read full files** where diffs alone lack sufficient context (e.g., the diff touches a method but you need to understand the class structure).

**3d. Build your code review mental model** — before spawning agents, you must answer:
- What did the plan say to do? What did the code actually do? Any divergence?
- What are the riskiest changes? (concurrency, public API surface, data mutation)
- What existing code does this interact with? (callers, base classes, interfaces)
- Are there tests? Do they cover the changed behavior?

## Step 4: Generate Code Review Dimensions

Derive from the code changes, not from a fixed menu. Consider these seed categories and select the 3-5 most relevant:

- **Plan Fidelity**: Does the code implement what the plan specified? Anything missing or extra?
- **Safety**: Thread safety, null handling, error paths, resource disposal, edge cases
- **Performance**: Allocations in hot paths, O(n) changes, lock contention
- **Integration**: Does it break callers? API contract changes? Serialization compatibility?
- **Code Quality**: Duplication, naming, dead code, complexity, readability
- **Test Coverage**: Are new behaviors tested? Are edge cases covered?

Each dimension gets: name, 4-6 specific questions targeting the actual changed files, and concrete search targets (class names, method names from the diff).

## Step 5: Create Round Tracking Task

```
TaskCreate(subject="Code Review R[N]: Task [T] — [TaskName]", description="Code review round [N] for plan task [T]. Files: [count]. Commits: [hashes]. Dimensions: [list].")
```

## Step 6: Compose & Launch Agents

Each agent prompt has four blocks:

**Context Block** (same for all):
- Plan section for the task (what was supposed to happen)
- Change manifest (commits, files)
- Project architecture notes relevant to the changed area

**Code Block** (same for all):
- Full diffs for all changed files
- Key surrounding code (callers of changed APIs, base class definitions, interface contracts)

**Dimension Block** (unique per agent):
- Dimension name and relevance to these specific changes
- 4-6 targeted review questions
- Concrete search targets in the diff and surrounding code
- P0/P1/P2 severity definitions in this dimension's context

**Output Format Block**:
```
P0: code is incorrect / will crash / data corruption / security hole
P1: likely bug / missing edge case / API contract violation / thread-safety gap
P2: style / readability / minor improvement / documentation
Each finding: title, file:line evidence, code snippet, impact, suggested fix.
```

Launch all agents in **one message**, all `run_in_background: true`. Name format: `r[N]-code-[dim]`. Agents MUST follow the **[Code Review Agent Protocol]** below.

## Step 7: Synthesize Code Review Report

When all agents complete:

1. **Read all results** — don't concatenate
2. **Deduplicate**: Same file:line from multiple agents → merge, cite all evidence, take highest severity
3. **Validate**: Cross-check against your deep-read understanding. Reject false positives (e.g., "missing null check" where the caller guarantees non-null). Upgrade real issues that agents under-scored.
4. **Register each P0 and P1 as a Task**:

```
TaskCreate(
  subject="[R2-P0-1] BehaviorLockManager.Acquire() missing lock release on exception path",
  description="If Acquire() throws after incrementing _lockCount, the count is never decremented.\nFile: BehaviorLockManager.cs:47-62\nCommit: abc1234\nPlan task: 6",
  metadata={"severity": "P0", "round": 2, "review_type": "code", "plan_task": "6", "file_path": "BehaviorLockManager.cs", "line_range": "47-62", "commit_hash": "abc1234", "plan_section": "1.1", "doc_line_hint": "BehaviorLockManager.Acquire"}
)
```

**Code review Task metadata**:
- `severity`: P0 / P1
- `round`: the round number
- `review_type`: `"code"` (distinguishes from plan review Tasks where `review_type` is absent or `"plan"`)
- `plan_task`: which plan task number this code implements
- `file_path`: primary file where the issue was found
- `line_range`: line range in the file (at the reviewed commit)
- `commit_hash`: commit (or CL number for P4) where the issue was introduced
- `plan_section`: corresponding plan section (for cross-reference)
- `doc_line_hint`: content phrase for grep relocation

5. **Output report**:

```markdown
# R[N] Code Review Report — Task [T]: [TaskName]

## Change Summary
Commits: [list] | Files: [count] | Lines: +[added] / -[removed]

## P0 Findings
| # | Issue | File | Lines | Impact |
|---|-------|------|-------|--------|

## P1 Findings
| # | Issue | File | Lines | Impact |
|---|-------|------|-------|--------|

## P2 Observations
[Bulleted list — not tracked as Tasks]

## Summary
P0: [count] | P1: [count] | P2: [count]
```

---

## Code Review Agent Protocol

When an agent is tasked with reviewing code changes, it must NOT just read the diff and report surface issues. It must **understand the change in context**:

### For each file in the change set:

1. **Understand the intent**: Read the plan section. What was this change supposed to accomplish?
2. **Read the diff carefully**: Understand every added, removed, and modified line. Don't skim.
3. **Check the context**: Read surrounding code in the full file. Does the change fit the existing patterns? Does it break assumptions other code depends on?
4. **Trace call sites**: Search for callers of any modified public/internal API. Are they compatible with the change?
5. **Verify edge cases**: For each modified code path, consider: null inputs, empty collections, concurrent access, exception paths, boundary values.
6. **Check test coverage**: Search for test files that exercise the changed code. Are new behaviors tested? Are modified behaviors' tests updated?

### Finding quality bar:

```
GOOD: "BehaviorLockManager.cs:52 — _lockCount++ happens before the try block.
       If TryAcquireLock() throws, _lockCount is never decremented.
       Callers (LogicFighter.cs:2616, SyncProcessor.cs:340) will see stale count."

BAD:  "The locking code might have issues."
BAD:  "Consider adding more error handling." (vague, no evidence)
```

Every finding MUST include: file path, line number(s), code snippet showing the problem, and concrete impact. "Might be an issue" is not a finding.
