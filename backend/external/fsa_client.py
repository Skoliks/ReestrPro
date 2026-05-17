from pathlib import Path

import requests


DEFAULT_USER_AGENT = "VKR-FSA-Archive-Downloader/1.0"
CHUNK_SIZE =  1024 * 1024


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
