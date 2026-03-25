# Frontend Features

This document maps mandatory product flows to frontend pages.

Rendering strategy for this project:

- HTMX-driven interaction for partial updates
- Django 6 template partials for reusable response fragments

## Required pages

- Dashboard summary page
- Transaction list page
- Add transaction page
- Edit transaction page
- Category management page

## Required flows

## Add transaction

1. Open form
2. Fill required fields
3. Submit
4. Confirm success feedback
5. Confirm updated list/summary fragment refreshes without full reload when HTMX is used

## Edit transaction

1. Open selected entry
2. Update data
3. Save
4. Confirm persistence and partial UI refresh

## Delete transaction

1. Trigger delete
2. Confirm action
3. Verify removal and recalculated totals in refreshed fragments

## Dashboard summary

Display at least:

- Total income
- Total expense
- Current balance

## UX priorities

- Fast input
- Clear validation messages
- Reliable feedback for create/update/delete
- Keep parity between full-page and partial rendering results