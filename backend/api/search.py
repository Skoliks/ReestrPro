from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.db.session import get_db
from backend.schemas.search import SearchRequest, SearchResponse
from backend.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"])
logger = get_logger(__name__)


@router.post("", response_model=SearchResponse)
async def search_documents(request: SearchRequest, db: AsyncSession = Depends(get_db)):
    try:
        service = SearchService(db)
        items, total = await service.search_documents(
            query=request.query,
            document_type=request.document_type,
            status=request.status,
            limit=request.limit,
            offset=request.offset,
        )
    except SQLAlchemyError:
        logger.exception("Classic search failed due to database error")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search service is temporarily unavailable",
        )
    except Exception:
        logger.exception("Classic search failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search request failed",
        )

    return SearchResponse(
        query=request.query,
        document_type=request.document_type,
        status=request.status,
        total=total,
        limit=request.limit,
        offset=request.offset,
        items=items,
    )
