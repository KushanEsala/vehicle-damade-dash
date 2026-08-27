import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_perfect_er_diagram(output_path):
    # High resolution 16.5 x 11.5 inches at 300 DPI
    fig, ax = plt.subplots(figsize=(16.5, 11.5), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Subsystem background bounding regions
    regions = [
        # (x, y, w, h, label, bg_color, border_color)
        (0.015, 0.68, 0.32, 0.30, "USER & AUTHENTICATION GOVERNANCE", "#f8fafc", "#cbd5e1"),
        (0.350, 0.68, 0.635, 0.30, "CUSTOMER & VEHICLE ASSET MANAGEMENT", "#f0fdf4", "#bbf7d0"),
        (0.015, 0.35, 0.32, 0.30, "INSURANCE POLICY & UNDERWRITING", "#fefce8", "#fef08a"),
        (0.350, 0.35, 0.635, 0.30, "VEHICLE INSPECTION & AI ANALYSIS PIPELINE", "#f0f9ff", "#bae6fd"),
        (0.015, 0.02, 0.970, 0.30, "DAMAGE COSTING, REPORT GENERATION & SYSTEM AUDITING", "#faf5ff", "#e9d5ff"),
    ]

    for rx, ry, rw, rh, rlabel, rbg, rborder in regions:
        region_rect = patches.FancyBboxPatch(
            (rx, ry), rw, rh, boxstyle="round,pad=0.01", ec=rborder, fc=rbg, lw=1.2, ls="--"
        )
        ax.add_patch(region_rect)
        ax.text(rx + 0.012, ry + rh - 0.018, rlabel, fontsize=8.5, fontweight='bold', color="#64748b", va='top')

    # Table specifications: (name, x, y, w, h, header_color, fields)
    tables = {
        "roles": (0.025, 0.705, 0.125, 0.22, "#1e40af", [
            ("PK id : BIGINT", True, False, False),
            ("UQ code : VARCHAR(30)", False, False, True),
            ("name : VARCHAR(60)", False, False, False),
            ("description : VARCHAR", False, False, False),
            ("created_at : DATETIME", False, False, False),
        ]),
        "users": (0.175, 0.705, 0.145, 0.24, "#1e40af", [
            ("PK id : BIGINT", True, False, False),
            ("FK role_id : BIGINT", False, True, False),
            ("FK customer_id : BIGINT", False, True, False),
            ("UQ username : VARCHAR(80)", False, False, True),
            ("email : VARCHAR(255)", False, False, False),
            ("password_hash : VARCHAR", False, False, False),
            ("is_active : BOOLEAN", False, False, False),
        ]),
        "customers": (0.365, 0.705, 0.145, 0.24, "#15803d", [
            ("PK id : BIGINT", True, False, False),
            ("UQ customer_code : VARCHAR", False, False, True),
            ("full_name : VARCHAR(150)", False, False, False),
            ("nic_or_passport : VARCHAR", False, False, False),
            ("phone_primary : VARCHAR", False, False, False),
            ("email : VARCHAR(255)", False, False, False),
            ("city : VARCHAR(100)", False, False, False),
            ("status : VARCHAR(20)", False, False, False),
        ]),
        "vehicles": (0.535, 0.705, 0.150, 0.24, "#15803d", [
            ("PK id : BIGINT", True, False, False),
            ("FK customer_id : BIGINT", False, True, False),
            ("UQ reg_number : VARCHAR(40)", False, False, True),
            ("chassis_number : VARCHAR", False, False, False),
            ("make : VARCHAR(100)", False, False, False),
            ("model : VARCHAR(100)", False, False, False),
            ("year : INT", False, False, False),
            ("fuel_type : VARCHAR(30)", False, False, False),
        ]),
        "company_profile": (0.710, 0.705, 0.135, 0.22, "#334155", [
            ("PK id : BIGINT", True, False, False),
            ("company_name : VARCHAR", False, False, False),
            ("tax_reg_no : VARCHAR", False, False, False),
            ("hotline : VARCHAR(30)", False, False, False),
            ("email : VARCHAR(255)", False, False, False),
            ("address : TEXT", False, False, False),
            ("default_vat_rate : FLOAT", False, False, False),
        ]),
        "app_sessions": (0.025, 0.375, 0.130, 0.22, "#1e40af", [
            ("PK id : BIGINT", True, False, False),
            ("FK user_id : BIGINT", False, True, False),
            ("UQ token : VARCHAR(255)", False, False, True),
            ("ip_address : VARCHAR(45)", False, False, False),
            ("expires_at : DATETIME", False, False, False),
            ("created_at : DATETIME", False, False, False),
        ]),
        "insurance_plans": (0.175, 0.375, 0.145, 0.22, "#b45309", [
            ("PK id : BIGINT", True, False, False),
            ("UQ plan_code : VARCHAR(30)", False, False, True),
            ("name : VARCHAR(100)", False, False, False),
            ("coverage_limit : DECIMAL", False, False, False),
            ("deductible : DECIMAL", False, False, False),
            ("is_active : BOOLEAN", False, False, False),
        ]),
        "vehicle_policies": (0.365, 0.375, 0.145, 0.24, "#b45309", [
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
        "vehicle_images": (0.535, 0.375, 0.145, 0.24, "#0284c7", [
            ("PK id : BIGINT", True, False, False),
            ("FK vehicle_id : BIGINT", False, True, False),
            ("storage_path : VARCHAR", False, False, False),
            ("image_hash_sha256 : CHAR(64)", False, False, False),
            ("mime_type : VARCHAR(50)", False, False, False),
            ("file_size_bytes : BIGINT", False, False, False),
            ("uploaded_at : DATETIME", False, False, False),
        ]),
        "analyses": (0.705, 0.375, 0.145, 0.25, "#0284c7", [
            ("PK id : BIGINT", True, False, False),
            ("UQ analysis_no : VARCHAR", False, False, True),
            ("FK vehicle_id : BIGINT", False, True, False),
            ("FK image_id : BIGINT", False, True, False),
            ("FK operator_id : BIGINT", False, True, False),
            ("has_vehicle : BOOLEAN", False, False, False),
            ("subtotal_repair : DECIMAL", False, False, False),
            ("vat_amount : DECIMAL", False, False, False),
            ("net_payable : DECIMAL", False, False, False),
            ("status : VARCHAR(20)", False, False, False),
        ]),
        "vehicle_inspection_notes": (0.865, 0.375, 0.110, 0.22, "#0284c7", [
            ("PK id : BIGINT", True, False, False),
            ("FK analysis_id : BIGINT", False, True, False),
            ("FK author_id : BIGINT", False, True, False),
            ("note_type : VARCHAR", False, False, False),
            ("content : TEXT", False, False, False),
            ("created_at : DATETIME", False, False, False),
        ]),
        "damage_pricing_catalog": (0.025, 0.045, 0.145, 0.23, "#0f766e", [
            ("PK id : BIGINT", True, False, False),
            ("damage_type : VARCHAR(50)", False, False, False),
            ("severity : VARCHAR(20)", False, False, False),
            ("default_labor_rate : DEC", False, False, False),
            ("default_part_cost : DEC", False, False, False),
            ("description : VARCHAR", False, False, False),
        ]),
        "analysis_damages": (0.190, 0.045, 0.165, 0.25, "#0f766e", [
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
        "reports": (0.380, 0.045, 0.155, 0.25, "#7e22ce", [
            ("PK id : BIGINT", True, False, False),
            ("UQ report_no : VARCHAR", False, False, True),
            ("FK analysis_id : BIGINT", False, True, False),
            ("FK generated_by : BIGINT", False, True, False),
            ("pdf_file_path : VARCHAR", False, False, False),
            ("pdf_hash_sha256 : CHAR(64)", False, False, False),
            ("final_amount : DECIMAL", False, False, False),
            ("generated_at : DATETIME", False, False, False),
        ]),
        "audit_logs": (0.560, 0.045, 0.230, 0.25, "#334155", [
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
    }

    # Draw all entity boxes
    for name, (x, y, w, h, hcolor, fields) in tables.items():
        card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004", ec="#1e293b", fc="#ffffff", lw=1.3)
        ax.add_patch(card)
        
        header_h = 0.036
        hdr = patches.Rectangle((x, y + h - header_h), w, header_h, ec="#1e293b", fc=hcolor, lw=1.3)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - header_h/2, name, fontsize=8.8, fontweight='bold', color="#ffffff", ha='center', va='center')

        line_y = y + h - header_h - 0.020
        for col_name, is_pk, is_fk, is_uq in fields:
            if is_pk:
                ax.text(x + 0.005, line_y, "PK", fontsize=6.8, fontweight='bold', color="#b91c1c", va='center')
                attr_text = col_name.replace("PK ", "")
                ax.text(x + 0.022, line_y, attr_text, fontsize=7.0, fontweight='bold', color="#0f172a", va='center')
            elif is_fk:
                ax.text(x + 0.005, line_y, "FK", fontsize=6.8, fontweight='bold', color="#1d4ed8", va='center')
                attr_text = col_name.replace("FK ", "")
                ax.text(x + 0.022, line_y, attr_text, fontsize=7.0, color="#1e293b", va='center')
            elif is_uq:
                ax.text(x + 0.005, line_y, "UQ", fontsize=6.5, fontweight='bold', color="#d97706", va='center')
                attr_text = col_name.replace("UQ ", "")
                ax.text(x + 0.022, line_y, attr_text, fontsize=7.0, color="#1e293b", va='center')
            else:
                ax.text(x + 0.010, line_y, col_name, fontsize=7.0, color="#334155", va='center')
            line_y -= 0.019

    # Draw Orthogonal Polyline Relationships
    def draw_orthogonal_relation(points, card1="1", card2="N", label="", color="#475569", ls="-", label_offset=(0, 0)):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        ax.plot(xs, ys, color=color, lw=1.3, ls=ls)
        
        # Cardinality badges at endpoints
        p_start = points[0]
        p_end = points[-1]
        ax.text(p_start[0], p_start[1], f" {card1} ", fontsize=7.0, fontweight='bold', color=color,
                ha='center', va='center', bbox=dict(boxstyle="round,pad=0.1", fc="#ffffff", ec=color, lw=0.6))
        ax.text(p_end[0], p_end[1], f" {card2} ", fontsize=7.0, fontweight='bold', color=color,
                ha='center', va='center', bbox=dict(boxstyle="round,pad=0.1", fc="#ffffff", ec=color, lw=0.6))
        
        # Label at midpoint segment
        if label:
            mid_idx = len(points) // 2
            p_m1 = points[mid_idx - 1]
            p_m2 = points[mid_idx]
            mx, my = (p_m1[0] + p_m2[0]) / 2 + label_offset[0], (p_m1[1] + p_m2[1]) / 2 + label_offset[1]
            ax.text(mx, my, label, fontsize=6.8, color="#0f172a", ha='center', va='center',
                    bbox=dict(boxstyle="round,pad=0.12", fc="#f8fafc", ec="#94a3b8", lw=0.7))

    # 1. roles -> users (1 : N)
    draw_orthogonal_relation([(0.150, 0.81), (0.175, 0.81)], "1", "0..N", "authorizes", "#1e40af")

    # 2. users -> app_sessions (1 : N)
    draw_orthogonal_relation([(0.20, 0.705), (0.20, 0.63), (0.09, 0.63), (0.09, 0.595)], "1", "0..N", "session", "#1e40af")

    # 3. customers -> users (0..1 : 0..1 optional portal account)
    draw_orthogonal_relation([(0.365, 0.85), (0.320, 0.85)], "0..1", "0..1", "provisions", "#1e40af")

    # 4. customers -> vehicles (1 : N)
    draw_orthogonal_relation([(0.510, 0.81), (0.535, 0.81)], "1", "1..N", "owns", "#15803d")

    # 5. insurance_plans -> vehicle_policies (1 : N)
    draw_orthogonal_relation([(0.320, 0.48), (0.365, 0.48)], "1", "1..N", "defines", "#b45309")

    # 6. vehicles -> vehicle_policies (1 : N)
    draw_orthogonal_relation([(0.57, 0.705), (0.57, 0.64), (0.44, 0.64), (0.44, 0.615)], "1", "1..N", "insured", "#b45309")

    # 7. vehicles -> vehicle_images (1 : N)
    draw_orthogonal_relation([(0.61, 0.705), (0.61, 0.615)], "1", "1..N", "contains", "#0284c7")

    # 8. vehicles -> analyses (1 : N)
    draw_orthogonal_relation([(0.66, 0.705), (0.66, 0.65), (0.75, 0.65), (0.75, 0.625)], "1", "1..N", "inspected", "#0284c7")

    # 9. vehicle_images -> analyses (1 : N)
    draw_orthogonal_relation([(0.680, 0.48), (0.705, 0.48)], "1", "1..N", "source", "#0284c7")

    # 10. analyses -> vehicle_inspection_notes (1 : N)
    draw_orthogonal_relation([(0.850, 0.48), (0.865, 0.48)], "1", "0..N", "remarks", "#0284c7")

    # 11. damage_pricing_catalog -> analysis_damages (1 : N lookup)
    draw_orthogonal_relation([(0.170, 0.16), (0.190, 0.16)], "1", "0..N", "pricing", "#0f766e")

    # 12. analyses -> analysis_damages (1 : N)
    draw_orthogonal_relation([(0.73, 0.375), (0.73, 0.32), (0.27, 0.32), (0.27, 0.295)], "1", "0..N", "detects defects", "#0f766e")

    # 13. analyses -> reports (1 : 1..N)
    draw_orthogonal_relation([(0.78, 0.375), (0.78, 0.33), (0.46, 0.33), (0.46, 0.295)], "1", "1..N", "publishes", "#7e22ce")

    # 14. analyses -> audit_logs (1 : N)
    draw_orthogonal_relation([(0.82, 0.375), (0.82, 0.32), (0.67, 0.32), (0.67, 0.295)], "1", "0..N", "audit log", "#334155")

    # Legend Box in Bottom-Right
    leg_box = patches.FancyBboxPatch((0.805, 0.045), 0.175, 0.25, boxstyle="round,pad=0.008", ec="#475569", fc="#ffffff", lw=1.2)
    ax.add_patch(leg_box)
    leg_hdr = patches.Rectangle((0.805, 0.255), 0.175, 0.040, ec="#475569", fc="#334155", lw=1.2)
    ax.add_patch(leg_hdr)
    ax.text(0.892, 0.275, "ERD NOTATION LEGEND", fontsize=7.5, fontweight='bold', color="#ffffff", ha='center', va='center')

    leg_items = [
        ("PK", "#b91c1c", "Primary Key (Unique Record ID)"),
        ("FK", "#1d4ed8", "Foreign Key (Referential Link)"),
        ("UQ", "#d97706", "Unique Constraint Column"),
        ("1 : N", "#475569", "One-to-Many Relationship"),
        ("1 : 1", "#475569", "One-to-One Relationship"),
        ("0..1", "#475569", "Optional Zero-or-One Mapping"),
        ("Entity", "#0284c7", "Database Table (3NF Schema)"),
    ]
    leg_y = 0.230
    for tag, col, desc in leg_items:
        ax.text(0.815, leg_y, tag, fontsize=6.8, fontweight='bold', color=col, va='center')
        ax.text(0.855, leg_y, desc, fontsize=6.8, color="#0f172a", va='center')
        leg_y -= 0.027

    # Bottom Title Note
    ax.text(0.50, 0.008, "Figure 4.3: Entity-Relationship Diagram (ERD) - 15 Normalized Database Entities, Attributes, Keys, and Relational Cardinalities (Database Model, Not UML)",
            fontsize=9.2, fontweight='bold', color="#0f172a", ha='center', va='center')

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Perfect ER Diagram successfully saved at: {output_path}")

if __name__ == "__main__":
    out_img = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\reports\uml_diagrams\er_diagram.png"
    draw_perfect_er_diagram(out_img)
