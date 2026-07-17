# INQACC Modernized Account Inquiry – Implementation Tasks

**Document ID:** `tasks.md`  
**Pipeline:** mainframe_modernization  
**Authority:** system-intent.md + intended-system.md + business-rules.md + requirements.md + spec.md + plan.md + program-analysis.md + mapping-matrix.md + traceability-matrix.md + test-spec.md + openapi.yaml  
**Status:** Implementation-ready task catalog  
**Generated:** 2024  
**Target Stack:** Java 21 + Spring Boot 3.3.x | React 18.x + TypeScript 5.x + Vite 5.x | Mock Repository (POC)  
**Delivery Horizon:** 26 weeks (6 months) to production readiness

---

## Executive Summary

This document defines **42 actionable engineering tasks** organized across **4 delivery phases** and **8 workstreams** (API Contract, Backend Service, Persistence, Authorization, Frontend, Integration, Observability, Deployment). Each task includes explicit dependencies, sizing estimates (S/M/L), requirement/rule mappings, and definition of done criteria. Tasks are sequenced to unblock parallel work while maintaining critical path integrity (API contract freeze by week 4, mock repository by week 8, E2E readiness by week 16).

---

## Task Catalog

---

## PHASE 1: Foundation & Contract Design (Weeks 1–4)

---

### TASK-001: Establish OpenAPI 3.0.3 Specification for Account Inquiry Endpoint

**Task ID:** `TASK-001`  
**Category:** API Contract Design  
**Phase:** 1  
**Week:** 1  
**Workstream:** API Contract  
**Estimate:** M (Medium)

**Description:**
Design and document the canonical OpenAPI 3.0.3 specification for the account inquiry REST endpoint. The specification shall define request/response schemas, path parameters, authentication requirements, error responses, and HTTP status codes aligned to FR-001, FR-002, BR-001, and MOD-001. Specification shall be generated from source of truth (manual or Spring Boot annotation-driven), reviewed for completeness, and frozen for downstream consumer integration.

**Requirements Linked:**
- `FR-001`: Execute Account Lookup by Composite Key
- `FR-002`: Validate Sortcode and Account Number Format
- `FR-003`: Return Standardized Account Record JSON
- `FR-004`: Return HTTP 400 Bad Request for Invalid Input
- `FR-005`: Return HTTP 404 Not Found for No Match
- `FR-006`: Return HTTP 401 Unauthorized for Missing/Invalid Token

**Business Rules Linked:**
- `BR-001`: Account Record Lookup by Composite Key (trigger, inputs, processing logic, outputs, error conditions)
- `BR-002`: Sortcode Format Validation (6 numeric digits)
- `BR-003`: Account Number Format Validation (8 numeric digits)

**Dependencies:**
- None (critical path starter)

