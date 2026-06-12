from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.db.session import get_db
from backend.schemas.document import DocumentDetailResponse
from backend.services.search_service import SearchService

router = APIRouter(prefix="/documents", tags=["documents"])
logger = get_logger(__name__)


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(document_id: int, db: AsyncSession = Depends(get_db)):
    try:
        service = SearchService(db)
        document = await service.get_document_by_id(document_id)
    except SQLAlchemyError:
        logger.exception("Document lookup failed due to database error")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document service is temporarily unavailable",
        )

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return document
