# Development Setup

This setup is intentionally minimal and aligned with hackathon constraints.

## Prerequisites

- `uv` (Astral) [Instalação](https://docs.astral.sh/uv/getting-started/installation/)
- Git

## Environment setup

```bash
uv init -p 3.13
uv sync
```

Create a `.env` file at the project root for local development:

```env
SECRET_KEY=unsafe-dev-secret-key-change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
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