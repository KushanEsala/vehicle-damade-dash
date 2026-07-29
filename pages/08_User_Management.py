from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import streamlit as st
from sqlalchemy.orm import joinedload

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from database.connection import get_db_session
from services.user_service import UserService
from services.authentication_service import AuthenticationService
from ui.layout import render_page_header

render_page_header("User Account Management", "Manage system administrators, operators, and customer accounts", "ADMINISTRATION", allowed_roles=["admin"])

admin_id = st.session_state.get("user_id") or 1

tab_list, tab_create = st.tabs(["System User Accounts", "Create Staff User"])

with tab_list:
    with get_db_session() as session:
        from database.models.user import User as UserModel
        u_service = UserService(session)
        users_orm = session.query(UserModel).options(joinedload(UserModel.role)).all()

        users_dicts = []
        for u in users_orm:
            users_dicts.append({
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role_name": u.role.name if u.role else "N/A",
                "is_active": u.is_active,
                "must_change_password": u.must_change_password,
                "last_login_at": u.last_login_at
            })

    table_data = [
        {
            "ID": u["id"],
            "Username": u["username"],
            "Email": u["email"],
            "Role": u["role_name"],
            "Active": "Active" if u["is_active"] else "Inactive",
            "Force Pass Change": "Yes" if u["must_change_password"] else "No",
            "Last Login": u["last_login_at"].strftime("%Y-%m-%d %H:%M") if u["last_login_at"] else "Never",
        }
        for u in users_dicts
    ]
    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### Administrative Password Reset")
    target_user_dict = st.selectbox("Select User Account for Password Reset", users_dicts, format_func=lambda u: f"{u['username']} ({u['email']})")
    if st.button("Generate Temporary Password"):
        try:
            with get_db_session() as session:
                auth_service = AuthenticationService(session)
                temp_p = auth_service.reset_password(admin_id, target_user_dict["id"])
            st.success(f"Temporary password generated for {target_user_dict['username']}:")
            st.code(temp_p)
            st.info("The user will be required to change this password on their next login.")
        except Exception as e:
            st.error(str(e))

with tab_create:
    with st.form("create_user_form"):
        username = st.text_input("Username", placeholder="operator_john")
        email = st.text_input("Email Address", placeholder="john@apexinsurance.lk")
        role_code = st.selectbox("Role", ["operator", "admin"])
        submit = st.form_submit_button("Create User Account", type="primary")

        if submit:
            try:
                with get_db_session() as session:
                    u_service = UserService(session)
                    user, temp_p = u_service.create_staff_user(username, email, role_code, admin_id)
                    username_saved = user.username
                st.success(f"User account '{username_saved}' created successfully!")
                st.code(f"Temporary Password: {temp_p}")
            except Exception as e:
                st.error(str(e))
