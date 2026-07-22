# Copilot Implementation Prompt

## Purpose
Generate implementation code for the INQACCCU modernization initiative—transforming a legacy COBOL CICS customer-account inquiry program into a Spring Boot 3.3.x REST API with React 18.x frontend. Use this prompt to drive iterative pull requests aligned with the mainframe modernization pipeline.

---

## Context & Mandatory Constraints

### System Intent (Binding Architecture)
- **Backend Stack:** Java 21, Spring Boot 3.3.x, Maven 3.9+
- **Frontend Stack:** React 18.x, TypeScript 5.x, Vite 5.x, Node.js 20 LTS
- **API Contract:** REST over HTTPS, OpenAPI 3.0.3
- **Authentication:** OAuth2 resource server with JWT bearer tokens
- **Authorization:** Role-based access control (RBAC) for customer-account inquiry endpoints
- **Persistence (POC):** Mock repository layer (no live CICS or DB2 connectivity)
- **Observability:** Structured JSON logging with correlation IDs; OpenTelemetry-ready tracing
- **Security Baseline:** TLS 1.2+, strict input validation, secrets via environment variables or secret manager only

### Preservation & Enhancement Rules
1. **Default Behavior:** Preserve all legacy observable behavior from INQACCCU COBOL program as the default execution path
2. **Future Enhancements:** Any new functionality must be explicitly marked and toggleable; do not change default behavior
3. **Architecture:** Keep controllers thin; business logic resides in service layer; repositories abstract persistence
4. **No Mainframe Mocking:** Do not attempt to call real CICS or DB2 systems in POC mode

---

## Feature: Customer Account Relationship Inquiry REST API

### Functional Scope

**Endpoint:** `GET /api/v1/customers/{customerId}/accounts`

**Input:**
- Path parameter: `customerId` (10-digit numeric string, required)
- Header: `Authorization: Bearer {JWT}` (required, OAuth2 resource server)

**Output (200 OK):**
```json
{
  "customerId": "0123456789",
  "customerFound": true,
  "numberOfAccounts": 2,
  "accounts": [
    {
      "eyeCatcher": "ACCT",
      "accountNumber": "12345678",
      "sortCode": "123456",
      "balance": "9876543.21",
      "interestRate": "2.5",
      "statementDate": "2025-01-15"
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request`: Invalid customer ID format or missing required fields
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: JWT valid but user role insufficient for `ROLE_CUSTOMER_INQUIRY`
- `500 Internal Server Error`: Unexpected server error

**Legacy Business Rules Mapped:**
- **BR001:** Accept 10-digit customer number; return CUSTOMER-FOUND flag (true/false) and 0–20 account records
- **BR002:** Validate customer number format strictly; reject non-numeric or invalid length inputs
- **BR003:** Return all associated accounts regardless of status (Active, Inactive, Closed)
- **BR004:** Preserve legacy response structure and field mappings from COBOL copybooks (INQACCCUZ, ACCOUNT, ACCDB2)

---

## Implementation Guidance

### Phase 1: Foundation & API Contract (Weeks 1–4)

#### Iteration 1A: Spring Boot Scaffolding (TASK-001)

**Objective:** Initialize Maven-based Spring Boot 3.3.x project with core dependencies.

**Deliverables:**
1. Create `pom.xml` with:
   - Spring Boot 3.3.x BOM
   - Spring Web, Spring Security (OAuth2 Resource Server)
   - Spring Data (mock persistence ready)
   - Micrometer Metrics, OpenTelemetry SDK
   - Jackson for JSON serialization
   - Lombok for boilerplate reduction
   - JUnit 5, Mockito for testing
2. Configure Maven profiles: `dev`, `test`, `prod`
3. Create `.gitignore` to exclude secrets, build artifacts, IDE files
4. Set Java 21 target in `<source>` and `<target>`
5. Establish directory structure: `src/main/java`, `src/test/java`, `src/main/resources`

**Acceptance Criteria:**
- [ ] AC-001.1: `mvn clean verify` succeeds; application starts with `mvn spring-boot:run`
- [ ] AC-001.2: No secrets in `pom.xml`; all sensitive configuration via environment variables
- [ ] AC-001.3: Build profiles selectable without code changes

**Pull Request Checklist:**
- All dependencies pinned to specific versions
- No `SNAPSHOT` or `RELEASE` versions in production profile
- Dependency security scan passes (no known CVEs)

---

#### Iteration 1B: Application Properties & Security Configuration (TASK-002)

**Objective:** Configure Spring Boot application for OAuth2 resource server and environment-driven secrets.

**Deliverables:**
1. Create `application.yml` (shared across profiles):
   ```yaml
   spring:
     application:
       name: inqacccu-api
     security:
       oauth2:
         resourceserver:
           jwt:
             issuer-uri: ${JWT_ISSUER_URI}
             jwk-set-uri: ${JWT_JWK_SET_URI}
   server:
     servlet:
       context-path: /api/v1
     ssl:
       enabled: true
       key-store: ${SERVER_SSL_KEYSTORE_PATH:#{null}}
       key-store-password: ${SERVER_SSL_KEYSTORE_PASSWORD}
   management:
     endpoints:
       web:
         exposure:
           include: health,metrics,info
   ```
