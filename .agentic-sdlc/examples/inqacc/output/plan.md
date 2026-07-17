# INQACC Modernized Account Inquiry – Delivery Plan

**Document ID:** `plan.md`  
**Pipeline:** mainframe_modernization  
**Authority:** provided/system-intent.md + output/intended-system.md + output/business-rules.md + output/requirements.md + output/spec.md + output/program-analysis.md + output/mapping-matrix.md + output/tasks.md + output/test-spec.md + output/traceability-matrix.md + output/openapi.yaml  
**Status:** Implementation-ready phased delivery plan  
**Generated:** 2024  
**Plan Horizon:** 6 months (26 weeks) to production readiness  
**Target Stack:** Java 21 + Spring Boot 3.3.x | React 18.x + TypeScript 5.x + Vite 5.x | Mock Repository (POC)

---

## Executive Summary

This document defines a phased delivery plan to modernize the legacy INQACC CICS-DB2 account inquiry program into a cloud-ready Spring Boot 3.3.x REST API with React 18.x web UI. The plan preserves legacy observable behavior while enabling future mainframe integration. Delivery is structured in **4 phases** spanning **26 weeks**, with explicit environment progression (dev → test → UAT → prod) and compliance checkpoints for security, API contract stability, and operational readiness.

**Critical Success Factors:**
- API contract freeze by end of Phase 1 (week 4)
- Mock repository fully functional by end of Phase 2 (week 8)
- Complete legacy parity and E2E testing by end of Phase 3 (week 16)
- Production-ready artifact hardening in Phase 4 (weeks 17–26)
- Zero critical security findings before production promotion

---

## 1. Phasing Overview

| Phase | Name | Duration | Primary Objective | Key Deliverables |
|-------|------|----------|-------------------|------------------|
| **1** | Foundation & Contract Design | Weeks 1–4 | Establish API contract, security baseline, build toolchain | OpenAPI 3.0.3 spec (frozen), OAuth2 adapter, Maven/Node.js build pipeline, dev environment setup |
| **2** | Core Service & Persistence | Weeks 5–8 | Implement account inquiry service, mock repository, structured logging | Spring Boot service, AccountRepository, mock data, structured JSON logging, integration tests (75%+ coverage) |
| **3** | Legacy Parity & Frontend | Weeks 9–16 | React UI, field mapping validation, E2E testing, UAT preparation | React web app (TypeScript + Vite), complete field mapping tests, E2E test suite, UAT readiness documentation |
| **4** | Hardening, Deployment & Operationalization | Weeks 17–26 | Security hardening, containerization, observability, production readiness | Docker image, deployment pipeline, security scanning report, operational runbooks, production sign-off |

---

## 2. Phase 1: Foundation & Contract Design (Weeks 1–4)

### 2.1 Objectives

- Define and freeze OpenAPI 3.0.3 REST API contract aligned to FR-001, FR-002, FR-003, BR-001
- Establish OAuth2 resource server security baseline (JWT bearer tokens, ACCOUNT_INQUIRER role)
- Configure Maven 3.9+ build pipeline with Spring Boot 3.3.x and required dependencies
- Configure Node.js 20 LTS + npm + Vite 5.x build pipeline for React 18.x frontend
- Set up development environment (IDE configurations, linting, code formatting, pre-commit hooks)
- Establish structured logging and correlation ID propagation framework
- Conduct security baseline review and authorize OAuth2 token handling
- Prepare UAT environment specification

### 2.2 Deliverables

| Deliverable | Owner | Due Date | Status Gate |
|---|---|---|---|
| **OpenAPI 3.0.3 Specification (openapi.yaml)** | Architecture + Backend Lead | Week 1 EOD | Contract review + freeze authorization |
| **Spring Boot 3.3.x Starter Project** | Backend Lead | Week 2 | Build success + dependency resolution |
| **OAuth2 Adapter Configuration (Spring Security)** | Backend Lead + Security | Week 2 | Security baseline review approved |
| **React 18.x + Vite 5.x Starter Project** | Frontend Lead | Week 2 | Build success + dev server operational |
| **Structured Logging Framework (SLF4J + JSON)** | Backend Lead | Week 3 | Correlation ID propagation verified |
| **Development Environment Runbook** | DevOps + Tech Lead | Week 3 | Team onboarding readiness |
| **Security Baseline Review Report** | Security Officer | Week 4 | Phase 1 gate approval |
| **UAT Environment Specification** | QA + DevOps | Week 4 | Infrastructure provisioning kickoff |

### 2.3 Work Breakdown

**TASK-001 to TASK-010** (API contract, OAuth2 adapter, build toolchain setup)

**Dependencies:**
- System Intent Blueprint (`provided/system-intent.md`) must be finalized before TASK-001 kickoff
- No external mainframe connectivity required (mock repository only)

**Risks:**
- **RISK-P1-001 (Medium):** OpenAPI specification scope creep beyond composite-key lookup. **Mitigation:** Require architecture sign-off on spec by EOD week 1; any additions require formal change control.
- **RISK-P1-002 (Medium):** Spring Boot OAuth2 Resource Server configuration complexity. **Mitigation:** Assign senior backend engineer; include external security review before week 2 gate.

