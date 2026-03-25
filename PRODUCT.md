# Personal Financie — Product Specification (Hackathon Edition)

> Product scope and execution guide for the Ctrl+Alt+AI hackathon. This document is aligned with `RULES.md` and prioritizes a local, demonstrable MVP.

## Table of Contents

- Overview
- Hackathon Constraints
- Vision & Objectives
- Success Metrics (Event-Focused)
- Target Users & Personas
- User Needs & User Stories
- Product Features (Hackathon MVP / Optional / Roadmap)
- Data Model (Entities & Relationships)
- API / Backend Endpoints
- UI / UX Flows
- Permissions, Roles & Security
- AI-Assisted Development & Copilot Usage
- Mandatory Deliverables Checklist
- Testing Strategy & QA Checklist
- Release Plan & Milestones
- Risks & Open Questions
- Appendix

## Overview

- **Name:** Personal Financie
- **Short summary:** A simple, secure personal finance manager to track incomes, expenses, categories, and balance.
- **Primary platform:** Web
- **Hackathon goal:** Deliver a functional local MVP and demonstrate fast feature evolution with automation.

## Hackathon Constraints

This section is mandatory and takes precedence over aspirational roadmap items.

- **Required stack:** Python, Django, SQLite, VS Code, GitHub Copilot.
- **Execution model:** Must run locally during presentation.
- **Infrastructure limits:** No Docker/containerization; no critical dependency on complex external infrastructure.
- **Data policy:** No real sensitive data, credentials, or non-authorized corporate resources.
- **Event format:** Base delivery + live implementation of a newly drawn feature during evaluation.
- **Scope strategy:** Prioritize mandatory base requirements first; only then implement optional differentials.

## Vision & Objectives

- **Vision statement:** Help users quickly understand and control personal cash flow through a clear and practical finance tracker.
- **Primary objectives:**
  - Register income and expenses consistently.
  - Organize transactions by category.
  - Keep an always-updated balance and simple dashboard summary.
  - Demonstrate maintainable, AI-assisted evolution under time pressure.

## Success Metrics (Event-Focused)

- **Delivery:** All mandatory base requirements working in live demo.
- **Reliability:** App boots locally with clear README instructions.
- **Adaptability:** Team can implement and demonstrate the drawn feature during the evaluation window.
- **AI effectiveness:** Copilot usage is continuous, explainable, and measurable in the workflow.

## Target Users & Personas

- **Primary persona:** Individual user managing monthly personal finances.
- **Secondary persona:** Freelancer with mixed personal/professional inflows and outflows.

## User Needs & User Stories

- As a user, I want to add income and expenses quickly so I can track my financial movement.
- As a user, I want to categorize transactions so I can understand where money comes from and goes.
- As a user, I want to edit or remove incorrect entries so my balance remains accurate.
- As a user, I want a simple dashboard summary so I can see my financial status at a glance.
- As a user, I want to import transactions from CSV so I can avoid manual retyping.

### Acceptance baseline

- Income and expense registration must work end-to-end.
- Categories must be selectable/creatable and applied to transactions.
- Listing, editing, deletion, and automatic balance calculation must work.
- Dashboard/summary must present core numbers clearly.

## Product Features (Hackathon MVP / Optional / Roadmap)

### 1) Hackathon MVP (mandatory)

1. Register income.
2. Register expenses.
3. Create/select categories.
4. List financial entries.
5. Automatically calculate current balance.
6. Edit entries.
7. Delete entries.
8. Display a simple dashboard/summary panel.

### 2) Optional differentials (only after MVP is done)

- Date/category filters.
- Search by payee/description/category.
- Simple charts.
- Better validations and error handling.
- Basic automated tests.
- Seed data for demo.
- More complete README and technical organization.

### 3) Post-event roadmap (out of hackathon MVP)

- Budgets and recurring transactions.
- Auto-categorization rules.
- Multi-currency support.
- Reconciliation workflows.
- Notifications.
- Bank integrations (Plaid/Open Banking).
- Subscription billing (Stripe).
- Third-party email/analytics/object storage integrations.
- Mobile apps.
- ML-based category suggestions.

## Data Model (Entities & Relationships)

### Core entities for hackathon MVP

- **User:** id, name, email.
- **Category:** id, user_id, name, type (income/expense).
- **Transaction:** id, user_id, date, amount, kind (income/expense), category_id, payee, notes.

