# Code Review Checklist – INQACC Modernized Account Inquiry

**Document ID:** `code-review-checklist.md`  
**Pipeline:** mainframe_modernization  
**Authority:** system-intent.md + intended-system.md + business-rules.md + requirements.md + spec.md + program-analysis.md + mapping-matrix.md + plan.md + tasks.md + test-spec.md + traceability-matrix.md + openapi.yaml + copilot-build-prompt.md  
**Status:** Implementation-ready code review framework  
**Generated:** 2024  
**Target Stack:** Java 21 + Spring Boot 3.3.x (backend) | React 18.x + TypeScript 5.x + Vite 5.x (frontend) | Mock Repository (POC)

---

## 1. Code Review Scope and Objectives

### 1.1 Review Authority

All code review activities shall measure conformance to:
- **System Intent Blueprint** (`provided/system-intent.md`, `system-intent.md`)
- **Target Architecture** (`intended-system.md`)
- **Business Rules** (`business-rules.md`) – rule-to-code mapping
- **Requirements** (`requirements.md`) – requirement-to-code mapping
- **Specification** (`spec.md`) – API contract and field mapping rules
- **Program Analysis** (`program-analysis.md`) – legacy behavior parity and data structure mapping
- **Mapping Matrix** (`mapping-matrix.md`) – component and data mapping
- **Traceability Matrix** (`traceability-matrix.md`) – requirement-to-implementation traceability
- **Test Specification** (`test-spec.md`) – test coverage expectations
- **OpenAPI 3.0.3 Contract** (`openapi.yaml`) – HTTP semantics and error envelope
- **Delivery Plan** (`plan.md`) – phased gates and stage gates
- **Tasks** (`tasks.md`) – acceptance criteria and definition of done
- **Copilot Build Prompt** (`copilot-build-prompt.md`) – implementation pattern guidance

### 1.2 Review Phases

| Phase | When | Reviewer | Primary Focus |
|-------|------|----------|----------------|
| **Pre-Commit** | Before pull request | Developer + IDE/linter | Style, build success, obvious violations |
| **Pull Request** | Before merge to main | Senior dev + architect | Architecture conformance, requirement traceability, legacy parity |
| **Integration** | Before promotion to UAT | QA + architecture | Test coverage, end-to-end flow, non-functional attributes |
| **Release** | Before production deployment | Security + ops + product | Security scanning, performance baseline, operational readiness |

### 1.3 Review Criteria

Code shall not be merged unless:
- **All architectural conformance checks pass** (see §2)
- **All naming and readability standards met** (see §3)
- **All error handling requirements satisfied** (see §4)
- **All test quality gates achieved** (see §5)
- **Legacy behavior parity verified** (see §6)
- **Traceability to requirements confirmed** (see §7)

---

## 2. Architectural Conformance Checklist

### 2.1 Spring Boot Backend Architecture

#### CK-ARCH-001: Thin Controller Pattern

**Rule ID:** `CK-ARCH-001`  
**Category:** Architectural Compliance  
**Requirement(s):** FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, NFR-001  
**Applies To:** `AccountInquiryController`, all `@RestController` classes

**Checklist Items:**

- [ ] **CK-ARCH-001-A:** Controller methods delegate all business logic to service layer; no domain logic in controller
- [ ] **CK-ARCH-001-B:** Controller methods contain only: `@RequestMapping` binding, parameter extraction, service invocation, response mapping
- [ ] **CK-ARCH-001-C:** All input validation delegated to service layer or `@Validated` + custom validators; no validation in controller body
- [ ] **CK-ARCH-001-D:** All error handling delegated to global `@ExceptionHandler` or `@RestControllerAdvice`; no try-catch logic in controller methods
- [ ] **CK-ARCH-001-E:** Controller method signatures contain no checked exceptions (throws clause); throws declared only on service interfaces
- [ ] **CK-ARCH-001-F:** Response status codes set via `@ResponseStatus` annotation or `ResponseEntity.status()`; never hardcoded in method body
- [ ] **CK-ARCH-001-G:** Content negotiation (JSON vs. XML) handled by Spring Web MVC defaults or explicit `@RequestMapping(produces=...)`
- [ ] **CK-ARCH-001-H:** No direct repository access from controller; all persistence operations via service or DAO layer

**Implementation Guidance:**

```java
// ✓ CORRECT: Thin controller delegating to service
@RestController
@RequestMapping("/v1/accounts")
public class AccountInquiryController {
    private final AccountInquiryService inquiryService;
    
    @GetMapping("/{sortcode}/{accountNumber}")
    public ResponseEntity<AccountResponseDto> getAccount(
        @PathVariable String sortcode,
        @PathVariable String accountNumber,
        @RequestHeader(name = "X-Correlation-ID", required = false) String correlationId
    ) {
        AccountResponseDto response = inquiryService.inquireAccount(
            sortcode, accountNumber, correlationId
        );
        return ResponseEntity.ok(response);
    }
}

// ✗ INCORRECT: Business logic in controller
@RestController
public class BadAccountController {
    @Autowired private AccountRepository repo;
    
    @GetMapping("/account/{id}")
    public AccountResponseDto getBadAccount(@PathVariable String id) {
        if (id.length() != 6) {  // ✗ Validation in controller
            throw new IllegalArgumentException("Invalid ID");
        }
        Account account = repo.findById(id).orElseThrow();  // ✗ Direct repo access
        return new AccountResponseDto(account);  // ✗ Mapping in controller
    }
}
```

