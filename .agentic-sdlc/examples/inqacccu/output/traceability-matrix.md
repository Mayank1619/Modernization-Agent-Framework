# Traceability Matrix

**Document ID:** `traceability-matrix-inqacccu-001`  
**Pipeline:** `mainframe_modernization`  
**Purpose:** Map legacy artifacts through business rules, requirements, specification, and test cases  
**Last Updated:** 2025  

---

## 1. Legacy Artifact to Modern Component Mapping

### 1.1 Program and Transaction Mapping

| Legacy Artifact         | Legacy Type          | Modern Component                     | Modern Type                     | Mapping Rationale                     |
|-------------------------|----------------------|--------------------------------------|----------------------------------|---------------------------------------|
| `cobol/INQACCCU.cbl`   | COBOL CICS Program    | `CustomerAccountsController`         | Spring Boot REST Controller      | CICS transaction → REST endpoint      |
| `cobol/INQACCCU.cbl`   | CICS Online Inquiry    | `GET /api/v1/customers/{customerId}/accounts` | HTTP REST Endpoint               | Transaction processing → RESTful inquiry |
| `cobol/INQACCCU.cbl`   | COBOL Program Logic    | `AccountInquiryService`             | Spring Service Layer             | Business logic encapsulation           |

### 1.2 Copybook-to-DTO Mapping

| Legacy Copybook         | Legacy Structure      | Modern Java Class                   | Field Mapping                    | Notes                                  |
|-------------------------|----------------------|--------------------------------------|----------------------------------|----------------------------------------|
| `copybooks/INQACCCUZ.cpy` | Communication Area   | `CustomerAccountsRequest`           | CUSTOMER-NUMBER → customerId     | Input binding                          |
| `copybooks/INQACCCUZ.cpy` | Communication Area   | `CustomerAccountsResponse`          | CUSTOMER-FOUND → customerFound    | Output binding                         |
| `copybooks/INQACCCUZ.cpy` | Communication Area   | `CustomerAccountsResponse`          | NUMBER-OF-ACCOUNTS → numberOfAccounts | Array size bound (0–20)              |
| `copybooks/INQACCCUZ.cpy` | ACCOUNT-DETAILS (OCCURS 1 TO 20) | `AccountDetail[]`               | Repeating group → Java array      | Dynamic cardinality via `@Size(max=20)` |
| `copybooks/ACCOUNT.cpy`  | ACCOUNT-DATA structure | `AccountDetail`                    | Direct field mapping              | COBOL copybook → DTO                  |
| `copybooks/ACCOUNT.cpy`  | ACCOUNT-EYE-CATCHER   | `AccountDetail.eyeCatcher`        | PIC X(4) → String                | Validation: must equal "ACCT"         |
| `copybooks/ACCOUNT.cpy`  | ACCOUNT-CUST-NO       | `AccountDetail.customerNumber`    | PIC 9(10) → String               | Immutable, matches parent              |
| `copybooks/ACCOUNT.cpy`  | ACCOUNT-SORT-CODE     | `AccountDetail.sortCode`          | PIC 9(6) → String                | 6-digit numeric                        |
| `copybooks/ACCOUNT.cpy`  | ACCOUNT-NUMBER        | `AccountDetail.accountNumber`     | PIC 9(8) → String                | 8-digit numeric                        |
| `copybooks/ACCOUNT.cpy`  | ACCOUNT-TYPE          | `AccountDetail.accountType`       | PIC X(8) → String                | e.g., "CHECKING", "SAVINGS"           |
| `copybooks/ACCOUNT.cpy`  | ACCOUNT-INTEREST-RATE | `AccountDetail.interestRate`      | PIC 9(4)V99 → BigDecimal         | 2 decimal places (e.g., 3.45)         |
| `copybooks/ACCOUNT.cpy`  | ACCOUNT-OPENED        | `AccountDetail.accountOpened`     | PIC 9(8) → LocalDate             | Format YYYYMMDD                       |
| `copybooks/ACCOUNT.cpy`  | ACCOUNT-OVERDRAFT-LIMIT | `AccountDetail.overdraftLimit`   | PIC 9(8) → Long                  | Integer amount in cents               |
| `copybooks/ACCOUNT.cpy`  | ACCOUNT-LAST-STMT-DATE | `AccountDetail.lastStatementDate` | PIC 9(8) → LocalDate             | Format YYYYMMDD                       |
| `copybooks/ACCOUNT.cpy`  | ACCOUNT-NEXT-STMT-DATE | `AccountDetail.nextStatementDate` | PIC 9(8) → LocalDate             | Format YYYYMMDD                       |
| `copybooks/ACCOUNT.cpy`  | ACCOUNT-AVAILABLE-BALANCE | `AccountDetail.availableBalance` | PIC S9(10)V99 → BigDecimal       | Signed, 2 decimal places               |
| `copybooks/ACCOUNT.cpy`  | ACCOUNT-ACTUAL-BALANCE | `AccountDetail.actualBalance`     | PIC S9(10)V99 → BigDecimal       | Signed, 2 decimal places               |
| `copybooks/ACCDB2.cpy`   | SQL DECLARE ACCOUNT   | `AccountRepository`                | Mock repository interface         | POC in-memory; production adapter-ready |

