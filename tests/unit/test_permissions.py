from __future__ import annotations

from core.permissions import (
    can_add_cost,
    can_create_customer,
    can_edit_company,
    can_manage_plans,
    can_view_customer,
    can_view_vehicle,
)


def test_customer_is_limited_to_own_records() -> None:
    assert can_view_customer("customer", 10, 10)
    assert not can_view_customer("customer", 11, 10)
    assert can_view_vehicle("customer", 10, 10)
    assert not can_view_vehicle("customer", 11, 10)


def test_operator_and_admin_mutation_boundaries() -> None:
    assert can_create_customer("operator")
    assert can_add_cost("operator")
    assert not can_manage_plans("operator")
    assert not can_edit_company("operator")
    assert can_manage_plans("admin")
    assert can_edit_company("admin")
