from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    report_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    analysis_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("analyses.id"), nullable=False, index=True)
    revision_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    pdf_path: Mapped[str] = mapped_column(String(500), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    snapshot_json: Mapped[Any] = mapped_column(JSON, nullable=False)
    generated_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    analysis: Mapped[Analysis] = relationship("Analysis", back_populates="reports")
