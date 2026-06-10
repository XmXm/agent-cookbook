---
name: planning-in
description: "Create planning files (task_plan.md, findings.md, progress.md) in .plans/NNN-description/. Supports multiple concurrent plans. Usage: /planning-in [description]. If description is provided, use it as the slug; if omitted, derive a short kebab-case slug from the user's task. Plan directory is auto-numbered (NNN-prefix, incrementing from existing plans). For existing plans, just @ the task_plan.md file directly. Use when the user says 'plan', 'plan in', 'planning in', 'start planning', or wants file-based planning."
user-invocable: true
disable-model-invocation: true
allowed-tools: "Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|Bash|Read|Glob|Grep"
      hooks:
        - type: command
          command: "for d in .plans/*/; do [ -f \"$d/task_plan.md\" ] && printf '[%s] %s\\n' \"$(basename \"$d\")\" \"$(grep -m1 '^## Current Phase' \"$d/task_plan.md\" -A1 2>/dev/null | tail -1)\"; done || true"
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "for d in .plans/*/; do [ -f \"$d/task_plan.md\" ] && echo '[planning-in] File updated. Check if any active plan phase needs status update.' && break; done || true"
  Stop:
    - hooks:
        - type: command
          command: "sh ~/.claude/skills/planning-in/scripts/check-complete.sh"
---

# Planning In

Create planning files in `.plans/<name>/`. Supports multiple concurrent plans.

Work like Manus: Use persistent markdown files as your "working memory on disk."

## FIRST: Check for Previous Session

**Before starting work**, check for unsynced context from a previous session:

```bash
python3 ~/.claude/skills/planning-in/scripts/session-catchup.py "$(pwd)"
```

If catchup report shows unsynced context:
1. Run `git diff --stat` to see actual code changes
2. Read current planning files
3. Update planning files based on catchup + git diff
4. Then proceed with task

## Invocation

```
/planning-in [description]
```

- **With description** → use it as the slug: `.plans/NNN-description/`
- **No description** → derive a short kebab-case slug from the user's current task

Plan directories are **auto-numbered** with a `NNN-` prefix. The number is determined by scanning `.plans/` and incrementing the highest existing number.

Examples:
- `/planning-in refactor` → `.plans/006-refactor/` (if 005 is the latest)
- `/planning-in fix login bug` → `.plans/006-fix-login-bug/`
- `/planning-in` → `.plans/006-add-user-auth/` (derived from task context)

For existing plans, the user will `@` reference the `task_plan.md` file directly — no skill invocation needed.

## Multi-Plan Architecture

Each plan is independent — own directory under `.plans/`, own files. Active plans are discovered by scanning `.plans/` for subdirectories containing `task_plan.md`.

```
.plans/
├── _index.json                     # global metadata cache (auto-maintained)
├── 001-monorepo-abtest-platform/   # completed
├── 003-feature-expansion/          # completed
├── 006-refactor/                   # active
│   ├── task_plan.md
│   ├── findings.md
│   └── progress.md
└── 007-fix-login-bug/              # active
    ├── task_plan.md
    ├── findings.md
    └── progress.md
```

Completed plans stay in `.plans/` alongside active ones — distinguished by phase status, not by directory location.

### Archiving a plan

To retire a plan without deleting it (abandoned, superseded, or rolled into another plan), move it under `.plans/archive/`. `discover_plan_dirs()` excludes the `archive/` (and `active/`) staging dirs, so archived plans drop out of the dashboard and index while their files stay on disk:

```bash
mkdir -p .plans/archive
git mv .plans/<NNN-name> .plans/archive/<NNN-name>   # or plain mv if not tracked
python3 ~/.claude/skills/planning-in/scripts/plans-index.py rebuild
```

Archiving differs from `planning-in-remove`: archive **keeps** the files (recoverable by moving back out of `archive/`), remove **deletes** them. Prefer archive for any plan you might want to revisit.

### Global Index (`.plans/_index.json`)

A cache of plan metadata: title, current phase, completion progress, error
count, file sizes, timestamps, aggregate status (`pending` / `in_progress` /
`complete` / `blocked`). Maintained by `scripts/plans-index.py`:

- `init-session.sh` calls `plans-index.py sync <plan-dir>` after creating a plan.
- `planning-in-status` reads it via `plans-index.py dashboard` (re-syncs from disk first).
- `planning-in-remove` calls `plans-index.py remove <plan-dir>` after deletion.

The index is **always derivable from disk** — if it goes missing or stale,
run `python3 scripts/plans-index.py rebuild`. Skills should treat it as a
fast-path and fall back to scanning `.plans/` if it's unreadable.

### Status vocabulary (canonical tokens)

