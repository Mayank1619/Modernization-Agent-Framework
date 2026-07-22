# QA Review Checklist for INQACCCU Modernization

## 1. Requirement Coverage Checks

| Requirement ID | Requirement Description                                                                 | Status  |
|----------------|-----------------------------------------------------------------------------------------|---------|
| FR-001         | The system must retrieve account records associated with a given customer number.      | Pending |
| FR-002         | The system must return a success flag indicating whether the customer was found.       | Pending |
| AC-001         | Given a customer number, when the account records are retrieved, then the system must return a list of associated account records. | Pending |
| AC-002         | If the customer number is invalid or not found, then the system must return a "Customer not found" message. | Pending |
| AC-003         | Given a customer number, when the format is validated, then the system must return a validation result indicating whether the format is valid or invalid. | Pending |
| AC-004         | When preparing account data for response, the system must ensure that the data is sanitized, and if sanitization fails, log the error and return a generic error message. | Pending |

## 2. Rule-to-Test Coverage

| Rule ID | Test Case ID | Test Description                                                                 |
|---------|--------------|----------------------------------------------------------------------------------|
| BR-001  | TC-001       | Test retrieval of account records based on valid customer number.                |
| BR-002  | TC-002       | Test success flag return when customer is found.                                 |
| BR-003  | TC-003       | Test format validation for customer number.                                      |
| BR-007  | TC-004       | Test data sanitization before response.                                         |

## 3. Data Mapping Validation Checks

| Legacy Artifact          | Modern Component                      | Validation Check Description                                      | Status  |
|--------------------------|--------------------------------------|------------------------------------------------------------------|---------|
| `cobol/INQACCCU.cbl`    | Spring Boot Service                  | Ensure data retrieval logic matches legacy behavior.             | Pending |
| `copybooks/ACCDB2.cpy`  | JPA Entity                           | Validate mapping of ACCOUNT table structure to JPA entity.      | Pending |
| `copybooks/ACCOUNT.cpy` | DTO (Data Transfer Object)           | Ensure DTO correctly represents account details in API response.  | Pending |
| `copybooks/INQACCCUZ.cpy` | Response Model                     | Validate inquiry result structures for API responses.            | Pending |

## 4. Non-Functional Verification Checks

| Check ID | Description                                                                 | Status  |
|----------|-----------------------------------------------------------------------------|---------|
| NF-001   | Verify that the application adheres to the security baseline (OAuth2, TLS).| Pending |
| NF-002   | Validate logging and metrics collection for request latency and error rates. | Pending |
| NF-003   | Ensure that input validation is strict and prevents injection attacks.      | Pending |
| NF-004   | Confirm that the application supports distributed tracing as per operational baseline. | Pending |

## 5. Additional Notes

- Ensure all components adhere to the specified technology stack and versions.
- Maintain strict input validation and sanitization to prevent injection attacks.
- Verify that legacy behavior is preserved as the default path and enhancements are toggleable.