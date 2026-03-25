# Models

Canonical MVP data model for this project.

## Core entities

## User

- Represents the application user.
- Uses Django auth model or a direct project equivalent.

## Category

- Fields (minimum): `name`, `type` (`income` or `expense`).
- Relationship: belongs to a user scope when applicable.
- Purpose: classify transactions.

## Transaction

- Fields (minimum): `date`, `amount`, `type`, `category`, `payee`, `notes`.
- Types: `income` and `expense`.
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