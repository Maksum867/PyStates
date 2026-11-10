"""Filename sanitization and article export for PyStates."""

from __future__ import annotations

import os
import re

# Windows reserved device names: creating ``con.md`` fails on Windows.
_RESERVED_NAMES = {
    "con",
    "prn",
    "aux",
    "nul",
    *{f"com{i}" for i in range(1, 10)},
    *{f"lpt{i}" for i in range(1, 10)},
}

#: Characters that are illegal in filenames on Windows/macOS/Linux.
#: Whitespace (\n, \t, ...) is not listed here on purpose: it is collapsed into
#: a single underscore below, so "line\nbreak" becomes "line_break".
FORBIDDEN_CHARS = ["/", "\\", ":", "*", "?", '"', "<", ">", "|", "\x00"]

#: Keep filenames below the common 255-byte limit with room for an extension.
MAX_BASENAME_LENGTH = 120

SUPPORTED_FORMATS = ("md", "txt")


def sanitize_filename(filename: str) -> str:
    """Turn an arbitrary article title into a safe, portable file name."""
    if not filename:
        return "article"

    clean_name = filename
    for char in FORBIDDEN_CHARS:
        clean_name = clean_name.replace(char, "")

    # Collapse any run of whitespace into a single underscore.
    clean_name = re.sub(r"\s+", "_", clean_name.strip())
    clean_name = clean_name.strip("_.")

    # Trailing dots/spaces are stripped by Windows and break round-tripping.
    clean_name = clean_name.rstrip(" .")

    if len(clean_name) > MAX_BASENAME_LENGTH:
        clean_name = clean_name[:MAX_BASENAME_LENGTH].rstrip("_.")

    if not clean_name or clean_name.lower() in _RESERVED_NAMES:
        clean_name = f"article_{clean_name}" if clean_name else "article"

    return clean_name


def build_filename(title: str, output_format: str = "md", custom_filename: str | None = None) -> str:
    """Return the final output filename for an article."""
    fmt = (output_format or "md").lower().lstrip(".")
    if fmt not in SUPPORTED_FORMATS:
        fmt = "md"

    if custom_filename:
        # Strip any directory component so ``-o ../x`` cannot escape the cwd.
        base_name = os.path.basename(custom_filename.strip())
        root, ext = os.path.splitext(base_name)
        # Drop a known output extension whatever the requested format, so
        # ``-o report.txt -f md`` yields ``report.md`` and not ``report.txt.md``.
        if ext.lower() in {f".{known}" for known in SUPPORTED_FORMATS}:
            base_name = root
        base_name = sanitize_filename(base_name)
    else:
        base_name = sanitize_filename(title)

    if not base_name:
        base_name = "article"

    return f"{base_name}.{fmt}"


def format_article(
    title: str,
    content: str,
    output_format: str = "md",
    author: str | None = None,
    date: str | None = None,
    sitename: str | None = None,
    url: str | None = None,
) -> str:
    """Render the article body according to ``output_format``."""
    fmt = (output_format or "md").lower().lstrip(".")
    if fmt not in SUPPORTED_FORMATS:
        fmt = "md"

    byline_parts = []
    if author:
        byline_parts.append(f"By {author}")
    if date:
        byline_parts.append(str(date))
    if sitename:
        byline_parts.append(str(sitename))
    byline = " · ".join(byline_parts)

    body = content.rstrip("\n")

    if fmt == "md":
        parts = [f"# {title}", ""]
        if byline:
            parts += [f"*{byline}*", ""]
        if url:
            parts += [f"<{url}>", ""]
        parts += [body, ""]
        return "\n".join(parts)

    underline = "=" * max(len(title), 1)
    parts = [title, underline, ""]
    if byline:
        parts += [byline, ""]
    if url:
        parts += [url, ""]
    parts += [body, ""]
    return "\n".join(parts)


def save_article(
    title: str,
    content: str,
    output_format: str = "md",
    custom_filename: str | None = None,
    output_dir: str | None = None,
    author: str | None = None,
    date: str | None = None,
    sitename: str | None = None,
    url: str | None = None,
) -> str:
    """Write the article to disk and return the path that was written."""
    filename = build_filename(title, output_format, custom_filename)
    fmt = filename.rsplit(".", 1)[-1]

    formatted_text = format_article(
        title=title,
        content=content,
        output_format=fmt,
        author=author,
        date=date,
        sitename=sitename,
        url=url,
    )

    path = os.path.join(output_dir, filename) if output_dir else filename

    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(formatted_text)

    return path
