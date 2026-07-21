# Mapping Matrix for INQACCCU Modernization

## 1. Legacy Artifact to Modern Component Mapping

| Legacy Artifact          | Modern Component                      | Description                                                  |
|--------------------------|--------------------------------------|--------------------------------------------------------------|
| `cobol/INQACCCU.cbl`    | Spring Boot Service                  | Handles account retrieval logic based on customer number.    |
| `copybooks/ACCDB2.cpy`  | JPA Entity                           | Maps to the ACCOUNT table structure in the database.         |
| `copybooks/ACCOUNT.cpy` | DTO (Data Transfer Object)           | Represents account details in the API response.              |
| `copybooks/INQACCCUZ.cpy` | Response Model                     | Contains inquiry result structures for API responses.         |

## 2. Requirement to Spec to Test Traceability

| Requirement ID | Requirement Description                                          | Source Rule ID | Spec Reference | Test Case ID |
|----------------|----------------------------------------------------------------|----------------|----------------|--------------|
| FR-001         | The system must retrieve account records associated with a given customer number. | BR-001         | 3.1            | TC-001       |
| FR-002         | The system must return a success flag indicating whether the customer was found. | BR-002         | 3.1            | TC-002       |
| AC-003         | Given a customer number, when the format is validated, then the system must return a validation result indicating whether the format is valid or invalid. | BR-003         | 3.1            | TC-003       |
| AC-004         | When preparing account data for response, the system must ensure that the data is sanitized. | BR-007         | 3.1            | TC-004       |

## 3. Rule-to-Test Coverage Indicators

| Rule ID | Test Case ID | Coverage Description                                          |
|---------|--------------|--------------------------------------------------------------|
| BR-001  | TC-001       | Tests retrieval of account records based on customer number. |
| BR-002  | TC-002       | Tests success flag return for found customer.                |
| BR-003  | TC-003       | Tests format validation for customer number.                 |
| BR-007  | TC-004       | Tests data sanitization before response.                     |

## 4. Additional Notes

- Ensure that all components adhere to the security baseline outlined in the system intent.
- Maintain strict input validation and sanitization to prevent injection attacks.
- The architecture must support distributed tracing as per operational baseline requirements.