### 1.3 Data Store Access Mapping

| Legacy Method            | Legacy Technology     | Modern Method                       | Modern Technology                | Migration Path                       |
|-------------------------|----------------------|--------------------------------------|----------------------------------|--------------------------------------|
| DLI Database Call       | CICS DLI             | `AccountRepository.findByCustomerId()` | Spring Data JPA (mock)          | Mock for POC; Spring Data adapters for production |
| DB2 SQL Query           | COBOL EXEC SQL       | Service-layer query delegation       | Spring Data repositories         | Repository abstraction layer         |
| No explicit caching     | Mainframe buffer pools | `@Cacheable` annotations            | Spring Cache Abstraction         | Future enhancement: Redis backing    |

---

## 2. Requirement to Spec to Test Traceability

### 2.1 Functional Requirements Traceability

| Requirement ID | Requirement Description                                           | Spec Reference                          | Spec ID     | Implementation Component                | Test Case ID |
|----------------|------------------------------------------------------------------|-----------------------------------------|-------------|-----------------------------------------|---------------|
| FR-001         | The system must retrieve account records associated with a given customer number. | 3.1 Retrieve Account Records            | SPEC-3.1    | `CustomerAccountsRequest.customerId`    | TC-001-001   |
| FR-001         | Accept 10-digit customer number                                   | 3.1 Input Validation                    | SPEC-3.1    | `CustomerAccountsRequest.customerId`    | TC-001-001   |
| FR-001         | Validate customer number format (numeric only)                   | 3.1 Input Validation                    | SPEC-3.1.1  | `@Pattern(regexp="[0-9]{10}")` on customerId | TC-001-002   |
| FR-002         | The system must return a success flag indicating whether the customer was found. | 3.1 Retrieve Account Records            | SPEC-3.1    | `CustomerAccountsResponse.customerFound` | TC-005-001   |
| FR-002         | Query associated accounts (0–20)                                 | 3.2 Account Retrieval                    | SPEC-3.2    | `AccountInquiryService.findAccountsByCustomerId()` | TC-002-001   |
| FR-002         | Return account details in response                                | 3.3 Response Payload                    | SPEC-3.3    | `CustomerAccountsResponse.accounts[]`   | TC-002-002   |
| FR-003         | Enforce OAuth2 authentication                                     | 4.1 Security – Authentication           | SPEC-4.1    | `SecurityConfig` bean, `@EnableResourceServer` | TC-003-001   |
| FR-003         | Validate JWT bearer token                                         | 4.1 Security – Authentication           | SPEC-4.1.1  | Spring Security `JwtDecoder` bean      | TC-003-002   |
| FR-004         | Enforce role-based access control (RBAC)                         | 4.2 Security – Authorization            | SPEC-4.2    | `@PreAuthorize("hasRole('ACCOUNT_INQUIRY')")` | TC-004-001   |
| FR-005         | Return `customerFound=true` if customer exists                   | 5.1 Success Response                    | SPEC-5.1    | `CustomerAccountsResponse.customerFound` | TC-005-001   |
| FR-005         | Return empty accounts array if no customer                        | 5.2 No-Accounts Response                | SPEC-5.2    | `CustomerAccountsResponse.accounts` (empty list) | TC-005-002   |
| FR-006         | Return HTTP 400 on invalid customer ID                            | 5.3 Error Responses                     | SPEC-5.3    | `@ExceptionHandler(MethodArgumentNotValidException.class)` | TC-006-001   |
| FR-007         | Return HTTP 401 on missing/invalid JWT                           | 5.4 Authentication Error                | SPEC-5.4    | Spring Security authentication entry point | TC-007-001   |
| FR-008         | Return HTTP 403 on insufficient role                             | 5.5 Authorization Error                 | SPEC-5.5    | Spring Security access denied handler   | TC-008-001   |
| FR-009         | Populate correlation ID in all logs                              | 6.1 Observability – Logging             | SPEC-6.1    | `MDC.put("correlationId", UUID)` in filter | TC-009-001   |
| FR-010         | Log request/response in structured JSON                          | 6.2 Observability – JSON Logging        | SPEC-6.2    | Logback `logstash-logback-encoder`     | TC-010-001   |
| FR-011         | Export Prometheus metrics                                         | 6.3 Observability – Metrics             | SPEC-6.3    | Micrometer `MeterRegistry` bean        | TC-011-001   |
| FR-012         | Support OpenTelemetry tracing hooks                               | 6.4 Observability – Tracing             | SPEC-6.4    | `io.opentelemetry:opentelemetry-api` instrumentation | TC-012-001   |

