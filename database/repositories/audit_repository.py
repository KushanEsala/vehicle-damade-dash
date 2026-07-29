from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session
from database.models.audit import AuditLog


class AuditRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def log_event(
        self,
        action: str,
        entity_type: str,
        user_id: int | None = None,
        entity_id: int | None = None,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        success: bool = True,
        failure_reason: str | None = None,
    ) -> AuditLog:
        # Security rule: remove passwords/hashes from audit dicts
        for d in (old_values, new_values):
            if d and isinstance(d, dict):
                for k in list(d.keys()):
                    if "password" in k.lower() or "secret" in k.lower():
                        d[k] = "[REDACTED]"

        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values_json=old_values,
            new_values_json=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
        )
        self.session.add(log)
        self.session.flush()
        return log

    def list_logs(self, limit: int = 100) -> list[AuditLog]:
        return (
            self.session.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
