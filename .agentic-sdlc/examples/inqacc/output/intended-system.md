# Intended System Blueprint

**Document ID:** `intended-system.md`  
**Pipeline:** mainframe_modernization  
**Authority:** provided/system-intent.md + Legacy Analysis (INQACC.cbl, ACCDB2.cpy, ACCOUNT.cpy, INQACCCZ.cpy)  
**Status:** Canonical target architecture for downstream requirement and spec generation  
**Generated:** 2024

---

## 1. Feature and Modernization Objective

**Primary Goal:**  
Modernize the legacy INQACC CICS-DB2 account inquiry program into a cloud-ready, web-accessible application that preserves legacy observable behavior while enabling future integration with live mainframe systems.

**Scope of Modernization:**
- Transform synchronous DB2 account lookup into a RESTful API endpoint
- Replace CICS terminal interface with React web UI
- Maintain composite-key lookup semantics (ACCOUNT_SORTCODE + ACCOUNT_NUMBER)
- Enforce role-based access control at API boundary
- Enable structured logging and request tracing for operational visibility

**In-Scope Enhancements:**
- Input validation at boundary (HTTP contract layer)
- Standardized JSON error responses
- Correlation ID propagation for distributed tracing
- OAuth2 bearer token authentication
- Mock data repository for POC (no live DB2/CICS connection)

---

## 2. Target Product Scope

**Application Name:** INQACC Modernized Account Inquiry  
**Business Domain:** Retail Banking – Account Inquiry  
**Primary User:** Bank employees performing account lookups  
**Primary Actors:**
- Authenticated bank employee (role: `ACCOUNT_INQUIRER` or above)
- Backend account inquiry service
- Mock repository (POC mode)

**User Stories (Summary):**
- US-001: As an authenticated bank employee, I can query an account by sortcode and account number to retrieve full account details
- US-002: As a bank employee, I receive clear error messages when sortcode or account number are invalid
- US-003: As an operations engineer, I can observe request latency, error rates, and correlation IDs in structured logs

**Deliverables:**
1. Spring Boot REST API (Java 21, Spring Boot 3.3.x)
2. React web application (TypeScript 5.x, Vite 5.x)
3. Mock repository adapter (in-memory or embedded database)
4. OpenAPI 3.0.3 specification (auto-generated from Spring)
5. Deployment artifacts (Docker image, Maven build)
6. Operational dashboards and logging pipeline configuration

---

## 3. Architecture Blueprint

### 3.1 High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser / Web Client                    │
│              (React 18.x + TypeScript 5.x)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS (TLS 1.2+)
                       │ Bearer Token (Authorization header)
                       │ Correlation ID (X-Correlation-ID header)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│             Spring Boot 3.3.x REST API Gateway              │
│                    (Java 21 Runtime)                        │
├─────────────────────────────────────────────────────────────┤
│ Spring Security OAuth2 Resource Server                      │
│ ├─ Token Validation (JWT bearer token)                      │
│ └─ Role-Based Authorization (ACCOUNT_INQUIRER role)        │
├─────────────────────────────────────────────────────────────┤
│ REST Controller Layer (@RestController)                     │
│ └─ GET /v1/accounts/{sortcode}/{accountNumber}             │
│    ├─ Path parameter validation                             │
│    ├─ Request header extraction (X-Correlation-ID)          │
│    └─ Response envelope (HTTP 200, 400, 401, 404, 500)     │
├─────────────────────────────────────────────────────────────┤
│ Service Layer (@Service)                                    │
│ └─ AccountInquiryService                                    │
│    ├─ Execute business rule BR-001 (composite key lookup)   │
│    ├─ Coordinate repository access                          │
│    ├─ Error translation to standardized JSON responses      │
│    └─ Correlation ID propagation                            │
├─────────────────────────────────────────────────────────────┤
│ Repository / Data Access Layer (@Repository)                │
│ └─ AccountRepository (Spring Data JPA or custom DAO)        │
│    ├─ Mock persistence layer (H2 embedded or in-memory)     │
│    ├─ Parameterized query: SELECT * FROM account           │
│    │  WHERE sortcode = ? AND account_number = ?             │
│    └─ Entity-to-DTO mapping                                 │
├─────────────────────────────────────────────────────────────┤
│ Cross-Cutting Concerns                                      │
│ ├─ Structured Logging (SLF4J + Logback; JSON format)       │
│ ├─ Correlation ID Management (MDC or request context)       │
│ ├─ Exception Translation (@ExceptionHandler)                │
│ └─ Input Validation (Bean Validation + custom validators)   │
└─────────────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│            Mock Data Repository Layer                       │
│        (H2 Embedded or In-Memory HashMap)                   │
│ ├─ Seed data: 20+ pre-configured account records            │
│ ├─ Account table schema matches ACCDB2.cpy definition       │
│ ├─ Composite key index on (sortcode, account_number)        │
│ └─ Zero network latency (POC mode)                          │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Deployment Target

