# business-rules.md

**Document ID:** `business-rules-inqacccu-001`  
**Pipeline:** `mainframe_modernization`  
**Target Artifact:** INQACCCU Business Rules Extraction  
**Generated From:** Legacy COBOL Analysis, Copybooks, System Intent  

---

## Rule Inventory

### BR001: Customer Inquiry Acceptance Rule

**ID:** BR001  
**Statement:** Accept a customer number (10 digits) as input and initiate an account relationship inquiry.  
**Trigger Condition:** Incoming CICS transaction with valid 10-digit customer number in CUSTOMER-NUMBER field.  
**Input:** 
- CUSTOMER-NUMBER (PIC 9(10))

**Output:**
- CUSTOMER-FOUND (PIC X: 'Y' or 'N')
- NUMBER-OF-ACCOUNTS (PIC S9(8) BINARY)
- ACCOUNT-DETAILS array (0–20 occurrences)

**Error Condition:** 
- If customer number is invalid or missing, CUSTOMER-FOUND = 'N', NUMBER-OF-ACCOUNTS = 0.

**Modernization Notes:** Map to Spring Boot REST endpoint `GET /api/v1/customers/{customerId}/accounts` with OAuth2 authorization.

---

### BR002: Account Lookup and Retrieval Rule

**ID:** BR002  
**Statement:** Query the ACCOUNT database table using customer number to retrieve all associated accounts, limited to maximum 20 records.  
**Trigger Condition:** CUSTOMER-FOUND = 'Y' and database connection established.  
**Input:**
- ACCOUNT_CUSTOMER_NUMBER (matched against input CUSTOMER-NUMBER)
- ACCOUNT table from DB2

**Output:**
- ACCOUNT-DETAILS array populated with up to 20 account records
- NUMBER-OF-ACCOUNTS = actual count of retrieved records

**Error Condition:**
- If database query fails, set COMM-FAIL-CODE and return empty account list.
- If no accounts found for valid customer, return NUMBER-OF-ACCOUNTS = 0.

**Modernization Notes:** Implement as service-layer method with mock repository for POC; preserve legacy query logic in adapter pattern.

---

### BR003: Account Record Population Rule

**ID:** BR003  
**Statement:** For each matched account record, populate communication area fields by copying database columns to COBOL copybook structure.  
**Trigger Condition:** Account row retrieved from ACCOUNT table.  
**Input:**
- ACCOUNT_EYECATCHER (CHAR(4))
- ACCOUNT_SORTCODE (CHAR(6))
- ACCOUNT_NUMBER (CHAR(8))
- ACCOUNT_TYPE (CHAR(8))
- ACCOUNT_INTEREST_RATE (DECIMAL(4, 2))
- ACCOUNT_OPENED (DATE)
- ACCOUNT_OVERDRAFT_LIMIT (INTEGER)
- ACCOUNT_LAST_STATEMENT (DATE)
- ACCOUNT_NEXT_STATEMENT (DATE)
- ACCOUNT_AVAILABLE_BALANCE (DECIMAL(10, 2))
- ACCOUNT_ACTUAL_BALANCE (DECIMAL(10, 2))

**Output:**
- COMM-EYE (PIC X(4)) ← ACCOUNT_EYECATCHER
- COMM-SCODE (PIC X(6)) ← ACCOUNT_SORTCODE
- COMM-ACCNO (PIC 9(8)) ← ACCOUNT_NUMBER
- COMM-ACC-TYPE (PIC X(8)) ← ACCOUNT_TYPE
- COMM-INT-RATE (PIC 9(4)V99) ← ACCOUNT_INTEREST_RATE
- COMM-OPENED (PIC 9(8)) ← ACCOUNT_OPENED
- COMM-OVERDRAFT (PIC 9(8)) ← ACCOUNT_OVERDRAFT_LIMIT
- COMM-LAST-STMT-DT (PIC 9(8)) ← ACCOUNT_LAST_STATEMENT
- COMM-NEXT-STMT-DT (PIC 9(8)) ← ACCOUNT_NEXT_STATEMENT
- COMM-AVAIL-BAL (PIC S9(10)V99) ← ACCOUNT_AVAILABLE_BALANCE
- COMM-ACTUAL-BAL (PIC S9(10)V99) ← ACCOUNT_ACTUAL_BALANCE

