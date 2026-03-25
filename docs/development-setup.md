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

## Static assets convention

- Root `static/` is for global assets shared by the whole application.
- Use `apps/<app_name>/static/<app_name>/...` for assets specific to one app.
- Global library examples:
	- `static/libs/tailwind/...`
	- `static/libs/htmx/...`
	- `static/libs/chartjs/...`
- Before adding a global asset, verify it is actually shared across multiple apps.

Example usage with `{% static %}`:

```django
{% load static %}

{# Global asset #}
<script src="{% static 'libs/chartjs/chart.umd.min.js' %}"></script>

{# App-local asset (example: transactions app) #}
<script src="{% static 'transactions/list.js' %}"></script>
```

## Scope notes

- Do not use Docker for this phase.
- Do not require PostgreSQL, Redis, Celery, or tenant-specific commands.
- Keep setup compatible with local execution and demo reliability.