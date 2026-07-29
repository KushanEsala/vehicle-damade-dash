from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import numpy as np


@dataclass
class VehicleDetection:
    vehicle_class: str
    confidence: float
    box: np.ndarray  # [x1, y1, x2, y2]

    def to_dict(self) -> dict[str, Any]:
        return {
            "vehicle": self.vehicle_class,
            "confidence": float(self.confidence),
            "box": self.box.tolist(),
        }


@dataclass
class DamageDetection:
    damage_class: str
    confidence: float
    box: np.ndarray  # [x1, y1, x2, y2]
    polygon: np.ndarray | None = None  # list of points [[x, y], ...]
    passed_vehicle_gate: bool = True
    overlap_ratio: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "damage": self.damage_class,
            "confidence": float(self.confidence),
            "box": self.box.tolist(),
            "polygon": self.polygon.tolist() if self.polygon is not None else None,
            "passed_vehicle_gate": self.passed_vehicle_gate,
            "overlap_ratio": float(self.overlap_ratio),
        }


@dataclass
class InferenceRequest:
    image: np.ndarray  # RGB uint8 numpy array
    damage_confidence: float = 0.30
    vehicle_confidence: float = 0.25
    require_vehicle: bool = True


@dataclass
class InferenceResult:
    annotated_image: np.ndarray
    vehicles: list[VehicleDetection] = field(default_factory=list)
    accepted_damages: list[DamageDetection] = field(default_factory=list)
    rejected_damages: list[DamageDetection] = field(default_factory=list)
    damage_model_hash: str = ""
    vehicle_model_hash: str = ""

    @property
    def vehicle_confirmed(self) -> bool:
        return len(self.vehicles) > 0


@dataclass
class ModelMetadata:
    model_key: str
    display_name: str
    file_path: str
    sha256: str
    classes: list[str]
    framework: str
    framework_version: str