**Error Condition:** If data type conversion fails (e.g., invalid date format), reject the account record and log error with COMM-FAIL-CODE.

**Modernization Notes:** Implement as DTO mapping layer (ModelMapper or MapStruct) in Spring Boot; preserve field semantics and validation rules.

---

### BR004: Account Eyecatcher Validation Rule

**ID:** BR004  
**Statement:** Validate that account record eyecatcher equals literal 'ACCT' to confirm record type integrity.  
**Trigger Condition:** Account record retrieved from database.  
**Input:**
- ACCOUNT_EYECATCHER (CHAR(4))

**Output:**
- ACCOUNT-EYECATCHER-VALUE condition set ('ACCT')

**Error Condition:** If eyecatcher ≠ 'ACCT', reject record as corrupted and set error flag.

**Modernization Notes:** Implement as record validation in AccountEntity; use constraint annotations (@Pattern or custom validator).

---

### BR005: Customer Found Status Rule

**ID:** BR005  
**Statement:** Set CUSTOMER-FOUND indicator based on whether at least one account record is retrieved for the input customer number.  
**Trigger Condition:** Database query completed.  
**Input:**
- Query result set size

**Output:**
- CUSTOMER-FOUND = 'Y' if NUMBER-OF-ACCOUNTS > 0
- CUSTOMER-FOUND = 'N' if NUMBER-OF-ACCOUNTS = 0

**Error Condition:** If query execution fails, default CUSTOMER-FOUND = 'N'.

**Modernization Notes:** Implement as conditional logic in service layer; expose as boolean field `customerFound` in REST response DTO.

---

### BR006: Maximum Accounts Boundary Rule

**ID:** BR006  
**Statement:** Limit account details array to maximum 20 occurrences (ACCOUNT-DETAILS OCCURS 1 TO 20).  
**Trigger Condition:** Account retrieval loop active.  
**Input:**
- Running count of processed account records

**Output:**
- NUMBER-OF-ACCOUNTS capped at 20
- Excess records discarded (or logged as truncation warning)

**Error Condition:** If NUMBER-OF-ACCOUNTS exceeds 20, truncate silently and optionally set warning flag in COMM-FAIL-CODE.

**Modernization Notes:** Enforce in Spring Data pagination or custom repository; document truncation behavior in API response headers or metadata field.

---

### BR007: Communication Area Success/Failure Flag Rule

**ID:** BR007  
**Statement:** Set COMM-SUCCESS and COMM-FAIL-CODE flags to indicate transaction completion status and error classification.  
**Trigger Condition:** Program completion (normal or exceptional).  
**Input:**
- Transaction outcome (success / database error / validation error / etc.)

**Output:**
- COMM-SUCCESS (PIC X: 'Y' or 'N')
- COMM-FAIL-CODE (PIC X: error classification code)

**Error Condition:** 
- Database connectivity failure → COMM-FAIL-CODE = 'D'
- Invalid customer number → COMM-FAIL-CODE = 'I'
- No customer found → COMM-FAIL-CODE = 'N'
- Successful query → COMM-SUCCESS = 'Y', COMM-FAIL-CODE = SPACE

**Modernization Notes:** Map to HTTP status codes (200, 400, 404, 500) in Spring Boot REST controller; include error code in standardized error response body (per security baseline).

---

### BR008: Date/Time Population Rule

**ID:** BR008  
**Statement:** Populate current date and time in response working storage using CICS ASKTIME and FORMATTIME.  
**Trigger Condition:** Program initialization (POPULATE-TIME-DATE section).  
**Input:**
- System time (CICS ASKTIME)

**Output:**
- WS-ORIG-DATE (DDMMYYYY format)
- WS-TIME-NOW (HH:MM:SS format)

