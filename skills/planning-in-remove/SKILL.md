---
name: planning-in-remove
description: "Remove a plan from the .planning-dir registry. Does NOT delete files on disk — only unregisters the plan so hooks stop tracking it. Usage: /planning-in-remove <dir>. Use when user says 'remove plan', 'unregister plan', 'stop tracking plan', or after archiving a completed plan."
user-invocable: true
disable-model-invocation: true
allowed-tools: "Read, Edit, Bash"
---

# Remove Plan from Registry

Unregister a plan directory from `.planning-dir`. Files on disk are preserved.

## Workflow

### 1. Identify target

Parse the argument as the directory to remove. If omitted, show the current registry and ask which one to remove:

```bash
cat -n .planning-dir 2>/dev/null
```

### 2. Remove from registry

```bash
grep -vxF "<directory>" .planning-dir > .planning-dir.tmp && mv .planning-dir.tmp .planning-dir
```

If `.planning-dir` is now empty, delete it:
```bash
[ -s .planning-dir ] || rm .planning-dir
```

### 3. Confirm

```
Removed ./plans/refactor from registry.
Files still on disk at ./plans/refactor/ — delete manually or use planning-archive first.
Active plans remaining: 1
```
