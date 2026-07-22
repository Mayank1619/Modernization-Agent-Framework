# plan.md

**Document ID:** `plan-inqacccu-modernization-001`  
**Pipeline:** `mainframe_modernization`  
**Target Output File:** `plan.md`  
**Purpose:** Phased delivery and modernization roadmap for INQACCCU CICS-to-REST transformation  
**Last Updated:** 2025

---

## Executive Summary

This plan delivers a phased modernization of the legacy INQACCCU COBOL CICS program into a cloud-native Spring Boot 3.3.x REST API backend paired with a React 18.x frontend. The delivery preserves all legacy observable behavior while establishing a foundation for future enhancements through feature toggles and clear separation of concerns. Delivery spans four phases: Foundation (Weeks 1–4), Integration & Security (Weeks 5–8), UAT & Hardening (Weeks 9–12), and Production Go-Live (Weeks 13–14).

---

## 1. Phase Overview and Timeline

### Phase 1: Foundation & API Contract Freeze
**Duration:** Weeks 1–4  
**Status:** Precondition for Phase 2  
**Goal:** Establish Spring Boot scaffold, API contract, and mock repository layer. Freeze OpenAPI 3.0.3 contract and obtain stakeholder sign-off.

#### Phase 1 Milestones

| Milestone ID | Milestone | Target Week | Owner | Gate Criteria |
|---|---|---|---|---|
| M1.1 | Project Setup & Environment Config | 1 | DevOps Lead | Maven 3.9+ repo configured; Node.js 20 LTS CI agents provisioned |
| M1.2 | API Contract Definition & Spec Freeze | 2 | API Architect | OpenAPI 3.0.3 document signed off; request/response schemas finalized |
| M1.3 | Spring Boot Scaffold & OAuth2 Configuration | 2 | Backend Lead | Spring Boot 3.3.x skeleton with security filter chain; JWT validator configured |
| M1.4 | Mock Repository Layer & DTO Mapping | 3 | Backend Developer | CustomerAccountRepository mock implementation; COBOL-to-Java DTO mapping complete |
| M1.5 | Business Logic Service Implementation (Legacy Path) | 3 | Backend Developer | CustomerAccountService preserving all BR001–BR004 logic; feature toggle framework in place |
| M1.6 | REST Controller & Endpoint Implementation | 3 | Backend Developer | `GET /api/v1/customers/{customerId}/accounts` fully functional; Happy path + error responses tested |
| M1.7 | React Scaffold & Component Design | 2 | Frontend Lead | Vite 5.x project; TypeScript 5.x configured; component hierarchy finalized |
| M1.8 | Frontend API Integration & Mock Service | 3 | Frontend Developer | Axios client configured; mock API service for offline dev |
| M1.9 | API Contract Freeze Sign-Off | 4 | Product Owner, API Architect | No further breaking changes to endpoint signatures or error response structure |

#### Phase 1 Deliverables

