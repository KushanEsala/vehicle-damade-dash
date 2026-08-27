import os

def sync_markdown():
    md_path = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\FINAL_PROJECT_THESIS_2026.md"
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Locate Chapter 4
    ch4_idx = -1
    ch5_idx = -1
    for i, line in enumerate(lines):
        if "## CHAPTER 4: SYSTEM DESIGN AND IMPLEMENTATION" in line:
            ch4_idx = i
        elif "## CHAPTER 5: TESTING, RESULTS AND DISCUSSION" in line:
            ch5_idx = i

    if ch4_idx != -1 and ch5_idx != -1:
        new_ch4 = """## CHAPTER 4: SYSTEM DESIGN AND IMPLEMENTATION

### 4.1 Introduction
This chapter details the 4-layer decoupled architecture, UML 2.5.1 behavioral models, 15-table relational database schema, user interface design principles, AI model training workflow, and core implementation details.

### 4.2 System Architecture
The system implements a 4-layer decoupled client-server architecture:
1. **Presentation Layer (Next.js 14):** React Server Components, TypeScript, Tailwind CSS, Admin Center, Review Workspace, Customer Portal.
2. **Application API Layer (FastAPI):** Asynchronous REST API routing, Pydantic validation, Argon2id auth, ReportLab PDF generator.
3. **Vision AI & Inference Layer:** PyTorch/YOLOv8 runtime, COCO vehicle validator (`yolov8n.pt`), 7-class damage segmenter (`best.pt`), 20% IoU spatial gating rule.
4. **Data & Persistence Layer:** 15 normalized MySQL tables, cryptographic file storage, immutable audit logs.

### 4.3 Database Design (15 Relational Tables)
The database schema is normalized to Third Normal Form (3NF), comprising: `roles`, `users`, `customers`, `vehicles`, `insurance_plans`, `vehicle_policies`, `vehicle_images`, `analyses`, `analysis_vehicle_detections`, `analysis_damages`, `analysis_revisions`, `reports`, `audit_logs`, `company_information`, and `model_versions`.

### 4.4 AI Model Training Methodology
• **Dataset:** 13,945 images (11,621 train = 83.33%, 2,324 val = 16.67%) across 7 classes: `scratch` (12,259), `dent` (4,708), `tear` (4,542), `missing_part` (2,370), `broken_lamp` (2,324), `puncture` (2,001), `broken_glass` (1,815).  
• **Hyperparameters:** $640 \\times 640$ resolution, Batch Size 16, 50 Epochs, SGD Optimizer (Momentum 0.937, Weight Decay 0.0005, Base LR 0.01 with Cosine Decay), Mosaic 1.0, HSV jitter ($h=0.015, s=0.7, v=0.4$).  
• **4-Stage Hardware Resume Workflow:** Epochs 1–15 on CPU (24h 9m, ~96m/epoch) $\\rightarrow$ Checkpoint transfer to NVIDIA RTX GPU (CUDA 12.8) & path re-anchoring via `prepare_dataset.py` $\\rightarrow$ Resume Epochs 16–50 (1m 18s/epoch, 45m 32s total) $\\rightarrow$ Real-time TensorBoard monitoring & best model selection at Epoch 44 (`best.pt`, SHA-256: `C9D86E67A4C14F65047F33C17B4C4357613A0A15B52F919D76FF1C8542C0D541`).

### 4.5 Implemented User Interfaces and Operational System Evidence
To provide empirical verification of system implementation and demonstrate the full operational lifecycle of the Apex Vehicle Assurance ERP platform, this section presents the implemented graphical user interfaces (GUIs) across all three role-based user personas: System Administrator, Claims Operations Officer, and Insured Policyholder.

#### 4.5.1 Authentication and Role-Based Access Control Interfaces
• **Figure 4.8: System Authentication and Role-Based Portal Sign-In Interface**  
![System Sign-In](reports/ui_screenshots/ui_01_signin_admin.png)  
*Explanation:* Visualizes the secure split-pane Next.js 14 sign-in interface with dark brand panel on the left and authenticated credentials form on the right. User passwords are verified against Argon2id memory-hard cryptographic hashes, and successful authentication generates cryptographically signed JWT access tokens stored within secure HttpOnly cookies to mitigate Cross-Site Scripting (XSS) and Session Hijacking vectors.

• **Figure 4.9: User Access Governance and Staff Account Management Interface**  
![User Management](reports/ui_screenshots/ui_14_user_management.png)  
*Explanation:* Visualizes the Administrator user management table and staff creation form. Details role assignment (`Operator`, `Admin`), auto-provisioning of customer credentials, account status toggles (`Active`, `Deactivated`), temporary password generation with cryptographic entropy, and audit logging of all administrative actions in the MySQL `audit_logs` table.

#### 4.5.2 Executive Dashboard and Underwriting Fleet Management
• **Figure 4.10: Executive Claims Overview and Real-Time Operational KPI Dashboard**  
![Executive Dashboard](reports/ui_screenshots/ui_02_dashboard_admin.png)  
*Explanation:* Renders five real-time Key Performance Indicator (KPI) summary cards querying MySQL aggregation endpoints: Total Registered Customers (11), Total Insured Vehicles (12), Total AI Analyses Conducted (6), Finalized Analyses Pending Settlement, and Cumulative Estimated Repair Costs in Sri Lankan Rupees (LKR).

• **Figure 4.11: Customer Registration and Automated Portal Provisioning Interface**  
![Customer Registration](reports/ui_screenshots/ui_03_customer_registration.png)  
*Explanation:* Shows the policyholder onboarding form with auto-generated standardized customer code (e.g., `CUS-2026-000015`), National Identity Card (NIC) / passport validation, and linked portal login credential issuance displayed via a dismissible security banner.

• **Figure 4.12: Registered Customer Records Directory and Portal Status Registry**  
![Customer Records](reports/ui_screenshots/ui_04_customer_records_list.png)  
*Explanation:* Displays the centralized customer directory supporting instant search, telephone/email contact verification, and active portal status indicators (`Active`, `Not Issued`).

• **Figure 4.13: Insured Vehicle Fleet Registration and Policy Binding Interface**  
![Vehicle Registration](reports/ui_screenshots/ui_05_vehicle_registration.png)  
*Explanation:* Operators bind vehicles to registered policyholders via foreign key constraints, capturing vehicle registration numbers (e.g., `CP-KD-9287`, `TST-121748`, `WP-CAB-1234`), chassis numbers, make, model, manufacturing year, and fuel type.

• **Figure 4.14: Insurance Coverage Plans and Underwriting Schedule Configuration**  
![Insurance Plans](reports/ui_screenshots/ui_06_insurance_plans.png)  
*Explanation:* Illustrates the insurance coverage plans configuration panel, defining statutory underwriting tiers (`Comprehensive Gold Auto Shield`, `Comprehensive Silver Shield`, `Platinum Premium Cover`, and `Third-Party Only`) with coverage limits up to LKR 10,000,000 and policy deductibles between LKR 5,000 and LKR 25,000.

#### 4.5.3 AI-Powered Damage Inspection and Interactive Segmentation Visualizer
• **Figure 4.15: Damage Inspection Photo Upload and Confidence Parameter Configuration**  
![New Assessment Upload](reports/ui_screenshots/ui_07_new_assessment_upload.png)  
*Explanation:* Claims officers select the target customer and registered vehicle from relational dropdowns, upload inspection imagery in JPG, PNG, or WEBP formats, and configure real-time dual confidence threshold sliders: Damage Finding Confidence (default 30%) and Vehicle Gating Confidence (default 25%).

• **Figure 4.16: Interactive AI Instance Segmentation Visualizer and Spatial Gating Canvas**  
![Damage Visualizer Canvas](reports/ui_screenshots/ui_08_damage_visualizer_canvas.png)  
*Explanation:* Demonstrates the core AI visualizer canvas following inference execution. The dual-stage pipeline achieves spatial noise suppression and multi-class instance segmentation: (1) COCO vehicle detector identifies the vehicle body with a green bounding box (`car 83%`); (2) fine-tuned YOLOv8 nano segmentation model extracts exact polygon boundaries: `Dent 39%` (blue mask across door panels), `Broken Glass 84%` (cyan mask on front window), and `Broken Glass 56%` (cyan mask on rear window). The top financial summary displays 3 accepted damage findings, an itemized subtotal of LKR 47,000, and a net estimate of LKR 54,050 including 15% statutory VAT.

#### 4.5.4 Assessment Review, Line-Item Financial Costing, and Claim Finalization
• **Figure 4.17: Assessment Review Header and Vehicle Claim Finalization Actions**  
![Assessment Review Header](reports/ui_screenshots/ui_09_assessment_review_header.png)  
*Explanation:* Displays the formal assessment review workspace header for Claim Reference `VDA-20260819-000007`, showing the linked vehicle badge (`TST-121748 Honda Civic`), system validation status (`Vehicle Confirmed`, `Analyzed`), and operational action buttons (`Reanalyze`, `Finalize report`).

• **Figure 4.18: Verified Damage Findings and Line-Item Repair Costing Editor**  
![Damage Summary Editor](reports/ui_screenshots/ui_10_damage_summary_editor.png)  
*Explanation:* Human-in-the-loop review interface where claims assessors can audit each AI-detected damage region, modify damage classifications, adjust severity ratings, enter custom panel descriptions, update itemized repair costs (Broken Glass: LKR 15,000; Broken Glass: LKR 20,000; Dent: LKR 12,000), or delete false alarms before committing the final settlement.

• **Figure 4.19: Company Damage Reports Centralized Archive and Download Repository**  
![Damage Reports Archive](reports/ui_screenshots/ui_11_damage_reports_archive.png)  
*Explanation:* Illustrates the centralized Company Damage Reports repository, indexing all finalized claims with direct PDF view and secure download capabilities.

#### 4.5.5 Generated Official PDF Reports and Policyholder Customer Portal
• **Figure 4.20: Official PDF Assessment Report (Page 1: Policyholder & Marked Damage Image)**  
![PDF Report Page 1](reports/ui_screenshots/ui_12_pdf_report_page1.png)  
*Explanation:* Page 1 of the official claim appraisal certificate compiled dynamically via ReportLab Platypus, containing the corporate letterhead, report metadata (`RPT-VDA-20260819-000007-R01`), policyholder/vehicle technical specifications, and high-resolution annotated inspection photograph.

• **Figure 4.21: Official PDF Assessment Report (Page 2: Itemized Costing & 15% Statutory VAT Breakdown)**  
![PDF Report Page 2](reports/ui_screenshots/ui_13_pdf_report_page2.png)  
*Explanation:* Page 2 of the official claim report detailing the verified findings table (Damage type, vehicle part, severity, confidence, estimated cost) and the statutory financial reconciliation table (Subtotal: LKR 47,000.00, 15% VAT: LKR 7,050.00, Discount: LKR 0.00, Total Estimated Repair Cost: LKR 54,050.00).

• **Figure 4.22: Policyholder Self-Service Customer Portal Dashboard and Records View**  
![Customer Portal Dashboard](reports/ui_screenshots/ui_15_customer_portal_dashboard.png)  
*Explanation:* Authenticated policyholders (`cus_16`) can view registered vehicles, monitor real-time claim processing status, review verified repair estimates, and download official PDF appraisal certificates without requiring manual branch visits.

• **Figure 4.23: Customer Portal Damage Assessment Review and Vehicle Status Interface**  
![Customer Portal Assessments](reports/ui_screenshots/ui_16_customer_portal_assessments.png)  
*Explanation:* Policyholder claims review interface displaying active claim status (`VDA-20260819-000010`, `KD 1125 BYD`, Finalized status, LKR 33,350 total), ensuring end-to-end transparency.

### 4.6 Core Implementation Code Snippets
```python
# FastAPI Service: Damage Analysis and Spatial Gating Pipeline
from ml.damage_analyzer import DamageAnalyzer
from ml.vehicle_validator import VehicleValidator

def analyze_vehicle_inspection(image_bytes: bytes, dmg_thresh: float = 0.30, veh_thresh: float = 0.25):
    # Step 1: Run COCO Vehicle Detector
    veh_result = VehicleValidator.detect(image_bytes, threshold=veh_thresh)
    
    # Step 2: Run Fine-Tuned YOLOv8 Damage Segmentation
    dmg_result = DamageAnalyzer.segment(image_bytes, threshold=dmg_thresh)
    
    # Step 3: Apply Spatial Gating Overlap Rule (20% IoU)
    accepted_damages = []
    for dmg in dmg_result.predictions:
        if veh_result.has_vehicle and veh_result.overlaps(dmg.box, min_ratio=0.20):
            dmg.passed_vehicle_gate = True
            accepted_damages.append(dmg)
        else:
            dmg.passed_vehicle_gate = False
            
    return {
        'accepted_damages': accepted_damages,
        'all_damages': dmg_result.predictions,
        'vehicle_detected': veh_result.has_vehicle
    }
```

```python
# Dynamic 15% Statutory VAT & Deductible Calculation Service
def compute_final_claim_financials(damages_list: list, deductible: float = 0.0, vat_rate: float = 0.15):
    subtotal_repair_cost = sum(item['estimated_cost'] for item in damages_list if item.get('accepted', True))
    vat_amount = subtotal_repair_cost * vat_rate
    gross_total_with_tax = subtotal_repair_cost + vat_amount
    net_claim_payable = max(0.0, gross_total_with_tax - deductible)
    
    return {
        'subtotal_repair_cost': round(subtotal_repair_cost, 2),
        'vat_rate_percent': round(vat_rate * 100, 1),
        'vat_amount': round(vat_amount, 2),
        'gross_total_with_tax': round(gross_total_with_tax, 2),
        'policy_deductible': round(deductible, 2),
        'net_claim_payable': round(net_claim_payable, 2)
    }
```

"""
        before_ch4 = "".join(lines[:ch4_idx])
        after_ch4 = "".join(lines[ch5_idx:])
        full_md = before_ch4 + new_ch4 + after_ch4

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(full_md)
        print(f"Successfully synchronized Chapter 4 with UI evidence in {md_path}")
    else:
        print("Error: Could not find chapter markers in markdown file.")

if __name__ == "__main__":
    sync_markdown()
