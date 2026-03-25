---
name: "E2E Testing Guidelines"
description: "Guidelines for end-to-end browser testing in Personal Financie"
applyTo: "**/tests/e2e/**/*.py"
---

# E2E Testing (Optional)

## Status

**Optional for MVP**. Do not block mandatory feature delivery on E2E setup.

## When to use

Use E2E only if time allows after mandatory scope is stable.

## E2E rules for this project

- Keep scenarios short and focused on critical user flows.
- Prefer stable semantic selectors.
- Do not require enterprise navigator frameworks by default.
- Keep local execution simple and reproducible.

If executed, follow project command standards with `uv run`.

## Priority reminder

Manual smoke validation of mandatory features has priority over building a large E2E suite during hackathon execution.

## References

- `docs/testing-guide.md`
- `docs/features-frontend.md`
