# Refactor Scan

Pre-refactor reconnaissance. Run this before proposing a Refactor-mode plan to
ground the recommendation in evidence instead of gut feel.

## Procedure

1. **Explore walk.** Sweep the target area (module, directory, subsystem) with
   broad reads. Map: public surface, internal seams, dependency direction,
   file sizes, duplication hotspots.

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

## When to skip

If the refactor target is a single file or a well-understood seam, skip the
scan and go straight to Refactor mode. The scan earns its keep only when the
blast radius is unclear.
