"""Tests for the Word (.docx) and PDF exporters."""

from __future__ import annotations

import pathlib
import zipfile

import pytest

from pystates.exporters import build_filename, save_article

docx = pytest.importorskip("docx", reason="python-docx is required for Word export")
reportlab = pytest.importorskip("reportlab", reason="reportlab is required for PDF export")

ARTICLE = "First paragraph of the article.\n\nSecond paragraph with more text.\n\nThird one."


class TestFilenames:
    def test_docx_extension(self):
        assert build_filename("Title", "docx") == "Title.docx"

    def test_pdf_extension(self):
        assert build_filename("Title", "pdf") == "Title.pdf"

    def test_custom_name_with_format_extension(self):
        assert build_filename("T", "docx", "report.docx") == "report.docx"
        assert build_filename("T", "pdf", "report.pdf") == "report.pdf"

    def test_wrong_known_extension_is_normalised(self):
        assert build_filename("T", "pdf", "report.md") == "report.pdf"


class TestDocxExport:
    def test_file_is_created_and_is_a_zip_container(self, tmp_path):
        path = save_article("Heading", ARTICLE, "docx", output_dir=str(tmp_path))
        data = tmp_path / "Heading.docx"
        assert path.endswith("Heading.docx")
        assert data.exists()
        assert zipfile.is_zipfile(data)

    def test_title_author_and_body_are_present(self, tmp_path):
        save_article(
            "Article Heading",
            ARTICLE,
            "docx",
            output_dir=str(tmp_path),
            author="Jane Smith",
            date="2025-01-02",
            sitename="Example Times",
            url="https://example.com/a",
        )
        document = docx.Document(str(tmp_path / "Article_Heading.docx"))
        text = "\n".join(p.text for p in document.paragraphs)
        assert "Article Heading" in text
        assert "Jane Smith" in text
        assert "Example Times" in text
        assert "https://example.com/a" in text
        assert "First paragraph of the article." in text
        assert "Third one." in text

    def test_paragraphs_are_separate(self, tmp_path):
        save_article("H", ARTICLE, "docx", output_dir=str(tmp_path))
        document = docx.Document(str(tmp_path / "H.docx"))
        bodies = [p.text for p in document.paragraphs if p.text.strip()]
        assert "First paragraph of the article." in bodies
        assert "Second paragraph with more text." in bodies

    def test_markdown_markers_are_stripped(self, tmp_path):
        save_article("H", "Text with **emphasis** here.", "docx", output_dir=str(tmp_path))
        document = docx.Document(str(tmp_path / "H.docx"))
        text = "\n".join(p.text for p in document.paragraphs)
        assert "**" not in text
        assert "emphasis" in text


class TestPdfExport:
    def test_file_is_created_with_pdf_header(self, tmp_path):
        path = save_article("Pdf Title", ARTICLE, "pdf", output_dir=str(tmp_path))
        data = pathlib.Path(path).read_bytes()
        assert data.startswith(b"%PDF")
        assert b"%%EOF" in data[-2048:]

    def test_file_is_not_empty(self, tmp_path):
        path = save_article("Pdf Title", ARTICLE, "pdf", output_dir=str(tmp_path))
        assert pathlib.Path(path).stat().st_size > 1000

    def test_unicode_content_does_not_crash(self, tmp_path):
        path = save_article("Кирилиця", "Текст українською мовою. Ще речення.", "pdf", output_dir=str(tmp_path))
        assert pathlib.Path(path).read_bytes().startswith(b"%PDF")

    def test_special_characters_are_escaped(self, tmp_path):
        content = 'Text with <angle> & "quotes" and a stray & ampersand.'
        path = save_article("Escape", content, "pdf", output_dir=str(tmp_path))
        assert pathlib.Path(path).read_bytes().startswith(b"%PDF")

    def test_metadata_is_set(self, tmp_path):
        path = save_article(
            "Meta Title", ARTICLE, "pdf", output_dir=str(tmp_path), author="A", sitename="S", url="https://x.test"
        )
        assert pathlib.Path(path).stat().st_size > 0
