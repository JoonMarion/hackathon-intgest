---
name: refactor-development
description: Shared refactoring workflow for Personal Financie. Use when updating existing code to current patterns while preserving behavior.
user-invocable: true
---

# Refactor Development Skill

Use this skill when a task requires rewriting existing code to align with Personal Financie patterns without changing functional behavior.

## When to Use

- Migrating legacy code to current architecture patterns
- Removing anti-patterns (direct model imports, business logic in views/tasks)
- Improving structure while keeping existing behavior and contracts
- Updating callers/import chains after symbol or module refactors

## Mandatory Reading

Before refactoring, review:
- [Code Architecture](../../instructions/code-architecture.instructions.md)
- [Dataclass Patterns](../../instructions/dataclass-patterns.instructions.md)
- [Testing Instructions](../../instructions/testing.instructions.md)
- [Architecture](../../../docs/architecture.md)
- Domain-specific docs for impacted areas (`features-backend`, `features-frontend`, `frontend-guide`)

## Core Principles

1. Preserve behavior: same inputs, outputs, side effects, and API contracts
2. Keep scope tight: refactor one module/group at a time
3. Verify continuously: run focused checks before and after each refactor batch
4. Prefer project-native patterns over introducing new abstractions

## Standard Workflow

1. **Understand contract**
   - Identify call sites, tests, and public interfaces
2. **Plan edits**
   - List files to touch and blast radius
3. **Apply refactor**
   - Keep changes incremental and reversible
4. **Update references**
   - Fix imports/usages for renamed/moved symbols
5. **Validate**
   - Run the most specific relevant checks/tests first, then broader checks

## Common Refactor Patterns

| Pattern | Before → After |
|---------|----------------|
| Fat views | business logic inside view methods → extract helper/service function |
| Dict-heavy data plumbing | `payload.get('x')` chains → typed dataclass with validation |
| Monetary float usage | float operations → `Decimal` operations with explicit quantization |
| Repeated template fragments | duplicated blocks → reusable Django partial/included template |
| Mixed responsibilities | validation + persistence + formatting in one function → split into clear steps |

## Validation Checklist

- [ ] No contract-breaking behavior change
- [ ] Relevant tests still pass
- [ ] Imports resolve without circular issues
- [ ] Decimal-safe monetary handling is preserved
- [ ] HTMX/template behavior remains compatible when views/templates changed
- [ ] Refactor scope stayed within requested boundaries

## Output Contract (for worker agents)

When using this skill in a worker subagent report:

```markdown
## Refactor Summary
- target_scope:
- patterns_applied:
- files_changed:
- validations_run:
- residual_risks:
```

## Project Notes

- Keep refactors proportional to MVP goals.
- Prefer clarity and maintainability over heavy abstractions.
- Use `uv run manage.py test <module>` or relevant focused checks after each refactor batch.
