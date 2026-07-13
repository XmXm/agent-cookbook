---
name: plan
description: "Take a position before any code: a quick 2-3 sentence stance on a small well-defined change (Lightweight), or a decision-complete plan — design and tradeoffs, opening the frame (格局, recommend the right target) vs grounding an over-ambitious idea (苟, a minimal verifiable first move), value judgment (Kill/Keep/Pivot) with multi-item triage, refactor planning, plan stress-testing, deep-module and domain vocabulary, lightweight acceptance against the approved plan, and persisting non-trivial plans (defaults to .plans/). A self-contained front door for code work; it decides and records the decision, it does not implement, debug, or review code."
when_to_use: "出方案, 给方案, 怎么设计, 用什么方案, 怎么弄合适, 哪种方式好, 快速判断怎么改, 判断一下, 值不值得, 要不要做, 有没有必要, 看看这几个需求, 重构怎么改, 重构方案, 帮我拷问这个计划, 验收一下, 打开格局, 格局太小, 站高一点, 别太保守, 太飘, 太理想化, 怎么落地, 先落地, 收一收, 苟一下, plan this, how should I design, what's the best approach, quick take, refactor plan, is this worth it, grill this plan, did we build what was asked, think bigger, make this real, what do I do first"
dispatch_intent: "New feature design, architecture, value judgment, refactor planning, plan stress-test, acceptance against an approved plan"
allowed-tools: "Read, Grep, Glob, Bash, WebFetch, WebSearch, Edit, Write"
---

<!-- Lightweight, Triage, and attack-angle sections adapted from Waza think
     (MIT, © 2026 Tw93); frame-vs-ground distilled from hai-stack; ladder from
     ponytail. Persistence contract lives in shared/plan-artifacts.md. -->

# Plan: Decide Before You Build

The front door for code work. Turn a rough idea into an approved plan, judge whether work should exist, plan a refactor, grill an existing plan, or accept finished work against the plan it promised. No code until the plan is approved.

State opinions directly. Take a position and name the evidence that would change it. Skip "that's interesting" and "there are many ways to think about this."

## Outcome Contract

- Outcome: a defensible position — a stance, verdict, or direction. When the work continues into code it becomes a decision-complete plan another engineer can execute without re-deciding; a plan file is a carrier for that decision, never the goal.
- Done when: Lightweight — what changes, where, why, and one risk are stated. Full modes — goal, scope and non-scope, chosen approach, rejected tradeoff, the most fragile assumption, tests, and rollback are concrete enough to act on. No `TBD`/`TODO`/"implement later".
- Evidence: current repo state (`pwd`, real config files, prior decisions/ADRs), live external docs when relevant, and explicit user constraints. Quote live values, never from memory.
- Output: one recommended direction (or one verdict), plus an execution-ready handoff when the work continues into code.

## Modes

Pick the mode that matches the ask. Each mode names what it may and may not do.

### Design (default)

For "build / design / how should I" asks. May: read code, study official solutions and mature competitors first, propose one recommended approach plus one close alternative, name the load-bearing assumption. Must not: write code, scaffold, or pseudo-code before approval.

Diagnose altitude before proposing (see [references/frame-vs-ground.md](references/frame-vs-ground.md)): if the proposal is too timid or patchy, open the 格局 and recommend the right target rather than the smallest patch; if it is vision-heavy with no first step, 苟 it into a minimal, verifiable first move with a cut list and a stop rule. Set the target high, ground the first move small.

Give one recommendation with effort, risk, and what existing code it builds on. Always include one minimal option. Apply the simplicity ladder ([references/lazy-ladder.md](references/lazy-ladder.md)) to every scope decision: the smallest thing that works is the default. When the design touches module shape, use the deep-module vocabulary ([references/deep-modules.md](references/deep-modules.md)) exactly. Before handing off, run the [references/handoff.md](references/handoff.md) checklist.

If requirements conflict — two contradicting sources, or two valid interpretations with different cost — name the specific conflict in one sentence and ask which takes precedence. Do not silently pick.

### Lightweight

