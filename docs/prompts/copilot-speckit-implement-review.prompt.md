# Copilot Spec Kit Implement and Review Prompt

Use this in VS Code Copilot Agent after running task `orchestrate:spec-to-speckit`.

## Goal

1. Load the latest imported Spec Kit bundle.
2. Apply/update project Spec Kit artifacts as needed.
3. Implement selected task scope.
4. Execute the project's Spec Kit review step.
5. Return findings and fixes.

## Inputs

- Imported bundle root: <SPEC_KIT_IMPORT_PATH>
- Task scope: <TASK_SCOPE>
- Project review command: <SPEC_KIT_REVIEW_COMMAND>

## Required Behavior

- Use bundle manifest first: `manifest.json`.
- Treat `spec.md`, `tasks.md`, `test-spec.md`, and `openapi.yaml` as authority.
- Keep implementation in scope for selected TASK IDs.
- If review fails, fix issues in scope and rerun review.
- Run detail drift validator against bundle specs:
	- `python scripts/validate_detail_drift.py --generated-output .agentic-sdlc/examples/inqacc/output --bundle-specs <SPEC_KIT_IMPORT_PATH>/specs`
- If detail drift fails, fix only in-scope artifacts and rerun validation.

## Output Format

1. Bundle applied summary
2. Files changed
3. Task IDs implemented
4. Review result (pass/fail + key findings)
5. Detail drift validation result (pass/fail + key findings)
6. Remaining blockers
