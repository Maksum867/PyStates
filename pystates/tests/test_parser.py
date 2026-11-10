"""Tests for pystates.parser (extraction + HTTP layer)."""

from __future__ import annotations

import pytest
import requests

from pystates import parser
from pystates.parser import ParseError, extract_article, fetch_and_parse_article, fetch_html


class TestExtractArticle:
    def test_extracts_title_from_page(self, article_html):
        result = extract_article(article_html)
        assert result["title"] == "The New AI Era"

    def test_extracts_body_text(self, article_html):
        result = extract_article(article_html)
        assert "Artificial intelligence is no longer a distant promise" in result["content"]

    def test_body_does_not_contain_navigation_or_footer(self, article_html):
        content = extract_article(article_html)["content"]
        assert "Subscribe" not in content
        assert "Copyright 2025" not in content

    def test_extracts_metadata_when_available(self, article_html):
        result = extract_article(article_html)
        assert result["author"] == "Jane Smith"
        assert result["sitename"] is None or isinstance(result["sitename"], str)

    def test_works_with_bytes_input(self, article_html_bytes):
        result = extract_article(article_html_bytes)
        assert result["title"] == "The New AI Era"
        assert "Artificial intelligence" in result["content"]

    def test_decodes_legacy_cp1251_page(self, cyrillic_cp1251_bytes):
        # Regression: passing response.text decoded as ISO-8859-1 mangled the text.
        result = extract_article(cyrillic_cp1251_bytes)
        assert "Новини України" in result["content"]
        assert "перевірки кодування" in result["content"]

    def test_raises_parse_error_for_empty_page(self, no_content_html):
        with pytest.raises(ParseError):
            extract_article(no_content_html)

    def test_parse_error_is_a_value_error(self):
        assert issubclass(ParseError, ValueError)

    def test_url_is_returned_unchanged(self, article_html):
        result = extract_article(article_html, url="https://example.com/x")
        assert result["url"] == "https://example.com/x"

    def test_falls_back_to_body_first_line_when_no_title(self):
        html = "<html><body><article><p>" + ("A sentence worth extracting. " * 20) + "</p></article></body></html>"
        result = extract_article(html)
        assert result["title"]
        assert result["title"] != "No name"


class TestFetchLayer:
    def test_fetch_html_returns_bytes(self, monkeypatch):
        class FakeResponse:
            content = b"<html>ok</html>"
            status_code = 200

            def raise_for_status(self):
                return None

        monkeypatch.setattr(parser.requests, "get", lambda *a, **kw: FakeResponse())
        assert fetch_html("https://example.com") == b"<html>ok</html>"

    def test_fetch_html_sends_user_agent_and_timeout(self, monkeypatch):
        captured = {}

        class FakeResponse:
            content = b"x"

            def raise_for_status(self):
                return None

        def fake_get(url, headers=None, timeout=None):
            captured["url"] = url
            captured["headers"] = headers
            captured["timeout"] = timeout
            return FakeResponse()

        monkeypatch.setattr(parser.requests, "get", fake_get)
        fetch_html("https://example.com", timeout=7)
        assert "Mozilla" in captured["headers"]["User-Agent"]
        assert captured["timeout"] == 7

    def test_http_error_propagates(self, monkeypatch):
        class FakeResponse:
            content = b""

            def raise_for_status(self):
                raise requests.HTTPError("404 Client Error")

        monkeypatch.setattr(parser.requests, "get", lambda *a, **kw: FakeResponse())
        with pytest.raises(requests.HTTPError):
            fetch_html("https://example.com/missing")

    def test_fetch_and_parse_article_end_to_end(self, monkeypatch, article_html_bytes):
        class FakeResponse:
            content = article_html_bytes

            def raise_for_status(self):
                return None

        monkeypatch.setattr(parser.requests, "get", lambda *a, **kw: FakeResponse())
        result = fetch_and_parse_article("https://example.com/article")
        assert result["title"] == "The New AI Era"
        assert result["url"] == "https://example.com/article"

    def test_default_timeout_is_used(self, monkeypatch):
        captured = {}

        class FakeResponse:
            content = b"<html></html>"

            def raise_for_status(self):
                return None

        def fake_get(url, headers=None, timeout=None):
            captured["timeout"] = timeout
            return FakeResponse()

        monkeypatch.setattr(parser.requests, "get", fake_get)
        fetch_html("https://example.com")
        assert captured["timeout"] == parser.DEFAULT_TIMEOUT


class TestPruning:
    def test_prune_xpaths_are_passed_by_default(self, monkeypatch):
        captured = {}

        def fake_extract(payload, **kwargs):
            captured.update(kwargs)
            return "Body text"

        monkeypatch.setattr(parser.trafilatura, "extract", fake_extract)
        monkeypatch.setattr(parser.trafilatura, "extract_metadata", lambda *a, **kw: None)
        extract_article("<html><body><p>Body text</p></body></html>")
        assert captured["prune_xpath"], "prune rules must be applied by default"
        assert any("related" in rule for rule in captured["prune_xpath"])

    def test_prune_can_be_disabled(self, monkeypatch):
        captured = {}

        def fake_extract(payload, **kwargs):
            captured.update(kwargs)
            return "Body text"

        monkeypatch.setattr(parser.trafilatura, "extract", fake_extract)
        monkeypatch.setattr(parser.trafilatura, "extract_metadata", lambda *a, **kw: None)
        extract_article("<html><body><p>Body text</p></body></html>", prune=False)
        assert captured["prune_xpath"] is None

    def test_related_block_is_removed(self, article_html):
        # A "related articles" aside must not leak into the exported text.
        html = article_html.replace(
            "</article>",
            "</article><aside class='related-articles'>Read next: Something Else Entirely</aside>",
        )
        result = extract_article(html)
        assert "Read next" not in result["content"]

    def test_newsletter_block_is_removed(self, article_html):
        html = article_html.replace(
            "</article>",
            "</article><div class='newsletter-signup'>Subscribe to our daily newsletter!</div>",
        )
        result = extract_article(html)
        assert "Subscribe to our daily" not in result["content"]

    def test_prune_rules_cover_known_container_names(self):
        rules = " ".join(parser.PRUNE_XPATHS)
        for token in ("related", "newsletter", "subscribe", "deepDive", "stayConnected"):
            assert token in rules
