import argparse
import shutil
from pathlib import Path

from backend.external.archive_extractor import extract_7z_archive
from backend.external.fsa_client import (
    download_archive,
    find_latest_archive_link,
    get_open_data_page_url,
)

DEFAULT_ARCHIVE_OUTPUT_PATHS = {
    "declaration": Path("backend/data/raw/declarations/latest_declaration.7z"),
    "certificate": Path("backend/data/raw/certificates/latest_certificate.7z"),
}

EXTRACTED_DIR_BY_TYPE = {
    "declaration": Path("backend/data/extracted/declarations"),
    "certificate": Path("backend/data/extracted/certificates"),
}


def get_default_archive_output_path(document_type: str) -> Path:
    output_path = DEFAULT_ARCHIVE_OUTPUT_PATHS.get(document_type)

    if output_path is None:
        raise ValueError("document_type должен быть declaration или certificate")

    return output_path


def get_extracted_output_dir(document_type: str) -> Path:
    output_dir = EXTRACTED_DIR_BY_TYPE.get(document_type)

    if output_dir is None:
        raise ValueError("document_type должен быть declaration или certificate")

    return output_dir


def reset_output_dir(output_dir: str | Path) -> Path:
    target_dir = Path(output_dir)

    if target_dir.exists():
        shutil.rmtree(target_dir)

    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def find_first_csv(files: list[Path]) -> Path:
    csv_files = sorted(
        file for file in files
        if file.is_file() and file.suffix.lower() == ".csv"
    )

    if not csv_files:
        raise FileNotFoundError("После распаковки не найден CSV-файл")

    return csv_files[0]


def build_batch_report(batch: object) -> dict[str, object]:
    return {
        "batch_id": getattr(batch, "id"),
        "status": getattr(batch, "status"),
        "total_rows": getattr(batch, "total_rows"),
        "processed_rows": getattr(batch, "processed_rows"),
        "failed_rows": getattr(batch, "failed_rows"),
        "error_message": getattr(batch, "error_message"),
    }


def sync_open_data(
    document_type: str,
    limit: int | None = None,
    output_path: str | Path | None = None,
    keep_extracted: bool = False,
) -> dict[str, object]:
    from backend.db.session import SessionLocal
    from backend.services.embedding_service import EmbeddingService
    from backend.services.import_service import ImportService

    page_url = get_open_data_page_url(document_type)
    archive_url = find_latest_archive_link(document_type)
    archive_output_path = (
        Path(output_path)
        if output_path is not None
        else get_default_archive_output_path(document_type)
    )
    extracted_output_dir = get_extracted_output_dir(document_type)

    print("Начинаю синхронизацию открытых данных Росаккредитации")
    print(f"Тип документов: {document_type}")
    print(f"Страница открытых данных: {page_url}")

    if limit is None:
        print()
        print(
            "Внимание: параметр --limit не указан. Будет выполнен импорт всего CSV-файла. "
            "Это может занять значительное время."
        )
    else:
        print()
        print(f"Тестовый режим: будет импортировано не более {limit} строк.")

    print()
    print(f"Найдена актуальная ссылка: {archive_url}")
    print(f"Архив будет сохранён в: {archive_output_path}")

    downloaded_archive_path = download_archive(
        url=archive_url,
        output_path=archive_output_path,
    )

    print("Архив скачан")

    if keep_extracted:
        extracted_output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Папка распаковки сохранена без очистки: {extracted_output_dir}")
    else:
        reset_output_dir(extracted_output_dir)
        print(f"Папка распаковки очищена: {extracted_output_dir}")

    extracted_files = extract_7z_archive(
        archive_path=downloaded_archive_path,
        output_dir=extracted_output_dir,
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
            limit=limit,
            source_name="Росаккредитация Open Data Sync",
        )
        batch_report = build_batch_report(batch)

        embedding_service = EmbeddingService(db)
        embedding_result = embedding_service.generate_for_import_batch(
            import_batch_id=batch_report["batch_id"],
            limit=batch_report["processed_rows"],
        )

    finally:
        db.close()

    return {
        "document_type": document_type,
        "page_url": page_url,
        "archive_url": archive_url,
        "archive_path": downloaded_archive_path,
        "extracted_dir": extracted_output_dir,
        "csv_file": csv_file,
        "batch_id": batch_report["batch_id"],
        "status": batch_report["status"],
        "total_rows": batch_report["total_rows"],
        "processed_rows": batch_report["processed_rows"],
        "failed_rows": batch_report["failed_rows"],
        "embeddings_total_documents": embedding_result["total_documents"],
        "embeddings_created": embedding_result["created"],
        "embeddings_skipped": embedding_result["skipped"],
        "error_message": batch_report["error_message"],
    }


def print_sync_report(report: dict[str, object]) -> None:
    print()
    print("Итоговый отчёт")
    print(f"Тип документов: {report['document_type']}")
    print(f"Страница открытых данных: {report['page_url']}")
    print(f"Актуальная ссылка: {report['archive_url']}")
    print(f"Путь к скачанному архиву: {report['archive_path']}")
    print(f"Папка распаковки: {report['extracted_dir']}")
    print(f"Найденный CSV-файл: {report['csv_file']}")
    print(f"batch_id: {report['batch_id']}")
    print(f"status: {report['status']}")
    print(f"total_rows: {report['total_rows']}")
    print(f"processed_rows: {report['processed_rows']}")
    print(f"failed_rows: {report['failed_rows']}")
    print(f"embeddings_total_documents: {report['embeddings_total_documents']}")
    print(f"embeddings_created: {report['embeddings_created']}")
    print(f"embeddings_skipped: {report['embeddings_skipped']}")

    error_message = report.get("error_message")

    if error_message:
        print(f"Error message: {error_message}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Полная административная синхронизация открытых данных Росаккредитации"
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
        help="Сколько строк импортировать из CSV для тестовой загрузки",
    )

    parser.add_argument(
        "--output",
        default=None,
        help="Путь, куда нужно сохранить скачанный архив",
    )

    parser.add_argument(
        "--keep-extracted",
        action="store_true",
        help="Не очищать папку распаковки перед распаковкой архива",
    )

    args = parser.parse_args()

    report = sync_open_data(
        document_type=args.type,
        limit=args.limit,
        output_path=args.output,
        keep_extracted=args.keep_extracted,
    )
    print_sync_report(report)


if __name__ == "__main__":
    main()
