"""
Data Models Module
Pydantic models for structured data throughout the pipeline
Enhanced with comprehensive Mathpix line data support for maximum information extraction
"""

from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from pathlib import Path


class ProcessingStage(str, Enum):
    """Processing pipeline stages"""
    OCR = "ocr"
    TOC_ANALYSIS = "toc_analysis"
    ORGANIZATION = "organization"


class VolumeType(str, Enum):
    """Volume types"""
    VOLUME_1 = "volume_1"
    VOLUME_2 = "volume_2"


# ========== TOC Models ==========

class Article(BaseModel):
    """Individual article in a chapter"""
    article_id: str
    article_number: int
    title: str
    page_start: int
    page_end: Optional[int] = None
    content_summary: Optional[str] = None
    equations: List[str] = Field(default_factory=list)
    figures: List[str] = Field(default_factory=list)


class Chapter(BaseModel):
    """Chapter in a book part"""
    chapter_id: str
    chapter_number: int
    title: str
    articles: Dict[str, Article] = Field(default_factory=dict)
    page_start: int
    page_end: Optional[int] = None


class Part(BaseModel):
    """Part of a volume (e.g., Electrostatics, Magnetism)"""
    part_id: str
    title: str
    chapters: Dict[str, Chapter] = Field(default_factory=dict)
    description: Optional[str] = None


class Volume(BaseModel):
    """Complete volume structure"""
    volume_id: str
    title: str
    parts: Dict[str, Part] = Field(default_factory=dict)
    preliminary_sections: Dict[str, Any] = Field(default_factory=dict)


class TOCStructure(BaseModel):
    """Complete table of contents structure"""
    volumes: Dict[str, Volume] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)


# ========== Enhanced Mathpix OCR Models ==========

class BoundingBox(BaseModel):
    """Bounding box for page elements (Mathpix region)"""
    top_left_x: int
    top_left_y: int
    width: int
    height: int


class PdfLineData(BaseModel):
    """
    Comprehensive line data from Mathpix API
    Full geometric and metadata information for maximum flexibility
    """
    # Identity and Hierarchy
    id: str
    parent_id: Optional[str] = None
    children_ids: List[str] = Field(default_factory=list)
    
    # Classification
    type: str  # title, text, equation, authors, figure, table, section_header, etc.
    subtype: Optional[str] = None
    
    # Position and Layout
    line: int  # Line number on page
    column: Optional[int] = None
    font_size: Optional[int] = None
    
    # Content
    text: str  # Searchable text
    text_display: str  # Mathpix Markdown with context
    conversion_output: bool  # Whether included in final MMD output
    
    # Text Properties
    is_printed: bool
    is_handwritten: bool
    
    # Geometry - Rectangle
    region: Optional[BoundingBox] = None
    
    # Geometry - Contour (list of [x,y] pairs for precise boundaries)
    cnt: List[List[int]] = Field(default_factory=list)
    
    # Confidence Metrics
    confidence: Optional[float] = None  # Overall line confidence [0,1]
    confidence_rate: Optional[float] = None  # Per-token geometric mean [0,1]
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PdfPageData(BaseModel):
    """Complete data for a single PDF page"""
    image_id: str  # Format: {pdf_id}-{page_num:02d}
    page: int  # Page number (1-indexed)
    page_height: Optional[int] = None  # Pixel height
    page_width: Optional[int] = None  # Pixel width
    lines: List[PdfLineData] = Field(default_factory=list)


class Equation(BaseModel):
    """Mathematical equation extracted from OCR"""
    equation_id: str
    latex: str
    mathml: Optional[str] = None
    location: Optional[BoundingBox] = None
    confidence: float = 1.0
    line_id: Optional[str] = None  # Reference to PdfLineData.id


class Figure(BaseModel):
    """Figure or diagram from page"""
    figure_id: str
    image_path: str
    caption: Optional[str] = None
    location: Optional[BoundingBox] = None
    description: Optional[str] = None
    line_id: Optional[str] = None  # Reference to PdfLineData.id


class ConversionFormat(BaseModel):
    """Status of a specific output format conversion"""
    format: str  # docx, tex.zip, html, pptx, etc.
    status: str  # processing, completed, error
    file_path: Optional[str] = None
    error_info: Optional[Dict[str, Any]] = None


class ProcessingStatus(BaseModel):
    """Overall PDF processing status from Mathpix"""
    status: str  # received, loaded, split, completed, error
    num_pages: Optional[int] = None
    num_pages_completed: Optional[int] = None
    percent_done: Optional[float] = None
    conversion_status: Dict[str, ConversionFormat] = Field(default_factory=dict)


class PageOCRResult(BaseModel):
    """Enhanced OCR result for a single page"""
    page_number: int
    pdf_id: str
    
    # Raw content
    raw_text: str
    mathpix_markdown: str  # MMD format
    standard_markdown: Optional[str] = None  # MD format
    
    # Comprehensive line-by-line data with ALL Mathpix fields
    line_data: List[PdfLineData] = Field(default_factory=list)
    
    # Extracted elements (derived from line_data)
    equations: List[Equation] = Field(default_factory=list)
    figures: List[Figure] = Field(default_factory=list)
    
    # Page geometry
    page_width: Optional[int] = None
    page_height: Optional[int] = None
    
    # Quality metrics
    confidence_score: float = 1.0
    average_confidence_rate: float = 1.0
    processing_time_seconds: float
    
    # Metadata
    mathpix_request_id: Optional[str] = None
    ocr_timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        arbitrary_types_allowed = True


