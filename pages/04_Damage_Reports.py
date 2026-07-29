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
from services.report_service import ReportService
from ui.layout import render_page_header

render_page_header("Official Damage Reports Archive", "View, filter, and download finalized PDF vehicle damage inspection reports", "REPORTS", allowed_roles=["admin", "operator", "customer"])

with get_db_session() as session:
    from database.models.report import Report as ReportModel
    from database.models.analysis import Analysis as AnalysisModel
    from database.models.vehicle import Vehicle as VehicleModel
    r_service = ReportService(session)
    reports_orm = session.query(ReportModel).options(
        joinedload(ReportModel.analysis).joinedload(AnalysisModel.vehicle).joinedload(VehicleModel.customer)
    ).all()

    reports_dicts = []
    for r in reports_orm:
        analysis = r.analysis
        vehicle = analysis.vehicle if analysis else None
        customer = vehicle.customer if vehicle else None

        reports_dicts.append({
            "id": r.id,
            "report_number": r.report_number,
            "analysis_number": analysis.analysis_number if analysis else "N/A",
            "registration_number": vehicle.registration_number if vehicle else "N/A",
            "make": vehicle.make if vehicle else "N/A",
            "model": vehicle.model if vehicle else "N/A",
            "customer_name": customer.full_name if customer else "N/A",
            "currency_code": analysis.currency_code if analysis else "LKR",
            "total_estimated_cost": analysis.total_estimated_cost if analysis else 0.0,
            "generated_at": r.generated_at,
            "revision_number": r.revision_number,
            "pdf_path": r.pdf_path
        })

if not reports_dicts:
    st.info("No generated report records found in database.")
else:
    table_data = [
        {
            "Report #": r["report_number"],
            "Analysis #": r["analysis_number"],
            "Vehicle": f"{r['registration_number']} ({r['make']} {r['model']})",
            "Customer": r["customer_name"],
            "Total Cost": f"{r['currency_code']} {r['total_estimated_cost']:,.2f}",
            "Generated At": r["generated_at"].strftime("%Y-%m-%d %H:%M"),
            "Revision": f"R{r['revision_number']:02d}",
        }
        for r in reports_dicts
    ]
    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### Download PDF Report Document")
    selected_report_dict = st.selectbox(
        "Select Report to Download",
        reports_dicts,
        format_func=lambda r: f"{r['report_number']} — {r['registration_number']}"
    )

    if selected_report_dict:
        with get_db_session() as session:
            r_service = ReportService(session)
            abs_path = r_service.storage.get_absolute_path(selected_report_dict["pdf_path"])
            if abs_path.is_file():
                st.download_button(
                    f"Download {selected_report_dict['report_number']}.pdf",
                    data=abs_path.read_bytes(),
                    file_name=f"{selected_report_dict['report_number']}.pdf",
                    mime="application/pdf",
                    type="primary",
                )
            else:
                st.error("Report PDF file not found on disk storage.")
