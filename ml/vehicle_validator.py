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

        result = model.predict(
            image_rgb,
            conf=confidence_threshold,
            iou=0.50,
            device=device,
            verbose=False,
        )[0]

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
