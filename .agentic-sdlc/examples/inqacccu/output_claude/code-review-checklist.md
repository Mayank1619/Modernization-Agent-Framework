# code-review-checklist.md

**Document ID:** `code-review-checklist-inqacccu-001`  
**Pipeline:** `mainframe_modernization`  
**Target System:** INQACCCU Customer Account Inquiry REST API  
**Generated:** 2025  
**Status:** Implementation-Ready  
**Scope:** Spring Boot 3.3.x Backend & React 18.x Frontend  

---

## 1. Architectural Conformance

### 1.1 Backend Architecture (Spring Boot 3.3.x, Java 21)

| Check ID | Control | Expected Outcome | Severity | Status |
|----------|---------|------------------|----------|--------|
| ARCH-B-001 | **Layered Architecture Adherence** – Controllers, Services, Repositories properly separated | Controllers remain thin (request/response only); business logic in service layer; persistence abstraction via repository interface | CRITICAL | ⚠️ REVIEW |
| ARCH-B-002 | **Spring Boot Dependency Injection** – All beans explicitly declared or auto-wired per Spring conventions | No hardcoded `new` keyword instantiation outside factories; all external dependencies injected via `@Autowired` or constructor injection | CRITICAL | ⚠️ REVIEW |
| ARCH-B-003 | **REST Endpoint Mapping** – Endpoint paths conform to OpenAPI 3.0.3 contract | `GET /api/v1/customers/{customerId}/accounts` returns `CustomerAccountsResponse` JSON; HTTP status codes (200, 400, 401, 403, 500) match spec | CRITICAL | ⚠️ REVIEW |
| ARCH-B-004 | **OAuth2 Resource Server Integration** – JWT bearer token validation on all protected endpoints | All endpoints decorated with `@PreAuthorize` or equivalent Spring Security filter; token claims extracted and validated before business logic execution | CRITICAL | ⚠️ REVIEW |
| ARCH-B-005 | **Role-Based Access Control (RBAC)** – Authorization enforced per endpoint specification | `@PreAuthorize("hasRole('CUSTOMER_INQUIRY')")` or equivalent; access denied responses (403) logged with correlation ID | HIGH | ⚠️ REVIEW |
| ARCH-B-006 | **Mock Repository Layer (POC)** – No live DB2 or CICS connectivity; in-memory data structures only | Repository implementation returns hardcoded or seeded mock data; no `@EnableCaching` connecting to external systems; clear documentation of mock nature | CRITICAL | ⚠️ REVIEW |
| ARCH-B-007 | **Observability Infrastructure** – JSON logging, correlation IDs, OpenTelemetry readiness | All requests tagged with UUID v4 correlation ID; log entries formatted as JSON; Spring Boot Actuator endpoints exposed for metrics; OpenTelemetry SDK imported and configured (even if exporters not active in POC) | CRITICAL | ⚠️ REVIEW |
| ARCH-B-008 | **Exception Handling Strategy** – Centralized error handling with standardized JSON responses | Global `@ControllerAdvice` or `@RestControllerAdvice` handler; all exceptions mapped to `ErrorResponse` DTO; no stack traces in production responses | CRITICAL | ⚠️ REVIEW |
| ARCH-B-009 | **Input Validation Strictness** – Legacy COBOL validation rules preserved | 10-digit customer ID validated as numeric only; no fuzzy matching or padding; 400 Bad Request for invalid input; validation annotations (`@Pattern`, `@NotNull`) on DTOs or controller parameters | CRITICAL | ⚠️ REVIEW |
| ARCH-B-010 | **Feature Toggle Framework** – Any enhancements marked explicitly and toggleable | All new features behind `@ConditionalOnProperty` or equivalent; legacy behavior is default; enhancement flags documented in deployment runbook | HIGH | ⚠️ REVIEW |
| ARCH-B-011 | **Maven POM Configuration** – Dependency versions and build configuration aligned with target stack | Java 21 source/target; Spring Boot 3.3.x BOM imported; Maven 3.9+ compatible; no deprecated dependencies; security advisories checked | HIGH | ⚠️ REVIEW |
| ARCH-B-012 | **Secrets Management** – No hardcoded credentials or connection strings | Database URLs, API keys, JWT signing keys sourced from environment variables or Spring Cloud Vault; `.gitignore` blocks `application-*.properties`, `*.key`, `*.pem` files | CRITICAL | ⚠️ REVIEW |

