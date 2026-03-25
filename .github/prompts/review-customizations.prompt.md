---
name: review-customizations
description: Run a standardized audit of .github Copilot customizations with severity-ranked findings.
agent: Copilot Docs Reviewer
argument-hint: "Optional focus area (agents|instructions|skills|prompts|all)"
---
Review `.github/**/*.md` customization files and produce a structured report.

Focus area: ${input:focus:all}

Requirements:
1. Use the project precedence rules: `RULES.md` → `PRODUCT.md` → active docs in `docs/README.md`.
2. Validate interoperability between instructions, agents, prompts, and skills.
3. Prioritize findings by severity and implementation risk.
4. Keep recommendations minimal, actionable, and MVP-aligned.

Output format:

## Summary
[Short overall assessment]

## Scores
| Area | Score | Notes |
|------|-------|-------|
| Copilot instructions | X/10 | ... |
| Instruction files | X/10 | ... |
| Agent definitions | X/10 | ... |
| Prompt files | X/10 | ... |
| Skill files | X/10 | ... |
| Overall | X/10 | ... |

## Critical Issues (must fix)
1. **[File]**: [Issue] — [Why it matters] — [Fix]

## Improvements (should fix)
1. **[File]**: [Issue] — [Recommendation]

## Suggestions (nice to have)
1. **[File]**: [Suggestion]

## Recommended Next Steps
1. [Highest-priority implementation action]
2. [Second action]
3. [Third action]
