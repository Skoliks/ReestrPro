import argparse

from backend.external.archive_extractor import extract_7z_archive


def main() -> None:
    parser = argparse.ArgumentParser(description="Распаковка .7z архива")

    parser.add_argument(
        "--archive",
        required=True,
        help="Путь к .7z архиву",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Папка для распаковки",
    )

    args = parser.parse_args()

    files = extract_7z_archive(
        archive_path=args.archive,
        output_dir=args.output,
    )

    print("Архив распакован")
    print("Файлы:")

    for file in files:
        print(file)


if __name__ == "__main__":
    main()