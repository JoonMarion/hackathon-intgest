---
name: django-project-initialization
description: Create and scaffold a Django 6 project with split settings and package-based apps under `apps/`, including app registration in project settings.
user-invocable: true
---

# Django Project Initialization Skill

Use this skill to initialize a new Django project (or normalize an early project) to a package-first structure with:

- `config/settings/{base,development,production,test}.py`
- `apps/` as the app root package
- app-level `models/`, `http/`, and `tests/` layout
- tests split into `tests/unit/` and `tests/integrations/`
- app-local templates using duck pattern under `apps/<app_name>/templates/<app_name>/...`
- app registration in `INSTALLED_APPS`

## Source of truth

When conflicts exist, follow:
1. `RULES.md`
2. `PRODUCT.md`
3. Active docs in `docs/README.md`

## Stack and constraints

- Python 3.13
- Django 6
- SQLite/local-first MVP
- Use `uv` commands only
- No Docker/containerization
- APIs are disallowed in this hackathon MVP

## Canonical app layout policy (strict)

For all new apps and scaffold-normalization work, this skill's target structure is mandatory.

- Do not keep or introduce flat app modules (`views.py`, `urls.py`, `tests.py`) as the primary layout.
- Use package-first app modules (`models/`, `http/`) and split tests into `tests/unit/` and `tests/integrations/`.
- Do not create `api/` packages in this hackathon scope.
- Keep templates app-local and organized by duck pattern (`apps/<app_name>/templates/<app_name>/...`) aligned to HTTP route/view responsibilities.

## When to use

- Starting a new Django codebase from scratch.
- Creating a new app in a project that already uses `apps/` package layout.
- Refactoring a flat app into package modules (`models/`, `http/`) without changing feature behavior.

## Required inputs

- `project_slug` (e.g., `myproject`)
- `app_name` (e.g., `accounts`, `products`)

## Target project structure

```
myproject/
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── test.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── manage.py
└── apps/
    ├── __init__.py
    ├── accounts/
    │   ├── __init__.py
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── user.py
    │   │   └── profile.py
    │   ├── http/
    │   │   ├── __init__.py
    │   │   ├── views.py
    │   │   ├── urls.py
    │   │   ├── forms.py
    │   │   ├── filtersets.py
    │   │   └── permissions.py
    │   ├── services.py
    │   └── tests/
    │       ├── __init__.py
    │       ├── unit/
    │       │   ├── __init__.py
    │       │   └── test_services.py
    │       └── integrations/
    │           ├── __init__.py
    │           └── test_http_transactions.py
    │   └── templates/
    │       └── accounts/
    │           ├── pages/
    │           │   ├── index.html
    │           │   └── form.html
    │           └── partials/
    │               └── summary_card.html
    └── products/
        ├── __init__.py
        ├── models/
        │   ├── __init__.py
        │   ├── product.py
        │   └── category.py
        ├── http/
        │   └── ...
        └── tests/
```

## Standard workflow

### 1) Initialize runtime and dependencies

```bash
uv init -p 3.13
uv add "django>=6,<7"
uv sync
```

### 2) Create project package as `config`

```bash
uv run django-admin startproject config .
```

### 3) Split settings module

Create:

- `config/settings/__init__.py`
- `config/settings/base.py`
- `config/settings/development.py`
- `config/settings/production.py`
- `config/settings/test.py`

Rules:

- `base.py` holds shared defaults (`INSTALLED_APPS`, middleware, templates, DB baseline).
- `development.py`, `production.py`, `test.py` import from base and override only environment-specific values.
- `manage.py`, `config/asgi.py`, and `config/wsgi.py` default to `config.settings.development` unless the caller sets `DJANGO_SETTINGS_MODULE`.

### 4) Create apps package root

```bash
mkdir -p apps
touch apps/__init__.py
```

### 5) Create app inside `apps/`

```bash
uv run manage.py startapp <app_name> apps/<app_name>
```

### 6) Convert app to package-first layout

For each app (example: `accounts`), ensure:

- `apps/accounts/models/` package with domain modules and re-exports in `models/__init__.py`
- `apps/accounts/http/` package for HTML/HTMX endpoints
- `apps/accounts/tests/` package with explicit test split:
  - `tests/unit/` for unit tests
  - `tests/integrations/` for integration tests
- `apps/accounts/templates/accounts/` with duck-pattern folders aligned to HTTP screens/fragments
- `apps/accounts/services.py` for domain service functions (when needed)

If files are created as flat modules by `startapp`, migrate code into package modules and keep imports explicit.

### 7) Register app in settings

Add app to `INSTALLED_APPS` in `config/settings/base.py`:

```python
INSTALLED_APPS = [
    # Django apps...
    "apps.<app_name>",
]
```

### 8) Wire URLs

Project root `config/urls.py` includes app URL entrypoint(s):

```python
from django.urls import include, path

urlpatterns = [
    path("<app_name>/", include("apps.<app_name>.http.urls")),
]
```

Within the app, keep dedicated `http/urls.py` module. If desired, add app-root `urls.py` as aggregator.
Within this hackathon scope, do not add `api/urls.py` or API route prefixes.

## App package checklist (per app)

- [ ] `apps/<app_name>/models/__init__.py` exports public models
- [ ] `apps/<app_name>/http/views.py` and `http/urls.py` present
- [ ] `apps/<app_name>/tests/__init__.py` present
- [ ] `apps/<app_name>/tests/unit/__init__.py` and unit tests present
- [ ] `apps/<app_name>/tests/integrations/__init__.py` and integration tests present
- [ ] app-local templates exist under `apps/<app_name>/templates/<app_name>/...` using duck pattern
- [ ] app is registered in `config/settings/base.py`
- [ ] imports resolve from package paths

## Validation checklist

Use `uv` commands only:

1. `uv run manage.py check`
2. `uv run manage.py makemigrations --check`
3. `uv run manage.py migrate`
4. `uv run manage.py test <apps.<app_name>.tests.module>`
5. verify folder compliance:
  - `apps/<app_name>/tests/unit/` and `apps/<app_name>/tests/integrations/`
  - `apps/<app_name>/templates/<app_name>/...` duck-pattern folders

## Guardrails

- Do not add infrastructure outside MVP scope.
- Keep refactors incremental; avoid changing URL names unless required.
- Prefer explicit imports over wildcard imports.
- Do not introduce API layer structures (`api/`) during this hackathon.

## Output contract (for worker reports)

```markdown
## Phase Report
- status: completed | blocked | partial
- files_changed:
  - <workspace relative path> (or "none")
- checks_run:
  - <tool/command + result>
- blockers:
  - <exact error output and failing file> (or "none")
- next_recommended_phase:
  - <phase id or "none">
```
