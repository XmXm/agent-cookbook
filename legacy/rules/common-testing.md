# Common Testing

- Scale test effort to risk: prioritize core logic, regression-prone areas, and any bug you just fixed. Don't force tests on throwaway scripts or obvious code.
- Pick test types as needed (unit / integration / E2E) — not every change needs the full set.
- Coverage serves confidence, not a fixed percentage gate.
- For complex or error-prone logic, writing the test first (TDD) is encouraged, not mandatory.
- When a test fails, suspect the implementation before changing the test — unless the test itself is wrong.
