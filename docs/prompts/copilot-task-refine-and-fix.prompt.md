# Copilot Task Refinement Prompt Template

Use this after an initial implementation to fix gaps.

## Goal

Refine implementation for:
- TASK IDs: <TASK_SCOPE>

## Validation Inputs

- Test failures (if any)
- .agentic-sdlc/examples/inqacc/output/spec.md
- .agentic-sdlc/examples/inqacc/output/tasks.md
- .agentic-sdlc/examples/inqacc/output/test-spec.md
- .agentic-sdlc/examples/inqacc/output/openapi.yaml

## Required Actions

1. Fix only issues related to selected TASK IDs.
2. Do not weaken assertions to make tests pass.
3. Keep API contracts and error codes consistent with spec/openapi.
4. Update or add tests where behavior changes.

## Output Summary

- Root causes addressed
- Files changed
- Tests updated
- Any unresolved risk
