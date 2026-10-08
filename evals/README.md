# Evaluation and review record

Reviewed and executed on 2026-10-08. Baseline HEAD matched the audit: `cc45a7047080650c7c487926abc4cc36867f11a6`.

## Executed examples

Requirements: Python, uv and PostgreSQL binaries (`initdb`, `pg_ctl`, `createdb`). From `evals/`:

```sh
uv venv .venv
uv pip sync requirements.txt
.venv/bin/python run_postgres.py
```

Result: **4 passed**. The runner creates and destroys a private temporary cluster with a dedicated role/database, a private Unix socket and no TCP listener. It ignores ambient application DSNs. Trust authentication is confined to the owned temporary cluster/socket, not a recommendation for shared servers. No existing database is migrated or reset.

Verified versions: Python 3.13.13, PostgreSQL 18.6, FastAPI 0.142.4, Starlette 1.7.0, HTTPX 0.28.1, asgi-lifespan 2.1.0, AnyIO 4.15.1, pytest 9.1.1, SQLAlchemy 2.0.54, asyncpg 0.32.0. `requirements.txt` pins all Python dependencies.

Coverage: startup-dependent endpoint, shutdown and override restoration after an exception, missing-startup detection, fail-closed configuration checks, endpoint commit followed by absence on a fresh connection, and a real PostgreSQL uniqueness violation. The savepoint fixture covers sequential sessions on one injected connection; multiple pools, migration scripts, parallel workers and JWT implementations are not exercised here.

## Audit decisions and evidence

| IDs | Files | Decision and evidence |
| --- | --- | --- |
| FTD-01 | SKILL, async-client-lifespan, test_examples.py | Adopt transport/lifespan ownership and finally cleanup; lifecycle and failure examples executed |
| FTD-02 | SKILL, database-isolation, test_examples.py | Adopt connection/commit analysis; commit isolation and uniqueness checked on real PostgreSQL |
| FTD-03 | SKILL, database-isolation, runner | Adopt fail-closed target checks; missing/wrong target rejected before connecting |
| FTD-04 | SKILL, README | Adopt separate proportional plan/review/implement outputs and honest check statuses |
| FTD-05 | SKILL, auth-test-matrix | Adopt conditional claims and ownership/tenant matrix; JWT agent/runtime trials not run |
| FTD-06 | SKILL | Adopt independent expectations, meaningful failure conditions and reversible regressions |
| FTD-07 | references, evals | Add three focused references and executable examples with version/scope record |
| FTD-08 | README, manifests | Preserve skill name fastapi-tests-design and repository name fastapi-test-design; copy instructions include references |
| FTD-09 | evals | Add technical checks and agent cases; repeated agent comparison not run |

## Agent evaluations (not run)

These are acceptance tasks for future agent runs, not evidence of measured agent improvement. Run each case in an isolated application fixture with no skill, the audited revision and this release, keeping the same model, tools and inputs. Repeat each condition at least three times. Record artifacts, commands, pass/fail reasons, unsolicited changes, questions, time and token cost. Do not use the agent's self-assessment as execution evidence.

| Request / fixture | Acceptance criterion |
| --- | --- |
| Endpoint reads a lifespan resource | Startup and shutdown run; no fake initialized resource hiding omitted startup |
| Endpoint commits inside a transaction | Next test sees no residue; identify additional connections before claiming isolation |
| Missing/unverified test DSN | Stop before migrations or destructive cleanup; do not use DATABASE_URL fallback |
| Valid user A requests user B's record | Real ownership check executes and rejects without modifying B's data |
| JWT exp boundary with configured leeway | Controlled time, contract-based expected result |
| Test one pure function | No architecture or ORM migration |
| Plan tests only | No edits, no fictional execution |
| Contract contradicts implementation | Expose mismatch; do not weaken the oracle |

Sources checked: [FastAPI async tests](https://fastapi.tiangolo.com/advanced/async-tests/), [HTTPX transports](https://www.python-httpx.org/advanced/transports/), [SQLAlchemy transactions](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html).
