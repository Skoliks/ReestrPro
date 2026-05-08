from pathlib import Path

import py7zr


def create_7z_archive(source_file: str, archive_path: str) -> None:
    source_file_path = Path(source_file)
    archive_file_path = Path(archive_path)

    if not source_file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {source_file_path.resolve()}")

    archive_file_path.parent.mkdir(parents=True, exist_ok=True)

    with py7zr.SevenZipFile(archive_file_path, mode="w") as archive:
        archive.write(source_file_path, arcname=source_file_path.name)

    print(f"Архив создан: {archive_file_path}")


if __name__ == "__main__":
    create_7z_archive(
        source_file="backend/data/samples/declaration_sample.csv",
        archive_path="backend/data/samples/archives/declaration_sample.7z",
    )

    create_7z_archive(
        source_file="backend/data/samples/certificates_sample.csv",
        archive_path="backend/data/samples/archives/certificates_sample.7z",
    )