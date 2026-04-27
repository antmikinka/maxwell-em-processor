import json
import os

def load_data(file_path):
    """Loads the JSON data from the given file path."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_pages(data):
    """Returns a sorted list of integer page numbers available in the data."""
    if 'pages' not in data:
        return []
    
    # Keys are strings, convert to int for sorting
    page_nums = [int(k) for k in data['pages'].keys()]
    return sorted(page_nums)

def get_page_content(data, page_num):
    """
    Returns a dictionary with content for the specified page number.
    Returns None if the page is not found.
    """
    page_key = str(page_num)
    if 'pages' in data and page_key in data['pages']:
        page_data = data['pages'][page_key]
        return {
            'page_number': page_data.get('page_number'),
            'raw_text': page_data.get('raw_text', ''),
            'mathpix_markdown': page_data.get('mathpix_markdown', '')
        }
    return None

def main():
    # Path to the JSON file
    # Assuming the script is run from the root or we provide absolute path. 
    # Using the path provided in the user context.
    file_path = r"c:\Users\antmi\Downloads\maxwell_em_processor\MAXWELL_VOLUME_2_MASTER_OUTPUT\volume_2_direct_result.json"
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    print(f"Loading data from {file_path}...")
    data = load_data(file_path)
    
    # List pages
    pages = list_pages(data)
    print(f"Total pages found: {len(pages)}")
    print(f"First 5 pages: {pages[:5]}")
    print(f"Last 5 pages: {pages[-5:]}")
    
    # Split Volume 2 into 5 parts as requested
    splits = [
        {
            "filename": "VOLUME_2_PRELIM_TOC.JSON",
            "start": 1,
            "end": 27
        },
        {
            "filename": "VOLUME_2_PART_3_MAGNETISM.JSON",
            "start": 28,
            "end": 164
        },
        {
            "filename": "VOLUME_2_PART_4_ELECTROMAGNETISM.JSON",
            "start": 165,
            "end": 520
        },
        {
            "filename": "VOLUME_2_INDEX.JSON",
            "start": 521,
            "end": 527
        },
        {
            "filename": "VOLUME_2_PLATES_DIAGRAMS.JSON",
            "start": 528,
            "end": 544
        }
    ]
    
    for split in splits:
        target_pages = list(range(split["start"], split["end"] + 1))
        print(f"\nExtracting {len(target_pages)} pages for {split['filename']} ({split['start']}-{split['end']})...")
        
        chapter_content = []
        for p in target_pages:
            content = get_page_content(data, p)
            if content:
                chapter_content.append(content)
            else:
                pass # Skip missing pages silently
                
        output_path = os.path.join(os.path.dirname(file_path), split["filename"])
        print(f"Saving to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chapter_content, f, indent=2, ensure_ascii=False)
            
    print("\nAll splits completed.")

if __name__ == "__main__":
    main()
