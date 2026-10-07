# Execution-Ready Handoff

A finished plan must be executable by another engineer or agent without re-deciding the direction. Condensed from the `think` handoff and validation sections.

## Validate before handing off

- More than 8 files or 1 new service? Acknowledge it explicitly.
- More than 3 components exchanging data? Draw an ASCII diagram and look for cycles.
- Every meaningful test path listed: happy path, errors, edge cases.
- Can this be rolled back without touching data?
- Every API key, token, MCP server, external API, and third-party CLI listed with a one-line purpose and reachability check. No credential requests mid-implementation.

## Attack angles (conditional)

Run only when the plan involves external dependencies, high concurrency, or data migration:

| Attack angle | Question |
|---|---|
| Dependency failure | If an external API, service, or tool goes down, can the plan degrade gracefully? |
| Scale explosion | At 10x data volume or user load, which step breaks first? |
| Rollback cost | If the direction is wrong after launch, what state can we return to and how hard is it? |

If an attack holds, deform the design to survive it. If it shatters the approach entirely, discard it and say why. Never present a plan that failed an attack without disclosing the failure.

## Plan red flags (self-check)

- A phase depends on the next phase to be useful (cannot ship alone).
- A "Phase 0: investigate / spike" exists. Investigation belongs before the plan, not inside it.
- Any `TBD` / `TODO` / "implement later" / "similar to step N" remains.

Either of the first two means the work is not staged; ship it as one phase instead of pretending it is staged. The third means the plan is not ready.

## Detached check (交接检查)

When the plan will be executed outside the current session (a fresh session, or
parallel worker agents), the question is: *could a new session, reading only
the plan directory plus the repo-level docs, start every phase without asking
anything the planning session already knew?* The author cannot answer that by
re-reading. Run the Detached check, which covers the sweep, the decision harvest, and
the cold-start pass at the depth its trigger allows: [detached-handoff.md](detached-handoff.md).

## Handoff contents

- Scope and non-scope.
- Chosen approach, and the one rejected alternative if the tradeoff was close.
- Public API, schema, command, config, or file-interface changes, if any.
- Verification commands and manual acceptance checks.
- Release, publish, migration, or issue/PR follow-through steps, if the task continues there.
- Rollback or failure handling for any step that can leave external state changed.

When the user asks to export a handoff, or the environment prevents further execution, make it execution-ready instead of explaining the limitation: file targets, key constants or selectors, exact commands, runtime or visual checklist, and risk boundaries. If the work depends on a screenshot or artifact, name the artifact and the pass/fail delta.

## Execution entry point

When the user approves the plan and says "implement" / "可以干" / "按计划实施",
implement directly, working through the plan phases as a to-do list and verifying
each. When `progress.md` has a phase handoff table, confirm the rows of the
phases this phase depends on (per the Playbook's orchestration section, else the
preceding phase) are filled before starting it; an empty row is drift, so name it
and stop. Fill the phase's own row when it merges. If the user invokes `/check`, its Plan Execution mode owns that loop and
transitions to Ship when done; do not enter `check` on your own. `plan` itself
does not implement code.

## Persisting the plan

Write the approved design header (Goal, Building/Not Building, Approach, Key Decisions, Premise Collapse, External Dependencies, Verification Plan, Rollback) into `task_plan.md` in the target directory (the directory the user named, or `.plans/<NNN>-<slug>/` by default — contract in `shared/plan-artifacts.md`). `plan` records the plan itself; there is no separate persistence step.
