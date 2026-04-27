# Maxwell TOC Extractor - Complete Access Schema
# ============================================

# This document provides the EXACT SCHEMA for accessing ALL data from Volume 1 and Volume 2
# including page numbers, content, equations, figures, and metadata

## 📋 EXECUTIVE SUMMARY

This schema provides the complete structure for accessing:
- Page numbers and content from both volumes
- Hierarchical organization (Parts → Chapters → Articles)
- Mathematical equations and figures
- Metadata and confidence scores
- Cross-volume navigation

## 🏗️ COMPLETE DATA SCHEMA

### 1. MASTER INDEX FILE SCHEMA
### File: `MASTER_TOC_INDEX.json`

```json
{
  "maxwell_toc_index": {
    "created_at": "2025-11-29T21:24:19.779678",
    "total_volumes": 2,
    "volumes": {
      "1": {
        "title": "Volume 1",
        "total_pages": 572,
        "total_parts": 834,
        "total_chapters": 10901,
        "total_articles": 13819,
        "path": "V1_Volume_1"
      },
      "2": {
        "title": "Volume 2",
        "total_pages": 544,
        "total_parts": [NUMBER],
        "total_chapters": [NUMBER],
        "total_articles": [NUMBER],
        "path": "V2_Volume_2"
      }
    },
    "navigation": {
      "file_naming": "V1_C002_A0015.json (Volume 1, Chapter 002, Article 0015)",
      "folder_structure": "V1_Volume_1/P01_Part_01/C001_Chapter_001/",
      "metadata_files": "Each level has metadata.json with structural info",
      "article_content": "Each article has full content, equations, figures"
    }
  }
}
```

### 2. VOLUME METADATA SCHEMA
### File: `V1_Volume_1/volume_metadata.json`

```json
{
  "volume_number": 1,
  "title": "Volume 1",
  "total_pages": 572,
  "total_parts": 834,
  "total_chapters": 10901,
  "total_articles": 13819,
  "created_at": "2025-11-29T21:24:19.779678",
  "structure_summary": {
    "parts": [
      {
        "part_number": 1,
        "title": "beyond the comprehension",
        "page_range": "11-20",
        "chapter_count": 5
      }
    ],
    "chapters_per_part": {
      "1": 5,
      "2": 3
    },
    "articles_per_chapter": {
      "1.1": 10,
      "1.2": 8
    }
  }
}
```

### 3. PART METADATA SCHEMA
### File: `V1_Volume_1/P01_Part_01_beyond the comprehension/part_metadata.json`

```json
{
  "part_id": "part_1",
  "part_number": 1,
  "title": "beyond the comprehension",
  "page_start": 11,
  "page_end": 20,
  "chapters": []
}
```

### 4. CHAPTER METADATA SCHEMA
### File: `V1_Volume_1/P01_Part_01_beyond the comprehension/C001_Chapter_001_The expression of a quantity consists of two factors, the nu/chapter_metadata.json`

```json
{
  "chapter_id": "chapter_1",
  "chapter_number": 1,
  "title": "The expression of a quantity consists of two factors, the nu",
  "page_start": 11,
  "page_end": 15,
  "articles": []
}
```

### 5. ARTICLE FILE SCHEMA (MAIN CONTENT)
### File: `V1_Volume_1/P01_Part_01_beyond the comprehension/C001_Chapter_001_The expression of a quantity consists of two factors, the nu/V1_C001_A0001.json`

```json
{
  "article_id": "article_1",
  "article_number": 1,
  "title_original": "ORIGINAL MATHEMATICAL TITLE WITH $\\frac{d}{dx}$",
  "title_safe": "SAFE VERSION FOR FOLDERS",
  "page_start": 11,
  "page_end": 12,
  "content": {
    "raw_text": "Full plain text content of the article...",
    "mathpix_markdown": "Formatted Markdown with LaTeX equations...",
    "structured_lines": [
      {
        "page": 11,
        "line_number": 1,
        "type": "text",
        "content": "Line text content",
        "mathpix_content": "Formatted line content",
        "font_size": 12,
        "confidence": 0.95
      }
    ]
  },
  "equations": [
    {
      "equation_id": "eq_1_0",
      "latex": "\\frac{d}{dx} x^2 = 2x",
      "mathml": "<math>...</math>",
      "page": 11,
      "location": {
        "top_left_x": 100,
        "top_left_y": 200,
        "width": 300,
        "height": 50
      },
      "confidence": 0.98
    }
  ],
  "figures": [
    {
      "figure_id": "fig_1_0",
      "image_path": "https://cdn.mathpix.com/...",
      "caption": "Figure caption text",
      "description": "Description of the figure",
      "page": 12,
      "location": {
        "top_left_x": 150,
        "top_left_y": 300,
        "width": 400,
        "height": 200
      }
    }
  ],
  "metadata": {
    "word_count": 1250,
    "line_count": 45,
    "confidence_score": 0.94
  }
}
```