### 2.2 Non-Functional Requirements Traceability

| Requirement ID | Requirement Statement | Spec Section | Spec ID | Implementation Component | Test Case ID |
|----------------|-----------------------|--------------|---------|--------------------------|---------------|
| NFR-001        | All inputs strictly validated before processing | 3.1 Input Validation | SPEC-3.1 | Bean Validation (`@Valid`, `@NotBlank`, `@Pattern`) | TC-NFR-001 |
| NFR-002        | Error responses in standardized JSON structure | 5.0 Response Format | SPEC-5.0 | `ApiErrorResponse` DTO | TC-NFR-002 |
| NFR-003        | TLS 1.2+ transport encryption | 4.3 Transport Security | SPEC-4.3 | Spring Boot server.ssl.enabled, keystore config | TC-NFR-003 |
| NFR-004        | Secrets never committed to source control | 4.4 Secrets Management | SPEC-4.4 | Environment variables, Spring Cloud Config | TC-NFR-004 |
| NFR-005        | No live CICS/DB2 connection in POC | 2.0 Scope | SPEC-2.0 | Mock `AccountRepository` implementation | TC-NFR-005 |
| NFR-006        | Request latency < 200ms (p95) | 6.3 Performance | SPEC-6.3 | Micrometer timer on endpoint | TC-NFR-006 |
| NFR-007        | Error rate < 1% in steady state | 6.3 Performance | SPEC-6.3 | Prometheus alert rules | TC-NFR-007 |
| NFR-008        | Support up to 100 concurrent requests | 6.3 Scalability | SPEC-6.3 | Load testing via JMeter | TC-NFR-008 |
| NFR-009        | Database response time tracked | 6.3 Performance | SPEC-6.3 | Repository layer metrics instrumentation | TC-NFR-009 |

---

## 3. Rule-to-Test Coverage Indicators

### 3.1 Business Rule Traceability

| Rule ID | Rule Description                                                                 | Test Case ID |
|---------|----------------------------------------------------------------------------------|---------------|
| BR-001  | The system must retrieve account records associated with a given customer number. | TC-001-001   |
| BR-002  | The system must return a success flag indicating whether the customer was found.  | TC-005-001   |
| BR-003  | The system must validate the format of the customer number.                      | TC-001-002   |
| BR-004  | The system must ensure that all data returned to the client is sanitized.        | TC-004       |

---

## 4. Test Case Coverage Map

### 4.1 Unit Test Coverage (Spring Boot Backend)

| Test Case ID | Test Name | Related Rule(s) | Related Requirement(s) | Class Under Test | Assertion(s) | Status |
|---------------|-----------|------------------|------------------------|------------------|---------------|--------|
| TC-001-001    | Valid 10-digit customer ID accepted | BR-001 | FR-001 | `CustomerAccountsRequest` | `@NotBlank`, `@Pattern` validation passes | ✓ READY |
| TC-001-002    | Non-numeric customer ID rejected | BR-003 | FR-001 | `CustomerAccountsRequest` | `ConstraintViolationException` raised | ✓ READY |
| TC-002-001    | findAccountsByCustomerId returns list | BR-002 | FR-002 | `AccountInquiryService` | `List<AccountDetail>` not null, size ≤ 20 | ✓ READY |
| TC-002-002    | Response payload contains all required fields | BR-006 | FR-002 | `CustomerAccountsResponse` | `eyeCatcher`, `accountNumber`, `sortCode`, `interestRate`, `balances` present | ✓ READY |
| TC-003-001    | JWT bearer token required for access | BR-008 | FR-003 | `SecurityConfig` | 401 Unauthorized without token | ✓ READY |
| TC-003-002    | Invalid JWT rejected | BR-008 | FR-003 | `JwtDecoder` | `JwtException` raised | ✓ READY |
| TC-004-001    | ACCOUNT_INQUIRY role required | BR-009 | FR-004 | `AccountInquiryController` | 403 Forbidden without role | ✓ READY |
| TC-005-001    | customerFound=true when customer exists | BR-001 | FR-005 | `CustomerAccountsResponse` | `customerFound` == true | ✓ READY |
| TC-005-002    | Empty accounts array when customer not found | BR-001 | FR-005 | `CustomerAccountsResponse` | `accounts.size()` == 0, `customerFound` == false | ✓ READY |
| TC-006-001    | 400 Bad Request on invalid input | BR-003, BR-005 | FR-006 | `GlobalExceptionHandler` | HTTP 400, error message in body | ✓ READY |
| TC-007-001    | 401 Unauthorized on missing JWT | BR-008 | FR-007 | `AuthenticationEntryPoint` | HTTP 401, `WWW-Authenticate` header | ✓ READY |
| TC-008-001    | 403 Forbidden on insufficient role | BR-009 | FR-008 | `AccountInquiryController` | HTTP 403, error message in body | ✓ READY |