# Governance Guidance

## Guardrails

- spec.md is the implementation source of truth.
- Legacy behavior must be preserved unless modernization enhancements are explicitly approved.
- Every business rule should have at least one test case in test-spec.md.
- Data contracts must reflect copybooks and approved specs only.
- POC mode must not connect to real mainframe systems.

## Review Cadence

- Analyst review: program-analysis.md, business-rules.md, requirements.md
- Architect review: spec.md, openapi.yaml, mapping-matrix.md
- Engineering review: plan.md, tasks.md, copilot-build-prompt.md
- QA review: test-spec.md, qa-review-checklist.md
- Governance sign-off: modernization-report.md
