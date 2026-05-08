from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.search import SearchRequest, SearchResponse
from backend.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
def search_documents(request: SearchRequest, db: Session = Depends(get_db)):
    service = SearchService(db)

    items, total = service.search_documents(
        query=request.query,
        document_type=request.document_type,
        status=request.status,
        limit=request.limit,
        offset=request.offset,
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