"""
Simple Mode Output Organizer - MATHPIX-ONLY
Focuses purely on comprehensive Mathpix data extraction and simple organization
No complex AI features - just extract and organize all available data
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from src.logger_config import get_logger
from src.data_models import PDFOCRResult, save_model_to_json
from config.config import get_settings

class SimpleModeOrganizer:
    """
    Simple Mode Organizer - extracts and organizes ALL Mathpix data
    No AI processing, no code generation - just comprehensive data capture
    """

    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger('simple_mode_organizer')
        self.simple_output_dir = Path(self.settings.output_dir) / 'simple-mode'
        self.simple_output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info("Simple Mode Organizer initialized - Mathpix-only data extraction")

    def organize_simple_output(
        self,
        pdf_path: Path,
        ocr_result: PDFOCRResult
    ) -> Dict[str, Any]:
        """
        Organize comprehensive Mathpix data in simple structure
        Args:
            pdf_path: Original PDF file path
            ocr_result: Complete OCR result from Mathpix
        Returns:
            Summary of organized data
        """
        self.logger.info(f"Starting simple mode organization for {type(pdf_path)}: {pdf_path}")

        # Ensure pdf_path is a Path object
        if not isinstance(pdf_path, Path):
            pdf_path = Path(str(pdf_path))
            self.logger.info(f"Converted pdf_path to Path object: {pdf_path}")

        self.logger.info(f"Starting simple mode organization for {pdf_path.name}")

        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_name = pdf_path.stem
        doc_output_dir = self.simple_output_dir / f"{timestamp}_{doc_name}"
        doc_output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        raw_dir = doc_output_dir / "raw"
        processed_dir = doc_output_dir / "processed"
        metadata_dir = doc_output_dir / "metadata"

        raw_dir.mkdir(exist_ok=True)
        processed_dir.mkdir(exist_ok=True)
        metadata_dir.mkdir(exist_ok=True)

        # 1. Save raw Mathpix response data
        self._save_raw_mathpix_data(ocr_result, raw_dir)

        # 2. Save processed output files
        self._save_processed_outputs(ocr_result, processed_dir)

        # 3. Save comprehensive metadata
        summary = self._save_metadata(ocr_result, metadata_dir, pdf_path, doc_name)

        # 4. Create simple organization summary
        self._create_organization_summary(summary, doc_output_dir)

        self.logger.info(f"Simple mode organization complete: {doc_output_dir}")
        self.logger.info(f"Extracted {summary['total_pages']} pages, {summary['total_lines']} lines, {summary['total_equations']} equations")

        return summary

    def _save_raw_mathpix_data(self, ocr_result: PDFOCRResult, raw_dir: Path):
        """Save all raw Mathpix API response data"""
        self.logger.info("Saving raw Mathpix data")

        # Save complete OCR result
        ocr_file = raw_dir / "complete_ocr_result.json"
        save_model_to_json(ocr_result, ocr_file)
        self.logger.info(f"Saved complete OCR result: {ocr_file}")

        # Save lines.json data if available
        if ocr_result.output_files.lines_json_file:
            lines_source = Path(ocr_result.output_files.lines_json_file)
            if lines_source.exists():
                lines_dest = raw_dir / "lines_data.json"
                shutil.copy2(lines_source, lines_dest)
                self.logger.info(f"Saved lines data: {lines_dest}")

        # Extract and save individual page data
        pages_dir = raw_dir / "pages"
        pages_dir.mkdir(exist_ok=True)

        for page_num, page_result in ocr_result.pages.items():
            page_file = pages_dir / f"page_{page_num:03d}.json"
            page_data = {
                "page_number": page_num,
                "pdf_id": page_result.pdf_id,
                "raw_text": page_result.raw_text,
                "mathpix_markdown": page_result.mathpix_markdown,
                "confidence_score": page_result.confidence_score,
                "processing_time_seconds": page_result.processing_time_seconds,
                "mathpix_request_id": page_result.mathpix_request_id,
                "ocr_timestamp": page_result.ocr_timestamp.isoformat() if page_result.ocr_timestamp else None,
                "line_data": [line.model_dump() for line in page_result.line_data],
                "equations": [eq.model_dump() for eq in page_result.equations],
                "page_width": page_result.page_width,
                "page_height": page_result.page_height
            }
            with open(page_file, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, indent=2, ensure_ascii=False, default=str)

        self.logger.info(f"Saved individual page data for {len(ocr_result.pages)} pages")

    def _save_processed_outputs(self, ocr_result: PDFOCRResult, processed_dir: Path):
        """Save all processed output formats"""
        self.logger.info("Saving processed output formats")

        # Copy all available output files
        output_files = [
            ("mmd_file", "Mathpix Markdown"),
            ("md_file", "Standard Markdown"),
            ("docx_file", "Microsoft Word"),
            ("html_file", "HTML"),
            ("latex_zip_file", "LaTeX with images"),
            ("tex_zip_file", "LaTeX source"),
            ("mmd_zip_file", "MMD with images"),
            ("md_zip_file", "MD with images"),
            ("html_zip_file", "HTML with images"),
            ("pdf_latex_file", "LaTeX PDF"),
            ("pdf_html_file", "HTML PDF"),
            ("pptx_file", "PowerPoint")
        ]

        for attr_name, description in output_files:
            file_path = getattr(ocr_result.output_files, attr_name, None)
            if file_path and Path(file_path).exists():
                source = Path(file_path)
                # Create appropriate extension
                if attr_name.endswith('_zip_file'):
                    ext = ".zip"
                elif attr_name == "docx_file":
                    ext = ".docx"
                elif attr_name == "pptx_file":
                    ext = ".pptx"
                elif attr_name == "html_file":
                    ext = ".html"
                elif attr_name == "md_file":
                    ext = ".md"
                elif attr_name == "mmd_file":
                    ext = ".mmd"
                elif attr_name in ["pdf_latex_file", "pdf_html_file"]:
                    ext = ".pdf"
                else:
                    ext = source.suffix

                dest = processed_dir / f"document{ext}"
                shutil.copy2(source, dest)
                self.logger.info(f"Saved {description}: {dest}")

    def _save_metadata(self, ocr_result: PDFOCRResult, metadata_dir: Path, pdf_path: Path, doc_name: str) -> Dict[str, Any]:
        """Save comprehensive metadata and extraction summary"""
        self.logger.info(f"Saving metadata for pdf_path type: {type(pdf_path)}, value: {pdf_path}")

        # Ensure pdf_path is a Path object
        if not isinstance(pdf_path, Path):
            pdf_path = Path(str(pdf_path))
            self.logger.info(f"Converted pdf_path to Path: {pdf_path}")

        self.logger.info("Saving comprehensive metadata")

        # Create extraction summary
        summary = {
            "document_info": {
                "original_file": str(pdf_path),
                "document_name": doc_name,
                "pdf_id": ocr_result.pdf_id,
                "volume_type": ocr_result.volume_type.value,
                "extraction_date": datetime.now().isoformat(),
                "processing_method": "Mathpix API - Simple Mode"
            },
            "extraction_metrics": {
                "total_pages": ocr_result.total_pages,
                "total_lines": ocr_result.total_lines,
                "total_equations": ocr_result.total_equations,
                "total_figures": ocr_result.total_figures,
                "average_confidence": ocr_result.average_confidence,
                "pages_with_low_confidence": ocr_result.pages_with_low_confidence
            },
            "output_formats": {
                "generated": [],
                "available": []
            },
            "quality_metrics": {
                "confidence_ranges": self._calculate_confidence_ranges(ocr_result),
                "page_quality_breakdown": self._calculate_page_quality(ocr_result),
                "equation_extraction_success": len([eq for page in ocr_result.pages.values() for eq in page.equations])
            }
        }
        self.logger.info("Created extraction summary")

        # Check available output formats
        self.logger.info("Checking available output formats")
        for attr_name in dir(ocr_result.output_files):
            self.logger.info(f"Checking attribute: {attr_name}")
            if attr_name.endswith('_file'):
                try:
                    file_path = getattr(ocr_result.output_files, attr_name)
                    self.logger.info(f"Got file_path type: {type(file_path)}, value: {file_path}")

                    # Only process if it's a valid path (not a method)
                    if file_path and isinstance(file_path, (str, Path)):
                        if Path(file_path).exists():
                            format_name = attr_name.replace('_file', '').replace('_', ' ').title()
                            summary["output_formats"]["available"].append(format_name)
                            self.logger.info(f"Added format: {format_name}")
                    else:
                        self.logger.info(f"Skipping {attr_name} - not a valid path type")
                except Exception as e:
                    self.logger.error(f"Error checking attribute {attr_name}: {e}")

        # Save extraction summary
        summary_file = metadata_dir / "extraction_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

        # Save confidence analysis
        confidence_analysis = {
            "page_confidence_scores": {
                str(page_num): page_result.confidence_score
                for page_num, page_result in ocr_result.pages.items()
            },
            "overall_statistics": {
                "mean_confidence": sum(p.confidence_score for p in ocr_result.pages.values()) / len(ocr_result.pages),
                "min_confidence": min(p.confidence_score for p in ocr_result.pages.values()),
                "max_confidence": max(p.confidence_score for p in ocr_result.pages.values()),
                "low_confidence_pages": ocr_result.pages_with_low_confidence
            }
        }

        confidence_file = metadata_dir / "confidence_analysis.json"
        with open(confidence_file, 'w', encoding='utf-8') as f:
            json.dump(confidence_analysis, f, indent=2, ensure_ascii=False, default=str)

        # Save structure map
        structure_map = {
            "document_structure": {
                "total_pages": ocr_result.total_pages,
                "page_numbers": sorted(ocr_result.pages.keys()),
                "content_types": {
                    "pages_with_equations": [page_num for page_num, page_result in ocr_result.pages.items() if page_result.equations],
                    "pages_with_text": [page_num for page_num, page_result in ocr_result.pages.items() if page_result.raw_text.strip()],
                    "pages_with_figures": []  # Could be enhanced if figure data is available
                }
            },
            "equation_breakdown": {
                "total_equations": ocr_result.total_equations,
                "equations_per_page": {
                    str(page_num): len(page_result.equations)
                    for page_num, page_result in ocr_result.pages.items()
                }
            }
        }

        structure_file = metadata_dir / "structure_map.json"
        with open(structure_file, 'w', encoding='utf-8') as f:
            json.dump(structure_map, f, indent=2, ensure_ascii=False, default=str)

        self.logger.info("Saved comprehensive metadata")
        return summary

    def _calculate_confidence_ranges(self, ocr_result: PDFOCRResult) -> Dict[str, int]:
        """Calculate confidence score ranges"""
        confidences = [page.confidence_score for page in ocr_result.pages.values()]
        ranges = {
            "excellent": sum(1 for c in confidences if c >= 0.9),
            "good": sum(1 for c in confidences if 0.8 <= c < 0.9),
            "fair": sum(1 for c in confidences if 0.7 <= c < 0.8),
            "poor": sum(1 for c in confidences if c < 0.7)
        }
        return ranges

    def _calculate_page_quality(self, ocr_result: PDFOCRResult) -> Dict[str, Any]:
        """Calculate page quality metrics"""
        quality_breakdown = {}
        for page_num, page_result in ocr_result.pages.items():
            quality_breakdown[str(page_num)] = {
                "confidence_score": page_result.confidence_score,
                "line_count": len(page_result.line_data),
                "equation_count": len(page_result.equations),
                "text_length": len(page_result.raw_text),
                "has_equations": len(page_result.equations) > 0,
                "has_substantial_text": len(page_result.raw_text.strip()) > 100
            }
        return quality_breakdown

    def _create_organization_summary(self, summary: Dict[str, Any], doc_output_dir: Path):
        """Create a human-readable organization summary"""
        summary_text = f"""
