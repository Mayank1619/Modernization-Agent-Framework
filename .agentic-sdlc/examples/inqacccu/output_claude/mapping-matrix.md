# mapping-matrix.md

**Document ID:** `mapping-matrix-inqacccu-001`  
**Pipeline:** `mainframe_modernization`  
**Target Output File:** `mapping-matrix.md`  
**Purpose:** Traceability matrix linking legacy artifacts through requirements, specifications, business rules, and implementation tests  
**Last Updated:** 2025

---

## 1. Legacy-to-Modern Component Mapping

### 1.1 Program-Level Mapping

| Legacy Artifact | Legacy Purpose | Modern Component | Modern Stack | Mapping Status | Notes |
|---|---|---|---|---|---|
| INQACCCU.cbl | CICS-based online inquiry transaction; accepts customer number; returns account relationships | `CustomerAccountsController` (REST endpoint handler) | Spring Boot 3.3.x, Java 21 | ✓ Complete | CICS transaction dispatch → Spring REST `GET /api/v1/customers/{customerId}/accounts` |
| INQACCCU.cbl | Business logic: customer lookup, account retrieval, DLI/DB2 access | `CustomerAccountsService` | Spring Boot Service layer | ✓ Complete | Core inquiry logic preserved; DB2 access → mock repository (POC) |
| INQACCCU.cbl | Error handling (CICS RESP codes, SQLCODE) | `GlobalExceptionHandler`, custom `ApiException` hierarchy | Spring `@ControllerAdvice` | ✓ Complete | Legacy RESP codes → HTTP status codes (400, 401, 403, 500) |
| INQACCCU.cbl | Audit/logging (WS-DATE-TIME, formatted output) | `StructuredLoggingFilter`, `LoggingAspect` | Spring AOP + SLF4J + JSON formatter | ✓ Complete | Flat COBOL logging → structured JSON with correlation ID |

---

### 1.2 Data Structure Mapping (Copybooks → Java DTOs)

| Legacy Copybook | Legacy Field | Field Type | Legacy PIC | Modern DTO Class | Modern Field | Java Type | Mapping Rule | Validation |
|---|---|---|---|---|---|---|---|---|
| INQACCCUZ.cpy | CUSTOMER-NUMBER | Input | 9(10) | `CustomerAccountsRequest` | `customerId` | String | Numeric string (10 chars) | Pattern: `^\d{10}$`; reject if non-numeric or length ≠ 10 |
| INQACCCUZ.cpy | NUMBER-OF-ACCOUNTS | Output | S9(8) BINARY | `CustomerAccountsResponse` | `numberOfAccounts` | Integer | Binary signed integer | Range: 0–20; fail-safe default 0 if lookup fails |
| INQACCCUZ.cpy | CUSTOMER-FOUND | Output | X(1) | `CustomerAccountsResponse` | `customerFound` | Boolean | 'Y' → true; 'N' → false | Enum conversion; no null permitted |
| ACCOUNT.cpy | ACCOUNT-EYE-CATCHER | Output | X(4) | `AccountDetail` | `eyeCatcher` | String | Literal 'ACCT' | Constant validator: must equal "ACCT" |
| ACCOUNT.cpy | ACCOUNT-SORT-CODE | Output | 9(6) | `AccountDetail` | `sortCode` | String | 6-digit numeric string | Pattern: `^\d{6}$`; reject padding with spaces |
| ACCOUNT.cpy | ACCOUNT-NUMBER | Output | 9(8) | `AccountDetail` | `accountNumber` | String | 8-digit numeric string | Pattern: `^\d{8}$` |
| ACCOUNT.cpy | ACCOUNT-TYPE | Output | X(8) | `AccountDetail` | `accountType` | String | Alphanumeric (8 chars max) | Enum: CURRENT, SAVINGS, LOAN, etc. |
| ACCOUNT.cpy | ACCOUNT-INTEREST-RATE | Output | 9(4)V99 | `AccountDetail` | `interestRate` | BigDecimal | Decimal: 999.99 format | Scale: 2; precision: 6 |
| ACCOUNT.cpy | ACCOUNT-OPENED | Output | 9(8) | `AccountDetail` | `opened` | LocalDate | YYYYMMDD → ISO 8601 | Parse as `yyyyMMdd`; return as ISO string |
| ACCOUNT.cpy | ACCOUNT-OVERDRAFT-LIMIT | Output | 9(8) | `AccountDetail` | `overdraftLimit` | Long | 8-digit numeric | Range: 0–99,999,999 |
| ACCOUNT.cpy | ACCOUNT-LAST-STMT-DATE | Output | 9(8) | `AccountDetail` | `lastStatementDate` | LocalDate | YYYYMMDD → ISO 8601 | Parse as `yyyyMMdd`; return as ISO string |
| ACCOUNT.cpy | ACCOUNT-NEXT-STMT-DATE | Output | 9(8) | `AccountDetail` | `nextStatementDate` | LocalDate | YYYYMMDD → ISO 8601 | Parse as `yyyyMMdd`; return as ISO string |
| ACCOUNT.cpy | ACCOUNT-AVAILABLE-BALANCE | Output | S9(10)V99 | `AccountDetail` | `availableBalance` | BigDecimal | Signed decimal: ±9,999,999.99 | Scale: 2; precision: 12 |
| ACCOUNT.cpy | ACCOUNT-ACTUAL-BALANCE | Output | S9(10)V99 | `AccountDetail` | `actualBalance` | BigDecimal | Signed decimal: ±9,999,999.99 | Scale: 2; precision: 12 |
| ACCDB2.cpy | ACCOUNT_EYECATCHER through ACCOUNT_ACTUAL_BALANCE | DB2 TABLE columns | SQL DECLARE | `AccountEntity` (JPA) | Mapped via Hibernate annotations | Entity fields + @Column | Direct 1:1 SQL-to-ORM mapping | DB2 domain constraints apply (e.g., NOT NULL on SORT-CODE, ACCOUNT-NUMBER) |