### 1.2 Frontend Architecture (React 18.x, TypeScript 5.x, Vite 5.x)

| Check ID | Control | Expected Outcome | Severity | Status |
|----------|---------|------------------|----------|--------|
| ARCH-F-001 | **Component-Based Structure** – Functional components with hooks | All components are functional, not class-based; React 18 hooks (`useState`, `useEffect`, `useContext`) used for state and lifecycle management | CRITICAL | ⚠️ REVIEW |
| ARCH-F-002 | **TypeScript Type Safety** – No `any` types without documentation | All props, state, and API responses typed explicitly; `tsconfig.json` includes `"strict": true`; generics used appropriately; `any` only with `// @ts-ignore` comments justified | HIGH | ⚠️ REVIEW |
| ARCH-F-003 | **API Integration Layer** – Abstracted HTTP client for backend communication | Axios or Fetch API wrapped in service layer; all endpoints call backend via typed service methods; authorization header (Bearer JWT) added automatically | CRITICAL | ⚠️ REVIEW |
| ARCH-F-004 | **Authentication & JWT Handling** – OAuth2 token stored securely and included in requests | JWT stored in secure HTTP-only cookie or session storage; token refresh logic implemented; 401 responses trigger re-authentication flow | CRITICAL | ⚠️ REVIEW |
| ARCH-F-005 | **Error Handling & User Feedback** – Errors from backend mapped to user-friendly messages | Error responses parsed; correlation ID displayed in error UI; network errors distinguished from application errors; loading/retry states managed | HIGH | ⚠️ REVIEW |
| ARCH-F-006 | **Vite Build Configuration** – Production build optimized and secure | `vite.config.ts` configured for production minification; environment variables prefixed with `VITE_`; no secrets embedded in frontend code; output files hashed for cache-busting | HIGH | ⚠️ REVIEW |
| ARCH-F-007 | **Form Input Validation** – Client-side validation mirrors backend rules | 10-digit customer ID input validated before submission; numeric-only enforcement; error messages displayed inline; disabled/loading states on buttons during submission | MEDIUM | ⚠️ REVIEW |

---

## 2. Code Quality & Readability

### 2.1 Naming Conventions

| Check ID | Control | Expected Outcome | Severity | Status |
|----------|---------|------------------|----------|--------|
| NAME-001 | **Java Class Naming** – PascalCase for public classes | Example: `CustomerAccountsController`, `CustomerAccountsService`, `AccountDetail`, `ErrorResponse` (not `customer_accounts_controller` or `customerAccountsController`) | HIGH | ⚠️ REVIEW |
| NAME-002 | **Java Method Naming** – camelCase for methods; verb-noun pattern | Example: `inquireAccounts()`, `validateCustomerId()`, `mapToResponse()` (not `InquireAccounts`, `validate_customer_id`) | HIGH | ⚠️ REVIEW |
| NAME-003 | **Java Field Naming** – camelCase; descriptive names aligned with legacy mapping | Example: `customerId`, `numberOfAccounts`, `accountDetails` (not `cid`, `num_accts`, `CUSTOMER_NUMBER`) | MEDIUM | ⚠️ REVIEW |
| NAME-004 | **REST Endpoint Path Naming** – lowercase, hyphen-separated; RESTful verbs** | Example: `/api/v1/customers/{customerId}/accounts` (not `/api/v1/inquireCustomer`, `/getAccounts`, `/customers_accounts`) | HIGH | ⚠️ REVIEW |
| NAME-005 | **JSON Field Naming** – camelCase (not COBOL UPPER-CASE) | Example: `{ "customerId": "...", "numberOfAccounts": ... }` (not `{ "CUSTOMER_NUMBER": ..., "NUMBER_OF_ACCOUNTS": ... }`) | MEDIUM | ⚠️ REVIEW |
| NAME-006 | **React Component Naming** – PascalCase; descriptive noun-based | Example: `CustomerAccountsForm`, `AccountsTable`, `ErrorAlert` (not `customerForm`, `getAccounts`, `app`) | HIGH | ⚠️ REVIEW |
| NAME-007 | **React Hook/Utility Function Naming** – camelCase; prefix with `use` for custom hooks | Example: `useCustomerInquiry()`, `formatAccountNumber()` (not `UseCustomerInquiry`, `use_customer_inquiry`) | HIGH | ⚠️ REVIEW |
| NAME-008 | **Configuration & Constants** – UPPER_SNAKE_CASE | Example: `API_BASE_URL`, `DEFAULT_PAGE_SIZE`, `JWT_EXPIRY_MINUTES` (not `ApiBaseUrl`, `apiBaseUrl`) | MEDIUM | ⚠️ REVIEW |
| NAME-009 | **Test Method Naming** – Clear Given-When-Then pattern | Example: `shouldReturnAccountsWhenCustomerExists()`, `shouldThrowValidationErrorWhenCustomerIdInvalid()` (not `test1()`, `testAccounts`) | HIGH | ⚠️ REVIEW |

