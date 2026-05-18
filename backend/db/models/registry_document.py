from datetime import date, datetime, UTC
from typing import  Any

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base



class RegistryDocument(Base):
    __tablename__ = "registry_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, index=True)
    
    import_batch_id: Mapped[int] = mapped_column(Integer, ForeignKey("import_batches.id"), nullable=False, index=True)
    
    source_document_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    document_number: Mapped[str] = mapped_column(String(255), nullable=False)
    temporary_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    registered_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    suspension_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    suspension_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    termination_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    renewal_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    prolongation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    technical_regulations: Mapped[str | None] = mapped_column(Text, nullable=True)
    product_group: Mapped[str | None] = mapped_column(Text)
    unified_product_list: Mapped[str | None] = mapped_column(Text)
    document_schema: Mapped[str | None] = mapped_column(Text)
    document_kind: Mapped[str | None] = mapped_column(Text)
    applicant_type: Mapped[str | None] = mapped_column(String(100))
    applicant_role: Mapped[str | None] = mapped_column(String(255))
    applicant_name: Mapped[str | None] = mapped_column(Text)
    applicant_address: Mapped[str | None] = mapped_column(Text)
    applicant_inn: Mapped[str | None] = mapped_column(String(20))
    applicant_ogrn: Mapped[str | None] = mapped_column(String(20))
    applicant_legal_form: Mapped[str | None] = mapped_column(String(255))
    applicant_branch: Mapped[str | None] = mapped_column(Text)
    manufacturer_type: Mapped[str | None] = mapped_column(String(100))
    manufacturer_name: Mapped[str | None] = mapped_column(Text)
    manufacturer_address: Mapped[str | None] = mapped_column(Text)
    manufacturer_inn: Mapped[str | None] = mapped_column(String(20))
    manufacturer_ogrn: Mapped[str | None] = mapped_column(String(20))
    manufacturer_legal_form: Mapped[str | None] = mapped_column(String(255))
    manufacturer_branch: Mapped[str | None] = mapped_column(Text)
    certification_body: Mapped[str | None] = mapped_column(Text)
    product_origin: Mapped[str | None] = mapped_column(Text)
    product_full_name: Mapped[str | None] = mapped_column(Text)
    product_batch_size: Mapped[str | None] = mapped_column(String(255))
    product_designation: Mapped[str | None] = mapped_column(Text)
    product_type: Mapped[str | None] = mapped_column(Text)
    product_brand: Mapped[str | None] = mapped_column(Text)
    product_model: Mapped[str | None] = mapped_column(Text)
    product_article: Mapped[str | None] = mapped_column(Text)
    product_grade: Mapped[str | None] = mapped_column(String(255))
    product_codes: Mapped[str | None] = mapped_column(Text)
    product_gtin: Mapped[str | None] = mapped_column(String(255))
    product_serial_number: Mapped[str | None] = mapped_column(String(255))
    product_standards: Mapped[str | None] = mapped_column(Text)
    test_laboratory: Mapped[str | None] = mapped_column(Text)
    test_protocol_date: Mapped[date | None] = mapped_column(Date)
    test_protocol_number: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text)
    search_text: Mapped[str] = mapped_column(Text, nullable=False)
    raw_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    
    import_batch = relationship("ImportBatch", back_populates="documents")
    embeddings = relationship(
    "DocumentEmbedding",
    back_populates="document",
    cascade="all, delete-orphan",
)
