# Docs Index

This folder was reformulated for the hackathon scope of this repository.

## Source of truth

When there is any conflict between documents, use this precedence:

1. `RULES.md` (event constraints and mandatory deliverables)
2. `PRODUCT.md` (product scope and MVP requirements)
3. Active docs in this folder

## Active docs (use now)

- `QUICKSTART.md` — fastest path to run the project locally
- `development-setup.md` — local environment and day-to-day setup
- `architecture.md` — simplified project architecture for this app
- `models.md` — data model and entity relationships for MVP
- `features-backend.md` — backend feature behavior and validation rules
- `features-frontend.md` — frontend flows and template expectations
- `frontend-guide.md` — practical template and UI conventions
- `testing-guide.md` — lean testing strategy for MVP
- `mocking-guide.md` — generic mocking patterns for tests
- `development-guide.md` — common implementation tasks
- `ai-assisted-workflow.md` — Copilot-assisted workflow and evidence checklist

## Legacy docs (reference only)

The files below were inherited from another larger project and are not primary guidance for this hackathon MVP:

- `code-patterns.md`
- `dataclass-guide.md`
- `extraction-guide.md`
- `migration-guide.md`
- `subagent-examples.md`

Use legacy docs only if a concrete task explicitly requires them.

## Scope guardrails

- Keep docs aligned with local-first execution.
- Do not reintroduce mandatory external infra requirements.
- Prioritize mandatory MVP features before optional differentials.
- Frontend implementation uses HTMX + Django template partials (Django 6).
- Python tooling and project commands use `uv` workflows.