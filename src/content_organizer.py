"""
Content Organizer Module - PAGE-BASED (No AI)
Organizes pages using TOC page numbers - simple, fast, accurate, zero cost
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
# Use local slugify function instead of external import to avoid unicode issues
from src.toc_analyzer import slugify
from src.data_models import (
    PDFOCRResult, PageOCRResult, OrganizedPage, OrganizationResult,
    ContentClassification, TOCStructure, save_model_to_json
)
from src.logger_config import get_logger
from src.toc_analyzer import TOCAnalyzer
from config.config import get_settings, get_paths

class ContentOrganizer:
    """
    Page-based content organization using TOC structure
    NO AI - uses page numbers from TOC for direct mapping
    Zero cost, instant results, 100% accurate
    """
    def __init__(self):
        self.settings = get_settings()
        self.paths = get_paths()
        self.logger = get_logger('content_organizer')
        self.toc_analyzer = TOCAnalyzer()
        self.toc_structure = self.toc_analyzer.load_toc_structure()
        if not self.toc_structure:
            self.logger.warning("No TOC structure found - will need to analyze first")
        self.logger.info("Content Organizer initialized (page-based, no AI)")

    def organize_pdf_content(
        self,
        ocr_result: PDFOCRResult
    ) -> OrganizationResult:
        """
        Organize pages using TOC page numbers
        Args:
            ocr_result: Complete OCR result for PDF
        Returns:
            Organization result with pages mapped to TOC structure
        """
        self.logger.info(f"Organizing content for {ocr_result.pdf_id}")
        self.logger.info("Using page-based mapping from TOC (no AI)")
        result = OrganizationResult(
            volume_id=ocr_result.volume_type.value
        )
        
        # Get volume number
        volume_num = int(ocr_result.volume_type.value.split('_')[1])
        
        # Ensure TOC structure is loaded before proceeding
        if not self.toc_structure:
            self.logger.error("Cannot organize content: TOC structure is not loaded.")
            # Attempt to reload or handle error appropriately
            # For now, raise an error to stop the pipeline
            raise ValueError("TOC structure is required for organization. Please ensure TOC analysis stage completed successfully.")
        
        # Build page -> article mapping from TOC
        page_mapping = self._build_page_mapping(ocr_result.volume_type.value)
        self.logger.info(f"Built page mapping: {len(page_mapping)} pages mapped")
        
        # Process each page
        pages_organized = 0
        pages_unmapped = 0
        unmapped_pages_list = []  # Track unmapped pages
        
        for page_num, page_ocr in ocr_result.pages.items():
            location = page_mapping.get(page_num)
            if location:
                # Page is in TOC - organize it
                organized_page = self._organize_page(
                    page_ocr,
                    location,
                    ocr_result.volume_type.value,
                    volume_num
                )
                result.organized_pages.append(organized_page)
                pages_organized += 1
            else:
                # Page not in TOC (maybe front matter, index, etc.)
                self.logger.debug(f"Page {page_num} not in TOC - skipping organization")
                pages_unmapped += 1
                unmapped_pages_list.append(page_num)

        # Generate statistics
        result.statistics = {
            'total_pages': len(ocr_result.pages),
            'pages_organized': pages_organized,
            'pages_unmapped': pages_unmapped,
            'unmapped_pages_list': sorted(unmapped_pages_list),
            'organization_method': 'page_based_toc',
            'ai_used': False,
            'cost': 0.0
        }
        result.organization_timestamp = datetime.now()
        
        # Save result
        self._save_organization_result(result)
        self.logger.info(
            f"Organization complete: {pages_organized} pages organized, "
            f"{pages_unmapped} pages unmapped"
        )
        
        if pages_unmapped > 0:
            self.logger.info(f"Unmapped pages: {sorted(unmapped_pages_list)}")
        
        return result

    def _build_page_mapping(self, volume_id: str) -> Dict[int, Dict]:
        """
        Build mapping from page number to TOC location
        Returns:
            Dict[page_num] = {
                'part_id': str,
                'chapter_id': str,
                'article_id': str,
                'article_title': str,
                'article_number': int
            }
        """
        if not self.toc_structure:
            self.logger.error("No TOC structure available in _build_page_mapping")
            return {}
        
        # Use the volume_id as it is (e.g., "volume_1", "volume_2")
        # The TOC structure should have volumes with these exact IDs
        volume = self.toc_structure.volumes.get(volume_id)
        if not volume:
            self.logger.error(f"Volume {volume_id} not found in TOC structure. Available volumes: {list(self.toc_structure.volumes.keys())}")
            return {}

        page_mapping = {}
        # Traverse TOC structure
        for part_id, part in volume.parts.items():
            for chapter_id, chapter in part.chapters.items():
                for article_id, article in chapter.articles.items():
                    # Map each page in article's range
                    page_start = article.page_start
                    # Handle case where page_end might be None or less than page_start
                    page_end = article.page_end if article.page_end else page_start
                    page_end = max(page_start, page_end)  # Ensure page_end >= page_start
                    
                    for page_num in range(page_start, page_end + 1):
                        page_mapping[page_num] = {
                            'part_id': part_id,
                            'part_title': part.title,
                            'chapter_id': chapter_id,
                            'chapter_title': chapter.title,
                            'chapter_number': chapter.chapter_number,
                            'article_id': article_id,
                            'article_title': article.title,
                            'article_number': article.article_number
                        }
        return page_mapping

    def _organize_page(
        self,
        page_ocr: PageOCRResult,
        location: Dict,
        volume_id: str,
        volume_num: int
    ) -> OrganizedPage:
        """
        Organize a single page based on TOC location
        Args:
            page_ocr: OCR data for page
            location: TOC location info
            volume_id: Volume identifier
            volume_num: Volume number
        Returns:
            Organized page with folder structure
        """
        # Create classification (deterministic from TOC)
        classification = ContentClassification(
            detected_part=location['part_id'],
            detected_chapter=location['chapter_id'],
            detected_article=location['article_id'],
            confidence_score=1.0,  # 100% confident - from TOC
            reasoning=f"Page {page_ocr.page_number} mapped from TOC: "
                     f"Article {location['article_number']} "
                     f"({location['article_title']})",
            extracted_section_headers=[],
            article_numbers_found=[location['article_number']]
        )
        
        # Create organized page record
        organized_page = OrganizedPage(
            page_number=page_ocr.page_number,
            volume_id=volume_id,
            part_id=location['part_id'],
            chapter_id=location['chapter_id'],
            article_id=location['article_id'],
            classification=classification,
            file_path="",  # Will be set during file organization
            ocr_data=page_ocr
        )
        
        # Organize files on disk
        self._organize_page_files(organized_page, location, volume_num)
        return organized_page

    def _organize_page_files(
        self,
        organized_page: OrganizedPage,
        location: Dict,
        volume_num: int
    ):
        """
        Create folder structure and save page files
        Folder structure: volume_N/part_id/chapter_id/article_id/page_NNNN.json
        """
        # Build folder path from TOC hierarchy
        base_dir = self.paths.organized_dir / f"volume_{volume_num}"
        
        # Validate and slugify components to create safe directory names
        if organized_page.part_id:
            part_slug = slugify(organized_page.part_id)
            if part_slug:  # Check if slugify didn't return an empty string
                base_dir = base_dir / part_slug
            else:
                self.logger.warning(f"Part ID '{organized_page.part_id}' resulted in an empty slug, skipping directory creation.")
        if organized_page.chapter_id:
            chapter_slug = slugify(organized_page.chapter_id)
            if chapter_slug:
                base_dir = base_dir / chapter_slug
            else:
                self.logger.warning(f"Chapter ID '{organized_page.chapter_id}' resulted in an empty slug, skipping directory creation.")
        if organized_page.article_id:
            article_slug = slugify(organized_page.article_id)
            if article_slug:
                base_dir = base_dir / article_slug
            else:
                self.logger.warning(f"Article ID '{organized_page.article_id}' resulted in an empty slug, skipping directory creation.")
        
        # Ensure the directory exists
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Save page content as JSON
        page_file = base_dir / f"page_{organized_page.page_number:04d}.json"
        save_model_to_json(organized_page, page_file)
        organized_page.file_path = str(page_file)
        
        # Also save a metadata file for the article (if first page)
        metadata_file = base_dir / "article_metadata.json"
        if not metadata_file.exists():
            metadata = {
                'article_id': location['article_id'],
                'article_number': location['article_number'],
                'article_title': location['article_title'],
                'chapter_id': location['chapter_id'],
                'chapter_number': location['chapter_number'],
                'chapter_title': location['chapter_title'],
                'part_id': location['part_id'],
                'part_title': location['part_title'],
                'pages': []  # Will be populated
            }
            import json
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Update metadata with this page
        import json
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        if organized_page.page_number not in metadata.get('pages', []):
            metadata.setdefault('pages', []).append(organized_page.page_number)
            metadata['pages'].sort()
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        self.logger.debug(
            f"Organized page {organized_page.page_number} -> "
            f"Article {location['article_number']}"
        )

    def _save_organization_result(self, result: OrganizationResult):
        """Save organization result to database"""
        result_file = self.paths.database_dir / f"{result.volume_id}_organization.json"
        save_model_to_json(result, result_file)
        self.logger.info(f"Saved organization result to {result_file}")

if __name__ == '__main__':
    organizer = ContentOrganizer()
    print("Page-based content organizer initialized (no AI)")