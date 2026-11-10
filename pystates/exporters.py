"""Filename sanitization and article export for PyStates."""

from __future__ import annotations

import os
import re
from xml.sax.saxutils import escape as _xml_escape

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

SUPPORTED_FORMATS = ("md", "txt", "docx", "pdf")


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


_MD_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_MD_HEADING = re.compile(r"^#{1,6}\s+", flags=re.M)
_MD_BOLD = re.compile(r"(\*\*|__)(.+?)\1")
_MD_ITALIC = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
_MD_CODE = re.compile(r"`([^`]+)`")


def markdown_to_plain(text: str) -> str:
    """Strip the most common markdown markers so .txt output stays plain."""
    text = _MD_IMAGE.sub("", text)
    text = _MD_LINK.sub(r"\1", text)
    text = _MD_HEADING.sub("", text)
    text = _MD_BOLD.sub(r"\2", text)
    text = _MD_ITALIC.sub(r"\1", text)
    text = _MD_CODE.sub(r"\1", text)
    return text


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

    # The extractor runs in markdown mode; a plain-text export must not
    # inherit "**bold**", "## heading" or "[link](url)" markers.
    body = markdown_to_plain(body)
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

    path = os.path.join(output_dir, filename) if output_dir else filename

    if fmt == "docx":
        write_docx(path, title, content, author=author, date=date, sitename=sitename, url=url)
    elif fmt == "pdf":
        write_pdf(path, title, content, author=author, date=date, sitename=sitename, url=url)
    else:
        formatted_text = format_article(
            title=title,
            content=content,
            output_format=fmt,
            author=author,
            date=date,
            sitename=sitename,
            url=url,
        )
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(formatted_text)

    return path


def _paragraphs(markdown_text: str) -> list[str]:
    """Split extracted markdown into cleaned plain-text blocks."""
    plain = markdown_to_plain(markdown_text)
    return [block.strip() for block in plain.split("\n\n") if block.strip()]


def write_docx(
    path: str,
    title: str,
    content: str,
    author: str | None = None,
    date: str | None = None,
    sitename: str | None = None,
    url: str | None = None,
) -> str:
    """Write the article as a Word (.docx) document."""
    try:
        from docx import Document
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise RuntimeError("Word export needs python-docx. Install it with: pip install 'pystates-CLI[word]'") from exc

    document = Document()
    document.add_heading(title, level=0)

    byline_parts = []
    if author:
        byline_parts.append(f"By {author}")
    if date:
        byline_parts.append(str(date))
    if sitename:
        byline_parts.append(str(sitename))
    if byline_parts:
        byline = document.add_paragraph(" · ".join(byline_parts))
        byline.runs[0].italic = True
    if url:
        document.add_paragraph(url)

    for block in _paragraphs(content):
        document.add_paragraph(block)

    document.save(path)
    return path


def _register_pdf_fonts() -> dict[str, str]:
    """Return font names, registering a Unicode TTF when one is available."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    candidates = [
        (
            "DejaVu",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        ),
        ("DejaVu", "/usr/share/fonts/dejavu/DejaVuSerif.ttf", "/usr/share/fonts/dejavu/DejaVuSerif-Bold.ttf"),
        (
            "Liberation",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        ),
    ]
    for name, regular, bold in candidates:
        if os.path.exists(regular):
            pdfmetrics.registerFont(TTFont(name, regular))
            if os.path.exists(bold):
                pdfmetrics.registerFont(TTFont(name + "-Bold", bold))
                return {"regular": name, "bold": name + "-Bold"}
            return {"regular": name, "bold": name}
    return {"regular": "Helvetica", "bold": "Helvetica-Bold"}


def write_pdf(
    path: str,
    title: str,
    content: str,
    author: str | None = None,
    date: str | None = None,
    sitename: str | None = None,
    url: str | None = None,
) -> str:
    """Write the article as a PDF document."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise RuntimeError("PDF export needs reportlab. Install it with: pip install 'pystates-CLI[pdf]'") from exc

    fonts = _register_pdf_fonts()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "PyStatesTitle",
        parent=styles["Title"],
        fontName=fonts["bold"],
        fontSize=20,
        leading=24,
        spaceAfter=10,
    )
    meta_style = ParagraphStyle(
        "PyStatesMeta",
        parent=styles["Normal"],
        fontName=fonts["regular"],
        fontSize=9,
        leading=13,
        textColor="#555555",
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "PyStatesBody",
        parent=styles["BodyText"],
        fontName=fonts["regular"],
        fontSize=10.5,
        leading=15.5,
        spaceAfter=8,
    )

    document = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=22 * mm,
        rightMargin=22 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title=title,
    )

    flow = [Paragraph(_xml_escape(title), title_style)]

    byline_parts = []
    if author:
        byline_parts.append(f"By {author}")
    if date:
        byline_parts.append(str(date))
    if sitename:
        byline_parts.append(str(sitename))
    if byline_parts:
        flow.append(Paragraph(_xml_escape(" · ".join(byline_parts)), meta_style))
    if url:
        flow.append(Paragraph(_xml_escape(url), meta_style))
    flow.append(Spacer(1, 6))

    for block in _paragraphs(content):
        flow.append(Paragraph(_xml_escape(block), body_style))

    document.build(flow)
    return path
