import docx

def analyze_thesis():
    doc_path = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\BSC-WD-22-36-01.docx"
    doc = docx.Document(doc_path)
    
    print(f"Total Paragraphs: {len(doc.paragraphs)}")
    print(f"Total Tables: {len(doc.tables)}")
    
    # Print sample paragraphs from each chapter
    print("\n--- SAMPLE PARAGRAPHS AUDIT ---")
    ch_markers = ["CHAPTER 1", "CHAPTER 2", "CHAPTER 3", "CHAPTER 4", "CHAPTER 5", "CHAPTER 6"]
    current_ch = None
    for p in doc.paragraphs:
        txt = p.text.strip()
        for ch in ch_markers:
            if ch in txt.upper():
                current_ch = ch
                print(f"\n[{current_ch}] Header: {txt}")
                break
        if current_ch and len(txt) > 100 and not any(ch in txt.upper() for ch in ch_markers):
            # print first 2 paragraphs per chapter
            # print(f"  {txt[:120]}...")
            pass

if __name__ == "__main__":
    analyze_thesis()
