from sqlalchemy.orm import Session

from backend.db.models.document_embedding import DocumentEmbedding
from backend.external.embedding_client import EmbeddingClient
from backend.repositories.document_repository import DocumentRepository
from backend.repositories.embedding_repository import EmbeddingRepository


class EmbeddingService:
    def __init__(self, db: Session) -> None:
        self.document_repository = DocumentRepository(db)
        self.embedding_repository = EmbeddingRepository(db)
        self.embedding_client = EmbeddingClient()

    def generate_for_documents(self, limit: int = 10) -> dict[str, int]:
        documents = self.document_repository.get_documents_for_embeddings(limit=limit)

        created_count = 0
        skipped_count = 0

        for document in documents:
            if self.embedding_repository.exists_for_document(
                document_id=document.id,
                model_name=self.embedding_client.model_name,
            ):
                skipped_count += 1
                continue

            embedding_vector = self.embedding_client.embed_text(document.search_text)

            embedding = DocumentEmbedding(
                document_id=document.id,
                embedding=embedding_vector,
                model_name=self.embedding_client.model_name,
                source_text=document.search_text,
            )

            self.embedding_repository.create(embedding)
            created_count += 1

        return {
            "total_documents": len(documents),
            "created": created_count,
            "skipped": skipped_count,
        }
        
    def semantic_search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[tuple[object, float]]:
        query_embedding = self.embedding_client.embed_text(query)

        return self.embedding_repository.search_similar(
            query_embedding=query_embedding,
            model_name=self.embedding_client.model_name,
            limit=limit,
        )
        
    def generate_for_import_batch(
    self,
    import_batch_id: int,
    limit: int | None = None,
    ) -> dict[str, int]:
        documents = self.document_repository.get_documents_for_embeddings_by_batch(
            import_batch_id=import_batch_id,
            limit=limit,
        )

        created_count = 0
        skipped_count = 0

        for document in documents:
            if self.embedding_repository.exists_for_document(
                document_id=document.id,
                model_name=self.embedding_client.model_name,
            ):
                skipped_count += 1
                continue

            embedding_vector = self.embedding_client.embed_text(document.search_text)

            embedding = DocumentEmbedding(
                document_id=document.id,
                embedding=embedding_vector,
                model_name=self.embedding_client.model_name,
                source_text=document.search_text,
            )

            self.embedding_repository.create(embedding)
            created_count += 1

        return {
            "total_documents": len(documents),
            "created": created_count,
            "skipped": skipped_count,
        }