2. Create `application-dev.yml`:
   - Override `ssl.enabled: false` for local development
   - Configure in-memory mock OAuth2 issuer for testing
3. Create `SecurityConfig` class:
   - Enable OAuth2 resource server filter chain
   - Configure RBAC: permit `/actuator/health` unauthenticated; require `ROLE_CUSTOMER_INQUIRY` for account endpoint
   - Add `JwtAuthenticationConverter` to map JWT claims to Spring Security authorities
4. Create `SecretValidator` bean to validate required environment variables at startup (e.g., `JWT_ISSUER_URI`, `JWT_JWK_SET_URI`)

**Acceptance Criteria:**
- [ ] AC-002.1: Application starts; `/actuator/health` returns 200 without JWT
- [ ] AC-002.2: Unauthenticated requests to `/api/v1/customers/{id}/accounts` return 401
- [ ] AC-002.3: Missing required secrets cause startup failure with clear error message
- [ ] AC-002.4: Valid JWT with `ROLE_CUSTOMER_INQUIRY` claim passes authorization filter
- [ ] AC-002.5: Valid JWT without required role returns 403

**Pull Request Checklist:**
- No hardcoded secrets; all externalized to environment variables
- `SecurityConfig` documented with Javadoc explaining RBAC rules
- Unit tests for `JwtAuthenticationConverter` and `SecretValidator`

---

#### Iteration 1C: Data Models & DTOs (TASK-003)

**Objective:** Define Java DTOs representing legacy COBOL copybook structures.

**Deliverables:**
1. Create `com.modernize.inqacccu.dto` package with:
   - `CustomerAccountsRequest` (if needed for input validation)
   - `CustomerAccountsResponse` wrapper DTO
   - `AccountDTO` (individual account record)
   - `ErrorResponse` (standardized error payload)
2. Map legacy COBOL fields to Java:
   - `CUSTOMER-NUMBER` (10 digits) → `String customerId`
   - `CUSTOMER-FOUND` ('Y'/'N') → `Boolean customerFound`
   - `NUMBER-OF-ACCOUNTS` (S9(8) BINARY) → `Integer numberOfAccounts`
   - Account fields: `accountNumber`, `sortCode`, `balance`, `interestRate`, `statementDate`
3. Add Jackson annotations:
   - `@JsonSerialize` for custom numeric formatting (balance, interest rate)
   - `@JsonProperty` to control field naming if needed
   - `@Schema` (OpenAPI) to document each field
4. Implement `equals`, `hashCode`, `toString` using Lombok `@Data` or `@EqualsAndHashCode`

**Example Structure:**
```java
@Data
@Builder
@Schema(description = "Customer account inquiry response")
public class CustomerAccountsResponse {
  @Schema(description = "10-digit customer ID", example = "0123456789")
  private String customerId;
  
  @Schema(description = "Whether customer was found")
  private Boolean customerFound;
  
  @Schema(description = "Number of associated accounts (0-20)")
  @Min(0) @Max(20)
  private Integer numberOfAccounts;
  
  @Schema(description = "List of account records")
  private List<AccountDTO> accounts;
}

@Data
@Builder
public class AccountDTO {
  private String eyeCatcher;
  private String accountNumber;
  private String sortCode;
  private String balance;
  private String interestRate;
  private String statementDate;
}

@Data
@Builder
public class ErrorResponse {
  private Integer status;
  private String message;
  private String correlationId;
  private LocalDateTime timestamp;
  private Map<String, Object> details;
}
```

**Acceptance Criteria:**
- [ ] AC-003.1: All DTOs compile without errors
- [ ] AC-003.2: Jackson serialization/deserialization works end-to-end (verified via test)
- [ ] AC-003.3: OpenAPI `@Schema` annotations populated; validate via OpenAPI spec generation

**Pull Request Checklist:**
- Immutable DTOs (use `@Builder`, no setters)
- No business logic in DTOs; data carriers only
- Comprehensive Javadoc for each DTO class and field

---

#### Iteration 1D: Mock Repository Layer (TASK-004)

**Objective:** Implement in-memory mock repository for POC phase (no DB2 or CICS connectivity).

**Deliverables:**
1. Create `com.modernize.inqacccu.repository` package with:
   - `AccountRepository` interface (contract for persistence)
   - `MockAccountRepository` implementation (hardcoded test data)
2. Define repository contract:
   ```java
   public interface AccountRepository {
     Optional<CustomerAccountRecord> findAccountsByCustomerId(String customerId);
   }
   ```
3. Implement mock with fixture data:
   ```java
   @Repository
   public class MockAccountRepository implements AccountRepository {
     private static final Map<String, CustomerAccountRecord> DATA = Map.ofEntries(
       Map.entry("0123456789", CustomerAccountRecord.builder()
         .customerId("0123456789")
         .customerFound(true)
         .accounts(List.of(
           AccountDTO.builder()
             .accountNumber("12345678")
             .sortCode("123456")
             .balance("9876543.21")
             .interestRate("2.5")
             .statementDate("2025-01-15")
             .build()
         ))
         .build())
     );
     
     @Override
     public Optional<CustomerAccountRecord> findAccountsByCustomerId(String customerId) {
       return Optional.ofNullable(DATA.get(customerId));
     }
   }
   ```
