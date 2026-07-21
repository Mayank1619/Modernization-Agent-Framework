# intended-system.md

## 1. Feature and Modernization Objective

**Goal:** Modernize the legacy INQACCCU COBOL program—a CICS-based customer-to-account relationship inquiry system—into a modern, web-accessible REST API backend paired with a React frontend. The system will accept a 10-digit customer number and return associated account records (0–20 accounts) with full account details including balances, interest rates, and statement dates.

**Modernization Principles:**
- Preserve all legacy observable behavior and business logic as the default execution path.
- Enable future enhancements through explicit feature toggles and clear separation of concerns.
- Replace CICS transaction processing with Spring Boot REST endpoints.
- Replace DB2/DLI access with a mock repository layer (POC phase; production will integrate via adapters).
- Maintain input validation strictness and error semantics from the original program.

---

## 2. Target Product Scope

**In Scope:**
- REST API for customer account inquiry: `GET /api/v1/customers/{customerId}/accounts`
- Role-based authorization for customer and account data access.
- React SPA frontend with customer search and account list display.
- Structured logging with correlation IDs for request traceability.
- Distributed tracing hooks (OpenTelemetry) for operational observability.
- Mock data repository for POC (no live mainframe or DB2 connections).
- Input validation and standardized error responses (legacy semantics preserved).

**Deliverables:**
- Spring Boot 3.3.x REST application (Java 21).
- React 18.x TypeScript frontend with Vite build tooling.
- OpenAPI 3.0.3 specification for API contract.
- Deployment-ready Docker configuration.
- Maven and Node.js build artifacts.

---

## 3. Architecture Blueprint

### 3.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  React Frontend (SPA)                        │
│        (TypeScript 5.x, Vite 5.x, Node.js 20 LTS)           │
└──────────────────────────────┬──────────────────────────────┘
                                │ HTTPS
                    ┌───────────▼──────────────┐
                    │  API Gateway / Load      │
                    │  Balancer (TLS 1.2+)     │
                    └───────────┬──────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────┐
│         Spring Boot 3.3.x REST Application Layer             │
├───────────────────────────────────────────────────────────────┤
│  HTTP Controllers (thin)                                      │
│  ├─ CustomerAccountController                                │
│  │  └─ GET /api/v1/customers/{customerId}/accounts          │
│  └─ HealthController (actuator endpoints)                    │
├───────────────────────────────────────────────────────────────┤
│  Service Layer (business logic, legacy behavior preserved)    │
│  ├─ CustomerAccountInquiryService                            │
│  │  ├─ Query validation (10-digit customer number)           │
│  │  ├─ Account fetch and enrichment                          │
│  │  └─ Error handling (legacy error codes/messages)          │
│  └─ AuthorizationService (RBAC enforcement)                  │
├───────────────────────────────────────────────────────────────┤
│  Data Access Layer (Repository pattern)                       │
│  ├─ MockAccountRepository (POC)                              │
│  ├─ IAccountRepository (interface for future DB2/adapter)    │
│  └─ EntityMapper (COBOL copybook → Java DTO conversion)      │
├───────────────────────────────────────────────────────────────┤
│  Cross-Cutting Concerns                                       │
│  ├─ OAuth2ResourceServerConfigurer (JWT validation)         │
│  ├─ RequestLoggingFilter (correlation ID injection)          │
│  ├─ GlobalExceptionHandler (standardized error responses)    │
│  ├─ OpenTelemetry Tracer (distributed tracing)               │
│  └─ MetricsRegistry (request latency, error counts)          │
└───────────────────────────────────────────────────────────────┘
                                │
                   ┌────────────▼────────────┐
                   │  Mock Data Repository    │
                   │  (JSON/In-Memory)        │
                   │  (POC only)              │
                   └──────────────────────────┘
