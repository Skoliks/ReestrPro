import argparse

from backend.external.fsa_client import (
    choose_latest_archive_link,
    filter_archive_links_by_type,
    find_archive_links,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Поиск ссылок на .7z архивы на странице открытых данных"
    )

    parser.add_argument(
        "--page-url",
        required=True,
        help="URL страницы, на которой нужно искать ссылки на архивы",
    )

    parser.add_argument(
        "--type",
        choices=["declaration", "certificate"],
        default=None,
        help="Тип документов для фильтрации ссылок",
    )

    args = parser.parse_args()

    links = find_archive_links(args.page_url)

    if args.type:
        links = filter_archive_links_by_type(
            links=links,
            document_type=args.type,
        )

    print(f"Найдено ссылок: {len(links)}")

    for link in links:
        print(link)

    if links:
        latest_link = choose_latest_archive_link(links)
        print()
        print("Выбранная ссылка:")
        print(latest_link)


if __name__ == "__main__":
    main()