4. Add note in code: "POC mock data; replace with DB2/CICS adapter in production"

**Acceptance Criteria:**
- [ ] AC-004.1: `MockAccountRepository` returns valid data for known customer IDs
- [ ] AC-004.2: Unknown customer IDs return empty `Optional`
- [ ] AC-004.3: No network calls or external dependencies

**Pull Request Checklist:**
- Test data covers: existing customer (1–20 accounts), non-existent customer
- Repository interface documented with Javadoc
- Comments clearly mark mock implementation as POC-only

---

#### Iteration 1E: Service Layer & Business Logic (TASK-005)

**Objective:** Implement business logic layer; keep controller thin.

**Deliverables:**
1. Create `com.modernize.inqacccu.service` package with:
   - `CustomerAccountsService` interface
   - `CustomerAccountsServiceImpl` implementation
2. Service methods:
   ```java
   public interface CustomerAccountsService {
     CustomerAccountsResponse inquireAccounts(String customerId);
   }
   ```
3. Implement business logic:
   ```java
   @Service
   @Slf4j
   public class CustomerAccountsServiceImpl implements CustomerAccountsService {
     private final AccountRepository accountRepository;
     private final InputValidator inputValidator;
     
     @Autowired
     public CustomerAccountsServiceImpl(AccountRepository accountRepository, InputValidator inputValidator) {
       this.accountRepository = accountRepository;
       this.inputValidator = inputValidator;
     }
     
     @Override
     public CustomerAccountsResponse inquireAccounts(String customerId) {
       // BR002: Validate input strictly
       inputValidator.validateCustomerId(customerId);
       
       // BR001: Lookup customer and accounts
       Optional<CustomerAccountRecord> record = accountRepository.findAccountsByCustomerId(customerId);
       
       if (record.isEmpty()) {
         // BR001: customer not found
         return CustomerAccountsResponse.builder()
           .customerId(customerId)
           .customerFound(false)
           .numberOfAccounts(0)
           .accounts(Collections.emptyList())
           .build();
       }
       
       // BR004: Return all accounts (preserved from legacy)
       CustomerAccountRecord data = record.get();
       return CustomerAccountsResponse.builder()
         .customerId(customerId)
         .customerFound(true)
         .numberOfAccounts(data.getAccounts().size())
         .accounts(data.getAccounts())
         .build();
     }
   }
   ```
4. Create `InputValidator` utility:
   ```java
   @Component
   public class InputValidator {
     public void validateCustomerId(String customerId) throws InvalidInputException {
       if (customerId == null || !customerId.matches("^\\d{10}$")) {
         throw new InvalidInputException("Customer ID must be exactly 10 digits");
       }
     }
   }
   ```

**Acceptance Criteria:**
- [ ] AC-005.1: Valid customer ID returns populated response
- [ ] AC-005.2: Invalid customer ID throws `InvalidInputException`
- [ ] AC-005.3: Non-existent customer ID returns `customerFound=false`, `numberOfAccounts=0`
- [ ] AC-005.4: All business rules (BR001–BR004) implemented and tested

**Pull Request Checklist:**
- Service logic isolated; no HTTP concerns
- Comprehensive unit tests for each business rule
- Logging at INFO level for customer lookups (no PII in logs unless needed for debugging)

---

#### Iteration 1F: REST Controller & Error Handling (TASK-006)

**Objective:** Implement REST controller; integrate service layer; define error handling.

**Deliverables:**
1. Create `com.modernize.inqacccu.controller` package with:
   - `CustomerAccountsController` REST endpoint handler
   - `GlobalExceptionHandler` for centralized error responses
2. Implement controller:
   ```java
   @RestController
   @RequestMapping("/customers")
   @Slf4j
   public class CustomerAccountsController {
     private final CustomerAccountsService service;
     
     @Autowired
     public CustomerAccountsController(CustomerAccountsService service) {
       this.service = service;
     }
     
     @GetMapping("/{customerId}/accounts")
     @PreAuthorize("hasRole('ROLE_CUSTOMER_INQUIRY')")
     @Operation(summary = "Inquire customer accounts", security = @SecurityRequirement(name = "bearer-jwt"))
     @ApiResponses({
       @ApiResponse(responseCode = "200", description = "Accounts found or customer not found"),
       @ApiResponse(responseCode = "400", description = "Invalid customer ID format"),
       @ApiResponse(responseCode = "401", description = "Missing or invalid JWT"),
       @ApiResponse(responseCode = "403", description = "Insufficient role"),
       @ApiResponse(responseCode = "500", description = "Server error")
     })
     public ResponseEntity<CustomerAccountsResponse> inquireAccounts(
         @PathVariable @Schema(description = "10-digit customer ID", example = "0123