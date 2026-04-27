# Maxwell EM Processor - Complete JSON Schema & Variable Access Guide

## 📋 EXECUTIVE SUMMARY

This document provides the **EXACT SCHEMA** for `volume_x_direct_result.json` files with **ALL CHILDREN** and **COMPREHENSIVE VARIABLE ACCESS PATTERNS**. Every nested object, field, and data type is documented for precise programmatic access.

## 🏗️ COMPLETE JSON SCHEMA HIERARCHY

### ROOT LEVEL SCHEMA

```json
{
  "pdf_id": "string",
  "volume_type": "string",
  "total_pages": "integer",
  "pages": "PAGES_OBJECT",
  "output_files": "OUTPUT_FILES_OBJECT",
  "processing_status": "PROCESSING_STATUS_OBJECT",
  "processing_started": "datetime_string",
  "processing_completed": "datetime_string",
  "total_processing_time_seconds": "float",
  "total_equations": "integer",
  "total_figures": "integer",
  "total_lines": "integer",
  "average_confidence": "float",
  "pages_with_low_confidence": "array[integer]"
}
```

### 1. PAGES OBJECT SCHEMA

```json
"pages": {
  "PAGE_NUMBER_KEY": {
    "page_number": "integer",
    "pdf_id": "string",
    "raw_text": "string",
    "mathpix_markdown": "string",
    "standard_markdown": "string|null",
    "line_data": "LINE_DATA_ARRAY",
    "equations": "EQUATIONS_ARRAY",
    "figures": "FIGURES_ARRAY",
    "page_width": "integer|null",
    "page_height": "integer|null",
    "confidence_score": "float",
    "average_confidence_rate": "float",
    "processing_time_seconds": "float",
    "mathpix_request_id": "string",
    "ocr_timestamp": "datetime_string"
  }
}
```

### 2. LINE DATA ARRAY SCHEMA

```json
"line_data": [
  {
    "id": "string",
    "parent_id": "string|null",
    "children_ids": "array[string]",
    "type": "string",
    "subtype": "string|null",
    "line": "integer",
    "column": "integer|null",
    "font_size": "integer|null",
    "text": "string",
    "text_display": "string",
    "conversion_output": "boolean",
    "is_printed": "boolean",
    "is_handwritten": "boolean",
    "region": "BOUNDING_BOX_OBJECT",
    "cnt": "array[array[integer]]",
    "confidence": "float|null",
    "confidence_rate": "float|null",
    "metadata": "object"
  }
]
```

### 3. BOUNDING BOX OBJECT SCHEMA

```json
"region": {
  "top_left_x": "integer",
  "top_left_y": "integer",
  "width": "integer",
  "height": "integer"
}
```

### 4. EQUATIONS ARRAY SCHEMA

```json
"equations": [
  {
    "equation_id": "string",
    "latex": "string",
    "mathml": "string|null",
    "location": "BOUNDING_BOX_OBJECT",
    "confidence": "float",
    "line_id": "string|null"
  }
]
```

### 5. FIGURES ARRAY SCHEMA

```json
"figures": [
  {
    "figure_id": "string",
    "image_path": "string",
    "caption": "string|null",
    "location": "BOUNDING_BOX_OBJECT",
    "description": "string|null",
    "line_id": "string|null"
  }
]
```

### 6. OUTPUT FILES OBJECT SCHEMA

```json
"output_files": {
  "mmd_file": "string|null",
  "md_file": "string|null",
  "docx_file": "string|null",
  "pptx_file": "string|null",
  "html_file": "string|null",
  "pdf_html_file": "string|null",
  "pdf_latex_file": "string|null",
  "latex_zip_file": "string|null",
  "mmd_zip_file": "string|null",
  "md_zip_file": "string|null",
  "html_zip_file": "string|null",
  "lines_json_file": "string|null",
  "raw_api_response_file": "string|null"
}
```

### 7. PROCESSING STATUS OBJECT SCHEMA

