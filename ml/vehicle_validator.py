from __future__ import annotations

import numpy as np
from core.constants import VEHICLE_CLASS_IDS
from ml.model_registry import ModelRegistry
from ml.types import VehicleDetection


class VehicleValidator:
    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self.registry = registry or ModelRegistry.get_instance()

    def detect_vehicles(
        self,
        image_rgb: np.ndarray,
        confidence_threshold: float = 0.25,
    ) -> list[VehicleDetection]:
        model = self.registry.load_vehicle_model()
        device = self.registry.get_device()

        # First pass is fast. A higher-resolution, slightly more permissive
        # second pass is used only when the standard pass cannot confirm a
        # vehicle, which improves difficult close-ups without double-counting.
        result = self._predict(model, image_rgb, confidence_threshold, 640, device)
        detections = self._extract(result)
        if not detections:
            retry_threshold = max(0.10, confidence_threshold * 0.72)
            result = self._predict(model, image_rgb, retry_threshold, 960, device)
            detections = self._extract(result)
        return self._deduplicate(detections)

    @staticmethod
    def _predict(model, image_rgb: np.ndarray, confidence: float, image_size: int, device):
        return model.predict(
            image_rgb,
            conf=confidence,
            iou=0.50,
            imgsz=image_size,
            device=device,
            verbose=False,
        )[0]

    @staticmethod
    def _extract(result) -> list[VehicleDetection]:
        detections: list[VehicleDetection] = []
        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)

            for box, conf, cid in zip(boxes, confidences, class_ids):
                if cid in VEHICLE_CLASS_IDS:
                    detections.append(
                        VehicleDetection(
                            vehicle_class=result.names[cid],
                            confidence=float(conf),
                            box=box,
                        )
                    )
        return detections

    @staticmethod
    def _deduplicate(detections: list[VehicleDetection]) -> list[VehicleDetection]:
        kept: list[VehicleDetection] = []
        for detection in sorted(detections, key=lambda item: item.confidence, reverse=True):
            x1, y1, x2, y2 = detection.box
            area = max(1.0, (x2 - x1) * (y2 - y1))
            duplicate = False
            for existing in kept:
                ex1, ey1, ex2, ey2 = existing.box
                ix1, iy1 = max(x1, ex1), max(y1, ey1)
                ix2, iy2 = min(x2, ex2), min(y2, ey2)
                intersection = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
                existing_area = max(1.0, (ex2 - ex1) * (ey2 - ey1))
                union = area + existing_area - intersection
                if intersection / union >= 0.55:
                    duplicate = True
                    break
            if not duplicate:
                kept.append(detection)
        return kept
