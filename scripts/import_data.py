import argparse

from backend.db.session import SessionLocal
from backend.services.import_service import ImportService


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Импорт сертификатов и деклараций из CSV"
    )

    parser.add_argument(
        "--file",
        required=True,
        help="Путь к CSV-файлу",
    )

    parser.add_argument(
        "--type",
        required=True,
        choices=["declaration", "certificate"],
        help="Тип документа: declaration или certificate",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Сколько строк импортировать. Например: 10",
    )

    args = parser.parse_args()

    db = SessionLocal()

    try:
        service = ImportService(db)

        batch = service.import_csv(
            file_path=args.file,
            document_type=args.type,
            limit=args.limit,
        )

        print("Импорт завершён")
        print(f"Batch ID: {batch.id}")
        print(f"Status: {batch.status}")
        print(f"Total rows: {batch.total_rows}")
        print(f"Processed rows: {batch.processed_rows}")
        print(f"Failed rows: {batch.failed_rows}")

        if batch.error_message:
            print(f"Error: {batch.error_message}")

    finally:
        db.close()


if __name__ == "__main__":
    main()