# Mocking Guide

Use mocking to isolate units and avoid brittle tests.

## When to mock

- Time-dependent logic
- External calls (if any are introduced later)
- Expensive or non-deterministic operations

## Common patterns

- Patch functions where they are imported.
- Keep mock return values explicit and minimal.
- Assert behavior (calls/arguments), not internal implementation.

## Example checklist for mocked tests

- Arrange deterministic input and mock outputs.
- Act on one unit under test.
- Assert result + expected mock interactions.

## Anti-patterns

- Over-mocking simple pure logic.
- Mocking objects you don’t need to isolate.
- Creating opaque, reusable mocks without clear intent.