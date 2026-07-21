# Program Analysis Report: INQACCCU

**Document ID:** `prog-analysis-inqacccu-001`  
**Generated:** Mainframe Modernization Pipeline  
**Target Output:** `program-analysis.md`

---

## 1. Program Inventory

| Attribute | Value |
|-----------|-------|
| **Program ID** | INQACCCU |
| **Author** | James O'Grady |
| **Copyright** | IBM Corp. 2023 |
| **Language** | COBOL |
| **Compile Options** | CBL CICS('SP,EDF,DLI'), CBL SQL |
| **Program Type** | Online Inquiry (CICS) |
| **Purpose** | Customer ↔ Account Relationship Inquiry |

---

## 2. Data Structures and Field Map

### 2.1 Input/Output Communication Area: `INQACCCUZ.cpy`

| Field Name | Type | Length | PIC Clause | Purpose | Modernization Notes |
|------------|------|--------|-----------|---------|-------------------|
| NUMBER-OF-ACCOUNTS | Binary signed | 4 bytes | S9(8) BINARY | Count of returned accounts (0–20) | Map to `Integer` in Java; validate upper bound |
| CUSTOMER-NUMBER | Numeric | 10 digits | 9(10) | Input: customer identifier | Convert to `String` or `Long`; add format validation |
| COMM-SUCCESS | Character | 1 byte | X | Success flag ('Y'/'N') | Map to `Boolean` response wrapper |
| COMM-FAIL-CODE | Character | 1 byte | X | Error code on failure | Standardize to enumerated error codes |
| CUSTOMER-FOUND | Character | 1 byte | X | Customer existence flag ('Y'/'N') | Include in response DTO |
| COMM-PCB-POINTER | Character | 4 bytes | X(4) | DLI pointer (mainframe-specific) | **REMOVE** in modernization; not applicable to Spring Boot |
| ACCOUNT-DETAILS (OCCURS 1-20) | Group | Variable | — | Repeating account records | Map to `List<AccountDetailDTO>` |

#### ACCOUNT-DETAILS Repeating Group (per occurrence):

| Field Name | Type | Length | PIC Clause | Purpose |
|------------|------|--------|-----------|---------|
| COMM-EYE | Character | 4 bytes | X(4) | Eyecatcher ('ACCT') |
| COMM-CUSTNO | Character | 10 bytes | X(10) | Customer number (redundant per occurrence) |
| COMM-SCODE | Character | 6 bytes | X(6) | Sort code (routing/bank code) |
| COMM-ACCNO | Numeric | 8 digits | 9(8) | Account number |
| COMM-ACC-TYPE | Character | 8 bytes | X(8) | Account type (e.g., 'CHECKING', 'SAVINGS') |
| COMM-INT-RATE | Decimal | 6 digits | 9(4)V99 | Interest rate (0–99.99%) |
| COMM-OPENED | Numeric | 8 digits | 9(8) | Account open date (YYYYMMDD) |
| COMM-OVERDRAFT | Numeric | 8 digits | 9(8) | Overdraft limit |
| COMM-LAST-STMT-DT | Numeric | 8 digits | 9(8) | Last statement date (YYYYMMDD) |
| COMM-NEXT-STMT-DT | Numeric | 8 digits | 9(8) | Next statement date (YYYYMMDD) |
| COMM-AVAIL-BAL | Signed Decimal | 12 digits | S9(10)V99 | Available balance (−999999999.99 to +999999999.99) |
| COMM-ACTUAL-BAL | Signed Decimal | 12 digits | S9(10)V99 | Actual balance (−999999999.99 to +999999999.99) |

### 2.2 Database Table: `ACCDB2.cpy`

**SQL Declaration:** `ACCOUNT` table

