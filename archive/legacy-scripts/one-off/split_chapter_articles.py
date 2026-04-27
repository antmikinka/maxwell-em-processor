
import json
import os
import re

def clean_filename(s):
    s = re.sub(r'[^a-zA-Z0-9\s]', '', s)
    return s.strip().replace(' ', '_').upper()

def split_text_and_capture(text, pattern):
    # returns [ (art_num_or_None, content_text), ... ]
    if not text:
        return [(None, "")]
    
    parts = pattern.split(text)
    # parts: [pre-text, num1, body1, num2, body2, ...]
    
    result = []
    # Item 0 is always pre-text (belongs to previous)
    result.append((None, parts[0]))
    
    i = 1
    while i < len(parts):
        art_num = parts[i]
        content = parts[i+1]
        # Reconstruct the header header roughly or just keep content? 
        # User wants "Article Files". Usually we want the header included in the text?
        # The user said "IT IS IDENTIFIABLE BY... 28.]". 
        # Typically we keep the header in the text.
        # "28.]" + content
        # We need to normalize or reconstruct the header from the capture group?
        # Actually, if we just prepend the art_num + ".] " it might be fake.
        # Better: capture the whole match? 
        # re.split only captures groups.
        # Let's use finditer to get exact ranges.
        i+=2
        
    return parts

def get_segments(text, pattern):
    """
    Returns list of dicts: {'art_num': int or None, 'text': str}
    'art_num' None means 'continues from previous'.
    'art_num' Integers means 'starts new article X'.
    """
    matches = list(pattern.finditer(text))
    segments = []
    
    last_pos = 0
    for m in matches:
        # content before match
        pre_text = text[last_pos:m.start()]
        if pre_text:
            segments.append({'art_num': None, 'text': pre_text})
        
        # The match itself constitutes the start of an article
        try:
            art_num = int(m.group(1))
        except ValueError:
            art_num = 0 # fall back
            
        # We include the match text in the content of the NEW article
        # So the new article starts with "28.] Experiment..."
        
        # Look ahead to next match or end
        # Actually, simpler:
        # The text form m.start() to m.end() is the header.
        # We start a new segment here.
        
        # But wait, we need the REST of the text until the next match.
        # We can't do that easily in one pass of matches without looking ahead.
        pass
    
    # Simpler approach using split indices
    # pattern has 1 capture group.
    parts = pattern.split(text) 
    # [text0, num1, text1, num2, text2]
    
    # Segment 0: text0. Belongs to PREVIOUS article.
    segments.append({'art_num': None, 'text': parts[0]})
    
    i = 1
    while i < len(parts):
        art_str = parts[i]
        body = parts[i+1]
        
        # Reconstruct header? We lost the exact punctuation (.] or ]) due to regex group `(\d+)`.
        # We should probably capture the full header in the regex using an outer group if we want exact preservation.
        # Let's adjust regex in main.
        
        i += 2
        
    return parts

