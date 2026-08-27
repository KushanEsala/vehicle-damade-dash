import os
import shutil

user_uploaded_dir = r"C:\Users\Hello\.gemini\antigravity\brain\5d3dcfee-256c-44d5-be3d-69346548a7c6\.user_uploaded"
dest_dir = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\reports\ui_screenshots"
os.makedirs(dest_dir, exist_ok=True)

mapping = {
    # Sign in
    "ui_01_signin_admin.png": "media_1787149422059.png",
    "ui_01b_signin_operator.png": "media_1787149431888.png",
    "ui_01c_signin_customer.png": "media_1787149446137.png",
    # Dashboard & Management
    "ui_02_dashboard_admin.png": "media_1787149422065.png",
    "ui_03_customer_registration.png": "media_1787149438309.png",
    "ui_04_customer_records_list.png": "media_1787149438335.png",
    "ui_05_vehicle_registration.png": "media_1787149438332.png",
    "ui_06_insurance_plans.png": "media_1787149446152.png",
    "ui_07_new_assessment_upload.png": "media_1787149422057.png",
    "ui_07b_new_assessment_operator.png": "media_1787149438313.png",
    # AI Detection & Review
    "ui_08_damage_visualizer_canvas.png": "media_1787149422089.png",
    "ui_09_assessment_review_header.png": "media_1787149422106.png",
    "ui_10_damage_summary_editor.png": "media_1787149431878.png",
    "ui_11_damage_reports_archive.png": "media_1787149431881.png",
    # PDF Generated Reports
    "ui_12_pdf_report_page1.png": "media_1787149431876.png",
    "ui_13_pdf_report_page2.png": "media_1787149438324.png",
    # User Admin & Customer Portal
    "ui_14_user_management.png": "media_1787149431859.png",
    "ui_15_customer_portal_dashboard.png": "media_1787149446131.png",
    "ui_16_customer_portal_assessments.png": "media_1787149446153.png",
    "ui_17_customer_portal_vehicles.png": "media_1787149446251.png",
}

for dest_name, src_name in mapping.items():
    src_path = os.path.join(user_uploaded_dir, src_name)
    dest_path = os.path.join(dest_dir, dest_name)
    if os.path.exists(src_path):
        shutil.copyfile(src_path, dest_path)
        print(f"Copied {src_name} -> {dest_name}")
    else:
        print(f"WARNING: Source {src_name} not found in {user_uploaded_dir}")

print("\nListing files in destination:")
for f in sorted(os.listdir(dest_dir)):
    print(f, os.path.getsize(os.path.join(dest_dir, f)), "bytes")
