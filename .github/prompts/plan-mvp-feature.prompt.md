---
name: plan-mvp-feature
description: Generate an MVP-first implementation plan aligned with hackathon constraints.
agent: Plan
argument-hint: "Describe the feature or paste requirement text"
---
Generate an implementation plan for this feature request:

${input:feature_request:Describe the feature and acceptance criteria}

Planning constraints:
- Follow precedence: `RULES.md` → `PRODUCT.md` → active docs in `docs/README.md`
- Keep scope local-first and demo-safe
- Prioritize mandatory MVP behavior before optional enhancements
- Use `uv` command patterns only
- Avoid Docker and complex external infrastructure

Required plan sections:
1. Overview
2. Requirements and assumptions
3. Architecture decisions (Django 6 + HTMX compatible)
4. Step-by-step implementation tasks
5. Validation plan (specific checks/tests)
6. Files expected to change
7. Risks and rollback strategy

Append a final `Phase Report` block using the project contract with:
- `status`
- `files_changed`
- `checks_run`
- `blockers`
- `next_recommended_phase`
