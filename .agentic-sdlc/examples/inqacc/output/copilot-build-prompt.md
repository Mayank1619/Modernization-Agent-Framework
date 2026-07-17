# Copilot Implementation Prompt

**Document ID:** `copilot-build-prompt.md`  
**Pipeline:** mainframe_modernization  
**Authority:** system-intent.md + intended-system.md + business-rules.md + requirements.md + spec.md + program-analysis.md + mapping-matrix.md + plan.md + tasks.md + test-spec.md + traceability-matrix.md + openapi.yaml  
**Status:** Implementation-ready Copilot guidance for iterative development  
**Generated:** 2024  
**Target Stack:** Java 21 + Spring Boot 3.3.x (backend) | React 18.x + TypeScript 5.x + Vite 5.x (frontend) | Mock Repository (POC)

---

## 1. Project Context and Objectives

### 1.1 Modernization Goal

Modernize the legacy INQACC CICS-DB2 account inquiry program into a cloud-ready, REST-based application with:

- **Backend:** Spring Boot 3.3.x REST API (Java 21, Maven 3.9+)
- **Frontend:** React 18.x web UI (TypeScript 5.x, Vite 5.x, Node.js 20 LTS)
- **Persistence:** Mock in-memory repository (POC, no live DB2/CICS)
- **Security:** OAuth2 bearer token authentication, role-based access control (ACCOUNT_INQUIRER role)
- **Observability:** Structured JSON logging with correlation ID propagation, distributed tracing readiness
- **API Contract:** OpenAPI 3.0.3 contract-first design (single source of truth)
- **Backward Compatibility:** Preserve legacy DB2 WHERE clause semantics and field mapping from INQACC.cbl

### 1.2 Critical Success Factors

| Factor | Indicator | Owner |
|--------|-----------|-------|
| **API Contract Stability** | OpenAPI 3.0.3 specification frozen by end of Phase 1 (week 4); no breaking changes without explicit governance | Architecture + API Team |
| **Thin Controllers** | All business logic in service layer; controllers delegate all validation, lookup, and error translation | Backend Dev + Code Review |
| **Comprehensive Testing** | 85%+ line coverage target; unit → integration → E2E test coverage; all 47+ test cases in test-spec.md implemented | QA + Backend Dev |
| **Legacy Parity** | Field mapping and behavior match COBOL/DB2 analysis from program-analysis.md; composite-key semantics preserved | Backend Dev + QA |
| **Iterative Delivery** | Implement smallest vertical slice first; deliver working code in each pull request; no incomplete features merged | Tech Lead + Scrum Master |

---

## 2. Development Environment Setup

### 2.1 Prerequisites

**Backend Development:**

```bash
# Verify Java 21
java -version
# Expected: openjdk version "21.x.x" or Oracle JDK 21.x

# Verify Maven 3.9+
mvn -version
# Expected: Apache Maven 3.9.x

# Verify Git
git --version
# Expected: git version 2.40+
```

**Frontend Development:**

```bash
# Verify Node.js 20 LTS
node -v
# Expected: v20.x.x

# Verify npm 10+
npm -v
# Expected: 10.x.x
```

### 2.2 Project Initialization

**Backend Setup:**

```bash
# Create Spring Boot 3.3.x starter project
cd /workspace/inqacc-backend
mvn archetype:generate \
  -DgroupId=com.inqacc \
  -DartifactId=inqacc-api \
  -DarchetypeArtifactId=maven-archetype-quickstart \
  -DinteractiveMode=false

# Add Spring Boot parent POM (replace generated pom.xml parent section)
# Target: Spring Boot 3.3.x with Spring Security OAuth2 Resource Server, Spring Data JPA, Springdoc OpenAPI
```

**Frontend Setup:**

```bash
# Create Vite + React + TypeScript project
npm create vite@latest inqacc-ui -- --template react-ts
cd inqacc-ui
npm install
```

### 2.3 Key Dependencies

**Backend (`pom.xml`):**

