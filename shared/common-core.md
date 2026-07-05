# Common Core

Coding style, security, and testing baseline shared across skills.

## Coding Style

- Prefer immutable updates: return new objects instead of mutating in place.
  Language-specific overrides apply (e.g. idiomatic in-place mutation for Go/C#
  structs and hot-path performance code).
- Prefer many small, cohesive files organized by feature/domain over a few large
  ones. No hard line-count limit.

## Security

- Never hardcode secrets (API keys, passwords, tokens). Use environment
  variables or a secret manager; validate they exist at startup; rotate anything
  that may have leaked.
- Don't trust external data (user input, API responses, file content) — validate
  at system boundaries.
- Prevent injection: parameterized queries for SQL, escape/sanitize for XSS.
  Apply auth/authorization based on each surface's sensitivity.
- Error messages must not leak sensitive data.

## Testing

- Scale test effort to risk: prioritize core logic, regression-prone areas, and
  any bug just fixed. Don't force tests on throwaway scripts or obvious code.
- Pick test types as needed (unit / integration / E2E) — not every change needs
  the full set.
- Coverage serves confidence, not a fixed percentage gate.
- For complex or error-prone logic, writing the test first (TDD) is encouraged,
  not mandatory.
- When a test fails, suspect the implementation before changing the test —
  unless the test itself is wrong.