For asks where the problem is already defined and the only open question is "how" — a small change, a method choice, a quick take. May: give one recommended change in 2-3 sentences — what changes, where (file:line if known), and why; name the brute-force version first and default to it unless the user wants elegance; state one risk; list involved files and flag if more than 5. Must not: expand into the full Design ritual, or absorb error/bug context (that routes to `/hunt`).

Upgrade to Design when 3+ genuinely different approaches with meaningful tradeoffs emerge. Boundary with `/lazy`: lazy constrains how small the implementation gets; Lightweight decides the stance on what to do.

### Evaluate

For "should this exist / is it worth it / 值不值得 / 要不要做" asks. May: snapshot current state (grep and read before opining), frame market/user/maintenance for product judgments. Must not: hide a business judgment inside a technical plan, or output a build-plan template.

Output a single **Kill / Keep / Pivot** verdict with reasons grounded in the user's real constraints. See [references/evaluation.md](references/evaluation.md) for the verdict format and the commercial-readiness gate.

For a bundle of 3+ independent items ("看看这几个需求", an issue carrying multiple requests), run the triage variant in [references/evaluation.md](references/evaluation.md): classify every item first, then wait for the user to confirm the accepted subset before any work.

### Refactor

For "how should I refactor / restructure this" asks. May: map the current seams, name the target deep module, define the verification that proves behavior is preserved, and the rollback. Must not: start editing code, or restructure without a behavior-preserving check.

A refactor plan changes shape, not behavior. When the blast radius is unclear, run a [references/refactor-scan.md](references/refactor-scan.md) first (Explore walk → deletion test → candidate list). State which seam moves and what stays identical, then hand off via [references/handoff.md](references/handoff.md). Use [references/deep-modules.md](references/deep-modules.md) for the target shape; apply the deletion test before proposing a new seam.

### Grill

For "stress-test / 拷问 this plan" asks. Interview the user one question at a time, walking each branch of the design tree and resolving dependencies between decisions. For every question, give your recommended answer. Asking several questions at once is forbidden. If a question can be answered by reading the codebase, read the codebase instead.

### Review (lightweight acceptance)

For "did we build what was asked / 验收一下" after implementation. May: compare the diff against the approved plan and label **on target / drift / incomplete**, run the project's verification command, and check the hard-stop subset in [references/review-gate.md](references/review-gate.md). Must not: substitute for a full diff/release review. Heavy diff review, release gates, and project audits are out of scope for this mode.

## Persist the Plan

The persistence contract lives in `shared/plan-artifacts.md`: when a plan file
earns its keep, the `.plans/<NNN>-<slug>/` layout, the roles of `task_plan.md`
/ `findings.md` / `research/` / `progress.md`, and the anti-bloat discipline.
In short: persist only when the work is multi-phase, 3+ steps, or spans
sessions — or when the user asks. A lightweight plan stays in the conversation;
the file is a carrier for the decision, never the goal. When the plan came from
fan-out research or will be executed outside this session, also persist the
full research reports to `research/` and write the Execution Playbook section
(orchestration discipline, copy-pasteable gates, context entry points), then
run the detached-execution self-check in [references/handoff.md](references/handoff.md).
During execution, `/check` Plan Execution updates `progress.md` against the
same contract; Review mode reads it back for acceptance.

## Knowledge Preflight

Before drafting a Design or Refactor recommendation, run the preflight defined
in `shared/knowledge-preflight.md`: search nmem for prior decisions on the
topic, and search the project KB (per `shared/project-routing.md`, if mounted
and the current work is within its declared Scope) for relevant patterns or
anti-patterns in the affected subsystem. If either source is unavailable or
out of scope, state so and proceed — preflight is non-blocking.

## Hard Rules

