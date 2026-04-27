#!/usr/bin/env python3
"""
Mathpix API Caller - Direct PDF Processing
Pure Mathpix API functionality without pipeline complexity
"""

import sys
import time
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

from src.mathpix_processor import MathpixProcessor
from src.data_models import VolumeType, save_model_to_json
from src.logger_config import init_logging, get_logger
from config.config import get_settings, get_paths


def main():
    """Direct Mathpix API caller - no pipeline complexity"""
    parser = argparse.ArgumentParser(
        description="Direct Mathpix API caller - extract data without pipeline overhead",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mathpix_api_caller.py --pdf input/vol2.pdf --volume 2
  python mathpix_api_caller.py --pdf vol1.pdf --volume 1 --page-ranges "1-50,100-150"
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
        '--page-ranges',
        type=str,
        help="Page ranges to process (e.g., '1-50,100-150')"
    )

    args = parser.parse_args()

    # Initialize logging and paths
    settings = get_settings()
    paths = get_paths()
    init_logging(paths.logs_dir, settings.log_level)
    logger = get_logger('mathpix_api_caller')

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

    print(f"\n🚀 DIRECT MATHPIX API CALLER")
    print(f"📄 Processing: {pdf_path}")
    print(f"📦 Volume: {args.volume}")
    print(f"📏 Pages: {args.page_ranges or 'ALL'}")
    print(f"⚡ No pipeline - direct Mathpix processing\n")

    # Initialize Mathpix processor directly
    logger.info("Initializing Mathpix processor directly")
    processor = MathpixProcessor()

    # Process PDF directly - no pipeline overhead
    volume_type = VolumeType(f"volume_{args.volume}")
    start_time = time.time()

    try:
        print("🔄 Starting Mathpix API processing...")
        result = processor.process_pdf(pdf_path, volume_type, args.page_ranges)
        duration = time.time() - start_time

        # Save result directly
        output_dir = paths.get_volume_dir(args.volume, 'raw_ocr')
        result_file = output_dir / f"volume_{args.volume}_direct_result.json"
        save_model_to_json(result, result_file)

        # Display results
        print(f"\n✅ MATHPIX PROCESSING COMPLETE!")
        print(f"⏱️  Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        print(f"📄 Pages Processed: {result.total_pages}")
        print(f"📝 Lines Extracted: {result.total_lines}")
        print(f"🧮 Equations Found: {result.total_equations}")
        print(f"📊 Figures Found: {result.total_figures}")
        print(f"🎯 Average Confidence: {result.average_confidence:.2%}")
        print(f"💾 Result Saved: {result_file}")

        if result.pages_with_low_confidence:
            print(f"⚠️  Low Confidence Pages: {len(result.pages_with_low_confidence)}")
            print(f"   Pages: {result.pages_with_low_confidence}")

        # Show available output formats
        output_formats = [f for f in vars(result.output_files).values() if f]
        if output_formats:
            print(f"📁 Output Formats: {len(output_formats)}")
            for attr_name, file_path in vars(result.output_files).items():
                if file_path:
                    format_name = attr_name.replace('_file', '').replace('_', ' ').title()
                    print(f"   ✓ {format_name}")

        print(f"\n🎯 All data extracted directly from Mathpix API - no pipeline overhead!")

    except Exception as e:
        print(f"\n❌ Mathpix processing failed: {e}")
        logger.error(f"Mathpix API call failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()