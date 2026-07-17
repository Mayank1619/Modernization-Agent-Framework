```markdown
# Mapping Matrix for INQACC Modernization

**Document ID:** `mapping-matrix.md`  
**Pipeline:** mainframe_modernization  
**Authority:** system-intent.md + intended-system.md + business-rules.md + requirements.md + spec.md + program-analysis.md + plan.md + tasks.md  
**Status:** Implementation-ready traceability matrix  
**Generated:** 2024  
**Stack:** Java 21 + Spring Boot 3.3.x (backend) | React 18.x + TypeScript 5.x + Vite 5.x (frontend) | Mock Repository (POC)

---

## 1. Legacy Artifact to Modern Component Mapping

### 1.1 COBOL Program Artifacts → Spring Boot Services

| Legacy Artifact | Type | Location | Modern Component | Spring Component | Responsibility |
|---|---|---|---|---|---|
| **INQACC.cbl** | CICS-DB2 Online Program | `cobol/INQACC.cbl` | Account Inquiry Service | `com.inqacc.service.AccountInquiryService` | Execute account lookup by composite key; coordinate repository access; error handling and correlation ID propagation |
| **INQACC Transaction Entry** | CICS Transaction Handler | INQACC.cbl (entry point) | REST Controller | `com.inqacc.controller.AccountInquiryController` | HTTP GET `/v1/accounts/{sortcode}/{accountNumber}` endpoint; request/response mapping; OAuth2 authentication/authorization check |
| **SQLCA (Embedded)** | SQL Communication Area | INQACC.cbl | SQLExceptionHandler | `com.inqacc.exception.AccountRepositoryExceptionHandler` | Map DB2 SQLCODE to HTTP 4xx/5xx status codes; correlation ID propagation; standardized error envelope |
| **Host Variable Structure (HOST-ACCOUNT-ROW)** | COBOL Data Structure | INQACC.cbl, lines 34–45 | DTO / Entity Class | `com.inqacc.dto.AccountResponseDto` + `com.inqacc.entity.AccountEntity` | Carry account record fields across service, DAO, and HTTP response layers |
| **ACC-CURSOR Declaration** | DB2 Cursor | INQACC.cbl | Repository SELECT Query | `com.inqacc.repository.AccountRepository.findBySortcodeAndNumber()` | Execute parameterized SQL SELECT with WHERE clause: `ACCOUNT_SORTCODE = ? AND ACCOUNT_NUMBER = ?` |
| **Program Error Path** | Abend Handling | INQACC.cbl (legacy: abends on error) | Exception Translation | `com.inqacc.exception.*Exception` classes + Global `@ExceptionHandler` | Translate legacy abend semantics to HTTP 4xx/5xx responses; return structured JSON error envelope with correlation ID |
| **Terminal I/O Interface** | CICS Formatted Output | INQACC.cbl (screen definition not provided) | REST JSON Response | `com.inqacc.dto.AccountResponseDto` | Render account record as JSON with standardized field names; include HTTP status code and correlation ID |

### 1.2 Copybook Structures → Java Data Classes

| Copybook | Records/Fields | Modern Mapping | Java Class | Location | Field Count | Validation Rules |
|---|---|---|---|---|---|---|
| **ACCDB2.cpy** | ACCOUNT table declaration (12 columns) | DB2 schema reference | `com.inqacc.entity.AccountEntity` | `src/main/java/com/inqacc/entity/` | 12 | ACCOUNT_SORTCODE NOT NULL (CHAR 6); ACCOUNT_NUMBER NOT NULL (CHAR 8); remaining 10 fields optional/nullable |
| **ACCOUNT.cpy** | ACCOUNT-DATA structure (11 fields, 1 redefine group) | COBOL working storage structure | `com.inqacc.dto.AccountResponseDto` | `src/main/java/com/inqacc/dto/` | 11 | Mirrors ACCDB2 12-column schema; field ordering preserved for legacy parity |
| **INQACCCZ.cpy** | CICS COMMAREA (13 fields + OCCURS 1–20) | Legacy communication interface | `com.inqacc.dto.AccountInquiryRequest` (input) + `com.inqacc.dto.AccountInquiryResponse` (output) | `src/main/java/com/inqacc/dto/` | Input: 2; Output: 13 | Input: CUSTOMER-NUMBER (10 digits), COMM-SCODE (6 digits), COMM-ACCNO (8 digits). Output: single account record (legacy limited to 1 in modern context) |

---

## 2. Field-Level Data Mapping (COBOL → Java → JSON)

### 2.1 ACCOUNT Table Field Mapping

| COBOL Name (ACCOUNT.cpy) | DB2 Name (ACCDB2.cpy) | Data Type | COBOL Picture | DB2 Type | Java Type | JSON Field Name | Validation | Nullable |
|---|---|---|---|---|---|---|---|---|
| ACCOUNT-EYE-CATCHER | ACCOUNT_EYECATCHER | Character | X(4) | CHAR(4) | String | `eyecatcher` | Must equal 'ACCT' | No |
| ACCOUNT-CUST-NO | ACCOUNT_CUSTOMER_NUMBER | Numeric | 9(10) | CHAR(10) | String | `customerNumber` | 10-digit numeric; left-padded with zeros | Yes |
| ACCOUNT-SORT-CODE | ACCOUNT_SORTCODE | Numeric | 9(6) | CHAR(6) NOT NULL | String | `sortcode` | Exactly 6 digits; no validation char; composite key part 1 | No |
| ACCOUNT-NUMBER | ACCOUNT_NUMBER | Numeric | 9(8) | CHAR(8) NOT NULL | String | `accountNumber` | Exactly 8 digits; no validation char; composite key part 2 | No |
| ACCOUNT-TYPE | ACCOUNT_TYPE | Character | X(8) | CHAR(8) | String | `accountType` | 8-char account classification (e.g., 'CHECKING', 'SAVINGS ') | Yes |
| ACCOUNT-INTEREST-RATE | ACCOUNT_INTEREST_RATE | Numeric Packed | 9(4)V99 | DECIMAL(4,2) | BigDecimal | `interestRate` | 2 decimal places; range 0.00–99.99 | Yes |
| ACCOUNT-OPENED | ACCOUNT_OPENED | Date | 9(8) | DATE | LocalDate | `openedDate` | YYYYMMDD format; must be ≤ today | Yes |
| ACCOUNT-OPENED-DAY / MONTH / YEAR | (redefine) | Date components | 99, 99, 9999 | (N/A) | (component parse) | (not exposed in JSON; parsed to ISO 8601) | Extracted and validated | Yes |
| ACCOUNT-OVERDRAFT-LIMIT | ACCOUNT_OVERDRAFT_LIMIT | Numeric | 9(8) | INTEGER | Long | `overdraftLimit` | Positive integer; currency in pence (GBP implied) | Yes |
| ACCOUNT-LAST-STMT-DATE | ACCOUNT_LAST_STATEMENT | Date | 9(8) | DATE | LocalDate | `lastStatementDate` | YYYYMMDD format; must be ≤ today | Yes |
| ACCOUNT-LAST-STMT-DAY / MONTH / YEAR | (redefine) | Date components | 99, 99, 9999 | (N/A) | (component parse) | (not exposed in JSON; parsed to ISO 8601) | Extracted and validated | Yes |
| ACCOUNT-NEXT-STMT-DATE | ACCOUNT_NEXT_STATEMENT | Date | 9(8) | DATE | LocalDate | `nextStatementDate` | YYYYMMDD format; must be ≥ today | Yes |
| ACCOUNT-NEXT-STMT-DAY / MONTH / YEAR | (redefine) | Date components | 99, 99, 9999 | (N/A) | (component parse) | (not exposed in JSON; parsed to ISO 8601) | Extracted and validated | Yes |
| ACCOUNT-AVAILABLE-BALANCE | ACCOUNT_AVAILABLE_BALANCE | Numeric Packed | S9(10)V99 | DECIMAL(10,2) | BigDecimal | `availableBalance` | 2 decimal places; signed; currency in pence (GBP) | Yes |
| ACCOUNT-ACTUAL-BALANCE | ACCOUNT_ACTUAL_BALANCE | Numeric Packed | S9(10)V99 | DECIMAL(10,2) | BigDecimal | `actualBalance` | 2 decimal places; signed; currency in pence (GBP) | Yes |

**Notes:**
- **Composite Key:** ACCOUNT-SORT-CODE + ACCOUNT-NUMBER form unique identifier; required in HTTP path parameters
- **Date Transformation:** YYYYMMDD (COBOL) → LocalDate (Java) → ISO 8601 string (JSON response); e.g., 20240115 → 2024-01-15
- **Numeric Transformation:** COBOL COMP-3 (packed decimal) → Java BigDecimal → JSON number; e.g., PIC S9(10)V99 with value 123456.78 → 123456.78 (JSON)
- **Character Padding:** COBOL PIC X(8) fields right-padded with spaces; Java trim before JSON serialization; e.g., 'CHECKING ' → 'CHECKING'
- **Nullable Fields:** All fields except sortcode, account number, and eyecatcher may be NULL in DB2; JSON response omits null fields (or explicit null, per OpenAPI spec)

---

## 3. Requirement to Implementation Component Mapping

### 3.1 Functional Requirements → Spring Boot Components

| Requirement ID | Requirement Statement | Business Rule(s) | Spring Component(s) | Test Case ID(s) |
|---|---|---|---|---|
| **FR-001** | Execute account lookup by composite key (ACCOUNT_SORTCODE + ACCOUNT_NUMBER) | BR-001 | `AccountInquiryService.findAccountBySortcodeAndNumber()`, `AccountRepository.findBySortcodeAndNumber()`, `AccountInquiryController.getAccountBySortcodeAndNumber()` | TC-001, TC-002, TC-003, TC-004 |
| **FR-002** | Validate sortcode format (6 numeric digits) | BR-002 | `AccountInquiryService.validateSortcode()` (or Spring Bean Validation `@Pattern`), `SortcodeValidator` | TC-005, TC-006 |
| **FR-003** | Validate account number format (8 numeric digits) | BR-003 | `AccountInquiryService.validateAccountNumber()` (or Spring Bean Validation `@Pattern`), `AccountNumberValidator` | TC-007, TC-008 |
| **FR-004** | Return HTTP 400 Bad Request for invalid sortcode or account number | BR-002, BR-003, BR-008 | `@ExceptionHandler` for `ValidationException`, `HttpMessageNotReadableException` handler | TC-009, TC-010, TC-011 |
| **FR-005** | Return HTTP 404 Not Found when no matching account exists | BR-001, BR-009 | `AccountInquiryService` (return empty Optional), `@ExceptionHandler` for `AccountNotFoundException` | TC-012, TC-013 |
| **FR-006** | Return HTTP 401 Unauthorized if OAuth2 token missing or invalid | BR-010 | Spring Security `@EnableResourceServer`, `OAuth2ResourceServerConfigurer`, `BearerTokenAuthenticationFilter` | TC-014, TC-015, TC-016 |
| **FR-007** | Return HTTP 403 Forbidden if user lacks ACCOUNT_INQUIRER role | BR-011 | Spring Security `@PreAuthorize("hasRole('ACCOUNT_INQUIRER')")`, `RoleBasedAuthorizationFilter` | TC-017, TC-018 |
| **FR-008** | Return standardized JSON error envelope with correlation ID and HTTP status | BR-012 | `ErrorEnvelopeDto`, `@ExceptionHandler` methods (global), `CorrelationIdInterceptor` | TC-019, TC-020, TC-021 |
| **FR-009** | Propagate correlation ID through all request/response boundaries | BR-013 | `CorrelationIdInterceptor`, `CorrelationIdService`, HTTP response header `X-Correlation-ID` | TC-022, TC-023, TC-024 |
| **FR-010** | Return successful account record as JSON (200 OK) with all 12 fields mapped | BR-001, BR-010 | `AccountResponseDto`, `AccountToResponseDtoMapper`, Jackson serialization | TC-025, TC-026, TC-027 |

### 3.2 Non-Functional Requirements → Architecture & Infrastructure Components

| Requirement ID | Requirement Statement | Business Rule(s) | Component(s) | Test Coverage |
|---|---|---|---|---|
| **NFR-001** | OAuth2 bearer token authentication at API boundary | BR-010 | Spring Security OAuth2 Resource Server; `JwtDecoder` bean | Token validation tests (TC-014–TC-018) |
| **NFR-002** | Role-based access control (ACCOUNT_INQUIRER role) | BR-011 | Spring Security `@PreAuthorize`, RoleBasedAuthorizationFilter | Authorization tests (TC-017–TC-018) |
| **NFR-003** | TLS 1.2+ transport encryption | System Intent | Spring Boot Tomcat SSL configuration (application.yml); reverse proxy SSL termination (production) | Infrastructure validation (ops checklist) |
| **NFR-004** | Structured JSON logging with correlation ID per request | BR-013 | SLF4J + Logback; custom `LogstashEncoder` (or similar JSON layout); `CorrelationIdLoggingFilter` | Logging tests (TC-028–TC-030) |
| **NFR-005** | Request latency metrics and error rate observability | System Intent | Micrometer + Spring Boot Actuator; custom `Timer` beans for endpoint latency | Metrics baseline tests (non-functional test plan) |
| **NFR-006** | Distributed tracing readiness (OpenTelemetry compatible) | System Intent | Spring Cloud Sleuth (or Spring Boot 3.3+ native tracing); `Tracer` bean; `X-Trace-ID` propagation | Tracing readiness review (ops checklist) |
| **NFR-007** | Stateless REST API (no server-side session state) | System Intent | Stateless `@RestController` with request-scoped beans; no `HttpSession` usage | Architectural compliance review (code review) |
| **NFR-008** | Mock repository for POC (no live DB2/CICS connectivity) | System Intent | `AccountRepository` backed by `HashMap<String, AccountEntity>` or H2 in-memory database | Mock repository tests (TC-031–TC-040) |

---

## 4. Business Rule to Test Traceability

### 4.1 Rule-to-Test Coverage Matrix

| Business Rule ID | Rule Statement | Trigger Condition | Test Case(s) | Test Type | Expected Outcome |
|---|---|---|---|---|---|
| **BR-001** | Account record lookup by composite key | Valid sortcode (6 digits) + valid account number (8 digits) + authenticated user with ACCOUNT_INQUIRER role | TC-001 (Happy path: account found), TC-002 (Account found with all 12 fields populated), TC-003 (Multiple accounts: ensure exact key match, not partial), TC-004 (Boundary: max 6-digit sortcode + max 8-digit account number) | Unit, Integration, E2E | SELECT returned exactly 1 record; HTTP 200 OK; JSON contains all 12 fields |
| **BR-002** | Sortcode format validation (6 numeric digits) | User submits sortcode in HTTP GET path parameter | TC-005 (Valid: '123456'), TC-006 (Invalid: '12345' / '1234567' / 'ABCDEF' / '12345 ' / empty string / null) | Unit, Integration | Valid: accepted; Invalid: HTTP 400 Bad Request with validation error detail |
| **BR-003** | Account number format validation (8 numeric digits) | User submits account number in HTTP GET path parameter | TC-007 (Valid: '12345678'), TC-008 (Invalid: '1234567' / '123456789' / 'ABCDEFGH' / '1234567 ' / empty string / null) | Unit, Integration | Valid: accepted; Invalid: HTTP 400 Bad Request with validation error detail |
| **BR-004** | The system must handle errors gracefully and provide standardized error responses. | Any error condition during account inquiry | TC-002 | Unit, Integration | HTTP 4xx/5xx status with structured error response |
| **BR-005** | The system must log all account inquiry requests and responses for auditing purposes. | Any account inquiry request | TC-003 | Unit, Integration | Log entry created with correlation ID |
| **BR-006** | The system must enforce role-based access control for account inquiry endpoints. | User without ACCOUNT_INQUIRER role attempts access | TC-017 | Unit, Integration | HTTP 403 Forbidden response |
| **BR-007** | The system must return standardized JSON error envelope with correlation ID and HTTP status. | Any error condition | TC-019 | Unit, Integration | JSON error envelope returned with correlation ID |
| **BR-008** | The system must propagate correlation ID through all request/response boundaries. | Any account inquiry request | TC-022 | Unit, Integration | Correlation ID present in response headers |
| **BR-009** | The system must return HTTP 404 Not Found when no matching account exists. | Valid sortcode and account number that do not exist | TC-012 | Unit, Integration | HTTP 404 Not Found response |
| **BR-010** | The system must return HTTP 401 Unauthorized if OAuth2 token missing or invalid. | Missing or invalid OAuth2 token | TC-014 | Unit, Integration | HTTP 401 Unauthorized response |
```