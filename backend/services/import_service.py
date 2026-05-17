from __future__ import annotations

import csv
from datetime import UTC, datetime
from pathlib import Path
from typing import TextIO

from sqlalchemy.orm import Session

from backend.db.models.import_batch import ImportBatch
from backend.db.models.registry_document import RegistryDocument
from backend.external.csv_mapper import map_row_to_document_data
from backend.repositories.document_repository import DocumentRepository
from backend.repositories.import_batch_repository import ImportBatchRepository


class ImportService:
    def __init__(
        self,
        db: Session,
        import_batch_repository: ImportBatchRepository | None = None,
        document_repository: DocumentRepository | None = None,
    ) -> None:
        self.db = db
        self.import_batch_repository = import_batch_repository or ImportBatchRepository(db)
        self.document_repository = document_repository or DocumentRepository(db)

    def import_csv(
        self,
        file_path: str | Path,
        document_type: str,
        limit: int | None = None,
        source_name: str = "Росаккредитация Open Data",
    ) -> ImportBatch:
        path = Path(file_path)

        self._validate_document_type(document_type)
        self._validate_limit(limit)

        batch = self.import_batch_repository.create(
            ImportBatch(
                source_name=source_name,
                source_file_name=path.name,
                document_type=document_type,
                status="running",
                started_at=datetime.now(UTC),
                total_rows=0,
                processed_rows=0,
                failed_rows=0,
                error_message=None,
            )
        )

        try:
            if not path.exists():
                raise FileNotFoundError(f"Файл не найден: {path.resolve()}")

            total_rows = 0
            processed_rows = 0
            failed_rows = 0

            with path.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file, dialect=self._detect_csv_dialect(file))

                for row in reader:
                    if limit is not None and total_rows >= limit:
                        break

                    total_rows += 1
                    current_row_number = total_rows
                    document_number: str | None = None

                    try:
                        document_data = map_row_to_document_data(
                            row=row,
                            document_type=document_type,
                            import_batch_id=batch.id,
                        )

                        document_number = document_data.get("document_number")

                        if document_number:
                            existing_document = (
                                self.document_repository.get_by_document_number_and_type(
                                    document_number=document_number,
                                    document_type=document_type,
                                )
                            )

                            if existing_document is not None:
                                processed_rows += 1
                                continue

                        document = RegistryDocument(**document_data)
                        self.document_repository.create(document)
                        processed_rows += 1

                    except Exception as exc:
                        self.db.rollback()
                        failed_rows += 1
                        print(self._format_row_error(
                            row_number=current_row_number,
                            document_type=document_type,
                            document_number=document_number,
                            exc=exc,
                        ))

            batch.total_rows = total_rows
            batch.processed_rows = processed_rows
            batch.failed_rows = failed_rows
            batch.status = "completed"
            batch.finished_at = datetime.now(UTC)
            batch.error_message = None
            return self.import_batch_repository.update(batch)

        except Exception as exc:
            self.db.rollback()
            batch.status = "failed"
            batch.finished_at = datetime.now(UTC)
            batch.error_message = self._format_batch_error(exc)
            return self.import_batch_repository.update(batch)

    def import_file(
        self,
        file_path: str | Path,
        document_type: str,
        limit: int | None = None,
        source_name: str = "Росаккредитация Open Data",
    ) -> ImportBatch:
        return self.import_csv(
            file_path=file_path,
            document_type=document_type,
            limit=limit,
            source_name=source_name,
        )

    @staticmethod
    def _validate_document_type(document_type: str) -> None:
        if document_type not in {"declaration", "certificate"}:
            raise ValueError(f"Unsupported document_type: {document_type}")

    @staticmethod
    def _validate_limit(limit: int | None) -> None:
        if limit is not None and limit < 0:
            raise ValueError("limit must be greater than or equal to 0")

    @staticmethod
    def _detect_csv_dialect(file: TextIO) -> type[csv.Dialect] | csv.Dialect:
        sample = file.read(4096)
        file.seek(0)

        try:
            return csv.Sniffer().sniff(sample, delimiters=",;")
        except csv.Error:
            return csv.excel

    @staticmethod
    def _format_batch_error(exc: Exception) -> str:
        if isinstance(exc, (FileNotFoundError, ValueError)):
            return str(exc)

        return f"{type(exc).__name__}: операция импорта завершилась с ошибкой"

    @staticmethod
    def _format_row_error(
        row_number: int,
        document_type: str,
        document_number: str | None,
        exc: Exception,
    ) -> str:
        reason_source = getattr(exc, "orig", exc)
        reason = str(reason_source).replace("\n", " ").strip()
        reason = reason[:300]

        return (
            f"Ошибка строки {row_number}: "
            f"document_type={document_type}, "
            f"document_number={document_number}, "
            f"error={type(exc).__name__}, "
            f"reason={reason}"
        )
