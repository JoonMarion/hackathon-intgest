---
name: "Dataclass Patterns"
description: "Guidelines for dataclass usage in Personal Financie"
applyTo: "{**/dataclasses.py,**/services/**/*.py}"
---

# Dataclass Patterns (Lightweight)

## Status

**Partially active** for lightweight structured data use.

## Use dataclasses when

- You need a typed data carrier for service/form processing
- Validation in `__post_init__` improves clarity

## Rules

- Keep dataclasses small and explicit.
- Use `Decimal` for monetary values.
- Validate critical constraints in `__post_init__`.
- Prefer plain Django forms/models for core request handling unless dataclass usage is clearly beneficial.

## Do not introduce by default

- Enterprise base dataclass frameworks inherited from another project
- Extraction-engine-specific dataclass patterns
- External API response modeling frameworks for MVP

## References

- `docs/models.md`
- `docs/features-backend.md`
