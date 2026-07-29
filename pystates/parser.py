import requests
import trafilatura


def fetch_and_parse_article(url: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    res = trafilatura.bare_extraction(response.text, as_dict=True)

    if res is None:
        raise ValueError('Failed to extract text')

    title = res.get("title") or "No name"
    content = res.get("text") or ""

    return {"title": title, "content": content}