```

### 3.2 Request Flow

1. **Frontend:** User enters customer ID (10 digits) → React component sends authenticated HTTP request.
2. **Transport:** HTTPS request includes OAuth2 JWT bearer token in `Authorization` header.
3. **API Gateway:** Load balancer validates TLS handshake, routes to Spring Boot backend.
4. **Spring Boot Entry:** HTTP controller receives request, extracts customer ID from path parameter.
5. **Security Layer:** OAuth2ResourceServerConfigurer validates JWT; AuthorizationService enforces RBAC.
6. **Service Layer:** CustomerAccountInquiryService applies legacy business rules (input validation, account lookup, response formatting).
7. **Data Layer:** MockAccountRepository returns account records; EntityMapper converts to REST DTO.
8. **Response:** JSON response with account array (0–20 items); tracing and metrics recorded.
9. **Frontend:** React component renders account list or error message.

---

## 4. Technology Stack and Versions

### 4.1 Backend

| Component | Version | Purpose |
|-----------|---------|---------|
| **Java Runtime** | 21 (LTS) | JVM runtime; latest stable with long-term support |
| **Spring Boot** | 3.3.x | Framework; REST, OAuth2, actuator, logging |
| **Spring Security** | 6.x (via Boot BOM) | OAuth2 resource server, JWT bearer token validation |
| **Spring Cloud Config** | 2023.x (via Boot BOM) | Secrets management; environment variable injection |
| **Maven** | 3.9+ | Build and dependency management |
| **Maven Plugins** | spring-boot-maven-plugin 3.3.x, maven-compiler-plugin 3.11+ | Build, packaging, Java 21 compilation |
| **Jackson** | 2.16+ (via Boot BOM) | JSON serialization/deserialization |
| **Lombok** | 1.18.30+ | Boilerplate reduction (@Data, @Slf4j) |
| **OpenTelemetry** | 1.32+ (stable API) | Distributed tracing, metrics export |
| **OpenTelemetry Spring Boot Starter** | 1.32+ | Auto-configuration for tracing and metrics |
| **Micrometer** | 1.12+ (via Boot BOM) | Metrics collection and export (Prometheus/Datadog compatible) |
| **Spring Boot Actuator** | 3.3.x (via Boot BOM) | `/health`, `/metrics`, `/prometheus` endpoints |
| **SLF4J + Logback** | 2.x (via Boot BOM) | Structured logging with JSON output |
| **JUnit 5** | 5.10+ (via Boot BOM) | Unit and integration test framework |
| **Mockito** | 5.x (via Boot BOM) | Mocking framework for service/repository tests |
| **SpringBootTest** | 3.3.x | Integration testing with embedded server |
| **Rest Assured** | 5.4+ | REST API contract testing |

### 4.2 Frontend

| Component | Version | Purpose |
|-----------|---------|---------|
| **Node.js** | 20.x (LTS) | JavaScript runtime and package management |
| **npm** | 10.x | Package manager |
| **React** | 18.x | UI framework and component library |
| **TypeScript** | 5.x | Static type checking for JavaScript |
| **Vite** | 5.x | Build tool and dev server (ESM-first) |
| **Axios** | 1.6+ | HTTP client for REST API calls |
| **React Router** | 6.x | Client-side routing |
| **Redux Toolkit** (optional) | 1.9.x | State management (if needed for complexity) |
| **TailwindCSS** (or equivalent) | 3.x | Utility-first CSS framework |
| **Vitest** | 1.x | Unit testing framework (Vite-native) |
| **React Testing Library** | 14.x | Component testing utilities |
| **ESLint** | 8.x | Linting and code quality |
| **Prettier** | 3.x | Code formatting |

### 4.3 API Contract

| Element | Specification |
|---------|---------------|
| **Protocol** | REST over HTTPS (TLS 1.2+) |
| **API Version** | v1 |
| **Format** | JSON |
| **OpenAPI Specification** | 3.0.3 |
| **Authentication Scheme** | OAuth2 Bearer Token (JWT) |
| **Content-Type** | application/json |

### 4.4 Build and Runtime

| Element | Detail |
|---------|--------|
| **Container Image** | openjdk:21-slim or official eclipse-temurin:21-jre-alpine |
| **Build Artifact** | Spring Boot JAR (executable, self-contained) |
| **Frontend Build** | Vite static bundle (`dist/`) deployed to CDN or served by Spring Boot |
| **Package Manager** | Maven for Java; npm for Node.js |

---

## 5. Security and Compliance Baseline

### 5.1 Authentication

- **Scheme:** OAuth2 Resource Server with JWT (JSON Web Token) bearer tokens.
- **Token Carrier:** `Authorization: Bearer <JWT>` HTTP header.
- **Token Validation:**
  - JWT signature verified against configured public key or JWKS endpoint.
  - Token expiration (`exp`) and issued-at (`iat`) claims validated.
  - Scope and role claims extracted for authorization.
- **Token Source (POC):** Mock issuer; production will integrate with enterprise IDP (e.g., Okta, Azure AD, Keycloak).
- **Implementation:** Spring Security `@EnableResourceServer` or Spring Boot 3.x `@EnableWebSecurity` with `oauth2ResourceServer()`.

### 5.2 Authorization (Role-Based Access Control)

- **Policy:** Role-based access control (RBAC) enforced at endpoint and service layers.
- **Roles:**
  - `ROLE_CUSTOMER_INQUIRY_READ`: Permitted to invoke `GET /api/v1/customers/{customerId}/accounts`.
  - `ROLE_ADMIN`: Administrative access (health checks, metrics).
- **Enforcement:**
  - `@PreAuthorize("hasRole('CUSTOMER_INQUIRY_READ')")` on service methods.
  - `@PostAuthorize` for row-level filtering if customer scope enforcement required (future).
- **Fallback:** If JWT validation fails or required role missing, return HTTP 401 (Unauthorized) or 403 (Forbidden).

### 5.3 Transport Security

- **Protocol:** HTTPS only; TLS 1.2 minimum.
- **Certificate:** Self-signed for POC; production will use enterprise CA-issued certificates.
- **Cipher Suites:** Modern, forward-secret-capable (e.g., ECDHE-RSA-AES128-GCM-SHA256).
- **HSTS:** Enable HTTP Strict-Transport-Security header (`max-age=31536000; includeSubDomains`).
- **No Plain HTTP:** All HTTP traffic redirected to HTTPS or rejected.

### 5.4 Input Validation

- **Path Parameters:**
  - Customer ID: exactly 10 numeric digits; reject if missing, non-numeric, or length != 10.
  - Return HTTP 400 (Bad Request) with standardized error response.
- **Query Parameters:** None defined in v1 scope; reject unexpected query strings.
- **Request Body:** None for inquiry endpoints (GET); validation framework in place for future POST/PUT.
- **Validation Implementation:**
  - `@PathVariable @Digits(integer=10, fraction=0)` on controller method parameter.
  - Custom `@Validated` annotation on service layer for business rule validation.
  - `GlobalExceptionHandler` catches `ConstraintViolationException` and returns standardized error.

### 5.5 Error Handling Policy

- **HTTP Status Codes:**
  - `200 OK`: Successful inquiry, customer found or not found (see response body).
  - `400 Bad Request`: Invalid customer ID format or missing required parameter.
  - `401 Unauthorized`: Missing or invalid OAuth2 token.
  - `403 Forbidden`: Token valid but user lacks required role.
  - `404 Not Found`: Endpoint does not exist.
  - `500 Internal Server Error`: Unexpected server failure.
  - `503 Service Unavailable`: Downstream repository or mock store unavailable.

- **Standardized Error Response:**
  ```json
  {
    "errorCode": "INVALID_CUSTOMER_ID",
    "message": "Customer ID must be exactly 10 numeric digits.",
    "timestamp": "2024-01-15T10:30:00Z",
    "correlationId": "req-abc123def456",
    "details": {
      "field": "customerId",
      "value": "12345"
    }
  }
  ```

- **Legacy Error Semantics Preserved:**
  - `CUSTOMER-FOUND = 'N'` (from COBOL) → HTTP 200 with `customerFound: false` and empty accounts array.
  - `CUSTOMER-FOUND = 'Y'` → HTTP 200 with `customerFound: true` and populated accounts array.
  - No 404 status for "customer not found"; business logic determines customer existence.

### 5.6 Secrets Handling

- **Secret Types:** OAuth2 client credentials (if service-to-service), JWT signing keys, database credentials (future), API tokens.
- **Storage:**
  - **Development:** `.env` file (not committed; listed in `.gitignore`); loaded via Spring Cloud Config or `spring-dotenv`.
  - **POC/Staging:** Environment variables injected by CI/CD pipeline or container orchestrator.
  - **Production:** Enterprise secret manager (Vault, AWS Secrets Manager, Azure Key Vault); Spring Cloud Vault auto-configuration.
- **Injection Mechanism:**
  - `@Value("${oauth2.issuer-uri}")` for simple scalar values.
  - `@ConfigurationProperties` for structured configs.
  - `EnvironmentVariableCredentialsProvider` for Vault/AWS Secrets.
- **Never in Source Control:**
  - No credentials in `application.properties`, `application.yml`, or hardcoded.
  - No secrets in Docker images; inject at runtime.
  - Pre-commit hook to scan for secrets using tool like `git-secrets` or `truffleHog`.

---

## 6. API and Integration Constraints

### 6.1 REST Endpoint Specification

**Endpoint:** `GET /api/v1/customers/{customerId}/accounts`

**Purpose:** Retrieve all accounts associated with a customer (legacy INQACCCU behavior).

**Path Parameters:**
| Name | Type | Constraint | Example |
|------|------|-----------|---------|
| `customerId` | String | Exactly 10 numeric digits (no leading zeros allowed per legacy) | `0123456789` |

**Query Parameters:** None defined for v1.

**Request Headers:**
| Header | Required | Value |
|--------|----------|-------|
| `Authorization` | Yes | `Bearer <JWT>` |
| `Accept` | No | `application/json` (default) |
| `X-Correlation-ID` | No | UUID; if absent, generated by server and returned |

**Response Status Codes:**
- `200 OK`: Successful inquiry (customer found or not found).
- `400 Bad Request`: Invalid customer ID.
- `401 Unauthorized`: Missing/invalid JWT.
- `403 Forbidden`: JWT valid but role insufficient.
- `500 Internal Server Error`: Server error.

**Successful Response Body (200 OK):**
```json
{
  "customerId": "0123456789",
  "customerFound": true,
  "numberOfAccounts": 2,
  "accounts": [
    {
      "eyeCatcher": "ACCT",
      "accountNumber": "12345678",
      "sortCode