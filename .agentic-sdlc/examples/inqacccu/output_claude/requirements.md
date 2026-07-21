# requirements.md

**Document ID:** `requirements-inqacccu-001`  
**Pipeline:** `mainframe_modernization`  
**Target Output File:** `requirements.md`  
**Generated From:** Intended System, Business Rules, Program Analysis, Legacy COBOL  

---

## 1. Scope

### 1.1 In Scope

- **Backend API:** Modernize INQACCCU CICS transaction into a Spring Boot 3.3.x REST API endpoint
- **Customer Account Inquiry:** Accept 10-digit customer number; return 0–20 associated account records with full details
- **Authentication & Authorization:** OAuth2 resource server with JWT bearer token validation; role-based access control
- **Data Mapping:** Transform COBOL copybook structures (INQACCCUZ, ACCOUNT, ACCDB2) into REST JSON payloads
- **Mock Repository Layer:** POC-phase persistence via in-memory mock (no live DB2 or CICS connection)
- **Observability:** Structured JSON logging, request correlation IDs, OpenTelemetry-ready tracing infrastructure
- **Frontend Integration:** React 18.x + TypeScript UI consuming REST endpoints; Vite 5.x build tooling
- **Error Standardization:** Preserve legacy error semantics; map to HTTP status codes and structured JSON error responses

### 1.2 Out of Scope

- Live mainframe CICS or DB2 connectivity in POC phase
- Custom authentication provider (rely on OAuth2 defaults)
- Batch account inquiry processing
- Account update/mutation operations (read-only inquiry only)
- Real-time account balancing or overdraft calculations beyond legacy fields
- Mainframe system integration beyond mock repository adapter pattern

---

## 2. Functional Requirements

### FR-001: Customer Account Inquiry Endpoint

**ID:** FR-001  
**Title:** REST endpoint to retrieve accounts by customer ID  
**Source Rule(s):** BR001, BR002 (Business Rules); INQACCCU COBOL logic (program-analysis-inqacccu-001 §2.1)  
**Description:**  
The system shall provide a REST GET endpoint `GET /api/v1/customers/{customerId}/accounts` that accepts a 10-digit customer number (path parameter) and returns all associated account records. The endpoint shall invoke an account inquiry service that queries the mock repository (or future DB2 adapter) for matching account records.

**Input:**
- Path Parameter: `customerId` (exactly 10 numeric digits; format validation required)
- Request Header: `Authorization: Bearer <JWT>`

**Output (200 OK):**
```json
{
  "customerId": "0123456789",
  "customerFound": true,
  "numberOfAccounts": 2,
  "accounts": [
    {
      "eyeCatcher": "ACCT",
      "accountNumber": "12345678",
      "sortCode": "123456",
      "accountType": "CHECKING",
      "interestRate": 1.25,
      "dateOpened": "20220115",
      "overdraftLimit": 5000,
      "lastStatementDate": "20240101",
      "nextStatementDate": "20240201",
      "availableBalance": 15000.50,
      "actualBalance": 14500.25
    }
  ]
}
```

**Error Outputs:**
- `400 Bad Request`: Customer ID format invalid (non-numeric, wrong length)
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: Valid JWT but insufficient role for endpoint
- `500 Internal Server Error`: Server error (logged with correlation ID)

**Acceptance Criteria:**
- AC-001, AC-002, AC-003 (see §5)

**Preserved Legacy Behavior:**
- Customer not found → `customerFound: false`, `numberOfAccounts: 0`, empty `accounts` array (map from CUSTOMER-FOUND = 'N')
- Returns 0–20 account records (map from DEPENDS ON clause in INQACCCUZ.cpy)
- All numeric fields serialized to JSON types matching legacy precision (e.g., interest rate 9(4)V99 → decimal/number)

---

### FR-002: Customer ID Validation (Strict)

**ID:** FR-002  
**Title:** Strict input validation for 10-digit customer number  
**Source Rule(s):** BR001, BR003 (Input validation); INQACCCU WS-CUST-INV check (program-analysis-inqacccu-001 §3.1)  
**Description:**  
The system shall enforce strict validation on the `customerId` path parameter:
- Must be exactly 10 numeric digits (0–9)
- Leading zeros are significant and must be preserved
- Non-numeric or incorrect-length values shall be rejected with HTTP 400

**Implementation Note:**  
Use Spring's `@PathVariable` with regex constraint or custom validator; reject before reaching service layer.

**Acceptance Criteria:**
- AC-004, AC-005

---

### FR-003: Account Details Data Transfer

**ID:** FR-003  
**Title:** Map legacy COBOL account fields to REST JSON DTO  
**Source Rule(s):** BR004, BR005 (Data Mapping); ACCOUNT.cpy and ACCDB2.cpy copybook structure  
**Description:**  
The system shall define a REST DTO (AccountDto) that maps all account fields from the legacy COBOL copybooks:

