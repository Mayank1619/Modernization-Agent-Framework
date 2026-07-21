# Intended System Blueprint

## 1. Feature and modernization objective
Modernize INQACCCU Customer ↔ Account Relationships Inquiry into a web-accessible application with a Spring Boot backend and React frontend while preserving legacy observable behavior.

## 2. Target product scope
The product will provide a web interface for users to inquire about customer-account relationships, allowing retrieval of account records based on customer numbers.

## 3. Architecture blueprint
The architecture will consist of a microservices-based backend using Spring Boot, serving a React frontend. The system will utilize RESTful APIs for communication, with a mock repository for persistence during the proof of concept (POC) phase.

## 4. Technology stack and versions
- **Backend**: Java 21, Spring Boot 3.3.x, Maven 3.9+
- **Frontend**: React 18.x, TypeScript 5.x, Vite 5.x, Node.js 20 LTS
- **API**: REST over HTTPS, OpenAPI 3.0.3
- **Persistence for POC**: Mock repository (no live CICS or DB2 connectivity)

## 5. Security and compliance baseline
- **Authentication**: OAuth2 resource server with JWT bearer tokens
- **Authorization**: Role-based access control for customer-account relationship inquiry endpoints
- **Transport Security**: TLS 1.2+
- **Input Validation**: Strict path/query validation and standardized error responses
- **Secrets Handling**: Environment variables or secret manager, never in source control

## 6. API and integration constraints
- The system must preserve legacy observable behavior unless explicitly marked as modernization enhancement.
- All API endpoints must adhere to the OpenAPI 3.0.3 specification.
- The system will not connect to real mainframe systems in POC mode.

## 7. Data and mapping constraints
- Data structures must align with legacy formats as defined in the COBOL copybooks.
- The system must ensure that all data returned to the client is sanitized to prevent injection attacks.

## 8. Observability and operational requirements
- **Logging**: Structured JSON logs with correlation ID per request
- **Metrics**: Request latency, error rate, downstream adapter status
- **Tracing**: Distributed tracing ready (OpenTelemetry)

## 9. Delivery constraints and environments
- Preserve legacy behavior as the default path.
- Any enhancement must be explicitly marked and toggleable.
- Controllers must remain thin, with business logic encapsulated in services.

## 10. Out of scope
- Direct integration with live CICS or DB2 systems during the POC phase.
- Any enhancements that alter the fundamental behavior of the legacy system without explicit approval.

## 11. Assumptions and open questions
- **ASM-001**: The legacy system's observable behavior is well understood and documented.
- **ASM-002**: Users will have access to the web application through standard web browsers.
- **Q-001**: What are the performance implications of translating synchronous CICS calls to RESTful API calls?
- **Q-002**: Are there any unknown dependencies on other systems that may affect functionality?