def main():
    chapter_file = "MAXWELL_VOLUME_1_MASTER_OUTPUT/VOLUME_1_PART_1_CHAPTERS/CHAPTER_I_DESCRIPTION_OF_PHENOMENA.JSON"
    index_file = "maxwell_article_index.json"
    output_dir = "MAXWELL_VOLUME_1_MASTER_OUTPUT/VOLUME_1_PART_1_CHAPTERS/CHAPTER_I_ARTICLES"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Output Directory (Absolute): {os.path.abspath(output_dir)}")
        
    with open(chapter_file, 'r', encoding='utf-8') as f:
        pages = json.load(f)
        
    with open(index_file, 'r', encoding='utf-8') as f:
        master_index = json.load(f)
        
    toc = master_index.get("VOLUME_1_PART_1_CHAPTER_I", [])
    
    # Sort pages
    pages.sort(key=lambda x: x['page_number'])
    
    # We want to capture the FULL header string to preserve it in the text.
    # Regex: ((?:\d+)\s*[. ]?\]) -> Group 1 is full match, Group 2 can be inner number?
    # No, split only includes capturing groups.
    # pattern = re.compile(r"((\d+)\s*[. ]?\])")
    # Split -> [pre, full_header, num, body, ... ]
    
    header_pattern = re.compile(r"((\d+)\s*[. ]?\])")
    
    # Dictionary to hold LIST of page objects for each article
    # articles[art_num] = [ {page_number, raw_text, mathpix_markdown}, ... ]
    articles_data = {}
    current_art = "INTRO" 
    
    print("Processing pages...")
    
    for p in pages:
        p_num = p['page_number']
        md = p.get('mathpix_markdown', '')
        raw = p.get('raw_text', '')
        
        # Split Markdown
        md_parts = header_pattern.split(md)
        # Structure: [text0, header1, num1, text1, header2, num2, text2...]
        
        # Use lists to store segments for this page
        # Each segment: (art_id, md_content)
        page_segments_md = []
        
        # 1. Handle Pre-text
        if md_parts[0]:
            page_segments_md.append((current_art, md_parts[0]))
            
        # 2. Handle Matches
        i = 1
        while i < len(md_parts):
            full_header = md_parts[i]
            art_num_str = md_parts[i+1]
            content = md_parts[i+2]
            
            # Check if the previous segment ended with a Section Header (or "pre-text" contains it at the end)
            # If so, we should steal it and prepend to THIS new article.
            
            # Logic: Look at the very LAST segment added to page_segments_md.
            if page_segments_md:
                last_art, last_text = page_segments_md[-1]
                
                # Regex to find a trailing section header
                # Pattern: \s*\\section\*\{[^}]+\}\s*$
                # Be careful not to match too much.
                section_pattern = re.compile(r"(\s*\\section\*\{[^}]+\}\s*)$", re.DOTALL)
                
                match = section_pattern.search(last_text)
                if match:
                    header_text = match.group(1)
                    # Remove from last_text
                    new_last_text = last_text[:match.start()]
                    
                    # Update previous segment
                    page_segments_md[-1] = (last_art, new_last_text)
                    
                    # Prepend to current header
                    full_header = header_text + full_header
            
            try:
                current_art = int(art_num_str)
            except ValueError:
                pass # keep current
                
            # Combine header + content
            full_content = full_header + content
            page_segments_md.append((current_art, full_content))
            
            i += 3
            
        # Now handle Raw Text
        # We attempt to align. If we find distinct headers in raw text, we split.
        
        # We attempt to align. If we find distinct headers in raw text, we split.
        
        raw_parts = header_pattern.split(raw)
        
        # Validation Step:
        # We must ensure that the headers found in Raw Text actually correspond to the headers in Markdown.
        # We check the content immediately following the header.
        
        # Strategy:
        # 1. Identify all headers in MD.
        # 2. Identify all headers in Raw.
        # 3. For each MD header, see if there is a corresponding Raw header that has matching content.
        # 4. If matching, map them. If not, we can't split Raw securely.
        
        # Extract (art_id, content_start) from MD parts
        md_matches = []
        i = 1
        while i < len(md_parts):
            m_id = md_parts[i+1] # str
            m_content = md_parts[i+2]
            md_matches.append({'id': m_id, 'content': m_content, 'idx': i})
            i += 3
            
        # Extract from Raw parts
        raw_matches = []
        j = 1
        while j < len(raw_parts):
            r_id = raw_parts[j+1]
            r_content = raw_parts[j+2]
            raw_matches.append({'id': r_id, 'content': r_content, 'full_header': raw_parts[j], 'idx': j})
            j += 3
            
        valid_split = True
        raw_segments_map = {}
        
        # If counts differ, valid_split = False immediately?
        # Not necessarily, maybe Raw missed one but caught another.
        # But for safety, if counts differ, we fallback to full text.
        if len(md_matches) != len(raw_matches):
            valid_split = False
        else:
            # Check content match
            for k in range(len(md_matches)):
                m = md_matches[k]
                r = raw_matches[k]
                
                # Check ID match
                if m['id'] != r['id']:
                    valid_split = False
                    break
                    
                # Check Content Fuzzy Match (first 20 chars)
                # Cleanup
                def clean_str(s): return re.sub(r'\s+', '', s).lower()[:30]
                
                mc = clean_str(m['content'])
                rc = clean_str(r['content'])
                
                # We expect rc to start with mc (or vice versa? OCR is noisy).
                # Usually RC should start with MC if structure is preserved.
                # If completely different (like Art 27/28 case), this will fail.
                
                # In Art 27/28 case: MC="Experiment II...", RC="ELECTRIFICATION..."
                # clean(MC) = "experimentii..."
                # clean(RC) = "electrification..."
                # No match.
                
                if mc and rc and (mc not in rc and rc not in mc):
                     # Similarity check ratio?
                     # Simple check:
                     pass # For now let's strict check start
                     if not (rc.startswith(mc[:10]) or mc.startswith(rc[:10])):
                         valid_split = False
                         # print(f"Mismatch on Page {p_num}: MD='{mc}' vs RAW='{rc}'")
                         break
        
        if valid_split:
            # Build the map
            current_raw_art = page_segments_md[0][0]
            if raw_parts[0]:
                if current_raw_art not in raw_segments_map: raw_segments_map[current_raw_art] = ""
                raw_segments_map[current_raw_art] += raw_parts[0]
                
            for k in range(len(raw_matches)):
                r = raw_matches[k]
                art_id = int(r['id'])
                if art_id not in raw_segments_map: raw_segments_map[art_id] = ""
                raw_segments_map[art_id] += r['full_header'] + r['content']
                
            use_split_raw = True
        else:
            use_split_raw = False
            # Fallback to full raw text for everyone


        # ...
        
        for (seg_art, seg_md) in page_segments_md:
            
            # Get corresponding raw text
            if use_split_raw:
                # We successfully split raw text
                seg_raw = raw_segments_map.get(seg_art, "")
                # If this article didn't appear in Raw Text (e.g. valid match in MD, but OCR fail in Raw),
                # Fallback? 
                if not seg_raw:
                    # Try fuzzy? 
                    # If MD found it, it's there. 
                    # Maybe raw text has "2 8 ]" scancode error?
                    # We can't fix that easily. 
                    # We'll leave it empty or provide full page warning? 
                    # Let's provide empty string rather than full page to satisfy "No Multiple Articles".
                    pass
            else:
                 # Raw text has no headers. 
                 # We must provide full raw text to EVERYONE, 
                 # OR we accept that we can't separate.
                 # The User Hate Multiple.
                 # But Data Loss is worse? 
                 # Let's provide full raw text (User said "KEEP SAME DATA").
                 seg_raw = raw
            
            # Add to Article
            if seg_art not in articles_data:
                articles_data[seg_art] = []
            
            # Construct Page Object
            # "KEEP THE SAME DATA ... LIKE page_number ..."
            page_obj = {
                "page_number": p_num,
                "raw_text": seg_raw,
                "mathpix_markdown": seg_md
            }
            articles_data[seg_art].append(page_obj)
                
    # Loop over Pre-text (INTRO) if it exists, maybe output it?
    # User only asked for Articles designated in TOC.
    # We will ignore 'INTRO' key unless user wants it.
    
    for item in toc:
        art_num = item['art']
        title = item['title']
        
        pages_list = articles_data.get(art_num, [])
        
        if not pages_list:
            print(f"Warning: No content for Article {art_num}")
            continue
            
        fname_title = clean_filename(title)[:50]
        fname = f"ARTICLE_{art_num}_{fname_title}.json"
        
        # Wrap in list or just output the list?
        # User said "STORE... IN A JSON FILE... KEEP SAME DATA"
        # Since input was a list of pages, output should be a list of pages.
        
        with open(os.path.join(output_dir, fname), 'w', encoding='utf-8') as f:
            json.dump(pages_list, f, indent=2, ensure_ascii=False)
            
    print(f"Split completed. Check {output_dir}")

if __name__ == "__main__":
    main()
