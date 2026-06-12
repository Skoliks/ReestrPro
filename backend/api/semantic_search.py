from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.db.session import get_db
from backend.schemas.semantic_search import (
    SemanticSearchRequest,
    SemanticSearchResponse,
    SemanticSearchResultItem,
)
from backend.services.embedding_service import EmbeddingService

router = APIRouter(prefix="/semantic-search", tags=["semantic-search"])
logger = get_logger(__name__)


@router.post("", response_model=SemanticSearchResponse)
async def semantic_search(
    request: SemanticSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = EmbeddingService(db)
        results = await service.semantic_search(
            query=request.query,
            limit=request.limit,
        )
    except SQLAlchemyError:
        logger.exception("Semantic search failed due to database error")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Semantic search service is temporarily unavailable",
        )
    except Exception:
        logger.exception("Semantic search failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Semantic search request failed",
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
