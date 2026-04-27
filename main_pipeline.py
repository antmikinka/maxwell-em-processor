"""
Main Pipeline Orchestrator - 3-STAGE PRODUCTION SYSTEM
Comprehensive PDF processing with maximum information extraction
Stages: OCR → TOC Analysis → Organization (Code Generation removed per user request)
"""

import sys
import argparse
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

from src.mathpix_processor import MathpixProcessor
from src.toc_analyzer import TOCAnalyzer
from src.content_organizer import ContentOrganizer
from src.simple_mode_organizer import SimpleModeOrganizer, organize_simple_mode
from src.health_monitor import get_health_monitor
from src.data_models import (
    VolumeType, ProcessingStage, PipelineState, Checkpoint,
    PDFOCRResult, OrganizationResult,
    save_model_to_json, load_model_from_json
)
from src.logger_config import init_logging, get_logger, get_stats_logger
from config.config import get_settings, get_paths


class MaxwellPipeline:
    """
    3-Stage Processing Pipeline for Maxwell EM Theory Books
    Focus: Maximum information extraction for user flexibility
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.paths = get_paths()
        
        # Initialize logging
        init_logging(self.paths.logs_dir, self.settings.log_level)
        
        self.logger = get_logger('maxwell_pipeline')
        self.stats_logger = get_stats_logger()
        
        # Initialize processors (only 3 stages now)
        self.mathpix = MathpixProcessor()
        self.toc_analyzer = TOCAnalyzer()
        self.organizer = ContentOrganizer()
        self.simple_organizer = SimpleModeOrganizer()
        self.health_monitor = get_health_monitor()
        
        # Pipeline state
        self.state = None
        
        self.logger.info("Maxwell Pipeline initialized - 3-Stage System")
        self.logger.info("Stages: OCR -> TOC Analysis -> Organization")
    
    def run_full_pipeline(
        self,
        pdf_path: Path,
        volume_num: int,
        page_ranges: Optional[str] = None
    ):
        """
        Execute complete 3-stage pipeline with maximum data extraction

        Args:
            pdf_path: Path to PDF file (500+ pages supported)
            volume_num: Volume number (1 or 2)
            page_ranges: Optional page range (e.g., "1-50,100-150")
        """
        volume_type = VolumeType(f"volume_{volume_num}")

        # Check if simple mode is enabled
        if self.settings.simple_mode:
            self.logger.info("=" * 80)
            self.logger.info("SIMPLE MODE ENABLED - MATHPIX-ONLY EXTRACTION")
            self.logger.info("Skipping TOC analysis and complex organization")
            self.logger.info("=" * 80)

            return self.run_simple_mode_pipeline(pdf_path, volume_type, page_ranges)

        self.logger.info(f"=" * 80)
        self.logger.info(f"STARTING 3-STAGE PIPELINE FOR: {pdf_path}")
        self.logger.info(f"Volume: {volume_num}, Pages: {page_ranges or 'ALL'}")
        self.logger.info(f"=" * 80)
        
        self.stats_logger.log_stage_start("Full 3-Stage Pipeline")

        # Start health monitoring
        self.health_monitor.start_monitoring()
        self.logger.info("Health monitoring started")

        start_time = time.time()
        
        try:
            # Initialize state
            self.state = PipelineState(
                current_stage=ProcessingStage.OCR,
                volume_id=volume_type.value
            )
            
            # ========== STAGE 1: OCR PROCESSING ==========
            self.logger.info("\n" + "="*80)
            self.logger.info("STAGE 1: OCR PROCESSING WITH MATHPIX")
            self.logger.info("Extracting: Text, Equations, Figures, Geometry, ALL Formats")
            self.logger.info("="*80)
            
            ocr_result = self.run_ocr_stage(pdf_path, volume_type, page_ranges)
            self._save_checkpoint(ProcessingStage.OCR, {
                'ocr_complete': True,
                'total_pages': ocr_result.total_pages,
                'total_equations': ocr_result.total_equations,
                'total_lines': ocr_result.total_lines
            })
            
            # ========== STAGE 2: TOC ANALYSIS ==========
            self.logger.info("\n" + "="*80)
            self.logger.info("STAGE 2: TABLE OF CONTENTS ANALYSIS")
            self.logger.info("Building: Volume → Part → Chapter → Article structure")
            self.logger.info("="*80)
            
            toc_structure = self.run_toc_stage()
            self._save_checkpoint(ProcessingStage.TOC_ANALYSIS, {'toc_complete': True})
            
            # ========== STAGE 3: CONTENT ORGANIZATION ==========
            self.logger.info("\n" + "="*80)
            self.logger.info("STAGE 3: CONTENT ORGANIZATION (PAGE-BASED)")
            self.logger.info("Organizing: Pages into TOC structure using page numbers")
            self.logger.info("Method: Direct TOC mapping (No AI, zero cost)")
            self.logger.info("="*80)
            
            org_result = self.run_organization_stage(ocr_result)
            self._save_checkpoint(ProcessingStage.ORGANIZATION, {'org_complete': True})
            
            # ========== PIPELINE COMPLETE ==========
            self.state.completed = True
            duration = time.time() - start_time
            
            stats = {
                'total_pages': ocr_result.total_pages,
                'total_lines': ocr_result.total_lines,
                'total_equations': ocr_result.total_equations,
                'total_figures': ocr_result.total_figures,
                'organized_pages': len(org_result.organized_pages),
                'output_formats': len([f for f in vars(ocr_result.output_files).values() if f])
            }
            
            self.logger.info("\n" + "="*80)
            self.logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
            self.logger.info(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            self.logger.info(f"Pages Processed: {stats['total_pages']}")
            self.logger.info(f"Lines Extracted: {stats['total_lines']}")
            self.logger.info(f"Equations Found: {stats['total_equations']}")
            self.logger.info(f"Output Formats: {stats['output_formats']}")
            self.logger.info("="*80 + "\n")
            
            self.stats_logger.log_stage_complete("Full 3-Stage Pipeline", duration, stats)

            # Stop health monitoring
            self.health_monitor.stop_monitoring()
            self.logger.info("Health monitoring stopped")

            # Print output locations
            self._print_output_summary(ocr_result, org_result)
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}", exc_info=True)
            self.state.error_count += 1
            raise
    
    def run_ocr_stage(
        self,
        pdf_path: Path,
        volume_type: VolumeType,
        page_ranges: Optional[str] = None
    ) -> PDFOCRResult:
        """
        Execute comprehensive OCR processing stage
        Extracts ALL data and formats from Mathpix
        """
        self.stats_logger.log_stage_start("Stage 1: OCR Processing")
        
        start_time = time.time()
        
        # Process with comprehensive data extraction
        if page_ranges is None:
            # Check if we need to chunk large documents
            estimated_pages = 300  # Conservative estimate based on Maxwell volumes
            if estimated_pages > 200:
                self.logger.info(f"Large document detected ({estimated_pages} pages) - using intelligent chunking")
                result = self._process_with_chunking(pdf_path, volume_type)
            else:
                self.logger.info(f"Document has {estimated_pages} pages - processing normally")
                result = self.mathpix.process_pdf(pdf_path, volume_type, page_ranges)
        else:
            # Process specified page ranges
            result = self.mathpix.process_pdf(pdf_path, volume_type, page_ranges)
        
        duration = time.time() - start_time
        stats = {
            'total_pages': result.total_pages,
            'total_lines': result.total_lines,
            'total_equations': result.total_equations,
            'total_figures': result.total_figures,
            'average_confidence': f"{result.average_confidence:.2%}",
            'processing_time': result.total_processing_time_seconds,
            'output_formats_generated': len([f for f in vars(result.output_files).values() if f])
        }
        
        self.stats_logger.log_stage_complete("Stage 1: OCR Processing", duration, stats)
        
        # Save comprehensive result
        result_file = self.paths.database_dir / f"{volume_type.value}_ocr_result.json"
        save_model_to_json(result, result_file)
        self.logger.info(f"Saved OCR result: {result_file}")
        
        return result
    
    def run_toc_stage(self):
        """Execute TOC analysis stage with proper path resolution"""
        self.stats_logger.log_stage_start("Stage 2: TOC Analysis")
        start_time = time.time()
        
        # Use smart path resolution for TOC files
        toc_dir = self.paths.input_dir  # Look in the input directory first
        
        # Volume 1 TOC file - use the file you just provided
        vol1_toc_candidates = [
            toc_dir / "v3 - Vol 1 - README.md",  # Your uploaded file name
            toc_dir / "Vol 1 - README.md",
            toc_dir / "volume_1_toc.md",
            toc_dir / "README.md"
        ]
        
        vol1_readme = None
        for candidate in vol1_toc_candidates:
            if candidate.exists():
                vol1_readme = candidate
                self.logger.info(f"Found Volume 1 TOC file: {vol1_readme}")
                break
        
        # Volume 2 TOC file (you'll provide this next)
        vol2_toc_candidates = [
            toc_dir / "v3 - Vol 2 - README.md",  # Expected name for your next file
            toc_dir / "Vol 2 - README.md",
            toc_dir / "volume_2_toc.md",
            toc_dir / "readme.md"
        ]
        
        vol2_readme = None
        for candidate in vol2_toc_candidates:
            if candidate.exists():
                vol2_readme = candidate
                self.logger.info(f"Found Volume 2 TOC file: {vol2_readme}")
                break
        
        # Handle missing files gracefully
        if not vol1_readme:
            error_msg = "Volume 1 TOC file not found! Please place your TOC file in the input directory."
            self.logger.error(error_msg)
            self.logger.error(f"Searched for Volume 1 TOC in: {[str(c) for c in vol1_toc_candidates]}")
            raise FileNotFoundError(error_msg)
        
        if not vol2_readme:
            self.logger.warning("Volume 2 TOC file not found yet - will use placeholder structure")
            # Create a minimal placeholder for Volume 2
            vol2_readme = self._create_placeholder_toc_file(2)
        
        # Parse TOC structure
        toc_structure = self.toc_analyzer.parse_from_readme_files(
            vol1_readme,
            vol2_readme
        )
        
        duration = time.time() - start_time
        stats = {
            'volumes_parsed': len(toc_structure.volumes),
            'total_parts': sum(len(v.parts) for v in toc_structure.volumes.values()),
            'total_chapters': sum(
                len(p.chapters) 
                for v in toc_structure.volumes.values() 
                for p in v.parts.values()
            )
        }
        self.stats_logger.log_stage_complete("Stage 2: TOC Analysis", duration, stats)
        return toc_structure

    def _create_placeholder_toc_file(self, volume_num: int) -> Path:
        """Create a minimal placeholder TOC file for missing volumes"""
        placeholder_path = self.paths.input_dir / f"volume_{volume_num}_placeholder_toc.md"
        placeholder_content = f"""
    # PLACEHOLDER TOC - VOLUME {volume_num}
    ## PART I. PLACEHOLDER PART
    ### CHAPTER I. PLACEHOLDER CHAPTER
    - Article 1: Placeholder article
    - Article 2: Placeholder article

    ## PART II. PLACEHOLDER PART 2
    ### CHAPTER I. ANOTHER PLACEHOLDER CHAPTER
    - Article 1: Placeholder article
    """
        with open(placeholder_path, 'w', encoding='utf-8') as f:
            f.write(placeholder_content)
        self.logger.warning(f"Created placeholder TOC file: {placeholder_path}")
        return placeholder_path

    
    def run_organization_stage(self, ocr_result: PDFOCRResult) -> OrganizationResult:
        """Execute content organization stage"""
        self.stats_logger.log_stage_start("Stage 3: Content Organization")
        
        start_time = time.time()
        
        result = self.organizer.organize_pdf_content(ocr_result)
        
        duration = time.time() - start_time
        stats = result.statistics
        stats['duration_seconds'] = duration
        
        self.stats_logger.log_stage_complete("Stage 3: Content Organization", duration, stats)

        return result

    def run_simple_mode_pipeline(
        self,
        pdf_path: Path,
        volume_type: VolumeType,
        page_ranges: Optional[str] = None
    ):
        """
        Execute simple mode pipeline - Mathpix-only extraction and organization

        Args:
            pdf_path: Path to PDF file
            volume_type: Volume type (volume_1 or volume_2)
            page_ranges: Optional page range
        """
        self.stats_logger.log_stage_start("Simple Mode: Mathpix-Only Pipeline")

        start_time = time.time()

        try:
            # Start health monitoring
            self.health_monitor.start_monitoring()
            self.logger.info("Health monitoring started")

            # ========== SIMPLE STAGE 1: OCR PROCESSING ==========
            self.logger.info("\n" + "="*80)
            self.logger.info("SIMPLE STAGE 1: MATHPIX OCR PROCESSING")
            self.logger.info("Extracting: Text, Equations, Figures, ALL Formats")
            self.logger.info("="*80)

            ocr_result = self.run_ocr_stage(pdf_path, volume_type, page_ranges)

            # ========== SIMPLE STAGE 2: SIMPLE ORGANIZATION ==========
            self.logger.info("\n" + "="*80)
            self.logger.info("SIMPLE STAGE 2: MATHPIX-ONLY ORGANIZATION")
            self.logger.info("Organizing: Raw data, processed formats, comprehensive metadata")
            self.logger.info("="*80)

            # Use simple mode organizer instead of complex TOC-based organization
            self.logger.info("Calling simple mode organizer...")
            summary = self.simple_organizer.organize_simple_output(pdf_path, ocr_result)
            self.logger.info(f"Simple mode organizer returned: {type(summary)}, keys: {list(summary.keys()) if isinstance(summary, dict) else 'Not a dict'}")

            # ========== SIMPLE PIPELINE COMPLETE ==========
            duration = time.time() - start_time

            stats = {
                'total_pages': ocr_result.total_pages,
                'total_lines': ocr_result.total_lines,
                'total_equations': ocr_result.total_equations,
                'total_figures': ocr_result.total_figures,
                'output_formats': len([f for f in vars(ocr_result.output_files).values() if f])
            }

            self.logger.info("\n" + "="*80)
            self.logger.info("SIMPLE MODE PIPELINE COMPLETED SUCCESSFULLY!")
            self.logger.info(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            self.logger.info(f"Pages Processed: {stats['total_pages']}")
            self.logger.info(f"Lines Extracted: {stats['total_lines']}")
            self.logger.info(f"Equations Found: {stats['total_equations']}")
            self.logger.info(f"Output Formats: {stats['output_formats']}")
            self.logger.info("="*80 + "\n")

            self.stats_logger.log_stage_complete("Simple Mode Pipeline", duration, stats)

            # Stop health monitoring
            self.health_monitor.stop_monitoring()
            self.logger.info("Health monitoring stopped")

            # Print simple mode output summary
            self._print_simple_output_summary(ocr_result, summary)

        except Exception as e:
            self.logger.error(f"Simple mode pipeline failed: {e}", exc_info=True)
            raise

    def _print_simple_output_summary(self, ocr_result: PDFOCRResult, summary: dict):
        """Print simple mode output summary"""
        print("\n" + "="*80)
        print("SIMPLE MODE OUTPUT SUMMARY - MATHPIX-ONLY DATA")
        print("="*80)

        print("\n📁 RAW MATHPIX DATA (All Formats):")
        print(f"   Location: {self.simple_organizer.simple_output_dir}")
        if ocr_result.output_files.mmd_file:
            print(f"   ✓ Mathpix Markdown (.mmd)")
        if ocr_result.output_files.md_file:
            print(f"   ✓ Standard Markdown (.md)")
        if ocr_result.output_files.docx_file:
            print(f"   ✓ Microsoft Word (.docx)")
        if ocr_result.output_files.latex_zip_file:
            print(f"   ✓ LaTeX with images (.tex.zip)")
        if ocr_result.output_files.html_file:
            print(f"   ✓ HTML rendering (.html)")
        if ocr_result.output_files.pptx_file:
            print(f"   ✓ PowerPoint (.pptx)")
        if ocr_result.output_files.lines_json_file:
            print(f"   ✓ Comprehensive line data (.lines.json) ← MOST DETAILED")

        print("\n📊 COMPREHENSIVE METADATA:")
        print(f"   Location: {self.simple_organizer.simple_output_dir}")
        print(f"   ✓ Complete OCR result JSON")
        print(f"   ✓ Individual page data")
        print(f"   ✓ Confidence analysis")
        print(f"   ✓ Structure mapping")
        print(f"   ✓ Extraction summary")

        print("\n📂 ORGANIZATION STRUCTURE:")
        print(f"   Raw/ - Complete Mathpix API responses")
        print(f"   Processed/ - Ready-to-use format files")
        print(f"   Metadata/ - Comprehensive extraction metadata")

        print("\n📝 LOGS & CACHE:")
        print(f"   Logs: {self.paths.logs_dir}")
        print(f"   Cache: {self.paths.cache_dir}")

        print("\n" + "="*80)
        print("All Mathpix data extracted and organized - pure data extraction!")
        print("No complex AI processing - maximum reliability and speed!")
        print("="*80 + "\n")
    
    def resume_from_checkpoint(self, volume_num: int):
        """Resume pipeline from last checkpoint"""
        self.logger.info("Attempting to resume from checkpoint")
        
        volume_type = VolumeType(f"volume_{volume_num}")
        
        # Check which stages are complete
        checkpoints = {
            ProcessingStage.OCR: self.paths.get_checkpoint_file(f"step_{ProcessingStage.OCR.value}"),
            ProcessingStage.TOC_ANALYSIS: self.paths.get_checkpoint_file(f"step_{ProcessingStage.TOC_ANALYSIS.value}"),
            ProcessingStage.ORGANIZATION: self.paths.get_checkpoint_file(f"step_{ProcessingStage.ORGANIZATION.value}"),
        }
        
        last_completed = None
        for stage, checkpoint_file in checkpoints.items():
            if checkpoint_file.exists():
                last_completed = stage
                self.logger.info(f"Found checkpoint: {stage.value}")
        
        if not last_completed:
            self.logger.error("No checkpoints found - cannot resume")
            return
        
        self.logger.info(f"Last completed stage: {last_completed.value}")
        self.logger.info("To continue, load the OCR result and run remaining stages")
    
    def _save_checkpoint(self, stage: ProcessingStage, data: dict):
        """Save checkpoint for resume capability"""
        if not self.settings.enable_checkpoints:
            return
        
        checkpoint = Checkpoint(
            stage=stage,
            volume_id=self.state.volume_id,
            completed=True,
            timestamp=datetime.now(),
            data=data
        )
        
        checkpoint_file = self.paths.get_checkpoint_file(f"step_{stage.value}")
        save_model_to_json(checkpoint, checkpoint_file)
        
        self.logger.info(f"✓ Checkpoint saved: {stage.value}")
    
    def _print_output_summary(self, ocr_result: PDFOCRResult, org_result: OrganizationResult):
        """Print comprehensive output summary"""
        print("\n" + "="*80)
        print("OUTPUT SUMMARY - ALL FILES SAVED")
        print("="*80)
        
        print("\n📁 RAW OCR DATA (All Formats):")
        print(f"   Location: {self.paths.raw_ocr_dir}")
        if ocr_result.output_files.mmd_file:
            print(f"   ✓ Mathpix Markdown (.mmd)")
        if ocr_result.output_files.md_file:
            print(f"   ✓ Standard Markdown (.md)")
        if ocr_result.output_files.docx_file:
            print(f"   ✓ Microsoft Word (.docx)")
        if ocr_result.output_files.latex_zip_file:
            print(f"   ✓ LaTeX with images (.tex.zip)")
        if ocr_result.output_files.html_file:
            print(f"   ✓ HTML rendering (.html)")
        if ocr_result.output_files.pptx_file:
            print(f"   ✓ PowerPoint (.pptx)")
        if ocr_result.output_files.lines_json_file:
            print(f"   ✓ Comprehensive line data (.lines.json) ← MOST DETAILED")
        
        print("\n📊 STRUCTURED DATA:")
        print(f"   Location: {self.paths.database_dir}")
        print(f"   ✓ Complete OCR result JSON")
        print(f"   ✓ TOC structure JSON")
        print(f"   ✓ Organization metadata JSON")
        
        print("\n📂 ORGANIZED CONTENT:")
        print(f"   Location: {self.paths.organized_dir}")
        print(f"   ✓ Pages organized by TOC hierarchy")
        print(f"   ✓ {len(org_result.organized_pages)} pages categorized")
        
        print("\n📝 LOGS & CACHE:")
        print(f"   Logs: {self.paths.logs_dir}")
        print(f"   Cache: {self.paths.cache_dir}")
        print(f"   Checkpoints: {self.paths.checkpoints_dir}")
        
        print("\n" + "="*80)
        print("All data extracted and saved - maximum flexibility for next steps!")
        print("="*80 + "\n")


def resolve_pdf_path(pdf_input: Path, project_root: Path) -> Path:
    """
    Smart PDF path resolution that checks multiple common locations

    Args:
        pdf_input: The path provided by the user
        project_root: The root directory of the project

    Returns:
        Resolved Path to the PDF file, or raises FileNotFoundError

    Strategy:
        1. Check if the provided path exists as-is (absolute or relative)
        2. Check in the input/ directory
        3. Check in the current working directory
        4. Check for common variations (with/without directory prefixes)
    """
    # List of directories to check, in order of preference
    search_directories = [
        project_root,           # Current directory (as-is)
        project_root / "input", # Standard input directory
        Path.cwd(),            # Current working directory
    ]

    # If the input path already exists, return it
    if pdf_input.exists():
        return pdf_input

    # Try to find the PDF in common locations
    pdf_filename = pdf_input.name  # Extract just the filename
    tried_paths = []

    for search_dir in search_directories:
        candidate_path = search_dir / pdf_filename
        tried_paths.append(candidate_path)

        if candidate_path.exists():
            print(f"Found PDF at: {candidate_path}")
            return candidate_path

    # If not found, provide helpful error message
    error_msg = f"PDF file not found: {pdf_input}\n"
    error_msg += f"Looked in the following locations:\n"
    for path in tried_paths:
        status = "✓ EXISTS" if path.exists() else "✗ not found"
        error_msg += f"  - {path} {status}\n"

    error_msg += f"\nPlease ensure the PDF file exists in one of these locations."
    error_msg += f"\nExample commands:\n"
    error_msg += f"  python main_pipeline.py --pdf input/{pdf_filename} --volume 1\n"
    error_msg += f"  python main_pipeline.py --pdf {pdf_filename} --volume 1\n"

    raise FileNotFoundError(error_msg)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Maxwell EM Theory - 3-Stage PDF Processing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process full PDF
  python main_pipeline.py --pdf input/maxwell_vol1.pdf --volume 1

  # Process specific pages
  python main_pipeline.py --pdf input/maxwell_vol1.pdf --volume 1 --page-ranges "1-50"

  # Process multiple ranges
  python main_pipeline.py --pdf input/maxwell_vol1.pdf --volume 1 --page-ranges "1-50,100-150,200-250"

Stages:
  Stage 1: OCR Processing (Mathpix - ALL formats)
  Stage 2: TOC Analysis (Structure extraction)
  Stage 3: Content Organization (Folder hierarchy)
"""
    )
    
    parser.add_argument(
        '--pdf',
        type=Path,
        required=True,
        help="Path to PDF file (500+ pages supported)"
    )
    
    parser.add_argument(
        '--volume',
        type=int,
        choices=[1, 2],
        required=True,
        help="Volume number (1=Electrostatics/Electrokinematics, 2=Magnetism/Electromagnetism)"
    )
    
    parser.add_argument(
        '--stage',
        choices=['ocr', 'toc', 'organize', 'full'],
        default='full',
        help="Pipeline stage to run (default: full)"
    )
    
    parser.add_argument(
        '--simple-mode',
        action='store_true',
        help="Enable simple mode - Mathpix-only extraction without complex AI processing"
    )
    
    parser.add_argument(
        '--page-ranges',
        type=str,
        help="Page ranges to process (e.g., '1-10,15,20-25')"
    )
    
    args = parser.parse_args()
    
    # Resolve PDF path with smart path resolution
    project_root = Path(__file__).parent
    try:
        resolved_pdf_path = resolve_pdf_path(args.pdf, project_root)
        print(f"Processing PDF: {resolved_pdf_path}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    pipeline = MaxwellPipeline()
    
    try:
        if hasattr(args, 'resume') and args.resume:
            pipeline.resume_from_checkpoint(args.volume)
        elif args.simple_mode:
            # Override configuration for simple mode
            pipeline.settings.simple_mode = True
            pipeline.run_full_pipeline(resolved_pdf_path, args.volume, args.page_ranges)
        elif args.stage == 'full':
            pipeline.run_full_pipeline(resolved_pdf_path, args.volume, args.page_ranges)
        else:
            print(f"Running individual stage: {args.stage}")
            # Individual stages can be implemented if needed
    
    except KeyboardInterrupt:
        pipeline.logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        pipeline.logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()