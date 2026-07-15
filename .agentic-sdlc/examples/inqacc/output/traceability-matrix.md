# Traceability Matrix

## Legacy Artifact to Modern Component Mapping

| Legacy Artifact          | Modern Component        |
|-------------------------|-------------------------|
| cobol/INQACC.cbl        | Account Retrieval Service|
| copybooks/ACCDB2.cpy    | Account Data Model      |
| copybooks/ACCOUNT.cpy    | Account Entity          |
| copybooks/INQACCCZ.cpy   | Account Query Handler   |

## Requirement to Spec to Test Traceability

| Requirement ID | Requirement Description                                   | Spec ID | Spec Description                          | Test ID | Test Description                          |
|----------------|---------------------------------------------------------|---------|------------------------------------------|---------|------------------------------------------|
| REQ-001        | Retrieve account details based on account number        | SPEC-001| Account Retrieval Specification          | TEST-001| Verify account details are retrieved     |
| REQ-002        | Validate account status for active accounts              | SPEC-002| Account Status Validation Specification  | TEST-002| Check active account status validation    |
| REQ-003        | Ensure account ID is valid during creation/update        | SPEC-003| Account ID Validation Specification      | TEST-003| Validate account ID format and presence  |

## Rule-to-Test Coverage Indicators

| Rule ID | Rule Description                                           | Test ID | Coverage Status |
|---------|-----------------------------------------------------------|---------|------------------|
| BR-001  | An account is considered active if its status is "A".    | TEST-002| Covered           |
| BR-002  | An account record must contain a valid account ID.       | TEST-003| Covered           |
| BR-003  | The program retrieves an account record from the DB2 datastore based on the input account number. | TEST-001| Covered           |