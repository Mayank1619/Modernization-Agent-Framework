# Program Analysis: INQACC Account Inquiry Modernization

**Document ID:** `program-analysis.md`  
**Analysis Date:** 2024  
**Target Pipeline:** mainframe_modernization  
**System Intent Authority:** provided/system-intent.md  
**Legacy Source Files:** cobol/INQACC.cbl, copybooks/ACCDB2.cpy, copybooks/ACCOUNT.cpy, copybooks/INQACCCZ.cpy  
**Target Stack:** Java 21, Spring Boot 3.3.x, React 18.x, TypeScript 5.x, Vite 5.x, Mock Repository (POC)

---

## 1. Program Inventory

### 1.1 Primary Program

| Attribute | Value |
|-----------|-------|
| **Program ID** | INQACC |
| **Author** | Jon Collett |
| **Type** | CICS-DB2 Online Inquiry Program |
| **Compiler Directives** | `CBL CICS('SP,EDF,DLI')`, `CBL SQL` |
| **Purpose** | Accept incoming account number; access DB2 ACCOUNT table; retrieve and return matching account record by composite key (ACCOUNT_SORTCODE + ACCOUNT_NUMBER) with optional ACCOUNT_TYPE discriminator |
| **Entry Point** | CICS Transaction (transaction code not documented in provided source) |
| **Error Handling Strategy** | Program abends on issues (legacy behavior noted in header comment: "Should there be any issues, the program will abend") |
| **Copybook Dependencies** | SORTCODE, ACCDB2, ACCOUNT, INQACCCZ, SQLCA (embedded) |
| **External Interfaces** | DB2 (ACCOUNT table via embedded SQL), CICS transaction dispatcher, terminal I/O |
| **State Management** | Stateless inquiry (read-only); no persistent working storage retained across transactions |
| **Performance Characteristics** | Synchronous blocking call to DB2; latency depends on table size and composite key index availability on (ACCOUNT_SORTCODE, ACCOUNT_NUMBER) |

### 1.2 Copybook Dependencies

| Copybook | Source | Records/Sections | Purpose |
|----------|--------|------------------|---------|
| **SORTCODE** | Referenced in INQACC.cbl (line 22) | Not provided | Assumed to define SORTCODE data structure or constants |
| **ACCDB2** | copybooks/ACCDB2.cpy | 1 EXEC SQL DECLARE TABLE | DB2 ACCOUNT table schema definition (12 columns) |
| **ACCOUNT** | copybooks/ACCOUNT.cpy | 1 structured copybook (ACCOUNT-DATA) | COBOL working storage structure mirroring DB2 ACCOUNT table |
| **INQACCCZ** | copybooks/INQACCCZ.cpy | 1 COMMAREA structure | CICS communication area for account inquiry results; supports 1–20 account occurrences |
| **SQLCA** | Embedded in INQACC.cbl (EXEC SQL INCLUDE SQLCA) | 1 SQL Communication Area | DB2 error/status feedback (SQLCODE, SQLSTATE) |

---

## 2. Data Structures and Field Map

### 2.1 Database Table Definition: ACCOUNT (ACCDB2.cpy)

**Source:** copybooks/ACCDB2.cpy  
**Schema Type:** DB2 SQL DECLARE TABLE  
**Composite Primary Key:** (ACCOUNT_SORTCODE, ACCOUNT_NUMBER)  
**Table Semantics:** Master account records for retail banking accounts

