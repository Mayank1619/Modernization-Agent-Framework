# Spec Prompt

Create implementation-ready specification from requirements.

Inputs must include `intended-system.md` when available.
The spec is the source of truth for implementation and must remain consistent with intended architecture and security baseline.

Include:
- Domain model
- API behavior
- Validation rules
- Error handling
- Security and observability notes

Required structure:
1. Feature name and objective
2. Intended system alignment summary
3. API endpoints with request/response contracts
4. Business rule realization
5. Validation and error semantics
6. Security and compliance controls
7. Non-functional behavior (latency, reliability, logging)
8. Acceptance criteria table with IDs `AC-xxx`

Quality constraints:
- No placeholder sections.
- No invented fields outside copybooks/requirements/spec artifacts.
- Identify modernization enhancements explicitly.

Spec must be the source of truth for implementation.
