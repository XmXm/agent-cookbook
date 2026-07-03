---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
---
# TypeScript/JavaScript Coding Style

> Extends [common-coding-style.md](./common-coding-style.md).

- Immutable updates via the spread operator (`{ ...user, name }`), not in-place mutation.
- Validate external input at boundaries with a schema library (e.g. Zod).
- No `console.log` in production code — use a proper logging library.
