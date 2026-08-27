import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_comprehensive_er_diagram(output_path):
    # Set high-resolution figure with clean styling
    fig, ax = plt.subplots(figsize=(15, 10.5), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Subsystem background bounding regions (light tinted backgrounds)
    regions = [
        # (x, y, w, h, label, color)
        (0.02, 0.69, 0.31, 0.29, "USER & ACCESS GOVERNANCE", "#f8fafc", "#cbd5e1"),
        (0.35, 0.69, 0.63, 0.29, "CUSTOMER & VEHICLE ASSET REGISTRY", "#f0fdf4", "#bbf7d0"),
        (0.02, 0.36, 0.31, 0.31, "POLICY & UNDERWRITING", "#fefce8", "#fef08a"),
        (0.35, 0.36, 0.63, 0.31, "AI DAMAGE INSPECTION & ASSESSMENT", "#f0f9ff", "#bae6fd"),
        (0.02, 0.02, 0.96, 0.32, "FINANCIAL COSTING, REPORTING & SYSTEM AUDITING", "#faf5ff", "#e9d5ff"),
    ]

    for rx, ry, rw, rh, rlabel, rbg, rborder in regions:
        region_rect = patches.FancyBboxPatch(
            (rx, ry), rw, rh, boxstyle="round,pad=0.01", ec=rborder, fc=rbg, lw=1.2, ls="--"
        )
        ax.add_patch(region_rect)
        ax.text(rx + 0.01, ry + rh - 0.02, rlabel, fontsize=8.5, fontweight='bold', color="#64748b", va='top')

    # Detailed table definitions: (name, x, y, w, h, header_color, [ (col, is_pk, is_fk, is_uq) ])
    # Formatted with clear types
    tables_data = [
        # 1. roles
        ("roles", 0.03, 0.72, 0.13, 0.21, "#1e40af", [
            ("PK id : BIGINT", True, False, False),
            ("UQ code : VARCHAR(30)", False, False, True),
            ("name : VARCHAR(60)", False, False, False),
            ("description : VARCHAR", False, False, False),
            ("created_at : DATETIME", False, False, False),
        ]),
        # 2. users
        ("users", 0.18, 0.72, 0.14, 0.21, "#1e40af", [
            ("PK id : BIGINT", True, False, False),
            ("FK role_id : BIGINT", False, True, False),
            ("FK customer_id : BIGINT", False, True, False),
            ("UQ username : VARCHAR(80)", False, False, True),
            ("email : VARCHAR(255)", False, False, False),
            ("password_hash : VARCHAR", False, False, False),
            ("is_active : BOOLEAN", False, False, False),
        ]),
        # 3. customers
        ("customers", 0.37, 0.72, 0.15, 0.22, "#15803d", [
            ("PK id : BIGINT", True, False, False),
            ("UQ customer_code : VARCHAR", False, False, True),
            ("full_name : VARCHAR(150)", False, False, False),
            ("nic_or_passport : VARCHAR", False, False, False),
            ("phone_primary : VARCHAR", False, False, False),
            ("email : VARCHAR(255)", False, False, False),
            ("city : VARCHAR(100)", False, False, False),
            ("status : VARCHAR(20)", False, False, False),
        ]),
        # 4. vehicles
        ("vehicles", 0.54, 0.72, 0.15, 0.22, "#15803d", [
            ("PK id : BIGINT", True, False, False),
            ("FK customer_id : BIGINT", False, True, False),
            ("UQ reg_number : VARCHAR(40)", False, False, True),
            ("chassis_number : VARCHAR", False, False, False),
            ("make : VARCHAR(100)", False, False, False),
            ("model : VARCHAR(100)", False, False, False),
            ("manufacture_year : INT", False, False, False),
            ("fuel_type : VARCHAR(30)", False, False, False),
        ]),
        # 5. company_profile
        ("company_profile", 0.71, 0.72, 0.14, 0.21, "#334155", [
            ("PK id : BIGINT", True, False, False),
            ("company_name : VARCHAR", False, False, False),
            ("tax_reg_no : VARCHAR", False, False, False),
            ("hotline : VARCHAR(30)", False, False, False),
            ("email : VARCHAR(255)", False, False, False),
            ("address : TEXT", False, False, False),
            ("default_vat_rate : FLOAT", False, False, False),
        ]),
        # 6. app_sessions
        ("app_sessions", 0.87, 0.72, 0.10, 0.21, "#1e40af", [
            ("PK id : BIGINT", True, False, False),
            ("FK user_id : BIGINT", False, True, False),
            ("token : VARCHAR(255)", False, False, True),
            ("ip_address : VARCHAR", False, False, False),
            ("expires_at : DATETIME", False, False, False),
        ]),
        # 7. insurance_plans
        ("insurance_plans", 0.03, 0.39, 0.13, 0.23, "#b45309", [
            ("PK id : BIGINT", True, False, False),
            ("UQ plan_code : VARCHAR(30)", False, False, True),
            ("name : VARCHAR(100)", False, False, False),
            ("coverage_limit : DECIMAL", False, False, False),
            ("deductible : DECIMAL", False, False, False),
            ("is_active : BOOLEAN", False, False, False),
        ]),
        # 8. vehicle_policies
        ("vehicle_policies", 0.18, 0.39, 0.14, 0.23, "#b45309", [
            ("PK id : BIGINT", True, False, False),
            ("FK vehicle_id : BIGINT", False, True, False),
            ("FK plan_id : BIGINT", False, True, False),
            ("UQ policy_no : VARCHAR(50)", False, False, True),
            ("start_date : DATE", False, False, False),
            ("end_date : DATE", False, False, False),
            ("coverage_limit : DECIMAL", False, False, False),
            ("deductible : DECIMAL", False, False, False),
            ("status : VARCHAR(20)", False, False, False),
        ]),
        # 9. vehicle_images
        ("vehicle_images", 0.37, 0.39, 0.14, 0.23, "#0284c7", [
            ("PK id : BIGINT", True, False, False),
            ("FK vehicle_id : BIGINT", False, True, False),
            ("storage_path : VARCHAR", False, False, False),
            ("image_hash_sha256 : CHAR(64)", False, False, False),
            ("mime_type : VARCHAR(50)", False, False, False),
            ("file_size_bytes : BIGINT", False, False, False),
            ("uploaded_at : DATETIME", False, False, False),
        ]),
        # 10. analyses
        ("analyses", 0.54, 0.39, 0.15, 0.24, "#0284c7", [
            ("PK id : BIGINT", True, False, False),
            ("UQ analysis_no : VARCHAR", False, False, True),
            ("FK vehicle_id : BIGINT", False, True, False),
            ("FK image_id : BIGINT", False, True, False),
            ("FK operator_id : BIGINT", False, True, False),
            ("has_vehicle : BOOLEAN", False, False, False),
            ("vehicle_confidence : FLOAT", False, False, False),
            ("subtotal_repair : DECIMAL", False, False, False),
            ("vat_amount : DECIMAL", False, False, False),
            ("net_payable : DECIMAL", False, False, False),
            ("status : VARCHAR(20)", False, False, False),
        ]),
        # 11. vehicle_inspection_notes
        ("vehicle_inspection_notes", 0.72, 0.39, 0.13, 0.23, "#0284c7", [
            ("PK id : BIGINT", True, False, False),
            ("FK analysis_id : BIGINT", False, True, False),
            ("FK author_id : BIGINT", False, True, False),
            ("note_category : VARCHAR", False, False, False),
            ("content : TEXT", False, False, False),
            ("created_at : DATETIME", False, False, False),
        ]),
        # 12. damage_pricing_catalog
        ("damage_pricing_catalog", 0.03, 0.05, 0.14, 0.24, "#0f766e", [
            ("PK id : BIGINT", True, False, False),
            ("damage_type : VARCHAR(50)", False, False, False),
            ("severity : VARCHAR(20)", False, False, False),
            ("default_labor_rate : DEC", False, False, False),
            ("default_part_cost : DEC", False, False, False),
            ("description : VARCHAR", False, False, False),
        ]),
        # 13. analysis_damages
        ("analysis_damages", 0.20, 0.05, 0.16, 0.25, "#0f766e", [
            ("PK id : BIGINT", True, False, False),
            ("FK analysis_id : BIGINT", False, True, False),
            ("damage_type : VARCHAR(50)", False, False, False),
            ("severity : VARCHAR(20)", False, False, False),
            ("confidence : FLOAT", False, False, False),
            ("passed_gate : BOOLEAN", False, False, False),
            ("polygon_points : JSON", False, False, False),
            ("estimated_cost : DECIMAL", False, False, False),
            ("is_accepted : BOOLEAN", False, False, False),
        ]),
        # 14. reports
        ("reports", 0.40, 0.05, 0.15, 0.25, "#7e22ce", [
            ("PK id : BIGINT", True, False, False),
            ("UQ report_no : VARCHAR", False, False, True),
            ("FK analysis_id : BIGINT", False, True, False),
            ("FK generated_by : BIGINT", False, True, False),
            ("pdf_file_path : VARCHAR", False, False, False),
            ("pdf_hash_sha256 : CHAR(64)", False, False, False),
            ("final_amount : DECIMAL", False, False, False),
            ("generated_at : DATETIME", False, False, False),
        ]),
        # 15. audit_logs
        ("audit_logs", 0.60, 0.05, 0.22, 0.25, "#334155", [
            ("PK id : BIGINT", True, False, False),
            ("FK actor_id : BIGINT", False, True, False),
            ("action : VARCHAR(60)", False, False, False),
            ("entity_name : VARCHAR(60)", False, False, False),
            ("entity_id : BIGINT", False, False, False),
            ("previous_state : JSON", False, False, False),
            ("new_state : JSON", False, False, False),
            ("ip_address : VARCHAR(45)", False, False, False),
            ("timestamp : DATETIME", False, False, False),
        ]),
    ]

    # Draw entity tables
    for name, x, y, w, h, hcolor, fields in tables_data:
        # Outer table card
        card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.005", ec="#1e293b", fc="#ffffff", lw=1.3)
        ax.add_patch(card)
        
        # Header banner
        header_h = 0.038
        hdr = patches.Rectangle((x, y + h - header_h), w, header_h, ec="#1e293b", fc=hcolor, lw=1.3)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - header_h/2, name, fontsize=9, fontweight='bold', color="#ffffff", ha='center', va='center')

        # Attributes list
        line_y = y + h - header_h - 0.022
        for col_name, is_pk, is_fk, is_uq in fields:
            # Color code keys
            if is_pk:
                ax.text(x + 0.006, line_y, "PK", fontsize=7, fontweight='bold', color="#b91c1c", va='center')
                attr_text = col_name.replace("PK ", "")
                ax.text(x + 0.024, line_y, attr_text, fontsize=7.2, fontweight='bold', color="#0f172a", va='center')
            elif is_fk:
                ax.text(x + 0.006, line_y, "FK", fontsize=7, fontweight='bold', color="#1d4ed8", va='center')
                attr_text = col_name.replace("FK ", "")
                ax.text(x + 0.024, line_y, attr_text, fontsize=7.2, color="#1e293b", va='center')
            elif is_uq:
                ax.text(x + 0.006, line_y, "UQ", fontsize=6.8, fontweight='bold', color="#d97706", va='center')
                attr_text = col_name.replace("UQ ", "")
                ax.text(x + 0.024, line_y, attr_text, fontsize=7.2, color="#1e293b", va='center')
            else:
                ax.text(x + 0.012, line_y, col_name, fontsize=7.2, color="#334155", va='center')
            line_y -= 0.020

    # Helper function for Crow's Foot relationship lines
    def draw_crows_foot(p1, p2, card1="1", card2="N", label="", color="#475569", ls="-"):
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, lw=1.4, ls=ls)
        # Cardinality tags
        ax.text(p1[0], p1[1], f" {card1} ", fontsize=7.5, fontweight='bold', color=color, bbox=dict(boxstyle="round,pad=0.1", fc="#ffffff", ec="none", alpha=0.85))
        ax.text(p2[0], p2[1], f" {card2} ", fontsize=7.5, fontweight='bold', color=color, bbox=dict(boxstyle="round,pad=0.1", fc="#ffffff", ec="none", alpha=0.85))
        if label:
            mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
            ax.text(mx, my, label, fontsize=6.8, color="#0f172a", ha='center', va='center', bbox=dict(boxstyle="round,pad=0.1", fc="#f8fafc", ec="#cbd5e1", lw=0.6))

    # Relationships (Crow's foot)
    # 1. roles -> users (1 : N)
    draw_crows_foot((0.16, 0.82), (0.18, 0.82), "1", "0..N", "authorizes", "#1e40af")
    
    # 2. customers -> users (0..1 : 0..1 optional portal account)
    draw_crows_foot((0.32, 0.82), (0.37, 0.82), "0..1", "0..1", "provisions", "#1e40af")

    # 3. customers -> vehicles (1 : N)
    draw_crows_foot((0.52, 0.82), (0.54, 0.82), "1", "1..N", "owns", "#15803d")

    # 4. users -> app_sessions (1 : N)
    draw_crows_foot((0.32, 0.90), (0.87, 0.90), "1", "0..N", "maintains session", "#1e40af", ls=":")

    # 5. vehicles -> vehicle_policies (1 : N)
    draw_crows_foot((0.58, 0.72), (0.28, 0.62), "1", "1..N", "insured by", "#b45309")

    # 6. insurance_plans -> vehicle_policies (1 : N)
    draw_crows_foot((0.16, 0.50), (0.18, 0.50), "1", "1..N", "defines", "#b45309")

    # 7. vehicles -> vehicle_images (1 : N)
    draw_crows_foot((0.58, 0.72), (0.44, 0.62), "1", "1..N", "contains", "#0284c7")

    # 8. vehicles -> analyses (1 : N)
    draw_crows_foot((0.61, 0.72), (0.61, 0.63), "1", "1..N", "inspected in", "#0284c7")

    # 9. vehicle_images -> analyses (1 : 1..N)
    draw_crows_foot((0.51, 0.50), (0.54, 0.50), "1", "1..N", "source photo", "#0284c7")

    # 10. analyses -> vehicle_inspection_notes (1 : N)
    draw_crows_foot((0.69, 0.50), (0.72, 0.50), "1", "0..N", "annotated by", "#0284c7")

    # 11. analyses -> analysis_damages (1 : N)
    draw_crows_foot((0.58, 0.39), (0.28, 0.30), "1", "0..N", "detects defects", "#0f766e")

    # 12. damage_pricing_catalog -> analysis_damages (1 : N optional lookup)
    draw_crows_foot((0.17, 0.17), (0.20, 0.17), "1", "0..N", "prices", "#0f766e")

    # 13. analyses -> reports (1 : 1..N)
    draw_crows_foot((0.61, 0.39), (0.47, 0.30), "1", "1..N", "publishes", "#7e22ce")

    # 14. users (operator) -> analyses (1 : N)
    draw_crows_foot((0.25, 0.72), (0.54, 0.55), "1", "1..N", "conducts", "#1e40af", ls=":")

    # 15. users (actor) -> audit_logs (1 : N)
    draw_crows_foot((0.25, 0.72), (0.65, 0.30), "1", "0..N", "audit tracks", "#334155", ls=":")

    # Legend Box in Top-Right
    leg_box = patches.FancyBboxPatch((0.84, 0.05), 0.14, 0.25, boxstyle="round,pad=0.008", ec="#475569", fc="#ffffff", lw=1.2)
    ax.add_patch(leg_box)
    leg_hdr = patches.Rectangle((0.84, 0.26), 0.14, 0.038, ec="#475569", fc="#334155", lw=1.2)
    ax.add_patch(leg_hdr)
    ax.text(0.91, 0.279, "ERD NOTATION LEGEND", fontsize=7.5, fontweight='bold', color="#ffffff", ha='center', va='center')

    leg_items = [
        ("PK", "#b91c1c", "Primary Key"),
        ("FK", "#1d4ed8", "Foreign Key"),
        ("UQ", "#d97706", "Unique Key"),
        ("1 : N", "#475569", "One-to-Many"),
        ("1 : 1", "#475569", "One-to-One"),
        ("0..1", "#475569", "Optional Mapping"),
        ("Table", "#0284c7", "Database Entity"),
    ]
    leg_y = 0.235
    for tag, col, desc in leg_items:
        ax.text(0.85, leg_y, tag, fontsize=7, fontweight='bold', color=col, va='center')
        ax.text(0.88, leg_y, desc, fontsize=7, color="#0f172a", va='center')
        leg_y -= 0.026

    # Bottom Title Note
    ax.text(0.50, 0.012, "Entity-Relationship Diagram (ERD) for Vehicle Damage Assessment Insurance ERP System (15 Normalized Relational Tables)",
            fontsize=9.5, fontweight='bold', color="#0f172a", ha='center', va='center')

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"High-fidelity ER Diagram successfully generated at: {output_path}")

if __name__ == "__main__":
    out_img = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\reports\uml_diagrams\er_diagram.png"
    draw_comprehensive_er_diagram(out_img)
