from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import streamlit as st
from sqlalchemy.orm import joinedload

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from database.connection import get_db_session
from services.analysis_service import AnalysisService
from services.report_service import ReportService
from ui.layout import render_page_header, render_evidence_rail

role_code = st.session_state.get("role_code")
is_customer = role_code == "customer"
render_page_header(
    "My Damage Assessments" if is_customer else "Analysis Review & Costing Workspace",
    "Review finalized vehicle findings and reports." if is_customer else "Review AI predictions, edit repair costs, and finalize the assessment.",
    "POLICYHOLDER PORTAL" if is_customer else "ANALYSIS WORKSPACE",
    allowed_roles=["admin", "operator", "customer"],
)

render_evidence_rail(current_step=4)

operator_id = st.session_state.get("user_id")
if not operator_id:
    st.error("A valid signed-in user is required.")
    st.stop()

with get_db_session() as session:
    a_service = AnalysisService(session)
    analyses_orm = a_service.analysis_repo.list_all()
    if is_customer:
        customer_id = st.session_state.get("customer_id")
        analyses_orm = [
            analysis for analysis in analyses_orm
            if analysis.status == "finalized"
            and analysis.vehicle
            and analysis.vehicle.customer_id == customer_id
        ]
    analyses_dicts = []
    for a in analyses_orm:
        analyses_dicts.append({
            "id": a.id,
            "analysis_number": a.analysis_number,
            "registration_number": a.vehicle.registration_number if a.vehicle else "Unknown",
            "status": a.status
        })

if not analyses_dicts:
    st.info("No analysis records found in database. Execute a new inspection first in 02_New_Analysis.")