Each phase's `**Status:**` field MUST use exactly one of these tokens — they are
states, not past-tense verbs:

| token | meaning | dashboard icon |
|-------|---------|----------------|
| `pending` | not started | ⏸️ |
| `in_progress` | actively being worked | 🔄 |
| `complete` | finished | ✅ |
| `blocked` / `failed` | stuck or failed | ❌ |

**Write `complete`, never `completed`.** `plans-index.py` matches the token with
exact equality (`status == "complete"`), so `completed` is silently NOT counted
as done — the phase reverts to `pending` in the dashboard even though it looks
finished. (Worse, `check-complete.sh` uses a substring grep that *does* accept
`completed`, so the two tools disagree.) Mirror the same set in the dir-tree
comments and in `progress.md`. When in doubt, copy the token from
`STATUS_ICONS` in `scripts/plans-index.py` — that map is the source of truth.

## Pre-flight (Before Creating Files)

Run these checks before initializing any plan files. Skipping pre-flight produces plans that look organized but rest on shaky assumptions.

1. **Path confirmation**: `pwd` and `git rev-parse --show-toplevel`. Confirm the working directory is the project the user actually means. Do not assume `~/project` and `~/www/project` are the same.
2. **Prior decisions**: Skim existing ADRs, design docs, and `.plans/` entries on the same topic. Avoid re-deciding what was already decided, or unknowingly contradicting a prior plan.
3. **Real config references**: If the plan involves a default value, env var, or config field, open the actual project config file (e.g. `package.json`, `tauri.conf.json`, `pake.json`, `.env.example`) and record the key name, file path, source of truth, and verification status. For secrets, record variable name, owner, and reachability status only; secret values stay in env vars or secret managers.
4. **Official solutions first**: Before recommending a custom implementation, check whether the framework, language stdlib, or ecosystem already provides the capability. If an official solution exists, it is the default unless you can articulate why it is insufficient.
5. **Blocking ambiguity**: If the user's requirements contain a conflict (two contradicting sources, two valid interpretations with different cost), stop and ask which takes precedence. Never silently pick one and write it into `task_plan.md`.

## Workflow

### 1. Resolve plan name

Determine the plan directory name with auto-numbering:

```bash
# Find next number from existing .plans/ directories
NEXT_NUM=$(ls -d .plans/[0-9]* 2>/dev/null | sed 's|.plans/||' | sed 's/-.*//' | sort -n | tail -1)
NEXT_NUM=$((${NEXT_NUM:-0} + 1))
NUM=$(printf "%03d" $NEXT_NUM)

# Derive slug from argument or task context
SLUG="<kebab-case-description>"  # from argument or derived from user's task
PLAN_NAME="${NUM}-${SLUG}"
PLAN_DIR=".plans/$PLAN_NAME"
mkdir -p "$PLAN_DIR"
```

### 2. Check for existing files

```bash
ls "$PLAN_DIR"/{task_plan,findings,progress}.md 2>/dev/null
```

If files exist: show status, ask resume or start fresh.

### 3. Initialize (Two-Phase)

**3a. Design Phase — fill the design header before writing phases**

Before phase tasks exist, populate the design header in `task_plan.md` with concrete content:

- `Goal` — one sentence end state
- `Building / Not Building` — explicit scope and out-of-scope list
- `Approach` — chosen direction with rationale; mention the rejected alternative only if the tradeoff was close
- `Key Decisions` — 3-5 decisions with reasoning
- `Premise Collapse` — most fragile assumption + what happens if it fails + mitigation
- `External Dependencies` — every API key name, env var name, MCP server, third-party CLI, credential owner, and reachability check; secret values stay out of plan files
- `Verification Plan` — per-phase command and expected outcome
- `Rollback` — how to undo each irreversible step (write `N/A` only when truly local-only)

If the user has already provided this content in the prior conversation (e.g. from a design discussion), transcribe it verbatim. Do not re-litigate decisions.

**Forbidden in the design header**: TBD, TODO, "implement later", "similar to step N", "details to be determined". A plan with placeholders is a promise to plan later.

**3b. Phase Skeleton — derive phases from Approach**

Split Approach into Phases by natural work unit, not by a fixed template. A bug fix might need 2 phases; a refactor might need 6. Each phase must include a concrete `Verification` command. If you cannot name the verification command, the phase is sliced too coarsely — split it.

Run the init script to scaffold files:
```bash
sh ~/.claude/skills/planning-in/scripts/init-session.sh "$PLAN_NAME"
```

The script generates the new template (design header + empty phase skeleton). Fill the design header before writing phase tasks.

### 4. Confirm

```
Plan: refactor
Directory: .plans/refactor/
Files: task_plan.md | findings.md | progress.md
Active plans: 2
```

