# SPECIFICATION: INQACCCU Customer Account Inquiry REST API

**Document ID:** `spec-inqacccu-modernization-001`  
**Pipeline:** `mainframe_modernization`  
**Version:** 1.0  
**Status:** Implementation-Ready  
**Last Updated:** 2025  

---

## 1. Feature and Objective

**Feature Name:** Customer Account Relationship Inquiry REST API

**Objective:** Modernize the legacy COBOL INQACCCU CICS transaction into a Spring Boot 3.3.x REST API backend. The system accepts a 10-digit customer number and returns 0–20 associated account records with complete account details (account number, sort code, balance, interest rate, statement date). The API enforces OAuth2 resource server authentication, role-based access control, strict input validation, and structured observability (JSON logging, correlation IDs, OpenTelemetry-ready tracing).

**Modernization Scope:**
- Replace CICS transaction processing with Spring Boot REST endpoints
- Preserve all legacy observable behavior as default execution path
- Replace DB2/DLI access with mock repository layer (POC phase)
- Introduce JWT bearer token authentication and RBAC
- Enable future enhancements via feature toggles with explicit marking

---

## 2. Intended System Alignment Summary

| Dimension | Target Baseline | Alignment Notes |
|-----------|-----------------|-----------------|
| **Backend Stack** | Java 21, Spring Boot 3.3.x, Maven 3.9+ | Spring Cloud for config; Maven for dependency management |
| **API Protocol** | REST over HTTPS, OpenAPI 3.0.3 | All endpoints must declare OpenAPI schema |
| **Authentication** | OAuth2 resource server with JWT bearer tokens | Spring Security 6.x; token validation at controller filter |
| **Authorization** | Role-based access control (RBAC) | Annotation-based: `@PreAuthorize("hasRole('CUSTOMER_INQUIRY')")` |
| **Persistence (POC)** | Mock repository, no live CICS/DB2 | In-memory mock; production adapter pattern for future DB2 integration |
| **Security Transport** | TLS 1.2+ mandatory | Spring Boot default; enforce in production via reverse proxy |
| **Input Validation** | Strict path/query parameter validation | 10-digit customer ID pattern: `^[0-9]{10}$`; fail-fast semantics |
| **Error Responses** | Standardized, no sensitive data exposure | RFC 7807 Problem+JSON format |
| **Logging** | Structured JSON with correlation ID per request | Spring Cloud Sleuth for correlation; Logback JSON encoder |
| **Metrics** | Prometheus-compatible; OpenTelemetry-ready | Micrometer + Spring Boot Actuator; tracing beans auto-configured |
| **Operational Logging** | JSON format with trace context | Correlation ID injected at ingress; propagated to mock repository |

---

## 3. Domain Model

### 3.1 Core Entities

#### **Customer**
| Field | Type | Constraint | Purpose |
|-------|------|-----------|---------|
| `customerId` | String | `^[0-9]{10}$` | 10-digit customer identifier (legacy CUSTOMER-NUMBER) |
| `customerFound` | Boolean | required | Indicates whether customer exists in legacy system |

#### **Account**
| Field | Type | Constraint | Purpose |
|-------|------|-----------|---------|
| `eyeCatcher` | String | fixed: `"ACCT"` | Legacy copybook identifier (preserved for audit trail) |
| `accountNumber` | String | 8 digits, `^[0-9]{8}$` | Unique account identifier (legacy ACCOUNT-NUMBER) |
| `sortCode` | String | 6 characters, `^[0-9]{6}$` | UK/international sort code (legacy SORT-CODE) |
| `accountType` | String | 1 char: A/B/C/D (legacy) | Account classification; preserved from ACCOUNT-TYPE |
| `accountStatus` | String | 1 char: A/I/C (legacy) | Active/Inactive/Closed (legacy ACCOUNT-STATUS) |
| `balance` | BigDecimal | precision 15,2 | Current account balance (legacy ACCOUNT-BALANCE) |
| `interestRate` | BigDecimal | precision 5,4 | Annual interest rate (legacy INTEREST-RATE) |
| `statementDate` | LocalDate | ISO 8601 (YYYY-MM-DD) | Last statement date (legacy STATEMENT-DATE) |
| `currencyCode` | String | 3 chars, ISO 4217 (default: GBP) | Currency (legacy CURRENCY-CODE) |

#### **CustomerAccountsResponse** (API Contract)
| Field | Type | Constraint | Purpose |
|-------|------|-----------|---------|
| `customerId` | String | `^[0-9]{10}$` | Request echoed back |
| `customerFound` | Boolean | required | Legacy CUSTOMER-FOUND indicator |
| `numberOfAccounts` | Integer | 0–20 (inclusive) | Count of returned accounts |
| `accounts` | Array[Account] | 0–20 elements | Ordered account records (legacy 0-occurrence to 20-occurrence) |

---

## 4. API Endpoints