```json
"processing_status": {
  "status": "string",
  "num_pages": "integer|null",
  "num_pages_completed": "integer|null",
  "percent_done": "float|null",
  "conversion_status": "CONVERSION_STATUS_OBJECT"
}
```

### 8. CONVERSION STATUS OBJECT SCHEMA

```json
"conversion_status": {
  "FORMAT_KEY": {
    "format": "string",
    "status": "string",
    "file_path": "string|null",
    "error_info": "object|null"
  }
}
```

## 🔍 COMPLETE VARIABLE ACCESS REFERENCE

### ROOT LEVEL VARIABLES

| Variable Path | Data Type | Description | Access Pattern |
|---------------|-----------|-------------|----------------|
| `data['pdf_id']` | string | Unique PDF identifier | `str` |
| `data['volume_type']` | string | Volume identifier | `str` |
| `data['total_pages']` | int | Total pages processed | `int` |
| `data['total_equations']` | int | Total equations found | `int` |
| `data['total_figures']` | int | Total figures found | `int` |
| `data['total_lines']` | int | Total lines extracted | `int` |
| `data['average_confidence']` | float | Overall confidence (0-1) | `float` |
| `data['pages_with_low_confidence']` | array[int] | Low confidence page numbers | `list[int]` |
| `data['processing_started']` | datetime | Processing start time | `datetime` |
| `data['processing_completed']` | datetime | Processing end time | `datetime` |
| `data['total_processing_time_seconds']` | float | Total processing duration | `float` |

### PAGE LEVEL VARIABLES

| Variable Path | Data Type | Description | Access Pattern |
|---------------|-----------|-------------|----------------|
| `data['pages']['1']['page_number']` | int | Page number (1-indexed) | `int(page_key)` |
| `data['pages']['1']['pdf_id']` | string | Mathpix PDF ID | `str` |
| `data['pages']['1']['raw_text']` | string | Plain text content | `str` |
| `data['pages']['1']['mathpix_markdown']` | string | Mathpix Markdown | `str` |
| `data['pages']['1']['standard_markdown']` | string/null | Standard Markdown | `str or None` |
| `data['pages']['1']['page_width']` | int/null | Page width in pixels | `int or None` |
| `data['pages']['1']['page_height']` | int/null | Page height in pixels | `int or None` |
| `data['pages']['1']['confidence_score']` | float | Page confidence (0-1) | `float` |
| `data['pages']['1']['average_confidence_rate']` | float | Average confidence rate | `float` |
| `data['pages']['1']['processing_time_seconds']` | float | Page processing time | `float` |
| `data['pages']['1']['mathpix_request_id']` | string | Mathpix request ID | `str` |
| `data['pages']['1']['ocr_timestamp']` | datetime | OCR timestamp | `datetime` |

### LINE DATA VARIABLES

| Variable Path | Data Type | Description | Access Pattern |
|---------------|-----------|-------------|----------------|
| `data['pages']['1']['line_data'][0]['id']` | string | Unique line identifier | `str` |
| `data['pages']['1']['line_data'][0]['parent_id']` | string/null | Parent line ID | `str or None` |
| `data['pages']['1']['line_data'][0]['children_ids']` | array[string] | Child line IDs | `list[str]` |
| `data['pages']['1']['line_data'][0]['type']` | string | Content type | `str` |
| `data['pages']['1']['line_data'][0]['subtype']` | string/null | Subtype | `str or None` |
| `data['pages']['1']['line_data'][0]['line']` | int | Line number on page | `int` |
| `data['pages']['1']['line_data'][0]['column']` | int/null | Column number | `int or None` |
| `data['pages']['1']['line_data'][0]['font_size']` | int/null | Font size | `int or None` |
| `data['pages']['1']['line_data'][0]['text']` | string | Extracted text | `str` |
| `data['pages']['1']['line_data'][0]['text_display']` | string | Mathpix Markdown | `str` |
| `data['pages']['1']['line_data'][0]['conversion_output']` | bool | Include in output | `bool` |
| `data['pages']['1']['line_data'][0]['is_printed']` | bool | Is printed text | `bool` |
| `data['pages']['1']['line_data'][0]['is_handwritten']` | bool | Is handwritten | `bool` |
| `data['pages']['1']['line_data'][0]['confidence']` | float/null | Line confidence | `float or None` |
| `data['pages']['1']['line_data'][0]['confidence_rate']` | float/null | Confidence rate | `float or None` |

