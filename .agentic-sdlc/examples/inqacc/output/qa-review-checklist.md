# QA Review Checklist & Report Skeleton

**Document ID:** `qa-review-checklist.md`  
**Pipeline:** mainframe_modernization  
**Authority:** system-intent.md + intended-system.md + business-rules.md + requirements.md + spec.md + program-analysis.md + mapping-matrix.md + plan.md + tasks.md + test-spec.md + traceability-matrix.md + openapi.yaml + copilot-build-prompt.md  
**Status:** QA verification framework for implementation artifacts  
**Generated:** 2024  
**Target Stack:** Java 21 + Spring Boot 3.3.x | React 18.x + TypeScript 5.x + Vite 5.x | Mock Repository (POC)

---

## 1. QA Review Scope and Objectives

### 1.1 Scope

This checklist provides structured verification of all generated artifacts and implementation increments against:

- **Requirement coverage:** All functional and non-functional requirements allocated to code artifacts
- **Rule-to-test traceability:** Every business rule has explicit test coverage (unit, integration, or E2E)
- **Data mapping validation:** Field transformation from legacy COBOL/DB2 to modern Java/JSON matches program analysis
- **Non-functional verification:** Security, performance, observability, and deployment readiness
- **API contract compliance:** Implementation adheres to OpenAPI 3.0.3 specification
- **Legacy parity:** Modernized behavior preserves legacy observable semantics (composite-key lookup, error codes, field ordering)

### 1.2 Review Objectives

| Objective | Success Criteria | Owner |
|-----------|-----------------|-------|
| **Requirement Traceability** | 100% of FR, NFR, and business rules have explicit test cases; traceability matrix 100% populated | QA Lead |
| **Test Coverage** | ≥85% line coverage (unit + integration); all 47+ test cases from test-spec.md implemented and passing | QA + Backend Dev |
| **Legacy Parity** | Field mapping, composite-key semantics, error handling match program-analysis.md findings; cross-ref validation performed | QA + Architecture |
| **API Contract** | Implementation matches OpenAPI 3.0.3 spec (paths, params, status codes, error envelope); contract tests passing | QA + Backend Dev |
| **Security Baseline** | OAuth2 authentication enforced; role-based access control (ACCOUNT_INQUIRER) verified; no hardcoded secrets; TLS validation | Security + QA |
| **Observability** | Structured JSON logging present; correlation ID propagation verified; metrics instrumentation in place | QA + Ops |
| **Deployment Readiness** | Docker image builds; Maven/npm builds reproducible; environment configuration externalized; no build failures | DevOps + QA |

### 1.3 Review Phases

| Phase | Artifact Type | Primary Verifier | Duration | Gate Criteria |
|-------|---------------|------------------|----------|---------------|
| **Phase 1A** | OpenAPI 3.0.3 Specification | Architecture + API Team | Week 1–2 | Contract stability, security scheme definition, error envelope consistency, no breaking changes without governance |
| **Phase 1B** | Build Configuration & Security Baseline | DevOps + Security | Week 2–4 | Maven/Node.js build reproducibility, OAuth2 adapter presence, TLS configuration, secrets externalized |
| **Phase 2A** | Spring Boot Service Layer | Backend Dev + QA | Week 5–6 | Requirement coverage mapping, business rule implementation, unit test execution (≥90% coverage), no critical code review findings |
| **Phase 2B** | Mock Repository & Data Access Layer | Backend Dev + QA | Week 6–8 | Data mapping accuracy (COBOL↔Java↔JSON), SQL semantics preservation, exception handling, integration tests (≥85% coverage) |
| **Phase 3A** | REST Controller & Integration Tests | Backend Dev + QA | Week 8–10 | HTTP contract validation (path params, headers, status codes), authentication flow verification, E2E scenarios passing |
| **Phase 3B** | React Frontend & E2E Tests | Frontend Dev + QA | Week 11–14 | UI rendering, API integration, error handling, accessibility baseline, E2E test suite (100% passing) |
| **Phase 4** | Deployment Artifacts & Operationalization | DevOps + Security + QA | Week 15–20 | Docker image security scan, performance baseline established, operational runbook validated, UAT readiness |

