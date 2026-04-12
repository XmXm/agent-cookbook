# Planning Archive Conventions

Shared conventions for `planning-archive`, `planning-split`, `planning-organize`, and `planning-review` skills.

## Archive Directory Layout

```
docs/planning-archive/
├── active/                          # Staging area for split-but-not-yet-archived tasks
│   ├── tasks/
│   │   ├── task-06-plan.md
│   │   ├── task-06-progress.md
│   │   └── ...
│   └── findings/
│       ├── show-entity-lifecycle.md
│       └── ...
├── 001-refactor-concurrent/         # Archived plan (numbered)
│   ├── task_plan.md                 # Full or index (depending on whether split was used)
│   ├── progress.md
│   ├── findings.md
│   ├── tasks/                       # Only present if plan was split before archiving
│   │   └── ...
│   └── findings/                    # Only present if plan was split before archiving
│       └── ...
├── 002-next-plan-name/
│   └── ...
```

## Naming Conventions

- **Plan directory**: `NNN-kebab-case-name` (3-digit zero-padded sequence + descriptive slug)
  - Sequence determined by scanning existing directories in `docs/planning-archive/`
- **Task files**: `task-NN-{plan,progress,findings}.md` (2-digit task number, or `phase-NN-*` for phase-based plans)
- **Finding files**: `kebab-case-topic.md` (derived from the `## ` heading)
- `tasks/` holds task-scoped content; `findings/` holds cross-task or project-level research

## What Gets Split vs. What Stays

| Content type | Destination | Split? |
|---|---|---|
| Project-level sections in task_plan.md (goal, architecture, design decisions, risks) | Stays in root file | No |
| Cross-cutting sections in task_plan.md (execution order, notes) | Stays in root file | No |
| Project-level sections in findings.md (Requirements, Technical Decisions) | Stays in root file | No |
| `### Task N:` section in task_plan.md | `tasks/task-NN-plan.md` | Per task |
| Date entries in progress.md tied to a task | `tasks/task-NN-progress.md` | Per task |
| `## Topic` section in findings.md tied to **one** task | `tasks/task-NN-findings.md` | Per task |
| `## Topic` section in findings.md spanning **multiple tasks** | `findings/topic-name.md` | Per topic |

**Findings ownership rule**: If a findings section serves only one task, it belongs in `tasks/`. If referenced by multiple tasks or is project-level knowledge, it belongs in `findings/`.

## How to Identify Task Boundaries

### task_plan.md

Primary pattern: `### Task N: Title` or `### Phase N: Title`
- Section runs until the next `### Task`/`### Phase` heading or a `## ` heading
- Sub-tasks use `#### N.M` numbering within the task section

### progress.md

Primary pattern: `## YYYY-MM-DD - Task N: Title` or `## Session N`
- A single task may span multiple date entries (multi-day work)
- Match by task number in the heading, or by reading content that references the task
- Each date entry is the unit of extraction — collect all entries for the same task

### findings.md

Primary pattern: `## Topic Title (YYYY-MM-DD)`
- Topics are rarely labeled by task number — match by reading content
- Some topics span multiple tasks (shared research) — keep as standalone files in `findings/`

## Split Link Format

When a section is split out, replace it in the root file with a single-line link:

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

## Split File Header Format

Each split file includes a metadata header:

```markdown
# Task NN: Title

> Source: task_plan.md | Plan: active
> Status: completed | Commits: abc1234, def5678

---

[original section content, verbatim]
```

## Directory Resolution

All planning skills that operate on existing plan files share this resolution logic. Run it before doing anything else:

1. If the user `@` referenced a specific file (e.g., `@plans/refactor/task_plan.md`) → use that file's parent directory
2. If `.planning-dir` exists:
   - Single entry → use that directory
   - Multiple entries → list them and ask the user which plan to operate on
3. Default → `.` (project root)

Set `PLAN_DIR` to the resolved directory. All file references use `$PLAN_DIR/task_plan.md`, `$PLAN_DIR/findings.md`, `$PLAN_DIR/progress.md`.

## Integration with Planning Tools

| Phase | Tool | Action |
|-------|------|--------|
| Start new plan (root) | `planning-with-files` | Creates task_plan.md, progress.md, findings.md in project root |
| Start new plan (custom dir) | `planning-in` | Creates the three files in a specified directory, registers in `.planning-dir` |
| During work | `planning-with-files` or `@` file directly | Maintains and updates the three files |
| Files getting large | `planning-split` | Splits completed tasks, keeps source files lean |
| Structure messy | `planning-organize` | Reorganizes sections for coherence |
| Quality check | `planning-review` | Multi-agent review of plan content |
| Plan complete | `planning-archive` | Archives entire plan, removes from `.planning-dir` registry |
| Start next plan | `planning-with-files` or `planning-in` | Creates fresh files for the new plan |

## Detecting Prior Splits

A plan has been previously split if **any** of these are true:
- `docs/planning-archive/active/` directory exists
- Root planning files contain markdown links pointing to `docs/planning-archive/active/`
  - Pattern: `](docs/planning-archive/active/` in any of the three files
