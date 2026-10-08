# Async client and lifespan

Use the project's installed HTTPX/FastAPI and async plugin versions. The example uses AnyIO's pytest plugin on asyncio; do not enable a second competing async auto mode. The complete runnable example and verified versions are in the repository's `evals/` directory.

Set isolated test configuration before importing or constructing an application that reads settings. Prefer an existing app factory. Function-scoped clients, app resources and async fixtures should share the same event loop; wider fixtures require compatible plugin/loop scopes.

```python
from contextlib import asynccontextmanager
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

@asynccontextmanager
async def app_client(app):
    previous = app.dependency_overrides.copy()
    try:
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
            ) as client:
                yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
```

The context closes the client before shutdown and restores overrides even after test failure. Use `manager.app` to propagate lifespan state. HTTPX's ASGI transport does not run lifespan by itself. For the error response contract, opt into `raise_app_exceptions=False` deliberately; normally let application errors fail the test.

Run a case whose endpoint uses a resource initialized during startup, assert it closes on exit, then create another app/client to check fresh state. A separate controlled case without lifespan should expose the missing initialization. A synchronous TestClient used as a context manager is also valid for an appropriate synchronous test; do not share loop-bound resources across its worker loop and another async loop.

This exercises in-process ASGI integration, not deployment, sockets or a real HTTP server.

Sources: [FastAPI async tests](https://fastapi.tiangolo.com/advanced/async-tests/), [HTTPX transports](https://www.python-httpx.org/advanced/transports/).