| Column Name | DB2 Type | Nullable | Legacy COBOL Field | Purpose |
|-------------|----------|----------|-------------------|---------|
| ACCOUNT_EYECATCHER | CHAR(4) | NOT NULL | ACCOUNT-EYE-CATCHER | Record marker ('ACCT') |
| ACCOUNT_CUSTOMER_NUMBER | CHAR(10) | YES | ACCOUNT-CUST-NO | Foreign key to customer |
| ACCOUNT_SORTCODE | CHAR(6) | NO | ACCOUNT-SORT-CODE | Bank routing code |
| ACCOUNT_NUMBER | CHAR(8) | NO | ACCOUNT-NUMBER | Primary key (with sort code) |
| ACCOUNT_TYPE | CHAR(8) | YES | ACCOUNT-TYPE | Account classification |
| ACCOUNT_INTEREST_RATE | DECIMAL(4,2) | YES | ACCOUNT-INTEREST-RATE | Annual rate (0–99.99%) |
| ACCOUNT_OPENED | DATE | YES | ACCOUNT-OPENED | Account creation date |
| ACCOUNT_OVERDRAFT_LIMIT | INTEGER | YES | ACCOUNT-OVERDRAFT-LIMIT | Overdraft facility amount |
| ACCOUNT_LAST_STATEMENT | DATE | YES | ACCOUNT-LAST-STMT-DATE | Most recent statement date |
| ACCOUNT_NEXT_STATEMENT | DATE | YES | ACCOUNT-NEXT-STMT-DATE | Projected next statement date |
| ACCOUNT_AVAILABLE_BALANCE | DECIMAL(10,2) | YES | ACCOUNT-AVAILABLE-BALANCE | Liquidity-adjusted balance |
| ACCOUNT_ACTUAL_BALANCE | DECIMAL(10,2) | YES | ACCOUNT-ACTUAL-BALANCE | Book balance |

**Assumed Primary Key:** `(ACCOUNT_SORTCODE, ACCOUNT_NUMBER)`  
**Assumed Foreign Key:** `ACCOUNT_CUSTOMER_NUMBER` → CUSTOMER table

---

## 3. Business Process Flow

### 3.1 Inquiry Sequence (Legacy CICS Online)

```
1. CICS terminal user enters customer number
   ↓
2. INQACCCU program receives CUSTOMER-NUMBER via COMMAREA
   ↓
3. Validate customer number format (10 digits)
   ↓
4. Query DB2 ACCOUNT table:
   WHERE ACCOUNT_CUSTOMER_NUMBER = input_customer_number
   ↓
5. Fetch up to 20 matching account records
   ↓
6. Populate ACCOUNT-DETAILS repeating group in response COMMAREA
   ↓
7. Set flags:
   - CUSTOMER-FOUND = 'Y' (if ≥1 match) or 'N' (if 0 matches)
   - NUMBER-OF-ACCOUNTS = count of matches
   - COMM-SUCCESS = 'Y' (if query succeeded) or 'N' (on error)
   - COMM-FAIL-CODE = error code (if applicable)
   ↓
8. Return COMMAREA to CICS terminal
   ↓
9. User views account roster with balances and statement dates
```

### 3.2 Assumptions (Marked Explicitly)