### 4.1 Endpoint: Query Customer Accounts

**Endpoint ID:** `EP001-GET-CUSTOMER-ACCOUNTS`

**HTTP Method:** `GET`

**Path:** `/api/v1/customers/{customerId}/accounts`

**Path Parameter:**
| Name | Type | Format | Validation | Required |
|------|------|--------|-----------|----------|
| `customerId` | String | Numeric | `^[0-9]{10}$`; fail-fast if invalid length or non-numeric | Yes |

**Query Parameters:** None

**Headers:**
| Name | Type | Format | Required | Purpose |
|------|------|--------|----------|---------|
| `Authorization` | String | `Bearer <JWT>` | Yes | OAuth2 bearer token; invalid/missing returns `401 Unauthorized` |
| `Content-Type` | String | `application/json` | No | Client hint; response always `application/json` |
| `X-Correlation-ID` | String | UUID v4 or client-supplied | No | Correlation ID for request tracing; auto-generated if omitted |

**Request Body:** None

**Authentication & Authorization:**
- **Scheme:** OAuth2 Resource Server with JWT bearer tokens
- **Required Role:** `CUSTOMER_INQUIRY` (or higher privilege)
- **Token Validation:** 
  - Signature verification via configured public key / JWKS endpoint
  - Expiration (`exp`) must be in future
  - Audience (`aud`) must match API service identifier
  - `scope` must include `customer:read` or equivalent
- **Failure Response:** `401 Unauthorized` if token absent, invalid, or expired; `403 Forbidden` if role insufficient

#### **4.1.1 Successful Response (200 OK)**

**Status:** `200 OK`

**Content-Type:** `application/json`

**Schema:**
```json
{
  "customerId": "0123456789",
  "customerFound": true,
  "numberOfAccounts": 2,
  "accounts": [
    {
      "eyeCatcher": "ACCT",
      "accountNumber": "12345678",
      "sortCode": "112233",
      "accountType": "A",
      "accountStatus": "A",
      "balance": "15234.50",
      "interestRate": "0.0250",
      "statementDate": "2024-12-15",
      "currencyCode": "GBP"
    },
    {
      "eyeCatcher": "ACCT",
      "accountNumber": "87654321",
      "sortCode": "445566",
      "accountType": "B",
      "accountStatus": "A",
      "balance": "8765.25",
      "interestRate": "0.0175",
      "statementDate": "2024-12-10",
      "currencyCode": "GBP"
    }
  ]
}
```

**Response Headers:**
| Name | Value | Purpose |
|------|-------|---------|
| `Content-Type` | `application/json; charset=utf-8` | Response media type |
| `X-Correlation-ID` | UUID v4 or echoed from request | Tracing identifier |
| `X-Request-Timestamp` | ISO 8601 | Server-side request receipt time |
| `Cache-Control` | `no-cache, no-store, must-revalidate` | Prevent caching of sensitive data |

#### **4.1.2 Customer Not Found (200 OK with `customerFound: false`)**

**Status:** `200 OK`

**Content-Type:** `application/json`

**Semantics:** Legacy behavior preserved: inquiry for non-existent customer returns `200 OK` with `customerFound: false`, `numberOfAccounts: 0`, empty `accounts` array.

**Schema:**
```json
{
  "customerId": "9999999999",
  "customerFound": false,
  "numberOfAccounts": 0,
  "accounts": []
}
```

#### **4.1.3 Invalid Customer ID (400 Bad Request)**

**Status:** `400 Bad Request`

**Content-Type:** `application/problem+json` (RFC 7807)

