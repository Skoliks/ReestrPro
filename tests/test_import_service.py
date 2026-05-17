from pathlib import Path

import pytest

from backend.db.models.import_batch import ImportBatch
from backend.services.import_service import ImportService


class FakeDB:
    def __init__(self) -> None:
        self.rollback_calls = 0

    def rollback(self) -> None:
        self.rollback_calls += 1


class FakeImportBatchRepository:
    def __init__(self) -> None:
        self.next_id = 1

    def create(self, batch: ImportBatch) -> ImportBatch:
        batch.id = self.next_id
        self.next_id += 1
        return batch

    def update(self, batch: ImportBatch) -> ImportBatch:
        return batch


class FakeDocumentRepository:
    def __init__(self, existing_documents: dict[tuple[str, str], object] | None = None) -> None:
        self.existing_documents = existing_documents or {}
        self.lookup_calls: list[tuple[str, str]] = []
        self.created_documents = []

    def get_by_document_number_and_type(
        self,
        document_number: str,
        document_type: str,
    ) -> object | None:
        self.lookup_calls.append((document_number, document_type))
        return self.existing_documents.get((document_number, document_type))

    def create(self, document):
        self.created_documents.append(document)
        return document


def write_csv(path: Path, row_ids: list[str]) -> None:
    lines = ["id"] + row_ids
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_import_csv_skips_duplicate_documents(monkeypatch, tmp_path: Path):
    csv_path = tmp_path / "documents.csv"
    write_csv(csv_path, ["duplicate-row"])

    def fake_map_row_to_document_data(row, document_type, import_batch_id):
        assert row["id"] == "duplicate-row"
        return {
            "import_batch_id": import_batch_id,
            "source_document_id": row["id"],
            "document_type": document_type,
            "document_number": "DECL-001",
            "status": "active",
            "search_text": "duplicate document",
            "raw_data": row,
        }

    monkeypatch.setattr(
        "backend.services.import_service.map_row_to_document_data",
        fake_map_row_to_document_data,
    )

    db = FakeDB()
    document_repository = FakeDocumentRepository(
        existing_documents={("DECL-001", "declaration"): object()}
    )
    service = ImportService(
        db=db,
        import_batch_repository=FakeImportBatchRepository(),
        document_repository=document_repository,
    )

    batch = service.import_csv(csv_path, document_type="declaration")

    assert batch.status == "completed"
    assert batch.total_rows == 1
    assert batch.processed_rows == 1
    assert batch.failed_rows == 0
    assert db.rollback_calls == 0
    assert document_repository.lookup_calls == [("DECL-001", "declaration")]
    assert document_repository.created_documents == []


def test_import_csv_creates_new_and_missing_number_documents(monkeypatch, tmp_path: Path):
    csv_path = tmp_path / "documents.csv"
    write_csv(csv_path, ["new-row", "missing-number-row"])

    mapped_rows = {
        "new-row": {
            "document_number": "DECL-002",
            "search_text": "new document",
        },
        "missing-number-row": {
            "document_number": None,
            "search_text": "missing number document",
        },
    }

    def fake_map_row_to_document_data(row, document_type, import_batch_id):
        mapped_row = mapped_rows[row["id"]]
        return {
            "import_batch_id": import_batch_id,
            "source_document_id": row["id"],
            "document_type": document_type,
            "document_number": mapped_row["document_number"],
            "status": "active",
            "search_text": mapped_row["search_text"],
            "raw_data": row,
        }

    monkeypatch.setattr(
        "backend.services.import_service.map_row_to_document_data",
        fake_map_row_to_document_data,
    )

    db = FakeDB()
    document_repository = FakeDocumentRepository()
    service = ImportService(
        db=db,
        import_batch_repository=FakeImportBatchRepository(),
        document_repository=document_repository,
    )

    batch = service.import_csv(csv_path, document_type="declaration")

    assert batch.status == "completed"
    assert batch.total_rows == 2
    assert batch.processed_rows == 2
    assert batch.failed_rows == 0
    assert db.rollback_calls == 0
    assert document_repository.lookup_calls == [("DECL-002", "declaration")]
    assert len(document_repository.created_documents) == 2
    assert document_repository.created_documents[0].document_number == "DECL-002"
    assert document_repository.created_documents[1].document_number is None


