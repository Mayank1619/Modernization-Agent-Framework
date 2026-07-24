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
All requirements must align with target stack, versions, and security baseline from intended system.

Produce:
- Scope
- Functional requirements with IDs
- Non-functional requirements
- Constraints and assumptions
- Acceptance criteria

Minimum detail expectations:
- Use IDs `FR-xxx`, `NFR-xxx`, `AC-xxx`, and `ASM-xxx`.
- Each functional requirement references at least one source rule or legacy behavior.
- Include explicit security, observability, and environment requirements.
- Separate preserved legacy behavior from modernization enhancements.


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

## Source: cobol/INQACCCU.cbl

CBL CICS('SP,EDF,DLI')
       CBL SQL
      ******************************************************************
      *                                                                *
      *  Copyright IBM Corp. 2023                                      *
      *                                                                *
      ******************************************************************
      ******************************************************************
      * This program takes an incoming customer number
      * and determines which accounts it is associated with
      * by accessing the datastore & retrieving
      * the associated account records matching on the customer number
      ******************************************************************

       IDENTIFICATION DIVISION.
       PROGRAM-ID. INQACCCU.
       AUTHOR. James O'Grady.


       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
      *SOURCE-COMPUTER.   IBM-370 WITH DEBU

[...trimmed for token budget...]

POPULATE-TIME-DATE SECTION.
       PTD010.
      D    DISPLAY 'POPULATE-TIME-DATE SECTION'.

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

## Source: copybooks/ABNDINFO.cpy

******************************************************************
      *                                                                *
      *  Copyright IBM Corp. 2023                                      *
      *                                                                *
      *                                                                *
      ******************************************************************
           03 ABND-VSAM-KEY.
              05 ABND-UTIME-KEY                  PIC S9(15) COMP-3.
              05 ABND-TASKNO-KEY                 PIC 9(4).
           03 ABND-APPLID                        PIC X(8).
           03 ABND-TRANID                        PIC X(4).
           03 ABND-DATE                          PIC X(10).
           03 ABND-TIME                          PIC X(8).
           03 ABND-CODE                          PIC X(4).
           03 ABND-PROGRAM                       PIC X(8).
           03 ABND-RESPCODE                      PIC S9(8) DISPLAY
                  SIGN LEADING SEPARATE.
           03 ABND-RESP2CODE                     PIC S9(8) DISPLAY
                  SIGN LEADING SEPARATE.
           03 ABND-SQLCODE                       PIC S9(8) DISPLAY
                  SIGN LEADING SEPARATE.
           03 ABND-FREEFORM                      PIC X(600).

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

## Source: copybooks/CUSTOMER.cpy

******************************************************************
      *                                                                *
      *  Copyright IBM Corp. 2023                                      *
      *
      *                                                                *
      ******************************************************************
           03 CUSTOMER-RECORD.
              05 CUSTOMER-EYECATCHER                 PIC X(4).
                 88 CUSTOMER-EYECATCHER-VALUE        VALUE 'CUST'.
              05 CUSTOMER-KEY.
                 07 CUSTOMER-SORTCODE                PIC 9(6) DISPLAY.
                 07 CUSTOMER-NUMBER                  PIC 9(10) DISPLAY.
              05 CUSTOMER-NAME.
                 07 CUSTOMER-TITLE                   PIC X(10).
                 07 CUSTOMER-FIRST-NAME              PIC X(50).
                 07 CUSTOMER-LAST-NAME               PIC X(50).
              05 CUSTOMER-DOB.
                 07 CU

[...trimmed for token budget...]

EATED-MONTH           PIC 99 DISPLAY.
                 07 CUSTOMER-CREATED-YEAR            PIC 9999 DISPLAY.
              05 CUSTOMER-CREDIT-SCORE               PIC 999.
              05 CUSTOMER-CS-REVIEW-DATE.
                 07 CUSTOMER-CS-REVIEW-DAY           PIC 99 DISPLAY.
                 07 CUSTOMER-CS-REVIEW-MONTH         PIC 99 DISPLAY.
                 07 CUSTOMER-CS-REVIEW-YEAR          PIC 9999 DISPLAY.

## Source: copybooks/INQACCCU.cpy

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
          03 COMM-PCB-POINTER          POINTER.
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

## Source: copybooks/INQCUSTZ.cpy

******************************************************************
      *                                                                *
      *  Copyright IBM Corp. 2023                                      *
      *                                                                *
      ******************************************************************
          03 INQCUST-EYE                  PIC X(4).
          03 INQCUST-SCODE                PIC X(6).
          03 INQCUST-CUSTNO               PIC 9(10).
          03 INQCUST-NAME.
             05 INQCUST-TITLE             PIC X(10).
             05 INQCUST-FIRST-NAME        PIC X(50).
             05 INQCUST-LAST-NAME         PIC X(50).
          03 INQCUST-DOB.
             05 INQCUST-DOB-DD            PIC 99 DISPLAY.
             05 INQCUST-DOB-MM            PIC 99 DISPLAY.
             05 INQCUST-DOB-YYYY          PIC 9999 DISPLAY.
          03 INQCUST-PHONE                PIC X(20).
          03 INQCUST-A

[...trimmed for token budget...]

DISPLAY.
          03 INQCUST-CREDIT-SCORE         PIC 999.
          03 INQCUST-CS-REVIEW-DT.
             05 INQCUST-CS-REVIEW-DD      PIC 99 DISPLAY.
             05 INQCUST-CS-REVIEW-MM      PIC 99 DISPLAY.
             05 INQCUST-CS-REVIEW-YYYY    PIC 9999 DISPLAY.
          03 INQCUST-INQ-SUCCESS          PIC X.
          03 INQCUST-INQ-FAIL-CD          PIC X.
          03 INQCUST-PCB-POINTER          PIC X(4).

## Source: copybooks/SORTCODE.cpy

******************************************************************
      *                                                                *
      *  Copyright IBM Corp. 2023                                      *
      *                                                                *
      *                                                                *
      ******************************************************************
       77 SORTCODE           PIC 9(6) VALUE 987654.

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

