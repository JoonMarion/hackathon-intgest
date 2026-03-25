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