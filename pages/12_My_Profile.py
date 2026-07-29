from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from database.connection import get_db_session
from services.authentication_service import AuthenticationService
from ui.layout import render_page_header

render_page_header("My Account Profile", "View your credentials and update your password", "USER PROFILE", allowed_roles=["admin", "operator", "customer"])

user_id = st.session_state.get("user_id") or 1
role = st.session_state.get("role_code") or "admin"

st.markdown(
    f"""
    <div class="erp-card">
      <p><b>Username:</b> <code>{st.session_state.get('username') or 'admin'}</code></p>
      <p><b>Email:</b> {st.session_state.get('user_email') or 'admin@apexinsurance.lk'}</p>
      <p><b>Assigned Role:</b> <span class="badge badge-verified">{role.upper()}</span></p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()
st.markdown("### Update Password")

with st.form("profile_change_password_form"):
    curr_p = st.text_input("Current Password", type="password")
    new_p = st.text_input("New Password", type="password")
    conf_p = st.text_input("Confirm New Password", type="password")
    submit = st.form_submit_button("Update Password", type="primary")

    if submit:
        if new_p != conf_p:
            st.error("New password and confirmation do not match.")
        else:
            try:
                with get_db_session() as session:
                    auth_service = AuthenticationService(session)
                    auth_service.change_password(user_id, curr_p, new_p)
                st.success("Password changed successfully!")
            except Exception as e:
                st.error(str(e))
