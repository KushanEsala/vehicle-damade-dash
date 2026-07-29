from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import BigInteger, Boolean, Date, DateTime, Integer, Numeric as SQLDecimal, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class InsurancePlan(Base):
    __tablename__ = "insurance_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    coverage_limit: Mapped[Decimal | None] = mapped_column(SQLDecimal(15, 2), nullable=True)
    deductible_amount: Mapped[Decimal] = mapped_column(SQLDecimal(15, 2), default=Decimal("0.00"), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), default="LKR", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )

    policies: Mapped[list[VehiclePolicy]] = relationship("VehiclePolicy", back_populates="plan")


class VehiclePolicy(Base):
    __tablename__ = "vehicle_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("vehicles.id"), nullable=False, index=True)
    plan_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("insurance_plans.id"), nullable=False, index=True)
    policy_number: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    premium_amount: Mapped[Decimal | None] = mapped_column(SQLDecimal(15, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )

    vehicle: Mapped[Vehicle] = relationship("Vehicle", back_populates="policies")
    plan: Mapped[InsurancePlan] = relationship("InsurancePlan", back_populates="policies")
