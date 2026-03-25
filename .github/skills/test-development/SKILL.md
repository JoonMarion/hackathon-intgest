---
name: test-development
description: Specialized skill for writing tests in Personal Financie. Use for focused unit/integration tests and pragmatic test debugging during MVP delivery.
---

# Test Development Skill

This skill provides practical guidance for writing and debugging tests in Personal Financie.

## When to Use This Skill

- Creating model/form/service unit tests
- Writing integration tests for Django views and HTMX endpoints
- Debugging test failures
- Applying mocking only at external boundaries

## Project Constraints

- Prioritize mandatory MVP flow reliability
- Keep tests focused and readable
- Use `uv` workflow commands
- Avoid enterprise testing infrastructure unless explicitly requested

## Key Concepts

### Test Base Classes

| Class | Purpose | Client |
|-------|---------|--------|
| `SimpleTestCase` | Pure logic tests without DB access | N/A |
| `TestCase` | DB-backed unit/integration tests | `Client` |

### Test Organization

```
<app>/tests/
├── unit/
│   ├── test_models.py
│   ├── test_forms.py
│   └── services/
│       └── test_<service_name>.py
└── integrations/
  ├── test_http_views.py
  └── test_api_views.py
```

Rule: place unit tests only under `tests/unit/`, and integration tests only under `tests/integrations/`.

## Mocking Patterns

Use [Mocking Patterns Instructions](../../instructions/mocking-patterns.instructions.md).

Golden rules:
- Patch at import location
- Mock external boundaries, not core business logic
- Prefer real DB behavior in `TestCase` when practical

## Debugging Tips

> Start with the smallest failing test, fix, then expand.

### Step 1: Identify Test Type
- Pure logic without DB? → `SimpleTestCase`
- Needs model/query behavior? → `TestCase`
- Testing view/form/HTMX response? → `TestCase` + Django `Client`

### Step 2: Create Minimal Failing Test
```python
def test_creates_transaction_with_valid_data(self):
    response = self.client.post("/transactions/create/", data={...})
    self.assertEqual(response.status_code, 302)
```

### Step 3: Add Complexity Incrementally
```python
# Add validation edge cases
# Add balance/dashboard effect assertions
# Add HTMX partial-response assertions when applicable
```

## Running Tests

- Run all tests:
  - `uv run manage.py test`
- Run focused module tests:
  - `uv run manage.py test <app.tests.module>`

When operating in agent/subagent workflows, use `execute/runTests` as the primary path. If `execute/runTests` is temporarily unavailable, run `execute/runTask` with task label `sleep`, then retry the same `execute/runTests` invocation.

## Common Issues

### Issue: Validation errors not appearing
Check form assertions and expected error keys.

### Issue: Test response differs for HTMX requests
Send appropriate HTMX headers and assert partial template/fragment content.

### Issue: Money comparisons fail unexpectedly
Use `Decimal` in expected values, never `float`.

## Error → Solution Lookup

| Error / Symptom | Likely Cause | Fix |
|----------------|-------------|-----|
| `AssertionError` on balance totals | Expected value uses float math | Use `Decimal` for expected totals |
| View returns full page instead of fragment | Missing HTMX request headers | Add HTMX headers in test client request |
| `TransactionManagementError` | Mixing `TestCase` with manual `transaction.atomic` | Use `TransactionTestCase` or remove manual transactions |
| Mock has no effect | Patching wrong import path | Patch where the function is **used**, not where it's **defined** |

## Debugging Decision Tree

```
Test failing?
├── Import/Setup error?
│   ├── ModuleNotFoundError → Check import path and app config
│   └── ImproperlyConfigured → Validate settings used by the test runner
├── Assertion failure?
│   ├── Wrong status code?
│   │   ├── 403 → Check auth/session state and permissions
│   │   ├── 404 → Check URL path and kwargs
│   │   └── 500 → Check server logs, likely unhandled exception
│   ├── Wrong data?
│   │   ├── Empty response → Confirm setup data exists
│   │   ├── Wrong totals → Check Decimal quantization/rounding
│   │   └── Unexpected fragment → Verify HTMX headers and template path
│   └── Mock assertion wrong?
│       ├── Patch target may be incorrect
│       └── Boundary may be over-mocked
└── Test hangs/times out?
    ├── External call not mocked → Patch boundary call
    └── DB lock/transaction issue → simplify transaction usage in test
```

## Test Type Selection Guide

```
What are you testing?
├── Pure logic (no DB, no I/O) → SimpleTestCase
├── Model/form validation → TestCase
├── Service logic with DB reads/writes → TestCase
├── View or HTMX endpoint rendering → TestCase + Client
└── UI browser flow (optional/post-MVP) → dedicated E2E setup
```

## References

- [Testing Instructions](../../instructions/testing.instructions.md)
- [Mocking Patterns Instructions](../../instructions/mocking-patterns.instructions.md)
- [Testing Guide](../../../docs/testing-guide.md)
- [Mocking Guide](../../../docs/mocking-guide.md)
