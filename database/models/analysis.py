from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from sqlalchemy import BigInteger, Boolean, DateTime, Numeric as SQLDecimal, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    model_key: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    model_type: Mapped[str] = mapped_column(String(40), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    classes_json: Mapped[Any] = mapped_column(JSON, nullable=False)
    framework: Mapped[str] = mapped_column(String(80), nullable=False)
    framework_version: Mapped[str] = mapped_column(String(40), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    analysis_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    vehicle_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("vehicles.id"), nullable=False, index=True)
    operator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    damage_model_version_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("model_versions.id"), nullable=False)
    vehicle_model_version_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("model_versions.id"), nullable=False)
    source_image_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("vehicle_images.id"), nullable=False)
    annotated_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="analyzed", nullable=False, index=True)
    damage_confidence: Mapped[Decimal] = mapped_column(SQLDecimal(5, 4), nullable=False)
    vehicle_confidence: Mapped[Decimal] = mapped_column(SQLDecimal(5, 4), nullable=False)
    require_vehicle_confirmation: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    vehicle_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    confirmation_overridden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    override_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_prediction_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    accepted_damage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejected_damage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    subtotal_cost: Mapped[Decimal] = mapped_column(SQLDecimal(15, 2), default=Decimal("0.00"), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(SQLDecimal(15, 2), default=Decimal("0.00"), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(SQLDecimal(15, 2), default=Decimal("0.00"), nullable=False)
    total_estimated_cost: Mapped[Decimal] = mapped_column(SQLDecimal(15, 2), default=Decimal("0.00"), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), default="LKR", nullable=False)
    operator_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finalized_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )

    vehicle: Mapped[Vehicle] = relationship("Vehicle", back_populates="analyses")
    vehicle_detections: Mapped[list[AnalysisVehicleDetection]] = relationship(
        "AnalysisVehicleDetection", back_populates="analysis", cascade="all, delete-orphan"
    )
    damages: Mapped[list[AnalysisDamage]] = relationship(
        "AnalysisDamage", back_populates="analysis", cascade="all, delete-orphan"
    )
    reports: Mapped[list[Report]] = relationship("Report", back_populates="analysis")


class AnalysisVehicleDetection(Base):
    __tablename__ = "analysis_vehicle_detections"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    analysis_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("analyses.id"), nullable=False, index=True)
    vehicle_class: Mapped[str] = mapped_column(String(60), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(SQLDecimal(7, 6), nullable=False)
    box_json: Mapped[Any] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    analysis: Mapped[Analysis] = relationship("Analysis", back_populates="vehicle_detections")


class AnalysisDamage(Base):
    __tablename__ = "analysis_damages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    analysis_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("analyses.id"), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(20), default="model", nullable=False)
    original_damage_class: Mapped[str | None] = mapped_column(String(80), nullable=True)
    final_damage_class: Mapped[str] = mapped_column(String(80), nullable=False)
    vehicle_part: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence: Mapped[Decimal | None] = mapped_column(SQLDecimal(7, 6), nullable=True)
    box_json: Mapped[Any] = mapped_column(JSON, nullable=False)
    polygon_json: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    model_polygon_json: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    mask_refined: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    overlap_ratio: Mapped[Decimal | None] = mapped_column(SQLDecimal(7, 6), nullable=True)
    passed_vehicle_gate: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    review_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="moderate", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    internal_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_cost: Mapped[Decimal] = mapped_column(SQLDecimal(15, 2), default=Decimal("0.00"), nullable=False)
    reviewed_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )

    analysis: Mapped[Analysis] = relationship("Analysis", back_populates="damages")


class AnalysisRevision(Base):
    __tablename__ = "analysis_revisions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    original_analysis_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("analyses.id"), nullable=False, index=True)
    replacement_analysis_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("analyses.id"), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
