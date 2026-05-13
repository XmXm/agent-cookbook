---
name: planning-review
description: "Multi-agent iterative review of planning documents and implemented code. Spawns parallel Agent Review Teams with dynamically generated review dimensions. Supports plan review (audit task_plan.md) and code review (audit code changes for completed plan tasks). Stores review reports and P0/P1 tracking under the plan directory."
user-invocable: true
disable-model-invocation: true
---

# Planning Review — Multi-Agent Iterative Review

Organize a parallel Agent Review Team to audit planning documents or implemented code. Supports plan review (R1 and R2+ iteration) and code review of completed tasks. Every invocation auto-detects round number and review type, then starts the appropriate flow.

## Directory Resolution

Follow the shared Directory Resolution rules to determine `PLAN_DIR`: scan `.plans/` for subdirectories containing `task_plan.md`. Single match → use it. Multiple → ask user.

## Review State Files

All durable review state lives under `$PLAN_DIR/review/`.

```
$PLAN_DIR/review/
├── index.md                      # Cross-round state: open/resolved P0/P1, round history, review mode notes
├── R1.md                         # Round 1 plan review report
├── R2.md                         # Round 2 plan review report
└── R3-code-task-6.md             # Code review report for a selected plan task
```

`review/index.md` is the cross-round memory. Each `R*.md` file is an immutable round snapshot unless the same round is still being synthesized.

Use this table schema in `review/index.md`:

```markdown
# Planning Review Index

## Metadata
| Field | Value |
|-------|-------|
| Plan | `.plans/<name>` |
| Current Round | R<N> |
| Last Review Type | Plan Review / Code Review |
| Last Updated | YYYY-MM-DD |

## Open P0/P1 Findings
| ID | Severity | Type | Round | Status | Finding | Evidence | Required Fix | Relocation Hint |
|----|----------|------|-------|--------|---------|----------|--------------|-----------------|

## Resolved P0/P1 Findings
| ID | Severity | Type | Found | Resolved | Finding | Evidence | Resolution Evidence |
|----|----------|------|-------|----------|---------|----------|---------------------|

## Round History
| Round | File | Type | Mode | Open P0 | Open P1 | Resolved |
|-------|------|------|------|---------|---------|----------|
```

Finding IDs use `R<N>-<severity>-<number>`, for example `R1-P0-1`. Code review findings also carry the same ID style and set `Type = Code`.

## Core Principles

1. **Leader comprehension first**: You must deeply understand the plan before spawning any agent. You are the Review Lead, not a dispatcher.
2. **Dimensions from content**: Read the plan, identify its core risks, then create review dimensions targeting those risks. Every plan is different — do not use a fixed dimension menu.
3. **File-backed findings**: Use `$PLAN_DIR/review/index.md` to register each P0/P1 with doc location, code evidence, required fix, status, and relocation hint. This file is the cross-round memory.
4. **R1 = wide + deep; R2+ = narrow + deeper**: First round covers everything thoroughly. Subsequent rounds focus on what changed.
5. **Code-verified findings**: Every finding must be backed by codebase evidence. Verification agents must search code to cross-validate, not just read the plan text.

---

## Entry Point: Auto-Detect Round & Mode

Every time this skill is invoked, start here:

### 1. Detect user intent

Check the user's message for explicit code review signals:
- Phrases: "review code", "review implementation", "code review", "review the code for task", "check the implementation"
- If detected → set `INTENT = code_review`
- Otherwise → set `INTENT = plan_review`

### 2. Check existing review state

```
mkdir -p "$PLAN_DIR/review"
Read "$PLAN_DIR/review/index.md" if present.
List "$PLAN_DIR/review"/R*.md and find the highest round number.
```

### 3. Determine current round

- **No review state found** → This is **R1** (first round).
  - If `INTENT = plan_review` → Go to **[First Round Flow]**
  - If `INTENT = code_review` → Go to **[Code Review Flow]**
