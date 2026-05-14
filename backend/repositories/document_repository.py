from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.db.models import RegistryDocument


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, document: RegistryDocument) -> RegistryDocument:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def create_many(self, documents: list[RegistryDocument]) -> None:
        self.db.add_all(documents)
        self.db.commit()

    def get_by_id(self, document_id: int) -> RegistryDocument | None:
        return (
            self.db.query(RegistryDocument)
            .filter(RegistryDocument.id == document_id)
            .first()
        )
    def search(
        self,
        query: str | None = None,
        document_type: str | None = None,
        status: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[RegistryDocument], int]:
        db_query = self.db.query(RegistryDocument)

        if document_type:
            db_query = db_query.filter(RegistryDocument.document_type == document_type)

        if status:
            db_query = db_query.filter(RegistryDocument.status == status)

        if query:
            pattern = f"%{query}%"

            db_query = db_query.filter(
                or_(
                    RegistryDocument.document_number.ilike(pattern),
                    RegistryDocument.applicant_name.ilike(pattern),
                    RegistryDocument.manufacturer_name.ilike(pattern),
                    RegistryDocument.product_full_name.ilike(pattern),
                    RegistryDocument.product_codes.ilike(pattern),
                    RegistryDocument.technical_regulations.ilike(pattern),
                )
            )

        total = db_query.count()

        items = (
            db_query
            .order_by(RegistryDocument.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return items, total
    
    def get_documents_for_embeddings(self, limit: int = 10):
        return (
            self.db.query(RegistryDocument)
            .filter(RegistryDocument.search_text.isnot(None))
            .order_by(RegistryDocument.id.asc())
            .limit(limit)
            .all()
        )