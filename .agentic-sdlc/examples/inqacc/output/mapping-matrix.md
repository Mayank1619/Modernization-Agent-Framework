# mapping-matrix.md

Status: DRY RUN

Agent: MappingMatrixAgent
Purpose: Create mapping and traceability matrices from requirements through implementation.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/output_primary

## Inputs Considered

- system-intent.md
- cobol/INQACC.cbl
- copybooks/ACCDB2.cpy
- copybooks/ACCOUNT.cpy
- copybooks/INQACCCZ.cpy
- output/business-rules.md
- output/code-review-checklist.md
- output/copilot-build-prompt.md
- output/intended-system.md
- output/mapping-matrix.md
- output/modernization-report.md
- output/plan.md
- output/program-analysis.md
- output/qa-review-checklist.md
- output/requirements.md
- output/spec.md
- output/tasks.md
- output/test-spec.md
- output/traceability-matrix.md
- output/openapi.yaml
- provided/system-intent.md

## Prompt Template

# Mapping Matrix Prompt

Generate mapping and traceability matrices.

Produce:
- Legacy artifact to modern component mapping
- Requirement to spec to test traceability
- Rule-to-test coverage indicators


## Input Previews

## Source: output/intended-system.md

# intended-system.md

Status: DRY RUN

Agent: SystemIntentAgent
Purpose: Define intended target system architecture and constraints before downstream requirement and spec generation.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/output_primary

## Inputs Considered

- system-intent.md
- cobol/INQACC.cbl
- copybooks/ACCDB2.cpy
- copybooks/ACCOUNT.cpy
- copybooks/INQACCCZ.cpy
- output/business-rules.md
- output/code-review-checklist.md
- output/copilot-build-prompt.md
- output/intended-system.md
- output/mapping-matrix.md
- output/modernization-report.md
- output/plan.md
- output/program-analysis.md
- output/qa-review-checklist.md
- output/requirements.md
- output/spec.md
- output/tasks.md
- output/test-spec.md
- output/traceability-matrix.md
- output/openapi.yaml
- provided/system-in

[...trimmed for token budget...]

H PIC 99.
              07 COMM-LAST-STMT-YEAR PIC 9999.
            05 COMM-NEXT-STMT-DT         PIC 9(8).
            05 COMM-NEXT-STMT-GROUP REDEFINES COMM-NEXT-STMT-DT.
              07 COMM-NEXT-STMT-DAY PIC 99.
              07 COMM-NEXT-STMT-MONTH PIC 99.
              07 COMM-NEXT-STMT-YEAR PIC 9999.
            05 COMM-AVAIL-BAL            PIC S9(10)V99.
            05 COMM-ACTUAL-BAL           PIC S9(10)V99.

## Source: provided/system-intent.md

# System Intent Blueprint

## Product goal
Modernize INQACC account inquiry into a web-accessible application with a Spring Boot backend and React frontend while preserving legacy observable behavior.

## Target stack
- Backend: Java 21, Spring Boot 3.3.x, Maven 3.9+
- Frontend: React 18.x, TypeScript 5.x, Vite 5.x, Node.js 20 LTS
- API: REST over HTTPS, OpenAPI 3.0.3
- Persistence for POC: Mock repository (no live CICS or DB2 connectivity)

## Security baseline
- Authentication: OAuth2 resource server with JWT bearer tokens
- Authorization: Role-based access control for account inquiry endpoints
- Transport: TLS 1.2+
- Input validation: strict path/query validation and standardized error responses
- Secrets handling: environment variables or secret manager, never in source control

## Operational baseline
- Logging: structured JSON logs with correlation ID per request
- Metrics: request latency, error rate, downstream adapter status
- Tracing: distributed tracing ready (OpenTelemetry)

## Delivery constraints
- Preserve legacy behavior as default path
- Any enhancement must be explicitly marked and toggleable
- Controllers remain thin, business logic in services
- Do not connect to real mainframe systems in POC mode

## Source: system-intent.md

# System Intent Blueprint

## Product goal
Modernize INQACC account inquiry into a web-accessible application with a Spring Boot backend and React frontend while preserving legacy observable behavior.

## Target stack
- Backend: Java 21, Spring Boot 3.3.x, Maven 3.9+
- Frontend: React 18.x, TypeScript 5.x, Vite 5.x, Node.js 20 LTS
- API: REST over HTTPS, OpenAPI 3.0.3
- Persistence for POC: Mock repository (no live CICS or DB2 connectivity)

