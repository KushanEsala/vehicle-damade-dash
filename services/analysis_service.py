from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from core.constants import AnalysisStatus, ReviewStatus, SeverityLevel
from core.exceptions import ValidationError, ResourceNotFoundError, AuthorizationError
from database.repositories.analysis_repository import AnalysisRepository
from database.repositories.vehicle_repository import VehicleRepository
from database.repositories.audit_repository import AuditRepository
from database.models.analysis import Analysis, AnalysisVehicleDetection, AnalysisDamage, ModelVersion
from ml.pipeline import get_pipeline
from ml.types import InferenceRequest
from services.costing_service import CostingService
from services.storage_service import StorageService


class AnalysisService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.analysis_repo = AnalysisRepository(session)
        self.vehicle_repo = VehicleRepository(session)
        self.audit_repo = AuditRepository(session)
        self.pipeline = get_pipeline()
        self.storage = StorageService()

    def generate_analysis_number(self) -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        count = len(self.analysis_repo.list_all()) + 1
        return f"VDA-{date_str}-{count:06d}"

    def run_new_analysis(
        self,
        vehicle_id: int,
        source_image_id: int,
        operator_user_id: int,
        image_bytes: bytes,
        damage_confidence: float = 0.30,
        vehicle_confidence: float = 0.25,
        require_vehicle_confirmation: bool = True,
    ) -> Analysis:
        from io import BytesIO
        from PIL import Image
        import numpy as np

        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise ResourceNotFoundError(f"Vehicle #{vehicle_id} not found.")

        # Decode image array
        pil_img = Image.open(BytesIO(image_bytes)).convert("RGB")
        image_rgb = np.asarray(pil_img)

        # Run inference pipeline
        request = InferenceRequest(
            image=image_rgb,
            damage_confidence=damage_confidence,
            vehicle_confidence=vehicle_confidence,
            require_vehicle=require_vehicle_confirmation,
        )
        result = self.pipeline.run(request)

        # Register active model versions
        damage_meta = self.pipeline.registry.get_damage_model_metadata()
        vehicle_meta = self.pipeline.registry.get_vehicle_model_metadata()

        d_version = self.analysis_repo.get_or_create_model_version(
            model_key=damage_meta.model_key,
            display_name=damage_meta.display_name,
            model_type="damage_segmenter",
            file_path=damage_meta.file_path,
            sha256=damage_meta.sha256,
            classes=damage_meta.classes,
            framework=damage_meta.framework,
            framework_version=damage_meta.framework_version,
        )
        v_version = self.analysis_repo.get_or_create_model_version(
            model_key=vehicle_meta.model_key,
            display_name=vehicle_meta.display_name,
            model_type="vehicle_detector",
            file_path=vehicle_meta.file_path,
            sha256=vehicle_meta.sha256,
            classes=vehicle_meta.classes,
            framework=vehicle_meta.framework,
            framework_version=vehicle_meta.framework_version,
        )

        analysis_num = self.generate_analysis_number()
        annotated_rel_path = self.storage.save_annotated_image(analysis_num, result.annotated_image)

        analysis = Analysis(
            analysis_number=analysis_num,
            vehicle_id=vehicle_id,
            operator_id=operator_user_id,
            damage_model_version_id=d_version.id,
            vehicle_model_version_id=v_version.id,
            source_image_id=source_image_id,
            annotated_image_path=annotated_rel_path,
            status=AnalysisStatus.ANALYZED.value,
            damage_confidence=Decimal(str(damage_confidence)),
            vehicle_confidence=Decimal(str(vehicle_confidence)),
            require_vehicle_confirmation=require_vehicle_confirmation,
            vehicle_confirmed=result.vehicle_confirmed,
            confirmation_overridden=False,
            raw_prediction_count=len(result.accepted_damages) + len(result.rejected_damages),
            accepted_damage_count=len(result.accepted_damages),
            rejected_damage_count=len(result.rejected_damages),
            analyzed_at=datetime.now(timezone.utc),
        )
        self.analysis_repo.save_analysis(analysis)

        # Store vehicle detections
        for v in result.vehicles:
            vd = AnalysisVehicleDetection(
                analysis_id=analysis.id,
                vehicle_class=v.vehicle_class,
                confidence=Decimal(str(round(v.confidence, 4))),
                box_json=v.box.tolist(),
            )
            self.session.add(vd)

        # Store accepted damages
        for d in result.accepted_damages:
            ad = AnalysisDamage(
                analysis_id=analysis.id,
                source="model",
                original_damage_class=d.damage_class,
                final_damage_class=d.damage_class,
                confidence=Decimal(str(round(d.confidence, 4))),
                box_json=d.box.tolist(),
                polygon_json=d.polygon.tolist() if d.polygon is not None else None,
                overlap_ratio=Decimal(str(round(d.overlap_ratio, 4))),
                passed_vehicle_gate=True,
                review_status=ReviewStatus.ACCEPTED.value,
                severity=SeverityLevel.MODERATE.value,
                estimated_cost=Decimal("0.00"),
            )
            self.session.add(ad)

        # Store rejected damages
        for d in result.rejected_damages:
            rd = AnalysisDamage(
                analysis_id=analysis.id,
                source="model",
                original_damage_class=d.damage_class,
                final_damage_class=d.damage_class,
                confidence=Decimal(str(round(d.confidence, 4))),
                box_json=d.box.tolist(),
                polygon_json=d.polygon.tolist() if d.polygon is not None else None,
                overlap_ratio=Decimal(str(round(d.overlap_ratio, 4))),
                passed_vehicle_gate=False,
                review_status=ReviewStatus.REJECTED.value,
                severity=SeverityLevel.MINOR.value,
                estimated_cost=Decimal("0.00"),
            )
            self.session.add(rd)

        self.session.flush()

        self.audit_repo.log_event(
            action="run_analysis",
            entity_type="analysis",
            user_id=operator_user_id,
            entity_id=analysis.id,
            new_values={"analysis_number": analysis_num, "accepted_damages": len(result.accepted_damages)},
        )

        return analysis

    def override_vehicle_confirmation(self, analysis_id: int, operator_user_id: int, reason: str) -> Analysis:
        analysis = self.analysis_repo.get_by_id(analysis_id)
        if not analysis:
            raise ResourceNotFoundError(f"Analysis #{analysis_id} not found.")

        if not reason or len(reason.strip()) < 5:
            raise ValidationError("Override reason must be at least 5 characters long.")

        analysis.confirmation_overridden = True
        analysis.override_reason = reason.strip()

        # Mark rejected damages as passed gate upon override
        for d in analysis.damages:
            if not d.passed_vehicle_gate:
                d.passed_vehicle_gate = True
                d.review_status = ReviewStatus.ACCEPTED.value

        self.analysis_repo.save_analysis(analysis)

        self.audit_repo.log_event(
            action="override_vehicle_confirmation",
            entity_type="analysis",
            user_id=operator_user_id,
            entity_id=analysis.id,
            new_values={"reason": reason},
        )

        return analysis

    def update_damage_item(
        self,
        damage_id: int,
        operator_user_id: int,
        final_class: str,
        severity: str,
        estimated_cost: Decimal | float | int,
        review_status: str = "accepted",
        vehicle_part: str | None = None,
        description: str | None = None,
        internal_note: str | None = None,
    ) -> AnalysisDamage:
        d = self.session.query(AnalysisDamage).filter(AnalysisDamage.id == damage_id).first()
        if not d:
            raise ResourceNotFoundError(f"Damage item #{damage_id} not found.")

        d.final_damage_class = final_class
        d.severity = severity
        d.estimated_cost = Decimal(str(estimated_cost))
        d.review_status = review_status
        d.vehicle_part = vehicle_part
        d.description = description
        d.internal_note = internal_note
        d.reviewed_by = operator_user_id
        d.reviewed_at = datetime.now(timezone.utc)

        self.session.flush()

        # Recalculate analysis totals
        analysis = d.analysis
        accepted_costs = [
            item.estimated_cost
            for item in analysis.damages
            if item.review_status in ("accepted", "corrected") and item.passed_vehicle_gate
        ]
        subtotal, tax, total = CostingService.calculate_analysis_totals(accepted_costs)
        analysis.subtotal_cost = subtotal
        analysis.tax_amount = tax
        analysis.total_estimated_cost = total
        self.analysis_repo.save_analysis(analysis)

        return d

    def finalize_analysis(self, analysis_id: int, operator_user_id: int, notes: str | None = None) -> Analysis:
        analysis = self.analysis_repo.get_by_id(analysis_id)
        if not analysis:
            raise ResourceNotFoundError(f"Analysis #{analysis_id} not found.")

        if analysis.status == AnalysisStatus.FINALIZED.value:
            raise ValidationError("Analysis is already finalized and immutable.")

        # Finalization validation
        for d in analysis.damages:
            if d.review_status in ("accepted", "corrected") and d.passed_vehicle_gate:
                if d.estimated_cost < Decimal("0.00"):
                    raise ValidationError(f"Damage item '{d.final_damage_class}' has negative cost.")

        analysis.status = AnalysisStatus.FINALIZED.value
        analysis.operator_notes = notes
        analysis.finalized_by = operator_user_id
        analysis.finalized_at = datetime.now(timezone.utc)
        self.analysis_repo.save_analysis(analysis)

        self.audit_repo.log_event(
            action="finalize_analysis",
            entity_type="analysis",
            user_id=operator_user_id,
            entity_id=analysis.id,
            new_values={"total_cost": str(analysis.total_estimated_cost)},
        )

        return analysis
