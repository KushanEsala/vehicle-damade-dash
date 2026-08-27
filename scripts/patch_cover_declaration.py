import os
import sys

def create_full_builder():
    # Read baseline script
    base_file = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\scripts\generate_final_thesis_docx.py"
    with open(base_file, "r", encoding="utf-8") as f:
        code = f.read()

    # Ensure cover page and declaration match the exact template
    # Check if SIBA logo is included in cover page
    old_cover = '''    # -------------------------------------------------------------
    # SECTION 1: COVER / TITLE PAGE
    # -------------------------------------------------------------
    sec1 = doc.sections[0]'''
    
    new_cover = '''    # -------------------------------------------------------------
    # SECTION 1: COVER / TITLE PAGE (SIBA Template Page 1)
    # -------------------------------------------------------------
    sec1 = doc.sections[0]
    sec1.page_width = Mm(210)
    sec1.page_height = Mm(297)
    sec1.top_margin = Inches(1.0)
    sec1.bottom_margin = Inches(1.0)
    sec1.left_margin = Inches(1.5)
    sec1.right_margin = Inches(1.0)
    sec1.different_first_page_header_footer = True

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(20)
    p_title.paragraph_format.space_after = Pt(20)
    r = p_title.add_run("VEHICLE DAMAGE DETECTION USING DEEP LEARNING INSTANCE SEGMENTATION FOR AUTOMATED INSURANCE ERP ASSESSMENT")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(16)
    p_sub.paragraph_format.space_after = Pt(16)
    r = p_sub.add_run("A PROJECT THESIS SUBMITTED BY")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

    p_author = doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_author.paragraph_format.space_before = Pt(14)
    p_author.paragraph_format.space_after = Pt(6)
    r = p_author.add_run("W.M.M.G. SENAVIRATHNE\\n(BSC/WD/22/36/01)")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True

    p_to = doc.add_paragraph()
    p_to.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_to.paragraph_format.space_before = Pt(16)
    p_to.paragraph_format.space_after = Pt(6)
    r = p_to.add_run("to the\\nDEPARTMENT OF INFORMATION TECHNOLOGY")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_deg.paragraph_format.space_before = Pt(16)
    p_deg.paragraph_format.space_after = Pt(6)
    r_deg_it = p_deg.add_run("in partial fulfilment of the requirement for the award of the degree of\\n")
    r_deg_it.font.name = 'Times New Roman'
    r_deg_it.font.size = Pt(12)
    r_deg_it.font.italic = True
    r_deg_name = p_deg.add_run("BSc. in Information Technology")
    r_deg_name.font.name = 'Times New Roman'
    r_deg_name.font.size = Pt(13)
    r_deg_name.font.bold = True

    p_of = doc.add_paragraph()
    p_of.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_of.paragraph_format.space_before = Pt(10)
    p_of.paragraph_format.space_after = Pt(8)
    r = p_of.add_run("of the")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)

    # SIBA Campus Logo
    logo_path = os.path.join(out_dir, "reports", "siba_logo.png")
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(4)
        p_logo.paragraph_format.space_after = Pt(8)
        run_logo = p_logo.add_run()
        run_logo.add_picture(logo_path, width=Inches(2.2))

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(6)
    p_inst.paragraph_format.space_after = Pt(0)
    r = p_inst.add_run("SRI LANKA INTERNATIONAL BUDDHIST ACADEMY\\nPALLEKELE SRI LANKA\\n2026")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

    # -------------------------------------------------------------
    # SECTION 2: PRELIMINARY PAGES (SIBA Template Pages 2 to 11)
    # -------------------------------------------------------------
    sec2 = doc.add_section()
    sec2.page_width = Mm(210)
    sec2.page_height = Mm(297)
    sec2.top_margin = Inches(1.0)
    sec2.bottom_margin = Inches(1.0)
    sec2.left_margin = Inches(1.5)
    sec2.right_margin = Inches(1.0)
    set_section_pagination(sec2, fmt="lowerRoman", start=1)

    p_f2 = sec2.footer.paragraphs[0]
    p_f2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_footer_page_number(p_f2)

    # DECLARATION (Template Page 2)
    add_h1("DECLARATION")
    add_p(
        "I do hereby declare that the work reported in this final project report was exclusively carried out by me "
        "under the supervision of Ms. Bhagya Thilakarathne. It describes the results of my own independent work "
        "except where due reference has been made in the text. No part of this project report has been submitted "
        "earlier or concurrently for the same or any other degree."
    )
    
    p_cand_sig = doc.add_paragraph()
    p_cand_sig.paragraph_format.space_before = Pt(28)
    p_cand_sig.paragraph_format.space_after = Pt(24)
    r_cs = p_cand_sig.add_run("Date: ………………………………………                     …………………………………………\\n                                                                           Signature of the Candidate")
    r_cs.font.name = 'Times New Roman'
    r_cs.font.size = Pt(11)

    p_cert = doc.add_paragraph()
    p_cert.paragraph_format.space_before = Pt(14)
    p_cert.paragraph_format.space_after = Pt(6)
    r_cert = p_cert.add_run("Certified by:\\nSupervisor: Ms. Bhagya Thilakarathne")
    r_cert.font.name = 'Times New Roman'
    r_cert.font.size = Pt(11)
    r_cert.font.bold = True

    p_sup_sig = doc.add_paragraph()
    p_sup_sig.paragraph_format.space_before = Pt(10)
    p_sup_sig.paragraph_format.space_after = Pt(20)
    r_ss = p_sup_sig.add_run("Date: …………………….                                  Signature: ………………………….")
    r_ss.font.name = 'Times New Roman'
    r_ss.font.size = Pt(11)

    p_hod = doc.add_paragraph()
    p_hod.paragraph_format.space_before = Pt(10)
    p_hod.paragraph_format.space_after = Pt(6)
    r_hod = p_hod.add_run("Head of the Department: Ms. Bhagya Thilakarathne")
    r_hod.font.name = 'Times New Roman'
    r_hod.font.size = Pt(11)
    r_hod.font.bold = True

    p_hod_sig = doc.add_paragraph()
    p_hod_sig.paragraph_format.space_before = Pt(10)
    p_hod_sig.paragraph_format.space_after = Pt(24)
    r_hs = p_hod_sig.add_run("Date: …………………….                                  Signature: ………………………….")
    r_hs.font.name = 'Times New Roman'
    r_hs.font.size = Pt(11)

    p_stamp = doc.add_paragraph()
    p_stamp.paragraph_format.space_before = Pt(12)
    p_stamp.paragraph_format.space_after = Pt(0)
    r_st = p_stamp.add_run("Department Stamp:")
    r_st.font.name = 'Times New Roman'
    r_st.font.size = Pt(11)
    r_st.font.bold = True

    doc.add_page_break()'''

    # Replace old cover section
    start_cover_target = '    # -------------------------------------------------------------\n    # SECTION 1: COVER / TITLE PAGE\n    # -------------------------------------------------------------\n    sec1 = doc.sections[0]'
    end_cover_target = '    # 1. DECLARATION\n    add_h1("DECLARATION")'

    if start_cover_target in code:
        cover_end_idx = code.find('    # 1. DECLARATION\n    add_h1("DECLARATION")')
        if cover_end_idx != -1:
            # Find where declaration ends
            decl_end_idx = code.find('    # 2. ABSTRACT\n    add_h1("ABSTRACT")', cover_end_idx)
            if decl_end_idx != -1:
                code = code[:code.find(start_cover_target)] + new_cover + "\n\n" + code[decl_end_idx:]
                print("Successfully updated Cover Page and Declaration to match exact SIBA Template!")
            else:
                print("Warning: Abstract marker not found")
        else:
            print("Warning: Declaration marker not found")
    else:
        print("Warning: Cover target not found")

    out_file = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\scripts\generate_final_thesis_docx.py"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"Master script updated at: {out_file}")

if __name__ == "__main__":
    create_full_builder()
