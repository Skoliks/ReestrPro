import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

DEFAULT_USER_AGENT = "VKR-FSA-Archive-Downloader/1.0"
CHUNK_SIZE = 1024 * 1024

OPEN_DATA_PAGE_URLS = {
    "declaration": "https://fsa.gov.ru/opendata/7736638268-rds/",
    "certificate": "https://fsa.gov.ru/opendata/7736638268-rss/",
}

ARCHIVE_URL_FRAGMENTS = {
    "declaration": "7736638268-rds",
    "certificate": "7736638268-rss",
}

ARCHIVE_NAME_PATTERN = re.compile(
    r"data-(\d{8})-structure-(\d{8})\.7z",
    re.IGNORECASE,
)


def download_archive(
    url: str,
    output_path: str | Path,
    timeout: int = 60,
) -> Path:
    target_path = Path(output_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
    }

    with requests.get(url, stream=True, timeout=timeout, headers=headers) as response:
        response.raise_for_status()

        with target_path.open("wb") as file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    file.write(chunk)

    return target_path


def find_archive_links(page_url: str, timeout: int = 30) -> list[str]:
    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
    }

    response = requests.get(page_url, headers=headers, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    archive_links: list[str] = []

    for link in soup.find_all("a"):
        href = link.get("href")

        if not href:
            continue

        absolute_url = urljoin(page_url, href)

        if ".7z" in absolute_url.lower():
            archive_links.append(absolute_url)

    return archive_links


def extract_archive_dates(url: str) -> tuple[str, str] | None:
    match = ARCHIVE_NAME_PATTERN.search(url)

    if not match:
        return None

    data_date, structure_date = match.groups()
    return data_date, structure_date


def filter_archive_links_by_type(
    links: list[str],
    document_type: str,
) -> list[str]:
    if document_type not in {"declaration", "certificate"}:
        raise ValueError("document_type должен быть declaration или certificate")

    if document_type == "declaration":
        keywords = ["declaration", "declarations", "decl", "rds", "деклара"]
    else:
        keywords = ["certificate", "certificates", "cert", "rss", "сертифик"]

    filtered_links: list[str] = []

    for link in links:
        normalized_link = link.lower()

        if any(keyword in normalized_link for keyword in keywords):
            filtered_links.append(link)

    return filtered_links


def choose_latest_archive_link(links: list[str]) -> str:
    if not links:
        raise FileNotFoundError("Не найдено подходящих ссылок на архивы")

    dated_links: list[tuple[str, str, str]] = []

    for link in links:
        archive_dates = extract_archive_dates(link)

        if archive_dates is None:
            continue

        data_date, structure_date = archive_dates
        dated_links.append((data_date, structure_date, link))

    if dated_links:
        dated_links.sort(key=lambda item: (item[0], item[1], item[2]))
        return dated_links[-1][2]

    return sorted(links)[-1]


def get_open_data_page_url(document_type: str) -> str:
    page_url = OPEN_DATA_PAGE_URLS.get(document_type)

    if page_url is None:
        raise ValueError("document_type должен быть declaration или certificate")

    return page_url


def find_latest_archive_link(document_type: str) -> str:
    page_url = get_open_data_page_url(document_type)
    links = find_archive_links(page_url)
    fragment = ARCHIVE_URL_FRAGMENTS[document_type]
    filtered_links = [link for link in links if fragment in link.lower()]
    return choose_latest_archive_link(filtered_links)
