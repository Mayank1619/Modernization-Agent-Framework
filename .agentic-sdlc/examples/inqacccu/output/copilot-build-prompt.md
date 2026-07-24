# copilot-build-prompt.md

Status: DRY RUN

Agent: CopilotPromptAgent
Purpose: Generate implementation prompts that can be pasted directly into GitHub Copilot.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacccu/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacccu/output

## Inputs Considered

- system-intent.md
- supporting/api/operation.yaml
- supporting/api/request.yaml
- supporting/api/response_200.yaml
- supporting/api/response_401.yaml
- supporting/api/response_403.yaml
- supporting/api/response_404.yaml
- supporting/api/response_500.yaml
- supporting/api/response_mapping.yaml
- supporting/zosAssets/zosAsset.yaml
- output/business-rules.md
- output/intended-system.md
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

## Source: output/intended-system.md

# intended-system.md

Status: DRY RUN

Agent: SystemIntentAgent
Purpose: Define intended target system architecture and constraints before downstream requirement and spec generation.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacccu/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacccu/output

## Inputs Considered

- system-intent.md
- supporting/api/operation.yaml
- supporting/api/request.yaml
- supporting/api/response_200.yaml
- supporting/api/response_401.yaml
- supporting/api/response_403.yaml
- supporting/api/response_404.yaml
- supporting/api/response_500.yaml
- supporting/api/response_mapping.yaml
- supporting/zosAssets/zosAsset.yaml
- cobol/INQACCCU.cbl
- copybooks/ABNDINFO.cpy
- copybooks/ACCDB2.cpy
- copybooks/ACCOUNT.cpy
- copybooks/CUSTOMER.cpy
- copybooks/INQACCCU.cpy
- copybooks/INQACCCZ.cpy
- copybooks/INQCUSTZ.cpy
- cop

[...trimmed for token budget...]

BM Corp. 2023                                      *
      *                                                                *
      *                                                                *
      ******************************************************************
       77 SORTCODE           PIC 9(6) VALUE 987654.

## Source: supporting/api/operation.yaml

---
version: "1.0"
zasset: "INQACCCU"

# Made with Bob

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

## Source: output/business-rules.md

# business-rules.md

Status: DRY RUN

Agent: BusinessRulesAgent
Purpose: Extract and normalize business rules from legacy analysis and source artifacts.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacccu/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacccu/output

## Inputs Considered

- cobol/INQACCCU.cbl
- copybooks/ABNDINFO.cpy
- copybooks/ACCDB2.cpy
- copybooks/ACCOUNT.cpy
- copybooks/CUSTOMER.cpy
- copybooks/INQACCCU.cpy
- copybooks/INQACCCZ.cpy
- copybooks/INQCUSTZ.cpy
- copybooks/SORTCODE.cpy
- system-intent.md
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

## Source:

[...trimmed for token budget...]

****
      *                                                                *
      *  Copyright IBM Corp. 2023                                      *
      *                                                                *
      *                                                                *
      ******************************************************************
       77 SORTCODE           PIC 9(6) VALUE 987654.

## Source: output/requirements.md

# requirements.md

Status: DRY RUN

Agent: RequirementsAgent
Purpose: Produce structured requirements from business rules and legacy findings.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacccu/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacccu/output

## Inputs Considered

- system-intent.md
- cobol/INQACCCU.cbl
- copybooks/ABNDINFO.cpy
- copybooks/ACCDB2.cpy
- copybooks/ACCOUNT.cpy
- copybooks/CUSTOMER.cpy
- copybooks/INQACCCU.cpy
- copybooks/INQACCCZ.cpy
- copybooks/INQCUSTZ.cpy
- copybooks/SORTCODE.cpy
- output/business-rules.md
- output/intended-system.md
- output/program-analysis.md

## Prompt Template

# Requirements Prompt

Convert business rules and analysis into clear functional and non-functional requirements.

Inputs must include `intended-system.md` when available.
All requirements must align with target stack, versions,

[...trimmed for token budget...]

****
      *                                                                *
      *  Copyright IBM Corp. 2023                                      *
      *                                                                *
      *                                                                *
      ******************************************************************
       77 SORTCODE           PIC 9(6) VALUE 987654.

## Source: output/spec.md

# spec.md

Status: DRY RUN

Agent: SpecAgent
Purpose: Generate implementation-ready functional and technical specification.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacccu/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacccu/output

## Inputs Considered

