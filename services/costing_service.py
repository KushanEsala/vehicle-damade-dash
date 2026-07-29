from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


class CostingService:
    """Exact decimal arithmetic for damage analysis cost calculations."""

    @staticmethod
    def format_currency(amount: Decimal | float | int, currency_code: str = "LKR") -> str:
        dec = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{currency_code} {dec:,.2f}"

    @staticmethod
    def calculate_analysis_totals(
        accepted_costs: list[Decimal | float | int],
        tax_rate: Decimal | float = Decimal("0.1500"),
        discount_amount: Decimal | float | int = Decimal("0.00"),
    ) -> tuple[Decimal, Decimal, Decimal]:
        """
        Returns (subtotal, tax_amount, total_estimated_cost).
        """
        subtotal = sum((Decimal(str(c)) for c in accepted_costs), Decimal("0.00")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        tax = (subtotal * Decimal(str(tax_rate))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        gross = subtotal + tax
        discount = Decimal(str(discount_amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total = max(Decimal("0.00"), gross - discount)
        return subtotal, tax, total