---

## 2. Requirement Coverage Verification

### 2.1 Functional Requirement Checklist

**REQ-CHECK-FR-001: Execute Account Lookup by Composite Key**

- [ ] Requirement FR-001 statement clearly defined in requirements.md
- [ ] Business rule BR-001 (Account Record Lookup by Composite Key) explicitly maps to FR-001
- [ ] OpenAPI specification includes GET `/v1/accounts/{sortcode}/{accountNumber}` endpoint (openapi.yaml)
- [ ] Path parameters documented with format constraints (pattern: `^\d{6}$` for sortcode, `^\d{8}$` for account number)
- [ ] Spring Boot controller method `getAccountBySortcodeAndNumber()` or equivalent implemented
- [ ] Service layer implements `AccountInquiryService.inquireAccount(String sortcode, String accountNumber)`
- [ ] Repository layer implements `findBySortcodeAndNumber(String sortcode, String accountNumber)` query
- [ ] Mock data repository contains ≥5 representative account test records
- [ ] Unit test case TC-001 (happy path: valid sortcode + account number → account retrieved) implemented and passing
- [ ] Unit test case TC-002 (account not found → returns empty/null) implemented and passing
- [ ] Unit test case TC-003 (DB/repository error → exception propagated) implemented and passing
- [ ] Integration test case TC-027 (end-to-end REST call with valid credentials) implemented and passing
- [ ] Legacy parity validation: field ordering and content match COBOL INQACC.cbl expected output
- [ ] Correlation ID attached to request and visible in structured logs
- [ ] All error conditions (ERR-001 through ERR-008) mapped to corresponding HTTP status codes

**Status:** [ ] Pass [ ] Fail [ ] Blocked  
**Verifier:** ________________  
**Date:** ________

---

**REQ-CHECK-FR-002: Validate Sortcode Format (6 Numeric Digits)**

- [ ] Requirement FR-002 statement clearly defined in requirements.md
- [ ] Business rule BR-002 (Sortcode Format Validation) explicitly maps to FR-002
- [ ] OpenAPI specification path parameter includes pattern constraint `^\d{6}$`
- [ ] Service layer implements `validateSortcode(String sortcode)` method
- [ ] Validation rejects non-numeric characters (letters, special chars, spaces)
- [ ] Validation rejects sortcodes shorter than 6 digits
- [ ] Validation rejects sortcodes longer than 6 digits
- [ ] Validation rejects empty or null sortcode (returns HTTP 400)
- [ ] Unit test case TC-004 (invalid sortcode: non-numeric) implemented and passing
- [ ] Unit test case TC-005 (invalid sortcode: wrong length) implemented and passing
- [ ] Integration test case TC-008 (HTTP 400 returned for invalid sortcode) implemented and passing
- [ ] Error envelope includes validation error code (e.g., `INVALID_SORTCODE_FORMAT`) and user-readable message
- [ ] Correlation ID present in error response

**Status:** [ ] Pass [ ] Fail [ ] Blocked  
**Verifier:** ________________  
**Date:** ________

---

**REQ-CHECK-FR-003: Validate Account Number Format (8 Numeric Digits)**

- [ ] Requirement FR-003 statement clearly defined in requirements.md
- [ ] Business rule BR-003 (Account Number Format Validation) explicitly maps to FR-003
- [ ] OpenAPI specification path parameter includes pattern constraint `^\d{8}$`
- [ ] Service layer implements `validateAccountNumber(String accountNumber)` method
- [ ] Validation rejects non-numeric characters (letters, special chars, spaces)
- [ ] Validation rejects account numbers shorter than 8 digits
- [ ] Validation rejects account numbers longer than 8 digits
- [ ] Validation rejects empty or null account number (returns HTTP 400)
- [ ] Unit test case TC-006 (invalid account number: non-numeric) implemented and passing
- [ ] Unit test case TC-007 (invalid account number: wrong length) implemented and passing
- [ ] Integration test case TC-009 (HTTP 400 returned for invalid account number) implemented and passing
- [ ] Error envelope includes validation error code (e.g., `INVALID_ACCOUNT_NUMBER_FORMAT`) and user-readable message
- [ ] Correlation ID present in error response

