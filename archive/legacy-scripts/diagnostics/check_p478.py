
import json

def main():
    file_path = "MAXWELL_VOLUME_1_MASTER_OUTPUT/VOLUME_1_PART_1_CHAPTERS/CHAPTER_I_DESCRIPTION_OF_PHENOMENA.JSON"
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    import re
    
    pattern = re.compile(r"(\d+)\s*\.\]")
    
    print("Scanning for Article headers (e.g., '27.]')...")
    for page in data:
        text = page.get('mathpix_markdown', '')
        matches = pattern.findall(text)
        if matches:
            print(f"Page {page.get('page_number')}: Found {matches}")
            # Print context for the first match
            first_match = pattern.search(text)
            start = max(0, first_match.start() - 20)
            end = min(len(text), first_match.end() + 50)
            print(f"  Context: ...{text[start:end].replace(chr(10), ' ')}...")

if __name__ == "__main__":
    main()
