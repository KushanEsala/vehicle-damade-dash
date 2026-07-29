from __future__ import annotations

import streamlit as st

from core.session import is_authenticated, login_user
from database.connection import get_db_session
from services.authentication_service import AuthenticationService
from ui.theme import inject_custom_theme


def render_login_page() -> None:
    inject_custom_theme()
    if is_authenticated():
        return

    st.markdown(
        """
        <style>
          [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display:none !important; }
          .main .block-container { max-width:1120px; padding-top:.65rem; }
        </style>
        <div class="login-shell">
          <section class="login-story">
            <div class="login-kicker">APEX VEHICLE ASSURANCE</div>
            <h1 class="login-title">Evidence-led claims assessment.</h1>
            <p class="login-copy">
              A secure workspace for policyholders and claims teams to register vehicles,
              review model-assisted damage findings, and issue traceable assessment reports.
            </p>
            <div class="login-trust">Protected access · Audited decisions · Human-reviewed findings</div>
          </section>
        </div>
        <div class="login-mobile-brand">APEX ASSURANCE</div>
        """,
        unsafe_allow_html=True,
    )

    # Streamlit controls remain native and accessible; CSS positions them over
    # the form half of the branded shell on desktop.
    st.markdown(
        """
        <style>
        div[data-testid="stForm"] {
          width:min(390px, calc(100vw - 3rem));
          margin:-505px max(2rem, calc((100% - 1000px)/2)) 0 auto;
          padding:0; border:0; background:transparent;
          position:relative; z-index:2;
        }
        @media(max-width:760px) {
          div[data-testid="stForm"] { width:100%; margin:1rem auto 0; padding:1.3rem; background:white; border:1px solid var(--line); border-radius:14px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        st.markdown(
            """
            <div class="login-form-heading">
              <h2>Sign in</h2>
              <p>Use your assigned insurance portal account.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        identifier = st.text_input("Username or email", placeholder="Enter your username or email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button(
            "Sign in securely",
            type="primary",
            icon=":material/login:",
            use_container_width=True,
        )
        if submitted:
            if not identifier.strip() or not password:
                st.error("Enter both your username/email and password.")
            else:
                try:
                    with get_db_session() as session:
                        user = AuthenticationService(session).authenticate(identifier.strip(), password)
                        values = {
                            "user_id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "role_code": user.role.code if user.role else "",
                            "customer_id": user.customer_id,
                            "must_change_password": user.must_change_password,
                        }
                    if values["role_code"] == "customer" and not values["customer_id"]:
                        st.error("This customer account is not linked to a policyholder record.")
                        st.stop()
                    login_user(**values)
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

    st.stop()
