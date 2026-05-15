from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.hybrid_search import (
    HybridSearchRequest,
    HybridSearchResponse,
    HybridSearchResultItem,
)
from backend.services.hybrid_search_service import HybridSearchService

router = APIRouter(prefix="/hybrid-search", tags=["hybrid-search"])


@router.post("", response_model=HybridSearchResponse)
def hybrid_search(
    request: HybridSearchRequest,
    db: Session = Depends(get_db),
):
    service = HybridSearchService(db)

    results = service.hybrid_search(
        query=request.query,
        document_type=request.document_type,
        status=request.status,
        limit=request.limit,
    )

    items = [
        HybridSearchResultItem(
            id=result["document"].id,
            document_type=result["document"].document_type,
            document_number=result["document"].document_number,
            status=result["document"].status,
            applicant_name=result["document"].applicant_name,
            manufacturer_name=result["document"].manufacturer_name,
            product_full_name=result["document"].product_full_name,
            keyword_score=result["keyword_score"],
            semantic_score=result["semantic_score"],
            final_score=result["final_score"],
        )
        for result in results
    ]

    return HybridSearchResponse(
        query=request.query,
        document_type=request.document_type,
        status=request.status,
        total=len(items),
        items=items,
    )