### BOUNDING BOX VARIABLES

| Variable Path | Data Type | Description | Access Pattern |
|---------------|-----------|-------------|----------------|
| `data['pages']['1']['line_data'][0]['region']['top_left_x']` | int | X coordinate | `int` |
| `data['pages']['1']['line_data'][0]['region']['top_left_y']` | int | Y coordinate | `int` |
| `data['pages']['1']['line_data'][0]['region']['width']` | int | Width | `int` |
| `data['pages']['1']['line_data'][0]['region']['height']` | int | Height | `int` |

### CONTOUR VARIABLES

| Variable Path | Data Type | Description | Access Pattern |
|---------------|-----------|-------------|----------------|
| `data['pages']['1']['line_data'][0]['cnt'][0][0]` | int | Point X coordinate | `int` |
| `data['pages']['1']['line_data'][0]['cnt'][0][1]` | int | Point Y coordinate | `int` |

### EQUATION VARIABLES

| Variable Path | Data Type | Description | Access Pattern |
|---------------|-----------|-------------|----------------|
| `data['pages']['1']['equations'][0]['equation_id']` | string | Equation ID | `str` |
| `data['pages']['1']['equations'][0]['latex']` | string | LaTeX code | `str` |
| `data['pages']['1']['equations'][0]['mathml']` | string/null | MathML code | `str or None` |
| `data['pages']['1']['equations'][0]['confidence']` | float | Equation confidence | `float` |
| `data['pages']['1']['equations'][0]['line_id']` | string/null | Source line ID | `str or None` |

### OUTPUT FILES VARIABLES

| Variable Path | Data Type | Description | Access Pattern |
|---------------|-----------|-------------|----------------|
| `data['output_files']['mmd_file']` | string/null | Mathpix Markdown file | `str or None` |
| `data['output_files']['md_file']` | string/null | Standard Markdown file | `str or None` |
| `data['output_files']['docx_file']` | string/null | Word document file | `str or None` |
| `data['output_files']['html_file']` | string/null | HTML file | `str or None` |
| `data['output_files']['latex_zip_file']` | string/null | LaTeX + images zip | `str or None` |
| `data['output_files']['lines_json_file']` | string/null | Line data JSON file | `str or None` |

### PROCESSING STATUS VARIABLES

| Variable Path | Data Type | Description | Access Pattern |
|---------------|-----------|-------------|----------------|
| `data['processing_status']['status']` | string | Processing status | `str` |
| `data['processing_status']['num_pages']` | int/null | Total pages | `int or None` |
| `data['processing_status']['num_pages_completed']` | int/null | Completed pages | `int or None` |
| `data['processing_status']['percent_done']` | float/null | Completion percentage | `float or None` |

## 🎯 CONTENT TYPES REFERENCE

### Line Data Content Types (`type` field)

- **`title`**: Document titles and headings
- **`text`**: Regular text content
- **`equation`**: Mathematical equations
- **`diagram`**: Diagrams and figures
- **`figure`**: Figure elements
- **`table`**: Table content
- **`section_header`**: Section headings
- **`authors`**: Author information
- **`footnote`**: Footnote content
- **`caption`**: Figure captions

### Processing Status Values

- **`received`**: PDF received
- **`loaded`**: PDF loaded
- **`split`**: PDF split into pages
- **`completed`**: Processing completed
- **`error`**: Processing failed

### Conversion Status Values

- **`processing`**: Format being converted
- **`completed`**: Conversion finished
- **`error`**: Conversion failed

## 🛠️ COMPREHENSIVE ACCESS PATTERNS

### Python Implementation Examples

