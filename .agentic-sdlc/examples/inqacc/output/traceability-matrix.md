```markdown
# Traceability Matrix for INQACC Modernization

**Document ID:** `traceability-matrix.md`  
**Pipeline:** mainframe_modernization  
**Authority:** provided/system-intent.md + intended-system.md + business-rules.md + requirements.md + spec.md + program-analysis.md + mapping-matrix.md + plan.md + tasks.md + test-spec.md + openapi.yaml  
**Status:** Implementation-ready traceability matrix  
**Generated:** 2024  
**Stack:** Java 21 + Spring Boot 3.3.x (backend) | React 18.x + TypeScript 5.x + Vite 5.x (frontend) | Mock Repository (POC)

## 1. Legacy Artifact to Modern Component Mapping

| Legacy Artifact         | Modern Component                        | Description                                           |
|-------------------------|----------------------------------------|-------------------------------------------------------|
| `cobol/INQACC.cbl`     | Spring Boot Service                    | Handles account inquiries and retrieves records.       |
| `copybooks/ACCDB2.cpy` | Database Entity Model                  | Represents account data structure in the application.  |
| `copybooks/ACCOUNT.cpy`| Data Transfer Object                   | Maps legacy account data to modern API response.      |
| `copybooks/INQACCCZ.cpy`| API Request/Response Model            | Structures data for account inquiries.                 |
| `output/business-rules.md`| Business Logic Implementation        | Enforces business rules in the service layer.         |
| `output/requirements.md`| Functional Requirements                | Defines system functionalities to be implemented.     |
| `output/spec.md`       | API Specification                      | Documents API endpoints and their contracts.          |

## 2. Requirement to Spec to Test Traceability

| Requirement ID | Requirement Description                                                                 | Spec Section        | Test Case ID |
|----------------|-----------------------------------------------------------------------------------------|----------------------|---------------|
| FR-001         | Execute Account Lookup by Composite Key (ACCOUNT_SORTCODE + ACCOUNT_NUMBER)           | 2.1, 2.2, 4.2; OpenAPI `GET /v1/accounts/{sortcode}/{accountNumber}` | TC-001       |
| FR-002         | Validate Sortcode Format (exactly 6 numeric digits)                                   | 2.3 (Validation Rules); OpenAPI path param pattern `^\d{6}$` | TC-004       |
| FR-003         | Validate Account Number Format (exactly 8 numeric digits)                             | 2.3 (Validation Rules); OpenAPI path param pattern `^\d{8}$` | TC-006       |
| FR-004         | Return HTTP 400 Bad Request with standardized error envelope for invalid sortcode     | 3.1 (Error Responses), 3.2 (Error Envelope); OpenAPI `400` response schema | TC-004       |
| FR-005         | Return HTTP 400 Bad Request with standardized error envelope for invalid account number | 3.1 (Error Responses), 3.2 (Error Envelope); OpenAPI `400` response schema | TC-006       |
| FR-006         | Return HTTP 404 Not Found when no matching account record exists                       | 3.1 (Error Responses); OpenAPI `404` response schema | TC-010       |
| FR-007         | Return HTTP 200 OK with complete account record JSON for valid matching account        | 2.1 (Endpoint Definition), 2.2 (Request/Response); OpenAPI `200` response schema | TC-001       |
| FR-008         | Return HTTP 401 Unauthorized when OAuth2 bearer token missing or invalid              | 2.1 (Security); OpenAPI `401` response schema | TC-012       |
| FR-009         | Return HTTP 403 Forbidden when authenticated user lacks ACCOUNT_INQUIRER role        | 2.1 (Security); OpenAPI `403` response schema | TC-014       |
| FR-010         | Attach X-Correlation-ID header to all HTTP responses                                   | 2.1 (Response Headers); OpenAPI response header definition | TC-016       |
| FR-011         | Propagate correlation ID through structured JSON logs                                   | 4.1 (Structured Logging); OpenAPI documentation | TC-018       |
| FR-012         | Support optional X-Correlation-ID header in request; generate UUID if not provided     | 2.1 (Request Headers); OpenAPI path parameter definition | TC-016       |
| FR-013         | Return all 12 account fields from ACCOUNT table in JSON response (per ACCDB2.cpy schema) | 2.2 (Account Response Schema); Mapping Matrix §1.2 | TC-011       |
| FR-014         | Preserve legacy field ordering and naming conventions from ACCOUNT.cpy                 | 2.2 (Account Response Schema); Mapping Matrix §1.2; Program Analysis §2.2 | TC-021       |
| FR-015         | Accept sortcode and account number as path parameters (not query string)              | 2.1 (Path Parameters); OpenAPI path definition `/accounts/{sortcode}/{accountNumber}` | TC-001       |
| FR-016         | Support optional X-Correlation-ID header in request                                   | 2.1 (Request Headers); OpenAPI parameter definition | TC-016       |

## 3. Rule-to-Test Coverage Indicators

| Rule ID | Rule Description                                                                 | Test Case ID |
|---------|----------------------------------------------------------------------------------|---------------|
| BR-001  | Account Record Lookup by Composite Key (ACCOUNT_SORTCODE + ACCOUNT_NUMBER)      | TC-001       |
| BR-002  | Sortcode Format Validation (exactly 6 numeric digits)                           | TC-004       |
| BR-003  | Account Number Format Validation (exactly 8 numeric digits)                     | TC-006       |
| BR-004  | Invalid Sortcode → HTTP 400 Bad Request with validation error detail            | TC-004       |
| BR-005  | Invalid Account Number → HTTP 400 Bad Request with validation error detail      | TC-006       |
| BR-006  | No Matching Record (Zero Rows) → HTTP 404 Not Found                             | TC-010       |
| BR-007  | Successful Lookup → HTTP 200 OK with complete Account JSON                      | TC-001       |
| BR-008  | Missing OAuth2 Bearer Token → HTTP 401 Unauthorized                             | TC-012       |
| BR-009  | Authenticated User Lacks ACCOUNT_INQUIRER Role → HTTP 403 Forbidden             | TC-014       |
| BR-010  | All 12 Account Fields Returned in Response                                       | TC-011       |
| BR-011  | Correlation ID Propagated to All Downstream Logs                                 | TC-018       |
| BR-012  | Correlation ID Generated if Not Provided in Request                              | TC-016       |
| BR-013  | Sortcode Path Parameter Extracted and Passed to Service Layer                   | TC-001       |
| BR-014  | Account Number Path Parameter Extracted and Passed to Service Layer             | TC-001       |
| BR-015  | Legacy Composite Key Semantics Preserved (No Account Type Discriminator in Modern Version) | TC-003       |
```