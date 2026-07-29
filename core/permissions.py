from __future__ import annotations

from typing import Callable, Any
import streamlit as st

from core.constants import RoleCode
from core.exceptions import AuthorizationError
from core.session import get_current_role, get_current_customer_id, is_authenticated


def can_manage_users(role: str | None) -> bool:
    return role == RoleCode.ADMIN


def can_edit_company(role: str | None) -> bool:
    return role == RoleCode.ADMIN


def can_manage_plans(role: str | None) -> bool:
    return role == RoleCode.ADMIN


def can_create_customer(role: str | None) -> bool:
    return role in (RoleCode.ADMIN, RoleCode.OPERATOR)


def can_register_vehicle(role: str | None) -> bool:
    return role in (RoleCode.ADMIN, RoleCode.OPERATOR)


def can_run_analysis(role: str | None) -> bool:
    return role in (RoleCode.ADMIN, RoleCode.OPERATOR)


def can_override_vehicle_check(role: str | None) -> bool:
    return role in (RoleCode.ADMIN, RoleCode.OPERATOR)


def can_add_cost(role: str | None) -> bool:
    return role in (RoleCode.ADMIN, RoleCode.OPERATOR)


def can_finalize_analysis(role: str | None) -> bool:
    return role in (RoleCode.ADMIN, RoleCode.OPERATOR)


def can_revise_analysis(role: str | None) -> bool:
    return role == RoleCode.ADMIN


def can_view_audit_logs(role: str | None) -> bool:
    return role == RoleCode.ADMIN


def can_activate_model(role: str | None) -> bool:
    return role == RoleCode.ADMIN


def can_view_customer(role: str | None, target_customer_id: int, current_customer_id: int | None) -> bool:
    if role in (RoleCode.ADMIN, RoleCode.OPERATOR):
        return True
    if role == RoleCode.CUSTOMER:
        return current_customer_id == target_customer_id
    return False


def can_view_vehicle(role: str | None, vehicle_owner_id: int, current_customer_id: int | None) -> bool:
    if role in (RoleCode.ADMIN, RoleCode.OPERATOR):
        return True
    if role == RoleCode.CUSTOMER:
        return current_customer_id == vehicle_owner_id
    return False


def require_role(allowed_roles: list[str]) -> Callable:
    """Decorator to enforce role permissions on service methods or UI blocks."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            role = get_current_role()
            if not is_authenticated() or role not in allowed_roles:
                raise AuthorizationError(f"Access denied for role '{role}'. Required: {allowed_roles}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