**Error Condition:** If CICS time service unavailable, use system default or return null.

**Modernization Notes:** Remove CICS dependency; use Java `java.time.LocalDateTime` or Spring Framework timing utilities. Include response timestamp in JSON body as ISO-8601 UTC format with correlation ID.

---

### BR009: PCB Pointer Management Rule

**ID:** BR009  
**Statement:** Maintain DLI PCB (Program Communication Block) pointer for IMS/CICS integration (legacy artifact).  
**Trigger Condition:** Program initialization and database access.  
**Input:**
- COMM-PCB-POINTER (PIC X(4))

**Output:**
- PCB pointer state maintained for IMS message handling

**Error Condition:** If PCB initialization fails, transaction fails with error code 'P'.

**Modernization Notes:** **REMOVE in modernization.** PCB pointers are IMS/CICS legacy constructs. Replace with Spring Data repository dependency injection. Document as "Legacy Artifact — Not Required" in modernization checklist.

---

### BR010: Authorization and Role-Based Access Control Rule

**ID:** BR010  
**Statement:** Validate that authenticated user holds required role to access customer-account inquiry for a given customer.  
**Trigger Condition:** Incoming REST request with OAuth2 JWT bearer token.  
**Input:**
- JWT bearer token
- Customer ID path parameter
- User roles from token claims

**Output:**
- Request authorized → proceed to service logic
- Request denied → return HTTP 403 Forbidden with error message

**Error Condition:** 
- Missing bearer token → HTTP 401 Unauthorized
- Invalid token signature → HTTP 401 Unauthorized
- User role insufficient → HTTP 403 Forbidden
- Customer ID mismatch with user's scope → HTTP 403 Forbidden

**Modernization Notes:** Implement using Spring Security with `@PreAuthorize` annotations and OAuth2ResourceServerConfigurer; extract customer scope from JWT claim validation.

---

### BR011: Input Validation Rule

**ID:** BR011  
**Statement:** Validate incoming customer number format and length before database query execution.  
**Trigger Condition:** REST request received with customer ID parameter.  
**Input:**
- Customer ID string from path parameter

**Output:**
- Valid: proceed to query
- Invalid: return HTTP 400 Bad Request with validation error details

**Error Condition:**
- Customer ID length ≠ 10 digits
- Customer ID contains non-numeric characters
- Customer ID is null or empty
- Customer ID outside valid business range (e.g., all zeros)

**Modernization Notes:** Implement using Spring Validation (@Pattern, @NotNull, custom validators); define in OpenAPI 3.0.3 schema; return standardized error response per security baseline.

---

### BR012: Structured Logging and Correlation Rule

**ID:** BR012  
**Statement:** Log all inquiry transactions with structured JSON format, including correlation ID for traceability.  
**Trigger Condition:** Request entry and exit points.  
**Input:**
- Request correlation ID (from HTTP header or generated)
- Customer ID, user principal, outcome, latency, error details

**Output:**
- JSON log record written to application log stream

**Example Log Entry:**
```json
{
  "timestamp": "2024-01-15T14:32:50.123Z",
  "correlationId": "req-12345-abcde",
  "level": "INFO",
  "message": "CustomerAccountInquiry completed",
  "customerId": "1234567890",
  "numberOfAccounts": 3,
  "latencyMs": 145,
  "principal": "user@example.com",
  "status": "SUCCESS"
}
```

**Error Condition:** 
- Missing correlation ID → generate new UUID
- Logging framework failure → fail-safe to stderr

**Modernization Notes:** Implement using Spring Cloud Sleuth + SLF4J with Logback/Log4j2; configure JSON encoder (Logstash or similar); enable distributed tracing readiness with OpenTelemetry.

---

### BR013: Metrics Collection Rule

**ID:** BR013  
**Statement:** Collect and expose operational metrics for customer inquiry endpoint.  
**Trigger Condition:** Each request completion.  
**Input:**
- Request latency (ms)
- HTTP status code
- Error classification (if applicable)
- Downstream adapter status (DB2 connection health)

