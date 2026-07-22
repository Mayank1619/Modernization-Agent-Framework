# Copilot Implementation Prompt

Use generated artifacts to produce implementation code in iterative pull requests.

Inputs:
- requirements.md
- spec.md
- plan.md
- tasks.md
- openapi.yaml
- mapping-matrix.md

Guidance:
- Implement smallest vertical slice first
- Keep controllers thin
- Keep business logic in services
- Add tests for every business rule

## Implementation Details

### 1. Backend Service Implementation

**Task ID**: TASK-001  
**Description**: Implement the backend service to retrieve account records based on a customer number.  
**Dependencies**: None  
**Estimate**: M  
**Definition of Done**: The service retrieves account records correctly, returns a success flag, and handles errors as per business rules.  
**Linked Requirements**: FR-001, FR-002  
**Acceptance Criteria**: AC-001, AC-002  

**Implementation Steps**:
1. Create a Spring Boot service class `AccountService`.
2. Implement a method `retrieveAccountRecords(String customerNumber)` that:
   - Validates the customer number format.
   - Retrieves account records from the mock repository.
   - Returns a success flag and the list of accounts or an error message if not found.
3. Ensure that the method adheres to business rules BR-001 and BR-002.

### 2. RESTful API Endpoint

**Task ID**: TASK-003  
**Description**: Create RESTful API endpoint for retrieving account records.  
**Dependencies**: TASK-001  
**Estimate**: S  
**Definition of Done**: The endpoint is accessible and returns the expected results based on input.  
**Linked Requirements**: FR-001  
**Acceptance Criteria**: AC-001, AC-002  

**Implementation Steps**:
1. Define a controller class `AccountController`.
2. Create a GET endpoint `/api/accounts` that:
   - Accepts `customerNumber` as a query parameter.
   - Calls `AccountService.retrieveAccountRecords()`.
   - Returns a JSON response with the success flag and account records or error message.

### 3. Frontend Component Development

**Task ID**: TASK-002  
**Description**: Develop the frontend component to input customer numbers and display account records.  
**Dependencies**: TASK-001  
**Estimate**: M  
**Definition of Done**: The component allows user input, displays results, and handles error messages appropriately.  
**Linked Requirements**: FR-001  
**Acceptance Criteria**: AC-001, AC-002  

**Implementation Steps**:
1. Create a React component `AccountInquiry`.
2. Implement input handling for customer number.
3. Call the API endpoint on form submission.
4. Display the results or error messages based on the API response.

### 4. Testing Implementation

**Test Cases Overview**:
- **TC-001**: Verify retrieval of account records for a valid customer number.
- **TC-002**: Verify success flag returned when customer is found.
- **TC-003**: Validate format of the customer number.
- **TC-004**: Ensure data sanitization before response.
- **TC-005**: Test retrieval failure for an invalid customer number.

**Implementation Steps**:
1. Create unit tests for `AccountService` to cover all business rules.
2. Create integration tests for `AccountController` to validate API responses.
3. Ensure all tests are automated and run in the CI/CD pipeline.

### 5. Security and Compliance

- Implement OAuth2 authentication for the API.
- Ensure all endpoints validate input strictly and sanitize output to prevent injection attacks.
- Log all requests with correlation IDs for tracing.

### 6. Documentation

- Update OpenAPI specification to reflect the new endpoint and its parameters.
- Document the service and controller classes with appropriate comments and usage examples.

### 7. Deployment

- Follow the delivery plan to deploy the application through the defined environments (development, testing, UAT).
- Ensure that legacy behavior is preserved and enhancements are toggleable as per the delivery constraints.

By following these steps, the implementation will align with the modernization objectives while adhering to the specified requirements and business rules.