**Status:** [ ] Pass [ ] Fail [ ] Blocked  
**Verifier:** ________________  
**Date:** ________

---

**REQ-CHECK-FR-004: Return HTTP 400 Bad Request for Invalid Input**

- [ ] Requirement FR-004 statement clearly defined in requirements.md
- [ ] OpenAPI specification defines 400 response with error envelope schema
- [ ] Error envelope includes: `errorCode`, `errorMessage`, `correlationId`, `timestamp`, `path`
- [ ] HTTP status line is exactly 400 Bad Request (not 422, 406, etc.)
- [ ] Response Content-Type is `application/json`
- [ ] Error codes are consistent across all validation failures (INVALID_SORTCODE_FORMAT, INVALID_ACCOUNT_NUMBER_FORMAT, etc.)
- [ ] Integration test case TC-008 (sortcode validation failure → 400) passing
- [ ] Integration test case TC-009 (account number validation failure → 400) passing
- [ ] User-readable error message provided (not stack trace)
- [ ] Correlation ID included in error response header and body

**Status:** [ ] Pass [ ] Fail [ ] Blocked  
**Verifier:** ________________  
**Date:** ________

---

**REQ-CHECK-FR-005: Return HTTP 404 Not Found for No Match**

- [ ] Requirement FR-005 statement clearly defined in requirements.md
- [ ] Business rule BR-001 includes "Return not-found condition if no match exists" processing step
- [ ] OpenAPI specification defines 404 response with error envelope schema
- [ ] HTTP status line is exactly 404 Not Found
- [ ] Response Content-Type is `application/json`
- [ ] Error envelope includes: `errorCode` (ACCOUNT_NOT_FOUND), `errorMessage`, `correlationId`, `timestamp`, `path`
- [ ] Service layer returns empty Optional or throws AccountNotFoundException
- [ ] Controller catches AccountNotFoundException and translates to HTTP 404 response
- [ ] Unit test case TC-002 (account not found in repository) implemented and passing
- [ ] Integration test case TC-010 (HTTP 404 returned for no matching account) implemented and passing
- [ ] Correlation ID present in error response

**Status:** [ ] Pass [ ] Fail [ ] Blocked  
**Verifier:** ________________  
**Date:** ________

---

**REQ-CHECK-FR-006: Return HTTP 401 Unauthorized for Missing/Invalid Token**

- [ ] Requirement FR-006 statement clearly defined in requirements.md
- [ ] Business rule BR-004 (Authentication and Authorization) explicitly maps to FR-006
- [ ] OpenAPI specification defines 401 response with error envelope schema
- [ ] HTTP status line is exactly 401 Unauthorized
- [ ] Response includes `WWW-Authenticate` header with scheme `Bearer realm="INQACC"`
- [ ] Spring Security OAuth2 Resource Server configured with JWT validation
- [ ] Missing Authorization header triggers 401 (not 403)
- [ ] Malformed Authorization header (e.g., missing "Bearer" prefix) triggers 401
- [ ] Expired JWT token triggers 401
- [ ] Invalid JWT signature triggers 401
- [ ] Error envelope includes: `errorCode` (AUTHENTICATION_FAILED), `errorMessage`, `correlationId`
- [ ] Integration test case TC-011 (missing token → 401) implemented and passing
- [ ] Integration test case TC-012 (invalid token → 401) implemented and passing
- [ ] Correlation ID present in error response

**Status:** [ ] Pass [ ] Fail [ ] Blocked  
**Verifier:** ________________  
**Date:** ________

---

**REQ-CHECK-FR-007: Return HTTP 403 Forbidden for Insufficient Role**

