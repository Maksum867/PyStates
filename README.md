<div align="center">

# PyStates

> **A lightweight, elegant Python CLI tool for fetching clean, distraction-free web articles.**

[![Python](https://img.shields.io/badge/python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Trafilatura](https://img.shields.io/badge/powered_by-trafilatura-FF6B6B?style=for-the-badge)](https://github.com/adbar/trafilatura)

</div>
---

## 📖 Description

**PyStates** is a fast, minimalist command-line utility that downloads full-length articles from major publications (The New Yorker, Wired, The Atlantic, and hundreds more) and extracts clean, readable text using the industry-leading [Trafilatura](https://github.com/adbar/trafilatura) library.

It automatically removes ads, navigation menus, sidebars, comments, and boilerplate, then saves the result as either beautifully formatted **Markdown** (`.md`) or clean **Plain Text** (`.txt`).

Designed for researchers, writers, journalists, students, and power users who want to archive high-quality content locally — without distractions or paywalls interfering with readability.

```bash
pystates -u https://www.newyorker.com/magazine/2025/01/20/the-new-ai-era
```

## ✨ Features

- 🚀 **Blazing Fast** — Downloads and processes articles in under 3 seconds
- 🛡️ **403 Bypass** — Smart custom `User-Agent` headers to reliably avoid common blocks
- 🧼 **Pristine Extraction** — Powered by Trafilatura for the cleanest possible text
- 📝 **Four Output Formats** — Markdown (`.md`), Plain Text (`.txt`), Word (`.docx`) and PDF (`.pdf`)
- 🧹 **Intelligent Filename Sanitization** — Generates safe OS filenames from article titles **without using `re`**
- ✍️ **Custom Filenames** — Override auto-generated names with the `-o` flag
- 🐍 **Modern Python Stack** — Built for Python 3.10+ with clean architecture
- 📦 **One-Command Installation** — `pip install -e .` for instant local development
- 🌐 **Broad Compatibility** — Works with virtually any news, magazine, or blog site supported by Trafilatura

## 🚀 Installation (Local Dev Mode)

```bash
# 1. Clone the repository
git clone https://github.com/Maksum867/PyStates.git
cd pystates

# 2. Install in editable/development mode
pip install -e .
```

### Optional: Word and PDF output

`md` and `txt` work out of the box. Word and PDF output need extra dependencies:

```bash
pip install "pystates-CLI[word]"   # .docx  (python-docx)
pip install "pystates-CLI[pdf]"    # .pdf   (reportlab)
pip install "pystates-CLI[word,pdf]"  # both
```

If a format is requested without its dependency installed, the CLI exits with a
clear message telling you which extra to install.

### Verify Installation

```bash
pystates --help
```

### Requirements

- Python ≥ 3.9
- `pip`

All dependencies (`requests`, `trafilatura`) are installed automatically via `pyproject.toml`. `argparse` ships with Python.

## 🖥️ Usage

### Command Syntax

```bash
pystates -u URL [OPTIONS]
```

### CLI Flags

| Short | Long        | Required | Default | Description |
|-------|-------------|----------|---------|-------------|
| `-u`  | `--url`     | **Yes**  | —       | The full URL of the article to fetch and process |
| `-f`  | `--format`  | No       | `md`    | Output format: `md`, `txt`, `docx` (Word) or `pdf` |
| `-o`  | `--output`  | No       | *(auto)* | Custom output filename. Any directory component is stripped; a matching extension is normalised |
| `-d`  | `--output-dir` | No    | `.`      | Directory to write the file into |
| `-q`  | `--quiet`   | No       | off     | Suppress progress output (useful in cron jobs and CI) |
|       | `--version` | No       | —       | Print the version and exit |

### Examples

#### 1. Basic usage (Markdown, auto-generated filename)

```bash
pystates -u "https://www.newyorker.com/magazine/2025/01/20/the-new-ai-era"
```

→ Creates `the-new-ai-era.md`

#### 2. Save as plain text

```bash
pystates -u "https://www.wired.com/story/the-future-of-coding/" -f txt
```

→ Creates `the-future-of-coding.txt`

#### 3. Custom output filename

```bash
pystates -u "https://www.theatlantic.com/ideas/archive/2025/07/climate-change/" \
         -o "climate_report_july_2025" \
         -f md
```

→ Creates `climate_report_july_2025.md`

#### 4. Full-featured command

```bash
pystates \
  --url "https://www.newyorker.com/culture/cultural-comment/the-end-of-the-internet-as-we-know-it" \
  --format txt \
  --output "end_of_internet"
```

#### 5. Export to Word or PDF

```bash
pystates -u "https://www.newyorker.com/books/page-turner/what-is-biography-for" -f docx
pystates -u "https://en.wikipedia.org/wiki/Ada_Lovelace" -f pdf
```

→ Creates `What_Is_Biography_For.docx` / `Ada_Lovelace.pdf`, with a proper title,
byline (author · date · publication) and one paragraph per source paragraph.

#### 6. View all options

```bash
pystates --help
```

### Sample Output (Markdown)

```markdown
# The New AI Era

*By Jane Smith · 2025-01-20 · The New Yorker*

<https://www.newyorker.com/culture/cultural-comment/the-end-of-the-internet-as-we-know-it>

---

Artificial intelligence is no longer a distant promise...

## A New Paradigm

The implications are profound...

```

## 📁 Project Structure

```
PyStates/
├── pystates/
│   ├── __init__.py          # Package metadata & version
│   ├── __main__.py          # Entry point for `python -m pystates`
│   ├── cli.py               # Argument parsing (argparse)
│   ├── exporters.py         # Filename sanitization + md/txt/docx/pdf export
│   └── parser.py            # HTTP fetching (custom UA) + Trafilatura parsing
│   └── tests/               # 75 pytest tests (unit + real-HTTP integration)
├── .github/
│   ├── workflows/
│   │   ├── tests.yml        # pytest matrix, lint, packaging
│   │   └── publish.yml      # build + publish to PyPI (Trusted Publishing)
│   └── dependabot.yml       # automatic dependency updates
├── pyproject.toml           # Modern packaging + entry points
├── CHANGELOG.md
├── .gitignore
└── README.md
```

## ⚠️ Known limitations

- **JavaScript-only pages are not supported.** PyStates downloads the HTML the
  server sends; sites that render the article in the browser (client-side React
  apps) may return a listing page or a paywall stub instead of the article.
  When the extracted text is suspiciously short, the CLI prints a warning on
  stderr and still writes the file.
- **Bot protection blocks some sites.** With a plain HTTP client, sites behind
  Cloudflare/Akamai may answer `403`/`401`. PyStates reports the HTTP error and
  exits with status `1`.
- **PDF fonts.** A Unicode TTF (DejaVu/Liberation) is used when present on the
  system, so Cyrillic and CJK render correctly on most Linux images and macOS;
  elsewhere ReportLab falls back to Helvetica, which only covers Latin-1.
- **The default User-Agent is a fixed desktop Chrome string.** It is not
  rotated, and it is not a "403 bypass".

## 🧪 Development & Testing

```bash
git clone https://github.com/Maksum867/PyStates.git
cd PyStates
pip install -e ".[dev]"
python -m pytest            # 75 tests, no network access required
ruff check . && ruff format --check .
```

The suite includes a real end-to-end run against a local `http.server`, so it
verifies the whole pipeline (download → extract → sanitize → write) without
touching the internet.

### Releasing

1. Bump the version in `pyproject.toml` and `pystates/__init__.py`.
2. Update `CHANGELOG.md`.
3. Publish a GitHub Release tagged `vX.Y.Z`.
4. `.github/workflows/publish.yml` runs the tests, builds the distributions and
   publishes to PyPI via Trusted Publishing (no API token needed).

## 📜 License

This project is released under the **MIT License**.

See [LICENSE](LICENSE) for the full text.

---

**PyStates** — preserving the web's best writing, one clean file at a time.

*Built with care by the open-source community.*