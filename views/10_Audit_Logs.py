from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from database.connection import get_db_session
from database.repositories.audit_repository import AuditRepository
from ui.layout import render_page_header

render_page_header("Append-Only Security Audit Trail", "System action logs, authentication events, override reasons, and security modifications", "SECURITY & AUDIT", allowed_roles=["admin"])

with get_db_session() as session:
    audit_repo = AuditRepository(session)
    logs = audit_repo.list_logs(limit=150)

    if not logs:
        log_data = []
    else:
        log_data = [
            {
                "Timestamp": entry.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "Action": entry.action.upper(),
                "Entity": entry.entity_type,
                "Entity ID": entry.entity_id or "—",
                "User ID": entry.user_id or "Anonymous",
                "Success": "YES" if entry.success else "NO",
                "Failure Reason": entry.failure_reason or "—",
                "IP Address": entry.ip_address or "Local",
            }
            for entry in logs
        ]

if not log_data:
    st.info("No audit logs recorded yet.")
else:
    st.dataframe(pd.DataFrame(log_data), use_container_width=True, hide_index=True)
