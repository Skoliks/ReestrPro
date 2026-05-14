from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.semantic_search import (
    SemanticSearchRequest,
    SemanticSearchResponse,
    SemanticSearchResultItem,
)
from backend.services.embedding_service import EmbeddingService

router = APIRouter(prefix="/semantic-search", tags=["semantic-search"])


@router.post("", response_model=SemanticSearchResponse)
def semantic_search(
    request: SemanticSearchRequest,
    db: Session = Depends(get_db),
):
    service = EmbeddingService(db)

    results = service.semantic_search(
        query=request.query,
        limit=request.limit,
    )

    items = [
        SemanticSearchResultItem(
            id=document.id,
            document_type=document.document_type,
            document_number=document.document_number,
            status=document.status,
            applicant_name=document.applicant_name,
            manufacturer_name=document.manufacturer_name,
            product_full_name=document.product_full_name,
            similarity_score=float(score),
        )
        for document, score in results
    ]

    return SemanticSearchResponse(
        query=request.query,
        total=len(items),
        items=items,
    )