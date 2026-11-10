"""End-to-end tests: a real local HTTP server, real requests, real files.

No external network access is required.
"""

from __future__ import annotations

import http.server
import threading

import pytest

from pystates.exporters import save_article
from pystates.parser import ParseError, fetch_and_parse_article

ARTICLE_PAGE = """<!doctype html>
<html><head><title>Integration Article</title></head>
<body>
  <nav>menu items here</nav>
  <article>
    <h1>Integration Article</h1>
    <p>This paragraph exists so that the extractor has enough text to work
       with, because very short documents are discarded as boilerplate.</p>
    <h2>Second section</h2>
    <p>Another paragraph with more words inside it, describing something
       reasonably interesting for a reader to consume.</p>
  </article>
  <footer>footer text</footer>
</body></html>
"""

LATIN1_PAGE = """<html><head><meta charset="windows-1251"><title>Кирилиця</title></head>
<body><article><h1>Кирилиця</h1>
<p>Текст сторінки у кодуванні windows-1251, який має зберегтися коректно
   після витягування та запису у файл.</p>
<p>Другий абзац для того, щоб алгоритм витягування не відкинув сторінку.</p>
</article></body></html>
"""


class _Handler(http.server.BaseHTTPRequestHandler):
    routes = {}

    def do_GET(self):  # noqa: N802
        body = self.routes.get(self.path)
        if body is None:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"not found")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # silence test output
        pass


@pytest.fixture(scope="module")
def server():
    _Handler.routes = {
        "/article.html": ARTICLE_PAGE.encode("utf-8"),
        "/cyrillic.html": LATIN1_PAGE.encode("cp1251"),
    }
    httpd = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()


def test_fetch_and_parse_over_real_http(server):
    result = fetch_and_parse_article(f"{server}/article.html")
    assert result["title"] == "Integration Article"
    assert "enough text to work with" in result["content"]
    assert "menu items here" not in result["content"]


def test_cyrillic_page_over_real_http(server):
    result = fetch_and_parse_article(f"{server}/cyrillic.html")
    assert "Кирилиця" in result["content"]
    assert "зберегтися коректно" in result["content"]


def test_end_to_end_file_written(server, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    article = fetch_and_parse_article(f"{server}/article.html")
    path = save_article(
        title=article["title"],
        content=article["content"],
        output_format="md",
        url=f"{server}/article.html",
    )
    written = (tmp_path / path).read_text(encoding="utf-8")
    assert written.startswith("# Integration Article")
    assert f"{server}/article.html" in written


def test_404_raises(server):
    import requests

    with pytest.raises(requests.HTTPError):
        fetch_and_parse_article(f"{server}/missing.html")


def test_plain_text_page_raises_parse_error(server):
    import requests

    with pytest.raises((ParseError, requests.HTTPError)):
        fetch_and_parse_article(f"{server}/nope")
