# Test Spec Prompt

## Test Specification for Business Rules and API Verification

### Unit Tests

#### Test Case 1: Verify Active Account Status
- **Test ID**: TC-001
- **Rule Mapped**: BR-001
- **Input**: WS-ACCOUNT-STATUS = "A"
- **Expected Output**: "ACCOUNT IS ACTIVE"
- **Description**: Test that an account with status "A" is recognized as active.

#### Test Case 2: Verify Inactive Account Status
- **Test ID**: TC-002
- **Rule Mapped**: BR-001
- **Input**: WS-ACCOUNT-STATUS = "I"
- **Expected Output**: "ACCOUNT NOT ACTIVE"
- **Description**: Test that an account with status "I" is recognized as not active.

#### Test Case 3: Validate Account ID Presence
- **Test ID**: TC-003
- **Rule Mapped**: BR-002
- **Input**: ACCOUNT-ID = null
- **Expected Output**: Error indicating invalid account ID
- **Description**: Test that an error is raised when the account ID is null.

#### Test Case 4: Validate Account ID Format
- **Test ID**: TC-004
- **Rule Mapped**: BR-002
- **Input**: ACCOUNT-ID = "123-ABC"
- **Expected Output**: Validity confirmation
- **Description**: Test that a correctly formatted account ID is validated successfully.

### Integration Tests

#### Test Case 5: Account Retrieval Service Integration
- **Test ID**: TC-005
- **Rule Mapped**: BR-003
- **Input**: ACCOUNT-ID = "12345"
- **Expected Output**: Account record retrieved from DB2
- **Description**: Test the integration of the account retrieval service with the DB2 datastore.

### Contract Tests

#### Test Case 6: API Contract for Account Status Check
- **Test ID**: TC-006
- **Endpoint**: /api/account/status
- **Input**: WS-ACCOUNT-STATUS = "A"
- **Expected Output**: 200 OK with body {"status": "ACCOUNT IS ACTIVE"}
- **Description**: Validate that the API contract for checking account status adheres to the expected response format.

### Negative and Boundary Scenarios

#### Test Case 7: Invalid Account ID Format
- **Test ID**: TC-007
- **Rule Mapped**: BR-002
- **Input**: ACCOUNT-ID = "invalid-id"
- **Expected Output**: Error indicating invalid account ID format
- **Description**: Test that an error is raised for an incorrectly formatted account ID.

#### Test Case 8: Empty Account ID
- **Test ID**: TC-008
- **Rule Mapped**: BR-002
- **Input**: ACCOUNT-ID = ""
- **Expected Output**: Error indicating account ID cannot be empty
- **Description**: Test that an error is raised when the account ID is empty.

### Rule-to-Test Mapping

| Rule Identifier | Test ID | Test Description                             |
|-----------------|---------|----------------------------------------------|
| BR-001          | TC-001  | Verify Active Account Status                 |
| BR-001          | TC-002  | Verify Inactive Account Status               |
| BR-002          | TC-003  | Validate Account ID Presence                 |
| BR-002          | TC-004  | Validate Account ID Format                   |
| BR-003          | TC-005  | Account Retrieval Service Integration        |
| -               | TC-006  | API Contract for Account Status Check       |
| BR-002          | TC-007  | Invalid Account ID Format                    |
| BR-002          | TC-008  | Empty Account ID                             |