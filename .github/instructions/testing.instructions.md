---
name: "Testing Guidelines"
description: "Guidelines for writing and running tests in Personal Financie"
applyTo: "**/tests/**/*.py"
---

# Testing Guidelines (MVP)

## Status

**Active for MVP** with a lean strategy.

## Testing priorities

1. Manual smoke checks for mandatory flows
2. Focused automated tests for core behavior
3. Optional broader coverage only after MVP is stable

Manual smoke validation of mandatory features is an MVP acceptance gate.

## Command standard

Use `uv` commands only:

- `uv run manage.py test`
- `uv run manage.py test <app.tests.module>`

For agent/subagent workflows, prefer `execute/runTests` for test execution. If `execute/runTests` is temporarily unavailable, run `execute/runTask` with task label `sleep`, then retry the same `execute/runTests` invocation.

## Minimum automated coverage (recommended)

- Model validation for money/category/transaction constraints
- View tests for create/list/edit/delete flows
- Dashboard summary/balance calculation checks

## Keep tests proportional

- Do not block MVP delivery on enterprise-level test infrastructure.
- Avoid introducing heavy testing frameworks unless explicitly requested.
- Keep fixtures small and readable.

## References

- `docs/testing-guide.md`
- `docs/mocking-guide.md`
