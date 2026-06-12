from __future__ import annotations

import csv
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import TextIO

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.db.models.import_batch import ImportBatch
from backend.db.models.registry_document import RegistryDocument
from backend.external.csv_mapper import map_row_to_document_data
from backend.repositories.document_repository import DocumentRepository
from backend.repositories.import_batch_repository import ImportBatchRepository

logger = get_logger(__name__)

DEFAULT_IMPORT_BATCH_SIZE = 500
DEFAULT_PROGRESS_LOG_INTERVAL = 1_000
DEFAULT_SOURCE_NAME = "Rosakkreditatsiya Open Data"


class ImportService:
    def __init__(
        self,
        db: AsyncSession,
        import_batch_repository: ImportBatchRepository | None = None,
        document_repository: DocumentRepository | None = None,
    ) -> None:
        self.db = db
        self.import_batch_repository = import_batch_repository or ImportBatchRepository(db)
        self.document_repository = document_repository or DocumentRepository(db)

    async def import_csv(
        self,
        file_path: str | Path,
        document_type: str,
        limit: int | None = None,
        source_name: str = DEFAULT_SOURCE_NAME,
        batch_size: int = DEFAULT_IMPORT_BATCH_SIZE,
    ) -> ImportBatch:
        path = Path(file_path)

        self._validate_document_type(document_type)
        self._validate_limit(limit)
        self._validate_batch_size(batch_size)
        logger.info(
            "Starting CSV import: file=%s document_type=%s limit=%s batch_size=%s",
            path,
            document_type,
            limit,
            batch_size,
        )

        batch = await self.import_batch_repository.create(
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
                raise FileNotFoundError(f"File was not found: {path.resolve()}")

            total_rows = 0
            processed_rows = 0
            failed_rows = 0
            added_rows = 0
            duplicate_rows = 0
            pending_documents: list[tuple[RegistryDocument, int, str | None]] = []

            with path.open("r", encoding="utf-8-sig", newline="") as file:
                self._increase_csv_field_size_limit()
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
                                await self.document_repository.get_by_document_number_and_type(
                                    document_number=document_number,
                                    document_type=document_type,
                                )
                            )

                            if existing_document is not None:
                                processed_rows += 1
                                duplicate_rows += 1
                                self._log_progress(
                                    total_rows=total_rows,
                                    processed_rows=processed_rows,
                                    added_rows=added_rows,
                                    duplicate_rows=duplicate_rows,
                                    failed_rows=failed_rows,
                                )
                                continue

                        document = RegistryDocument(**document_data)
                        pending_documents.append(
                            (document, current_row_number, document_number)
                        )

                        if len(pending_documents) >= batch_size:
                            added_now, failed_now = await self._flush_pending_documents(
                                pending_documents=pending_documents,
                                document_type=document_type,
                            )
                            pending_documents.clear()
                            added_rows += added_now
                            failed_rows += failed_now
                            processed_rows += added_now

                    except Exception as exc:
                        await self.db.rollback()
                        failed_rows += 1
                        row_error = self._format_row_error(
                            row_number=current_row_number,
                            document_type=document_type,
                            document_number=document_number,
                            exc=exc,
                        )
                        logger.warning(row_error)
                        print(row_error)

                    self._log_progress(
                        total_rows=total_rows,
                        processed_rows=processed_rows,
                        added_rows=added_rows,
                        duplicate_rows=duplicate_rows,
                        failed_rows=failed_rows,
                    )

                if pending_documents:
                    added_now, failed_now = await self._flush_pending_documents(
                        pending_documents=pending_documents,
                        document_type=document_type,
                    )
                    added_rows += added_now
                    failed_rows += failed_now
                    processed_rows += added_now

            batch.total_rows = total_rows
            batch.processed_rows = processed_rows
            batch.failed_rows = failed_rows
            batch.status = "completed"
            batch.finished_at = datetime.now(UTC)
            batch.error_message = None
            self._set_runtime_counters(
                batch=batch,
                added_rows=added_rows,
                duplicate_rows=duplicate_rows,
            )
            logger.info(
                (
                    "CSV import completed: batch_id=%s total=%s processed=%s "
                    "added=%s duplicates=%s failed=%s"
                ),
                batch.id,
                total_rows,
                processed_rows,
                added_rows,
                duplicate_rows,
                failed_rows,
            )
            return await self.import_batch_repository.update(batch)

        except Exception as exc:
            await self.db.rollback()
            batch.status = "failed"
            batch.finished_at = datetime.now(UTC)
            batch.error_message = self._format_batch_error(exc)
            self._set_runtime_counters(
                batch=batch,
                added_rows=0,
                duplicate_rows=0,
            )
            logger.exception(
                "CSV import failed: batch_id=%s file=%s document_type=%s",
                batch.id,
                path,
                document_type,
            )
            return await self.import_batch_repository.update(batch)

    async def import_file(
        self,
        file_path: str | Path,
        document_type: str,
        limit: int | None = None,
        source_name: str = DEFAULT_SOURCE_NAME,
        batch_size: int = DEFAULT_IMPORT_BATCH_SIZE,
    ) -> ImportBatch:
        return await self.import_csv(
            file_path=file_path,
            document_type=document_type,
            limit=limit,
            source_name=source_name,
            batch_size=batch_size,
        )

    async def _flush_pending_documents(
        self,
        pending_documents: list[tuple[RegistryDocument, int, str | None]],
        document_type: str,
    ) -> tuple[int, int]:
        documents = [document for document, _, _ in pending_documents]

        try:
            await self.document_repository.create_many(documents)
            return len(documents), 0

        except Exception as exc:
            await self.db.rollback()
            logger.warning(
                "Batch insert failed, retrying row by row: count=%s error=%s",
                len(documents),
                exc,
            )

        added_rows = 0
        failed_rows = 0

        for document, row_number, document_number in pending_documents:
            try:
                await self.document_repository.create(document)
                added_rows += 1
            except Exception as exc:
                await self.db.rollback()
                failed_rows += 1
                row_error = self._format_row_error(
                    row_number=row_number,
                    document_type=document_type,
                    document_number=document_number,
                    exc=exc,
                )
                logger.warning(row_error)
                print(row_error)

        return added_rows, failed_rows

    @staticmethod
    def _validate_document_type(document_type: str) -> None:
        if document_type not in {"declaration", "certificate"}:
            raise ValueError(f"Unsupported document_type: {document_type}")

    @staticmethod
    def _validate_limit(limit: int | None) -> None:
        if limit is not None and limit < 0:
            raise ValueError("limit must be greater than or equal to 0")

    @staticmethod
    def _validate_batch_size(batch_size: int) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than 0")

    @staticmethod
    def _set_runtime_counters(
        batch: ImportBatch,
        added_rows: int,
        duplicate_rows: int,
    ) -> None:
        batch.added_rows = added_rows
        batch.duplicate_rows = duplicate_rows

    @staticmethod
    def _log_progress(
        total_rows: int,
        processed_rows: int,
        added_rows: int,
        duplicate_rows: int,
        failed_rows: int,
    ) -> None:
        if total_rows == 0 or total_rows % DEFAULT_PROGRESS_LOG_INTERVAL != 0:
            return

        logger.info(
            (
                "CSV import progress: read=%s processed=%s added=%s "
                "duplicates=%s failed=%s"
            ),
            total_rows,
            processed_rows,
            added_rows,
            duplicate_rows,
            failed_rows,
        )

    @staticmethod
    def _detect_csv_dialect(file: TextIO) -> type[csv.Dialect] | csv.Dialect:
        sample = file.read(4096)
        file.seek(0)

        try:
            return csv.Sniffer().sniff(sample, delimiters=",;")
        except csv.Error:
            return csv.excel

    @staticmethod
    def _increase_csv_field_size_limit() -> None:
        max_size = sys.maxsize

        while True:
            try:
                csv.field_size_limit(max_size)
                break
            except OverflowError:
                max_size = int(max_size / 10)

    @staticmethod
    def _format_batch_error(exc: Exception) -> str:
        if isinstance(exc, (FileNotFoundError, ValueError)):
            return f"Error: {type(exc).__name__}: {str(exc)[:300]}"

        reason_source = getattr(exc, "orig", exc)
        reason = str(reason_source).replace("\n", " ").strip()
        reason = reason[:300]

        if not reason:
            reason = "import failed"

        return f"Error: {type(exc).__name__}: {reason}"

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
        hint = ""

        if "value too long for type character varying" in reason.lower():
            hint = (
                " hint=one of the text fields is probably longer than "
                "the target database column."
            )

        return (
            f"Row import error {row_number}: "
            f"document_type={document_type}, "
            f"document_number={document_number}, "
            f"error={type(exc).__name__}, "
            f"reason={reason}{hint}"
        )
