# Lightweight Acceptance Gate

For accepting finished work against the plan it promised. This is not a full code review. Heavy diff review, release gates, project audits, and triage are out of scope here.

## Did we build what was asked?

Compare the diff against the approved plan and label one of:

- **on target** — the diff matches the stated goal and scope.
- **drift** — a changed file, new dependency, new abstraction, or behavior change does not trace back to the goal in one sentence. Label drift until proven necessary.
- **incomplete** — part of the approved scope is missing.

Drift signals (any one is enough): a changed file unrelated to the goal, pure refactoring when the goal was a fix, a new dependency the goal did not mention, a new abstraction not required by the goal, or a cleanup change that quietly adds user-visible behavior.

## Hard-stop subset (block acceptance)

A focused subset of full-review hard stops, enough to catch irreversible harm at acceptance time:

- **No unverified claims.** "Tests pass" / "I verified X" only when the command output is in this session's transcript. Otherwise say "based on reading the code".
- **Re-read before citing facts.** Re-read line numbers, dirty-file counts, and branch state this turn before writing them into an acceptance note. Stale recall is the recurring long-session failure.
- **Unknown identifiers.** Any function, variable, or type introduced in the diff that does not exist in the codebase is a hard stop. `grep -r "name" .` before approving.
- **Dead-code deletion without proof.** "Zero callers / unused" must be checked across the whole repo (entrypoints, docs, tests, generated dispatch, CI, dynamic lookups) before deleting.
- **Injection, validation, credentials.** Injection at entry points; credentials hardcoded, logged, or committed.
- **Unexpected dependency changes.** New dependency or version bump not obviously required by the diff.
- **Generated-artifact drift.** Source changes that require regenerated/bundled outputs must include the regenerated output.

## Verification must run

Run the project's verification command this session and paste the output. If none exists, document `verification: none -- no command available` as a structural gap, not a pass. For a bug fix, a regression test that fails on the old code must exist before acceptance.

## Finding quality

Every reported finding cites file:line, the specific trigger, and why existing guards do not already prevent it. A clean acceptance is a valid acceptance; do not manufacture findings. When the diff and scope are larger than acceptance can responsibly cover, escalate to a full code review.
