
import json

def main():
    file_path = "MAXWELL_VOLUME_2_MASTER_OUTPUT/VOLUME_2_PART_3_MAGNETISM.JSON"
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if data:
        # Assuming sorted, but let's be safe
        page_nums = [p.get('page_number', 0) for p in data]
        print(f"Min Page: {min(page_nums)}")
        print(f"Max Page: {max(page_nums)}")

if __name__ == "__main__":
    main()
