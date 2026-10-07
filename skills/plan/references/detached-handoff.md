# Detached Check (交接检查)

Make a persisted plan executable by a fresh session or worker agents that never
saw the planning conversation. The plan directory, repo-level docs, and source
must be enough to start every phase; anything else is a leak.

Applies to a plan that will be executed by a session that did not plan it.
Workers dispatched and accepted within the planning session (e.g. a delegate
chain) are not detached. If an approved plan exists only in the conversation
and the user asks for a cross-session handoff, persist it first under the
`shared/plan-artifacts.md` contract, then run this check. If there is no
approved plan at all (an in-progress conversation, an unapproved design), the
check does not apply: say so and suggest the user run `/handoff`, the
session-level skill, which is user-invoked only. Tracking execution state
belongs to `progress.md` under `/check` Plan Execution.

## Depth

The depth depends on how the check was triggered, so that routine persistence
does not become an expensive ritual:

| Trigger | Run |
|---|---|
| Automatic, because a plan was persisted for detached execution | Sweep lens A, plus rows 15–16 of lens B, answered from the plan text and repo reading without running gates or live probes; step 2 only for decisions actually found; the first-tier re-read. Report as "self-checked, not cold-start verified". Never escalates beyond this row on its own; offer the fuller check in one line |
| The user explicitly asks for a check on a cross-repo plan, one that depends on external environments, or one with 3+ phases | Full live sweep, step 2, and the per-phase cold-start simulation. The simulation fans out only if the environment's orchestration rules permit it; otherwise run the first tier and say so |
| Explicit ask on a smaller plan | Full live sweep, step 2, and the first-tier re-read; offer the simulation in one line |

## Done when

- Every phase can be started, and driven to its verification gate, from the
  plan directory, repo docs, and source alone, without guessing a
  consequential decision.
- Every question that remains is a deliberate, written confirmation point
  (e.g. "confirm before each paid run"), never a missing fact or open decision.
- No reference points into session-only storage.
- The status line reflects the real state (e.g. `已批准待实施`).
- The report says which tier ran. A self-check is labeled as such: the
  author cannot see what they know implicitly, so only the cold-start tier
  counts as verified.

## 1. Sweep

Two lenses. A row is clean when it does not apply (no plan text needed) or the
plan answers it with evidence checked live (open the config, run `--help`,
read the guard test, run the gate command). Fix hits in place, in the section
named (revision discipline in `shared/plan-artifacts.md`).

### A. Context the planner knows but the plan does not say

| # | Category | Look for | Fix into |
|---|---|---|---|
| 1 | Session-only artifacts | scratchpad or `/tmp` paths, generated schemas/types, local clones, agent transcripts cited as evidence | `research/` transcription, or a regeneration command with the tool version |
| 2 | Baseline and drift | commit the plan was written against; `file:line` references | Playbook baseline, plus "relocate by symbol, not line" and known drift |
| 3 | Environments and access | which environment or host each phase runs on, how to reach it, whether it shares state with production | Playbook "External dependencies and access" |
| 4 | Isolation from production | how tests avoid production state: credentials, config dirs, ports, databases, registered clients or devices | Playbook "Integration isolation" |
| 5 | Authorization for costly or outward actions | paid model or API calls, remote logins, tool upgrades, production reads | Playbook rule per action: pre-authorized budget, or confirm before each run |
| 6 | Branch, push, and release interplay | can unfinished commits ride along with another session's push or a deploy? | Playbook branch discipline, stated explicitly |
| 7 | Guards the plan must overturn | tests or docs encoding an earlier decision the plan reverses | name each guard; record the reversal as a decision |
| 8 | Live environment facts | the user's actual config makes a test path never trigger; tool defaults differ by OS | the phase gate, with the test-only configuration that exercises the path |
| 9 | Phase handoff facts | values only known after phase N that phase N+1 needs (measured limits, chosen fallbacks, commits) | the `progress.md` handoff table |
| 10 | Rollout and rollback reality | cross-repo deploy order; how a user turns the feature on and off; one-way schema changes (forward-fix only); the stop-the-bleeding lever, verified to exist | Playbook release checklist and rollback section |

### B. Claims an implementer would stop on