## 🔍 COMPLETE VARIABLE ACCESS REFERENCE

### VOLUME 1 ACCESS PATTERNS

```python
import json
from pathlib import Path

# Load master index
with open('Maxwell_TOC_Fixed/MASTER_TOC_INDEX.json', 'r') as f:
    master_index = json.load(f)

# Get Volume 1 info
volume1_info = master_index['maxwell_toc_index']['volumes']['1']
print(f"Volume 1: {volume1_info['total_pages']} pages, {volume1_info['total_parts']} parts")

# Load volume metadata
volume1_dir = Path('Maxwell_TOC_Fixed') / volume1_info['path']
with open(volume1_dir / 'volume_metadata.json', 'r') as f:
    volume1_data = json.load(f)

# Access page numbers from structure summary
for part_summary in volume1_data['structure_summary']['parts']:
    print(f"Part {part_summary['part_number']}: pages {part_summary['page_range']}")

# Load specific article
article_path = volume1_dir / 'P01_Part_01_beyond the comprehension' / 'C001_Chapter_001_The expression of a quantity consists of two factors, the nu' / 'V1_C001_A0001.json'

with open(article_path, 'r') as f:
    article = json.load(f)

# Access page numbers
print(f"Article pages: {article['page_start']} to {article['page_end']}")

# Access content
print(f"Raw content: {article['content']['raw_text'][:100]}...")
print(f"Mathpix content: {article['content']['mathpix_markdown'][:100]}...")

# Access mathematical equations
for eq in article['equations']:
    print(f"Equation {eq['equation_id']}: {eq['latex']} (page {eq['page']})")

# Access figures
for fig in article['figures']:
    print(f"Figure {fig['figure_id']}: {fig['caption']} (page {fig['page']})")

# Access structured lines
for line in article['content']['structured_lines']:
    print(f"Page {line['page']}, Line {line['line_number']}: {line['content'][:50]}...")
```

### VOLUME 2 ACCESS PATTERNS

```python
# Load Volume 2 info
if '2' in master_index['maxwell_toc_index']['volumes']:
    volume2_info = master_index['maxwell_toc_index']['volumes']['2']
    print(f"Volume 2: {volume2_info['total_pages']} pages")

    # Load volume 2 metadata
    volume2_dir = Path('Maxwell_TOC_Fixed') / volume2_info['path']
    with open(volume2_dir / 'volume_metadata.json', 'r') as f:
        volume2_data = json.load(f)

    # Access volume 2 articles (same pattern as volume 1)
    # V2_C002_A0015.json format
```

### CROSS-VOLUME NAVIGATION

```python
# Get all volumes
volumes = master_index['maxwell_toc_index']['volumes']

# Iterate through both volumes
for volume_num, volume_info in volumes.items():
    print(f"Volume {volume_num}: {volume_info['total_pages']} pages")

    # Load volume data
    volume_dir = Path('Maxwell_TOC_Fixed') / volume_info['path']
    with open(volume_dir / 'volume_metadata.json', 'r') as f:
        volume_data = json.load(f)

    # Get total statistics
    total_parts = volume_data['total_parts']
    total_chapters = volume_data['total_chapters']
    total_articles = volume_data['total_articles']

    print(f"Volume {volume_num}: {total_parts} parts, {total_chapters} chapters, {total_articles} articles")
```

### PAGE NUMBER EXTRACTION