**Verification Method:** Code review + static analysis (PMD, SonarQube rules `S1186`, `S2160`)  
**Failure Impact:** Major – Violates separation of concerns; prevents reuse and testability

---

#### CK-ARCH-002: Service Layer Business Logic Isolation

**Rule ID:** `CK-ARCH-002`  
**Category:** Architectural Compliance  
**Requirement(s):** BR-001, BR-002, BR-003, FR-001, FR-002, FR-003  
**Applies To:** `AccountInquiryService`, all `@Service` classes

**Checklist Items:**

- [ ] **CK-ARCH-002-A:** All business rule logic encapsulated in service methods; no rule processing in DAO or controller
- [ ] **CK-ARCH-002-B:** Service layer methods have single, well-defined responsibility (SRP); separation of validation, lookup, error translation
- [ ] **CK-ARCH-002-C:** Service methods depend on repository interfaces (abstraction), not concrete implementations
- [ ] **CK-ARCH-002-D:** Service methods return domain objects or DTOs; no HTTP status codes or response entities in service layer
- [ ] **CK-ARCH-002-E:** All BR-001 through BR-010 business rules have explicit method or code block with docstring reference
- [ ] **CK-ARCH-002-F:** Correlation ID propagated as method parameter or ThreadLocal; never extracted from static context
- [ ] **CK-ARCH-002-G:** Service layer does not directly instantiate or manage HTTP clients; uses injected adapters
- [ ] **CK-ARCH-002-H:** Service methods declare checked exceptions only for business contract (e.g., `AccountNotFoundException`); wrap platform exceptions

**Implementation Guidance:**

```java
// ✓ CORRECT: Service layer isolates business logic
@Service
public class AccountInquiryService {
    private final AccountRepository repository;
    private final ValidationService validator;
    private final CorrelationIdProvider correlationIdProvider;
    
    public AccountResponseDto inquireAccount(
        String sortcode, String accountNumber, String providedCorrelationId
    ) throws AccountNotFoundException, ValidationException {
        // Rule: BR-001, BR-002, BR-003 – Validate inputs and execute lookup
        String correlationId = correlationIdProvider.resolve(providedCorrelationId);
        
        // BR-002: Validate sortcode format
        validator.validateSortcodeFormat(sortcode);
        
        // BR-003: Validate account number format
        validator.validateAccountNumberFormat(accountNumber);
        
        // BR-001: Execute composite-key lookup
        Account account = repository.findBySortcodeAndNumber(sortcode, accountNumber)
            .orElseThrow(() -> new AccountNotFoundException(
                String.format("No account found for %s/%s", sortcode, accountNumber),
                correlationId
            ));
        
        // Transform to DTO
        return AccountResponseMapper.toDto(account, correlationId);
    }
}

// ✗ INCORRECT: Mixed concerns in service
@Service
public class BadAccountService {
    @Autowired private AccountRepository repo;
    
    public ResponseEntity<?> badInquire(String id) {  // ✗ Returns HTTP response
        if (!id.matches("\\d{6}")) {  // ✗ Validation scattered
            return ResponseEntity.badRequest().body("Bad ID");
        }
        Account account = repo.findById(id).orElseThrow();
        // ✗ HTTP concern in service layer
        return ResponseEntity.ok(account);
    }
}
```

**Verification Method:** Code review + unit test coverage inspection  
**Failure Impact:** Major – Prevents reuse, complicates testing, violates layering

---

#### CK-ARCH-003: Exception Translation and Error Envelope Standardization

**Rule ID:** `CK-ARCH-003`  
**Category:** Architectural Compliance  
**Requirement(s):** FR-004, FR-005, FR-006, FR-007, FR-009, NFR-004  
**Applies To:** Global `@ExceptionHandler`, `@RestControllerAdvice`, custom exception classes

**Checklist Items:**

- [ ] **CK-ARCH-003-A:** Global `@RestControllerAdvice` or `@ExceptionHandler` translates all platform exceptions to business exceptions with HTTP status
- [ ] **CK-ARCH-003-B:** All custom exception classes (e.g., `ValidationException`, `AccountNotFoundException`) extend application base exception hierarchy; not generic `RuntimeException`
- [ ] **CK-ARCH-003-C:** Error envelope conforms to OpenAPI spec (spec.md §3.2): `{ "error": { "code": "ERR-NNN", "message": "...", "correlationId": "..." } }`
- [ ] **CK-ARCH-003-D:** Each error path (validation failure, not found, auth failure, server error) returns correct HTTP status code per FR-004 through FR-009
- [ ] **CK-ARCH-003-E:** Correlation ID included in all error responses (header `X-Correlation-ID` + JSON body)
- [ ] **CK-ARCH-003-F:** No sensitive information (stack traces, SQL, internal service details) leaked in error messages for client-facing responses
- [ ] **CK-ARCH-003-G:** Logging includes full exception context with correlation ID; error response to client is sanitized
- [ ] **CK-ARCH-003-H:** Custom exception constructors include correlationId as parameter; never null

