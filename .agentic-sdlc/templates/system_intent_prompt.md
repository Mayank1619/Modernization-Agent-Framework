# System Intent Prompt

Create `intended-system.md` as the canonical target-system blueprint used by all downstream agents.

Use legacy inputs plus any provided `system-intent.md` or `intended-system.md` notes.
If user-provided intent exists, it overrides defaults.

Required sections (use this exact order):
1. Feature and modernization objective
2. Target product scope
3. Architecture blueprint
4. Technology stack and versions
5. Security and compliance baseline
6. API and integration constraints
7. Data and mapping constraints
8. Observability and operational requirements
9. Delivery constraints and environments
10. Out of scope
11. Assumptions and open questions

Section requirements:
- Technology stack and versions must include backend, frontend, build tooling, runtime, and test frameworks.
- Security section must include authN/authZ approach, transport security, input validation, error-handling policy, and secrets handling.
- Constraints must preserve legacy observable behavior unless explicitly marked as modernization enhancement.
- Mark each assumption with ID `ASM-xxx`.
- Mark each open question with ID `Q-xxx`.

Output rules:
- Output only markdown content for `intended-system.md`.
- Do not invent legacy fields not present in source artifacts.
- Keep language implementation-ready and specific.
