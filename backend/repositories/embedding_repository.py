from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.document_embedding import DocumentEmbedding
from backend.db.models.registry_document import RegistryDocument


class EmbeddingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, embedding: DocumentEmbedding) -> DocumentEmbedding:
        self.db.add(embedding)
        await self.db.commit()
        await self.db.refresh(embedding)
        return embedding

    async def create_many(self, embeddings: list[DocumentEmbedding]) -> None:
        if not embeddings:
            return

        self.db.add_all(embeddings)
        await self.db.commit()

    async def exists_for_document(self, document_id: int, model_name: str) -> bool:
        result = await self.db.execute(
            select(DocumentEmbedding).where(
                DocumentEmbedding.document_id == document_id,
                DocumentEmbedding.model_name == model_name,
            )
        )
        return result.scalar_one_or_none() is not None

    async def search_similar(
        self,
        query_embedding: list[float],
        model_name: str,
        limit: int = 5,
    ) -> list[tuple[RegistryDocument, float]]:
        distance = DocumentEmbedding.embedding.cosine_distance(query_embedding)

        result = await self.db.execute(
            select(
                RegistryDocument,
                (1 - distance).label("similarity_score"),
            )
            .join(
                DocumentEmbedding,
                DocumentEmbedding.document_id == RegistryDocument.id,
            )
            .where(DocumentEmbedding.model_name == model_name)
            .order_by(distance)
            .limit(limit)
        )

        return [(row[0], row[1]) for row in result.all()]
