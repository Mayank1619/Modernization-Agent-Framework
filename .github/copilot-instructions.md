# Repository Copilot Instructions

This repository uses Spec-Driven Development for mainframe modernization.

## Non-Negotiable Rules

1. Use spec.md as the source of truth for implementation decisions.
2. Never invent fields that are not present in copybooks, requirements, or spec artifacts.
3. Preserve legacy behavior unless explicitly marked as a modernization enhancement.
4. Generate tests for every business rule.
5. Keep controllers thin.
6. Keep business logic in services.
7. Use repository interfaces for legacy adapters.
8. Do not connect to real mainframe systems in POC mode.

## Working Mode

- Prefer small incremental pull requests.
- Keep generated code aligned to openapi.yaml and tasks.md.
- Update mapping-matrix.md and traceability-matrix.md when requirements change.

## Copilot Agent Implementation Workflow

1. Treat these as authoritative inputs before writing code:
	- `.agentic-sdlc/examples/inqacc/output/spec.md`
	- `.agentic-sdlc/examples/inqacc/output/tasks.md`
	- `.agentic-sdlc/examples/inqacc/output/test-spec.md`
	- `.agentic-sdlc/examples/inqacc/output/openapi.yaml`
	- `.agentic-sdlc/examples/inqacc/output/copilot-build-prompt.md`
2. Implement only the requested task scope (for example TASK-001 to TASK-003).
3. For each implemented task:
	- Add or update tests that cover acceptance criteria.
	- Keep a clear mapping from requirement/task IDs to code and tests.
4. If requirements are unclear or contradictory, stop and ask for clarification rather than inventing behavior.
5. Keep commits reviewable:
	- One cohesive feature slice per change.
	- No unrelated refactors.

## Output Expectations for Agent Runs

- Return a short traceability summary with:
  - Implemented task IDs
  - Files changed
  - Tests added/updated
  - Remaining tasks not implemented
- Prefer deterministic, compilable code over speculative scaffolding.
