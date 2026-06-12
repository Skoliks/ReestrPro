from fastapi.testclient import TestClient

from backend.api import search as search_api
from backend.main import app


class FakeDocument:
    id = 11
    document_type = "declaration"
    document_number = "DECL-011"
    status = "active"
    applicant_name = "Applicant"
    manufacturer_name = "Manufacturer"
    product_full_name = "Product"


def test_search_endpoint_calls_service_with_request_filters(monkeypatch):
    calls = []

    class FakeSearchService:
        def __init__(self, db):
            assert db == "fake-db"

        async def search_documents(
            self,
            query,
            document_type,
            status,
            limit,
            offset,
        ):
            calls.append(
                {
                    "query": query,
                    "document_type": document_type,
                    "status": status,
                    "limit": limit,
                    "offset": offset,
                }
            )
            return [FakeDocument()], 1

    async def override_get_db():
        yield "fake-db"

    monkeypatch.setattr(search_api, "SearchService", FakeSearchService)
    app.dependency_overrides[search_api.get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.post(
                "/search",
                json={
                    "query": "product",
                    "document_type": "declaration",
                    "status": "active",
                    "limit": 5,
                    "offset": 2,
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert calls == [
        {
            "query": "product",
            "document_type": "declaration",
            "status": "active",
            "limit": 5,
            "offset": 2,
        }
    ]
    assert response.json()["items"] == [
        {
            "id": 11,
            "document_type": "declaration",
            "document_number": "DECL-011",
            "status": "active",
            "applicant_name": "Applicant",
            "manufacturer_name": "Manufacturer",
            "product_full_name": "Product",
        }
    ]


def test_search_endpoint_returns_empty_result(monkeypatch):
    class FakeSearchService:
        def __init__(self, db):
            pass

        async def search_documents(self, **kwargs):
            return [], 0

    async def override_get_db():
        yield "fake-db"

    monkeypatch.setattr(search_api, "SearchService", FakeSearchService)
    app.dependency_overrides[search_api.get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.post("/search", json={"query": "missing", "limit": 10})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["items"] == []


def test_search_endpoint_rejects_limit_above_schema_limit(monkeypatch):
    service_was_called = False

    class FakeSearchService:
        def __init__(self, db):
            nonlocal service_was_called
            service_was_called = True

    monkeypatch.setattr(search_api, "SearchService", FakeSearchService)

    with TestClient(app) as client:
        response = client.post("/search", json={"query": "test", "limit": 101})

    assert response.status_code == 422
    assert service_was_called is False
