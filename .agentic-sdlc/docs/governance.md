# Governance Guidance

## Guardrails

- spec.md is the implementation source of truth.
- intended-system.md is the target architecture and security source of truth for downstream artifacts.
- Legacy behavior must be preserved unless modernization enhancements are explicitly approved.
- Every business rule should have at least one test case in test-spec.md.
- Data contracts must reflect copybooks and approved specs only.
- POC mode must not connect to real mainframe systems.
- In dual-model mode, review dual-model-analysis.md before implementation handoff.

## Review Cadence

- Analyst review: program-analysis.md, business-rules.md, requirements.md
- Architect review: spec.md, openapi.yaml, mapping-matrix.md
- Engineering review: plan.md, tasks.md, copilot-build-prompt.md
- QA review: test-spec.md, qa-review-checklist.md
- Dual-model review: output_primary vs output_claude with merged output and dual-model-analysis.md
- Governance sign-off: modernization-report.md
