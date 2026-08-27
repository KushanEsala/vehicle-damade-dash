import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_section_pagination(section, fmt="decimal", start=None):
    sectPr = section._sectPr
    for child in list(sectPr):
        if child.tag.endswith('pgNumType'):
            sectPr.remove(child)
    w_ns = nsdecls('w')
    if start is not None:
        xml_str = f'<w:pgNumType {w_ns} w:fmt="{fmt}" w:start="{start}"/>'
    else:
        xml_str = f'<w:pgNumType {w_ns} w:fmt="{fmt}"/>'
    pgNumType = parse_xml(xml_str)
    sectPr.append(pgNumType)

def add_field_code(paragraph, field_text):
    w_ns = nsdecls('w')
    xml_str = (
        f'<w:r {w_ns}><w:fldChar w:fldCharType="begin"/></w:r>'
        f'<w:r {w_ns}><w:instrText xml:space="preserve"> {field_text} </w:instrText></w:r>'
        f'<w:r {w_ns}><w:fldChar w:fldCharType="separate"/></w:r>'
        f'<w:r {w_ns}><w:fldChar w:fldCharType="end"/></w:r>'
    )
    r_elems = parse_xml(f'<w:wrapper {w_ns}>{xml_str}</w:wrapper>')
    for child in list(r_elems):
        paragraph._p.append(child)

def add_footer_page_number(paragraph):
    add_field_code(paragraph, "PAGE")

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    for child in list(tcPr):
        if child.tag.endswith('shd'):
            tcPr.remove(child)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_content(cell, text, bold=False, font_size=9.5, align=WD_ALIGN_PARAGRAPH.LEFT, line_spacing=1.15, space_after=2):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(font_size)
    run.font.bold = bold
    return run

def add_figure_caption(doc, caption_text):
    p = doc.add_paragraph(style='Caption')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(12)
    
    r1 = p.add_run("Figure ")
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(10)
    r1.font.italic = True

    add_field_code(p, "SEQ Figure \\* ARABIC")

    r2 = p.add_run(f": {caption_text}")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(10)
    r2.font.italic = True

def add_table_caption(doc, caption_text):
    p = doc.add_paragraph(style='Caption')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    
    r1 = p.add_run("Table ")
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(10)
    r1.font.italic = True

    add_field_code(p, "SEQ Table \\* ARABIC")

    r2 = p.add_run(f": {caption_text}")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(10)
    r2.font.italic = True

def add_picture_with_caption(doc, img_path, caption_text, width_inches=5.4):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(3)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(width_inches))

        add_figure_caption(doc, caption_text)
    else:
        print(f"Warning: Image file not found at {img_path}")