class OutputFiles(BaseModel):
    """All output files from Mathpix processing - maximum flexibility"""
    # Primary text formats
    mmd_file: Optional[str] = None  # Mathpix Markdown (primary)
    md_file: Optional[str] = None  # Standard Markdown
    
    # Document formats
    docx_file: Optional[str] = None  # Microsoft Word
    pptx_file: Optional[str] = None  # PowerPoint
    html_file: Optional[str] = None  # HTML rendering
    
    # PDF formats
    pdf_html_file: Optional[str] = None  # PDF with HTML rendering
    pdf_latex_file: Optional[str] = None  # PDF with LaTeX (selectable equations)
    
    # Archive formats (includes images)
    latex_zip_file: Optional[str] = None  # LaTeX + images
    mmd_zip_file: Optional[str] = None  # MMD + images
    md_zip_file: Optional[str] = None  # MD + images
    html_zip_file: Optional[str] = None  # HTML + images
    
    # Structured data
    lines_json_file: Optional[str] = None  # Comprehensive line-by-line data
    
    # Raw data
    raw_api_response_file: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        arbitrary_types_allowed = True


class PDFOCRResult(BaseModel):
    """Complete OCR result for a PDF with maximum information extraction"""
    pdf_id: str
    volume_type: VolumeType
    total_pages: int

    # Page-level results with full line data
    pages: Dict[int, PageOCRResult] = Field(default_factory=dict)

    # All output files in multiple formats
    output_files: OutputFiles = Field(default_factory=OutputFiles)

    # Processing metadata
    processing_status: ProcessingStatus
    processing_started: datetime = Field(default_factory=datetime.now)
    processing_completed: Optional[datetime] = None
    total_processing_time_seconds: Optional[float] = None

    # Statistics for entire PDF
    total_equations: int = 0
    total_figures: int = 0
    total_lines: int = 0
    average_confidence: float = 0.0
    pages_with_low_confidence: List[int] = Field(default_factory=list)  # confidence < 0.7

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        arbitrary_types_allowed = True


# ========== Content Organization Models ==========

class ContentClassification(BaseModel):
    """Page classification based on TOC page numbers (deterministic)"""
    detected_part: Optional[str] = None
    detected_chapter: Optional[str] = None
    detected_article: Optional[str] = None
    confidence_score: float  # 1.0 for TOC-based, <1.0 if uncertain
    reasoning: str  # Explanation of classification source
    extracted_section_headers: List[str] = Field(default_factory=list)
    article_numbers_found: List[int] = Field(default_factory=list)


class OrganizedPage(BaseModel):
    """Page with organizational metadata"""
    page_number: int
    volume_id: str
    part_id: Optional[str] = None
    chapter_id: Optional[str] = None
    article_id: Optional[str] = None
    classification: ContentClassification
    file_path: str
    ocr_data: PageOCRResult


class OrganizationResult(BaseModel):
    """Results of content organization"""
    volume_id: str
    organized_pages: List[OrganizedPage] = Field(default_factory=list)
    folder_structure_created: Dict[str, str] = Field(default_factory=dict)
    organization_timestamp: datetime = Field(default_factory=datetime.now)
    statistics: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        arbitrary_types_allowed = True


# ========== Checkpoint Models ==========

class Checkpoint(BaseModel):
    """Processing checkpoint for resume capability"""
    stage: ProcessingStage
    volume_id: str
    completed: bool
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = Field(default_factory=dict)
    next_step: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        arbitrary_types_allowed = True


class PipelineState(BaseModel):
    """Complete pipeline state"""
    current_stage: ProcessingStage
    volume_id: str
    checkpoints: List[Checkpoint] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    completed: bool = False
    error_count: int = 0

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        arbitrary_types_allowed = True


# ========== API Models ==========

class MathpixAPIRequest(BaseModel):
    """Mathpix API request configuration"""
    file_path: Optional[str] = None
    url: Optional[str] = None
    conversion_formats: Dict[str, bool] = Field(default_factory=dict)
    page_ranges: Optional[str] = None
    streaming: bool = False
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class APICache(BaseModel):
    """Cached API response"""
    cache_key: str
    api_name: str
    request_data: Dict[str, Any]
    response_data: Dict[str, Any]
    cached_at: datetime = Field(default_factory=datetime.now)
    hit_count: int = 0

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        arbitrary_types_allowed = True


# ========== Statistics Models ==========

class ProcessingStatistics(BaseModel):
    """Overall processing statistics"""
    stage: ProcessingStage
    volume_id: str
    total_items: int
    processed_items: int
    failed_items: int
    success_rate: float = 0.0
    total_api_calls: int = 0
    cached_responses: int = 0
    processing_time_seconds: float = 0.0
    average_time_per_item: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @field_validator('success_rate', mode='before')
    def calculate_success_rate(cls, v, values):
        processed = values.data.get('processed_items', 0)
        failed = values.data.get('failed_items', 0)
        total = processed + failed
        return (processed / total * 100) if total > 0 else 0.0


# Utility functions for model serialization

def save_model_to_json(model: BaseModel, file_path: Path):
    """Save Pydantic model to JSON file"""
    import json
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(model.model_dump(), f, indent=2, ensure_ascii=False, default=str)


def load_model_from_json(model_class: type[BaseModel], file_path: Path) -> BaseModel:
    """Load Pydantic model from JSON file"""
    import json
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return model_class(**data)