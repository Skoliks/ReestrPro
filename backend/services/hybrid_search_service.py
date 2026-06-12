from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.document_repository import DocumentRepository
from backend.services.embedding_service import EmbeddingService


class HybridSearchService:
    def __init__(self, db: AsyncSession) -> None:
        self.document_repository = DocumentRepository(db)
        self.embedding_service = EmbeddingService(db)

    async def hybrid_search(
        self,
        query: str,
        document_type: str | None = None,
        status: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        classic_items, _ = await self.document_repository.search(
            query=query,
            document_type=document_type,
            status=status,
            limit=limit,
            offset=0,
        )

        semantic_results = await self.embedding_service.semantic_search(
            query=query,
            limit=limit,
        )

        results_by_id: dict[int, dict] = {}

        for document in classic_items:
            results_by_id[document.id] = {
                "document": document,
                "keyword_score": 1.0,
                "semantic_score": 0.0,
            }

        for document, semantic_score in semantic_results:
            if document_type and document.document_type != document_type:
                continue

            if status and document.status != status:
                continue

            if document.id not in results_by_id:
                results_by_id[document.id] = {
                    "document": document,
                    "keyword_score": 0.0,
                    "semantic_score": float(semantic_score),
                }
            else:
                results_by_id[document.id]["semantic_score"] = float(semantic_score)

        results = []

        for item in results_by_id.values():
            keyword_score = item["keyword_score"]
            semantic_score = item["semantic_score"]

            final_score = self._calculate_final_score(
                keyword_score=keyword_score,
                semantic_score=semantic_score,
            )

            results.append(
                {
                    "document": item["document"],
                    "keyword_score": keyword_score,
                    "semantic_score": semantic_score,
                    "final_score": final_score,
                }
            )

        results.sort(key=lambda item: item["final_score"], reverse=True)

        return results[:limit]

    @staticmethod
    def _calculate_final_score(keyword_score: float, semantic_score: float) -> float:
        return keyword_score * 0.4 + semantic_score * 0.6
