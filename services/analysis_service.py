from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from core.constants import AnalysisStatus, ReviewStatus, SeverityLevel
from core.exceptions import (
    AuthorizationError,
    NonVehicleImageError,
    ResourceNotFoundError,
    ValidationError,
)
from database.repositories.analysis_repository import AnalysisRepository
from database.repositories.vehicle_repository import VehicleRepository
from database.repositories.audit_repository import AuditRepository
from database.models.analysis import Analysis, AnalysisVehicleDetection, AnalysisDamage, AnalysisRevision, ModelVersion
from database.models.user import Role, User
from ml.pipeline import get_pipeline
from ml.types import InferenceRequest, InferenceResult
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

    def _require_staff(self, user_id: int) -> None:
        staff = (
            self.session.query(User)
            .join(User.role)
            .filter(
                User.id == user_id,
                User.is_active.is_(True),
                Role.code.in_(("admin", "operator")),
            )
            .first()
        )
        if not staff:
            raise AuthorizationError("An active administrator or operator account is required.")

    @staticmethod
    def _require_vehicle_image(result: InferenceResult) -> None:
        if result.image_rejected_as_non_vehicle or not result.vehicle_confirmed:
            raise NonVehicleImageError("Please attach a vehicle image.")

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
        from PIL import Image, ImageOps
        import numpy as np

        self._require_staff(operator_user_id)
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise ResourceNotFoundError(f"Vehicle #{vehicle_id} not found.")

        # Decode image array
        try:
            pil_img = Image.open(BytesIO(image_bytes))
            pil_img = ImageOps.exif_transpose(pil_img).convert("RGB")
            if pil_img.width < 160 or pil_img.height < 160:
                raise ValidationError("Inspection images must be at least 160 × 160 pixels.")
            if pil_img.width * pil_img.height > 40_000_000:
                raise ValidationError("Inspection image dimensions are too large.")
        except ValidationError:
            raise
        except Exception as exc:
            raise ValidationError(f"The uploaded inspection image could not be decoded: {exc}") from exc
        image_rgb = np.asarray(pil_img)

        # Run inference pipeline
        request = InferenceRequest(
            image=image_rgb,
            damage_confidence=damage_confidence,
            vehicle_confidence=vehicle_confidence,
            require_vehicle=require_vehicle_confirmation,
        )
        result = self.pipeline.run(request)
        self._require_vehicle_image(result)

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
                source=d.source,
                original_damage_class=d.original_damage_class or d.damage_class,
                final_damage_class=d.damage_class,
                confidence=Decimal(str(round(d.confidence, 4))),
                box_json=d.box.tolist(),
                polygon_json=d.polygon.tolist() if d.polygon is not None else None,
                model_polygon_json=d.model_polygon.tolist() if d.model_polygon is not None else None,
                mask_refined=d.mask_refined,
                overlap_ratio=Decimal(str(round(d.overlap_ratio, 4))),
                passed_vehicle_gate=True,
                review_status=(
                    ReviewStatus.CORRECTED.value
                    if str(d.original_damage_class or d.damage_class).lower().strip()
                    != str(d.damage_class).lower().strip()
                    else ReviewStatus.ACCEPTED.value
                ),
                vehicle_part=d.vehicle_part,
                severity=d.severity or SeverityLevel.MODERATE.value,
                description=d.description,
                internal_note=d.validation_note,
                estimated_cost=Decimal("0.00"),
            )
            self.session.add(ad)

        # Store rejected damages
        for d in result.rejected_damages:
            rd = AnalysisDamage(
                analysis_id=analysis.id,
                source=d.source,
                original_damage_class=d.original_damage_class or d.damage_class,
                final_damage_class=d.damage_class,
                confidence=Decimal(str(round(d.confidence, 4))),
                box_json=d.box.tolist(),
                polygon_json=d.polygon.tolist() if d.polygon is not None else None,
                model_polygon_json=d.model_polygon.tolist() if d.model_polygon is not None else None,
                mask_refined=d.mask_refined,
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
        self._require_staff(operator_user_id)
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
        self._require_staff(operator_user_id)
        d = self.session.query(AnalysisDamage).filter(AnalysisDamage.id == damage_id).first()
        if not d:
            raise ResourceNotFoundError(f"Damage item #{damage_id} not found.")
        if d.analysis.status in (AnalysisStatus.FINALIZED.value, AnalysisStatus.SUPERSEDED.value):
            raise ValidationError("Finalized or superseded assessment findings cannot be changed.")

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
        self._require_staff(operator_user_id)
        analysis = self.analysis_repo.get_by_id(analysis_id)
        if not analysis:
            raise ResourceNotFoundError(f"Analysis #{analysis_id} not found.")

        if analysis.status == AnalysisStatus.FINALIZED.value:
            raise ValidationError("Analysis is already finalized and immutable.")
        if analysis.status == AnalysisStatus.SUPERSEDED.value:
            raise ValidationError("A superseded analysis cannot be finalized.")

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

    def delete_damage_item(self, analysis_id: int, damage_id: int, operator_user_id: int) -> Analysis:
        self._require_staff(operator_user_id)
        analysis = self.analysis_repo.get_by_id(analysis_id)
        if not analysis:
            raise ResourceNotFoundError(f"Analysis #{analysis_id} not found.")
        if analysis.status in (AnalysisStatus.FINALIZED.value, AnalysisStatus.SUPERSEDED.value):
            raise ValidationError("Finalized or superseded assessment findings cannot be deleted.")
        damage = (
            self.session.query(AnalysisDamage)
            .filter(AnalysisDamage.id == damage_id, AnalysisDamage.analysis_id == analysis_id)
            .first()
        )
        if not damage:
            raise ResourceNotFoundError(f"Damage item #{damage_id} not found.")
        deleted_class = damage.final_damage_class
        self.session.delete(damage)
        self.session.flush()

        remaining = (
            self.session.query(AnalysisDamage)
            .filter(
                AnalysisDamage.analysis_id == analysis_id,
                AnalysisDamage.review_status.in_(("accepted", "corrected")),
                AnalysisDamage.passed_vehicle_gate.is_(True),
            )
            .all()
        )
        subtotal, tax, total = CostingService.calculate_analysis_totals([item.estimated_cost for item in remaining])
        analysis.accepted_damage_count = len(remaining)
        analysis.subtotal_cost = subtotal
        analysis.tax_amount = tax
        analysis.total_estimated_cost = total
        self._refresh_annotated_image(analysis, remaining)
        self.analysis_repo.save_analysis(analysis)
        self.audit_repo.log_event(
            action="delete_damage_finding",
            entity_type="analysis_damage",
            user_id=operator_user_id,
            entity_id=damage_id,
            old_values={"analysis_id": analysis_id, "damage_class": deleted_class},
        )
        return analysis

    def reanalyze(
        self,
        analysis_id: int,
        operator_user_id: int,
        *,
        damage_confidence: float,
        vehicle_confidence: float,
        require_vehicle: bool,
        reason: str,
    ) -> Analysis:
        from database.models.vehicle import VehicleImage

        self._require_staff(operator_user_id)
        original = self.analysis_repo.get_by_id(analysis_id)
        if not original:
            raise ResourceNotFoundError(f"Analysis #{analysis_id} not found.")
        if original.status == AnalysisStatus.FINALIZED.value:
            raise ValidationError("Finalized assessments cannot be reanalyzed.")
        if original.status == AnalysisStatus.SUPERSEDED.value:
            raise ValidationError("This assessment has already been replaced by a newer analysis.")
        source = self.session.query(VehicleImage).filter(VehicleImage.id == original.source_image_id).first()
        if not source:
            raise ResourceNotFoundError("The original inspection image is unavailable.")
        source_path = self.storage.get_absolute_path(source.storage_path)
        if not source_path.is_file():
            raise ResourceNotFoundError("The original inspection image file is unavailable.")

        replacement = self.run_new_analysis(
            vehicle_id=original.vehicle_id,
            source_image_id=original.source_image_id,
            operator_user_id=operator_user_id,
            image_bytes=source_path.read_bytes(),
            damage_confidence=damage_confidence,
            vehicle_confidence=vehicle_confidence,
            require_vehicle_confirmation=require_vehicle,
        )
        original.status = AnalysisStatus.SUPERSEDED.value
        self.analysis_repo.save_analysis(original)
        self.session.add(
            AnalysisRevision(
                original_analysis_id=original.id,
                replacement_analysis_id=replacement.id,
                reason=reason.strip(),
                created_by=operator_user_id,
            )
        )
        self.session.flush()
        self.audit_repo.log_event(
            action="reanalyze_assessment",
            entity_type="analysis",
            user_id=operator_user_id,
            entity_id=replacement.id,
            new_values={
                "replaces_analysis_id": original.id,
                "damage_confidence": damage_confidence,
                "vehicle_confidence": vehicle_confidence,
                "reason": reason,
            },
        )
        return replacement

    def _refresh_annotated_image(self, analysis: Analysis, damages: list[AnalysisDamage]) -> None:
        from PIL import Image, ImageOps
        import numpy as np
        from database.models.vehicle import VehicleImage
        from ml.annotator import annotate_image
        from ml.types import DamageDetection, VehicleDetection

        source = self.session.query(VehicleImage).filter(VehicleImage.id == analysis.source_image_id).first()
        if not source:
            return
        source_path = self.storage.get_absolute_path(source.storage_path)
        if not source_path.is_file():
            return
        image_rgb = np.asarray(ImageOps.exif_transpose(Image.open(source_path)).convert("RGB"))
        vehicles = [
            VehicleDetection(
                vehicle_class=item.vehicle_class,
                confidence=float(item.confidence),
                box=np.asarray(item.box_json, dtype=float),
            )
            for item in analysis.vehicle_detections
        ]
        accepted = [
            DamageDetection(
                damage_class=item.final_damage_class,
                confidence=float(item.confidence or 0),
                box=np.asarray(item.box_json, dtype=float),
                source=item.source,
                polygon=np.asarray(item.polygon_json, dtype=float) if item.polygon_json else None,
                model_polygon=np.asarray(item.model_polygon_json, dtype=float) if item.model_polygon_json else None,
                mask_refined=bool(item.mask_refined),
                passed_vehicle_gate=True,
                overlap_ratio=float(item.overlap_ratio or 0),
            )
            for item in damages
        ]
        analysis.annotated_image_path = self.storage.save_annotated_image(
            analysis.analysis_number,
            annotate_image(image_rgb, vehicles, accepted),
        )