- system-intent.md
- supporting/api/operation.yaml
- supporting/api/request.yaml
- supporting/api/response_200.yaml
- supporting/api/response_401.yaml
- supporting/api/response_403.yaml
- supporting/api/response_404.yaml
- supporting/api/response_500.yaml
- supporting/api/response_mapping.yaml
- supporting/zosAssets/zosAsset.yaml
- output/business-rules.md
- output/intended-system.md
- output/program-analysis.md
- output/requirements.md

## Prompt Template

# Spec Prompt

Create implementation-ready specification from requirements.

Inputs must include `intended-system.md` when avai

[...trimmed for token budget...]

pping.yaml

---
version: "1.0"
response_200.yaml:
  condition: "$exists($zosAssetResponse.commarea.INQACCCZ) or
    $not($exists($zosAssetResponse.abendCode))"
  httpStatusCode: 200
response_400.yaml:
  httpStatusCode: 400
response_401.yaml:
  httpStatusCode: 401
response_403.yaml:
  httpStatusCode: 403
response_404.yaml:
  httpStatusCode: 404
response_500.yaml:
  condition: true
  httpStatusCode: 500

# Made with Bob

## Source: output/openapi.yaml

# openapi.yaml

Status: DRY RUN

Agent: OpenApiAgent
Purpose: Generate OpenAPI starter contract from requirements and spec artifacts.

## Pipeline Context

- Pipeline: mainframe_modernization
- Input Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacccu/legacy
- Output Root: C:/vscode/AgentsMainframeModernization/.agentic-sdlc/examples/inqacccu/output

## Inputs Considered

- system-intent.md
- supporting/api/operation.yaml
- supporting/api/request.yaml
- supporting/api/response_200.yaml
- supporting/api/response_401.yaml
- supporting/api/response_403.yaml
- supporting/api/response_404.yaml
- supporting/api/response_500.yaml
- supporting/api/response_mapping.yaml
- supporting/zosAssets/zosAsset.yaml
- output/business-rules.md
- output/intended-system.md
- output/mapping-matrix.md
- output/plan.md
- output/program-analysis.md
- output/requirements.md
- output/spec.md
- output/tasks.md
- output/test-spec.md
- output/traceability-matrix.md

## P

[...trimmed for token budget...]

able: false
        template: "ERROR_CODE"
    - message:
        required: true
        nullable: false
        template: "Error message"

## Source: supporting/api/response_500.yaml

---
version: "1.2"
mappings:
- body:
    mappings:
    - code:
        required: true
        nullable: false
        template: "ERROR_CODE"
    - message:
        required: true
        nullable: false
        template: "Error message"

## Source: supporting/api/operation.yaml

---
version: "1.0"
zasset: "INQACCCU"

# Made with Bob

## Source: supporting/api/request.yaml

---
version: "1.2"
mappings:
- commarea:
    mappings:
    - INQACCCZ:
        required: false
        nullable: false
        mappings:
        - CUSTOMER-NUMBER:
            required: false
            nullable: false
            expression: "$pathParameters.customerId"

## Source: supporting/api/response_200.yaml

---
version: "1.2"
mappings:
- body:
    mappings:
    - accounts:
        required: true
        nullable: false
        foreach:
          input: "$zosAssetResponse.commarea.INQACCCZ.\"ACCOUNT-DETAILS\""
          mappings:
          - accountId:
              required: true
              nullable: false
              template: "{{$item.\"COMM-ACCNO\"}}"
          - accountType:
              required: true
              nullable: false
              template: "{{$item.\"COMM-ACC-TYPE\"}}"
          - currency:
              required: true
              nullable: false
              template: "GBP"
          - accountNumber:
              required: false
              nullable: false
              template: "{{$item.\"COMM-ACCNO\"}}"
          - sortCode:
              required: false
              nullable: false
              template: "{{$item.\"COMM-SCODE\"}}"
          - status:
              required: true
              nullable: false
              template: "ACTIVE"
    - totalCount:
        required: false
        nullable: false
        expression: "$count($zosAssetResponse.commarea.INQACCCZ.\"ACCOUNT-DETAILS\"\
          )"

## Source: supporting/api/response_401.yaml

---
version: "1.2"
mappings:
- body:
    mappings:
    - code:
        required: true
        nullable: false
        template: "ERROR_CODE"
    - message:
        required: true
        nullable: false
        template: "Error message"

## Source: supporting/api/response_403.yaml

---
version: "1.2"
mappings:
- body:
    mappings:
    - code:
        required: true
        nullable: false
        template: "ERROR_CODE"
    - message:
        required: true
        nullable: false
        template: "Error message"

## Source: supporting/api/response_404.yaml

---
version: "1.2"
mappings:
- body:
    mappings:
    - code:
        required: true
        nullable: false
        template: "ERROR_CODE"
    - message:
        required: true
        nullable: false
        template: "Error message"

