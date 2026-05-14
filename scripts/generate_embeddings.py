import argparse

from backend.db.session import SessionLocal
from backend.services.embedding_service import EmbeddingService


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Генерация embeddings для документов"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Сколько документов обработать",
    )

    args = parser.parse_args()

    db = SessionLocal()

    try:
        service = EmbeddingService(db)
        result = service.generate_for_documents(limit=args.limit)

        print("Генерация embeddings завершена")
        print(f"Всего документов взято: {result['total_documents']}")
        print(f"Создано embeddings: {result['created']}")
        print(f"Пропущено: {result['skipped']}")

    finally:
        db.close()


if __name__ == "__main__":
    main()