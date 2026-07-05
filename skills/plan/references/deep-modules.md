# Deep Modules and Domain Vocabulary

Design **deep modules**: a lot of behaviour behind a small interface, at a clean seam, testable through that interface. Use this language wherever code is designed or restructured. Condensed from the `codebase-design`, `improve-codebase-architecture`, and `domain-modeling` references.

## Glossary (use these terms exactly)

Do not substitute "component", "service", "API", or "boundary".

- **Module** — anything with an interface and an implementation. Scale-agnostic: a function, class, package, or tier-spanning slice.
- **Interface** — everything a caller must know to use the module correctly: type signature plus invariants, ordering constraints, error modes, required config, and performance characteristics. Broader than "API" or "signature".
- **Implementation** — what is inside a module. Distinct from an adapter.
- **Depth** — leverage at the interface: how much behaviour a caller or test exercises per unit of interface they must learn. Deep = much behaviour behind a small interface. Shallow = interface nearly as complex as the implementation.
- **Seam** (Michael Feathers) — a place you can alter behaviour without editing in that place; where a module's interface lives. Where to put the seam is its own decision.
- **Adapter** — a concrete thing satisfying an interface at a seam. Describes role, not substance.
- **Leverage** — what callers get from depth: more capability per unit of interface. **Locality** — what maintainers get: change, bugs, and verification concentrate in one place.

## Principles

- **Depth is a property of the interface, not the implementation.** A deep module can be internally composed of small swappable parts that are not part of its interface.
- **The deletion test.** Imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it earned its keep.
- **The interface is the test surface.** Callers and tests cross the same seam. Wanting to test past the interface means the module is the wrong shape.
- **One adapter is a hypothetical seam; two adapters is a real one.** Do not introduce a seam unless something actually varies across it.

## Designing for testability

- Accept dependencies, do not create them inside the function.
- Return results, do not mutate via side effects.
- Small surface area: fewer methods and params = simpler tests.

## Finding deepening opportunities (refactor scan)

Walk the code and note friction rather than following rigid heuristics:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules shallow (interface nearly as complex as implementation)?
- Where were pure functions extracted just for testability, but the real bugs hide in how they are called (no locality)?
- Where do tightly-coupled modules leak across their seams?
- Which parts are untested or hard to test through their current interface?

Apply the deletion test to anything suspected shallow: would deleting it concentrate complexity, or just move it? "Concentrates" is the signal to deepen.

## Domain vocabulary (keep CONTEXT.md current)

When planning names a domain concept, keep the model sharp inline:

- **Challenge against the glossary.** A term conflicting with `CONTEXT.md` gets called out immediately.
- **Sharpen fuzzy language.** Propose a precise canonical term ("account" → Customer or User?).
- **Update `CONTEXT.md` the moment a term resolves.** Do not batch. `CONTEXT.md` is a glossary, free of implementation detail. Create it lazily if absent.
- **Offer an ADR sparingly** — only when the decision is hard to reverse, surprising without context, and the result of a real trade-off. If any of the three is missing, skip it.

## Rejected framings

- Depth as ratio of implementation-lines to interface-lines (rewards padding). Use depth-as-leverage.
- "Interface" as only the language `interface` keyword or public methods (too narrow).
- "Boundary" (overloaded with DDD's bounded context). Say seam or interface.
