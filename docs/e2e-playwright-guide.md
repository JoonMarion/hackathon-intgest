# Playwright E2E Guide

This document records E2E testing conventions for future interactions with GitHub Copilot.

## Goal

Create short, deterministic browser tests that validate critical user journeys without coupling tests to CSS or implementation details.

## Current suite

- `apps/core/tests/e2e/base.py`
- `apps/core/tests/e2e/test_auth_navigation_flows.py`
- `apps/core/tests/e2e/test_accounts_flows.py`
- `apps/core/tests/e2e/test_categories_flows.py`
- `apps/core/tests/e2e/test_transactions_flows.py`
- `apps/core/tests/e2e/test_dashboard_flows.py`

Covered journeys:

- Protected routes redirect to login (unauthenticated)
- Cross-page navigation smoke flow
- Login using e-mail credential
- Login and logout via topbar menu
- Registration then login
- Profile edit
- Password change with re-login
- Category creation + transaction creation
- Category edit
- Category delete
- Category delete cancel
- Transaction edit
- Transaction delete
- Transaction delete cancel
- Transaction filter flow
- Transaction pagination + ordering
- Dashboard date filters + theme toggle
- Dashboard summary/recent/ranking + placeholder visibility

## Coverage matrix by flow

Covered now:

- Authentication: login (username/email), logout, register
- Account management: profile edit, password change
- Categories: create, edit, delete, cancel delete
- Transactions: create, edit, delete, cancel delete, filters, ordering, pagination
- Dashboard: summary visibility, date filter, clear filter, theme toggle, rankings
- Route protection: authenticated access guard redirects

Remaining gaps (next iteration):

- Form cancel/back flows (`categories-form-cancel-link-click`, `transactions-form-cancel-link-click`)
- Toast dismissal interaction (`core-toasts-dismiss-click`)
- Pagination boundary assertions for categories (if pagination is introduced later)

## Standard commands

Run E2E only:

```bash
$ uv run pytest apps/core/tests/e2e -q
```

Run specific scenario:

```bash
$ uv run pytest apps/core/tests/e2e/test_dashboard_flows.py -k dashboard -q
```

## Selector standard

Use `data-e2e-selector` as the stable contract between UI and tests.

Examples:

- `page.get_by_test_id("transactions-form-submit-click")`
- `page.locator("[data-e2e-selector^='transactions-index-edit-link-click-']")`

Do not use:

- Tailwind or CSS class selectors
- Deep chained selectors tied to layout
- Generic selectors such as `button` for critical actions

## Best practices adopted from official docs

### Playwright

- Prefer resilient locators and web-first assertions (`expect(locator).to_be_visible()`).
- Keep tests isolated (fresh context, no cross-test dependency).
- Focus on user-visible behavior and outcomes.
- Avoid testing third-party pages and flows outside project control.

References:

- `https://playwright.dev/docs/best-practices`
- `https://playwright.dev/docs/locators`

### Cypress (cross-framework practices applied)

- Use `data-*` attributes as explicit testing contracts.
- Reset/prepare state before each test instead of relying on after hooks.
- Avoid arbitrary waiting; rely on explicit conditions.
- Keep tests independent and runnable in isolation.

Reference:

- `https://docs.cypress.io/app/core-concepts/best-practices`

## Copilot prompt template for new E2E tests

Use this prompt pattern when asking Copilot for more E2E coverage:

```text
Create Playwright E2E tests for <flow-name>.
Requirements:
1) Use only data-e2e-selector for interactions.
2) Keep tests isolated and deterministic.
3) Avoid sleep/wait-for-time; use web-first assertions.
4) Cover happy path and one key negative or filter scenario.
5) Include run commands with uv.
```

## Review checklist for E2E PRs

- Every interaction uses `data-e2e-selector`
- No fixed `sleep` or arbitrary waits
- Test data is created inside each scenario
- Assertions validate user-visible outcomes
- Tests can run independently