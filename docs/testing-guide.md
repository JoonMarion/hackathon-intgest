# Testing Guide

This guide defines a lean testing approach for the hackathon MVP.

## Testing priorities

1. Mandatory flow reliability (manual smoke checks)
2. Core unit/integration tests for critical behavior
3. Optional broader coverage only after MVP is stable

## Minimum recommended automated tests

- Model validations for transaction/category data
- View tests for create/edit/delete/list flows
- Dashboard summary calculation test

## Run tests

```bash
$ uv run manage.py test
```

Run one module:

```bash
$ uv run manage.py test <app_name>.tests
```

## Manual smoke checklist (before demo)

- Create income and expense entries
- Edit one entry and verify persistence
- Delete one entry and verify removal
- Confirm updated balance on dashboard
- Confirm category assignment works

## Scope notes

- E2E suites are optional for this phase.
- Do not block MVP delivery on advanced test infrastructure.

## Playwright E2E (implemented)

The project now includes browser E2E coverage with Playwright in:

- `apps/core/tests/e2e/` (modular files by domain)

Run only E2E tests:

```bash
$ uv run pytest apps/core/tests/e2e -q
```

Run one scenario:

```bash
$ uv run pytest apps/core/tests/e2e/test_auth_navigation_flows.py -k login -q
```

### Selector contract

- Use only `data-e2e-selector` for interactions.
- Avoid CSS class selectors and brittle DOM chains.
- Keep textual assertions only for visible business outcomes.

### Practical best practices (Playwright + Cypress)

- Keep each test isolated and independent.
- Seed deterministic data per test; do not depend on previous tests.
- Prefer web-first assertions and locator retries instead of fixed sleeps.
- Keep scenarios focused on user-visible behavior.
- Test only systems we control; avoid third-party UI dependencies.
- Use clear setup in `setUp`/`beforeEach` and avoid cleanup in `afterEach` when not required.

For detailed guidance and Copilot prompt patterns, see `docs/e2e-playwright-guide.md`.