**Runtime Environment:**
- **Container Orchestration:** Docker (single container per environment)
- **Cloud Platform:** AWS ECS / Kubernetes / On-Premises Docker host
- **Application Server:** Embedded Tomcat (Spring Boot default)
- **Port Exposure:** HTTPS 8443 (TLS termination at ingress) or 8080 (HTTP via load balancer proxy)

**Frontend Deployment:**
- **Build Output:** Static files (HTML, JavaScript, CSS) via Vite 5.x build
- **Hosting:** CloudFront / S3 (AWS) or static file server (on-premises)
- **API Base URL:** Configurable via environment variable or config file

---

## 4. Technology Stack and Versions

### 4.1 Backend Stack

| Component | Version | Purpose | Rationale |
|-----------|---------|---------|-----------|
| **Java Runtime** | 21 (LTS) | Application runtime | LTS release; modern language features; production-grade stability |
| **Spring Boot** | 3.3.x | REST API framework | Latest stable; Spring Security 6.x OAuth2 resource server; Spring Data JPA |
| **Spring Framework** | 6.x (embedded in Boot) | Core IoC, AOP, web | Latest stable; comprehensive feature set |
| **Spring Security** | 6.x | OAuth2 resource server, RBAC | Native JWT bearer token support; role-based method security |
| **Spring Data JPA** | 3.x | Data access abstraction | Repository pattern; entity mapping; query DSL |
| **Maven** | 3.9+ | Build tool | Reproducible builds; dependency management; plugins for code quality |
| **H2 Database** | 2.x or latest | Mock persistence (POC) | Lightweight embedded; supports full SQL; in-memory or file-based modes |
| **SLF4J** | 2.x | Logging facade | Standardized; integrates with Logback |
| **Logback** | 1.4.x+ | Logging implementation | JSON output support; correlation ID MDC integration |
| **Jackson** | 2.15.x+ | JSON serialization | Built into Spring Boot; customizable serialization |
| **Bean Validation (Jakarta)** | 3.0.x | Input validation | JSR-380; @NotNull, @Pattern, @Size annotations |
| **OpenAPI 3.0.3** | Generated from annotations | API contract | Spring Boot 3.3.x auto-generates from @RestController |
| **Springdoc OpenAPI** | 2.x (optional) | OpenAPI documentation | Swagger UI auto-generation (if required) |

### 4.2 Frontend Stack

| Component | Version | Purpose | Rationale |
|-----------|---------|---------|-----------|
| **Node.js** | 20 LTS | JavaScript runtime | LTS release; npm package manager |
| **React** | 18.x | UI framework | Industry standard; hooks-based stateful components; ecosystem maturity |
| **TypeScript** | 5.x | Type safety | Compile-time error detection; improved developer experience; long-term maintainability |
| **Vite** | 5.x | Build tool & dev server | Fast HMR; optimized production builds; native ES module support |
| **Axios** | 1.6.x+ | HTTP client | Simple API; request/response interceptors for correlation ID propagation |
| **React Query** (optional) | 5.x | Server state management | Automatic caching; request deduplication; background sync (if required) |
| **React Testing Library** | 14.x+ | UI component testing | Best practices alignment; accessible component testing |
| **Vitest** | 1.x+ | Unit test framework | Vite-native; Jest-compatible API; fast execution |

### 4.3 DevOps & Infrastructure Stack

| Component | Version | Purpose | Rationale |
|-----------|---------|---------|-----------|
| **Docker** | 20.x+ | Containerization | Consistent environment across dev/test/prod |
| **Docker Compose** | 2.x+ | Local orchestration | Multi-container local development (backend + database) |
| **Kubernetes** | 1.26+ (optional) | Container orchestration | Scalability; self-healing; rolling updates (future-proofing) |
| **Git** | 2.40+ | Version control | Source code management; branching strategy |
| **GitHub Actions** (or equivalent) | Native CI/CD | Automated build & test | Per-commit validation; integration test execution |
| **TLS Certificate** | 1.2+ / 1.3 | Transport security | HTTPS enforcement; certificate management via cert-manager or cloud provider |

### 4.4 Security & Authentication Stack

