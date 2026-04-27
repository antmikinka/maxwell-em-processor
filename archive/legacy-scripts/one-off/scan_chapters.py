
import json
import re

def main():
    file_path = "MAXWELL_VOLUME_2_MASTER_OUTPUT/VOLUME_2_PART_4_ELECTROMAGNETISM.JSON"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    print(f"Loaded {len(data)} pages.")
    
    # Sort just in case
    data.sort(key=lambda x: x.get('page_number', 0))

    chapter_pattern = re.compile(r"CHAPTER\s+([IVX]+)", re.IGNORECASE)

    for page in data:
        page_num = page.get('page_number')
        text = page.get('mathpix_markdown', '')
        
        # Look for CHAPTER X at start of lines or arguably anywhere prominent
        # But usually they are headers.
        
        # simple check
        if "CHAPTER" in text:
            # Try to extract the number
            match = chapter_pattern.search(text)
            if match:
                print(f"Page {page_num}: Found {match.group(0)}")
            else:
                # Might be a mention of a chapter, print snippet
                print(f"Page {page_num}: 'CHAPTER' found, but regex didn't match cleanly. Snippet: {text[:100].replace(chr(10), ' ')}")

if __name__ == "__main__":
    main()
