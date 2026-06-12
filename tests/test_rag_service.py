import asyncio

from backend.services import rag_service
from backend.services.rag_service import RagService


class FakeDocument:
    id = 42
    document_type = "certificate"
    document_number = "CERT-042"
    status = "active"
    applicant_name = "Applicant"
    manufacturer_name = "Manufacturer"
    product_full_name = "Product"
    product_codes = "1234"
    technical_regulations = "TR TEST"


def test_rag_service_returns_answer_and_sources_without_real_gigachat(monkeypatch):
    captured_prompt = {}

    class FakeHybridSearchService:
        def __init__(self, db):
            assert db == "fake-db"

        async def hybrid_search(self, query: str, limit: int):
            assert query == "question"
            assert limit == 2
            return [
                {
                    "document": FakeDocument(),
                    "final_score": 0.87,
                }
            ]

    class FakeLLMClient:
        def generate_answer(self, question: str, context: str) -> str:
            captured_prompt["question"] = question
            captured_prompt["context"] = context
            return "Mocked RAG answer"

    monkeypatch.setattr(
        rag_service,
        "HybridSearchService",
        FakeHybridSearchService,
    )
    monkeypatch.setattr(rag_service, "LLMClient", FakeLLMClient)

    service = RagService(db="fake-db")

    result = asyncio.run(service.ask(question="question", limit=2))

    assert result == {
        "question": "question",
        "answer": "Mocked RAG answer",
        "sources": [
            {
                "document_id": 42,
                "document_type": "certificate",
                "document_number": "CERT-042",
                "status": "active",
                "product_full_name": "Product",
                "final_score": 0.87,
            }
        ],
    }
    assert captured_prompt["question"] == "question"
    assert "CERT-042" in captured_prompt["context"]
    assert "Product" in captured_prompt["context"]


def test_rag_service_passes_empty_search_context_to_llm(monkeypatch):
    captured_context = {}

    class FakeHybridSearchService:
        def __init__(self, db):
            pass

        async def hybrid_search(self, query: str, limit: int):
            return []

    class FakeLLMClient:
        def generate_answer(self, question: str, context: str) -> str:
            captured_context["value"] = context
            return "Nothing found"

    monkeypatch.setattr(
        rag_service,
        "HybridSearchService",
        FakeHybridSearchService,
    )
    monkeypatch.setattr(rag_service, "LLMClient", FakeLLMClient)

    service = RagService(db="fake-db")

    result = asyncio.run(service.ask(question="missing", limit=3))

    assert result == {
        "question": "missing",
        "answer": "Nothing found",
        "sources": [],
    }
    assert captured_context["value"]