**Team & Effort Estimate:**

| Role | FTE | Primary Tasks |
|---|---|---|
| **Architecture Lead** | 0.5 | OpenAPI design, security baseline, tech stack validation |
| **Backend Lead** | 1.0 | Spring Boot setup, OAuth2 adapter, logging framework |
| **Frontend Lead** | 1.0 | React + Vite setup, development environment |
| **Security Officer** | 0.25 | OAuth2 token handling review, transport security |
| **DevOps** | 0.5 | Maven/npm pipeline, artifact repository, environment provisioning |

### 2.4 Phase 1 Gate Criteria (Week 4 EOD)

**MUST PASS (Blocking):**
- ✓ OpenAPI 3.0.3 specification frozen with architecture sign-off
- ✓ OAuth2 JWT bearer token validation functional (Spring Security Resource Server)
- ✓ Maven 3.9+ build produces executable Spring Boot 3.3.x JAR with no critical security findings
- ✓ Node.js 20 LTS + npm build produces Vite dev server and production bundle
- ✓ Correlation ID injected in all application logs (SLF4J JSON format)
- ✓ ACCOUNT_INQUIRER role recognized by OAuth2 adapter
- ✓ Structured logging test suite passes (correlation ID propagation verified)
- ✓ Development environment runbook reviewed and approved by all team members

**SHOULD PASS (Non-blocking, escalate if missing):**
- ✓ Pre-commit hooks (code formatting, linting) operational for both Java and TypeScript
- ✓ IDE configurations (IntelliJ, VSCode) documented and distributed
- ✓ Security baseline review completed with zero critical findings

**Phase 1 Sign-Off Authority:** Program Manager + Architecture Lead + Security Officer

---

## 3. Phase 2: Core Service & Persistence (Weeks 5–8)

### 3.1 Objectives

- Implement Spring Boot REST controller for GET `/accounts/{sortcode}/{accountNumber}` endpoint
- Implement AccountInquiryService with business logic for BR-001 (composite-key lookup)
- Implement validation service for FR-002 (sortcode/account number format validation)
- Implement mock AccountRepository with in-memory or H2 embedded database
- Implement global exception handler for standardized error responses (FR-004, FR-005, FR-006)
- Implement structured logging with correlation ID propagation across all service methods
- Achieve 75%+ unit and integration test coverage for service and persistence layers
- Produce comprehensive API integration test suite validating OpenAPI contract compliance
- Generate API documentation from code (Spring OpenAPI auto-generation)

### 3.2 Deliverables

| Deliverable | Owner | Due Date | Status Gate |
|---|---|---|---|
| **AccountInquiryController (REST endpoint)** | Backend Dev Team | Week 5 | Integration test passes |
| **AccountInquiryService (business logic)** | Backend Dev Team | Week 5 | Unit tests 80%+ coverage |
| **ValidationService (format checks)** | Backend Dev Team | Week 5 | Unit tests 90%+ coverage |
| **AccountRepository (mock persistence)** | Backend Dev Team | Week 6 | Integration tests, data mapping verified |
| **GlobalExceptionHandler (error translation)** | Backend Dev Team | Week 6 | All error paths tested (TC-008, TC-009, TC-010) |
| **Structured Logging Implementation** | Backend Dev Team | Week 6 | Correlation ID tests pass; sample logs reviewed |
| **Unit Test Suite (service + data layers)** | QA + Backend Dev | Week 7 | 75%+ coverage report; all tests pass |
| **Integration Test Suite (Spring Boot context)** | QA + Backend Dev | Week 7 | Contract tests pass; end-to-end flows verified |
| **API Documentation (generated from code)** | Backend Dev Team | Week 8 | Matches openapi.yaml (phase 1) |
| **Mock Data Repository (ACCOUNT records)** | Backend Dev Team | Week 8 | 20+ test accounts pre-loaded; full field mapping |
| **Phase 2 QA Report** | QA Lead | Week 8 | Coverage metrics, risk assessment |

### 3.3 Work Breakdown

**TASK-011 to TASK-024** (REST controller, service layer, validation, exception handling, mock repository, unit/integration tests)

**Key Components to Implement:**

```
Backend Source Tree:
├── src/main/java/com/inqacc/
│   ├── controller/
│   │   └── AccountInquiryController.java
│   ├── service/
│   │   ├── AccountInquiryService.java
│   │   └── ValidationService.java
│   ├── repository/
│   │   ├── AccountRepository.java
│   │   └── MockAccountRepository.java (implementation)
│   ├── entity/
│   │   └── AccountEntity.java
│   ├── dto/
│   │   ├── AccountResponseDto.java
│   │   └── ErrorResponseDto.java
│   ├── exception/
│   │   ├── AccountNotFoundException.java
│   │   ├── ValidationException.java
│   │   └── GlobalExceptionHandler.java
│   ├── logging/
│   │   └── CorrelationIdFilter.java
│   └── config/
│       ├── OAuth2Config.java
│       └── WebConfig.java
├── src/test/java/com/inqacc/
│   ├── service/
│   │   ├── AccountInquiryServiceTest.java
│   │   └── ValidationServiceTest.java
│   ├── repository/
│   │   └── MockAccountRepositoryTest.java
│   ├── controller/
│   │   └── AccountInquiryControllerTest.java
│   └── integration/
│       └── AccountInquiryE2ETest.java
└── pom.xml (Maven configuration)
```

