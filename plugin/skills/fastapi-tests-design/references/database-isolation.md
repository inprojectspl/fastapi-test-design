# PostgreSQL isolation

Before selecting a fixture, trace the driver/ORM, connection acquisition, app commits and rollbacks, background tasks, workers and migrations. Verify the target before connecting or mutating: explicit test-only configuration, dedicated credentials and ownership/identity checks. Reject missing or mismatched targets; do not inspect or print secret values. Never use a production URL as a fallback.

## Choose for the behavior being tested

- **Ordinary application tests, one injectable connection:** an outer transaction can isolate writes if every session joins that connection correctly.
- **Multiple connections, pools or background workers:** use an owned disposable database/schema per test or worker, or a proven reset strategy encompassing every writer. Stop/join background tasks before cleanup. One session rollback is insufficient.
- **Real commit visibility, locks or concurrency:** use independent real transactions in an isolated database. A savepoint fixture changes commit semantics and can hide the behavior being tested.
- **Migrations:** execute actual migration scripts against a disposable database; model `create_all` alone does not test them.

## SQLAlchemy 2.x variant

Assumptions: async SQLAlchemy 2.x, PostgreSQL driver with working SAVEPOINT support, sequential sessions bound to this connection, no independent pool acquisition or concurrent sharing of the session. Test settings and schema are already initialized in a verified isolated environment.

```python
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

@asynccontextmanager
async def isolated_session(engine):
    async with engine.connect() as connection:
        outer = await connection.begin()
        try:
            async with AsyncSession(
                bind=connection, join_transaction_mode="create_savepoint"
            ) as session:
                yield session
        finally:
            if outer.is_active:
                await outer.rollback()
```

Override the application's session dependency to yield this session, restoring the previous override afterward. Application `session.commit()` releases its savepoint while the outer transaction remains available for teardown. Prove this with an endpoint that actually commits and a subsequent fresh connection that sees no inserted row. Also test a real uniqueness violation on PostgreSQL. Do not claim isolation for additional app connections this fixture never intercepts.

For direct asyncpg, check whether the code uses the injected connection or acquires from its pool. A transaction on one connection covers only that connection. Do not introduce SQLAlchemy just to use this example.

See [SQLAlchemy joining a session into an external transaction](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites). The repository evaluation describes the tested version and scope; this is not a universal ORM recipe.
