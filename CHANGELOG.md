# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-11-10

A correctness and features pass driven by an end-to-end audit of the tool against
live articles. Nine real bugs were found and fixed; the project gained two new
export formats, a test suite and CI.

### Added

- **Word (`.docx`) export** via `-f docx` — real title heading, italic byline
  (author · date · publication), source URL and one Word paragraph per article
  paragraph. Requires the `word` extra (`python-docx`).
- **PDF export** via `-f pdf` — A4 layout, proper title/byline blocks, auto
  Unicode TTF (DejaVu/Liberation) when available so Cyrillic and CJK render.
  Requires the `pdf` extra (`reportlab`).
- **Related-article and newsletter blocks are pruned.** Extraction now passes a
  `prune_xpath` list that drops `aside`, `[class*=related]`, `[class*=newsletter]`,
  `[class*=subscribe]`, `[class*=promo]`, `[class*=deepDive]`, `[class*=stayConnected]`
  and similar containers before the text is extracted. Verified on a live MIT
  Technology Review article: the trailing "Deep Dive" teaser list and the
  "Stay connected" newsletter box are gone (9 366 → 8 453 characters), while the
  body text is untouched. Regression-checked against 7 other sites — no loss.
  New `--no-prune` flag restores the old behaviour.
- New extras: `pystates-CLI[word]`, `pystates-CLI[pdf]`; `[dev]` now includes
  both so CI exercises every format.
- `-d/--output-dir` to write the file into a chosen directory.
- `-q/--quiet` for cron jobs and scripts, and a `--version` flag.
- Author, publication date and source site are written into the exported
  document as a byline, and the source URL is recorded.
- `pystates/tests/` — 98 tests covering filename sanitization, export/format
  (md, txt, docx, pdf), the HTTP layer, extraction, pruning, the CLI contract,
  and a real end-to-end run against a local HTTP server (no external network
  needed).
- `.github/workflows/tests.yml` — pytest on 3 operating systems × 5 Python
  versions, plus lint and a packaging job.
- `.github/workflows/publish.yml` — build, validate and publish to (Test)PyPI
  through Trusted Publishing, triggered by a GitHub Release.
- `.github/dependabot.yml` — weekly dependency and actions updates.
- `.txt` export strips markdown markers (`**bold**`, `## heading`,
  `[link](url)`) instead of leaking them from the structured extractor output.

### Changed

- `SUPPORTED_FORMATS` is now `("md", "txt", "docx", "pdf")`; `-f` validates
  against it, and unknown formats still fall back to Markdown.
- Requesting `docx`/`pdf` without the corresponding dependency now fails with a
  clear message naming the extra to install, instead of a bare `ImportError`.
- `rich` was a declared dependency but never imported; it has been removed.
- `argparse` was listed as a dependency in the README — it is part of the
  standard library, and the claim has been corrected.
- Packaging metadata refreshed: project URLs point at the real repository,
  `license-files` is declared, the obsolete license classifier was dropped, and
  the `dev` extra now exists.

### Fixed

- **Article title was always lost.** `trafilatura.bare_extraction(as_dict=True)`
  leaves `title` as `None` unless `with_metadata=True`, so every file was named
  `No_name.md` and started with `# No name`. Titles and bylines now come from
  `trafilatura.extract_metadata()`.
- **Non-ASCII pages were mangled.** `requests` decodes any `text/*` response
  without a `charset` as ISO-8859-1, which destroyed legacy-encoded pages
  (e.g. windows-1251). The raw response **bytes** are now handed to Trafilatura,
  which detects the encoding from the document.
- **All paragraphs were merged into one giant line.** The extractor ran in the
  default `txt` output mode, which joins paragraph breaks, so a 10 000-character
  article became a single unreadable line. Extraction now uses
  `output_format="markdown"` with `include_formatting=True`, preserving paragraph
  structure and emphasis.
- **Inline promo text leaked into the article.** `favor_precision=True` is now
  used, which drops subscribe/newsletter banners that the recall-oriented
  default keeps.
- **`-o` allowed writing outside the working directory.** `-o ../secret` wrote a
  file outside the current folder; any directory component is now stripped.
- **`-o report.txt -f md` produced `report.txt.md`.** A known output extension is
  now normalised to the requested format, giving `report.md`.
- **Exit codes were swallowed.** Failures exited `0` when run through the console
  script because `main()` returned nothing; `main()` now returns `0`/`1` and
  `__main__.py` propagates it with `sys.exit(main())`.
- **`sanitize_filename` could produce unusable names.** Titles longer than 255
  bytes raised `OSError`, Windows reserved device names (`con`, `nul`, `com1`…)
  failed on Windows, and newlines/tabs were silently glued together instead of
  becoming separators.
- **Silent "success" on non-article pages.** When the extracted text is shorter
  than 400 characters (listing pages, paywall stubs, JavaScript-rendered sites)
  the CLI now prints a warning on stderr while still writing the file — the exit
  code stays `0` because the extraction itself succeeded.
- **`.docx` byline crashed.** It used a non-existent Word style name (`Italic`)
  and failed on documents created without the built-in template; italics are now
  applied to the run directly.

## [0.1.0] — 2025

- Initial release: `-u/--url`, `-f/--format {md,txt}`, `-o/--output`.