| # | Assumption | Evidence | Risk |
|---|-----------|----------|------|
| A1 | Query returns **up to 20 accounts per customer** | `ACCOUNT-DETAILS OCCURS 1 TO 20 DEPENDING ON NUMBER-OF-ACCOUNTS` | Customers with >20 accounts will be truncated; no pagination in legacy design. **Modernization:** implement pagination. |
| A2 | Customer number is **always 10 numeric digits**, left-padded with zeros | `PIC 9(10)` in input and DB2 schema | Validation must reject non-numeric or <10-char input. **Modernization:** stricter format validation in API contract. |
| A3 | Date fields are **YYYYMMDD format** in COBOL; DATE type in DB2 | `PIC 9(8)` in COBOL; `DATE` in SQL schema | Conversion required: DB2 DATE → COBOL numeric 8-digit. **Modernization:** use ISO 8601 in JSON API. |
| A4 | Program uses **CICS pseudo-conversational model** (request-response) | `CBL CICS('SP,EDF,DLI')` compile options; ASKTIME, FORMATTIME directives | Legacy online inquiry; no persistent session. **Modernization:** stateless REST endpoint. |
| A5 | DB2 connectivity is **synchronous and blocking** | Implicit in EXEC SQL structure | Long-running queries will block CICS transaction. **Modernization:** consider async adapters if latency is concern. |
| A6 | **DLI (Data Language Interface) pointer** is passed but purpose unclear | `COMM-PCB-POINTER PIC X(4)` in COMMAREA | Likely legacy artifact from prior DLI integration. **Action:** confirm with SME; remove if unused. |
| A7 | Eyecatcher 'ACCT' is **data validation marker**, not functional flag | `88 ACCOUNT-EYECATCHER-VALUE VALUE 'ACCT'` in copybook | Defensive programming; indicates well-formed record. **Modernization:** validate at serialization layer only. |
| A8 | **No explicit error handling shown in snippet** for DB2 failures (SQLCODE, SQLERRM) | Preview truncated; infer from COMM-FAIL-CODE field | Error codes must be catalogued from full source. **Risk:** ambiguous error reporting. |
| A9 | **Decimal precision:** balances stored as `DECIMAL(10,2)` (±99,999,999.99) and `9(10)V99` in COBOL | Both schemas align | **Modernization:** use `java.math.BigDecimal` for monetary values; no floating-point arithmetic. |

---

## 4. Batch vs. Online Assumptions

| Characteristic | Classification | Evidence |
|---|---|---|
| **Invocation** | **Online (CICS)** | `CBL CICS(...)` compile option; ASKTIME/FORMATTIME directives indicate real-time transaction |
| **Concurrency** | **Multi-user** | CICS is multi-threaded; no locking strategy visible in preview |
| **Data Scope** | **Single inquiry per request** | One CUSTOMER-NUMBER input; 1–20 accounts output per call |
| **Latency Sensitivity** | **High** | Real-time terminal user waiting; query must complete in sub-second |
| **Transactionality** | **Likely read-only** | No UPDATE/DELETE observed; SELECT + FETCH implied |
| **Logging** | **CICS Transaction Server logs** | Legacy audit trail via CICS Transaction ID; not portable to modern stacks |
| **Scheduling** | **On-demand** | No batch scheduling; triggered by user interaction |

**Modernization Impact:**  
Convert to **stateless REST endpoint** (Spring Boot `@RestController`); no session affinity required.

---

## 5. Risks and Unknowns

### 5.1 Critical Risks

| ID | Risk | Severity | Mitigation Strategy |
|----|------|----------|-------------------|
| **R-001** | **Data truncation at 20 accounts** | HIGH | Implement pagination in REST API; document breaking change in release notes |
| **R-002** | **Decimal precision loss in JSON serialization** | MEDIUM | Use `BigDecimal` Java type; configure Jackson to preserve scale |
| **R-003** | **SQLCODE/SQLERRM error codes not documented** | MEDIUM | Extract full error handling from source; catalogue codes in error response enum |
| **R-004** | **Date format ambiguity (YYYYMMDD vs. ISO 8601)** | MEDIUM | Enforce ISO 8601 (RFC 3339) in REST API; add automated test for date boundary cases |
| **R-005** | **Customer number validation logic not visible** | MEDIUM | Confirm: is format validation done in INQACCCU or upstream? Add explicit regex: `^\d{10}$` |
| **R-006** | **DLI pointer (COMM-PCB-POINTER) purpose unclear** | LOW | Confirm with SME; likely legacy artifact; safe to remove |
| **R-007** | **Concurrent request handling not documented** | MEDIUM | Assume stateless concurrent model; mock repository must be thread-safe |

### 5.2 Data Quality Unknowns

