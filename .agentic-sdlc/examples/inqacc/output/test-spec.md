```markdown
# Test Specification for INQACC Modernization

**Document ID:** `test-spec.md`  
**Pipeline:** mainframe_modernization  
**Authority:** system-intent.md + intended-system.md + business-rules.md + requirements.md + spec.md + program-analysis.md + mapping-matrix.md + plan.md + tasks.md + traceability-matrix.md  
**Status:** Implementation-ready test specification  
**Generated:** 2024  
**Target Stack:** Java 21 + Spring Boot 3.3.x + React 18.x + TypeScript 5.x + Vite 5.x + Mock Repository (POC)

---

## 1. Test Strategy and Coverage Framework

### 1.1 Test Scope

**In Scope:**
- Unit tests for service layer (account inquiry, validation, error translation)
- Unit tests for data access layer (repository, entity mapping, mock persistence)
- Unit tests for HTTP controllers and request/response binding
- Integration tests for Spring Boot REST endpoint, OAuth2 authentication, role-based authorization
- Contract tests for OpenAPI 3.0.3 specification compliance and HTTP semantics
- Boundary and negative scenario testing for input validation and error handling paths
- Legacy parity tests to verify modernized behavior matches COBOL/DB2 semantics from INQACC.cbl
- Modernization enhancement tests for new capabilities (OAuth2 bearer tokens, structured JSON logging, correlation ID propagation)
- Performance baseline tests for response latency under expected load
- React component tests (TypeScript + React Testing Library) for UI rendering and API integration
- E2E tests for complete workflow (authentication → inquiry → display result)

**Out of Scope:**
- Live CICS transaction server integration testing
- Live DB2 mainframe database connectivity testing
- Account modification, creation, or deletion workflows
- Batch account inquiry or multi-account bulk operations
- Load testing beyond baseline performance expectations (handled in separate performance test plan)
- Real mainframe system monitoring or health check testing
- Production deployment validation (handled in operational readiness checklist)

### 1.2 Test Pyramid and Coverage Distribution

```
        ┌──────────────────────────────────────┐
        │  E2E / Contract Tests                │  5–10%
        │  (Browser + Backend API)             │  (3–5 test cases)
        ├──────────────────────────────────────┤
        │  Integration Tests                   │  20–30%
        │  (Spring Boot + Mock Repository)     │  (8–12 test cases)
        ├──────────────────────────────────────┤
        │  Unit Tests                          │  60–75%
        │  (Service, DAO, Controller, Util)    │  (30–40 test cases)
        └──────────────────────────────────────┘
