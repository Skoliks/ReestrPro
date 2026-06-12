import argparse
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.db.session import SessionLocal
from backend.external.archive_extractor import extract_7z_archive
from backend.services.embedding_service import EmbeddingService
from backend.services.import_service import ImportService


EXTRACTED_DIR_BY_TYPE = {
    "declaration": Path("backend/data/extracted/declarations"),
    "certificate": Path("backend/data/extracted/certificates"),
}


def find_first_csv(files: list[Path]) -> Path:
    csv_files = [
        file
        for file in files
        if file.is_file() and file.suffix.lower() == ".csv"
    ]

    if not csv_files:
        raise FileNotFoundError("CSV file was not found after archive extraction")

    return csv_files[0]


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract archive, import CSV and generate embeddings"
    )

    parser.add_argument(
        "--archive",
        required=True,
        help="Path to .7z archive",
    )

    parser.add_argument(
        "--type",
        required=True,
        choices=["declaration", "certificate"],
        help="Document type: declaration or certificate",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="How many CSV rows to import",
    )

    args = parser.parse_args()

    archive_path = Path(args.archive)
    document_type = args.type
    output_dir = EXTRACTED_DIR_BY_TYPE[document_type]

    print("Starting archive processing")
    print(f"Archive: {archive_path}")
    print(f"Document type: {document_type}")
    print(f"Extract directory: {output_dir}")

    extracted_files = extract_7z_archive(
        archive_path=archive_path,
        output_dir=output_dir,
    )

    csv_file = find_first_csv(extracted_files)

    print("Archive extracted")
    print(f"CSV file: {csv_file}")

    async with SessionLocal() as db:
        import_service = ImportService(db)

        batch = await import_service.import_csv(
            file_path=csv_file,
            document_type=document_type,
            limit=args.limit,
            source_name="Rosakkreditatsiya Open Data Archive",
        )

        print("Import completed")
        print(f"Batch ID: {batch.id}")
        print(f"Status: {batch.status}")
        print(f"Total rows: {batch.total_rows}")
        print(f"Processed rows: {batch.processed_rows}")
        print(f"Added rows: {getattr(batch, 'added_rows', 'unknown')}")
        print(f"Duplicate rows skipped: {getattr(batch, 'duplicate_rows', 'unknown')}")
        print(f"Failed rows: {batch.failed_rows}")

        embedding_service = EmbeddingService(db)

        embedding_result = await embedding_service.generate_for_import_batch(
            import_batch_id=batch.id,
            limit=batch.processed_rows,
        )

        print("Embedding generation completed")
        print(f"Total documents selected: {embedding_result['total_documents']}")
        print(f"Created embeddings: {embedding_result['created']}")
        print(f"Skipped: {embedding_result['skipped']}")


if __name__ == "__main__":
    asyncio.run(main())