- [ ] Requirement FR-007 statement clearly defined in requirements.md
- [ ] Business rule BR-004 includes role-based authorization (ACCOUNT_INQUIRER role required)
- [ ] OpenAPI specification defines 403 response with error envelope schema
- [ ] HTTP status line is exactly 403 Forbidden
- [ ] Spring Security `@PreAuthorize("hasRole('ACCOUNT_INQUIRER')")` annotation on controller method
- [ ] User with valid JWT but lacking ACCOUNT_INQUIRER role receives 403
- [ ] Error envelope includes: `errorCode` (INSUFFICIENT_PRIVILEGES), `errorMessage`, `correlationId`
- [ ] Integration test case TC-013 (valid token, wrong role → 403) implemented and passing
- [ ] Correlation ID present in error response
- [ ] Role validation occurs before service layer invocation

**Status:** [ ] Pass [ ] Fail [ ] Blocked  
**Verifier:** ________________  
**Date:** ________

---

**REQ-CHECK-FR-008: Return Standardized Account Record JSON**

- [ ] Requirement FR-008 statement clearly defined in requirements.md
- [ ] OpenAPI specification defines 200 response with AccountResponseDto schema
- [ ] HTTP status line is exactly 200 OK
- [ ] Response Content-Type is `application/json; charset=utf-8`
- [ ] All 12 ACCOUNT table fields mapped to JSON properties (per program-analysis.md, ACCDB2.cpy)
- [ ] Field names match OpenAPI schema (e.g., `sortcode`, `accountNumber`, `accountType`, `accountStatus`, `balance`, `currency`, `openDate`, `closeDate`, `accountHolder`, `sortcodeReference`, `accountTypeReference`, `lastUpdated`)
- [ ] Field order in JSON response consistent with OpenAPI specification
- [ ] All field data types match specification (string, number, date, boolean, etc.)
- [ ] No null fields unless explicitly optional in specification
- [ ] Unit test case TC-001 (happy path response structure) implemented and passing
- [ ] Integration test case TC-027 (full E2E response validation) implemented and passing
- [ ] Legacy parity: JSON structure preserves COBOL field semantics and content
- [ ] Date fields formatted as ISO 8601 (YYYY-MM-DD)
- [ ] Numeric fields (balance, references) preserve precision and decimal places
- [ ] Correlation ID included in response header `X-Correlation-ID`

**Status:** [ ] Pass [ ] Fail [ ] Blocked  
**Verifier:** ________________  
**Date:** ________

---

### 2.2 Non-Functional Requirement Checklist

**REQ-CHECK-NFR-001: OAuth2 Bearer Token Authentication**

- [ ] NFR-001 statement clearly defined in requirements.md
- [ ] Business rule BR-004 explicitly covers authentication mechanism
- [ ] Spring Security OAuth2 Resource Server dependency present in pom.xml
- [ ] `spring.security.oauth2.resourceserver.jwt.issuer-uri` configured in application.properties
- [ ] `spring.security.oauth2.resourceserver.jwt.jwk-set-uri` configured
- [ ] JWT token validation enabled with public key verification
- [ ] Bearer token extraction from Authorization header implemented
- [ ] @PreAuthorize annotations on all protected endpoints
- [ ] Integration test validates JWT token acceptance and rejection
- [ ] OpenAPI specification includes OAuth2 security scheme
- [ ] No hardcoded credentials in source code

**Status:** [ ] Pass [ ] Fail [ ] Blocked  
**Verifier:** ________________  
**Date:** ________

---

**REQ-CHECK-NFR-002: Role-Based Access Control (ACCOUNT_INQUIRER)**

- [ ] NFR-002 statement clearly defined in requirements.md
- [ ] Business rule BR-004 includes role-based authorization requirement
- [ ] Spring Security role mapper configured to recognize ACCOUNT_INQUIRER role
- [ ] @PreAuthorize("hasRole('ACCOUNT_INQUIRER')") annotation present on account inquiry endpoint
- [ ] Test data includes JWT tokens with and without ACCOUNT_INQUIRER role
- [ ] Integration test TC-013 validates role-based rejection (403 Forbidden)
- [ ] Integration test validates successful access with ACCOUNT_INQUIRER role
- [ ] Role is extracted from JWT claims (e.g., `realm_access.roles` or `roles` claim)
- [ ] No hardcoded role allowlists in code (roles from JWT only)

**Status:** [ ] Pass [ ] Fail [ ]