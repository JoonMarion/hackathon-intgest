> ⚠️ Legacy reference: inherited from another project. These examples may not match this repository MVP scope.
> Use `docs/README.md`, `RULES.md`, and `PRODUCT.md` first.

# Subagent Prompt Examples

Reference prompts for autonomous subagent tasks in IntGestPED.

For the orchestrator that coordinates these subagents, see [Feature Builder](.github/../.github/agents/feature-builder.agent.md).

## Codebase Analysis

### Audit Extraction Engine Coverage
```
Analyze the extraction engine:
1. Read extraction-engine.instructions.md first
2. List all TipoDocumento types with registered extractors in extractors_by_type.py
3. Identify which extractors use PageGroup for multi-page documents
4. Report any extractors missing the redis_lock pattern
```

### Audit CRUD Implementations
```
Audit CRUD implementations:
1. Read crud-development.instructions.md
2. Find all Crud/MasterDetailCrud classes across views files
3. Check each has form_class and list_field_names defined
4. Verify URL registration in corresponding http/urls.py
5. Report CRUDs missing from rules/group_administrativo.py
```

## Pattern Compliance

### Verify Service Layer Patterns
```
Verify service layer patterns:
1. Read code-architecture.instructions.md section on services
2. Find all folders in **/services/ directories
3. Check if services use LazyModels (not direct model imports)
4. Verify presence of queries.py where database access exists
5. Report services with business logic in tasks.py instead
```

### Check Test Coverage for Services
```
Check test coverage for services:
1. Read testing.instructions.md
2. List all service folders in the codebase
3. Find corresponding test files in tests/unit/services/
4. Report services without test coverage
```

## Feature Research

### Trace Document Signing Flow
```
Research how document signing works end-to-end:
1. Start from intgest_sign/ external API integration
2. Find tasks that call signing services
3. Trace the flow from file upload to signed document
4. Document the complete flow with file references
```

### Understand PublishedPeriod Verification
```
Understand the PublishedPeriod verification process:
1. Find PublishedPeriod model and its status enum
2. Locate the verification service/task
3. Identify what validations are performed
4. Document the rejection criteria and messages
```

## Feature Builder Dispatch Pattern (v2)

Use this template when orchestrating implementation phases:

```markdown
## Dispatch Packet
- phase_id: 3
- objective: Implement service + view updates for payment-note linking
- scope: services, views, forms, urls for intgest_ped/files only
- files_to_touch:
   - intgest_ped/files/services/relation_linker/processor.py
   - intgest_ped/files/services/relation_linker/queries.py
   - intgest_ped/files/views/...
- forbidden_files:
   - intgest_ped/files/models/**
   - intgest_ped/files/migrations/**
- required_instructions:
   - .github/instructions/code-architecture.instructions.md
   - .github/instructions/crud-development.instructions.md
   - .github/instructions/testing.instructions.md
- acceptance_checks:
   - import check passes
   - runTests("intgest_ped/files/tests/unit/services/relation_linker") passes
   - runTask("django check") passes
- report_format: "Phase Report"
```

Expected worker response:

```markdown
## Phase Report
- status: completed
- files_changed:
      - intgest_ped/files/services/relation_linker/processor.py
      - intgest_ped/files/services/relation_linker/queries.py
- checks_run:
      - runTests("intgest_ped/files/tests/unit/services/relation_linker"): passed
   - runTask("django check"): passed
- blockers:
      - none
- next_recommended_phase:
      - 5
```

## Frontend Development

### Create Async-Loading UI Component
```
Create a lazy-loading button component:
1. Read .github/agents/frontend-dev.agent.md for all frontend conventions
2. In the template partial, render a neutral spinner button with data-status-url
   pointing to the API endpoint and a JS hook class (js-my-hook)
3. Create a vanilla JS file in intgest_ped/static/assets/js/portal/ that:
   - Uses document.querySelectorAll to find all hook elements
   - Calls fetch() on each data-status-url
   - Toggles CSS classes and icon based on the JSON response
4. Register the JS file in default_scripts.html after ped.js
5. Add data-selenium-selector attributes to all interactive elements
```

### Modify Portal Template Component
```
Modify the portal component at intgest_ped/templates/portal/pages/components/<name>.html:
1. Read .github/agents/frontend-dev.agent.md for template and selector conventions
2. Review the current template content and identify the change scope
3. Preserve all existing data-selenium-selector attributes
4. Use Tailwind utility classes and project custom classes (btn-navbar-*, effect-zoom)
5. Use fa-duotone icon prefix for all new icons
6. If adding JS behavior, use data- attributes + addEventListener (not inline onclick)
```

### Add Page-Specific JavaScript
```
Add a new JS feature for the portal:
1. Read .github/agents/frontend-dev.agent.md for JS coding rules
2. Create the file in intgest_ped/static/assets/js/portal/
3. Use const/let only, vanilla JS with fetch(), DOMContentLoaded listener
4. Include CSRF token via getCookie('csrftoken') for POST/PUT/DELETE
5. Use SweetAlert2 (Swal.fire) for confirmations and error displays
6. Register the script in default_scripts.html after ped.js
7. Add data-selenium-selector attributes to any DOM elements created by the script
```

## Output Format for Research Tasks

Structure research findings as:

```markdown
## Summary
[One paragraph overview]

## Findings
1. [Finding with file references]
2. [Finding with code examples if relevant]

## Recommendations
- [Actionable items]

## Files Analyzed
- [List of files read/searched]
```

## Search Strategies Reference

| Looking For | Where to Search |
|-------------|-----------------|
| Model definition | `models.py` or `models/` in target app |
| Service implementation | `<app>/services/<feature>/` |
| CRUD registration | `http/urls.py` — search for `include(*.get_urls())` |
| Task definition | `<app>/tasks.py` |
| Extractor function | `extraction_engine/extractors_by_type.py` |
| Permission groups | `intgest_ped/rules/group_*.py` |
| Enum values | `intgest_ped/util/enums/` |
| E2E navigator | `intgest_ped/tests/e2e/navigation/navigators/` |
| E2E selectors | `intgest_ped/tests/e2e/navigation/selectors.py` |
| E2E test data | `intgest_ped/tests/e2e/configs/static_manager.py` |