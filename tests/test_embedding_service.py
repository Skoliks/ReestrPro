import asyncio
from types import SimpleNamespace

from backend.services import embedding_service
from backend.services.embedding_service import EmbeddingService


def test_generate_for_documents_skips_existing_and_saves_new_embeddings(monkeypatch):
    documents = [
        SimpleNamespace(id=1, search_text="existing document"),
        SimpleNamespace(id=2, search_text="new document 1"),
        SimpleNamespace(id=3, search_text="new document 2"),
    ]
    created_batches = []
    embedded_texts = []

    class FakeDocumentRepository:
        def __init__(self, db):
            self.db = db

        async def get_documents_for_embeddings(self, limit: int):
            assert limit == 3
            return documents

    class FakeEmbeddingRepository:
        def __init__(self, db):
            self.db = db

        async def exists_for_document(self, document_id: int, model_name: str) -> bool:
            assert model_name == "fake-model"
            return document_id == 1

        async def create_many(self, embeddings):
            created_batches.append(embeddings)

    class FakeEmbeddingClient:
        model_name = "fake-model"

        def embed_texts(self, texts):
            embedded_texts.append(texts)
            return [[0.1, 0.2], [0.3, 0.4]]

    monkeypatch.setattr(
        embedding_service,
        "DocumentRepository",
        FakeDocumentRepository,
    )
    monkeypatch.setattr(
        embedding_service,
        "EmbeddingRepository",
        FakeEmbeddingRepository,
    )
    monkeypatch.setattr(
        embedding_service,
        "EmbeddingClient",
        FakeEmbeddingClient,
    )

    service = EmbeddingService(db=object())

    result = asyncio.run(service.generate_for_documents(limit=3, batch_size=10))

    assert result == {
        "total_documents": 3,
        "created": 2,
        "skipped": 1,
    }
    assert embedded_texts == [["new document 1", "new document 2"]]
    assert len(created_batches) == 1
    assert [embedding.document_id for embedding in created_batches[0]] == [2, 3]
