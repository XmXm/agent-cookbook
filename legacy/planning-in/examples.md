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
├── 001-auth-refactor/
│   ├── task_plan.md
│   ├── findings.md
│   └── progress.md
└── 002-dark-mode/
    ├── task_plan.md
    ├── findings.md
    └── progress.md
```

### PreToolUse hook now shows both:
```
[001-auth-refactor] Phase 2: Auth handler patch
[002-dark-mode] Phase 1: Theme token inventory
```

### Working on auth-refactor:
```bash
Read .plans/001-auth-refactor/task_plan.md
Edit src/auth/login.ts
Edit .plans/001-auth-refactor/progress.md        # Log changes
Edit .plans/001-auth-refactor/task_plan.md       # Update phase
```

### Switching to dark-mode:
```bash
Read .plans/002-dark-mode/task_plan.md           # Context switch
Read .plans/002-dark-mode/findings.md
Edit src/styles/theme.ts
Edit .plans/002-dark-mode/findings.md            # 2-Action Rule
```

---

## Example 3: Bug Fix with Error Recovery

**User:** `/planning-in fix-login-bug`

### task_plan.md after investigation:
```markdown
# Task Plan: fix-login-bug

## Goal
Fix TypeError in validateToken() preventing successful login.

## Building / Not Building
**Building:** Fix the async user lookup path in validateToken(), add regression coverage, and update the affected auth fixture.
**Not Building (out of scope):** Session storage redesign, provider migration, UI layout changes.

## Approach
Patch the missing await at the auth boundary, then update the mock fixture that models getUser(). Keep the fix inside the login validation path and prove it with the auth unit test plus a manual login smoke check.

## Key Decisions
| Decision | Rationale |
|----------|-----------|
| Fix validateToken() directly | The reproduced stack trace points to the auth validation path |
| Update the getUser() mock fixture | The failing regression test uses the same async contract |

## Premise Collapse
- **Most fragile assumption:** validateToken() is the only caller that treats getUser() as a sync value.
- **If it fails:** Other auth call sites may keep throwing TypeError after this patch.
- **Mitigation:** Search all getUser() call sites and include the result in findings.md before editing.

## External Dependencies
| Dependency | Why needed | Source / owner | Reachability check | Status |
|------------|------------|----------------|--------------------|--------|
| Local test runner | Regression coverage | package.json `test` script | `npm test -- auth` | ready |

## Verification Plan
| Phase | Command | Expected outcome |
|-------|---------|------------------|
| Phase 1 | `rg "getUser\\(" src test` | All call sites reviewed |
| Phase 2 | `npm test -- auth` | Auth tests pass |
| Phase 3 | Manual login smoke | Login completes without TypeError |

## Rollback
Revert the validateToken() patch and fixture update in one commit if the regression test exposes a wider auth contract issue.

---

## Current Phase
Phase 2

## Phases

### Phase 1: Reproduce and bound auth call sites
- [x] Reproduce the error
- [x] Locate auth handler: src/auth/login.ts
- [x] Search getUser() call sites
- **Verification:** `rg "getUser\\(" src test`
- **Status:** complete

### Phase 2: Patch validateToken async handling
- [x] Trace call chain
- [x] Found: user object not awaited properly
- [ ] Fix async/await in validateToken()
- [ ] Add error boundary
- **Verification:** `npm test -- auth`
- **Status:** in_progress

### Phase 3: Login smoke verification
- [ ] Manual login test
- **Verification:** Manual login smoke
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
