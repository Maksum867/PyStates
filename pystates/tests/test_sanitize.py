"""Tests for pystates.exporters.sanitize_filename."""

from __future__ import annotations

import os

import pytest

from pystates.exporters import MAX_BASENAME_LENGTH, sanitize_filename


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Hello world", "Hello_world"),
        ("  padded  title  ", "padded_title"),
        ('a/b\\c:d*e?f"g<h>i|j', "abcdefghij"),
        ("line\nbreak\r\nand\ttab", "line_break_and_tab"),
        ("multiple    spaces", "multiple_spaces"),
        ("trailing___", "trailing"),
        ("...dots...", "dots"),
    ],
)
def test_sanitize_replaces_or_removes_unsafe_characters(raw, expected):
    assert sanitize_filename(raw) == expected


def test_sanitize_keeps_unicode_letters():
    assert sanitize_filename("Новини України") == "Новини_України"


def test_sanitize_keeps_inner_dots_and_dashes():
    assert sanitize_filename("v1.2-release notes") == "v1.2-release_notes"


@pytest.mark.parametrize("raw", ["", "   ", "///", "..."])
def test_sanitize_falls_back_for_empty_results(raw):
    assert sanitize_filename(raw) == "article"


@pytest.mark.parametrize("reserved", ["CON", "con", "Nul", "com1", "LPT9"])
def test_sanitize_avoids_windows_reserved_names(reserved):
    result = sanitize_filename(reserved)
    assert result.lower() not in {"con", "nul", "com1", "lpt9"}
    assert result.startswith("article_")


def test_sanitize_truncates_very_long_titles():
    result = sanitize_filename("Long title " * 60)
    assert len(result) <= MAX_BASENAME_LENGTH


def test_sanitize_result_is_usable_as_a_filename(tmp_path):
    name = sanitize_filename("A/B: report? <draft>")
    path = tmp_path / f"{name}.md"
    path.write_text("x", encoding="utf-8")
    assert path.exists()


def test_sanitize_never_returns_path_separators():
    result = sanitize_filename("../etc/passwd")
    assert os.sep not in result
    assert "/" not in result
