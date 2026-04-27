# Maxwell EM Theory Processor

Automated processing pipeline for James Clerk Maxwell's electromagnetic treatises. Extracts, analyzes, and organizes content from scanned volumes using OCR, AI classification, and hierarchical structure mapping.

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
- OpenRouter API key (for AI classification mode)

### Installation

```bash
# Clone the repository
git clone <repository-url>
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
OPENROUTER_API_KEY=your_api_key
```

### Running the Pipeline

```bash
# Full pipeline (OCR + TOC + AI Classification)
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
├── input/                    # Source PDFs and README files
├── output/                   # Processed output data
├── main_pipeline.py          # Pipeline orchestrator
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore rules
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
| `ARCHITECTURE.md` | System architecture with visual diagrams |
| `USAGE_GUIDE.md` | Setup, configuration, and usage examples |
| `archive/ARCHIVE_MANIFEST.md` | Legacy artifact inventory |

## License

See individual source files for licensing details.
