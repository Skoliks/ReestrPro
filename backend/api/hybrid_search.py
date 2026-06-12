from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.db.session import get_db
from backend.schemas.hybrid_search import (
    HybridSearchRequest,
    HybridSearchResponse,
    HybridSearchResultItem,
)
from backend.services.hybrid_search_service import HybridSearchService

router = APIRouter(prefix="/hybrid-search", tags=["hybrid-search"])
logger = get_logger(__name__)


@router.post("", response_model=HybridSearchResponse)
async def hybrid_search(
    request: HybridSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = HybridSearchService(db)
        results = await service.hybrid_search(
            query=request.query,
            document_type=request.document_type,
            status=request.status,
            limit=request.limit,
        )
    except SQLAlchemyError:
        logger.exception("Hybrid search failed due to database error")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Hybrid search service is temporarily unavailable",
        )
    except Exception:
        logger.exception("Hybrid search failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Hybrid search request failed",
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
