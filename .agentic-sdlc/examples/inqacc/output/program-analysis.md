# Program Analysis

## Program Inventory
- **Program Name**: INQACC
- **Description**: This program takes an incoming account number, accesses the DB2 datastore, and retrieves the associated account record matching on the account number and account type. If there are any issues, the program will abend.

## Data Structures and Field Map
### Account Table (from ACCDB2.cpy)
| Field Name                     | Data Type   | Length | Constraints       |
|--------------------------------|-------------|--------|--------------------|
| ACCOUNT_EYECATCHER            | CHAR        | 4      |                    |
| ACCOUNT_CUSTOMER_NUMBER        | CHAR        | 10     |                    |
| ACCOUNT_SORTCODE               | CHAR        | 6      | NOT NULL           |
| ACCOUNT_NUMBER                 | CHAR        | 8      | NOT NULL           |
| ACCOUNT_TYPE                   | CHAR        | 8      |                    |

### Account Data Structure (from ACCOUNT.cpy)
| Field Name                     | Data Type   | Length | Constraints       |
|--------------------------------|-------------|--------|--------------------|
| ACCOUNT-EYE-CATCHER           | PIC X       | 4      |                    |
| ACCOUNT-CUST-NO               | PIC 9       | 10     |                    |
| ACCOUNT-SORT-CODE             | PIC 9       | 6      |                    |
| ACCOUNT-NUMBER                | PIC 9       | 8      |                    |

### Inquiry Account Control Structure (from INQACCCZ.cpy)
| Field Name                     | Data Type   | Length | Constraints       |
|--------------------------------|-------------|--------|--------------------|
| NUMBER-OF-ACCOUNTS             | PIC S9      | 8      | BINARY             |
| CUSTOMER-NUMBER                | PIC 9       | 10     |                    |
| COMM-SUCCESS                   | PIC X       | 1      |                    |
| COMM-FAIL-CODE                 | PIC X       | 1      |                    |
| CUSTOMER-FOUND                 | PIC X       | 1      |                    |
| COMM-PCB-POINTER               | PIC X       | 4      |                    |
| ACCOUNT-DETAILS                | OCCURS 1 TO 20 |        |                    |

## Business Process Flow
1. Receive incoming account number.
2. Validate account number format.
3. Access DB2 datastore to retrieve account record.
4. Check if account exists and is active.
5. Return account details or error message if not found.

## Batch/Online Assumptions
- The program is assumed to be executed in an online transaction processing environment due to the CICS directive.
- It is assumed that the DB2 datastore is always accessible during execution.

## Risks and Unknowns
- Potential for program abend if the DB2 datastore is not reachable.
- Unknowns regarding the handling of invalid account numbers and their impact on user experience.
- Risks associated with data integrity if the account number format is not strictly validated before processing.