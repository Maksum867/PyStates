<div align="center">

# PyStates

> **A lightweight, elegant Python CLI tool for fetching clean, distraction-free web articles.**

[![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
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
- 📝 **Dual Format Support** — Native `.md` (with headings, emphasis, and structure) or `.txt`
- 🧹 **Intelligent Filename Sanitization** — Generates safe OS filenames from article titles **without using `re`**
- ✍️ **Custom Filenames** — Override auto-generated names with the `-o` flag
- 🐍 **Modern Python Stack** — Built for Python 3.10+ with clean architecture
- 📦 **One-Command Installation** — `pip install -e .` for instant local development
- 🌐 **Broad Compatibility** — Works with virtually any news, magazine, or blog site supported by Trafilatura

## 🚀 Installation (Local Dev Mode)

```bash
# 1. Clone the repository
git clone https://github.com/your-org/pystates.git
cd pystates

# 2. Install in editable/development mode
pip install -e .
```

### Verify Installation

```bash
pystates --help
```

### Requirements

- Python ≥ 3.10
- `pip`

All dependencies (`requests`, `trafilatura`, `argparse`) are automatically installed via `pyproject.toml`.

## 🖥️ Usage

### Command Syntax

```bash
pystates -u URL [OPTIONS]
```

### CLI Flags

| Short | Long        | Required | Default | Description |
|-------|-------------|----------|---------|-------------|
| `-u`  | `--url`     | **Yes**  | —       | The full URL of the article to fetch and process |
| `-f`  | `--format`  | No       | `md`    | Output format. Accepted values: `md` or `txt` |
| `-o`  | `--output`  | No       | *(auto)* | Custom output filename **without extension**. If omitted, a sanitized version of the article title is used |

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

#### 5. View all options

```bash
pystates --help
```

### Sample Output (Markdown)

```markdown
# The New AI Era

**By Jane Smith**  
*Published: January 20, 2025*  
*Source: The New Yorker*

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
│   ├── exporters.py         # Filename sanitization + .md/.txt formatting
│   └── parser.py            # HTTP fetching (custom UA) + Trafilatura parsing
├── pyproject.toml           # Modern packaging + entry points
├── .gitignore
└── README.md
```

## 📜 License

This project is released under the **MIT License**.

See [LICENSE](LICENSE) for the full text.

---

**PyStates** — preserving the web's best writing, one clean file at a time.

*Built with care by the open-source community.*