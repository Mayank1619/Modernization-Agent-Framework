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

## Source: output/program-analysis.md

# program-analysis.md

Status: DRY RUN

Agent: LegacyAnalysisAgent
Purpose: Analyze COBOL programs and copybooks to produce modernization-ready program analysis.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/output

## Inputs Considered

- cobol/INQACC01.cbl
- copybooks/ACCTREC.cpy

## Prompt Template

# Legacy Analysis Prompt

Analyze the provided COBOL programs and copybooks.

Produce:
- Program inventory
- Data structures and field map
- Business process flow
- Batch/online assumptions
- Risks and unknowns

Keep findings factual. Mark assumptions explicitly.


## Input Previews

## Source: cobol/INQACC01

## Source: output/requirements.md

# requirements.md

Status: DRY RUN

Agent: RequirementsAgent
Purpose: Produce structured requirements from business rules and legacy findings.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/output

## Inputs Considered

- cobol/INQACC01.cbl
- copybooks/ACCTREC.cpy
- output/business-rules.md
- output/program-analysis.md

## Prompt Template

# Requirements Prompt

Convert business rules and analysis into clear functional and non-functional requirements.

Produce:
- Scope
- Functional requirements with IDs
- Non-functional requirements
- Constraints and assumptions
- Acceptance criteria


## Input Previews

##

