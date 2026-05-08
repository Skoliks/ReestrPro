from pydantic import BaseModel, Field

from backend.schemas.document import DocumentShortResponse


class SearchRequest(BaseModel):
    query: str | None = Field(default=None, description="Поисковый запрос")
    document_type: str | None = Field(default=None, description="certificate или declaration")
    status: str | None = Field(default=None, description="Статус документа")
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SearchResponse(BaseModel):
    query: str | None
    document_type: str | None
    status: str | None
    total: int
    limit: int
    offset: int
    items: list[DocumentShortResponse]