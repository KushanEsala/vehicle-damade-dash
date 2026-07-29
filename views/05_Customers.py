from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from database.connection import get_db_session
from services.customer_service import CustomerService
from ui.layout import render_page_header

render_page_header("Customer Policyholder Register", "Search, register, and maintain policyholder files", "CUSTOMERS", allowed_roles=["admin", "operator"])

operator_id = st.session_state.get("user_id")
if not operator_id:
    st.error("A valid signed-in operator is required.")
    st.stop()

tab_list, tab_create = st.tabs(["Customer Directory", "Register New Customer"])

with tab_list:
    search_query = st.text_input("Search Customer Directory (Name, Code, Phone, Email, NIC)", "")
    with get_db_session() as session:
        c_service = CustomerService(session)
        if search_query:
            c_list = c_service.search_customers(search_query)
        else:
            c_list = c_service.list_customers()

        if not c_list:
            st.info("No customers found matching search criteria.")
        else:
            table_data = [
                {
                    "Code": c.customer_code,
                    "Full Name": c.full_name,
                    "NIC/Passport": c.nic_or_passport or "N/A",
                    "Primary Phone": c.phone_primary,
                    "Email": c.email,
                    "City": c.city,
                    "Status": c.status.upper(),
                }
                for c in c_list
            ]
            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

with tab_create:
    with st.form("create_customer_form"):
        c1, c2 = st.columns(2)
        with c1:
            full_name = st.text_input("Full Name *", placeholder="Sunil Perera")
            nic_or_passport = st.text_input("NIC or Passport Number", placeholder="198812345678")
            phone_primary = st.text_input("Primary Phone *", placeholder="+94 77 123 4567")
            phone_secondary = st.text_input("Secondary Phone", placeholder="+94 11 234 5678")
        with c2:
            email = st.text_input("Email Address *", placeholder="sunil@example.lk")
            address_line_1 = st.text_input("Address Line 1 *", placeholder="45 Temple Road")
            address_line_2 = st.text_input("Address Line 2", placeholder="Nawala")
            city = st.text_input("City *", placeholder="Rajagiriya")

        st.divider()
        create_account = st.checkbox("Create Policyholder Login Account for Customer Portal", value=True)

        submit = st.form_submit_button("Register Customer File", type="primary", use_container_width=True)

        if submit:
            try:
                with get_db_session() as session:
                    c_service = CustomerService(session)
                    customer, temp_p = c_service.create_customer(
                        full_name=full_name,
                        phone_primary=phone_primary,
                        email=email,
                        address_line_1=address_line_1,
                        city=city,
                        operator_user_id=operator_id,
                        nic_or_passport=nic_or_passport,
                        phone_secondary=phone_secondary,
                        address_line_2=address_line_2,
                        create_user_account=create_account,
                    )
                    code = customer.customer_code
                    c_id = customer.id
                st.success(f"Customer registered successfully! Assigned Code: {code}")
                if temp_p:
                    st.info(f"Customer portal login generated: Username: `cus_{c_id}` | Temporary Password:")
                    st.code(temp_p)
            except Exception as e:
                st.error(str(e))
