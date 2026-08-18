# Maxwell EM Theory Processor

Automated processing pipeline for James Clerk Maxwell's electromagnetic treatises. Extracts, analyzes, and organizes content from scanned volumes using OCR, AI classification, and hierarchical structure mapping.

---

## Overview

This project provides a production-ready pipeline for converting scanned Maxwell electromagnetic theory volumes (PDFs) into structured, navigable, and semantically organized content. The pipeline handles OCR processing via Mathpix API, table-of-contents analysis, AI-powered content classification, and output organization by volume, part, chapter, and article hierarchy.

## Pipeline Architecture

```
Input PDFs → OCR (Mathpix) → TOC Analysis → AI Classification → Organized Output
```

### Stages

| Stage | Module | Description |
|-------|--------|-------------|
| 1 - OCR | `src/mathpix_processor.py` | PDF-to-text via Mathpix API with LaTeX equation recognition, caching, and logging |
| 2 - TOC | `src/toc_analyzer.py` | Parses README files to extract hierarchical structure (Volume > Part > Chapter > Article) |
| 3 - Organize | `src/content_organizer.py` | AI classification of page content using OpenRouter, section detection, article identification |
| 4 - Simple Mode | `src/simple_mode_organizer.py` | Lightweight organization mode without AI classification |

### Core Infrastructure

| Module | Purpose |
|--------|---------|
| `src/data_models.py` | Pydantic models for articles, chapters, parts, and volumes |
| `src/retry_handler.py` | Configurable retry logic with exponential backoff for API calls |
| `src/circuit_breaker.py` | Circuit breaker pattern for external API resilience |
| `src/health_monitor.py` | Pipeline health monitoring and status reporting |
| `src/logger_config.py` | Structured logging configuration |
| `src/utils.py` | Shared utilities (slugification, file handling, etc.) |
| `config/config.py` | Centralized configuration management |
| `main_pipeline.py` | Orchestration entry point |

## Quick Start

### Prerequisites

- Python 3.9+
- 8GB+ RAM recommended
- 10GB+ disk space for outputs
- Mathpix API credentials (App ID + App Key)

### Installation

```bash
# Clone the repository
git clone https://github.com/antmikinka/maxwell-em-processor.git
cd maxwell_em_processor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API credentials
```

### Configuration

Create a `.env` file in the project root:

```
MATHPIX_APP_ID=your_app_id
MATHPIX_APP_KEY=your_app_key
MATHPIX_URL=https://api.mathpix.com
```

### Running the Pipeline

```bash
# Full pipeline (OCR + TOC + Organization)
python main_pipeline.py

# Simple mode (OCR + basic organization, no AI)
python main_pipeline.py --simple

# Specific volume
python main_pipeline.py --volume 1
python main_pipeline.py --volume 2
```

## Project Structure

```
maxwell_em_processor/
├── archive/                  # Archived legacy artifacts
│   ├── documentation/        # Historical planning docs
│   ├── legacy-scripts/       # Old iteration scripts
│   │   ├── extractors/       # TOC extraction iterations
│   │   ├── mathpix/          # Direct Mathpix API scripts
│   │   ├── diagnostics/      # Validation and sanity-check scripts
│   │   ├── splitters/        # Volume splitting scripts
│   │   └── one-off/          # One-off processing and setup scripts
│   └── ARCHIVE_MANIFEST.md   # What was archived and why
├── config/                   # Configuration module
│   ├── config.py             # Settings management
│   └── config.txt            # Configuration defaults
├── src/                      # Production source code
│   ├── circuit_breaker.py    # API resilience pattern
│   ├── content_organizer.py  # Stage 3: AI content organization
│   ├── data_models.py        # Pydantic data models
│   ├── health_monitor.py     # Pipeline monitoring
│   ├── logger_config.py      # Logging setup
│   ├── mathpix_processor.py  # Stage 1: OCR processing
│   ├── retry_handler.py      # Retry logic
│   ├── simple_mode_organizer.py  # Simple organization mode
│   ├── toc_analyzer.py       # Stage 2: TOC analysis
│   └── utils.py              # Shared utilities
├── mpxpy/                    # Vendored Mathpix SDK fork (MIT)
├── input/                    # Maxwell 1873 scans + TOC READMEs (public domain)
├── MAXWELL_VOLUME_1_MASTER_OUTPUT/  # Published Volume I OCR edition (public domain)
├── MAXWELL_VOLUME_2_MASTER_OUTPUT/  # Published Volume II OCR edition (public domain)
├── output/                   # Local cache/logs/trial OCR (not published)
├── main_pipeline.py          # Pipeline orchestrator
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore rules
├── LICENSE                   # Split grant (MIT / CC BY 4.0 / public domain)
├── LICENSES/                 # Official full license texts
│   ├── MIT.txt
│   └── CC-BY-4.0.txt
├── LICENSING.md              # Licensing decision record
├── NOTICE                    # Third-party (Mathpix) attribution
├── CITATION.cff              # Courtesy citation for the software/edition
├── ARCHITECTURE.md           # Detailed system architecture
└── USAGE_GUIDE.md            # Comprehensive usage documentation
```

