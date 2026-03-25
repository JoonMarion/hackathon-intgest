# Backend Features

This guide describes backend behavior expected for the hackathon MVP.

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

- `models.py`: Category and Transaction models
- `forms.py`: validation and user input handling
- `views.py`: create/list/edit/delete and summary views
- `urls.py`: route mapping

## Validation rules (minimum)

- Required: date, amount, transaction type, category
- Optional: payee, notes
- Reject invalid numeric amounts

## CSV import (optional differential)

If implemented in this phase:

- Support mapping of required columns
- Validate row-level errors
- Return a summary of imported/skipped/failed rows

## Scope guard

Do not add infrastructure-dependent backend features before mandatory MVP is complete.