| Component | Version | Purpose | Rationale |
|-----------|---------|---------|-----------|
| **OAuth2 Authorization Server** | (External) | Bearer token issuance | Pre-configured; OIDC-compliant (e.g., Keycloak, Okta, AWS Cognito) |
| **JWT (JSON Web Token)** | Standard (RFC 7519) | Token format | Self-contained claims; signature validation; no database lookup required |
| **Spring Security OAuth2 Resource Server** | 6.x | Token validation | Native Spring support; validates JWT signature and expiration |
| **TLS** | 1.2 or 1.3 | Transport security | HTTPS enforcement; certificate-based authentication |
| **Secrets Manager** | (Cloud provider native) | Credentials storage | Environment variables injected at container runtime; no hardcoded secrets |

---

## 5. Security and Compliance Baseline

### 5.1 Authentication

**Mechanism:** OAuth2 Bearer Token (JWT)

**Flow:**
1. User (bank employee) authenticates via external OAuth2 provider (e.g., corporate identity provider)
2. Provider issues JWT bearer token with claims: `sub` (user ID), `aud` (audience), `scope` (e.g., `account:read`), `roles` (e.g., `["ACCOUNT_INQUIRER"]`)
3. Client includes token in Authorization header: `Authorization: Bearer <jwt_token>`
4. Spring Security OAuth2 Resource Server validates:
   - Token signature (using provider's public key)
   - Token expiration
   - Issuer (iss claim)
   - Audience (aud claim) matches application
5. On success, authentication object is populated with user principal and authorities

**Configuration (Spring Boot):**
```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://auth-server.internal/.well-known/openid-configuration
          jwk-set-uri: https://auth-server.internal/keys
```

**Token Claims (Required):**
- `sub`: Subject (user ID)
- `aud`: Audience (must include application identifier)
- `exp`: Expiration time (Unix timestamp)
- `iat`: Issued at (Unix timestamp)
- `iss`: Issuer URI
- `scope`: Space-separated scopes (must include `account:read` or similar)

### 5.2 Authorization

**Model:** Role-Based Access Control (RBAC)

**Roles:**
- `ACCOUNT_INQUIRER`: Allows GET account inquiry endpoint
- `ACCOUNT_ADMIN`: Implicit superuser (future use)

**Enforcement:**
```java
@GetMapping("/v1/accounts/{sortcode}/{accountNumber}")
@PreAuthorize("hasRole('ACCOUNT_INQUIRER')")
public ResponseEntity<AccountResponseDto> getAccount(
    @PathVariable String sortcode,
    @PathVariable String accountNumber,
    @RequestHeader(value = "X-Correlation-ID", required = false) String correlationId
) { ... }
```

**Authorization Failure Response:**
- HTTP 403 Forbidden if user lacks required role
- HTTP 401 Unauthorized if token is missing or invalid

### 5.3 Transport Security

**Protocol:** HTTPS (TLS 1.2 minimum; TLS 1.3 preferred)

**Certificate Management:**
- Production: Enterprise certificate from trusted CA (not self-signed)
- Non-prod: Self-signed certificate acceptable during development (with browser trust override)
- Rotation: Automated via cloud provider (AWS ACM, Azure Key Vault) or cert-manager (Kubernetes)

**Spring Boot Configuration:**
```yaml
server:
  ssl:
    enabled: true
    key-store: /etc/inqacc/keystore.p12
    key-store-password: ${KEYSTORE_PASSWORD}  # Injected via environment variable
    key-store-type: PKCS12
    protocol: TLSv1.2
```

**HSTS (HTTP Strict Transport Security):**
- Response header: `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- Enforcement via Spring Security:
```java
@Configuration
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.headers(headers -> headers.httpStrictTransportSecurity().maxAgeInSeconds(31536000));
        return http.build();
    }
}
```

### 5.4 Input Validation

**Layer 1: HTTP Contract Validation (Spring MVC)**
- Path parameter validation: `@PathVariable` with `@Pattern` annotation
- Query parameter validation: `@RequestParam` with `@Size`, `@NotNull`
- Request body validation: `@Valid` on DTO classes

**Example (Path Parameters):**
```java
@GetMapping("/v1/accounts/{sortcode}/{accountNumber}")
public ResponseEntity<AccountResponseDto> getAccount(
    @PathVariable
    @Pattern(regexp = "^\\d{6}$", message = "Sortcode must be exactly 6 digits")
    String sortcode,
    
    @PathVariable
    @Pattern(regexp = "^\\d{8}$", message = "Account number must be exactly 8 digits")
    String accountNumber
) { ... }
```

**Layer 2: Business Logic Validation (Service)**
- Null checks
- Business rule enforcement (e.g., account active status)
- Cross-field validation

**Layer 3: Rejection Policy**
- Reject all invalid input immediately
- Return HTTP 400 Bad Request with structured error detail
- Include validation error message in error envelope (see §5.6)

### 5.5 Error Handling Policy

**Principle:** Fail securely; never expose system internals in error responses

**Error Categories:**

| Category | HTTP Status | Example