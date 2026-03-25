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

## Prompt examples

- "Use Feature Builder to implement transaction edit flow end-to-end (view, template partial, tests)."
- "Use Feature Builder to add category CRUD with HTMX partial updates."
- "Use Feature Builder to add dashboard summary cards and corresponding tests."

## Evaluation readiness checklist

- Can explain where Copilot helped most
- Can explain how Feature Builder orchestrated the implementation
- Can show how prompts evolved
- Can apply the same process to the newly drawn feature
- Can distinguish generated code from reviewed/fixed behavior