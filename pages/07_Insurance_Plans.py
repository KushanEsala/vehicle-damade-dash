from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from database.connection import get_db_session
from services.plan_service import PlanService
from ui.layout import render_page_header

render_page_header("Insurance Policy Plans", "Configure insurance coverage plans, deductible amounts, and policy limits", "ADMINISTRATION", allowed_roles=["admin", "operator"])

admin_id = st.session_state.get("user_id") or 1

tab_list, tab_create = st.tabs(["Active Insurance Plans", "Create New Plan"])

with tab_list:
    with get_db_session() as session:
        p_service = PlanService(session)
        plans = p_service.list_active_plans()

        if not plans:
            st.info("No active plans registered.")
        else:
            table_data = [
                {
                    "Plan Code": p.plan_code,
                    "Name": p.name,
                    "Deductible": f"{p.currency_code} {p.deductible_amount:,.2f}",
                    "Coverage Limit": f"{p.currency_code} {p.coverage_limit:,.2f}" if p.coverage_limit else "Unlimited",
                    "Active": "Yes" if p.is_active else "No",
                }
                for p in plans
            ]
            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

with tab_create:
    with st.form("create_plan_form"):
        code = st.text_input("Plan Code *", placeholder="PLN-SILVER-AUTO")
        name = st.text_input("Plan Name *", placeholder="Silver Third Party & Collision Shield")
        desc = st.text_area("Description *", placeholder="Comprehensive coverage with LKR 10,000 deductible.")
        deductible = st.number_input("Deductible Amount (LKR) *", min_value=0.0, value=10000.0, step=1000.0)
        limit = st.number_input("Coverage Limit (LKR)", min_value=0.0, value=2500000.0, step=100000.0)

        submit = st.form_submit_button("Create Insurance Plan", type="primary")

        if submit:
            try:
                with get_db_session() as session:
                    p_service = PlanService(session)
                    plan = p_service.create_plan(
                        plan_code=code,
                        name=name,
                        description=desc,
                        deductible_amount=deductible,
                        admin_user_id=admin_id,
                        coverage_limit=limit,
                    )
                    p_name = plan.name
                st.success(f"Insurance plan '{p_name}' created successfully!")
            except Exception as e:
                st.error(str(e))
