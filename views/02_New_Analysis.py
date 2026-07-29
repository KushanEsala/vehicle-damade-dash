from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from database.connection import get_db_session
from services.customer_service import CustomerService
from services.vehicle_service import VehicleService
from services.analysis_service import AnalysisService
from ui.layout import render_page_header, render_evidence_rail

render_page_header("New AI Damage Inspection", "Execute YOLO vehicle confirmation and damage segmentation model on inspection photo", "ANALYSIS WORKSPACE", allowed_roles=["admin", "operator"])

render_evidence_rail(current_step=3)

operator_id = st.session_state.get("user_id")
if not operator_id:
    st.error("A valid signed-in operator is required.")
    st.stop()

with get_db_session() as session:
    c_service = CustomerService(session)
    customers = c_service.list_customers()
    customer_options = [{"id": c.id, "display": f"{c.full_name} ({c.customer_code})"} for c in customers]

if not customer_options:
    st.warning("No customer policyholders registered in system. Register a customer first in 05_Customers.")
else:
    st.markdown("### 1. Select Customer & Vehicle File")
    col_cust, col_veh = st.columns(2)
    with col_cust:
        selected_c_index = st.selectbox(
            "Customer Profile",
            range(len(customer_options)),
            format_func=lambda i: customer_options[i]["display"]
        )
        selected_customer_id = customer_options[selected_c_index]["id"]

    with get_db_session() as session:
        v_service = VehicleService(session)
        customer_vehicles = v_service.list_vehicles_by_customer(selected_customer_id)
        vehicle_options = [{"id": v.id, "display": f"{v.registration_number} — {v.make} {v.model}"} for v in customer_vehicles]

    with col_veh:
        if not vehicle_options:
            st.error("Selected customer has no registered vehicles. Register a vehicle in 06_Vehicles.")
            selected_vehicle_id = None
        else:
            selected_v_index = st.selectbox(
                "Insured Vehicle",
                range(len(vehicle_options)),
                format_func=lambda i: vehicle_options[i]["display"]
            )
            selected_vehicle_id = vehicle_options[selected_v_index]["id"]

    if selected_vehicle_id:
        st.divider()
        st.markdown("### 2. Model Detection Controls & Thresholds")
        st.caption("Adjust confidence parameters directly on this control panel before executing inference.")

        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
        with ctrl_col1:
            damage_confidence = st.slider("Damage Confidence Threshold", 0.10, 0.90, 0.30, 0.05)
        with ctrl_col2:
            vehicle_confidence = st.slider("Vehicle Confirmation Threshold", 0.10, 0.90, 0.25, 0.05)
        with ctrl_col3:
            st.write("")
            st.write("")
            require_vehicle = st.toggle("Require Vehicle Confirmation Gate", value=True)

        st.divider()

        st.markdown("### 3. Upload Inspection Photo & Run AI Inference")
        uploaded_image = st.file_uploader("Upload vehicle photo (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])

        if uploaded_image:
            st.image(uploaded_image, caption="Source Inspection Photo", use_container_width=True)

            if st.button("Run AI Damage Inspection Pipeline", type="primary", use_container_width=True):
                with st.spinner("Executing YOLO vehicle confirmation and damage segmentation..."):
                    try:
                        file_bytes = uploaded_image.getvalue()
                        with get_db_session() as session:
                            v_service = VehicleService(session)
                            a_service = AnalysisService(session)

                            v_img = v_service.upload_vehicle_image(
                                vehicle_id=selected_vehicle_id,
                                file_bytes=file_bytes,
                                filename=uploaded_image.name,
                                operator_user_id=operator_id,
                                category="damage",
                            )

                            analysis = a_service.run_new_analysis(
                                vehicle_id=selected_vehicle_id,
                                source_image_id=v_img.id,
                                operator_user_id=operator_id,
                                image_bytes=file_bytes,
                                damage_confidence=damage_confidence,
                                vehicle_confidence=vehicle_confidence,
                                require_vehicle_confirmation=require_vehicle,
                            )
                            analysis_id = analysis.id
                            analysis_num = analysis.analysis_number

                        st.session_state["active_analysis_id"] = analysis_id
                        st.success(f"Analysis completed successfully! Case Analysis #: {analysis_num}")
                        st.info("Switch to 03_Analysis_Review to inspect predictions and edit repair cost items.")
                    except Exception as e:
                        st.error(f"Inference failed: {e}")
