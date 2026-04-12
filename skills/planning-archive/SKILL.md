---
name: planning-archive
description: "Archive completed planning documents (task_plan.md, progress.md, findings.md) into a numbered directory under docs/planning-archive/. Works with plans created by planning-with-files (project root) or planning-in (custom directory). Does NOT split tasks — use planning-split for that. Handles both unsplit and previously-split plans. Use when the user says 'archive plan', 'archive this plan', 'plan done', or when all tasks/phases are complete."
user-invocable: true
disable-model-invocation: true
---

# Planning Archive

Move a completed plan's three root files (task_plan.md, progress.md, findings.md) into a numbered archive directory. No splitting — files are archived as-is.

For directory conventions, naming rules, and task boundary identification, read [references/conventions.md](references/conventions.md).

## When to Use

- The plan is complete (all tasks/phases done)
- The user wants to clear root planning files and start fresh
- The user says "archive plan", "archive", "plan done"

## Directory Resolution

Follow the shared Directory Resolution rules in [references/conventions.md](references/conventions.md) to determine `PLAN_DIR`.

## Workflow

### 1. Determine plan_id

Ask the user for a name, or suggest one based on the plan's title.

Format: `NNN-kebab-case-name` (e.g., `001-monorepo-platform`)

Determine the sequence number by scanning existing directories:
```bash
ls docs/planning-archive/ 2>/dev/null
```
Next number = highest existing NNN + 1, or 001 if none exist. Exclude `active/` from numbering.

### 2. Pre-flight check

Read all three files from `$PLAN_DIR`. Check for unfinished tasks/phases.

If any task is not marked completed, warn the user:
```
WARNING: Task 21 status is "in_progress" — archive anyway? [y/N]
```

Print a summary:
```
Plan: 001-refactor-concurrent
Files: task_plan.md (277 lines) | progress.md (101 lines) | findings.md (194 lines)
Status: all phases complete
Previously split: yes/no
```

### 3. Detect prior splits

Check whether `planning-split` was previously used:

1. Check if `docs/planning-archive/active/` exists
2. Check if root files contain links matching `](docs/planning-archive/active/`

**If NOT split** (simple case):
- Create archive directory: `mkdir -p docs/planning-archive/{plan_id}`
- Move files: `mv $PLAN_DIR/task_plan.md $PLAN_DIR/progress.md $PLAN_DIR/findings.md docs/planning-archive/{plan_id}/`
- Done.

**If previously split** (path update needed):
- Create archive directory: `mkdir -p docs/planning-archive/{plan_id}`
- Move split files: `mv docs/planning-archive/active/tasks docs/planning-archive/{plan_id}/` (if exists)
- Move split findings: `mv docs/planning-archive/active/findings docs/planning-archive/{plan_id}/` (if exists)
- Update paths in all three files: replace `docs/planning-archive/active/` with `docs/planning-archive/{plan_id}/` throughout
- Move updated files: `mv $PLAN_DIR/task_plan.md $PLAN_DIR/progress.md $PLAN_DIR/findings.md docs/planning-archive/{plan_id}/`
- Remove staging: `rmdir docs/planning-archive/active/` (should be empty now)

### 4. Verify

- Confirm archive directory has the expected files
- If split files exist, confirm all internal links resolve
- Report: `Archived to docs/planning-archive/{plan_id}/ — N files`

### 5. Clean up

- `$PLAN_DIR` should now be free of planning files
- If `$PLAN_DIR` is not project root and is now empty, remove it: `rmdir $PLAN_DIR`
- If plan was registered in `.planning-dir`, remove the entry (same as `/planning-in:remove`)
