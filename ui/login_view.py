from __future__ import annotations

import streamlit as st
from database.connection import get_db_session
from services.authentication_service import AuthenticationService
from core.session import login_user, is_authenticated
from ui.theme import inject_custom_theme


def render_login_page() -> None:
    """
    Renders the primary Login Landing Page and stops further script execution if unauthenticated.
    Hides sidebar completely when not logged in.
    """
    inject_custom_theme()

    # Hide sidebar completely when not authenticated
    st.markdown(
        """
        <style>
          [data-testid="stSidebar"] { display: none !important; }
          [data-testid="stSidebarNav"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if is_authenticated():
        return

    # Header section
    st.markdown(
        """
        <div style="text-align: center; margin-top: 1.5rem; margin-bottom: 2rem;">
          <div style="color: #50DBB7; font-size: 0.85rem; font-weight: 800; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 0.5rem;">
            APEX INSURANCE ERP
          </div>
          <h1 style="font-size: 2.6rem; font-weight: 800; color: #E9F0F5; margin: 0; line-height: 1.15;">
            Vehicle Damage Assessment System
          </h1>
          <p style="color: #91A1AE; font-size: 1.05rem; margin-top: 0.5rem;">
            Sign in to access your role-based insurance workspace
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Centered Login Card
    col_left, col_card, col_right = st.columns([1, 2.2, 1])

    with col_card:
        st.markdown(
            """
            <div class="erp-card" style="border-top: 4px solid #50DBB7; padding: 2rem 2.2rem;">
              <h3 style="margin-top: 0; color: #E9F0F5; font-size: 1.3rem;">System Authentication</h3>
              <p style="color: #91A1AE; font-size: 0.88rem; margin-bottom: 1.5rem;">
                Enter your system credentials below to continue.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            username_input = st.text_input("Username or Email Address", value="admin", placeholder="e.g. admin or operator_john")
            password_input = st.text_input("Password", type="password", value="Admin@123456", placeholder="••••••••••••")

            submit_btn = st.form_submit_button("Sign In to ERP Portal", type="primary", use_container_width=True)

            if submit_btn:
                if not username_input or not password_input:
                    st.error("Please enter both username/email and password.")
                else:
                    try:
                        with get_db_session() as session:
                            auth_service = AuthenticationService(session)
                            user = auth_service.authenticate(username_input.strip(), password_input)

                            u_id = user.id
                            u_name = user.username
                            u_email = user.email
                            u_role = user.role.code if user.role else "admin"
                            u_cust_id = user.customer_id
                            u_must_change = user.must_change_password

                        login_user(
                            user_id=u_id,
                            username=u_name,
                            email=u_email,
                            role_code=u_role,
                            customer_id=u_cust_id,
                            must_change_password=u_must_change,
                        )
                        st.success(f"Welcome back, {u_name}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Authentication Failed: {e}")

        st.markdown(
            """
            <div style="margin-top: 1.5rem; padding: 1rem 1.2rem; background: #101820; border: 1px solid #26313D; border-radius: 12px; font-size: 0.88rem; color: #91A1AE;">
              <b>Default Credentials for Testing:</b><br/>
              • <b>Administrator</b>: <code>admin</code> / <code>Admin@123456</code>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Halt execution so unauthenticated users CANNOT see any page content
    st.stop()