- **Review state exists** → This is **R(N+1)** where N = highest round number in `review/R*.md`. Go to **[Iteration Round Flow]** (which offers code review as Mode D).

---

## First Round Flow (R1)

### Step 1: Leader Deep-Read

This is the most important step. Do NOT skip or rush it.

**1a. Read all plan documents**

Read the full task/section under review in `$PLAN_DIR/task_plan.md`. Also read relevant sections of `$PLAN_DIR/findings.md` (prior research, data dependencies) and `$PLAN_DIR/progress.md` (what's done vs remaining).

**1b. Build your mental model**

Before composing any agent prompt, you must be able to answer:
- What is this plan trying to achieve? What's the core transformation?
- What are the 3-5 hardest problems this plan must solve?
- Where are the plan's assumptions? Which are validated vs unvalidated?
- What domain knowledge is required? (threading model, language constraints, API contracts, etc.)
- What does the plan explicitly say it will NOT do? (scope boundaries)

**1c. Determine review scale**

| Signal | Scale | Agent count |
|--------|-------|-------------|
| 1-2 phases, single concern, low risk | **Light** | 0 (review inline) |
| 3-5 phases, 2+ concerns | **Standard** | 2-3 agents |
| 5+ phases, cross-cutting concerns | **Heavy** | 3-4 agents |

For **Light** plans, go to **[Inline Review]**.

### Step 2: Generate Review Dimensions

Do NOT pick from a fixed menu. Derive from what you read:

1. Identify the plan's **top 3-5 risk areas** (what's most likely to go wrong)
2. For each risk, formulate a **review dimension**:
   - A descriptive name (e.g., "Cross-thread data consistency", "API call-site coverage completeness")
   - 4-6 specific verification questions for codebase search
   - Concrete search targets: class names, method names, patterns

### Step 3: Prepare Review Files

1. Create `$PLAN_DIR/review/` if it is missing.
2. Create or refresh `$PLAN_DIR/review/index.md` with metadata, open/resolved findings tables, and round history.
3. Reserve `$PLAN_DIR/review/R1.md` as the report path for this round.
4. Record the planned dimensions and agent count in the round report setup section.

### Step 4: Compose & Launch Agents

Each agent prompt has three blocks:

**Context Block** (same for all — include generously):
- Project architecture summary (from your deep-read)
- Full plan section under review (agents cannot see the conversation)
- Relevant findings.md sections
- Code conventions or constraints

**Dimension Block** (unique per agent):
- Dimension name and why it matters
- 4-6 specific verification questions
- Concrete search targets
- P0/P1/P2 severity definitions in this dimension's context

**Output Format Block**:
```
P0: blocks implementation / causes build failure / produces incorrect results
P1: improves quality / prevents likely bugs / resolves ambiguity
P2: nice to have / style / documentation
Each finding: title, evidence (file:line), impact, suggested fix.
```

Launch all agents in **one message**, all `run_in_background: true`.

Inform the user: agent count, dimension names, what each is looking for.

### Step 5: Synthesize R1 Report

When all agents complete:

1. **Read all results** carefully — don't concatenate
2. **Deduplicate**: Same issue from multiple agents → merge, cite all evidence, take highest severity
3. **Validate**: Use your deep-read understanding to sanity-check. Reject false positives. Upgrade missed P0s.
4. **Write `$PLAN_DIR/review/R1.md`** with P0/P1/P2 graded findings, review setup, evidence, impact, and required fixes.
5. **Update `$PLAN_DIR/review/index.md`**:
   - Add each P0/P1 to `Open P0/P1 Findings`
   - Include `ID`, `Severity`, `Type`, `Round`, `Status`, `Finding`, `Evidence`, `Required Fix`, and `Relocation Hint`
   - Use `doc_line_hint` as the relocation hint, for example `BehaviorLockSnapshot struct`
   - Add a `Round History` row pointing to `review/R1.md`
