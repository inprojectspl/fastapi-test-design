---
name: fastapi-tests-design
description: Designs high-quality test strategy and implementation plans for FastAPI backends using JWT auth and PostgreSQL. Use when user asks to create, improve, review, or refactor tests for routers, services, repositories, auth dependencies, permission checks, or validation logic in FastAPI projects.
---

# fastapi-tests-design

## Purpose
Produce deterministic, maintainable test plans and test code guidance for FastAPI + JWT + PostgreSQL backends.

This skill is optimized to prevent:
- fake unit tests that secretly depend on DB/network,
- flaky async/database tests,
- auth/security blind spots,
- weak assertion patterns that create false confidence.

## When to use
Use this skill when the user asks to:
- add or redesign tests for a FastAPI backend,
- validate JWT/auth/authorization behavior,
- define unit vs integration boundaries,
- improve fixture architecture and isolation,
- review test quality and anti-patterns.

## CRITICAL rules
1. Keep boundaries explicit:
   - **Unit tests**: no HTTP, no real DB, no network.
   - **Narrow integration tests**: HTTP + app wiring, controlled dependencies.
   - **DB-bound tests**: repository + real Postgres behavior.
2. Do not claim a test is unit if it touches a real database, filesystem, clock, network, or framework runtime.
3. Prefer async-first test setup when app/database stack is async.
4. Security-sensitive paths require negative tests (not only happy path).
5. Every proposed test must include a concrete failure condition and assertion target.

## What to inspect first
Before proposing tests, extract:
1. Architectural layering:
   - routes/controllers,
   - services/use-cases,
   - repositories/data access,
   - auth dependencies/security utilities.
2. Dependency injection points (`Depends`, provider functions, settings providers).
3. Auth model:
   - token minting,
   - token decoding/validation,
   - scope/role checks,
   - disabled/revoked user handling.
4. Data boundaries:
   - where Postgres is accessed,
   - transaction/session lifecycle,
   - migrations and DB-specific logic.
5. Current test stack:
   - pytest plugins,
   - async client choice,
   - fixture strategy,
   - dependency override usage.

## Classification heuristics (must apply)
Classify each requested test target using this decision order:

1. **Touches HTTP boundary?**
   - Yes -> API-level or narrow integration.
   - No -> candidate unit or DB-bound.
2. **Touches real database behavior?**
   - Yes -> DB-bound integration/repository test.
   - No -> unit/API-level.
3. **Primary intent is auth policy enforcement?**
   - Yes -> auth/security test class.
4. **Requires framework runtime, dependency graph, serialization, or middleware?**
   - Yes -> not pure unit.

Output the classification explicitly for each test area.

## FastAPI + JWT + PostgreSQL testing playbook

### A) True unit tests (service/domain/utility)
Use for:
- business rules in services/use-cases,
- pure token helpers,
- validators and transformation logic,
- permission policy functions.

Requirements:
- inject repository/auth adapters as mocks/fakes,
- freeze time when testing expiry-sensitive logic,
- control UUID/random/environment sources,
- assert exact outcomes (return values, raised exceptions, interactions).

### B) Narrow integration tests (FastAPI app wiring)
Use for:
- router-to-service wiring,
- request/response validation contracts,
- dependency override behavior,
- exception translation to HTTP responses.

Requirements:
- use app factory if available,
- isolate dependency overrides per test and clear after each,
- use async client for async stack,
- test both success and failure response contracts.

### C) Auth/security tests (JWT and authorization)
Must include negative-path coverage for:
- missing token,
- malformed token,
- invalid signature,
- wrong algorithm,
- expired token,
- disabled/revoked user,
- missing role/scope,
- access to protected resources with insufficient permissions.

Requirements:
- test middleware/dependency behavior directly through HTTP layer,
- verify expected status codes and error semantics,
- do not rely only on mocked “always-authenticated user” fixtures.

### D) Database-bound behavior tests (repository + Postgres semantics)
Use for:
- SQL constraints and uniqueness,
- transaction behavior,
- query correctness,
- migration-critical behavior.

Requirements:
- run against isolated test DB state,
- ensure per-test cleanup (transaction rollback or equivalent isolation strategy),
- avoid cross-test state leakage,
- keep business-rule tests out of repository tests unless DB behavior is the subject.

## Fixture architecture recommendations
Enforce this shape where feasible:
1. `settings` fixture (testing environment, secrets, DB URL).
2. `app` fixture from factory (fresh instance).
3. `db_session` fixture (isolated session/transaction strategy).
4. `client` fixture (`httpx.AsyncClient` for async stacks).
5. `dependency_override` helper fixture with guaranteed cleanup.
6. factory fixtures for test data generation (users, roles, entities).

## Determinism checklist
When relevant, require deterministic control for:
- time (`exp`, token freshness windows),
- UUID generation,
- randomness,
- environment/settings,
- timezone assumptions,
- ordering/pagination defaults.

## Anti-patterns to reject
Reject or rewrite plans containing:
- “unit tests” that hit real DB/network,
- fat router tests that duplicate service tests,
- auth tests covering only valid token path,
- shared mutable fixtures causing cross-test contamination,
- weak assertions (`status_code == 200` only, no payload/error semantics),
- over-mocking that removes behavior actually under test,
- synchronous test clients on async DB stacks that create loop issues.

## Required output contract
Every final answer must use this structure:

1. **Scope & assumptions**
   - What was requested, what was inferred, open risks.
2. **Test classification map**
   - Target -> test type (unit / narrow integration / API-level / auth-security / DB-bound) + rationale.
3. **Proposed test cases**
   - Prioritized list with Given/When/Then focus and failure-path coverage.
4. **Fixture & isolation plan**
   - Concrete fixtures, overrides, cleanup rules.
5. **Implementation sketch**
   - File-level plan and naming conventions.
6. **Quality gate**
   - Explicit pass/fail checklist below.

## Quality gate (MANDATORY before finalizing)
Do not finalize output until all are true:
- [ ] Classification is explicit and consistent with boundaries.
- [ ] At least one negative test exists for each security-sensitive path.
- [ ] Time/UUID/env determinism controls are defined where needed.
- [ ] DB isolation strategy is explicit (no hidden shared state).
- [ ] Assertions are behavior-specific, not generic.
- [ ] No anti-pattern from this skill appears in the proposal.

## Example mini-classification
- `AuthService.validate_credentials` -> **Unit**
- `GET /tasks` schema and error mapping -> **API-level / narrow integration**
- `JWTBearer` invalid signature and expired token handling -> **Auth/security**
- `TaskRepository.create` unique constraint behavior in Postgres -> **DB-bound**

## Output style
- Be direct, opinionated, and implementation-ready.
- Prefer concrete test names and fixture names over abstract advice.
- Keep recommendations aligned to FastAPI + JWT + PostgreSQL realities.
- If context is missing, ask only high-leverage questions needed to avoid incorrect test boundaries.