### Optional/support entities

- **Account:** optional for MVP; include only if it does not delay mandatory scope.
- **ImportLog:** optional helper for CSV import summaries.

### Relationships

- A User has many Categories and Transactions.
- A Transaction belongs to one Category.

## API / Backend Endpoints

Implementation can be server-rendered views, API endpoints, or a mixed approach. If API endpoints are used, prefer:

- `POST /api/auth/login` (if authentication is implemented)
- `GET/POST /api/categories`
- `GET/POST /api/transactions`
- `PATCH/DELETE /api/transactions/{id}`
- `POST /api/transactions/import` (CSV)
- `GET /api/reports/summary` (dashboard totals)

CSV import expectations:

- Required columns: `Date`, `Amount`, `Payee`, `Account` (or mapped equivalent).
- Support column mapping in import flow.
- Duplicate detection by `date + amount + payee`, and `ImportId` when present.
- Return/import preview with row-level errors and summary counts.

## UI / UX Flows

- **Onboarding:** access app → create first categories (if none) → add first transaction → view dashboard.
- **Add transaction:** simple form (date, amount, type, category, payee, notes).
- **Manage records:** list → edit/delete.
- **Import CSV:** upload → map columns → validate preview → confirm import.
- **Dashboard:** total income, total expenses, current balance, and optional category summary.

## Permissions, Roles & Security

- Minimal roles for hackathon: single user flow or basic authenticated user flow.
- Validate all AI-generated code before merging.
- Do not expose secrets or real credentials.
- Use only synthetic/demo data.

## AI-Assisted Development & Copilot Usage

The project must evidence effective AI-assisted development.

- Use Copilot across multiple phases (models/views/forms/templates/tests/docs).
- Keep prompt/response evidence or concise notes of how Copilot accelerated delivery.
- Be ready to explain what was generated, what was adapted, and why.
- During evaluation, use your established automation flow to implement the drawn feature.

## Mandatory Deliverables Checklist

- [ ] Application runs locally during presentation.
- [ ] Repository matches what is demonstrated.
- [ ] README contains minimum execution instructions.
- [ ] Mandatory MVP features are demonstrably working.
- [ ] Team explains how AI/automation was used in practice.
- [ ] Team provides concrete evidence of assisted development.
- [ ] Team demonstrates live evolution with the drawn feature.
- [ ] Team clearly explains what is complete and what is not.

## Testing Strategy & QA Checklist

- **Required for acceptance:** manual validation of all mandatory MVP flows.
- **Recommended differentials:**
  - Unit tests for core model/business rules.
  - Integration tests for transaction/category flows.
  - Basic import validation tests.
- Include a quick smoke checklist before demo:
  - App starts cleanly.
  - Create/edit/delete works.
  - Balance updates correctly.
  - Dashboard values are coherent.

## Release Plan & Milestones

- **v0.1 (Hackathon MVP):** all mandatory base requirements delivered and demo-ready.
- **v0.2 (Post-event short term):** budgets, recurring transactions, basic auto-categorization.
- **v1.0 (Post-event medium term):** integrations, subscriptions, advanced analytics, mobile.

## Risks & Open Questions

- **Scope risk:** too many optional features before mandatory MVP is complete.
- **Demo risk:** unresolved local setup issues near presentation time.
- **Quality risk:** accepting AI-generated code without review.
- **Open question:** implement account entity in MVP or keep transaction-centric single ledger?
- **Open question:** include authentication in MVP or keep single-user local mode for speed?

## Appendix

### Glossary

- **Transaction:** one financial movement (income or expense).
- **Category:** classification of transaction purpose/source.
- **Payee:** merchant/person associated with a transaction.
- **Ledger:** ordered record of financial entries.

### CSV Import Spec (initial)

- Required columns: `Date`, `Amount`, `Payee`, `Account` (or mapped equivalent).
- Optional columns: `Category`, `Notes`, `Currency`, `ImportId`.
- Date formats accepted: `DD/MM/YYYY`, `MM/DD/YYYY`, ISO (with mapping support).
- Signed amount convention: `+` income, `-` expense.
- Duplicate detection by `date + amount + payee`, and by `ImportId` when present.
- Error handling: row-level validation + actionable import summary (`imported`, `skipped`, `failed`).

### Maintainer Notes

- Keep this file as the product/documentation source of truth for event scope.
- When scope changes, update constraints, milestones, and checklist together.