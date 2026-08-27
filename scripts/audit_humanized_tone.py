import docx

def review_chapters():
    doc = docx.Document(r"d:\FinalProject 2026\vehicle_damade_dash_cloned\Vehicle_Damage_Assessment_Final_Thesis_2026_Latest.docx")
    
    sections = [
        "1.1 Background",
        "1.2 Problem Statement",
        "2.2 Theoretical",
        "3.2 Research",
        "4.2 System Architecture",
        "4.4 Database Design",
        "4.5 User Interface Design",
        "4.7 Algorithms",
        "5.9 Performance",
        "5.11 Discussion",
        "6.2 Summary",
        "6.8 Conclusion"
    ]
    
    current_sec = None
    captured = {}
    
    for p in doc.paragraphs:
        t = p.text.strip()
        for s in sections:
            if s.lower() in t.lower():
                current_sec = s
                captured[current_sec] = []
                break
        if current_sec and len(t) > 60 and not any(s.lower() in t.lower() for s in sections):
            if len(captured[current_sec]) < 2:
                captured[current_sec].append(t)

    print("=" * 80)
    print("HUMANIZED ACADEMIC TONE AUDIT SAMPLE")
    print("=" * 80)
    for sec, paras in captured.items():
        print(f"\n[{sec}]")
        for i, p in enumerate(paras):
            print(f"  P{i+1}: {p}\n")
    print("=" * 80)

if __name__ == "__main__":
    review_chapters()