```xml
<properties>
  <maven.compiler.source>21</maven.compiler.source>
  <maven.compiler.target>21</maven.compiler.target>
  <spring-boot.version>3.3.x</spring-boot.version>
  <java.version>21</java.version>
</properties>

<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-dependencies</artifactId>
      <version>${spring-boot.version}</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>

<dependencies>
  <!-- Spring Web MVC -->
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
  </dependency>

  <!-- Spring Security OAuth2 Resource Server -->
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
  </dependency>

  <!-- Spring Data JPA -->
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
  </dependency>

  <!-- H2 Database (Mock Persistence) -->
  <dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>runtime</scope>
  </dependency>

  <!-- Springdoc OpenAPI (Swagger UI + auto-generation) -->
  <dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.x.x</version>
  </dependency>

  <!-- Logging: Structured JSON logs -->
  <dependency>
    <groupId>net.logstash.logback</groupId>
    <artifactId>logstash-logback-encoder</artifactId>
    <version>7.x</version>
  </dependency>

  <!-- JUnit 5 + Mockito -->
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
  </dependency>

  <!-- REST Assured for Integration Tests -->
  <dependency>
    <groupId>io.rest-assured</groupId>
    <artifactId>rest-assured</artifactId>
    <version>5.x</version>
    <scope>test</scope>
  </dependency>
</dependencies>
```

**Frontend (`package.json`):**

```json
{
  "name": "inqacc-ui",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives"
  },
  "dependencies": {
    "react": "^18.x.x",
    "react-dom": "^18.x.x",
    "react-router-dom": "^6.x.x",
    "axios": "^1.x.x"
  },
  "devDependencies": {
    "@types/react": "^18.x.x",
    "@types/react-dom": "^18.x.x",
    "@typescript-eslint/eslint-plugin": "^6.x.x",
    "@typescript-eslint/parser": "^6.x.x",
    "@vitejs/plugin-react": "^4.x.x",
    "eslint": "^8.x.x",
    "typescript": "^5.x.x",
    "vite": "^5.x.x",
    "vitest": "^0.x.x",
    "@testing-library/react": "^14.x.x",
    "@testing-library/jest-dom": "^6.x.x"
  }
}
```

---

## 3. Architecture and Implementation Patterns

### 3.1 Backend Layered Architecture

```
com.inqacc.
├── controller/
│   ├── AccountInquiryController.java          # HTTP GET /v1/accounts/{sortcode}/{accountNumber}
│   └── advice/
│       └── AccountInquiryControllerAdvice.java # @ExceptionHandler → standardized error envelope
├── service/
│   ├── AccountInquiryService.java             # Core business logic: validation, lookup, error translation
│   └── CorrelationIdService.java              # Generate/propagate correlation ID
├── repository/
│   ├── AccountRepository.java                 # Spring Data JPA: findBySortcodeAndNumber()
│   └── AccountRepositoryImpl.java              # Custom implementation if needed
├── entity/
│   ├── Account.java                           # JPA Entity mapping to ACCOUNT table
│   └── AccountMapper.java                     # Entity ↔ DTO transformation
├── dto/
│   ├── AccountRequestDto.java                 # Request binding (path vars)
│   ├── AccountResponseDto.java                # Response DTO (all 12 fields from program-analysis.md)
│   ├── ErrorResponseDto.java                  # Standardized error envelope (spec §3.2)
│   └── ValidationErrorDto.java                # Field-level validation details
├── exception/
│   ├── AccountNotFoundException.java           # No matching record (HTTP 404)
│   ├── InvalidAccountFormatException.java     # Format validation failure (HTTP 400)
│   ├── AccountRepositoryException.java        # Data access layer errors (HTTP 503/500)
│   └── UnauthorizedException.java             # Missing/invalid token (HTTP 401)
├── security/
│   ├── SecurityConfig.java                    # OAuth2 Resource Server configuration
│   ├── JwtConverter.java                      # Extract roles from JWT token
│   └── AuthenticationFilter.java               # Optional custom authentication logic
├── logging/
│   ├── StructuredLogProvider.java             # Centralized structured logging with correlation ID
│   └── RequestLoggingFilter.java               # Log HTTP request/response with correlation ID
├── config/
│   ├── OpenApiConfig.java                     # Springdoc OpenAPI auto-generation configuration
│   └── ApplicationProperties.java              # @ConfigurationProperties for env vars
├── mock/
│   └── MockAccountDataInitializer.java        # Load mock test data on startup (H2)
└── Application.java                            # Spring Boot entry point
```

### 3.2 Controller Implementation Pattern (Thin Controller)

