"""Tests for filename building and article export."""

from __future__ import annotations

from pystates.exporters import build_filename, format_article, save_article


class TestBuildFilename:
    def test_uses_sanitized_title_and_extension(self):
        assert build_filename("The New AI Era", "md") == "The_New_AI_Era.md"

    def test_txt_format(self):
        assert build_filename("Test", "txt") == "Test.txt"

    def test_unknown_format_falls_back_to_markdown(self):
        assert build_filename("Test", "pdf") == "Test.md"

    def test_custom_name_without_extension(self):
        assert build_filename("Ignored", "md", "my_article") == "my_article.md"

    def test_custom_name_with_matching_extension_is_not_duplicated(self):
        assert build_filename("Ignored", "md", "my_article.md") == "my_article.md"

    def test_custom_name_with_other_known_extension_is_normalised(self):
        # Regression: used to produce "report.txt.md".
        assert build_filename("Ignored", "md", "report.txt") == "report.md"
        assert build_filename("Ignored", "txt", "report.md") == "report.txt"

    def test_custom_extension_is_case_insensitive(self):
        assert build_filename("Ignored", "md", "Big.MD") == "Big.md"

    def test_directory_component_is_stripped(self):
        # Regression: ``-o ../escaped`` used to write outside the cwd.
        assert build_filename("Ignored", "md", "../../escaped") == "escaped.md"
        assert build_filename("Ignored", "md", "docs/note") == "note.md"

    def test_empty_title_falls_back(self):
        assert build_filename("", "md") == "article.md"


class TestFormatArticle:
    def test_markdown_has_h1_title(self):
        out = format_article("Title", "Body text", "md")
        assert out.startswith("# Title\n")

    def test_markdown_includes_byline_when_metadata_present(self):
        out = format_article(
            "Title",
            "Body",
            "md",
            author="Jane Smith",
            date="2025-01-01",
            sitename="The New Yorker",
        )
        assert "*By Jane Smith · 2025-01-01 · The New Yorker*" in out

    def test_markdown_without_metadata_has_no_empty_byline(self):
        out = format_article("Title", "Body", "md")
        assert "*By" not in out
        assert "\n\n\n" not in out

    def test_markdown_includes_source_url(self):
        out = format_article("Title", "Body", "md", url="https://example.com/a")
        assert "https://example.com/a" in out

    def test_txt_underlines_title(self):
        out = format_article("Title", "Body", "txt")
        lines = out.splitlines()
        assert lines[0] == "Title"
        assert lines[1] == "=" * len("Title")

    def test_content_is_not_double_newline_terminated(self):
        out = format_article("Title", "Body\n\n", "md")
        assert out.endswith("Body\n")


class TestSaveArticle:
    def test_writes_utf8_file_and_returns_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = save_article("Hello World", "Тіло статті", "md")
        assert path == "Hello_World.md"
        assert (tmp_path / path).read_text(encoding="utf-8").startswith("# Hello World")

    def test_respects_output_dir(self, tmp_path):
        target = tmp_path / "out"
        target.mkdir()
        path = save_article("T", "B", "txt", output_dir=str(target))
        assert (target / "T.txt").exists()
        assert path == str(target / "T.txt")

    def test_overwrites_existing_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        save_article("Same", "first", "md")
        save_article("Same", "second", "md")
        assert (tmp_path / "Same.md").read_text(encoding="utf-8").count("second") == 1

    def test_path_traversal_is_blocked(self, tmp_path, monkeypatch):
        work = tmp_path / "work"
        work.mkdir()
        monkeypatch.chdir(work)
        save_article("T", "B", "md", custom_filename="../escaped")
        assert not (tmp_path / "escaped.md").exists()
        assert (work / "escaped.md").exists()

    def test_writes_lf_line_endings(self, tmp_path):
        path = save_article("T", "line1\nline2", "txt", output_dir=str(tmp_path))
        raw = (tmp_path / f"{path.split('/')[-1]}").read_bytes()
        assert b"\r\n" not in raw