**Dependencies:**
- Phase 1 OpenAPI specification must be finalized and authorized
- Spring Boot 3.3.x starter project from Phase 1 available
- OAuth2 adapter from Phase 1 operational

**Risks:**
- **RISK-P2-001 (Medium):** Field mapping between COBOL ACCOUNT copybook and Java AccountEntity may have discrepancies. **Mitigation:** Conduct detailed mapping review (program-analysis.md) before TASK-015 start; pair-program implementation with legacy analyst.
- **RISK-P2-002 (Medium):** Mock repository implementation complexity if using H2 embedded DB. **Mitigation:** Start with in-memory HashMap; escalate to H2 only if persistence required between server restarts.
- **RISK-P2-003 (Low):** Integration test flakiness due to OAuth2 mock setup. **Mitigation:** Use Spring Security test annotations (@WithMockUser); test OAuth2 adapter separately in Phase 1.

**Team & Effort Estimate:**

| Role | FTE | Primary Tasks |
|---|---|---|
| **Backend Dev Lead** | 1.0 | Controller, service, repository design + code review |
| **Backend Dev (2x Junior)** | 2.0 | Controller, service, validation, exception handler implementation |
| **QA Automation Lead** | 0.75 | Test strategy, unit/integration test design, mock data setup |
| **QA Automation (1x)** | 1.0 | Unit test implementation, integration test suite |

### 3.4 Phase 2 Gate Criteria (Week 8 EOD)

**MUST PASS (Blocking):**
- ✓ AccountInquiryController GET endpoint functional and responds to HTTP requests
- ✓ AccountInquiryService executes BR-001 (composite-key lookup) correctly
- ✓ ValidationService rejects invalid sortcodes and account numbers per FR-002
- ✓ Mock AccountRepository returns correct account records matching composite key
- ✓ GlobalExceptionHandler translates service exceptions to standardized HTTP error responses (FR-004, FR-005, FR-006)
- ✓ Unit test coverage ≥ 75% (service + repository layers); all tests passing
- ✓ Integration test coverage ≥ 75% (controller + service layers); all tests passing
- ✓ Correlation ID present in all structured log entries (JSON format)
- ✓ OpenAPI specification auto-generated from code matches Phase 1 frozen spec
- ✓ Mock data repository contains ≥ 20 test ACCOUNT records with complete field population

**SHOULD PASS (Non-blocking, escalate if missing):**
- ✓ Contract test suite validates HTTP semantics against openapi.yaml
- ✓ Code review completed; all critical findings resolved
- ✓ Performance baseline latency < 100ms for account lookup (p95)

**Phase 2 Sign-Off Authority:** Tech Lead + QA Lead + Backend Lead

---

## 4. Phase 3: Legacy Parity & Frontend (Weeks 9–16)

### 4.1 Objectives

- Implement React 18.x web UI with TypeScript 5.x for account inquiry interface
- Integrate React frontend with Spring Boot REST API (authentication flow, request/response handling)
- Conduct comprehensive legacy parity validation (COBOL/DB2 behavior → modernized behavior)
- Implement React component unit tests (React Testing Library + Vitest)
- Implement end-to-end (E2E) test suite covering complete user workflows
- Prepare UAT environment with all hardening and pre-release validations
- Achieve 80%+ overall line coverage (backend + frontend combined)
- Validate all test cases from test-spec.md (47+ explicit test cases)
- Produce comprehensive E2E test report with evidence of legacy parity

### 4.2 Deliverables

| Deliverable | Owner | Due Date | Status Gate |
|---|---|---|---|
| **React 18.x Frontend Application** | Frontend Dev Team | Week 10 | Builds without errors; dev server operational |
| **AccountInquiry React Component** | Frontend Dev Team | Week 10 | API integration functional; displays account details |
| **Authentication/Authorization Flow (OAuth2 UI)** | Frontend Dev Team | Week 11 | Login/logout flow works; bearer token captured |
| **Input Validation UI (sortcode/account number)** | Frontend Dev Team | Week 11 | Client-side validation; error messages displayed |
| **Error Handling & Display (4xx/5xx responses)** | Frontend Dev Team | Week 11 | Error messages from API rendered correctly |
| **React Component Tests** | QA + Frontend Dev | Week 12 | 80%+ coverage; all component tests pass |
| **E2E Test Suite (Playwright or Cypress)** | QA Automation | Week 13 | All 47+ test cases from test-spec.md implemented |
| **Legacy Parity Validation Report** | QA Lead + Backend Lead | Week 14 | All COBOL observable behavior verified in modernized system |
| **Field Mapping Validation Tests** | QA + Backend Dev | Week 14