from backend.db.session import SessionLocal
from backend.repositories.document_repository import DocumentRepository
from backend.services.hybrid_search_service import HybridSearchService


def search_registry(query: str, limit: int = 5) -> dict:
    db = SessionLocal()

    try:
        service = HybridSearchService(db)

        results = service.hybrid_search(
            query=query,
            limit=limit,
        )

        items = []

        for result in results:
            document = result["document"]

            items.append(
                {
                    "id": document.id,
                    "document_type": document.document_type,
                    "document_number": document.document_number,
                    "status": document.status,
                    "applicant_name": document.applicant_name,
                    "manufacturer_name": document.manufacturer_name,
                    "product_full_name": document.product_full_name,
                    "keyword_score": result["keyword_score"],
                    "semantic_score": result["semantic_score"],
                    "final_score": result["final_score"],
                }
            )

        return {
            "query": query,
            "total": len(items),
            "items": items,
        }

    finally:
        db.close()


def get_document_card(document_id: int) -> dict:
    db = SessionLocal()

    try:
        repository = DocumentRepository(db)
        document = repository.get_by_id(document_id)

        if document is None:
            return {
                "found": False,
                "message": "Документ не найден",
                "document": None,
            }

        return {
            "found": True,
            "document": {
                "id": document.id,
                "document_type": document.document_type,
                "document_number": document.document_number,
                "status": document.status,
                "registered_at": document.registered_at.isoformat()
                if document.registered_at
                else None,
                "valid_until": document.valid_until.isoformat()
                if document.valid_until
                else None,
                "applicant_name": document.applicant_name,
                "manufacturer_name": document.manufacturer_name,
                "product_full_name": document.product_full_name,
                "product_codes": document.product_codes,
                "technical_regulations": document.technical_regulations,
                "source_url": document.source_url,
            },
        }

    finally:
        db.close()