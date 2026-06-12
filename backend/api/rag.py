from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.db.session import get_db
from backend.schemas.rag import AskRequest, AskResponse
from backend.services.rag_service import RagService

router = APIRouter(prefix="/ask", tags=["rag"])
logger = get_logger(__name__)


@router.post("", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = RagService(db)
        result = await service.ask(
            question=request.question,
            limit=request.limit,
        )
    except SQLAlchemyError:
        logger.exception("RAG request failed due to database error")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG service is temporarily unavailable",
        )
    except ValueError as exc:
        logger.warning("RAG request failed due to configuration error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG service is not configured",
        )
    except Exception:
        logger.exception("RAG or GigaChat request failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate RAG answer",
        )

    return result
