---
name: "django-flat-to-package-refactor-v2"
description: Guidelines for evolving from flat `views.py` and `urls.py` to explicit app-root `http/` and `api/` packages with a canonical aggregator in Personal Financie.
user-invocable: true
---

# Django Flat-to-Package Refactor (Personal Financie)

Use this skill when an app still has flat `views.py` and/or `urls.py` and you want a clearer app-root structure with explicit `http/` and `api/` packages.

## Source of truth

When conflicts exist, follow:
1. `RULES.md`
2. `PRODUCT.md`
3. Active docs in `docs/README.md`

## When to use

- You need cleaner separation between HTML/HTMX endpoints and API endpoints.
- Flat files are growing and hard to maintain.
- You want staged refactor with backward compatibility.

## Target structure

For an app `myapp`:

```
myapp/
├── http/
│   ├── __init__.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── api/
│   ├── __init__.py
│   ├── views.py
│   ├── serializers.py   # only if API layer exists
│   └── urls.py
├── urls.py              # canonical app aggregator
├── views.py             # optional temporary compatibility shim
└── forms.py             # optional temporary compatibility shim
```

## Core rules

1. Keep route names stable where possible.
2. Keep `app_name` stable.
3. Prefer explicit imports in compatibility shims (no wildcard imports).
4. Keep HTTP routes compatible with Django templates + HTMX partial flows.
5. Keep changes incremental; avoid big-bang path rewrites unless requested.

## Canonical aggregator pattern

```python
from django.urls import include, path

app_name = "myapp"

urlpatterns = [
    path("", include("myapp.http.urls")),
    path("api/", include("myapp.api.urls")),
]
```

Use empty prefix for `http` routes unless a feature explicitly requires a different prefix.

## Migration workflow

1. Create `http/` and `api/` packages.
2. Move view/form code to package modules.
3. Create `http/urls.py` and `api/urls.py` preserving route `name=` values.
4. Replace old URL entrypoint with canonical app-root `urls.py` aggregator.
5. Add temporary compatibility shims for `views.py` and/or `forms.py` when needed.
6. Update imports/callers incrementally.
7. Remove shims only after callers are migrated and tests are green.

## Validation checklist

Use `uv` command style only:

1. `uv run manage.py check`
2. `uv run manage.py makemigrations --check`
3. `uv run manage.py test <app.tests.module>`
4. Optional broader run: `uv run manage.py test`

## Risks and mitigations

- Route breakage: preserve route names and add compatibility aliases if needed.
- Import breakage: keep explicit shims temporarily.
- Scope drift: refactor structure only; do not introduce unrelated behavior changes.

## References

- `docs/architecture.md`
- `docs/features-backend.md`
- `docs/features-frontend.md`
- `docs/development-setup.md`
