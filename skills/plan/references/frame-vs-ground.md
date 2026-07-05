# 格局 vs 苟: Altitude and Grounding

Two opposite failure modes a plan can fall into, and the move that fixes each. Distilled from the `geju` (格局, opens the frame) and `goudi` (苟帝, grounds it) pair in the read-only `refs/hai-stack` source.

They are not opposites applied to the same decision. **Open the 格局 on the target; 苟 on the first move.** Set the direction high (do not let compatibility or refactor fear shrink it), then compress the first step to the smallest thing that proves the direction.

## Diagnose first: which failure mode?

| Symptom | Move | The proposal is |
|---|---|---|
| Too timid, patchy, compatibility-worshipping (太碎 / 太怂 / 别动旧的) | 打开格局 (open the frame) | under-reaching — patching around the wrong target model |
| Vision-heavy, no first step (愿景多落地少 / 太飘 / 太理想化) | 苟 (ground it) | over-reaching — ambition with no move that survives contact with reality |
| Grand target and also scared to delete | 格局 then 苟 | both — open the target, then ground the first move |

When unsure, open the 格局 on the target, then 苟 the first move. A good plan usually does both.

## 打开格局 — open the frame

Recommend the right target model, not the smallest patch. 大胆假设，小心求证. Refactor difficulty, compatibility fear, and existing shape are constraints to price, not masters to obey.

Real-vs-not-real constraint test (the operational heart):

- **Real**: public API, persisted data, documented integration, user promise, deployment/compliance constraint, explicit user instruction.
- **Not enough to bend the direction**: internal callers, stale naming, old layout, a partial existing implementation, "this will be a big diff."

Moves (use at least one when the discussion is stuck in local optimization):

- **End-state backcasting** — if this were excellent in six months, what is true? Work back from there, not from today's layout.
- **Zero-legacy** — if we started today with no old callers, what would we build? Compare; it exposes inertia vs real compatibility.
- **Kill the wrong concept** — delete concepts that encode the wrong model: duplicate names for one lifecycle, transitional wrappers with no contract, Manager/Service/Context blobs, plan phases that exist only because the doc already has them.
- **10x question** — what obviously breaks at 10x usage, teams, or surface? Reveals the weak axis.
- **Constraint inversion** — what if this constraint were removed? Then decide whether it deserves to survive.
- **Non-negotiable principles** — name 2-4 the design must not violate before discussing implementation.
- **Tasteful deletion** — deletion is a design act; do not hide it behind "simplify later."

What to fight: compatibility worship, local-detail trap, refactor fear, mild-answer bias. Lead with the sharp thesis, label it a hypothesis when evidence is thin, and name the first proof point and the falsifier. Do not flatten the call into a balanced non-answer.

## 苟 — ground it

先把路踩实，再谈大胜利. Keep the bold target; compress the first step, not the ambition. Not timid and not anti-refactor — it rejects fantasy migrations, not clean targets, and the default is a smaller proof, not standing still.

Reality check — scan for five anti-patterns:

- **Vision without first step** — sounds right, nobody knows what to do this afternoon.
- **Fake migration plan** — clean target, but the path assumes everything changes at once.
- **Unpriced risk** — "we can refactor" with no cost on data loss, blast radius, missing tests, or hidden callers.
- **Long-term correct, short-term irresponsible** — the full thing now starves the current goal.
- **No stop rule** — the plan can only continue; it cannot fail gracefully.

Then produce:

- **Minimum viable move** — one narrow vertical slice or proof point. State what it changes and what it refuses to change. Prefer something that creates evidence, not more planning.
- **Cut list** — what the first move must NOT attempt: compatibility work with no real contract, polish that does not affect the proof point, broad migration before the slice is proven.
- **Verification** — observable success criteria plus named failure signals, cheap enough to run before confidence decays.
- **Stop rule** — what evidence kills or pauses the direction, what can be rolled back or isolated, what decision to defer.
- **Landing verdict** — go / shrink / pause / reject / validate-first; lead with it.

## How this composes with the simplicity ladder

The simplicity ladder ([lazy-ladder.md](lazy-ladder.md)) is the build-size reflex: the smallest code that works. 格局/苟 is the altitude judgment one level up — 格局 picks the target direction, 苟 picks the first move that proves it. Open the frame on what to build toward; apply the ladder and the cut list to what to build first.
