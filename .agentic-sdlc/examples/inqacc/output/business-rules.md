# Business Rules

## Rule 1
- **Rule Identifier**: BR-001
- **Rule Statement**: An account is considered active if its status is "A".
- **Trigger Conditions**: When the account status is checked.
- **Inputs**: WS-ACCOUNT-STATUS
- **Outputs**: "ACCOUNT IS ACTIVE" or "ACCOUNT NOT ACTIVE"
- **Error Conditions**: None specified.

## Rule 2
- **Rule Identifier**: BR-002
- **Rule Statement**: An account record must contain a valid account ID.
- **Trigger Conditions**: When an account record is created or updated.
- **Inputs**: ACCOUNT-ID
- **Outputs**: Validity confirmation
- **Error Conditions**: If ACCOUNT-ID is null or does not meet format requirements.

## Rule 3
- **Rule Identifier**: BR-003
- **Rule Statement**: The program retrieves an account record from the DB2 datastore based on the incoming account number and account type.
- **Trigger Conditions**: When an account number is provided for inquiry.
- **Inputs**: ACCOUNT-NUMBER, ACCOUNT-TYPE
- **Outputs**: ACCOUNT-RECORD
- **Error Conditions**: If the account number does not exist or if there is a database access error.

## Rule 4
- **Rule Identifier**: BR-004
- **Rule Statement**: The program must handle abend conditions gracefully.
- **Trigger Conditions**: When an error occurs during account retrieval.
- **Inputs**: Error codes from database operations
- **Outputs**: Error handling response
- **Error Conditions**: Any database access failure or invalid input parameters.