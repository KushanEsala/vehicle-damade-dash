from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("customers.id"), nullable=False, index=True)
    vehicle_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    registration_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    chassis_number: Mapped[str | None] = mapped_column(String(80), unique=True, nullable=True, index=True)
    engine_number: Mapped[str | None] = mapped_column(String(80), nullable=True)
    make: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    manufactured_year: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    colour: Mapped[str] = mapped_column(String(60), nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(40), default="Car", nullable=False)
    fuel_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    odometer_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    primary_image_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    created_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )

    customer: Mapped[Customer] = relationship("Customer", back_populates="vehicles")
    images: Mapped[list[VehicleImage]] = relationship("VehicleImage", back_populates="vehicle")
    policies: Mapped[list[VehiclePolicy]] = relationship("VehiclePolicy", back_populates="vehicle")
    analyses: Mapped[list[Analysis]] = relationship("Analysis", back_populates="vehicle")


class VehicleImage(Base):
    __tablename__ = "vehicle_images"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("vehicles.id"), nullable=False, index=True)
    analysis_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("analyses.id"), nullable=True)
    image_category: Mapped[str] = mapped_column(String(40), default="profile", nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    width_px: Mapped[int] = mapped_column(Integer, nullable=False)
    height_px: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    uploaded_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    vehicle: Mapped[Vehicle] = relationship("Vehicle", back_populates="images")