6. **Output a concise report** and include the report path.

---

## Iteration Round Flow (R2+)

### Step 1: Read State & Present Mode Menu

**1a. Load prior findings**

```
Read "$PLAN_DIR/review/index.md" and collect rows in "Open P0/P1 Findings".
If index.md is missing but R*.md files exist, rebuild the open list from the newest round report before continuing.
```

**1b. Present review mode menu**

Ask the user to choose via the available user-input mechanism:

```
This is review round R[N]. Detected [X] open P0(s) and [Y] open P1(s).

Select review mode for this round:
A. Verify Fixes — focus on checking whether prior P0/P1 items have been resolved
B. Find New Issues — run a fresh full review on the current plan
C. Verify Fixes + Find New Issues — do both in parallel
D. Code Review — review actual code changes for completed plan tasks
```

**1c. Auto-select fallback**

- If user selects A (Verify Fixes) and the open list is empty → auto-switch to B, inform the user: "All prior P0/P1 items are closed. Auto-switching to Find New Issues mode."
- If user selects D → Go to **[Code Review Flow]**.
- If user doesn't respond or defers → default to C if open P0/P1 exist, otherwise B.

### Step 2: Read the Delta

1. Read the updated `$PLAN_DIR/task_plan.md` — focus on what changed
2. Read the user's fix description (from their message or a change summary)
3. For each open P0/P1 row, use `Relocation Hint` to grep and locate the fix in the updated document. If the section moved, update `review/index.md` with the new location in the evidence or required-fix text.

### Step 3: Configure Agents by Mode

**Mode A: Verify Fixes**
- Agent count: 1-2 (focused)
- Each agent receives: prior open P0/P1 list + fix description + changed plan sections
- Dimensions: derived from P0/P1 categories (e.g., if all P0s are thread-safety related, spawn one thread-safety verification agent)
- **Agent must cross-validate against code** — see [Verification Agent Protocol] below

**Mode B: Find New Issues**
- Same as R1 flow: deep-read updated plan, generate fresh dimensions, spawn full agent team
- Agents are told: "This is round [N]. Prior rounds found [summary]. Focus on areas NOT previously reviewed, or areas significantly changed."

**Mode C: Verify Fixes + Find New Issues**
- Spawn verification agents (Mode A) + new-issue agents (Mode B) **in parallel**
- Typically 2 verification + 2 new-issue = 4 agents total
- Or 1 verification + 2 new-issue if open P0 count is small

### Step 4: Launch Agents

All in one message, all `run_in_background: true`. Name format: `r[N]-verify-[dim]` or `r[N]-new-[dim]`.

### Step 5: Synthesize Report

1. **Resolution tracking** (Mode A/C): For each prior open P0/P1 row:
   - `Resolved` → move the row to `Resolved P0/P1 Findings` and add resolution evidence
   - `Partial` → keep the row open, set `Status = Partial`, and append the current round note
   - `Unresolved` → keep the row open, set `Status = Open`, and append the current round evidence
   - `New Issue` → add a new open row with current round number

2. **New findings** (Mode B/C): Add new P0/P1 rows to `Open P0/P1 Findings` with current round number

3. **Write the round report** to `$PLAN_DIR/review/R[N].md` with this format:
   ```markdown
   # R[N] Review Report — [Mode Name]

   ## Prior P0/P1 Resolution Status (if Mode A or C)
   | Finding ID | Issue | Status | Evidence |
   |---------|-------|--------|----------|

   ## New P0 Findings (if Mode B or C)
   ...

   ## New P1 Findings (if Mode B or C)
   ...

   ## Summary
   Open P0: [count] | Open P1: [count] | Resolved this round: [count]
   ```

4. **Update `review/index.md`** with the new open/resolved counts and a `Round History` row.

---

## Verification Agent Protocol

When an agent is tasked with verifying a fix (Mode A or C), it must NOT just read the plan text and say "looks fixed". It must **cross-validate against the actual codebase**:

