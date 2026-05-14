# Code Review Flow

Review actual code changes for completed plan tasks. Validates that implementation matches plan intent and meets quality standards. This flow is reached via Entry Point (`INTENT = code_review`) or Mode D in the R2+ menu.

## Step 1: Identify Completed Tasks

**1a. Read plan to find completed tasks**

Read `$PLAN_DIR/task_plan.md` and `$PLAN_DIR/progress.md`. Identify tasks with status `completed` (or equivalent markers: all `[x]` checkboxes checked, "Status: completed" in plan section, split file headers with `Status: completed`).

**1b. Present task selection**

If multiple tasks are completed, ask the user which to review via the available user-input mechanism:

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

**3d. Extract project context** — the same Project Context block produced in plan review (`README`, `AGENTS.md`, manifests, CI workflows, build scripts). Compress into:
- Verification commands the project actually uses (test, lint, build)
- Generated or bundled outputs that must stay in sync with sources
- Release artifacts and version fields
- Domain-specific risk areas the project documents

This block becomes part of every Code Review agent's Context Block. If project docs name a verification command, prefer it over auto-detection in the sign-off `verification:` row.

**3e. Build your code review mental model** — before spawning agents, you must answer:
- What did the plan say to do? What did the code actually do? Any divergence?
- What are the riskiest changes? (concurrency, public API surface, data mutation)
- What existing code does this interact with? (callers, base classes, interfaces)
- Are there tests? Do they cover the changed behavior?

## Step 3.5: Plan ↔ Code Drift Check

Before generating dimensions, classify the diff against its plan task. Drift findings are **first-class** and reported separately from functional findings — they do not get folded into "code quality" P2s.

Label each task's diff:

- **on target** — diff fully implements the task description, nothing more, nothing less
- **drift** — diff includes work outside the task scope: pure refactors, renames, formatting, restructuring, new dependencies, new abstractions, deletion of unrelated code
- **incomplete** — task checklist contains items not addressed by the diff

Drift signals (any one is enough to label drift):
- A changed file has no connection to the task
- The diff includes pure refactoring when the task was a fix or feature
- A new dependency appears that the task did not mention
- Code unrelated to the task was deleted or commented out
- A new abstraction or helper was introduced that the task does not require

Record the label in the report's Change Summary section. `drift` and `incomplete` produce their own findings (typically P1, escalating to P0 if the unrelated change touches auth / payments / data mutation / public API).

## Step 4: Generate Code Review Dimensions

Code Review dimensions come from two sources: **mandatory dimensions** (always run) and **plan-specific dimensions** (derived from the diff).

**4a. Mandatory Hard Stop Sweep (always run for Mode D)**

Regardless of the diff content, every Code Review run includes one Hard Stop sweep agent that checks the full set below. This is non-negotiable; it does not consume one of the plan-specific dimension slots.

The sweep must check every category, even when the diff appears unrelated:

| Hard Stop category | What to look for |
|--------------------|------------------|
| **Destructive auto-execution** | Any task or codepath marked safe / auto-run that mutates user-visible state (history files, configs, preferences, installed software) without explicit confirmation |
| **Generated artifact drift** | Source files changed but generated / bundled outputs (compiled assets, generated bindings, snapshot files, lockfiles) not regenerated to match |
| **Version skew** | Version fields across manifests, package metadata, app configs, changelogs, tags, and lockfiles out of sync |
| **Unknown identifiers in diff** | Any function, type, variable, or import introduced in the diff that has no definition elsewhere in the codebase. Grep before approving — no results outside the diff = does not exist |
| **Injection at trust boundaries** | SQL / shell / path / template injection at user-controlled input points |
| **Secret / credential exposure** | Hardcoded credentials, secrets logged, secrets committed, secrets copied into public docs |
| **Dependency drift** | Unexpected additions or version bumps in `package.json` / `Cargo.toml` / `go.mod` / `requirements.txt` / `pyproject.toml` not obviously required by the diff |

Findings from the Hard Stop sweep flow into the same P0/P1 buckets and get an Action Class like any other finding. The sweep agent's findings are reported under a dedicated `## Hard Stop Findings` section in the code review report.

**4b. Plan-specific dimensions**

In addition to the Hard Stop sweep, derive 3-5 dimensions from the actual code changes. Consider these seed categories and select the most relevant:

- **Plan Fidelity**: Does the code implement what the plan specified? Anything missing or extra? (overlaps with Step 3.5 drift label — use this dimension to deepen, not duplicate)
- **Safety**: Thread safety, null handling, error paths, resource disposal, edge cases
- **Performance**: Allocations in hot paths, O(n) changes, lock contention
- **Integration**: Does it break callers? API contract changes? Serialization compatibility?
- **Code Quality**: Duplication, naming, dead code, complexity, readability
- **Test Coverage**: Are new behaviors tested? Are edge cases covered?

Each dimension gets: name, 4-6 specific questions targeting the actual changed files, and concrete search targets (class names, method names from the diff).

## Step 5: Prepare Code Review Files

1. Create `$PLAN_DIR/review/` if it is missing.
2. Read or create `$PLAN_DIR/review/index.md`.
3. Reserve `$PLAN_DIR/review/R[N]-code-task-[T].md` as the report path.
4. Record the selected task, change manifest, dimensions, commits, and changed file count in the report setup section.

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
4. **Write `$PLAN_DIR/review/R[N]-code-task-[T].md`** with P0/P1/P2 graded findings, change summary, evidence, impact, and suggested fixes.
5. **Update `$PLAN_DIR/review/index.md`**:
   - Add each P0/P1 to `Open P0/P1 Findings`
   - Set `Type = Code`
   - Include `ID`, `Severity`, `Action Class`, `Type`, `Round`, `Status`, `Finding`, `Evidence`, `Required Fix`, and `Relocation Hint`
   - Put file path, line range, commit hash or CL number, and plan task in the `Evidence` cell
   - Add a `Round History` row pointing to the code review report file
6. **Output report** ending with the **Sign-off Block** defined in `SKILL.md`:

```markdown
# R[N] Code Review Report — Task [T]: [TaskName]

## Change Summary
Commits: [list] | Files: [count] | Lines: +[added] / -[removed]
Drift label: on target / drift / incomplete  ([one-sentence justification])

## Hard Stop Findings
| # | Category | Issue | File | Lines | Impact | Action Class |
|---|----------|-------|------|-------|--------|--------------|

## P0 Findings
| # | Issue | File | Lines | Impact | Action Class |
|---|-------|------|-------|--------|--------------|

## P1 Findings
| # | Issue | File | Lines | Impact | Action Class |
|---|-------|------|-------|--------|--------------|

## P2 Observations
[Bulleted list]

## Summary
P0: [count] | P1: [count] | P2: [count] | Drift: [label]

## Sign-off
~~~
plan section:    Task [T]: [TaskName]
review depth:    light / standard / heavy
mode:            Mode D code
project context: [yes — list key sources, or none]
mandatory dims:  hard-stop-sweep=run, plan-fidelity=[covered/inferred]
specialists:     [security, architecture, ...] or none
hard stops:      N found, N requiring fix, N waived (with reason)
verification:    <command> -> pass / fail / none -- no command available
findings:        P0=N P1=N P2=N
open after:      P0=N P1=N
~~~
```

If `verification` is `none -- no command available`, the report MUST flag this as a structural gap in the project, not a free pass. Mode D cannot declare done without running something.

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
