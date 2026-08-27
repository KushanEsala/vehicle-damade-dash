import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_perfect_eer_diagram(output_path):
    # Professional 20.0 x 14.0 inches canvas at 300 DPI
    fig, ax = plt.subplots(figsize=(20.0, 14.0), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Background fill
    fig.patch.set_facecolor('#f8fafc')
    ax.set_facecolor('#f8fafc')

    # =========================================================================
    # 1. SUBSYSTEM BACKGROUND REGIONS (EER Subject Modules)
    # =========================================================================
    subsystems = [
        (1.5, 66.0, 31.5, 31.5, "1. USER ACCESS & IDENTITY GOVERNANCE", "#f1f5f9", "#cbd5e1"),
        (34.5, 66.0, 64.0, 31.5, "2. CUSTOMER & VEHICLE ASSET MANAGEMENT (FLEET REGISTRY)", "#f0fdf4", "#bbf7d0"),
        (1.5, 33.5, 31.5, 31.0, "3. INSURANCE POLICY & UNDERWRITING", "#fefce8", "#fef08a"),
        (34.5, 33.5, 64.0, 31.0, "4. AI DAMAGE INSPECTION & ASSESSMENT PIPELINE", "#f0f9ff", "#bae6fd"),
        (1.5, 2.0, 97.0, 30.0, "5. DAMAGE COSTING, REPORT GENERATION & SYSTEM AUDITING", "#faf5ff", "#e9d5ff"),
    ]

    for sx, sy, sw, sh, stitle, sbg, sstroke in subsystems:
        box = patches.FancyBboxPatch((sx, sy), sw, sh, boxstyle="round,pad=0.5", ec=sstroke, fc=sbg, lw=1.5, ls="--")
        ax.add_patch(box)
        pill = patches.FancyBboxPatch((sx + 1.2, sy + sh - 2.8), len(stitle)*0.44 + 2.0, 2.2,
                                     boxstyle="round,pad=0.2", ec=sstroke, fc="#ffffff", lw=1.0)
        ax.add_patch(pill)
        ax.text(sx + 2.0, sy + sh - 1.7, stitle, fontsize=8.2, fontweight='bold', color="#334155", va='center')

    # =========================================================================
    # 2. ENTITY TABLE CARDS (With Exact Types, Keys & Nullability)
    # =========================================================================
    tables = {
        "roles": (2.8, 73.5, 13.0, 21.0, "#1e40af", "STRONG", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("UQ", "code", "VARCHAR(30)", "NN"),
            (" ", "name", "VARCHAR(60)", "NN"),
            (" ", "description", "VARCHAR(255)", "NULL"),
            (" ", "created_at", "DATETIME", "NN"),
        ]),
        "users": (17.5, 73.5, 14.0, 21.0, "#1e40af", "STRONG", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("FK", "role_id", "BIGINT(20)", "NN"),
            ("FK", "customer_id", "BIGINT(20)", "NULL"),
            ("UQ", "username", "VARCHAR(80)", "NN"),
            ("UQ", "email", "VARCHAR(255)", "NN"),
            (" ", "password_hash", "VARCHAR(255)", "NN"),
            (" ", "is_active", "TINYINT(1)", "NN"),
        ]),
        "customers": (36.5, 70.5, 18.0, 24.5, "#15803d", "STRONG", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("UQ", "customer_code", "VARCHAR(30)", "NN"),
            (" ", "full_name", "VARCHAR(150)", "NN"),
            ("UQ", "nic_or_passport", "VARCHAR(60)", "NULL"),
            (" ", "phone_primary", "VARCHAR(30)", "NN"),
            (" ", "email", "VARCHAR(255)", "NN"),
            (" ", "city", "VARCHAR(100)", "NN"),
            (" ", "status", "VARCHAR(20)", "NN"),
        ]),
        "vehicles": (57.0, 70.5, 18.5, 24.5, "#15803d", "STRONG", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("FK", "customer_id", "BIGINT(20)", "NN"),
            ("UQ", "reg_number", "VARCHAR(40)", "NN"),
            (" ", "chassis_number", "VARCHAR(80)", "NULL"),
            (" ", "make", "VARCHAR(100)", "NN"),
            (" ", "model", "VARCHAR(100)", "NN"),
            (" ", "year", "INT(11)", "NULL"),
            (" ", "fuel_type", "VARCHAR(30)", "NN"),
        ]),
        "company_profile": (78.0, 72.0, 18.5, 23.0, "#334155", "STRONG", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            (" ", "company_name", "VARCHAR(150)", "NN"),
            (" ", "tax_reg_no", "VARCHAR(50)", "NN"),
            (" ", "hotline", "VARCHAR(30)", "NN"),
            (" ", "email", "VARCHAR(255)", "NN"),
            (" ", "default_vat_rate", "FLOAT", "NN"),
            (" ", "address", "TEXT", "NULL"),
        ]),
        "app_sessions": (2.8, 36.0, 13.0, 24.0, "#1e40af", "WEAK", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("FK", "user_id", "BIGINT(20)", "NN"),
            ("UQ", "token", "VARCHAR(255)", "NN"),
            (" ", "ip_address", "VARCHAR(45)", "NN"),
            (" ", "expires_at", "DATETIME", "NN"),
            (" ", "created_at", "DATETIME", "NN"),
        ]),
        "insurance_plans": (17.5, 36.0, 14.0, 24.0, "#b45309", "STRONG", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("UQ", "plan_code", "VARCHAR(30)", "NN"),
            (" ", "name", "VARCHAR(100)", "NN"),
            (" ", "coverage_limit", "DECIMAL(12,2)", "NN"),
            (" ", "deductible", "DECIMAL(10,2)", "NN"),
            (" ", "is_active", "TINYINT(1)", "NN"),
        ]),
        "vehicle_policies": (36.5, 36.0, 14.0, 25.0, "#b45309", "STRONG", [
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
        "vehicle_images": (52.5, 36.0, 14.0, 25.0, "#0284c7", "WEAK", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("FK", "vehicle_id", "BIGINT(20)", "NN"),
            (" ", "storage_path", "VARCHAR(500)", "NN"),
            (" ", "image_hash_sha256", "CHAR(64)", "NN"),
            (" ", "mime_type", "VARCHAR(50)", "NN"),
            (" ", "file_size_bytes", "BIGINT(20)", "NN"),
            (" ", "uploaded_at", "DATETIME", "NN"),
        ]),
        "analyses": (68.5, 35.5, 14.5, 25.5, "#0284c7", "STRONG", [
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
        "vehicle_inspection_notes": (84.5, 36.0, 13.0, 24.0, "#0284c7", "WEAK", [
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
        "analysis_damages": (28.0, 4.5, 15.5, 25.0, "#0f766e", "WEAK", [
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
        "reports": (45.5, 4.5, 15.5, 25.0, "#7e22ce", "WEAK", [
            ("PK", "id", "BIGINT(20)", "NN AI"),
            ("UQ", "report_no", "VARCHAR(50)", "NN"),
            ("FK", "analysis_id", "BIGINT(20)", "NN"),
            ("FK", "generated_by", "BIGINT(20)", "NN"),
            (" ", "pdf_file_path", "VARCHAR(500)", "NN"),
            (" ", "pdf_hash_sha256", "CHAR(64)", "NN"),
            (" ", "final_amount", "DECIMAL(12,2)", "NN"),
            (" ", "generated_at", "DATETIME", "NN"),
        ]),
        "audit_logs": (62.5, 4.5, 15.5, 25.0, "#334155", "WEAK", [
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
    # 3. DRAW TABLES
    # =========================================================================
    for name, (tx, ty, tw, th, tcolor, etype, attrs) in tables.items():
        # Shadow
        shadow = patches.FancyBboxPatch((tx + 0.25, ty - 0.25), tw, th, boxstyle="round,pad=0.15", ec="none", fc="#cbd5e1", alpha=0.5)
        ax.add_patch(shadow)

        # Card
        card = patches.FancyBboxPatch((tx, ty), tw, th, boxstyle="round,pad=0.08", ec="#1e293b", fc="#ffffff", lw=1.3)
        ax.add_patch(card)

        if etype == "WEAK":
            inner_card = patches.FancyBboxPatch((tx + 0.2, ty + 0.2), tw - 0.4, th - 0.4,
                                               boxstyle="round,pad=0.05", ec="#64748b", fc="none", lw=0.6, ls=":")
            ax.add_patch(inner_card)

        # Header
        header_h = 3.2
        header_rect = patches.Rectangle((tx, ty + th - header_h), tw, header_h, ec="#1e293b", fc=tcolor, lw=1.3)
        ax.add_patch(header_rect)
        ax.text(tx + 0.5, ty + th - 1.6, name, fontsize=8.5, fontweight='bold', color="#ffffff", va='center')
        type_tag = "[Strong Entity]" if etype == "STRONG" else "[Weak Entity]"
        ax.text(tx + tw - 0.5, ty + th - 1.6, type_tag, fontsize=6.0, color="#e0e7ff", ha='right', va='center')

        # Rows
        row_h = (th - header_h - 0.6) / max(len(attrs), 1)
        curr_y = ty + th - header_h - 0.3

        for idx, (tag, col_name, dtype, null_str) in enumerate(attrs):
            row_y = curr_y - (idx + 1) * row_h + row_h/2
            if idx % 2 == 1:
                row_bg = patches.Rectangle((tx + 0.05, curr_y - (idx + 1) * row_h), tw - 0.1, row_h, ec="none", fc="#f8fafc")
                ax.add_patch(row_bg)

            if tag == "PK":
                pk_badge = patches.FancyBboxPatch((tx + 0.3, row_y - 0.7), 1.5, 1.4, boxstyle="round,pad=0.05", ec="#b91c1c", fc="#fee2e2", lw=0.7)
                ax.add_patch(pk_badge)
                ax.text(tx + 1.05, row_y, "PK", fontsize=5.6, fontweight='bold', color="#b91c1c", ha='center', va='center')
            elif tag == "FK":
                fk_badge = patches.FancyBboxPatch((tx + 0.3, row_y - 0.7), 1.5, 1.4, boxstyle="round,pad=0.05", ec="#1d4ed8", fc="#dbeafe", lw=0.7)
                ax.add_patch(fk_badge)
                ax.text(tx + 1.05, row_y, "FK", fontsize=5.6, fontweight='bold', color="#1d4ed8", ha='center', va='center')
            elif tag == "UQ":
                uq_badge = patches.FancyBboxPatch((tx + 0.3, row_y - 0.7), 1.5, 1.4, boxstyle="round,pad=0.05", ec="#d97706", fc="#fef3c7", lw=0.7)
                ax.add_patch(uq_badge)
                ax.text(tx + 1.05, row_y, "UQ", fontsize=5.4, fontweight='bold', color="#b45309", ha='center', va='center')
            else:
                ax.plot(tx + 1.05, row_y, marker='o', markersize=2.2, color="#94a3b8")

            col_weight = 'bold' if tag in ["PK", "UQ"] else 'normal'
            col_color = "#0f172a" if tag != "FK" else "#1e3a8a"
            ax.text(tx + 2.1, row_y, col_name, fontsize=6.6, fontweight=col_weight, color=col_color, va='center')
            ax.text(tx + tw - 0.4, row_y, f"{dtype} {null_str}", fontsize=5.6, color="#64748b", ha='right', va='center')

    # =========================================================================
    # 4. EER SPECIALIZATION HIERARCHIES (Inheritance Circles & Subclasses)
    # =========================================================================
    # A. User Specialization: users -> [Admin User], [Claims Assessor], [Policyholder]
    spec_cx, spec_cy = 24.5, 70.0
    circle_d = patches.Circle((spec_cx, spec_cy), 0.9, ec="#1e40af", fc="#eff6ff", lw=1.2)
    ax.add_patch(circle_d)
    ax.text(spec_cx, spec_cy, "d", fontsize=7.5, fontweight='bold', color="#1e40af", ha='center', va='center')
    ax.plot([24.5, 24.5], [73.5, spec_cy + 0.9], color="#1e40af", lw=1.2)

    user_subclasses = [
        ("Admin User", 18.0, 67.5),
        ("Claims Assessor", 24.5, 67.5),
        ("Policyholder", 31.0, 67.5),
    ]
    for sname, sx, sy in user_subclasses:
        ax.plot([spec_cx, sx], [spec_cy - 0.9, sy + 1.0], color="#1e40af", lw=0.9)
        scard = patches.FancyBboxPatch((sx - 2.7, sy - 0.5), 5.4, 1.5, boxstyle="round,pad=0.1", ec="#3b82f6", fc="#ffffff", lw=0.8)
        ax.add_patch(scard)
        ax.text(sx, sy + 0.25, sname, fontsize=5.6, fontweight='bold', color="#1e40af", ha='center', va='center')

    # B. Damage Defect Specialization: analysis_damages -> 7 Subclasses
    dmg_cx, dmg_cy = 20.0, 16.5
    circle_dmg = patches.Circle((dmg_cx, dmg_cy), 0.9, ec="#0f766e", fc="#f0fdfa", lw=1.2)
    ax.add_patch(circle_dmg)
    ax.text(dmg_cx, dmg_cy, "d", fontsize=7.5, fontweight='bold', color="#0f766e", ha='center', va='center')
    ax.plot([28.0, dmg_cx + 0.9], [16.5, dmg_cy], color="#0f766e", lw=1.2)

    dmg_subclasses = ["Scratch", "Dent", "Tear", "Broken Lamp", "Broken Glass", "Puncture", "Missing Part"]
    for d_idx, d_name in enumerate(dmg_subclasses):
        dy = 26.5 - d_idx * 3.2
        ax.plot([dmg_cx - 0.9, 21.5, 21.5, 22.0], [dmg_cy, dmg_cy, dy + 0.5, dy + 0.5], color="#0f766e", lw=0.7)
        dpill = patches.FancyBboxPatch((22.0, dy - 0.4), 5.2, 1.7, boxstyle="round,pad=0.1", ec="#0d9488", fc="#ffffff", lw=0.7)
        ax.add_patch(dpill)
        ax.text(24.6, dy + 0.45, f"is-a: {d_name}", fontsize=5.4, fontweight='bold', color="#0f766e", ha='center', va='center')

    # =========================================================================
    # 5. CLEAN CROW'S FOOT RELATIONSHIPS (True Crow's Foot Forks & Double Ticks)
    # =========================================================================
    def draw_crows_foot(points, card_start="1", card_end="N", label="", color="#475569", ls="-", label_offset=(0,0)):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        ax.plot(xs, ys, color=color, lw=1.2, ls=ls)

        # 1. Start Symbol (1 or 0..1)
        p0, p1 = points[0], points[1]
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        dist = (dx**2 + dy**2)**0.5
        if dist > 0:
            ux, uy = dx/dist, dy/dist
            vx, vy = -uy, ux
            if card_start == "1":
                b1x, b1y = p0[0] + ux*0.8, p0[1] + uy*0.8
                b2x, b2y = p0[0] + ux*1.5, p0[1] + uy*1.5
                ax.plot([b1x - vx*0.7, b1x + vx*0.7], [b1y - vy*0.7, b1y + vy*0.7], color=color, lw=1.3)
                ax.plot([b2x - vx*0.7, b2x + vx*0.7], [b2y - vy*0.7, b2y + vy*0.7], color=color, lw=1.3)
            elif card_start == "0..1":
                cx, cy = p0[0] + ux*1.0, p0[1] + uy*1.0
                circ = patches.Circle((cx, cy), 0.5, ec=color, fc="#ffffff", lw=1.0)
                ax.add_patch(circ)
                bx, by = p0[0] + ux*1.8, p0[1] + uy*1.8
                ax.plot([bx - vx*0.7, bx + vx*0.7], [by - vy*0.7, by + vy*0.7], color=color, lw=1.3)

        # 2. End Symbol (Many or 1)
        pn, pn_prev = points[-1], points[-2]
        edx, edy = pn_prev[0] - pn[0], pn_prev[1] - pn[1]
        edist = (edx**2 + edy**2)**0.5
        if edist > 0:
            eux, euy = edx/edist, edy/edist
            evx, evy = -euy, eux
            if "N" in card_end:
                # Crow's foot fork
                fx, fy = pn[0] + eux*1.6, pn[1] + euy*1.6
                ax.plot([pn[0], fx - evx*0.9], [pn[1], fy - evy*0.9], color=color, lw=1.3)
                ax.plot([pn[0], fx], [pn[1], fy], color=color, lw=1.3)
                ax.plot([pn[0], fx + evx*0.9], [pn[1], fy + evy*0.9], color=color, lw=1.3)
                if "0" in card_end:
                    circ_end = patches.Circle((pn[0] + eux*2.3, pn[1] + euy*2.3), 0.5, ec=color, fc="#ffffff", lw=1.0)
                    ax.add_patch(circ_end)
                else:
                    barx, bary = pn[0] + eux*2.2, pn[1] + euy*2.2
                    ax.plot([barx - evx*0.7, barx + evx*0.7], [bary - evy*0.7, bary + evy*0.7], color=color, lw=1.3)
            elif card_end == "1":
                b1x, b1y = pn[0] + eux*0.8, pn[1] + euy*0.8
                b2x, b2y = pn[0] + eux*1.5, pn[1] + euy*1.5
                ax.plot([b1x - evx*0.7, b1x + evx*0.7], [b1y - evy*0.7, b1y + evy*0.7], color=color, lw=1.3)
                ax.plot([b2x - evx*0.7, b2x + evx*0.7], [b2y - evy*0.7, b2y + evy*0.7], color=color, lw=1.3)

        # 3. Label Badge
        if label:
            mid_idx = len(points) // 2
            pm1, pm2 = points[mid_idx - 1], points[mid_idx]
            mx, my = (pm1[0] + pm2[0])/2 + label_offset[0], (pm1[1] + pm2[1])/2 + label_offset[1]
            lbl_pill = patches.FancyBboxPatch((mx - len(label)*0.24, my - 0.6), len(label)*0.48, 1.2,
                                             boxstyle="round,pad=0.1", ec="#cbd5e1", fc="#ffffff", lw=0.7)
            ax.add_patch(lbl_pill)
            ax.text(mx, my, label, fontsize=5.8, fontweight='bold', color="#1e293b", ha='center', va='center')

    # Relationships:
    # 1. roles -> users (1 : 0..N)
    draw_crows_foot([(15.8, 83.5), (17.5, 83.5)], "1", "0..N", "authorizes", "#1e40af")

    # 2. users -> app_sessions (1 : 0..N)
    draw_crows_foot([(20.0, 73.5), (20.0, 62.0), (9.0, 62.0), (9.0, 60.0)], "1", "0..N", "session", "#1e40af")

    # 3. customers -> users (0..1 : 0..1 optional portal)
    draw_crows_foot([(36.5, 86.0), (31.5, 86.0)], "0..1", "0..1", "provisions", "#1e40af")

    # 4. customers -> vehicles (1 : 1..N)
    draw_crows_foot([(54.5, 82.0), (57.0, 82.0)], "1", "1..N", "owns fleet", "#15803d")

    # 5. insurance_plans -> vehicle_policies (1 : 1..N)
    draw_crows_foot([(31.5, 48.0), (36.5, 48.0)], "1", "1..N", "defines terms", "#b45309")

    # 6. vehicles -> vehicle_policies (1 : 1..N)
    draw_crows_foot([(61.0, 70.5), (61.0, 63.5), (43.0, 63.5), (43.0, 61.0)], "1", "1..N", "insured by", "#b45309")

    # 7. vehicles -> vehicle_images (1 : 1..N)
    draw_crows_foot([(66.0, 70.5), (66.0, 62.5), (59.0, 62.5), (59.0, 61.0)], "1", "1..N", "contains photos", "#0284c7")

    # 8. vehicles -> analyses (1 : 1..N)
    draw_crows_foot([(71.0, 70.5), (71.0, 62.0), (74.0, 62.0), (74.0, 61.0)], "1", "1..N", "inspected in", "#0284c7")

    # 9. vehicle_images -> analyses (1 : 1..N)
    draw_crows_foot([(66.5, 48.0), (68.5, 48.0)], "1", "1..N", "source", "#0284c7")

    # 10. analyses -> vehicle_inspection_notes (1 : 0..N)
    draw_crows_foot([(83.0, 48.0), (84.5, 48.0)], "1", "0..N", "remarks", "#0284c7")

    # 11. damage_pricing_catalog -> analysis_damages (1 : 0..N)
    draw_crows_foot([(17.3, 16.0), (28.0, 16.0)], "1", "0..N", "catalog pricing", "#0f766e")

    # 12. analyses -> analysis_damages (1 : 0..N)
    draw_crows_foot([(71.0, 35.5), (71.0, 31.5), (35.0, 31.5), (35.0, 29.5)], "1", "0..N", "detects defects", "#0f766e")

    # 13. analyses -> reports (1 : 1..N)
    draw_crows_foot([(76.0, 35.5), (76.0, 32.5), (53.0, 32.5), (53.0, 29.5)], "1", "1..N", "publishes claim", "#7e22ce")

    # 14. analyses -> audit_logs (1 : 0..N)
    draw_crows_foot([(81.0, 35.5), (81.0, 31.5), (70.0, 31.5), (70.0, 29.5)], "1", "0..N", "audit trail", "#334155")

    # =========================================================================
    # 6. EER NOTATION LEGEND (Bottom Right)
    # =========================================================================
    leg_x, leg_y, leg_w, leg_h = 79.5, 4.5, 18.0, 25.0
    leg_shadow = patches.FancyBboxPatch((leg_x + 0.25, leg_y - 0.25), leg_w, leg_h, boxstyle="round,pad=0.15", ec="none", fc="#cbd5e1", alpha=0.5)
    ax.add_patch(leg_shadow)
    leg_card = patches.FancyBboxPatch((leg_x, leg_y), leg_w, leg_h, boxstyle="round,pad=0.08", ec="#1e293b", fc="#ffffff", lw=1.3)
    ax.add_patch(leg_card)

    leg_hdr = patches.Rectangle((leg_x, leg_y + leg_h - 3.2), leg_w, 3.2, ec="#1e293b", fc="#1e293b", lw=1.3)
    ax.add_patch(leg_hdr)
    ax.text(leg_x + leg_w/2, leg_y + leg_h - 1.6, "ENHANCED ER (EER) NOTATION GUIDE", fontsize=7.2, fontweight='bold', color="#ffffff", ha='center', va='center')

    legend_entries = [
        ("PK", "#b91c1c", "Primary Key (Unique Record ID)"),
        ("FK", "#1d4ed8", "Foreign Key (Referential Integrity)"),
        ("UQ", "#d97706", "Unique Key Constraint"),
        ("[Strong Entity]", "#15803d", "Independent Entity Table"),
        ("[Weak Entity]", "#475569", "Dependent / Child Entity Table"),
        ("||-----|<", "#475569", "Mandatory 1 to Mandatory Many (1:1..N)"),
        ("o|-----o<", "#475569", "Optional 0..1 to Optional Many (0..1:0..N)"),
        ("(d)", "#1e40af", "Disjoint Specialization Subclasses"),
    ]

    ly = leg_y + leg_h - 4.8
    for sym, col, desc in legend_entries:
        if sym in ["PK", "FK", "UQ"]:
            pill = patches.FancyBboxPatch((leg_x + 0.6, ly - 0.7), 1.8, 1.4, boxstyle="round,pad=0.05", ec=col, fc="#ffffff", lw=0.7)
            ax.add_patch(pill)
            ax.text(leg_x + 1.5, ly, sym, fontsize=5.6, fontweight='bold', color=col, ha='center', va='center')
        elif sym == "(d)":
            c_circ = patches.Circle((leg_x + 1.5, ly), 0.65, ec=col, fc="#eff6ff", lw=0.9)
            ax.add_patch(c_circ)
            ax.text(leg_x + 1.5, ly, "d", fontsize=6.0, fontweight='bold', color=col, ha='center', va='center')
        else:
            ax.text(leg_x + 1.5, ly, sym, fontsize=5.8, fontweight='bold', color=col, ha='center', va='center')

        ax.text(leg_x + 3.2, ly, desc, fontsize=5.6, color="#1e293b", va='center')
        ly -= 2.4

    # Caption at bottom
    ax.text(50.0, 1.0, "Figure 4.3: Enhanced Entity-Relationship Diagram (EERD) - 15 Normalized Database Entities, Attributes, Constraints, and Specialization Hierarchies (Database Model, Not UML)",
            fontsize=9.0, fontweight='bold', color="#0f172a", ha='center', va='center')

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Perfect EER Diagram successfully generated at: {output_path}")

if __name__ == "__main__":
    out_path = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\reports\uml_diagrams\er_diagram.png"
    draw_perfect_eer_diagram(out_path)
