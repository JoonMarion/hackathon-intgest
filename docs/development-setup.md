# Development Setup

This setup is intentionally minimal and aligned with hackathon constraints.

## Prerequisites

- Python 3.13
- `uv` (Astral)
- Git

## Environment setup

```bash
uv init -p 3.13
uv sync
```

When adding dependencies, use:

```bash
uv add <package-name>
uv sync
```

## Database setup (SQLite)

```bash
uv run manage.py migrate
```

Optional:

```bash
uv run manage.py createsuperuser
```

## Run server

```bash
uv run manage.py runserver
```

## Common commands

```bash
uv run manage.py makemigrations
uv run manage.py migrate
uv run manage.py test
```

## Scope notes

- Do not use Docker for this phase.
- Do not require PostgreSQL, Redis, Celery, or tenant-specific commands.
- Keep setup compatible with local execution and demo reliability.