else:
    active_id = st.session_state.get("active_analysis_id")
    selected_idx = 0
    if active_id:
        for i, a in enumerate(analyses_dicts):
            if a["id"] == active_id:
                selected_idx = i
                break

    selected_analysis_dict = st.selectbox(
        "Select Case Analysis Record",
        analyses_dicts,
        index=selected_idx,
        format_func=lambda a: f"{a['analysis_number']} — {a['registration_number']} ({a['status'].upper()})"
    )

    st.divider()

    with get_db_session() as session:
        from database.models.analysis import Analysis as AnalysisModel
        from database.models.vehicle import Vehicle as VehicleModel
        a_service = AnalysisService(session)
        analysis = session.query(AnalysisModel).options(
            joinedload(AnalysisModel.vehicle).joinedload(VehicleModel.images),
            joinedload(AnalysisModel.damages)
        ).filter_by(id=selected_analysis_dict["id"]).first()
        if not analysis:
            st.error("The selected assessment no longer exists.")
            st.stop()
        if is_customer and (
            not analysis.vehicle
            or analysis.vehicle.customer_id != st.session_state.get("customer_id")
            or analysis.status != "finalized"
        ):
            st.error("You do not have permission to view this assessment.")
            st.stop()

        col_img1, col_img2 = st.columns(2)
        with col_img1:
            st.markdown("### Source Inspection Photo")
            src_path = a_service.storage.get_absolute_path(analysis.vehicle.images[0].storage_path) if analysis.vehicle and analysis.vehicle.images else None
            if src_path and src_path.is_file():
                st.image(str(src_path), caption="Original Photo", use_container_width=True)
            else:
                st.info("Source image file not found on disk.")

        with col_img2:
            st.markdown("### Validated Model Damage Overlay")
            if analysis.annotated_image_path:
                ann_path = a_service.storage.get_absolute_path(analysis.annotated_image_path)
                if ann_path.is_file():
                    st.image(str(ann_path), caption="YOLO Annotated Overlay", use_container_width=True)

        st.divider()

        # Vehicle Gate Status & Override
        c_gate1, c_gate2 = st.columns([2, 1])
        with c_gate1:
            if analysis.vehicle_confirmed:
                st.success("Vehicle Confirmation Gate: PASSED (Supported vehicle detected in photo)")
            elif analysis.confirmation_overridden:
                st.warning(f"Vehicle Gate: OVERRIDDEN (Reason: '{analysis.override_reason}')")
            else:
                st.error("Vehicle Confirmation Gate: FAILED (No vehicle detected by model gate)")

        with c_gate2:
            if not is_customer and not analysis.vehicle_confirmed and not analysis.confirmation_overridden and analysis.status != "finalized":
                with st.popover("Override Vehicle Gate"):
                    reason = st.text_input("Mandatory Override Reason", placeholder="Close-up panel crop of door damage")
                    if st.button("Confirm Operator Override"):
                        try:
                            a_service.override_vehicle_confirmation(analysis.id, operator_id, reason)
                            st.success("Vehicle gate overridden successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

        st.divider()

        # Damage Table & Editing
        st.markdown("### Accepted Damage Line Items & Repair Costing")
        accepted_damages = [d for d in analysis.damages if d.passed_vehicle_gate]

        if not accepted_damages:
            st.info("No damage line items accepted for this analysis.")
        else:
            for d in accepted_damages:
                with st.expander(f"Damage #{d.id}: {d.final_damage_class.replace('_', ' ').title()} — Cost: {analysis.currency_code} {d.estimated_cost:,.2f}", expanded=True):
                    if is_customer or analysis.status == "finalized":
                        st.write(f"**Part:** {d.vehicle_part or 'General Panel'} | **Severity:** {d.severity.capitalize()} | **Cost:** {analysis.currency_code} {d.estimated_cost:,.2f}")
                        st.write(f"**Description:** {d.description or 'N/A'}")
                    else:
                        with st.form(f"edit_damage_{d.id}"):
                            f1, f2, f3 = st.columns(3)
                            with f1:
                                final_cls = st.selectbox("Damage Class", ["scratch", "dent", "tear", "missing_part", "broken_lamp", "puncture", "broken_glass"], index=["scratch", "dent", "tear", "missing_part", "broken_lamp", "puncture", "broken_glass"].index(d.final_damage_class) if d.final_damage_class in ["scratch", "dent", "tear", "missing_part", "broken_lamp", "puncture", "broken_glass"] else 0)
                                v_part = st.text_input("Vehicle Part", value=d.vehicle_part or "Front Bumper")
                            with f2:
                                sev = st.selectbox("Severity Level", ["minor", "moderate", "severe", "critical"], index=["minor", "moderate", "severe", "critical"].index(d.severity) if d.severity in ["minor", "moderate", "severe", "critical"] else 1)
                                cost = st.number_input("Estimated Repair Cost", value=float(d.estimated_cost), min_value=0.0, step=100.0)
                            with f3:
                                desc = st.text_area("Customer-Visible Description", value=d.description or "")
                                note = st.text_input("Internal Note", value=d.internal_note or "")

                            if st.form_submit_button("Save Damage Line Item"):
                                try:
                                    a_service.update_damage_item(
                                        damage_id=d.id,
                                        operator_user_id=operator_id,
                                        final_class=final_cls,
                                        severity=sev,
                                        estimated_cost=cost,
                                        vehicle_part=v_part,
                                        description=desc,
                                        internal_note=note,
                                    )
                                    st.success("Damage line item updated!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(str(e))

        st.divider()

        # Cost Totals Summary & Finalization
        st.markdown("### Analysis Financial Totals")
        t1, t2, t3 = st.columns(3)
        t1.metric("Subtotal Cost", f"{analysis.currency_code} {analysis.subtotal_cost:,.2f}")
        t2.metric("Tax Amount (VAT 15%)", f"{analysis.currency_code} {analysis.tax_amount:,.2f}")
        t3.metric("Total Estimated Cost", f"{analysis.currency_code} {analysis.total_estimated_cost:,.2f}")

        if not is_customer and analysis.status != "finalized":
            st.divider()
            st.markdown("### Finalize Assessment & Build PDF Report")
            final_notes = st.text_area("Operator Final Notes", value=analysis.operator_notes or "")
            if st.button("Finalize Analysis & Generate Official Report", type="primary", use_container_width=True):
                try:
                    r_service = ReportService(session)

                    a_service.finalize_analysis(analysis.id, operator_id, final_notes)
                    report = r_service.generate_pdf_report(analysis.id, operator_id)

                    st.success(f"Analysis #{analysis.analysis_number} finalized successfully!")
                    st.info(f"Generated PDF Report #: {report.report_number}")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        elif analysis.status == "finalized":
            st.success("This analysis is FINALIZED and locked against modification.")
            r_service = ReportService(session)
            report = r_service.report_repo.get_by_analysis_id(analysis.id)
            if report:
                abs_pdf = r_service.storage.get_absolute_path(report.pdf_path)
                if abs_pdf.is_file():
                    st.download_button(
                        "Download Official PDF Report",
                        data=abs_pdf.read_bytes(),
                        file_name=f"{report.report_number}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True,
                    )
        else:
            st.info("This assessment is still being reviewed and is not yet available in the customer portal.")
