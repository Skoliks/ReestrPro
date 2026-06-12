import asyncio
from datetime import UTC, datetime

from backend.db.models.import_batch import ImportBatch
from backend.db.models.registry_document import RegistryDocument
from backend.db.session import SessionLocal
from backend.repositories.document_repository import DocumentRepository
from backend.repositories.import_batch_repository import ImportBatchRepository


async def main() -> None:
    async with SessionLocal() as db:
        batch_repo = ImportBatchRepository(db)
        document_repo = DocumentRepository(db)

        batch = ImportBatch(
            source_name="test",
            source_file_name="test.csv",
            document_type="declaration",
            status="running",
            started_at=datetime.now(UTC),
        )

        batch = await batch_repo.create(batch)

        document = RegistryDocument(
            import_batch_id=batch.id,
            source_document_id="test-1",
            document_type="declaration",
            document_number="TEST-123",
            status="active",
            product_full_name="Test product",
            raw_data={"test": "value"},
            search_text="Test document TEST-123",
        )

        document = await document_repo.create(document)
        found_document = await document_repo.get_by_id(document.id)

        print("batch id:", batch.id)
        print("document id:", document.id)
        print(
            "found document number:",
            found_document.document_number if found_document else None,
        )


if __name__ == "__main__":
    asyncio.run(main())