| ID | Unknown | Impact | Action Items |
|----|---------|--------|--------------|
| **U-001** | **Do all ACCOUNT records have ACCOUNT_CUSTOMER_NUMBER?** | Foreign key validation; orphaned records? | Query: `SELECT COUNT(*) WHERE ACCOUNT_CUSTOMER_NUMBER IS NULL` |
| **U-002** | **What is distribution of accounts per customer (min, max, average)?** | Pagination design; caching strategy | Run: `SELECT CUSTOMER_NUMBER, COUNT(*) FROM ACCOUNT GROUP BY CUSTOMER_NUMBER ORDER BY COUNT(*) DESC LIMIT 10` |
| **U-003** | **Are date fields ever NULL or do they default to epoch (00000000)?** | API contract; serialization handling | Confirm with DB2 schema constraints and sample query results |
| **U-004** | **Do overlapping ACCOUNT_SORTCODE + ACCOUNT_NUMBER exist (duplicate keys)?** | Data integrity; join correctness | Run: `SELECT ACCOUNT_SORTCODE, ACCOUNT_NUMBER, COUNT(*) FROM ACCOUNT GROUP BY 1, 2 HAVING COUNT(*) > 1` |
| **U-005** | **What is the maximum length of ACCOUNT_TYPE and is it standardized?** | Enum vs. string in DTO | Validate all distinct values: `SELECT DISTINCT ACCOUNT_TYPE FROM ACCOUNT` |

### 5.3 Operational Unknowns

| ID | Unknown | Impact | Action Items |
|----|---------|--------|--------------|
| **O-001** | **Current throughput and latency SLA for INQACCCU in production** | Performance tuning baseline | Obtain from operations: response time p50, p95, p99; TPS |
| **O-002** | **Are there any ETL or data refresh windows?** | Cache invalidation strategy; availability | Confirm daily/weekly batch jobs that load ACCOUNT table |
| **O-003** | **What authentication/authorization is currently enforced?** | OAuth2 scope mapping; role names | Interview CICS security team; map RACF roles to Spring Security authorities |
| **O-004** | **Are there downstream consumers of INQACCCU output (API integration)?** | API versioning; backward compatibility | Identify all CICS transactions or systems calling INQACCCU |

---

## 6. Modernization Readiness Assessment

### 6.1 Target Architecture Alignment (per `system-intent.md`)

| Requirement | Status | Notes |
|-------------|--------|-------|
| **Backend: Java 21, Spring Boot 3.3.x** | ✅ READY | No JDK-specific dependencies in COBOL; straightforward mapping |
| **Frontend: React 18.x, TypeScript 5.x** | ✅ READY | Simple inquiry UI; list + detail view pattern |
| **API: REST over HTTPS, OpenAPI 3.0.3** | ⚠️ PLANNED | Define `/api/v1/customers/{customerId}/accounts` GET endpoint; generate spec |
| **OAuth2 + JWT** | ⚠️ PLANNED | Assume bearer token in Authorization header; validate customer scopes |
| **Role-based access control** | ⚠️ PLANNED | Map CICS RACF roles to Spring Security @PreAuthorize annotations |
| **Mock repository (no live DB2)** | ⚠️ PLANNED | Create `AccountRepositoryMock` returning hardcoded test datasets |
| **Structured JSON logging + correlation ID** | ⚠️ PLANNED | Configure Spring Cloud Sleuth + Logback; log all DB queries |
| **OpenTelemetry ready** | ⚠️ PLANNED | Add `spring-boot-starter-actuator` + micrometer; export to Jaeger/Datadog |

### 6.2 Data Model Mapping (COBOL → Java DTO)

```java
// Legacy COBOL: INQACCCUZ.cpy
// Modernized DTO hierarchy:

@Data
public class CustomerAccountsResponse {
  private String customerId;        // CUSTOMER-NUMBER (10 digits)
  private Boolean customerFound;    // CUSTOMER-FOUND ('Y'/'N')
  private Integer numberOfAcc