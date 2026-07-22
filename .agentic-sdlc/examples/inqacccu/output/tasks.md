# tasks.md

**Document ID:** `tasks-inqacccu-modernization-001`  
**Pipeline:** `mainframe_modernization`  
**Generated:** TaskAgent for INQACCCU Modernization  
**Status:** Implementation-Ready  
**Last Updated:** 2025

---

## Task Inventory

### TASK-001: Spring Boot Project Scaffolding & Dependency Management

**ID:** TASK-001  
**Title:** Initialize Spring Boot 3.3.x Maven project with core dependencies  
**Description:**  
Create a new Maven-based Spring Boot 3.3.x project with Java 21 target. Include dependencies for Spring Web, Spring Security (OAuth2 Resource Server), Spring Data (mock persistence), Micrometer Metrics, OpenTelemetry, Jackson (JSON serialization), Lombok, and JUnit 5. Configure `pom.xml` with Maven 3.9+ and establish build profiles for development, test, and production. Set up `.gitignore` to exclude secrets and build artifacts.

**Linked Requirements:**  
- REQ-ARCH-001 (Backend Stack: Java 21, Spring Boot 3.3.x)  
- REQ-SEC-001 (OAuth2 Resource Server Configuration)  
- NFR-008 (Metrics & Observability)  
- NFR-009 (Distributed Tracing Readiness)

**Linked Business Rules:**  
- BR006 (Secrets Management)

**Dependencies:**  
None (foundation task)

**Estimate:** S (Small)

**Acceptance Criteria:**
- [ ] AC-001.1: Maven project builds successfully with `mvn clean package` on Java 21
- [ ] AC-001.2: All required Spring dependencies declared and versions pinned
- [ ] AC-001.3: Build profiles (dev, test, prod) configured and selectable
- [ ] AC-001.4: `.gitignore` excludes `secrets/`, `target/`, `*.env` files
- [ ] AC-001.5: GitHub Actions or equivalent CI pipeline triggers on commit

**Definition of Done:**
- Source repository initialized
- `pom.xml` validated against Spring Boot 3.3.x release notes
- Build succeeds on clean environment
- `.m2` dependencies downloaded and cached
- README documents build and run instructions

---

### TASK-002: OpenAPI 3.0.3 Contract & API Documentation

**ID:** TASK-002  
**Title:** Define and publish OpenAPI 3.0.3 specification for `/api/v1/customers/{customerId}/accounts`  
**Description:**  
Produce an OpenAPI 3.0.3 specification document (YAML or JSON) that formally defines the REST endpoint contract. Include request/response schemas derived from COBOL copybooks (INQACCCUZ, ACCOUNT, ACCDB2), all HTTP status codes (200, 400, 401, 403, 500), and OAuth2 security scheme. Configure Spring Boot with `springdoc-openapi-starter-webmvc-ui` to auto-generate Swagger UI. Document field constraints (10-digit customer ID, 0–20 account limit, field lengths, decimal precision).

**Linked Requirements:**  
- REQ-API-001 (REST Endpoint Contract)  
- REQ-API-002 (Request/Response Schemas)  
- REQ-SEC-001 (OAuth2 Bearer Token Validation)

**Linked Business Rules:**  
- BR001 (Customer Inquiry Acceptance)  
- BR002 (Account Details Mapping)  
- BR003 (Input Validation Strictness)

**Dependencies:**  
- TASK-001 (Spring Boot scaffolding)

**Estimate:** M (Medium)

**Acceptance Criteria:**
- [ ] AC-002.1: OpenAPI 3.0.3 YAML file created and committed to `docs/openapi.yaml`
- [ ] AC-002.2: All request/response objects match COBOL field definitions (customerId format, account array structure)
- [ ] AC-002.3: OAuth2 securityScheme defined with Bearer token requirement
- [ ] AC-002.4: HTTP status codes (200, 400, 401, 403, 500) documented with example responses
- [ ] AC-002.5: Swagger UI accessible at `/swagger-ui.html` and auto-generated from specification
- [ ] AC-002.6: Input validation rules (10-digit customer, max 20 accounts) reflected in schema constraints

