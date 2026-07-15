# modernization-report.md

Status: DRY RUN

Agent: ReportAgent
Purpose: Compile a final modernization report that summarizes outputs and next actions.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/output

## Inputs Considered

- output/business-rules.md
- output/code-review-checklist.md
- output/copilot-build-prompt.md
- output/mapping-matrix.md
- output/plan.md
- output/program-analysis.md
- output/qa-review-checklist.md
- output/requirements.md
- output/spec.md
- output/tasks.md
- output/test-spec.md
- output/traceability-matrix.md
- output/openapi.yaml

## Prompt Template

# Final Report Prompt

Compile modernization report with:
- Inputs reviewed
- Artifacts generated
- Risks and gaps
- Recommended next actions
- Copilot usage notes


## Input Previews

## Source: output/business-rules.md

# business-rules.md

Status: DRY RUN

Agent: BusinessRulesAgent
Purpose: Extract and normalize business rules from legacy analysis and source artifacts.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/output

## Inputs Considered

- cobol/INQACC01.cbl
- copybooks/ACCTREC.cpy
- output/program-analysis.md

## Prompt Template

# Business Rules Prompt

Extract business rules from legacy sources and analysis outputs.

Produce:
- Rule identifier
- Rule statement
- Trigger conditions
- Inputs and outputs
- Error conditions

Avoid implementation details where possible.


## Input Previews

## Source: cobol/INQACC01.c

## Source: output/code-review-checklist.md

# code-review-checklist.md

Status: DRY RUN

Agent: CodeReviewAgent
Purpose: Produce code review checklist and architecture conformance report skeleton.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/output

## Inputs Considered

- output/business-rules.md
- output/copilot-build-prompt.md
- output/mapping-matrix.md
- output/plan.md
- output/program-analysis.md
- output/qa-review-checklist.md
- output/requirements.md
- output/spec.md
- output/tasks.md
- output/test-spec.md
- output/traceability-matrix.md
- output/openapi.yaml

## Prompt Template

# Code Review Prompt

Create code review checklist aligned with

## Source: output/copilot-build-prompt.md

# copilot-build-prompt.md

Status: DRY RUN

Agent: CopilotPromptAgent
Purpose: Generate implementation prompts that can be pasted directly into GitHub Copilot.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/output

## Inputs Considered

- output/business-rules.md
- output/mapping-matrix.md
- output/plan.md
- output/program-analysis.md
- output/requirements.md
- output/spec.md
- output/tasks.md
- output/test-spec.md
- output/traceability-matrix.md
- output/openapi.yaml

## Prompt Template

# Copilot Implementation Prompt

Use generated artifacts to produce implementation code in iterative pull requests.

Inpu

## Source: output/mapping-matrix.md

# mapping-matrix.md

Status: DRY RUN

Agent: MappingMatrixAgent
Purpose: Create mapping and traceability matrices from requirements through implementation.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/output

## Inputs Considered

- cobol/INQACC01.cbl
- copybooks/ACCTREC.cpy
- output/business-rules.md
- output/plan.md
- output/program-analysis.md
- output/requirements.md
- output/spec.md
- output/tasks.md

## Prompt Template

# Mapping Matrix Prompt

Generate mapping and traceability matrices.

Produce:
- Legacy artifact to modern component mapping
- Requirement to spec to test traceability
- Rule-to-test

## Source: output/plan.md

# plan.md

Status: DRY RUN

Agent: PlanAgent
Purpose: Build phased modernization and delivery plan from the approved specification.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/output

## Inputs Considered

- output/business-rules.md
- output/program-analysis.md
- output/requirements.md
- output/spec.md

## Prompt Template

# Plan Prompt

Produce delivery plan aligned with spec and requirements.

Include:
- Phases
- Milestones
- Dependencies
- Risks and mitigations
- Team ownership suggestions


## Input Previews

## Source: output/business-rules.md

# business-rules.md

Status: DRY RUN

Agent: BusinessRul

