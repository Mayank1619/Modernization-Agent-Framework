# qa-review-checklist.md

**Document ID:** `qa-review-checklist-inqacccu-001`  
**Pipeline:** `mainframe_modernization`  
**Target System:** INQACCCU Customer Account Inquiry REST API  
**Generated:** 2025  
**Status:** Implementation-Ready  

---

## 1. Requirement Coverage Verification

### 1.1 Functional Requirements Checklist

| REQ ID | Requirement Title | Artifact Source | Verification Method | Status | Notes |
|--------|-------------------|-----------------|---------------------|--------|-------|
| REQ-FUNC-001 | Accept 10-digit customer number via REST endpoint | spec.md, intended-system.md | Unit test + Integration test | ⚠️ PLANNED | Validate path parameter binding, numeric constraint enforcement |
| REQ-FUNC-002 | Return 0–20 account records for valid customer | spec.md, business-rules.md (BR001) | Integration test + Mock repository verification | ⚠️ PLANNED | Confirm array size bounds; test boundary cases (0, 1, 20 accounts) |
| REQ-FUNC-003 | Return account details: account number, sort code, balance, interest rate, statement date | spec.md, mapping-matrix.md | Schema validation test against OpenAPI 3.0.3 | ⚠️ PLANNED | Verify JSON payload matches `AccountDetail` DTO structure |
| REQ-FUNC-004 | Return customer not found indicator (`customerFound: false`, `numberOfAccounts: 0`) | spec.md, business-rules.md (BR001) | Unit test: invalid customer lookup | ⚠️ PLANNED | Test with non-existent customer ID; confirm error semantics preserved |
| REQ-FUNC-005 | Preserve legacy observable behavior as default path | intended-system.md, plan.md | Regression test against legacy COBOL output samples | ⚠️ PLANNED | Compare REST JSON response with equivalent legacy CICS output |
| REQ-ARCH-001 | Backend Stack: Java 21, Spring Boot 3.3.x, Maven 3.9+ | system-intent.md, plan.md | Build artifact verification; JVM version check | ⚠️ PLANNED | Confirm POM declares correct versions; verify Maven 3.9+ used |
| REQ-ARCH-002 | Frontend Stack: React 18.x, TypeScript 5.x, Vite 5.x, Node.js 20 LTS | system-intent.md | package.json version audit | ⚠️ PLANNED | Lock dependency versions; verify Node 20 in CI/CD environment |
| REQ-SEC-001 | OAuth2 Resource Server with JWT bearer token validation | spec.md, business-rules.md (BR005) | Security integration test; token format validation | ⚠️ PLANNED | Test valid/invalid/expired JWT; verify `@Secured` annotations on endpoints |
| REQ-SEC-002 | Role-based access control (RBAC) for customer-account endpoints | spec.md, business-rules.md (BR005) | Authorization test matrix (multiple roles) | ⚠️ PLANNED | Verify insufficient role returns `403 Forbidden`; admin role returns `200 OK` |
| REQ-SEC-003 | Input validation: strict 10-digit customer number format | spec.md, business-rules.md (BR003) | Boundary test: non-numeric, length != 10, null, empty string | ⚠️ PLANNED | Confirm `400 Bad Request` for each invalid case |
| REQ-SEC-004 | TLS 1.2+ transport security | system-intent.md | SSL/TLS configuration audit; security headers validation | ⚠️ PLANNED | Verify `Strict-Transport-Security`, `X-Content-Type-Options` headers present |
| REQ-SEC-005 | Secrets handling via environment variables or secret manager | system-intent.md, business-rules.md (BR006) | Secret injection test; source code audit for hardcoded values | ⚠️ PLANNED | Verify no credentials in `application.properties`, POM, or source files |
| REQ-OBS-001 | Structured JSON logging with correlation ID per request | spec.md, requirements.md (NFR-007) | Log output format validation; MDC correlation ID propagation test | ⚠️ PLANNED | Parse logs as JSON; verify `correlationId` field present and unique per request |
| REQ-OBS-002 | OpenTelemetry-ready tracing instrumentation | spec.md, requirements.md (NFR-009) | Trace exporter configuration test; span creation verification | ⚠️ PLANNED | Confirm `spring-boot-starter-actuator` and OpenTelemetry SDK configured |
| REQ-PERSIST-001 | Mock repository layer for POC (no live DB2 or CICS) | intended-system.md, tasks.md (TASK-002) | Mock data verification; repository interface test | ⚠️ PLANNED | Verify `@Repository` marked as `@Mock` or in-memory implementation |
| REQ-API-001 | REST API conforms to OpenAPI 3.0.3 specification | openapi.yaml, spec.md | OpenAPI validator test; Swagger UI schema generation | ⚠️ PLANNED | Run Swagger Codegen validation; verify all endpoints and models documented |

---

### 1.2 Non-Functional Requirements Checklist