### 2.2 Code Readability & Style

| Check ID | Control | Expected Outcome | Severity | Status |
|----------|---------|------------------|----------|--------|
| READ-001 | **Indentation & Formatting** – Consistent whitespace; 2-4 space indents | All files follow consistent indentation; no mixed tabs/spaces; line length ≤ 120 characters (configurable in formatter) | MEDIUM | ⚠️ REVIEW |
| READ-002 | **Method Length** – Methods under 30 lines; single responsibility principle | Complex logic extracted to private helper methods or services; readability improved without sacrificing functionality | HIGH | ⚠️ REVIEW |
| READ-003 | **Comment Quality** – Meaningful comments; no noise | Comments explain *why*, not *what*; outdated comments removed; complex algorithms documented with brief rationale | MEDIUM | ⚠️ REVIEW |
| READ-004 | **Dead Code Removal** – No unused imports, fields, or methods | IDE warnings (`unused variable`, `unused import`) addressed; version control comments removed; debug code cleaned up | MEDIUM | ⚠️ REVIEW |
| READ-005 | **Logging Clarity** – Structured logging with appropriate levels | `INFO` for significant events (successful inquiry); `WARN` for non-critical issues (customer not found); `ERROR` for failures; correlation ID included in all logs | HIGH | ⚠️ REVIEW |

---

## 3. Error Handling & Resilience

### 3.1 Exception Handling Strategy

| Check ID | Control | Expected Outcome | Severity | Status |
|----------|---------|------------------|----------|--------|
| ERROR-001 | **Exception Hierarchy** – Custom exceptions for business logic errors | Example: `CustomerNotFoundException extends RuntimeException`; `InvalidCustomerIdException` for validation errors; specific exception caught and mapped to HTTP status | HIGH | ⚠️ REVIEW |
| ERROR-002 | **Null Pointer Protection** – No unguarded null dereferences | Null checks explicit; Optional<T> used where appropriate; `@NotNull` annotations on method parameters; defensive programming in repository mock | CRITICAL | ⚠️ REVIEW |
| ERROR-003 | **Global Error Handler** – Centralized exception-to-response mapping | `@ControllerAdvice` or `@RestControllerAdvice` with `@ExceptionHandler` methods; all exceptions logged with correlation ID; consistent `ErrorResponse` JSON returned | CRITICAL | ⚠️ REVIEW |
| ERROR-004 | **HTTP Status Code Mapping** – Correct status codes per OpenAPI spec | 200 OK for successful inquiry; 400 Bad Request for invalid customer ID; 401 Unauthorized for missing/invalid JWT; 403 Forbidden for insufficient role; 500 Internal Server Error for server-side faults | CRITICAL | ⚠️ REVIEW |
| ERROR-005 | **Error Response Format** – JSON error structure includes correlation ID | Example: `{ "status": 400, "message": "Invalid customer ID", "correlationId": "uuid", "details": {...} }` (per OpenAPI spec section 6.2) | HIGH | ⚠️ REVIEW |
| ERROR-006 | **Validation Error Details** – Field-level errors exposed safely** | Example: `{ "validationErrors": [{ "field": "customerId", "message": "Must be 10 digits" }] }` (no internal stack traces) | MEDIUM | ⚠️ REVIEW |
| ERROR-007 | **Resource Not Found** – 404 responses for missing resources | If customer inquiry returns no accounts, response is 200 OK with `customerFound: false` (not 404); if endpoint itself missing, 404 returned | HIGH | ⚠️ REVIEW |
| ERROR-008 | **Timeout Handling** – Request timeouts managed gracefully | Repository calls and external API calls have explicit timeouts; timeout exceptions caught and mapped to 500 or 503 response; user notified of timeout | MEDIUM | ⚠️ REVIEW |