**Output:**
- Micrometer metrics registered and exported

**Metrics to Track:**
- `inqacccu.inquiry.requests.total` (counter by status code)
- `inqacccu.inquiry.latency.seconds` (histogram)
- `inqacccu.inquiry.errors.total` (counter by error type)
- `inqacccu.db.connection.health` (gauge: up/down)

**Modernization Notes:** Implement using Spring Boot Actuator + Micrometer; export to Prometheus (or Datadog/Jaeger) per operational baseline.

---

### BR014: Temporal Data Format Rule

**ID:** BR014  
**Statement:** All date fields must be converted from COBOL numeric format (YYYYMMDD or DDMMYYYY) to ISO-8601 UTC format (YYYY-MM-DDTHH:MM:SSZ) in REST response.  
**Trigger Condition:** Account record population.  
**Input:**
- ACCOUNT_OPENED (DATE)
- ACCOUNT_LAST_STATEMENT (DATE)
- ACCOUNT_NEXT_STATEMENT (DATE)

**Output:**
- JSON response field: `accountOpened: "2023-01-15"`
- JSON response field: `lastStatementDate: "2023-12-31T23:59:59Z"`

**Error Condition:** If date value is null, invalid, or zero-date, return null in JSON or document as missing_date flag.

**Modernization Notes:** Implement using Jackson `@JsonFormat(pattern="yyyy-MM-dd'T'HH:mm:ss'Z'")` or custom serializer; validate date bounds (1900–2099 range for banking context).

---

### BR015: Decimal Precision and Rounding Rule

**ID:** BR015  
**Statement:** All monetary amounts (balances, interest rates) must maintain 2 decimal places and use banker's rounding (HALF_EVEN) for calculation.  
**Trigger Condition:** Account balance or interest rate population.  
**Input:**
- ACCOUNT_AVAILABLE_BALANCE (DECIMAL(10, 2))
- ACCOUNT_ACTUAL_BALANCE (DECIMAL(10, 2))
- ACCOUNT_INTEREST_RATE (DECIMAL(4, 2))

**Output:**
- JSON response field with 2 decimal places: `"availableBalance": "12345.67"`

**Error Condition:** If precision loss detected during conversion, log warning and retain maximum available precision.

**Modernization Notes:** Use Java `java.math.BigDecimal` with `RoundingMode.HALF_EVEN`; configure Jackson serializer to enforce 2-decimal JSON output; document rounding policy in API documentation.

---

### BR016: Response Envelope and Versioning Rule

**ID:** BR016  
**Statement:** All REST responses must be wrapped in a standard envelope with API version, timestamp, and optional metadata.  
**Trigger Condition:** Request completion (success or error).  
**Input:**
- Response payload (account details or error)
- API version (from header or config)

**Output:**
```json
{
  "apiVersion": "v1",
  "timestamp": "2024-01-15T14:32:50.123Z",
  "correlationId": "req-12345-abcde",
  "data": { ... },
  "errors": null
}
```

**Error Condition:**
- On error, `data: null`, `errors: [{ code: "...", message: "..." }]`

**Modernization Notes:** Implement as Spring @ControllerAdvice with custom response wrapper; configure in OpenAPI 3.0.3 schema definition.

---

### BR017: Secret and Configuration Management Rule

**ID:** BR017  
**Statement:** Database credentials, OAuth2 secrets, and API keys must be externalized from source code and managed via environment variables or secret manager.  
**Trigger Condition:** Application bootstrap.  
**Input:**
- Environment variables (e.g., DB_HOST, DB_PORT, OAUTH2_CLIENT_SECRET)
- Secret manager (e.g., AWS Secrets Manager, HashiCorp Vault)

**Output:**
- Credentials injected into Spring context without source exposure

**Error Condition:** 
- Missing required secret → application startup fails with clear error
- Invalid secret format → validation failure during initialization

**Modernization Notes:** Use Spring Cloud Config + `@Value` or Spring Cloud Vault; document required environment variables in deployment runbook; never commit secrets