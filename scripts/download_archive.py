import argparse

from backend.external.fsa_client import download_archive


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Скачивание .7z архива по прямой ссылке"
    )

    parser.add_argument(
        "--url",
        required=True,
        help="Прямая ссылка на .7z архив",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Путь, куда нужно сохранить архив",
    )

    args = parser.parse_args()

    archive_path = download_archive(
        url=args.url,
        output_path=args.output,
    )

    print("Архив успешно скачан")
    print(f"Путь: {archive_path}")


if __name__ == "__main__":
    main()
