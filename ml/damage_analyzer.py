from __future__ import annotations

import numpy as np
from ml.model_registry import ModelRegistry
from ml.matching import damage_matches_vehicle
from ml.types import DamageDetection, VehicleDetection


class DamageAnalyzer:
    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self.registry = registry or ModelRegistry.get_instance()

    def analyze_damage(
        self,
        image_rgb: np.ndarray,
        vehicles: list[VehicleDetection],
        confidence_threshold: float = 0.30,
        require_vehicle: bool = True,
    ) -> tuple[list[DamageDetection], list[DamageDetection]]:
        """
        Runs damage segmentation model on image_rgb.
        Returns (accepted_damages, rejected_damages).
        """
        model = self.registry.load_damage_model()
        device = self.registry.get_device()

        result = model.predict(
            image_rgb,
            conf=confidence_threshold,
            iou=0.50,
            retina_masks=True,
            device=device,
            verbose=False,
        )[0]

        accepted: list[DamageDetection] = []
        rejected: list[DamageDetection] = []
        vehicle_boxes = [v.box for v in vehicles]
        polygons = result.masks.xy if result.masks is not None else []

        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)

            for idx, (box, conf, cid) in enumerate(zip(boxes, confidences, class_ids)):
                poly = polygons[idx] if idx < len(polygons) else None
                matched, overlap = damage_matches_vehicle(box, vehicle_boxes)
                passed_gate = not require_vehicle or matched

                detection = DamageDetection(
                    damage_class=result.names[cid],
                    confidence=float(conf),
                    box=box,
                    polygon=poly,
                    passed_vehicle_gate=passed_gate,
                    overlap_ratio=overlap,
                )

                if passed_gate:
                    accepted.append(detection)
                else:
                    rejected.append(detection)

        return accepted, rejected
