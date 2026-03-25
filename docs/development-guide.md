# Development Guide

Practical recipes for common implementation tasks.

## Add a new form-based feature

1. Add/adjust model fields
2. Create/update form class
3. Implement view logic
4. Add route in `urls.py`
5. Create/update template
6. Add tests or smoke checks

## Add a new field safely

1. Update model
2. Run `uv run manage.py makemigrations`
3. Run `uv run manage.py migrate`
4. Update forms/views/templates
5. Update tests

## Common commands

```bash
uv run manage.py makemigrations
uv run manage.py migrate
uv run manage.py runserver
uv run manage.py test
```

## Definition of done (MVP)

- Feature is reachable via UI
- Validation is correct
- Dashboard/list reflects data changes
- No conflict with mandatory scope priorities