# Spec Document for INQACC Modernization

**Document ID:** `spec.md`  
**Pipeline:** mainframe_modernization  
**Authority:** provided/system-intent.md + intended-system.md + business-rules.md + requirements.md + program-analysis.md + mapping-matrix.md  
**Status:** Implementation-ready canonical specification  
**Generated:** 2024  
**Stack:** Java 21 + Spring Boot 3.3.x (backend) | React 18.x + TypeScript 5.x + Vite 5.x (frontend) | Mock Repository (POC)

---

## 1. Feature Overview and Modernization Objective

### 1.1 Feature Name
**INQACC Modernized Account Inquiry Service**

### 1.2 Objective
Modernize the legacy INQACC CICS-DB2 account inquiry program into a cloud-ready, RESTful web service with distributed authentication, structured observability, and web UI while preserving legacy observable behavior and enabling future mainframe system integration.

### 1.3 Scope Boundaries

**In-Scope:**
- Composite-key account lookup (ACCOUNT_SORTCODE + ACCOUNT_NUMBER)
- OAuth2 bearer token authentication and role-based authorization (ACCOUNT_INQUIRER role)
- Standardized JSON request/response contracts
- Mock data repository (POC, no live DB2/CICS)
- Structured logging with correlation ID propagation
- OpenAPI 3.0.3 contract-first API design
- React web UI for employee account inquiry
- Input validation at HTTP boundary
- Error categorization with standard HTTP status codes and error envelope

**Out-of-Scope:**
- Live CICS transaction server integration
- Live DB2 mainframe database connectivity
- Account modification or creation workflows
- Multi-account batch inquiry
- Account statement generation or history retrieval
- Real-time mainframe system monitoring or health checks

## 2. Intended System Alignment Summary

This specification aligns to the canonical target architecture defined in `provided/system-intent.md`:

| Dimension | Target | Implementation Strategy |
|-----------|--------|------------------------|
| **Backend Runtime** | Java 21 + Spring Boot 3.3.x | Maven-based build; Spring Web MVC REST stack; Spring Security OAuth2 Resource Server |
| **Frontend Runtime** | React 18.x + TypeScript 5.x + Vite 5.x | Node.js 20 LTS; npm-based dependency management; React Router for navigation |
| **API Protocol** | REST over HTTPS; OpenAPI 3.0.3 | Spring MVC `@RestController` with Springdoc OpenAPI auto-generation |
| **Authentication** | OAuth2 resource server; JWT bearer tokens | Spring Security OAuth2 Resource Server; token validation at controller boundary |
| **Authorization** | Role-based access control (ACCOUNT_INQUIRER) | Spring Security `@PreAuthorize` annotations on service methods; RBAC enforced at service layer |
| **Persistence (POC)** | Mock in-memory repository | Spring Data JPA with H2 embedded database or custom in-memory Map-based repository |
| **Observability** | Structured JSON logging + correlation ID propagation | SLF4J + Logback with JSON encoder; MDC (Mapped Diagnostic Context) for correlation ID |
| **Error Handling** | Standardized JSON error envelope | Global `@ExceptionHandler` in `GlobalExceptionHandler` class; mapped to HTTP status codes per OpenAPI spec |
| **Modernization Enhancements** | OAuth2, structured logging, correlation IDs, JSON REST | All new capabilities explicitly marked; legacy lookup semantics preserved as default path |

---

## 3. API Endpoints with Request/Response Contracts

### 3.1 Account Inquiry Endpoint: GET /v1/accounts/{sortcode}/{accountNumber}

**Endpoint ID:** `ENDPOINT-001`  
**HTTP Method:** GET  
**Path:** `/v1/accounts/{sortcode}/{accountNumber}`  
**Protocol:** HTTPS only (TLS 1.2 minimum)  
**Authentication:** OAuth2 Bearer Token (JWT)  
**Authorization:** Requires `ACCOUNT_INQUIRER` role or higher

#### 3.1.1 Request Contract

**Path Parameters:**

| Parameter | Type | Format | Constraints | Example | Mapping |
|-----------|------|--------|-------------|---------|---------|
| `sortcode` | String | `^\d{6}$` | Exactly 6 numeric digits; required; no leading zeros trimmed | `"123456"` | ACCOUNT_SORTCODE (CHAR(6)) |
| `accountNumber` | String | `^\d{8}$` | Exactly 8 numeric digits; required | `"98765432"` | ACCOUNT_NUMBER (CHAR(8)) |

**Header Parameters:**

