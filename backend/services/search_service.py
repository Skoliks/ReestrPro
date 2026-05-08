from sqlalchemy.orm import Session

from backend.db.models.registry_document import RegistryDocument
from backend.repositories.document_repository import DocumentRepository


class SearchService:
    def __init__(self, db: Session):
        self.document_repository = DocumentRepository(db)

    def get_document_by_id(self, document_id: int) -> RegistryDocument | None:
        return self.document_repository.get_by_id(document_id)

    def search_documents(
        self,
        query: str | None = None,
        document_type: str | None = None,
        status: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[RegistryDocument], int]:
        return self.document_repository.search(
            query=query,
            document_type=document_type,
            status=status,
            limit=limit,
            offset=offset,
        )