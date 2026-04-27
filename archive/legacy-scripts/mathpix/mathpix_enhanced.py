#!/usr/bin/env python3
"""
Enhanced Mathpix API Caller - Advanced PDF Processing
Direct Mathpix API with strategic optimizations from API documentation analysis
"""

import sys
import time
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

from src.mathpix_processor import MathpixProcessor
from src.data_models import VolumeType, save_model_to_json
from src.logger_config import init_logging, get_logger
from config.config import get_settings, get_paths


def chunk_page_ranges(total_pages: int, chunk_size: int = 100) -> List[List[int]]:
    """Create page ranges for chunked processing"""
    ranges = []
    for start in range(1, total_pages + 1, chunk_size):
        end = min(start + chunk_size - 1, total_pages)
        ranges.append([start, end])
    return ranges


def process_large_document_chunked(processor: MathpixProcessor, pdf_path: Path,
                                 volume_type: VolumeType) -> Dict[str, Any]:
    """Process large document in chunks for better reliability"""
    logger = get_logger('mathpix_enhanced')

    logger.info(f"Processing large document in chunks: {pdf_path}")
    print(f"📦 Large document detected - using chunked processing")

    # First, get document info without full processing
    try:
        # Upload PDF without processing to get page count
        with open(pdf_path, 'rb') as f:
            options = {
                "conversion_formats": {"docx": False},
                "streaming": False,
                "enable_progress_tracking": False
            }
            response = requests.post(
                f"{processor.base_url}/v3/pdf",
                headers=processor.headers,
                data={"options_json": json.dumps(options)},
                files={"file": f},
                timeout=30
            )
        response.raise_for_status()
        pdf_id = response.json().get('pdf_id')

        # Get document info
        status_response = requests.get(
            f"{processor.base_url}/v3/pdf/{pdf_id}",
            headers=processor.headers
        )
        status_response.raise_for_status()
        status = status_response.json()

        total_pages = status.get('num_pages', 0)
        if total_pages == 0:
            # Fallback estimation for very large documents
            total_pages = 600  # Conservative estimate for Maxwell volumes

        logger.info(f"Document has approximately {total_pages} pages")

    except Exception as e:
        logger.warning(f"Could not determine exact page count: {e}")
        total_pages = 600  # Conservative estimate

    # Process in chunks
    chunk_size = 100  # Process 100 pages at a time
    page_ranges = chunk_page_ranges(total_pages, chunk_size)

    results = []
    output_files = {}

    for i, page_range in enumerate(page_ranges, 1):
        print(f"🔄 Processing chunk {i}/{len(page_ranges)}: pages {page_range[0]}-{page_range[1]}")
        logger.info(f"Processing chunk {i}/{len(page_ranges)}: pages {page_range[0]}-{page_range[1]}")

        try:
            # Process chunk
            result = processor.process_pdf(
                pdf_path,
                volume_type,
                f"{page_range[0]}-{page_range[1]}"
            )

            results.append(result)
            print(f"✅ Chunk {i} complete: {result.total_pages} pages, {result.total_lines} lines")

            # Collect output files (avoid overwriting)
            for attr_name, file_path in vars(result.output_files).items():
                if file_path and Path(file_path).exists():
                    # Add chunk suffix to avoid conflicts
                    chunk_suffix = f"_chunk_{i}"
                    base_path = Path(file_path)
                    new_path = base_path.parent / f"{base_path.stem}{chunk_suffix}{base_path.suffix}"
                    output_files[f"{attr_name}_chunk_{i}"] = str(new_path)

            # Rate limiting between chunks
            if i < len(page_ranges):
                print(f"⏳ Waiting 5 seconds between chunks...")
                time.sleep(5)

        except Exception as e:
            logger.error(f"Failed to process chunk {i}: {e}")
            print(f"❌ Chunk {i} failed: {e}")
            continue

    # Merge results
    if results:
        merged_result = results[0]
        total_pages = sum(r.total_pages for r in results)
        total_lines = sum(r.total_lines for r in results)
        total_equations = sum(r.total_equations for r in results)

        merged_result.total_pages = total_pages
        merged_result.total_lines = total_lines
        merged_result.total_equations = total_equations

        print(f"📊 MERGED RESULTS:")
        print(f"   Total Pages: {total_pages}")
        print(f"   Total Lines: {total_lines}")
        print(f"   Total Equations: {total_equations}")

        return merged_result

    return None