### 3.2 Resilience & Observability

| Check ID | Control | Expected Outcome | Severity | Status |
|----------|---------|------------------|----------|--------|
| RESIL-001 | **Correlation ID Propagation** – Request-scoped correlation ID through call stack | UUID v4 generated on entry; included in all log statements, error responses, and (optionally) passed to downstream adapters; matches format in OpenAPI spec | CRITICAL | ⚠️ REVIEW |
| RESIL-002 | **Structured JSON Logging** – All log entries machine-parseable | Log format: `{ "timestamp": "...", "level": "INFO", "correlationId": "...", "message": "...", "context": {...} }`; no unstructured console.log in frontend | HIGH | ⚠️ REVIEW |
| RESIL-003 | **Metrics Instrumentation** – Request latency, error rate, business metrics tracked | Spring Boot Actuator exposes `http.server.requests` histogram; custom metrics for `customer.inquiry.found_rate`, `customer.inquiry.error_rate`; exportable to Prometheus format | HIGH | ⚠️ REVIEW |
| RESIL-004 | **Circuit Breaker Pattern (Optional)** – Graceful degradation for downstream adapter failures | If future production integrations use circuit breakers (e.g., Resilience4j), fallback behavior documented; POC may omit if mock repository only | MEDIUM | ⚠️ REVIEW |

---

## 4. Test Quality & Coverage

### 4.1 Unit Test Standards

| Check ID | Control | Expected Outcome | Severity | Status |
|----------|---------|------------------|----------|--------|
| TEST-U-001 | **Test Framework** – JUnit 5 + Mockito for Java; Jest/Vitest for TypeScript | All tests use current framework versions; no JUnit 4 or deprecated mock libraries; test class names follow `*Test.java` or `*.test.ts` convention | HIGH | ⚠️ REVIEW |
| TEST-U-002 | **Service Layer Tests** – Business logic tested in isolation | `CustomerAccountsService` tests mock repository; all branches (customer found, not found, invalid input) covered; test cases document expected behavior | HIGH | ⚠️ REVIEW |
| TEST-U-003 | **Controller Tests** – Endpoint request/response mapping validated | Spring `MockMvc` or equivalent; request with valid/invalid customer ID tested; response status and JSON structure verified; JWT/authorization skipped in unit test (integration test responsibility) | HIGH | ⚠️ REVIEW |
| TEST-U-004 | **DTO/Entity Mapping Tests** – Legacy-to-modern field transformation verified | COBOL `INQACCCUZ` → Java `CustomerAccountsResponse` mapping tested; null/empty handling verified; date format conversion (COBOL numeric → ISO 8601) confirmed | MEDIUM | ⚠️ REVIEW |
| TEST-U-005 | **Input Validation Tests** – Customer ID validation rules enforced | Tests for: 10-digit numeric only, non-numeric rejected, empty/null rejected, length bounds;