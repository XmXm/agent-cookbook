---
name: planning-in-status
description: "Show all active plans tracked in .planning-dir registry. Displays each plan's name, directory, current phase, and completion progress. Use when the user says 'planning status', 'show plans', 'plan status', or '/planning-in-status'."
user-invocable: true
disable-model-invocation: true
allowed-tools: "Read, Bash, Glob, Grep"
---

# Planning Status

Show a dashboard of all active plans registered in `.planning-dir`.

## Workflow

### 1. Read registry

```bash
cat .planning-dir 2>/dev/null
```

If `.planning-dir` doesn't exist or is empty, report: `No active plans. Use /planning-in <dir> to create one.`

### 2. For each registered directory

Read `task_plan.md` and extract:
- **Plan title**: first `# ` heading
- **Current phase**: `## Current Phase` value
- **Phase completion**: count phases with `complete` vs total phases
- **Phase list with status icons**: show each phase name with its status icon
- **Error count**: count rows in `## Errors Encountered` table (if present)
- **File sizes**: line counts of all three files

If a registered directory is missing or has no `task_plan.md`, mark it as `[stale]`.

### Status Icons

- `pending` → ⏸️
- `in_progress` → 🔄
- `complete` → ✅
- `failed` or `blocked` → ❌

### 3. Output format

```
Active Plans (2):

  [refactor] ./plans/refactor/
    API Refactor — Phase 4/5 (🔄 in_progress)
    ✅ Phase 1: Requirements & Discovery
    ✅ Phase 2: Planning & Structure
    ✅ Phase 3: Implementation
    🔄 Phase 4: Testing & Verification  ← current
    ⏸️ Phase 5: Delivery
    Files: task_plan(120L) findings(45L) progress(80L)
    Errors logged: 2

  [auth] ./plans/auth/
    Auth Migration — Phase 2/5 (🔄 in_progress)
    ✅ Phase 1: Requirements & Discovery
    🔄 Phase 2: Planning & Structure  ← current
    ⏸️ Phase 3: Implementation
    ⏸️ Phase 4: Testing & Verification
    ⏸️ Phase 5: Delivery
    Files: task_plan(60L) findings(20L) progress(30L)
    Errors logged: 0
```

### 4. Stale entries

If any entry points to a missing directory or missing `task_plan.md`:

```
  [old-feature] ./plans/old-feature/ [stale — no task_plan.md]
```

Suggest: `Use /planning-in:remove to clean up stale entries.`