def build_siba_thesis():
    out_dir = r"d:\FinalProject 2026\vehicle_damade_dash_cloned"
    out_file = os.path.join(out_dir, "Vehicle_Damage_Assessment_Final_Thesis_2026.docx")
    out_file_latest = os.path.join(out_dir, "Vehicle_Damage_Assessment_Final_Thesis_2026_Latest.docx")
    out_file_backup = os.path.join(out_dir, "Vehicle_Damage_Assessment_Final_Report_Repaired_Dynamic.docx")

    doc = Document()

    # Image Paths
    uml_dir = os.path.join(out_dir, "reports", "uml_diagrams")
    ui_dir = os.path.join(out_dir, "reports", "ui_screenshots")
    plots_dir = os.path.join(out_dir, "Runscomplete", "runs", "vehicle_damage_seg-2")
    logo_path = os.path.join(out_dir, "reports", "siba_logo.png")

    img_use_case = os.path.join(uml_dir, "use_case_diagram.png")
    img_class = os.path.join(uml_dir, "class_diagram.png")
    img_activity = os.path.join(uml_dir, "activity_diagram.png")
    img_er = os.path.join(uml_dir, "er_diagram.png")
    img_seq = os.path.join(uml_dir, "sequence_diagram.png")
    img_deploy = os.path.join(uml_dir, "deployment_diagram.png")
    img_arch = os.path.join(uml_dir, "architectural_design.png")

    img_labels = os.path.join(plots_dir, "labels.jpg")
    img_results = os.path.join(plots_dir, "results.png")
    img_pr = os.path.join(plots_dir, "MaskPR_curve.png")
    img_f1 = os.path.join(plots_dir, "MaskF1_curve.png")
    img_p = os.path.join(plots_dir, "MaskP_curve.png")
    img_r = os.path.join(plots_dir, "MaskR_curve.png")
    img_cm = os.path.join(plots_dir, "confusion_matrix.png")
    img_cmn = os.path.join(plots_dir, "confusion_matrix_normalized.png")

    # Base Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)

    h1_style = doc.styles['Heading 1']
    h1_style.font.name = 'Times New Roman'
    h1_style.font.size = Pt(16)
    h1_style.font.bold = True
    h1_style.font.color.rgb = RGBColor(0, 0, 0)

    h2_style = doc.styles['Heading 2']
    h2_style.font.name = 'Times New Roman'
    h2_style.font.size = Pt(14)
    h2_style.font.bold = True
    h2_style.font.color.rgb = RGBColor(0, 0, 0)

    h3_style = doc.styles['Heading 3']
    h3_style.font.name = 'Times New Roman'
    h3_style.font.size = Pt(12)
    h3_style.font.bold = True
    h3_style.font.color.rgb = RGBColor(0, 0, 0)

    caption_style = doc.styles['Caption']
    caption_style.font.name = 'Times New Roman'
    caption_style.font.size = Pt(10)
    caption_style.font.italic = True
    caption_style.font.color.rgb = RGBColor(0, 0, 0)

    # Helper functions
    def add_p(text, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6, line_spacing=1.5):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.line_spacing = line_spacing
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.bold = bold
        run.font.italic = italic
        return p

    def add_h1(text, align=WD_ALIGN_PARAGRAPH.CENTER):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)
        run.font.bold = True
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.bold = True
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.bold = True
        return p

    def add_section_paragraphs(para_list):
        for text in para_list:
            add_p(text)

    # =========================================================================
    # SECTION 1: COVER / TITLE PAGE (Template Page 1 - No Page Number)
    # =========================================================================
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
    p_title.paragraph_format.space_before = Pt(24)
    p_title.paragraph_format.space_after = Pt(24)
    r = p_title.add_run("VEHICLE DAMAGE DETECTION USING DEEP LEARNING INSTANCE SEGMENTATION FOR AUTOMATED INSURANCE ERP ASSESSMENT")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(18)
    p_sub.paragraph_format.space_after = Pt(18)
    r = p_sub.add_run("A PROJECT THESIS SUBMITTED BY")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

    p_author = doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_author.paragraph_format.space_before = Pt(16)
    p_author.paragraph_format.space_after = Pt(6)
    r = p_author.add_run("W.M.M.G. SENAVIRATHNE\n(BSC/WD/22/36/01)")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True

    p_to = doc.add_paragraph()
    p_to.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_to.paragraph_format.space_before = Pt(18)
    p_to.paragraph_format.space_after = Pt(6)
    r = p_to.add_run("to the\nDEPARTMENT OF INFORMATION TECHNOLOGY")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_deg.paragraph_format.space_before = Pt(18)
    p_deg.paragraph_format.space_after = Pt(6)
    r_deg_it = p_deg.add_run("in partial fulfilment of the requirement for the award of the degree of\n")
    r_deg_it.font.name = 'Times New Roman'
    r_deg_it.font.size = Pt(12)
    r_deg_it.font.italic = True
    r_deg_name = p_deg.add_run("BSc. in Information Technology")
    r_deg_name.font.name = 'Times New Roman'
    r_deg_name.font.size = Pt(13)
    r_deg_name.font.bold = True

    p_of = doc.add_paragraph()
    p_of.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_of.paragraph_format.space_before = Pt(12)
    p_of.paragraph_format.space_after = Pt(10)
    r = p_of.add_run("of the")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)

    # SIBA Campus Logo
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
    r = p_inst.add_run("SRI LANKA INTERNATIONAL BUDDHIST ACADEMY\nPALLEKELE SRI LANKA\n2026")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

    # =========================================================================
    # SECTION 2: PRELIMINARY PAGES (Template Pages 2 to 11 - Roman i, ii, iii...)
    # =========================================================================
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

    # 1. DECLARATION (Template Page 2)
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
    r_cs = p_cand_sig.add_run("Date: ………………………………………                     …………………………………………\n                                                                           Signature of the Candidate")
    r_cs.font.name = 'Times New Roman'
    r_cs.font.size = Pt(11)

    p_cert = doc.add_paragraph()
    p_cert.paragraph_format.space_before = Pt(14)
    p_cert.paragraph_format.space_after = Pt(6)
    r_cert = p_cert.add_run("Certified by:\nSupervisor: Ms. Bhagya Thilakarathne")
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

    doc.add_page_break()

    # 2. ABSTRACT (Template Page 3)
    add_h1("ABSTRACT")
    add_section_paragraphs([
        "Manual motor vehicle damage inspection in traditional insurance claims management has long presented operational challenges, including subjective damage severity assessments, prolonged claim settlement turnaround times, paper-intensive record keeping, and vulnerability to inconsistent financial repair costing. To resolve these operational challenges, this research designed, implemented, and empirically evaluated an enterprise-grade, web-based vehicle damage inspection and claims enterprise resource planning (ERP) platform named Apex Vehicle Assurance.",
        "An Agile engineering approach was adopted, decoupling the system architecture across four distinct operational layers: an interactive single-page presentation tier built on Next.js 14, React 18, and Tailwind CSS; an asynchronous RESTful backend API service engineered in Python FastAPI; a dual-model deep learning computer vision pipeline executing YOLOv8 nano instance segmentation combined with COCO vehicle spatial gating; and a transactional data persistence tier structured across 15 normalized MySQL 8.0 relational tables.",
        "The computer vision inspection pipeline was trained on a curated real-world dataset comprising 13,945 automotive inspection photographs across seven damage categories: scratch, dent, tear, missing part, broken lamp, puncture, and broken glass. Training was conducted over 50 epochs utilizing a multi-stage hardware acceleration workflow. Empirical model evaluation at Epoch 44 achieved a mask Mean Average Precision (mAP50) of 41.20% and bounding box precision of 55.91%, with inference latency under 35 milliseconds on GPU hardware and end-to-end claim analysis completing within 107 milliseconds.",
        "The primary contribution of this work lies in the seamless architectural integration of real-time deep learning polygonal damage segmentation with automated, human-in-the-loop repair costing, statutory 15% Sri Lankan VAT financial computation, role-based access governance, and dynamic PDF appraisal generation. The system successfully demonstrates that integrating single-stage instance segmentation with enterprise insurance workflows eliminates subjective human bias, accelerates claims processing, and establishes an immutable, auditable foundation for modern motor insurance underwriting."
    ])

    doc.add_page_break()

    # 3. ACKNOWLEDGEMENT (Template Page 4)
    add_h1("ACKNOWLEDGEMENT")
    add_section_paragraphs([
        "First and foremost, I wish to express my deepest gratitude and sincere appreciation to my research supervisor, Ms. Bhagya Thilakarathne, Head of the Department of Information Technology and Senior Lecturer in IT at Sri Lanka International Buddhist Academy (SIBA Campus), for her invaluable guidance, intellectual mentorship, and continuous encouragement throughout every phase of this project. Her constructive critiques and insightful advice regarding system modeling, deep learning architectures, and academic writing significantly shaped the quality and rigor of this thesis.",
        "I extend my heartfelt thanks to the academic, technical, and administrative staff of the Department of Information Technology at SIBA Campus for providing the computational laboratory infrastructure, software resources, and an enriching academic environment that enabled the successful completion of this degree.",
        "I am also deeply grateful to the automotive insurance professionals and claims assessors who provided practical domain insights into motor claims appraisal, repair labor cataloging, and statutory underwriting requirements during the initial requirement elicitation phase of this study.",
        "Finally, I express my profound gratitude to my family and friends for their enduring patience, moral support, and unwavering confidence in my abilities during long hours of research, model training, and software development."
    ])

    doc.add_page_break()

    # 4. TABLE OF CONTENTS (Template Pages 5 to 8)
    add_h1("TABLE OF CONTENTS")
    p_toc_inst = doc.add_paragraph()
    p_toc_inst.paragraph_format.space_before = Pt(4)
    p_toc_inst.paragraph_format.space_after = Pt(12)
    add_field_code(p_toc_inst, 'TOC \\o "1-3" \\h \\z \\u')

    # Add clean formatted Table of Contents lines matching template
    toc_entries = [
        ("DECLARATION", "i", False),
        ("ABSTRACT", "ii", False),
        ("ACKNOWLEDGEMENT", "iii", False),
        ("LIST OF FIGURES", "viii", False),
        ("LIST OF TABLES", "ix", False),
        ("LIST OF ABBREVIATIONS", "x", False),
        ("CHAPTER 1: INTRODUCTION", "1", True),
        ("  1.1 Background", "1", False),
        ("  1.2 Problem Statement", "2", False),
        ("  1.3 Aim and Objectives", "3", False),
        ("    1.3.1 Main Objective", "3", False),
        ("    1.3.2 Specific Objectives", "3", False),
        ("  1.4 Research Questions", "4", False),
        ("  1.5 Scope", "4", False),
        ("  1.6 Significance", "5", False),
        ("  1.7 Limitations", "5", False),
        ("  1.8 Organization of the Report", "6", False),
        ("CHAPTER 2: LITERATURE REVIEW", "7", True),
        ("  2.1 Introduction", "7", False),
        ("  2.2 Theoretical / Conceptual Background", "8", False),
        ("  2.3 Domain and Technology Background", "10", False),
        ("  2.4 Existing Systems / Related Work", "12", False),
        ("  2.5 Comparison of Existing Systems", "14", False),
        ("  2.6 Research / Technology Gap", "16", False),
        ("  2.7 Proposed Contribution", "17", False),
        ("  2.8 Chapter Summary", "18", False),
        ("CHAPTER 3: METHODOLOGY AND REQUIREMENTS", "19", True),
        ("  3.1 Introduction", "19", False),
        ("  3.2 Research / Development Methodology", "19", False),
        ("  3.3 Project Development Process", "21", False),
        ("  3.4 Requirement Elicitation", "22", False),
        ("  3.5 Functional Requirements", "23", False),
        ("  3.6 Non-Functional Requirements", "25", False),
        ("  3.7 User Requirements", "26", False),
        ("  3.8 Hardware Requirements", "27", False),
        ("  3.9 Software Requirements", "28", False),
        ("  3.10 Feasibility Analysis", "29", False),
        ("  3.11 System Modelling", "30", False),
        ("  3.12 Technologies Used", "31", False),
        ("  3.13 Chapter Summary", "32", False),
        ("  3.14 Requirement Traceability", "33", False),
        ("CHAPTER 4: SYSTEM DESIGN AND IMPLEMENTATION", "35", True),
        ("  4.1 Introduction", "35", False),
        ("  4.2 System Architecture", "35", False),
        ("  4.3 System Components", "37", False),
        ("  4.4 Database Design", "39", False),
        ("  4.5 User Interface Design and Implemented System Evidence", "42", False),
        ("    4.5.1 Authentication and Role-Based Access Control Interfaces", "43", False),
        ("    4.5.2 Executive Dashboard and Underwriting Fleet Management", "45", False),
        ("    4.5.3 AI-Powered Damage Inspection and Interactive Visualizer", "48", False),
        ("    4.5.4 Assessment Review, Line-Item Costing, and Claim Finalization", "51", False),
        ("    4.5.5 Generated PDF Assessment Reports and Customer Self-Service Portal", "54", False),
        ("  4.6 Module Design and UML Behavioral Models", "57", False),
        ("  4.7 Algorithms / Models", "60", False),
        ("  4.8 Implementation Details and Core Code Snippets", "62", False),
        ("  4.9 Security Implementation", "64", False),
        ("  4.10 Integration and Deployment", "65", False),
        ("  4.11 Chapter Summary", "66", False),
        ("CHAPTER 5: TESTING, RESULTS AND DISCUSSION", "67", True),
        ("  5.1 Introduction", "67", False),
        ("  5.2 Testing Strategy", "67", False),
        ("  5.3 Unit Testing", "68", False),
        ("  5.4 Integration Testing", "69", False),
        ("  5.5 System Testing", "69", False),
        ("  5.6 User Acceptance Testing", "70", False),
        ("  5.7 Functional Test Results", "70", False),
        ("  5.8 Non-Functional Test Results", "72", False),
        ("  5.9 Performance / Model Evaluation", "73", False),
        ("  5.10 Comparison with Existing Systems", "76", False),
        ("  5.11 Discussion", "77", False),
        ("  5.12 Limitations", "78", False),
        ("  5.13 Chapter Summary", "79", False),
        ("CHAPTER 6: CONCLUSION AND FUTURE WORK", "80", True),
        ("  6.1 Introduction", "80", False),
        ("  6.2 Summary of the Project", "80", False),
        ("  6.3 Achievement of Objectives", "81", False),
        ("  6.4 Key Findings", "82", False),
        ("  6.5 Contributions", "83", False),
        ("  6.6 Limitations", "83", False),
        ("  6.7 Future Work", "84", False),
        ("  6.8 Conclusion", "84", False),
        ("REFERENCES", "85", True),
        ("APPENDIX A – Detailed Database DDL & Schema Definitions", "88", True),
        ("APPENDIX B – Complete REST API Endpoint Specification Matrix", "90", True),
        ("APPENDIX C – Deployment & Troubleshooting Procedures", "91", True),
        ("APPENDIX D – Complete Functional & Non-Functional Test Case Suite", "92", True),
        ("APPENDIX E – Supervisor Quality Checklist Compliance", "93", True),
    ]

    t_toc = doc.add_table(rows=len(toc_entries), cols=2)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_toc.autofit = False
    for r_i, (entry_title, page_str, is_bold) in enumerate(toc_entries):
        c0 = t_toc.rows[r_i].cells[0]
        c1 = t_toc.rows[r_i].cells[1]
        c0.width = Inches(5.2)
        c1.width = Inches(0.8)
        set_cell_content(c0, entry_title, bold=is_bold, font_size=9.5, space_after=1)
        set_cell_content(c1, page_str, bold=is_bold, font_size=9.5, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=1)

    doc.add_page_break()

    # 5. LIST OF FIGURES (Template Page 9)
    add_h1("LIST OF FIGURES")
    p_lof = doc.add_paragraph()
    p_lof.paragraph_format.space_before = Pt(4)
    p_lof.paragraph_format.space_after = Pt(12)
    add_field_code(p_lof, 'TOC \\h \\z \\c "Figure"')

    # 6. LIST OF TABLES (Template Page 10)
    add_h1("LIST OF TABLES")
    p_lot = doc.add_paragraph()
    p_lot.paragraph_format.space_before = Pt(4)
    p_lot.paragraph_format.space_after = Pt(12)
    add_field_code(p_lot, 'TOC \\h \\z \\c "Table"')

    doc.add_page_break()

    # 7. LIST OF ABBREVIATIONS (Template Page 11)
    add_h1("LIST OF ABBREVIATIONS")
    
    abbreviations_list = [
        ("AI", "Artificial Intelligence"),
        ("API", "Application Programming Interface"),
        ("ARGON2", "Argon2 Password Hashing Algorithm (Argon2id Memory-Hard)"),
        ("ASGI", "Asynchronous Server Gateway Interface"),
        ("BCE", "Binary Cross-Entropy Loss"),
        ("CIoU", "Complete Intersection over Union Loss"),
        ("CNN", "Convolutional Neural Network"),
        ("COCO", "Common Objects in Context Dataset / Standard Object Detection Benchmark"),
        ("CPU", "Central Processing Unit"),
        ("CSP", "Cross-Stage Partial Network Architecture"),
        ("CUDA", "Compute Unified Device Architecture (NVIDIA Parallel Computing)"),
        ("DDL", "Data Definition Language"),
        ("DFL", "Distribution Focal Loss"),
        ("EERD", "Enhanced Entity-Relationship Diagram (Database Modeling Standard)"),
        ("ER / ERD", "Entity-Relationship / Entity-Relationship Diagram"),
        ("ERP", "Enterprise Resource Planning"),
        ("FNOL", "First Notice of Loss"),
        ("FR", "Functional Requirement"),
        ("GPU", "Graphics Processing Unit"),
        ("GUI", "Graphical User Interface"),
        ("HSV", "Hue, Saturation, Value Color Space"),
        ("HTTP / HTTPS", "Hypertext Transfer Protocol / Hypertext Transfer Protocol Secure"),
        ("IEEE", "Institute of Electrical and Electronics Engineers"),
        ("IoU", "Intersection over Union"),
        ("JSON", "JavaScript Object Notation"),
        ("JWT", "JSON Web Token"),
        ("mAP", "Mean Average Precision"),
        ("NFR", "Non-Functional Requirement"),
        ("NIC", "National Identity Card"),
        ("NMS", "Non-Maximum Suppression"),
        ("ORM", "Object-Relational Mapping"),
        ("PAN", "Path Aggregation Network"),
        ("PDF", "Portable Document Format"),
        ("PR", "Precision-Recall"),
        ("RBAC", "Role-Based Access Control"),
        ("REST", "Representational State Transfer"),
        ("SDLC", "Software Development Life Cycle"),
        ("SGD", "Stochastic Gradient Descent"),
        ("SQL", "Structured Query Language"),
        ("UAT", "User Acceptance Testing"),
        ("UML", "Unified Modeling Language (UML 2.5.1 Specification)"),
        ("VAT", "Value Added Tax (Statutory 15% Sri Lanka Rate)"),
        ("WCAG", "Web Content Accessibility Guidelines (WCAG 2.1 AA)"),
        ("YOLO", "You Only Look Once (Real-Time Object Detection & Segmentation)"),
    ]

    t_abbr = doc.add_table(rows=len(abbreviations_list), cols=2)
    t_abbr.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_abbr.autofit = False
    for r_i, (abbr, full_text) in enumerate(abbreviations_list):
        c0 = t_abbr.rows[r_i].cells[0]
        c1 = t_abbr.rows[r_i].cells[1]
        c0.width = Inches(1.8)
        c1.width = Inches(4.2)
        set_cell_content(c0, abbr, bold=True, font_size=10, space_after=2)
        set_cell_content(c1, full_text, bold=False, font_size=10, space_after=2)

    doc.add_page_break()

    # =========================================================================
    # SECTION 3: MAIN BODY CHAPTERS (Template Pages 12+ - Arabic 1, 2, 3...)
    # =========================================================================
    sec3 = doc.add_section()
    sec3.page_width = Mm(210)
    sec3.page_height = Mm(297)
    sec3.top_margin = Inches(1.0)
    sec3.bottom_margin = Inches(1.0)
    sec3.left_margin = Inches(1.5)
    sec3.right_margin = Inches(1.0)
    set_section_pagination(sec3, fmt="decimal", start=1)

    p_f3 = sec3.footer.paragraphs[0]
    p_f3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_footer_page_number(p_f3)

    # -------------------------------------------------------------
    # CHAPTER 1: INTRODUCTION (Template Pages 12-13)
    # -------------------------------------------------------------
    add_h1("CHAPTER 1: INTRODUCTION")

    add_h2("1.1 Background")
    add_section_paragraphs([
        "With the rapid advancement of artificial intelligence, deep learning, and computer vision technologies, automated visual inspection systems have emerged as transformative engineering tools across modern industrial, automotive, and enterprise sectors. In the motor vehicle insurance domain, damage assessment represents the foundational operational workflow governing policy validation, claim liability determination, repair cost estimation, and final financial settlement. Traditionally, when an accident occurs, the First Notice of Loss (FNOL) initiates a series of manual inspection steps requiring field claim assessors or certified garage engineers to physically travel to accident scenes or repair centers, take non-standardized digital photos, record damage severity on paper clipboards, and manually transcribe observations into legacy branch desktop applications.",
        "This traditional, paper-heavy assessment lifecycle introduces substantial operational friction, administrative overheads, and financial leakage into motor insurance workflows. Physical claim processing cycles typically span anywhere between three to seven business days per claim, resulting in claim backlogs, delayed payouts, and customer dissatisfaction. Moreover, inspection photos are often stored across unindexed local network drives or physical paper folders, complicating historical auditing and cross-claim fraud detection. Manual inspections are also inherently subjective; different human assessors frequently assign disparate repair costs and severity classifications to identical body panel defects, introducing financial unpredictability and underwriting disputes.",
        "Deep learning instance segmentation provides an automated, objective, and high-speed alternative for motor vehicle damage analysis. By applying single-stage convolutional neural networks to digital inspection images, automated systems can simultaneously detect the spatial location of damaged regions, classify the specific defect type (such as scratches, dents, tears, punctures, broken lamps, or broken glass), and generate pixel-precise polygonal segmentation masks outlining the exact boundary of each defect. When tightly coupled with an Enterprise Resource Planning (ERP) platform, visual AI predictions seamlessly feed into automated financial costing engines, role-based approval workflows, and immutable security audit logs, providing insurance enterprises with a modern, transparent, and auditable digital claims management infrastructure."
    ])

    add_h2("1.2 Problem Statement")
    add_section_paragraphs([
        "Conventional automotive insurance claim workflows face critical operational bottlenecks: subjective manual inspections, prolonged turnaround times, fragmented record-keeping, and the lack of automated visual verification to ensure uploaded photos genuinely contain damaged vehicles rather than non-automotive backgrounds. Field assessments remain highly susceptible to human subjectivity, as different estimators assign varying repair costs and severity classifications to identical body panel damages.",
        "Furthermore, existing claim management systems operate in disconnected data silos, separating inspection imagery from insurance policy records, customer profiles, and regional garage repair pricing catalogs. This fragmentation creates administrative overheads and prevents automated end-to-end claim reconciliation. An integrated, role-based software platform combining real-time computer vision instance segmentation with enterprise resource management is urgently required to resolve these systemic inefficiencies."
    ])

    add_h2("1.3 Aim and Objectives")
    add_h3("1.3.1 Main Objective")
    add_section_paragraphs([
        "The primary aim of this research project is to design, develop, and evaluate an automated, role-based motor vehicle damage assessment and insurance Enterprise Resource Planning (ERP) platform that integrates deep learning polygonal instance segmentation with automated financial costing, spatial validation gating, and dynamic PDF claim report generation."
    ])

    add_h3("1.3.2 Specific Objectives")
    add_section_paragraphs([
        "To accomplish the main aim, five specific, measurable engineering objectives were established:",
        "• OBJ-01: Train and optimize a deep learning instance segmentation model (YOLOv8 nano) on a curated dataset of 13,945 automotive inspection images to accurately classify and segment seven distinct vehicle damage categories (scratch, dent, tear, missing part, broken lamp, puncture, and broken glass).",
        "• OBJ-02: Develop and validate a spatial overlap gating algorithm combining a pre-trained COCO vehicle detector with a 20% Intersection over Union (IoU) boundary rule to automatically suppress background false alarms and confirm vehicle presence.",
        "• OBJ-03: Design and implement a decoupled 4-layer enterprise software architecture featuring a Next.js 14 presentation frontend, a Python FastAPI RESTful backend service, and a 15-table MySQL 8.0 relational database normalized to Third Normal Form (3NF).",
        "• OBJ-04: Implement an automated financial repair costing engine incorporating regional unit price catalogs, statutory 15% Sri Lankan Value Added Tax (VAT) computations, policy deductible deductions, and automated PDF claim appraisal certificate compilation via ReportLab.",
        "• OBJ-05: Enforce comprehensive role-based access control (RBAC), Argon2id cryptographic password hashing, HttpOnly session cookie governance, and immutable database audit logging across System Administrator, Claims Assessor, and Policyholder Customer personas."
    ])

    add_h2("1.4 Research Questions")
    add_section_paragraphs([
        "This research addresses four central engineering research questions:",
        "• RQ1: How accurately can single-stage deep learning instance segmentation models classify and delineate fine-grained automotive surface defects across diverse lighting and environmental conditions?",
        "• RQ2: How effectively does spatial intersection gating between a generic vehicle detector and a defect segmenter filter out non-automotive background noise in inspection photographs?",
        "• RQ3: What architectural decoupling strategies best ensure sub-second API response latency, transactional data integrity, and strict referential consistency in an insurance ERP platform?",
        "• RQ4: How does integrating automated visual AI appraisals with human-in-the-loop line-item costing affect operational efficiency and turnaround time in enterprise motor claims workflows?"
    ])

    add_h2("1.5 Scope")
    add_section_paragraphs([
        "The project scope encompasses the design, implementation, and empirical evaluation of the full-stack Apex Vehicle Assurance ERP platform. The system supports three user roles: System Administrators, Claims Operations Officers, and Insured Policyholders. The computer vision subsystem is specialized for seven exterior motor vehicle damage categories (scratch, dent, tear, missing part, broken lamp, puncture, broken glass) captured in standard 2D RGB photographs under diverse lighting conditions. The backend architecture provides end-to-end relational data management across 15 normalized tables, automated 15% VAT and deductible financial calculations, and dynamic PDF claim report generation. Internal structural chassis deformities requiring laser frame measuring benches, engine mechanical failures, and real-time video stream processing remain outside the immediate prototype scope."
    ])

    add_h2("1.6 Significance")
    add_section_paragraphs([
        "This project provides substantial practical, economic, and technological contributions to the motor insurance industry. By automating visual damage detection and line-item repair costing, insurance enterprises can reduce average claim turnaround times from several business days to under two minutes, drastically cutting operational administrative overheads. Standardized damage catalogs and automated 15% VAT calculations eliminate subjective human estimation discrepancies, fostering trust and transparency between insurers, garages, and policyholders. Furthermore, the 4-layer decoupled architecture demonstrates a reproducible, production-ready blueprint for deploying advanced deep learning computer vision within mission-critical enterprise software environments."
    ])

    add_h2("1.7 Limitations")
    add_section_paragraphs([
        "The system operates with specific technical and environmental constraints. The deep learning segmentation model is optimized for high-resolution 2D RGB photographic imagery and does not infer hidden internal structural or mechanical engine damage. Extreme image blur, heavy nighttime shadowing, or severely obstructed vehicle panels can impact boundary segmentation accuracy, which is mitigated through the built-in human-in-the-loop assessor review interface. The unit pricing catalog is pre-configured for standard Sri Lankan market repair rates and requires periodic administrative updates to reflect changing material and labor costs."
    ])

    add_h2("1.8 Organization of the Report")
    add_section_paragraphs([
        "The remainder of this thesis is organized into five subsequent chapters:",
        "• Chapter 2 (Literature Review): Synthesizes theoretical foundations of computer vision defect detection, evaluates deep learning instance segmentation architectures, reviews existing enterprise claim management solutions, and defines the research gap.",
        "• Chapter 3 (Methodology and Requirements): Details the Agile development lifecycle, requirement elicitation techniques, functional and non-functional specifications, hardware/software constraints, feasibility analysis, and requirement traceability.",
        "• Chapter 4 (System Design and Implementation): Presents the 4-layer decoupled architecture, UML 2.5.1 behavioral models, 15-table MySQL database schema, UI design principles, 16 implemented interface screenshots with in-depth operational explanations, AI model training workflow, and core implementation code snippets.",
        "• Chapter 5 (Testing, Results and Discussion): Documents unit, integration, system, and user acceptance testing (UAT), evaluates YOLOv8 model training curves and confusion matrices, benchmarks latency and throughput, and provides a critical comparative discussion.",
        "• Chapter 6 (Conclusion and Future Work): Evaluates the achievement of all five project objectives against measurable criteria, summarizes key findings, articulates academic and industrial contributions, outlines project limitations, and identifies future research trajectories."
    ])

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 2: LITERATURE REVIEW (Template Pages 14-15)
    # -------------------------------------------------------------
    add_h1("CHAPTER 2: LITERATURE REVIEW")

    add_h2("2.1 Introduction")
    add_section_paragraphs([
        "Automated vehicle inspection, surface defect localization, and insurance claim automation have attracted significant research interest across computer vision, machine learning, and enterprise software engineering. In the automotive insurance sector, traditional claim assessment has long been constrained by manual, paper-based workflows that are labor-intensive, slow, and susceptible to human subjectivity. This literature review critically examines the evolution of computer vision defect detection, analyzes deep learning instance segmentation architectures, evaluates enterprise resource planning (ERP) integration models, conducts a comparative synthesis of existing solutions, and articulates the specific technological gaps addressed by this research."
    ])

    add_h2("2.2 Theoretical / Conceptual Background")
    add_section_paragraphs([
        "Computer vision defect detection has progressed through three fundamental technical paradigms over the past two decades [1]:",
        "1. Classical Handcrafted Feature Engineering: Early inspection systems relied on edge detection operators (Sobel, Canny, Prewitt), morphological operations, and texture descriptors (Haar-like wavelets, Histogram of Oriented Gradients [HOG], Local Binary Patterns [LBP]) coupled with shallow classifiers such as Support Vector Machines (SVM). These methods performed adequately under rigidly controlled laboratory lighting but failed in unconstrained real-world automotive environments due to specular vehicle paint reflections, complex background clutter, and varying camera viewing angles [2].",
        "2. Two-Stage Deep Learning Architectures (R-CNN, Fast R-CNN, Faster R-CNN, Mask R-CNN): The deep learning revolution introduced Region Proposal Networks (RPN) that generate candidate bounding boxes followed by RoIAlign pooling and multi-task convolutional heads. Mask R-CNN [3] established the gold standard for instance segmentation by adding a parallel Fully Convolutional Network (FCN) branch to predict pixel-precise binary masks. However, two-stage architectures require substantial computational resources, exhibiting high inference latency (150–400 ms per image) that hinders real-time interactive enterprise workflows.",
        "3. Single-Stage Deep Learning Architectures (SSD, YOLOv5, YOLOv7, YOLOv8): Single-stage architectures formulate detection and segmentation as a unified regression problem across spatial grid cells. Ultralytics YOLOv8 [4] incorporates an anchor-free Cross-Stage Partial Network with 2-FPN (C2f) backbone, Distribution Focal Loss (DFL), Complete IoU (CIoU) bounding box regression, and ProtoNet mask coefficient heads. This architecture achieves an optimal Pareto trade-off between mean Average Precision (mAP) and ultra-low latency (15–35 ms), making it ideal for scalable enterprise cloud and on-premise deployments."
    ])

    add_h2("2.3 Domain and Technology Background")
    add_section_paragraphs([
        "Modern insurance claims processing operates within strict legal, financial, and architectural constraints. In enterprise motor insurance, First Notice of Loss (FNOL) systems must securely authenticate multiple stakeholder personas: internal administrators, claims operations officers, and external policyholder customers. Modern enterprise software engineering mandates decoupled, microservice-aligned architectures where interactive Single-Page Application (SPA) frontends communicate with asynchronous backend API microservices through structured RESTful protocols [5].",
        "FastAPI leverages Python's asynchronous server gateway interface (ASGI) and Uvicorn workers to deliver high-concurrency request dispatching, Pydantic type validation, and automatic OpenAPI documentation. Relational databases adhering to Third Normal Form (3NF) remain essential for persistent policyholder and financial state management, ensuring transactional ACID guarantees during claim settlement [6]. Furthermore, ReportLab Platypus enables dynamic, server-side PDF document compilation, generating tamper-evident appraisal reports formatted to statutory corporate and tax specifications."
    ])

    add_h2("2.4 Existing Systems / Related Work")
    add_section_paragraphs([
        "Several academic and commercial initiatives have explored automated automotive damage analysis:",
        "• Commercial Platforms (Tractable AI, CCC ONE, Mitchell Cloud): Industry-leading proprietary platforms utilize proprietary deep neural networks to evaluate insurance claims. While highly effective, these solutions operate as closed commercial software-as-a-service (SaaS) ecosystems with expensive subscription models, lack open source customization, and do not provide integrated regional pricing schedules or statutory tax tailoring for emerging insurance markets [7].",
        "• Academic Research Implementations: Patil et al. [8] developed a convolutional neural network for classifying vehicle damage severity across whole images but lacked spatial defect localization and polygonal segmentation masks. Zhang et al. [9] applied Faster R-CNN for bounding box damage detection on vehicle body panels; however, rectangular bounding boxes fail to capture irregular scratch and dent shapes, leading to inaccurate repair surface area estimations. Kumar et al. [10] combined Mask R-CNN with basic repair cost lookup tables but did not implement spatial validation gating, resulting in high false positive rates when processing background clutter and non-automotive scene elements."
    ])

    add_h2("2.5 Comparison of Existing Systems")
    add_p("Table 2.1 presents a comparative evaluation of existing academic and commercial automotive damage assessment solutions against the proposed Apex Vehicle Assurance platform.")

    add_table_caption(doc, "Comparison of Existing Automotive Damage Assessment Systems")

    t_comp = doc.add_table(rows=6, cols=5)
    t_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_comp.autofit = False

    comp_headers = ["System / Research Study", "Core AI Architecture", "Spatial Delineation Type", "Vehicle Gating & Validation", "Enterprise ERP Integration"]
    comp_widths = [Inches(1.6), Inches(1.4), Inches(1.3), Inches(1.2), Inches(1.5)]
    for i, h in enumerate(comp_headers):
        cell = t_comp.rows[0].cells[i]
        cell.width = comp_widths[i]
        set_cell_content(cell, h, bold=True, font_size=9.5)
        set_cell_background(cell, "E0E0E0")

    comp_data = [
        ("Patil et al. (2020) [8]", "VGG-16 CNN Classifier", "Whole-Image Classification Only", "No (Accepts Any Image)", "None (Standalone Python Script)"),
        ("Zhang et al. (2021) [9]", "Faster R-CNN Detector", "Rectangular Bounding Boxes", "No Spatial Overlap Gate", "Basic SQLite Prototype"),
        ("Kumar et al. (2023) [10]", "Mask R-CNN Segmenter", "Polygonal Mask Segmentation", "No Vehicle Verification", "Manual Lookup Table"),
        ("Tractable AI (Commercial) [7]", "Proprietary Deep CNNs", "Bounding Box & Heatmaps", "Proprietary Visual Checks", "Closed Commercial SaaS Cloud"),
        ("Apex Assurance (Proposed)", "YOLOv8 Nano Instance Seg + COCO Gate", "Pixel-Precise Polygon Masks (7 Classes)", "Yes (20% IoU Vehicle Boundary Gate)", "Full Decoupled ERP (Next.js 14, FastAPI, 15 MySQL Tables)"),
    ]

    for r_idx, row_data in enumerate(comp_data):
        row_cells = t_comp.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].width = comp_widths[c_idx]
            is_prop = (r_idx == len(comp_data) - 1)
            set_cell_content(row_cells[c_idx], val, bold=is_prop, font_size=8.5)
            if is_prop:
                set_cell_background(row_cells[c_idx], "F0FDF4")

    add_h2("2.6 Research / Technology Gap")
    add_section_paragraphs([
        "A critical analysis of the literature reveals four distinct technological gaps:",
        "1. Absence of Spatial Vehicle Presence Gating: Existing academic models execute defect detection indiscriminately across all input imagery, producing false alarms on background textures (such as cracked walls, road asphalt, and foliage). An automated spatial verification rule is required to confirm that detected defects reside physically on valid vehicle panels.",
        "2. Disconnect Between Computer Vision and Enterprise Relational Schemas: Prior research primarily focuses on isolated neural network training metrics, neglecting relational integration with multi-role user governance, customer directories, vehicle registries, and immutable audit trails.",
        "3. Lack of Interactive Human-in-the-Loop Costing Workflows: Purely automated AI systems lack transparent appraisal adjustment mechanisms, preventing human assessors from reviewing, updating, or overriding individual line-item repair costs before final policy settlement.",
        "4. Absence of Dynamic Statutory Tax and Report Compilation: Existing platforms do not automate regional statutory tax calculations (e.g., Sri Lankan 15% VAT) or generate official, downloadable, tamper-evident PDF claim appraisal certificates within a unified workflow."
    ])

    add_h2("2.7 Proposed Contribution")
    add_section_paragraphs([
        "This project directly bridges these identified research gaps by engineering an integrated, production-grade automotive insurance ERP ecosystem that seamlessly couples YOLOv8 nano polygonal instance segmentation with a 20% IoU spatial gating validator, a 15-table MySQL 8.0 relational schema, an interactive Next.js 14 review workspace, automated 15% VAT financial costing, and dynamic ReportLab PDF claim certificate compilation."
    ])

    add_h2("2.8 Chapter Summary")
    add_section_paragraphs([
        "This chapter reviewed the evolution of computer vision defect localization, evaluated two-stage versus single-stage deep learning architectures, synthesized related academic and commercial systems, and established the research gap. The next chapter details the methodology, development process, and comprehensive functional and non-functional requirements."
    ])

    doc.add_page_break()

    # Save to file
    out_script = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\scripts\build_siba_template_thesis.py"
    print(f"Base generator template script written successfully.")

if __name__ == "__main__":
    build_siba_thesis()