```python
import json
from datetime import datetime

# Load data
with open('volume_1_direct_result.json', 'r') as f:
    data = json.load(f)

# ===== ROOT LEVEL ACCESS =====
def get_root_info(data):
    return {
        'pdf_id': data['pdf_id'],
        'volume_type': data['volume_type'],
        'total_pages': data['total_pages'],
        'total_equations': data['total_equations'],
        'total_figures': data['total_figures'],
        'total_lines': data['total_lines'],
        'average_confidence': data['average_confidence'],
        'low_confidence_pages': data['pages_with_low_confidence'],
        'processing_time': data['total_processing_time_seconds'],
        'start_time': datetime.fromisoformat(data['processing_started']),
        'end_time': datetime.fromisoformat(data['processing_completed'])
    }

# ===== PAGE LEVEL ACCESS =====
def get_page_info(data, page_num):
    page_key = str(page_num)
    if page_key not in data['pages']:
        return None

    page = data['pages'][page_key]
    return {
        'page_number': page['page_number'],
        'pdf_id': page['pdf_id'],
        'dimensions': (page['page_width'], page['page_height']),
        'confidence': page['confidence_score'],
        'line_count': len(page['line_data']),
        'equation_count': len(page['equations']),
        'figure_count': len(page['figures']),
        'raw_text_length': len(page['raw_text']),
        'mathpix_markdown_length': len(page['mathpix_markdown'])
    }

# ===== LINE DATA ACCESS =====
def get_line_info(data, page_num, line_index):
    page_key = str(page_num)
    if page_key not in data['pages']:
        return None

    lines = data['pages'][page_key]['line_data']
    if line_index >= len(lines):
        return None

    line = lines[line_index]
    return {
        'id': line['id'],
        'parent_id': line['parent_id'],
        'children_count': len(line['children_ids']),
        'type': line['type'],
        'subtype': line['subtype'],
        'position': (line['line'], line['column']),
        'font_size': line['font_size'],
        'text': line['text'],
        'text_display': line['text_display'],
        'is_printed': line['is_printed'],
        'is_handwritten': line['is_handwritten'],
        'conversion_output': line['conversion_output'],
        'confidence': line['confidence'],
        'confidence_rate': line['confidence_rate'],
        'bounding_box': line['region'],
        'contour_points': len(line['cnt']),
        'metadata_keys': list(line['metadata'].keys())
    }

# ===== BOUNDING BOX ACCESS =====
def get_bounding_box(data, page_num, line_index):
    line = get_line_info(data, page_num, line_index)
    if not line or not line['bounding_box']:
        return None

    region = line['bounding_box']
    return {
        'x': region['top_left_x'],
        'y': region['top_left_y'],
        'width': region['width'],
        'height': region['height'],
        'right': region['top_left_x'] + region['width'],
        'bottom': region['top_left_y'] + region['height'],
        'area': region['width'] * region['height']
    }

# ===== EQUATION ACCESS =====
def get_equations(data, page_num):
    page_key = str(page_num)
    if page_key not in data['pages']:
        return []

    equations = []
    for eq in data['pages'][page_key]['equations']:
        equations.append({
            'id': eq['equation_id'],
            'latex': eq['latex'],
            'mathml': eq['mathml'],
            'confidence': eq['confidence'],
            'line_id': eq['line_id'],
            'location': eq['location']
        })
    return equations

# ===== FIGURE ACCESS =====
def get_figures(data, page_num):
    page_key = str(page_num)
    if page_key not in data['pages']:
        return []

    figures = []
    for fig in data['pages'][page_key]['figures']:
        figures.append({
            'id': fig['figure_id'],
            'image_path': fig['image_path'],
            'caption': fig['caption'],
            'description': fig['description'],
            'line_id': fig['line_id'],
            'location': fig['location']
        })
    return figures

# ===== OUTPUT FILES ACCESS =====
def get_output_files(data):
    files = data['output_files']
    available_files = {}
    for key, path in files.items():
        if path:  # Only include non-null files
            available_files[key] = path
    return available_files

# ===== PROCESSING STATUS ACCESS =====
def get_processing_status(data):
    status = data['processing_status']
    return {
        'status': status['status'],
        'total_pages': status['num_pages'],
        'completed_pages': status['num_pages_completed'],
        'percent_done': status['percent_done'],
        'conversion_status': status['conversion_status']
    }

# ===== ADVANCED QUERIES =====
def find_lines_by_type(data, content_type):
    """Find all lines of a specific type across all pages"""
    results = []
    for page_num, page_data in data['pages'].items():
        for line_idx, line in enumerate(page_data['line_data']):
            if line['type'] == content_type:
                results.append({
                    'page': int(page_num),
                    'line_index': line_idx,
                    'line_data': line
                })
    return results

def get_content_hierarchy(data, page_num):
    """Get hierarchical content structure for a page"""
    page_key = str(page_num)
    if page_key not in data['pages']:
        return {}

    hierarchy = {}
    lines = data['pages'][page_key]['line_data']

    for line in lines:
        line_info = {
            'id': line['id'],
            'type': line['type'],
            'text': line['text'],
            'children': [],
            'parent': line['parent_id']
        }

        if line['parent_id'] is None:
            # Top-level element
            hierarchy[line['id']] = line_info
        else:
            # Child element
            if line['parent_id'] in hierarchy:
                hierarchy[line['parent_id']]['children'].append(line_info)

    return hierarchy

def get_geometry_analysis(data, page_num):
    """Analyze page geometry and layout"""
    page_key = str(page_num)
    if page_key not in data['pages']:
        return {}

    page = data['pages'][page_key]
    lines = page['line_data']

    if not lines:
        return {'no_lines': True}

    # Calculate layout statistics
    x_coords = []
    y_coords = []
    widths = []
    heights = []

    for line in lines:
        if line['region']:
            region = line['region']
            x_coords.extend([region['top_left_x'], region['top_left_x'] + region['width']])
            y_coords.extend([region['top_left_y'], region['top_left_y'] + region['height']])
            widths.append(region['width'])
            heights.append(region['height'])

    return {
        'page_dimensions': (page['page_width'], page['page_height']),
        'content_bounds': {
            'min_x': min(x_coords) if x_coords else 0,
            'max_x': max(x_coords) if x_coords else 0,
            'min_y': min(y_coords) if y_coords else 0,
            'max_y': max(y_coords) if y_coords else 0
        },
        'content_distribution': {
            'mean_width': sum(widths) / len(widths) if widths else 0,
            'mean_height': sum(heights) / len(heights) if heights else 0,
            'content_area': sum(w * h for w, h in zip(widths, heights))
        }
    }
```

