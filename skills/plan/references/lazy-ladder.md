# Simplicity Ladder

The best code is the code never written. Lazy means efficient, not careless. Apply this at every scope decision in a plan: the smallest rung that holds is the default. Adapted from [ponytail](https://github.com/DietrichGebert/ponytail) (MIT) and the retired `lazy` skill.

## The Ladder

Stop at the first rung that holds. Two rungs work, take the higher one and move on.

1. **Does this need to exist at all?** Speculative need = skip it, say so in one line. (YAGNI)
2. **Stdlib does it?** Use it.
3. **Native platform feature covers it?** `<input type="date">` over a picker lib, CSS over JS, a DB constraint over app code.
4. **Already-installed dependency solves it?** Use it. Never add a new dependency for what a few lines can do.
5. **Can it be one line?** One line.
6. **Only then:** the minimum code that works.

The ladder is a reflex, not a research project. The first lazy solution that works is the right one.

## Rules

- No unrequested abstractions: no interface with one implementation, no factory for one product, no config for a value that never changes.
- No boilerplate or scaffolding "for later". Later can scaffold for itself.
- Deletion over addition. Boring over clever. Fewest files, shortest working diff.
- Two stdlib options of the same size? Take the one correct on edge cases. Lazy means less code, not the flimsier algorithm.
- Mark deliberate simplifications with a `lazy:` comment so the shortcut reads as intent. If it has a known ceiling, name it and the upgrade path: `# lazy: global lock, per-account locks if throughput matters`.

## Intensity

| Level | Behavior |
|---|---|
| lite | Build what's asked, name the lazier alternative in one line. User picks. |
| full (default) | The ladder enforced. Stdlib/native first. Shortest diff, shortest explanation. |
| ultra | YAGNI extremist. Deletion before addition. Ship the one-liner, challenge the rest of the requirement in the same breath. |

## When NOT to be lazy

Never simplify away: input validation at trust boundaries, error handling that prevents data loss, security, accessibility basics, or anything explicitly requested. If the user insists on the full version, build it without re-arguing. Hardware and the physical world are never the ideal spec: a clock drifts, a sensor reads off. Leave the calibration knob, not just less code.

Non-trivial logic (a branch, loop, parser, money/security path) leaves ONE runnable check behind: the smallest thing that fails if the logic breaks. Trivial one-liners need no test.