## The Core Pattern

```
Context Window = RAM (volatile, limited)
Filesystem = Disk (persistent, unlimited)

→ Anything important gets written to disk.
```

## File Purposes

| File | Purpose | When to Update |
|------|---------|----------------|
| `task_plan.md` | Phases, progress, decisions | After each phase |
| `findings.md` | Research, discoveries | After ANY discovery |
| `progress.md` | Session log, test results | Throughout session |

## Templates

### task_plan.md

The template is split into a **design header** (must be filled before phases) and a **phase body** (derived from Approach). No section may contain TBD / TODO / "implement later" placeholders.

```markdown
# Task Plan: [Plan Name]

## Goal
[One sentence end state]

## Building / Not Building
**Building:** [what this plan delivers]
**Not Building (out of scope):** [explicit non-goals; protects against scope drift]

## Approach
[Chosen direction with rationale. Mention the rejected alternative only if the tradeoff was close (>40% chance the user would prefer it).]

## Key Decisions
| Decision | Rationale |
|----------|-----------|

## Premise Collapse
- **Most fragile assumption:** [the load-bearing assumption most likely to be wrong]
- **If it fails:** [what breaks]
- **Mitigation:** [how the design survives or how we detect early]

## External Dependencies
| Dependency | Why needed | Source / owner | Reachability check | Status |
|------------|------------|----------------|--------------------|--------|
| (API key name / env var name / MCP / 3rd-party CLI / credential owner) | | | | pending / ready / blocked |

## Verification Plan
| Phase | Command | Expected outcome |
|-------|---------|------------------|

## Rollback
[For each irreversible step: how to undo. Write `N/A — local-only` only when there is no external state change.]

---

## Current Phase
Phase 1

<!-- TERMINOLOGY NOTE:
     "Phase 1/2/3/4" = implementation stages (here).
     "P0/P1/P2" = review severity (planning-review skill only).
     Never abbreviate phases as P1/P2 — that collides with review severity. -->

## Phases

### Phase 1: [Concrete name derived from Approach]
- [ ] [Specific action]
- [ ] [Specific action]
- **Verification:** [exact command, must match Verification Plan row]
- **Status:** in_progress
<!-- Status token MUST be one of: pending | in_progress | complete | blocked | failed.
     Write "complete", NOT "completed" — the index parser matches it exactly. -->

<!-- Add additional phases as the work naturally splits.
     Do NOT pad to 5 phases. A bug fix may need 2; a refactor may need 6.
     Every phase MUST have a concrete Verification command. -->

## Decisions Made
| Decision | Rationale |
|----------|-----------|

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
```

### findings.md

```markdown
# Findings & Decisions

## Requirements
-

## Research Findings
-

## Technical Decisions
| Decision | Rationale |
|----------|-----------|

## Issues Encountered
| Issue | Resolution |
|-------|------------|

## Resources
-
```

### progress.md

```markdown
# Progress Log

## Session: [DATE]

### Phase 1: [Title]
- **Status:** in_progress
- **Started:** [DATE]
- Actions taken:
  -
- Files created/modified:
  -

## Test Results
| Test | Expected | Actual | Status |
|------|----------|--------|--------|

## Error Log
| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|
```

## Critical Rules

### 1. Create Plan First
Never start a complex task without `task_plan.md`. Non-negotiable.

### 2. The 2-Action Rule
> "After every 2 view/browser/search operations, IMMEDIATELY save key findings to text files."

This prevents visual/multimodal information from being lost.

### 3. Read Before Decide
Before major decisions, read the plan file. This keeps goals in your attention window.

### 4. Update After Act
After completing any phase:
- Mark phase status: `in_progress` → `complete`
- Log any errors encountered
- Note files created/modified

### 5. Log ALL Errors
Every error goes in the plan file. This builds knowledge and prevents repetition.

```markdown
## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| FileNotFoundError | 1 | Created default config |
| API timeout | 2 | Added retry logic |
```

### 6. Never Repeat Failures
```
if action_failed:
    next_action != same_action
```
Track what you tried. Mutate the approach.

### 7. Design Before Phases
No `Approach` / `Not Building` / `Premise Collapse` → no phase tasks. Phases are the execution path of Approach, not placeholders to fill in later. Filling phases first produces busy-work that points in the wrong direction.

### 8. No Placeholders in Approved Plan
TBD, TODO, "implement later", "similar to step N", "details to be determined" are forbidden in `task_plan.md` once the design header is approved. A plan with placeholders is a promise to plan later — and that later usually doesn't happen.