| Header | Type | Required | Format | Purpose | Example |
|--------|------|----------|--------|---------|---------|
| `Authorization` | String | Yes | `Bearer <JWT_token>` | OAuth2 bearer token for authentication | `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `X-Correlation-ID` | String | No | UUID v4 | Optional correlation ID for distributed tracing. If omitted, backend generates unique UUID. | `550e8400-e29b-41d4-a716-446655440000` |

**Request Body:** None

**Validation Rules (Applied Before Service Logic):**

- `sortcode` must match pattern `^\d{6}$` (non-empty, exactly 6 digits)
  - **Failure Response:** HTTP 400 Bad Request (see §3.4.1)
  - **Error Code:** `VALIDATION_ERROR`
  - **Error Message:** `"Sortcode must be exactly 6 numeric digits"`

- `accountNumber` must match pattern `^\d{8}$` (non-empty, exactly 8 digits)
  - **Failure Response:** HTTP 400 Bad Request (see §3.4.1)
  - **Error Code:** `VALIDATION_ERROR`
  - **Error Message:** `"Account number must be exactly 8 numeric digits"`

- `Authorization` header must be present and contain valid JWT token with `ACCOUNT_INQUIRER` scope
  - **Failure Response:** HTTP 401 Unauthorized (see §3.4.2) if token missing
  - **Failure Response:** HTTP 403 Forbidden (see §3.4.3) if token invalid or insufficient scope

#### 3.1.2 Success Response (HTTP 200 OK)

**Response Body Schema:** `AccountResponse`

```json
{
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "account": {
    "eyecatcher": "ACCOUNT-DATA",
    "customerNumber": "C000000123",
    "sortcode": "123456",
    "accountNumber": "98765432",
    "accountType": "CHK",
    "accountStatus": "A",
    "accountName": "John Doe Account",
    "accountBalance": "50000.00",
    "accountCurrency": "GBP",
    "accountOpenDate": "2020-01-15",
    "accountManager": "Manager 1",
    "lastTransactionDate": "2024-01-10"
  },
  "timestamp": "2024-01-15T14:23:45.123Z"
}
```

**Response Headers:**

| Header | Type | Value | Purpose |
|--------|------|-------|---------|
| `X-Correlation-ID` | String | UUID from request or generated | Echo correlation ID for tracing |
| `Content-Type` | String | `application/json; charset=utf-8` | Response content type |
| `Cache-Control` | String | `no-store, no-cache, must-revalidate` | Disable caching for sensitive data |

**Field Mapping (COBOL → JSON):**

| COBOL Field (from ACCOUNT.cpy) | JSON Field | Type | Length | Description |
|--------------------------------|------------|------|--------|-------------|
| `ACCOUNT-EYECATCHER` | `eyecatcher` | String | 12 | Literal string "ACCOUNT-DATA" |
| `ACCOUNT-CUSTOMER-NUMBER` | `customerNumber` | String | 10 | Customer identifier |
| `ACCOUNT-SORTCODE` | `sortcode` | String | 6 | Sort code (request parameter echo) |
| `ACCOUNT-NUMBER` | `accountNumber` | String | 8 | Account number (request parameter echo) |
| `ACCOUNT-TYPE` | `accountType` | String | 3 | Account type code (e.g., "CHK", "SAV") |
| `ACCOUNT-STATUS` | `accountStatus` | String | 1 | Account status flag (e.g., "A"=Active, "C"=Closed) |
| `ACCOUNT-NAME` | `accountName` | String | 40 | Account holder name |
| `ACCOUNT-BALANCE` | `accountBalance` | String (decimal) | 12,2 | Current account balance (formatted with 2 decimals) |
| `ACCOUNT-CURRENCY` | `accountCurrency` | String | 3 | ISO 4217 currency code (e.g., "GBP", "USD") |
| `ACCOUNT-OPEN-DATE` | `accountOpenDate` | String (ISO 8601) | 10 | Account open date in YYYY-MM-DD format |
| `ACCOUNT-MANAGER` | `accountManager` | String | 40 | Account manager name |
| `ACCOUNT-LAST-TXN-DATE` | `lastTransactionDate` | String (ISO 8601) | 10 | Last transaction date in YYYY-MM-DD format |

#### 3.1.3 Error Response: HTTP 400 Bad Request (Invalid Input)

**Error Code:** `VALIDATION_ERROR`  
**Applicable Scenarios:**
- Sortcode does not match pattern `^\d{6}$`
- Account number does not match pattern `^\d{8}$`
- Path parameter is empty or missing

**Response Body:**

```json
{
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": [
      {
        "field": "sortcode",
        "value": "12345",
        "reason": "Must be exactly 6 numeric digits"
      }
    ]
  },
  "timestamp": "2024-01-15T14:23:45.123Z"
}
```

**HTTP Status Code:** `400`  
**Response Headers:** `X-Correlation-ID`, `Content-Type: application/json`

#### 3.1.4 Error Response: HTTP 401 Unauthorized (Missing/Invalid Token)

**Error Code:** `UNAUTHORIZED`  
**Applicable Scenarios:**
- `Authorization` header missing
- JWT token malformed or expired
- Token does not contain required `ACCOUNT_INQUIRER` scope

**Response Body:**

```json
{
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required. Provide a valid OAuth2 bearer token with ACCOUNT_INQUIRER scope.",
    "details": []
  },
  "timestamp": "2024-01-15T14:23:45.123Z"
}
```

**HTTP Status Code:** `401`  
**Response Headers:** `WWW-Authenticate: Bearer realm="INQACC", X-Correlation-ID`, `Content-Type: application/json`

#### 3.1.5 Error Response: HTTP 403 Forbidden (Insufficient Authorization)

**Error Code:** `FORBIDDEN`  
**Applicable Scenarios:**
- JWT token valid but user role does not include `ACCOUNT_INQUIRER`
- Token scope insufficient for account inquiry operation

**Response Body:**

```json
{
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions. Required role: ACCOUNT_INQUIRER",
    "details": []
  },
  "timestamp": "2024-01-15T14:23:45.123Z"
}
```

**HTTP Status Code:** `403`  
**Response Headers:** `X-Correlation-ID`, `Content-Type: application/json`

#### 3.1.6 Error Response: HTTP 404 Not Found (No Matching Account)

**Error Code:** `ACCOUNT_NOT_FOUND`  
**Applicable Scenarios:**
- Sortcode and account number are valid format
- No matching record exists in ACCOUNT table (composite key not found)

**Response Body:**

```json
{
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "error": {
    "code": "ACCOUNT_NOT_FOUND",
    "message": "No account found for the specified sortcode and account number",
    "details": [
      {
        "field": "composite_key",
        "value": "sortcode=123456, accountNumber=98765432",
        "reason": "Record does not exist in ACCOUNT table"
      }
    ]
  },
  "timestamp": "2024-01-15T14:23:45.123Z"
}
```

**HTTP Status Code:** `404`  
**Response Headers:** `X-Correlation-ID`, `Content-Type: application/json`

#### 3.1.7 Error Response: HTTP 500 Internal Server Error (Repository/System Failure)

**Error Code:** `INTERNAL_SERVER_ERROR`  
**Applicable Scenarios:**
- Mock repository connection failure
- Unexpected exception during account lookup (null pointer, data corruption, etc.)
- Database adapter error (if future live DB2 integration)

**Response Body:**

```json
{
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred while processing your request",
    "details": []
  },
  "timestamp": "2024-01-15T14:23:45.123Z"
}
```

**HTTP Status Code:** `500`  
**Response Headers:** `X-Correlation-ID`, `Content-Type: application/json`  
**Note:** Backend shall log full stack trace with correlation ID; do not expose internal stack trace to client.

#### 3.1.8 Error Response: HTTP 503 Service Unavailable (Downstream Adapter Unreachable)

**Error Code:** `SERVICE_UNAVAILABLE`  
**Applicable Scenarios:**
- Mock repository initialization failure
- Database adapter not available (future live DB2 integration)
- Circuit breaker open on downstream service

**Response Body:**

```json
{
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Account inquiry service is temporarily unavailable. Please try again later.",
    "details": []
  },
  "timestamp": "2024-01-15T14:23:45.123Z"
}
```

**HTTP Status Code:** `503`  
**Response Headers:** `Retry-After: 60`, `X-Correlation-ID`, `Content-Type: application/json`

---

## 4. Business Rule Realization

### 4.1 Rule ID: BR-001
- **Description:** Retrieve account records based on account number and type.
- **Inputs:** 
  - Account Number (HV-ACCOUNT-ACC-NO)
  - Account Type (HV-ACCOUNT-ACC-TYPE)
- **Outputs:** Account details as specified in the API response.

### 4.2 Rule ID: BR-002
- **Description:** Handle errors gracefully and provide standardized error responses.
- **Outputs:** Standardized error response format.

### 4.3 Rule ID: BR-003
- **Description:** Log all account inquiry requests and responses.
- **Outputs:** Structured JSON log entry.

### 4.4 Rule ID: BR-004
- **Description:** Enforce role-based access control for account inquiry endpoints.
- **Outputs:** Access granted or denied based on user roles.

## 5. Validation and Error Semantics
- **Validation Rules:**
  - Account Number and Account Type must not be empty and must conform to expected formats.
- **Error Handling:**
  - Return a 400 Bad Request for invalid inputs.

## 6. Security and Compliance Controls
- **Authentication:** OAuth2 resource server with JWT bearer tokens.
- **Authorization:** Role-based access control for account inquiry endpoints.
- **Transport Security:** TLS 1.2+ for all communications.
- **Input Validation:** Strict path/query validation and standardized error responses.
- **Secrets Handling:** Environment variables or secret manager, never in source control.

## 7. Non-Functional Behavior
- **Latency:** API response time should be under 200ms for 95% of requests.
- **Reliability:** 99.9% uptime for the account inquiry service.
- **Logging:** Structured JSON logs with correlation ID per request.
- **Metrics:** Request latency, error rate, and downstream adapter status.
- **Tracing:** Distributed tracing ready (OpenTelemetry).

## 8. Acceptance Criteria Table

| Acceptance Criteria ID | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| AC-001                 | The system retrieves account records based on valid account number and type.|
| AC-002                 | The system returns a 400 error for invalid account number or type.         |
| AC-003                 | The system logs all requests and responses in structured JSON format.      |
| AC-004                 | The system enforces role-based access control for account inquiry endpoints.|
| AC-005                 | The system returns a 403 error for unauthorized access attempts.           |
| AC-006                 | The system maintains legacy observable behavior in all responses.          |