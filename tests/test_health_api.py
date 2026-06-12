from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from backend.api import health as health_api
from backend.main import app


class FakeHealthyDB:
    async def execute(self, statement):
        assert "SELECT 1" in str(statement)


class FakeBrokenDB:
    async def execute(self, statement):
        raise SQLAlchemyError("db unavailable")


def test_health_endpoint_returns_ok():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_db_endpoint_returns_ok_without_real_database():
    async def override_get_db():
        yield FakeHealthyDB()

    app.dependency_overrides[health_api.get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.get("/health/db")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "connected",
    }


def test_health_db_endpoint_returns_503_on_database_error():
    async def override_get_db():
        yield FakeBrokenDB()

    app.dependency_overrides[health_api.get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.get("/health/db")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["detail"] == {
        "status": "error",
        "database": "disconnected",
    }