```java
// AccountInquiryController.java
@RestController
@RequestMapping("/v1/accounts")
@RequiredArgsConstructor
@Slf4j
public class AccountInquiryController {

  private final AccountInquiryService accountInquiryService;
  private final CorrelationIdService correlationIdService;

  /**
   * GET /v1/accounts/{sortcode}/{accountNumber}
   * Retrieve account by composite key. Delegates all business logic to service layer.
   * 
   * @param sortcode ACCOUNT_SORTCODE (6 numeric digits)
   * @param accountNumber ACCOUNT_NUMBER (8 numeric digits)
   * @param correlationId optional X-Correlation-ID header (generated if not provided)
   * @return AccountResponseDto with all 12 ACCOUNT fields
   */
  @GetMapping("/{sortcode}/{accountNumber}")
  public ResponseEntity<AccountResponseDto> getAccount(
      @PathVariable @Pattern(regexp = "^\\d{6}$") String sortcode,
      @PathVariable @Pattern(regexp = "^\\d{8}$") String accountNumber,
      @RequestHeader(name = "X-Correlation-ID", required = false) String correlationId) {

    // Generate or use provided correlation ID
    String requestCorrelationId = correlationIdService.getOrGenerateCorrelationId(correlationId);
    
    // Log request
    log.info("Account inquiry request",
        Map.of(
            "correlationId", requestCorrelationId,
            "sortcode", sortcode,
            "accountNumber", accountNumber
        ));

    // Delegate to service layer
    AccountResponseDto response = accountInquiryService.inquireAccount(
        sortcode, accountNumber, requestCorrelationId);

    // Return with correlation ID in response header
    return ResponseEntity.ok()
        .header("X-Correlation-ID", requestCorrelationId)
        .body(response);
  }
}
```

### 3.3 Service Implementation Pattern (Business Logic)

```java
// AccountInquiryService.java
@Service
@RequiredArgsConstructor
@Slf4j
public class AccountInquiryService {

  private final AccountRepository accountRepository;

  /**
   * Execute account inquiry by composite key.
   * Encapsulates all validation, lookup, and error translation logic.
   * 
   * Linked to:
   * - BR-001: Account Record Lookup by Composite Key
   * - BR-002: Sortcode Format Validation
   * - BR-003: Account Number Format Validation
   * - FR-001, FR-002, FR-003, FR-004, FR-005, FR-006
   * 
   * @param sortcode ACCOUNT_SORTCODE (pre-validated by controller)
   * @param accountNumber ACCOUNT_NUMBER (pre-validated by controller)
   * @param correlationId for correlation and tracing
   * @return AccountResponseDto with all populated fields
   * @throws InvalidAccountFormatException if sortcode or accountNumber format invalid (HTTP 400)
   * @throws AccountNotFoundException if no matching record (HTTP 404)
   * @throws AccountRepositoryException if database error (HTTP 503/500)
   */
  public AccountResponseDto inquireAccount(
      String sortcode, String accountNumber, String correlationId) {

    // Step 1: Validate sortcode format (BR-002)
    validateSortcode(sortcode);

    // Step 2: Validate account number format (BR-003)
    validateAccountNumber(accountNumber);

    // Step 3: Execute composite-key lookup (BR-001)
    // Maps to legacy INQACC.cbl SQL: SELECT * FROM ACCOUNT WHERE ACCOUNT_SORTCODE = ? AND ACCOUNT_NUMBER = ?
    Account account = accountRepository.findBySortcodeAndNumber(sortcode, accountNumber)
        .orElseThrow(() -> new AccountNotFoundException(
            String.format("Account not found for sortcode=%s, accountNumber=%s", sortcode, accountNumber),
            correlationId));

    // Step 4: Map entity to response DTO (preserves all 12 fields from program-analysis.md)
    AccountResponseDto response = AccountMapper.toResponseDto(account);
    response.setCorrelationId(correlationId);

    // Step 5: Log successful lookup
    log.info("Account inquiry successful",
        Map.of(
            "correlationId", correlationId,
            "accountId", account.getAccountId(),
            "accountStatus", account.getAccountStatus()
        ));

    return response;
  }

  /**
   * Validate sortcode format (BR-002).
   * Must be exactly 6 numeric digits.
   */
  private void validateSortcode(String sortcode) {
    if (sortcode == null || !sortcode.matches("^\\d{6}$")) {
      throw new InvalidAccountFormatException(
          "Sortcode must be exactly 6 numeric digits",
          "sortcode", sortcode);
    }
  }

  /**
   * Validate account number format (BR-003).
   * Must be exactly 8 numeric digits.
   */
  private void validateAccountNumber(String accountNumber) {
    if (accountNumber == null || !accountNumber.matches("^\\d{8