## Security baseline
- Authentication: OAuth2 resource server with JWT bearer tokens
- Authorization: Role-based access control for account inquiry endpoints
- Transport: TLS 1.2+
- Input validation: strict path/query validation and standardized error responses
- Secrets handling: environment variables or secret manager, never in source control

## Operational baseline
- Logging: structured JSON logs with correlation ID per request
- Metrics: request latency, error rate, downstream adapter status
- Tracing: distributed tracing ready (OpenTelemetry)

## Delivery constraints
- Preserve legacy behavior as default path
- Any enhancement must be explicitly marked and toggleable
- Controllers remain thin, business logic in services
- Do not connect to real mainframe systems in POC mode

## Source: cobol/INQACC.cbl

CBL CICS('SP,EDF,DLI')
       CBL SQL
      ******************************************************************
      *                                                                *
      *  Copyright IBM Corp. 2023                                      *
      *                                                                *
      ******************************************************************

      ******************************************************************
      * This program takes an incoming account number. It then accesses
      * the DB2 datastore & retrieves the associated account record/row
      * matching on the account number & the account_type.
      *
      * Should there be any issues, the program will abend.
      *
      ******************************************************************

       IDENTIFICATION DIVISION.
       PROGRAM-ID. INQACC.
       AUTHOR. Jon Collett.

       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.

[...trimmed for token budget...]

END-IF.

       GLAD999.
           EXIT.


       POPULATE-TIME-DATE SECTION.
       PTD010.

           EXEC CICS ASKTIME
              ABSTIME(WS-U-TIME)
           END-EXEC.

           EXEC CICS FORMATTIME
                     ABSTIME(WS-U-TIME)
                     DDMMYYYY(WS-ORIG-DATE)
                     TIME(WS-TIME-NOW)
                     DATESEP
           END-EXEC.

       PTD999.
           EXIT.

## Source: copybooks/ACCDB2.cpy

******************************************************************
      *                                                                *
      *  Copyright IBM Corp. 2023                                      *
      *                                                                *
      *                                                                *
      ******************************************************************
           EXEC SQL DECLARE ACCOUNT TABLE
              ( ACCOUNT_EYECATCHER             CHAR(4),
                ACCOUNT_CUSTOMER_NUMBER        CHAR(10),
                ACCOUNT_SORTCODE               CHAR(6) NOT NULL,
                ACCOUNT_NUMBER                 CHAR(8) NOT NULL,
                ACCOUNT_TYPE                   CHAR(8),
                ACCOUNT_INTEREST_RATE          DECIMAL(4, 2),
                ACCOUNT_OPENED                 DATE,
                ACCOUNT_OVERDRAFT_LIMIT        INTEGER,
                ACCOUNT_LAST_STATEMENT         DATE,
                ACCOUNT_NEXT_STATEMENT         DATE,
                ACCOUNT_AVAILABLE_BALANCE      DECIMAL(10, 2),
                ACCOUNT_ACTUAL_BALANCE         DECIMAL(10, 2) )
           END-EXEC.

## Source: copybooks/ACCOUNT.cpy

******************************************************************
      *                                                                *
      *  Copyright IBM Corp. 2023                                      *
      *                                                                *
      *                                                                *
      ******************************************************************
              03 ACCOUNT-DATA.
                 05 ACCOUNT-EYE-CATCHER        PIC X(4).
                 88 ACCOUNT-EYECATCHER-VALUE        VALUE 'ACCT'.
                 05 ACCOUNT-CUST-NO            PIC 9(10).
                 05 ACCOUNT-KEY.
                    07 ACCOUNT-SORT-CODE       PIC 9(6).
                    07 ACCOUNT-NUMBER          PIC 9(8).
                 05 ACCOUNT-TYPE               PIC X(8).
                 05 ACCOUNT-INTEREST-RATE      PIC 9(4)V99.
                 05 ACCOUNT-OPENED             PIC 9(8).

[...trimmed for token budget...]

OUNT-NEXT-STMT-DATE     PIC 9(8).
                 05 ACCOUNT-NEXT-STMT-GROUP
                   REDEFINES ACCOUNT-NEXT-STMT-DATE.
                    07 ACCOUNT-NEXT-STMT-DAY   PIC 99.
                    07 ACCOUNT-NEXT-STMT-MONTH PIC 99.
                    07 ACCOUNT-NEXT-STMT-YEAR  PIC 9999.
                 05 ACCOUNT-AVAILABLE-BALANCE  PIC S9(10)V99.
                 05 ACCOUNT-ACTUAL-BALANCE     PIC S9(10)V99.