```

**Coverage Target:** 85%+ line coverage (unit + integration combined); 100% coverage of critical paths (authentication, validation, composite-key lookup, error translation).

### 1.3 Test Environment and Execution Strategy

| Environment | Runtime Stack | Persistence | Authentication | Purpose |
|-------------|---------------|-------------|-----------------|---------|
| **Developer Local** | Java 21 + Maven; Node.js 20 + npm | Mock (in-memory H2) | Mock OAuth2 token provider (TestJwtTokenGenerator) | Rapid iteration; pre-commit verification |
| **CI/CD Pipeline** | Java 21 + Maven; Node.js 20 + npm | Mock (in-memory H2) | Mock OAuth2 token provider; test fixtures | Automated gate checks; pull request validation |
| **Integration Test Environment** | Java 21 + Spring Boot 3.3.x; React 18.x via Vite dev server | Mock (H2 embedded) | Mock OAuth2 resource server (Spring Security + @EnableResourceServer) | Full integration testing; API contract verification |
| **User Acceptance Testing (UAT)** | Java 21 + Spring Boot 3.3.x (containerized); React 18.x (production build) | Mock repository (H2 or PostgreSQL test instance) | OAuth2 bearer tokens from UAT authorization server | End-user workflow validation; non-functional acceptance |
| **Production Readiness** | Java 21 + Spring Boot 3.3.x (Docker); React 18.x (static asset CDN) | Mock repository (to be replaced with real DB2 adapter in future phase) | OAuth2 bearer tokens from production authorization server | Pre-deployment smoke test; artifact validation |

---

## 2. Unit Test Specifications

### 2.1 Service Layer Tests

---

#### TC-001: Account Record Retrieval
- **Description:** Verify that the system retrieves account records based on valid account number and account type.
- **Mapped Requirement:** FR-001
- **Inputs:**
  - Account Number: "12345678"
  - Account Type: "SAVINGS"
- **Expected Output:**
  ```json
  {
    "accountEyecatcher": "EYEC",
    "customerNumber": "CUST1234",
    "sortCode": "SORT01",
    "interestRate": 1.5,
    "openedDate": "2021-01-01",
    "overdraftLimit": 1000,
    "lastStatementDate": "2023-01-01",
    "nextStatementDate": "2023-07-01",
    "availableBalance": 5000.00,
    "actualBalance": 4500.00
  }
  ```

---

#### TC-002: Invalid Account Number
- **Description:** Verify that the system returns an error for an invalid account number.
- **Mapped Requirement:** FR-001
- **Inputs:**
  - Account Number: "INVALID"
  - Account Type: "SAVINGS"
- **Expected Output:**
  ```json
  {
    "errorCode": "400",
    "errorMessage": "Invalid account number"
  }
  ```

---

#### TC-003: Error Handling
- **Description:** Verify that the system handles errors gracefully and returns standardized error responses.
- **Mapped Requirement:** FR-002
- **Inputs:**
  - Error details: { "code": "DB_ERROR", "message": "Database access failed" }
- **Expected Output:**
  ```json
  {
    "errorCode": "500",
    "errorMessage": "Internal server error"
  }
  ```

---

#### TC-004: Logging of Requests and Responses
- **Description:** Verify that all account inquiry requests and responses are logged correctly.
- **Mapped Requirement:** FR-003
- **Inputs:**
  - Request: { "accountNumber": "12345678", "accountType": "SAVINGS" }
  - Response: { "accountEyecatcher": "EYEC", ... }
- **Expected Log Entry:**
  ```json
  {
    "correlationId": "abc123",
    "timestamp": "2023-10-01T12:00:00Z",
    "request": { "accountNumber": "12345678", "accountType": "SAVINGS" },
    "response": { "accountEyecatcher": "EYEC", ... }
  }
  ```

---

#### TC-005: Role-Based Access Control
- **Description:** Verify that access is granted or denied based on user roles.
- **Mapped Requirement:** FR-004
- **Inputs:**
  - User Token: "valid_jwt_token"
- **Expected Output:**
  - Access Granted: 200 OK
  - Access Denied: 403 Forbidden

---

## 3. Integration Tests

### TC-006: Integration with Frontend
- **Description:** Verify that the frontend can successfully call the account inquiry API and display results.
- **Mapped Requirement:** FR-001
- **Expected Output:**
  - Successful retrieval of account details displayed in the frontend.
  - Error message displayed for invalid account inquiries.

---

## 4. Contract Tests

### TC-007: API Contract Compliance
- **Description:** Verify that the API adheres to the OpenAPI specification.
- **Mapped Requirement:** FR-001
- **Expected Output:**
  - API responses match the defined schema in `openapi.yaml`.

---

## 5. Negative and Boundary Scenarios

### TC-008: Missing Account Number
- **Description:** Verify that the system returns an error when the account number is missing.
- **Mapped Requirement:** FR-001
- **Inputs:**
  - Account Number: ""
  - Account Type: "SAVINGS"
- **Expected Output:**
  ```json
  {
    "errorCode": "400",
    "errorMessage": "Account number is required"
  }
  ```

---

### TC-009: Invalid Account Type
- **Description:** Verify that the system returns an error for an invalid account type.
- **Mapped Requirement:** FR-001
- **Inputs:**
  - Account Number: "12345678"
  - Account Type: "INVALID_TYPE"
- **Expected Output:**
  ```json
  {
    "errorCode": "400",
    "errorMessage": "Invalid account type"
  }
  ```

---

## 6. Security Tests

### TC-010: Unauthorized Access
- **Description:** Verify that the system denies access to unauthorized users.
- **Mapped Requirement:** FR-004
- **Inputs:**
  - User Token: "invalid_jwt_token"
- **Expected Output:**
  - Access Denied: 403 Forbidden

---

## 7. Performance Tests

### TC-011: Response Time Under Load
- **Description:** Verify that the system responds within acceptable time limits under load.
- **Mapped Requirement:** FR-001
- **Expected Output:**
  - Response time should be less than 200ms for 95% of requests under load.

---

## 8. Legacy Parity Tests

### TC-012: Legacy Behavior Verification
- **Description:** Verify that the system maintains legacy observable behavior for account inquiries.
- **Mapped Requirement:** FR-001
- **Expected Output:**
  - Responses for legacy account inquiries match the expected legacy outputs.

---

## 9. Modernization Enhancement Tests

### TC-013: New Feature Verification
- **Description:** Verify that any new features introduced do not affect existing functionalities.
- **Mapped Requirement:** FR-001
- **Expected Output:**
  - Existing functionalities remain intact while new features operate as expected.
```