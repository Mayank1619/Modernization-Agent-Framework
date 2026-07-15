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

