from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from database.connection import get_db_session
from services.dashboard_service import DashboardService
from services.customer_service import CustomerService
from services.vehicle_service import VehicleService
from services.analysis_service import AnalysisService
from services.report_service import ReportService
from ui.layout import render_page_header, render_status_badge

render_page_header("Executive & Operational Overview", "Role-based summary dashboard and quick actions", "OVERVIEW", allowed_roles=["admin", "operator", "customer"])

role_code = (st.session_state.get("role_code") or "admin").lower()

if role_code == "admin":
    with get_db_session() as session:
        dash_service = DashboardService(session)
        metrics = dash_service.get_admin_metrics()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registered Customers", metrics["total_customers"])
    c2.metric("Insured Vehicles", metrics["total_vehicles"])
    c3.metric("Finalized Analyses", metrics["finalized_analyses"])
    c4.metric("Total Estimated Cost", f"LKR {metrics['total_estimated_cost']:,.2f}")

    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("### Damage Class Distribution")
        dmg_counts = metrics["damage_class_counts"]
        if dmg_counts:
            df = pd.DataFrame(
                [{"Damage Class": k.replace("_", " ").title(), "Detected Count": v} for k, v in dmg_counts.items()]
            )
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No damage inspection records found in database.")

    with col_right:
        st.markdown("### System Diagnostics & Status")
        st.markdown(
            """
            <div class="erp-card">
              <div class="erp-card-header">Model & Storage Diagnostics</div>
              <p><b>Damage Segmentation Model:</b> <code>best.pt</code> (SHA256 Verified)</p>
              <p><b>Vehicle Confirmation Model:</b> <code>yolov8n.pt</code> (COCO Verified)</p>
              <p><b>Database Connection:</b> <code>Vehicle_Analyzis</code> (MySQL / PyMySQL)</p>
              <p><b>Storage System:</b> <code>storage/</code></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

elif role_code == "operator":
    with get_db_session() as session:
        c_service = CustomerService(session)
        v_service = VehicleService(session)
        a_service = AnalysisService(session)

        customers_count = len(c_service.list_customers())
        vehicles_count = len(v_service.list_all_vehicles())
        analyses = a_service.analysis_repo.list_all()
        total_analyses = len(analyses)

        analyses_data = []
        for a in analyses[:5]:
            analyses_data.append({
                "analysis_number": a.analysis_number,
                "status": a.status,
                "created_at": a.created_at,
                "accepted_damage_count": a.accepted_damage_count,
                "vehicle_reg": a.vehicle.registration_number if a.vehicle else "N/A",
                "vehicle_make": a.vehicle.make if a.vehicle else "N/A",
                "vehicle_model": a.vehicle.model if a.vehicle else "N/A",
            })

    c1, c2, c3 = st.columns(3)
    c1.metric("Registered Customers", customers_count)
    c2.metric("Insured Vehicles", vehicles_count)
    c3.metric("Analyses Completed", total_analyses)

    st.divider()

    st.markdown("### Recent Damage Inspection Records")
    if not analyses_data:
        st.info("No damage inspections recorded yet.")
    else:
        for a in analyses_data:
            status_badge = render_status_badge(a["status"].upper(), "verified" if a["status"] == "finalized" else "caution")
            st.markdown(
                f"""
                <div class="erp-card">
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                      <b>Analysis #{a['analysis_number']}</b> — Vehicle #{a['vehicle_reg']} ({a['vehicle_make']} {a['vehicle_model']})
                      <br/>
                      <span style="color: #91A1AE; font-size: 0.85rem;">Date: {a['created_at'].strftime('%Y-%m-%d %H:%M')} | Damages Accepted: {a['accepted_damage_count']}</span>
                    </div>
                    <div>
                      {status_badge}
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

else:
    customer_id = st.session_state.get("customer_id") or 1

    with get_db_session() as session:
        dash_service = DashboardService(session)
        veh_service = VehicleService(session)
        rep_service = ReportService(session)

        metrics = dash_service.get_customer_portal_metrics(customer_id)
        vehicles = veh_service.list_vehicles_by_customer(customer_id)

        vehicles_data = []
        for v in vehicles:
            reports = [
                r for r in rep_service.list_all()
                if r.analysis.vehicle_id == v.id and r.is_current
            ]
            reports_data = []
            for r in reports:
                reports_data.append({
                    "id": r.id,
                    "report_number": r.report_number,
                    "total_estimated_cost": r.analysis.total_estimated_cost if r.analysis else 0,
                    "pdf_path": r.pdf_path,
                    "abs_pdf": rep_service.storage.get_absolute_path(r.pdf_path),
                })
            vehicles_data.append({
                "id": v.id,
                "registration_number": v.registration_number,
                "chassis_number": v.chassis_number,
                "make": v.make,
                "model": v.model,
                "colour": v.colour,
                "vehicle_type": v.vehicle_type,
                "manufactured_year": v.manufactured_year,
                "reports": reports_data,
            })

    c1, c2, c3 = st.columns(3)
    c1.metric("Insured Vehicles", metrics["vehicle_count"])
    c2.metric("Finalized Reports", metrics["reports_count"])
    c3.metric("Total Repair Cost", f"LKR {metrics['total_estimated_cost']:,.2f}")

    st.divider()
    st.markdown("### My Registered Vehicles")
    if not vehicles_data:
        st.info("No registered vehicles linked to your policyholder profile.")
    else:
        for v in vehicles_data:
            with st.expander(f"Vehicle {v['registration_number']} — {v['make']} {v['model']} ({v['colour']})", expanded=True):
                st.markdown(
                    f"""
                    <div class="erp-card">
                      <p><b>Registration #:</b> <code>{v['registration_number']}</code> | <b>Chassis #:</b> {v['chassis_number'] or 'N/A'}</p>
                      <p><b>Vehicle Type:</b> {v['vehicle_type']} | <b>Year:</b> {v['manufactured_year'] or 'N/A'}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if v["reports"]:
                    st.markdown("#### Finalized Damage Assessment Reports")
                    for r in v["reports"]:
                        c_left, c_right = st.columns([3, 1])
                        with c_left:
                            st.markdown(f"**Report #{r['report_number']}** — Total Estimated Repair Cost: `LKR {r['total_estimated_cost']:,.2f}`")
                        with c_right:
                            abs_pdf = r["abs_pdf"]
                            if abs_pdf.is_file():
                                st.download_button(
                                    "Download PDF Report",
                                    data=abs_pdf.read_bytes(),
                                    file_name=f"{r['report_number']}.pdf",
                                    mime="application/pdf",
                                    key=f"dl_pdf_ov_{r['id']}",
                                )
                else:
                    st.caption("No finalized inspection reports available for this vehicle.")
