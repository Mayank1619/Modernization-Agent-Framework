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
