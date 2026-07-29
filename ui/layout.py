from __future__ import annotations

import streamlit as st
from ui.theme import inject_custom_theme
from core.session import check_session_timeout, is_authenticated, logout_user, get_current_role


def apply_role_sidebar_filtering() -> None:
    """Compatibility no-op; navigation is now constructed server-side by role."""
    return


def render_sidebar_identity() -> None:
    if not is_authenticated():
        return
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-lockup">
              <div class="brand-mark"><span class="material-symbols-rounded">shield</span></div>
              <div>
                <div class="brand-name">APEX ASSURANCE</div>
                <div class="brand-subtitle">Claims intelligence</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="appearance-label">
              <span class="material-symbols-rounded">contrast</span>
              <span>Appearance</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.toggle(
            "Dark mode",
            key="dark_mode",
            help="Switch between dark and light application themes.",
        )


def render_sidebar_footer() -> None:
    """Renders user account info and Logout button at the bottom of sidebar."""
    if not is_authenticated():
        return

    username = st.session_state.get("username", "User")
    role_code = st.session_state.get("role_code", "USER").upper()

    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-account">
              <div class="sidebar-account-icon"><span class="material-symbols-rounded">account_circle</span></div>
              <div>
              <div class="sidebar-account-name">
                {username}
              </div>
              <div class="sidebar-account-role">
                {role_code}
              </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Sign out", key="sidebar_logout_btn", icon=":material/logout:", use_container_width=True):
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

    init_session_state()
    inject_custom_theme()
    ensure_database_ready()

    if require_auth and not is_authenticated():
        render_login_page()

    if require_auth and (not is_authenticated() or check_session_timeout()):
        render_login_page()
        st.stop()

    current_role = get_current_role()
    if allowed_roles and current_role not in allowed_roles:
        st.error("You do not have permission to access this page.")
        st.stop()

    if current_role == "customer" and not st.session_state.get("customer_id"):
        st.error("Your account is not linked to a policyholder record.")
        st.stop()


def render_page_header(
    title: str,
    subtitle: str | None = None,
    category: str = "VEHICLE INSURANCE ERP",
    require_auth: bool = True,
    allowed_roles: list[str] | None = None,
) -> None:
    """Renders the standardized Apex insurance workspace header."""
    ensure_page_initialized(title, require_auth=require_auth, allowed_roles=allowed_roles)
    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
          <div style="color: #0F766E; font-size: 0.72rem; font-weight: 800; letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 0.35rem;">
            {category}
          </div>
          <h1 style="font-size: 2.15rem; font-weight: 800; color: #102A43; margin: 0; line-height: 1.15;">
            {title}
          </h1>
          {f'<p style="color: #637381; font-size: .96rem; margin-top: .4rem; margin-bottom: 0;">{subtitle}</p>' if subtitle else ''}
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
