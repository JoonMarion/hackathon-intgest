# Models

Canonical MVP data model for this project.

## Shared model primitives

- Shared `Kind` enums must live in `config/models/choices.py` (neutral location, reusable across apps).
- Common timestamp fields are provided by abstract `BaseModel` in `config/models/base.py` (`created_at`, `updated_at`).
- Canonical imports for shared model primitives should come from `config/models/__init__.py`.
- Domain models must define an explicit `class Meta`.

## Core entities

## User

- Represents the application user.
- Uses Django auth model or a direct project equivalent.

## Category

- Fields (minimum): `name`, `kind` (`income` or `expense`, backed by shared `Kind` enums).
- Relationship: belongs to a user scope when applicable.
- Purpose: classify transactions.

## Transaction

- Fields (minimum): `transaction_date`, `amount`, `kind`, `category`, `description`.
- Kinds: `income` and `expense` from shared enums.
- Relationship: belongs to a category.

## Business rules

- Amount must be valid numeric.
- Category must be selectable during creation/edit.
- Balance should be derivable from transaction data.

## MVP alignment

This model set exists to support mandatory features from `RULES.md` and `PRODUCT.md`:

- Register income/expense
- Categorize entries
- List/edit/delete entries
- Compute and display summary balance