**Definition of Done:**
- OpenAPI document reviewed and approved by architecture team
- Swagger UI renders correctly in browser
- No validation errors in specification (use `spectacle` or OpenAPI linter)
- Documentation includes example customer inquiry scenarios

---

### TASK-003: OAuth2 Resource Server Configuration & JWT Validation

**ID:** TASK-003  
**Title:** Implement Spring Security OAuth2 resource server with JWT bearer token validation  
**Description:**  
Configure Spring Security as an OAuth2 resource server to intercept HTTP requests, extract and validate JWT bearer tokens, and enforce role-based access control (RBAC). Define security rules to require `CUSTOMER_INQUIRY_READ` role for `/api/v1/customers/*/accounts` endpoints. Integrate with external OIDC provider (mock or real) for token validation. Set up exception handling for missing (`401`) and insufficient (`403`) authorization. Document required environment variables (`OAUTH2_JWK_SET_URI`, `OAUTH2_ISSUER_URI`, etc.) in a `.env.example` file.

**Linked Requirements:**  
- REQ-SEC-001 (OAuth2 Resource Server)  
- REQ-SEC-002 (JWT Bearer Token Validation)  
- REQ-SEC-003 (Role-Based Access Control)

**Linked Business Rules:**  
- BR006 (Secrets Management)

**Dependencies:**  
- TASK-001 (Spring Boot scaffolding)

**Estimate:** M (Medium)

**Acceptance Criteria:**
- [ ] AC-003.1: Spring Security OAuth2 resource server configured in `SecurityConfig.java`
- [ ] AC-003.2: Valid JWT with `CUSTOMER_INQUIRY_READ` role returns 200 OK
- [ ] AC-003.3: Missing bearer token returns 401 Unauthorized with JSON error response
- [ ] AC-003.4: Valid JWT with insufficient role returns 403 Forbidden with JSON error response
- [ ] AC-003.5: Token validation integrates with configurable JWK Set URI (environment variable)
- [ ] AC-003.6: `.env.example` documents all required OAuth2 environment variables

**Definition of Done:**
- Security configuration passes Spring Security audit
- Integration tests validate token validation and RBAC logic
- Error responses match OpenAPI specification
- No hardcoded secrets in source code

---

### TASK-004: Input Validation & Error Response Standardization

**ID:** TASK-004  
**Title:** Implement strict input validation and standardized error response handling  
**Description:**  
Create a centralized input validation layer to enforce customer ID format (exactly 10 digits, numeric only), reject leading zeros (legacy COBOL behavior), and validate query parameters. Implement a global `@ControllerAdvice` exception handler to catch validation errors and return standardized JSON error responses matching OpenAPI specification. Error responses must include `status`, `message`, `timestamp`, and `correlationId`. Configure JSR-303/Jakarta Validation annotations on DTOs. Test edge cases: empty customer ID, 11-digit ID, alphanumeric characters, null/missing path variables.

**Linked Requirements:**  
- REQ-API-001 (Request Validation)  
- REQ-API-003 (Standardized Error Responses)

**Linked Business Rules:**  
- BR003 (Input Validation Strictness)

**Dependencies:**  
- TASK-002 (OpenAPI contract definition)

**Estimate:** M (Medium)

**Acceptance Criteria:**
- [ ] AC-004.1: Customer ID validated as exactly 10 numeric digits via `@Pattern` annotation
- [ ] AC-004.2: Invalid format (e.g., "12345678AB") returns 400 Bad Request with detailed error message
- [ ] AC-004.3: Global exception handler catches `ConstraintViolationException` and `MethodArgumentNotValidException`
- [ ] AC-004.4: All error responses include `status`, `message`, `timestamp`, and `correlationId` fields
- [ ] AC-004.5: Edge cases tested: empty string, null, 11-digit, alphabetic, special characters
- [ ] AC-004.6: Input validation preserves legacy COBOL behavior (no fuzzy matching or padding)

