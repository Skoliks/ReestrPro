import asyncio

from backend.db.session import SessionLocal
from backend.services.embedding_service import EmbeddingService


async def main() -> None:
    async with SessionLocal() as db:
        service = EmbeddingService(db)

        query = "детская одежда"
        results = await service.semantic_search(query=query, limit=5)

        print(f"Query: {query}")
        print("Results:")

        for document, score in results:
            print("-" * 80)
            print(f"ID: {document.id}")
            print(f"Type: {document.document_type}")
            print(f"Number: {document.document_number}")
            print(f"Status: {document.status}")
            print(f"Product: {document.product_full_name}")
            print(f"Score: {score}")


if __name__ == "__main__":
    asyncio.run(main())
