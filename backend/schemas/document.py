from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class DocumentShortResponse(BaseModel):
    id: int
    document_type: str
    document_number: str | None = None
    status: str | None = None
    applicant_name: str | None = None
    manufacturer_name: str | None = None
    product_full_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class DocumentDetailResponse(DocumentShortResponse):
    registered_at: date | None = None
    valid_until: date | None = None
    technical_regulations: str | None = None
    product_group: str | None = None
    product_brand: str | None = None
    product_model: str | None = None
    product_article: str | None = None
    product_codes: str | None = None
    test_laboratory: str | None = None
    test_protocol_date: date | None = None
    test_protocol_number: str | None = None
    source_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)