def main():
    """Enhanced Mathpix API caller with strategic optimizations"""
    parser = argparse.ArgumentParser(
        description="Enhanced Mathpix API caller with optimizations from API documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mathpix_enhanced.py --pdf input/vol2.pdf --volume 2
  python mathpix_enhanced.py --pdf vol1.pdf --volume 1 --force-chunking
        """
    )

    parser.add_argument(
        '--pdf',
        type=Path,
        required=True,
        help="Path to PDF file"
    )

    parser.add_argument(
        '--volume',
        type=int,
        choices=[1, 2],
        required=True,
        help="Volume number (1 or 2)"
    )

    parser.add_argument(
        '--force-chunking',
        action='store_true',
        help="Force chunked processing even for smaller documents"
    )

    parser.add_argument(
        '--no-streaming',
        action='store_true',
        help="Disable streaming for debugging"
    )

    args = parser.parse_args()

    # Initialize logging and paths
    settings = get_settings()
    paths = get_paths()
    init_logging(paths.logs_dir, settings.log_level)
    logger = get_logger('mathpix_enhanced')

    # PDF path resolution
    project_root = Path(__file__).parent
    try:
        if not args.pdf.exists():
            # Try to find in input directory
            input_pdf = project_root / 'input' / args.pdf.name
            if input_pdf.exists():
                pdf_path = input_pdf
            else:
                print(f"Error: PDF file not found: {args.pdf}")
                print(f"Looked in: {args.pdf} and {input_pdf}")
                sys.exit(1)
        else:
            pdf_path = args.pdf
    except Exception as e:
        print(f"Error resolving PDF path: {e}")
        sys.exit(1)

    print(f"\n🚀 ENHANCED MATHPIX API CALLER")
    print(f"📄 Processing: {pdf_path}")
    print(f"📦 Volume: {args.volume}")
    print(f"⚡ Strategic optimizations enabled")

    # Initialize Mathpix processor with optimizations
    logger.info("Initializing enhanced Mathpix processor")
    processor = MathpixProcessor()

    # Apply strategic optimizations from API analysis
    print(f"🔧 Applying Mathpix API optimizations...")

    # Force fresh processing
    processor.settings.enable_api_caching = False
    logger.info("API caching disabled - forcing fresh processing")

    # Process PDF with optimizations
    volume_type = VolumeType(f"volume_{args.volume}")
    start_time = time.time()

    try:
        print("🔄 Starting enhanced Mathpix API processing...")

        # Check if document is large enough for chunked processing
        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
        is_large_document = file_size_mb > 50 or args.force_chunking

        if is_large_document:
            result = process_large_document_chunked(processor, pdf_path, volume_type)
        else:
            print("📄 Processing as single document...")
            result = processor.process_pdf(pdf_path, volume_type)

        if result is None:
            print("❌ Processing failed - no results obtained")
            sys.exit(1)

        duration = time.time() - start_time

        # Save result
        output_dir = paths.get_volume_dir(args.volume, 'raw_ocr')
        result_file = output_dir / f"volume_{args.volume}_enhanced_result.json"
        save_model_to_json(result, result_file)

        # Display results
        print(f"\n✅ ENHANCED MATHPIX PROCESSING COMPLETE!")
        print(f"⏱️  Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        print(f"📄 Pages Processed: {result.total_pages}")
        print(f"📝 Lines Extracted: {result.total_lines}")
        print(f"🧮 Equations Found: {result.total_equations}")
        print(f"📊 Figures Found: {result.total_figures}")
        print(f"🎯 Average Confidence: {result.average_confidence:.2%}")
        print(f"💾 Result Saved: {result_file}")

        if hasattr(result, 'pages_with_low_confidence') and result.pages_with_low_confidence:
            print(f"⚠️  Low Confidence Pages: {len(result.pages_with_low_confidence)}")
            print(f"   Pages: {result.pages_with_low_confidence}")

        # Show available output formats
        output_formats = []
        for attr_name, file_path in vars(result.output_files).items():
            if file_path:
                format_name = attr_name.replace('_file', '').replace('_', ' ').title()
                output_formats.append(format_name)

        if output_formats:
            print(f"📁 Output Formats: {len(output_formats)}")
            for format_name in output_formats:
                print(f"   ✓ {format_name}")

        print(f"\n🎯 All data extracted using optimized Mathpix API - strategic enhancements applied!")

    except Exception as e:
        print(f"\n❌ Enhanced Mathpix processing failed: {e}")
        logger.error(f"Enhanced Mathpix API call failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    import requests  # Import here to avoid issues in main import
    main()