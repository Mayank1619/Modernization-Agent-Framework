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

## Business Rules

### Rule 1
- **Rule Identifier**: BR-001
- **Rule Statement**: An account is considered active if its status is "A".
- **Trigger Conditions**: When the account status is checked.
- **Inputs**: WS-ACCOUNT-STATUS
- **Outputs**: "ACCOUNT IS ACTIVE" or "ACCOUNT NOT ACTIVE"
- **Error Conditions**: None specified.

### Rule 2
- **Rule Identifier**: BR-002
- **Rule Statement**: An account record must contain a valid account ID.
- **Trigger Conditions**: When an account record is created or updated.
- **Inputs**: ACCOUNT-ID
- **Outputs**: Validity confirmation
- **Error Conditions**: If ACCOUNT-ID is null or does not meet format requirements.

### Rule 3
- **Rule Identifier**: BR-003
- **Rule Statement**: The program retrieves an account record from the DB2 datastore based on the input account ID.
- **Trigger Conditions**: When an account retrieval request is made.
- **Inputs**: ACCOUNT-ID
- **Outputs**: Account record data
- **Error Conditions**: If ACCOUNT-ID does not exist in the datastore.

## Mapping Matrix

### Legacy Artifact to Modern Component Mapping

| Legacy Artifact         | Modern Component         |
|-------------------------|--------------------------|
| cobol/INQACC.cbl       | Account Retrieval Service |
| copybooks/ACCDB2.cpy   | Account Data Model       |
| copybooks/ACCOUNT.cpy   | Account Entity           |
| copybooks/INQACCCZ.cpy | Account Query Handler    |

### Requirement to Spec to Test Traceability

| Requirement ID | Requirement Description                                      | Spec ID | Spec Description                          | Test ID | Test Description                         |
|----------------|------------------------------------------------------------|---------|------------------------------------------|---------|------------------------------------------|
| REQ-001        | An account must be retrievable by a valid account ID.     | SPEC-001| Define the account retrieval process.    | TEST-001| Verify account retrieval with valid ID.  |
| REQ-002        | An account must be marked active based on its status.      | SPEC-002| Define the account status check process. | TEST-002| Verify account status check functionality.|

## Code Review Checklist

### Architectural Conformance
- Ensure all components adhere to the defined architecture.
- Verify that the mapping from legacy artifacts to modern components is correctly implemented.
- Confirm that services are properly separated and business logic is encapsulated.

### Naming and Readability
- Check that all variable, function, and class names are descriptive and follow naming conventions.
- Ensure code is formatted consistently and is easy to read.
- Review comments for clarity and relevance.

### Error Handling
- Validate that error conditions specified in business rules are handled appropriately.
- Ensure that meaningful error messages are provided for users and logs.
- Check for proper use of exceptions and error codes.

### Test Quality
- Confirm that tests cover all business rules and edge cases.