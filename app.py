from __future__ import annotations

import streamlit as st

from core.session import (
    check_session_timeout,
    get_current_role,
    init_session_state,
    is_authenticated,
)
from database.connection import ensure_database_ready
from ui.layout import render_sidebar_footer, render_sidebar_identity
from ui.login_view import render_login_page
from ui.theme import inject_custom_theme


st.set_page_config(
    page_title="Apex Vehicle Assurance",
    page_icon=":material/shield:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={},
)

init_session_state()
inject_custom_theme()
ensure_database_ready()

if check_session_timeout():
    st.warning("Your session expired after a period of inactivity. Sign in again.")

if not is_authenticated():
    render_login_page()
    st.stop()

role = get_current_role()
if role not in {"admin", "operator", "customer"}:
    st.error("This account has no valid application role. Contact an administrator.")
    st.stop()

if role == "customer" and not st.session_state.get("customer_id"):
    st.error("This customer account is not linked to a policyholder record. Contact the insurance company.")
    st.stop()

common = [
    st.Page("views/01_Overview.py", title="Overview", icon=":material/dashboard:", default=True),
]

if role == "admin":
    pages = {
        "Workspace": common
        + [
            st.Page("views/02_New_Analysis.py", title="New analysis", icon=":material/document_scanner:"),
            st.Page("views/03_Analysis_Review.py", title="Analysis review", icon=":material/fact_check:"),
            st.Page("views/04_Damage_Reports.py", title="Damage reports", icon=":material/description:"),
        ],
        "Records": [
            st.Page("views/05_Customers.py", title="Customers", icon=":material/groups:"),
            st.Page("views/06_Vehicles.py", title="Vehicles", icon=":material/directions_car:"),
            st.Page("views/07_Insurance_Plans.py", title="Insurance plans", icon=":material/verified_user:"),
        ],
        "Administration": [
            st.Page("views/08_User_Management.py", title="User management", icon=":material/manage_accounts:"),
            st.Page("views/09_Company_Settings.py", title="Company settings", icon=":material/domain:"),
            st.Page("views/10_Audit_Logs.py", title="Audit logs", icon=":material/history:"),
            st.Page("views/11_Model_Tester.py", title="Model diagnostics", icon=":material/model_training:"),
            st.Page("views/12_My_Profile.py", title="My profile", icon=":material/account_circle:"),
        ],
    }
elif role == "operator":
    pages = {
        "Workspace": common
        + [
            st.Page("views/02_New_Analysis.py", title="New analysis", icon=":material/document_scanner:"),
            st.Page("views/03_Analysis_Review.py", title="Analysis review", icon=":material/fact_check:"),
            st.Page("views/04_Damage_Reports.py", title="Damage reports", icon=":material/description:"),
        ],
        "Records": [
            st.Page("views/05_Customers.py", title="Customers", icon=":material/groups:"),
            st.Page("views/06_Vehicles.py", title="Vehicles", icon=":material/directions_car:"),
            st.Page("views/07_Insurance_Plans.py", title="Insurance plans", icon=":material/verified_user:"),
        ],
        "Account": [
            st.Page("views/12_My_Profile.py", title="My profile", icon=":material/account_circle:"),
        ],
    }
else:
    pages = {
        "My insurance": common
        + [
            st.Page("views/03_Analysis_Review.py", title="My assessments", icon=":material/fact_check:"),
            st.Page("views/04_Damage_Reports.py", title="My damage reports", icon=":material/description:"),
            st.Page("views/12_My_Profile.py", title="My profile", icon=":material/account_circle:"),
        ]
    }

render_sidebar_identity()
navigation = st.navigation(pages, position="sidebar", expanded=True)
render_sidebar_footer()
navigation.run()
