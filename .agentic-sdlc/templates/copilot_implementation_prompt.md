# Copilot Implementation Prompt

Use generated artifacts to produce implementation code in iterative pull requests.

Inputs:
- requirements.md
- spec.md
- plan.md
- tasks.md
- openapi.yaml
- mapping-matrix.md

Guidance:
- Implement smallest vertical slice first
- Keep controllers thin
- Keep business logic in services
- Add tests for every business rule
