---
name: planning-split
description: "Split large completed task sections from planning documents (task_plan.md, progress.md, findings.md) into individual files under docs/planning-archive/active/. Works with plans created by planning-with-files (project root) or planning-in (custom directory). Source files stay in place but get slimmer — split sections are replaced with one-line links. Does NOT archive or delete source files — use planning-archive for that. Use when planning files exceed ~1000 lines, when the user says 'split task', 'split planning docs', 'planning files too big', 'slim down plan'."
user-invocable: true
disable-model-invocation: true
---

# Planning Split

Extract completed task sections from planning files into individual files under `docs/planning-archive/active/`. Source files remain the working documents — they just get slimmer by replacing extracted sections with links.

For directory conventions, naming rules, and task boundary identification, read the shared conventions file:
`~/.claude/skills/planning-archive/references/conventions.md`

## Directory Resolution

Follow the shared Directory Resolution rules in `~/.claude/skills/planning-archive/references/conventions.md` to determine `PLAN_DIR`.

> **Note**: Source files come from `$PLAN_DIR`, but the staging directory for split files is always `docs/planning-archive/active/` at the project root — this keeps the archive centralized regardless of where the plan lives.

## When to Use

- Planning files are getting large (>1000 lines combined)
- Multiple tasks are completed and taking up space in the source files
- The user wants to focus source files on active work only
- The user says "split", "slim down", "archive completed tasks"

## Rules

- Only split tasks that are **completed** and **not the current or previous task**
- Unfinished tasks always keep their full content in the source files
- Keep project-level sections (goal, architecture, decisions, risks) in source files
- Minimum threshold: task section must be **>30 lines** to be worth splitting
- Already-split sections (containing links to `docs/planning-archive/active/`) are skipped

## Workflow

### 1. Create staging directory

```bash
mkdir -p docs/planning-archive/active/tasks
mkdir -p docs/planning-archive/active/findings
```

### 2. Build task inventory

Read all three source files from `$PLAN_DIR`. For each file, identify every task/phase section using the boundary rules from conventions.md.

Print an inventory table:

```
Source files: $PLAN_DIR/task_plan.md (3365 lines), progress.md (1625 lines), findings.md (1830 lines)

Splittable sections:
| Task | Title                          | Status    | Lines plan | Lines progress | Lines findings | Split? |
|------|--------------------------------|-----------|-----------|---------------|----------------|--------|
| 6    | BaseEntityReplica lifecycle     | completed | 43        | 12            | 0              | yes    |
| 7    | BaseEntityReplica field trim    | completed | 68        | 35            | 28             | yes    |
| 21   | _src delegate decoupling       | in_prog   | 95        | 40            | 30             | NO     |
| 22   | Current task                   | in_prog   | 20        | 5             | 0              | NO     |

Findings topics (cross-task):
| Topic                          | Lines | Split? |
|--------------------------------|-------|--------|
| ShowEntity lifecycle timing    | 78    | yes    |
| Sync mechanism overview        | 45    | yes    |

Estimated reduction: 3365 -> 1850 lines (task_plan.md), ...
```

Confirm with user before proceeding.

### 3. Extract sections into individual files

For each splittable task, extract content verbatim into individual files:

**Task plan content** -> `docs/planning-archive/active/tasks/task-NN-plan.md`:
```markdown
# Task NN: Title

> Source: task_plan.md | Plan: active
> Status: completed

---

[original section content, verbatim]
```

**Task progress entries** -> `docs/planning-archive/active/tasks/task-NN-progress.md`:
```markdown
# Task NN: Title — Progress

> Source: progress.md | Plan: active

---

[all date entries for this task, verbatim]
```

**Task-scoped findings** -> `docs/planning-archive/active/tasks/task-NN-findings.md`
**Cross-task findings** -> `docs/planning-archive/active/findings/topic-name.md`

### 4. Replace sections in root files with links

In each root file, replace the extracted section with a single-line link:

**task_plan.md**:
```markdown
### Task N: Title — [plan](docs/planning-archive/active/tasks/task-NN-plan.md)
> One-line summary of what this task accomplished.
```

**progress.md**:
```markdown
## YYYY-MM-DD ~ YYYY-MM-DD — Task N: Title — [progress](docs/planning-archive/active/tasks/task-NN-progress.md)
> Key outcome in one line.
```

**findings.md**:
```markdown
## Topic Title — [detail](docs/planning-archive/active/findings/topic-name.md)
> Key insight in one line.
```

### 5. Report

Show before/after line counts:

```
Split complete:
  task_plan.md:  3365 -> 1850 lines (-45%)
  progress.md:   1625 -> 890 lines (-45%)
  findings.md:   1830 -> 1200 lines (-34%)

Files created: 12 in tasks/, 2 in findings/
```

## After Splitting

When the plan is eventually complete, use `planning-archive` to move everything into a numbered directory. It will detect the `active/` staging area and merge it automatically, updating all internal paths.
