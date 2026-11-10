"""Command-line interface for PyStates."""

from __future__ import annotations

import argparse
import sys

from pystates import __version__
from pystates.exporters import save_article
from pystates.parser import ParseError, fetch_and_parse_article

#: Below this many characters the "article" is almost certainly a nav page,
#: a paywall stub or a JavaScript-rendered listing rather than real content.
MIN_USEFUL_CHARS = 400


def build_parser() -> argparse.ArgumentParser:
    from pystates.exporters import SUPPORTED_FORMATS as FORMATS

    parser = argparse.ArgumentParser(
        prog="pystates",
        description="Download a web article and save it as clean Markdown or plain text.",
    )
    parser.add_argument("-u", "--url", required=True, help="URL of the article to fetch")
    parser.add_argument(
        "-f",
        "--format",
        default="md",
        choices=list(FORMATS),
        help="Output format (default: md)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Custom output filename, with or without extension",
    )
    parser.add_argument(
        "-d",
        "--output-dir",
        default=None,
        help="Directory to write the file into (default: current directory)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if not args.quiet:
            print(f"Downloading article from: {args.url}...")

        article = fetch_and_parse_article(args.url)

        if len(article["content"]) < MIN_USEFUL_CHARS:
            print(
                "Warning: extracted text is very short "
                f"({len(article['content'])} characters). The page may be a listing, "
                "a paywall stub, or rendered by JavaScript — try a direct article URL.",
                file=sys.stderr,
            )

        saved_file = save_article(
            title=article["title"],
            content=article["content"],
            output_format=args.format,
            custom_filename=args.output,
            output_dir=args.output_dir,
            author=article.get("author"),
            date=article.get("date"),
            sitename=article.get("sitename"),
            url=args.url,
        )
        if not args.quiet:
            print(f"Saved article to: {saved_file}")
        return 0
    except ParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # network errors, permission errors, ...
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
