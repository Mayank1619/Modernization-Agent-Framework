# Agent Catalog

## Purpose

Defines each framework agent role and when to use it.

## Agents

1. LegacyAnalysisAgent
- Use when onboarding COBOL/copybook assets.
- Produces program-analysis.md.

2. BusinessRulesAgent
- Use after legacy analysis.
- Produces business-rules.md.

3. RequirementsAgent
- Use after business rules are drafted.
- Produces requirements.md.

4. SpecAgent
- Use when requirements are stable enough for design.
- Produces spec.md.

5. PlanAgent
- Use to define phased delivery path.
- Produces plan.md.

6. TaskAgent
- Use to create engineering backlog slices.
- Produces tasks.md.

7. MappingMatrixAgent
- Use to map legacy elements and maintain traceability.
- Produces mapping-matrix.md and traceability-matrix.md.

8. TestSpecAgent
- Use to define test strategy from rules and spec.
- Produces test-spec.md.

9. OpenApiAgent
- Use to create API contract starter.
- Produces openapi.yaml.

10. CopilotPromptAgent
- Use to generate Copilot implementation prompts.
- Produces copilot-build-prompt.md.

11. QAReviewAgent
- Use before and after implementation iterations.
- Produces qa-review-checklist.md.

12. CodeReviewAgent
- Use during PR review and architecture checks.
- Produces code-review-checklist.md.

13. ReportAgent
- Use at iteration close or milestone review.
- Produces modernization-report.md.