```python
def get_all_page_ranges(volume_num):
    """Get all page ranges from a volume"""
    volume_dir = Path(f'Maxwell_TOC_Fixed/V{volume_num}_Volume_{volume_num}')

    # Load volume metadata
    with open(volume_dir / 'volume_metadata.json', 'r') as f:
        volume_data = json.load(f)

    page_ranges = []

    # Iterate through parts
    for part_dir in (volume_dir).iterdir():
        if part_dir.is_dir() and part_dir.name.startswith('P'):
            with open(part_dir / 'part_metadata.json', 'r') as f:
                part_data = json.load(f)

            part_range = {
                'part_number': part_data['part_number'],
                'part_title': part_data['title'],
                'page_start': part_data['page_start'],
                'page_end': part_data['page_end']
            }

            # Iterate through chapters in this part
            for chapter_dir in part_dir.iterdir():
                if chapter_dir.is_dir() and chapter_dir.name.startswith('C'):
                    with open(chapter_dir / 'chapter_metadata.json', 'r') as f:
                        chapter_data = json.load(f)

                    chapter_range = {
                        'chapter_number': chapter_data['chapter_number'],
                        'chapter_title': chapter_data['title'],
                        'page_start': chapter_data['page_start'],
                        'page_end': chapter_data['page_end']
                    }

                    # Iterate through articles in this chapter
                    for article_file in chapter_dir.iterdir():
                        if article_file.name.endswith('.json') and article_file.name.startswith(f'V{volume_num}_'):
                            with open(article_file, 'r') as f:
                                article_data = json.load(f)

                            article_range = {
                                'article_number': article_data['article_number'],
                                'article_title': article_data['title_original'],
                                'page_start': article_data['page_start'],
                                'page_end': article_data['page_end'],
                                'equations_count': len(article_data['equations']),
                                'figures_count': len(article_data['figures']),
                                'word_count': article_data['metadata']['word_count']
                            }

                            page_ranges.append({
                                'volume': volume_num,
                                'part': part_range,
                                'chapter': chapter_range,
                                'article': article_range
                            })

    return page_ranges

# Usage
volume1_pages = get_all_page_ranges(1)
print(f"Volume 1 has {len(volume1_pages)} articles with page ranges")

# Example: Find articles in specific page range
for item in volume1_pages:
    if 50 <= item['article']['page_start'] <= 100:
        print(f"Article {item['article']['article_number']} in pages {item['article']['page_start']}-{item['article']['page_end']}")
```

### MATHEMATICAL CONTENT EXTRACTION

```python
def extract_all_equations(volume_num):
    """Extract all mathematical equations from a volume"""
    equations = []
    volume_dir = Path(f'Maxwell_TOC_Fixed/V{volume_num}_Volume_{volume_num}')

    for article_file in volume_dir.rglob(f'V{volume_num}_*.json'):
        with open(article_file, 'r') as f:
            article = json.load(f)

        for eq in article['equations']:
            equation_info = {
                'volume': volume_num,
                'article_id': article['article_id'],
                'article_number': article['article_number'],
                'article_title': article['title_original'],
                'article_pages': f"{article['page_start']}-{article['page_end']}",
                'equation_id': eq['equation_id'],
                'latex': eq['latex'],
                'mathml': eq['mathml'],
                'page': eq['page'],
                'confidence': eq['confidence']
            }
            equations.append(equation_info)

    return equations

# Usage
volume1_equations = extract_all_equations(1)
print(f"Volume 1 has {len(volume1_equations)} equations")

# Find equations with specific LaTeX
for eq in volume1_equations:
    if 'frac' in eq['latex']:
        print(f"Found fraction in {eq['article_title']}: {eq['latex'][:50]}...")
```

### CONTENT SEARCH AND ANALYSIS

```python
def search_content(volume_num, search_term):
    """Search for content across all articles in a volume"""
    results = []
    volume_dir = Path(f'Maxwell_TOC_Fixed/V{volume_num}_Volume_{volume_num}')

    for article_file in volume_dir.rglob(f'V{volume_num}_*.json'):
        with open(article_file, 'r') as f:
            article = json.load(f)

        # Search in raw text
        if search_term.lower() in article['content']['raw_text'].lower():
            results.append({
                'volume': volume_num,
                'article_id': article['article_id'],
                'article_number': article['article_number'],
                'article_title': article['title_original'],
                'article_pages': f"{article['page_start']}-{article['page_end']}",
                'content_type': 'raw_text',
                'content': article['content']['raw_text'][:200] + '...'
            })

        # Search in mathpix markdown
        if search_term.lower() in article['content']['mathpix_markdown'].lower():
            results.append({
                'volume': volume_num,
                'article_id': article['article_id'],
                'article_number': article['article_number'],
                'article_title': article['title_original'],
                'article_pages': f"{article['page_start']}-{article['page_end']}",
                'content_type': 'mathpix_markdown',
                'content': article['content']['mathpix_markdown'][:200] + '...'
            })

    return results

# Usage
search_results = search_content(1, 'Maxwell')
print(f"Found {len(search_results)} articles mentioning 'Maxwell' in Volume 1")

# Search for mathematical expressions
math_results = search_content(1, '\\frac')
print(f"Found {len(math_results)} articles with fractions in Volume 1")
```

### STATISTICS AND ANALYSIS