**Definition of Done:**
- Unit tests cover all validation paths
- Integration tests validate error response format against OpenAPI spec
- Code review confirms no duplicate validation logic across endpoints
- Documentation includes validation rule reference

---

### TASK-005: Customer Account Repository Mock Implementation

**ID:** TASK-005  
**Title:** Implement in-memory mock repository for customer account data (POC phase)  
**Description:**  
Create a `CustomerAccountRepository` interface and in-memory `MockCustomerAccountRepository` implementation to return hardcoded test data for POC validation. The mock shall return 0–20 accounts per customer based on predefined test dataset (e.g., customer "0000000001" returns 2 accounts, "0000000002" returns 5 accounts, others return 0). Implement account data with all fields mapped from COBOL copybooks (account number, sort code, balance, interest rate, statement date, account status). Set up a Spring `@Configuration` class to conditionally wire the mock (POC) or real adapter (production). Include integration tests to validate data structure and account count limits.

**Linked Requirements:**  
- REQ-DATA-001 (Mock Persistence for POC)  
- REQ-DATA-002 (Account Data Mapping)

**Linked Business Rules:**  
- BR001 (Customer Inquiry Acceptance)  
- BR002 (Account Details Mapping)  
- BR004 (Account Status Preservation)

**Dependencies:**  
- TASK-001 (Spring Boot scaffolding)

**Estimate:** M (Medium)

**Acceptance Criteria:**
- [ ] AC-005.1: `CustomerAccountRepository` interface defined with `findAccountsByCustomerId(String customerId)` method
- [ ] AC-005.2: Mock implementation returns 0–20 accounts; no accounts found returns empty list (not null)
- [ ] AC-005.3: Test dataset includes customers with 0, 2, 5, and 20 accounts
- [ ] AC-005.4: Account objects include all COBOL-mapped fields (account number, sort code, balance, interest rate, statement date, status)
- [ ] AC-005.5: Spring profile `mock` activates mock repository; `production` profile loads real adapter stub
- [ ] AC-005.6: Integration tests validate correct account count and field presence for multiple customers

**Definition of Done:**
- Repository interface and mock implementation committed
- Test data fixtures documented in code
- Spring configuration verified to switch implementations via `@ActiveProfiles`
- No direct database calls in POC mode

---

### TASK-006: Customer Account Service Layer Implementation

**ID:** TASK-006  
**Title:** Implement business logic service layer (`CustomerAccountService`)  
**Description:**  
Create a `CustomerAccountService` class to orchestrate customer account inquiry business logic. The service receives a customer ID from the controller, invokes the repository to retrieve accounts, and applies business rules (BR001–BR004): validate customer found flag, enforce 0–20 account limit, preserve account status, and apply any future feature toggles. Service shall be thin-controller, thick-service design. Implement feature toggle framework (e.g., Spring Cloud Config or custom enum-based toggles) to enable/disable enhancements. Include logging of service method entry/exit with customer ID (non-sensitive) and account count. Implement timeout handling for repository calls (mock: no timeout required; production: 5-second default).

**Linked Requirements:**  
- REQ-BUS-001 (Business Logic Preservation)  
- REQ-ARCH-001 (Thin Controller, Thick Service Pattern)  
- NFR-006 (Feature Toggles)

**Linked Business Rules:**  
- BR001, BR002, BR003, BR004, BR005 (Core inquiry logic and toggles)

**Dependencies:**  
- TASK-005 (Repository implementation)

**Estimate:** M (Medium)

**Acceptance Criteria:**
- [ ] AC-006.1: `CustomerAccountService` class implements inquiry logic with repository dependency injection
- [ ] AC-006.2: Service method returns `CustomerAccountsResponse` DTO matching OpenAPI schema
- [ ] AC-006.3: Service validates `numberOfAccounts` <= 20 and returns error if exceeded (data integrity safeguard)
- [ ] AC-006.4: Feature toggle framework integrated; `@FeatureToggle` annotation supports method-level toggles
- [ ] AC-006.5: Debug/info logging captures customer ID and account count (no sensitive data logged)
- [ ] AC-006.6: Unit tests mock repository and validate service logic for multiple customer scenarios (0, 2, 20 accounts)
- [ ] AC-006.7: Timeout handling tested (mock: passthrough; production: enforced at adapter level)