| # | Probe | Check | Fix into |
|---|---|---|---|
| 11 | Reuse and existence | every mechanism the plan says to reuse, extend, or rely on (task kinds, commands, flags, UI entry points, providers, storage slots) exists at the baseline and supports the new use: types and encoding, size caps, lifecycle and deletion, namespace, reachability | the section making the claim |
| 12 | Name-only designs | each new file format, event, route, UI element, or tunable has a spec (location, fields, ID and version rules, options, thresholds, failure and close behavior), or an explicit delegation stating the constraints the implementer must satisfy | the section introducing it |
| 13 | Contracts consumed or held fixed | the real input shape from generated types, `--help`, or source, including per-OS variants; when a phase keeps a contract unchanged, map each new fact onto an existing type and check that type's side effects (e.g. an event type that fails the run) | the phase scope, as a mapping |
| 14 | Contracts frozen across phases | schemas, protocols, or field sets frozen early that later phases need, plus the mixed-version window: when versions are negotiated versus when payloads, digests, or IDs are frozen, and how in-flight old-shape records are handled | a complete field table in the freezing phase; release checklist |
| 15 | Internal consistency | statements about the same object agree across sections and research; every new discriminator or column states its value and behavior for each existing row kind and caller; uniqueness and deterministic-ID invariants survive every state transition (requeue, retry, cancel) | the single authoritative section; delete the conflicting text |
| 16 | Design-to-phase traceability | every design element (column, command, feature bullet, "e.g." list) belongs to exactly one phase with its files, schema change, and failure semantics; no deliverable depends on a later phase unless its partial form is specified | each phase's scope |
| 17 | Capacity of reused channels | count, size, time, and retention limits on every pipeline, queue, or table the new workload uses; a worst-case estimate for the longest allowed run; degrade at the limit rather than kill the work | the design section, plus a gate measurement |
| 18 | Authorization revalidation | for each new principal, source, or cached result: what is rechecked at dispatch, reconnect, and each call; cancel versus reject per failure, with error codes; what cached results may return after revocation; lookup keys scoped to the owner | the security or protocol section |
| 19 | Migration mechanics | entry points (preflight and runtime), backups, per-record failure policy, scale, test isolation from persistent dev stores | the migration's phase scope |
| 20 | Executable acceptance | run every gate command and inspect false positives and negatives; invariance checks name exact targets and tolerate tool-managed state; behavior-preservation claims capture a baseline before the change; acceptance names concrete fixtures that exist in the target environment; live or expensive tests are excluded from default runs, with results written to a named file | the phase gate |

Text added by earlier fixes or verifiers is swept the same way before the next round.

## 2. Decision harvest

Collect every item only the user can decide: authorization, which environment,
reversing a prior decision, branch or release policy. These are independent
confirmations, so ask them in one batch, one question per decision, with the
recommended option first. When the answers depend on each other, switch to
Grill's one-question-at-a-time interview. Do not ask anything the repo can answer.

Record each answer only in `task_plan.md`, in Key Decisions or the Playbook
rule it governs, marked `用户决策`. Never leave "to be confirmed" in the plan:
an unanswered decision blocks the handoff; it is not a placeholder.

## 3. Cold-start pass

**First tier — adversarial re-read (always).** Re-run the sweep reading as a
stranger: every "the implementer will know" is a leak. Label the result
self-checked.

**Second tier — simulation (per Depth).** One fresh agent per phase, then one
verifier. Fresh-agent brief:

> You have no access to the planning conversation. Read only the plan
> directory, the repo docs it points to, and source. Could you start phase N
> and reach its verification gate without stopping to ask or guessing a
> consequential decision? Unknowns the phase is meant to discover are not
> gaps. Classify each gap as `missing` (only the planner or user could know),
> `discoverable` (findable in the repo within about 10 minutes; say where), or
> `broken_ref`. Read-only; no paid calls.

The verifier drops `discoverable` items and anything the plan already answers,
merges duplicates, and writes the exact addition and target section for each
gap it keeps. Fold kept gaps in place, and send new user decisions back to step 2.

Run at most two rounds. The second round asks only for gaps that still block
or would cause a consequential wrong guess. If gaps are not dropping sharply
by then, stop and report the structural hole to the user; a third round of
detail will not fix it.

Fan-out follows the environment's orchestration rules (for example, only when
the user opted into multi-agent work). When that is not allowed, stay on the
first tier and label it honestly; do not present it as a simulation.

## 4. Write-back

- The plan stays the current decision: rewrite affected sections in place.
  There are no addendum sections, and no per-round revision logs in
  `research/` or elsewhere; git keeps the history.
- Report each pass in the conversation, per the skill's Output
  (verdict per phase, decisions collected, gaps fixed and where).
- Update the Playbook's applicable subsections and seed the `progress.md`
  handoff table (templates in `shared/plan-artifacts.md`).
- Any decision a phase needs is written in the plan. Memory-store keywords are
  background only, never the sole source.

## Anti-patterns

- Dumping the conversation into the plan instead of the decisions and facts it produced.
- Writing N/A sections for categories that do not apply.
- Line numbers as the only locator for code that other sessions keep changing.
- Secrets, tokens, or personal credentials in the plan. Name where they live and how to verify them instead.
- Presenting an author re-read as a cold-start pass.
- Adding detail indefinitely. Once every phase can start, the remaining
  unknowns are the phases' own work, captured by the handoff table.
