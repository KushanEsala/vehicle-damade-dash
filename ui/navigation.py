from __future__ import annotations

import streamlit as st
from core.constants import RoleCode
from core.session import get_current_role, logout_user, is_authenticated


def render_navigation() -> str | None:
    """
    Renders role-specific navigation sidebar and returns the selected page identifier.
    """
    if not is_authenticated():
        return "login"

    role = get_current_role()

    with st.sidebar:
        st.markdown(
            """
            <div style="padding-bottom: 1rem; border-bottom: 1px solid #26313D; margin-bottom: 1rem;">
              <div style="font-weight: 800; font-size: 1.1rem; color: #50DBB7;">
                APEX INSURANCE ERP
              </div>
              <div style="font-size: 0.8rem; color: #91A1AE;">Vehicle Damage Inspection</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(f"Logged in as: **{st.session_state.get('username')}** ({role.upper() if role else 'GUEST'})")

        if role == RoleCode.ADMIN:
            options = {
                "admin_dashboard": "Admin Dashboard",
                "customers": "Customers",
                "vehicles": "Vehicles",
                "analysis_new": "New Analysis",
                "reports": "Damage Reports",
                "users": "User Management",
                "plans": "Insurance Plans",
                "company_settings": "Company Settings",
                "audit_logs": "Audit Logs",
                "profile": "My Profile",
            }
        elif role == RoleCode.OPERATOR:
            options = {
                "operator_dashboard": "Operator Workspace",
                "customers": "Customers",
                "vehicles": "Vehicles",
                "analysis_new": "New Analysis",
                "reports": "Damage Reports",
                "profile": "My Profile",
            }
        elif role == RoleCode.CUSTOMER:
            options = {
                "customer_dashboard": "Customer Portal",
                "vehicles": "My Vehicles",
                "reports": "My Damage Reports",
                "profile": "My Profile",
            }
        else:
            options = {"login": "Login"}

        selected_key = st.radio("Navigation", list(options.keys()), format_func=lambda k: options[k], label_visibility="collapsed")

        st.divider()
        if st.button("Sign Out", use_container_width=True):
            logout_user()
            st.rerun()

        return selected_key
