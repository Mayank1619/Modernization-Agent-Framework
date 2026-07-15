# traceability-matrix.md

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
- Rule-to-test coverage indicators


## Input Previews

## Source: cobol/INQACC01.cbl

IDENTIFICATION DIVISION.
       PROGRAM-ID. INQACC01.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-ACCOUNT-ID          PIC X(12).
       01  WS-ACCOUNT-STATUS      PIC X(01).
       PROCEDURE DIVISION.
           DISPLAY "INQACC01 START".
           MOVE "A12345678901" TO WS-ACCOUNT-ID.
           MOVE "A" TO WS-ACCOUNT-STATUS.
           IF WS-ACCOUNT-STATUS = "A"
               DISPLAY "ACCOUNT IS ACTIVE"
           ELSE
               DISPLAY "ACCOUNT NOT ACTIVE"
           END-IF.
           GOBACK.

## Source: copybooks/ACCTREC.cpy

01  ACCOUNT-RECORD.
           05  ACCOUNT-ID         PIC X(12).
           05  CUSTOMER-ID        PIC X(10).
           05  ACCOUNT-TYPE       PIC X(02).
           05  ACCOUNT-STATUS     PIC X(01).
           05  OPEN-DATE          PIC 9(8).

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

