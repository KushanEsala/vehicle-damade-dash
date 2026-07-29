from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import BigInteger, DateTime, Integer, Numeric as SQLDecimal, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class CompanyInformation(Base):
    __tablename__ = "company_information"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String(200), default="Apex Vehicle Assurance Services", nullable=False)
    registration_number: Mapped[str] = mapped_column(String(100), default="PV-10029384", nullable=False)
    address_line_1: Mapped[str] = mapped_column(String(255), default="100 Commercial Drive", nullable=False)
    address_line_2: Mapped[str | None] = mapped_column(String(255), default="Level 4, Apex Tower", nullable=True)
    city: Mapped[str] = mapped_column(String(100), default="Colombo", nullable=False)
    phone: Mapped[str] = mapped_column(String(40), default="+94 11 234 5678", nullable=False)
    email: Mapped[str] = mapped_column(String(255), default="claims@apexinsurance.lk", nullable=False)
    website: Mapped[str | None] = mapped_column(String(255), default="https://apexinsurance.lk", nullable=True)
    logo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    currency_code: Mapped[str] = mapped_column(String(3), default="LKR", nullable=False)
    tax_label: Mapped[str] = mapped_column(String(30), default="VAT", nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(SQLDecimal(7, 4), default=Decimal("0.1500"), nullable=False)
    report_footer: Mapped[str | None] = mapped_column(
        Text,
        default="Official Vehicle Damage Assessment Report produced by Apex Insurance ERP. Advisory only.",
        nullable=True,
    )
    updated_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )
