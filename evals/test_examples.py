from contextlib import asynccontextmanager
import os
from pathlib import Path

import pytest
from asgi_lifespan import LifespanManager
from fastapi import Depends, FastAPI, Request
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


@pytest.fixture
def anyio_backend():
    return "asyncio"


def make_app():
    @asynccontextmanager
    async def lifespan(app):
        app.state.resource = {"open": True}
        try:
            yield
        finally:
            app.state.resource["open"] = False

    app = FastAPI(lifespan=lifespan)

    def identity():
        return "original"

    @app.get("/resource")
    async def resource(request: Request, user=Depends(identity)):
        assert request.app.state.resource["open"]
        return {"user": user, "open": True}

    return app, identity


@asynccontextmanager
async def app_client(app):
    previous = app.dependency_overrides.copy()
    try:
        async with LifespanManager(app) as manager:
            async with AsyncClient(transport=ASGITransport(app=manager.app), base_url="http://test") as client:
                yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


@pytest.mark.anyio
async def test_lifespan_and_override_cleanup_after_failure():
    app, identity = make_app()
    with pytest.raises(AssertionError, match="controlled failure"):
        async with app_client(app) as client:
            app.dependency_overrides[identity] = lambda: "overridden"
            response = await client.get("/resource")
            assert response.status_code == 200
            assert response.json() == {"user": "overridden", "open": True}
            raise AssertionError("controlled failure")
    assert not app.state.resource["open"]
    assert app.dependency_overrides == {}
    async with app_client(app) as client:
        assert (await client.get("/resource")).json() == {"user": "original", "open": True}
    assert not app.state.resource["open"]


@pytest.mark.anyio
async def test_missing_startup_is_detected():
    app, _ = make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with pytest.raises(AttributeError, match="resource"):
            await client.get("/resource")


def verified_url():
    value = os.environ.get("SKILL_EVAL_DATABASE_URL")
    owned = os.environ.get("SKILL_EVAL_OWNED_DIR")
    if not value or not owned:
        raise RuntimeError("Run through run_postgres.py with an owned temporary cluster")
    url = make_url(value)
    directory = Path(owned)
    if not (directory / "owned-eval-cluster").is_file() or url.query.get("host") != str(directory / "socket") or url.database != "skill_eval" or url.username != "skill_eval":
        raise RuntimeError("Unverified database target")
    return url


def test_missing_or_unverified_database_configuration_fails_closed(monkeypatch):
    monkeypatch.delenv("SKILL_EVAL_DATABASE_URL", raising=False)
    monkeypatch.delenv("SKILL_EVAL_OWNED_DIR", raising=False)
    with pytest.raises(RuntimeError):
        verified_url()
    monkeypatch.setenv("SKILL_EVAL_DATABASE_URL", "postgresql+asyncpg://skill_eval@localhost/not_owned")
    monkeypatch.setenv("SKILL_EVAL_OWNED_DIR", "/does-not-exist")
    with pytest.raises(RuntimeError):
        verified_url()


@asynccontextmanager
async def isolated_session(engine):
    async with engine.connect() as connection:
        outer = await connection.begin()
        try:
            async with AsyncSession(bind=connection, join_transaction_mode="create_savepoint") as session:
                yield session
        finally:
            if outer.is_active:
                await outer.rollback()


@pytest.mark.anyio
async def test_endpoint_commit_is_rolled_back_and_postgres_checks_uniqueness():
    engine = create_async_engine(verified_url())
    try:
        async with engine.begin() as connection:
            await connection.execute(text("CREATE TABLE sample (id integer PRIMARY KEY, label text UNIQUE NOT NULL)"))
        async with isolated_session(engine) as session:
            app = FastAPI()

            async def get_session():
                yield session

            @app.post("/items")
            async def insert(db=Depends(get_session)):
                await db.execute(text("INSERT INTO sample VALUES (1, 'one')"))
                await db.commit()
                return {"id": 1, "label": "one"}

            async with app_client(app) as client:
                response = await client.post("/items")
                assert response.status_code == 200
                assert response.json() == {"id": 1, "label": "one"}
            assert (await session.execute(text("SELECT count(*) FROM sample"))).scalar_one() == 1
        async with engine.connect() as connection:
            assert (await connection.execute(text("SELECT count(*) FROM sample"))).scalar_one() == 0
        async with isolated_session(engine) as session:
            await session.execute(text("INSERT INTO sample VALUES (2, 'duplicate')"))
            await session.commit()
            with pytest.raises(IntegrityError):
                await session.execute(text("INSERT INTO sample VALUES (3, 'duplicate')"))
            await session.rollback()
        async with engine.connect() as connection:
            assert (await connection.execute(text("SELECT count(*) FROM sample"))).scalar_one() == 0
    finally:
        await engine.dispose()
