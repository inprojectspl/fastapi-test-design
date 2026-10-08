---
name: fastapi-tests-design
description: Plans, reviews and implements tests for FastAPI backends using JWT auth and PostgreSQL. Use when the user asks to create, improve, review or refactor tests for routers, services, repositories, auth dependencies, permission checks or validation logic in FastAPI projects, or to fix flaky async or database tests there. Also use for Polish requests such as "napisz testy do endpointu", "testy FastAPI", "testy autoryzacji JWT" or "izolacja bazy w testach".
---

# fastapi-tests-design

## Purpose
Produce deterministic, maintainable test plans, reviews and test code for FastAPI + JWT + PostgreSQL backends.

This skill is optimized to prevent:
- fake unit tests that secretly depend on DB/network,
- flaky async/database tests,
- auth/security blind spots,
- weak assertion patterns that create false confidence.

## Match the requested mode

- **Plan:** boundaries, prioritized scenarios, expectation sources, assumptions and fixture/isolation choices. Do not edit code or imply execution.
- **Review:** located findings, impact and corrections. Do not rewrite the application without a request.
- **Implement:** make authorized test changes and run the narrowest relevant project command. Report actual commands/results, skips and blockers, distinguishing tests from lint/typecheck.

Scale the response to the task. A single function does not need a six-section architecture report. Respect existing layers, ORM, auth mechanism and pytest plugins; do not introduce JWT, SQLAlchemy, a new app factory or service/repository layers merely to fit this skill.

## CRITICAL rules
1. Keep boundaries explicit:
   - **Unit tests**: no HTTP, no real DB, no network.
   - **Narrow integration tests**: HTTP + app wiring, controlled dependencies.
   - **DB-bound tests**: repository + real Postgres behavior.
2. Do not claim a test is unit if it touches a real database, filesystem, clock, network, or framework runtime.
3. Prefer async-first test setup when app/database stack is async.
4. Security-sensitive paths require negative tests (not only happy path).
5. Every important test needs a concrete defect it detects and an independent expectation source: requirement, contract, accepted example or bug report. Do not reproduce the implementation algorithm as the oracle. Surface conflicts instead of recording current bugs as expected behavior.
6. Before mutations, migrations or cleanup, verify an explicitly selected isolated test environment with dedicated credentials and an agreed target check. Missing/unverified configuration fails closed. A database name containing `test` is insufficient; never fall back to production `DATABASE_URL` or print secrets. Scope cache/queue cleanup to owned test resources.

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
   - transaction/session lifecycle, commits, additional connections, background writes and parallel workers,
   - migrations and DB-specific logic.
5. Current test stack:
   - installed library versions, pytest plugins and async/loop configuration,
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
- isolate dependency overrides per test and restore the prior mapping in guaranteed cleanup,
- for an async stack, use HTTPX `AsyncClient` with `ASGITransport`; manage lifespan explicitly when startup/shutdown owns resources. Read [async client and lifespan](references/async-client-lifespan.md) when implementing this setup,
- configure test settings before app construction/import and lifespan, and align fixture/loop scope with async resource ownership. A synchronous `TestClient` is valid when loop boundaries are respected; in-process ASGI tests are not automatically server-level E2E,
- test both success and failure response contracts.

### C) Auth/security tests (JWT and authorization)
Must include negative-path coverage for:
- missing token,
- malformed token,
- invalid signature,
- wrong algorithm,
- expired token,
- disabled/revoked user when part of the contract,
- missing role/scope,
- access to protected resources with insufficient permissions,
- valid user A accessing user B's resources, including equal roles and cross-tenant access where applicable.

For JWT claim/time tests or resource access coverage, read [auth test matrix](references/auth-test-matrix.md). Issuer, audience, nbf, leeway and revocation expectations come from the actual contract, not this skill.

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
- choose isolation after tracing all commits, connections, background tasks and parallel workers; a rollback on one session cannot undo unrelated connections,
- read [database isolation](references/database-isolation.md) before implementing transaction fixtures or database resets; prove endpoint commits do not leak into the next test,
- use real PostgreSQL for its constraints and transactional behavior, not SQLite or mocks,
- avoid cross-test state leakage,
- keep business-rule tests out of repository tests unless DB behavior is the subject.

## Fixture architecture recommendations
Reuse existing fixtures where possible; these are responsibilities, not mandatory names or a required architecture:
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

## Verification and output

Use the selected mode's contract. For broader plans include classification, Given/When/Then scenarios, expectations and fixture isolation. For implementations, include files changed, exact commands/results and anything unverified. Use `not applicable`, `not verified` or `blocked` with reasons rather than claiming every gate passed.

Check relevant boundaries, negative security paths, deterministic time/data, cleanup and behavior-specific assertions. Assert response/error semantics and important side effects, not only HTTP status. Do not change production boundaries, disable auth, weaken assertions, add skip/xfail or lower quality gates solely to obtain green tests.

For regressions, demonstrate failure before the fix and success after it when the revision and environment are available. Distinguish target failures from setup failures. Controlled mutations belong only in isolated, reversible experiments within the authorized scope and must not remain in delivered code.

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
