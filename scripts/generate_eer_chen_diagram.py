import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, Ellipse
import numpy as np

def draw_chen_eer_diagram(output_path):
    # Ultra-high-resolution 36 x 24 inches at 300 DPI canvas
    fig, ax = plt.subplots(figsize=(36, 24), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Canvas Background
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    # Subsystem background bounding regions
    regions = [
        # (x, y, w, h, label, bg_color, border_color)
        (1.0, 68.0, 31.0, 30.0, "USER & AUTHENTICATION GOVERNANCE", "#f8fafc", "#cbd5e1"),
        (33.0, 68.0, 66.0, 30.0, "CUSTOMER & VEHICLE ASSET MANAGEMENT", "#f0fdf4", "#bbf7d0"),
        (1.0, 35.0, 31.0, 32.0, "INSURANCE POLICY & UNDERWRITING", "#fefce8", "#fef08a"),
        (33.0, 35.0, 66.0, 32.0, "VEHICLE INSPECTION & AI ANALYSIS PIPELINE", "#f0f9ff", "#bae6fd"),
        (1.0, 2.0, 98.0, 32.0, "DAMAGE COSTING, REPORT GENERATION & SYSTEM AUDITING", "#faf5ff", "#e9d5ff"),
    ]

    for rx, ry, rw, rh, rlabel, rbg, rborder in regions:
        region_rect = FancyBboxPatch(
            (rx, ry), rw, rh, boxstyle="round,pad=0.4", ec=rborder, fc=rbg, lw=1.2, ls="--"
        )
        ax.add_patch(region_rect)
        pill = FancyBboxPatch((rx + 0.8, ry + rh - 2.0), len(rlabel)*0.30 + 1.5, 1.6,
                              boxstyle="round,pad=0.2", ec=rborder, fc="#ffffff", lw=0.9)
        ax.add_patch(pill)
        ax.text(rx + 1.4, ry + rh - 1.2, rlabel, fontsize=8.0, fontweight='bold', color="#475569", va='center')

    # =========================================================================
    # HELPER DRAWING FUNCTIONS
    # =========================================================================
    def draw_entity(x, y, w, h, name, is_weak=False, bg="#ffffff", border="#1e293b"):
        if is_weak:
            rect_out = Rectangle((x - w/2, y - h/2), w, h, ec=border, fc=bg, lw=1.6, zorder=3)
            ax.add_patch(rect_out)
            pad = 0.32
            rect_in = Rectangle((x - w/2 + pad, y - h/2 + pad), w - 2*pad, h - 2*pad, ec=border, fc="none", lw=1.0, zorder=3)
            ax.add_patch(rect_in)
        else:
            rect = Rectangle((x - w/2, y - h/2), w, h, ec=border, fc=bg, lw=1.6, zorder=3)
            ax.add_patch(rect)
        
        ax.text(x, y, name, fontsize=8.4, fontweight='bold', color="#0f172a", ha='center', va='center', zorder=4)

    def draw_relationship(x, y, w, h, name, is_weak=False, bg="#ffffff", border="#b45309"):
        pts_out = np.array([
            [x, y + h/2],
            [x + w/2, y],
            [x, y - h/2],
            [x - w/2, y]
        ])
        poly_out = Polygon(pts_out, ec=border, fc=bg, lw=1.4, zorder=3)
        ax.add_patch(poly_out)

        if is_weak:
            pts_in = np.array([
                [x, y + h/2 - 0.35],
                [x + w/2 - 0.5, y],
                [x, y - h/2 + 0.35],
                [x - w/2 + 0.5, y]
            ])
            poly_in = Polygon(pts_in, ec=border, fc="none", lw=1.0, zorder=3)
            ax.add_patch(poly_in)
            
        ax.text(x, y, name, fontsize=7.2, fontweight='bold', color="#0f172a", ha='center', va='center', zorder=4)

    def draw_attribute(x, y, w, h, name, attr_type="REGULAR", bg="#ffffff", border="#475569"):
        if attr_type == "DERIVED":
            ell = Ellipse((x, y), w, h, ec=border, fc=bg, lw=1.2, ls="--", zorder=3)
            ax.add_patch(ell)
            ax.text(x, y, name, fontsize=6.6, color="#0f172a", ha='center', va='center', zorder=4)
        elif attr_type == "MULTIVALUED":
            ell_out = Ellipse((x, y), w, h, ec=border, fc=bg, lw=1.2, zorder=3)
            ax.add_patch(ell_out)
            pad_w, pad_h = 0.45, 0.28
            ell_in = Ellipse((x, y), w - pad_w, h - pad_h, ec=border, fc="none", lw=0.9, zorder=3)
            ax.add_patch(ell_in)
            ax.text(x, y, name, fontsize=6.6, color="#0f172a", ha='center', va='center', zorder=4)
        elif attr_type == "PK":
            ell = Ellipse((x, y), w, h, ec="#b91c1c", fc="#fff1f2", lw=1.3, zorder=3)
            ax.add_patch(ell)
            ax.text(x, y, name, fontsize=6.8, fontweight='bold', color="#991b1b", ha='center', va='center', zorder=4)
            tw = len(name) * 0.15
            ax.plot([x - tw, x + tw], [y - 0.35, y - 0.35], color="#991b1b", lw=1.2, zorder=4)
        else: # REGULAR
            ell = Ellipse((x, y), w, h, ec=border, fc=bg, lw=1.1, zorder=3)
            ax.add_patch(ell)
            ax.text(x, y, name, fontsize=6.6, color="#1e293b", ha='center', va='center', zorder=4)

    def draw_attr_link(ex, ey, ax_pos, ay_pos, color="#94a3b8"):
        ax.plot([ex, ax_pos], [ey, ay_pos], color=color, lw=0.9, ls="-", zorder=2)

    def draw_eer_relation_line(points, card_start="MANDATORY_ONE", card_end="MANDATORY_MANY", color="#1e293b"):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        ax.plot(xs, ys, color=color, lw=1.2, zorder=2)

        def draw_marker(p_end, p_prev, ctype):
            dx = p_end[0] - p_prev[0]
            dy = p_end[1] - p_prev[1]
            dist = np.hypot(dx, dy)
            if dist == 0:
                return
            ux = dx / dist
            uy = dy / dist
            nx = -uy
            ny = ux

            d1 = 0.5
            d2 = 1.0
            s = 0.45

            if ctype == "MANDATORY_ONE": # -||-
                p1 = (p_end[0] - ux*d1, p_end[1] - uy*d1)
                p2 = (p_end[0] - ux*d2, p_end[1] - uy*d2)
                ax.plot([p1[0] - nx*s, p1[0] + nx*s], [p1[1] - ny*s, p1[1] + ny*s], color=color, lw=1.4, zorder=5)
                ax.plot([p2[0] - nx*s, p2[0] + nx*s], [p2[1] - ny*s, p2[1] + ny*s], color=color, lw=1.4, zorder=5)

            elif ctype == "OPTIONAL_ONE": # -o-|
                p1 = (p_end[0] - ux*d1, p_end[1] - uy*d1)
                p2 = (p_end[0] - ux*d2, p_end[1] - uy*d2)
                ax.plot([p1[0] - nx*s, p1[0] + nx*s], [p1[1] - ny*s, p1[1] + ny*s], color=color, lw=1.4, zorder=5)
                circ = plt.Circle(p2, radius=0.28, ec=color, fc="#ffffff", lw=1.3, zorder=5)
                ax.add_patch(circ)

            elif ctype == "MANDATORY_MANY": # -|-<
                p_base = (p_end[0] - ux*d1, p_end[1] - uy*d1)
                ax.plot([p_end[0], p_base[0] - nx*s], [p_end[1], p_base[1] - ny*s], color=color, lw=1.3, zorder=5)
                ax.plot([p_end[0], p_base[0] + nx*s], [p_end[1], p_base[1] + ny*s], color=color, lw=1.3, zorder=5)
                p_bar = (p_end[0] - ux*d2, p_end[1] - uy*d2)
                ax.plot([p_bar[0] - nx*s, p_bar[0] + nx*s], [p_bar[1] - ny*s, p_bar[1] + ny*s], color=color, lw=1.4, zorder=5)

            elif ctype == "OPTIONAL_MANY": # -o-<
                p_base = (p_end[0] - ux*d1, p_end[1] - uy*d1)
                ax.plot([p_end[0], p_base[0] - nx*s], [p_end[1], p_base[1] - ny*s], color=color, lw=1.3, zorder=5)
                ax.plot([p_end[0], p_base[0] + nx*s], [p_end[1], p_base[1] + ny*s], color=color, lw=1.3, zorder=5)
                p_circ = (p_end[0] - ux*d2, p_end[1] - uy*d2)
                circ = plt.Circle(p_circ, radius=0.28, ec=color, fc="#ffffff", lw=1.3, zorder=5)
                ax.add_patch(circ)

        if card_start:
            draw_marker(points[0], points[1], card_start)
        if card_end:
            draw_marker(points[-1], points[-2], card_end)

    # =========================================================================
    # 1. ENTITY COORDINATES AND ATTRIBUTES DEFINITION
    # =========================================================================
    entities = {
        # 1. User Governance
        "ROLES": (6.5, 87.0, 5.5, 2.2, False, "#eff6ff", "#1d4ed8"),
        "USERS": (21.5, 87.0, 5.5, 2.2, False, "#eff6ff", "#1d4ed8"),
        "APP_SESSIONS": (6.5, 73.0, 6.2, 2.2, True, "#f8fafc", "#475569"),

        # 2. Customer & Vehicle
        "CUSTOMERS": (41.0, 87.0, 6.0, 2.2, False, "#f0fdf4", "#15803d"),
        "VEHICLES": (63.0, 87.0, 5.5, 2.2, False, "#f0fdf4", "#15803d"),
        "COMPANY_PROFILE": (88.0, 87.0, 7.5, 2.2, False, "#f1f5f9", "#334155"),

        # 3. Insurance Policy
        "INSURANCE_PLANS": (7.0, 51.0, 7.2, 2.2, False, "#fef3c7", "#b45309"),
        "VEHICLE_POLICIES": (24.0, 51.0, 7.2, 2.2, False, "#fef3c7", "#b45309"),

        # 4. Vehicle Inspection & Analysis
        "VEHICLE_IMAGES": (43.0, 51.0, 6.8, 2.2, True, "#e0f2fe", "#0284c7"),
        "ANALYSES": (65.0, 51.0, 5.5, 2.2, False, "#e0f2fe", "#0284c7"),
        "INSPECTION_NOTES": (89.0, 51.0, 7.5, 2.2, True, "#e0f2fe", "#0284c7"),

        # 5. Damage & Auditing
        "DAMAGE_CATALOG": (10.0, 16.0, 7.5, 2.2, False, "#f0fdf4", "#0f766e"),
        "ANALYSIS_DAMAGES": (35.0, 16.0, 7.8, 2.2, True, "#f0fdf4", "#0f766e"),
        "REPORTS": (65.0, 16.0, 6.2, 2.2, True, "#faf5ff", "#7e22ce"),
        "AUDIT_LOGS": (85.0, 16.0, 6.5, 2.2, True, "#f8fafc", "#334155"),
    }

    for ename, (ex, ey, ew, eh, is_w, ebg, eborder) in entities.items():
        draw_entity(ex, ey, ew, eh, ename, is_w, ebg, eborder)

    # Clean non-overlapping attribute placements
    attrs_map = {
        "ROLES": [
            ("id", -3.2, 3.2, 2.2, 1.1, "PK"),
            ("code", 0.0, 3.5, 2.4, 1.1, "REGULAR"),
            ("name", 3.2, 3.2, 2.4, 1.1, "REGULAR"),
            ("description", -3.2, -3.2, 3.2, 1.1, "REGULAR"),
            ("created_at", 3.2, -3.2, 2.8, 1.1, "REGULAR"),
        ],
        "USERS": [
            ("id", -3.6, 3.6, 2.2, 1.1, "PK"),
            ("username", -3.6, -3.4, 2.8, 1.1, "REGULAR"),
            ("email", 0.0, -3.8, 2.4, 1.1, "REGULAR"),
            ("password_hash", 3.6, -3.4, 3.2, 1.1, "REGULAR"),
            ("is_active", 3.6, 3.6, 2.4, 1.1, "REGULAR"),
        ],
        "APP_SESSIONS": [
            ("id", -3.8, 3.0, 2.0, 1.1, "PK"),
            ("token", -3.8, -3.0, 2.4, 1.1, "REGULAR"),
            ("ip_address", 0.0, -3.8, 2.8, 1.1, "REGULAR"),
            ("expires_at", 3.8, -3.0, 2.6, 1.1, "REGULAR"),
            ("created_at", 3.8, 3.0, 2.6, 1.1, "REGULAR"),
        ],
        "CUSTOMERS": [
            ("id", -4.2, 3.8, 2.2, 1.1, "PK"),
            ("customer_code", -1.6, 4.8, 3.2, 1.1, "REGULAR"),
            ("full_name", 1.8, 4.8, 2.8, 1.1, "REGULAR"),
            ("nic_or_passport", 4.5, 3.8, 3.4, 1.1, "REGULAR"),
            ("phone_primary", -4.2, -3.8, 3.2, 1.1, "REGULAR"),
            ("email", -1.4, -4.6, 2.4, 1.1, "REGULAR"),
            ("city", 1.4, -4.6, 2.2, 1.1, "REGULAR"),
            ("status", 4.0, -3.8, 2.2, 1.1, "REGULAR"),
        ],
        "VEHICLES": [
            ("id", -4.0, 3.8, 2.2, 1.1, "PK"),
            ("reg_number", -1.4, 4.8, 3.0, 1.1, "REGULAR"),
            ("chassis_number", 1.8, 4.8, 3.4, 1.1, "REGULAR"),
            ("make", 4.4, 3.8, 2.2, 1.1, "REGULAR"),
            ("model", -4.2, -3.8, 2.2, 1.1, "REGULAR"),
            ("year", 4.2, -3.8, 2.0, 1.1, "REGULAR"),
            ("fuel_type", 0.0, -4.8, 2.4, 1.1, "REGULAR"),
        ],
        "COMPANY_PROFILE": [
            ("id", -4.5, 3.8, 2.2, 1.1, "PK"),
            ("company_name", -1.5, 4.8, 3.4, 1.1, "REGULAR"),
            ("tax_reg_no", 2.0, 4.8, 3.0, 1.1, "REGULAR"),
            ("hotline", 4.8, 3.8, 2.4, 1.1, "REGULAR"),
            ("email", -4.2, -3.8, 2.4, 1.1, "REGULAR"),
            ("address", -1.4, -4.6, 2.4, 1.1, "REGULAR"),
            ("default_vat_rate", 2.4, -4.6, 3.4, 1.1, "REGULAR"),
        ],
        "INSURANCE_PLANS": [
            ("id", -4.5, 3.5, 2.2, 1.1, "PK"),
            ("plan_code", -1.5, 4.5, 2.8, 1.1, "REGULAR"),
            ("name", 1.8, 4.5, 2.4, 1.1, "REGULAR"),
            ("coverage_limit", 4.8, 3.5, 3.2, 1.1, "REGULAR"),
            ("deductible", -3.2, -3.8, 2.6, 1.1, "REGULAR"),
            ("is_active", 3.2, -3.8, 2.4, 1.1, "REGULAR"),
        ],
        "VEHICLE_POLICIES": [
            ("id", -4.5, 3.8, 2.2, 1.1, "PK"),
            ("policy_no", -1.5, 4.8, 2.8, 1.1, "REGULAR"),
            ("start_date", 1.8, 4.8, 2.6, 1.1, "REGULAR"),
            ("end_date", 4.5, 3.8, 2.6, 1.1, "REGULAR"),
            ("coverage_limit", -3.5, -4.0, 3.2, 1.1, "REGULAR"),
            ("deductible", 0.0, -4.6, 2.6, 1.1, "REGULAR"),
            ("status", 3.5, -4.0, 2.2, 1.1, "REGULAR"),
        ],
        "VEHICLE_IMAGES": [
            ("id", -4.2, 3.8, 2.2, 1.1, "PK"),
            ("storage_path", -1.4, 4.8, 3.0, 1.1, "REGULAR"),
            ("image_hash", 1.8, 4.8, 3.0, 1.1, "REGULAR"),
            ("mime_type", 4.4, 3.8, 2.6, 1.1, "REGULAR"),
            ("file_size_bytes", -2.8, -4.0, 3.2, 1.1, "REGULAR"),
            ("uploaded_at", 2.8, -4.0, 2.8, 1.1, "REGULAR"),
        ],
        "ANALYSES": [
            ("id", -4.0, 3.8, 2.2, 1.1, "PK"),
            ("analysis_no", -1.4, 4.8, 3.0, 1.1, "REGULAR"),
            ("has_vehicle", 1.8, 4.8, 2.8, 1.1, "REGULAR"),
            ("status", 4.2, 3.8, 2.2, 1.1, "REGULAR"),
            ("subtotal_repair", -4.6, -3.5, 3.2, 1.1, "DERIVED"),
            ("vat_amount", -2.6, -4.6, 2.6, 1.1, "DERIVED"),
            ("net_payable", 4.6, -3.5, 2.8, 1.1, "DERIVED"),
        ],
        "INSPECTION_NOTES": [
            ("id", -4.2, 3.8, 2.2, 1.1, "PK"),
            ("note_type", 0.0, 4.5, 2.6, 1.1, "REGULAR"),
            ("content", 4.2, 3.8, 2.4, 1.1, "REGULAR"),
            ("created_at", 0.0, -4.0, 2.6, 1.1, "REGULAR"),
        ],
        "DAMAGE_CATALOG": [
            ("id", -4.5, 3.8, 2.2, 1.1, "PK"),
            ("damage_type", -1.5, 4.8, 3.0, 1.1, "REGULAR"),
            ("severity", 1.8, 4.8, 2.4, 1.1, "REGULAR"),
            ("labor_rate", 4.5, 3.8, 2.6, 1.1, "REGULAR"),
            ("part_cost", -2.8, -4.0, 2.6, 1.1, "REGULAR"),
            ("description", 2.8, -4.0, 2.8, 1.1, "REGULAR"),
        ],
        "ANALYSIS_DAMAGES": [
            ("id", -4.8, 3.8, 2.2, 1.1, "PK"),
            ("damage_type", -2.0, 4.8, 3.0, 1.1, "REGULAR"),
            ("severity", 1.2, 4.8, 2.4, 1.1, "REGULAR"),
            ("confidence", 4.5, 3.8, 2.6, 1.1, "REGULAR"),
            ("passed_gate", -4.5, -4.0, 2.8, 1.1, "REGULAR"),
            ("polygon_points", -1.4, -4.8, 3.4, 1.1, "MULTIVALUED"),
            ("estimated_cost", 1.8, -4.8, 3.0, 1.1, "DERIVED"),
            ("is_accepted", 4.8, -4.0, 2.6, 1.1, "REGULAR"),
        ],
        "REPORTS": [
            ("id", -4.5, 3.8, 2.2, 1.1, "PK"),
            ("report_no", -1.8, 4.8, 2.6, 1.1, "REGULAR"),
            ("pdf_file_path", 2.2, 4.8, 3.0, 1.1, "REGULAR"),
            ("pdf_hash", 4.8, 3.8, 2.4, 1.1, "REGULAR"),
            ("final_amount", -2.4, -4.0, 2.8, 1.1, "DERIVED"),
            ("generated_at", 2.4, -4.0, 2.8, 1.1, "REGULAR"),
        ],
        "AUDIT_LOGS": [
            ("id", -4.5, 3.8, 2.2, 1.1, "PK"),
            ("action", -1.5, 4.8, 2.4, 1.1, "REGULAR"),
            ("entity_name", 1.8, 4.8, 2.8, 1.1, "REGULAR"),
            ("entity_id", 4.5, 3.8, 2.4, 1.1, "REGULAR"),
            ("previous_state", -3.5, -4.0, 3.0, 1.1, "REGULAR"),
            ("new_state", 0.0, -4.6, 2.6, 1.1, "REGULAR"),
            ("timestamp", 3.5, -4.0, 2.6, 1.1, "REGULAR"),
        ],
    }

    for ename, alist in attrs_map.items():
        ex, ey, ew, eh, is_w, ebg, eborder = entities[ename]
        for aname, dx, dy, aw, ah, atype in alist:
            ax_pos, ay_pos = ex + dx, ey + dy
            draw_attr_link(ex, ey, ax_pos, ay_pos)
            draw_attribute(ax_pos, ay_pos, aw, ah, aname, atype)

    # =========================================================================
    # 2. RELATIONSHIPS DEFINITION & LINES
    # =========================================================================
    # 1. roles -> users (authorizes)
    draw_relationship(14.0, 87.0, 4.8, 2.4, "Authorizes", False, "#fef3c7", "#b45309")
    draw_eer_relation_line([(9.25, 87.0), (11.6, 87.0)], "MANDATORY_ONE", None)
    draw_eer_relation_line([(16.4, 87.0), (18.75, 87.0)], None, "OPTIONAL_MANY")

    # 2. users -> app_sessions (identifying relationship: has_session)
    draw_relationship(14.0, 75.0, 4.8, 2.4, "Has Session", True, "#fdf4ff", "#7e22ce")
    draw_eer_relation_line([(19.5, 85.9), (19.5, 75.0), (16.4, 75.0)], "MANDATORY_ONE", None)
    draw_eer_relation_line([(11.6, 75.0), (9.6, 75.0), (9.6, 74.1)], None, "OPTIONAL_MANY")

    # 3. customers -> users (provisions)
    draw_relationship(31.25, 87.0, 4.8, 2.4, "Provisions", False, "#fef3c7", "#b45309")
    draw_eer_relation_line([(38.0, 87.0), (33.65, 87.0)], "OPTIONAL_ONE", None)
    draw_eer_relation_line([(28.85, 87.0), (24.25, 87.0)], None, "OPTIONAL_ONE")

    # 4. customers -> vehicles (owns)
    draw_relationship(52.0, 87.0, 4.8, 2.4, "Owns", False, "#fef3c7", "#15803d")
    draw_eer_relation_line([(44.0, 87.0), (49.6, 87.0)], "MANDATORY_ONE", None)
    draw_eer_relation_line([(54.4, 87.0), (60.25, 87.0)], None, "MANDATORY_MANY")

    # 5. insurance_plans -> vehicle_policies (defines)
    draw_relationship(15.5, 51.0, 4.8, 2.4, "Defines", False, "#fef3c7", "#b45309")
    draw_eer_relation_line([(10.6, 51.0), (13.1, 51.0)], "MANDATORY_ONE", None)
    draw_eer_relation_line([(17.9, 51.0), (20.4, 51.0)], None, "MANDATORY_MANY")

    # 6. vehicles -> vehicle_policies (insured_under)
    draw_relationship(32.0, 60.5, 5.2, 2.4, "Insured Under", False, "#fef3c7", "#b45309")
    draw_eer_relation_line([(63.0, 85.9), (63.0, 60.5), (34.6, 60.5)], "MANDATORY_ONE", None)
    draw_eer_relation_line([(29.4, 60.5), (24.0, 60.5), (24.0, 52.1)], None, "MANDATORY_MANY")

    # 7. vehicles -> vehicle_images (contains - identifying)
    draw_relationship(53.0, 64.0, 5.0, 2.4, "Contains", True, "#fdf4ff", "#0284c7")
    draw_eer_relation_line([(61.0, 85.9), (61.0, 64.0), (55.5, 64.0)], "MANDATORY_ONE", None)
    draw_eer_relation_line([(50.5, 64.0), (43.0, 64.0), (43.0, 52.1)], None, "MANDATORY_MANY")

    # 8. vehicles -> analyses (subject_of)
    draw_relationship(65.0, 69.0, 5.0, 2.4, "Subject Of", False, "#fef3c7", "#0284c7")
    draw_eer_relation_line([(64.5, 85.9), (64.5, 70.2)], "MANDATORY_ONE", None)
    draw_eer_relation_line([(65.0, 67.8), (65.0, 52.1)], None, "MANDATORY_MANY")

    # 9. vehicle_images -> analyses (feeds)
    draw_relationship(54.0, 51.0, 4.8, 2.4, "Feeds", False, "#fef3c7", "#0284c7")
    draw_eer_relation_line([(46.4, 51.0), (51.6, 51.0)], "MANDATORY_ONE", None)
    draw_eer_relation_line([(56.4, 51.0), (62.25, 51.0)], None, "MANDATORY_MANY")

    # 10. users -> analyses (performs)
    draw_relationship(76.0, 69.0, 5.0, 2.4, "Performs", False, "#fef3c7", "#1d4ed8")
    draw_eer_relation_line([(21.5, 88.1), (21.5, 96.0), (76.0, 96.0), (76.0, 70.2)], "MANDATORY_ONE", None)
    draw_eer_relation_line([(76.0, 67.8), (76.0, 52.1), (67.75, 52.1)], None, "OPTIONAL_MANY")

    # 11. analyses -> inspection_notes (remarks - identifying)
    draw_relationship(77.0, 51.0, 5.0, 2.4, "Remarks", True, "#fdf4ff", "#0284c7")
    draw_eer_relation_line([(67.75, 51.0), (74.5, 51.0)], "MANDATORY_ONE", None)
    draw_eer_relation_line([(79.5, 51.0), (85.25, 51.0)], None, "OPTIONAL_MANY")

    # 12. users -> inspection_notes (authors)
    draw_relationship(89.0, 69.0, 4.8, 2.4, "Authors", False, "#fef3c7", "#1d4ed8")
    draw_eer_relation_line([(76.0, 96.0), (89.0, 96.0), (89.0, 70.2)], None, None)
    draw_eer_relation_line([(89.0, 67.8), (89.0, 52.1)], None, "OPTIONAL_MANY")

    # 13. analyses -> reports (publishes - identifying)
    draw_relationship(65.0, 33.0, 5.0, 2.4, "Publishes", True, "#fdf4ff", "#7e22ce")
    draw_eer_relation_line([(65.0, 49.9), (65.0, 34.2)], "MANDATORY_ONE", None)
    draw_eer_relation_line([(65.0, 31.8), (65.0, 17.1)], None, "MANDATORY_ONE")

    # 14. analyses -> analysis_damages (detects - identifying)
    draw_relationship(48.0, 33.0, 5.0, 2.4, "Detects", True, "#fdf4ff", "#0f766e")
    draw_eer_relation_line([(62.5, 33.0), (50.5, 33.0)], "MANDATORY_ONE", None)
    draw_eer_relation_line([(45.5, 33.0), (35.0, 33.0), (35.0, 17.1)], None, "OPTIONAL_MANY")

    # 15. damage_catalog -> analysis_damages (prices)
    draw_relationship(22.5, 16.0, 4.8, 2.4, "Prices", False, "#fef3c7", "#0f766e")
    draw_eer_relation_line([(13.75, 16.0), (20.1, 16.0)], "MANDATORY_ONE", None)
    draw_eer_relation_line([(24.9, 16.0), (31.1, 16.0)], None, "OPTIONAL_MANY")

    # 16. users -> reports (generates)
    draw_relationship(52.0, 24.5, 5.0, 2.4, "Generates", False, "#fef3c7", "#1d4ed8")
    draw_eer_relation_line([(21.5, 85.9), (21.5, 24.5), (49.5, 24.5)], "MANDATORY_ONE", None)
    draw_eer_relation_line([(54.5, 24.5), (65.0, 24.5)], None, "OPTIONAL_MANY")

    # 17. users -> audit_logs (logs - identifying)
    draw_relationship(85.0, 33.0, 5.0, 2.4, "Logs", True, "#fdf4ff", "#334155")
    draw_eer_relation_line([(89.0, 96.0), (98.0, 96.0), (98.0, 33.0), (87.5, 33.0)], None, None)
    draw_eer_relation_line([(85.0, 31.8), (85.0, 17.1)], None, "OPTIONAL_MANY")

    # 18. company_profile -> reports (brands)
    draw_relationship(76.0, 24.5, 5.0, 2.4, "Brands", False, "#fef3c7", "#334155")
    draw_eer_relation_line([(88.0, 85.9), (88.0, 80.0), (95.5, 80.0), (95.5, 24.5), (78.5, 24.5)], "MANDATORY_ONE", None)
    draw_eer_relation_line([(73.5, 24.5), (65.0, 24.5)], None, "MANDATORY_MANY")

    # Caption Title at Bottom
    ax.text(50.0, 0.8, "Figure 4.3: Enhanced Entity-Relationship (EER) Diagram - Entity Sets, Weak Entities, Attributes, Identifying Relationships, and Structural Constraints",
            fontsize=9.8, fontweight='bold', color="#0f172a", ha='center', va='center')

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"EER diagram with COMPANY_PROFILE relationship successfully generated at: {output_path}")

if __name__ == "__main__":
    out_dir = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\reports\uml_diagrams"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "er_diagram.png")
    draw_chen_eer_diagram(out_file)
