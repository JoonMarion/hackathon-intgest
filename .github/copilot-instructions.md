# Personal Financie Copilot Instructions

Personal Financie is a hackathon-focused Django application for personal finance management.

Primary objective: deliver and demonstrate a reliable local MVP aligned with `RULES.md` and `PRODUCT.md`.

## Project Scope and Priorities

- This is a **local-first hackathon project**.
- Mandatory MVP scope comes from `RULES.md` and `PRODUCT.md`.
- Prioritize mandatory features before optional enhancements.
- Do not introduce unnecessary enterprise-level complexity.

## Tech Stack

- Python **3.13**
- Django **6** (use Django 6-compatible patterns, including template partials)
- SQLite
- HTMX for frontend interactions
- GitHub Copilot for AI-assisted development

## Tooling Rules (uv)

Use `uv` for environment, dependency, and command execution:

- Initialize project Python: `uv init -p 3.13`
- Sync dependencies: `uv sync`
- Add dependencies: `uv add <package-name>`
- Run project commands with `uv run`:
  - `uv run manage.py <command>`
  - `uv run <project-installed-cli>`

Use `uv` exclusively in project guidance. Do not suggest `pip` or manual venv workflows.

## Execution and Task Policy

- For agent/subagent workflows, do not use or request `runInTerminal`, except in `Django App Builder` where terminal usage is explicitly allowed with strict guardrails.
- Prefer validated agent tools for checks/tests (`pylance-mcp-server/*`, `execute/runTests`, `execute/testFailure`) and VS Code tasks for command-based flows.
- In agent/subagent workflows, run tests through `execute/runTests` as the primary path.
- If `execute/runTests` is temporarily unavailable (for example during MCP refresh), run `execute/runTask` with task label `sleep`, then retry the same `execute/runTests` invocation.
- Prefer VS Code tasks for recurring Django command operations (check, makemigrations, migrate) to keep execution predictable.
- Keep `uv run manage.py <command>` as the canonical command form behind tasks and documentation.

## Frontend Rules

- Use HTMX for server-driven interactivity and partial updates.
- Use Django template inheritance and template partials for reusable fragments.
- Prefer progressive enhancement over SPA patterns for MVP.

## Static Asset Conventions

- Root `static/` is for global shared assets used across the whole application (including `static/libs/...`).
- Use `apps/<app_name>/static/<app_name>/...` for assets specific to a single app.
- In templates, always use `{% static %}` with the correct path.
- Avoid placing app-specific files in root `static/`.

## Infrastructure Constraints

- Keep the app runnable locally for presentation.
- Do not use Docker or any containerization in this project.
- Do not introduce critical dependencies on complex external infrastructure.
- Do not implement or depend on external API integrations for MVP unless explicitly requested by the user.

## Documentation Source of Truth

When instructions conflict, follow this order:

1. `RULES.md`
2. `PRODUCT.md`
3. Active docs indexed in `docs/README.md`

Use active docs in `docs/` as secondary references after `RULES.md` and `PRODUCT.md`. Treat legacy/inherited docs as reference-only.

## Project Documentation

For detailed implementation patterns, consult active docs listed in `docs/README.md`.
Prefer guidance from `docs/development-setup.md`, `docs/features-backend.md`, `docs/features-frontend.md`, and `docs/testing-guide.md` for day-to-day implementation decisions.

## Workflow Preferences

- Use subagents for read-only investigation/research to keep implementation context clean.
- Ask for clarification when requirements are ambiguous.
- Keep changes focused and minimal; avoid scope drift.

## Agent Orchestration

For multi-phase work (e.g., models + views + templates + tests), use the **Feature Builder** agent as the primary orchestrator:

- `.github/agents/feature-builder.agent.md`

For small and isolated changes, direct implementation is acceptable.

## Coding Conventions (Project-Level)

- User-facing strings should be clear and consistent.
- Monetary values must use decimal-safe handling (avoid `float` for persisted money values).
- Keep forms and validation explicit and predictable.
- Favor readability and maintainability over framework-heavy abstractions.

## Model Layer Conventions

- Keep shared `Kind` enums in `config/models/choices.py`.
- Keep abstract shared `BaseModel` in `config/models/base.py` with `created_at` and `updated_at`.
- Use `config/models/__init__.py` as canonical import surface for shared model primitives.
- Require explicit `class Meta` in domain models.
- Maintain wording and implementation guidance consistent with Django 6, Python 3.13, and `uv`.

## Testing and Validation

- Prioritize smoke reliability of mandatory flows.
- Add focused tests for critical behavior where feasible.
- Ensure updates do not break local run/demo path.
- For multi-phase work, apply phase gates before handoff: touched tests pass, imports resolve, and local run path remains functional.
