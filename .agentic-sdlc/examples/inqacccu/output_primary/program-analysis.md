# Program Analysis

## 1. Program Inventory

### 1.1 Program Details
- **Program Name**: INQACCCU
- **Author**: James O'Grady
- **Purpose**: To retrieve account records associated with a given customer number.

### 1.2 Related Copybooks
- **ACCDB2.cpy**: Defines the SQL structure for the ACCOUNT table.
- **ACCOUNT.cpy**: Contains the data structure for account details.
- **INQACCCUZ.cpy**: Contains the data structure for inquiry results.

## 2. Data Structures and Field Map

### 2.1 Data Structures
#### 2.1.1 ACCOUNT Table Structure (from ACCDB2.cpy)
| Field Name                  | Type          | Length |
|-----------------------------|---------------|--------|
| ACCOUNT_EYECATCHER          | CHAR          | 4      |
| ACCOUNT_CUSTOMER_NUMBER     | CHAR          | 10     |
| ACCOUNT_SORTCODE            | CHAR          | 6      |
| ACCOUNT_NUMBER              | CHAR          | 8      |
| ACCOUNT_TYPE                | CHAR          | 8      |
| ACCOUNT_INTEREST_RATE       | DECIMAL       | 4,2    |
| ACCOUNT_OPENED              | DATE          | -      |
| ACCOUNT_OVERDRAFT_LIMIT     | INTEGER       | -      |
| ACCOUNT_LAST_STATEMENT      | DATE          | -      |
| ACCOUNT_NEXT_STATEMENT      | DATE          | -      |
| ACCOUNT_AVAILABLE_BALANCE    | DECIMAL      | 10,2   |
| ACCOUNT_ACTUAL_BALANCE      | DECIMAL       | 10,2   |

#### 2.1.2 ACCOUNT-DATA Structure (from ACCOUNT.cpy)
| Field Name                  | Type          | Length |
|-----------------------------|---------------|--------|
| ACCOUNT-EYE-CATCHER         | PIC X         | 4      |
| ACCOUNT-CUST-NO             | PIC 9         | 10     |
| ACCOUNT-KEY                 | -             | -      |
| ACCOUNT-SORT-CODE           | PIC 9         | 6      |
| ACCOUNT-NUMBER              | PIC 9         | 8      |
| ACCOUNT-TYPE                | PIC X         | 8      |
| ACCOUNT-INTEREST-RATE       | PIC 9(4)V99   | -      |
| ACCOUNT-OPENED              | PIC 9         | 8      |
| ACCOUNT-OVERDRAFT-LIMIT     | PIC 9         | 8      |
| ACCOUNT-LAST-STMT-DATE      | PIC 9         | 8      |
| ACCOUNT-NEXT-STMT-DATE      | PIC 9         | 8      |
| ACCOUNT-AVAILABLE-BALANCE    | PIC S9(10)V99 | -      |
| ACCOUNT-ACTUAL-BALANCE      | PIC S9(10)V99 | -      |

#### 2.1.3 INQACCCUZ Structure (from INQACCCUZ.cpy)
| Field Name                  | Type          | Length |
|-----------------------------|---------------|--------|
| NUMBER-OF-ACCOUNTS          | PIC S9        | 8      |
| CUSTOMER-NUMBER             | PIC 9         | 10     |
| COMM-SUCCESS                | PIC X         | 1      |
| COMM-FAIL-CODE              | PIC X         | 1      |
| CUSTOMER-FOUND              | PIC X         | 1      |
| COMM-PCB-POINTER            | PIC X         | 4      |
| ACCOUNT-DETAILS             | OCCURS 1 TO 20| -      |
| COMM-EYE                    | PIC X         | 4      |
| COMM-CUSTNO                 | PIC X         | 10     |
| COMM-SCODE                  | PIC X         | 6      |
| COMM-ACCNO                  | PIC 9         | 8      |
| COMM-ACC-TYPE               | PIC X         | 8      |
| COMM-INT-RATE               | PIC 9(4)V99   | -      |
| COMM-OPENED                 | PIC 9         | 8      |
| COMM-OVERDRAFT              | PIC 9         | 8      |
| COMM-LAST-STMT-DT           | PIC 9         | 8      |
| COMM-NEXT-STMT-DT           | PIC 9         | 8      |
| COMM-AVAIL-BAL              | PIC S9(10)V99 | -      |
| COMM-ACTUAL-BAL             | PIC S9(10)V99 | -      |

## 3. Business Process Flow

1. **Input**: Customer number is provided.
2. **Process**:
   - Check if the customer exists in the datastore.
   - If found, retrieve associated account records.
   - Populate the account details into the output structure.
3. **Output**: Return the number of accounts and their details.

## 4. Batch/Online Assumptions

- The program operates in an online transaction processing environment.
- It assumes synchronous communication with the datastore.
- The maximum number of accounts returned is capped at 20.

## 5. Risks and Unknowns

- **Data Integrity**: Potential discrepancies between legacy data and modernized data structures.
- **Performance**: The impact of translating synchronous CICS calls to RESTful API calls.
- **Behavioral Consistency**: Ensuring that the modernized application preserves the legacy behavior as specified.
- **Unknown Dependencies**: Other systems or processes that may interact with INQACCCU are not documented and could affect functionality.