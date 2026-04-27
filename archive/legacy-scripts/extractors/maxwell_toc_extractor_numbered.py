#!/usr/bin/env python3
"""
Maxwell TOC Extractor & Hierarchical Organizer - NUMBERED VERSION
==============================================================

This script extracts Table of Contents, Chapters, and Articles from Maxwell's
Electromagnetic Theory treatise and creates a comprehensive hierarchical folder/file structure.

FEATURE: Uses NUMBERED filenames to avoid filesystem issues with mathematical expressions
while preserving all mathematical content in the JSON metadata.

Filename Format: V1_C2_A15.json (Volume 1, Chapter 2, Article 15)

Author: Claude Code Assistant
Date: November 28, 2025
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('maxwell_toc_extractor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MaxwellTOCExtractor:
    """Extracts and organizes Maxwell's treatise into hierarchical structure with numbered files"""

    def __init__(self, base_output_dir: str = "Maxwell_TOC"):
        """
        Initialize the TOC extractor

        Args:
            base_output_dir: Base directory for output structure
        """
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)

        # Content classification patterns
        self.part_patterns = [
            r'PART\s+(\d+)\s*[:\.\-]?\s*(.+)',
            r'(\w+)\s+PART\s*[:\.\-]?\s*(.+)',
            r'BOOK\s+(\d+)\s*[:\.\-]?\s*(.+)',
            r'(\w+)\s+BOOK\s*[:\.\-]?\s*(.+)'
        ]

        self.chapter_patterns = [
            r'CHAPTER\s+(\d+)\s*[:\.\-]?\s*(.+)',
            r'Chap\.\s*(\d+)\s*[:\.\-]?\s*(.+)',
            r'(\d+)\s*[:\.\-]?\s*(.+?)(?:\n|$)',
            r'[\*\#]+\s*Chapter\s*(\d+)\s*[:\.\-]?\s*(.+)'
        ]

        self.article_patterns = [
            r'ARTICLE\s+(\d+)\s*[:\.\-]?\s*(.+)',
            r'Art\.\s*(\d+)\s*[:\.\-]?\s*(.+)',
            r'(\d+)\.\s*(.+?)(?:\n|$)',
            r'[\*\#]*\s*(\d+)\s*[:\-]?\s*(.+?)(?:\n|$)'
        ]

        # Volume structure
        self.volumes = {}
        logger.info(f"Maxwell TOC Extractor initialized. Output directory: {self.base_output_dir}")

    def load_volume_data(self, volume_num: int) -> Dict[str, Any]:
        """
        Load volume data from JSON file

        Args:
            volume_num: Volume number (1 or 2)

        Returns:
            Volume data dictionary
        """
        json_file = self.base_output_dir.parent / f"MAXWELL_VOLUME_{volume_num}_MASTER_OUTPUT" / f"volume_{volume_num}_direct_result.json"

        if not json_file.exists():
            logger.error(f"Volume {volume_num} JSON file not found: {json_file}")
            return {}

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded Volume {volume_num} data: {data['total_pages']} pages")
            return data
        except Exception as e:
            logger.error(f"Error loading Volume {volume_num} data: {e}")
            return {}

    def extract_content_hierarchy(self, volume_data: Dict[str, Any], volume_num: int) -> Dict[str, Any]:
        """
        Extract hierarchical content structure from volume data

        Args:
            volume_data: Volume data dictionary
            volume_num: Volume number

        Returns:
            Hierarchical structure dictionary
        """
        logger.info(f"Extracting content hierarchy from Volume {volume_num}")

        hierarchy = {
            "volume": {
                "number": volume_num,
                "title": f"Volume {volume_num}",
                "total_pages": volume_data.get('total_pages', 0),
                "parts": []
            }
        }

        # Analyze pages to identify structure
        pages_content = {}
        for page_num, page_data in volume_data.get('pages', {}).items():
            page_content = {
                'raw_text': page_data.get('raw_text', ''),
                'mathpix_markdown': page_data.get('mathpix_markdown', ''),
                'line_data': page_data.get('line_data', []),
                'page_number': int(page_num)
            }
            pages_content[int(page_num)] = page_content

        # Sort pages by number
        sorted_pages = sorted(pages_content.items())

        # Extract parts, chapters, and articles
        parts = self._find_parts(sorted_pages)
        logger.info(f"Found {len(parts)} parts in Volume {volume_num}")

        for part_idx, part in enumerate(parts):
            part_data = {
                "part_id": f"part_{part_idx + 1}",
                "part_number": part_idx + 1,
                "title": part['title'],
                "page_start": part['page_start'],
                "page_end": part.get('page_end', volume_data.get('total_pages', 0)),
                "chapters": []
            }

            # Find chapters within this part
            part_pages = [(p, d) for p, d in sorted_pages
                        if p >= part['page_start'] and
                        (p <= part.get('page_end', volume_data.get('total_pages', 0)))]

            chapters = self._find_chapters(part_pages)
            logger.info(f"Found {len(chapters)} chapters in Part {part_idx + 1}")

            for chapter_idx, chapter in enumerate(chapters):
                chapter_data = {
                    "chapter_id": f"chapter_{chapter_idx + 1}",
                    "chapter_number": chapter['number'],
                    "title": chapter['title'],
                    "page_start": chapter['page_start'],
                    "page_end": chapter.get('page_end', part.get('page_end', volume_data.get('total_pages', 0))),
                    "articles": []
                }

                # Find articles within this chapter
                chapter_pages = [(p, d) for p, d in part_pages
                               if p >= chapter['page_start'] and
                               (p <= chapter.get('page_end', part.get('page_end', volume_data.get('total_pages', 0))))]

                articles = self._find_articles(chapter_pages)
                logger.info(f"Found {len(articles)} articles in Chapter {chapter['number']}")

                for article_idx, article in enumerate(articles):
                    article_data = {
                        "article_id": f"article_{article['number']}",
                        "article_number": article['number'],
                        "title_original": article['title'],  # Keep original mathematical title
                        "title_safe": self._create_safe_title(article['title']),  # Safe version for folders
                        "page_start": article['page_start'],
                        "page_end": article.get('page_end', chapter.get('page_end', volume_data.get('total_pages', 0))),
                        "content": self._extract_article_content(chapter_pages, article),
                        "equations": self._extract_equations(chapter_pages, article),
                        "figures": self._extract_figures(chapter_pages, article),
                        "metadata": {
                            "word_count": article.get('word_count', 0),
                            "line_count": article.get('line_count', 0),
                            "confidence_score": article.get('confidence_score', 0.0)
                        }
                    }
                    chapter_data["articles"].append(article_data)

                part_data["chapters"].append(chapter_data)

            hierarchy["volume"]["parts"].append(part_data)

        return hierarchy

    def _find_parts(self, sorted_pages: List[Tuple[int, Dict]]) -> List[Dict]:
        """Find parts in the document"""
        parts = []
        current_part = None

        for page_num, page_data in sorted_pages:
            content = f"{page_data['raw_text']} {page_data['mathpix_markdown']}".strip()

            for pattern in self.part_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    if current_part:
                        # End current part
                        current_part['page_end'] = page_num - 1
                        parts.append(current_part)

                    # Start new part
                    if len(match) >= 2:
                        part_number = match[0] if match[0].isdigit() else len(parts) + 1
                        part_title = match[1].strip()
                        current_part = {
                            'number': part_number,
                            'title': part_title,
                            'page_start': page_num
                        }
                        logger.info(f"Found Part {part_number}: {part_title} (page {page_num})")

        # Handle last part
        if current_part:
            current_part['page_end'] = sorted_pages[-1][0]
            parts.append(current_part)

        # Fallback: if no parts found, create a default part
        if not parts:
            parts.append({
                'number': 1,
                'title': f"Volume {sorted_pages[0][1].get('page_number', 1) // 100 + 1} Content",
                'page_start': sorted_pages[0][0],
                'page_end': sorted_pages[-1][0]
            })

        return parts

    def _find_chapters(self, pages: List[Tuple[int, Dict]]) -> List[Dict]:
        """Find chapters within a section"""
        chapters = []
        current_chapter = None

        for page_num, page_data in pages:
            content = f"{page_data['raw_text']} {page_data['mathpix_markdown']}".strip()

            for pattern in self.chapter_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    if current_chapter:
                        # End current chapter
                        current_chapter['page_end'] = page_num - 1
                        chapters.append(current_chapter)

                    # Start new chapter
                    if len(match) >= 2:
                        chapter_number = int(match[0]) if match[0].isdigit() else len(chapters) + 1
                        chapter_title = match[1].strip()
                        current_chapter = {
                            'number': chapter_number,
                            'title': chapter_title,
                            'page_start': page_num
                        }
                        logger.info(f"Found Chapter {chapter_number}: {chapter_title} (page {page_num})")

        # Handle last chapter
        if current_chapter:
            current_chapter['page_end'] = pages[-1][0]
            chapters.append(current_chapter)

        return chapters

    def _find_articles(self, pages: List[Tuple[int, Dict]]) -> List[Dict]:
        """Find articles within a chapter"""
        articles = []
        current_article = None

        for page_num, page_data in pages:
            content = f"{page_data['raw_text']} {page_data['mathpix_markdown']}".strip()

            for pattern in self.article_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    if current_article:
                        # End current article
                        current_article['page_end'] = page_num - 1
                        articles.append(current_article)

                    # Start new article
                    if len(match) >= 2:
                        article_number = int(match[0]) if match[0].isdigit() else len(articles) + 1
                        article_title = match[1].strip()
                        current_article = {
                            'number': article_number,
                            'title': article_title,
                            'page_start': page_num,
                            'word_count': 0,
                            'line_count': 0,
                            'confidence_score': 0.0
                        }
                        logger.info(f"Found Article {article_number}: {article_title} (page {page_num})")

        # Handle last article
        if current_article:
            current_article['page_end'] = pages[-1][0]
            articles.append(current_article)

        return articles

    def _create_safe_title(self, title: str) -> str:
        """
        Create a safe version of the title for folder names
        Keep essential info but remove problematic characters
        """
        if not title or not title.strip():
            return "Article"

        # Replace common mathematical symbols with words
        replacements = {
            '$': '',
            '\\': '',
            '{': '',
            '}': '',
            '[': '',
            ']': '',
            '^': '',
            '_': '',
            '&': 'and',
            '%': 'percent',
            '#': 'number',
            '@': 'at',
            '+': 'plus',
            '=': 'equals',
            ';': '',
            ',': '',
            '!': '',
            '?': '',
            '(': '',
            ')': '',
            '<': 'less_than',
            '>': 'greater_than',
            '"': '',
            "'": ''
        }

        safe_title = title
        for old_char, new_char in replacements.items():
            safe_title = safe_title.replace(old_char, new_char)

        # Remove LaTeX commands
        import re
        safe_title = re.sub(r'\\[a-zA-Z]+', '', safe_title)
        safe_title = re.sub(r'\\[{}]', '', safe_title)

        # Normalize whitespace
        safe_title = re.sub(r'\s+', ' ', safe_title)
        safe_title = safe_title.strip()

        # Limit length for folders
        max_length = 60
        if len(safe_title) > max_length:
            safe_title = safe_title[:max_length].strip()

        # Remove leading/trailing problematic chars
        safe_title = safe_title.strip(' ._-')

        return safe_title if safe_title else "Article"

    def _extract_article_content(self, pages: List[Tuple[int, Dict]], article: Dict) -> Dict:
        """Extract content for a specific article"""
        content = {
            "raw_text": "",
            "mathpix_markdown": "",
            "structured_lines": []
        }

        article_start = article['page_start']
        article_end = article.get('page_end', article_start)

        for page_num, page_data in pages:
            if article_start <= page_num <= article_end:
                # Add page content
                content["raw_text"] += f"\n--- Page {page_num} ---\n{page_data['raw_text']}\n"
                content["mathpix_markdown"] += f"\n--- Page {page_num} ---\n{page_data['mathpix_markdown']}\n"

                # Add structured lines
                for line in page_data['line_data']:
                    if line.get('type') in ['text', 'equation', 'title']:
                        line_data = {
                            'page': page_num,
                            'line_number': line.get('line'),
                            'type': line.get('type'),
                            'content': line.get('text', ''),
                            'mathpix_content': line.get('text_display', ''),
                            'font_size': line.get('font_size'),
                            'confidence': line.get('confidence')
                        }
                        content["structured_lines"].append(line_data)

        return content

    def _extract_equations(self, pages: List[Tuple[int, Dict]], article: Dict) -> List[Dict]:
        """Extract equations for a specific article"""
        equations = []
        article_start = article['page_start']
        article_end = article.get('page_end', article_start)

        for page_num, page_data in pages:
            if article_start <= page_num <= article_end:
                for eq in page_data.get('equations', []):
                    equation_data = {
                        'equation_id': eq.get('equation_id'),
                        'latex': eq.get('latex'),
                        'mathml': eq.get('mathml'),
                        'page': page_num,
                        'location': eq.get('location'),
                        'confidence': eq.get('confidence')
                    }
                    equations.append(equation_data)

        return equations

    def _extract_figures(self, pages: List[Tuple[int, Dict]], article: Dict) -> List[Dict]:
        """Extract figures for a specific article"""
        figures = []
        article_start = article['page_start']
        article_end = article.get('page_end', article_start)

        for page_num, page_data in pages:
            if article_start <= page_num <= article_end:
                for fig in page_data.get('figures', []):
                    figure_data = {
                        'figure_id': fig.get('figure_id'),
                        'image_path': fig.get('image_path'),
                        'caption': fig.get('caption'),
                        'description': fig.get('description'),
                        'page': page_num,
                        'location': fig.get('location')
                    }
                    figures.append(figure_data)

        return figures

    def create_hierarchical_structure(self, hierarchy: Dict[str, Any], volume_num: int):
        """
        Create the hierarchical folder/file structure with numbered files
        """
        volume_dir = self.base_output_dir / f"V{volume_num}_Volume_{volume_num}"
        volume_dir.mkdir(exist_ok=True)

        logger.info(f"Creating hierarchical structure for Volume {volume_num}")

        # Create volume metadata
        volume_metadata = {
            "volume_number": volume_num,
            "title": hierarchy["volume"]["title"],
            "total_pages": hierarchy["volume"]["total_pages"],
            "total_parts": len(hierarchy["volume"]["parts"]),
            "total_chapters": sum(len(part["chapters"]) for part in hierarchy["volume"]["parts"]),
            "total_articles": sum(len(chapter["articles"]) for part in hierarchy["volume"]["parts"] for chapter in part["chapters"]),
            "created_at": datetime.now().isoformat(),
            "structure_summary": self._generate_structure_summary(hierarchy)
        }

        # Save volume metadata
        with open(volume_dir / "volume_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(volume_metadata, f, indent=2)

        # Create parts
        for part in hierarchy["volume"]["parts"]:
            part_dir = volume_dir / f"P{part['part_number']:02d}_Part_{part['part_number']:02d}_{self._create_safe_title(part['title'])}"
            part_dir.mkdir(exist_ok=True)

            # Save part metadata
            with open(part_dir / "part_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(part, f, indent=2)

            # Create chapters
            for chapter in part["chapters"]:
                chapter_dir = part_dir / f"C{chapter['chapter_number']:03d}_Chapter_{chapter['chapter_number']:03d}_{self._create_safe_title(chapter['title'])}"
                chapter_dir.mkdir(exist_ok=True)

                # Save chapter metadata
                with open(chapter_dir / "chapter_metadata.json", 'w', encoding='utf-8') as f:
                    json.dump(chapter, f, indent=2)

                # Create articles with NUMBERED filenames
                for article in chapter["articles"]:
                    # NUMBERED FILENAME FORMAT: V1_C2_A15.json
                    article_filename = f"V{volume_num}_C{chapter['chapter_number']:03d}_A{article['article_number']:04d}.json"
                    article_path = chapter_dir / article_filename

                    # Save article data with original mathematical title preserved
                    with open(article_path, 'w', encoding='utf-8') as f:
                        json.dump(article, f, indent=2)

                    logger.info(f"Created article file: {article_path}")

        logger.info(f"Hierarchical structure created for Volume {volume_num}")

    def _generate_structure_summary(self, hierarchy: Dict[str, Any]) -> Dict:
        """Generate a summary of the structure"""
        summary = {
            "parts": [],
            "chapters_per_part": {},
            "articles_per_chapter": {}
        }

        for part_idx, part in enumerate(hierarchy["volume"]["parts"]):
            part_summary = {
                "part_number": part["part_number"],
                "title": part["title"],
                "page_range": f"{part['page_start']}-{part.get('page_end', 'unknown')}",
                "chapter_count": len(part["chapters"])
            }
            summary["parts"].append(part_summary)
            summary["chapters_per_part"][part["part_number"]] = len(part["chapters"])

            for chapter in part["chapters"]:
                summary["articles_per_chapter"][f"{part['part_number']}.{chapter['chapter_number']}"] = len(chapter["articles"])

        return summary

    def generate_master_index(self):
        """Generate a master index file for the entire structure"""
        master_index = {
            "maxwell_toc_index": {
                "created_at": datetime.now().isoformat(),
                "total_volumes": len([d for d in self.base_output_dir.iterdir() if d.is_dir() and d.name.startswith('V')]),
                "volumes": {},
                "navigation": {
                    "file_naming": "NUMBERED FORMAT: V1_C002_A0015.json (Volume 1, Chapter 002, Article 0015)",
                    "folder_structure": "V1_Volume_1/P01_Part_01/C001_Chapter_001/",
                    "metadata_files": "Each level has a metadata.json file with structural information",
                    "article_content": "Each article contains full content, equations, and figures with original mathematical titles preserved"
                }
            }
        }

        # Scan for volumes
        for volume_dir in self.base_output_dir.iterdir():
            if volume_dir.is_dir() and volume_dir.name.startswith('V'):
                volume_num = int(volume_dir.name.split('_')[0][1:])

                volume_metadata_file = volume_dir / "volume_metadata.json"
                if volume_metadata_file.exists():
                    with open(volume_metadata_file, 'r', encoding='utf-8') as f:
                        volume_metadata = json.load(f)

                    master_index["maxwell_toc_index"]["volumes"][volume_num] = {
                        "title": volume_metadata["title"],
                        "total_pages": volume_metadata["total_pages"],
                        "total_parts": volume_metadata["total_parts"],
                        "total_chapters": volume_metadata["total_chapters"],
                        "total_articles": volume_metadata["total_articles"],
                        "path": str(volume_dir.relative_to(self.base_output_dir))
                    }

        # Save master index
        with open(self.base_output_dir / "MASTER_TOC_INDEX.json", 'w', encoding='utf-8') as f:
            json.dump(master_index, f, indent=2)

        logger.info("Master TOC index generated")

    def process_both_volumes(self):
        """Process both volumes and create complete hierarchical structure"""
        logger.info("Starting comprehensive TOC extraction for both volumes")

        for volume_num in [1, 2]:
            logger.info(f"Processing Volume {volume_num}")

            # Load volume data
            volume_data = self.load_volume_data(volume_num)
            if not volume_data:
                logger.warning(f"Skipping Volume {volume_num} - no data available")
                continue

            # Extract hierarchy
            hierarchy = self.extract_content_hierarchy(volume_data, volume_num)

            # Create structure
            self.create_hierarchical_structure(hierarchy, volume_num)

        # Generate master index
        self.generate_master_index()

        logger.info("TOC extraction completed for both volumes")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Maxwell TOC Extractor & Hierarchical Organizer - NUMBERED VERSION")
    parser.add_argument("--base-dir", default="Maxwell_TOC",
                       help="Base directory for output structure (default: Maxwell_TOC)")
    parser.add_argument("--volume", type=int, choices=[1, 2, 0], default=0,
                       help="Volume to process (1, 2, or 0 for both)")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    extractor = MaxwellTOCExtractor(args.base_dir)

    if args.volume == 0:
        extractor.process_both_volumes()
    else:
        logger.info(f"Processing Volume {args.volume}")
        volume_data = extractor.load_volume_data(args.volume)
        if volume_data:
            hierarchy = extractor.extract_content_hierarchy(volume_data, args.volume)
            extractor.create_hierarchical_structure(hierarchy, args.volume)
            extractor.generate_master_index()

    logger.info("Maxwell TOC extraction completed successfully!")
    print(f"\n✅ TOC extraction completed!")
    print(f"📁 Output directory: {extractor.base_output_dir}")
    print(f"📋 Master index: {extractor.base_output_dir / 'MASTER_TOC_INDEX.json'}")
    print(f"🔢 File naming: V1_C002_A0015.json (Volume 1, Chapter 002, Article 0015)")
    print(f"🧮 Mathematical titles preserved in JSON metadata!")


if __name__ == "__main__":
    main()