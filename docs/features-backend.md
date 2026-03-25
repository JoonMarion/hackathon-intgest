# Backend Features

This guide describes backend behavior expected for the hackathon MVP.

> ⚠️ IMPORTANTE: Abordagem do MVP sem APIs. Não criar nem consumir endpoints API.

## Mandatory feature set

- Create income entries
- Create expense entries
- Create/select categories
- List entries
- Edit entries
- Delete entries
- Calculate updated balance
- Provide summary data for dashboard

## Suggested implementation modules

- `apps/<app>/models/`: Category and Transaction domain models
- `config/models/choices.py`: shared `Kind` enums
- `config/models/base.py`: abstract `BaseModel` with `created_at` and `updated_at`
- `config/models/__init__.py`: canonical import surface for shared model primitives
- `apps/<app>/http/forms.py`: validation and user input handling
- `apps/<app>/http/views.py`: create/list/edit/delete and summary views
- `apps/<app>/http/urls.py`: route mapping

Domain models should always declare explicit `class Meta`.

## Validation rules (minimum)

- Required: date, amount, transaction type, category
- Optional: description
- Reject invalid numeric amounts

## CSV import (optional differential)

If implemented in this phase:

- Support mapping of required columns
- Validate row-level errors
- Return a summary of imported/skipped/failed rows

## Scope guard

Do not add infrastructure-dependent backend features before mandatory MVP is complete.