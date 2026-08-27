import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_use_case_diagram(output_path):
    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    ax.axis('off')
    
    # System boundary box
    rect = patches.FancyBboxPatch((0.25, 0.05), 0.50, 0.90, boxstyle="round,pad=0.02", ec="#1e293b", fc="#f8fafc", lw=2)
    ax.add_patch(rect)
    ax.text(0.50, 0.92, "Vehicle Damage Insurance ERP System Boundary", fontsize=12, fontweight='bold', ha='center', color="#0f172a")

    # Actors
    actors = [
        ("System Administrator", 0.08, 0.70),
        ("Claims Operator", 0.08, 0.40),
        ("Policyholder Customer", 0.92, 0.50)
    ]
    
    for name, x, y in actors:
        # Simple actor stick figure representation
        circle = patches.Circle((x, y + 0.05), 0.03, ec="#1e3a8a", fc="#dbeafe", lw=2)
        ax.add_patch(circle)
        ax.plot([x, x], [y + 0.02, y - 0.04], color="#1e3a8a", lw=2) # body
        ax.plot([x - 0.03, x + 0.03], [y, y], color="#1e3a8a", lw=2) # arms
        ax.plot([x, x - 0.02], [y - 0.04, y - 0.08], color="#1e3a8a", lw=2) # leg L
        ax.plot([x, x + 0.02], [y - 0.04, y - 0.08], color="#1e3a8a", lw=2) # leg R
        ax.text(x, y - 0.12, name, fontsize=10, fontweight='bold', ha='center', color="#0f172a")

    # Use Cases inside system boundary
    use_cases = [
        ("Manage Users & Roles", 0.50, 0.82),
        ("Configure Plans & Company", 0.50, 0.72),
        ("Register Customer & Vehicle", 0.50, 0.60),
        ("Upload & AI Inspection", 0.50, 0.48),
        ("Review & Cost Assessment", 0.50, 0.36),
        ("Generate PDF Claim Report", 0.50, 0.24),
        ("View Owned Claims & Status", 0.50, 0.12),
    ]

    for title, x, y in use_cases:
        ellipse = patches.Ellipse((x, y), 0.38, 0.08, ec="#2563eb", fc="#eff6ff", lw=1.5)
        ax.add_patch(ellipse)
        ax.text(x, y, title, fontsize=9.5, fontweight='bold', ha='center', va='center', color="#1e40af")

    # Lines connecting actors to use cases
    # Admin connects to 1, 2
    ax.plot([0.12, 0.31], [0.70, 0.82], color="#475569", lw=1.2, ls="--")
    ax.plot([0.12, 0.31], [0.70, 0.72], color="#475569", lw=1.2, ls="--")
    
    # Operator connects to 3, 4, 5, 6
    ax.plot([0.12, 0.31], [0.40, 0.60], color="#475569", lw=1.2, ls="--")
    ax.plot([0.12, 0.31], [0.40, 0.48], color="#475569", lw=1.2, ls="--")
    ax.plot([0.12, 0.31], [0.40, 0.36], color="#475569", lw=1.2, ls="--")
    ax.plot([0.12, 0.31], [0.40, 0.24], color="#475569", lw=1.2, ls="--")

    # Customer connects to 6, 7
    ax.plot([0.88, 0.69], [0.50, 0.24], color="#475569", lw=1.2, ls="--")
    ax.plot([0.88, 0.69], [0.50, 0.12], color="#475569", lw=1.2, ls="--")

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def draw_class_diagram(output_path):
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.axis('off')

    # Class boxes
    classes = [
        ("User", 0.10, 0.70, 0.22, 0.24, ["id: int", "username: str", "password_hash: str", "role_id: int"], ["authenticate()", "change_password()"]),
        ("Role", 0.10, 0.35, 0.22, 0.20, ["id: int", "code: str", "name: str"], ["get_permissions()"]),
        ("Customer", 0.40, 0.70, 0.24, 0.24, ["id: int", "customer_code: str", "full_name: str", "email: str"], ["register()", "get_vehicles()"]),
        ("Vehicle", 0.40, 0.35, 0.24, 0.24, ["id: int", "registration_number: str", "chassis_number: str", "make: str"], ["get_policies()", "get_analyses()"]),
        ("Analysis", 0.72, 0.55, 0.24, 0.38, ["id: int", "analysis_number: str", "status: str", "total_estimated_cost: float", "accepted_damage_count: int"], ["run_inspection()", "reanalyze()", "finalize()"]),
        ("AnalysisDamage", 0.72, 0.10, 0.24, 0.35, ["id: int", "final_damage_class: str", "severity: str", "estimated_cost: float", "passed_vehicle_gate: bool"], ["update_cost()", "override_gate()"]),
    ]

    for title, x, y, w, h, attrs, methods in classes:
        # Box frame
        rect = patches.Rectangle((x, y), w, h, ec="#1e293b", fc="#ffffff", lw=1.5)
        ax.add_patch(rect)
        # Header box
        hdr = patches.Rectangle((x, y + h - 0.05), w, 0.05, ec="#1e293b", fc="#3b82f6", lw=1.5)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - 0.025, title, fontsize=10, fontweight='bold', ha='center', va='center', color="#ffffff")

        # Attributes
        attr_text = "\n".join(attrs)
        ax.text(x + 0.01, y + h - 0.07, attr_text, fontsize=8, va='top', color="#1e293b")

        # Divider line
        ax.plot([x, x + w], [y + h/2 - 0.01, y + h/2 - 0.01], color="#cbd5e1", lw=1)

        # Methods
        meth_text = "\n".join(methods)
        ax.text(x + 0.01, y + h/2 - 0.03, meth_text, fontsize=8, va='top', color="#1e293b")

    # Relationship arrows
    ax.annotate("", xy=(0.21, 0.55), xytext=(0.21, 0.70), arrowprops=dict(arrowstyle="->", lw=1.5, color="#475569"))
    ax.text(0.22, 0.62, "1..* has", fontsize=8, color="#475569")

    ax.annotate("", xy=(0.40, 0.82), xytext=(0.32, 0.82), arrowprops=dict(arrowstyle="->", lw=1.5, color="#475569"))
    ax.text(0.33, 0.84, "0..1 maps to", fontsize=8, color="#475569")

    ax.annotate("", xy=(0.52, 0.59), xytext=(0.52, 0.70), arrowprops=dict(arrowstyle="->", lw=1.5, color="#475569"))
    ax.text(0.53, 0.64, "1..* owns", fontsize=8, color="#475569")

    ax.annotate("", xy=(0.72, 0.74), xytext=(0.64, 0.47), arrowprops=dict(arrowstyle="->", lw=1.5, color="#475569"))
    ax.text(0.65, 0.62, "1..* analyzed", fontsize=8, color="#475569")

    ax.annotate("", xy=(0.84, 0.45), xytext=(0.84, 0.55), arrowprops=dict(arrowstyle="->", lw=1.5, color="#475569"))
    ax.text(0.85, 0.50, "1..* contains", fontsize=8, color="#475569")

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def draw_er_diagram(output_path):
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.axis('off')

    # Tables representation
    tables = [
        ("roles", 0.05, 0.75, ["id (PK)", "code (UQ)", "name"]),
        ("users", 0.28, 0.75, ["id (PK)", "role_id (FK)", "customer_id (FK)", "username (UQ)", "password_hash"]),
        ("customers", 0.55, 0.75, ["id (PK)", "customer_code (UQ)", "full_name", "email", "phone_primary"]),
        ("vehicles", 0.80, 0.75, ["id (PK)", "customer_id (FK)", "registration_number (UQ)", "chassis_number"]),
        
        ("insurance_plans", 0.05, 0.35, ["id (PK)", "plan_code (UQ)", "name", "coverage_limit", "deductible"]),
        ("vehicle_policies", 0.28, 0.35, ["id (PK)", "vehicle_id (FK)", "plan_id (FK)", "policy_number"]),
        ("vehicle_images", 0.55, 0.35, ["id (PK)", "vehicle_id (FK)", "storage_path", "sha256"]),
        ("analyses", 0.80, 0.35, ["id (PK)", "analysis_number (UQ)", "vehicle_id (FK)", "operator_id (FK)"]),

        ("analysis_damages", 0.40, 0.05, ["id (PK)", "analysis_id (FK)", "final_damage_class", "estimated_cost"]),
        ("reports", 0.70, 0.05, ["id (PK)", "report_number (UQ)", "analysis_id (FK)", "pdf_path"]),
    ]

    for title, x, y, fields in tables:
        w, h = 0.20, 0.22
        rect = patches.Rectangle((x, y), w, h, ec="#1e293b", fc="#ffffff", lw=1.5)
        ax.add_patch(rect)
        hdr = patches.Rectangle((x, y + h - 0.04), w, 0.04, ec="#1e293b", fc="#0284c7", lw=1.5)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - 0.02, title, fontsize=9, fontweight='bold', ha='center', va='center', color="#ffffff")
        
        f_text = "\n".join(fields)
        ax.text(x + 0.01, y + h - 0.06, f_text, fontsize=7.5, va='top', color="#0f172a")

    # Connectors
    ax.plot([0.25, 0.28], [0.86, 0.86], color="#64748b", lw=1.5) # roles -> users
    ax.plot([0.48, 0.55], [0.86, 0.86], color="#64748b", lw=1.5) # users -> customers
    ax.plot([0.75, 0.80], [0.86, 0.86], color="#64748b", lw=1.5) # customers -> vehicles

    ax.plot([0.25, 0.28], [0.46, 0.46], color="#0284c7", lw=1.5) # insurance_plans -> vehicle_policies (plan_id FK)
    ax.plot([0.38, 0.38, 0.90, 0.90], [0.57, 0.66, 0.66, 0.75], color="#0284c7", lw=1.5, ls="--") # vehicle_policies -> vehicles (vehicle_id FK)

    ax.plot([0.65, 0.65], [0.75, 0.57], color="#64748b", lw=1.5) # customers -> vehicle_images
    ax.plot([0.90, 0.90], [0.75, 0.57], color="#64748b", lw=1.5) # vehicles -> analyses

    ax.plot([0.85, 0.50], [0.35, 0.27], color="#64748b", lw=1.5) # analyses -> analysis_damages
    ax.plot([0.90, 0.80], [0.35, 0.27], color="#64748b", lw=1.5) # analyses -> reports

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def draw_sequence_diagram(output_path):
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.axis('off')

    lifelines = [
        ("Claims Operator", 0.10),
        ("Next.js Frontend", 0.30),
        ("FastAPI Backend", 0.50),
        ("YOLO AI Pipeline", 0.70),
        ("MySQL / Storage", 0.90),
    ]

    for name, x in lifelines:
        # Header block
        rect = patches.Rectangle((x - 0.08, 0.88), 0.16, 0.08, ec="#1e293b", fc="#e2e8f0", lw=1.5)
        ax.add_patch(rect)
        ax.text(x, 0.92, name, fontsize=8.5, fontweight='bold', ha='center', va='center', color="#0f172a")
        # Vertical lifeline
        ax.plot([x, x], [0.08, 0.88], color="#cbd5e1", lw=1.2, ls="--")

    # Message arrows
    messages = [
        (0.10, 0.30, 0.80, "1. Select Inspection Photo & Submit"),
        (0.30, 0.50, 0.72, "2. POST /api/analyses/upload (Image Bytes)"),
        (0.50, 0.70, 0.64, "3. Run COCO Gate & YOLO Segmentation"),
        (0.70, 0.50, 0.56, "4. Return Classes, Masks, Confidences"),
        (0.50, 0.90, 0.48, "5. Save Analysis & Damage Entities"),
        (0.90, 0.50, 0.40, "6. Confirm Record Insertion"),
        (0.50, 0.30, 0.32, "7. Return Analysis Data & Visual Overlay"),
        (0.30, 0.10, 0.24, "8. Render Review & Costing Interface"),
    ]

    for x1, x2, y, text in messages:
        ax.annotate("", xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle="->", lw=1.2, color="#2563eb"))
        ax.text((x1 + x2)/2, y + 0.02, text, fontsize=8, fontweight='bold', ha='center', color="#1e40af")

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def draw_deployment_diagram(output_path):
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.axis('off')

    nodes = [
        ("Client Browser Node", 0.08, 0.25, 0.24, 0.55, ["Web Browser", "Next.js React Client", "JWT Token Storage"]),
        ("Web & API Application Server Node", 0.38, 0.25, 0.26, 0.55, ["Next.js Server (Port 3000)", "FastAPI Server (Port 8000)", "Argon2 Auth Engine", "Report PDF Engine"]),
        ("AI Inference & Storage Node", 0.70, 0.25, 0.26, 0.55, ["PyTorch CUDA Engine", "YOLOv8 Damage Model", "COCO Vehicle Gate", "MySQL 8.0 DB (Port 3306)"]),
    ]

    for title, x, y, w, h, comps in nodes:
        # Node 3D effect box
        rect = patches.Rectangle((x, y), w, h, ec="#1e293b", fc="#f1f5f9", lw=1.5)
        ax.add_patch(rect)
        hdr = patches.Rectangle((x, y + h - 0.06), w, 0.06, ec="#1e293b", fc="#475569", lw=1.5)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - 0.03, title, fontsize=8.5, fontweight='bold', ha='center', va='center', color="#ffffff")

        # Components inside
        for idx, c in enumerate(comps):
            c_rect = patches.Rectangle((x + 0.02, y + h - 0.12 - idx*0.10), w - 0.04, 0.08, ec="#3b82f6", fc="#ffffff", lw=1)
            ax.add_patch(c_rect)
            ax.text(x + w/2, y + h - 0.08 - idx*0.10, c, fontsize=8, ha='center', va='center', color="#1e293b")

    # Network connections
    ax.annotate("", xy=(0.38, 0.52), xytext=(0.32, 0.52), arrowprops=dict(arrowstyle="<->", lw=1.5, color="#2563eb"))
    ax.text(0.35, 0.55, "HTTP/HTTPS (Port 3000)", fontsize=7.5, fontweight='bold', ha='center', color="#1e40af")

    ax.annotate("", xy=(0.70, 0.52), xytext=(0.64, 0.52), arrowprops=dict(arrowstyle="<->", lw=1.5, color="#2563eb"))
    ax.text(0.67, 0.55, "REST / SQL (Port 8000/3306)", fontsize=7.5, fontweight='bold', ha='center', color="#1e40af")

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def draw_architectural_design(output_path):
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.axis('off')

    layers = [
        ("Presentation Layer (Next.js 14)", 0.08, 0.75, 0.84, 0.15, ["React Dashboard UI", "Customer Portal", "Inspection Review Workspace"], "#3b82f6"),
        ("Application API Layer (FastAPI)", 0.08, 0.52, 0.84, 0.15, ["JWT Authentication", "Claims & Policy Router", "PDF Report Service"], "#0284c7"),
        ("Vision AI & Inference Layer", 0.08, 0.29, 0.84, 0.15, ["YOLOv8 Damage Segmenter", "COCO Vehicle Gate"], "#0d9488"),
        ("Data & Persistence Layer", 0.08, 0.06, 0.84, 0.15, ["MySQL (15 Relational Tables)", "Local File Storage", "Security Audit Logs"], "#334155"),
    ]

    for title, x, y, w, h, items, color in layers:
        rect = patches.Rectangle((x, y), w, h, ec="#1e293b", fc="#ffffff", lw=1.5)
        ax.add_patch(rect)
        hdr = patches.Rectangle((x, y + h - 0.04), w, 0.04, ec="#1e293b", fc=color, lw=1.5)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - 0.02, title, fontsize=9.5, fontweight='bold', ha='center', va='center', color="#ffffff")

        # Sub items
        iw = (w - 0.08) / len(items)
        for idx, item in enumerate(items):
            i_rect = patches.Rectangle((x + 0.02 + idx*(iw + 0.02), y + 0.02), iw, 0.07, ec="#cbd5e1", fc="#f8fafc", lw=1)
            ax.add_patch(i_rect)
            ax.text(x + 0.02 + idx*(iw + 0.02) + iw/2, y + 0.055, item, fontsize=8, ha='center', va='center', color="#0f172a")

    # Vertical arrows connecting layers
    for y_pos in [0.75, 0.52, 0.29]:
        ax.annotate("", xy=(0.50, y_pos - 0.08), xytext=(0.50, y_pos), arrowprops=dict(arrowstyle="->", lw=1.5, color="#64748b"))

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def draw_activity_diagram(output_path):
    fig, ax = plt.subplots(figsize=(11, 10), dpi=300)
    ax.axis('off')

    # Initial node (filled circle)
    init_circle = patches.Circle((0.50, 0.95), 0.018, ec="#0f172a", fc="#0f172a")
    ax.add_patch(init_circle)
    ax.text(0.50, 0.975, "Start (Operator Upload)", fontsize=9, fontweight='bold', ha='center', color="#0f172a")

    # Arrow from Start to Upload Action
    ax.annotate("", xy=(0.50, 0.90), xytext=(0.50, 0.93), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1e293b"))

    # Activity: Upload Inspection Image
    act1 = patches.FancyBboxPatch((0.35, 0.85), 0.30, 0.045, boxstyle="round,pad=0.01", ec="#2563eb", fc="#eff6ff", lw=1.5)
    ax.add_patch(act1)
    ax.text(0.50, 0.872, "Upload Inspection Photograph", fontsize=8.5, fontweight='bold', ha='center', va='center', color="#1e40af")

    # Arrow to Decision: Valid Image Format
    ax.annotate("", xy=(0.50, 0.81), xytext=(0.50, 0.85), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1e293b"))

    # Decision Diamond 1: Format Valid?
    diamond1 = patches.Polygon([[0.50, 0.81], [0.55, 0.78], [0.50, 0.75], [0.45, 0.78]], ec="#d97706", fc="#fef3c7", lw=1.5)
    ax.add_patch(diamond1)
    ax.text(0.50, 0.78, "Valid\nFormat?", fontsize=7.5, fontweight='bold', ha='center', va='center', color="#92400e")

    # Invalid branch to rejected final node
    ax.plot([0.55, 0.85, 0.85], [0.78, 0.78, 0.72], color="#dc2626", lw=1.2)
    ax.text(0.68, 0.79, "[Invalid]", fontsize=7.5, fontweight='bold', color="#dc2626")
    err_box = patches.FancyBboxPatch((0.74, 0.67), 0.22, 0.045, boxstyle="round,pad=0.01", ec="#dc2626", fc="#fef2f2", lw=1.2)
    ax.add_patch(err_box)
    ax.text(0.85, 0.692, "Display Format Error", fontsize=8, ha='center', va='center', color="#991b1b")
    
    # Fork Bar: Parallel AI Processing (COCO Gate & YOLO Segmentation)
    ax.annotate("", xy=(0.50, 0.71), xytext=(0.50, 0.75), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1e293b"))
    ax.text(0.51, 0.73, "[Valid Image]", fontsize=7.5, fontweight='bold', color="#16a34a")

    fork_bar = patches.Rectangle((0.25, 0.705), 0.50, 0.008, ec="#0f172a", fc="#0f172a")
    ax.add_patch(fork_bar)

    # Parallel Branch 1: COCO Vehicle Detection
    ax.annotate("", xy=(0.35, 0.65), xytext=(0.35, 0.705), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1e293b"))
    act_coco = patches.FancyBboxPatch((0.22, 0.605), 0.26, 0.045, boxstyle="round,pad=0.01", ec="#0284c7", fc="#f0f9ff", lw=1.5)
    ax.add_patch(act_coco)
    ax.text(0.35, 0.627, "Run COCO Vehicle Detector\n(yolov8n.pt)", fontsize=7.5, fontweight='bold', ha='center', va='center', color="#0369a1")

    # Parallel Branch 2: YOLOv8 Damage Segmentation
    ax.annotate("", xy=(0.65, 0.65), xytext=(0.65, 0.705), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1e293b"))
    act_dmg = patches.FancyBboxPatch((0.52, 0.605), 0.26, 0.045, boxstyle="round,pad=0.01", ec="#0d9488", fc="#f0fdfa", lw=1.5)
    ax.add_patch(act_dmg)
    ax.text(0.65, 0.627, "Run YOLOv8 Damage Model\n(7-Class best.pt)", fontsize=7.5, fontweight='bold', ha='center', va='center', color="#0f766e")

    # Join Bar
    ax.annotate("", xy=(0.35, 0.56), xytext=(0.35, 0.605), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1e293b"))
    ax.annotate("", xy=(0.65, 0.56), xytext=(0.65, 0.605), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1e293b"))
    join_bar = patches.Rectangle((0.25, 0.555), 0.50, 0.008, ec="#0f172a", fc="#0f172a")
    ax.add_patch(join_bar)

    # Activity: Spatial Overlap Gating
    ax.annotate("", xy=(0.50, 0.51), xytext=(0.50, 0.555), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1e293b"))
    act_gate = patches.FancyBboxPatch((0.32, 0.465), 0.36, 0.045, boxstyle="round,pad=0.01", ec="#4f46e5", fc="#eef2ff", lw=1.5)
    ax.add_patch(act_gate)
    ax.text(0.50, 0.487, "Evaluate 20% IoU Spatial Overlap Gate", fontsize=8, fontweight='bold', ha='center', va='center', color="#3730a3")

    # Decision Diamond 2: Overlap >= 20% or Manual Override?
    ax.annotate("", xy=(0.50, 0.425), xytext=(0.50, 0.465), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1e293b"))
    diamond2 = patches.Polygon([[0.50, 0.425], [0.56, 0.395], [0.50, 0.365], [0.44, 0.395]], ec="#d97706", fc="#fef3c7", lw=1.5)
    ax.add_patch(diamond2)
    ax.text(0.50, 0.395, "Passed\nGate?", fontsize=7.5, fontweight='bold', ha='center', va='center', color="#92400e")

    # Rejected damage path (filtered out)
    ax.plot([0.56, 0.82, 0.82], [0.395, 0.395, 0.34], color="#64748b", lw=1.2)
    ax.text(0.66, 0.405, "[IoU < 20%]", fontsize=7.5, fontweight='bold', color="#64748b")
    suppr_box = patches.FancyBboxPatch((0.72, 0.295), 0.20, 0.045, boxstyle="round,pad=0.01", ec="#64748b", fc="#f8fafc", lw=1.2)
    ax.add_patch(suppr_box)
    ax.text(0.82, 0.317, "Suppress Background\nFalse Alarm", fontsize=7.5, ha='center', va='center', color="#334155")

    # Accepted / Override Path
    ax.annotate("", xy=(0.50, 0.325), xytext=(0.50, 0.365), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1e293b"))
    ax.text(0.51, 0.345, "[Passed / Override]", fontsize=7.5, fontweight='bold', color="#16a34a")

    # Activity: Operator Review & Line-Item Costing
    act_review = patches.FancyBboxPatch((0.30, 0.275), 0.40, 0.05, boxstyle="round,pad=0.01", ec="#0284c7", fc="#f0f9ff", lw=1.5)
    ax.add_patch(act_review)
    ax.text(0.50, 0.30, "Operator Review & Financial Costing\n(Edit Class, Adjust Rates, Auto-15% VAT)", fontsize=8, fontweight='bold', ha='center', va='center', color="#0369a1")

    # Activity: Finalize & Generate PDF Claim Report
    ax.annotate("", xy=(0.50, 0.23), xytext=(0.50, 0.275), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1e293b"))
    act_pdf = patches.FancyBboxPatch((0.32, 0.18), 0.36, 0.05, boxstyle="round,pad=0.01", ec="#16a34a", fc="#f0fdf4", lw=1.5)
    ax.add_patch(act_pdf)
    ax.text(0.50, 0.205, "Finalize Claim & Generate Branded PDF\n(Save Analysis, Images & Audit Trail)", fontsize=8, fontweight='bold', ha='center', va='center', color="#15803d")

    # Activity: Customer Notification & Portal Access
    ax.annotate("", xy=(0.50, 0.135), xytext=(0.50, 0.18), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1e293b"))
    act_cust = patches.FancyBboxPatch((0.33, 0.09), 0.34, 0.045, boxstyle="round,pad=0.01", ec="#9333ea", fc="#faf5ff", lw=1.5)
    ax.add_patch(act_cust)
    ax.text(0.50, 0.112, "Customer Portal Access & PDF Download", fontsize=8, fontweight='bold', ha='center', va='center', color="#7e22ce")

    # Final Node (Bullseye)
    ax.annotate("", xy=(0.50, 0.05), xytext=(0.50, 0.09), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1e293b"))
    final_outer = patches.Circle((0.50, 0.035), 0.018, ec="#0f172a", fc="#ffffff", lw=1.5)
    final_inner = patches.Circle((0.50, 0.035), 0.010, ec="#0f172a", fc="#0f172a")
    ax.add_patch(final_outer)
    ax.add_patch(final_inner)
    ax.text(0.50, 0.008, "End (Claim Finalized)", fontsize=9, fontweight='bold', ha='center', color="#0f172a")

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def main():
    out_dir = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\reports\uml_diagrams"
    os.makedirs(out_dir, exist_ok=True)
    
    draw_use_case_diagram(os.path.join(out_dir, "use_case_diagram.png"))
    draw_class_diagram(os.path.join(out_dir, "class_diagram.png"))
    draw_activity_diagram(os.path.join(out_dir, "activity_diagram.png"))
    draw_er_diagram(os.path.join(out_dir, "er_diagram.png"))
    draw_sequence_diagram(os.path.join(out_dir, "sequence_diagram.png"))
    draw_deployment_diagram(os.path.join(out_dir, "deployment_diagram.png"))
    draw_architectural_design(os.path.join(out_dir, "architectural_design.png"))
    
    print("All 7 UML & Architecture Diagrams generated successfully in:", out_dir)

if __name__ == "__main__":
    main()

