from pathlib import Path

import py7zr


def extract_7z_archive(archive_path: str | Path, output_dir: str | Path) -> list[Path]:
    archive_path = Path(archive_path)
    output_dir = Path(output_dir)

    if not archive_path.exists():
        raise FileNotFoundError(f"Архив не найден: {archive_path.resolve()}")

    output_dir.mkdir(parents=True, exist_ok=True)

    with py7zr.SevenZipFile(archive_path, mode="r") as archive:
        archive.extractall(path=output_dir)

    return list(output_dir.rglob("*"))