| NFR ID | NFR Title | Acceptance Criteria | Verification Method | Status | Notes |
|--------|-----------|---------------------|---------------------|--------|-------|
| NFR-001 | Performance: Response time ≤ 200ms (p95) for customer inquiry | Latency measurement under normal load | Load test: 100 concurrent requests; measure p95 latency | ⚠️ PLANNED | Use JMeter or Gatling; establish baseline after Phase 1 |
| NFR-002 | Availability: 99.9% uptime SLA in production | Uptime monitoring and incident tracking | Synthetic monitoring; track downtime minutes per month | ⚠️ PLANNED | Configure health check endpoint; integrate with monitoring platform |
| NFR-003 | Scalability: Horizontal scaling via container orchestration | Auto-scaling policy definition | Kubernetes deployment test; verify pod replica scaling | ⚠️ PLANNED | Test HPA trigger thresholds (CPU, memory); confirm stateless design |
| NFR-004 | Data Consistency: Account list returned is point-in-time snapshot | Transactional query semantics | Mock repository transaction test; verify snapshot isolation | ⚠️ PLANNED | Confirm no phantom reads; document consistency model |
| NFR-005 | Backward Compatibility: API versioning strategy (v1 baseline) | URL path includes version; deprecation headers | Versioning test: v1 and v2 endpoints coexist; verify deprecation warning | ⚠️ PLANNED | Add `Deprecated: true` in OpenAPI spec for deprecated endpoints |
| NFR-006 | Security: No sensitive data (passwords, tokens, PII) in logs | Log sanitization configuration | Log content audit; verify masking filters applied | ⚠️ PLANNED | Use Logback regex filter to redact PII; test with sample customer data |
| NFR-007 | Observability: Structured JSON logging with correlation ID | All logs include ISO 8601 timestamp, level, logger name, message, correlation ID | Log parser validation; JSON schema compliance test | ⚠️ PLANNED | Verify Logstash compatibility; test with ELK stack |
| NFR-008 | Metrics: Prometheus-compatible metrics export | Metrics endpoint at `/actuator/metrics`; latency, error rate, custom metrics | Metrics scrape test; Prometheus YAML validation | ⚠️ PLANNED | Verify histogram buckets and gauge registrations |
| NFR-009 | Tracing: OpenTelemetry instrumentation ready | Spans exported via OTLP or compatible exporter; trace propagation across services | Trace verification test; Jaeger/Zipkin UI inspection | ⚠️ PLANNED | Configure OTEL_EXPORTER_OTLP_ENDPOINT; test trace sampling rate |
| NFR-010 | Correlation ID: UUID v4 format; propagated to downstream calls | Correlation ID header format validation; header propagation across services | Header propagation test; downstream system log correlation | ⚠️ PLANNED | Verify `X-Correlation-ID` header preserved in outbound HTTP calls |
| NFR-011 | Error Handling: Standardized JSON error response structure | All errors return `{ code, message, details, correlationId }` | Error response schema validation test | ⚠️ PLANNED | Test error scenarios: 400, 401, 403, 404, 500; verify JSON compliance |
| NFR-012 | Accessibility (Frontend): WCAG 2.1 AA compliance | React UI component accessibility audit | Axe accessibility test; keyboard navigation verification | ⚠️ PLANNED | Automate accessibility scanning in CI/CD; manual screen reader testing |
| NFR-013 | Code Quality: Minimum 80% code coverage for backend | JUnit 5 test suite coverage report | Jacoco coverage report generation and validation | ⚠️ PLANNED | Set Maven build failure gate at < 80% coverage |
| NFR-014 | Documentation: API documentation auto-generated from OpenAPI | Swagger UI available at `/swagger-ui.html` | Swagger UI endpoint availability test | ⚠️ PLANNED | Verify Spring Doc integration; test endpoint discovery |

---

## 2. Business Rule-to-Test Coverage Matrix

### 2.1 Business Rule Verification

