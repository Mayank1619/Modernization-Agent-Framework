# Traceability Matrix

## 1. Legacy Artifact to Modern Component Mapping

| Legacy Artifact         | Modern Component                     |
|-------------------------|--------------------------------------|
| `cobol/INQACCCU.cbl`   | Spring Boot Service for Account Inquiry |
| `copybooks/ACCDB2.cpy` | JPA Entity for Account               |
| `copybooks/ACCOUNT.cpy`| DTO for Account Details              |
| `copybooks/INQACCCUZ.cpy` | Response Model for Account Inquiry  |

## 2. Requirement to Spec to Test Traceability

| Requirement ID | Requirement Description                                           | Spec Reference                          | Test Case ID |
|----------------|------------------------------------------------------------------|-----------------------------------------|---------------|
| FR-001         | The system must retrieve account records associated with a given customer number. | 3.1 Retrieve Account Records            | TC-001       |
| FR-002         | The system must return a success flag indicating whether the customer was found. | 3.1 Retrieve Account Records            | TC-002       |
| AC-003         | Given a customer number, when the format is validated, then the system must return a validation result indicating whether the format is valid or invalid. | 3.1 Retrieve Account Records            | TC-003       |
| AC-004         | When preparing account data for response, the system must ensure that the data is sanitized. | 3.1 Retrieve Account Records            | TC-004       |

## 3. Rule-to-Test Coverage Indicators

| Rule ID | Rule Description                                                                 | Test Case ID |
|---------|----------------------------------------------------------------------------------|---------------|
| BR-001  | The system must retrieve account records associated with a given customer number. | TC-001       |
| BR-002  | The system must return a success flag indicating whether the customer was found.  | TC-002       |
| BR-003  | The system must validate the format of the customer number.                      | TC-003       |
| BR-007  | The system must ensure that all data returned to the client is sanitized.        | TC-004       |