
import json

def main():
    file_path = "MAXWELL_VOLUME_1_MASTER_OUTPUT/VOLUME_1_PART_1_ELECTROSTATICS.JSON"
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for page in data:
        if page.get('page_number') == 204:
            print(f"--- Page 204 Content ---")
            print(page.get('mathpix_markdown', '')[:500])
            break

if __name__ == "__main__":
    main()
