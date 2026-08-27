import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

def draw_real_eer_diagram(output_path):
    # Professional Ultra-High-Resolution Canvas (18.5 x 13.0 inches at 300 DPI)
    fig, ax = plt.subplots(figsize=(18.5, 13.0), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Canvas Background
    fig.patch.set_facecolor('#f8fafc')
    ax.set_facecolor('#f8fafc')

    # =========================================================================
    # 1. SUBSYSTEM BACKGROUND CLUSTERS (EER Subject Areas)
    # =========================================================================
    subsystems = [
        # (x, y, w, h, title, fill_color, stroke_color)
        (1.5, 66.0, 31.0, 31.5, "1. USER ACCESS & IDENTITY GOVERNANCE", "#f1f5f9", "#cbd5e1"),
        (33.5, 66.0, 65.0, 31.5, "2. CUSTOMER & VEHICLE ASSET MANAGEMENT (FLEET REGISTRY)", "#f0fdf4", "#bbf7d0"),
        (1.5, 34.0, 31.0, 30.5, "3. INSURANCE POLICY & UNDERWRITING", "#fefce8", "#fef08a"),
        (33.5, 34.0, 65.0, 30.5, "4. AI DAMAGE INSPECTION & INFERENCE WORKSPACE", "#f0f9ff", "#bae6fd"),
        (1.5, 2.0, 97.0, 30.5, "5. DAMAGE COSTING, CLAIM REPORTING & SYSTEM AUDIT ENGINE", "#faf5ff", "#e9d5ff"),
    ]

    for sx, sy, sw, sh, stitle, sbg, sstroke in subsystems:
        # Cluster background box
        box = patches.FancyBboxPatch((sx, sy), sw, sh, boxstyle="round,pad=0.5", ec=sstroke, fc=sbg, lw=1.5, ls="--")
        ax.add_patch(box)
        # Cluster title pill
        pill = patches.FancyBboxPatch((sx + 1.2, sy + sh - 2.8), len(stitle)*0.48 + 2.0, 2.2,
                                     boxstyle="round,pad=0.2", ec=sstroke, fc="#ffffff", lw=1.0)
        ax.add_patch(pill)
        ax.text(sx + 2.2, sy + sh - 1.7, stitle, fontsize=8.5, fontweight='bold', color="#334155", va='center')

    # =========================================================================
    # 2. ENTITY TABLE CARDS (With Real EER Attribute Compartments)
    # =========================================================================
    # Entity definition structure:
    # key: (x, y, w, h, header_color, entity_type, [ (tag, col_name, data_type, null_str) ])
    # entity_type: 'STRONG', 'WEAK'
    tables = {
        "roles": (2.8, 70.0, 13.5, 23.5, "#1e40af", "STRONG", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("UQ", "code", "VARCHAR(30)", "NN"),
            (" ", "name", "VARCHAR(60)", "NN"),
            (" ", "description", "VARCHAR(255)", "NULL"),
            (" ", "created_at", "DATETIME", "NN"),
        ]),
        "users": (17.5, 68.0, 14.0, 26.5, "#1e40af", "STRONG", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("FK", "role_id", "BIGINT(20)", "NN"),
            ("FK", "customer_id", "BIGINT(20)", "NULL"),
            ("UQ", "username", "VARCHAR(80)", "NN"),
            ("UQ", "email", "VARCHAR(255)", "NN"),
            (" ", "password_hash", "VARCHAR(255)", "NN"),
            (" ", "is_active", "TINYINT(1)", "NN"),
            (" ", "failed_logins", "INT(11)", "NN"),
            (" ", "created_at", "DATETIME", "NN"),
        ]),
        "customers": (35.0, 68.0, 14.5, 26.5, "#15803d", "STRONG", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("UQ", "customer_code", "VARCHAR(30)", "NN"),
            (" ", "full_name", "VARCHAR(150)", "NN"),
            ("UQ", "nic_or_passport", "VARCHAR(60)", "NULL"),
            (" ", "phone_primary", "VARCHAR(30)", "NN"),
            (" ", "email", "VARCHAR(255)", "NN"),
            (" ", "city", "VARCHAR(100)", "NN"),
            (" ", "status", "VARCHAR(20)", "NN"),
            ("FK", "created_by", "BIGINT(20)", "NULL"),
        ]),
        "vehicles": (51.0, 68.0, 14.5, 26.5, "#15803d", "STRONG", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("FK", "customer_id", "BIGINT(20)", "NN"),
            ("UQ", "reg_number", "VARCHAR(40)", "NN"),
            (" ", "chassis_number", "VARCHAR(80)", "NULL"),
            (" ", "make", "VARCHAR(100)", "NN"),
            (" ", "model", "VARCHAR(100)", "NN"),
            (" ", "manufacture_year", "INT(11)", "NULL"),
            (" ", "fuel_type", "VARCHAR(30)", "NN"),
            (" ", "created_at", "DATETIME", "NN"),
        ]),
        "company_profile": (67.0, 71.0, 13.5, 23.0, "#334155", "STRONG", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            (" ", "company_name", "VARCHAR(150)", "NN"),
            (" ", "tax_reg_no", "VARCHAR(50)", "NN"),
            (" ", "hotline", "VARCHAR(30)", "NN"),
            (" ", "email", "VARCHAR(255)", "NN"),
            (" ", "default_vat_rate", "FLOAT", "NN"),
            (" ", "address", "TEXT", "NULL"),
        ]),
        "app_sessions": (2.8, 36.5, 13.5, 24.5, "#1e40af", "WEAK", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("FK", "user_id", "BIGINT(20)", "NN"),
            ("UQ", "token", "VARCHAR(255)", "NN"),
            (" ", "ip_address", "VARCHAR(45)", "NN"),
            (" ", "expires_at", "DATETIME", "NN"),
            (" ", "created_at", "DATETIME", "NN"),
        ]),
        "insurance_plans": (17.5, 36.5, 14.0, 24.5, "#b45309", "STRONG", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("UQ", "plan_code", "VARCHAR(30)", "NN"),
            (" ", "name", "VARCHAR(100)", "NN"),
            (" ", "coverage_limit", "DECIMAL(12,2)", "NN"),
            (" ", "deductible", "DECIMAL(10,2)", "NN"),
            (" ", "is_active", "TINYINT(1)", "NN"),
        ]),
        "vehicle_policies": (35.0, 36.5, 14.5, 25.5, "#b45309", "STRONG", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("FK", "vehicle_id", "BIGINT(20)", "NN"),
            ("FK", "plan_id", "BIGINT(20)", "NN"),
            ("UQ", "policy_no", "VARCHAR(50)", "NN"),
            (" ", "start_date", "DATE", "NN"),
            (" ", "end_date", "DATE", "NN"),
            (" ", "coverage_limit", "DECIMAL(12,2)", "NN"),
            (" ", "deductible", "DECIMAL(10,2)", "NN"),
            (" ", "status", "VARCHAR(20)", "NN"),
        ]),
        "vehicle_images": (51.0, 36.5, 14.5, 25.5, "#0284c7", "WEAK", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("FK", "vehicle_id", "BIGINT(20)", "NN"),
            (" ", "storage_path", "VARCHAR(500)", "NN"),
            (" ", "image_hash_sha256", "CHAR(64)", "NN"),
            (" ", "mime_type", "VARCHAR(50)", "NN"),
            (" ", "file_size_bytes", "BIGINT(20)", "NN"),
            (" ", "uploaded_at", "DATETIME", "NN"),
        ]),
        "analyses": (67.0, 36.0, 15.0, 26.5, "#0284c7", "STRONG", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("UQ", "analysis_no", "VARCHAR(40)", "NN"),
            ("FK", "vehicle_id", "BIGINT(20)", "NN"),
            ("FK", "image_id", "BIGINT(20)", "NN"),
            ("FK", "operator_id", "BIGINT(20)", "NN"),
            (" ", "has_vehicle", "TINYINT(1)", "NN"),
            (" ", "subtotal_repair", "DECIMAL(12,2)", "NN"),
            (" ", "vat_amount", "DECIMAL(10,2)", "NN"),
            (" ", "net_payable", "DECIMAL(12,2)", "NN"),
            (" ", "status", "VARCHAR(20)", "NN"),
        ]),
        "vehicle_inspection_notes": (83.5, 36.5, 14.0, 24.5, "#0284c7", "WEAK", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("FK", "analysis_id", "BIGINT(20)", "NN"),
            ("FK", "author_id", "BIGINT(20)", "NN"),
            (" ", "note_type", "VARCHAR(40)", "NN"),
            (" ", "content", "TEXT", "NN"),
            (" ", "created_at", "DATETIME", "NN"),
        ]),
        "damage_pricing_catalog": (2.8, 4.5, 14.5, 24.5, "#0f766e", "STRONG", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            (" ", "damage_type", "VARCHAR(50)", "NN"),
            (" ", "severity", "VARCHAR(20)", "NN"),
            (" ", "default_labor_rate", "DECIMAL(10,2)", "NN"),
            (" ", "default_part_cost", "DECIMAL(10,2)", "NN"),
            (" ", "description", "VARCHAR(255)", "NULL"),
        ]),
        "analysis_damages": (19.0, 4.5, 15.5, 25.5, "#0f766e", "WEAK", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("FK", "analysis_id", "BIGINT(20)", "NN"),
            (" ", "damage_type", "VARCHAR(50)", "NN"),
            (" ", "severity", "VARCHAR(20)", "NN"),
            (" ", "confidence", "FLOAT", "NN"),
            (" ", "passed_gate", "TINYINT(1)", "NN"),
            (" ", "polygon_points", "JSON", "NULL"),
            (" ", "estimated_cost", "DECIMAL(10,2)", "NN"),
            (" ", "is_accepted", "TINYINT(1)", "NN"),
        ]),
        "reports": (36.0, 4.5, 15.5, 25.5, "#7e22ce", "WEAK", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("UQ", "report_no", "VARCHAR(50)", "NN"),
            ("FK", "analysis_id", "BIGINT(20)", "NN"),
            ("FK", "generated_by", "BIGINT(20)", "NN"),
            (" ", "pdf_file_path", "VARCHAR(500)", "NN"),
            (" ", "pdf_hash_sha256", "CHAR(64)", "NN"),
            (" ", "final_amount", "DECIMAL(12,2)", "NN"),
            (" ", "generated_at", "DATETIME", "NN"),
        ]),
        "audit_logs": (53.0, 4.5, 20.0, 25.5, "#334155", "WEAK", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("FK", "actor_id", "BIGINT(20)", "NULL"),
            (" ", "action", "VARCHAR(60)", "NN"),
            (" ", "entity_name", "VARCHAR(60)", "NN"),
            (" ", "entity_id", "BIGINT(20)", "NULL"),
            (" ", "previous_state", "JSON", "NULL"),
            (" ", "new_state", "JSON", "NULL"),
            (" ", "ip_address", "VARCHAR(45)", "NN"),
            (" ", "timestamp", "DATETIME", "NN"),
        ]),
    }

    # =========================================================================
    # 3. DRAW TABLES (Workbench / EER Entity Style)
    # =========================================================================
    for name, (tx, ty, tw, th, tcolor, etype, attrs) in tables.items():
        # Outer Card with subtle shadow
        shadow = patches.FancyBboxPatch((tx + 0.3, ty - 0.3), tw, th, boxstyle="round,pad=0.2", ec="none", fc="#e2e8f0", alpha=0.6)
        ax.add_patch(shadow)

        # Entity Box (Double border for Weak Entity if applicable)
        card_fc = "#ffffff"
        card_ec = "#1e293b" if etype == "STRONG" else "#475569"
        card = patches.FancyBboxPatch((tx, ty), tw, th, boxstyle="round,pad=0.1", ec=card_ec, fc=card_fc, lw=1.4)
        ax.add_patch(card)

        if etype == "WEAK":
            # Inner border for weak entity formal EER representation
            inner_card = patches.FancyBboxPatch((tx + 0.25, ty + 0.25), tw - 0.5, th - 0.5,
                                               boxstyle="round,pad=0.05", ec=card_ec, fc="none", lw=0.7, ls=":")
            ax.add_patch(inner_card)

        # Table Header Bar
        header_h = 3.6
        header_rect = patches.Rectangle((tx, ty + th - header_h), tw, header_h, ec=card_ec, fc=tcolor, lw=1.4)
        ax.add_patch(header_rect)

        # Header Title & Type Tag
        ax.text(tx + 0.6, ty + th - 1.8, name, fontsize=8.5, fontweight='bold', color="#ffffff", va='center')
        type_tag = "[Strong]" if etype == "STRONG" else "[Weak]"
        ax.text(tx + tw - 0.6, ty + th - 1.8, type_tag, fontsize=6.5, color="#e0e7ff", ha='right', va='center')

        # Attribute Rows with Zebra Striping
        row_h = (th - header_h - 0.8) / max(len(attrs), 1)
        curr_y = ty + th - header_h - 0.4

        for idx, (tag, col_name, dtype, null_str) in enumerate(attrs):
            row_y = curr_y - (idx + 1) * row_h + row_h/2
            
            # Subtle row zebra background
            if idx % 2 == 1:
                row_bg = patches.Rectangle((tx + 0.1, curr_y - (idx + 1) * row_h), tw - 0.2, row_h, ec="none", fc="#f8fafc")
                ax.add_patch(row_bg)

            # Key Badge (PK/FK/UQ)
            if tag == "PK":
                pk_badge = patches.FancyBboxPatch((tx + 0.4, row_y - 0.8), 1.6, 1.6, boxstyle="round,pad=0.05", ec="#b91c1c", fc="#fee2e2", lw=0.8)
                ax.add_patch(pk_badge)
                ax.text(tx + 1.2, row_y, "PK", fontsize=5.8, fontweight='bold', color="#b91c1c", ha='center', va='center')
            elif tag == "FK":
                fk_badge = patches.FancyBboxPatch((tx + 0.4, row_y - 0.8), 1.6, 1.6, boxstyle="round,pad=0.05", ec="#1d4ed8", fc="#dbeafe", lw=0.8)
                ax.add_patch(fk_badge)
                ax.text(tx + 1.2, row_y, "FK", fontsize=5.8, fontweight='bold', color="#1d4ed8", ha='center', va='center')
            elif tag == "UQ":
                uq_badge = patches.FancyBboxPatch((tx + 0.4, row_y - 0.8), 1.6, 1.6, boxstyle="round,pad=0.05", ec="#d97706", fc="#fef3c7", lw=0.8)
                ax.add_patch(uq_badge)
                ax.text(tx + 1.2, row_y, "UQ", fontsize=5.5, fontweight='bold', color="#b45309", ha='center', va='center')
            else:
                ax.plot(tx + 1.2, row_y, marker='o', markersize=2.5, color="#94a3b8")

            # Column Name
            name_weight = 'bold' if tag in ["PK", "UQ"] else 'normal'
            name_color = "#0f172a" if tag != "FK" else "#1e3a8a"
            ax.text(tx + 2.3, row_y, col_name, fontsize=6.8, fontweight=name_weight, color=name_color, va='center')

            # Data Type & Nullability (Right Aligned in Monospace style)
            ax.text(tx + tw - 0.5, row_y, f"{dtype} {null_str}", fontsize=5.8, color="#64748b", ha='right', va='center')

    # =========================================================================
    # 4. EER SPECIALIZATION / GENERALIZATION HIERARCHIES (Inheritance Circles)
    # =========================================================================
    # A. Specialization: User Hierarchy (users -> Admin, Assessor, Policyholder)
    # Draw Specialization circle '(d)' below users
    spec_cx, spec_cy = 24.5, 65.5
    circle_d = patches.Circle((spec_cx, spec_cy), 1.1, ec="#1e40af", fc="#eff6ff", lw=1.2)
    ax.add_patch(circle_d)
    ax.text(spec_cx, spec_cy, "d", fontsize=8, fontweight='bold', color="#1e40af", ha='center', va='center')

    # Superclass line from users
    ax.plot([24.5, 24.5], [68.0, spec_cy + 1.1], color="#1e40af", lw=1.3)
    # Specialization Subclasses
    subclasses = [
        ("Admin User", 18.0, 62.8),
        ("Claims Assessor", 24.5, 62.8),
        ("Policyholder", 31.0, 62.8),
    ]
    for sub_name, sx, sy in subclasses:
        ax.plot([spec_cx, sx], [spec_cy - 1.1, sy + 1.2], color="#1e40af", lw=1.0)
        sub_card = patches.FancyBboxPatch((sx - 2.8, sy - 0.6), 5.6, 1.8, boxstyle="round,pad=0.1", ec="#3b82f6", fc="#ffffff", lw=0.9)
        ax.add_patch(sub_card)
        ax.text(sx, sy + 0.3, sub_name, fontsize=5.8, fontweight='bold', color="#1e40af", ha='center', va='center')

    # B. Specialization: Damage Classes Hierarchy (analysis_damages -> 7 Subclasses)
    # Draw Specialization circle '(d)' to the right of analysis_damages
    dmg_cx, dmg_cy = 35.0, 17.0
    circle_dmg = patches.Circle((dmg_cx, dmg_cy), 1.1, ec="#0f766e", fc="#f0fdfa", lw=1.2)
    ax.add_patch(circle_dmg)
    ax.text(dmg_cx, dmg_cy, "d", fontsize=8, fontweight='bold', color="#0f766e", ha='center', va='center')

    ax.plot([34.5, dmg_cx - 1.1], [17.0, dmg_cy], color="#0f766e", lw=1.3)
    dmg_subclasses = ["Scratch", "Dent", "Tear", "Broken Lamp", "Broken Glass", "Puncture", "Missing Part"]
    for d_idx, d_name in enumerate(dmg_subclasses):
        dy = 28.5 - d_idx * 3.4
        # connecting elbow
        ax.plot([dmg_cx + 1.1, 37.0, 37.0, 37.5], [dmg_cy, dmg_cy, dy + 0.5, dy + 0.5], color="#0f766e", lw=0.8)
        d_pill = patches.FancyBboxPatch((37.5, dy - 0.5), 5.5, 2.0, boxstyle="round,pad=0.1", ec="#0d9488", fc="#ffffff", lw=0.8)
        ax.add_patch(d_pill)
        ax.text(40.25, dy + 0.5, f"is-a: {d_name}", fontsize=5.5, fontweight='bold', color="#0f766e", ha='center', va='center')

    # =========================================================================
    # 5. AUTHENTIC CROW'S FOOT RELATIONSHIP ROUTING & NOTATION
    # =========================================================================
    # Helper to draw genuine Crow's Foot forks and double bars
    def draw_crows_foot_edge(points, card_start="1", card_end="N", label="", color="#475569", ls="-", label_offset=(0,0)):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        ax.plot(xs, ys, color=color, lw=1.4, ls=ls)

        # 1. Start Symbol (usually 1 or 0..1)
        p0 = points[0]
        p1 = points[1]
        # Unit direction vector
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        dist = (dx**2 + dy**2)**0.5
        if dist > 0:
            ux, uy = dx/dist, dy/dist
            # Perpendicular vector
            vx, vy = -uy, ux
            # Draw double bars for Mandatory One (||)
            if card_start == "1":
                b1_x, b1_y = p0[0] + ux*1.0, p0[1] + uy*1.0
                b2_x, b2_y = p0[0] + ux*1.8, p0[1] + uy*1.8
                ax.plot([b1_x - vx*0.8, b1_x + vx*0.8], [b1_y - vy*0.8, b1_y + vy*0.8], color=color, lw=1.5)
                ax.plot([b2_x - vx*0.8, b2_x + vx*0.8], [b2_y - vy*0.8, b2_y + vy*0.8], color=color, lw=1.5)
            elif card_start == "0..1":
                # Circle and bar (o|)
                c_x, c_y = p0[0] + ux*1.2, p0[1] + uy*1.2
                circ = patches.Circle((c_x, c_y), 0.6, ec=color, fc="#ffffff", lw=1.2)
                ax.add_patch(circ)
                b_x, b_y = p0[0] + ux*2.2, p0[1] + uy*2.2
                ax.plot([b_x - vx*0.8, b_x + vx*0.8], [b_y - vy*0.8, b_y + vy*0.8], color=color, lw=1.5)

        # 2. End Symbol (usually Many / Crow's foot or One)
        pn = points[-1]
        pn_prev = points[-2]
        edx, edy = pn_prev[0] - pn[0], pn_prev[1] - pn[1]
        edist = (edx**2 + edy**2)**0.5
        if edist > 0:
            eux, euy = edx/edist, edy/edist
            evx, evy = -euy, eux
            if "N" in card_end:
                # Authentic Crow's Foot Fork (3 prongs)
                fork_base_x, fork_base_y = pn[0] + eux*2.0, pn[1] + euy*2.0
                ax.plot([pn[0], fork_base_x - evx*1.1], [pn[1], fork_base_y - evy*1.1], color=color, lw=1.5)
                ax.plot([pn[0], fork_base_x], [pn[1], fork_base_y], color=color, lw=1.5)
                ax.plot([pn[0], fork_base_x + evx*1.1], [pn[1], fork_base_y + evy*1.1], color=color, lw=1.5)
                # Mandatory bar or optional circle before fork
                if "0" in card_end:
                    circ_end = patches.Circle((pn[0] + eux*2.8, pn[1] + euy*2.8), 0.6, ec=color, fc="#ffffff", lw=1.2)
                    ax.add_patch(circ_end)
                else:
                    bar_x, bar_y = pn[0] + eux*2.6, pn[1] + euy*2.6
                    ax.plot([bar_x - evx*0.8, bar_x + evx*0.8], [bar_y - evy*0.8, bar_y + evy*0.8], color=color, lw=1.5)
            elif card_end == "1":
                b1_x, b1_y = pn[0] + eux*1.0, pn[1] + euy*1.0
                b2_x, b2_y = pn[0] + eux*1.8, pn[1] + euy*1.8
                ax.plot([b1_x - evx*0.8, b1_x + evx*0.8], [b1_y - evy*0.8, b1_y + evy*0.8], color=color, lw=1.5)
                ax.plot([b2_x - evx*0.8, b2_x + evx*0.8], [b2_y - evy*0.8, b2_y + evy*0.8], color=color, lw=1.5)

        # 3. Label Badge at midpoint
        if label:
            mid_idx = len(points) // 2
            pm1, pm2 = points[mid_idx - 1], points[mid_idx]
            mx, my = (pm1[0] + pm2[0])/2 + label_offset[0], (pm1[1] + pm2[1])/2 + label_offset[1]
            lbl_pill = patches.FancyBboxPatch((mx - len(label)*0.28, my - 0.7), len(label)*0.56, 1.4,
                                             boxstyle="round,pad=0.1", ec="#cbd5e1", fc="#ffffff", lw=0.8)
            ax.add_patch(lbl_pill)
            ax.text(mx, my, label, fontsize=6.2, fontweight='bold', color="#1e293b", ha='center', va='center')

    # --- Draw All 14 Core Database Relationships with Clean Routing ---

    # 1. roles -> users (1 : 0..N) Non-identifying
    draw_crows_foot_edge([(16.3, 81.0), (17.5, 81.0)], "1", "0..N", "authorizes", "#1e40af")

    # 2. users -> app_sessions (1 : 0..N) Identifying
    draw_crows_foot_edge([(20.0, 68.0), (20.0, 63.5), (9.5, 63.5), (9.5, 61.0)], "1", "0..N", "maintains session", "#1e40af")

    # 3. customers -> users (0..1 : 0..1 optional portal user link)
    draw_crows_foot_edge([(35.0, 84.0), (31.5, 84.0)], "0..1", "0..1", "provisions portal", "#1e40af")

    # 4. customers -> vehicles (1 : 1..N) Strong ownership
    draw_crows_foot_edge([(49.5, 81.0), (51.0, 81.0)], "1", "1..N", "owns fleet", "#15803d")

    # 5. insurance_plans -> vehicle_policies (1 : 1..N)
    draw_crows_foot_edge([(31.5, 48.0), (35.0, 48.0)], "1", "1..N", "defines terms", "#b45309")

    # 6. vehicles -> vehicle_policies (1 : 1..N)
    draw_crows_foot_edge([(55.0, 68.0), (55.0, 64.0), (42.0, 64.0), (42.0, 62.0)], "1", "1..N", "insured by", "#b45309")

    # 7. vehicles -> vehicle_images (1 : 1..N)
    draw_crows_foot_edge([(58.5, 68.0), (58.5, 62.0)], "1", "1..N", "contains photos", "#0284c7")

    # 8. vehicles -> analyses (1 : 1..N)
    draw_crows_foot_edge([(63.0, 68.0), (63.0, 64.5), (71.5, 64.5), (71.5, 62.5)], "1", "1..N", "inspected in", "#0284c7")

    # 9. vehicle_images -> analyses (1 : 1..N)
    draw_crows_foot_edge([(65.5, 48.0), (67.0, 48.0)], "1", "1..N", "source photo", "#0284c7")

    # 10. analyses -> vehicle_inspection_notes (1 : 0..N)
    draw_crows_foot_edge([(82.0, 48.0), (83.5, 48.0)], "1", "0..N", "remarks", "#0284c7")

    # 11. damage_pricing_catalog -> analysis_damages (1 : 0..N lookup)
    draw_crows_foot_edge([(17.3, 16.0), (19.0, 16.0)], "1", "0..N", "prices catalog", "#0f766e")

    # 12. analyses -> analysis_damages (1 : 0..N) Identifying
    draw_crows_foot_edge([(70.0, 36.0), (70.0, 32.5), (26.5, 32.5), (26.5, 30.0)], "1", "0..N", "detects defects", "#0f766e")

    # 13. analyses -> reports (1 : 1..N)
    draw_crows_foot_edge([(74.5, 36.0), (74.5, 33.5), (44.0, 33.5), (44.0, 30.0)], "1", "1..N", "publishes claim", "#7e22ce")

    # 14. analyses -> audit_logs (1 : 0..N)
    draw_crows_foot_edge([(79.0, 36.0), (79.0, 32.5), (63.0, 32.5), (63.0, 30.0)], "1", "0..N", "audit trail", "#334155")

    # =========================================================================
    # 6. AUTHENTIC EER NOTATION LEGEND (Bottom Right Panel)
    # =========================================================================
    leg_x, leg_y, leg_w, leg_h = 75.5, 4.5, 23.0, 25.5
    leg_shadow = patches.FancyBboxPatch((leg_x + 0.3, leg_y - 0.3), leg_w, leg_h, boxstyle="round,pad=0.2", ec="none", fc="#e2e8f0", alpha=0.6)
    ax.add_patch(leg_shadow)
    leg_card = patches.FancyBboxPatch((leg_x, leg_y), leg_w, leg_h, boxstyle="round,pad=0.1", ec="#1e293b", fc="#ffffff", lw=1.4)
    ax.add_patch(leg_card)

    # Legend Header
    leg_hdr = patches.Rectangle((leg_x, leg_y + leg_h - 3.6), leg_w, 3.6, ec="#1e293b", fc="#1e293b", lw=1.4)
    ax.add_patch(leg_hdr)
    ax.text(leg_x + leg_w/2, leg_y + leg_h - 1.8, "ENHANCED ER (EER) NOTATION GUIDE", fontsize=8.0, fontweight='bold', color="#ffffff", ha='center', va='center')

    # Legend Items
    legend_entries = [
        ("PK", "#b91c1c", "Primary Key (Unique Record Identifier)"),
        ("FK", "#1d4ed8", "Foreign Key (Referential Integrity Constraint)"),
        ("UQ", "#d97706", "Unique Constraint (Candidate Key)"),
        ("[Strong]", "#15803d", "Strong Entity (Independent Existence)"),
        ("[Weak]", "#475569", "Weak / Dependent Entity (FK Dependent)"),
        ("||-----|<", "#475569", "Mandatory One to Mandatory Many (1 : 1..N)"),
        ("o|-----o<", "#475569", "Optional Zero/One to Optional Many (0..1 : 0..N)"),
        ("(d)", "#1e40af", "Disjoint Specialization / Generalization Subclass"),
    ]

    ly = leg_y + leg_h - 5.4
    for sym, col, desc in legend_entries:
        if sym == "PK" or sym == "FK" or sym == "UQ":
            pill = patches.FancyBboxPatch((leg_x + 0.8, ly - 0.8), 2.2, 1.6, boxstyle="round,pad=0.05", ec=col, fc="#ffffff", lw=0.8)
            ax.add_patch(pill)
            ax.text(leg_x + 1.9, ly, sym, fontsize=6.2, fontweight='bold', color=col, ha='center', va='center')
        elif sym == "(d)":
            c_circ = patches.Circle((leg_x + 1.9, ly), 0.8, ec=col, fc="#eff6ff", lw=1.0)
            ax.add_patch(c_circ)
            ax.text(leg_x + 1.9, ly, "d", fontsize=6.5, fontweight='bold', color=col, ha='center', va='center')
        else:
            ax.text(leg_x + 1.9, ly, sym, fontsize=6.5, fontweight='bold', color=col, ha='center', va='center')

        ax.text(leg_x + 3.8, ly, desc, fontsize=6.2, color="#1e293b", va='center')
        ly -= 2.6

    # =========================================================================
    # 7. BOTTOM DOCUMENT CAPTION
    # =========================================================================
    ax.text(50.0, 1.0, "Figure 4.3: Enhanced Entity-Relationship Diagram (EERD) - 15 Normalized Database Entities, Attributes, Constraints, and Specialization Hierarchies",
            fontsize=9.5, fontweight='bold', color="#0f172a", ha='center', va='center')

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Genuine Real EER Diagram successfully generated at: {output_path}")

if __name__ == "__main__":
    out_path = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\reports\uml_diagrams\er_diagram.png"
    draw_real_eer_diagram(out_path)