| DB2 Column | SQL Type | Nullable | COBOL Host Var | COBOL Type | Host Var Size | JSON Field (Modern) | Validation/Constraint |
|---|---|---|---|---|---|---|---|
| ACCOUNT_EYECATCHER | CHAR(4) | YES | HV-ACCOUNT-EYECATCHER | PIC X(4) | 4 bytes | `eyecatcher` | Literal 'ACCT' record marker; presence indicates valid account record |
| ACCOUNT_CUSTOMER_NUMBER | CHAR(10) | YES | HV-ACCOUNT-CUST-NO | PIC X(10) | 10 bytes | `customerNumber` | Numeric string (10 digits max); cross-reference to CUSTOMER master table |
| ACCOUNT_SORTCODE | CHAR(6) | NO | HV-ACCOUNT-SORTCODE | PIC X(6) | 6 bytes | `sortcode` | Bank routing code; composite key part 1; format: 6 numeric digits (required) |
| ACCOUNT_NUMBER | CHAR(8) | NO | HV-ACCOUNT-ACC-NO | PIC X(8) | 8 bytes | `accountNumber` | Account identifier; composite key part 2; format: 8 numeric digits (required) |
| ACCOUNT_TYPE | CHAR(8) | YES | HV-ACCOUNT-ACC-TYPE | PIC X(8) | 8 bytes | `accountType` | Account classification (e.g., 'CURRENT', 'SAVINGS', 'ISA'); optional discriminator in WHERE clause |
| ACCOUNT_INTEREST_RATE | DECIMAL(4,2) | YES | HV-ACCOUNT-INT-RATE | PIC S9(4)V99 COMP-3 | 3 bytes (packed) | `interestRate` | Annual interest rate as numeric decimal (e.g., 2.50 = 2.5%); range [0, 99.99] |
| ACCOUNT_OPENED | DATE | YES | HV-ACCOUNT-OPENED | PIC X(10) | 10 bytes | `accountOpened` | Account open date; format YYYY-MM-DD in DB2, stored as YYYYMMDD in COBOL |
| ACCOUNT_OVERDRAFT_LIMIT | INTEGER | YES | HV-ACCOUNT-OVERDRAFT-LIM | PIC S9(9) COMP | 4 bytes (binary) | `overdraftLimit` | Maximum overdraft allowance in minor currency units (pence); range: 0 to 999,999,999 |
| ACCOUNT_LAST_STATEMENT | DATE | YES | HV-ACCOUNT-LAST-STMT | PIC X(10) | 10 bytes | `lastStatementDate` | Date of last generated statement; format YYYY-MM-DD (DB2) → YYYYMMDD (COBOL) |
| ACCOUNT_NEXT_STATEMENT | DATE | YES | HV-ACCOUNT-NEXT-STMT | PIC X(10) | 10 bytes | `nextStatementDate` | Date of next scheduled statement; format YYYY-MM-DD (DB2) → YYYYMMDD (COBOL) |
| ACCOUNT_AVAILABLE_BALANCE | DECIMAL(10,2) | YES | HV-ACCOUNT-AVAIL-BAL | PIC S9(10)V99 COMP-3 | 6 bytes (packed) | `availableBalance` | Available balance in minor currency units (pence); includes active holds and pending transactions |
| ACCOUNT_ACTUAL_BALANCE | DECIMAL(10,2) | YES | HV-ACCOUNT-ACTUAL-BAL | PIC S9(10)V99 COMP-3 | 6 bytes (packed) | `actualBalance` | Actual account balance in minor currency units (pence); ledger balance excluding holds |

### 2.2 COBOL Working Storage Structure: HOST-ACCOUNT-ROW (INQACC.cbl, lines 34–45)

**Purpose:** DB2 host variable container for ACCOUNT table row retrieval  
**Total Record Size:** 75 bytes (4+10+6+8+8+3+10+4+10+10+6+6 bytes per field + alignment padding)

```cobol
01 HOST-ACCOUNT-ROW.
   03 HV-ACCOUNT-EYECATCHER     PIC X(4).
   03 HV-ACCOUNT-CUST-NO        PIC X(10).
   03 HV-ACCOUNT-SORTCODE       PIC X(6).
   03 HV-ACCOUNT-ACC-NO         PIC X(8).
   03 HV-ACCOUNT-ACC-TYPE       PIC X(8).
   03 HV-ACCOUNT-INT-RATE       PIC S9(4)V99 COMP-3.
   03 HV-ACCOUNT-OPENED         PIC X(10).
   03 HV-ACCOUNT-OVERDRAFT-LIM  PIC S9(9) COMP.
   03 HV-ACCOUNT-LAST-STMT      PIC X(10).
   03 HV-ACCOUNT-NEXT-STMT      PIC X(10).
   03 HV-ACCOUNT-AVAIL-BAL      PIC S9(10)V99 COMP-3.
   03 HV-ACCOUNT-ACTUAL-BAL     PIC S9(10)V99 COMP-3.
```

**Field Mapping to Modern JSON (DTO):**

| COBOL Variable | COBOL Type | Modernized JSON Field | Java Type | Transformation Rule |
|---|---|---|---|---|
| HV-ACCOUNT-EYECATCHER | PIC X(4) | `eyecatcher` | String | Trim trailing spaces; validate presence of 'ACCT' |
| HV-ACCOUNT-CUST-NO | PIC X(10) | `customerNumber` | String | Trim trailing spaces; pad with zeros if numeric |
| HV-ACCOUNT-SORTCODE | PIC X(6) | `sortcode` | String | Trim trailing spaces; validate 6 numeric digits |
| HV-ACCOUNT-ACC-NO | PIC X(8) | `accountNumber` | String | Trim trailing spaces; validate 8 numeric digits |
| HV-ACCOUNT-ACC-TYPE | PIC X(8) | `accountType` | String | Trim trailing spaces; enumerate values (CURRENT, SAVINGS, ISA, etc.) |
| HV-ACCOUNT-INT-RATE | PIC S9(4)V99 COMP-3 | `interestRate` | BigDecimal | Unpack COMP-3 binary; scale by 2 decimal places (divide by 100) |
| HV-ACCOUNT-OPENED | PIC X(10) | `accountOpened` | LocalDate | Parse YYYYMMDD format; convert to ISO 8601 YYYY-MM-DD in JSON |
| HV-ACCOUNT-OVERDRAFT-LIM | PIC S9(9) COMP | `overdraftLimit` | Long | Unpack binary integer; treat as pence value |
| HV-ACCOUNT-LAST-STMT | PIC X(10) | `lastStatementDate` | LocalDate | Parse YYYYMMDD format; convert to ISO 8601 YYYY-MM-DD in JSON |
| HV-ACCOUNT-NEXT-STMT | PIC X(10) | `nextStatementDate` | LocalDate | Parse YYYYMMDD format; convert to ISO 8601 YYYY-MM-DD in JSON |
| HV-ACCOUNT-AVAIL-BAL | PIC S9(10)V99 COMP-3 | `availableBalance` | BigDecimal | Unpack COMP-3 binary; scale by 2 decimal places (divide by 100); preserve sign |
| HV-ACCOUNT-ACTUAL-BAL | PIC S9(10)V99 COMP-3 | `actualBalance` | BigDecimal | Unpack COMP-3 binary; scale by 2 decimal places (divide by 100); preserve sign |

