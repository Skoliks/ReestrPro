from sqlalchemy.orm import Session

from backend.db.models.document_embedding import DocumentEmbedding
from backend.db.models.registry_document import RegistryDocument

class EmbeddingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, embedding: DocumentEmbedding) -> DocumentEmbedding:
        self.db.add(embedding)
        self.db.commit()
        self.db.refresh(embedding)
        return embedding

    def exists_for_document(self, document_id: int, model_name: str) -> bool:
        return (
            self.db.query(DocumentEmbedding)
            .filter(
                DocumentEmbedding.document_id == document_id,
                DocumentEmbedding.model_name == model_name,
            )
            .first()
            is not None
        )
    def search_similar(
        self,
        query_embedding: list[float],
        model_name: str,
        limit: int = 5,
    ) -> list[tuple[RegistryDocument, float]]:
        distance = DocumentEmbedding.embedding.cosine_distance(query_embedding)

        rows = (
            self.db.query(
                RegistryDocument,
                (1 - distance).label("similarity_score"),
            )
            .join(
                DocumentEmbedding,
                DocumentEmbedding.document_id == RegistryDocument.id,
            )
            .filter(DocumentEmbedding.model_name == model_name)
            .order_by(distance)
            .limit(limit)
            .all()
        )

        return rows