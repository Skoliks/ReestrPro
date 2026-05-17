from pathlib import Path

from scripts.sync_open_data import (
    build_batch_report,
    get_default_archive_output_path,
    get_extracted_output_dir,
)


def test_get_default_archive_output_path_returns_declaration_path() -> None:
    assert get_default_archive_output_path("declaration") == Path(
        "backend/data/raw/declarations/latest_declaration.7z"
    )


def test_get_default_archive_output_path_returns_certificate_path() -> None:
    assert get_default_archive_output_path("certificate") == Path(
        "backend/data/raw/certificates/latest_certificate.7z"
    )


def test_get_extracted_output_dir_returns_declaration_dir() -> None:
    assert get_extracted_output_dir("declaration") == Path(
        "backend/data/extracted/declarations"
    )


def test_get_extracted_output_dir_returns_certificate_dir() -> None:
    assert get_extracted_output_dir("certificate") == Path(
        "backend/data/extracted/certificates"
    )


def test_build_batch_report_copies_batch_fields_to_plain_dict() -> None:
    class FakeBatch:
        id = 101
        status = "completed"
        total_rows = 10
        processed_rows = 8
        failed_rows = 2
        error_message = None

    assert build_batch_report(FakeBatch()) == {
        "batch_id": 101,
        "status": "completed",
        "total_rows": 10,
        "processed_rows": 8,
        "failed_rows": 2,
        "error_message": None,
    }