### 2.3 COMMAREA Structure: INQACCCZ (copybooks/INQACCCZ.cpy)

**Purpose:** CICS communication area for passing account inquiry results between INQACC and calling transaction  
**Semantics:** Supports 1–20 account records per inquiry (OCCURS 1 TO 20 DEPENDING ON NUMBER-OF-ACCOUNTS)

| COMMAREA Field | COBOL Type | Cardinality | Modernized Field (REST Response) | Purpose |
|---|---|---|---|---|
| NUMBER-OF-ACCOUNTS | PIC S9(8) BINARY | 1 | `accounts[]` (array length) | Count of returned account records (0–20); in modern REST, represented as JSON array |
| CUSTOMER-NUMBER | PIC 9(10) | 1 | `customerNumber` (top-level) | Customer identifier for cross-reference |
| COMM-SUCCESS | PIC X | 1 | HTTP Status Code (implicit) | Success indicator ('Y' = success, ' ' or 'N' = failure); modernized as HTTP 200/4xx/5xx |
| COMM-FAIL-CODE | PIC X | 1 | `error.code` (error envelope) | Application error code (e.g., 'A001' for account not found); modernized in error response |
| CUSTOMER-FOUND | PIC X | 1 | Implicit in response presence | Customer existence indicator ('Y'/'N'); modernized as HTTP 200 (found) or 404 (not found) |
| COMM-PCB-POINTER | PIC X(4) | 1 | N/A | DLI PCB pointer (mainframe-specific); not applicable in modern REST API |
| ACCOUNT-DETAILS | OCCURS 1–20 | Variable | `accounts[]` (JSON array of AccountRecord objects) | Repeated account record structure |
| └─ COMM-EYE | PIC X(4) | Per occurrence | `eyecatcher` | Record marker ('ACCT') |
| └─ COMM-CUSTNO | PIC X(10) | Per occurrence | `customerNumber` | Customer number |
| └─ COMM-SCODE | PIC X(6) | Per occurrence | `sortcode` | Bank sort code |
| └─ COMM-ACCNO | PIC 9(8) | Per occurrence | `accountNumber` | Account number |
| └─ COMM-ACC-TYPE | PIC X(8) | Per occurrence | `accountType` | Account type |
| └─ COMM-INT-RATE | PIC 9(4)V99 | Per occurrence | `interestRate` | Interest rate |
| └─ COMM-OPENED | PIC 9(8) | Per occurrence | `accountOpened` | Account open date (YYYYMMDD) |
| └─ COMM-OVERDRAFT | PIC 9(8) | Per occurrence | `overdraftLimit` | Overdraft limit |
| └─ COMM-LAST-STMT-DT | PIC 9(8) | Per occurrence | `lastStatementDate` | Last statement date (YYYYMMDD) |
| └─ COMM-NEXT-STMT-DT | PIC 9(8) | Per occurrence | `nextStatementDate` | Next statement date (YYYYMMDD) |
| └─ COMM-AVAIL-BAL | PIC S9(10)V99 | Per occurrence | `availableBalance` | Available balance (pence) |
| └─ COMM-ACTUAL-BAL | PIC S9(10)V99 | Per occurrence | `actualBalance` | Actual balance (pence) |

**Note:** Legacy INQACCCZ supports up to 20 account occurrences (OCCURS 1 TO 20). Modernized REST API returns single account record per request (no array); multiple account support deferred to future enhancement.

### 2.4 ACCOUNT Copybook Structure (copybooks/ACCOUNT.cpy)

**Purpose:** COBOL working storage structure for account data manipulation in batch and online programs  
**Semantics:** Mirrors DB2 ACCOUNT table with REDEFINES clauses for date field decomposition

```cobol
03 ACCOUNT-DATA.
   05 ACCOUNT-EYE-CATCHER        PIC X(4).
      88 ACCOUNT-EYECATCHER-VALUE       VALUE 'ACCT'.
   05 ACCOUNT-CUST-NO            PIC 9(10).
   05 ACCOUNT-KEY.
      07 ACCOUNT-SORT-CODE       PIC 9(6).
      07 ACCOUNT-NUMBER          PIC 9(8).
   05 ACCOUNT-TYPE               PIC X(8).
   05 ACCOUNT-INTEREST-RATE      PIC 9(4)V99.
   05 ACCOUNT-OPENED             PIC 9(8).
   05 ACCOUNT-OPENED-GROUP REDEFINES ACCOUNT-OPENED.
      07 ACCOUNT-OPENED-DAY       PIC 99.
      07 ACCOUNT-OPENED-MONTH