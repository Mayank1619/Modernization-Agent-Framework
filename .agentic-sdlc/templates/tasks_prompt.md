# Tasks Prompt

Generate implementation tasks from plan.

Inputs must include `intended-system.md` when available.

For each task include:
- Task ID
- Description
- Dependencies
- Estimate (S/M/L)
- Definition of done

Minimum detail expectations:
- Use IDs `TASK-xxx`.
- Link each task to requirement IDs and acceptance criteria IDs.
- Include backend, frontend (if in scope), API contract, security, and test tasks.
- Include at least one migration/adapter task and one observability task.
