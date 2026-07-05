# Evaluation: Kill / Keep / Pivot

For judging whether something should exist, be kept, exposed, or removed. Condensed from the `think` evaluation mode.

State the evaluation target and what kind of judgment is needed (value, risk, or tradeoff). Snapshot current state first: what it does, who uses it, what depends on it. Grep and read before opining.

For product pivot, commercialization, or business-direction asks, frame market, user, distribution, willingness-to-pay, and maintenance burden before proposing technology. Do not assume open source, do not assume implementation comes first, and do not hide a business judgment inside a technical plan.

## Output format

Line 1: one of **Kill** / **Keep** / **Pivot** as the verdict. No preamble.

Then three reasons grounded in the user's actual constraints (time, motivation, business model, maintenance cost), not generic tradeoffs.

- **Pivot**: list specific directions, one per line, each actionable.
- **Kill or major rework**: list impact scope (files, dependents, migration cost) before asking for confirmation.

Do not use a build-plan template here. Do not list options. Give one verdict.

## Triage variant (bundle of asks)

Activate when the input contains 3+ distinct items that could each be accepted or rejected independently: "看看这几个需求", an issue carrying multiple requests, a batch of screenshots. Do not treat the bundle as a to-do list. Classify each item first:

| Bucket | Meaning | Action |
|---|---|---|
| **Bug** | Broken behavior with evidence | Route to fix (`/hunt` if the root cause is unknown) |
| **Already works** | The feature exists but the reporter missed it | Point to the existing affordance |
| **Accepted improvement** | Genuine gap, low-risk, aligns with direction | Plan it |
| **Cosmetic / preference** | Subjective, no functional impact | Note it; act only if the owner agrees |
| **Out of scope** | Conflicts with the product boundary or adds unjustified complexity | Decline with one sentence |

Output the classification table first, then wait for the user to confirm the accepted subset before any work. "Already works" misidentified as missing is the most common waste — grep for the existing affordance before classifying an item as a gap.

## Commercial readiness gate

When the judgment is whether a product, paid feature, launch, or version is chargeable, evaluate chargeability before implementation. Check: delivery and update path, first-run activation/onboarding, payment/license/trial boundary, privacy and network promises, headline-feature reliability and honest degradation, support/refund triggers, competitor wedge, and solo-maintainer maintenance burden.

A product is not ready to charge because the happy path works locally. Missing distribution, update, licensing, privacy disclosure, or headline-feature reliability is a Keep-building or Pivot blocker.

## Negative-user feedback is not automatic scope

When the evaluation is triggered by a refund customer, a churn report, or a "competitor X is more intuitive" comparison, do not convert the complaint into a rework plan by default. First check whether the current behavior is intentional product differentiation. Read the project's own `AGENTS.md` / `CLAUDE.md` / product notes for phrases like "review-first", "verifiability over speed", "evidence-driven", "explicit confirmation". If the criticized behavior is named there as a deliberate choice, the verdict is **Keep**, with one sentence on why the differentiation matters and a note that the maintainer can override. Do not write a "fix the friction" plan that quietly removes the differentiator.
