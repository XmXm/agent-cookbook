---
name: planning-in
description: "Create planning files (task_plan.md, findings.md, progress.md) in a specified directory or project root. Supports multiple concurrent plans via .planning-dir registry. Usage: /planning-in [dir]. No argument = project root (like planning-with-files). With directory = multi-plan mode, name inferred from basename. For existing plans, just @ the task_plan.md file directly. Use when the user says 'plan', 'plan in', 'planning in', 'start planning', or wants file-based planning."
user-invocable: true
disable-model-invocation: true
allowed-tools: "Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|Bash|Read|Glob|Grep"
      hooks:
        - type: command
          command: "[ -f .planning-dir ] && while IFS= read -r d; do [ -n \"$d\" ] && [ -f \"$d/task_plan.md\" ] && printf '[%s] %s\\n' \"$(basename \"$d\")\" \"$(grep -m1 '^## Current Phase' \"$d/task_plan.md\" -A1 2>/dev/null | tail -1)\"; done < .planning-dir || true"
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "[ -f .planning-dir ] && echo '[planning-in] File updated. Check if any active plan phase needs status update.' || true"
  Stop:
    - hooks:
        - type: command
          command: "sh ~/.claude/skills/planning-in/scripts/check-complete.sh"
---

# Planning In

Create planning files in a **user-specified directory**. Supports multiple concurrent plans.

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
/planning-in [directory]
```

- **No argument** → project root (equivalent to `planning-with-files`), plan name = project directory basename
- **With directory** → multi-plan mode, plan name inferred from directory basename (e.g., `./plans/refactor` → "refactor")

Examples:
- `/planning-in` — create plan in project root
- `/planning-in ./plans/refactor` — create plan "refactor"
- `/planning-in ./plans/auth` — create another concurrent plan "auth"

For existing plans, the user will `@` reference the `task_plan.md` file directly — no skill invocation needed.

## Multi-Plan Architecture

Each plan is independent — own directory, own files. `.planning-dir` in the project root is a **registry** (one path per line) tracking all active plans.

```
# .planning-dir
./plans/refactor
./plans/auth
```

## Workflow

### 1. Parse directory and infer name

```bash
PLAN_DIR="${argument:-.}"   # default to project root if no argument
if [ "$PLAN_DIR" = "." ]; then
    PLAN_NAME="$(basename "$(pwd)")"
else
    PLAN_NAME="$(basename "$PLAN_DIR")"
    mkdir -p "$PLAN_DIR"
fi
```

### 2. Register

Append to `.planning-dir` (skip if already registered):

```bash
grep -qxF "$PLAN_DIR" .planning-dir 2>/dev/null || echo "$PLAN_DIR" >> .planning-dir
```

> Add `.planning-dir` to `.gitignore` — it's a local session artifact.

### 3. Check for existing files

```bash
ls "$PLAN_DIR"/{task_plan,findings,progress}.md 2>/dev/null
```

If files exist: show status, ask resume or start fresh.

### 4. Initialize

Run the init script:
```bash
sh ~/.claude/skills/planning-in/scripts/init-session.sh "$PLAN_DIR"
```

Or create files directly using the templates below.

### 5. Confirm

```
Plan: refactor
Directory: ./plans/refactor/
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

```markdown
# Task Plan: [Plan Name]

## Goal
[One sentence describing the end state]

## Current Phase
Phase 1

## Phases

### Phase 1: Requirements & Discovery
- [ ] Understand user intent
- [ ] Identify constraints and requirements
- [ ] Document findings in findings.md
- **Status:** in_progress

### Phase 2: Planning & Structure
- [ ] Define technical approach
- [ ] Create project structure if needed
- [ ] Document decisions with rationale
- **Status:** pending

### Phase 3: Implementation
- [ ] Execute the plan step by step
- [ ] Write code to files before executing
- [ ] Test incrementally
- **Status:** pending

### Phase 4: Testing & Verification
- [ ] Verify all requirements met
- [ ] Document test results in progress.md
- [ ] Fix any issues found
- **Status:** pending

### Phase 5: Delivery
- [ ] Review all output files
- [ ] Ensure deliverables are complete
- [ ] Deliver to user
- **Status:** pending

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

## The 5-Question Reboot Test

If you can answer these, your context management is solid:

| Question | Answer Source |
|----------|---------------|
| Where am I? | Current phase in task_plan.md |
| Where am I going? | Remaining phases |
| What's the goal? | Goal statement in plan |
| What have I learned? | findings.md |
| What have I done? | progress.md |

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

## Scripts

Helper scripts for automation:

- `scripts/init-session.sh` — Initialize planning files in a directory
- `scripts/check-complete.sh` — Verify all phases complete across all plans
- `scripts/session-catchup.py` — Recover context from previous session

## Advanced Topics

- **Manus Principles:** See [reference.md](reference.md)
- **Real Examples:** See [examples.md](examples.md)

## Integration with Other Planning Skills

| Skill | Integration |
|-------|------------|
| `planning-in:status` | Show all active plans from registry |
| `planning-in:remove` | Remove a plan from registry (keeps files) |
| `planning-organize` | Pass the specific plan directory as argument |
| `planning-split` | Splits completed tasks from a specific plan directory |
| `planning-archive` | Archives a specific plan directory, then remove from registry |
| `planning-review` | Reviews a specific plan directory |
