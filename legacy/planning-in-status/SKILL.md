---
name: planning-in-status
description: "Show all active plans from .plans/. Displays each plan's name, directory, current phase, and completion progress. Use when the user says 'planning status', 'show plans', 'plan status', or '/planning-in-status'."
user-invocable: true
disable-model-invocation: true
allowed-tools: "Read, Bash, Glob, Grep"
---

# Planning Status

Show a dashboard of all plans in `.plans/`, fed by the global metadata
index `.plans/_index.json`.

## Workflow

### 1. Render via the index

The single source of truth for the dashboard is `plans-index.py dashboard`.
It re-syncs the index from disk before printing, so output is always fresh:

```bash
python3 ~/.agents/skills/planning-in/scripts/plans-index.py dashboard
```

This produces sections for **Active**, **Completed**, and **Stale** plans
with status icons, phase progress, current phase, file line counts,
error counts, and last-updated timestamp.

If `.plans/` does not exist or contains no plans, it prints:

```
No active plans. Use /planning-in <name> to create one.
```

### 2. Fallback (index unreadable)

If the script fails (missing python3, broken file, unusual layout),
fall back to the legacy scan:

```bash
find .plans -maxdepth 2 -name task_plan.md -exec dirname {} \;
```

For each directory, read `task_plan.md` and extract:

- **Plan title**: first `# ` heading
- **Current phase**: value under `## Current Phase`
- **Phase status**: each `**Status:** xxx` line within `### Phase N:` sections
- **Error count**: data rows in the `## Errors Encountered` table
- **File sizes**: `wc -l` of the three files

Exclude `archive/`, `active/` staging, and any directory starting with `_`
(including `_index.json`).

### Status Icons

| status | icon |
|--------|------|
| `pending` | ⏸️ |
| `in_progress` | 🔄 |
| `complete` | ✅ |
| `failed` / `blocked` | ❌ |

### Aggregate plan status (from index)

- All phases `complete` → **complete**
- Any phase `failed` or `blocked` → **blocked**
- Any phase `in_progress` (or some `complete`, others `pending`) → **in_progress**
- Else → **pending**

### Stale entries

Directories without `task_plan.md` appear in the **Stale** section.
Suggest: `Use /planning-in-remove to clean up stale directories.`

## Manual JSON access

For automation or programmatic queries, read the index directly:

```bash
python3 ~/.agents/skills/planning-in/scripts/plans-index.py show
# or just:
cat .plans/_index.json
```

If the index is missing or stale, rebuild it from disk (idempotent):

```bash
python3 ~/.agents/skills/planning-in/scripts/plans-index.py rebuild
```
