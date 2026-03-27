# AI-Assisted Workflow

How the team uses GitHub Copilot during implementation and evaluation.

## Primary orchestration mode

This project centers AI-assisted implementation around the custom **Feature Builder** agent defined in:

- `.github/agents/feature-builder.agent.md`

Use this agent as the default orchestrator for multi-step feature delivery.

## Workflow goals

- Accelerate implementation of mandatory MVP features
- Keep quality through human review of generated code
- Demonstrate repeatable automation during the drawn feature stage

## Recommended loop

1. Define task in one sentence.
2. Dispatch through Feature Builder for decomposition and coordinated execution.
3. Review generated/updated artifacts and adapt to project rules.
4. Run smoke checks/tests.
5. Document what was automated and what was adjusted manually.

## Frontend visual verification (when needed)

When a change affects templates, HTMX fragments, or interaction behavior, include a short browser validation step.

Suggested flow:
1. Ask the orchestrator to route UI work to `Frontend Dev`.
2. Open the target route with browser tooling (`openBrowserPage`) and verify render output.
3. Attempt one critical interaction (for example create/edit/delete or HTMX refresh).
4. Record result as evidence in the phase report (`checks_run`).

Notes:
- Browser validation complements tests and does not replace `execute/runTests`.
- Keep checks focused and fast; this is not a full E2E suite.
- If browser interaction is unavailable, report explicit skip reason and continue with test gates.

## Copilot + E2E test requests

When asking Copilot to add browser tests, always include an explicit selector contract:

- Use `data-e2e-selector` in every interaction.
- Keep scenarios isolated and deterministic.
- Avoid fixed sleeps; prefer assertion-based waiting.
- Keep one file focused on a small set of critical journeys.

Suggested request:

"Create Playwright E2E tests for <flow> using only data-e2e-selector, with isolated data per test and no arbitrary waits."

## Prompt examples

- "Use Feature Builder to implement transaction edit flow end-to-end (view, template partial, tests)."
- "Use Feature Builder to add category CRUD with HTMX partial updates."
- "Use Feature Builder to add dashboard summary cards and corresponding tests."
- "Use Feature Builder and include browser visual verification for the updated HTMX transaction list flow."

## Evaluation readiness checklist

- Can explain where Copilot helped most
- Can explain how Feature Builder orchestrated the implementation
- Can show how prompts evolved
- Can apply the same process to the newly drawn feature
- Can distinguish generated code from reviewed/fixed behavior