**Definition of Done:**
- Service class follows Spring best practices (dependency injection, transactional boundaries)
- All business rules (BR001–BR005) validated in unit tests
- Code review confirms no direct database calls or HTTP calls in service
- Documentation maps service methods to business rules

---

### TASK-007: REST Controller Implementation

**ID:** TASK-007  
**Title:** Implement Spring REST controller for `/api/v1/customers/{customerId}/accounts` endpoint  
**Description:**  
Create a `CustomerAccountController` class with a single REST endpoint handler for `GET /api/v1/customers/{customerId}/accounts`. The controller shall be thin: extract path variable (customer ID), invoke service, and return response. Add `@SecurityRequirement` annotation for OpenAPI to reflect OAuth2 requirement. Implement error handling delegation to global exception handler (TASK-004). Add request/response logging via Spring interceptor. Include correlation ID extraction from request header (`X-Correlation-ID`) or generation if missing; pass correlation ID to service for tracing. Configure `@RequestMapping` with API versioning (`/api/v1`).

**Linked Requirements:**  
- REQ-API-001 (REST Endpoint)  
- REQ-SEC-002 (OAuth2 Enforcement at Controller)  
- NFR-010 (Correlation ID Tracing)

**Linked Business Rules:**  
- BR001 (Customer Inquiry Acceptance)

**Dependencies:**  
- TASK-006 (Service layer)  
- TASK-003 (OAuth2 configuration)

**Estimate:** S (Small)

**Acceptance Criteria:**
- [ ] AC-007.1: Controller class defined at `@RequestMapping("/api/v1/customers")`
- [ ] AC-007.2: GET handler method `/api/v1/customers/{customerId}/accounts` returns 200 with response body
- [ ] AC-007.3: `@SecurityRequirement(name = "oauth2")` annotation present for OpenAPI
- [ ] AC-007.4: Path variable `customerId` auto-validated via JSR-303 (delegated from TASK-004)
- [ ] AC-007.5: Correlation ID extracted from `X-Correlation-ID` header or UUID generated if missing
- [ ] AC-007.6: Correlation ID passed to service and included in response headers
- [ ] AC-007.7: Integration tests validate endpoint returns correct response and status codes

**Definition of Done:**
- Controller code reviewed for thin-controller pattern compliance
- Endpoint registered in Swagger UI and OpenAPI spec
- Integration tests cover success and error scenarios
- Correlation ID tracing verified end-to-end

---

### TASK-008: Structured Logging & Correlation ID Infrastructure

**ID:** TASK-008  
**Title:** Configure structured JSON logging with correlation IDs and request tracing  
**Description:**  
Integrate Logback and SLF4J to output structured JSON logs (not plain text). Configure Logback to include timestamp, log level, logger name, message, and correlation ID in every log line. Implement a request filter to extract or generate correlation ID from `X-Correlation-ID` header and bind to Mapped Diagnostic Context (MDC). Ensure correlation ID is included in all downstream logs without explicit parameter passing. Configure JSON output format using Logstash Logback Encoder or Jackson JSON provider. Test logs with a simple request and verify JSON structure. Document correlation ID usage in deployment guide.

**Linked Requirements:**  
- NFR-007 (Structured Logging)  
- NFR-010 (Correlation ID Tracing)

**Linked Business Rules:**  
- None directly

**Dependencies:**  
- TASK-001 (Spring Boot scaffolding)

**Estimate:** M (Medium)

**Acceptance Criteria:**
- [ ] AC-008.1: Logback configuration uses Logstash Logback Encoder or equivalent JSON provider
- [ ] AC-008.2: All logs include fields: `timestamp`, `level`,