---

## 2. Requirements-to-Specification Traceability

### 2.1 Functional Requirements → Spec Sections

| Requirement ID | Requirement Title | Requirement Statement | Spec Section | Spec ID | Implementation Status | Test Coverage |
|---|---|---|---|---|---|---|
| FR-001 | Customer Account Inquiry Acceptance | Accept 10-digit customer number; initiate account inquiry | Section 2.1.1: Input Specification | `spec-input-001` | ✓ In Progress | `IT001`, `IT002` |
| FR-002 | Account Retrieval | Retrieve 0–20 associated account records from data store | Section 2.2: Data Retrieval Logic | `spec-retrieve-001` | ✓ In Progress | `IT003`, `IT004`, `IT005` |
| FR-003 | Account Detail Return | Return complete account structure with all 13 fields | Section 2.3: Output Specification | `spec-output-001` | ✓ In Progress | `IT006`, `IT007` |
| FR-004 | Customer Not Found Handling | If customer not found, set CUSTOMER-FOUND='N' and return zero accounts | Section 2.4.1: Not Found Case | `spec-notfound-001` | ✓ Planned | `IT008` |
| FR-005 | Multiple Accounts | Support 1–20 accounts per customer | Section 2.3: Output Schema (accounts array) | `spec-output-001` | ✓ Planned | `IT009`, `IT010` |
| FR-006 | Authentication & Authorization | Enforce OAuth2 JWT bearer token; validate role for inquiry | Section 3.1: Security – Authentication | `spec-security-auth-001` | ✓ Planned | `SEC001`, `SEC002` |
| FR-007 | Strict Input Validation | Reject non-numeric or wrong-length customer IDs | Section 2.1.2: Input Validation Rules | `spec-input-validation-001` | ✓ Planned | `IV001`, `IV002`, `IV003` |
| FR-008 | Error Response Standardization | Return JSON error response with HTTP status code and message | Section 4.1: Error Handling | `spec-error-001` | ✓ Planned | `ERR001`, `ERR002`, `ERR003` |
| NFR-001 | Logging – Structured JSON | Log all requests/responses in structured JSON format with correlation ID | Section 5.1: Observability – Logging | `spec-logging-001` | ✓ Planned | `OBS001`, `OBS002` |
| NFR-002 | Metrics – Prometheus Export | Export latency, error rate, business metrics | Section 5.2: Observability – Metrics | `spec-metrics-001` | ✓ Planned | `OBS003`, `OBS004` |
| NFR-003 | Tracing – OpenTelemetry Ready | Instrument for distributed tracing (Jaeger/Datadog compatible) | Section 5.3: Observability – Tracing | `spec-tracing-001` | ✓ Planned | `OBS005` |
| NFR-004 | TLS Transport Security | All endpoints require TLS 1.2+ | Section 3.2: Transport Security | `spec-security-transport-001` | ✓ Planned | `SEC003`, `SEC004` |
| NFR-005 | Secrets Management | No secrets in source; use environment variables or Vault | Section 3.3: Secrets Management | `spec-security-secrets-001` | ✓ Planned | `SEC005` |

---

## 3. Business Rules-to-Test Traceability

### 3.1 Rule Inventory with Test Coverage

