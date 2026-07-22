# test-spec.md

**Document ID:** `test-spec-inqacccu-001`  
**Pipeline:** `mainframe_modernization`  
**Target Output File:** `test-spec.md`  
**Version:** 1.0  
**Status:** Implementation-Ready  
**Last Updated:** 2025  

---

## 1. Test Specification Overview

### 1.1 Purpose and Scope

This document defines comprehensive test specifications for the INQACCCU modernization initiative. Tests verify:
- **Functional Requirements (FR):** Customer account inquiry API behavior, legacy parity, and enhancement toggles
- **Business Rules (BR):** Customer acceptance, account retrieval, validation strictness, status preservation, and secret handling
- **Non-Functional Requirements (NFR):** Security, observability, performance, and error handling
- **Negative & Boundary Scenarios:** Invalid inputs, missing records, authorization failures, timeouts
- **Legacy Parity & Modernization:** Preserve observable behavior while enabling future enhancements

### 1.2 Test Levels

| Test Level | Scope | Tools/Framework | Responsibility |
|---|---|---|---|
| **Unit Tests** | Single class/method; business logic; DTOs | JUnit 5, Mockito, AssertJ | Backend Development Team |
| **Integration Tests** | Spring context; controller+service+repository | Spring Boot Test, TestContainers | Backend Development Team |
| **Contract Tests** | API request/response payloads; backward compatibility | Spring Cloud Contract, Pact | API Lead |
| **Security Tests** | OAuth2 token validation; role-based access; input sanitization | Spring Security Test, OWASP ZAP | Security Team |
| **Performance Tests** | Response latency; throughput; resource usage | JMH, Gatling | Performance Engineer |
| **E2E Tests** | Full API flow through React frontend; user scenarios | Cypress, Selenium | QA Team |

---

## 2. Unit Tests

### 2.1 CustomerAccountsService Unit Tests

#### TC-101: Customer Found with Multiple Accounts

**ID:** `TC-101`  
**Requirement Mapping:** `FR-001`, `BR001`, `BR002`  
**Test Type:** Unit  
**Test Class:** `CustomerAccountsServiceTest`  

**Setup:**
```java
@Mock
private CustomerRepository customerRepository;

@Mock
private AccountRepository accountRepository;

@InjectMocks
private CustomerAccountsService service;

@BeforeEach
void setUp() {
    MockitoAnnotations.openMocks(this);
}
```

**Precondition:**
- Mock customer repository returns customer ID "0123456789" with `customerFound = true`
- Mock account repository returns 2 accounts with full details

**Test Steps:**
1. Call `service.inquireCustomerAccounts("0123456789")`
2. Verify returned `CustomerAccountsResponse` has:
   - `customerId = "0123456789"`
   - `customerFound = true`
   - `numberOfAccounts = 2`
   - `accounts[0].accountNumber = "12345678"` (eyeCatcher "ACCT")
   - `accounts[1].balance = 5000.50`

**Expected Result:**
- Service returns populated response matching legacy COBOL output structure
- No exceptions thrown

**Assertion Code:**
```java
@Test
void testInquireCustomerAccounts_Found() {
    // Arrange
    String customerId = "0123456789";
    Customer mockCustomer = Customer.builder()
        .customerId(customerId)
        .customerFound(true)
        .build();
    when(customerRepository.findById(customerId))
        .thenReturn(Optional.of(mockCustomer));
    
    List<Account> mockAccounts = Arrays.asList(
        Account.builder()
            .eyeCatcher("ACCT")
            .accountNumber("12345678")
            .sortCode("123456")
            .balance(new BigDecimal("1000.00"))
            .interestRate(new BigDecimal("2.5"))
            .statementDate("2025-01-31")
            .build(),
        Account.builder()
            .eyeCatcher("ACCT")
            .accountNumber("87654321")
            .sortCode("654321")
            .balance(new BigDecimal("5000.50"))
            .interestRate(new BigDecimal("3.0"))
            .statementDate("2025-01-31")
            .build()
    );
    when(accountRepository.findByCustomerId(customerId))
        .thenReturn(mockAccounts);

    // Act
    CustomerAccountsResponse response = service.inquireCustomerAccounts(customerId);

    // Assert
    assertThat(response)
        .isNotNull()
        .extracting("customerId", "customerFound", "numberOfAccounts")
        .containsExactly(customerId, true, 2);
    assertThat(response.getAccounts())
        .hasSize(2)
        .extracting("accountNumber")
        .containsExactly("12345678", "87654321");
    verify(customerRepository).findById(customerId);
    verify(accountRepository).findByCustomerId(customerId);
}
```

**Pass Criteria:**
- All assertions pass; no exceptions
- Mock interactions verified

---

#### TC-102: Customer Not Found

**ID:** `TC-102`  
**Requirement Mapping:** `FR-001`, `BR001`, `BR003`  
**Test Type:** Unit  

**Setup:** Same as TC-101

