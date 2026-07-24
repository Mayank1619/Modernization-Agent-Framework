# Copilot Agent Workflow

This guide connects the SDLC artifact pipeline to GitHub Copilot Agent in VS Code.

## 0) Run Copilot Agent in VS Code

Use this quick start each time you want Copilot to implement from specs.

1. Open this repository folder in VS Code.
2. Open Copilot Chat:
	- `Ctrl+Alt+I` (or `Cmd+Option+I` on macOS), or
	- View -> Chat.
3. Switch chat mode to `Agent` (not Ask/Edit).
4. Attach relevant files in chat before prompting:
	- `.agentic-sdlc/examples/inqacc/output/spec.md`
	- `.agentic-sdlc/examples/inqacc/output/tasks.md`
	- `.agentic-sdlc/examples/inqacc/output/test-spec.md`
	- `.agentic-sdlc/examples/inqacc/output/openapi.yaml`
	- `docs/prompts/copilot-task-implementation.prompt.md`
5. Paste your implementation request with explicit task IDs.
6. Let Agent apply changes, then run `test:python:all`.
7. If tests/review fail, run with:
	- `docs/prompts/copilot-task-refine-and-fix.prompt.md`

Starter prompt (normal flow):

```text
Implement TASK-001 to TASK-003 only.
Use these as authority: spec.md, tasks.md, test-spec.md, openapi.yaml.
Follow repo copilot instructions and keep changes in scope.
Add/adjust tests for acceptance criteria.
Return a traceability summary: task IDs implemented, files changed, tests updated, blockers.
```

Starter prompt (Spec Kit flow):

```text
Use the latest imported Spec Kit bundle at <SPEC_KIT_IMPORT_PATH>.
Implement <TASK_SCOPE> only.
Run review command: <SPEC_KIT_REVIEW_COMMAND>.
Run detail drift check:
python scripts/validate_detail_drift.py --generated-output .agentic-sdlc/examples/inqacc/output --bundle-specs <SPEC_KIT_IMPORT_PATH>/specs
Fix in-scope findings and rerun review.
Return: bundle applied summary, files changed, implemented task IDs, review result, blockers.
```

If `Agent` mode is not available, update VS Code and GitHub Copilot extensions, then sign in again.

## 0.1) Day-1 5-Minute Checklist

Use this exact sequence for a first successful run.

1. Set local keys and optional Spec Kit bridge settings in `.env.local`.
2. Run VS Code task: `validate:quick`.
3. Run VS Code task: `pipeline:generate:default`.
4. Open Copilot Chat in `Agent` mode.
5. Attach these files in chat:
	- `.agentic-sdlc/examples/inqacc/output/spec.md`
	- `.agentic-sdlc/examples/inqacc/output/tasks.md`
	- `.agentic-sdlc/examples/inqacc/output/test-spec.md`
	- `.agentic-sdlc/examples/inqacc/output/openapi.yaml`
	- `docs/prompts/copilot-task-implementation.prompt.md`
6. Ask Copilot to implement `TASK-001` only.
7. Run VS Code task: `test:python:all`.
8. If tests fail, use prompt: `docs/prompts/copilot-task-refine-and-fix.prompt.md`.
9. Run detail drift validation against the imported Spec Kit bundle.
10. Commit only when tests pass, detail drift validation passes, and traceability summary is complete.

Spec Kit variant:

1. Set `SPEC_KIT_PROJECT_DIR` and `SPEC_KIT_IMPORT_SUBDIR` in `.env.local`.
2. Run VS Code task: `orchestrate:spec-to-speckit`.
3. Use prompt: `docs/prompts/copilot-speckit-implement-review.prompt.md`.
4. Provide `<SPEC_KIT_IMPORT_PATH>`, `<TASK_SCOPE>`, and `<SPEC_KIT_REVIEW_COMMAND>`.
5. Run detail drift validator and fix only in-scope drift findings.

## 1) Generate or Refresh Artifacts

Use one of these VS Code tasks:

- pipeline:generate:default
- pipeline:autotune:tokens
- pipeline:dual:compare

Expected authoritative artifacts:

- .agentic-sdlc/examples/inqacc/output/spec.md
- .agentic-sdlc/examples/inqacc/output/tasks.md
- .agentic-sdlc/examples/inqacc/output/test-spec.md
- .agentic-sdlc/examples/inqacc/output/openapi.yaml
- .agentic-sdlc/examples/inqacc/output/copilot-build-prompt.md

## 2) Implement a Small Task Slice with Copilot Agent

Open this prompt template and fill TASK scope:

- docs/prompts/copilot-task-implementation.prompt.md

Recommended task size:

- 1 to 3 TASK IDs per iteration

## 2.1) Optional Spec Kit Bridge (Bundle -> Import -> Implement -> Review)

Set `.env.local` for target project bridge:

- SPEC_KIT_PROJECT_DIR=<absolute path to target project>
- SPEC_KIT_IMPORT_SUBDIR=spec-kit/imports

Run VS Code task:

- orchestrate:spec-to-speckit

What this does:

1. Regenerates authoritative artifacts.
2. Builds normalized bundle in `.agentic-sdlc/spec-kit-bundles/current`.
3. Publishes bundle into target project's Spec Kit import folder.

Then use this Copilot prompt template:

- docs/prompts/copilot-speckit-implement-review.prompt.md

Provide values for:

- `<SPEC_KIT_IMPORT_PATH>`
- `<TASK_SCOPE>`
- `<SPEC_KIT_REVIEW_COMMAND>`

## 2.2) Multi-Agent Spec Kit Generation Mode

Use this when you want richer package generation with tighter control over over-detail or under-detail drift.

Prompt template:

- docs/prompts/copilot-multi-agent-speckit-orchestration.prompt.md

Recommended flow:

1. Run `orchestrate:spec-to-speckit`.
2. Use the multi-agent orchestration prompt and provide:
	- `<SPEC_KIT_IMPORT_PATH>`
	- `<SPEC_KIT_REVIEW_COMMAND>`
3. Execute phases in order (foundation, design/contracts, delivery readiness).
4. Run detail drift validation and fix only in-scope findings.
5. Return traceability and drift summary before implementation handoff.

## 3) Validate Immediately

Run:

- test:python:all
- python scripts/validate_detail_drift.py --generated-output .agentic-sdlc/examples/inqacc/output --bundle-specs <SPEC_KIT_IMPORT_PATH>/specs

If failures occur, use:

- docs/prompts/copilot-task-refine-and-fix.prompt.md

## 4) Keep Traceability

For every implementation slice, include:

- Implemented TASK IDs
- Files changed
- Tests added/updated
- Outstanding blockers

## 5) Recommended Iteration Loop

1. Generate/refresh artifacts.
2. Implement one task slice.
3. Run tests.
4. Fix only in-scope issues.
5. Commit.
6. Repeat.

## 6) Notes

- Keep `.env` free of real secrets; use `.env.local` for local keys.
- Avoid broad refactors during task-scope implementation.
- If requirements are contradictory, stop and clarify before coding.
- If `speckit:publish` fails, verify `SPEC_KIT_PROJECT_DIR` is set and points to a valid folder.
