import asyncio
from datetime import date

from backend.mcp import tools


class FakeDB:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        self.closed = True


class FakeDocument:
    id = 7
    document_type = "certificate"
    document_number = "CERT-001"
    applicant_name = "Applicant LLC"
    manufacturer_name = "Manufacturer LLC"
    product_full_name = "Test product"
    status = "active"
    registered_at = date(2026, 1, 10)
    valid_until = date(2027, 1, 10)
    product_codes = "1234"
    technical_regulations = "TR TEST"
    source_url = "https://example.test/document"


def test_search_registry_returns_json_compatible_items(monkeypatch):
    fake_db = FakeDB()

    class FakeHybridSearchService:
        def __init__(self, db):
            assert db is fake_db

        async def hybrid_search(self, query: str, limit: int):
            assert query == "test"
            assert limit == 5
            return [
                {
                    "document": FakeDocument(),
                    "keyword_score": 1.0,
                    "semantic_score": 0.5,
                    "final_score": 0.7,
                }
            ]

    monkeypatch.setattr(tools, "SessionLocal", lambda: fake_db)
    monkeypatch.setattr(
        tools,
        "_get_hybrid_search_service_class",
        lambda: FakeHybridSearchService,
    )

    result = asyncio.run(tools.search_registry(query="test", limit=5))

    assert fake_db.closed is True
    assert result["query"] == "test"
    assert result["total"] == 1
    assert result["items"][0] == {
        "id": 7,
        "document_type": "certificate",
        "document_number": "CERT-001",
        "applicant": "Applicant LLC",
        "manufacturer": "Manufacturer LLC",
        "product_name": "Test product",
        "status": "active",
        "start_date": "2026-01-10",
        "end_date": "2027-01-10",
        "score": 0.7,
        "keyword_score": 1.0,
        "semantic_score": 0.5,
        "product_codes": "1234",
        "technical_regulations": "TR TEST",
        "source_url": "https://example.test/document",
    }


def test_get_document_card_closes_db_session(monkeypatch):
    fake_db = FakeDB()

    class FakeDocumentRepository:
        def __init__(self, db):
            assert db is fake_db

        async def get_by_id(self, document_id: int):
            assert document_id == 7
            return FakeDocument()

    monkeypatch.setattr(tools, "SessionLocal", lambda: fake_db)
    monkeypatch.setattr(
        tools,
        "_get_document_repository_class",
        lambda: FakeDocumentRepository,
    )

    result = asyncio.run(tools.get_document_card(document_id=7))

    assert fake_db.closed is True
    assert result["found"] is True
    assert result["document"]["id"] == 7
    assert result["document"]["start_date"] == "2026-01-10"
    assert result["document"]["end_date"] == "2027-01-10"


def test_ask_registry_uses_rag_service_without_real_llm(monkeypatch):
    fake_db = FakeDB()

    class FakeRagService:
        def __init__(self, db):
            assert db is fake_db

        async def ask(self, question: str, limit: int):
            assert question == "question"
            assert limit == 3
            return {
                "question": question,
                "answer": "RAG answer",
                "sources": [
                    {
                        "document_id": 7,
                        "document_type": "certificate",
                        "document_number": "CERT-001",
                        "status": "active",
                        "product_full_name": "Test product",
                        "final_score": 0.9,
                    }
                ],
            }

    class FakeDocumentRepository:
        def __init__(self, db):
            assert db is fake_db

        async def get_by_id(self, document_id: int):
            assert document_id == 7
            return FakeDocument()

    monkeypatch.setattr(tools, "SessionLocal", lambda: fake_db)
    monkeypatch.setattr(tools, "_get_rag_service_class", lambda: FakeRagService)
    monkeypatch.setattr(
        tools,
        "_get_document_repository_class",
        lambda: FakeDocumentRepository,
    )

    result = asyncio.run(tools.ask_registry(question="question", limit=3))

    assert fake_db.closed is True
    assert result["question"] == "question"
    assert result["explanation"] == "RAG answer"
    assert result["sources"][0]["id"] == 7
    assert result["sources"][0]["score"] == 0.9