### For each P0/P1 under verification:

1. **Locate the fix in the plan**: Use `doc_line_hint` to find the relevant section in the updated plan
2. **Understand the claimed fix**: What does the plan say it will do differently?
3. **Search the codebase to validate**:
   - If the fix claims "X already exists" → grep for X, confirm it exists, check its implementation
   - If the fix claims "change type from struct to class" → search for the type, verify current definition
   - If the fix claims "field Y is already synced" → find the ReplicaSetter/SyncFrom call, confirm it covers Y
   - If the fix claims "method Z is thread-safe" → read method Z's implementation, verify thread-safety
4. **Check blast radius**: Does the fix touch code that has other callers? Search for references to modified APIs.
5. **Verify language/platform constraints**: If the fix involves volatile, Interlocked, or other concurrency primitives, confirm they are legal for the specified types in the target language version.

### Verification verdict per finding:

```
Resolved     — [code evidence confirming the fix is correct]
Partial      — [what's fixed + what's still missing, with code evidence]
Unresolved   — [why the fix doesn't work, with code evidence]
New Issue    — [the fix itself introduced a new problem]
```

The agent MUST provide file:line evidence for every verdict. "The plan says it's fixed" is not evidence.

---

## Code Review Flow

Follow the complete Code Review Flow in [`./references/code-review-flow.md`](./references/code-review-flow.md). That document covers: identifying completed tasks, resolving code changes, leader deep-read, dimension generation, agent composition, and the Code Review Agent Protocol.

---

## Inline Review (Light Plans)

For simple plans (1-2 phases, single concern):
- Skip agent team entirely
- Review inline in your response and write the same findings to `$PLAN_DIR/review/R[N].md`
- Still use P0/P1/P2 grading
- Register any P0/P1 findings in `$PLAN_DIR/review/index.md`
- For code review of Light plans: review code inline with the same P0/P1/P2 grading and use `Type = Code` in the index row.
- Follow the same Entry Point auto-detection — if prior review state exists, show the mode menu

---

## Optional Task Mirror

Some runtimes provide Task tools. After writing `review/index.md` and the round report, you may mirror open P0/P1 rows into TaskCreate/TaskUpdate for UI convenience. The review files remain authoritative.

Mirror each row with these fields:

```json
{
  "severity": "P0",
  "round": 1,
  "review_type": "plan",
  "plan_section": "1.1",
  "doc_line_hint": "BehaviorLockSnapshot struct",
  "review_file": "$PLAN_DIR/review/R1.md"
}
```

Use the mirror only after the file-backed state is updated.

## Anti-Patterns

1. **Dispatching without understanding**: Launching agents before you've deeply read the plan produces vague reviews. Leader deep-read is non-negotiable.
2. **Fixed dimension menus**: Derive dimensions from plan content. Two plans in the same repo get different dimensions.
3. **Broad re-review on R2+**: Mode A (Verify Fixes) should NOT re-scan the whole plan. Only the fixes and their blast radius.
4. **Line-number anchoring**: Use `doc_line_hint` (content phrase grep) to relocate findings. Line numbers break on edit.
5. **Severity inflation**: P0 = "will fail". Not "could be better".
6. **Skipping index updates**: `review/index.md` is the R2+ memory for R1 findings and resolution status.
7. **Missing code evidence**: "This might be a problem" is not a finding. "LogicFighter.cs:2616 Dictionary<int,int> not thread-safe" is.
8. **Plan-text-only verification**: Saying "the plan now says sealed class so P0-1 is fixed" without grepping the codebase is lazy verification. The Verification Agent Protocol exists to prevent this.
9. **Diff-only code review**: Reading only the diff without understanding the surrounding code produces shallow findings. Always read the full file context for non-trivial changes.
10. **Plan-code disconnect**: Reviewing code without reading the corresponding plan section. The plan defines what "correct" means — without it, you're just linting.
