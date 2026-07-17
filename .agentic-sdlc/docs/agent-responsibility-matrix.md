# Agent Responsibility Matrix

| Agent | Primary Input | Primary Output | Primary Responsibility |
|---|---|---|---|
| LegacyAnalysisAgent | COBOL + copybooks | program-analysis.md | Legacy inventory and structure analysis |
| BusinessRulesAgent | Legacy + analysis | business-rules.md | Business rule extraction |
| SystemIntentAgent | Legacy + provided system intent | intended-system.md | Target architecture, stack, and security intent baseline |
| RequirementsAgent | Rules + analysis | requirements.md | Requirement formalization |
| SpecAgent | requirements.md | spec.md | Functional and technical spec |
| PlanAgent | spec.md | plan.md | Delivery plan |
| TaskAgent | plan.md | tasks.md | Engineering task breakdown |
| MappingMatrixAgent | requirements/spec/tasks | mapping-matrix.md + traceability-matrix.md | Mapping and traceability |
| TestSpecAgent | rules/spec | test-spec.md | Test strategy and test cases |
| OpenApiAgent | requirements/spec | openapi.yaml | API contract skeleton |
| CopilotPromptAgent | all artifacts | copilot-build-prompt.md | Implementation prompt generation |
| QAReviewAgent | all artifacts | qa-review-checklist.md | QA verification guidance |
| CodeReviewAgent | all artifacts | code-review-checklist.md | Code review guidance |
| ReportAgent | all artifacts | modernization-report.md | Final summary report |

## Orchestration Responsibilities

| Component | Primary Responsibility |
|---|---|
| PipelineRunner | Sequential single-model artifact generation |
| DualRunOrchestrator | Primary + Claude runs, per-artifact compare, merge, and analysis reporting |