| Business Rule ID | Rule Title | Rule Statement | Rule Type | Spec Reference | Test ID(s) | Test Type | Test Status |
|---|---|---|---|---|---|---|---|
| BR001 | Customer Inquiry Acceptance | Accept 10-digit customer number input; set up inquiry context | Input Acceptance | Section 2.1.1 | `IT001`, `IT002` | Functional | ✓ Planned |
| BR002 | Account Retrieval from Datastore | Query account records where CUSTOMER-NUMBER matches input | Data Retrieval | Section 2.2 | `IT003`, `IT004`, `IT005` | Functional | ✓ Planned |
| BR003 | Strict Input Validation – No Fuzzy Matching | Reject customer IDs that are non-numeric, wrong length, or have spaces | Input Validation | Section 2.1.2 | `IV001`, `IV002`, `IV003`, `IV004` | Functional | ✓ Planned |
| BR004 | Account Status Preservation | Return all accounts regardless of status (Active, Inactive, Closed) | Data Retrieval | Section 2.2 | `IT006`, `IT007` | Functional | ✓ Planned |
| BR005 | Upper Bound Enforcement – Max 20 Accounts | Limit returned accounts to maximum 20; truncate if more exist | Data Retrieval | Section 2.3 | `IT009`, `IT010` | Functional | ✓ Planned |
| BR006 | Customer Not Found Response | If no customer record exists, set CUSTOMER-FOUND='N', return zero accounts | Exception Handling | Section 2.4.1 | `IT008`, `ERR001` | Functional | ✓ Planned |
| BR007 | Zero Accounts Valid State | Customer found but has zero accounts is a valid outcome | Exception Handling | Section 2.4.2 | `IT011` | Functional | ✓ Planned |
| BR008 | Authentication Enforcement | All requests must present valid OAuth2 JWT bearer token | Security | Section 3.1 | `SEC001`, `SEC002` | Security | ✓ Planned |
| BR009 | Role-Based Access Control | Only users with 'CUSTOMER_INQUIRY_READ' role may call endpoint | Security | Section 3.1 | `SEC002`, `SEC006` | Security | ✓ Planned |
| BR010 | Secrets Never in Source | Database credentials, OAuth2 secrets never committed to repository | Security | Section 3.3 | `SEC005` | Security | ✓ Planned |
| BR011 | Structured Logging – Correlation ID | Every request logged with unique correlation ID for traceability | Observability | Section 5.1 | `OBS001`, `OBS002` | Non-Functional | ✓ Planned |
| BR012 | Legacy Behavior Preservation (Default) | All legacy observable behavior maintained as default execution path | Behavioral | Section 1.2 | `IT001`–`IT011` | Functional | ✓ Planned |

---

## 4. Specification-to-Implementation Task Mapping

### 4.1 Spec Sections → Dev Tasks

| Spec Section | Spec ID | Implementation Task | Task ID | Owner | Delivery Phase | Status |
|---|---|---|---|---|---|---|
| Section 2.1: Input Specification | `spec-input-001` | Create `CustomerAccountsRequest` DTO and path variable extraction | `DEV-001` | Backend Lead | Phase 1 (Weeks 1–4) | ✓ Planned |
| Section 2.1.2: Input Validation Rules | `spec-input-validation-001` | Implement `@Pattern` validator; add `CustomerIdValidator` bean | `DEV-002` | Backend Lead | Phase 1 | ✓ Planned |
| Section 2.2: Data Retrieval Logic | `spec-retrieve-001` | Implement `AccountRepository` (mock) and `CustomerAccountsService.findAccountsByCustomerId()` | `DEV-003` | Backend Lead | Phase 1 | ✓ Planned |
| Section 2.3: Output Specification | `spec-output-001` | Create `CustomerAccountsResponse` and `AccountDetail` DTOs; configure Jackson serialization | `DEV-004` | Backend Lead | Phase 1 | ✓ Planned |
| Section 2.4: Error Handling | `spec-error-001` | Implement `GlobalExceptionHandler` with custom exception types (`CustomerNotFoundException`, `InvalidCustomerIdException`) | `DEV-005` | Backend Lead | Phase 1 | ✓ Planned |
| Section 3.1: Authentication | `spec-security-auth-001` | Configure OAuth2 resource server; add `@PreAuthorize("hasRole('CUSTOMER_INQUIRY_READ')")` annotations | `DEV-006` | Security Lead | Phase 2 (Weeks 5–8) | ✓ Planned |
| Section 3.1: Authorization | `spec-security-auth-001` | Implement `SecurityConfig` bean; define role mappings | `DEV-007` | Security Lead | Phase 2 | ✓ Planned |
| Section 3.2: Transport Security | `spec-security-transport-001` | Enable HTTPS in application.yml; configure TLS 1.2+ cipher suites | `DEV-008` | DevOps Lead | Phase 2 | ✓ Planned |
| Section 3.3: Secrets Management | `spec-security-secrets-001` | Configure Spring Cloud Config (or Vault); externalize DB_URL, OAUTH2_SECRET via environment variables | `DEV-009` | Security Lead | Phase 2 | ✓ Planned |
| Section 5.1: Logging – Structured JSON | `spec-logging-001` | Add Logback configuration with JSON encoder; implement `LoggingAspect` for request/response logging | `DEV-010` | Backend Lead | Phase 2 | ✓ Planned |
| Section 5.2: Metrics – Prometheus | `spec-metrics-001` | Add `spring-boot-starter-actuator` and Micrometer; define custom metrics (e.g., `customer_found_rate`) | `DEV-011` | Observability Lead | Phase 2 | ✓ Planned |
| Section 5.3: Tracing – OpenTelemetry | `spec-tracing-001` | Add OpenTelemetry SDK and auto-instrumentation; configure span exporters | `DEV-012` | Observability Lead | Phase 2 | ✓ Planned |
| Section 6: API Versioning & Compatibility | `spec-api-001` | Design URL structure `/api/v1/customers/{customerId}/accounts`; document backward-compatibility strategy | `DEV-013` | Architect | Phase 1 | ✓ Planned |

---

##