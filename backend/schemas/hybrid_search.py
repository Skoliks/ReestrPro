from pydantic import BaseModel, Field

from backend.schemas.document import DocumentShortResponse


class HybridSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Поисковый запрос")
    document_type: str | None = Field(default=None, description="certificate или declaration")
    status: str | None = Field(default=None, description="Статус документа")
    limit: int = Field(default=10, ge=1, le=50)


class HybridSearchResultItem(DocumentShortResponse):
    keyword_score: float
    semantic_score: float
    final_score: float


class HybridSearchResponse(BaseModel):
    query: str
    document_type: str | None
    status: str | None
    total: int
    items: list[HybridSearchResultItem]