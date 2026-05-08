from sqlalchemy.orm import Session

from backend.db.models.registry_document import RegistryDocument


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