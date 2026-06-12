import argparse
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.db.session import SessionLocal
from backend.services.import_service import ImportService


async def main() -> None:
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

    async with SessionLocal() as db:
        service = ImportService(db)

        batch = await service.import_csv(
            file_path=args.file,
            document_type=args.type,
            limit=args.limit,
        )

        print("Импорт завершён")
        print(f"Batch ID: {batch.id}")
        print(f"Status: {batch.status}")
        print(f"Total rows: {batch.total_rows}")
        print(f"Processed rows: {batch.processed_rows}")
        print(f"Added rows: {getattr(batch, 'added_rows', 'unknown')}")
        print(f"Duplicate rows skipped: {getattr(batch, 'duplicate_rows', 'unknown')}")
        print(f"Failed rows: {batch.failed_rows}")

        if batch.error_message:
            print(f"Error: {batch.error_message}")


if __name__ == "__main__":
    asyncio.run(main())
