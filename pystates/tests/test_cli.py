"""Tests for the command-line interface (no network access)."""

from __future__ import annotations

import pytest
import requests

from pystates import cli
from pystates.parser import ParseError

ARTICLE = {
    "title": "Test Article",
    "content": "Body of the article.",
    "author": "Jane Smith",
    "date": "2025-01-01",
    "sitename": "Example",
    "url": "https://example.com/a",
}


@pytest.fixture()
def fake_fetch(monkeypatch):
    """Patch the CLI's fetch function and record what it was called with."""

    calls = {}

    def fake(url, **kwargs):
        calls["url"] = url
        return dict(ARTICLE)

    monkeypatch.setattr(cli, "fetch_and_parse_article", fake)
    return calls


class TestArguments:
    def test_url_is_required(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            cli.main([])
        assert excinfo.value.code == 2
        assert "required" in capsys.readouterr().err

    def test_help_exits_zero(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            cli.main(["--help"])
        assert excinfo.value.code == 0
        assert "usage:" in capsys.readouterr().out

    def test_version_flag(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            cli.main(["--version"])
        assert excinfo.value.code == 0
        assert "pystates" in capsys.readouterr().out

    def test_invalid_format_rejected(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            cli.main(["-u", "https://example.com", "-f", "rtf"])
        assert excinfo.value.code == 2

    def test_output_dir_flag_is_accepted(self, fake_fetch, tmp_path):
        code = cli.main(["-u", "https://example.com", "-d", str(tmp_path), "-q"])
        assert code == 0
        assert (tmp_path / "Test_Article.md").exists()


class TestRun:
    def test_successful_run_prints_path_and_returns_zero(self, fake_fetch, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        code = cli.main(["-u", "https://example.com/a"])
        out = capsys.readouterr().out
        assert code == 0
        assert "Saved article to: Test_Article.md" in out
        assert (tmp_path / "Test_Article.md").read_text(encoding="utf-8").startswith("# Test Article")

    def test_quiet_suppresses_output(self, fake_fetch, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        code = cli.main(["-u", "https://example.com/a", "-q"])
        assert code == 0
        assert capsys.readouterr().out == ""

    def test_format_txt_is_honoured(self, fake_fetch, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cli.main(["-u", "https://example.com/a", "-f", "txt", "-q"])
        assert (tmp_path / "Test_Article.txt").exists()

    def test_custom_output_name(self, fake_fetch, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cli.main(["-u", "https://example.com/a", "-o", "custom", "-q"])
        assert (tmp_path / "custom.md").exists()

    def test_url_is_passed_through(self, fake_fetch, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cli.main(["-u", "https://example.com/some/page", "-q"])
        assert fake_fetch["url"] == "https://example.com/some/page"


class TestErrors:
    def test_parse_error_returns_one_and_writes_stderr(self, monkeypatch, capsys):
        def boom(url, **kwargs):
            raise ParseError("Failed to extract text")

        monkeypatch.setattr(cli, "fetch_and_parse_article", boom)
        code = cli.main(["-u", "https://example.com/bad", "-q"])
        assert code == 1
        assert "Failed to extract text" in capsys.readouterr().err

    def test_http_error_returns_one(self, monkeypatch, capsys):
        def boom(url, **kwargs):
            raise requests.HTTPError("404 Client Error")

        monkeypatch.setattr(cli, "fetch_and_parse_article", boom)
        code = cli.main(["-u", "https://example.com/missing", "-q"])
        assert code == 1
        assert "404" in capsys.readouterr().err

    def test_connection_error_returns_one(self, monkeypatch, capsys):
        def boom(url, **kwargs):
            raise requests.ConnectionError("dns failure")

        monkeypatch.setattr(cli, "fetch_and_parse_article", boom)
        assert cli.main(["-u", "https://example.com", "-q"]) == 1
        assert "dns failure" in capsys.readouterr().err

    def test_unwritable_path_returns_one(self, monkeypatch, capsys):
        def ok(url, **kwargs):
            return dict(ARTICLE)

        monkeypatch.setattr(cli, "fetch_and_parse_article", ok)
        code = cli.main(["-u", "https://example.com", "-d", "/root/../proc/forbidden", "-q"])
        assert code == 1
