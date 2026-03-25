---
name: "Test Mocking Patterns"
description: "Guidelines for mocking in unit and integration tests in Personal Financie"
applyTo: "**/tests/**/*.py"
---

# Mocking Patterns (MVP)

## Status

**Active for MVP** with generic Python/Django mocking only.

## Use mocking for

- Time-dependent behavior
- Optional external boundaries (if introduced)
- Non-deterministic operations

## Core rules

1. Patch at import location.
2. Mock boundaries, not internal business logic by default.
3. Keep mocks minimal and explicit.
4. Prefer real DB behavior in integration tests where practical.

Example:

```python
from unittest.mock import patch

@patch("app.services.reports.now")
def test_summary_uses_fixed_time(mock_now):
	mock_now.return_value = "2026-03-24"
	...
```

## Avoid

- Redis/Textract/FakeStore/JWT enterprise patterns from inherited projects
- Over-mocking simple deterministic logic

## References

- `docs/mocking-guide.md`
- `docs/testing-guide.md`
