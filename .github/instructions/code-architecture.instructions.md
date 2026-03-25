---
name: "Code Architecture and Best Practices"
description: "Guidelines for code organization and Python best practices in Personal Financie"
applyTo: "{**/models.py,**/models/**/*.py,**/views.py,**/forms.py,**/urls.py,**/http/**/*.py,**/api/**/*.py,**/services.py,**/services/**/*.py,**/utils/**/*.py,**/management/commands/**/*.py}"
---

# Personal Financie Code Architecture

Use this file as the global baseline for Python code in this repository.

## Source of truth precedence

When instructions conflict, follow:

1. `RULES.md`
2. `PRODUCT.md`
3. Active docs listed in `docs/README.md`

## Project constraints

- Python version: **3.13**
- Runtime: local-first with SQLite
- No Docker/containerization
- No critical dependency on complex external infrastructure
- Mandatory MVP features first, optional features later

## Tooling

Use `uv` exclusively:

- `uv init -p 3.13`
- `uv sync`
- `uv add <package-name>`
- `uv run manage.py <command>`

Do not suggest `pip` or manual venv workflows.

## Architecture style

- Prefer simple Django patterns over heavy framework abstractions.
- Services are optional in MVP; extract only when it improves readability/testability.
- Keep implementation explicit and easy to reason about.

## Canonical app structure

- Use package-first app layout under `apps/<app_name>/` with `models/` and `http/` as the default MVP structure.
- APIs are disallowed in this hackathon MVP (`PRODUCT.md`); do not create `api/` packages or API endpoints.
- Keep API-related applyTo coverage as inherited compatibility metadata only.
- Split tests under `apps/<app_name>/tests/unit/` and `apps/<app_name>/tests/integrations/`.
- Keep templates app-local using duck pattern under `apps/<app_name>/templates/<app_name>/...`.
- Do not treat flat modules (`views.py`, `urls.py`, `tests.py`) as the primary structure for new scaffolding.

## Import flow

Prefer one-way dependencies:

```
utils → services (optional) → models/forms → http/views → http/urls
```

## Type hints

- Use type hints where practical for parameters/returns.
- Use modern Python typing syntax supported by Python 3.13.
- Use `Decimal` for money-related function signatures.

## Financial data safety

- Never use `float` for persisted monetary values.
- Use `DecimalField` in models and `Decimal` in Python logic.

## Model-layer conventions

- Keep shared `Kind` enums in `config/models/choices.py`.
- Keep shared abstract `BaseModel` in `config/models/base.py` with `created_at` and `updated_at`.
- Use `config/models/__init__.py` as the canonical import surface for shared model primitives.
- Require explicit `class Meta` in all domain models.
- Keep model guidance aligned with project stack: Django 6, Python 3.13, and `uv`.

## Frontend integration awareness

Backend code must remain compatible with:

- HTMX-driven interactions
- Django 6 template partial rendering

References:

- `docs/features-backend.md`
- `docs/features-frontend.md`
- `docs/frontend-guide.md`

## Testing expectations

- Prioritize mandatory flow reliability.
- Keep tests focused and proportional to MVP scope.
- Ensure local run path remains functional after changes.

## Do not introduce by default

- Multi-tenant architecture
- Redis/Celery requirements
- Enterprise SSO frameworks
- External API integration complexity
- Enterprise custom CRUD frameworks
