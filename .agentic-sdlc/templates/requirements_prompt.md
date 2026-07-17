# Requirements Prompt

Convert business rules and analysis into clear functional and non-functional requirements.

Inputs must include `intended-system.md` when available.
All requirements must align with target stack, versions, and security baseline from intended system.

Produce:
- Scope
- Functional requirements with IDs
- Non-functional requirements
- Constraints and assumptions
- Acceptance criteria

Minimum detail expectations:
- Use IDs `FR-xxx`, `NFR-xxx`, `AC-xxx`, and `ASM-xxx`.
- Each functional requirement references at least one source rule or legacy behavior.
- Include explicit security, observability, and environment requirements.
- Separate preserved legacy behavior from modernization enhancements.
