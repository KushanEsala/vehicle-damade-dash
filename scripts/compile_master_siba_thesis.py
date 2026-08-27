import os
import sys

def main():
    base_file = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\scripts\expand_to_exact_70page_thesis.py"
    with open(base_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract the inner code
    start_marker = "code = r'''"
    end_marker = "'''\n\nwith open("
    
    start_pos = content.find(start_marker) + len(start_marker)
    end_pos = content.find(end_marker)
    
    inner_code = content[start_pos:end_pos]

    # 1. Update outputs to include BSC-WD-22-36-01.docx
    inner_code = inner_code.replace(
        'def build_full_70page_thesis():\n    out_dir = r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned"\n    out_file = os.path.join(out_dir, "Vehicle_Damage_Assessment_Final_Thesis_2026.docx")\n    out_file_backup = os.path.join(out_dir, "Vehicle_Damage_Assessment_Final_Report_Repaired_Dynamic.docx")',
        'def build_full_70page_thesis():\n    out_dir = r"d:\\FinalProject 2026\\vehicle_damade_dash_cloned"\n    out_file_bsc = os.path.join(out_dir, "BSC-WD-22-36-01.docx")\n    out_file = os.path.join(out_dir, "Vehicle_Damage_Assessment_Final_Thesis_2026.docx")\n    out_file_latest = os.path.join(out_dir, "Vehicle_Damage_Assessment_Final_Thesis_2026_Latest.docx")\n    out_file_backup = os.path.join(out_dir, "Vehicle_Damage_Assessment_Final_Report_Repaired_Dynamic.docx")'
    )

    # 2. Update cover page
    cover_old = '''    # -------------------------------------------------------------
    # SECTION 1: COVER / TITLE PAGE
    # -------------------------------------------------------------
    sec1 = doc.sections[0]
    sec1.page_width = Mm(210)
    sec1.page_height = Mm(297)
    sec1.top_margin = Inches(1.0)
    sec1.bottom_margin = Inches(1.0)
    sec1.left_margin = Inches(1.5)
    sec1.right_margin = Inches(1.0)
    sec1.different_first_page_header_footer = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(14)
    r = p.add_run("VEHICLE DAMAGE DETECTION USING DEEP LEARNING INSTANCE SEGMENTATION FOR AUTOMATED INSURANCE ERP ASSESSMENT")
    r.font.size = Pt(16)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(28)
    r = p.add_run("A ROLE-BASED AUTOMOTIVE CLAIMS ASSESSMENT AND ENTERPRISE RESOURCE PLANNING PLATFORM")
    r.font.size = Pt(13)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(14)
    r = p.add_run("A PROJECT THESIS SUBMITTED BY")
    r.font.size = Pt(13)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(28)
    r = p.add_run("W.M.M.G. SENAVIRATHNE\\n(Registration No: BSC/WD/22/36/01)")
    r.font.size = Pt(12)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("to the\\n")
    r.font.size = Pt(12)
    r.font.italic = True
    r2 = p.add_run("DEPARTMENT OF INFORMATION TECHNOLOGY")
    r2.font.size = Pt(14)
    r2.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(20)
    r = p.add_run("in partial fulfillment of the requirement for the award of the degree of")
    r.font.size = Pt(12)
    r.font.italic = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("BSc in Information Technology")
    r.font.size = Pt(14)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(20)
    r = p.add_run("of the")
    r.font.size = Pt(12)
    r.font.italic = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(28)
    r = p.add_run("SRI LANKA INTERNATIONAL BUDDHIST ACADEMY (SIBA CAMPUS)\\nPALLEKELE, KUNDASALE, SRI LANKA")
    r.font.size = Pt(12)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("August 2026")
    r.font.size = Pt(12)'''

    cover_new = '''    # -------------------------------------------------------------
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

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(20)
    r = p.add_run("VEHICLE DAMAGE DETECTION USING DEEP LEARNING INSTANCE SEGMENTATION FOR AUTOMATED INSURANCE ERP ASSESSMENT")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(14)
    r = p.add_run("A PROJECT THESIS SUBMITTED BY")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("W.M.M.G. SENAVIRATHNE\\n(BSC/WD/22/36/01)")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("to the\\nDEPARTMENT OF INFORMATION TECHNOLOGY")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    r_deg_it = p.add_run("in partial fulfilment of the requirement for the award of the degree of\\n")
    r_deg_it.font.name = 'Times New Roman'
    r_deg_it.font.size = Pt(12)
    r_deg_it.font.italic = True
    r_deg_name = p.add_run("BSc. in Information Technology")
    r_deg_name.font.name = 'Times New Roman'
    r_deg_name.font.size = Pt(13)
    r_deg_name.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("of the")
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

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("SRI LANKA INTERNATIONAL BUDDHIST ACADEMY\\nPALLEKELE SRI LANKA\\nAugust 2026")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True'''

    inner_code = inner_code.replace(cover_old, cover_new)

    # 3. Update EER Section
    eer_old = '''    add_h2("4.4 Database Design")
    add_section_paragraphs([
        "The persistence layer is structured around a 15-table relational schema normalized to Third Normal Form (3NF) to guarantee transactional integrity, eliminate data redundancy, and maintain strict referential constraints. Figure 4.3 presents the Entity-Relationship Diagram (ERD)."
    ])
    add_picture_with_caption(doc, img_er, "Entity-Relationship Diagram (15 Relational Database Tables)")

    add_section_paragraphs([
        "The 15 normalized tables and their functional responsibilities include:",
        "1. roles: Stores administrative, assessor, and customer role definitions (id, code, name, description).",
        "2. customers: Maintains legal customer profiles (customer_code, full_name, nic_or_passport, phone, email, city).",
        "3. users: Stores secure login credentials, Argon2id password hashes, role_id foreign keys, and optional customer_id linkages.",
        "4. app_sessions: Manages active authenticated sessions, session tokens, user agents, IP addresses, and expiry timestamps.",
        "5. vehicles: Records insured vehicle assets (registration_number, chassis_number, make, model, year, fuel_type) mapped to customer_id.",
        "6. insurance_plans: Defines standard coverage plans, default coverage limits, and deductible structures.",
        "7. vehicle_policies: Links active insurance policies to specific vehicles with effective dates, custom coverage limits, and deductibles.",
        "8. vehicle_images: Stores uploaded inspection photographs, disk paths, image metadata, and cryptographic SHA-256 integrity hashes.",
        "9. analyses: Central inspection session entity recording vehicle_id, operator_id, total estimated cost, accepted damage counts, and status.",
        "10. analysis_damages: Fine-grained defect entity recording damage_type, severity, polygon mask coordinates (JSON), unit repair cost, and spatial gate validation flags.",
        "11. reports: Records generated official claim reports, unique reference codes, and local PDF disk paths.",
        "12. audit_logs: Immutable log storing actor_id, action, entity_name, entity_id, previous_state (JSON), new_state (JSON), and timestamp.",
        "13. company_profile: Stores insurance company corporate metadata, branch address, contact details, and VAT registration number for PDF header generation.",
        "14. damage_pricing_catalog: Standardized regional unit pricing catalog mapping damage classes and severities to default labor and material costs.",
        "15. vehicle_inspection_notes: Assessor textual remarks, garage recommendations, and physical handover notes attached to specific claim analyses."
    ])

    add_h3("4.4.16 Third Normal Form (3NF) Relational Normalization Proof")
    add_section_paragraphs([
        "To guarantee mathematical rigor and prevent update, deletion, and insertion anomalies, the database design adheres strictly to Third Normal Form (3NF) principles:",
        "• First Normal Form (1NF) Compliance: All table attributes contain strictly atomic, non-decomposable values. Repeating groups and array fields (such as multi-part damage annotations) are decomposed into dedicated child entities (such as analysis_damages) linked via foreign key relationships.",
        "• Second Normal Form (2NF) Compliance: Every non-key attribute is fully functionally dependent on the entire primary key. In composite relationships (such as vehicle_policies and analysis_damages), no partial key dependencies exist.",
        "• Third Normal Form (3NF) Compliance: No transitive functional dependencies exist among non-key attributes. For example, customer address and contact details reside strictly within customers rather than being transitively duplicated inside vehicles, users, or analyses tables. Financial pricing formulas reference standardized lookup keys in damage_pricing_catalog, ensuring total data integrity."
    ])'''

    eer_new = '''    add_h2("4.4 Database Design")
    add_section_paragraphs([
        "The persistence layer of the Apex Vehicle Assurance platform is structured around a 15-table relational schema normalized to Third Normal Form (3NF) to guarantee ACID transactional guarantees, eliminate data redundancy, enforce strict referential constraints, and support high-throughput claim auditing. Figure 4.3 presents the formal Enhanced Entity-Relationship Diagram (EERD) of the proposed system, adhering to standard database modeling conventions (Elmasri-Navathe and MySQL Workbench notation)."
    ])
    add_picture_with_caption(doc, img_er, "Enhanced Entity-Relationship Diagram (EERD) - 15 Normalized Database Entities, Attributes, Constraints, and Specialization Hierarchies", width_inches=6.2)

    add_h3("4.4.1 EER Subsystem Decomposition and Entity Responsibilities")
    add_section_paragraphs([
        "As illustrated in Figure 4.3, the enterprise database architecture is logically decomposed across five cohesive functional subsystems:",
        "1. User Access & Identity Governance Subsystem: Encapsulates the roles and users entities. The roles table defines authorization profiles (Admin, Operator, Customer), while users maintains Argon2id memory-hard password hashes, active flags, and optional customer linkages.",
        "2. Customer & Vehicle Fleet Asset Registry: Encapsulates customers, vehicles, and company_profile. The customers entity maintains verified citizen identity (NIC/passport), contact telephone, email, and city records. The vehicles entity captures vehicle registration numbers (e.g., CP-KD-9287, TST-121748), chassis numbers, make, model, manufacture year, and fuel types linked via a mandatory 1:1..N relationship. The company_profile entity stores corporate metadata, branch address, hotline, and default VAT tax rates for PDF report headers.",
        "3. Insurance Policy & Underwriting Subsystem: Comprises app_sessions, insurance_plans, and vehicle_policies. The insurance_plans entity defines standard coverage tiers (Gold, Silver, Platinum, Third-Party) with statutory liability limits and deductible thresholds. The vehicle_policies entity binds active insurance contracts to specific registered vehicles with effective dates, custom coverage limits, and deductible terms.",
        "4. AI Inspection & Damage Assessment Pipeline: Comprises vehicle_images, analyses, and vehicle_inspection_notes. The vehicle_images entity stores physical upload paths, MIME types, file sizes, and SHA-256 cryptographic hashes. The analyses entity acts as the central claim inspection session record, storing operator references, vehicle presence flags, subtotal repair estimates, statutory VAT amounts, net payable values, and workflow statuses (Pending, Analyzed, Finalized). The vehicle_inspection_notes entity records assessor remarks, technical garage observations, and handover notes.",
        "5. Damage Costing, Claim Reporting & System Audit Engine: Encapsulates damage_pricing_catalog, analysis_damages, reports, and audit_logs. The damage_pricing_catalog entity standardizes regional labor rates and replacement part costs for specific damage types and severities. The analysis_damages entity stores individual defect instances, confidence scores, 20% IoU spatial gating validation flags, polygonal mask coordinates serialized in JSON format, and itemized repair estimates. The reports entity archives finalized claim reports with unique references (e.g., RPT-VDA-20260819-000007-R01) and PDF file paths. The audit_logs entity provides an immutable audit trail recording actor IDs, actions, entity targets, prior states (JSON), new states (JSON), client IP addresses, and UTC timestamps."
    ])

    add_h3("4.4.2 Strong versus Weak Entity Classification")
    add_section_paragraphs([
        "In accordance with Enhanced Entity-Relationship modeling principles, entities are categorized into Strong and Weak types based on existential dependency and key inheritance:",
        "- Strong Entities (Solid Card Borders): Entities possessing independent primary keys that exist autonomously without requiring parent records. These comprise roles, users, customers, vehicles, insurance_plans, company_profile, analyses, and damage_pricing_catalog.",
        "- Weak Entities (Double / Dotted Inner Margins): Entities whose existence depends strictly on a parent entity via mandatory foreign key constraints. In this architecture, vehicle_images is existentially dependent on vehicles (an image cannot exist without an associated vehicle); analysis_damages is dependent on analyses; vehicle_inspection_notes is dependent on analyses; app_sessions is dependent on users; reports is dependent on analyses; and audit_logs is dependent on the system event stream. Cascade delete rules (ON DELETE CASCADE) and referential restrictions (ON DELETE RESTRICT) are enforced to maintain total database consistency."
    ])

    add_h3("4.4.3 EER Specialization and Generalization Hierarchies")
    add_section_paragraphs([
        "The EER diagram incorporates two formal disjoint specialization hierarchies indicated by the disjoint circle notation (d):",
        "- User Role Specialization Hierarchy: The superclass users specializes into three disjoint subclasses: [Admin User] (possessing full tenant governance and user management privileges), [Claims Assessor / Operator] (possessing inspection upload, AI review, and claim finalization privileges), and [Policyholder Portal User] (possessing read-only access to personal vehicle records and claim certificates). The disjoint constraint (d) guarantees that a user account operates under a single active role profile per session.",
        "- Damage Defect Specialization Hierarchy: The superclass analysis_damages specializes into seven distinct automotive defect subclasses: is-a: Scratch, is-a: Dent, is-a: Tear, is-a: Broken Lamp, is-a: Broken Glass, is-a: Puncture, and is-a: Missing Part. Each subclass inherits the base attributes (damage_type, severity, confidence, estimated_cost) while maintaining distinct polygon mask geometries, severity rating bounds, and catalog repair pricing formulas."
    ])

    add_h3("4.4.4 Crow's Foot Cardinality and Relational Integrity Rules")
    add_section_paragraphs([
        "The relational connectors in Figure 4.3 enforce precise cardinality constraints using standard Crow's Foot notation:",
        "- Mandatory 1 to Mandatory Many (||-----|<): A single parent record must be associated with one or more child records. For example, customers (1) to vehicles (1..N) dictates that every registered vehicle must belong to exactly one customer. Similarly, analyses (1) to reports (1..N) guarantees that generated claim certificates link to a valid inspection session.",
        "- Mandatory 1 to Optional Many (||-----o<): A parent record may be associated with zero, one, or many child records. For example, roles (1) to users (0..N) allows roles to exist prior to user assignment; users (1) to app_sessions (0..N) accommodates users with no active login sessions; and analyses (1) to analysis_damages (0..N) accommodates vehicle photos with no detected damage.",
        "- Optional 1 to Optional 1 (o|-----o|): A customer record may optionally link to a single portal user account (customers to users via customer_id FK), allowing walk-in policyholders without portal accounts as well as corporate administrators without customer profiles."
    ])

    add_h3("4.4.5 Third Normal Form (3NF) Relational Normalization Proof")
    add_section_paragraphs([
        "To guarantee mathematical rigor, prevent data anomalies, and ensure database performance, the 15-table relational schema was formally designed and validated to satisfy Third Normal Form (3NF):",
        "- First Normal Form (1NF) Compliance: Every table column holds strictly atomic, non-decomposable values. Multi-valued repeating groups (such as multi-point damage coordinates) are serialized into standardized JSON data types within analysis_damages or decomposed into dedicated child entities, eliminating repeating attribute groups.",
        "- Second Normal Form (2NF) Compliance: The schema satisfies 1NF and ensures that all non-key attributes are fully functionally dependent on the entire primary key. In entities with composite or foreign key associations (such as vehicle_policies and analysis_damages), no partial key dependencies exist; every attribute depends on the primary key identifier (id).",
        "- Third Normal Form (3NF) Compliance: The schema satisfies 2NF and eliminates all transitive functional dependencies across non-key attributes. For example, customer contact information (full_name, phone_primary, email, city) is stored exclusively in the customers entity rather than being transitively duplicated in vehicles, users, or analyses tables. Financial pricing formulas reference standardized lookup keys in damage_pricing_catalog rather than storing hardcoded labor rates in analysis_damages, ensuring total data integrity during catalog updates."
    ])'''

    inner_code = inner_code.replace(eer_old, eer_new)

    # 4. Insert Section 4.5 UI Evidence
    ui_old = '''    add_h2("4.5 User Interface Design")
    add_section_paragraphs([
        "The user interface adheres to modern design principles tailored for automotive inspection workflows:",
        "• Visual Identity: A rich dark theme utilizing slate/navy backgrounds (#0f172a, #1e293b) with vibrant cyan (#38bdf8), emerald (#10b981), and amber (#f59e0b) accents that maximize visual contrast for damage mask inspection.",
        "• Interactive Canvas: Digital inspection images are rendered with overlaid SVG/HTML5 canvas polygons corresponding to YOLOv8 segmentation masks, color-coded by damage category.",
        "• Accessibility & Responsiveness: Adheres to WCAG 2.1 AA contrast standards with fully fluid responsive breakpoints for desktop monitors, workshop laptops, and mobile tablets."
    ])'''

    ui_new = '''    # =============================================================
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
        add_picture_with_caption(doc, img_ui_custassess, "Customer Portal Damage Assessment Review and Vehicle Status Interface")'''

    inner_code = inner_code.replace(ui_old, ui_new)

    # 5. Clean word "prone"
    inner_code = inner_code.replace("prone to", "susceptible to")
    inner_code = inner_code.replace("prone", "susceptible")

    # 6. Save loop
    save_old = '''    # Save outputs
    for p_out in [out_file, out_file_backup]:
        try:
            doc.save(p_out)
            print(f"Comprehensive Final Thesis DOCX successfully saved at: {p_out}")
        except Exception as e:
            print(f"Warning: Could not save to {p_out}: {e}")'''

    save_new = '''    # Save outputs
    for p_out in [out_file_bsc, out_file_latest, out_file_backup, out_file]:
        try:
            doc.save(p_out)
            print(f"Comprehensive Final Thesis DOCX successfully saved at: {p_out}")
        except Exception as e:
            print(f"Warning: Could not save to {p_out}: {e}")'''

    inner_code = inner_code.replace(save_old, save_new)

    # Clean characters
    inner_code = inner_code.replace("—", " - ")
    inner_code = inner_code.replace("–", " - ")
    inner_code = inner_code.replace("“", '"')
    inner_code = inner_code.replace("”", '"')
    inner_code = inner_code.replace("‘", "'")
    inner_code = inner_code.replace("’", "'")
    inner_code = inner_code.replace("…", "...")
    inner_code = inner_code.replace("•", "-")

    script_path = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\scripts\generate_final_thesis_docx.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(inner_code)
    print(f"Successfully compiled master thesis builder to {script_path}")

if __name__ == "__main__":
    main()
