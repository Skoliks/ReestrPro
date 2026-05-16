import argparse
from pathlib import Path

from backend.db.session import SessionLocal
from backend.external.archive_extractor import extract_7z_archive
from backend.services.embedding_service import EmbeddingService
from backend.services.import_service import ImportService


EXTRACTED_DIR_BY_TYPE = {
    "declaration": Path("backend/data/extracted/declarations"),
    "certificate": Path("backend/data/extracted/certificates"),
}


def find_first_csv(files: list[Path]) -> Path:
    csv_files = [file for file in files if file.is_file() and file.suffix.lower() == ".csv"]

    if not csv_files:
        raise FileNotFoundError("После распаковки не найден CSV-файл")

    return csv_files[0]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Распаковка архива, импорт CSV и генерация embeddings"
    )

    parser.add_argument(
        "--archive",
        required=True,
        help="Путь к .7z архиву",
    )

    parser.add_argument(
        "--type",
        required=True,
        choices=["declaration", "certificate"],
        help="Тип документов: declaration или certificate",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Сколько строк импортировать из CSV",
    )

    args = parser.parse_args()

    archive_path = Path(args.archive)
    document_type = args.type
    output_dir = EXTRACTED_DIR_BY_TYPE[document_type]

    print("Начинаю обработку архива")
    print(f"Архив: {archive_path}")
    print(f"Тип документов: {document_type}")
    print(f"Папка распаковки: {output_dir}")

    extracted_files = extract_7z_archive(
        archive_path=archive_path,
        output_dir=output_dir,
    )

    csv_file = find_first_csv(extracted_files)

    print("Архив распакован")
    print(f"Найден CSV-файл: {csv_file}")

    db = SessionLocal()

    try:
        import_service = ImportService(db)

        batch = import_service.import_csv(
            file_path=csv_file,
            document_type=document_type,
            limit=args.limit,
            source_name="Росаккредитация Open Data Archive",
        )

        print("Импорт завершён")
        print(f"Batch ID: {batch.id}")
        print(f"Status: {batch.status}")
        print(f"Total rows: {batch.total_rows}")
        print(f"Processed rows: {batch.processed_rows}")
        print(f"Failed rows: {batch.failed_rows}")

        embedding_service = EmbeddingService(db)

        embedding_result = embedding_service.generate_for_import_batch(
        import_batch_id=batch.id,
        limit=batch.processed_rows,
    )

        print("Генерация embeddings завершена")
        print(f"Всего документов взято: {embedding_result['total_documents']}")
        print(f"Создано embeddings: {embedding_result['created']}")
        print(f"Пропущено: {embedding_result['skipped']}")

    finally:
        db.close()


if __name__ == "__main__":
    main()