| Legacy Field (COBOL) | DTO Field | Type | Notes |
|---|---|---|---|
| ACCOUNT-EYE-CATCHER | eyeCatcher | String | Always "ACCT" |
| ACCOUNT-CUST-NO | customerId | String | Preserved from parent response |
| ACCOUNT-SORT-CODE | sortCode | String | 6 digits |
| ACCOUNT-NUMBER | accountNumber | String | 8 digits |
| ACCOUNT-TYPE | accountType | String | Up to 8 chars |
| ACCOUNT-INTEREST-RATE | interestRate | BigDecimal | 9(4)V99 format |
| ACCOUNT-OPENED | dateOpened | String | YYYYMMDD format |
| ACCOUNT-OVERDRAFT-LIMIT | overdraftLimit | Long | 8 digits |
| ACCOUNT-LAST-STMT-DATE | lastStatementDate | String | YYYYMMDD format |
| ACCOUNT-NEXT-STMT-DATE | nextStatementDate | String | YYYYMMDD format |
| ACCOUNT-AVAILABLE-BALANCE | availableBalance | BigDecimal | S9(10)V99 format |
| ACCOUNT-ACTUAL-BALANCE | actualBalance | BigDecimal | S9(10)V99 format |

**Acceptance Criteria:**
- AC-006, AC-007

---

### FR-004: OAuth2 Authentication Enforcement

**ID:** FR-004  
**Title:** Authenticate all REST API requests via OAuth2 JWT bearer tokens  
**Source Rule(s):** Security Baseline (system-intent.md); BR006 (Security)  
**Description:**  
The system shall enforce OAuth2 resource server authentication on all customer account inquiry endpoints. Each request must carry a valid JWT bearer token in the `Authorization` header. The token shall be validated against the configured OAuth2 provider (issuer, signature, expiration). Missing or invalid tokens shall return HTTP 401.

**Implementation Note:**  
Use Spring Security + `spring-boot-starter-oauth2-resource-server`; configure issuer URI and audience in `application.yml`.

**Acceptance Criteria:**
- AC-008, AC-009

---

### FR-005: Role-Based Access Control

**ID:** FR-005  
**Title:** Enforce role-based authorization for account inquiry endpoints  
**Source Rule(s):** Security Baseline (system-intent.md); BR007 (Authorization)  
**Description:**  
The system shall support role-based access control (RBAC) for the customer account inquiry endpoint. Authorized roles (e.g., `ACCOUNT_INQUIRER`, `ADMIN`) shall be extracted from JWT claims. Requests with valid JWT but insufficient role shall return HTTP 403 Forbidden.

**Role Definitions:**
- `ACCOUNT_INQUIRER`: Can execute customer account inquiry
- `ADMIN`: Full system access

**Implementation Note:**  
Use Spring Security `@PreAuthorize` or `SecurityFilterChain`; extract roles from JWT via custom claim mapping.

**Acceptance Criteria:**
- AC-010, AC-011

---

### FR-006: Structured JSON Logging with Correlation ID

**ID:** FR-006  
**Title:** Emit structured JSON logs with per-request correlation ID  
**Source Rule(s):** Operational Baseline (system-intent.md); BR008 (Observability)  
**Description:**  
All API requests and service operations shall emit structured JSON logs including:
- Timestamp (ISO 8601)
- Correlation ID (unique per request; preserved across service calls)
- Request path, method, query parameters
- Response status code, latency
- Business context (customerId, number of accounts returned)
- Error stack trace (if applicable)

Log level: INFO for successful requests, WARN for client errors (4xx), ERROR for server errors (5xx).

**Implementation Note:**  
Use SLF4J + Logback with JSON encoder; generate correlation ID in request filter; pass via MDC (Mapped Diagnostic Context).

**Acceptance Criteria:**
- AC-012, AC-013

---

### FR-007: Mock Repository Adapter Pattern

**ID:** FR-007  
**Title:** Provide mock repository implementation for POC phase  
**Source Rule(s):** BR009, BR010 (Data Persistence); System Intent (Delivery Constraints)  
**Description:**  
The system shall implement a `CustomerAccountRepository` interface with a mock in-memory implementation for POC. The mock shall:
- Return pre-seeded test data for known customer IDs (e.g., "0123456789")
- Return empty account list for unknown customers
- Support future adapter pattern for live DB2 connectivity without code changes

**Mock Data Example:**
```json
{
  "0123456789": {
    "customerFound": true,
    "accounts": [
      {"accountNumber": "12345678", "sortCode": "123456", ...},
      {"accountNumber": "87654321", "sortCode": "654321", ...}
    ]
  }
}
```

**Acceptance Criteria:**
- AC-014, AC-015

---

### FR-008: Environment-Based Configuration

**ID:** FR-008  
**Title:** Externalize all secrets and environment-specific settings  
**Source Rule(s):** BR011 (Secrets Handling); Security Baseline (system-intent.md)  
**Description:**  
All sensitive configuration (OAuth2 issuer URI, secret keys, database connection strings, API tokens) shall be externalized via environment variables or Spring Cloud Vault. No secrets shall be committed to source control. `application.yml` shall contain placeholders referencing `${OAUTH2_ISSUER}`, `${VAULT_ADDR}`, etc.

