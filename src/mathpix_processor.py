"""
Mathpix Processor Module - PRODUCTION GRADE
Comprehensive PDF OCR processing with maximum information extraction
Designed for 500+ page scientific PDFs with all Mathpix output formats
"""

import time
import hashlib
import json
import requests
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from src.data_models import (
    PDFOCRResult, PageOCRResult, PdfLineData, PdfPageData,
    Equation, Figure, BoundingBox, VolumeType, ProcessingStatus,
    ConversionFormat, OutputFiles, save_model_to_json
)
from src.logger_config import get_logger, get_api_logger
from src.circuit_breaker import get_mathpix_circuit_breaker
from src.retry_handler import get_mathpix_retry_handler, get_smart_retry_handler
from config.config import get_settings, get_paths


class MathpixProcessor:
    """
    Production-grade Mathpix API processor
    Handles large PDFs with comprehensive data extraction
    """

    def __init__(self):
        self.settings = get_settings()
        self.paths = get_paths()
        self.logger = get_logger('mathpix_processor')
        self.api_logger = get_api_logger(
            self.paths.mathpix_cache_dir,
            'mathpix'
        )

        # Reliability components
        self.circuit_breaker = get_mathpix_circuit_breaker()
        self.retry_handler = get_mathpix_retry_handler()

        # Mathpix API endpoints
        self.base_url = self.settings.mathpix_url
        self.pdf_endpoint = f"{self.base_url}/v3/pdf"
        self.converter_endpoint = f"{self.base_url}/v3/converter"

        # Headers
        self.headers = {
            "app_id": self.settings.mathpix_app_id,
            "app_key": self.settings.mathpix_app_key
        }

        self.logger.info("Mathpix processor initialized with reliability enhancements")
    
    def process_pdf(
        self,
        pdf_path: Path,
        volume_type: VolumeType,
        page_ranges: Optional[str] = None
    ) -> PDFOCRResult:
        """
        Process complete PDF with ALL output formats
        
        Args:
            pdf_path: Path to PDF file
            volume_type: Volume identifier
            page_ranges: Optional page range (e.g., "1-50,100-150")
        
        Returns:
            Complete PDF OCR result with all formats
        """
        self.logger.info(f"Starting comprehensive PDF processing: {pdf_path}")
        
        # Generate PDF ID
        pdf_id = self._generate_pdf_id(pdf_path)
        
        # Check cache
        if self.settings.enable_api_caching:
            cached_result = self._load_cached_result(pdf_id)
            if cached_result:
                self.logger.info(f"Using cached result for {pdf_id}")
                return cached_result
        
        # Step 1: Upload PDF and request ALL conversions
        mathpix_pdf_id = self._upload_pdf(pdf_path, page_ranges)
        
        # Step 2: Poll for processing completion
        self._wait_for_processing(mathpix_pdf_id)
        
        # Step 3: Poll for ALL conversion completions
        self._wait_for_conversions(mathpix_pdf_id)
        
        # Step 4: Download ALL output formats
        output_files = self._download_all_formats(mathpix_pdf_id, volume_type)
        
        # Step 5: Parse comprehensive line data
        pages_data = self._parse_lines_json(mathpix_pdf_id, output_files.lines_json_file)
        
        # Step 6: Build complete result
        result = self._build_ocr_result(
            pdf_id,
            mathpix_pdf_id,
            volume_type,
            pages_data,
            output_files
        )
        
        # Cache result
        if self.settings.enable_api_caching:
            self._cache_result(pdf_id, result)
        
        self.logger.info(
            f"PDF processing complete: {result.total_pages} pages, "
            f"{result.total_lines} lines, {result.total_equations} equations"
        )
        
        return result
    
    def _upload_pdf(self, pdf_path: Path, page_ranges: Optional[str]) -> str:
        """
        Upload PDF and request ALL conversion formats with reliability enhancements

        Returns:
            Mathpix pdf_id
        """
        self.logger.info(f"Uploading PDF with reliability enhancements: {pdf_path}")

        # Define the upload function for retry/circuit breaker
        def upload_function():
            # Request ALL conversion formats simultaneously
            options = {
                "conversion_formats": {
                    "docx": True,
                    "md": True,
                    "tex.zip": True,
                    "html": True,
                    "latex.pdf": False,  # DISABLE: Too heavy, causes timeouts/internal errors
                    "pdf": False,      # DISABLE: Too heavy, causes timeouts/internal errors
                    "pptx": False,      # DISABLE: Unlikely needed for a textbook
                    "md.zip": True,
                    "html.zip": True
                },
                # Enhanced options for Maxwell's electromagnetic theory
                "enable_tables_fallback": True,  # Complex tables
                "include_equation_tags": True,  # Equation numbering
                "idiomatic_eqn_arrays": True,  # Better equation formatting
                "rm_spaces": True,  # Clean whitespace
                "include_smiles": False,  # DISABLE: Chemistry parsing for Physics textbook
                "numbers_default_to_math": False,  # Keep numbers as text when appropriate
                "math_inline_delimiters": ["$", "$"],
                "math_display_delimiters": ["$$", "$$"],

                # NEW: Strategic enhancements from Mathpix API analysis
                "enable_geometry": True,           # Preserve geometric layout
                "extract_inline_math": True,       # Better inline equation handling
                "math_dollar_inline": True,        # Dollar sign inline math
                "bracket_inline_math": True,       # Bracket inline math
                "enable_experimental_features": False,  # Keep disabled for stability
                "include_fonts": True,             # Font analysis
                "analyze_diagrams": True,          # Enhanced diagram processing
                "include_diagram_text": True,      # NEW: Extract text from diagrams (Mathpix recommendation)
                "extract_bibliography": False,     # DISABLE: Not needed for Maxwell treatise
                "preserve_line_breaks": True,      # Line structure preservation
                "enable_math_context": True,       # Mathematical context awareness
                "enable_advanced_tables": True,    # Advanced table processing
                "enable_tables_fallback": True,    # NEW: Advanced table processing with fallback
                "preserve_notation": True,         # Mathematical notation preservation
                "scientific_document_mode": True,  # Scientific document optimization
                "math_heavy_processing": True,     # Math-heavy content optimization
                "enable_multipass": True,          # Multi-pass processing for quality
                "enable_error_recovery": True,     # Enhanced error recovery
                "streaming": True,                 # Enable streaming for large documents
                "enable_progress_tracking": True,  # Better progress visibility
                "include_smiles": False,           # DISABLE: Chemistry parsing for Physics textbook
                "numbers_default_to_math": False,  # Keep numbers as text when appropriate
                "math_inline_delimiters": ["$", "$"],
                "math_display_delimiters": ["$$", "$$"]
            }

            # Add streaming support for large documents (>200 pages)
            if page_ranges:
                options["page_ranges"] = page_ranges

            # Enable streaming for large documents
            total_pages_estimate = 200  # Conservative estimate
            if page_ranges:
                # Parse page ranges to estimate size
                try:
                    ranges = page_ranges.split(',')
                    total_pages_estimate = sum(
                        int(r.split('-')[1]) - int(r.split('-')[0]) + 1 if '-' in r else 1
                        for r in ranges
                    )
                except:
                    pass

            if total_pages_estimate > 100:  # Large document threshold
                options["streaming"] = True
                options["enable_progress_tracking"] = True

            # Upload with file
            self.api_logger.log_request(
                'pdf_upload',
                {'file': str(pdf_path), 'options': options}
            )

            with open(pdf_path, 'rb') as f:
                response = requests.post(
                    self.pdf_endpoint,
                    headers=self.headers,
                    data={"options_json": json.dumps(options)},
                    files={"file": f},
                    timeout=self.settings.timeout_seconds
                )

            response.raise_for_status()
            result = response.json()

            self.api_logger.log_response('pdf_upload', result)

            # Check for Mathpix API errors
            if 'error' in result:
                error_msg = result.get('error', 'Unknown error from Mathpix API')
                self.logger.error(f"Mathpix API error: {error_msg}")
                self.logger.error(f"Full response: {result}")
                raise RuntimeError(f"Mathpix API returned error: {error_msg}")

            pdf_id = result.get('pdf_id')
            if not pdf_id:
                self.logger.error(f"No pdf_id in response: {result}")
                raise ValueError(f"No pdf_id in response: {result}")

            return pdf_id

        # Execute with circuit breaker and retry logic
        try:
            # Use circuit breaker first
            pdf_id = self.circuit_breaker.call_with_circuit(upload_function)
            self.logger.info(f"PDF uploaded successfully through circuit breaker: {pdf_id}")
            return pdf_id

        except Exception as e:
            # If circuit breaker fails, try with retry logic as fallback
            self.logger.warning(f"Circuit breaker failed, trying with retry logic: {e}")

            def retry_upload_function():
                return upload_function()

            try:
                pdf_id = self.retry_handler.execute_with_retry(
                    retry_upload_function,
                    context=f"PDF upload for {pdf_path.name}"
                )
                self.logger.info(f"PDF uploaded successfully with retry logic: {pdf_id}")
                return pdf_id
            except Exception as retry_e:
                self.logger.error(f"PDF upload failed after all reliability measures: {retry_e}")
                raise
    
    def _wait_for_processing(self, pdf_id: str, max_wait_seconds: int = 3600):
        """
        Poll for PDF processing completion (OCR phase)
        Handles 500+ page PDFs with appropriate timeouts
        """
        self.logger.info(f"Waiting for PDF processing: {pdf_id}")
        
        start_time = time.time()
        check_interval = 5  # Start with 5 seconds
        max_interval = 30  # Max 30 seconds between checks
        
        while True:
            if time.time() - start_time > max_wait_seconds:
                raise TimeoutError(f"PDF processing timeout after {max_wait_seconds}s")
            
            # Check status
            status_url = f"{self.pdf_endpoint}/{pdf_id}"
            response = requests.get(status_url, headers=self.headers)
            response.raise_for_status()
            status = response.json()
            
            current_status = status.get('status')
            percent = status.get('percent_done', 0)
            pages_done = status.get('num_pages_completed', 0)
            total_pages = status.get('num_pages', '?')
            
            self.logger.info(
                f"Processing: {current_status} - {percent:.1f}% "
                f"({pages_done}/{total_pages} pages)"
            )
            
            if current_status == 'completed':
                self.logger.info("PDF processing completed")
                return status
            elif current_status == 'error':
                error_msg = status.get('error', 'Unknown error')
                raise RuntimeError(f"PDF processing failed: {error_msg}")
            
            # Exponential backoff
            time.sleep(check_interval)
            check_interval = min(check_interval * 1.2, max_interval)
    
    def _wait_for_conversions(self, pdf_id: str, max_wait_seconds: int = 1800):
        """
        Poll for ALL format conversion completions
        """
        self.logger.info(f"Waiting for format conversions: {pdf_id}")
        
        start_time = time.time()
        check_interval = 5
        max_interval = 20
        
        while True:
            if time.time() - start_time > max_wait_seconds:
                self.logger.warning("Conversion timeout - some formats may be incomplete")
                return
            
            # Check conversion status
            status_url = f"{self.converter_endpoint}/{pdf_id}"
            response = requests.get(status_url, headers=self.headers)
            response.raise_for_status()
            status = response.json()
            
            conversion_status = status.get('conversion_status', {})
            
            # Check if all conversions are complete
            all_complete = True
            statuses = []
            
            for fmt, fmt_status in conversion_status.items():
                status_val = fmt_status.get('status', 'unknown')
                statuses.append(f"{fmt}:{status_val}")
                
                if status_val not in ['completed', 'error']:
                    all_complete = False
            
            self.logger.info(f"Conversions: {', '.join(statuses)}")
            
            if all_complete:
                self.logger.info("All conversions completed")
                return conversion_status
            
            time.sleep(check_interval)
            check_interval = min(check_interval * 1.2, max_interval)
    
    def _download_all_formats(
        self,
        pdf_id: str,
        volume_type: VolumeType
    ) -> OutputFiles:
        """
        Download ALL output formats for maximum flexibility
        """
        self.logger.info(f"Downloading all output formats for {pdf_id}")
        
        volume_num = int(volume_type.value.split('_')[1])
        output_dir = self.paths.get_volume_dir(volume_num, 'raw_ocr')
        
        output_files = OutputFiles()
        
        # Format: (extension, attribute_name, binary_mode)
        formats = [
            ('mmd', 'mmd_file', False),
            ('md', 'md_file', False),
            ('docx', 'docx_file', True),
            ('pptx', 'pptx_file', True),
            ('html', 'html_file', False),
            ('latex.pdf', 'pdf_latex_file', True),
            ('pdf', 'pdf_html_file', True),
            ('tex.zip', 'latex_zip_file', True),
            ('mmd.zip', 'mmd_zip_file', True),
            ('md.zip', 'md_zip_file', True),
            ('html.zip', 'html_zip_file', True),
            ('lines.json', 'lines_json_file', False),
        ]
        
        for ext, attr, binary in formats:
            try:
                url = f"{self.pdf_endpoint}/{pdf_id}.{ext}"
                response = requests.get(url, headers=self.headers, timeout=60)
                
                if response.status_code == 200:
                    # Sanitize extension for filename
                    safe_ext = ext.replace('.', '_')
                    filename = f"{pdf_id}.{safe_ext}"
                    if ext in ['tex.zip', 'mmd.zip', 'md.zip', 'html.zip']:
                        filename = f"{pdf_id}.{ext}"
                    
                    file_path = output_dir / filename
                    
                    mode = 'wb' if binary else 'w'
                    content = response.content if binary else response.text

                    if binary:
                        with open(file_path, mode) as f:
                            f.write(content)
                    else:
                        with open(file_path, mode, encoding='utf-8') as f:
                            f.write(content)
                    
                    setattr(output_files, attr, str(file_path))
                    self.logger.info(f"Downloaded: {ext}")
                else:
                    self.logger.warning(f"Failed to download {ext}: {response.status_code}")
            
            except Exception as e:
                self.logger.warning(f"Error downloading {ext}: {e}")
        
        return output_files
    
    def _parse_lines_json(
        self,
        pdf_id: str,
        lines_json_path: Optional[str]
    ) -> List[PdfPageData]:
        """
        Parse comprehensive line-by-line data from lines.json
        This contains ALL geometric and metadata information
        """
        if not lines_json_path or not Path(lines_json_path).exists():
            self.logger.warning("No lines.json file available")
            return []
        
        self.logger.info("Parsing comprehensive line data from lines.json")

        with open(lines_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pages_data = []
        
        for page_data in data.get('pages', []):
            # Parse page-level data
            page = PdfPageData(
                image_id=page_data.get('image_id', ''),
                page=page_data.get('page', 0),
                page_height=page_data.get('page_height'),
                page_width=page_data.get('page_width')
            )
            
            # Parse all lines with COMPLETE information
            for line_data in page_data.get('lines', []):
                # Parse bounding box
                region = None
                if 'region' in line_data:
                    r = line_data['region']
                    region = BoundingBox(
                        top_left_x=r.get('top_left_x', 0),
                        top_left_y=r.get('top_left_y', 0),
                        width=r.get('width', 0),
                        height=r.get('height', 0)
                    )
                
                # Create comprehensive line data
                line = PdfLineData(
                    id=line_data.get('id', ''),
                    parent_id=line_data.get('parent_id'),
                    children_ids=line_data.get('children_ids', []),
                    type=line_data.get('type', ''),
                    subtype=line_data.get('subtype'),
                    line=line_data.get('line', 0),
                    column=line_data.get('column'),
                    font_size=line_data.get('font_size'),
                    text=line_data.get('text', ''),
                    text_display=line_data.get('text_display', ''),
                    conversion_output=line_data.get('conversion_output', False),
                    is_printed=line_data.get('is_printed', True),
                    is_handwritten=line_data.get('is_handwritten', False),
                    region=region,
                    cnt=line_data.get('cnt', []),
                    confidence=line_data.get('confidence'),
                    confidence_rate=line_data.get('confidence_rate'),
                    metadata={k: v for k, v in line_data.items() 
                             if k not in ['id', 'parent_id', 'children_ids', 'type', 
                                         'subtype', 'line', 'column', 'font_size', 'text',
                                         'text_display', 'conversion_output', 'is_printed',
                                         'is_handwritten', 'region', 'cnt', 'confidence',
                                         'confidence_rate']}
                )
                
                page.lines.append(line)
            
            pages_data.append(page)
        
        self.logger.info(f"Parsed {len(pages_data)} pages with full line data")
        return pages_data
    
    def _build_ocr_result(
        self,
        pdf_id: str,
        mathpix_pdf_id: str,
        volume_type: VolumeType,
        pages_data: List[PdfPageData],
        output_files: OutputFiles
    ) -> PDFOCRResult:
        """
        Build comprehensive OCR result with all data
        """
        self.logger.info("Building comprehensive OCR result")
        
        # Initialize result
        result = PDFOCRResult(
            pdf_id=pdf_id,
            volume_type=volume_type,
            total_pages=len(pages_data),
            output_files=output_files,
            processing_status=ProcessingStatus(status='completed'),
            processing_started=datetime.now()
        )
        
        # Process each page
        total_equations = 0
        total_lines = 0
        confidence_scores = []
        
        for page_data in pages_data:
            # Extract equations from lines
            equations = []
            eq_count = 0
            for line in page_data.lines:
                if line.type == 'equation' or '$' in line.text_display:
                    eq = Equation(
                        equation_id=f"eq_{page_data.page}_{eq_count}",
                        latex=line.text_display,
                        location=line.region,
                        confidence=line.confidence or 1.0,
                        line_id=line.id
                    )
                    equations.append(eq)
                    eq_count += 1
            
            total_equations += len(equations)
            total_lines += len(page_data.lines)
            
            # Build page result
            page_result = PageOCRResult(
                page_number=page_data.page,
                pdf_id=mathpix_pdf_id,
                raw_text='\n'.join(l.text for l in page_data.lines),
                mathpix_markdown='\n'.join(l.text_display for l in page_data.lines if l.conversion_output),
                line_data=page_data.lines,
                equations=equations,
                page_width=page_data.page_width,
                page_height=page_data.page_height,
                processing_time_seconds=0,
                mathpix_request_id=mathpix_pdf_id
            )
            
            # Calculate page confidence
            page_confidences = [l.confidence for l in page_data.lines if l.confidence]
            if page_confidences:
                page_result.confidence_score = sum(page_confidences) / len(page_confidences)
                confidence_scores.append(page_result.confidence_score)

                # NEW: Quality control - flag low confidence pages
                if page_result.confidence_score < self.settings.confidence_threshold:
                    self.logger.warning(f"Page {page_data.page} has low confidence: {page_result.confidence_score:.2%}")
            else:
                # Default high confidence if no line-level confidence available
                page_result.confidence_score = 1.0
                confidence_scores.append(1.0)
            
            result.pages[page_data.page] = page_result
        
        # Set overall statistics
        result.total_equations = total_equations
        result.total_lines = total_lines
        result.average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 1.0
        result.pages_with_low_confidence = [
            p.page_number for p in result.pages.values()
            if p.confidence_score < self.settings.confidence_threshold
        ]

        # NEW: Quality metrics
        quality_metrics = {
            'confidence_ranges': {
                'excellent': sum(1 for c in confidence_scores if c >= 0.9),
                'good': sum(1 for c in confidence_scores if 0.8 <= c < 0.9),
                'fair': sum(1 for c in confidence_scores if 0.7 <= c < 0.8),
                'poor': sum(1 for c in confidence_scores if c < 0.7)
            },
            'quality_score': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 1.0,
            'total_low_confidence_pages': len(result.pages_with_low_confidence)
        }
        self.logger.info(f"Quality metrics: {quality_metrics}")
        
        result.processing_completed = datetime.now()
        
        return result
    
    def _generate_pdf_id(self, pdf_path: Path) -> str:
        """Generate unique ID for PDF"""
        return hashlib.md5(f"{pdf_path.name}_{pdf_path.stat().st_size}".encode()).hexdigest()[:16]
    
    def _cache_result(self, pdf_id: str, result: PDFOCRResult):
        """Cache complete result"""
        cache_file = self.paths.mathpix_cache_dir / f"{pdf_id}_complete.json"
        save_model_to_json(result, cache_file)
        self.api_logger.cache_response(f"{pdf_id}_complete", result.model_dump())
    
    def _load_cached_result(self, pdf_id: str) -> Optional[PDFOCRResult]:
        """Load cached result"""
        from src.data_models import load_model_from_json
        
        cache_file = self.paths.mathpix_cache_dir / f"{pdf_id}_complete.json"
        if not cache_file.exists():
            return None
        
        try:
            return load_model_from_json(PDFOCRResult, cache_file)
        except Exception as e:
            self.logger.warning(f"Failed to load cache: {e}")
            return None


if __name__ == '__main__':
    # Test
    processor = MathpixProcessor()
    print("Enhanced Mathpix processor initialized")