### 9. External Dependencies Upfront
Every API key name, env var name, MCP server, third-party CLI, OAuth flow, and credential owner must be listed in `External Dependencies` and verified reachable **before Phase 1 starts**. Secret values stay in the environment or secret manager; the plan stores names, ownership, paths, and redacted status.

### 10. Document Language Follows Session Language
Planning documents (task_plan.md, findings.md, progress.md) must be written in the same language the user is currently using in the conversation. If the user speaks Chinese, write the plan in Chinese; if English, write in English. Default to Chinese (中文) when the session language is ambiguous or mixed. Technical identifiers (file paths, code, command names) remain in their original form regardless of document language.

## The 3-Strike Error Protocol

```
ATTEMPT 1: Diagnose & Fix
  → Read error carefully
  → Identify root cause
  → Apply targeted fix

ATTEMPT 2: Alternative Approach
  → Same error? Try different method
  → Different tool? Different library?
  → NEVER repeat exact same failing action

ATTEMPT 3: Broader Rethink
  → Question assumptions
  → Search for solutions
  → Consider updating the plan

AFTER 3 FAILURES: Escalate to User
  → Explain what you tried
  → Share the specific error
  → Ask for guidance
```

## Read vs Write Decision Matrix

| Situation | Action | Reason |
|-----------|--------|--------|
| Just wrote a file | DON'T read | Content still in context |
| Viewed image/PDF | Write findings NOW | Multimodal → text before lost |
| Browser returned data | Write to file | Screenshots don't persist |
| Starting new phase | Read plan/findings | Re-orient if context stale |
| Error occurred | Read relevant file | Need current state to fix |
| Resuming after gap | Read all planning files | Recover state |

## The 7-Question Reboot Test

If you can answer these, your context management and design memory are solid:

| Question | Answer Source |
|----------|---------------|
| Where am I? | Current phase in task_plan.md |
| Where am I going? | Remaining phases |
| What's the goal? | Goal statement in plan |
| What have I learned? | findings.md |
| What have I done? | progress.md |
| What did I assume that could be wrong? | Premise Collapse in task_plan.md |
| Which steps need rollback if they fail? | Rollback section in task_plan.md |

## When to Use This Pattern

**Use for:**
- Multi-step tasks (3+ steps)
- Research tasks
- Building/creating projects
- Tasks spanning many tool calls
- Anything requiring organization

**Skip for:**
- Simple questions
- Single-file edits
- Quick lookups

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Use TodoWrite for persistence | Create task_plan.md file |
| State goals once and forget | Re-read plan before decisions |
| Hide errors and retry silently | Log errors to plan file |
| Stuff everything in context | Store large content in files |
| Start executing immediately | Create plan file FIRST |
| Repeat failed actions | Track attempts, mutate approach |
| Create files in skill directory | Create files in the plan directory |
| Pad to a generic Phase 1–5 template | Split phases by natural work unit derived from Approach |
| Write phase tasks with no Verification | Every phase needs a concrete verification command; if you can't name one, the phase is too coarse |
| Quote default values / config from memory | Open the actual project config file and record the live source path, key name, and safe value metadata |
| Skip Premise Collapse and jump to tasks | State the most fragile assumption explicitly; let the design survive its failure |
| Ask the user for an API key mid-Phase 3 | List every credential in External Dependencies before Phase 1 starts |
| Leave TBD / TODO in the design header | A plan with placeholders is a promise to plan later — fill it now or stop |
| Abbreviate "Phase 1" as "P1" | Always write "Phase 1" in full — "P1" means review severity (planning-review) |

## Scripts

Helper scripts for automation:

- `scripts/init-session.sh` — Initialize planning files in a directory (also syncs `_index.json`)
- `scripts/check-complete.sh` — Verify all phases complete across all plans
- `scripts/session-catchup.py` — Recover context from previous session
- `scripts/plans-index.py` — Maintain `.plans/_index.json` (rebuild / sync / remove / show / dashboard)

Update plan metadata after editing `task_plan.md`:

```bash
python3 ~/.agents/skills/planning-in/scripts/plans-index.py sync .plans/<plan-dir>
```

Or rebuild the entire index from disk (safe to run anytime):

```bash
python3 ~/.agents/skills/planning-in/scripts/plans-index.py rebuild
```

## Advanced Topics

- **Manus Principles:** See [reference.md](reference.md)
- **Real Examples:** See [examples.md](examples.md)

## Integration with Other Planning Skills

| Skill | Integration |
|-------|------------|
| `planning-in:status` | Show all active plans from `.plans/` |
| `planning-in:remove` | Delete a plan directory from `.plans/` |
| `planning-organize` | Pass the specific plan directory as argument |
| `planning-split` | Splits completed tasks into `.plans/<NNN-name>/tasks/` |
| `planning-review` | Reviews a specific plan directory |
