from __future__ import annotations

from decimal import Decimal
from services.costing_service import CostingService


def test_costing_service_totals():
    costs = [15000.00, 25000.50, 5000.25]
    subtotal, tax, total = CostingService.calculate_analysis_totals(
        accepted_costs=costs,
        tax_rate=Decimal("0.1500"),
        discount_amount=Decimal("1000.00"),
    )

    assert subtotal == Decimal("45000.75")
    assert tax == Decimal("6750.11")
    assert total == Decimal("50750.86")


def test_currency_formatter():
    formatted = CostingService.format_currency(1234567.891, currency_code="LKR")
    assert formatted == "LKR 1,234,567.89"
