
import json
import os

def main():
    input_path = "MAXWELL_VOLUME_1_MASTER_OUTPUT/VOLUME_1_PART_2_ELECTROKINEMATICS.JSON"
    output_dir = "MAXWELL_VOLUME_1_MASTER_OUTPUT/VOLUME_1_PART_2_CHAPTERS"
    
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
        {"num": "I",    "title": "THE_ELECTRIC_CURRENT", "start": 389, "end": 396},
        {"num": "II",   "title": "CONDUCTION_AND_RESISTANCE", "start": 397, "end": 401},
        {"num": "III",  "title": "ELECTROMOTIVE_FORCE_BETWEEN_BODIES_IN_CONTACT", "start": 402, "end": 409},
        {"num": "IV",   "title": "ELECTROLYSIS", "start": 410, "end": 421},
        {"num": "V",    "title": "ELECTROLYTIC_POLARIZATION", "start": 422, "end": 433},
        {"num": "VI",   "title": "MATHEMATICAL_THEORY_OF_THE_DISTRIBUTION_OF_ELECTRIC_CURRENTS", "start": 434, "end": 445},
        {"num": "VII",  "title": "CONDUCTION_IN_THREE_DIMENSIONS", "start": 446, "end": 452},
        {"num": "VIII", "title": "RESISTANCE_AND_CONDUCTIVITY_IN_THREE_DIMENSIONS", "start": 453, "end": 469},
        {"num": "IX",   "title": "CONDUCTION_THROUGH_HETEROGENEOUS_MEDIA", "start": 470, "end": 484},
        {"num": "X",    "title": "CONDUCTION_IN_DIELECTRICS", "start": 485, "end": 499},
        {"num": "XI",   "title": "MEASUREMENT_OF_THE_ELECTRIC_RESISTANCE_OF_CONDUCTORS", "start": 500, "end": 529},
        {"num": "XII",  "title": "ELECTRIC_RESISTANCE_OF_SUBSTANCES", "start": 530, "end": 541}
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
