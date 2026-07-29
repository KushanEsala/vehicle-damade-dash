from __future__ import annotations

import hashlib
import io
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from sqlalchemy.orm import Session

from core.exceptions import ResourceNotFoundError, ValidationError
from database.repositories.analysis_repository import AnalysisRepository
from database.repositories.report_repository import ReportRepository
from database.repositories.audit_repository import AuditRepository
from database.models.company import CompanyInformation
from database.models.report import Report
from reports.pdf_builder import PDFReportBuilder
from services.storage_service import StorageService


class ReportService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.analysis_repo = AnalysisRepository(session)
        self.report_repo = ReportRepository(session)
        self.audit_repo = AuditRepository(session)
        self.storage = StorageService()

    def generate_report_number(self, analysis_num: str, revision: int = 1) -> str:
        return f"RPT-{analysis_num}-R{revision:02d}"

    def list_all(self) -> list[Report]:
        return self.report_repo.list_all()

    def list_for_customer(self, customer_id: int) -> list[Report]:
        """Return only reports owned by a customer through the report's vehicle."""
        from database.models.analysis import Analysis
        from database.models.vehicle import Vehicle

        return (
            self.session.query(Report)
            .join(Report.analysis)
            .join(Analysis.vehicle)
            .filter(Vehicle.customer_id == customer_id)
            .order_by(Report.generated_at.desc())
            .all()
        )

    def get_authorized_report(
        self,
        report_id: int,
        *,
        role_code: str,
        customer_id: int | None = None,
    ) -> Report:
        report = self.report_repo.get_by_id(report_id)
        if not report:
            raise ResourceNotFoundError(f"Report #{report_id} not found.")
        if role_code == "customer":
            owner_id = report.analysis.vehicle.customer_id
            if customer_id is None or owner_id != customer_id:
                raise ResourceNotFoundError(f"Report #{report_id} not found.")
        elif role_code not in {"admin", "operator"}:
            raise ResourceNotFoundError(f"Report #{report_id} not found.")
        return report

    def build_snapshot(self, analysis_id: int) -> dict[str, Any]:
        analysis = self.analysis_repo.get_by_id(analysis_id)
        if not analysis:
            raise ResourceNotFoundError(f"Analysis #{analysis_id} not found.")

        vehicle = analysis.vehicle
        customer = vehicle.customer
        company = self.session.query(CompanyInformation).first()

        damages = [
            {
                "id": d.id,
                "final_damage_class": d.final_damage_class,
                "vehicle_part": d.vehicle_part or "General Panel",
                "severity": d.severity,
                "confidence": float(d.confidence) if d.confidence is not None else None,
                "description": d.description or "",
                "estimated_cost": float(d.estimated_cost),
            }
            for d in analysis.damages
            if d.review_status in ("accepted", "corrected") and d.passed_vehicle_gate
        ]

        return {
            "analysis_id": analysis.id,
            "analysis_number": analysis.analysis_number,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "company": {
                "company_name": company.company_name if company else "Apex Assurance",
                "address_line_1": company.address_line_1 if company else "",
                "city": company.city if company else "",
                "phone": company.phone if company else "",
                "email": company.email if company else "",
                "tax_label": company.tax_label if company else "VAT",
                "report_footer": company.report_footer if company else "",
            },
            "customer": {
                "full_name": customer.full_name,
                "customer_code": customer.customer_code,
                "phone_primary": customer.phone_primary,
                "email": customer.email,
                "nic_or_passport": customer.nic_or_passport,
            },
            "vehicle": {
                "registration_number": vehicle.registration_number,
                "make": vehicle.make,
                "model": vehicle.model,
                "manufactured_year": vehicle.manufactured_year,
                "colour": vehicle.colour,
                "vehicle_type": vehicle.vehicle_type,
            },
            "damages": damages,
            "currency_code": analysis.currency_code,
            "totals": {
                "subtotal": float(analysis.subtotal_cost),
                "tax": float(analysis.tax_amount),
                "discount": float(analysis.discount_amount),
                "total": float(analysis.total_estimated_cost),
            },
            "operator_notes": analysis.operator_notes,
            "override_used": analysis.confirmation_overridden,
            "override_reason": analysis.override_reason if analysis.confirmation_overridden else None,
        }

    def generate_pdf_report(self, analysis_id: int, user_id: int) -> Report:
        analysis = self.analysis_repo.get_by_id(analysis_id)
        if not analysis:
            raise ResourceNotFoundError(f"Analysis #{analysis_id} not found.")

        existing = self.report_repo.get_by_analysis_id(analysis_id)
        revision = (existing.revision_number + 1) if existing else 1
        if existing:
            existing.is_current = False
            self.report_repo.save(existing)

        report_num = self.generate_report_number(analysis.analysis_number, revision)
        snapshot = self.build_snapshot(analysis_id)
        snapshot["report_number"] = report_num
        snapshot["layout_version"] = 2

        # Render PDF to memory
        pdf_bytes = self._render_pdf(snapshot, analysis)
        sha256 = hashlib.sha256(pdf_bytes).hexdigest()

        # Save to disk
        now = datetime.now(timezone.utc)
        rel_dir = Path("reports") / str(now.year) / f"{now.month:02d}"
        abs_dir = self.storage.root / rel_dir
        abs_dir.mkdir(parents=True, exist_ok=True)

        rel_path = rel_dir / f"{report_num}.pdf"
        abs_path = self.storage.root / rel_path
        abs_path.write_bytes(pdf_bytes)

        report = Report(
            report_number=report_num,
            analysis_id=analysis_id,
            revision_number=revision,
            pdf_path=str(rel_path).replace("\\", "/"),
            sha256=sha256,
            snapshot_json=snapshot,
            generated_by=user_id,
            generated_at=now,
            is_current=True,
        )
        self.report_repo.save(report)

        self.audit_repo.log_event(
            action="generate_report",
            entity_type="report",
            user_id=user_id,
            entity_id=report.id,
            new_values={"report_number": report_num, "sha256": sha256},
        )

        return report

    def ensure_current_pdf_layout(self, report: Report) -> Report:
        """Upgrade older generated PDFs to the current visual report layout."""
        snapshot = dict(report.snapshot_json or {})
        if int(snapshot.get("layout_version", 1)) >= 2:
            return report
        snapshot["layout_version"] = 2
        snapshot["report_number"] = report.report_number
        pdf_bytes = self._render_pdf(snapshot, report.analysis)
        path = self.storage.get_absolute_path(report.pdf_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pdf_bytes)
        report.sha256 = hashlib.sha256(pdf_bytes).hexdigest()
        report.snapshot_json = snapshot
        self.report_repo.save(report)
        return report

    def _render_pdf(self, snapshot: dict[str, Any], analysis: Any) -> bytes:
        render_snapshot = dict(snapshot)
        if analysis.annotated_image_path:
            image_path = self.storage.get_absolute_path(analysis.annotated_image_path)
            if image_path.is_file():
                render_snapshot["_annotated_image_path"] = str(image_path)
        pdf_stream = io.BytesIO()
        PDFReportBuilder.build_report_pdf(render_snapshot, pdf_stream)
        return pdf_stream.getvalue()
