import argparse

from backend.external.fsa_client import (
    find_latest_archive_link,
    get_open_data_page_url,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Поиск актуальной ссылки на .7z архив открытых данных Росаккредитации"
    )

    parser.add_argument(
        "--type",
        required=True,
        choices=["declaration", "certificate"],
        help="Тип документов: declaration или certificate",
    )

    args = parser.parse_args()

    page_url = get_open_data_page_url(args.type)
    archive_url = find_latest_archive_link(args.type)

    print(f"Тип документов: {args.type}")
    print(f"Страница открытых данных: {page_url}")
    print(f"Актуальная ссылка: {archive_url}")


if __name__ == "__main__":
    main()