**Acceptance Criteria:**
1. `AC-OP-001`: OpenAPI 3.0.3 JSON/YAML file includes GET endpoint `/accounts/{sortcode}/{accountNumber}`
2. `AC-OP-002`: Request path parameters include `sortcode` (pattern: `^\d{6}$`) and `accountNumber` (pattern: `^\d{8}$`) with correct schema type and examples
3. `AC-OP-003`: Success response (HTTP 200) includes `AccountResponse` schema with 12 fields: `eyecatcher`, `customerNumber`, `sortcode`, `accountNumber`, `accountType`, `accountStatus`, `openingDate`, `currency`, `balance`, `availableBalance`, `lastUpdated`, `description`
4. `AC-OP-004`: HTTP 400 error response includes `ErrorResponse` schema with `code`, `message`, `correlationId`, `timestamp` fields
5. `AC-OP-005`: HTTP 404 error response includes `ErrorResponse` schema with correlation ID
6. `AC-OP-006`: HTTP 401 error response includes `ErrorResponse` schema with correlation ID
7. `AC-OP-007`: Security scheme defined as `OAuth2Bearer` (type: http, scheme: bearer)
8. `AC-OP-008`: Optional `X-Correlation-ID` request header documented (UUID format); response includes `X-Correlation-ID` header
9. `AC-OP-009`: Specification includes server definitions for dev (http://localhost:8080/v1), test, UAT, and prod environments
10. `AC-OP-010`: Specification signed off by architecture team; no further breaking changes permitted without governance approval

**Definition of Done:**
- OpenAPI 3.0.3 file (openapi.yaml) validated against OpenAPI 3.0.3 schema
- Specification matches output/openapi.yaml from artifact library
- Code review completed by architecture team and API lead
- Specification published to API portal or versioned in source repository (v1.0.0 tag)
- Downstream consumers (frontend, test automation, client code generation) notified of availability
- Zero breaking changes permitted after sign-off without formal change control

---

### TASK-002: Set Up Maven Build Configuration and Spring Boot Project Structure

**Task ID:** `TASK-002`  
**Category:** Build & Infrastructure  
**Phase:** 1  
**Week:** 1–2  
**Workstream:** Backend Service  
**Estimate:** M (Medium)

**Description:**
Initialize Maven-based Spring Boot 3.3.x project structure with Java 21 compilation target. Configure parent POM, dependency management (Spring Boot BOM, Spring Cloud, testing libraries), Maven plugins (compiler, Surefire, Jacoco, Shade for assembly), build profiles (dev, test, prod), and reproducible build settings. Establish project layout following Spring Boot conventions: src/main/java, src/main/resources, src/test/java, src/test/resources.

**Requirements Linked:**
- `FR-011`: Technology stack conformance (Java 21, Spring Boot 3.3.x, Maven 3.9+)

**Business Rules Linked:**
- None (infrastructure)

**Dependencies:**
- None (critical path starter)

**Acceptance Criteria:**
1. `AC-BUILD-001`: Maven pom.xml created with Spring Boot 3.3.x parent POM
2. `AC-BUILD-002`: Java 21 compilation target configured (maven-compiler-plugin source/target = 21)
3. `AC-BUILD-003`: Spring Web, Spring Data JPA, Spring Security, Spring Cloud OpenFeign dependencies declared
4. `AC-BUILD-004`: Testing dependencies included (JUnit 5, Mockito, Spring Boot Test, REST Assured)
5. `AC-BUILD-005`: Maven Shade plugin configured for uber-JAR assembly (if required)
6. `AC-BUILD-006`: Jacoco code coverage plugin configured with 85% line coverage threshold
7. `AC-BUILD-007`: Build profiles defined: `dev` (logging=DEBUG, mocked-auth=enabled), `test` (in-memory H2), `prod` (external OAuth2)
8. `AC-BUILD-008`: Project compiles cleanly: `mvn clean compile` succeeds
9. `AC-BUILD-009`: Unit test skeleton executes: `mvn test` runs (0 failures expected initially)
10. `AC-BUILD-010`: Maven build is reproducible (no non-deterministic outputs; timestamps, build IDs stable)

**Definition of Done:**
- pom.xml checked into version control with proper encoding (UTF-8)
- Project directory structure follows Spring Boot conventions
- README.md includes build and run instructions
- CI/CD pipeline (GitHub Actions, Jenkins) configured to execute `mvn clean package`
- Build succeeds on CI and locally with same output hash (reproducible build)
- No compile warnings or errors

---

### TASK-003: Configure OAuth2 Resource Server and JWT Bearer Token Validation

**Task ID:** `TASK-003`  
**Category:** Authorization & Security  
**Phase:** 1  
**Week:** 2–3  
**Workstream:** Authorization  
**Estimate:** M (Medium)

**Description:**
Configure Spring Security OAuth2 Resource Server to validate incoming JWT bearer tokens against a pre-configured authorization server (e.g., Keycloak, Auth0, or in-memory for dev). Implement token validation, role extraction (ACCOUNT_INQUIRER), and SecurityContext population. Create mock OAuth2 adapter for POC environments that generates signed tokens for testing. Integrate with `AccountInquiryController` to enforce `@PreAuthorize("hasRole('ACCOUNT_INQUIRER')")` on account inquiry endpoints.

**Requirements Linked:**
- `FR-006`: Return HTTP 401 Unauthorized for Missing/Invalid Token
- `FR-007`: Return HTTP 403 Forbidden for User Lacking ACCOUNT_INQUIRER Role
- `FR-009`: Enforce Role-Based Access Control (ACCOUNT_INQUIRER)

**Business Rules Linked:**
- `BR-004`: User Authentication and Role Verification (trigger, processing, outputs, error conditions)

**Dependencies:**
- TASK-001 (API contract must define security scheme)
- TASK-002 (Maven build with Spring Security dependency)

**Acceptance Criteria:**
1. `AC-AUTH-001`: Spring Security OAuth2 Resource Server configured via `application.yml` (issuer-uri, JWK set-uri, audience validation)
2. `AC-AUTH-002`: JWT bearer token validation interceptor implemented as Spring Security `@Component` or `@Configuration` class
3. `AC-AUTH-003`: Role extraction from JWT claim `realm_access.roles` or equivalent (configurable per provider)
4. `AC-AUTH-004`: Mock OAuth2 adapter generates signed JWT tokens for dev/test with configurable expiry and role claim
5. `AC-AUTH-005`: SecurityContext populated with authenticated principal and granted authorities after token validation
6. `AC-AUTH-006`: Requests without bearer token receive HTTP 401 Unauthorized with `WWW-Authenticate: Bearer` header
7. `AC-AUTH-007`: Requests with expired or invalid token receive HTTP 401 Unauthorized with error detail in body
8. `AC-AUTH-008`: Requests with valid token but missing ACCOUNT_INQUIRER role receive HTTP 403 Forbidden
9. `AC-AUTH-009`: Integration test validates token validation flow: valid token → 200, invalid token → 401, missing role → 403
10. `AC-AUTH-010`: OAuth2 configuration extracted to environment variables (issuer-uri, client-id, client-secret); no hardcoded credentials

**Definition of Done:**
- Spring Security OAuth2 Resource Server configuration compiles and runs without errors
- Mock OAuth2 adapter generates valid JWTs that pass validation
- Integration test suite includes OAuth2 flow tests (TASK-028)
- All OAuth2 configuration externalized via environment variables or application-{profile}.yml
- Security baseline documented in README.md

---

### TASK-004: Design and Implement Account Entity and Repository Interface

**Task ID:** `TASK-004`  
**Category:** Data Access Layer  
**Phase:** 1  
**Week:** 2  
**Workstream:** Persistence  
**Estimate:** M (Medium)

**Description:**
Design Java entity class `AccountEntity` (JPA `@Entity`) mapping to 12 ACCOUNT table fields from legacy ACCDB2.cpy and ACCOUNT.cpy copybooks. Define Spring Data JPA repository interface `AccountRepository` with method signature `findBySortcodeAndNumber(String sortcode, String accountNumber)` to execute parameterized SQL SELECT with composite-key WHERE clause. Implement entity equals/hashCode using sortcode+accountNumber composite key. Document field mapping from legacy COBOL field names to modern Java property names and JSON serialization names.

**Requirements Linked:**
- `FR-001`: Execute Account Lookup by Composite Key
- `FR-003`: Return Standardized Account Record JSON

**Business Rules Linked:**
- `BR-001`: Account Record Lookup by Composite Key (data structure mapping)

**Dependencies:**
- TASK-002 (Maven build with Spring Data JPA dependency)

**Acceptance Criteria:**
1. `AC-ENTITY-001`: `AccountEntity` JPA entity class created in `com.inqacc.entity` package
2. `AC-ENTITY-002`: Entity includes 12 properties (with @JsonProperty names): `eyecatcher`, `customerNumber`, `sortcode`, `accountNumber`, `accountType`, `accountStatus`, `openingDate`, `currency`, `balance`, `availableBalance`, `lastUpdated`, `description`
3. `AC-ENTITY-003`: @Id composite key or @EmbeddedId mapping on (sortcode, accountNumber) fields
4. `AC-ENTITY-004`: @Table annotation specifies table name (default: "ACCOUNT") and schema (if applicable)
5. `AC-ENTITY-005`: Field types match program-analysis.md mapping: sortcode (String, length 6), accountNumber (String, length 8), balance (BigDecimal), openingDate (LocalDate), etc.
6. `AC-ENTITY-007`: `AccountRepository` extends `CrudRepository<AccountEntity, CompositeKey>` or uses @Query for custom finder method
7. `AC-ENTITY-008`: Repository method `findBySortcodeAndNumber(String, String)` returns `Optional<AccountEntity>`
8. `AC-ENTITY-009`: Entity includes `@ToString`, `@EqualsAndHashCode` (via Lombok or manual implementation) using composite key
9. `AC-ENTITY-010`: Mapping document created (mapping-matrix.md section 1.2) linking legacy field names → Java properties → JSON names
10. `AC-ENTITY-011`: Entity compiles; no JPA validation errors

**Definition of Done:**
- `AccountEntity` and `AccountRepository` classes committed to version control
- Entity mapping documented in mapping-matrix.md
- Unit tests verify entity instantiation and composite-key semantics (TASK-016)
- Repository method signature matches OpenAPI path parameters

---

### TASK-005: Create Mock In-Memory Account Repository Implementation

**Task ID:** `TASK-005`  
**Category:** Data Access Layer  
**Phase:** 1  
**Week:** 2–3  
**Workstream:** Persistence  
**Estimate:** M (Medium)

**Description:**
Implement mock in-memory account repository (no external database) with 10–20 predefined account test records. Load test data at application startup from CSV, JSON, or hardcoded initialization. Implement `AccountRepository.findBySortcodeAndNumber()` using stream operations or HashMap lookup. Support both dev/test profile (in-memory map) and future prod profile (JPA-based). Ensure mock data covers happy path (valid lookups), edge cases (zero results), and test-specific scenarios (special account types for negative testing).

**Requirements Linked:**
- `FR-001`: Execute Account Lookup by Composite Key (mock implementation)
- `FR-005`: Return HTTP 404 Not Found (mock returns empty Optional)

**Business Rules Linked:**
- `BR-001`: Account Record Lookup by Composite Key (mock data must conform to BR rules)

**Dependencies:**
- TASK-004 (Repository interface and entity definition)

**Acceptance Criteria:**
1. `AC-MOCK-001`: `InMemoryAccountRepository` class implements `AccountRepository` interface
2. `AC-MOCK-002`: Mock repository loads 10–20 test account records at startup (via `@PostConstruct` or `ApplicationRunner`)
3. `AC-MOCK-003`: Test data includes valid account (sortcode=123456, accountNumber=98765432) for happy-path tests
4. `AC-MOCK-004`: Test data includes account not found scenario (sortcode=999999, accountNumber=00000000 returns empty)
5. `AC-MOCK-005`: Test data includes edge-case accounts: zero balance, future opening date, inactive status, various account types
6. `AC-MOCK-006`: `findBySortcodeAndNumber()` executes case-sensitive string matching on sortcode and accountNumber
7. `AC-MOCK-007`: Returns `Optional.empty()` when no match found (never throws exception)
8. `AC-MOCK-008`: Mock repository is activated via Spring profile `dev` or `test` (conditional `@ConditionalOnProperty`)
9. `AC-MOCK-009`: Mock data is externalizable (CSV or JSON file in classpath, not hardcoded if possible)
10. `AC-MOCK-010`: Unit tests verify lookup success and not-found scenarios (TASK-016)

**Definition of Done:**
- InMemoryAccountRepository committed to version control
- Mock test data (CSV/JSON or initialization code) included in source
- Spring profile integration verified (dev/test profiles load mock repository)
- Unit and integration tests execute successfully against mock data
- No external database required to run application

---

### TASK-006: Implement Structured JSON Logging with Correlation ID

**Task ID:** `TASK-006`  
**Category:** Observability  
**Phase:** 1  
**Week:** 3  
**Workstream:** Observability  
**Estimate:** M (Medium