- **backend/** Spring Boot application source (Maven structure)
  - `src/main/java/com/company/inqacccu/controller/CustomerAccountController.java`
  - `src/main/java/com/company/inqacccu/service/CustomerAccountService.java`
  - `src/main/java/com/company/inqacccu/repository/CustomerAccountRepository.java` (mock)
  - `src/main/java/com/company/inqacccu/dto/` (request/response DTOs)
  - `src/main/resources/application-dev.yml` (OAuth2, logging, observability config)
  - `pom.xml` (Spring Boot 3.3.x BOM, security starter, actuator)
- **frontend/** React application source (Vite structure)
  - `src/components/CustomerInquiry.tsx`
  - `src/services/customerAccountApi.ts`
  - `src/auth/authContext.tsx` (OAuth2 token management)
  - `vite.config.ts`, `tsconfig.json`
- **docs/**
  - `openapi-3.0.3.yaml` (API contract, FROZEN)
  - `API-INTEGRATION-GUIDE.md` (endpoint specs, auth, error handling)
  - `ARCHITECTURE.md` (component diagram, data flow)

#### Phase 1 Dependencies

- Java 21 JDK, Maven 3.9+ available on CI agents
- Node.js 20 LTS available on CI agents
- OAuth2 Authorization Server (external) provisioned and reachable from DEV environment
- Git repository with branch protection on `main`
- Definition of "legacy behavior" documented and agreed (BR001–BR004)

#### Phase 1 Risks & Mitigations

| Risk ID | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| R1.1 | API contract instability; stakeholders request mid-phase changes | Medium | High | Enforce strict change control; require written sign-off on OpenAPI doc before Phase 2 start |
| R1.2 | OAuth2 Authorization Server not ready or unreachable from DEV | High | High | Pre-provision mock OAuth2 token validator (in-memory JwtDecoder); document fallback auth mode for local dev |
| R1.3 | Mismatch between COBOL field precision (PIC clauses) and Java types | Medium | Medium | Create explicit DTO mapping test cases matching each COBOL copybook field; use Hamcrest matchers to validate precision loss |
| R1.4 | Frontend framework decision delayed; React 18.x toolchain not stabilized | Low | Medium | Confirm React 18.x + Vite 5.x stack in Week 1; lock dependency versions in package-lock.json |

---

### Phase 2: Integration, Security Hardening & Test Strategy Approval
**Duration:** Weeks 5–8  
**Dependency:** API Contract Freeze (M1.9) complete  
**Goal:** Implement comprehensive security controls, structured observability, and complete automated test coverage. Freeze test strategy and obtain QA sign-off.

#### Phase 2 Milestones

| Milestone ID | Milestone | Target Week | Owner | Gate Criteria |
|---|---|---|---|---|
| M2.1 | Security Hardening: Input Validation & Sanitization | 5 | Security Architect | All RFC 3986 path/query validation rules implemented; OWASP Top 10 checks in place |
| M2.2 | OAuth2 Resource Server: JWT Validation & RBAC | 5 | Backend Lead | JWT signature validation via Authorization Server public key; role extraction and @PreAuthorize decorators |
| M2.3 | Secrets Management: Environment Variables & Configuration | 5 | DevOps Lead | All secrets (OAuth2 client secret, DB2 adapter creds) externalized; documented in deployment runbook |
| M2.4 | Structured JSON Logging & Correlation ID Propagation | 6 | Backend Developer | SLF4J + Logback configured; correlation ID injected into MDC; sample log output validated |
| M2.5 | OpenTelemetry Instrumentation: Tracing Ready | 6 | Backend Developer | `spring-boot-starter-actuator` + OpenTelemetry instrumentation library; exporter configured (Jaeger/Datadog agent URL set via env var) |
| M2.6 | Metrics & Health Checks: Prometheus Format | 6 | Backend Developer | Micrometer metrics exported; custom business metrics (customer_found_rate, account_query_latency_ms); `/actuator/health` endpoint operational |
| M2.7 | Unit Test Suite: 80%+ Code Coverage | 7 | QA Lead, Backend Developer | CustomerAccountService, repository, and controller unit tests; mock OAuth2 context for auth tests |
| M2.8 | Integration Test Suite: End-to-End API Validation | 7 | QA Lead | Mock OAuth2 token generation; full Happy Path + Error Scenario tests; response payload validation against OpenAPI schema |
| M2.9 | Frontend Unit & Integration Tests: React Components | 7 | QA Lead, Frontend Developer | Jest/React Testing Library; auth context mocking; API mock service tests |
| M2.10 | Test Strategy Freeze & QA Sign-Off | 8 | QA Lead, Product Owner | Automated test plan documented; test environment provisioning checklist signed; no manual testing rework expected in later phases |

#### Phase 2 Deliverables

- **backend/**
  - `src/main/java/com/company/inqacccu/config/SecurityConfig.java` (OAuth2 resource server, JWT validation)
  - `src/main/java/com/company/inqacccu/config/ObservabilityConfig.java` (logging, tracing, metrics)
  - `src/test/java/com/company/inqacccu/service/CustomerAccountServiceTest.java` (unit tests)
  - `src/test/java/com/company/inqacccu/controller/CustomerAccountControllerIntegrationTest.java` (integration tests)
  - `application-test.yml` (test-specific OAuth2 mock, h2 in-memory DB for mock repo)
  - Updated `pom.xml` (spring-cloud-starter-config, spring-cloud-starter-bootstrap, micrometer-registry-prometheus)
- **frontend/**
  - `src/__tests__/CustomerInquiry.test.tsx`
  - `src/__tests__/authContext.test.tsx`
  - Updated `package.json` (jest, @testing-library/react)
- **docs/**
  - `TEST-STRATEGY.md` (test types, coverage goals, defect management)
  - `SECURITY-HARDENING-CHECKLIST.md` (OWASP validation, secrets handling, OAuth2 configuration)
  - `DEPLOYMENT-RUNBOOK.md` (environment variable reference, secret initialization, health check validation)

#### Phase 2 Dependencies

- Phase 1 API Contract Freeze complete and signed
- Spring Cloud Config Server or HashiCorp Vault integration ready (for secrets)
- OAuth2 Authorization Server stable and documented
- QA environment provisioned with mock OAuth2 token generator
- CI/CD pipeline (Jenkins, GitLab CI, GitHub Actions) configured for automated test execution

#### Phase 2 Risks & Mitigations

| Risk ID | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| R2.1 | OAuth2 Authorization Server integration delays; JWT public key endpoint unstable | Medium | High | Implement local JWT mock token generator in test profile; document fallback token validation for development |
| R2.2 | Observability instrumentation causes performance regression (tracing overhead) | Medium | Medium | Profile latency impact; if >50ms p99 increase, disable high-cardinality tracing attributes and re-evaluate |
| R2.3 | Test suite execution time grows >15 minutes; blocks CI/CD pipeline | Low | Medium | Parallelize test execution (Maven Surefire parallel mode); separate unit from integration tests by profile |
| R2.4 | Secrets manager integration fails in local dev environment | Low | Medium | Provide default secrets file (git-ignored) for local development; document setup in DEV-ENVIRONMENT.md |

---

### Phase 3: User Acceptance Testing (UAT) & Hardening
**Duration:** Weeks 9–12  
**Dependency:** Test Strategy Freeze (M2.10) complete; DEV environment stable  
**Goal:** Deploy to UAT; execute legacy parity validation and UAT regression suite. Harden based on UAT findings. Obtain stakeholder sign-off on functional and non-functional requirements.

#### Phase 3 Milestones

| Milestone ID | Milestone | Target Week | Owner | Gate Criteria |
|---|---|---|---|---|
| M3.1 | UAT Environment Provisioning | 9 | DevOps Lead | Kubernetes cluster (or VM) with Spring Boot app, React frontend, mock repository; DNS resolved; TLS 1.2+ configured |
| M3.2 | Legacy Parity Test Execution | 9–10 | QA Lead, BA | Execute 50+ legacy INQACCCU test cases (customer found/not found, 0–20 accounts, account details precision); compare REST JSON response to original CICS output |
| M3.3 | Frontend UAT Regression Suite | 10 | QA Lead | Execute React component regression tests; browser compatibility check (Chrome, Firefox, Safari); responsive design validation |
| M3.4 | Performance & Load Testing | 10 | Performance Engineer | Load test: 100 concurrent users, 10,000 req/min; validate p99 latency <500ms; error rate <0.1%; heap usage stable |
| M3.5 | Security Penetration Testing & Compliance Review | 11 | Security Architect | Penetration test OAuth2 boundary; validate OWASP Top 10 mitigations; audit secrets handling; produce compliance report |
| M3.6 | Observability Validation in UAT | 11 | DevOps Lead | Confirm structured logs appear in aggregation tool; correlation IDs trace end-to-end; metrics scrape without errors |
| M3.7 | Defect Triage & Root Cause Analysis | 11 | QA Lead, Dev Team | All UAT defects logged; P0/P1 defects resolved; P2 defects triaged for post-launch; P3 deferred or documented as known issues |
| M3.8 | Stakeholder Sign-Off: Functional & NFR Compliance | 12 | Product Owner, Ops Lead | Formal sign-off document: legacy behavior validated, security controls confirmed, performance acceptable, observability operational |

#### Phase 3 Deliverables

- **UAT Artifacts**
  - `UAT-TEST-RESULTS.md` (legacy parity matrix, pass/fail by test case)
  - `LOAD-TEST-REPORT.pdf` (latency distributions, error rates, resource utilization)
  - `SECURITY-ASSESSMENT-REPORT.pdf` (penetration findings, remediation status)
  - `COMPLIANCE-CHECKLIST.md` (OWASP, TLS 1.2+, secrets, audit log format)
- **Hardening Fixes** (commits to `main` branch)
  - Bug fixes for any P0/P1 defects
  - Performance optimization patches (if needed)
  - Security remediation patches (if needed)
- **Updated Documentation**
  - `PRODUCTION-READINESS-CHECKLIST.md` (post-UAT sign-off)
  - `KNOWN-ISSUES.md` (P3 defects, deferred enhancements)

#### Phase 3 Dependencies

- DEV environment stable and all automated tests passing
- UAT environment identical to PROD (same OS, Java version, Spring Boot version, Node.js version)
- Legacy INQACCCU reference system accessible for comparison testing (or documented test case outputs archived)
- Load testing tool (JMeter, Gatling) configured for UAT environment
- Penetration testing engagement scoped and resourced

#### Phase 3 Risks & Mitigations

| Risk ID | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| R3.1 | Legacy reference system unavailable; parity validation blocked | Medium | High | Archive known-good CICS transaction outputs in test case fixtures; use as golden reference instead of live system |
| R3.2 | UAT environment not identical to PROD; findings don't translate | Low | High | Use Infrastructure-as-Code (Terraform/CloudFormation) to ensure DEV/UAT/PROD are built from same template; document any deviations |
| R3.3 | Performance targets not met; p99 latency >500ms due to mock repository or auth overhead | Medium | High | Profile bottlenecks; optimize JWT validation caching; consider read-through cache for customer queries; document performance limits in runbook |
| R3.4 | Security vulnerabilities found late; require major rework | Low | Critical | Conduct threat modeling in Phase 1; leverage OWASP security scanning tools (Snyk, OWASP ZAP) in CI/CD from Phase 2 onwards |

---

### Phase 4: Production Go-Live & Monitoring
**Duration:** Weeks 13–14  
**Dependency:** Stakeholder Sign-Off (M3.8) complete; all P0/P1 defects resolved  
**Goal:** Deploy to Production; execute cutover plan; monitor stability for 48 hours; establish incident response procedures.

#### Phase 4 Milestones

| Milestone ID | Milestone | Target Week | Owner | Gate Criteria |
|---|---|---|---|---|
| M4.1 | Production Environment Provisioning | 13 | DevOps Lead | HA/LB configured; TLS 1.2+ and certificate chain validated; secrets injected; health checks pass |