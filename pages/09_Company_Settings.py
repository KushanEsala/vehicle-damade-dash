from __future__ import annotations

import sys
from pathlib import Path
from decimal import Decimal
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from database.connection import get_db_session
from database.models.company import CompanyInformation
from ui.layout import render_page_header

render_page_header("Company Profile & Report Settings", "Update official company details, currency, tax rates, and PDF report footer text", "ADMINISTRATION", allowed_roles=["admin"])

admin_id = st.session_state.get("user_id") or 1

with get_db_session() as session:
    company = session.query(CompanyInformation).first()
    if company:
        company_dict = {
            "id": company.id,
            "company_name": company.company_name,
            "registration_number": company.registration_number,
            "phone": company.phone,
            "email": company.email,
            "website": company.website,
            "address_line_1": company.address_line_1,
            "address_line_2": company.address_line_2,
            "city": company.city,
            "currency_code": company.currency_code,
            "tax_label": company.tax_label,
            "tax_rate": company.tax_rate,
            "report_footer": company.report_footer
        }
    else:
        company_dict = None

if not company_dict:
    st.warning("Company information record not found.")
else:
    with st.form("company_settings_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Company Name", value=company_dict["company_name"])
            reg_num = st.text_input("Registration Number", value=company_dict["registration_number"])
            phone = st.text_input("Telephone", value=company_dict["phone"])
            email = st.text_input("Official Email", value=company_dict["email"])
            website = st.text_input("Website", value=company_dict["website"] or "")
        with c2:
            addr1 = st.text_input("Address Line 1", value=company_dict["address_line_1"])
            addr2 = st.text_input("Address Line 2", value=company_dict["address_line_2"] or "")
            city = st.text_input("City", value=company_dict["city"])
            currency = st.text_input("Default Currency Code", value=company_dict["currency_code"])
            tax_label = st.text_input("Tax Label", value=company_dict["tax_label"])
            tax_rate = st.number_input("Tax Rate (e.g. 0.15 = 15%)", value=float(company_dict["tax_rate"]), min_value=0.0, max_value=1.0, step=0.01)

        footer = st.text_area("Report Disclaimer Footer", value=company_dict["report_footer"] or "")

        submit = st.form_submit_button("Save Company Settings", type="primary", use_container_width=True)

        if submit:
            try:
                with get_db_session() as session:
                    comp = session.query(CompanyInformation).filter(CompanyInformation.id == company_dict["id"]).first()
                    if comp:
                        comp.company_name = name.strip()
                        comp.registration_number = reg_num.strip()
                        comp.phone = phone.strip()
                        comp.email = email.strip()
                        comp.website = website.strip()
                        comp.address_line_1 = addr1.strip()
                        comp.address_line_2 = addr2.strip()
                        comp.city = city.strip()
                        comp.currency_code = currency.strip().upper()
                        comp.tax_label = tax_label.strip()
                        comp.tax_rate = Decimal(str(tax_rate))
                        comp.report_footer = footer.strip()
                        comp.updated_by = admin_id
                st.success("Company settings updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(str(e))