| BR ID | Business Rule | Trigger Condition | Expected Output | Test Type | Test Case ID | Status | Notes |
|-------|---------------|--------------------|-----------------|-----------|--------------|--------|-------|
| BR001 | Customer Inquiry Acceptance Rule | Valid 10-digit customer number | CUSTOMER-FOUND = 'Y'; NUMBER-OF-ACCOUNTS = 0–20; ACCOUNT-DETAILS array | Unit + Integration | TC-BR001-001 | ⚠️ PLANNED | Test with customer ID `0123456789` (valid); verify `customerFound: true` |
| BR001 | Customer Inquiry Acceptance Rule | Invalid/missing customer number | CUSTOMER-FOUND = 'N'; NUMBER-OF-ACCOUNTS = 0 | Unit | TC-BR001-002 | ⚠️ PLANNED | Test with `null`, empty string, non-numeric, length != 10 |
| BR002 | Account Balance Retrieval Rule | Valid customer with N accounts (0 ≤ N ≤ 20) | Return all N account records with complete details | Integration | TC-BR002-001 | ⚠️ PLANNED | Test edge cases: 0 accounts, 1 account, 20 accounts (boundary) |
| BR002 | Account Balance Retrieval Rule | Valid customer with > 20 accounts | Return only first 20 accounts; log warning | Integration | TC-BR002-002 | ⚠️ PLANNED | Mock repository to return 25 accounts; verify truncation to 20 |
| BR003 | Input Validation Strictness Rule | Non-numeric customer ID | Return `400 Bad Request` with error message | Unit | TC-BR003-001 | ⚠️ PLANNED | Test with `ABC1234567`, `012345678A` |
| BR003 | Input Validation Strictness Rule | Customer ID length != 10 | Return `400 Bad Request` | Unit | TC-BR003-002 | ⚠️ PLANNED | Test lengths: 9, 11 digits |
| BR003 | Input Validation Strictness Rule | Leading/trailing whitespace in customer ID | Reject input; no padding/trimming | Unit | TC-BR003-003 | ⚠️ PLANNED | Verify strictness: legacy COBOL-like padding behavior NOT applied |
| BR004 | Account Status Preservation Rule | Query returns all account statuses (Active, Inactive, Closed) | Return all accounts regardless of status | Integration | TC-BR004-001 | ⚠️ PLANNED | Mock repository returns mixed status accounts; verify all returned |
| BR005 | OAuth2 Authorization Rule | Valid JWT with required role | Allow request; return `200 OK` with account data | Integration | TC-BR005-001 | ⚠️ PLANNED | Test with valid JWT issued by test OAuth2 provider |
| BR005 | OAuth2 Authorization Rule | Valid JWT with insufficient role | Deny request; return `403 Forbidden` | Integration | TC-BR005-002 | ⚠️ PLANNED | Test with valid JWT but missing `customer-inquirer` role |
| BR005 | OAuth2 Authorization Rule | Missing or invalid JWT | Deny request; return `401 Unauthorized` | Unit | TC-BR005-003 | ⚠️ PLANNED | Test with no Authorization header, invalid token, expired token |
| BR006 | Secrets Handling Rule | Database credentials required at startup | Secrets injected via environment variable or secret manager; never hardcoded | Unit | TC-BR006-001 | ⚠️ PLANNED | Source code audit: grep for password patterns; CI/CD secret scanner |
| BR006 | Secrets Handling Rule | Missing required secret at startup | Application fails to start; logs clear error message (no secret leak in logs) | Unit | TC-BR006-002 | ⚠️ PLANNED | Set missing env var; verify startup error; audit log for credential exposure |

---

## 3. Data Mapping Validation Checklist

### 3.1 Legacy-to-Modern Data Structure Mapping

| Legacy Copybook | Legacy Field | Type/Length | Modern Java DTO | Modern Type | Mapping Test | Status | Notes |
|-----------------|--------------|-------------|-----------------|-------------|--------------|--------|-------|
| INQACCCUZ.cpy | CUSTOMER-NUMBER | PIC 9(10) | `CustomerAccountsResponse.customerId` | `String` | String format; no leading zeros lost | ⚠️ PLANNED | Test: `0000000001` → `"0000000001"` (preserve zeros) |
| INQACCCUZ.cpy | CUSTOMER-FOUND | PIC X ('Y'/'N') | `CustomerAccountsResponse.customerFound` | `Boolean` | Y → true; N → false | ⚠️ PLANNED | Test both Y and N cases |
| INQACCCUZ.cpy | NUMBER-OF-ACCOUNTS | S9(8) BINARY | `CustomerAccountsResponse.numberOfAccounts` | `Integer` | Range: 0–20 (validate upper bound) | ⚠️ PLANNED | Test boundary: 0, 1, 20; reject > 20 |
| ACCOUNT.cpy | ACCOUNT-NUMBER | PIC 9(8) | `AccountDetail.accountNumber` | `String` | Preserve leading zeros | ⚠️ PLANNED | Test: `00012345` → `"00012345"` |
| ACCOUNT.cpy | SORT-CODE | PIC 9(6) | `AccountDetail.sortCode` | `String` | Numeric string, no transformation | ⚠️ PLANNED | Test: `123456` → `"123456"` |
| ACCOUNT.cpy | ACCOUNT-BALANCE | PIC S9(13)V99 COMP-3 | `AccountDetail.balance` | `BigDecimal` | Preserve precision; scale = 2 | ⚠️ PLANNED | Test: `1234567890123.45` maintains 2 decimal places |
| ACCOUNT.cpy | INTEREST-RATE | PIC 9(3)V99 COMP-3 | `AccountDetail.interestRate` | `BigDecimal` | Preserve scale; scale = 2 | ⚠️ PLANNED | Test: `5.25` → `5.25` |
| ACCOUNT.cpy | STATEMENT-DATE | PIC 9(8) (YYYYMMDD) | `AccountDetail.statementDate` | `LocalDate` | ISO 8601 format in JSON | ⚠️ PLANNED | Test: `20250115` → `"2025-01-15"` |
| ACCOUNT.cpy | ACCOUNT-STATUS | PIC X(8) | `AccountDetail.status` | `String` (enum: ACTIVE, INACTIVE, CLOSED) | Case normalization | ⚠️ PLANNED | Test: `ACTIVE  ` (with padding) → `"ACTIVE"` |
| ACCDB2.cpy | EYE-CATCHER | PIC X(4) ('ACCT') | `AccountDetail.eyeCatcher` | `String` | Literal value validation |