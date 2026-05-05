---
name: planning-in-remove
description: "Remove a plan directory from .plans/. Deletes the plan's task_plan.md, findings.md, progress.md and its directory. Usage: /planning-in-remove <name>. Use when user says 'remove plan', 'delete plan', 'clean up plan', or to remove stale or completed plans that were not archived."
user-invocable: true
disable-model-invocation: true
allowed-tools: "Read, Edit, Bash"
---

# Remove Plan

Delete a plan directory from `.plans/`. This removes all planning files for that plan.

## Workflow

### 1. Identify target

Parse the argument as the plan name. If omitted, show active plans and ask which one to remove:

```bash
find .plans -maxdepth 2 -name task_plan.md -exec dirname {} \;
```

### 2. Confirm

Show what will be deleted:

```
About to delete: .plans/refactor/
  task_plan.md (277 lines)
  progress.md (101 lines)
  findings.md (194 lines)
Continue? [y/N]
```

### 3. Delete

```bash
rm -rf ".plans/<plan-name>"
```

### 4. Update the global index

After deletion, drop the entry from `.plans/_index.json`:

```bash
python3 ~/.agents/skills/planning-in/scripts/plans-index.py remove ".plans/<plan-name>"
```

If that script is unavailable or fails, the index can always be regenerated from disk:

```bash
python3 ~/.agents/skills/planning-in/scripts/plans-index.py rebuild
```

### 5. Confirm

```
Deleted .plans/refactor/ (3 files removed).
Removed .plans/refactor from .plans/_index.json.
Active plans remaining: 1
```