- **No code before approval.** Design, Lightweight, Evaluate, and Refactor modes produce a stance, plan, or verdict only. Implementation starts when the user says "implement", "可以干", "直接改", or equivalent.
- **No placeholders in an approved plan.** `TBD`, `TODO`, "implement later", "similar to step N", "details to be determined" mean the plan is not ready. Fill it or stop.
- **Confirm the path first.** Run `pwd` / `git rev-parse --show-toplevel` before any filesystem operation. Never assume `~/project` and `~/www/project` are the same.
- **The baseline branch is immovable.** The main checkout stays on the branch it was on when the plan was approved (the baseline, e.g. `dev`) for the whole life of the plan. Never `git switch` / `git checkout -b` the main checkout onto a feature branch — a parallel session merging into the baseline will silently land its commits on the wrong branch. Any work that needs a different branch happens inside a dedicated worktree.
- **Worktrees exist only for true parallelism.** Non-concurrent (single-track) execution develops and commits directly on the current branch of the main checkout — no new branch, no new worktree. Create worktrees only when 2+ phases/tasks genuinely run at the same time; merge them back serially on the baseline branch.
- **Live values only.** Open the actual config file for any default, env var, or field. Never quote a default from memory or docs.
- **Separate target altitude from first-move size.** Open the 格局 on the target (do not let compatibility or refactor fear shrink the direction); 苟 the first move (smallest verifiable slice, cut list, stop rule). They apply to different layers, not the same decision — see [references/frame-vs-ground.md](references/frame-vs-ground.md).
- **Name the premise collapse.** State the most fragile load-bearing assumption: "This plan assumes X. If X fails, Y happens." Deform the design to survive it, or disclose that it does not.
- **Surface rule conflicts.** If the plan contradicts a "never X / must Y / hard rule" in `AGENTS.md` / `CLAUDE.md` or other project-level instructions, name the contradiction and stop; do not silently override.
- **Phase independence.** Each phase must be independently mergeable. A "Phase 0: investigate" or a phase that only works once the next one lands means the plan is not ready.

## Scope

`plan` is self-contained: it produces the plan and can write it to disk itself when the work warrants it (see Persist the Plan). It stops at an approved plan — it does not implement code, debug runtime failures, run a full diff or release review, or polish prose. When planning names a new domain concept, update `CONTEXT.md` inline (see the domain section in [references/deep-modules.md](references/deep-modules.md)).

## Gotchas

| What happened | Rule |
|---|---|
| Moved files to `~/project`, repo was at `~/www/project` | `pwd` before the first filesystem op |
| Asked for an API key after 3 implementation steps | List every credential/dependency in the handoff before approval |
| "判断一下这个报错" routed to Evaluate | Error/bug context is debugging, not planning. Evaluate is value/existence judgment only |
| Rejected design restarted from scratch | Ask what specifically failed; re-enter with narrowed constraints |
| Approved plan got re-debated | Execute it. Stop only for repo drift, missing permissions, or unsafe external state |
| Introduced a second language/runtime silently | Never add a new language or runtime without explicit approval |
| Built a shallow pass-through "for structure" | Apply the deletion test: if deleting it just moves complexity, it earns nothing |
| Small defined ask got the full design ritual | Problem defined + only "how" open = Lightweight: a 2-3 sentence stance |
| Parallel session switched the main checkout to its feature branch; another session's `merge into dev` landed on that branch instead | Baseline branch is immovable; feature branches are checked out only inside worktrees |
| Single-track plan spawned a worktree + branch for no concurrency | Worktrees only for true parallelism; otherwise develop directly on the current branch |

## Output

**Approved design:**
- **Building**: what this is (1 paragraph)
- **Not building**: explicit out-of-scope list
- **Approach**: chosen option with rationale (+ one close alternative only if >40% likely preferred)
- **Key decisions**: 3-5 with reasoning
- **Premise collapse**: the most fragile assumption + what happens if it fails
- **Handoff**: file targets, verification commands, rollback (when work continues into code)

**Lightweight:** 2-3 sentences — what changes, where, why — plus the brute-force default and one risk. No template.

**Evaluate:** one `Kill` / `Keep` / `Pivot` verdict + three reasons. No options list.

After approval, stop. Persist the plan to a directory only when the work is non-trivial or the user asks (see Persist the Plan); a lightweight plan stays in the conversation. Implementation starts when the user says so; afterward, use Review mode for acceptance.