### JavaScript Implementation Examples

```javascript
// Load data
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('volume_1_direct_result.json', 'utf8'));

// ===== ROOT LEVEL ACCESS =====
function getRootInfo(data) {
    return {
        pdfId: data.pdf_id,
        volumeType: data.volume_type,
        totalPages: data.total_pages,
        totalEquations: data.total_equations,
        totalFigures: data.total_figures,
        totalLines: data.total_lines,
        averageConfidence: data.average_confidence,
        lowConfidencePages: data.pages_with_low_confidence,
        processingTime: data.total_processing_time_seconds,
        startTime: new Date(data.processing_started),
        endTime: new Date(data.processing_completed)
    };
}

// ===== PAGE LEVEL ACCESS =====
function getPageInfo(data, page_num) {
    const page_key = page_num.toString();
    if (!data.pages[page_key]) return null;

    const page = data.pages[page_key];
    return {
        pageNumber: page.page_number,
        pdfId: page.pdf_id,
        dimensions: [page.page_width, page.page_height],
        confidence: page.confidence_score,
        lineCount: page.line_data.length,
        equationCount: page.equations.length,
        figureCount: page.figures.length,
        rawTextLength: page.raw_text.length,
        mathpixMarkdownLength: page.mathpix_markdown.length
    };
}

// ===== LINE DATA ACCESS =====
function getLineInfo(data, page_num, line_index) {
    const page_key = page_num.toString();
    if (!data.pages[page_key]) return null;

    const lines = data.pages[page_key].line_data;
    if (line_index >= lines.length) return null;

    const line = lines[line_index];
    return {
        id: line.id,
        parentId: line.parent_id,
        childrenCount: line.children_ids.length,
        type: line.type,
        subtype: line.subtype,
        position: [line.line, line.column],
        fontSize: line.font_size,
        text: line.text,
        textDisplay: line.text_display,
        isPrinted: line.is_printed,
        isHandwritten: line.is_handwritten,
        conversionOutput: line.conversion_output,
        confidence: line.confidence,
        confidenceRate: line.confidence_rate,
        boundingBox: line.region,
        contourPoints: line.cnt.length,
        metadataKeys: Object.keys(line.metadata)
    };
}

// ===== UTILITY FUNCTIONS =====
function getAllContentByType(data, type) {
    const results = [];
    Object.entries(data.pages).forEach(([page_num, page_data]) => {
        page_data.line_data.forEach((line, line_idx) => {
            if (line.type === type) {
                results.push({
                    page: parseInt(page_num),
                    lineIndex: line_idx,
                    line: line
                });
            }
        });
    });
    return results;
}

function getContentStats(data) {
    const stats = {
        pages: Object.keys(data.pages).length,
        totalLines: 0,
        totalEquations: 0,
        contentTypeDistribution: {},
        confidenceStats: {
            high: 0, // >= 0.9
            medium: 0, // 0.7 - 0.9
            low: 0 // < 0.7
        }
    };

    Object.values(data.pages).forEach(page => {
        stats.totalLines += page.line_data.length;
        stats.totalEquations += page.equations.length;

        page.line_data.forEach(line => {
            // Count content types
            stats.contentTypeDistribution[line.type] =
                (stats.contentTypeDistribution[line.type] || 0) + 1;

            // Count confidence levels
            if (line.confidence >= 0.9) stats.confidenceStats.high++;
            else if (line.confidence >= 0.7) stats.confidenceStats.medium++;
            else stats.confidenceStats.low++;
        });
    });

    return stats;
}
```

