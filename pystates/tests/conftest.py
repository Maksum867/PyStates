"""Shared fixtures for the PyStates test suite."""

from __future__ import annotations

import pytest

ARTICLE_HTML = """<!doctype html>
<html>
  <head>
    <title>Fallback Title From Head</title>
    <meta name="author" content="Jane Smith">
  </head>
  <body>
    <nav>Home | About | Subscribe</nav>
    <article>
      <h1>The New AI Era</h1>
      <p>Artificial intelligence is no longer a distant promise. It is here,
         and it is reshaping how we work every single day.</p>
      <p>In the paragraphs that follow, we examine what changed in the last two
         years and why it matters for everyone involved.</p>
      <h2>A New Paradigm</h2>
      <p>The implications are profound, and they touch nearly every industry
         that depends on knowledge work and software.</p>
      <p>Read on for a detailed breakdown of the forces at play, and what to
         watch next in this rapidly moving field.</p>
    </article>
    <footer>Copyright 2025</footer>
  </body>
</html>
"""

NO_CONTENT_HTML = """<!doctype html>
<html><head><title>Empty</title></head>
<body><div id="x"></div></body></html>
"""

CYRILLIC_CP1251_HTML = """<html>
  <head><meta charset="windows-1251"><title>Новини України</title></head>
  <body>
    <article>
      <h1>Новини України</h1>
      <p>Це тестовий текст українською мовою для перевірки кодування сторінки
         та коректного збереження символів у файл.</p>
      <p>Ще один абзац, щоб текст був достатньо довгим для витягування
         алгоритмом Trafilatura без помилок.</p>
    </article>
  </body>
</html>
"""


@pytest.fixture()
def article_html() -> str:
    """A small, realistic article page."""
    return ARTICLE_HTML


@pytest.fixture()
def article_html_bytes() -> bytes:
    """The same article page as raw bytes."""
    return ARTICLE_HTML.encode("utf-8")


@pytest.fixture()
def no_content_html() -> str:
    """A page with no extractable article body."""
    return NO_CONTENT_HTML


@pytest.fixture()
def cyrillic_cp1251_bytes() -> bytes:
    """A legacy-encoded (windows-1251) page, as served by older sites."""
    return CYRILLIC_CP1251_HTML.encode("cp1251")
