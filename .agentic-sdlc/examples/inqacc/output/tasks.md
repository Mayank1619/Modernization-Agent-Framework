# Tasks Prompt

Generate implementation tasks from plan.

## Task 1
- **Task ID**: TASK-001
- **Description**: Implement the Account Inquiry Service based on the legacy COBOL component `cobol/INQACC01.cbl`.
- **Dependencies**: None
- **Estimate**: M
- **Definition of done**: The service is implemented, tested, and integrated with the existing system.

## Task 2
- **Task ID**: TASK-002
- **Description**: Create the Account Record Model based on the legacy copybook `copybooks/ACCTREC.cpy`.
- **Dependencies**: None
- **Estimate**: S
- **Definition of done**: The model is created, validated against business rules, and documented.

## Task 3
- **Task ID**: TASK-003
- **Description**: Develop unit tests for business rule BR-001 to ensure account status is checked correctly.
- **Dependencies**: TASK-001
- **Estimate**: S
- **Definition of done**: Unit tests are written, passing, and cover all scenarios for BR-001.

## Task 4
- **Task ID**: TASK-004
- **Description**: Develop unit tests for business rule BR-002 to validate account ID presence and format.
- **Dependencies**: TASK-002
- **Estimate**: S
- **Definition of done**: Unit tests are written, passing, and cover all scenarios for BR-002.

## Task 5
- **Task ID**: TASK-005
- **Description**: Conduct a code review for the Account Inquiry Service implementation.
- **Dependencies**: TASK-001
- **Estimate**: M
- **Definition of done**: Code review is completed, and feedback is addressed.

## Task 6
- **Task ID**: TASK-006
- **Description**: Conduct a QA review of the Account Record Model and its associated tests.
- **Dependencies**: TASK-002, TASK-004
- **Estimate**: M
- **Definition of done**: QA review is completed, and all issues are resolved.

## Task 7
- **Task ID**: TASK-007
- **Description**: Update the mapping matrix to reflect the new modern components and their legacy counterparts.
- **Dependencies**: TASK-001, TASK-002
- **Estimate**: S
- **Definition of done**: Mapping matrix is updated and reviewed for accuracy.