**Schema:**
```json
{
  "type": "https://api.example.com/errors/invalid-customer-id",
  "title": "Invalid Customer ID",
  "status": 400,
  "detail": "Customer ID must be exactly 10 numeric digits; received: '12345' (5 digits).",
  "instance": "/api/v1/customers/12345/accounts",
  "correlationId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Validation Rules Triggering 400:**
- Customer ID length ≠ 10
- Customer ID contains non-numeric characters
- Customer ID is missing from URI path

#### **4.1.4 Missing or Invalid Bearer Token (401 Unauthorized)**

**Status:** `401 Unauthorized`

**Content-Type:** `application/problem+json`

**Schema:**
```json
{
  "type": "https://api.example.com/errors/unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Bearer token is missing, malformed, or invalid. Ensure the Authorization header contains a valid JWT.",
  "instance": "/api/v1/customers/0123456789/accounts",
  "correlationId": "550e8400-e29b-41d4-a716-446655440001",
  "WWW-Authenticate": "Bearer realm=\"api.example.com\", error=\"invalid_token\""
}
```

**Trigger Conditions:**
- `Authorization` header absent
- `Authorization` header value does not start with `Bearer `
- JWT signature invalid
- JWT expired (`exp` claim in past)
- JWT `aud` claim does not match API service identifier
- Required scopes missing from JWT

#### **4.1.5 Insufficient Role/Permission (403 Forbidden)**

**Status:** `403 Forbidden`

**Content-Type:** `application/problem+json`

**Schema:**
```json
{
  "type": "https://api.example.com/errors/forbidden",
  "title": "Forbidden",
  "status": 403,
  "detail": "User role does not grant access to customer account inquiry. Required role: CUSTOMER_INQUIRY.",
  "instance": "/api/v1/customers/0123456789/accounts",
  "correlationId": "550e8400-e29b-41d4-a716-446655440002"
}
```

**Trigger Conditions:**
- JWT token valid and not expired
- User identity authenticated
- User's granted roles do not include `CUSTOMER_INQUIRY` or equivalent

#### **4.1.6 Server Error (500 Internal Server Error)**

**Status:** `500 Internal Server Error`

**Content-Type:** `application/problem+json`

**Schema:**
```json
{
  "type": "https://api.example.com/errors/internal-server-error",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected error occurred while processing the request. Please contact support with the correlation ID.",
  "instance": "/api/v1/customers/0123456789/accounts",
  "correlationId": "550e8400-e29b-41d4-a716-446655440003"
}
```

**Trigger Conditions:**
- Unhandled exception during repository access
- Database/mock adapter unavailable
- Network error retrieving customer/account data

**No sensitive stack traces or internal details exposed to client.**

---

## 5. Business Rules Realization

### BR001: Customer Inquiry Acceptance Rule

**ID:** `BR001`

**Statement:** Accept a customer number (10 digits) as input and initiate an account relationship inquiry.

**Realization in REST API:**
- **Input:** Path parameter `customerId` (10 numeric digits)
- **Validation:** Regex `^[0-9]{10}$` applied immediately at controller input; invalid format returns `400 Bad Request` before business logic execution
- **Processing:** Forward valid customer ID to `CustomerInquiryService.getAccountsByCustomerId(String customerId)`
- **Output:** `CustomerAccountsResponse` JSON object with `customerFound`, `numberOfAccounts`, and `accounts` array
- **Error:** Non-existent customer returns `200 OK` with `customerFound: false`, `numberOfAccounts: 0`, empty accounts list (legacy behavior preserved)

**Implementation Artifact:**
```java
@RestController
@RequestMapping("/api/v1/customers")
public class CustomerAccountController {

  @GetMapping("/{customerId}/accounts")
  @PreAuthorize("hasRole('CUSTOMER_INQUIRY')")
  public ResponseEntity<CustomerAccountsResponse> getAccountsByCustomerId(
    @PathVariable
    @Pattern(regexp = "^[0-9]{10}$", message = "Customer ID must be exactly 10 numeric digits")
    String customerId,
    @RequestHeader(name = "X-Correlation-ID", required = false) String correlationId
  ) {
    // Service call delegated to business logic layer
    CustomerAccountsResponse response = customerInquiryService.getAccountsByCustomerId(customerId);
    
    // Add response headers for correlation and caching directives
    return ResponseEntity
      .ok()
      .header("X-Correlation-ID", correlationId != null ? correlationId : UUID.randomUUID().toString())
      .header("Cache-Control", "no-cache, no-store, must-revalidate")
      .body(response);
  }
}
```

---

### BR002: Account Limit Rule

**ID:** `BR002`

**Statement:** Return a maximum of 20 accounts per customer inquiry.

**Realization:**
- **Constraint:** `numberOfAccounts` field capped at 20; accounts array contains 0–20 elements
- **Validation Logic in Service Layer:**
  ```java
  List<Account> allAccounts = accountRepository.findByCustomerId(customerId);
  List<Account> limitedAccounts = allAccounts.stream()
    .limit(20)
    .collect(Collectors.toList());
  
  response.setNumberOfAccounts(limitedAccounts.size());
  response.setAccounts(limitedAccounts);
  ```
- **Behavior:** If customer has >20 accounts, only first 20 returned; client receives truncation indication via `numberOfAccounts == 20` and array length
- **Modernization Enhancement:** Future ENHANCEMENT-001 (toggle-able) may add pagination to retrieve >20 accounts; legacy path returns first 20 only

---

### BR003: Preserved Input Validation Strictness

**ID:** `BR003`

**Statement:** Reject customer ID if not exactly 10 numeric digits. Fail-fast without downstream repository access.

**Realization:**
- **Bean Validation:** `@Pattern(regexp = "^[0-9]{10}$")` applied to `@PathVariable customerId`
- **Failure Response:** `400 Bad Request` with RFC 7807 Problem+JSON detail
- **No Fallback:** Invalid input does not attempt legacy CICS-like fuzzy matching or padding
- **Modernization:** Input validation strictness preserved from legacy COBOL; error messaging enhanced with JSON structure

---

### BR004: Account Status Preservation

**ID:** `BR004`

**Statement:** Return all accounts associated with customer, regardless of account status (Active, Inactive, Closed).

**Realization:**