# Maxwell TOC Extractor & Hierarchical Organizer

## 📋 Overview

The **Maxwell TOC Extractor** is a comprehensive Python script that automatically extracts the Table of Contents, Chapters, and Articles from Maxwell's Electromagnetic Theory treatise and creates a **hierarchical folder/file structure** with individual JSON files for each article.

## 🎯 Features

### ✅ **Automatic Content Detection**
- **Parts**: Automatically detects major sections (Parts, Books)
- **Chapters**: Identifies chapter boundaries and titles
- **Articles**: Extracts individual articles with numbering
- **Smart Pattern Matching**: Uses multiple regex patterns for reliable detection

### ✅ **Hierarchical Folder Structure**
```
Maxwell_TOC/
├── Volume_1/
│   ├── volume_metadata.json
│   ├── Part_01_Electrostatics/
│   │   ├── part_metadata.json
│   │   ├── Chapter_001_Description_of_Motion/
│   │   │   ├── chapter_metadata.json
│   │   │   ├── Article_0001_Introductory.json
│   │   │   ├── Article_0002_Preliminary_Notions.json
│   │   │   └── ...
│   │   └── Chapter_002_Coulomb's_Law/
│   │       ├── chapter_metadata.json
│   │       ├── Article_0015_Coulomb's_Experiment.json
│   │       └── ...
│   └── ...
├── Volume_2/
│   ├── volume_metadata.json
│   └── ...
└── MASTER_TOC_INDEX.json
```

### ✅ **Comprehensive Article Content**
Each article JSON file contains:
- **Full Text Content**: Raw text and Mathpix Markdown
- **Mathematical Equations**: LaTeX and MathML formats
- **Figures & Diagrams**: Image paths and captions
- **Metadata**: Page ranges, word count, confidence scores
- **Structured Lines**: Line-by-line content with types and formatting

### ✅ **Rich Metadata**
- **Volume Metadata**: Total pages, parts, chapters, articles
- **Part Metadata**: Page ranges and chapter counts
- **Chapter Metadata**: Article counts and content summaries
- **Article Metadata**: Word counts, equations, figures, confidence scores

## 🚀 Usage

### Basic Usage

```bash
# Extract TOC for both volumes
python maxwell_toc_extractor.py

# Extract TOC for specific volume only
python maxwell_toc_extractor.py --volume 1
python maxwell_toc_extractor.py --volume 2

# Custom output directory
python maxwell_toc_extractor.py --base-dir My_Maxwell_TOC

# Verbose output
python maxwell_toc_extractor.py --verbose
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--base-dir` | Output directory base name | `Maxwell_TOC` |
| `--volume` | Volume to process (1, 2, or 0 for both) | `0` (both) |
| `--verbose` | Enable detailed logging | `False` |

## 📁 Output Structure

### Volume Level
```
Volume_1/
├── volume_metadata.json          # Volume summary and stats
└── MASTER_TOC_INDEX.json         # Complete navigation index
```

### Part Level
```
Part_01_Electrostatics/
├── part_metadata.json             # Part information
├── Chapter_001_Description_of_Motion/
└── Chapter_002_Coulomb's_Law/
```

### Chapter Level
```
Chapter_001_Description_of_Motion/
├── chapter_metadata.json          # Chapter information
├── Article_0001_Introductory.json
├── Article_0002_Preliminary_Notions.json
└── ...
```

### Article Level (Individual Files)
```json
{
  "article_id": "article_1",
  "article_number": 1,
  "title": "Introductory",
  "page_start": 1,
  "page_end": 5,
  "content": {
    "raw_text": "Full text content...",
    "mathpix_markdown": "Formatted Markdown with equations...",
    "structured_lines": [
      {
        "page": 1,
        "line_number": 1,
        "type": "text",
        "content": "Line content",
        "mathpix_content": "Formatted content",
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
      "page": 2,
      "location": {"top_left_x": 100, "top_left_y": 200, "width": 300, "height": 50}
    }
  ],
  "figures": [
    {
      "figure_id": "fig_1_0",
      "image_path": "https://cdn.mathpix.com/...",
      "caption": "Figure caption",
      "description": "Description text",
      "page": 3,
      "location": {"top_left_x": 150, "top_left_y": 300, "width": 400, "height": 200}
    }
  ],
  "metadata": {
    "word_count": 1250,
    "line_count": 45,
    "confidence_score": 0.94
  }
}
```

## 🔍 Content Detection Patterns

### Part Detection
- `PART 1: Electrostatics`
- `BOOK II: Magnetism`
- `FIRST PART: Fundamental Principles`

### Chapter Detection
- `CHAPTER 1: Description of Motion`
- `Chap. 2: Coulomb's Law`
- `1: Introduction to Electrostatics`

### Article Detection
- `ARTICLE 1: Introductory`
- `Art. 2: Preliminary Notions`
- `1. Fundamental Concepts`
- `15. Coulomb's Experiment`

## 📊 Generated Reports

### Volume Metadata (`volume_metadata.json`)
```json
{
  "volume_number": 1,
  "title": "Volume 1",
  "total_pages": 572,
  "total_parts": 3,
  "total_chapters": 21,
  "total_articles": 785,
  "created_at": "2025-11-28T16:30:00",
  "structure_summary": {
    "parts": [
      {
        "part_number": 1,
        "title": "Electrostatics",
        "page_range": "1-200",
        "chapter_count": 7
      }
    ]
  }
}
```