**Precondition:**
- Mock customer repository returns empty `Optional` for customer ID "9999999999"

**Test Steps:**
1. Call `service.inquireCustomerAccounts("9999999999")`
2. Verify returned `CustomerAccountsResponse` has:
   - `customerId = "9999999999"`
   - `customerFound = false`
   - `numberOfAccounts = 0`
   - `accounts` is empty list

**Assertion Code:**
```java
@Test
void testInquireCustomerAccounts_NotFound() {
    // Arrange
    String customerId = "9999999999";
    when(customerRepository.findById(customerId))
        .thenReturn(Optional.empty());

    // Act
    CustomerAccountsResponse response = service.inquireCustomerAccounts(customerId);

    // Assert
    assertThat(response)
        .isNotNull()
        .extracting("customerId", "customerFound", "numberOfAccounts")
        .containsExactly(customerId, false, 0);
    assertThat(response.getAccounts())
        .isEmpty();
    verify(accountRepository, never()).findByCustomerId(customerId);
}
```

**Pass Criteria:**
- Response indicates customer not found; account repository never called

---

#### TC-103: Maximum Account Count Boundary (20 Accounts)

**ID:** `TC-103`  
**Requirement Mapping:** `FR-001`, `BR002`, `NFR-002`  
**Test Type:** Unit (Boundary)  

**Setup:** Same as TC-101

**Precondition:**
- Mock customer repository returns customer found
- Mock account repository returns exactly 20 accounts

**Test Steps:**
1. Call `service.inquireCustomerAccounts(customerId)`
2. Verify `numberOfAccounts = 20`
3. Verify all 20 accounts returned in `accounts` array

**Assertion Code:**
```java
@Test
void testInquireCustomerAccounts_MaximumAccounts() {
    // Arrange
    String customerId = "0123456789";
    Customer mockCustomer = Customer.builder()
        .customerId(customerId)
        .customerFound(true)
        .build();
    when(customerRepository.findById(customerId))
        .thenReturn(Optional.of(mockCustomer));
    
    List<Account> mockAccounts = IntStream.range(0, 20)
        .mapToObj(i -> Account.builder()
            .eyeCatcher("ACCT")
            .accountNumber(String.format("%08d", i))
            .sortCode("000000")
            .balance(BigDecimal.valueOf(i * 1000))
            .interestRate(BigDecimal.valueOf(2.0))
            .statementDate("2025-01-31")
            .build())
        .collect(Collectors.toList());
    when(accountRepository.findByCustomerId(customerId))
        .thenReturn(mockAccounts);

    // Act
    CustomerAccountsResponse response = service.inquireCustomerAccounts(customerId);

    // Assert
    assertThat(response.getNumberOfAccounts()).isEqualTo(20);
    assertThat(response.getAccounts()).hasSize(20);
}
```

**Pass Criteria:**
- All 20 accounts returned; count accurate

---

#### TC-104: Customer ID Validation – Invalid Format

**ID:** `TC-104`  
**Requirement Mapping:** `FR-006`, `BR003`, `BR005`  
**Test Type:** Unit (Negative)  

**Setup:** Same as TC-101

**Precondition:**
- Customer ID is null, empty, or non-numeric

**Test Steps:**
1. Call `service.inquireCustomerAccounts(invalidId)` with:
   - `null`
   - `""`
   - `"123abc4567"` (non-numeric)
   - `"12345"` (too short)
2. Verify `InvalidCustomerIdException` is thrown

**Assertion Code:**
```java
@Test
void testInquireCustomerAccounts_InvalidFormat() {
    // Arrange & Act & Assert
    assertThatThrownBy(() -> service.inquireCustomerAccounts(null))
        .isInstanceOf(InvalidCustomerIdException.class)
        .hasMessage("Customer ID cannot be null");
    
    assertThatThrownBy(() -> service.inquireCustomerAccounts(""))
        .isInstanceOf(InvalidCustomerIdException.class)
        .hasMessage("Customer ID cannot be empty");
    
    assertThatThrownBy(() -> service.inquireCustomerAccounts("123abc4567"))
        .isInstanceOf(InvalidCustomerIdException.class)
        .hasMessage("Customer ID must be 10 digits");
    
    assertThatThrownBy(() -> service.inquireCustomerAccounts("12345"))
        .isInstanceOf(InvalidCustomerIdException.class)
        .hasMessage("Customer ID must be exactly 10 characters");
}
```

**Pass Criteria:**
- All invalid formats raise expected exception
- Exception message matches specification

---

### 2.2 CustomerAccountsController Unit Tests

#### TC-105: Controller Returns 200 OK with Valid JWT

**ID:** `TC-105`  
**Requirement Mapping:** `FR-007`, `FR-008`, `BR008`  
**Test Type:** Unit  
**Test Class:** `CustomerAccountsControllerTest`  

