from backend.external.fsa_client import (
    choose_latest_archive_link,
    extract_archive_dates,
)


def test_extract_archive_dates_returns_dates_from_archive_url() -> None:
    url = "https://fsa.gov.ru/opendata/7736638268-rds/data-20260131-structure-20260212.7z"

    assert extract_archive_dates(url) == ("20260131", "20260212")


def test_choose_latest_archive_link_prefers_newer_data_and_structure_dates() -> None:
    links = [
        "https://fsa.gov.ru/opendata/7736638268-rds/data-20260130-structure-20260212.7z",
        "https://fsa.gov.ru/opendata/7736638268-rds/data-20260131-structure-20260210.7z",
        "https://fsa.gov.ru/opendata/7736638268-rds/data-20260131-structure-20260212.7z",
    ]

    assert (
        choose_latest_archive_link(links)
        == "https://fsa.gov.ru/opendata/7736638268-rds/data-20260131-structure-20260212.7z"
    )