**Implementation Guidance:**

```java
// ✓ CORRECT: Standardized exception translation
@RestControllerAdvice
public class AccountInquiryControllerAdvice {
    private static final Logger log = LoggerFactory.getLogger(AccountInquiryControllerAdvice.class);
    
    @ExceptionHandler(ValidationException.class)
    public ResponseEntity<ErrorEnvelope> handleValidation(
        ValidationException ex, HttpServletRequest req
    ) {
        String correlationId = ex.getCorrelationId();
        log.warn("Validation error: {}", ex.getMessage(), ex);  // Full context in log
        
        ErrorEnvelope envelope = ErrorEnvelope.builder()
            .code(ex.getErrorCode())  // e.g., "ERR-001"
            .message(ex.getMessage())
            .correlationId(correlationId)
            .build();
        
        return ResponseEntity
            .status(HttpStatus.BAD_REQUEST)
            .header("X-Correlation-ID", correlationId)
            .body(envelope);
    }
    
    @ExceptionHandler(AccountNotFoundException.class)
    public ResponseEntity<ErrorEnvelope> handleNotFound(
        AccountNotFoundException ex
    ) {
        log.info("Account not found: correlationId={}", ex.getCorrelationId());
        
        ErrorEnvelope envelope = ErrorEnvelope.builder()
            .code("ERR-005")
            .message("Account not found")  // Generic message
            .correlationId(ex.getCorrelationId())
            .build();
        
        return ResponseEntity
            .status(HttpStatus.NOT_FOUND)
            .header("X-Correlation-ID", ex.getCorrelationId())
            .body(envelope);
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorEnvelope> handleGenericException(
        Exception ex, HttpServletRequest req
    ) {
        String correlationId = (String) req.getAttribute("X-Correlation-ID");
        log.error("Unexpected error: correlationId={}", correlationId, ex);  // Full trace in log
        
        ErrorEnvelope envelope = ErrorEnvelope.builder()
            .code("ERR-500")
            .message("An unexpected error occurred. Please contact support with correlation ID.")
            .correlationId(correlationId)
            .build();
        
        return ResponseEntity
            .status(HttpStatus.INTERNAL_SERVER_ERROR)
            .header("X-Correlation-ID", correlationId)
            .body(envelope);
    }
}

// ✗ INCORRECT: Leaking sensitive info, inconsistent envelope
@ExceptionHandler(Exception.class)
public ResponseEntity<?> badErrorHandler(Exception ex) {
    // ✗ Stack trace exposed to client
    return ResponseEntity.status(500).body(ex.toString());
}
```

**Verification Method:** Integration tests + OpenAPI validation  
**Failure Impact:** Critical – Violates security baseline, breaks client contracts

---

#### CK-ARCH-004: Repository and Data Access Layer Pattern

**Rule ID:** `CK-ARCH-004`  
**Category:** Architectural Compliance  
**Requirement(s):** BR-001, FR-001, NFR-002  
**Applies To:** `AccountRepository`, all `@Repository` classes

**Checklist Items:**

- [ ] **CK-ARCH-004-A:** Repository extends `JpaRepository<T, ID>` or equivalent Spring Data interface; not raw `JdbcTemplate`
- [ ] **CK-ARCH-004-B:** Repository method signature mirrors business rule inputs/outputs (e.g., `findBySortcodeAndNumber(String, String)` for BR-001)
- [ ] **CK-ARCH-004-C:** Repository queries use Spring Data derived queries or `@Query` with named parameters; no string concatenation or SQL injection vectors
- [ ] **CK-ARCH-004-D:** Repository returns `Optional<T>` for single-record lookups; never null or unchecked casts
- [ ] **CK-ARCH-004-E:** No business logic in repository methods; queries only
- [ ] **CK-ARCH-004-F:** Entity class annotations (`@Entity`, `@Table`, `@Column`) correctly map to database schema from program-analysis.md
- [ ] **CK-ARCH-004-G:** Entity relationships (if any) use `@ManyToOne`, `@OneToMany` with explicit `fetch=LAZY`; no N+1 query issues
- [ ] **CK-ARCH-004-H:** Repository is injected as interface, not concrete implementation

**Implementation Guidance:**

```java
// ✓ CORRECT: Spring Data repository with named query
public interface AccountRepository extends JpaRepository<Account, String> {
    Optional<Account> findBySortcodeAndNumber(
        @Param("sortcode") String sortcode,
        @Param("accountNumber") String accountNumber
    );
}

//