**Required Environment Variables:**
- `OAUTH2_ISSUER`: OAuth2 provider issuer URI
- `OAUTH2_CLIENT_ID`: (if applicable)
- `LOG_LEVEL`: Logging level (default: INFO)
- `SPRING_PROFILES_ACTIVE`: Active Spring profile (mock | prod)

**Acceptance Criteria:**
- AC-016, AC-017

---

### FR-009: OpenAPI 3.0.3 Schema Documentation

**ID:** FR-009  
**Title:** Publish REST API via OpenAPI 3.0.3 schema  
**Source Rule(s):** Intended System (API specification); system-intent.md  
**Description:**  
The system shall generate and expose an OpenAPI 3.0.3 specification document at `/v3/api-docs` and a Swagger UI at `/swagger-ui.html`. The spec shall document:
- All endpoints (paths, methods, parameters)
- Request/response schemas (DTO classes)
- Authentication scheme (OAuth2)
- Error responses (400, 401, 403, 500)
- Example payloads

**Implementation Note:**  
Use `springdoc-openapi-starter-webmvc-ui` dependency; annotate controllers and DTOs with `@Operation`, `@Schema`, etc.

**Acceptance Criteria:**
- AC-018, AC-019

---

### FR-010: Error Response Standardization

**ID:** FR-010  
**Title:** Standardize error response format across all HTTP status codes  
**Source Rule(s):** Intended System (HTTP semantics); BR012 (Error Handling)  
**Description:**  
All error responses shall follow a consistent JSON structure:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "status": 400,
  "error": "Bad Request",
  "message": "Customer ID must be exactly 10 numeric digits",
  "path": "/api/v1/customers/invalid/accounts",
  "correlationId": "req-12345-abcde"
}
```

**Implementation Note:**  
Create global `@ControllerAdvice` exception handler; map business exceptions to HTTP status codes; include correlation ID in all responses.

**Acceptance Criteria:**
- AC-020, AC-021

---

## 3. Non-Functional Requirements

### NFR-001: Performance – Request Latency

**ID:** NFR-001  
**Title:** API response time requirement  
**Description:**  
Account inquiry requests shall complete with mean response time ≤ 200 ms (p95: ≤ 500 ms) under normal load (1000 concurrent users). Mock repository queries shall return within 10 ms; future DB2 adapter shall be optimized to meet latency target.

**Measurement:**  
Monitor via Spring Actuator metrics (http.server.requests duration); export to observability platform (Prometheus, Datadog).

---

### NFR-002: Availability – Uptime Target

**ID:** NFR-002  
**Title:** Service availability SLA  
**Description:**  
The modernized account inquiry service shall maintain 99.5% availability (monthly uptime target). Graceful degradation: if mock repository is unavailable, return HTTP 503 Service Unavailable with clear error message.

---

### NFR-003: Scalability – Horizontal Scaling

**ID:** NFR-003  
**Title:** Stateless design for horizontal scaling  
**Description:**  
The backend service shall be designed as stateless (no server-side session state). All request context (customer ID, JWT claims) shall be derived from HTTP headers or path parameters. This enables horizontal scaling via container orchestration (Kubernetes) without session affinity.

---

### NFR-004: Security – Transport Encryption

**ID:** NFR-004  
**Title:** TLS 1.2+ encryption for all network traffic  
**Description:**  
All API traffic shall be encrypted via TLS 1.2 or higher. Self-signed certificates acceptable for POC; production requires CA-signed certificates. Spring Boot shall be configured with `server.ssl.enabled=true` and appropriate key store.

---

### NFR-005: Security – Input Validation

**ID:** NFR-005  
**Title:** Prevent injection attacks via strict input validation  
**Description:**  
All user-supplied input (path parameters, query strings, request bodies) shall be validated against expected format and length. Reject non-conforming input before processing. Use Spring Validation annotations (`@Pattern`, `@Size`) on DTO fields.

---

### NFR-006: Security – Secret Management

**ID:** NFR-006  
**Title:** No hardcoded credentials in source code  
**Description:**  
All secrets (API keys, database passwords, OAuth2 credentials) shall be injected via environment variables or Spring Cloud Vault at runtime. Source code review shall flag any committed secrets; CI/CD pipeline shall scan for credential patterns.

---

### NFR-007: Observability – Logging

**ID:** NFR-007  
**Title:** Structured JSON logging for all significant events  
**Description:**  
Application logs shall be emitted in JSON format with standardized fields (timestamp, level, logger, message, context) to enable log aggregation and analysis. Correlation ID shall be included in all logs related to a single request.

---

### NFR-008: Observability – Metrics

**ID:** NFR-008  
**Title:** Expose application metrics for monitoring  
**Description:**  
Spring Boot Actuator shall expose metrics via `/actuator/metrics` endpoint:
- HTTP request latency (http.server.requests)
- Request rate (throughput)
- Error rate (by status code)
- Custom business metrics (e.g., customer_found_rate)

Metrics shall be formatted for Prometheus scraping; integration with observability platform (Datadog, New Relic) optional in POC.

---

### NFR-009: Observability – Distributed Tracing

**ID:** NFR-009  
**Title:** Enable OpenTelemetry instrumentation for distributed tracing  
**Description:**  
The backend shall be instrumented