from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from database.connection import get_db_session
from services.vehicle_service import VehicleService
from services.customer_service import CustomerService
from services.plan_service import PlanService
from ui.layout import render_page_header

render_page_header("Insured Vehicle Register", "Register vehicles, upload inspection images, and assign policy plans", "VEHICLES", allowed_roles=["admin", "operator"])

operator_id = st.session_state.get("user_id") or 1

tab_list, tab_register, tab_upload = st.tabs(["Vehicle Directory", "Register New Vehicle", "Upload Inspection Image"])

with tab_list:
    with get_db_session() as session:
        v_service = VehicleService(session)
        vehicles_list = v_service.list_all_vehicles()

        table_data = []
        for v in vehicles_list:
            table_data.append({
                "Code": v.vehicle_code,
                "Reg Number": v.registration_number,
                "Owner": v.customer.full_name if v.customer else "N/A",
                "Make / Model": f"{v.make} {v.model}",
                "Year": v.manufactured_year or "N/A",
                "Colour": v.colour,
                "Type": v.vehicle_type,
                "Status": v.status.upper(),
            })

    if not table_data:
        st.info("No vehicle records registered yet.")
    else:
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

with tab_register:
    with get_db_session() as session:
        c_service = CustomerService(session)
        p_service = PlanService(session)
        customers = c_service.list_customers()
        plans = p_service.list_active_plans()

        customer_opts = [{"id": c.id, "display": f"{c.full_name} ({c.customer_code})"} for c in customers]
        plan_opts = [{"id": p.id, "display": f"{p.name} ({p.currency_code} {p.deductible_amount:,.2f} deductible)"} for p in plans]

    if not customer_opts:
        st.warning("Please register at least one customer in 05_Customers before registering a vehicle.")
    else:
        with st.form("register_vehicle_form"):
            c_index = st.selectbox("Vehicle Owner (Customer) *", range(len(customer_opts)), format_func=lambda i: customer_opts[i]["display"])
            target_customer_id = customer_opts[c_index]["id"]

            c1, c2 = st.columns(2)
            with c1:
                reg_num = st.text_input("Registration Number *", placeholder="CAB-1234")
                make = st.text_input("Make *", placeholder="Toyota")
                model = st.text_input("Model *", placeholder="Prius")
                colour = st.text_input("Colour *", placeholder="Pearl White")
            with c2:
                chassis = st.text_input("Chassis Number", placeholder="JTDKN36U001234567")
                engine = st.text_input("Engine Number", placeholder="2ZR-123456")
                year = st.number_input("Manufactured Year", min_value=1950, max_value=2030, value=2020)
                v_type = st.selectbox("Vehicle Type", ["Car", "Motorcycle", "Bus", "Truck"])

            st.divider()
            if plan_opts:
                p_index = st.selectbox("Insurance Plan", range(len(plan_opts)), format_func=lambda i: plan_opts[i]["display"])
                target_plan_id = plan_opts[p_index]["id"]
            else:
                target_plan_id = None

            policy_num = st.text_input("Policy Number", placeholder="POL-CAB-1234")

            submit = st.form_submit_button("Register Vehicle", type="primary", use_container_width=True)

            if submit:
                try:
                    with get_db_session() as session:
                        v_service = VehicleService(session)
                        v = v_service.register_vehicle(
                            customer_id=target_customer_id,
                            registration_number=reg_num,
                            make=make,
                            model=model,
                            colour=colour,
                            operator_user_id=operator_id,
                            chassis_number=chassis,
                            engine_number=engine,
                            manufactured_year=year,
                            vehicle_type=v_type,
                            plan_id=target_plan_id,
                            policy_number=policy_num,
                        )
                        reg = v.registration_number
                        code = v.vehicle_code
                    st.success(f"Vehicle {reg} registered successfully! Assigned Code: {code}")
                except Exception as e:
                    st.error(str(e))

with tab_upload:
    with get_db_session() as session:
        v_service = VehicleService(session)
        vehicles_list = v_service.list_all_vehicles()
        veh_opts = [{"id": v.id, "display": f"{v.registration_number} — {v.make} {v.model}"} for v in vehicles_list]

    if not veh_opts:
        st.info("No registered vehicles available.")
    else:
        v_index = st.selectbox("Select Target Vehicle for Inspection Image", range(len(veh_opts)), format_func=lambda i: veh_opts[i]["display"])
        target_veh_id = veh_opts[v_index]["id"]

        uploaded_file = st.file_uploader("Choose vehicle inspection photo (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])
        category = st.selectbox("Image Category", ["profile", "front", "rear", "left", "right", "damage", "other"])

        if st.button("Save Image to Vehicle Record", type="primary"):
            if not uploaded_file:
                st.error("Please upload an image file.")
            else:
                try:
                    with get_db_session() as session:
                        v_service = VehicleService(session)
                        v_service.upload_vehicle_image(
                            vehicle_id=target_veh_id,
                            file_bytes=uploaded_file.getvalue(),
                            filename=uploaded_file.name,
                            operator_user_id=operator_id,
                            category=category,
                            is_primary=True,
                        )
                    st.success(f"Image '{uploaded_file.name}' saved to vehicle record successfully!")
                except Exception as e:
                    st.error(str(e))
