import pytest
import redis.asyncio as redis
from httpx2 import AsyncClient, ASGITransport
from datetime import date

from src.crud.models import TradeResultsOrm
from src.main import app
from src.config import settings
from src.crud.dependencies import get_redis_client
from src.crud.schemas import FiltersSchema


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def tc():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        follow_redirects=True,
    ) as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
def redis_setup():
    r = redis.Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
    )

    def redis_client():
        return r

    return redis_client


@pytest.fixture(scope="session", autouse=True)
def override(redis_setup):
    app.dependency_overrides[get_redis_client] = redis_setup
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def dates_data():
    return {
        "dates": [
            "2026-07-08",
            "2026-07-07",
            "2026-07-06",
            "2026-07-03",
            "2026-07-02",
        ]
    }


@pytest.fixture
def results_data():
    d = {
        "id": 1,
        "exchange_product_id": "A",
        "exchange_product_name": "A",
        "oil_id": "A",
        "delivery_basis_id": "A",
        "delivery_basis_name": "A",
        "delivery_type_id": "A",
        "volume": 1,
        "total": 1,
        "count": 1,
        "date": date(2026, 1, 1),
        "created_on": date(2026, 1, 1),
        "updated_on": None,
    }
    res = TradeResultsOrm(**d)
    return [res]


@pytest.fixture
def filters():
    return FiltersSchema()
