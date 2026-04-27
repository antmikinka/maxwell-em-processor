
import json
import os

def main():
    input_path = "MAXWELL_VOLUME_2_MASTER_OUTPUT/VOLUME_2_PART_4_ELECTROMAGNETISM.JSON"
    output_dir = "MAXWELL_VOLUME_2_MASTER_OUTPUT/VOLUME_2_PART_4_CHAPTERS"
    
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
    
    # Ranges adjusted based on verification (XXI starts 478, XX starts 458)
    chapters = [
        {"num": "I",    "title": "ELECTROMAGNETIC_FORCE", "start": 165, "end": 184},
        {"num": "II",   "title": "AMPERES_INVESTIGATION_OF_THE_MUTUAL_ACTION_OF_ELECTRIC_CURRENTS", "start": 185, "end": 201},
        {"num": "III",  "title": "ON_THE_INDUCTION_OF_ELECTRIC_CURRENTS", "start": 202, "end": 221},
        {"num": "IV",   "title": "ON_THE_INDUCTION_OF_A_CURRENT_ON_ITSELF", "start": 222, "end": 225},
        {"num": "V",    "title": "ON_THE_EQUATIONS_OF_MOTION_OF_A_CONNECTED_SYSTEM", "start": 226, "end": 237},
        {"num": "VI",   "title": "DYNAMICAL_THEORY_OF_ELECTROMAGNETISM", "start": 238, "end": 249},
        {"num": "VII",  "title": "THEORY_OF_ELECTRIC_CIRCUITS", "start": 250, "end": 255},
        {"num": "VIII", "title": "EXPLORATION_OF_THE_FIELD_BY_MEANS_OF_THE_SECONDARY_CIRCUIT", "start": 256, "end": 273},
        {"num": "IX",   "title": "GENERAL_EQUATIONS_OF_THE_ELECTROMAGNETIC_FIELD", "start": 274, "end": 289},
        {"num": "X",    "title": "DIMENSIONS_OF_ELECTRIC_UNITS", "start": 290, "end": 296},
        {"num": "XI",   "title": "ON_ENERGY_AND_STRESS_IN_THE_ELECTROMAGNETIC_FIELD", "start": 297, "end": 312},
        {"num": "XII",  "title": "CURRENT_SHEETS", "start": 313, "end": 341},
        {"num": "XIII", "title": "PARALLEL_CURRENTS", "start": 342, "end": 357},
        {"num": "XIV",  "title": "CIRCULAR_CURRENTS", "start": 358, "end": 377},
        {"num": "XV",   "title": "ELECTROMAGNETIC_INSTRUMENTS", "start": 378, "end": 400},
        {"num": "XVI",  "title": "ELECTROMAGNETIC_OBSERVATIONS", "start": 401, "end": 418},
        {"num": "XVII", "title": "COMPARISON_OF_COILS", "start": 419, "end": 428},
        {"num": "XVIII", "title": "ELECTROMAGNETIC_UNIT_OF_RESISTANCE", "start": 429, "end": 439},
        {"num": "XIX",  "title": "COMPARISON_OF_THE_ELECTROSTATIC_WITH_THE_ELECTROMAGNETIC_UNITS", "start": 440, "end": 457},
        {"num": "XX",   "title": "ELECTROMAGNETIC_THEORY_OF_LIGHT", "start": 458, "end": 477},
        {"num": "XXI",  "title": "MAGNETIC_ACTION_ON_LIGHT", "start": 478, "end": 497},
        {"num": "XXII", "title": "FERROMAGNETISM_AND_DIAMAGNETISM_EXPLAINED_BY_MOLECULAR_CURRENTS", "start": 498, "end": 506},
        {"num": "XXIII","title": "THEORIES_OF_ACTION_AT_A_DISTANCE", "start": 507, "end": 520}
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
