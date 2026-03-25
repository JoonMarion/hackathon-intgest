# Quick Start

Run the app locally with minimal steps.

## Prerequisites

- Python 3.13
- `uv` (Astral)
- Git

SQLite is used by default. No Docker is required.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Run migrations.
4. Create a superuser (optional, for Django admin).

```bash
uv init -p 3.13
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

## First MVP smoke check

Validate the mandatory base scope quickly:

1. Create at least one category.
2. Add one income and one expense.
3. Verify listing includes both entries.
4. Edit one entry and confirm updated values.
5. Delete one entry and confirm it is removed.
6. Verify dashboard/summary balance updates correctly.

## Troubleshooting

- **Module import error**: confirm virtual environment is active.
- **Migration errors**: rerun `uv run manage.py migrate` after dependency sync.
- **Port in use**: run `uv run manage.py runserver 0.0.0.0:8001`.