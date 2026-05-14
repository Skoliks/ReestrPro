from backend.db.session import SessionLocal
from backend.services.embedding_service import EmbeddingService


def main() -> None:
    db = SessionLocal()

    try:
        service = EmbeddingService(db)

        query = "детская одежда"
        results = service.semantic_search(query=query, limit=5)

        print(f"Запрос: {query}")
        print("Результаты:")

        for document, score in results:
            print("-" * 80)
            print(f"ID: {document.id}")
            print(f"Тип: {document.document_type}")
            print(f"Номер: {document.document_number}")
            print(f"Статус: {document.status}")
            print(f"Продукция: {document.product_full_name}")
            print(f"Score: {score}")

    finally:
        db.close()


if __name__ == "__main__":
    main()