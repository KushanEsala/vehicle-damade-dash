from __future__ import annotations

import numpy as np

from ml.annotator import annotate_image
from ml.damage_analyzer import DamageAnalyzer
from ml.model_registry import ModelRegistry
from ml.types import InferenceRequest, InferenceResult
from ml.vehicle_validator import VehicleValidator


class DamageInspectionPipeline:
    """Integrated damage inspection pipeline orchestrator."""

    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self.registry = registry or ModelRegistry.get_instance()
        self.vehicle_validator = VehicleValidator(self.registry)
        self.damage_analyzer = DamageAnalyzer(self.registry)

    def run(self, request: InferenceRequest) -> InferenceResult:
        vehicles = self.vehicle_validator.detect_vehicles(
            image_rgb=request.image,
            confidence_threshold=request.vehicle_confidence,
        )

        accepted, rejected = self.damage_analyzer.analyze_damage(
            image_rgb=request.image,
            vehicles=vehicles,
            confidence_threshold=request.damage_confidence,
            require_vehicle=request.require_vehicle,
        )

        annotated = annotate_image(request.image, vehicles, accepted)

        damage_meta = self.registry.get_damage_model_metadata()
        vehicle_meta = self.registry.get_vehicle_model_metadata()

        return InferenceResult(
            annotated_image=annotated,
            vehicles=vehicles,
            accepted_damages=accepted,
            rejected_damages=rejected,
            damage_model_hash=damage_meta.sha256,
            vehicle_model_hash=vehicle_meta.sha256,
        )


_pipeline_instance: DamageInspectionPipeline | None = None


def get_pipeline() -> DamageInspectionPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = DamageInspectionPipeline()
    return _pipeline_instance
