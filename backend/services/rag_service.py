from sqlalchemy.orm import Session

from backend.external.llm_client import LLMClient
from backend.services.hybrid_search_service import HybridSearchService


class RagService:
    def __init__(self, db: Session) -> None:
        self.hybrid_search_service = HybridSearchService(db)
        self.llm_client = LLMClient()

    def ask(self, question: str, limit: int = 3) -> dict:
        search_results = self.hybrid_search_service.hybrid_search(
            query=question,
            limit=limit,
        )

        context = self._build_context(search_results)

        answer = self.llm_client.generate_answer(
            question=question,
            context=context,
        )

        sources = []

        for result in search_results:
            document = result["document"]

            sources.append(
                {
                    "document_id": document.id,
                    "document_type": document.document_type,
                    "document_number": document.document_number,
                    "status": document.status,
                    "product_full_name": document.product_full_name,
                    "final_score": result["final_score"],
                }
            )

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
        }

    @staticmethod
    def _build_context(search_results: list[dict]) -> str:
        if not search_results:
            return "Документы по запросу не найдены."

        context_parts = []

        for index, result in enumerate(search_results, start=1):
            document = result["document"]

            context_parts.append(
                "\n".join(
                    [
                        f"Документ {index}:",
                        f"ID: {document.id}",
                        f"Тип документа: {document.document_type}",
                        f"Номер документа: {document.document_number}",
                        f"Статус: {document.status}",
                        f"Заявитель: {document.applicant_name}",
                        f"Изготовитель: {document.manufacturer_name}",
                        f"Продукция: {document.product_full_name}",
                        f"Коды продукции: {document.product_codes}",
                        f"Технические регламенты: {document.technical_regulations}",
                        f"Итоговая оценка поиска: {result['final_score']}",
                    ]
                )
            )

        return "\n\n".join(context_parts)