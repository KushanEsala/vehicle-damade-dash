import os
import re

def main():
    src_file = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\scripts\expand_to_exact_70page_thesis.py"
    with open(src_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Define the rich Section 4.5 with all 16 UI screenshots and in-depth academic explanations
    section_4_5_code = '''
    # =============================================================
    # 4.5 USER INTERFACE DESIGN & IMPLEMENTED SYSTEM EVIDENCE
    # =============================================================
    add_h2("4.5 User Interface Design and Implemented System Evidence")
    add_section_paragraphs([
        "To provide empirical verification of system implementation and demonstrate the full operational lifecycle of the "
        "Apex Vehicle Assurance ERP platform, this section presents the implemented graphical user interfaces (GUIs) across "
        "all three role-based user personas: System Administrator, Claims Operations Officer, and Insured Policyholder. "
        "The web application was developed using Next.js 14 (App Router) with React 18, TypeScript, and Tailwind CSS, "
        "providing a responsive, dark/light theme-adaptive user experience adhering strictly to WCAG 2.1 AA accessibility guidelines. "
        "The interfaces seamlessly integrate client-side interactive visual canvas overlays with asynchronous RESTful APIs "
        "powered by the FastAPI backend, PyTorch YOLOv8 instance segmentation engine, MySQL 8.0 relational database, and ReportLab PDF compiler."
    ])

    # 4.5.1 Authentication & RBAC Interfaces
    add_h3("4.5.1 Authentication and Role-Based Access Control Interfaces")
    add_section_paragraphs([
        "The access governance subsystem enforces strict identity verification, multi-tier role authorization, and audit logging. "
        "Figure 4.8 illustrates the secure split-pane sign-in interface, featuring an automotive brand panel on the left and an "
        "authenticated credentials form on the right. User passwords are verified against Argon2id memory-hard cryptographic hashes, "
        "and successful authentication generates cryptographically signed JWT access tokens stored within secure HttpOnly, SameSite "
        "browser cookies to mitigate Cross-Site Scripting (XSS) and Session Hijacking vectors."
    ])
    
    img_ui_signin = os.path.join(r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned\\reports\\ui_screenshots", "ui_01_signin_admin.png")
    if os.path.exists(img_ui_signin):
        add_picture_with_caption(doc, img_ui_signin, "System Authentication and Role-Based Portal Sign-In Interface")
    
    add_section_paragraphs([
        "Following successful sign-in, the Next.js middleware dynamically evaluates the decoded JWT role claim and routes the "
        "authenticated user to their authorized workspace. Figure 4.9 presents the User Management interface accessible exclusively "
        "to the System Administrator. This interface provides staff account creation (Operators and Administrators), automated "
        "portal account provisioning for newly onboarded customers, cryptographic temporary password generation with high entropy, "
        "and immediate account deactivation/deletion controls with full audit trail tracking in the MySQL audit_logs table."
    ])

    img_ui_usermgmt = os.path.join(r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned\\reports\\ui_screenshots", "ui_14_user_management.png")
    if os.path.exists(img_ui_usermgmt):
        add_picture_with_caption(doc, img_ui_usermgmt, "User Access Governance and Staff Account Management Interface")

    # 4.5.2 Executive Dashboard & Underwriting Asset Registry
    add_h3("4.5.2 Executive Dashboard and Underwriting Fleet Management")
    add_section_paragraphs([
        "Figure 4.10 depicts the Claims Overview Executive Dashboard. The dashboard renders five real-time Key Performance "
        "Indicator (KPI) summary cards querying MySQL aggregation endpoints: Total Registered Customers (11), Total Insured "
        "Vehicles (12), Total AI Analyses Conducted (6), Finalized Analyses Pending Settlement, and Cumulative Estimated Repair "
        "Costs in Sri Lankan Rupees (LKR). The work queue provides one-click navigation to pending vehicle inspections and claims."
    ])

    img_ui_dash = os.path.join(r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned\\reports\\ui_screenshots", "ui_02_dashboard_admin.png")
    if os.path.exists(img_ui_dash):
        add_picture_with_caption(doc, img_ui_dash, "Executive Claims Overview and Real-Time Operational KPI Dashboard")

    add_section_paragraphs([
        "Figure 4.11 and Figure 4.12 showcase the Policyholder Registration and Customer Directory subsystems. When onboarding a new "
        "policyholder, the system auto-generates a standardized customer code (e.g., CUS-2026-000015), validates National Identity Card "
        "(NIC) and passport formats, and provisions a linked portal login credential displayed via a dismissible security banner. "
        "The customer directory provides instant search, telephone/email contact verification, and active portal status indicators."
    ])

    img_ui_custreg = os.path.join(r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned\\reports\\ui_screenshots", "ui_03_customer_registration.png")
    if os.path.exists(img_ui_custreg):
        add_picture_with_caption(doc, img_ui_custreg, "Customer Registration and Automated Portal Provisioning Interface")

    img_ui_custlist = os.path.join(r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned\\reports\\ui_screenshots", "ui_04_customer_records_list.png")
    if os.path.exists(img_ui_custlist):
        add_picture_with_caption(doc, img_ui_custlist, "Registered Customer Records Directory and Portal Status Registry")

    add_section_paragraphs([
        "Figure 4.13 displays the Insured Vehicle Fleet Registration interface. Operators bind vehicles to registered policyholders "
        "via foreign key constraints, capturing vehicle registration numbers (e.g., CP-KD-9287, TST-121748, WP-CAB-1234), chassis numbers, "
        "make, model, manufacturing year, and fuel type. Figure 4.14 illustrates the Insurance Coverage Plans configuration panel, "
        "defining statutory underwriting tiers (Comprehensive Gold Auto Shield, Comprehensive Silver Shield, Platinum Premium Cover, "
        "and Third-Party Only) with coverage limits ranging up to LKR 10,000,000 and policy deductibles between LKR 5,000 and LKR 25,000."
    ])

    img_ui_vehreg = os.path.join(r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned\\reports\\ui_screenshots", "ui_05_vehicle_registration.png")
    if os.path.exists(img_ui_vehreg):
        add_picture_with_caption(doc, img_ui_vehreg, "Insured Vehicle Fleet Registration and Policy Binding Interface")

    img_ui_plans = os.path.join(r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned\\reports\\ui_screenshots", "ui_06_insurance_plans.png")
    if os.path.exists(img_ui_plans):
        add_picture_with_caption(doc, img_ui_plans, "Insurance Coverage Plans and Underwriting Schedule Configuration")

    # 4.5.3 AI-Powered Damage Inspection & Interactive Segmentation Visualizer
    add_h3("4.5.3 AI-Powered Damage Inspection and Interactive Visualizer")
    add_section_paragraphs([
        "Figure 4.15 illustrates the New Assessment inspection photo submission workspace. Claims officers select the target customer "
        "and registered vehicle from relational dropdowns, upload inspection imagery in JPG, PNG, or WEBP formats, and configure "
        "real-time dual confidence threshold sliders: Damage Finding Confidence (default 30%) and Vehicle Gating Confidence (default 25%). "
        "An operational checklist provides physical capture guidance (maintaining focus on damaged panels, including vehicle context, "
        "and avoiding severe cropping) to ensure optimal inference quality."
    ])

    img_ui_newassess = os.path.join(r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned\\reports\\ui_screenshots", "ui_07_new_assessment_upload.png")
    if os.path.exists(img_ui_newassess):
        add_picture_with_caption(doc, img_ui_newassess, "Damage Inspection Photo Upload and Confidence Parameter Configuration")

    add_section_paragraphs([
        "Figure 4.16 demonstrates the core AI visualizer canvas following inference execution. The dual-stage pipeline achieves "
        "spatial noise suppression and multi-class instance segmentation. First, the COCO vehicle detector identifies the vehicle body "
        "with a green bounding box (labeled 'car 83%'). Simultaneously, the fine-tuned YOLOv8 nano segmentation model extracts exact "
        "polygon boundaries for detected defects: a large 'Dent' mask covering the driver and passenger doors (confidence 39%), a "
        "'Broken Glass' mask over the front driver window (confidence 84%), and a second 'Broken Glass' mask over the rear quarter glass "
        "(confidence 56%). The top financial summary displays 3 accepted damage findings, an itemized subtotal of LKR 47,000, and a "
        "net estimate of LKR 54,050 including 15% statutory Value Added Tax (VAT)."
    ])

    img_ui_segcanvas = os.path.join(r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned\\reports\\ui_screenshots", "ui_08_damage_visualizer_canvas.png")
    if os.path.exists(img_ui_segcanvas):
        add_picture_with_caption(doc, img_ui_segcanvas, "Interactive AI Instance Segmentation Visualizer and Spatial Gating Canvas")

    # 4.5.4 Assessment Review, Line-Item Financial Costing & Reporting
    add_h3("4.5.4 Assessment Review, Line-Item Costing, and Claim Finalization")
    add_section_paragraphs([
        "Figure 4.17 presents the formal Assessment Review workspace header for Claim Reference VDA-20260819-000007. The header "
        "displays the linked vehicle badge (TST-121748 Honda Civic), system validation status ('Vehicle Confirmed', 'Analyzed'), "
        "and primary action buttons allowing the assessor to trigger automated re-analysis or finalize and issue the formal report."
    ])

    img_ui_reviewhdr = os.path.join(r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned\\reports\\ui_screenshots", "ui_09_assessment_review_header.png")
    if os.path.exists(img_ui_reviewhdr):
        add_picture_with_caption(doc, img_ui_reviewhdr, "Assessment Review Header and Vehicle Claim Finalization Actions")

    add_section_paragraphs([
        "Figure 4.18 demonstrates the human-in-the-loop Verified Findings and Damage Summary Editor. In accordance with insurance "
        "standard operating procedures, the human assessor retains full control to audit each AI-detected damage region. Assessors "
        "can modify the damage classification, adjust severity ratings (e.g., Moderate), enter custom panel descriptions, update "
        "itemized repair costs (Broken Glass: LKR 15,000; Broken Glass: LKR 20,000; Dent: LKR 12,000), or delete false alarms before "
        "committing the final settlement amount. Figure 4.19 illustrates the centralized Company Damage Reports repository, indexing "
        "all finalized claims with direct PDF view and secure download capabilities."
    ])

    img_ui_summaryedit = os.path.join(r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned\\reports\\ui_screenshots", "ui_10_damage_summary_editor.png")
    if os.path.exists(img_ui_summaryedit):
        add_picture_with_caption(doc, img_ui_summaryedit, "Verified Damage Findings and Line-Item Repair Costing Editor")

    img_ui_reportslist = os.path.join(r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned\\reports\\ui_screenshots", "ui_11_damage_reports_archive.png")
    if os.path.exists(img_ui_reportslist):
        add_picture_with_caption(doc, img_ui_reportslist, "Company Damage Reports Centralized Archive and Download Repository")

    # 4.5.5 Official PDF Reports & Customer Self-Service Portal
    add_h3("4.5.5 Generated PDF Assessment Reports and Customer Self-Service Portal")
    add_section_paragraphs([
        "Figure 4.20 and Figure 4.21 present the two-page official vehicle damage assessment report compiled dynamically via the "
        "ReportLab Platypus engine. Page 1 contains the Apex Vehicle Assurance corporate letterhead, report metadata (Report No: "
        "RPT-VDA-20260819-000007-R01), policyholder and vehicle technical specifications, and the high-resolution inspection image "
        "with rendered AI segmentation masks. Page 2 presents the itemized damage repair schedule (Broken Glass 83.8%: LKR 15,000.00; "
        "Broken Glass 56.4%: LKR 20,000.00; Dent 39.4%: LKR 12,000.00) followed by the statutory financial reconciliation table "
        "reflecting Subtotal: LKR 47,000.00, 15% VAT: LKR 7,050.00, and Total Estimated Repair Cost: LKR 54,050.00."
    ])

    img_ui_pdf1 = os.path.join(r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned\\reports\\ui_screenshots", "ui_12_pdf_report_page1.png")
    if os.path.exists(img_ui_pdf1):
        add_picture_with_caption(doc, img_ui_pdf1, "Official PDF Assessment Report (Page 1: Policyholder and Marked Damage Image)")

    img_ui_pdf2 = os.path.join(r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned\\reports\\ui_screenshots", "ui_13_pdf_report_page2.png")
    if os.path.exists(img_ui_pdf2):
        add_picture_with_caption(doc, img_ui_pdf2, "Official PDF Assessment Report (Page 2: Itemized Costing and 15% VAT Breakdown)")

    add_section_paragraphs([
        "Figure 4.22 and Figure 4.23 illustrate the Policyholder Self-Service Customer Portal. Authenticated policyholders (e.g., cus_16) "
        "can view registered vehicles (e.g., KD 1125 BYD), monitor the real-time processing status of their damage assessments, "
        "review verified repair estimates (e.g., LKR 33,350 for Claim VDA-20260819-000010), and download official PDF appraisal "
        "certificates without requiring manual branch visits or telephone follow-ups."
    ])

    img_ui_custdash = os.path.join(r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned\\reports\\ui_screenshots", "ui_15_customer_portal_dashboard.png")
    if os.path.exists(img_ui_custdash):
        add_picture_with_caption(doc, img_ui_custdash, "Policyholder Self-Service Customer Portal Dashboard and Records View")

    img_ui_custassess = os.path.join(r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned\\reports\\ui_screenshots", "ui_16_customer_portal_assessments.png")
    if os.path.exists(img_ui_custassess):
        add_picture_with_caption(doc, img_ui_custassess, "Customer Portal Damage Assessment Review and Vehicle Status Interface")
'''

    # Pattern to replace old 4.5 User Interface Design
    old_pattern = r'add_h2\("4\.5 User Interface Design"\)[\s\S]*?add_h2\("4\.6 Module Design & UML Behavioral Models"\)'
    replacement = section_4_5_code + '\n    add_h2("4.6 Module Design & UML Behavioral Models")'

    new_content = re.sub(old_pattern, lambda m: replacement, content)
    if new_content == content:
        print("WARNING: Regex pattern did not match old section 4.5!")
    else:
        print("Successfully replaced Section 4.5 with comprehensive UI Evidence!")

    # Write out the updated master script
    out_script = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\scripts\generate_final_thesis_docx.py"
    with open(out_script, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Saved updated master generator script to {out_script}")

if __name__ == "__main__":
    main()
