from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.document import DocumentDetailResponse
from backend.services.search_service import SearchService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    service = SearchService(db)
    document = service.get_document_by_id(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Документ не найден")

    return document