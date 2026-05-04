# Examples: Planning-In Multi-Plan Workflow

## Example 1: Research Task (Single Plan)

**User:** `/planning-in exercise-research`

```
Plan: exercise-research
Directory: .plans/exercise-research/
Files: task_plan.md | findings.md | progress.md
Active plans: 1
```

### Loop 1: Create Plan
```bash
Edit .plans/exercise-research/task_plan.md   # Set goal and phases
```

### Loop 2: Research
```bash
Read .plans/exercise-research/task_plan.md   # Refresh goals
WebSearch "morning exercise benefits"
Edit .plans/exercise-research/findings.md    # Store findings (2-Action Rule)
Edit .plans/exercise-research/task_plan.md   # Mark Phase 2 complete
```

### Loop 3: Synthesize & Deliver
```bash
Read .plans/exercise-research/task_plan.md   # Refresh goals
Read .plans/exercise-research/findings.md    # Get findings
Write summary.md                              # Deliverable
Edit .plans/exercise-research/task_plan.md   # Mark complete
```

---

## Example 2: Concurrent Plans (Multi-Plan)

**User runs two plans in parallel:**

```bash
/planning-in auth-refactor
/planning-in dark-mode
```

```
.plans/
├── auth-refactor/
│   ├── task_plan.md
│   ├── findings.md
│   └── progress.md
└── dark-mode/
    ├── task_plan.md
    ├── findings.md
    └── progress.md
```

### PreToolUse hook now shows both:
```
[auth-refactor] Phase 3: Implementation
[dark-mode] Phase 1: Requirements & Discovery
```

### Working on auth-refactor:
```bash
Read .plans/auth-refactor/task_plan.md
Edit src/auth/login.ts
Edit .plans/auth-refactor/progress.md        # Log changes
Edit .plans/auth-refactor/task_plan.md       # Update phase
```

### Switching to dark-mode:
```bash
Read .plans/dark-mode/task_plan.md           # Context switch
Read .plans/dark-mode/findings.md
Edit src/styles/theme.ts
Edit .plans/dark-mode/findings.md            # 2-Action Rule
```

---

## Example 3: Bug Fix with Error Recovery

**User:** `/planning-in fix-login-bug`

### task_plan.md after investigation:
```markdown
# Task Plan: fix-login-bug

## Goal
Fix TypeError in validateToken() preventing successful login.

## Current Phase
Phase 3

## Phases

### Phase 1: Understand Bug Report
- [x] Reproduce the error
- [x] Locate auth handler: src/auth/login.ts
- **Status:** complete

### Phase 2: Identify Root Cause
- [x] Trace call chain
- [x] Found: user object not awaited properly
- **Status:** complete

### Phase 3: Implement Fix
- [ ] Fix async/await in validateToken()
- [ ] Add error boundary
- **Status:** in_progress

### Phase 4: Test & Verify
- [ ] Run unit tests
- [ ] Manual login test
- **Status:** pending

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| TypeError: Cannot read 'token' of undefined | 1 | Root cause: missing await on getUser() |
| Test still failing after fix | 2 | Also needed to update mock in test fixture |
```

### The 3-Strike Protocol in action:
```
Attempt 1: Fix await → test still fails
Attempt 2: Update test mock → passes
(No need for Attempt 3)
```

---

## Example 4: Error Recovery Pattern

When something fails, DON'T hide it:

### Before (Wrong)
```
Action: Read config.json
Error: File not found
Action: Read config.json    # Silent retry — BAD
```

### After (Correct)
```
Action: Read config.json
Error: File not found

# Update plan errors table:
| config.json not found | 1 | Will create default config |

Action: Write config.json (default config)
Action: Read config.json
Success!
```

---

## The Read-Before-Decide Pattern

**Always read the plan before major decisions:**

```
[Many tool calls have happened...]
[Context is getting long...]
[Original goal might be forgotten...]

→ Read .plans/my-plan/task_plan.md    # Goals back in attention!
→ Now make the decision                # Goals are fresh in context
```

This is why Manus can handle ~50 tool calls without losing track. The plan file acts as a "goal refresh" mechanism.

---

## Lifecycle Example: Plan → Complete → Archive

```bash
/planning-in feature-x          # Create plan (auto-numbered, e.g. .plans/006-feature-x/)
# ... work on feature-x ...
/planning-in-status              # Check all plans
# feature-x shows 5/5 phases complete
# Plan stays in .plans/006-feature-x/ — completed plans remain in place
```