MATHPIX-ONLY MODE - EXTRACTION SUMMARY
=====================================

Document: {summary['document_info']['document_name']}
Original File: {summary['document_info']['original_file']}
Extraction Date: {summary['document_info']['extraction_date']}

EXTRACTION METRICS:
- Total Pages: {summary['extraction_metrics']['total_pages']}
- Total Lines: {summary['extraction_metrics']['total_lines']}
- Total Equations: {summary['extraction_metrics']['total_equations']}
- Total Figures: {summary['extraction_metrics']['total_figures']}
- Average Confidence: {summary['extraction_metrics']['average_confidence']:.2%}
- Low Confidence Pages: {len(summary['extraction_metrics']['pages_with_low_confidence'])}

OUTPUT FORMATS AVAILABLE:
{chr(10).join(f"- {fmt}" for fmt in summary['output_formats']['available'])}

FILE STRUCTURE:
{doc_output_dir}/
├── raw/
│   ├── complete_ocr_result.json     # Complete Mathpix OCR data
│   ├── lines_data.json              # Line-by-line extraction data
│   └── pages/                       # Individual page data
│       ├── page_001.json
│       ├── page_002.json
│       └── ...
├── processed/                       # Ready-to-use formats
│   ├── document.mmd                 # Mathpix Markdown
│   ├── document.docx                # Microsoft Word
│   ├── document.html                # HTML format
│   └── ...
└── metadata/                        # Extraction metadata
    ├── extraction_summary.json      # Overall extraction summary
    ├── confidence_analysis.json     # Confidence score analysis
    └── structure_map.json           # Document structure mapping

All data extracted using Mathpix API with comprehensive metadata preservation.
No AI processing or code generation - pure data extraction and organization.
"""

        summary_file = doc_output_dir / "README_EXTRACTION_SUMMARY.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_text.strip())

        self.logger.info(f"Created organization summary: {summary_file}")

def organize_simple_mode(pdf_path: Path, ocr_result: PDFOCRResult) -> Dict[str, Any]:
    """Convenience function to organize simple mode output"""
    organizer = SimpleModeOrganizer()
    return organizer.organize_simple_output(pdf_path, ocr_result)