## Key Features

- **Caching**: All Mathpix API responses cached to avoid redundant API calls
- **Resilience**: Circuit breaker pattern and configurable retry logic for API failures
- **Monitoring**: Real-time pipeline health monitoring with status reports
- **Structured Output**: Organized by Maxwell's original hierarchy (Volume > Part > Chapter > Article)
- **LaTeX Support**: Full equation extraction and preservation via Mathpix
- **Logging**: Comprehensive structured logging for debugging and audit trails
- **Dual Mode**: Full AI classification mode and lightweight simple mode

## Published sources and OCR

The Treatise scans and a readable OCR edition are in the repository so
others can inspect the work. Maxwell's 1873 text is public domain. This
project claims no copyright in the scans or in the mechanical OCR.

| Path | What you get |
|------|----------------|
| `input/15773-A Treatise On Electricity And Magnetism Vol-i.pdf` | Volume I scan |
| `input/15774-A Treatise On Electricity And Magnetism Vol-ii.pdf` | Volume II scan |
| `MAXWELL_VOLUME_1_MASTER_OUTPUT/volume_1_ocr.md` | Volume I OCR (Markdown + LaTeX) |
| `MAXWELL_VOLUME_2_MASTER_OUTPUT/volume_2_ocr.md` | Volume II OCR (Markdown + LaTeX) |
| `MAXWELL_VOLUME_*_MASTER_OUTPUT/` | Chapter JSON, TOC extracts, processing reports |
| `maxwell_article_index.json` | Article number / title / page map |

See `input/README.md` and each volume folder's `README.md`.

Not published: raw Mathpix zip/html/docx dumps, API caches, logs, a
failed TOC-split tree, and any non-Maxwell PDF that may exist locally
(including modern textbook chapters).

## Output

The pipeline produces:
- JSON files with page-level content and metadata
- Markdown files with OCR-extracted text and LaTeX equations
- Structured TOC hierarchy mappings
- Organized output directories per volume and part
- Processing reports and summaries

## Documentation

| Document | Purpose |
|----------|---------|
| `LICENSE` | The license grant (controls if docs disagree) |
| `LICENSES/MIT.txt` | Official MIT License text |
| `LICENSES/CC-BY-4.0.txt` | Official CC BY 4.0 legal code |
| `CITATION.cff` | Courtesy citation for the software and edition |
| `ARCHITECTURE.md` | System architecture with visual diagrams |
| `USAGE_GUIDE.md` | Setup, configuration, and usage examples |
| `LICENSING.md` | Licensing decision record and file-by-file map |
| `NOTICE` | Third-party attribution for vendored Mathpix SDK |
| `input/README.md` | Which source PDFs are published |
| `archive/ARCHIVE_MANIFEST.md` | Legacy artifact inventory |

---

## Licensing

This repository contains works under different licenses. It is not
dual-licensed as a single work.

| Material | License |
|----------|---------|
| Original code (`src/`, `config/`, `main_pipeline.py`, `archive/legacy-scripts/`) | [MIT](LICENSES/MIT.txt) |
| Original documentation and analysis (`README.md`, `ARCHITECTURE.md`, `USAGE_GUIDE.md`, `LICENSING.md`, `archive/documentation/`) | [CC BY 4.0](LICENSES/CC-BY-4.0.txt) |
| Vendored `mpxpy/` | MIT inbound (Mathpix, Inc.; modifications by Anthony Mikinka). See [NOTICE](NOTICE) and `mpxpy/LICENSE.txt` |
| Maxwell's 1873 text, mechanical OCR, factual indexes, input TOC READMEs | Public domain — no copyright claimed |
| Other inbound files (non-Maxwell PDFs under `input/`) | Not licensed by this project |

**Original code (MIT):** use, modify, distribute, sell. Keep the copyright notice.

**Original docs (CC BY 4.0):** share and adapt, including commercially. Credit Anthony Mikinka, link the license, and note changes.

**Maxwell:** public domain. Use his words without permission. OCR and article/page indexes of the Treatise are not a CC BY dataset.

Citing this project as the edition you used is welcome as scholarly
courtesy. It is not a copyright condition on Maxwell. See
[CITATION.cff](CITATION.cff).

See [LICENSE](LICENSE) for the grant, [LICENSES/](LICENSES/) for the
official full texts, [NOTICE](NOTICE) for third-party attribution, and
[LICENSING.md](LICENSING.md) for the decision record.

---

This README is original project documentation licensed under
[CC BY 4.0](LICENSES/CC-BY-4.0.txt)
([deed](https://creativecommons.org/licenses/by/4.0/)).
Maxwell's 1873 text, where quoted, is public domain.

*Author: Anthony Mikinka*
