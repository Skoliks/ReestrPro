from datetime import date
from typing import Any

from backend.db.models.registry_document import RegistryDocument
from backend.db.session import SessionLocal


def _get_document_repository_class():
    from backend.repositories.document_repository import DocumentRepository

    return DocumentRepository


def _get_hybrid_search_service_class():
    from backend.services.hybrid_search_service import HybridSearchService

    return HybridSearchService


def _get_rag_service_class():
    from backend.services.rag_service import RagService

    return RagService


def _date_to_string(value: date | None) -> str | None:
    if value is None:
        return None

    return value.isoformat()


def _format_document(
    document: RegistryDocument,
    score: float | None = None,
    keyword_score: float | None = None,
    semantic_score: float | None = None,
) -> dict[str, Any]:
    return {
        "id": document.id,
        "document_type": document.document_type,
        "document_number": document.document_number,
        "applicant": document.applicant_name,
        "manufacturer": document.manufacturer_name,
        "product_name": document.product_full_name,
        "status": document.status,
        "start_date": _date_to_string(document.registered_at),
        "end_date": _date_to_string(document.valid_until),
        "score": score,
        "keyword_score": keyword_score,
        "semantic_score": semantic_score,
        "product_codes": document.product_codes,
        "technical_regulations": document.technical_regulations,
        "source_url": document.source_url,
    }


async def search_registry(query: str, limit: int = 5) -> dict[str, Any]:
    """Search certificates and declarations with the existing hybrid search service."""
    async with SessionLocal() as db:
        HybridSearchService = _get_hybrid_search_service_class()
        service = HybridSearchService(db)

        results = await service.hybrid_search(
            query=query,
            limit=limit,
        )

        items = []

        for result in results:
            document = result["document"]

            items.append(
                _format_document(
                    document=document,
                    score=float(result["final_score"]),
                    keyword_score=float(result["keyword_score"]),
                    semantic_score=float(result["semantic_score"]),
                )
            )

        return {
            "query": query,
            "total": len(items),
            "items": items,
        }


async def get_document_card(document_id: int) -> dict[str, Any]:
    """Return a JSON-compatible document card by registry document id."""
    async with SessionLocal() as db:
        DocumentRepository = _get_document_repository_class()
        repository = DocumentRepository(db)
        document = await repository.get_by_id(document_id)

        if document is None:
            return {
                "found": False,
                "message": "Document not found",
                "document": None,
            }

        return {
            "found": True,
            "document": _format_document(document=document),
        }


async def ask_registry(question: str, limit: int = 3) -> dict[str, Any]:
    """Ask a RAG question using the existing RagService and return answer with sources."""
    async with SessionLocal() as db:
        RagService = _get_rag_service_class()
        DocumentRepository = _get_document_repository_class()
        service = RagService(db)
        result = await service.ask(question=question, limit=limit)
        repository = DocumentRepository(db)

        sources = []

        for source in result.get("sources", []):
            document_id = source.get("document_id")
            document = (
                await repository.get_by_id(document_id)
                if document_id is not None
                else None
            )

            if document is None:
                sources.append(
                    {
                        "id": document_id,
                        "document_type": source.get("document_type"),
                        "document_number": source.get("document_number"),
                        "applicant": None,
                        "manufacturer": None,
                        "product_name": source.get("product_full_name"),
                        "status": source.get("status"),
                        "start_date": None,
                        "end_date": None,
                        "score": source.get("final_score"),
                    }
                )
                continue

            sources.append(
                _format_document(
                    document=document,
                    score=source.get("final_score"),
                )
            )

        return {
            "question": result["question"],
            "explanation": result["answer"],
            "sources": sources,
        }
