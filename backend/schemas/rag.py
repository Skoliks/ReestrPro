from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Вопрос пользователя")
    limit: int = Field(default=3, ge=1, le=10)


class RagSource(BaseModel):
    document_id: int
    document_type: str
    document_number: str | None = None
    status: str | None = None
    product_full_name: str | None = None
    final_score: float | None = None


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[RagSource]