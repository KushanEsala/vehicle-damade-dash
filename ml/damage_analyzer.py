from __future__ import annotations

import numpy as np
from ml.model_registry import ModelRegistry
from ml.matching import damage_matches_vehicle
from ml.types import DamageDetection, VehicleDetection


class DamageAnalyzer:
    CLASS_CONFIDENCE_FLOORS = {
        # Puncture is visually ambiguous on ordinary body panels. Requiring a
        # stronger score removes many bumper/grille false positives.
        "puncture": 0.60,
    }

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
            imgsz=768,
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
                class_name = str(result.names[cid]).lower().strip()
                confidence_passed = float(conf) >= self.CLASS_CONFIDENCE_FLOORS.get(class_name, confidence_threshold)
                semantic_passed = self._is_spatially_plausible(class_name, box, vehicle_boxes)
                passed_gate = (not require_vehicle or matched) and confidence_passed and semantic_passed

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

    @staticmethod
    def _is_spatially_plausible(
        damage_class: str,
        damage_box: np.ndarray,
        vehicle_boxes: list[np.ndarray],
    ) -> bool:
        """Apply conservative class/location checks without changing model weights."""
        if damage_class != "puncture":
            return True
        if not vehicle_boxes:
            return False
        dx1, dy1, dx2, dy2 = damage_box
        center_x, center_y = (dx1 + dx2) / 2.0, (dy1 + dy2) / 2.0
        containing = [
            box for box in vehicle_boxes
            if box[0] <= center_x <= box[2] and box[1] <= center_y <= box[3]
        ]
        if not containing:
            return False
        # A puncture must be in the lower outer wheel zones of a full vehicle
        # box. Central bumper, grille and lamp regions are rejected.
        vehicle = max(containing, key=lambda box: (box[2] - box[0]) * (box[3] - box[1]))
        vx1, vy1, vx2, vy2 = vehicle
        width, height = max(vx2 - vx1, 1.0), max(vy2 - vy1, 1.0)
        relative_x = (center_x - vx1) / width
        relative_y = (center_y - vy1) / height
        return relative_y >= 0.52 and (relative_x <= 0.34 or relative_x >= 0.68)
