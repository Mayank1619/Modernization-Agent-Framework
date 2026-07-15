# Mapping Matrix

## Legacy Artifact to Modern Component Mapping

| Legacy Artifact         | Modern Component         |
|-------------------------|--------------------------|
| cobol/INQACC.cbl       | Account Retrieval Service |
| copybooks/ACCDB2.cpy   | Account Data Model       |
| copybooks/ACCOUNT.cpy   | Account Entity           |
| copybooks/INQACCCZ.cpy | Account Query Handler    |

## Requirement to Spec to Test Traceability

| Requirement ID | Requirement Description                                      | Spec ID | Spec Description                          | Test ID | Test Description                         |
|----------------|------------------------------------------------------------|---------|------------------------------------------|---------|------------------------------------------|
| REQ-001        | The system must retrieve account details based on account number. | SPEC-001| Account Retrieval Specification          | TEST-001| Verify account details retrieval         |
| REQ-002        | The system must validate account ID during creation/update. | SPEC-002| Account ID Validation Specification      | TEST-002| Validate account ID format               |
| REQ-003        | The system must indicate if an account is active.         | SPEC-003| Active Account Status Specification      | TEST-003| Check active status of an account        |

## Rule-to-Test Coverage Indicators

| Rule ID | Rule Description                                            | Test ID | Coverage Status |
|---------|------------------------------------------------------------|---------|------------------|
| BR-001  | An account is considered active if its status is "A".     | TEST-003| Covered           |
| BR-002  | An account record must contain a valid account ID.        | TEST-002| Covered           |
| BR-003  | The program retrieves an account record from the DB2 datastore based on the incoming account number. | TEST-001| Covered           |