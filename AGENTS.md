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

3. SystemIntentAgent
- Use after business rules to capture intended target architecture and constraints.
- Produces intended-system.md.

4. RequirementsAgent
- Use after business rules are drafted.
- Produces requirements.md.

5. SpecAgent
- Use when requirements are stable enough for design.
- Produces spec.md.

6. PlanAgent
- Use to define phased delivery path.
- Produces plan.md.

7. TaskAgent
- Use to create engineering backlog slices.
- Produces tasks.md.

8. MappingMatrixAgent
- Use to map legacy elements and maintain traceability.
- Produces mapping-matrix.md and traceability-matrix.md.

9. TestSpecAgent
- Use to define test strategy from rules and spec.
- Produces test-spec.md.

10. OpenApiAgent
- Use to create API contract starter.
- Produces openapi.yaml.

11. CopilotPromptAgent
- Use to generate Copilot implementation prompts.
- Produces copilot-build-prompt.md.

12. QAReviewAgent
- Use before and after implementation iterations.
- Produces qa-review-checklist.md.

13. CodeReviewAgent
- Use during PR review and architecture checks.
- Produces code-review-checklist.md.

14. ReportAgent
- Use at iteration close or milestone review.
- Produces modernization-report.md.
