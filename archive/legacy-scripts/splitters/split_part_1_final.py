
import json
import os

def main():
    input_path = "MAXWELL_VOLUME_1_MASTER_OUTPUT/VOLUME_1_PART_1_ELECTROSTATICS.JSON"
    output_dir = "MAXWELL_VOLUME_1_MASTER_OUTPUT/VOLUME_1_PART_1_CHAPTERS"
    
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
        {"num": "I",    "title": "DESCRIPTION_OF_PHENOMENA", "start": 67, "end": 105},
        {"num": "II",   "title": "ELEMENTARY_MATHEMATICAL_THEORY_OF_ELECTRICITY", "start": 106, "end": 137},
        {"num": "III",  "title": "ON_ELECTRICAL_WORK_AND_ENERGY_IN_A_SYSTEM_OF_CONDUCTORS", "start": 138, "end": 157},
        {"num": "IV",   "title": "GENERAL_THEOREMS", "start": 158, "end": 189},
        {"num": "V",    "title": "MECHANICAL_ACTION_BETWEEN_TWO_ELECTRICAL_SYSTEMS", "start": 190, "end": 203},
        {"num": "VI",   "title": "POINTS_AND_LINES_OF_EQUILIBRIUM", "start": 204, "end": 211},
        {"num": "VII",  "title": "FORMS_OF_EQUIPOTENTIAL_SURFACES_AND_LINES_OF_FLOW", "start": 212, "end": 220},
        {"num": "VIII", "title": "SIMPLE_CASES_OF_ELECTRIFICATION", "start": 221, "end": 228},
        {"num": "IX",   "title": "SPHERICAL_HARMONICS", "start": 229, "end": 266},
        {"num": "X",    "title": "CONFOCAL_SURFACES_OF_THE_SECOND_DEGREE", "start": 267, "end": 278},
        {"num": "XI",   "title": "THEORY_OF_ELECTRIC_IMAGES", "start": 279, "end": 318},
        {"num": "XII",  "title": "CONJUGATE_FUNCTIONS_IN_TWO_DIMENSIONS", "start": 319, "end": 351},
        {"num": "XIII", "title": "ELECTROSTATIC_INSTRUMENTS", "start": 352, "end": 388}
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
