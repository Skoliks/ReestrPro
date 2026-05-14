from pydantic import BaseModel, Field

from backend.schemas.document import DocumentShortResponse


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Поисковый запрос")
    limit: int = Field(default=5, ge=1, le=50)


class SemanticSearchResultItem(DocumentShortResponse):
    similarity_score: float


class SemanticSearchResponse(BaseModel):
    query: str
    total: int
    items: list[SemanticSearchResultItem]