# Architecture

This document describes the simplified architecture for the Personal Financie hackathon MVP.

## Stack

- Python 3.13
- Django
- SQLite
- HTMX
- Server-rendered templates with Django 6 template partials

## Architecture style

- Monolithic Django app structure
- Local-first execution
- Minimal dependencies
- Feature-first implementation for mandatory MVP scope

## Core domains

- **Accounts/Auth**: optional basic authentication flow
- **Categories**: create/select category for transactions
- **Transactions**: income + expense registration, listing, edit, delete
- **Dashboard**: summary totals and updated balance

## Data flow

1. User interacts with Django template forms.
2. HTMX requests submit/refresh targeted UI regions when applicable.
3. Views validate and persist data through Django ORM.
4. Dashboard aggregates totals from transaction data.
5. UI renders full templates or template partials depending on request mode.

## Project organization (recommended)

```
project/
├── manage.py
├── app/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── tests/
├── templates/
├── static/
└── docs/
```

## Non-goals for MVP

The following are intentionally out of scope for this phase:

- Multi-tenancy
- Celery/Redis workers
- Complex external API integrations
- Document extraction pipelines
- Native mobile apps

## Architecture decisions

- Keep operations synchronous to reduce complexity.
- Prefer clear CRUD flows over advanced abstractions.
- Use business validations in forms and/or model clean methods.
- Keep dashboard metrics simple and deterministic.