
import json

def main():
    file_path = "MAXWELL_VOLUME_2_MASTER_OUTPUT/VOLUME_2_PART_4_ELECTROMAGNETISM.JSON"
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    pages_to_check = [458, 478, 479, 480]
    
    for page in data:
        p_num = page.get('page_number')
        if p_num in pages_to_check:
            print(f"--- Page {p_num} Content Start ---")
            print(page.get('mathpix_markdown', '')[:300].replace('\n', ' '))
            print(f"--- Page {p_num} Content End ---")

if __name__ == "__main__":
    main()
