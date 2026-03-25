# Frontend Guide

This guide focuses on practical frontend patterns for the hackathon MVP.

## Frontend stack

- HTMX for progressive interaction and partial page updates
- Django templates with Django 6 template partials
- Server-rendered HTML as the default rendering strategy

## Templates

- Use Django template inheritance with a base layout.
- Use template partials to isolate reusable fragments (forms, table rows, summary cards).
- Keep pages simple and task-oriented.
- Prefer explicit labels and error messages in forms.

## HTMX conventions

- Prefer HTMX for create/edit/delete/list refresh interactions.
- Return partial templates for HTMX requests and full templates for standard requests.
- Keep endpoints deterministic so both full and partial rendering remain consistent.

## Core screens

- Dashboard summary
- Transaction list
- Add/edit transaction form
- Category management

## Form UX guidelines

- Show validation errors near fields.
- Use clear success/error flash messages.
- Keep required fields minimal for quick data entry.
- For HTMX submissions, ensure response fragments can update feedback and affected sections.

## Styling

- Use existing styling approach already present in the repository.
- Prioritize readability and consistent spacing.
- Avoid introducing heavy UI framework complexity during MVP.

## Accessibility basics

- Ensure labels are linked to inputs.
- Use semantic headings and button text.
- Avoid interaction patterns that require JavaScript when not necessary.

## Out of scope for this phase

- Complex SPA behavior
- Advanced component systems
- Mobile-native design targets