### Master Index (`MASTER_TOC_INDEX.json`)
```json
{
  "maxwell_toc_index": {
    "created_at": "2025-11-28T16:30:00",
    "total_volumes": 2,
    "volumes": {
      "1": {
        "title": "Volume 1",
        "total_pages": 572,
        "total_parts": 3,
        "total_chapters": 21,
        "total_articles": 785,
        "path": "Volume_1"
      },
      "2": {
        "title": "Volume 2",
        "total_pages": 544,
        "total_parts": 2,
        "total_chapters": 18,
        "total_articles": 642,
        "path": "Volume_2"
      }
    },
    "navigation": {
      "volume_structure": "Volume_X/Part_XX_Title/Chapter_XXX_Title/Article_XXXX_Title.json",
      "metadata_files": "Each level has a metadata.json file with structural information",
      "article_content": "Each article contains full content, equations, and figures"
    }
  }
}
```

## 🛠️ Advanced Usage Examples

### Extract Specific Volume with Custom Output
```bash
python maxwell_toc_extractor.py --volume 1 --base-dir Maxwell_Volume_1_TOC --verbose
```

### Process Both Volumes for Research
```bash
# Create research-friendly structure
python maxwell_toc_extractor.py --base-dir Maxwell_Research_TOC

# Navigate to specific article
cd Maxwell_Research_TOC/Volume_1/Part_01_Electrostatics/Chapter_002_Coulombs_Law/
cat Article_0015_Coulombs_Experiment.json | jq '.content.mathpix_markdown'
```

### Extract Mathematical Content Only
```python
import json
from pathlib import Path

# Load an article
article_path = Path("Maxwell_TOC/Volume_1/Part_01_Electrostatics/Chapter_001_Description_of_Motion/Article_0001_Introductory.json")

with open(article_path, 'r') as f:
    article = json.load(f)

# Extract all equations from the article
equations = article['equations']
for eq in equations:
    print(f"Equation {eq['equation_id']}: {eq['latex']}")

# Extract all mathematical content
mathematical_content = []
if article['content']['mathpix_markdown']:
    lines = article['content']['mathpix_markdown'].split('\n')
    for line in lines:
        if any(char in line for char in ['$', '\\', '∫', '∑', '∏']):
            mathematical_content.append(line.strip())
```

## 🔧 Integration with Existing Pipeline

The TOC extractor automatically looks for JSON files generated by the Maxwell EM processor:

```
MAXWELL_VOLUME_1_MASTER_OUTPUT/volume_1_direct_result.json
MAXWELL_VOLUME_2_MASTER_OUTPUT/volume_2_direct_result.json
```

### Prerequisites
1. Run the Maxwell EM processor pipeline first
2. Ensure JSON files are in the expected locations
3. Run the TOC extractor

### Workflow
```bash
# 1. Process volumes (if not already done)
python main_pipeline.py --pdf "15773-A Treatise On Electricity And Magnetism Vol-i.pdf" --volume 1 --stage full
python main_pipeline.py --pdf "15774-A Treatise On Electricity And Magnetism Vol-ii.pdf" --volume 2 --stage full

# 2. Extract TOC and create hierarchy
python maxwell_toc_extractor.py

# 3. Explore the structured content
ls -la Maxwell_TOC/Volume_1/Part_01_Electrostatics/
```

## 📈 Expected Output Statistics

Based on Maxwell's treatise structure:

### Volume 1 (Electrostatics & Electrokinematics)
- **Parts**: 3 major sections
- **Chapters**: 20+ chapters
- **Articles**: 700+ individual articles
- **Equations**: 5000+ mathematical expressions
- **Figures**: 200+ diagrams and illustrations

### Volume 2 (Magnetism & Electromagnetism)
- **Parts**: 2 major sections
- **Chapters**: 15+ chapters
- **Articles**: 600+ individual articles
- **Equations**: 4000+ mathematical expressions
- **Figures**: 150+ diagrams and illustrations

## 🎯 Use Cases

### Academic Research
- Navigate specific articles and sections
- Extract mathematical content for analysis
- Cross-reference between volumes
- Study content organization and structure

### Content Analysis
- Analyze equation distribution across volumes
- Study figure and diagram placement
- Examine writing patterns and structure
- Content mining and text analysis

### Educational Applications
- Create study guides and summaries
- Extract specific topics for teaching
- Generate practice problems from equations
- Build interactive content browsers

### Digital Humanities
- Text mining and analysis
- Historical content analysis
- Structure and organization studies
- Cross-referencing and citation analysis

## 🚀 Quick Start

1. **Ensure volumes are processed**:
   ```bash
   ls MAXWELL_VOLUME_1_MASTER_OUTPUT/volume_1_direct_result.json
   ls MAXWELL_VOLUME_2_MASTER_OUTPUT/volume_2_direct_result.json
   ```

2. **Run TOC extractor**:
   ```bash
   python maxwell_toc_extractor.py
   ```

3. **Explore the structure**:
   ```bash
   tree Maxwell_TOC/ -L 3
   cat Maxwell_TOC/MASTER_TOC_INDEX.json
   ```

4. **Access specific content**:
   ```bash
   # Find articles about Coulomb's Law
   find Maxwell_TOC -name "*.json" -exec grep -l "Coulomb" {} \;

   # Extract equations from a specific article
   python -c "
   import json
   with open('Maxwell_TOC/Volume_1/Part_01_Electrostatics/Chapter_002_Coulombs_Law/Article_0015_Coulombs_Experiment.json') as f:
       article = json.load(f)
   for eq in article['equations']:
       print(eq['latex'])
   "
   ```

The Maxwell TOC Extractor provides a **comprehensive, hierarchical organization** of Maxwell's complete electromagnetic theory treatise with **individual JSON files for each article** containing full content, equations, figures, and metadata - perfect for research, analysis, and content exploration! 🎯