## Source: copybooks/INQACCCZ.cpy

******************************************************************
      *                                                                *
      *  Copyright IBM Corp. 2023                                      *
      *                                                                *
      *                                                                *
      ******************************************************************
          03 NUMBER-OF-ACCOUNTS        PIC S9(8) BINARY.
          03 CUSTOMER-NUMBER           PIC 9(10).
          03 COMM-SUCCESS              PIC X.
          03 COMM-FAIL-CODE            PIC X.
          03 CUSTOMER-FOUND            PIC X.
          03 COMM-PCB-POINTER          PIC X(4).
          03 ACCOUNT-DETAILS OCCURS 1 TO 20 DEPENDING ON
              NUMBER-OF-ACCOUNTS.
            05 COMM-EYE                  PIC X(4).
            05 COMM-CUSTNO               PIC X(10).
            05 COMM-SCODE                PIC X(6).

[...trimmed for token budget...]

H PIC 99.
              07 COMM-LAST-STMT-YEAR PIC 9999.
            05 COMM-NEXT-STMT-DT         PIC 9(8).
            05 COMM-NEXT-STMT-GROUP REDEFINES COMM-NEXT-STMT-DT.
              07 COMM-NEXT-STMT-DAY PIC 99.
              07 COMM-NEXT-STMT-MONTH PIC 99.
              07 COMM-NEXT-STMT-YEAR PIC 9999.
            05 COMM-AVAIL-BAL            PIC S9(10)V99.
            05 COMM-ACTUAL-BAL           PIC S9(10)V99.

## Source: output/business-rules.md

# business-rules.md

Status: DRY RUN

Agent: BusinessRulesAgent
Purpose: Extract and normalize business rules from legacy analysis and source artifacts.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/output_primary

## Inputs Considered

- cobol/INQACC.cbl
- copybooks/ACCDB2.cpy
- copybooks/ACCOUNT.cpy
- copybooks/INQACCCZ.cpy
- system-intent.md
- output/business-rules.md
- output/code-review-checklist.md
- output/copilot-build-prompt.md
- output/intended-system.md
- output/mapping-matrix.md
- output/modernization-report.md
- output/plan.md
- output/program-analysis.md
- output/qa-review-checklist.md
- output/requirements.md
- output/spec.md
- output/tasks.md
- output/test-spec.md
- output/traceability-matrix.md
- output/openapi.yaml
- provided/system-intent.md

## Prompt Template

#

[...trimmed for token budget...]

H PIC 99.
              07 COMM-LAST-STMT-YEAR PIC 9999.
            05 COMM-NEXT-STMT-DT         PIC 9(8).
            05 COMM-NEXT-STMT-GROUP REDEFINES COMM-NEXT-STMT-DT.
              07 COMM-NEXT-STMT-DAY PIC 99.
              07 COMM-NEXT-STMT-MONTH PIC 99.
              07 COMM-NEXT-STMT-YEAR PIC 9999.
            05 COMM-AVAIL-BAL            PIC S9(10)V99.
            05 COMM-ACTUAL-BAL           PIC S9(10)V99.

## Source: output/requirements.md

# requirements.md

Status: DRY RUN

Agent: RequirementsAgent
Purpose: Produce structured requirements from business rules and legacy findings.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/output_primary

## Inputs Considered

- system-intent.md
- cobol/INQACC.cbl
- copybooks/ACCDB2.cpy
- copybooks/ACCOUNT.cpy
- copybooks/INQACCCZ.cpy
- output/business-rules.md
- output/code-review-checklist.md
- output/copilot-build-prompt.md
- output/intended-system.md
- output/mapping-matrix.md
- output/modernization-report.md
- output/plan.md
- output/program-analysis.md
- output/qa-review-checklist.md
- output/requirements.md
- output/spec.md
- output/tasks.md
- output/test-spec.md
- output/traceability-matrix.md
- output/openapi.yaml
- provided/system-intent.md

## Prompt Template

# Requireme

[...trimmed for token budget...]

H PIC 99.
              07 COMM-LAST-STMT-YEAR PIC 9999.
            05 COMM-NEXT-STMT-DT         PIC 9(8).
            05 COMM-NEXT-STMT-GROUP REDEFINES COMM-NEXT-STMT-DT.
              07 COMM-NEXT-STMT-DAY PIC 99.
              07 COMM-NEXT-STMT-MONTH PIC 99.
              07 COMM-NEXT-STMT-YEAR PIC 9999.
            05 COMM-AVAIL-BAL            PIC S9(10)V99.
            05 COMM-ACTUAL-BAL           PIC S9(10)V99.

