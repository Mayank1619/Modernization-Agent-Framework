# System Intent Blueprint

## Product goal

Modernize INQACCCU Customer ↔ Account Relationships Inquiry into a
web-accessible application with a Spring Boot backend and React frontend
while preserving legacy observable behavior.

## Target stack

-   Backend: Java 21, Spring Boot 3.3.x, Maven 3.9+
-   Frontend: React 18.x, TypeScript 5.x, Vite 5.x, Node.js 20 LTS
-   API: REST over HTTPS, OpenAPI 3.0.3
-   Persistence for POC: Mock repository (no live CICS or DB2
    connectivity)

## Security baseline

-   Authentication: OAuth2 resource server with JWT bearer tokens
-   Authorization: Role-based access control for customer-account
    relationship inquiry endpoints
-   Transport: TLS 1.2+
-   Input validation: strict path/query validation and standardized
    error responses
-   Secrets handling: environment variables or secret manager, never in
    source control

## Operational baseline

-   Logging: structured JSON logs with correlation ID per request
-   Metrics: request latency, error rate, downstream adapter status
-   Tracing: distributed tracing ready (OpenTelemetry)

## Delivery constraints

-   Preserve legacy behavior as default path
-   Any enhancement must be explicitly marked and toggleable
-   Controllers remain thin, business logic in services
-   Do not connect to real mainframe systems in POC mode