def write_document_csv(path: Path, delimiter: str) -> None:
    path.write_text(
        delimiter.join(["id", "Номер ДС", "Статус", "Полное наименование"]) + "\n"
        + delimiter.join(["row-1", "DECL-100", "Действует", "Тестовая продукция"]) + "\n",
        encoding="utf-8",
    )


@pytest.mark.parametrize("delimiter", [",", ";"])
def test_import_csv_reads_comma_and_semicolon_delimited_files(
    monkeypatch,
    tmp_path: Path,
    delimiter: str,
):
    csv_path = tmp_path / f"documents_{ord(delimiter)}.csv"
    write_document_csv(csv_path, delimiter)

    captured_rows: list[dict[str, str]] = []

    def fake_map_row_to_document_data(row, document_type, import_batch_id):
        captured_rows.append(row)
        return {
            "import_batch_id": import_batch_id,
            "source_document_id": row["id"],
            "document_type": document_type,
            "document_number": row["Номер ДС"],
            "status": row["Статус"],
            "product_full_name": row["Полное наименование"],
            "search_text": row["Полное наименование"],
            "raw_data": row,
        }

    monkeypatch.setattr(
        "backend.services.import_service.map_row_to_document_data",
        fake_map_row_to_document_data,
    )

    db = FakeDB()
    document_repository = FakeDocumentRepository()
    service = ImportService(
        db=db,
        import_batch_repository=FakeImportBatchRepository(),
        document_repository=document_repository,
    )

    batch = service.import_csv(csv_path, document_type="declaration")

    assert batch.status == "completed"
    assert batch.total_rows == 1
    assert batch.processed_rows == 1
    assert batch.failed_rows == 0
    assert db.rollback_calls == 0
    assert len(captured_rows) == 1
    assert captured_rows[0]["id"] == "row-1"
    assert captured_rows[0]["Номер ДС"] == "DECL-100"
    assert captured_rows[0]["Статус"] == "Действует"
    assert captured_rows[0]["Полное наименование"] == "Тестовая продукция"
    assert len(document_repository.created_documents) == 1
    assert document_repository.created_documents[0].document_number == "DECL-100"
    assert document_repository.created_documents[0].status == "Действует"
    assert (
        document_repository.created_documents[0].product_full_name
        == "Тестовая продукция"
    )


def test_import_csv_with_limit_one_does_not_import_second_row_after_first_row_error(
    monkeypatch,
    tmp_path: Path,
    capsys,
):
    csv_path = tmp_path / "documents.csv"
    csv_path.write_text(
        "id,Номер ДС,Статус\n"
        "row-1,DECL-ERROR,Ошибка\n"
        "row-2,DECL-OK,Действует\n",
        encoding="utf-8",
    )

    def fake_map_row_to_document_data(row, document_type, import_batch_id):
        if row["id"] == "row-1":
            return {
                "import_batch_id": import_batch_id,
                "source_document_id": row["id"],
                "document_type": document_type,
                "document_number": row["Номер ДС"],
                "status": row["Статус"],
                "search_text": "broken document",
                "raw_data": row,
            }

        return {
            "import_batch_id": import_batch_id,
            "source_document_id": row["id"],
            "document_type": document_type,
            "document_number": row["Номер ДС"],
            "status": row["Статус"],
            "search_text": "ok document",
            "raw_data": row,
        }

    monkeypatch.setattr(
        "backend.services.import_service.map_row_to_document_data",
        fake_map_row_to_document_data,
    )

    db = FakeDB()
    document_repository = FakeDocumentRepository()

    def fake_create(document):
        if document.document_number == "DECL-ERROR":
            error = Exception("insert failed")
            error.orig = Exception("invalid input syntax for type date")
            raise error

        document_repository.created_documents.append(document)
        return document

    document_repository.create = fake_create

    service = ImportService(
        db=db,
        import_batch_repository=FakeImportBatchRepository(),
        document_repository=document_repository,
    )

    batch = service.import_csv(csv_path, document_type="declaration", limit=1)
    captured = capsys.readouterr()

    assert batch.status == "completed"
    assert batch.total_rows == 1
    assert batch.failed_rows == 1
    assert batch.processed_rows == 0
    assert db.rollback_calls == 1
    assert document_repository.created_documents == []
    assert "Ошибка строки 1:" in captured.out
    assert "document_type=declaration" in captured.out
    assert "document_number=DECL-ERROR" in captured.out
    assert "reason=invalid input syntax for type date" in captured.out