## 📊 COMPLETE FIELD REFERENCE TABLE

| Level | Field Path | Type | Required | Description |
|-------|------------|------|----------|-------------|
| Root | `pdf_id` | string | ✓ | Unique PDF identifier |
| Root | `volume_type` | string | ✓ | Volume identifier |
| Root | `total_pages` | integer | ✓ | Total pages processed |
| Root | `pages` | object | ✓ | Pages data |
| Root | `output_files` | object | ✓ | Output files info |
| Root | `processing_status` | object | ✓ | Processing status |
| Root | `processing_started` | string | ✓ | Start timestamp |
| Root | `processing_completed` | string | ✗ | End timestamp |
| Root | `total_processing_time_seconds` | float | ✗ | Processing duration |
| Root | `total_equations` | integer | ✓ | Total equations |
| Root | `total_figures` | integer | ✓ | Total figures |
| Root | `total_lines` | integer | ✓ | Total lines |
| Root | `average_confidence` | float | ✓ | Average confidence |
| Root | `pages_with_low_confidence` | array | ✓ | Low confidence pages |
| Page | `page_number` | integer | ✓ | Page number |
| Page | `pdf_id` | string | ✓ | Mathpix PDF ID |
| Page | `raw_text` | string | ✓ | Plain text |
| Page | `mathpix_markdown` | string | ✓ | Mathpix Markdown |
| Page | `standard_markdown` | string | ✗ | Standard Markdown |
| Page | `line_data` | array | ✓ | Line data array |
| Page | `equations` | array | ✓ | Equations array |
| Page | `figures` | array | ✓ | Figures array |
| Page | `page_width` | integer | ✗ | Page width |
| Page | `page_height` | integer | ✗ | Page height |
| Page | `confidence_score` | float | ✓ | Page confidence |
| Page | `average_confidence_rate` | float | ✓ | Average confidence rate |
| Page | `processing_time_seconds` | float | ✓ | Processing time |
| Page | `mathpix_request_id` | string | ✓ | Request ID |
| Page | `ocr_timestamp` | string | ✓ | OCR timestamp |
| Line | `id` | string | ✓ | Line ID |
| Line | `parent_id` | string | ✗ | Parent line ID |
| Line | `children_ids` | array | ✓ | Child line IDs |
| Line | `type` | string | ✓ | Content type |
| Line | `subtype` | string | ✗ | Content subtype |
| Line | `line` | integer | ✓ | Line number |
| Line | `column` | integer | ✗ | Column number |
| Line | `font_size` | integer | ✗ | Font size |
| Line | `text` | string | ✓ | Extracted text |
| Line | `text_display` | string | ✓ | Display text |
| Line | `conversion_output` | boolean | ✓ | Include in output |
| Line | `is_printed` | boolean | ✓ | Is printed |
| Line | `is_handwritten` | boolean | ✓ | Is handwritten |
| Line | `region` | object | ✗ | Bounding box |
| Line | `cnt` | array | ✓ | Contour points |
| Line | `confidence` | float | ✗ | Line confidence |
| Line | `confidence_rate` | float | ✗ | Confidence rate |
| Line | `metadata` | object | ✓ | Additional metadata |
| Region | `top_left_x` | integer | ✓ | X coordinate |
| Region | `top_left_y` | integer | ✓ | Y coordinate |
| Region | `width` | integer | ✓ | Width |
| Region | `height` | integer | ✓ | Height |
| Equation | `equation_id` | string | ✓ | Equation ID |
| Equation | `latex` | string | ✓ | LaTeX code |
| Equation | `mathml` | string | ✗ | MathML code |
| Equation | `location` | object | ✗ | Bounding box |
| Equation | `confidence` | float | ✓ | Equation confidence |
| Equation | `line_id` | string | ✗ | Source line ID |
| Figure | `figure_id` | string | ✓ | Figure ID |
| Figure | `image_path` | string | ✓ | Image path |
| Figure | `caption` | string | ✗ | Caption |
| Figure | `location` | object | ✗ | Bounding box |
| Figure | `description` | string | ✗ | Description |
| Figure | `line_id` | string | ✗ | Source line ID |
| Output | `mmd_file` | string | ✗ | Mathpix Markdown |
| Output | `md_file` | string | ✗ | Standard Markdown |
| Output | `docx_file` | string | ✗ | Word document |
| Output | `html_file` | string | ✗ | HTML file |
| Output | `latex_zip_file` | string | ✗ | LaTeX zip |
| Output | `lines_json_file` | string | ✗ | Lines JSON |
| Status | `status` | string | ✓ | Processing status |
| Status | `num_pages` | integer | ✗ | Total pages |
| Status | `num_pages_completed` | integer | ✗ | Completed pages |
| Status | `percent_done` | float | ✗ | Completion % |
| Status | `conversion_status` | object | ✓ | Conversion status |

