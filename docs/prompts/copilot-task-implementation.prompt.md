# Copilot Task Implementation Prompt Template

Use this in VS Code Copilot Agent mode.

## Goal

Implement only this task scope:
- TASK IDs: <TASK_SCOPE>

## Authoritative Inputs

- .agentic-sdlc/examples/inqacc/output/spec.md
- .agentic-sdlc/examples/inqacc/output/tasks.md
- .agentic-sdlc/examples/inqacc/output/test-spec.md
- .agentic-sdlc/examples/inqacc/output/openapi.yaml
- .agentic-sdlc/examples/inqacc/output/copilot-build-prompt.md

## Constraints

- Do not invent fields or behavior outside documented requirements.
- Keep controllers thin; put business logic in services.
- Preserve legacy behavior unless explicitly marked as modernization enhancement.
- Align API contracts with openapi.yaml.
- Implement tests for acceptance criteria tied to selected TASK IDs.

## Deliverables

1. Implement code for TASK IDs in scope only.
2. Add/update tests proving acceptance criteria.
3. Provide a traceability summary:
   - TASK IDs implemented
   - Files changed
   - Tests added/updated
   - Open items or blockers

## Stop Conditions

- If requirements conflict or are missing, stop and ask for clarification.
- If change exceeds scope, split into follow-up tasks.
