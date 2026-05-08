from datetime import UTC, datetime

from backend.db.models.import_batch import ImportBatch
from backend.db.models.registry_document import RegistryDocument
from backend.db.session import SessionLocal
from backend.repositories.document_repository import DocumentRepository
from backend.repositories.import_batch_repository import ImportBatchRepository


db = SessionLocal()

try:
    batch_repo = ImportBatchRepository(db)
    document_repo = DocumentRepository(db)

    batch = ImportBatch(
        source_name="test",
        source_file_name="test.csv",
        document_type="declaration",
        status="running",
        started_at=datetime.now(UTC),
    )

    batch = batch_repo.create(batch)

    document = RegistryDocument(
        import_batch_id=batch.id,
        source_document_id="test-1",
        document_type="declaration",
        document_number="TEST-123",
        status="Действует",
        product_full_name="Тестовая продукция",
        raw_data={"test": "value"},
        search_text="Тестовый документ TEST-123",
    )

    document = document_repo.create(document)

    found_document = document_repo.get_by_id(document.id)

    print("batch id:", batch.id)
    print("document id:", document.id)
    print("found document number:", found_document.document_number if found_document else None)

finally:
    db.close()