## Source: output/spec.md

# spec.md

Status: DRY RUN

Agent: SpecAgent
Purpose: Generate implementation-ready functional and technical specification.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/output_primary

## Inputs Considered

- system-intent.md
- output/business-rules.md
- output/code-review-checklist.md
- output/copilot-build-prompt.md
- output/intended-system.md
- output/mapping-matrix.md
- output/modernization-report.md
- output/plan.md
- output/program-analysis.md
- output/qa-review-checklist.md
- output/requirements.md
- output/spec.md
- output/tasks.md
- output/test-spec.md
- output/traceability-matrix.md
- output/openapi.yaml
- provided/system-intent.md

## Prompt Template

# Spec Prompt

Create implementation-ready specification from requirements.

Inputs must include `intended-system.md` whe

[...trimmed for token budget...]

H PIC 99.
              07 COMM-LAST-STMT-YEAR PIC 9999.
            05 COMM-NEXT-STMT-DT         PIC 9(8).
            05 COMM-NEXT-STMT-GROUP REDEFINES COMM-NEXT-STMT-DT.
              07 COMM-NEXT-STMT-DAY PIC 99.
              07 COMM-NEXT-STMT-MONTH PIC 99.
              07 COMM-NEXT-STMT-YEAR PIC 9999.
            05 COMM-AVAIL-BAL            PIC S9(10)V99.
            05 COMM-ACTUAL-BAL           PIC S9(10)V99.

## Source: output/openapi.yaml

# openapi.yaml

Status: DRY RUN

Agent: OpenApiAgent
Purpose: Generate OpenAPI starter contract from requirements and spec artifacts.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/output_primary

## Inputs Considered

- system-intent.md
- output/business-rules.md
- output/code-review-checklist.md
- output/copilot-build-prompt.md
- output/intended-system.md
- output/mapping-matrix.md
- output/modernization-report.md
- output/plan.md
- output/program-analysis.md
- output/qa-review-checklist.md
- output/requirements.md
- output/spec.md
- output/tasks.md
- output/test-spec.md
- output/traceability-matrix.md
- output/openapi.yaml
- provided/system-intent.md

## Prompt Template

# OpenAPI Prompt

Generate an OpenAPI contract skeleton based on requirements and specification.

Inputs must i

[...trimmed for token budget...]

H PIC 99.
              07 COMM-LAST-STMT-YEAR PIC 9999.
            05 COMM-NEXT-STMT-DT         PIC 9(8).
            05 COMM-NEXT-STMT-GROUP REDEFINES COMM-NEXT-STMT-DT.
              07 COMM-NEXT-STMT-DAY PIC 99.
              07 COMM-NEXT-STMT-MONTH PIC 99.
              07 COMM-NEXT-STMT-YEAR PIC 9999.
            05 COMM-AVAIL-BAL            PIC S9(10)V99.
            05 COMM-ACTUAL-BAL           PIC S9(10)V99.

## Source: output/code-review-checklist.md

# code-review-checklist.md

Status: DRY RUN

Agent: CodeReviewAgent
Purpose: Produce code review checklist and architecture conformance report skeleton.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacc/output_primary

## Inputs Considered

- system-intent.md
- output/business-rules.md
- output/code-review-checklist.md
- output/copilot-build-prompt.md
- output/intended-system.md
- output/mapping-matrix.md
- output/modernization-report.md
- output/plan.md
- output/program-analysis.md
- output/qa-review-checklist.md
- output/requirements.md
- output/spec.md
- output/tasks.md
- output/test-spec.md
- output/traceability-matrix.md
- output/openapi.yaml
- provided/system-intent.md

## Prompt Template

# Code Review Prompt

Create code review checklist aligned with spec-driven implementation.

[...trimmed for token budget...]

H PIC 99.
              07 COMM-LAST-STMT-YEAR PIC 9999.
            05 COMM-NEXT-STMT-DT         PIC 9(8).
            05 COMM-NEXT-STMT-GROUP REDEFINES COMM-NEXT-STMT-DT.
              07 COMM-NEXT-STMT-DAY PIC 99.
              07 COMM-NEXT-STMT-MONTH PIC 99.
              07 COMM-NEXT-STMT-YEAR PIC 9999.
            05 COMM-AVAIL-BAL            PIC S9(10)V99.
            05 COMM-ACTUAL-BAL           PIC S9(10)V99.