**Setup:**
```java
@WebMvcTest(CustomerAccountsController.class)
class CustomerAccountsControllerTest {
    @MockBean
    private CustomerAccountsService service;
    
    @Autowired
    private MockMvc mockMvc;
    
    @Autowired
    private JwtDecoder jwtDecoder;
}
```

**Precondition:**
- Controller is mocked with valid Spring Security context
- Valid JWT bearer token in Authorization header
- Service returns populated response

**Test Steps:**
1. Prepare valid JWT token with role `ROLE_CUSTOMER_INQUIRY`
2. Send `GET /api/v1/customers/0123456789/accounts` with Authorization header
3. Verify response status is 200 OK
4. Verify response body matches `CustomerAccountsResponse` DTO

**Assertion Code:**
```java
@Test
void testInquireAccounts_ValidJwt_ReturnsOk() throws Exception {
    // Arrange
    String customerId = "0123456789";
    String validToken = generateValidJwt("ROLE_CUSTOMER_INQUIRY");
    CustomerAccountsResponse mockResponse = CustomerAccountsResponse.builder()
        .customerId(customerId)
        .customerFound(true)
        .numberOfAccounts(2)
        .accounts(Arrays.asList(
            AccountDto.builder().accountNumber("12345678").balance(new BigDecimal("1000")).build(),
            AccountDto.builder().accountNumber("87654321").balance(new BigDecimal("5000")).build()
        ))
        .build();
    when(service.inquireCustomerAccounts(customerId))
        .thenReturn(mockResponse);

    // Act & Assert
    mockMvc.perform(get("/api/v1/customers/{customerId}/accounts", customerId)
            .header("Authorization", "Bearer " + validToken)
            .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.customerId").value(customerId))
        .andExpect(jsonPath("$.customerFound").value(true))
        .andExpect(jsonPath("$.numberOfAccounts").value(2))
        .andExpect(jsonPath("$.accounts", hasSize(2)));
}
```

**Pass Criteria:**
- HTTP 200 response; JSON payload matches expected structure

---

#### TC-106: Controller Returns 401 Unauthorized on Missing JWT

**ID:** `TC-106`  
**Requirement Mapping:** `FR-007`, `BR008`, `NFR-005`  
**Test Type:** Unit (Negative)  

**Setup:** Same as TC-105

**Precondition:**
- Authorization header is missing

**Test Steps:**
1. Send `GET /api/v1/customers/0123456789/accounts` without Authorization header
2. Verify response status is 401 Unauthorized
3. Verify `WWW-Authenticate` header is present

**Assertion Code:**
```java
@Test
void testInquireAccounts_NoJwt_Returns401() throws Exception {
    // Act & Assert
    mockMvc.perform(get("/api/v1/customers/0123456789/accounts")
            .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isUnauthorized())
        .andExpect(header().exists("WWW-Authenticate"));
}
```

**Pass Criteria:**
- HTTP 401 response; authentication challenge header present

---

#### TC-107: Controller Returns 403 Forbidden on Insufficient Role

**ID:** `TC-107`  
**Requirement Mapping:** `FR-007`, `BR009`, `NFR-005`  
**Test Type:** Unit (Negative)  

**Setup:** Same as TC-105

**Precondition:**
- Valid JWT token present but with role `ROLE_READONLY` (insufficient for inquiry)

**Test Steps:**
1. Prepare JWT with insufficient role
2. Send `GET /api/v1/customers/0123456789/accounts` with token
3. Verify response status is 403 Forbidden

**Assertion Code:**
```java
@Test
void testInquireAccounts_InsufficientRole_Returns403() throws Exception {
    // Arrange
    String invalidToken = generateValidJwt("ROLE_READONLY");

    // Act & Assert
    mockMvc.perform(get("/api/v1/customers/0123456789/accounts", "0123456789")
            .header("Authorization", "Bearer " + invalidToken)
            .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isForbidden());
}
```

**Pass Criteria:**
- HTTP 403 response; access denied

---

#### TC-108: Controller Returns 400 Bad Request on Invalid Customer ID

**ID:** `TC-108`  
**Requirement Mapping:** `FR-006`, `BR003`, `BR005`  
**Test Type:** Unit (Negative)  

**Setup:** Same as TC-105

**Precondition:**
- Valid JWT present
- Customer ID in path is invalid format (e.g., "abc1234567", "12345")

**Test Steps:**
1. Send `GET /api/v1/customers/abc1234567/accounts` with valid JWT
2. Verify response status is 400 Bad Request
3. Verify error message body contains validation details

**Assertion Code:**
```java
@Test
void testInquireAccounts_InvalidCustomerId_Returns400() throws Exception {
    // Arrange
    String validToken = generateValidJwt("ROLE_CUSTOMER_INQUIRY");

    // Act & Assert
    mockMvc.perform(get("/api/v1/customers/abc1234567/accounts")
            .header("Authorization", "Bearer " + validToken)
            .contentType(MediaType.APPLICATION_JSON