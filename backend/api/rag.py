from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.rag import AskRequest, AskResponse
from backend.services.rag_service import RagService

router = APIRouter(prefix="/ask", tags=["rag"])


@router.post("", response_model=AskResponse)
def ask_question(
    request: AskRequest,
    db: Session = Depends(get_db),
):
    service = RagService(db)

    result = service.ask(
        question=request.question,
        limit=request.limit,
    )

    return result