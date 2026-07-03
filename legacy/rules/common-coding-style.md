# Common Coding Style

- Prefer immutable updates: return new objects instead of mutating in place. This is a default leaning, not an absolute — language-specific rules may override it (e.g. idiomatic in-place mutation for Go/C# structs and hot-path performance code).
- Prefer many small, cohesive files organized by feature/domain over a few large ones. No hard line-count limit.
