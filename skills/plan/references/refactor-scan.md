# Refactor Scan

Pre-refactor reconnaissance. Run this before proposing a Refactor-mode plan to
ground the recommendation in evidence instead of gut feel.

## Procedure

1. **Explore walk.** Sweep the target area (module, directory, subsystem) with
   broad reads. Map: public surface, internal seams, dependency direction,
   file sizes, duplication hotspots. Apply the smell lenses below while
   walking. Probe fix churn (distilled from Waza `/health`):
   `git log --oneline --since='90 days ago' -- <area> | grep -iE 'fix|修复'`,
   grouped by module — 3+ fix commits converging on one area signal a missing
   structural invariant (each fix is a guess at a rule that was never written
   down). That area enters the candidate list, typically at High strength: it
   removes a known bug class. Write down the invariant those fixes were
   converging toward.

2. **Deletion test.** For every abstraction or indirection you consider
   introducing, ask: "If I delete this, does complexity move or disappear?"
   If it only moves, the abstraction earns nothing — cut it from the proposal.

3. **Candidate list.** Produce a markdown table:

   | File / Seam | Problem | Proposed Change | Strength |
   |---|---|---|---|
   | `path/to/file.cs` | 800-line god class, 4 concerns | Split into X, Y, Z | High — 3 callers benefit |
   | ... | ... | ... | Medium / Low |

   Strength levels:
   - **High** — multiple callers benefit, removes a known bug class, or
     unblocks a pending feature.
   - **Medium** — improves readability or testability; no immediate external
     pressure.
   - **Low** — cosmetic or speculative; defer unless bundled with a High item.

4. **Output.** The candidate list feeds the Refactor mode's plan. Do not
   generate an HTML report — markdown is the format.

## Smell lenses

Condensed from the APoSD red-flags catalog (Ousterhout's 14) in the read-only
`refs/hai-stack` source (`hai-architecture/references/red-flags.md`). Apply
during the Explore walk. A lens hit is not yet a finding: it still needs the
deletion test and a file:line citation. Information leakage is the most
damaging — prioritize it. SSOT violations (the same fact owned in two places)
cluster at boundaries the type system cannot reach — language↔DB, layer↔layer,
language↔wire — sweep those first (from `hai-ssot`).

| Red flag | Tell | Legitimate exception |
|---|---|---|
| Shallow module | exported surface ≈ internal logic; wrapper that only renames | protocol translators (HTTP handlers, DTOs, adapters) are inherently shallow |
| Information leakage | two modules know the same format/protocol internals; change one, must change the other | — |
| Temporal decomposition | modules named after phases (reader/processor/writer) sharing one structure's internals | — |
| Overexposure | params or options most callers zero out | — |
| Pass-through method | forwards with a same-shape signature, adds nothing; pure-delegation middle layer | protocol translation is pass-through by nature |
| Repetition | the same decision/algorithm encoded in several places | three similar lines is coincidence, not repetition |
| Special-general mixture | caller-specific branches inside a generic-named module | — |
| Conjoined methods | A sets state B silently depends on; undocumented required call order | — |
| Comment repeats code / docs leak implementation | comment deletable with zero loss; API docs change when only the implementation changed | — |
| Vague name | data/info/result/manager/helper/util; one name, several concepts | — |
| Hard to pick / hard to describe | the honest name needs "and"; doc comment longer than the body | — |
| Nonobvious code | cause and effect far apart; unexplained casts; clever over readable | — |

## Wide refactors: expand–contract

Distilled from mattpocock-skills `to-tickets`. A wide refactor is one
mechanical change — rename a shared symbol, retype a column, move a seam —
whose blast radius fans across the codebase, so no single edit can land
green. Do not plan it as one phase. Shape it as:

1. **Expand** — add the new form beside the old; nothing breaks. A dual-track
   feature flag is a common carrier for this stage.
2. **Migrate** — move call sites in batches sized by blast radius (per
   package, per directory); each batch independently mergeable, CI green
   throughout because the old form still exists.
3. **Contract** — delete the old form once no caller remains (prove it with a
   repo-wide grep), as its own final phase.

This is the standard way a wide refactor satisfies the "every phase
independently mergeable" hard rule. While both tracks coexist, verify both:
flag off must preserve old behavior, flag on must pass the same checks.

## When to skip

If the refactor target is a single file or a well-understood seam, skip the
scan and go straight to Refactor mode. The scan earns its keep only when the
blast radius is unclear.
