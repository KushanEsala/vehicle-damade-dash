from __future__ import annotations

from datetime import datetime, timezone
import streamlit as st

from core.config import get_settings
from core.constants import RoleCode
from core.exceptions import AuthorizationError, AuthenticationError


def init_session_state() -> None:
    """Ensures standard session state variables exist."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "role_code" not in st.session_state:
        st.session_state.role_code = None
    if "customer_id" not in st.session_state:
        st.session_state.customer_id = None
    if "must_change_password" not in st.session_state:
        st.session_state.must_change_password = False
    if "auth_timestamp" not in st.session_state:
        st.session_state.auth_timestamp = None
    if "last_activity" not in st.session_state:
        st.session_state.last_activity = None


def check_session_timeout() -> bool:
    """Checks if the session has expired due to inactivity."""
    if not st.session_state.get("authenticated"):
        return False
    last_act = st.session_state.get("last_activity")
    if last_act is None:
        return False
    
    settings = get_settings()
    now = datetime.now(timezone.utc)
    elapsed_minutes = (now - last_act).total_seconds() / 60.0
    if elapsed_minutes > settings.SESSION_TIMEOUT_MINUTES:
        logout_user()
        return True
    
    st.session_state.last_activity = now
    return False


def login_user(
    user_id: int,
    username: str,
    email: str,
    role_code: str,
    customer_id: int | None = None,
    must_change_password: bool = False,
) -> None:
    """Sets session state on successful login."""
    now = datetime.now(timezone.utc)
    st.session_state.authenticated = True
    st.session_state.user_id = user_id
    st.session_state.username = username
    st.session_state.user_email = email
    st.session_state.role_code = role_code
    st.session_state.customer_id = customer_id
    st.session_state.must_change_password = must_change_password
    st.session_state.auth_timestamp = now
    st.session_state.last_activity = now


def logout_user() -> None:
    """Clears all authentication state."""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.user_email = None
    st.session_state.role_code = None
    st.session_state.customer_id = None
    st.session_state.must_change_password = False
    st.session_state.auth_timestamp = None
    st.session_state.last_activity = None


def get_current_user_id() -> int | None:
    return st.session_state.get("user_id")


def get_current_role() -> str | None:
    return st.session_state.get("role_code")


def get_current_customer_id() -> int | None:
    return st.session_state.get("customer_id")


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated"))
