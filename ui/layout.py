from __future__ import annotations

import streamlit as st
from ui.theme import inject_custom_theme
from core.session import is_authenticated, logout_user, get_current_role


def apply_role_sidebar_filtering() -> None:
    """Injects CSS rules to hide unauthorized page links from the Streamlit sidebar based on user role."""
    if not is_authenticated():
        return

    role = (get_current_role() or "admin").lower()

    hidden_selectors = []
    if role == "operator":
        # Operator cannot access admin management / system diagnostic pages
        hidden_selectors = [
            'a[href*="User_Management"]',
            'a[href*="Company_Settings"]',
            'a[href*="Audit_Logs"]',
            'a[href*="Model_Tester"]',
        ]
    elif role == "customer":
        # Customer can only access Overview, Damage Reports, and My Profile
        hidden_selectors = [
            'a[href*="New_Analysis"]',
            'a[href*="Analysis_Review"]',
            'a[href*="Customers"]',
            'a[href*="Vehicles"]',
            'a[href*="Insurance_Plans"]',
            'a[href*="User_Management"]',
            'a[href*="Company_Settings"]',
            'a[href*="Audit_Logs"]',
            'a[href*="Model_Tester"]',
        ]

    if hidden_selectors:
        css_rules = ", ".join([f'[data-testid="stSidebarNav"] {sel}' for sel in hidden_selectors])
        st.markdown(
            f"""
            <style>
              {css_rules} {{
                display: none !important;
              }}
            </style>
            """,
            unsafe_allow_html=True,
        )


def render_sidebar_footer() -> None:
    """Renders user account info and Logout button at the bottom of sidebar."""
    if not is_authenticated():
        return

    username = st.session_state.get("username", "User")
    role_code = st.session_state.get("role_code", "USER").upper()

    with st.sidebar:
        st.markdown("---")
        st.markdown(
            f"""
            <div style="padding: 0.5rem 0; margin-bottom: 0.5rem;">
              <div style="font-weight: 700; font-size: 0.95rem; color: #E9F0F5;">
                {username}
              </div>
              <div style="font-size: 0.78rem; color: #50DBB7; font-weight: 700; letter-spacing: 0.05em;">
                {role_code} ACCOUNT
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Logout", key="sidebar_logout_btn", use_container_width=True):
            logout_user()
            st.rerun()


def ensure_page_initialized(
    title: str = "Vehicle Damage Insurance ERP",
    require_auth: bool = True,
    allowed_roles: list[str] | None = None,
) -> None:
    """Ensures page configuration, CSS theme, DB connection, and session state are ready."""
    try:
        st.set_page_config(page_title=title, layout="wide", initial_sidebar_state="expanded")
    except Exception:
        pass

    from database.connection import ensure_database_ready
    from core.session import init_session_state
    from ui.login_view import render_login_page

    ensure_database_ready()
    inject_custom_theme()
    init_session_state()

    if require_auth and not is_authenticated():
        render_login_page()

    current_role = (get_current_role() or "admin").lower()
    if allowed_roles and current_role not in allowed_roles:
        st.error(f"Access Denied: Your account role '{current_role.upper()}' does not have permission to access this section.")
        st.info("Use the sidebar menu to navigate to your permitted pages.")
        render_sidebar_footer()
        st.stop()

    apply_role_sidebar_filtering()
    render_sidebar_footer()


def render_page_header(
    title: str,
    subtitle: str | None = None,
    category: str = "VEHICLE INSURANCE ERP",
    require_auth: bool = True,
    allowed_roles: list[str] | None = None,
) -> None:
    """Renders standardized page header with dark automotive aesthetic."""
    ensure_page_initialized(title, require_auth=require_auth, allowed_roles=allowed_roles)
    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
          <div style="color: #50DBB7; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 0.25rem;">
            {category}
          </div>
          <h1 style="font-size: 2.2rem; font-weight: 700; color: #E9F0F5; margin: 0; line-height: 1.15;">
            {title}
          </h1>
          {f'<p style="color: #91A1AE; font-size: 1rem; margin-top: 0.35rem; margin-bottom: 0;">{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_evidence_rail(current_step: int = 1) -> None:
    """
    Renders Section 11.4 Inspection Evidence Rail:
    Step 1: Vehicle record -> Step 2: Source photo -> Step 3: Model findings -> Step 4: Operator decisions -> Step 5: Cost -> Step 6: Report
    """
    steps = [
        "1. Vehicle",
        "2. Source Photo",
        "3. Model Findings",
        "4. Review & Override",
        "5. Costing",
        "6. Final Report",
    ]
    html_parts = ['<div class="evidence-rail">']
    for idx, step_name in enumerate(steps, start=1):
        if idx == current_step:
            css_class = "rail-step active"
        elif idx < current_step:
            css_class = "rail-step completed"
        else:
            css_class = "rail-step"

        html_parts.append(f'<div class="{css_class}">{step_name}</div>')
        if idx < len(steps):
            html_parts.append('<div class="rail-arrow">→</div>')
    html_parts.append('</div>')
    st.markdown("".join(html_parts), unsafe_allow_html=True)


def render_status_badge(text: str, badge_type: str = "neutral") -> str:
    """Returns HTML for a status badge (verified, caution, danger, analysis, neutral)."""
    return f'<span class="badge badge-{badge_type}">{text}</span>'
