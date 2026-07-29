from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any
import ultralytics
from ultralytics import YOLO

from core.config import get_settings
from core.exceptions import ModelInferenceError
from ml.types import ModelMetadata


class ModelRegistry:
    _instance: ModelRegistry | None = None
    _damage_model: YOLO | None = None
    _vehicle_model: YOLO | None = None

    @classmethod
    def get_instance(cls) -> ModelRegistry:
        if cls._instance is None:
            cls._instance = ModelRegistry()
        return cls._instance

    @staticmethod
    def calculate_sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as f:
            for block in iter(lambda: f.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    def get_device(self) -> int | str:
        try:
            import torch
            return 0 if torch.cuda.is_available() else "cpu"
        except Exception:
            return "cpu"

    def load_damage_model(self) -> YOLO:
        if self._damage_model is None:
            settings = get_settings()
            path = settings.damage_model_abs_path
            if not path.is_file():
                raise ModelInferenceError(f"Damage model file not found at: {path}")
            try:
                self._damage_model = YOLO(str(path))
            except Exception as e:
                raise ModelInferenceError(f"Failed to load damage YOLO model: {e}")
        return self._damage_model

    def load_vehicle_model(self) -> YOLO:
        if self._vehicle_model is None:
            settings = get_settings()
            path = settings.vehicle_model_abs_path
            if not path.is_file():
                raise ModelInferenceError(f"Vehicle model file not found at: {path}")
            try:
                self._vehicle_model = YOLO(str(path))
            except Exception as e:
                raise ModelInferenceError(f"Failed to load vehicle YOLO model: {e}")
        return self._vehicle_model

    def get_damage_model_metadata(self) -> ModelMetadata:
        settings = get_settings()
        path = settings.damage_model_abs_path
        model = self.load_damage_model()
        classes = list(model.names.values())
        return ModelMetadata(
            model_key="vehicle_damage_seg_v1",
            display_name="Vehicle Damage Segmentation V1",
            file_path=str(settings.DAMAGE_MODEL_PATH),
            sha256=self.calculate_sha256(path),
            classes=classes,
            framework="Ultralytics YOLOv8",
            framework_version=ultralytics.__version__,
        )

    def get_vehicle_model_metadata(self) -> ModelMetadata:
        settings = get_settings()
        path = settings.vehicle_model_abs_path
        model = self.load_vehicle_model()
        classes = [name for cid, name in model.names.items() if cid in {2, 3, 5, 7}]
        return ModelMetadata(
            model_key="coco_vehicle_detector_v1",
            display_name="YOLOv8 COCO Vehicle Detector",
            file_path=str(settings.VEHICLE_MODEL_PATH),
            sha256=self.calculate_sha256(path),
            classes=classes,
            framework="Ultralytics YOLOv8",
            framework_version=ultralytics.__version__,
        )
