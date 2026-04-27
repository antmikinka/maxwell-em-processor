
import json
import os

def main():
    input_path = "MAXWELL_VOLUME_2_MASTER_OUTPUT/VOLUME_2_PART_3_MAGNETISM.JSON"
    output_dir = "MAXWELL_VOLUME_2_MASTER_OUTPUT/VOLUME_2_PART_3_CHAPTERS"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
        
    print(f"Reading input from: {input_path}")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: Input file not found.")
        return
        
    # Map page_number to page object for easy access
    pages = {p['page_number']: p for p in data}
    
    chapters = [
        {"num": "I",    "title": "ELEMENTARY_THEORY_OF_MAGNETISM", "start": 28, "end": 48},
        {"num": "II",   "title": "MAGNETIC_FORCE_AND_MAGNETIC_INDUCTION", "start": 49, "end": 59},
        {"num": "III",  "title": "MAGNETIC_SOLENOIDS_AND_SHELLS", "start": 60, "end": 73},
        {"num": "IV",   "title": "INDUCED_MAGNETIZATION", "start": 74, "end": 85},
        {"num": "V",    "title": "PARTICULAR_PROBLEMS_IN_MAGNETIC_INDUCTION", "start": 86, "end": 105},
        {"num": "VI",   "title": "WEBERS_THEORY_OF_INDUCED_MAGNETISM", "start": 106, "end": 121},
        {"num": "VII",  "title": "MAGNETIC_MEASUREMENTS", "start": 122, "end": 155},
        {"num": "VIII", "title": "ON_TERRESTRIAL_MAGNETISM", "start": 156, "end": 164}
    ]
    
    print("\nStarting split...")
    for chap in chapters:
        filename = f"CHAPTER_{chap['num']}_{chap['title']}.JSON"
        file_path = os.path.join(output_dir, filename)
        
        chap_pages = []
        for p_num in range(chap['start'], chap['end'] + 1):
            if p_num in pages:
                chap_pages.append(pages[p_num])
            else:
                print(f"Warning: Page {p_num} (Chapter {chap['num']}) missing in source.")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(chap_pages, f, indent=2, ensure_ascii=False)
            
        print(f"  -> {filename}: {len(chap_pages)} pages ({chap['start']}-{chap['end']})")

    print("\nDone.")

if __name__ == "__main__":
    main()