```python
def get_volume_statistics(volume_num):
    """Get comprehensive statistics for a volume"""
    volume_dir = Path(f'Maxwell_TOC_Fixed/V{volume_num}_Volume_{volume_num}')

    stats = {
        'volume': volume_num,
        'total_articles': 0,
        'total_equations': 0,
        'total_figures': 0,
        'total_words': 0,
        'total_pages': 0,
        'page_distribution': {},
        'part_stats': {},
        'chapter_stats': {}
    }

    for article_file in volume_dir.rglob(f'V{volume_num}_*.json'):
        with open(article_file, 'r') as f:
            article = json.load(f)

        stats['total_articles'] += 1
        stats['total_equations'] += len(article['equations'])
        stats['total_figures'] += len(article['figures'])
        stats['total_words'] += article['metadata']['word_count']

        # Page distribution
        page_range = f"{article['page_start']}-{article['page_end']}"
        stats['page_distribution'][page_range] = stats['page_distribution'].get(page_range, 0) + 1

        # Track max page
        if article['page_end'] > stats['total_pages']:
            stats['total_pages'] = article['page_end']

    return stats

# Usage
volume1_stats = get_volume_statistics(1)
print(f"Volume 1 Statistics:")
print(f"  Articles: {volume1_stats['total_articles']}")
print(f"  Equations: {volume1_stats['total_equations']}")
print(f"  Figures: {volume1_stats['total_figures']}")
print(f"  Words: {volume1_stats['total_words']}")
print(f"  Pages: {volume1_stats['total_pages']}")

# Compare volumes
volume2_stats = get_volume_statistics(2)
print(f"\nVolume 2 Statistics:")
print(f"  Articles: {volume2_stats['total_articles']}")
print(f"  Equations: {volume2_stats['total_equations']}")
```

### COMPLETE FILE ACCESS REFERENCE

| File Type | Path Pattern | Access Method | Key Data |
|-----------|--------------|---------------|----------|
| Master Index | `MASTER_TOC_INDEX.json` | `json.load()` | Volume counts, navigation info |
| Volume Metadata | `VX_Volume_X/volume_metadata.json` | `json.load()` | Total pages, parts, chapters, articles |
| Part Metadata | `VX_Volume_X/PXX_Part_XX_*/part_metadata.json` | `json.load()` | Part page ranges, chapter counts |
| Chapter Metadata | `VX_Volume_X/PXX_Part_XX_*/CXXX_Chapter_XXX_*/chapter_metadata.json` | `json.load()` | Chapter page ranges, article counts |
| Article Content | `VX_Volume_X/PXX_Part_XX_*/CXXX_Chapter_XXX_*/VX_CXXX_AXXXX.json` | `json.load()` | Full content, equations, figures, metadata |

### FILE NAMING CONVENTIONS

| Component | Format | Example |
|-----------|--------|---------|
| Volume Directory | `V{volume_num}_Volume_{volume_num}` | `V1_Volume_1` |
| Part Directory | `P{part_number:02d}_Part_{part_number:02d}_{safe_title}` | `P01_Part_01_beyond the comprehension` |
| Chapter Directory | `C{chapter_number:03d}_Chapter_{chapter_number:03d}_{safe_title}` | `C001_Chapter_001_The expression of a quantity consists of two factors, the nu` |
| Article File | `V{volume_num}_C{chapter_number:03d}_A{article_number:04d}.json` | `V1_C001_A0001.json` |

### DATA FIELD REFERENCE

| Level | Field | Type | Description |
|-------|-------|------|-------------|
| Master | `maxwell_toc_index.volumes.{num}.total_pages` | int | Total pages in volume |
| Master | `maxwell_toc_index.volumes.{num}.total_parts` | int | Total parts in volume |
| Master | `maxwell_toc_index.volumes.{num}.total_chapters` | int | Total chapters in volume |
| Master | `maxwell_toc_index.volumes.{num}.total_articles` | int | Total articles in volume |
| Volume | `title` | string | Volume title |
| Volume | `total_pages` | int | Total pages |
| Volume | `structure_summary.parts` | array | Part summaries |
| Part | `part_number` | int | Part number |
| Part | `title` | string | Part title (original) |
| Part | `page_start` | int | Start page |
| Part | `page_end` | int | End page |
| Chapter | `chapter_number` | int | Chapter number |
| Chapter | `title` | string | Chapter title (original) |
| Chapter | `page_start` | int | Start page |
| Chapter | `page_end` | int | End page |
| Article | `article_number` | int | Article number |
| Article | `title_original` | string | Original title with math |
| Article | `title_safe` | string | Safe title for folders |
| Article | `page_start` | int | Start page |
| Article | `page_end` | int | End page |
| Article | `content.raw_text` | string | Plain text content |
| Article | `content.mathpix_markdown` | string | Formatted Markdown |
| Article | `content.structured_lines` | array | Line-by-line content |
| Article | `equations` | array | Mathematical equations |
| Article | `figures` | array | Figures and diagrams |
| Article | `metadata.word_count` | int | Word count |
| Article | `metadata.line_count` | int | Line count |
| Article | `metadata.confidence_score` | float | Confidence score |

This complete schema provides EVERYTHING needed to access page numbers, content, equations, and all metadata from both Volume 1 and Volume 2 with exact file paths, data structures, and Python access patterns!