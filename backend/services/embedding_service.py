from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.db.models.document_embedding import DocumentEmbedding
from backend.external.embedding_client import EmbeddingClient
from backend.repositories.document_repository import DocumentRepository
from backend.repositories.embedding_repository import EmbeddingRepository

logger = get_logger(__name__)

DEFAULT_EMBEDDING_BATCH_SIZE = 32


class EmbeddingService:
    def __init__(self, db: AsyncSession) -> None:
        self.document_repository = DocumentRepository(db)
        self.embedding_repository = EmbeddingRepository(db)
        try:
            self.embedding_client = EmbeddingClient()
        except Exception:
            logger.exception("Embedding model initialization failed")
            raise

    async def generate_for_documents(
        self,
        limit: int = 10,
        batch_size: int = DEFAULT_EMBEDDING_BATCH_SIZE,
    ) -> dict[str, int]:
        documents = await self.document_repository.get_documents_for_embeddings(limit=limit)

        return await self._generate_for_document_list(
            documents=documents,
            batch_size=batch_size,
            log_context="all_documents",
        )

    async def semantic_search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[tuple[object, float]]:
        query_embedding = self.embedding_client.embed_text(query)

        return await self.embedding_repository.search_similar(
            query_embedding=query_embedding,
            model_name=self.embedding_client.model_name,
            limit=limit,
        )

    async def generate_for_import_batch(
        self,
        import_batch_id: int,
        limit: int | None = None,
        batch_size: int = DEFAULT_EMBEDDING_BATCH_SIZE,
    ) -> dict[str, int]:
        documents = await self.document_repository.get_documents_for_embeddings_by_batch(
            import_batch_id=import_batch_id,
            limit=limit,
        )

        return await self._generate_for_document_list(
            documents=documents,
            batch_size=batch_size,
            log_context=f"import_batch_id={import_batch_id}",
        )

    async def _generate_for_document_list(
        self,
        documents: list[object],
        batch_size: int,
        log_context: str,
    ) -> dict[str, int]:
        self._validate_batch_size(batch_size)

        created_count = 0
        skipped_count = 0
        documents_to_embed = []

        logger.info(
            "Embedding generation started: context=%s selected=%s batch_size=%s",
            log_context,
            len(documents),
            batch_size,
        )

        for document in documents:
            if await self.embedding_repository.exists_for_document(
                document_id=document.id,
                model_name=self.embedding_client.model_name,
            ):
                skipped_count += 1
                continue

            documents_to_embed.append(document)

        for start in range(0, len(documents_to_embed), batch_size):
            batch_documents = documents_to_embed[start:start + batch_size]
            texts = [document.search_text for document in batch_documents]
            embedding_vectors = self.embedding_client.embed_texts(texts)

            embeddings = [
                DocumentEmbedding(
                    document_id=document.id,
                    embedding=embedding_vector,
                    model_name=self.embedding_client.model_name,
                    source_text=document.search_text,
                )
                for document, embedding_vector in zip(
                    batch_documents,
                    embedding_vectors,
                    strict=True,
                )
            ]

            await self.embedding_repository.create_many(embeddings)
            created_count += len(embeddings)
            logger.info(
                "Embedding generation progress: context=%s created=%s skipped=%s total=%s",
                log_context,
                created_count,
                skipped_count,
                len(documents),
            )

        logger.info(
            "Embedding generation completed: context=%s selected=%s created=%s skipped=%s",
            log_context,
            len(documents),
            created_count,
            skipped_count,
        )

        return {
            "total_documents": len(documents),
            "created": created_count,
            "skipped": skipped_count,
        }

    @staticmethod
    def _validate_batch_size(batch_size: int) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than 0")
