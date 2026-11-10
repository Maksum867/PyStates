"""HTTP fetching + article extraction for PyStates."""

from __future__ import annotations

import requests
import trafilatura

DEFAULT_TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class ParseError(ValueError):
    """Raised when an article cannot be fetched or its text cannot be extracted."""


def fetch_html(url: str, timeout: int = DEFAULT_TIMEOUT) -> bytes:
    """Download ``url`` and return the raw body as bytes.

    Returning bytes (instead of ``response.text``) lets Trafilatura detect the
    real encoding from the document itself. ``requests`` falls back to
    ISO-8859-1 for any ``text/*`` response without a charset, which silently
    mangles non-ASCII pages (e.g. legacy windows-1251 sites).
    """
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.content


def extract_article(html: str | bytes, url: str | None = None) -> dict:
    """Extract title, text and metadata from raw HTML."""
    if isinstance(html, bytes):
        payload: str | bytes = html
    else:
        payload = html

    metadata = trafilatura.extract_metadata(payload)
    # ``output_format="markdown"`` + ``include_formatting=True`` keeps paragraph
    # breaks and emphasis. The default ("txt") output joins every paragraph into
    # one giant line, which makes the exported file unreadable for long articles.
    # ``favor_precision`` drops inline promo/boilerplate that the recall-oriented
    # default happily keeps (e.g. subscribe banners in the middle of the text).
    text = trafilatura.extract(
        payload,
        url=url,
        include_comments=False,
        include_tables=True,
        favor_precision=True,
        output_format="markdown",
        include_formatting=True,
    )

    if not text:
        raise ParseError("Failed to extract text")

    title = None
    author = None
    date = None
    sitename = None
    if metadata is not None:
        title = getattr(metadata, "title", None)
        author = getattr(metadata, "author", None)
        date = getattr(metadata, "date", None)
        sitename = getattr(metadata, "sitename", None)

    if not title:
        # Fall back to the first line of the extracted body, then to a default.
        first_line = text.splitlines()[0].strip() if text.strip() else ""
        title = first_line[:120] or "No name"

    return {
        "title": title,
        "content": text,
        "author": author,
        "date": date,
        "sitename": sitename,
        "url": url,
    }


def fetch_and_parse_article(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Download ``url`` and return its parsed article data."""
    html = fetch_html(url, timeout=timeout)
    return extract_article(html, url=url)