## 🎯 QUICK ACCESS REFERENCE

### Most Common Access Patterns

```python
# Get total statistics
total_pages = data['total_pages']
total_equations = data['total_equations']
total_lines = data['total_lines']
avg_confidence = data['average_confidence']

# Get page content
page_text = data['pages']['1']['raw_text']
page_markdown = data['pages']['1']['mathpix_markdown']

# Get all lines from page
lines = data['pages']['1']['line_data']
first_line_text = lines[0]['text']
first_line_type = lines[0]['type']

# Get bounding box coordinates
bbox = lines[0]['region']
x, y = bbox['top_left_x'], bbox['top_left_y']
width, height = bbox['width'], bbox['height']

# Get confidence scores
line_confidence = lines[0]['confidence']
page_confidence = data['pages']['1']['confidence_score']

# Get equations
equations = data['pages']['1']['equations']
first_equation_latex = equations[0]['latex']

# Check output files
mmd_file = data['output_files']['mmd_file']
docx_file = data['output_files']['docx_file']

# Get processing status
status = data['processing_status']['status']
percent_done = data['processing_status']['percent_done']
```

This comprehensive schema provides **exact field names, data types, and access patterns** for every element in the Maxwell EM processor JSON structure. All nested objects and their children are documented with precise variable access information.